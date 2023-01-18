"""Application routes."""
# -*- encoding: utf-8 -*-
import hashlib
import hmac
import logging
import random
from flask_login import (
    login_required,
    login_user,
    logout_user,
    current_user,
)
from flask import (
    jsonify,
    redirect,
    request,
    session,
    url_for,
    Blueprint,
)
from esipy.exceptions import APIException
from flask_app.utils_esi_auth import (
    esisecurity,
    login_manager,
)

import flask_app.config as config
from flask_app.models import User, db
from sqlalchemy.orm.exc import NoResultFound


connector_login_bp = Blueprint(
    "connector_login_bp",
    __name__,
)

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------
# Flask Login requirements
# -----------------------------------------------------------------------
@login_manager.user_loader
def load_user(character_id):
    """Required user loader for Flask-Login"""
    return User.query.get(character_id)


# -----------------------------------------------------------------------
# Login / Logout Routes
# -----------------------------------------------------------------------
def generate_token():
    """Generates a non-guessable OAuth token"""
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    rand = random.SystemRandom()
    random_string = "".join(rand.choice(chars) for _ in range(40))
    return hmac.new(
        config.SECRET_KEY.encode("utf-8"),
        random_string.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


@connector_login_bp.route("/sso/login")
def login():
    """this redirects the user to the EVE SSO login"""
    token = generate_token()
    session["token"] = token
    return redirect(
        esisecurity.get_auth_uri(
            state=token,
            scopes=[
                "esi-location.read_location.v1 esi-location.read_ship_type.v1"
                " esi-skills.read_skills.v1 esi-skills.read_skillqueue.v1"
                " esi-wallet.read_character_wallet.v1"
                " esi-wallet.read_corporation_wallet.v1 esi-search.search_structures.v1"
                " esi-clones.read_clones.v1 esi-characters.read_contacts.v1"
                " esi-universe.read_structures.v1"
                " esi-bookmarks.read_character_bookmarks.v1"
                " esi-killmails.read_killmails.v1"
                " esi-corporations.read_corporation_membership.v1"
                " esi-assets.read_assets.v1 esi-planets.manage_planets.v1"
                " esi-fittings.read_fittings.v1 esi-fittings.write_fittings.v1"
                " esi-markets.structure_markets.v1 esi-corporations.read_structures.v1"
                " esi-characters.read_loyalty.v1 esi-characters.read_opportunities.v1"
                " esi-characters.read_medals.v1 esi-characters.read_standings.v1"
                " esi-characters.read_agents_research.v1"
                " esi-industry.read_character_jobs.v1"
                " esi-markets.read_character_orders.v1"
                " esi-characters.read_blueprints.v1"
                " esi-characters.read_corporation_roles.v1 esi-location.read_online.v1"
                " esi-contracts.read_character_contracts.v1 esi-clones.read_implants.v1"
                " esi-characters.read_fatigue.v1"
                " esi-killmails.read_corporation_killmails.v1"
                " esi-wallet.read_corporation_wallets.v1"
                " esi-characters.read_notifications.v1"
                " esi-corporations.read_divisions.v1 esi-corporations.read_contacts.v1"
                " esi-assets.read_corporation_assets.v1 esi-corporations.read_titles.v1"
                " esi-corporations.read_blueprints.v1"
                " esi-bookmarks.read_corporation_bookmarks.v1"
                " esi-contracts.read_corporation_contracts.v1"
                " esi-corporations.read_standings.v1 esi-corporations.read_starbases.v1"
                " esi-industry.read_corporation_jobs.v1"
                " esi-markets.read_corporation_orders.v1"
                " esi-corporations.read_container_logs.v1"
                " esi-industry.read_character_mining.v1"
                " esi-industry.read_corporation_mining.v1"
                " esi-planets.read_customs_offices.v1"
                " esi-corporations.read_facilities.v1 esi-corporations.read_medals.v1"
                " esi-characters.read_titles.v1 esi-alliances.read_contacts.v1"
                " esi-characters.read_fw_stats.v1 esi-corporations.read_fw_stats.v1"
                " esi-characterstats.read.v1"
            ],
        )
    )


@connector_login_bp.route("/sso/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("connector_login_bp.index"))


@connector_login_bp.route("/sso/callback")
def callback():
    """This is where the user comes after he logged in SSO"""
    # get the code from the login process
    code = request.args.get("code")
    token = request.args.get("state")

    # compare the state with the saved token for CSRF check
    sess_token = session.pop("token", None)
    if sess_token is None or token is None or token != sess_token:
        return "Login EVE Online SSO failed: Session Token Mismatch", 403

    # now we try to get tokens
    try:
        auth_response = esisecurity.auth(code)
    except APIException as e:
        return "Login EVE Online SSO failed: %s" % e, 403

    # we get the character informations
    cdata = esisecurity.verify()

    # if the user is already authed, we log him out
    if current_user.is_authenticated:
        logout_user()

    # now we check in database, if the user exists
    # actually we'd have to also check with character_owner_hash, to be
    # sure the owner is still the same, but that's an example only...
    try:
        user = User.query.filter(
            User.character_id == cdata["sub"].split(":")[2],
        ).one()

    except NoResultFound:
        user = User()
        user.character_id = cdata["sub"].split(":")[2]

    user.character_owner_hash = cdata["owner"]
    user.character_name = cdata["name"]
    user.update_token(auth_response)

    # now the user is ready, so update/create it and log the user
    try:
        db.session.merge(user)
        db.session.commit()

        login_user(user)
        session.permanent = True

    except:
        logger.exception("Cannot login the user - uid: %d" % user.character_id)
        db.session.rollback()
        logout_user()

    return redirect(url_for("character_details_bp.clone_status"))


@connector_login_bp.route("/logout_character")
def logout_character():
    character_id = request.args.get("character_id")
    redirect_page = request.args.get("redirect")

    log_out_character(character_id)
    return redirect(url_for(redirect_page))


def log_out_character(character_id):
    try:
        User.query.filter(User.character_id == character_id).delete(
            synchronize_session="fetch"
        )
        db.session.commit()
    except Exception as e:
        logger.warning(
            f"http error when removing character {character_id}: {e} - character not"
            " found"
        )
        logger.exception("Cannot login the user - uid: %d" % character_id)
        db.session.rollback()

    return redirect(url_for("character_details_bp.clone_status"))


@connector_login_bp.route("/info")
def ping():
    return jsonify(config.ESI_VERSION)

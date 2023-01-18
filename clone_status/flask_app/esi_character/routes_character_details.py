import json
import logging
from sqlalchemy import null
from flask import Blueprint, jsonify, request, render_template
from flask_app.models import User

from esipy.exceptions import APIException

from flask_app.utils_esi_auth import (
    esiapp,
    esiclient,
    esisecurity,
)

logger = logging.getLogger(__name__)

character_details_bp = Blueprint(
    "character_details_bp",
    __name__,
)


@character_details_bp.route("/")
def clone_status():

    all_data = User.query.all()

    clone_status_generated = {}

    for character in all_data:
        # test if the session is active
        clone_status_generated[character.character_id] = {}

        if character.is_authenticated:
            esisecurity.update_token(character.get_sso_data())
        else:
            clone_status_generated[character.character_id]["name"] = "Not authenticated"
            break

        try:
            op = esiapp.op["get_characters_character_id"](
                character_id=character.character_id
            )
            response = esiclient.request(op)
            clone_status_generated[character.character_id]["name"] = response.data.name
        except Exception as e:
            logger.warn(
                f"Exception {e} while getting character name for char"
                f" {character.character_id}"
            )
        try:
            op = esiapp.op["get_characters_character_id_online"](
                character_id=character.character_id
            )
            status = esiclient.request(op)
            clone_status_generated[character.character_id][
                "login_status"
            ] = status.data.online
        except Exception as e:
            logger.warn(f"Exception {e}")
            clone_status_generated[character.character_id][
                "login_status"
            ] = "Error fetching esi data"
        try:
            op_implants = esiapp.op["get_characters_character_id_implants"](
                character_id=character.character_id
            )
            implants = esiclient.request(op_implants).data
            is_training_clone = test_for_training_clone(implants)

            clone_status_generated[character.character_id]["active_implants"] = implants
            clone_status_generated[character.character_id][
                "is_training_clone"
            ] = is_training_clone
        except Exception as e:
            logger.warn(f"Exception {e}")
            clone_status_generated[character.character_id][
                "is_training_clone"
            ] = "Error fetching esi data"
            clone_status_generated[character.character_id][
                "active_implants"
            ] = "Error fetching esi data"

    return render_template(
        "clone_status.html",
        **{
            "clone_status": clone_status_generated,
        },
    )


def test_for_training_clone(character_implants):
    training_implants = [27148, 10217, 10209, 10213, 10222]
    for character_implant in character_implants:
        if character_implant in training_implants:
            return True
    return False


@character_details_bp.route("/request_character_wallet", methods=["POST"])
def request_character_wallet_post():
    wallet = request_character_wallet()
    return jsonify(wallet.data)


def request_character_wallet():
    wallet = None
    user = User.query.filter(
        User.character_id == int(request.form.get("character_id"))
    ).one()

    esisecurity.update_token(user.get_sso_data())
    op = esiapp.op["get_characters_character_id_wallet"](character_id=user.character_id)
    wallet = esiclient.request(op)
    return wallet


@character_details_bp.route("/v2/request_character_wallet", methods=["GET"])
def request_character_wallet_get_v2():
    wallet = request_character_wallet_v2()
    return jsonify(wallet.data)


def request_character_wallet_v2():
    wallet = None
    user = User.query.filter(
        User.character_id == int(request.args.get("character_id"))
    ).one()

    esisecurity.update_token(user.get_sso_data())
    op = esiapp.op["get_characters_character_id_wallet"](character_id=user.character_id)
    wallet = esiclient.request(op)
    return wallet


@character_details_bp.route("/request_character_details", methods=["POST"])
def request_character_details_post():
    response = None
    try:
        character_id = request.form.get("character_id")
        user = User.query.filter(User.character_id == int(character_id)).one()
        esisecurity.update_token(user.get_sso_data())
        op = esiapp.op["get_characters_character_id"](character_id=user.character_id)

        response = esiclient.request(op)
        response_data = json.dumps(response.data, indent=4, sort_keys=True, default=str)
        response_data = json.loads(response_data)
        response = jsonify(response_data)
        response.status_code = 200
    except APIException as e:
        logger.warning(
            f"http error when requesting location of character {user.character_id}: {e}"
        )
        response = jsonify("")
        response.status_code = 500
    return response

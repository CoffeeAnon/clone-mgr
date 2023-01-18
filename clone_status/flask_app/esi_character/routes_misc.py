from flask import Blueprint, jsonify
import logging
from flask_app.models import User, db

character_misc_bp = Blueprint(
    "character_misc_bp",
    __name__,
)

logger = logging.getLogger(__name__)


@character_misc_bp.route("/request_stored_characters")
def get_character_list():
    data = {}
    try:
        characters = []
        query = db.session.query(User).order_by(User.character_id)
        print(f"Number of characters: {len(query.all())}")
        for instance in query.all():
            character = {"character_id": instance.character_id}
            characters.append(character)
        response = jsonify(characters)
        response.status_code = 200
        return response
    except:
        logger.exception("Error: Cannot list characters.")

    response = jsonify(data)
    response.status_code = 500
    return response

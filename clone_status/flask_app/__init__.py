"""Initialize Flask app."""
# -*- encoding: utf-8 -*-
import socket, os
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.model import DefaultMeta
from urllib3.connection import HTTPConnection
import flask_app.config as config
from flask import (
    Flask,
)

# ...
HTTPConnection.default_socket_options = HTTPConnection.default_socket_options + [
    (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1),
    (socket.SOL_TCP, socket.TCP_KEEPIDLE, 45),
    (socket.SOL_TCP, socket.TCP_KEEPINTVL, 10),
    (socket.SOL_TCP, socket.TCP_KEEPCNT, 6),
]

db = SQLAlchemy()
migrate = Migrate()

# satisfies mypy
BaseModel: DefaultMeta = db.Model


def create_app():
    """Construct the core application."""
    app = Flask(__name__, instance_relative_config=False)

    app.config.from_object(config)

    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
        basedir, "app.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        # init db

        # Import blueprints and required functions
        from .connector_login import routes_login
        from .esi_character import routes_character_details  # Import routes
        from .esi_character import routes_misc  # Import routes

        #
        # Register Blueprints
        app.register_blueprint(
            routes_login.connector_login_bp,
        )
        app.register_blueprint(routes_misc.character_misc_bp)
        app.register_blueprint(routes_character_details.character_details_bp)

        HTTPConnection.default_socket_options = (
            HTTPConnection.default_socket_options
            + [
                (socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1),
                (socket.SOL_TCP, socket.TCP_KEEPIDLE, 45),
                (socket.SOL_TCP, socket.TCP_KEEPINTVL, 10),
                (socket.SOL_TCP, socket.TCP_KEEPCNT, 6),
            ]
        )

        return app

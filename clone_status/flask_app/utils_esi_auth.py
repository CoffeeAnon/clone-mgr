"""Application routes."""
# -*- encoding: utf-8 -*-
import logging
from flask import current_app as app
from esipy import EsiApp, EsiClient, EsiSecurity

import flask_app.config as config
from flask_login import (
    LoginManager,
)

esiapp = EsiApp().get_latest_swagger

# init the security object
esisecurity = EsiSecurity(
    redirect_uri=config.ESI_CALLBACK,
    client_id=config.ESI_CLIENT_ID,
    secret_key=config.SECRET_KEY,
    headers={"User-Agent": config.ESI_USER_AGENT},
)

# init the client
esiclient = EsiClient(
    security=esisecurity,
    cache=None,
    headers={"User-Agent": config.ESI_USER_AGENT},
)

# logger stuff
logger = logging.getLogger(__name__)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
console.setFormatter(formatter)
logger.addHandler(console)

# init flask login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

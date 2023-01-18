# -*- encoding: utf-8 -*-
import os
import datetime
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), "../../.env")
load_dotenv(dotenv_path)

# -----------------------------------------------------
# Application configurations
# ------------------------------------------------------
DEBUG = True
SECRET_KEY = os.environ.get("ESI_SECRET_KEY")
PORT = 5000
HOST = "0.0.0.0"
CALLBACK_HOST = os.environ.get("SERVICE_URL")
# -----------------------------------------------------
# SQL Alchemy configs
# -----------------------------------------------------
SQLALCHEMY_DATABASE_URI = "sqlite:///app.db"
# -----------------------------------------------------
# ESI Configs
# -----------------------------------------------------
ESI_DATASOURCE = "tranquility"  # Change it to 'singularity' to use the test server
ESI_SWAGGER_JSON = (
    "https://esi.tech.ccp.is/latest/swagger.json?datasource=%s" % ESI_DATASOURCE
)
ESI_CLIENT_ID = os.environ.get("ESI_CLIENT_ID")  # your client ID
ESI_USER_AGENT = os.environ.get("ESI_USER_AGENT")
ESI_CALLBACK = os.environ.get("ESI_CALLBACK")  # the callback URI registered with CCP
ESI_USER_AGENT = os.environ.get("ESI_USER_AGENT")
ESI_VERSION = "0.2"

# ------------------------------------------------------
# Session settings for flask login
# ------------------------------------------------------
PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=30)

# ------------------------------------------------------
# DO NOT EDIT
# Fix warnings from flask-sqlalchemy / others
# ------------------------------------------------------
SQLALCHEMY_TRACK_MODIFICATIONS = True

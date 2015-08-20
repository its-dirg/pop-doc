# pylint: disable=missing-docstring,import-error,no-name-in-module
from flask.ext.login import LoginManager
from flask_bootstrap import Bootstrap
from flask import Flask
import uuid

__author__ = 'mathiashedstrom'

APP = Flask(__name__, static_folder='static')
APP.secret_key = str(uuid.uuid4())  # Replace with your secret key
LOGIN_MANAGER = LoginManager()
LOGIN_MANAGER.init_app(APP)
Bootstrap(APP)

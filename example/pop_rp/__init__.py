from flask.ext.login import LoginManager
from flask_bootstrap import Bootstrap
from flask import Flask
import uuid

__author__ = 'mathiashedstrom'

app = Flask(__name__, static_folder='static')
app.secret_key = str(uuid.uuid4())  # Replace with your secret key
login_manager = LoginManager()
login_manager.init_app(app)
Bootstrap(app)

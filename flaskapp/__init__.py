from flask import Flask
from flask_login import LoginManager

from flaskapp import config, utils

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"

utils.refresh_credentials(app)


app.secret_key = config.flask_secret_key


from flaskapp import cli, views  # noqa - required for flask

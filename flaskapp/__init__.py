from flask import Flask
from flask_login import LoginManager
from pymongo import MongoClient
from pymongo.encryption import ClientEncryption

from flaskapp import config

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"

regularClient = MongoClient(config.connection_string)
keyVaultClient = MongoClient(config.connection_string_keyvault_db)

client_encryption = ClientEncryption(
    config.kms_providers,
    config.key_vault_namespace,
    keyVaultClient,
    codec_options=keyVaultClient.codec_options,
)
app.mongodb = regularClient
app.mongodb_key_vault = keyVaultClient
app.mongodb_encryption_client = client_encryption

app.user_collection = regularClient[config.db_name].user
app.data_collection = regularClient[config.db_name].data


app.secret_key = config.flask_secret_key


from flaskapp import cli, views  # noqa - required for flask

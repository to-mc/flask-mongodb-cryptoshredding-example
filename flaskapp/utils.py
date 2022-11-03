import urllib.parse

import boto3
from pymongo import MongoClient
from pymongo.encryption import ClientEncryption

from flaskapp import config


def assume_role(aws_role_arn):
    sts_client = boto3.client("sts")
    assumed_role_object = sts_client.assume_role(
        RoleArn=aws_role_arn, RoleSessionName="AssumeRoleSession1", DurationSeconds=900
    )

    return assumed_role_object["Credentials"]


def setup_mongodb_client(
    flask_app, credentials, hostname, client_param_name="mongodb", set_collections=False
):
    access_key_id = urllib.parse.quote_plus(credentials["AccessKeyId"])
    secret_access_key = urllib.parse.quote_plus(credentials["SecretAccessKey"])
    session_token = urllib.parse.quote_plus(credentials["SessionToken"])
    connection_string = (
        f"mongodb+srv://{access_key_id}:{secret_access_key}@{hostname}/?"
        f"authMechanism=MONGODB-AWS&authMechanismProperties=AWS_SESSION_TOKEN:{session_token}&authSource=$external"
    )

    mongo_client = MongoClient(connection_string)
    setattr(flask_app, client_param_name, mongo_client)

    if set_collections:
        data_coll = mongo_client[config.db_name].data
        users_coll = mongo_client[config.db_name].user
        setattr(flask_app, "data_collection", data_coll)
        setattr(flask_app, "user_collection", users_coll)


def setup_encryption_client(flask_app, credentials, provider):
    kms_providers = {
        provider: {
            "accessKeyId": credentials["AccessKeyId"],
            "secretAccessKey": credentials["SecretAccessKey"],
            "sessionToken": credentials["SessionToken"],
        }
    }
    encryption_client = ClientEncryption(
        kms_providers,
        config.key_vault_namespace,
        flask_app.mongodb_key_vault,
        codec_options=flask_app.mongodb_key_vault.codec_options,
    )

    flask_app.mongodb_encryption_client = encryption_client


def refresh_credentials(flask_app):
    credentials = assume_role(aws_role_arn=config.awsrole)
    setup_mongodb_client(
        flask_app=flask_app,
        credentials=credentials,
        hostname=config.mongodb_hostname,
        client_param_name="mongodb",
        set_collections=True,
    )
    setup_mongodb_client(
        flask_app=flask_app,
        credentials=credentials,
        hostname=config.mongodb_keyvault_hostname,
        client_param_name="mongodb_key_vault",
    )
    setup_encryption_client(
        flask_app=flask_app, credentials=credentials, provider=config.kms_provider
    )

import os
import urllib.parse

from flaskapp.utils import assume_role

provider = "aws"
awsrole = os.environ["ATLAS_AWS_ROLE"]
db_name = "CSFLE-CRYPTOSHREDDING"
credentials = assume_role(awsrole)
kms_providers = {
    provider: {
        "accessKeyId": credentials["AccessKeyId"],
        "secretAccessKey": credentials["SecretAccessKey"],
        "sessionToken": credentials["SessionToken"],
    }
}

access_key_id = urllib.parse.quote_plus(credentials["AccessKeyId"])
secret_access_key = urllib.parse.quote_plus(credentials["SecretAccessKey"])
session_token = urllib.parse.quote_plus(credentials["SessionToken"])

kms_key_arn = os.environ["ATLAS_AWS_KMS_KEY"]
kms_key_region = os.environ["AWS_DEFAULT_REGION"]
master_key = {
    "region": kms_key_region,
    "key": kms_key_arn,
}
key_vault_db = "encryption"
key_vault_coll = "___keyVault"
key_vault_namespace = f"{key_vault_db}.{key_vault_coll}"

connection_string = (
    f"mongodb+srv://{access_key_id}:{secret_access_key}@{os.environ['ATLAS_CLUSTER_HOSTNAME']}/?"
    f"authMechanism=MONGODB-AWS&authMechanismProperties=AWS_SESSION_TOKEN:{session_token}&authSource=$external"
)
connection_string_keyvault_db = (
    f"mongodb+srv://{access_key_id}:{secret_access_key}@{os.environ['ATLAS_KEYVAULT_CLUSTER_HOSTNAME']}/?"
    f"authMechanism=MONGODB-AWS&authMechanismProperties=AWS_SESSION_TOKEN:{session_token}&authSource=$external"
)

flask_secret_key = os.environ["FLASK_SECRET_KEY"]

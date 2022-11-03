import os

awsrole = os.environ["ATLAS_AWS_ROLE"]
db_name = "CSFLE-CRYPTOSHREDDING"

kms_provider = "aws"

kms_key_arn = os.environ["ATLAS_AWS_KMS_KEY"]
kms_key_region = os.environ["AWS_DEFAULT_REGION"]
master_key = {
    "region": kms_key_region,
    "key": kms_key_arn,
}
key_vault_db = "encryption"
key_vault_coll = "___keyVault"
key_vault_namespace = f"{key_vault_db}.{key_vault_coll}"

flask_secret_key = os.environ["FLASK_SECRET_KEY"]

mongodb_hostname = os.environ["ATLAS_CLUSTER_HOSTNAME"]
mongodb_keyvault_hostname = os.environ["ATLAS_KEYVAULT_CLUSTER_HOSTNAME"]

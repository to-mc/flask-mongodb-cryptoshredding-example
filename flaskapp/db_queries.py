from functools import wraps

import pymongo
from flask_login import current_user
from pymongo.encryption import Algorithm

from flaskapp import app, utils
from flaskapp.config import kms_provider, master_key

# Fields to encrypt, and the algorithm to encrypt them with
ENCRYPTED_FIELDS = {
    # Deterministic encryption for username, because we need to search on it
    "username": Algorithm.AEAD_AES_256_CBC_HMAC_SHA_512_Deterministic,
    # Random encryption for value, as we don't need to search on it
    "value": Algorithm.AEAD_AES_256_CBC_HMAC_SHA_512_Random,
}


def aws_credential_handler(func):
    """
    Decorator for functions using temporary AWS credentials from an assumed role.
    If the operation fails due to credential expiry, try to refresh the credentials before retrying the operation.
    """

    @wraps(func)
    def wrapper_func(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except pymongo.errors.OperationFailure as ex:
            if ex.details.get("codeName") == "AuthenticationFailed":
                app.logger.exception(ex)
                app.logger.warn(
                    "Auth failed to MongoDB. Trying to refresh temporary AWS credentials before"
                    " attempting again."
                )
                utils.refresh_credentials(app)
                return func(*args, **kwargs)
            raise ex  # Re-raise the exception if its not about expired credentials
        except pymongo.errors.EncryptionError as ex:
            if "expired" in ex._message:
                app.logger.exception(ex)
                app.logger.warn(
                    "Auth failed when trying encryption operation. Trying to refresh temporary AWS"
                    " credentials before attempting again."
                )
                utils.refresh_credentials(app)
                return func(*args, **kwargs)
            raise ex  # Re-raise the exception if its not about expired credentials

    return wrapper_func


@aws_credential_handler
def find_user(query):
    user = app.user_collection.find_one(query)
    return user


@aws_credential_handler
def create_key(userId):
    data_key_id = app.mongodb_encryption_client.create_data_key(
        kms_provider, master_key, key_alt_names=[userId]
    )
    return data_key_id


@aws_credential_handler
def encrypt_field(field, algorithm):
    try:
        field = app.mongodb_encryption_client.encrypt(
            field,
            algorithm,
            key_alt_name=current_user.username,
        )
        return field
    except pymongo.errors.EncryptionError as ex:
        if "not all keys requested were satisfied" in ex._message:
            app.logger.warn(
                "Encryption failed: could not find data encryption key for user:"
                f" {current_user.username}"
            )
        raise ex


def decrypt_field(field):
    try:
        field = app.mongodb_encryption_client.decrypt(field)
        return field, True
    except pymongo.errors.EncryptionError as ex:
        if "not all keys requested were satisfied" in ex._message:
            app.logger.warn(
                "Decryption failed: could not find data encryption key to decrypt the record."
            )
            return field, False
        raise ex


@aws_credential_handler
def insert_data(document):
    document["username"] = current_user.username
    for field, algo in ENCRYPTED_FIELDS.items():
        if document.get(field):
            document[field] = encrypt_field(document[field], algo)
    app.data_collection.insert_one(document)


@aws_credential_handler
def query_data(query):
    for field, algo in ENCRYPTED_FIELDS.items():
        if query.get(field):
            query[field] = encrypt_field(query[field], algo)

    results = list(app.data_collection.find(query))

    for field in ENCRYPTED_FIELDS.keys():
        for result in results:
            if result.get(field):
                result[field], _ = decrypt_field(result[field])

    return results


@aws_credential_handler
def delete_single_data_item(query):
    for field, algo in ENCRYPTED_FIELDS.items():
        if query.get(field):
            query[field] = encrypt_field(query[field], algo)

    result = app.data_collection.delete_one(query)
    return result


@aws_credential_handler
def delete_user(username):
    app.user_collection.delete_one({"username": username})


@aws_credential_handler
def delete_all_data_for_user(username):
    username = encrypt_field(username, Algorithm.AEAD_AES_256_CBC_HMAC_SHA_512_Deterministic)
    app.data_collection.delete_many({"username": username})


@aws_credential_handler
def fetch_all_data_unencrypted(decrypt=False):
    results = list(app.data_collection.find())

    if decrypt:
        for field in ENCRYPTED_FIELDS.keys():
            for result in results:
                if result.get(field):
                    result[field], result["encryption_succeeded"] = decrypt_field(result[field])

    return results

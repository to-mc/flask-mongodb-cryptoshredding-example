import pymongo
from flask_login import current_user
from pymongo.encryption import Algorithm

from flaskapp import app
from flaskapp.config import master_key, provider

# Fields to encrypt, and the algorithm to encrypt them with
ENCRYPTED_FIELDS = {
    "username": Algorithm.AEAD_AES_256_CBC_HMAC_SHA_512_Deterministic,
    "value": Algorithm.AEAD_AES_256_CBC_HMAC_SHA_512_Random,
}


def create_key(userId):
    data_key_id = app.mongodb_encryption_client.create_data_key(
        provider, master_key, key_alt_names=[userId]
    )
    return data_key_id


def encrypt_field(field, algorithm):
    try:
        field = app.mongodb_encryption_client.encrypt(
            field,
            algorithm,
            key_alt_name=current_user.username,
        )
        return field
    except pymongo.errors.EncryptionError as ex:
        app.logger.warn(
            f"Encryption failed: could not find encryption key for user: {current_user.username}"
        )
        raise ex


def decrypt_field(field):
    try:
        field = app.mongodb_encryption_client.decrypt(field)
        return field, True
    except pymongo.errors.EncryptionError:
        app.logger.warn(
            f"Decryption failed: could not find encryption key for user: {current_user.username}"
        )
        return field, False


def insert_data(document):
    document["username"] = current_user.username
    for field, algo in ENCRYPTED_FIELDS.items():
        if document.get(field):
            document[field] = encrypt_field(document[field], algo)
    app.data_collection.insert_one(document)


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


def delete_single_data_item(query):
    for field, algo in ENCRYPTED_FIELDS.items():
        if query.get(field):
            query[field] = encrypt_field(query[field], algo)

    result = app.data_collection.delete_one(query)
    return result


def delete_user(username):
    app.user_collection.delete_one({"username": username})


def delete_all_data_for_user(username):
    username = encrypt_field(username, Algorithm.AEAD_AES_256_CBC_HMAC_SHA_512_Deterministic)
    app.data_collection.delete_many({"username": username})


def fetch_all_data_unencrypted(decrypt=False, skip=0, limit=20):
    results = list(app.data_collection.find(limit=limit, skip=skip))

    if decrypt:
        for field in ENCRYPTED_FIELDS.keys():
            for result in results:
                if result.get(field):
                    result[field], result["encryption_succeeded"] = decrypt_field(result[field])
    return results

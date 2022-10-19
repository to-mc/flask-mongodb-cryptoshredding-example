from flaskapp import app, config


@app.cli.command("create-indexes")
def create_indexes():
    app.mongodb_key_vault[config.key_vault_db][config.key_vault_coll].create_index(
        [("keyAltNames", 1)], unique=True
    )

    app.user_collection.create_index([("username", 1)], unique=True)
    print("Indexes created")

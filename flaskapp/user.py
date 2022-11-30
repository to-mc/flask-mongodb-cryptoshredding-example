from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from flaskapp import app, db_queries
from flaskapp.config import db_name


class User(UserMixin):
    def __init__(self, id=""):
        self.username = None
        self.id = id
        self.password_hash = None
        self.dek_id = ""

    def hash_password(self, password):
        self.password_hash = generate_password_hash(password)

    @staticmethod
    def validate_login(password_hash, password):
        return check_password_hash(password_hash, password)

    @classmethod
    def build_user_from_db(cls, user):
        user_obj = cls(str(user["_id"]))
        user_obj.username = user["username"]
        user_obj.password_hash = user["password_hash"]
        user_obj.dek_id = user["dek_id"]
        return user_obj

    @classmethod
    def create_user(cls, username, password):
        user_obj = cls()
        user_obj.username = username
        user_obj.hash_password(password=password)
        user_obj.save()
        return user_obj

    def save(self):
        dek_id = db_queries.create_key(self.username)
        result = app.mongodb[db_name].user.insert_one(
            {
                "username": self.username,
                "password_hash": self.password_hash,
                "dek_id": dek_id,
                "createdAt": datetime.now(),
            }
        )
        if result:
            self.id = result.inserted_id
            return True
        else:
            return False

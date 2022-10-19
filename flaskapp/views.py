import pymongo
from bson import ObjectId, json_util
from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from flaskapp import app, db_queries, forms, login_manager
from flaskapp.config import db_name
from flaskapp.user import User


@login_manager.user_loader
def load_user(user_id):
    _id = json_util.loads(user_id)
    result = app.mongodb[db_name]["user"].find_one({"_id": _id})
    if result:
        user = User.build_user_from_db(result)
    else:
        return None
    return user


@app.route("/deletePref", methods=["POST"])
@login_required
def delete():
    preference = request.form.get("userpref_id")
    db_queries.delete_single_preference_doc(
        query={"_id": ObjectId(preference), "username": current_user.username},
    )
    return redirect(url_for("home"))


@app.route("/", methods=["GET", "POST"])
@login_required
def home():
    form = forms.AddDataForm()
    if form.validate_on_submit():
        document = {
            "key": form.key.data,
            "value": form.value.data,
        }
        db_queries.insert_preference_doc(document=document)
        flash("Data added!", category="info")

        return redirect(url_for("login"))
    try:
        user_preferences = db_queries.retrieve_preference_docs(
            query={"username": current_user.username},
        )
    except pymongo.errors.EncryptionError as ex:
        app.logger.exception(ex)
        flash("Encryption failure trying to retrieve data", category="error")
        user_preferences = []

    return render_template("home.html", form=form, user_preferences=user_preferences)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = forms.SignInForm()
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = app.mongodb[db_name].user.find_one({"username": username})
        if user and User.validate_login(user["password_hash"], password):
            user_obj = User.build_user_from_db(user)
            login_user(user_obj, remember=True)
            return redirect(url_for("home"))
        else:
            flash("Incorrect username or password", category="error")
            return redirect(url_for("login"))

    return render_template("login.html", form=form)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = forms.SignUpForm()
    if form.validate_on_submit():
        username = request.form.get("username")
        password = request.form.get("password")
        if username and password:
            user = app.mongodb[db_name].user.find_one({"username": username})
            if user:
                flash("User already exists with that username")
                return redirect(url_for("login"))
            user = User.create_user(username=username, password=password)
            flash("User created, please log in", category="success")

            return redirect(url_for("login"))

        else:
            return redirect(url_for("signup"))

    return render_template("signup.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/admin")
@login_required
def admin():
    return render_template("admin.html")


@app.route("/shredKey")
@login_required
def shred_key():
    app.mongodb_encryption_client.delete_key(id=current_user.dek_id)
    flash(
        "Data encryption key has been deleted. Existing data will no longer be accessible once cache expires",
        category="info",
    )
    return redirect(url_for("home"))


@app.route("/deleteUser")
def delete_user():
    app.user_collection.delete_one({"username": current_user.username})

    flash(
        f'User: "{current_user.username}" deleted',
        category="info",
    )
    logout_user()
    return redirect(url_for("home"))


@app.route("/deleteUserAndKey")
def delete_user_and_key():
    app.user_collection.delete_one({"username": current_user.username})
    app.mongodb_encryption_client.delete_key(id=current_user.dek_id)

    flash(
        f"User: {current_user.username} deleted along with their data encryption key",
        category="info",
    )
    logout_user()
    return redirect(url_for("home"))


@app.route("/deleteUserData")
def delete_user_data():
    db_queries.delete_all_data_for_user(current_user.username)

    flash(
        f"Data for user: {current_user.username} deleted",
        category="info",
    )
    return redirect(url_for("admin"))

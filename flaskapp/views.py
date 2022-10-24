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


@app.route("/delete-single-item", methods=["POST"])
@login_required
def delete_single_item():
    data_item = request.form.get("item_id")
    result = db_queries.delete_single_data_item(
        query={"_id": ObjectId(data_item), "username": current_user.username},
    )
    if result.deleted_count:
        flash("Item deleted!", category="info")
    else:
        flash("Could not find item or its not owned by your user!", category="danger")
    return redirect(url_for("user_data"))


@app.route("/user-data", methods=["GET", "POST"])
@login_required
def user_data():
    form = forms.AddDataForm()
    if form.validate_on_submit():
        document = {
            "key": form.key.data,
            "value": form.value.data,
        }
        try:
            db_queries.insert_data(document=document)
            flash("Item added!", category="info")
        except pymongo.errors.EncryptionError as ex:
            app.logger.exception(ex)
            flash("Could not add new data, no encryption key found!", category="danger")

        return redirect(url_for("user_data"))
    try:
        user_data = db_queries.query_data(
            query={"username": current_user.username},
        )
    except pymongo.errors.EncryptionError as ex:
        app.logger.exception(ex)
        flash("Encryption failure trying to retrieve data", category="danger")
        user_data = []

    return render_template("userdata.html", form=form, user_data=user_data)


@app.route("/")
def home():
    return render_template("home.html")


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
            login_user(user_obj, remember=form.remember_me.data)
            return redirect(url_for("user_data"))
        else:
            flash("Incorrect username or password", category="danger")
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
                flash("User already exists with that username", category="danger")
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
    user = current_user.username
    logout_user()
    flash(f"User {user} logged out", category="success")
    return redirect(url_for("login"))


@app.route("/admin")
@login_required
def admin():
    admin_actions = [
        {
            "title": "Fetch data for all users",
            "text": "Show all the data added by any user",
            "link": url_for("fetch_all_data"),
            "btnclass": "primary",
        },
        {
            "title": "Delete encryption key",
            "text": (
                "This will delete <strong>only the encryption key</strong> for the logged in user,"
                " and can be used to demonstrate that you will no longer be able to access your"
                " data that was encrypted with the key."
            ),
            "link": url_for("shred_key"),
        },
        {
            "title": "Delete user and encryption key",
            "text": (
                "Delete the record for the logged in user from the database, as well as the"
                " related encryption key. The data records will remain, but will be unreadable as"
                " they can no longer be decrypted."
            ),
            "link": url_for("delete_user_and_key"),
        },
        {
            "title": "Delete user",
            "text": (
                "Delete the record for the logged in user from the database. The data records"
                " will remain, and can potentially be read as the encryption key still exists."
            ),
            "link": url_for("delete_user"),
        },
        {
            "title": "Delete all data for user",
            "text": "Delete the data records added by the logged in user.",
            "link": url_for("delete_user_data"),
        },
    ]
    return render_template("admin.html", actions=admin_actions)


@app.route("/delete-data-key")
@login_required
def shred_key():
    app.mongodb_encryption_client.delete_key(id=current_user.dek_id)
    flash(
        "Data encryption key has been deleted. Existing data will no longer be accessible once"
        " cache expires",
        category="info",
    )
    return redirect(url_for("user_data"))


@app.route("/delete-user")
def delete_user():
    app.user_collection.delete_one({"username": current_user.username})

    flash(
        f'User: "{current_user.username}" deleted and logged out',
        category="info",
    )
    logout_user()
    return redirect(url_for("home"))


@app.route("/delete-user-and-key")
def delete_user_and_key():
    app.user_collection.delete_one({"username": current_user.username})
    app.mongodb_encryption_client.delete_key(id=current_user.dek_id)

    flash(
        f"User: {current_user.username} deleted along with their data encryption key",
        category="info",
    )
    logout_user()
    return redirect(url_for("home"))


@app.route("/delete-user-data")
def delete_user_data():
    db_queries.delete_all_data_for_user(current_user.username)

    flash(
        f"Data for user: {current_user.username} deleted",
        category="info",
    )
    return redirect(url_for("admin"))


@app.route("/fetch-all-data")
def fetch_all_data():
    # Naive pagination implementation that will not perform well at scale
    page_size = 20
    page = int(request.args.get("page", 1))
    skip = (page - 1) * page_size
    data, total = db_queries.fetch_all_data_unencrypted(decrypt=True, skip=skip, limit=page_size)

    return render_template(
        "alldata.html",
        data=data,
        skip=skip,
        page=page,
        total_count=total,
    )

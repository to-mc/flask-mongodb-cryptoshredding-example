from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField, validators


class SignUpForm(FlaskForm):
    username = StringField("Username", [validators.Length(min=4, max=25)])
    password = PasswordField(
        "New Password",
        [
            validators.DataRequired(),
            validators.EqualTo("confirm", message="Passwords must match"),
        ],
    )
    confirm = PasswordField("Repeat Password")
    submit = SubmitField("Sign up")


class SignInForm(FlaskForm):
    username = StringField("Username", [validators.Length(min=4, max=25)])
    password = PasswordField(
        "Password",
        [
            validators.DataRequired(),
        ],
    )
    remember_me = BooleanField("Remember me")
    submit = SubmitField("Login")


class AddDataForm(FlaskForm):
    name = StringField("Name", [validators.DataRequired()], render_kw={"placeholder": "Shoe size"})
    value = StringField("Value", [validators.DataRequired()], render_kw={"placeholder": "10"})
    submit = SubmitField("Add data")

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo

class VegetableForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    price = StringField("Price", validators=[DataRequired()])
    selling_unit = StringField("Selling Unit", validators=[DataRequired()])
    image = FileField("Image", validators=[FileAllowed(['png', 'jpg', 'jpeg'])])
    submit = SubmitField("Submit")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember me")
    submit = SubmitField("Continue")


class RegistrationForm(FlaskForm):
    first_name = StringField("First Name",
                validators=[DataRequired(), Length(min=2, max=20)])
    last_name = StringField("Last Name",
                validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField("Email",
                validators=[DataRequired()])
    password = PasswordField("Password",
                validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password",
                validators=[DataRequired(), EqualTo("password")])

    submit = SubmitField("Sign Up")
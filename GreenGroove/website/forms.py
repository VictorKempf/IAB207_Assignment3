from flask_wtf import FlaskForm
from wtforms.fields import TextAreaField, SubmitField, StringField, PasswordField
from wtforms.validators import InputRequired, Length, Email, EqualTo

# creates the login information
class LoginForm(FlaskForm):
    email=StringField("Email", validators=[InputRequired(), Email("Please enter a valid email")])
    password=PasswordField("Password", validators=[InputRequired('Enter password')])
    submit = SubmitField("Login")

 # this is the registration form
class RegisterForm(FlaskForm):
    first_name=StringField("First Name", validators=[InputRequired()])
    surname=StringField("Surname", validators=[InputRequired()])
    email = StringField("Email Address", validators=[InputRequired(), Email("Please enter a valid email")])
    contact_number = StringField("Contact Number", validators=[InputRequired()])
    street_address = StringField("Street Address", validators=[InputRequired()])
    # linking two fields - password should be equal to data entered in confirm
    password=PasswordField("Password", validators=[
                InputRequired(),
                EqualTo('confirm', message="Passwords should match")])
    confirm = PasswordField("Confirm Password", validators=[InputRequired()])

    # submit button
    submit = SubmitField("Register")
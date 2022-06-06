from ctypes import addressof
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, PasswordField, TextAreaField, IntegerField, DateField
from wtforms.validators import Email, InputRequired, DataRequired, Length



class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])


class UserAddForm(FlaskForm):
    """Form for adding users."""

    email = StringField('E-mail', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class UserUpdateForm(FlaskForm):
    """ Form for updating users. """
    username = StringField(
        'Username',
        validators=[DataRequired(),
                    Length(max=30)])

    email = StringField(
        'E-mail',
        validators=[DataRequired(),
                    Email()])

    first_name = StringField(
        "First Name", 
        validators=[DataRequired()])

    last_name = StringField(
        "Last Name", 
        validators=[InputRequired()])

    password = PasswordField(
        'Enter your password',
        validators=[DataRequired(),
                    Length(min=6)]
    )

class NewPurchaseForm(FlaskForm):
    product_name = StringField("Product Name", validators=[InputRequired()])
    units_purchased = IntegerField('Amount Purchased', validators = [InputRequired()])
    date_purchased = DateField('Date Purchased', validators = [InputRequired()])

class PasswordResetForm(FlaskForm):
    """Form for reset user password."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])

class UserLogoutForm(FlaskForm):
    """ Form for user logout """

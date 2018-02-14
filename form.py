# project/forms.py
# from flask_wtf import Form
from wtforms import Form,StringField, DateField, IntegerField, \
    SelectField, PasswordField
from wtforms.validators import DataRequired, NumberRange,Length,EqualTo


from flask import session
from wtforms.csrf.session import SessionCSRF
from _config import *

class MyBaseForm(Form):
    class Meta:
        csrf = True
        csrf_class = SessionCSRF
        csrf_secret = CSRF_SECRET_KEY

        @property
        def csrf_context(self):
            return session

class RegistrationForm(MyBaseForm):
    username = StringField('Identifiant', validators=[DataRequired(),Length(min=4, max=25)])
    password = PasswordField('Mot de passe', [
        DataRequired(),
        EqualTo('confirm', message='Les mots de passe ne sont pas les meme')
    ])
    confirm = PasswordField('Repetez mot de passe')

class LoginForm(MyBaseForm):
	username = StringField('Identifiant', validators=[DataRequired(),Length(min=4, max=25)])
	password = PasswordField('Mot de passe', [DataRequired()])

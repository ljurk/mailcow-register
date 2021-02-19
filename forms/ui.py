from os import getenv
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField
from wtforms.validators import Optional, DataRequired


class BaseForm(FlaskForm):
    token = StringField('Token', description='will be regenerated on page reload', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    submit = SubmitField('Submit')
    message = "~"

class Admin(BaseForm):
    domain = StringField('Domain', default=getenv("REGISTER_DOMAIN"), validators=[DataRequired()])
    tlsIn = BooleanField('TLS in', default=True)
    tlsOut = BooleanField('TLS out', default=True)
    quota = IntegerField("Quota", default=getenv("REGISTER_QUOTA"), validators=[DataRequired()])


class Ui(BaseForm):
    fullname = StringField('Fullname', validators=[Optional()])
    password = PasswordField('Password', validators=[Optional()])

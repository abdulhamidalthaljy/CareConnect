from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, DecimalField
from wtforms.validators import DataRequired, Length, EqualTo, Optional


class LoginForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Length(min=1, max=150)])
    password = PasswordField('password', validators=[DataRequired()])


class RegisterForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), Length(min=3, max=150)])
    password = PasswordField('password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('confirm_password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('role', choices=[('patient', 'Patient'), ('doctor', 'Doctor')], default='patient')


class ProfileForm(FlaskForm):
    full_name = StringField('full_name', validators=[Optional(), Length(max=200)])
    address = StringField('address', validators=[Optional(), Length(max=300)])
    allergies = TextAreaField('allergies', validators=[Optional()])
    health_history = TextAreaField('health_history', validators=[Optional()])


class MedicineForm(FlaskForm):
    name = StringField('name', validators=[DataRequired(), Length(max=200)])
    dosage = StringField('dosage', validators=[Optional(), Length(max=200)])


class AppointmentForm(FlaskForm):
    doctor_id = StringField('doctor_id', validators=[DataRequired()])
    start_time = StringField('start_time', validators=[DataRequired()])

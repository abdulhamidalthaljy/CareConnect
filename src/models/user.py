from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from src.extensions import db, login_manager


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), default='patient')

    # relationships
    profile = db.relationship('PatientProfile', back_populates='user', uselist=False)
    medicines = db.relationship('Medicine', back_populates='patient', cascade='all, delete-orphan')
    vitals = db.relationship('Vitals', back_populates='patient', cascade='all, delete-orphan')
    files = db.relationship('MedicalFile', back_populates='patient', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def activities(self):
        # placeholder for template compatibility; can be populated later
        return []


@login_manager.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except Exception:
        return None


class PatientProfile(db.Model):
    __tablename__ = 'patient_profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    full_name = db.Column(db.String(200))
    address = db.Column(db.String(300))
    health_history = db.Column(db.Text)
    allergies = db.Column(db.Text)
    user = db.relationship('User', back_populates='profile')


class Medicine(db.Model):
    __tablename__ = 'medicines'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    dosage = db.Column(db.String(200))
    patient = db.relationship('User', back_populates='medicines')


class Vitals(db.Model):
    __tablename__ = 'vitals'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(50))
    value1 = db.Column(db.String(100))
    value2 = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    patient = db.relationship('User', back_populates='vitals')


class MedicalFile(db.Model):
    __tablename__ = 'medical_files'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    original_filename = db.Column(db.String(300))
    storage_filename = db.Column(db.String(300), unique=True)
    upload_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    patient = db.relationship('User', back_populates='files')


class Appointment(db.Model):
    __tablename__ = 'appointments'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), default='pending')


class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message_text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

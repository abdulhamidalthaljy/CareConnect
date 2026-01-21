from flask import Blueprint, render_template, abort, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime

from src.models.user import User, PatientProfile, Medicine, Vitals, MedicalFile
from src.extensions import db

doctor = Blueprint('doctor', __name__)


def is_doctor():
    return (current_user.role or '').strip().lower() == 'doctor'


@doctor.route('/doctor')
@login_required
def dashboard():
    # only doctors may access
    if not is_doctor():
        abort(403)
    patients = User.query.filter(User.role.ilike('patient')).order_by(User.username).all()
    return render_template('doctor_dashboard.html', patients=patients)


@doctor.route('/doctor/view/<int:patient_id>')
@login_required
def view_patient(patient_id):
    if not is_doctor():
        abort(403)
    patient = User.query.get_or_404(patient_id)
    if (patient.role or '').strip().lower() != 'patient':
        abort(404)

    profile = PatientProfile.query.filter_by(user_id=patient.id).first()
    medicines = Medicine.query.filter_by(patient_id=patient.id).all()
    vitals = Vitals.query.filter_by(patient_id=patient.id).order_by(Vitals.timestamp.desc()).all()
    files = MedicalFile.query.filter_by(patient_id=patient.id).all()

    return render_template('patient_view.html', patient=patient, profile=profile, medicines=medicines, vitals=vitals, files=files)


@doctor.route('/doctor/update_profile/<int:patient_id>', methods=['POST'])
@login_required
def update_patient_profile(patient_id):
    if not is_doctor():
        abort(403)
    patient = User.query.get_or_404(patient_id)
    if (patient.role or '').strip().lower() != 'patient':
        abort(404)

    full_name = request.form.get('full_name', '').strip()
    address = request.form.get('address', '').strip()
    allergies = request.form.get('allergies', '').strip()
    health_history = request.form.get('health_history', '').strip()

    profile = PatientProfile.query.filter_by(user_id=patient.id).first()
    if not profile:
        profile = PatientProfile(user_id=patient.id)
        db.session.add(profile)

    profile.full_name = full_name
    profile.address = address
    profile.allergies = allergies
    profile.health_history = health_history
    db.session.commit()

    flash('Patient profile updated.', 'success')
    return redirect(url_for('doctor.view_patient', patient_id=patient_id))


@doctor.route('/doctor/add_medicine/<int:patient_id>', methods=['POST'])
@login_required
def add_patient_medicine(patient_id):
    if not is_doctor():
        abort(403)
    patient = User.query.get_or_404(patient_id)

    name = request.form.get('name', '').strip()
    dosage = request.form.get('dosage', '').strip()

    if not name:
        flash('Medicine name is required.', 'danger')
        return redirect(url_for('doctor.view_patient', patient_id=patient_id))

    med = Medicine(patient_id=patient.id, name=name, dosage=dosage)
    db.session.add(med)
    db.session.commit()

    flash('Medicine added.', 'success')
    return redirect(url_for('doctor.view_patient', patient_id=patient_id))


@doctor.route('/doctor/delete_medicine/<int:med_id>', methods=['POST'])
@login_required
def delete_patient_medicine(med_id):
    if not is_doctor():
        abort(403)
    med = Medicine.query.get_or_404(med_id)
    patient_id = med.patient_id
    db.session.delete(med)
    db.session.commit()

    flash('Medicine removed.', 'info')
    return redirect(url_for('doctor.view_patient', patient_id=patient_id))


@doctor.route('/doctor/add_vital/<int:patient_id>', methods=['POST'])
@login_required
def add_patient_vital(patient_id):
    if not is_doctor():
        abort(403)
    patient = User.query.get_or_404(patient_id)

    v_type = request.form.get('type', 'bp')
    value1 = request.form.get('value1', '').strip()
    value2 = request.form.get('value2', '').strip()

    if not value1:
        flash('Value is required.', 'danger')
        return redirect(url_for('doctor.view_patient', patient_id=patient_id))

    try:
        float(value1)
        if value2:
            float(value2)
    except ValueError:
        flash('Values must be numeric.', 'danger')
        return redirect(url_for('doctor.view_patient', patient_id=patient_id))

    vital = Vitals(patient_id=patient.id, type=v_type, value1=value1, value2=value2 or None, timestamp=datetime.utcnow())
    db.session.add(vital)
    db.session.commit()

    flash('Vital added.', 'success')
    return redirect(url_for('doctor.view_patient', patient_id=patient_id))


@doctor.route('/doctor/delete_vital/<int:vital_id>', methods=['POST'])
@login_required
def delete_patient_vital(vital_id):
    if not is_doctor():
        abort(403)
    vital = Vitals.query.get_or_404(vital_id)
    patient_id = vital.patient_id
    db.session.delete(vital)
    db.session.commit()

    flash('Vital removed.', 'info')
    return redirect(url_for('doctor.view_patient', patient_id=patient_id))

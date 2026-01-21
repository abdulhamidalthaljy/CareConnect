from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from datetime import datetime

from src.models.user import User, Appointment
from src.extensions import db
from src.forms import AppointmentForm

appointments = Blueprint('appointments', __name__)


@appointments.route('/appointments')
@login_required
def patient_appointments():
    # patient view: request appointment and see own appointments
    if (current_user.role or '').strip().lower() != 'patient':
        abort(403)
    doctors = User.query.filter(User.role.ilike('doctor')).all()
    my_apps = Appointment.query.filter_by(patient_id=current_user.id).order_by(Appointment.start_time.desc()).all()
    return render_template('appointments.html', doctors=doctors, appointments=my_apps)


@appointments.route('/request_appointment', methods=['POST'])
@login_required
def request_appointment():
    if (current_user.role or '').strip().lower() != 'patient':
        abort(403)
    form = AppointmentForm()
    if form.validate_on_submit():
        doctor_id = form.doctor_id.data
        start_time = form.start_time.data
        try:
            dt = datetime.fromisoformat(start_time)
        except Exception:
            flash('Invalid date/time format', 'danger')
            return redirect(url_for('appointments.patient_appointments'))

        app_obj = Appointment(patient_id=current_user.id, doctor_id=int(doctor_id), start_time=dt, status='pending')
        db.session.add(app_obj)
        db.session.commit()
        flash('Appointment requested', 'success')
        return redirect(url_for('appointments.patient_appointments'))

    flash('Doctor and start time are required', 'danger')
    return redirect(url_for('appointments.patient_appointments'))


@appointments.route('/doctor/appointments')
@login_required
def doctor_appointments():
    if (current_user.role or '').strip().lower() != 'doctor':
        abort(403)
    # allow optional status filter via ?status=pending|confirmed|cancelled|all
    status = (request.args.get('status') or '').strip().lower()
    q = Appointment.query.filter_by(doctor_id=current_user.id)
    if status and status != 'all':
        q = q.filter_by(status=status)
    apps = q.order_by(Appointment.start_time.asc()).all()

    # build patient id -> username map to display human-readable names
    patient_ids = list({a.patient_id for a in apps}) if apps else []
    patient_map = {}
    if patient_ids:
        patients = User.query.filter(User.id.in_(patient_ids)).all()
        patient_map = {p.id: p.username for p in patients}

    return render_template('doctor_appointments.html', appointments=apps, patient_map=patient_map, current_status=status or 'all')


@appointments.route('/confirm_appointment/<int:app_id>')
@login_required
def confirm_appointment(app_id):
    if (current_user.role or '').strip().lower() != 'doctor':
        abort(403)
    app_obj = Appointment.query.get_or_404(app_id)
    if app_obj.doctor_id != current_user.id:
        abort(403)
    app_obj.status = 'confirmed'
    db.session.commit()
    flash('Appointment confirmed', 'success')
    return redirect(url_for('appointments.doctor_appointments'))


@appointments.route('/cancel_appointment/<int:app_id>')
@login_required
def cancel_appointment(app_id):
    # either doctor or patient can cancel
    app_obj = Appointment.query.get_or_404(app_id)
    if (current_user.role or '').strip().lower() == 'doctor' and app_obj.doctor_id != current_user.id:
        abort(403)
    if (current_user.role or '').strip().lower() == 'patient' and app_obj.patient_id != current_user.id:
        abort(403)
    app_obj.status = 'cancelled'
    db.session.commit()
    flash('Appointment cancelled', 'info')
    # redirect appropriately
    if (current_user.role or '').strip().lower() == 'doctor':
        return redirect(url_for('appointments.doctor_appointments'))
    return redirect(url_for('appointments.patient_appointments'))

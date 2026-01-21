from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required

from src.models.user import User
from src.extensions import db
from src.forms import LoginForm, RegisterForm

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        current_app.logger.debug('Login attempt for username=%s', username)
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            current_app.logger.debug('Login failed for %s', username)
            flash('Invalid username or password', 'danger')
            return render_template('auth/login.html', form=form)

        login_user(user)
        current_app.logger.debug('Login successful for %s', username)
        flash('Login successful!', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('auth/login.html', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        password = form.password.data
        role = (form.role.data or 'patient').strip().lower()

        current_app.logger.debug('Register attempt for username=%s role=%s', username, role)
        existing = User.query.filter_by(username=username).first()
        if existing:
            current_app.logger.debug('Register failed: username exists %s', username)
            flash('Username already exists. Please choose another.', 'danger')
            return render_template('auth/register.html', form=form)

        new_user = User(username=username, role=role)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        current_app.logger.debug('Registered new user id=%s username=%s', new_user.id, new_user.username)
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
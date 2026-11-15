"""
Authentication Routes for Personal Expense Tracker
Handles registration, login, logout, and session management.
"""
from flask import Blueprint, request, session, redirect, url_for, flash, render_template
from functools import wraps

from backend.services.auth_service import auth_service
from shared.constants.app_constants import (
    FrontendRoutes, BackendRoutes, FormFieldNames, TemplateVariables, ErrorMessages
)


auth_bp = Blueprint('auth', __name__)


def login_required(f):
    """Decorator to require login for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if TemplateVariables.USER_ID not in session:
            flash(ErrorMessages.UNAUTHORIZED, 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route(BackendRoutes.REGISTER, methods=['GET', 'POST'])
def register():
    """User registration."""
    if request.method == 'GET':
        return render_template('register.html')

    # POST - Process registration
    name = request.form.get(FormFieldNames.NAME, '').strip()
    email = request.form.get(FormFieldNames.EMAIL, '').strip().lower()
    password = request.form.get(FormFieldNames.PASSWORD, '')
    confirm_password = request.form.get(FormFieldNames.CONFIRM_PASSWORD, '')

    success, user_id, errors = auth_service.register_user(name, email, password, confirm_password)

    if success:
        session[TemplateVariables.USER_ID] = user_id
        session[TemplateVariables.USER_NAME] = name
        session.permanent = True
        flash('Registration successful! Welcome!', 'success')
        return redirect(url_for('main.dashboard'))

    # Return errors to template
    for error in errors:
        for field, message in error.items():
            flash(message, 'error')
    return render_template('register.html', name=name, email=email), 400


@auth_bp.route(BackendRoutes.LOGIN, methods=['GET', 'POST'])
def login():
    """User login."""
    if request.method == 'GET':
        # If already logged in, redirect to dashboard
        if TemplateVariables.USER_ID in session:
            return redirect(url_for('main.dashboard'))
        return render_template('login.html')

    # POST - Process login
    email = request.form.get(FormFieldNames.EMAIL, '').strip().lower()
    password = request.form.get(FormFieldNames.PASSWORD, '')

    success, user, errors = auth_service.login_user(email, password)

    if success:
        session[TemplateVariables.USER_ID] = user['user_id']
        session[TemplateVariables.USER_NAME] = user['name']
        session.permanent = True
        flash('Login successful!', 'success')
        return redirect(url_for('main.dashboard'))

    for error in errors:
        for field, message in error.items():
            flash(message, 'error')
    return render_template('login.html', email=email), 400


@auth_bp.route(BackendRoutes.LOGOUT)
def logout():
    """User logout."""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile')
@login_required
def profile():
    """User profile page."""
    user = auth_service.get_user_by_id(session[TemplateVariables.USER_ID])
    return render_template('profile.html', user=user)
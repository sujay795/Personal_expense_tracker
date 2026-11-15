"""
Main Routes for Personal Expense Tracker
Handles dashboard and main page routing.
"""
from flask import Blueprint, session, redirect, url_for, render_template
from functools import wraps

from backend.services.report_service import report_service
from shared.constants.app_constants import (
    FrontendRoutes, TemplateVariables, ErrorMessages
)


main_bp = Blueprint('main', __name__)


def login_required(f):
    """Decorator to require login for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if TemplateVariables.USER_ID not in session:
            flash(ErrorMessages.UNAUTHORIZED, 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@main_bp.route('/')
def index():
    """Root route - redirect to dashboard or login."""
    if TemplateVariables.USER_ID in session:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))


@main_bp.route(FrontendRoutes.DASHBOARD)
@login_required
def dashboard():
    """Dashboard with totals, recent transactions, and budget status."""
    user_id = session[TemplateVariables.USER_ID]
    user_name = session.get(TemplateVariables.USER_NAME, 'User')

    dashboard_data = report_service.get_dashboard_data(user_id)

    return render_template('dashboard.html',
                           user_name=user_name,
                           **dashboard_data)
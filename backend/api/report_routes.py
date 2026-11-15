"""
Report Routes for Personal Expense Tracker
Handles report generation and display.
"""
from flask import Blueprint, request, session, redirect, url_for, flash, render_template
from datetime import date
from functools import wraps

from backend.services.report_service import report_service
from backend.services.transaction_service import transaction_service
from shared.constants.app_constants import (
    BackendRoutes, TemplateVariables, ErrorMessages, TransactionConstants
)


report_bp = Blueprint('reports', __name__)


def login_required(f):
    """Decorator to require login for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if TemplateVariables.USER_ID not in session:
            flash(ErrorMessages.UNAUTHORIZED, 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@report_bp.route(BackendRoutes.REPORTS, methods=['GET'])
@login_required
def reports():
    """View reports with month/year filter."""
    user_id = session[TemplateVariables.USER_ID]

    # Get filter parameters
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int, default=date.today().year)

    if month:
        # Monthly report
        report_data = report_service.get_monthly_report(user_id, month, year)
        report_type = 'monthly'
    else:
        # Yearly report
        report_data = report_service.get_yearly_report(user_id, year)
        report_type = 'yearly'

    # Also get all-time totals for reference
    all_time = report_service.get_all_time_report(user_id)

    return render_template('reports.html',
                           report=report_data,
                           report_type=report_type,
                           selected_month=month,
                           selected_year=year,
                           all_time=all_time,
                           months=range(1, 13),
                           years=range(2020, date.today().year + 2),
                           categories=TransactionConstants.CATEGORIES)
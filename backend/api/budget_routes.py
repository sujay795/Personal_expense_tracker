"""
Budget Routes for Personal Expense Tracker
Handles budget creation, viewing, and management.
"""
from flask import Blueprint, request, session, redirect, url_for, flash, render_template
from datetime import date
from functools import wraps

from backend.services.budget_service import budget_service
from backend.services.transaction_service import transaction_service
from shared.constants.app_constants import (
    BackendRoutes, FormFieldNames, TemplateVariables, ErrorMessages
)


budget_bp = Blueprint('budget', __name__)


def login_required(f):
    """Decorator to require login for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if TemplateVariables.USER_ID not in session:
            flash(ErrorMessages.UNAUTHORIZED, 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@budget_bp.route(BackendRoutes.BUDGET, methods=['GET', 'POST'])
@login_required
def budget():
    """View and manage budgets."""
    user_id = session[TemplateVariables.USER_ID]

    if request.method == 'POST':
        # Create or update budget
        month = int(request.form.get(FormFieldNames.MONTH, date.today().month))
        year = int(request.form.get(FormFieldNames.YEAR, date.today().year))
        limit_amount = request.form.get(FormFieldNames.LIMIT_AMOUNT, '')

        success, budget_id, errors = budget_service.create_budget(user_id, month, year, limit_amount)

        if success:
            flash('Budget saved successfully!', 'success')
            return redirect(url_for('budget.budget'))

        for error in errors:
            for field, message in error.items():
                flash(message, 'error')

    # GET - Show budgets
    budgets = budget_service.get_all_budgets(user_id)
    current_budget = budget_service.get_current_budget(user_id)

    return render_template('budget.html',
                           budgets=budgets,
                           current_budget=current_budget,
                           today=date.today())


@budget_bp.route('/budget/<int:budget_id>/delete', methods=['POST'])
@login_required
def delete_budget(budget_id: int):
    """Delete a budget."""
    user_id = session[TemplateVariables.USER_ID]

    success, errors = budget_service.delete_budget(user_id, budget_id)

    if success:
        flash('Budget deleted successfully!', 'success')
    else:
        for error in errors:
            for field, message in error.items():
                flash(message, 'error')

    return redirect(url_for('budget.budget'))
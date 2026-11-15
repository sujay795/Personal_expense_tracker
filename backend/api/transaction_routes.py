"""
Transaction Routes for Personal Expense Tracker
Handles CRUD operations for transactions.
"""
from flask import Blueprint, request, session, redirect, url_for, flash, render_template, jsonify
from functools import wraps

from backend.services.transaction_service import transaction_service
from backend.services.auth_service import auth_service
from shared.contracts.api_schemas import TransactionType, TransactionCategory
from shared.constants.app_constants import (
    FrontendRoutes, BackendRoutes, FormFieldNames, TemplateVariables, ErrorMessages, TransactionConstants
)


transaction_bp = Blueprint('transactions', __name__)


def login_required(f):
    """Decorator to require login for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if TemplateVariables.USER_ID not in session:
            flash(ErrorMessages.UNAUTHORIZED, 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@transaction_bp.route(BackendRoutes.TRANSACTIONS, methods=['GET'])
@login_required
def list_transactions():
    """List transactions with filters and pagination."""
    user_id = session[TemplateVariables.USER_ID]

    # Get filter parameters
    txn_type = request.args.get('type', '')
    category = request.args.get('category', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    page = int(request.args.get('page', 1))
    per_page = 20

    transactions, total = transaction_service.get_transactions(
        user_id, page, per_page, txn_type, category, start_date, end_date
    )

    total_pages = (total + per_page - 1) // per_page

    return render_template('transactions.html',
                           transactions=transactions,
                           total=total,
                           page=page,
                           total_pages=total_pages,
                           type_filter=txn_type,
                           category_filter=category,
                           start_date=start_date,
                           end_date=end_date,
                           categories=TransactionConstants.CATEGORIES,
                           transaction_types=[t.value for t in TransactionType])


@transaction_bp.route(BackendRoutes.TRANSACTION_CREATE, methods=['GET', 'POST'])
@login_required
def add_transaction():
    """Add a new transaction."""
    user_id = session[TemplateVariables.USER_ID]

    if request.method == 'GET':
        return render_template('add_transaction.html',
                               categories=TransactionConstants.CATEGORIES,
                               transaction_types=[t.value for t in TransactionType])

    # POST - Create transaction
    txn_type = request.form.get(FormFieldNames.TRANSACTION_TYPE, '')
    amount = request.form.get(FormFieldNames.AMOUNT, '')
    category = request.form.get(FormFieldNames.CATEGORY, '')
    date_str = request.form.get(FormFieldNames.DATE, '')
    description = request.form.get(FormFieldNames.DESCRIPTION, '')

    success, txn_id, errors = transaction_service.create_transaction(
        user_id, txn_type, amount, category, date_str, description
    )

    if success:
        flash('Transaction added successfully!', 'success')
        return redirect(url_for('transactions.list_transactions'))

    for error in errors:
        for field, message in error.items():
            flash(message, 'error')
    return render_template('add_transaction.html',
                           categories=TransactionConstants.CATEGORIES,
                           transaction_types=[t.value for t in TransactionType],
                           form_data=request.form), 400


@transaction_bp.route(BackendRoutes.TRANSACTION_EDIT, methods=['GET', 'POST'])
@login_required
def edit_transaction(transaction_id: int):
    """Edit a transaction."""
    user_id = session[TemplateVariables.USER_ID]

    txn = transaction_service.get_transaction(user_id, transaction_id)
    if not txn:
        flash(ErrorMessages.TRANSACTION_NOT_FOUND, 'error')
        return redirect(url_for('transactions.list_transactions'))

    if request.method == 'GET':
        return render_template('edit_transaction.html',
                               transaction=txn,
                               categories=TransactionConstants.CATEGORIES,
                               transaction_types=[t.value for t in TransactionType])

    # POST - Update transaction
    txn_type = request.form.get(FormFieldNames.TRANSACTION_TYPE) or None
    amount = request.form.get(FormFieldNames.AMOUNT) or None
    category = request.form.get(FormFieldNames.CATEGORY) or None
    date_str = request.form.get(FormFieldNames.DATE) or None
    description = request.form.get(FormFieldNames.DESCRIPTION)

    success, errors = transaction_service.update_transaction(
        user_id, transaction_id, txn_type, amount, category, date_str, description
    )

    if success:
        flash('Transaction updated successfully!', 'success')
        return redirect(url_for('transactions.list_transactions'))

    for error in errors:
        for field, message in error.items():
            flash(message, 'error')
    return render_template('edit_transaction.html',
                           transaction=txn,
                           categories=TransactionConstants.CATEGORIES,
                           transaction_types=[t.value for t in TransactionType]), 400


@transaction_bp.route(BackendRoutes.TRANSACTION_DELETE, methods=['POST'])
@login_required
def delete_transaction(transaction_id: int):
    """Delete a transaction."""
    user_id = session[TemplateVariables.USER_ID]

    success, errors = transaction_service.delete_transaction(user_id, transaction_id)

    if success:
        flash('Transaction deleted successfully!', 'success')
    else:
        for error in errors:
            for field, message in error.items():
                flash(message, 'error')

    return redirect(url_for('transactions.list_transactions'))
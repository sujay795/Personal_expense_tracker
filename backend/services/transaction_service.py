"""
Transaction Service for Personal Expense Tracker
Handles CRUD operations for transactions.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Tuple, Dict, Any

from backend.database.connection import get_db
from shared.contracts.api_schemas import TransactionType, TransactionCategory
from shared.constants.app_constants import (
    ErrorMessages, TransactionConstants, FormFieldNames
)


class TransactionService:
    """Service for transaction management."""

    VALID_CATEGORIES = set(c.value for c in TransactionCategory)
    VALID_TYPES = set(t.value for t in TransactionType)

    def __init__(self):
        self.db = get_db()

    def validate_transaction(self, txn_type: str, amount: str, category: str, 
                             date_str: str, description: str = "") -> Tuple[bool, list]:
        """Validate transaction input."""
        errors = []

        # Validate type
        if not txn_type or txn_type not in self.VALID_TYPES:
            errors.append({FormFieldNames.TRANSACTION_TYPE: ErrorMessages.INVALID_TYPE})

        # Validate amount
        try:
            amount_val = Decimal(str(amount))
            if amount_val <= 0:
                errors.append({FormFieldNames.AMOUNT: ErrorMessages.INVALID_AMOUNT})
            elif amount_val > TransactionConstants.MAX_AMOUNT:
                errors.append({FormFieldNames.AMOUNT: "Amount is too large"})
        except Exception:
            errors.append({FormFieldNames.AMOUNT: ErrorMessages.INVALID_AMOUNT})

        # Validate category
        if not category or category not in self.VALID_CATEGORIES:
            errors.append({FormFieldNames.CATEGORY: ErrorMessages.INVALID_CATEGORY})

        # Validate date
        try:
            datetime.strptime(date_str, "%Y-%m-%d").date()
        except Exception:
            errors.append({FormFieldNames.DATE: ErrorMessages.INVALID_DATE})

        # Validate description length
        if description and len(description) > 500:
            errors.append({FormFieldNames.DESCRIPTION: "Description too long (max 500 characters)"})

        return len(errors) == 0, errors

    def create_transaction(self, user_id: int, txn_type: str, amount: str,
                           category: str, date_str: str, description: str = "") -> Tuple[bool, Optional[int], list]:
        """Create a new transaction. Returns (success, transaction_id, errors)."""
        is_valid, errors = self.validate_transaction(txn_type, amount, category, date_str, description)
        if not is_valid:
            return False, None, errors

        with self.db.get_db() as conn:
            cursor = conn.execute(
                """INSERT INTO transactions (user_id, type, amount, category, description, date)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (user_id, txn_type, float(amount), category, description.strip() if description else None, date_str)
            )
            transaction_id = cursor.lastrowid

        return True, transaction_id, []

    def get_transaction(self, user_id: int, transaction_id: int) -> Optional[Dict[str, Any]]:
        """Get a single transaction by ID (only if belongs to user)."""
        with self.db.get_db() as conn:
            txn = conn.execute(
                """SELECT transaction_id, user_id, type, amount, category, description, date, created_at
                   FROM transactions WHERE transaction_id = ? AND user_id = ?""",
                (transaction_id, user_id)
            ).fetchone()

            if txn:
                return dict(txn)
        return None

    def get_transactions(self, user_id: int, page: int = 1, per_page: int = 20,
                         txn_type: Optional[str] = None, category: Optional[str] = None,
                         start_date: Optional[str] = None, end_date: Optional[str] = None) -> Tuple[List[Dict], int]:
        """Get paginated transactions with optional filters."""
        offset = (page - 1) * per_page
        conditions = ["user_id = ?"]
        params = [user_id]

        if txn_type and txn_type in self.VALID_TYPES:
            conditions.append("type = ?")
            params.append(txn_type)

        if category and category in self.VALID_CATEGORIES:
            conditions.append("category = ?")
            params.append(category)

        if start_date:
            conditions.append("date >= ?")
            params.append(start_date)

        if end_date:
            conditions.append("date <= ?")
            params.append(end_date)

        where_clause = " AND ".join(conditions)

        with self.db.get_db() as conn:
            # Get total count
            total = conn.execute(
                f"SELECT COUNT(*) FROM transactions WHERE {where_clause}", params
            ).fetchone()[0]

            # Get transactions
            txns = conn.execute(
                f"""SELECT transaction_id, user_id, type, amount, category, description, date, created_at
                    FROM transactions WHERE {where_clause}
                    ORDER BY date DESC, created_at DESC
                    LIMIT ? OFFSET ?""",
                params + [per_page, offset]
            ).fetchall()

        return [dict(t) for t in txns], total

    def update_transaction(self, user_id: int, transaction_id: int,
                           txn_type: Optional[str] = None, amount: Optional[str] = None,
                           category: Optional[str] = None, date_str: Optional[str] = None,
                           description: Optional[str] = None) -> Tuple[bool, list]:
        """Update a transaction. Returns (success, errors)."""
        # Get existing transaction
        existing = self.get_transaction(user_id, transaction_id)
        if not existing:
            return False, [{'general': ErrorMessages.TRANSACTION_NOT_FOUND}]

        # Use existing values if not provided
        new_type = txn_type if txn_type is not None else existing['type']
        new_amount = amount if amount is not None else str(existing['amount'])
        new_category = category if category is not None else existing['category']
        new_date = date_str if date_str is not None else existing['date']
        new_description = description if description is not None else existing['description']

        # Validate
        is_valid, errors = self.validate_transaction(new_type, new_amount, new_category, new_date, new_description or "")
        if not is_valid:
            return False, errors

        with self.db.get_db() as conn:
            conn.execute(
                """UPDATE transactions 
                   SET type = ?, amount = ?, category = ?, description = ?, date = ?
                   WHERE transaction_id = ? AND user_id = ?""",
                (new_type, float(new_amount), new_category, new_description, new_date, transaction_id, user_id)
            )

        return True, []

    def delete_transaction(self, user_id: int, transaction_id: int) -> Tuple[bool, list]:
        """Delete a transaction. Returns (success, errors)."""
        existing = self.get_transaction(user_id, transaction_id)
        if not existing:
            return False, [{'general': ErrorMessages.TRANSACTION_NOT_FOUND}]

        with self.db.get_db() as conn:
            conn.execute(
                "DELETE FROM transactions WHERE transaction_id = ? AND user_id = ?",
                (transaction_id, user_id)
            )

        return True, []

    def get_totals(self, user_id: int, start_date: Optional[str] = None,
                   end_date: Optional[str] = None) -> Dict[str, Decimal]:
        """Get income, expense, and balance totals for a period."""
        conditions = ["user_id = ?"]
        params = [user_id]

        if start_date:
            conditions.append("date >= ?")
            params.append(start_date)
        if end_date:
            conditions.append("date <= ?")
            params.append(end_date)

        where_clause = " AND ".join(conditions)

        with self.db.get_db() as conn:
            income = conn.execute(
                f"SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE {where_clause} AND type = 'Income'",
                params
            ).fetchone()[0]

            expenses = conn.execute(
                f"SELECT COALESCE(SUM(amount), 0) FROM transactions WHERE {where_clause} AND type = 'Expense'",
                params
            ).fetchone()[0]

        return {
            'income': Decimal(str(income)),
            'expenses': Decimal(str(expenses)),
            'balance': Decimal(str(income)) - Decimal(str(expenses))
        }

    def get_recent_transactions(self, user_id: int, limit: int = 5) -> List[Dict]:
        """Get recent transactions for dashboard."""
        with self.db.get_db() as conn:
            txns = conn.execute(
                """SELECT transaction_id, user_id, type, amount, category, description, date, created_at
                   FROM transactions WHERE user_id = ?
                   ORDER BY date DESC, created_at DESC
                   LIMIT ?""",
                (user_id, limit)
            ).fetchall()

        return [dict(t) for t in txns]

    def get_category_totals(self, user_id: int, start_date: Optional[str] = None,
                            end_date: Optional[str] = None) -> List[Dict]:
        """Get expense totals by category for reports."""
        conditions = ["user_id = ?", "type = 'Expense'"]
        params = [user_id]

        if start_date:
            conditions.append("date >= ?")
            params.append(start_date)
        if end_date:
            conditions.append("date <= ?")
            params.append(end_date)

        where_clause = " AND ".join(conditions)

        with self.db.get_db() as conn:
            totals = conn.execute(
                f"""SELECT category, COALESCE(SUM(amount), 0) as total, COUNT(*) as count
                    FROM transactions WHERE {where_clause}
                    GROUP BY category ORDER BY total DESC""",
                params
            ).fetchall()

        return [dict(t) for t in totals]

    def get_monthly_trend(self, user_id: int, year: int) -> List[Dict]:
        """Get monthly income/expense trend for a year."""
        with self.db.get_db() as conn:
            trend = conn.execute(
                """SELECT 
                    CAST(strftime('%m', date) AS INTEGER) as month,
                    strftime('%Y', date) as year,
                    COALESCE(SUM(CASE WHEN type = 'Income' THEN amount ELSE 0 END), 0) as income,
                    COALESCE(SUM(CASE WHEN type = 'Expense' THEN amount ELSE 0 END), 0) as expenses
                   FROM transactions 
                   WHERE user_id = ? AND strftime('%Y', date) = ?
                   GROUP BY month, year
                   ORDER BY month""",
                (user_id, str(year))
            ).fetchall()

        return [dict(t) for t in trend]


# Global transaction service instance
transaction_service = TransactionService()
"""
Budget Service for Personal Expense Tracker
Handles budget creation, updates, and status checking.
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Dict, Any, Tuple, List

from backend.database.connection import get_db
from backend.services.transaction_service import transaction_service
from shared.constants.app_constants import (
    ErrorMessages, BudgetConstants, FormFieldNames
)


class BudgetService:
    """Service for budget management."""

    def __init__(self):
        self.db = get_db()

    def validate_budget(self, month: str, year: str, limit_amount: str) -> Tuple[bool, list]:
        """Validate budget input."""
        errors = []

        try:
            month_val = int(month)
            if month_val < 1 or month_val > 12:
                errors.append({FormFieldNames.MONTH: ErrorMessages.INVALID_MONTH})
        except Exception:
            errors.append({FormFieldNames.MONTH: ErrorMessages.INVALID_MONTH})

        try:
            year_val = int(year)
            if year_val < 2020 or year_val > 2030:
                errors.append({FormFieldNames.YEAR: ErrorMessages.INVALID_YEAR})
        except Exception:
            errors.append({FormFieldNames.YEAR: ErrorMessages.INVALID_YEAR})

        try:
            limit_val = Decimal(str(limit_amount))
            if limit_val <= 0:
                errors.append({FormFieldNames.LIMIT_AMOUNT: ErrorMessages.INVALID_AMOUNT})
            elif limit_val > BudgetConstants.MAX_LIMIT_AMOUNT:
                errors.append({FormFieldNames.LIMIT_AMOUNT: "Budget limit is too large"})
        except Exception:
            errors.append({FormFieldNames.LIMIT_AMOUNT: ErrorMessages.INVALID_AMOUNT})

        return len(errors) == 0, errors

    def create_budget(self, user_id: int, month: int, year: int, limit_amount: str) -> Tuple[bool, Optional[int], list]:
        """Create or update a budget. Returns (success, budget_id, errors)."""
        is_valid, errors = self.validate_budget(str(month), str(year), limit_amount)
        if not is_valid:
            return False, None, errors

        with self.db.get_db() as conn:
            # Check if budget exists
            existing = conn.execute(
                "SELECT budget_id FROM budgets WHERE user_id = ? AND month = ? AND year = ?",
                (user_id, month, year)
            ).fetchone()

            if existing:
                # Update existing budget
                conn.execute(
                    "UPDATE budgets SET limit_amount = ? WHERE budget_id = ?",
                    (float(limit_amount), existing['budget_id'])
                )
                budget_id = existing['budget_id']
            else:
                # Create new budget
                cursor = conn.execute(
                    "INSERT INTO budgets (user_id, month, year, limit_amount) VALUES (?, ?, ?, ?)",
                    (user_id, month, year, float(limit_amount))
                )
                budget_id = cursor.lastrowid

        return True, budget_id, []

    def get_budget(self, user_id: int, month: int, year: int) -> Optional[Dict[str, Any]]:
        """Get budget for a specific month/year."""
        with self.db.get_db() as conn:
            budget = conn.execute(
                "SELECT budget_id, user_id, month, year, limit_amount, created_at "
                "FROM budgets WHERE user_id = ? AND month = ? AND year = ?",
                (user_id, month, year)
            ).fetchone()

            if budget:
                return dict(budget)
        return None

    def get_current_budget(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get budget for current month."""
        today = date.today()
        return self.get_budget(user_id, today.month, today.year)

    def get_budget_status(self, user_id: int, month: int, year: int) -> Optional[Dict[str, Any]]:
        """Get budget with spent amount and status."""
        budget = self.get_budget(user_id, month, year)
        if not budget:
            return None

        # Calculate start and end date for the month
        from calendar import monthrange
        start_date = f"{year}-{month:02d}-01"
        _, last_day = monthrange(year, month)
        end_date = f"{year}-{month:02d}-{last_day:02d}"

        # Get expenses for this month
        totals = transaction_service.get_totals(user_id, start_date, end_date)
        spent = totals['expenses']
        limit = Decimal(str(budget['limit_amount']))
        remaining = limit - spent
        is_exceeded = spent >= limit

        return {
            'budget_id': budget['budget_id'],
            'user_id': budget['user_id'],
            'month': budget['month'],
            'year': budget['year'],
            'limit_amount': limit,
            'spent_amount': spent,
            'remaining_amount': remaining,
            'is_exceeded': is_exceeded,
            'created_at': budget['created_at']
        }

    def get_all_budgets(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all budgets for a user with status."""
        with self.db.get_db() as conn:
            budgets = conn.execute(
                "SELECT budget_id, user_id, month, year, limit_amount, created_at "
                "FROM budgets WHERE user_id = ? ORDER BY year DESC, month DESC",
                (user_id,)
            ).fetchall()

        result = []
        for budget in budgets:
            status = self.get_budget_status(user_id, budget['month'], budget['year'])
            if status:
                result.append(status)

        return result

    def delete_budget(self, user_id: int, budget_id: int) -> Tuple[bool, list]:
        """Delete a budget."""
        with self.db.get_db() as conn:
            cursor = conn.execute(
                "DELETE FROM budgets WHERE budget_id = ? AND user_id = ?",
                (budget_id, user_id)
            )
            if cursor.rowcount == 0:
                return False, [{'general': ErrorMessages.BUDGET_NOT_FOUND}]

        return True, []


# Global budget service instance
budget_service = BudgetService()
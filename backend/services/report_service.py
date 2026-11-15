"""
Report Service for Personal Expense Tracker
Handles report generation for transactions, categories, and trends.
"""
from datetime import date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from calendar import monthrange

from backend.database.connection import get_db
from backend.services.transaction_service import transaction_service
from backend.services.budget_service import budget_service
from shared.contracts.api_schemas import TransactionCategory


class ReportService:
    """Service for report generation."""

    def __init__(self):
        self.db = get_db()

    def get_monthly_report(self, user_id: int, month: int, year: int) -> Dict[str, Any]:
        """Get detailed report for a specific month."""
        # Calculate date range
        start_date = f"{year}-{month:02d}-01"
        _, last_day = monthrange(year, month)
        end_date = f"{year}-{month:02d}-{last_day:02d}"

        # Get totals
        totals = transaction_service.get_totals(user_id, start_date, end_date)

        # Get category breakdown
        category_totals = transaction_service.get_category_totals(user_id, start_date, end_date)
        total_expenses = totals['expenses']

        by_category = []
        for cat in category_totals:
            cat_total = Decimal(str(cat['total']))
            percentage = float(cat_total / total_expenses * 100) if total_expenses > 0 else 0
            by_category.append({
                'category': cat['category'],
                'total_amount': cat_total,
                'transaction_count': cat['count'],
                'percentage': round(percentage, 1)
            })

        # Get budget status
        budget_status = budget_service.get_budget_status(user_id, month, year)

        return {
            'user_id': user_id,
            'period_month': month,
            'period_year': year,
            'total_income': totals['income'],
            'total_expenses': totals['expenses'],
            'balance': totals['balance'],
            'by_category': by_category,
            'budget_status': budget_status
        }

    def get_yearly_report(self, user_id: int, year: int) -> Dict[str, Any]:
        """Get yearly report with monthly trend."""
        # Get monthly trend
        monthly_trend = transaction_service.get_monthly_trend(user_id, year)

        # Calculate totals
        total_income = sum(Decimal(str(m['income'])) for m in monthly_trend)
        total_expenses = sum(Decimal(str(m['expenses'])) for m in monthly_trend)

        # Get category totals for the year
        start_date = f"{year}-01-01"
        end_date = f"{year}-12-31"
        category_totals = transaction_service.get_category_totals(user_id, start_date, end_date)
        total_expenses_year = total_expenses

        by_category = []
        for cat in category_totals:
            cat_total = Decimal(str(cat['total']))
            percentage = float(cat_total / total_expenses_year * 100) if total_expenses_year > 0 else 0
            by_category.append({
                'category': cat['category'],
                'total_amount': cat_total,
                'transaction_count': cat['count'],
                'percentage': round(percentage, 1)
            })

        monthly_summary = []
        for m in monthly_trend:
            monthly_summary.append({
                'month': m['month'],
                'year': m['year'],
                'income': Decimal(str(m['income'])),
                'expenses': Decimal(str(m['expenses'])),
                'balance': Decimal(str(m['income'])) - Decimal(str(m['expenses']))
            })

        return {
            'user_id': user_id,
            'period_month': None,
            'period_year': year,
            'total_income': total_income,
            'total_expenses': total_expenses,
            'balance': total_income - total_expenses,
            'by_category': by_category,
            'monthly_trend': monthly_summary
        }

    def get_all_time_report(self, user_id: int) -> Dict[str, Any]:
        """Get all-time report."""
        totals = transaction_service.get_totals(user_id)

        category_totals = transaction_service.get_category_totals(user_id)
        total_expenses = totals['expenses']

        by_category = []
        for cat in category_totals:
            cat_total = Decimal(str(cat['total']))
            percentage = float(cat_total / total_expenses * 100) if total_expenses > 0 else 0
            by_category.append({
                'category': cat['category'],
                'total_amount': cat_total,
                'transaction_count': cat['count'],
                'percentage': round(percentage, 1)
            })

        return {
            'user_id': user_id,
            'period_month': None,
            'period_year': None,
            'total_income': totals['income'],
            'total_expenses': totals['expenses'],
            'balance': totals['balance'],
            'by_category': by_category,
            'monthly_trend': []
        }

    def get_dashboard_data(self, user_id: int) -> Dict[str, Any]:
        """Get all data needed for dashboard."""
        # Overall totals
        totals = transaction_service.get_totals(user_id)

        # Recent transactions
        recent_transactions = transaction_service.get_recent_transactions(user_id, 5)

        # Current budget status
        budget_status = budget_service.get_current_budget(user_id)
        if budget_status:
            budget_status = budget_service.get_budget_status(
                user_id, budget_status['month'], budget_status['year']
            )

        return {
            'user_id': user_id,
            'total_income': totals['income'],
            'total_expenses': totals['expenses'],
            'balance': totals['balance'],
            'recent_transactions': recent_transactions,
            'budget_status': budget_status
        }


# Global report service instance
report_service = ReportService()
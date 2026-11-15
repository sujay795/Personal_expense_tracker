"""
Application Constants for Personal Expense Tracker
Centralized configuration based on project specifications from PDFs.
"""

from enum import Enum
from decimal import Decimal


class AppConfig:
    """Application-level configuration constants."""
    APP_NAME = "Personal Expense Tracker"
    APP_VERSION = "1.0.0"
    CURRENCY_SYMBOL = "₹"
    CURRENCY_CODE = "INR"
    DEFAULT_DATE_FORMAT = "%Y-%m-%d"
    DISPLAY_DATE_FORMAT = "%d %b %Y"


class DatabaseConfig:
    """Database configuration constants."""
    DB_NAME = "expense_tracker.db"
    USERS_TABLE = "users"
    TRANSACTIONS_TABLE = "transactions"
    BUDGETS_TABLE = "budgets"
    
    # Table creation SQL (from backend PDF)
    CREATE_USERS_TABLE = f"""
    CREATE TABLE IF NOT EXISTS {USERS_TABLE} (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    )
    """
    
    CREATE_TRANSACTIONS_TABLE = f"""
    CREATE TABLE IF NOT EXISTS {TRANSACTIONS_TABLE} (
        transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        type TEXT NOT NULL CHECK(type IN ('Income', 'Expense')),
        amount REAL NOT NULL CHECK(amount > 0),
        category TEXT NOT NULL,
        description TEXT,
        date TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES {USERS_TABLE} (user_id)
    )
    """
    
    CREATE_BUDGETS_TABLE = f"""
    CREATE TABLE IF NOT EXISTS {BUDGETS_TABLE} (
        budget_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        month INTEGER NOT NULL CHECK(month BETWEEN 1 AND 12),
        year INTEGER NOT NULL CHECK(year BETWEEN 2020 AND 2030),
        limit_amount REAL NOT NULL CHECK(limit_amount > 0),
        FOREIGN KEY (user_id) REFERENCES {USERS_TABLE} (user_id),
        UNIQUE(user_id, month, year)
    )
    """


class AuthConfig:
    """Authentication and authorization constants."""
    SESSION_KEY = "user_id"
    SESSION_NAME_KEY = "user_name"
    PASSWORD_HASH_METHOD = "pbkdf2:sha256:600000$"  # Werkzeug default
    SESSION_PERMANENT = True


class TransactionConstants:
    """Transaction-related constants from project specs."""
    MAX_DESCRIPTION_LENGTH = 500
    MIN_AMOUNT = Decimal("0.01")
    MAX_AMOUNT = Decimal("999999999.99")
    DECIMAL_PLACES = 2

    # Categories from project specification (Frontend PDF)
    CATEGORIES = [
        "Food",
        "Travel",
        "Shopping",
        "Education",
        "Bills",
        "Entertainment",
        "Others"
    ]

    CATEGORY_ICONS = {
        "Food": "🍔",
        "Travel": "🚌",
        "Shopping": "🛍️",
        "Education": "📚",
        "Bills": "📄",
        "Entertainment": "🎮",
        "Others": "📦",
    }

    CATEGORY_COLORS = {
        "Food": "#FF6B6B",
        "Travel": "#4ECDC4",
        "Shopping": "#FFD93D",
        "Education": "#6BCB77",
        "Bills": "#FF6B9D",
        "Entertainment": "#C44DFF",
        "Others": "#94A3B8",
    }

    INCOME_CATEGORIES = {"Salary", "Freelance", "Investment", "Others"}
    EXPENSE_CATEGORIES = {"Food", "Travel", "Shopping", "Education", "Bills", "Entertainment", "Others"}


class BudgetConstants:
    """Budget-related constants from project specs."""
    MAX_LIMIT_AMOUNT = Decimal("999999999.99")
    MIN_LIMIT_AMOUNT = Decimal("0.01")
    DEFAULT_MONTH = None  # Current month
    DEFAULT_YEAR = None   # Current year


class ReportConstants:
    """Report generation constants."""
    CHART_COLORS = [
        "#FF6B6B", "#4ECDC4", "#FFD93D", "#6BCB77",
        "#FF6B9D", "#C44DFF", "#FF9F1C", "#2EC4B6"
    ]
    MAX_REPORT_MONTHS = 12


class HTTPStatus:
    """HTTP status codes used in the application."""
    OK = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    INTERNAL_SERVER_ERROR = 500


class ErrorMessages:
    """Standardized error messages from project specs."""
    # Auth errors
    INVALID_CREDENTIALS = "Invalid email or password"
    EMAIL_EXISTS = "Email already registered"
    USER_NOT_FOUND = "User not found"
    UNAUTHORIZED = "Please log in to access this page"
    SESSION_EXPIRED = "Session expired, please log in again"

    # Validation errors
    REQUIRED_FIELD = "This field is required"
    INVALID_EMAIL = "Invalid email format"
    PASSWORD_MISMATCH = "Passwords do not match"
    PASSWORD_TOO_SHORT = "Password must be at least 6 characters"
    INVALID_AMOUNT = "Amount must be greater than zero"
    INVALID_TYPE = "Type must be Income or Expense"
    INVALID_CATEGORY = "Invalid category selected"
    INVALID_DATE = "Invalid date format"
    INVALID_MONTH = "Month must be between 1 and 12"
    INVALID_YEAR = "Year must be between 2020 and 2030"
    BUDGET_EXISTS = "Budget already exists for this month/year"

    # Resource errors
    TRANSACTION_NOT_FOUND = "Transaction not found"
    BUDGET_NOT_FOUND = "Budget not found"
    ACCESS_DENIED = "You can only access your own records"


class FrontendRoutes:
    """Frontend route constants from project specs."""
    LOGIN = "/login"
    REGISTER = "/register"
    LOGOUT = "/logout"
    DASHBOARD = "/dashboard"
    TRANSACTIONS = "/transactions"
    ADD_TRANSACTION = "/transactions/add"
    EDIT_TRANSACTION = "/transactions/<int:id>/edit"
    DELETE_TRANSACTION = "/transactions/<int:id>/delete"
    REPORTS = "/reports"
    BUDGET = "/budget"


class BackendRoutes:
    """Backend API route constants (suggested from PDFs)."""
    # Auth
    REGISTER = "/register"
    LOGIN = "/login"
    LOGOUT = "/logout"

    # Dashboard
    DASHBOARD = "/dashboard"

    # Transactions
    TRANSACTIONS = "/transactions"
    TRANSACTION_CREATE = "/transactions"  # POST
    TRANSACTION_EDIT = "/transactions/<int:id>/edit"  # POST
    TRANSACTION_DELETE = "/transactions/<int:id>/delete"  # POST

    # Reports
    REPORTS = "/reports"

    # Budget
    BUDGET = "/budget"


class FormFieldNames:
    """Form field names for frontend-backend integration (from PDF contracts)."""
    # Auth
    NAME = "name"
    EMAIL = "email"
    PASSWORD = "password"
    CONFIRM_PASSWORD = "confirm_password"

    # Transaction
    TRANSACTION_TYPE = "type"
    AMOUNT = "amount"
    CATEGORY = "category"
    DESCRIPTION = "description"
    DATE = "date"

    # Budget
    MONTH = "month"
    YEAR = "year"
    LIMIT_AMOUNT = "limit_amount"

    # Reports
    REPORT_MONTH = "month"
    REPORT_YEAR = "year"


class TemplateVariables:
    """Template variable names passed from backend to frontend."""
    # User
    USER_ID = "user_id"
    USER_NAME = "user_name"

    # Dashboard
    TOTAL_INCOME = "total_income"
    TOTAL_EXPENSES = "total_expenses"
    BALANCE = "balance"
    RECENT_TRANSACTIONS = "recent_transactions"

    # Transactions
    TRANSACTIONS = "transactions"
    TRANSACTION = "transaction"

    # Reports
    REPORT_DATA = "report_data"
    CATEGORY_TOTALS = "category_totals"
    MONTHLY_TOTALS = "monthly_totals"
    SELECTED_MONTH = "selected_month"
    SELECTED_YEAR = "selected_year"

    # Budget
    BUDGET = "budget"
    BUDGET_STATUS = "budget_status"
    SPENT_AMOUNT = "spent_amount"
    REMAINING_AMOUNT = "remaining_amount"
    IS_EXCEEDED = "is_exceeded"

    # Errors
    ERROR = "error"
    ERRORS = "errors"
    SUCCESS = "success"
"""
Sample Data for Personal Expense Tracker
Based on project specifications from PDFs.
Used for testing, development, and seeding the database.
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from shared.contracts.api_schemas import (
    TransactionType, TransactionCategory,
    RegisterRequest, TransactionCreate, BudgetCreate, ReportFilter
)


# ===== SAMPLE USERS =====
SAMPLE_USERS = [
    RegisterRequest(
        name="John Doe",
        email="john.doe@example.com",
        password="password123",
        confirm_password="password123"
    ),
    RegisterRequest(
        name="Jane Smith",
        email="jane.smith@example.com",
        password="password123",
        confirm_password="password123"
    ),
]


# ===== SAMPLE TRANSACTIONS =====
def generate_sample_transactions(user_id: int, count: int = 30) -> list[TransactionCreate]:
    """Generate sample transactions for a user based on project categories."""
    import random

    categories = [
        TransactionCategory.FOOD,
        TransactionCategory.TRAVEL,
        TransactionCategory.SHOPPING,
        TransactionCategory.EDUCATION,
        TransactionCategory.BILLS,
        TransactionCategory.ENTERTAINMENT,
        TransactionCategory.OTHERS,
    ]

    descriptions = {
        TransactionCategory.FOOD: ["Groceries", "Restaurant", "Coffee", "Food delivery", "Snacks"],
        TransactionCategory.TRAVEL: ["Gas", "Bus fare", "Train ticket", "Uber", "Car maintenance"],
        TransactionCategory.SHOPPING: ["Clothes", "Electronics", "Home goods", "Gifts", "Online shopping"],
        TransactionCategory.EDUCATION: ["Online course", "Books", "Certification", "Workshop", "Tuition"],
        TransactionCategory.BILLS: ["Electricity bill", "Water bill", "Internet", "Phone bill", "Gas bill"],
        TransactionCategory.ENTERTAINMENT: ["Movie tickets", "Streaming subscription", "Games", "Concert", "Events"],
        TransactionCategory.OTHERS: ["Miscellaneous", "Donation", "Repairs", "Medical", "Other"],
    }

    transactions = []
    base_date = date.today() - timedelta(days=90)  # 3 months ago

    for i in range(count):
        # 80% expenses, 20% income
        is_income = random.random() < 0.2

        if is_income:
            txn_type = TransactionType.INCOME
            category = TransactionCategory.OTHERS  # Income uses Others or custom
            amount = Decimal(str(round(random.uniform(5000, 50000), 2)))
        else:
            txn_type = TransactionType.EXPENSE
            category = random.choice(categories)
            amount = Decimal(str(round(random.uniform(50, 3000), 2)))

        transaction_date = base_date + timedelta(days=random.randint(0, 90))
        description = random.choice(descriptions.get(category, ["Miscellaneous"]))

        transactions.append(TransactionCreate(
            type=txn_type,
            amount=amount,
            category=category,
            description=description,
            date=transaction_date,
        ))

    return transactions


SAMPLE_TRANSACTIONS_USER_1 = generate_sample_transactions(1, 30)
SAMPLE_TRANSACTIONS_USER_2 = generate_sample_transactions(2, 20)


# ===== SAMPLE BUDGETS =====
from datetime import date as dt_date
today = dt_date.today()

SAMPLE_BUDGETS = [
    BudgetCreate(
        month=today.month,
        year=today.year,
        limit_amount=Decimal("15000.00"),
    ),
    BudgetCreate(
        month=today.month - 1 if today.month > 1 else 12,
        year=today.year if today.month > 1 else today.year - 1,
        limit_amount=Decimal("12000.00"),
    ),
]


# ===== SAMPLE REPORT FILTERS =====
SAMPLE_REPORT_FILTERS = {
    "current_month": ReportFilter(
        month=today.month,
        year=today.year,
    ),
    "last_month": ReportFilter(
        month=today.month - 1 if today.month > 1 else 12,
        year=today.year if today.month > 1 else today.year - 1,
    ),
    "year_to_date": ReportFilter(
        month=None,
        year=today.year,
    ),
}


# ===== MOCK API RESPONSES =====
MOCK_DASHBOARD_RESPONSE = {
    "user_id": 1,
    "total_income": "45000.00",
    "total_expenses": "28500.75",
    "balance": "16499.25",
    "recent_transactions": [
        {
            "transaction_id": 1,
            "user_id": 1,
            "type": "Expense",
            "amount": "1500.00",
            "category": "Food",
            "description": "Weekly groceries",
            "date": "2024-12-15",
            "created_at": "2024-12-15T14:30:00Z",
        },
        {
            "transaction_id": 2,
            "user_id": 1,
            "type": "Expense",
            "amount": "800.00",
            "category": "Travel",
            "description": "Gas refill",
            "date": "2024-12-14",
            "created_at": "2024-12-14T16:00:00Z",
        },
        {
            "transaction_id": 3,
            "user_id": 1,
            "type": "Income",
            "amount": "25000.00",
            "category": "Others",
            "description": "Monthly salary",
            "date": "2024-12-01",
            "created_at": "2024-12-01T09:00:00Z",
        },
    ],
    "budget_status": {
        "budget_id": 1,
        "user_id": 1,
        "month": 12,
        "year": 2024,
        "limit_amount": "15000.00",
        "spent_amount": "12500.50",
        "remaining_amount": "2499.50",
        "is_exceeded": False,
        "created_at": "2024-12-01T00:00:00Z",
    }
}

MOCK_TRANSACTION_RESPONSE = {
    "transaction_id": 1,
    "user_id": 1,
    "type": "Expense",
    "amount": "1500.00",
    "category": "Food",
    "description": "Weekly groceries",
    "date": "2024-12-15",
    "created_at": "2024-12-15T14:30:00Z",
}

MOCK_BUDGET_RESPONSE = {
    "budget_id": 1,
    "user_id": 1,
    "month": 12,
    "year": 2024,
    "limit_amount": "15000.00",
    "spent_amount": "12500.50",
    "remaining_amount": "2499.50",
    "is_exceeded": False,
    "created_at": "2024-12-01T00:00:00Z",
}

MOCK_REPORT_RESPONSE = {
    "user_id": 1,
    "period_month": 12,
    "period_year": 2024,
    "total_income": "45000.00",
    "total_expenses": "28500.75",
    "balance": "16499.25",
    "by_category": [
        {"category": "Food", "total_amount": "8500.00", "transaction_count": 12, "percentage": 29.8},
        {"category": "Travel", "total_amount": "3200.00", "transaction_count": 8, "percentage": 11.2},
        {"category": "Shopping", "total_amount": "2500.00", "transaction_count": 5, "percentage": 8.8},
        {"category": "Bills", "total_amount": "4500.00", "transaction_count": 4, "percentage": 15.8},
        {"category": "Entertainment", "total_amount": "1800.00", "transaction_count": 3, "percentage": 6.3},
        {"category": "Education", "total_amount": "2000.00", "transaction_count": 2, "percentage": 7.0},
        {"category": "Others", "total_amount": "6000.75", "transaction_count": 6, "percentage": 21.1},
    ],
    "monthly_trend": [
        {"month": 10, "year": 2024, "income": "42000.00", "expenses": "26000.00", "balance": "16000.00"},
        {"month": 11, "year": 2024, "income": "43000.00", "expenses": "29500.00", "balance": "13500.00"},
        {"month": 12, "year": 2024, "income": "45000.00", "expenses": "28500.75", "balance": "16499.25"},
    ],
}


# ===== SEED SQL FOR SQLITE =====
SEED_SQL = """
-- Sample seed data for Personal Expense Tracker
-- Run after table creation

-- Users (passwords are hashed 'password123' using werkzeug)
-- Hash: pbkdf2:sha256:600000$...
INSERT INTO users (name, email, password_hash) VALUES
('John Doe', 'john.doe@example.com', 'pbkdf2:sha256:600000$salt1$hash1'),
('Jane Smith', 'jane.smith@example.com', 'pbkdf2:sha256:600000$salt2$hash2');

-- Budgets for user 1 (current month and last month)
INSERT INTO budgets (user_id, month, year, limit_amount) VALUES
(1, 12, 2024, 15000.00),
(1, 11, 2024, 12000.00);

-- Budgets for user 2
INSERT INTO budgets (user_id, month, year, limit_amount) VALUES
(2, 12, 2024, 10000.00);

-- Sample transactions for user 1 (last 3 months)
-- Incomes
INSERT INTO transactions (user_id, type, amount, category, description, date) VALUES
(1, 'Income', 25000.00, 'Others', 'Monthly salary', '2024-12-01'),
(1, 'Income', 5000.00, 'Others', 'Freelance project', '2024-12-10'),
(1, 'Income', 23000.00, 'Others', 'Monthly salary', '2024-11-01'),
(1, 'Income', 22000.00, 'Others', 'Monthly salary', '2024-10-01');

-- Expenses (categorized)
INSERT INTO transactions (user_id, type, amount, category, description, date) VALUES
-- December
(1, 'Expense', 1500.00, 'Food', 'Weekly groceries', '2024-12-02'),
(1, 'Expense', 800.00, 'Travel', 'Gas refill', '2024-12-03'),
(1, 'Expense', 1200.00, 'Food', 'Restaurant dinner', '2024-12-05'),
(1, 'Expense', 500.00, 'Entertainment', 'Movie tickets', '2024-12-07'),
(1, 'Expense', 2000.00, 'Bills', 'Electricity bill', '2024-12-10'),
(1, 'Expense', 3000.00, 'Shopping', 'New headphones', '2024-12-12'),
(1, 'Expense', 900.00, 'Food', 'Groceries', '2024-12-14'),
(1, 'Expense', 600.00, 'Travel', 'Bus pass', '2024-12-16'),
(1, 'Expense', 1500.00, 'Entertainment', 'Concert tickets', '2024-12-18'),
(1, 'Expense', 2500.00, 'Bills', 'Internet & phone', '2024-12-20'),
-- November
(1, 'Expense', 1200.00, 'Food', 'Groceries', '2024-11-02'),
(1, 'Expense', 700.00, 'Travel', 'Gas', '2024-11-03'),
(1, 'Expense', 1800.00, 'Shopping', 'Clothes', '2024-11-05'),
(1, 'Expense', 1500.00, 'Bills', 'Water bill', '2024-11-10'),
(1, 'Expense', 900.00, 'Food', 'Restaurant', '2024-11-15'),
(1, 'Expense', 600.00, 'Entertainment', 'Streaming', '2024-11-18'),
(1, 'Expense', 2000.00, 'Education', 'Online course', '2024-11-20'),
(1, 'Expense', 800.00, 'Travel', 'Train ticket', '2024-11-25'),
-- October
(1, 'Expense', 1100.00, 'Food', 'Groceries', '2024-10-02'),
(1, 'Expense', 650.00, 'Travel', 'Gas', '2024-10-03'),
(1, 'Expense', 1500.00, 'Bills', 'Electricity', '2024-10-05'),
(1, 'Expense', 2200.00, 'Shopping', 'Electronics', '2024-10-10'),
(1, 'Expense', 850.00, 'Food', 'Restaurant', '2024-10-15'),
(1, 'Expense', 400.00, 'Entertainment', 'Games', '2024-10-20');

-- Sample transactions for user 2
INSERT INTO transactions (user_id, type, amount, category, description, date) VALUES
(2, 'Income', 18000.00, 'Others', 'Salary', '2024-12-01'),
(2, 'Expense', 800.00, 'Food', 'Groceries', '2024-12-02'),
(2, 'Expense', 400.00, 'Travel', 'Bus fare', '2024-12-03'),
(2, 'Expense', 1200.00, 'Bills', 'Rent', '2024-12-05'),
(2, 'Expense', 600.00, 'Shopping', 'Clothes', '2024-12-10'),
(2, 'Expense', 300.00, 'Food', 'Restaurant', '2024-12-15');
"""


# ===== TEST DATA HELPERS =====
class TestDataFactory:
    """Factory for creating test data programmatically."""

    @staticmethod
    def create_user(name: str = "Test User", email: str = "test@example.com") -> RegisterRequest:
        return RegisterRequest(
            name=name,
            email=email,
            password="TestPass123!",
            confirm_password="TestPass123!"
        )

    @staticmethod
    def create_transaction(
        txn_type: TransactionType = TransactionType.EXPENSE,
        amount: Decimal = Decimal("100.00"),
        category: TransactionCategory = TransactionCategory.FOOD,
        date_val: date = None,
    ) -> TransactionCreate:
        return TransactionCreate(
            type=txn_type,
            amount=amount,
            category=category,
            description="Test transaction",
            date=date_val or date.today(),
        )

    @staticmethod
    def create_budget(
        month: int = None,
        year: int = None,
        limit_amount: Decimal = Decimal("5000.00"),
    ) -> BudgetCreate:
        today = date.today()
        return BudgetCreate(
            month=month or today.month,
            year=year or today.year,
            limit_amount=limit_amount,
        )


# ===== EXPORTS =====
__all__ = [
    "SAMPLE_USERS",
    "SAMPLE_TRANSACTIONS_USER_1",
    "SAMPLE_TRANSACTIONS_USER_2",
    "SAMPLE_BUDGETS",
    "SAMPLE_REPORT_FILTERS",
    "MOCK_DASHBOARD_RESPONSE",
    "MOCK_TRANSACTION_RESPONSE",
    "MOCK_BUDGET_RESPONSE",
    "MOCK_REPORT_RESPONSE",
    "TestDataFactory",
    "SEED_SQL",
]
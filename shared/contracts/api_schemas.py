"""
API Contracts / Schemas for Personal Expense Tracker
Defines request/response structures based on project specifications.
"""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr


class TransactionType(str, Enum):
    INCOME = "Income"
    EXPENSE = "Expense"


class TransactionCategory(str, Enum):
    FOOD = "Food"
    TRAVEL = "Travel"
    SHOPPING = "Shopping"
    EDUCATION = "Education"
    BILLS = "Bills"
    ENTERTAINMENT = "Entertainment"
    OTHERS = "Others"


# ===== AUTH CONTRACTS =====
class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    confirm_password: str = Field(..., min_length=6, max_length=100)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    created_at: datetime


# ===== TRANSACTION CONTRACTS =====
class TransactionCreate(BaseModel):
    type: TransactionType
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    category: TransactionCategory
    description: Optional[str] = Field(None, max_length=500)
    date: date


class TransactionUpdate(BaseModel):
    type: Optional[TransactionType] = None
    amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    category: Optional[TransactionCategory] = None
    description: Optional[str] = Field(None, max_length=500)
    date: Optional[date] = None


class TransactionResponse(BaseModel):
    transaction_id: int
    user_id: int
    type: TransactionType
    amount: Decimal
    category: TransactionCategory
    description: Optional[str]
    date: date
    created_at: datetime


class TransactionListResponse(BaseModel):
    transactions: List[TransactionResponse]
    total: int


# ===== BUDGET CONTRACTS =====
class BudgetCreate(BaseModel):
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2020, le=2030)
    limit_amount: Decimal = Field(..., gt=0, decimal_places=2)


class BudgetUpdate(BaseModel):
    limit_amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2)


class BudgetResponse(BaseModel):
    budget_id: int
    user_id: int
    month: int
    year: int
    limit_amount: Decimal
    spent_amount: Decimal
    remaining_amount: Decimal
    is_exceeded: bool
    created_at: datetime


# ===== REPORT CONTRACTS =====
class ReportFilter(BaseModel):
    month: Optional[int] = Field(None, ge=1, le=12)
    year: Optional[int] = Field(None, ge=2020, le=2030)


class CategorySummary(BaseModel):
    category: TransactionCategory
    total_amount: Decimal
    transaction_count: int
    percentage: float


class MonthlySummary(BaseModel):
    month: int
    year: int
    income: Decimal
    expenses: Decimal
    balance: Decimal


class ReportResponse(BaseModel):
    user_id: int
    period_month: Optional[int]
    period_year: Optional[int]
    total_income: Decimal
    total_expenses: Decimal
    balance: Decimal
    by_category: List[CategorySummary]
    monthly_trend: List[MonthlySummary]


# ===== DASHBOARD CONTRACTS =====
class DashboardResponse(BaseModel):
    user_id: int
    total_income: Decimal
    total_expenses: Decimal
    balance: Decimal
    recent_transactions: List[TransactionResponse]
    budget_status: Optional[BudgetResponse] = None


# ===== ERROR CONTRACTS =====
class ErrorResponse(BaseModel):
    error: str
    message: str
    status_code: int


class ValidationErrorResponse(BaseModel):
    error: str = "Validation Error"
    message: str
    details: List[dict]
    status_code: int = 400
"""
Database Connection Module for Personal Expense Tracker
Handles SQLite connection, initialization, and helper functions.
"""
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

from backend.config import config


class Database:
    """Database connection and management."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(config['default'].DATABASE_PATH)

    def get_connection(self) -> sqlite3.Connection:
        """Get a new database connection with row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    @contextmanager
    def get_db(self):
        """Context manager for database connection."""
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def init_db(self) -> None:
        """Initialize database tables."""
        with self.get_db() as conn:
            conn.executescript(self._get_schema())

    def _get_schema(self) -> str:
        """Return the complete database schema."""
        return """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('Income', 'Expense')),
            amount REAL NOT NULL CHECK(amount > 0),
            category TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS budgets (
            budget_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            month INTEGER NOT NULL CHECK(month BETWEEN 1 AND 12),
            year INTEGER NOT NULL CHECK(year BETWEEN 2020 AND 2030),
            limit_amount REAL NOT NULL CHECK(limit_amount > 0),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
            UNIQUE(user_id, month, year)
        );

        CREATE INDEX IF NOT EXISTS idx_transactions_user_date 
            ON transactions(user_id, date);
        CREATE INDEX IF NOT EXISTS idx_transactions_user_type 
            ON transactions(user_id, type);
        CREATE INDEX IF NOT EXISTS idx_budgets_user_month_year 
            ON budgets(user_id, month, year);
        """


# Global database instance
db = Database()


def get_db():
    """Get database instance."""
    return db


def init_db(db_path: Optional[str] = None) -> None:
    """Initialize database with given path."""
    global db
    if db_path:
        db = Database(db_path)
    db.init_db()
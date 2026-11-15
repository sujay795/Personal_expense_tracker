"""
Backend Configuration for Personal Expense Tracker
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600 * 24 * 7  # 7 days


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    DATABASE_PATH = BASE_DIR / 'expense_tracker.db'


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    DATABASE_PATH = BASE_DIR / 'expense_tracker.db'
    SESSION_COOKIE_SECURE = True


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    DATABASE_PATH = BASE_DIR / 'test_expense_tracker.db'


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig,
}
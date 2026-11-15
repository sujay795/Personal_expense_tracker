"""
Flask Application Factory for Personal Expense Tracker
Main entry point for the backend application.
"""
import os
from flask import Flask

from backend.config import config
from backend.database.connection import init_db
from backend.api.auth_routes import auth_bp
from backend.api.main_routes import main_bp
from backend.api.transaction_routes import transaction_bp
from backend.api.budget_routes import budget_bp
from backend.api.report_routes import report_bp


def create_app(config_name: str = None) -> Flask:
    """Create and configure the Flask application."""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')

    app = Flask(__name__,
                template_folder=os.path.join(os.path.dirname(__file__), '..', 'frontend', 'templates'),
                static_folder=os.path.join(os.path.dirname(__file__), '..', 'frontend', 'static'))

    # Load configuration
    app.config.from_object(config[config_name])

    # Initialize database
    init_db(app.config.get('DATABASE_PATH'))

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(transaction_bp)
    app.register_blueprint(budget_bp)
    app.register_blueprint(report_bp)

    # Context processor for template globals
    @app.context_processor
    def inject_globals():
        from shared.constants.app_constants import AppConfig
        return {
            'app_name': AppConfig.APP_NAME,
            'currency_symbol': AppConfig.CURRENCY_SYMBOL,
        }

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        return render_template('errors/500.html'), 500

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
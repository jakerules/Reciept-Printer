"""
Configuration settings for the Email Task Manager application.
This module contains different configuration classes for various environments.
"""
import os
from datetime import timedelta

class Config:
    """Base configuration class with common settings."""
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-please-change-in-production')
    DEBUG = False
    TESTING = False
    
    # SQLAlchemy settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email settings
    GMAIL_API_CREDENTIALS = os.environ.get('GMAIL_API_CREDENTIALS', 'credentials.json')
    GMAIL_API_TOKEN = os.environ.get('GMAIL_API_TOKEN', 'token.json')
    EMAIL_CHECK_INTERVAL = int(os.environ.get('EMAIL_CHECK_INTERVAL', 300))  # in seconds
    
    # Printer settings
    DEFAULT_PRINTER = os.environ.get('DEFAULT_PRINTER', '')
    RECEIPT_WIDTH = int(os.environ.get('RECEIPT_WIDTH', 80))  # characters
    PRINT_HEADER = os.environ.get('PRINT_HEADER', 'Task Receipt')
    PRINT_FOOTER = os.environ.get('PRINT_FOOTER', 'Thank you!')
    
    # NLP settings
    SPACY_MODEL = os.environ.get('SPACY_MODEL', 'en_core_web_sm')
    USE_OPENAI = os.environ.get('USE_OPENAI', 'False').lower() == 'true'
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
    
    # Task settings
    DEFAULT_TASK_PRIORITY = os.environ.get('DEFAULT_TASK_PRIORITY', 'Medium')
    TASK_PRIORITIES = ['Low', 'Medium', 'High', 'Urgent']
    TASK_STATUSES = ['New', 'In Progress', 'Completed', 'Cancelled']


class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL', 'sqlite:///dev.db')
    
    # For development, we might want to check emails more frequently
    EMAIL_CHECK_INTERVAL = int(os.environ.get('EMAIL_CHECK_INTERVAL', 60))


class TestingConfig(Config):
    """Testing environment configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL', 'sqlite:///test.db')
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production environment configuration."""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///prod.db')
    
    # In production, we should use a proper secret key
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-should-set-a-secret-key-environment-variable'
    
    # SSL settings for production
    SSL_REDIRECT = os.environ.get('SSL_REDIRECT', 'False').lower() == 'true'
    
    @classmethod
    def init_app(cls, app):
        """Initialize production application."""
        # Log to stderr in production
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        # Handle proxy server headers
        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)


# Default configuration to use
DefaultConfig = DevelopmentConfig
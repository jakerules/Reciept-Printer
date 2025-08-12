"""
Main application initialization module.
This module initializes the Flask application and configures all its components.
"""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app(config=None):
    """
    Create and configure the Flask application.
    
    Args:
        config: Configuration object or path to configuration file
        
    Returns:
        Flask application instance
    """
    app = Flask(__name__, instance_relative_config=True)
    
    # Load default configuration
    app.config.from_object('config.config.DefaultConfig')
    
    # Load environment specific configuration
    if config:
        if isinstance(config, str):
            app.config.from_pyfile(config)
        else:
            app.config.from_object(config)
    
    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Register blueprints
    with app.app_context():
        # Import blueprints
        from app.controllers.auth import auth_bp
        from app.controllers.main import main_bp
        from app.controllers.tasks import tasks_bp
        from app.controllers.emails import emails_bp
        from app.controllers.printer import printer_bp
        
        # Register blueprints
        app.register_blueprint(auth_bp)
        app.register_blueprint(main_bp)
        app.register_blueprint(tasks_bp)
        app.register_blueprint(emails_bp)
        app.register_blueprint(printer_bp)
        
        # Create database tables if they don't exist
        db.create_all()
    
    # Register error handlers
    from app.controllers.errors import register_error_handlers
    register_error_handlers(app)
    
    return app
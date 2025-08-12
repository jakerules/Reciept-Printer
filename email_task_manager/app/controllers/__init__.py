"""
Controllers package initialization.
"""
from app.controllers.auth import auth_bp
from app.controllers.main import main_bp
from app.controllers.tasks import tasks_bp
from app.controllers.emails import emails_bp
from app.controllers.printer import printer_bp
from app.controllers.errors import register_error_handlers

# Add any additional controllers here
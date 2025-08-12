"""
Main application entry point.
"""
import os
from app import create_app, db
from app.models import User, Email, Task, PrinterConfig
from app.services import start_background_services, stop_background_services

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """
    Make objects available in the shell context.
    This allows you to work with these objects in the Flask shell.
    """
    return {
        'db': db,
        'User': User,
        'Email': Email,
        'Task': Task,
        'PrinterConfig': PrinterConfig
    }

@app.before_first_request
def before_first_request():
    """
    Run before the first request is processed.
    This is a good place to start background services.
    """
    # Start background services
    start_background_services(app)

@app.teardown_appcontext
def teardown_appcontext(exception=None):
    """
    Run when the application context ends.
    This is a good place to clean up resources.
    """
    # Stop background services on shutdown
    stop_background_services()

if __name__ == '__main__':
    # Create a default admin user if no users exist
    with app.app_context():
        if User.query.count() == 0:
            admin = User(
                username='admin',
                email='admin@example.com',
                is_admin=True
            )
            admin.password = 'admin'  # This will be hashed
            db.session.add(admin)
            db.session.commit()
            print('Created default admin user: admin / admin')
        
        # Create a default printer configuration if none exists
        if PrinterConfig.query.count() == 0:
            config = PrinterConfig(
                name='Default Printer',
                description='Default printer configuration',
                printer_type='cups' if os.name != 'nt' else 'windows',
                printer_name='',  # Will use system default
                paper_width=80,
                header_text='Task Receipt',
                footer_text='Thank you!',
                is_default=True,
                is_active=True
            )
            db.session.add(config)
            db.session.commit()
            print('Created default printer configuration')
    
    # Run the application
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    app.run(host=host, port=port, debug=debug)
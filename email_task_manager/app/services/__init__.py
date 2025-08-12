"""
Services package initialization.
"""
import schedule
import time
import threading
from flask import current_app

# Import service modules
from app.services.email import create_gmail_service, process_emails
from app.services.printer import print_new_tasks

# Background scheduler thread
scheduler_thread = None
stop_scheduler = False

def start_background_services(app):
    """
    Start background services for email checking and task printing.
    
    Args:
        app: Flask application instance
    """
    global scheduler_thread, stop_scheduler
    
    if scheduler_thread and scheduler_thread.is_alive():
        return  # Already running
    
    stop_scheduler = False
    
    # Define the scheduler function
    def run_scheduler():
        with app.app_context():
            # Schedule email checking
            email_interval = app.config.get('EMAIL_CHECK_INTERVAL', 300)  # Default to 5 minutes
            schedule.every(email_interval).seconds.do(lambda: check_emails(app))
            
            # Schedule task printing
            schedule.every(60).seconds.do(lambda: print_new_tasks(app))
            
            # Run the scheduler
            while not stop_scheduler:
                schedule.run_pending()
                time.sleep(1)
    
    # Start the scheduler thread
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    app.logger.info("Background services started")

def stop_background_services():
    """Stop background services."""
    global stop_scheduler
    stop_scheduler = True
    
    if scheduler_thread:
        scheduler_thread.join(timeout=5)

def check_emails(app):
    """
    Check for new emails and process them.
    
    Args:
        app: Flask application instance
        
    Returns:
        Number of emails fetched
    """
    try:
        # Create Gmail service
        gmail_service = create_gmail_service(app)
        
        # Fetch new emails
        emails = gmail_service.fetch_unprocessed_emails()
        
        if emails:
            app.logger.info(f"Fetched {len(emails)} new emails")
            
            # Process the emails
            processed = process_emails(app)
            app.logger.info(f"Processed {processed} emails")
            
            # Mark emails as read in Gmail
            for email in emails:
                gmail_service.mark_as_read(email.gmail_id)
        
        return len(emails)
        
    except Exception as e:
        app.logger.error(f"Error checking emails: {str(e)}")
        return 0
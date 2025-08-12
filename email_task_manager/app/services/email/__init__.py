"""
Email services package initialization.
"""
import os
import json
from app.services.email.gmail_service import GmailService
from app.services.email.email_parser import EmailParser
from app import db
from app.models import Email

def create_gmail_service(app):
    """
    Create a Gmail service instance.
    
    Args:
        app: Flask application instance
        
    Returns:
        GmailService instance
    """
    credentials_path = app.config.get('GMAIL_API_CREDENTIALS')
    token_path = app.config.get('GMAIL_API_TOKEN')
    
    # Ensure the credentials file exists
    if not os.path.exists(credentials_path):
        raise FileNotFoundError(f"Gmail API credentials file not found: {credentials_path}")
    
    return GmailService(credentials_path, token_path)

def create_email_parser(app):
    """
    Create an email parser instance.
    
    Args:
        app: Flask application instance
        
    Returns:
        EmailParser instance
    """
    spacy_model = app.config.get('SPACY_MODEL')
    use_openai = app.config.get('USE_OPENAI')
    openai_api_key = app.config.get('OPENAI_API_KEY')
    
    return EmailParser(spacy_model, use_openai, openai_api_key)

def process_emails(app):
    """
    Process unprocessed emails.
    
    Args:
        app: Flask application instance
        
    Returns:
        Number of emails processed
    """
    with app.app_context():
        # Get unprocessed emails
        unprocessed_emails = Email.query.filter_by(is_processed=False).all()
        
        if not unprocessed_emails:
            return 0
        
        # Create email parser
        parser = create_email_parser(app)
        
        # Process each email
        processed_count = 0
        for email in unprocessed_emails:
            try:
                # Parse email and extract tasks
                tasks = parser.parse_email(email)
                
                # Mark email as processed
                email.is_processed = True
                email.processed_at = datetime.utcnow()
                db.session.commit()
                
                processed_count += 1
                
            except Exception as e:
                # Log the error
                email.processing_error = str(e)
                db.session.commit()
        
        return processed_count
"""
Emails controller for managing emails.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required
from app import db
from app.models import Email, Task
from app.services.email import create_gmail_service, create_email_parser

# Create blueprint
emails_bp = Blueprint('emails', __name__, url_prefix='/emails')

@emails_bp.route('/')
@login_required
def index():
    """Display all emails."""
    # Get filter parameters
    processed = request.args.get('processed', 'all')
    
    # Build query
    query = Email.query
    
    if processed != 'all':
        is_processed = processed == 'yes'
        query = query.filter_by(is_processed=is_processed)
    
    # Order by received date (newest first)
    emails = query.order_by(Email.received_at.desc()).all()
    
    return render_template(
        'emails/index.html',
        emails=emails,
        processed=processed
    )

@emails_bp.route('/<int:email_id>')
@login_required
def view(email_id):
    """View a specific email."""
    email = Email.query.get_or_404(email_id)
    
    # Get tasks created from this email
    tasks = Task.query.filter_by(email_id=email.id).all()
    
    return render_template('emails/view.html', email=email, tasks=tasks)

@emails_bp.route('/fetch')
@login_required
def fetch():
    """Fetch new emails."""
    try:
        # Create Gmail service
        gmail_service = create_gmail_service(current_app)
        
        # Fetch new emails
        emails = gmail_service.fetch_unprocessed_emails()
        
        if emails:
            flash(f'Successfully fetched {len(emails)} new emails', 'success')
        else:
            flash('No new emails found', 'info')
            
    except Exception as e:
        flash(f'Error fetching emails: {str(e)}', 'error')
    
    return redirect(url_for('emails.index'))

@emails_bp.route('/<int:email_id>/process')
@login_required
def process(email_id):
    """Process an email to extract tasks."""
    email = Email.query.get_or_404(email_id)
    
    if email.is_processed:
        flash('Email has already been processed', 'info')
        return redirect(url_for('emails.view', email_id=email.id))
    
    try:
        # Create email parser
        parser = create_email_parser(current_app)
        
        # Parse email and extract tasks
        tasks = parser.parse_email(email)
        
        # Mark email as processed
        email.is_processed = True
        email.processed_at = datetime.utcnow()
        db.session.commit()
        
        if tasks:
            flash(f'Successfully extracted {len(tasks)} tasks from email', 'success')
        else:
            flash('No tasks extracted from email', 'info')
            
    except Exception as e:
        flash(f'Error processing email: {str(e)}', 'error')
    
    return redirect(url_for('emails.view', email_id=email.id))

@emails_bp.route('/<int:email_id>/delete', methods=['POST'])
@login_required
def delete(email_id):
    """Delete an email."""
    email = Email.query.get_or_404(email_id)
    
    # Check if email has associated tasks
    if Task.query.filter_by(email_id=email.id).count() > 0:
        flash('Cannot delete email with associated tasks', 'error')
        return redirect(url_for('emails.view', email_id=email.id))
    
    db.session.delete(email)
    db.session.commit()
    
    flash('Email deleted successfully', 'success')
    return redirect(url_for('emails.index'))
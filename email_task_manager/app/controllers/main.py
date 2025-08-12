"""
Main controller for the application dashboard and home page.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Task, Email, PrinterConfig
from app.services.email import check_emails

# Create blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Handle home page."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('main/index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Handle dashboard page."""
    # Get task statistics
    total_tasks = Task.query.count()
    new_tasks = Task.query.filter_by(status='New').count()
    in_progress_tasks = Task.query.filter_by(status='In Progress').count()
    completed_tasks = Task.query.filter_by(status='Completed').count()
    
    # Get email statistics
    total_emails = Email.query.count()
    unprocessed_emails = Email.query.filter_by(is_processed=False).count()
    
    # Get recent tasks
    recent_tasks = Task.query.order_by(Task.created_at.desc()).limit(5).all()
    
    # Get printer status
    printer_config = PrinterConfig.get_default()
    printer_status = "Configured" if printer_config else "Not Configured"
    
    return render_template(
        'main/dashboard.html',
        total_tasks=total_tasks,
        new_tasks=new_tasks,
        in_progress_tasks=in_progress_tasks,
        completed_tasks=completed_tasks,
        total_emails=total_emails,
        unprocessed_emails=unprocessed_emails,
        recent_tasks=recent_tasks,
        printer_status=printer_status
    )

@main_bp.route('/check-emails')
@login_required
def check_emails_route():
    """Manually check for new emails."""
    try:
        # Check for new emails
        count = check_emails(current_app)
        
        if count > 0:
            flash(f'Successfully fetched {count} new emails', 'success')
        else:
            flash('No new emails found', 'info')
            
    except Exception as e:
        flash(f'Error checking emails: {str(e)}', 'error')
    
    return redirect(url_for('main.dashboard'))

@main_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Handle application settings."""
    if request.method == 'POST':
        # Update settings
        if 'email_check_interval' in request.form:
            try:
                interval = int(request.form.get('email_check_interval'))
                if interval < 30:
                    flash('Email check interval must be at least 30 seconds', 'error')
                else:
                    current_app.config['EMAIL_CHECK_INTERVAL'] = interval
                    flash('Email check interval updated', 'success')
            except ValueError:
                flash('Invalid email check interval', 'error')
        
        # Other settings can be added here
    
    return render_template(
        'main/settings.html',
        email_check_interval=current_app.config.get('EMAIL_CHECK_INTERVAL', 300)
    )
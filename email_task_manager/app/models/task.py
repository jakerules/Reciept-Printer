"""
Task model for storing tasks extracted from emails.
"""
from datetime import datetime
from app import db

class Task(db.Model):
    """Task model for storing tasks extracted from emails."""
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    priority = db.Column(db.String(20), default='Medium')  # Low, Medium, High, Urgent
    status = db.Column(db.String(20), default='New')  # New, In Progress, Completed, Cancelled
    due_date = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    email_id = db.Column(db.Integer, db.ForeignKey('emails.id'))
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    # Additional extracted information
    requestor_name = db.Column(db.String(100), nullable=True)
    requestor_email = db.Column(db.String(120), nullable=True)
    requestor_phone = db.Column(db.String(20), nullable=True)
    location = db.Column(db.String(255), nullable=True)
    tags = db.Column(db.String(255), nullable=True)  # Comma-separated tags
    
    # Printing information
    is_printed = db.Column(db.Boolean, default=False)
    last_printed_at = db.Column(db.DateTime, nullable=True)
    print_count = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        """String representation of the task."""
        return f'<Task {self.title}>'
    
    @property
    def is_overdue(self):
        """Check if the task is overdue."""
        if self.due_date and self.status != 'Completed' and self.status != 'Cancelled':
            return self.due_date < datetime.utcnow()
        return False
    
    @property
    def tag_list(self):
        """Return the list of tags."""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []
    
    def mark_as_printed(self):
        """Mark the task as printed."""
        self.is_printed = True
        self.last_printed_at = datetime.utcnow()
        self.print_count += 1
        db.session.commit()
    
    def mark_as_completed(self):
        """Mark the task as completed."""
        self.status = 'Completed'
        self.completed_at = datetime.utcnow()
        db.session.commit()
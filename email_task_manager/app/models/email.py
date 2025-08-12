"""
Email model for storing parsed email information.
"""
from datetime import datetime
from app import db

class Email(db.Model):
    """Email model for storing parsed email information."""
    __tablename__ = 'emails'
    
    id = db.Column(db.Integer, primary_key=True)
    gmail_id = db.Column(db.String(64), unique=True, index=True)
    sender = db.Column(db.String(120))
    sender_email = db.Column(db.String(120))
    subject = db.Column(db.String(255))
    body_text = db.Column(db.Text)
    body_html = db.Column(db.Text)
    received_at = db.Column(db.DateTime)
    processed_at = db.Column(db.DateTime)
    is_processed = db.Column(db.Boolean, default=False)
    processing_error = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    tasks = db.relationship('Task', backref='source_email', lazy='dynamic')
    
    def __repr__(self):
        """String representation of the email."""
        return f'<Email {self.subject}>'
    
    @property
    def short_body(self):
        """Return a shortened version of the email body."""
        if self.body_text:
            return self.body_text[:100] + '...' if len(self.body_text) > 100 else self.body_text
        return ''
    
    @property
    def task_count(self):
        """Return the number of tasks created from this email."""
        return self.tasks.count()
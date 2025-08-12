"""
Printer configuration model for storing printer settings.
"""
from datetime import datetime
from app import db

class PrinterConfig(db.Model):
    """Printer configuration model for storing printer settings."""
    __tablename__ = 'printer_configs'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(255), nullable=True)
    
    # Printer connection details
    printer_type = db.Column(db.String(50))  # 'cups', 'windows', 'network', 'usb'
    printer_name = db.Column(db.String(100))  # System printer name or identifier
    printer_address = db.Column(db.String(255), nullable=True)  # IP address or USB port
    printer_port = db.Column(db.Integer, nullable=True)  # Port number for network printers
    
    # Receipt formatting
    paper_width = db.Column(db.Integer, default=80)  # Characters per line
    header_text = db.Column(db.Text, nullable=True)
    footer_text = db.Column(db.Text, nullable=True)
    font_size = db.Column(db.String(20), default='normal')  # small, normal, large
    include_logo = db.Column(db.Boolean, default=False)
    logo_path = db.Column(db.String(255), nullable=True)
    
    # Behavior settings
    auto_print = db.Column(db.Boolean, default=False)  # Auto-print new tasks
    print_on_status_change = db.Column(db.Boolean, default=False)
    cut_paper = db.Column(db.Boolean, default=True)
    copies = db.Column(db.Integer, default=1)
    
    is_default = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        """String representation of the printer configuration."""
        return f'<PrinterConfig {self.name}>'
    
    @classmethod
    def get_default(cls):
        """Get the default printer configuration."""
        return cls.query.filter_by(is_default=True, is_active=True).first()
    
    def set_as_default(self):
        """Set this printer configuration as the default."""
        # Reset all other configs
        PrinterConfig.query.filter_by(is_default=True).update({'is_default': False})
        # Set this one as default
        self.is_default = True
        db.session.commit()
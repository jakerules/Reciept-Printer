"""
Printer controller for managing printer configurations and printing tasks.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
import platform
from app import db
from app.models import PrinterConfig, Task
from app.services.printer import print_tasks

# Create blueprint
printer_bp = Blueprint('printer', __name__, url_prefix='/printer')

@printer_bp.route('/')
@login_required
def index():
    """Display printer configurations."""
    # Get all printer configurations
    printer_configs = PrinterConfig.query.all()
    
    # Get system information
    system = platform.system()  # 'Windows', 'Darwin' (Mac), or 'Linux'
    
    return render_template(
        'printer/index.html',
        printer_configs=printer_configs,
        system=system
    )

@printer_bp.route('/config/create', methods=['GET', 'POST'])
@login_required
def create_config():
    """Create a new printer configuration."""
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        printer_type = request.form.get('printer_type')
        printer_name = request.form.get('printer_name')
        printer_address = request.form.get('printer_address')
        printer_port = request.form.get('printer_port')
        paper_width = request.form.get('paper_width')
        header_text = request.form.get('header_text')
        footer_text = request.form.get('footer_text')
        font_size = request.form.get('font_size')
        include_logo = request.form.get('include_logo') == 'on'
        logo_path = request.form.get('logo_path')
        auto_print = request.form.get('auto_print') == 'on'
        print_on_status_change = request.form.get('print_on_status_change') == 'on'
        cut_paper = request.form.get('cut_paper') == 'on'
        copies = request.form.get('copies')
        is_default = request.form.get('is_default') == 'on'
        
        # Validate input
        if not name or not printer_type or not printer_name:
            flash('Name, printer type, and printer name are required', 'error')
            return render_template('printer/create_config.html')
        
        # Create new printer configuration
        config = PrinterConfig(
            name=name,
            description=description,
            printer_type=printer_type,
            printer_name=printer_name,
            printer_address=printer_address,
            paper_width=int(paper_width) if paper_width else 80,
            header_text=header_text,
            footer_text=footer_text,
            font_size=font_size,
            include_logo=include_logo,
            logo_path=logo_path,
            auto_print=auto_print,
            print_on_status_change=print_on_status_change,
            cut_paper=cut_paper,
            copies=int(copies) if copies else 1,
            is_active=True
        )
        
        # Set port if provided
        if printer_port:
            try:
                config.printer_port = int(printer_port)
            except ValueError:
                flash('Printer port must be a number', 'error')
                return render_template('printer/create_config.html')
        
        db.session.add(config)
        
        # If this is set as default, update other configs
        if is_default:
            PrinterConfig.query.filter_by(is_default=True).update({'is_default': False})
            config.is_default = True
        
        db.session.commit()
        
        flash('Printer configuration created successfully', 'success')
        return redirect(url_for('printer.index'))
    
    return render_template('printer/create_config.html')

@printer_bp.route('/config/<int:config_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_config(config_id):
    """Edit a printer configuration."""
    config = PrinterConfig.query.get_or_404(config_id)
    
    if request.method == 'POST':
        config.name = request.form.get('name')
        config.description = request.form.get('description')
        config.printer_type = request.form.get('printer_type')
        config.printer_name = request.form.get('printer_name')
        config.printer_address = request.form.get('printer_address')
        config.paper_width = int(request.form.get('paper_width') or 80)
        config.header_text = request.form.get('header_text')
        config.footer_text = request.form.get('footer_text')
        config.font_size = request.form.get('font_size')
        config.include_logo = request.form.get('include_logo') == 'on'
        config.logo_path = request.form.get('logo_path')
        config.auto_print = request.form.get('auto_print') == 'on'
        config.print_on_status_change = request.form.get('print_on_status_change') == 'on'
        config.cut_paper = request.form.get('cut_paper') == 'on'
        config.copies = int(request.form.get('copies') or 1)
        config.is_active = request.form.get('is_active') == 'on'
        
        # Set port if provided
        printer_port = request.form.get('printer_port')
        if printer_port:
            try:
                config.printer_port = int(printer_port)
            except ValueError:
                flash('Printer port must be a number', 'error')
                return render_template('printer/edit_config.html', config=config)
        else:
            config.printer_port = None
        
        # If this is set as default, update other configs
        is_default = request.form.get('is_default') == 'on'
        if is_default and not config.is_default:
            PrinterConfig.query.filter_by(is_default=True).update({'is_default': False})
            config.is_default = True
        
        db.session.commit()
        
        flash('Printer configuration updated successfully', 'success')
        return redirect(url_for('printer.index'))
    
    return render_template('printer/edit_config.html', config=config)

@printer_bp.route('/config/<int:config_id>/delete', methods=['POST'])
@login_required
def delete_config(config_id):
    """Delete a printer configuration."""
    config = PrinterConfig.query.get_or_404(config_id)
    
    # Check if this is the default config
    if config.is_default:
        flash('Cannot delete the default printer configuration', 'error')
        return redirect(url_for('printer.index'))
    
    db.session.delete(config)
    db.session.commit()
    
    flash('Printer configuration deleted successfully', 'success')
    return redirect(url_for('printer.index'))

@printer_bp.route('/config/<int:config_id>/set-default', methods=['POST'])
@login_required
def set_default_config(config_id):
    """Set a printer configuration as default."""
    config = PrinterConfig.query.get_or_404(config_id)
    
    # Update all configs
    PrinterConfig.query.filter_by(is_default=True).update({'is_default': False})
    
    # Set this one as default
    config.is_default = True
    db.session.commit()
    
    flash('Default printer configuration updated', 'success')
    return redirect(url_for('printer.index'))

@printer_bp.route('/print-batch', methods=['GET', 'POST'])
@login_required
def print_batch():
    """Print a batch of tasks."""
    if request.method == 'POST':
        task_ids = request.form.getlist('task_ids')
        printer_config_id = request.form.get('printer_config_id')
        
        if not task_ids:
            flash('No tasks selected', 'error')
            return redirect(url_for('tasks.index'))
        
        # Get tasks
        tasks = Task.query.filter(Task.id.in_(task_ids)).all()
        
        # Get printer configuration
        printer_config = None
        if printer_config_id:
            printer_config = PrinterConfig.query.get(printer_config_id)
        
        try:
            # Print tasks
            count = print_tasks(tasks, printer_config)
            
            if count > 0:
                flash(f'Successfully printed {count} tasks', 'success')
            else:
                flash('Failed to print tasks', 'error')
                
        except Exception as e:
            flash(f'Error printing tasks: {str(e)}', 'error')
        
        return redirect(url_for('tasks.index'))
    
    # Get tasks to print
    task_ids = request.args.getlist('task_ids')
    tasks = []
    
    if task_ids:
        tasks = Task.query.filter(Task.id.in_(task_ids)).all()
    
    # Get printer configurations
    printer_configs = PrinterConfig.query.filter_by(is_active=True).all()
    
    return render_template(
        'printer/print_batch.html',
        tasks=tasks,
        printer_configs=printer_configs
    )

@printer_bp.route('/test-print/<int:config_id>')
@login_required
def test_print(config_id):
    """Test a printer configuration."""
    config = PrinterConfig.query.get_or_404(config_id)
    
    try:
        from app.services.printer.printer_service import PrinterService
        
        # Create printer service
        service = PrinterService(config)
        
        # Create test content
        content = f"""
{'=' * config.paper_width}
{'TEST PRINT'.center(config.paper_width)}
{'=' * config.paper_width}

Printer: {config.name}
Type: {config.printer_type}
System: {platform.system()}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{'=' * config.paper_width}
{'If you can read this, printing works!'.center(config.paper_width)}
{'=' * config.paper_width}

"""
        
        # Print test content
        if service._print_windows(content) if platform.system() == 'Windows' else service._print_unix(content):
            flash('Test print sent successfully', 'success')
        else:
            flash('Failed to send test print', 'error')
            
    except Exception as e:
        flash(f'Error testing printer: {str(e)}', 'error')
    
    return redirect(url_for('printer.index'))
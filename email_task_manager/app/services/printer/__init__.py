"""
Printer services package initialization.
"""
from app.services.printer.printer_service import PrinterService
from app.models import PrinterConfig, Task

def get_printer_service(printer_config=None):
    """
    Get a printer service instance.
    
    Args:
        printer_config: PrinterConfig object or None to use default
        
    Returns:
        PrinterService instance
    """
    if not printer_config:
        printer_config = PrinterConfig.get_default()
        
    if not printer_config:
        raise ValueError("No printer configuration available")
        
    return PrinterService(printer_config)

def print_task(task, printer_config=None):
    """
    Print a task.
    
    Args:
        task: Task object to print
        printer_config: PrinterConfig object or None to use default
        
    Returns:
        Boolean indicating success
    """
    service = get_printer_service(printer_config)
    return service.print_task(task)

def print_tasks(tasks, printer_config=None):
    """
    Print multiple tasks.
    
    Args:
        tasks: List of Task objects to print
        printer_config: PrinterConfig object or None to use default
        
    Returns:
        Number of successfully printed tasks
    """
    service = get_printer_service(printer_config)
    return service.print_tasks(tasks)

def print_new_tasks(app):
    """
    Print all new unprinted tasks.
    
    Args:
        app: Flask application instance
        
    Returns:
        Number of tasks printed
    """
    with app.app_context():
        # Get default printer configuration
        printer_config = PrinterConfig.get_default()
        
        if not printer_config or not printer_config.auto_print:
            return 0
        
        # Get unprinted tasks
        unprinted_tasks = Task.query.filter_by(is_printed=False).all()
        
        if not unprinted_tasks:
            return 0
        
        # Print tasks
        service = get_printer_service(printer_config)
        return service.print_tasks(unprinted_tasks)
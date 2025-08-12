"""
Printer service for printing tasks to receipt printers.
"""
import os
import platform
import tempfile
from datetime import datetime
from app.models import PrinterConfig

class PrinterService:
    """Service for printing tasks to receipt printers."""
    
    def __init__(self, printer_config=None):
        """
        Initialize the printer service.
        
        Args:
            printer_config: PrinterConfig object or None to use default
        """
        self.printer_config = printer_config or PrinterConfig.get_default()
        self.system = platform.system()  # 'Windows', 'Darwin' (Mac), or 'Linux'
    
    def print_task(self, task):
        """
        Print a task to the receipt printer.
        
        Args:
            task: Task object to print
            
        Returns:
            Boolean indicating success
        """
        if not self.printer_config:
            raise ValueError("No printer configuration available")
        
        # Format the task for printing
        content = self._format_task(task)
        
        # Print based on the operating system
        success = False
        if self.system == 'Windows':
            success = self._print_windows(content)
        elif self.system in ['Darwin', 'Linux']:
            success = self._print_unix(content)
        else:
            raise NotImplementedError(f"Printing not implemented for {self.system}")
        
        # Update task print status if successful
        if success:
            task.mark_as_printed()
        
        return success
    
    def print_tasks(self, tasks):
        """
        Print multiple tasks to the receipt printer.
        
        Args:
            tasks: List of Task objects to print
            
        Returns:
            Number of successfully printed tasks
        """
        if not tasks:
            return 0
        
        success_count = 0
        for task in tasks:
            if self.print_task(task):
                success_count += 1
        
        return success_count
    
    def _format_task(self, task):
        """
        Format a task for printing.
        
        Args:
            task: Task object to format
            
        Returns:
            Formatted string ready for printing
        """
        width = self.printer_config.paper_width or 40
        
        # Create header
        header = self.printer_config.header_text or "Task Receipt"
        header = f"\n{header.center(width)}\n"
        header += f"{'-' * width}\n"
        
        # Format task details
        task_id = f"Task ID: {task.id}"
        created_date = f"Created: {task.created_at.strftime('%Y-%m-%d %H:%M')}"
        
        title = f"TITLE: {task.title}"
        if len(title) > width:
            # Wrap title if it's too long
            title = title[:width-3] + "..."
        
        # Format description with word wrapping
        description_lines = []
        if task.description:
            desc = "DESCRIPTION:"
            description_lines.append(desc)
            
            words = task.description.split()
            current_line = ""
            
            for word in words:
                if len(current_line) + len(word) + 1 <= width:
                    if current_line:
                        current_line += " " + word
                    else:
                        current_line = word
                else:
                    description_lines.append(current_line)
                    current_line = word
            
            if current_line:
                description_lines.append(current_line)
        
        # Format priority and status
        priority = f"Priority: {task.priority}"
        status = f"Status: {task.status}"
        
        # Format due date
        due_date = "Due: N/A"
        if task.due_date:
            due_date = f"Due: {task.due_date.strftime('%Y-%m-%d %H:%M')}"
        
        # Format requestor information
        requestor = f"From: {task.requestor_name}" if task.requestor_name else ""
        requestor_email = f"Email: {task.requestor_email}" if task.requestor_email else ""
        
        # Format location
        location = f"Location: {task.location}" if task.location else ""
        
        # Combine all parts
        content = [
            header,
            task_id,
            created_date,
            "",
            title,
            ""
        ]
        
        content.extend(description_lines)
        content.append("")
        
        content.extend([
            priority,
            status,
            due_date,
            ""
        ])
        
        if requestor:
            content.append(requestor)
        if requestor_email:
            content.append(requestor_email)
        if location:
            content.append(location)
        
        # Add footer
        content.append(f"{'-' * width}")
        footer = self.printer_config.footer_text or f"Printed: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        content.append(footer.center(width))
        content.append("\n\n\n")  # Add space for cutting
        
        return "\n".join(content)
    
    def _print_windows(self, content):
        """
        Print content on Windows.
        
        Args:
            content: Formatted string to print
            
        Returns:
            Boolean indicating success
        """
        try:
            import win32print
            import win32ui
            
            # Create a temporary file with the content
            with tempfile.NamedTemporaryFile(delete=False, suffix='.txt', mode='w') as temp:
                temp.write(content)
                temp_path = temp.name
            
            # Get the printer name
            printer_name = self.printer_config.printer_name
            if not printer_name:
                printer_name = win32print.GetDefaultPrinter()
            
            # Open the printer
            hPrinter = win32print.OpenPrinter(printer_name)
            try:
                # Start a print job
                job = win32print.StartDocPrinter(hPrinter, 1, ("Task Receipt", temp_path, "RAW"))
                try:
                    win32print.StartPagePrinter(hPrinter)
                    
                    # Read and send the file content
                    with open(temp_path, 'rb') as file:
                        data = file.read()
                        win32print.WritePrinter(hPrinter, data)
                    
                    win32print.EndPagePrinter(hPrinter)
                finally:
                    win32print.EndDocPrinter(hPrinter)
            finally:
                win32print.ClosePrinter(hPrinter)
            
            # Clean up the temporary file
            os.unlink(temp_path)
            
            return True
            
        except Exception as e:
            print(f"Error printing on Windows: {str(e)}")
            return False
    
    def _print_unix(self, content):
        """
        Print content on Unix-based systems (Mac/Linux).
        
        Args:
            content: Formatted string to print
            
        Returns:
            Boolean indicating success
        """
        try:
            # Determine if we should use CUPS or direct ESC/POS
            if self.printer_config.printer_type == 'cups':
                return self._print_cups(content)
            else:
                return self._print_escpos(content)
        except Exception as e:
            print(f"Error printing on Unix: {str(e)}")
            return False
    
    def _print_cups(self, content):
        """
        Print using CUPS.
        
        Args:
            content: Formatted string to print
            
        Returns:
            Boolean indicating success
        """
        try:
            import cups
            
            # Create a temporary file with the content
            with tempfile.NamedTemporaryFile(delete=False, suffix='.txt', mode='w') as temp:
                temp.write(content)
                temp_path = temp.name
            
            # Connect to CUPS
            conn = cups.Connection()
            
            # Get the printer name
            printer_name = self.printer_config.printer_name
            if not printer_name:
                printers = conn.getPrinters()
                if printers:
                    printer_name = list(printers.keys())[0]
                else:
                    raise ValueError("No printers available")
            
            # Print the file
            job_id = conn.printFile(
                printer_name,
                temp_path,
                "Task Receipt",
                {}
            )
            
            # Clean up the temporary file
            os.unlink(temp_path)
            
            return job_id > 0
            
        except Exception as e:
            print(f"Error printing with CUPS: {str(e)}")
            return False
    
    def _print_escpos(self, content):
        """
        Print using ESC/POS commands.
        
        Args:
            content: Formatted string to print
            
        Returns:
            Boolean indicating success
        """
        try:
            from escpos.printer import Usb, Network, File
            
            # Determine printer connection type
            printer = None
            if self.printer_config.printer_type == 'usb':
                # For USB printers, we need vendor_id and product_id
                # These would typically be stored in the printer_address field as "vendor_id:product_id"
                if self.printer_config.printer_address:
                    vendor_id, product_id = self.printer_config.printer_address.split(':')
                    printer = Usb(int(vendor_id, 16), int(product_id, 16))
                else:
                    raise ValueError("USB printer requires vendor_id and product_id")
            
            elif self.printer_config.printer_type == 'network':
                # For network printers, we need IP address and port
                printer = Network(
                    self.printer_config.printer_address,
                    self.printer_config.printer_port or 9100
                )
            
            elif self.printer_config.printer_type == 'file':
                # For file-based printers (e.g., /dev/usb/lp0)
                printer = File(self.printer_config.printer_address)
            
            else:
                raise ValueError(f"Unsupported printer type: {self.printer_config.printer_type}")
            
            # Print the content
            printer.text(content)
            
            # Cut the paper if configured
            if self.printer_config.cut_paper:
                printer.cut()
            
            printer.close()
            return True
            
        except Exception as e:
            print(f"Error printing with ESC/POS: {str(e)}")
            return False
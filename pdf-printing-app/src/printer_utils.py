from fpdf import FPDF
import requests
import os
import win32print
import win32api
import tempfile
import time

def send_pdf_to_printer(pdf_path, printer_destination):
    """
    Send a PDF to either a network printer or local Windows printer
    
    Args:
        pdf_path: Path to the PDF file
        printer_destination: Either an IP address or Windows printer name
    """
    try:
        if '.' in printer_destination:  # Assumes IP address
            return send_to_network_printer(pdf_path, printer_destination)
        else:
            return send_to_windows_printer(pdf_path, printer_destination)
    except Exception as e:
        print(f"Error sending to printer: {e}")
        return None

def send_to_network_printer(pdf_path, printer_ip):
    """Send PDF to a network printer"""
    try:
        with open(pdf_path, 'rb') as pdf_file:
            response = requests.post(f'http://{printer_ip}/print', files={'file': pdf_file})
            response.raise_for_status()
            return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error sending PDF to network printer: {e}")
        return None

def send_to_usb_printer(pdf_path, printer_device):
    """Send PDF to a USB printer"""
    try:
        if not os.path.exists(printer_device):
            raise FileNotFoundError(f"Printer device {printer_device} not found")
            
        # For receipt printer, we might need to add special formatting or commands here
        with open(pdf_path, 'rb') as pdf_file:
            data = pdf_file.read()
            
        with open(printer_device, 'wb') as printer:
            printer.write(data)
            # Add form feed character to eject the page
            printer.write(b'\f')
            
        return {"status": "success", "device": printer_device}
    except Exception as e:
        print(f"Error sending to USB printer: {e}")
        return None

def send_receipt_to_printer(text, printer_device):
    """
    Send text receipt to USB printer with proper formatting
    """
    try:
        if not os.path.exists(printer_device):
            raise FileNotFoundError(f"Printer device {printer_device} not found")

        # Add receipt printer initialization sequence if needed
        init_sequence = b'\x1b\x40'  # ESC @ - Initialize printer
        
        # Format the text for the receipt printer
        formatted_text = (
            text.encode('ascii', 'replace')  # Convert to ASCII
            + b'\n\n\n'  # Add some line feeds for spacing
            + b'\x1d\x56\x41\x03'  # Paper cut command (may need adjustment for your printer)
        )
        
        with open(printer_device, 'wb') as printer:
            printer.write(init_sequence)
            printer.write(formatted_text)
            
        return {"status": "success", "device": printer_device}
    except Exception as e:
        print(f"Error sending receipt to USB printer: {e}")
        return None

def check_printer_status(printer_destination):
    """Check printer status for either network or USB printer"""
    try:
        if printer_destination.startswith('/dev/'):
            return check_usb_printer_status(printer_destination)
        else:
            return check_network_printer_status(printer_destination)
    except Exception as e:
        print(f"Error checking printer status: {e}")
        return None

def check_network_printer_status(printer_ip):
    """Check network printer status"""
    try:
        response = requests.get(f'http://{printer_ip}/status')
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error checking network printer status: {e}")
        return None

def check_usb_printer_status(printer_device):
    """Check USB printer status"""
    try:
        if os.path.exists(printer_device):
            # Basic check if device exists and is writable
            if os.access(printer_device, os.W_OK):
                return {"status": "ready", "device": printer_device}
            else:
                return {"status": "not writable", "device": printer_device}
        else:
            return {"status": "not found", "device": printer_device}
    except Exception as e:
        print(f"Error checking USB printer status: {e}")
        return None
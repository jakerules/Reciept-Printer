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

def send_to_windows_printer(pdf_path, printer_name):
    """Send PDF to a Windows printer"""
    try:
        if printer_name not in [printer[2] for printer in win32print.EnumPrinters(2)]:
            raise ValueError(f"Printer '{printer_name}' not found")
            
        win32api.ShellExecute(0, "print", pdf_path, f'"{printer_name}"', ".", 0)
        return {"status": "success", "printer": printer_name}
    except Exception as e:
        print(f"Error sending to Windows printer: {e}")
        return None

def send_receipt_to_printer(text, printer_name):
    """
    Send text receipt to Windows printer with proper formatting
    """
    try:
        # Create a temporary file for the formatted receipt
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt', mode='w', encoding='utf-8') as temp:
            # Add receipt formatting
            formatted_text = (
                "\x1B@"  # Initialize printer
                + text
                + "\n\n\n"  # Add some line feeds for spacing
                + "\x1D\x56\x41\x03"  # Paper cut command
            )
            temp.write(formatted_text)
            temp_path = temp.name

        # Get the default printer handle
        printer_handle = win32print.OpenPrinter(printer_name)
        try:
            # Start a print job
            job = win32print.StartDocPrinter(printer_handle, 1, ("Receipt", None, "RAW"))
            try:
                win32print.StartPagePrinter(printer_handle)
                with open(temp_path, 'rb') as f:
                    data = f.read()
                    win32print.WritePrinter(printer_handle, data)
                win32print.EndPagePrinter(printer_handle)
            finally:
                win32print.EndDocPrinter(printer_handle)
        finally:
            win32print.ClosePrinter(printer_handle)
            
        # Clean up temporary file
        os.unlink(temp_path)
        return {"status": "success", "printer": printer_name}
    except Exception as e:
        print(f"Error sending receipt to printer: {e}")
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
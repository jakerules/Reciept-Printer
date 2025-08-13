from fpdf import FPDF
import requests

def send_pdf_to_printer(pdf_path, printer_ip):
    try:
        with open(pdf_path, 'rb') as pdf_file:
            response = requests.post(f'http://{printer_ip}/print', files={'file': pdf_file})
            response.raise_for_status()
            return response.json()  # Assuming the printer returns a JSON response
    except requests.exceptions.RequestException as e:
        print(f"Error sending PDF to printer: {e}")
        return None

def check_printer_status(printer_ip):
    try:
        response = requests.get(f'http://{printer_ip}/status')
        response.raise_for_status()
        return response.json()  # Assuming the printer returns a JSON response
    except requests.exceptions.RequestException as e:
        print(f"Error checking printer status: {e}")
        return None
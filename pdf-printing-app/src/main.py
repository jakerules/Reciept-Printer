from flask import Flask, request, jsonify
import os
from pdf_utils import download_pdf, add_footer_text, save_modified_pdf
from printer_utils import send_pdf_to_printer, send_receipt_to_printer
from receipt_utils import generate_receipt
from config import printer_ip, pdf_download_path, modified_pdf_path
# Define usb_receipt_printer here if needed, for example:
usb_receipt_printer = "/dev/usb/lp0"  # Update this path as appropriate for your environment

app = Flask(__name__)

@app.route('/print-job', methods=['POST'])
def handle_print_job():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data received"}), 400

        # Convert array format to dictionary
        data_dict = {}
        for item in data:
            for key, value in item.items():
                data_dict[key] = value

        # Required fields
        pdf_url = data_dict.get('URL')
        job_data = {
            'JobID': data_dict.get('JobID'),
            'quantity': data_dict.get('quantity'),
            'size': data_dict.get('size'),
            'date': data_dict.get('date'),
            'staple': data_dict.get('staple'),
            '2side': data_dict.get('2side'),
            'hole': data_dict.get('hole'),
            'who': data_dict.get('who'),
            'where': data_dict.get('where')
        }
        
        # Use JobID as footer text
        footer_text = f"Job ID: {job_data['JobID']}"

        if not all([pdf_url, job_data['JobID']]):
            return jsonify({"error": "Missing required fields (URL or JobID)"}), 400

        # Step 1: Download and process PDF
        try:
            pdf_stream = download_pdf(pdf_url)
        except Exception as e:
            return jsonify({
                "error": f"Failed to download or validate PDF: {str(e)}",
                "url": pdf_url
            }), 500
        
        # Step 2: Add footer text
        try:
            modified_pdf_stream = add_footer_text(pdf_stream, footer_text)
        except Exception as e:
            return jsonify({
                "error": f"Failed to add footer to PDF: {str(e)}"
            }), 500
        
        # Step 3: Save modified PDF
        try:
            save_modified_pdf(modified_pdf_stream, modified_pdf_path)
        except Exception as e:
            return jsonify({
                "error": f"Failed to save modified PDF: {str(e)}"
            }), 500
        
        # Step 4: Send to IP printer
        print_result = send_pdf_to_printer(modified_pdf_path, printer_ip)
        if not print_result:
            return jsonify({"error": "Failed to send PDF to printer"}), 500
            
        # Step 5: Generate and print receipt
        receipt_text = generate_receipt(job_data)
        receipt_result = send_receipt_to_printer(receipt_text, usb_receipt_printer)
        if not receipt_result:
            return jsonify({"warning": "PDF printed but receipt failed to print"}), 206

        # Clean up temporary files
        if os.path.exists(modified_pdf_path):
            os.remove(modified_pdf_path)

        return jsonify({
            "status": "success",
            "message": "PDF printed and receipt generated successfully",
            "print_job_id": print_result.get('job_id')
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5112)
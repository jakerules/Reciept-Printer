printer_ip = "192.168.1.100"
receipt_printer_name = "RECEIPT-PRINTER"  # Windows printer name from Control Panel
temp_dir = "C:\\Windows\\Temp"  # Windows temporary directory
pdf_download_path = temp_dir + "\\downloaded_pdf.pdf"
modified_pdf_path = temp_dir + "\\modified_pdf.pdf"
receipt_template = "Job ID: {}\nQuantity: {}\nPaper Size: {}\nDate Wanted: {}\nPages: {}\nStaple: {}\nDouble Sided: {}\nHole Punch: {}"
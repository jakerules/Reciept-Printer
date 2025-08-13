# PDF Printing Application

This project is designed to handle PDF printing tasks via a webhook. It retrieves a PDF from a provided URL, modifies it by adding footer text, and sends it to an IP printer. Additionally, it generates a job receipt formatted for a POS receipt printer.

## Project Structure

```
pdf-printing-app
├── src
│   ├── main.py          # Entry point of the application
│   ├── pdf_utils.py     # Utility functions for PDF operations
│   ├── printer_utils.py  # Functions for sending PDFs to the IP printer
│   ├── receipt_utils.py  # Functions for generating job receipts
│   └── config.py        # Configuration settings
├── requirements.txt      # Project dependencies
└── README.md            # Project documentation
```

## Prerequisites

- Windows 10/11
- Python 3.7 or higher
- Network-enabled IP printer for main document printing
- Receipt printer installed in Windows
- Network connectivity to access PDF URLs
- Administrator access for printer configuration

## Setup Instructions

1. Clone the repository:
   ```cmd
   git clone <repository-url>
   cd pdf-printing-app
   ```

2. Install the required dependencies:
   ```cmd
   pip install -r requirements.txt
   ```

3. Configure Windows Printer:
   - Open Windows Settings
   - Go to Devices > Printers & scanners
   - Add your receipt printer if not already installed
   - Note down the exact printer name as shown in Windows

4. Configure the printer settings in `src/config.py`:
   ```python
   printer_ip = "192.168.1.100"  # Your IP printer address for documents
   receipt_printer_name = "RECEIPT-PRINTER"  # Your Windows printer name
   ```

5. Verify printer configuration:
   ```python
   # In Python console
   import win32print
   printers = [printer[2] for printer in win32print.EnumPrinters(2)]
   print(printers)  # Should list your receipt printer
   ```

## Running the Application

Start the Flask server:
```bash
python src/main.py
```

The server will start on `http://localhost:5000` by default.

## API Documentation

### Print Job Endpoint

**URL:** `/print-job`
**Method:** `POST`
**Content-Type:** `application/json`

#### Request Body

```json
{
    "pdf_url": "https://example.com/document.pdf",
    "footer_text": "Your footer text here",
    "job_data": {
        "job_id": "12345",
        "quantity": "2",
        "paper_size": "A4",
        "date_wanted": "2025-08-15",
        "pages": "5",
        "staple": "Yes",
        "double_sided": "Yes",
        "hole_punch": "No"
    }
}
```

#### Required Fields

- `pdf_url` (string): URL of the PDF to be printed
- `footer_text` (string): Text to be added to the PDF footer
- `job_data` (object): Job information for the receipt
  - `job_id` (string): Unique identifier for the job
  - `quantity` (string): Number of copies
  - `paper_size` (string): Size of paper (e.g., "A4", "Letter")
  - `date_wanted` (string): Required completion date
  - `pages` (string): Number of pages
  - `staple` (string): Whether stapling is required ("Yes"/"No")
  - `double_sided` (string): Whether double-sided printing is required ("Yes"/"No")
  - `hole_punch` (string): Whether hole punching is required ("Yes"/"No")

#### Response

Success (200 OK):
```json
{
    "status": "success",
    "message": "PDF printed and receipt generated successfully",
    "print_job_id": "12345"
}
```

Error (400 Bad Request):
```json
{
    "error": "Missing required fields"
}
```

Error (500 Internal Server Error):
```json
{
    "error": "Failed to send PDF to printer"
}
```

## Features

- **PDF Processing**
  - Downloads PDFs from remote URLs
  - Adds customizable footer text in size 5 font
  - Preserves original PDF content and formatting

- **Printing Capabilities**
  - Sends modified PDFs to network-enabled IP printers
  - Direct USB printing support for receipt printer
  - ESC/POS command support for receipt formatting
  - Automatic paper cutting and formatting for receipts
  - Supports mixed network and USB printer configurations

- **Job Receipt Details**
  - Comprehensive job information
  - Clear, formatted layout
  - Essential print specifications

## Error Handling

The application includes robust error handling for:
- Invalid JSON data
- Missing required fields
- PDF download failures
- Network printer connection issues
- USB printer access permissions
- Device not found errors
- File processing errors

## Troubleshooting

Common issues and solutions:

1. Printer Not Found
   ```python
   # Check if Windows can see your printer
   import win32print
   printers = [printer[2] for printer in win32print.EnumPrinters(2)]
   print(printers)
   ```

2. Permission Issues
   - Run Command Prompt as Administrator
   - Verify printer permissions in Windows Security settings
   - Check printer sharing settings if using network printer

3. Print Quality Issues
   - Open Printer Properties in Windows
   - Verify printer preferences and default settings
   - Update printer drivers if needed
   - Check printer status in Windows queue

4. Common Windows Printer Problems
   - Clear printer queue if jobs are stuck
   - Restart Print Spooler service:
     ```cmd
     net stop spooler
     net start spooler
     ```
   - Check Windows Event Viewer for printer errors

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.
# Receipt-Printer

This application provides a web interface and an email webhook to print text to a receipt printer.

## Features

- **Web UI:** A simple web page at the root URL (`/`) to manually enter and print text.
- **Email Webhook:** An endpoint at `/email-webhook` to receive emails (e.g., from Mailgun) and print their content.
- **Dockerized:** Comes with a `Dockerfile` for easy and consistent deployment.
- **Tested:** Includes a basic test suite to verify functionality.

## How to Run

### Using Docker (Recommended)

1.  **Build the Docker image:**
    ```bash
    docker build -t receipt-printer .
    ```

2.  **Run the Docker container:**
    ```bash
    docker run -p 8000:8000 -d --name receipt-printer-app receipt-printer
    ```
    This runs the container in detached mode. The application will be available at `http://localhost:8000`.

### For Development (Running Locally)

The easiest way to run the application locally for development is to use the provided script.

1.  **Run the script from your terminal:**
    ```bash
    ./run-local.sh
    ```
    If you get a "permission denied" error, you may need to make the script executable first by running: `chmod +x run-local.sh`.

    The script will install all necessary dependencies and then start the web server. You can access it at `http://localhost:8000`.

#### Manual Local Setup

If you prefer to run the commands manually, you can follow these steps:

1.  **Create a virtual environment (optional but recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    ```

3.  **Run the server:**
    ```bash
    uvicorn app.main:app --reload
    ```

## How to Test

1.  **Make sure development dependencies are installed.**
    ```bash
    pip install -r requirements-dev.txt
    ```

2.  **Run the tests from the root directory:**
    ```bash
    pytest
    ```

## Printer Configuration

The printer logic is located in `app/printer.py`. By default, it uses a `Dummy` printer that logs the intended output to the console where the app is running.

To use a real printer, you will need to modify this file to use a different `escpos` printer class (e.g., `escpos.printer.Usb` or `escpos.printer.Network`) and provide the correct connection details for your specific hardware.
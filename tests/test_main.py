from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Add the project root to the Python path to allow for absolute imports
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app

client = TestClient(app)

def test_read_form_loads_successfully():
    """
    Tests that the main page (GET /) loads correctly and contains the expected form.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert 'action="/print"' in response.text
    assert "<textarea" in response.text

@patch('app.main.printer_service')
def test_print_text_from_form(mock_printer_service: MagicMock):
    """
    Tests the manual print endpoint (POST /print).
    The TestClient follows redirects by default, so we check for a final 200 OK
    status after the redirect. The main purpose is to verify that the
    printer service was called correctly during the initial POST.
    """
    test_message = "This is a test message from the web form."
    response = client.post("/print", data={"text_to_print": test_message})

    # The client follows the redirect, so the final status code should be 200
    assert response.status_code == 200
    # And the final page should be the home page
    assert "<h1>Receipt Printer</h1>" in response.text

    # Verify that the printer service was called with the correct text (with a newline)
    mock_printer_service.print_text.assert_called_once_with(test_message + "\n")

@patch('app.main.printer_service')
def test_email_webhook_with_valid_payload(mock_printer_service: MagicMock):
    """
    Tests the email webhook endpoint (POST /email-webhook) with a valid payload.
    It should return a success message and have called the printer service.
    """
    email_payload = {
        "sender": "jane.doe@example.com",
        "subject": "Important Memo",
        "body-plain": "Please remember to submit your reports by 5 PM."
    }
    response = client.post("/email-webhook", json=email_payload)

    assert response.status_code == 200
    assert response.json() == {"message": "Email processed and sent to printer service."}

    # Construct the expected formatted string that the service should receive
    expected_print_text = (
        f"New Email:\n"
        f"From: {email_payload['sender']}\n"
        f"Subject: {email_payload['subject']}\n"
        f"--------------------\n"
        f"{email_payload['body-plain']}"
    )
    # The endpoint adds a final \n itself
    mock_printer_service.print_text.assert_called_once_with(expected_print_text + "\n")

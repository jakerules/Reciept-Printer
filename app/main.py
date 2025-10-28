from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

# Corrected import for intra-package module
from .printer import printer_service

# --- Pydantic Model for Incoming Email ---
class IncomingEmail(BaseModel):
    """
    Defines the structure for incoming email data from a webhook.
    """
    sender: str
    subject: str
    body_plain: str = Field(..., alias='body-plain')


# --- FastAPI App Initialization ---
app = FastAPI()
templates = Jinja2Templates(directory="templates")


# --- Web UI Endpoints ---
@app.get("/", response_class=HTMLResponse)
async def read_form(request: Request):
    """
    Serves the main page with a form to enter text.
    """
    return templates.TemplateResponse("index.html", {"request": request, "message": ""})

@app.post("/print")
async def print_text(request: Request, text_to_print: str = Form(...)):
    """
    Receives text from the web form and sends it to the printer service.
    """
    # Use the printer service to "print" the text.
    # Add a newline for better formatting on a real receipt.
    printer_service.print_text(text_to_print + "\n")

    # It's good practice to redirect after a POST to prevent re-submission.
    response = RedirectResponse(url="/", status_code=303)
    return response


# --- Email Webhook Endpoint ---
@app.post("/email-webhook")
async def email_webhook(email: IncomingEmail):
    """
    Webhook endpoint to receive incoming emails. It parses the email
    and sends the content to the printer service for printing.
    """
    print("--- Received Email via Webhook ---")

    # Format the text for the receipt
    formatted_text = (
        f"New Email:\n"
        f"From: {email.sender}\n"
        f"Subject: {email.subject}\n"
        f"--------------------\n"
        f"{email.body_plain}"
    )

    # Send the formatted text to the printer service
    printer_service.print_text(formatted_text + "\n")

    return {"message": "Email processed and sent to printer service."}

"""
Gmail service for fetching emails using the Gmail API.
"""
import os
import base64
import re
import email
from datetime import datetime
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from email.utils import parsedate_to_datetime
from app import db
from app.models import Email

# Define the scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class GmailService:
    """Service for interacting with Gmail API."""
    
    def __init__(self, credentials_path, token_path):
        """
        Initialize the Gmail service.
        
        Args:
            credentials_path: Path to the credentials.json file
            token_path: Path to the token.json file
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = self._get_gmail_service()
    
    def _get_gmail_service(self):
        """
        Get an authorized Gmail API service instance.
        
        Returns:
            Gmail API service instance
        """
        creds = None
        
        # Check if token.json file exists
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_info(
                json.loads(open(self.token_path).read()), SCOPES)
        
        # If credentials don't exist or are invalid, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        
        # Build the service
        return build('gmail', 'v1', credentials=creds)
    
    def fetch_unprocessed_emails(self, max_results=10):
        """
        Fetch unprocessed emails from Gmail.
        
        Args:
            max_results: Maximum number of emails to fetch
            
        Returns:
            List of fetched emails
        """
        # Get list of emails that haven't been processed yet
        query = "is:unread"
        results = self.service.users().messages().list(
            userId='me', q=query, maxResults=max_results).execute()
        
        messages = results.get('messages', [])
        fetched_emails = []
        
        for message in messages:
            # Check if email already exists in database
            existing_email = Email.query.filter_by(gmail_id=message['id']).first()
            if existing_email:
                continue
                
            # Get the email details
            msg = self.service.users().messages().get(
                userId='me', id=message['id'], format='full').execute()
            
            # Parse email details
            headers = msg['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            date_str = next((h['value'] for h in headers if h['name'] == 'Date'), None)
            
            # Extract sender email
            sender_email = re.search(r'<(.+?)>', sender)
            if sender_email:
                sender_email = sender_email.group(1)
            else:
                sender_email = sender
            
            # Parse date
            received_at = datetime.utcnow()
            if date_str:
                try:
                    received_at = parsedate_to_datetime(date_str)
                except Exception:
                    pass
            
            # Extract body
            body_text = ''
            body_html = ''
            
            if 'parts' in msg['payload']:
                for part in msg['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        body_text = base64.urlsafe_b64decode(
                            part['body']['data']).decode('utf-8')
                    elif part['mimeType'] == 'text/html':
                        body_html = base64.urlsafe_b64decode(
                            part['body']['data']).decode('utf-8')
            elif 'body' in msg['payload'] and 'data' in msg['payload']['body']:
                body_text = base64.urlsafe_b64decode(
                    msg['payload']['body']['data']).decode('utf-8')
            
            # Create new email record
            new_email = Email(
                gmail_id=message['id'],
                sender=sender,
                sender_email=sender_email,
                subject=subject,
                body_text=body_text,
                body_html=body_html,
                received_at=received_at,
                is_processed=False
            )
            
            db.session.add(new_email)
            fetched_emails.append(new_email)
        
        # Commit all new emails to database
        if fetched_emails:
            db.session.commit()
        
        return fetched_emails
    
    def mark_as_read(self, gmail_id):
        """
        Mark an email as read in Gmail.
        
        Args:
            gmail_id: Gmail message ID
        """
        self.service.users().messages().modify(
            userId='me',
            id=gmail_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()
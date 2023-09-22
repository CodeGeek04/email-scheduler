from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import base64
from datetime import datetime
import time
from email.mime.text import MIMEText


def read_threads(service):
    query = 'is:unread'
    results = service.users().threads().list(userId='me', q=query).execute()
    threads = results.get('threads', [])
    return threads


def read_emails(service):
    query = 'is:unread'
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])
    return messages


def get_message_text(message):
    payload = message['payload']
    if 'parts' in payload:
        for part in payload['parts']:
            mimeType = part.get('mimeType')
            body = part.get('body')
            data = body.get('data')
            if part.get('parts'):
                for subpart in part.get('parts'):
                    data = subpart.get('body').get('data')
                    if data:
                        text = base64.urlsafe_b64decode(data).decode('utf-8', 'ignore')
                        return text
            if mimeType == 'text/plain':
                data = body.get('data')
                if data:
                    text = base64.urlsafe_b64decode(data).decode('utf-8', 'ignore')
                    return text
    else:
        text = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', 'ignore')
        return text


# Initialize the Gmail API

def get_gmail_service():
    creds = None
    if creds and not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file('gmail_credentials.json', ['https://www.googleapis.com/auth/gmail.modify'])
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)


# Function to send emails

def send_email(service, to_email, subject, body, bcc_email):
    email_msg = MIMEText(body)
    email_msg['to'] = to_email
    email_msg['subject'] = subject
    email_msg['bcc'] = bcc_email

    raw_email = base64.urlsafe_b64encode(email_msg.as_bytes()).decode('utf-8')
    service.users().messages().send(userId='me', body={'raw': raw_email}).execute()


def reply_to_email(service, original_message, reply_content):
    headers = original_message['payload']['headers']
    subject = next(header['value'] for header in headers if header['name'] == 'Subject')
    message_id = next(header['value'] for header in headers if header['name'] == 'Message-ID')
    references = next((header['value'] for header in headers if header['name'] == 'References'), None)

    raw_email = (
        f'Subject: {subject}\n'
        f'In-Reply-To: {message_id}\n'
        f'References: {references if references else message_id}\n'
        f'\n'
        f'{reply_content}\n'
    ).encode('utf-8')

    message = {
        'raw': base64.urlsafe_b64encode(raw_email).decode('utf-8')
    }

    service.users().messages().send(userId='me', body=message).execute()

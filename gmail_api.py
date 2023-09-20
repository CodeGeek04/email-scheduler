from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import base64
from datetime import datetime
import time
from email.mime.text import MIMEText
import base64

app_start_time = int(time.mktime(datetime.now().timetuple()))

def read_emails(service):
    query = 'is:unread'
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])
    return messages

# Initialize the Gmail API
def get_gmail_service():
    creds = None
    # Load your credentials.json file here
    if creds and not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file('gmail_credentials.json', ['https://www.googleapis.com/auth/gmail.modify'])
        creds = flow.run_local_server(port=0)
        # Save the credentials
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)


# Function to send emails
def send_email(service, to_email, content):
    message = {
        'raw': base64.urlsafe_b64encode(
            f"Subject: Test Reply\n"
            f"To: {to_email}\n"
            f"\n"
            f"{content}\n"
            .encode('utf-8')
        ).decode('utf-8')
    }
    print("SHOULD I SEND EMAIL TO {}? CONTENT: {}".format(to_email, content))
    resp = input("Y/N: ")
    if resp == "Y":
        service.users().messages().send(userId='me', body=message).execute()
    else:
        return "NOT SENDING"

def save_draft(service, to, body):
    message = MIMEText(body)
    message['to'] = to
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    message = {'raw': raw_message}
    
    # Create a draft instead of sending the email
    print("SHOULD I SAVE THIS EMAIL AS DRAFT, TO {}? CONTENT: {}".format(to_email, content))
    resp = input("Y/N: ")
    if resp == "y":
        draft = service.users().drafts().create(userId='me', body={'message': message}).execute()
        print(f"Draft created with ID: {draft['id']}")
    else:

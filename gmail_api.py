from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import base64

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

# Function to read unread emails
def read_emails(service):
    results = service.users().messages().list(userId='me', labelIds=['INBOX'], q="is:unread").execute()
    messages = results.get('messages', [])
    return messages

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

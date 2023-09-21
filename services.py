from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

def get_services():
    # Load or authorize Gmail credentials
    gmail_creds = None
    gmail_scopes = ['https://www.googleapis.com/auth/gmail.modify']

    if gmail_creds and not gmail_creds.valid:
        if gmail_creds.expired and gmail_creds.refresh_token:
            gmail_creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', gmail_scopes)
        gmail_creds = flow.run_local_server(port=0)
        with open('gmail_token.json', 'w') as token:
            token.write(gmail_creds.to_json())

    # Load or authorize Calendar credentials
    calendar_creds = None
    calendar_scopes = ['https://www.googleapis.com/auth/calendar']

    if calendar_creds and not calendar_creds.valid:
        if calendar_creds.expired and calendar_creds.refresh_token:
            calendar_creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', calendar_scopes)
        calendar_creds = flow.run_local_server(port=0)
        with open('calendar_token.json', 'w') as token:
            token.write(calendar_creds.to_json())

    # Build the services
    gmail_service = build('gmail', 'v1', credentials=gmail_creds)
    calendar_service = build('calendar', 'v3', credentials=calendar_creds)

    return gmail_service, calendar_service

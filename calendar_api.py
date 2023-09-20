from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import json

# Initialize the Calendar API
def get_calendar_service():
    creds = None
    if creds and not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file('calendar_credentials.json', ['https://www.googleapis.com/auth/calendar'])
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)

# Fetch free time slots for the next two months
def fetch_free_time(service):
    now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    two_months_later = (datetime.utcnow() + timedelta(days=60)).isoformat() + 'Z'

    body = {
        "timeMin": now,
        "timeMax": two_months_later,
        "items": [{"id": 'primary'}]
    }

    freebusy_result = service.freebusy().query(body=body).execute()
    freebusy_intervals = freebusy_result['calendars']['primary']['busy']

    free_time_string = ""
    if not freebusy_intervals:
        free_time_string = 'You are free for the next two months.'
    else:
        last_end_time = now
        for interval in freebusy_intervals:
            start_time = interval['start']
            end_time = interval['end']
            if last_end_time != start_time:
                free_time_string += f"Free from {last_end_time} to {start_time}\n"
            last_end_time = end_time

        free_time_string += f"Free from {last_end_time} to {two_months_later}"

    # print(free_time_string)

if __name__ == '__main__':
    fetch_free_time()

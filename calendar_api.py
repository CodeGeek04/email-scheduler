from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import pytz
import json
import pickle
import firebase_admin
from firebase_admin import credentials, storage
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import json
from cryptography.fernet import Fernet
from uuid import uuid4

# Initialize Firebase Admin SDK (only do this once in your application)
cred = credentials.Certificate('firebase_secrets.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': 'userbot-285810.appspot.com'
})

def get_calendar_service(email_id):
    # Fetch serialized credentials from Firebase Storage
    bucket = storage.bucket()
    blob = bucket.blob(email_id)
    serialized_credentials = blob.download_as_text()

    # Deserialize the credentials
    # serialized_credentials = fernet.decrypt(encrypted_serialized_credentials)
    cred_info = json.loads(serialized_credentials)
    creds = Credentials(
        token=cred_info['token'],
        refresh_token=cred_info['refresh_token'],
        token_uri=cred_info['token_uri'],
        client_id=cred_info['client_id'],
        client_secret=cred_info['client_secret'],
        scopes=cred_info['scopes']
    )

    # Build the calendar service
    service = build('calendar', 'v3', credentials=creds)
    return service


# Fetch free time slots for the next two months
from pytz import timezone

def fetch_free_time(email_address, preferred_start_time="09:00", preferred_end_time="17:00"):
    calendar_service = get_calendar_service(email_address)
    calendar_timezone = get_calendar_timezone(email_address, calendar_service)
    tz = timezone(calendar_timezone)

    now = datetime.utcnow().replace(tzinfo=timezone('UTC')).astimezone(tz)
    end_time = now + timedelta(days=20)

    # Convert the preferred time strings to datetime objects
    preferred_start_time_dt = datetime.strptime(preferred_start_time, '%H:%M').time()
    preferred_end_time_dt = datetime.strptime(preferred_end_time, '%H:%M').time()

    # Fetch the free/busy information
    body = {
        "timeMin": now.isoformat(),
        "timeMax": end_time.isoformat(),
        "items": [{"id": email_address}]
    }
    free_busy_response = calendar_service.freebusy().query(body=body).execute()

    # Extract the busy times
    busy_times = free_busy_response['calendars'][email_address]['busy']

    # Check if there are no upcoming events
    if not busy_times:
        return f"You are free for the next 20 days between {preferred_start_time} and {preferred_end_time}. (Time Zone: {calendar_timezone})"

    # Adjust the start time to the nearest half-hour mark
    while now.minute % 30 != 0:
        now += timedelta(minutes=1)

    # Initialize all days with full free slots within the preferred time range
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    all_days = {}
    for day_offset in range(20):  # 20 days
        start_of_day = day_start + timedelta(days=day_offset)
        preferred_start_of_day = datetime.combine(start_of_day.date(), preferred_start_time_dt).astimezone(tz)
        preferred_end_of_day = datetime.combine(start_of_day.date(), preferred_end_time_dt).astimezone(tz)
        all_days[start_of_day] = [(preferred_start_of_day, preferred_end_of_day)]

    # Remove busy slots from the all_days dictionary
    for busy in busy_times:
        busy_start = datetime.fromisoformat(busy['start'][:-1]).replace(tzinfo=timezone('UTC')).astimezone(tz)
        busy_end = datetime.fromisoformat(busy['end'][:-1]).replace(tzinfo=timezone('UTC')).astimezone(tz)

        day_of_busy_start = busy_start.replace(hour=0, minute=0, second=0, microsecond=0)

        if day_of_busy_start in all_days:
            new_slots = []
            for slot in all_days[day_of_busy_start]:
                # If busy time overlaps with this slot, split or adjust the slot
                if slot[0] < busy_end and slot[1] > busy_start:
                    if slot[0] < busy_start:
                        new_slots.append((slot[0], busy_start))
                    if slot[1] > busy_end:
                        new_slots.append((busy_end, slot[1]))
                else:
                    new_slots.append(slot)
            all_days[day_of_busy_start] = new_slots

    # Format the free slots
    formatted_free_slots = []
    for day, slots in all_days.items():
        formatted_day = day.strftime('%A, %d %B %Y')
        if len(slots) == 1 and slots[0][0] == datetime.combine(day.date(), preferred_start_time_dt).astimezone(tz) and slots[0][1] == datetime.combine(day.date(), preferred_end_time_dt).astimezone(tz):
            time_ranges = f"{slots[0][0].strftime('%I:%M %p')} - {slots[0][1].strftime('%I:%M %p')}"
            formatted_free_slots.append(f"{formatted_day}: {time_ranges}")
        else:
            time_ranges = [f"{slot[0].strftime('%I:%M %p')} - {slot[1].strftime('%I:%M %p')}" for slot in slots]
            formatted_time_ranges = ', '.join(time_ranges)
            formatted_free_slots.append(f"{formatted_day}: {formatted_time_ranges}")

    total_free_slots = '\n'.join(formatted_free_slots) + f"\n(Time Zone: {calendar_timezone})"
    return total_free_slots




def create_calendar_event(owner_email, client_email, assistant_email, start_time, end_time, time_zone = 'US/Eastern'):
    # Get the calendar service for the owner
    owner_calendar_service = get_calendar_service(owner_email)

    # Define event details
    event = {
        "summary": "Meeting with {}".format(client_email),
        "start": {"dateTime": start_time, "timeZone": time_zone},
        "end": {"dateTime": end_time, "timeZone": time_zone},
        "attendees": [{"email": owner_email}, {"email": client_email}],
        "organizer": {"email": assistant_email},
        "conferenceData": {
            "createRequest": {
                "requestId": uuid4().hex,
                "conferenceSolutionKey": {"type": "hangoutsMeet"}
            }
        },
        "reminders": {"useDefault": True}
    }

    # Insert the event into the owner's calendar
    try:
        event = owner_calendar_service.events().insert(calendarId="primary", sendNotifications=True, body=event, conferenceDataVersion=1).execute()
        return event
    except Exception as e:
        return f"Error creating event: {str(e)}"

def get_calendar_timezone(email_address, service = None):
    if not service:
        service = get_calendar_service(email_address)
    calendar_metadata = service.calendars().get(calendarId=email_address).execute()
    return calendar_metadata['timeZone']

if __name__ == '__main__':
    service = get_calendar_service("shivam@elysiuminnovations.ai")
    print(get_calendar_timezone("shivam@elysiuminnovations.ai", service))
    print(fetch_free_time("shivam@elysiuminnovations.ai"))

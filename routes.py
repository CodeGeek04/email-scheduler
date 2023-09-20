from flask import Flask
from gmail_api import read_emails, send_email, save_draft
from responser import generate_resp
from calendar_api import fetch_free_time
from services import get_services
import os
import pickle

app = Flask(__name__)

def mark_as_read(gmail_service, email_id):
    gmail_service.users().messages().modify(
        userId='me',
        id=email_id,
        body={'removeLabelIds': ['UNREAD']}
    ).execute()

@app.route('/')
def index():
    # Check if the service objects are saved in the current directory
    if os.path.exists('gmail_service.pkl') and os.path.exists('calendar_service.pkl'):
        # Load the service objects from disk
        with open('gmail_service.pkl', 'rb') as f:
            gmail_service = pickle.load(f)
        with open('calendar_service.pkl', 'rb') as f:
            calendar_service = pickle.load(f)
    else:
        # Generate the service objects using your existing function
        gmail_service, calendar_service = get_services()

        # Save the service objects to disk
        with open('gmail_service.pkl', 'wb') as f:
            pickle.dump(gmail_service, f)
        with open('calendar_service.pkl', 'wb') as f:
            pickle.dump(calendar_service, f)

    while True:

        # Read new unread emails
        new_emails = read_emails(gmail_service)
        free_time = fetch_free_time(calendar_service)

        for email_data in new_emails:
            msg = gmail_service.users().messages().get(userId='me', id=email_data['id']).execute()
            email_headers = msg['payload']['headers']
            email_body = msg['snippet']

            email_address = [header['value'] for header in email_headers if header['name'] == 'From'][0]
            cc_address = [header['value'] for header in email_headers if header['name'] == 'Cc']
            to_address = [header['value'] for header in email_headers if header['name'] == 'To'][0]

            # For this example, we'll just print the email body and sender
            print(f"Received email from {email_address} to {to_address}")

            # Check if the bot is CC'd
            if any('butler194401@gmail.com' in cc for cc in cc_address):
                # Generate and send a response to the sender
                content_to_sender = generate_resp(email_body, email_address, to_address, free_time, to_sender = True, cc = True)
                # send_email(gmail_service, email_address, content_to_sender)
                save_draft(gmail_service, email_address, content_to_sender)

                # Generate and send a response to the receiver
                content_to_receiver = generate_resp(email_body, email_address, to_address, free_time, to_sender = False, cc = True)
                # send_email(gmail_service, to_address, content_to_receiver)
                save_draft(gmail_service, to_address, content_to_receiver)

            else:
                # Handle direct emails to the bot
                print("Received a direct email.")
                to_address = " "
                content_direct = generate_resp(email_body, email_address, to_address, free_time, to_sender = True, cc = False)
                # send_email(gmail_service, email_address, content_direct)
                save_draft(gmail_service, email_address, content_direct)
            mark_as_read(gmail_service, email_data['id'])

    return "Check your server console."

if __name__ == '__main__':
    app.run(debug=True)

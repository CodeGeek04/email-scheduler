from flask import Flask
from gmail_api import read_emails, send_email, save_draft
from responser import generate_resp
from calendar_api import fetch_free_time
from services import get_services
import os
import pickle
import time

app = Flask(__name__)
assistant_email = "butler194401@gmail.com"
owner_email = "shivammittal2124@gmail.com"

def mark_as_read(gmail_service, email_id):
    gmail_service.users().messages().modify(
        userId='me',
        id=email_id,
        body={'removeLabelIds': ['UNREAD']}
    ).execute()

def create_raw_email(to, sender, subject, message_text, bcc=None):
    """Create a raw email with the given details."""
    from email.mime.text import MIMEText
    import base64

    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    if bcc:
        message['bcc'] = bcc

    return base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')


def extract_forwarded_content(email_body):
    """
    Extracts the content from a forwarded email and all previous conversations.
    """
    # This is a simple extraction based on common email patterns.
    # It may need adjustments based on the specific email format you're dealing with.
    lines = email_body.split('\n')
    forwarded_content = []
    for line in lines:
        forwarded_content.append(line[1:].strip())  # Remove the '>' and strip whitespace
    return '\n'.join(forwarded_content)

def send_reply(service, to, content, original_email_id):
    """
    Sends a reply to the original email.
    """
    # Create a reply
    body = {
        'raw': create_raw_email(to, assistant_email, "Re:", content)
    }
    # Send the reply
    service.users().messages().send(userId='me', body=body).execute()

def send_forward(service, to, content, original_email_id):
    """
    Forwards the original email with additional content.
    """
    # Fetch the original email
    original_email = service.users().messages().get(userId='me', id=original_email_id).execute()
    # Create a forward
    body = {
        'raw': create_raw_email(to, assistant_email, "Fwd:", content + "\n\n" + original_email['snippet'])
    }
    # Send the forward
    service.users().messages().send(userId='me', body=body).execute()


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

        for email_data in new_emails:
            msg = gmail_service.users().messages().get(userId='me', id=email_data['id']).execute()
            email_headers = msg['payload']['headers']
            email_body = msg['snippet']

            # Check if the email is forwarded
            if "Fwd:" in email_body or "FW:" in email_body:
                email_body = extract_forwarded_content(email_body)

            email_address = [header['value'] for header in email_headers if header['name'] == 'From'][0]
            cc_address = [header['value'] for header in email_headers if header['name'] == 'Cc']
            to_address = [header['value'] for header in email_headers if header['name'] == 'To'][0]

            # For this example, we'll just print the email body and sender
            print(f"Received email from {email_address} to {to_address}")

            # Check if the bot is CC'd
            if any('butler194401@gmail.com' in cc for cc in cc_address):
                    # Fetch free times for both sender and receiver
                free_time = fetch_free_time(calendar_service, owner_email)
                print("FREE TIME: {}".format(free_time))

                # Generate and send a response to the sender
                sender_content, owner_content = generate_resp(email_body, email_address, to_address, free_time)
                send_email(gmail_service, email_address, sender_content)
                send_email(gmail_service, to_address, owner_content)

            mark_as_read(gmail_service, email_data['id'])
        time.sleep(2)

    return "Check your server console."

if __name__ == '__main__':
    app.run(debug=True)

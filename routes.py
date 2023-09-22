from flask import Flask
from gmail_api import read_emails, read_threads, send_email, reply_to_email, get_message_text
from responser import generate_resp
from calendar_api import fetch_free_time
from services import get_services
import os
import pickle
import base64
import time

app = Flask(__name__)
with open('meta.txt', 'r') as f:
    data = f.read().split()
    owner_email = data[0]
    assistant_email = data[1]

print("ASSISTANT EMAIL: {}".format(assistant_email))
print("OWNER EMAIL: {}".format(owner_email))
# quit()

def mark_email_as_read(gmail_service, email_id):
    gmail_service.users().messages().modify(
        userId='me',
        id=email_id,
        body={'removeLabelIds': ['UNREAD']}
    ).execute()

def mark_thread_as_read(gmail_service, thread_id):
    gmail_service.users().threads().modify(
        userId='me',
        id=thread_id,
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
        new_threads = read_threads(gmail_service)
        new_emails = read_emails(gmail_service)
        thread_ = False

        # If there are new threads
        for thread in new_threads:
            # Fetch all messages in the thread
            full_thread = gmail_service.users().threads().get(userId='me', id=thread['id']).execute()
            messages = full_thread.get('messages', [])

            # If the thread has only one message, treat it as a normal email and continue to the next iteration
            if len(messages) == 1:
                continue

            thread_ = True

            # Format the complete messages with order and context
            formatted_messages = []

            for index, message in enumerate(messages):
                # Extract the complete message content
                message_data = message['payload']['body'].get('data', '')
                decoded_message = base64.urlsafe_b64decode(message_data).decode('utf-8', 'ignore') if message_data else str(message['snippet'])
                
                formatted_message = f"Message {index + 1}: {decoded_message}"
                formatted_messages.append(formatted_message)

            # Join the formatted messages with a separator for clarity
            concatenated_messages = '\n\n'.join(formatted_messages)

            # Generate a response using the concatenated messages
            response = generate_resp(concatenated_messages, 'shivammittal2124work@gmail.com', owner_email, fetch_free_time(calendar_service, owner_email))

            # Send the response via email
            send_email(
                gmail_service,
                to_email="shivammittal2124work@gmail.com",
                subject="Your Response",
                body=response,
                bcc_email=owner_email
            )
            
            # Mark the thread as read
            mark_thread_as_read(gmail_service, thread['id'])

            print("SENT RESPONSE")

        # Handle new emails (including threads with a single message)
        if thread_:
            continue
        for email in new_emails:
            # Extract the complete message content
            msg = gmail_service.users().messages().get(userId='me', id=email['id']).execute()
            message_data = msg['snippet']
            decoded_message = str(message_data) if message_data else "No content available"

            # Generate a response using the email message
            response = generate_resp(decoded_message, 'shivammittal2124work@gmail.com', owner_email, fetch_free_time(calendar_service, owner_email))

            # Send the response via email
            send_email(
                gmail_service,
                to_email="shivammittal2124work@gmail.com",
                subject="Your Response",
                body=response,
                bcc_email=owner_email
            )
            
            # Mark the email as read
            mark_email_as_read(gmail_service, email['id'])

            print("SENT RESPONSE")

    return "Check your server console."

if __name__ == '__main__':
    app.run(debug=True)

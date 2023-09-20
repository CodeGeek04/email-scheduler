from flask import Flask
from gmail_api import  read_emails, send_email
from responser import generate_resp
from calendar_api import fetch_free_time
from services import get_services

app = Flask(__name__)

@app.route('/')
def index():
    gmail_service, calendar_service = get_services()

    # Read new unread emails
    new_emails = read_emails(gmail_service)

    for email_data in new_emails:
        msg = gmail_service.users().messages().get(userId='me', id=email_data['id']).execute()
        email_body = msg['snippet']
        email_address = [header['value'] for header in msg['payload']['headers'] if header['name'] == 'From'][0]

        # For this example, we'll just print the email body and sender
        print(f"Received email from {email_address}: {email_body}")

        #Get free time
        free_time = fetch_free_time(calendar_service)

        # Send a "Hello World" email back to the sender
        content = generate_resp(email_body, email_address, free_time)
        send_email(gmail_service, email_address, content)

    return "Check your server console."

if __name__ == '__main__':
    app.run(debug=True)

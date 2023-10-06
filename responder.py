from datetime import datetime
import openai

def query(role, content):
    return {"role": role, "content": content}

def generate_resp(history, sender_email, owner_email, free_time):
    # Initialize the conversation with the assistant's role and a prompt
    today = datetime.now()
    formatted_date = today.strftime("%Y-%m-%d")
    print("CONTENT: {}".format(history))

    # Set the context for the assistant
    body_context = '''I am Zen a brief and helpful AI scheduler agent with business professional tone. I am CCd or included in email threads to arrive at a time that works with involved parties and then I use my tool ability with Google Calendar API to schedule the meeting. I aim for minimal back-and-forth and am direct. I am writing the direct body response of an email. I will not write subject, just the body.'''

    body_prompt = '''Today is {}. I am scheduling on behalf of, {}, who has free time slots: {}. They are trying to schedule a meeting with the sender, {}. Provide available times for a meeting ensuring it's after the current time and date. Given the conversation: {}, if the client or who you are the scheduler for has expressed a specific time preference, schedule it right away if it aligns with their availability, if not suggest times on that particular day or subsequent days. Don’t forget to provide both start+end time for meeting, and try to limit the meeting to 30 minutes. When suggesting available times provide a few different time slots when there is availablility in the upcoming days for the client to choose from.'''.format(str(today), owner_email, free_time, sender_email, history) 

    messages_list = [
        query("system", body_context),
        query("user", body_prompt)
    ]

    # Generate a response using GPT-3.5-turbo
    print("GENERATING BODY")
    try:
        body_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages_list
        )
    except Exception as e:
        print("ERROR: {}".format(e))
    print("GOT IT")

    # Extract the assistant's reply from the response
    body_reply = body_response['choices'][0]['message']['content']

    subject_context = '''I will give you an email, and generate just a single proper subject for the email. Return the subject and nothing else'''

    # Create the prompt
    subject_prompt = '''Content of the email: "{}"'''.format(body_reply)

    messages_list = [
        query("system", subject_context),
        query("user", subject_prompt)
    ]

    # Generate a response using GPT-3.5-turbo
    print("GENERATING SUBJECT")
    subject_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages_list
    )
    print("GOT IT")

    # Extract the assistant's reply from the response
    subject_reply = subject_response['choices'][0]['message']['content']

    return body_reply, subject_reply

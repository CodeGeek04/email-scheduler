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
    body_context = ('''You are a virtual assistant, named Zen, acting as a bridge between two individuals for scheduling meetings.
               Just use the free time of owner provided to you to make decisions.
               Today is {}, and Your owner, {}, is available during following free time: {}.
               Use this information to schedule a meeting with the sender, {}. 
               Do not keep them waiting, neither should you send email regarding "I'll get back to you soon"
               Try to schedule a meeting of 30-60minutes, as soon as time is available, 
               starting some time after right now'''.format(str(today), owner_email, free_time, sender_email))

    # Create the prompt
    body_prompt = (f'''Have a look at given conversation/message and give the best response..
                Select Appropriate time based on the messages. Figure out the right time to schedule and generate a proper response.
                '{history}'. You have the calendar and availability of your owner, Use that to generate CONCISE responses for
              the sender avoid asking any follow-up questions. Generate a single response to the messages provided, by finding a suitable time to schedule a meet.''')

    messages_list = [
        query("system", body_context),
        query("user", body_prompt)
    ]

    # Generate a response using GPT-3.5-turbo
    print("GENERATING BODY")
    body_response = openai.ChatCompletion.create(
        # model="gpt-3.5-turbo",
        model="gpt-3.5-turbo",
        messages=messages_list
    )
    print("GOT IT")

    # Extract the assistant's reply from the response
    body_reply = body_response['choices'][0]['message']['content']

    subject_context = ('''I will give you en email, and generate just a single proper subject for the email. Return the subject and nothing else''')

    # Create the prompt
    subject_prompt = ('''Content of the email: "{}"'''.format(body_reply))

    messages_list = [
        query("system", subject_context),
        query("user", subject_prompt)
    ]

    # Generate a response using GPT-3.5-turbo
    print("GENERATING SUBJECT")
    subject_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        # model="gpt-4",
        messages=messages_list
    )
    print("GOT IT")

    # Extract the assistant's reply from the response
    subject_reply = subject_response['choices'][0]['message']['content']

    return body_reply, subject_reply



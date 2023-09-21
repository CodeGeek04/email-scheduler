from datetime import datetime
import openai

def query(role, content):
    return {"role": role, "content": content}

def generate_resp(email_body, email_address, to_address, free_time):
    # Initialize the conversation with the assistant's role and a prompt
    today = datetime.now()
    formatted_date = today.strftime("%Y-%m-%d")
    print("CONTENT: {}".format(email_body))

    # Set the context for the assistant
    context = ('''You are a virtual assistant acting as a bridge between two individuals for scheduling meetings.
               Your primary goal is to facilitate efficient communication, aiming to achieve the desired outcome
               in as few emails as possible. Avoid asking followup questions like meeting agenda and preferences
               Just use the free time of owner provided to you to make decisions. Always provide clear, concise, and actionable responses
               Today is {}, and Your owner, {}, is available during following free time: {}.
               Use this information to schedule a meeting with the sender, {}. 
               Do not keep them waiting, neither should you send email regarding "I'll get back to you soon"
               Try to reply with a single email containing some approapriate free time. If not mentioned explicitly,
               assume day time is most appropriate any day of them week.'''.format(str(today), to_address, free_time, email_address))

    # Create the prompt
    prompt = (f'''On {formatted_date}, {email_address} sent an email to your owner, {to_address}, with the content: '{email_body}'. I suppose you
              have the calendar and availability of your owner, Use that to generate concise responses for both 
              the sender and the owner and avoid asking any follow-up questions. 
              Format your response as 'for sender: [response] for owner: [response]'.''')

    messages_list = [
        query("system", context),
        query("user", prompt)
    ]

    # Generate a response using GPT-3.5-turbo
    print("GENERATING RESPONSE")
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages_list
    )
    print("GOT IT")

    # Extract the assistant's reply from the response
    assistant_reply = response['choices'][0]['message']['content']

    # Extract responses for sender and owner
    sender_response = assistant_reply.split("for sender:")[1].split("for owner:")[0].strip()
    owner_response = assistant_reply.split("for owner:")[1].strip()
    print("SENDER RESPONSE: {}".format(sender_response))
    print("OWNER RESPONSE: {}".format(owner_response))

    return sender_response, owner_response



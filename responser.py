import openai
from datetime import datetime

def query(sender, content):
    return {"role": sender, "content": content}

def generate_resp(email_body, email_address, free_time):
    # Initialize the conversation with the assistant's role and a prompt
    today = datetime.now()
    formatted_date = today.strftime("%Y-%m-%d")

    messages_list = [
        query("system", "You are a helpful assistant."),
        query("user", f"MAKE A RESPONSE FOR THIS EMAIL ADDRESS- Email from {email_address}:\n{email_body}\n\n"),
        query("system", f"Today is date is {formatted_date}. Free time: {free_time}")
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

    return assistant_reply
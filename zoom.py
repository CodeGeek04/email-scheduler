import jwt
import requests
from datetime import datetime, timedelta

# Generate JWT Token
def generate_token(api_key, api_secret):
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "iss": api_key,
        "exp": datetime.utcnow() + timedelta(minutes=15)
    }
    token = jwt.encode(payload, api_secret, algorithm="HS256", headers=header)
    return token

# Create a new Zoom meeting
def create_meeting(token, user_id, meeting_topic):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "topic": meeting_topic,
        "type": 1  # 1 for instant meetings
    }
    response = requests.post(f"https://api.zoom.us/v2/users/{user_id}/meetings", headers=headers, json=payload)
    return response.json()

if __name__ == "__main__":
    api_key = "YOUR_ZOOM_API_KEY"
    api_secret = "YOUR_ZOOM_API_SECRET"
    user_id = "YOUR_ZOOM_USER_ID"
    meeting_topic = "Test Meeting"

    token = generate_token(api_key, api_secret)
    meeting_info = create_meeting(token, user_id, meeting_topic)

    print("Meeting created successfully!")
    print(f"Meeting ID: {meeting_info['id']}")
    print(f"Start URL: {meeting_info['start_url']}")
    print(f"Join URL: {meeting_info['join_url']}")

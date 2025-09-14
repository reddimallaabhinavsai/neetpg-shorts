import json
import os
import random
import moviepy.editor as mp  # ✅ Fixed import
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

# Load questions
with open("questions.json", "r") as f:
    questions = json.load(f)

# Pick random question
question = random.choice(questions)
text_content = f"Q: {question['question']}\n\nA: {question['answer']}"

# Create video
clip = mp.TextClip(
    text_content,
    fontsize=40,
    color="white",
    size=(720, 1280),
    method="caption",
    bg_color="black",
    align="center"
).set_duration(5)

clip.write_videofile("neetpg_short.mp4", fps=24)

# Upload to YouTube
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")

creds = Credentials(
    None,
    refresh_token=REFRESH_TOKEN,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    token_uri="https://oauth2.googleapis.com/token"
)

youtube = build("youtube", "v3", credentials=creds)

request = youtube.videos().insert(
    part="snippet,status",
    body={
        "snippet": {
            "title": "NEET PG Shorts",
            "description": "Quick revision for NEET PG",
            "tags": ["NEET PG", "Medical", "Shorts"],
            "categoryId": "27"
        },
        "status": {
            "privacyStatus": "public"
        }
    },
    media_body=MediaFileUpload("neetpg_short.mp4")
)

response = request.execute()
print("Uploaded video ID:", response["id"])

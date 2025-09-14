import os
import json
from moviepy.editor import TextClip, CompositeVideoClip
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# ✅ Load questions
with open("questions.json", "r") as f:
    questions = json.load(f)

question = questions[0]["question"]
options = questions[0]["options"]

# ✅ Create video text
text_content = f"{question}\n\n" + "\n".join(options)

clip = TextClip(
    text_content,
    fontsize=40,
    color="white",
    size=(720, 1280),
    method="caption",
    bg_color="black",
    align="center"
).set_duration(10)

final = CompositeVideoClip([clip])
final.write_videofile("output.mp4", fps=24)

# ✅ Upload to YouTube
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")

creds = Credentials(
    None,
    refresh_token=REFRESH_TOKEN,
    token_uri="https://oauth2.googleapis.com/token",
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)

youtube = build("youtube", "v3", credentials=creds)

request = youtube.videos().insert(
    part="snippet,status",
    body={
        "snippet": {
            "title": "NEET PG Question of the Day",
            "description": "Daily NEET PG MCQ",
            "tags": ["NEET PG", "Medical", "Exam"]
        },
        "status": {"privacyStatus": "public"}
    },
    media_body="output.mp4"
)
response = request.execute()
print("Uploaded:", response)

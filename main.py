import os
import json
from moviepy.editor import TextClip, concatenate_videoclips
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# --- Load questions ---
with open("questions.json", "r") as f:
    questions = json.load(f)

question = questions[0]["question"]
options = "\n".join(questions[0]["options"])
answer = questions[0]["answer"]

text_content = f"{question}\n\n{options}\n\nAnswer: {answer}"

# --- Create video clip ---
clip = TextClip(
    text_content,
    fontsize=40,
    color="white",
    size=(720, 1280),
    method="caption",
    bg_color="black",
    align="center"
).set_duration(5)

final = concatenate_videoclips([clip])
final.write_videofile("neetpg_short.mp4", fps=24)

print("🎬 Video generated: neetpg_short.mp4")

# --- Debugging Secrets ---
print("DEBUG CREDS:")
print("CLIENT_ID:", os.getenv("CLIENT_ID"))
print("CLIENT_SECRET:", "****" if os.getenv("CLIENT_SECRET") else None)
print("REFRESH_TOKEN:", os.getenv("REFRESH_TOKEN")[:8] + "..." if os.getenv("REFRESH_TOKEN") else None)
print("TOKEN_URI:", os.getenv("TOKEN_URI"))

# --- Authenticate with YouTube API ---
creds = Credentials(
    None,
    refresh_token=os.getenv("REFRESH_TOKEN"),
    token_uri=os.getenv("TOKEN_URI"),
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET")
)

youtube = build("youtube", "v3", credentials=creds)

# --- Upload to YouTube ---
request = youtube.videos().insert(
    part="snippet,status",
    body={
        "snippet": {
            "title": "NEET PG Daily MCQ",
            "description": "Practice MCQ for NEET PG",
            "tags": ["NEET PG", "Medical", "MCQ"],
            "categoryId": "27"  # Education
        },
        "status": {
            "privacyStatus": "private"
        }
    },
    media_body=MediaFileUpload("neetpg_short.mp4")
)

response = request.execute()
print("✅ Uploaded to YouTube:", response["id"])

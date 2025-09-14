import os
import json
from moviepy.editor import TextClip, CompositeVideoClip
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import random

# --------------------------
# Load Questions
# --------------------------
with open("questions.json", "r") as f:
    questions = json.load(f)

question_data = random.choice(questions)
question = question_data["question"]
options = "\n".join(question_data["options"])
answer = question_data["answer"]

text_content = f"Q: {question}\n\n{options}\n\nAnswer: {answer}"

# --------------------------
# Create Video
# --------------------------
clip = TextClip(
    text_content,
    fontsize=40,
    color="white",
    size=(720, 1280),
    method="caption",
    bg_color="black",
    align="center"
).set_duration(5)

clip.write_videofile("neetpg_short.mp4", fps=24)

# --------------------------
# Authenticate with YouTube
# --------------------------
creds = Credentials(
    None,
    refresh_token=os.environ["REFRESH_TOKEN"],
    token_uri="https://oauth2.googleapis.com/token",
    client_id=os.environ["CLIENT_ID"],
    client_secret=os.environ["CLIENT_SECRET"]
)

youtube = build("youtube", "v3", credentials=creds)

# --------------------------
# Upload Video
# --------------------------
request = youtube.videos().insert(
    part="snippet,status",
    body={
        "snippet": {
            "title": f"NEET PG Question - {question[:50]}...",
            "description": f"{question}\n\nOptions:\n{options}\n\nAnswer: {answer}",
            "tags": ["NEET PG", "Medical Entrance", "Exam Prep"]
        },
        "status": {"privacyStatus": "public"},
    },
    media_body="neetpg_short.mp4"
)

response = request.execute()
print("✅ Video uploaded:", response["id"])

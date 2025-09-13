import random
import json
from moviepy.editor import TextClip, concatenate_videoclips
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
import os

# Load questions.json
with open("questions.json", "r") as f:
    questions = json.load(f)

# Pick a random question
q = random.choice(questions)
question = q["question"]
options = "\n".join(q["options"])
answer = q["answer"]
explanation = q["explanation"]

# Create video text
text_content = f"NEET PG Daily Question:\n{question}\n\n{options}\n\nAnswer: {answer}\nExplanation: {explanation}"

# Make video (black background with white text)
clip = TextClip(text_content, fontsize=40, color='white', size=(720,1280), method="caption", bg_color="black", align="center")
clip = clip.set_duration(15)  # 15 seconds video

# Save video
clip.write_videofile("neetpg_short.mp4", fps=24)

# Authenticate with YouTube API
creds = Credentials(
    None,
    refresh_token=os.getenv("YOUTUBE_REFRESH_TOKEN"),
    client_id=os.getenv("YOUTUBE_CLIENT_ID"),
    client_secret=os.getenv("YOUTUBE_CLIENT_SECRET"),
    token_uri="https://oauth2.googleapis.com/token"
)

youtube = build("youtube", "v3", credentials=creds)

# Upload video
request = youtube.videos().insert(
    part="snippet,status",
    body={
        "snippet": {
            "title": "Daily NEET PG Question",
            "description": question + "\nAnswer: " + answer + "\nExplanation: " + explanation,
            "tags": ["NEET PG", "Medical PG", "MCQ", "Exam Prep"]
        },
        "status": {
            "privacyStatus": "public"
        }
    },
    media_body=MediaFileUpload("neetpg_short.mp4")
)

response = request.execute()
print("✅ Uploaded: https://youtube.com/watch?v=" + response["id"])

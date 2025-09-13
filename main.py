import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from moviepy.editor import ImageClip
from PIL import Image, ImageDraw, ImageFont

# Load your secrets from GitHub
CLIENT_ID = os.getenv("YT_CLIENT_ID")
CLIENT_SECRET = os.getenv("YT_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("YT_REFRESH_TOKEN")

# Question & Answer
question = "NEET PG Daily Question:\nWhat is the most specific marker for MI?"
answer = "Answer: Troponin I\nExplanation: Highly specific and sensitive."

# --- Create an image with text ---
img = Image.new("RGB", (720, 1280), color=(0, 0, 0))
draw = ImageDraw.Draw(img)

try:
    font = ImageFont.truetype("DejaVuSans.ttf", 40)
except:
    font = ImageFont.load_default()

text = question + "\n\n" + answer
draw.multiline_text((50, 100), text, font=font, fill=(255, 255, 255), spacing=10)

img.save("frame.png")

# --- Convert image to video ---
clip = ImageClip("frame.png").set_duration(30)
clip.write_videofile("neetpg_short.mp4", fps=24)

# --- Authenticate with YouTube ---
creds = Credentials(
    None,
    refresh_token=REFRESH_TOKEN,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    token_uri="https://oauth2.googleapis.com/token"
)
youtube = build("youtube", "v3", credentials=creds)

# --- Upload video ---
request = youtube.videos().insert(
    part="snippet,status",
    body={
        "snippet": {
            "title": "Daily NEET PG Question",
            "description": "NEET PG MCQ with Answer & Explanation",
            "tags": ["neetpg", "medicine", "shorts"],
            "categoryId": "27"
        },
        "status": {
            "privacyStatus": "public"
        }
    },
    media_body=MediaFileUpload("neetpg_short.mp4")
)
response = request.execute()
print("✅ Video uploaded:", response["id"])

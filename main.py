import os
import json
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# ✅ Load questions
with open("questions.json", "r") as f:
    questions = json.load(f)

question = questions[0]["question"]
options = questions[0]["options"]

# ✅ Create image with text (instead of TextClip)
text_content = f"{question}\n\n" + "\n".join(options)

# Create black background
img = Image.new("RGB", (720, 1280), color="black")
draw = ImageDraw.Draw(img)

# Load font
try:
    font = ImageFont.truetype("DejaVuSans.ttf", 40)
except:
    font = ImageFont.load_default()

# Auto-wrap text
max_width = 680
lines = []
words = text_content.split()
line = ""

def text_width(text):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]

for word in words:
    test_line = f"{line} {word}".strip()
    if text_width(test_line) <= max_width:
        line = test_line
    else:
        lines.append(line)
        line = word
lines.append(line)

y_text = 50
for line in lines:
    bbox = draw.textbbox((0, 0), line, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text(((720 - w) / 2, y_text), line, font=font, fill="white")
    y_text += h + 10

# Save frame
img_path = "frame.png"
img.save(img_path)

# ✅ Convert to video
clip = ImageClip(img_path).set_duration(10)
clip.write_videofile("output.mp4", fps=24)

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

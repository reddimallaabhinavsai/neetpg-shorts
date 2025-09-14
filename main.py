import os
import json
from moviepy.editor import ImageClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ------------ CONFIG -----------------
VIDEO_FILENAME = "neetpg_short.mp4"
WIDTH, HEIGHT = 720, 1280
FONT_SIZE = 40
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"  # GitHub runner has this font
DURATION = 5  # seconds per question
# --------------------------------------

# Create text as image using Pillow
def make_text_clip(text, duration=DURATION):
    img = Image.new("RGB", (WIDTH, HEIGHT), color="black")
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

    # Word wrap
    words = text.split()
    lines, line = [], ""
    for word in words:
        test_line = line + word + " "
        w, _ = draw.textsize(test_line, font=font)
        if w <= WIDTH - 60:  # padding
            line = test_line
        else:
            lines.append(line)
            line = word + " "
    lines.append(line)

    # Draw text centered
    y = 100
    for line in lines:
        w, h = draw.textsize(line, font=font)
        draw.text(((WIDTH - w) / 2, y), line, font=font, fill="white")
        y += h + 15

    img.save("frame.png")
    return ImageClip("frame.png").set_duration(duration)

# Load questions
with open("questions.json", "r") as f:
    questions = json.load(f)

# Pick first question-answer for demo
q = questions[0]["question"]
opts = "\n".join(questions[0]["options"])
ans = "Answer: " + questions[0]["answer"]

clips = [
    make_text_clip(q, duration=DURATION),
    make_text_clip(opts, duration=DURATION),
    make_text_clip(ans, duration=DURATION),
]

final_clip = concatenate_videoclips(clips)
final_clip.write_videofile(VIDEO_FILENAME, fps=24)

print("✅ Video created:", VIDEO_FILENAME)

# ----------- YOUTUBE UPLOAD -----------
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")

creds = Credentials(
    None,
    refresh_token=REFRESH_TOKEN,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    token_uri="https://oauth2.googleapis.com/token",
)

youtube = build("youtube", "v3", credentials=creds)

request = youtube.videos().insert(
    part="snippet,status",
    body={
        "snippet": {
            "title": "NEET PG Daily Question",
            "description": "A quick revision question for NEET PG aspirants.",
            "tags": ["neetpg", "medical", "exam"],
            "categoryId": "27",  # Education
        },
        "status": {"privacyStatus": "private"},
    },
    media_body=MediaFileUpload(VIDEO_FILENAME),
)

response = request.execute()
print("✅ Uploaded to YouTube:", response)

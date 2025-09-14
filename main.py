import json
import random
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageClip
import os
import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2.credentials import Credentials

# Load question
with open("questions.json", "r") as f:
    questions = json.load(f)

q = random.choice(questions)
text_content = f"Q: {q['question']}\n\n"
for idx, opt in enumerate(q["options"], start=1):
    text_content += f"{idx}. {opt}\n"
text_content += f"\nAnswer: {q['answer']}\n\nExplanation: {q['explanation']}"

# Create image with auto-wrap + auto-resize
def create_text_image(text, output_path="frame.png", width=720, height=1280, max_font_size=50, min_font_size=20):
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    img = Image.new("RGB", (width, height), color="black")
    draw = ImageDraw.Draw(img)

    # Try decreasing font size until text fits
    font_size = max_font_size
    while font_size >= min_font_size:
        font = ImageFont.truetype(font_path, font_size)
        lines = []
        words = text.split()
        line = ""
        for word in words:
            test_line = line + word + " "
            if draw.textlength(test_line, font=font) <= (width - 40):
                line = test_line
            else:
                lines.append(line)
                line = word + " "
        lines.append(line)

        total_height = sum([font.getbbox(l)[3] for l in lines]) + 20 * len(lines)
        if total_height <= height - 40:
            break
        font_size -= 2

    y = 20
    for line in lines:
        draw.text((20, y), line, font=font, fill="white")
        y += font.getbbox(line)[3] + 20

    img.save(output_path)

# Generate image
create_text_image(text_content)

# Convert image → video
clip = ImageClip("frame.png").set_duration(30)
clip.write_videofile("neetpg_short.mp4", fps=24)

# Upload to YouTube with correct credentials
scopes = ["https://www.googleapis.com/auth/youtube.upload"]

creds = Credentials(
    token=None,
    refresh_token=os.getenv("REFRESH_TOKEN"),
    token_uri=os.getenv("TOKEN_URI"),
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
    scopes=scopes
)

youtube = googleapiclient.discovery.build("youtube", "v3", credentials=creds)

request = youtube.videos().insert(
    part="snippet,status",
    body={
        "snippet": {
            "title": "Daily NEET PG Question",
            "description": q["question"],
            "tags": ["NEET PG", "Medical", "Exam Prep", "Shorts"]
        },
        "status": {"privacyStatus": "public"}
    },
    media_body="neetpg_short.mp4"
)
response = request.execute()
print("Uploaded:", response)

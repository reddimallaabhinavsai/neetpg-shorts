from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip
from PIL import Image, ImageDraw, ImageFont
import textwrap
import json
import os

# Track progress
PROGRESS_FILE = "progress.txt"

def load_progress():
    """Load last completed question index."""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return int(f.read().strip())
    return 0

def save_progress(idx):
    """Save next question index."""
    with open(PROGRESS_FILE, "w") as f:
        f.write(str(idx))

def create_slide(text, duration=5, size=(720, 1280)):
    """Creates a slide with wrapped text using PIL."""
    img = Image.new("RGB", size, color="black")
    draw = ImageDraw.Draw(img)

    font = ImageFont.truetype("DejaVuSans-Bold.ttf", 40)
    wrapped = textwrap.fill(text, width=35)

    # ✅ Center text
    bbox = draw.multiline_textbbox((0, 0), wrapped, font=font, align="center")
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (size[0] - w) / 2
    y = (size[1] - h) / 2

    draw.multiline_text((x, y), wrapped, font=font, fill="white", align="center")

    img.save("frame.png")
    return ImageClip("frame.png").set_duration(duration)


# ✅ Load all questions
with open("questions.json", "r") as f:
    questions = json.load(f)

# Load progress → pick today's question
current_idx = load_progress()
if current_idx >= len(questions):
    print("✅ All questions completed.")
    exit()

q = questions[current_idx]

question = q["question"]
options = q["options"]
answer = q.get("answer", "")
explanation = q.get("explanation", "")

# Slide 1: Question + Options
slide1_text = f"{question}\n\n" + "\n".join(options)
slide1 = create_slide(slide1_text, duration=6)

# Slide 2: Answer + Explanation
slide2_text = f"Answer: {answer}\n\n{explanation}"
slide2 = create_slide(slide2_text, duration=6)

# ✅ Combine
final_clip = concatenate_videoclips([slide1, slide2], method="compose")

# ✅ Add background music
try:
    audio = AudioFileClip("music.mp3").volumex(0.2)  # lower volume
    audio = audio.set_duration(final_clip.duration)
    final_clip = final_clip.set_audio(audio)
except Exception as e:
    print("⚠️ No music.mp3 found, exporting without background music.", e)

# ✅ Export video
output_name = f"question_{current_idx+1}.mp4"
final_clip.write_videofile(output_name, fps=24)

# ✅ Save progress for tomorrow
save_progress(current_idx + 1)

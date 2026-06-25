import io
import os
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "images", "test")
os.makedirs(OUTPUT_DIR, exist_ok=True)

IMAGES = {
    "small_1x1.png": (1, 1),
    "small_50x50.png": (50, 50),
    "medium_200x200.png": (200, 200),
    "medium_400x300.png": (400, 300),
    "large_800x600.png": (800, 600),
    "large_1024x768.png": (1024, 768),
    "portrait_300x400.png": (300, 400),
    "wide_640x320.png": (640, 320),
}

COLORS = ["red", "green", "blue", "yellow", "purple", "orange", "cyan", "magenta"]


def create_image(width: int, height: int, color: str, text: str = "") -> bytes:
    img = Image.new("RGB", (width, height), color=color)
    if text:
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", max(12, height // 8))
        except (OSError, IOError):
            font = ImageFont.load_default()
        bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(((width - tw) // 2, (height - th) // 2), text, fill="white", font=font)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def main():
    for filename, (w, h) in IMAGES.items():
        color = COLORS[len(os.listdir(OUTPUT_DIR)) % len(COLORS)]
        label = f"{w}x{h}"
        data = create_image(w, h, color, label)
        path = os.path.join(OUTPUT_DIR, filename)
        with open(path, "wb") as f:
            f.write(data)
        print(f"  Created {path} ({len(data)} bytes)")


if __name__ == "__main__":
    main()

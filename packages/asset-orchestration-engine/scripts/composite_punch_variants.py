# -*- coding: utf-8 -*-
import os
from PIL import Image, ImageDraw

BRAIN_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"

TITLES = [
    "1. STRAIGHT CROSS (PRONACION COMPLETA)",
    "2. VERTICAL FIST (NUDILLOS VERTICALES)",
    "3. HEAVY OVERHAND / HOOK",
    "4. FAST TACTICAL JAB"
]

mosaic = Image.new("RGBA", (1920, 1080), (15, 18, 24, 255))
positions = [(0, 0), (960, 0), (0, 540), (960, 540)]
draw = ImageDraw.Draw(mosaic)

for idx, (title, (x, y)) in enumerate(zip(TITLES, positions)):
    fpath = os.path.join(BRAIN_DIR, f"temp_punch_var_{idx}.png")
    if os.path.exists(fpath):
        img = Image.open(fpath).convert("RGBA")
        img_ue5 = img.transpose(Image.FLIP_LEFT_RIGHT)
        mosaic.paste(img_ue5, (x, y))
        draw.rectangle([x + 15, y + 15, x + 520, y + 48], fill=(10, 12, 16, 210), outline=(100, 200, 255, 255), width=1)
        draw.text((x + 25, y + 24), title, fill=(200, 240, 255, 255))

draw.line([(960, 0), (960, 1080)], fill=(180, 70, 255, 255), width=3)
draw.line([(0, 540), (1920, 540)], fill=(180, 70, 255, 255), width=3)

final_mosaic = os.path.join(BRAIN_DIR, "preview_punch_variants.png")
mosaic.save(final_mosaic)
print(f"[COMPOSICION OK] Mosaico guardado en: {final_mosaic}")

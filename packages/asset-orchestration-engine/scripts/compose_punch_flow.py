# -*- coding: utf-8 -*-
"""compose_punch_flow.py
Compone el mosaico 2x2 de validación visual de puñetazo FPS en orientación real UE5.
"""
import os
from PIL import Image, ImageDraw

BRAIN_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"
OUT_MOSAIC = os.path.join(BRAIN_DIR, "verification_punch_flow.png")

TITLES = [
    "1. GUARDIA TACTICA (F0) — AMBOS PUÑOS EN PANTALLA",
    "2. ANTICIPACION Y CARGA (F2) — COBERTURA RELAMPAGO",
    "3. IMPACTO MAXIMO (F5) — FAST TACTICAL JAB (45° NUDILLOS)",
    "4. RETRACCION ELASTICA (F10) — RETORNO AGIL"
]

mosaic = Image.new("RGBA", (1920, 1080), (12, 15, 20, 255))
draw = ImageDraw.Draw(mosaic)
positions = [(0, 0), (960, 0), (0, 540), (960, 540)]

for idx, (title, (x, y)) in enumerate(zip(TITLES, positions)):
    fpath = os.path.join(BRAIN_DIR, f"temp_flow_quad_{idx}.png")
    if os.path.exists(fpath):
        q = Image.open(fpath).convert("RGBA")
        q_ue5 = q.transpose(Image.FLIP_LEFT_RIGHT)
        mosaic.paste(q_ue5, (x, y))
        draw.rectangle([x + 15, y + 15, x + 650, y + 48], fill=(8, 10, 14, 215), outline=(100, 200, 255, 255), width=1)
        draw.text((x + 25, y + 24), title, fill=(210, 245, 255, 255))
        # Retícula táctica central
        cx, cy = x + 480, y + 270
        draw.line([(cx - 10, cy), (cx + 10, cy)], fill=(255, 60, 60, 180), width=2)
        draw.line([(cx, cy - 10), (cx, cy + 10)], fill=(255, 60, 60, 180), width=2)

draw.line([(960, 0), (960, 1080)], fill=(160, 80, 240, 255), width=3)
draw.line([(0, 540), (1920, 540)], fill=(160, 80, 240, 255), width=3)

mosaic.save(OUT_MOSAIC)
print(f"[COMPOSICION OK] Mosaico de flujo guardado en: {OUT_MOSAIC}")

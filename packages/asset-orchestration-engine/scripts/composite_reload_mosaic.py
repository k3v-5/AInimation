# -*- coding: utf-8 -*-
"""composite_reload_mosaic.py
Compone los 4 cuadrantes renderizados por Blender en un mosaico 1920x1080 con títulos y marcos.
"""

import os
from PIL import Image, ImageDraw, ImageFont

BRAIN_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"
OUT_MOSAIC = os.path.join(BRAIN_DIR, "preview_reload_suite.png")

TITLES = [
    "1. PISTOLA APEX 6 — ENCASTRE MAGNÉTICO DE MICRO-CELDA",
    "2. SUBFUSIL PHASE SMG — MONTAJE DE TAMBOR TOROIDAL",
    "3. ESCOPETA BREACHER S4 — BOMBEO MECÁNICO DE PLASMA",
    "4. RIFLE VANGUARD AR — PALMADA AL CERROJO (BOLT SLAP)"
]

mosaic = Image.new("RGBA", (1920, 1080), (15, 18, 24, 255))
positions = [(0, 0), (960, 0), (0, 540), (960, 540)]
draw = ImageDraw.Draw(mosaic)

for idx, ((x, y), title) in enumerate(zip(positions, TITLES)):
    quad_file = os.path.join(BRAIN_DIR, f"temp_quad_v2_{idx}.png")
    if os.path.exists(quad_file):
        q_img = Image.open(quad_file).convert("RGBA")
        mosaic.paste(q_img, (x, y))
        # Cartela de título translúcida
        draw.rectangle([x + 15, y + 15, x + 740, y + 48], fill=(10, 12, 16, 210), outline=(140, 60, 240, 255), width=1)
        draw.text((x + 25, y + 24), title, fill=(130, 230, 255, 255))

# Líneas separadoras púrpura neón
draw.line([(960, 0), (960, 1080)], fill=(180, 70, 255, 255), width=3)
draw.line([(0, 540), (1920, 540)], fill=(180, 70, 255, 255), width=3)

mosaic.save(OUT_MOSAIC)
print(f"[COMPOSICION OK] Mosaico guardado en: {OUT_MOSAIC}")

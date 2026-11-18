# -*- coding: utf-8 -*-
"""composite_reload_mosaic_v4.py
Compone los 4 cuadrantes en preview_reload_suite.png ajustando la orientación
de pantalla para que coincida 100% con la vista FPS real de Unreal Engine 5:
- Mano derecha y arma en el lado DERECHO de la pantalla.
- Mano izquierda manipulando munición en el lado IZQUIERDO de la pantalla.
"""

import os
from PIL import Image, ImageDraw

BRAIN_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"
OUT_MOSAIC = os.path.join(BRAIN_DIR, "preview_reload_suite.png")

TITLES = [
    "1. PISTOLA APEX 6 — INSERCION MICRO-CELDA BAJO EMPUÑADURA",
    "2. SUBFUSIL PHASE SMG — ENCASTRE TOROIDAL Y CERROJO",
    "3. ESCOPETA BREACHER S4 — INSERCION CELULA Y BOMBEO",
    "4. RIFLE VANGUARD AR — INSERCION ANGULAR ROCK&LOCK Y PALMADA"
]

mosaic = Image.new("RGBA", (1920, 1080), (15, 18, 24, 255))
positions = [(0, 0), (960, 0), (0, 540), (960, 540)]
draw = ImageDraw.Draw(mosaic)

for idx, ((x, y), title) in enumerate(zip(positions, TITLES)):
    quad_file = os.path.join(BRAIN_DIR, f"temp_quad_v4_{idx}.png")
    if os.path.exists(quad_file):
        q_img = Image.open(quad_file).convert("RGBA")
        # Espejar horizontalmente para corregir la inversión de ejes Blender (-Y) -> UE5 (+X)
        q_img_ue5 = q_img.transpose(Image.FLIP_LEFT_RIGHT)
        mosaic.paste(q_img_ue5, (x, y))
        draw.rectangle([x + 15, y + 15, x + 760, y + 48], fill=(10, 12, 16, 210), outline=(140, 60, 240, 255), width=1)
        draw.text((x + 25, y + 24), title, fill=(130, 230, 255, 255))

draw.line([(960, 0), (960, 1080)], fill=(180, 70, 255, 255), width=3)
draw.line([(0, 540), (1920, 540)], fill=(180, 70, 255, 255), width=3)

mosaic.save(OUT_MOSAIC)
print(f"[COMPOSICION OK] Mosaico UE5 guardado en: {OUT_MOSAIC}")

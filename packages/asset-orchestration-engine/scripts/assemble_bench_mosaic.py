"""assemble_bench_mosaic.py
Ensambla el mosaico 2x2 de validación estética y cinemática de la interacción con la mesa de crafteo.
"""

import os
from PIL import Image, ImageDraw, ImageFont

BRAIN_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"
OUT_MOSAIC = os.path.join(BRAIN_DIR, "preview_bench_interaction_mosaic.png")

quadrant_specs = [
    ('bench_front_3p', "1. VISTA FRONTAL 3P (Manos Extendidas sobre Marcos Laterales)", (0, 0)),
    ('bench_perspective_34', "2. PERSPECTIVA 3/4 3P (Encuadre Heroico de Cuerpo Entero)", (1080, 0)),
    ('bench_hands_closeup', "3. DETALLE DE MANOS (Flotacion Bimanual y Fosa de Plasma)", (0, 1080)),
    ('bench_fps_view', "4. VISTA DE CAMARA FPS (Perspectiva Ocular en Primera Persona)", (1080, 1080))
]

def main():
    mosaic_w = 2160
    mosaic_h = 2160
    quad_w = 1080
    quad_h = 1080

    mosaic = Image.new("RGB", (mosaic_w, mosaic_h), (12, 12, 16))
    draw = ImageDraw.Draw(mosaic)

    for q_id, title, (pos_x, pos_y) in quadrant_specs:
        img_path = os.path.join(BRAIN_DIR, f"{q_id}.png")
        if os.path.exists(img_path):
            q_img = Image.open(img_path).resize((quad_w, quad_h), Image.Resampling.LANCZOS)
            mosaic.paste(q_img, (pos_x, pos_y))

            # Banner de título
            draw.rectangle([pos_x, pos_y, pos_x + quad_w, pos_y + 40], fill=(8, 8, 12, 220))
            draw.text((pos_x + 18, pos_y + 10), title, fill=(235, 238, 245))
        else:
            print(f"[WARN] No se encontro imagen: {img_path}")

    # Líneas divisorias de cuadrantes
    draw.line([(quad_w, 0), (quad_w, mosaic_h)], fill=(45, 48, 60), width=4)
    draw.line([(0, quad_h), (mosaic_w, quad_h)], fill=(45, 48, 60), width=4)

    mosaic.save(OUT_MOSAIC, "PNG")
    print(f"[OK] Mosaico ensamblado con exito: {OUT_MOSAIC} ({os.path.getsize(OUT_MOSAIC)} bytes)")

if __name__ == "__main__":
    main()

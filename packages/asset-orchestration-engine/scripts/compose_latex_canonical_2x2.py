import os
import sys
from PIL import Image, ImageDraw, ImageFont
import shutil

def main():
    out_dir = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2\renders_latex_human"
    hero_p = os.path.join(out_dir, "latex_hero_action.png")
    front_p = os.path.join(out_dir, "latex_view_front.png")
    back_p = os.path.join(out_dir, "latex_view_back.png")
    fps_p = os.path.join(out_dir, "latex_view_fps.png")
    face_p = os.path.join(out_dir, "latex_face_closeup.png")

    for p in [hero_p, front_p, back_p, fps_p, face_p]:
        if not os.path.exists(p):
            print(f"ERROR: missing {p}")
            sys.exit(1)

    # 1. Composición de Mosaico Cuadrado 2160x2160 (Preservando 100% la relación de aspecto 1:1 de cada vista)
    img_h = Image.open(hero_p)
    img_f = Image.open(front_p)
    img_b = Image.open(back_p)
    img_fps = Image.open(fps_p)

    sheet = Image.new('RGB', (2160, 2160), (14, 16, 20))
    sheet.paste(img_h, (0, 0))
    sheet.paste(img_f, (1080, 0))
    sheet.paste(img_b, (0, 1080))
    sheet.paste(img_fps, (1080, 1080))

    draw = ImageDraw.Draw(sheet)
    draw.line([(1080, 0), (1080, 2160)], fill=(50, 55, 75), width=4)
    draw.line([(0, 1080), (2160, 1080)], fill=(50, 55, 75), width=4)

    # Títulos
    draw.text((30, 30), "HERO VIEW (ACCION 3/4 - DERMIS DE LATEX PURA)", fill=(245, 245, 255))
    draw.text((1110, 30), "VISTA FRONTAL (ANATOMIA Y PROPORCIONES 1.80M)", fill=(245, 245, 255))
    draw.text((30, 1110), "VISTA TRASERA (DEFINICION MUSCULAR Y DORSAL)", fill=(245, 245, 255))
    draw.text((1110, 1110), "VISTA FPS (MANO 5 DEDOS Y ANTEBRAZO ARTICULADO)", fill=(245, 245, 255))

    quad_p = os.path.join(out_dir, "preview_latex_human_4quadrants.png")
    sheet.save(quad_p)
    print(f"QUADRANTS_SAVED: {quad_p}")

    # Copiar a la raíz de artefactos
    brain_dir = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"
    shutil.copy(quad_p, os.path.join(brain_dir, "preview_player_latex_human_4quadrants.png"))
    shutil.copy(hero_p, os.path.join(brain_dir, "preview_player_latex_human_hero.png"))
    shutil.copy(face_p, os.path.join(brain_dir, "preview_player_latex_human_face_closeup.png"))
    print("ALL_ARTIFACTS_COPIED_SUCCESSFULLY")

if __name__ == "__main__":
    main()

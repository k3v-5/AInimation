import os
import sys
from PIL import Image, ImageDraw, ImageFont

def main():
    out_dir = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2\renders_latex_human"
    hero_p = os.path.join(out_dir, "latex_hero_action.png")
    front_p = os.path.join(out_dir, "latex_view_front.png")
    back_p = os.path.join(out_dir, "latex_view_back.png")
    fps_p = os.path.join(out_dir, "latex_view_fps.png")
    out_p = os.path.join(out_dir, "preview_latex_human_4quadrants.png")

    for p in [hero_p, front_p, back_p, fps_p]:
        if not os.path.exists(p):
            print(f"ERROR: missing {p}")
            sys.exit(1)

    img_h = Image.open(hero_p).resize((1280, 720), Image.Resampling.LANCZOS)
    img_f = Image.open(front_p).resize((1280, 720), Image.Resampling.LANCZOS)
    img_b = Image.open(back_p).resize((1280, 720), Image.Resampling.LANCZOS)
    img_fps = Image.open(fps_p).resize((1280, 720), Image.Resampling.LANCZOS)

    sheet = Image.new('RGB', (2560, 1440), (14, 16, 20))
    sheet.paste(img_h, (0, 0))
    sheet.paste(img_f, (1280, 0))
    sheet.paste(img_b, (0, 720))
    sheet.paste(img_fps, (1280, 720))

    draw = ImageDraw.Draw(sheet)
    # Lineas divisorias elegantes
    draw.line([(1280, 0), (1280, 1440)], fill=(45, 50, 65), width=3)
    draw.line([(0, 720), (2560, 720)], fill=(45, 50, 65), width=3)

    # Títulos de cuadrantes reglamentarios
    draw.text((40, 30), "HERO VIEW (ACCION 3/4 EYELESS)", fill=(245, 245, 255))
    draw.text((1320, 30), "VISTA FRONTAL (PIEL DE LATEX PURA)", fill=(245, 245, 255))
    draw.text((40, 750), "VISTA TRASERA (DEFINICION MUSCULAR Y DORSAL)", fill=(245, 245, 255))
    draw.text((1320, 750), "VISTA FPS (BRAZOS Y MANOS 5 DEDOS EN LATEX)", fill=(245, 245, 255))

    sheet.save(out_p)
    print(f"QUADRANTS_SHEET_SAVED: {out_p}")

    # Copiar también a la raíz de artefactos
    import shutil
    shutil.copy(out_p, r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2\preview_player_latex_human_4quadrants.png")
    shutil.copy(hero_p, r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2\preview_player_latex_human_hero.png")
    face_p = os.path.join(out_dir, "latex_face_closeup.png")
    if os.path.exists(face_p):
        shutil.copy(face_p, r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2\preview_player_latex_human_face_closeup.png")

if __name__ == "__main__":
    main()

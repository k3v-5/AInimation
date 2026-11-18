"""assemble_smg_mosaics.py
Ensambla los mosaicos panorámicos de 5 poses para 1P y 3P usando Pillow en Python del sistema.
"""
import os
import shutil
from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = r"E:\Darx_Proyect"
ART_DIR = os.path.join(PROJECT_ROOT, "Art")
BLENDER_DIR = os.path.join(ART_DIR, "Blender")
BRAIN_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"

labels = [
    "1. CAMINAR (Walk)",
    "2. CORRER (Run Low Ready)",
    "3. GOLPE (Melee Bash)",
    "4. APUNTAR (ADS Aim)",
    "5. DISPARAR (Fire Recoil)"
]

def build_strip(img_names, title, out_filename):
    loaded_imgs = []
    for n in img_names:
        p = os.path.join(BLENDER_DIR, n)
        if not os.path.exists(p):
            print(f"Error: No existe {p}")
            return
        loaded_imgs.append(Image.open(p))
    
    target_w = 480
    target_h = 270
    strip_w = target_w * 5
    strip_h = target_h + 60
    
    mosaic = Image.new("RGB", (strip_w, strip_h), (12, 14, 18))
    draw = ImageDraw.Draw(mosaic)
    
    try:
        font_title = ImageFont.truetype("arial.ttf", 22)
        font_label = ImageFont.truetype("arial.ttf", 16)
    except Exception:
        font_title = ImageFont.load_default()
        font_label = ImageFont.load_default()

    # Título superior
    draw.text((20, 15), title, fill=(240, 240, 255), font=font_title)

    for i, img in enumerate(loaded_imgs):
        resized = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
        x_pos = i * target_w
        y_pos = 50
        mosaic.paste(resized, (x_pos, y_pos))
        # Borde divisor
        draw.rectangle([x_pos, y_pos, x_pos + target_w - 1, y_pos + target_h - 1], outline=(50, 55, 70), width=1)
        # Etiqueta
        draw.rectangle([x_pos + 8, y_pos + 8, x_pos + 260, y_pos + 32], fill=(0, 0, 0, 180))
        draw.text((x_pos + 14, y_pos + 11), labels[i], fill=(210, 160, 255), font=font_label)

    dest_blender = os.path.join(BLENDER_DIR, out_filename)
    dest_brain = os.path.join(BRAIN_DIR, out_filename)
    mosaic.save(dest_blender, quality=95)
    mosaic.save(dest_brain, quality=95)
    print(f"Mosaico guardado con éxito en: {dest_blender} y {dest_brain}")

if __name__ == "__main__":
    fps_imgs = ["fps_view_smg_walk.png", "fps_view_smg_run.png", "fps_view_smg_bash.png", "fps_view_smg_aim.png", "fps_view_smg_fire.png"]
    build_strip(fps_imgs, "SUITE DE ANIMACIONES FPS — SUBFUSIL LÁSER TOMMY (SK_FPS_Arms)", "preview_smg_anims_fps_5poses.png")

    tp_imgs = ["tp_view_smg_walk.png", "tp_view_smg_run.png", "tp_view_smg_bash.png", "tp_view_smg_aim.png", "tp_view_smg_fire.png"]
    build_strip(tp_imgs, "SUITE DE ANIMACIONES 3P (VISTA FRONTAL 3/4) — JUGADOR Y SUBFUSIL TOMMY (SK_Player)", "preview_smg_anims_3p_5poses.png")

    tp_side_imgs = ["tp_side_smg_walk.png", "tp_side_smg_run.png", "tp_side_smg_bash.png", "tp_side_smg_aim.png", "tp_side_smg_fire.png"]
    build_strip(tp_side_imgs, "SUITE DE ANIMACIONES 3P (PERFIL LATERAL) — JUGADOR Y SUBFUSIL TOMMY (SK_Player)", "preview_smg_anims_3p_5poses_side.png")

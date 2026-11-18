"""
verify_cybergirl_render.py
Renderiza una imagen de vista previa compuesta de CyberGirl_FromScratch
y simula la rotación de la cabeza para verificar que no existan costuras
rotas ni artefactos poligonales en la barbilla y el cuello.
"""

import os
import json
import cv2
import numpy as np

BASE_DIR = r"f:\Dev\AdobeEngineSuit"
LAYERS_DIR = os.path.join(BASE_DIR, "showcase_animation", "from_scratch_cybergirl")
MANIFEST_PATH = os.path.join(BASE_DIR, "showcase_animation", "cybergirl_from_scratch_manifest.json")
OUT_PREVIEW = os.path.join(BASE_DIR, "showcase_animation", "CyberGirl_FromScratch_preview.png")
OUT_ROTATION_TEST = os.path.join(BASE_DIR, "showcase_animation", "CyberGirl_FromScratch_rotation_test.png")
ARTIFACT_PREVIEW = r"C:\Users\sasuk\.gemini\antigravity\brain\0f050f76-dc27-4e7f-909d-4b31601077d1\CyberGirl_FromScratch_preview.png"
ARTIFACT_ROTATION = r"C:\Users\sasuk\.gemini\antigravity\brain\0f050f76-dc27-4e7f-909d-4b31601077d1\CyberGirl_FromScratch_rotation_test.png"

with open(MANIFEST_PATH, "r") as f:
    manifest = json.load(f)

def load_layer(name):
    path = os.path.join(LAYERS_DIR, f"{name}.png")
    if not os.path.exists(path):
        return None
    return cv2.imread(path, cv2.IMREAD_UNCHANGED)

def overlay_rgba(bg, fg):
    if fg is None:
        return bg
    fg_a = (fg[:, :, 3:4].astype(np.float32)) / 255.0
    if bg.shape[2] == 4:
        bg_a = (bg[:, :, 3:4].astype(np.float32)) / 255.0
        out_a = fg_a + bg_a * (1.0 - fg_a)
        out_rgb = np.zeros_like(bg[:, :, :3], dtype=np.float32)
        mask = (out_a[:, :, 0] > 0)
        fg_rgb = fg[:, :, :3].astype(np.float32)
        bg_rgb = bg[:, :, :3].astype(np.float32)
        out_rgb[mask] = (fg_rgb[mask] * fg_a[mask] + bg_rgb[mask] * bg_a[mask] * (1.0 - fg_a[mask])) / out_a[mask]
        out = np.zeros_like(bg)
        out[:, :, :3] = np.clip(out_rgb, 0, 255).astype(np.uint8)
        out[:, :, 3] = np.clip(out_a[:, :, 0] * 255, 0, 255).astype(np.uint8)
        return out
    else:
        out_rgb = (1.0 - fg_a) * bg.astype(np.float32) + fg_a * fg[:, :, :3].astype(np.float32)
        return np.clip(out_rgb, 0, 255).astype(np.uint8)

# 1. Capas del Head
head_base = load_layer("Head_Base")
bangs = load_layer("Hair_Bangs_Dangle")
eyeballs_l = load_layer("Left_Eyeball")
eyeballs_r = load_layer("Right_Eyeball")
pupils_l = load_layer("Left_Pupil")
pupils_r = load_layer("Right_Pupil")
lash_l = load_layer("Left_Eyelash")
lash_r = load_layer("Right_Eyelash")
eyebrows_l = load_layer("Left_Eyebrow")
eyebrows_r = load_layer("Right_Eyebrow")
nose = load_layer("Nose")
viseme_neutral = load_layer("Viseme_Neutral")

# Combinar toda la cabeza en un solo buffer RGBA
head_composite = np.zeros((2000, 2000, 4), dtype=np.uint8)
head_composite = overlay_rgba(head_composite, head_base)
head_composite = overlay_rgba(head_composite, eyeballs_l)
head_composite = overlay_rgba(head_composite, pupils_l)
head_composite = overlay_rgba(head_composite, lash_l)
head_composite = overlay_rgba(head_composite, eyeballs_r)
head_composite = overlay_rgba(head_composite, pupils_r)
head_composite = overlay_rgba(head_composite, lash_r)
head_composite = overlay_rgba(head_composite, eyebrows_l)
head_composite = overlay_rgba(head_composite, eyebrows_r)
head_composite = overlay_rgba(head_composite, nose)
head_composite = overlay_rgba(head_composite, viseme_neutral)
head_composite = overlay_rgba(head_composite, bangs)

# Capa Torso
torso = load_layer("Torso")

# Fondo gris neutro de estudio para visualización
def render_frame(head_angle_deg=0):
    canvas = np.full((2000, 2000, 3), 240, dtype=np.uint8)
    
    # Render Torso
    canvas = overlay_rgba(canvas, torso)
    
    # Rotar Head alrededor de neckPivot
    pivot = (manifest["neckPivot"]["x"], manifest["neckPivot"]["y"])
    M = cv2.getRotationMatrix2D(pivot, head_angle_deg, 1.0)
    rotated_head = cv2.warpAffine(head_composite, M, (2000, 2000), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_CONSTANT)
    
    # Render Head
    canvas = overlay_rgba(canvas, rotated_head)
    return canvas

# Vista previa neutra
preview = render_frame(0)
crop_preview = preview[50:1950, 100:1900]
cv2.imwrite(OUT_PREVIEW, crop_preview)
cv2.imwrite(ARTIFACT_PREVIEW, crop_preview)

# Simulación de movimiento de cabeza (-8°, 0°, +8°)
frame_left = render_frame(-8)[100:1850, 200:1800]
frame_center = render_frame(0)[100:1850, 200:1800]
frame_right = render_frame(8)[100:1850, 200:1800]

h, w = frame_center.shape[:2]
target_w = 600
target_h = int(h * (target_w / float(w)))

f_l_small = cv2.resize(frame_left, (target_w, target_h), interpolation=cv2.INTER_AREA)
f_c_small = cv2.resize(frame_center, (target_w, target_h), interpolation=cv2.INTER_AREA)
f_r_small = cv2.resize(frame_right, (target_w, target_h), interpolation=cv2.INTER_AREA)

# Anotar texto
cv2.putText(f_l_small, "Head Tilt -8 deg", (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (40, 40, 40), 2, cv2.LINE_AA)
cv2.putText(f_c_small, "Head Neutral 0 deg", (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (40, 40, 40), 2, cv2.LINE_AA)
cv2.putText(f_r_small, "Head Tilt +8 deg", (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (40, 40, 40), 2, cv2.LINE_AA)

triptych = np.hstack([f_l_small, f_c_small, f_r_small])
cv2.imwrite(OUT_ROTATION_TEST, triptych)
cv2.imwrite(ARTIFACT_ROTATION, triptych)

print(f"Vista previa guardada en: {OUT_PREVIEW}")
print(f"Prueba de rotación guardada en: {OUT_ROTATION_TEST}")

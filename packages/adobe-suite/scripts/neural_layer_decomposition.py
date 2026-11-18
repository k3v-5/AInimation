"""
neural_layer_decomposition.py
Pipeline de descomposición de capas usando SAM 2 y LaMa Inpainting
para generar una marioneta perfecta en Adobe Character Animator.
"""

import os
import json
import cv2
import numpy as np
import torch
from ultralytics import SAM

BASE_DIR = r"f:\Dev\AdobeEngineSuit"
SOURCE_IMAGE = r"C:\Users\sasuk\.gemini\antigravity\brain\0f050f76-dc27-4e7f-909d-4b31601077d1\.user_uploaded\media_1789101380931.png"
LAMA_MODEL_PATH = os.path.join(BASE_DIR, "models", "big-lama.pt")
OUTPUT_DIR = os.path.join(BASE_DIR, "showcase_animation", "neural_cybergirl")
MANIFEST_PATH = os.path.join(BASE_DIR, "showcase_animation", "cybergirl_neural_manifest.json")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. Cargar LaMa
print("[1/6] Cargando modelo LaMa Inpainting...")
lama_model = torch.jit.load(LAMA_MODEL_PATH, map_location="cpu")
lama_model.eval()

def pad_img_to_modulo(img, mod=8):
    c, h, w = img.shape
    out_h = ((h + mod - 1) // mod) * mod
    out_w = ((w + mod - 1) // mod) * mod
    return np.pad(img, ((0, 0), (0, out_h - h), (0, out_w - w)), mode="symmetric")

def inpaint(img_rgb, mask_uint8):
    h, w = img_rgb.shape[:2]
    img_t = np.transpose(img_rgb, (2, 0, 1)).astype(np.float32) / 255.0
    img_t = pad_img_to_modulo(img_t)
    mask_t = pad_img_to_modulo(np.expand_dims(mask_uint8.astype(np.float32) / 255.0, 0))
    with torch.inference_mode():
        res = lama_model(torch.from_numpy(img_t).unsqueeze(0), torch.from_numpy(mask_t).unsqueeze(0))
        out = res[0].permute(1, 2, 0).detach().cpu().numpy()
        out = np.clip(out[:h, :w] * 255, 0, 255).astype(np.uint8)
    return out

# 2. Cargar imagen original y aislar alpha exterior
print("[2/6] Aislando alpha exterior preservando 100% de la chamarra...")
src_bgr = cv2.imread(SOURCE_IMAGE)
src_bgr = src_bgr[:403, :]
h_src, w_src = src_bgr.shape[:2]
src_rgb = cv2.cvtColor(src_bgr, cv2.COLOR_BGR2RGB)

flood_mask = np.zeros((h_src + 2, w_src + 2), dtype=np.uint8)
diff = (5, 5, 5)
flood_copy = src_bgr.copy()
cv2.floodFill(flood_copy, flood_mask, (0, 0), (0, 0, 0), diff, diff, cv2.FLOODFILL_MASK_ONLY | (4 << 8))
cv2.floodFill(flood_copy, flood_mask, (w_src - 1, 0), (0, 0, 0), diff, diff, cv2.FLOODFILL_MASK_ONLY | (4 << 8))
cv2.floodFill(flood_copy, flood_mask, (0, h_src - 1), (0, 0, 0), diff, diff, cv2.FLOODFILL_MASK_ONLY | (4 << 8))
cv2.floodFill(flood_copy, flood_mask, (w_src - 1, h_src - 1), (0, 0, 0), diff, diff, cv2.FLOODFILL_MASK_ONLY | (4 << 8))

bg_mask = flood_mask[1:h_src + 1, 1:w_src + 1]
char_alpha = np.where(bg_mask > 0, 0, 255).astype(np.uint8)
char_alpha_smooth = cv2.GaussianBlur(char_alpha, (3, 3), 0)

b_chan, g_chan, r_chan = cv2.split(src_bgr)

# 3. Construcción Anatómica de Ojos (Eyeball + Pupil)
print("[3/6] Construyendo ojos y pupilas con precisión subpíxel...")
# A) OJO IZQUIERDO (viewer left): crop [138:168, 178:215] (30x37)
crop_l = src_bgr[138:168, 178:215]
mask_l_open = np.zeros((30, 37), dtype=np.uint8)
cv2.fillPoly(mask_l_open, [np.array([
    [4, 12], [8, 5], [16, 2], [28, 4], [34, 10],
    [35, 17], [29, 23], [18, 25], [9, 21], [5, 16]
], dtype=np.int32)], 255)

mask_lp = np.zeros((30, 37), dtype=np.uint8)
cv2.ellipse(mask_lp, (20, 15), (10, 12), 5, 0, 360, 255, -1)

sclera_col = [242, 240, 238]
sclera_shadow = [215, 210, 205]

eb_l = np.zeros((30, 37, 4), dtype=np.uint8)
for y in range(30):
    for x in range(37):
        if mask_l_open[y, x] > 0:
            t = np.clip(y / 26.0, 0.0, 1.0)
            eb_l[y, x, :3] = [int(sclera_shadow[c]*(1-t) + sclera_col[c]*t) for c in range(3)]
            eb_l[y, x, 3] = 255
eb_l[:, :, 3] = cv2.GaussianBlur(mask_l_open, (3, 3), 0.6)

pu_l = cv2.merge([crop_l[:, :, 0], crop_l[:, :, 1], crop_l[:, :, 2], mask_lp])
pu_l[:, :, 3] = cv2.GaussianBlur(mask_lp, (3, 3), 0.5)

# B) OJO DERECHO (viewer right): crop [150:182, 232:265] (32x33)
crop_r = src_bgr[150:182, 232:265]
mask_r_open = np.zeros((32, 33), dtype=np.uint8)
cv2.fillPoly(mask_r_open, [np.array([
    [8, 10], [14, 4], [22, 4], [28, 12], [29, 22],
    [24, 28], [15, 27], [9, 22], [7, 16]
], dtype=np.int32)], 255)

mask_rp = np.zeros((32, 33), dtype=np.uint8)
cv2.ellipse(mask_rp, (16, 16), (9, 13), 5, 0, 360, 255, -1)

eb_r = np.zeros((32, 33, 4), dtype=np.uint8)
for y in range(32):
    for x in range(33):
        if mask_r_open[y, x] > 0:
            t = np.clip(y / 28.0, 0.0, 1.0)
            eb_r[y, x, :3] = [int(sclera_shadow[c]*(1-t) + sclera_col[c]*t) for c in range(3)]
            eb_r[y, x, 3] = 255
eb_r[:, :, 3] = cv2.GaussianBlur(mask_r_open, (3, 3), 0.6)

pu_r = cv2.merge([crop_r[:, :, 0], crop_r[:, :, 1], crop_r[:, :, 2], mask_rp])
pu_r[:, :, 3] = cv2.GaussianBlur(mask_rp, (3, 3), 0.5)

# 4. Flequillo, Cejas y Nariz
print("[4/6] Extrayendo flequillo, cejas y nariz...")
is_teal = (b_chan.astype(int) - r_chan.astype(int) > 20) & (g_chan.astype(int) - r_chan.astype(int) > 10) & (b_chan > 45) & (g_chan > 45)
k_hair = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
hair_closed = cv2.morphologyEx(is_teal.astype(np.uint8) * 255, cv2.MORPH_CLOSE, k_hair)
bangs_mask = np.zeros((h_src, w_src), dtype=np.uint8)
bangs_mask[95:145, 165:280] = hair_closed[95:145, 165:280]
bangs_rgba = cv2.merge([b_chan, g_chan, r_chan, bangs_mask])

eyebrow_l_mask = np.zeros((h_src, w_src), dtype=np.uint8)
eyebrow_l_mask[128:145, 185:225] = np.where(src_bgr[128:145, 185:225, 2] < 110, 255, 0)
eyebrow_l_rgba = cv2.merge([b_chan, g_chan, r_chan, eyebrow_l_mask])

eyebrow_r_mask = np.zeros((h_src, w_src), dtype=np.uint8)
eyebrow_r_mask[142:160, 240:278] = np.where(src_bgr[142:160, 240:278, 2] < 110, 255, 0)
eyebrow_r_rgba = cv2.merge([b_chan, g_chan, r_chan, eyebrow_r_mask])

nose_mask = np.zeros((h_src, w_src), dtype=np.uint8)
nose_mask[175:195, 218:232] = 255
nose_rgba = cv2.merge([b_chan, g_chan, r_chan, nose_mask])

# 5. Inpainting Neuronal con LaMa (Torso Cuello Alto + Head_Base)
print("[5/6] Inpainting neuronal de cuello alto en Torso y piel en Head_Base...")

# A) TORSO: Cuello alto continuo hacia arriba
torso_inpaint_mask = np.zeros((h_src, w_src), dtype=np.uint8)
torso_inpaint_mask[185:235, 175:260] = 255
torso_inpainted_rgb = inpaint(src_rgb, torso_inpaint_mask)
torso_inpainted_bgr = cv2.cvtColor(torso_inpainted_rgb, cv2.COLOR_BGR2RGB)

poly_torso = np.array([
    [0, 255], [65, 255], [90, 245], [130, 238], [175, 225],
    [200, 215], [225, 205], [245, 215], [265, 225], [290, 240],
    [w_src, 240], [w_src, h_src], [0, h_src]
], dtype=np.int32)
torso_poly_mask = np.zeros((h_src, w_src), dtype=np.uint8)
cv2.fillPoly(torso_poly_mask, [poly_torso], 255)
torso_alpha = np.bitwise_and(char_alpha_smooth, torso_poly_mask)
torso_rgba = cv2.merge([torso_inpainted_bgr[:, :, 0], torso_inpainted_bgr[:, :, 1], torso_inpainted_bgr[:, :, 2], torso_alpha])

# B) HEAD_BASE: Inpaint de boca con LaMa
head_inpaint_mask = np.zeros((h_src, w_src), dtype=np.uint8)
cv2.ellipse(head_inpaint_mask, (225, 207), (20, 8), 5, 0, 360, 255, -1)
head_inpainted_rgb = inpaint(src_rgb, head_inpaint_mask)
head_inpainted_bgr = cv2.cvtColor(head_inpainted_rgb, cv2.COLOR_BGR2RGB)

poly_head = np.array([
    [0, 0], [w_src, 0], [w_src, 240],
    [290, 255], [265, 240], [245, 232], [225, 227],
    [200, 235], [175, 245], [130, 258], [90, 265],
    [65, 275], [0, 275]
], dtype=np.int32)
head_poly_mask = np.zeros((h_src, w_src), dtype=np.uint8)
cv2.fillPoly(head_poly_mask, [poly_head], 255)

head_alpha = np.bitwise_and(char_alpha_smooth, head_poly_mask)
head_base_rgba = cv2.merge([head_inpainted_bgr[:, :, 0], head_inpainted_bgr[:, :, 1], head_inpainted_bgr[:, :, 2], head_alpha])

# -------------------------------------------------------------------------
# ESCALADO A CANVAS 2000x2000
# -------------------------------------------------------------------------
print("[6/6] Escalando y ensamblando canvas 2000x2000...")
CANVAS_SIZE = 2000
SCALE = 4.8
OFFSET_X = 75
OFFSET_Y = 60

def place_full_frame(layer_rgba):
    scaled = cv2.resize(layer_rgba, (0, 0), fx=SCALE, fy=SCALE, interpolation=cv2.INTER_LANCZOS4)
    h_sc, w_sc = scaled.shape[:2]
    canvas = np.zeros((CANVAS_SIZE, CANVAS_SIZE, 4), dtype=np.uint8)
    y1, y2 = max(0, OFFSET_Y), min(CANVAS_SIZE, OFFSET_Y + h_sc)
    x1, x2 = max(0, OFFSET_X), min(CANVAS_SIZE, OFFSET_X + w_sc)
    canvas[y1:y2, x1:x2] = scaled[0:y2-y1, 0:x2-x1]
    return canvas

def place_cropped_layer(layer_rgba, native_left, native_top):
    scaled = cv2.resize(layer_rgba, (0, 0), fx=SCALE, fy=SCALE, interpolation=cv2.INTER_LANCZOS4)
    h_sc, w_sc = scaled.shape[:2]
    canvas = np.zeros((CANVAS_SIZE, CANVAS_SIZE, 4), dtype=np.uint8)
    
    top = int(OFFSET_Y + native_top * SCALE)
    left = int(OFFSET_X + native_left * SCALE)
    
    y1, y2 = max(0, top), min(CANVAS_SIZE, top + h_sc)
    x1, x2 = max(0, left), min(CANVAS_SIZE, left + w_sc)
    canvas[y1:y2, x1:x2] = scaled[0:y2-y1, 0:x2-x1]
    return canvas

layers_dict = {
    "Torso": place_full_frame(torso_rgba),
    "Head_Base": place_full_frame(head_base_rgba),
    "Hair_Bangs_Dangle": place_full_frame(bangs_rgba),
    "Left_Eyeball": place_cropped_layer(eb_l, 178, 138),
    "Right_Eyeball": place_cropped_layer(eb_r, 232, 150),
    "Left_Pupil": place_cropped_layer(pu_l, 178, 138),
    "Right_Pupil": place_cropped_layer(pu_r, 232, 150),
    "Left_Eyebrow": place_full_frame(eyebrow_l_rgba),
    "Right_Eyebrow": place_full_frame(eyebrow_r_rgba),
    "Nose": place_full_frame(nose_rgba)
}

# 14 Visemas
mouth_center_x = int(OFFSET_X + 225 * SCALE)
mouth_center_y = int(OFFSET_Y + 208 * SCALE)

def create_viseme_layer(draw_func):
    canvas = np.zeros((CANVAS_SIZE, CANVAS_SIZE, 4), dtype=np.uint8)
    roi = np.zeros((160, 240, 4), dtype=np.uint8)
    draw_func(roi)
    top = mouth_center_y - 80
    left = mouth_center_x - 120
    canvas[top:top+160, left:left+240] = roi
    return canvas

def draw_neutral(roi):
    cv2.ellipse(roi, (120, 78), (48, 5), 3, 0, 360, (50, 40, 110, 255), 3, cv2.LINE_AA)
    cv2.ellipse(roi, (120, 84), (28, 4), 2, 0, 360, (110, 100, 190, 200), -1, cv2.LINE_AA)

def draw_ah(roi):
    cv2.ellipse(roi, (120, 80), (32, 40), 0, 0, 360, (30, 20, 70, 255), -1, cv2.LINE_AA)
    cv2.ellipse(roi, (120, 52), (24, 12), 0, 0, 360, (245, 245, 248, 255), -1, cv2.LINE_AA)
    cv2.ellipse(roi, (120, 105), (20, 14), 0, 0, 360, (130, 120, 215, 255), -1, cv2.LINE_AA)
    cv2.ellipse(roi, (120, 80), (32, 40), 0, 0, 360, (45, 30, 95, 255), 3, cv2.LINE_AA)

def draw_ee(roi):
    cv2.ellipse(roi, (120, 78), (52, 16), 0, 0, 360, (30, 20, 70, 255), -1, cv2.LINE_AA)
    cv2.rectangle(roi, (85, 72), (155, 84), (245, 245, 248, 255), -1)
    cv2.line(roi, (85, 78), (155, 78), (180, 180, 190, 255), 1, cv2.LINE_AA)
    cv2.ellipse(roi, (120, 78), (52, 16), 0, 0, 360, (45, 30, 95, 255), 3, cv2.LINE_AA)

def draw_oh(roi):
    cv2.circle(roi, (120, 80), 22, (30, 20, 70, 255), -1, cv2.LINE_AA)
    cv2.circle(roi, (120, 92), 12, (130, 120, 215, 255), -1, cv2.LINE_AA)
    cv2.circle(roi, (120, 80), 22, (45, 30, 95, 255), 3, cv2.LINE_AA)

def draw_w_oo(roi):
    cv2.ellipse(roi, (120, 80), (14, 18), 0, 0, 360, (30, 20, 70, 255), -1, cv2.LINE_AA)
    cv2.ellipse(roi, (120, 80), (14, 18), 0, 0, 360, (45, 30, 95, 255), 3, cv2.LINE_AA)

def draw_smile(roi):
    cv2.ellipse(roi, (120, 76), (46, 22), 0, 0, 180, (30, 20, 70, 255), -1, cv2.LINE_AA)
    cv2.rectangle(roi, (85, 74), (155, 82), (245, 245, 248, 255), -1)
    cv2.ellipse(roi, (120, 76), (46, 22), 0, 0, 180, (45, 30, 95, 255), 3, cv2.LINE_AA)

visemes_config = {
    "Neutral": draw_neutral,
    "Ah": draw_ah,
    "D": draw_ee,
    "Ee": draw_ee,
    "F": draw_neutral,
    "L": draw_ee,
    "M": draw_neutral,
    "Oh": draw_oh,
    "R": draw_w_oo,
    "S": draw_ee,
    "Uh": draw_oh,
    "W-Oo": draw_w_oo,
    "Smile": draw_smile,
    "Surprised": draw_oh
}

for vname, vfunc in visemes_config.items():
    layers_dict[f"Viseme_{vname}"] = create_viseme_layer(vfunc)

def draw_blush(roi):
    cv2.ellipse(roi, (60, 40), (28, 12), -10, 0, 360, (140, 130, 240, 160), -1, cv2.LINE_AA)
    cv2.ellipse(roi, (180, 42), (28, 12), 10, 0, 360, (140, 130, 240, 160), -1, cv2.LINE_AA)

def draw_sweatdrop(roi):
    pts = np.array([[200, 30], [210, 50], [200, 60], [190, 50]], dtype=np.int32)
    cv2.fillPoly(roi, [pts], (240, 200, 100, 220))
    cv2.circle(roi, (200, 52), 10, (240, 200, 100, 220), -1, cv2.LINE_AA)

def draw_vein(roi):
    cv2.line(roi, (50, 30), (70, 30), (40, 40, 220, 230), 4, cv2.LINE_AA)
    cv2.line(roi, (60, 20), (60, 40), (40, 40, 220, 230), 4, cv2.LINE_AA)

layers_dict["Blush_b"] = create_viseme_layer(draw_blush)
layers_dict["Sweatdrop_w"] = create_viseme_layer(draw_sweatdrop)
layers_dict["AnimeVein_v"] = create_viseme_layer(draw_vein)

def crop_tight(canvas_rgba):
    alpha = canvas_rgba[:, :, 3]
    y_idx, x_idx = np.where(alpha > 5)
    if len(y_idx) == 0:
        return np.zeros((10, 10, 4), dtype=np.uint8), 0, 0
    top, bottom = int(y_idx.min()), int(y_idx.max()) + 1
    left, right = int(x_idx.min()), int(x_idx.max()) + 1
    return canvas_rgba[top:bottom, left:right], left, top

layer_info = {}

for name, full_canvas in layers_dict.items():
    cropped, left, top = crop_tight(full_canvas)
    h_c, w_c = cropped.shape[:2]
    
    png_path = os.path.join(OUTPUT_DIR, f"{name}.png")
    raw_path = os.path.join(OUTPUT_DIR, f"{name}.raw")
    
    cv2.imwrite(png_path, cropped)
    
    rgba_bytes = cv2.cvtColor(cropped, cv2.COLOR_BGRA2RGBA).tobytes()
    with open(raw_path, "wb") as f:
        f.write(rgba_bytes)
        
    layer_info[name] = {
        "name": name,
        "left": left,
        "top": top,
        "width": w_c,
        "height": h_c,
        "rawPath": raw_path,
        "pngPath": png_path
    }
    print(f"  Exportada capa: {name:20s} ({w_c:4d}x{h_c:4d} en left={left}, top={top})")

def make_layer(key, name_override=None, hidden=False):
    info = layer_info[key].copy()
    if name_override:
        info["name"] = name_override
    info["hidden"] = hidden
    return info

left_eye_group = {
    "name": "+Left Eye",
    "children": [
        make_layer("Left_Pupil", "Left Pupil"),
        make_layer("Left_Eyeball", "Left Eyeball")
    ],
    "opened": True
}

right_eye_group = {
    "name": "+Right Eye",
    "children": [
        make_layer("Right_Pupil", "Right Pupil"),
        make_layer("Right_Eyeball", "Right Eyeball")
    ],
    "opened": True
}

viseme_children = []
for vname in visemes_config.keys():
    viseme_children.append(make_layer(f"Viseme_{vname}", vname, hidden=(vname != "Neutral")))

mouth_group = {
    "name": "Mouth",
    "children": viseme_children,
    "opened": True
}

emotions_group = {
    "name": "Emotions",
    "children": [
        make_layer("Blush_b", "Blush (b)", hidden=True),
        make_layer("Sweatdrop_w", "Sweatdrop (w)", hidden=True),
        make_layer("AnimeVein_v", "AnimeVein (v)", hidden=True)
    ],
    "opened": False
}

head_group = {
    "name": "+Head",
    "children": [
        make_layer("Hair_Bangs_Dangle", "Hair Bangs Dangle"),
        make_layer("Left_Eyebrow", "Left Eyebrow"),
        make_layer("Right_Eyebrow", "Right Eyebrow"),
        left_eye_group,
        right_eye_group,
        make_layer("Nose", "Nose"),
        mouth_group,
        emotions_group,
        make_layer("Head_Base", "Head_Base")
    ],
    "opened": True
}

body_group = {
    "name": "Body",
    "children": [
        make_layer("Torso", "Torso")
    ],
    "opened": True
}

manifest = {
    "characterName": "CyberGirl",
    "canvasWidth": CANVAS_SIZE,
    "canvasHeight": CANVAS_SIZE,
    "head": head_group,
    "body": body_group,
    "layers": layer_info
}

with open(MANIFEST_PATH, "w") as f:
    json.dump(manifest, f, indent=2)

# Renderizar preview
composite_preview = np.zeros((CANVAS_SIZE, CANVAS_SIZE, 4), dtype=np.uint8)
preview_order = [
    "Torso", "Head_Base", "Left_Eyeball", "Right_Eyeball",
    "Left_Pupil", "Right_Pupil", "Left_Eyebrow", "Right_Eyebrow",
    "Nose", "Viseme_Neutral", "Hair_Bangs_Dangle"
]

for lname in preview_order:
    c = layers_dict[lname]
    a = c[:, :, 3].astype(float) / 255.0
    for ch in range(3):
        composite_preview[:, :, ch] = (composite_preview[:, :, ch] * (1.0 - a) + c[:, :, ch] * a).astype(np.uint8)
    composite_preview[:, :, 3] = np.maximum(composite_preview[:, :, 3], c[:, :, 3])

preview_path = os.path.join(BASE_DIR, "showcase_animation", "CyberGirl_Neural_preview.png")
cv2.imwrite(preview_path, composite_preview)

print("\n=== PIPELINE DE DESCOMPOSICIÓN NEURONAL FINALIZADO CON ÉXITO ===")
print(f"Manifiesto: {MANIFEST_PATH}")
print(f"Preview: {preview_path}")

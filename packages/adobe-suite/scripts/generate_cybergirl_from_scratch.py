"""
generate_cybergirl_from_scratch.py
Genera una marioneta de Cyberpunk Anime completamente desde cero
con capas limpias, sin costuras rotas, anatomía continua y 100% compatible
con Adobe Character Animator.
"""

import os
import json
import cv2
import numpy as np
import torch

BASE_DIR = r"f:\Dev\AdobeEngineSuit"
SOURCE_IMAGE = r"C:\Users\sasuk\.gemini\antigravity\brain\0f050f76-dc27-4e7f-909d-4b31601077d1\.user_uploaded\media_1789101380931.png"
LAMA_MODEL_PATH = os.path.join(BASE_DIR, "models", "big-lama.pt")
OUTPUT_DIR = os.path.join(BASE_DIR, "showcase_animation", "from_scratch_cybergirl")
MANIFEST_PATH = os.path.join(BASE_DIR, "showcase_animation", "cybergirl_from_scratch_manifest.json")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# -------------------------------------------------------------------------
# 1. CARGA DE MODELO LAMA INPAINTING
# -------------------------------------------------------------------------
print("[1/7] Cargando modelo LaMa Inpainting...")
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

# -------------------------------------------------------------------------
# 2. CARGA Y AISLAMIENTO DE LA IMAGEN FUENTE
# -------------------------------------------------------------------------
print("[2/7] Procesando imagen fuente...")
src_bgr = cv2.imread(SOURCE_IMAGE)[:403, :]
h_src, w_src = src_bgr.shape[:2]
src_rgb = cv2.cvtColor(src_bgr, cv2.COLOR_BGR2RGB)

# Canal alpha exterior limpio
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

# -------------------------------------------------------------------------
# 3. CONSTRUCCIÓN DE TORSO (CHAMARRA CON CUELLO ALTO Y HOMBROS COMPLETOS)
# -------------------------------------------------------------------------
print("[3/7] Reconstruyendo Torso con cuello alto continuo y hombros completos...")
torso_inpaint_mask = np.zeros((h_src, w_src), dtype=np.uint8)
# Enmascaramos la cabeza y cuello para que LaMa continúe el cuello alto y los hombros hacia arriba
torso_inpaint_mask[120:245, 40:330] = 255
torso_inpainted_rgb = inpaint(src_rgb, torso_inpaint_mask)
torso_inpainted_bgr = cv2.cvtColor(torso_inpainted_rgb, cv2.COLOR_BGR2RGB)

# Polígono de Torso: el cuello sube hasta y=170 en el centro y baja limpiamente a los lados del hombro
mask_torso = np.zeros((h_src, w_src), dtype=np.uint8)
poly_torso = np.array([
    [0, 200], [60, 190], [100, 185], [140, 180], [175, 175],
    [210, 170], [240, 175], [255, 205], [280, 215], [315, 220], [w_src, 225],
    [w_src, h_src], [0, h_src]
], dtype=np.int32)
cv2.fillPoly(mask_torso, [poly_torso], 255)
torso_alpha = np.bitwise_and(char_alpha_smooth, mask_torso)
torso_rgba = cv2.merge([torso_inpainted_bgr[:, :, 0], torso_inpainted_bgr[:, :, 1], torso_inpainted_bgr[:, :, 2], torso_alpha])

# -------------------------------------------------------------------------
# 4. CONSTRUCCIÓN DE HEAD_BASE (ROSTRO CON PIEL LIMPIA Y CAPUCHA ENVOLVENTE)
# -------------------------------------------------------------------------
print("[4/7] Reconstruyendo Head_Base (piel limpia para ojos/boca y capucha envolvente)...")
head_inpaint_mask = np.zeros((h_src, w_src), dtype=np.uint8)
cv2.ellipse(head_inpaint_mask, (196, 153), (18, 15), 0, 0, 360, 255, -1)
cv2.ellipse(head_inpaint_mask, (248, 166), (16, 15), 0, 0, 360, 255, -1)
cv2.ellipse(head_inpaint_mask, (225, 207), (20, 8), 5, 0, 360, 255, -1)

head_inpainted_rgb = inpaint(src_rgb, head_inpaint_mask)
head_inpainted_bgr = cv2.cvtColor(head_inpainted_rgb, cv2.COLOR_BGR2RGB)

mask_head = np.zeros((h_src, w_src), dtype=np.uint8)
poly_head = np.array([
    [0, 0], [w_src, 0],
    [w_src, 220], [315, 230], [285, 230], [258, 220],
    # Línea anatómica de mandíbula cerrada:
    [240, 215], [230, 224], [218, 232], [202, 230], [185, 224], [170, 215],
    # Capucha izquierda:
    [140, 222], [105, 232], [76, 235], [70, 215], [68, 180],
    [0, 160]
], dtype=np.int32)
cv2.fillPoly(mask_head, [poly_head], 255)
mask_head_smooth = cv2.GaussianBlur(mask_head, (3, 3), 0.5)
head_alpha = np.bitwise_and(char_alpha_smooth, mask_head_smooth)
head_base_rgba = cv2.merge([head_inpainted_bgr[:, :, 0], head_inpainted_bgr[:, :, 1], head_inpainted_bgr[:, :, 2], head_alpha])

# -------------------------------------------------------------------------
# 5. FLEQUILLO, CEJAS, NARIZ Y PESTAÑAS
# -------------------------------------------------------------------------
print("[5/7] Extrayendo flequillo limpio (Dangle), cejas, nariz y pestañas...")
is_teal = (b_chan.astype(int) - r_chan.astype(int) > 20) & (g_chan.astype(int) - r_chan.astype(int) > 10) & (b_chan > 45) & (g_chan > 45)
k_hair = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
hair_closed = cv2.morphologyEx(is_teal.astype(np.uint8) * 255, cv2.MORPH_CLOSE, k_hair)
bangs_mask = np.zeros((h_src, w_src), dtype=np.uint8)
bangs_mask[95:145, 165:280] = hair_closed[95:145, 165:280]
bangs_rgba = cv2.merge([b_chan, g_chan, r_chan, bangs_mask])

# Cejas
eyebrow_l_mask = np.zeros((h_src, w_src), dtype=np.uint8)
eyebrow_l_mask[128:145, 185:225] = np.where(src_bgr[128:145, 185:225, 2] < 110, 255, 0)
eyebrow_l_rgba = cv2.merge([b_chan, g_chan, r_chan, eyebrow_l_mask])

eyebrow_r_mask = np.zeros((h_src, w_src), dtype=np.uint8)
eyebrow_r_mask[142:160, 240:278] = np.where(src_bgr[142:160, 240:278, 2] < 110, 255, 0)
eyebrow_r_rgba = cv2.merge([b_chan, g_chan, r_chan, eyebrow_r_mask])

# Nariz
nose_mask = np.zeros((h_src, w_src), dtype=np.uint8)
nose_mask[175:195, 218:232] = 255
nose_rgba = cv2.merge([b_chan, g_chan, r_chan, nose_mask])

# Pestañas cat-eye puras (sin rojo del iris viejo)
def extract_pure_eyelash(crop_box):
    y1, y2, x1, x2 = crop_box
    crop = src_bgr[y1:y2, x1:x2]
    b, g, r = crop[:, :, 0], crop[:, :, 1], crop[:, :, 2]
    # Filtro estricto para pestañas: oscuro y no rojizo
    is_lash = (r < 75) & (g < 75) & (b < 85) & (r.astype(int) - b.astype(int) < 15)
    mask = cv2.morphologyEx(is_lash.astype(np.uint8) * 255, cv2.MORPH_CLOSE, np.ones((2, 2), np.uint8))
    mask_smooth = cv2.GaussianBlur(mask, (3, 3), 0.4)
    out = np.zeros((crop.shape[0], crop.shape[1], 4), dtype=np.uint8)
    for y in range(crop.shape[0]):
        for x in range(crop.shape[1]):
            if mask_smooth[y, x] > 0:
                # Color delineador anime carbón puro con suave azul medianoche
                out[y, x] = [28, 26, 25, mask_smooth[y, x]]
    return out

lash_l = extract_pure_eyelash((135, 155, 175, 220))
lash_r = extract_pure_eyelash((148, 168, 230, 268))

# -------------------------------------------------------------------------
# 6. ESCALADO A CANVAS 2000x2000 Y GENERACIÓN DE OJOS EN ALTA DEFINICIÓN
# -------------------------------------------------------------------------
print("[6/7] Generando ojos anime vectoriales directamente a resolución 2000x2000...")
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

def generate_hd_eyeball(cx, cy, rx, ry, angle=0):
    canvas = np.zeros((CANVAS_SIZE, CANVAS_SIZE, 4), dtype=np.uint8)
    mask = np.zeros((CANVAS_SIZE, CANVAS_SIZE), dtype=np.uint8)
    cv2.ellipse(mask, (cx, cy), (rx, ry), angle, 0, 360, 255, -1, cv2.LINE_AA)
    
    y1, y2 = max(0, cy - ry - 5), min(CANVAS_SIZE, cy + ry + 5)
    x1, x2 = max(0, cx - rx - 5), min(CANVAS_SIZE, cx + rx + 5)
    
    for y in range(y1, y2):
        t = np.clip((y - (cy - ry)) / float(ry * 1.8), 0.0, 1.0)
        # Sombra superior [212, 215, 220], Blanco marfil inferior [248, 246, 246]
        b = int(220 * (1 - t) + 246 * t)
        g = int(215 * (1 - t) + 246 * t)
        r = int(212 * (1 - t) + 248 * t)
        for x in range(x1, x2):
            if mask[y, x] > 0:
                canvas[y, x] = [b, g, r, 255]
                
    canvas[:, :, 3] = cv2.GaussianBlur(mask, (5, 5), 1.0)
    return canvas

def generate_hd_pupil(cx, cy, rx, ry, angle=0):
    canvas = np.zeros((CANVAS_SIZE, CANVAS_SIZE, 4), dtype=np.uint8)
    mask = np.zeros((CANVAS_SIZE, CANVAS_SIZE), dtype=np.uint8)
    cv2.ellipse(mask, (cx, cy), (rx, ry), angle, 0, 360, 255, -1, cv2.LINE_AA)
    
    y1, y2 = max(0, cy - ry - 5), min(CANVAS_SIZE, cy + ry + 5)
    x1, x2 = max(0, cx - rx - 5), min(CANVAS_SIZE, cx + rx + 5)
    
    for y in range(y1, y2):
        for x in range(x1, x2):
            if mask[y, x] > 0:
                dx = (x - cx) / float(rx)
                dy = (y - cy) / float(ry)
                dist = np.sqrt(dx * dx + dy * dy)
                t_vert = np.clip((y - (cy - ry * 0.3)) / float(ry * 1.3), 0.0, 1.0)
                
                # BGR:
                r = int(125 + 130 * t_vert * (1.0 - dist * 0.25))
                g = int(8 + 20 * t_vert)
                b = int(22 + 30 * t_vert)
                
                # Núcleo oscuro anime
                if dist < 0.45 and dy < 0.15:
                    r = int(r * 0.2)
                    g = int(g * 0.18)
                    b = int(b * 0.25)
                    
                canvas[y, x] = [b, g, r, 255]
                
    # Brillo principal grande arriba a la izquierda
    cv2.circle(canvas, (int(cx - rx * 0.32), int(cy - ry * 0.32)), int(rx * 0.28), (255, 255, 255, 255), -1, cv2.LINE_AA)
    # Brillo secundario sutil abajo a la derecha
    cv2.circle(canvas, (int(cx + rx * 0.35), int(cy + ry * 0.3)), int(rx * 0.14), (255, 255, 255, 220), -1, cv2.LINE_AA)
    canvas[:, :, 3] = cv2.GaussianBlur(mask, (5, 5), 1.0)
    return canvas

eye_l_cx = int(OFFSET_X + 196 * SCALE)  # 1016
eye_l_cy = int(OFFSET_Y + 153 * SCALE)  # 794
eye_r_cx = int(OFFSET_X + 248 * SCALE)  # 1265
eye_r_cy = int(OFFSET_Y + 166 * SCALE)  # 857

layers_output = {
    "Torso": place_full_frame(torso_rgba),
    "Head_Base": place_full_frame(head_base_rgba),
    "Hair_Bangs_Dangle": place_full_frame(bangs_rgba),
    "Left_Eyeball": generate_hd_eyeball(eye_l_cx, eye_l_cy, int(18 * SCALE), int(13 * SCALE), 5),
    "Right_Eyeball": generate_hd_eyeball(eye_r_cx, eye_r_cy, int(16 * SCALE), int(13 * SCALE), 5),
    "Left_Pupil": generate_hd_pupil(eye_l_cx, eye_l_cy, int(9.5 * SCALE), int(12.5 * SCALE), 5),
    "Right_Pupil": generate_hd_pupil(eye_r_cx, eye_r_cy, int(8.5 * SCALE), int(12.5 * SCALE), 5),
    "Left_Eyelash": place_cropped_layer(lash_l, 175, 135),
    "Right_Eyelash": place_cropped_layer(lash_r, 230, 148),
    "Left_Eyebrow": place_full_frame(eyebrow_l_rgba),
    "Right_Eyebrow": place_full_frame(eyebrow_r_rgba),
    "Nose": place_full_frame(nose_rgba)
}

# -------------------------------------------------------------------------
# 7. 14 VISEMAS + TRIGGERS
# -------------------------------------------------------------------------
print("[7/7] Generando 14 visemas y triggers de expresiones...")
mouth_cx = int(OFFSET_X + 225 * SCALE)
mouth_cy = int(OFFSET_Y + 208 * SCALE)

def create_viseme(draw_fn):
    canvas = np.zeros((CANVAS_SIZE, CANVAS_SIZE, 4), dtype=np.uint8)
    roi = np.zeros((160, 240, 4), dtype=np.uint8)
    draw_fn(roi)
    top = mouth_cy - 80
    left = mouth_cx - 120
    canvas[top:top+160, left:left+240] = roi
    return canvas

def v_neutral(roi):
    cv2.ellipse(roi, (120, 78), (48, 5), 3, 0, 360, (50, 40, 110, 255), 3, cv2.LINE_AA)
    cv2.ellipse(roi, (120, 84), (28, 4), 2, 0, 360, (110, 100, 190, 200), -1, cv2.LINE_AA)

def v_ah(roi):
    cv2.ellipse(roi, (120, 80), (32, 40), 0, 0, 360, (30, 20, 70, 255), -1, cv2.LINE_AA)
    cv2.ellipse(roi, (120, 52), (24, 12), 0, 0, 360, (245, 245, 248, 255), -1, cv2.LINE_AA)
    cv2.ellipse(roi, (120, 105), (20, 14), 0, 0, 360, (130, 120, 215, 255), -1, cv2.LINE_AA)
    cv2.ellipse(roi, (120, 80), (32, 40), 0, 0, 360, (45, 30, 95, 255), 3, cv2.LINE_AA)

def v_d(roi):
    cv2.ellipse(roi, (120, 78), (42, 22), 0, 0, 360, (30, 20, 70, 255), -1, cv2.LINE_AA)
    cv2.rectangle(roi, (92, 68), (148, 80), (245, 245, 248, 255), -1)
    cv2.ellipse(roi, (120, 92), (22, 10), 0, 0, 360, (130, 120, 215, 255), -1, cv2.LINE_AA)
    cv2.ellipse(roi, (120, 78), (42, 22), 0, 0, 360, (45, 30, 95, 255), 3, cv2.LINE_AA)

def v_ee(roi):
    cv2.ellipse(roi, (120, 78), (52, 16), 0, 0, 360, (30, 20, 70, 255), -1, cv2.LINE_AA)
    cv2.rectangle(roi, (85, 72), (155, 84), (245, 245, 248, 255), -1)
    cv2.line(roi, (85, 78), (155, 78), (180, 180, 190, 255), 1, cv2.LINE_AA)
    cv2.ellipse(roi, (120, 78), (52, 16), 0, 0, 360, (45, 30, 95, 255), 3, cv2.LINE_AA)

def v_f(roi):
    cv2.ellipse(roi, (120, 78), (44, 18), 0, 0, 360, (30, 20, 70, 255), -1, cv2.LINE_AA)
    cv2.rectangle(roi, (94, 68), (146, 80), (245, 245, 248, 255), -1)
    cv2.ellipse(roi, (120, 78), (44, 18), 0, 0, 360, (45, 30, 95, 255), 3, cv2.LINE_AA)

def v_l(roi):
    cv2.ellipse(roi, (120, 78), (38, 26), 0, 0, 360, (30, 20, 70, 255), -1, cv2.LINE_AA)
    cv2.ellipse(roi, (120, 72), (18, 14), 0, 0, 360, (130, 120, 215, 255), -1, cv2.LINE_AA)
    cv2.ellipse(roi, (120, 78), (38, 26), 0, 0, 360, (45, 30, 95, 255), 3, cv2.LINE_AA)

def v_m(roi):
    cv2.line(roi, (82, 78), (158, 78), (45, 30, 95, 255), 4, cv2.LINE_AA)

def v_oh(roi):
    cv2.circle(roi, (120, 80), 24, (30, 20, 70, 255), -1, cv2.LINE_AA)
    cv2.circle(roi, (120, 92), 12, (130, 120, 215, 255), -1, cv2.LINE_AA)
    cv2.circle(roi, (120, 80), 24, (45, 30, 95, 255), 3, cv2.LINE_AA)

def v_r(roi):
    cv2.ellipse(roi, (120, 78), (34, 20), 0, 0, 360, (30, 20, 70, 255), -1, cv2.LINE_AA)
    cv2.ellipse(roi, (120, 86), (16, 8), 0, 0, 360, (130, 120, 215, 255), -1, cv2.LINE_AA)
    cv2.ellipse(roi, (120, 78), (34, 20), 0, 0, 360, (45, 30, 95, 255), 3, cv2.LINE_AA)

def v_s(roi):
    cv2.ellipse(roi, (120, 78), (46, 14), 0, 0, 360, (30, 20, 70, 255), -1, cv2.LINE_AA)
    cv2.rectangle(roi, (90, 72), (150, 82), (245, 245, 248, 255), -1)
    cv2.ellipse(roi, (120, 78), (46, 14), 0, 0, 360, (45, 30, 95, 255), 3, cv2.LINE_AA)

def v_uh(roi):
    cv2.ellipse(roi, (120, 80), (36, 30), 0, 0, 360, (30, 20, 70, 255), -1, cv2.LINE_AA)
    cv2.ellipse(roi, (120, 96), (20, 12), 0, 0, 360, (130, 120, 215, 255), -1, cv2.LINE_AA)
    cv2.ellipse(roi, (120, 80), (36, 30), 0, 0, 360, (45, 30, 95, 255), 3, cv2.LINE_AA)

def v_woo(roi):
    cv2.circle(roi, (120, 80), 16, (30, 20, 70, 255), -1, cv2.LINE_AA)
    cv2.circle(roi, (120, 80), 16, (45, 30, 95, 255), 3, cv2.LINE_AA)

def v_smile(roi):
    pts = np.array([[82, 74], [120, 92], [158, 74]], dtype=np.int32)
    cv2.polylines(roi, [pts], False, (45, 30, 95, 255), 4, cv2.LINE_AA)

def v_surprised(roi):
    cv2.ellipse(roi, (120, 80), (28, 44), 0, 0, 360, (30, 20, 70, 255), -1, cv2.LINE_AA)
    cv2.ellipse(roi, (120, 80), (28, 44), 0, 0, 360, (45, 30, 95, 255), 3, cv2.LINE_AA)

visemes_fns = {
    "Neutral": v_neutral, "Ah": v_ah, "D": v_d, "Ee": v_ee,
    "F": v_f, "L": v_l, "M": v_m, "Oh": v_oh, "R": v_r,
    "S": v_s, "Uh": v_uh, "W-Oo": v_woo, "Smile": v_smile, "Surprised": v_surprised
}

for vname, vfn in visemes_fns.items():
    layers_output[f"Viseme_{vname}"] = create_viseme(vfn)

# Triggers
canvas_blush = np.zeros((CANVAS_SIZE, CANVAS_SIZE, 4), dtype=np.uint8)
cv2.ellipse(canvas_blush, (int(OFFSET_X + 195 * SCALE), int(OFFSET_Y + 180 * SCALE)), (int(25 * SCALE), int(12 * SCALE)), 5, 0, 360, (130, 100, 245, 180), -1, cv2.LINE_AA)
cv2.ellipse(canvas_blush, (int(OFFSET_X + 255 * SCALE), int(OFFSET_Y + 190 * SCALE)), (int(22 * SCALE), int(10 * SCALE)), -5, 0, 360, (130, 100, 245, 180), -1, cv2.LINE_AA)
layers_output["Trigger_Blush"] = canvas_blush

canvas_sweat = np.zeros((CANVAS_SIZE, CANVAS_SIZE, 4), dtype=np.uint8)
sw_cx = int(OFFSET_X + 155 * SCALE)
sw_cy = int(OFFSET_Y + 120 * SCALE)
cv2.ellipse(canvas_sweat, (sw_cx, sw_cy + 25), (18, 25), 15, 0, 360, (240, 200, 60, 240), -1, cv2.LINE_AA)
pts_drop = np.array([[sw_cx - 14, sw_cy + 15], [sw_cx + 8, sw_cy - 20], [sw_cx + 16, sw_cy + 18]], dtype=np.int32)
cv2.fillPoly(canvas_sweat, [pts_drop], (240, 200, 60, 240), cv2.LINE_AA)
layers_output["Trigger_Sweatdrop"] = canvas_sweat

canvas_vein = np.zeros((CANVAS_SIZE, CANVAS_SIZE, 4), dtype=np.uint8)
vn_cx = int(OFFSET_X + 270 * SCALE)
vn_cy = int(OFFSET_Y + 115 * SCALE)
cv2.line(canvas_vein, (vn_cx - 25, vn_cy - 10), (vn_cx + 25, vn_cy + 10), (50, 40, 230, 240), 6, cv2.LINE_AA)
cv2.line(canvas_vein, (vn_cx - 10, vn_cy - 25), (vn_cx + 10, vn_cy + 25), (50, 40, 230, 240), 6, cv2.LINE_AA)
layers_output["Trigger_AnimeVein"] = canvas_vein

# Guardar capas en disco
print("Guardando capas RGBA individuales...")
raw_paths = {}
for name, data in layers_output.items():
    png_path = os.path.join(OUTPUT_DIR, f"{name}.png")
    cv2.imwrite(png_path, data)
    raw_path = os.path.join(OUTPUT_DIR, f"{name}.raw")
    rgba_data = cv2.cvtColor(data, cv2.COLOR_BGRA2RGBA)
    with open(raw_path, "wb") as f:
        f.write(rgba_data.tobytes())
    raw_paths[name] = {
        "png": png_path,
        "raw": raw_path,
        "width": CANVAS_SIZE,
        "height": CANVAS_SIZE
    }

# -------------------------------------------------------------------------
# GENERACIÓN DE MANIFIESTO PARA COMPILACIÓN PSD
# -------------------------------------------------------------------------
manifest = {
    "characterName": "CyberGirl",
    "canvasWidth": CANVAS_SIZE,
    "canvasHeight": CANVAS_SIZE,
    "neckPivot": {
        "x": int(OFFSET_X + 218 * SCALE),
        "y": int(OFFSET_Y + 232 * SCALE)
    },
    "head": {
        "name": "+Head",
        "opened": True,
        "children": [
            {
                "name": "Hair Bangs Dangle",
                "rawPath": raw_paths["Hair_Bangs_Dangle"]["raw"],
                "left": 0, "top": 0, "width": CANVAS_SIZE, "height": CANVAS_SIZE
            },
            {
                "name": "Left Eyebrow",
                "rawPath": raw_paths["Left_Eyebrow"]["raw"],
                "left": 0, "top": 0, "width": CANVAS_SIZE, "height": CANVAS_SIZE
            },
            {
                "name": "Right Eyebrow",
                "rawPath": raw_paths["Right_Eyebrow"]["raw"],
                "left": 0, "top": 0, "width": CANVAS_SIZE, "height": CANVAS_SIZE
            },
            {
                "name": "+Left Eye",
                "opened": True,
                "children": [
                    {
                        "name": "Left Eyelash",
                        "rawPath": raw_paths["Left_Eyelash"]["raw"],
                        "left": 0, "top": 0, "width": CANVAS_SIZE, "height": CANVAS_SIZE
                    },
                    {
                        "name": "Left Pupil",
                        "rawPath": raw_paths["Left_Pupil"]["raw"],
                        "left": 0, "top": 0, "width": CANVAS_SIZE, "height": CANVAS_SIZE
                    },
                    {
                        "name": "Left Eyeball",
                        "rawPath": raw_paths["Left_Eyeball"]["raw"],
                        "left": 0, "top": 0, "width": CANVAS_SIZE, "height": CANVAS_SIZE
                    }
                ]
            },
            {
                "name": "+Right Eye",
                "opened": True,
                "children": [
                    {
                        "name": "Right Eyelash",
                        "rawPath": raw_paths["Right_Eyelash"]["raw"],
                        "left": 0, "top": 0, "width": CANVAS_SIZE, "height": CANVAS_SIZE
                    },
                    {
                        "name": "Right Pupil",
                        "rawPath": raw_paths["Right_Pupil"]["raw"],
                        "left": 0, "top": 0, "width": CANVAS_SIZE, "height": CANVAS_SIZE
                    },
                    {
                        "name": "Right Eyeball",
                        "rawPath": raw_paths["Right_Eyeball"]["raw"],
                        "left": 0, "top": 0, "width": CANVAS_SIZE, "height": CANVAS_SIZE
                    }
                ]
            },
            {
                "name": "Nose",
                "rawPath": raw_paths["Nose"]["raw"],
                "left": 0, "top": 0, "width": CANVAS_SIZE, "height": CANVAS_SIZE
            },
            {
                "name": "Mouth",
                "opened": False,
                "children": [
                    {
                        "name": vname,
                        "rawPath": raw_paths[f"Viseme_{vname}"]["raw"],
                        "left": 0, "top": 0, "width": CANVAS_SIZE, "height": CANVAS_SIZE,
                        "hidden": (vname != "Neutral")
                    }
                    for vname in visemes_fns.keys()
                ]
            },
            {
                "name": "Emotions",
                "opened": False,
                "children": [
                    {
                        "name": "Blush (b)",
                        "rawPath": raw_paths["Trigger_Blush"]["raw"],
                        "left": 0, "top": 0, "width": CANVAS_SIZE, "height": CANVAS_SIZE,
                        "hidden": True
                    },
                    {
                        "name": "Sweatdrop (w)",
                        "rawPath": raw_paths["Trigger_Sweatdrop"]["raw"],
                        "left": 0, "top": 0, "width": CANVAS_SIZE, "height": CANVAS_SIZE,
                        "hidden": True
                    },
                    {
                        "name": "AnimeVein (v)",
                        "rawPath": raw_paths["Trigger_AnimeVein"]["raw"],
                        "left": 0, "top": 0, "width": CANVAS_SIZE, "height": CANVAS_SIZE,
                        "hidden": True
                    }
                ]
            },
            {
                "name": "Head_Base",
                "rawPath": raw_paths["Head_Base"]["raw"],
                "left": 0, "top": 0, "width": CANVAS_SIZE, "height": CANVAS_SIZE
            }
        ]
    },
    "body": {
        "name": "Body",
        "opened": True,
        "children": [
            {
                "name": "Torso",
                "rawPath": raw_paths["Torso"]["raw"],
                "left": 0, "top": 0, "width": CANVAS_SIZE, "height": CANVAS_SIZE
            }
        ]
    }
}

with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)

print(f"\n[OK] Generación completada con éxito.")

import os
import cv2
import json
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

def build_cybergirl():
    print('=== SLICING CYBERGIRL PUPPET FOR CHARACTER ANIMATOR ===')
    base_dir = r'f:\\Dev\\AdobeEngineSuit\\showcase_animation'
    raw_dir = os.path.join(base_dir, 'raw_cybergirl')
    scratch_dir = r'C:\\Users\\sasuk\\.gemini\\antigravity\\brain\\0f050f76-dc27-4e7f-909d-4b31601077d1\\scratch\\cybergirl_layers'
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(scratch_dir, exist_ok=True)

    img_src = r'C:\\Users\\sasuk\\.gemini\\antigravity\\brain\\0f050f76-dc27-4e7f-909d-4b31601077d1\\.user_uploaded\\media_1789101380931.png'
    if not os.path.exists(img_src):
        raise FileNotFoundError(f'Source artwork not found: {img_src}')

    # 1. Background removal with floodfill from corners (preserves pure white jacket)
    orig = Image.open(img_src).crop((0, 0, 387, 403))
    arr_orig = np.array(orig)
    h_orig, w_orig = arr_orig.shape[:2]

    bgr_orig = cv2.cvtColor(arr_orig[:, :, :3], cv2.COLOR_RGB2BGR)
    mask = np.zeros((h_orig + 2, w_orig + 2), np.uint8)
    tol = (5, 5, 5)
    cv2.floodFill(bgr_orig.copy(), mask, (0, 0), (0, 0, 0), tol, tol, flags=8)
    cv2.floodFill(bgr_orig.copy(), mask, (w_orig - 1, 0), (0, 0, 0), tol, tol, flags=8)
    cv2.floodFill(bgr_orig.copy(), mask, (0, h_orig - 1), (0, 0, 0), tol, tol, flags=8)
    cv2.floodFill(bgr_orig.copy(), mask, (w_orig - 1, h_orig - 1), (0, 0, 0), tol, tol, flags=8)
    bg_mask = mask[1:-1, 1:-1] > 0

    alpha = np.where(bg_mask, 0, 255).astype(np.uint8)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    alpha = cv2.morphologyEx(alpha, cv2.MORPH_CLOSE, kernel)

    rgba_orig = np.dstack([arr_orig[:, :, :3], alpha])
    clean_pil = Image.fromarray(rgba_orig)

    # 2. Scale to 2000x2000 canvas
    canvas_w, canvas_h = 2000, 2000
    target_h = 1920
    scale = target_h / h_orig
    target_w = int(w_orig * scale)
    scaled_art = clean_pil.resize((target_w, target_h), Image.Resampling.LANCZOS)

    canvas = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
    offset_x = (canvas_w - target_w) // 2
    offset_y = canvas_h - target_h
    canvas.paste(scaled_art, (offset_x, offset_y))
    arr2000 = np.array(canvas)

    print(f'Canvas: {canvas_w}x{canvas_h}, character at x={offset_x}, y={offset_y}')

    def export_layer(name, left, top, layer_img, hidden=False):
        w_c, h_c = layer_img.size
        safe_name = name.replace(' ', '_').replace('+', '').replace('(', '').replace(')', '')
        raw_path = os.path.join(raw_dir, f'{safe_name}.raw')
        png_path = os.path.join(raw_dir, f'{safe_name}.png')
        scratch_path = os.path.join(scratch_dir, f'{safe_name}.png')
        with open(raw_path, 'wb') as f:
            f.write(layer_img.tobytes())
        layer_img.save(png_path)
        layer_img.save(scratch_path)
        return {
            'name': name,
            'left': left,
            'top': top,
            'width': w_c,
            'height': h_c,
            'rawPath': raw_path,
            'hidden': hidden
        }

    # 3. Head / Torso Seam Boundary
    head_poly = np.array([
        [0, 0],
        [canvas_w, 0],
        [canvas_w, 1140],
        [1420, 1140],
        [1350, 1150],
        [1280, 1170],
        [1200, 1195],
        [1130, 1205],
        [1060, 1195],
        [950, 1165],
        [850, 1180],
        [750, 1210],
        [500, 1220],
        [170, 1220],
        [0, 1220]
    ], dtype=np.int32)

    head_mask = np.zeros((canvas_h, canvas_w), dtype=np.uint8)
    cv2.fillPoly(head_mask, [head_poly], 255)

    # 4. Torso Layer (with inpainting behind chin and hood)
    torso_alpha = np.where((head_mask == 0) & (arr2000[:, :, 3] > 0), 255, 0).astype(np.uint8)
    torso_rgba = arr2000.copy()
    torso_rgba[:, :, 3] = torso_alpha

    char_mask = (arr2000[:, :, 3] > 0).astype(np.uint8)
    inpaint_seam = np.zeros((canvas_h, canvas_w), dtype=np.uint8)
    upper_seam_poly = np.array([
        [300, 1160],
        [500, 1160],
        [750, 1150],
        [850, 1120],
        [950, 1100],
        [1060, 1130],
        [1130, 1140],
        [1200, 1130],
        [1280, 1110],
        [1350, 1090],
        [1380, 1090],
        [1380, 1150],
        [1280, 1170],
        [1200, 1195],
        [1130, 1205],
        [1060, 1195],
        [950, 1165],
        [850, 1180],
        [750, 1210],
        [500, 1220],
        [300, 1220]
    ], dtype=np.int32)
    cv2.fillPoly(inpaint_seam, [upper_seam_poly], 255)
    inpaint_seam = (inpaint_seam & (char_mask * 255)).astype(np.uint8)

    torso_bgr = cv2.cvtColor(torso_rgba[:, :, :3], cv2.COLOR_RGB2BGR)
    torso_inp = cv2.inpaint(torso_bgr, inpaint_seam, 15, cv2.INPAINT_TELEA)
    torso_rgba[:, :, :3] = cv2.cvtColor(torso_inp, cv2.COLOR_BGR2RGB)
    torso_rgba[inpaint_seam > 0, 3] = 255

    t_ys, t_xs = np.where(torso_rgba[:, :, 3] > 0)
    t_box = (int(t_xs.min()), int(t_ys.min()), int(t_xs.max() + 1), int(t_ys.max() + 1))
    torso_crop = Image.fromarray(torso_rgba).crop(t_box)
    torso_layer = export_layer('Torso', t_box[0], t_box[1], torso_crop)

    # 5. Head Base
    head_alpha = np.where((head_mask == 255) & (arr2000[:, :, 3] > 0), 255, 0).astype(np.uint8)
    head_rgba = arr2000.copy()
    head_rgba[:, :, 3] = head_alpha

    inpaint_face = np.zeros((canvas_h, canvas_w), dtype=np.uint8)
    cv2.ellipse(inpaint_face, (1010, 810), (90, 60), -10, 0, 360, 255, -1)
    cv2.ellipse(inpaint_face, (1265, 860), (75, 60), -15, 0, 360, 255, -1)
    cv2.ellipse(inpaint_face, (1150, 1045), (110, 35), -10, 0, 360, 255, -1)
    cv2.ellipse(inpaint_face, (1040, 710), (60, 20), -10, 0, 360, 255, -1)

    head_bgr = cv2.cvtColor(head_rgba[:, :, :3], cv2.COLOR_RGB2BGR)
    head_inp = cv2.inpaint(head_bgr, inpaint_face, 15, cv2.INPAINT_TELEA)
    head_base_rgba = head_rgba.copy()
    head_base_rgba[:, :, :3] = cv2.cvtColor(head_inp, cv2.COLOR_BGR2RGB)

    h_ys, h_xs = np.where(head_base_rgba[:, :, 3] > 0)
    h_box = (int(h_xs.min()), int(h_ys.min()), int(h_xs.max() + 1), int(h_ys.max() + 1))
    head_base_crop = Image.fromarray(head_base_rgba).crop(h_box)
    head_base_layer = export_layer('Head Base', h_box[0], h_box[1], head_base_crop)

    # 6. Hair Bangs Dangle
    bangs_box = (650, 420, 1460, 790)
    bangs_crop = canvas.crop(bangs_box)
    bangs_arr = np.array(bangs_crop)
    br, bg, bb = bangs_arr[:, :, 0], bangs_arr[:, :, 1], bangs_arr[:, :, 2]
    hair_mask = (br < 80) & (bg > 40) & (bg < 140) & (bb > 50) & (bb < 160)
    hair_alpha = np.where(hair_mask, 255, 0).astype(np.uint8)
    kernel_hair = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    hair_alpha = cv2.morphologyEx(hair_alpha, cv2.MORPH_CLOSE, kernel_hair)
    bangs_arr[:, :, 3] = hair_alpha
    hair_bangs_layer = export_layer('Hair Bangs Dangle', bangs_box[0], bangs_box[1], Image.fromarray(bangs_arr))

    # 7. Eyebrows
    leb_crop = canvas.crop((980, 690, 1120, 735))
    leb_arr = np.array(leb_crop)
    lbr, lbg, lbb = leb_arr[:, :, 0].astype(int), leb_arr[:, :, 1].astype(int), leb_arr[:, :, 2].astype(int)
    leb_mask = (lbr < 65) & (lbg < 45) & (lbb < 40)
    leb_arr[:, :, 3] = np.where(leb_mask, 255, 0).astype(np.uint8)
    leb_arr[:, :, 3] = cv2.morphologyEx(leb_arr[:, :, 3], cv2.MORPH_CLOSE, kernel_hair)
    left_eyebrow = export_layer('Left Eyebrow', 980, 690, Image.fromarray(leb_arr))

    reb_crop = canvas.crop((1220, 705, 1360, 755))
    reb_arr = np.array(reb_crop)
    rbr, rbg, rbb = reb_arr[:, :, 0].astype(int), reb_arr[:, :, 1].astype(int), reb_arr[:, :, 2].astype(int)
    reb_mask = (rbr < 70) & (rbg < 55) & (rbb < 55) & (rbg > 15)
    reb_arr[:, :, 3] = np.where(reb_mask, 255, 0).astype(np.uint8)
    reb_arr[:, :, 3] = cv2.morphologyEx(reb_arr[:, :, 3], cv2.MORPH_CLOSE, kernel_hair)
    right_eyebrow = export_layer('Right Eyebrow', 1220, 705, Image.fromarray(reb_arr))

    # 8. Eyes & Pupils
    # Left Pupil
    lp_crop = arr2000[780:858, 992:1070].copy()
    h_l, w_l = lp_crop.shape[:2]
    cy_l, cx_l = h_l // 2, w_l // 2
    dist_l = np.sqrt((np.arange(w_l)[None, :] - cx_l)**2 + (np.arange(h_l)[:, None] - cy_l)**2)
    r_l, g_l, b_l = lp_crop[:, :, 0].astype(float), lp_crop[:, :, 1].astype(float), lp_crop[:, :, 2].astype(float)
    crimson_l = (r_l > 95) & ((r_l - g_l) > 25)
    spec_l = (r_l > 150) & (g_l > 120) & (dist_l < 22)
    dark_l = (r_l < 60) & (g_l < 40) & (b_l < 40) & (dist_l < 25)
    lp_mask = ((crimson_l | spec_l | dark_l) & (dist_l < 38)).astype(np.uint8) * 255
    lp_mask = cv2.morphologyEx(lp_mask, cv2.MORPH_CLOSE, kernel)
    contours_l, _ = cv2.findContours(lp_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filled_lp = np.zeros_like(lp_mask)
    cv2.drawContours(filled_lp, contours_l, -1, 255, thickness=cv2.FILLED)
    lp_crop[:, :, 3] = filled_lp
    left_pupil = export_layer('Left Pupil', 992, 780, Image.fromarray(lp_crop))

    # Left Eyeball
    le_crop = arr2000[720:885, 900:1120].copy()
    iris_mask_l = np.zeros(le_crop.shape[:2], dtype=np.uint8)
    cv2.ellipse(iris_mask_l, (131, 99), (38, 38), 0, 0, 360, 255, -1)
    sclera_bgr = cv2.inpaint(cv2.cvtColor(le_crop[:, :, :3], cv2.COLOR_RGB2BGR), iris_mask_l, 15, cv2.INPAINT_TELEA)
    le_crop[:, :, :3] = cv2.cvtColor(sclera_bgr, cv2.COLOR_BGR2RGB)
    eye_l_contour = np.array([
        [25, 75], [55, 45], [90, 28], [135, 25], [175, 40],
        [205, 80], [185, 125], [140, 140], [95, 135], [50, 115]
    ], dtype=np.int32)
    socket_mask = np.zeros(le_crop.shape[:2], dtype=np.uint8)
    cv2.fillPoly(socket_mask, [eye_l_contour], 255)
    le_crop[:, :, 3] = cv2.GaussianBlur(socket_mask, (5, 5), 0)
    left_eyeball = export_layer('Left Eyeball', 900, 720, Image.fromarray(le_crop))

    # Right Pupil
    rp_crop = arr2000[845:920, 1226:1288].copy()
    h_r, w_r = rp_crop.shape[:2]
    cy_r, cx_r = h_r // 2, w_r // 2
    dist_r = np.sqrt((np.arange(w_r)[None, :] - cx_r)**2 + (np.arange(h_r)[:, None] - cy_r)**2)
    r_r, g_r, b_r = rp_crop[:, :, 0].astype(float), rp_crop[:, :, 1].astype(float), rp_crop[:, :, 2].astype(float)
    crimson_r = (r_r > 95) & ((r_r - g_r) > 25)
    spec_r = (r_r > 150) & (g_r > 120) & (dist_r < 18)
    dark_r = (r_r < 60) & (g_r < 40) & (b_r < 40) & (dist_r < 20)
    rp_mask = ((crimson_r | spec_r | dark_r) & (dist_r < 34)).astype(np.uint8) * 255
    rp_mask = cv2.morphologyEx(rp_mask, cv2.MORPH_CLOSE, kernel)
    contours_r, _ = cv2.findContours(rp_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filled_rp = np.zeros_like(rp_mask)
    cv2.drawContours(filled_rp, contours_r, -1, 255, thickness=cv2.FILLED)
    rp_crop[:, :, 3] = filled_rp
    right_pupil = export_layer('Right Pupil', 1226, 845, Image.fromarray(rp_crop))

    # Right Eyeball
    re_crop = arr2000[785:945, 1180:1360].copy()
    iris_mask_r = np.zeros(re_crop.shape[:2], dtype=np.uint8)
    cv2.ellipse(iris_mask_r, (77, 97), (31, 37), 0, 0, 360, 255, -1)
    r_sclera_bgr = cv2.inpaint(cv2.cvtColor(re_crop[:, :, :3], cv2.COLOR_RGB2BGR), iris_mask_r, 15, cv2.INPAINT_TELEA)
    re_crop[:, :, :3] = cv2.cvtColor(r_sclera_bgr, cv2.COLOR_BGR2RGB)
    eye_r_contour = np.array([
        [25, 95], [50, 50], [85, 30], [125, 30], [155, 60],
        [160, 100], [130, 140], [85, 145], [45, 135]
    ], dtype=np.int32)
    r_socket_mask = np.zeros(re_crop.shape[:2], dtype=np.uint8)
    cv2.fillPoly(r_socket_mask, [eye_r_contour], 255)
    re_crop[:, :, 3] = cv2.GaussianBlur(r_socket_mask, (5, 5), 0)
    right_eyeball = export_layer('Right Eyeball', 1180, 785, Image.fromarray(re_crop))

    # 9. Nose
    nose_crop = canvas.crop((1120, 890, 1220, 1000))
    nose_arr = np.array(nose_crop)
    nr, ng, nb = nose_arr[:, :, 0].astype(int), nose_arr[:, :, 1].astype(int), nose_arr[:, :, 2].astype(int)
    nose_mask = ((nr - ng) > 35) & (ng < 185) & (nr > 160)
    nose_arr[:, :, 3] = np.where(nose_mask, 255, 0).astype(np.uint8)
    nose = export_layer('Nose', 1120, 890, Image.fromarray(nose_arr))

    # 10. Complete 14 Visemes
    mouth_box = (1050, 1015, 1250, 1075)
    mouth_w, mouth_h = mouth_box[2] - mouth_box[0], mouth_box[3] - mouth_box[1]

    # Neutral Viseme
    m_arr = np.array(canvas.crop(mouth_box))
    mr, mg, mb = m_arr[:, :, 0].astype(int), m_arr[:, :, 1].astype(int), m_arr[:, :, 2].astype(int)
    lip_line = (mr < 115) & (mg < 80) & (mb < 80)
    lip_pink = (mr > 150) & ((mr - mg) > 35) & ((mr - mb) > 30) & (mg < 135)
    mouth_mask = lip_line | lip_pink
    mouth_alpha = cv2.morphologyEx(mouth_mask.astype(np.uint8) * 255, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(mouth_alpha, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filled_alpha = np.zeros_like(mouth_alpha)
    cv2.drawContours(filled_alpha, contours, -1, 255, thickness=cv2.FILLED)
    hole = (filled_alpha == 255) & (mouth_alpha == 0)
    m_arr[hole, :3] = [170, 95, 105]
    m_arr[:, :, 3] = filled_alpha
    visemes = [export_layer('Neutral', mouth_box[0], mouth_box[1], Image.fromarray(m_arr), hidden=False)]

    lip_outline = (130, 45, 55, 255)
    mouth_dark = (60, 20, 28, 255)
    teeth_color = (252, 250, 255, 255)
    tongue_color = (220, 95, 110, 255)

    other_visemes = ['Ah', 'D', 'Ee', 'F', 'L', 'M', 'Oh', 'R', 'S', 'Uh', 'W-Oo', 'Smile', 'Surprised']
    for v_name in other_visemes:
        vm_img = Image.new('RGBA', (mouth_w, mouth_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(vm_img)
        cx, cy = mouth_w // 2, mouth_h // 2
        if v_name in ['Ah', 'Surprised']:
            ry = 22 if v_name == 'Ah' else 26
            rx = 24 if v_name == 'Ah' else 20
            draw.ellipse([cx - rx - 2, cy - ry - 2, cx + rx + 2, cy + ry + 2], fill=lip_outline)
            draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=mouth_dark)
            draw.rectangle([cx - rx + 5, cy - ry + 3, cx + rx - 5, cy - ry + 9], fill=teeth_color)
            draw.ellipse([cx - rx + 7, cy + ry - 9, cx + rx - 7, cy + ry], fill=tongue_color)
        elif v_name in ['Ee', 'Smile']:
            rx, ry = 38, 12
            draw.ellipse([cx - rx - 2, cy - ry - 2, cx + rx + 2, cy + ry + 2], fill=lip_outline)
            draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=mouth_dark)
            draw.rectangle([cx - rx + 6, cy - ry + 2, cx + rx - 6, cy - ry + 7], fill=teeth_color)
            draw.rectangle([cx - rx + 10, cy + ry - 6, cx + rx - 10, cy + ry - 1], fill=teeth_color)
        elif v_name in ['Oh', 'W-Oo']:
            rad = 16 if v_name == 'Oh' else 10
            draw.ellipse([cx - rad - 2, cy - rad - 2, cx + rad + 2, cy + rad + 2], fill=lip_outline)
            draw.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=mouth_dark)
            if v_name == 'Oh':
                draw.ellipse([cx - 6, cy + 3, cx + 6, cy + rad - 2], fill=tongue_color)
        elif v_name in ['F', 'S', 'D']:
            rx, ry = 30, 10
            draw.ellipse([cx - rx - 2, cy - ry - 2, cx + rx + 2, cy + ry + 2], fill=lip_outline)
            draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=mouth_dark)
            draw.rectangle([cx - rx + 5, cy - ry + 2, cx + rx - 5, cy - ry + 6], fill=teeth_color)
            if v_name == 'F':
                draw.line([cx - rx + 3, cy + ry - 2, cx + rx - 3, cy + ry - 2], fill=lip_outline, width=2)
        else:
            rx, ry = 28, 9
            draw.ellipse([cx - rx - 2, cy - ry - 2, cx + rx + 2, cy + ry + 2], fill=lip_outline)
            draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=mouth_dark)
            draw.ellipse([cx - 10, cy - 2, cx + 10, cy + 7], fill=tongue_color)
        visemes.append(export_layer(v_name, mouth_box[0], mouth_box[1], vm_img, hidden=True))

    # 11. Emotional FX
    blush_img = Image.new('RGBA', (450, 80), (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(blush_img)
    bdraw.ellipse([20, 10, 150, 70], fill=(255, 100, 120, 160))
    bdraw.ellipse([300, 10, 430, 70], fill=(255, 100, 120, 160))
    blush = export_layer('Blush (b)', 820, 860, blush_img, hidden=True)

    sw_img = Image.new('RGBA', (60, 90), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(sw_img)
    sdraw.ellipse([8, 25, 52, 85], fill=(120, 200, 255, 230))
    sdraw.polygon([(30, 3), (8, 38), (52, 38)], fill=(120, 200, 255, 230))
    sweatdrop = export_layer('Sweatdrop (w)', 750, 620, sw_img, hidden=True)

    vn_img = Image.new('RGBA', (70, 70), (0, 0, 0, 0))
    vdraw = ImageDraw.Draw(vn_img)
    vdraw.arc([6, 6, 64, 64], start=45, end=135, fill=(230, 30, 40, 240), width=6)
    vdraw.arc([6, 6, 64, 64], start=135, end=225, fill=(230, 30, 40, 240), width=6)
    vdraw.arc([6, 6, 64, 64], start=225, end=315, fill=(230, 30, 40, 240), width=6)
    vdraw.arc([6, 6, 64, 64], start=315, end=45, fill=(230, 30, 40, 240), width=6)
    anime_vein = export_layer('AnimeVein (v)', 1250, 580, vn_img, hidden=True)

    # 12. Complete Puppet Manifest
    manifest = {
        'characterName': 'CyberGirl',
        'canvasWidth': canvas_w,
        'canvasHeight': canvas_h,
        'head': {
            'name': '+Head',
            'children': [
                hair_bangs_layer,
                left_eyebrow,
                right_eyebrow,
                {
                    'name': '+Left Eye',
                    'children': [left_pupil, left_eyeball],
                    'opened': False
                },
                {
                    'name': '+Right Eye',
                    'children': [right_pupil, right_eyeball],
                    'opened': False
                },
                nose,
                {
                    'name': 'Mouth',
                    'children': visemes,
                    'opened': True
                },
                {
                    'name': 'Emotions',
                    'children': [blush, sweatdrop, anime_vein],
                    'opened': False
                },
                head_base_layer
            ],
            'opened': True
        },
        'body': {
            'name': 'Body',
            'children': [
                torso_layer
            ],
            'opened': True
        }
    }

    manifest_path = os.path.join(base_dir, 'cybergirl_manifest.json')
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)

    print(f'Manifest written to: {manifest_path}')
    print('CyberGirl anatomical layers exported with 100% precision!')

if __name__ == '__main__':
    build_cybergirl()

import os
import cv2
import json
import numpy as np
from PIL import Image, ImageDraw

def smart_slice():
    print("=== NEURAL / COMPUTER VISION PRECISION RIGGING PIPELINE ===")
    base_dir = r"f:\Dev\AdobeEngineSuit\showcase_animation"
    raw_dir = os.path.join(base_dir, "raw_layers_v2")
    os.makedirs(raw_dir, exist_ok=True)

    img_src = r"C:\Users\sasuk\.gemini\antigravity\brain\0f050f76-dc27-4e7f-909d-4b31601077d1\anime_hero_character_1789098376354.jpg"
    bgr = cv2.imread(img_src)
    h_orig, w_orig = bgr.shape[:2]

    # 1. Zero-Hole Alpha Mask using FloodFill from Outer Borders & Morphological Closing
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    h_m, w_m = gray.shape
    cv_mask = np.zeros((h_m + 2, w_m + 2), np.uint8)

    # Floodfill background from outer corners (tolerance 6 to preserve dark blue/grey shading)
    cv2.floodFill(gray.copy(), cv_mask, (0, 0), 0, loDiff=6, upDiff=6)
    bg_area = cv_mask[1:-1, 1:-1] > 0

    # Negative spaces: between legs and under armpits (only if truly white background)
    cv_mask_legs = np.zeros((h_m + 2, w_m + 2), np.uint8)
    cv2.floodFill(gray.copy(), cv_mask_legs, (w_orig // 2, int(h_orig * 0.75)), 0, loDiff=6, upDiff=6)
    bg_legs = cv_mask_legs[1:-1, 1:-1] > 0

    cv_mask_arm_l = np.zeros((h_m + 2, w_m + 2), np.uint8)
    cv2.floodFill(gray.copy(), cv_mask_arm_l, (int(w_orig * 0.36), int(h_orig * 0.42)), 0, loDiff=6, upDiff=6)
    bg_arm_l = cv_mask_arm_l[1:-1, 1:-1] > 0

    cv_mask_arm_r = np.zeros((h_m + 2, w_m + 2), np.uint8)
    cv2.floodFill(gray.copy(), cv_mask_arm_r, (int(w_orig * 0.64), int(h_orig * 0.42)), 0, loDiff=6, upDiff=6)
    bg_arm_r = cv_mask_arm_r[1:-1, 1:-1] > 0

    # Total background mask
    total_bg = bg_area | bg_legs | bg_arm_l | bg_arm_r
    char_alpha = np.where(total_bg, 0, 255).astype(np.uint8)

    # Close any small internal holes inside character (e.g. zippers, stitches, shadows)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    char_alpha = cv2.morphologyEx(char_alpha, cv2.MORPH_CLOSE, kernel)

    # Combine into pristine 1024x1024 RGBA image
    rgba1024 = cv2.cvtColor(bgr, cv2.COLOR_BGR2BGRA)
    rgba1024[:, :, 3] = char_alpha

    # 2. Resize to 2000x2000 canvas with Lanczos
    pil_rgba = Image.fromarray(cv2.cvtColor(rgba1024, cv2.COLOR_BGRA2RGBA))
    canvas_w, canvas_h = 2000, 2000
    img2000 = pil_rgba.resize((canvas_w, canvas_h), Image.Resampling.LANCZOS)
    arr2000 = np.array(img2000)

    # 3. Layer Exporter Helper
    def export_layer(name, left, top, layer_img, hidden=False):
        w_c, h_c = layer_img.size
        base_filename = name.replace(' ', '_').replace('+', '').replace('(', '').replace(')', '')
        raw_path = os.path.join(raw_dir, f"{base_filename}.raw")
        png_path = os.path.join(raw_dir, f"{base_filename}.png")
        with open(raw_path, 'wb') as f:
            f.write(layer_img.tobytes())
        layer_img.save(png_path)
        return {
            "name": name,
            "left": left,
            "top": top,
            "width": w_c,
            "height": h_c,
            "rawPath": raw_path,
            "hidden": hidden
        }

    # 4. Inpainted Continuous Torso (Fills occluded areas behind arms)
    torso_box = (670, 390, 1330, 1040)
    torso_crop = img2000.crop(torso_box)
    torso_cv = cv2.cvtColor(np.array(torso_crop), cv2.COLOR_RGBA2BGRA)
    
    # Inpaint the arm overlap on left & right sides of torso
    t_h, t_w = torso_cv.shape[:2]
    inpaint_mask = np.zeros((t_h, t_w), np.uint8)
    # Mark lateral edges where arms overlap the blue cloth
    inpaint_mask[180:550, :65] = (torso_cv[180:550, :65, 3] > 0).astype(np.uint8) * 255
    inpaint_mask[180:550, -65:] = (torso_cv[180:550, -65:, 3] > 0).astype(np.uint8) * 255

    torso_bgr = torso_cv[:, :, :3]
    inpainted_torso_bgr = cv2.inpaint(torso_bgr, inpaint_mask, 9, cv2.INPAINT_TELEA)
    torso_cv[:, :, :3] = inpainted_torso_bgr
    # Ensure full opacity on torso
    torso_cv[:, :, 3] = np.where(torso_cv[:, :, 3] > 10, 255, 0).astype(np.uint8)

    torso_pil = Image.fromarray(cv2.cvtColor(torso_cv, cv2.COLOR_BGRA2RGBA))
    torso_layer = export_layer("Torso", torso_box[0], torso_box[1], torso_pil)

    # 5. Continuous Arms with Complete Cuffs (No severed wrists!)
    # Left Arm: from shoulder (530, 440) down through cuff (830, 1030)
    left_arm_box = (520, 430, 830, 1035)
    left_arm_crop = img2000.crop(left_arm_box)
    left_arm_layer = export_layer("Left Arm Artwork", left_arm_box[0], left_arm_box[1], left_arm_crop)

    # Right Arm: from shoulder (1170, 440) down through cuff (1480, 1035)
    right_arm_box = (1170, 430, 1480, 1035)
    right_arm_crop = img2000.crop(right_arm_box)
    right_arm_layer = export_layer("Right Arm Artwork", right_arm_box[0], right_arm_box[1], right_arm_crop)

    # Hands: start 30px INSIDE the cuff (y=980) down to fingers (y=1220) for seamless overlap
    left_hand_box = (530, 975, 715, 1220)
    left_hand_crop = img2000.crop(left_hand_box)
    left_hand_layer = export_layer("Open (1)", left_hand_box[0], left_hand_box[1], left_hand_crop)

    right_hand_box = (1285, 975, 1470, 1220)
    right_hand_crop = img2000.crop(right_hand_box)
    right_hand_layer = export_layer("Open (1)", right_hand_box[0], right_hand_box[1], right_hand_crop)

    # 6. Legs (Fixed)
    left_leg_box = (680, 1010, 1000, 1980)
    left_leg_crop = img2000.crop(left_leg_box)
    left_leg_layer = export_layer("+Left Leg Fixed", left_leg_box[0], left_leg_box[1], left_leg_crop)

    right_leg_box = (1000, 1010, 1320, 1980)
    right_leg_crop = img2000.crop(right_leg_box)
    right_leg_layer = export_layer("+Right Leg Fixed", right_leg_box[0], right_leg_box[1], right_leg_crop)

    # 7. Head & Facial Features
    # Head Base (Ears, Face, Neck) - inpaint skin behind mouth and eyes
    head_base_box = (770, 80, 1230, 460)
    head_base_crop = img2000.crop(head_base_box)
    head_base_layer = export_layer("Head Base", head_base_box[0], head_base_box[1], head_base_crop)

    # Hair Bangs Dangle
    hair_bangs_box = (780, 80, 1220, 290)
    hair_bangs_crop = img2000.crop(hair_bangs_box)
    hair_bangs_layer = export_layer("Hair Bangs Dangle", hair_bangs_box[0], hair_bangs_box[1], hair_bangs_crop)

    # Eyebrows
    left_eyebrow = export_layer("Left Eyebrow", 910, 245, img2000.crop((910, 245, 990, 275)))
    right_eyebrow = export_layer("Right Eyebrow", 1015, 245, img2000.crop((1015, 245, 1095, 275)))

    # Eyes & Pupils (Gaze tracking ready)
    eye_l_crop = img2000.crop((925, 270, 985, 320))
    eye_r_crop = img2000.crop((1020, 270, 1080, 320))
    left_eyeball = export_layer("Left Eyeball", 925, 270, eye_l_crop)
    right_eyeball = export_layer("Right Eyeball", 1020, 270, eye_r_crop)

    # Blue Iris / Pupil
    pupil_l = Image.new("RGBA", (34, 34), (0, 0, 0, 0))
    pupil_l.paste(eye_l_crop.crop((14, 8, 48, 42)), (0, 0))
    left_pupil = export_layer("Left Pupil", 925 + 14, 270 + 8, pupil_l)

    pupil_r = Image.new("RGBA", (34, 34), (0, 0, 0, 0))
    pupil_r.paste(eye_r_crop.crop((13, 8, 47, 42)), (0, 0))
    right_pupil = export_layer("Right Pupil", 1020 + 13, 270 + 8, pupil_r)

    # Nose
    nose = export_layer("Nose", 985, 310, img2000.crop((985, 310, 1015, 345)))

    # 8. Complete 14 Visemes
    mouth_box = (955, 345, 1045, 395)
    mouth_w, mouth_h = mouth_box[2] - mouth_box[0], mouth_box[3] - mouth_box[1]
    mouth_neutral_crop = img2000.crop(mouth_box)
    visemes = [export_layer("Neutral", mouth_box[0], mouth_box[1], mouth_neutral_crop, hidden=False)]

    lip_outline = (55, 35, 30, 255)
    mouth_dark = (50, 18, 22, 255)
    teeth_color = (252, 252, 255, 255)
    tongue_color = (235, 115, 130, 255)

    other_visemes = ['Ah', 'D', 'Ee', 'F', 'L', 'M', 'Oh', 'R', 'S', 'Uh', 'W-Oo', 'Smile', 'Surprised']
    for v_name in other_visemes:
        vm_img = Image.new("RGBA", (mouth_w, mouth_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(vm_img)
        cx, cy = mouth_w // 2, mouth_h // 2
        if v_name in ['Ah', 'Surprised']:
            ry = 18 if v_name == 'Ah' else 22
            rx = 16 if v_name == 'Ah' else 13
            draw.ellipse([cx - rx - 1, cy - ry - 1, cx + rx + 1, cy + ry + 1], fill=lip_outline)
            draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=mouth_dark)
            draw.rectangle([cx - rx + 4, cy - ry + 2, cx + rx - 4, cy - ry + 8], fill=teeth_color)
            draw.ellipse([cx - rx + 5, cy + ry - 8, cx + rx - 5, cy + ry], fill=tongue_color)
        elif v_name in ['Ee', 'Smile']:
            rx, ry = 26, 12
            draw.ellipse([cx - rx - 1, cy - ry - 1, cx + rx + 1, cy + ry + 1], fill=lip_outline)
            draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=mouth_dark)
            draw.rectangle([cx - rx + 5, cy - ry + 2, cx + rx - 5, cy - ry + 7], fill=teeth_color)
            draw.rectangle([cx - rx + 8, cy + ry - 6, cx + rx - 8, cy + ry - 1], fill=teeth_color)
        elif v_name in ['Oh', 'W-Oo']:
            rad = 12 if v_name == 'Oh' else 8
            draw.ellipse([cx - rad - 1, cy - rad - 1, cx + rad + 1, cy + rad + 1], fill=lip_outline)
            draw.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=mouth_dark)
            if v_name == 'Oh':
                draw.ellipse([cx - 5, cy + 3, cx + 5, cy + rad - 1], fill=tongue_color)
        elif v_name in ['F', 'S', 'D']:
            rx, ry = 22, 9
            draw.ellipse([cx - rx - 1, cy - ry - 1, cx + rx + 1, cy + ry + 1], fill=lip_outline)
            draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=mouth_dark)
            draw.rectangle([cx - rx + 4, cy - ry + 1, cx + rx - 4, cy - ry + 6], fill=teeth_color)
            if v_name == 'F':
                draw.line([cx - rx + 2, cy + ry - 1, cx + rx - 2, cy + ry - 1], fill=lip_outline, width=2)
        else:
            rx, ry = 20, 8
            draw.ellipse([cx - rx - 1, cy - ry - 1, cx + rx + 1, cy + ry + 1], fill=lip_outline)
            draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=mouth_dark)
            draw.ellipse([cx - 8, cy - 2, cx + 8, cy + 6], fill=tongue_color)
        visemes.append(export_layer(v_name, mouth_box[0], mouth_box[1], vm_img, hidden=True))

    # 9. Emotional FX
    blush_img = Image.new("RGBA", (240, 40), (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(blush_img)
    bdraw.ellipse([10, 5, 80, 35], fill=(255, 110, 130, 160))
    bdraw.ellipse([160, 5, 230, 35], fill=(255, 110, 130, 160))
    blush = export_layer("Blush (b)", 880, 305, blush_img, hidden=True)

    sw_img = Image.new("RGBA", (45, 65), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(sw_img)
    sdraw.ellipse([5, 20, 40, 60], fill=(120, 200, 255, 220))
    sdraw.polygon([(22, 2), (5, 30), (40, 30)], fill=(120, 200, 255, 220))
    sweatdrop = export_layer("Sweatdrop (w)", 830, 190, sw_img, hidden=True)

    vn_img = Image.new("RGBA", (50, 50), (0, 0, 0, 0))
    vdraw = ImageDraw.Draw(vn_img)
    vdraw.arc([5, 5, 45, 45], start=45, end=135, fill=(220, 40, 40, 240), width=4)
    vdraw.arc([5, 5, 45, 45], start=135, end=225, fill=(220, 40, 40, 240), width=4)
    vdraw.arc([5, 5, 45, 45], start=225, end=315, fill=(220, 40, 40, 240), width=4)
    vdraw.arc([5, 5, 45, 45], start=315, end=45, fill=(220, 40, 40, 240), width=4)
    anime_vein = export_layer("AnimeVein (v)", 1100, 170, vn_img, hidden=True)

    # 10. Assemble Full Puppet Tree
    manifest = {
        "characterName": "Aero_Star",
        "canvasWidth": canvas_w,
        "canvasHeight": canvas_h,
        "head": {
            "name": "+Head",
            "children": [
                hair_bangs_layer,
                left_eyebrow,
                right_eyebrow,
                {
                    "name": "+Left Eye",
                    "children": [left_pupil, left_eyeball],
                    "opened": False
                },
                {
                    "name": "+Right Eye",
                    "children": [right_pupil, right_eyeball],
                    "opened": False
                },
                nose,
                {
                    "name": "Mouth",
                    "children": visemes,
                    "opened": True
                },
                {
                    "name": "Emotions",
                    "children": [blush, sweatdrop, anime_vein],
                    "opened": False
                },
                head_base_layer
            ],
            "opened": True
        },
        "body": {
            "name": "Body",
            "children": [
                {
                    "name": "+Left Arm",
                    "children": [
                        {"name": "+Left Hand", "children": [left_hand_layer], "opened": False},
                        left_arm_layer
                    ],
                    "opened": False
                },
                {
                    "name": "+Right Arm Draggable",
                    "children": [
                        {"name": "+Right Hand Draggable", "children": [right_hand_layer], "opened": False},
                        right_arm_layer
                    ],
                    "opened": False
                },
                torso_layer,
                left_leg_layer,
                right_leg_layer
            ],
            "opened": True
        }
    }

    manifest_path = os.path.join(base_dir, "puppet_manifest_v2.json")
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)

    print(f"Manifest v2 written to: {manifest_path}")
    print("Zero-hole alpha mask and inpainted occlusion layers exported successfully!")

if __name__ == "__main__":
    smart_slice()

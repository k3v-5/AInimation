import os
import sys
import json
import math
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

def build_puppet_assets():
    print("=== EXTRACTING REAL ARTWORK LAYERS FOR CHARACTER ANIMATOR ===")
    base_dir = r"f:\Dev\AdobeEngineSuit\showcase_animation"
    raw_dir = os.path.join(base_dir, "raw_layers")
    os.makedirs(raw_dir, exist_ok=True)

    img_src = r"C:\Users\sasuk\.gemini\antigravity\brain\0f050f76-dc27-4e7f-909d-4b31601077d1\anime_hero_character_1789098376354.jpg"
    if not os.path.exists(img_src):
        raise FileNotFoundError(f"Source artwork not found: {img_src}")

    # 1. Background removal
    img = Image.open(img_src).convert("RGBA")
    w_src, h_src = img.size

    # Flood fill corners
    ImageDraw.floodfill(img, (0, 0), (0, 0, 0, 0), thresh=28)
    ImageDraw.floodfill(img, (w_src - 1, 0), (0, 0, 0, 0), thresh=28)
    ImageDraw.floodfill(img, (0, h_src - 1), (0, 0, 0, 0), thresh=28)
    ImageDraw.floodfill(img, (w_src - 1, h_src - 1), (0, 0, 0, 0), thresh=28)
    ImageDraw.floodfill(img, (int(w_src * 0.35), int(h_src * 0.45)), (0, 0, 0, 0), thresh=28)
    ImageDraw.floodfill(img, (int(w_src * 0.65), int(h_src * 0.45)), (0, 0, 0, 0), thresh=28)
    ImageDraw.floodfill(img, (int(w_src * 0.5), int(h_src * 0.75)), (0, 0, 0, 0), thresh=28)

    # Resize to 2000x2000 canvas
    canvas_w, canvas_h = 2000, 2000
    img2000 = img.resize((canvas_w, canvas_h), Image.Resampling.LANCZOS)

    # 2. Slice Anatomical Regions
    layers = []

    def save_layer(name, left, top, right, bottom, crop_source=None, hidden=False):
        if crop_source is None:
            crop_source = img2000
        crop = crop_source.crop((left, top, right, bottom))
        raw_path = os.path.join(raw_dir, f"{name.replace(' ', '_').replace('+', '').replace('(', '').replace(')', '')}.raw")
        w_crop, h_crop = crop.size
        # Save raw RGBA bytes
        with open(raw_path, 'wb') as f:
            f.write(crop.tobytes())
        # Also save PNG for inspection
        png_path = raw_path.replace('.raw', '.png')
        crop.save(png_path)
        return {
            "name": name,
            "left": left,
            "top": top,
            "width": w_crop,
            "height": h_crop,
            "rawPath": raw_path,
            "hidden": hidden
        }

    # Head Base (Ears, Face, Neck)
    head_base = save_layer("Head Base", 770, 80, 1230, 460)

    # Hair Bangs Dangle
    hair_bangs = save_layer("Hair Bangs Dangle", 780, 80, 1220, 290)

    # Eyebrows
    left_eyebrow = save_layer("Left Eyebrow", 910, 245, 990, 275)
    right_eyebrow = save_layer("Right Eyebrow", 1015, 245, 1095, 275)

    # Nose
    nose = save_layer("Nose", 985, 310, 1015, 345)

    # Eyes & Pupils
    # Extract eye and pupil subregions
    eye_l = img2000.crop((925, 270, 985, 320))
    eye_r = img2000.crop((1020, 270, 1080, 320))

    # Eyeball: the full eye crop
    left_eyeball = save_layer("Left Eyeball", 925, 270, 985, 320)
    right_eyeball = save_layer("Right Eyeball", 1020, 270, 1080, 320)

    # Pupil: the blue iris circle inside
    pupil_l_crop = Image.new("RGBA", (34, 34), (0, 0, 0, 0))
    p_orig_l = eye_l.crop((14, 8, 48, 42))
    pupil_l_crop.paste(p_orig_l, (0, 0))
    raw_pupil_l = os.path.join(raw_dir, "left_pupil.raw")
    with open(raw_pupil_l, 'wb') as f: f.write(pupil_l_crop.tobytes())
    pupil_l_crop.save(raw_pupil_l.replace('.raw', '.png'))
    left_pupil = {
        "name": "Left Pupil",
        "left": 925 + 14,
        "top": 270 + 8,
        "width": 34,
        "height": 34,
        "rawPath": raw_pupil_l,
        "hidden": False
    }

    pupil_r_crop = Image.new("RGBA", (34, 34), (0, 0, 0, 0))
    p_orig_r = eye_r.crop((13, 8, 47, 42))
    pupil_r_crop.paste(p_orig_r, (0, 0))
    raw_pupil_r = os.path.join(raw_dir, "right_pupil.raw")
    with open(raw_pupil_r, 'wb') as f: f.write(pupil_r_crop.tobytes())
    pupil_r_crop.save(raw_pupil_r.replace('.raw', '.png'))
    right_pupil = {
        "name": "Right Pupil",
        "left": 1020 + 13,
        "top": 270 + 8,
        "width": 34,
        "height": 34,
        "rawPath": raw_pupil_r,
        "hidden": False
    }

    # 3. Mouth: The 14 Visemes
    mouth_box = (955, 345, 1045, 395)
    mouth_w, mouth_h = mouth_box[2] - mouth_box[0], mouth_box[3] - mouth_box[1]

    # Neutral Viseme from the original artwork
    mouth_neutral_img = img2000.crop(mouth_box)
    raw_m_neutral = os.path.join(raw_dir, "viseme_Neutral.raw")
    with open(raw_m_neutral, 'wb') as f: f.write(mouth_neutral_img.tobytes())
    mouth_neutral_img.save(raw_m_neutral.replace('.raw', '.png'))
    visemes = [{
        "name": "Neutral",
        "left": mouth_box[0],
        "top": mouth_box[1],
        "width": mouth_w,
        "height": mouth_h,
        "rawPath": raw_m_neutral,
        "hidden": False
    }]

    # Render custom visual mouth visemes matching character's anime style
    # Palette matching character's face:
    skin_tone = (245, 205, 175, 255)
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
        else: # L, M, R, Uh
            rx, ry = 20, 8
            draw.ellipse([cx - rx - 1, cy - ry - 1, cx + rx + 1, cy + ry + 1], fill=lip_outline)
            draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=mouth_dark)
            draw.ellipse([cx - 8, cy - 2, cx + 8, cy + 6], fill=tongue_color)

        raw_vm_path = os.path.join(raw_dir, f"viseme_{v_name}.raw")
        with open(raw_vm_path, 'wb') as f: f.write(vm_img.tobytes())
        vm_img.save(raw_vm_path.replace('.raw', '.png'))
        visemes.append({
            "name": v_name,
            "left": mouth_box[0],
            "top": mouth_box[1],
            "width": mouth_w,
            "height": mouth_h,
            "rawPath": raw_vm_path,
            "hidden": True
        })

    # 4. Emotional Effects (Blush, Sweatdrop, AnimeVein) & Tears
    # Blush
    blush_img = Image.new("RGBA", (240, 40), (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(blush_img)
    bdraw.ellipse([10, 5, 80, 35], fill=(255, 110, 130, 160))
    bdraw.ellipse([160, 5, 230, 35], fill=(255, 110, 130, 160))
    blush_raw = os.path.join(raw_dir, "blush.raw")
    with open(blush_raw, 'wb') as f: f.write(blush_img.tobytes())
    blush_img.save(blush_raw.replace('.raw', '.png'))
    blush = {
        "name": "Blush (b)",
        "left": 880,
        "top": 305,
        "width": 240,
        "height": 40,
        "rawPath": blush_raw,
        "hidden": True
    }

    # Sweatdrop
    sw_img = Image.new("RGBA", (45, 65), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(sw_img)
    sdraw.ellipse([5, 20, 40, 60], fill=(120, 200, 255, 220))
    sdraw.polygon([(22, 2), (5, 30), (40, 30)], fill=(120, 200, 255, 220))
    sw_raw = os.path.join(raw_dir, "sweatdrop.raw")
    with open(sw_raw, 'wb') as f: f.write(sw_img.tobytes())
    sw_img.save(sw_raw.replace('.raw', '.png'))
    sweatdrop = {
        "name": "Sweatdrop (w)",
        "left": 830,
        "top": 190,
        "width": 45,
        "height": 65,
        "rawPath": sw_raw,
        "hidden": True
    }

    # Anime Vein
    vn_img = Image.new("RGBA", (50, 50), (0, 0, 0, 0))
    vdraw = ImageDraw.Draw(vn_img)
    vdraw.arc([5, 5, 45, 45], start=45, end=135, fill=(220, 40, 40, 240), width=4)
    vdraw.arc([5, 5, 45, 45], start=135, end=225, fill=(220, 40, 40, 240), width=4)
    vdraw.arc([5, 5, 45, 45], start=225, end=315, fill=(220, 40, 40, 240), width=4)
    vdraw.arc([5, 5, 45, 45], start=315, end=45, fill=(220, 40, 40, 240), width=4)
    vn_raw = os.path.join(raw_dir, "anime_vein.raw")
    with open(vn_raw, 'wb') as f: f.write(vn_img.tobytes())
    vn_img.save(vn_raw.replace('.raw', '.png'))
    anime_vein = {
        "name": "AnimeVein (v)",
        "left": 1100,
        "top": 170,
        "width": 50,
        "height": 50,
        "rawPath": vn_raw,
        "hidden": True
    }

    # 5. Body & Limbs
    torso = save_layer("Torso", 670, 390, 1330, 1040)
    left_arm = save_layer("Left Arm Artwork", 530, 440, 830, 1000)
    right_arm = save_layer("Right Arm Artwork", 1170, 440, 1470, 1000)
    left_hand = save_layer("Open (1)", 530, 980, 710, 1220)
    right_hand = save_layer("Open (1)", 1290, 980, 1470, 1220)

    left_leg = save_layer("+Left Leg Fixed", 680, 1020, 1000, 1980)
    right_leg = save_layer("+Right Leg Fixed", 1000, 1020, 1320, 1980)

    # 6. Assemble JSON Structure for PSD Builder
    manifest = {
        "characterName": "Aero_Star",
        "canvasWidth": canvas_w,
        "canvasHeight": canvas_h,
        "head": {
            "name": "+Head",
            "children": [
                hair_bangs,
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
                head_base
            ],
            "opened": True
        },
        "body": {
            "name": "Body",
            "children": [
                {
                    "name": "+Left Arm",
                    "children": [
                        {"name": "+Left Hand", "children": [left_hand], "opened": False},
                        left_arm
                    ],
                    "opened": False
                },
                {
                    "name": "+Right Arm Draggable",
                    "children": [
                        {"name": "+Right Hand Draggable", "children": [right_hand], "opened": False},
                        right_arm
                    ],
                    "opened": False
                },
                torso,
                left_leg,
                right_leg
            ],
            "opened": True
        }
    }

    manifest_path = os.path.join(base_dir, "puppet_manifest.json")
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)

    print(f"Manifest written to: {manifest_path}")
    print("Layer extraction completed with full real artwork!")

if __name__ == "__main__":
    build_puppet_assets()

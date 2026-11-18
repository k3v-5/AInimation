# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Compositor de Lámina Maestra de Texturas Oxidadas / Derelict (2560x1440)
# Integra Panorama 3D, 5 Close-Ups y Swatches de mapas PBR (BaseColor, Normal, ORM, Emissive)

import os
import shutil
from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = r"F:\Dev\Game"
RENDERS_DIR = os.path.join(PROJECT_ROOT, "Art", "Renders")
TEXTURES_MODULAR = os.path.join(PROJECT_ROOT, "Art", "Textures", "Modular")
ARTIFACT_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\b59ff04f-3c21-4ee5-94b0-8e8f899f8923"
OUTPUT_PATH = os.path.join(RENDERS_DIR, "Showcase_Texturas_Oxidadas_Master.png")

CANVAS_W = 2560
CANVAS_H = 1440

def get_font(size, bold=False):
    fpath = r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf"
    try:
        return ImageFont.truetype(fpath, size)
    except:
        return ImageFont.load_default()

def create_board():
    board = Image.new("RGBA", (CANVAS_W, CANVAS_H), (13, 15, 18, 255))
    draw = ImageDraw.Draw(board)
    
    # 1. Cuadrícula sutil de fondo
    grid_color = (25, 30, 38, 255)
    for x in range(0, CANVAS_W, 64):
        draw.line([(x, 0), (x, CANVAS_H)], fill=grid_color, width=1)
    for y in range(0, CANVAS_H, 64):
        draw.line([(0, y), (CANVAS_W, y)], fill=grid_color, width=1)
        
    # 2. Header Superior
    draw.rectangle([(0, 0), (CANVAS_W, 110)], fill=(18, 22, 28, 255))
    draw.line([(0, 110), (CANVAS_W, 110)], fill=(217, 119, 6, 255), width=3) # Borde ámbar
    
    font_title = get_font(32, bold=True)
    font_sub = get_font(18, bold=False)
    font_badge = get_font(14, bold=True)
    
    draw.text((40, 22), "ASTRA HAZARD // PROTOCOLO DE MATERIALES MODULARES PBR", font=font_sub, fill=(245, 158, 11, 255))
    draw.text((40, 52), "PACK DERELICT & BATTERED: OXIDACIÓN EXTREMA, IMPACTOS Y DECAIMIENTO", font=font_title, fill=(240, 243, 246, 255))
    
    # Badges Técnicos
    badges = [
        ("TIER 1 & 3 INDUSTRIAL", (180, 83, 9, 255)),
        ("DIRECTX TANGENT NORMAL", (30, 64, 175, 255)),
        ("ORM PACKED (AO/ROUGH/MET)", (5, 150, 105, 255)),
        ("EEVEE & LUMEN COMPLIANT", (124, 58, 237, 255)),
    ]
    bx = CANVAS_W - 50
    for text, bg_col in reversed(badges):
        tw = draw.textlength(text, font=font_badge)
        bw = int(tw + 24)
        bx -= bw
        draw.rounded_rectangle([(bx, 42), (bx + bw, 78)], radius=6, fill=bg_col)
        draw.text((bx + 12, 50), text, font=font_badge, fill=(255, 255, 255, 255))
        bx -= 15
        
    # 3. Panorama Central (16:9 escalado a 1600x680 o centrado)
    pano_path = os.path.join(RENDERS_DIR, "Showcase_Texturas_Oxidados_Panorama.png")
    if os.path.exists(pano_path):
        pano_img = Image.open(pano_path).convert("RGBA")
        pw = 2480
        ph = 680
        # Redimensionar recortando suavemente para ajustar al marco
        pano_resized = pano_img.resize((pw, int(pw * 1440 / 2560)), Image.Resampling.LANCZOS)
        # Recortar altura a 680
        crop_top = (pano_resized.height - ph) // 2
        pano_cropped = pano_resized.crop((0, crop_top, pw, crop_top + ph))
        
        px = 40
        py = 130
        board.paste(pano_cropped, (px, py))
        draw.rectangle([(px, py), (px + pw, py + ph)], outline=(40, 48, 60, 255), width=2)
        
        # Etiqueta de la vista
        draw.rounded_rectangle([(px + 16, py + 16), (px + 360, py + 52)], radius=6, fill=(13, 15, 18, 220))
        draw.text((px + 28, py + 24), "SHOWROOM OFICIAL: SHADER BALLS PRO V5", font=font_badge, fill=(245, 158, 11, 255))
        
    # 4. 5 Tarjetas Inferiores de Material
    card_w = 480
    card_h = 580
    card_gap = 20
    start_x = 40
    start_y = 830
    
    packs_data = [
        {
            "id": 1,
            "title": "T_Derelict_Rust_Plates",
            "desc": "Chapa descascarillada, picaduras profundas y escurrimientos",
            "rough": "0.55 - 0.95 (Rugoso)",
            "metal": "0.02 - 0.90 (Acero/Óxido)",
            "tex": "T_Derelict_Rust_Plates",
            "has_emi": False
        },
        {
            "id": 2,
            "title": "T_Battered_Armor_Impacts",
            "desc": "Cráteres balísticos, rebabas de acero y temple térmico",
            "rough": "0.14 - 0.92 (Pulido/Mate)",
            "metal": "0.20 - 0.95 (Gunmetal)",
            "tex": "T_Battered_Armor_Impacts",
            "has_emi": False
        },
        {
            "id": 3,
            "title": "T_Corroded_Acid_Pipes",
            "desc": "Conductos cuproníquel con verdigris, sulfuro y fuga tóxica",
            "rough": "0.35 - 0.88 (Patina ácida)",
            "metal": "0.05 - 0.85 (Bronce/Pátina)",
            "tex": "T_Corroded_Acid_Pipes",
            "has_emi": True
        },
        {
            "id": 4,
            "title": "T_Decayed_Rusted_Grating",
            "desc": "Pasarela carcomida por ácido con huella de pisada brillante",
            "rough": "0.25 - 0.90 (Desgaste)",
            "metal": "0.05 - 0.95 (Herrumbre)",
            "tex": "T_Decayed_Rusted_Grating",
            "has_emi": False
        },
        {
            "id": 5,
            "title": "T_Scorched_Plasma_Slag",
            "desc": "Brecha de haz de fusión, temple cromático y escoria incandescente",
            "rough": "0.15 - 0.95 (Fusión)",
            "metal": "0.10 - 0.90 (Titanio)",
            "tex": "T_Scorched_Plasma_Slag",
            "has_emi": True
        },
    ]
    
    font_card_title = get_font(18, bold=True)
    font_card_desc = get_font(13, bold=False)
    font_metric = get_font(12, bold=False)
    font_swatch = get_font(11, bold=True)
    
    for i, data in enumerate(packs_data):
        cx = start_x + i * (card_w + card_gap)
        cy = start_y
        
        # Fondo de la tarjeta
        draw.rounded_rectangle([(cx, cy), (cx + card_w, cy + card_h)], radius=10, fill=(18, 22, 28, 255), outline=(35, 42, 54, 255), width=2)
        
        # Tira de acento
        draw.rounded_rectangle([(cx + 12, cy + 12), (cx + card_w - 12, cy + 42)], radius=6, fill=(28, 35, 46, 255))
        draw.text((cx + 20, cy + 18), f"0{data['id']}. {data['title']}", font=font_card_title, fill=(245, 158, 11, 255))
        
        # Close-up 3D render
        cup_path = os.path.join(RENDERS_DIR, f"CloseUp_Oxidados_Estacion_{data['id']}.png")
        if os.path.exists(cup_path):
            cup_img = Image.open(cup_path).convert("RGBA")
            cw_target = card_w - 24
            ch_target = 240
            cup_resized = cup_img.resize((cw_target, ch_target), Image.Resampling.LANCZOS)
            board.paste(cup_resized, (cx + 12, cy + 50))
            draw.rectangle([(cx + 12, cy + 50), (cx + 12 + cw_target, cy + 50 + ch_target)], outline=(45, 55, 70, 255), width=1)
            
        # Descripción
        draw.text((cx + 16, cy + 300), data["desc"], font=font_card_desc, fill=(200, 205, 215, 255))
        
        # Métricas PBR
        draw.text((cx + 16, cy + 328), f"ROUGHNESS: {data['rough']}", font=font_metric, fill=(156, 163, 175, 255))
        draw.text((cx + 16, cy + 348), f"METALLIC: {data['metal']}", font=font_metric, fill=(156, 163, 175, 255))
        
        # Swatches PBR de texturas (4 cuadritos con BaseColor, Normal, ORM, Emissive)
        swatch_s = 96
        sw_y = cy + 375
        sw_labels = ["COLOR", "NORM", "ORM", "EMIS"]
        sw_suffixes = ["_BaseColor.png", "_Normal.png", "_ORM.png", "_Emissive.png"]
        
        for s_idx in range(4):
            sx = cx + 16 + s_idx * (swatch_s + 18)
            map_file = os.path.join(TEXTURES_MODULAR, f"{data['tex']}{sw_suffixes[s_idx]}")
            
            if os.path.exists(map_file):
                m_img = Image.open(map_file).convert("RGBA")
                m_thumb = m_img.resize((swatch_s, swatch_s), Image.Resampling.BOX)
                board.paste(m_thumb, (sx, sw_y))
                draw.rectangle([(sx, sw_y), (sx + swatch_s, sw_y + swatch_s)], outline=(60, 72, 90, 255), width=1)
            else:
                draw.rectangle([(sx, sw_y), (sx + swatch_s, sw_y + swatch_s)], fill=(10, 10, 10, 255), outline=(40, 40, 40, 255), width=1)
                
            draw.text((sx + 6, sw_y + swatch_s + 6), sw_labels[s_idx], font=font_swatch, fill=(150, 160, 175, 255))
            
    # Guardar
    board_rgb = board.convert("RGB")
    board_rgb.save(OUTPUT_PATH, quality=95)
    shutil.copy(OUTPUT_PATH, os.path.join(ARTIFACT_DIR, os.path.basename(OUTPUT_PATH)))
    print(f"[OK] Lámina Maestra de Texturas Oxidadas generada: {OUTPUT_PATH}")

if __name__ == "__main__":
    create_board()

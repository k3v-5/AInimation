# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Compositor de Lámina Maestra de Texturas de Lujo Art Déco (2560x1440)
# Integra Panorama 3D, 5 Close-Ups y Swatches de mapas PBR (BaseColor, Normal, ORM, Emissive)

import os
import shutil
from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = r"F:\Dev\Game"
RENDERS_DIR = os.path.join(PROJECT_ROOT, "Art", "Renders")
TEXTURES_MODULAR = os.path.join(PROJECT_ROOT, "Art", "Textures", "Modular")
ARTIFACT_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\b59ff04f-3c21-4ee5-94b0-8e8f899f8923"
OUTPUT_PATH = os.path.join(RENDERS_DIR, "Showcase_Texturas_Lujo_Master.png")

CANVAS_W = 2560
CANVAS_H = 1440

def get_font(size, bold=False):
    fpath = r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf"
    try:
        return ImageFont.truetype(fpath, size)
    except:
        return ImageFont.load_default()

def create_board():
    board = Image.new("RGBA", (CANVAS_W, CANVAS_H), (14, 13, 16, 255))
    draw = ImageDraw.Draw(board)
    
    # 1. Cuadrícula sutil dorada de fondo
    grid_color = (28, 25, 32, 255)
    for x in range(0, CANVAS_W, 64):
        draw.line([(x, 0), (x, CANVAS_H)], fill=grid_color, width=1)
    for y in range(0, CANVAS_H, 64):
        draw.line([(0, y), (CANVAS_W, y)], fill=grid_color, width=1)
        
    # 2. Header Superior
    draw.rectangle([(0, 0), (CANVAS_W, 110)], fill=(20, 18, 24, 255))
    draw.line([(0, 110), (CANVAS_W, 110)], fill=(234, 179, 8, 255), width=3) # Borde dorado champagne
    
    font_title = get_font(32, bold=True)
    font_sub = get_font(18, bold=False)
    font_badge = get_font(14, bold=True)
    
    draw.text((40, 22), "ASTRA HAZARD // PROTOCOLO DE MATERIALES MODULARES PBR", font=font_sub, fill=(250, 204, 21, 255))
    draw.text((40, 52), "PACK LUXURY & ART DÉCO: CRUCERO CELESTIA, MÁRMOL, ORO Y MADERAS NOBLES", font=font_title, fill=(245, 243, 248, 255))
    
    # Badges Técnicos
    badges = [
        ("TIER 2 CELESTIA CRUISE", (161, 98, 7, 255)),
        ("DIRECTX TANGENT NORMAL", (30, 64, 175, 255)),
        ("ORM PACKED (AO/ROUGH/MET)", (5, 150, 105, 255)),
        ("HIGH-POLISH REFLECTIONS", (124, 58, 237, 255)),
    ]
    bx = CANVAS_W - 50
    for text, bg_col in reversed(badges):
        tw = draw.textlength(text, font=font_badge)
        bw = int(tw + 24)
        bx -= bw
        draw.rounded_rectangle([(bx, 42), (bx + bw, 78)], radius=6, fill=bg_col)
        draw.text((bx + 12, 50), text, font=font_badge, fill=(255, 255, 255, 255))
        bx -= 15
        
    # 3. Panorama Central
    pano_path = os.path.join(RENDERS_DIR, "Showcase_Texturas_Lujo_Panorama.png")
    if os.path.exists(pano_path):
        pano_img = Image.open(pano_path).convert("RGBA")
        pw = 2480
        ph = 680
        pano_resized = pano_img.resize((pw, int(pw * 1440 / 2560)), Image.Resampling.LANCZOS)
        crop_top = (pano_resized.height - ph) // 2
        pano_cropped = pano_resized.crop((0, crop_top, pw, crop_top + ph))
        
        px = 40
        py = 130
        board.paste(pano_cropped, (px, py))
        draw.rectangle([(px, py), (px + pw, py + ph)], outline=(50, 44, 60, 255), width=2)
        
        draw.rounded_rectangle([(px + 16, py + 16), (px + 360, py + 52)], radius=6, fill=(14, 13, 16, 220))
        draw.text((px + 28, py + 24), "SHOWROOM OFICIAL: SHADER BALLS PRO V5", font=font_badge, fill=(250, 204, 21, 255))
        
    # 4. 5 Tarjetas Inferiores de Material
    card_w = 480
    card_h = 580
    card_gap = 20
    start_x = 40
    start_y = 830
    
    packs_data = [
        {
            "id": 1,
            "title": "T_Luxury_Marble_Gold_Inlay",
            "desc": "Mármol Calacatta pulido espejo con filigrana Art Déco de oro",
            "rough": "0.08 - 0.14 (Ultra Pulido)",
            "metal": "0.00 - 1.00 (Mármol / Oro 24k)",
            "tex": "T_Luxury_Marble_Gold_Inlay",
            "has_emi": False
        },
        {
            "id": 2,
            "title": "T_Luxury_Walnut_Wood_Panels",
            "desc": "Boiserie vertical de nogal noble con molduras y latón dorado",
            "rough": "0.16 - 0.24 (Satinado fino)",
            "metal": "0.00 - 0.98 (Madera / Latón)",
            "tex": "T_Luxury_Walnut_Wood_Panels",
            "has_emi": False
        },
        {
            "id": 3,
            "title": "T_Luxury_ArtDeco_Gilded_Brass",
            "desc": "Escamas solares fluted con pátina bronce en acanaladuras",
            "rough": "0.14 - 0.70 (Cepillado)",
            "metal": "0.98 (Latón arquitectónico)",
            "tex": "T_Luxury_ArtDeco_Gilded_Brass",
            "has_emi": False
        },
        {
            "id": 4,
            "title": "T_Luxury_Quilted_Velvet_Leather",
            "desc": "Capitoné Chesterfield azul noche con botones dorados 3D",
            "rough": "0.15 - 0.42 (Cuero / Botones)",
            "metal": "0.00 - 1.00 (Cuero / Oro)",
            "tex": "T_Luxury_Quilted_Velvet_Leather",
            "has_emi": False
        },
        {
            "id": 5,
            "title": "T_Luxury_Smoked_Glass_Lattice",
            "desc": "Vidrio obsidiana templado con tracería dorada y luz cálida 2700K",
            "rough": "0.05 - 0.18 (Espejo / Latón)",
            "metal": "0.05 - 0.98 (Vidrio / Tracería)",
            "tex": "T_Luxury_Smoked_Glass_Lattice",
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
        
        draw.rounded_rectangle([(cx, cy), (cx + card_w, cy + card_h)], radius=10, fill=(20, 18, 24, 255), outline=(45, 38, 55, 255), width=2)
        
        draw.rounded_rectangle([(cx + 12, cy + 12), (cx + card_w - 12, cy + 42)], radius=6, fill=(32, 28, 40, 255))
        draw.text((cx + 20, cy + 18), f"0{data['id']}. {data['title']}", font=font_card_title, fill=(250, 204, 21, 255))
        
        cup_path = os.path.join(RENDERS_DIR, f"CloseUp_Lujo_Estacion_{data['id']}.png")
        if os.path.exists(cup_path):
            cup_img = Image.open(cup_path).convert("RGBA")
            cw_target = card_w - 24
            ch_target = 240
            cup_resized = cup_img.resize((cw_target, ch_target), Image.Resampling.LANCZOS)
            board.paste(cup_resized, (cx + 12, cy + 50))
            draw.rectangle([(cx + 12, cy + 50), (cx + 12 + cw_target, cy + 50 + ch_target)], outline=(60, 50, 75, 255), width=1)
            
        draw.text((cx + 16, cy + 300), data["desc"], font=font_card_desc, fill=(215, 210, 225, 255))
        draw.text((cx + 16, cy + 328), f"ROUGHNESS: {data['rough']}", font=font_metric, fill=(170, 165, 185, 255))
        draw.text((cx + 16, cy + 348), f"METALLIC: {data['metal']}", font=font_metric, fill=(170, 165, 185, 255))
        
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
                draw.rectangle([(sx, sw_y), (sx + swatch_s, sw_y + swatch_s)], outline=(80, 70, 95, 255), width=1)
            else:
                draw.rectangle([(sx, sw_y), (sx + swatch_s, sw_y + swatch_s)], fill=(10, 10, 10, 255), outline=(40, 40, 40, 255), width=1)
                
            draw.text((sx + 6, sw_y + swatch_s + 6), sw_labels[s_idx], font=font_swatch, fill=(160, 155, 175, 255))
            
    board_rgb = board.convert("RGB")
    board_rgb.save(OUTPUT_PATH, quality=95)
    shutil.copy(OUTPUT_PATH, os.path.join(ARTIFACT_DIR, os.path.basename(OUTPUT_PATH)))
    print(f"[OK] Lámina Maestra de Texturas de Lujo generada: {OUTPUT_PATH}")

if __name__ == "__main__":
    create_board()

# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Compositor de la Lámina Maestra de Texturas y Materiales PBR (2560x1440) - V5 Pro

import os
import shutil
from PIL import Image, ImageDraw, ImageFont

RENDERS_DIR = r"F:\Dev\Game\Art\Renders"
ARTIFACT_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\b59ff04f-3c21-4ee5-94b0-8e8f899f8923"

def get_font(size, bold=True):
    font_paths = [
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\seguiemb.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\consola.ttf"
    ]
    for p in font_paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

def compose_master_sheet():
    width = 2560
    height = 1440
    canvas = Image.new("RGBA", (width, height), (14, 15, 17, 255))
    draw = ImageDraw.Draw(canvas)
    
    # Fuentes
    font_title = get_font(40, bold=True)
    font_subtitle = get_font(20, bold=False)
    font_card_num = get_font(15, bold=True)
    font_card_title = get_font(21, bold=True)
    font_card_tag = get_font(13, bold=True)
    font_card_desc = get_font(15, bold=False)
    font_badge = get_font(15, bold=True)
    font_banner = get_font(22, bold=True)
    
    # 1. Encabezado Superior (y: 0 .. 95)
    draw.rectangle([(0, 0), (width, 90)], fill=(20, 22, 26, 255))
    draw.line([(0, 90), (width, 90)], fill=(245, 195, 30, 255), width=3)
    
    draw.text((50, 18), "CATÁLOGO MAESTRO DE TEXTURAS Y MATERIALES PBR MODULARES", fill=(245, 245, 245, 255), font=font_title)
    draw.text((50, 62), "SECTOR INDUSTRIAL & FÁBRICA // CEL-SHADING & PBR ORM PACKING // UNREAL ENGINE 5 READY", fill=(175, 180, 190, 255), font=font_subtitle)
    
    # Badges
    badges = [
        ("PBR 2048x2048", (45, 140, 240, 255)),
        ("BLENDER 5.2 LTS", (235, 120, 30, 255)),
        ("CEL-SHADE INLINES", (40, 180, 80, 255)),
        ("ORM PACKED", (190, 60, 220, 255))
    ]
    bx = 1720
    for text, color in badges:
        bw = 175
        draw.rounded_rectangle([(bx, 24), (bx + bw, 66)], radius=6, fill=(28, 30, 36, 255), outline=color, width=2)
        draw.text((bx + 14, 36), text, fill=color, font=font_badge)
        bx += 195
        
    # 2. Panel Principal Superior: Panorama Completo del Banco de Pruebas (y: 105 .. 780)
    panorama_path = os.path.join(RENDERS_DIR, "Showcase_Material_Test_Bench_Master.png")
    pano_x = 50
    pano_y = 105
    pano_w = 2460
    pano_h = 675
    
    if os.path.exists(panorama_path):
        img_pano = Image.open(panorama_path).convert("RGBA")
        # Recorte de bandas vacías superior/inferior para maximizar presencia de las estaciones
        pw, ph = img_pano.size
        crop_top = int(ph * 0.22)
        crop_bottom = int(ph * 0.61)
        img_pano_cropped = img_pano.crop((0, crop_top, pw, crop_bottom))
        
        img_pano_resized = img_pano_cropped.resize((pano_w, pano_h), Image.Resampling.LANCZOS)
        canvas.paste(img_pano_resized, (pano_x, pano_y))
        draw.rectangle([(pano_x, pano_y), (pano_x + pano_w, pano_y + pano_h)], outline=(55, 60, 70, 255), width=2)
        
        # Etiqueta sobre el panorama
        banner_w = 640
        draw.rounded_rectangle([(pano_x + 20, pano_y + 18), (pano_x + 20 + banner_w, pano_y + 60)], radius=6, fill=(18, 20, 24, 230), outline=(245, 195, 30, 255), width=2)
        draw.text((pano_x + 35, pano_y + 26), "MATERIAL TEST BENCH: ESTACIONES 01 A 05", fill=(245, 195, 30, 255), font=font_banner)
        
    # 3. Paneles Inferiores: 5 Columnas Focales con Proporción 4:3 Nativa (y: 795 .. 1415)
    stations = [
        {
            "num": "ESTACIÓN 01",
            "title": "TRIM INDUSTRIAL",
            "tag": "TRIM SHEET // HAZARD 45°",
            "desc": "Chevrons de advertencia, placas remachadas, rejilla de filtro y zócalo corrugado.",
            "img": "Showcase_Material_Trim_Industrial.png",
            "specs": [("NORM", "Bevel 45° Inlines"), ("ORM", "Metal 0.85 | Rough 0.35")]
        },
        {
            "num": "ESTACIÓN 02",
            "title": "STEEL PLATES",
            "tag": "ARMOR BULKHEAD // WELD SEAMS",
            "desc": "Blindaje de 4 paneles, cordón de soldadura, biseles inlines y marcadores de esquina.",
            "img": "Showcase_Material_Steel_Plates.png",
            "specs": [("NORM", "Bevel Seams + Welds"), ("ORM", "Metal 0.95 | Rough 0.28")]
        },
        {
            "num": "ESTACIÓN 03",
            "title": "GRATING WALKWAY",
            "tag": "VENTILATED MESH // WALKWAYS",
            "desc": "Malla calada de diamante con relieve normal, peldaños biselados y tubos de soporte.",
            "img": "Showcase_Material_Grating_Walkway.png",
            "specs": [("NORM", "Rhomboid Mesh Depth"), ("ORM", "Metal 0.90 | Rough 0.40")]
        },
        {
            "num": "ESTACIÓN 04",
            "title": "CONCRETE FACTORY",
            "tag": "PORE TEXTURE // OIL STAINS",
            "desc": "Hormigón poroso con fisuras dendríticas y manchas orgánicas de aceite y grasa industrial.",
            "img": "Showcase_Material_Concrete_Factory.png",
            "specs": [("NORM", "Pore & Crack Inlines"), ("ORM", "Metal 0.05 | Rough 0.82")]
        },
        {
            "num": "ESTACIÓN 05",
            "title": "PROPS MACHINERY",
            "tag": "ATLAS // CRT OSCILLOSCOPE",
            "desc": "Manómetro de latón analógico, pantalla fósforo CRT verde y botón de parada de emergencia.",
            "img": "Showcase_Material_Props_Machinery.png",
            "specs": [("EMIS", "CRT Green + Alert Red"), ("ORM", "Brass Metal | Screen Rough")]
        }
    ]
    
    card_y = 795
    card_h = 620
    card_w = 478
    gap_x = 17
    start_x = (width - (5 * card_w + 4 * gap_x)) // 2
    
    # Tamaño de la imagen interior: ancho 462, alto 346 (ratio 4:3 perfecto)
    inner_img_w = card_w - 16
    inner_img_h = int(inner_img_w * (3.0 / 4.0)) # 346 px
    
    for i, st in enumerate(stations):
        cx = start_x + i * (card_w + gap_x)
        
        # Marco del Contenedor
        draw.rounded_rectangle([(cx, card_y), (cx + card_w, card_y + card_h)], radius=8, fill=(22, 24, 28, 255), outline=(45, 50, 60, 255), width=2)
        
        # Recorte y Render focal en proporción 4:3 sin distorsión geométrica
        c_path = os.path.join(RENDERS_DIR, st["img"])
        if os.path.exists(c_path):
            img_c = Image.open(c_path).convert("RGBA")
            cw, ch = img_c.size
            # Recorte 4:3 centrado en el shader ball y props
            target_crop_w = int(ch * (4.0 / 3.0)) # 1080 * 1.333 = 1440
            crop_x0 = (cw - target_crop_w) // 2
            img_c_cropped = img_c.crop((crop_x0, 0, crop_x0 + target_crop_w, ch))
            
            img_c_res = img_c_cropped.resize((inner_img_w, inner_img_h), Image.Resampling.LANCZOS)
            canvas.paste(img_c_res, (cx + 8, card_y + 8))
            draw.rectangle([(cx + 8, card_y + 8), (cx + 8 + inner_img_w, card_y + 8 + inner_img_h)], outline=(35, 40, 48, 255), width=1)
            
        # Textos informativos de la tarjeta
        # Número de estación
        draw.rounded_rectangle([(cx + 14, card_y + inner_img_h + 16), (cx + 125, card_y + inner_img_h + 38)], radius=4, fill=(35, 40, 50, 255), outline=(245, 195, 30, 255), width=1)
        draw.text((cx + 22, card_y + inner_img_h + 19), st["num"], fill=(245, 195, 30, 255), font=font_card_num)
        
        # Tag técnico
        draw.text((cx + 135, card_y + inner_img_h + 21), st["tag"], fill=(120, 185, 255, 255), font=font_card_tag)
        
        # Título del material
        draw.text((cx + 14, card_y + inner_img_h + 46), st["title"], fill=(245, 245, 245, 255), font=font_card_title)
        
        # Descripción envolvente
        desc_lines = []
        words = st["desc"].split()
        cur_line = ""
        for w in words:
            test_l = (cur_line + " " + w).strip()
            if len(test_l) > 42:
                desc_lines.append(cur_line)
                cur_line = w
            else:
                cur_line = test_l
        if cur_line:
            desc_lines.append(cur_line)
            
        desc_y = card_y + inner_img_h + 76
        for line in desc_lines:
            draw.text((cx + 14, desc_y), line, fill=(155, 162, 175, 255), font=font_card_desc)
            desc_y += 20
            
        # Píldoras de Especificaciones Técnicas
        pill_y = card_y + card_h - 48
        for p_idx, (p_tag, p_val) in enumerate(st.get("specs", [])):
            px = cx + 14 + p_idx * 225
            pw = 215
            draw.rounded_rectangle([(px, pill_y), (px + pw, pill_y + 32)], radius=5, fill=(16, 18, 22, 255), outline=(60, 65, 78, 255), width=1)
            draw.text((px + 8, pill_y + 8), p_tag, fill=(245, 195, 30, 255), font=font_card_tag)
            draw.text((px + 55, pill_y + 9), p_val, fill=(200, 205, 215, 255), font=font_card_desc)
            
    out_master = os.path.join(RENDERS_DIR, "Showcase_Catalogo_Texturas_Master.png")
    canvas.save(out_master)
    shutil.copy(out_master, os.path.join(ARTIFACT_DIR, "Showcase_Catalogo_Texturas_Master.png"))
    print(f"[OK] Lámina maestra compuesta y guardada: {out_master}")

if __name__ == "__main__":
    compose_master_sheet()

# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Generador Maestro de Texturas Modulares PBR Estilizadas V2 (Fase Industrial & Fábrica)
# Corrige manchas geométricas, escalas de malla, balance de rótulos, contraste tonal y mapas normales/ORM.

import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUTPUT_DIR = r"F:\Dev\Game\Art\Textures\Modular"
os.makedirs(OUTPUT_DIR, exist_ok=True)

RES = 2048

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

def height_to_normal(height_array, strength=4.5):
    """
    Convierte array de altura float32 [0.0..1.0] a mapa de normales tangent-space RGB.
    DirectX / Unreal: Eje Y invertido.
    """
    gy, gx = np.gradient(height_array)
    gx = -gx * strength
    gy = gy * strength
    gz = np.ones_like(gx)
    
    norm = np.sqrt(gx**2 + gy**2 + gz**2)
    norm = np.maximum(norm, 1e-6)
    nx = gx / norm
    ny = gy / norm
    nz = gz / norm
    
    r = np.clip((nx * 0.5 + 0.5) * 255.0, 0, 255).astype(np.uint8)
    g = np.clip((ny * 0.5 + 0.5) * 255.0, 0, 255).astype(np.uint8)
    b = np.clip((nz * 0.5 + 0.5) * 255.0, 0, 255).astype(np.uint8)
    return Image.fromarray(np.stack([r, g, b], axis=-1), mode="RGB")

def pack_orm(ao_array, roughness_array, metallic_array):
    r = np.clip(ao_array * 255.0, 0, 255).astype(np.uint8)
    g = np.clip(roughness_array * 255.0, 0, 255).astype(np.uint8)
    b = np.clip(metallic_array * 255.0, 0, 255).astype(np.uint8)
    return Image.fromarray(np.stack([r, g, b], axis=-1), mode="RGB")

# ==============================================================================
# 1. TRIM INDUSTRIAL V2 (Equilibrio de Franjas y Rótulos Proporcionales)
# ==============================================================================
def generate_trim_industrial_v2():
    prefix = os.path.join(OUTPUT_DIR, "T_Trim_Industrial")
    base = Image.new("RGBA", (RES, RES), (45, 42, 40, 255))
    draw = ImageDraw.Draw(base)
    
    height_img = Image.new("L", (RES, RES), 128)
    hdraw = ImageDraw.Draw(height_img)
    
    ao_map = np.ones((RES, RES), dtype=np.float32)
    rough_map = np.full((RES, RES), 0.60, dtype=np.float32)
    metal_map = np.full((RES, RES), 0.85, dtype=np.float32)
    
    emissive = Image.new("RGB", (RES, RES), (0, 0, 0))
    edraw = ImageDraw.Draw(emissive)
    
    # BANDA 1 (0..300): Franja Hazard de Seguridad (Chevrons a 45°)
    yellow = (245, 195, 20, 255)
    black = (20, 20, 22, 255)
    for x in range(-500, RES + 600, 140):
        draw.polygon([(x, 0), (x + 70, 0), (x + 70 - 300, 300), (x - 300, 300)], fill=black)
        draw.polygon([(x + 70, 0), (x + 140, 0), (x + 140 - 300, 300), (x + 70 - 300, 300)], fill=yellow)
    # Inlines gruesos en bordes
    draw.rectangle([(0, 0), (RES, 16)], fill=(12, 12, 12, 255))
    draw.rectangle([(0, 284), (RES, 300)], fill=(12, 12, 12, 255))
    hdraw.rectangle([(0, 0), (RES, 16)], fill=60)
    hdraw.rectangle([(0, 284), (RES, 300)], fill=60)
    
    # Raspones metálicos en la franja hazard
    for sx in [150, 420, 890, 1340, 1780]:
        draw.line([(sx, 40), (sx + 90, 240)], fill=(175, 175, 175, 255), width=3)
        draw.line([(sx + 5, 40), (sx + 95, 240)], fill=(12, 12, 12, 255), width=1)
        hdraw.line([(sx, 40), (sx + 90, 240)], fill=190, width=3)
    
    rough_map[0:300, :] = 0.50
    metal_map[0:300, :] = 0.30
    ao_map[0:16, :] = 0.25
    ao_map[284:300, :] = 0.25
    
    # BANDA 2 (300..850): Placas de Acero Gunmetal con Remaches y Óxido
    steel_col = (110, 105, 102, 255)
    draw.rectangle([(0, 300), (RES, 850)], fill=steel_col)
    hdraw.rectangle([(0, 300), (RES, 850)], fill=155)
    
    # Juntas verticales biseladas cada 512px
    for px in range(0, RES, 512):
        draw.rectangle([(px - 6, 300), (px + 6, 850)], fill=(15, 15, 15, 255))
        draw.line([(px + 7, 300), (px + 7, 850)], fill=(175, 170, 165, 255), width=3)
        hdraw.rectangle([(px - 6, 300), (px + 6, 850)], fill=60)
        ao_map[300:850, max(0, px - 12):min(RES, px + 12)] = 0.2
    
    # Junta horizontal central
    draw.rectangle([(0, 570), (RES, 582)], fill=(15, 15, 15, 255))
    draw.line([(0, 583), (RES, 583)], fill=(175, 170, 165, 255), width=3)
    hdraw.rectangle([(0, 570), (RES, 582)], fill=60)
    ao_map[566:586, :] = 0.2
    
    # Remaches con volumen y sombreado
    for py in [340, 540, 610, 810]:
        for px in range(32, RES, 64):
            draw.ellipse([(px - 12, py - 12), (px + 12, py + 12)], fill=(14, 14, 14, 255))
            draw.ellipse([(px - 10, py - 10), (px + 9, py + 9)], fill=(150, 145, 140, 255))
            draw.ellipse([(px - 6, py - 6), (px + 5, py + 5)], fill=(210, 205, 200, 255))
            hdraw.ellipse([(px - 11, py - 11), (px + 11, py + 11)], fill=240)
            rough_map[py-11:py+11, px-11:px+11] = 0.30
            metal_map[py-11:py+11, px-11:px+11] = 0.95
    
    # Chorretones de óxido naranja intenso
    for rx in [220, 750, 1280, 1800]:
        draw.polygon([(rx, 575), (rx + 90, 575), (rx + 120, 800), (rx - 30, 800)], fill=(170, 72, 22, 230))
        draw.polygon([(rx + 20, 575), (rx + 60, 575), (rx + 80, 740), (rx, 740)], fill=(210, 95, 28, 240))
        rough_map[575:800, rx-20:rx+110] = 0.92
        metal_map[575:800, rx-20:rx+110] = 0.05
    
    # BANDA 3 (850..1350): Rejilla Perforada Diamond Mesh
    draw.rectangle([(0, 850), (RES, 1350)], fill=(20, 18, 16, 255))
    hdraw.rectangle([(0, 850), (RES, 1350)], fill=30)
    
    mesh_col = (145, 140, 135, 255)
    for x in range(-500, RES + 600, 48):
        draw.line([(x, 850), (x + 500, 1350)], fill=(12, 12, 12, 255), width=6)
        draw.line([(x + 2, 850), (x + 502, 1350)], fill=mesh_col, width=3)
        draw.line([(x + 500, 850), (x, 1350)], fill=(12, 12, 12, 255), width=6)
        draw.line([(x + 502, 850), (x + 2, 1350)], fill=mesh_col, width=3)
        hdraw.line([(x, 850), (x + 500, 1350)], fill=210, width=5)
        hdraw.line([(x + 500, 850), (x, 1350)], fill=210, width=5)
        
    # Marcos de contención superior e inferior
    draw.rectangle([(0, 850), (RES, 878)], fill=(75, 72, 68, 255), outline=(12, 12, 12, 255), width=3)
    draw.rectangle([(0, 1322), (RES, 1350)], fill=(75, 72, 68, 255), outline=(12, 12, 12, 255), width=3)
    hdraw.rectangle([(0, 850), (RES, 878)], fill=180)
    hdraw.rectangle([(0, 1322), (RES, 1350)], fill=180)
    ao_map[878:1322, :] = 0.40
    
    # BANDA 4 (1350..1700): Señalética Técnica Estarcida (Proporcional y Estilizada)
    draw.rectangle([(0, 1350), (RES, 1700)], fill=(195, 148, 24, 255))
    hdraw.rectangle([(0, 1350), (RES, 1700)], fill=140)
    
    font_ind = get_font(52, bold=True)
    font_sub = get_font(30, bold=True)
    
    # Rótulos técnicos limpios
    draw.text((70, 1380), "[ SECTOR 07 ] // ACCESO INDUSTRIAL", fill=(14, 14, 16, 255), font=font_ind)
    draw.text((70, 1460), "PURGA DE VAPOR: VÁLVULAS N-12 / N-14", fill=(14, 14, 16, 255), font=font_sub)
    draw.text((70, 1515), "PRECAUCIÓN: ATMÓSFERA TÓXICA CLASE 3", fill=(160, 20, 15, 255), font=font_sub)
    
    draw.text((1150, 1380), "PRESIÓN MÁX: 350 BAR", fill=(14, 14, 16, 255), font=font_ind)
    draw.text((1150, 1460), "CÓDIGO: HAZ-8842 // AUTORIZADO", fill=(14, 14, 16, 255), font=font_sub)
    draw.text((1150, 1515), "ESTADO SISTEMA: EN LÍNEA", fill=(20, 95, 30, 255), font=font_sub)
    
    # Piloto LED de advertencia con emisión pura
    edraw.ellipse([(1940, 1385), (1985, 1430)], fill=(255, 35, 15))
    draw.ellipse([(1936, 1381), (1989, 1434)], fill=(12, 12, 12, 255))
    draw.ellipse([(1940, 1385), (1985, 1430)], fill=(255, 60, 30, 255))
    hdraw.ellipse([(1940, 1385), (1985, 1430)], fill=220)
    
    rough_map[1350:1700, :] = 0.58
    metal_map[1350:1700, :] = 0.22
    
    # BANDA 5 (1700..2048): Chapa Corrugada Naval
    draw.rectangle([(0, 1700), (RES, 2048)], fill=(48, 75, 110, 255))
    for cx in range(0, RES, 64):
        draw.rectangle([(cx, 1700), (cx + 32, 2048)], fill=(32, 54, 82, 255))
        draw.rectangle([(cx + 32, 1700), (cx + 64, 2048)], fill=(62, 98, 142, 255))
        draw.line([(cx, 1700), (cx, 2048)], fill=(14, 25, 42, 255), width=3)
        draw.line([(cx + 32, 1700), (cx + 32, 2048)], fill=(85, 130, 185, 255), width=2)
        hdraw.rectangle([(cx, 1700), (cx + 32, 2048)], fill=95)
        hdraw.rectangle([(cx + 32, 1700), (cx + 64, 2048)], fill=205)
        
    draw.text((60, 1740), "ASTRA LOGISTICS // CONTENEDOR HAZMAT", fill=(230, 235, 245, 255), font=font_ind)
    draw.text((60, 1820), "DEPÓSITO ESTRUCTURAL REFORZADO #07", fill=(245, 195, 30, 255), font=font_sub)
    rough_map[1700:2048, :] = 0.42
    metal_map[1700:2048, :] = 0.88
    
    base.save(f"{prefix}_BaseColor.png")
    h_smooth = height_img.filter(ImageFilter.GaussianBlur(radius=1.8))
    normal_img = height_to_normal(np.array(h_smooth, dtype=np.float32) / 255.0, strength=5.5)
    normal_img.save(f"{prefix}_Normal.png")
    pack_orm(ao_map, rough_map, metal_map).save(f"{prefix}_ORM.png")
    emissive.save(f"{prefix}_Emissive.png")
    print(f"[OK] Generado T_Trim_Industrial V2 completo")

# ==============================================================================
# 2. CONCRETE FACTORY V2 (Manchas Orgánicas Irregulares y Grietas Dendríticas)
# ==============================================================================
def generate_concrete_factory_v2():
    prefix = os.path.join(OUTPUT_DIR, "T_Concrete_Factory")
    
    # Cemento gris industrial con grano de piedra
    np.random.seed(123)
    c_base = 125
    noise = (np.random.randn(RES, RES) * 16).astype(np.int16)
    concrete_raw = np.clip(c_base + noise, 0, 255).astype(np.uint8)
    
    # Matriz RGB con sutil tinte ocre/cálido industrial
    r = np.clip(concrete_raw * 1.02, 0, 255).astype(np.uint8)
    g = np.clip(concrete_raw * 1.00, 0, 255).astype(np.uint8)
    b = np.clip(concrete_raw * 0.96, 0, 255).astype(np.uint8)
    base_img = Image.fromarray(np.stack([r, g, b], axis=-1), mode="RGB")
    draw = ImageDraw.Draw(base_img)
    
    height_img = Image.fromarray(concrete_raw, mode="L")
    hdraw = ImageDraw.Draw(height_img)
    
    ao_map = np.ones((RES, RES), dtype=np.float32)
    rough_map = np.full((RES, RES), 0.88, dtype=np.float32)
    metal_map = np.zeros((RES, RES), dtype=np.float32) # Dieléctrico puro
    emissive = Image.new("RGB", (RES, RES), (0, 0, 0))
    
    # Manchas de aceite ORGÁNICAS mediante cúmulos fractales elípticos
    for center_x, center_y, max_r in [(480, 520, 280), (1380, 1420, 340), (780, 1680, 220), (1620, 480, 260)]:
        # Generar sub-gotas alrededor del centro
        for _ in range(65):
            angle = np.random.uniform(0, 2 * math.pi)
            dist = np.random.uniform(0, max_r) * np.random.uniform(0.3, 1.0)
            spot_x = int(center_x + dist * math.cos(angle))
            spot_y = int(center_y + dist * math.sin(angle))
            spot_r = int(np.random.uniform(15, 65))
            
            # Tono aceite oscuro
            oil_tone = (42, 38, 32)
            draw.ellipse([(spot_x - spot_r, spot_y - spot_r), (spot_x + spot_r, spot_y + spot_r)], fill=oil_tone)
            # Roughness bajo (aceite brillante)
            y1, y2 = max(0, spot_y - spot_r), min(RES, spot_y + spot_r)
            x1, x2 = max(0, spot_x - spot_r), min(RES, spot_x + spot_r)
            rough_map[y1:y2, x1:x2] = 0.45
            
    # Grietas dendríticas ramificadas (estilo cómic con inlines)
    main_cracks = [
        # Grieta 1
        [(150, 0), (220, 350), (320, 720), (260, 1100), (380, 1550), (450, 2048)],
        # Grieta 2
        [(1350, 0), (1280, 400), (1420, 850), (1550, 1300), (1480, 1750), (1600, 2048)],
        # Grieta transversal
        [(0, 880), (320, 920), (750, 860), (1200, 940), (1650, 890), (2048, 930)]
    ]
    
    # Ramas secundarias
    sub_branches = [
        [(320, 720), (510, 820), (680, 800)],
        [(260, 1100), (420, 1250), (550, 1350)],
        [(1420, 850), (1250, 1020), (1150, 1120)],
        [(1550, 1300), (1750, 1420), (1920, 1480)]
    ]
    
    all_cracks = [(main_cracks, 7, 3), (sub_branches, 4, 2)]
    for crack_list, w_outer, w_inner in all_cracks:
        for crack in crack_list:
            for i in range(len(crack) - 1):
                p1, p2 = crack[i], crack[i+1]
                draw.line([p1, p2], fill=(16, 14, 14), width=w_outer)
                draw.line([p1, p2], fill=(50, 46, 44), width=w_inner)
                hdraw.line([p1, p2], fill=20, width=w_outer + 2)
                hdraw.line([p1, p2], fill=5, width=w_inner)
    
    base_img.save(f"{prefix}_BaseColor.png")
    h_smooth = height_img.filter(ImageFilter.GaussianBlur(radius=2.0))
    normal_img = height_to_normal(np.array(h_smooth, dtype=np.float32) / 255.0, strength=6.0)
    normal_img.save(f"{prefix}_Normal.png")
    
    h_crack_mask = (np.array(height_img) < 60).astype(np.float32)
    ao_map = 1.0 - (h_crack_mask * 0.8)
    pack_orm(ao_map, rough_map, metal_map).save(f"{prefix}_ORM.png")
    emissive.save(f"{prefix}_Emissive.png")
    print(f"[OK] Generado T_Concrete_Factory V2 completo")

# ==============================================================================
# 3. STEEL PLATES V2 (Contraste Tonal, Desgaste de Aristas y Soldaduras)
# ==============================================================================
def generate_steel_plates_v2():
    prefix = os.path.join(OUTPUT_DIR, "T_Steel_Plates")
    # Base acero gris medio templado
    base = Image.new("RGBA", (RES, RES), (92, 88, 85, 255))
    draw = ImageDraw.Draw(base)
    
    height_img = Image.new("L", (RES, RES), 150)
    hdraw = ImageDraw.Draw(height_img)
    
    ao_map = np.ones((RES, RES), dtype=np.float32)
    rough_map = np.full((RES, RES), 0.44, dtype=np.float32)
    metal_map = np.full((RES, RES), 0.92, dtype=np.float32)
    emissive = Image.new("RGB", (RES, RES), (0, 0, 0))
    
    # 4 Cuadrantes de placas de blindaje
    grid = [0, 1024, 2048]
    for i in range(2):
        for j in range(2):
            x1, x2 = grid[i], grid[i+1]
            y1, y2 = grid[j], grid[j+1]
            
            # Bisel de arista con desgaste brillante (edge highlight)
            draw.rectangle([(x1 + 12, y1 + 12), (x2 - 12, y2 - 12)], outline=(14, 14, 14, 255), width=8)
            draw.rectangle([(x1 + 16, y1 + 16), (x2 - 16, y2 - 16)], outline=(195, 192, 190, 255), width=3)
            hdraw.rectangle([(x1 + 12, y1 + 12), (x2 - 12, y2 - 12)], fill=185)
            
            # Remaches reforzados visibles
            for rx in range(x1 + 64, x2 - 50, 72):
                for ry in [y1 + 64, y2 - 64]:
                    draw.ellipse([(rx - 12, ry - 12), (rx + 12, ry + 12)], fill=(12, 12, 12, 255))
                    draw.ellipse([(rx - 9, ry - 9), (rx + 8, ry + 8)], fill=(160, 155, 150, 255))
                    draw.ellipse([(rx - 5, ry - 5), (rx + 4, ry + 4)], fill=(225, 220, 215, 255))
                    hdraw.ellipse([(rx - 10, ry - 10), (rx + 10, ry + 10)], fill=245)
            for ry in range(y1 + 64, y2 - 50, 72):
                for rx in [x1 + 64, x2 - 64]:
                    draw.ellipse([(rx - 12, ry - 12), (rx + 12, ry + 12)], fill=(12, 12, 12, 255))
                    draw.ellipse([(rx - 9, ry - 9), (rx + 8, ry + 8)], fill=(160, 155, 150, 255))
                    draw.ellipse([(rx - 5, ry - 5), (rx + 4, ry + 4)], fill=(225, 220, 215, 255))
                    hdraw.ellipse([(rx - 10, ry - 10), (rx + 10, ry + 10)], fill=245)
            
            # Cordón de soldadura en diagonal con micro-arrugas
            draw.line([(x1 + 250, y1 + 80), (x1 + 420, y1 + 250)], fill=(205, 200, 195, 255), width=10)
            draw.line([(x1 + 250, y1 + 80), (x1 + 420, y1 + 250)], fill=(16, 16, 16, 255), width=2)
            hdraw.line([(x1 + 250, y1 + 80), (x1 + 420, y1 + 250)], fill=230, width=10)
            
            # Mancha de óxido en esquinas de placa
            draw.polygon([(x1 + 12, y1 + 12), (x1 + 180, y1 + 12), (x1 + 12, y1 + 180)], fill=(160, 68, 22, 220))
            rough_map[y1+12:y1+180, x1+12:x1+180] = 0.90
            metal_map[y1+12:y1+180, x1+12:x1+180] = 0.10
    
    # Juntas cruciformes maestras (inlines oscuros de 20 px)
    draw.line([(1024, 0), (1024, RES)], fill=(12, 12, 12, 255), width=20)
    draw.line([(0, 1024), (RES, 1024)], fill=(12, 12, 12, 255), width=20)
    hdraw.line([(1024, 0), (1024, RES)], fill=40, width=20)
    hdraw.line([(0, 1024), (RES, 1024)], fill=40, width=20)
    ao_map[:, 1014:1034] = 0.15
    ao_map[1014:1034, :] = 0.15
    
    base.save(f"{prefix}_BaseColor.png")
    h_smooth = height_img.filter(ImageFilter.GaussianBlur(radius=2.0))
    normal_img = height_to_normal(np.array(h_smooth, dtype=np.float32) / 255.0, strength=6.0)
    normal_img.save(f"{prefix}_Normal.png")
    pack_orm(ao_map, rough_map, metal_map).save(f"{prefix}_ORM.png")
    emissive.save(f"{prefix}_Emissive.png")
    print(f"[OK] Generado T_Steel_Plates V2 completo")

# ==============================================================================
# 4. GRATING WALKWAY V2 (Malla Calada con Mayor Escala y Legibilidad)
# ==============================================================================
def generate_grating_walkway_v2():
    prefix = os.path.join(OUTPUT_DIR, "T_Grating_Walkway")
    base = Image.new("RGBA", (RES, RES), (30, 28, 26, 255))
    draw = ImageDraw.Draw(base)
    
    height_img = Image.new("L", (RES, RES), 30)
    hdraw = ImageDraw.Draw(height_img)
    
    ao_map = np.full((RES, RES), 0.35, dtype=np.float32)
    rough_map = np.full((RES, RES), 0.50, dtype=np.float32)
    metal_map = np.full((RES, RES), 0.92, dtype=np.float32)
    emissive = Image.new("RGB", (RES, RES), (0, 0, 0))
    
    # Marco exterior reforzado de 120 px
    bw = 120
    draw.rectangle([(0, 0), (RES, bw)], fill=(85, 82, 80, 255))
    draw.rectangle([(0, RES - bw), (RES, RES)], fill=(85, 82, 80, 255))
    draw.rectangle([(0, 0), (bw, RES)], fill=(85, 82, 80, 255))
    draw.rectangle([(RES - bw, 0), (RES, RES)], fill=(85, 82, 80, 255))
    
    hdraw.rectangle([(0, 0), (RES, bw)], fill=210)
    hdraw.rectangle([(0, RES - bw), (RES, RES)], fill=210)
    hdraw.rectangle([(0, 0), (bw, RES)], fill=210)
    hdraw.rectangle([(RES - bw, 0), (RES, RES)], fill=210)
    
    # Pernos en marco
    for p in range(60, RES, 120):
        for y_pos in [60, RES - 60]:
            draw.ellipse([(p-12, y_pos-12), (p+12, y_pos+12)], fill=(12, 12, 12, 255))
            draw.ellipse([(p-9, y_pos-9), (p+8, y_pos+8)], fill=(170, 165, 160, 255))
            hdraw.ellipse([(p-10, y_pos-10), (p+10, y_pos+10)], fill=255)
        for x_pos in [60, RES - 60]:
            draw.ellipse([(x_pos-12, p-12), (x_pos+12, p+12)], fill=(12, 12, 12, 255))
            draw.ellipse([(x_pos-9, p-9), (x_pos+8, p+8)], fill=(170, 165, 160, 255))
            hdraw.ellipse([(x_pos-10, p-10), (x_pos+10, p+10)], fill=255)
            
    # Malla de acero en rombos más anchos (paso de 64 px para máxima legibilidad 3D)
    step = 64
    mesh_steel = (140, 135, 130, 255)
    for x in range(bw, RES - bw, step):
        for y in range(bw, RES - bw, step):
            cx = x + step // 2
            cy = y + step // 2
            r = step // 2 - 4
            pts = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
            draw.polygon(pts, fill=mesh_steel, outline=(14, 14, 14, 255))
            hdraw.polygon(pts, fill=225)
            
            # Hueco central ocluido
            ir = r - 12
            ipts = [(cx, cy - ir), (cx + ir, cy), (cx, cy + ir), (cx - ir, cy)]
            draw.polygon(ipts, fill=(16, 14, 12, 255))
            hdraw.polygon(ipts, fill=20)
            
    base.save(f"{prefix}_BaseColor.png")
    h_smooth = height_img.filter(ImageFilter.GaussianBlur(radius=1.6))
    normal_img = height_to_normal(np.array(h_smooth, dtype=np.float32) / 255.0, strength=6.5)
    normal_img.save(f"{prefix}_Normal.png")
    ao_map = np.clip(np.array(h_smooth, dtype=np.float32) / 255.0 * 0.8 + 0.2, 0.1, 1.0)
    pack_orm(ao_map, rough_map, metal_map).save(f"{prefix}_ORM.png")
    emissive.save(f"{prefix}_Emissive.png")
    print(f"[OK] Generado T_Grating_Walkway V2 completo")

# ==============================================================================
# 5. PROPS MACHINERY V2 (Pantalla CRT, Manómetros y Tubería con Layout Óptimo)
# ==============================================================================
def generate_props_machinery_v2():
    prefix = os.path.join(OUTPUT_DIR, "T_Props_Machinery")
    base = Image.new("RGBA", (RES, RES), (42, 44, 48, 255))
    draw = ImageDraw.Draw(base)
    
    height_img = Image.new("L", (RES, RES), 130)
    hdraw = ImageDraw.Draw(height_img)
    
    ao_map = np.ones((RES, RES), dtype=np.float32)
    rough_map = np.full((RES, RES), 0.50, dtype=np.float32)
    metal_map = np.full((RES, RES), 0.75, dtype=np.float32)
    
    emissive = Image.new("RGB", (RES, RES), (0, 0, 0))
    edraw = ImageDraw.Draw(emissive)
    
    # CUADRANTE 1 (0..1024, 0..1024): Manómetro Analógico de Latón
    cx, cy = 512, 512
    draw.ellipse([(cx - 440, cy - 440), (cx + 440, cy + 440)], fill=(205, 155, 45, 255), outline=(14, 14, 14, 255), width=12)
    hdraw.ellipse([(cx - 440, cy - 440), (cx + 440, cy + 440)], fill=220)
    
    draw.ellipse([(cx - 360, cy - 360), (cx + 360, cy + 360)], fill=(240, 235, 225, 255), outline=(16, 16, 16, 255), width=8)
    hdraw.ellipse([(cx - 360, cy - 360), (cx + 360, cy + 360)], fill=160)
    
    for deg in range(0, 360, 10):
        rad = math.radians(deg)
        length = 38 if deg % 30 == 0 else 20
        w = 6 if deg % 30 == 0 else 3
        p1 = (cx + int(340 * math.cos(rad)), cy + int(340 * math.sin(rad)))
        p2 = (cx + int((340 - length) * math.cos(rad)), cy + int((340 - length) * math.sin(rad)))
        draw.line([p1, p2], fill=(20, 20, 20, 255), width=w)
        
    rad_needle = math.radians(225)
    p_needle = (cx + int(290 * math.cos(rad_needle)), cy + int(290 * math.sin(rad_needle)))
    draw.line([(cx, cy), p_needle], fill=(215, 25, 18, 255), width=10)
    draw.ellipse([(cx - 28, cy - 28), (cx + 28, cy + 28)], fill=(14, 14, 14, 255))
    draw.ellipse([(cx - 18, cy - 18), (cx + 18, cy + 18)], fill=(210, 205, 200, 255))
    hdraw.ellipse([(cx - 22, cy - 22), (cx + 22, cy + 22)], fill=250)
    
    font_dial = get_font(42, bold=True)
    draw.text((cx - 95, cy + 120), "BAR x 100", fill=(20, 20, 20, 255), font=font_dial)
    draw.text((cx - 130, cy + 175), "ASTRA VAPOR", fill=(190, 20, 15, 255), font=font_dial)
    
    rough_map[0:1024, 0:1024] = 0.22
    metal_map[0:1024, 0:1024] = 0.88
    
    # CUADRANTE 2 (1024..2048, 0..1024): Monitor CRT de Fósforo Verde
    draw.rectangle([(1060, 40), (2008, 980)], fill=(30, 32, 35, 255), outline=(14, 14, 14, 255), width=12)
    hdraw.rectangle([(1060, 40), (2008, 980)], fill=190)
    
    draw.rectangle([(1120, 100), (1948, 920)], fill=(6, 25, 10, 255), outline=(16, 45, 20, 255), width=8)
    hdraw.rectangle([(1120, 100), (1948, 920)], fill=165)
    
    edraw.rectangle([(1120, 100), (1948, 920)], fill=(6, 25, 10))
    for gx in range(1120, 1948, 64):
        edraw.line([(gx, 100), (gx, 920)], fill=(15, 68, 25), width=1)
    for gy in range(100, 920, 64):
        edraw.line([(1120, gy), (1948, gy)], fill=(15, 68, 25), width=1)
        
    pts_sine = []
    for sx in range(1140, 1930, 8):
        sy = int(510 + math.sin((sx - 1140) * 0.04) * 140 + math.cos((sx - 1140) * 0.1) * 35)
        pts_sine.append((sx, sy))
    for i in range(len(pts_sine) - 1):
        edraw.line([pts_sine[i], pts_sine[i+1]], fill=(45, 255, 65), width=5)
        draw.line([pts_sine[i], pts_sine[i+1]], fill=(45, 255, 65, 255), width=5)
        
    font_crt = get_font(38, bold=True)
    edraw.text((1150, 130), "TELEMETRÍA SECTOR 07: ACTIVO", fill=(45, 255, 65), font=font_crt)
    edraw.text((1150, 185), "PRESIÓN VAPOR: 98.4% [ESTABLE]", fill=(120, 255, 140), font=font_crt)
    draw.text((1150, 130), "TELEMETRÍA SECTOR 07: ACTIVO", fill=(45, 255, 65, 255), font=font_crt)
    draw.text((1150, 185), "PRESIÓN VAPOR: 98.4% [ESTABLE]", fill=(120, 255, 140, 255), font=font_crt)
    
    rough_map[0:1024, 1024:2048] = 0.18
    metal_map[0:1024, 1024:2048] = 0.12
    
    # CUADRANTE 3 (0..1024, 1024..2048): Botón de Parada de Emergencia y Balizas
    draw.rectangle([(40, 1060), (980, 2008)], fill=(65, 62, 58, 255), outline=(14, 14, 14, 255), width=10)
    hdraw.rectangle([(40, 1060), (980, 2008)], fill=150)
    
    bx, by = 340, 1530
    draw.ellipse([(bx - 170, by - 170), (bx + 170, by + 170)], fill=(245, 195, 25, 255), outline=(14, 14, 14, 255), width=10)
    draw.ellipse([(bx - 140, by - 140), (bx + 140, by + 140)], fill=(215, 25, 18, 255), outline=(12, 12, 12, 255), width=8)
    hdraw.ellipse([(bx - 140, by - 140), (bx + 140, by + 140)], fill=250)
    font_btn = get_font(34, bold=True)
    draw.text((bx - 120, by - 16), "PARADA", fill=(255, 255, 255, 255), font=font_btn)
    draw.text((bx - 140, by + 24), "EMERGENCIA", fill=(255, 255, 255, 255), font=font_btn)
    
    for ly, col, ecol in [(1230, (255, 30, 20, 255), (255, 30, 20)), (1380, (245, 190, 20, 255), (245, 190, 20)), (1750, (30, 225, 45, 255), (30, 225, 45))]:
        draw.ellipse([(720, ly), (810, ly + 90)], fill=col, outline=(14, 14, 14, 255), width=8)
        edraw.ellipse([(720, ly), (810, ly + 90)], fill=ecol)
        hdraw.ellipse([(720, ly), (810, ly + 90)], fill=235)
        
    # CUADRANTE 4 (1024..2048, 1024..2048): Tuberías de Bronce Corrugado y Bridas
    draw.rectangle([(1024, 1024), (RES, RES)], fill=(32, 34, 38, 255))
    py1, py2 = 1220, 1620
    draw.rectangle([(1024, py1), (RES, py2)], fill=(175, 105, 48, 255))
    for px in range(1024, RES, 48):
        draw.line([(px, py1), (px, py2)], fill=(115, 62, 25, 255), width=5)
        draw.line([(px + 4, py1), (px + 4, py2)], fill=(225, 150, 80, 255), width=3)
        hdraw.line([(px, py1), (px, py2)], fill=215, width=6)
        
    for fx in [1280, 1720]:
        draw.rectangle([(fx - 28, py1 - 35), (fx + 28, py2 + 35)], fill=(80, 80, 85, 255), outline=(14, 14, 14, 255), width=8)
        hdraw.rectangle([(fx - 28, py1 - 35), (fx + 28, py2 + 35)], fill=245)
        for by in range(py1 - 18, py2 + 30, 56):
            draw.ellipse([(fx - 9, by - 9), (fx + 9, by + 9)], fill=(12, 12, 12, 255))
            draw.ellipse([(fx - 6, by - 6), (fx + 6, by + 6)], fill=(195, 195, 195, 255))
            hdraw.ellipse([(fx - 7, by - 7), (fx + 7, by + 7)], fill=255)
            
    base.save(f"{prefix}_BaseColor.png")
    h_smooth = height_img.filter(ImageFilter.GaussianBlur(radius=1.8))
    normal_img = height_to_normal(np.array(h_smooth, dtype=np.float32) / 255.0, strength=6.0)
    normal_img.save(f"{prefix}_Normal.png")
    pack_orm(ao_map, rough_map, metal_map).save(f"{prefix}_ORM.png")
    emissive.save(f"{prefix}_Emissive.png")
    print(f"[OK] Generado T_Props_Machinery V2 completo")

def main():
    print("=== INICIANDO GENERACIÓN PBR V2 MEJORADA ===")
    generate_trim_industrial_v2()
    generate_concrete_factory_v2()
    generate_steel_plates_v2()
    generate_grating_walkway_v2()
    generate_props_machinery_v2()
    print("=== TODAS LAS TEXTURAS PBR V2 GENERADAS CON ÉXITO ===")

if __name__ == "__main__":
    main()

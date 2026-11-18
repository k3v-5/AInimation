# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Generador Maestro de Texturas Modulares PBR Estilizadas (Fase Industrial & Fábrica)
# Produce mapas BaseColor (con inlines/desgaste), Normal (tangent-space), ORM (AO/Roughness/Metallic) y Emissive en 2048x2048.

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

def height_to_normal(height_array, strength=4.0):
    """
    Convierte un array 2D de altura float32 [0.0, 1.0] a un mapa de normales tangent-space RGB [0..255].
    Formato estándar Unreal Engine (X+, Y-, Z+ / Tangent space).
    """
    h, w = height_array.shape
    # Gradientes Sobel
    gy, gx = np.gradient(height_array)
    # Escalar por fuerza
    gx = -gx * strength
    gy = gy * strength  # DirectX / Unreal (eje Y invertido respecto a OpenGL)
    gz = np.ones_like(gx)
    
    # Normalizar vector
    norm = np.sqrt(gx**2 + gy**2 + gz**2)
    norm = np.maximum(norm, 1e-6)
    nx = gx / norm
    ny = gy / norm
    nz = gz / norm
    
    # Mapear [-1, 1] a [0, 255]
    r = np.clip((nx * 0.5 + 0.5) * 255.0, 0, 255).astype(np.uint8)
    g = np.clip((ny * 0.5 + 0.5) * 255.0, 0, 255).astype(np.uint8)
    b = np.clip((nz * 0.5 + 0.5) * 255.0, 0, 255).astype(np.uint8)
    
    normal_img = np.stack([r, g, b], axis=-1)
    return Image.fromarray(normal_img, mode="RGB")

def pack_orm(ao_array, roughness_array, metallic_array):
    """
    Empaqueta AO (R), Roughness (G) y Metallic (B) en un único mapa de imagen RGB.
    """
    r = np.clip(ao_array * 255.0, 0, 255).astype(np.uint8)
    g = np.clip(roughness_array * 255.0, 0, 255).astype(np.uint8)
    b = np.clip(metallic_array * 255.0, 0, 255).astype(np.uint8)
    orm_img = np.stack([r, g, b], axis=-1)
    return Image.fromarray(orm_img, mode="RGB")

# ==============================================================================
# 1. TRIM SHEET MAESTRO INDUSTRIAL (T_Trim_Industrial_PBR)
# ==============================================================================
def generate_trim_industrial_pbr():
    prefix = os.path.join(OUTPUT_DIR, "T_Trim_Industrial")
    
    base = Image.new("RGBA", (RES, RES), (48, 45, 42, 255))
    draw = ImageDraw.Draw(base)
    
    height_img = Image.new("L", (RES, RES), 128)
    hdraw = ImageDraw.Draw(height_img)
    
    ao_map = np.ones((RES, RES), dtype=np.float32)
    rough_map = np.full((RES, RES), 0.65, dtype=np.float32)
    metal_map = np.full((RES, RES), 0.85, dtype=np.float32)
    
    emissive = Image.new("RGB", (RES, RES), (0, 0, 0))
    edraw = ImageDraw.Draw(emissive)
    
    # -------------------------------------------------------------
    # BANDA 1: Franja Hazard Chevrons (y: 0 - 256)
    # -------------------------------------------------------------
    yellow = (245, 190, 20, 255)
    black = (22, 22, 24, 255)
    for x in range(-500, RES + 600, 128):
        draw.polygon([(x, 0), (x + 64, 0), (x + 64 - 256, 256), (x - 256, 256)], fill=black)
        draw.polygon([(x + 64, 0), (x + 128, 0), (x + 128 - 256, 256), (x + 64 - 256, 256)], fill=yellow)
    
    # Bordes con línea negra gruesa de entintado (inlines)
    draw.rectangle([(0, 0), (RES, 14)], fill=(12, 12, 12, 255))
    draw.rectangle([(0, 242), (RES, 256)], fill=(12, 12, 12, 255))
    hdraw.rectangle([(0, 0), (RES, 14)], fill=80)
    hdraw.rectangle([(0, 242), (RES, 256)], fill=80)
    
    # Desgaste y arañazos en franja hazard
    for sx in [120, 340, 780, 1100, 1450, 1820]:
        draw.line([(sx, 40), (sx + 80, 190)], fill=(70, 68, 65, 255), width=3)
        draw.line([(sx + 5, 40), (sx + 85, 190)], fill=(12, 12, 12, 255), width=1)
    
    rough_map[0:256, :] = 0.55
    metal_map[0:256, :] = 0.25  # Pintura sobre metal
    ao_map[0:14, :] = 0.3
    ao_map[242:256, :] = 0.3
    
    # -------------------------------------------------------------
    # BANDA 2: Placas de Acero Pesado y Remaches (y: 256 - 768)
    # -------------------------------------------------------------
    steel_base = (78, 76, 74, 255)
    draw.rectangle([(0, 256), (RES, 768)], fill=steel_base)
    hdraw.rectangle([(0, 256), (RES, 768)], fill=150)
    
    # Juntas verticales de placa cada 512px con inlines oscuros y bisel de luz
    for px in range(0, RES, 512):
        draw.rectangle([(px - 4, 256), (px + 4, 768)], fill=(15, 15, 15, 255))
        draw.line([(px + 5, 256), (px + 5, 768)], fill=(140, 138, 135, 255), width=2)
        hdraw.rectangle([(px - 4, 256), (px + 4, 768)], fill=70)
        ao_map[256:768, max(0, px - 8):min(RES, px + 8)] = 0.2
    
    # Junta horizontal central
    draw.rectangle([(0, 508), (RES, 516)], fill=(15, 15, 15, 255))
    draw.line([(0, 517), (RES, 517)], fill=(140, 138, 135, 255), width=2)
    hdraw.rectangle([(0, 508), (RES, 516)], fill=70)
    ao_map[506:518, :] = 0.2
    
    # Remaches reforzados con relieve y AO
    for py in [285, 485, 540, 740]:
        for px in range(32, RES, 64):
            # BaseColor
            draw.ellipse([(px - 11, py - 11), (px + 11, py + 11)], fill=(18, 18, 18, 255))
            draw.ellipse([(px - 9, py - 9), (px + 8, py + 8)], fill=(125, 120, 115, 255))
            draw.ellipse([(px - 6, py - 6), (px + 4, py + 4)], fill=(185, 180, 175, 255))
            # Height
            hdraw.ellipse([(px - 10, py - 10), (px + 10, py + 10)], fill=230)
            # Roughness / Metal
            rough_map[py-10:py+10, px-10:px+10] = 0.35
            metal_map[py-10:py+10, px-10:px+10] = 0.95
    
    # Pátina de óxido naranja hand-painted
    rust_col = (165, 68, 22, 230)
    for rx in [160, 680, 1220, 1740]:
        draw.polygon([(rx, 512), (rx + 85, 512), (rx + 115, 710), (rx - 25, 710)], fill=rust_col)
        rough_map[512:710, rx-20:rx+100] = 0.92
        metal_map[512:710, rx-20:rx+100] = 0.05
    
    rough_map[256:768, :] = np.where(rough_map[256:768, :] > 0.8, rough_map[256:768, :], 0.48)
    metal_map[256:768, :] = np.where(metal_map[256:768, :] < 0.2, metal_map[256:768, :], 0.88)
    
    # -------------------------------------------------------------
    # BANDA 3: Rejilla Perforada Diamond Mesh (y: 768 - 1280)
    # -------------------------------------------------------------
    grate_bg = (24, 22, 20, 255)
    draw.rectangle([(0, 768), (RES, 1280)], fill=grate_bg)
    hdraw.rectangle([(0, 768), (RES, 1280)], fill=40)
    
    mesh_color = (135, 130, 125, 255)
    mesh_line_dark = (14, 14, 14, 255)
    for x in range(-500, RES + 600, 32):
        draw.line([(x, 768), (x + 512, 1280)], fill=mesh_line_dark, width=5)
        draw.line([(x + 2, 768), (x + 514, 1280)], fill=mesh_color, width=2)
        draw.line([(x + 512, 768), (x, 1280)], fill=mesh_line_dark, width=5)
        draw.line([(x + 514, 768), (x + 2, 1280)], fill=mesh_color, width=2)
        
        hdraw.line([(x, 768), (x + 512, 1280)], fill=200, width=4)
        hdraw.line([(x + 512, 768), (x, 1280)], fill=200, width=4)
    
    # Marcos de contención superior e inferior
    draw.rectangle([(0, 768), (RES, 792)], fill=(65, 62, 58, 255), outline=(12, 12, 12, 255), width=3)
    draw.rectangle([(0, 1256), (RES, 1280)], fill=(65, 62, 58, 255), outline=(12, 12, 12, 255), width=3)
    hdraw.rectangle([(0, 768), (RES, 792)], fill=180)
    hdraw.rectangle([(0, 1256), (RES, 1280)], fill=180)
    
    rough_map[768:1280, :] = 0.52
    metal_map[768:1280, :] = 0.92
    ao_map[792:1256, :] = 0.45  # Cavidad de rejilla oscura
    
    # -------------------------------------------------------------
    # BANDA 4: Paneles Estarcidos y Rótulos Industriales (y: 1280 - 1664)
    # -------------------------------------------------------------
    panel_bg = (210, 160, 22, 255) # Amarillo ocre industrial
    draw.rectangle([(0, 1280), (RES, 1664)], fill=panel_bg)
    hdraw.rectangle([(0, 1280), (RES, 1664)], fill=140)
    
    font_large = get_font(68, bold=True)
    font_med = get_font(42, bold=True)
    font_small = get_font(30, bold=True)
    
    # Rótulos en negro profundo de cómic
    ink_black = (14, 14, 16, 255)
    draw.text((70, 1315), "FACTORÍA SECTOR 07", fill=ink_black, font=font_large)
    draw.text((1050, 1315), "VAPOR // ALTA PRESIÓN", fill=(175, 25, 20, 255), font=font_large)
    draw.text((70, 1425), "PRESIÓN MÁX: 350 BAR [AUTORIZADO]", fill=(40, 35, 20, 255), font=font_med)
    draw.text((1050, 1425), "PELIGRO DE ASFIXIA: PURGA ACTIVA", fill=ink_black, font=font_med)
    draw.text((70, 1530), "VÁLVULAS DE SEGURIDAD N-12 Y N-14", fill=(55, 45, 25, 255), font=font_small)
    draw.text((1200, 1530), "[ CÓDIGO OPERACIONAL HAZ-740 ]", fill=ink_black, font=font_small)
    
    # Luz indicadora emisiva en la banda
    edraw.ellipse([(1930, 1330), (1970, 1370)], fill=(255, 30, 10)) # Piloto rojo de peligro
    draw.ellipse([(1926, 1326), (1974, 1374)], fill=(12, 12, 12, 255))
    draw.ellipse([(1930, 1330), (1970, 1370)], fill=(255, 60, 30, 255))
    hdraw.ellipse([(1930, 1330), (1970, 1370)], fill=210)
    
    rough_map[1280:1664, :] = 0.60
    metal_map[1280:1664, :] = 0.20
    
    # -------------------------------------------------------------
    # BANDA 5: Chapa Corrugada Naval con Remaches de Onda (y: 1664 - 2048)
    # -------------------------------------------------------------
    draw.rectangle([(0, 1664), (RES, 2048)], fill=(40, 68, 105, 255))
    for cx in range(0, RES, 64):
        # Gradiente de altura de onda corrugada
        draw.rectangle([(cx, 1664), (cx + 32, 2048)], fill=(28, 50, 80, 255))
        draw.rectangle([(cx + 32, 1664), (cx + 64, 2048)], fill=(55, 90, 135, 255))
        draw.line([(cx, 1664), (cx, 2048)], fill=(12, 22, 40, 255), width=3)
        draw.line([(cx + 32, 1664), (cx + 32, 2048)], fill=(75, 120, 175, 255), width=2)
        
        # Height map sinusoidal para mapa de normales
        hdraw.rectangle([(cx, 1664), (cx + 32, 2048)], fill=90)
        hdraw.rectangle([(cx + 32, 1664), (cx + 64, 2048)], fill=200)
    
    draw.text((60, 1720), "ASTRA HAZARD // REFINERÍA", fill=(225, 230, 240, 255), font=font_large)
    draw.text((60, 1830), "DEPÓSITO ESTRUCTURAL #07", fill=(245, 195, 30, 255), font=font_med)
    draw.text((60, 1920), "CAPACIDAD: 120.000 L // FLUIDO CLASE 4", fill=(180, 200, 225, 255), font=font_small)
    
    rough_map[1664:2048, :] = 0.45
    metal_map[1664:2048, :] = 0.85
    
    # Renderizar mapas y guardar
    base.save(f"{prefix}_BaseColor.png")
    
    # Suavizado de bordes en mapa de altura antes del cálculo de normales
    height_smoothed = height_img.filter(ImageFilter.GaussianBlur(radius=1.8))
    h_arr = np.array(height_smoothed, dtype=np.float32) / 255.0
    
    normal_img = height_to_normal(h_arr, strength=5.5)
    normal_img.save(f"{prefix}_Normal.png")
    
    orm_img = pack_orm(ao_map, rough_map, metal_map)
    orm_img.save(f"{prefix}_ORM.png")
    
    emissive.save(f"{prefix}_Emissive.png")
    print(f"[OK] Generado pack PBR completo: {prefix}_[BaseColor/Normal/ORM/Emissive].png")

# ==============================================================================
# 2. ATLAS DE HORMIGÓN Y CEMENTO CON GRIETAS (T_Concrete_Factory_PBR)
# ==============================================================================
def generate_concrete_factory_pbr():
    prefix = os.path.join(OUTPUT_DIR, "T_Concrete_Factory")
    
    base = Image.new("RGBA", (RES, RES), (110, 108, 105, 255))
    draw = ImageDraw.Draw(base)
    
    height_img = Image.new("L", (RES, RES), 128)
    hdraw = ImageDraw.Draw(height_img)
    
    ao_map = np.ones((RES, RES), dtype=np.float32)
    rough_map = np.full((RES, RES), 0.90, dtype=np.float32)
    metal_map = np.zeros((RES, RES), dtype=np.float32) # Hormigón es 100% dieléctrico
    emissive = Image.new("RGB", (RES, RES), (0, 0, 0))
    
    # Micro-ruido de grano de hormigón
    np.random.seed(42)
    noise = (np.random.rand(RES, RES) * 35 - 17).astype(np.int16)
    concrete_base_rgb = np.array(base.convert("RGB"), dtype=np.int16)
    concrete_base_rgb[:, :, 0] = np.clip(concrete_base_rgb[:, :, 0] + noise, 0, 255)
    concrete_base_rgb[:, :, 1] = np.clip(concrete_base_rgb[:, :, 1] + noise, 0, 255)
    concrete_base_rgb[:, :, 2] = np.clip(concrete_base_rgb[:, :, 2] + noise, 0, 255)
    base = Image.fromarray(concrete_base_rgb.astype(np.uint8), mode="RGB")
    draw = ImageDraw.Draw(base)
    
    # Grietas estructurales profundas de cómic (inlines oscuros)
    cracks = [
        [(200, 0), (280, 420), (380, 800), (320, 1250), (450, 1800), (520, 2048)],
        [(1400, 0), (1320, 350), (1450, 720), (1600, 1100), (1520, 1600), (1680, 2048)],
        [(0, 950), (450, 1020), (950, 980), (1400, 1080), (2048, 1020)],
        [(650, 600), (820, 850), (1100, 920)],
        [(1150, 1300), (1350, 1550), (1480, 1850)]
    ]
    
    for crack in cracks:
        for i in range(len(crack) - 1):
            p1 = crack[i]
            p2 = crack[i+1]
            draw.line([p1, p2], fill=(18, 18, 18), width=7)
            draw.line([p1, p2], fill=(45, 42, 40), width=3)
            # Altura negativa (hendidura profunda)
            hdraw.line([p1, p2], fill=30, width=8)
            hdraw.line([p1, p2], fill=10, width=4)
    
    # Manchas de aceite y humedad industrial
    stain_col = (55, 52, 48)
    for cx, cy, r in [(500, 600, 240), (1300, 1400, 320), (850, 1650, 180), (1650, 450, 210)]:
        draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], fill=stain_col)
        rough_map[max(0, cy-r):min(RES, cy+r), max(0, cx-r):min(RES, cx+r)] = 0.55 # Aceite más reflectante
    
    base.save(f"{prefix}_BaseColor.png")
    
    h_smooth = height_img.filter(ImageFilter.GaussianBlur(radius=2.2))
    h_arr = np.array(h_smooth, dtype=np.float32) / 255.0
    normal_img = height_to_normal(h_arr, strength=6.0)
    normal_img.save(f"{prefix}_Normal.png")
    
    # AO en grietas
    h_crack_mask = (np.array(height_img) < 80).astype(np.float32)
    ao_map = 1.0 - (h_crack_mask * 0.75)
    
    orm_img = pack_orm(ao_map, rough_map, metal_map)
    orm_img.save(f"{prefix}_ORM.png")
    
    emissive.save(f"{prefix}_Emissive.png")
    print(f"[OK] Generado pack PBR completo: {prefix}_[BaseColor/Normal/ORM/Emissive].png")

# ==============================================================================
# 3. ATLAS DE REJILLAS Y PASARELAS CALADAS (T_Grating_Walkway_PBR)
# ==============================================================================
def generate_grating_walkway_pbr():
    prefix = os.path.join(OUTPUT_DIR, "T_Grating_Walkway")
    
    base = Image.new("RGBA", (RES, RES), (32, 30, 28, 255))
    draw = ImageDraw.Draw(base)
    
    height_img = Image.new("L", (RES, RES), 30)
    hdraw = ImageDraw.Draw(height_img)
    
    ao_map = np.full((RES, RES), 0.35, dtype=np.float32)
    rough_map = np.full((RES, RES), 0.55, dtype=np.float32)
    metal_map = np.full((RES, RES), 0.90, dtype=np.float32)
    emissive = Image.new("RGB", (RES, RES), (0, 0, 0))
    
    # Marco exterior de vigas perimetrales
    beam_w = 96
    draw.rectangle([(0, 0), (RES, beam_w)], fill=(75, 72, 70, 255))
    draw.rectangle([(0, RES - beam_w), (RES, RES)], fill=(75, 72, 70, 255))
    draw.rectangle([(0, 0), (beam_w, RES)], fill=(75, 72, 70, 255))
    draw.rectangle([(RES - beam_w, 0), (RES, RES)], fill=(75, 72, 70, 255))
    
    hdraw.rectangle([(0, 0), (RES, beam_w)], fill=200)
    hdraw.rectangle([(0, RES - beam_w), (RES, RES)], fill=200)
    hdraw.rectangle([(0, 0), (beam_w, RES)], fill=200)
    hdraw.rectangle([(RES - beam_w, 0), (RES, RES)], fill=200)
    
    # Remaches en los marcos
    for p in range(48, RES, 96):
        # Superior e inferior
        draw.ellipse([(p-9, 48-9), (p+9, 48+9)], fill=(15, 15, 15, 255))
        draw.ellipse([(p-7, 48-7), (p+6, 48+6)], fill=(160, 155, 150, 255))
        hdraw.ellipse([(p-8, 48-8), (p+8, 48+8)], fill=255)
        
        draw.ellipse([(p-9, RES-48-9), (p+9, RES-48+9)], fill=(15, 15, 15, 255))
        draw.ellipse([(p-7, RES-48-7), (p+6, RES-48+6)], fill=(160, 155, 150, 255))
        hdraw.ellipse([(p-8, RES-48-8), (p+8, RES-48+8)], fill=255)
    
    # Patrón de rejilla interna en rombos de acero entrelazado
    step = 48
    steel_grate = (120, 115, 110, 255)
    for x in range(beam_w, RES - beam_w, step):
        for y in range(beam_w, RES - beam_w, step):
            # Rombo metálico
            cx = x + step // 2
            cy = y + step // 2
            r = step // 2 - 4
            pts = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
            draw.polygon(pts, fill=steel_grate, outline=(18, 18, 18, 255))
            hdraw.polygon(pts, fill=220)
            
            # Orificio central hueco
            inner_r = r - 10
            ipts = [(cx, cy - inner_r), (cx + inner_r, cy), (cx, cy + inner_r), (cx - inner_r, cy)]
            draw.polygon(ipts, fill=(18, 16, 15, 255))
            hdraw.polygon(ipts, fill=20)
    
    base.save(f"{prefix}_BaseColor.png")
    
    h_smooth = height_img.filter(ImageFilter.GaussianBlur(radius=1.5))
    h_arr = np.array(h_smooth, dtype=np.float32) / 255.0
    normal_img = height_to_normal(h_arr, strength=6.5)
    normal_img.save(f"{prefix}_Normal.png")
    
    ao_map = np.clip(h_arr * 0.8 + 0.2, 0.1, 1.0)
    orm_img = pack_orm(ao_map, rough_map, metal_map)
    orm_img.save(f"{prefix}_ORM.png")
    
    emissive.save(f"{prefix}_Emissive.png")
    print(f"[OK] Generado pack PBR completo: {prefix}_[BaseColor/Normal/ORM/Emissive].png")

# ==============================================================================
# 4. ATLAS DE PLACAS DE ACERO Y VIGAS I (T_Steel_Plates_PBR)
# ==============================================================================
def generate_steel_plates_pbr():
    prefix = os.path.join(OUTPUT_DIR, "T_Steel_Plates")
    
    base = Image.new("RGBA", (RES, RES), (65, 62, 60, 255))
    draw = ImageDraw.Draw(base)
    
    height_img = Image.new("L", (RES, RES), 140)
    hdraw = ImageDraw.Draw(height_img)
    
    ao_map = np.ones((RES, RES), dtype=np.float32)
    rough_map = np.full((RES, RES), 0.48, dtype=np.float32)
    metal_map = np.full((RES, RES), 0.92, dtype=np.float32)
    emissive = Image.new("RGB", (RES, RES), (0, 0, 0))
    
    # Cuadrícula de 4 grandes placas de acero pesado soldadas (1024x1024 cada una)
    grid_coords = [0, 1024, 2048]
    for i in range(len(grid_coords) - 1):
        for j in range(len(grid_coords) - 1):
            x1, x2 = grid_coords[i], grid_coords[i+1]
            y1, y2 = grid_coords[j], grid_coords[j+1]
            
            # Bisel perimetral de placa
            draw.rectangle([(x1 + 8, y1 + 8), (x2 - 8, y2 - 8)], outline=(12, 12, 12, 255), width=6)
            hdraw.rectangle([(x1 + 8, y1 + 8), (x2 - 8, y2 - 8)], fill=180)
            
            # Doble hilera de remaches perimetrales
            for rx in range(x1 + 48, x2 - 40, 64):
                for ry in [y1 + 48, y2 - 48]:
                    draw.ellipse([(rx - 10, ry - 10), (rx + 10, ry + 10)], fill=(12, 12, 12, 255))
                    draw.ellipse([(rx - 7, ry - 7), (rx + 6, ry + 6)], fill=(160, 155, 150, 255))
                    hdraw.ellipse([(rx - 8, ry - 8), (rx + 8, ry + 8)], fill=240)
            for ry in range(y1 + 48, y2 - 40, 64):
                for rx in [x1 + 48, x2 - 48]:
                    draw.ellipse([(rx - 10, ry - 10), (rx + 10, ry + 10)], fill=(12, 12, 12, 255))
                    draw.ellipse([(rx - 7, ry - 7), (rx + 6, ry + 6)], fill=(160, 155, 150, 255))
                    hdraw.ellipse([(rx - 8, ry - 8), (rx + 8, ry + 8)], fill=240)
            
            # Cordón de soldadura diagonal
            draw.line([(x1 + 300, y1 + 100), (x1 + 450, y1 + 250)], fill=(185, 180, 175, 255), width=8)
            draw.line([(x1 + 300, y1 + 100), (x1 + 450, y1 + 250)], fill=(20, 20, 20, 255), width=2)
            hdraw.line([(x1 + 300, y1 + 100), (x1 + 450, y1 + 250)], fill=220, width=8)
    
    # Juntas principales profundas (inlines negros)
    draw.line([(1024, 0), (1024, RES)], fill=(10, 10, 10, 255), width=16)
    draw.line([(0, 1024), (RES, 1024)], fill=(10, 10, 10, 255), width=16)
    hdraw.line([(1024, 0), (1024, RES)], fill=40, width=16)
    hdraw.line([(0, 1024), (RES, 1024)], fill=40, width=16)
    
    ao_map[:, 1016:1032] = 0.2
    ao_map[1016:1032, :] = 0.2
    
    base.save(f"{prefix}_BaseColor.png")
    
    h_smooth = height_img.filter(ImageFilter.GaussianBlur(radius=2.0))
    h_arr = np.array(h_smooth, dtype=np.float32) / 255.0
    normal_img = height_to_normal(h_arr, strength=6.0)
    normal_img.save(f"{prefix}_Normal.png")
    
    orm_img = pack_orm(ao_map, rough_map, metal_map)
    orm_img.save(f"{prefix}_ORM.png")
    
    emissive.save(f"{prefix}_Emissive.png")
    print(f"[OK] Generado pack PBR completo: {prefix}_[BaseColor/Normal/ORM/Emissive].png")

# ==============================================================================
# 5. ATLAS DE PROPS Y MAQUINARIA DE CONTROL (T_Props_Machinery_PBR)
# ==============================================================================
def generate_props_machinery_pbr():
    prefix = os.path.join(OUTPUT_DIR, "T_Props_Machinery")
    
    base = Image.new("RGBA", (RES, RES), (40, 42, 45, 255))
    draw = ImageDraw.Draw(base)
    
    height_img = Image.new("L", (RES, RES), 128)
    hdraw = ImageDraw.Draw(height_img)
    
    ao_map = np.ones((RES, RES), dtype=np.float32)
    rough_map = np.full((RES, RES), 0.55, dtype=np.float32)
    metal_map = np.full((RES, RES), 0.70, dtype=np.float32)
    
    emissive = Image.new("RGB", (RES, RES), (0, 0, 0))
    edraw = ImageDraw.Draw(emissive)
    
    # -------------------------------------------------------------
    # CUADRANTE 1 (0..1024, 0..1024): Diales Analógicos y Manómetros
    # -------------------------------------------------------------
    cx, cy = 512, 512
    r_outer = 440
    # Bisel de latón exterior
    draw.ellipse([(cx - r_outer, cy - r_outer), (cx + r_outer, cy + r_outer)], fill=(195, 145, 45, 255), outline=(15, 15, 15, 255), width=10)
    hdraw.ellipse([(cx - r_outer, cy - r_outer), (cx + r_outer, cy + r_outer)], fill=210)
    
    # Carátula blanca con desgaste
    r_inner = 360
    draw.ellipse([(cx - r_inner, cy - r_inner), (cx + r_inner, cy + r_inner)], fill=(235, 230, 220, 255), outline=(18, 18, 18, 255), width=8)
    hdraw.ellipse([(cx - r_inner, cy - r_inner), (cx + r_inner, cy + r_inner)], fill=150)
    
    # Marcas radiales del manómetro
    for deg in range(0, 360, 10):
        rad = math.radians(deg)
        length = 35 if deg % 30 == 0 else 18
        w = 5 if deg % 30 == 0 else 2
        p1 = (cx + int((r_inner - 20) * math.cos(rad)), cy + int((r_inner - 20) * math.sin(rad)))
        p2 = (cx + int((r_inner - 20 - length) * math.cos(rad)), cy + int((r_inner - 20 - length) * math.sin(rad)))
        draw.line([p1, p2], fill=(22, 22, 22, 255), width=w)
    
    # Aguja indicadora roja
    rad_needle = math.radians(220)
    p_needle = (cx + int((r_inner - 50) * math.cos(rad_needle)), cy + int((r_inner - 50) * math.sin(rad_needle)))
    draw.line([(cx, cy), p_needle], fill=(210, 25, 20, 255), width=8)
    draw.ellipse([(cx - 24, cy - 24), (cx + 24, cy + 24)], fill=(18, 18, 18, 255))
    draw.ellipse([(cx - 16, cy - 16), (cx + 16, cy + 16)], fill=(200, 195, 190, 255))
    hdraw.ellipse([(cx - 20, cy - 20), (cx + 20, cy + 20)], fill=240)
    
    # Rótulo del dial
    font_dial = get_font(38, bold=True)
    draw.text((cx - 85, cy + 120), "BAR x 100", fill=(25, 25, 25, 255), font=font_dial)
    draw.text((cx - 110, cy + 175), "ASTRA VAPOR", fill=(180, 25, 20, 255), font=font_dial)
    
    rough_map[0:1024, 0:1024] = 0.25 # Vidrio pulido
    metal_map[0:1024, 0:1024] = 0.85
    
    # -------------------------------------------------------------
    # CUADRANTE 2 (1024..2048, 0..1024): Pantalla CRT Fósforo Verde
    # -------------------------------------------------------------
    # Marco de monitor
    draw.rectangle([(1060, 40), (2008, 980)], fill=(32, 35, 38, 255), outline=(12, 12, 12, 255), width=10)
    hdraw.rectangle([(1060, 40), (2008, 980)], fill=190)
    
    # Cristal CRT abombado verde oscuro
    draw.rectangle([(1120, 100), (1948, 920)], fill=(8, 28, 12, 255), outline=(18, 45, 22, 255), width=6)
    hdraw.rectangle([(1120, 100), (1948, 920)], fill=160)
    
    # Rejilla osciloscopio y radar
    edraw.rectangle([(1120, 100), (1948, 920)], fill=(5, 22, 10))
    for gx in range(1120, 1948, 64):
        edraw.line([(gx, 100), (gx, 920)], fill=(15, 65, 25), width=1)
    for gy in range(100, 920, 64):
        edraw.line([(1120, gy), (1948, gy)], fill=(15, 65, 25), width=1)
    
    # Curva senoidal y telemetría brillante (Emissive)
    points_sine = []
    for sx in range(1140, 1930, 8):
        sy = int(510 + math.sin((sx - 1140) * 0.04) * 140 + math.cos((sx - 1140) * 0.1) * 35)
        points_sine.append((sx, sy))
    for i in range(len(points_sine) - 1):
        edraw.line([points_sine[i], points_sine[i+1]], fill=(45, 255, 65), width=4)
        draw.line([points_sine[i], points_sine[i+1]], fill=(45, 255, 65, 255), width=4)
    
    font_crt = get_font(36, bold=True)
    edraw.text((1150, 130), "SISTEMA TELEMETRÍA SECTOR 07: ACTIVO", fill=(45, 255, 65), font=font_crt)
    edraw.text((1150, 180), "PRESIÓN VAPOR: 98.4% [ESTABLE]", fill=(120, 255, 140), font=font_crt)
    draw.text((1150, 130), "SISTEMA TELEMETRÍA SECTOR 07: ACTIVO", fill=(45, 255, 65, 255), font=font_crt)
    draw.text((1150, 180), "PRESIÓN VAPOR: 98.4% [ESTABLE]", fill=(120, 255, 140, 255), font=font_crt)
    
    rough_map[0:1024, 1024:2048] = 0.20
    metal_map[0:1024, 1024:2048] = 0.10
    
    # -------------------------------------------------------------
    # CUADRANTE 3 (0..1024, 1024..2048): Botones de Emergencia y Válvulas
    # -------------------------------------------------------------
    draw.rectangle([(40, 1060), (980, 2008)], fill=(65, 60, 55, 255), outline=(12, 12, 12, 255), width=8)
    hdraw.rectangle([(40, 1060), (980, 2008)], fill=150)
    
    # Botón tipo hongo rojo de parada de emergencia
    bx, by = 300, 1500
    r_btn = 150
    draw.ellipse([(bx - r_btn - 20, by - r_btn - 20), (bx + r_btn + 20, by + r_btn + 20)], fill=(240, 195, 25, 255), outline=(15, 15, 15, 255), width=8)
    draw.ellipse([(bx - r_btn, by - r_btn), (bx + r_btn, by + r_btn)], fill=(210, 25, 20, 255), outline=(12, 12, 12, 255), width=6)
    hdraw.ellipse([(bx - r_btn, by - r_btn), (bx + r_btn, by + r_btn)], fill=245)
    
    font_btn = get_font(32, bold=True)
    draw.text((bx - 120, by - 16), "PARADA EMERGENCIA", fill=(255, 255, 255, 255), font=font_btn)
    
    # Luces piloto LED emisivas
    for ly, col, ecol in [(1250, (255, 30, 20, 255), (255, 30, 20)), (1380, (245, 190, 20, 255), (245, 190, 20)), (1750, (30, 220, 45, 255), (30, 220, 45))]:
        draw.ellipse([(700, ly), (790, ly + 90)], fill=col, outline=(12, 12, 12, 255), width=6)
        edraw.ellipse([(700, ly), (790, ly + 90)], fill=ecol)
        hdraw.ellipse([(700, ly), (790, ly + 90)], fill=230)
    
    # -------------------------------------------------------------
    # CUADRANTE 4 (1024..2048, 1024..2048): Tuberías Corrugadas y Juntas
    # -------------------------------------------------------------
    draw.rectangle([(1024, 1024), (RES, RES)], fill=(35, 38, 42, 255))
    # Tubería horizontal gruesa
    pipe_y1, pipe_y2 = 1200, 1600
    draw.rectangle([(1024, pipe_y1), (RES, pipe_y2)], fill=(160, 95, 45, 255)) # Cobre/bronce industrial
    for px in range(1024, RES, 48):
        draw.line([(px, pipe_y1), (px, pipe_y2)], fill=(110, 60, 25, 255), width=4)
        draw.line([(px + 4, pipe_y1), (px + 4, pipe_y2)], fill=(210, 140, 75, 255), width=2)
        hdraw.line([(px, pipe_y1), (px, pipe_y2)], fill=210, width=6)
    
    # Bridas de acople reforzadas
    for fx in [1280, 1720]:
        draw.rectangle([(fx - 24, pipe_y1 - 30), (fx + 24, pipe_y2 + 30)], fill=(75, 75, 78, 255), outline=(12, 12, 12, 255), width=6)
        hdraw.rectangle([(fx - 24, pipe_y1 - 30), (fx + 24, pipe_y2 + 30)], fill=240)
        # Pernos de brida
        for by in range(pipe_y1 - 15, pipe_y2 + 25, 55):
            draw.ellipse([(fx - 8, by - 8), (fx + 8, by + 8)], fill=(15, 15, 15, 255))
            draw.ellipse([(fx - 5, by - 5), (fx + 5, by + 5)], fill=(185, 185, 185, 255))
            hdraw.ellipse([(fx - 6, by - 6), (fx + 6, by + 6)], fill=255)
    
    base.save(f"{prefix}_BaseColor.png")
    
    h_smooth = height_img.filter(ImageFilter.GaussianBlur(radius=1.8))
    h_arr = np.array(h_smooth, dtype=np.float32) / 255.0
    normal_img = height_to_normal(h_arr, strength=6.0)
    normal_img.save(f"{prefix}_Normal.png")
    
    orm_img = pack_orm(ao_map, rough_map, metal_map)
    orm_img.save(f"{prefix}_ORM.png")
    
    emissive.save(f"{prefix}_Emissive.png")
    print(f"[OK] Generado pack PBR completo: {prefix}_[BaseColor/Normal/ORM/Emissive].png")

def main():
    print("=== INICIANDO GENERACIÓN MAESTRA DE TEXTURAS PBR MODULARES ===")
    generate_trim_industrial_pbr()
    generate_concrete_factory_pbr()
    generate_grating_walkway_pbr()
    generate_steel_plates_pbr()
    generate_props_machinery_pbr()
    print("=== TODAS LAS FAMILIAS PBR INDUSTRIALES GENERADAS CON ÉXITO ===")

if __name__ == "__main__":
    main()

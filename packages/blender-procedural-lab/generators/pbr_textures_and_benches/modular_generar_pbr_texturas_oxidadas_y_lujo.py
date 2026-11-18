# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Generador Maestro de Texturas Modulares PBR V2: Pack Derelict/Oxidado (5) y Pack Luxury Art Déco (5)
# Generación procedural de alta calidad con sombreado de dos tonos, pátina orgánica,
# relieves normales profundos y empaquetado ORM para Unreal Engine 5.

import os
import math
import shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUTPUT_DIR = r"F:\Dev\Game\Art\Textures\Modular"
ARTIFACT_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\b59ff04f-3c21-4ee5-94b0-8e8f899f8923"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(ARTIFACT_DIR, exist_ok=True)

RES = 2048

def height_to_normal(height_array, strength=4.5):
    """
    Convierte array de altura float32 [0.0..1.0] a mapa de normales tangent-space RGB.
    DirectX / Unreal: Eje Y invertido (+X derecha, -Y abajo, +Z arriba).
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

def save_and_export_maps(prefix, base_img, normal_img, orm_img, emissive_img):
    bc_path = f"{prefix}_BaseColor.png"
    n_path = f"{prefix}_Normal.png"
    orm_path = f"{prefix}_ORM.png"
    emi_path = f"{prefix}_Emissive.png"
    
    base_img.save(bc_path)
    normal_img.save(n_path)
    orm_img.save(orm_path)
    emissive_img.save(emi_path)
    
    shutil.copy(bc_path, os.path.join(ARTIFACT_DIR, os.path.basename(bc_path)))
    shutil.copy(n_path, os.path.join(ARTIFACT_DIR, os.path.basename(n_path)))
    shutil.copy(orm_path, os.path.join(ARTIFACT_DIR, os.path.basename(orm_path)))
    shutil.copy(emi_path, os.path.join(ARTIFACT_DIR, os.path.basename(emi_path)))
    print(f"  [OK] Exportados mapas para: {os.path.basename(prefix)}")

def make_fractal_noise(shape, octaves=4, persistence=0.5, seed=42):
    np.random.seed(seed)
    noise = np.zeros(shape, dtype=np.float32)
    h, w = shape
    freq = 1.0
    amp = 1.0
    total_amp = 0.0
    for o in range(octaves):
        scale = max(2, int(w // (freq * 8)))
        low_res = np.random.rand(max(2, h // scale), max(2, w // scale)).astype(np.float32)
        img = Image.fromarray(low_res).resize((w, h), Image.Resampling.BILINEAR)
        noise += np.array(img) * amp
        total_amp += amp
        amp *= persistence
        freq *= 2.0
    return noise / total_amp

# ==============================================================================
# SECCIÓN I: 5 PACKS OXIDADOS / PERCUTIDOS (DERELICT & BATTLE-WORN)
# ==============================================================================

# 1. T_Derelict_Rust_Plates
def generate_derelict_rust_plates():
    print("[1/10] Generando T_Derelict_Rust_Plates V2...")
    prefix = os.path.join(OUTPUT_DIR, "T_Derelict_Rust_Plates")
    
    rust_macro = make_fractal_noise((RES, RES), octaves=4, persistence=0.55, seed=111)
    rust_micro = make_fractal_noise((RES, RES), octaves=6, persistence=0.65, seed=112)
    pitting = make_fractal_noise((RES, RES), octaves=7, persistence=0.70, seed=113)
    
    paint_col = np.array([52, 62, 50], dtype=np.float32)      # Verde militar desgastado
    paint_chipped = np.array([28, 34, 26], dtype=np.float32)  # Borde oscuro de pintura
    raw_metal = np.array([145, 140, 135], dtype=np.float32)   # Acero raspado brillante
    rust_bright = np.array([195, 82, 22], dtype=np.float32)   # Óxido naranja vivo
    rust_dark = np.array([84, 32, 12], dtype=np.float32)      # Costra de óxido profunda
    
    rust_mask = np.clip((rust_macro * 0.7 + rust_micro * 0.3 - 0.40) / 0.18, 0.0, 1.0)
    deep_rust = np.clip((rust_micro - 0.50) / 0.25, 0.0, 1.0) * rust_mask
    
    rust_color = rust_dark[None, None, :] * (1.0 - deep_rust[:, :, None]) + rust_bright[None, None, :] * deep_rust[:, :, None]
    albedo = paint_col[None, None, :] * (1.0 - rust_mask[:, :, None]) + rust_color * rust_mask[:, :, None]
    
    # Bordes descascarados con halo metálico
    edge_peel = np.exp(-((rust_mask - 0.5)**2) / 0.04)
    albedo = albedo * (1.0 - edge_peel[:, :, None] * 0.6) + raw_metal[None, None, :] * (edge_peel[:, :, None] * 0.6)
    
    # Agregar cuadrícula de 4 paneles de blindaje pesado con juntas biseladas
    base_img = Image.fromarray(np.clip(albedo, 0, 255).astype(np.uint8), mode="RGB")
    draw = ImageDraw.Draw(base_img)
    
    # Juntas centrales
    draw.line([(RES // 2, 0), (RES // 2, RES)], fill=(12, 12, 14), width=10)
    draw.line([(0, RES // 2), (RES, RES // 2)], fill=(12, 12, 14), width=10)
    
    # Remaches con escorrentía de óxido vertical
    for rx in range(128, RES, 256):
        for ry in [70, RES // 2 - 70, RES // 2 + 70, RES - 70]:
            # Chorretón de óxido cayendo del remache
            draw.line([(rx, ry), (rx, min(RES, ry + 160))], fill=(110, 42, 16), width=8)
            draw.line([(rx - 1, ry), (rx - 1, min(RES, ry + 120))], fill=(165, 68, 22), width=4)
            # Cabeza de remache
            draw.ellipse([(rx - 18, ry - 18), (rx + 18, ry + 18)], fill=(30, 22, 18), outline=(10, 8, 6), width=3)
            draw.ellipse([(rx - 10, ry - 10), (rx + 10, ry + 10)], fill=(160, 65, 22))
            
    # Altura
    height = 0.58 - rust_mask * 0.22 - pitting * deep_rust * 0.18 + (1.0 - rust_mask) * 0.08
    h_img = Image.fromarray((height * 255).astype(np.uint8), mode="L")
    hdraw = ImageDraw.Draw(h_img)
    hdraw.line([(RES // 2, 0), (RES // 2, RES)], fill=45, width=10)
    hdraw.line([(0, RES // 2), (RES, RES // 2)], fill=45, width=10)
    for rx in range(128, RES, 256):
        for ry in [70, RES // 2 - 70, RES // 2 + 70, RES - 70]:
            hdraw.ellipse([(rx - 18, ry - 18), (rx + 18, ry + 18)], fill=200)
            
    height_array = np.array(h_img, dtype=np.float32) / 255.0
    normal_img = height_to_normal(height_array, strength=5.8)
    
    ao_map = np.clip(1.0 - deep_rust * 0.45 - (1.0 - height_array) * 0.35, 0.20, 1.0)
    rough_map = np.clip(0.45 * (1.0 - rust_mask) + 0.92 * rust_mask + pitting * 0.08, 0.25, 0.98)
    metal_map = np.clip(0.08 * rust_mask + 0.75 * (1.0 - rust_mask) * (1.0 - deep_rust), 0.0, 0.85)
    orm_img = pack_orm(ao_map, rough_map, metal_map)
    
    emissive_img = Image.new("RGB", (RES, RES), (0, 0, 0))
    save_and_export_maps(prefix, base_img, normal_img, orm_img, emissive_img)

# 2. T_Battered_Armor_Impacts
def generate_battered_armor_impacts():
    print("[2/10] Generando T_Battered_Armor_Impacts V2...")
    prefix = os.path.join(OUTPUT_DIR, "T_Battered_Armor_Impacts")
    
    # Blindaje de acero balístico con abolladuras, raspaduras de metralla y cráteres orgánicos
    base_img = Image.new("RGB", (RES, RES), (62, 65, 72))
    draw = ImageDraw.Draw(base_img)
    
    # Cuadrícula de 2 grandes mamparos acorazados con cordón de unión biselado
    draw.line([(RES // 2, 0), (RES // 2, RES)], fill=(16, 18, 22), width=14)
    # Hileras de remaches balísticos perimetrales
    for y in range(80, RES, 160):
        for x in [80, RES // 2 - 60, RES // 2 + 60, RES - 80]:
            draw.ellipse([(x - 14, y - 14), (x + 14, y + 14)], fill=(40, 42, 48), outline=(12, 14, 16), width=3)
            draw.ellipse([(x - 8, y - 8), (x + 8, y + 8)], fill=(140, 145, 155))
            
    height = np.full((RES, RES), 0.62, dtype=np.float32)
    ao_map = np.ones((RES, RES), dtype=np.float32)
    rough_map = np.full((RES, RES), 0.40, dtype=np.float32)
    metal_map = np.full((RES, RES), 0.92, dtype=np.float32)
    
    # Arañazos profundos por abrasión angular
    np.random.seed(222)
    for _ in range(80):
        x1, y1 = np.random.randint(0, RES, 2)
        angle = np.random.uniform(0, math.pi * 2)
        length = np.random.randint(60, 320)
        x2 = int(x1 + math.cos(angle) * length)
        y2 = int(y1 + math.sin(angle) * length)
        draw.line([(x1, y1), (x2, y2)], fill=(195, 200, 210), width=3)
        draw.line([(x1 + 2, y1 + 2), (x2 + 2, y2 + 2)], fill=(15, 16, 18), width=1)
        
    # Impactos orgánicos balísticos irregulares (no círculos perfectos)
    impact_centers = [
        (450, 480, 140, 1.2), (1500, 380, 160, 0.9), (980, 1150, 190, 1.4),
        (320, 1480, 120, 0.8), (1680, 1350, 150, 1.1), (820, 420, 110, 1.3),
        (1300, 1620, 130, 0.7), (400, 950, 105, 1.0)
    ]
    
    yy, xx = np.indices((RES, RES))
    impact_noise = make_fractal_noise((RES, RES), octaves=5, persistence=0.6, seed=223)
    
    for cx, cy, rad, aspect in impact_centers:
        # Distancia elíptica distorsionada por ruido fractal
        dx = (xx - cx) / aspect
        dy = (yy - cy)
        dist = np.sqrt(dx**2 + dy**2) * (1.0 + (impact_noise - 0.5) * 0.45)
        
        in_core = dist < rad * 0.45
        in_cavity = (dist >= rad * 0.45) & (dist < rad * 0.9)
        in_rim = (dist >= rad * 0.9) & (dist < rad * 1.35)
        in_halo = (dist >= rad * 1.35) & (dist < rad * 2.2)
        
        # Geometría: cráter cóncavo con reborde levantado
        depth_fac = np.clip(1.0 - (dist / rad), 0.0, 1.0)
        height[dist < rad] -= depth_fac[dist < rad] * 0.48
        rim_fac = np.clip(1.0 - np.abs(dist - rad * 1.1) / (rad * 0.25), 0.0, 1.0)
        height[in_rim] += rim_fac[in_rim] * 0.26
        
        # Color:
        # Núcleo: metal fundido oscuro quemado
        arr_rgb = np.array(base_img)
        arr_rgb[in_core] = [22, 22, 25]
        # Cavidad: acero vivo brillante raspado
        arr_rgb[in_cavity] = [175, 180, 192]
        # Reborde: metal quemado con rebaba
        arr_rgb[in_rim] = [75, 78, 88]
        # Halo: hollín y pintura quemada
        arr_rgb[in_halo] = (arr_rgb[in_halo] * 0.65).astype(np.uint8)
        base_img = Image.fromarray(arr_rgb)
        draw = ImageDraw.Draw(base_img)
        
        # Grietas radiales angulares saliendo del impacto
        for a in np.linspace(0, math.pi * 2, 10, endpoint=False):
            jitter = np.random.uniform(0.7, 1.5)
            gx = int(cx + math.cos(a) * rad * 1.8 * jitter * aspect)
            gy = int(cy + math.sin(a) * rad * 1.8 * jitter)
            draw.line([(cx + int(math.cos(a) * rad * 0.4), cy + int(math.sin(a) * rad * 0.4)), (gx, gy)], fill=(12, 14, 16), width=3)
            
        rough_map[in_cavity] = 0.18 # Acero virgen reflectante
        rough_map[in_halo] = 0.88   # Pintura quemada mate
        metal_map[in_cavity] = 0.98
        metal_map[in_halo] = 0.35
        ao_map[in_core] = 0.25
        
    height = np.clip(height, 0.0, 1.0)
    normal_img = height_to_normal(height, strength=6.2)
    orm_img = pack_orm(ao_map, rough_map, metal_map)
    emissive_img = Image.new("RGB", (RES, RES), (0, 0, 0))
    save_and_export_maps(prefix, base_img, normal_img, orm_img, emissive_img)

# 3. T_Corroded_Acid_Pipes
def generate_corroded_acid_pipes():
    print("[3/10] Generando T_Corroded_Acid_Pipes V2...")
    prefix = os.path.join(OUTPUT_DIR, "T_Corroded_Acid_Pipes")
    
    # Metal base con corrosión química por ácido fluorhídrico y pátina de sulfato
    acid_noise1 = make_fractal_noise((RES, RES), octaves=6, persistence=0.6, seed=331)
    acid_noise2 = make_fractal_noise((RES, RES), octaves=5, persistence=0.55, seed=332)
    
    pipe_metal = np.array([72, 68, 64], dtype=np.float32)
    acid_verdigris = np.array([32, 130, 88], dtype=np.float32)   # Pátina turquesa ácida
    sulfur_crust = np.array([185, 178, 88], dtype=np.float32)    # Costra amarillenta
    corroded_flesh = np.array([38, 22, 16], dtype=np.float32)    # Cavidad carcomida oscura
    
    acid_mask = np.clip((acid_noise1 - 0.38) / 0.22, 0.0, 1.0)
    crust_mask = np.clip((acid_noise2 - 0.55) / 0.20, 0.0, 1.0) * acid_mask
    deep_pitting = (acid_noise1 > 0.70)
    
    albedo = pipe_metal[None, None, :] * (1.0 - acid_mask[:, :, None]) + acid_verdigris[None, None, :] * acid_mask[:, :, None]
    albedo = albedo * (1.0 - crust_mask[:, :, None]) + sulfur_crust[None, None, :] * crust_mask[:, :, None]
    albedo[deep_pitting] = corroded_flesh
    
    base_img = Image.fromarray(np.clip(albedo, 0, 255).astype(np.uint8), mode="RGB")
    draw = ImageDraw.Draw(base_img)
    
    # 3 Bridas de tubería con remaches reforzados
    for by in [420, 1024, 1620]:
        # Sombra y marco de brida
        draw.rectangle([(0, by - 28), (RES, by + 28)], fill=(42, 44, 40), outline=(14, 16, 14), width=4)
        for bx in range(80, RES, 160):
            draw.ellipse([(bx - 14, by - 14), (bx + 14, by + 14)], fill=(125, 135, 105), outline=(12, 15, 12), width=2)
            
    # Goteos verticales de ácido derramado
    for dx in [280, 720, 1240, 1780]:
        draw.line([(dx, 0), (dx + 15, RES)], fill=(28, 115, 75), width=18)
        draw.line([(dx + 4, 0), (dx + 19, RES)], fill=(160, 195, 90), width=6)
        
    height = 0.55 - acid_mask * 0.28 - deep_pitting * 0.18 + (1.0 - acid_mask) * 0.10
    normal_img = height_to_normal(height, strength=6.0)
    
    ao_map = np.clip(1.0 - acid_mask * 0.45 - deep_pitting * 0.35, 0.18, 1.0)
    rough_map = np.clip(0.48 * (1.0 - acid_mask) + 0.90 * crust_mask + 0.24 * (acid_mask * (1.0 - crust_mask)), 0.20, 0.98)
    metal_map = np.clip(0.82 * (1.0 - acid_mask) + 0.12 * acid_mask, 0.0, 0.85)
    orm_img = pack_orm(ao_map, rough_map, metal_map)
    
    # Fuga ácida fosforescente sutil
    emissive = np.zeros((RES, RES, 3), dtype=np.uint8)
    emissive[deep_pitting] = [45, 235, 120]
    emissive_img = Image.fromarray(emissive, mode="RGB").filter(ImageFilter.GaussianBlur(radius=4))
    
    save_and_export_maps(prefix, base_img, normal_img, orm_img, emissive_img)

# 4. T_Decayed_Rusted_Grating
def generate_decayed_rusted_grating():
    print("[4/10] Generando T_Decayed_Rusted_Grating V2...")
    prefix = os.path.join(OUTPUT_DIR, "T_Decayed_Rusted_Grating")
    
    # Fondo: vacío industrial oscuro de pozo de maquinaria
    base_img = Image.new("RGB", (RES, RES), (15, 14, 14))
    draw = ImageDraw.Draw(base_img)
    
    height = np.zeros((RES, RES), dtype=np.float32)
    ao_map = np.full((RES, RES), 0.12, dtype=np.float32)
    rough_map = np.full((RES, RES), 0.92, dtype=np.float32)
    metal_map = np.full((RES, RES), 0.15, dtype=np.float32)
    
    # Malla de rombo diamantado con sectores destruidos
    step = 80
    half = step // 2
    rust_noise = make_fractal_noise((RES, RES), octaves=4, persistence=0.55, seed=444)
    
    # Agujero masivo corroído central
    yy, xx = np.indices((RES, RES))
    dist_hole = np.sqrt((xx - 1024)**2 + (yy - 1024)**2) * (1.0 + (rust_noise - 0.5) * 0.5)
    
    for y in range(0, RES + step, step):
        for x in range(0, RES + step, step):
            dh = dist_hole[min(y, RES-1), min(x, RES-1)]
            if dh < 450:
                # Agujero central: barras rotas y curvadas hacia abajo
                if np.random.rand() < 0.25:
                    draw.line([(x - half, y), (x + 10, y + 25)], fill=(125, 48, 18), width=10)
                continue
                
            r_val = rust_noise[min(y, RES-1), min(x, RES-1)]
            bar_color = (165, 68, 22) if r_val > 0.42 else (88, 86, 84)
            
            # Rombo continuo con barras dobles
            draw.polygon([(x, y - half), (x + half, y), (x, y + half), (x - half, y)], outline=bar_color, width=12)
            draw.line([(x - half, y), (x + half, y)], fill=bar_color, width=6)
            
            # Altura
            x0, x1 = max(0, x - half), min(RES, x + half)
            y0, y1 = max(0, y - half), min(RES, y + half)
            height[y0:y1, x0:x1] = np.maximum(height[y0:y1, x0:x1], 0.72)
            ao_map[y0:y1, x0:x1] = 0.85
            rough_map[y0:y1, x0:x1] = 0.80 if r_val > 0.42 else 0.45
            metal_map[y0:y1, x0:x1] = 0.20 if r_val > 0.42 else 0.80
            
    # Marco de viga pesada perimetral
    draw.rectangle([(0, 0), (RES, 90)], fill=(85, 42, 20), outline=(12, 10, 8), width=8)
    draw.rectangle([(0, RES - 90), (RES, RES)], fill=(85, 42, 20), outline=(12, 10, 8), width=8)
    height[:90, :] = 0.88
    height[RES-90:, :] = 0.88
    ao_map[:90, :] = 0.95
    ao_map[RES-90:, :] = 0.95
    
    # Pernos oxidados
    for px in range(100, RES, 200):
        draw.ellipse([(px - 22, 45 - 22), (px + 22, 45 + 22)], fill=(35, 18, 12), outline=(10, 8, 6), width=3)
        draw.ellipse([(px - 22, RES - 45 - 22), (px + 22, RES - 45 + 22)], fill=(35, 18, 12), outline=(10, 8, 6), width=3)
        
    normal_img = height_to_normal(height, strength=5.5)
    orm_img = pack_orm(ao_map, rough_map, metal_map)
    emissive_img = Image.new("RGB", (RES, RES), (0, 0, 0))
    save_and_export_maps(prefix, base_img, normal_img, orm_img, emissive_img)

# 5. T_Scorched_Plasma_Slag
def generate_scorched_plasma_slag():
    print("[5/10] Generando T_Scorched_Plasma_Slag V2...")
    prefix = os.path.join(OUTPUT_DIR, "T_Scorched_Plasma_Slag")
    
    # Chapa de blindaje con quemaduras de plasma orgánicas y gradiente de temple térmico
    slag_noise = make_fractal_noise((RES, RES), octaves=5, persistence=0.6, seed=551)
    wave_noise = make_fractal_noise((RES, RES), octaves=4, persistence=0.5, seed=552)
    
    albedo = np.full((RES, RES, 3), [78, 80, 88], dtype=np.float32) # Acero base
    height = np.full((RES, RES), 0.55, dtype=np.float32)
    rough_map = np.full((RES, RES), 0.38, dtype=np.float32)
    metal_map = np.full((RES, RES), 0.92, dtype=np.float32)
    emissive = np.zeros((RES, RES, 3), dtype=np.float32)
    
    yy, xx = np.indices((RES, RES))
    # Trayectoria de impacto de plasma orgánico (no círculos)
    blasts = [
        (650, 750, 520, 1.3),
        (1450, 1250, 580, 0.8),
        (1200, 480, 380, 1.1)
    ]
    
    for bx, by, brad, aspect in blasts:
        dx = (xx - bx) / aspect
        dy = (yy - by)
        dist = np.sqrt(dx**2 + dy**2) * (1.0 + (wave_noise - 0.5) * 0.4)
        norm_d = np.clip(dist / brad, 0.0, 1.0)
        
        # Gradiente suave de temple térmico
        # Carbón negro en el epicentro
        c_mask = norm_d < 0.30
        albedo[c_mask] = [20, 20, 22]
        rough_map[c_mask] = 0.92
        metal_map[c_mask] = 0.20
        height[c_mask] -= 0.15
        
        # Azul eléctrico de temple
        b_mask = (norm_d >= 0.30) & (norm_d < 0.50)
        albedo[b_mask] = [38, 72, 175]
        rough_map[b_mask] = 0.15
        
        # Púrpura/magenta
        p_mask = (norm_d >= 0.50) & (norm_d < 0.70)
        albedo[p_mask] = [115, 42, 135]
        rough_map[p_mask] = 0.20
        
        # Ámbar dorado
        a_mask = (norm_d >= 0.70) & (norm_d < 0.95)
        albedo[a_mask] = [190, 128, 38]
        rough_map[a_mask] = 0.26
        
    # Salpicaduras orgánicas de escoria fundida solidificada
    slag_mask = (slag_noise > 0.64)
    albedo[slag_mask] = [32, 28, 26]
    height[slag_mask] += 0.38
    rough_map[slag_mask] = 0.85
    metal_map[slag_mask] = 0.35
    
    # Núcleos incandescentes de escoria viva
    for bx, by, brad, _ in blasts:
        dist = np.sqrt((xx - bx)**2 + (yy - by)**2)
        hot = (dist < brad * 0.40) & (slag_noise > 0.70)
        emissive[hot] = [255, 95, 20]
        albedo[hot] = [255, 145, 45]
        
    base_img = Image.fromarray(np.clip(albedo, 0, 255).astype(np.uint8), mode="RGB")
    normal_img = height_to_normal(height, strength=6.2)
    ao_map = np.clip(1.0 - (slag_noise > 0.60) * 0.4, 0.25, 1.0)
    orm_img = pack_orm(ao_map, rough_map, metal_map)
    emissive_img = Image.fromarray(np.clip(emissive, 0, 255).astype(np.uint8), mode="RGB").filter(ImageFilter.GaussianBlur(radius=2))
    save_and_export_maps(prefix, base_img, normal_img, orm_img, emissive_img)

# ==============================================================================
# SECCIÓN II: 5 PACKS DE LUJO / ART DÉCO (CRUCERO CELESTIA TIER 2)
# ==============================================================================

# 6. T_Luxury_Marble_Gold_Inlay
def generate_luxury_marble_gold_inlay():
    print("[6/10] Generando T_Luxury_Marble_Gold_Inlay V2...")
    prefix = os.path.join(OUTPUT_DIR, "T_Luxury_Marble_Gold_Inlay")
    
    # Mármol Carrara de alto brillo con vetas multi-escala orgánicas y filigrana Art Déco dorada gruesa
    m_noise1 = make_fractal_noise((RES, RES), octaves=6, persistence=0.55, seed=661)
    m_noise2 = make_fractal_noise((RES, RES), octaves=4, persistence=0.50, seed=662)
    
    yy, xx = np.indices((RES, RES))
    vein_coord = (xx * 0.0025 + yy * 0.0025 + m_noise1 * 3.5)
    vein_val = np.sin(vein_coord * math.pi)
    vein_mask = np.clip(1.0 - np.abs(vein_val) * 3.2, 0.0, 1.0)
    
    marble_base = np.array([242, 242, 240], dtype=np.float32)
    marble_vein = np.array([125, 130, 142], dtype=np.float32)
    albedo = marble_base[None, None, :] * (1.0 - vein_mask[:, :, None] * 0.50) + marble_vein[None, None, :] * (vein_mask[:, :, None] * 0.50)
    
    base_img = Image.fromarray(np.clip(albedo, 0, 255).astype(np.uint8), mode="RGB")
    draw = ImageDraw.Draw(base_img)
    
    height = np.full((RES, RES), 0.65, dtype=np.float32)
    ao_map = np.ones((RES, RES), dtype=np.float32)
    rough_map = np.full((RES, RES), 0.06, dtype=np.float32) # Mármol ultra-pulido tipo espejo
    metal_map = np.zeros((RES, RES), dtype=np.float32)
    
    gold_color = (238, 192, 52)
    gold_dark = (165, 125, 26)
    
    # Baldosón geométrico monumental Art Déco con pletinas doradas de 28px de ancho
    tile_size = RES // 2
    for tx in [0, tile_size]:
        for ty in [0, tile_size]:
            cx, cy = tx + tile_size // 2, ty + tile_size // 2
            r = tile_size // 2 - 50
            # Marco romboidal dorado ancho
            draw.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], outline=gold_color, width=28)
            draw.polygon([(cx, cy - r + 38), (cx + r - 38, cy), (cx, cy + r - 38), (cx - r + 38, cy)], outline=gold_dark, width=10)
            # Sol radiante interior
            for a in np.linspace(0, math.pi * 2, 8, endpoint=False):
                gx = int(cx + math.cos(a) * (r - 80))
                gy = int(cy + math.sin(a) * (r - 80))
                draw.line([(cx, cy), (gx, gy)], fill=gold_color, width=12)
            # Medallón central
            draw.ellipse([(cx - 32, cy - 32), (cx + 32, cy + 32)], fill=gold_color, outline=gold_dark, width=6)
            
    # Listelos exteriores dorados
    draw.rectangle([(0, 0), (RES, RES)], outline=gold_color, width=32)
    draw.line([(tile_size, 0), (tile_size, RES)], fill=gold_color, width=32)
    draw.line([(0, tile_size), (RES, tile_size)], fill=gold_color, width=32)
    
    # Detección de oro para ORM y Normal
    arr_rgb = np.array(base_img)
    is_gold = (arr_rgb[:, :, 0] > 165) & (arr_rgb[:, :, 1] > 125) & (arr_rgb[:, :, 2] < 90)
    metal_map[is_gold] = 1.0 # 100% Oro puro
    rough_map[is_gold] = 0.16 # Latón/Oro satinado
    height[is_gold] += 0.22  # Pletinas en relieve biselado
    
    normal_img = height_to_normal(height, strength=4.5)
    orm_img = pack_orm(ao_map, rough_map, metal_map)
    emissive_img = Image.new("RGB", (RES, RES), (0, 0, 0))
    save_and_export_maps(prefix, base_img, normal_img, orm_img, emissive_img)

# 7. T_Luxury_Walnut_Wood_Panels
def generate_luxury_walnut_wood_panels():
    print("[7/10] Generando T_Luxury_Walnut_Wood_Panels V2...")
    prefix = os.path.join(OUTPUT_DIR, "T_Luxury_Walnut_Wood_Panels")
    
    # Madera noble con vetas VERTICALES naturales (alineadas con los paneles)
    w_noise = make_fractal_noise((RES, RES), octaves=5, persistence=0.52, seed=771)
    yy, xx = np.indices((RES, RES))
    
    # Vetas verticales (frecuencia alta en X, ondulación suave en Y)
    grain_coord = xx * 0.015 + w_noise * 4.0
    grain_val = np.sin(grain_coord * math.pi * 2.0)
    grain_mask = np.clip(grain_val * 0.5 + 0.5, 0.0, 1.0)
    
    dark_walnut = np.array([42, 22, 12], dtype=np.float32)
    light_walnut = np.array([92, 54, 30], dtype=np.float32)
    albedo = dark_walnut[None, None, :] * (1.0 - grain_mask[:, :, None]) + light_walnut[None, None, :] * grain_mask[:, :, None]
    
    base_img = Image.fromarray(np.clip(albedo, 0, 255).astype(np.uint8), mode="RGB")
    draw = ImageDraw.Draw(base_img)
    
    height = np.full((RES, RES), 0.58, dtype=np.float32) + grain_mask * 0.04
    ao_map = np.ones((RES, RES), dtype=np.float32)
    rough_map = np.full((RES, RES), 0.20, dtype=np.float32) # Barniz caoba francés brillante
    metal_map = np.zeros((RES, RES), dtype=np.float32)
    
    gold_trim = (225, 180, 48)
    gold_dark = (150, 110, 22)
    
    # 2 Paneles de boiserie monumentales
    pw = RES // 2
    for px in [0, pw]:
        # Moldura exterior de madera biselada
        draw.rectangle([(px + 36, 36), (px + pw - 36, RES - 36)], outline=(22, 10, 4), width=18)
        # Moldura de latón dorado ancha
        draw.rectangle([(px + 62, 62), (px + pw - 62, RES - 62)], outline=gold_trim, width=14)
        draw.rectangle([(px + 76, 76), (px + pw - 76, RES - 76)], outline=gold_dark, width=6)
        
    arr_rgb = np.array(base_img)
    is_gold = (arr_rgb[:, :, 0] > 180) & (arr_rgb[:, :, 1] > 135) & (arr_rgb[:, :, 2] < 70)
    metal_map[is_gold] = 0.98
    rough_map[is_gold] = 0.16
    height[is_gold] += 0.24
    
    normal_img = height_to_normal(height, strength=4.8)
    orm_img = pack_orm(ao_map, rough_map, metal_map)
    emissive_img = Image.new("RGB", (RES, RES), (0, 0, 0))
    save_and_export_maps(prefix, base_img, normal_img, orm_img, emissive_img)

# 8. T_Luxury_ArtDeco_Gilded_Brass
def generate_luxury_artdeco_gilded_brass():
    print("[8/10] Generando T_Luxury_ArtDeco_Gilded_Brass V2...")
    prefix = os.path.join(OUTPUT_DIR, "T_Luxury_ArtDeco_Gilded_Brass")
    
    # Mosaico de abanicos solares entrelazados (Sunburst Scallop) con relieve volumétrico
    base_img = Image.new("RGB", (RES, RES), (228, 188, 62))
    draw = ImageDraw.Draw(base_img)
    
    height = np.full((RES, RES), 0.45, dtype=np.float32)
    step_y = 384
    step_x = 384
    
    # Dibujar abanicos volumétricos de arriba hacia abajo
    for row in range(-1, RES // step_y + 2):
        for col in range(-1, RES // step_x + 2):
            cx = col * step_x + (step_x // 2 if row % 2 == 1 else 0)
            cy = row * step_y
            
            # Pétalos de abanico con degradado de color y profundidad
            for rad in range(220, 30, -32):
                level = rad / 220.0
                gold_tone = (int(165 + level * 75), int(120 + level * 70), int(25 + level * 40))
                draw.arc([(cx - rad, cy - rad), (cx + rad, cy + rad)], start=0, end=180, fill=gold_tone, width=14)
                
            # Rayos biselados
            for a in np.linspace(0, math.pi, 9):
                rx2 = int(cx + math.cos(a) * 220)
                ry2 = int(cy + math.sin(a) * 220)
                draw.line([(cx, cy), (rx2, ry2)], fill=(150, 105, 24), width=6)
                draw.line([(cx + 1, cy + 1), (rx2 + 1, ry2 + 1)], fill=(245, 215, 95), width=2)
                
    arr_gray = np.array(base_img.convert("L"), dtype=np.float32) / 255.0
    height = 0.35 + arr_gray * 0.55
    normal_img = height_to_normal(height, strength=5.2)
    
    ao_map = np.clip(arr_gray * 1.15, 0.45, 1.0)
    rough_map = np.full((RES, RES), 0.22, dtype=np.float32) # Latón dorado reflectante
    metal_map = np.ones((RES, RES), dtype=np.float32)        # 100% Metal
    orm_img = pack_orm(ao_map, rough_map, metal_map)
    
    emissive_img = Image.new("RGB", (RES, RES), (0, 0, 0))
    save_and_export_maps(prefix, base_img, normal_img, orm_img, emissive_img)

# 9. T_Luxury_Quilted_Velvet_Leather
def generate_luxury_quilted_velvet_leather():
    print("[9/10] Generando T_Luxury_Quilted_Velvet_Leather V2...")
    prefix = os.path.join(OUTPUT_DIR, "T_Luxury_Quilted_Velvet_Leather")
    
    # Cuero azul medianoche noble con almohadillado capitoné volumétrico y botones de latón
    velvet_base = (24, 32, 52)
    dark_seam = (10, 14, 22)
    gold_button = (240, 195, 48)
    
    base_img = Image.new("RGB", (RES, RES), velvet_base)
    draw = ImageDraw.Draw(base_img)
    
    diamond_w = 256
    diamond_h = 360
    
    height = np.zeros((RES, RES), dtype=np.float32)
    yy, xx = np.indices((RES, RES))
    
    # Almohadillado convexo suave por rombo
    for cy in range(-diamond_h, RES + diamond_h * 2, diamond_h):
        for cx in range(-diamond_w, RES + diamond_w * 2, diamond_w):
            px = cx + (diamond_w // 2 if (cy // diamond_h) % 2 == 1 else 0)
            py = cy
            dist_x = np.abs(xx - px) / (diamond_w / 2.0)
            dist_y = np.abs(yy - py) / (diamond_h / 2.0)
            diamond_dist = dist_x + dist_y
            
            mask = diamond_dist < 1.0
            dist_clamped = np.clip(diamond_dist, 0.0, 1.0)
            pillow = np.cos(dist_clamped * math.pi * 0.5) ** 1.6
            height = np.maximum(height, pillow * 0.72 * mask)
            
            # Costuras oscuras en rombo
            draw.polygon([
                (px, py - diamond_h // 2),
                (px + diamond_w // 2, py),
                (px, py + diamond_h // 2),
                (px - diamond_w // 2, py)
            ], outline=dark_seam, width=8)
            
    # Botones dorados 3D en los vértices
    buttons = []
    for cy in range(-diamond_h, RES + diamond_h * 2, diamond_h):
        for cx in range(-diamond_w, RES + diamond_w * 2, diamond_w):
            px = cx + (diamond_w // 2 if (cy // diamond_h) % 2 == 1 else 0)
            py = cy - diamond_h // 2
            buttons.append((px, py))
            draw.ellipse([(px - 18, py - 18), (px + 18, py + 18)], fill=gold_button, outline=(140, 95, 18), width=4)
            draw.ellipse([(px - 8, py - 8), (px + 8, py + 8)], fill=(255, 220, 85))
            
    ao_map = np.clip(height * 0.75 + 0.30, 0.25, 1.0)
    rough_map = np.full((RES, RES), 0.44, dtype=np.float32) # Cuero satinado suave
    metal_map = np.zeros((RES, RES), dtype=np.float32)
    
    for bx, by in buttons:
        if 0 <= bx < RES and 0 <= by < RES:
            x0, x1 = max(0, bx - 18), min(RES, bx + 18)
            y0, y1 = max(0, by - 18), min(RES, by + 18)
            metal_map[y0:y1, x0:x1] = 1.0
            rough_map[y0:y1, x0:x1] = 0.14
            height[y0:y1, x0:x1] = 0.88
            
    normal_img = height_to_normal(height, strength=5.8)
    orm_img = pack_orm(ao_map, rough_map, metal_map)
    emissive_img = Image.new("RGB", (RES, RES), (0, 0, 0))
    save_and_export_maps(prefix, base_img, normal_img, orm_img, emissive_img)

# 10. T_Luxury_Smoked_Glass_Lattice
def generate_luxury_smoked_glass_lattice():
    print("[10/10] Generando T_Luxury_Smoked_Glass_Lattice V2...")
    prefix = os.path.join(OUTPUT_DIR, "T_Luxury_Smoked_Glass_Lattice")
    
    # Vidrio ahumado obsidiana oscuro con celosía geométrica Art Déco de latón y retroiluminación cálida
    glass_col = (20, 18, 22)
    gold_lattice = (236, 195, 52)
    gold_dark = (160, 120, 26)
    
    base_img = Image.new("RGB", (RES, RES), glass_col)
    draw = ImageDraw.Draw(base_img)
    
    height = np.full((RES, RES), 0.50, dtype=np.float32)
    ao_map = np.ones((RES, RES), dtype=np.float32)
    rough_map = np.full((RES, RES), 0.04, dtype=np.float32) # Vidrio espejo ultra-reflectante
    metal_map = np.zeros((RES, RES), dtype=np.float32)
    emissive = np.zeros((RES, RES, 3), dtype=np.uint8)
    
    grid = 512
    for gy in range(0, RES, grid):
        for gx in range(0, RES, grid):
            # Celosía de latón de 22px de ancho
            draw.rectangle([(gx + 36, gy + 36), (gx + grid - 36, gy + grid - 36)], outline=gold_lattice, width=22)
            draw.polygon([
                (gx + grid // 2, gy + 36),
                (gx + grid - 36, gy + grid // 2),
                (gx + grid // 2, gy + grid - 36),
                (gx + 36, gy + grid // 2)
            ], outline=gold_dark, width=16)
            draw.ellipse([(gx + grid // 2 - 36, gy + grid // 2 - 36), (gx + grid // 2 + 36, gy + grid // 2 + 36)], fill=gold_lattice, outline=gold_dark, width=6)
            
            # Tiras de luz emisiva ámbar difusa
            emissive[gy + 44:gy + 56, gx + 44:gx + grid - 44] = [255, 215, 140]
            emissive[gy + grid - 56:gy + grid - 44, gx + 44:gx + grid - 44] = [255, 215, 140]
            emissive[gy + 44:gy + grid - 44, gx + 44:gx + 56] = [255, 215, 140]
            emissive[gy + 44:gy + grid - 44, gx + grid - 56:gx + grid - 44] = [255, 215, 140]
            
    arr_rgb = np.array(base_img)
    is_gold = (arr_rgb[:, :, 0] > 150) & (arr_rgb[:, :, 1] > 110) & (arr_rgb[:, :, 2] < 70)
    metal_map[is_gold] = 0.98
    rough_map[is_gold] = 0.16
    height[is_gold] += 0.25
    ao_map[is_gold] = 0.90
    
    normal_img = height_to_normal(height, strength=4.8)
    orm_img = pack_orm(ao_map, rough_map, metal_map)
    emissive_img = Image.fromarray(emissive, mode="RGB").filter(ImageFilter.GaussianBlur(radius=3))
    save_and_export_maps(prefix, base_img, normal_img, orm_img, emissive_img)

def main():
    print("=== INICIANDO SÍNTESIS DE ALTA CALIDAD: 10 PACKS PBR (40 MAPAS) ===")
    generate_derelict_rust_plates()
    generate_battered_armor_impacts()
    generate_corroded_acid_pipes()
    generate_decayed_rusted_grating()
    generate_scorched_plasma_slag()
    
    generate_luxury_marble_gold_inlay()
    generate_luxury_walnut_wood_panels()
    generate_luxury_artdeco_gilded_brass()
    generate_luxury_quilted_velvet_leather()
    generate_luxury_smoked_glass_lattice()
    print("=== TODOS LOS 40 MAPAS PBR V2 GENERADOS EXITOSAMENTE ===")

if __name__ == "__main__":
    main()

"""generate_bench_textures.py
Genera proceduralmente las texturas de alta resolución para la Mesa de Crafteo:
1. T_Bench_Vortex.png: Vórtice de plasma violeta/magenta en espiral galáctica con filamentos de energía y brillo central.
2. T_Bench_HoloHUD.png: Pantalla holográfica HUD táctica con retícula circular, núcleo violeta, barras de telemetría y códigos sci-fi.
"""

import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

TEX_DIR = r"E:\Darx_Proyect\Art\Textures"
os.makedirs(TEX_DIR, exist_ok=True)

def generate_vortex_texture(output_path, size=1024):
    print(f"Generando textura de Vórtice de Plasma ({size}x{size})...")
    
    # Coordenadas normalizadas centradas en [-1, 1]
    y, x = np.ogrid[-1:1:size*1j, -1:1:size*1j]
    r = np.sqrt(x**2 + y**2)
    theta = np.arctan2(y, x)
    
    # 1. Espiral Logarítmica Suave (3 brazos helicoidales)
    spiral_arms = 3
    twist = 6.2 * np.sqrt(np.maximum(r, 0.005))
    phase = theta * spiral_arms + twist
    
    # Brazos espirales principales con caída suave
    arm1 = np.cos(phase) * 0.5 + 0.5
    arm1 = arm1 ** 2.0
    
    # Segundo conjunto de filamentos finos contra-rotantes y armónicos
    phase2 = theta * 6 + twist * 1.5
    arm2 = np.cos(phase2) * 0.5 + 0.5
    arm2 = arm2 ** 3.0
    
    # Micro-filamentos y turbulencia cósmica
    filament_noise = (np.sin(x * 30 + y * 25 + theta * 4) * np.cos(y * 28 - x * 20)) * 0.5 + 0.5
    
    # Mezcla de plasma
    plasma = arm1 * 0.65 + arm2 * 0.35 + filament_noise * arm1 * 0.25
    
    # 2. Núcleo central de alta energía (Eye of the storm)
    core_eye = np.exp(- (r / 0.12) ** 2) * 1.5
    core_ring = np.exp(- ((r - 0.18) / 0.05) ** 2) * 0.6
    
    # 3. Caída radial hacia el borde exterior (R_max = 0.85)
    falloff = np.clip((0.85 - r) / 0.38, 0.0, 1.0)
    falloff = falloff ** 1.6
    
    # Intensidad compuesta
    intensity = (plasma * 0.70 + core_eye * 0.80 + core_ring * 0.40) * falloff
    intensity = np.clip(intensity, 0.0, 1.0)
    
    # 4. Paleta de Color Gradual: Púrpura -> Neón Magenta -> Lavanda -> Blanco
    r_ch = np.clip(intensity * 1.5 - 0.08, 0, 1) * 0.95
    g_ch = np.clip((intensity - 0.45) * 1.8, 0, 1) * 0.55 + np.clip(intensity * 0.18, 0, 0.18)
    b_ch = np.clip(intensity * 1.7, 0, 1)
    
    # Realce de neón violeta
    r_ch = r_ch * 0.90 + 0.15 * intensity
    g_ch = g_ch * 0.60
    b_ch = b_ch * 1.0
    
    # Centro blanco/lavanda brillante
    bright_mask = np.clip((intensity - 0.75) / 0.25, 0, 1)
    r_ch = r_ch * (1 - bright_mask) + 1.0 * bright_mask
    g_ch = g_ch * (1 - bright_mask) + 0.92 * bright_mask
    b_ch = b_ch * (1 - bright_mask) + 1.0 * bright_mask
    
    alpha = np.clip(intensity * 1.4, 0.0, 1.0) * falloff
    
    img_array = np.zeros((size, size, 4), dtype=np.uint8)
    img_array[..., 0] = (np.clip(r_ch, 0, 1) * 255).astype(np.uint8)
    img_array[..., 1] = (np.clip(g_ch, 0, 1) * 255).astype(np.uint8)
    img_array[..., 2] = (np.clip(b_ch, 0, 1) * 255).astype(np.uint8)
    img_array[..., 3] = (np.clip(alpha, 0, 1) * 255).astype(np.uint8)
    
    img = Image.fromarray(img_array, mode='RGBA')
    glow = img.filter(ImageFilter.GaussianBlur(radius=5))
    final_img = Image.alpha_composite(glow, img)
    
    final_img.save(output_path, "PNG")
    print(f"Textura de Vórtice guardada en: {output_path}")

def generate_hud_texture(output_path, width=1600, height=1000):
    print(f"Generando textura de Holograma HUD Táctico ({width}x{height})...")
    
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Paleta de Colores HUD
    C_CYAN = (0, 240, 255, 230)
    C_CYAN_DIM = (0, 200, 230, 120)
    C_WHITE = (230, 255, 255, 240)
    C_MAGENTA = (210, 60, 255, 240)
    C_MAGENTA_CORE = (255, 140, 255, 255)
    C_BG_TINT = (2, 18, 32, 60)
    
    # 1. Fondo translúcido con marco biselado
    margin = 35
    cut = 25
    x0, y0 = margin, margin
    x1, y1 = width - margin, height - margin
    
    # Polígono del marco biselado sci-fi
    poly_pts = [
        (x0 + cut, y0), (x1 - cut, y0), (x1, y0 + cut),
        (x1, y1 - cut), (x1 - cut, y1), (x0 + cut, y1),
        (x0, y1 - cut), (x0, y0 + cut)
    ]
    draw.polygon(poly_pts, fill=C_BG_TINT, outline=C_CYAN, width=3)
    
    # Línea interior fina paralela
    in_m = 10
    poly_inner = [
        (x0 + cut + in_m*0.5, y0 + in_m), (x1 - cut - in_m*0.5, y0 + in_m), (x1 - in_m, y0 + cut + in_m*0.5),
        (x1 - in_m, y1 - cut - in_m*0.5), (x1 - cut - in_m*0.5, y1 - in_m), (x0 + cut + in_m*0.5, y1 - in_m),
        (x0 + in_m, y1 - cut - in_m*0.5), (x0 + in_m, y0 + cut + in_m*0.5)
    ]
    draw.polygon(poly_inner, outline=C_CYAN_DIM, width=1)
    
    # Esquinas reforzadas (Corner Brackets)
    br_len = 35
    for cx, cy, sx, sy in [(x0, y0, 1, 1), (x1, y0, -1, 1), (x1, y1, -1, -1), (x0, y1, 1, -1)]:
        draw.line([(cx + sx*5, cy + sy*cut + sy*5), (cx + sx*5, cy + sy*cut + sy*br_len)], fill=C_WHITE, width=4)
        draw.line([(cx + sx*cut + sx*5, cy + sy*5), (cx + sx*cut + sx*br_len, cy + sy*5)], fill=C_WHITE, width=4)
    
    # 2. Barra Superior (Header)
    draw.rectangle([x0 + 60, y0 + 15, x0 + 480, y0 + 42], fill=(0, 200, 255, 45), outline=C_CYAN, width=1)
    draw.text((x0 + 75, y0 + 20), "DARX-OS // MOLECULAR SYNTHESIS MATRIX v4.2", fill=C_WHITE)
    draw.text((x0 + 510, y0 + 20), "STATUS: [ONLINE]", fill=(120, 255, 140, 240))
    draw.text((x1 - 380, y0 + 20), "SEC_ID: 0x8F9C // DIAGNOSTIC", fill=C_CYAN)
    
    # Segmentos de telemetría superior
    for i in range(12):
        bx = x0 + 700 + i * 22
        draw.rectangle([bx, y0 + 22, bx + 14, y0 + 34], fill=C_CYAN if i < 9 else (0, 80, 100, 100))
        
    # 3. Retícula Circular Central (Fiel a la referencia)
    xc, yc = width // 2, height // 2 + 15
    
    # Anillo exterior mayor (R = 250) con marcas de graduación
    R_outer = 250
    draw.ellipse([xc - R_outer, yc - R_outer, xc + R_outer, yc + R_outer], outline=C_CYAN_DIM, width=2)
    for deg in range(0, 360, 6):
        rad = math.radians(deg)
        t_len = 14 if deg % 30 == 0 else (8 if deg % 12 == 0 else 4)
        col = C_WHITE if deg % 30 == 0 else C_CYAN
        x_a = xc + math.cos(rad) * (R_outer - t_len)
        y_a = yc + math.sin(rad) * (R_outer - t_len)
        x_b = xc + math.cos(rad) * (R_outer + 4)
        y_b = yc + math.sin(rad) * (R_outer + 4)
        draw.line([(x_a, y_a), (x_b, y_b)], fill=col, width=2 if deg % 30 == 0 else 1)
    
    # Anillo Segmentado Medio (R = 190) con arcos interrumpidos
    R_mid = 190
    draw.arc([xc - R_mid, yc - R_mid, xc + R_mid, yc + R_mid], start=15, end=75, fill=C_CYAN, width=4)
    draw.arc([xc - R_mid, yc - R_mid, xc + R_mid, yc + R_mid], start=105, end=165, fill=C_CYAN, width=4)
    draw.arc([xc - R_mid, yc - R_mid, xc + R_mid, yc + R_mid], start=195, end=255, fill=C_CYAN, width=4)
    draw.arc([xc - R_mid, yc - R_mid, xc + R_mid, yc + R_mid], start=285, end=345, fill=C_CYAN, width=4)
    
    # Anillo interior (R = 140)
    R_inner = 140
    draw.ellipse([xc - R_inner, yc - R_inner, xc + R_inner, yc + R_inner], outline=C_CYAN, width=2)
    cross_gap = 60
    cross_ext = 210
    draw.line([(xc - cross_ext, yc), (xc - cross_gap, yc)], fill=C_CYAN_DIM, width=1)
    draw.line([(xc + cross_gap, yc), (xc + cross_ext, yc)], fill=C_CYAN_DIM, width=1)
    draw.line([(xc, yc - cross_ext), (xc, yc - cross_gap)], fill=C_CYAN_DIM, width=1)
    draw.line([(xc, yc + cross_gap), (xc, yc + cross_ext)], fill=C_CYAN_DIM, width=1)
    
    # NÚCLEO HOLOGRÁFICO PÚRPURA / VIOLETA
    R_core = 70
    draw.ellipse([xc - R_core, yc - R_core, xc + R_core, yc + R_core], fill=(140, 20, 220, 90), outline=C_MAGENTA, width=3)
    draw.ellipse([xc - 45, yc - 45, xc + 45, yc + 45], fill=(180, 40, 255, 100), outline=C_MAGENTA_CORE, width=2)
    draw.ellipse([xc - 22, yc - 22, xc + 22, yc + 22], fill=(230, 120, 255, 150), outline=C_WHITE, width=2)
    draw.ellipse([xc - 6, yc - 6, xc + 6, yc + 6], fill=(255, 255, 255, 255))
    
    draw.line([(xc - 55, yc), (xc + 55, yc)], fill=C_MAGENTA_CORE, width=2)
    draw.line([(xc, yc - 55), (xc, yc + 55)], fill=C_MAGENTA_CORE, width=2)
    
    # 4. Panel Izquierdo: Telemetría y Contenedores
    lx0, ly0 = x0 + 40, y0 + 90
    draw.text((lx0, ly0), "// FIELD HARMONICS", fill=C_WHITE)
    
    bars = [
        ("VORTEX FLUX", 0.92, C_CYAN),
        ("PLASMA STABILITY", 0.84, C_CYAN),
        ("CONTAINMENT COIL", 0.98, C_MAGENTA),
        ("THERMAL GRADIENT", 0.65, C_CYAN),
    ]
    for idx, (label, pct, col) in enumerate(bars):
        by = ly0 + 35 + idx * 55
        draw.text((lx0, by), label, fill=C_CYAN_DIM)
        draw.rectangle([lx0, by + 20, lx0 + 260, by + 34], outline=C_CYAN_DIM, width=1)
        n_segs = 16
        filled_segs = int(n_segs * pct)
        for s in range(n_segs):
            sx_a = lx0 + 3 + s * 16
            if s < filled_segs:
                draw.rectangle([sx_a, by + 23, sx_a + 12, by + 31], fill=col)
        draw.text((lx0 + 270, by + 18), f"{int(pct*100)}%", fill=col)
    
    # Gráfico de osciloscopio
    wy0 = ly0 + 275
    draw.text((lx0, wy0), "// WAVEFORM RESONANCE", fill=C_WHITE)
    draw.rectangle([lx0, wy0 + 25, lx0 + 310, wy0 + 130], fill=(0, 40, 60, 40), outline=C_CYAN_DIM, width=1)
    for gx in range(lx0 + 30, lx0 + 310, 40):
        draw.line([(gx, wy0 + 25), (gx, wy0 + 130)], fill=(0, 180, 220, 30), width=1)
    for gy in range(wy0 + 45, wy0 + 130, 25):
        draw.line([(lx0, gy), (lx0 + 310, gy)], fill=(0, 180, 220, 30), width=1)
    
    wave_pts = []
    for px in range(lx0 + 5, lx0 + 305, 3):
        t = (px - lx0) / 300.0 * 4 * math.pi
        py = wy0 + 78 + math.sin(t) * 32 * math.cos(t * 0.35)
        wave_pts.append((px, py))
    draw.line(wave_pts, fill=C_CYAN, width=2)
    
    # 5. Panel Derecho: Diagnóstico y Ranuras de Síntesis
    rx0 = x1 - 350
    draw.text((rx0, ly0), "// MOLECULAR COMPILATION", fill=C_WHITE)
    
    # Mini cubo 3D isométrico
    box_cx = rx0 + 150
    box_cy = ly0 + 95
    b_size = 45
    pts_cube = [
        (box_cx, box_cy - b_size),
        (box_cx + b_size * 0.86, box_cy - b_size * 0.5),
        (box_cx + b_size * 0.86, box_cy + b_size * 0.5),
        (box_cx, box_cy + b_size),
        (box_cx - b_size * 0.86, box_cy + b_size * 0.5),
        (box_cx - b_size * 0.86, box_cy - b_size * 0.5),
    ]
    draw.polygon(pts_cube, outline=C_CYAN, width=2)
    draw.line([(box_cx, box_cy), pts_cube[0]], fill=C_CYAN, width=2)
    draw.line([(box_cx, box_cy), pts_cube[2]], fill=C_CYAN, width=2)
    draw.line([(box_cx, box_cy), pts_cube[4]], fill=C_CYAN, width=2)
    draw.ellipse([box_cx - 10, box_cy - 10, box_cx + 10, box_cy + 10], fill=(210, 60, 255, 120), outline=C_MAGENTA)
    
    # Ranuras de items
    slot_y = ly0 + 175
    for s_idx in range(3):
        sy_box = slot_y + s_idx * 55
        draw.rectangle([rx0, sy_box, rx0 + 310, sy_box + 44], fill=(0, 40, 60, 50), outline=C_CYAN_DIM, width=1)
        draw.rectangle([rx0 + 5, sy_box + 5, rx0 + 39, sy_box + 39], fill=(0, 180, 220, 40), outline=C_CYAN, width=1)
        if s_idx == 0:
            draw.text((rx0 + 50, sy_box + 8), "CATALYST: DARK_PLASMA", fill=C_WHITE)
            draw.text((rx0 + 50, sy_box + 24), "STATE: LOADED [100%]", fill=C_CYAN)
        elif s_idx == 1:
            draw.text((rx0 + 50, sy_box + 8), "REACTION MATRIX", fill=C_WHITE)
            draw.text((rx0 + 50, sy_box + 24), "STATE: SYNCHRONIZED", fill=(120, 255, 140, 220))
        else:
            draw.text((rx0 + 50, sy_box + 8), "OUTPUT BUFFER", fill=C_WHITE)
            draw.text((rx0 + 50, sy_box + 24), "STATE: AWAITING COMMAND", fill=(255, 200, 80, 220))
            
    # Mini medidor auxiliar
    gauge_cx = rx0 + 150
    gauge_cy = slot_y + 230
    draw.ellipse([gauge_cx - 45, gauge_cy - 45, gauge_cx + 45, gauge_cy + 45], outline=C_CYAN_DIM, width=2)
    draw.arc([gauge_cx - 45, gauge_cy - 45, gauge_cx + 45, gauge_cy + 45], start=-140, end=40, fill=C_CYAN, width=4)
    draw.text((gauge_cx - 28, gauge_cy - 6), "OUTPUT", fill=C_WHITE)
    
    # 6. Pie de Página
    fy = y1 - 40
    bar_x = x0 + 40
    for w_i in [2, 4, 1, 3, 6, 2, 1, 4, 2, 5, 1, 3, 2, 4, 1, 2, 5, 2, 3, 1]:
        draw.rectangle([bar_x, fy, bar_x + w_i, fy + 22], fill=C_CYAN)
        bar_x += w_i + 3
    
    draw.text((x0 + 180, fy + 4), "SYS_STATUS: OPTIMAL  |  PRESS [INTERACT] TO ENGAGE FORGING SEQUENCE", fill=C_CYAN)
    draw.text((x1 - 250, fy + 4), "ID // DARX-CRAFT-BENCH-01", fill=C_WHITE)
    
    # 7. Resplandor Holográfico Bloom
    glow = img.filter(ImageFilter.GaussianBlur(radius=4))
    final_hud = Image.alpha_composite(glow, img)
    
    final_hud.save(output_path, "PNG")
    print(f"Textura de Holograma HUD guardada en: {output_path}")

if __name__ == "__main__":
    v_path = os.path.join(TEX_DIR, "T_Bench_Vortex.png")
    h_path = os.path.join(TEX_DIR, "T_Bench_HoloHUD.png")
    generate_vortex_texture(v_path, 1024)
    generate_hud_texture(h_path, 1600, 1000)
    print("Todas las texturas generadas con éxito.")

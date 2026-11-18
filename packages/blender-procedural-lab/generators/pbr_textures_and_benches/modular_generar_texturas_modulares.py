# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Generador Maestro de Texturas y Trim Sheets Modulares Desacoplados
# Genera mapas PNG de alta resolución (2048x2048) en Art/Textures/Modular/

import os
import math
from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = r"F:\Dev\Game\Art\Textures\Modular"
os.makedirs(OUTPUT_DIR, exist_ok=True)

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

def generate_industrial_trim():
    path = os.path.join(OUTPUT_DIR, "T_Trim_Industrial_Modular.png")
    img = Image.new("RGBA", (2048, 2048), (55, 45, 40, 255))
    draw = ImageDraw.Draw(img)

    # 1. Banda Hazard Chevron (y: 0 - 256)
    yellow = (240, 195, 25, 255)
    black = (28, 26, 25, 255)
    for x in range(-500, 2600, 120):
        draw.polygon([(x, 0), (x + 60, 0), (x + 60 - 256, 256), (x - 256, 256)], fill=black)
        draw.polygon([(x + 60, 0), (x + 120, 0), (x + 120 - 256, 256), (x + 60 - 256, 256)], fill=yellow)
    draw.rectangle([(0, 0), (2048, 12)], fill=(15, 15, 15, 255))
    draw.rectangle([(0, 244), (2048, 256)], fill=(15, 15, 15, 255))

    # 2. Banda de Placas de Acero Pesado con Remaches (y: 256 - 768)
    steel = (90, 85, 80, 255)
    steel_dark = (50, 48, 45, 255)
    draw.rectangle([(0, 256), (2048, 768)], fill=steel)
    for px in range(0, 2048, 512):
        draw.line([(px, 256), (px, 768)], fill=steel_dark, width=6)
        draw.line([(px+3, 256), (px+3, 768)], fill=(130, 125, 120, 255), width=2)
    # Línea horizontal de unión
    draw.line([(0, 512), (2048, 512)], fill=steel_dark, width=6)
    draw.line([(0, 515), (2048, 515)], fill=(130, 125, 120, 255), width=2)
    # Filas de remaches
    for py in [280, 488, 536, 744]:
        for px in range(32, 2048, 64):
            # Cabeza de perno / remache
            draw.ellipse([(px-10, py-10), (px+10, py+10)], fill=(40, 38, 35, 255))
            draw.ellipse([(px-8, py-8), (px+6, py+6)], fill=(160, 155, 150, 255))
            draw.ellipse([(px-5, py-5), (px+3, py+3)], fill=(200, 195, 190, 255))

    # Manchas de óxido y corrosión
    rust_colors = [(140, 55, 25, 220), (175, 75, 30, 200), (95, 35, 15, 240)]
    for ox in [180, 620, 1150, 1680]:
        draw.polygon([(ox, 512), (ox+70, 512), (ox+100, 720), (ox-30, 720)], fill=rust_colors[0])
        draw.polygon([(ox+15, 512), (ox+45, 512), (ox+60, 660), (ox-10, 660)], fill=rust_colors[1])

    # 3. Banda Rejilla de Suelo Antideslizante (Diamond Mesh) (y: 768 - 1280)
    grate_bg = (35, 32, 30, 255)
    draw.rectangle([(0, 768), (2048, 1280)], fill=grate_bg)
    mesh_line = (110, 105, 100, 255)
    for x in range(-500, 2600, 32):
        draw.line([(x, 768), (x + 512, 1280)], fill=mesh_line, width=2)
        draw.line([(x + 512, 768), (x, 1280)], fill=mesh_line, width=2)
    # Bordes reforzados
    draw.rectangle([(0, 768), (2048, 788)], fill=(75, 70, 65, 255))
    draw.rectangle([(0, 1260), (2048, 1280)], fill=(75, 70, 65, 255))

    # 4. Banda Paneles Pintados Amarillos Industriales con Rótulos (y: 1280 - 1664)
    ind_yellow = (215, 165, 25, 255)
    draw.rectangle([(0, 1280), (2048, 1664)], fill=ind_yellow)
    font_large = get_font(72, bold=True)
    font_med = get_font(46, bold=True)
    font_small = get_font(32, bold=True)
    # Rótulos en estarcido (stencil)
    draw.text((80, 1330), "QUÍMICO MORTAL", fill=(25, 25, 25, 255), font=font_large)
    draw.text((950, 1330), "ACIDGOO // SECTOR 04", fill=(30, 140, 20, 255), font=font_large)
    draw.text((80, 1450), "MAX LOAD: 50.000 KG", fill=(60, 45, 15, 255), font=font_med)
    draw.text((950, 1450), "PRECAUCIÓN: CORROSIÓN ACTIVA", fill=(160, 30, 20, 255), font=font_med)
    draw.text((80, 1550), "[ ISO-9001 BULK HAZMAT CARRIER ]", fill=(50, 40, 20, 255), font=font_small)
    draw.text((1200, 1550), "AIRLOCK BAY D-12", fill=(25, 25, 25, 255), font=font_small)

    # 5. Banda Chapa Corrugada de Contenedor (y: 1664 - 2048)
    corr_base = (45, 75, 115, 255) # Azul naval industrial
    draw.rectangle([(0, 1664), (2048, 2048)], fill=corr_base)
    for cx in range(0, 2048, 64):
        # Sombra y luz de onda corrugada
        draw.rectangle([(cx, 1664), (cx + 32, 2048)], fill=(32, 55, 88, 255))
        draw.rectangle([(cx + 32, 1664), (cx + 64, 2048)], fill=(58, 95, 145, 255))
        draw.line([(cx, 1664), (cx, 2048)], fill=(20, 35, 60, 255), width=2)
        draw.line([(cx + 32, 1664), (cx + 32, 2048)], fill=(80, 125, 180, 255), width=2)
    # Esquinas reforzadas
    draw.text((60, 1720), "ASTRA LOGISTICS", fill=(230, 230, 230, 255), font=font_med)
    draw.text((60, 1800), "CONT-ID: #HAZ-9824", fill=(210, 180, 40, 255), font=font_small)

    img.save(path)
    print(f"[OK] Generado: {path}")

def generate_artdeco_trim():
    path = os.path.join(OUTPUT_DIR, "T_Trim_ArtDeco_Modular.png")
    img = Image.new("RGBA", (2048, 2048), (45, 18, 12, 255))
    draw = ImageDraw.Draw(img)

    gold_bright = (245, 205, 85, 255)
    gold_dark = (175, 130, 35, 255)
    velvet_burgundy = (85, 14, 28, 255)
    velvet_shadow = (45, 8, 16, 255)

    # 1. Madera Caoba Pulida (y: 0 - 512)
    mahogany_dark = (52, 22, 15, 255)
    mahogany_light = (78, 32, 22, 255)
    for y in range(0, 512):
        factor = (math.sin(y * 0.08) + math.cos(y * 0.02) + 2) / 4.0
        r = int(mahogany_dark[0] + factor * (mahogany_light[0] - mahogany_dark[0]))
        g = int(mahogany_dark[1] + factor * (mahogany_light[1] - mahogany_dark[1]))
        b = int(mahogany_dark[2] + factor * (mahogany_light[2] - mahogany_dark[2]))
        draw.line([(0, y), (2048, y)], fill=(r, g, b, 255))
    # Marcos dorados incrustados en la madera
    for mx in range(64, 2048, 512):
        draw.rectangle([(mx, 32), (mx + 384, 480)], outline=gold_dark, width=6)
        draw.rectangle([(mx + 20, 52), (mx + 364, 460)], outline=gold_bright, width=3)
        # Rombo central Art Déco
        cx = mx + 192
        cy = 256
        draw.polygon([(cx, 80), (cx + 120, cy), (cx, 432), (cx - 120, cy)], outline=gold_bright, width=4)

    # 2. Grecas y Molduras Doradas Geométricas (y: 512 - 1024)
    draw.rectangle([(0, 512), (2048, 1024)], fill=(28, 22, 18, 255))
    # Frisos escalonados de latón
    for step_y in range(540, 1000, 110):
        for x in range(0, 2048, 128):
            # Escalón ziggurat Art Déco
            draw.polygon([
                (x, step_y + 80), (x + 20, step_y + 80), (x + 20, step_y + 40),
                (x + 40, step_y + 40), (x + 40, step_y), (x + 88, step_y),
                (x + 88, step_y + 40), (x + 108, step_y + 40), (x + 108, step_y + 80),
                (x + 128, step_y + 80)
            ], outline=gold_bright, width=3)
            draw.line([(x, step_y + 80), (x + 128, step_y + 80)], fill=gold_dark, width=4)

    # 3. Terciopelo Burdeos Capitoné con Botones (y: 1024 - 1536)
    draw.rectangle([(0, 1024), (2048, 1536)], fill=velvet_burgundy)
    for vy in range(1024, 1536, 128):
        for vx in range(0, 2048, 128):
            # Líneas diagonales de costura en rombos
            draw.line([(vx, vy), (vx + 128, vy + 128)], fill=velvet_shadow, width=4)
            draw.line([(vx + 128, vy), (vx, vy + 128)], fill=velvet_shadow, width=4)
    # Botones dorados en los vértices
    for vy in range(1024, 1536 + 64, 64):
        for vx in range(0, 2048 + 64, 64):
            if ((vx // 64) + (vy // 64)) % 2 == 0:
                draw.ellipse([(vx-8, vy-8), (vx+8, vy+8)], fill=(35, 6, 12, 255))
                draw.ellipse([(vx-5, vy-5), (vx+5, vy+5)], fill=gold_bright)

    # 4. Vidrio Biselado / Espejo & Candelabros (y: 1536 - 2048)
    glass_tone = (195, 215, 225, 255)
    draw.rectangle([(0, 1536), (2048, 2048)], fill=(40, 52, 60, 255))
    # Facetas de espejo y cristal con reflejos cálidos
    for gx in range(0, 2048, 256):
        draw.polygon([(gx, 1536), (gx + 128, 1536), (gx + 256, 2048), (gx + 128, 2048)], fill=(65, 85, 100, 255))
        draw.line([(gx, 1536), (gx + 256, 2048)], fill=gold_bright, width=3)
        draw.line([(gx + 128, 1536), (gx + 128, 2048)], fill=(120, 155, 175, 255), width=2)

    img.save(path)
    print(f"[OK] Generado: {path}")

def generate_plasma_trim():
    path = os.path.join(OUTPUT_DIR, "T_Trim_Plasma_Modular.png")
    img = Image.new("RGBA", (2048, 2048), (24, 28, 35, 255))
    draw = ImageDraw.Draw(img)

    cyan_glow = (45, 225, 255, 255)
    cyan_bright = (190, 250, 255, 255)
    coil_copper = (195, 115, 55, 255)
    coil_brass = (235, 175, 45, 255)
    warning_yellow = (245, 210, 25, 255)

    # 1. Chapa Gunmetal con Pernos Recesados (y: 0 - 512)
    draw.rectangle([(0, 0), (2048, 512)], fill=(38, 42, 50, 255))
    for px in range(0, 2048, 256):
        draw.line([(px, 0), (px, 512)], fill=(15, 18, 22, 255), width=5)
        draw.line([(px+2, 0), (px+2, 512)], fill=(65, 75, 90, 255), width=2)
    draw.line([(0, 256), (2048, 256)], fill=(15, 18, 22, 255), width=5)
    # Pernos hexagonales
    for px in range(32, 2048, 64):
        for py in [32, 224, 288, 480]:
            draw.ellipse([(px-7, py-7), (px+7, py+7)], fill=(20, 24, 28, 255))
            draw.ellipse([(px-5, py-5), (px+5, py+5)], fill=(90, 105, 120, 255))

    # 2. Devanados de Cobre y Bobinas Magnéticas Tokamak (y: 512 - 1024)
    draw.rectangle([(0, 512), (2048, 1024)], fill=(18, 18, 22, 255))
    for y in range(512, 1024, 24):
        draw.rectangle([(0, y), (2048, y + 16)], fill=coil_copper)
        draw.line([(0, y), (2048, y)], fill=(110, 55, 20, 255), width=3)
        draw.line([(0, y + 8), (2048, y + 8)], fill=coil_brass, width=2)
    # Abrazaderas cerámicas de aislamiento
    for x in range(128, 2048, 256):
        draw.rectangle([(x, 512), (x + 48, 1024)], fill=(225, 225, 220, 255), outline=(50, 50, 50, 255), width=4)

    # 3. Señalética de Alta Energía y Peligro (y: 1024 - 1536)
    draw.rectangle([(0, 1024), (2048, 1536)], fill=(32, 35, 40, 255))
    # Cartel 1: REFINERÍA DE PLASMA
    draw.rectangle([(64, 1056), (960, 1500)], fill=warning_yellow, outline=(15, 15, 15, 255), width=10)
    font_title = get_font(70, bold=True)
    font_sub = get_font(42, bold=True)
    draw.text((120, 1120), "REFINERÍA", fill=(15, 15, 15, 255), font=font_title)
    draw.text((120, 1210), "DE PLASMA", fill=(15, 15, 15, 255), font=font_title)
    draw.text((120, 1340), "[ SECTOR TOKAMAK 07 ]", fill=(15, 15, 15, 255), font=font_sub)
    draw.text((120, 1410), "CONFINAMIENTO ACTIVO", fill=(160, 20, 15, 255), font=font_sub)

    # Cartel 2: PELIGRO: ALTA ENERGÍA
    draw.rectangle([(1088, 1056), (1984, 1500)], fill=warning_yellow, outline=(15, 15, 15, 255), width=10)
    draw.text((1140, 1120), "PELIGRO:", fill=(180, 15, 15, 255), font=font_title)
    draw.text((1140, 1210), "ALTA ENERGÍA", fill=(15, 15, 15, 255), font=font_title)
    draw.text((1140, 1340), "VOLTAJE: 50.000 kV", fill=(15, 15, 15, 255), font=font_sub)
    draw.text((1140, 1410), "NÚCLEO EN RESONANCIA", fill=(15, 15, 15, 255), font=font_sub)

    # 4. Conductos y Arcos de Plasma Cian Emisivo (y: 1536 - 2048)
    draw.rectangle([(0, 1536), (2048, 2048)], fill=(8, 16, 25, 255))
    # Rayos eléctricos y plasma
    for y in range(1560, 2020, 120):
        draw.line([(0, y), (2048, y)], fill=cyan_glow, width=28)
        draw.line([(0, y), (2048, y)], fill=cyan_bright, width=12)
        draw.line([(0, y), (2048, y)], fill=(255, 255, 255, 255), width=4)
    # Malla hexagonal de contención
    for hx in range(0, 2048, 48):
        for hy in range(1536, 2048, 48):
            draw.regular_polygon((hx, hy, 18), n_sides=6, outline=(25, 85, 120, 180), width=2)

    img.save(path)
    print(f"[OK] Generado: {path}")

def generate_enemy_components_trim():
    path = os.path.join(OUTPUT_DIR, "T_Trim_EnemyParts_Modular.png")
    img = Image.new("RGBA", (2048, 2048), (30, 28, 26, 255))
    draw = ImageDraw.Draw(img)

    font_gauge = get_font(28, bold=True)
    font_bold = get_font(48, bold=True)

    # Cuadrante 1: Manómetro Analógico de Presión (0, 0 a 1024, 1024)
    # Dial Face
    center_dial = (512, 512)
    radius_dial = 420
    draw.ellipse([(center_dial[0]-radius_dial, center_dial[1]-radius_dial),
                  (center_dial[0]+radius_dial, center_dial[1]+radius_dial)],
                 fill=(245, 242, 230, 255), outline=(35, 30, 25, 255), width=24)
    draw.ellipse([(center_dial[0]-radius_dial+16, center_dial[1]-radius_dial+16),
                  (center_dial[0]+radius_dial-16, center_dial[1]+radius_dial-16)],
                 outline=(180, 140, 45, 255), width=10) # Borde de latón

    # Zona Roja de Peligro (arco de 30° a 90°)
    draw.arc([(center_dial[0]-350, center_dial[1]-350), (center_dial[0]+350, center_dial[1]+350)],
             start=300, end=360, fill=(210, 35, 25, 255), width=24)

    # Ticks y números en el dial
    for angle_deg in range(140, 400 + 1, 15):
        rad = math.radians(angle_deg)
        inner_r = 310 if angle_deg % 30 == 0 else 340
        x1 = center_dial[0] + inner_r * math.cos(rad)
        y1 = center_dial[1] + inner_r * math.sin(rad)
        x2 = center_dial[0] + 370 * math.cos(rad)
        y2 = center_dial[1] + 370 * math.sin(rad)
        draw.line([(x1, y1), (x2, y2)], fill=(25, 25, 25, 255), width=6 if angle_deg % 30 == 0 else 3)

    draw.text((430, 360), "PSI x 100", fill=(55, 55, 55, 255), font=font_gauge)
    draw.text((420, 620), "OVERHEAT", fill=(190, 30, 20, 255), font=font_gauge)
    # Aguja roja afilada apuntando a la zona de peligro
    needle_rad = math.radians(335)
    nx = center_dial[0] + 320 * math.cos(needle_rad)
    ny = center_dial[1] + 320 * math.sin(needle_rad)
    draw.line([center_dial, (nx, ny)], fill=(225, 25, 25, 255), width=10)
    draw.ellipse([(center_dial[0]-32, center_dial[1]-32), (center_dial[0]+32, center_dial[1]+32)],
                 fill=(25, 25, 25, 255), outline=(180, 140, 45, 255), width=6)

    # Cuadrante 2: Sierra Circular y Dientes de Acero (1024, 0 a 2048, 1024)
    center_saw = (1536, 512)
    radius_saw = 400
    draw.ellipse([(center_saw[0]-radius_saw, center_saw[1]-radius_saw),
                  (center_saw[0]+radius_saw, center_saw[1]+radius_saw)],
                 fill=(135, 140, 145, 255), outline=(40, 42, 45, 255), width=18)
    # Dientes triangulares
    num_teeth = 20
    for i in range(num_teeth):
        a1 = math.radians(i * (360 / num_teeth))
        a2 = math.radians((i + 0.6) * (360 / num_teeth))
        a3 = math.radians((i + 0.9) * (360 / num_teeth))
        p1 = (center_saw[0] + 380 * math.cos(a1), center_saw[1] + 380 * math.sin(a1))
        p2 = (center_saw[0] + 460 * math.cos(a2), center_saw[1] + 460 * math.sin(a2))
        p3 = (center_saw[0] + 380 * math.cos(a3), center_saw[1] + 380 * math.sin(a3))
        draw.polygon([p1, p2, p3], fill=(185, 190, 195, 255), outline=(30, 30, 30, 255))
    # Buje central y orificios de aligeramiento
    draw.ellipse([(center_saw[0]-140, center_saw[1]-140), (center_saw[0]+140, center_saw[1]+140)],
                 fill=(55, 58, 62, 255), outline=(25, 25, 25, 255), width=10)
    for h_a in range(0, 360, 60):
        h_rad = math.radians(h_a)
        hx = center_saw[0] + 250 * math.cos(h_rad)
        hy = center_saw[1] + 250 * math.sin(h_rad)
        draw.ellipse([(hx-40, hy-40), (hx+40, hy+40)], fill=(30, 28, 26, 255), outline=(15, 15, 15, 255), width=6)

    # Cuadrante 3: Sensor Óptico / Lente Tri-Visor (0, 1024 a 1024, 2048)
    center_lens = (512, 1536)
    draw.ellipse([(center_lens[0]-380, center_lens[1]-380), (center_lens[0]+380, center_lens[1]+380)],
                 fill=(15, 20, 28, 255), outline=(75, 85, 95, 255), width=20)
    # Lente convexa de esmeralda / cian
    draw.ellipse([(center_lens[0]-320, center_lens[1]-320), (center_lens[0]+320, center_lens[1]+320)],
                 fill=(15, 85, 55, 255), outline=(40, 225, 130, 255), width=12)
    # Retícula HUD emisiva
    draw.ellipse([(center_lens[0]-220, center_lens[1]-220), (center_lens[0]+220, center_lens[1]+220)],
                 outline=(60, 255, 160, 255), width=6)
    draw.ellipse([(center_lens[0]-110, center_lens[1]-110), (center_lens[0]+110, center_lens[1]+110)],
                 outline=(180, 255, 210, 255), width=8)
    draw.line([(center_lens[0]-320, center_lens[1]), (center_lens[0]+320, center_lens[1])], fill=(60, 255, 160, 255), width=4)
    draw.line([(center_lens[0], center_lens[1]-320), (center_lens[0], center_lens[1]+320)], fill=(60, 255, 160, 255), width=4)
    draw.text((240, 1850), "TARGET LOCK: 98.4%", fill=(60, 255, 160, 255), font=font_gauge)

    # Cuadrante 4: Textura de Fuego / Llamas Cómic 2D y Magma (1024, 1024 a 2048, 2048)
    draw.rectangle([(1024, 1024), (2048, 2048)], fill=(30, 15, 10, 255))
    # Lenguas de fuego estilizadas con degradado plano
    for fx in range(1060, 2000, 180):
        # Llama exterior naranja oscuro
        draw.polygon([(fx, 2048), (fx + 90, 1150), (fx + 180, 2048)], fill=(225, 75, 15, 255))
        # Llama interior naranja brillante
        draw.polygon([(fx + 25, 2048), (fx + 90, 1300), (fx + 155, 2048)], fill=(255, 155, 20, 255))
        # Núcleo amarillo puro
        draw.polygon([(fx + 50, 2048), (fx + 90, 1520), (fx + 130, 2048)], fill=(255, 245, 80, 255))
        # Contornos de cómic
        draw.line([(fx, 2048), (fx + 90, 1150), (fx + 180, 2048)], fill=(15, 8, 5, 255), width=6)

    img.save(path)
    print(f"[OK] Generado: {path}")

if __name__ == "__main__":
    generate_industrial_trim()
    generate_artdeco_trim()
    generate_plasma_trim()
    generate_enemy_components_trim()
    print("Todas las texturas modulares han sido generadas con exito.")

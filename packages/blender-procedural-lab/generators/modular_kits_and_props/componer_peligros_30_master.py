# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Compositor de Lamina Maestra Tecnica: 30 Peligros Ambientales (H01 al H30)
# Resolucion 2560 x 1600 - Matriz 5x6 con fichas tecnicas, categorias y metadatos de juego

import os
import sys
import shutil
from PIL import Image, ImageDraw, ImageFont
import textwrap

RENDERS_DIR = r"F:\Dev\Game\Art\Renders"
ARTIFACT_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\b59ff04f-3c21-4ee5-94b0-8e8f899f8923"
OUTPUT_FILE = os.path.join(RENDERS_DIR, "Showcase_Peligros_Ambientales_30_Master.png")
ARTIFACT_FILE = os.path.join(ARTIFACT_DIR, "Showcase_Peligros_Ambientales_30_Master.png")

ALL_HAZARDS = [
    # Lote 1: Térmicos e Ígneos
    (1, "CloseUp_H01_Fire_Bulkhead_Rupture.png", "H01: Fuga en Mamparo Igneo", "Termico / Fuego", (230, 76, 60)),
    (2, "CloseUp_H02_Electrical_Arc_Fire_Box.png", "H02: Cuadro de Arcos Igneos", "Termico / Electrico", (230, 76, 60)),
    (3, "CloseUp_H03_Magnesium_Chemical_Fire.png", "H03: Fuego Quimico Magnesio", "Termico / Quimico", (230, 76, 60)),
    (4, "CloseUp_H04_Plasma_Nozzle_Breach.png", "H04: Brecha Tobera Plasma", "Termico / Plasma", (230, 76, 60)),
    (5, "CloseUp_H05_Vent_Duct_Inferno.png", "H05: Conducto en Ignicion", "Termico / Ventilacion", (230, 76, 60)),
    (6, "CloseUp_H06_Habitation_Flashover.png", "H06: Flashover en Camarote", "Termico / Colapso", (230, 76, 60)),
    # Lote 2: Fugas de Presión y Fluidos
    (7, "CloseUp_H07_Superheated_Steam_Jet.png", "H07: Chorro Vapor a 280C", "Fluidos / Presion", (41, 128, 185)),
    (8, "CloseUp_H08_Hydraulic_Oil_Slick.png", "H08: Charco Aceite Hidraulico", "Fluidos / Resbalon", (41, 128, 185)),
    (9, "CloseUp_H09_Hydrofluoric_Acid_Puddle.png", "H09: Charco Acido Fluorhidrico", "Fluidos / Corrosivo", (41, 128, 185)),
    (10, "CloseUp_H10_Liquid_Nitrogen_Cryo_Leak.png", "H10: Criofuga de Nitrogeno", "Fluidos / Criogenico", (41, 128, 185)),
    (11, "CloseUp_H11_Hull_Decompression_Vortex.png", "H11: Vortice Despresurizacion", "Fluidos / Vacio", (41, 128, 185)),
    (12, "CloseUp_H12_Toxic_Coolant_Flooding.png", "H12: Inundacion Refrigerante", "Fluidos / Anegamiento", (41, 128, 185)),
    # Lote 3: Eléctricos y Energía
    (13, "CloseUp_H13_Live_Arcing_Whip_Cable.png", "H13: Cable Alta Tension Danzante", "Energia / Alto Voltaje", (241, 196, 15)),
    (14, "CloseUp_H14_Aux_Generator_Meltdown.png", "H14: Generador en Meltdown", "Energia / Sobrecarga", (241, 196, 15)),
    (15, "CloseUp_H15_Electrified_Floor_Grating.png", "H15: Rejilla Piso Electrificada", "Energia / Electrocutacion", (241, 196, 15)),
    (16, "CloseUp_H16_Battery_Rack_Thermal_Runaway.png", "H16: Fuga Termica Baterias", "Energia / Quimico", (241, 196, 15)),
    (17, "CloseUp_H17_Rogue_Scraping_Electromagnet.png", "H17: Electroiman Descontrolado", "Energia / Magnetismo", (241, 196, 15)),
    (18, "CloseUp_H18_Blown_High_Amp_Fuse_Bank.png", "H18: Banco Fusibles Calcinado", "Energia / Descarga", (241, 196, 15)),
    # Lote 4: Colapsos Estructurales
    (19, "CloseUp_H19_Fractured_Structural_IBeam.png", "H19: Viga I Maestra Partida", "Estructural / Traccion", (230, 126, 34)),
    (20, "CloseUp_H20_Collapsed_Ceiling_Baffle.png", "H20: Falso Techo Desprendido", "Estructural / Desprendimiento", (230, 126, 34)),
    (21, "CloseUp_H21_Overpressured_Bulging_Bulkhead.png", "H21: Mamparo Abombado", "Estructural / Sobrepresion", (230, 126, 34)),
    (22, "CloseUp_H22_Broken_Catwalk_Section.png", "H22: Pasarela Partida en V", "Estructural / Caida", (230, 126, 34)),
    (23, "CloseUp_H23_Jammed_Blast_Gate_Angle.png", "H23: Compuerta Blast Atascada", "Estructural / Bloqueo", (230, 126, 34)),
    (24, "CloseUp_H24_Twisted_Cage_Ladder_Collapse.png", "H24: Escalera Gato Colapsada", "Estructural / Deformacion", (230, 126, 34)),
    # Lote 5: Biológicos y Radiológicos
    (25, "CloseUp_H25_Shattered_BSL4_Incubator.png", "H25: Incubadora BSL-4 Rota", "Biologico / Esporas", (39, 174, 96)),
    (26, "CloseUp_H26_Exposed_Fuel_Rod_Basket.png", "H26: Barras Nuclear Cherenkov", "Radiacion / Ionizante", (155, 89, 182)),
    (27, "CloseUp_H27_Slime_Clogged_Valve.png", "H27: Valvula con Escoria Bio", "Biologico / Mucilago", (39, 174, 96)),
    (28, "CloseUp_H28_Overflowing_Toxic_Sump.png", "H28: Sumidero Septico Caustico", "Biologico / Putrefaccion", (142, 68, 173)),
    (29, "CloseUp_H29_Shattered_Cryo_Dewar.png", "H29: Frasco Patogeno Volcado", "Biologico / Contagio", (39, 174, 96)),
    (30, "CloseUp_H30_Fungal_Colonized_Scrubber.png", "H30: Depurador con Moho Parasito", "Biologico / Infeccion Aire", (39, 174, 96)),
]

def build_master_sheet():
    print("[*] Componiendo Lamina Maestra Tecnica 2.5K de los 30 Peligros Ambientales...")
    W, H = 2560, 1600
    canvas = Image.new("RGBA", (W, H), (12, 14, 18, 255))
    draw = ImageDraw.Draw(canvas)
    
    try:
        font_main = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 26)
        font_sub = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 15)
        font_pill = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 13)
        font_card_code = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 13)
        font_card_title = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 12)
        font_card_cat = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 11)
        font_foot = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 11)
    except:
        font_main = font_sub = font_pill = font_card_code = font_card_title = font_card_cat = font_foot = ImageFont.load_default()
        
    draw.text((40, 20), "ASTRA HAZARD // SISTEMA DE CRISIS Y CATÁSTROFES AMBIENTALES // BLENDER 5.2 LTS", fill=(0, 200, 240), font=font_sub)
    draw.text((40, 48), "SUITE MAESTRA OFICIAL DE 30 PELIGROS AMBIENTALES (H01 A H30 COMPLETO)", fill=(255, 255, 255), font=font_main)
    
    badges = [
        ("30 PELIGROS 3D", (41, 128, 185)),
        ("5 CATEGORÍAS SISTÉMICAS", (39, 174, 96)),
        ("FISICA RAGDOLL & MECÁNICAS DE JUEGO", (211, 84, 0)),
        ("CERTIFICADO CERO BUGS", (142, 68, 173))
    ]
    cur_x = W - 40
    for btext, bcol in reversed(badges):
        tw = len(btext) * 8 + 22
        cur_x -= tw
        draw.rounded_rectangle((cur_x, 34, cur_x + tw - 10, 68), radius=6, fill=bcol)
        draw.text((cur_x + 10, 43), btext, fill=(255, 255, 255), font=font_pill)
        cur_x -= 10
        
    draw.line([(40, 92), (W - 40, 92)], fill=(45, 52, 65), width=2)
    
    # Matriz 5 filas x 6 columnas
    # Espacio disponible: Y de 105 a 1570 -> 1465px de alto para 5 filas (~280px por fila)
    # X de 40 a 2520 -> 2480px de ancho para 6 columnas (~400px por columna)
    cols = 6
    rows = 5
    card_w = 398
    card_h = 278
    gap_x = 18
    gap_y = 15
    start_x = 40
    start_y = 108
    
    for idx, (hid, img_filename, htitle, hcat, hcol) in enumerate(ALL_HAZARDS):
        c_i = idx % cols
        r_i = idx // cols
        cx = start_x + c_i * (card_w + gap_x)
        cy = start_y + r_i * (card_h + gap_y)
        
        # Fondo de la tarjeta
        draw.rounded_rectangle((cx, cy, cx + card_w, cy + card_h), radius=6, fill=(18, 21, 28, 255), outline=(38, 44, 56), width=2)
        
        # Barra lateral de color de categoría
        draw.rounded_rectangle((cx, cy, cx + 6, cy + card_h), radius=3, fill=hcol)
        
        # Miniatura del render (220 x 220)
        img_path = os.path.join(RENDERS_DIR, img_filename)
        thumb_size = 238
        if os.path.exists(img_path):
            thumb_img = Image.open(img_path).convert("RGBA")
            resized = thumb_img.resize((thumb_size, thumb_size), Image.Resampling.LANCZOS)
            canvas.paste(resized, (cx + 14, cy + 20))
            draw.rectangle((cx + 14, cy + 20, cx + 14 + thumb_size, cy + 20 + thumb_size), outline=(45, 52, 65), width=1)
            
        # Panel derecho de datos
        tx = cx + 262
        draw.rounded_rectangle((tx, cy + 18, cx + card_w - 14, cy + 42), radius=4, fill=(25, 30, 40))
        draw.text((tx + 8, cy + 22), f"ID: H{hid:02d}", fill=(0, 200, 240), font=font_card_code)
        
        ty = cy + 50
        # Categoría
        draw.rounded_rectangle((tx, ty, cx + card_w - 14, ty + 24), radius=4, fill=(hcol[0]//4, hcol[1]//4, hcol[2]//4))
        draw.text((tx + 6, ty + 4), hcat, fill=hcol, font=font_card_cat)
        ty += 32
        
        # Título
        t_lines = textwrap.wrap(htitle, width=16)
        for tl in t_lines[:2]:
            draw.text((tx, ty), tl, fill=(255, 255, 255), font=font_card_title)
            ty += 18
            
        draw.line([(tx, ty + 4), (cx + card_w - 14, ty + 4)], fill=(40, 48, 62), width=1)
        ty += 14
        
        # Datos del sistema
        draw.text((tx, ty), "• Cel-Shading 3D", fill=(175, 185, 200), font=font_card_cat)
        ty += 16
        draw.text((tx, ty), "• PBR Stylized", fill=(175, 185, 200), font=font_card_cat)
        ty += 16
        draw.text((tx, ty), "• Deteccion Fisica", fill=(175, 185, 200), font=font_card_cat)
        ty += 16
        draw.text((tx, ty), "• Mitigacion Activa", fill=(175, 185, 200), font=font_card_cat)
        
        # Badge de estado
        draw.rounded_rectangle((tx, cy + card_h - 32, cx + card_w - 14, cy + card_h - 12), radius=4, fill=(15, 26, 20))
        draw.text((tx + 6, cy + card_h - 28), "ESTADO: CERTIFICADO", fill=(46, 204, 113), font=font_foot)
        
    canvas.save(OUTPUT_FILE, format="PNG")
    shutil.copy2(OUTPUT_FILE, ARTIFACT_FILE)
    print(f"[+] Lamina Maestra Oficial guardada en: {OUTPUT_FILE}")
    print(f"[+] Sincronizada con artefacto con exito: {ARTIFACT_FILE}")

if __name__ == "__main__":
    build_master_sheet()

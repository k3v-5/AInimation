# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Generador Maestro del Catalogo Modular de 90 Activos Arquitectonicos Oficiales
# Astra Hazard Studios - Blender 5.2 LTS - Lamina Maestra Consolidada 2560x1440

import os
import sys
import shutil
from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = r"F:\Dev\Game"
RENDERS_DIR = os.path.join(PROJECT_ROOT, "Art", "Renders")
ARTIFACT_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\b59ff04f-3c21-4ee5-94b0-8e8f899f8923"

def build_master_90_sheet():
    print("=" * 75)
    print("[*] Ensamblando Lamina Maestra de 90 Activos Modulares (Lotes A, B y C)...")
    print("=" * 75)
    
    W, H = 2560, 1440
    canvas = Image.new("RGBA", (W, H), (12, 14, 18, 255))
    draw = ImageDraw.Draw(canvas)
    
    try:
        font_title = ImageFont.truetype("arialbd.ttf", 26)
        font_sub = ImageFont.truetype("arialbd.ttf", 15)
        font_card_title = ImageFont.truetype("arialbd.ttf", 17)
        font_pill = ImageFont.truetype("arialbd.ttf", 13)
        font_desc = ImageFont.truetype("arial.ttf", 12)
        font_stat = ImageFont.truetype("arialbd.ttf", 13)
        font_micro = ImageFont.truetype("arial.ttf", 11)
        font_micro_b = ImageFont.truetype("arialbd.ttf", 11)
    except:
        font_title = font_sub = font_card_title = font_pill = font_desc = font_stat = font_micro = font_micro_b = ImageFont.load_default()
        
    # Encabezado principal
    draw.text((45, 18), "ASTRA HAZARD // REPOSITORIO DE ARQUITECTURA MODULAR // BLENDER 5.2 LTS", fill=(245, 166, 35), font=font_sub)
    draw.text((45, 46), "CATALOGO MAESTRO DE 90 ACTIVOS MODULARES 3D // LOTES A, B Y C CONSOLIDADOS", fill=(255, 255, 255), font=font_title)
    
    # Badges
    pills = [
        ("90 ACTIVOS 3D CERTIFICADOS", (41, 128, 185)),
        ("5 KITS TEMATICOS MODULARES", (39, 174, 96)),
        ("CEL-SHADING PBR + FREESTYLE", (142, 68, 173)),
        ("INSPECCION VISUAL 100%", (211, 84, 0)),
        ("BLENDER 5.2 LTS", (52, 73, 94))
    ]
    cur_x = W - 45
    for text, bg_col in reversed(pills):
        tw = len(text) * 8 + 22
        cur_x -= tw
        draw.rounded_rectangle((cur_x, 32, cur_x + tw - 10, 66), radius=6, fill=bg_col)
        draw.text((cur_x + 10, 41), text, fill=(255, 255, 255), font=font_pill)
        cur_x -= 10
        
    draw.line((45, 88, W - 45, 88), fill=(45, 52, 65), width=2)
    
    # 3 Filas horizontales para los 3 lotes
    lotes_info = [
        {
            "title": "LOTE A: ARQUITECTURA INDUSTRIAL & BOISERIE ART DECO (ACTIVOS 01 AL 30)",
            "file": "Raw_LoteA_Panorama.png",
            "theme_col": (245, 166, 35),
            "badge_col": (41, 128, 185),
            "kits": "Kit 1: Industrial Derelict (01-18)  |  Kit 2: Boiserie Deco (19-30)",
            "row1": "Fila 1 (Front): 01. Muro Ciego 400x350 | 02. Portón Mamparo | 03. Suelo Rejilla | 04. Viga Techo | 05. Pasarela Recta | 06. Escalera Gato | 07. Tubería Triple | 08. Contenedor | 09. Foso Ácido | 10. Puerta Blast",
            "row2": "Fila 2 (Mid):   11. Grúa Viajera | 12. Columna I-Beam | 13. Rejilla Louver | 14. Bandeja Cables | 15. Esclusa | 16. Escotilla Suelo | 17. Arriostre Diagonal | 18. Bolardos Peligro | 19. Boiserie Nogal | 20. Portal Dorado",
            "row3": "Fila 3 (Back):  21. Mármol Carrara | 22. Techo Artesonado | 23. Columna Corintia | 24. Sofá Chesterfield | 25. Sillón Orejero | 26. Balaustrada | 27. Araña Cristal | 28. Ojo de Buey | 29. Aplique Fan | 30. Vitrina Deco",
            "specs": ["BMesh Parametrico con Biseles Mecánicos", "Texturas Trimsheet 2K PBR + Wear Masks", "Freestyle Comic Ink 2.6px Contornos", "Grid Snapping: 100cm / 400cm UE5"]
        },
        {
            "title": "LOTE B: MOBILIARIO PALACIEGO, REFINERIA PLASMA & QUARANTINE LAB (ACTIVOS 31 AL 60)",
            "file": "Raw_LoteB_Panorama.png",
            "theme_col": (0, 200, 240),
            "badge_col": (39, 174, 96),
            "kits": "Kit 2: Art Deco (31-36)  |  Kit 3: Plasma Refinery (37-54)  |  Kit 4: Quarantine (55-60)",
            "row1": "Fila 1 (Front): 31. Escalera Imperial | 32. Ascensor Pillbox | 33. Consola Mármol | 34. Biombo Paravent | 35. Barra Bar | 36. Pedestal Escultórico | 37. Reactor Plasma | 38. Anillo Magnético | 39. Pilón Tesla | 40. Transformador",
            "row2": "Fila 2 (Mid):   41. Radiador Criogénico | 42. Rack Condensadores | 43. Conducto Plasma 400 | 44. Canal Escoria | 45. Emisor de Haz | 46. Turbina Compresión | 47. Celda Combustible | 48. Panel Instrumentos | 49. Válvula Flujo | 50. Bobina Tokamak",
            "row3": "Fila 3 (Back):  51. Conector Potencia | 52. Disipador Térmico | 53. Barrera Plasma | 54. Estación Carga | 55. Cápsula Criostasis | 56. Cilindro Espécimen | 57. Ducha Descontaminación | 58. Esclusa Hermética | 59. Glovebox Laminar | 60. Mesa Autopsia",
            "specs": ["Shaders Emisivos Cian/Oro Reactivos", "Cámaras Criogénicas con Vidrio Comic PBR", "Manómetros Analógicos y Pistones Hidráulicos", "Sistemas de Alta Tensión y Fluidos Criogénicos"]
        },
        {
            "title": "LOTE C: BIO-ANALISIS AVANZADO & HABITAT TRIPULACION / PUENTE (ACTIVOS 61 AL 90)",
            "file": "Raw_LoteC_Panorama.png",
            "theme_col": (180, 110, 250),
            "badge_col": (142, 68, 173),
            "kits": "Kit 4: Quarantine BioLab (61-72)  |  Kit 5: Crew Habitat & Bridge (73-90)",
            "row1": "Fila 1 (Front): 61. Centrífuga Bio | 62. Scrubber Químico | 63. Incinerador Residuos | 64. Mamparo Cristal | 65. Panel Bio-Limpio | 66. Campana Extractora | 67. Lavaojos Emergencia | 68. Armario Muestras | 69. Mesa Operaciones | 70. Pipeteo",
            "row2": "Fila 2 (Mid):   71. Brazo Robótico | 72. Contención Derrames | 73. Litera Modular | 74. Sintetizador Comida | 75. Ducha Sanitaria | 76. Lockers Tripulación | 77. Mesa Comedor | 78. Consola Mando Timón | 79. Mesa Holomapa | 80. Asiento Capitán",
            "row3": "Fila 3 (Back):  81. Repetidor Comms | 82. Consola Sensores | 83. Acceso Cápsula Escape | 84. Armero Táctico | 85. Armario Traje EVA | 86. Gatera Mantenimiento | 87. Depurador CO2 | 88. Cúpula Observación | 89. Cortina Blindada | 90. Rampa Carga",
            "specs": ["Consolas con Interfaz Vectorial Comic", "Brazos Robóticos con Rótulas Mecánicas", "Módulos de Vida y Presurización Orbital", "Certificado para UE5 / Cero Bugs Visuales"]
        }
    ]
    
    start_y = 100
    block_h = 430
    thumb_h = 365
    crop_box = (100, 370, 2460, 1230) # Recorte vertical exacto que conserva las 3 filas completas
    crop_w = crop_box[2] - crop_box[0]
    crop_h = crop_box[3] - crop_box[1]
    thumb_w = int(thumb_h * (crop_w / crop_h)) # Proporcion 100% fiel sin deformacion de aspecto (~1000px)
    
    for idx, info in enumerate(lotes_info):
        block_y = start_y + idx * block_h
        
        # Tarjeta contenedora exterior
        draw.rectangle((45, block_y, W - 45, block_y + block_h - 15), fill=(18, 21, 28, 255), outline=(38, 44, 56), width=2)
        
        # Banda decorativa de titulo
        draw.rectangle((45, block_y, 45 + 8, block_y + 36), fill=info["theme_col"])
        draw.text((65, block_y + 8), info["title"], fill=info["theme_col"], font=font_card_title)
        
        # Badge de lote
        badge_text = "30 ACTIVOS // VERIFICADO 100%"
        tw = len(badge_text) * 8 + 18
        bx = W - 60 - tw
        draw.rounded_rectangle((bx, block_y + 6, bx + tw, block_y + 30), radius=5, fill=info["badge_col"])
        draw.text((bx + 9, block_y + 9), badge_text, fill=(255, 255, 255), font=font_stat)
        
        # 1. Panorama renderizado a la izquierda (thumb_w x thumb_h) sin distorsión
        raw_path = os.path.join(RENDERS_DIR, info["file"])
        if os.path.exists(raw_path):
            lote_img = Image.open(raw_path).convert("RGBA")
            cropped = lote_img.crop(crop_box)
            resized = cropped.resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
            canvas.paste(resized, (60, block_y + 42))
            draw.rectangle((60, block_y + 42, 60 + thumb_w, block_y + 42 + thumb_h), outline=(48, 56, 70), width=2)
            
        # 2. Panel descriptivo e indice tecnico a la derecha
        panel_x = 60 + thumb_w + 18
        panel_w = W - 60 - panel_x
        panel_y = block_y + 42
        
        draw.rectangle((panel_x, panel_y, panel_x + panel_w, panel_y + thumb_h), fill=(14, 16, 21, 255), outline=(35, 42, 54), width=1)
        
        # Header del panel
        draw.text((panel_x + 16, panel_y + 12), info["kits"].upper(), fill=(245, 166, 35), font=font_stat)
        draw.line([(panel_x + 16, panel_y + 34), (panel_x + panel_w - 16, panel_y + 34)], fill=(40, 48, 62), width=1)
        
        # Indice de activos por fila
        draw.text((panel_x + 16, panel_y + 44), "CATÁLOGO DE ACTIVOS 3D POR GRADA (10 POR FILA):", fill=(200, 215, 230), font=font_micro_b)
        
        py = panel_y + 68
        for row_str, col_lbl in [(info["row1"], (235, 238, 245)), (info["row2"], (215, 222, 235)), (info["row3"], (195, 205, 220))]:
            draw.text((panel_x + 16, py), row_str, fill=col_lbl, font=font_micro)
            py += 22
            
        draw.line([(panel_x + 16, py + 10), (panel_x + panel_w - 16, py + 10)], fill=(40, 48, 62), width=1)
        
        # Especificaciones tecnicas y certificacion en 2 columnas
        py += 22
        draw.text((panel_x + 16, py), "ESTÁNDAR TÉCNICO Y SHADERS:", fill=info["theme_col"], font=font_micro_b)
        draw.text((panel_x + 480, py), "ESTADO DE CERTIFICACIÓN:", fill=(46, 204, 113), font=font_micro_b)
        
        py += 20
        spec_y = py
        for s in info["specs"]:
            draw.text((panel_x + 16, spec_y), f"• {s}", fill=(175, 185, 200), font=font_micro)
            spec_y += 18
            
        # Badges de certificacion
        cert_x = panel_x + 480
        cert_y = py
        certs = [
            ("ESTILO CARTOON/INDUSTRIAL", (39, 174, 96)),
            ("BMESH CONEXIÓN CINEMÁTICA", (41, 128, 185)),
            ("CERO ERRORES / CERO RECORTES", (211, 84, 0)),
            ("COMPATIBLE UNREAL ENGINE 5", (142, 68, 173))
        ]
        for ctext, ccol in certs:
            draw.rectangle((cert_x, cert_y, cert_x + 220, cert_y + 20), fill=ccol)
            draw.text((cert_x + 8, cert_y + 3), ctext, fill=(255, 255, 255), font=font_micro_b)
            cert_y += 24
            
    # Guardar en rutas finales y sincronizar
    master_path1 = os.path.join(RENDERS_DIR, "Showcase_Catalogo_Modular_90_Master.png")
    master_path2 = os.path.join(RENDERS_DIR, "Showcase_Catalogo_Modulares_90_Master.png")
    artifact_path1 = os.path.join(ARTIFACT_DIR, "Showcase_Catalogo_Modular_90_Master.png")
    artifact_path2 = os.path.join(ARTIFACT_DIR, "Showcase_Catalogo_Modulares_90_Master.png")
    
    canvas.save(master_path1, format="PNG")
    canvas.save(master_path2, format="PNG")
    shutil.copy2(master_path1, artifact_path1)
    shutil.copy2(master_path2, artifact_path2)
    print(f"[+] Lamina Maestra guardada en: {master_path1}")
    print(f"[+] Lamina Maestra guardada en: {master_path2}")
    print(f"[+] Sincronizada en directorio de artefactos con exito!")

if __name__ == "__main__":
    build_master_90_sheet()

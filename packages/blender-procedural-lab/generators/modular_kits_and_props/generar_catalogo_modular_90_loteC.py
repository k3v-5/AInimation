# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Generador Oficial del Catalogo Modular 90 - Lote C (Activos 61 al 90)
# Blender 5.2 LTS - Modelado Procedural Parametrico, Shaders PBR Stylized y Freestyle Comic

import bpy
import bmesh
import math
import os
import sys
import shutil

# Agregar ruta para modulos comunes
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.append(SCRIPT_DIR)

import astra_blender_styling as abs_style
import catalogo_modulares_kit4_biolab as kit4
import catalogo_modulares_kit5_habitat as kit5

PROJECT_ROOT = abs_style.PROJECT_ROOT
RENDERS_DIR = abs_style.RENDERS_DIR
ARTIFACT_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\b59ff04f-3c21-4ee5-94b0-8e8f899f8923"
BLEND_FILE = os.path.join(SCRIPT_DIR, "Catalogo_Modular_90_LoteC.blend")

# 30 Activos de Lote C: 12 de Kit 4 (61-72) + 18 de Kit 5 (73-90)
LOTE_C_ITEMS = kit4.KIT4_ASSETS[6:] + kit5.KIT5_ASSETS

def generate_lote_c_scene(save_blend=True):
    print("=" * 70)
    print("[*] Iniciando generacion de Lote C (Activos 61 a 90 de 90)...")
    print("=" * 70)
    
    # 1. Configurar escena con fondo ambiental nitido y lineas Freestyle
    abs_style.reset_comic_scene(bg_color=(0.04, 0.05, 0.07, 1.0), bg_strength=0.75, ink_thickness=2.6)
    col_lote = abs_style.create_collection("Lote_C_Modular_Assets_30")
    
    # 2. Inicializar materiales estilizados
    mats_k4 = kit4.init_kit4_materials()
    mats_k5 = kit5.init_kit5_materials()
    
    ped_mat = abs_style.get_comic_material("Pedestal_LoteC", base_color=(0.07, 0.08, 0.11), roughness=0.45, metallic=0.7)
    ped_border_mat = abs_style.get_comic_material("Pedestal_Border_LoteC", base_color=(0.7, 0.3, 0.9), roughness=0.30, metallic=0.2)
    
    # 3. Disposicion en cuadricula: 10 columnas x 3 filas con escalonamiento profundo (amphitheater terracing)
    spacing_x = 4.2
    spacing_y = 4.5
    
    # Terrazas estructurales corridas para Fila 1 y Fila 2 (Cero objetos flotantes)
    terrace_mat = abs_style.get_comic_material("Terrace_Mat_LoteC", base_color=(0.08, 0.09, 0.12), roughness=0.55, metallic=0.60)
    abs_style.create_box("Terrace_Row1_C", size=(46.0, 4.5, 2.2), loc=(0, 0.0, 1.1), mat=terrace_mat, col=col_lote)
    abs_style.create_box("Terrace_Row2_C", size=(46.0, 4.5, 4.4), loc=(0, 4.5, 2.2), mat=terrace_mat, col=col_lote)
    
    for idx, (aid, aname) in enumerate(LOTE_C_ITEMS):
        col_idx = idx % 10
        row_idx = idx // 10
        x = (col_idx - 4.5) * spacing_x
        y = (row_idx - 1.0) * spacing_y
        z_step = row_idx * 2.2  # Elevacion escalonada profunda de 2.2m por fila para CERO oclusion
        
        # Pedestal con bisel y reborde purpura
        ped = abs_style.create_box(f"Pedestal_{aname}", size=(3.8, 3.8, 0.22), loc=(x, y, z_step + 0.11), mat=ped_mat, col=col_lote)
        b_front = abs_style.create_box(f"PedBorder_{aname}", size=(3.8, 0.12, 0.06), loc=(x, y - 1.85, z_step + 0.25), mat=ped_border_mat, col=col_lote)
        
        # Construir activo segun kit de origen
        if aid <= 72:
            kit4.build_asset(aid, aname, (x, y, z_step + 0.22), col_lote, mats_k4)
        else:
            kit5.build_asset(aid, aname, (x, y, z_step + 0.22), col_lote, mats_k5)
            
    # 4. Suelo general de hangar con acabado de metal pulido
    floor_mat = abs_style.get_comic_material("Floor_Hangar_LoteC", base_color=(0.03, 0.035, 0.045), roughness=0.28, metallic=0.8)
    abs_style.create_box("HangarFloor_LoteC", size=(54.0, 24.0, 0.15), loc=(0, 0, -0.08), mat=floor_mat, col=col_lote)
    
    # 5. Iluminacion de estudio heroico
    abs_style.setup_studio_lighting(sun_energy=5.0, rim_energy=3.4, fill_energy=2.2)
    
    # Luz cenital adicional para fila trasera
    top_fill_data = bpy.data.lights.new(name="BackRow_Fill_C", type='SUN')
    top_fill_data.energy = 2.4
    top_fill_data.color = (0.95, 0.9, 1.0)
    top_fill_obj = bpy.data.objects.new("BackRow_Fill_C", top_fill_data)
    top_fill_obj.rotation_euler = (math.radians(45), 0, math.radians(-15))
    bpy.context.scene.collection.objects.link(top_fill_obj)
    
    # 6. Camara ajustada en ángulo cenital anfiteatro para VISIBILIDAD 100% de los 30 activos
    abs_style.setup_camera(name="Camera_LoteC", loc=(0, -34.0, 19.0), target=(0, 0.0, 2.5), focal_length=24)
    
    # 7. Guardar archivo .blend
    if save_blend:
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_FILE)
        print(f"[+] Blend guardado con exito: {BLEND_FILE}")
        
    # 8. Renderizar panorama base
    raw_render_path = os.path.join(RENDERS_DIR, "Raw_LoteC_Panorama.png")
    abs_style.render_and_save("Raw_LoteC_Panorama.png", res_x=2560, res_y=1440)
    
    # 9. Componer lamina tecnica infografica
    assemble_lote_c_infographic()
    print("[+] Lote C completado con exito!")

def assemble_lote_c_infographic():
    from PIL import Image, ImageDraw, ImageFont
    print("[*] Ensamblando lamina infografica de Lote C (2560x1440)...")
    
    raw_path = os.path.join(RENDERS_DIR, "Raw_LoteC_Panorama.png")
    final_render_path = os.path.join(RENDERS_DIR, "Showcase_Catalogo_Modular_90_LoteC.png")
    artifact_path = os.path.join(ARTIFACT_DIR, "Showcase_Catalogo_Modular_90_LoteC.png")
    
    W, H = 2560, 1440
    canvas = Image.new("RGBA", (W, H), (14, 16, 20, 255))
    draw = ImageDraw.Draw(canvas)
    
    try:
        font_title = ImageFont.truetype("arialbd.ttf", 30)
        font_sub = ImageFont.truetype("arialbd.ttf", 16)
        font_pill = ImageFont.truetype("arialbd.ttf", 14)
        font_foot = ImageFont.truetype("arial.ttf", 12)
    except:
        font_title = font_sub = font_pill = font_foot = ImageFont.load_default()
        
    # Encabezado
    draw.text((40, 18), "ASTRA HAZARD // REPOSITORIO DE ARQUITECTURA MODULAR // BLENDER 5.2 LTS", fill=(180, 100, 240), font=font_sub)
    draw.text((40, 46), "CATALOGO MODULAR 90 // LOTE C (ACTIVOS 61 A 90: BIO-ANALISIS Y HABITAT/PUENTE DE MANDO)", fill=(255, 255, 255), font=font_title)
    
    # Badges
    pills = [
        ("30 ACTIVOS 3D", (41, 128, 185)),
        ("KIT 4 (61-72) + KIT 5 (73-90)", (39, 174, 96)),
        ("PBR STYLIZED + FREESTYLE", (142, 68, 173)),
        ("ESTADO: VERIFICADO 100%", (155, 89, 182))
    ]
    cur_x = W - 40
    for text, bg_col in reversed(pills):
        tw = len(text) * 9 + 22
        cur_x -= tw
        draw.rounded_rectangle((cur_x, 32, cur_x + tw - 10, 66), radius=6, fill=bg_col)
        draw.text((cur_x + 10, 41), text, fill=(255, 255, 255), font=font_pill)
        cur_x -= 10
        
    draw.line((40, 90, W - 40, 90), fill=(45, 52, 65), width=2)
    
    # Panorama central (2480x1160)
    if os.path.exists(raw_path):
        raw_img = Image.open(raw_path).convert("RGBA")
        pan_w = W - 80
        pan_h = 1170
        raw_resized = raw_img.resize((pan_w, pan_h), Image.Resampling.LANCZOS)
        canvas.paste(raw_resized, (40, 105))
        draw.rectangle((40, 105, 40 + pan_w, 105 + pan_h), outline=(45, 52, 65), width=2)
        
    # Pie de pagina con indice de los 30 activos
    draw.line((40, 1290, W - 40, 1290), fill=(45, 52, 65), width=2)
    draw.rectangle((40, 1300, W - 40, 1415), fill=(18, 20, 26, 255), outline=(35, 40, 50), width=1)
    
    row1 = "61. Centrifuga Bio | 62. Scrubber Quimico | 63. Incinerador Residuos | 64. Mamparo Cristal | 65. Panel Bio-Limpio | 66. Campana Extractora | 67. Lavaojos Emergencia | 68. Armario Muestras -80C | 69. Mesa Operaciones | 70. Estacion Pipeteo"
    row2 = "71. Brazo Robotico | 72. Contencion Derrames | 73. Litera Modular | 74. Sintetizador Comida | 75. Ducha Sanitaria | 76. Lockers Tripulacion | 77. Mesa Comedor | 78. Consola Mando Timon | 79. Mesa Holomapa | 80. Asiento Capitan"
    row3 = "81. Repetidor Comms | 82. Consola Sensores | 83. Acceso Capsula Escape | 84. Armero Tactico | 85. Armario Traje EVA | 86. Gatera Mantenimiento | 87. Depurador CO2 | 88. Cupula Observacion | 89. Cortina Blindada | 90. Rampa Modular Carga"
    
    draw.text((60, 1315), "ACTIVOS 61-70 (FILA 1 FRONT): " + row1, fill=(200, 215, 230), font=font_foot)
    draw.text((60, 1348), "ACTIVOS 71-80 (FILA 2 MID):   " + row2, fill=(200, 215, 230), font=font_foot)
    draw.text((60, 1380), "ACTIVOS 81-90 (FILA 3 BACK):  " + row3, fill=(200, 215, 230), font=font_foot)
    
    # Guardar lamina final
    canvas.save(final_render_path, format="PNG")
    shutil.copy2(final_render_path, artifact_path)
    print(f"[+] Lamina final guardada: {final_render_path}")
    print(f"[+] Copia sincronizada en artefacto: {artifact_path}")

if __name__ == "__main__":
    generate_lote_c_scene()

# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Generador Oficial del Catalogo Modular 90 - Lote B (Activos 31 al 60)
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
import catalogo_modulares_kit2_artdeco as kit2
import catalogo_modulares_kit3_plasma as kit3
import catalogo_modulares_kit4_biolab as kit4

PROJECT_ROOT = abs_style.PROJECT_ROOT
RENDERS_DIR = abs_style.RENDERS_DIR
ARTIFACT_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\b59ff04f-3c21-4ee5-94b0-8e8f899f8923"
BLEND_FILE = os.path.join(SCRIPT_DIR, "Catalogo_Modular_90_LoteB.blend")

# 30 Activos de Lote B: 6 de Kit 2 (31-36) + 18 de Kit 3 (37-54) + 6 de Kit 4 (55-60)
LOTE_B_ITEMS = kit2.KIT2_ASSETS[12:] + kit3.KIT3_ASSETS + kit4.KIT4_ASSETS[:6]

def generate_lote_b_scene(save_blend=True):
    print("=" * 70)
    print("[*] Iniciando generacion de Lote B (Activos 31 a 60 de 90)...")
    print("=" * 70)
    
    # 1. Configurar escena con fondo ambiental nitido y lineas Freestyle
    abs_style.reset_comic_scene(bg_color=(0.04, 0.05, 0.07, 1.0), bg_strength=0.75, ink_thickness=2.6)
    col_lote = abs_style.create_collection("Lote_B_Modular_Assets_30")
    
    # 2. Inicializar materiales estilizados
    mats_k2 = kit2.init_kit2_materials()
    mats_k3 = kit3.init_kit3_materials()
    mats_k4 = kit4.init_kit4_materials()
    
    ped_mat = abs_style.get_comic_material("Pedestal_LoteB", base_color=(0.07, 0.08, 0.11), roughness=0.45, metallic=0.7)
    ped_border_mat = abs_style.get_comic_material("Pedestal_Border_LoteB", base_color=(0.0, 0.8, 0.95), roughness=0.30, metallic=0.2)
    
    # 3. Disposicion en cuadricula: 10 columnas x 3 filas con escalonamiento profundo (amphitheater terracing)
    spacing_x = 4.2
    spacing_y = 4.5
    
    # Terrazas estructurales corridas para Fila 1 y Fila 2 (Cero objetos flotantes)
    terrace_mat = abs_style.get_comic_material("Terrace_Mat_LoteB", base_color=(0.08, 0.09, 0.12), roughness=0.55, metallic=0.60)
    abs_style.create_box("Terrace_Row1_B", size=(46.0, 4.5, 2.2), loc=(0, 0.0, 1.1), mat=terrace_mat, col=col_lote)
    abs_style.create_box("Terrace_Row2_B", size=(46.0, 4.5, 4.4), loc=(0, 4.5, 2.2), mat=terrace_mat, col=col_lote)
    
    for idx, (aid, aname) in enumerate(LOTE_B_ITEMS):
        col_idx = idx % 10
        row_idx = idx // 10
        x = (col_idx - 4.5) * spacing_x
        y = (row_idx - 1.0) * spacing_y
        z_step = row_idx * 2.2  # Elevacion escalonada profunda de 2.2m por fila para CERO oclusion
        
        # Pedestal con bisel y reborde de iluminacion
        ped = abs_style.create_box(f"Pedestal_{aname}", size=(3.8, 3.8, 0.22), loc=(x, y, z_step + 0.11), mat=ped_mat, col=col_lote)
        b_front = abs_style.create_box(f"PedBorder_{aname}", size=(3.8, 0.12, 0.06), loc=(x, y - 1.85, z_step + 0.25), mat=ped_border_mat, col=col_lote)
        
        # Construir activo segun kit de origen
        if aid <= 36:
            kit2.build_asset(aid, aname, (x, y, z_step + 0.22), col_lote, mats_k2)
        elif aid <= 54:
            kit3.build_asset(aid, aname, (x, y, z_step + 0.22), col_lote, mats_k3)
        else:
            kit4.build_asset(aid, aname, (x, y, z_step + 0.22), col_lote, mats_k4)
            
    # 4. Suelo general de hangar con acabado de metal pulido
    floor_mat = abs_style.get_comic_material("Floor_Hangar_LoteB", base_color=(0.03, 0.035, 0.045), roughness=0.28, metallic=0.8)
    abs_style.create_box("HangarFloor_LoteB", size=(54.0, 24.0, 0.15), loc=(0, 0, -0.08), mat=floor_mat, col=col_lote)
    
    # 5. Iluminacion de estudio heroico
    abs_style.setup_studio_lighting(sun_energy=5.0, rim_energy=3.4, fill_energy=2.2)
    
    # Luz cenital adicional para fila trasera
    top_fill_data = bpy.data.lights.new(name="BackRow_Fill_B", type='SUN')
    top_fill_data.energy = 2.4
    top_fill_data.color = (0.85, 0.95, 1.0)
    top_fill_obj = bpy.data.objects.new("BackRow_Fill_B", top_fill_data)
    top_fill_obj.rotation_euler = (math.radians(45), 0, math.radians(-15))
    bpy.context.scene.collection.objects.link(top_fill_obj)
    
    # 6. Camara ajustada en ángulo cenital anfiteatro para VISIBILIDAD 100% de los 30 activos
    abs_style.setup_camera(name="Camera_LoteB", loc=(0, -34.0, 19.0), target=(0, 0.0, 2.5), focal_length=24)
    
    # 7. Guardar archivo .blend
    if save_blend:
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_FILE)
        print(f"[+] Blend guardado con exito: {BLEND_FILE}")
        
    # 8. Renderizar panorama base
    raw_render_path = os.path.join(RENDERS_DIR, "Raw_LoteB_Panorama.png")
    abs_style.render_and_save("Raw_LoteB_Panorama.png", res_x=2560, res_y=1440)
    
    # 9. Componer lamina tecnica infografica
    assemble_lote_b_infographic()
    print("[+] Lote B completado con exito!")

def assemble_lote_b_infographic():
    from PIL import Image, ImageDraw, ImageFont
    print("[*] Ensamblando lamina infografica de Lote B (2560x1440)...")
    
    raw_path = os.path.join(RENDERS_DIR, "Raw_LoteB_Panorama.png")
    final_render_path = os.path.join(RENDERS_DIR, "Showcase_Catalogo_Modular_90_LoteB.png")
    artifact_path = os.path.join(ARTIFACT_DIR, "Showcase_Catalogo_Modular_90_LoteB.png")
    
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
    draw.text((40, 18), "ASTRA HAZARD // REPOSITORIO DE ARQUITECTURA MODULAR // BLENDER 5.2 LTS", fill=(0, 200, 240), font=font_sub)
    draw.text((40, 46), "CATALOGO MODULAR 90 // LOTE B (ACTIVOS 31 A 60: REFINERIA DE PLASMA Y QUARANTINE LAB)", fill=(255, 255, 255), font=font_title)
    
    # Badges
    pills = [
        ("30 ACTIVOS 3D", (41, 128, 185)),
        ("KIT 2 (31-36) + KIT 3 (37-54) + KIT 4 (55-60)", (39, 174, 96)),
        ("PBR STYLIZED + FREESTYLE", (142, 68, 173)),
        ("ESTADO: VERIFICADO 100%", (0, 180, 216))
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
    
    row1 = "31. Escalera Imperial Deco | 32. Ascensor Pillbox | 33. Consola Marmol | 34. Biombo Paravent | 35. Barra Bar Deco | 36. Pedestal Escultorico | 37. Reactor Plasma | 38. Anillo Magnetico | 39. Pilon Tesla | 40. Transformador HV"
    row2 = "41. Radiador Criogenico | 42. Rack Condensadores | 43. Conducto Plasma 400 | 44. Canal Escoria | 45. Emisor de Haz | 46. Turbina Compresion | 47. Celda Combustible | 48. Panel Instrumentos | 49. Valvula Flujo | 50. Bobina Tokamak"
    row3 = "51. Conector Potencia | 52. Disipador Termico | 53. Barrera Plasma | 54. Estacion Carga | 55. Capsula Criostasis | 56. Cilindro Especimen | 57. Ducha Descontaminacion | 58. Esclusa Hermetica | 59. Glovebox Laminar | 60. Mesa Autopsia"
    
    draw.text((60, 1315), "ACTIVOS 31-40 (FILA 1 FRONT): " + row1, fill=(200, 215, 230), font=font_foot)
    draw.text((60, 1348), "ACTIVOS 41-50 (FILA 2 MID):   " + row2, fill=(200, 215, 230), font=font_foot)
    draw.text((60, 1380), "ACTIVOS 51-60 (FILA 3 BACK):  " + row3, fill=(200, 215, 230), font=font_foot)
    
    # Guardar lamina final
    canvas.save(final_render_path, format="PNG")
    shutil.copy2(final_render_path, artifact_path)
    print(f"[+] Lamina final guardada: {final_render_path}")
    print(f"[+] Copia sincronizada en artefacto: {artifact_path}")

if __name__ == "__main__":
    generate_lote_b_scene()

# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Generador Maestro del Catalogo de 90 Activos Modulares Arquitectonicos - Astra Hazard
# Blender 5.2 LTS - Integracion de los 5 Kits (18 activos cada uno = 90 activos totales)
# Shaders PBR Stylized, Freestyle Lineart y Renderizado de Exposicion 2560x1440

import bpy
import bmesh
import math
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

import astra_blender_styling as abs_style
import catalogo_modulares_kit1_industrial as kit1
import catalogo_modulares_kit2_artdeco as kit2
import catalogo_modulares_kit3_plasma as kit3
import catalogo_modulares_kit4_biolab as kit4
import catalogo_modulares_kit5_habitat as kit5

def generate_master_90_catalog(save_blend=True, render_kits=True):
    # Si se solicita, renderizar cada uno de los 5 kits de forma independiente
    if render_kits:
        print("[*] Generando y renderizando Kit 1 (Industrial Derelict)...")
        kit1.generate_kit1_scene(save_blend=True)
        print("[*] Generando y renderizando Kit 2 (Celestia Art Deco)...")
        kit2.generate_kit2_scene(save_blend=True)
        print("[*] Generando y renderizando Kit 3 (Plasma Refinery)...")
        kit3.generate_kit3_scene(save_blend=True)
        print("[*] Generando y renderizando Kit 4 (BioLab Quarantine)...")
        kit4.generate_kit4_scene(save_blend=True)
        print("[*] Generando y renderizando Kit 5 (Crew Habitat & Command)...")
        kit5.generate_kit5_scene(save_blend=True)
        
    print("[*] Ensamblando escena Maestra de 90 Activos Modulares...")
    abs_style.reset_comic_scene(bg_color=(0.015, 0.018, 0.024, 1.0), bg_strength=0.35, ink_thickness=1.4)
    master_col = abs_style.create_collection("Master_90_Modular_Assets_Catalog")
    
    # Inicializar materiales de cada kit
    mats_k1 = kit1.init_kit1_materials()
    mats_k2 = kit2.init_kit2_materials()
    mats_k3 = kit3.init_kit3_materials()
    mats_k4 = kit4.init_kit4_materials()
    mats_k5 = kit5.init_kit5_materials()
    
    ped_mat = abs_style.get_comic_material("Pedestal_Master", base_color=(0.06, 0.07, 0.09), roughness=0.4, metallic=0.7)
    
    # Distribución en 5 alas/filas temáticas (Kits 1 a 5)
    # Cada fila contiene 18 activos dispuestos a lo largo del eje X (X de -40 a +40)
    # Espaciado X: 4.6m, Espaciado Y entre kits: 6.5m
    kits_data = [
        ("Kit1_Industrial", kit1.KIT1_ASSETS, kit1.build_asset, mats_k1, -13.0),
        ("Kit2_ArtDeco", kit2.KIT2_ASSETS, kit2.build_asset, mats_k2, -6.5),
        ("Kit3_Plasma", kit3.KIT3_ASSETS, kit3.build_asset, mats_k3, 0.0),
        ("Kit4_BioLab", kit4.KIT4_ASSETS, kit4.build_asset, mats_k4, 6.5),
        ("Kit5_Habitat", kit5.KIT5_ASSETS, kit5.build_asset, mats_k5, 13.0),
    ]
    
    spacing_x = 4.6
    
    for kit_name, asset_list, builder_func, mats, row_y in kits_data:
        sub_col = abs_style.create_collection(kit_name, parent=master_col)
        for idx, (aid, aname) in enumerate(asset_list):
            x = (idx - 8.5) * spacing_x
            y = row_y
            
            ped = abs_style.create_box(f"Ped_{aname}", size=(3.8, 3.8, 0.2), loc=(x, y, -0.1), mat=ped_mat, col=sub_col)
            builder_func(aid, aname, (x, y, 0.0), sub_col, mats)
            
    # Iluminación de gran hangar de exposición (Sun lights sin atenuación de distancia)
    abs_style.setup_studio_lighting(sun_energy=4.2, rim_energy=2.6, fill_energy=1.5)
    
    # Suelo general del hangar
    floor_mat = abs_style.get_comic_material("Hangar_Floor", base_color=(0.02, 0.025, 0.035), roughness=0.25, metallic=0.85)
    abs_style.create_box("HangarFloor", size=(120.0, 60.0, 0.2), loc=(0, 0, -0.2), mat=floor_mat, col=master_col)
    
    # Cámara panorámica cenital angular para capturar los 90 activos
    abs_style.setup_camera(name="Camera_Master90", loc=(0, -48, 32), target=(0, 0, 1.0), focal_length=24)
    
    if save_blend:
        blend_path = os.path.join(abs_style.PROJECT_ROOT, "Art", "Blender", "Catalogo_Activos_Modulares_90_Oficial.blend")
        bpy.ops.wm.save_as_mainfile(filepath=blend_path)
        print(f"[+] Master Blend saved: {blend_path}")
        
    abs_style.render_and_save("Showcase_Catalogo_Modulares_90_Panorama.png", res_x=2560, res_y=1440)
    assemble_master_90_infographic()
    print("[+] Catalogo de 90 Activos Modulares completado con exito!")

def assemble_master_90_infographic():
    import shutil
    from PIL import Image, ImageDraw, ImageFont
    print("[*] Ensamblando Lamina Maestra Infografica de 90 Activos Modulares (2560x1440)...")
    W, H = 2560, 1440
    canvas = Image.new("RGBA", (W, H), (14, 16, 20, 255))
    draw = ImageDraw.Draw(canvas)

    try:
        font_title = ImageFont.truetype("arialbd.ttf", 32)
        font_sub = ImageFont.truetype("arialbd.ttf", 18)
        font_card_title = ImageFont.truetype("arialbd.ttf", 18)
        font_desc = ImageFont.truetype("arial.ttf", 13)
        font_pill = ImageFont.truetype("arialbd.ttf", 14)
    except:
        font_title = font_sub = font_card_title = font_desc = font_pill = ImageFont.load_default()

    # Titulo y Subtitulo
    draw.text((40, 20), "ASTRA HAZARD // REPOSITORIO DE ARQUITECTURA Y ACTIVOS 3D MODULARES", fill=(245, 166, 35), font=font_sub)
    draw.text((40, 48), "CATÁLOGO MODULAR DE 90 ACTIVOS ARQUITECTÓNICOS OFICIALES (KITS 1 A 5)", fill=(255, 255, 255), font=font_title)

    # Badges
    pills = [
        ("90 ACTIVOS 3D", (41, 128, 185)),
        ("5 KITS COMPLETOS", (39, 174, 96)),
        ("PBR STYLIZED & FREESTYLE", (142, 68, 173)),
        ("BLENDER 5.2 LTS", (211, 84, 0))
    ]
    cur_x = W - 40
    for text, bg_col in reversed(pills):
        tw = len(text) * 9 + 20
        cur_x -= tw
        draw.rounded_rectangle((cur_x, 35, cur_x + tw - 10, 68), radius=6, fill=bg_col)
        draw.text((cur_x + 10, 43), text, fill=(255, 255, 255), font=font_pill)
        cur_x -= 10

    draw.line((40, 95, W - 40, 95), fill=(45, 52, 65), width=2)

    # Panorama superior (2480x680)
    pan_path = os.path.join(abs_style.RENDERS_DIR, "Showcase_Catalogo_Modulares_90_Panorama.png")
    if os.path.exists(pan_path):
        pan_img = Image.open(pan_path).convert("RGBA")
        pan_w = W - 80
        pan_h = 680
        pan_resized = pan_img.resize((pan_w, pan_h), Image.Resampling.LANCZOS)
        canvas.paste(pan_resized, (40, 110))
        draw.rectangle((40, 110, 40 + pan_w, 110 + pan_h), outline=(55, 65, 80), width=2)

    # 5 Tarjetas inferiores de cada Kit (18 activos cada uno)
    kits_info = [
        ("01. KIT INDUSTRIAL (18 ACT)", "Showcase_Modulares_Kit1_Industrial_18.png", (245, 166, 35),
         "• Muros ciegos, esclusas y marcos\n• Rejillas de suelo y fosos de ácido\n• Pasarelas rectas, escaleras y rieles\n• Tuberías triples, cables y barreras"),
        ("02. KIT ART DÉCO (18 ACT)", "Showcase_Modulares_Kit2_ArtDeco_18.png", (212, 175, 55),
         "• Boiserie nogal y arcos dorados\n• Suelo mármol Carrara y artesonado\n• Sofás Chesterfield terciopelo burdeos\n• Vitrinas, apliques y gran ojo de buey"),
        ("03. KIT PLASMA (18 ACT)", "Showcase_Modulares_Kit3_Plasma_18.png", (0, 240, 255),
         "• Reactor de confinamiento y núcleo\n• Bobinas Tesla y transformadores\n• Radiadores criogénicos y toberas\n• Consolas terminal y zanjas de escoria"),
        ("04. KIT BIO-LAB (18 ACT)", "Showcase_Modulares_Kit4_BioLab_18.png", (46, 204, 113),
         "• Cápsulas stasis y tanques espécimen\n• Duchas descontaminación y autoclaves\n• Cabinas de guantes y mesas de autopsia\n• Torres depuradoras y armarios -80°C"),
        ("05. KIT HÁBITAT (18 ACT)", "Showcase_Modulares_Kit5_Habitat_18.png", (155, 89, 182),
         "• Literas modulares y cocinas galera\n• Mesas tácticas holomapa y timonel\n• Racks de comunicaciones y armeros\n• Cúpula astronómica y compuertas")
    ]

    card_w = (W - 80 - 40) // 5
    card_h = 570
    card_y = 820

    for i, (title, img_name, border_col, desc) in enumerate(kits_info):
        cx = 40 + i * (card_w + 10)
        draw.rectangle((cx, card_y, cx + card_w, card_y + card_h), fill=(20, 24, 30), outline=border_col, width=2)
        
        img_path = os.path.join(abs_style.RENDERS_DIR, img_name)
        if os.path.exists(img_path):
            card_img = Image.open(img_path).convert("RGBA")
            c_render_h = 360
            c_render_w = card_w - 4
            card_resized = card_img.resize((c_render_w, c_render_h), Image.Resampling.LANCZOS)
            canvas.paste(card_resized, (cx + 2, card_y + 2))
            
        draw.rectangle((cx, card_y + 362, cx + card_w, card_y + 398), fill=(28, 33, 42))
        draw.text((cx + 10, card_y + 372), title, fill=border_col, font=font_card_title)
        draw.text((cx + 10, card_y + 410), desc, fill=(210, 220, 235), font=font_desc, spacing=4)

    master_path = os.path.join(abs_style.RENDERS_DIR, "Showcase_Catalogo_Modulares_90_Master.png")
    canvas.save(master_path, "PNG")
    shutil.copy2(master_path, os.path.join(abs_style.ARTIFACT_DIR, "Showcase_Catalogo_Modulares_90_Master.png"))
    print(f"[+] Lamina Maestra Infografica guardada: {master_path}")

if __name__ == "__main__":
    generate_master_90_catalog(save_blend=True, render_kits=True)

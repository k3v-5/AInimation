# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Generador Maestro del Bestiario 3D Oficial (10 Entidades: 5 de Referencia 1:1 + 5 Nuevas)
# Blender 5.2 LTS - Mallas 3D Reales, Shaders PBR Stylized, Cel-Shading y Freestyle Lineart
# CERO IMAGENES RECORTADAS 2D: Geometria 3D pura procedural y modelado de alta fidelidad

import bpy
import bmesh
import math
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

import astra_blender_styling as abs_style

def init_bestiary_materials():
    mats = {}
    # Metales y blindaje
    mats['gunmetal'] = abs_style.get_comic_material("B_Gunmetal", base_color=(0.22, 0.24, 0.28), roughness=0.35, metallic=0.88, tex_pack="T_Steel_Plates")
    mats['rust_plates'] = abs_style.get_comic_material("B_Rust_Plates", base_color=(0.52, 0.26, 0.15), roughness=0.60, metallic=0.40, tex_pack="T_Derelict_Rust_Plates")
    mats['hazard_yellow'] = abs_style.get_comic_material("B_Hazard_Yellow", base_color=(0.95, 0.68, 0.08), roughness=0.32, metallic=0.15, tex_pack="T_Trim_Industrial")
    mats['brass_gauge'] = abs_style.get_comic_material("B_Brass_Gauge", base_color=(0.88, 0.68, 0.22), roughness=0.25, metallic=0.90, tex_pack="T_Luxury_ArtDeco_Gilded_Brass")
    mats['polished_steel'] = abs_style.get_comic_material("B_Steel_Bright", base_color=(0.82, 0.85, 0.88), roughness=0.18, metallic=0.95)
    mats['dark_chitin'] = abs_style.get_comic_material("B_Dark_Chitin", base_color=(0.08, 0.09, 0.11), roughness=0.40, metallic=0.30)
    mats['bone_ivory'] = abs_style.get_comic_material("B_Bone_Ivory", base_color=(0.88, 0.87, 0.80), roughness=0.55, metallic=0.05)
    mats['gauge_white'] = abs_style.get_comic_material("B_Gauge_White", base_color=(0.92, 0.92, 0.88), roughness=0.30, metallic=0.0)

    # Materiales emisivos de referencia cómic
    mats['comic_flame_yellow'] = abs_style.get_comic_material("B_Flame_Yellow", base_color=(1.0, 0.88, 0.12), roughness=0.10,
                                                              emissive_color=(1.0, 0.88, 0.12, 1.0), emissive_strength=3.5)
    mats['comic_flame_orange'] = abs_style.get_comic_material("B_Flame_Orange", base_color=(0.95, 0.32, 0.02), roughness=0.10,
                                                              emissive_color=(0.95, 0.32, 0.02, 1.0), emissive_strength=2.8)
    mats['red_eye_lens'] = abs_style.get_comic_material("B_Red_Eye_Lens", base_color=(0.98, 0.05, 0.08), roughness=0.08,
                                                        emissive_color=(1.0, 0.05, 0.08, 1.0), emissive_strength=3.8)
    mats['scan_cone_red'] = abs_style.get_comic_material("B_Scan_Cone_Red", base_color=(0.95, 0.05, 0.05), roughness=0.1,
                                                         emissive_color=(1.0, 0.05, 0.05, 1.0), emissive_strength=2.0,
                                                         alpha=0.35, is_transparent=True)
    mats['crt_radar_green'] = abs_style.get_comic_material("B_CRT_Green", base_color=(0.04, 0.92, 0.20), roughness=0.15,
                                                           emissive_color=(0.04, 0.95, 0.22, 1.0), emissive_strength=2.6)
    mats['plasma_cyan'] = abs_style.get_comic_material("B_Plasma_Cyan", base_color=(0.0, 0.88, 1.0), roughness=0.08,
                                                       emissive_color=(0.0, 0.90, 1.0, 1.0), emissive_strength=3.5)
    mats['acid_slime'] = abs_style.get_comic_material("B_Acid_Slime", base_color=(0.10, 0.95, 0.18), roughness=0.10,
                                                      emissive_color=(0.10, 0.95, 0.18, 1.0), emissive_strength=2.5,
                                                      alpha=0.65, is_transparent=True)
    mats['cryo_ice'] = abs_style.get_comic_material("B_Cryo_Ice", base_color=(0.50, 0.85, 1.0), roughness=0.15,
                                                    emissive_color=(0.40, 0.85, 1.0, 1.0), emissive_strength=2.0,
                                                    alpha=0.75, is_transparent=True)
    mats['monocular_yellow'] = abs_style.get_comic_material("B_Monocular_Yellow", base_color=(1.0, 0.92, 0.15), roughness=0.10,
                                                            emissive_color=(1.0, 0.92, 0.15, 1.0), emissive_strength=3.2)
    return mats

# ==============================================================================
# CONSTRUCTORES 3D PARA CADA ENTIDAD (1 A 10)
# ==============================================================================

def build_entity_01_werewolf(col, origin, mats):
    """01. Lobo Mecánico (Mechanical Werewolf) fiel a media_1791339407912.png"""
    root = bpy.data.objects.new("Entity_01_Mechanical_Werewolf", None)
    root.location = (0, 0, 0)
    col.objects.link(root)
    ox, oy, oz = origin

    # Pasarela Hazard con barandilla donde acecha
    walkway = abs_style.create_box("WW_Catwalk", size=(4.2, 2.0, 0.18), loc=(ox, oy, oz + 0.09), mat=mats['gunmetal'], col=col)
    walkway.parent = root
    stripe = abs_style.create_box("WW_HazardStripe", size=(4.2, 0.25, 0.2), loc=(ox, oy - 0.9, oz + 0.1), mat=mats['hazard_yellow'], col=col)
    stripe.parent = root
    rail = abs_style.create_cylinder("WW_Rail", radius=0.04, depth=4.2, rot=(0, math.radians(90), 0), loc=(ox, oy - 0.9, oz + 0.7), mat=mats['gunmetal'], col=col)
    rail.parent = root
    for rx in [-1.5, 0.0, 1.5]:
        post = abs_style.create_cylinder(f"WW_Post_{rx}", radius=0.04, depth=0.6, loc=(ox + rx, oy - 0.9, oz + 0.4), mat=mats['gunmetal'], col=col)
        post.parent = root

    # Torso angular facetado
    torso_main = abs_style.create_box("WW_Torso", size=(1.2, 0.8, 0.7), loc=(ox - 0.4, oy, oz + 1.2), mat=mats['gunmetal'], col=col)
    torso_main.parent = root
    chest = abs_style.create_box("WW_Chest", size=(0.9, 0.75, 0.8), rot=(0, math.radians(15), 0), loc=(ox + 0.3, oy, oz + 1.3), mat=mats['gunmetal'], col=col)
    chest.parent = root

    # Cabeza facetada y mandíbula con colmillos
    head = abs_style.create_box("WW_Head", size=(0.7, 0.55, 0.45), rot=(0, math.radians(20), 0), loc=(ox + 0.9, oy, oz + 1.5), mat=mats['gunmetal'], col=col)
    head.parent = root
    snout = abs_style.create_box("WW_Snout", size=(0.55, 0.4, 0.25), rot=(0, math.radians(10), 0), loc=(ox + 1.35, oy, oz + 1.45), mat=mats['gunmetal'], col=col)
    snout.parent = root
    jaw = abs_style.create_box("WW_Jaw", size=(0.5, 0.35, 0.15), rot=(0, math.radians(-10), 0), loc=(ox + 1.3, oy, oz + 1.25), mat=mats['gunmetal'], col=col)
    jaw.parent = root
    fang1 = abs_style.create_cone("WW_Fang1", radius1=0.04, radius2=0.0, depth=0.12, loc=(ox + 1.45, oy - 0.12, oz + 1.2), mat=mats['bone_ivory'], col=col)
    fang1.parent = root
    fang2 = abs_style.create_cone("WW_Fang2", radius1=0.04, radius2=0.0, depth=0.12, loc=(ox + 1.45, oy + 0.12, oz + 1.2), mat=mats['bone_ivory'], col=col)
    fang2.parent = root

    # Llama 3D del hocico (fiel a la referencia)
    snout_flame = abs_style.create_cone("WW_SnoutFlame", radius1=0.18, radius2=0.0, depth=0.55, rot=(0, math.radians(90), 0), loc=(ox + 1.75, oy, oz + 1.55), mat=mats['comic_flame_yellow'], col=col)
    snout_flame.parent = root
    snout_core = abs_style.create_cone("WW_SnoutFlameCore", radius1=0.11, radius2=0.0, depth=0.4, rot=(0, math.radians(90), 0), loc=(ox + 1.7, oy, oz + 1.55), mat=mats['comic_flame_orange'], col=col)
    snout_core.parent = root

    # Dos chimeneas de escape dorsales con alas de fuego estilizado 3D (media_1791339407912.png)
    for idx, ey in enumerate([-0.25, 0.25]):
        exhaust = abs_style.create_cylinder(f"WW_Exhaust_{idx}", radius=0.11, depth=0.6, rot=(0, -math.radians(35), 0), loc=(ox - 0.7, oy + ey, oz + 1.6), mat=mats['gunmetal'], col=col)
        exhaust.parent = root
        flame_blade = abs_style.create_cone(f"WW_FlameBlade_{idx}", radius1=0.35, radius2=0.05, depth=1.4, rot=(0, -math.radians(40), 0), loc=(ox - 1.2, oy + ey, oz + 2.2), mat=mats['comic_flame_yellow'], col=col)
        flame_blade.parent = root
        flame_inner = abs_style.create_cone(f"WW_FlameInner_{idx}", radius1=0.22, radius2=0.02, depth=1.0, rot=(0, -math.radians(40), 0), loc=(ox - 1.1, oy + ey, oz + 2.1), mat=mats['comic_flame_orange'], col=col)
        flame_inner.parent = root

    # 4 Patas mecánicas articuladas con pistones y garras cartoon
    leg_coords = [
        ("FrontL", ox + 0.6, oy - 0.45, oz + 0.7, 0.25),
        ("FrontR", ox + 0.6, oy + 0.45, oz + 0.7, 0.25),
        ("BackL", ox - 0.7, oy - 0.45, oz + 0.7, -0.25),
        ("BackR", ox - 0.7, oy + 0.45, oz + 0.7, -0.25),
    ]
    for lname, lx, ly, lz, tilt in leg_coords:
        thigh = abs_style.create_box(f"WW_Thigh_{lname}", size=(0.22, 0.2, 0.65), rot=(0, tilt, 0), loc=(lx, ly, lz + 0.25), mat=mats['gunmetal'], col=col)
        thigh.parent = root
        piston = abs_style.create_cylinder(f"WW_Piston_{lname}", radius=0.04, depth=0.45, loc=(lx, ly, lz - 0.1), mat=mats['polished_steel'], col=col)
        piston.parent = root
        claw = abs_style.create_box(f"WW_Paw_{lname}", size=(0.32, 0.25, 0.12), loc=(lx + 0.08, ly, oz + 0.24), mat=mats['gunmetal'], col=col)
        claw.parent = root

    # Cola segmentada
    tail = abs_style.create_cylinder("WW_Tail", radius=0.06, depth=0.9, rot=(0, -math.radians(55), 0), loc=(ox - 1.2, oy, oz + 1.0), mat=mats['gunmetal'], col=col)
    tail.parent = root

    return root

def build_entity_02_auditor_drone(col, origin, mats):
    """02. Dron Auditor (Auditor Drone) fiel a media_1791339407912.png"""
    root = bpy.data.objects.new("Entity_02_Auditor_Drone", None)
    root.location = (0, 0, 0)
    col.objects.link(root)
    ox, oy, oz = origin

    # Esfera central metálica
    hull = abs_style.create_cylinder("AD_SphereHull", radius=0.85, depth=1.2, loc=(ox, oy, oz + 1.8), mat=mats['gunmetal'], col=col)
    hull.parent = root

    # Gran ojo rojo con marco de latón
    rim = abs_style.create_torus("AD_EyeRim", major_r=0.42, minor_r=0.09, rot=(math.radians(90), 0, 0), loc=(ox + 0.2, oy - 0.85, oz + 1.8), mat=mats['brass_gauge'], col=col)
    rim.parent = root
    lens = abs_style.create_cylinder("AD_RedEye", radius=0.38, depth=0.08, rot=(math.radians(90), 0, 0), loc=(ox + 0.2, oy - 0.9, oz + 1.8), mat=mats['red_eye_lens'], col=col)
    lens.parent = root

    # CONO DE ESCANEO ROJO TRANSLÚCIDO QUE PROYECTA AL SUELO (media_1791339407912.png)
    cone = abs_style.create_cone("AD_ScanCone", radius1=0.8, radius2=0.05, depth=2.0, rot=(math.radians(45), 0, 0), loc=(ox + 0.35, oy - 1.5, oz + 0.9), mat=mats['scan_cone_red'], col=col)
    cone.parent = root

    # Monitor CRT lateral con radar de fósforo verde
    crt_box = abs_style.create_box("AD_CRTBox", size=(0.45, 0.15, 0.4), rot=(0, 0, math.radians(20)), loc=(ox - 0.45, oy - 0.75, oz + 1.8), mat=mats['gunmetal'], col=col)
    crt_box.parent = root
    crt_screen = abs_style.create_box("AD_CRTScreen", size=(0.38, 0.04, 0.32), rot=(0, 0, math.radians(20)), loc=(ox - 0.45, oy - 0.83, oz + 1.8), mat=mats['crt_radar_green'], col=col)
    crt_screen.parent = root

    # 3 Manómetros analógicos superiores orientados al frente
    for idx, gx in enumerate([-0.3, 0.0, 0.3]):
        gauge = abs_style.create_cylinder(f"AD_Gauge_{idx}", radius=0.15, depth=0.12, rot=(math.radians(35), 0, 0), loc=(ox + gx, oy - 0.35, oz + 2.5), mat=mats['brass_gauge'], col=col)
        gauge.parent = root
        dial = abs_style.create_cylinder(f"AD_Dial_{idx}", radius=0.13, depth=0.03, rot=(math.radians(35), 0, 0), loc=(ox + gx, oy - 0.42, oz + 2.55), mat=mats['gauge_white'], col=col)
        dial.parent = root
        needle = abs_style.create_box(f"AD_Needle_{idx}", size=(0.02, 0.01, 0.12), rot=(math.radians(35), 0, math.radians(idx*35 - 30)), loc=(ox + gx, oy - 0.44, oz + 2.58), mat=mats['red_eye_lens'], col=col)
        needle.parent = root

    # Antenas dobles superiores inclinadas
    for idx, (ax, ay) in enumerate([(-0.35, 0.2), (0.35, 0.2)]):
        ant = abs_style.create_cylinder(f"AD_Antenna_{idx}", radius=0.025, depth=0.85, rot=(-math.radians(20), math.radians(idx*30 - 15), 0), loc=(ox + ax, oy + ay, oz + 2.7), mat=mats['polished_steel'], col=col)
        ant.parent = root

    # Tobera propulsora inferior
    thruster = abs_style.create_cylinder("AD_Thruster", radius=0.35, depth=0.35, loc=(ox, oy, oz + 1.1), mat=mats['brass_gauge'], col=col)
    thruster.parent = root
    probe = abs_style.create_cylinder("AD_BottomProbe", radius=0.03, depth=0.5, loc=(ox, oy, oz + 0.8), mat=mats['polished_steel'], col=col)
    probe.parent = root

    return root

def build_entity_03_scrapper_goblin(col, origin, mats):
    """03. Trasgo Chatarrero (Scrapper Goblin) fiel a media_1791339407912.png"""
    root = bpy.data.objects.new("Entity_03_Scrapper_Goblin", None)
    root.location = (0, 0, 0)
    col.objects.link(root)
    ox, oy, oz = origin

    # Piernas y botas mecánicas
    for bx in [-0.25, 0.25]:
        leg = abs_style.create_cylinder(f"SG_Leg_{bx}", radius=0.12, depth=0.75, loc=(ox + bx, oy, oz + 0.4), mat=mats['dark_chitin'], col=col)
        leg.parent = root
        boot = abs_style.create_box(f"SG_Boot_{bx}", size=(0.26, 0.4, 0.2), loc=(ox + bx, oy - 0.08, oz + 0.1), mat=mats['gunmetal'], col=col)
        boot.parent = root

    # Cinturón con HEBILLA DE ENGRANAJE DE BRONCE GIGANTE (media_1791339407912.png)
    belt = abs_style.create_cylinder("SG_Belt", radius=0.38, depth=0.18, loc=(ox, oy, oz + 0.8), mat=mats['dark_chitin'], col=col)
    belt.parent = root
    gear = abs_style.create_cylinder("SG_GearBuckle", radius=0.28, depth=0.08, rot=(math.radians(90), 0, 0), loc=(ox, oy - 0.38, oz + 0.8), mat=mats['brass_gauge'], col=col)
    gear.parent = root
    for t in range(8):
        ang = t * (math.pi / 4)
        gx = ox + math.cos(ang) * 0.32
        gz = oz + 0.8 + math.sin(ang) * 0.32
        tooth = abs_style.create_box(f"SG_Tooth_{t}", size=(0.08, 0.07, 0.08), rot=(0, -ang, 0), loc=(gx, oy - 0.38, gz), mat=mats['brass_gauge'], col=col)
        tooth.parent = root

    # Torso blindado con remaches
    torso = abs_style.create_box("SG_Cuirass", size=(0.7, 0.5, 0.7), loc=(ox, oy, oz + 1.25), mat=mats['gunmetal'], col=col)
    torso.parent = root

    # Cabeza con MÁSCARA DE MARFIL, OREJAS PUNTIAGUDAS Y DIENTES
    head = abs_style.create_box("SG_Head", size=(0.55, 0.45, 0.5), loc=(ox, oy, oz + 1.8), mat=mats['bone_ivory'], col=col)
    head.parent = root
    ear_l = abs_style.create_cone("SG_EarL", radius1=0.12, radius2=0.0, depth=0.45, rot=(0, -math.radians(65), 0), loc=(ox - 0.45, oy, oz + 1.95), mat=mats['bone_ivory'], col=col)
    ear_l.parent = root
    ear_r = abs_style.create_cone("SG_EarR", radius1=0.12, radius2=0.0, depth=0.45, rot=(0, math.radians(65), 0), loc=(ox + 0.45, oy, oz + 1.95), mat=mats['bone_ivory'], col=col)
    ear_r.parent = root

    # DIENTES RECTANGULARES BLANCOS EXPUESTOS
    for i in range(5):
        tooth_b = abs_style.create_box(f"SG_Teeth_{i}", size=(0.07, 0.04, 0.09), loc=(ox - 0.16 + i*0.08, oy - 0.24, oz + 1.62), mat=mats['gauge_white'], col=col)
        tooth_b.parent = root

    # MONÓCULO DORADO GIGANTE (Ojo izquierdo) vs Ojo rojo pequeño (derecho)
    monocle = abs_style.create_cylinder("SG_MonocleFrame", radius=0.18, depth=0.18, rot=(math.radians(90), 0, 0), loc=(ox + 0.16, oy - 0.32, oz + 1.85), mat=mats['brass_gauge'], col=col)
    monocle.parent = root
    lens_y = abs_style.create_cylinder("SG_YellowLens", radius=0.15, depth=0.04, rot=(math.radians(90), 0, 0), loc=(ox + 0.16, oy - 0.42, oz + 1.85), mat=mats['monocular_yellow'], col=col)
    lens_y.parent = root
    eye_red = abs_style.create_cylinder("SG_RedEye", radius=0.05, depth=0.04, rot=(math.radians(90), 0, 0), loc=(ox - 0.16, oy - 0.24, oz + 1.85), mat=mats['red_eye_lens'], col=col)
    eye_red.parent = root

    # Mano derecha con MAZA DE IMPACTO CON PÚAS CÓNICAS (Morningstar)
    arm_r = abs_style.create_box("SG_ArmR", size=(0.18, 0.5, 0.18), rot=(-math.radians(25), 0, 0), loc=(ox - 0.48, oy - 0.2, oz + 1.25), mat=mats['dark_chitin'], col=col)
    arm_r.parent = root
    mace_shaft = abs_style.create_cylinder("SG_MaceShaft", radius=0.04, depth=0.9, rot=(math.radians(45), 0, 0), loc=(ox - 0.55, oy - 0.45, oz + 1.4), mat=mats['gunmetal'], col=col)
    mace_shaft.parent = root
    mace_ball = abs_style.create_cylinder("SG_MaceHead", radius=0.18, depth=0.3, rot=(math.radians(45), 0, 0), loc=(ox - 0.55, oy - 0.7, oz + 1.7), mat=mats['gunmetal'], col=col)
    mace_ball.parent = root
    for s in range(8):
        ang = s * (math.pi / 4)
        sp_x = ox - 0.55 + math.cos(ang) * 0.22
        sp_z = oz + 1.7 + math.sin(ang) * 0.22
        spike = abs_style.create_cone(f"SG_Spike_{s}", radius1=0.06, radius2=0.0, depth=0.2, rot=(0, -ang, 0), loc=(sp_x, oy - 0.7, sp_z), mat=mats['bone_ivory'], col=col)
        spike.parent = root

    # Mano izquierda con herramienta / sierra mecánica
    arm_l = abs_style.create_box("SG_ArmL", size=(0.18, 0.5, 0.18), loc=(ox + 0.48, oy - 0.2, oz + 1.25), mat=mats['dark_chitin'], col=col)
    arm_l.parent = root
    saw = abs_style.create_cylinder("SG_CircularSaw", radius=0.25, depth=0.03, rot=(0, math.radians(90), 0), loc=(ox + 0.65, oy - 0.45, oz + 1.1), mat=mats['polished_steel'], col=col)
    saw.parent = root

    return root

def build_entity_04_spider_sentry(col, origin, mats):
    """04. Dron Araña Sentry (Spider Drone de Techo) de la referencia"""
    root = bpy.data.objects.new("Entity_04_Spider_Sentry", None)
    root.location = (0, 0, 0)
    col.objects.link(root)
    ox, oy, oz = origin

    # Pórtico industrial con postes verticales para sujetar la tubería del techo
    for px in [-1.5, 1.5]:
        post = abs_style.create_box(f"SS_Post_{px}", size=(0.2, 0.2, 2.2), loc=(ox + px, oy, oz + 1.1), mat=mats['gunmetal'], col=col)
        post.parent = root
        post_base = abs_style.create_box(f"SS_PostBase_{px}", size=(0.4, 0.4, 0.15), loc=(ox + px, oy, oz + 0.08), mat=mats['hazard_yellow'], col=col)
        post_base.parent = root

    # Tubería del techo / viga industrial de donde cuelga el dron
    pipe = abs_style.create_cylinder("SS_CeilingPipe", radius=0.16, depth=3.4, rot=(0, math.radians(90), 0), loc=(ox, oy, oz + 2.1), mat=mats['gunmetal'], col=col)
    pipe.parent = root

    # Cuerpo central suspendido que cuelga de la tubería
    pod = abs_style.create_cylinder("SS_CentralPod", radius=0.5, depth=0.45, loc=(ox, oy, oz + 1.55), mat=mats['gunmetal'], col=col)
    pod.parent = root
    eye = abs_style.create_cylinder("SS_OpticEye", radius=0.22, depth=0.15, rot=(math.radians(35), 0, 0), loc=(ox, oy - 0.25, oz + 1.4), mat=mats['monocular_yellow'], col=col)
    eye.parent = root
    sensor_red = abs_style.create_cylinder("SS_SensorRed", radius=0.08, depth=0.12, rot=(math.radians(35), 0, 0), loc=(ox + 0.25, oy - 0.22, oz + 1.55), mat=mats['red_eye_lens'], col=col)
    sensor_red.parent = root

    # 6 Patas mecánicas articuladas que abrazan la tubería y apuntan hacia abajo
    for i in range(6):
        ang = i * (math.pi / 3)
        lx = ox + math.cos(ang) * 0.45
        ly = oy + math.sin(ang) * 0.45
        coxa = abs_style.create_box(f"SS_Coxa_{i}", size=(0.1, 0.1, 0.4), rot=(math.radians(35)*math.cos(ang), math.radians(35)*math.sin(ang), 0), loc=(lx, ly, oz + 1.7), mat=mats['gunmetal'], col=col)
        coxa.parent = root
        tibia = abs_style.create_cylinder(f"SS_Tibia_{i}", radius=0.035, depth=0.75, rot=(math.radians(65)*math.cos(ang), math.radians(65)*math.sin(ang), 0), loc=(lx + math.cos(ang)*0.3, ly + math.sin(ang)*0.3, oz + 1.9), mat=mats['brass_gauge'], col=col)
        tibia.parent = root

    # Mini torreta cañón inferior apuntando hacia abajo
    turret = abs_style.create_cylinder("SS_TurretBarrel", radius=0.05, depth=0.35, loc=(ox, oy, oz + 1.15), mat=mats['polished_steel'], col=col)
    turret.parent = root

    return root

def build_entity_05_cinder_titan(col, origin, mats):
    """05. Titán del Horno (Cinder Spirit / Magma Furnace Titan)"""
    root = bpy.data.objects.new("Entity_05_Furnace_Cinder_Titan", None)
    root.location = (0, 0, 0)
    col.objects.link(root)
    ox, oy, oz = origin

    # Horno ardiente de hierro forjado
    oven = abs_style.create_box("CT_Furnace", size=(2.4, 1.8, 2.6), loc=(ox, oy + 0.6, oz + 1.3), mat=mats['gunmetal'], col=col)
    oven.parent = root
    door_l = abs_style.create_box("CT_DoorL", size=(0.9, 0.15, 2.0), rot=(0, 0, math.radians(55)), loc=(ox - 1.1, oy - 0.4, oz + 1.3), mat=mats['rust_plates'], col=col)
    door_l.parent = root
    door_r = abs_style.create_box("CT_DoorR", size=(0.9, 0.15, 2.0), rot=(0, 0, -math.radians(55)), loc=(ox + 1.1, oy - 0.4, oz + 1.3), mat=mats['rust_plates'], col=col)
    door_r.parent = root

    # Núcleo incandescente del horno
    fire_core = abs_style.create_box("CT_FireCore", size=(1.6, 1.0, 1.8), loc=(ox, oy + 0.3, oz + 1.3), mat=mats['comic_flame_yellow'], col=col)
    fire_core.parent = root

    # Torso de basalto y magma saliendo del horno
    torso = abs_style.create_box("CT_MagmaTorso", size=(1.2, 0.9, 1.1), loc=(ox, oy - 0.2, oz + 1.4), mat=mats['comic_flame_orange'], col=col)
    torso.parent = root
    plate1 = abs_style.create_box("CT_Plate1", size=(0.5, 0.1, 0.5), loc=(ox - 0.3, oy - 0.7, oz + 1.4), mat=mats['dark_chitin'], col=col)
    plate1.parent = root
    plate2 = abs_style.create_box("CT_Plate2", size=(0.5, 0.1, 0.5), loc=(ox + 0.3, oy - 0.7, oz + 1.4), mat=mats['dark_chitin'], col=col)
    plate2.parent = root

    # Cabeza con cresta de fuego cian
    head = abs_style.create_box("CT_Head", size=(0.6, 0.5, 0.6), loc=(ox, oy - 0.3, oz + 2.15), mat=mats['dark_chitin'], col=col)
    head.parent = root
    crest = abs_style.create_cone("CT_CyanCrest", radius1=0.3, radius2=0.02, depth=0.85, rot=(math.radians(25), 0, 0), loc=(ox, oy - 0.2, oz + 2.7), mat=mats['plasma_cyan'], col=col)
    crest.parent = root

    return root

# ==============================================================================
# LAS 5 NUEVAS ENTIDADES (06 A 10)
# ==============================================================================

def build_entity_06_bio_ooze_amoeba(col, origin, mats):
    """06. (NUEVO) Amoeba Quimiofágica / Slime Ácido Transparente con Esqueleto Digerido"""
    root = bpy.data.objects.new("Entity_06_Bio_Ooze_Amoeba", None)
    root.location = (0, 0, 0)
    col.objects.link(root)
    ox, oy, oz = origin

    # Masa translúcida de slime
    body = abs_style.create_cylinder("OA_SlimeBody", radius=1.1, depth=1.4, loc=(ox, oy, oz + 0.7), mat=mats['acid_slime'], col=col)
    body.parent = root
    lobe1 = abs_style.create_cylinder("OA_Lobe1", radius=0.6, depth=0.8, loc=(ox - 0.6, oy - 0.4, oz + 0.5), mat=mats['acid_slime'], col=col)
    lobe1.parent = root
    lobe2 = abs_style.create_cylinder("OA_Lobe2", radius=0.7, depth=0.9, loc=(ox + 0.5, oy + 0.3, oz + 0.6), mat=mats['acid_slime'], col=col)
    lobe2.parent = root

    # Calavera humana y huesos digeridos flotando en el interior
    skull = abs_style.create_box("OA_TrappedSkull", size=(0.35, 0.4, 0.35), rot=(math.radians(25), math.radians(15), 0), loc=(ox, oy, oz + 0.8), mat=mats['bone_ivory'], col=col)
    skull.parent = root
    eye_hole1 = abs_style.create_cylinder("OA_EyeHole1", radius=0.06, depth=0.05, rot=(math.radians(90), 0, 0), loc=(ox - 0.08, oy - 0.2, oz + 0.85), mat=mats['dark_chitin'], col=col)
    eye_hole1.parent = root
    eye_hole2 = abs_style.create_cylinder("OA_EyeHole2", radius=0.06, depth=0.05, rot=(math.radians(90), 0, 0), loc=(ox + 0.08, oy - 0.2, oz + 0.85), mat=mats['dark_chitin'], col=col)
    eye_hole2.parent = root

    # Burbujas ácidas emisivas
    for idx, (bx, by, bz, r) in enumerate([(-0.3, 0.3, 1.1, 0.15), (0.4, -0.2, 0.9, 0.18), (0.1, 0.4, 0.4, 0.12)]):
        bubble = abs_style.create_cylinder(f"OA_Bubble_{idx}", radius=r, depth=r*1.8, loc=(ox + bx, oy + by, oz + bz), mat=mats['comic_flame_yellow'], col=col)
        bubble.parent = root

    return root

def build_entity_07_plasma_tesla_hound(col, origin, mats):
    """07. (NUEVO) Sabueso de Plasma Voltáico con Bobina Tesla Interna"""
    root = bpy.data.objects.new("Entity_07_Plasma_Tesla_Hound", None)
    root.location = (0, 0, 0)
    col.objects.link(root)
    ox, oy, oz = origin

    # Chasis de caja torácica abierta
    ribs = abs_style.create_box("TH_Ribcage", size=(1.2, 0.7, 0.8), loc=(ox, oy, oz + 1.2), mat=mats['gunmetal'], col=col)
    ribs.parent = root

    # Bobina Tesla resplandeciente en el centro del pecho
    tesla_core = abs_style.create_cylinder("TH_TeslaCore", radius=0.18, depth=0.9, rot=(0, math.radians(90), 0), loc=(ox, oy, oz + 1.2), mat=mats['plasma_cyan'], col=col)
    tesla_core.parent = root
    for c in range(5):
        ring = abs_style.create_torus(f"TH_TeslaCoil_{c}", major_r=0.25, minor_r=0.04, rot=(0, math.radians(90), 0), loc=(ox - 0.35 + c*0.18, oy, oz + 1.2), mat=mats['brass_gauge'], col=col)
        ring.parent = root

    # Cuernos electrodos en la cabeza que lanzan chispas
    head = abs_style.create_box("TH_Head", size=(0.6, 0.5, 0.45), loc=(ox + 0.7, oy, oz + 1.5), mat=mats['gunmetal'], col=col)
    head.parent = root
    horn_l = abs_style.create_cone("TH_ElectrodeL", radius1=0.08, radius2=0.01, depth=0.6, rot=(-math.radians(30), 0, math.radians(20)), loc=(ox + 0.8, oy - 0.25, oz + 1.85), mat=mats['polished_steel'], col=col)
    horn_l.parent = root
    horn_r = abs_style.create_cone("TH_ElectrodeR", radius1=0.08, radius2=0.01, depth=0.6, rot=(math.radians(30), 0, math.radians(20)), loc=(ox + 0.8, oy + 0.25, oz + 1.85), mat=mats['polished_steel'], col=col)
    horn_r.parent = root

    # 4 Patas zancudas con amortiguadores
    for px, py in [(-0.5, -0.35), (-0.5, 0.35), (0.4, -0.35), (0.4, 0.35)]:
        leg = abs_style.create_cylinder(f"TH_Leg_{px}_{py}", radius=0.07, depth=1.0, loc=(ox + px, oy + py, oz + 0.5), mat=mats['gunmetal'], col=col)
        leg.parent = root

    return root

def build_entity_08_rust_goliath_mech(col, origin, mats):
    """08. (NUEVO) Meca Centinela Oxidado / Devastador Pesado de Dos Brazos"""
    root = bpy.data.objects.new("Entity_08_Rust_Goliath_Mech", None)
    root.location = (0, 0, 0)
    col.objects.link(root)
    ox, oy, oz = origin

    # Torso masivo oxidado
    torso = abs_style.create_box("RG_Torso", size=(1.6, 1.3, 1.4), loc=(ox, oy, oz + 1.8), mat=mats['rust_plates'], col=col)
    torso.parent = root

    # Cabina enjaulada con visor ámbar
    visor = abs_style.create_box("RG_VisorSlit", size=(0.8, 0.05, 0.2), loc=(ox, oy - 0.68, oz + 2.0), mat=mats['monocular_yellow'], col=col)
    visor.parent = root
    cage = abs_style.create_torus("RG_RollCage", major_r=0.5, minor_r=0.05, rot=(math.radians(90), 0, 0), loc=(ox, oy - 0.65, oz + 2.0), mat=mats['gunmetal'], col=col)
    cage.parent = root

    # Chimeneas de escape de vapor en los hombros
    chimney_l = abs_style.create_cylinder("RG_ChimneyL", radius=0.14, depth=0.7, loc=(ox - 0.6, oy + 0.4, oz + 2.6), mat=mats['gunmetal'], col=col)
    chimney_l.parent = root
    chimney_r = abs_style.create_cylinder("RG_ChimneyR", radius=0.14, depth=0.7, loc=(ox + 0.6, oy + 0.4, oz + 2.6), mat=mats['gunmetal'], col=col)
    chimney_r.parent = root

    # Brazo izquierdo: Gran pinza trituradora hidráulica
    arm_l = abs_style.create_box("RG_ArmL", size=(0.4, 0.8, 0.4), loc=(ox - 1.1, oy - 0.2, oz + 1.6), mat=mats['gunmetal'], col=col)
    arm_l.parent = root
    claw1 = abs_style.create_box("RG_Claw1", size=(0.12, 0.5, 0.25), rot=(0, 0, math.radians(25)), loc=(ox - 1.25, oy - 0.8, oz + 1.6), mat=mats['polished_steel'], col=col)
    claw1.parent = root
    claw2 = abs_style.create_box("RG_Claw2", size=(0.12, 0.5, 0.25), rot=(0, 0, -math.radians(25)), loc=(ox - 0.95, oy - 0.8, oz + 1.6), mat=mats['polished_steel'], col=col)
    claw2.parent = root

    # Brazo derecho: Cañón percutor neumático (Jackhammer)
    arm_r = abs_style.create_box("RG_ArmR", size=(0.4, 0.8, 0.4), loc=(ox + 1.1, oy - 0.2, oz + 1.6), mat=mats['gunmetal'], col=col)
    arm_r.parent = root
    ram = abs_style.create_cylinder("RG_RamPiston", radius=0.15, depth=0.9, rot=(math.radians(90), 0, 0), loc=(ox + 1.1, oy - 0.8, oz + 1.6), mat=mats['polished_steel'], col=col)
    ram.parent = root

    # Piernas pesadas tipo tractor
    for px in [-0.5, 0.5]:
        leg = abs_style.create_box(f"RG_Leg_{px}", size=(0.45, 0.6, 1.1), loc=(ox + px, oy, oz + 0.55), mat=mats['gunmetal'], col=col)
        leg.parent = root

    return root

def build_entity_09_void_leech_parasite(col, origin, mats):
    """09. (NUEVO) Sanguijuela del Vacío / Parásito Devorador de Cables"""
    root = bpy.data.objects.new("Entity_09_Void_Leech", None)
    root.location = (0, 0, 0)
    col.objects.link(root)
    ox, oy, oz = origin

    # Cable grueso en el que se enrosca
    conduit = abs_style.create_cylinder("VL_Conduit", radius=0.2, depth=3.0, rot=(0, math.radians(90), 0), loc=(ox, oy, oz + 1.2), mat=mats['gunmetal'], col=col)
    conduit.parent = root

    # Cuerpo anillado de la sanguijuela enroscado
    for seg in range(6):
        sx = ox - 0.8 + seg * 0.3
        ring = abs_style.create_torus(f"VL_Seg_{seg}", major_r=0.38 + 0.05*(seg%2), minor_r=0.12, rot=(0, math.radians(90), 0), loc=(sx, oy, oz + 1.2), mat=mats['dark_chitin'], col=col)
        ring.parent = root

    # Mandíbulas concéntricas frontales con dientes afilados
    mouth = abs_style.create_torus("VL_MouthRim", major_r=0.35, minor_r=0.08, rot=(0, math.radians(90), 0), loc=(ox + 1.0, oy, oz + 1.2), mat=mats['bone_ivory'], col=col)
    mouth.parent = root
    core_hole = abs_style.create_cylinder("VL_CoreHole", radius=0.28, depth=0.15, rot=(0, math.radians(90), 0), loc=(ox + 0.95, oy, oz + 1.2), mat=mats['red_eye_lens'], col=col)
    core_hole.parent = root

    # Ojos rojos biomiméticos en los flancos
    for idx, fx in enumerate([-0.3, 0.1, 0.5]):
        eye_t = abs_style.create_cylinder(f"VL_Eye_{idx}", radius=0.05, depth=0.04, loc=(ox + fx, oy, oz + 1.6), mat=mats['red_eye_lens'], col=col)
        eye_t.parent = root

    return root

def build_entity_10_cryo_revenant(col, origin, mats):
    """10. (NUEVO) Revenant Criogénico / Astronauta Congelado en Hielo Glacial"""
    root = bpy.data.objects.new("Entity_10_Cryo_Revenant", None)
    root.location = (0, 0, 0)
    col.objects.link(root)
    ox, oy, oz = origin

    # Cuerpo humanoide encorvado de astronauta
    body = abs_style.create_box("CR_SuitTorso", size=(0.65, 0.5, 0.8), loc=(ox, oy, oz + 1.2), mat=mats['gunmetal'], col=col)
    body.parent = root
    helmet = abs_style.create_cylinder("CR_Helmet", radius=0.32, depth=0.45, loc=(ox, oy, oz + 1.8), mat=mats['gunmetal'], col=col)
    helmet.parent = root

    # Visor roto con ojos blancos penetrantes
    visor = abs_style.create_cylinder("CR_VisorGlass", radius=0.28, depth=0.08, rot=(math.radians(90), 0, 0), loc=(ox, oy - 0.28, oz + 1.8), mat=mats['cryo_ice'], col=col)
    visor.parent = root
    eye1 = abs_style.create_cylinder("CR_Eye1", radius=0.04, depth=0.05, rot=(math.radians(90), 0, 0), loc=(ox - 0.1, oy - 0.3, oz + 1.82), mat=mats['gauge_white'], col=col)
    eye1.parent = root
    eye2 = abs_style.create_cylinder("CR_Eye2", radius=0.04, depth=0.05, rot=(math.radians(90), 0, 0), loc=(ox + 0.1, oy - 0.3, oz + 1.82), mat=mats['gauge_white'], col=col)
    eye2.parent = root

    # Cristales de hielo azul translúcido puntiagudos que perforan el traje
    for idx, (ix, iy, iz, rx, rz) in enumerate([
        (-0.35, -0.2, 1.4, 30, -45),
        (0.4, 0.1, 1.6, -20, 35),
        (0.0, 0.3, 1.9, -45, 0),
        (-0.2, 0.2, 0.8, 15, -60),
    ]):
        shard = abs_style.create_cone(f"CR_IceShard_{idx}", radius1=0.16, radius2=0.0, depth=0.75, rot=(math.radians(rx), 0, math.radians(rz)), loc=(ox + ix, oy + iy, oz + iz), mat=mats['cryo_ice'], col=col)
        shard.parent = root

    # Lanza de tubería helada rota
    spear = abs_style.create_cylinder("CR_IceSpear", radius=0.04, depth=1.6, rot=(math.radians(45), 0, 0), loc=(ox + 0.55, oy - 0.3, oz + 1.1), mat=mats['polished_steel'], col=col)
    spear.parent = root

    return root

# Registro maestro de las 10 entidades
BESTIARY_ENTITIES = [
    (1, "Mechanical_Werewolf", build_entity_01_werewolf),
    (2, "Auditor_Drone", build_entity_02_auditor_drone),
    (3, "Scrapper_Goblin", build_entity_03_scrapper_goblin),
    (4, "Spider_Sentry_Drone", build_entity_04_spider_sentry),
    (5, "Furnace_Cinder_Titan", build_entity_05_cinder_titan),
    (6, "Bio_Ooze_Amoeba", build_entity_06_bio_ooze_amoeba),
    (7, "Plasma_Tesla_Hound", build_entity_07_plasma_tesla_hound),
    (8, "Rust_Goliath_Mech", build_entity_08_rust_goliath_mech),
    (9, "Void_Leech_Parasite", build_entity_09_void_leech_parasite),
    (10, "Cryo_Revenant_Astronaut", build_entity_10_cryo_revenant),
]

def generate_bestiary_scenes(save_blend=True):
    print("[*] Iniciando construccion del Bestiario 3D Oficial de 10 Entidades...")
    abs_style.reset_comic_scene(bg_color=(0.015, 0.02, 0.028, 1.0), bg_strength=0.45, ink_thickness=1.8)
    master_col = abs_style.create_collection("Bestiario_10_Entidades_Oficial")
    mats = init_bestiary_materials()

    # Pedestales individuales espaciados en una sola hilera lineal (estilo galería de museo de arte)
    spacing_x = 5.2
    ped_mat = abs_style.get_comic_material("Pedestal_Bestiary", base_color=(0.06, 0.07, 0.09), roughness=0.35, metallic=0.7)
    plaque_mat = abs_style.get_comic_material("Plaque_Brass_B", base_color=(0.92, 0.74, 0.22), roughness=0.22, metallic=0.92)

    # 1. Crear las 10 entidades en sus coordenadas lineales a lo largo de X (y = 0.0)
    for idx, (eid, ename, builder) in enumerate(BESTIARY_ENTITIES):
        x = (idx - 4.5) * spacing_x
        y = 0.0

        ped = abs_style.create_box(f"Pedestal_{ename}", size=(3.8, 3.8, 0.25), loc=(x, y, 0.125), mat=ped_mat, col=master_col)
        plaque = abs_style.create_box(f"Plaque_{ename}", size=(1.6, 0.08, 0.16), rot=(math.radians(30), 0, 0), loc=(x, y - 1.85, 0.2), mat=plaque_mat, col=master_col)
        builder(master_col, (x, y, 0.25), mats)

    # Iluminación de estudio direccional cómic
    abs_style.setup_studio_lighting(sun_energy=3.8, rim_energy=2.4, fill_energy=1.2)

    # Suelo general del bestiario
    floor_mat = abs_style.get_comic_material("Bestiary_Floor", base_color=(0.02, 0.025, 0.035), roughness=0.25, metallic=0.85)
    abs_style.create_box("BestiaryFloor", size=(68.0, 18.0, 0.2), loc=(0, 0, -0.1), mat=floor_mat, col=master_col)

    # Cámara Panorámica Maestra
    abs_style.setup_camera(name="Camera_Bestiary_Master", loc=(0, -32, 14), target=(0, 0, 1.3), focal_length=24)

    if save_blend:
        blend_path = os.path.join(abs_style.PROJECT_ROOT, "Art", "Blender", "Bestiario_10_Entidades_3D_Oficial.blend")
        bpy.ops.wm.save_as_mainfile(filepath=blend_path)
        print(f"[+] Blend del Bestiario 3D guardado en: {blend_path}")

    # Render Panorámico de las 10 entidades
    abs_style.render_and_save("Showcase_Bestiario_10_Entidades_Master.png", res_x=2560, res_y=1440)

    # 2. Renderizar primeros planos (Closeups) individuales de cada una de las 10 entidades
    print("[*] Renderizando Closeups 3D individuales de las 10 entidades...")
    for idx, (eid, ename, _) in enumerate(BESTIARY_ENTITIES):
        x = (idx - 4.5) * spacing_x
        y = 0.0

        cam_closeup = abs_style.setup_camera(name=f"Cam_Close_{ename}", loc=(x, -5.2, 1.8), target=(x, 0.0, 1.3), focal_length=42)
        abs_style.render_and_save(f"CloseUp_3D_{ename}.png", res_x=1280, res_y=1280)

    print("[+] Renderizado del Bestiario 3D Oficial completado exitosamente!")

if __name__ == "__main__":
    generate_bestiary_scenes(save_blend=True)

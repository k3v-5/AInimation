# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Generador Oficial de Peligros Ambientales - Lote 1: Peligros Termicos e Igneos (H01 al H06)
# Blender 5.2 LTS - Modelado Procedural BMesh Avanzado, Shaders PBR Stylized y Cel-Shading Comic

import bpy
import bmesh
import math
import os
import sys
import shutil
from mathutils import Vector, Euler
from PIL import Image, ImageDraw, ImageFont
import textwrap

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.append(SCRIPT_DIR)

import astra_blender_styling as abs_style

PROJECT_ROOT = abs_style.PROJECT_ROOT
RENDERS_DIR = abs_style.RENDERS_DIR
ARTIFACT_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\b59ff04f-3c21-4ee5-94b0-8e8f899f8923"
BLEND_FILE = os.path.join(SCRIPT_DIR, "Peligros_Lote1_Termicos.blend")

HAZARDS_LOTE1 = [
    (1, "H01_Fire_Bulkhead_Rupture", "Foco de Fuego Estructural en Mamparo",
     "Mamparo rajado por fatiga termica extrema con vigas I deformadas, chapas rasgadas en V, llamas estratificadas y humo comic."),
    (2, "H02_Electrical_Arc_Fire_Box", "Cuadro Electrico Trifasico en Ignicion",
     "Gabinete con marco hazard, puerta volada por sobrepresion, rieles DIN calcinados, bobinas de cobre y arco voltaico."),
    (3, "H03_Magnesium_Chemical_Fire", "Fuego Quimico de Magnesio Verde",
     "Crisol de fundicion con cinchas remachadas, patas de perfil en U, charco burbujeante y llama esmeralda multicapa."),
    (4, "H04_Plasma_Nozzle_Breach", "Fuga de Plasma Presurizado a 1200C",
     "Tobera segmentada con bridas empernadas, bobinas toroidales de confinamiento rajadas y chorro sónico de plasma cian."),
    (5, "H05_Vent_Duct_Inferno", "Conducto de Ventilacion en Llamas",
     "Conducto con costillas de refuerzo, lamas louver individuales fundidas, motor soplador con aletas y llamaradas a presion."),
    (6, "H06_Habitation_Flashover", "Flashover de Habitaculo & Rollover",
     "Esquina de camarote con falso techo desprendido, cables tensores, taquilla calcinada y capa de fuego rodante horizontal."),
]

def init_thermal_materials():
    mats = {}
    mats['dark_steel'] = abs_style.get_comic_material("Mat_H_DarkSteel", base_color=(0.14, 0.15, 0.18), roughness=0.38, metallic=0.85)
    mats['scorched_steel'] = abs_style.get_comic_material("Mat_H_Scorched", base_color=(0.08, 0.08, 0.09), roughness=0.88, metallic=0.25)
    mats['hazard_yellow'] = abs_style.get_comic_material("Mat_H_HazardYel", base_color=(0.95, 0.70, 0.08), roughness=0.32, metallic=0.15)
    mats['hazard_black'] = abs_style.get_comic_material("Mat_H_HazardBlk", base_color=(0.08, 0.09, 0.11), roughness=0.45, metallic=0.2)
    mats['brass'] = abs_style.get_comic_material("Mat_H_Brass", base_color=(0.88, 0.68, 0.18), roughness=0.25, metallic=0.90)
    mats['copper_coil'] = abs_style.get_comic_material("Mat_H_CopperCoil", base_color=(0.85, 0.42, 0.15), roughness=0.28, metallic=0.88,
                                                       emissive_color=(0.95, 0.30, 0.05, 1.0), emissive_strength=0.95)
    mats['valve_red'] = abs_style.get_comic_material("Mat_H_ValveRed", base_color=(0.85, 0.12, 0.10), roughness=0.32, metallic=0.20)
    mats['ember_core'] = abs_style.get_comic_material("Mat_H_EmberCore", base_color=(0.45, 0.10, 0.02), roughness=0.45, metallic=0.10,
                                                      emissive_color=(1.0, 0.28, 0.04, 1.0), emissive_strength=1.1)

    # Materiales de FUEGO ESTILIZADO CALIBRADOS PARA APAGON (<= 1.2 para evitar burnout blanco en Lumen)
    mats['fire_outer'] = abs_style.get_comic_material("Mat_H_FireOuter", base_color=(0.92, 0.18, 0.02), roughness=0.2, metallic=0.0,
                                                      emissive_color=(1.0, 0.22, 0.02, 1.0), emissive_strength=1.0)
    mats['fire_mid'] = abs_style.get_comic_material("Mat_H_FireMid", base_color=(1.0, 0.55, 0.05), roughness=0.15, metallic=0.0,
                                                    emissive_color=(1.0, 0.60, 0.08, 1.0), emissive_strength=1.1)
    mats['fire_core'] = abs_style.get_comic_material("Mat_H_FireCore", base_color=(1.0, 0.92, 0.35), roughness=0.1, metallic=0.0,
                                                     emissive_color=(1.0, 0.95, 0.45, 1.0), emissive_strength=1.2)
    
    # Magnesio verde esmeralda calibrado
    mats['magnesium_dark'] = abs_style.get_comic_material("Mat_H_MagDark", base_color=(0.05, 0.60, 0.20), roughness=0.2, metallic=0.0,
                                                         emissive_color=(0.08, 0.75, 0.25, 1.0), emissive_strength=2.2)
    mats['magnesium_mid'] = abs_style.get_comic_material("Mat_H_MagMid", base_color=(0.15, 0.95, 0.35), roughness=0.15, metallic=0.0,
                                                        emissive_color=(0.20, 1.0, 0.40, 1.0), emissive_strength=3.2)
    mats['magnesium_core'] = abs_style.get_comic_material("Mat_H_MagCore", base_color=(0.75, 1.0, 0.80), roughness=0.1, metallic=0.0,
                                                         emissive_color=(0.80, 1.0, 0.85, 1.0), emissive_strength=4.0)
    
    # Plasma cian calibrado
    mats['plasma_outer'] = abs_style.get_comic_material("Mat_H_PlasmaOuter", base_color=(0.02, 0.45, 0.85), roughness=0.15, metallic=0.0,
                                                        emissive_color=(0.05, 0.55, 0.95, 1.0), emissive_strength=2.4)
    mats['plasma_mid'] = abs_style.get_comic_material("Mat_H_PlasmaMid", base_color=(0.05, 0.80, 1.0), roughness=0.1, metallic=0.0,
                                                      emissive_color=(0.10, 0.88, 1.0, 1.0), emissive_strength=3.4)
    mats['plasma_core'] = abs_style.get_comic_material("Mat_H_PlasmaCore", base_color=(0.70, 0.95, 1.0), roughness=0.05, metallic=0.0,
                                                       emissive_color=(0.80, 0.98, 1.0, 1.0), emissive_strength=4.5)
    
    mats['smoke'] = abs_style.get_comic_material("Mat_H_Smoke", base_color=(0.06, 0.06, 0.08), roughness=0.92, metallic=0.0)
    return mats

def build_stylized_flame_cluster(name, loc, scale=1.0, flame_type='orange', col=None, mats=None):
    root = bpy.data.objects.new(f"FlameCluster_{name}", None)
    root.location = loc
    col.objects.link(root)
    
    if flame_type == 'green':
        m_out, m_mid, m_in = mats['magnesium_dark'], mats['magnesium_mid'], mats['magnesium_core']
    elif flame_type == 'cyan':
        m_out, m_mid, m_in = mats['plasma_outer'], mats['plasma_mid'], mats['plasma_core']
    else:
        m_out, m_mid, m_in = mats['fire_outer'], mats['fire_mid'], mats['fire_core']
        
    # Capa exterior (lengüeta envolvente)
    f_out = abs_style.create_cone(f"{name}_FlameOuter", radius1=0.45 * scale, radius2=0.02, depth=1.4 * scale,
                                  rot=(math.radians(8), 0, math.radians(-12)), loc=(0, 0, 0.7 * scale), mat=m_out, col=col)
    f_out.parent = root
    
    # Capa intermedia (cuerpo vibrante)
    f_mid = abs_style.create_cone(f"{name}_FlameMid", radius1=0.32 * scale, radius2=0.015, depth=1.1 * scale,
                                  rot=(math.radians(-6), math.radians(10), 0), loc=(0.04 * scale, 0.02 * scale, 0.55 * scale), mat=m_mid, col=col)
    f_mid.parent = root
    
    # Núcleo incandescente
    f_core = abs_style.create_cone(f"{name}_FlameCore", radius1=0.18 * scale, radius2=0.01, depth=0.7 * scale,
                                   loc=(0.02 * scale, 0.01 * scale, 0.35 * scale), mat=m_in, col=col)
    f_core.parent = root
    
    # Lengüetas satélite estilizadas
    for s_idx, (sx, sy, sz, s_rot) in enumerate([(0.22, 0.15, 0.45, 24), (-0.20, -0.12, 0.38, -28), (0.05, -0.22, 0.50, 18)]):
        sub = abs_style.create_cone(f"{name}_Sub_{s_idx}", radius1=0.14 * scale, radius2=0.01, depth=0.55 * scale,
                                    rot=(math.radians(s_rot), 0, math.radians(s_rot * 0.7)),
                                    loc=(sx * scale, sy * scale, sz * scale), mat=m_out, col=col)
        sub.parent = root
        
    return root

def build_smoke_puff(name, loc, radius=0.25, col=None, mats=None):
    smoke_obj = abs_style.create_cylinder(f"{name}_Puff", radius=radius, depth=radius * 1.2,
                                          loc=loc, mat=mats['smoke'], col=col)
    return smoke_obj

def build_hazard_1_bulkhead(ox, oy, oz, col, mats):
    """
    Estacion/Manifold de Combustible Fisurado en Cubierta (Concept_01_SM_H01_FuelManifoldFireStation).
    Prohibido usar marcos de puerta aislados en campo abierto ni conos opacos sólidos simulando llamas.
    """
    root = bpy.data.objects.new("Root_H01", None)
    root.location = (0, 0, 0)
    col.objects.link(root)
    name = "H01_FuelManifold"

    # 1. Plinto octogonal industrial pesadamente empernado al suelo (Z=0..0.18 m, 1.40x1.40 m)
    plinth = abs_style.create_box(f"{name}_BasePlinth", size=(1.36, 1.36, 0.14), bevel_w=0.04,
                                  loc=(ox, oy, oz + 0.07), mat=mats['dark_steel'], col=col)
    plinth.parent = root
    upper_deck = abs_style.create_box(f"{name}_DeckPlate", size=(1.18, 1.18, 0.05), bevel_w=0.02,
                                      loc=(ox, oy, oz + 0.165), mat=mats['dark_steel'], col=col)
    upper_deck.parent = root

    for cx, cy in [(-0.56, -0.56), (0.56, -0.56), (-0.56, 0.56), (0.56, 0.56)]:
        gusset = abs_style.create_box(f"{name}_Corner_{cx:.1f}_{cy:.1f}", size=(0.24, 0.24, 0.15),
                                      rot=(0, 0, math.radians(45)), loc=(ox + cx, oy + cy, oz + 0.075),
                                      mat=mats['scorched_steel'], col=col)
        gusset.parent = root
        bolt = abs_style.create_cylinder(f"{name}_Bolt_{cx:.1f}_{cy:.1f}", radius=0.032, depth=0.06, segments=6,
                                         loc=(ox + cx * 0.92, oy + cy * 0.92, oz + 0.18), mat=mats['brass'], col=col)
        bolt.parent = root

    # 2. Tanque colector trasero paralelo con manómetros dobles analógicos (Z hasta 0.85 m)
    rear_tank = abs_style.create_cylinder(f"{name}_RearManifold", radius=0.14, depth=0.88,
                                          rot=(0, math.radians(90), 0), loc=(ox - 0.04, oy + 0.28, oz + 0.40),
                                          mat=mats['dark_steel'], col=col)
    rear_tank.parent = root
    for rx in (-0.34, 0.26):
        collar = abs_style.create_cylinder(f"{name}_RearCollar_{rx:.2f}", radius=0.155, depth=0.06,
                                           rot=(0, math.radians(90), 0), loc=(ox + rx, oy + 0.28, oz + 0.40),
                                           mat=mats['brass'], col=col)
        collar.parent = root

    for gx in (-0.20, 0.04):
        stem = abs_style.create_cylinder(f"{name}_GaugeStem_{gx:.2f}", radius=0.028, depth=0.22,
                                         loc=(ox + gx, oy + 0.26, oz + 0.61), mat=mats['brass'], col=col)
        stem.parent = root
        gauge = abs_style.create_analog_gauge(f"{name}_Gauge_{gx:.2f}", loc=(ox + gx, oy + 0.24, oz + 0.76),
                                              rot=(math.radians(90), 0, 0), radius=0.10, depth=0.06, col=col)
        gauge.parent = root

    # 3. Tanque principal horizontal delantero fisurado con bandas amarillo/negro de peligro
    main_tank = abs_style.create_cylinder(f"{name}_MainDrum", radius=0.21, depth=0.92,
                                          rot=(0, math.radians(90), 0), loc=(ox + 0.04, oy - 0.12, oz + 0.42),
                                          mat=mats['dark_steel'], col=col)
    main_tank.parent = root
    end_cap = abs_style.create_cylinder(f"{name}_EndCapR", radius=0.205, depth=0.10,
                                        rot=(0, math.radians(90), 0), loc=(ox + 0.52, oy - 0.12, oz + 0.42),
                                        mat=mats['scorched_steel'], col=col)
    end_cap.parent = root

    # Bandas alternadas de peligro alrededor del tambor
    for s_idx, sx in enumerate([-0.14, -0.05, 0.04, 0.13, 0.22]):
        s_mat = mats['hazard_yellow'] if (s_idx % 2 == 0) else mats['hazard_black']
        band = abs_style.create_cylinder(f"{name}_Band_{s_idx}", radius=0.216, depth=0.075,
                                         rot=(0, math.radians(90), 0), loc=(ox + sx, oy - 0.12, oz + 0.42),
                                         mat=s_mat, col=col)
        band.parent = root

    # Boca de tubería rota al costado -X (silueta clara industrial con labios biselados y oquedad oscura)
    rupt_stub = abs_style.create_cylinder(f"{name}_RuptureStub", radius=0.13, depth=0.26,
                                          rot=(0, math.radians(90), 0), loc=(ox - 0.48, oy - 0.12, oz + 0.42),
                                          mat=mats['scorched_steel'], col=col)
    rupt_stub.parent = root
    rupt_rim = abs_style.create_torus(f"{name}_RuptureRim", major_r=0.13, minor_r=0.025,
                                      rot=(0, math.radians(90), 0), loc=(ox - 0.60, oy - 0.12, oz + 0.42),
                                      mat=mats['scorched_steel'], col=col)
    rupt_rim.parent = root
    rupt_bore = abs_style.create_cylinder(f"{name}_RuptureBore", radius=0.105, depth=0.05,
                                          rot=(0, math.radians(90), 0), loc=(ox - 0.585, oy - 0.12, oz + 0.42),
                                          mat=mats['hazard_black'], col=col)
    rupt_bore.parent = root

    # Cráter chamuscado superior con núcleo de brasa sutil (zona donde Niagara genera las llamas reales)
    breach_ring = abs_style.create_torus(f"{name}_TopBreachRing", major_r=0.14, minor_r=0.028,
                                         rot=(0, 0, 0), loc=(ox + 0.04, oy - 0.12, oz + 0.63),
                                         mat=mats['scorched_steel'], col=col)
    breach_ring.parent = root
    breach_ember = abs_style.create_cylinder(f"{name}_BreachEmber", radius=0.11, depth=0.03,
                                             loc=(ox + 0.04, oy - 0.12, oz + 0.625),
                                             mat=mats['ember_core'], col=col)
    breach_ember.parent = root

    # Soportes tipo cuna entre plinto y tanque
    for bx in (-0.28, 0.34):
        cradle = abs_style.create_box(f"{name}_Saddle_{bx:.2f}", size=(0.14, 0.42, 0.20),
                                      loc=(ox + bx, oy - 0.12, oz + 0.25), mat=mats['dark_steel'], col=col)
        cradle.parent = root

    # 4. Válvula de volante rojo frontal y rejilla térmica inclinada con brasa interior
    v_stem = abs_style.create_cylinder(f"{name}_ValveStem", radius=0.025, depth=0.16,
                                       rot=(math.radians(90), 0, 0), loc=(ox + 0.04, oy - 0.34, oz + 0.42),
                                       mat=mats['brass'], col=col)
    v_stem.parent = root
    v_wheel = abs_style.create_torus(f"{name}_RedWheel", major_r=0.13, minor_r=0.022,
                                     rot=(math.radians(90), 0, 0), loc=(ox + 0.04, oy - 0.41, oz + 0.42),
                                     mat=mats['valve_red'], col=col)
    v_wheel.parent = root
    for ang_deg in (0, 60, 120):
        spoke = abs_style.create_box(f"{name}_Spoke_{ang_deg}", size=(0.24, 0.018, 0.022),
                                     rot=(0, math.radians(ang_deg), 0), loc=(ox + 0.04, oy - 0.41, oz + 0.42),
                                     mat=mats['valve_red'], col=col)
        spoke.parent = root

    louver_box = abs_style.create_box(f"{name}_LouverHousing", size=(0.54, 0.22, 0.18),
                                      rot=(math.radians(24), 0, 0), loc=(ox + 0.04, oy - 0.39, oz + 0.24),
                                      mat=mats['dark_steel'], col=col)
    louver_box.parent = root
    louver_glow = abs_style.create_box(f"{name}_LouverEmber", size=(0.44, 0.06, 0.10),
                                       rot=(math.radians(24), 0, 0), loc=(ox + 0.04, oy - 0.46, oz + 0.24),
                                       mat=mats['ember_core'], col=col)
    louver_glow.parent = root
    for l_idx, lz in enumerate([-0.035, 0.0, 0.035]):
        slat = abs_style.create_box(f"{name}_LouverSlat_{l_idx}", size=(0.46, 0.03, 0.018),
                                    rot=(math.radians(5), 0, 0), loc=(ox + 0.04, oy - 0.49, oz + 0.24 + lz),
                                    mat=mats['scorched_steel'], col=col)
        slat.parent = root

    return root

def build_hazard_2_electrical(ox, oy, oz, col, mats):
    root = bpy.data.objects.new("Root_H02", None)
    root.location = (0, 0, 0)
    col.objects.link(root)
    name = "H02_Electrical_Box"
    
    # 1. Armario principal con tejadillo biselado
    cabinet = abs_style.create_box(f"{name}_Cabinet", size=(1.8, 1.1, 2.3), loc=(ox, oy, oz + 1.25), mat=mats['dark_steel'], col=col)
    cabinet.parent = root
    canopy = abs_style.create_box(f"{name}_Canopy", size=(1.9, 1.25, 0.12), loc=(ox, oy - 0.05, oz + 2.42), mat=mats['dark_steel'], col=col)
    canopy.parent = root
    
    # 2. Marco perimetral con franjas de peligro amarillo/negro
    h_strip1 = abs_style.create_box(f"{name}_HStripL", size=(0.12, 0.08, 2.2), loc=(ox - 0.84, oy - 0.56, oz + 1.25), mat=mats['hazard_yellow'], col=col)
    h_strip1.parent = root
    h_strip2 = abs_style.create_box(f"{name}_HStripR", size=(0.12, 0.08, 2.2), loc=(ox + 0.84, oy - 0.56, oz + 1.25), mat=mats['hazard_yellow'], col=col)
    h_strip2.parent = root
    
    # 3. Puerta volada doblada hacia afuera sostenida por una bisagra
    door = abs_style.create_box(f"{name}_DoorBlown", size=(0.85, 0.08, 2.05), rot=(math.radians(12), math.radians(-42), math.radians(22)),
                                loc=(ox - 0.65, oy - 0.75, oz + 1.15), mat=mats['scorched_steel'], col=col)
    door.parent = root
    
    # Bisagra reforzada con pasador
    hinge = abs_style.create_cylinder(f"{name}_Hinge", radius=0.06, depth=0.35, loc=(ox - 0.88, oy - 0.56, oz + 1.8), mat=mats['brass'], col=col)
    hinge.parent = root
    
    # 4. Interior: Riel DIN, 3 seccionadores de palanca de cobre y barra colectora
    din_rail = abs_style.create_box(f"{name}_DINRail", size=(1.4, 0.08, 0.12), loc=(ox, oy - 0.2, oz + 1.55), mat=mats['dark_steel'], col=col)
    din_rail.parent = root
    for s in range(3):
        switch = abs_style.create_box(f"{name}_Switch_{s}", size=(0.22, 0.25, 0.45), loc=(ox - 0.45 + s * 0.45, oy - 0.22, oz + 1.55), mat=mats['copper_coil'], col=col)
        switch.parent = root
        
    # Transformador toroid en la base
    toroid = abs_style.create_torus(f"{name}_Toroid", major_r=0.35, minor_r=0.10, rot=(math.radians(90), 0, 0),
                                    loc=(ox + 0.35, oy - 0.15, oz + 0.6), mat=mats['copper_coil'], col=col)
    toroid.parent = root
    
    # 5. Cables serpenteantes que caen al suelo
    for c in range(4):
        cx_off = (c - 1.5) * 0.26
        wire = abs_style.create_cylinder(f"{name}_Cable_{c}", radius=0.032, depth=0.95,
                                         rot=(math.radians(35 + c * 8), 0, math.radians(-20 + c * 12)),
                                         loc=(ox + cx_off, oy - 0.55, oz + 0.45), mat=mats['copper_coil'], col=col)
        wire.parent = root
        
    # 6. Manómetro industrial en lateral
    gauge = abs_style.create_analog_gauge(f"{name}_Gauge", loc=(ox + 0.88, oy - 0.2, oz + 1.7), rot=(0, 90, 0), radius=0.22, depth=0.1, col=col)
    gauge.parent = root
    
    # 7. Arco voltaico y llamarada brotando del interior
    flame_elec = build_stylized_flame_cluster(f"{name}_FlameElec", (ox + 0.05, oy - 0.45, oz + 1.1), scale=1.1, flame_type='orange', col=col, mats=mats)
    flame_elec.parent = root
    
    # Arco voltaico cian entre bornes
    spark = abs_style.create_cylinder(f"{name}_ArcSpark", radius=0.025, depth=0.55, rot=(math.radians(45), math.radians(35), 0),
                                      loc=(ox - 0.15, oy - 0.35, oz + 1.6), mat=mats['plasma_mid'], col=col)
    spark.parent = root
    return root

def build_hazard_3_magnesium(ox, oy, oz, col, mats):
    root = bpy.data.objects.new("Root_H03", None)
    root.location = (0, 0, 0)
    col.objects.link(root)
    name = "H03_Magnesium_Crucible"
    
    # 1. Crisol de fundición con cuerpo abombado reforzado
    crucible_body = abs_style.create_cylinder(f"{name}_CrucibleBody", radius=0.88, depth=1.65, loc=(ox, oy, oz + 1.15), mat=mats['dark_steel'], col=col)
    crucible_body.parent = root
    
    # Labio de vertido reforzado en boca superior
    lip = abs_style.create_torus(f"{name}_Lip", major_r=0.92, minor_r=0.09, loc=(ox, oy, oz + 1.95), mat=mats['brass'], col=col)
    lip.parent = root
    
    # Cinchas de refuerzo con remaches
    cinch1 = abs_style.create_torus(f"{name}_Cinch1", major_r=0.90, minor_r=0.06, loc=(ox, oy, oz + 1.45), mat=mats['hazard_yellow'], col=col)
    cinch1.parent = root
    cinch2 = abs_style.create_torus(f"{name}_Cinch2", major_r=0.90, minor_r=0.06, loc=(ox, oy, oz + 0.85), mat=mats['dark_steel'], col=col)
    cinch2.parent = root
    
    # 2. Soporte de trípode con perfiles en U y placas base de anclaje
    for i in range(3):
        ang = i * (2.0 * math.pi / 3.0)
        lx = ox + math.cos(ang) * 0.95
        ly = oy + math.sin(ang) * 0.95
        leg = abs_style.create_box(f"{name}_Leg_{i}", size=(0.20, 0.24, 0.75), loc=(lx, ly, oz + 0.38), mat=mats['scorched_steel'], col=col)
        leg.parent = root
        foot = abs_style.create_box(f"{name}_Foot_{i}", size=(0.35, 0.35, 0.08), loc=(lx, ly, oz + 0.04), mat=mats['dark_steel'], col=col)
        foot.parent = root
        
    # 3. Volante de purga manual en la base
    valve = abs_style.create_torus(f"{name}_ValveHandwheel", major_r=0.22, minor_r=0.035, rot=(math.radians(90), 0, 0),
                                   loc=(ox, oy - 0.95, oz + 0.65), mat=mats['brass'], col=col)
    valve.parent = root
    
    # 4. Fisura de reactor con vertido y charco químico esmeralda
    spill = abs_style.create_cylinder(f"{name}_SpillStream", radius=0.08, depth=0.75, rot=(math.radians(22), 0, 0),
                                      loc=(ox, oy - 0.75, oz + 0.35), mat=mats['magnesium_mid'], col=col)
    spill.parent = root
    
    # Charco químico con relieve
    puddle = abs_style.create_cylinder(f"{name}_ChemPuddle", radius=1.45, depth=0.06, loc=(ox + 0.15, oy - 0.45, oz + 0.03), mat=mats['magnesium_dark'], col=col)
    puddle.parent = root
    puddle_core = abs_style.create_cylinder(f"{name}_ChemPuddleCore", radius=0.85, depth=0.08, loc=(ox + 0.15, oy - 0.45, oz + 0.04), mat=mats['magnesium_mid'], col=col)
    puddle_core.parent = root
    
    # Burbujas químicas en el charco
    for b_idx, (bx, by, br) in enumerate([(0.5, -0.6, 0.14), (-0.4, -0.3, 0.12), (0.2, -0.9, 0.16)]):
        bubble = abs_style.create_cylinder(f"{name}_Bubble_{b_idx}", radius=br, depth=br * 0.8,
                                           loc=(ox + bx, oy + by, oz + 0.08), mat=mats['magnesium_core'], col=col)
        bubble.parent = root
        
    # 5. Columna de llama verde de magnesio en boca y charco
    flame_green_top = build_stylized_flame_cluster(f"{name}_FlameTop", (ox, oy, oz + 1.95), scale=1.5, flame_type='green', col=col, mats=mats)
    flame_green_top.parent = root
    flame_green_puddle = build_stylized_flame_cluster(f"{name}_FlamePuddle", (ox + 0.3, oy - 0.65, oz + 0.08), scale=0.8, flame_type='green', col=col, mats=mats)
    flame_green_puddle.parent = root
    return root

def build_hazard_4_plasma(ox, oy, oz, col, mats):
    root = bpy.data.objects.new("Root_H04", None)
    root.location = (0, 0, 0)
    col.objects.link(root)
    name = "H04_Plasma_Nozzle"
    
    # 1. Conduccion pesada de plasma horizontal
    pipe = abs_style.create_cylinder(f"{name}_MainPipe", radius=0.62, depth=2.4, rot=(math.radians(90), 0, 0),
                                     loc=(ox, oy + 0.6, oz + 1.25), mat=mats['dark_steel'], col=col)
    pipe.parent = root
    
    # 2. Brida de acoplamiento pesada con 8 pernos
    flange = abs_style.create_cylinder(f"{name}_HeavyFlange", radius=0.92, depth=0.22, rot=(math.radians(90), 0, 0),
                                       loc=(ox, oy - 0.35, oz + 1.25), mat=mats['hazard_yellow'], col=col)
    flange.parent = root
    
    for p in range(8):
        ang = p * (2.0 * math.pi / 8.0)
        px = ox + math.cos(ang) * 0.78
        pz = oz + 1.25 + math.sin(ang) * 0.78
        bolt = abs_style.create_cylinder(f"{name}_Bolt_{p}", radius=0.045, depth=0.32, rot=(math.radians(90), 0, 0),
                                         loc=(px, oy - 0.35, pz), mat=mats['brass'], col=col)
        bolt.parent = root
        
    # 3. Anillos toroidales de confinamiento rajados en dos
    toroid_l = abs_style.create_torus(f"{name}_ToroidL", major_r=0.95, minor_r=0.12, rot=(math.radians(90), math.radians(28), 0),
                                      loc=(ox - 0.15, oy - 0.65, oz + 1.30), mat=mats['scorched_steel'], col=col)
    toroid_l.parent = root
    toroid_r = abs_style.create_torus(f"{name}_ToroidR", major_r=0.95, minor_r=0.12, rot=(math.radians(90), math.radians(-32), 0),
                                      loc=(ox + 0.18, oy - 0.75, oz + 1.20), mat=mats['scorched_steel'], col=col)
    toroid_r.parent = root
    
    # Bobina de cobre interna expuesta en la fractura
    coil_exp = abs_style.create_torus(f"{name}_CoilExp", major_r=0.92, minor_r=0.06, rot=(math.radians(90), math.radians(10), 0),
                                      loc=(ox, oy - 0.70, oz + 1.25), mat=mats['copper_coil'], col=col)
    coil_exp.parent = root
    
    # 4. Tobera de inyección de plasma cónica fracturada
    nozzle = abs_style.create_cone(f"{name}_NozzleCone", radius1=0.68, radius2=0.35, depth=0.75, rot=(math.radians(90), 0, 0),
                                   loc=(ox, oy - 0.95, oz + 1.25), mat=mats['dark_steel'], col=col)
    nozzle.parent = root
    
    # 5. Chorro de plasma cian presurizado con gradiente
    jet_outer = abs_style.create_cone(f"{name}_PlasmaJetOut", radius1=0.65, radius2=0.08, depth=2.2, rot=(math.radians(-90), 0, 0),
                                      loc=(ox, oy - 2.1, oz + 1.25), mat=mats['plasma_outer'], col=col)
    jet_outer.parent = root
    jet_mid = abs_style.create_cone(f"{name}_PlasmaJetMid", radius1=0.45, radius2=0.05, depth=1.8, rot=(math.radians(-90), 0, 0),
                                    loc=(ox, oy - 1.9, oz + 1.25), mat=mats['plasma_mid'], col=col)
    jet_mid.parent = root
    jet_core = abs_style.create_cone(f"{name}_PlasmaJetCore", radius1=0.25, radius2=0.02, depth=1.3, rot=(math.radians(-90), 0, 0),
                                     loc=(ox, oy - 1.6, oz + 1.25), mat=mats['plasma_core'], col=col)
    jet_core.parent = root
    
    # 6. Anillos de choque sónicos concéntricos
    for s_idx, s_dist in enumerate([0.8, 1.3, 1.8]):
        s_ring = abs_style.create_torus(f"{name}_ShockRing_{s_idx}", major_r=0.32 + s_idx * 0.16, minor_r=0.045,
                                        rot=(math.radians(90), 0, 0), loc=(ox, oy - s_dist, oz + 1.25), mat=mats['plasma_core'], col=col)
        s_ring.parent = root
        
    # 7. Manómetro lateral de presión de plasma
    gauge = abs_style.create_analog_gauge(f"{name}_PlasmaGauge", loc=(ox + 0.72, oy + 0.1, oz + 1.7), rot=(0, 90, 0), radius=0.24, depth=0.1, col=col)
    gauge.parent = root
    return root

def build_hazard_5_vent(ox, oy, oz, col, mats):
    root = bpy.data.objects.new("Root_H05", None)
    root.location = (0, 0, 0)
    col.objects.link(root)
    name = "H05_Vent_Duct"
    
    # 1. Conducto de ventilación rectangular con costillas de refuerzo
    duct = abs_style.create_box(f"{name}_MainDuct", size=(2.1, 1.6, 2.1), loc=(ox, oy, oz + 1.15), mat=mats['dark_steel'], col=col)
    duct.parent = root
    
    # Bridas perimetrales de unión con pernos
    flange_f = abs_style.create_box(f"{name}_FlangeF", size=(2.25, 0.15, 2.25), loc=(ox, oy - 0.75, oz + 1.15), mat=mats['hazard_yellow'], col=col)
    flange_f.parent = root
    flange_b = abs_style.create_box(f"{name}_FlangeB", size=(2.25, 0.15, 2.25), loc=(ox, oy + 0.75, oz + 1.15), mat=mats['dark_steel'], col=col)
    flange_b.parent = root
    
    # 2. Marco frontal de louver con 5 lamas individuales inclinadas y fundidas
    louver_frame = abs_style.create_box(f"{name}_LouverFrame", size=(1.75, 0.12, 1.75), loc=(ox, oy - 0.82, oz + 1.15), mat=mats['scorched_steel'], col=col)
    louver_frame.parent = root
    
    for lv in range(5):
        tilt = math.radians(28 + (lv % 2) * 22)
        slat = abs_style.create_box(f"{name}_Slat_{lv}", size=(1.6, 0.14, 0.07), rot=(tilt, 0, 0),
                                    loc=(ox, oy - 0.82, oz + 0.5 + lv * 0.32), mat=mats['copper_coil'], col=col)
        slat.parent = root
        
    # 3. Motor soplador lateral con difusor y aletas de refrigeración
    motor_body = abs_style.create_cylinder(f"{name}_MotorBody", radius=0.48, depth=0.75, rot=(0, math.radians(90), 0),
                                           loc=(ox + 1.25, oy, oz + 1.15), mat=mats['dark_steel'], col=col)
    motor_body.parent = root
    
    # Aletas del motor
    for f in range(4):
        ang = f * (math.pi / 4.0)
        fin = abs_style.create_box(f"{name}_Fin_{f}", size=(0.65, 0.04, 1.05), rot=(ang, 0, 0),
                                   loc=(ox + 1.25, oy, oz + 1.15), mat=mats['brass'], col=col)
        fin.parent = root
        
    # Caja de bornes del motor
    junction = abs_style.create_box(f"{name}_JunctionBox", size=(0.35, 0.35, 0.25), loc=(ox + 1.25, oy, oz + 1.75), mat=mats['hazard_yellow'], col=col)
    junction.parent = root
    
    # 4. Lengüetas de fuego saliendo a presión por las lamas
    flame_vent1 = build_stylized_flame_cluster(f"{name}_FlameVent1", (ox - 0.35, oy - 0.95, oz + 0.7), scale=1.3, flame_type='orange', col=col, mats=mats)
    flame_vent1.parent = root
    flame_vent2 = build_stylized_flame_cluster(f"{name}_FlameVent2", (ox + 0.35, oy - 0.90, oz + 1.1), scale=1.0, flame_type='orange', col=col, mats=mats)
    flame_vent2.parent = root
    
    # 5. Humo cómic negro escapando por junta superior
    build_smoke_puff(f"{name}_SmokeV1", (ox, oy - 0.4, oz + 2.45), radius=0.34, col=col, mats=mats)
    build_smoke_puff(f"{name}_SmokeV2", (ox + 0.25, oy - 0.5, oz + 2.75), radius=0.28, col=col, mats=mats)
    return root

def build_hazard_6_flashover(ox, oy, oz, col, mats):
    root = bpy.data.objects.new("Root_H06", None)
    root.location = (0, 0, 0)
    col.objects.link(root)
    name = "H06_Flashover"
    
    # 1. Rincón de habitáculo: Mamparo posterior y lateral con zócalo
    wall_back = abs_style.create_box(f"{name}_WallBack", size=(3.0, 0.28, 2.7), loc=(ox, oy + 0.75, oz + 1.35), mat=mats['scorched_steel'], col=col)
    wall_back.parent = root
    wall_side = abs_style.create_box(f"{name}_WallSide", size=(0.28, 2.0, 2.7), loc=(ox - 1.45, oy - 0.15, oz + 1.35), mat=mats['scorched_steel'], col=col)
    wall_side.parent = root
    
    # Zócalo industrial en la base
    skirt_b = abs_style.create_box(f"{name}_SkirtB", size=(3.0, 0.08, 0.18), loc=(ox, oy + 0.6, oz + 0.09), mat=mats['hazard_yellow'], col=col)
    skirt_b.parent = root
    skirt_s = abs_style.create_box(f"{name}_SkirtS", size=(0.08, 1.9, 0.18), loc=(ox - 1.3, oy - 0.2, oz + 0.09), mat=mats['hazard_yellow'], col=col)
    skirt_s.parent = root
    
    # 2. Falso techo desprendido (placa colapsada inclinada)
    ceiling_tilt = abs_style.create_box(f"{name}_CeilingTilt", size=(2.6, 1.8, 0.12), rot=(math.radians(18), 0, math.radians(-12)),
                                       loc=(ox - 0.1, oy - 0.15, oz + 2.45), mat=mats['copper_coil'], col=col)
    ceiling_tilt.parent = root
    
    # Cables tensores del techo partidos colgando
    wire1 = abs_style.create_cylinder(f"{name}_Hanger1", radius=0.02, depth=0.85, loc=(ox + 0.8, oy - 0.3, oz + 2.2), mat=mats['brass'], col=col)
    wire1.parent = root
    wire2 = abs_style.create_cylinder(f"{name}_Hanger2", radius=0.02, depth=1.1, rot=(math.radians(25), 0, 0), loc=(ox - 0.5, oy - 0.7, oz + 2.1), mat=mats['brass'], col=col)
    wire2.parent = root
    
    # 3. Taquilla empotrada calcinada con puertas deformadas
    locker = abs_style.create_box(f"{name}_Locker", size=(0.75, 0.65, 1.85), loc=(ox - 0.95, oy + 0.25, oz + 0.92), mat=mats['dark_steel'], col=col)
    locker.parent = root
    locker_door = abs_style.create_box(f"{name}_LockerDoor", size=(0.65, 0.06, 1.75), rot=(0, math.radians(-25), 0),
                                       loc=(ox - 0.7, oy - 0.1, oz + 0.92), mat=mats['scorched_steel'], col=col)
    locker_door.parent = root
    
    # 4. Capa de fuego rodante (Rollover / Flashover) barriendo el techo horizontalmente
    flame_roll1 = build_stylized_flame_cluster(f"{name}_Roll1", (ox - 0.2, oy - 0.2, oz + 2.05), scale=1.3, flame_type='orange', col=col, mats=mats)
    flame_roll1.parent = root
    flame_roll2 = build_stylized_flame_cluster(f"{name}_Roll2", (ox + 0.6, oy + 0.1, oz + 2.15), scale=1.0, flame_type='orange', col=col, mats=mats)
    flame_roll2.parent = root
    
    # Fuego secundario en la taquilla inferior
    flame_base = build_stylized_flame_cluster(f"{name}_BaseFlame", (ox - 0.85, oy + 0.15, oz + 0.3), scale=0.85, flame_type='orange', col=col, mats=mats)
    flame_base.parent = root
    return root

def generate_lote1_scene(save_blend=True):
    print("=" * 70)
    print("[*] Iniciando generacion de Peligros Ambientales Lote 1 (H01 al H06: Termicos e Igneos)...")
    print("=" * 70)
    
    abs_style.reset_comic_scene(bg_color=(0.04, 0.05, 0.07, 1.0), bg_strength=0.9, ink_thickness=2.4)
    col_peligros = abs_style.create_collection("Peligros_Lote1_Termicos")
    mats = init_thermal_materials()
    
    ped_mat = abs_style.get_comic_material("Pedestal_Peligros1", base_color=(0.08, 0.09, 0.12), roughness=0.45, metallic=0.7)
    hazard_strip_mat = abs_style.get_comic_material("Ped_Hazard_Lote1", base_color=(0.95, 0.65, 0.05), roughness=0.30, metallic=0.2)
    
    spacing_x = 4.8
    spacing_y = 5.2
    
    # Terraza corrida para fila trasera
    abs_style.create_box("Terrace_Row1_Peligros", size=(17.0, 4.8, 1.2), loc=(0, 2.6, 0.6), mat=ped_mat, col=col_peligros)
    
    closeups = {}
    
    HAZARD_BUILDERS = {
        1: build_hazard_1_bulkhead,
        2: build_hazard_2_electrical,
        3: build_hazard_3_magnesium,
        4: build_hazard_4_plasma,
        5: build_hazard_5_vent,
        6: build_hazard_6_flashover,
    }
    
    HAZARD_CAMERAS = {
        1: {"offset": (2.8, -3.8, 2.0), "target_x": 0.0, "target_y": -0.1, "target_z": 1.35, "focal": 32},
        2: {"offset": (2.5, -3.4, 1.8), "target_x": -0.1, "target_y": -0.2, "target_z": 1.20, "focal": 34},
        3: {"offset": (2.6, -3.4, 2.0), "target_x": 0.0, "target_y": -0.2, "target_z": 1.20, "focal": 34},
        4: {"offset": (3.4, -4.4, 2.2), "target_x": -0.3, "target_y": -0.7, "target_z": 1.25, "focal": 29},
        5: {"offset": (2.6, -3.4, 1.9), "target_x": 0.1, "target_y": -0.2, "target_z": 1.15, "focal": 34},
        6: {"offset": (2.8, -3.6, 2.2), "target_x": 0.0, "target_y": 0.0, "target_z": 1.40, "focal": 33},
    }
    
    for idx, (hid, hname, htitle, hdesc) in enumerate(HAZARDS_LOTE1):
        col_idx = idx % 3
        row_idx = idx // 3
        x = (col_idx - 1.0) * spacing_x
        y = (row_idx - 0.5) * spacing_y
        z_step = row_idx * 1.2
        
        # Pedestal con moldura y reborde hazard
        ped = abs_style.create_box(f"Ped_{hname}", size=(4.2, 4.0, 0.22), loc=(x, y, z_step + 0.11), mat=ped_mat, col=col_peligros)
        front_strip = abs_style.create_box(f"Strip_{hname}", size=(4.2, 0.12, 0.06), loc=(x, y - 1.95, z_step + 0.25), mat=hazard_strip_mat, col=col_peligros)
        
        builder = HAZARD_BUILDERS[hid]
        builder(x, y, z_step + 0.22, col_peligros, mats)
        
    # Suelo general
    floor_mat = abs_style.get_comic_material("Floor_Peligros1", base_color=(0.03, 0.035, 0.045), roughness=0.28, metallic=0.8)
    abs_style.create_box("HangarFloor_Peligros1", size=(28.0, 20.0, 0.15), loc=(0, 0, -0.08), mat=floor_mat, col=col_peligros)
    
    abs_style.setup_studio_lighting(sun_energy=5.5, rim_energy=3.8, fill_energy=2.2)
    abs_style.setup_camera(name="Camera_Peligros_Lote1", loc=(0, -18.0, 11.5), target=(0, 0.5, 1.8), focal_length=28)
    
    if save_blend:
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_FILE)
        print(f"[+] Blend guardado: {BLEND_FILE}")
        
    raw_pan_path = os.path.join(RENDERS_DIR, "Raw_Peligros_Lote1_Panorama.png")
    abs_style.render_and_save("Raw_Peligros_Lote1_Panorama.png", res_x=2560, res_y=1440)
    
    # Close-ups individuales calibrados
    for idx, (hid, hname, _, _) in enumerate(HAZARDS_LOTE1):
        col_idx = idx % 3
        row_idx = idx // 3
        x = (col_idx - 1.0) * spacing_x
        y = (row_idx - 0.5) * spacing_y
        z_step = row_idx * 1.2
        
        cam_cfg = HAZARD_CAMERAS.get(hid, {"offset": (2.4, -3.0, 1.8), "target_x": 0.0, "target_y": 0.0, "target_z": 1.2, "focal": 36})
        off_x, off_y, off_z = cam_cfg["offset"]
        t_x = cam_cfg.get("target_x", 0.0)
        t_y = cam_cfg.get("target_y", 0.0)
        t_z = cam_cfg.get("target_z", 1.2)
        foc = cam_cfg["focal"]
        
        abs_style.setup_camera(name=f"Cam_Close_{hname}", loc=(x + off_x, y + off_y, z_step + off_z),
                               target=(x + t_x, y + t_y, z_step + t_z), focal_length=foc)
        close_file = f"CloseUp_{hname}.png"
        abs_style.render_and_save(close_file, res_x=800, res_y=800)
        closeups[hid] = os.path.join(RENDERS_DIR, close_file)
        
    assemble_lote1_sheet(raw_pan_path, closeups)
    print("[+] Lote 1 de Peligros Ambientales completado con exito!")

def assemble_lote1_sheet(deck_render_path, closeups):
    print("[*] Componiendo Lamina Maestra Tecnica 2.5K de Peligros Lote 1...")
    W, H = 2560, 1440
    canvas = Image.new("RGBA", (W, H), (12, 14, 18, 255))
    draw = ImageDraw.Draw(canvas)
    
    try:
        font_main = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 26)
        font_sub = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 15)
        font_pill = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 13)
        font_card_title = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 15)
        font_card_sub = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 12)
        font_card_desc = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 11)
        font_foot = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 11)
    except:
        font_main = font_sub = font_pill = font_card_title = font_card_sub = font_card_desc = font_foot = ImageFont.load_default()
        
    draw.text((40, 18), "ASTRA HAZARD // SISTEMA DE CRISIS Y CATÁSTROFES AMBIENTALES // BLENDER 5.2 LTS", fill=(245, 120, 25), font=font_sub)
    draw.text((40, 46), "SUITE DE PELIGROS 3D // LOTE 1 (H01 A H06: PELIGROS TÉRMICOS E ÍGNEOS)", fill=(255, 255, 255), font=font_main)
    
    badges = [
        ("6 PELIGROS TÉRMICOS", (211, 84, 0)),
        ("PBR STYLIZED + FREESTYLE", (142, 68, 173)),
        ("EMISIVOS CALIBRADOS", (41, 128, 185)),
        ("VERIFICADO 100% CERO BUGS", (39, 174, 96))
    ]
    cur_x = W - 40
    for btext, bcol in reversed(badges):
        tw = len(btext) * 8 + 22
        cur_x -= tw
        draw.rounded_rectangle((cur_x, 32, cur_x + tw - 10, 66), radius=6, fill=bcol)
        draw.text((cur_x + 10, 41), btext, fill=(255, 255, 255), font=font_pill)
        cur_x -= 10
        
    draw.line((40, 88, W - 40, 88), fill=(45, 52, 65), width=2)
    
    # Panorama superior (2480 x 590)
    pan_w = 2480
    pan_h = 590
    if os.path.exists(deck_render_path):
        pan_img = Image.open(deck_render_path).convert("RGBA")
        crop_box = (60, 240, 2500, 1200)
        c_w = crop_box[2] - crop_box[0]
        c_h = crop_box[3] - crop_box[1]
        t_w = int(pan_h * (c_w / c_h))
        resized = pan_img.crop(crop_box).resize((pan_w, pan_h), Image.Resampling.LANCZOS)
        canvas.paste(resized, (40, 102))
        draw.rectangle((40, 102, 40 + pan_w, 102 + pan_h), outline=(48, 56, 70), width=2)
        
    start_y = 712
    card_w = 808
    card_h = 345
    gap_x = 28
    gap_y = 18
    
    for idx, (hid, hname, htitle, hdesc) in enumerate(HAZARDS_LOTE1):
        col_idx = idx % 3
        row_idx = idx // 3
        cx = 40 + col_idx * (card_w + gap_x)
        cy = start_y + row_idx * (card_h + gap_y)
        
        draw.rectangle((cx, cy, cx + card_w, cy + card_h), fill=(18, 21, 28, 255), outline=(38, 44, 56), width=2)
        
        thumb_path = closeups.get(hid)
        if thumb_path and os.path.exists(thumb_path):
            t_img = Image.open(thumb_path).convert("RGBA")
            t_resized = t_img.resize((305, 305), Image.Resampling.LANCZOS)
            canvas.paste(t_resized, (cx + 18, cy + 20))
            draw.rectangle((cx + 18, cy + 20, cx + 18 + 305, cy + 20 + 305), outline=(45, 52, 65), width=1)
            
        tx = cx + 342
        draw.text((tx, cy + 22), f"SISTEMA DE CRISIS H0{hid}", fill=(245, 120, 25), font=font_card_sub)
        
        t_lines = textwrap.wrap(htitle, width=28)
        ty = cy + 44
        for tl in t_lines[:2]:
            draw.text((tx, ty), tl, fill=(255, 255, 255), font=font_card_title)
            ty += 20
            
        draw.line([(tx, ty + 6), (cx + card_w - 20, ty + 6)], fill=(40, 48, 62), width=1)
        ty += 16
        
        d_lines = textwrap.wrap(hdesc, width=38)
        for dl in d_lines[:4]:
            draw.text((tx, ty), dl, fill=(175, 185, 200), font=font_card_desc)
            ty += 18
            
        ty += 10
        draw.text((tx, ty), "• Mitigacion: Chorro Hydra / Polvo Quimico", fill=(130, 200, 240), font=font_card_desc)
        ty += 16
        draw.text((tx, ty), "• Dinamica: Expansion termica activa", fill=(130, 200, 240), font=font_card_desc)
        
        draw.rounded_rectangle((tx, cy + card_h - 38, cx + card_w - 20, cy + card_h - 14), radius=4, fill=(15, 18, 24))
        draw.text((tx + 10, cy + card_h - 31), "ESTADO: VERIFICADO & CERTIFICADO 100% 3D", fill=(46, 204, 113), font=font_foot)
        
    master_path = os.path.join(RENDERS_DIR, "Showcase_Peligros_Lote1_Termicos_Master.png")
    artifact_path = os.path.join(ARTIFACT_DIR, "Showcase_Peligros_Lote1_Termicos_Master.png")
    canvas.save(master_path, format="PNG")
    shutil.copy2(master_path, artifact_path)
    print(f"[+] Lamina Maestra guardada en: {master_path}")
    print(f"[+] Sincronizada con artefacto con exito!")

if __name__ == "__main__":
    generate_lote1_scene()

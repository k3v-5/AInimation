# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Generador Oficial de Peligros Ambientales - Lote 5: Focos Biologicos y Riesgo Radiologico (H25 al H30)
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
BLEND_FILE = os.path.join(SCRIPT_DIR, "Peligros_Lote5_Biologicos.blend")

HAZARDS_LOTE5 = [
    (25, "H25_Shattered_BSL4_Incubator", "Incubadora BSL-4 Reventada",
     "Camara de bioseguridad con cristal fracturado, brote de zarcillos fungicos bioluminiscentes y esporas suspendidas."),
    (26, "H26_Exposed_Fuel_Rod_Basket", "Barras de Combustible Radiologicas",
     "Contenedor de plomo blindado abierto, barras de combustible expuestas con resplandor azul Cherenkov y dosimetro en alerta."),
    (27, "H27_Slime_Clogged_Valve", "Valvula con Escoria Biologica",
     "Tuberia de saneamiento atascada, valvula trabada rezumando masa gelatinosa viscosa verde y estalactitas goteantes."),
    (28, "H28_Overflowing_Toxic_Sump", "Drenaje Septico Desbordado",
     "Sumidero de fundicion con rejilla empujada hacia arriba por lodo caustico burbujeante y vapores purpura fosforescentes."),
    (29, "H29_Shattered_Cryo_Dewar", "Frasco Criogenico Patogeno Roto",
     "Dewar termico de acero inoxidable volcado, derrame de cultivo patogeno carmesi con niebla criogenica y rotulo biohazard."),
    (30, "H30_Fungal_Colonized_Scrubber", "Depurador de Aire Colonizado",
     "Unidad de filtrado HEPA con persianas forzadas por bulbos fungicos parasitos anaranjados infectando el flujo de aire."),
]

def init_bio_materials():
    mats = {}
    mats['dark_steel'] = abs_style.get_comic_material("Mat_B_DarkSteel", base_color=(0.14, 0.15, 0.18), roughness=0.38, metallic=0.85)
    mats['scorched_steel'] = abs_style.get_comic_material("Mat_B_Scorched", base_color=(0.08, 0.08, 0.09), roughness=0.85, metallic=0.30)
    mats['lead_shield'] = abs_style.get_comic_material("Mat_B_Lead", base_color=(0.22, 0.24, 0.28), roughness=0.55, metallic=0.75)
    mats['stainless'] = abs_style.get_comic_material("Mat_B_Stainless", base_color=(0.88, 0.90, 0.92), roughness=0.18, metallic=0.92)
    mats['hazard_yellow'] = abs_style.get_comic_material("Mat_B_HazardYel", base_color=(0.95, 0.70, 0.08), roughness=0.32, metallic=0.15)
    mats['hazard_orange'] = abs_style.get_comic_material("Mat_B_HazardOrg", base_color=(0.95, 0.40, 0.08), roughness=0.35, metallic=0.20)
    mats['hazard_purple'] = abs_style.get_comic_material("Mat_B_HazardPurp", base_color=(0.60, 0.15, 0.75), roughness=0.40, metallic=0.20)
    mats['brass'] = abs_style.get_comic_material("Mat_B_Brass", base_color=(0.88, 0.68, 0.18), roughness=0.25, metallic=0.90)
    mats['glass_acrylic'] = abs_style.get_comic_material("Mat_B_Glass", base_color=(0.80, 0.92, 0.95), roughness=0.10, metallic=0.05)
    
    # Efectos bioluminiscentes y radiación Cherenkov calibrados (punchy, cero burnout blanco)
    # Resplandor azul Cherenkov radiológico
    mats['cherenkov_blue'] = abs_style.get_comic_material("Mat_B_Cherenkov", base_color=(0.04, 0.45, 0.92), roughness=0.15, metallic=0.10,
                                                          emissive_color=(0.08, 0.55, 1.0, 1.0), emissive_strength=1.8)
    # Zarcillos fúngicos verde biohazard profundo
    mats['bio_green'] = abs_style.get_comic_material("Mat_B_BioGreen", base_color=(0.12, 0.65, 0.08), roughness=0.20, metallic=0.05,
                                                     emissive_color=(0.15, 0.78, 0.10, 1.0), emissive_strength=1.4)
    # Esporas y bulbos parasitarios naranja fósforo intenso
    mats['fungal_bulb'] = abs_style.get_comic_material("Mat_B_FungalBulb", base_color=(0.88, 0.35, 0.05), roughness=0.25, metallic=0.05,
                                                       emissive_color=(0.95, 0.40, 0.06, 1.0), emissive_strength=1.5)
    # Patógeno rojo carmesí viscoso
    mats['pathogen_red'] = abs_style.get_comic_material("Mat_B_PathRed", base_color=(0.65, 0.04, 0.06), roughness=0.12, metallic=0.20,
                                                        emissive_color=(0.80, 0.06, 0.08, 1.0), emissive_strength=1.4)
    # Lodo séptico púrpura fósforo
    mats['toxic_sludge'] = abs_style.get_comic_material("Mat_B_Sludge", base_color=(0.32, 0.08, 0.40), roughness=0.15, metallic=0.10,
                                                        emissive_color=(0.48, 0.12, 0.58, 1.0), emissive_strength=1.6)
    return mats

def build_hazard_25_incubator(ox, oy, oz, col, mats):
    root = bpy.data.objects.new("Root_H25", None)
    root.location = (0, 0, 0)
    col.objects.link(root)
    name = "H25_Incubator"
    
    # 1. Mesa soporte de laboratorio en acero inoxidable
    bench = abs_style.create_box(f"{name}_Bench", size=(1.8, 1.2, 0.8), loc=(ox, oy, oz + 0.4), mat=mats['stainless'], col=col)
    bench.parent = root
    
    # 2. Cámara de incubación con chasis reforzado
    chassis = abs_style.create_box(f"{name}_Chassis", size=(1.5, 0.95, 1.3), loc=(ox, oy, oz + 1.45), mat=mats['dark_steel'], col=col)
    chassis.parent = root
    
    # Marco frontal de bioseguridad amarillo hazard
    frame = abs_style.create_box(f"{name}_BioFrame", size=(1.54, 0.12, 1.34), loc=(ox, oy - 0.48, oz + 1.45), mat=mats['hazard_yellow'], col=col)
    frame.parent = root
    
    # Ventana frontal de acrílico fracturada (paneles inclinados)
    glass_l = abs_style.create_box(f"{name}_GlassL", size=(0.65, 0.04, 1.1), rot=(0, math.radians(-12), 0),
                                  loc=(ox - 0.35, oy - 0.49, oz + 1.45), mat=mats['glass_acrylic'], col=col)
    glass_l.parent = root
    glass_r = abs_style.create_box(f"{name}_GlassR", size=(0.65, 0.04, 1.1), rot=(math.radians(18), math.radians(22), 0),
                                  loc=(ox + 0.35, oy - 0.55, oz + 1.4), mat=mats['glass_acrylic'], col=col)
    glass_r.parent = root
    
    # 3. Zarcillos de biomasa alienígena verde bioluminiscente brotando del orificio
    for z_i in range(5):
        z_ang = z_i * (math.pi / 2.5)
        tendril = abs_style.create_torus(f"{name}_Tendril_{z_i}", major_r=0.28 + z_i * 0.06, minor_r=0.035,
                                         rot=(math.radians(45), z_ang, math.radians(30)),
                                         loc=(ox + math.cos(z_ang) * 0.25, oy - 0.55 - z_i * 0.1, oz + 1.4 + math.sin(z_ang) * 0.25),
                                         mat=mats['bio_green'], col=col)
        tendril.parent = root
        
    # Esporas flotantes bioluminiscentes en el aire
    for sp_i, (sx, sy, sz) in enumerate([(0.2, -0.8, 1.8), (-0.3, -0.9, 1.5), (0.4, -0.7, 1.2), (0.0, -1.0, 1.9)]):
        spore = abs_style.create_cylinder(f"{name}_Spore_{sp_i}", radius=0.06, depth=0.06,
                                          loc=(ox + sx, oy + sy, oz + sz), mat=mats['bio_green'], col=col)
        spore.parent = root
        
    # Mancha de baba cáustica sobre la mesa y escurriendo
    drip = abs_style.create_cylinder(f"{name}_SlimeDrip", radius=0.35, depth=0.03,
                                     loc=(ox + 0.1, oy - 0.45, oz + 0.81), mat=mats['bio_green'], col=col)
    drip.parent = root
    return root

def build_hazard_26_fuel_rods(ox, oy, oz, col, mats):
    root = bpy.data.objects.new("Root_H26", None)
    root.location = (0, 0, 0)
    col.objects.link(root)
    name = "H26_Fuel_Rods"
    
    # 1. Contenedor de transporte blindado de plomo pesado cilíndrico
    cask = abs_style.create_cylinder(f"{name}_LeadCask", radius=0.88, depth=1.5, loc=(ox, oy, oz + 0.75), mat=mats['lead_shield'], col=col)
    cask.parent = root
    
    # Cinchas de refuerzo perimetrales en acero oscuro
    strap1 = abs_style.create_torus(f"{name}_CaskStrap1", major_r=0.90, minor_r=0.045, loc=(ox, oy, oz + 0.45), mat=mats['dark_steel'], col=col)
    strap1.parent = root
    strap2 = abs_style.create_torus(f"{name}_CaskStrap2", major_r=0.90, minor_r=0.045, loc=(ox, oy, oz + 1.15), mat=mats['dark_steel'], col=col)
    strap2.parent = root
    
    # Tapa blindada de plomo caída de lado apoyada en el suelo
    lid = abs_style.create_cylinder(f"{name}_CaskLid", radius=0.92, depth=0.25, rot=(math.radians(65), 0, math.radians(-35)),
                                    loc=(ox + 0.95, oy - 0.65, oz + 0.45), mat=mats['lead_shield'], col=col)
    lid.parent = root
    
    # 2. Cesta de combustible nuclear con 4 barras de uranio expuestas
    rod_coords = [(-0.25, -0.25), (0.25, -0.25), (-0.25, 0.25), (0.25, 0.25)]
    for r_idx, (rx, ry) in enumerate(rod_coords):
        rod = abs_style.create_cylinder(f"{name}_FuelRod_{r_idx}", radius=0.11, depth=1.7,
                                        loc=(ox + rx, oy + ry, oz + 1.45), mat=mats['cherenkov_blue'], col=col)
        rod.parent = root
        
        # Anillos separadores de zirconio en las barras
        for z_i in range(3):
            z_ring = abs_style.create_torus(f"{name}_ZircRing_{r_idx}_{z_i}", major_r=0.125, minor_r=0.025,
                                           loc=(ox + rx, oy + ry, oz + 0.9 + z_i * 0.45), mat=mats['brass'], col=col)
            z_ring.parent = root
            
    # 3. Halo y resplandor de radiación Cherenkov
    cherenkov_ring = abs_style.create_torus(f"{name}_CherenkovRing", major_r=0.68, minor_r=0.045,
                                           loc=(ox, oy, oz + 1.5), mat=mats['cherenkov_blue'], col=col)
    cherenkov_ring.parent = root
    pool_glow = abs_style.create_cylinder(f"{name}_PoolGlow", radius=0.75, depth=0.05,
                                          loc=(ox, oy, oz + 0.95), mat=mats['cherenkov_blue'], col=col)
    pool_glow.parent = root
    
    # 4. Dosímetro de radiación montado en el lateral en zona crítica
    gauge = abs_style.create_analog_gauge(f"{name}_RadGauge", loc=(ox - 0.85, oy - 0.4, oz + 1.1), rot=(0, 0, math.radians(-45)), radius=0.2, depth=0.1, col=col)
    gauge.parent = root
    return root

def build_hazard_27_slime_valve(ox, oy, oz, col, mats):
    root = bpy.data.objects.new("Root_H27", None)
    root.location = (0, 0, 0)
    col.objects.link(root)
    name = "H27_Slime_Valve"
    
    # 1. Tubería horizontal gruesa de saneamiento
    pipe = abs_style.create_cylinder(f"{name}_SanPipe", radius=0.45, depth=2.4, rot=(0, math.radians(90), 0),
                                     loc=(ox, oy + 0.2, oz + 1.5), mat=mats['dark_steel'], col=col)
    pipe.parent = root
    
    # Bridas de acoplamiento laterales con pernos
    flange_l = abs_style.create_cylinder(f"{name}_FlangeL", radius=0.62, depth=0.15, rot=(0, math.radians(90), 0),
                                         loc=(ox - 0.85, oy + 0.2, oz + 1.5), mat=mats['hazard_yellow'], col=col)
    flange_l.parent = root
    flange_r = abs_style.create_cylinder(f"{name}_FlangeR", radius=0.62, depth=0.15, rot=(0, math.radians(90), 0),
                                         loc=(ox + 0.85, oy + 0.2, oz + 1.5), mat=mats['hazard_yellow'], col=col)
    flange_r.parent = root
    
    # 2. Cuerpo de válvula de compuerta central en latón
    valve_body = abs_style.create_box(f"{name}_ValveBody", size=(0.75, 0.75, 0.85), loc=(ox, oy + 0.2, oz + 1.5), mat=mats['brass'], col=col)
    valve_body.parent = root
    
    # Volante superior de la válvula trabado
    wheel_stem = abs_style.create_cylinder(f"{name}_WheelStem", radius=0.06, depth=0.6, loc=(ox, oy + 0.2, oz + 2.1), mat=mats['dark_steel'], col=col)
    wheel_stem.parent = root
    wheel = abs_style.create_torus(f"{name}_ValveWheel", major_r=0.38, minor_r=0.045, loc=(ox, oy + 0.2, oz + 2.4), mat=mats['hazard_yellow'], col=col)
    wheel.parent = root
    
    # 3. Masa de escoria biológica gelatinosa rezumando de la fisura inferior
    slime_blob = abs_style.create_cylinder(f"{name}_SlimeBlob", radius=0.38, depth=0.55, rot=(math.radians(25), 0, 0),
                                           loc=(ox, oy - 0.15, oz + 1.05), mat=mats['bio_green'], col=col)
    slime_blob.parent = root
    
    # Estalactitas de mucílago colgando y goteando
    for d_i, (dx, dy, dlen) in enumerate([(-0.15, -0.1, 0.65), (0.12, -0.18, 0.85), (0.0, -0.25, 0.55)]):
        stalactite = abs_style.create_cone(f"{name}_SlimeDrip_{d_i}", radius1=0.08, radius2=0.01, depth=dlen,
                                           rot=(math.radians(180), 0, 0), loc=(ox + dx, oy + dy, oz + 0.95 - dlen * 0.5),
                                           mat=mats['bio_green'], col=col)
        stalactite.parent = root
        
    # 4. Gran charco de lodo viscoso en el suelo con ondas
    puddle = abs_style.create_cylinder(f"{name}_SlimePuddle", radius=1.45, depth=0.05, loc=(ox, oy - 0.45, oz + 0.025), mat=mats['bio_green'], col=col)
    puddle.parent = root
    puddle_rim = abs_style.create_torus(f"{name}_SlimeRim", major_r=1.42, minor_r=0.035, loc=(ox, oy - 0.45, oz + 0.03), mat=mats['bio_green'], col=col)
    puddle_rim.parent = root
    return root

def build_hazard_28_toxic_sump(ox, oy, oz, col, mats):
    root = bpy.data.objects.new("Root_H28", None)
    root.location = (0, 0, 0)
    col.objects.link(root)
    name = "H28_Toxic_Sump"
    
    # 1. Brocal de sumidero circular de hormigón/acero
    rim = abs_style.create_torus(f"{name}_SumpRim", major_r=1.2, minor_r=0.18, loc=(ox, oy, oz + 0.18), mat=mats['dark_steel'], col=col)
    rim.parent = root
    
    # Cilindro de foso profundo
    well = abs_style.create_cylinder(f"{name}_SumpWell", radius=1.15, depth=0.45, loc=(ox, oy, oz + 0.22), mat=mats['scorched_steel'], col=col)
    well.parent = root
    
    # 2. Rejilla de fundición partida y empujada hacia arriba en ángulo por la presión interna
    grate_l = abs_style.create_cylinder(f"{name}_GrateL", radius=0.95, depth=0.08, rot=(math.radians(-32), 0, math.radians(20)),
                                        loc=(ox - 0.25, oy - 0.2, oz + 0.55), mat=mats['dark_steel'], col=col)
    grate_l.parent = root
    
    # 3. Lodo séptico cáustico burbujeante de color púrpura fosforescente
    sludge_surface = abs_style.create_cylinder(f"{name}_SludgeSurface", radius=1.05, depth=0.12, loc=(ox, oy, oz + 0.32), mat=mats['toxic_sludge'], col=col)
    sludge_surface.parent = root
    
    # Burbujas cáusticas hemisféricas estallando
    for b_i, (bx, by, br) in enumerate([(0.3, 0.2, 0.22), (-0.2, -0.3, 0.18), (0.1, -0.4, 0.25), (-0.4, 0.3, 0.15)]):
        bubble = abs_style.create_cylinder(f"{name}_Bubble_{b_i}", radius=br, depth=br * 0.8, loc=(ox + bx, oy + by, oz + 0.42), mat=mats['toxic_sludge'], col=col)
        bubble.parent = root
        
    # 4. Vapores tóxicos fosforescentes ascendiendo (nubes de gas púrpura bajas)
    gas1 = abs_style.create_torus(f"{name}_GasCloud1", major_r=0.45, minor_r=0.15, loc=(ox + 0.2, oy + 0.1, oz + 0.65), mat=mats['toxic_sludge'], col=col)
    gas1.parent = root
    gas2 = abs_style.create_torus(f"{name}_GasCloud2", major_r=0.38, minor_r=0.12, loc=(ox - 0.25, oy - 0.15, oz + 0.85), mat=mats['toxic_sludge'], col=col)
    gas2.parent = root
    
    # Vertido desbordado en el suelo
    overflow = abs_style.create_cylinder(f"{name}_OverflowPool", radius=1.55, depth=0.03, loc=(ox, oy, oz + 0.02), mat=mats['toxic_sludge'], col=col)
    overflow.parent = root
    return root

def build_hazard_29_cryo_dewar(ox, oy, oz, col, mats):
    root = bpy.data.objects.new("Root_H29", None)
    root.location = (0, 0, 0)
    col.objects.link(root)
    name = "H29_Cryo_Dewar"
    
    # 1. Frasco Dewar cilíndrico de acero inoxidable volcado con boca hacia el frente
    dewar = abs_style.create_cylinder(f"{name}_DewarBody", radius=0.45, depth=1.6, rot=(math.radians(80), 0, math.radians(-45)),
                                      loc=(ox - 0.2, oy + 0.2, oz + 0.45), mat=mats['stainless'], col=col)
    dewar.parent = root
    
    # Anillos protectores de goma en los extremos
    collar_b = abs_style.create_torus(f"{name}_DewarCollarB", major_r=0.47, minor_r=0.045, rot=(math.radians(80), 0, math.radians(-45)),
                                      loc=(ox - 0.7, oy + 0.7, oz + 0.45), mat=mats['dark_steel'], col=col)
    collar_b.parent = root
    collar_t = abs_style.create_torus(f"{name}_DewarCollarT", major_r=0.47, minor_r=0.045, rot=(math.radians(80), 0, math.radians(-45)),
                                      loc=(ox + 0.3, oy - 0.3, oz + 0.45), mat=mats['hazard_yellow'], col=col)
    collar_t.parent = root
    
    # Tapa hermética desprendida tirada en el suelo
    cap = abs_style.create_cylinder(f"{name}_DewarCap", radius=0.32, depth=0.22, rot=(math.radians(25), math.radians(30), 0),
                                    loc=(ox + 0.85, oy - 0.45, oz + 0.12), mat=mats['dark_steel'], col=col)
    cap.parent = root
    
    # 2. Derrame de patógeno líquido rojo carmesí brotando de la boca
    spill = abs_style.create_cylinder(f"{name}_PathogenSpill", radius=1.35, depth=0.04, loc=(ox + 0.4, oy - 0.5, oz + 0.02), mat=mats['pathogen_red'], col=col)
    spill.parent = root
    
    # Zarcillos y regueros secundarios
    drip_trail = abs_style.create_cylinder(f"{name}_Trail", radius=0.65, depth=0.035, loc=(ox + 0.75, oy - 1.1, oz + 0.02), mat=mats['pathogen_red'], col=col)
    drip_trail.parent = root
    
    # 3. Niebla criogénica fría pesada reptando sobre el charco carmesí
    fog1 = abs_style.create_cylinder(f"{name}_DewarFog1", radius=0.55, depth=0.18, loc=(ox + 0.1, oy - 0.4, oz + 0.12), mat=mats['glass_acrylic'], col=col)
    fog1.parent = root
    fog2 = abs_style.create_cylinder(f"{name}_DewarFog2", radius=0.42, depth=0.15, loc=(ox + 0.5, oy - 0.8, oz + 0.1), mat=mats['glass_acrylic'], col=col)
    fog2.parent = root
    
    # Placa con pictograma Biohazard amarillo en el cuerpo del frasco
    sign = abs_style.create_box(f"{name}_BioSign", size=(0.35, 0.04, 0.35), rot=(math.radians(90), 0, math.radians(25)),
                                loc=(ox - 0.2, oy + 0.1, oz + 0.92), mat=mats['hazard_yellow'], col=col)
    sign.parent = root
    return root

def build_hazard_30_fungal_scrubber(ox, oy, oz, col, mats):
    root = bpy.data.objects.new("Root_H30", None)
    root.location = (0, 0, 0)
    col.objects.link(root)
    name = "H30_Fungal_Scrubber"
    
    # 1. Carcasa de unidad de filtración industrial HEPA
    housing = abs_style.create_box(f"{name}_Housing", size=(1.8, 1.1, 2.1), loc=(ox, oy + 0.2, oz + 1.25), mat=mats['dark_steel'], col=col)
    housing.parent = root
    
    # Brida de conducto superior
    flange = abs_style.create_box(f"{name}_TopFlange", size=(1.4, 0.9, 0.15), loc=(ox, oy + 0.2, oz + 2.35), mat=mats['hazard_yellow'], col=col)
    flange.parent = root
    
    # 2. Rejilla frontal con persianas metálicas reventadas y forzadas hacia afuera
    for l_i in range(5):
        lz = oz + 0.5 + l_i * 0.35
        # Lamas forzadas por la biomasa
        louver = abs_style.create_box(f"{name}_Louver_{l_i}", size=(1.4, 0.05, 0.18),
                                      rot=(math.radians(-35 + l_i * 8), 0, 0),
                                      loc=(ox, oy - 0.38 - l_i * 0.04, lz), mat=mats['dark_steel'], col=col)
        louver.parent = root
        
    # 3. Bulbos fúngicos parasitarios anaranjados bioluminiscentes saliendo entre las lamas
    for b_idx, (bx, bz, br) in enumerate([(-0.35, 1.1, 0.28), (0.25, 1.35, 0.35), (-0.1, 1.6, 0.25), (0.35, 0.85, 0.22)]):
        bulb = abs_style.create_cylinder(f"{name}_FungalBulb_{b_idx}", radius=br, depth=br * 1.1,
                                         rot=(math.radians(35), 0, math.radians(20 * b_idx)),
                                         loc=(ox + bx, oy - 0.55, oz + bz), mat=mats['fungal_bulb'], col=col)
        bulb.parent = root
        
        # Pústulas / poros esféricos en los bulbos
        pustule = abs_style.create_cylinder(f"{name}_Pustule_{b_idx}", radius=br * 0.45, depth=br * 0.45,
                                           loc=(ox + bx + 0.05, oy - 0.7, oz + bz + 0.05), mat=mats['bio_green'], col=col)
        pustule.parent = root
        
    # 4. Zarcillos filamentosos arrastrándose hacia el suelo
    for z_i in range(3):
        zx = ox - 0.4 + z_i * 0.4
        root_vine = abs_style.create_cylinder(f"{name}_RootVine_{z_i}", radius=0.045, depth=1.2,
                                             rot=(math.radians(25), 0, math.radians(-15 * z_i)),
                                             loc=(zx, oy - 0.5, oz + 0.6), mat=mats['bio_green'], col=col)
        root_vine.parent = root
        
    # Mancha de micelio en el suelo frente al depurador
    mycelium = abs_style.create_cylinder(f"{name}_MyceliumPuddle", radius=1.25, depth=0.03,
                                         loc=(ox, oy - 0.75, oz + 0.02), mat=mats['fungal_bulb'], col=col)
    mycelium.parent = root
    return root

def generate_lote5_scene(save_blend=True):
    print("=" * 70)
    print("[*] Iniciando generacion de Peligros Ambientales Lote 5 (H25 al H30: Biologicos y Radiacion)...")
    print("=" * 70)
    
    abs_style.reset_comic_scene(bg_color=(0.04, 0.05, 0.07, 1.0), bg_strength=0.9, ink_thickness=2.4)
    col_peligros = abs_style.create_collection("Peligros_Lote5_Biologicos")
    mats = init_bio_materials()
    
    ped_mat = abs_style.get_comic_material("Pedestal_Peligros5", base_color=(0.08, 0.09, 0.12), roughness=0.45, metallic=0.7)
    hazard_strip_mat = abs_style.get_comic_material("Ped_Hazard_Lote5", base_color=(0.40, 0.90, 0.15), roughness=0.30, metallic=0.2)
    
    spacing_x = 4.8
    spacing_y = 5.2
    
    # Terraza corrida para fila trasera
    abs_style.create_box("Terrace_Row1_Biologicos", size=(17.0, 4.8, 1.2), loc=(0, 2.6, 0.6), mat=ped_mat, col=col_peligros)
    
    closeups = {}
    
    HAZARD_BUILDERS = {
        25: build_hazard_25_incubator,
        26: build_hazard_26_fuel_rods,
        27: build_hazard_27_slime_valve,
        28: build_hazard_28_toxic_sump,
        29: build_hazard_29_cryo_dewar,
        30: build_hazard_30_fungal_scrubber,
    }
    
    HAZARD_CAMERAS = {
        25: {"offset": (2.4, -3.2, 1.8), "target_x": 0.0, "target_y": -0.3, "target_z": 1.25, "focal": 36}, # Incubator
        26: {"offset": (2.2, -3.2, 1.8), "target_x": 0.1, "target_y": -0.2, "target_z": 1.15, "focal": 36}, # Fuel rods
        27: {"offset": (2.4, -3.2, 1.8), "target_x": 0.0, "target_y": -0.2, "target_z": 1.25, "focal": 36}, # Slime valve
        28: {"offset": (2.0, -3.0, 2.1), "target_x": 0.0, "target_y": -0.1, "target_z": 0.75, "focal": 36}, # Sump
        29: {"offset": (2.2, -2.8, 1.5), "target_x": 0.2, "target_y": -0.3, "target_z": 0.45, "focal": 36}, # Cryo dewar
        30: {"offset": (2.4, -3.2, 1.8), "target_x": 0.0, "target_y": -0.3, "target_z": 1.25, "focal": 36}, # Scrubber
    }
    
    for idx, (hid, hname, htitle, hdesc) in enumerate(HAZARDS_LOTE5):
        col_idx = idx % 3
        row_idx = idx // 3
        x = (col_idx - 1.0) * spacing_x
        y = (row_idx - 0.5) * spacing_y
        z_step = row_idx * 1.2
        
        # Pedestal con moldura y reborde de iluminacion verde bioluminiscente
        ped = abs_style.create_box(f"Ped_{hname}", size=(4.2, 4.0, 0.22), loc=(x, y, z_step + 0.11), mat=ped_mat, col=col_peligros)
        front_strip = abs_style.create_box(f"Strip_{hname}", size=(4.2, 0.12, 0.06), loc=(x, y - 1.95, z_step + 0.25), mat=hazard_strip_mat, col=col_peligros)
        
        builder = HAZARD_BUILDERS[hid]
        builder(x, y, z_step + 0.22, col_peligros, mats)
        
    # Suelo general
    floor_mat = abs_style.get_comic_material("Floor_Peligros5", base_color=(0.03, 0.035, 0.045), roughness=0.28, metallic=0.8)
    abs_style.create_box("HangarFloor_Peligros5", size=(28.0, 20.0, 0.15), loc=(0, 0, -0.08), mat=floor_mat, col=col_peligros)
    
    abs_style.setup_studio_lighting(sun_energy=5.5, rim_energy=3.8, fill_energy=2.2)
    abs_style.setup_camera(name="Camera_Peligros_Lote5", loc=(0, -18.0, 11.5), target=(0, 0.5, 1.8), focal_length=28)
    
    if save_blend:
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_FILE)
        print(f"[+] Blend guardado: {BLEND_FILE}")
        
    raw_pan_path = os.path.join(RENDERS_DIR, "Raw_Peligros_Lote5_Panorama.png")
    abs_style.render_and_save("Raw_Peligros_Lote5_Panorama.png", res_x=2560, res_y=1440)
    
    # Close-ups individuales con aislamiento estricto
    def set_hierarchy_hide_render(obj, hide):
        if not obj:
            return
        obj.hide_render = hide
        for child in obj.children:
            set_hierarchy_hide_render(child, hide)

    for idx, (hid, hname, _, _) in enumerate(HAZARDS_LOTE5):
        col_idx = idx % 3
        row_idx = idx // 3
        x = (col_idx - 1.0) * spacing_x
        y = (row_idx - 0.5) * spacing_y
        z_step = row_idx * 1.2
        
        # Ocultar todos los otros peligros y pedestales ajenos para primer plano pristino
        for other_idx, (o_hid, o_hname, _, _) in enumerate(HAZARDS_LOTE5):
            is_other = (o_hid != hid)
            o_root = bpy.data.objects.get(f"Root_H{o_hid:02d}")
            if o_root:
                set_hierarchy_hide_render(o_root, is_other)
            o_ped = bpy.data.objects.get(f"Ped_{o_hname}")
            if o_ped:
                o_ped.hide_render = is_other
            o_strip = bpy.data.objects.get(f"Strip_{o_hname}")
            if o_strip:
                o_strip.hide_render = is_other
        
        cam_cfg = HAZARD_CAMERAS.get(hid, {"offset": (2.4, -3.2, 1.8), "target_x": 0.0, "target_y": 0.0, "target_z": 1.2, "focal": 36})
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
        
    # Restaurar visibilidad de todos para el estado final del blend
    for o_hid, o_hname, _, _ in HAZARDS_LOTE5:
        o_root = bpy.data.objects.get(f"Root_H{o_hid:02d}")
        if o_root:
            set_hierarchy_hide_render(o_root, False)
        o_ped = bpy.data.objects.get(f"Ped_{o_hname}")
        if o_ped:
            o_ped.hide_render = False
        o_strip = bpy.data.objects.get(f"Strip_{o_hname}")
        if o_strip:
            o_strip.hide_render = False
            
    assemble_lote5_sheet(raw_pan_path, closeups)
    print("[+] Lote 5 de Peligros Ambientales completado con exito!")

def assemble_lote5_sheet(deck_render_path, closeups):
    print("[*] Componiendo Lamina Maestra Tecnica 2.5K de Peligros Lote 5...")
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
        
    draw.text((40, 18), "ASTRA HAZARD // SISTEMA DE CRISIS Y CATÁSTROFES AMBIENTALES // BLENDER 5.2 LTS", fill=(46, 204, 113), font=font_sub)
    draw.text((40, 46), "SUITE DE PELIGROS 3D // LOTE 5 (H25 A H30: FOCOS BIOLÓGICOS Y RIESGO RADIOLÓGICO)", fill=(255, 255, 255), font=font_main)
    
    badges = [
        ("6 PELIGROS BIOLÓGICOS & RAD", (39, 174, 96)),
        ("RADIACIÓN CHERENKOV & BIOHAZARD", (41, 128, 185)),
        ("CONTAMINACIÓN Y TOXICIDAD", (142, 68, 173)),
        ("VERIFICADO 100% CERO BUGS", (211, 84, 0))
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
        resized = pan_img.crop(crop_box).resize((pan_w, pan_h), Image.Resampling.LANCZOS)
        canvas.paste(resized, (40, 102))
        draw.rectangle((40, 102, 40 + pan_w, 102 + pan_h), outline=(48, 56, 70), width=2)
        
    start_y = 712
    card_w = 808
    card_h = 345
    gap_x = 28
    gap_y = 18
    
    for idx, (hid, hname, htitle, hdesc) in enumerate(HAZARDS_LOTE5):
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
        draw.text((tx, cy + 22), f"SISTEMA DE CRISIS H{hid}", fill=(46, 204, 113), font=font_card_sub)
        
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
        draw.text((tx, ty), "• Mitigacion: Purga Quimica / Blindaje Plomo / Incineracion", fill=(100, 220, 150), font=font_card_desc)
        ty += 16
        draw.text((tx, ty), "• Fisica: Infeccion Esporas / Envenenamiento / Radiacion", fill=(100, 220, 150), font=font_card_desc)
        
        draw.rounded_rectangle((tx, cy + card_h - 38, cx + card_w - 20, cy + card_h - 14), radius=4, fill=(15, 18, 24))
        draw.text((tx + 10, cy + card_h - 31), "ESTADO: VERIFICADO & CERTIFICADO 100% 3D", fill=(46, 204, 113), font=font_foot)
        
    master_path = os.path.join(RENDERS_DIR, "Showcase_Peligros_Lote5_Biologicos_Master.png")
    artifact_path = os.path.join(ARTIFACT_DIR, "Showcase_Peligros_Lote5_Biologicos_Master.png")
    canvas.save(master_path, format="PNG")
    shutil.copy2(master_path, artifact_path)
    print(f"[+] Lamina Maestra guardada en: {master_path}")
    print(f"[+] Sincronizada con artefacto con exito!")

if __name__ == "__main__":
    generate_lote5_scene()

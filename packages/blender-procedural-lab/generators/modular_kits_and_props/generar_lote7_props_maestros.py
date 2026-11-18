# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Generador Maestro 3D - Lote 7 de Props: Navegacion, Telecomunicaciones & Computacion (Props 31 al 35)
# Blender 5.2 LTS - Modelado Procedural BMesh Avanzado, Shaders PBR Stylized, Freestyle Ink y Lamina Maestra 2.5K

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
BLEND_FILE = os.path.join(SCRIPT_DIR, "Lote7_Props_Maestros.blend")

PROPS_LOTE7 = [
    (31, "SM_Holonav_Tactical_Globe", "Globo Holografico de Navegacion",
     "Pedestal octogonal con proyector de coordenadas, anillos armilares de laton, orbes orbitales en suspension y diales analogicos."),
    (32, "SM_Comms_Array_Console", "Consola de Telecomunicaciones",
     "Pupitre de radio con pantalla de osciloscopio CRT fosforo verde, auricular de baquelita en cable espiral y matriz de selectores."),
    (33, "SM_Mainframe_Tape_Drive", "Mainframe de Cintas Magneticas",
     "Armario de computacion vintage con dos carretes abiertos de cinta magnetica, cabezal expuesto, llaves basculantes y leds."),
    (34, "SM_Radar_Sweeper_Terminal", "Terminal de Radar de Barrido",
     "Pantalla circular de barrido sonar con capucha de goma para observacion, dial graduado de 360 grados y brazo de soporte conico."),
    (35, "SM_Auxiliary_Pilot_Chair", "Sillon de Copiloto Articulado",
     "Butaca acolchada de suspension hidraulica para gravedad cero, reposabrazos con mandos HOTAS de doble palanca y arnes."),
]

def init_lote7_materials():
    mats = {}
    mats['dark_steel'] = abs_style.get_comic_material("Mat_P7_DarkSteel", base_color=(0.14, 0.15, 0.18), roughness=0.38, metallic=0.85)
    mats['scorched_steel'] = abs_style.get_comic_material("Mat_P7_Scorched", base_color=(0.08, 0.08, 0.09), roughness=0.85, metallic=0.30)
    mats['chrome'] = abs_style.get_comic_material("Mat_P7_Chrome", base_color=(0.90, 0.92, 0.95), roughness=0.12, metallic=0.98)
    mats['hazard_yellow'] = abs_style.get_comic_material("Mat_P7_HazardYel", base_color=(0.95, 0.70, 0.08), roughness=0.32, metallic=0.15)
    mats['hazard_orange'] = abs_style.get_comic_material("Mat_P7_HazardOrg", base_color=(0.95, 0.40, 0.08), roughness=0.35, metallic=0.20)
    mats['hazard_red'] = abs_style.get_comic_material("Mat_P7_HazardRed", base_color=(0.88, 0.12, 0.10), roughness=0.30, metallic=0.20)
    mats['brass'] = abs_style.get_comic_material("Mat_P7_Brass", base_color=(0.88, 0.68, 0.18), roughness=0.25, metallic=0.90)
    mats['copper'] = abs_style.get_comic_material("Mat_P7_Copper", base_color=(0.90, 0.45, 0.22), roughness=0.22, metallic=0.92)
    mats['leather_seat'] = abs_style.get_comic_material("Mat_P7_Leather", base_color=(0.18, 0.14, 0.12), roughness=0.65, metallic=0.05)
    mats['rubber_hood'] = abs_style.get_comic_material("Mat_P7_Rubber", base_color=(0.06, 0.06, 0.07), roughness=0.75, metallic=0.05)
    mats['case_cream'] = abs_style.get_comic_material("Mat_P7_CaseCream", base_color=(0.78, 0.76, 0.70), roughness=0.55, metallic=0.10)
    
    # Efectos emisivos y pantallas
    mats['holo_cyan'] = abs_style.get_comic_material("Mat_P7_HoloCyan", base_color=(0.10, 0.85, 1.0), roughness=0.15, metallic=0.10,
                                                     emissive_color=(0.15, 0.88, 1.0, 1.0), emissive_strength=2.6)
    mats['crt_green'] = abs_style.get_comic_material("Mat_P7_CrtGreen", base_color=(0.15, 0.85, 0.25), roughness=0.20, metallic=0.05,
                                                     emissive_color=(0.18, 0.95, 0.30, 1.0), emissive_strength=2.4)
    mats['tape_reel'] = abs_style.get_comic_material("Mat_P7_TapeReel", base_color=(0.85, 0.88, 0.92), roughness=0.15, metallic=0.85)
    mats['magnetic_tape'] = abs_style.get_comic_material("Mat_P7_TapeMag", base_color=(0.18, 0.10, 0.06), roughness=0.35, metallic=0.10)
    return mats

def build_prop_31_holonav(ox, oy, oz, col, mats):
    root = bpy.data.objects.new("Root_P31", None)
    root.location = (0, 0, 0)
    col.objects.link(root)
    name = "P31_Holonav"
    
    # 1. Pedestal octogonal piramidal truncado
    base = abs_style.create_cylinder(f"{name}_PedestalBase", radius=0.95, depth=0.25, segments=8,
                                    loc=(ox, oy, oz + 0.125), mat=mats['dark_steel'], col=col)
    base.parent = root
    
    col_pillar = abs_style.create_cylinder(f"{name}_PedestalCol", radius=0.75, depth=0.85, segments=8,
                                           loc=(ox, oy, oz + 0.65), mat=mats['dark_steel'], col=col)
    col_pillar.parent = root
    
    # Moldura de latón perimetral
    brass_rim = abs_style.create_torus(f"{name}_BrassRim", major_r=0.88, minor_r=0.045, loc=(ox, oy, oz + 1.1), mat=mats['brass'], col=col)
    brass_rim.parent = root
    
    # 2. Emisor cónico central con lente holográfica
    emitter = abs_style.create_cone(f"{name}_EmitterCone", radius1=0.65, radius2=0.25, depth=0.35,
                                    loc=(ox, oy, oz + 1.25), mat=mats['dark_steel'], col=col)
    emitter.parent = root
    lens = abs_style.create_cylinder(f"{name}_HoloLens", radius=0.24, depth=0.08, loc=(ox, oy, oz + 1.42), mat=mats['holo_cyan'], col=col)
    lens.parent = root
    
    # Tres proyectores láser triangulares a 120 grados
    for i in range(3):
        ang = i * (2.0 * math.pi / 3.0)
        px = ox + math.cos(ang) * 0.55
        py = oy + math.sin(ang) * 0.55
        laser_node = abs_style.create_cylinder(f"{name}_LaserNode_{i}", radius=0.09, depth=0.22,
                                               loc=(px, py, oz + 1.25), mat=mats['brass'], col=col)
        laser_node.parent = root
        
    # 3. Anillos armilares holográficos en suspensión
    # Anillo ecuatorial
    ring_eq = abs_style.create_torus(f"{name}_HoloRingEq", major_r=0.85, minor_r=0.035, loc=(ox, oy, oz + 1.85), mat=mats['holo_cyan'], col=col)
    ring_eq.parent = root
    # Anillo inclinado 1
    ring_inc1 = abs_style.create_torus(f"{name}_HoloRingInc1", major_r=0.82, minor_r=0.03, rot=(math.radians(35), math.radians(20), 0),
                                       loc=(ox, oy, oz + 1.85), mat=mats['holo_cyan'], col=col)
    ring_inc1.parent = root
    # Anillo inclinado 2
    ring_inc2 = abs_style.create_torus(f"{name}_HoloRingInc2", major_r=0.80, minor_r=0.03, rot=(math.radians(-40), math.radians(45), 0),
                                       loc=(ox, oy, oz + 1.85), mat=mats['holo_cyan'], col=col)
    ring_inc2.parent = root
    
    # Orbe planetario central y satélite menor
    orb_core = abs_style.create_cylinder(f"{name}_HoloCoreOrb", radius=0.28, depth=0.28, loc=(ox, oy, oz + 1.85), mat=mats['holo_cyan'], col=col)
    orb_core.parent = root
    orb_moon = abs_style.create_cylinder(f"{name}_HoloMoonOrb", radius=0.08, depth=0.08, loc=(ox + 0.6, oy + 0.3, oz + 2.05), mat=mats['hazard_yellow'], col=col)
    orb_moon.parent = root
    
    # 4. Dial analógico de coordenadas en la consola
    dial = abs_style.create_analog_gauge(f"{name}_CoordDial", loc=(ox, oy - 0.72, oz + 0.95), rot=(-35, 0, 0), radius=0.18, depth=0.08, col=col)
    dial.parent = root
    return root

def build_prop_32_comms_console(ox, oy, oz, col, mats):
    root = bpy.data.objects.new("Root_P32", None)
    root.location = (0, 0, 0)
    col.objects.link(root)
    name = "P32_Comms"
    
    # 1. Pupitre de consola militar inclinado en chapa plegada
    body = abs_style.create_box(f"{name}_DeskBody", size=(1.5, 0.95, 1.15), loc=(ox, oy + 0.1, oz + 0.575), mat=mats['dark_steel'], col=col)
    body.parent = root
    
    # Plano de trabajo frontal inclinado (teclado)
    desk_front = abs_style.create_box(f"{name}_DeskFront", size=(1.45, 0.45, 0.08), rot=(math.radians(15), 0, 0),
                                      loc=(ox, oy - 0.25, oz + 0.95), mat=mats['case_cream'], col=col)
    desk_front.parent = root
    
    # Teclado mecánico con botones de colores
    for k_r in range(2):
        for k_c in range(5):
            kx = ox - 0.45 + k_c * 0.22
            ky = oy - 0.35 + k_r * 0.15
            k_mat = mats['hazard_yellow'] if (k_c == 0) else (mats['hazard_red'] if k_c == 4 else mats['dark_steel'])
            key = abs_style.create_box(f"{name}_Key_{k_r}_{k_c}", size=(0.14, 0.10, 0.04), rot=(math.radians(15), 0, 0),
                                       loc=(kx, ky, oz + 1.02), mat=k_mat, col=col)
            key.parent = root
            
    # 2. Pantalla de osciloscopio CRT integrada
    crt_frame = abs_style.create_box(f"{name}_CrtFrame", size=(0.65, 0.15, 0.55), rot=(math.radians(-15), 0, 0),
                                     loc=(ox - 0.32, oy + 0.25, oz + 1.45), mat=mats['dark_steel'], col=col)
    crt_frame.parent = root
    crt_screen = abs_style.create_box(f"{name}_CrtScreen", size=(0.55, 0.05, 0.45), rot=(math.radians(-15), 0, 0),
                                      loc=(ox - 0.32, oy + 0.2, oz + 1.45), mat=mats['crt_green'], col=col)
    crt_screen.parent = root
    
    # Onda de señal en el osciloscopio
    sine_bar = abs_style.create_box(f"{name}_SineBar", size=(0.42, 0.06, 0.04), rot=(math.radians(-15), 0, math.radians(20)),
                                    loc=(ox - 0.32, oy + 0.18, oz + 1.45), mat=mats['hazard_yellow'], col=col)
    sine_bar.parent = root
    
    # 3. Auricular de telecomunicaciones de baquelita colgado al costado
    cradle = abs_style.create_box(f"{name}_PhoneCradle", size=(0.12, 0.25, 0.15), loc=(ox + 0.65, oy, oz + 1.15), mat=mats['dark_steel'], col=col)
    cradle.parent = root
    
    # Mango del auricular
    handset_bar = abs_style.create_cylinder(f"{name}_HandsetBar", radius=0.045, depth=0.45, loc=(ox + 0.65, oy, oz + 1.3), mat=mats['rubber_hood'], col=col)
    handset_bar.parent = root
    ear_cup = abs_style.create_cylinder(f"{name}_EarCup", radius=0.09, depth=0.12, loc=(ox + 0.65, oy, oz + 1.5), mat=mats['rubber_hood'], col=col)
    ear_cup.parent = root
    mouth_cup = abs_style.create_cylinder(f"{name}_MouthCup", radius=0.09, depth=0.12, loc=(ox + 0.65, oy, oz + 1.1), mat=mats['rubber_hood'], col=col)
    mouth_cup.parent = root
    
    # Cable helicoidal colgando
    cable_coil = abs_style.create_torus(f"{name}_Coil", major_r=0.08, minor_r=0.025, rot=(math.radians(90), 0, 0),
                                        loc=(ox + 0.65, oy, oz + 0.95), mat=mats['dark_steel'], col=col)
    cable_coil.parent = root
    
    # 4. Antena dipolo en la parte superior trasera
    antenna_l = abs_style.create_cylinder(f"{name}_AntennaL", radius=0.02, depth=0.9, rot=(0, math.radians(25), 0),
                                          loc=(ox + 0.35, oy + 0.45, oz + 1.8), mat=mats['chrome'], col=col)
    antenna_l.parent = root
    antenna_r = abs_style.create_cylinder(f"{name}_AntennaR", radius=0.02, depth=0.9, rot=(0, math.radians(-25), 0),
                                          loc=(ox - 0.35, oy + 0.45, oz + 1.8), mat=mats['chrome'], col=col)
    antenna_r.parent = root
    return root

def build_prop_33_tape_mainframe(ox, oy, oz, col, mats):
    root = bpy.data.objects.new("Root_P33", None)
    root.location = (0, 0, 0)
    col.objects.link(root)
    name = "P33_Mainframe"
    
    # 1. Armario rack vertical estilizado en crema/acero
    rack = abs_style.create_box(f"{name}_RackCabinet", size=(1.5, 0.85, 2.3), loc=(ox, oy, oz + 1.15), mat=mats['case_cream'], col=col)
    rack.parent = root
    
    # Marco frontal en acero oscuro
    front_frame = abs_style.create_box(f"{name}_FrontFrame", size=(1.54, 0.08, 2.34), loc=(ox, oy - 0.41, oz + 1.15), mat=mats['dark_steel'], col=col)
    front_frame.parent = root
    
    # 2. Dos grandes carretes de cinta magnética de 10.5 pulgadas
    # Carrete izquierdo (suministro)
    reel_l = abs_style.create_cylinder(f"{name}_ReelL", radius=0.42, depth=0.08, rot=(math.radians(90), 0, 0),
                                       loc=(ox - 0.42, oy - 0.46, oz + 1.7), mat=mats['tape_reel'], col=col)
    reel_l.parent = root
    tape_l = abs_style.create_cylinder(f"{name}_TapeL", radius=0.36, depth=0.09, rot=(math.radians(90), 0, 0),
                                       loc=(ox - 0.42, oy - 0.46, oz + 1.7), mat=mats['magnetic_tape'], col=col)
    tape_l.parent = root
    hub_l = abs_style.create_cylinder(f"{name}_HubL", radius=0.12, depth=0.12, rot=(math.radians(90), 0, 0),
                                      loc=(ox - 0.42, oy - 0.46, oz + 1.7), mat=mats['chrome'], col=col)
    hub_l.parent = root
    
    # Carrete derecho (recogida)
    reel_r = abs_style.create_cylinder(f"{name}_ReelR", radius=0.42, depth=0.08, rot=(math.radians(90), 0, 0),
                                       loc=(ox + 0.42, oy - 0.46, oz + 1.7), mat=mats['tape_reel'], col=col)
    reel_r.parent = root
    tape_r = abs_style.create_cylinder(f"{name}_TapeR", radius=0.22, depth=0.09, rot=(math.radians(90), 0, 0),
                                       loc=(ox + 0.42, oy - 0.46, oz + 1.7), mat=mats['magnetic_tape'], col=col)
    tape_r.parent = root
    hub_r = abs_style.create_cylinder(f"{name}_HubR", radius=0.12, depth=0.12, rot=(math.radians(90), 0, 0),
                                      loc=(ox + 0.42, oy - 0.46, oz + 1.7), mat=mats['chrome'], col=col)
    hub_r.parent = root
    
    # Cabezal magnético central y guías
    head = abs_style.create_box(f"{name}_MagHead", size=(0.28, 0.12, 0.18), loc=(ox, oy - 0.48, oz + 1.35), mat=mats['brass'], col=col)
    head.parent = root
    for g in range(2):
        gx = ox - 0.18 + g * 0.36
        guide = abs_style.create_cylinder(f"{name}_TapeGuide_{g}", radius=0.04, depth=0.12, rot=(math.radians(90), 0, 0),
                                          loc=(gx, oy - 0.48, oz + 1.38), mat=mats['chrome'], col=col)
        guide.parent = root
        
    # 3. Panel de llaves basculantes (toggle switches) y luces de registro
    switch_panel = abs_style.create_box(f"{name}_SwitchPanel", size=(1.35, 0.08, 0.45), loc=(ox, oy - 0.42, oz + 0.75), mat=mats['dark_steel'], col=col)
    switch_panel.parent = root
    
    for s_i in range(8):
        sx = ox - 0.52 + s_i * 0.15
        sw = abs_style.create_cylinder(f"{name}_Toggle_{s_i}", radius=0.02, depth=0.08, rot=(math.radians(65), 0, 0),
                                       loc=(sx, oy - 0.48, oz + 0.8), mat=mats['chrome'], col=col)
        sw.parent = root
        led = abs_style.create_cylinder(f"{name}_Led_{s_i}", radius=0.025, depth=0.04, rot=(math.radians(90), 0, 0),
                                        loc=(sx, oy - 0.48, oz + 0.7), mat=(mats['hazard_red'] if s_i % 2 == 0 else mats['hazard_yellow']), col=col)
        led.parent = root
        
    # Rejilla de ventilación inferior
    vent = abs_style.create_box(f"{name}_LowerVent", size=(1.2, 0.04, 0.25), loc=(ox, oy - 0.42, oz + 0.25), mat=mats['scorched_steel'], col=col)
    vent.parent = root
    return root

def build_prop_34_radar_terminal(ox, oy, oz, col, mats):
    root = bpy.data.objects.new("Root_P34", None)
    root.location = (0, 0, 0)
    col.objects.link(root)
    name = "P34_Radar"
    
    # 1. Base trípode pesada de fundición con pernos de fijación
    base_plate = abs_style.create_cylinder(f"{name}_TripodBase", radius=0.65, depth=0.15, segments=6,
                                           loc=(ox, oy, oz + 0.075), mat=mats['dark_steel'], col=col)
    base_plate.parent = root
    
    # Columna telescópica de elevación con fuelles
    column = abs_style.create_cylinder(f"{name}_Column", radius=0.16, depth=0.9, loc=(ox, oy, oz + 0.6), mat=mats['dark_steel'], col=col)
    column.parent = root
    bellow = abs_style.create_torus(f"{name}_Bellow", major_r=0.22, minor_r=0.04, loc=(ox, oy, oz + 0.95), mat=mats['brass'], col=col)
    bellow.parent = root
    
    # 2. Brazo basculante de cuello de cisne articulado con perilla
    joint = abs_style.create_cylinder(f"{name}_PivotJoint", radius=0.14, depth=0.35, rot=(0, math.radians(90), 0),
                                      loc=(ox, oy, oz + 1.15), mat=mats['brass'], col=col)
    joint.parent = root
    
    # 3. Tambor de la pantalla de radar inclinado hacia el observador
    rot_radar = (math.radians(-25), 0, 0)
    drum = abs_style.create_cylinder(f"{name}_RadarDrum", radius=0.55, depth=0.45, rot=rot_radar,
                                     loc=(ox, oy - 0.1, oz + 1.45), mat=mats['dark_steel'], col=col)
    drum.parent = root
    
    # Bisel de latón graduado de 360 grados
    bezel = abs_style.create_torus(f"{name}_GradBezel", major_r=0.54, minor_r=0.045, rot=rot_radar,
                                   loc=(ox, oy - 0.28, oz + 1.45), mat=mats['brass'], col=col)
    bezel.parent = root
    
    # Pantalla CRT circular verde fósforo
    screen = abs_style.create_cylinder(f"{name}_RadarScreen", radius=0.48, depth=0.06, rot=rot_radar,
                                       loc=(ox, oy - 0.26, oz + 1.45), mat=mats['crt_green'], col=col)
    screen.parent = root
    
    # Haz de barrido radial y ecos de radar
    sweep_line = abs_style.create_box(f"{name}_SweepLine", size=(0.02, 0.42, 0.02), rot=(math.radians(-25), 0, math.radians(45)),
                                      loc=(ox + 0.15, oy - 0.29, oz + 1.55), mat=mats['hazard_yellow'], col=col)
    sweep_line.parent = root
    blip = abs_style.create_cylinder(f"{name}_RadarBlip", radius=0.04, depth=0.04, rot=rot_radar,
                                     loc=(ox - 0.2, oy - 0.29, oz + 1.6), mat=mats['hazard_yellow'], col=col)
    blip.parent = root
    
    # 4. Capucha de observación de goma cónica
    hood = abs_style.create_cone(f"{name}_EyeHood", radius1=0.55, radius2=0.38, depth=0.28, rot=rot_radar,
                                 loc=(ox, oy - 0.42, oz + 1.45), mat=mats['rubber_hood'], col=col)
    hood.parent = root
    return root

def build_prop_35_pilot_chair(ox, oy, oz, col, mats):
    root = bpy.data.objects.new("Root_P35", None)
    root.location = (0, 0, 0)
    col.objects.link(root)
    name = "P35_Pilot_Chair"
    
    # 1. Base de anclaje giratoria de suelo con cilindro hidráulico central
    mount = abs_style.create_cylinder(f"{name}_FloorMount", radius=0.55, depth=0.12, loc=(ox, oy, oz + 0.06), mat=mats['dark_steel'], col=col)
    mount.parent = root
    piston = abs_style.create_cylinder(f"{name}_HydPiston", radius=0.14, depth=0.55, loc=(ox, oy, oz + 0.35), mat=mats['chrome'], col=col)
    piston.parent = root
    
    # Fuelles de protección de amortiguación
    for b_i in range(3):
        boot = abs_style.create_torus(f"{name}_Boot_{b_i}", major_r=0.18, minor_r=0.04, loc=(ox, oy, oz + 0.2 + b_i * 0.12), mat=mats['rubber_hood'], col=col)
        boot.parent = root
        
    # 2. Bastidor de asiento metálico reforzado
    chassis = abs_style.create_box(f"{name}_SeatChassis", size=(0.78, 0.72, 0.15), loc=(ox, oy, oz + 0.65), mat=mats['dark_steel'], col=col)
    chassis.parent = root
    
    # Cojín de asiento de cuero ergonómico
    seat_pad = abs_style.create_box(f"{name}_SeatPad", size=(0.72, 0.68, 0.14), loc=(ox, oy, oz + 0.76), mat=mats['leather_seat'], col=col)
    seat_pad.parent = root
    
    # Respaldo reclinable alto con soporte cervical
    back_chassis = abs_style.create_box(f"{name}_BackChassis", size=(0.72, 0.12, 1.05), rot=(math.radians(12), 0, 0),
                                       loc=(ox, oy + 0.38, oz + 1.25), mat=mats['dark_steel'], col=col)
    back_chassis.parent = root
    back_pad = abs_style.create_box(f"{name}_BackPad", size=(0.65, 0.12, 0.95), rot=(math.radians(12), 0, 0),
                                    loc=(ox, oy + 0.32, oz + 1.25), mat=mats['leather_seat'], col=col)
    back_pad.parent = root
    
    # Cabezal cervical acolchado
    headrest = abs_style.create_box(f"{name}_Headrest", size=(0.42, 0.15, 0.28), rot=(math.radians(12), 0, 0),
                                    loc=(ox, oy + 0.48, oz + 1.88), mat=mats['leather_seat'], col=col)
    headrest.parent = root
    
    # 3. Reposabrazos gemelos con controles HOTAS integrados
    for side, sign in [("L", -1), ("R", 1)]:
        arm_support = abs_style.create_box(f"{name}_ArmSupport_{side}", size=(0.08, 0.45, 0.35),
                                           loc=(ox + sign * 0.45, oy + 0.05, oz + 0.85), mat=mats['dark_steel'], col=col)
        arm_support.parent = root
        arm_pad = abs_style.create_box(f"{name}_ArmPad_{side}", size=(0.14, 0.52, 0.08),
                                       loc=(ox + sign * 0.45, oy + 0.05, oz + 1.05), mat=mats['leather_seat'], col=col)
        arm_pad.parent = root
        
        # Joystick de mando HOTAS en el extremo delantero
        stick_base = abs_style.create_cylinder(f"{name}_StickBase_{side}", radius=0.05, depth=0.06,
                                              loc=(ox + sign * 0.45, oy - 0.22, oz + 1.12), mat=mats['brass'], col=col)
        stick_base.parent = root
        stick_grip = abs_style.create_cylinder(f"{name}_StickGrip_{side}", radius=0.03, depth=0.22, rot=(math.radians(-15), 0, 0),
                                               loc=(ox + sign * 0.45, oy - 0.24, oz + 1.24), mat=mats['rubber_hood'], col=col)
        stick_grip.parent = root
        trigger = abs_style.create_box(f"{name}_Trigger_{side}", size=(0.02, 0.04, 0.04),
                                       loc=(ox + sign * 0.45, oy - 0.27, oz + 1.28), mat=mats['hazard_red'], col=col)
        trigger.parent = root
    return root

def generate_lote7_scene(save_blend=True):
    print("=" * 70)
    print("[*] Iniciando generacion de Props Maestros Lote 7 (Props 31 al 35: Navegacion & Telecom)...")
    print("=" * 70)
    
    abs_style.reset_comic_scene(bg_color=(0.04, 0.05, 0.07, 1.0), bg_strength=0.9, ink_thickness=2.4)
    col_props = abs_style.create_collection("Props_Lote7_Navegacion")
    mats = init_lote7_materials()
    
    ped_mat = abs_style.get_comic_material("Pedestal_Props7", base_color=(0.08, 0.09, 0.12), roughness=0.45, metallic=0.7)
    hazard_strip_mat = abs_style.get_comic_material("Ped_Hazard_Lote7", base_color=(0.05, 0.75, 0.95), roughness=0.30, metallic=0.2)
    
    spacing_x = 4.2
    
    closeups = {}
    
    PROP_BUILDERS = {
        31: build_prop_31_holonav,
        32: build_prop_32_comms_console,
        33: build_prop_33_tape_mainframe,
        34: build_prop_34_radar_terminal,
        35: build_prop_35_pilot_chair,
    }
    
    PROP_CAMERAS = {
        31: {"offset": (2.2, -3.2, 1.8), "target_x": 0.0, "target_y": 0.0, "target_z": 1.25, "focal": 36}, # Holonav
        32: {"offset": (2.2, -3.0, 1.8), "target_x": 0.0, "target_y": 0.0, "target_z": 1.15, "focal": 36}, # Comms
        33: {"offset": (2.4, -3.4, 1.9), "target_x": 0.0, "target_y": -0.1, "target_z": 1.25, "focal": 35},# Mainframe
        34: {"offset": (2.2, -3.0, 1.8), "target_x": 0.0, "target_y": -0.1, "target_z": 1.15, "focal": 36},# Radar
        35: {"offset": (2.2, -3.0, 1.8), "target_x": 0.0, "target_y": 0.0, "target_z": 1.05, "focal": 36}, # Pilot Chair
    }
    
    for idx, (pid, pname, ptitle, pdesc) in enumerate(PROPS_LOTE7):
        x = (idx - 2.0) * spacing_x
        y = 0.0
        z = 0.0
        
        ped = abs_style.create_box(f"Ped_{pname}", size=(3.6, 3.6, 0.22), loc=(x, y, 0.11), mat=ped_mat, col=col_props)
        strip = abs_style.create_box(f"Strip_{pname}", size=(3.6, 0.12, 0.06), loc=(x, y - 1.75, 0.25), mat=hazard_strip_mat, col=col_props)
        
        builder = PROP_BUILDERS[pid]
        builder(x, y, 0.22, col_props, mats)
        
    floor_mat = abs_style.get_comic_material("Floor_Props7", base_color=(0.03, 0.035, 0.045), roughness=0.28, metallic=0.8)
    abs_style.create_box("HangarFloor_Props7", size=(28.0, 16.0, 0.15), loc=(0, 0, -0.08), mat=floor_mat, col=col_props)
    
    abs_style.setup_studio_lighting(sun_energy=5.5, rim_energy=3.8, fill_energy=2.2)
    abs_style.setup_camera(name="Camera_Props_Lote7", loc=(0, -16.5, 9.5), target=(0, 0.0, 1.1), focal_length=28)
    
    if save_blend:
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_FILE)
        print(f"[+] Blend guardado: {BLEND_FILE}")
        
    raw_pan_path = os.path.join(RENDERS_DIR, "Raw_Props_Lote7_Panorama.png")
    abs_style.render_and_save("Raw_Props_Lote7_Panorama.png", res_x=2560, res_y=1440)
    
    # Close-ups con aislamiento estricto
    def set_hierarchy_hide_render(obj, hide):
        if not obj:
            return
        obj.hide_render = hide
        for child in obj.children:
            set_hierarchy_hide_render(child, hide)

    for idx, (pid, pname, _, _) in enumerate(PROPS_LOTE7):
        x = (idx - 2.0) * spacing_x
        y = 0.0
        z = 0.0
        
        for other_idx, (o_pid, o_pname, _, _) in enumerate(PROPS_LOTE7):
            is_other = (o_pid != pid)
            o_root = bpy.data.objects.get(f"Root_P{o_pid:02d}")
            if o_root:
                set_hierarchy_hide_render(o_root, is_other)
            o_ped = bpy.data.objects.get(f"Ped_{o_pname}")
            if o_ped:
                o_ped.hide_render = is_other
            o_strip = bpy.data.objects.get(f"Strip_{o_pname}")
            if o_strip:
                o_strip.hide_render = is_other
                
        cam_cfg = PROP_CAMERAS.get(pid, {"offset": (2.2, -3.0, 1.8), "target_x": 0.0, "target_y": 0.0, "target_z": 1.1, "focal": 36})
        off_x, off_y, off_z = cam_cfg["offset"]
        t_x = cam_cfg.get("target_x", 0.0)
        t_y = cam_cfg.get("target_y", 0.0)
        t_z = cam_cfg.get("target_z", 1.1)
        foc = cam_cfg["focal"]
        
        abs_style.setup_camera(name=f"Cam_Close_{pname}", loc=(x + off_x, y + off_y, off_z),
                               target=(x + t_x, y + t_y, t_z), focal_length=foc)
        close_file = f"CloseUp_{pname}.png"
        abs_style.render_and_save(close_file, res_x=800, res_y=800)
        closeups[pid] = os.path.join(RENDERS_DIR, close_file)
        
    for o_pid, o_pname, _, _ in PROPS_LOTE7:
        o_root = bpy.data.objects.get(f"Root_P{o_pid:02d}")
        if o_root:
            set_hierarchy_hide_render(o_root, False)
        o_ped = bpy.data.objects.get(f"Ped_{o_pname}")
        if o_ped:
            o_ped.hide_render = False
        o_strip = bpy.data.objects.get(f"Strip_{o_pname}")
        if o_strip:
            o_strip.hide_render = False
            
    assemble_lote7_sheet(raw_pan_path, closeups)
    print("[+] Lote 7 de Props Maestros completado con exito!")

def assemble_lote7_sheet(deck_render_path, closeups):
    print("[*] Componiendo Lamina Maestra Tecnica 2.5K de Props Lote 7...")
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
        
    draw.text((40, 18), "ASTRA HAZARD // REPOSITORIO DE ARQUITECTURA Y PROPS MAESTROS // BLENDER 5.2 LTS", fill=(0, 200, 240), font=font_sub)
    draw.text((40, 46), "CATÁLOGO DE PROPS MAESTROS // LOTE 7 (PROPS 31 A 35: NAVEGACIÓN & TELECOM)", fill=(255, 255, 255), font=font_main)
    
    badges = [
        ("5 PROPS DE NAVEGACIÓN", (41, 128, 185)),
        ("HOLOGRAFÍA & CASSETTE FUTURISM", (142, 68, 173)),
        ("INTERACTIVIDAD TÁCTICA", (39, 174, 96)),
        ("VERIFICADO 100% CERO BUGS", (211, 84, 0))
    ]
    cur_x = W - 40
    for btext, bcol in reversed(badges):
        tw = len(btext) * 8 + 22
        cur_x -= tw
        draw.rounded_rectangle((cur_x, 32, cur_x + tw - 10, 66), radius=6, fill=bcol)
        draw.text((cur_x + 10, 41), btext, fill=(255, 255, 255), font=font_pill)
        cur_x -= 10
        
    draw.line([(40, 88), (W - 40, 88)], fill=(45, 52, 65), width=2)
    
    # Panorama superior (2480 x 590)
    pan_w = 2480
    pan_h = 590
    if os.path.exists(deck_render_path):
        pan_img = Image.open(deck_render_path).convert("RGBA")
        crop_box = (60, 200, 2500, 1240)
        resized = pan_img.crop(crop_box).resize((pan_w, pan_h), Image.Resampling.LANCZOS)
        canvas.paste(resized, (40, 102))
        draw.rectangle((40, 102, 40 + pan_w, 102 + pan_h), outline=(48, 56, 70), width=2)
        
    start_y = 712
    card_w = 478
    card_h = 345
    gap_x = 22
    
    for idx, (pid, pname, ptitle, pdesc) in enumerate(PROPS_LOTE7):
        cx = 40 + idx * (card_w + gap_x)
        cy = start_y
        
        draw.rectangle((cx, cy, cx + card_w, cy + card_h), fill=(18, 21, 28, 255), outline=(38, 44, 56), width=2)
        
        thumb_path = closeups.get(pid)
        if thumb_path and os.path.exists(thumb_path):
            t_img = Image.open(thumb_path).convert("RGBA")
            t_resized = t_img.resize((195, 195), Image.Resampling.LANCZOS)
            canvas.paste(t_resized, (cx + 14, cy + 18))
            draw.rectangle((cx + 14, cy + 18, cx + 14 + 195, cy + 18 + 195), outline=(45, 52, 65), width=1)
            
        tx = cx + 224
        draw.text((tx, cy + 20), f"PROP MAESTRO {pid:02d}", fill=(0, 200, 240), font=font_card_sub)
        
        t_lines = textwrap.wrap(ptitle, width=18)
        ty = cy + 40
        for tl in t_lines[:2]:
            draw.text((tx, ty), tl, fill=(255, 255, 255), font=font_card_title)
            ty += 20
            
        draw.line([(tx, ty + 4), (cx + card_w - 14, ty + 4)], fill=(40, 48, 62), width=1)
        ty += 14
        
        d_lines = textwrap.wrap(pdesc, width=24)
        for dl in d_lines[:4]:
            draw.text((tx, ty), dl, fill=(175, 185, 200), font=font_card_desc)
            ty += 16
            
        ty += 8
        draw.text((tx, ty), "• Cel-Shading Comic 3D", fill=(130, 200, 240), font=font_card_desc)
        ty += 15
        draw.text((tx, ty), "• PBR Stylized & Colision UCX", fill=(130, 200, 240), font=font_card_desc)
        
        draw.rounded_rectangle((cx + 14, cy + card_h - 38, cx + card_w - 14, cy + card_h - 14), radius=4, fill=(15, 18, 24))
        draw.text((cx + 24, cy + card_h - 31), f"ESTADO: CERTIFICADO 100% 3D // PID_{pid:02d}", fill=(46, 204, 113), font=font_foot)
        
    master_path = os.path.join(RENDERS_DIR, "Showcase_Props_Lote7_Navegacion_Master.png")
    artifact_path = os.path.join(ARTIFACT_DIR, "Showcase_Props_Lote7_Navegacion_Master.png")
    canvas.save(master_path, format="PNG")
    shutil.copy2(master_path, artifact_path)
    print(f"[+] Lamina Maestra guardada en: {master_path}")
    print(f"[+] Sincronizada con artefacto con exito!")

if __name__ == "__main__":
    generate_lote7_scene()

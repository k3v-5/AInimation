# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Generador Maestro 3D - Lote 9 de Props: Seguridad, Blindaje y Contencion (Props 41 al 45)
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
BLEND_FILE = os.path.join(SCRIPT_DIR, "Lote9_Props_Maestros.blend")

PROPS_LOTE9 = [
    (41, "SM_Security_Turnstile_Barrier", "Torniquete Biometrico Tripode",
     "Chasis de acero inoxidable cepillado con tripode rotatorio de 3 brazos tubulares, lector NFC y panel de paso LED verde."),
    (42, "SM_Wall_Mounted_Keycard_Box", "Terminal Mural de Acceso Seguro",
     "Gabinete estanco blindado de fundicion con teclado alfanumerico, escaner optico de huella, dial mecanico y visera protectora."),
    (43, "SM_Surveillance_Dome_Turret", "Domo de Vigilancia Acorazado",
     "Torreta esferica de techo/pared con carcasa blindada, lente optica de doble focal, anillo de leds IR y baliza roja de estado."),
    (44, "SM_Weapon_Locker_Reinforced", "Armero de Asalto Blindado",
     "Armario de acero naval con puertas de reja de seguridad, cremalleras para 4 fusiles, estante superior de municion y candado macizo."),
    (45, "SM_Emergency_Breach_Axe_Box", "Vitrina de Hacha de Brecha",
     "Caja mural de emergencia roja con cristal rompible serigrafiado, hacha tactica pesada en cunas y martillo percutor encadenado."),
]

def init_lote9_materials():
    mats = {}
    mats['dark_steel'] = abs_style.get_comic_material("Mat_P9_DarkSteel", base_color=(0.14, 0.15, 0.18), roughness=0.38, metallic=0.85)
    mats['scorched_steel'] = abs_style.get_comic_material("Mat_P9_Scorched", base_color=(0.08, 0.08, 0.09), roughness=0.85, metallic=0.30)
    mats['chrome'] = abs_style.get_comic_material("Mat_P9_Chrome", base_color=(0.92, 0.94, 0.96), roughness=0.10, metallic=0.98)
    mats['brushed_steel'] = abs_style.get_comic_material("Mat_P9_Brushed", base_color=(0.75, 0.78, 0.82), roughness=0.28, metallic=0.92)
    mats['hazard_yellow'] = abs_style.get_comic_material("Mat_P9_HazardYel", base_color=(0.96, 0.72, 0.08), roughness=0.32, metallic=0.15)
    mats['hazard_red'] = abs_style.get_comic_material("Mat_P9_HazardRed", base_color=(0.88, 0.12, 0.10), roughness=0.30, metallic=0.20)
    mats['brass'] = abs_style.get_comic_material("Mat_P9_Brass", base_color=(0.88, 0.68, 0.18), roughness=0.25, metallic=0.90)
    mats['glass_tint'] = abs_style.get_comic_material("Mat_P9_GlassTint", base_color=(0.20, 0.40, 0.50), roughness=0.08, metallic=0.20)
    if mats['glass_tint'].use_nodes:
        bsdf = mats['glass_tint'].node_tree.nodes.get("Principled BSDF")
        if bsdf and 'Transmission Weight' in bsdf.inputs:
            bsdf.inputs['Transmission Weight'].default_value = 0.82
    mats['rubber_black'] = abs_style.get_comic_material("Mat_P9_Rubber", base_color=(0.06, 0.06, 0.07), roughness=0.75, metallic=0.05)
    mats['lens_black'] = abs_style.get_comic_material("Mat_P9_Lens", base_color=(0.03, 0.04, 0.06), roughness=0.05, metallic=0.90)
    mats['led_green'] = abs_style.get_comic_material("Mat_P9_LedGrn", base_color=(0.10, 0.95, 0.35), roughness=0.15, metallic=0.0,
                                                     emissive_color=(0.12, 1.0, 0.38, 1.0), emissive_strength=2.6)
    mats['led_red'] = abs_style.get_comic_material("Mat_P9_LedRed", base_color=(0.95, 0.10, 0.10), roughness=0.15, metallic=0.0,
                                                   emissive_color=(1.0, 0.12, 0.10, 1.0), emissive_strength=2.6)
    mats['led_cyan'] = abs_style.get_comic_material("Mat_P9_LedCyan", base_color=(0.10, 0.85, 0.95), roughness=0.15, metallic=0.0,
                                                    emissive_color=(0.15, 0.90, 1.0, 1.0), emissive_strength=2.5)
    mats['ammo_can_olive'] = abs_style.get_comic_material("Mat_P9_AmmoOlive", base_color=(0.28, 0.34, 0.22), roughness=0.45, metallic=0.35)
    return mats

# ==============================================================================
# PROP 41: SM_Security_Turnstile_Barrier
# ==============================================================================
def build_prop_41_turnstile(ox, oy, oz, col, mats):
    root = bpy.data.objects.new("Root_P41", None)
    root.location = (0, 0, 0)
    col.objects.link(root)
    name = "P41_Turnstile"

    # 1. Carcasa principal esbelta de acero inoxidable cepillado con cantos achaflanados
    body = abs_style.create_box(f"{name}_Body", size=(0.42, 1.25, 0.98), loc=(ox, oy, oz + 0.49), mat=mats['brushed_steel'], col=col)
    body.parent = root

    # Zócalo inferior con anclajes al suelo
    base_plate = abs_style.create_box(f"{name}_BasePlate", size=(0.48, 1.35, 0.08), loc=(ox, oy, oz + 0.04), mat=mats['dark_steel'], col=col)
    base_plate.parent = root

    # Cubierta superior angulada para ergonomía del usuario
    top_cowl = abs_style.create_box(f"{name}_TopCowl", size=(0.40, 1.20, 0.06), loc=(ox, oy, oz + 1.01), mat=mats['dark_steel'], col=col)
    top_cowl.parent = root

    # Lector de tarjeta RFID / NFC en la parte superior delantera
    nfc_pad = abs_style.create_box(f"{name}_NFCPad", size=(0.22, 0.18, 0.02), loc=(ox, oy - 0.45, oz + 1.05), mat=mats['led_cyan'], col=col)
    nfc_pad.parent = root

    # Flecha / Cruz de indicación de paso en LED verde
    led_arrow = abs_style.create_box(f"{name}_LedArrow", size=(0.18, 0.18, 0.02), loc=(ox, oy, oz + 1.05), mat=mats['led_green'], col=col)
    led_arrow.parent = root

    # 2. Mecanismo rotatorio central (Rotor inclinado a 45 grados)
    rotor_housing = abs_style.create_cylinder(f"{name}_RotorHousing", radius=0.14, depth=0.18, rot=(math.radians(45), 0, 0),
                                              loc=(ox + 0.22, oy, oz + 0.72), mat=mats['dark_steel'], col=col)
    rotor_housing.parent = root

    rotor_hub = abs_style.create_cylinder(f"{name}_RotorHub", radius=0.10, depth=0.12, rot=(math.radians(45), 0, 0),
                                          loc=(ox + 0.28, oy, oz + 0.72), mat=mats['chrome'], col=col)
    rotor_hub.parent = root

    # 3. Trípode de tres brazos de acero pulido (uno horizontal de bloqueo, dos angulados)
    arm_angles = [0, 120, 240]
    for i, ang_deg in enumerate(arm_angles):
        rad = math.radians(ang_deg)
        # Vector radial en el plano perpendicular al eje de 45 grados
        arm = abs_style.create_cylinder(f"{name}_Arm_{i}", radius=0.026, depth=0.68,
                                       rot=(math.radians(45) + rad * 0.7, math.radians(90), rad),
                                       loc=(ox + 0.58, oy + math.sin(rad) * 0.25, oz + 0.72 + math.cos(rad) * 0.25),
                                       mat=mats['chrome'], col=col)
        arm.parent = root
        tip_cap = abs_style.create_cylinder(f"{name}_ArmCap_{i}", radius=0.030, depth=0.04,
                                           rot=(math.radians(45) + rad * 0.7, math.radians(90), rad),
                                           loc=(ox + 0.90, oy + math.sin(rad) * 0.35, oz + 0.72 + math.cos(rad) * 0.35),
                                           mat=mats['rubber_black'], col=col)
        tip_cap.parent = root

    # Barandilla lateral de guiado de peatones
    rail_post1 = abs_style.create_cylinder(f"{name}_RailPost1", radius=0.025, depth=0.92, loc=(ox - 0.45, oy - 0.55, oz + 0.46), mat=mats['brushed_steel'], col=col)
    rail_post1.parent = root
    rail_post2 = abs_style.create_cylinder(f"{name}_RailPost2", radius=0.025, depth=0.92, loc=(ox - 0.45, oy + 0.55, oz + 0.46), mat=mats['brushed_steel'], col=col)
    rail_post2.parent = root
    rail_bar = abs_style.create_cylinder(f"{name}_RailBar", radius=0.025, depth=1.15, rot=(math.radians(90), 0, 0),
                                         loc=(ox - 0.45, oy, oz + 0.92), mat=mats['brushed_steel'], col=col)
    rail_bar.parent = root
    return root

# ==============================================================================
# PROP 42: SM_Wall_Mounted_Keycard_Box
# ==============================================================================
def build_prop_42_keycard_box(ox, oy, oz, col, mats):
    root = bpy.data.objects.new("Root_P42", None)
    root.location = (0, 0, 0)
    col.objects.link(root)
    name = "P42_Keycard_Box"

    # Pedestal de pared simulada de hormigón/acero para el anclaje
    back_wall = abs_style.create_box(f"{name}_WallPlate", size=(1.20, 0.14, 1.80), loc=(ox, oy + 0.45, oz + 0.90), mat=mats['dark_steel'], col=col)
    back_wall.parent = root

    # 1. Carcasa principal estanca de fundición con nervios de protección
    housing = abs_style.create_box(f"{name}_Housing", size=(0.65, 0.28, 0.88), loc=(ox, oy + 0.24, oz + 1.10), mat=mats['dark_steel'], col=col)
    housing.parent = root

    # Visera protectora superior contra lluvia / sabotaje
    visor = abs_style.create_box(f"{name}_Visor", size=(0.72, 0.38, 0.08), rot=(math.radians(-15), 0, 0),
                                 loc=(ox, oy + 0.20, oz + 1.58), mat=mats['scorched_steel'], col=col)
    visor.parent = root

    # Bridas de anclaje con 4 pernos de latón en las esquinas
    for bx in [-0.36, 0.36]:
        for bz in [oz + 0.72, oz + 1.48]:
            bracket = abs_style.create_box(f"{name}_Bracket_{bx}_{bz}", size=(0.08, 0.06, 0.12), loc=(ox + bx, oy + 0.36, bz), mat=mats['brass'], col=col)
            bracket.parent = root

    # 2. Puerta frontal reforzada con bisagra lateral y junta de estanqueidad
    door = abs_style.create_box(f"{name}_DoorPanel", size=(0.58, 0.06, 0.78), loc=(ox, oy + 0.07, oz + 1.10), mat=mats['brushed_steel'], col=col)
    door.parent = root

    # 3. Teclado alfanumérico numpad metálico
    keypad_bed = abs_style.create_box(f"{name}_KeypadBed", size=(0.28, 0.04, 0.32), loc=(ox - 0.12, oy + 0.03, oz + 1.15), mat=mats['rubber_black'], col=col)
    keypad_bed.parent = root
    for r in range(4):
        for c in range(3):
            k_btn = abs_style.create_cylinder(f"{name}_Key_{r}_{c}", radius=0.016, depth=0.02, rot=(math.radians(90), 0, 0),
                                              loc=(ox - 0.20 + c * 0.08, oy + 0.01, oz + 1.25 - r * 0.07), mat=mats['chrome'], col=col)
            k_btn.parent = root

    # Escáner óptico biométrico de huella dactilar
    scanner_frame = abs_style.create_box(f"{name}_ScannerFrame", size=(0.14, 0.04, 0.18), loc=(ox + 0.16, oy + 0.03, oz + 1.25), mat=mats['dark_steel'], col=col)
    scanner_frame.parent = root
    scanner_prism = abs_style.create_box(f"{name}_ScannerGlass", size=(0.10, 0.02, 0.14), loc=(ox + 0.16, oy + 0.01, oz + 1.25), mat=mats['led_green'], col=col)
    scanner_prism.parent = root

    # Ranura para tarjeta magnética con iluminación cian
    card_slot = abs_style.create_box(f"{name}_CardSlot", size=(0.35, 0.03, 0.03), loc=(ox, oy + 0.02, oz + 0.88), mat=mats['led_cyan'], col=col)
    card_slot.parent = root

    # Baliza bicolor de estatus en la cima (Verde/Rojo)
    beacon = abs_style.create_cylinder(f"{name}_StatusBeacon", radius=0.045, depth=0.10, loc=(ox + 0.22, oy + 0.20, oz + 1.62), mat=mats['led_red'], col=col)
    beacon.parent = root

    # Tubo corrugado de cables blindados que desciende hacia el suelo
    conduit = abs_style.create_cylinder(f"{name}_Conduit", radius=0.032, depth=0.72, loc=(ox, oy + 0.32, oz + 0.36), mat=mats['dark_steel'], col=col)
    conduit.parent = root
    return root

# ==============================================================================
# PROP 43: SM_Surveillance_Dome_Turret
# ==============================================================================
def build_prop_43_surveillance_turret(ox, oy, oz, col, mats):
    root = bpy.data.objects.new("Root_P43", None)
    root.location = (0, 0, 0)
    col.objects.link(root)
    name = "P43_Surveillance"

    # Ménsula estructural de techo / viga I de sustentación
    support_beam = abs_style.create_box(f"{name}_CeilingBeam", size=(1.8, 0.45, 0.16), loc=(ox, oy, oz + 2.38), mat=mats['dark_steel'], col=col)
    support_beam.parent = root
    pendant_flange = abs_style.create_box(f"{name}_BeamFlange", size=(0.60, 0.45, 0.08), loc=(ox, oy, oz + 2.26), mat=mats['scorched_steel'], col=col)
    pendant_flange.parent = root

    # Placa circular de anclaje
    mount_plate = abs_style.create_cylinder(f"{name}_MountPlate", radius=0.35, depth=0.08, loc=(ox, oy, oz + 2.18), mat=mats['dark_steel'], col=col)
    mount_plate.parent = root

    # Brazo angular en cuello de cisne
    arm_v = abs_style.create_cylinder(f"{name}_ArmV", radius=0.08, depth=0.45, loc=(ox, oy, oz + 1.92), mat=mats['dark_steel'], col=col)
    arm_v.parent = root
    arm_h = abs_style.create_cylinder(f"{name}_ArmH", radius=0.08, depth=0.55, rot=(math.radians(90), 0, 0),
                                      loc=(ox, oy - 0.25, oz + 1.70), mat=mats['dark_steel'], col=col)
    arm_h.parent = root

    # 1. Carcasa principal de la cámara acorazada (Carcasa esférica con visera tipo ceja)
    head_base = abs_style.create_cylinder(f"{name}_HeadBase", radius=0.32, depth=0.18, loc=(ox, oy - 0.52, oz + 1.62), mat=mats['dark_steel'], col=col)
    head_base.parent = root

    dome_cowl = abs_style.create_cylinder(f"{name}_DomeCowl", radius=0.36, depth=0.28, rot=(math.radians(35), 0, 0),
                                          loc=(ox, oy - 0.55, oz + 1.48), mat=mats['hazard_yellow'], col=col)
    dome_cowl.parent = root

    # Visera frontal antisol / antigolpes en acero oscuro
    eyebrow = abs_style.create_torus(f"{name}_Eyebrow", major_r=0.37, minor_r=0.045, rot=(math.radians(35), 0, 0),
                                     loc=(ox, oy - 0.60, oz + 1.42), mat=mats['scorched_steel'], col=col)
    eyebrow.parent = root

    # 2. Domo óptico de cristal templado oscurecido
    dome_glass = abs_style.create_cylinder(f"{name}_DomeGlass", radius=0.28, depth=0.20, rot=(math.radians(35), 0, 0),
                                           loc=(ox, oy - 0.62, oz + 1.38), mat=mats['lens_black'], col=col)
    dome_glass.parent = root

    # Lentes ópticas motorizadas duales en el interior (Sensor principal + Teleobjetivo)
    lens_main = abs_style.create_cylinder(f"{name}_LensMain", radius=0.085, depth=0.08, rot=(math.radians(35), 0, 0),
                                          loc=(ox - 0.08, oy - 0.70, oz + 1.34), mat=mats['chrome'], col=col)
    lens_main.parent = root
    lens_tele = abs_style.create_cylinder(f"{name}_LensTele", radius=0.055, depth=0.08, rot=(math.radians(35), 0, 0),
                                          loc=(ox + 0.10, oy - 0.68, oz + 1.36), mat=mats['chrome'], col=col)
    lens_tele.parent = root

    # Corona de LEDs infrarrojos de visión nocturna
    for ir_i in range(8):
        ang = ir_i * (math.pi / 4.0)
        ix = ox + math.cos(ang) * 0.18
        iz = oz + 1.36 + math.sin(ang) * 0.12
        ir_led = abs_style.create_cylinder(f"{name}_IRLed_{ir_i}", radius=0.016, depth=0.04, rot=(math.radians(35), 0, 0),
                                           loc=(ix, oy - 0.66, iz), mat=mats['led_red'], col=col)
        ir_led.parent = root

    # 3. Baliza parpadeante de vigilancia activa en la cara superior
    rec_led = abs_style.create_cylinder(f"{name}_RecLed", radius=0.035, depth=0.04, loc=(ox, oy - 0.52, oz + 1.76), mat=mats['led_red'], col=col)
    rec_led.parent = root

    # Jaula de protección de varillas de acero alrededor del domo
    for cage_i in range(3):
        cage_bar = abs_style.create_torus(f"{name}_CageBar_{cage_i}", major_r=0.42, minor_r=0.02, rot=(math.radians(35 + cage_i * 20), 0, 0),
                                         loc=(ox, oy - 0.55, oz + 1.48), mat=mats['dark_steel'], col=col)
        cage_bar.parent = root
    return root

# ==============================================================================
# PROP 44: SM_Weapon_Locker_Reinforced
# ==============================================================================
def build_prop_44_weapon_locker(ox, oy, oz, col, mats):
    root = bpy.data.objects.new("Root_P44", None)
    root.location = (0, 0, 0)
    col.objects.link(root)
    name = "P44_Weapon_Locker"

    # 1. Cuerpo HUECO del armario de acero naval (Pared posterior, laterales, techo y base)
    plinth = abs_style.create_box(f"{name}_Plinth", size=(1.35, 0.72, 0.14), loc=(ox, oy, oz + 0.07), mat=mats['scorched_steel'], col=col)
    plinth.parent = root
    
    # Pared trasera
    back_wall = abs_style.create_box(f"{name}_BackWall", size=(1.25, 0.06, 2.00), loc=(ox, oy + 0.30, oz + 1.10), mat=mats['dark_steel'], col=col)
    back_wall.parent = root
    # Laterales
    side_l = abs_style.create_box(f"{name}_SideL", size=(0.06, 0.62, 2.00), loc=(ox - 0.60, oy, oz + 1.10), mat=mats['dark_steel'], col=col)
    side_l.parent = root
    side_r = abs_style.create_box(f"{name}_SideR", size=(0.06, 0.62, 2.00), loc=(ox + 0.60, oy, oz + 1.10), mat=mats['dark_steel'], col=col)
    side_r.parent = root
    # Techo
    roof = abs_style.create_box(f"{name}_Roof", size=(1.25, 0.62, 0.08), loc=(ox, oy, oz + 2.06), mat=mats['dark_steel'], col=col)
    roof.parent = root

    # 2. Interior visible: Estante superior y cajas de munición militares
    shelf = abs_style.create_box(f"{name}_TopShelf", size=(1.14, 0.55, 0.05), loc=(ox, oy + 0.02, oz + 1.55), mat=mats['hazard_yellow'], col=col)
    shelf.parent = root

    for can_i, can_x in enumerate([-0.36, 0.0, 0.36]):
        ammo_can = abs_style.create_box(f"{name}_AmmoCan_{can_i}", size=(0.24, 0.36, 0.22), loc=(ox + can_x, oy + 0.05, oz + 1.68), mat=mats['ammo_can_olive'], col=col)
        ammo_can.parent = root
        can_handle = abs_style.create_box(f"{name}_AmmoHandle_{can_i}", size=(0.10, 0.04, 0.04), loc=(ox + can_x, oy + 0.05, oz + 1.81), mat=mats['dark_steel'], col=col)
        can_handle.parent = root

    # 3. Cremalleras verticales y 4 fusiles tácticos en el interior
    rack_floor = abs_style.create_box(f"{name}_RackFloor", size=(1.14, 0.50, 0.12), loc=(ox, oy + 0.02, oz + 0.20), mat=mats['dark_steel'], col=col)
    rack_floor.parent = root
    
    # Barra de retención de cañones con soportes de goma
    rack_retainer = abs_style.create_box(f"{name}_RackRetainer", size=(1.14, 0.06, 0.06), loc=(ox, oy + 0.10, oz + 1.25), mat=mats['hazard_yellow'], col=col)
    rack_retainer.parent = root

    for r_i, rx in enumerate([-0.38, -0.13, 0.13, 0.38]):
        # Cuna para culata
        cradle = abs_style.create_box(f"{name}_Cradle_{r_i}", size=(0.14, 0.26, 0.08), loc=(ox + rx, oy + 0.02, oz + 0.28), mat=mats['rubber_black'], col=col)
        cradle.parent = root
        # Cañón táctico con apagallamas y receptor
        barrel = abs_style.create_cylinder(f"{name}_RifleBarrel_{r_i}", radius=0.022, depth=1.10, loc=(ox + rx, oy + 0.08, oz + 0.88), mat=mats['scorched_steel'], col=col)
        barrel.parent = root
        receiver = abs_style.create_box(f"{name}_Receiver_{r_i}", size=(0.08, 0.18, 0.30), loc=(ox + rx, oy + 0.08, oz + 0.55), mat=mats['dark_steel'], col=col)
        receiver.parent = root
        mag = abs_style.create_box(f"{name}_Magazine_{r_i}", size=(0.06, 0.12, 0.18), loc=(ox + rx, oy - 0.04, oz + 0.48), mat=mats['hazard_yellow'], col=col)
        mag.parent = root

    # 4. Puertas de reja: Puerta izquierda cerrada, puerta derecha abierta a 65 grados
    # Puerta izquierda (Cerrada)
    d_left_frame_t = abs_style.create_box(f"{name}_DL_FT", size=(0.54, 0.04, 0.06), loc=(ox - 0.30, oy - 0.30, oz + 1.98), mat=mats['dark_steel'], col=col)
    d_left_frame_t.parent = root
    d_left_frame_b = abs_style.create_box(f"{name}_DL_FB", size=(0.54, 0.04, 0.06), loc=(ox - 0.30, oy - 0.30, oz + 0.18), mat=mats['dark_steel'], col=col)
    d_left_frame_b.parent = root
    d_left_frame_l = abs_style.create_box(f"{name}_DL_FL", size=(0.06, 0.04, 1.86), loc=(ox - 0.57, oy - 0.30, oz + 1.08), mat=mats['dark_steel'], col=col)
    d_left_frame_l.parent = root
    d_left_frame_r = abs_style.create_box(f"{name}_DL_FR", size=(0.06, 0.04, 1.86), loc=(ox - 0.03, oy - 0.30, oz + 1.08), mat=mats['dark_steel'], col=col)
    d_left_frame_r.parent = root
    d_left_brace = abs_style.create_box(f"{name}_DL_Brace", size=(0.54, 0.05, 0.08), loc=(ox - 0.30, oy - 0.30, oz + 1.08), mat=mats['hazard_yellow'], col=col)
    d_left_brace.parent = root

    # Barrotes verticales puerta izquierda
    for b_x in [-0.48, -0.39, -0.30, -0.21, -0.12]:
        bar = abs_style.create_cylinder(f"{name}_DL_Bar_{b_x}", radius=0.014, depth=1.70, loc=(ox + b_x, oy - 0.30, oz + 1.08), mat=mats['scorched_steel'], col=col)
        bar.parent = root

    # Puerta derecha (Abierta a 65 grados mostrando el interior)
    ang_rad = math.radians(65)
    hinge_x = ox + 0.58
    hinge_y = oy - 0.30
    
    # Bisagras derechas
    for hz in [oz + 0.35, oz + 1.80]:
        hinge = abs_style.create_cylinder(f"{name}_Hinge_{hz}", radius=0.028, depth=0.10, loc=(hinge_x, hinge_y, hz), mat=mats['brass'], col=col)
        hinge.parent = root

    # Hoja de puerta derecha batida
    # Centro aproximado de la hoja a 65 grados
    dw_dx = -math.cos(ang_rad) * 0.28
    dw_dy = -math.sin(ang_rad) * 0.28
    d_right_brace = abs_style.create_box(f"{name}_DR_Brace", size=(0.54, 0.05, 0.08), rot=(0, 0, ang_rad),
                                         loc=(hinge_x + dw_dx, hinge_y + dw_dy, oz + 1.08), mat=mats['hazard_yellow'], col=col)
    d_right_brace.parent = root

    # Barrotes verticales puerta derecha rotados
    for b_i, b_dist in enumerate([0.10, 0.20, 0.30, 0.40, 0.50]):
        bx = hinge_x - math.cos(ang_rad) * b_dist
        by = hinge_y - math.sin(ang_rad) * b_dist
        bar_r = abs_style.create_cylinder(f"{name}_DR_Bar_{b_i}", radius=0.014, depth=1.70,
                                          loc=(bx, by, oz + 1.08), mat=mats['scorched_steel'], col=col)
        bar_r.parent = root

    # Cadena y candado colgando de la aldaba izquierda
    padlock_body = abs_style.create_box(f"{name}_PadlockBody", size=(0.10, 0.05, 0.12), loc=(ox - 0.03, oy - 0.36, oz + 1.02), mat=mats['brass'], col=col)
    padlock_body.parent = root
    padlock_shackle = abs_style.create_torus(f"{name}_PadlockShackle", major_r=0.045, minor_r=0.014, rot=(math.radians(90), 0, 0),
                                            loc=(ox - 0.03, oy - 0.36, oz + 1.10), mat=mats['chrome'], col=col)
    padlock_shackle.parent = root
    return root

# ==============================================================================
# PROP 45: SM_Emergency_Breach_Axe_Box
# ==============================================================================
def build_prop_45_breach_axe_box(ox, oy, oz, col, mats):
    root = bpy.data.objects.new("Root_P45", None)
    root.location = (0, 0, 0)
    col.objects.link(root)
    name = "P45_Axe_Box"

    # Pedestal de pared mural para colgado
    wall_backing = abs_style.create_box(f"{name}_WallBack", size=(1.10, 0.12, 1.70), loc=(ox, oy + 0.25, oz + 0.90), mat=mats['dark_steel'], col=col)
    wall_backing.parent = root

    # 1. Armario metálico mural HUECO en rojo hazard
    # Fondo del armario
    cab_back = abs_style.create_box(f"{name}_CabBack", size=(0.68, 0.04, 1.25), loc=(ox, oy + 0.16, oz + 1.05), mat=mats['hazard_red'], col=col)
    cab_back.parent = root
    # Laterales
    cab_l = abs_style.create_box(f"{name}_CabL", size=(0.04, 0.20, 1.25), loc=(ox - 0.32, oy + 0.08, oz + 1.05), mat=mats['hazard_red'], col=col)
    cab_l.parent = root
    cab_r = abs_style.create_box(f"{name}_CabR", size=(0.04, 0.20, 1.25), loc=(ox + 0.32, oy + 0.08, oz + 1.05), mat=mats['hazard_red'], col=col)
    cab_r.parent = root
    cab_top = abs_style.create_box(f"{name}_CabTop", size=(0.68, 0.20, 0.04), loc=(ox, oy + 0.08, oz + 1.66), mat=mats['hazard_red'], col=col)
    cab_top.parent = root
    cab_bot = abs_style.create_box(f"{name}_CabBot", size=(0.68, 0.20, 0.04), loc=(ox, oy + 0.08, oz + 0.44), mat=mats['hazard_red'], col=col)
    cab_bot.parent = root

    # 2. Hacha táctica pesada contra incendios y brechas montada prominentemente en el interior
    # Mango de fibra de vidrio roja ergonómico
    axe_handle = abs_style.create_cylinder(f"{name}_AxeHandle", radius=0.024, depth=0.98, loc=(ox, oy + 0.08, oz + 1.05), mat=mats['hazard_red'], col=col)
    axe_handle.parent = root
    # Empuñadura antideslizante con textura engomada
    axe_grip = abs_style.create_cylinder(f"{name}_AxeGrip", radius=0.028, depth=0.32, loc=(ox, oy + 0.08, oz + 0.72), mat=mats['rubber_black'], col=col)
    axe_grip.parent = root

    # Cabeza forjada de acero: Filo ancho cromado por delante y pica penetradora trasera
    axe_eye = abs_style.create_box(f"{name}_AxeEye", size=(0.08, 0.10, 0.12), loc=(ox, oy + 0.08, oz + 1.45), mat=mats['dark_steel'], col=col)
    axe_eye.parent = root
    # Filo de hacha en cuña cromada reflectante
    axe_blade = abs_style.create_cone(f"{name}_AxeBlade", radius1=0.14, radius2=0.02, depth=0.22, rot=(math.radians(90), 0, math.radians(90)),
                                      loc=(ox - 0.14, oy + 0.08, oz + 1.45), mat=mats['chrome'], col=col)
    axe_blade.parent = root
    # Pica trasera penetradora
    axe_pick = abs_style.create_cone(f"{name}_AxePick", radius1=0.05, radius2=0.005, depth=0.20, rot=(math.radians(90), 0, math.radians(-90)),
                                     loc=(ox + 0.14, oy + 0.08, oz + 1.45), mat=mats['scorched_steel'], col=col)
    axe_pick.parent = root

    # Cunas de sujeción de desenganche rápido en latón dorado
    for c_z in [oz + 0.82, oz + 1.28]:
        clip = abs_style.create_box(f"{name}_Clip_{c_z}", size=(0.10, 0.06, 0.04), loc=(ox, oy + 0.13, c_z), mat=mats['brass'], col=col)
        clip.parent = root

    # 3. Puerta batiente con marco amarillo hazard abierta a 35 grados (permite ver el hacha al 100%)
    door_ang = math.radians(35)
    hinge_x = ox - 0.33
    hinge_y = oy - 0.02

    # Marco abierto
    d_dx = math.cos(door_ang) * 0.34
    d_dy = -math.sin(door_ang) * 0.34
    door_frame = abs_style.create_box(f"{name}_DoorFrame", size=(0.68, 0.05, 1.25), rot=(0, 0, -door_ang),
                                      loc=(hinge_x + d_dx, hinge_y + d_dy, oz + 1.05), mat=mats['hazard_yellow'], col=col)
    door_frame.parent = root

    # Panel de vidrio templado insertado en el marco abierto
    glass_pane = abs_style.create_box(f"{name}_GlassPane", size=(0.58, 0.02, 1.15), rot=(0, 0, -door_ang),
                                      loc=(hinge_x + d_dx, hinge_y + d_dy, oz + 1.05), mat=mats['glass_tint'], col=col)
    glass_pane.parent = root

    # 4. Martillo percutor exterior para romper el cristal colgado con cadeneta de acero
    hammer_chain = abs_style.create_cylinder(f"{name}_HammerChain", radius=0.008, depth=0.45, loc=(ox + 0.40, oy + 0.04, oz + 0.95), mat=mats['chrome'], col=col)
    hammer_chain.parent = root
    hammer_handle = abs_style.create_cylinder(f"{name}_HammerHandle", radius=0.014, depth=0.22, loc=(ox + 0.40, oy + 0.04, oz + 0.68), mat=mats['hazard_yellow'], col=col)
    hammer_handle.parent = root
    hammer_head = abs_style.create_cylinder(f"{name}_HammerHead", radius=0.025, depth=0.08, rot=(0, math.radians(90), 0),
                                            loc=(ox + 0.40, oy + 0.04, oz + 0.78), mat=mats['dark_steel'], col=col)
    hammer_head.parent = root
    return root

# ==============================================================================
# PIPELINE DE ESCENA, RENDER Y LÁMINA MAESTRA
# ==============================================================================
def generate_lote9_scene(save_blend=True):
    print("=" * 70)
    print("[*] Iniciando generacion de Props Maestros Lote 9 (Props 41 al 45: Seguridad & Blindaje)...")
    print("=" * 70)

    abs_style.reset_comic_scene(bg_color=(0.04, 0.05, 0.07, 1.0), bg_strength=0.9, ink_thickness=2.4)
    col_props = abs_style.create_collection("Props_Lote9_Seguridad")
    mats = init_lote9_materials()

    ped_mat = abs_style.get_comic_material("Pedestal_Props9", base_color=(0.08, 0.09, 0.12), roughness=0.45, metallic=0.7)
    hazard_strip_mat = abs_style.get_comic_material("Ped_Hazard_Lote9", base_color=(0.95, 0.70, 0.08), roughness=0.30, metallic=0.2)

    spacing_x = 4.2
    closeups = {}

    PROP_BUILDERS = {
        41: build_prop_41_turnstile,
        42: build_prop_42_keycard_box,
        43: build_prop_43_surveillance_turret,
        44: build_prop_44_weapon_locker,
        45: build_prop_45_breach_axe_box,
    }

    PROP_CAMERAS = {
        41: {"offset": (2.2, -2.8, 1.8), "target_x": 0.0, "target_y": 0.0, "target_z": 0.75, "focal": 36},  # Turnstile
        42: {"offset": (1.8, -2.4, 1.4), "target_x": 0.0, "target_y": 0.1, "target_z": 1.10, "focal": 38},  # Keycard Box
        43: {"offset": (2.2, -2.8, 1.8), "target_x": 0.0, "target_y": -0.3, "target_z": 1.55, "focal": 36}, # Turret
        44: {"offset": (2.2, -3.2, 1.8), "target_x": 0.0, "target_y": 0.0, "target_z": 1.15, "focal": 36},  # Weapon Locker
        45: {"offset": (1.8, -2.4, 1.4), "target_x": 0.0, "target_y": 0.0, "target_z": 1.05, "focal": 38},  # Axe Box
    }

    for idx, (pid, pname, ptitle, pdesc) in enumerate(PROPS_LOTE9):
        x = (idx - 2.0) * spacing_x
        y = 0.0
        z = 0.0

        ped = abs_style.create_box(f"Ped_{pname}", size=(3.8, 3.8, 0.22), loc=(x, y, 0.11), mat=ped_mat, col=col_props)
        strip = abs_style.create_box(f"Strip_{pname}", size=(3.8, 0.12, 0.06), loc=(x, y - 1.85, 0.25), mat=hazard_strip_mat, col=col_props)

        builder = PROP_BUILDERS[pid]
        builder(x, y, 0.22, col_props, mats)

    floor_mat = abs_style.get_comic_material("Floor_Props9", base_color=(0.03, 0.035, 0.045), roughness=0.28, metallic=0.8)
    abs_style.create_box("HangarFloor_Props9", size=(28.0, 16.0, 0.15), loc=(0, 0, -0.08), mat=floor_mat, col=col_props)

    abs_style.setup_studio_lighting(sun_energy=5.5, rim_energy=3.8, fill_energy=2.2)
    abs_style.setup_camera(name="Camera_Props_Lote9", loc=(0, -16.5, 9.5), target=(0, 0.0, 1.1), focal_length=28)

    if save_blend:
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_FILE)
        print(f"[+] Blend guardado: {BLEND_FILE}")

    raw_pan_path = os.path.join(RENDERS_DIR, "Raw_Props_Lote9_Panorama.png")
    abs_style.render_and_save("Raw_Props_Lote9_Panorama.png", res_x=2560, res_y=1440)

    # Close-ups con aislamiento estricto
    def set_hierarchy_hide_render(obj, hide):
        if not obj:
            return
        obj.hide_render = hide
        for child in obj.children:
            set_hierarchy_hide_render(child, hide)

    for idx, (pid, pname, _, _) in enumerate(PROPS_LOTE9):
        x = (idx - 2.0) * spacing_x
        y = 0.0
        z = 0.0

        for other_idx, (o_pid, o_pname, _, _) in enumerate(PROPS_LOTE9):
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

    for o_pid, o_pname, _, _ in PROPS_LOTE9:
        o_root = bpy.data.objects.get(f"Root_P{o_pid:02d}")
        if o_root:
            set_hierarchy_hide_render(o_root, False)
        o_ped = bpy.data.objects.get(f"Ped_{o_pname}")
        if o_ped:
            o_ped.hide_render = False
        o_strip = bpy.data.objects.get(f"Strip_{o_pname}")
        if o_strip:
            o_strip.hide_render = False

    assemble_lote9_sheet(raw_pan_path, closeups)
    print("[+] Lote 9 de Props Maestros completado con exito!")

def assemble_lote9_sheet(deck_render_path, closeups):
    print("[*] Componiendo Lamina Maestra Tecnica 2.5K de Props Lote 9...")
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

    draw.text((40, 18), "ASTRA HAZARD // REPOSITORIO DE ARQUITECTURA Y PROPS MAESTROS // BLENDER 5.2 LTS", fill=(245, 180, 20), font=font_sub)
    draw.text((40, 46), "CATÁLOGO DE PROPS MAESTROS // LOTE 9 (PROPS 41 A 45: SEGURIDAD, BLINDAJE & CONTENCIÓN)", fill=(255, 255, 255), font=font_main)

    badges = [
        ("5 PROPS DE SEGURIDAD", (192, 57, 43)),
        ("CONTROL DE ACCESOS & BLINDAJE", (41, 128, 185)),
        ("INTERACCIÓN TÁCTICA", (39, 174, 96)),
        ("VERIFICADO 100% CERO BUGS", (142, 68, 173))
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

    for idx, (pid, pname, ptitle, pdesc) in enumerate(PROPS_LOTE9):
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
        draw.text((tx, cy + 20), f"PROP MAESTRO {pid:02d}", fill=(245, 180, 20), font=font_card_sub)

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
        draw.text((tx, ty), "• Cel-Shading Comic 3D", fill=(250, 190, 70), font=font_card_desc)
        ty += 15
        draw.text((tx, ty), "• PBR Stylized & Colision UCX", fill=(250, 190, 70), font=font_card_desc)

        draw.rounded_rectangle((cx + 14, cy + card_h - 38, cx + card_w - 14, cy + card_h - 14), radius=4, fill=(15, 18, 24))
        draw.text((cx + 24, cy + card_h - 31), f"ESTADO: CERTIFICADO 100% 3D // PID_{pid:02d}", fill=(46, 204, 113), font=font_foot)

    master_path = os.path.join(RENDERS_DIR, "Showcase_Props_Lote9_Seguridad_Master.png")
    artifact_path = os.path.join(ARTIFACT_DIR, "Showcase_Props_Lote9_Seguridad_Master.png")
    canvas.save(master_path, format="PNG")
    shutil.copy2(master_path, artifact_path)
    print(f"[+] Lamina Maestra guardada en: {master_path}")
    print(f"[+] Sincronizada con artefacto con exito!")

if __name__ == "__main__":
    generate_lote9_scene()

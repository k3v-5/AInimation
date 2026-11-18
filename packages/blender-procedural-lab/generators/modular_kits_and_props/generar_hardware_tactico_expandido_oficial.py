# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Suite Oficial de Hardware Tactico Expandido (6 Dispositivos: 4 Base + 2 Nuevos)
# Blender 5.2 LTS - Shaders Stylized PBR, Cel-Shading y Freestyle Lineart

import bpy
import bmesh
import math
import os
import sys
from mathutils import Vector, Euler


script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

import astra_blender_styling as abs_style

def init_hardware_materials():
    mats = {}
    mats['hazard_yellow'] = abs_style.get_comic_material("HW_Hazard_Yellow", base_color=(0.95, 0.68, 0.08), roughness=0.32, metallic=0.15, tex_pack="T_Trim_Industrial")
    mats['safety_orange'] = abs_style.get_comic_material("HW_Safety_Orange", base_color=(0.95, 0.38, 0.06), roughness=0.35, metallic=0.10)
    mats['gunmetal'] = abs_style.get_comic_material("HW_Gunmetal", base_color=(0.20, 0.22, 0.26), roughness=0.35, metallic=0.88, tex_pack="T_Steel_Plates")
    mats['steel_bright'] = abs_style.get_comic_material("HW_Steel_Bright", base_color=(0.82, 0.85, 0.88), roughness=0.18, metallic=0.95)
    mats['copper'] = abs_style.get_comic_material("HW_Copper", base_color=(0.95, 0.45, 0.22), roughness=0.25, metallic=0.92)
    mats['carbon_fiber'] = abs_style.get_comic_material("HW_Carbon_Fiber", base_color=(0.08, 0.09, 0.10), roughness=0.55, metallic=0.25)
    mats['holo_cyan'] = abs_style.get_comic_material("HW_Holo_Cyan", base_color=(0.0, 0.85, 1.0), roughness=0.08,
                                                     emissive_color=(0.0, 0.90, 1.0, 1.0), emissive_strength=3.2)
    mats['holo_green'] = abs_style.get_comic_material("HW_Holo_Green", base_color=(0.05, 0.95, 0.35), roughness=0.08,
                                                      emissive_color=(0.05, 0.95, 0.35, 1.0), emissive_strength=3.0)
    mats['amber_led'] = abs_style.get_comic_material("HW_Amber_LED", base_color=(1.0, 0.70, 0.05), roughness=0.08,
                                                     emissive_color=(1.0, 0.75, 0.05, 1.0), emissive_strength=3.0)
    mats['lamp_glow'] = abs_style.get_comic_material("HW_Lamp_Glow", base_color=(0.98, 0.95, 0.70), roughness=0.15, metallic=0.0,
                                                     emissive_color=(1.0, 0.96, 0.75, 1.0), emissive_strength=3.6)
    mats['rubber_black'] = abs_style.get_comic_material("HW_Rubber_Black", base_color=(0.06, 0.06, 0.07), roughness=0.75, metallic=0.05)
    return mats

def build_hardware_device(hw_id, name, origin, col, mats):
    root = bpy.data.objects.new(f"Root_{name}", None)
    root.location = (0, 0, 0)
    col.objects.link(root)
    ox, oy, oz = origin

    if hw_id == 1: # HW01_Stasis_Pod_Cryo
        shell = abs_style.create_cylinder(f"{name}_Shell", radius=0.8, depth=2.8, loc=(ox, oy, oz + 1.4), mat=mats['gunmetal'], col=col)
        shell.parent = root
        glass = abs_style.create_cylinder(f"{name}_GlassWindow", radius=0.65, depth=1.8, loc=(ox, oy - 0.2, oz + 1.5), mat=mats['holo_cyan'], col=col)
        glass.parent = root
        ecg = abs_style.create_box(f"{name}_ECGMonitor", size=(0.4, 0.1, 0.3), loc=(ox, oy - 0.85, oz + 2.5), mat=mats['holo_green'], col=col)
        ecg.parent = root

    elif hw_id == 2: # HW02_Holographic_Table_3D
        base = abs_style.create_cylinder(f"{name}_Pedestal", radius=1.2, depth=0.8, loc=(ox, oy, oz + 0.4), mat=mats['gunmetal'], col=col)
        base.parent = root
        emitter = abs_style.create_torus(f"{name}_Ring", major_r=1.25, minor_r=0.08, loc=(ox, oy, oz + 0.8), mat=mats['steel_bright'], col=col)
        emitter.parent = root
        holo_disk = abs_style.create_cylinder(f"{name}_HoloGridDisk", radius=1.05, depth=0.03, loc=(ox, oy, oz + 0.82), mat=mats['holo_cyan'], col=col)
        holo_disk.parent = root
        holo_ring1 = abs_style.create_torus(f"{name}_HoloRingOuter", major_r=0.78, minor_r=0.022, loc=(ox, oy, oz + 1.02), mat=mats['holo_cyan'], col=col)
        holo_ring1.parent = root
        holo_ring2 = abs_style.create_torus(f"{name}_HoloRingInner", major_r=0.46, minor_r=0.018, loc=(ox, oy, oz + 1.15), mat=mats['holo_green'], col=col)
        holo_ring2.parent = root
        holo_core = abs_style.create_box(f"{name}_ShipHoloHull", size=(0.75, 0.28, 0.14), loc=(ox, oy, oz + 1.15), mat=mats['holo_cyan'], col=col)
        holo_core.parent = root
        holo_beacon = abs_style.create_cylinder(f"{name}_ShipHoloBeacon", radius=0.08, depth=0.28, loc=(ox, oy, oz + 1.28), mat=mats['amber_led'], col=col)
        holo_beacon.parent = root

    elif hw_id == 3: # HW03_Wrist_PDA_Scanner
        chassis = abs_style.create_box(f"{name}_Body", size=(0.6, 0.8, 0.18), loc=(ox, oy, oz + 0.6), mat=mats['gunmetal'], col=col)
        chassis.parent = root
        screen = abs_style.create_box(f"{name}_Screen", size=(0.48, 0.65, 0.05), loc=(ox, oy, oz + 0.7), mat=mats['holo_green'], col=col)
        screen.parent = root
        strap = abs_style.create_torus(f"{name}_WristStrap", major_r=0.45, minor_r=0.06, rot=(0, math.radians(90), 0), loc=(ox, oy, oz + 0.45), mat=mats['carbon_fiber'], col=col)
        strap.parent = root

    elif hw_id == 4: # HW04_Signal_Repeater_Station (Baliza SOS & Foco Táctico de Emergencia de Despliegue Rápido)
        # 1. Chasis central / Carcasa de batería y aviónica
        chassis = abs_style.create_cylinder(f"{name}_PowerChassis", radius=0.22, depth=0.32, segments=8, loc=(ox, oy, oz + 0.68), mat=mats['gunmetal'], col=col)
        chassis.parent = root
        hinge_ring = abs_style.create_cylinder(f"{name}_LegHingeRing", radius=0.24, depth=0.08, loc=(ox, oy, oz + 0.54), mat=mats['hazard_yellow'], col=col)
        hinge_ring.parent = root
        spread_hub = abs_style.create_cylinder(f"{name}_SpreaderHub", radius=0.10, depth=0.06, loc=(ox, oy, oz + 0.28), mat=mats['gunmetal'], col=col)
        spread_hub.parent = root
        mast_clamp = abs_style.create_cylinder(f"{name}_MastClampLower", radius=0.15, depth=0.08, loc=(ox, oy, oz + 0.88), mat=mats['hazard_yellow'], col=col)
        mast_clamp.parent = root
        clamp_knob = abs_style.create_cylinder(f"{name}_ClampKnob", radius=0.03, depth=0.12, rot=(0, math.radians(90), 0), loc=(ox + 0.17, oy, oz + 0.88), mat=mats['steel_bright'], col=col)
        clamp_knob.parent = root
        carry_handle = abs_style.create_box(f"{name}_CarryHandle", size=(0.06, 0.26, 0.10), loc=(ox - 0.22, oy, oz + 0.72), mat=mats['safety_orange'], col=col)
        carry_handle.parent = root

        # Panel de control y telemetría frontal (-Y)
        ctrl_panel = abs_style.create_box(f"{name}_ControlPanel", size=(0.18, 0.05, 0.14), rot=(math.radians(20), 0, 0), loc=(ox, oy - 0.20, oz + 0.72), mat=mats['gunmetal'], col=col)
        ctrl_panel.parent = root
        disp_screen = abs_style.create_box(f"{name}_DisplayScreen", size=(0.12, 0.02, 0.07), rot=(math.radians(20), 0, 0), loc=(ox, oy - 0.22, oz + 0.74), mat=mats['holo_cyan'], col=col)
        disp_screen.parent = root
        led1 = abs_style.create_cylinder(f"{name}_StatusLED1", radius=0.012, depth=0.02, rot=(math.radians(110), 0, 0), loc=(ox - 0.05, oy - 0.22, oz + 0.68), mat=mats['amber_led'], col=col)
        led1.parent = root
        led2 = abs_style.create_cylinder(f"{name}_StatusLED2", radius=0.012, depth=0.02, rot=(math.radians(110), 0, 0), loc=(ox + 0.05, oy - 0.22, oz + 0.68), mat=mats['holo_green'], col=col)
        led2.parent = root

        # 2. Trípode articulado simétrico a 120° (100% conectado mecánicamente y apoyado en Z = 0)
        for i in range(3):
            theta = i * (2.0 * math.pi / 3.0)
            cos_t = math.cos(theta)
            sin_t = math.sin(theta)

            p_hinge = Vector((ox + 0.20 * cos_t, oy + 0.20 * sin_t, oz + 0.54))
            p_foot = Vector((ox + 0.62 * cos_t, oy + 0.62 * sin_t, oz + 0.03))

            v_leg = p_foot - p_hinge
            l_leg = v_leg.length
            p_leg_mid = (p_hinge + p_foot) * 0.5
            rot_leg = Vector((0.0, 0.0, 1.0)).rotation_difference(v_leg).to_euler()

            leg_strut = abs_style.create_cylinder(f"{name}_LegStrut_{i}", radius=0.042, depth=l_leg, loc=p_leg_mid, rot=rot_leg, mat=mats['gunmetal'], col=col)
            leg_strut.parent = root

            p_sleeve = p_hinge + v_leg * 0.28
            leg_sleeve = abs_style.create_cylinder(f"{name}_LegSleeve_{i}", radius=0.050, depth=l_leg * 0.45, loc=p_sleeve, rot=rot_leg, mat=mats['hazard_yellow'], col=col)
            leg_sleeve.parent = root

            p_piston = p_hinge + v_leg * 0.72
            leg_piston = abs_style.create_cylinder(f"{name}_LegPiston_{i}", radius=0.030, depth=l_leg * 0.38, loc=p_piston, rot=rot_leg, mat=mats['steel_bright'], col=col)
            leg_piston.parent = root

            foot_pad = abs_style.create_cylinder(f"{name}_FootPad_{i}", radius=0.10, depth=0.03, loc=(p_foot.x, p_foot.y, oz + 0.015), mat=mats['rubber_black'], col=col)
            foot_pad.parent = root
            foot_bracket = abs_style.create_box(f"{name}_FootBracket_{i}", size=(0.08, 0.08, 0.06), loc=(p_foot.x, p_foot.y, oz + 0.05), mat=mats['gunmetal'], col=col)
            foot_bracket.parent = root

            p_spread_hub = Vector((ox + 0.10 * cos_t, oy + 0.10 * sin_t, oz + 0.28))
            v_spread = p_leg_mid - p_spread_hub
            l_spread = v_spread.length
            p_spread_mid = (p_spread_hub + p_leg_mid) * 0.5
            rot_spread = Vector((0.0, 0.0, 1.0)).rotation_difference(v_spread).to_euler()

            spreader = abs_style.create_cylinder(f"{name}_Spreader_{i}", radius=0.018, depth=l_spread, loc=p_spread_mid, rot=rot_spread, mat=mats['steel_bright'], col=col)
            spreader.parent = root

        # 3. Mástil telescópico con cable helicoidal
        mast_lower = abs_style.create_cylinder(f"{name}_MastLower", radius=0.065, depth=0.70, loc=(ox, oy, oz + 1.22), mat=mats['gunmetal'], col=col)
        mast_lower.parent = root

        collar_mid = abs_style.create_cylinder(f"{name}_MastCollarMid", radius=0.080, depth=0.07, loc=(ox, oy, oz + 1.58), mat=mats['hazard_yellow'], col=col)
        collar_mid.parent = root
        collar_lever = abs_style.create_cylinder(f"{name}_CollarLever", radius=0.016, depth=0.12, rot=(0, math.radians(90), 0), loc=(ox + 0.09, oy, oz + 1.58), mat=mats['steel_bright'], col=col)
        collar_lever.parent = root

        mast_upper = abs_style.create_cylinder(f"{name}_MastUpper", radius=0.048, depth=0.65, loc=(ox, oy, oz + 1.92), mat=mats['steel_bright'], col=col)
        mast_upper.parent = root

        for s in range(4):
            cable = abs_style.create_torus(f"{name}_CableCoil_{s}", major_r=0.078, minor_r=0.015, rot=(math.radians(12), math.radians(6), 0), loc=(ox, oy, oz + 1.05 + s * 0.14), mat=mats['carbon_fiber'], col=col)
            cable.parent = root

        # 4. Cabezal dual: Horquilla de montaje + Foco de trabajo orientable + Baliza transpondedora SOS
        head_collar = abs_style.create_cylinder(f"{name}_HeadCollar", radius=0.065, depth=0.06, loc=(ox, oy, oz + 2.26), mat=mats['hazard_yellow'], col=col)
        head_collar.parent = root

        fork_l = abs_style.create_box(f"{name}_ForkL", size=(0.035, 0.08, 0.26), loc=(ox - 0.20, oy, oz + 2.39), mat=mats['gunmetal'], col=col)
        fork_l.parent = root
        fork_r = abs_style.create_box(f"{name}_ForkR", size=(0.035, 0.08, 0.26), loc=(ox + 0.20, oy, oz + 2.39), mat=mats['gunmetal'], col=col)
        fork_r.parent = root

        pin_l = abs_style.create_cylinder(f"{name}_ForkPinL", radius=0.032, depth=0.05, rot=(0, math.radians(90), 0), loc=(ox - 0.21, oy, oz + 2.48), mat=mats['steel_bright'], col=col)
        pin_l.parent = root
        pin_r = abs_style.create_cylinder(f"{name}_ForkPinR", radius=0.032, depth=0.05, rot=(0, math.radians(90), 0), loc=(ox + 0.21, oy, oz + 2.48), mat=mats['steel_bright'], col=col)
        pin_r.parent = root

        # FOCO INDUSTRIAL DE TRABAJO (Inclinado 25° hacia abajo iluminando hacia el frente -Y)
        tilt_lamp = (math.radians(25), 0, 0)

        lamp_body = abs_style.create_box(f"{name}_LampChassis", size=(0.34, 0.16, 0.22), rot=tilt_lamp, loc=(ox, oy - 0.04, oz + 2.48), mat=mats['gunmetal'], col=col)
        lamp_body.parent = root

        for fin_i in range(5):
            fin = abs_style.create_box(f"{name}_LampFin_{fin_i}", size=(0.30, 0.012, 0.17), rot=tilt_lamp, loc=(ox, oy + 0.03 + fin_i * 0.018, oz + 2.48), mat=mats['steel_bright'], col=col)
            fin.parent = root

        lamp_bezel = abs_style.create_box(f"{name}_LampBezel", size=(0.36, 0.03, 0.24), rot=tilt_lamp, loc=(ox, oy - 0.12, oz + 2.48), mat=mats['hazard_yellow'], col=col)
        lamp_bezel.parent = root

        lamp_lens = abs_style.create_box(f"{name}_LampLens", size=(0.30, 0.015, 0.18), rot=tilt_lamp, loc=(ox, oy - 0.135, oz + 2.48), mat=mats['lamp_glow'], col=col)
        lamp_lens.parent = root

        for rx in [-0.09, 0.0, 0.09]:
            for rz_off in [-0.04, 0.04]:
                led_cup = abs_style.create_cylinder(f"{name}_LedCup_{rx}_{rz_off}", radius=0.030, depth=0.012, rot=(math.radians(115), 0, 0), loc=(ox + rx, oy - 0.14, oz + 2.48 + rz_off), mat=mats['steel_bright'], col=col)
                led_cup.parent = root

        for gz_off in [-0.06, 0.0, 0.06]:
            gbar_h = abs_style.create_cylinder(f"{name}_GrilleBarH_{gz_off}", radius=0.005, depth=0.33, rot=(0, math.radians(90), 0), loc=(ox, oy - 0.15, oz + 2.48 + gz_off), mat=mats['steel_bright'], col=col)
            gbar_h.parent = root
        for gx_off in [-0.10, 0.10]:
            gbar_v = abs_style.create_cylinder(f"{name}_GrilleBarV_{gx_off}", radius=0.005, depth=0.20, rot=tilt_lamp, loc=(ox + gx_off, oy - 0.15, oz + 2.48), mat=mats['steel_bright'], col=col)
            gbar_v.parent = root

        # BALIZA SOS Y MATRIZ DE TELEMETRÍA (Cabezal superior)
        ant_riser = abs_style.create_cylinder(f"{name}_AntennaRiser", radius=0.035, depth=0.16, loc=(ox, oy, oz + 2.66), mat=mats['gunmetal'], col=col)
        ant_riser.parent = root

        beacon_base = abs_style.create_cylinder(f"{name}_BeaconBase", radius=0.060, depth=0.04, loc=(ox, oy, oz + 2.74), mat=mats['hazard_yellow'], col=col)
        beacon_base.parent = root
        beacon_dome = abs_style.create_cylinder(f"{name}_BeaconDome", radius=0.048, depth=0.08, loc=(ox, oy, oz + 2.80), mat=mats['amber_led'], col=col)
        beacon_dome.parent = root
        beacon_rib = abs_style.create_torus(f"{name}_BeaconRib", major_r=0.052, minor_r=0.005, rot=(0, math.radians(90), 0), loc=(ox, oy, oz + 2.80), mat=mats['steel_bright'], col=col)
        beacon_rib.parent = root

        ant_l = abs_style.create_cylinder(f"{name}_AntennaL", radius=0.007, depth=0.55, rot=(0, math.radians(-12), 0), loc=(ox - 0.13, oy, oz + 2.82), mat=mats['steel_bright'], col=col)
        ant_l.parent = root
        ant_r = abs_style.create_cylinder(f"{name}_AntennaR", radius=0.007, depth=0.55, rot=(0, math.radians(12), 0), loc=(ox + 0.13, oy, oz + 2.82), mat=mats['steel_bright'], col=col)
        ant_r.parent = root

        dish_arm = abs_style.create_box(f"{name}_DishArm", size=(0.04, 0.10, 0.04), loc=(ox, oy + 0.10, oz + 2.65), mat=mats['gunmetal'], col=col)
        dish_arm.parent = root
        parabolic_dish = abs_style.create_cone(f"{name}_ParabolicDish", radius1=0.20, radius2=0.06, depth=0.08, rot=(math.radians(-90), 0, 0), loc=(ox, oy + 0.16, oz + 2.65), mat=mats['hazard_yellow'], col=col)
        parabolic_dish.parent = root
        feed_horn = abs_style.create_cylinder(f"{name}_FeedHorn", radius=0.018, depth=0.08, rot=(math.radians(90), 0, 0), loc=(ox, oy + 0.18, oz + 2.65), mat=mats['holo_cyan'], col=col)
        feed_horn.parent = root


    elif hw_id == 5: # HW05_Tactical_Drone_Dock_Station (NUEVO)
        backplate = abs_style.create_box(f"{name}_WallMount", size=(1.8, 0.25, 2.2), loc=(ox, oy, oz + 1.4), mat=mats['gunmetal'], col=col)
        backplate.parent = root
        cradle = abs_style.create_cylinder(f"{name}_DockBay", radius=0.65, depth=0.4, rot=(math.radians(90), 0, 0), loc=(ox, oy - 0.2, oz + 1.4), mat=mats['hazard_yellow'], col=col)
        cradle.parent = root
        coil = abs_style.create_torus(f"{name}_InductionCoil", major_r=0.55, minor_r=0.06, rot=(math.radians(90), 0, 0), loc=(ox, oy - 0.35, oz + 1.4), mat=mats['copper'], col=col)
        coil.parent = root
        panel = abs_style.create_box(f"{name}_StatusLED", size=(0.6, 0.05, 0.25), loc=(ox, oy - 0.3, oz + 2.25), mat=mats['holo_cyan'], col=col)
        panel.parent = root

    elif hw_id == 6: # HW06_Atmospheric_Purification_Pylon (NUEVO)
        base = abs_style.create_box(f"{name}_GroundPlinth", size=(1.2, 1.2, 0.2), loc=(ox, oy, oz + 0.1), mat=mats['gunmetal'], col=col)
        base.parent = root
        tower = abs_style.create_cylinder(f"{name}_TurbineTower", radius=0.42, depth=1.8, loc=(ox, oy, oz + 1.05), mat=mats['safety_orange'], col=col)
        tower.parent = root
        grille = abs_style.create_cylinder(f"{name}_VentGrille", radius=0.45, depth=0.4, loc=(ox, oy, oz + 0.8), mat=mats['gunmetal'], col=col)
        grille.parent = root
        ion_ring1 = abs_style.create_torus(f"{name}_IonRing1", major_r=0.48, minor_r=0.05, loc=(ox, oy, oz + 1.4), mat=mats['holo_cyan'], col=col)
        ion_ring1.parent = root
        ion_ring2 = abs_style.create_torus(f"{name}_IonRing2", major_r=0.48, minor_r=0.05, loc=(ox, oy, oz + 1.7), mat=mats['holo_cyan'], col=col)
        ion_ring2.parent = root
        strobe = abs_style.create_cylinder(f"{name}_TopStrobe", radius=0.18, depth=0.25, loc=(ox, oy, oz + 2.15), mat=mats['amber_led'], col=col)
        strobe.parent = root

    return root

from PIL import Image, ImageDraw, ImageFont
import shutil

HARDWARE_DATA = [
    (1, "HW01_Stasis_Pod_Cryo", "Capsula Medica de Estasis Criogenica", "Camara de preservacion para heridos criticos con cupula de cuarzo, monitor ECG y soporte vital"),
    (2, "HW02_Holographic_Table_3D", "Mesa Holografica de Mando Táctico", "Mesa de navegacion octogonal con proyector volumetrico 3D del plano estructural y anomalias"),
    (3, "HW03_Wrist_PDA_Scanner", "Terminal Biometrico de Muneca", "Computadora tactica de interfaz neuronal con sensor atmosferico y cartografia topologica local"),
    (4, "HW04_Signal_Repeater_Station", "Estacion de Transmision SOS", "Plataforma de comunicaciones de largo alcance con mastil telescopico y antena parabolica orientable"),
    (5, "HW05_Tactical_Drone_Dock_Station", "Estacion de Atraque de Drones", "Bahia de acoplamiento vertical con bobinas de recarga inductiva y panel de diagnostico de baterias"),
    (6, "HW06_Atmospheric_Purification_Pylon", "Pilon de Purificacion Atmosferica", "Torre de filtrado de gases toxicos de 3 fases con anillos ionicos y alarma estroboscopica"),
]

def generate_hardware_technical_sheet(deck_render_path, closeups):
    print("[*] Componiendo Lamina Maestra Tecnica 2.5K de Hardware Tactico...")
    sheet_w, sheet_h = 2560, 1440
    canvas = Image.new("RGBA", (sheet_w, sheet_h), (12, 15, 20, 255))
    draw = ImageDraw.Draw(canvas)
    
    try:
        font_main = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 30)
        font_sub = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 15)
        font_pill = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 12)
        font_card_title = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 16)
        font_card_sub = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 12)
        font_card_desc = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 11)
    except Exception:
        font_main = font_sub = font_pill = font_card_title = font_card_sub = font_card_desc = ImageFont.load_default()
        
    # Header
    draw.rectangle((0, 0, sheet_w, 70), fill=(18, 22, 28))
    draw.text((28, 12), "ASTRA HAZARD // HARDWARE TACTICO DE ESTACION & MISION", fill=(25, 200, 240), font=font_sub)
    draw.text((28, 30), "HARDWARE TACTICO AVANZADO // SISTEMAS DE COMANDO, ESTASIS & LOGISTICA 100% 3D", fill=(255, 255, 255), font=font_main)
    
    # Badges
    badges = [("6 SISTEMAS OFICIALES", (25, 200, 240)), ("4 BASE + 2 NUEVOS", (245, 175, 25)), ("CEL-SHADING COMIC", (180, 80, 240)), ("BLENDER 5.2 LTS", (80, 120, 255))]
    bx = sheet_w - 28
    for btext, bcol in reversed(badges):
        tw = len(btext) * 8 + 20
        bx -= tw + 10
        draw.rounded_rectangle((bx, 20, bx + tw, 48), radius=5, fill=bcol)
        draw.text((bx + 10, 27), btext, fill=(10, 10, 15), font=font_pill)
        
    # Render del puente de comando en la mitad superior
    if os.path.exists(deck_render_path):
        deck_img = Image.open(deck_render_path).convert("RGBA")
        d_thumb = deck_img.resize((2504, 630), Image.Resampling.LANCZOS)
        canvas.paste(d_thumb, (28, 85))
        draw.rectangle((28, 85, 2532, 715), outline=(50, 60, 75), width=2)
        
    # Grid de 6 tarjetas tecnicas en la mitad inferior (3 columnas x 2 filas)
    grid_start_y = 730
    card_w = 824
    card_h = 335
    gap_x = 16
    gap_y = 12
    
    for idx, (hid, hname, htitle, hdesc) in enumerate(HARDWARE_DATA):
        c_col = idx % 3
        c_row = idx // 3
        cx = 28 + c_col * (card_w + gap_x)
        cy = grid_start_y + c_row * (card_h + gap_y)
        
        # Tarjeta
        draw.rounded_rectangle((cx, cy, cx + card_w, cy + card_h), radius=6, fill=(20, 25, 32), outline=(42, 50, 62), width=1)
        
        # Thumbnail render close-up (Lado izquierdo)
        c_img_path = closeups.get(hid)
        if c_img_path and os.path.exists(c_img_path):
            c_img = Image.open(c_img_path).convert("RGBA")
            thumb = c_img.resize((280, 290), Image.Resampling.LANCZOS)
            canvas.paste(thumb, (cx + 8, cy + 8))
            draw.rectangle((cx + 8, cy + 8, cx + 288, cy + 298), outline=(40, 48, 58), width=1)
            
        # Contenido textual (Lado derecho)
        tx = cx + 302
        tag_color = (25, 200, 240) if hid <= 4 else (245, 175, 25)
        draw.text((tx, cy + 18), f"SISTEMA HW0{hid} // {'SISTEMA BASE REVISADO' if hid<=4 else 'NUEVO DISPOSITIVO TACTICO'}", fill=tag_color, font=font_card_sub)
        draw.text((tx, cy + 38), htitle, fill=(255, 255, 255), font=font_card_title)
        draw.line([(tx, cy + 64), (cx + card_w - 12, cy + 64)], fill=(45, 52, 65), width=1)
        
        words = hdesc.split(" ")
        lines = []
        cur_line = ""
        for w in words:
            if len(cur_line + " " + w) > 42:
                lines.append(cur_line.strip())
                cur_line = w
            else:
                cur_line += " " + w
        if cur_line:
            lines.append(cur_line.strip())
            
        ly = cy + 76
        for line in lines[:4]:
            draw.text((tx, ly), line, fill=(175, 190, 205), font=font_card_desc)
            ly += 22
            
        # Estado pill
        draw.rounded_rectangle((tx, cy + card_h - 38, cx + card_w - 12, cy + card_h - 14), radius=4, fill=(15, 18, 24))
        draw.text((tx + 10, cy + card_h - 32), "ESTADO: VERIFICADO & CERTIFICADO 100% 3D", fill=tag_color, font=font_pill)

    master_path = os.path.join(abs_style.RENDERS_DIR, "Showcase_Hardware_Tactico_Expandido_Master.png")
    canvas.save(master_path)
    print(f"[+] Lamina Maestra Hardware Tactico generada: {master_path}")
    shutil.copy2(master_path, os.path.join(abs_style.ARTIFACT_DIR, "Showcase_Hardware_Tactico_Expandido_Master.png"))
    
    # Tambien guardar con el alias Showcase_Hardware_Tactico_5_Master.png para total compatibilidad
    alias_path = os.path.join(abs_style.RENDERS_DIR, "Showcase_Hardware_Tactico_5_Master.png")
    canvas.save(alias_path)
    shutil.copy2(alias_path, os.path.join(abs_style.ARTIFACT_DIR, "Showcase_Hardware_Tactico_5_Master.png"))

def generate_hardware_scene(save_blend=True):
    abs_style.reset_comic_scene(bg_color=(0.10, 0.12, 0.16, 1.0), bg_strength=1.2, ink_thickness=1.4)
    col = abs_style.create_collection("Hardware_Tactico_Expandido")
    mats = init_hardware_materials()

    # Grid de 3 columnas x 2 filas en el Puente de Mando
    spacing_x = 3.6
    spacing_y = 3.8
    ped_mat = abs_style.get_comic_material("Pedestal_HW", base_color=(0.14, 0.16, 0.20), roughness=0.35, metallic=0.75, tex_pack="T_Steel_Plates")
    border_mat = abs_style.get_comic_material("Hazard_Border_HW", base_color=(0.15, 0.85, 0.95), roughness=0.35, metallic=0.10)
    plaque_mat = abs_style.get_comic_material("Plaque_Brass_HW", base_color=(0.92, 0.74, 0.22), roughness=0.22, metallic=0.92)

    closeups = {}

    for idx, (hid, hname, _, _) in enumerate(HARDWARE_DATA):
        col_idx = idx % 3
        row_idx = idx // 3
        x = (col_idx - 1.0) * spacing_x
        y = (row_idx - 0.5) * spacing_y

        # Pedestal tecnologico octogonal/cuadrado con reborde de luz
        abs_style.create_box(f"Pedestal_{hname}", size=(3.0, 3.0, 0.25), loc=(x, y, 0.125), mat=ped_mat, col=col)
        abs_style.create_box(f"BorderF_{hname}", size=(3.05, 0.05, 0.05), loc=(x, y - 1.5, 0.25), mat=border_mat, col=col)
        abs_style.create_box(f"Plaque_{hname}", size=(1.4, 0.08, 0.12), rot=(math.radians(30), 0, 0), loc=(x, y - 1.45, 0.22), mat=plaque_mat, col=col)
        
        # Construir dispositivo
        build_hardware_device(hid, hname, (x, y, 0.25), col, mats)

    # Entorno del Puente de Mando (Paredes, suelo de placas y vigas)
    floor_mat = abs_style.get_comic_material("HW_Floor", base_color=(0.12, 0.14, 0.18), roughness=0.30, metallic=0.85, tex_pack="T_Decayed_Rusted_Grating")
    abs_style.create_box("HWFloor", size=(22.0, 16.0, 0.2), loc=(0, 0, -0.1), mat=floor_mat, col=col)
    
    wall_mat = abs_style.get_comic_material("HW_Wall", base_color=(0.15, 0.17, 0.22), roughness=0.45, metallic=0.75, tex_pack="T_Steel_Plates")
    abs_style.create_box("HWWallBack", size=(22.0, 0.3, 6.0), loc=(0, 5.5, 2.9), mat=wall_mat, col=col)

    # Iluminacion de puente
    sun_data = bpy.data.lights.new(name="Light_Sun_HW", type='SUN')
    sun_data.energy = 4.8
    sun_data.color = (1.0, 0.98, 0.95)
    sun_obj = bpy.data.objects.new("Light_Sun_HW", sun_data)
    sun_obj.rotation_euler = (math.radians(48), math.radians(12), math.radians(-30))
    col.objects.link(sun_obj)

    fill_data = bpy.data.lights.new(name="Light_Fill_HW", type='SUN')
    fill_data.energy = 2.4
    fill_data.color = (0.85, 0.92, 1.0)
    fill_obj = bpy.data.objects.new("Light_Fill_HW", fill_data)
    fill_obj.rotation_euler = (math.radians(25), math.radians(-25), math.radians(45))
    col.objects.link(fill_obj)

    # Camara Panoramica 3/4 Heroica del Puente de Mando
    abs_style.setup_camera(name="Camera_Hardware_Deck", loc=(5.5, -9.5, 6.2), target=(0, 0.5, 1.5), focal_length=32)

    if save_blend:
        blend_path = os.path.join(abs_style.PROJECT_ROOT, "Art", "Blender", "Hardware_Tactico_Expandido_Oficial.blend")
        bpy.ops.wm.save_as_mainfile(filepath=blend_path)
        print(f"[+] Hardware Blend saved: {blend_path}")

    deck_render_path = os.path.join(abs_style.RENDERS_DIR, "Showcase_Hardware_Tactico_Expandido_Panorama.png")
    abs_style.render_and_save("Showcase_Hardware_Tactico_Expandido_Panorama.png", res_x=2560, res_y=1440)
    
    # Renderizar close-ups individuales de los 6 dispositivos en perspectiva 3/4 calibrada
    HW_CAMERAS = {
        1: {"offset": (2.8, -4.0, 2.4), "target_z": 1.4, "focal": 33},  # Pod Cryo (alto 2.8m)
        2: {"offset": (2.4, -3.0, 2.0), "target_z": 0.9, "focal": 36},  # Holo Table
        3: {"offset": (1.4, -1.8, 1.2), "target_z": 0.6, "focal": 46},  # Wrist PDA Scanner
        4: {"offset": (2.6, -3.6, 2.2), "target_z": 1.2, "focal": 34},  # Signal Repeater (mástil alto)
        5: {"offset": (2.6, -3.4, 2.0), "target_z": 1.3, "focal": 36},  # Drone Dock
        6: {"offset": (2.6, -3.5, 2.2), "target_z": 1.2, "focal": 35},  # Purification Pylon (torre alta)
    }

    for idx, (hid, hname, _, _) in enumerate(HARDWARE_DATA):
        col_idx = idx % 3
        row_idx = idx // 3
        x = (col_idx - 1.0) * spacing_x
        y = (row_idx - 0.5) * spacing_y
        
        cam_cfg = HW_CAMERAS.get(hid, {"offset": (2.4, -3.0, 2.0), "target_z": 1.0, "focal": 38})
        off_x, off_y, off_z = cam_cfg["offset"]
        t_z = cam_cfg["target_z"]
        foc = cam_cfg["focal"]
        
        abs_style.setup_camera(name=f"Cam_Close_{hname}", loc=(x + off_x, y + off_y, off_z), target=(x, y, t_z), focal_length=foc)
        close_file = f"CloseUp_{hname}.png"
        abs_style.render_and_save(close_file, res_x=800, res_y=800)
        closeups[hid] = os.path.join(abs_style.RENDERS_DIR, close_file)

    # Componer Lamina Maestra Tecnica 2.5K
    generate_hardware_technical_sheet(deck_render_path, closeups)
    print("[+] Suite Oficial de Hardware Tactico Renderizada y Compuesta al 100%!")

if __name__ == "__main__":
    generate_hardware_scene()

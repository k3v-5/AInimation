# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Arsenal Oficial de 20 Armas y Herramientas de Bombero Espacial - Astra Hazard
# Blender 5.2 LTS - Shaders Stylized PBR, Cel-Shading, Dial Delineation y Freestyle Ink Lineart

import bpy
import bmesh
import math
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

import astra_blender_styling as abs_style

def init_weapons_materials():
    mats = {}
    mats['hazard_yellow'] = abs_style.get_comic_material("W_Hazard_Yellow", base_color=(0.96, 0.68, 0.08), roughness=0.32, metallic=0.15, tex_pack="T_Trim_Industrial")
    mats['safety_orange'] = abs_style.get_comic_material("W_Safety_Orange", base_color=(0.95, 0.35, 0.05), roughness=0.35, metallic=0.10)
    mats['gunmetal'] = abs_style.get_comic_material("W_Gunmetal", base_color=(0.20, 0.22, 0.26), roughness=0.35, metallic=0.88, tex_pack="T_Steel_Plates")
    mats['steel_bright'] = abs_style.get_comic_material("W_Steel_Bright", base_color=(0.80, 0.84, 0.88), roughness=0.18, metallic=0.95)
    mats['brass_gold'] = abs_style.get_comic_material("W_Brass_Gold", base_color=(0.92, 0.74, 0.22), roughness=0.22, metallic=0.90, tex_pack="T_Luxury_ArtDeco_Gilded_Brass")
    mats['copper'] = abs_style.get_comic_material("W_Copper", base_color=(0.95, 0.45, 0.22), roughness=0.25, metallic=0.92)
    mats['carbon_fiber'] = abs_style.get_comic_material("W_Carbon_Fiber", base_color=(0.08, 0.09, 0.10), roughness=0.55, metallic=0.25)
    mats['rubber_grip'] = abs_style.get_comic_material("W_Rubber_Grip", base_color=(0.10, 0.10, 0.12), roughness=0.85, metallic=0.0)
    mats['fire_ext_red'] = abs_style.get_comic_material("W_Fire_Ext_Red", base_color=(0.88, 0.10, 0.08), roughness=0.28, metallic=0.25)
    
    # Materiales emisivos
    mats['plasma_orange'] = abs_style.get_comic_material("W_Plasma_Orange", base_color=(1.0, 0.45, 0.05), roughness=0.10,
                                                          emissive_color=(1.0, 0.45, 0.05, 1.0), emissive_strength=3.0)
    mats['cryo_cyan'] = abs_style.get_comic_material("W_Cryo_Cyan", base_color=(0.05, 0.90, 1.0), roughness=0.08,
                                                     emissive_color=(0.05, 0.90, 1.0, 1.0), emissive_strength=3.2)
    mats['emp_blue'] = abs_style.get_comic_material("W_EMP_Blue", base_color=(0.15, 0.45, 1.0), roughness=0.10,
                                                    emissive_color=(0.15, 0.45, 1.0, 1.0), emissive_strength=3.5)
    mats['acid_green'] = abs_style.get_comic_material("W_Acid_Green", base_color=(0.15, 0.95, 0.20), roughness=0.10,
                                                      emissive_color=(0.15, 0.95, 0.20, 1.0), emissive_strength=2.8)
    mats['gauge_white'] = abs_style.get_comic_material("W_Gauge_White", base_color=(0.92, 0.92, 0.88), roughness=0.3, metallic=0.0)
    return mats

def build_weapon(weapon_id, name, origin, col, mats):
    root = bpy.data.objects.new(f"Root_{name}", None)
    root.location = (0, 0, 0)
    col.objects.link(root)
    ox, oy, oz = origin

    if weapon_id == 1: # W01_Hydra_Heavy_Hose
        body = abs_style.create_cylinder(f"{name}_Barrel", radius=0.12, depth=1.6, rot=(math.radians(90), 0, 0), loc=(ox, oy, oz + 0.9), mat=mats['hazard_yellow'], col=col)
        body.parent = root
        nozzle = abs_style.create_cone(f"{name}_Nozzle", radius1=0.18, radius2=0.08, depth=0.4, rot=(math.radians(90), 0, 0), loc=(ox, oy - 0.95, oz + 0.9), mat=mats['brass_gold'], col=col)
        nozzle.parent = root
        handle_f = abs_style.create_torus(f"{name}_HandleF", major_r=0.18, minor_r=0.035, rot=(0, math.radians(90), 0), loc=(ox, oy - 0.3, oz + 1.1), mat=mats['rubber_grip'], col=col)
        handle_f.parent = root
        handle_r = abs_style.create_cylinder(f"{name}_HandleR", radius=0.04, depth=0.35, loc=(ox, oy + 0.5, oz + 0.7), mat=mats['rubber_grip'], col=col)
        handle_r.parent = root
        gauge = abs_style.create_cylinder(f"{name}_Gauge", radius=0.09, depth=0.05, rot=(0, 0, 0), loc=(ox, oy + 0.2, oz + 1.05), mat=mats['brass_gold'], col=col)
        gauge.parent = root
        gauge_dial = abs_style.create_cylinder(f"{name}_Dial", radius=0.075, depth=0.02, loc=(ox, oy + 0.2, oz + 1.08), mat=mats['gauge_white'], col=col)
        gauge_dial.parent = root

    elif weapon_id == 2: # W02_Thermal_Shock_Axe
        shaft = abs_style.create_cylinder(f"{name}_Shaft", radius=0.035, depth=1.2, loc=(ox, oy, oz + 0.6), mat=mats['carbon_fiber'], col=col)
        shaft.parent = root
        head = abs_style.create_box(f"{name}_Head", size=(0.12, 0.45, 0.25), loc=(ox, oy, oz + 1.15), mat=mats['gunmetal'], col=col)
        head.parent = root
        edge = abs_style.create_box(f"{name}_ThermalEdge", size=(0.04, 0.22, 0.28), loc=(ox, oy - 0.25, oz + 1.15), mat=mats['plasma_orange'], col=col)
        edge.parent = root
        pick = abs_style.create_cone(f"{name}_Spike", radius1=0.06, radius2=0.0, depth=0.25, rot=(0, math.radians(90), 0), loc=(ox, oy + 0.25, oz + 1.15), mat=mats['gunmetal'], col=col)
        pick.parent = root
        pommel = abs_style.create_cylinder(f"{name}_BatteryPommel", radius=0.055, depth=0.18, loc=(ox, oy, oz + 0.1), mat=mats['hazard_yellow'], col=col)
        pommel.parent = root

    elif weapon_id == 3: # W03_Cryo_CO2_Extinguisher
        tank = abs_style.create_cylinder(f"{name}_Tank", radius=0.22, depth=0.9, loc=(ox, oy, oz + 0.65), mat=mats['fire_ext_red'], col=col)
        tank.parent = root
        valve = abs_style.create_box(f"{name}_ValveHead", size=(0.12, 0.16, 0.15), loc=(ox, oy, oz + 1.18), mat=mats['brass_gold'], col=col)
        valve.parent = root
        horn = abs_style.create_cone(f"{name}_Horn", radius1=0.16, radius2=0.05, depth=0.55, rot=(math.radians(35), 0, 0), loc=(ox, oy - 0.25, oz + 0.95), mat=mats['carbon_fiber'], col=col)
        horn.parent = root
        dial = abs_style.create_cylinder(f"{name}_Dial", radius=0.05, depth=0.03, rot=(math.radians(90), 0, 0), loc=(ox, oy - 0.1, oz + 1.18), mat=mats['gauge_white'], col=col)
        dial.parent = root

    elif weapon_id == 4: # W04_Bio_Defibrillator_Unit
        box_u = abs_style.create_box(f"{name}_Case", size=(0.6, 0.45, 0.25), loc=(ox, oy, oz + 0.8), mat=mats['hazard_yellow'], col=col)
        box_u.parent = root
        screen = abs_style.create_box(f"{name}_ECGDisplay", size=(0.35, 0.02, 0.16), loc=(ox, oy - 0.23, oz + 0.8), mat=mats['acid_green'], col=col)
        screen.parent = root
        paddle_l = abs_style.create_box(f"{name}_PaddleL", size=(0.14, 0.14, 0.18), loc=(ox - 0.4, oy, oz + 0.8), mat=mats['gunmetal'], col=col)
        paddle_l.parent = root
        paddle_r = abs_style.create_box(f"{name}_PaddleR", size=(0.14, 0.14, 0.18), loc=(ox + 0.4, oy, oz + 0.8), mat=mats['gunmetal'], col=col)
        paddle_r.parent = root

    elif weapon_id == 5: # W05_Plasma_Halligan_Bar
        bar = abs_style.create_cylinder(f"{name}_Bar", radius=0.03, depth=1.3, loc=(ox, oy, oz + 0.65), mat=mats['gunmetal'], col=col)
        bar.parent = root
        adze = abs_style.create_box(f"{name}_Adze", size=(0.04, 0.25, 0.15), loc=(ox, oy - 0.12, oz + 1.25), mat=mats['plasma_orange'], col=col)
        adze.parent = root
        fork = abs_style.create_box(f"{name}_Fork", size=(0.04, 0.16, 0.2), loc=(ox, oy, oz + 0.1), mat=mats['plasma_orange'], col=col)
        fork.parent = root

    elif weapon_id == 6: # W06_Rotary_Rescue_Saw
        engine = abs_style.create_box(f"{name}_Motor", size=(0.35, 0.65, 0.35), loc=(ox, oy + 0.2, oz + 0.8), mat=mats['safety_orange'], col=col)
        engine.parent = root
        arm = abs_style.create_box(f"{name}_BladeArm", size=(0.08, 0.5, 0.12), loc=(ox, oy - 0.35, oz + 0.8), mat=mats['gunmetal'], col=col)
        arm.parent = root
        blade = abs_style.create_cylinder(f"{name}_DiamondBlade", radius=0.35, depth=0.02, rot=(0, math.radians(90), 0), loc=(ox, oy - 0.65, oz + 0.8), mat=mats['steel_bright'], col=col)
        blade.parent = root
        guard = abs_style.create_cylinder(f"{name}_SparkGuard", radius=0.38, depth=0.05, rot=(0, math.radians(90), 0), loc=(ox, oy - 0.65, oz + 0.8), mat=mats['safety_orange'], col=col)
        guard.parent = root

    elif weapon_id == 7: # W07_Pneumatic_Bolt_Cutter
        jaw_l = abs_style.create_box(f"{name}_JawL", size=(0.05, 0.18, 0.25), loc=(ox - 0.05, oy - 0.5, oz + 0.8), mat=mats['steel_bright'], col=col)
        jaw_l.parent = root
        jaw_r = abs_style.create_box(f"{name}_JawR", size=(0.05, 0.18, 0.25), loc=(ox + 0.05, oy - 0.5, oz + 0.8), mat=mats['steel_bright'], col=col)
        jaw_r.parent = root
        piston = abs_style.create_cylinder(f"{name}_AirRam", radius=0.1, depth=0.7, rot=(math.radians(90), 0, 0), loc=(ox, oy, oz + 0.8), mat=mats['hazard_yellow'], col=col)
        piston.parent = root

    elif weapon_id == 8: # W08_Chemical_Foam_Mortar
        barrel = abs_style.create_cylinder(f"{name}_MortarTube", radius=0.16, depth=1.2, rot=(math.radians(90), 0, 0), loc=(ox, oy, oz + 0.8), mat=mats['hazard_yellow'], col=col)
        barrel.parent = root
        drum = abs_style.create_cylinder(f"{name}_RotaryDrum", radius=0.25, depth=0.35, loc=(ox, oy + 0.2, oz + 0.8), mat=mats['gunmetal'], col=col)
        drum.parent = root
        stock = abs_style.create_box(f"{name}_Stock", size=(0.12, 0.45, 0.25), loc=(ox, oy + 0.65, oz + 0.75), mat=mats['carbon_fiber'], col=col)
        stock.parent = root

    elif weapon_id == 9: # W09_Thermal_Lance_Cutter
        lance = abs_style.create_cylinder(f"{name}_LanceRod", radius=0.03, depth=1.8, rot=(math.radians(90), 0, 0), loc=(ox, oy, oz + 0.8), mat=mats['steel_bright'], col=col)
        lance.parent = root
        tip = abs_style.create_cylinder(f"{name}_FlameTip", radius=0.045, depth=0.35, rot=(math.radians(90), 0, 0), loc=(ox, oy - 0.95, oz + 0.8), mat=mats['plasma_orange'], col=col)
        tip.parent = root
        shield = abs_style.create_cone(f"{name}_HeatShield", radius1=0.25, radius2=0.05, depth=0.2, rot=(math.radians(90), 0, 0), loc=(ox, oy - 0.3, oz + 0.8), mat=mats['carbon_fiber'], col=col)
        shield.parent = root

    elif weapon_id == 10: # W10_EMP_Disruptor_Pistol
        receiver = abs_style.create_box(f"{name}_Receiver", size=(0.14, 0.5, 0.22), loc=(ox, oy, oz + 0.8), mat=mats['gunmetal'], col=col)
        receiver.parent = root
        grip = abs_style.create_box(f"{name}_Grip", size=(0.1, 0.16, 0.3), rot=(math.radians(15), 0, 0), loc=(ox, oy + 0.15, oz + 0.6), mat=mats['rubber_grip'], col=col)
        grip.parent = root
        for i in range(4):
            ring = abs_style.create_torus(f"{name}_EMPRing_{i}", major_r=0.12, minor_r=0.025, rot=(math.radians(90), 0, 0), loc=(ox, oy - 0.1 - i*0.1, oz + 0.8), mat=mats['copper'], col=col)
            ring.parent = root
        core = abs_style.create_cylinder(f"{name}_EMPBeam", radius=0.04, depth=0.55, rot=(math.radians(90), 0, 0), loc=(ox, oy - 0.25, oz + 0.8), mat=mats['emp_blue'], col=col)
        core.parent = root

    elif weapon_id == 11: # W11_Shock_Spreader_Jaws
        body = abs_style.create_box(f"{name}_Body", size=(0.3, 0.6, 0.3), loc=(ox, oy + 0.2, oz + 0.8), mat=mats['hazard_yellow'], col=col)
        body.parent = root
        arm_l = abs_style.create_box(f"{name}_SpreaderL", size=(0.08, 0.55, 0.15), rot=(0, 0, math.radians(20)), loc=(ox - 0.15, oy - 0.35, oz + 0.8), mat=mats['steel_bright'], col=col)
        arm_l.parent = root
        arm_r = abs_style.create_box(f"{name}_SpreaderR", size=(0.08, 0.55, 0.15), rot=(0, 0, -math.radians(20)), loc=(ox + 0.15, oy - 0.35, oz + 0.8), mat=mats['steel_bright'], col=col)
        arm_r.parent = root

    elif weapon_id == 12: # W12_Cryo_Grenade_Launcher
        frame = abs_style.create_box(f"{name}_Frame", size=(0.2, 0.7, 0.3), loc=(ox, oy, oz + 0.8), mat=mats['gunmetal'], col=col)
        frame.parent = root
        cluster = abs_style.create_cylinder(f"{name}_4Breech", radius=0.22, depth=0.45, rot=(math.radians(90), 0, 0), loc=(ox, oy - 0.1, oz + 0.8), mat=mats['hazard_yellow'], col=col)
        cluster.parent = root
        barrel = abs_style.create_cylinder(f"{name}_CryoMuzzle", radius=0.15, depth=0.5, rot=(math.radians(90), 0, 0), loc=(ox, oy - 0.5, oz + 0.8), mat=mats['cryo_cyan'], col=col)
        barrel.parent = root

    elif weapon_id == 13: # W13_Pneumatic_Ram_Battering
        ram_body = abs_style.create_cylinder(f"{name}_RamCylinder", radius=0.16, depth=1.5, rot=(math.radians(90), 0, 0), loc=(ox, oy, oz + 0.8), mat=mats['hazard_yellow'], col=col)
        ram_body.parent = root
        ram_head = abs_style.create_cylinder(f"{name}_RamHead", radius=0.22, depth=0.2, rot=(math.radians(90), 0, 0), loc=(ox, oy - 0.8, oz + 0.8), mat=mats['steel_bright'], col=col)
        ram_head.parent = root
        grip_f = abs_style.create_torus(f"{name}_GripF", major_r=0.22, minor_r=0.035, loc=(ox, oy - 0.2, oz + 0.8), mat=mats['rubber_grip'], col=col)
        grip_f.parent = root
        grip_r = abs_style.create_torus(f"{name}_GripR", major_r=0.22, minor_r=0.035, loc=(ox, oy + 0.4, oz + 0.8), mat=mats['rubber_grip'], col=col)
        grip_r.parent = root

    elif weapon_id == 14: # W14_Electromagnetic_Net_Caster
        chassis = abs_style.create_box(f"{name}_Chassis", size=(0.22, 0.6, 0.25), loc=(ox, oy, oz + 0.8), mat=mats['carbon_fiber'], col=col)
        chassis.parent = root
        for i in range(5):
            ang = i * (2 * math.pi / 5)
            nx = ox + math.cos(ang) * 0.16
            nz = oz + 0.8 + math.sin(ang) * 0.16
            tube = abs_style.create_cylinder(f"{name}_Tube_{i}", radius=0.05, depth=0.45, rot=(math.radians(90), 0, 0), loc=(nx, oy - 0.45, nz), mat=mats['copper'], col=col)
            tube.parent = root

    elif weapon_id == 15: # W15_Corrosive_Neutralizer_Sprayer
        tank_l = abs_style.create_cylinder(f"{name}_TankAcid", radius=0.15, depth=0.8, loc=(ox - 0.2, oy + 0.3, oz + 0.7), mat=mats['hazard_yellow'], col=col)
        tank_l.parent = root
        tank_r = abs_style.create_cylinder(f"{name}_TankBase", radius=0.15, depth=0.8, loc=(ox + 0.2, oy + 0.3, oz + 0.7), mat=mats['acid_green'], col=col)
        tank_r.parent = root
        gun = abs_style.create_cylinder(f"{name}_SprayLance", radius=0.04, depth=1.0, rot=(math.radians(90), 0, 0), loc=(ox, oy - 0.3, oz + 0.8), mat=mats['gunmetal'], col=col)
        gun.parent = root

    elif weapon_id == 16: # W16_Magnesium_Flare_Launcher
        bell = abs_style.create_cone(f"{name}_BellMuzzle", radius1=0.18, radius2=0.08, depth=0.45, rot=(math.radians(90), 0, 0), loc=(ox, oy - 0.3, oz + 0.8), mat=mats['brass_gold'], col=col)
        bell.parent = root
        frame = abs_style.create_box(f"{name}_Frame", size=(0.12, 0.35, 0.2), loc=(ox, oy, oz + 0.8), mat=mats['safety_orange'], col=col)
        frame.parent = root
        grip = abs_style.create_box(f"{name}_Grip", size=(0.08, 0.15, 0.25), rot=(math.radians(20), 0, 0), loc=(ox, oy + 0.15, oz + 0.65), mat=mats['safety_orange'], col=col)
        grip.parent = root

    elif weapon_id == 17: # W17_Sonic_Fire_Suppressor
        horn = abs_style.create_cone(f"{name}_SonicHorn", radius1=0.35, radius2=0.1, depth=0.7, rot=(math.radians(90), 0, 0), loc=(ox, oy - 0.4, oz + 0.8), mat=mats['gunmetal'], col=col)
        horn.parent = root
        emitter = abs_style.create_cylinder(f"{name}_CoreTransducer", radius=0.14, depth=0.5, rot=(math.radians(90), 0, 0), loc=(ox, oy + 0.15, oz + 0.8), mat=mats['emp_blue'], col=col)
        emitter.parent = root

    elif weapon_id == 18: # W18_Arc_Welder_Rescue_Torch
        handle = abs_style.create_cylinder(f"{name}_Handle", radius=0.05, depth=0.5, loc=(ox, oy, oz + 0.6), mat=mats['carbon_fiber'], col=col)
        handle.parent = root
        head = abs_style.create_cylinder(f"{name}_TorchHead", radius=0.06, depth=0.3, rot=(math.radians(60), 0, 0), loc=(ox, oy - 0.1, oz + 0.95), mat=mats['copper'], col=col)
        head.parent = root
        arc = abs_style.create_cone(f"{name}_ArcSpike", radius1=0.02, radius2=0.0, depth=0.15, rot=(math.radians(60), 0, 0), loc=(ox, oy - 0.22, oz + 1.05), mat=mats['emp_blue'], col=col)
        arc.parent = root

    elif weapon_id == 19: # W19_High_Pressure_Foam_Cannon
        cannon = abs_style.create_cylinder(f"{name}_Barrel", radius=0.2, depth=1.6, rot=(math.radians(90), 0, 0), loc=(ox, oy, oz + 1.1), mat=mats['hazard_yellow'], col=col)
        cannon.parent = root
        tripod_hub = abs_style.create_cylinder(f"{name}_Hub", radius=0.25, depth=0.2, loc=(ox, oy, oz + 0.8), mat=mats['gunmetal'], col=col)
        tripod_hub.parent = root
        for i in range(3):
            ang = i * (2 * math.pi / 3)
            leg = abs_style.create_cylinder(f"{name}_Leg_{i}", radius=0.06, depth=1.0, rot=(math.radians(35) * math.cos(ang), math.radians(35) * math.sin(ang), 0), loc=(ox + math.sin(ang)*0.4, oy + math.cos(ang)*0.4, oz + 0.4), mat=mats['steel_bright'], col=col)
            leg.parent = root

    elif weapon_id == 20: # W20_Tactical_Rescue_Machete
        blade = abs_style.create_box(f"{name}_Blade", size=(0.03, 0.8, 0.14), loc=(ox, oy - 0.35, oz + 0.8), mat=mats['gunmetal'], col=col)
        blade.parent = root
        serration = abs_style.create_box(f"{name}_Teeth", size=(0.04, 0.4, 0.05), loc=(ox, oy - 0.35, oz + 0.88), mat=mats['steel_bright'], col=col)
        serration.parent = root
        handle = abs_style.create_cylinder(f"{name}_Grip", radius=0.035, depth=0.28, rot=(math.radians(90), 0, 0), loc=(ox, oy + 0.2, oz + 0.8), mat=mats['rubber_grip'], col=col)
        handle.parent = root

    return root

WEAPONS_20 = [
    (1, "W01_Hydra_Heavy_Hose"),
    (2, "W02_Thermal_Shock_Axe"),
    (3, "W03_Cryo_CO2_Extinguisher"),
    (4, "W04_Bio_Defibrillator_Unit"),
    (5, "W05_Plasma_Halligan_Bar"),
    (6, "W06_Rotary_Rescue_Saw"),
    (7, "W07_Pneumatic_Bolt_Cutter"),
    (8, "W08_Chemical_Foam_Mortar"),
    (9, "W09_Thermal_Lance_Cutter"),
    (10, "W10_EMP_Disruptor_Pistol"),
    (11, "W11_Shock_Spreader_Jaws"),
    (12, "W12_Cryo_Grenade_Launcher"),
    (13, "W13_Pneumatic_Ram_Battering"),
    (14, "W14_Electromagnetic_Net_Caster"),
    (15, "W15_Corrosive_Neutralizer_Sprayer"),
    (16, "W16_Magnesium_Flare_Launcher"),
    (17, "W17_Sonic_Fire_Suppressor"),
    (18, "W18_Arc_Welder_Rescue_Torch"),
    (19, "W19_High_Pressure_Foam_Cannon"),
    (20, "W20_Tactical_Rescue_Machete"),
]

def generate_weapons_scene(save_blend=True):
    abs_style.reset_comic_scene(bg_color=(0.015, 0.02, 0.028, 1.0), bg_strength=0.4, ink_thickness=1.6)
    col = abs_style.create_collection("Arsenal_Armas_20_Oficial")
    mats = init_weapons_materials()
    
    # Grid de 10 columnas x 2 filas
    spacing_x = 3.6
    spacing_y = 5.0
    ped_mat = abs_style.get_comic_material("Pedestal_Weapons", base_color=(0.07, 0.08, 0.10), roughness=0.35, metallic=0.7)
    plaque_mat = abs_style.get_comic_material("Plaque_Brass", base_color=(0.92, 0.74, 0.22), roughness=0.22, metallic=0.92)
    
    for idx, (wid, wname) in enumerate(WEAPONS_20):
        col_idx = idx % 10
        row_idx = idx // 10
        x = (col_idx - 4.5) * spacing_x
        y = (row_idx - 0.5) * spacing_y
        
        ped = abs_style.create_box(f"Pedestal_{wname}", size=(2.8, 2.8, 0.3), loc=(x, y, 0.15), mat=ped_mat, col=col)
        plaque = abs_style.create_box(f"Plaque_{wname}", size=(1.2, 0.08, 0.15), rot=(math.radians(30), 0, 0), loc=(x, y - 1.35, 0.22), mat=plaque_mat, col=col)
        build_weapon(wid, wname, (x, y, 0.3), col, mats)
        
    abs_style.setup_studio_lighting(sun_energy=3.8, rim_energy=2.4, fill_energy=1.2)
    
    # Suelo de exposición del arsenal
    floor_mat = abs_style.get_comic_material("Arsenal_Floor", base_color=(0.02, 0.025, 0.035), roughness=0.25, metallic=0.85)
    abs_style.create_box("ArmoryFloor", size=(60.0, 30.0, 0.2), loc=(0, 0, -0.1), mat=floor_mat, col=col)
    
    abs_style.setup_camera(name="Camera_Weapons", loc=(0, -20, 11), target=(0, 0, 0.6), focal_length=30)
    
    if save_blend:
        blend_path = os.path.join(abs_style.PROJECT_ROOT, "Art", "Blender", "Arsenal_Armas_20_Oficial.blend")
        bpy.ops.wm.save_as_mainfile(filepath=blend_path)
        print(f"[+] Arsenal Blend saved: {blend_path}")
        
    abs_style.render_and_save("Showcase_Arsenal_Armas_20_Master.png", res_x=2560, res_y=1440)
    
    # Renderizar closeups de las 4 armas principales de referencia
    for wid, wname in WEAPONS_20[:4]:
        col_idx = (wid - 1) % 10
        row_idx = (wid - 1) // 10
        x = (col_idx - 4.5) * spacing_x
        y = (row_idx - 0.5) * spacing_y
        abs_style.setup_camera(name=f"Cam_Close_{wname}", loc=(x, y - 3.2, 1.8), target=(x, y, 0.9), focal_length=45)
        abs_style.render_and_save(f"CloseUp_{wname}.png", res_x=1280, res_y=1280)
        
    print("[+] Render de Arsenal de 20 Armas y Closeups completado con exito!")

if __name__ == "__main__":
    generate_weapons_scene()

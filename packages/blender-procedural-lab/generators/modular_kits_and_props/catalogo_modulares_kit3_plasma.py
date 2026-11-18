# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Kit 3: Refineria de Plasma y Alta Tension (Activos 37 a 54 de 90)
# Blender 5.2 LTS - Modelado Parametrico, Shaders PBR Stylized y Freestyle Lineart

import bpy
import bmesh
import math
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

import astra_blender_styling as abs_style

def init_kit3_materials():
    mats = {}
    mats['dark_steel'] = abs_style.get_comic_material("K3_Plasma_DarkSteel", base_color=(0.16, 0.20, 0.25), roughness=0.35, metallic=0.85, tex_pack="T_Props_Machinery")
    mats['cyan_core'] = abs_style.get_comic_material("K3_Plasma_CyanCore", base_color=(0.0, 0.88, 1.0), roughness=0.08, metallic=0.0, emissive_color=(0.0, 0.90, 1.0, 1.0), emissive_strength=3.2)
    mats['copper'] = abs_style.get_comic_material("K3_Plasma_Copper", base_color=(0.95, 0.45, 0.22), roughness=0.28, metallic=0.92)
    mats['ceramic'] = abs_style.get_comic_material("K3_Insulator_Ceramic", base_color=(0.90, 0.88, 0.82), roughness=0.15, metallic=0.0)
    mats['hazard_yellow'] = abs_style.get_comic_material("K3_Hazard_Yellow", base_color=(0.95, 0.70, 0.08), roughness=0.35, metallic=0.10)
    mats['carbon'] = abs_style.get_comic_material("K3_Carbon_Shield", base_color=(0.07, 0.08, 0.09), roughness=0.60, metallic=0.20)
    mats['valve_red'] = abs_style.get_comic_material("K3_Valve_Red", base_color=(0.85, 0.12, 0.10), roughness=0.30, metallic=0.2)
    return mats

def build_asset(asset_id, name, origin, col, mats):
    root = bpy.data.objects.new(f"Root_{name}", None)
    root.location = (0, 0, 0)
    col.objects.link(root)
    
    ox, oy, oz = origin
    
    if asset_id == 37: # SM_Mod_37_Plasma_Reactor_Core_Chamber
        base = abs_style.create_cylinder(f"{name}_Base", radius=1.6, depth=0.6, loc=(ox, oy, oz + 0.3), mat=mats['dark_steel'], col=col)
        base.parent = root
        core = abs_style.create_cylinder(f"{name}_CyanCore", radius=1.1, depth=2.4, loc=(ox, oy, oz + 1.8), mat=mats['cyan_core'], col=col)
        core.parent = root
        for i in range(4):
            ang = i * (math.pi / 2)
            px = ox + math.cos(ang) * 1.5
            py = oy + math.sin(ang) * 1.5
            piston = abs_style.create_cylinder(f"{name}_Piston_{i}", radius=0.15, depth=2.4, loc=(px, py, oz + 1.8), mat=mats['copper'], col=col)
            piston.parent = root
        cap = abs_style.create_cylinder(f"{name}_Cap", radius=1.6, depth=0.5, loc=(ox, oy, oz + 3.25), mat=mats['dark_steel'], col=col)
        cap.parent = root

    elif asset_id == 38: # SM_Mod_38_Plasma_Magnetic_Confinement_Ring
        torus = abs_style.create_torus(f"{name}_Torus", major_r=1.5, minor_r=0.35, loc=(ox, oy, oz + 1.75), mat=mats['dark_steel'], col=col)
        torus.parent = root
        for a in range(8):
            ang = a * (math.pi / 4)
            px = ox + math.cos(ang) * 1.5
            py = oy + math.sin(ang) * 1.5
            coil = abs_style.create_torus(f"{name}_Coil_{a}", major_r=0.45, minor_r=0.08, rot=(math.radians(90), 0, ang), loc=(px, py, oz + 1.75), mat=mats['copper'], col=col)
            coil.parent = root
        core_plasma = abs_style.create_cylinder(f"{name}_Beam", radius=0.18, depth=3.5, loc=(ox, oy, oz + 1.75), mat=mats['cyan_core'], col=col)
        core_plasma.parent = root

    elif asset_id == 39: # SM_Mod_39_Plasma_Tesla_Discharge_Pylon
        base = abs_style.create_cylinder(f"{name}_Base", radius=0.8, depth=0.4, loc=(ox, oy, oz + 0.2), mat=mats['dark_steel'], col=col)
        base.parent = root
        for i in range(5):
            ring = abs_style.create_cylinder(f"{name}_Insulator_{i}", radius=0.55 - i*0.04, depth=0.25, loc=(ox, oy, oz + 0.6 + i*0.45), mat=mats['ceramic'], col=col)
            ring.parent = root
        top_sphere = abs_style.create_cylinder(f"{name}_TopElectrode", radius=0.6, depth=0.6, loc=(ox, oy, oz + 3.1), mat=mats['copper'], col=col)
        top_sphere.parent = root
        arc = abs_style.create_torus(f"{name}_ArcRing", major_r=0.75, minor_r=0.05, loc=(ox, oy, oz + 3.1), mat=mats['cyan_core'], col=col)
        arc.parent = root

    elif asset_id == 40: # SM_Mod_40_Plasma_HighVoltage_Transformer
        body = abs_style.create_box(f"{name}_Body", size=(2.2, 1.8, 2.0), loc=(ox, oy, oz + 1.2), mat=mats['dark_steel'], col=col)
        body.parent = root
        for fx in [-0.9, -0.45, 0.0, 0.45, 0.9]:
            fin = abs_style.create_box(f"{name}_FinL_{fx}", size=(0.04, 0.4, 1.8), loc=(ox + fx, oy - 1.05, oz + 1.2), mat=mats['copper'], col=col)
            fin.parent = root
        bushing1 = abs_style.create_cylinder(f"{name}_Bushing1", radius=0.15, depth=0.8, loc=(ox - 0.5, oy, oz + 2.5), mat=mats['ceramic'], col=col)
        bushing1.parent = root
        bushing2 = abs_style.create_cylinder(f"{name}_Bushing2", radius=0.15, depth=0.8, loc=(ox + 0.5, oy, oz + 2.5), mat=mats['ceramic'], col=col)
        bushing2.parent = root

    elif asset_id == 41: # SM_Mod_41_Plasma_Cryo_Cooling_Radiator
        frame = abs_style.create_box(f"{name}_Frame", size=(3.0, 0.8, 3.2), loc=(ox, oy, oz + 1.6), mat=mats['dark_steel'], col=col)
        frame.parent = root
        for i in range(7):
            tube = abs_style.create_cylinder(f"{name}_CryoTube_{i}", radius=0.08, depth=2.8, rot=(0, math.radians(90), 0), loc=(ox, oy, oz + 0.4 + i*0.4), mat=mats['cyan_core'], col=col)
            tube.parent = root

    elif asset_id == 42: # SM_Mod_42_Plasma_Capacitor_Bank_Rack
        rack = abs_style.create_box(f"{name}_Rack", size=(2.4, 1.0, 2.8), loc=(ox, oy, oz + 1.4), mat=mats['dark_steel'], col=col)
        rack.parent = root
        for row in [0.6, 1.4, 2.2]:
            for col_i in [-0.7, 0.0, 0.7]:
                cap = abs_style.create_cylinder(f"{name}_Cap_{row}_{col_i}", radius=0.22, depth=0.6, loc=(ox + col_i, oy - 0.2, oz + row), mat=mats['copper'], col=col)
                cap.parent = root
                led = abs_style.create_cylinder(f"{name}_LED_{row}_{col_i}", radius=0.04, depth=0.08, rot=(math.radians(90), 0, 0), loc=(ox + col_i, oy - 0.52, oz + row + 0.2), mat=mats['cyan_core'], col=col)
                led.parent = root

    elif asset_id == 43: # SM_Mod_43_Plasma_Insulated_Conduit_400cm
        conduit = abs_style.create_cylinder(f"{name}_Conduit", radius=0.35, depth=4.0, rot=(0, math.radians(90), 0), loc=(ox, oy, oz + 2.0), mat=mats['dark_steel'], col=col)
        conduit.parent = root
        for wx in [-1.2, 0.0, 1.2]:
            window = abs_style.create_box(f"{name}_GlowWindow_{wx}", size=(0.6, 0.72, 0.2), loc=(ox + wx, oy, oz + 2.0), mat=mats['cyan_core'], col=col)
            window.parent = root

    elif asset_id == 44: # SM_Mod_44_Plasma_Slag_Runoff_Channel
        trench = abs_style.create_box(f"{name}_Trench", size=(4.0, 1.4, 0.5), loc=(ox, oy, oz + 0.25), mat=mats['carbon'], col=col)
        trench.parent = root
        slag = abs_style.create_box(f"{name}_MoltenSlag", size=(3.9, 0.9, 0.2), loc=(ox, oy, oz + 0.2), mat=mats['cyan_core'], col=col)
        slag.parent = root
        curb = abs_style.create_box(f"{name}_HazardBorder", size=(4.0, 1.45, 0.1), loc=(ox, oy, oz + 0.52), mat=mats['hazard_yellow'], col=col)
        curb.parent = root

    elif asset_id == 45: # SM_Mod_45_Plasma_Beam_Focusing_Emitter
        pedestal = abs_style.create_box(f"{name}_Pedestal", size=(1.2, 1.2, 0.8), loc=(ox, oy, oz + 0.4), mat=mats['dark_steel'], col=col)
        pedestal.parent = root
        nozzle = abs_style.create_cone(f"{name}_Nozzle", radius1=0.6, radius2=0.2, depth=1.6, rot=(math.radians(90), 0, 0), loc=(ox, oy, oz + 1.4), mat=mats['dark_steel'], col=col)
        nozzle.parent = root
        lens = abs_style.create_cylinder(f"{name}_FocusLens", radius=0.25, depth=0.1, rot=(math.radians(90), 0, 0), loc=(ox, oy - 0.82, oz + 1.4), mat=mats['cyan_core'], col=col)
        lens.parent = root

    elif asset_id == 46: # SM_Mod_46_Plasma_Turbine_Generator_Housing
        housing = abs_style.create_cylinder(f"{name}_Turbine", radius=1.3, depth=3.0, rot=(0, math.radians(90), 0), loc=(ox, oy, oz + 1.5), mat=mats['dark_steel'], col=col)
        housing.parent = root
        flange_l = abs_style.create_torus(f"{name}_FlangeL", major_r=1.35, minor_r=0.08, rot=(0, math.radians(90), 0), loc=(ox - 1.2, oy, oz + 1.5), mat=mats['copper'], col=col)
        flange_l.parent = root
        flange_r = abs_style.create_torus(f"{name}_FlangeR", major_r=1.35, minor_r=0.08, rot=(0, math.radians(90), 0), loc=(ox + 1.2, oy, oz + 1.5), mat=mats['copper'], col=col)
        flange_r.parent = root

    elif asset_id == 47: # SM_Mod_47_Plasma_Control_Terminal_Console
        desk = abs_style.create_box(f"{name}_Desk", size=(2.0, 1.0, 0.9), loc=(ox, oy, oz + 0.45), mat=mats['dark_steel'], col=col)
        desk.parent = root
        console = abs_style.create_box(f"{name}_ConsoleTop", size=(1.8, 0.8, 0.6), rot=(math.radians(25), 0, 0), loc=(ox, oy + 0.1, oz + 1.1), mat=mats['dark_steel'], col=col)
        console.parent = root
        screen1 = abs_style.create_box(f"{name}_Screen1", size=(0.5, 0.05, 0.35), rot=(math.radians(25), 0, 0), loc=(ox - 0.55, oy - 0.25, oz + 1.2), mat=mats['cyan_core'], col=col)
        screen1.parent = root
        screen2 = abs_style.create_box(f"{name}_Screen2", size=(0.5, 0.05, 0.35), rot=(math.radians(25), 0, 0), loc=(ox + 0.55, oy - 0.25, oz + 1.2), mat=mats['cyan_core'], col=col)
        screen2.parent = root

    elif asset_id == 48: # SM_Mod_48_Plasma_Emergency_Dump_Vent
        pipe = abs_style.create_cylinder(f"{name}_VentStack", radius=0.4, depth=3.2, loc=(ox, oy, oz + 1.6), mat=mats['dark_steel'], col=col)
        pipe.parent = root
        vent_cap = abs_style.create_cone(f"{name}_VentCap", radius1=0.7, radius2=0.3, depth=0.5, loc=(ox, oy, oz + 3.3), mat=mats['hazard_yellow'], col=col)
        vent_cap.parent = root
        valve = abs_style.create_torus(f"{name}_ReliefValve", major_r=0.3, minor_r=0.06, rot=(math.radians(90), 0, 0), loc=(ox, oy - 0.42, oz + 1.5), mat=mats['valve_red'], col=col)
        valve.parent = root

    elif asset_id == 49: # SM_Mod_49_Plasma_Shielding_Tile_Wall
        wall = abs_style.create_box(f"{name}_Wall", size=(4.0, 0.4, 3.5), loc=(ox, oy, oz + 1.75), mat=mats['carbon'], col=col)
        wall.parent = root
        for tx in range(-3, 4):
            for tz in range(1, 5):
                tile = abs_style.create_box(f"{name}_Tile_{tx}_{tz}", size=(0.48, 0.42, 0.65), loc=(ox + tx*0.55, oy, oz + tz*0.7), mat=mats['dark_steel'], col=col)
                tile.parent = root

    elif asset_id == 50: # SM_Mod_50_Plasma_Magnetic_Valve_Manifold
        manifold = abs_style.create_cylinder(f"{name}_Header", radius=0.3, depth=2.8, rot=(0, math.radians(90), 0), loc=(ox, oy, oz + 1.4), mat=mats['dark_steel'], col=col)
        manifold.parent = root
        for sx in [-0.9, -0.3, 0.3, 0.9]:
            solenoid = abs_style.create_cylinder(f"{name}_Sol_{sx}", radius=0.18, depth=0.8, loc=(ox + sx, oy, oz + 1.9), mat=mats['copper'], col=col)
            solenoid.parent = root

    elif asset_id == 51: # SM_Mod_51_Plasma_Arc_Furnace_Crucible
        pot = abs_style.create_cylinder(f"{name}_Pot", radius=1.3, depth=1.8, loc=(ox, oy, oz + 1.1), mat=mats['dark_steel'], col=col)
        pot.parent = root
        bath = abs_style.create_cylinder(f"{name}_Melt", radius=1.1, depth=0.3, loc=(ox, oy, oz + 1.8), mat=mats['cyan_core'], col=col)
        bath.parent = root
        electrode = abs_style.create_cylinder(f"{name}_Electrode", radius=0.15, depth=1.6, loc=(ox, oy, oz + 2.4), mat=mats['carbon'], col=col)
        electrode.parent = root

    elif asset_id == 52: # SM_Mod_52_Plasma_Diagnostic_Sensor_Array
        post = abs_style.create_cylinder(f"{name}_Mast", radius=0.1, depth=2.6, loc=(ox, oy, oz + 1.3), mat=mats['dark_steel'], col=col)
        post.parent = root
        array = abs_style.create_box(f"{name}_SensorBox", size=(0.8, 0.5, 0.7), loc=(ox, oy, oz + 2.4), mat=mats['hazard_yellow'], col=col)
        array.parent = root
        sensor_eye = abs_style.create_cylinder(f"{name}_SpectroEye", radius=0.18, depth=0.1, rot=(math.radians(90), 0, 0), loc=(ox, oy - 0.26, oz + 2.4), mat=mats['cyan_core'], col=col)
        sensor_eye.parent = root

    elif asset_id == 53: # SM_Mod_53_Plasma_Safety_Interlock_Gate
        post_l = abs_style.create_cylinder(f"{name}_PostL", radius=0.2, depth=2.4, loc=(ox - 1.4, oy, oz + 1.2), mat=mats['hazard_yellow'], col=col)
        post_l.parent = root
        post_r = abs_style.create_cylinder(f"{name}_PostR", radius=0.2, depth=2.4, loc=(ox + 1.4, oy, oz + 1.2), mat=mats['hazard_yellow'], col=col)
        post_r.parent = root
        bar = abs_style.create_box(f"{name}_InterlockBar", size=(2.6, 0.1, 0.25), loc=(ox, oy, oz + 1.2), mat=mats['dark_steel'], col=col)
        bar.parent = root
        field = abs_style.create_box(f"{name}_PlasmaBarrier", size=(2.5, 0.04, 1.8), loc=(ox, oy, oz + 1.2), mat=mats['cyan_core'], col=col)
        field.parent = root

    elif asset_id == 54: # SM_Mod_54_Plasma_Energy_Cell_Charging_Station
        cabinet = abs_style.create_box(f"{name}_Cabinet", size=(1.8, 0.8, 2.6), loc=(ox, oy, oz + 1.3), mat=mats['dark_steel'], col=col)
        cabinet.parent = root
        for slot in range(3):
            cell = abs_style.create_cylinder(f"{name}_Cell_{slot}", radius=0.14, depth=0.7, loc=(ox - 0.5 + slot*0.5, oy - 0.25, oz + 1.4), mat=mats['cyan_core'], col=col)
            cell.parent = root
            bracket = abs_style.create_box(f"{name}_Socket_{slot}", size=(0.35, 0.35, 0.15), loc=(ox - 0.5 + slot*0.5, oy - 0.25, oz + 1.0), mat=mats['copper'], col=col)
            bracket.parent = root

    return root

KIT3_ASSETS = [
    (37, "SM_Mod_37_Plasma_Reactor_Core_Chamber"),
    (38, "SM_Mod_38_Plasma_Magnetic_Confinement_Ring"),
    (39, "SM_Mod_39_Plasma_Tesla_Discharge_Pylon"),
    (40, "SM_Mod_40_Plasma_HighVoltage_Transformer"),
    (41, "SM_Mod_41_Plasma_Cryo_Cooling_Radiator"),
    (42, "SM_Mod_42_Plasma_Capacitor_Bank_Rack"),
    (43, "SM_Mod_43_Plasma_Insulated_Conduit_400cm"),
    (44, "SM_Mod_44_Plasma_Slag_Runoff_Channel"),
    (45, "SM_Mod_45_Plasma_Beam_Focusing_Emitter"),
    (46, "SM_Mod_46_Plasma_Turbine_Generator_Housing"),
    (47, "SM_Mod_47_Plasma_Control_Terminal_Console"),
    (48, "SM_Mod_48_Plasma_Emergency_Dump_Vent"),
    (49, "SM_Mod_49_Plasma_Shielding_Tile_Wall"),
    (50, "SM_Mod_50_Plasma_Magnetic_Valve_Manifold"),
    (51, "SM_Mod_51_Plasma_Arc_Furnace_Crucible"),
    (52, "SM_Mod_52_Plasma_Diagnostic_Sensor_Array"),
    (53, "SM_Mod_53_Plasma_Safety_Interlock_Gate"),
    (54, "SM_Mod_54_Plasma_Energy_Cell_Charging_Station"),
]

def generate_kit3_scene(save_blend=True):
    abs_style.reset_comic_scene()
    col = abs_style.create_collection("Kit3_Plasma_Refinery")
    mats = init_kit3_materials()
    
    spacing_x = 4.8
    spacing_y = 5.2
    ped_mat = abs_style.get_comic_material("Pedestal_K3", base_color=(0.06, 0.08, 0.11), roughness=0.35, metallic=0.75)
    
    for idx, (aid, aname) in enumerate(KIT3_ASSETS):
        col_idx = idx % 6
        row_idx = idx // 6
        x = (col_idx - 2.5) * spacing_x
        y = (row_idx - 1.0) * spacing_y
        
        ped = abs_style.create_box(f"Pedestal_{aname}", size=(4.2, 4.2, 0.25), loc=(x, y, -0.125), mat=ped_mat, col=col)
        build_asset(aid, aname, (x, y, 0.0), col, mats)
        
    floor_mat = abs_style.get_comic_material("Floor_K3", base_color=(0.02, 0.025, 0.035), roughness=0.25, metallic=0.85)
    abs_style.create_box("FloorK3", size=(38.0, 24.0, 0.1), loc=(0, 0, -0.2), mat=floor_mat, col=col)
    abs_style.setup_studio_lighting(sun_energy=3.8, rim_energy=2.4, fill_energy=1.2)
    abs_style.setup_camera(name="Camera_Kit3", loc=(0, -24, 15), target=(0, 0, 1.2), focal_length=32)
    
    if save_blend:
        blend_path = os.path.join(abs_style.PROJECT_ROOT, "Art", "Blender", "Catalogo_Modulares_Kit3_Plasma.blend")
        bpy.ops.wm.save_as_mainfile(filepath=blend_path)
        print(f"[+] Blend saved: {blend_path}")
        
    abs_style.render_and_save("Showcase_Modulares_Kit3_Plasma_18.png", res_x=2560, res_y=1440)

if __name__ == "__main__":
    generate_kit3_scene()

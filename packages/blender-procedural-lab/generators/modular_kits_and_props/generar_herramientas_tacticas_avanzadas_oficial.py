# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Suite Oficial de 8 Herramientas Tacticas Avanzadas de Rescate (3 Existentes + 5 Nuevas)
# Blender 5.2 LTS - Shaders Stylized PBR, Cel-Shading y Freestyle Ink Lineart

import bpy
import bmesh
import math
import os
import sys

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

import astra_blender_styling as abs_style

def init_tactical_materials():
    mats = {}
    mats['hazard_yellow'] = abs_style.get_comic_material("T_Hazard_Yellow", base_color=(0.95, 0.70, 0.08), roughness=0.32, metallic=0.15, tex_pack="T_Trim_Industrial")
    mats['safety_orange'] = abs_style.get_comic_material("T_Safety_Orange", base_color=(0.95, 0.38, 0.06), roughness=0.35, metallic=0.10)
    mats['gunmetal'] = abs_style.get_comic_material("T_Gunmetal", base_color=(0.20, 0.22, 0.26), roughness=0.35, metallic=0.88, tex_pack="T_Steel_Plates")
    mats['steel_bright'] = abs_style.get_comic_material("T_Steel_Bright", base_color=(0.82, 0.85, 0.88), roughness=0.18, metallic=0.95)
    mats['copper'] = abs_style.get_comic_material("T_Copper", base_color=(0.95, 0.45, 0.22), roughness=0.25, metallic=0.92)
    mats['carbon_fiber'] = abs_style.get_comic_material("T_Carbon_Fiber", base_color=(0.08, 0.09, 0.10), roughness=0.55, metallic=0.25)
    mats['rubber_grip'] = abs_style.get_comic_material("T_Rubber_Grip", base_color=(0.10, 0.10, 0.12), roughness=0.85, metallic=0.0)
    mats['screen_flir'] = abs_style.get_comic_material("T_Screen_FLIR", base_color=(0.95, 0.60, 0.05), roughness=0.10, emissive_color=(1.0, 0.65, 0.05, 1.0), emissive_strength=2.8)
    mats['screen_green'] = abs_style.get_comic_material("T_Screen_Green", base_color=(0.05, 0.95, 0.35), roughness=0.10, emissive_color=(0.05, 0.95, 0.35, 1.0), emissive_strength=2.8)
    mats['beacon_blue'] = abs_style.get_comic_material("T_Beacon_Blue", base_color=(0.10, 0.75, 1.0), roughness=0.08, emissive_color=(0.10, 0.80, 1.0, 1.0), emissive_strength=3.5)
    mats['strobe_amber'] = abs_style.get_comic_material("T_Strobe_Amber", base_color=(1.0, 0.75, 0.10), roughness=0.08, emissive_color=(1.0, 0.80, 0.10, 1.0), emissive_strength=3.2)
    mats['foam_canister'] = abs_style.get_comic_material("T_Foam_Canister", base_color=(0.12, 0.45, 0.40), roughness=0.35, metallic=0.30)
    return mats

def build_tactical_tool(tool_id, name, origin, col, mats):
    root = bpy.data.objects.new(f"Root_{name}", None)
    root.location = (0, 0, 0)
    col.objects.link(root)
    ox, oy, oz = origin

    if tool_id == 1: # T01_Foam_Launcher_Heavy
        cannon = abs_style.create_cylinder(f"{name}_Barrel", radius=0.18, depth=1.4, rot=(math.radians(90), 0, 0), loc=(ox, oy, oz + 0.8), mat=mats['hazard_yellow'], col=col)
        cannon.parent = root
        canister = abs_style.create_cylinder(f"{name}_Tank", radius=0.16, depth=0.8, loc=(ox, oy + 0.1, oz + 0.45), mat=mats['foam_canister'], col=col)
        canister.parent = root
        diffuser = abs_style.create_cone(f"{name}_Diffuser", radius1=0.28, radius2=0.18, depth=0.3, rot=(math.radians(90), 0, 0), loc=(ox, oy - 0.8, oz + 0.8), mat=mats['gunmetal'], col=col)
        diffuser.parent = root
        gauge = abs_style.create_cylinder(f"{name}_Gauge", radius=0.07, depth=0.04, rot=(0, math.radians(90), 0), loc=(ox + 0.19, oy - 0.2, oz + 0.8), mat=mats['strobe_amber'], col=col)
        gauge.parent = root

    elif tool_id == 2: # T02_Net_Gun_Quad_Launcher
        receiver = abs_style.create_box(f"{name}_Body", size=(0.35, 0.7, 0.3), loc=(ox, oy, oz + 0.8), mat=mats['carbon_fiber'], col=col)
        receiver.parent = root
        for i in range(4):
            qx = ox - 0.1 + (i % 2) * 0.2
            qz = oz + 0.72 + (i // 2) * 0.16
            barrel = abs_style.create_cylinder(f"{name}_Tube_{i}", radius=0.06, depth=0.55, rot=(math.radians(90), 0, 0), loc=(qx, oy - 0.45, qz), mat=mats['copper'], col=col)
            barrel.parent = root
        laser = abs_style.create_cylinder(f"{name}_LaserSight", radius=0.03, depth=0.3, rot=(math.radians(90), 0, 0), loc=(ox, oy - 0.4, oz + 0.95), mat=mats['beacon_blue'], col=col)
        laser.parent = root

    elif tool_id == 3: # T03_Hydraulic_Jack_15T
        base = abs_style.create_box(f"{name}_Foot", size=(0.55, 0.55, 0.12), loc=(ox, oy, oz + 0.06), mat=mats['gunmetal'], col=col)
        base.parent = root
        body = abs_style.create_cylinder(f"{name}_Cylinder", radius=0.18, depth=0.9, loc=(ox, oy, oz + 0.55), mat=mats['hazard_yellow'], col=col)
        body.parent = root
        ram = abs_style.create_cylinder(f"{name}_RamShaft", radius=0.11, depth=0.6, loc=(ox, oy, oz + 1.15), mat=mats['steel_bright'], col=col)
        ram.parent = root
        saddle = abs_style.create_cylinder(f"{name}_Saddle", radius=0.14, depth=0.08, loc=(ox, oy, oz + 1.48), mat=mats['gunmetal'], col=col)
        saddle.parent = root
        lever = abs_style.create_cylinder(f"{name}_Handle", radius=0.03, depth=1.1, rot=(math.radians(35), 0, 0), loc=(ox, oy + 0.4, oz + 0.8), mat=mats['rubber_grip'], col=col)
        lever.parent = root

    elif tool_id == 4: # T04_Thermal_Imaging_Surveyor (NUEVO)
        body = abs_style.create_box(f"{name}_Chassis", size=(0.45, 0.35, 0.5), loc=(ox, oy, oz + 0.8), mat=mats['safety_orange'], col=col)
        body.parent = root
        screen = abs_style.create_box(f"{name}_FLIRScreen", size=(0.36, 0.02, 0.28), loc=(ox, oy + 0.18, oz + 0.82), mat=mats['screen_flir'], col=col)
        screen.parent = root
        lens_l = abs_style.create_cylinder(f"{name}_LensL", radius=0.08, depth=0.15, rot=(math.radians(90), 0, 0), loc=(ox - 0.12, oy - 0.2, oz + 0.8), mat=mats['gunmetal'], col=col)
        lens_l.parent = root
        lens_r = abs_style.create_cylinder(f"{name}_LensR", radius=0.08, depth=0.15, rot=(math.radians(90), 0, 0), loc=(ox + 0.12, oy - 0.2, oz + 0.8), mat=mats['beacon_blue'], col=col)
        lens_r.parent = root
        grip = abs_style.create_cylinder(f"{name}_Handle", radius=0.04, depth=0.35, loc=(ox, oy, oz + 0.42), mat=mats['rubber_grip'], col=col)
        grip.parent = root

    elif tool_id == 5: # T05_MultiGas_Atmospheric_Sniffer (NUEVO)
        unit = abs_style.create_box(f"{name}_DetectorBody", size=(0.28, 0.18, 0.65), loc=(ox, oy, oz + 0.8), mat=mats['hazard_yellow'], col=col)
        unit.parent = root
        display = abs_style.create_box(f"{name}_LCD", size=(0.2, 0.02, 0.16), loc=(ox, oy - 0.1, oz + 0.9), mat=mats['screen_green'], col=col)
        display.parent = root
        probe = abs_style.create_cylinder(f"{name}_FlexibleProbe", radius=0.02, depth=0.8, loc=(ox, oy, oz + 1.45), mat=mats['steel_bright'], col=col)
        probe.parent = root
        strobe = abs_style.create_cylinder(f"{name}_AlarmBeacon", radius=0.06, depth=0.1, loc=(ox + 0.1, oy, oz + 1.15), mat=mats['strobe_amber'], col=col)
        strobe.parent = root

    elif tool_id == 6: # T06_Pneumatic_Pipe_Sealing_Clamp (NUEVO)
        ring_l = abs_style.create_torus(f"{name}_JawHalf1", major_r=0.28, minor_r=0.05, loc=(ox, oy, oz + 0.8), mat=mats['gunmetal'], col=col)
        ring_l.parent = root
        lining = abs_style.create_torus(f"{name}_VitonSeal", major_r=0.25, minor_r=0.04, loc=(ox, oy, oz + 0.8), mat=mats['rubber_grip'], col=col)
        lining.parent = root
        handle_t = abs_style.create_cylinder(f"{name}_LeverT", radius=0.03, depth=0.6, rot=(0, math.radians(90), 0), loc=(ox - 0.4, oy, oz + 0.9), mat=mats['hazard_yellow'], col=col)
        handle_t.parent = root
        handle_b = abs_style.create_cylinder(f"{name}_LeverB", radius=0.03, depth=0.6, rot=(0, math.radians(90), 0), loc=(ox + 0.4, oy, oz + 0.7), mat=mats['hazard_yellow'], col=col)
        handle_b.parent = root
        relief = abs_style.create_cylinder(f"{name}_BypassValve", radius=0.04, depth=0.2, loc=(ox, oy - 0.32, oz + 0.8), mat=mats['copper'], col=col)
        relief.parent = root

    elif tool_id == 7: # T07_Micro_Recon_Hover_Drone (NUEVO)
        cage = abs_style.create_torus(f"{name}_CageRing1", major_r=0.35, minor_r=0.025, loc=(ox, oy, oz + 0.8), mat=mats['carbon_fiber'], col=col)
        cage.parent = root
        cage2 = abs_style.create_torus(f"{name}_CageRing2", major_r=0.35, minor_r=0.025, rot=(math.radians(90), 0, 0), loc=(ox, oy, oz + 0.8), mat=mats['carbon_fiber'], col=col)
        cage2.parent = root
        core = abs_style.create_cylinder(f"{name}_AvionicsCore", radius=0.14, depth=0.22, loc=(ox, oy, oz + 0.8), mat=mats['hazard_yellow'], col=col)
        core.parent = root
        lens = abs_style.create_cylinder(f"{name}_SensorEye", radius=0.07, depth=0.08, rot=(math.radians(90), 0, 0), loc=(ox, oy - 0.15, oz + 0.8), mat=mats['beacon_blue'], col=col)
        lens.parent = root
        rotor_t = abs_style.create_cylinder(f"{name}_RotorTop", radius=0.28, depth=0.015, loc=(ox, oy, oz + 0.95), mat=mats['gunmetal'], col=col)
        rotor_t.parent = root
        rotor_b = abs_style.create_cylinder(f"{name}_RotorBot", radius=0.28, depth=0.015, loc=(ox, oy, oz + 0.65), mat=mats['gunmetal'], col=col)
        rotor_b.parent = root

    elif tool_id == 8: # T08_Portable_Air_Scrubber_Beacon (NUEVO)
        unit = abs_style.create_cylinder(f"{name}_ScrubberBody", radius=0.38, depth=0.85, loc=(ox, oy, oz + 0.5), mat=mats['hazard_yellow'], col=col)
        unit.parent = root
        filter_mesh = abs_style.create_cylinder(f"{name}_FilterGrille", radius=0.4, depth=0.4, loc=(ox, oy, oz + 0.5), mat=mats['gunmetal'], col=col)
        filter_mesh.parent = root
        pylon = abs_style.create_cylinder(f"{name}_BeaconMast", radius=0.04, depth=0.9, loc=(ox, oy, oz + 1.25), mat=mats['steel_bright'], col=col)
        pylon.parent = root
        strobe = abs_style.create_cylinder(f"{name}_StrobeLight", radius=0.1, depth=0.18, loc=(ox, oy, oz + 1.7), mat=mats['beacon_blue'], col=col)
        strobe.parent = root

    return root

TACTICAL_TOOLS = [
    (1, "T01_Foam_Launcher_Heavy"),
    (2, "T02_Net_Gun_Quad_Launcher"),
    (3, "T03_Hydraulic_Jack_15T"),
    (4, "T04_Thermal_Imaging_Surveyor"),
    (5, "T05_MultiGas_Atmospheric_Sniffer"),
    (6, "T06_Pneumatic_Pipe_Sealing_Clamp"),
    (7, "T07_Micro_Recon_Hover_Drone"),
    (8, "T08_Portable_Air_Scrubber_Beacon"),
]

def generate_tactical_scene(save_blend=True):
    abs_style.reset_comic_scene(bg_color=(0.015, 0.02, 0.028, 1.0), bg_strength=0.4, ink_thickness=1.6)
    col = abs_style.create_collection("Herramientas_Tacticas_Avanzadas")
    mats = init_tactical_materials()
    
    # Grid de 4 columnas x 2 filas
    spacing_x = 4.4
    spacing_y = 5.2
    ped_mat = abs_style.get_comic_material("Pedestal_Tactical", base_color=(0.08, 0.09, 0.12), roughness=0.35, metallic=0.7)
    plaque_mat = abs_style.get_comic_material("Plaque_Brass_T", base_color=(0.92, 0.74, 0.22), roughness=0.22, metallic=0.92)
    
    for idx, (tid, tname) in enumerate(TACTICAL_TOOLS):
        col_idx = idx % 4
        row_idx = idx // 4
        x = (col_idx - 1.5) * spacing_x
        y = (row_idx - 0.5) * spacing_y
        
        ped = abs_style.create_box(f"Pedestal_{tname}", size=(3.2, 3.2, 0.3), loc=(x, y, 0.15), mat=ped_mat, col=col)
        plaque = abs_style.create_box(f"Plaque_{tname}", size=(1.4, 0.08, 0.15), rot=(math.radians(30), 0, 0), loc=(x, y - 1.55, 0.22), mat=plaque_mat, col=col)
        build_tactical_tool(tid, tname, (x, y, 0.3), col, mats)
        
    abs_style.setup_studio_lighting(sun_energy=3.8, rim_energy=2.4, fill_energy=1.2)
    
    floor_mat = abs_style.get_comic_material("Tactical_Floor", base_color=(0.02, 0.025, 0.035), roughness=0.25, metallic=0.85)
    abs_style.create_box("TacticalFloor", size=(40.0, 24.0, 0.2), loc=(0, 0, -0.1), mat=floor_mat, col=col)
    
    abs_style.setup_camera(name="Camera_Tactical", loc=(0, -18, 11), target=(0, 0, 0.8), focal_length=32)
    
    if save_blend:
        blend_path = os.path.join(abs_style.PROJECT_ROOT, "Art", "Blender", "Herramientas_Tacticas_Avanzadas_Oficial.blend")
        bpy.ops.wm.save_as_mainfile(filepath=blend_path)
        print(f"[+] Tactical Tools Blend saved: {blend_path}")
        
    abs_style.render_and_save("Showcase_Herramientas_Tacticas_Avanzadas_Master.png", res_x=2560, res_y=1440)
    
    # Closeups de herramientas clave (incluyendo nuevos objetos tácticos)
    for tid, tname in [TACTICAL_TOOLS[3], TACTICAL_TOOLS[4], TACTICAL_TOOLS[6]]: # FLIR, Sniffer, Micro-Drone
        col_idx = (tid - 1) % 4
        row_idx = (tid - 1) // 4
        x = (col_idx - 1.5) * spacing_x
        y = (row_idx - 0.5) * spacing_y
        abs_style.setup_camera(name=f"Cam_Close_{tname}", loc=(x, y - 3.2, 1.8), target=(x, y, 0.9), focal_length=45)
        abs_style.render_and_save(f"CloseUp_{tname}.png", res_x=1280, res_y=1280)
        
    print("[+] Render de Herramientas Tacticas Avanzadas completado con exito!")

if __name__ == "__main__":
    generate_tactical_scene()

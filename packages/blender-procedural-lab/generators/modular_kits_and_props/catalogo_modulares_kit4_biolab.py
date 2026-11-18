# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Kit 4: Laboratorio Biologico y Cuarentena Criogenica (Activos 55 a 72 de 90)
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

def init_kit4_materials():
    mats = {}
    mats['clean_white'] = abs_style.get_comic_material("K4_Bio_CleanWhite", base_color=(0.88, 0.90, 0.92), roughness=0.22, metallic=0.1)
    mats['hazard_orange'] = abs_style.get_comic_material("K4_Bio_HazardOrange", base_color=(0.95, 0.40, 0.05), roughness=0.35, metallic=0.15)
    mats['acid_green'] = abs_style.get_comic_material("K4_Bio_AcidGreen", base_color=(0.10, 0.95, 0.20), roughness=0.10, metallic=0.0, emissive_color=(0.10, 0.95, 0.20, 1.0), emissive_strength=2.6)
    mats['bio_glass'] = abs_style.get_comic_material("K4_Bio_Glass", base_color=(0.85, 0.95, 0.92), roughness=0.05, metallic=0.1, alpha=0.55, is_transparent=True)
    mats['bio_steel'] = abs_style.get_comic_material("K4_Bio_Steel", base_color=(0.65, 0.68, 0.72), roughness=0.18, metallic=0.90)
    mats['rubber'] = abs_style.get_comic_material("K4_Bio_RubberSeal", base_color=(0.12, 0.13, 0.15), roughness=0.85, metallic=0.0)
    mats['stasis_cyan'] = abs_style.get_comic_material("K4_Bio_StasisCyan", base_color=(0.0, 0.85, 0.95), roughness=0.1, emissive_color=(0.0, 0.85, 0.95, 1.0), emissive_strength=2.0)
    return mats

def build_asset(asset_id, name, origin, col, mats):
    root = bpy.data.objects.new(f"Root_{name}", None)
    root.location = (0, 0, 0)
    col.objects.link(root)
    
    ox, oy, oz = origin
    
    if asset_id == 55: # SM_Mod_55_Bio_Cryo_Stasis_Pod_Vertical
        shell = abs_style.create_cylinder(f"{name}_Shell", radius=0.75, depth=2.8, loc=(ox, oy, oz + 1.4), mat=mats['clean_white'], col=col)
        shell.parent = root
        glass = abs_style.create_cylinder(f"{name}_Window", radius=0.6, depth=1.8, loc=(ox, oy - 0.2, oz + 1.5), mat=mats['stasis_cyan'], col=col)
        glass.parent = root
        rim_top = abs_style.create_torus(f"{name}_RimT", major_r=0.8, minor_r=0.08, loc=(ox, oy, oz + 2.7), mat=mats['hazard_orange'], col=col)
        rim_top.parent = root
        rim_bot = abs_style.create_torus(f"{name}_RimB", major_r=0.8, minor_r=0.08, loc=(ox, oy, oz + 0.2), mat=mats['hazard_orange'], col=col)
        rim_bot.parent = root

    elif asset_id == 56: # SM_Mod_56_Bio_Specimen_Containment_Cylinder
        base = abs_style.create_cylinder(f"{name}_Base", radius=1.0, depth=0.4, loc=(ox, oy, oz + 0.2), mat=mats['bio_steel'], col=col)
        base.parent = root
        tank = abs_style.create_cylinder(f"{name}_Glass", radius=0.85, depth=2.2, loc=(ox, oy, oz + 1.5), mat=mats['acid_green'], col=col)
        tank.parent = root
        cap = abs_style.create_cylinder(f"{name}_Cap", radius=1.0, depth=0.35, loc=(ox, oy, oz + 2.75), mat=mats['clean_white'], col=col)
        cap.parent = root

    elif asset_id == 57: # SM_Mod_57_Bio_Decontamination_Shower_Arch
        post_l = abs_style.create_cylinder(f"{name}_PostL", radius=0.15, depth=3.2, loc=(ox - 1.2, oy, oz + 1.6), mat=mats['hazard_orange'], col=col)
        post_l.parent = root
        post_r = abs_style.create_cylinder(f"{name}_PostR", radius=0.15, depth=3.2, loc=(ox + 1.2, oy, oz + 1.6), mat=mats['hazard_orange'], col=col)
        post_r.parent = root
        top_arch = abs_style.create_cylinder(f"{name}_Header", radius=0.18, depth=2.4, rot=(0, math.radians(90), 0), loc=(ox, oy, oz + 3.1), mat=mats['hazard_orange'], col=col)
        top_arch.parent = root
        nozzle = abs_style.create_cone(f"{name}_Nozzle", radius1=0.25, radius2=0.08, depth=0.3, loc=(ox, oy, oz + 2.9), mat=mats['bio_steel'], col=col)
        nozzle.parent = root
        grate = abs_style.create_box(f"{name}_DrainGrate", size=(2.0, 1.6, 0.1), loc=(ox, oy, oz + 0.05), mat=mats['bio_steel'], col=col)
        grate.parent = root

    elif asset_id == 58: # SM_Mod_58_Bio_Airlock_Hermetic_Hatch
        frame = abs_style.create_box(f"{name}_Frame", size=(2.8, 0.4, 3.2), loc=(ox, oy, oz + 1.6), mat=mats['clean_white'], col=col)
        frame.parent = root
        seal = abs_style.create_torus(f"{name}_SiliconeSeal", major_r=1.1, minor_r=0.08, loc=(ox, oy - 0.2, oz + 1.6), mat=mats['hazard_orange'], col=col)
        seal.parent = root
        door = abs_style.create_cylinder(f"{name}_HatchPlate", radius=1.05, depth=0.18, rot=(math.radians(90), 0, 0), loc=(ox, oy - 0.1, oz + 1.6), mat=mats['clean_white'], col=col)
        door.parent = root
        wheel = abs_style.create_torus(f"{name}_LockWheel", major_r=0.35, minor_r=0.05, rot=(math.radians(90), 0, 0), loc=(ox, oy - 0.22, oz + 1.6), mat=mats['hazard_orange'], col=col)
        wheel.parent = root

    elif asset_id == 59: # SM_Mod_59_Bio_Laminar_Flow_Glovebox
        table = abs_style.create_box(f"{name}_Bench", size=(2.2, 1.2, 0.9), loc=(ox, oy, oz + 0.45), mat=mats['bio_steel'], col=col)
        table.parent = root
        hood = abs_style.create_box(f"{name}_Hood", size=(2.0, 1.0, 1.4), loc=(ox, oy, oz + 1.6), mat=mats['clean_white'], col=col)
        hood.parent = root
        screen = abs_style.create_box(f"{name}_GlassFront", size=(1.8, 0.05, 1.0), loc=(ox, oy - 0.48, oz + 1.5), mat=mats['bio_glass'], col=col)
        screen.parent = root
        for gx in [-0.4, 0.4]:
            port = abs_style.create_torus(f"{name}_GlovePort_{gx}", major_r=0.18, minor_r=0.03, rot=(math.radians(90), 0, 0), loc=(ox + gx, oy - 0.5, oz + 1.3), mat=mats['rubber'], col=col)
            port.parent = root

    elif asset_id == 60: # SM_Mod_60_Bio_Surgical_Autopsy_Table
        pedestal = abs_style.create_cylinder(f"{name}_Pedestal", radius=0.35, depth=0.8, loc=(ox, oy, oz + 0.4), mat=mats['bio_steel'], col=col)
        pedestal.parent = root
        slab = abs_style.create_box(f"{name}_Slab", size=(2.4, 0.9, 0.15), loc=(ox, oy, oz + 0.88), mat=mats['bio_steel'], col=col)
        slab.parent = root
        curb = abs_style.create_box(f"{name}_Rim", size=(2.45, 0.95, 0.05), loc=(ox, oy, oz + 0.98), mat=mats['hazard_orange'], col=col)
        curb.parent = root
        drain = abs_style.create_cylinder(f"{name}_Drain", radius=0.08, depth=0.05, loc=(ox - 0.9, oy, oz + 0.96), mat=mats['acid_green'], col=col)
        drain.parent = root

    elif asset_id == 61: # SM_Mod_61_Bio_Centrifuge_Analyzer_Unit
        box_c = abs_style.create_box(f"{name}_Chassis", size=(1.2, 1.2, 0.9), loc=(ox, oy, oz + 0.45), mat=mats['clean_white'], col=col)
        box_c.parent = root
        rotor = abs_style.create_cylinder(f"{name}_Drum", radius=0.45, depth=0.2, loc=(ox, oy, oz + 0.95), mat=mats['bio_steel'], col=col)
        rotor.parent = root
        lid = abs_style.create_torus(f"{name}_LidSeal", major_r=0.48, minor_r=0.04, loc=(ox, oy, oz + 1.0), mat=mats['hazard_orange'], col=col)
        lid.parent = root

    elif asset_id == 62: # SM_Mod_62_Bio_Chemical_Scrubber_Tower
        tower = abs_style.create_cylinder(f"{name}_Tower", radius=0.6, depth=3.2, loc=(ox, oy, oz + 1.6), mat=mats['clean_white'], col=col)
        tower.parent = root
        for rz in [0.8, 1.6, 2.4]:
            band = abs_style.create_torus(f"{name}_Band_{rz}", major_r=0.62, minor_r=0.04, loc=(ox, oy, oz + rz), mat=mats['hazard_orange'], col=col)
            band.parent = root
        filter_core = abs_style.create_box(f"{name}_HEPAFilter", size=(0.7, 0.7, 0.5), loc=(ox, oy, oz + 3.0), mat=mats['rubber'], col=col)
        filter_core.parent = root

    elif asset_id == 63: # SM_Mod_63_Bio_Hazard_Waste_Incinerator
        oven = abs_style.create_box(f"{name}_Body", size=(1.8, 1.6, 2.2), loc=(ox, oy, oz + 1.1), mat=mats['hazard_orange'], col=col)
        oven.parent = root
        hatch = abs_style.create_box(f"{name}_Door", size=(1.2, 0.2, 1.2), loc=(ox, oy - 0.8, oz + 1.2), mat=mats['bio_steel'], col=col)
        hatch.parent = root
        glow = abs_style.create_box(f"{name}_FireGlow", size=(0.9, 0.05, 0.3), loc=(ox, oy - 0.9, oz + 1.2), mat=mats['acid_green'], col=col)
        glow.parent = root

    elif asset_id == 64: # SM_Mod_64_Bio_Partition_Glass_Wall_400x350
        frame_l = abs_style.create_box(f"{name}_MullionL", size=(0.2, 0.3, 3.5), loc=(ox - 1.9, oy, oz + 1.75), mat=mats['clean_white'], col=col)
        frame_l.parent = root
        frame_r = abs_style.create_box(f"{name}_MullionR", size=(0.2, 0.3, 3.5), loc=(ox + 1.9, oy, oz + 1.75), mat=mats['clean_white'], col=col)
        frame_r.parent = root
        frame_c = abs_style.create_box(f"{name}_MullionC", size=(0.15, 0.3, 3.5), loc=(ox, oy, oz + 1.75), mat=mats['clean_white'], col=col)
        frame_c.parent = root
        glass = abs_style.create_box(f"{name}_GlassPane", size=(3.8, 0.08, 3.2), loc=(ox, oy, oz + 1.75), mat=mats['bio_glass'], col=col)
        glass.parent = root

    elif asset_id == 65: # SM_Mod_65_Bio_Autoclave_Sterilizer_Chamber
        tank = abs_style.create_cylinder(f"{name}_Chamber", radius=0.65, depth=1.8, rot=(math.radians(90), 0, 0), loc=(ox, oy, oz + 1.2), mat=mats['bio_steel'], col=col)
        tank.parent = root
        door_wheel = abs_style.create_torus(f"{name}_Wheel", major_r=0.45, minor_r=0.06, rot=(math.radians(90), 0, 0), loc=(ox, oy - 0.95, oz + 1.2), mat=mats['hazard_orange'], col=col)
        door_wheel.parent = root
        stand = abs_style.create_box(f"{name}_Stand", size=(1.2, 1.4, 0.7), loc=(ox, oy, oz + 0.35), mat=mats['clean_white'], col=col)
        stand.parent = root

    elif asset_id == 66: # SM_Mod_66_Bio_Sample_Cold_Storage_Rack
        cab = abs_style.create_box(f"{name}_Cabinet", size=(1.6, 0.9, 2.6), loc=(ox, oy, oz + 1.3), mat=mats['bio_steel'], col=col)
        cab.parent = root
        for ry in [0.7, 1.4, 2.1]:
            handle = abs_style.create_box(f"{name}_Drawer_{ry}", size=(1.3, 0.08, 0.4), loc=(ox, oy - 0.45, oz + ry), mat=mats['clean_white'], col=col)
            handle.parent = root
            led = abs_style.create_cylinder(f"{name}_LED_{ry}", radius=0.03, depth=0.05, rot=(math.radians(90), 0, 0), loc=(ox + 0.55, oy - 0.48, oz + ry), mat=mats['stasis_cyan'], col=col)
            led.parent = root

    elif asset_id == 67: # SM_Mod_67_Bio_Drainage_Gutters_Floor
        floor = abs_style.create_box(f"{name}_Floor", size=(4.0, 4.0, 0.2), loc=(ox, oy, oz + 0.1), mat=mats['clean_white'], col=col)
        floor.parent = root
        gutter1 = abs_style.create_box(f"{name}_GutterL", size=(3.8, 0.3, 0.08), loc=(ox, oy - 1.5, oz + 0.17), mat=mats['bio_steel'], col=col)
        gutter1.parent = root
        gutter2 = abs_style.create_box(f"{name}_GutterR", size=(3.8, 0.3, 0.08), loc=(ox, oy + 1.5, oz + 0.17), mat=mats['bio_steel'], col=col)
        gutter2.parent = root

    elif asset_id == 68: # SM_Mod_68_Bio_Overhead_Surgical_Lamp
        rod = abs_style.create_cylinder(f"{name}_Stem", radius=0.05, depth=1.2, loc=(ox, oy, oz + 2.8), mat=mats['bio_steel'], col=col)
        rod.parent = root
        dome = abs_style.create_cone(f"{name}_Reflector", radius1=0.8, radius2=0.2, depth=0.3, loc=(ox, oy, oz + 2.1), mat=mats['clean_white'], col=col)
        dome.parent = root
        for i in range(4):
            ang = i * (math.pi / 2)
            lx = ox + math.cos(ang) * 0.45
            ly = oy + math.sin(ang) * 0.45
            led = abs_style.create_cylinder(f"{name}_Spot_{i}", radius=0.12, depth=0.05, loc=(lx, ly, oz + 2.0), mat=mats['stasis_cyan'], col=col)
            led.parent = root

    elif asset_id == 69: # SM_Mod_69_Bio_Emergency_Eyewash_Station
        bowl = abs_style.create_cylinder(f"{name}_Bowl", radius=0.35, depth=0.2, loc=(ox, oy, oz + 1.1), mat=mats['hazard_orange'], col=col)
        bowl.parent = root
        ped = abs_style.create_cylinder(f"{name}_Ped", radius=0.08, depth=1.0, loc=(ox, oy, oz + 0.5), mat=mats['bio_steel'], col=col)
        ped.parent = root
        pull_rod = abs_style.create_cylinder(f"{name}_Lever", radius=0.02, depth=0.8, loc=(ox + 0.4, oy, oz + 1.8), mat=mats['hazard_orange'], col=col)
        pull_rod.parent = root

    elif asset_id == 70: # SM_Mod_70_Bio_Quarantine_Isolation_Tent
        frame = abs_style.create_box(f"{name}_Frame", size=(3.0, 3.0, 2.8), loc=(ox, oy, oz + 1.4), mat=mats['bio_steel'], bevel=True, col=col)
        frame.parent = root
        curtain = abs_style.create_box(f"{name}_Curtain", size=(2.9, 2.9, 2.6), loc=(ox, oy, oz + 1.4), mat=mats['hazard_orange'], col=col)
        curtain.parent = root

    elif asset_id == 71: # SM_Mod_71_Bio_Robotic_Sample_Arm_Rig
        base = abs_style.create_cylinder(f"{name}_Turret", radius=0.35, depth=0.4, loc=(ox, oy, oz + 0.2), mat=mats['clean_white'], col=col)
        base.parent = root
        arm1 = abs_style.create_box(f"{name}_LowerArm", size=(0.15, 0.15, 1.2), rot=(0, math.radians(30), 0), loc=(ox + 0.3, oy, oz + 0.9), mat=mats['hazard_orange'], col=col)
        arm1.parent = root
        arm2 = abs_style.create_box(f"{name}_UpperArm", size=(0.12, 0.12, 1.0), rot=(0, -math.radians(45), 0), loc=(ox + 0.7, oy, oz + 1.7), mat=mats['bio_steel'], col=col)
        arm2.parent = root
        gripper = abs_style.create_torus(f"{name}_Gripper", major_r=0.15, minor_r=0.04, loc=(ox + 1.1, oy, oz + 2.0), mat=mats['hazard_orange'], col=col)
        gripper.parent = root

    elif asset_id == 72: # SM_Mod_72_Bio_Toxin_Spill_Containment_Curb
        curb = abs_style.create_box(f"{name}_Curb", size=(4.0, 0.35, 0.3), loc=(ox, oy, oz + 0.15), mat=mats['hazard_orange'], col=col)
        curb.parent = root
        stripe = abs_style.create_box(f"{name}_Stripe", size=(3.8, 0.38, 0.08), loc=(ox, oy, oz + 0.15), mat=mats['clean_white'], col=col)
        stripe.parent = root

    return root

KIT4_ASSETS = [
    (55, "SM_Mod_55_Bio_Cryo_Stasis_Pod_Vertical"),
    (56, "SM_Mod_56_Bio_Specimen_Containment_Cylinder"),
    (57, "SM_Mod_57_Bio_Decontamination_Shower_Arch"),
    (58, "SM_Mod_58_Bio_Airlock_Hermetic_Hatch"),
    (59, "SM_Mod_59_Bio_Laminar_Flow_Glovebox"),
    (60, "SM_Mod_60_Bio_Surgical_Autopsy_Table"),
    (61, "SM_Mod_61_Bio_Centrifuge_Analyzer_Unit"),
    (62, "SM_Mod_62_Bio_Chemical_Scrubber_Tower"),
    (63, "SM_Mod_63_Bio_Hazard_Waste_Incinerator"),
    (64, "SM_Mod_64_Bio_Partition_Glass_Wall_400x350"),
    (65, "SM_Mod_65_Bio_Autoclave_Sterilizer_Chamber"),
    (66, "SM_Mod_66_Bio_Sample_Cold_Storage_Rack"),
    (67, "SM_Mod_67_Bio_Drainage_Gutters_Floor"),
    (68, "SM_Mod_68_Bio_Overhead_Surgical_Lamp"),
    (69, "SM_Mod_69_Bio_Emergency_Eyewash_Station"),
    (70, "SM_Mod_70_Bio_Quarantine_Isolation_Tent"),
    (71, "SM_Mod_71_Bio_Robotic_Sample_Arm_Rig"),
    (72, "SM_Mod_72_Bio_Toxin_Spill_Containment_Curb"),
]

def generate_kit4_scene(save_blend=True):
    abs_style.reset_comic_scene()
    col = abs_style.create_collection("Kit4_BioLab_Quarantine")
    mats = init_kit4_materials()
    
    spacing_x = 4.8
    spacing_y = 5.2
    ped_mat = abs_style.get_comic_material("Pedestal_K4", base_color=(0.12, 0.14, 0.16), roughness=0.3, metallic=0.6)
    
    for idx, (aid, aname) in enumerate(KIT4_ASSETS):
        col_idx = idx % 6
        row_idx = idx // 6
        x = (col_idx - 2.5) * spacing_x
        y = (row_idx - 1.0) * spacing_y
        
        ped = abs_style.create_box(f"Pedestal_{aname}", size=(4.2, 4.2, 0.25), loc=(x, y, -0.125), mat=ped_mat, col=col)
        build_asset(aid, aname, (x, y, 0.0), col, mats)
        
    floor_mat = abs_style.get_comic_material("Floor_K4", base_color=(0.02, 0.025, 0.035), roughness=0.25, metallic=0.85)
    abs_style.create_box("FloorK4", size=(38.0, 24.0, 0.1), loc=(0, 0, -0.2), mat=floor_mat, col=col)
    abs_style.setup_studio_lighting(sun_energy=3.8, rim_energy=2.4, fill_energy=1.2)
    abs_style.setup_camera(name="Camera_Kit4", loc=(0, -24, 15), target=(0, 0, 1.2), focal_length=32)
    
    if save_blend:
        blend_path = os.path.join(abs_style.PROJECT_ROOT, "Art", "Blender", "Catalogo_Modulares_Kit4_BioLab.blend")
        bpy.ops.wm.save_as_mainfile(filepath=blend_path)
        print(f"[+] Blend saved: {blend_path}")
        
    abs_style.render_and_save("Showcase_Modulares_Kit4_BioLab_18.png", res_x=2560, res_y=1440)

if __name__ == "__main__":
    generate_kit4_scene()

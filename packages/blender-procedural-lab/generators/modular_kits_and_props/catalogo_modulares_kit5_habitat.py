# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Kit 5: Habitat de Tripulacion y Puente de Mando Tactico (Activos 73 a 90 de 90)
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

def init_kit5_materials():
    mats = {}
    mats['navy_blue'] = abs_style.get_comic_material("K5_Hab_NavyBlue", base_color=(0.12, 0.18, 0.28), roughness=0.40, metallic=0.20)
    mats['matte_grey'] = abs_style.get_comic_material("K5_Hab_MatteGrey", base_color=(0.35, 0.38, 0.42), roughness=0.45, metallic=0.35)
    mats['leather'] = abs_style.get_comic_material("K5_Hab_LeatherBrown", base_color=(0.28, 0.16, 0.10), roughness=0.65, metallic=0.05)
    mats['holo_green'] = abs_style.get_comic_material("K5_Hab_HoloGreen", base_color=(0.05, 0.95, 0.45), roughness=0.10, metallic=0.0, emissive_color=(0.05, 0.95, 0.45, 1.0), emissive_strength=2.8)
    mats['amber_crt'] = abs_style.get_comic_material("K5_Hab_AmberCRT", base_color=(0.95, 0.65, 0.10), roughness=0.15, metallic=0.0, emissive_color=(0.95, 0.65, 0.10, 1.0), emissive_strength=2.5)
    mats['steel_bright'] = abs_style.get_comic_material("K5_Hab_SteelBright", base_color=(0.75, 0.78, 0.82), roughness=0.25, metallic=0.88)
    mats['hazard_yellow'] = abs_style.get_comic_material("K5_Hazard_Yellow", base_color=(0.95, 0.70, 0.08), roughness=0.35, metallic=0.10)
    return mats

def build_asset(asset_id, name, origin, col, mats):
    root = bpy.data.objects.new(f"Root_{name}", None)
    root.location = (0, 0, 0)
    col.objects.link(root)
    
    ox, oy, oz = origin
    
    if asset_id == 73: # SM_Mod_73_Hab_Crew_Bunk_Pod_Double
        frame = abs_style.create_box(f"{name}_Frame", size=(2.4, 1.2, 2.6), loc=(ox, oy, oz + 1.3), mat=mats['navy_blue'], col=col)
        frame.parent = root
        bed1 = abs_style.create_box(f"{name}_BedBot", size=(2.1, 1.0, 0.25), loc=(ox, oy, oz + 0.5), mat=mats['matte_grey'], col=col)
        bed1.parent = root
        bed2 = abs_style.create_box(f"{name}_BedTop", size=(2.1, 1.0, 0.25), loc=(ox, oy, oz + 1.7), mat=mats['matte_grey'], col=col)
        bed2.parent = root
        ladder = abs_style.create_cylinder(f"{name}_LadderRail", radius=0.03, depth=2.4, loc=(ox - 1.0, oy - 0.55, oz + 1.2), mat=mats['steel_bright'], col=col)
        ladder.parent = root

    elif asset_id == 74: # SM_Mod_74_Hab_Galley_Food_Synthesizer
        counter = abs_style.create_box(f"{name}_Counter", size=(1.8, 0.9, 1.0), loc=(ox, oy, oz + 0.5), mat=mats['navy_blue'], col=col)
        counter.parent = root
        dispenser = abs_style.create_box(f"{name}_Niche", size=(0.8, 0.5, 0.5), loc=(ox, oy - 0.2, oz + 1.25), mat=mats['steel_bright'], col=col)
        dispenser.parent = root
        tray = abs_style.create_box(f"{name}_FoodTray", size=(0.4, 0.3, 0.05), loc=(ox, oy - 0.2, oz + 1.05), mat=mats['amber_crt'], col=col)
        tray.parent = root

    elif asset_id == 75: # SM_Mod_75_Hab_Sanitary_Shower_Module
        booth = abs_style.create_box(f"{name}_Booth", size=(1.4, 1.4, 2.6), loc=(ox, oy, oz + 1.3), mat=mats['matte_grey'], col=col)
        booth.parent = root
        door_glass = abs_style.create_box(f"{name}_GlassDoor", size=(1.0, 0.05, 2.2), loc=(ox, oy - 0.65, oz + 1.2), mat=mats['holo_green'], col=col)
        door_glass.parent = root
        shower_head = abs_style.create_torus(f"{name}_Head", major_r=0.2, minor_r=0.04, rot=(math.radians(90), 0, 0), loc=(ox, oy, oz + 2.3), mat=mats['steel_bright'], col=col)
        shower_head.parent = root

    elif asset_id == 76: # SM_Mod_76_Hab_Lockers_Storage_Row
        bank = abs_style.create_box(f"{name}_Bank", size=(2.4, 0.7, 2.4), loc=(ox, oy, oz + 1.2), mat=mats['navy_blue'], col=col)
        bank.parent = root
        for lx in [-0.9, -0.3, 0.3, 0.9]:
            seam = abs_style.create_box(f"{name}_LockerSeam_{lx}", size=(0.55, 0.05, 2.2), loc=(ox + lx, oy - 0.33, oz + 1.2), mat=mats['matte_grey'], col=col)
            seam.parent = root
            pad = abs_style.create_box(f"{name}_Keypad_{lx}", size=(0.1, 0.06, 0.15), loc=(ox + lx, oy - 0.35, oz + 1.4), mat=mats['amber_crt'], col=col)
            pad.parent = root

    elif asset_id == 77: # SM_Mod_77_Hab_Recreation_Mess_Table
        top = abs_style.create_box(f"{name}_TableTop", size=(2.4, 1.1, 0.1), loc=(ox, oy, oz + 0.8), mat=mats['steel_bright'], col=col)
        top.parent = root
        ped1 = abs_style.create_cylinder(f"{name}_Ped1", radius=0.08, depth=0.75, loc=(ox - 0.8, oy, oz + 0.4), mat=mats['navy_blue'], col=col)
        ped1.parent = root
        ped2 = abs_style.create_cylinder(f"{name}_Ped2", radius=0.08, depth=0.75, loc=(ox + 0.8, oy, oz + 0.4), mat=mats['navy_blue'], col=col)
        ped2.parent = root
        bench_l = abs_style.create_box(f"{name}_BenchL", size=(2.2, 0.35, 0.08), loc=(ox, oy - 0.8, oz + 0.45), mat=mats['leather'], col=col)
        bench_l.parent = root
        bench_r = abs_style.create_box(f"{name}_BenchR", size=(2.2, 0.35, 0.08), loc=(ox, oy + 0.8, oz + 0.45), mat=mats['leather'], col=col)
        bench_r.parent = root

    elif asset_id == 78: # SM_Mod_78_Hab_Command_Helm_Console
        console = abs_style.create_box(f"{name}_Base", size=(2.6, 1.2, 0.9), loc=(ox, oy, oz + 0.45), mat=mats['navy_blue'], col=col)
        console.parent = root
        hood = abs_style.create_box(f"{name}_Hood", size=(2.4, 0.8, 0.5), rot=(math.radians(30), 0, 0), loc=(ox, oy + 0.1, oz + 1.1), mat=mats['matte_grey'], col=col)
        hood.parent = root
        screen_l = abs_style.create_box(f"{name}_ScreenL", size=(0.7, 0.05, 0.4), rot=(math.radians(30), 0, 0), loc=(ox - 0.7, oy - 0.25, oz + 1.2), mat=mats['holo_green'], col=col)
        screen_l.parent = root
        screen_r = abs_style.create_box(f"{name}_ScreenR", size=(0.7, 0.05, 0.4), rot=(math.radians(30), 0, 0), loc=(ox + 0.7, oy - 0.25, oz + 1.2), mat=mats['amber_crt'], col=col)
        screen_r.parent = root

    elif asset_id == 79: # SM_Mod_79_Hab_Tactical_Holomap_Table
        base = abs_style.create_cylinder(f"{name}_Base", radius=1.3, depth=0.8, loc=(ox, oy, oz + 0.4), mat=mats['navy_blue'], col=col)
        base.parent = root
        ring = abs_style.create_torus(f"{name}_EmmiterRing", major_r=1.35, minor_r=0.08, loc=(ox, oy, oz + 0.8), mat=mats['steel_bright'], col=col)
        ring.parent = root
        holo_grid = abs_style.create_cylinder(f"{name}_HoloCone", radius=1.1, depth=0.05, loc=(ox, oy, oz + 0.82), mat=mats['holo_green'], col=col)
        holo_grid.parent = root
        ship_wire = abs_style.create_cone(f"{name}_HoloShipWire", radius1=0.4, radius2=0.0, depth=0.8, rot=(0, math.radians(90), 0), loc=(ox, oy, oz + 1.4), mat=mats['holo_green'], col=col)
        ship_wire.parent = root

    elif asset_id == 80: # SM_Mod_80_Hab_Captains_Command_Chair
        ped = abs_style.create_cylinder(f"{name}_Pedestal", radius=0.25, depth=0.5, loc=(ox, oy, oz + 0.25), mat=mats['navy_blue'], col=col)
        ped.parent = root
        seat = abs_style.create_box(f"{name}_Seat", size=(0.8, 0.8, 0.2), loc=(ox, oy, oz + 0.55), mat=mats['leather'], col=col)
        seat.parent = root
        back = abs_style.create_box(f"{name}_Back", size=(0.8, 0.2, 0.9), loc=(ox, oy + 0.3, oz + 1.05), mat=mats['leather'], col=col)
        back.parent = root
        arm_l = abs_style.create_box(f"{name}_ArmL", size=(0.15, 0.6, 0.1), loc=(ox - 0.45, oy, oz + 0.75), mat=mats['steel_bright'], col=col)
        arm_l.parent = root
        arm_r = abs_style.create_box(f"{name}_ArmR", size=(0.15, 0.6, 0.1), loc=(ox + 0.45, oy, oz + 0.75), mat=mats['steel_bright'], col=col)
        arm_r.parent = root

    elif asset_id == 81: # SM_Mod_81_Hab_Comms_Relay_Station
        rack = abs_style.create_box(f"{name}_Rack", size=(1.6, 0.8, 2.8), loc=(ox, oy, oz + 1.4), mat=mats['navy_blue'], col=col)
        rack.parent = root
        for rz in [0.7, 1.4, 2.1]:
            unit = abs_style.create_box(f"{name}_SubUnit_{rz}", size=(1.4, 0.08, 0.5), loc=(ox, oy - 0.38, oz + rz), mat=mats['matte_grey'], col=col)
            unit.parent = root
            dial = abs_style.create_cylinder(f"{name}_Dial_{rz}", radius=0.08, depth=0.05, rot=(math.radians(90), 0, 0), loc=(ox + 0.4, oy - 0.42, oz + rz), mat=mats['amber_crt'], col=col)
            dial.parent = root

    elif asset_id == 82: # SM_Mod_82_Hab_Sensors_Ops_Station
        ops_bench = abs_style.create_box(f"{name}_Bench", size=(1.8, 1.0, 0.9), loc=(ox, oy, oz + 0.45), mat=mats['navy_blue'], col=col)
        ops_bench.parent = root
        dish = abs_style.create_cone(f"{name}_RadarScreen", radius1=0.6, radius2=0.0, depth=0.2, rot=(math.radians(45), 0, 0), loc=(ox, oy - 0.1, oz + 1.25), mat=mats['holo_green'], col=col)
        dish.parent = root

    elif asset_id == 83: # SM_Mod_83_Hab_Escape_Pod_Access_Tube
        ring = abs_style.create_torus(f"{name}_OuterHatchRing", major_r=1.4, minor_r=0.2, rot=(math.radians(90), 0, 0), loc=(ox, oy, oz + 1.7), mat=mats['hazard_yellow'], col=col)
        ring.parent = root
        door = abs_style.create_cylinder(f"{name}_PodHatch", radius=1.2, depth=0.25, rot=(math.radians(90), 0, 0), loc=(ox, oy, oz + 1.7), mat=mats['navy_blue'], col=col)
        door.parent = root
        lever = abs_style.create_cylinder(f"{name}_EjectLever", radius=0.05, depth=0.6, loc=(ox + 1.1, oy - 0.25, oz + 1.7), mat=mats['amber_crt'], col=col)
        lever.parent = root

    elif asset_id == 84: # SM_Mod_84_Hab_Armory_Weapon_Locker
        rack_w = abs_style.create_box(f"{name}_Locker", size=(2.0, 0.7, 2.6), loc=(ox, oy, oz + 1.3), mat=mats['matte_grey'], col=col)
        rack_w.parent = root
        for slot in range(4):
            sx = ox - 0.6 + slot * 0.4
            cradle = abs_style.create_box(f"{name}_Slot_{slot}", size=(0.15, 0.4, 1.8), loc=(sx, oy - 0.1, oz + 1.3), mat=mats['navy_blue'], col=col)
            cradle.parent = root
            laser_lock = abs_style.create_cylinder(f"{name}_LockBeam_{slot}", radius=0.02, depth=0.2, rot=(0, math.radians(90), 0), loc=(sx, oy - 0.32, oz + 1.8), mat=mats['amber_crt'], col=col)
            laser_lock.parent = root

    elif asset_id == 85: # SM_Mod_85_Hab_EVA_Suit_Stowage_Bay
        alcove = abs_style.create_box(f"{name}_Alcove", size=(1.8, 1.2, 2.8), loc=(ox, oy, oz + 1.4), mat=mats['navy_blue'], col=col)
        alcove.parent = root
        hang_bar = abs_style.create_cylinder(f"{name}_Hanger", radius=0.05, depth=1.4, rot=(0, math.radians(90), 0), loc=(ox, oy, oz + 2.4), mat=mats['steel_bright'], col=col)
        hang_bar.parent = root
        ped = abs_style.create_cylinder(f"{name}_FootPed", radius=0.45, depth=0.15, loc=(ox, oy, oz + 0.1), mat=mats['hazard_yellow'], col=col)
        ped.parent = root

    elif asset_id == 86: # SM_Mod_86_Hab_Maintenance_Crawlway_Duct
        duct = abs_style.create_box(f"{name}_Duct", size=(1.6, 3.8, 1.6), loc=(ox, oy, oz + 0.8), mat=mats['matte_grey'], col=col)
        duct.parent = root
        ring_fr = abs_style.create_torus(f"{name}_Flange", major_r=0.9, minor_r=0.1, rot=(math.radians(90), 0, 0), loc=(ox, oy - 1.8, oz + 0.8), mat=mats['hazard_yellow'], col=col)
        ring_fr.parent = root

    elif asset_id == 87: # SM_Mod_87_Hab_LifeSupport_CO2_Scrubber
        tank = abs_style.create_cylinder(f"{name}_Canister", radius=0.6, depth=2.4, loc=(ox, oy, oz + 1.2), mat=mats['navy_blue'], col=col)
        tank.parent = root
        gauge = abs_style.create_cylinder(f"{name}_PPMDisplay", radius=0.18, depth=0.08, rot=(math.radians(90), 0, 0), loc=(ox, oy - 0.62, oz + 1.6), mat=mats['holo_green'], col=col)
        gauge.parent = root
        valve = abs_style.create_torus(f"{name}_PurgeValve", major_r=0.25, minor_r=0.05, rot=(math.radians(90), 0, 0), loc=(ox, oy - 0.62, oz + 0.8), mat=mats['amber_crt'], col=col)
        valve.parent = root

    elif asset_id == 88: # SM_Mod_88_Hab_Observation_Dome_Skylight
        rim = abs_style.create_cylinder(f"{name}_Collar", radius=1.6, depth=0.3, loc=(ox, oy, oz + 3.1), mat=mats['navy_blue'], col=col)
        rim.parent = root
        glass_dome = abs_style.create_cylinder(f"{name}_Dome", radius=1.45, depth=0.2, loc=(ox, oy, oz + 3.25), mat=mats['holo_green'], col=col)
        glass_dome.parent = root

    elif asset_id == 89: # SM_Mod_89_Hab_Heavy_Blast_Shutter_Curtain
        frame = abs_style.create_box(f"{name}_Frame", size=(3.2, 0.4, 2.6), loc=(ox, oy, oz + 1.5), mat=mats['matte_grey'], col=col)
        frame.parent = root
        for slat in range(5):
            slat_b = abs_style.create_box(f"{name}_Slat_{slat}", size=(2.8, 0.12, 0.4), loc=(ox, oy, oz + 0.5 + slat * 0.45), mat=mats['navy_blue'], col=col)
            slat_b.parent = root

    elif asset_id == 90: # SM_Mod_90_Hab_Cargo_Loading_Ramp_Modular
        ramp = abs_style.create_box(f"{name}_RampDeck", size=(3.2, 3.6, 0.18), rot=(math.radians(15), 0, 0), loc=(ox, oy, oz + 0.6), mat=mats['matte_grey'], col=col)
        ramp.parent = root
        edge_l = abs_style.create_box(f"{name}_CurbL", size=(0.15, 3.6, 0.25), rot=(math.radians(15), 0, 0), loc=(ox - 1.55, oy, oz + 0.65), mat=mats['hazard_yellow'], col=col)
        edge_l.parent = root
        edge_r = abs_style.create_box(f"{name}_CurbR", size=(0.15, 3.6, 0.25), rot=(math.radians(15), 0, 0), loc=(ox + 1.55, oy, oz + 0.65), mat=mats['hazard_yellow'], col=col)
        edge_r.parent = root

    return root

KIT5_ASSETS = [
    (73, "SM_Mod_73_Hab_Crew_Bunk_Pod_Double"),
    (74, "SM_Mod_74_Hab_Galley_Food_Synthesizer"),
    (75, "SM_Mod_75_Hab_Sanitary_Shower_Module"),
    (76, "SM_Mod_76_Hab_Lockers_Storage_Row"),
    (77, "SM_Mod_77_Hab_Recreation_Mess_Table"),
    (78, "SM_Mod_78_Hab_Command_Helm_Console"),
    (79, "SM_Mod_79_Hab_Tactical_Holomap_Table"),
    (80, "SM_Mod_80_Hab_Captains_Command_Chair"),
    (81, "SM_Mod_81_Hab_Comms_Relay_Station"),
    (82, "SM_Mod_82_Hab_Sensors_Ops_Station"),
    (83, "SM_Mod_83_Hab_Escape_Pod_Access_Tube"),
    (84, "SM_Mod_84_Hab_Armory_Weapon_Locker"),
    (85, "SM_Mod_85_Hab_EVA_Suit_Stowage_Bay"),
    (86, "SM_Mod_86_Hab_Maintenance_Crawlway_Duct"),
    (87, "SM_Mod_87_Hab_LifeSupport_CO2_Scrubber"),
    (88, "SM_Mod_88_Hab_Observation_Dome_Skylight"),
    (89, "SM_Mod_89_Hab_Heavy_Blast_Shutter_Curtain"),
    (90, "SM_Mod_90_Hab_Cargo_Loading_Ramp_Modular"),
]

def generate_kit5_scene(save_blend=True):
    abs_style.reset_comic_scene()
    col = abs_style.create_collection("Kit5_Crew_Habitat_Command")
    mats = init_kit5_materials()
    
    spacing_x = 4.8
    spacing_y = 5.2
    ped_mat = abs_style.get_comic_material("Pedestal_K5", base_color=(0.08, 0.10, 0.14), roughness=0.35, metallic=0.7)
    
    for idx, (aid, aname) in enumerate(KIT5_ASSETS):
        col_idx = idx % 6
        row_idx = idx // 6
        x = (col_idx - 2.5) * spacing_x
        y = (row_idx - 1.0) * spacing_y
        
        ped = abs_style.create_box(f"Pedestal_{aname}", size=(4.2, 4.2, 0.25), loc=(x, y, -0.125), mat=ped_mat, col=col)
        build_asset(aid, aname, (x, y, 0.0), col, mats)
        
    floor_mat = abs_style.get_comic_material("Floor_K5", base_color=(0.02, 0.025, 0.035), roughness=0.25, metallic=0.85)
    abs_style.create_box("FloorK5", size=(38.0, 24.0, 0.1), loc=(0, 0, -0.2), mat=floor_mat, col=col)
    abs_style.setup_studio_lighting(sun_energy=3.8, rim_energy=2.4, fill_energy=1.2)
    abs_style.setup_camera(name="Camera_Kit5", loc=(0, -24, 15), target=(0, 0, 1.2), focal_length=32)
    
    if save_blend:
        blend_path = os.path.join(abs_style.PROJECT_ROOT, "Art", "Blender", "Catalogo_Modulares_Kit5_Habitat.blend")
        bpy.ops.wm.save_as_mainfile(filepath=blend_path)
        print(f"[+] Blend saved: {blend_path}")
        
    abs_style.render_and_save("Showcase_Modulares_Kit5_Habitat_18.png", res_x=2560, res_y=1440)

if __name__ == "__main__":
    generate_kit5_scene()

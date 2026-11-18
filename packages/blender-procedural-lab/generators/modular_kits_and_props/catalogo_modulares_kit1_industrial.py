# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Kit 1: Estructuras Industriales y Carguero Derelict (Activos 01 a 18 de 90)
# Blender 5.2 LTS - Modelado Parametrico, Shaders PBR Stylized y Freestyle Lineart

import bpy
import bmesh
import math
import os
import sys

# Agregar ruta para importar modulo comun
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

import astra_blender_styling as abs_style

def init_kit1_materials():
    mats = {}
    mats['hazard_yellow'] = abs_style.get_comic_material("K1_Hazard_Yellow", base_color=(0.95, 0.65, 0.10), roughness=0.35, metallic=0.1, tex_pack="T_Trim_Industrial")
    mats['rust_hull'] = abs_style.get_comic_material("K1_Rust_Hull", base_color=(0.55, 0.28, 0.16), roughness=0.55, metallic=0.35, tex_pack="T_Derelict_Rust_Plates", tex_mix=0.50)
    mats['teal_metal'] = abs_style.get_comic_material("K1_Teal_Metal", base_color=(0.12, 0.44, 0.42), roughness=0.45, metallic=0.15, tex_pack="T_Battered_Armor_Impacts")
    mats['steel_dark'] = abs_style.get_comic_material("K1_Steel_Dark", base_color=(0.20, 0.22, 0.25), roughness=0.38, metallic=0.85, tex_pack="T_Steel_Plates")
    mats['steel_bright'] = abs_style.get_comic_material("K1_Steel_Bright", base_color=(0.75, 0.78, 0.82), roughness=0.20, metallic=0.92)
    mats['grate_steel'] = abs_style.get_comic_material("K1_Grate_Steel", base_color=(0.25, 0.26, 0.30), roughness=0.40, metallic=0.80, tex_pack="T_Grating_Walkway")
    mats['toxic_acid'] = abs_style.get_comic_material("K1_Toxic_Acid", base_color=(0.04, 0.88, 0.14), roughness=0.10, metallic=0.0,
                                                       emissive_color=(0.05, 0.95, 0.16, 1.0), emissive_strength=1.6)
    mats['pipe_olive'] = abs_style.get_comic_material("K1_Pipe_Olive", base_color=(0.28, 0.38, 0.22), roughness=0.45, metallic=0.45, tex_pack="T_Corroded_Acid_Pipes")
    mats['valve_red'] = abs_style.get_comic_material("K1_Valve_Red", base_color=(0.85, 0.12, 0.10), roughness=0.30, metallic=0.2)
    mats['emissive_cyan'] = abs_style.get_comic_material("K1_Emissive_Cyan", base_color=(0.1, 0.8, 1.0), roughness=0.1,
                                                         emissive_color=(0.1, 0.85, 1.0, 1.0), emissive_strength=2.2)
    return mats

def build_asset(asset_id, name, origin, col, mats):
    root = bpy.data.objects.new(f"Root_{name}", None)
    root.location = (0, 0, 0)
    col.objects.link(root)
    
    ox, oy, oz = origin
    
    if asset_id == 1: # SM_Mod_01_Cargo_Wall_Solid_400x350
        w = abs_style.create_box(f"{name}_Wall", size=(4.0, 0.4, 3.5), loc=(ox, oy, oz + 1.75), mat=mats['rust_hull'], col=col)
        w.parent = root
        v1 = abs_style.create_box(f"{name}_RibL", size=(0.25, 0.5, 3.5), loc=(ox - 1.8, oy, oz + 1.75), mat=mats['hazard_yellow'], col=col)
        v1.parent = root
        v2 = abs_style.create_box(f"{name}_RibR", size=(0.25, 0.5, 3.5), loc=(ox + 1.8, oy, oz + 1.75), mat=mats['hazard_yellow'], col=col)
        v2.parent = root
        hb = abs_style.create_box(f"{name}_BeamH", size=(3.8, 0.48, 0.25), loc=(ox, oy, oz + 2.6), mat=mats['steel_dark'], col=col)
        hb.parent = root
        
    elif asset_id == 2: # SM_Mod_02_Cargo_Doorway_Bulkhead_400x350 (Marco de compuerta abierto 100% transitable)
        fr_l = abs_style.create_box(f"{name}_PostL", size=(0.8, 0.5, 3.5), loc=(ox - 1.6, oy, oz + 1.75), mat=mats['hazard_yellow'], col=col)
        fr_l.parent = root
        fr_r = abs_style.create_box(f"{name}_PostR", size=(0.8, 0.5, 3.5), loc=(ox + 1.6, oy, oz + 1.75), mat=mats['hazard_yellow'], col=col)
        fr_r.parent = root
        fr_t = abs_style.create_box(f"{name}_Lintel", size=(2.4, 0.5, 0.8), loc=(ox, oy, oz + 3.1), mat=mats['steel_dark'], col=col)
        fr_t.parent = root
        jamb_l = abs_style.create_box(f"{name}_JambL", size=(0.12, 0.54, 2.7), loc=(ox - 1.15, oy, oz + 1.35), mat=mats['steel_dark'], col=col)
        jamb_l.parent = root
        jamb_r = abs_style.create_box(f"{name}_JambR", size=(0.12, 0.54, 2.7), loc=(ox + 1.15, oy, oz + 1.35), mat=mats['steel_dark'], col=col)
        jamb_r.parent = root
        beacon = abs_style.create_box(f"{name}_HeaderBeacon", size=(1.2, 0.56, 0.14), loc=(ox, oy, oz + 2.85), mat=mats['emissive_cyan'], col=col)
        beacon.parent = root

    elif asset_id == 3: # SM_Mod_03_Cargo_Floor_Grate_400x400
        fr = abs_style.create_box(f"{name}_Frame", size=(4.0, 4.0, 0.2), loc=(ox, oy, oz + 0.1), mat=mats['steel_dark'], col=col)
        fr.parent = root
        gr = abs_style.create_box(f"{name}_Grate", size=(3.6, 3.6, 0.08), loc=(ox, oy, oz + 0.16), mat=mats['grate_steel'], col=col)
        gr.parent = root
        for i in range(-1, 2):
            bm = abs_style.create_box(f"{name}_Support_{i}", size=(0.15, 3.8, 0.18), loc=(ox + i*1.2, oy, oz + 0.09), mat=mats['hazard_yellow'], col=col)
            bm.parent = root

    elif asset_id == 4: # SM_Mod_04_Cargo_Ceiling_Girder_400x400
        ceil = abs_style.create_box(f"{name}_Panel", size=(4.0, 4.0, 0.15), loc=(ox, oy, oz + 3.42), mat=mats['rust_hull'], col=col)
        ceil.parent = root
        for gx in [-1.3, 0.0, 1.3]:
            g = abs_style.create_box(f"{name}_GirderX_{gx}", size=(0.2, 4.0, 0.35), loc=(ox + gx, oy, oz + 3.2), mat=mats['hazard_yellow'], col=col)
            g.parent = root
        lgt = abs_style.create_box(f"{name}_LightStrip", size=(2.8, 0.3, 0.08), loc=(ox, oy, oz + 3.1), mat=mats['emissive_cyan'], col=col)
        lgt.parent = root

    elif asset_id == 5: # SM_Mod_05_Catwalk_Straight_400x150
        floor = abs_style.create_box(f"{name}_Deck", size=(4.0, 1.5, 0.15), loc=(ox, oy, oz + 1.5), mat=mats['grate_steel'], col=col)
        floor.parent = root
        rail_t = abs_style.create_cylinder(f"{name}_RailTop", radius=0.04, depth=4.0, rot=(0, math.radians(90), 0), loc=(ox, oy + 0.7, oz + 2.5), mat=mats['hazard_yellow'], col=col)
        rail_t.parent = root
        rail_m = abs_style.create_cylinder(f"{name}_RailMid", radius=0.03, depth=4.0, rot=(0, math.radians(90), 0), loc=(ox, oy + 0.7, oz + 2.0), mat=mats['hazard_yellow'], col=col)
        rail_m.parent = root
        for px in [-1.8, -0.6, 0.6, 1.8]:
            post = abs_style.create_cylinder(f"{name}_Post_{px}", radius=0.04, depth=1.0, loc=(ox + px, oy + 0.7, oz + 2.0), mat=mats['steel_dark'], col=col)
            post.parent = root

    elif asset_id == 6: # SM_Mod_06_Catwalk_Stairs_400x350
        stringer1 = abs_style.create_box(f"{name}_StrL", size=(0.1, 3.8, 0.3), rot=(math.radians(45), 0, 0), loc=(ox - 0.7, oy, oz + 1.75), mat=mats['steel_dark'], col=col)
        stringer1.parent = root
        stringer2 = abs_style.create_box(f"{name}_StrR", size=(0.1, 3.8, 0.3), rot=(math.radians(45), 0, 0), loc=(ox + 0.7, oy, oz + 1.75), mat=mats['steel_dark'], col=col)
        stringer2.parent = root
        for s in range(8):
            sy = -1.4 + s * 0.4
            sz = 0.2 + s * 0.4
            step = abs_style.create_box(f"{name}_Step_{s}", size=(1.3, 0.35, 0.06), loc=(ox, oy + sy, oz + sz), mat=mats['grate_steel'], col=col)
            step.parent = root

    elif asset_id == 7: # SM_Mod_07_Pipe_Cluster_Triple_400cm
        for idx, (py, pz, r, mat) in enumerate([(-0.3, 1.8, 0.16, mats['pipe_olive']), (0.0, 2.2, 0.22, mats['steel_dark']), (0.3, 1.7, 0.14, mats['rust_hull'])]):
            p = abs_style.create_cylinder(f"{name}_Pipe_{idx}", radius=r, depth=4.0, rot=(0, math.radians(90), 0), loc=(ox, oy + py, oz + pz), mat=mat, col=col)
            p.parent = root
            for fx in [-1.5, 0.0, 1.5]:
                fl = abs_style.create_torus(f"{name}_Flange_{idx}_{fx}", major_r=r+0.05, minor_r=0.03, rot=(0, math.radians(90), 0), loc=(ox + fx, oy + py, oz + pz), mat=mats['steel_bright'], col=col)
                fl.parent = root
        v = abs_style.create_cylinder(f"{name}_Valve", radius=0.2, depth=0.06, rot=(math.radians(90), 0, 0), loc=(ox, oy - 0.3, oz + 2.1), mat=mats['valve_red'], col=col)
        v.parent = root

    elif asset_id == 8: # SM_Mod_08_Cargo_Container_Standard
        body = abs_style.create_box(f"{name}_Body", size=(3.6, 1.8, 1.8), loc=(ox, oy, oz + 0.9), mat=mats['teal_metal'], col=col)
        body.parent = root
        for cx in [-1.8, 1.8]:
            for cy in [-0.9, 0.9]:
                c = abs_style.create_box(f"{name}_Corner_{cx}_{cy}", size=(0.16, 0.16, 1.82), loc=(ox + cx, oy + cy, oz + 0.9), mat=mats['hazard_yellow'], col=col)
                c.parent = root
        door_line = abs_style.create_box(f"{name}_DoorSeam", size=(0.04, 0.04, 1.7), loc=(ox + 1.81, oy, oz + 0.9), mat=mats['steel_dark'], col=col)
        door_line.parent = root

    elif asset_id == 9: # SM_Mod_09_Hazard_Waste_Trench_400x100
        curb_l = abs_style.create_box(f"{name}_CurbL", size=(4.0, 0.25, 0.4), loc=(ox, oy - 0.5, oz + 0.2), mat=mats['steel_dark'], col=col)
        curb_l.parent = root
        curb_r = abs_style.create_box(f"{name}_CurbR", size=(4.0, 0.25, 0.4), loc=(ox, oy + 0.5, oz + 0.2), mat=mats['steel_dark'], col=col)
        curb_r.parent = root
        acid = abs_style.create_box(f"{name}_ToxicLiquid", size=(3.9, 0.75, 0.15), loc=(ox, oy, oz + 0.1), mat=mats['toxic_acid'], col=col)
        acid.parent = root
        for gx in [-1.3, 0.0, 1.3]:
            sec = abs_style.create_box(f"{name}_GrateSec_{gx}", size=(1.0, 0.85, 0.05), loc=(ox + gx, oy, oz + 0.38), mat=mats['grate_steel'], col=col)
            sec.parent = root

    elif asset_id == 10: # SM_Mod_10_Heavy_Blast_Door_Single
        frame = abs_style.create_box(f"{name}_Frame", size=(2.8, 0.6, 3.4), loc=(ox, oy, oz + 1.7), mat=mats['steel_dark'], col=col)
        frame.parent = root
        slab = abs_style.create_box(f"{name}_Slab", size=(2.2, 0.35, 3.0), loc=(ox, oy, oz + 1.5), mat=mats['rust_hull'], col=col)
        slab.parent = root
        stripe = abs_style.create_box(f"{name}_HazardStripe", size=(2.0, 0.37, 0.35), loc=(ox, oy, oz + 1.2), mat=mats['hazard_yellow'], col=col)
        stripe.parent = root

    elif asset_id == 11: # SM_Mod_11_Overhead_Crane_Rail_400cm
        beam = abs_style.create_box(f"{name}_IBeam", size=(4.0, 0.35, 0.5), loc=(ox, oy, oz + 3.1), mat=mats['hazard_yellow'], col=col)
        beam.parent = root
        trolley = abs_style.create_box(f"{name}_Trolley", size=(0.8, 0.6, 0.4), loc=(ox, oy, oz + 2.7), mat=mats['steel_dark'], col=col)
        trolley.parent = root
        hook = abs_style.create_torus(f"{name}_Hook", major_r=0.25, minor_r=0.06, loc=(ox, oy, oz + 2.2), mat=mats['steel_bright'], col=col)
        hook.parent = root

    elif asset_id == 12: # SM_Mod_12_Structural_Column_IBeam_350cm
        col_ib = abs_style.create_box(f"{name}_FlangeL", size=(0.4, 0.08, 3.5), loc=(ox, oy - 0.2, oz + 1.75), mat=mats['rust_hull'], col=col)
        col_ib.parent = root
        col_ib2 = abs_style.create_box(f"{name}_FlangeR", size=(0.4, 0.08, 3.5), loc=(ox, oy + 0.2, oz + 1.75), mat=mats['rust_hull'], col=col)
        col_ib2.parent = root
        web = abs_style.create_box(f"{name}_Web", size=(0.1, 0.35, 3.5), loc=(ox, oy, oz + 1.75), mat=mats['steel_dark'], col=col)
        web.parent = root
        base = abs_style.create_box(f"{name}_BasePlate", size=(0.7, 0.7, 0.15), loc=(ox, oy, oz + 0.075), mat=mats['hazard_yellow'], col=col)
        base.parent = root

    elif asset_id == 13: # SM_Mod_13_Ventilation_Intake_Louver
        box_v = abs_style.create_box(f"{name}_Box", size=(1.8, 0.4, 1.8), loc=(ox, oy, oz + 1.8), mat=mats['steel_dark'], col=col)
        box_v.parent = root
        for lv in range(6):
            louver = abs_style.create_box(f"{name}_Louver_{lv}", size=(1.5, 0.04, 0.15), rot=(math.radians(35), 0, 0), loc=(ox, oy + 0.15, oz + 1.15 + lv*0.22), mat=mats['hazard_yellow'], col=col)
            louver.parent = root

    elif asset_id == 14: # SM_Mod_14_Cable_Tray_Suspended_400cm
        tray = abs_style.create_box(f"{name}_Tray", size=(4.0, 0.8, 0.1), loc=(ox, oy, oz + 3.0), mat=mats['grate_steel'], col=col)
        tray.parent = root
        for cx, r, col_m in [(-0.2, 0.06, mats['valve_red']), (0.0, 0.08, mats['hazard_yellow']), (0.2, 0.07, mats['steel_dark'])]:
            cbl = abs_style.create_cylinder(f"{name}_Cable_{cx}", radius=r, depth=4.0, rot=(0, math.radians(90), 0), loc=(ox, oy + cx, oz + 3.12), mat=col_m, col=col)
            cbl.parent = root
        hanger1 = abs_style.create_cylinder(f"{name}_Hanger1", radius=0.03, depth=0.8, loc=(ox - 1.5, oy, oz + 3.4), mat=mats['steel_bright'], col=col)
        hanger1.parent = root
        hanger2 = abs_style.create_cylinder(f"{name}_Hanger2", radius=0.03, depth=0.8, loc=(ox + 1.5, oy, oz + 3.4), mat=mats['steel_bright'], col=col)
        hanger2.parent = root

    elif asset_id == 15: # SM_Mod_15_Airlock_Interlock_Chamber
        cyl = abs_style.create_cylinder(f"{name}_Chamber", radius=1.6, depth=3.0, rot=(0, 0, 0), loc=(ox, oy, oz + 1.5), mat=mats['rust_hull'], col=col)
        cyl.parent = root
        ring1 = abs_style.create_torus(f"{name}_RingTop", major_r=1.65, minor_r=0.1, loc=(ox, oy, oz + 2.7), mat=mats['hazard_yellow'], col=col)
        ring1.parent = root
        ring2 = abs_style.create_torus(f"{name}_RingBot", major_r=1.65, minor_r=0.1, loc=(ox, oy, oz + 0.3), mat=mats['hazard_yellow'], col=col)
        ring2.parent = root
        porthole = abs_style.create_cylinder(f"{name}_Glass", radius=0.45, depth=0.2, rot=(math.radians(90), 0, 0), loc=(ox, oy - 1.6, oz + 1.6), mat=mats['emissive_cyan'], col=col)
        porthole.parent = root

    elif asset_id == 16: # SM_Mod_16_Floor_Hatch_Maintenance
        rim = abs_style.create_box(f"{name}_Rim", size=(1.8, 1.8, 0.15), loc=(ox, oy, oz + 0.08), mat=mats['steel_dark'], col=col)
        rim.parent = root
        hatch = abs_style.create_box(f"{name}_Plate", size=(1.5, 1.5, 0.12), loc=(ox, oy, oz + 0.12), mat=mats['hazard_yellow'], col=col)
        hatch.parent = root
        wheel = abs_style.create_torus(f"{name}_HandleWheel", major_r=0.25, minor_r=0.04, loc=(ox, oy, oz + 0.22), mat=mats['valve_red'], col=col)
        wheel.parent = root

    elif asset_id == 17: # SM_Mod_17_Corner_Reinforcement_Brace
        diag = abs_style.create_box(f"{name}_Strut", size=(0.25, 0.25, 2.2), rot=(0, math.radians(45), 0), loc=(ox, oy, oz + 1.6), mat=mats['hazard_yellow'], col=col)
        diag.parent = root
        pad1 = abs_style.create_box(f"{name}_PadTop", size=(0.4, 0.4, 0.12), loc=(ox + 0.75, oy, oz + 2.35), mat=mats['steel_dark'], col=col)
        pad1.parent = root
        pad2 = abs_style.create_box(f"{name}_PadBot", size=(0.4, 0.4, 0.12), loc=(ox - 0.75, oy, oz + 0.85), mat=mats['steel_dark'], col=col)
        pad2.parent = root

    elif asset_id == 18: # SM_Mod_18_Hazard_Barrier_Bollard_Set
        base_b = abs_style.create_box(f"{name}_Base", size=(3.2, 0.5, 0.1), loc=(ox, oy, oz + 0.05), mat=mats['steel_dark'], col=col)
        base_b.parent = root
        for bx in [-1.2, 0.0, 1.2]:
            b = abs_style.create_cylinder(f"{name}_Post_{bx}", radius=0.14, depth=1.1, loc=(ox + bx, oy, oz + 0.6), mat=mats['hazard_yellow'], col=col)
            b.parent = root
            cap = abs_style.create_cylinder(f"{name}_Cap_{bx}", radius=0.16, depth=0.08, loc=(ox + bx, oy, oz + 1.15), mat=mats['steel_bright'], col=col)
            cap.parent = root
        chain = abs_style.create_cylinder(f"{name}_Bar", radius=0.04, depth=2.8, rot=(0, math.radians(90), 0), loc=(ox, oy, oz + 0.85), mat=mats['valve_red'], col=col)
        chain.parent = root

    return root

KIT1_ASSETS = [
    (1, "SM_Mod_01_Cargo_Wall_Solid_400x350"),
    (2, "SM_Mod_02_Cargo_Doorway_Bulkhead_400x350"),
    (3, "SM_Mod_03_Cargo_Floor_Grate_400x400"),
    (4, "SM_Mod_04_Cargo_Ceiling_Girder_400x400"),
    (5, "SM_Mod_05_Catwalk_Straight_400x150"),
    (6, "SM_Mod_06_Catwalk_Stairs_400x350"),
    (7, "SM_Mod_07_Pipe_Cluster_Triple_400cm"),
    (8, "SM_Mod_08_Cargo_Container_Standard"),
    (9, "SM_Mod_09_Hazard_Waste_Trench_400x100"),
    (10, "SM_Mod_10_Heavy_Blast_Door_Single"),
    (11, "SM_Mod_11_Overhead_Crane_Rail_400cm"),
    (12, "SM_Mod_12_Structural_Column_IBeam_350cm"),
    (13, "SM_Mod_13_Ventilation_Intake_Louver"),
    (14, "SM_Mod_14_Cable_Tray_Suspended_400cm"),
    (15, "SM_Mod_15_Airlock_Interlock_Chamber"),
    (16, "SM_Mod_16_Floor_Hatch_Maintenance"),
    (17, "SM_Mod_17_Corner_Reinforcement_Brace"),
    (18, "SM_Mod_18_Hazard_Barrier_Bollard_Set"),
]

def generate_kit1_scene(save_blend=True):
    abs_style.reset_comic_scene()
    col = abs_style.create_collection("Kit1_Industrial_Derelict")
    mats = init_kit1_materials()
    
    # Grid de exhibición 6 columnas x 3 filas
    spacing_x = 4.8
    spacing_y = 5.2
    
    ped_mat = abs_style.get_comic_material("Pedestal_K1", base_color=(0.08, 0.09, 0.12), roughness=0.5, metallic=0.6)
    
    for idx, (aid, aname) in enumerate(KIT1_ASSETS):
        col_idx = idx % 6
        row_idx = idx // 6
        x = (col_idx - 2.5) * spacing_x
        y = (row_idx - 1.0) * spacing_y
        
        # Pedestal
        ped = abs_style.create_box(f"Pedestal_{aname}", size=(4.2, 4.2, 0.25), loc=(x, y, -0.125), mat=ped_mat, col=col)
        build_asset(aid, aname, (x, y, 0.0), col, mats)
        
    floor_mat = abs_style.get_comic_material("Floor_K1", base_color=(0.02, 0.025, 0.035), roughness=0.25, metallic=0.85)
    abs_style.create_box("FloorK1", size=(38.0, 24.0, 0.1), loc=(0, 0, -0.2), mat=floor_mat, col=col)
    abs_style.setup_studio_lighting(sun_energy=3.8, rim_energy=2.4, fill_energy=1.2)
    abs_style.setup_camera(name="Camera_Kit1", loc=(0, -24, 15), target=(0, 0, 1.2), focal_length=32)
    
    if save_blend:
        blend_path = os.path.join(abs_style.PROJECT_ROOT, "Art", "Blender", "Catalogo_Modulares_Kit1_Industrial.blend")
        bpy.ops.wm.save_as_mainfile(filepath=blend_path)
        print(f"[+] Blend saved: {blend_path}")
        
    abs_style.render_and_save("Showcase_Modulares_Kit1_Industrial_18.png", res_x=2560, res_y=1440)

if __name__ == "__main__":
    generate_kit1_scene()

# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Kit 2: Crucero de Lujo Celestia Art Deco (Activos 19 a 36 de 90)
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

def init_kit2_materials():
    mats = {}
    mats['velvet'] = abs_style.get_comic_material("K2_Burgundy_Velvet", base_color=(0.16, 0.008, 0.018), roughness=0.82, metallic=0.0, tex_pack="T_Luxury_Quilted_Velvet_Leather", tex_mix=0.30, blend_type='MULTIPLY')
    mats['wood'] = abs_style.get_comic_material("K2_Mahogany_Wood", base_color=(0.28, 0.12, 0.06), roughness=0.32, metallic=0.0, tex_pack="T_Luxury_Walnut_Wood_Panels")
    mats['gold'] = abs_style.get_comic_material("K2_ArtDeco_Gold", base_color=(0.95, 0.74, 0.20), roughness=0.22, metallic=0.92, tex_pack="T_Luxury_ArtDeco_Gilded_Brass")
    mats['marble'] = abs_style.get_comic_material("K2_Carrara_Marble", base_color=(0.85, 0.85, 0.83), roughness=0.18, metallic=0.0, tex_pack="T_Luxury_Marble_Gold_Inlay")
    mats['glass'] = abs_style.get_comic_material("K2_Mirror_Glass", base_color=(0.90, 0.94, 0.96), roughness=0.05, metallic=0.98)
    mats['glow'] = abs_style.get_comic_material("K2_Lamp_Glow", base_color=(1.0, 0.78, 0.35), roughness=0.2, metallic=0.0, emissive_color=(1.0, 0.78, 0.35, 1.0), emissive_strength=2.2)
    mats['obsidian'] = abs_style.get_comic_material("K2_Obsidian_Black", base_color=(0.04, 0.04, 0.05), roughness=0.15, metallic=0.3)
    return mats

def build_asset(asset_id, name, origin, col, mats):
    root = bpy.data.objects.new(f"Root_{name}", None)
    root.location = (0, 0, 0)
    col.objects.link(root)
    
    ox, oy, oz = origin
    
    if asset_id == 19: # SM_Mod_19_Deco_Wall_Boiserie_400x350
        w = abs_style.create_box(f"{name}_Wall", size=(4.0, 0.4, 3.5), loc=(ox, oy, oz + 1.75), mat=mats['wood'], col=col)
        w.parent = root
        for px in [-1.2, 0.0, 1.2]:
            mld = abs_style.create_box(f"{name}_Molding_{px}", size=(0.9, 0.45, 2.6), loc=(ox + px, oy, oz + 1.8), mat=mats['gold'], col=col)
            mld.parent = root
            ins = abs_style.create_box(f"{name}_Inset_{px}", size=(0.8, 0.46, 2.5), loc=(ox + px, oy, oz + 1.8), mat=mats['wood'], col=col)
            ins.parent = root
        base = abs_style.create_box(f"{name}_Baseboard", size=(4.0, 0.46, 0.3), loc=(ox, oy, oz + 0.15), mat=mats['gold'], col=col)
        base.parent = root

    elif asset_id == 20: # SM_Mod_20_Deco_Arched_Portal_400x350 (Portal arqueado abierto 100% transitable)
        fr_l = abs_style.create_box(f"{name}_ColL", size=(0.8, 0.5, 3.5), loc=(ox - 1.6, oy, oz + 1.75), mat=mats['gold'], col=col)
        fr_l.parent = root
        fr_r = abs_style.create_box(f"{name}_ColR", size=(0.8, 0.5, 3.5), loc=(ox + 1.6, oy, oz + 1.75), mat=mats['gold'], col=col)
        fr_r.parent = root
        wall_fill = abs_style.create_box(f"{name}_SpandrelTop", size=(2.4, 0.45, 0.8), loc=(ox, oy, oz + 3.1), mat=mats['wood'], col=col)
        wall_fill.parent = root
        header_gold = abs_style.create_box(f"{name}_HeaderGold", size=(2.5, 0.52, 0.16), loc=(ox, oy, oz + 2.75), mat=mats['gold'], col=col)
        header_gold.parent = root

    elif asset_id == 21: # SM_Mod_21_Deco_Marble_Floor_Pattern_400x400
        slab = abs_style.create_box(f"{name}_Slab", size=(4.0, 4.0, 0.2), loc=(ox, oy, oz + 0.1), mat=mats['marble'], col=col)
        slab.parent = root
        brass_rim = abs_style.create_box(f"{name}_BrassInlay", size=(3.6, 3.6, 0.21), loc=(ox, oy, oz + 0.105), mat=mats['gold'], col=col)
        brass_rim.parent = root
        center = abs_style.create_box(f"{name}_CenterMarble", size=(3.4, 3.4, 0.22), loc=(ox, oy, oz + 0.11), mat=mats['marble'], col=col)
        center.parent = root

    elif asset_id == 22: # SM_Mod_22_Deco_Coffered_Ceiling_400x400
        ceiling = abs_style.create_box(f"{name}_Ceiling", size=(4.0, 4.0, 0.2), loc=(ox, oy, oz + 3.4), mat=mats['wood'], col=col)
        ceiling.parent = root
        for cx in [-1.0, 1.0]:
            for cy in [-1.0, 1.0]:
                coffer = abs_style.create_box(f"{name}_Coffer_{cx}_{cy}", size=(1.6, 1.6, 0.15), loc=(ox + cx, oy + cy, oz + 3.25), mat=mats['gold'], col=col)
                coffer.parent = root
                c_light = abs_style.create_box(f"{name}_CofferGlow_{cx}_{cy}", size=(1.2, 1.2, 0.05), loc=(ox + cx, oy + cy, oz + 3.2), mat=mats['glow'], col=col)
                c_light.parent = root

    elif asset_id == 23: # SM_Mod_23_Deco_Corinthian_Column_350cm
        shaft = abs_style.create_cylinder(f"{name}_Shaft", radius=0.35, depth=3.0, loc=(ox, oy, oz + 1.65), mat=mats['marble'], col=col)
        shaft.parent = root
        capital = abs_style.create_cone(f"{name}_Capital", radius1=0.6, radius2=0.35, depth=0.45, loc=(ox, oy, oz + 3.25), mat=mats['gold'], col=col)
        capital.parent = root
        base = abs_style.create_box(f"{name}_Base", size=(0.9, 0.9, 0.3), loc=(ox, oy, oz + 0.15), mat=mats['gold'], col=col)
        base.parent = root

    elif asset_id == 24: # SM_Mod_24_Deco_Chesterfield_Sofa_240cm
        cushion = abs_style.create_box(f"{name}_Seat", size=(2.4, 0.9, 0.4), loc=(ox, oy, oz + 0.35), mat=mats['velvet'], col=col)
        cushion.parent = root
        back = abs_style.create_box(f"{name}_Back", size=(2.4, 0.3, 0.7), loc=(ox, oy + 0.35, oz + 0.75), mat=mats['velvet'], col=col)
        back.parent = root
        arm_l = abs_style.create_cylinder(f"{name}_ArmL", radius=0.2, depth=0.9, rot=(math.radians(90), 0, 0), loc=(ox - 1.2, oy, oz + 0.55), mat=mats['velvet'], col=col)
        arm_l.parent = root
        arm_r = abs_style.create_cylinder(f"{name}_ArmR", radius=0.2, depth=0.9, rot=(math.radians(90), 0, 0), loc=(ox + 1.2, oy, oz + 0.55), mat=mats['velvet'], col=col)
        arm_r.parent = root
        for lx in [-1.1, 1.1]:
            for ly in [-0.35, 0.35]:
                leg = abs_style.create_cylinder(f"{name}_Leg_{lx}_{ly}", radius=0.04, depth=0.18, loc=(ox + lx, oy + ly, oz + 0.09), mat=mats['gold'], col=col)
                leg.parent = root

    elif asset_id == 25: # SM_Mod_25_Deco_Lounge_Armchair
        seat = abs_style.create_box(f"{name}_Seat", size=(0.95, 0.95, 0.35), loc=(ox, oy, oz + 0.35), mat=mats['velvet'], col=col)
        seat.parent = root
        back = abs_style.create_box(f"{name}_Back", size=(0.95, 0.25, 0.8), loc=(ox, oy + 0.35, oz + 0.8), mat=mats['velvet'], col=col)
        back.parent = root
        for lx in [-0.4, 0.4]:
            for ly in [-0.4, 0.4]:
                leg = abs_style.create_cylinder(f"{name}_Leg_{lx}_{ly}", radius=0.035, depth=0.2, loc=(ox + lx, oy + ly, oz + 0.1), mat=mats['gold'], col=col)
                leg.parent = root

    elif asset_id == 26: # SM_Mod_26_Deco_Gilded_Balustrade_400cm
        rail = abs_style.create_box(f"{name}_TopRail", size=(4.0, 0.15, 0.08), loc=(ox, oy, oz + 1.1), mat=mats['wood'], col=col)
        rail.parent = root
        base = abs_style.create_box(f"{name}_BasePlinth", size=(4.0, 0.2, 0.1), loc=(ox, oy, oz + 0.05), mat=mats['marble'], col=col)
        base.parent = root
        for bx in range(-5, 6):
            post = abs_style.create_cylinder(f"{name}_Baluster_{bx}", radius=0.035, depth=0.95, loc=(ox + bx*0.36, oy, oz + 0.58), mat=mats['gold'], col=col)
            post.parent = root

    elif asset_id == 27: # SM_Mod_27_Deco_Tiered_Chandelier
        tier1 = abs_style.create_torus(f"{name}_Tier1", major_r=0.9, minor_r=0.08, loc=(ox, oy, oz + 2.5), mat=mats['gold'], col=col)
        tier1.parent = root
        tier2 = abs_style.create_torus(f"{name}_Tier2", major_r=0.6, minor_r=0.06, loc=(ox, oy, oz + 2.2), mat=mats['gold'], col=col)
        tier2.parent = root
        tier3 = abs_style.create_torus(f"{name}_Tier3", major_r=0.3, minor_r=0.05, loc=(ox, oy, oz + 1.9), mat=mats['gold'], col=col)
        tier3.parent = root
        bulb = abs_style.create_cylinder(f"{name}_BulbCore", radius=0.15, depth=0.8, loc=(ox, oy, oz + 2.2), mat=mats['glow'], col=col)
        bulb.parent = root
        rod = abs_style.create_cylinder(f"{name}_StemRod", radius=0.02, depth=1.0, loc=(ox, oy, oz + 3.0), mat=mats['gold'], col=col)
        rod.parent = root

    elif asset_id == 28: # SM_Mod_28_Deco_Observatory_Porthole_Large
        rim = abs_style.create_torus(f"{name}_GoldRim", major_r=1.5, minor_r=0.15, rot=(math.radians(90), 0, 0), loc=(ox, oy, oz + 1.75), mat=mats['gold'], col=col)
        rim.parent = root
        glass = abs_style.create_cylinder(f"{name}_GlassPane", radius=1.45, depth=0.05, rot=(math.radians(90), 0, 0), loc=(ox, oy, oz + 1.75), mat=mats['glass'], col=col)
        glass.parent = root
        grill = abs_style.create_box(f"{name}_MuntinH", size=(2.9, 0.06, 0.04), loc=(ox, oy, oz + 1.75), mat=mats['gold'], col=col)
        grill.parent = root

    elif asset_id == 29: # SM_Mod_29_Deco_Wall_Sconce_Fan
        bracket = abs_style.create_box(f"{name}_Bracket", size=(0.15, 0.1, 0.3), loc=(ox, oy - 0.05, oz + 2.0), mat=mats['gold'], col=col)
        bracket.parent = root
        shade = abs_style.create_cone(f"{name}_FanShade", radius1=0.35, radius2=0.05, depth=0.5, rot=(0, 0, 0), loc=(ox, oy - 0.2, oz + 2.1), mat=mats['glow'], col=col)
        shade.parent = root

    elif asset_id == 30: # SM_Mod_30_Deco_Display_Cabinet_Vitrines
        case = abs_style.create_box(f"{name}_Case", size=(1.8, 0.6, 2.8), loc=(ox, oy, oz + 1.4), mat=mats['wood'], col=col)
        case.parent = root
        vitrine = abs_style.create_box(f"{name}_GlassWindow", size=(1.5, 0.45, 1.8), loc=(ox, oy - 0.1, oz + 1.6), mat=mats['glass'], col=col)
        vitrine.parent = root
        trim = abs_style.create_box(f"{name}_GoldTrim", size=(1.55, 0.48, 0.06), loc=(ox, oy - 0.1, oz + 2.5), mat=mats['gold'], col=col)
        trim.parent = root

    elif asset_id == 31: # SM_Mod_31_Deco_Grand_Staircase_Step_Section
        base = abs_style.create_box(f"{name}_Base", size=(2.4, 2.0, 0.3), loc=(ox, oy, oz + 0.15), mat=mats['marble'], col=col)
        base.parent = root
        for i in range(4):
            st = abs_style.create_box(f"{name}_Step_{i}", size=(2.2 - i*0.2, 0.45, 0.2), loc=(ox, oy - 0.6 + i*0.4, oz + 0.2 + i*0.2), mat=mats['marble'], col=col)
            st.parent = root
            edge = abs_style.create_box(f"{name}_Nosing_{i}", size=(2.22 - i*0.2, 0.06, 0.05), loc=(ox, oy - 0.82 + i*0.4, oz + 0.3 + i*0.2), mat=mats['gold'], col=col)
            edge.parent = root

    elif asset_id == 32: # SM_Mod_32_Deco_Elevator_Door_Pillbox
        frame = abs_style.create_box(f"{name}_Frame", size=(2.4, 0.4, 3.2), loc=(ox, oy, oz + 1.6), mat=mats['gold'], col=col)
        frame.parent = root
        door_l = abs_style.create_box(f"{name}_DoorL", size=(0.95, 0.1, 2.7), loc=(ox - 0.5, oy - 0.05, oz + 1.35), mat=mats['wood'], col=col)
        door_l.parent = root
        door_r = abs_style.create_box(f"{name}_DoorR", size=(0.95, 0.1, 2.7), loc=(ox + 0.5, oy - 0.05, oz + 1.35), mat=mats['wood'], col=col)
        door_r.parent = root
        dial = abs_style.create_torus(f"{name}_FloorDial", major_r=0.3, minor_r=0.04, rot=(math.radians(90), 0, 0), loc=(ox, oy - 0.22, oz + 2.85), mat=mats['gold'], col=col)
        dial.parent = root

    elif asset_id == 33: # SM_Mod_33_Deco_Console_Table_Marble
        top = abs_style.create_box(f"{name}_Top", size=(2.0, 0.6, 0.08), loc=(ox, oy, oz + 0.85), mat=mats['obsidian'], col=col)
        top.parent = root
        skirt = abs_style.create_box(f"{name}_Skirt", size=(1.9, 0.5, 0.1), loc=(ox, oy, oz + 0.78), mat=mats['gold'], col=col)
        skirt.parent = root
        for lx in [-0.85, 0.85]:
            leg = abs_style.create_cylinder(f"{name}_Leg_{lx}", radius=0.04, depth=0.8, loc=(ox + lx, oy, oz + 0.4), mat=mats['gold'], col=col)
            leg.parent = root

    elif asset_id == 34: # SM_Mod_34_Deco_Decorative_Screen_Paravent
        for px in [-0.9, 0.0, 0.9]:
            panel = abs_style.create_box(f"{name}_Leaf_{px}", size=(0.85, 0.06, 2.4), loc=(ox + px, oy, oz + 1.2), mat=mats['wood'], col=col)
            panel.parent = root
            gold_inlay = abs_style.create_box(f"{name}_GoldLeaf_{px}", size=(0.7, 0.07, 2.0), loc=(ox + px, oy, oz + 1.2), mat=mats['gold'], col=col)
            gold_inlay.parent = root

    elif asset_id == 35: # SM_Mod_35_Deco_Cocktail_Bar_Counter
        counter = abs_style.create_box(f"{name}_Top", size=(3.2, 0.8, 0.1), loc=(ox, oy, oz + 1.1), mat=mats['obsidian'], col=col)
        counter.parent = root
        facade = abs_style.create_box(f"{name}_Facade", size=(3.0, 0.6, 1.0), loc=(ox, oy, oz + 0.55), mat=mats['wood'], col=col)
        facade.parent = root
        footrail = abs_style.create_cylinder(f"{name}_Footrail", radius=0.035, depth=3.0, rot=(0, math.radians(90), 0), loc=(ox, oy - 0.45, oz + 0.2), mat=mats['gold'], col=col)
        footrail.parent = root

    elif asset_id == 36: # SM_Mod_36_Deco_Sculptural_Pedestal
        plinth = abs_style.create_box(f"{name}_Plinth", size=(0.8, 0.8, 1.4), loc=(ox, oy, oz + 0.7), mat=mats['marble'], col=col)
        plinth.parent = root
        cap = abs_style.create_box(f"{name}_Cap", size=(0.9, 0.9, 0.1), loc=(ox, oy, oz + 1.45), mat=mats['gold'], col=col)
        cap.parent = root
        base = abs_style.create_box(f"{name}_Base", size=(0.95, 0.95, 0.12), loc=(ox, oy, oz + 0.06), mat=mats['gold'], col=col)
        base.parent = root

    return root

KIT2_ASSETS = [
    (19, "SM_Mod_19_Deco_Wall_Boiserie_400x350"),
    (20, "SM_Mod_20_Deco_Arched_Portal_400x350"),
    (21, "SM_Mod_21_Deco_Marble_Floor_Pattern_400x400"),
    (22, "SM_Mod_22_Deco_Coffered_Ceiling_400x400"),
    (23, "SM_Mod_23_Deco_Corinthian_Column_350cm"),
    (24, "SM_Mod_24_Deco_Chesterfield_Sofa_240cm"),
    (25, "SM_Mod_25_Deco_Lounge_Armchair"),
    (26, "SM_Mod_26_Deco_Gilded_Balustrade_400cm"),
    (27, "SM_Mod_27_Deco_Tiered_Chandelier"),
    (28, "SM_Mod_28_Deco_Observatory_Porthole_Large"),
    (29, "SM_Mod_29_Deco_Wall_Sconce_Fan"),
    (30, "SM_Mod_30_Deco_Display_Cabinet_Vitrines"),
    (31, "SM_Mod_31_Deco_Grand_Staircase_Step_Section"),
    (32, "SM_Mod_32_Deco_Elevator_Door_Pillbox"),
    (33, "SM_Mod_33_Deco_Console_Table_Marble"),
    (34, "SM_Mod_34_Deco_Decorative_Screen_Paravent"),
    (35, "SM_Mod_35_Deco_Cocktail_Bar_Counter"),
    (36, "SM_Mod_36_Deco_Sculptural_Pedestal"),
]

def generate_kit2_scene(save_blend=True):
    abs_style.reset_comic_scene()
    col = abs_style.create_collection("Kit2_Celestia_ArtDeco")
    mats = init_kit2_materials()
    
    spacing_x = 4.8
    spacing_y = 5.2
    ped_mat = abs_style.get_comic_material("Pedestal_K2", base_color=(0.10, 0.08, 0.07), roughness=0.3, metallic=0.7)
    
    for idx, (aid, aname) in enumerate(KIT2_ASSETS):
        col_idx = idx % 6
        row_idx = idx // 6
        x = (col_idx - 2.5) * spacing_x
        y = (row_idx - 1.0) * spacing_y
        
        ped = abs_style.create_box(f"Pedestal_{aname}", size=(4.2, 4.2, 0.25), loc=(x, y, -0.125), mat=ped_mat, col=col)
        build_asset(aid, aname, (x, y, 0.0), col, mats)
        
    floor_mat = abs_style.get_comic_material("Floor_K2", base_color=(0.02, 0.025, 0.035), roughness=0.25, metallic=0.85)
    abs_style.create_box("FloorK2", size=(38.0, 24.0, 0.1), loc=(0, 0, -0.2), mat=floor_mat, col=col)
    abs_style.setup_studio_lighting(sun_energy=3.8, rim_energy=2.4, fill_energy=1.2)
    abs_style.setup_camera(name="Camera_Kit2", loc=(0, -24, 15), target=(0, 0, 1.2), focal_length=32)
    
    if save_blend:
        blend_path = os.path.join(abs_style.PROJECT_ROOT, "Art", "Blender", "Catalogo_Modulares_Kit2_ArtDeco.blend")
        bpy.ops.wm.save_as_mainfile(filepath=blend_path)
        print(f"[+] Blend saved: {blend_path}")
        
    abs_style.render_and_save("Showcase_Modulares_Kit2_ArtDeco_18.png", res_x=2560, res_y=1440)

if __name__ == "__main__":
    generate_kit2_scene()

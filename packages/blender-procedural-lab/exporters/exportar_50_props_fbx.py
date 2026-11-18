# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Pipeline de Exportación Automatizada de 50 Props Maestros a formato FBX para Unreal Engine 5.8
# Exporta mallas estáticas limpias centradas en origen (Z base = 0) con volúmenes de colisión UCX.

import bpy
import bmesh
import os
import sys
from mathutils import Vector

PROJECT_ROOT = r"F:\Dev\Game"
FBX_PROPS_DIR = os.path.join(PROJECT_ROOT, "Art", "FBX", "Props")
os.makedirs(FBX_PROPS_DIR, exist_ok=True)

LOTES_CONFIG = [
    # Lote 1: Acceso & Esclusas
    {
        "blend": os.path.join(PROJECT_ROOT, "Art", "Blender", "Lote1_Props_Maestros_Oficial.blend"),
        "type": "single",
        "props": [
            (1, "SM_Airlock_Heavy_Hatch"),
            (2, "SM_Ventilation_Grating_Duct"),
            (3, "SM_Hydraulic_Blast_Door"),
            (4, "SM_Crawlway_Escape_Portal"),
            (5, "SM_Cryo_Tube_Maintenance_Hatch"),
        ]
    },
    # Lote 2: Energía & Red Auxiliar
    {
        "blend": os.path.join(PROJECT_ROOT, "Art", "Blender", "Lote2_Props_Maestros_Oficial.blend"),
        "type": "single",
        "props": [
            (6, "SM_Backup_Diesel_Generator"),
            (7, "SM_High_Voltage_Breaker_Box"),
            (8, "SM_Portable_Battery_Rack"),
            (9, "SM_Industrial_Cable_Reel"),
            (10, "SM_Emergency_Capacitor_Bank"),
        ]
    },
    # Lote 3: Fluidos & Residuos
    {
        "blend": os.path.join(PROJECT_ROOT, "Art", "Blender", "Lote3_Props_Maestros_Oficial.blend"),
        "type": "single",
        "props": [
            (11, "SM_Decontamination_Shower_Unit"),
            (12, "SM_Hazardous_Waste_Incinerator"),
            (13, "SM_Pressurized_Coolant_Manifold"),
            (14, "SM_Biohazard_Storage_Vault"),
            (15, "SM_Radiation_Lead_Shield_Screen"),
        ]
    },
    # Lote 4: Medicina & Soporte Vital
    {
        "blend": os.path.join(PROJECT_ROOT, "Art", "Blender", "Lote4_Props_Maestros_Oficial.blend"),
        "type": "single",
        "props": [
            (16, "SM_Trauma_Kit_Wall_Cabinet"),
            (17, "SM_Stasis_Sleeper_Pod"),
            (18, "SM_Oxygen_Scrubber_Cartridge_Rack"),
            (19, "SM_Burn_Triage_Gurney"),
            (20, "SM_Casualty_Identification_Kiosk"),
        ]
    },
    # Lote 5: Cajas Negras & Datos
    {
        "blend": os.path.join(PROJECT_ROOT, "Art", "Blender", "Lote5_Props_Maestros_Oficial.blend"),
        "type": "single",
        "props": [
            (21, "SM_Flight_Data_Recorder_BlackBox"),
            (22, "SM_Server_Rack_Reinforced"),
            (23, "SM_Captains_Secure_Vault"),
            (24, "SM_Cartographic_Navigation_Table"),
            (25, "SM_SOS_Transponder_Mast"),
        ]
    },
    # Lote 6: Camarotes & Hábitat
    {
        "blend": os.path.join(PROJECT_ROOT, "Art", "Blender", "Lote6_Props_Maestros_Oficial.blend"),
        "type": "single",
        "props": [
            (26, "SM_Crew_Bunk_Double_Fold"),
            (27, "SM_Nutrient_Paste_Dispenser"),
            (28, "SM_Hydroponic_Sprout_Chamber"),
            (29, "SM_Sanitation_Locker_Unit"),
            (30, "SM_Crew_Personal_Locker"),
        ]
    },
    # Lote 7: Navegación & Telecomunicaciones
    {
        "blend": os.path.join(PROJECT_ROOT, "Art", "Blender", "Lote7_Props_Maestros.blend"),
        "type": "hierarchy",
        "props": [
            (31, "Root_P31", "SM_Holonav_Tactical_Globe"),
            (32, "Root_P32", "SM_Comms_Array_Console"),
            (33, "Root_P33", "SM_Mainframe_Tape_Drive"),
            (34, "Root_P34", "SM_Radar_Sweeper_Terminal"),
            (35, "Root_P35", "SM_Auxiliary_Pilot_Chair"),
        ]
    },
    # Lote 8: Almacén, Logística & Carga Pesada
    {
        "blend": os.path.join(PROJECT_ROOT, "Art", "Blender", "Lote8_Props_Maestros.blend"),
        "type": "hierarchy",
        "props": [
            (36, "Root_P36", "SM_Heavy_Pallet_Jack"),
            (37, "Root_P37", "SM_Cargo_Container_Maglock"),
            (38, "Root_P38", "SM_Overhead_Crane_Trolley"),
            (39, "Root_P39", "SM_Barrel_Storage_Rack"),
            (40, "Root_P40", "SM_Cargo_Scale_Platform"),
        ]
    },
    # Lote 9: Seguridad & Blindaje
    {
        "blend": os.path.join(PROJECT_ROOT, "Art", "Blender", "Lote9_Props_Maestros.blend"),
        "type": "hierarchy",
        "props": [
            (41, "Root_P41", "SM_Security_Turnstile_Barrier"),
            (42, "Root_P42", "SM_Wall_Mounted_Keycard_Box"),
            (43, "Root_P43", "SM_Surveillance_Dome_Turret"),
            (44, "Root_P44", "SM_Weapon_Locker_Reinforced"),
            (45, "Root_P45", "SM_Emergency_Breach_Axe_Box"),
        ]
    },
    # Lote 10: Taller & Mecanizado
    {
        "blend": os.path.join(PROJECT_ROOT, "Art", "Blender", "Lote10_Props_Maestros.blend"),
        "type": "hierarchy",
        "props": [
            (46, "Root_P46", "SM_Heavy_Duty_Workbench"),
            (47, "Root_P47", "SM_Arc_Welding_Rig_Cart"),
            (48, "Root_P48", "SM_Pedestal_Drill_Press"),
            (49, "Root_P49", "SM_Parts_Washer_Station"),
            (50, "Root_P50", "SM_Heavy_Hydraulic_Floor_Press"),
        ]
    },
]

def export_single_mesh_prop(prop_id, prop_name):
    obj = bpy.data.objects.get(prop_name)
    if not obj:
        print(f"[ERROR] Prop {prop_id}: Objeto '{prop_name}' no encontrado en escena.")
        return False
        
    bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    min_x = min(c.x for c in bbox_corners)
    max_x = max(c.x for c in bbox_corners)
    min_y = min(c.y for c in bbox_corners)
    max_y = max(c.y for c in bbox_corners)
    min_z = min(c.z for c in bbox_corners)
    max_z = max(c.z for c in bbox_corners)
    
    center_x = (min_x + max_x) / 2.0
    center_y = (min_y + max_y) / 2.0
    base_z = min_z
    
    width = max(max_x - min_x, 0.05)
    depth = max(max_y - min_y, 0.05)
    height = max(max_z - min_z, 0.05)
    
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.duplicate()
    dup_obj = bpy.context.active_object
    dup_obj.name = f"EXPORT_{prop_name}"
    
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    for v in dup_obj.data.vertices:
        v.co.x -= center_x
        v.co.y -= center_y
        v.co.z -= base_z
    dup_obj.data.update()
    
    # UCX Box
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, height / 2.0))
    ucx_obj = bpy.context.active_object
    ucx_obj.name = f"UCX_{prop_name}_01"
    ucx_obj.scale = (width, depth, height)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    dup_obj.name = prop_name
    
    bpy.ops.object.select_all(action='DESELECT')
    dup_obj.select_set(True)
    ucx_obj.select_set(True)
    bpy.context.view_layer.objects.active = dup_obj
    
    fbx_path = os.path.join(FBX_PROPS_DIR, f"{prop_name}.fbx")
    bpy.ops.export_scene.fbx(
        filepath=fbx_path,
        use_selection=True,
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_ALL',
        axis_forward='-Z',
        axis_up='Y',
        mesh_smooth_type='FACE'
    )
    
    # Limpieza temporal
    bpy.data.objects.remove(ucx_obj, do_unlink=True)
    bpy.data.objects.remove(dup_obj, do_unlink=True)
    
    print(f"[OK] Prop {prop_id:02d} ({prop_name}) exportado -> {fbx_path}")
    return True

def export_hierarchy_prop(prop_id, root_name, prop_name):
    root = bpy.data.objects.get(root_name)
    if not root:
        print(f"[ERROR] Prop {prop_id}: Root '{root_name}' no encontrado en escena.")
        return False
        
    mesh_children = [c for c in root.children if c.type == 'MESH']
    if not mesh_children:
        print(f"[ERROR] Prop {prop_id}: Sin hijos mesh para '{root_name}'.")
        return False
        
    all_corners = []
    for c in mesh_children:
        corners = [c.matrix_world @ Vector(corner) for corner in c.bound_box]
        all_corners.extend(corners)
        
    min_x = min(c.x for c in all_corners)
    max_x = max(c.x for c in all_corners)
    min_y = min(c.y for c in all_corners)
    max_y = max(c.y for c in all_corners)
    min_z = min(c.z for c in all_corners)
    max_z = max(c.z for c in all_corners)
    
    center_x = (min_x + max_x) / 2.0
    center_y = (min_y + max_y) / 2.0
    base_z = min_z
    
    width = max(max_x - min_x, 0.05)
    depth = max(max_y - min_y, 0.05)
    height = max(max_z - min_z, 0.05)
    
    bpy.ops.object.select_all(action='DESELECT')
    for c in mesh_children:
        c.select_set(True)
    bpy.context.view_layer.objects.active = mesh_children[0]
    bpy.ops.object.duplicate()
    
    dup_meshes = [o for o in bpy.context.selected_objects if o.type == 'MESH']
    for dm in dup_meshes:
        dm.parent = None
        
    bpy.context.view_layer.objects.active = dup_meshes[0]
    bpy.ops.object.join()
    
    joined_obj = bpy.context.active_object
    joined_obj.name = prop_name
    
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    for v in joined_obj.data.vertices:
        v.co.x -= center_x
        v.co.y -= center_y
        v.co.z -= base_z
    joined_obj.data.update()
    
    # UCX Box
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, height / 2.0))
    ucx_obj = bpy.context.active_object
    ucx_obj.name = f"UCX_{prop_name}_01"
    ucx_obj.scale = (width, depth, height)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    bpy.ops.object.select_all(action='DESELECT')
    joined_obj.select_set(True)
    ucx_obj.select_set(True)
    bpy.context.view_layer.objects.active = joined_obj
    
    fbx_path = os.path.join(FBX_PROPS_DIR, f"{prop_name}.fbx")
    bpy.ops.export_scene.fbx(
        filepath=fbx_path,
        use_selection=True,
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_ALL',
        axis_forward='-Z',
        axis_up='Y',
        mesh_smooth_type='FACE'
    )
    
    bpy.data.objects.remove(ucx_obj, do_unlink=True)
    bpy.data.objects.remove(joined_obj, do_unlink=True)
    
    print(f"[OK] Prop {prop_id:02d} ({prop_name}) exportado -> {fbx_path}")
    return True

def main():
    print("=" * 80)
    print("INICIANDO PIPELINE DE EXPORTACIÓN FBX - 50 PROPS MAESTROS")
    print("=" * 80)
    
    total_exported = 0
    for lote_idx, lote in enumerate(LOTES_CONFIG, 1):
        blend_path = lote["blend"]
        if not os.path.exists(blend_path):
            print(f"[SKIP] Lote {lote_idx}: No existe archivo {blend_path}")
            continue
            
        print(f"\n--- Procesando Lote {lote_idx} ({os.path.basename(blend_path)}) ---")
        bpy.ops.wm.open_mainfile(filepath=blend_path)
        
        lote_type = lote["type"]
        if lote_type == "single":
            for prop_id, prop_name in lote["props"]:
                if export_single_mesh_prop(prop_id, prop_name):
                    total_exported += 1
        elif lote_type == "hierarchy":
            for prop_id, root_name, prop_name in lote["props"]:
                if export_hierarchy_prop(prop_id, root_name, prop_name):
                    total_exported += 1
                    
    print("\n" + "=" * 80)
    print(f"EXPORTACIÓN COMPLETADA: {total_exported}/50 Props exportados a {FBX_PROPS_DIR}")
    print("=" * 80)

if __name__ == "__main__":
    main()

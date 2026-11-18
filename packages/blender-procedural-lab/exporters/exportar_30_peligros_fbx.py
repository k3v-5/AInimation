# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Pipeline de Exportación Automatizada de los 30 Peligros Ambientales a FBX para Unreal Engine 5.8
# Centrado en origen (Z base = 0), unificación de submallas y generación de volúmenes de colisión UCX.

import bpy
import bmesh
import os
import sys
from mathutils import Vector

PROJECT_ROOT = r"F:\Dev\Game"
FBX_HAZARDS_DIR = os.path.join(PROJECT_ROOT, "Art", "FBX", "Hazards")
os.makedirs(FBX_HAZARDS_DIR, exist_ok=True)

HAZARDS_CONFIG = [
    # Lote 1: Térmicos e Ígneos (H01 al H06)
    {
        "blend": os.path.join(PROJECT_ROOT, "Art", "Blender", "Peligros_Lote1_Termicos.blend"),
        "hazards": [
            (1, "Root_H01", "SM_H01_Fire_Bulkhead_Rupture"),
            (2, "Root_H02", "SM_H02_Electrical_Arc_Fire_Box"),
            (3, "Root_H03", "SM_H03_Magnesium_Chemical_Fire"),
            (4, "Root_H04", "SM_H04_Plasma_Nozzle_Breach"),
            (5, "Root_H05", "SM_H05_Vent_Duct_Inferno"),
            (6, "Root_H06", "SM_H06_Habitation_Flashover"),
        ]
    },
    # Lote 2: Presión, Fugas & Fluidos Críticos (H07 al H12)
    {
        "blend": os.path.join(PROJECT_ROOT, "Art", "Blender", "Peligros_Lote2_Fluidos.blend"),
        "hazards": [
            (7, "Root_H07", "SM_H07_Superheated_Steam_Jet"),
            (8, "Root_H08", "SM_H08_Hydraulic_Oil_Slick"),
            (9, "Root_H09", "SM_H09_Hydrofluoric_Acid_Puddle"),
            (10, "Root_H10", "SM_H10_Liquid_Nitrogen_Cryo_Leak"),
            (11, "Root_H11", "SM_H11_Hull_Decompression_Vortex"),
            (12, "Root_H12", "SM_H12_Toxic_Coolant_Flooding"),
        ]
    },
    # Lote 3: Eléctricos, Arcos & Energía (H13 al H18)
    {
        "blend": os.path.join(PROJECT_ROOT, "Art", "Blender", "Peligros_Lote3_Electricos.blend"),
        "hazards": [
            (13, "Root_H13", "SM_H13_Live_Arcing_Whip_Cable"),
            (14, "Root_H14", "SM_H14_Aux_Generator_Meltdown"),
            (15, "Root_H15", "SM_H15_Electrified_Floor_Grating"),
            (16, "Root_H16", "SM_H16_Battery_Rack_Thermal_Runaway"),
            (17, "Root_H17", "SM_H17_Rogue_Scraping_Electromagnet"),
            (18, "Root_H18", "SM_H18_Blown_High_Amp_Fuse_Bank"),
        ]
    },
    # Lote 4: Colapsos Estructurales & Escombros (H19 al H24)
    {
        "blend": os.path.join(PROJECT_ROOT, "Art", "Blender", "Peligros_Lote4_Estructurales.blend"),
        "hazards": [
            (19, "Root_H19", "SM_H19_Fractured_Structural_IBeam"),
            (20, "Root_H20", "SM_H20_Collapsed_Ceiling_Baffle"),
            (21, "Root_H21", "SM_H21_Overpressured_Bulging_Bulkhead"),
            (22, "Root_H22", "SM_H22_Broken_Catwalk_Section"),
            (23, "Root_H23", "SM_H23_Jammed_Blast_Gate_Angle"),
            (24, "Root_H24", "SM_H24_Twisted_Cage_Ladder_Collapse"),
        ]
    },
    # Lote 5: Biológicos, Tóxicos & Radiológicos (H25 al H30)
    {
        "blend": os.path.join(PROJECT_ROOT, "Art", "Blender", "Peligros_Lote5_Biologicos.blend"),
        "hazards": [
            (25, "Root_H25", "SM_H25_Shattered_BSL4_Incubator"),
            (26, "Root_H26", "SM_H26_Exposed_Fuel_Rod_Basket"),
            (27, "Root_H27", "SM_H27_Slime_Clogged_Valve"),
            (28, "Root_H28", "SM_H28_Overflowing_Toxic_Sump"),
            (29, "Root_H29", "SM_H29_Shattered_Cryo_Dewar"),
            (30, "Root_H30", "SM_H30_Fungal_Colonized_Scrubber"),
        ]
    },
]

def get_all_mesh_descendants(obj):
    meshes = []
    for child in obj.children:
        if child.type == 'MESH':
            meshes.append(child)
        meshes.extend(get_all_mesh_descendants(child))
    return meshes

def export_hazard_to_fbx(hazard_id, root_name, mesh_name):
    root = bpy.data.objects.get(root_name)
    if not root:
        print(f"[ERROR] H{hazard_id:02d}: Root '{root_name}' no encontrado en escena.")
        return False
        
    mesh_children = get_all_mesh_descendants(root)
    if not mesh_children:
        print(f"[ERROR] H{hazard_id:02d}: Sin submallas mesh bajo '{root_name}'.")
        return False
        
    # Calcular bounding box en espacio de mundo
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
    
    width = max(max_x - min_x, 0.10)
    depth = max(max_y - min_y, 0.10)
    height = max(max_z - min_z, 0.10)
    
    # Duplicar y unir submallas
    bpy.ops.object.select_all(action='DESELECT')
    for c in mesh_children:
        c.select_set(True)
    bpy.context.view_layer.objects.active = mesh_children[0]
    bpy.ops.object.duplicate()
    
    dup_meshes = [o for o in bpy.context.selected_objects if o.type == 'MESH']
    for dm in dup_meshes:
        mw = dm.matrix_world.copy()
        dm.parent = None
        dm.matrix_world = mw
        
    bpy.context.view_layer.objects.active = dup_meshes[0]
    bpy.ops.object.join()
    
    joined_obj = bpy.context.active_object
    joined_obj.name = mesh_name
    
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # Recalcular bounding box exacto desde los vértices ya aplicados al espacio mundo
    verts = joined_obj.data.vertices
    min_x = min(v.co.x for v in verts)
    max_x = max(v.co.x for v in verts)
    min_y = min(v.co.y for v in verts)
    max_y = max(v.co.y for v in verts)
    min_z = min(v.co.z for v in verts)
    max_z = max(v.co.z for v in verts)

    center_x = (min_x + max_x) / 2.0
    center_y = (min_y + max_y) / 2.0
    base_z = min_z

    width = max(max_x - min_x, 0.10)
    depth = max(max_y - min_y, 0.10)
    height = max(max_z - min_z, 0.10)
    
    # Trasladar vértices al origen de contacto inferior (0, 0, 0)
    for v in verts:
        v.co.x -= center_x
        v.co.y -= center_y
        v.co.z -= base_z
    joined_obj.data.update()
    
    # Generar volumen de colisión convexa UCX_
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, height / 2.0))
    ucx_obj = bpy.context.active_object
    ucx_obj.name = f"UCX_{mesh_name}_01"
    ucx_obj.scale = (width, depth, height)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    # Seleccionar malla y colisión para exportar FBX
    bpy.ops.object.select_all(action='DESELECT')
    joined_obj.select_set(True)
    ucx_obj.select_set(True)
    bpy.context.view_layer.objects.active = joined_obj
    
    fbx_path = os.path.join(FBX_HAZARDS_DIR, f"{mesh_name}.fbx")
    bpy.ops.export_scene.fbx(
        filepath=fbx_path,
        use_selection=True,
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_ALL',
        axis_forward='-Z',
        axis_up='Y',
        mesh_smooth_type='FACE'
    )
    
    # Limpieza de temporales en escena
    bpy.data.objects.remove(ucx_obj, do_unlink=True)
    bpy.data.objects.remove(joined_obj, do_unlink=True)
    
    print(f" [OK] Peligro H{hazard_id:02d} ({mesh_name}) -> {fbx_path} (Dims: {width:.2f}x{depth:.2f}x{height:.2f} m)")
    return True

def main():
    print("=" * 80)
    print("PIPELINE DE EXPORTACIÓN FBX: 30 PELIGROS AMBIENTALES (H01 AL H30)")
    print("=" * 80)
    
    total_exported = 0
    total_expected = 30
    
    for lote_idx, lote_data in enumerate(HAZARDS_CONFIG, start=1):
        blend_file = lote_data["blend"]
        print(f"\n---> PROCESANDO LOTE {lote_idx} [{os.path.basename(blend_file)}]...")
        
        if not os.path.exists(blend_file):
            print(f"[FATAL] No existe archivo .blend: {blend_file}")
            continue
            
        bpy.ops.wm.open_mainfile(filepath=blend_file)
        
        for h_id, root_name, mesh_name in lote_data["hazards"]:
            if export_hazard_to_fbx(h_id, root_name, mesh_name):
                total_exported += 1
                
    print("\n" + "=" * 80)
    print(f"EXPORTACIÓN FBX COMPLETADA: {total_exported}/{total_expected} PELIGROS GENERADOS")
    print("=" * 80)

if __name__ == "__main__":
    main()

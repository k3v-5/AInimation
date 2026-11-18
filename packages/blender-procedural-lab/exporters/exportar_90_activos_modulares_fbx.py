# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Pipeline de Exportación Automatizada del Catálogo Modular de 90 Activos a FBX para Unreal Engine 5.8
# Centrado en origen (Z base = 0), unificación de mallas, preservación de materiales y volúmenes de colisión UCX.

import bpy
import bmesh
import os
import sys
from mathutils import Vector

PROJECT_ROOT = r"F:\Dev\Game"
BLEND_FILE = os.path.join(PROJECT_ROOT, "Art", "Blender", "Catalogo_Activos_Modulares_90_Oficial.blend")
FBX_MODULAR_DIR = os.path.join(PROJECT_ROOT, "Art", "FBX", "Environment", "Modular")
os.makedirs(FBX_MODULAR_DIR, exist_ok=True)

def get_all_descendant_meshes(parent_obj):
    """Obtiene recursivamente todas las mallas hijas directas e indirectas."""
    meshes = []
    for child in parent_obj.children:
        if child.type == 'MESH':
            meshes.append(child)
        meshes.extend(get_all_descendant_meshes(child))
    return meshes

def export_modular_asset_to_fbx(root_obj):
    sm_name = root_obj.name.replace("Root_", "")
    meshes = get_all_descendant_meshes(root_obj)
    if not meshes:
        print(f"[ERROR] {sm_name}: No se encontraron mallas hijas para '{root_obj.name}'.")
        return False

    # Calcular bounding box total en espacio de mundo
    all_corners = []
    for m in meshes:
        corners = [m.matrix_world @ Vector(c) for c in m.bound_box]
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

    # Duplicar todas las mallas para unión limpia sin tocar originales
    bpy.ops.object.select_all(action='DESELECT')
    for m in meshes:
        m.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.object.duplicate()

    dup_meshes = [o for o in bpy.context.selected_objects if o.type == 'MESH']
    for dm in dup_meshes:
        dm.parent = None

    bpy.context.view_layer.objects.active = dup_meshes[0]
    bpy.ops.object.join()

    joined_obj = bpy.context.active_object
    joined_obj.name = sm_name

    # Hornear transformaciones a nivel de mundo
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # Desplazar vértices al origen de contacto inferior (0, 0, 0)
    for v in joined_obj.data.vertices:
        v.co.x -= center_x
        v.co.y -= center_y
        v.co.z -= base_z
    joined_obj.data.update()

    # Generar volumen de colisión convexa UCX_
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, height / 2.0))
    ucx_obj = bpy.context.active_object
    ucx_obj.name = f"UCX_{sm_name}_01"
    ucx_obj.scale = (width * 0.98, depth * 0.98, height)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    # Seleccionar malla principal y volumen UCX para exportación
    bpy.ops.object.select_all(action='DESELECT')
    joined_obj.select_set(True)
    ucx_obj.select_set(True)
    bpy.context.view_layer.objects.active = joined_obj

    fbx_path = os.path.join(FBX_MODULAR_DIR, f"{sm_name}.fbx")
    bpy.ops.export_scene.fbx(
        filepath=fbx_path,
        use_selection=True,
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_ALL',
        axis_forward='-Z',
        axis_up='Y',
        mesh_smooth_type='FACE'
    )

    # Limpieza de duplicados y auxiliares
    bpy.data.objects.remove(ucx_obj, do_unlink=True)
    bpy.data.objects.remove(joined_obj, do_unlink=True)

    print(f" [OK] {sm_name} -> {fbx_path} [Dims: {width:.2f}x{depth:.2f}x{height:.2f} m]")
    return True

def main():
    print("=" * 80)
    print("PIPELINE DE EXPORTACIÓN FBX: CATÁLOGO MODULAR DE 90 ACTIVOS OFICIALES")
    print("=" * 80)

    if not os.path.exists(BLEND_FILE):
        print(f"[FATAL] No existe archivo .blend: {BLEND_FILE}")
        sys.exit(1)

    print(f"Abriendo archivo maestro: {BLEND_FILE}")
    bpy.ops.wm.open_mainfile(filepath=BLEND_FILE)

    roots = [o for o in bpy.data.objects if o.name.startswith("Root_SM_Mod_")]
    def get_root_id(r):
        parts = r.name.split("_")
        for p in parts:
            if p.isdigit():
                return int(p)
        return 999
    roots.sort(key=get_root_id)

    total_expected = len(roots)
    print(f"Detectados {total_expected} activos modulares en escena.")

    total_exported = 0
    for idx, r in enumerate(roots, 1):
        print(f"[{idx:02d}/{total_expected:02d}] Procesando {r.name}...")
        if export_modular_asset_to_fbx(r):
            total_exported += 1

    print("\n" + "=" * 80)
    print(f"EXPORTACIÓN FBX COMPLETADA: {total_exported}/{total_expected} ACTIVOS MODULARES GENERADOS EN {FBX_MODULAR_DIR}")
    print("=" * 80)

if __name__ == "__main__":
    main()

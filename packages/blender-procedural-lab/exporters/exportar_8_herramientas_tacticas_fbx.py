# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Pipeline de Exportación Automatizada de la Suite de 8 Herramientas Tácticas Avanzadas a FBX para Unreal Engine 5.8
# Centrado en origen (Z base = 0), unificación de mallas, preservación de materiales y volúmenes de colisión UCX.

import bpy
import bmesh
import os
import sys
from mathutils import Vector

PROJECT_ROOT = r"F:\Dev\Game"
BLEND_FILE = os.path.join(PROJECT_ROOT, "Art", "Blender", "Herramientas_Tacticas_8_Oficial.blend")
FBX_TACTICAL_DIR = os.path.join(PROJECT_ROOT, "Art", "FBX", "Equipment", "Tactical")
os.makedirs(FBX_TACTICAL_DIR, exist_ok=True)

TACTICAL_TOOLS_CONFIG = [
    (1, "T01_Foam_Launcher_Heavy", "Lanzador de Espuma Pesada Compacto"),
    (2, "T02_Net_Gun_Quad_Launcher", "Lanzador de Red Electrostatica Cuadruple"),
    (3, "T03_Hydraulic_Jack_15T", "Gato Hidraulico de Rescate 15T"),
    (4, "T04_Deployable_Repeater_Beacon", "Baliza Repetidora Desplegable"),
    (5, "T05_Acoustic_Motion_Scanner", "Escaner Acustico de Supervivientes PDA"),
    (6, "T06_Retractable_Titanium_Grapnel", "Gancho Neumatico de Anclaje y Rescate"),
    (7, "T07_Heavy_Hydraulic_Shears", "Cizalla Hidraulica Combinada de Rescate"),
    (8, "T08_Folding_Thermal_Shield", "Escudo Termico Plegable Balistico")
]

def get_all_descendant_meshes(parent_obj):
    """Obtiene recursivamente todas las mallas hijas directas e indirectas."""
    meshes = []
    for child in parent_obj.children:
        if child.type == 'MESH':
            meshes.append(child)
        meshes.extend(get_all_descendant_meshes(child))
    return meshes

def export_tool_to_fbx(tool_id, tool_name, label):
    root_name = f"Root_{tool_name}"
    root = bpy.data.objects.get(root_name)
    if not root:
        print(f"[ERROR] T{tool_id:02d}: Root '{root_name}' no encontrado en escena.")
        return False

    meshes = get_all_descendant_meshes(root)
    if not meshes:
        print(f"[ERROR] T{tool_id:02d}: No se encontraron mallas hijas para '{root_name}'.")
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

    width = max(max_x - min_x, 0.05)
    depth = max(max_y - min_y, 0.05)
    height = max(max_z - min_z, 0.05)

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
    sm_name = f"SM_{tool_name}"
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
    ucx_obj.scale = (width * 0.96, depth * 0.96, height)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    # Seleccionar malla principal y volumen UCX para exportación
    bpy.ops.object.select_all(action='DESELECT')
    joined_obj.select_set(True)
    ucx_obj.select_set(True)
    bpy.context.view_layer.objects.active = joined_obj

    fbx_path = os.path.join(FBX_TACTICAL_DIR, f"{sm_name}.fbx")
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

    print(f" [OK] T{tool_id:02d} ({sm_name} | {label}) -> {fbx_path} [Dims: {width:.2f}x{depth:.2f}x{height:.2f} m]")
    return True

def main():
    print("=" * 80)
    print("PIPELINE DE EXPORTACIÓN FBX: 8 HERRAMIENTAS TÁCTICAS AVANZADAS")
    print("=" * 80)

    if not os.path.exists(BLEND_FILE):
        print(f"[FATAL] No existe archivo .blend: {BLEND_FILE}")
        sys.exit(1)

    print(f"Abriendo archivo maestro: {BLEND_FILE}")
    bpy.ops.wm.open_mainfile(filepath=BLEND_FILE)

    total_exported = 0
    total_expected = len(TACTICAL_TOOLS_CONFIG)

    for t_id, t_name, label in TACTICAL_TOOLS_CONFIG:
        if export_tool_to_fbx(t_id, t_name, label):
            total_exported += 1

    print("\n" + "=" * 80)
    print(f"EXPORTACIÓN FBX COMPLETADA: {total_exported}/{total_expected} HERRAMIENTAS GENERADAS EN {FBX_TACTICAL_DIR}")
    print("=" * 80)

if __name__ == "__main__":
    main()

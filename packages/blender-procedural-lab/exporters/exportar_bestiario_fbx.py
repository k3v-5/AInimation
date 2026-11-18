# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Pipeline de Exportación Automatizada del Bestiario (10 Entidades Biomecánicas) a FBX para Unreal Engine 5.8
# Centrado en origen (Z base = 0), preservación de materiales y volúmenes de colisión UCX.

import bpy
import bmesh
import os
import sys
from mathutils import Vector

PROJECT_ROOT = r"F:\Dev\Game"
BLEND_FILE = os.path.join(PROJECT_ROOT, "Art", "Blender", "Bestiario_10_Entidades_Oficial.blend")
FBX_BESTIARY_DIR = os.path.join(PROJECT_ROOT, "Art", "FBX", "Bestiary")
os.makedirs(FBX_BESTIARY_DIR, exist_ok=True)

BESTIARY_ENTITIES = [
    (1, "SM_Bestiary_01_Werewolf", "Licantropo Biomecanico Alfa (Cyber-Lycan)"),
    (2, "SM_Bestiary_02_Drone", "Droide Auditor Volador de Astra Corp"),
    (3, "SM_Bestiary_03_Scrapper", "Duende Chatarrero Ladron (Hoarder Gremlin)"),
    (4, "SM_Bestiary_04_Spider", "Acechador de Conductos Aranido (Vent Stalker)"),
    (5, "SM_Bestiary_05_Golem", "GolemAbrasador Igneo de Fundicion (Cinder Stalker)"),
    (6, "SM_Bestiary_06_Brute", "Demolidor Enforcer Blindado (Enforcer Brute)"),
    (7, "SM_Bestiary_07_Leech", "Sanguijuela Energetica Parasita (Plasma Leech)"),
    (8, "SM_Bestiary_08_Hound", "Sabueso de Patrulla Cuadrupedo (Cyber Hound)"),
    (9, "SM_Bestiary_09_Keeper", "Guardian de Estacion Centinela (Station Keeper)"),
    (10, "SM_Bestiary_10_Creeper", "Merodeador Silueta Espectral (Thermal Echo Creeper)"),
]

def export_entity_to_fbx(entity_id, mesh_name, label):
    obj = bpy.data.objects.get(mesh_name)
    if not obj:
        print(f"[ERROR] E{entity_id:02d}: Objeto '{mesh_name}' no encontrado en escena.")
        return False

    # Calcular bounding box en espacio de mundo
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    min_x = min(c.x for c in corners)
    max_x = max(c.x for c in corners)
    min_y = min(c.y for c in corners)
    max_y = max(c.y for c in corners)
    min_z = min(c.z for c in corners)
    max_z = max(c.z for c in corners)

    center_x = (min_x + max_x) / 2.0
    center_y = (min_y + max_y) / 2.0
    base_z = min_z

    width = max(max_x - min_x, 0.10)
    depth = max(max_y - min_y, 0.10)
    height = max(max_z - min_z, 0.10)

    # Duplicar objeto para aplicar centrado y exportación limpia
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.duplicate()

    dup_obj = bpy.context.active_object
    dup_obj.name = f"{mesh_name}_Export"
    dup_obj.parent = None

    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # Trasladar vértices al origen de contacto inferior (0, 0, 0)
    for v in dup_obj.data.vertices:
        v.co.x -= center_x
        v.co.y -= center_y
        v.co.z -= base_z
    dup_obj.data.update()

    # Generar volumen de colisión convexa UCX_
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, height / 2.0))
    ucx_obj = bpy.context.active_object
    ucx_obj.name = f"UCX_{mesh_name}_01"
    ucx_obj.scale = (width * 0.95, depth * 0.95, height)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    # Seleccionar malla y colisión para exportar FBX
    bpy.ops.object.select_all(action='DESELECT')
    dup_obj.select_set(True)
    ucx_obj.select_set(True)
    bpy.context.view_layer.objects.active = dup_obj

    # Asegurar nombre final en exportación
    orig_dup_name = dup_obj.name
    dup_obj.name = mesh_name

    fbx_path = os.path.join(FBX_BESTIARY_DIR, f"{mesh_name}.fbx")
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
    bpy.data.objects.remove(dup_obj, do_unlink=True)

    print(f" [OK] E{entity_id:02d} ({mesh_name} | {label}) -> {fbx_path} [Dims: {width:.2f}x{depth:.2f}x{height:.2f} m]")
    return True

def main():
    print("=" * 80)
    print("PIPELINE DE EXPORTACIÓN FBX: BESTIARIO 10 ENTIDADES HOSTILES")
    print("=" * 80)

    if not os.path.exists(BLEND_FILE):
        print(f"[FATAL] No existe archivo .blend: {BLEND_FILE}")
        sys.exit(1)

    print(f"Abriendo archivo maestro: {BLEND_FILE}")
    bpy.ops.wm.open_mainfile(filepath=BLEND_FILE)

    total_exported = 0
    total_expected = len(BESTIARY_ENTITIES)

    for e_id, mesh_name, label in BESTIARY_ENTITIES:
        if export_entity_to_fbx(e_id, mesh_name, label):
            total_exported += 1

    print("\n" + "=" * 80)
    print(f"EXPORTACIÓN FBX COMPLETADA: {total_exported}/{total_expected} ENTIDADES GENERADAS EN {FBX_BESTIARY_DIR}")
    print("=" * 80)

if __name__ == "__main__":
    main()

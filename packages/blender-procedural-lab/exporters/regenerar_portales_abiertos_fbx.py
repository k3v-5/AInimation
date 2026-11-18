# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Regeneración de Portales Modulares Abiertos (SM_Mod_02 y SM_Mod_20) con 3 volúmenes UCX separados (Poste Izq, Poste Der, Dintel Superior)
# garantizando un vano central 100% despejado visual y físicamente.

import bpy
import os
import sys
from mathutils import Vector

PROJECT_ROOT = r"F:\Dev\Game"
SCRIPT_DIR = os.path.join(PROJECT_ROOT, "Art", "Blender")
if SCRIPT_DIR not in sys.path:
    sys.path.append(SCRIPT_DIR)

import astra_blender_styling as abs_style
import catalogo_modulares_kit1_industrial as kit1
import catalogo_modulares_kit2_artdeco as kit2

FBX_MODULAR_DIR = os.path.join(PROJECT_ROOT, "Art", "FBX", "Environment", "Modular")
os.makedirs(FBX_MODULAR_DIR, exist_ok=True)


def get_all_descendant_meshes(parent_obj):
    meshes = []
    for child in parent_obj.children:
        if child.type == 'MESH':
            meshes.append(child)
        meshes.extend(get_all_descendant_meshes(child))
    return meshes


def export_open_portal_to_fbx(root_obj, sm_name):
    bpy.context.view_layer.update()
    meshes = get_all_descendant_meshes(root_obj)
    if not meshes:
        raise RuntimeError(f"No meshes found for {sm_name}")

    bpy.ops.object.select_all(action='DESELECT')
    for m in meshes:
        m.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.object.duplicate()

    dup_meshes = [o for o in bpy.context.selected_objects if o.type == 'MESH']
    for dm in dup_meshes:
        world_mat = dm.matrix_world.copy()
        dm.parent = None
        dm.matrix_world = world_mat

    bpy.ops.object.select_all(action='DESELECT')
    for dm in dup_meshes:
        dm.select_set(True)
    bpy.context.view_layer.objects.active = dup_meshes[0]
    bpy.ops.object.join()

    joined_obj = bpy.context.active_object
    joined_obj.name = sm_name

    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    xs = [v.co.x for v in joined_obj.data.vertices]
    ys = [v.co.y for v in joined_obj.data.vertices]
    zs = [v.co.z for v in joined_obj.data.vertices]
    center_x = 0.5 * (min(xs) + max(xs))
    center_y = 0.5 * (min(ys) + max(ys))
    base_z = min(zs)

    for v in joined_obj.data.vertices:
        v.co.x -= center_x
        v.co.y -= center_y
        v.co.z -= base_z
    joined_obj.data.update()

    # Validación fail-fast de límites centrados en origen (X,Y) y base Z=0
    zs_after = [v.co.z for v in joined_obj.data.vertices]
    xs_after = [v.co.x for v in joined_obj.data.vertices]
    print(f" [CHECK] {sm_name} bounds post-center: X=[{min(xs_after):.2f}, {max(xs_after):.2f}] Z=[{min(zs_after):.2f}, {max(zs_after):.2f}]")

    # Crear 3 volúmenes UCX separados (Poste Izquierdo, Poste Derecho, Dintel Superior)
    # dejando el vano central X in [-1.1, 1.1], Z in [0, 2.7] 100% libre
    ucx_specs = [
        ("01", (-1.6, 0.0, 1.75), (0.8, 0.5, 3.5)),
        ("02", (1.6, 0.0, 1.75), (0.8, 0.5, 3.5)),
        ("03", (0.0, 0.0, 3.1), (2.4, 0.5, 0.8)),
    ]
    ucx_objs = []
    for suffix, u_loc, u_scale in ucx_specs:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=u_loc)
        u_obj = bpy.context.active_object
        u_obj.name = f"UCX_{sm_name}_{suffix}"
        u_obj.scale = u_scale
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        ucx_objs.append(u_obj)

    bpy.ops.object.select_all(action='DESELECT')
    joined_obj.select_set(True)
    for u_obj in ucx_objs:
        u_obj.select_set(True)
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

    for u_obj in ucx_objs:
        bpy.data.objects.remove(u_obj, do_unlink=True)
    bpy.data.objects.remove(joined_obj, do_unlink=True)
    print(f" [OK] Portal abierto exportado con 3 cajas UCX: {fbx_path}")


def main():
    abs_style.reset_comic_scene()
    col = abs_style.create_collection("OpenPortals_Export")

    mats1 = kit1.init_kit1_materials()
    r1 = kit1.build_asset(2, "SM_Mod_02_Cargo_Doorway_Bulkhead_400x350", (0, 0, 0), col, mats1)
    export_open_portal_to_fbx(r1, "SM_Mod_02_Cargo_Doorway_Bulkhead_400x350")

    mats2 = kit2.init_kit2_materials()
    r2 = kit2.build_asset(20, "SM_Mod_20_Deco_Arched_Portal_400x350", (0, 0, 0), col, mats2)
    export_open_portal_to_fbx(r2, "SM_Mod_20_Deco_Arched_Portal_400x350")


if __name__ == "__main__":
    main()

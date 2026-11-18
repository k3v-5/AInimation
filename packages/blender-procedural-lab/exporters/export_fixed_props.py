import sys
import os
import bpy
import bmesh
import math
from mathutils import Vector, Euler

PROJECT_ROOT = "F:/Dev/Game"
sys.path.append(os.path.join(PROJECT_ROOT, "Art", "Blender"))

import astra_blender_styling as abs_style
import generar_lote2_props_maestros as lote2
import generar_lote10_props_maestros as lote10

FBX_DIR = os.path.join(PROJECT_ROOT, "Art", "FBX", "Props")
os.makedirs(FBX_DIR, exist_ok=True)

# -------------------------------------------------------------
# 1. EXPORT SM_Backup_Diesel_Generator (PROP 06)
# -------------------------------------------------------------
bpy.ops.wm.read_factory_settings(use_empty=True)
col = bpy.data.collections.new("Export_Generator")
bpy.context.scene.collection.children.link(col)
mats2 = lote2.create_materials()
gen_obj = lote2.build_prop06_diesel_generator(col, mats2)

# Ensure normals are recalculated outward
bpy.context.view_layer.objects.active = gen_obj
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')

# Center and ground
bbox = [Vector(b) for b in gen_obj.bound_box]
min_x = min(b.x for b in bbox)
max_x = max(b.x for b in bbox)
min_y = min(b.y for b in bbox)
max_y = max(b.y for b in bbox)
min_z = min(b.z for b in bbox)
max_z = max(b.z for b in bbox)

center_x = (min_x + max_x) * 0.5
center_y = (min_y + max_y) * 0.5
base_z = min_z

for v in gen_obj.data.vertices:
    v.co.x -= center_x
    v.co.y -= center_y
    v.co.z -= base_z
gen_obj.data.update()

# Add UCX collision
w = max_x - min_x
d = max_y - min_y
h = max_z - min_z
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, h * 0.5))
ucx_gen = bpy.context.active_object
ucx_gen.name = "UCX_SM_Backup_Diesel_Generator_01"
ucx_gen.scale = (w, d, h)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

gen_obj.name = "SM_Backup_Diesel_Generator"
bpy.ops.object.select_all(action='DESELECT')
gen_obj.select_set(True)
ucx_gen.select_set(True)
bpy.context.view_layer.objects.active = gen_obj

fbx_gen_path = os.path.join(FBX_DIR, "SM_Backup_Diesel_Generator.fbx")
bpy.ops.export_scene.fbx(
    filepath=fbx_gen_path,
    use_selection=True,
    apply_unit_scale=True,
    apply_scale_options='FBX_SCALE_ALL',
    axis_forward='-Z',
    axis_up='Y',
    mesh_smooth_type='FACE'
)
print(f"[OK] Exported fixed generator to: {fbx_gen_path}")

# -------------------------------------------------------------
# 2. EXPORT SM_Arc_Welding_Rig_Cart (PROP 47)
# -------------------------------------------------------------
bpy.ops.wm.read_factory_settings(use_empty=True)
col10 = bpy.data.collections.new("Export_Welder")
bpy.context.scene.collection.children.link(col10)
mats10 = lote10.init_lote10_materials()
welder_root = lote10.build_prop_47_welding_cart(0, 0, 0, col10, mats10)

# Join all children into single mesh or export hierarchy
bpy.ops.object.select_all(action='DESELECT')
children = [c for c in welder_root.children if c.type == 'MESH']
for c in children:
    c.select_set(True)
bpy.context.view_layer.objects.active = children[0]
bpy.ops.object.join()
joined_welder = bpy.context.active_object

bpy.context.view_layer.objects.active = joined_welder
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode='OBJECT')

bbox10 = [Vector(b) for b in joined_welder.bound_box]
min_x10 = min(b.x for b in bbox10)
max_x10 = max(b.x for b in bbox10)
min_y10 = min(b.y for b in bbox10)
max_y10 = max(b.y for b in bbox10)
min_z10 = min(b.z for b in bbox10)
max_z10 = max(b.z for b in bbox10)

center_x10 = (min_x10 + max_x10) * 0.5
center_y10 = (min_y10 + max_y10) * 0.5
base_z10 = min_z10

for v in joined_welder.data.vertices:
    v.co.x -= center_x10
    v.co.y -= center_y10
    v.co.z -= base_z10
joined_welder.data.update()

w10 = max_x10 - min_x10
d10 = max_y10 - min_y10
h10 = max_z10 - min_z10
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, h10 * 0.5))
ucx_weld = bpy.context.active_object
ucx_weld.name = "UCX_SM_Arc_Welding_Rig_Cart_01"
ucx_weld.scale = (w10, d10, h10)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

joined_welder.name = "SM_Arc_Welding_Rig_Cart"
bpy.ops.object.select_all(action='DESELECT')
joined_welder.select_set(True)
ucx_weld.select_set(True)
bpy.context.view_layer.objects.active = joined_welder

fbx_weld_path = os.path.join(FBX_DIR, "SM_Arc_Welding_Rig_Cart.fbx")
bpy.ops.export_scene.fbx(
    filepath=fbx_weld_path,
    use_selection=True,
    apply_unit_scale=True,
    apply_scale_options='FBX_SCALE_ALL',
    axis_forward='-Z',
    axis_up='Y',
    mesh_smooth_type='FACE'
)
print(f"[OK] Exported fixed welding cart to: {fbx_weld_path}")
print("[SUCCESS] All fixed props exported cleanly.")

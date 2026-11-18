"""check_parts_world_pos.py
Verifica la posicion en mundo de cada parte del SMG cuando esta parented a weapon.
"""
import bpy
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=r"E:\Darx_Proyect\Art\FBX\SK_FPS_Arms.fbx")
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]

with bpy.data.libraries.load(r"E:\Darx_Proyect\Art\Blender\SM_Wep_PhaseSMG_Workspace.blend", link=False) as (data_from, data_to):
    data_to.objects = [n for n in data_from.objects if n not in ("StudioTable", "Cam", "KeyLight", "FillLight", "RimLight", "Light_ReactorSMG")]

smg_objs = [o for o in data_to.objects if o is not None]
for o in smg_objs:
    bpy.context.scene.collection.objects.link(o)

bpy.ops.object.select_all(action='DESELECT')
for o in smg_objs:
    o.select_set(True)
bpy.context.view_layer.objects.active = smg_objs[0]
bpy.ops.object.join()
smg = bpy.context.active_object

smg.parent = arm
smg.parent_type = 'BONE'
smg.parent_bone = 'weapon'

bpy.context.view_layer.update()

# Imprimir posicion de vertices extremos
verts = [smg.matrix_world @ v.co for v in smg.data.vertices]
min_x = min(v.x for v in verts); max_x = max(v.x for v in verts)
min_y = min(v.y for v in verts); max_y = max(v.y for v in verts)
min_z = min(v.z for v in verts); max_z = max(v.z for v in verts)

print(f"SMG World Bounding Box:")
print(f"  X: {min_x:.4f} .. {max_x:.4f} (center = {(min_x+max_x)/2:.4f})")
print(f"  Y: {min_y:.4f} .. {max_y:.4f} (center = {(min_y+max_y)/2:.4f})")
print(f"  Z: {min_z:.4f} .. {max_z:.4f} (center = {(min_z+max_z)/2:.4f})")

# En SMG local:
# Buttpad estaba en Y = -0.282
# Muzzle estaba en Y = +0.579
p_butt = smg.matrix_world @ Vector((0, -0.282, 0.065))
p_muzzle = smg.matrix_world @ Vector((0, 0.579, 0.125))
p_grip = smg.matrix_world @ Vector((0, 0.008, 0.012))
p_foregrip = smg.matrix_world @ Vector((0, 0.24, -0.06))

print(f"  p_butt world: {p_butt}")
print(f"  p_muzzle world: {p_muzzle}")
print(f"  p_grip world: {p_grip}")
print(f"  p_foregrip world: {p_foregrip}")

# Huesos de la mano
hr = arm.pose.bones['hand_R']
hl = arm.pose.bones['hand_L']
print(f"  hand_R head world: {arm.matrix_world @ hr.head}")
print(f"  hand_L head world: {arm.matrix_world @ hl.head}")

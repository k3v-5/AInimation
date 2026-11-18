"""test_bone_parenting.py
Prueba parent directo a hueso weapon en SK_FPS_Arms y a hand_R en SK_Player.
"""
import bpy
from mathutils import Vector, Euler, Matrix

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
smg.name = "SMG"

# Parenting a hueso 'weapon'
smg.parent = arm
smg.parent_type = 'BONE'
smg.parent_bone = 'weapon'
smg.location = (0, 0, 0)
smg.rotation_euler = (0, 0, 0)

bpy.context.view_layer.update()
print("SMG parented to weapon with loc=(0,0,0) rot=(0,0,0):")
print("World matrix:")
print(smg.matrix_world)
print(f"SMG world location: {smg.matrix_world.translation}")

# Probemos con rotación en el hueso weapon
wb = arm.pose.bones['weapon']
wb.rotation_mode = 'XYZ'
wb.rotation_euler = (0, 0, 0)
bpy.context.view_layer.update()
print(f"When weapon rot=(0,0,0), SMG world loc: {smg.matrix_world.translation}")

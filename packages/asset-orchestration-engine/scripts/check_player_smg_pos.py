"""check_player_smg_pos.py
Verifica la posicion y orientacion del SMG parented a hand_R en SK_Player.
"""
import bpy
from mathutils import Vector, Euler, Matrix

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=r"E:\Darx_Proyect\Art\FBX\SK_Player.fbx")
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

# Parenting a hand_R
smg.parent = arm
smg.parent_type = 'BONE'
smg.parent_bone = 'hand_R'

bpy.context.view_layer.update()

hr = arm.pose.bones['hand_R']
print(f"hand_R rest matrix in world:\n{arm.matrix_world @ hr.matrix}")
print(f"SMG world matrix when parented to hand_R with loc=0 rot=0:\n{smg.matrix_world}")

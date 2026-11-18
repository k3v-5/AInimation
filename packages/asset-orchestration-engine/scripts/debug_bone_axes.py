"""debug_bone_axes.py
Inspecciona la orientacion de los ejes locales (roll y matrices) de los huesos de SK_Player.
"""
import bpy
from mathutils import Vector, Matrix

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=r"E:\Darx_Proyect\Art\FBX\SK_FPS_Arms.fbx")
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]

for bname in ('root', 'upperarm_R', 'forearm_R', 'hand_R', 'upperarm_L', 'forearm_L', 'hand_L'):
    b = arm.data.bones[bname]
    pb = arm.pose.bones[bname]
    print(f"\nBone {bname}:")
    print(f"  matrix_local:\n{b.matrix_local}")
    print(f"  X-axis (local in arm): {b.matrix_local.to_3x3() @ Vector((1, 0, 0))}")
    print(f"  Y-axis (along bone):   {b.matrix_local.to_3x3() @ Vector((0, 1, 0))}")
    print(f"  Z-axis (local in arm): {b.matrix_local.to_3x3() @ Vector((0, 0, 1))}")

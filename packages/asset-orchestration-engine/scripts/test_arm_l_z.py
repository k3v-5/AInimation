"""test_arm_l_z.py
Determina que rotZ en upperarm_L cruza el brazo hacia la derecha (+X).
"""
import bpy
import math
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=r"E:\Darx_Proyect\Art\FBX\SK_Player.fbx")
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
pb_ul = arm.pose.bones['upperarm_L']
pb_hl = arm.pose.bones['hand_L']
pb_ul.rotation_mode = 'XYZ'

for z_deg in (-60, -30, 0, 30, 60):
    pb_ul.rotation_euler = (math.radians(-30), 0, math.radians(z_deg))
    bpy.context.view_layer.update()
    pos = arm.matrix_world @ pb_hl.head
    print(f"upperarm_L rotZ={z_deg:+3d} -> hand_L X={pos.x:+.4f}, Y={pos.y:+.4f}, Z={pos.z:+.4f}")

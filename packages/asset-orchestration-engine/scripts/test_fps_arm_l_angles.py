"""test_fps_arm_l_angles.py
Determina que rotaciones en upperarm_L y forearm_L colocan hand_L
directamente sobre la empuñadura delantera en SK_FPS_Arms.
"""
import bpy
import math
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=r"E:\Darx_Proyect\Art\FBX\SK_FPS_Arms.fbx")
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]

for pb in arm.pose.bones:
    pb.rotation_mode = 'XYZ'

pb_ul = arm.pose.bones['upperarm_L']
pb_fl = arm.pose.bones['forearm_L']
pb_hl = arm.pose.bones['hand_L']

# Objetivo empuñadura delantera en FPS:
# En test_fps_5poses.py con smg.location = (0.01, 0.08, 0.0):
# Foregrip en mundo es aproximadamente X = +0.10, Y = -0.42, Z = -0.12
target = Vector((0.10, -0.42, -0.12))

best_dist = 1e9
best_rot = None

for ux in range(-60, 60, 10):
    for uz in range(-60, 60, 10):
        for fx in range(-80, 20, 10):
            for fz in range(-40, 40, 10):
                pb_ul.rotation_euler = (math.radians(ux), 0, math.radians(uz))
                pb_fl.rotation_euler = (math.radians(fx), 0, math.radians(fz))
                bpy.context.view_layer.update()
                pos = arm.matrix_world @ pb_hl.head
                dist = (pos - target).length
                if dist < best_dist:
                    best_dist = dist
                    best_rot = (ux, uz, fx, fz, pos)

print(f"Mejor rotacion brazo izquierdo FPS:")
print(f"  upperarm_L rotX={best_rot[0]}, rotZ={best_rot[1]}")
print(f"  forearm_L  rotX={best_rot[2]}, rotZ={best_rot[3]}")
print(f"  hand_L pos={best_rot[4]}, dist={best_dist:.4f} m")

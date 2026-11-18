# -*- coding: utf-8 -*-
import bpy
import math

arm = bpy.data.objects.get('ARM_FPS')
mesh = bpy.data.objects.get('SK_FPS_Arms')
act = bpy.data.actions.get('A_FPS_Unarmed_Punch_R')
print("Arm found:", arm is not None, "Mesh found:", mesh is not None, "Act found:", act is not None)

if arm and act:
    arm.animation_data.action = act
    scene = bpy.context.scene
    for f in [0, 2, 6, 9, 13]:
        scene.frame_set(f)
        bpy.context.view_layer.update()
        hl = arm.matrix_world @ arm.pose.bones["hand_L"].matrix.translation
        hr = arm.matrix_world @ arm.pose.bones["hand_R"].matrix.translation
        root = arm.matrix_world @ arm.pose.bones["root"].matrix.translation
        print(f"F{f:2d}: root=({root.x:.3f}, {root.y:.3f}, {root.z:.3f}) | hand_L=({hl.x:.3f}, {hl.y:.3f}, {hl.z:.3f}) | hand_R=({hr.x:.3f}, {hr.y:.3f}, {hr.z:.3f})")

# Check existing camera in blend
cams = [o for o in bpy.data.objects if o.type == 'CAMERA']
print("Existing cameras in blend:", [c.name for c in cams])
for c in cams:
    print(c.name, "loc:", c.location[:], "rot:", [round(math.degrees(a), 1) for a in c.rotation_euler])

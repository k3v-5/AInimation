"""inspect_player_walk_curves.py
Inspecciona qué canales y qué huesos anima A_Player_Walk.fbx
"""
import os
import bpy

WALK_FBX = r"E:\Darx_Proyect\Art\FBX\Anim_Player\A_Player_Walk.fbx"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=WALK_FBX)

arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
act = arm.animation_data.action

print(f"Action: {act.name}")
print(f"Frame range: {act.frame_range}")
print(f"Total fcurves: {len(act.fcurves) if hasattr(act, 'fcurves') else 'Blender 5 layers'}")

for pb in arm.pose.bones:
    if any(k in pb.name for k in ('thigh', 'calf', 'upperarm', 'hand')):
        print(f"Bone: {pb.name:15s} RotMode: {pb.rotation_mode} Rot: {pb.rotation_euler if pb.rotation_mode=='XYZ' else pb.rotation_quaternion}")

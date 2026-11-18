"""inspect_canon_rifle_idle.py
Inspecciona con detalle A_FPS_Rifle_Idle.fbx y A_Player_Rifle_Idle.fbx.
"""
import os
import math
import bpy

PROJECT_ROOT = r"E:\Darx_Proyect"
ART_DIR = os.path.join(PROJECT_ROOT, "Art")
FPS_RIFLE = os.path.join(ART_DIR, "FBX", "Anim_FPS", "A_FPS_Rifle_Idle.fbx")
PLAYER_RIFLE = os.path.join(ART_DIR, "FBX", "Anim_Player", "A_Player_Rifle_Idle.fbx")

print("="*60)
print("1. CANONICAL FPS RIFLE IDLE")
print("="*60)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=FPS_RIFLE)
arm_fps = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
bpy.context.scene.frame_set(0)
bpy.context.view_layer.update()

for pb in arm_fps.pose.bones:
    mw = arm_fps.matrix_world @ pb.matrix
    loc = mw.to_translation()
    rot = pb.matrix.to_euler()
    print(f"FPS {pb.name:15s} Loc: ({pb.location.x:.3f}, {pb.location.y:.3f}, {pb.location.z:.3f}) RotEulerDeg: ({math.degrees(rot.x):.1f}, {math.degrees(rot.y):.1f}, {math.degrees(rot.z):.1f}) WorldLoc: ({loc.x:.3f}, {loc.y:.3f}, {loc.z:.3f})")

print("\n" + "="*60)
print("2. CANONICAL 3P PLAYER RIFLE IDLE")
print("="*60)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=PLAYER_RIFLE)
arm_p = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
bpy.context.scene.frame_set(0)
bpy.context.view_layer.update()

for pb in arm_p.pose.bones:
    mw = arm_p.matrix_world @ pb.matrix
    loc = mw.to_translation()
    rot = pb.matrix.to_euler()
    print(f"3P {pb.name:15s} Loc: ({pb.location.x:.3f}, {pb.location.y:.3f}, {pb.location.z:.3f}) RotEulerDeg: ({math.degrees(rot.x):.1f}, {math.degrees(rot.y):.1f}, {math.degrees(rot.z):.1f}) WorldLoc: ({loc.x:.3f}, {loc.y:.3f}, {loc.z:.3f})")

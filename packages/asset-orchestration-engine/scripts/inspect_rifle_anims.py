"""inspect_rifle_anims.py
Inspecciona cómo están configurados los huesos en A_FPS_Rifle_Idle.fbx y A_FPS_Rifle_Walk.fbx.
"""
import os
import math
import bpy

PROJECT_ROOT = r"E:\Darx_Proyect"
ART_DIR = os.path.join(PROJECT_ROOT, "Art")
RIFLE_IDLE = os.path.join(ART_DIR, "FBX", "Anim_FPS", "A_FPS_Rifle_Idle.fbx")

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=RIFLE_IDLE)

arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
print(f"Armature: {arm.name}")
print(f"Action: {arm.animation_data.action.name if arm.animation_data and arm.animation_data.action else 'None'}")

bpy.context.scene.frame_set(0)
bpy.context.view_layer.update()

for pb in arm.pose.bones:
    rot_deg = [math.degrees(a) for a in pb.rotation_euler] if pb.rotation_mode == 'XYZ' else pb.rotation_quaternion
    mw = arm.matrix_world @ pb.matrix
    loc = mw.to_translation()
    print(f"Bone: {pb.name:15s} Loc: ({pb.location.x:.3f}, {pb.location.y:.3f}, {pb.location.z:.3f}) Rot: {rot_deg} WorldLoc: ({loc.x:.3f}, {loc.y:.3f}, {loc.z:.3f})")

# Also check 3P rifle anims if any exist
print("\nBuscando animaciones de Player (3P)...")
for root, dirs, files in os.walk(os.path.join(ART_DIR, "FBX")):
    for f in files:
        if f.endswith(".fbx") and "Player" in f and "SMG" not in f:
            print(f"Encontrado FBX de Player: {os.path.join(root, f)}")

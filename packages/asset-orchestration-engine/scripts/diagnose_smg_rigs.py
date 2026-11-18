"""diagnose_smg_rigs.py
Diagnóstico empírico de huesos, transforms de descanso y posicionamiento de grips para 1P y 3P.
"""
import os
import bpy
from mathutils import Vector, Euler, Matrix

PROJECT_ROOT = r"E:\Darx_Proyect"
ART_DIR = os.path.join(PROJECT_ROOT, "Art")
BLENDER_DIR = os.path.join(ART_DIR, "Blender")
SMG_BLEND = os.path.join(BLENDER_DIR, "SM_Wep_PhaseSMG_Workspace.blend")
FPS_FBX = os.path.join(ART_DIR, "FBX", "SK_FPS_Arms.fbx")
PLAYER_FBX = os.path.join(ART_DIR, "FBX", "SK_Player.fbx")

print("="*60)
print("1. DIAGNÓSTICO SK_FPS_Arms")
print("="*60)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=FPS_FBX)
fps_arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]

print(f"Armature FPS: {fps_arm.name}")
for b in fps_arm.data.bones:
    parent_name = b.parent.name if b.parent else "None"
    print(f"Bone: {b.name:20s} Parent: {parent_name:15s} Head: ({b.head_local.x:.3f}, {b.head_local.y:.3f}, {b.head_local.z:.3f}) Tail: ({b.tail_local.x:.3f}, {b.tail_local.y:.3f}, {b.tail_local.z:.3f})")

print("\nPose bones en Rest:")
for pb in fps_arm.pose.bones:
    mw = fps_arm.matrix_world @ pb.matrix
    loc = mw.to_translation()
    print(f"PB {pb.name:20s} WorldLoc: ({loc.x:.3f}, {loc.y:.3f}, {loc.z:.3f})")

print("="*60)
print("2. DIAGNÓSTICO SK_Player")
print("="*60)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=PLAYER_FBX)
player_arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]

print(f"Armature Player: {player_arm.name}")
for b in player_arm.data.bones:
    if any(k in b.name.lower() for k in ('hand', 'arm', 'weapon', 'spine', 'chest')):
        parent_name = b.parent.name if b.parent else "None"
        print(f"Bone: {b.name:20s} Parent: {parent_name:15s} Head: ({b.head_local.x:.3f}, {b.head_local.y:.3f}, {b.head_local.z:.3f})")

print("\nPose bones Player en Rest:")
for pb in player_arm.pose.bones:
    if any(k in pb.name.lower() for k in ('hand', 'arm', 'weapon', 'spine', 'chest')):
        mw = player_arm.matrix_world @ pb.matrix
        loc = mw.to_translation()
        print(f"PB {pb.name:20s} WorldLoc: ({loc.x:.3f}, {loc.y:.3f}, {loc.z:.3f})")

print("="*60)
print("3. DIAGNÓSTICO SM_Wep_PhaseSMG")
print("="*60)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.open_mainfile(filepath=SMG_BLEND)
print("Objetos en SMG Blend:")
for o in bpy.data.objects:
    if o.type == 'MESH':
        print(f"Mesh: {o.name:25s} Loc: ({o.location.x:.3f}, {o.location.y:.3f}, {o.location.z:.3f}) Dim: ({o.dimensions.x:.3f}, {o.dimensions.y:.3f}, {o.dimensions.z:.3f})")

print("\nDIAGNÓSTICO COMPLETADO.")

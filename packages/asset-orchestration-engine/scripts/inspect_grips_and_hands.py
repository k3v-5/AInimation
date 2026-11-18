"""inspect_grips_and_hands.py
Calcula la posición exacta de las empuñaduras del SMG y las manos en 1P y 3P.
"""
import os
import math
import bpy
from mathutils import Vector, Euler, Matrix

PROJECT_ROOT = r"E:\Darx_Proyect"
ART_DIR = os.path.join(PROJECT_ROOT, "Art")
BLENDER_DIR = os.path.join(ART_DIR, "Blender")
SMG_BLEND = os.path.join(BLENDER_DIR, "SM_Wep_PhaseSMG_Workspace.blend")
FPS_FBX = os.path.join(ART_DIR, "FBX", "SK_FPS_Arms.fbx")
PLAYER_FBX = os.path.join(ART_DIR, "FBX", "SK_Player.fbx")

# 1. Inspeccionar SMG Blend directamente
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.open_mainfile(filepath=SMG_BLEND)

print("\n" + "="*60)
print("1. OBJETOS Y GRIPS EN SM_Wep_PhaseSMG_Workspace.blend")
print("="*60)
for o in bpy.data.objects:
    if "grip" in o.name.lower() or "drum" in o.name.lower() or "receiver" in o.name.lower():
        bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
        center = sum(bb, Vector((0,0,0))) / 8.0
        print(f"{o.name:25s} Loc: ({o.location.x:.3f}, {o.location.y:.3f}, {o.location.z:.3f}) BBox Center: ({center.x:.3f}, {center.y:.3f}, {center.z:.3f})")

# 2. Inspeccionar FPS
print("\n" + "="*60)
print("2. INSPECCION FPS: Relación entre Weapon Bone y Manos")
print("="*60)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=FPS_FBX)
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]

print("Pose Bones en Rest:")
for bname in ['weapon', 'hand_R', 'forearm_R', 'hand_L', 'forearm_L']:
    pb = arm.pose.bones.get(bname)
    mw = arm.matrix_world @ pb.matrix
    loc = mw.to_translation()
    print(f"  {bname:12s} WorldLoc: ({loc.x:.3f}, {loc.y:.3f}, {loc.z:.3f})")

# 3. Inspeccionar 3P
print("\n" + "="*60)
print("3. INSPECCION 3P: Relación entre hand_R y hand_L")
print("="*60)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=PLAYER_FBX)
arm_p = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]

for bname in ['hand_R', 'forearm_R', 'upperarm_R', 'hand_L', 'forearm_L', 'upperarm_L', 'chest']:
    pb = arm_p.pose.bones.get(bname)
    mw = arm_p.matrix_world @ pb.matrix
    loc = mw.to_translation()
    print(f"  {bname:12s} WorldLoc: ({loc.x:.3f}, {loc.y:.3f}, {loc.z:.3f})")


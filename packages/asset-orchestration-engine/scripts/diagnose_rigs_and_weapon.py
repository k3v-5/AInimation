"""diagnose_rigs_and_weapon.py
Extrae medidas exactas de:
1. SM_Wep_PhaseSMG_Workspace.blend: dimensiones, centro, posición de empuñadura trasera, vertical, culata, mira.
2. SK_FPS_Arms.fbx: jerarquía de huesos, posiciones en rest pose, orientación.
3. SK_Player.fbx: jerarquía de huesos, posiciones en rest pose, distancia entre manos y pecho.
"""
import os
import bpy
from mathutils import Vector, Matrix

PROJECT_ROOT = r"E:\Darx_Proyect"
ART_DIR = os.path.join(PROJECT_ROOT, "Art")
BLENDER_DIR = os.path.join(ART_DIR, "Blender")
SMG_BLEND = os.path.join(BLENDER_DIR, "SM_Wep_PhaseSMG_Workspace.blend")
FPS_FBX = os.path.join(ART_DIR, "FBX", "SK_FPS_Arms.fbx")
PLAYER_FBX = os.path.join(ART_DIR, "FBX", "SK_Player.fbx")

print("--- 1. DIAGNOSTICO SMG ---")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.open_mainfile(filepath=SMG_BLEND)

# Calcular bounding box total de los objetos del arma
all_mesh_objs = [o for o in bpy.data.objects if o.type == 'MESH' and o.name not in ("StudioTable",)]
min_co = Vector((1e9, 1e9, 1e9))
max_co = Vector((-1e9, -1e9, -1e9))

for o in all_mesh_objs:
    for corner in o.bound_box:
        w_co = o.matrix_world @ Vector(corner)
        min_co.x = min(min_co.x, w_co.x)
        min_co.y = min(min_co.y, w_co.y)
        min_co.z = min(min_co.z, w_co.z)
        max_co.x = max(max_co.x, w_co.x)
        max_co.y = max(max_co.y, w_co.y)
        max_co.z = max(max_co.z, w_co.z)

print(f"SMG Bounding Box Min: {min_co}")
print(f"SMG Bounding Box Max: {max_co}")
print(f"SMG Size: X={max_co.x - min_co.x:.4f}, Y={max_co.y - min_co.y:.4f}, Z={max_co.z - min_co.z:.4f}")

# Buscar piezas clave
for o in all_mesh_objs:
    if any(k in o.name.lower() for k in ("grip", "stock", "drum", "sight", "trigger", "barrel")):
        print(f"  Part: {o.name} -> loc={o.location}")

print("\n--- 2. DIAGNOSTICO SK_FPS_Arms ---")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=FPS_FBX)
arm_fps = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
print(f"FPS Armature: {arm_fps.name}")
for b in arm_fps.data.bones:
    print(f"  Bone: {b.name}, head={b.head_local}, tail={b.tail_local}")

print("\n--- 3. DIAGNOSTICO SK_Player ---")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=PLAYER_FBX)
arm_player = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
print(f"Player Armature: {arm_player.name}")
for bname in ("pelvis", "spine", "chest", "head", "clavicle_R", "upperarm_R", "forearm_R", "hand_R", "clavicle_L", "upperarm_L", "forearm_L", "hand_L"):
    b = arm_player.data.bones.get(bname)
    if b:
        print(f"  Bone: {b.name}, head={b.head_local}, tail={b.tail_local}")

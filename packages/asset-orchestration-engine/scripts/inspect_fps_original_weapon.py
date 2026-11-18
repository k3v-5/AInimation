"""inspect_fps_original_weapon.py
Inspecciona la orientación y posición original de la pistola en SK_FPS_Arms.
"""
import os
import bpy
from mathutils import Vector, Euler, Matrix

PROJECT_ROOT = r"E:\Darx_Proyect"
ART_DIR = os.path.join(PROJECT_ROOT, "Art")
FPS_FBX = os.path.join(ART_DIR, "FBX", "SK_FPS_Arms.fbx")

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=FPS_FBX)
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
mesh = [o for o in bpy.data.objects if o.type == 'MESH'][0]

print("="*60)
print("ORIGINAL WEAPON IN FPS_FBX:")
print("="*60)
w_vg = mesh.vertex_groups.get('weapon')
if w_vg:
    v_weapon = [v.co for v in mesh.data.vertices if any(g.group == w_vg.index for g in v.groups)]
    print(f"Pistol vertices count: {len(v_weapon)}")
    min_c = Vector((min(v.x for v in v_weapon), min(v.y for v in v_weapon), min(v.z for v in v_weapon)))
    max_c = Vector((max(v.x for v in v_weapon), max(v.y for v in v_weapon), max(v.z for v in v_weapon)))
    center = (min_c + max_c) / 2.0
    print(f"Pistol BBox Min: ({min_c.x:.3f}, {min_c.y:.3f}, {min_c.z:.3f})")
    print(f"Pistol BBox Max: ({max_c.x:.3f}, {max_c.y:.3f}, {max_c.z:.3f})")
    print(f"Pistol BBox Center: ({center.x:.3f}, {center.y:.3f}, {center.z:.3f})")
    print(f"Pistol Dimensions: ({max_c.x-min_c.x:.3f}, {max_c.y-min_c.y:.3f}, {max_c.z-min_c.z:.3f})")

wb = arm.pose.bones.get('weapon')
print(f"Weapon Bone Matrix:\n{wb.matrix}")
print(f"Weapon Bone Head: {arm.data.bones['weapon'].head_local}")
print(f"Weapon Bone Tail: {arm.data.bones['weapon'].tail_local}")

# Also check hand_R and hand_L mesh vertices!
vg_hr = mesh.vertex_groups.get('hand_R')
if vg_hr:
    v_hr = [v.co for v in mesh.data.vertices if any(g.group == vg_hr.index for g in v.groups)]
    c_hr = sum(v_hr, Vector((0,0,0))) / len(v_hr)
    print(f"Hand_R vertices center: ({c_hr.x:.3f}, {c_hr.y:.3f}, {c_hr.z:.3f})")

vg_hl = mesh.vertex_groups.get('hand_L')
if vg_hl:
    v_hl = [v.co for v in mesh.data.vertices if any(g.group == vg_hl.index for g in v.groups)]
    c_hl = sum(v_hl, Vector((0,0,0))) / len(v_hl)
    print(f"Hand_L vertices center: ({c_hl.x:.3f}, {c_hl.y:.3f}, {c_hl.z:.3f})")

"""check_fps_weapon_matrix.py
Inspecciona la orientacion del hueso weapon y los vertices originales de la pistola.
"""
import bpy
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=r"E:\Darx_Proyect\Art\FBX\SK_FPS_Arms.fbx")

arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
mesh = [o for o in bpy.data.objects if o.type == 'MESH'][0]

weapon_bone = arm.pose.bones.get('weapon')
print(f"weapon bone matrix:\n{weapon_bone.matrix}")

# Vértices con peso en weapon
weapon_vg = mesh.vertex_groups.get('weapon')
if weapon_vg:
    weapon_verts = [v.co for v in mesh.data.vertices for g in v.groups if g.group == weapon_vg.index]
    min_x = min(v.x for v in weapon_verts)
    max_x = max(v.x for v in weapon_verts)
    min_y = min(v.y for v in weapon_verts)
    max_y = max(v.y for v in weapon_verts)
    min_z = min(v.z for v in weapon_verts)
    max_z = max(v.z for v in weapon_verts)
    print(f"Original weapon mesh bbox in SK_FPS_Arms:")
    print(f"  X: {min_x:.4f} .. {max_x:.4f}")
    print(f"  Y: {min_y:.4f} .. {max_y:.4f}")
    print(f"  Z: {min_z:.4f} .. {max_z:.4f}")

"""inspect_player_canonical_blend.py
Inspecciona el armature y la malla en DarX_Player_Rigged_Canonical.blend
"""
import os
import bpy

from mathutils import Vector

blend_path = r"E:\Darx_Proyect\Saved\Player_Skin_Workspace\DarX_Player_Rigged_Canonical.blend"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.open_mainfile(filepath=blend_path)

print("Objetos en blend:")
for o in bpy.data.objects:
    print(f"  {o.name:30s} Type: {o.type}")

arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
mesh = [o for o in bpy.data.objects if o.type == 'MESH'][0]

print(f"\nArmature: {arm.name}")
print(f"Mesh: {mesh.name}, Verts: {len(mesh.data.vertices)}")

print("\nEdit/Rest Bones vs Vertex Groups:")
for b in arm.data.bones:
    if any(k in b.name for k in ('hand', 'upperarm', 'forearm', 'chest')):
        vg = mesh.vertex_groups.get(b.name)
        if vg:
            v_in_g = [v.co for v in mesh.data.vertices if any(g.group == vg.index and g.weight > 0.5 for g in v.groups)]
            c = sum(v_in_g, Vector((0,0,0))) / len(v_in_g) if v_in_g else None
            print(f"Bone: {b.name:15s} Head: ({b.head_local.x:.3f}, {b.head_local.y:.3f}, {b.head_local.z:.3f}) | Mesh Verts Center: {f'({c.x:.3f}, {c.y:.3f}, {c.z:.3f})' if c else 'None'}")

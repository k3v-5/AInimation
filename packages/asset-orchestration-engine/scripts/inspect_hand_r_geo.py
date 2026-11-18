# -*- coding: utf-8 -*-
import bpy

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=r"E:\Darx_Proyect\Art\FBX\SK_FPS_Arms.fbx")
mesh = [o for o in bpy.data.objects if o.type == 'MESH'][0]

print("Mesh materials:")
for m in mesh.data.materials:
    print("  ", m.name if m else "None")

# Check polygons and materials on the right hand
mat_slots = set()
for poly in mesh.data.polygons:
    # check if vertices belong to hand_R
    is_hr = False
    for vi in poly.vertices:
        v = mesh.data.vertices[vi]
        groups = [mesh.vertex_groups[g.group].name for g in v.groups]
        if 'hand_R' in groups:
            is_hr = True
            break
    if is_hr:
        mat_slots.add(poly.material_index)

print("Material slots used by hand_R:", mat_slots)

# Check all vertices of hand_R
hr_verts = []
for v in mesh.data.vertices:
    for g in v.groups:
        if mesh.vertex_groups[g.group].name == 'hand_R':
            hr_verts.append((v.index, g.weight, [mesh.vertex_groups[g2.group].name for g2 in v.groups]))
            break

print(f"hand_R has {len(hr_verts)} vertices.")
# Sample 10 vertices
for item in hr_verts[:15]:
    print(" ", item)

# -*- coding: utf-8 -*-
import bpy

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=r"E:\Darx_Proyect\Art\FBX\SK_FPS_Arms.fbx")
mesh = [o for o in bpy.data.objects if o.type == 'MESH'][0]

print("Vertex groups in SK_FPS_Arms:")
for vg in mesh.vertex_groups:
    print("  ", vg.name)

# Count vertices with weapon/cell
w_count = 0
pure_w = 0
for v in mesh.data.vertices:
    groups = {mesh.vertex_groups[g.group].name: g.weight for g in v.groups}
    if 'weapon' in groups or 'cell' in groups:
        w_count += 1
        if len(groups) == 1 or (len(groups) == 2 and 'weapon' in groups and 'cell' in groups):
            pure_w += 1
        else:
            print(f"Vertex {v.index} has mixed groups:", groups)

print(f"Total verts: {len(mesh.data.vertices)}, with weapon/cell: {w_count}, pure weapon/cell: {pure_w}")

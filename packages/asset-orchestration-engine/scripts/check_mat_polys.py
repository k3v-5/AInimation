# -*- coding: utf-8 -*-
import bpy

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=r"E:\Darx_Proyect\Art\FBX\SK_FPS_Arms.fbx")
mesh = [o for o in bpy.data.objects if o.type == 'MESH'][0]

counts = {}
for p in mesh.data.polygons:
    mat_name = mesh.data.materials[p.material_index].name if p.material_index < len(mesh.data.materials) else "None"
    counts[mat_name] = counts.get(mat_name, 0) + 1

for name, cnt in counts.items():
    print(f"Material {name}: {cnt} polys")

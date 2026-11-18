# -*- coding: utf-8 -*-
import bpy

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=r"E:\Darx_Proyect\Art\FBX\SK_FPS_Arms.fbx")
mesh = [o for o in bpy.data.objects if o.type == 'MESH'][0]

vg_hr = mesh.vertex_groups['hand_R'].index
hr_verts = set(v.index for v in mesh.data.vertices if any(g.group == vg_hr and g.weight > 0.5 for g in v.groups))

# Check materials of polygons containing hand_R verts
poly_mats = {}
for p in mesh.data.polygons:
    if any(vi in hr_verts for vi in p.vertices):
        mname = mesh.data.materials[p.material_index].name
        poly_mats[mname] = poly_mats.get(mname, 0) + 1

print("Polygons in hand_R by material:", poly_mats)

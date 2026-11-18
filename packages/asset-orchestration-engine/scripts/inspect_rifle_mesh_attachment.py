"""inspect_rifle_mesh_attachment.py
Inspecciona si hay mallas de arma en A_FPS_Rifle_Idle.fbx o cómo se asocia.
"""
import os
import bpy

PROJECT_ROOT = r"E:\Darx_Proyect"
ART_DIR = os.path.join(PROJECT_ROOT, "Art")
FPS_RIFLE = os.path.join(ART_DIR, "FBX", "Anim_FPS", "A_FPS_Rifle_Idle.fbx")

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=FPS_RIFLE)

print("Objetos en A_FPS_Rifle_Idle.fbx:")
for o in bpy.data.objects:
    print(f"  Objeto: {o.name:25s} Tipo: {o.type:10s} Parent: {o.parent.name if o.parent else 'None'}")
    if o.type == 'MESH':
        print(f"    Vertex count: {len(o.data.vertices)}")
        print(f"    Vertex groups: {[vg.name for vg in o.vertex_groups]}")

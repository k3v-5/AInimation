import bpy
import os
import math
from mathutils import Vector, Euler, Matrix

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# 1. Import SK_FPS_Arms
fps_fbx = r"E:\Darx_Proyect\Art\FBX\SK_FPS_Arms.fbx"
bpy.ops.import_scene.fbx(filepath=fps_fbx)

arm = None
fps_mesh = None
for o in bpy.data.objects:
    if o.type == 'ARMATURE':
        arm = o
    elif o.type == 'MESH':
        fps_mesh = o

print("Imported Armature:", arm.name if arm else None)
print("Imported Mesh:", fps_mesh.name if fps_mesh else None)

# 2. Append SMG meshes from SM_Wep_PhaseSMG_Workspace.blend
smg_blend = r"E:\Darx_Proyect\Art\Blender\SM_Wep_PhaseSMG_Workspace.blend"
with bpy.data.libraries.load(smg_blend, link=False) as (data_from, data_to):
    data_to.objects = [name for name in data_from.objects if name not in ("StudioTable", "Cam", "KeyLight", "FillLight", "RimLight", "Light_ReactorSMG")]

smg_objs = []
for o in data_to.objects:
    if o is not None:
        scene.collection.objects.link(o)
        smg_objs.append(o)

print("Appended SMG objects:", len(smg_objs))

# Parent all SMG meshes to an Empty
smg_root = bpy.data.objects.new("SMG_Weapon_Root", None)
scene.collection.objects.link(smg_root)
for o in smg_objs:
    o.parent = smg_root

# Set camera
cam_data = bpy.data.cameras.new("FPS_Cam")
cam_data.lens = 28
cam_obj = bpy.data.objects.new("FPS_Cam", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_obj.location = (0.0, 0.05, 0.0)
cam_obj.rotation_euler = (math.radians(90), 0, math.radians(180))

# Lighting
sun = bpy.data.lights.new("Sun", 'SUN')
sun.energy = 4.0
sun_obj = bpy.data.objects.new("Sun", sun)
sun_obj.rotation_euler = (math.radians(45), math.radians(30), 0)
scene.collection.objects.link(sun_obj)

scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
test_render = r"E:\Darx_Proyect\Art\Blender\test_fps_smg_initial.png"
scene.render.filepath = test_render
bpy.ops.render.render(write_still=True)
print("Rendered test to:", test_render)

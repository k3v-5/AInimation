import bpy
import os
import math
from mathutils import Vector, Euler, Matrix

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# 1. Import SK_FPS_Arms
fps_fbx = r"E:\Darx_Proyect\Art\FBX\SK_FPS_Arms.fbx"
bpy.ops.import_scene.fbx(filepath=fps_fbx)

arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
fps_mesh = [o for o in bpy.data.objects if o.type == 'MESH'][0]

# Hide old pistol vertices
for v in fps_mesh.data.vertices:
    for g in v.groups:
        if fps_mesh.vertex_groups[g.group].name in ('weapon', 'cell'):
            v.co = Vector((0, 0, -100))
            break

# 2. Append SMG meshes
smg_blend = r"E:\Darx_Proyect\Art\Blender\SM_Wep_PhaseSMG_Workspace.blend"
with bpy.data.libraries.load(smg_blend, link=False) as (data_from, data_to):
    data_to.objects = [name for name in data_from.objects if name not in ("StudioTable", "Cam", "KeyLight", "FillLight", "RimLight", "Light_ReactorSMG")]

smg_objs = [o for o in data_to.objects if o is not None]
for o in smg_objs:
    scene.collection.objects.link(o)

bpy.ops.object.select_all(action='DESELECT')
for o in smg_objs:
    o.select_set(True)
bpy.context.view_layer.objects.active = smg_objs[0]
bpy.ops.object.join()
smg_mesh = bpy.context.active_object
smg_mesh.name = "SM_Wep_PhaseSMG_Ref"

for pb in arm.pose.bones:
    pb.rotation_mode = 'XYZ'

# Rotate SMG 180 degrees around Z so muzzle points forward (-Y) and stock points back (+Y)
# Also apply offset so rear grip aligns with hand_R
smg_mesh.rotation_euler = (0, 0, math.radians(180))
bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

# Now in SMG space (after 180 Z rot):
# Muzzle is at -Y (~ -0.575)
# Stock is at +Y (~ +0.282)
# Rear grip is at Y ~ +0.046, Z ~ -0.022
# Foregrip is at Y ~ -0.232, Z ~ -0.022

# Attach to weapon bone
c = smg_mesh.constraints.new('CHILD_OF')
c.target = arm
c.subtarget = 'weapon'
# weapon bone in SK_FPS_Arms has its own local axes. Let's inspect its alignment:
c.inverse_matrix = Matrix.Translation(Vector((0.0, 0.0, 0.0)))

# Let's set camera at player's eye looking towards -Y
cam_data = bpy.data.cameras.new("FPS_Cam")
cam_data.lens = 32
cam_obj = bpy.data.objects.new("FPS_Cam", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_obj.location = (0.0, 0.20, 0.0)

target = bpy.data.objects.new("CamTarget", None)
target.location = (0.05, -0.60, -0.15)
scene.collection.objects.link(target)
tt = cam_obj.constraints.new('TRACK_TO')
tt.target = target
tt.track_axis = 'TRACK_NEGATIVE_Z'
tt.up_axis = 'UP_Y'

# Studio Lights
l1_data = bpy.data.lights.new("Key", 'AREA')
l1_data.energy = 500
l1_data.size = 2.0
l1 = bpy.data.objects.new("Key", l1_data)
l1.location = (0.9, 0.0, 0.8)
scene.collection.objects.link(l1)

l2_data = bpy.data.lights.new("Rim", 'AREA')
l2_data.energy = 400
l2_data.size = 2.5
l2_data.color = (0.75, 0.2, 1.0)
l2 = bpy.data.objects.new("Rim", l2_data)
l2.location = (-1.0, -0.6, 0.6)
scene.collection.objects.link(l2)

l3_data = bpy.data.lights.new("Fill", 'AREA')
l3_data.energy = 200
l3_data.size = 2.0
l3 = bpy.data.objects.new("Fill", l3_data)
l3.location = (0.1, -1.2, 0.3)
scene.collection.objects.link(l3)

scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 960
scene.render.resolution_y = 540
out = r"E:\Darx_Proyect\Art\Blender\test_fps_smg_forward.png"
scene.render.filepath = out
bpy.ops.render.render(write_still=True)
print("Rendered to:", out)

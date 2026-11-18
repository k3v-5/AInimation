import bpy
import os
import math
from mathutils import Vector, Euler, Matrix

# Reset scene
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# 1. Import SK_FPS_Arms
fps_fbx = r"E:\Darx_Proyect\Art\FBX\SK_FPS_Arms.fbx"
bpy.ops.import_scene.fbx(filepath=fps_fbx)

arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
fps_mesh = [o for o in bpy.data.objects if o.type == 'MESH'][0]

# Hide the old pistol geometry by collapsing vertices in 'weapon' and 'cell' groups to 0
for v in fps_mesh.data.vertices:
    is_old_gun = False
    for g in v.groups:
        vg_name = fps_mesh.vertex_groups[g.group].name
        if vg_name in ('weapon', 'cell'):
            is_old_gun = True
            break
    if is_old_gun:
        v.co = Vector((0, 0, -100)) # Move far away or hide

# 2. Append SMG meshes
smg_blend = r"E:\Darx_Proyect\Art\Blender\SM_Wep_PhaseSMG_Workspace.blend"
with bpy.data.libraries.load(smg_blend, link=False) as (data_from, data_to):
    data_to.objects = [name for name in data_from.objects if name not in ("StudioTable", "Cam", "KeyLight", "FillLight", "RimLight", "Light_ReactorSMG")]

smg_objs = []
for o in data_to.objects:
    if o is not None:
        scene.collection.objects.link(o)
        smg_objs.append(o)

# Join SMG meshes into a single reference object
bpy.ops.object.select_all(action='DESELECT')
for o in smg_objs:
    o.select_set(True)
bpy.context.view_layer.objects.active = smg_objs[0]
bpy.ops.object.join()
smg_mesh = bpy.context.active_object
smg_mesh.name = "SM_Wep_PhaseSMG_Ref"

# Parent to bone 'weapon'
# In SK_FPS_Arms, bone 'weapon' is at (0.098, -0.226, -0.088).
# In SMG local coords, rear grip is around (0, -0.046, -0.022).
# Let's attach smg_mesh to 'weapon' bone using a Child-Of constraint
c = smg_mesh.constraints.new('CHILD_OF')
c.target = arm
c.subtarget = 'weapon'
# Let's adjust offset so rear grip fits comfortably into the right hand:
c.inverse_matrix = Matrix.Translation(Vector((0.0, 0.05, 0.02)))

# Pose test: let's pose left arm to grab the vertical foregrip!
# The vertical foregrip is at SMG local (0, 0.232, -0.022).
for pb in arm.pose.bones:
    pb.rotation_mode = 'XYZ'

# Let's rotate left arm so hand_L wraps the foregrip
pb_uL = arm.pose.bones['upperarm_L']
pb_fL = arm.pose.bones['forearm_L']
pb_hL = arm.pose.bones['hand_L']

pb_uL.rotation_euler = (math.radians(24), math.radians(-12), math.radians(32))
pb_fL.rotation_euler = (math.radians(-42), math.radians(18), math.radians(-26))
pb_hL.rotation_euler = (math.radians(15), math.radians(-10), math.radians(20))

# Setup Camera (FPS view)
cam_data = bpy.data.cameras.new("FPS_Cam")
cam_data.lens = 30
cam_obj = bpy.data.objects.new("FPS_Cam", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_obj.location = (0.0, 0.18, 0.0)

target = bpy.data.objects.new("CamTarget", None)
target.location = (0.02, -0.45, -0.10)
scene.collection.objects.link(target)
tt = cam_obj.constraints.new('TRACK_TO')
tt.target = target
tt.track_axis = 'TRACK_NEGATIVE_Z'
tt.up_axis = 'UP_Y'

# Studio Lights
l1_data = bpy.data.lights.new("Key", 'AREA')
l1_data.energy = 400
l1_data.size = 1.5
l1 = bpy.data.objects.new("Key", l1_data)
l1.location = (0.8, -0.2, 0.6)
scene.collection.objects.link(l1)

l2_data = bpy.data.lights.new("Rim", 'AREA')
l2_data.energy = 350
l2_data.size = 2.0
l2_data.color = (0.75, 0.2, 1.0)
l2 = bpy.data.objects.new("Rim", l2_data)
l2.location = (-0.8, -0.4, 0.5)
scene.collection.objects.link(l2)

l3_data = bpy.data.lights.new("Fill", 'AREA')
l3_data.energy = 150
l3_data.size = 1.5
l3 = bpy.data.objects.new("Fill", l3_data)
l3.location = (0.0, -1.0, 0.2)
scene.collection.objects.link(l3)

scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 960
scene.render.resolution_y = 540
out = r"E:\Darx_Proyect\Art\Blender\test_fps_smg_grip.png"
scene.render.filepath = out
bpy.ops.render.render(write_still=True)
print("Rendered to:", out)

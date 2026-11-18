import bpy
import os
import math
from mathutils import Vector, Euler, Matrix

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# 1. Import SK_Player
player_fbx = r"E:\Darx_Proyect\Art\FBX\SK_Player.fbx"
bpy.ops.import_scene.fbx(filepath=player_fbx)

arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
player_mesh = [o for o in bpy.data.objects if o.type == 'MESH'][0]

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

# Torso & Spine: upright, alert tactical posture
arm.pose.bones['spine'].rotation_euler = (math.radians(-2), 0, math.radians(-10))
arm.pose.bones['chest'].rotation_euler = (math.radians(-2), 0, math.radians(-8))
arm.pose.bones['head'].rotation_euler = (math.radians(2), 0, math.radians(12))

# Position the SMG with safe clearance (>= 15cm from torso, no clipping):
# Stock at X = 0.18, Y = 0.16, Z = 1.34 (resting in shoulder pocket)
# Receiver at Y = 0.44
# Foregrip at Y = 0.68
smg_mesh.location = (0.18, 0.44, 1.32)
smg_mesh.rotation_euler = (math.radians(-2), math.radians(1), math.radians(-2))

# Right arm (shoulder and elbow bend naturally to hold rear grip):
arm.pose.bones['clavicle_R'].rotation_euler = (0, 0, math.radians(5))
arm.pose.bones['upperarm_R'].rotation_euler = (math.radians(-48), math.radians(18), math.radians(-22))
arm.pose.bones['forearm_R'].rotation_euler = (math.radians(-62), math.radians(0), math.radians(24))
arm.pose.bones['hand_R'].rotation_euler = (math.radians(16), math.radians(-12), math.radians(10))

# Left arm (reaches forward to hold vertical foregrip):
arm.pose.bones['clavicle_L'].rotation_euler = (0, 0, math.radians(12))
arm.pose.bones['upperarm_L'].rotation_euler = (math.radians(-58), math.radians(-16), math.radians(36))
arm.pose.bones['forearm_L'].rotation_euler = (math.radians(-48), math.radians(12), math.radians(-18))
arm.pose.bones['hand_L'].rotation_euler = (math.radians(10), math.radians(-8), math.radians(15))

# Legs in grounded ready stance:
arm.pose.bones['thigh_R'].rotation_euler = (math.radians(10), 0, math.radians(6))
arm.pose.bones['calf_R'].rotation_euler = (math.radians(12), 0, 0)
arm.pose.bones['thigh_L'].rotation_euler = (math.radians(-14), 0, math.radians(-6))
arm.pose.bones['calf_L'].rotation_euler = (math.radians(16), 0, 0)

# Camera (Front 3/4 hero view)
cam_data = bpy.data.cameras.new("TP_Cam")
cam_data.lens = 42
cam_obj = bpy.data.objects.new("TP_Cam", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_obj.location = (1.8, 2.3, 1.25)

target = bpy.data.objects.new("Target", None)
target.location = (0.08, 0.20, 1.15)
scene.collection.objects.link(target)
tt = cam_obj.constraints.new('TRACK_TO')
tt.target = target
tt.track_axis = 'TRACK_NEGATIVE_Z'
tt.up_axis = 'UP_Y'

# Studio Lights
l1_data = bpy.data.lights.new("Key", 'POINT')
l1_data.energy = 950
l1 = bpy.data.objects.new("Key", l1_data)
l1.location = (2.0, 1.8, 2.4)
scene.collection.objects.link(l1)

l2_data = bpy.data.lights.new("Rim", 'POINT')
l2_data.energy = 750
l2_data.color = (0.75, 0.2, 1.0)
l2 = bpy.data.objects.new("Rim", l2_data)
l2.location = (-1.8, -1.8, 2.0)
scene.collection.objects.link(l2)

l3_data = bpy.data.lights.new("Fill", 'POINT')
l3_data.energy = 400
l3 = bpy.data.objects.new("Fill", l3_data)
l3.location = (-1.5, 2.0, 1.2)
scene.collection.objects.link(l3)

scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 960
scene.render.resolution_y = 540
out = r"E:\Darx_Proyect\Art\Blender\test_tp_smg_clean_stance.png"
scene.render.filepath = out
bpy.ops.render.render(write_still=True)
print("Rendered to:", out)

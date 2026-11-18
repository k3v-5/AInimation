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

# Aim / Stance:
# Character faces +Y.
# We want the weapon at chest height: X ~ 0.16, Y ~ 0.28, Z ~ 1.30, pointing towards +Y.
# In SMG coords, muzzle is +Y, stock is -Y. So SMG already points towards +Y!
# Rear grip is at (0, -0.046, -0.022) in SMG coords.
# Vertical foregrip is at (0, +0.232, -0.022) in SMG coords.

# Let's position the weapon in world space directly in front of the right shoulder:
# Shoulder is at X ~ 0.18, Y ~ 0.0, Z ~ 1.38.
# Weapon root positioned so rear grip is at X = 0.16, Y = 0.24, Z = 1.30:
smg_mesh.location = (0.16, 0.286, 1.322)
smg_mesh.rotation_euler = (math.radians(-4), math.radians(2), math.radians(0))

# Now let's pose arm bones so hand_R reaches rear grip and hand_L reaches foregrip:
# Torso angled slightly for shooting:
arm.pose.bones['spine'].rotation_euler = (math.radians(-2), 0, math.radians(-12))
arm.pose.bones['chest'].rotation_euler = (math.radians(-4), 0, math.radians(-10))
arm.pose.bones['head'].rotation_euler = (math.radians(2), 0, math.radians(16))

# Right arm:
arm.pose.bones['upperarm_R'].rotation_euler = (math.radians(-32), math.radians(14), math.radians(-18))
arm.pose.bones['forearm_R'].rotation_euler = (math.radians(-72), math.radians(0), math.radians(12))
arm.pose.bones['hand_R'].rotation_euler = (math.radians(12), math.radians(-16), math.radians(10))

# Left arm:
arm.pose.bones['upperarm_L'].rotation_euler = (math.radians(-52), math.radians(-22), math.radians(26))
arm.pose.bones['forearm_L'].rotation_euler = (math.radians(-64), math.radians(18), math.radians(-14))
arm.pose.bones['hand_L'].rotation_euler = (math.radians(-14), math.radians(12), math.radians(-24))

# Legs in stable braced stance:
arm.pose.bones['thigh_R'].rotation_euler = (math.radians(12), 0, math.radians(8))
arm.pose.bones['calf_R'].rotation_euler = (math.radians(14), 0, 0)
arm.pose.bones['thigh_L'].rotation_euler = (math.radians(-16), 0, math.radians(-6))
arm.pose.bones['calf_L'].rotation_euler = (math.radians(18), 0, 0)

# Camera (Front 3/4 hero view of full character)
cam_data = bpy.data.cameras.new("TP_Cam")
cam_data.lens = 42
cam_obj = bpy.data.objects.new("TP_Cam", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_obj.location = (1.9, 2.3, 1.25)

target = bpy.data.objects.new("Target", None)
target.location = (0.05, 0.10, 1.10)
scene.collection.objects.link(target)
tt = cam_obj.constraints.new('TRACK_TO')
tt.target = target
tt.track_axis = 'TRACK_NEGATIVE_Z'
tt.up_axis = 'UP_Y'

# Studio Lights
l1_data = bpy.data.lights.new("Key", 'POINT')
l1_data.energy = 900
l1 = bpy.data.objects.new("Key", l1_data)
l1.location = (2.0, 1.8, 2.4)
scene.collection.objects.link(l1)

l2_data = bpy.data.lights.new("Rim", 'POINT')
l2_data.energy = 700
l2_data.color = (0.75, 0.2, 1.0)
l2 = bpy.data.objects.new("Rim", l2_data)
l2.location = (-1.8, -1.8, 2.0)
scene.collection.objects.link(l2)

l3_data = bpy.data.lights.new("Fill", 'POINT')
l3_data.energy = 350
l3 = bpy.data.objects.new("Fill", l3_data)
l3.location = (-1.5, 2.0, 1.2)
scene.collection.objects.link(l3)

scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 960
scene.render.resolution_y = 540
out = r"E:\Darx_Proyect\Art\Blender\test_tp_smg_natural_aim.png"
scene.render.filepath = out
bpy.ops.render.render(write_still=True)
print("Rendered to:", out)

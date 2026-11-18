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

# Let's set up a standard Aim / Shoot pose:
# Torso angled slightly
arm.pose.bones['spine'].rotation_euler = (math.radians(4), 0, math.radians(15))
arm.pose.bones['chest'].rotation_euler = (math.radians(2), 0, math.radians(12))
arm.pose.bones['head'].rotation_euler = (math.radians(0), 0, math.radians(-15))

# Right arm: raised to shoulder level, aiming forward
# upperarm_R: -78 forward, -12 out
arm.pose.bones['upperarm_R'].rotation_euler = (math.radians(-78), math.radians(0), math.radians(16))
arm.pose.bones['forearm_R'].rotation_euler = (math.radians(-42), math.radians(0), math.radians(0))
arm.pose.bones['hand_R'].rotation_euler = (math.radians(0), math.radians(0), math.radians(0))

# Left arm: reaching forward to vertical foregrip
arm.pose.bones['upperarm_L'].rotation_euler = (math.radians(-62), math.radians(0), math.radians(-32))
arm.pose.bones['forearm_L'].rotation_euler = (math.radians(-52), math.radians(0), math.radians(18))
arm.pose.bones['hand_L'].rotation_euler = (math.radians(10), math.radians(0), math.radians(-10))

# Legs in stable shooting stance
arm.pose.bones['thigh_R'].rotation_euler = (math.radians(8), 0, math.radians(6))
arm.pose.bones['calf_R'].rotation_euler = (math.radians(12), 0, 0)
arm.pose.bones['thigh_L'].rotation_euler = (math.radians(-14), 0, math.radians(-6))
arm.pose.bones['calf_L'].rotation_euler = (math.radians(16), 0, 0)

bpy.context.view_layer.update()

# Let's place the SMG so that its rear grip is at hand_R world position,
# pointing towards -Y (forward), with top rail towards +Z (up).
mw_hand = arm.matrix_world @ arm.pose.bones['hand_R'].matrix
hand_loc = mw_hand.to_translation()
print("Hand_R location:", [round(x, 3) for x in hand_loc])

# In SMG coords (where muzzle is +Y, stock is -Y):
# To aim forward along -Y: rotate 180 around Z!
# If rear grip is at (0, -0.046, -0.022):
# We parent smg_mesh to arm with bone 'hand_R'
c = smg_mesh.constraints.new('CHILD_OF')
c.target = arm
c.subtarget = 'hand_R'

# Let's test a clean local transform relative to hand_R:
# hand_R rest matrix has bone Y pointing down (-Z) and bone Z pointing forward (-Y)
# Let's set inverse_matrix to identity and set smg_mesh location/rotation in hand space:
c.inverse_matrix = Matrix.Identity(4)
smg_mesh.rotation_euler = (math.radians(-90), math.radians(90), 0)
smg_mesh.location = (0.02, 0.05, -0.04)

# Camera (3/4 front view)
cam_data = bpy.data.cameras.new("TP_Cam")
cam_data.lens = 45
cam_obj = bpy.data.objects.new("TP_Cam", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_obj.location = (2.2, -2.4, 1.40)

target = bpy.data.objects.new("Target", None)
target.location = (0.1, -0.2, 1.20)
scene.collection.objects.link(target)
tt = cam_obj.constraints.new('TRACK_TO')
tt.target = target
tt.track_axis = 'TRACK_NEGATIVE_Z'
tt.up_axis = 'UP_Y'

# Studio Lights
l1_data = bpy.data.lights.new("Key", 'POINT')
l1_data.energy = 900
l1 = bpy.data.objects.new("Key", l1_data)
l1.location = (2.2, -2.2, 2.5)
scene.collection.objects.link(l1)

l2_data = bpy.data.lights.new("Rim", 'POINT')
l2_data.energy = 700
l2_data.color = (0.75, 0.2, 1.0)
l2 = bpy.data.objects.new("Rim", l2_data)
l2.location = (-2.0, 2.0, 2.2)
scene.collection.objects.link(l2)

l3_data = bpy.data.lights.new("Fill", 'POINT')
l3_data.energy = 350
l3 = bpy.data.objects.new("Fill", l3_data)
l3.location = (-1.8, -2.0, 1.2)
scene.collection.objects.link(l3)

scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 960
scene.render.resolution_y = 540
out = r"E:\Darx_Proyect\Art\Blender\test_tp_smg_aim.png"
scene.render.filepath = out
bpy.ops.render.render(write_still=True)
print("Rendered to:", out)

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

# Torso & Spine:
# Bladed stance: torso rotated slightly clockwise (Z = -12 deg)
arm.pose.bones['spine'].rotation_euler = (math.radians(4), 0, math.radians(-12))
arm.pose.bones['chest'].rotation_euler = (math.radians(2), 0, math.radians(-8))
arm.pose.bones['neck'].rotation_euler = (math.radians(0), 0, math.radians(16))
arm.pose.bones['head'].rotation_euler = (math.radians(-2), 0, math.radians(6))

# Right arm:
# Shoulder pushes forward (+X) and inward (+Z):
arm.pose.bones['clavicle_R'].rotation_euler = (math.radians(4), 0, math.radians(8))
arm.pose.bones['upperarm_R'].rotation_euler = (math.radians(52), math.radians(-8), math.radians(38))
arm.pose.bones['forearm_R'].rotation_euler = (math.radians(44), math.radians(12), math.radians(10))
arm.pose.bones['hand_R'].rotation_euler = (math.radians(-12), math.radians(18), math.radians(15))

# Left arm:
# Shoulder pushes forward (+X) and reaches across chest (-Z):
arm.pose.bones['clavicle_L'].rotation_euler = (math.radians(6), 0, math.radians(-12))
arm.pose.bones['upperarm_L'].rotation_euler = (math.radians(64), math.radians(12), math.radians(-34))
arm.pose.bones['forearm_L'].rotation_euler = (math.radians(38), math.radians(-16), math.radians(-12))
arm.pose.bones['hand_L'].rotation_euler = (math.radians(18), math.radians(-12), math.radians(-25))

# Legs in braced tactical shooting stance:
arm.pose.bones['thigh_R'].rotation_euler = (math.radians(-14), 0, math.radians(8))
arm.pose.bones['calf_R'].rotation_euler = (math.radians(-18), 0, 0)
arm.pose.bones['thigh_L'].rotation_euler = (math.radians(16), 0, math.radians(-6))
arm.pose.bones['calf_L'].rotation_euler = (math.radians(-8), 0, 0)

bpy.context.view_layer.update()

# Get hand_R position in world space
mw_hR = arm.matrix_world @ arm.pose.bones['hand_R'].matrix
pos_hR = mw_hR.to_translation()
print('Hand_R position:', [round(x, 3) for x in pos_hR])
mw_hL = arm.matrix_world @ arm.pose.bones['hand_L'].matrix
pos_hL = mw_hL.to_translation()
print('Hand_L position:', [round(x, 3) for x in pos_hL])

# Position the SMG so rear grip is right at hand_R, pointing towards +Y
# In SMG coords, rear grip is at Y = -0.046, Z = -0.022.
# So weapon origin is at pos_hR + (0, +0.046, +0.022)
smg_mesh.location = (pos_hR[0], pos_hR[1] + 0.046, pos_hR[2] + 0.022)
smg_mesh.rotation_euler = (math.radians(-2), math.radians(0), math.radians(-4))

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
out = r"E:\Darx_Proyect\Art\Blender\test_tp_smg_real_aim.png"
scene.render.filepath = out
bpy.ops.render.render(write_still=True)
print("Rendered to:", out)

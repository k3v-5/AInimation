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

# In SK_Player, the model looks towards -Y.
# In SMG coords, muzzle is at +Y, stock is at -Y.
# So SMG should be rotated 180 degrees around Z so muzzle points towards -Y.
smg_mesh.rotation_euler = (0, 0, math.radians(180))
bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

# Attach to hand_R
c = smg_mesh.constraints.new('CHILD_OF')
c.target = arm
c.subtarget = 'hand_R'
# In hand_R local coords, let's adjust position:
c.inverse_matrix = Matrix.Translation(Vector((0.0, 0.05, 0.02)))

# Pose the character in a solid two-handed tactical rifle/SMG carry:
# Right arm:
pb_uR = arm.pose.bones['upperarm_R']
pb_fR = arm.pose.bones['forearm_R']
pb_hR = arm.pose.bones['hand_R']

# Left arm:
pb_uL = arm.pose.bones['upperarm_L']
pb_fL = arm.pose.bones['forearm_L']
pb_hL = arm.pose.bones['hand_L']

# Torso & Pelvis:
pb_spine = arm.pose.bones['spine']
pb_chest = arm.pose.bones['chest']
pb_head = arm.pose.bones['head']

pb_spine.rotation_euler = (math.radians(4), 0, math.radians(-6))
pb_chest.rotation_euler = (math.radians(2), 0, math.radians(-8))
pb_head.rotation_euler = (math.radians(2), 0, math.radians(12))

# Right arm holding grip at chest/waist height
pb_uR.rotation_euler = (math.radians(-42), math.radians(12), math.radians(16))
pb_fR.rotation_euler = (math.radians(-54), math.radians(0), math.radians(0))
pb_hR.rotation_euler = (math.radians(12), math.radians(-10), math.radians(0))

# Left arm wrapping across chest to grasp vertical foregrip
pb_uL.rotation_euler = (math.radians(-58), math.radians(-18), math.radians(-24))
pb_fL.rotation_euler = (math.radians(-68), math.radians(14), math.radians(16))
pb_hL.rotation_euler = (math.radians(-8), math.radians(12), math.radians(-20))

# Legs in slight combat ready stance
arm.pose.bones['thigh_R'].rotation_euler = (math.radians(8), 0, math.radians(4))
arm.pose.bones['calf_R'].rotation_euler = (math.radians(10), 0, 0)
arm.pose.bones['thigh_L'].rotation_euler = (math.radians(-12), 0, math.radians(-4))
arm.pose.bones['calf_L'].rotation_euler = (math.radians(16), 0, 0)

# Camera (3/4 front action perspective)
cam_data = bpy.data.cameras.new("TP_Cam")
cam_data.lens = 45
cam_obj = bpy.data.objects.new("TP_Cam", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_obj.location = (2.2, -2.6, 1.35)

target = bpy.data.objects.new("Target", None)
target.location = (0.0, -0.10, 1.05)
scene.collection.objects.link(target)
tt = cam_obj.constraints.new('TRACK_TO')
tt.target = target
tt.track_axis = 'TRACK_NEGATIVE_Z'
tt.up_axis = 'UP_Y'

# Studio Lights
l1_data = bpy.data.lights.new("Key", 'POINT')
l1_data.energy = 850
l1 = bpy.data.objects.new("Key", l1_data)
l1.location = (2.2, -2.2, 2.5)
scene.collection.objects.link(l1)

l2_data = bpy.data.lights.new("Rim", 'POINT')
l2_data.energy = 650
l2_data.color = (0.75, 0.2, 1.0)
l2 = bpy.data.objects.new("Rim", l2_data)
l2.location = (-2.0, 2.0, 2.2)
scene.collection.objects.link(l2)

l3_data = bpy.data.lights.new("Fill", 'POINT')
l3_data.energy = 300
l3 = bpy.data.objects.new("Fill", l3_data)
l3.location = (-1.8, -2.0, 1.2)
scene.collection.objects.link(l3)

scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 960
scene.render.resolution_y = 540
out = r"E:\Darx_Proyect\Art\Blender\test_tp_smg_carry.png"
scene.render.filepath = out
bpy.ops.render.render(write_still=True)
print("Rendered to:", out)

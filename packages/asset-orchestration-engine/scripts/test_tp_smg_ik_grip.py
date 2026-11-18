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

# Rotate torso into combat Weaver stance (bladed upper body):
arm.pose.bones['spine'].rotation_euler = (math.radians(4), 0, math.radians(20))
arm.pose.bones['chest'].rotation_euler = (math.radians(2), 0, math.radians(18))
arm.pose.bones['head'].rotation_euler = (math.radians(0), 0, math.radians(-35))
arm.pose.bones['clavicle_R'].rotation_euler = (0, 0, math.radians(-5))
arm.pose.bones['clavicle_L'].rotation_euler = (0, 0, math.radians(15))

# Position the SMG at chest/shoulder level pointing forward (+Y):
# Stock tucked right into right pectoral (X ~ 0.14, Y ~ 0.12, Z ~ 1.34)
# Rear grip is at X ~ 0.14, Y ~ 0.36, Z ~ 1.28
# Foregrip is at X ~ 0.14, Y ~ 0.64, Z ~ 1.28
smg_mesh.location = (0.14, 0.40, 1.30)
smg_mesh.rotation_euler = (math.radians(2), math.radians(-1), math.radians(2))

# Create targets for IK:
t_R = bpy.data.objects.new("Target_Grip_R", None)
t_R.location = (0.14, 0.354, 1.278) # Rear grip
scene.collection.objects.link(t_R)

t_L = bpy.data.objects.new("Target_Grip_L", None)
t_L.location = (0.14, 0.632, 1.278) # Foregrip
scene.collection.objects.link(t_L)

# Add IK to forearm_R and forearm_L
c_ik_R = arm.pose.bones['forearm_R'].constraints.new('IK')
c_ik_R.target = t_R
c_ik_R.chain_count = 2

c_ik_L = arm.pose.bones['forearm_L'].constraints.new('IK')
c_ik_L.target = t_L
c_ik_L.chain_count = 2

# Legs in tactical shooting stance
arm.pose.bones['thigh_R'].rotation_euler = (math.radians(-12), 0, math.radians(8))
arm.pose.bones['calf_R'].rotation_euler = (math.radians(18), 0, 0)
arm.pose.bones['thigh_L'].rotation_euler = (math.radians(14), 0, math.radians(-6))
arm.pose.bones['calf_L'].rotation_euler = (math.radians(12), 0, 0)

bpy.context.view_layer.update()

# Hand alignments:
# In IK, the hand bone follows forearm. Let's adjust hand rotation to grip:
arm.pose.bones['hand_R'].rotation_euler = (math.radians(-10), math.radians(15), math.radians(20))
arm.pose.bones['hand_L'].rotation_euler = (math.radians(-20), math.radians(25), math.radians(45))

# Camera (Front 3/4 hero view)
cam_data = bpy.data.cameras.new("TP_Cam")
cam_data.lens = 42
cam_obj = bpy.data.objects.new("TP_Cam", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_obj.location = (1.8, 2.2, 1.30)

target = bpy.data.objects.new("Target", None)
target.location = (0.08, 0.25, 1.15)
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
out = r"E:\Darx_Proyect\Art\Blender\test_tp_smg_ik_grip.png"
scene.render.filepath = out
bpy.ops.render.render(write_still=True)
print("Rendered to:", out)

# Print the evaluated angles
for b in ['upperarm_R', 'forearm_R', 'upperarm_L', 'forearm_L']:
    pb = arm.pose.bones[b]
    # matrix in parent space
    m = pb.matrix
    print(f'{b} evaluated loc: {[round(x, 3) for x in m.to_translation()]}')

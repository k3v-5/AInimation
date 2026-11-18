"""test_player_ik_bake.py
Bake visual del IK en SK_Player para garantizar que el solver pose los huesos del brazo izquierdo.
"""
import bpy
import math
import shutil
from mathutils import Vector, Euler

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

bpy.ops.import_scene.fbx(filepath=r"E:\Darx_Proyect\Art\FBX\SK_Player.fbx")
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
player_mesh = [o for o in bpy.data.objects if o.type == 'MESH'][0]

with bpy.data.libraries.load(r"E:\Darx_Proyect\Art\Blender\SM_Wep_PhaseSMG_Workspace.blend", link=False) as (data_from, data_to):
    data_to.objects = [n for n in data_from.objects if n not in ("StudioTable", "Cam", "KeyLight", "FillLight", "RimLight", "Light_ReactorSMG")]

smg_objs = [o for o in data_to.objects if o is not None]
for o in smg_objs:
    scene.collection.objects.link(o)

bpy.ops.object.select_all(action='DESELECT')
for o in smg_objs:
    o.select_set(True)
bpy.context.view_layer.objects.active = smg_objs[0]
bpy.ops.object.join()
smg = bpy.context.active_object
smg.name = "SMG"

# Parenting a hand_R
smg.parent = arm
smg.parent_type = 'BONE'
smg.parent_bone = 'hand_R'

# Orientación calibrada:
smg.rotation_euler = (math.radians(-15.68), math.radians(-167.9), math.radians(-6.74))
smg.location = (0.0, 0.05, 0.01)

for pb in arm.pose.bones:
    pb.rotation_mode = 'XYZ'

# Torso y cabeza
pb_spine = arm.pose.bones['spine']
pb_chest = arm.pose.bones['chest']
pb_head = arm.pose.bones['head']

pb_spine.rotation_euler = (math.radians(6), 0, math.radians(-8))
pb_chest.rotation_euler = (math.radians(4), 0, math.radians(-6))
pb_head.rotation_euler = (math.radians(-4), 0, math.radians(10))

# Brazo derecho
pb_cr = arm.pose.bones['clavicle_R']
pb_ur = arm.pose.bones['upperarm_R']
pb_fr = arm.pose.bones['forearm_R']
pb_hr = arm.pose.bones['hand_R']

pb_cr.rotation_euler = (math.radians(-2), 0, math.radians(-4))
pb_ur.rotation_euler = (math.radians(-42), math.radians(4), math.radians(-18))
pb_fr.rotation_euler = (math.radians(-50), math.radians(-8), math.radians(10))
pb_hr.rotation_euler = (math.radians(10), math.radians(-10), math.radians(-4))

# Empty en el mango vertical Tommy del SMG
fg_target = bpy.data.objects.new("ForegripTarget", None)
fg_target.parent = smg
fg_target.location = (0.0, 0.23, -0.06)
scene.collection.objects.link(fg_target)

# Pole target para el codo izquierdo
pole_l = bpy.data.objects.new("ElbowPole_L", None)
pole_l.parent = arm
pole_l.location = (-0.5, 0.2, 1.0)
scene.collection.objects.link(pole_l)

bpy.context.view_layer.update()

# IK en hand_L
pb_hl = arm.pose.bones['hand_L']
c_ik = pb_hl.constraints.new('IK')
c_ik.target = fg_target
c_ik.pole_target = pole_l
c_ik.pole_angle = math.radians(90)
c_ik.chain_count = 2

# Animar y Visual Bake
arm.animation_data_create()
act = bpy.data.actions.new(name="A_Test_Bake_3P")
arm.animation_data.action = act
scene.frame_set(1)

bpy.ops.object.select_all(action='DESELECT')
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='POSE')
bpy.ops.pose.select_all(action='SELECT')

bpy.ops.nla.bake(
    frame_start=1,
    frame_end=1,
    only_selected=False,
    visual_keying=True,
    clear_constraints=False,
    bake_types={'POSE'}
)
bpy.ops.object.mode_set(mode='OBJECT')

# Imprimir posicion final de hand_L y foregrip
bpy.context.view_layer.update()
print(f"Foregrip target world: {fg_target.matrix_world.translation}")
print(f"hand_L head world: {arm.matrix_world @ pb_hl.head}")

# Luces
l1 = bpy.data.objects.new("L1", bpy.data.lights.new("L1", 'SUN'))
l1.data.energy = 3.5
l1.rotation_euler = (0.8, 0.3, -0.6)
scene.collection.objects.link(l1)

l2 = bpy.data.objects.new("L2", bpy.data.lights.new("L2", 'AREA'))
l2.data.energy = 500.0
l2.data.size = 2.5
l2.location = (1.5, -2.0, 1.6)
scene.collection.objects.link(l2)

l3 = bpy.data.objects.new("L3", bpy.data.lights.new("L3", 'AREA'))
l3.data.energy = 350.0
l3.data.size = 2.0
l3.data.color = (0.75, 0.2, 1.0)
l3.location = (-1.5, 1.0, 1.5)
scene.collection.objects.link(l3)

# Cámara 3/4 frontal
cam_data = bpy.data.cameras.new("Cam3P")
cam_data.lens = 45
cam = bpy.data.objects.new("Cam3P", cam_data)
cam.location = (1.5, -2.4, 1.35)

target = bpy.data.objects.new("CamTarget", None)
target.location = (0.05, -0.2, 1.25)
scene.collection.objects.link(target)

tt = cam.constraints.new('TRACK_TO')
tt.target = target
tt.track_axis = 'TRACK_NEGATIVE_Z'
tt.up_axis = 'UP_Y'

scene.collection.objects.link(cam)
scene.camera = cam

scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 960
scene.render.resolution_y = 540
out_img = r"E:\Darx_Proyect\Art\Blender\test_player_ik_bake.png"
scene.render.filepath = out_img
bpy.ops.render.render(write_still=True)
shutil.copyfile(out_img, r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2\test_player_ik_bake.png")
print("Rendered test_player_ik_bake.png")

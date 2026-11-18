import bpy, math, os
from mathutils import Vector, Euler, Matrix

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# 1. Import Player
bpy.ops.import_scene.fbx(filepath=r'E:\Darx_Proyect\Art\FBX\SK_Player.fbx')
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
arm.name = 'ARM_Player'
mesh = [o for o in bpy.data.objects if o.type == 'MESH'][0]

# 2. Import SMG
with bpy.data.libraries.load(r'E:\Darx_Proyect\Art\Blender\SM_Wep_PhaseSMG_Workspace.blend', link=False) as (df, dt):
    dt.objects = [n for n in df.objects if n not in ('StudioTable', 'Cam', 'KeyLight', 'FillLight', 'RimLight', 'Light_ReactorSMG')]
for o in dt.objects: scene.collection.objects.link(o)
bpy.ops.object.select_all(action='DESELECT')
for o in dt.objects: o.select_set(True)
bpy.context.view_layer.objects.active = dt.objects[0]
bpy.ops.object.join()
smg = bpy.context.active_object
smg.name = 'SMG'

# 3. Position SMG in front of player
# Rotated 180 in Z to face -Y, slightly angled down 5 deg
smg.rotation_euler = (math.radians(-5), math.radians(0), math.radians(180))
smg.location = (0.16, -0.40, 1.32)

bpy.context.view_layer.update()

rgrip_world = smg.matrix_world @ Vector((0, -0.0465, -0.0225))
fgrip_world = smg.matrix_world @ Vector((0, 0.2318, -0.0220))
butt_world = smg.matrix_world @ Vector((0, -0.282, 0.065))
muzzle_world = smg.matrix_world @ Vector((0, 0.565, 0.085))

print('SMG Butt world pos:', butt_world)
print('SMG Rear Grip world pos:', rgrip_world)
print('SMG Foregrip world pos:', fgrip_world)

# Create IK targets
t_r = bpy.data.objects.new('Target_R', None)
t_r.location = rgrip_world
scene.collection.objects.link(t_r)

t_l = bpy.data.objects.new('Target_L', None)
t_l.location = fgrip_world
scene.collection.objects.link(t_l)

# Set base torso / legs stance
pb_spine = arm.pose.bones['spine']
pb_spine.rotation_mode = 'XYZ'
pb_spine.rotation_euler = (math.radians(-4), 0, math.radians(-12))

pb_chest = arm.pose.bones['chest']
pb_chest.rotation_mode = 'XYZ'
pb_chest.rotation_euler = (math.radians(-2), 0, math.radians(-8))

pb_pelvis = arm.pose.bones['pelvis']
pb_pelvis.rotation_mode = 'XYZ'
pb_pelvis.rotation_euler = (0, 0, math.radians(4))

pb_head = arm.pose.bones['head']
pb_head.rotation_mode = 'XYZ'
pb_head.rotation_euler = (math.radians(2), 0, math.radians(20))

# Setup IK constraints
ik_r = arm.pose.bones['hand_R'].constraints.new('IK')
ik_r.target = t_r
ik_r.chain_count = 2

ik_l = arm.pose.bones['hand_L'].constraints.new('IK')
ik_l.target = t_l
ik_l.chain_count = 2

bpy.context.view_layer.update()

# Render test view
cam = bpy.data.cameras.new('TestCam')
cam.lens = 45
cam_obj = bpy.data.objects.new('TestCam', cam)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_obj.location = (1.4, -2.3, 1.35)
target = bpy.data.objects.new('CamTarget', None)
target.location = (0.05, -0.2, 1.25)
scene.collection.objects.link(target)
tt = cam_obj.constraints.new('TRACK_TO')
tt.target = target
tt.track_axis = 'TRACK_NEGATIVE_Z'
tt.up_axis = 'UP_Y'

# Light
l = bpy.data.objects.new('Sun', bpy.data.lights.new('Sun', 'SUN'))
l.data.energy = 3.5
l.rotation_euler = (0.8, 0.3, -0.6)
scene.collection.objects.link(l)

scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 960
scene.render.resolution_y = 540
out_path = r'C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2\test_ik_pose_3p.png'
scene.render.filepath = out_path
bpy.ops.render.render(write_still=True)
print('Rendered to:', out_path)

import bpy, math, os
from mathutils import Vector, Euler, Matrix

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# 1. Import Player
bpy.ops.import_scene.fbx(filepath=r'E:\Darx_Proyect\Art\FBX\SK_Player.fbx')
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
arm.name = 'ARM_Player'
mesh = [o for o in bpy.data.objects if o.type == 'MESH'][0]

for pb in arm.pose.bones: pb.rotation_mode = 'XYZ'

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

# Torso bladed stance (Yaw on Y!)
arm.pose.bones['spine'].rotation_euler = (math.radians(-6), math.radians(14), 0)
arm.pose.bones['chest'].rotation_euler = (math.radians(-4), math.radians(12), 0)
arm.pose.bones['head'].rotation_euler  = (math.radians(4),  math.radians(-24), 0) # looks forward

# Legs combat stance
arm.pose.bones['thigh_R'].rotation_euler = (math.radians(14), 0, math.radians(-4))
arm.pose.bones['calf_R'].rotation_euler  = (math.radians(-12), 0, 0)
arm.pose.bones['thigh_L'].rotation_euler = (math.radians(-14), 0, math.radians(6))
arm.pose.bones['calf_L'].rotation_euler  = (math.radians(8), 0, 0)

# Clavicles
arm.pose.bones['clavicle_L'].rotation_euler = (0, 0, math.radians(-12)) # shoulder forward
arm.pose.bones['clavicle_R'].rotation_euler = (0, 0, math.radians(-4))

bpy.context.view_layer.update()

# Position SMG in world
# Muzzle points to -Y, stock rests in front of right shoulder (X~0.16, Y~-0.16, Z~1.38)
# Buttpad is at local (0, -0.282, 0.065)
# SMG rotated 180 in Z to face -Y, pitched down -4 deg
smg.rotation_euler = (math.radians(-4), 0, math.radians(180))
smg.location = (0.17, -0.42, 1.34)
bpy.context.view_layer.update()

rgrip_world = smg.matrix_world @ Vector((0, -0.0465, -0.0225))
fgrip_world = smg.matrix_world @ Vector((0, 0.2318, -0.0220))
butt_world  = smg.matrix_world @ Vector((0, -0.282, 0.065))
print('Butt world:', butt_world)
print('Rear grip world:', rgrip_world)
print('Foregrip world:', fgrip_world)

# Arm rotations:
# Right arm holding rear grip:
# upperarm_R: reaches forward (-X) and slightly in (+Z)
arm.pose.bones['upperarm_R'].rotation_euler = (math.radians(-28), math.radians(-12), math.radians(18))
arm.pose.bones['forearm_R'].rotation_euler  = (math.radians(-64), math.radians(14),  math.radians(-16))
arm.pose.bones['hand_R'].rotation_euler     = (math.radians(10),  math.radians(-15), math.radians(12))

# Left arm reaching across chest to foregrip:
# upperarm_L: reaches forward (-X) and inward (-Z)
arm.pose.bones['upperarm_L'].rotation_euler = (math.radians(-48), math.radians(10),  math.radians(-44))
arm.pose.bones['forearm_L'].rotation_euler  = (math.radians(-42), math.radians(-14), math.radians(-22))
arm.pose.bones['hand_L'].rotation_euler     = (math.radians(-8),  math.radians(18),  math.radians(-10))

bpy.context.view_layer.update()

# Let's inspect distance from hand_R to rgrip and hand_L to fgrip:
h_r = (arm.matrix_world @ arm.pose.bones['hand_R'].matrix).to_translation()
h_l = (arm.matrix_world @ arm.pose.bones['hand_L'].matrix).to_translation()
print(f'Hand R to Rear grip dist: {(h_r - rgrip_world).length*100:.2f} cm (hand={h_r})')
print(f'Hand L to Fore grip dist: {(h_l - fgrip_world).length*100:.2f} cm (hand={h_l})')

# Parent SMG to hand_R using parent_set with KEEP TRANSFORM so it moves perfectly with hand_R!
bpy.ops.object.select_all(action='DESELECT')
smg.select_set(True)
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
arm.data.bones.active = arm.data.bones['hand_R']
# In pose mode:
bpy.ops.object.mode_set(mode='POSE')
bpy.ops.object.parent_set(type='BONE')
bpy.ops.object.mode_set(mode='OBJECT')
print('Parented SMG to hand_R with native KEEP_TRANSFORM!')

# Render test view
cam = bpy.data.cameras.new('TestCam')
cam.lens = 42
cam_obj = bpy.data.objects.new('TestCam', cam)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_obj.location = (1.4, -2.4, 1.35)
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
out_path = r'C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2\test_player_perfect_pose.png'
scene.render.filepath = out_path
bpy.ops.render.render(write_still=True)
print('Rendered to:', out_path)

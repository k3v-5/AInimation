import bpy, math
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

bpy.ops.import_scene.fbx(filepath=r'E:\Darx_Proyect\Art\FBX\SK_Player.fbx')
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
mesh = [o for o in bpy.data.objects if o.type == 'MESH'][0]
for pb in arm.pose.bones: pb.rotation_mode = 'XYZ'

# Torso bladed combat stance (facing +Y):
# Spine & chest rotated to bring left shoulder forward (+Y)
arm.pose.bones['spine'].rotation_euler = (math.radians(-4), math.radians(-15), 0)
arm.pose.bones['chest'].rotation_euler = (math.radians(-2), math.radians(-15), 0)
arm.pose.bones['head'].rotation_euler  = (math.radians(2),  math.radians(28), 0) # head looks forward to +Y
arm.pose.bones['clavicle_L'].rotation_euler = (0, 0, math.radians(18)) # shoulder forward
arm.pose.bones['clavicle_R'].rotation_euler = (0, 0, math.radians(-6))

# Legs combat stance (facing +Y)
arm.pose.bones['thigh_R'].rotation_euler = (math.radians(-16), 0, math.radians(-4)) # right leg back
arm.pose.bones['calf_R'].rotation_euler  = (math.radians(14), 0, 0)
arm.pose.bones['thigh_L'].rotation_euler = (math.radians(18), 0, math.radians(6))  # left leg forward
arm.pose.bones['calf_L'].rotation_euler  = (math.radians(-12), 0, 0)

# Import SMG
with bpy.data.libraries.load(r'E:\Darx_Proyect\Art\Blender\SM_Wep_PhaseSMG_Workspace.blend', link=False) as (df, dt):
    dt.objects = [n for n in df.objects if n not in ('StudioTable', 'Cam', 'KeyLight', 'FillLight', 'RimLight', 'Light_ReactorSMG')]
for o in dt.objects: scene.collection.objects.link(o)
bpy.ops.object.select_all(action='DESELECT')
for o in dt.objects: o.select_set(True)
bpy.context.view_layer.objects.active = dt.objects[0]
bpy.ops.object.join()
smg = bpy.context.active_object
smg.name = 'SMG'

# Weapon orientation facing +Y
smg.rotation_euler = (math.radians(-4), math.radians(2), math.radians(6))
smg.location = (0.14, 0.22, 1.28)
bpy.context.view_layer.update()

rgrip = smg.matrix_world @ Vector((0, -0.0465, -0.0225))
fgrip = smg.matrix_world @ Vector((0, 0.2318, -0.0220))
butt  = smg.matrix_world @ Vector((0, -0.282, 0.065))
print('Stock Butt world:', butt)
print('Rear grip world:', rgrip)
print('Foregrip world:', fgrip)

# Right arm pose to hold rear grip:
arm.pose.bones['upperarm_R'].rotation_euler = (math.radians(42), math.radians(-15), math.radians(-18))
arm.pose.bones['forearm_R'].rotation_euler  = (math.radians(52), math.radians(10), math.radians(15))
arm.pose.bones['hand_R'].rotation_euler     = (math.radians(8), math.radians(12), math.radians(-10))

# Left arm pose to hold front vertical grip:
arm.pose.bones['upperarm_L'].rotation_euler = (math.radians(55), math.radians(25), math.radians(-38))
arm.pose.bones['forearm_L'].rotation_euler  = (math.radians(48), math.radians(-15), math.radians(-25))
arm.pose.bones['hand_L'].rotation_euler     = (math.radians(10), math.radians(-20), math.radians(35))

bpy.context.view_layer.update()

# Camera looking at front 3/4 (from +X, +Y, +Z):
cam = bpy.data.cameras.new('Cam')
cam.lens = 42
cam_obj = bpy.data.objects.new('Cam', cam)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_obj.location = (1.4, 2.4, 1.35)
target = bpy.data.objects.new('CamTarget', None)
target.location = (0.05, 0.1, 1.25)
scene.collection.objects.link(target)
tt = cam_obj.constraints.new('TRACK_TO')
tt.target = target
tt.track_axis = 'TRACK_NEGATIVE_Z'
tt.up_axis = 'UP_Y'

# Lights in front (+Y)
l1 = bpy.data.objects.new('Key', bpy.data.lights.new('Key', 'SUN'))
l1.data.energy = 3.5
l1.rotation_euler = (math.radians(-50), math.radians(20), math.radians(160))
scene.collection.objects.link(l1)

l2 = bpy.data.objects.new('Fill', bpy.data.lights.new('Fill', 'AREA'))
l2.data.energy = 400.0
l2.data.size = 2.0
l2.location = (-1.2, 2.0, 1.5)
scene.collection.objects.link(l2)

scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 960
scene.render.resolution_y = 540
out_img = r'C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2\test_player_tactical_stance.png'
scene.render.filepath = out_img
bpy.ops.render.render(write_still=True)
print('Rendered to:', out_img)

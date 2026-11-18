import bpy, math
from mathutils import Vector

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

# Torso stance (Player faces +Y!)
# Bladed stance: Right shoulder back (-Y), left shoulder forward (+Y)
# Chest local Y rotates yaw!
arm.pose.bones['spine'].rotation_euler = (math.radians(-4), math.radians(12), 0)
arm.pose.bones['chest'].rotation_euler = (math.radians(-2), math.radians(10), 0)
arm.pose.bones['head'].rotation_euler  = (math.radians(2),  math.radians(-20), 0) # head looks forward to +Y
arm.pose.bones['clavicle_L'].rotation_euler = (0, 0, math.radians(-12)) # shoulder pushed forward
arm.pose.bones['clavicle_R'].rotation_euler = (0, 0, math.radians(-4))

# Legs combat stance (facing +Y)
arm.pose.bones['thigh_R'].rotation_euler = (math.radians(-14), 0, math.radians(-4)) # right leg back
arm.pose.bones['calf_R'].rotation_euler  = (math.radians(12), 0, 0)
arm.pose.bones['thigh_L'].rotation_euler = (math.radians(16), 0, math.radians(6))  # left leg forward
arm.pose.bones['calf_L'].rotation_euler  = (math.radians(-10), 0, 0)

# Arms:
# Right arm: rotX > 0 (forward), rotZ > 0 (inward to centerline)
arm.pose.bones['upperarm_R'].rotation_euler = (math.radians(38), math.radians(-8), math.radians(42))
arm.pose.bones['forearm_R'].rotation_euler  = (math.radians(56), math.radians(12), math.radians(8))
arm.pose.bones['hand_R'].rotation_euler     = (math.radians(8), math.radians(15), math.radians(-20))

# Left arm: rotX > 0 (forward), rotZ < 0 (inward to centerline)
arm.pose.bones['upperarm_L'].rotation_euler = (math.radians(48), math.radians(14), math.radians(-54))
arm.pose.bones['forearm_L'].rotation_euler  = (math.radians(44), math.radians(-10), math.radians(-16))
arm.pose.bones['hand_L'].rotation_euler     = (math.radians(12), math.radians(-18), math.radians(25))

bpy.context.view_layer.update()

# Position SMG facing +Y:
# In SMG blend, local +Y is forward. So rot = (0, 0, 0) points to +Y!
smg.rotation_euler = (math.radians(-4), math.radians(2), math.radians(4)) # slightly pitched down 4 deg
# Position SMG in front of player
# Stock buttpad is at local (0, -0.282, 0.065). If SMG at (0.16, 0.35, 1.28):
# buttpad is at (0.16, 0.35 - 0.282, 1.28 + 0.065) = (0.16, 0.068, 1.345) [resting on right shoulder front!]
smg.location = (0.17, 0.36, 1.27)
bpy.context.view_layer.update()

# Evaluate hand positions:
dg = bpy.context.evaluated_depsgraph_get()
eval_mesh = mesh.evaluated_get(dg).to_mesh()

vg_r = mesh.vertex_groups['hand_R']
verts_r = [v.index for v in mesh.data.vertices for g in v.groups if g.group == vg_r.index and g.weight > 0.8]
h_r = sum((eval_mesh.vertices[i].co for i in verts_r), Vector()) / len(verts_r)

vg_l = mesh.vertex_groups['hand_L']
verts_l = [v.index for v in mesh.data.vertices for g in v.groups if g.group == vg_l.index and g.weight > 0.8]
h_l = sum((eval_mesh.vertices[i].co for i in verts_l), Vector()) / len(verts_l)

rgrip = smg.matrix_world @ Vector((0, -0.0465, -0.0225))
fgrip = smg.matrix_world @ Vector((0, 0.2318, -0.0220))
butt  = smg.matrix_world @ Vector((0, -0.282, 0.065))
print('Stock Butt world:', butt)
print('Rear grip world:', rgrip, 'Evaluated hand_R:', h_r, f'dist={(h_r-rgrip).length*100:.2f}cm')
print('Foregrip world:', fgrip, 'Evaluated hand_L:', h_l, f'dist={(h_l-fgrip).length*100:.2f}cm')

# Camera looking from front 3/4 at (+X, +Y, +Z):
cam = bpy.data.cameras.new('Cam')
cam.lens = 42
cam_obj = bpy.data.objects.new('Cam', cam)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_obj.location = (1.4, 2.4, 1.35)
target = bpy.data.objects.new('CamTarget', None)
target.location = (0.05, 0.2, 1.25)
scene.collection.objects.link(target)
tt = cam_obj.constraints.new('TRACK_TO')
tt.target = target
tt.track_axis = 'TRACK_NEGATIVE_Z'
tt.up_axis = 'UP_Y'

# Lights
l1 = bpy.data.objects.new('Key', bpy.data.lights.new('Key', 'SUN'))
l1.data.energy = 3.5
l1.rotation_euler = (0.8, -0.3, 0.6)
scene.collection.objects.link(l1)

scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 960
scene.render.resolution_y = 540
out_img = r'C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2\test_player_forward_combat.png'
scene.render.filepath = out_img
bpy.ops.render.render(write_still=True)
print('Rendered to:', out_img)

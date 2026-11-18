import bpy, math
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

bpy.ops.import_scene.fbx(filepath=r'E:\Darx_Proyect\Art\FBX\SK_FPS_Arms.fbx')
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
mesh = [o for o in bpy.data.objects if o.type == 'MESH'][0]

for v in mesh.data.vertices:
    for g in v.groups:
        if mesh.vertex_groups[g.group].name in ('weapon', 'cell'):
            v.co = Vector((0, 0, -100))
            break

for pb in arm.pose.bones: pb.rotation_mode = 'XYZ'

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
smg.parent = arm
smg.parent_type = 'BONE'
smg.parent_bone = 'weapon'
smg.location = (0.01, 0.04, 0.0)

# Right arm pose (natural viewmodel holding weapon):
arm.pose.bones['upperarm_R'].rotation_euler = (math.radians(-10), math.radians(4), math.radians(-2))
arm.pose.bones['forearm_R'].rotation_euler  = (math.radians(-12), math.radians(2), 0)
arm.pose.bones['hand_R'].rotation_euler     = (math.radians(2), math.radians(-4), math.radians(2))
arm.pose.bones['weapon'].rotation_euler     = (math.radians(-4), math.radians(4), 0)

bpy.context.view_layer.update()

fgrip = smg.matrix_world @ Vector((0, 0.2318, -0.0220))
print('Foregrip target in world:', fgrip)

# Shoulder clavicle extension forward/inward + arm rotation:
arm.pose.bones['upperarm_L'].location = (0.16, -0.10, 0.22)
arm.pose.bones['upperarm_L'].rotation_euler = (math.radians(-32), math.radians(22), math.radians(16))
arm.pose.bones['forearm_L'].rotation_euler  = (math.radians(-28), math.radians(-18), math.radians(12))
arm.pose.bones['hand_L'].rotation_euler     = (math.radians(20), math.radians(-20), math.radians(50))

bpy.context.view_layer.update()
hl = (arm.matrix_world @ arm.pose.bones['hand_L'].matrix).to_translation()
print('hand_L wrist pos:', hl, f'dist to fgrip: {(hl-fgrip).length*100:.2f}cm')

# Camera
cam = bpy.data.cameras.new('Cam')
cam.lens = 18
cam_obj = bpy.data.objects.new('Cam', cam)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_obj.location = (0.01, 0.24, 0.06)
cam_obj.rotation_euler = (math.radians(88), 0, math.radians(180))

# Lights
l1 = bpy.data.objects.new('Key', bpy.data.lights.new('Key', 'SUN'))
l1.data.energy = 3.5
l1.rotation_euler = (0.7, 0.3, -2.4)
scene.collection.objects.link(l1)

scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 960
scene.render.resolution_y = 540
out_img = r'C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2\test_fps_clamped_grip.png'
scene.render.filepath = out_img
bpy.ops.render.render(write_still=True)
print('Rendered to:', out_img)

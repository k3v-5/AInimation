import bpy, math, time
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# 1. Import FPS arms
bpy.ops.import_scene.fbx(filepath=r'E:\Darx_Proyect\Art\FBX\SK_FPS_Arms.fbx')
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
arm.name = 'ARM_FPS'
fps_mesh = [o for o in bpy.data.objects if o.type == 'MESH'][0]

for v in fps_mesh.data.vertices:
    for g in v.groups:
        if fps_mesh.vertex_groups[g.group].name in ('weapon', 'cell'):
            v.co = Vector((0, 0, -100))
            break

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

smg.parent = arm
smg.parent_type = 'BONE'
smg.parent_bone = 'weapon'
smg.location = (0.01, 0.08, 0.0)
smg.rotation_euler = (0, 0, 0)

# Base Right Hand pose
arm.pose.bones['upperarm_R'].rotation_euler = (math.radians(-8), math.radians(4), math.radians(-2))
arm.pose.bones['forearm_R'].rotation_euler  = (math.radians(-14), math.radians(2), 0)
arm.pose.bones['hand_R'].rotation_euler     = (math.radians(2), math.radians(-4), math.radians(2))
arm.pose.bones['weapon'].rotation_euler     = (math.radians(-6), math.radians(6), math.radians(-2))

bpy.context.view_layer.update()

# Calculate exact Foregrip world position:
# SMG local foregrip is at (0, 0.2318, -0.0220)
fgrip_pos = smg.matrix_world @ Vector((0, 0.2318, -0.0220))
print('Foregrip world pos:', fgrip_pos)

# Now optimize left arm (upperarm_L, forearm_L, hand_L) to place hand_L right at fgrip_pos!
pb_u = arm.pose.bones['upperarm_L']
pb_f = arm.pose.bones['forearm_L']
pb_h = arm.pose.bones['hand_L']

best_dist = 1e9
best_angles = None

# Grid search for left arm
for u_rx in range(-10, 45, 5):
    for u_ry in range(-35, 15, 5):
        for u_rz in range(-20, 45, 5):
            for f_rx in range(-75, -20, 5):
                for f_ry in range(-25, 25, 10):
                    for f_rz in range(-35, 25, 10):
                        pb_u.rotation_euler = (math.radians(u_rx), math.radians(u_ry), math.radians(u_rz))
                        pb_f.rotation_euler = (math.radians(f_rx), math.radians(f_ry), math.radians(f_rz))
                        bpy.context.view_layer.update()
                        h_pos = (arm.matrix_world @ pb_h.matrix).to_translation()
                        d = (h_pos - fgrip_pos).length
                        if d < best_dist:
                            best_dist = d
                            best_angles = (u_rx, u_ry, u_rz, f_rx, f_ry, f_rz)

print(f'Initial search best dist: {best_dist*100:.2f} cm, angles: {best_angles}')

# Fine refine +- 4 deg
u_rx, u_ry, u_rz, f_rx, f_ry, f_rz = best_angles
for du_rx in range(-3, 4):
    for du_ry in range(-3, 4):
        for du_rz in range(-3, 4):
            for df_rx in range(-3, 4):
                pb_u.rotation_euler = (math.radians(u_rx + du_rx), math.radians(u_ry + du_ry), math.radians(u_rz + du_rz))
                pb_f.rotation_euler = (math.radians(f_rx + df_rx), math.radians(f_ry), math.radians(f_rz))
                bpy.context.view_layer.update()
                h_pos = (arm.matrix_world @ pb_h.matrix).to_translation()
                d = (h_pos - fgrip_pos).length
                if d < best_dist:
                    best_dist = d
                    best_angles = (u_rx + du_rx, u_ry + du_ry, u_rz + du_rz, f_rx + df_rx, f_ry, f_rz)

print(f'Refined best dist: {best_dist*100:.2f} cm, angles: {best_angles}')
u_rx, u_ry, u_rz, f_rx, f_ry, f_rz = best_angles
pb_u.rotation_euler = (math.radians(u_rx), math.radians(u_ry), math.radians(u_rz))
pb_f.rotation_euler = (math.radians(f_rx), math.radians(f_ry), math.radians(f_rz))
# hand_L rotation to wrap fingers around vertical grip
pb_h.rotation_euler = (math.radians(15), math.radians(-10), math.radians(35))
bpy.context.view_layer.update()

# Render FPS camera
cam = bpy.data.cameras.new('RenderCam')
cam.lens = 18
cam_obj = bpy.data.objects.new('RenderCam', cam)
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
out_img = r'C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2\test_fps_perfect_grip.png'
scene.render.filepath = out_img
bpy.ops.render.render(write_still=True)
print('Rendered to:', out_img)

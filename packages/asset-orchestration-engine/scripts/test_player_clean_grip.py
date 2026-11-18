"""test_player_clean_grip.py
Prueba postura con:
upperarm_R rotX negativo, rotZ negativo (hacia el pecho).
forearm_R rotX negativo (codo doblado adelante).
upperarm_L rotX negativo, rotZ positivo (hacia el pecho).
forearm_L rotX negativo (codo doblado adelante y arriba).
SMG parented a hand_R con orientacion horizontal hacia el frente (-Y).
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

# En hand_R:
# Para que el SMG apunte hacia el cañón (-Y mundo):
# Probemos rotaciones del SMG en hand_R:
smg.rotation_euler = (math.radians(-15.68), math.radians(-167.9), math.radians(-6.74))
smg.location = (0.0, 0.05, 0.01)

for pb in arm.pose.bones:
    pb.rotation_mode = 'XYZ'

# Torso y cabeza
pb_spine = arm.pose.bones['spine']
pb_chest = arm.pose.bones['chest']
pb_head = arm.pose.bones['head']

pb_spine.rotation_euler = (math.radians(4), 0, math.radians(-6))
pb_chest.rotation_euler = (math.radians(2), 0, math.radians(-4))
pb_head.rotation_euler = (math.radians(-2), 0, math.radians(6))

# Brazo derecho sosteniendo empuñadura trasera:
pb_cr = arm.pose.bones['clavicle_R']
pb_ur = arm.pose.bones['upperarm_R']
pb_fr = arm.pose.bones['forearm_R']
pb_hr = arm.pose.bones['hand_R']

pb_cr.rotation_euler = (math.radians(-2), 0, math.radians(-4))
pb_ur.rotation_euler = (math.radians(-48), math.radians(6), math.radians(-22))
pb_fr.rotation_euler = (math.radians(-65), math.radians(-10), math.radians(12))
pb_hr.rotation_euler = (math.radians(15), math.radians(-12), math.radians(-8))

# Brazo izquierdo alcanzando la empuñadura vertical:
pb_cl = arm.pose.bones['clavicle_L']
pb_ul = arm.pose.bones['upperarm_L']
pb_fl = arm.pose.bones['forearm_L']
pb_hl = arm.pose.bones['hand_L']

pb_cl.rotation_euler = (math.radians(-4), 0, math.radians(6))
pb_ul.rotation_euler = (math.radians(-54), math.radians(-12), math.radians(28))
pb_fl.rotation_euler = (math.radians(-75), math.radians(15), math.radians(-18))
pb_hl.rotation_euler = (math.radians(10), math.radians(15), math.radians(-20))

bpy.context.view_layer.update()

# Luces frontales
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
cam.location = (1.4, -2.4, 1.35)

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
out_img = r"E:\Darx_Proyect\Art\Blender\test_player_clean_grip.png"
scene.render.filepath = out_img
bpy.ops.render.render(write_still=True)
shutil.copyfile(out_img, r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2\test_player_clean_grip.png")
print("Rendered test_player_clean_grip.png")

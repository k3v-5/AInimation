"""test_player_arm_angles.py
Ajusta con precision los angulos de ambos brazos y la rotacion del SMG en SK_Player
para lograr el agarre perfecto a dos manos del Subfusil Tommy Gun.
"""
import bpy
import math
import shutil
from mathutils import Vector, Euler

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

bpy.ops.import_scene.fbx(filepath=r"E:\Darx_Proyect\Art\FBX\SK_Player.fbx")
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]

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

smg.parent = arm
smg.parent_type = 'BONE'
smg.parent_bone = 'hand_R'

# El arma debe apuntar horizontalmente hacia adelante (-Y mundo).
# En la prueba anterior, rotX = -90 apuntaba hacia arriba (+Z).
# Por tanto, rotX = 0 apuntará hacia adelante (-Y)!
smg.rotation_euler = (math.radians(0), math.radians(0), math.radians(0))
smg.location = (0.0, 0.08, 0.0)

for pb in arm.pose.bones:
    pb.rotation_mode = 'XYZ'

# Brazo derecho:
# upperarm_R rotX negativo levanta el brazo hacia adelante (-Y).
# forearm_R rotX positivo dobla el codo hacia adelante.
# rotZ acerca el brazo hacia el centro del pecho.
pb_ur = arm.pose.bones['upperarm_R']
pb_fr = arm.pose.bones['forearm_R']
pb_hr = arm.pose.bones['hand_R']

pb_ur.rotation_euler = (math.radians(-45), math.radians(10), math.radians(-25))
pb_fr.rotation_euler = (math.radians(55), math.radians(15), math.radians(-10))
pb_hr.rotation_euler = (math.radians(-10), math.radians(10), math.radians(0))

# Brazo izquierdo:
# upperarm_L rotX negativo levanta el brazo adelante (-Y).
# rotZ positivo cruza el brazo por delante del pecho hacia la derecha (+X).
# forearm_L rotX positivo dobla el antebrazo hacia arriba y hacia la empuñadura vertical.
pb_ul = arm.pose.bones['upperarm_L']
pb_fl = arm.pose.bones['forearm_L']
pb_hl = arm.pose.bones['hand_L']

pb_ul.rotation_euler = (math.radians(-50), math.radians(-15), math.radians(48))
pb_fl.rotation_euler = (math.radians(65), math.radians(10), math.radians(20))
pb_hl.rotation_euler = (math.radians(-15), math.radians(-10), math.radians(35))

bpy.context.view_layer.update()

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
l3.location = (-1.5, -1.0, 1.5)
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
out_img = r"E:\Darx_Proyect\Art\Blender\test_player_arm_angles.png"
scene.render.filepath = out_img
bpy.ops.render.render(write_still=True)
shutil.copyfile(out_img, r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2\test_player_arm_angles.png")
print("Rendered test_player_arm_angles.png")

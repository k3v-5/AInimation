"""test_player_front_camera.py
Verifica la vista frontal 3/4 de SK_Player colocando la camara en frente (-Y).
"""
import bpy
import math
import shutil
from mathutils import Vector, Euler

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# 1. Importar SK_Player
bpy.ops.import_scene.fbx(filepath=r"E:\Darx_Proyect\Art\FBX\SK_Player.fbx")
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
player_mesh = [o for o in bpy.data.objects if o.type == 'MESH'][0]

# 2. Cargar SMG
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

# En hand_R de SK_Player:
# hand_R en reposo cuelga al lado del cuerpo.
# Cuando el brazo se levanta hacia el frente (-Y):
# Vamos a ver la orientacion del arma:
smg.rotation_euler = (math.radians(-90), 0, 0)
smg.location = (0.0, 0.06, 0.02)

for pb in arm.pose.bones:
    pb.rotation_mode = 'XYZ'

# Brazo derecho levantado hacia adelante (-Y) sosteniendo la empuñadura trasera
pb_ur = arm.pose.bones['upperarm_R']
pb_fr = arm.pose.bones['forearm_R']
pb_hr = arm.pose.bones['hand_R']

# En SK_Player, para mover el brazo hacia el frente (-Y), rotX es NEGATIVO:
pb_ur.rotation_euler = (math.radians(-50), math.radians(8), math.radians(-18))
pb_fr.rotation_euler = (math.radians(-40), math.radians(-8), math.radians(-6))
pb_hr.rotation_euler = (math.radians(10), math.radians(10), math.radians(5))

# Brazo izquierdo alcanzando la empuñadura vertical delantera:
pb_ul = arm.pose.bones['upperarm_L']
pb_fl = arm.pose.bones['forearm_L']
pb_hl = arm.pose.bones['hand_L']

pb_ul.rotation_euler = (math.radians(-54), math.radians(-12), math.radians(30))
pb_fl.rotation_euler = (math.radians(-44), math.radians(14), math.radians(16))
pb_hl.rotation_euler = (math.radians(5), math.radians(20), math.radians(24))

bpy.context.view_layer.update()

# Luces frontales
l1 = bpy.data.objects.new("L1", bpy.data.lights.new("L1", 'SUN'))
l1.data.energy = 3.5
l1.rotation_euler = (0.8, 0.3, -0.6) # apuntando hacia +Y (hacia la cara del personaje)
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

# Cámara 3/4 FRONTAL (en -Y):
cam_data = bpy.data.cameras.new("Cam3P")
cam_data.lens = 42
cam = bpy.data.objects.new("Cam3P", cam_data)
cam.location = (1.5, -2.5, 1.35)

target = bpy.data.objects.new("CamTarget", None)
target.location = (0.05, -0.15, 1.2)
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
out_img = r"E:\Darx_Proyect\Art\Blender\test_player_front_camera.png"
scene.render.filepath = out_img
bpy.ops.render.render(write_still=True)
shutil.copyfile(out_img, r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2\test_player_front_camera.png")
print("Rendered test_player_front_camera.png")

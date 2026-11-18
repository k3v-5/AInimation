"""test_player_perfect_stance.py
Calibra la postura de combate de SK_Player con el SMG:
Brazo derecho sosteniendo la empuñadura trasera y gatillo,
Brazo izquierdo en la empuñadura delantera vertical,
Culata en el hombro con buffer seguro (cero clipping en torso).
"""
import bpy
import math
import shutil
from mathutils import Vector, Euler, Matrix

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
# El hueso apunta hacia abajo (+Y local va hacia los dedos).
# Para que el arma apunte hacia el frente (+Y mundo cuando la mano apunta al frente):
# Vamos a calibrar la rotacion local del arma en hand_R:
smg.rotation_euler = (math.radians(90), 0, math.radians(180))
smg.location = (0.0, 0.08, -0.02)

for pb in arm.pose.bones:
    pb.rotation_mode = 'XYZ'

# Postura de tiro táctica (Aim / Stance):
# Torso inclinado ligeramente adelante y perfilado hacia el objetivo
pb_pelvis = arm.pose.bones['pelvis']
pb_spine = arm.pose.bones['spine']
pb_chest = arm.pose.bones['chest']
pb_head = arm.pose.bones['head']

pb_spine.rotation_euler = (math.radians(-4), 0, math.radians(12))
pb_chest.rotation_euler = (math.radians(-2), 0, math.radians(8))
pb_head.rotation_euler = (math.radians(2), 0, math.radians(-15))

# Piernas en posición de guardia táctica
pb_th_r = arm.pose.bones['thigh_R']
pb_cf_r = arm.pose.bones['calf_R']
pb_th_l = arm.pose.bones['thigh_L']
pb_cf_l = arm.pose.bones['calf_L']

pb_th_r.rotation_euler = (math.radians(14), 0, math.radians(-4))  # pierna derecha atrás
pb_cf_r.rotation_euler = (math.radians(16), 0, 0)
pb_th_l.rotation_euler = (math.radians(-16), 0, math.radians(4))  # pierna izquierda adelante
pb_cf_l.rotation_euler = (math.radians(8), 0, 0)

# Brazo derecho levantando el arma al hombro
pb_c_r = arm.pose.bones['clavicle_R']
pb_u_r = arm.pose.bones['upperarm_R']
pb_f_r = arm.pose.bones['forearm_R']
pb_h_r = arm.pose.bones['hand_R']

pb_c_r.rotation_euler = (math.radians(-2), 0, math.radians(-6))
pb_u_r.rotation_euler = (math.radians(-52), math.radians(8), math.radians(-28))
pb_f_r.rotation_euler = (math.radians(-42), math.radians(-12), math.radians(-8))
pb_h_r.rotation_euler = (math.radians(12), math.radians(-16), math.radians(10))

# Brazo izquierdo sosteniendo la empuñadura delantera vertical
pb_c_l = arm.pose.bones['clavicle_L']
pb_u_l = arm.pose.bones['upperarm_L']
pb_f_l = arm.pose.bones['forearm_L']
pb_h_l = arm.pose.bones['hand_L']

pb_c_l.rotation_euler = (math.radians(-4), 0, math.radians(10))
pb_u_l.rotation_euler = (math.radians(-58), math.radians(-14), math.radians(34))
pb_f_l.rotation_euler = (math.radians(-38), math.radians(16), math.radians(12))
pb_h_l.rotation_euler = (math.radians(-14), math.radians(12), math.radians(20))

bpy.context.view_layer.update()

# Luces frontales y 3/4
l1 = bpy.data.objects.new("L1", bpy.data.lights.new("L1", 'SUN'))
l1.data.energy = 3.5
l1.rotation_euler = (0.7, -0.4, 0.5) # luz frontal iluminando al personaje
scene.collection.objects.link(l1)

l2 = bpy.data.objects.new("L2", bpy.data.lights.new("L2", 'AREA'))
l2.data.energy = 500.0
l2.data.size = 2.5
l2.location = (1.5, 2.0, 1.6)
scene.collection.objects.link(l2)

l3 = bpy.data.objects.new("L3", bpy.data.lights.new("L3", 'AREA'))
l3.data.energy = 350.0
l3.data.size = 2.0
l3.data.color = (0.75, 0.2, 1.0)
l3.location = (-1.5, -1.0, 1.5)
scene.collection.objects.link(l3)

# Cámara 3/4 frontal mostrando cuerpo entero y el arma
cam_data = bpy.data.cameras.new("Cam3P")
cam_data.lens = 45
cam = bpy.data.objects.new("Cam3P", cam_data)
# Jugador está en (0, 0, 0), mira a +Y.
# Cámara en frente a la derecha (+X, +Y):
cam.location = (1.6, 2.6, 1.35)

target = bpy.data.objects.new("CamTarget", None)
target.location = (0.05, 0.2, 1.2)
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
out_img = r"E:\Darx_Proyect\Art\Blender\test_player_perfect_stance.png"
scene.render.filepath = out_img
bpy.ops.render.render(write_still=True)
shutil.copyfile(out_img, r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2\test_player_perfect_stance.png")
print("Rendered test_player_perfect_stance.png")

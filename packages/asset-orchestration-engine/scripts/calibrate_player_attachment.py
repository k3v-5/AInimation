"""calibrate_player_attachment.py
Encuentra la orientacion y offset exacto del arma en hand_R de SK_Player
para que encaje naturalmente en la palma, apuntando al frente, y calcule
la posicion exacta para que la mano izquierda agarre la empuñadura delantera.
"""
import bpy
import math
import shutil
from mathutils import Vector, Euler, Matrix

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

# En SK_Player, el jugador mira hacia +Y en reposo.
# La mano derecha (hand_R) en reposo cuelga al lado del cuerpo.
# Si el brazo derecho se levanta para apuntar al frente (+Y):
# Vamos a rotar los huesos de los brazos para poner al personaje en postura de tiro:
pb_spine = arm.pose.bones['spine']
pb_chest = arm.pose.bones['chest']
pb_r_clav = arm.pose.bones['clavicle_R']
pb_r_up = arm.pose.bones['upperarm_R']
pb_r_fore = arm.pose.bones['forearm_R']
pb_r_hand = arm.pose.bones['hand_R']

pb_l_clav = arm.pose.bones['clavicle_L']
pb_l_up = arm.pose.bones['upperarm_L']
pb_l_fore = arm.pose.bones['forearm_L']
pb_l_hand = arm.pose.bones['hand_L']

for pb in (pb_spine, pb_chest, pb_r_clav, pb_r_up, pb_r_fore, pb_r_hand, pb_l_clav, pb_l_up, pb_l_fore, pb_l_hand):
    pb.rotation_mode = 'XYZ'

# En reposo, arm_player tiene:
# upperarm_R rotX positivo levanta el brazo hacia +Y (frente)
# forearm_R rotX positivo dobla el codo hacia adelante
# Probemos rotaciones naturales para sostener un subfusil:
pb_r_up.rotation_euler = (math.radians(70), math.radians(0), math.radians(15))
pb_r_fore.rotation_euler = (math.radians(45), math.radians(0), math.radians(10))
pb_r_hand.rotation_euler = (math.radians(-25), math.radians(0), math.radians(0))

# Attach SMG to hand_R
smg.parent = arm
smg.parent_type = 'BONE'
smg.parent_bone = 'hand_R'

# La empuñadura trasera del SMG en local está en (0, 0.008, 0.012).
# Orientar el SMG relativo a hand_R:
# Para que el cañón apunte hacia adelante cuando la mano está en esa pose:
smg.rotation_euler = (math.radians(-90), math.radians(0), math.radians(0))
smg.location = (0.0, 0.12, 0.03)

bpy.context.view_layer.update()

# Ver en qué posición del mundo queda la empuñadura delantera (foregrip)
p_foregrip_world = smg.matrix_world @ Vector((0, 0.24, -0.06))
print(f"Target foregrip in world: {p_foregrip_world}")
print(f"hand_R in world: {arm.matrix_world @ pb_r_hand.matrix.translation}")

# Ajustar brazo izquierdo para que hand_L alcance p_foregrip_world:
# Posicion de hand_L en reposo es (-0.228, -0.115, 0.955)
# p_foregrip_world estará aproximadamente en (X ~ 0.10, Y ~ 0.45, Z ~ 1.25)
# Entonces el brazo izquierdo debe rotar hacia adelante (+Y) y hacia adentro (+X):
pb_l_up.rotation_euler = (math.radians(65), math.radians(-20), math.radians(-35))
pb_l_fore.rotation_euler = (math.radians(60), math.radians(10), math.radians(20))
pb_l_hand.rotation_euler = (math.radians(10), math.radians(0), math.radians(25))

bpy.context.view_layer.update()
print(f"hand_L in world: {arm.matrix_world @ pb_l_hand.matrix.translation}")

# Luz
l_data = bpy.data.lights.new("Sun", 'SUN')
l_data.energy = 4.0
l = bpy.data.objects.new("Sun", l_data)
l.rotation_euler = (0.8, -0.5, 0.3)
scene.collection.objects.link(l)

# Camara
cam_data = bpy.data.cameras.new("Cam3P")
cam_data.lens = 50
cam = bpy.data.objects.new("Cam3P", cam_data)
cam.location = (1.5, 1.8, 1.3)
# Apuntar al pecho/arma
target = bpy.data.objects.new("Target", None)
target.location = (0.05, 0.25, 1.25)
scene.collection.objects.link(target)

c_tr = cam.constraints.new('TRACK_TO')
c_tr.target = target
c_tr.track_axis = 'TRACK_NEGATIVE_Z'
c_tr.up_axis = 'UP_Y'
scene.collection.objects.link(cam)
scene.camera = cam

scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 960
scene.render.resolution_y = 540
out_img = r"E:\Darx_Proyect\Art\Blender\test_player_calibration.png"
scene.render.filepath = out_img
bpy.ops.render.render(write_still=True)
shutil.copyfile(out_img, r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2\test_player_calibration.png")
print("Rendered test_player_calibration.png")

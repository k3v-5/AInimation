import bpy
import math
from mathutils import Vector, Euler, Matrix

BLEND_FILE = "f:/Dev/Game/Art/Blender/SK_Firefighter_Official_Rigged.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND_FILE)

arm_obj = bpy.data.objects.get("SK_Firefighter_Armature")
gun_obj = bpy.data.objects.get("SM_ExtinguisherCannon")

def R(deg):
    return math.radians(deg)

# Posicion y rotacion del cañon en espacio de mundo:
# Sostenido al costado derecho a la altura de la cintura/pecho
gun_pos = Vector((-0.07, -0.32, 0.82))
# En Blender: -X local es el cañon. Si Z rot = +90, -X va a -Y (al frente)
# Pitch leve: R(-4)
gun_rot = Euler((R(-4), 0, R(90)))
gun_obj.location = gun_pos
gun_obj.rotation_euler = gun_rot
bpy.context.view_layer.update()

gun_mat = gun_obj.matrix_world
grip_r_world = gun_mat @ Vector((0.17, 0, -0.14))   # Empuñadura trasera
grip_l_world = gun_mat @ Vector((-0.11, 0, -0.13))  # Empuñadura delantera

print("=" * 60)
print(f"Grip R Target: {grip_r_world}")
print(f"Grip L Target: {grip_l_world}")

bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='POSE')
pb = arm_obj.pose.bones

# 1. Reset
for b in pb:
    b.rotation_euler = Euler((0, 0, 0))
    b.location = Vector((0, 0, 0))

# Postura base erguida
pb['pelvis'].rotation_euler = Euler((R(2), 0.0, 0.0))
pb['spine_01'].rotation_euler = Euler((R(3), 0.0, 0.0))
pb['spine_02'].rotation_euler = Euler((R(2), 0.0, 0.0))

# Piernas firmes
pb['thigh_l'].rotation_euler = Euler((R(2), 0.0, R(1)))
pb['calf_l'].rotation_euler = Euler((R(6), 0.0, 0.0))
pb['foot_l'].rotation_euler = Euler((R(-6), 0.0, 0.0))
pb['thigh_r'].rotation_euler = Euler((R(2), 0.0, R(-1)))
pb['calf_r'].rotation_euler = Euler((R(6), 0.0, 0.0))
pb['foot_r'].rotation_euler = Euler((R(-6), 0.0, 0.0))

# BRAZO DERECHO:
# Para llevar la mano derecha a (-0.07, -0.15, 0.72):
# El hombro está en (-0.28, 0.01, 1.14)
# Clavicle_r: flexiona ligeramente hacia adelante
pb['clavicle_r'].rotation_euler = Euler((R(-5), 0, R(-3)))
# Upperarm_r: rotar hacia adelante (-X en Blender = hacia -Y adelante)
# y aducir hacia adentro (hacia el pecho, +Z en brazo derecho)
pb['upperarm_r'].rotation_euler = Euler((R(-35), R(-15), R(35)))
# Lowerarm_r: flexionar codo (-Z flexiona hacia adelante/adentro)
pb['lowerarm_r'].rotation_euler = Euler((R(10), R(15), R(-75)))
# Hand_r: mano empuñando la culata/gatillo
pb['hand_r'].rotation_euler = Euler((R(15), R(20), R(-15)))

# BRAZO IZQUIERDO:
# Para llevar la mano izquierda a (-0.07, -0.43, 0.74):
# El hombro izquierdo está en (+0.28, 0.01, 1.14)
# Debe alcanzar cruzando el pecho hacia la derecha y adelante!
pb['clavicle_l'].rotation_euler = Euler((R(-8), 0, R(5)))
# Upperarm_l: adelante (-X) y adentro hacia la derecha (-Z cruza el pecho)
pb['upperarm_l'].rotation_euler = Euler((R(-55), R(15), R(-40)))
# Lowerarm_l: flexionar codo (+Z flexiona el codo izquierdo)
pb['lowerarm_l'].rotation_euler = Euler((R(-10), R(-15), R(55)))
# Hand_l: mano sosteniendo el cañón por debajo
pb['hand_l'].rotation_euler = Euler((R(-10), R(-15), R(25)))

bpy.context.view_layer.update()

loc_r = (arm_obj.matrix_world @ pb['hand_r'].matrix).to_translation()
loc_l = (arm_obj.matrix_world @ pb['hand_l'].matrix).to_translation()
print(f"hand_r: {loc_r} | Dist R: {(loc_r - grip_r_world).length:.4f}m")
print(f"hand_l: {loc_l} | Dist L: {(loc_l - grip_l_world).length:.4f}m")

# Colocar weapon_socket_r exactamente en la mano derecha con orientacion del arma
# En Blender pose bone weapon_socket_r:
# pb['weapon_socket_r']
sock_loc = (arm_obj.matrix_world @ pb['weapon_socket_r'].matrix).to_translation()
print(f"weapon_socket_r world loc: {sock_loc}")

# Renderizar cámara frontal diagonal 3/4
cam_data = bpy.data.cameras.new("GripCam")
cam_obj = bpy.data.objects.new("GripCam", cam_data)
bpy.context.scene.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj

cam_obj.location = Vector((1.4, -2.1, 1.05))
cam_dir = Vector((-0.05, -0.25, 0.80)) - cam_obj.location
rot_quat = cam_dir.to_track_quat('-Z', 'Y')
cam_obj.rotation_euler = rot_quat.to_euler()

bpy.context.scene.render.resolution_x = 960
bpy.context.scene.render.resolution_y = 720
bpy.context.scene.render.filepath = "C:/Users/sasuk/.gemini/antigravity/brain/b59ff04f-3c21-4ee5-94b0-8e8f899f8923/Verify_Blender_Weapon_Grip_Test3.png"
bpy.ops.render.render(write_still=True)
print(f"Render 3 guardado en {bpy.context.scene.render.filepath}")

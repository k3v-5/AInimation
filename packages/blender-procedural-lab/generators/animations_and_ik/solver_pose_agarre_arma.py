import bpy
import math
from mathutils import Vector, Euler, Matrix
import os

BLEND_FILE = "f:/Dev/Game/Art/Blender/SK_Firefighter_Official_Rigged.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND_FILE)

arm_obj = bpy.data.objects.get("SK_Firefighter_Armature")
char_obj = bpy.data.objects.get("SK_Firefighter_Official")
gun_obj = bpy.data.objects.get("SM_ExtinguisherCannon")

def R(deg):
    return math.radians(deg)

# 1. Colocar el cañón en la posición táctica ideal frente al pecho del bombero
# En Blender: Z es arriba, -Y es adelante, +X es izquierda del bombero (-X es derecha del bombero)
# Bombero centro pecho está en (0, 0, 1.05)
# El cañón debe estar ligeramente a la derecha del centro: X = -0.12, Y = -0.32 (adelante), Z = 0.88
# Y debe apuntar hacia adelante (-Y).
# Como en el cañón el cañón/boquilla va hacia -X local:
# Si rotamos Z = -90° (R(-90)):
#   -X local rota hacia +Y local de Blender (atrás) o -Y?
#   Vector(-1, 0, 0) rotado por Z = -90°:
#   x' = -1 * cos(-90) - 0 = 0
#   y' = -1 * sin(-90) = -1 * (-1) = +1 (atrás)
#   Vector(-1, 0, 0) rotado por Z = +90°:
#   x' = 0
#   y' = -1 * sin(90) = -1 (ADELANTE!)
# Por tanto, una rotación de Z = +90° en el cañón hace que el cañón apunte hacia ADELANTE (-Y)!

gun_pos = Vector((-0.10, -0.32, 0.88))
# Leve inclinación táctica: apuntando ligeramente hacia arriba/frente (Pitch ~ -5°)
gun_rot = Euler((R(-4), 0, R(90)))

gun_obj.location = gun_pos
gun_obj.rotation_euler = gun_rot
bpy.context.view_layer.update()

# Matriz del arma en mundo
gun_matrix = gun_obj.matrix_world

# Posiciones de los agarres en mundo:
# Empuñadura trasera en local: (0.17, 0, -0.14)
# Empuñadura delantera en local: (-0.11, 0, -0.13)
rear_grip_local = Vector((0.17, 0, -0.14))
front_grip_local = Vector((-0.11, 0, -0.13))

rear_grip_world = gun_matrix @ rear_grip_local
front_grip_world = gun_matrix @ front_grip_local

print(f"Punto Agarre Trasero (Mano Derecha): {rear_grip_world}")
print(f"Punto Agarre Delantero (Mano Izquierda): {front_grip_world}")

# 2. Configurar la pose del bombero para alcanzar exactamente estos puntos
bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='POSE')
pb = arm_obj.pose.bones

# Reset
for b in pb:
    b.rotation_euler = Euler((0, 0, 0))
    b.location = Vector((0, 0, 0))

# Postura base erguida
pb['pelvis'].rotation_euler = Euler((R(2), 0.0, 0.0))
pb['spine_01'].rotation_euler = Euler((R(3), 0.0, 0.0))
pb['spine_02'].rotation_euler = Euler((R(2), 0.0, 0.0))

# Ahora buscamos las rotaciones de brazos que lleven hand_r a rear_grip_world y hand_l a front_grip_world
# Brazo derecho:
# Queremos que la mano derecha esté en rear_grip_world: (-0.10, -0.15, 0.74) aprox
# Clavicle_r: ligera flexión hacia adelante
pb['clavicle_r'].rotation_euler = Euler((R(-5), 0, R(-4)))
# Upperarm_r: hacia adelante y convergiendo hacia el pecho
pb['upperarm_r'].rotation_euler = Euler((R(-42), R(-12), R(38)))
# Lowerarm_r: codo flexionado hacia adelante/adentro
pb['lowerarm_r'].rotation_euler = Euler((R(-18), R(24), R(-58)))
# Hand_r: orientada a la empuñadura
pb['hand_r'].rotation_euler = Euler((R(12), R(15), R(-20)))

# Brazo izquierdo (mano adelantada que sostiene el cañón frontal):
# Clavicle_l:
pb['clavicle_l'].rotation_euler = Euler((R(-8), 0, R(6)))
# Upperarm_l: extendido hacia adelante y cruzando hacia la derecha
pb['upperarm_l'].rotation_euler = Euler((R(-48), R(15), R(-44)))
# Lowerarm_l: antebrazo flexionado sosteniendo el guardamanos
pb['lowerarm_l'].rotation_euler = Euler((R(-15), R(-20), R(62)))
# Hand_l:
pb['hand_l'].rotation_euler = Euler((R(10), R(-15), R(25)))

bpy.context.view_layer.update()

hand_r_world = (arm_obj.matrix_world @ pb['hand_r'].matrix).to_translation()
hand_l_world = (arm_obj.matrix_world @ pb['hand_l'].matrix).to_translation()

print(f"hand_r World: {hand_r_world} | Dist a Grip Trasero: {(hand_r_world - rear_grip_world).length:.4f}m")
print(f"hand_l World: {hand_l_world} | Dist a Grip Delantero: {(hand_l_world - front_grip_world).length:.4f}m")

# Render de comprobación visual
cam_data = bpy.data.cameras.new("TestCam")
cam_obj = bpy.data.objects.new("TestCam", cam_data)
bpy.context.scene.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj

# Vista diagonal 3/4 frontal
cam_obj.location = Vector((1.8, -2.4, 1.2))
cam_dir = Vector((-0.05, -0.2, 0.85)) - cam_obj.location
rot_quat = cam_dir.to_track_quat('-Z', 'Y')
cam_obj.rotation_euler = rot_quat.to_euler()

# Configurar render
bpy.context.scene.render.resolution_x = 960
bpy.context.scene.render.resolution_y = 720
bpy.context.scene.render.filepath = "C:/Users/sasuk/.gemini/antigravity/brain/b59ff04f-3c21-4ee5-94b0-8e8f899f8923/Verify_Blender_Weapon_Grip_Test1.png"
bpy.ops.render.render(write_still=True)
print(f"Render guardado en {bpy.context.scene.render.filepath}")

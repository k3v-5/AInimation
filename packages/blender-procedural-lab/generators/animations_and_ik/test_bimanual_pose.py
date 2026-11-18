import bpy
import math
from mathutils import Vector, Euler, Matrix

def R(deg):
    return math.radians(deg)

BLEND_FILE = "f:/Dev/Game/Art/Blender/SK_Firefighter_Official_Rigged.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND_FILE)

arm_obj = bpy.data.objects.get("SK_Firefighter_Armature")
gun_obj = bpy.data.objects.get("SM_ExtinguisherCannon")

# Ubicacion y rotacion del cañón en espacio de mundo en Blender:
# En Blender: el personaje mira hacia -Y (+Y es espalda, +Z arriba, +X izquierda del personaje, -X derecha del personaje)
# En SM_ExtinguisherCannon: -X es el cañón, +X es la culata, -Z son las empuñaduras, +Z es el riel superior.
# Para que el cañón apunte al frente (-Y):
# Rotación en Z debe ser +90°:
# -X rotado +90° en Z va a -Y (frente)!
# +X rotado +90° en Z va a +Y (espalda/culata)!
# -Z (empuñaduras) queda apuntando hacia abajo (-Z)!
# +Z (riel superior) queda apuntando hacia arriba (+Z)!
# Esto es PERFECTO.

# Posicion del cañon en espacio de mundo:
# Ligeramente a la derecha del centro del cuerpo (X = -0.06)
# Al frente del torso a la altura de la cintura/pecho bajo (Y = -0.30, Z = 0.88)
gun_pos = Vector((-0.06, -0.32, 0.86))
gun_rot = Euler((0.0, 0.0, R(90))) # Apuntando recto hacia el frente (-Y)

gun_obj.location = gun_pos
gun_obj.rotation_euler = gun_rot
bpy.context.view_layer.update()

gun_mat = gun_obj.matrix_world
grip_r_world = gun_mat @ Vector((0.17, 0, -0.14))   # Empuñadura trasera
grip_l_world = gun_mat @ Vector((-0.11, 0, -0.13))  # Empuñadura delantera

print("=" * 60)
print(f"Grip R Target (Rear Handle / hand_r): {grip_r_world}")
print(f"Grip L Target (Front Handle / hand_l): {grip_l_world}")

bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='POSE')
pb = arm_obj.pose.bones

# Reset
for b in pb:
    b.rotation_euler = Euler((0, 0, 0))
    b.location = Vector((0, 0, 0))

# Postura base erguida y estable
pb['pelvis'].location = Vector((0.0, -0.01, 0.0))
pb['pelvis'].rotation_euler = Euler((R(2), 0.0, 0.0))
pb['thigh_l'].rotation_euler = Euler((R(2), 0.0, R(1)))
pb['calf_l'].rotation_euler = Euler((R(6), 0.0, 0.0))
pb['foot_l'].rotation_euler = Euler((R(-6), 0.0, 0.0))
pb['thigh_r'].rotation_euler = Euler((R(2), 0.0, R(-1)))
pb['calf_r'].rotation_euler = Euler((R(6), 0.0, 0.0))
pb['foot_r'].rotation_euler = Euler((R(-6), 0.0, 0.0))
pb['spine_01'].rotation_euler = Euler((R(3), 0.0, 0.0))
pb['spine_02'].rotation_euler = Euler((R(2), 0.0, 0.0))
pb['neck_01'].rotation_euler = Euler((R(-2), 0.0, 0.0))
pb['head'].rotation_euler = Euler((R(-2), 0.0, 0.0))

# Ahora rotamos clavículas y brazos para que las manos lleguen con precisión natural a las empuñaduras
bpy.context.view_layer.update()

# Imprimir coordenadas de referencia
print("Bones base pose:")
for bname in ['clavicle_r', 'upperarm_r', 'lowerarm_r', 'hand_r', 'clavicle_l', 'upperarm_l', 'lowerarm_l', 'hand_l']:
    loc = (arm_obj.matrix_world @ pb[bname].matrix).to_translation()
    print(f"  {bname}: {loc}")

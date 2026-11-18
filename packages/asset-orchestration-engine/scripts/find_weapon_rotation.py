"""find_weapon_rotation.py
Encuentra la rotacion exacta en hand_R para que el cañón apunte hacia -Y (frente)
y la parte superior del arma apunte hacia +Z (arriba).
"""
import bpy
import math
from mathutils import Vector, Euler, Matrix

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=r"E:\Darx_Proyect\Art\FBX\SK_Player.fbx")
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]

# Poner brazo derecho en postura de tiro
for pb in arm.pose.bones:
    pb.rotation_mode = 'XYZ'

pb_ur = arm.pose.bones['upperarm_R']
pb_fr = arm.pose.bones['forearm_R']
pb_hr = arm.pose.bones['hand_R']

pb_ur.rotation_euler = (math.radians(-48), math.radians(6), math.radians(-22))
pb_fr.rotation_euler = (math.radians(-65), math.radians(-10), math.radians(12))
pb_hr.rotation_euler = (math.radians(15), math.radians(-12), math.radians(-8))

bpy.context.view_layer.update()

# Matrix mundial de hand_R
m_hr = arm.matrix_world @ pb_hr.matrix

# En el SMG:
# El cañón apunta a +Y local, y arriba es +Z local.
# Queremos que en el mundo:
# Cañón apunte a -Y mundo: Vector((0, -1, 0))
# Arriba apunte a +Z mundo: Vector((0, 0, 1))
# Por tanto, la matriz de orientación deseada del arma en el mundo es:
# X = (1, 0, 0)
# Y = (0, -1, 0)
# Z = (0, 0, 1)  (con X = Y cross Z = (0, -1, 0) x (0, 0, 1) = (-1, 0, 0))
# Así que:
# R_world_desired = Matrix([[-1, 0, 0], [0, -1, 0], [0, 0, 1]])
R_desired = Matrix((
    (-1,  0, 0),
    ( 0, -1, 0),
    ( 0,  0, 1)
))

# Si SMG es hijo de hand_R:
# R_world = R_hr @ R_local
# => R_local = R_hr.inverted() @ R_desired
R_hr = m_hr.to_3x3()
R_local = R_hr.inverted() @ R_desired

euler_local = R_local.to_euler('XYZ')
print("Rotacion local exacta para el SMG en hand_R:")
print(f"  deg: {[round(math.degrees(a), 2) for a in euler_local]}")

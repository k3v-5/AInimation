"""test_player_arm_sweep.py
Encuentra los angulos exactos de upperarm_R, forearm_R, upperarm_L, forearm_L
mediante barrido analítico para que las manos coincidan exactamente con las empuñaduras.
"""
import bpy
import math
from mathutils import Vector, Matrix

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=r"E:\Darx_Proyect\Art\FBX\SK_Player.fbx")
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]

for pb in arm.pose.bones:
    pb.rotation_mode = 'XYZ'

# En la postura de disparo ideal:
# El hombro derecho está en (0.228, -0.01, 1.52).
# La mano derecha (hand_R) debe estar en el costado derecho del pecho:
# X ~ 0.18, Y ~ -0.22, Z ~ 1.25.
# El hombro izquierdo está en (-0.228, -0.01, 1.52).
# La mano izquierda (hand_L) debe estar en el mango delantero:
# X ~ 0.16, Y ~ -0.45, Z ~ 1.18.

# Probemos distintas rotaciones de upperarm y forearm y midamos la distancia al objetivo:
target_hand_R = Vector((0.18, -0.22, 1.25))
target_hand_L = Vector((0.16, -0.45, 1.18))

best_dist_r = 1e9
best_rot_r = None

pb_ur = arm.pose.bones['upperarm_R']
pb_fr = arm.pose.bones['forearm_R']
pb_hr = arm.pose.bones['hand_R']

# Barrido de rotaciones para brazo derecho
for ur_x in range(-60, 0, 5):
    for ur_z in range(-50, 20, 5):
        for fr_x in range(-90, -20, 5):
            pb_ur.rotation_euler = (math.radians(ur_x), 0, math.radians(ur_z))
            pb_fr.rotation_euler = (math.radians(fr_x), 0, 0)
            bpy.context.view_layer.update()
            pos_hr = arm.matrix_world @ pb_hr.head
            dist = (pos_hr - target_hand_R).length
            if dist < best_dist_r:
                best_dist_r = dist
                best_rot_r = (ur_x, ur_z, fr_x, pos_hr)

print(f"Mejor postura brazo derecho (hand_R):")
print(f"  upperarm_R rotX={best_rot_r[0]}, rotZ={best_rot_r[1]}")
print(f"  forearm_R rotX={best_rot_r[2]}")
print(f"  pos={best_rot_r[3]}, dist={best_dist_r:.4f} m")

# Barrido de rotaciones para brazo izquierdo
best_dist_l = 1e9
best_rot_l = None

pb_ul = arm.pose.bones['upperarm_L']
pb_fl = arm.pose.bones['forearm_L']
pb_hl = arm.pose.bones['hand_L']

for ul_x in range(-70, -10, 5):
    for ul_z in range(0, 70, 5):
        for fl_x in range(-90, -10, 5):
            pb_ul.rotation_euler = (math.radians(ul_x), 0, math.radians(ul_z))
            pb_fl.rotation_euler = (math.radians(fl_x), 0, 0)
            bpy.context.view_layer.update()
            pos_hl = arm.matrix_world @ pb_hl.head
            dist = (pos_hl - target_hand_L).length
            if dist < best_dist_l:
                best_dist_l = dist
                best_rot_l = (ul_x, ul_z, fl_x, pos_hl)

print(f"Mejor postura brazo izquierdo (hand_L):")
print(f"  upperarm_L rotX={best_rot_l[0]}, rotZ={best_rot_l[1]}")
print(f"  forearm_L rotX={best_rot_l[2]}")
print(f"  pos={best_rot_l[3]}, dist={best_dist_l:.4f} m")

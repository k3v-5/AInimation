# -*- coding: utf-8 -*-
import bpy
import math
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=r"E:\Darx_Proyect\Art\FBX\SK_FPS_Arms.fbx")
arm = bpy.data.objects['ARM_FPS_Arms']

for pb in arm.pose.bones:
    pb.rotation_mode = 'XYZ'
    pb.rotation_euler = (0, 0, 0)
    pb.location = (0, 0, 0)

pb_uR = arm.pose.bones['upperarm_R']
pb_fR = arm.pose.bones['forearm_R']
pb_hR = arm.pose.bones['hand_R']

pb_uL = arm.pose.bones['upperarm_L']
pb_fL = arm.pose.bones['forearm_L']
pb_hL = arm.pose.bones['hand_L']

print("\n--- TESTEANDO ANGULOS ELEVADOS ---")

# Vamos a probar combinaciones de rotacion para elevar el brazo derecho al centro de la camara
best_dist = 999.0
best_r = None

target_pos_R = Vector((0.05, -0.45, -0.08)) # Posicion ideal para puño / arma en pantalla

for ux in range(-90, 40, 10):
    for uy in range(-90, 40, 10):
        for uz in range(-90, 40, 10):
            pb_uR.rotation_euler = (math.radians(ux), math.radians(uy), math.radians(uz))
            for fx in range(-90, 90, 15):
                pb_fR.rotation_euler = (math.radians(fx), 0, 0)
                bpy.context.view_layer.update()
                hr = arm.matrix_world @ pb_hR.matrix.translation
                d = (hr - target_pos_R).length
                if d < best_dist:
                    best_dist = d
                    best_r = (ux, uy, uz, fx, hr.copy())

print(f"Mejor aproximacion Brazo R (dist={best_dist:.3f}):")
print(f"  upperarm_R: ({best_r[0]}, {best_r[1]}, {best_r[2]}), forearm_R: ({best_r[3]}, 0, 0)")
print(f"  hand_R pos: ({best_r[4].x:.3f}, {best_r[4].y:.3f}, {best_r[4].z:.3f})")
v_angle = math.degrees(math.atan2(best_r[4].z, -best_r[4].y))
h_angle = math.degrees(math.atan2(best_r[4].x, -best_r[4].y))
print(f"  Angulo de camara: vertical={v_angle:.1f} deg, horiz={h_angle:.1f} deg")

# Ahora para la mano izquierda (alcanzando la recámara o guardia)
target_pos_L = Vector((-0.08, -0.35, -0.10))
best_dist_L = 999.0
best_l = None

for ux in range(-90, 60, 10):
    for uy in range(-90, 60, 10):
        for uz in range(-90, 60, 10):
            pb_uL.rotation_euler = (math.radians(ux), math.radians(uy), math.radians(uz))
            for fx in range(-90, 90, 15):
                pb_fL.rotation_euler = (math.radians(fx), 0, 0)
                bpy.context.view_layer.update()
                hl = arm.matrix_world @ pb_hL.matrix.translation
                d = (hl - target_pos_L).length
                if d < best_dist_L:
                    best_dist_L = d
                    best_l = (ux, uy, uz, fx, hl.copy())

print(f"\nMejor aproximacion Brazo L (dist={best_dist_L:.3f}):")
print(f"  upperarm_L: ({best_l[0]}, {best_l[1]}, {best_l[2]}), forearm_L: ({best_l[3]}, 0, 0)")
print(f"  hand_L pos: ({best_l[4].x:.3f}, {best_l[4].y:.3f}, {best_l[4].z:.3f})")
v_angle_l = math.degrees(math.atan2(best_l[4].z, -best_l[4].y))
h_angle_l = math.degrees(math.atan2(best_l[4].x, -best_l[4].y))
print(f"  Angulo de camara: vertical={v_angle_l:.1f} deg, horiz={h_angle_l:.1f} deg")

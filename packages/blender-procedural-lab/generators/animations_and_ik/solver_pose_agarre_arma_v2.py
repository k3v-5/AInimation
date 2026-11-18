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

# Colocación ergonómica natural del arma pegada al cuerpo:
# El bombero la sostiene al costado derecho/pecho:
# Posición del arma:
gun_pos = Vector((-0.08, -0.28, 0.84))
gun_rot = Euler((R(-2), 0, R(90)))

gun_obj.location = gun_pos
gun_obj.rotation_euler = gun_rot
bpy.context.view_layer.update()

gun_matrix = gun_obj.matrix_world
rear_grip_local = Vector((0.17, 0, -0.14))
front_grip_local = Vector((-0.11, 0, -0.13))

target_r = gun_matrix @ rear_grip_local
target_l = gun_matrix @ front_grip_local

print(f"Target Right Grip (Rear): {target_r}")
print(f"Target Left Grip (Front): {target_l}")

bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='POSE')
pb = arm_obj.pose.bones

# Postura base erguida
pb['pelvis'].rotation_euler = Euler((R(2), 0.0, 0.0))
pb['spine_01'].rotation_euler = Euler((R(3), 0.0, 0.0))
pb['spine_02'].rotation_euler = Euler((R(2), 0.0, 0.0))

# Optimizador por gradiente descendente / grid search para Right Arm
# Variables: upperarm_r (rx, ry, rz), lowerarm_r (rx, ry, rz)
best_dist_r = 999.0
best_angles_r = None

# Grid search refinado para brazo derecho
for ur_x in range(-80, -20, 5):      # adelante
    for ur_y in range(-40, 40, 8):
        for ur_z in range(-40, 60, 8):    # adentro hacia el pecho
            for lr_z in range(-120, -20, 8):  # flexión de codo
                for lr_x in range(-40, 40, 10):
                    pb['upperarm_r'].rotation_euler = Euler((R(ur_x), R(ur_y), R(ur_z)))
                    pb['lowerarm_r'].rotation_euler = Euler((R(lr_x), 0, R(lr_z)))
                    bpy.context.view_layer.update()
                    loc = (arm_obj.matrix_world @ pb['hand_r'].matrix).to_translation()
                    d = (loc - target_r).length
                    if d < best_dist_r:
                        best_dist_r = d
                        best_angles_r = (ur_x, ur_y, ur_z, lr_x, lr_z)

print(f"Mejor Brazo Derecho: dist={best_dist_r:.4f}m con angles={best_angles_r}")

# Grid search para brazo izquierdo
best_dist_l = 999.0
best_angles_l = None

for ul_x in range(-90, -30, 5):      # adelante
    for ul_y in range(-40, 40, 8):
        for ul_z in range(-70, 30, 8):    # adentro cruzando hacia el arma
            for ll_z in range(20, 130, 8):    # flexión de codo izquierdo
                for ll_x in range(-40, 40, 10):
                    pb['upperarm_l'].rotation_euler = Euler((R(ul_x), R(ul_y), R(ul_z)))
                    pb['lowerarm_l'].rotation_euler = Euler((R(ll_x), 0, R(ll_z)))
                    bpy.context.view_layer.update()
                    loc = (arm_obj.matrix_world @ pb['hand_l'].matrix).to_translation()
                    d = (loc - target_l).length
                    if d < best_dist_l:
                        best_dist_l = d
                        best_angles_l = (ul_x, ul_y, ul_z, ll_x, ll_z)

print(f"Mejor Brazo Izquierdo: dist={best_dist_l:.4f}m con angles={best_angles_l}")

# Aplicar los mejores
ur_x, ur_y, ur_z, lr_x, lr_z = best_angles_r
pb['upperarm_r'].rotation_euler = Euler((R(ur_x), R(ur_y), R(ur_z)))
pb['lowerarm_r'].rotation_euler = Euler((R(lr_x), 0, R(lr_z)))
pb['hand_r'].rotation_euler = Euler((R(-10), R(15), R(-20)))

ul_x, ul_y, ul_z, ll_x, ll_z = best_angles_l
pb['upperarm_l'].rotation_euler = Euler((R(ul_x), R(ul_y), R(ul_z)))
pb['lowerarm_l'].rotation_euler = Euler((R(ll_x), 0, R(ll_z)))
pb['hand_l'].rotation_euler = Euler((R(15), R(-10), R(20)))

bpy.context.view_layer.update()

# Render de comprobación
cam_data = bpy.data.cameras.new("TestCam2")
cam_obj = bpy.data.objects.new("TestCam2", cam_data)
bpy.context.scene.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj

cam_obj.location = Vector((1.6, -2.2, 1.1))
cam_dir = Vector((-0.05, -0.2, 0.85)) - cam_obj.location
rot_quat = cam_dir.to_track_quat('-Z', 'Y')
cam_obj.rotation_euler = rot_quat.to_euler()

bpy.context.scene.render.resolution_x = 960
bpy.context.scene.render.resolution_y = 720
bpy.context.scene.render.filepath = "C:/Users/sasuk/.gemini/antigravity/brain/b59ff04f-3c21-4ee5-94b0-8e8f899f8923/Verify_Blender_Weapon_Grip_Test2.png"
bpy.ops.render.render(write_still=True)
print(f"Render 2 guardado en {bpy.context.scene.render.filepath}")

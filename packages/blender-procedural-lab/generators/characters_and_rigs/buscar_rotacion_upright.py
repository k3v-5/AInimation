import bpy
import math
from mathutils import Vector, Euler

BLEND_FILE = "f:/Dev/Game/Art/Blender/SK_Firefighter_Official_Rigged.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND_FILE)
arm_obj = bpy.data.objects.get("SK_Firefighter_Armature")
gun_obj = bpy.data.objects.get("SM_ExtinguisherCannon")

def R(deg):
    return math.radians(deg)

bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='POSE')
pb = arm_obj.pose.bones

# Tronco erguido firme
pb['pelvis'].rotation_euler = Euler((R(2), 0.0, 0.0))
pb['spine_01'].rotation_euler = Euler((R(3), 0.0, 0.0))
pb['spine_02'].rotation_euler = Euler((R(2), 0.0, 0.0))
pb['clavicle_r'].rotation_euler = Euler((R(-8), 0, R(-4)))
pb['clavicle_l'].rotation_euler = Euler((R(-18), 0, R(10)))

pb['upperarm_r'].rotation_euler = Euler((R(-48), R(12), R(36)))
pb['lowerarm_r'].rotation_euler = Euler((R(-20), R(15), R(-80)))
pb['hand_r'].rotation_euler = Euler((R(18), R(20), R(-15)))

pb['upperarm_l'].rotation_euler = Euler((R(-56), R(-18), R(-48)))
pb['lowerarm_l'].rotation_euler = Euler((R(-20), R(-15), R(68)))
pb['hand_l'].rotation_euler = Euler((R(16), R(-10), R(22)))

bpy.context.view_layer.update()

gun_obj.parent = arm_obj
gun_obj.parent_type = 'BONE'
gun_obj.parent_bone = 'weapon_socket_r'

for rx in range(0, 360, 45):
    for ry in range(0, 360, 45):
        for rz in range(0, 360, 45):
            gun_obj.rotation_euler = Euler((R(rx), R(ry), R(rz)))
            bpy.context.view_layer.update()
            
            m3 = gun_obj.matrix_world.to_3x3()
            b_dir = m3 @ Vector((-1, 0, 0))  # Cañón (-X local)
            g_dir = m3 @ Vector((0, 0, -1))  # Empuñaduras (-Z local)
            
            # Queremos que b_dir apunte adelante (Y < 0) y g_dir apunte abajo (Z < 0)
            score = -b_dir.y - g_dir.z
            if b_dir.y < -0.5 and g_dir.z < -0.5:
                print(f"Cand: rot=({rx}, {ry}, {rz}) -> barrel_Y={b_dir.y:.2f}, grip_Z={g_dir.z:.2f}, score={score:.2f}")


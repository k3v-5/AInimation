import bpy
import math
from mathutils import Vector, Euler, Matrix
import os

BLEND_FILE = "f:/Dev/Game/Art/Blender/SK_Firefighter_Official_Rigged.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND_FILE)

arm_obj = bpy.data.objects.get("SK_Firefighter_Armature")
char_obj = bpy.data.objects.get("SK_Firefighter_Official")
gun_obj = bpy.data.objects.get("SM_ExtinguisherCannon")

print("=" * 60)
print("ANALISIS DE HUESOS Y SOCKETS EN BLENDER")
print("=" * 60)

def R(deg):
    return math.radians(deg)

# Inspeccionar rest pose
bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='EDIT')
eb = arm_obj.data.edit_bones
for bname in ['hand_r', 'hand_l', 'weapon_socket_r']:
    if bname in eb:
        b = eb[bname]
        print(f"EditBone '{bname}': head={b.head}, tail={b.tail}, roll={b.roll}, parent={b.parent.name if b.parent else 'None'}")

bpy.ops.object.mode_set(mode='POSE')
pb = arm_obj.pose.bones

# Aplicar pose Hose Hold
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
pb['upperarm_r'].rotation_euler = Euler((R(25), R(12), R(10)))
pb['lowerarm_r'].rotation_euler = Euler((0.0, 0.0, -R(65)))
pb['hand_r'].rotation_euler = Euler((0.0, 0.0, 0.0))
pb['upperarm_l'].rotation_euler = Euler((R(32), R(-16), R(-12)))
pb['lowerarm_l'].rotation_euler = Euler((0.0, 0.0, R(70)))
pb['hand_l'].rotation_euler = Euler((0.0, 0.0, 0.0))

bpy.context.view_layer.update()

for bname in ['hand_r', 'hand_l', 'weapon_socket_r']:
    bone = pb[bname]
    mat = arm_obj.matrix_world @ bone.matrix
    loc = mat.to_translation()
    rot = mat.to_euler()
    print(f"Pose Bone '{bname}': WorldLoc={loc}, WorldRot(deg)=({math.degrees(rot.x):.1f}, {math.degrees(rot.y):.1f}, {math.degrees(rot.z):.1f})")

# Si el arma se emparenta a weapon_socket_r con transform relativo identidad
sock_mat = arm_obj.matrix_world @ pb['weapon_socket_r'].matrix
print(f"weapon_socket_r Matrix World Translation: {sock_mat.to_translation()}")

# Geometria del cañon
print("\nGeometria del SM_ExtinguisherCannon:")
print(f"  gun_obj dimensions: {gun_obj.dimensions}")
print(f"  gun_obj location: {gun_obj.location}")
print("=" * 60)

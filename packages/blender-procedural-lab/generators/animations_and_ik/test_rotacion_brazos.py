import bpy
import math
from mathutils import Vector, Euler, Matrix

BLEND_FILE = "f:/Dev/Game/Art/Blender/SK_Firefighter_Official_Rigged.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND_FILE)

arm_obj = bpy.data.objects.get("SK_Firefighter_Armature")
char_obj = bpy.data.objects.get("SK_Firefighter_Official")

# En rest pose:
bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='EDIT')
eb = arm_obj.data.edit_bones
head = eb['head']
foot_l = eb['foot_l']
print(f"head: head={head.head}, tail={head.tail}")
print(f"foot_l: head={foot_l.head}, tail={foot_l.tail}")
# La punta del pie va hacia -Y:
# foot.tail = (0.26 * sign, -0.16, 0.02) -> -Y ES EL FRENTE DEL PERSONAJE!
print("El frente del personaje es efectivamente -Y (hacia adelante).")

bpy.ops.object.mode_set(mode='POSE')
pb = arm_obj.pose.bones
print("\nProbando rotación de brazo hacia adelante:")
for ang in [-30, -15, 0, 15, 30]:
    pb['upperarm_r'].rotation_euler = Euler((math.radians(ang), 0, 0))
    bpy.context.view_layer.update()
    loc = (arm_obj.matrix_world @ pb['hand_r'].matrix).to_translation()
    print(f"  upperarm_r X={ang}° -> hand_r Y={loc.y:.4f}, Z={loc.z:.4f}")


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

bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='POSE')
pb = arm_obj.pose.bones

# Postura erguida táctica con brazos al frente
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

pb['clavicle_r'].rotation_euler = Euler((R(-8), 0, R(-4)))
pb['clavicle_l'].rotation_euler = Euler((R(-18), 0, R(10)))

pb['upperarm_r'].rotation_euler = Euler((R(-48), R(12), R(36)))
pb['lowerarm_r'].rotation_euler = Euler((R(-20), R(15), R(-80)))
pb['hand_r'].rotation_euler = Euler((R(18), R(20), R(-15)))

pb['upperarm_l'].rotation_euler = Euler((R(-56), R(-18), R(-48)))
pb['lowerarm_l'].rotation_euler = Euler((R(-20), R(-15), R(68)))
pb['hand_l'].rotation_euler = Euler((R(16), R(-10), R(22)))

bpy.context.view_layer.update()

# Emparentar gun_obj a weapon_socket_r
gun_obj.parent = arm_obj
gun_obj.parent_type = 'BONE'
gun_obj.parent_bone = 'weapon_socket_r'

# Colocar con la rotación óptima encontrada: rot=(45°, 0°, 270°) y offset para encajar en la mano
gun_obj.location = Vector((-0.03, -0.15, -0.05))
gun_obj.rotation_euler = Euler((R(45), R(0), R(270)))
bpy.context.view_layer.update()

# Render cámara 3/4 frontal
cam_data = bpy.data.cameras.new("HoseHoldCamV2")
cam_obj = bpy.data.objects.new("HoseHoldCamV2", cam_data)
bpy.context.scene.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj

cam_obj.location = Vector((1.3, -2.1, 1.05))
cam_dir = Vector((-0.05, -0.22, 0.82)) - cam_obj.location
rot_quat = cam_dir.to_track_quat('-Z', 'Y')
cam_obj.rotation_euler = rot_quat.to_euler()

bpy.context.scene.render.resolution_x = 960
bpy.context.scene.render.resolution_y = 720
out_path = "C:/Users/sasuk/.gemini/antigravity/brain/b59ff04f-3c21-4ee5-94b0-8e8f899f8923/Verify_Blender_Hose_Hold_Perfect.png"
bpy.context.scene.render.filepath = out_path
bpy.ops.render.render(write_still=True)
print(f"Render perfecto guardado en {out_path}")

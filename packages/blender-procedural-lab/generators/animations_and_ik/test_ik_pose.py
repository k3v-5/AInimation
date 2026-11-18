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
gun_pos = Vector((-0.06, -0.32, 0.86))
gun_rot = Euler((0.0, 0.0, R(90))) # Apuntando al frente (-Y)
gun_obj.location = gun_pos
gun_obj.rotation_euler = gun_rot
bpy.context.view_layer.update()

gun_mat = gun_obj.matrix_world
grip_r_world = gun_mat @ Vector((0.17, 0, -0.14))   # Empuñadura trasera
grip_l_world = gun_mat @ Vector((-0.11, 0, -0.13))  # Empuñadura delantera

print(f"Grip R Target: {grip_r_world}")
print(f"Grip L Target: {grip_l_world}")

bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='POSE')
pb = arm_obj.pose.bones

# Reset
for b in pb:
    b.rotation_euler = Euler((0, 0, 0))
    b.location = Vector((0, 0, 0))

# Postura base erguida
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

# Clavículas proyectadas ligeramente hacia el frente
pb['clavicle_r'].rotation_euler = Euler((R(-8), 0.0, R(-4)))
pb['clavicle_l'].rotation_euler = Euler((R(-18), 0.0, R(10)))

# Crear empties de target para IK
target_r = bpy.data.objects.new("Target_R", None)
bpy.context.scene.collection.objects.link(target_r)
target_r.location = grip_r_world

target_l = bpy.data.objects.new("Target_L", None)
bpy.context.scene.collection.objects.link(target_l)
target_l.location = grip_l_world

# Añadir restricciones IK a hand_r y hand_l (chain length = 2: hand y lowerarm, con upperarm)
c_r = pb['hand_r'].constraints.new('IK')
c_r.target = target_r
c_r.chain_count = 2

c_l = pb['hand_l'].constraints.new('IK')
c_l.target = target_l
c_l.chain_count = 2

bpy.context.view_layer.update()

loc_r = (arm_obj.matrix_world @ pb['hand_r'].matrix).to_translation()
loc_l = (arm_obj.matrix_world @ pb['hand_l'].matrix).to_translation()

print(f"Hand R World: {loc_r} | Dist: {(loc_r - grip_r_world).length:.4f}m")
print(f"Hand L World: {loc_l} | Dist: {(loc_l - grip_l_world).length:.4f}m")

# Render cámara 3/4 frontal
cam_data = bpy.data.cameras.new("IKCam")
cam_obj = bpy.data.objects.new("IKCam", cam_data)
bpy.context.scene.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj

cam_obj.location = Vector((1.3, -2.1, 1.05))
cam_dir = Vector((-0.05, -0.22, 0.82)) - cam_obj.location
rot_quat = cam_dir.to_track_quat('-Z', 'Y')
cam_obj.rotation_euler = rot_quat.to_euler()

bpy.context.scene.render.resolution_x = 960
bpy.context.scene.render.resolution_y = 720
out_path = "C:/Users/sasuk/.gemini/antigravity/brain/b59ff04f-3c21-4ee5-94b0-8e8f899f8923/Verify_IK_Test.png"
bpy.context.scene.render.filepath = out_path
bpy.ops.render.render(write_still=True)
print(f"Render IK guardado en {out_path}")

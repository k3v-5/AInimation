import bpy
import math
from mathutils import Vector, Euler, Matrix

BLEND_FILE = "f:/Dev/Game/Art/Blender/SK_Firefighter_Official_Rigged.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND_FILE)

arm_obj = bpy.data.objects.get("SK_Firefighter_Armature")
gun_obj = bpy.data.objects.get("SM_ExtinguisherCannon")

def R(deg):
    return math.radians(deg)

# Posición ergonómica natural del arma:
# Descansando en la cadera/pecho derecho, apuntando al frente
gun_pos = Vector((-0.09, -0.20, 0.83))
gun_rot = Euler((R(-3), 0, R(90)))
gun_obj.location = gun_pos
gun_obj.rotation_euler = gun_rot
bpy.context.view_layer.update()

gun_mat = gun_obj.matrix_world
grip_r_world = gun_mat @ Vector((0.17, 0, -0.14))
grip_l_world = gun_mat @ Vector((-0.11, 0, -0.13))

print("=" * 60)
print(f"Grip R Target: {grip_r_world}")
print(f"Grip L Target: {grip_l_world}")

bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='POSE')
pb = arm_obj.pose.bones

# Reset
for b in pb:
    b.rotation_euler = Euler((0, 0, 0))
    b.location = Vector((0, 0, 0))

# Tronco erguido
pb['pelvis'].rotation_euler = Euler((R(2), 0.0, 0.0))
pb['spine_01'].rotation_euler = Euler((R(3), 0.0, 0.0))
pb['spine_02'].rotation_euler = Euler((R(2), 0.0, 0.0))

# Clavículas orientadas tácticamente
pb['clavicle_r'].rotation_euler = Euler((R(-6), 0, R(-4)))
pb['clavicle_l'].rotation_euler = Euler((R(-16), 0, R(12)))

# Crear empties de objetivo IK
empty_r = bpy.data.objects.new("IK_Target_R", None)
bpy.context.scene.collection.objects.link(empty_r)
empty_r.location = grip_r_world

empty_l = bpy.data.objects.new("IK_Target_L", None)
bpy.context.scene.collection.objects.link(empty_l)
empty_l.location = grip_l_world

# Añadir IK constraints en hand_r y hand_l
c_r = pb['hand_r'].constraints.new('IK')
c_r.target = empty_r
c_r.chain_count = 2  # afecta upperarm_r y lowerarm_r

c_l = pb['hand_l'].constraints.new('IK')
c_l.target = empty_l
c_l.chain_count = 2  # afecta upperarm_l y lowerarm_l

# Orientar manos a las empuñaduras
pb['hand_r'].rotation_euler = Euler((R(12), R(18), R(-15)))
pb['hand_l'].rotation_euler = Euler((R(15), R(-12), R(25)))

bpy.context.view_layer.update()

# Comprobar distancias resultantes
loc_r = (arm_obj.matrix_world @ pb['hand_r'].matrix).to_translation()
loc_l = (arm_obj.matrix_world @ pb['hand_l'].matrix).to_translation()

print(f"Resultado IK hand_r: {loc_r} | Error: {(loc_r - grip_r_world).length * 100:.2f} cm")
print(f"Resultado IK hand_l: {loc_l} | Error: {(loc_l - grip_l_world).length * 100:.2f} cm")

# Extraer matrices y Euler resultantes
for bname in ['upperarm_r', 'lowerarm_r', 'hand_r', 'upperarm_l', 'lowerarm_l', 'hand_l']:
    b = pb[bname]
    rot = b.matrix.to_euler()
    print(f"Bone '{bname}': rot euler (deg) = ({math.degrees(rot.x):.2f}, {math.degrees(rot.y):.2f}, {math.degrees(rot.z):.2f})")

# Render de comprobación visual frontal 3/4
cam_data = bpy.data.cameras.new("GripCamIK")
cam_obj = bpy.data.objects.new("GripCamIK", cam_data)
bpy.context.scene.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj

cam_obj.location = Vector((1.3, -2.0, 1.05))
cam_dir = Vector((-0.05, -0.22, 0.82)) - cam_obj.location
rot_quat = cam_dir.to_track_quat('-Z', 'Y')
cam_obj.rotation_euler = rot_quat.to_euler()

bpy.context.scene.render.resolution_x = 960
bpy.context.scene.render.resolution_y = 720
bpy.context.scene.render.filepath = "C:/Users/sasuk/.gemini/antigravity/brain/b59ff04f-3c21-4ee5-94b0-8e8f899f8923/Verify_Blender_Weapon_Grip_IK.png"
bpy.ops.render.render(write_still=True)
print(f"Render IK guardado en {bpy.context.scene.render.filepath}")

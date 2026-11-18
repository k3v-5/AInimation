import bpy
import math
from mathutils import Vector, Euler, Matrix

def R(deg):
    return math.radians(deg)

def D(rad):
    return math.degrees(rad)

BLEND_FILE = "f:/Dev/Game/Art/Blender/SK_Firefighter_Official_Rigged.blend"
bpy.ops.wm.open_mainfile(filepath=BLEND_FILE)

arm_obj = bpy.data.objects.get("SK_Firefighter_Armature")
gun_obj = bpy.data.objects.get("SM_ExtinguisherCannon")

bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode='POSE')
pb = arm_obj.pose.bones

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

# Posición táctica del cañón:
# En Blender: -Y es el frente, +Z es arriba, -X es el lado derecho del personaje
gun_pos = Vector((-0.07, -0.32, 0.94))
gun_rot = Euler((0.0, 0.0, R(90.0))) # Yaw = 90° alinea -X_mesh (cañón) con -Y_Blender (frente)

gun_obj.location = gun_pos
gun_obj.rotation_euler = gun_rot
bpy.context.view_layer.update()

gun_mat = gun_obj.matrix_world
grip_r_world = gun_mat @ Vector((0.17, 0, -0.14))   # Empuñadura trasera
grip_l_world = gun_mat @ Vector((-0.11, 0, -0.13))  # Empuñadura delantera

print("=" * 60)
print(f"Target Grip R (Rear Handle): {grip_r_world}")
print(f"Target Grip L (Front Handle): {grip_l_world}")

def solve_arm(bone_names, target_hand_bone, target_pos, initial_angles, bounds, step_sizes, iterations=1200):
    best_angles = [list(angs) for angs in initial_angles]
    
    def eval_loss(angles):
        for name, angs in zip(bone_names, angles):
            pb[name].rotation_euler = Euler(angs)
        bpy.context.view_layer.update()
        # Usamos el punto medio entre head y tail de la mano (centro del puño cerrado)
        h_head = (arm_obj.matrix_world @ pb[target_hand_bone].head)
        h_tail = (arm_obj.matrix_world @ pb[target_hand_bone].tail)
        hand_center = (h_head + h_tail) * 0.5
        return (hand_center - target_pos).length, hand_center

    best_loss, best_loc = eval_loss(best_angles)
    
    for it in range(iterations):
        improved = False
        decay = max(0.05, 1.0 - (it / float(iterations)) * 0.95)
        
        for b_idx in range(len(bone_names)):
            for a_idx in range(3):
                orig_val = best_angles[b_idx][a_idx]
                step = step_sizes[b_idx][a_idx] * decay
                min_val, max_val = bounds[b_idx][a_idx]
                
                for direction in [1.0, -1.0]:
                    new_val = max(min_val, min(max_val, orig_val + direction * step))
                    test_angles = [list(angs) for angs in best_angles]
                    test_angles[b_idx][a_idx] = new_val
                    
                    loss, loc = eval_loss(test_angles)
                    if loss < best_loss:
                        best_loss = loss
                        best_loc = loc
                        best_angles = test_angles
                        improved = True
                        break
        if best_loss < 0.002: # 2 mm
            break
            
    return best_angles, best_loss, best_loc

# --- BRAZO DERECHO ---
bones_r = ['clavicle_r', 'upperarm_r', 'lowerarm_r']
init_r = [
    [R(-6), 0.0, R(-3)],
    [R(-45), R(10), R(25)],
    [R(-15), R(10), R(-75)]
]
bounds_r = [
    [ (R(-20), R(5)), (R(-10), R(10)), (R(-15), R(10)) ],
    [ (R(-75), R(-15)), (R(-40), R(40)), (R(0), R(70)) ],
    [ (R(-60), R(40)), (R(-40), R(40)), (R(-130), R(-20)) ]
]
steps_r = [
    [R(2), R(1), R(2)],
    [R(3), R(3), R(3)],
    [R(3), R(3), R(3)]
]

best_r, loss_r, loc_r = solve_arm(bones_r, 'hand_r', grip_r_world, init_r, bounds_r, steps_r, 1500)
print(f"Right Arm Solved! Loss: {loss_r*100:.2f} cm | Hand Center: {loc_r}")
for bname, angs in zip(bones_r, best_r):
    pb[bname].rotation_euler = Euler(angs)
    print(f"  {bname}: Euler(({D(angs[0]):.1f}, {D(angs[1]):.1f}, {D(angs[2]):.1f}) deg)")

# Orientar mano derecha para empuñar el gatillo trasero (vertical hacia abajo)
pb['hand_r'].rotation_euler = Euler((R(12), R(15), R(-20)))
bpy.context.view_layer.update()

# --- BRAZO IZQUIERDO ---
bones_l = ['clavicle_l', 'upperarm_l', 'lowerarm_l']
init_l = [
    [R(-15), 0.0, R(8)],
    [R(-55), R(10), R(-35)],
    [R(-15), R(-10), R(65)]
]
bounds_l = [
    [ (R(-35), R(5)), (R(-10), R(10)), (R(-10), R(25)) ],
    [ (R(-85), R(-20)), (R(-40), R(40)), (R(-80), R(20)) ],
    [ (R(-60), R(40)), (R(-40), R(40)), (R(20), R(130)) ]
]
steps_l = [
    [R(2), R(1), R(2)],
    [R(3), R(3), R(3)],
    [R(3), R(3), R(3)]
]

best_l, loss_l, loc_l = solve_arm(bones_l, 'hand_l', grip_l_world, init_l, bounds_l, steps_l, 1500)
print(f"Left Arm Solved! Loss: {loss_l*100:.2f} cm | Hand Center: {loc_l}")
for bname, angs in zip(bones_l, best_l):
    pb[bname].rotation_euler = Euler(angs)
    print(f"  {bname}: Euler(({D(angs[0]):.1f}, {D(angs[1]):.1f}, {D(angs[2]):.1f}) deg)")

# Orientar mano izquierda para envolver el mango frontal
pb['hand_l'].rotation_euler = Euler((R(-8), R(-12), R(20)))
bpy.context.view_layer.update()

# Render 1: Cámara 3/4 frontal
cam_data = bpy.data.cameras.new("SolveCam1")
cam_obj = bpy.data.objects.new("SolveCam1", cam_data)
bpy.context.scene.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj

cam_obj.location = Vector((1.3, -2.1, 1.15))
cam_dir = Vector((-0.07, -0.28, 0.92)) - cam_obj.location
rot_quat = cam_dir.to_track_quat('-Z', 'Y')
cam_obj.rotation_euler = rot_quat.to_euler()

bpy.context.scene.render.resolution_x = 960
bpy.context.scene.render.resolution_y = 720
out_path1 = "C:/Users/sasuk/.gemini/antigravity/brain/b59ff04f-3c21-4ee5-94b0-8e8f899f8923/Verify_Solve_Exact_Front34.png"
bpy.context.scene.render.filepath = out_path1
bpy.ops.render.render(write_still=True)
print(f"Render 1 guardado en {out_path1}")

# Render 2: Cámara sobre el hombro derecho (vista 3P)
cam_obj.location = Vector((-0.7, 1.3, 1.35))
cam_dir = Vector((-0.07, -0.5, 0.94)) - cam_obj.location
rot_quat = cam_dir.to_track_quat('-Z', 'Y')
cam_obj.rotation_euler = rot_quat.to_euler()

out_path2 = "C:/Users/sasuk/.gemini/antigravity/brain/b59ff04f-3c21-4ee5-94b0-8e8f899f8923/Verify_Solve_Exact_OverShoulder.png"
bpy.context.scene.render.filepath = out_path2
bpy.ops.render.render(write_still=True)
print(f"Render 2 guardado en {out_path2}")

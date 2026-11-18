"""generate_fps_unarmed_suite.py
Genera la suite de animaciones desarmadas en primera persona para SK_FPS_Arms:
- A_FPS_Unarmed_Idle (postura simétrica relajada/táctica idéntica a la posición de brazos del personaje)
- A_FPS_Unarmed_Walk (locomoción fluida de caminata con brazos en posición coordinada)
- A_FPS_Unarmed_Run (carrera dinámica con balanceo controlado)
Exporta los FBX a Art/FBX/Anim_FPS/ y renderiza previsualizaciones de validación.
"""

import os
import sys
import math
import bpy
from mathutils import Vector, Euler

PROJECT_ROOT = r"E:\Darx_Proyect"
FBX_FPS_ARMS = os.path.join(PROJECT_ROOT, "Art", "FBX", "SK_FPS_Arms.fbx")
OUT_DIR_FPS = os.path.join(PROJECT_ROOT, "Art", "FBX", "Anim_FPS")
PREVIEW_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"

sys.path.append(os.path.join(PROJECT_ROOT, "Art", "Blender"))
import darx_lib as dl

def export_fps_action(arm_obj, act, filename):
    arm_obj.data.pose_position = 'POSE'
    arm_obj.animation_data.action = act
    if hasattr(arm_obj.animation_data, "action_slot") and act.slots:
        for s in act.slots:
            arm_obj.animation_data.action_slot = s
            break
    bpy.context.scene.frame_start = int(act.frame_range[0])
    bpy.context.scene.frame_end = int(act.frame_range[1])
    bpy.context.scene.frame_set(int(act.frame_range[0]))
    bpy.context.view_layer.update()
    dl.export_fbx([arm_obj], filename, armature=True, anim=True, subdir="Anim_FPS")
    print(f"  [OK] Exportada {filename} ({int(act.frame_range[1]) - int(act.frame_range[0]) + 1} frames)")

def main():
    print("=== [1/4] CARGANDO SK_FPS_Arms.fbx ===")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.render.fps = 30
    bpy.ops.import_scene.fbx(filepath=FBX_FPS_ARMS)

    arm_obj = next((o for o in bpy.data.objects if o.type == 'ARMATURE'), None)
    mesh_obj = next((o for o in bpy.data.objects if o.type == 'MESH'), None)
    if not arm_obj:
        raise RuntimeError("No se encontró armadura en SK_FPS_Arms.fbx")

    arm_obj.name = "ARM_FPS"

    # Reset bones
    for pb in arm_obj.pose.bones:
        pb.rotation_mode = 'XYZ'
        pb.rotation_euler = (0, 0, 0)
        pb.location = (0, 0, 0)

    # Postura calibrada simétrica que coincide con la postura del personaje (brazos descendidos a 45 grados)
    R_UPPER_ROT = (-45, -25, 20)
    R_FOREARM_ROT = (-65, 15, -15)
    R_HAND_ROT = (15, 0, 0)

    L_UPPER_ROT = (-20, 25, -20)
    L_FOREARM_ROT = (-35, -15, 15)
    L_HAND_ROT = (15, 0, 0)

    def _guard_pose(r_breath=0.0, l_breath=0.0, root_y=0.0, root_z=0.0):
        return {
            "root": {"loc": (0.0, root_y, root_z)},
            "weapon": {"loc": (0.0, 0.0, 0.0), "rot": (0.0, 0.0, 0.0)},
            "cell": {"loc": (0.0, 0.0, 0.0), "rot": (0.0, 0.0, 0.0)},
            "upperarm_R": {"rot": (R_UPPER_ROT[0] + r_breath, R_UPPER_ROT[1], R_UPPER_ROT[2])},
            "forearm_R": {"rot": (R_FOREARM_ROT[0] - r_breath * 0.5, R_FOREARM_ROT[1], R_FOREARM_ROT[2])},
            "hand_R": {"rot": R_HAND_ROT},
            "upperarm_L": {"rot": (L_UPPER_ROT[0] + l_breath, L_UPPER_ROT[1], L_UPPER_ROT[2])},
            "forearm_L": {"rot": (L_FOREARM_ROT[0] - l_breath * 0.5, L_FOREARM_ROT[1], L_FOREARM_ROT[2])},
            "hand_L": {"rot": L_HAND_ROT},
        }

    print("=== [2/4] CONSTRUYENDO ANIMACIONES DESARMADAS FPS ===")
    
    # --- A_FPS_Unarmed_Idle (60 frames, respiración sutil) ---
    idle_keys = {
        0: _guard_pose(r_breath=0.0, l_breath=0.0, root_y=0.0, root_z=0.0),
        30: _guard_pose(r_breath=1.5, l_breath=1.5, root_y=0.002, root_z=-0.003),
        60: _guard_pose(r_breath=0.0, l_breath=0.0, root_y=0.0, root_z=0.0),
    }
    act_idle = dl.action(arm_obj, "A_FPS_Unarmed_Idle", 60, idle_keys, loop=True, interp='BEZIER')
    export_fps_action(arm_obj, act_idle, "A_FPS_Unarmed_Idle.fbx")

    # --- A_FPS_Unarmed_Walk (30 frames, paso alternado) ---
    walk_keys = {}
    for f, (step_r, step_l, bob_z, bob_x) in [
        (0,  (0.0,  0.0,  0.000,  0.000)),
        (7,  (3.0, -2.5, -0.012,  0.004)),
        (15, (0.0,  0.0,  0.002,  0.000)),
        (22, (-2.5, 3.0, -0.012, -0.004)),
        (30, (0.0,  0.0,  0.000,  0.000)),
    ]:
        walk_keys[f] = {
            "root": {"loc": (bob_x, 0.0, bob_z)},
            "weapon": {"loc": (0.0, 0.0, 0.0), "rot": (0.0, 0.0, 0.0)},
            "cell": {"loc": (0.0, 0.0, 0.0), "rot": (0.0, 0.0, 0.0)},
            "upperarm_R": {"rot": (R_UPPER_ROT[0] + step_r, R_UPPER_ROT[1] + step_r * 0.3, R_UPPER_ROT[2])},
            "forearm_R": {"rot": (R_FOREARM_ROT[0] - step_r * 0.4, R_FOREARM_ROT[1], R_FOREARM_ROT[2])},
            "hand_R": {"rot": (R_HAND_ROT[0] + step_r * 0.2, R_HAND_ROT[1], R_HAND_ROT[2])},
            "upperarm_L": {"rot": (L_UPPER_ROT[0] + step_l, L_UPPER_ROT[1] - step_l * 0.3, L_UPPER_ROT[2])},
            "forearm_L": {"rot": (L_FOREARM_ROT[0] - step_l * 0.4, L_FOREARM_ROT[1], L_FOREARM_ROT[2])},
            "hand_L": {"rot": (L_HAND_ROT[0] + step_l * 0.2, L_HAND_ROT[1], L_HAND_ROT[2])},
        }
    act_walk = dl.action(arm_obj, "A_FPS_Unarmed_Walk", 30, walk_keys, loop=True, interp='BEZIER')
    export_fps_action(arm_obj, act_walk, "A_FPS_Unarmed_Walk.fbx")

    # --- A_FPS_Unarmed_Run (22 frames, carrera dinámica) ---
    run_keys = {}
    for f, (pump_r, pump_l, bob_z, bob_x) in [
        (0,  (0.0,   0.0,   0.000,  0.000)),
        (5,  (5.0,  -4.0,  -0.020,  0.006)),
        (11, (0.0,   0.0,   0.004,  0.000)),
        (16, (-4.0,  5.0,  -0.020, -0.006)),
        (22, (0.0,   0.0,   0.000,  0.000)),
    ]:
        run_keys[f] = {
            "root": {"loc": (bob_x, 0.0, bob_z)},
            "weapon": {"loc": (0.0, 0.0, 0.0), "rot": (0.0, 0.0, 0.0)},
            "cell": {"loc": (0.0, 0.0, 0.0), "rot": (0.0, 0.0, 0.0)},
            "upperarm_R": {"rot": (R_UPPER_ROT[0] + pump_r, R_UPPER_ROT[1] + pump_r * 0.3, R_UPPER_ROT[2])},
            "forearm_R": {"rot": (R_FOREARM_ROT[0] - pump_r * 0.5, R_FOREARM_ROT[1], R_FOREARM_ROT[2])},
            "hand_R": {"rot": (R_HAND_ROT[0] + pump_r * 0.2, R_HAND_ROT[1], R_HAND_ROT[2])},
            "upperarm_L": {"rot": (L_UPPER_ROT[0] + pump_l, L_UPPER_ROT[1] - pump_l * 0.3, L_UPPER_ROT[2])},
            "forearm_L": {"rot": (L_FOREARM_ROT[0] - pump_l * 0.5, L_FOREARM_ROT[1], L_FOREARM_ROT[2])},
            "hand_L": {"rot": (L_HAND_ROT[0] + pump_l * 0.2, L_HAND_ROT[1], L_HAND_ROT[2])},
        }
    act_run = dl.action(arm_obj, "A_FPS_Unarmed_Run", 22, run_keys, loop=True, interp='BEZIER')
    export_fps_action(arm_obj, act_run, "A_FPS_Unarmed_Run.fbx")

    print("=== [3/4] RENDERIZANDO PREVISUALIZACIONES DE VALIDACIÓN ===")
    arm_obj.animation_data.action = act_idle
    if hasattr(arm_obj.animation_data, "action_slot") and act_idle.slots:
        arm_obj.animation_data.action_slot = act_idle.slots[0]
    bpy.context.scene.frame_set(0)
    bpy.context.view_layer.update()

    pb_w = arm_obj.pose.bones.get("weapon")
    if pb_w:
        pb_w.scale = (0.0001, 0.0001, 0.0001)

    scene = bpy.context.scene
    scene.render.resolution_x = 768
    scene.render.resolution_y = 768

    for o in list(scene.collection.objects):
        if o.type in ('LIGHT', 'CAMERA'):
            bpy.data.objects.remove(o, do_unlink=True)

    world = scene.world or bpy.data.worlds.new('StudioWorld')
    scene.world = world
    bg = world.node_tree.nodes.get('Background')
    if bg:
        bg.inputs['Color'].default_value = (0.05, 0.05, 0.07, 1.0)
        bg.inputs['Strength'].default_value = 1.0

    l_key = bpy.data.lights.new('Key', 'SUN')
    l_key.energy = 4.0
    o_key = bpy.data.objects.new('Key', l_key)
    o_key.rotation_euler = (math.radians(-50), math.radians(25), math.radians(160))
    scene.collection.objects.link(o_key)

    l_fill = bpy.data.lights.new('Fill', 'SUN')
    l_fill.energy = 2.0
    l_fill.color = (0.7, 0.8, 1.0)
    o_fill = bpy.data.objects.new('Fill', l_fill)
    o_fill.rotation_euler = (math.radians(35), math.radians(-30), math.radians(-45))
    scene.collection.objects.link(o_fill)

    cam_data = bpy.data.cameras.new('Cam')
    cam_obj = bpy.data.objects.new('Cam', cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    cam_obj.location = Vector((0.0, 1.8, -0.4))
    cam_obj.rotation_euler = (math.radians(90), 0, math.radians(180))
    p_front = os.path.join(PREVIEW_DIR, "validation_fps_arms_unarmed_front.png")
    scene.render.filepath = p_front
    bpy.ops.render.render(write_still=True)
    print(f"  [OK] Render frontal: {p_front}")

    print("=== [4/4] GENERACIÓN DE ANIMACIONES FPS DESARMADAS COMPLETADA ===")

if __name__ == "__main__":
    main()

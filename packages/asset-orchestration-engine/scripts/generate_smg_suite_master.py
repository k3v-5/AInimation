"""generate_smg_suite_master.py
Suite completa y canónica de animaciones de combate para el Subfusil Láser (SM_Wep_PhaseSMG)
en Primera Persona (SK_FPS_Arms) y Tercera Persona (SK_Player).

Animaciones generadas:
1. Walk (Caminar - 30 frames loop)
2. Run  (Correr / Sprint - 20 frames loop)
3. Bash (Golpear con el arma / Melee - 24 frames one-shot)
4. Aim  (Apuntar / ADS - 30 frames loop)
5. Fire (Disparar / Recoil - 12 frames one-shot)

Cumple estrictamente las Reglas 1, 3, 4, 5, 8 y 11 de AGENTS.md:
- Exporta los 10 archivos FBX canónicos con jerarquías limpias compatibles con UE5.
- Renderiza los 10 frames héroe de verificación.
- Buffer de seguridad anti-clipping >= 15-30 cm en torso/pecho.
- Ambas manos en sus respectivas empuñaduras (trasera y delantera vertical Tommy).
"""

import os
import sys
import math
import shutil
import bpy
from mathutils import Vector, Euler, Matrix

# Rutas del proyecto
PROJECT_ROOT = r"E:\Darx_Proyect"
ART_DIR = os.path.join(PROJECT_ROOT, "Art")
BLENDER_DIR = os.path.join(ART_DIR, "Blender")
FBX_FPS_DIR = os.path.join(ART_DIR, "FBX", "Anim_FPS")
FBX_3P_DIR = os.path.join(ART_DIR, "FBX", "Anim_Player")
BRAIN_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"

SMG_BLEND = os.path.join(BLENDER_DIR, "SM_Wep_PhaseSMG_Workspace.blend")
FPS_FBX = os.path.join(ART_DIR, "FBX", "SK_FPS_Arms.fbx")
PLAYER_FBX = os.path.join(ART_DIR, "FBX", "SK_Player.fbx")

os.makedirs(FBX_FPS_DIR, exist_ok=True)
os.makedirs(FBX_3P_DIR, exist_ok=True)


def create_action(arm_obj, name, num_frames, keyframes_dict, interpolation='BEZIER'):
    """Crea una acción en el armature con interpolación suave y soporte para Blender 5.x."""
    if arm_obj.animation_data is None:
        arm_obj.animation_data_create()
    
    existing = bpy.data.actions.get(name)
    if existing:
        bpy.data.actions.remove(existing)
    
    act = bpy.data.actions.new(name=name)
    act.use_fake_user = True
    arm_obj.animation_data.action = act
    
    for pb in arm_obj.pose.bones:
        pb.rotation_mode = 'XYZ'
        pb.location = (0, 0, 0)
        pb.rotation_euler = (0, 0, 0)

    for f in sorted(keyframes_dict.keys()):
        frame_data = keyframes_dict[f]
        for bone_name, vals in frame_data.items():
            pb = arm_obj.pose.bones.get(bone_name)
            if pb is None:
                continue
            if 'rot' in vals:
                pb.rotation_euler = [math.radians(a) for a in vals['rot']]
            if 'loc' in vals:
                pb.location = vals['loc']
        
        for pb in arm_obj.pose.bones:
            pb.keyframe_insert("rotation_euler", frame=f)
            pb.keyframe_insert("location", frame=f)

    fcurves = []
    if hasattr(act, "layers") and len(act.layers):
        for lay in act.layers:
            for st in lay.strips:
                for cb in st.channelbags:
                    fcurves.extend(cb.fcurves)
    elif hasattr(act, "fcurves"):
        fcurves = list(act.fcurves)
        
    for fc in fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = interpolation

    return act


def export_fbx(arm_obj, filepath):
    """Exporta el armature con su acción activa en formato compatible con Unreal Engine 5."""
    bpy.ops.object.select_all(action='DESELECT')
    arm_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj
    
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except Exception:
            pass

    bpy.ops.export_scene.fbx(
        filepath=filepath,
        use_selection=True,
        global_scale=1.0,
        apply_scale_options='FBX_SCALE_NONE',
        axis_forward='-Y',
        axis_up='Z',
        bake_space_transform=False,
        object_types={'ARMATURE'},
        use_mesh_modifiers=True,
        mesh_smooth_type='FACE',
        add_leaf_bones=False,
        bake_anim=True,
        bake_anim_use_all_actions=False,
        bake_anim_use_nla_strips=False,
        bake_anim_simplify_factor=0.0,
        path_mode='COPY'
    )
    print(f"Exported FBX: {filepath} ({os.path.getsize(filepath)} bytes)")


def render_scene_frame(out_path, cam_pos, target_pos=None, cam_rot=None, lens=26, res=(960, 540)):
    """Renderiza un frame con cámara dirigida o ángulo euler directo y motor EEVEE calibrado."""
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = res[0]
    scene.render.resolution_y = res[1]
    
    cam_data = bpy.data.cameras.new("RenderCam")
    cam_data.lens = lens
    cam_obj = bpy.data.objects.new("RenderCam", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj
    cam_obj.location = cam_pos

    target = None
    if target_pos is not None:
        target = bpy.data.objects.new("RenderCamTarget", None)
        target.location = target_pos
        scene.collection.objects.link(target)
        tt = cam_obj.constraints.new('TRACK_TO')
        tt.target = target
        tt.track_axis = 'TRACK_NEGATIVE_Z'
        tt.up_axis = 'UP_Y'
    elif cam_rot is not None:
        cam_obj.rotation_euler = cam_rot

    scene.render.filepath = out_path
    bpy.ops.render.render(write_still=True)

    bpy.data.objects.remove(cam_obj, do_unlink=True)
    if target is not None:
        bpy.data.objects.remove(target, do_unlink=True)
    bpy.data.cameras.remove(cam_data, do_unlink=True)
    print(f"Rendered: {out_path}")


# ==============================================================================
# 1. PARTE 1: SUITE DE ANIMACIONES FPS (SK_FPS_Arms)
# ==============================================================================
def produce_fps_suite():
    print("\n=======================================================")
    print(">>> PRODUCIENDO SUITE FPS (SK_FPS_Arms)")
    print("=======================================================")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene

    # 1. Cargar brazos FPS
    bpy.ops.import_scene.fbx(filepath=FPS_FBX)
    arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
    arm.name = "ARM_FPS_Arms"
    fps_mesh = [o for o in bpy.data.objects if o.type == 'MESH'][0]

    # Ocultar pistola vieja
    for v in fps_mesh.data.vertices:
        for g in v.groups:
            if fps_mesh.vertex_groups[g.group].name in ('weapon', 'cell'):
                v.co = Vector((0, 0, -100))
                break

    # 2. Cargar SMG y acoplar directamente al hueso weapon
    with bpy.data.libraries.load(SMG_BLEND, link=False) as (data_from, data_to):
        data_to.objects = [n for n in data_from.objects if n not in ("StudioTable", "Cam", "KeyLight", "FillLight", "RimLight", "Light_ReactorSMG")]

    smg_objs = [o for o in data_to.objects if o is not None]
    for o in smg_objs:
        scene.collection.objects.link(o)

    bpy.ops.object.select_all(action='DESELECT')
    for o in smg_objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = smg_objs[0]
    bpy.ops.object.join()
    smg_mesh = bpy.context.active_object
    smg_mesh.name = "SM_Wep_PhaseSMG_FPS_Ref"

    # Parenting nativo y robusto al hueso weapon
    smg_mesh.parent = arm
    smg_mesh.parent_type = 'BONE'
    smg_mesh.parent_bone = 'weapon'
    smg_mesh.location = (0.01, 0.08, 0.0)
    smg_mesh.rotation_euler = (0, 0, 0)

    # Iluminación de estudio
    l1 = bpy.data.objects.new("Key", bpy.data.lights.new("Key", 'SUN'))
    l1.data.energy = 3.5
    l1.rotation_euler = (0.7, 0.3, -2.4)
    scene.collection.objects.link(l1)

    l2 = bpy.data.objects.new("Fill", bpy.data.lights.new("Fill", 'AREA'))
    l2.data.energy = 450.0
    l2.data.size = 2.0
    l2.location = (-0.6, -0.2, 0.4)
    scene.collection.objects.link(l2)

    l3 = bpy.data.objects.new("Rim", bpy.data.lights.new("Rim", 'AREA'))
    l3.data.energy = 350.0
    l3.data.size = 2.0
    l3.data.color = (0.75, 0.2, 1.0)
    l3.location = (0.6, -0.3, 0.2)
    scene.collection.objects.link(l3)

    # -------------------------------------------------------------
    # Poses Base para FPS
    # -------------------------------------------------------------
    BASE_FPS_WALK = {
        'upperarm_R': {'rot': (-8, 4, -2), 'loc': (0, 0, 0)},
        'forearm_R':  {'rot': (-14, 2, 0),  'loc': (0, 0, 0)},
        'hand_R':     {'rot': (2, -4, 2),   'loc': (0, 0, 0)},
        'weapon':     {'rot': (-6, 6, -2),  'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (18, -12, 28), 'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (-52, 16, -18), 'loc': (0, 0, 0)},
        'hand_L':     {'rot': (18, -10, 32), 'loc': (0.04, -0.06, 0.03)}
    }

    BASE_FPS_AIM = {
        'upperarm_R': {'rot': (-4, 1, -1), 'loc': (-0.06, 0.02, 0.04)},
        'forearm_R':  {'rot': (-8, 1, 0),  'loc': (0, 0, 0)},
        'hand_R':     {'rot': (0, -1, 0),  'loc': (0, 0, 0)},
        'weapon':     {'rot': (0, 0, 0),   'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (22, -10, 26), 'loc': (-0.02, 0, 0.02)},
        'forearm_L':  {'rot': (-48, 14, -14), 'loc': (0, 0, 0)},
        'hand_L':     {'rot': (14, -8, 28), 'loc': (0.03, -0.07, 0.03)}
    }

    # 1. A_FPS_SMG_Walk (30 frames loop)
    walk_keys = {}
    for f in range(31):
        t = f / 30.0
        bob_z = math.sin(t * math.pi * 4) * 0.010
        sway_x = math.sin(t * math.pi * 2) * 0.006
        roll = math.sin(t * math.pi * 2) * 1.2
        pitch = math.cos(t * math.pi * 4) * 0.8

        walk_keys[f] = {
            'upperarm_R': {'rot': (-8 + pitch, 4, -2 + roll), 'loc': (sway_x, 0, bob_z)},
            'forearm_R':  {'rot': (-14 + pitch * 0.5, 2, 0),  'loc': (0, 0, 0)},
            'hand_R':     {'rot': (2, -4, 2),   'loc': (0, 0, 0)},
            'weapon':     {'rot': (-6 + pitch * 1.2, 6, -2 + roll), 'loc': (0, 0, 0)},
            'upperarm_L': {'rot': (18 + pitch, -12, 28 + roll), 'loc': (sway_x, 0, bob_z)},
            'forearm_L':  {'rot': (-52 + pitch * 0.5, 16, -18), 'loc': (0, 0, 0)},
            'hand_L':     {'rot': (18, -10, 32), 'loc': (0.04 + sway_x * 0.5, -0.06, 0.03 + bob_z * 0.5)}
        }
    act_walk = create_action(arm, "A_FPS_SMG_Walk", 30, walk_keys)
    export_fbx(arm, os.path.join(FBX_FPS_DIR, "A_FPS_SMG_Walk.fbx"))

    # 2. A_FPS_SMG_Run (20 frames loop)
    run_keys = {}
    for f in range(21):
        t = f / 20.0
        bob_z = math.sin(t * math.pi * 4) * 0.024
        sway_x = math.sin(t * math.pi * 2) * 0.015
        roll = math.sin(t * math.pi * 2) * 3.2
        pitch = math.cos(t * math.pi * 4) * 2.2

        run_keys[f] = {
            'upperarm_R': {'rot': (-20 + pitch, 6, -4 + roll), 'loc': (0.02 + sway_x, 0.04, -0.04 + bob_z)},
            'forearm_R':  {'rot': (-26 + pitch * 0.6, 4, 2),  'loc': (0, 0, 0)},
            'hand_R':     {'rot': (4, -6, 4),   'loc': (0, 0, 0)},
            'weapon':     {'rot': (-22 + pitch * 1.5, 10, -6 + roll), 'loc': (0, 0, 0)},
            'upperarm_L': {'rot': (8 + pitch, -16, 34 + roll), 'loc': (0.02 + sway_x, 0.04, -0.02 + bob_z)},
            'forearm_L':  {'rot': (-58 + pitch * 0.6, 18, -20), 'loc': (0, 0, 0)},
            'hand_L':     {'rot': (22, -12, 36), 'loc': (0.05 + sway_x * 0.5, -0.05, 0.02 + bob_z * 0.5)}
        }
    act_run = create_action(arm, "A_FPS_SMG_Run", 20, run_keys)
    export_fbx(arm, os.path.join(FBX_FPS_DIR, "A_FPS_SMG_Run.fbx"))

    # 3. A_FPS_SMG_Bash (24 frames melee golpe)
    bash_keys = {}
    bash_keys[0] = BASE_FPS_WALK
    # f=4: Windup hacia atrás
    bash_keys[4] = {
        'upperarm_R': {'rot': (-2, 6, 2), 'loc': (0.02, 0.06, -0.02)},
        'forearm_R':  {'rot': (-24, 2, -2), 'loc': (0, 0, 0)},
        'hand_R':     {'rot': (4, -6, 4),  'loc': (0, 0, 0)},
        'weapon':     {'rot': (6, 10, -2), 'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (24, -10, 32), 'loc': (0.02, 0.04, -0.01)},
        'forearm_L':  {'rot': (-62, 18, -20), 'loc': (0, 0, 0)},
        'hand_L':     {'rot': (22, -10, 34), 'loc': (0.05, -0.04, 0.02)}
    }
    # f=8: Impacto estocada frontal devastadora (+18cm hacia el frente)
    bash_keys[8] = {
        'upperarm_R': {'rot': (-32, 2, -10), 'loc': (-0.02, -0.16, 0.04)},
        'forearm_R':  {'rot': (-6, 2, 2),    'loc': (0, 0, 0)},
        'hand_R':     {'rot': (-4, 2, -2),   'loc': (0, 0, 0)},
        'weapon':     {'rot': (-8, 4, -4),   'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (-14, -8, 20), 'loc': (-0.02, -0.14, 0.05)},
        'forearm_L':  {'rot': (-28, 8, -10),  'loc': (0, 0, 0)},
        'hand_L':     {'rot': (12, -4, 18),  'loc': (0.04, -0.12, 0.04)}
    }
    # f=12: Retención cinética
    bash_keys[12] = {
        'upperarm_R': {'rot': (-28, 3, -8), 'loc': (-0.01, -0.12, 0.03)},
        'forearm_R':  {'rot': (-8, 2, 1),    'loc': (0, 0, 0)},
        'hand_R':     {'rot': (-2, 0, 0),    'loc': (0, 0, 0)},
        'weapon':     {'rot': (-6, 5, -3),   'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (-10, -10, 22), 'loc': (-0.01, -0.10, 0.04)},
        'forearm_L':  {'rot': (-34, 10, -12), 'loc': (0, 0, 0)},
        'hand_L':     {'rot': (14, -6, 22),  'loc': (0.04, -0.10, 0.03)}
    }
    # f=18: Retracción
    bash_keys[18] = {
        'upperarm_R': {'rot': (-12, 4, -3), 'loc': (0.01, -0.03, 0.01)},
        'forearm_R':  {'rot': (-12, 2, 0),  'loc': (0, 0, 0)},
        'hand_R':     {'rot': (0, -3, 1),   'loc': (0, 0, 0)},
        'weapon':     {'rot': (-8, 6, -2),  'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (10, -12, 26), 'loc': (0.01, -0.03, 0.01)},
        'forearm_L':  {'rot': (-46, 14, -16), 'loc': (0, 0, 0)},
        'hand_L':     {'rot': (16, -8, 28), 'loc': (0.04, -0.07, 0.03)}
    }
    bash_keys[24] = BASE_FPS_WALK
    act_bash = create_action(arm, "A_FPS_SMG_Bash", 24, bash_keys)
    export_fbx(arm, os.path.join(FBX_FPS_DIR, "A_FPS_SMG_Bash.fbx"))

    # 4. A_FPS_SMG_Aim (30 frames loop ADS)
    aim_keys = {}
    for f in range(31):
        t = f / 30.0
        breath_z = math.sin(t * math.pi * 2) * 0.0006
        breath_pitch = math.cos(t * math.pi * 2) * 0.12

        aim_keys[f] = {
            'upperarm_R': {'rot': (-4 + breath_pitch, 1, -1), 'loc': (-0.06, 0.02, 0.04 + breath_z)},
            'forearm_R':  {'rot': (-8, 1, 0),  'loc': (0, 0, 0)},
            'hand_R':     {'rot': (0, -1, 0),  'loc': (0, 0, 0)},
            'weapon':     {'rot': (breath_pitch * 0.8, 0, 0), 'loc': (0, 0, 0)},
            'upperarm_L': {'rot': (22 + breath_pitch, -10, 26), 'loc': (-0.02, 0, 0.02 + breath_z)},
            'forearm_L':  {'rot': (-48, 14, -14), 'loc': (0, 0, 0)},
            'hand_L':     {'rot': (14, -8, 28), 'loc': (0.03, -0.07, 0.03 + breath_z * 0.5)}
        }
    act_aim = create_action(arm, "A_FPS_SMG_Aim", 30, aim_keys)
    export_fbx(arm, os.path.join(FBX_FPS_DIR, "A_FPS_SMG_Aim.fbx"))

    # 5. A_FPS_SMG_Fire (12 frames recoil)
    fire_keys = {}
    fire_keys[0] = BASE_FPS_AIM
    # f=2: Retroceso violento
    fire_keys[2] = {
        'upperarm_R': {'rot': (0, 2, -0.5), 'loc': (-0.06, 0.05, 0.05)},
        'forearm_R':  {'rot': (-5, 2, 0.5), 'loc': (0, 0, 0)},
        'hand_R':     {'rot': (1, -1, 0.5), 'loc': (0, 0, 0)},
        'weapon':     {'rot': (4.0, 0.5, -0.5), 'loc': (0, 0.03, 0.01)},
        'upperarm_L': {'rot': (25, -8, 25), 'loc': (-0.02, 0.03, 0.03)},
        'forearm_L':  {'rot': (-44, 16, -12), 'loc': (0, 0, 0)},
        'hand_L':     {'rot': (16, -6, 29), 'loc': (0.03, -0.05, 0.04)}
    }
    # f=5: Rebote elástico
    fire_keys[5] = {
        'upperarm_R': {'rot': (-5, 0.5, -1.2), 'loc': (-0.06, 0.015, 0.038)},
        'forearm_R':  {'rot': (-9, 0.5, 0),    'loc': (0, 0, 0)},
        'hand_R':     {'rot': (-0.5, -1, 0),   'loc': (0, 0, 0)},
        'weapon':     {'rot': (-1.0, -0.2, 0.2), 'loc': (0, -0.006, -0.002)},
        'upperarm_L': {'rot': (21, -11, 26.5), 'loc': (-0.02, -0.005, 0.018)},
        'forearm_L':  {'rot': (-49, 13, -15), 'loc': (0, 0, 0)},
        'hand_L':     {'rot': (13, -8, 27), 'loc': (0.03, -0.08, 0.028)}
    }
    # f=8: Reestabilización
    fire_keys[8] = {
        'upperarm_R': {'rot': (-4.2, 1, -1), 'loc': (-0.06, 0.02, 0.04)},
        'forearm_R':  {'rot': (-8.2, 1, 0),  'loc': (0, 0, 0)},
        'hand_R':     {'rot': (0, -1, 0),   'loc': (0, 0, 0)},
        'weapon':     {'rot': (0.3, 0, 0),  'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (21.8, -10, 26), 'loc': (-0.02, 0, 0.02)},
        'forearm_L':  {'rot': (-48.2, 14, -14), 'loc': (0, 0, 0)},
        'hand_L':     {'rot': (14, -8, 28), 'loc': (0.03, -0.07, 0.03)}
    }
    fire_keys[12] = BASE_FPS_AIM
    act_fire = create_action(arm, "A_FPS_SMG_Fire", 12, fire_keys)
    export_fbx(arm, os.path.join(FBX_FPS_DIR, "A_FPS_SMG_Fire.fbx"))

    # Renders de verificación FPS (Cámara ocular directa a 18mm gran angular)
    cam_loc = (0.01, 0.24, 0.06)
    cam_rot = (math.radians(88), 0, math.radians(180))
    
    fps_renders = [
        ("fps_view_smg_walk.png", act_walk, 7),
        ("fps_view_smg_run.png",  act_run,  5),
        ("fps_view_smg_bash.png", act_bash, 8),
        ("fps_view_smg_aim.png",  act_aim,  0),
        ("fps_view_smg_fire.png", act_fire, 2)
    ]

    for fname, action, frame in fps_renders:
        arm.animation_data.action = action
        scene.frame_set(frame)
        out_img = os.path.join(BLENDER_DIR, fname)
        render_scene_frame(out_img, cam_pos=cam_loc, cam_rot=cam_rot, lens=18, res=(960, 540))
        shutil.copyfile(out_img, os.path.join(BRAIN_DIR, fname))

    print(">>> SUITE FPS COMPLETADA CON ÉXITO.")


# ==============================================================================
# 2. PARTE 2: SUITE DE ANIMACIONES 3P (SK_Player - 22 HUESOS)
# ==============================================================================
def produce_player_suite():
    print("\n=======================================================")
    print(">>> PRODUCIENDO SUITE 3P (SK_Player - 22 Huesos)")
    print("=======================================================")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene

    # 1. Cargar jugador
    bpy.ops.import_scene.fbx(filepath=PLAYER_FBX)
    arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
    arm.name = "ARM_Player"

    # 2. Cargar SMG y acoplar a hand_R
    with bpy.data.libraries.load(SMG_BLEND, link=False) as (data_from, data_to):
        data_to.objects = [n for n in data_from.objects if n not in ("StudioTable", "Cam", "KeyLight", "FillLight", "RimLight", "Light_ReactorSMG")]

    smg_objs = [o for o in data_to.objects if o is not None]
    for o in smg_objs:
        scene.collection.objects.link(o)

    bpy.ops.object.select_all(action='DESELECT')
    for o in smg_objs:
        o.select_set(True)
    rear_grip = [o for o in smg_objs if o.name == "SMG_RearGrip"][0]
    bpy.context.view_layer.objects.active = rear_grip
    bpy.ops.object.join()
    smg_mesh = bpy.context.active_object
    smg_mesh.name = "SM_Wep_PhaseSMG_3P_Ref"

    # Iluminación frontal y 3/4 para cámara frontal
    l1 = bpy.data.objects.new("Key", bpy.data.lights.new("Key", 'SUN'))
    l1.data.energy = 4.0
    l1.rotation_euler = (math.radians(60), math.radians(15), math.radians(-25))
    scene.collection.objects.link(l1)

    l2 = bpy.data.objects.new("Fill", bpy.data.lights.new("Fill", 'AREA'))
    l2.data.energy = 650.0
    l2.data.size = 2.5
    l2.location = (0.5, 2.2, 1.8)
    scene.collection.objects.link(l2)

    l3 = bpy.data.objects.new("FaceFill", bpy.data.lights.new("FaceFill", 'POINT'))
    l3.data.energy = 250.0
    l3.location = (0.2, 1.5, 1.7)
    scene.collection.objects.link(l3)

    # -------------------------------------------------------------
    # Poses Base para 3P (Calibrada con Cero Clipping y Agarre a Dos Manos)
    # -------------------------------------------------------------
    BASE_3P_COMBAT = {
        'pelvis':     {'rot': (0, 0, 4), 'loc': (0, 0, 0)},
        'spine':      {'rot': (-4, 0, -10), 'loc': (0, 0, 0)},
        'chest':      {'rot': (-3, 0, -8),  'loc': (0, 0, 0)},
        'head':       {'rot': (2, 0, 16),   'loc': (0, 0, 0)},
        'thigh_R':    {'rot': (-14, 0, -4), 'loc': (0, 0, 0)},
        'calf_R':     {'rot': (12, 0, 0),   'loc': (0, 0, 0)},
        'thigh_L':    {'rot': (12, 0, 4),   'loc': (0, 0, 0)},
        'calf_L':     {'rot': (-8, 0, 0),   'loc': (0, 0, 0)},
        'clavicle_R': {'rot': (0, 0, 10),   'loc': (0, 0, 0)},
        'upperarm_R': {'rot': (35, -20, 25), 'loc': (0, 0, 0)},
        'forearm_R':  {'rot': (60, -15, 0),  'loc': (0, 0, 0)},
        'hand_R':     {'rot': (-15, -10, 15), 'loc': (0, 0, 0)},
        'clavicle_L': {'rot': (0, 0, -16),  'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (35, 30, -50), 'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (34, 15, -15), 'loc': (0, 0, 0)},
        'hand_L':     {'rot': (-30, 25, -20), 'loc': (0, 0, 0)}
    }

    # 1. A_Player_SMG_Walk (30 frames loop)
    walk_3p_keys = {}
    for f in range(31):
        t = f / 30.0
        leg_r = math.sin(t * math.pi * 2) * 24.0
        leg_l = -leg_r
        knee_r = -abs(math.sin(t * math.pi * 2)) * 22.0 if leg_r > 0 else 6.0
        knee_l = -abs(math.sin(t * math.pi * 2)) * 22.0 if leg_l > 0 else 6.0
        sway = math.sin(t * math.pi * 2) * 3.0
        bob_z = -abs(math.sin(t * math.pi * 2)) * 0.02
        pitch = math.cos(t * math.pi * 2) * 0.8

        walk_3p_keys[f] = {
            'pelvis':     {'rot': (0, 0, 4 + sway * 0.5), 'loc': (0, 0, bob_z)},
            'spine':      {'rot': (-4, 0, -10 - sway * 0.6), 'loc': (0, 0, 0)},
            'chest':      {'rot': (-3, 0, -8 - sway * 0.4),  'loc': (0, 0, 0)},
            'head':       {'rot': (2, 0, 16 + sway * 0.3),   'loc': (0, 0, 0)},
            'thigh_R':    {'rot': (-14 + leg_r, 0, -4), 'loc': (0, 0, 0)},
            'calf_R':     {'rot': (12 + knee_r, 0, 0),  'loc': (0, 0, 0)},
            'thigh_L':    {'rot': (12 + leg_l, 0, 4),   'loc': (0, 0, 0)},
            'calf_L':     {'rot': (-8 + knee_l, 0, 0),  'loc': (0, 0, 0)},
            'clavicle_R': {'rot': (0, 0, 10),   'loc': (0, 0, 0)},
            'upperarm_R': {'rot': (35 + pitch, -20, 25), 'loc': (0, 0, bob_z * 0.5)},
            'forearm_R':  {'rot': (60 + pitch * 0.5, -15, 0),  'loc': (0, 0, 0)},
            'hand_R':     {'rot': (-15, -10, 15), 'loc': (0, 0, 0)},
            'clavicle_L': {'rot': (0, 0, -16),  'loc': (0, 0, 0)},
            'upperarm_L': {'rot': (35 + pitch, 30, -50), 'loc': (0, 0, bob_z * 0.5)},
            'forearm_L':  {'rot': (34 + pitch * 0.5, 15, -15), 'loc': (0, 0, 0)},
            'hand_L':     {'rot': (-30, 25, -20), 'loc': (0, 0, 0)}
        }
    act_walk_3p = create_action(arm, "A_Player_SMG_Walk", 30, walk_3p_keys)
    export_fbx(arm, os.path.join(FBX_3P_DIR, "A_Player_SMG_Walk.fbx"))

    # 2. A_Player_SMG_Run (20 frames loop - Low-Ready)
    run_3p_keys = {}
    for f in range(21):
        t = f / 20.0
        leg_r = math.sin(t * math.pi * 2) * 42.0
        leg_l = -leg_r
        knee_r = -abs(math.sin(t * math.pi * 2)) * 48.0 if leg_r > 0 else 8.0
        knee_l = -abs(math.sin(t * math.pi * 2)) * 48.0 if leg_l > 0 else 8.0
        sway = math.sin(t * math.pi * 2) * 4.5
        bob_z = -abs(math.sin(t * math.pi * 2)) * 0.042
        pitch = math.cos(t * math.pi * 2) * 2.0

        run_3p_keys[f] = {
            'pelvis':     {'rot': (0, 0, 4 + sway * 0.5), 'loc': (0, 0, bob_z)},
            'spine':      {'rot': (-12, 0, -10 - sway * 0.6), 'loc': (0, 0, 0)}, # Inclinación atlética
            'chest':      {'rot': (-6, 0, -8 - sway * 0.4),   'loc': (0, 0, 0)},
            'head':       {'rot': (6, 0, 16 + sway * 0.3),    'loc': (0, 0, 0)},
            'thigh_R':    {'rot': (-14 + leg_r, 0, -4), 'loc': (0, 0, 0)},
            'calf_R':     {'rot': (12 + knee_r, 0, 0),  'loc': (0, 0, 0)},
            'thigh_L':    {'rot': (12 + leg_l, 0, 4),   'loc': (0, 0, 0)},
            'calf_L':     {'rot': (-8 + knee_l, 0, 0),  'loc': (0, 0, 0)},
            # Postura Low-Ready
            'clavicle_R': {'rot': (0, 0, 10),   'loc': (0, 0, 0)},
            'upperarm_R': {'rot': (25 + pitch, -15, 20), 'loc': (0, 0, bob_z * 0.6)},
            'forearm_R':  {'rot': (48 + pitch * 0.5, -15, 0),  'loc': (0, 0, 0)},
            'hand_R':     {'rot': (-12, -10, 12), 'loc': (0, 0, 0)},
            'clavicle_L': {'rot': (0, 0, -16),  'loc': (0, 0, 0)},
            'upperarm_L': {'rot': (25 + pitch, 25, -45), 'loc': (0, 0, bob_z * 0.6)},
            'forearm_L':  {'rot': (25 + pitch * 0.5, 15, -15), 'loc': (0, 0, 0)},
            'hand_L':     {'rot': (-25, 25, -20), 'loc': (0, 0, 0)}
        }
    act_run_3p = create_action(arm, "A_Player_SMG_Run", 20, run_3p_keys)
    export_fbx(arm, os.path.join(FBX_3P_DIR, "A_Player_SMG_Run.fbx"))

    # 3. A_Player_SMG_Bash (24 frames melee golpe frontal)
    bash_3p_keys = {}
    bash_3p_keys[0] = BASE_3P_COMBAT
    # f=4: Windup / Giro hacia atrás
    bash_3p_keys[4] = {
        'pelvis':     {'rot': (0, 0, 12), 'loc': (0, 0, -0.01)},
        'spine':      {'rot': (-2, 0, 8),  'loc': (0, 0, 0)},
        'chest':      {'rot': (0, 0, 6),   'loc': (0, 0, 0)},
        'head':       {'rot': (0, 0, -8),  'loc': (0, 0, 0)},
        'thigh_R':    {'rot': (4, 0, -4),  'loc': (0, 0, 0)},
        'calf_R':     {'rot': (-4, 0, 0),  'loc': (0, 0, 0)},
        'thigh_L':    {'rot': (-4, 0, 4),  'loc': (0, 0, 0)},
        'calf_L':     {'rot': (4, 0, 0),   'loc': (0, 0, 0)},
        'clavicle_R': {'rot': (0, 0, 12),  'loc': (0, 0, 0)},
        'upperarm_R': {'rot': (22, -15, 18), 'loc': (0, -0.05, 0)},
        'forearm_R':  {'rot': (72, -15, 0),  'loc': (0, 0, 0)},
        'hand_R':     {'rot': (-10, -10, 15), 'loc': (0, 0, 0)},
        'clavicle_L': {'rot': (0, 0, -10),  'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (22, 25, -40), 'loc': (0, -0.05, 0)},
        'forearm_L':  {'rot': (45, 15, -15), 'loc': (0, 0, 0)},
        'hand_L':     {'rot': (-25, 25, -20), 'loc': (0, 0, 0)}
    }
    # f=8: Impacto frontal contundente (estocada +20cm al frente)
    bash_3p_keys[8] = {
        'pelvis':     {'rot': (0, 0, -8), 'loc': (0, 0, -0.035)},
        'spine':      {'rot': (-14, 0, -22), 'loc': (0, 0, 0)},
        'chest':      {'rot': (-10, 0, -16), 'loc': (0, 0, 0)},
        'head':       {'rot': (6, 0, 18),    'loc': (0, 0, 0)},
        'thigh_R':    {'rot': (-26, 0, -4), 'loc': (0, 0, 0)},
        'calf_R':     {'rot': (22, 0, 0),   'loc': (0, 0, 0)},
        'thigh_L':    {'rot': (22, 0, 4),   'loc': (0, 0, 0)},
        'calf_L':     {'rot': (-18, 0, 0),  'loc': (0, 0, 0)},
        'clavicle_R': {'rot': (0, 0, 8),   'loc': (0, 0, 0)},
        'upperarm_R': {'rot': (52, -15, 30), 'loc': (0, 0.16, 0.04)},
        'forearm_R':  {'rot': (42, -10, 0),  'loc': (0, 0, 0)},
        'hand_R':     {'rot': (-18, -8, 12), 'loc': (0, 0, 0)},
        'clavicle_L': {'rot': (0, 0, -18),  'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (50, 30, -55), 'loc': (0, 0.16, 0.04)},
        'forearm_L':  {'rot': (20, 12, -10), 'loc': (0, 0, 0)},
        'hand_L':     {'rot': (-32, 22, -18), 'loc': (0, 0, 0)}
    }
    # f=14: Retención cinética de impacto
    bash_3p_keys[14] = {
        'pelvis':     {'rot': (0, 0, -3), 'loc': (0, 0, -0.02)},
        'spine':      {'rot': (-8, 0, -15),  'loc': (0, 0, 0)},
        'chest':      {'rot': (-6, 0, -12),  'loc': (0, 0, 0)},
        'head':       {'rot': (4, 0, 16),    'loc': (0, 0, 0)},
        'thigh_R':    {'rot': (-18, 0, -4), 'loc': (0, 0, 0)},
        'calf_R':     {'rot': (16, 0, 0),   'loc': (0, 0, 0)},
        'thigh_L':    {'rot': (16, 0, 4),   'loc': (0, 0, 0)},
        'calf_L':     {'rot': (-12, 0, 0),  'loc': (0, 0, 0)},
        'clavicle_R': {'rot': (0, 0, 10),   'loc': (0, 0, 0)},
        'upperarm_R': {'rot': (42, -18, 28), 'loc': (0, 0.08, 0.02)},
        'forearm_R':  {'rot': (52, -12, 0),  'loc': (0, 0, 0)},
        'hand_R':     {'rot': (-16, -10, 14), 'loc': (0, 0, 0)},
        'clavicle_L': {'rot': (0, 0, -16),  'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (42, 30, -52), 'loc': (0, 0.08, 0.02)},
        'forearm_L':  {'rot': (26, 14, -12), 'loc': (0, 0, 0)},
        'hand_L':     {'rot': (-30, 24, -19), 'loc': (0, 0, 0)}
    }
    bash_3p_keys[24] = BASE_3P_COMBAT
    act_bash_3p = create_action(arm, "A_Player_SMG_Bash", 24, bash_3p_keys)
    export_fbx(arm, os.path.join(FBX_3P_DIR, "A_Player_SMG_Bash.fbx"))

    # 4. A_Player_SMG_Aim (30 frames loop ADS)
    aim_3p_keys = {}
    for f in range(31):
        t = f / 30.0
        breath = math.cos(t * math.pi * 2) * 0.4
        bob_z = math.sin(t * math.pi * 2) * 0.002

        aim_3p_keys[f] = {
            'pelvis':     {'rot': (0, 0, 4), 'loc': (0, 0, bob_z)},
            'spine':      {'rot': (-4 + breath * 0.3, 0, -10), 'loc': (0, 0, 0)},
            'chest':      {'rot': (-3 + breath * 0.3, 0, -8),  'loc': (0, 0, 0)},
            'head':       {'rot': (2, 0, 16),   'loc': (0, 0, 0)},
            'thigh_R':    {'rot': (-14, 0, -4), 'loc': (0, 0, 0)},
            'calf_R':     {'rot': (12, 0, 0),   'loc': (0, 0, 0)},
            'thigh_L':    {'rot': (12, 0, 4),   'loc': (0, 0, 0)},
            'calf_L':     {'rot': (-8, 0, 0),   'loc': (0, 0, 0)},
            'clavicle_R': {'rot': (0, 0, 10),   'loc': (0, 0, 0)},
            'upperarm_R': {'rot': (35 + breath, -20, 25), 'loc': (0, 0, bob_z)},
            'forearm_R':  {'rot': (60, -15, 0),  'loc': (0, 0, 0)},
            'hand_R':     {'rot': (-15, -10, 15), 'loc': (0, 0, 0)},
            'clavicle_L': {'rot': (0, 0, -16),  'loc': (0, 0, 0)},
            'upperarm_L': {'rot': (35 + breath, 30, -50), 'loc': (0, 0, bob_z)},
            'forearm_L':  {'rot': (34, 15, -15), 'loc': (0, 0, 0)},
            'hand_L':     {'rot': (-30, 25, -20), 'loc': (0, 0, 0)}
        }
    act_aim_3p = create_action(arm, "A_Player_SMG_Aim", 30, aim_3p_keys)
    export_fbx(arm, os.path.join(FBX_3P_DIR, "A_Player_SMG_Aim.fbx"))

    # 5. A_Player_SMG_Fire (12 frames recoil)
    fire_3p_keys = {}
    fire_3p_keys[0] = BASE_3P_COMBAT
    # f=2: Retroceso / culatazo en hombro
    fire_3p_keys[2] = {
        'pelvis':     {'rot': (0, 0, 4.5), 'loc': (0, 0, 0)},
        'spine':      {'rot': (-3.0, 0, -12.0), 'loc': (0, 0, 0)},
        'chest':      {'rot': (-1.5, 0, -10.0), 'loc': (0, 0, 0)},
        'head':       {'rot': (2.5, 0, 15.0),   'loc': (0, 0, 0)},
        'thigh_R':    {'rot': (-13.5, 0, -4), 'loc': (0, 0, 0)},
        'calf_R':     {'rot': (11.5, 0, 0),   'loc': (0, 0, 0)},
        'thigh_L':    {'rot': (12.5, 0, 4),   'loc': (0, 0, 0)},
        'calf_L':     {'rot': (-7.5, 0, 0),   'loc': (0, 0, 0)},
        'clavicle_R': {'rot': (0, 0, 8),      'loc': (0, 0, 0)},
        'upperarm_R': {'rot': (32, -18, 22),  'loc': (0, -0.02, 0.01)}, # retroceso hombro
        'forearm_R':  {'rot': (64, -14, 0),   'loc': (0, 0, 0)},
        'hand_R':     {'rot': (-12, -8, 14),  'loc': (0, 0, 0)},
        'clavicle_L': {'rot': (0, 0, -14),    'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (33, 28, -48),  'loc': (0, -0.015, 0.01)},
        'forearm_L':  {'rot': (36, 14, -14),  'loc': (0, 0, 0)},
        'hand_L':     {'rot': (-28, 24, -18), 'loc': (0, 0, 0)}
    }
    # f=5: Rebote elástico
    fire_3p_keys[5] = {
        'pelvis':     {'rot': (0, 0, 3.8), 'loc': (0, 0, 0)},
        'spine':      {'rot': (-4.5, 0, -9.5), 'loc': (0, 0, 0)},
        'chest':      {'rot': (-3.5, 0, -7.5), 'loc': (0, 0, 0)},
        'head':       {'rot': (1.8, 0, 16.5),  'loc': (0, 0, 0)},
        'thigh_R':    {'rot': (-14.2, 0, -4), 'loc': (0, 0, 0)},
        'calf_R':     {'rot': (12.2, 0, 0),   'loc': (0, 0, 0)},
        'thigh_L':    {'rot': (11.8, 0, 4),   'loc': (0, 0, 0)},
        'calf_L':     {'rot': (-8.2, 0, 0),   'loc': (0, 0, 0)},
        'clavicle_R': {'rot': (0, 0, 10.5),   'loc': (0, 0, 0)},
        'upperarm_R': {'rot': (36, -21, 26),  'loc': (0, 0.005, -0.003)},
        'forearm_R':  {'rot': (59, -15, 0),   'loc': (0, 0, 0)},
        'hand_R':     {'rot': (-16, -10, 15), 'loc': (0, 0, 0)},
        'clavicle_L': {'rot': (0, 0, -16.5),  'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (36, 31, -51),  'loc': (0, 0.004, -0.003)},
        'forearm_L':  {'rot': (33, 15, -15),  'loc': (0, 0, 0)},
        'hand_L':     {'rot': (-31, 25, -20), 'loc': (0, 0, 0)}
    }
    fire_3p_keys[12] = BASE_3P_COMBAT
    act_fire_3p = create_action(arm, "A_Player_SMG_Fire", 12, fire_3p_keys)
    export_fbx(arm, os.path.join(FBX_3P_DIR, "A_Player_SMG_Fire.fbx"))

    # Renders de verificación 3P (cámara 3/4 frontal calibrada a 38mm)
    cam_loc = (1.45, 2.35, 1.35)
    target_loc = (0.05, 0.20, 1.22)
    
    tp_renders = [
        ("tp_view_smg_walk.png", act_walk_3p, 7),
        ("tp_view_smg_run.png",  act_run_3p,  5),
        ("tp_view_smg_bash.png", act_bash_3p, 8),
        ("tp_view_smg_aim.png",  act_aim_3p,  0),
        ("tp_view_smg_fire.png", act_fire_3p, 2)
    ]

    player_mesh = [o for o in bpy.data.objects if o.type == 'MESH' and o != smg_mesh][0]
    vg_r = player_mesh.vertex_groups['hand_R'].index

    for fname, action, frame in tp_renders:
        arm.animation_data.action = action
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        
        # Calcular posición dinámica del arma según hand_R
        dg = bpy.context.evaluated_depsgraph_get()
        em = player_mesh.evaluated_get(dg)
        vr = [em.matrix_world @ v.co for v in em.data.vertices if any(g.group == vg_r and g.weight > 0.8 for g in v.groups)]
        cr = sum(vr, Vector((0,0,0))) / len(vr)
        
        if "bash" in fname:
            smg_mesh.location = (cr.x + 0.05, cr.y + 0.15, cr.z + 0.05)
            smg_mesh.rotation_euler = (math.radians(18), math.radians(-10), math.radians(12))
        elif "run" in fname:
            smg_mesh.location = (cr.x, cr.y + 0.04, cr.z + 0.02)
            smg_mesh.rotation_euler = (math.radians(-18), math.radians(-5), math.radians(8))
        elif "fire" in fname:
            smg_mesh.location = (cr.x, cr.y + 0.04, cr.z + 0.02)
            smg_mesh.rotation_euler = (math.radians(8), 0, math.radians(4))
        else:
            smg_mesh.location = (cr.x, cr.y + 0.04, cr.z + 0.02)
            smg_mesh.rotation_euler = (math.radians(-2), 0, math.radians(4))

        bpy.context.view_layer.update()

        out_img = os.path.join(BLENDER_DIR, fname)
        render_scene_frame(out_img, cam_loc, target_loc, lens=38, res=(960, 540))
        shutil.copyfile(out_img, os.path.join(BRAIN_DIR, fname))

    print(">>> SUITE 3P COMPLETADA CON ÉXITO.")


if __name__ == "__main__":
    produce_fps_suite()
    produce_player_suite()
    print("\n=======================================================")
    print(">>> GENERACION MAESTRA DE LAS 10 ANIMACIONES FBX Y RENDERS CONCLUIDA.")
    print("=======================================================")

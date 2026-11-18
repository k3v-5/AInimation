"""generate_smg_suite_animations.py
Suite completa de animaciones de combate para el Subfusil Láser (SM_Wep_PhaseSMG)
en Primera Persona (SK_FPS_Arms) y Tercera Persona (SK_Player).

Animaciones generadas:
1. Walk (Caminar - 30 frames loop)
2. Run  (Correr - 20 frames loop)
3. Bash (Golpear con el arma / Melee - 24 frames one-shot)
4. Aim  (Apuntar / ADS - 30 frames loop)
5. Fire (Disparar / Recoil - 12 frames one-shot)

Genera los 10 archivos FBX canónicos y los mosaicos de validación visual de 5 poses para 1P y 3P.
Cumple estrictamente las Reglas 1, 4, 5, 8 y 11 de AGENTS.md.
"""

import os
import sys
import math
import shutil
import bpy
from mathutils import Vector, Euler, Matrix
try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

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
    
    # Eliminar acción previa con el mismo nombre si existe
    existing = bpy.data.actions.get(name)
    if existing:
        bpy.data.actions.remove(existing)
    
    act = bpy.data.actions.new(name=name)
    act.use_fake_user = True
    arm_obj.animation_data.action = act
    
    # Asegurar modo XYZ en pose bones
    for pb in arm_obj.pose.bones:
        pb.rotation_mode = 'XYZ'
        pb.location = (0, 0, 0)
        pb.rotation_euler = (0, 0, 0)

    # Insertar claves
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
        
        # Keyframear todos los huesos en este frame para solidez de take FBX
        for pb in arm_obj.pose.bones:
            pb.keyframe_insert("rotation_euler", frame=f)
            pb.keyframe_insert("location", frame=f)

    # Ajustar interpolación de fcurves
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


def render_scene_frame(out_path, cam_pos, target_pos, lens=30, res=(960, 540)):
    """Renderiza un frame de la pose actual con iluminación de estudio calibrada."""
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

    target = bpy.data.objects.new("RenderCamTarget", None)
    target.location = target_pos
    scene.collection.objects.link(target)
    
    tt = cam_obj.constraints.new('TRACK_TO')
    tt.target = target
    tt.track_axis = 'TRACK_NEGATIVE_Z'
    tt.up_axis = 'UP_Y'

    scene.render.filepath = out_path
    bpy.ops.render.render(write_still=True)

    bpy.data.objects.remove(cam_obj, do_unlink=True)
    bpy.data.objects.remove(target, do_unlink=True)
    bpy.data.cameras.remove(cam_data, do_unlink=True)
    print(f"Rendered: {out_path}")


# ==============================================================================
# 1. PARTE 1: ANIMACIONES DE PRIMERA PERSONA (FPS ARMS)
# ==============================================================================
def produce_fps_suite():
    print("\n=======================================================")
    print(">>> PRODUCIENDO SUITE FPS (SK_FPS_Arms)")
    print("=======================================================")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene

    # 1. Importar esqueleto y brazos FPS
    bpy.ops.import_scene.fbx(filepath=FPS_FBX)
    arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
    arm.name = "ARM_FPS_Arms"
    fps_mesh = [o for o in bpy.data.objects if o.type == 'MESH'][0]

    # Ocultar la pistola original desplazando sus vértices lejos
    for v in fps_mesh.data.vertices:
        for g in v.groups:
            if fps_mesh.vertex_groups[g.group].name in ('weapon', 'cell'):
                v.co = Vector((0, 0, -100))
                break

    # 2. Cargar y unir la malla del Subfusil Tommy Gun
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

    # Acoplar al hueso weapon
    c = smg_mesh.constraints.new('CHILD_OF')
    c.target = arm
    c.subtarget = 'weapon'
    c.inverse_matrix = Matrix.Translation(Vector((0.0, 0.046, 0.022)))

    # Iluminación de estudio para FPS
    l1_data = bpy.data.lights.new("FPS_Key", 'AREA')
    l1_data.energy = 600
    l1_data.size = 2.5
    l1 = bpy.data.objects.new("FPS_Key", l1_data)
    l1.location = (1.2, -0.1, 0.9)
    scene.collection.objects.link(l1)

    l2_data = bpy.data.lights.new("FPS_Rim", 'AREA')
    l2_data.energy = 480
    l2_data.size = 3.0
    l2_data.color = (0.75, 0.2, 1.0)
    l2 = bpy.data.objects.new("FPS_Rim", l2_data)
    l2.location = (-1.2, -0.6, 0.7)
    scene.collection.objects.link(l2)

    l3_data = bpy.data.lights.new("FPS_Fill", 'AREA')
    l3_data.energy = 240
    l3_data.size = 2.5
    l3 = bpy.data.objects.new("FPS_Fill", l3_data)
    l3.location = (0.1, -1.2, 0.4)
    scene.collection.objects.link(l3)

    # -------------------------------------------------------------
    # Poses Base para FPS
    # -------------------------------------------------------------
    # Stance Base (Caminar / Patrol)
    BASE_WALK = {
        'upperarm_R': {'rot': (-14, 5, -2), 'loc': (0, 0, 0)},
        'forearm_R':  {'rot': (-20, 4, 0),  'loc': (0, 0, 0)},
        'hand_R':     {'rot': (2, -4, 2),   'loc': (0, 0, 0)},
        'weapon':     {'rot': (-14, 8, -4), 'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (-4, -16, 38), 'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (-44, 16, -14), 'loc': (0, 0, 0)},
        'hand_L':     {'rot': (18, -6, 24), 'loc': (0.06, -0.08, 0.02)}
    }

    # Stance Sprint (Low Ready rápido)
    BASE_RUN = {
        'upperarm_R': {'rot': (-24, 8, -6), 'loc': (0.01, 0.04, -0.04)},
        'forearm_R':  {'rot': (-32, 6, 2),  'loc': (0, 0, 0)},
        'hand_R':     {'rot': (4, -6, 4),   'loc': (0, 0, 0)},
        'weapon':     {'rot': (-28, 12, -8), 'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (-12, -18, 42), 'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (-52, 18, -16), 'loc': (0, 0, 0)},
        'hand_L':     {'rot': (22, -8, 28), 'loc': (0.06, -0.06, 0.01)}
    }

    # Stance Aim (ADS - Centrado óptico)
    BASE_AIM = {
        'upperarm_R': {'rot': (-8, 1, -1), 'loc': (-0.088, 0.02, 0.048)},
        'forearm_R':  {'rot': (-12, 1, 0), 'loc': (0, 0, 0)},
        'hand_R':     {'rot': (0, -1, 0),  'loc': (0, 0, 0)},
        'weapon':     {'rot': (0, 0, 0),   'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (2, -12, 32), 'loc': (-0.02, 0, 0.02)},
        'forearm_L':  {'rot': (-38, 12, -10), 'loc': (0, 0, 0)},
        'hand_L':     {'rot': (14, -4, 20), 'loc': (0.05, -0.09, 0.03)}
    }

    # 1. A_FPS_SMG_Walk (30 frames loop)
    walk_keys = {}
    for f in range(31):
        t = f / 30.0
        # Oscilación dual armónica de pasos
        bob_z = math.sin(t * math.pi * 4) * 0.012
        sway_x = math.sin(t * math.pi * 2) * 0.008
        roll = math.sin(t * math.pi * 2) * 1.5
        pitch = math.cos(t * math.pi * 4) * 1.0

        walk_keys[f] = {
            'upperarm_R': {'rot': (-14 + pitch, 5, -2 + roll), 'loc': (sway_x, 0, bob_z)},
            'forearm_R':  {'rot': (-20 + pitch * 0.5, 4, 0),  'loc': (0, 0, 0)},
            'hand_R':     {'rot': (2, -4, 2),   'loc': (0, 0, 0)},
            'weapon':     {'rot': (-14 + pitch * 1.2, 8, -4 + roll), 'loc': (0, 0, 0)},
            'upperarm_L': {'rot': (-4 + pitch, -16, 38 + roll), 'loc': (sway_x, 0, bob_z)},
            'forearm_L':  {'rot': (-44 + pitch * 0.5, 16, -14), 'loc': (0, 0, 0)},
            'hand_L':     {'rot': (18, -6, 24), 'loc': (0.06 + sway_x * 0.5, -0.08, 0.02 + bob_z * 0.5)}
        }
    act_walk = create_action(arm, "A_FPS_SMG_Walk", 30, walk_keys)
    export_fbx(arm, os.path.join(FBX_FPS_DIR, "A_FPS_SMG_Walk.fbx"))

    # 2. A_FPS_SMG_Run (20 frames loop)
    run_keys = {}
    for f in range(21):
        t = f / 20.0
        bob_z = math.sin(t * math.pi * 4) * 0.028
        sway_x = math.sin(t * math.pi * 2) * 0.018
        roll = math.sin(t * math.pi * 2) * 3.8
        pitch = math.cos(t * math.pi * 4) * 2.8

        run_keys[f] = {
            'upperarm_R': {'rot': (-24 + pitch, 8, -6 + roll), 'loc': (0.01 + sway_x, 0.04, -0.04 + bob_z)},
            'forearm_R':  {'rot': (-32 + pitch * 0.6, 6, 2),  'loc': (0, 0, 0)},
            'hand_R':     {'rot': (4, -6, 4),   'loc': (0, 0, 0)},
            'weapon':     {'rot': (-28 + pitch * 1.5, 12, -8 + roll), 'loc': (0, 0, 0)},
            'upperarm_L': {'rot': (-12 + pitch, -18, 42 + roll), 'loc': (sway_x, 0.04, bob_z)},
            'forearm_L':  {'rot': (-52 + pitch * 0.6, 18, -16), 'loc': (0, 0, 0)},
            'hand_L':     {'rot': (22, -8, 28), 'loc': (0.06 + sway_x * 0.5, -0.06, 0.01 + bob_z * 0.5)}
        }
    act_run = create_action(arm, "A_FPS_SMG_Run", 20, run_keys)
    export_fbx(arm, os.path.join(FBX_FPS_DIR, "A_FPS_SMG_Run.fbx"))

    # 3. A_FPS_SMG_Bash (24 frames melee golpe)
    bash_keys = {}
    bash_keys[0] = BASE_WALK
    # f=4: Carga / Windup hacia atrás
    bash_keys[4] = {
        'upperarm_R': {'rot': (-6, 8, 4), 'loc': (0.02, 0.08, -0.02)},
        'forearm_R':  {'rot': (-38, 4, -4), 'loc': (0, 0, 0)},
        'hand_R':     {'rot': (6, -8, 6),  'loc': (0, 0, 0)},
        'weapon':     {'rot': (8, 14, -2), 'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (6, -12, 45), 'loc': (0.02, 0.06, -0.01)},
        'forearm_L':  {'rot': (-58, 20, -18), 'loc': (0, 0, 0)},
        'hand_L':     {'rot': (24, -8, 30), 'loc': (0.07, -0.04, 0.02)}
    }
    # f=8: Impacto / Estocada frontal devastadora (+20cm en Y)
    bash_keys[8] = {
        'upperarm_R': {'rot': (-36, 2, -12), 'loc': (-0.03, -0.20, 0.04)},
        'forearm_R':  {'rot': (-4, 2, 4),    'loc': (0, 0, 0)},
        'hand_R':     {'rot': (-4, 2, -2),   'loc': (0, 0, 0)},
        'weapon':     {'rot': (-8, 4, -4),   'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (-28, -8, 24), 'loc': (-0.02, -0.18, 0.05)},
        'forearm_L':  {'rot': (-18, 8, -6),  'loc': (0, 0, 0)},
        'hand_L':     {'rot': (8, -2, 14),   'loc': (0.04, -0.14, 0.04)}
    }
    # f=12: Retención cinética y temblor
    bash_keys[12] = {
        'upperarm_R': {'rot': (-34, 3, -10), 'loc': (-0.02, -0.16, 0.03)},
        'forearm_R':  {'rot': (-8, 3, 2),    'loc': (0, 0, 0)},
        'hand_R':     {'rot': (-2, 0, 0),    'loc': (0, 0, 0)},
        'weapon':     {'rot': (-6, 5, -3),   'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (-24, -10, 28), 'loc': (-0.01, -0.14, 0.04)},
        'forearm_L':  {'rot': (-24, 10, -8),  'loc': (0, 0, 0)},
        'hand_L':     {'rot': (10, -4, 16),  'loc': (0.05, -0.12, 0.03)}
    }
    # f=18: Retracción
    bash_keys[18] = {
        'upperarm_R': {'rot': (-18, 5, -4), 'loc': (0.01, -0.04, 0.01)},
        'forearm_R':  {'rot': (-16, 4, 0),  'loc': (0, 0, 0)},
        'hand_R':     {'rot': (0, -3, 1),   'loc': (0, 0, 0)},
        'weapon':     {'rot': (-12, 7, -3), 'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (-8, -14, 34), 'loc': (0.01, -0.04, 0.01)},
        'forearm_L':  {'rot': (-38, 14, -12), 'loc': (0, 0, 0)},
        'hand_L':     {'rot': (15, -5, 20), 'loc': (0.05, -0.09, 0.02)}
    }
    bash_keys[24] = BASE_WALK
    act_bash = create_action(arm, "A_FPS_SMG_Bash", 24, bash_keys)
    export_fbx(arm, os.path.join(FBX_FPS_DIR, "A_FPS_SMG_Bash.fbx"))

    # 4. A_FPS_SMG_Aim (30 frames loop ADS)
    aim_keys = {}
    for f in range(31):
        t = f / 30.0
        breath_z = math.sin(t * math.pi * 2) * 0.0008
        breath_pitch = math.cos(t * math.pi * 2) * 0.15

        aim_keys[f] = {
            'upperarm_R': {'rot': (-8 + breath_pitch, 1, -1), 'loc': (-0.088, 0.02, 0.048 + breath_z)},
            'forearm_R':  {'rot': (-12, 1, 0), 'loc': (0, 0, 0)},
            'hand_R':     {'rot': (0, -1, 0),  'loc': (0, 0, 0)},
            'weapon':     {'rot': (breath_pitch * 0.8, 0, 0), 'loc': (0, 0, 0)},
            'upperarm_L': {'rot': (2 + breath_pitch, -12, 32), 'loc': (-0.02, 0, 0.02 + breath_z)},
            'forearm_L':  {'rot': (-38, 12, -10), 'loc': (0, 0, 0)},
            'hand_L':     {'rot': (14, -4, 20), 'loc': (0.05, -0.09, 0.03 + breath_z * 0.5)}
        }
    act_aim = create_action(arm, "A_FPS_SMG_Aim", 30, aim_keys)
    export_fbx(arm, os.path.join(FBX_FPS_DIR, "A_FPS_SMG_Aim.fbx"))

    # 5. A_FPS_SMG_Fire (12 frames recoil)
    fire_keys = {}
    fire_keys[0] = BASE_AIM
    # f=2: Culatazo máximo / Retroceso violento
    fire_keys[2] = {
        'upperarm_R': {'rot': (-4, 2, -0.5), 'loc': (-0.088, 0.056, 0.058)},
        'forearm_R':  {'rot': (-8, 2, 0.5),  'loc': (0, 0, 0)},
        'hand_R':     {'rot': (1, -1, 0.5),  'loc': (0, 0, 0)},
        'weapon':     {'rot': (4.2, 0.8, -0.5), 'loc': (0, 0.036, 0.012)},
        'upperarm_L': {'rot': (5, -10, 31), 'loc': (-0.02, 0.034, 0.028)},
        'forearm_L':  {'rot': (-34, 14, -8), 'loc': (0, 0, 0)},
        'hand_L':     {'rot': (16, -3, 21), 'loc': (0.05, -0.06, 0.04)}
    }
    # f=5: Rebote elástico
    fire_keys[5] = {
        'upperarm_R': {'rot': (-9, 0.5, -1.2), 'loc': (-0.088, 0.012, 0.045)},
        'forearm_R':  {'rot': (-13, 0.5, 0), 'loc': (0, 0, 0)},
        'hand_R':     {'rot': (-0.5, -1, 0), 'loc': (0, 0, 0)},
        'weapon':     {'rot': (-1.2, -0.2, 0.2), 'loc': (0, -0.008, -0.003)},
        'upperarm_L': {'rot': (1, -13, 32.5), 'loc': (-0.02, -0.008, 0.018)},
        'forearm_L':  {'rot': (-39, 11, -11), 'loc': (0, 0, 0)},
        'hand_L':     {'rot': (13, -4, 19), 'loc': (0.05, -0.10, 0.027)}
    }
    # f=8: Reestabilización
    fire_keys[8] = {
        'upperarm_R': {'rot': (-8.2, 1, -1), 'loc': (-0.088, 0.018, 0.047)},
        'forearm_R':  {'rot': (-12.2, 1, 0), 'loc': (0, 0, 0)},
        'hand_R':     {'rot': (0, -1, 0),  'loc': (0, 0, 0)},
        'weapon':     {'rot': (0.4, 0, 0), 'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (1.8, -12, 32), 'loc': (-0.02, 0, 0.02)},
        'forearm_L':  {'rot': (-38.2, 12, -10), 'loc': (0, 0, 0)},
        'hand_L':     {'rot': (14, -4, 20), 'loc': (0.05, -0.09, 0.03)}
    }
    fire_keys[12] = BASE_AIM
    act_fire = create_action(arm, "A_FPS_SMG_Fire", 12, fire_keys)
    export_fbx(arm, os.path.join(FBX_FPS_DIR, "A_FPS_SMG_Fire.fbx"))

    # -------------------------------------------------------------
    # Renderizado de Frames de Verificación FPS
    # -------------------------------------------------------------
    cam_loc = (0.02, 0.38, 0.04)
    target_loc = (0.05, -0.45, -0.16)
    
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
        render_scene_frame(out_img, cam_loc, target_loc, lens=26, res=(960, 540))
        shutil.copyfile(out_img, os.path.join(BRAIN_DIR, fname))

    print(">>> SUITE FPS COMPLETADA CON ÉXITO.")


# ==============================================================================
# 2. PARTE 2: ANIMACIONES DE TERCERA PERSONA (SK_PLAYER - 22 HUESOS)
# ==============================================================================
def produce_player_suite():
    print("\n=======================================================")
    print(">>> PRODUCIENDO SUITE 3P (SK_Player - 22 Huesos)")
    print("=======================================================")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene

    # 1. Importar esqueleto y jugador canónico
    bpy.ops.import_scene.fbx(filepath=PLAYER_FBX)
    arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
    arm.name = "ARM_Player"

    # 2. Cargar y unir la malla del Subfusil Tommy Gun
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
    smg_mesh.name = "SM_Wep_PhaseSMG_3P_Ref"

    # En 3P, el arma se emparenta rigidamente a hand_R con offset calibrado
    c = smg_mesh.constraints.new('CHILD_OF')
    c.target = arm
    c.subtarget = 'hand_R'
    # Transform calibrado para que la empuñadura trasera coincida con la palma de hand_R
    c.inverse_matrix = Matrix.Translation(Vector((0.0, 0.05, 0.02)))

    # Iluminación de estudio para 3P
    l1_data = bpy.data.lights.new("3P_Key", 'POINT')
    l1_data.energy = 950
    l1 = bpy.data.objects.new("3P_Key", l1_data)
    l1.location = (2.0, 1.8, 2.4)
    scene.collection.objects.link(l1)

    l2_data = bpy.data.lights.new("3P_Rim", 'POINT')
    l2_data.energy = 750
    l2_data.color = (0.75, 0.2, 1.0)
    l2 = bpy.data.objects.new("3P_Rim", l2_data)
    l2.location = (-1.8, -1.8, 2.0)
    scene.collection.objects.link(l2)

    l3_data = bpy.data.lights.new("3P_Fill", 'POINT')
    l3_data.energy = 400
    l3 = bpy.data.objects.new("3P_Fill", l3_data)
    l3.location = (-1.5, 2.0, 1.2)
    scene.collection.objects.link(l3)

    # -------------------------------------------------------------
    # Poses Base para 3P
    # -------------------------------------------------------------
    # 1. A_Player_SMG_Walk (30 frames loop)
    # Ciclo de marcha completo con piernas alternadas y agarre táctico del arma
    walk_3p_keys = {}
    
    def get_walk_pose(t_stride, leg_fwd_R):
        # t_stride: 0 a 1 para un semi-paso
        # rotX positivo = adelante en SK_Player
        thigh_fwd = math.sin(t_stride * math.pi) * 28.0 * (1 if leg_fwd_R else -1)
        thigh_back = -math.sin(t_stride * math.pi) * 24.0 * (1 if leg_fwd_R else -1)
        knee_bend = -abs(math.sin(t_stride * math.pi)) * 32.0
        pelvis_z = -abs(math.sin(t_stride * math.pi * 2)) * 0.024
        spine_lean = 4.0
        spine_sway = math.sin(t_stride * math.pi) * 2.5 * (1 if leg_fwd_R else -1)

        return {
            'pelvis':     {'rot': (0, 0, spine_sway * 0.5), 'loc': (0, 0, pelvis_z)},
            'spine':      {'rot': (spine_lean, 0, -spine_sway), 'loc': (0, 0, 0)},
            'chest':      {'rot': (2, 0, -spine_sway * 0.6),   'loc': (0, 0, 0)},
            'head':       {'rot': (0, 0, spine_sway * 0.4),    'loc': (0, 0, 0)},
            'thigh_R':    {'rot': (thigh_fwd if leg_fwd_R else thigh_back, 0, 4), 'loc': (0, 0, 0)},
            'calf_R':     {'rot': (knee_bend if not leg_fwd_R else 6, 0, 0),      'loc': (0, 0, 0)},
            'thigh_L':    {'rot': (thigh_back if leg_fwd_R else thigh_fwd, 0, -4), 'loc': (0, 0, 0)},
            'calf_L':     {'rot': (knee_bend if leg_fwd_R else 6, 0, 0),          'loc': (0, 0, 0)},
            # Brazos sosteniendo el subfusil en guardia táctica frontal
            'clavicle_R': {'rot': (4, 0, 6), 'loc': (0, 0, 0)},
            'upperarm_R': {'rot': (42, -6, 32), 'loc': (0, 0, 0)},
            'forearm_R':  {'rot': (38, 8, 8),   'loc': (0, 0, 0)},
            'hand_R':     {'rot': (-8, 14, 12), 'loc': (0, 0, 0)},
            'clavicle_L': {'rot': (6, 0, -10), 'loc': (0, 0, 0)},
            'upperarm_L': {'rot': (54, 10, -28), 'loc': (0, 0, 0)},
            'forearm_L':  {'rot': (32, -12, -10), 'loc': (0, 0, 0)},
            'hand_L':     {'rot': (14, -8, -20), 'loc': (0, 0, 0)}
        }

    for f in range(31):
        if f <= 15:
            walk_3p_keys[f] = get_walk_pose(f / 15.0, leg_fwd_R=True)
        else:
            walk_3p_keys[f] = get_walk_pose((f - 15) / 15.0, leg_fwd_R=False)

    act_walk_3p = create_action(arm, "A_Player_SMG_Walk", 30, walk_3p_keys)
    export_fbx(arm, os.path.join(FBX_3P_DIR, "A_Player_SMG_Walk.fbx"))

    # 2. A_Player_SMG_Run (20 frames loop sprint)
    run_3p_keys = {}
    for f in range(21):
        t = f / 20.0
        leg_fwd = math.sin(t * math.pi * 2) * 44.0
        knee_bend = -abs(math.sin(t * math.pi * 2)) * 65.0
        pelvis_z = -abs(math.sin(t * math.pi * 2)) * 0.045
        spine_lean = 12.0
        sway = math.sin(t * math.pi * 2) * 4.0

        run_3p_keys[f] = {
            'pelvis':     {'rot': (0, 0, sway * 0.4), 'loc': (0, 0, pelvis_z)},
            'spine':      {'rot': (spine_lean, 0, -sway), 'loc': (0, 0, 0)},
            'chest':      {'rot': (4, 0, -sway * 0.6),    'loc': (0, 0, 0)},
            'head':       {'rot': (-4, 0, sway * 0.5),    'loc': (0, 0, 0)},
            'thigh_R':    {'rot': (leg_fwd, 0, 6),        'loc': (0, 0, 0)},
            'calf_R':     {'rot': (knee_bend if leg_fwd < 0 else 8, 0, 0), 'loc': (0, 0, 0)},
            'thigh_L':    {'rot': (-leg_fwd, 0, -6),      'loc': (0, 0, 0)},
            'calf_L':     {'rot': (knee_bend if leg_fwd > 0 else 8, 0, 0), 'loc': (0, 0, 0)},
            # Arma en Low Ready ceñida en carrera
            'clavicle_R': {'rot': (6, 0, 8), 'loc': (0, 0, 0)},
            'upperarm_R': {'rot': (32, -4, 28), 'loc': (0, 0, 0)},
            'forearm_R':  {'rot': (48, 6, 6),   'loc': (0, 0, 0)},
            'hand_R':     {'rot': (-6, 10, 8),  'loc': (0, 0, 0)},
            'clavicle_L': {'rot': (8, 0, -14), 'loc': (0, 0, 0)},
            'upperarm_L': {'rot': (46, 8, -24), 'loc': (0, 0, 0)},
            'forearm_L':  {'rot': (42, -10, -8), 'loc': (0, 0, 0)},
            'hand_L':     {'rot': (12, -6, -16), 'loc': (0, 0, 0)}
        }
    act_run_3p = create_action(arm, "A_Player_SMG_Run", 20, run_3p_keys)
    export_fbx(arm, os.path.join(FBX_3P_DIR, "A_Player_SMG_Run.fbx"))

    # 3. A_Player_SMG_Bash (24 frames melee golpe)
    bash_3p_keys = {}
    BASE_COMBAT_3P = {
        'pelvis':     {'rot': (0, 0, -6), 'loc': (0, 0, 0)},
        'spine':      {'rot': (4, 0, -12), 'loc': (0, 0, 0)},
        'chest':      {'rot': (2, 0, -8),  'loc': (0, 0, 0)},
        'head':       {'rot': (-2, 0, 6),  'loc': (0, 0, 0)},
        'thigh_R':    {'rot': (-14, 0, 8), 'loc': (0, 0, 0)},
        'calf_R':     {'rot': (-18, 0, 0), 'loc': (0, 0, 0)},
        'thigh_L':    {'rot': (16, 0, -6), 'loc': (0, 0, 0)},
        'calf_L':     {'rot': (-8, 0, 0),  'loc': (0, 0, 0)},
        'clavicle_R': {'rot': (4, 0, 8), 'loc': (0, 0, 0)},
        'upperarm_R': {'rot': (52, -8, 38), 'loc': (0, 0, 0)},
        'forearm_R':  {'rot': (44, 12, 10), 'loc': (0, 0, 0)},
        'hand_R':     {'rot': (-12, 18, 15), 'loc': (0, 0, 0)},
        'clavicle_L': {'rot': (6, 0, -12), 'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (64, 12, -34), 'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (38, -16, -12), 'loc': (0, 0, 0)},
        'hand_L':     {'rot': (18, -12, -25), 'loc': (0, 0, 0)}
    }
    bash_3p_keys[0] = BASE_COMBAT_3P
    # f=4: Windup / Giro hacia atrás del torso
    bash_3p_keys[4] = {
        'pelvis':     {'rot': (0, 0, -14), 'loc': (0, 0, -0.01)},
        'spine':      {'rot': (2, 0, -22), 'loc': (0, 0, 0)},
        'chest':      {'rot': (0, 0, -18), 'loc': (0, 0, 0)},
        'head':       {'rot': (0, 0, 18),  'loc': (0, 0, 0)},
        'thigh_R':    {'rot': (-22, 0, 10), 'loc': (0, 0, 0)},
        'calf_R':     {'rot': (-24, 0, 0),  'loc': (0, 0, 0)},
        'thigh_L':    {'rot': (12, 0, -8),  'loc': (0, 0, 0)},
        'calf_L':     {'rot': (-14, 0, 0),  'loc': (0, 0, 0)},
        'clavicle_R': {'rot': (2, 0, 4), 'loc': (0, 0, 0)},
        'upperarm_R': {'rot': (38, -4, 28), 'loc': (0, 0, 0)},
        'forearm_R':  {'rot': (58, 14, 14), 'loc': (0, 0, 0)},
        'hand_R':     {'rot': (-6, 14, 10), 'loc': (0, 0, 0)},
        'clavicle_L': {'rot': (4, 0, -8), 'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (48, 8, -26), 'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (52, -18, -16), 'loc': (0, 0, 0)},
        'hand_L':     {'rot': (12, -8, -18), 'loc': (0, 0, 0)}
    }
    # f=8: Embestida frontal demoledora
    bash_3p_keys[8] = {
        'pelvis':     {'rot': (0, 0, 4), 'loc': (0, 0, -0.035)},
        'spine':      {'rot': (16, 0, 8), 'loc': (0, 0, 0)},
        'chest':      {'rot': (12, 0, 6), 'loc': (0, 0, 0)},
        'head':       {'rot': (-6, 0, -8), 'loc': (0, 0, 0)},
        'thigh_R':    {'rot': (28, 0, 6),  'loc': (0, 0, 0)},
        'calf_R':     {'rot': (-10, 0, 0), 'loc': (0, 0, 0)},
        'thigh_L':    {'rot': (-26, 0, -8), 'loc': (0, 0, 0)},
        'calf_L':     {'rot': (-32, 0, 0),  'loc': (0, 0, 0)},
        'clavicle_R': {'rot': (8, 0, 14), 'loc': (0, 0, 0)},
        'upperarm_R': {'rot': (74, -12, 42), 'loc': (0, 0, 0)},
        'forearm_R':  {'rot': (22, 8, 6),    'loc': (0, 0, 0)},
        'hand_R':     {'rot': (-16, 20, 18), 'loc': (0, 0, 0)},
        'clavicle_L': {'rot': (12, 0, -18), 'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (82, 16, -38), 'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (20, -12, -8), 'loc': (0, 0, 0)},
        'hand_L':     {'rot': (22, -14, -28), 'loc': (0, 0, 0)}
    }
    # f=14: Retroceso de impacto
    bash_3p_keys[14] = {
        'pelvis':     {'rot': (0, 0, 0), 'loc': (0, 0, -0.02)},
        'spine':      {'rot': (10, 0, -4), 'loc': (0, 0, 0)},
        'chest':      {'rot': (8, 0, -3),  'loc': (0, 0, 0)},
        'head':       {'rot': (-4, 0, 0),  'loc': (0, 0, 0)},
        'thigh_R':    {'rot': (18, 0, 6),  'loc': (0, 0, 0)},
        'calf_R':     {'rot': (-12, 0, 0), 'loc': (0, 0, 0)},
        'thigh_L':    {'rot': (-20, 0, -7), 'loc': (0, 0, 0)},
        'calf_L':     {'rot': (-22, 0, 0),  'loc': (0, 0, 0)},
        'clavicle_R': {'rot': (6, 0, 10), 'loc': (0, 0, 0)},
        'upperarm_R': {'rot': (62, -10, 40), 'loc': (0, 0, 0)},
        'forearm_R':  {'rot': (34, 10, 8),   'loc': (0, 0, 0)},
        'hand_R':     {'rot': (-14, 19, 16), 'loc': (0, 0, 0)},
        'clavicle_L': {'rot': (8, 0, -14), 'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (72, 14, -36), 'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (28, -14, -10), 'loc': (0, 0, 0)},
        'hand_L':     {'rot': (20, -13, -26), 'loc': (0, 0, 0)}
    }
    bash_3p_keys[24] = BASE_COMBAT_3P
    act_bash_3p = create_action(arm, "A_Player_SMG_Bash", 24, bash_3p_keys)
    export_fbx(arm, os.path.join(FBX_3P_DIR, "A_Player_SMG_Bash.fbx"))

    # 4. A_Player_SMG_Aim (30 frames loop)
    aim_3p_keys = {}
    for f in range(31):
        t = f / 30.0
        breath_pitch = math.cos(t * math.pi * 2) * 0.8
        breath_z = math.sin(t * math.pi * 2) * 0.003

        aim_3p_keys[f] = {
            'pelvis':     {'rot': (0, 0, -6), 'loc': (0, 0, breath_z)},
            'spine':      {'rot': (4 + breath_pitch * 0.5, 0, -12), 'loc': (0, 0, 0)},
            'chest':      {'rot': (2 + breath_pitch * 0.5, 0, -8),  'loc': (0, 0, 0)},
            'head':       {'rot': (-2, 0, 6),  'loc': (0, 0, 0)},
            'thigh_R':    {'rot': (-14, 0, 8), 'loc': (0, 0, 0)},
            'calf_R':     {'rot': (-18, 0, 0), 'loc': (0, 0, 0)},
            'thigh_L':    {'rot': (16, 0, -6), 'loc': (0, 0, 0)},
            'calf_L':     {'rot': (-8, 0, 0),  'loc': (0, 0, 0)},
            'clavicle_R': {'rot': (4, 0, 8), 'loc': (0, 0, 0)},
            'upperarm_R': {'rot': (52 + breath_pitch, -8, 38), 'loc': (0, 0, 0)},
            'forearm_R':  {'rot': (44, 12, 10), 'loc': (0, 0, 0)},
            'hand_R':     {'rot': (-12, 18, 15), 'loc': (0, 0, 0)},
            'clavicle_L': {'rot': (6, 0, -12), 'loc': (0, 0, 0)},
            'upperarm_L': {'rot': (64 + breath_pitch, 12, -34), 'loc': (0, 0, 0)},
            'forearm_L':  {'rot': (38, -16, -12), 'loc': (0, 0, 0)},
            'hand_L':     {'rot': (18, -12, -25), 'loc': (0, 0, 0)}
        }
    act_aim_3p = create_action(arm, "A_Player_SMG_Aim", 30, aim_3p_keys)
    export_fbx(arm, os.path.join(FBX_3P_DIR, "A_Player_SMG_Aim.fbx"))

    # 5. A_Player_SMG_Fire (12 frames recoil)
    fire_3p_keys = {}
    fire_3p_keys[0] = BASE_COMBAT_3P
    # f=2: Retroceso / Hombro derecho empujado atrás
    fire_3p_keys[2] = {
        'pelvis':     {'rot': (0, 0, -7), 'loc': (0, 0, 0)},
        'spine':      {'rot': (1, 0, -15), 'loc': (0, 0, 0)},
        'chest':      {'rot': (-1, 0, -12), 'loc': (0, 0, 0)},
        'head':       {'rot': (0, 0, 10),  'loc': (0, 0, 0)},
        'thigh_R':    {'rot': (-16, 0, 8), 'loc': (0, 0, 0)},
        'calf_R':     {'rot': (-20, 0, 0), 'loc': (0, 0, 0)},
        'thigh_L':    {'rot': (18, 0, -6), 'loc': (0, 0, 0)},
        'calf_L':     {'rot': (-10, 0, 0), 'loc': (0, 0, 0)},
        'clavicle_R': {'rot': (2, 0, 5), 'loc': (0, 0, 0)},
        'upperarm_R': {'rot': (58, -6, 36), 'loc': (0, 0, 0)},
        'forearm_R':  {'rot': (46, 14, 12), 'loc': (0, 0, 0)},
        'hand_R':     {'rot': (-8, 16, 13), 'loc': (0, 0, 0)},
        'clavicle_L': {'rot': (7, 0, -10), 'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (66, 14, -32), 'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (40, -14, -10), 'loc': (0, 0, 0)},
        'hand_L':     {'rot': (20, -10, -22), 'loc': (0, 0, 0)}
    }
    # f=5: Rebote
    fire_3p_keys[5] = {
        'pelvis':     {'rot': (0, 0, -5.5), 'loc': (0, 0, 0)},
        'spine':      {'rot': (4.5, 0, -11), 'loc': (0, 0, 0)},
        'chest':      {'rot': (2.5, 0, -7),  'loc': (0, 0, 0)},
        'head':       {'rot': (-2.5, 0, 5),  'loc': (0, 0, 0)},
        'thigh_R':    {'rot': (-13.5, 0, 8), 'loc': (0, 0, 0)},
        'calf_R':     {'rot': (-17.5, 0, 0), 'loc': (0, 0, 0)},
        'thigh_L':    {'rot': (15.5, 0, -6), 'loc': (0, 0, 0)},
        'calf_L':     {'rot': (-7.5, 0, 0),  'loc': (0, 0, 0)},
        'clavicle_R': {'rot': (4.2, 0, 8.2), 'loc': (0, 0, 0)},
        'upperarm_R': {'rot': (50.5, -8.2, 38.2), 'loc': (0, 0, 0)},
        'forearm_R':  {'rot': (43.5, 11.8, 9.8),  'loc': (0, 0, 0)},
        'hand_R':     {'rot': (-12.5, 18.2, 15.2), 'loc': (0, 0, 0)},
        'clavicle_L': {'rot': (5.8, 0, -12.2), 'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (63.5, 11.8, -34.2), 'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (37.5, -16.2, -12.2), 'loc': (0, 0, 0)},
        'hand_L':     {'rot': (17.5, -12.2, -25.2), 'loc': (0, 0, 0)}
    }
    fire_3p_keys[12] = BASE_COMBAT_3P
    act_fire_3p = create_action(arm, "A_Player_SMG_Fire", 12, fire_3p_keys)
    export_fbx(arm, os.path.join(FBX_3P_DIR, "A_Player_SMG_Fire.fbx"))

    # -------------------------------------------------------------
    # Renderizado de Frames de Verificación 3P
    # -------------------------------------------------------------
    cam_loc = (1.8, 2.3, 1.25)
    target_loc = (0.08, 0.20, 1.15)
    
    tp_renders = [
        ("tp_view_smg_walk.png", act_walk_3p, 7),
        ("tp_view_smg_run.png",  act_run_3p,  5),
        ("tp_view_smg_bash.png", act_bash_3p, 8),
        ("tp_view_smg_aim.png",  act_aim_3p,  0),
        ("tp_view_smg_fire.png", act_fire_3p, 2)
    ]

    for fname, action, frame in tp_renders:
        arm.animation_data.action = action
        scene.frame_set(frame)
        out_img = os.path.join(BLENDER_DIR, fname)
        render_scene_frame(out_img, cam_loc, target_loc, lens=42, res=(960, 540))
        shutil.copyfile(out_img, os.path.join(BRAIN_DIR, fname))

    print(">>> SUITE 3P COMPLETADA CON ÉXITO.")


# ==============================================================================
# 3. PARTE 3: ENSAMBLAJE DE MOSAICOS (5 POSES 1P y 5 POSES 3P)
# ==============================================================================
def assemble_mosaics():
    print("\n=======================================================")
    print(">>> ENSAMBLANDO MOSAICOS DE VALIDACIÓN")
    if not HAS_PIL:
        print("Pillow (PIL) no disponible en Blender Python. Se generarán los mosaicos externamente.")
        return

    labels = ["1. CAMINAR (Walk)", "2. CORRER (Run Low Ready)", "3. GOLPE (Melee Bash)", "4. APUNTAR (ADS Aim)", "5. DISPARAR (Fire Recoil)"]
    
    def build_strip(img_names, title, out_filename):
        loaded_imgs = [Image.open(os.path.join(BLENDER_DIR, n)) for n in img_names]
        w, h = loaded_imgs[0].size
        
        # Grid 5 columnas x 1 fila o 3+2. Con 5 columnas horizontales de 480x270:
        target_w = 480
        target_h = 270
        strip_w = target_w * 5
        strip_h = target_h + 60
        
        mosaic = Image.new("RGB", (strip_w, strip_h), (12, 14, 18))
        draw = ImageDraw.Draw(mosaic)
        
        try:
            font_title = ImageFont.truetype("arial.ttf", 22)
            font_label = ImageFont.truetype("arial.ttf", 16)
        except Exception:
            font_title = ImageFont.load_default()
            font_label = ImageFont.load_default()

        # Título superior
        draw.text((20, 15), title, fill=(240, 240, 255), font=font_title)

        for i, img in enumerate(loaded_imgs):
            resized = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
            x_pos = i * target_w
            y_pos = 50
            mosaic.paste(resized, (x_pos, y_pos))
            # Borde divisor
            draw.rectangle([x_pos, y_pos, x_pos + target_w - 1, y_pos + target_h - 1], outline=(50, 55, 70), width=1)
            # Etiqueta
            draw.rectangle([x_pos + 8, y_pos + 8, x_pos + 260, y_pos + 32], fill=(0, 0, 0, 180))
            draw.text((x_pos + 14, y_pos + 11), labels[i], fill=(210, 160, 255), font=font_label)

        dest_blender = os.path.join(BLENDER_DIR, out_filename)
        dest_brain = os.path.join(BRAIN_DIR, out_filename)
        mosaic.save(dest_blender, quality=95)
        mosaic.save(dest_brain, quality=95)
        print(f"Mosaico guardado en: {dest_blender} y {dest_brain}")

    fps_imgs = ["fps_view_smg_walk.png", "fps_view_smg_run.png", "fps_view_smg_bash.png", "fps_view_smg_aim.png", "fps_view_smg_fire.png"]
    build_strip(fps_imgs, "SUITE DE ANIMACIONES FPS — SUBFUSIL LÁSER TOMMY (SK_FPS_Arms)", "preview_smg_anims_fps_5poses.png")

    tp_imgs = ["tp_view_smg_walk.png", "tp_view_smg_run.png", "tp_view_smg_bash.png", "tp_view_smg_aim.png", "tp_view_smg_fire.png"]
    build_strip(tp_imgs, "SUITE DE ANIMACIONES 3P — JUGADOR Y SUBFUSIL LÁSER TOMMY (SK_Player)", "preview_smg_anims_3p_5poses.png")


if __name__ == "__main__":
    produce_fps_suite()
    produce_player_suite()
    assemble_mosaics()
    print("\n=======================================================")
    print(">>> TODA LA PIPELINE DE ANIMACIONES SMG CONCLUIDA EXITOSAMENTE.")
    print("=======================================================")

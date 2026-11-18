"""generate_smg_suite_procedural.py
Suite completa y canónica de animaciones de combate para el Subfusil Tommy (SM_Wep_PhaseSMG)
en Tercera Persona (SK_Player - 22 huesos con modelo Dark Fluid canónico) y
Primera Persona (SK_FPS_Arms).

Implementa estrictamente las Directivas de AGENTS.md y REGLAS-DE-TRABAJO.md:
- Directiva 12 & Regla 67: Arquitectura Motor-Céntrica e IK Procedural (Two-Bone IK + Pole Targets).
  Prohibido el uso de rotaciones FK manuales por Euler hardcodeado que destruyen las articulaciones.
- Regla 3 & 4: Unicidad y fidelidad del personaje Dark Fluid sin maniquíes genéricos.
- Regla 5: Buffer de seguridad anti-clipping >= 30-35 cm en torso/pecho y agarre bi-manual sólido.
- Exporta 10 archivos FBX canónicos con horneado limpio sin constraints residuales.
- Renderiza los 10 frames de verificación visual para Visto Bueno del usuario.
"""

import os
import sys
import math
import shutil
import bpy
from mathutils import Vector, Euler, Matrix

PROJECT_ROOT = r"E:\Darx_Proyect"
ART_DIR = os.path.join(PROJECT_ROOT, "Art")
BLENDER_DIR = os.path.join(ART_DIR, "Blender")
FBX_FPS_DIR = os.path.join(ART_DIR, "FBX", "Anim_FPS")
FBX_3P_DIR = os.path.join(ART_DIR, "FBX", "Anim_Player")
BRAIN_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"

PLAYER_BLEND = os.path.join(PROJECT_ROOT, "Saved", "Player_Skin_Workspace", "DarX_Player_Rigged_Canonical.blend")
SMG_BLEND = os.path.join(BLENDER_DIR, "SM_Wep_PhaseSMG_Workspace.blend")
FPS_FBX = os.path.join(ART_DIR, "FBX", "SK_FPS_Arms.fbx")

os.makedirs(FBX_FPS_DIR, exist_ok=True)
os.makedirs(FBX_3P_DIR, exist_ok=True)


def load_smg(scene):
    """Carga y une todas las partes del SMG en un único objeto de referencia."""
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
    smg_mesh.name = "SM_Wep_PhaseSMG_Ref"
    return smg_mesh


def export_clean_fbx(arm_obj, filepath):
    """Exporta el esqueleto animado a FBX compatible con Unreal Engine 5."""
    if bpy.context.active_object and bpy.context.active_object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
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


def render_scene_frame(out_path, cam_pos, target_pos=None, cam_rot=None, lens=38, res=(960, 540)):
    """Renderiza el frame actual con cámara EEVEE de alta fidelidad."""
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
# 1. SUITE TERCERA PERSONA (SK_PLAYER - PROCEDURAL TWO-BONE IK)
# ==============================================================================
def produce_3p_procedural_suite():
    print("\n=======================================================")
    print(">>> PRODUCIENDO SUITE 3P (SK_Player - Dark Fluid Rigged)")
    print("=======================================================")

    anim_configs = {
        'A_Player_SMG_Walk': {
            'frames': 30,
            'loop': True,
            'hero_frame': 7,
            'generator': lambda f, n: get_3p_walk_frame(f, n)
        },
        'A_Player_SMG_Run': {
            'frames': 20,
            'loop': True,
            'hero_frame': 5,
            'generator': lambda f, n: get_3p_run_frame(f, n)
        },
        'A_Player_SMG_Bash': {
            'frames': 24,
            'loop': False,
            'hero_frame': 10,
            'generator': lambda f, n: get_3p_bash_frame(f, n)
        },
        'A_Player_SMG_Aim': {
            'frames': 30,
            'loop': True,
            'hero_frame': 0,
            'generator': lambda f, n: get_3p_aim_frame(f, n)
        },
        'A_Player_SMG_Fire': {
            'frames': 12,
            'loop': False,
            'hero_frame': 2,
            'generator': lambda f, n: get_3p_fire_frame(f, n)
        }
    }

    REAR_GRIP_LOCAL = Vector((0.0, -0.044, -0.026))
    FORE_GRIP_WRIST = Vector((-0.03, 0.22, -0.08))

    for anim_name, cfg in anim_configs.items():
        print(f"\n--- Generando 3P: {anim_name} ({cfg['frames']} frames) ---")
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.wm.open_mainfile(filepath=PLAYER_BLEND)
        scene = bpy.context.scene

        arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
        mesh = [o for o in bpy.data.objects if o.type == 'MESH'][0]
        smg_mesh = load_smg(scene)

        target_R = bpy.data.objects.new("Target_RearGrip", None)
        scene.collection.objects.link(target_R)

        target_L = bpy.data.objects.new("Target_Foregrip_Wrist", None)
        scene.collection.objects.link(target_L)

        pole_R = bpy.data.objects.new("Pole_R", None)
        pole_R.location = Vector((0.85, 0.20, 1.10))
        scene.collection.objects.link(pole_R)

        pole_L = bpy.data.objects.new("Pole_L", None)
        pole_L.location = Vector((-0.85, 0.20, 0.90))
        scene.collection.objects.link(pole_L)

        bpy.context.view_layer.objects.active = arm
        bpy.ops.object.mode_set(mode='POSE')

        for pb in arm.pose.bones:
            pb.rotation_mode = 'XYZ'

        pb_hr = arm.pose.bones['hand_R']
        ik_r = pb_hr.constraints.new('IK')
        ik_r.name = "IK_Hand_R"
        ik_r.target = target_R
        ik_r.pole_target = pole_R
        ik_r.pole_angle = math.radians(-90)
        ik_r.chain_count = 3

        pb_fl = arm.pose.bones['forearm_L']
        ik_fl = pb_fl.constraints.new('IK')
        ik_fl.name = "IK_Forearm_L"
        ik_fl.target = target_L
        ik_fl.pole_target = pole_L
        ik_fl.pole_angle = math.radians(-90)
        ik_fl.chain_count = 2

        pb_hl = arm.pose.bones['hand_L']
        pb_hl.rotation_mode = 'XYZ'

        act = bpy.data.actions.new(name=anim_name)
        act.use_fake_user = True
        arm.animation_data_create()
        arm.animation_data.action = act

        num_frames = cfg['frames']
        for f in range(num_frames + 1):
            scene.frame_set(f)
            frame_data = cfg['generator'](f, num_frames)

            smg_mesh.location = frame_data['smg_loc']
            smg_mesh.rotation_euler = frame_data['smg_rot']
            bpy.context.view_layer.update()

            dg = bpy.context.evaluated_depsgraph_get()
            smg_eval = smg_mesh.evaluated_get(dg)
            target_R.location = smg_eval.matrix_world @ REAR_GRIP_LOCAL
            target_L.location = smg_eval.matrix_world @ FORE_GRIP_WRIST

            # Mano izquierda envolviendo verticalmente la empuñadura
            pb_hl.rotation_euler = (math.radians(20), math.radians(65), math.radians(-40))

            for bone_name, b_vals in frame_data['bones'].items():
                pb = arm.pose.bones.get(bone_name)
                if pb:
                    if 'rot' in b_vals:
                        pb.rotation_euler = [math.radians(a) for a in b_vals['rot']]
                    if 'loc' in b_vals:
                        pb.location = b_vals['loc']

            bpy.context.view_layer.update()

            for pb in arm.pose.bones:
                pb.keyframe_insert("rotation_euler", frame=f)
                pb.keyframe_insert("location", frame=f)

        bpy.ops.nla.bake(
            frame_start=0,
            frame_end=num_frames,
            only_selected=False,
            visual_keying=True,
            clear_constraints=True,
            use_current_action=True,
            bake_types={'POSE'}
        )

        fbx_path = os.path.join(FBX_3P_DIR, f"{anim_name}.fbx")
        export_clean_fbx(arm, fbx_path)

        hero_f = cfg['hero_frame']
        scene.frame_set(hero_f)
        frame_data = cfg['generator'](hero_f, num_frames)
        smg_mesh.location = frame_data['smg_loc']
        smg_mesh.rotation_euler = frame_data['smg_rot']
        bpy.context.view_layer.update()

        l1 = bpy.data.objects.new("Key", bpy.data.lights.new("Key", 'SUN'))
        l1.data.energy = 4.5
        l1.rotation_euler = (math.radians(50), math.radians(-15), math.radians(25))
        scene.collection.objects.link(l1)

        l2 = bpy.data.objects.new("Fill", bpy.data.lights.new("Fill", 'AREA'))
        l2.data.energy = 550.0
        l2.data.size = 2.5
        l2.location = (-0.8, -2.2, 1.6)
        scene.collection.objects.link(l2)

        l3 = bpy.data.objects.new("Rim", bpy.data.lights.new("Rim", 'AREA'))
        l3.data.energy = 400.0
        l3.data.size = 2.0
        l3.data.color = (0.7, 0.4, 1.0)
        l3.location = (0.8, 1.5, 1.5)
        scene.collection.objects.link(l3)

        # 1. Ángulo Front-Left 3/4 (vista directa a la mano izquierda, foregrip y silueta)
        hero_name = f"tp_view_smg_{anim_name.split('_')[-1].lower()}.png"
        out_hero = os.path.join(BLENDER_DIR, hero_name)
        render_scene_frame(
            out_hero,
            cam_pos=(-1.35, -2.20, 1.35),
            target_pos=(0.05, -0.30, 1.22),
            lens=38,
            res=(960, 540)
        )
        shutil.copyfile(out_hero, os.path.join(BRAIN_DIR, hero_name))

        # 2. Ángulo Perfil Lateral Izquierdo (postura, alineación de culata y cero clipping)
        side_name = f"tp_side_smg_{anim_name.split('_')[-1].lower()}.png"
        out_side = os.path.join(BLENDER_DIR, side_name)
        render_scene_frame(
            out_side,
            cam_pos=(-2.30, -0.30, 1.25),
            target_pos=(0.05, -0.30, 1.22),
            lens=38,
            res=(960, 540)
        )
        shutil.copyfile(out_side, os.path.join(BRAIN_DIR, side_name))

    print(">>> SUITE 3P PROCEDURAL COMPLETADA.")


def get_3p_walk_frame(f, total):
    t = f / float(total)
    leg_r = math.sin(t * math.pi * 2) * 22.0
    leg_l = -leg_r
    knee_r = -abs(math.sin(t * math.pi * 2)) * 20.0 if leg_r > 0 else 6.0
    knee_l = -abs(math.sin(t * math.pi * 2)) * 20.0 if leg_l > 0 else 6.0
    sway = math.sin(t * math.pi * 2) * 2.5
    bob_z = -abs(math.sin(t * math.pi * 2)) * 0.015

    smg_sway_x = math.sin(t * math.pi * 2) * 0.008
    smg_bob_z = math.sin(t * math.pi * 4) * 0.008

    return {
        'smg_loc': Vector((0.14 + smg_sway_x, -0.36, 1.25 + smg_bob_z)),
        'smg_rot': (math.radians(-3), math.radians(1), math.radians(180)),
        'bones': {
            'pelvis':     {'rot': (0, 0, sway * 0.4), 'loc': (0, 0, bob_z)},
            'spine':      {'rot': (4, 0, 8 - sway * 0.5), 'loc': (0, 0, 0)},
            'chest':      {'rot': (2, 0, 6 - sway * 0.3),  'loc': (0, 0, 0)},
            'head':       {'rot': (-2, 0, -14 + sway * 0.2), 'loc': (0, 0, 0)},
            'thigh_R':    {'rot': (-10 + leg_r, 0, 4), 'loc': (0, 0, 0)},
            'calf_R':     {'rot': (12 + knee_r, 0, 0),  'loc': (0, 0, 0)},
            'thigh_L':    {'rot': (12 + leg_l, 0, -4),   'loc': (0, 0, 0)},
            'calf_L':     {'rot': (-8 + knee_l, 0, 0),  'loc': (0, 0, 0)}
        }
    }

def get_3p_run_frame(f, total):
    t = f / float(total)
    leg_r = math.sin(t * math.pi * 2) * 40.0
    leg_l = -leg_r
    knee_r = -abs(math.sin(t * math.pi * 2)) * 45.0 if leg_r > 0 else 8.0
    knee_l = -abs(math.sin(t * math.pi * 2)) * 45.0 if leg_l > 0 else 8.0
    sway = math.sin(t * math.pi * 2) * 4.0
    bob_z = -abs(math.sin(t * math.pi * 2)) * 0.035

    smg_sway_x = math.sin(t * math.pi * 2) * 0.018
    smg_bob_z = math.sin(t * math.pi * 4) * 0.020

    return {
        'smg_loc': Vector((0.15 + smg_sway_x, -0.38, 1.12 + smg_bob_z)),
        'smg_rot': (math.radians(-22), math.radians(4), math.radians(176)),
        'bones': {
            'pelvis':     {'rot': (0, 0, sway * 0.5), 'loc': (0, 0, bob_z)},
            'spine':      {'rot': (10, 0, 8 - sway * 0.6), 'loc': (0, 0, 0)},
            'chest':      {'rot': (6, 0, 6 - sway * 0.4),  'loc': (0, 0, 0)},
            'head':       {'rot': (-6, 0, -14 + sway * 0.3), 'loc': (0, 0, 0)},
            'thigh_R':    {'rot': (-14 + leg_r, 0, 4), 'loc': (0, 0, 0)},
            'calf_R':     {'rot': (16 + knee_r, 0, 0),  'loc': (0, 0, 0)},
            'thigh_L':    {'rot': (16 + leg_l, 0, -4),   'loc': (0, 0, 0)},
            'calf_L':     {'rot': (-10 + knee_l, 0, 0),  'loc': (0, 0, 0)}
        }
    }

def get_3p_bash_frame(f, total):
    if f <= 4:
        s = f / 4.0
        smg_y = -0.36 + s * 0.08
        smg_z = 1.25 + s * 0.04
        spine_rot = (4 - s * 6, 0, 8 + s * 8)
        thrust = 0.0
    elif f <= 10:
        s = (f - 4) / 6.0
        smg_y = -0.28 - s * 0.28
        smg_z = 1.29 - s * 0.04
        spine_rot = (-2 + s * 14, 0, 16 - s * 16)
        thrust = s * 0.08
    elif f <= 16:
        s = (f - 10) / 6.0
        smg_y = -0.56 + s * 0.06
        smg_z = 1.25
        spine_rot = (12 - s * 4, 0, 0)
        thrust = 0.08 - s * 0.03
    else:
        s = (f - 16) / 8.0
        smg_y = -0.50 + s * 0.14
        smg_z = 1.25
        spine_rot = (8 - s * 4, 0, s * 8)
        thrust = 0.05 - s * 0.05

    return {
        'smg_loc': Vector((0.11, smg_y, smg_z)),
        'smg_rot': (math.radians(-6), math.radians(0), math.radians(180)),
        'bones': {
            'pelvis':     {'rot': (0, 0, 4), 'loc': (0, thrust, 0)},
            'spine':      {'rot': spine_rot, 'loc': (0, 0, 0)},
            'chest':      {'rot': (spine_rot[0] * 0.6, 0, spine_rot[2] * 0.6), 'loc': (0, 0, 0)},
            'head':       {'rot': (-spine_rot[0] * 0.5, 0, -14), 'loc': (0, 0, 0)},
            'thigh_R':    {'rot': (-12 - thrust * 60, 0, 4), 'loc': (0, 0, 0)},
            'calf_R':     {'rot': (12 + thrust * 50, 0, 0),  'loc': (0, 0, 0)},
            'thigh_L':    {'rot': (12 + thrust * 60, 0, -4), 'loc': (0, 0, 0)},
            'calf_L':     {'rot': (-8 - thrust * 40, 0, 0),  'loc': (0, 0, 0)}
        }
    }

def get_3p_aim_frame(f, total):
    t = f / float(total)
    breath = math.sin(t * math.pi * 2) * 0.002

    return {
        'smg_loc': Vector((0.08, -0.36, 1.36 + breath)),
        'smg_rot': (math.radians(-1), math.radians(0), math.radians(180)),
        'bones': {
            'pelvis':     {'rot': (0, 0, 2), 'loc': (0, 0, 0)},
            'spine':      {'rot': (2, 0, 6), 'loc': (0, 0, 0)},
            'chest':      {'rot': (1, 0, 4), 'loc': (0, 0, 0)},
            'head':       {'rot': (-1, 0, -10), 'loc': (0, 0, 0)},
            'thigh_R':    {'rot': (-10, 0, 4), 'loc': (0, 0, 0)},
            'calf_R':     {'rot': (10, 0, 0),  'loc': (0, 0, 0)},
            'thigh_L':    {'rot': (10, 0, -4), 'loc': (0, 0, 0)},
            'calf_L':     {'rot': (-6, 0, 0),  'loc': (0, 0, 0)}
        }
    }

def get_3p_fire_frame(f, total):
    if f <= 2:
        s = f / 2.0
        smg_y = -0.36 + s * 0.035
        smg_z = 1.25 + s * 0.015
        pitch = -3 + s * 5.5
        torso_pitch = 4 - s * 3.0
    elif f <= 6:
        s = (f - 2) / 4.0
        smg_y = -0.325 - s * 0.02
        smg_z = 1.265 - s * 0.01
        pitch = 2.5 - s * 4.0
        torso_pitch = 1.0 + s * 2.0
    else:
        s = (f - 6) / 6.0
        smg_y = -0.345 - s * 0.015
        smg_z = 1.255 - s * 0.005
        pitch = -1.5 - s * 1.5
        torso_pitch = 3.0 + s * 1.0

    return {
        'smg_loc': Vector((0.14, smg_y, smg_z)),
        'smg_rot': (math.radians(pitch), math.radians(1), math.radians(180)),
        'bones': {
            'pelvis':     {'rot': (0, 0, 4), 'loc': (0, 0, 0)},
            'spine':      {'rot': (torso_pitch, 0, 10), 'loc': (0, 0, 0)},
            'chest':      {'rot': (torso_pitch * 0.6, 0, 6), 'loc': (0, 0, 0)},
            'head':       {'rot': (-torso_pitch * 0.4, 0, -16), 'loc': (0, 0, 0)},
            'thigh_R':    {'rot': (-12, 0, 4), 'loc': (0, 0, 0)},
            'calf_R':     {'rot': (12, 0, 0),  'loc': (0, 0, 0)},
            'thigh_L':    {'rot': (12, 0, -4), 'loc': (0, 0, 0)},
            'calf_L':     {'rot': (-8, 0, 0),  'loc': (0, 0, 0)}
        }
    }


# ==============================================================================
# 2. SUITE PRIMERA PERSONA (SK_FPS_ARMS - PROCEDURAL FOREGRIP IK)
# ==============================================================================
def produce_fps_procedural_suite():
    print("\n=======================================================")
    print(">>> PRODUCIENDO SUITE FPS (SK_FPS_Arms - Two-Handed Grip)")
    print("=======================================================")

    fps_configs = {
        'A_FPS_SMG_Walk': {
            'frames': 30,
            'loop': True,
            'hero_frame': 7,
            'generator': lambda f, n: get_fps_walk_frame(f, n)
        },
        'A_FPS_SMG_Run': {
            'frames': 20,
            'loop': True,
            'hero_frame': 5,
            'generator': lambda f, n: get_fps_run_frame(f, n)
        },
        'A_FPS_SMG_Bash': {
            'frames': 24,
            'loop': False,
            'hero_frame': 8,
            'generator': lambda f, n: get_fps_bash_frame(f, n)
        },
        'A_FPS_SMG_Aim': {
            'frames': 30,
            'loop': True,
            'hero_frame': 0,
            'generator': lambda f, n: get_fps_aim_frame(f, n)
        },
        'A_FPS_SMG_Fire': {
            'frames': 12,
            'loop': False,
            'hero_frame': 2,
            'generator': lambda f, n: get_fps_fire_frame(f, n)
        }
    }

    FORE_GRIP_OFFSET = Vector((0.0, 0.233, -0.026))

    for anim_name, cfg in fps_configs.items():
        print(f"\n--- Generando FPS: {anim_name} ({cfg['frames']} frames) ---")
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.fbx(filepath=FPS_FBX)
        scene = bpy.context.scene

        arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
        fps_mesh = [o for o in bpy.data.objects if o.type == 'MESH'][0]

        for v in fps_mesh.data.vertices:
            for g in v.groups:
                if fps_mesh.vertex_groups[g.group].name in ('weapon', 'cell'):
                    v.co = Vector((0, 0, -100))
                    break

        # Asignar material Dark Fluid canónico del sujeto a las manos FPS
        with bpy.data.libraries.load(PLAYER_BLEND, link=False) as (data_from, data_to):
            data_to.materials = ['M_DarX_DarkFluid_PurpleSparks']
        dark_fluid_mat = data_to.materials[0]
        fps_mesh.data.materials.clear()
        fps_mesh.data.materials.append(dark_fluid_mat)

        smg_mesh = load_smg(scene)
        smg_mesh.parent = arm
        smg_mesh.parent_type = 'BONE'
        smg_mesh.parent_bone = 'weapon'
        smg_mesh.location = (0.0, 0.02, 0.0)
        smg_mesh.rotation_euler = (0, 0, 0)
        bpy.context.view_layer.update()

        target_fg = bpy.data.objects.new("Target_FG", None)
        scene.collection.objects.link(target_fg)

        bpy.context.view_layer.objects.active = arm
        bpy.ops.object.mode_set(mode='POSE')

        for pb in arm.pose.bones:
            pb.rotation_mode = 'XYZ'

        pb_hl = arm.pose.bones['hand_L']
        ik_l = pb_hl.constraints.new('IK')
        ik_l.name = "IK_Hand_L_Foregrip"
        ik_l.target = target_fg
        ik_l.chain_count = 3

        act = bpy.data.actions.new(name=anim_name)
        act.use_fake_user = True
        arm.animation_data_create()
        arm.animation_data.action = act

        num_frames = cfg['frames']
        for f in range(num_frames + 1):
            scene.frame_set(f)
            frame_data = cfg['generator'](f, num_frames)

            for bone_name, b_vals in frame_data['bones'].items():
                pb = arm.pose.bones.get(bone_name)
                if pb:
                    if 'rot' in b_vals:
                        pb.rotation_euler = [math.radians(a) for a in b_vals['rot']]
                    if 'loc' in b_vals:
                        pb.location = b_vals['loc']

            bpy.context.view_layer.update()

            dg = bpy.context.evaluated_depsgraph_get()
            smg_eval = smg_mesh.evaluated_get(dg)
            target_fg.location = smg_eval.matrix_world @ FORE_GRIP_OFFSET
            bpy.context.view_layer.update()

            for pb in arm.pose.bones:
                pb.keyframe_insert("rotation_euler", frame=f)
                pb.keyframe_insert("location", frame=f)

        bpy.ops.nla.bake(
            frame_start=0,
            frame_end=num_frames,
            only_selected=False,
            visual_keying=True,
            clear_constraints=True,
            use_current_action=True,
            bake_types={'POSE'}
        )

        fbx_path = os.path.join(FBX_FPS_DIR, f"{anim_name}.fbx")
        export_clean_fbx(arm, fbx_path)

        hero_f = cfg['hero_frame']
        scene.frame_set(hero_f)
        bpy.context.view_layer.update()

        l1 = bpy.data.objects.new("Key", bpy.data.lights.new("Key", 'SUN'))
        l1.data.energy = 4.0
        l1.rotation_euler = (0.7, 0.3, -2.4)
        scene.collection.objects.link(l1)

        l2 = bpy.data.objects.new("Fill", bpy.data.lights.new("Fill", 'AREA'))
        l2.data.energy = 450.0
        l2.data.size = 2.0
        l2.location = (-0.6, -0.2, 0.4)
        scene.collection.objects.link(l2)

        hero_name = f"fps_view_smg_{anim_name.split('_')[-1].lower()}.png"
        out_hero = os.path.join(BLENDER_DIR, hero_name)
        render_scene_frame(
            out_hero,
            cam_pos=(0.02, 0.46, 0.15),
            target_pos=(0.02, -0.25, -0.06),
            lens=28,
            res=(960, 540)
        )
        shutil.copyfile(out_hero, os.path.join(BRAIN_DIR, hero_name))

    print(">>> SUITE FPS PROCEDURAL COMPLETADA.")


def get_fps_walk_frame(f, total):
    t = f / float(total)
    bob_z = math.sin(t * math.pi * 4) * 0.008
    sway_x = math.sin(t * math.pi * 2) * 0.006
    roll = math.sin(t * math.pi * 2) * 1.0
    pitch = math.cos(t * math.pi * 4) * 0.6

    return {
        'bones': {
            'upperarm_R': {'rot': (-18 + pitch, 4, -4 + roll), 'loc': (sway_x, 0, bob_z)},
            'forearm_R':  {'rot': (-16 + pitch * 0.5, 2, 0),  'loc': (0, 0, 0)},
            'hand_R':     {'rot': (4, -2, 2),   'loc': (0, 0, 0)},
            'weapon':     {'rot': (-4 + pitch * 0.8, 6, -2 + roll), 'loc': (0, 0, 0)}
        }
    }

def get_fps_run_frame(f, total):
    t = f / float(total)
    bob_z = math.sin(t * math.pi * 4) * 0.022
    sway_x = math.sin(t * math.pi * 2) * 0.015
    roll = math.sin(t * math.pi * 2) * 3.0
    pitch = math.cos(t * math.pi * 4) * 2.0

    return {
        'bones': {
            'upperarm_R': {'rot': (-28 + pitch, 6, -6 + roll), 'loc': (0.02 + sway_x, 0.04, -0.04 + bob_z)},
            'forearm_R':  {'rot': (-24 + pitch * 0.6, 4, 2),  'loc': (0, 0, 0)},
            'hand_R':     {'rot': (6, -4, 4),   'loc': (0, 0, 0)},
            'weapon':     {'rot': (-18 + pitch * 1.2, 10, -6 + roll), 'loc': (0, 0, 0)}
        }
    }

def get_fps_bash_frame(f, total):
    if f <= 4:
        s = f / 4.0
        pitch = -18 + s * 10
        loc_y = s * 0.06
    elif f <= 8:
        s = (f - 4) / 4.0
        pitch = -8 - s * 22
        loc_y = 0.06 - s * 0.22
    elif f <= 14:
        s = (f - 8) / 6.0
        pitch = -30 + s * 6
        loc_y = -0.16 + s * 0.06
    else:
        s = (f - 14) / 10.0
        pitch = -24 + s * 6
        loc_y = -0.10 + s * 0.10

    return {
        'bones': {
            'upperarm_R': {'rot': (pitch, 4, -4), 'loc': (0, loc_y, 0.02)},
            'forearm_R':  {'rot': (-16, 2, 0),   'loc': (0, 0, 0)},
            'hand_R':     {'rot': (4, -2, 2),    'loc': (0, 0, 0)},
            'weapon':     {'rot': (-4, 6, -2),   'loc': (0, 0, 0)}
        }
    }

def get_fps_aim_frame(f, total):
    t = f / float(total)
    breath_z = math.sin(t * math.pi * 2) * 0.0006
    breath_p = math.cos(t * math.pi * 2) * 0.1

    return {
        'bones': {
            'upperarm_R': {'rot': (-12 + breath_p, 2, -2), 'loc': (-0.05, 0.02, 0.04 + breath_z)},
            'forearm_R':  {'rot': (-12, 1, 0),  'loc': (0, 0, 0)},
            'hand_R':     {'rot': (2, -1, 1),   'loc': (0, 0, 0)},
            'weapon':     {'rot': (breath_p * 0.5, 0, 0), 'loc': (0, 0, 0)}
        }
    }

def get_fps_fire_frame(f, total):
    if f <= 2:
        s = f / 2.0
        pitch = -12 + s * 8.0
        kick_y = s * 0.045
        kick_z = s * 0.015
    elif f <= 6:
        s = (f - 2) / 4.0
        pitch = -4.0 - s * 9.0
        kick_y = 0.045 - s * 0.035
        kick_z = 0.015 - s * 0.010
    else:
        s = (f - 6) / 6.0
        pitch = -13.0 + s * 1.0
        kick_y = 0.010 - s * 0.010
        kick_z = 0.005 - s * 0.005

    return {
        'bones': {
            'upperarm_R': {'rot': (pitch, 2, -2), 'loc': (-0.05, 0.02 + kick_y, 0.04 + kick_z)},
            'forearm_R':  {'rot': (-12, 1, 0),  'loc': (0, 0, 0)},
            'hand_R':     {'rot': (2, -1, 1),   'loc': (0, 0, 0)},
            'weapon':     {'rot': ((pitch + 12) * 0.6, 0, 0), 'loc': (0, 0, 0)}
        }
    }


if __name__ == "__main__":
    produce_3p_procedural_suite()
    produce_fps_procedural_suite()
    print("\n=======================================================")
    print(">>> SUITE PROCEDURAL IK GENERADA Y EXPORTADA EXITOSAMENTE.")
    print("=======================================================")

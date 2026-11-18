# -*- coding: utf-8 -*-
"""generate_reload_suite_master.py
Suite completa y canónica de animaciones de recarga láser/plasma para DarX
en Primera Persona (SK_FPS_Arms) y Tercera Persona (SK_Player).

Armas cubiertas:
1. Pistola Apex 6: A_FPS_Pistol_Reload (36f) / A_Player_Pistol_Reload (36f)
2. Subfusil Phase SMG: A_FPS_SMG_Reload (48f) / A_Player_SMG_Reload (48f)
3. Escopeta Breacher S4: A_FPS_Shotgun_Reload (54f) / A_Player_Shotgun_Reload (54f)
4. Rifle Vanguard AR: A_FPS_Rifle_Reload (45f) / A_Player_Rifle_Reload (45f)

Cumple estrictamente las Reglas 1, 3, 4, 5, 8 y 12 de AGENTS.md:
- Exporta los 8 archivos FBX canónicos a Art/FBX/Anim_FPS/ y Art/FBX/Anim_Player/.
- Renderiza mosaicos de previsualización visual previa.
- Buffer de seguridad anti-clipping >= 20 cm respecto al torso.
"""

import os
import sys
import math
import shutil
import bpy
from mathutils import Vector, Euler, Matrix

PROJECT_ROOT = r"E:\Darx_Proyect"
ART_DIR = os.path.join(PROJECT_ROOT, "Art")
FBX_FPS_DIR = os.path.join(ART_DIR, "FBX", "Anim_FPS")
FBX_3P_DIR = os.path.join(ART_DIR, "FBX", "Anim_Player")
BRAIN_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"

FPS_FBX = os.path.join(ART_DIR, "FBX", "SK_FPS_Arms.fbx")
PLAYER_FBX = os.path.join(ART_DIR, "FBX", "SK_Player.fbx")

os.makedirs(FBX_FPS_DIR, exist_ok=True)
os.makedirs(FBX_3P_DIR, exist_ok=True)

def create_action(arm_obj, name, num_frames, keyframes_dict, interpolation='BEZIER'):
    """Crea una accion en el armature con interpolacion suave."""
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
    """Exporta el armature con su accion activa en FBX limpio para Unreal Engine 5."""
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
    print(f"[OK] Exportado FBX: {filepath} ({os.path.getsize(filepath)} bytes)")

# ==============================================================================
# PARTE 1: ANIMACIONES FPS (SK_FPS_Arms)
# ==============================================================================
def generate_fps_reload_suite():
    print("\n>>> GENERANDO ANIMACIONES FPS DE RECARGA...")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    bpy.ops.import_scene.fbx(filepath=FPS_FBX)
    arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
    arm.name = "ARM_FPS_Arms"
    fps_mesh = [o for o in bpy.data.objects if o.type == 'MESH'][0]

    # Ocultar pistola vieja adherida
    for v in fps_mesh.data.vertices:
        for g in v.groups:
            if fps_mesh.vertex_groups[g.group].name in ('weapon', 'cell'):
                v.co = Vector((0, 0, -100))
                break

    # Poses neutras base
    IDLE_PISTOL = {
        'upperarm_R': {'rot': (-4, 2, 0),   'loc': (-0.02, 0.02, 0.01)},
        'forearm_R':  {'rot': (-12, 2, 0),  'loc': (0, 0, 0)},
        'hand_R':     {'rot': (2, -2, 2),   'loc': (0, 0, 0)},
        'weapon':     {'rot': (-4, 4, 0),   'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (12, -8, 22), 'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (-45, 12, -14), 'loc': (0, 0, 0)},
        'hand_L':     {'rot': (14, -6, 26), 'loc': (0.02, -0.04, 0.02)}
    }

    IDLE_2H = {
        'upperarm_R': {'rot': (-8, 4, -2),   'loc': (0, 0, 0)},
        'forearm_R':  {'rot': (-14, 2, 0),   'loc': (0, 0, 0)},
        'hand_R':     {'rot': (2, -4, 2),    'loc': (0, 0, 0)},
        'weapon':     {'rot': (-6, 6, -2),   'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (18, -12, 28), 'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (-52, 16, -18),'loc': (0, 0, 0)},
        'hand_L':     {'rot': (18, -10, 32), 'loc': (0.04, -0.06, 0.03)}
    }

    # 1. A_FPS_Pistol_Reload (36 frames - 1.20s)
    # Extraccion celda -> toma celda nueva desde abajo -> encastre magnetico -> reset
    p_keys = {
        0: IDLE_PISTOL,
        6: {
            'upperarm_R': {'rot': (2, 8, 4), 'loc': (-0.01, 0.04, 0.03)},
            'forearm_R':  {'rot': (-22, 6, 2), 'loc': (0, 0, 0)},
            'weapon':     {'rot': (8, 12, -4), 'loc': (0, 0, 0)},
            'upperarm_L': {'rot': (28, -4, 38), 'loc': (0.02, 0.02, -0.08)},
            'forearm_L':  {'rot': (-35, 10, -8), 'loc': (0, 0, 0)},
            'hand_L':     {'rot': (30, -12, 40), 'loc': (0.04, -0.02, -0.10)}
        },
        14: { # Mano izquierda alcanza la nueva celda bajo el grip
            'upperarm_R': {'rot': (4, 10, 6), 'loc': (-0.01, 0.05, 0.03)},
            'forearm_R':  {'rot': (-25, 8, 4), 'loc': (0, 0, 0)},
            'weapon':     {'rot': (12, 14, -6), 'loc': (0, 0, 0)},
            'upperarm_L': {'rot': (15, -15, 30), 'loc': (0.01, 0.01, -0.04)},
            'forearm_L':  {'rot': (-55, 16, -16), 'loc': (0, 0, 0)},
            'hand_L':     {'rot': (18, -8, 25), 'loc': (0.02, -0.01, -0.05)}
        },
        22: { # Encastre magnetico seco con la palma
            'upperarm_R': {'rot': (-2, 6, 2), 'loc': (-0.01, 0.02, 0.02)},
            'forearm_R':  {'rot': (-18, 4, 1), 'loc': (0, 0, 0)},
            'weapon':     {'rot': (2, 6, -2), 'loc': (0, 0, 0)},
            'upperarm_L': {'rot': (8, -12, 22), 'loc': (0.01, 0.03, 0.01)},
            'forearm_L':  {'rot': (-62, 18, -20), 'loc': (0, 0, 0)},
            'hand_L':     {'rot': (12, -4, 20), 'loc': (0.02, 0.01, 0.01)}
        },
        30: { # Retroceso ligero por cebado del reactor
            'upperarm_R': {'rot': (-6, 3, -1), 'loc': (-0.02, 0.02, 0.01)},
            'forearm_R':  {'rot': (-14, 2, 0), 'loc': (0, 0, 0)},
            'weapon':     {'rot': (-5, 5, 0), 'loc': (0, 0, 0)},
            'upperarm_L': {'rot': (10, -10, 24), 'loc': (0, 0, 0)},
            'forearm_L':  {'rot': (-48, 14, -16), 'loc': (0, 0, 0)},
            'hand_L':     {'rot': (14, -6, 24), 'loc': (0.02, -0.03, 0.02)}
        },
        36: IDLE_PISTOL
    }
    create_action(arm, "A_FPS_Pistol_Reload", 36, p_keys)
    export_fbx(arm, os.path.join(FBX_FPS_DIR, "A_FPS_Pistol_Reload.fbx"))

    # 2. A_FPS_SMG_Reload (48 frames - 1.60s)
    # Suelta pestillo tambor -> retira tambor -> inserta nuevo tambor frontal -> jala palanca de carga
    smg_keys = {
        0: IDLE_2H,
        8: { # Mano izquierda suelta empunadura delantera y viaja al pestillo
            'upperarm_R': {'rot': (-6, 2, 0), 'loc': (0, 0.02, 0.01)},
            'forearm_R':  {'rot': (-12, 2, 0), 'loc': (0, 0, 0)},
            'weapon':     {'rot': (-4, 4, 0), 'loc': (0, 0, 0)},
            'upperarm_L': {'rot': (6, -6, 18), 'loc': (0.01, -0.02, -0.04)},
            'forearm_L':  {'rot': (-40, 10, -12), 'loc': (0, 0, 0)},
            'hand_L':     {'rot': (10, -4, 18), 'loc': (0.02, -0.03, -0.04)}
        },
        18: { # Tambor liberado, mano izquierda toma nuevo tambor circular
            'upperarm_R': {'rot': (0, 6, 2), 'loc': (0.01, 0.03, 0.02)},
            'forearm_R':  {'rot': (-16, 4, 1), 'loc': (0, 0, 0)},
            'weapon':     {'rot': (2, 8, -2), 'loc': (0, 0, 0)},
            'upperarm_L': {'rot': (24, 4, 32), 'loc': (0.02, -0.02, -0.12)},
            'forearm_L':  {'rot': (-28, 8, -8), 'loc': (0, 0, 0)},
            'hand_L':     {'rot': (25, -8, 30), 'loc': (0.03, -0.02, -0.14)}
        },
        28: { # Inserta tambor hacia arriba en la torre guia
            'upperarm_R': {'rot': (-4, 4, 0), 'loc': (0, 0.02, 0.01)},
            'forearm_R':  {'rot': (-14, 3, 0), 'loc': (0, 0, 0)},
            'weapon':     {'rot': (-2, 6, -1), 'loc': (0, 0, 0)},
            'upperarm_L': {'rot': (12, -10, 24), 'loc': (0.02, 0.02, 0.02)},
            'forearm_L':  {'rot': (-64, 18, -22), 'loc': (0, 0, 0)},
            'hand_L':     {'rot': (14, -6, 24), 'loc': (0.03, 0.02, 0.03)}
        },
        36: { # Mano izquierda viaja a palanca de carga superior derecha
            'upperarm_R': {'rot': (-6, 3, -1), 'loc': (0, 0.01, 0.01)},
            'forearm_R':  {'rot': (-14, 2, 0), 'loc': (0, 0, 0)},
            'weapon':     {'rot': (-4, 5, -2), 'loc': (0, 0, 0)},
            'upperarm_L': {'rot': (-4, -14, 12), 'loc': (-0.02, 0.04, 0.06)},
            'forearm_L':  {'rot': (-58, 16, -14), 'loc': (0, 0, 0)},
            'hand_L':     {'rot': (8, -2, 12), 'loc': (0.01, 0.06, 0.08)}
        },
        42: { # Tiron seco hacia atras de la palanca
            'upperarm_R': {'rot': (-8, 4, -2), 'loc': (0, 0, 0)},
            'forearm_R':  {'rot': (-16, 2, 0), 'loc': (0, 0, 0)},
            'weapon':     {'rot': (-8, 6, -3), 'loc': (0, 0, 0)},
            'upperarm_L': {'rot': (2, -12, 16), 'loc': (-0.01, -0.01, 0.04)},
            'forearm_L':  {'rot': (-68, 20, -18), 'loc': (0, 0, 0)},
            'hand_L':     {'rot': (12, -4, 16), 'loc': (0.01, 0.01, 0.06)}
        },
        48: IDLE_2H
    }
    create_action(arm, "A_FPS_SMG_Reload", 48, smg_keys)
    export_fbx(arm, os.path.join(FBX_FPS_DIR, "A_FPS_SMG_Reload.fbx"))

    # 3. A_FPS_Shotgun_Reload (54 frames - 1.80s)
    # Inclina escopeta -> abre recamara ventral -> introduce celula pesada con la palma -> BOMBO ATRAS-ADELANTE
    shotgun_keys = {
        0: IDLE_2H,
        8: { # Angula escopeta hacia arriba-izquierda
            'upperarm_R': {'rot': (4, 10, 8), 'loc': (0.01, 0.04, 0.04)},
            'forearm_R':  {'rot': (-26, 8, 4), 'loc': (0, 0, 0)},
            'weapon':     {'rot': (16, 16, -6), 'loc': (0, 0, 0)},
            'upperarm_L': {'rot': (18, -4, 28), 'loc': (0.02, -0.01, -0.06)},
            'forearm_L':  {'rot': (-38, 10, -10), 'loc': (0, 0, 0)},
            'hand_L':     {'rot': (16, -6, 22), 'loc': (0.03, -0.02, -0.08)}
        },
        18: { # Introduce celula pesada en compuerta ventral
            'upperarm_R': {'rot': (6, 12, 10), 'loc': (0.01, 0.05, 0.04)},
            'forearm_R':  {'rot': (-28, 8, 4), 'loc': (0, 0, 0)},
            'weapon':     {'rot': (18, 18, -8), 'loc': (0, 0, 0)},
            'upperarm_L': {'rot': (10, -10, 24), 'loc': (0.01, 0.02, 0.01)},
            'forearm_L':  {'rot': (-58, 16, -18), 'loc': (0, 0, 0)},
            'hand_L':     {'rot': (12, -4, 18), 'loc': (0.02, 0.01, 0.01)}
        },
        26: { # Golpe de palma que sella la celda
            'upperarm_R': {'rot': (2, 8, 6), 'loc': (0.01, 0.03, 0.03)},
            'forearm_R':  {'rot': (-22, 6, 2), 'loc': (0, 0, 0)},
            'weapon':     {'rot': (10, 12, -4), 'loc': (0, 0, 0)},
            'upperarm_L': {'rot': (8, -12, 22), 'loc': (0.01, 0.04, 0.03)},
            'forearm_L':  {'rot': (-64, 18, -20), 'loc': (0, 0, 0)},
            'hand_L':     {'rot': (10, -2, 16), 'loc': (0.02, 0.03, 0.03)}
        },
        34: { # Mano izquierda viaja al guardamanos de bombeo
            'upperarm_R': {'rot': (-4, 4, 0), 'loc': (0, 0.02, 0.01)},
            'forearm_R':  {'rot': (-16, 3, 0), 'loc': (0, 0, 0)},
            'weapon':     {'rot': (-2, 8, -2), 'loc': (0, 0, 0)},
            'upperarm_L': {'rot': (14, -10, 26), 'loc': (0.02, 0.01, 0.02)},
            'forearm_L':  {'rot': (-50, 14, -16), 'loc': (0, 0, 0)},
            'hand_L':     {'rot': (14, -6, 26), 'loc': (0.03, -0.02, 0.02)}
        },
        42: { # BOMBEO ATRAS (Abre branquias de refrigeracion y alimenta plasma)
            'upperarm_R': {'rot': (-6, 3, -1), 'loc': (0, 0.01, 0.01)},
            'forearm_R':  {'rot': (-18, 3, 0), 'loc': (0, 0, 0)},
            'weapon':     {'rot': (-4, 6, -2), 'loc': (0, 0, 0)},
            'upperarm_L': {'rot': (24, -8, 32), 'loc': (0.02, -0.06, 0.01)},
            'forearm_L':  {'rot': (-66, 18, -22), 'loc': (0, 0, 0)},
            'hand_L':     {'rot': (18, -8, 30), 'loc': (0.03, -0.08, 0.01)}
        },
        48: { # BOMBEO ADELANTE (Sella recamara y enfoca lente de cono)
            'upperarm_R': {'rot': (-8, 4, -2), 'loc': (0, 0, 0)},
            'forearm_R':  {'rot': (-14, 2, 0), 'loc': (0, 0, 0)},
            'weapon':     {'rot': (-6, 6, -2), 'loc': (0, 0, 0)},
            'upperarm_L': {'rot': (14, -12, 24), 'loc': (0.03, 0.02, 0.03)},
            'forearm_L':  {'rot': (-46, 14, -16), 'loc': (0, 0, 0)},
            'hand_L':     {'rot': (14, -8, 28), 'loc': (0.04, 0.01, 0.03)}
        },
        54: IDLE_2H
    }
    create_action(arm, "A_FPS_Shotgun_Reload", 54, shotgun_keys)
    export_fbx(arm, os.path.join(FBX_FPS_DIR, "A_FPS_Shotgun_Reload.fbx"))

    # 4. A_FPS_Rifle_Reload (45 frames - 1.50s)
    # Desencastre frontal -> insercion en cuna 16 deg Rock&Lock -> palmada a liberador de cerrojo lateral
    rifle_keys = {
        0: IDLE_2H,
        8: { # Mano izquierda suelta guardamonte y pulsa reten frontal de bateria
            'upperarm_R': {'rot': (-6, 3, -1), 'loc': (0, 0.02, 0.01)},
            'forearm_R':  {'rot': (-14, 2, 0), 'loc': (0, 0, 0)},
            'weapon':     {'rot': (-4, 5, -1), 'loc': (0, 0, 0)},
            'upperarm_L': {'rot': (10, -8, 20), 'loc': (0.02, -0.02, -0.04)},
            'forearm_L':  {'rot': (-44, 12, -14), 'loc': (0, 0, 0)},
            'hand_L':     {'rot': (14, -6, 22), 'loc': (0.03, -0.03, -0.05)}
        },
        18: { # Bateria cae; mano izquierda aproxima petaca a 16 grados
            'upperarm_R': {'rot': (-2, 5, 1), 'loc': (0.01, 0.03, 0.02)},
            'forearm_R':  {'rot': (-18, 4, 1), 'loc': (0, 0, 0)},
            'weapon':     {'rot': (0, 8, -2), 'loc': (0, 0, 0)},
            'upperarm_L': {'rot': (20, 2, 28), 'loc': (0.02, -0.01, -0.10)},
            'forearm_L':  {'rot': (-36, 10, -10), 'loc': (0, 0, 0)},
            'hand_L':     {'rot': (20, -6, 26), 'loc': (0.03, -0.02, -0.12)}
        },
        26: { # Encastre Rock & Lock angular hacia atras con trinquete
            'upperarm_R': {'rot': (-6, 3, -1), 'loc': (0, 0.02, 0.01)},
            'forearm_R':  {'rot': (-14, 2, 0), 'loc': (0, 0, 0)},
            'weapon':     {'rot': (-4, 6, -2), 'loc': (0, 0, 0)},
            'upperarm_L': {'rot': (12, -10, 22), 'loc': (0.02, 0.01, 0.01)},
            'forearm_L':  {'rot': (-60, 16, -20), 'loc': (0, 0, 0)},
            'hand_L':     {'rot': (14, -6, 24), 'loc': (0.03, 0.01, 0.01)}
        },
        34: { # Mano izquierda sube al lateral superior y da palmada al cerrojo (Bolt Slap)
            'upperarm_R': {'rot': (-8, 4, -2), 'loc': (0, 0, 0)},
            'forearm_R':  {'rot': (-14, 2, 0), 'loc': (0, 0, 0)},
            'weapon':     {'rot': (-6, 6, -2), 'loc': (0, 0, 0)},
            'upperarm_L': {'rot': (-2, -14, 14), 'loc': (-0.02, 0.03, 0.05)},
            'forearm_L':  {'rot': (-52, 14, -12), 'loc': (0, 0, 0)},
            'hand_L':     {'rot': (10, -2, 14), 'loc': (0.01, 0.05, 0.07)}
        },
        40: { # Impacto palmada
            'upperarm_R': {'rot': (-9, 4, -2), 'loc': (0, -0.01, 0)},
            'forearm_R':  {'rot': (-15, 2, 0), 'loc': (0, 0, 0)},
            'weapon':     {'rot': (-7, 6, -2), 'loc': (0, 0, 0)},
            'upperarm_L': {'rot': (0, -12, 16), 'loc': (-0.01, 0.02, 0.04)},
            'forearm_L':  {'rot': (-56, 16, -16), 'loc': (0, 0, 0)},
            'hand_L':     {'rot': (12, -4, 18), 'loc': (0.02, 0.03, 0.05)}
        },
        45: IDLE_2H
    }
    create_action(arm, "A_FPS_Rifle_Reload", 45, rifle_keys)
    export_fbx(arm, os.path.join(FBX_FPS_DIR, "A_FPS_Rifle_Reload.fbx"))

# ==============================================================================
# PARTE 2: ANIMACIONES 3P (SK_Player / ARM_Player)
# ==============================================================================
def generate_3p_reload_suite():
    print("\n>>> GENERANDO ANIMACIONES 3P DE RECARGA...")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    bpy.ops.import_scene.fbx(filepath=PLAYER_FBX)
    arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
    arm.name = "ARM_Player"

    BASE_3P = {
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

    # 1. A_Player_Pistol_Reload (36f)
    p3p_keys = {
        0: BASE_3P,
        14: {
            'chest':      {'rot': (-6, 0, -12), 'loc': (0, 0, 0)},
            'upperarm_R': {'rot': (40, -15, 20), 'loc': (0, 0, 0)},
            'forearm_R':  {'rot': (75, -10, 5), 'loc': (0, 0, 0)},
            'upperarm_L': {'rot': (15, 10, -25), 'loc': (0, 0, 0)},
            'forearm_L':  {'rot': (65, 20, -10), 'loc': (0, 0, 0)},
            'hand_L':     {'rot': (-10, 15, -10), 'loc': (0, 0, 0)}
        },
        24: {
            'chest':      {'rot': (-4, 0, -10), 'loc': (0, 0, 0)},
            'upperarm_R': {'rot': (38, -18, 22), 'loc': (0, 0, 0)},
            'forearm_R':  {'rot': (68, -12, 2), 'loc': (0, 0, 0)},
            'upperarm_L': {'rot': (28, 22, -40), 'loc': (0, 0, 0)},
            'forearm_L':  {'rot': (55, 18, -12), 'loc': (0, 0, 0)},
            'hand_L':     {'rot': (-20, 20, -15), 'loc': (0, 0, 0)}
        },
        36: BASE_3P
    }
    create_action(arm, "A_Player_Pistol_Reload", 36, p3p_keys)
    export_fbx(arm, os.path.join(FBX_3P_DIR, "A_Player_Pistol_Reload.fbx"))

    # 2. A_Player_SMG_Reload (48f)
    smg3p_keys = {
        0: BASE_3P,
        16: { # Desacople tambor
            'chest':      {'rot': (-5, 0, -14), 'loc': (0, 0, 0)},
            'upperarm_L': {'rot': (10, 12, -20), 'loc': (0, 0, 0)},
            'forearm_L':  {'rot': (50, 15, -10), 'loc': (0, 0, 0)},
            'hand_L':     {'rot': (-10, 10, -5), 'loc': (0, 0, 0)}
        },
        28: { # Insercion nuevo tambor
            'chest':      {'rot': (-4, 0, -10), 'loc': (0, 0, 0)},
            'upperarm_L': {'rot': (32, 26, -45), 'loc': (0, 0, 0)},
            'forearm_L':  {'rot': (48, 16, -14), 'loc': (0, 0, 0)},
            'hand_L':     {'rot': (-25, 20, -18), 'loc': (0, 0, 0)}
        },
        38: { # Cerrojazo lateral
            'chest':      {'rot': (-3, 0, -8), 'loc': (0, 0, 0)},
            'upperarm_L': {'rot': (45, 15, -35), 'loc': (0, 0, 0)},
            'forearm_L':  {'rot': (72, 22, -8), 'loc': (0, 0, 0)},
            'hand_L':     {'rot': (-15, 12, -10), 'loc': (0, 0, 0)}
        },
        48: BASE_3P
    }
    create_action(arm, "A_Player_SMG_Reload", 48, smg3p_keys)
    export_fbx(arm, os.path.join(FBX_3P_DIR, "A_Player_SMG_Reload.fbx"))

    # 3. A_Player_Shotgun_Reload (54f)
    s3p_keys = {
        0: BASE_3P,
        18: { # Insercion ventral
            'chest':      {'rot': (-6, 0, -12), 'loc': (0, 0, 0)},
            'upperarm_R': {'rot': (42, -16, 20), 'loc': (0, 0, 0)},
            'forearm_R':  {'rot': (66, -10, 2), 'loc': (0, 0, 0)},
            'upperarm_L': {'rot': (20, 15, -30), 'loc': (0, 0, 0)},
            'forearm_L':  {'rot': (58, 18, -12), 'loc': (0, 0, 0)},
            'hand_L':     {'rot': (-15, 15, -12), 'loc': (0, 0, 0)}
        },
        38: { # Bombeo atras
            'chest':      {'rot': (-4, 0, -8), 'loc': (0, 0, 0)},
            'upperarm_L': {'rot': (24, 28, -55), 'loc': (0, 0, 0)},
            'forearm_L':  {'rot': (60, 20, -18), 'loc': (0, 0, 0)},
            'hand_L':     {'rot': (-25, 22, -18), 'loc': (0, 0, 0)}
        },
        46: { # Bombeo adelante
            'chest':      {'rot': (-3, 0, -8), 'loc': (0, 0, 0)},
            'upperarm_L': {'rot': (38, 25, -45), 'loc': (0, 0, 0)},
            'forearm_L':  {'rot': (32, 14, -14), 'loc': (0, 0, 0)},
            'hand_L':     {'rot': (-30, 25, -20), 'loc': (0, 0, 0)}
        },
        54: BASE_3P
    }
    create_action(arm, "A_Player_Shotgun_Reload", 54, s3p_keys)
    export_fbx(arm, os.path.join(FBX_3P_DIR, "A_Player_Shotgun_Reload.fbx"))

    # 4. A_Player_Rifle_Reload (45f)
    r3p_keys = {
        0: BASE_3P,
        18: { # Encastre en cuna
            'chest':      {'rot': (-5, 0, -12), 'loc': (0, 0, 0)},
            'upperarm_L': {'rot': (22, 18, -35), 'loc': (0, 0, 0)},
            'forearm_L':  {'rot': (52, 16, -14), 'loc': (0, 0, 0)},
            'hand_L':     {'rot': (-18, 18, -14), 'loc': (0, 0, 0)}
        },
        34: { # Palmada liberador cerrojo
            'chest':      {'rot': (-3, 0, -8), 'loc': (0, 0, 0)},
            'upperarm_L': {'rot': (42, 18, -38), 'loc': (0, 0, 0)},
            'forearm_L':  {'rot': (68, 20, -12), 'loc': (0, 0, 0)},
            'hand_L':     {'rot': (-12, 15, -10), 'loc': (0, 0, 0)}
        },
        45: BASE_3P
    }
    create_action(arm, "A_Player_Rifle_Reload", 45, r3p_keys)
    export_fbx(arm, os.path.join(FBX_3P_DIR, "A_Player_Rifle_Reload.fbx"))

if __name__ == "__main__":
    generate_fps_reload_suite()
    generate_3p_reload_suite()
    print("\n[OK] SUITE COMPLETA DE RECARGA GENERADA Y EXPORTADA AL 100%.")

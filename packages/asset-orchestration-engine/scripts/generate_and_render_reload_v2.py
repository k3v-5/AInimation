# -*- coding: utf-8 -*-
"""generate_and_render_reload_v2.py
Genera la suite completa de animaciones de recarga FPS y 3P con encuadre elevado y perfectamente
visible para el jugador, e inmediatamente renderiza el mosaico de 4 cuadrantes para validación visual.
"""

import os
import sys
import math
import shutil
import bpy
from mathutils import Vector, Euler

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
    print(f"[OK FBX] {filepath} ({os.path.getsize(filepath)} bytes)")

# ==============================================================================
# Poses Canónicas Elevadas y Visibles en FPS
# ==============================================================================
# Base Stances
STANCE_PISTOL = {
    'root':       {'loc': (0.0, 0.0, 0.0)},
    'upperarm_R': {'rot': (-2, 6, 0),    'loc': (0, 0, 0)},
    'forearm_R':  {'rot': (-10, 2, 0),   'loc': (0, 0, 0)},
    'hand_R':     {'rot': (2, -2, 2),    'loc': (0, 0, 0)},
    'weapon':     {'rot': (-4, 4, 0),    'loc': (0, 0, 0)},
    'upperarm_L': {'rot': (10, -5, 15),  'loc': (0, 0, 0)},
    'forearm_L':  {'rot': (-40, 10, -10),'loc': (0, 0, 0)},
    'hand_L':     {'rot': (15, -5, 20),  'loc': (0.02, -0.03, 0.02)}
}

STANCE_2H = {
    'root':       {'loc': (0.0, 0.0, 0.0)},
    'upperarm_R': {'rot': (-6, 4, -2),   'loc': (0, 0, 0)},
    'forearm_R':  {'rot': (-12, 2, 0),   'loc': (0, 0, 0)},
    'hand_R':     {'rot': (2, -4, 2),    'loc': (0, 0, 0)},
    'weapon':     {'rot': (-6, 6, -2),   'loc': (0, 0, 0)},
    'upperarm_L': {'rot': (14, -10, 22), 'loc': (0, 0, 0)},
    'forearm_L':  {'rot': (-48, 14, -16),'loc': (0, 0, 0)},
    'hand_L':     {'rot': (16, -8, 26),  'loc': (0.03, -0.04, 0.02)}
}

# 1. PISTOLA APEX 6
PISTOL_KEYS = {
    0: STANCE_PISTOL,
    6: { # Arma se eleva e inclina exponiendo el brocal
        'root':       {'loc': (0.0, -0.03, 0.06)},
        'upperarm_R': {'rot': (-10, 12, 4), 'loc': (0, 0, 0)},
        'forearm_R':  {'rot': (8, 4, 0),    'loc': (0, 0, 0)},
        'hand_R':     {'rot': (4, -8, 6),   'loc': (0, 0, 0)},
        'weapon':     {'rot': (10, 14, -6), 'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (-15, -25, 15), 'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (10, 8, -5),    'loc': (0, 0, 0)},
        'hand_L':     {'rot': (12, 5, 15),    'loc': (0, 0, 0)}
    },
    14: { # Mano izquierda entra sosteniendo la celda de energía brillante
        'root':       {'loc': (0.0, -0.04, 0.08)},
        'upperarm_R': {'rot': (-12, 14, 4), 'loc': (0, 0, 0)},
        'forearm_R':  {'rot': (14, 4, 0),   'loc': (0, 0, 0)},
        'hand_R':     {'rot': (5, -10, 8),  'loc': (0, 0, 0)},
        'weapon':     {'rot': (14, 16, -8), 'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (-26, -34, 22), 'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (26, 12, -8),   'loc': (0, 0, 0)},
        'hand_L':     {'rot': (16, 8, 18),    'loc': (0, 0, 0)}
    },
    22: { # ENCASTRE MAGNÉTICO SECO CON LA PALMA (Pico de visibilidad)
        'root':       {'loc': (0.0, -0.04, 0.09)},
        'upperarm_R': {'rot': (-10, 12, 2), 'loc': (0, 0, 0)},
        'forearm_R':  {'rot': (16, 4, 0),   'loc': (0, 0, 0)},
        'hand_R':     {'rot': (4, -8, 6),   'loc': (0, 0, 0)},
        'weapon':     {'rot': (10, 12, -6), 'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (-28, -38, 25), 'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (35, 14, -10),  'loc': (0, 0, 0)},
        'hand_L':     {'rot': (18, 12, 22),   'loc': (0, 0, 0)}
    },
    30: { # Retroceso ligero y descenso suave de la mano izquierda
        'root':       {'loc': (0.0, -0.02, 0.03)},
        'upperarm_R': {'rot': (-5, 8, 0),   'loc': (0, 0, 0)},
        'forearm_R':  {'rot': (-2, 2, 0),   'loc': (0, 0, 0)},
        'hand_R':     {'rot': (2, -4, 2),   'loc': (0, 0, 0)},
        'weapon':     {'rot': (0, 6, -2),   'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (-8, -18, 16), 'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (-15, 8, -8),  'loc': (0, 0, 0)},
        'hand_L':     {'rot': (14, 0, 18),   'loc': (0, 0, 0)}
    },
    36: STANCE_PISTOL
}

# 2. SUBFUSIL PHASE SMG
SMG_KEYS = {
    0: STANCE_2H,
    8: { # Mano izquierda suelta empuñadura y pulsa pestillo superior
        'root':       {'loc': (0.0, -0.03, 0.06)},
        'upperarm_R': {'rot': (-8, 6, -1), 'loc': (0, 0, 0)},
        'forearm_R':  {'rot': (5, 2, 0),   'loc': (0, 0, 0)},
        'hand_R':     {'rot': (2, -4, 2),  'loc': (0, 0, 0)},
        'weapon':     {'rot': (2, 8, -2),  'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (-12, -20, 18), 'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (10, 10, -8),   'loc': (0, 0, 0)},
        'hand_L':     {'rot': (14, 4, 18),    'loc': (0, 0, 0)}
    },
    18: { # Mano izquierda presenta nuevo tambor toroidal frontal
        'root':       {'loc': (0.0, -0.04, 0.08)},
        'upperarm_R': {'rot': (-10, 8, 0), 'loc': (0, 0, 0)},
        'forearm_R':  {'rot': (10, 3, 0),  'loc': (0, 0, 0)},
        'hand_R':     {'rot': (3, -6, 4),  'loc': (0, 0, 0)},
        'weapon':     {'rot': (6, 10, -4), 'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (-22, -30, 22), 'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (22, 12, -10),  'loc': (0, 0, 0)},
        'hand_L':     {'rot': (16, 8, 20),    'loc': (0, 0, 0)}
    },
    28: { # ENCASTRE DE TAMBOR TOROIDAL FRONTAL
        'root':       {'loc': (0.0, -0.05, 0.09)},
        'upperarm_R': {'rot': (-12, 10, 2), 'loc': (0, 0, 0)},
        'forearm_R':  {'rot': (14, 4, 0),   'loc': (0, 0, 0)},
        'hand_R':     {'rot': (4, -8, 6),   'loc': (0, 0, 0)},
        'weapon':     {'rot': (8, 12, -6),  'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (-26, -36, 26), 'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (32, 15, -12),  'loc': (0, 0, 0)},
        'hand_L':     {'rot': (18, 12, 24),   'loc': (0, 0, 0)}
    },
    36: { # Mano izquierda viaja a la palanca de carga superior
        'root':       {'loc': (0.0, -0.04, 0.08)},
        'upperarm_R': {'rot': (-10, 8, 0), 'loc': (0, 0, 0)},
        'forearm_R':  {'rot': (10, 3, 0),  'loc': (0, 0, 0)},
        'hand_R':     {'rot': (3, -6, 4),  'loc': (0, 0, 0)},
        'weapon':     {'rot': (4, 8, -4),  'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (-30, -22, 16), 'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (42, 16, -8),   'loc': (0, 0, 0)},
        'hand_L':     {'rot': (15, 10, 16),   'loc': (0, 0, 0)}
    },
    42: { # TIRÓN SECO HACIA ATRÁS DE LA PALANCA DE CARGA
        'root':       {'loc': (0.0, -0.03, 0.07)},
        'upperarm_R': {'rot': (-12, 6, -1), 'loc': (0, 0, 0)},
        'forearm_R':  {'rot': (8, 2, 0),    'loc': (0, 0, 0)},
        'hand_R':     {'rot': (2, -4, 2),   'loc': (0, 0, 0)},
        'weapon':     {'rot': (0, 6, -2),   'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (-22, -18, 12), 'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (34, 12, -6),   'loc': (0, 0, 0)},
        'hand_L':     {'rot': (16, 8, 14),    'loc': (0, 0, 0)}
    },
    48: STANCE_2H
}

# 3. ESCOPETA BREACHER S4
SHOTGUN_KEYS = {
    0: STANCE_2H,
    8: { # Escopeta se inclina arriba-izquierda exponiendo compuerta ventral
        'root':       {'loc': (0.0, -0.04, 0.08)},
        'upperarm_R': {'rot': (-14, 16, 6), 'loc': (0, 0, 0)},
        'forearm_R':  {'rot': (15, 6, 2),   'loc': (0, 0, 0)},
        'hand_R':     {'rot': (6, -10, 8),  'loc': (0, 0, 0)},
        'weapon':     {'rot': (16, 18, -8), 'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (-18, -28, 20), 'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (18, 10, -8),   'loc': (0, 0, 0)},
        'hand_L':     {'rot': (14, 6, 18),    'loc': (0, 0, 0)}
    },
    18: { # Mano izquierda aproxima célula cuádruple ventral
        'root':       {'loc': (0.0, -0.05, 0.09)},
        'upperarm_R': {'rot': (-16, 18, 8), 'loc': (0, 0, 0)},
        'forearm_R':  {'rot': (18, 8, 3),   'loc': (0, 0, 0)},
        'hand_R':     {'rot': (7, -12, 10), 'loc': (0, 0, 0)},
        'weapon':     {'rot': (20, 20, -10), 'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (-26, -34, 24), 'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (28, 14, -10),  'loc': (0, 0, 0)},
        'hand_L':     {'rot': (16, 10, 20),   'loc': (0, 0, 0)}
    },
    26: { # GOLPE DE PALMA VENTRAL QUE ENCASTRA LA CÉLULA
        'root':       {'loc': (0.0, -0.05, 0.10)},
        'upperarm_R': {'rot': (-14, 16, 6), 'loc': (0, 0, 0)},
        'forearm_R':  {'rot': (16, 6, 2),   'loc': (0, 0, 0)},
        'hand_R':     {'rot': (6, -10, 8),  'loc': (0, 0, 0)},
        'weapon':     {'rot': (16, 16, -8), 'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (-28, -38, 28), 'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (36, 16, -12),  'loc': (0, 0, 0)},
        'hand_L':     {'rot': (18, 14, 24),   'loc': (0, 0, 0)}
    },
    34: { # Mano izquierda sube al guardamanos de bombeo
        'root':       {'loc': (0.0, -0.04, 0.08)},
        'upperarm_R': {'rot': (-10, 10, 2), 'loc': (0, 0, 0)},
        'forearm_R':  {'rot': (10, 4, 0),   'loc': (0, 0, 0)},
        'hand_R':     {'rot': (4, -6, 4),   'loc': (0, 0, 0)},
        'weapon':     {'rot': (6, 10, -4),  'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (-20, -28, 20), 'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (24, 12, -8),   'loc': (0, 0, 0)},
        'hand_L':     {'rot': (16, 8, 20),    'loc': (0, 0, 0)}
    },
    42: { # BOMBEO ATRÁS (ACCIONAMIENTO FÍSICO CON ANTEBRAZO COMPLETO)
        'root':       {'loc': (0.0, -0.03, 0.08)},
        'upperarm_R': {'rot': (-12, 8, 0),  'loc': (0, 0, 0)},
        'forearm_R':  {'rot': (8, 3, 0),    'loc': (0, 0, 0)},
        'hand_R':     {'rot': (3, -6, 4),   'loc': (0, 0, 0)},
        'weapon':     {'rot': (4, 8, -4),   'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (-14, -22, 16), 'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (18, 10, -6),   'loc': (0, 0, 0)},
        'hand_L':     {'rot': (14, 6, 18),    'loc': (0, 0, 0)}
    },
    48: { # BOMBEO ADELANTE (CIERRE DE LA RECÁMARA)
        'root':       {'loc': (0.0, -0.05, 0.09)},
        'upperarm_R': {'rot': (-10, 8, 0),  'loc': (0, 0, 0)},
        'forearm_R':  {'rot': (10, 3, 0),   'loc': (0, 0, 0)},
        'hand_R':     {'rot': (3, -6, 4),   'loc': (0, 0, 0)},
        'weapon':     {'rot': (4, 8, -4),   'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (-24, -32, 24), 'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (30, 14, -10),  'loc': (0, 0, 0)},
        'hand_L':     {'rot': (18, 10, 22),   'loc': (0, 0, 0)}
    },
    54: STANCE_2H
}

# 4. RIFLE VANGUARD AR
RIFLE_KEYS = {
    0: STANCE_2H,
    8: { # Mano izquierda viaja al retén de batería
        'root':       {'loc': (0.0, -0.03, 0.06)},
        'upperarm_R': {'rot': (-8, 6, -1), 'loc': (0, 0, 0)},
        'forearm_R':  {'rot': (5, 2, 0),   'loc': (0, 0, 0)},
        'hand_R':     {'rot': (2, -4, 2),  'loc': (0, 0, 0)},
        'weapon':     {'rot': (2, 8, -2),  'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (-14, -22, 18), 'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (12, 10, -8),   'loc': (0, 0, 0)},
        'hand_L':     {'rot': (14, 4, 18),    'loc': (0, 0, 0)}
    },
    18: { # Presenta petaca angular a 16 grados
        'root':       {'loc': (0.0, -0.04, 0.08)},
        'upperarm_R': {'rot': (-10, 8, 0), 'loc': (0, 0, 0)},
        'forearm_R':  {'rot': (10, 3, 0),  'loc': (0, 0, 0)},
        'hand_R':     {'rot': (3, -6, 4),  'loc': (0, 0, 0)},
        'weapon':     {'rot': (6, 10, -4), 'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (-22, -32, 22), 'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (24, 12, -10),  'loc': (0, 0, 0)},
        'hand_L':     {'rot': (16, 8, 20),    'loc': (0, 0, 0)}
    },
    26: { # ENCASTRE ROCK & LOCK CON TRINQUETE (Pico de visibilidad)
        'root':       {'loc': (0.0, -0.05, 0.09)},
        'upperarm_R': {'rot': (-12, 10, 2), 'loc': (0, 0, 0)},
        'forearm_R':  {'rot': (14, 4, 0),   'loc': (0, 0, 0)},
        'hand_R':     {'rot': (4, -8, 6),   'loc': (0, 0, 0)},
        'weapon':     {'rot': (8, 12, -6),  'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (-26, -38, 26), 'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (34, 15, -12),  'loc': (0, 0, 0)},
        'hand_L':     {'rot': (18, 12, 24),   'loc': (0, 0, 0)}
    },
    34: { # PALMADA AL LIBERADOR LATERAL DEL CERROJO (BOLT SLAP)
        'root':       {'loc': (0.0, -0.04, 0.08)},
        'upperarm_R': {'rot': (-10, 8, 0), 'loc': (0, 0, 0)},
        'forearm_R':  {'rot': (10, 3, 0),  'loc': (0, 0, 0)},
        'hand_R':     {'rot': (3, -6, 4),  'loc': (0, 0, 0)},
        'weapon':     {'rot': (4, 8, -4),  'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (-32, -26, 18), 'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (44, 18, -10),  'loc': (0, 0, 0)},
        'hand_L':     {'rot': (16, 12, 18),   'loc': (0, 0, 0)}
    },
    40: { # Impacto de la palmada y retorno
        'root':       {'loc': (0.0, -0.03, 0.07)},
        'upperarm_R': {'rot': (-12, 6, -1), 'loc': (0, 0, 0)},
        'forearm_R':  {'rot': (8, 2, 0),    'loc': (0, 0, 0)},
        'hand_R':     {'rot': (2, -4, 2),   'loc': (0, 0, 0)},
        'weapon':     {'rot': (2, 6, -2),   'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (-24, -20, 14), 'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (32, 12, -8),   'loc': (0, 0, 0)},
        'hand_L':     {'rot': (14, 8, 16),    'loc': (0, 0, 0)}
    },
    45: STANCE_2H
}

print("\n>>> EXPORTANDO SUITE FPS A FBX...")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=FPS_FBX)
arm_fps = bpy.data.objects['ARM_FPS_Arms']

SUITE = [
    ("A_FPS_Pistol_Reload", 36, PISTOL_KEYS),
    ("A_FPS_SMG_Reload", 48, SMG_KEYS),
    ("A_FPS_Shotgun_Reload", 54, SHOTGUN_KEYS),
    ("A_FPS_Rifle_Reload", 45, RIFLE_KEYS)
]

for name, frames, keys in SUITE:
    create_action(arm_fps, name, frames, keys)
    export_fbx(arm_fps, os.path.join(FBX_FPS_DIR, f"{name}.fbx"))

print("\n>>> SUITE FPS EXPORTADA EXITOSAMENTE.")

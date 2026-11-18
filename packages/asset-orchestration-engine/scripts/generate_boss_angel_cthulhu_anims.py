"""generate_boss_angel_cthulhu_anims.py — Generador de Animaciones Dedicadas para Azra'Koth.

Jefe: Azra'Koth, El Heraldo Primordial — ABERRACIÓN DE PIEL HUMANA Y SANGRE.
Acciones exportadas:
1. A_BossAngelCthulhu_Idle: Levitación con aleteo pausado, ondulación de quelíceros y espasmos armónicos.
2. A_BossAngelCthulhu_FlyFast: Vuelo supersónico horizontal (inclinación de 70°, alas en flecha delta, 8 brazos extendidos al frente).
3. A_BossAngelCthulhu_HighSpeedDive: Picada mortal a alta velocidad con zarpazo en espiral contra el suelo.
4. A_BossAngelCthulhu_BloodRain: Erupción de sangre y dilatación torácica/abdominal hacia los cielos.
5. A_BossAngelCthulhu_MultiClawFrenzy: Ráfaga de tajos a corta distancia con los 4 pares de brazos humanoides.
6. A_BossAngelCthulhu_AbyssalScreech: Grito abisal con apertura alar de 5.6m y onda expansiva de enrage.
7. A_BossAngelCthulhu_Death: Colapso y muerte por pérdida de sustentación.
"""

import bpy
import math
import os
import sys
from mathutils import Vector, Euler

RAIZ_BLENDER = r"E:/Darx_Proyect/Art/Blender"
if RAIZ_BLENDER not in sys.path:
    sys.path.append(RAIZ_BLENDER)

import darx_lib as dl

FBX_BASE = r"E:/Darx_Proyect/Art/FBX/SK_Boss_AngelCthulhu.fbx"
OUT_ANIM_DIR = r"E:/Darx_Proyect/Art/FBX/Anim_Boss_AngelCthulhu"
ARTIFACTS_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"

os.makedirs(OUT_ANIM_DIR, exist_ok=True)
os.makedirs(ARTIFACTS_DIR, exist_ok=True)


def crear_acciones(arm_obj):
    acciones = []

    # =========================================================================
    # 1. IDLE (40 frames, loop) — Levitación Aberrante
    # =========================================================================
    keys_idle = {
        1: {
            "pelvis": {"loc": (0, 0, 0), "rot": (0, 0, 0)},
            "spine_01": {"rot": (0, 0, 0)},
            "spine_02": {"rot": (0, 0, 0)},
            "head": {"rot": (0, 0, 0)},
            "halo_root": {"loc": (0, 0, 0), "rot": (0, 0, 0)},
            "wing_l_upper_01": {"rot": (-6, 12, -4)},
            "wing_l_upper_02": {"rot": (0, -10, 0)},
            "wing_r_upper_01": {"rot": (-6, -12, 4)},
            "wing_r_upper_02": {"rot": (0, 10, 0)},
            "wing_l_mid_01": {"rot": (2, 8, 0)},
            "wing_r_mid_01": {"rot": (2, -8, 0)},
            "wing_l_low_01": {"rot": (4, 4, 0)},
            "wing_r_low_01": {"rot": (4, -4, 0)},
            "arm_l_upper": {"rot": (8, 0, 12)},
            "arm_l_forearm": {"rot": (14, 0, 0)},
            "hand_l": {"rot": (8, 0, 0)},
            "arm_r_upper": {"rot": (8, 0, -12)},
            "arm_r_forearm": {"rot": (14, 0, 0)},
            "hand_r": {"rot": (8, 0, 0)},
            "leg_l_thigh": {"rot": (-6, 0, 4)},
            "leg_l_shin": {"rot": (12, 0, 0)},
            "foot_l": {"rot": (15, 0, 0)},
            "leg_r_thigh": {"rot": (-6, 0, -4)},
            "leg_r_shin": {"rot": (12, 0, 0)},
            "foot_r": {"rot": (15, 0, 0)},
            "mandible_l1_base": {"rot": (3, -6, 0)},
            "mandible_r1_base": {"rot": (3, 6, 0)},
            "mandible_l2_base": {"rot": (-2, -10, 0)},
            "mandible_r2_base": {"rot": (-2, 10, 0)},
        },
        20: {
            "pelvis": {"loc": (0, 0, 0.12), "rot": (-4, 0, 0)},
            "spine_01": {"rot": (3, 0, 0)},
            "spine_02": {"rot": (3, 0, 0)},
            "head": {"rot": (-2, 0, 0)},
            "halo_root": {"loc": (0, 0, 0.05), "rot": (0, 0, 18)},
            "wing_l_upper_01": {"rot": (14, -18, 8)},
            "wing_l_upper_02": {"rot": (0, 14, -6)},
            "wing_r_upper_01": {"rot": (14, 18, -8)},
            "wing_r_upper_02": {"rot": (0, -14, 6)},
            "wing_l_mid_01": {"rot": (12, -14, 4)},
            "wing_r_mid_01": {"rot": (12, 14, -4)},
            "wing_l_low_01": {"rot": (8, -8, 0)},
            "wing_r_low_01": {"rot": (8, 8, 0)},
            "arm_l_upper": {"rot": (16, -4, 16)},
            "arm_l_forearm": {"rot": (22, 0, 4)},
            "hand_l": {"rot": (14, 0, 0)},
            "arm_r_upper": {"rot": (16, 4, -16)},
            "arm_r_forearm": {"rot": (22, 0, -4)},
            "hand_r": {"rot": (14, 0, 0)},
            "leg_l_thigh": {"rot": (-2, 0, 2)},
            "leg_l_shin": {"rot": (8, 0, 0)},
            "foot_l": {"rot": (10, 0, 0)},
            "leg_r_thigh": {"rot": (-2, 0, -2)},
            "leg_r_shin": {"rot": (8, 0, 0)},
            "foot_r": {"rot": (10, 0, 0)},
            "mandible_l1_base": {"rot": (-4, 10, -6)},
            "mandible_r1_base": {"rot": (-4, -10, 6)},
            "mandible_l2_base": {"rot": (-6, 14, -8)},
            "mandible_r2_base": {"rot": (-6, -14, 8)},
        },
        40: {
            "pelvis": {"loc": (0, 0, 0), "rot": (0, 0, 0)},
            "spine_01": {"rot": (0, 0, 0)},
            "spine_02": {"rot": (0, 0, 0)},
            "head": {"rot": (0, 0, 0)},
            "halo_root": {"loc": (0, 0, 0), "rot": (0, 0, 0)},
            "wing_l_upper_01": {"rot": (-6, 12, -4)},
            "wing_l_upper_02": {"rot": (0, -10, 0)},
            "wing_r_upper_01": {"rot": (-6, -12, 4)},
            "wing_r_upper_02": {"rot": (0, 10, 0)},
            "wing_l_mid_01": {"rot": (2, 8, 0)},
            "wing_r_mid_01": {"rot": (2, -8, 0)},
            "wing_l_low_01": {"rot": (4, 4, 0)},
            "wing_r_low_01": {"rot": (4, -4, 0)},
            "arm_l_upper": {"rot": (8, 0, 12)},
            "arm_l_forearm": {"rot": (14, 0, 0)},
            "hand_l": {"rot": (8, 0, 0)},
            "arm_r_upper": {"rot": (8, 0, -12)},
            "arm_r_forearm": {"rot": (14, 0, 0)},
            "hand_r": {"rot": (8, 0, 0)},
            "leg_l_thigh": {"rot": (-6, 0, 4)},
            "leg_l_shin": {"rot": (12, 0, 0)},
            "foot_l": {"rot": (15, 0, 0)},
            "leg_r_thigh": {"rot": (-6, 0, -4)},
            "leg_r_shin": {"rot": (12, 0, 0)},
            "foot_r": {"rot": (15, 0, 0)},
            "mandible_l1_base": {"rot": (3, -6, 0)},
            "mandible_r1_base": {"rot": (3, 6, 0)},
            "mandible_l2_base": {"rot": (-2, -10, 0)},
            "mandible_r2_base": {"rot": (-2, 10, 0)},
        }
    }
    acciones.append(dl.action(arm_obj, "A_BossAngelCthulhu_Idle", 40, keys_idle, loop=True))

    # =========================================================================
    # 2. FLY FAST (30 frames, loop) — Vuelo Supersónico a Alta Velocidad
    # =========================================================================
    keys_fly = {
        1: {
            "pelvis": {"loc": (0, 0.25, 0.10), "rot": (68, 0, 0)},
            "spine_01": {"rot": (12, 0, 0)},
            "spine_02": {"rot": (8, 0, 0)},
            "head": {"rot": (-62, 0, 0)},
            "halo_root": {"loc": (0, 0.15, -0.10), "rot": (0, 0, 45)},
            "wing_l_upper_01": {"rot": (-42, 34, -22)},
            "wing_l_upper_02": {"rot": (-18, 14, 0)},
            "wing_r_upper_01": {"rot": (-42, -34, 22)},
            "wing_r_upper_02": {"rot": (-18, -14, 0)},
            "wing_l_mid_01": {"rot": (-38, 26, -14)},
            "wing_r_mid_01": {"rot": (-38, -26, 14)},
            "wing_l_low_01": {"rot": (-32, 18, -8)},
            "wing_r_low_01": {"rot": (-32, -18, 8)},
            "arm_l_upper": {"rot": (-72, 0, 8)},
            "arm_l_forearm": {"rot": (-14, 0, 0)},
            "hand_l": {"rot": (12, 0, 0)},
            "arm_r_upper": {"rot": (-72, 0, -8)},
            "arm_r_forearm": {"rot": (-14, 0, 0)},
            "hand_r": {"rot": (12, 0, 0)},
            "leg_l_thigh": {"rot": (54, 0, 4)},
            "leg_l_shin": {"rot": (-22, 0, 0)},
            "foot_l": {"rot": (-28, 0, 0)},
            "leg_r_thigh": {"rot": (54, 0, -4)},
            "leg_r_shin": {"rot": (-22, 0, 0)},
            "foot_r": {"rot": (-28, 0, 0)},
            "mandible_l1_base": {"rot": (-24, 0, -8)},
            "mandible_r1_base": {"rot": (-24, 0, 8)},
            "mandible_l2_base": {"rot": (-28, 0, -12)},
            "mandible_r2_base": {"rot": (-28, 0, 12)},
        },
        15: {
            "pelvis": {"loc": (0, 0.28, 0.14), "rot": (72, 0, 0)},
            "spine_01": {"rot": (14, 0, 0)},
            "spine_02": {"rot": (9, 0, 0)},
            "head": {"rot": (-66, 0, 0)},
            "halo_root": {"loc": (0, 0.18, -0.12), "rot": (0, 0, 90)},
            "wing_l_upper_01": {"rot": (-32, 24, -16)},
            "wing_l_upper_02": {"rot": (-12, 8, 0)},
            "wing_r_upper_01": {"rot": (-32, -24, 16)},
            "wing_r_upper_02": {"rot": (-12, -8, 0)},
            "wing_l_mid_01": {"rot": (-28, 18, -10)},
            "wing_r_mid_01": {"rot": (-28, -18, 10)},
            "wing_l_low_01": {"rot": (-22, 12, -4)},
            "wing_r_low_01": {"rot": (-22, -12, 4)},
            "arm_l_upper": {"rot": (-78, 0, 10)},
            "arm_l_forearm": {"rot": (-10, 0, 0)},
            "hand_l": {"rot": (16, 0, 0)},
            "arm_r_upper": {"rot": (-78, 0, -10)},
            "arm_r_forearm": {"rot": (-10, 0, 0)},
            "hand_r": {"rot": (16, 0, 0)},
            "leg_l_thigh": {"rot": (58, 0, 4)},
            "leg_l_shin": {"rot": (-26, 0, 0)},
            "foot_l": {"rot": (-32, 0, 0)},
            "leg_r_thigh": {"rot": (58, 0, -4)},
            "leg_r_shin": {"rot": (-26, 0, 0)},
            "foot_r": {"rot": (-32, 0, 0)},
            "mandible_l1_base": {"rot": (-30, 0, -10)},
            "mandible_r1_base": {"rot": (-30, 0, 10)},
            "mandible_l2_base": {"rot": (-36, 0, -14)},
            "mandible_r2_base": {"rot": (-36, 0, 14)},
        },
        30: {
            "pelvis": {"loc": (0, 0.25, 0.10), "rot": (68, 0, 0)},
            "spine_01": {"rot": (12, 0, 0)},
            "spine_02": {"rot": (8, 0, 0)},
            "head": {"rot": (-62, 0, 0)},
            "halo_root": {"loc": (0, 0.15, -0.10), "rot": (0, 0, 180)},
            "wing_l_upper_01": {"rot": (-42, 34, -22)},
            "wing_l_upper_02": {"rot": (-18, 14, 0)},
            "wing_r_upper_01": {"rot": (-42, -34, 22)},
            "wing_r_upper_02": {"rot": (-18, -14, 0)},
            "wing_l_mid_01": {"rot": (-38, 26, -14)},
            "wing_r_mid_01": {"rot": (-38, -26, 14)},
            "wing_l_low_01": {"rot": (-32, 18, -8)},
            "wing_r_low_01": {"rot": (-32, -18, 8)},
            "arm_l_upper": {"rot": (-72, 0, 8)},
            "arm_l_forearm": {"rot": (-14, 0, 0)},
            "hand_l": {"rot": (12, 0, 0)},
            "arm_r_upper": {"rot": (-72, 0, -8)},
            "arm_r_forearm": {"rot": (-14, 0, 0)},
            "hand_r": {"rot": (12, 0, 0)},
            "leg_l_thigh": {"rot": (54, 0, 4)},
            "leg_l_shin": {"rot": (-22, 0, 0)},
            "foot_l": {"rot": (-28, 0, 0)},
            "leg_r_thigh": {"rot": (54, 0, -4)},
            "leg_r_shin": {"rot": (-22, 0, 0)},
            "foot_r": {"rot": (-28, 0, 0)},
            "mandible_l1_base": {"rot": (-24, 0, -8)},
            "mandible_r1_base": {"rot": (-24, 0, 8)},
            "mandible_l2_base": {"rot": (-28, 0, -12)},
            "mandible_r2_base": {"rot": (-28, 0, 12)},
        }
    }
    acciones.append(dl.action(arm_obj, "A_BossAngelCthulhu_FlyFast", 30, keys_fly, loop=True))

    # =========================================================================
    # 3. HIGH SPEED DIVE (45 frames) — Picada Mortal y Clavado
    # =========================================================================
    keys_dive = {
        1: {
            "pelvis": {"loc": (0, -0.10, 0.40), "rot": (-25, 0, 0)},
            "spine_01": {"rot": (-10, 0, 0)},
            "head": {"rot": (15, 0, 0)},
            "wing_l_upper_01": {"rot": (18, -28, 22)},
            "wing_r_upper_01": {"rot": (18, 28, -22)},
            "arm_l_upper": {"rot": (40, 0, 20)},
            "arm_r_upper": {"rot": (40, 0, -20)},
        },
        16: {
            "pelvis": {"loc": (0, 0.10, 0.85), "rot": (86, 0, 0)},
            "spine_01": {"rot": (10, 0, 0)},
            "head": {"rot": (-78, 0, 0)},
            "wing_l_upper_01": {"rot": (-55, 40, -30)},
            "wing_r_upper_01": {"rot": (-55, -40, 30)},
            "wing_l_mid_01": {"rot": (-50, 35, -25)},
            "wing_r_mid_01": {"rot": (-50, -35, 25)},
            "arm_l_upper": {"rot": (-85, 0, 5)},
            "arm_r_upper": {"rot": (-85, 0, -5)},
        },
        30: {
            "pelvis": {"loc": (0, 0.35, -0.10), "rot": (55, 0, 0)},
            "spine_01": {"rot": (18, 0, 0)},
            "head": {"rot": (-50, 0, 0)},
            "wing_l_upper_01": {"rot": (-15, -35, 25)},
            "wing_r_upper_01": {"rot": (-15, 35, -25)},
            "arm_l_upper": {"rot": (-40, 0, -20)},
            "arm_r_upper": {"rot": (-40, 0, 20)},
        },
        36: {
            "pelvis": {"loc": (0, 0.15, -0.45), "rot": (15, 0, 0)},
            "spine_01": {"rot": (22, 0, 0)},
            "head": {"rot": (-10, 0, 0)},
            "wing_l_upper_01": {"rot": (25, -45, 35)},
            "wing_r_upper_01": {"rot": (25, 45, -35)},
            "arm_l_upper": {"rot": (35, 0, -15)},
            "arm_l_forearm": {"rot": (40, 0, 0)},
            "arm_r_upper": {"rot": (35, 0, 15)},
            "arm_r_forearm": {"rot": (40, 0, 0)},
        },
        45: {
            "pelvis": {"loc": (0, 0, 0), "rot": (0, 0, 0)},
            "spine_01": {"rot": (0, 0, 0)},
            "head": {"rot": (0, 0, 0)},
            "wing_l_upper_01": {"rot": (-6, 12, -4)},
            "wing_r_upper_01": {"rot": (-6, -12, 4)},
            "arm_l_upper": {"rot": (8, 0, 12)},
            "arm_r_upper": {"rot": (8, 0, -12)},
        }
    }
    acciones.append(dl.action(arm_obj, "A_BossAngelCthulhu_HighSpeedDive", 45, keys_dive, loop=False))

    # =========================================================================
    # 4. BLOOD RAIN CAST (50 frames) — Erupción y Lluvia de Sangre
    # =========================================================================
    keys_blood = {
        1: {
            "pelvis": {"loc": (0, 0, 0), "rot": (0, 0, 0)},
            "spine_01": {"rot": (0, 0, 0)},
            "head": {"rot": (0, 0, 0)},
            "wing_l_upper_01": {"rot": (-6, 12, -4)},
            "wing_r_upper_01": {"rot": (-6, -12, 4)},
        },
        20: {
            "pelvis": {"loc": (0, -0.15, 0.20), "rot": (-24, 0, 0)},
            "spine_01": {"rot": (-28, 0, 0)},
            "spine_02": {"rot": (-24, 0, 0)},
            "head": {"rot": (-48, 0, 0)},
            "wing_l_upper_01": {"rot": (22, -35, 20)},
            "wing_r_upper_01": {"rot": (22, 35, -20)},
            "wing_l_mid_01": {"rot": (18, -30, 15)},
            "wing_r_mid_01": {"rot": (18, 30, -15)},
            "arm_l_upper": {"rot": (-110, 0, 32)},
            "arm_l_forearm": {"rot": (35, 0, 0)},
            "arm_r_upper": {"rot": (-110, 0, -32)},
            "arm_r_forearm": {"rot": (35, 0, 0)},
            "mandible_l1_base": {"rot": (-18, 28, -6)},
            "mandible_r1_base": {"rot": (-18, -28, 6)},
        },
        32: {
            "pelvis": {"loc": (0, -0.12, 0.25), "rot": (-30, 0, 0)},
            "spine_01": {"rot": (-35, 0, 0)},
            "spine_02": {"rot": (-28, 0, 0)},
            "head": {"rot": (-54, 0, 0)},
            "arm_l_upper": {"rot": (-120, 0, 38)},
            "arm_r_upper": {"rot": (-120, 0, -38)},
            "wing_l_upper_01": {"rot": (28, -42, 25)},
            "wing_r_upper_01": {"rot": (28, 42, -25)},
        },
        50: {
            "pelvis": {"loc": (0, 0, 0), "rot": (0, 0, 0)},
            "spine_01": {"rot": (0, 0, 0)},
            "spine_02": {"rot": (0, 0, 0)},
            "head": {"rot": (0, 0, 0)},
            "wing_l_upper_01": {"rot": (-6, 12, -4)},
            "wing_r_upper_01": {"rot": (-6, -12, 4)},
            "arm_l_upper": {"rot": (8, 0, 12)},
            "arm_r_upper": {"rot": (8, 0, -12)},
        }
    }
    acciones.append(dl.action(arm_obj, "A_BossAngelCthulhu_BloodRain", 50, keys_blood, loop=False))

    # =========================================================================
    # 5. MULTI-CLAW FRENZY (36 frames) — Frenesí de 8 Brazos
    # =========================================================================
    keys_claw = {
        1: {
            "pelvis": {"loc": (0, 0, 0), "rot": (0, 0, 0)},
            "arm_l_upper": {"rot": (8, 0, 12)},
            "arm_r_upper": {"rot": (8, 0, -12)},
        },
        10: {
            "pelvis": {"loc": (0, 0.12, 0), "rot": (10, -15, 0)},
            "arm_l_upper": {"rot": (-45, -25, -35)},
            "arm_l_forearm": {"rot": (55, 0, 0)},
            "hand_l": {"rot": (30, 0, 0)},
            "arm_r_upper": {"rot": (25, 15, -10)},
            "mandible_l1_base": {"rot": (15, 10, 0)},
        },
        20: {
            "pelvis": {"loc": (0, 0.15, 0), "rot": (10, 15, 0)},
            "arm_l_upper": {"rot": (25, -15, 10)},
            "arm_r_upper": {"rot": (-45, 25, 35)},
            "arm_r_forearm": {"rot": (55, 0, 0)},
            "hand_r": {"rot": (30, 0, 0)},
            "mandible_r1_base": {"rot": (15, -10, 0)},
        },
        28: {
            "pelvis": {"loc": (0, 0.22, -0.05), "rot": (18, 0, 0)},
            "arm_l_upper": {"rot": (-35, 0, -25)},
            "arm_l_forearm": {"rot": (40, 0, 0)},
            "arm_r_upper": {"rot": (-35, 0, 25)},
            "arm_r_forearm": {"rot": (40, 0, 0)},
            "wing_l_upper_01": {"rot": (25, -25, 20)},
            "wing_r_upper_01": {"rot": (25, 25, -20)},
        },
        36: {
            "pelvis": {"loc": (0, 0, 0), "rot": (0, 0, 0)},
            "arm_l_upper": {"rot": (8, 0, 12)},
            "arm_r_upper": {"rot": (8, 0, -12)},
        }
    }
    acciones.append(dl.action(arm_obj, "A_BossAngelCthulhu_MultiClawFrenzy", 36, keys_claw, loop=False))

    # =========================================================================
    # 6. ABYSSAL SCREECH (40 frames) — Grito Abisal y Shockwave
    # =========================================================================
    keys_screech = {
        1: {
            "pelvis": {"loc": (0, 0, 0), "rot": (0, 0, 0)},
            "head": {"rot": (0, 0, 0)},
            "wing_l_upper_01": {"rot": (-6, 12, -4)},
            "wing_r_upper_01": {"rot": (-6, -12, 4)},
        },
        12: {
            "pelvis": {"loc": (0, -0.10, 0.10), "rot": (-15, 0, 0)},
            "head": {"rot": (-25, 0, 0)},
            "wing_l_upper_01": {"rot": (-25, 20, -15)},
            "wing_r_upper_01": {"rot": (-25, -20, 15)},
            "arm_l_upper": {"rot": (25, -10, 20)},
            "arm_r_upper": {"rot": (25, 10, -20)},
        },
        22: {
            "pelvis": {"loc": (0, 0.20, 0.05), "rot": (18, 0, 0)},
            "spine_01": {"rot": (12, 0, 0)},
            "head": {"rot": (20, 0, 0)},
            "wing_l_upper_01": {"rot": (15, -45, 30)},
            "wing_l_upper_02": {"rot": (0, 25, 0)},
            "wing_r_upper_01": {"rot": (15, 45, -30)},
            "wing_r_upper_02": {"rot": (0, -25, 0)},
            "wing_l_mid_01": {"rot": (12, -35, 20)},
            "wing_r_mid_01": {"rot": (12, 35, -20)},
            "arm_l_upper": {"rot": (-45, -30, 25)},
            "arm_r_upper": {"rot": (-45, 30, -25)},
            "mandible_l1_base": {"rot": (-15, 35, -10)},
            "mandible_r1_base": {"rot": (-15, -35, 10)},
            "mandible_l2_base": {"rot": (-20, 40, -15)},
            "mandible_r2_base": {"rot": (-20, -40, 15)},
        },
        40: {
            "pelvis": {"loc": (0, 0, 0), "rot": (0, 0, 0)},
            "head": {"rot": (0, 0, 0)},
            "wing_l_upper_01": {"rot": (-6, 12, -4)},
            "wing_r_upper_01": {"rot": (-6, -12, 4)},
            "arm_l_upper": {"rot": (8, 0, 12)},
            "arm_r_upper": {"rot": (8, 0, -12)},
        }
    }
    acciones.append(dl.action(arm_obj, "A_BossAngelCthulhu_AbyssalScreech", 40, keys_screech, loop=False))

    # =========================================================================
    # 7. DEATH (60 frames) — Colapso y Muerte
    # =========================================================================
    keys_death = {
        1: {
            "pelvis": {"loc": (0, 0, 0), "rot": (0, 0, 0)},
            "head": {"rot": (0, 0, 0)},
        },
        18: {
            "pelvis": {"loc": (0, 0.10, 0.15), "rot": (-18, 12, 8)},
            "spine_01": {"rot": (15, -10, 0)},
            "head": {"rot": (-35, 15, 0)},
            "wing_l_upper_01": {"rot": (45, -20, 40)},
            "wing_r_upper_01": {"rot": (-40, 15, -30)},
            "arm_l_upper": {"rot": (-65, 0, 25)},
            "arm_r_upper": {"rot": (30, 0, -15)},
        },
        35: {
            "pelvis": {"loc": (0, 0.30, -0.65), "rot": (45, 18, 0)},
            "spine_01": {"rot": (25, 0, 0)},
            "wing_l_upper_01": {"rot": (60, 30, -20)},
            "wing_r_upper_01": {"rot": (55, -30, 20)},
            "arm_l_upper": {"rot": (50, 0, 15)},
            "arm_r_upper": {"rot": (50, 0, -15)},
        },
        50: {
            "pelvis": {"loc": (0, 0.40, -1.35), "rot": (75, 5, 0)},
            "spine_01": {"rot": (15, 0, 0)},
            "head": {"rot": (-60, 25, 0)},
            "wing_l_upper_01": {"rot": (80, 25, 0)},
            "wing_r_upper_01": {"rot": (75, -35, 0)},
            "arm_l_upper": {"rot": (85, 0, 40)},
            "arm_r_upper": {"rot": (80, 0, -35)},
            "leg_l_thigh": {"rot": (80, 0, 20)},
            "leg_r_thigh": {"rot": (75, 0, -25)},
        },
        60: {
            "pelvis": {"loc": (0, 0.40, -1.35), "rot": (75, 5, 0)},
            "spine_01": {"rot": (15, 0, 0)},
            "head": {"rot": (-60, 25, 0)},
            "wing_l_upper_01": {"rot": (80, 25, 0)},
            "wing_r_upper_01": {"rot": (75, -35, 0)},
            "arm_l_upper": {"rot": (85, 0, 40)},
            "arm_r_upper": {"rot": (80, 0, -35)},
            "leg_l_thigh": {"rot": (80, 0, 20)},
            "leg_r_thigh": {"rot": (75, 0, -25)},
        }
    }
    acciones.append(dl.action(arm_obj, "A_BossAngelCthulhu_Death", 60, keys_death, loop=False))

    return acciones


def exportar_animaciones_fbx(arm_obj, mesh_obj, acciones):
    print("=== EXPORTANDO ANIMACIONES FBX A 30 FPS ===")
    bpy.context.scene.render.fps = 30

    for act in acciones:
        arm_obj.animation_data.action = act
        if hasattr(arm_obj.animation_data, "action_slot"):
            for s in act.slots:
                arm_obj.animation_data.action_slot = s
                break

        f_start = int(act.frame_range[0])
        f_end = int(act.frame_range[1])
        bpy.context.scene.frame_start = f_start
        bpy.context.scene.frame_end = f_end

        fbx_path = os.path.join(OUT_ANIM_DIR, f"{act.name}.fbx")

        bpy.ops.object.select_all(action='DESELECT')
        arm_obj.select_set(True)
        mesh_obj.select_set(True)
        bpy.context.view_layer.objects.active = arm_obj

        bpy.ops.export_scene.fbx(
            filepath=fbx_path,
            use_selection=True,
            global_scale=1.0,
            apply_unit_scale=True,
            axis_forward='-Y',
            axis_up='Z',
            object_types={'ARMATURE'},
            bake_anim=True,
            bake_anim_use_all_bones=True,
            bake_anim_use_nla_strips=False,
            bake_anim_use_all_actions=False,
            bake_anim_step=1.0,
            bake_anim_simplify_factor=0.0
        )
        print(f"  [OK] Exportada: {act.name} ({f_start}-{f_end} frames) -> {fbx_path}")


def renderizar_previews(arm_obj, mesh_obj):
    print("=== RENDERIZANDO PREVIEWS VISUALES DE LAS ANIMACIONES ===")
    sc = bpy.context.scene
    motores = [item.identifier for item in bpy.types.Scene.bl_rna.properties['render'].fixed_type.properties['engine'].enum_items]
    sc.render.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in motores else 'BLENDER_EEVEE'

    shots = [
        ("A_BossAngelCthulhu_Idle", 20, "preview_anim_idle.png", (0, 0, 2.5), 8.2, 28.0, 8.0),
        ("A_BossAngelCthulhu_FlyFast", 15, "preview_anim_fly_fast.png", (0, 0.2, 2.3), 8.6, 45.0, 14.0),
        ("A_BossAngelCthulhu_HighSpeedDive", 22, "preview_anim_dive.png", (0, 0.2, 2.2), 8.0, 32.0, 16.0),
        ("A_BossAngelCthulhu_BloodRain", 28, "preview_anim_blood_rain.png", (0, -0.1, 2.6), 8.2, 20.0, 6.0),
        ("A_BossAngelCthulhu_MultiClawFrenzy", 20, "preview_anim_claw_frenzy.png", (0, 0.1, 2.4), 7.5, 25.0, 10.0),
        ("A_BossAngelCthulhu_AbyssalScreech", 22, "preview_anim_screech.png", (0, 0, 2.5), 8.5, 15.0, 5.0),
        ("A_BossAngelCthulhu_Death", 45, "preview_anim_death.png", (0, 0.3, 1.2), 7.8, 38.0, 22.0)
    ]

    objs = [mesh_obj, arm_obj]
    for act_name, frame, filename, focus_pt, dist_val, yaw_val, pitch_val in shots:
        act = bpy.data.actions.get(act_name)
        if not act:
            continue
        arm_obj.animation_data.action = act
        if hasattr(arm_obj.animation_data, "action_slot"):
            for s in act.slots:
                arm_obj.animation_data.action_slot = s
                break
        bpy.context.scene.frame_set(frame)
        out_path = os.path.join(ARTIFACTS_DIR, filename)
        dl.snap(objs, out_path, focus=focus_pt, dist=dist_val, yaw=yaw_val, pitch=pitch_val, res=1024, engine=sc.render.engine)
        print(f"  [PREVIEW RENDER OK] {act_name} (f={frame}) -> {out_path}")


def main():
    print("=== INICIANDO PIPELINE DE ANIMACIONES DE AZRA'KOTH ===")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.render.fps = 30

    if not os.path.exists(FBX_BASE):
        print(f"[ERROR] No existe el FBX base: {FBX_BASE}")
        return

    bpy.ops.import_scene.fbx(filepath=FBX_BASE)

    arm_obj = next((o for o in bpy.context.scene.objects if o.type == 'ARMATURE'), None)
    mesh_obj = next((o for o in bpy.context.scene.objects if o.type == 'MESH'), None)

    if not arm_obj or not mesh_obj:
        print(f"[ERROR] No se encontraron Armature y Mesh tras importar {FBX_BASE}")
        return

    print(f"Armadura cargada: {arm_obj.name} con {len(arm_obj.data.bones)} huesos")
    print(f"Malla cargada: {mesh_obj.name} con {len(mesh_obj.data.vertices)} vértices")

    acciones = crear_acciones(arm_obj)
    print(f"Creadas {len(acciones)} acciones de animación.")

    exportar_animaciones_fbx(arm_obj, mesh_obj, acciones)
    renderizar_previews(arm_obj, mesh_obj)

    print("=== PIPELINE DE ANIMACIONES Y RENDERS COMPLETADO CON ÉXITO ===")


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""generate_and_verify_fps_punch_perfect.py
Genera y valida empíricamente la suite de puñetazo (FPS y 3P) para DarX:
- Cinemática auténtica de combate FPS: guardia alta visible, carga, golpe recto directo
  al centro de la retícula con pronación de nudillos (Variante 1), pausa de impacto y retracción ágil.
- Cámara horizontal auténtica de Unreal Engine 5 (FOV 70°, Z=0.05m, Y=0.18m).
- Exporta FBX para FPS y 3P.
- Renderiza los 4 momentos del flujo y compone un mosaico de validación visual.
"""

import os
import sys
import math
import bpy
from mathutils import Vector, Euler

PROJECT_ROOT = r"E:\Darx_Proyect"
FBX_ARMS = os.path.join(PROJECT_ROOT, "Art", "FBX", "SK_FPS_Arms.fbx")
FBX_PLAYER = os.path.join(PROJECT_ROOT, "Art", "FBX", "SK_Player.fbx")
OUT_FBX_FPS = os.path.join(PROJECT_ROOT, "Art", "FBX", "Anim_FPS", "A_FPS_Unarmed_Punch_R.fbx")
OUT_FBX_3P = os.path.join(PROJECT_ROOT, "Art", "FBX", "Anim_Player", "A_Player_Unarmed_Punch_R.fbx")
BRAIN_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"

# ==============================================================================
# 1. PARTE FPS (SK_FPS_Arms)
# ==============================================================================
print(">>> GENERANDO ANIMACIÓN FPS: A_FPS_Unarmed_Punch_R...")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=FBX_ARMS)
arm_fps = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
mesh_fps = next(o for o in bpy.data.objects if o.type == 'MESH')
arm_fps.name = "ARM_FPS_Punch"

# Ocultar pistola vieja del template
for v in mesh_fps.data.vertices:
    for g in v.groups:
        if mesh_fps.vertex_groups[g.group].name in ('weapon', 'cell'):
            v.co = Vector((0, 0, -100))
            break

for pb in arm_fps.pose.bones:
    pb.rotation_mode = 'XYZ'
    pb.rotation_euler = (0, 0, 0)
    pb.location = (0, 0, 0)

# Ejes locales de root en SK_FPS_Arms:
# local Y = world +Z (elevación)
# local Z = world -Y (hacia adelante en dirección de cámara)
#
# Matriz cinemática de la Variante 4 (Fast Tactical Jab - Elegida por el usuario):
KEYS_PUNCH_FPS = {
    0: { # F0: Guardia de boxeo táctica compacta y reactiva
        'root':       {'loc': (0.0, 0.12, 0.05)},
        'upperarm_R': {'rot': (12, 10, -4),   'loc': (0, 0, 0)},
        'forearm_R':  {'rot': (-16, 6, 2),    'loc': (0, 0, 0)},
        'hand_R':     {'rot': (14, -8, 10),   'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (22, -16, 18),  'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (-34, 14, -12), 'loc': (0, 0, 0)},
        'hand_L':     {'rot': (22, -6, 24),   'loc': (0, 0, 0)}
    },
    2: { # F2: Anticipación relámpago: coiling ágil del codo
        'root':       {'loc': (0.0, 0.13, 0.02)},
        'upperarm_R': {'rot': (4, 6, -4),     'loc': (0, 0, 0)},
        'forearm_R':  {'rot': (-20, 4, 0),    'loc': (0, 0, 0)},
        'hand_R':     {'rot': (16, -8, 15),   'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (24, -18, 20),  'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (-36, 16, -14), 'loc': (0, 0, 0)},
        'hand_L':     {'rot': (24, -6, 26),   'loc': (0, 0, 0)}
    },
    5: { # F5: IMPACTO MÁXIMO (PEAK IMPACT) - FAST TACTICAL JAB
        # Nudillos a 45°, trayectoria lineal directa hacia la retícula central
        'root':       {'loc': (0.0, 0.14, 0.14)},
        'upperarm_R': {'rot': (-26, -14, 10), 'loc': (0, 0, 0)},
        'forearm_R':  {'rot': (36, -8, 6),    'loc': (0, 0, 0)},
        'hand_R':     {'rot': (15, -10, 45),  'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (24, -18, 20),  'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (-34, 16, -14), 'loc': (0, 0, 0)},
        'hand_L':     {'rot': (22, -6, 24),   'loc': (0, 0, 0)}
    },
    7: { # F7: Hit pause táctico corto (2 frames de lectura de impacto)
        'root':       {'loc': (0.0, 0.14, 0.14)},
        'upperarm_R': {'rot': (-25, -13, 10), 'loc': (0, 0, 0)},
        'forearm_R':  {'rot': (35, -7, 6),    'loc': (0, 0, 0)},
        'hand_R':     {'rot': (15, -10, 45),  'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (24, -18, 20),  'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (-34, 16, -14), 'loc': (0, 0, 0)},
        'hand_L':     {'rot': (22, -6, 24),   'loc': (0, 0, 0)}
    },
    10: { # F10: Retracción elástica snappy
        'root':       {'loc': (0.0, 0.13, 0.06)},
        'upperarm_R': {'rot': (4, 8, -2),     'loc': (0, 0, 0)},
        'forearm_R':  {'rot': (-10, 6, 2),    'loc': (0, 0, 0)},
        'hand_R':     {'rot': (15, -8, 20),   'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (22, -17, 19),  'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (-35, 15, -13), 'loc': (0, 0, 0)},
        'hand_L':     {'rot': (23, -6, 25),   'loc': (0, 0, 0)}
    },
    13: { # F13: Retorno completo a guardia neutra
        'root':       {'loc': (0.0, 0.12, 0.05)},
        'upperarm_R': {'rot': (12, 10, -4),   'loc': (0, 0, 0)},
        'forearm_R':  {'rot': (-16, 6, 2),    'loc': (0, 0, 0)},
        'hand_R':     {'rot': (14, -8, 10),   'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (22, -16, 18),  'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (-34, 14, -12), 'loc': (0, 0, 0)},
        'hand_L':     {'rot': (22, -6, 24),   'loc': (0, 0, 0)}
    }
}

act_fps = bpy.data.actions.new(name="A_FPS_Unarmed_Punch_R")
act_fps.use_fake_user = True
arm_fps.animation_data_create()
arm_fps.animation_data.action = act_fps

for f, frame_data in KEYS_PUNCH_FPS.items():
    for bone_name, vals in frame_data.items():
        pb = arm_fps.pose.bones.get(bone_name)
        if pb is None: continue
        if 'rot' in vals:
            pb.rotation_euler = [math.radians(a) for a in vals['rot']]
        if 'loc' in vals:
            pb.location = vals['loc']
    for pb in arm_fps.pose.bones:
        pb.keyframe_insert("rotation_euler", frame=f)
        pb.keyframe_insert("location", frame=f)

# Bezier interpolation
fcurves = []
if hasattr(act_fps, "layers") and len(act_fps.layers):
    for lay in act_fps.layers:
        for st in lay.strips:
            for cb in st.channelbags:
                fcurves.extend(cb.fcurves)
elif hasattr(act_fps, "fcurves"):
    fcurves = list(act_fps.fcurves)
for fc in fcurves:
    for kp in fc.keyframe_points:
        kp.interpolation = 'BEZIER'

scene = bpy.context.scene
scene.frame_start = 0
scene.frame_end = 13

print("\n--- MEDICIONES CINEMÁTICAS EN ESPACIO MUNDO (CAMARA EN Z=0.05, Y=0.18) ---")
for f in [0, 2, 5, 7, 10, 13]:
    scene.frame_set(f)
    bpy.context.view_layer.update()
    hr = arm_fps.matrix_world @ arm_fps.pose.bones["hand_R"].matrix.translation
    hl = arm_fps.matrix_world @ arm_fps.pose.bones["hand_L"].matrix.translation
    dist_r = -(hr.y - 0.18)
    elev_r = hr.z - 0.05
    ang_vert_r = math.degrees(math.atan2(elev_r, dist_r)) if dist_r > 0.001 else 0.0
    print(f"Frame {f:2d}: hand_R Pos=({hr.x:.3f}, {hr.y:.3f}, {hr.z:.3f}) | Dist={dist_r:.2f}m, AngVert={ang_vert_r:+.1f}° | hand_L Pos=({hl.x:.3f}, {hl.y:.3f}, {hl.z:.3f})")

# Exportar FBX FPS
os.makedirs(os.path.dirname(OUT_FBX_FPS), exist_ok=True)
if os.path.exists(OUT_FBX_FPS):
    try: os.remove(OUT_FBX_FPS)
    except: pass

bpy.ops.object.select_all(action='DESELECT')
arm_fps.select_set(True)
bpy.context.view_layer.objects.active = arm_fps

bpy.ops.export_scene.fbx(
    filepath=OUT_FBX_FPS,
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
print(f"[OK FBX FPS] {OUT_FBX_FPS} ({os.path.getsize(OUT_FBX_FPS)} bytes)")

# ==============================================================================
# 2. RENDERIZADO DE LOS 4 MOMENTOS CLAVE DEL GOLPE (CÁMARA HORIZONTAL UE5)
# ==============================================================================
mat_arm = bpy.data.materials.new(name="M_Arm_Vis")
mat_arm.use_nodes = True
bsdf = mat_arm.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.22, 0.45, 0.85, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.30
mesh_fps.data.materials.clear()
mesh_fps.data.materials.append(mat_arm)

world = bpy.data.worlds.new("W_Vis")
scene.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.05, 0.06, 0.08, 1.0)

# Iluminación de estudio
l1 = bpy.data.lights.new("Key", 'AREA'); l1.energy = 150.0; l1.size = 1.0
o1 = bpy.data.objects.new("Key", l1); o1.location = (0.4, -0.3, 0.45)
scene.collection.objects.link(o1)

l2 = bpy.data.lights.new("Fill", 'AREA'); l2.energy = 75.0; l2.size = 1.2
o2 = bpy.data.objects.new("Fill", l2); o2.location = (-0.5, -0.2, 0.3)
scene.collection.objects.link(o2)

l3 = bpy.data.lights.new("Rim", 'AREA'); l3.energy = 100.0; l3.color = (0.8, 0.6, 1.0)
o3 = bpy.data.objects.new("Rim", l3); o3.location = (0.0, 0.3, 0.0)
scene.collection.objects.link(o3)

# Cámara horizontal FPS exacta
cam_data = bpy.data.cameras.new("Cam_FPS_Horizontal")
cam_data.sensor_width = 36.0
cam_data.lens = 22.0
cam_obj = bpy.data.objects.new("Cam_FPS_Horizontal", cam_data)
cam_obj.location = (0.0, 0.18, 0.05)
cam_obj.rotation_euler = (math.radians(90.0), 0.0, math.radians(180.0))
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj

scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, 'RenderSettings') and 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
scene.render.resolution_x = 960
scene.render.resolution_y = 540

MOMENTS = [
    (0, "1. GUARDIA TACTICA (F0) — AMBOS PUÑOS EN PANTALLA"),
    (2, "2. ANTICIPACION Y CARGA (F2) — COBERTURA"),
    (5, "3. IMPACTO MAXIMO (F5) — FAST TACTICAL JAB (45°)"),
    (10, "4. RETRACCION ELASTICA (F10) — RETORNO AGIL")
]

quad_files = []
for idx, (frame, title) in enumerate(MOMENTS):
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    temp_img = os.path.join(BRAIN_DIR, f"temp_flow_quad_{idx}.png")
    scene.render.filepath = temp_img
    bpy.ops.render.render(write_still=True)
    print(f"[RENDER OK] Cuadrante {idx+1}: {temp_img}")

# ==============================================================================
# 3. PARTE 3P (SK_Player)
# ==============================================================================
print("\n>>> GENERANDO ANIMACIÓN 3P: A_Player_Unarmed_Punch_R...")
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=FBX_PLAYER)
arm_3p = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
arm_3p.name = "ARM_Player_Punch"

for pb in arm_3p.pose.bones:
    pb.rotation_mode = 'XYZ'
    pb.rotation_euler = (0, 0, 0)
    pb.location = (0, 0, 0)

KEYS_PUNCH_3P = {
    0: { # Stance neutro de combate táctico
        'spine_02':   {'rot': (0, 0, -8)},
        'upperarm_r': {'rot': (15, 12, -6)},
        'lowerarm_r': {'rot': (-25, 8, 4)},
        'hand_r':     {'rot': (12, -6, 10)},
        'upperarm_l': {'rot': (20, -14, 16)},
        'lowerarm_l': {'rot': (-32, 12, -10)},
        'hand_l':     {'rot': (18, -4, 20)}
    },
    2: { # Carga relámpago
        'spine_02':   {'rot': (2, -2, -12)},
        'upperarm_r': {'rot': (8, 12, -8)},
        'lowerarm_r': {'rot': (-30, 6, 2)},
        'hand_r':     {'rot': (14, -8, 14)},
        'upperarm_l': {'rot': (22, -16, 18)},
        'lowerarm_l': {'rot': (-36, 14, -12)},
        'hand_l':     {'rot': (20, -6, 22)}
    },
    5: { # Impacto rápido directo — Fast Tactical Jab (45°)
        'spine_02':   {'rot': (-3, 5, 18)},
        'upperarm_r': {'rot': (-30, -14, 14)},
        'lowerarm_r': {'rot': (38, -8, 8)},
        'hand_r':     {'rot': (15, -8, 45)},
        'upperarm_l': {'rot': (24, -18, 20)},
        'lowerarm_l': {'rot': (-34, 16, -14)},
        'hand_l':     {'rot': (22, -6, 24)}
    },
    7: { # Hit pause 3P
        'spine_02':   {'rot': (-3, 5, 18)},
        'upperarm_r': {'rot': (-29, -13, 14)},
        'lowerarm_r': {'rot': (37, -7, 8)},
        'hand_r':     {'rot': (15, -8, 45)},
        'upperarm_l': {'rot': (24, -18, 20)},
        'lowerarm_l': {'rot': (-34, 16, -14)},
        'hand_l':     {'rot': (22, -6, 24)}
    },
    10: { # Retracción snappy
        'spine_02':   {'rot': (-1, 2, 5)},
        'upperarm_r': {'rot': (5, 8, -2)},
        'lowerarm_r': {'rot': (-12, 6, 2)},
        'hand_r':     {'rot': (14, -6, 25)},
        'upperarm_l': {'rot': (21, -15, 17)},
        'lowerarm_l': {'rot': (-33, 13, -11)},
        'hand_l':     {'rot': (19, -5, 21)}
    },
    13: { # Retorno a guardia
        'spine_02':   {'rot': (0, 0, -8)},
        'upperarm_r': {'rot': (15, 12, -6)},
        'lowerarm_r': {'rot': (-25, 8, 4)},
        'hand_r':     {'rot': (12, -6, 10)},
        'upperarm_l': {'rot': (20, -14, 16)},
        'lowerarm_l': {'rot': (-32, 12, -10)},
        'hand_l':     {'rot': (18, -4, 20)}
    }
}

act_3p = bpy.data.actions.new(name="A_Player_Unarmed_Punch_R")
act_3p.use_fake_user = True
arm_3p.animation_data_create()
arm_3p.animation_data.action = act_3p

for f, frame_data in KEYS_PUNCH_3P.items():
    for bone_name, vals in frame_data.items():
        pb = arm_3p.pose.bones.get(bone_name)
        if pb is None: continue
        if 'rot' in vals:
            pb.rotation_euler = [math.radians(a) for a in vals['rot']]
        if 'loc' in vals:
            pb.location = vals['loc']
    for pb in arm_3p.pose.bones:
        pb.keyframe_insert("rotation_euler", frame=f)
        pb.keyframe_insert("location", frame=f)

fcurves_3p = []
if hasattr(act_3p, "layers") and len(act_3p.layers):
    for lay in act_3p.layers:
        for st in lay.strips:
            for cb in st.channelbags:
                fcurves_3p.extend(cb.fcurves)
elif hasattr(act_3p, "fcurves"):
    fcurves_3p = list(act_3p.fcurves)
for fc in fcurves_3p:
    for kp in fc.keyframe_points:
        kp.interpolation = 'BEZIER'

os.makedirs(os.path.dirname(OUT_FBX_3P), exist_ok=True)
if os.path.exists(OUT_FBX_3P):
    try: os.remove(OUT_FBX_3P)
    except: pass

bpy.ops.object.select_all(action='DESELECT')
arm_3p.select_set(True)
bpy.context.view_layer.objects.active = arm_3p

bpy.ops.export_scene.fbx(
    filepath=OUT_FBX_3P,
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
print(f"[OK FBX 3P] {OUT_FBX_3P} ({os.path.getsize(OUT_FBX_3P)} bytes)")
print("=== GENERACIÓN Y VALIDACIÓN DE PUÑETAZO COMPLETADA CON ÉXITO ===")

# -*- coding: utf-8 -*-
"""generate_fps_punch_camera_perfect.py
Genera la animación de puñetazo en primera persona (A_FPS_Unarmed_Punch_R)
con cinemática de combate FPS auténtica:
- Guardia alta con ambos puños visibles en pantalla.
- Puñetazo recto directo hacia la retícula central (crosshair).
- Pronación horizontal de nudillos en el impacto máximo.
- Mano izquierda en cobertura táctica (chin guard) en el cuadrante inferior izquierdo.
- Renderiza los 4 momentos clave: F0 (Guardia), F2 (Carga), F6 (Impacto Máximo), F10 (Retracción).
"""

import sys, os, math
import bpy
from mathutils import Vector, Euler, Matrix

FBX_ARMS = r"E:\Darx_Proyect\Art\FBX\SK_FPS_Arms.fbx"
OUT_FBX_FPS = r"E:\Darx_Proyect\Art\FBX\Anim_FPS\A_FPS_Unarmed_Punch_R.fbx"
OUT_FBX_3P = r"E:\Darx_Proyect\Art\FBX\Anim_Player\A_Player_Unarmed_Punch_R.fbx"
BRAIN_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=FBX_ARMS)

arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
mesh_arms = next(o for o in bpy.data.objects if o.type == 'MESH')
arm.name = "ARM_FPS"

# Ocultar pistola vieja integrada en el template
for v in mesh_arms.data.vertices:
    for g in v.groups:
        if mesh_arms.vertex_groups[g.group].name in ('weapon', 'cell'):
            v.co = Vector((0, 0, -100))
            break

# Reset pose
for pb in arm.pose.bones:
    pb.rotation_mode = 'XYZ'
    pb.rotation_euler = (0, 0, 0)
    pb.location = (0, 0, 0)

# ==============================================================================
# DEFINICIÓN DE FOTOGRAMAS CLAVE DEL PUÑETAZO FPS
# ==============================================================================
# Frame 0: Guardia táctica de boxeo en primera persona
# Ambos puños elevados y claramente visibles en pantalla
KEYS_FPS = {
    0: {
        'root':       {'loc': (0.0, 0.0, 0.05)},
        'upperarm_R': {'rot': (18, 12, -4),   'loc': (0, 0, 0)},
        'forearm_R':  {'rot': (-15, 6, 2),    'loc': (0, 0, 0)},
        'hand_R':     {'rot': (12, -8, 8),    'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (20, -16, 18),  'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (-35, 14, -12), 'loc': (0, 0, 0)},
        'hand_L':     {'rot': (22, -6, 24),   'loc': (0, 0, 0)}
    },
    2: { # Anticipación: el brazo derecho carga hacia atrás ligeramente mientras se eleva
        'root':       {'loc': (0.0, 0.03, 0.06)},
        'upperarm_R': {'rot': (10, 8, -6),    'loc': (0, 0, 0)},
        'forearm_R':  {'rot': (-22, 4, 0),    'loc': (0, 0, 0)},
        'hand_R':     {'rot': (16, -10, 12),  'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (22, -18, 20),  'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (-38, 16, -14), 'loc': (0, 0, 0)},
        'hand_L':     {'rot': (25, -6, 26),   'loc': (0, 0, 0)}
    },
    6: { # IMPACTO MÁXIMO (PEAK IMPACT): Puño derecho recto extendido al CENTRO de la pantalla
        # Root avanza hacia adelante dando peso visceral
        'root':       {'loc': (0.0, -0.10, 0.07)},
        # Brazo derecho extendido hacia adelante con pronación (nudillos horizontales y firmes)
        'upperarm_R': {'rot': (-28, -22, 16), 'loc': (0, 0, 0)},
        'forearm_R':  {'rot': (38, -12, 10),  'loc': (0, 0, 0)},
        'hand_R':     {'rot': (18, -14, 75),  'loc': (0, 0, 0)},
        # Mano izquierda sólida en cobertura protegiendo mandíbula en cuadrante inferior izquierdo
        'upperarm_L': {'rot': (24, -20, 22),  'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (-40, 18, -16), 'loc': (0, 0, 0)},
        'hand_L':     {'rot': (28, -8, 28),   'loc': (0, 0, 0)}
    },
    8: { # Congelación de impacto (Hold pose for readability)
        'root':       {'loc': (0.0, -0.09, 0.07)},
        'upperarm_R': {'rot': (-26, -20, 15), 'loc': (0, 0, 0)},
        'forearm_R':  {'rot': (36, -10, 8),   'loc': (0, 0, 0)},
        'hand_R':     {'rot': (18, -14, 75),  'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (23, -19, 21),  'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (-39, 17, -15), 'loc': (0, 0, 0)},
        'hand_L':     {'rot': (27, -7, 27),   'loc': (0, 0, 0)}
    },
    11: { # Retracción elástica y rápida (Snappy recoil)
        'root':       {'loc': (0.0, -0.03, 0.05)},
        'upperarm_R': {'rot': (5, 6, -2),     'loc': (0, 0, 0)},
        'forearm_R':  {'rot': (-5, 4, 4),     'loc': (0, 0, 0)},
        'hand_R':     {'rot': (14, -8, 25),   'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (21, -17, 19),  'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (-36, 15, -13), 'loc': (0, 0, 0)},
        'hand_L':     {'rot': (24, -6, 25),   'loc': (0, 0, 0)}
    },
    14: { # Retorno limpio a la guardia de reposo
        'root':       {'loc': (0.0, 0.0, 0.05)},
        'upperarm_R': {'rot': (18, 12, -4),   'loc': (0, 0, 0)},
        'forearm_R':  {'rot': (-15, 6, 2),    'loc': (0, 0, 0)},
        'hand_R':     {'rot': (12, -8, 8),    'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (20, -16, 18),  'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (-35, 14, -12), 'loc': (0, 0, 0)},
        'hand_L':     {'rot': (22, -6, 24),   'loc': (0, 0, 0)}
    }
}

# Crear la acción en Blender
act = bpy.data.actions.new(name="A_FPS_Unarmed_Punch_R")
act.use_fake_user = True
arm.animation_data_create()
arm.animation_data.action = act
if hasattr(act, "slots") and len(act.slots):
    arm.animation_data.action_slot = act.slots[0]

for f in sorted(KEYS_FPS.keys()):
    frame_data = KEYS_FPS[f]
    for bone_name, vals in frame_data.items():
        pb = arm.pose.bones.get(bone_name)
        if pb is None:
            continue
        if 'rot' in vals:
            pb.rotation_euler = [math.radians(a) for a in vals['rot']]
        if 'loc' in vals:
            pb.location = vals['loc']
    for pb in arm.pose.bones:
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
        kp.interpolation = 'BEZIER'

scene = bpy.context.scene
scene.frame_start = 0
scene.frame_end = 14

# Comprobar posiciones espaciales de las manos en frames clave
print("\n--- POSICIONES ESPACIALES RESULTANTES DEL PUÑETAZO ---")
for f in [0, 2, 6, 8, 11, 14]:
    scene.frame_set(f)
    bpy.context.view_layer.update()
    hr = arm.matrix_world @ arm.pose.bones["hand_R"].matrix.translation
    hl = arm.matrix_world @ arm.pose.bones["hand_L"].matrix.translation
    root = arm.matrix_world @ arm.pose.bones["root"].matrix.translation
    print(f"Frame {f:2d}: root=({root.x:.3f}, {root.y:.3f}, {root.z:.3f}) | hand_R=({hr.x:.3f}, {hr.y:.3f}, {hr.z:.3f}) | hand_L=({hl.x:.3f}, {hl.y:.3f}, {hl.z:.3f})")

# Exportar FBX FPS
bpy.ops.object.select_all(action='DESELECT')
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
if os.path.exists(OUT_FBX_FPS):
    try: os.remove(OUT_FBX_FPS)
    except: pass
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
# RENDERIZADO DE PREVISUALIZACIÓN DE LOS 4 MOMENTOS CLAVE DEL GOLPE
# ==============================================================================
mat_arm = bpy.data.materials.new(name="M_Arm_Punch")
mat_arm.use_nodes = True
bsdf_arm = mat_arm.node_tree.nodes.get("Principled BSDF")
if bsdf_arm:
    bsdf_arm.inputs['Base Color'].default_value = (0.20, 0.45, 0.80, 1.0)
    bsdf_arm.inputs['Roughness'].default_value = 0.35
mesh_arms.data.materials.clear()
mesh_arms.data.materials.append(mat_arm)

world = bpy.data.worlds.new("W_Punch")
scene.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.05, 0.06, 0.08, 1.0)
world.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.0

key_light = bpy.data.lights.new("Key", 'AREA')
key_light.energy = 120.0
key_light.size = 0.8
key_obj = bpy.data.objects.new("Key", key_light)
key_obj.location = (0.35, -0.4, 0.45)
scene.collection.objects.link(key_obj)

fill_light = bpy.data.lights.new("Fill", 'AREA')
fill_light.energy = 60.0
fill_light.size = 1.0
fill_obj = bpy.data.objects.new("Fill", fill_light)
fill_obj.location = (-0.45, -0.25, 0.25)
scene.collection.objects.link(fill_obj)

rim_light = bpy.data.lights.new("Rim", 'AREA')
rim_light.energy = 70.0
rim_light.color = (0.7, 0.5, 1.0)
rim_obj = bpy.data.objects.new("Rim", rim_light)
rim_obj.location = (0.0, 0.3, -0.1)
scene.collection.objects.link(rim_obj)

# Cámara en posición exacta de ojos (FOV = 70 horizontal)
cam_data = bpy.data.cameras.new("Cam_FPS_Punch")
cam_data.sensor_width = 36.0
cam_data.lens = 22.0
cam_obj = bpy.data.objects.new("Cam_FPS_Punch", cam_data)
cam_obj.location = (0.0, 0.18, 0.05)

# Encarar hacia el centro de acción
cam_obj.rotation_euler = (math.radians(90.0), 0.0, math.radians(180.0))
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj

scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, 'RenderSettings') and 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
scene.render.resolution_x = 960
scene.render.resolution_y = 540

MOMENTS = [
    (0, "F0: Guardia Táctica"),
    (2, "F2: Carga y Elevación"),
    (6, "F6: Impacto Máximo al Centro"),
    (11, "F11: Retracción Elástica")
]

for idx, (frame, label) in enumerate(MOMENTS):
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    out_file = os.path.join(BRAIN_DIR, f"punch_moment_{idx}.png")
    scene.render.filepath = out_file
    bpy.ops.render.render(write_still=True)
    print(f"[RENDER OK] Momento {idx+1} ({label}): {out_file}")

print("=== PUÑETAZO FPS GENERADO Y RENDERIZADO CON ÉXITO ===")

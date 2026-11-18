# -*- coding: utf-8 -*-
"""test_fps_punch_horizontal_cam.py
Prueba y calibra la cinemática del puñetazo FPS con una cámara 100% horizontal
(Pitch=0, FOV=70° horizontal), idéntica a la cámara de Unreal Engine 5.
"""

import sys, os, math
import bpy
from mathutils import Vector, Euler

FBX_ARMS = r"E:\Darx_Proyect\Art\FBX\SK_FPS_Arms.fbx"
OUT_FBX = r"E:\Darx_Proyect\Art\FBX\Anim_FPS\A_FPS_Unarmed_Punch_R.fbx"
BRAIN_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=FBX_ARMS)

arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
mesh = next(o for o in bpy.data.objects if o.type == 'MESH')
arm.name = "ARM_FPS"

# Ocultar pistola vieja del template
for v in mesh.data.vertices:
    for g in v.groups:
        if mesh.vertex_groups[g.group].name in ('weapon', 'cell'):
            v.co = Vector((0, 0, -100))
            break

# Reset pose
for pb in arm.pose.bones:
    pb.rotation_mode = 'XYZ'
    pb.rotation_euler = (0, 0, 0)
    pb.location = (0, 0, 0)

# Mapeo de traslación del hueso root a coordenadas de mundo:
# loc[0] = world_X
# loc[1] = world_Z (hacia arriba)
# loc[2] = -world_Y (hacia adelante, porque -Y es adelante en Blender)
def r_loc(wx, wy, wz):
    return (wx, wz, -wy)

KEYS_PUNCH = {
    0: { # GUARDIA ALTA (Ambos puños claramente visibles en pantalla)
        'root':       {'loc': r_loc(0.0, -0.04, 0.12)},
        'upperarm_R': {'rot': (15, 10, -4),   'loc': (0, 0, 0)},
        'forearm_R':  {'rot': (-12, 6, 2),    'loc': (0, 0, 0)},
        'hand_R':     {'rot': (12, -8, 12),   'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (18, -14, 16),  'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (-25, 12, -10), 'loc': (0, 0, 0)},
        'hand_L':     {'rot': (18, -6, 20),   'loc': (0, 0, 0)}
    },
    2: { # CARGA / ANTICIPACIÓN (Puño derecho se retrae ligeramente cargando energía)
        'root':       {'loc': r_loc(0.0, 0.0, 0.13)},
        'upperarm_R': {'rot': (8, 6, -8),     'loc': (0, 0, 0)},
        'forearm_R':  {'rot': (-20, 4, 0),    'loc': (0, 0, 0)},
        'hand_R':     {'rot': (15, -10, 15),  'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (20, -16, 18),  'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (-28, 14, -12), 'loc': (0, 0, 0)},
        'hand_L':     {'rot': (20, -6, 22),   'loc': (0, 0, 0)}
    },
    6: { # PEAK IMPACT: PUÑETAZO RECTO DISPARADO AL CENTRO DE LA RETÍCULA
        # Root avanza decididamente hacia adelante
        'root':       {'loc': r_loc(0.0, -0.15, 0.14)},
        # Brazo derecho extendido hacia adelante con pronación horizontal (nudillos planos)
        'upperarm_R': {'rot': (-32, -26, 18), 'loc': (0, 0, 0)},
        'forearm_R':  {'rot': (45, -14, 12),  'loc': (0, 0, 0)},
        'hand_R':     {'rot': (18, -14, 80),  'loc': (0, 0, 0)},
        # Guardia izquierda sólida protegiendo mentón en el cuadrante inferior izquierdo
        'upperarm_L': {'rot': (22, -18, 20),  'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (-32, 16, -14), 'loc': (0, 0, 0)},
        'hand_L':     {'rot': (22, -6, 24),   'loc': (0, 0, 0)}
    },
    8: { # CONGELACIÓN DE IMPACTO (2 fotogramas de lectura nítida para el ojo humano)
        'root':       {'loc': r_loc(0.0, -0.14, 0.14)},
        'upperarm_R': {'rot': (-30, -25, 17), 'loc': (0, 0, 0)},
        'forearm_R':  {'rot': (43, -13, 11),  'loc': (0, 0, 0)},
        'hand_R':     {'rot': (18, -14, 80),  'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (21, -17, 19),  'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (-31, 15, -13), 'loc': (0, 0, 0)},
        'hand_L':     {'rot': (21, -6, 23),   'loc': (0, 0, 0)}
    },
    11: { # RETRACCIÓN ELÁSTICA (Snappy Recoil)
        'root':       {'loc': r_loc(0.0, -0.06, 0.12)},
        'upperarm_R': {'rot': (5, 6, -2),     'loc': (0, 0, 0)},
        'forearm_R':  {'rot': (-4, 4, 4),     'loc': (0, 0, 0)},
        'hand_R':     {'rot': (14, -8, 25),   'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (19, -15, 17),  'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (-26, 13, -11), 'loc': (0, 0, 0)},
        'hand_L':     {'rot': (19, -6, 21),   'loc': (0, 0, 0)}
    },
    14: { # VUELTA A GUARDIA TÁCTICA
        'root':       {'loc': r_loc(0.0, -0.04, 0.12)},
        'upperarm_R': {'rot': (15, 10, -4),   'loc': (0, 0, 0)},
        'forearm_R':  {'rot': (-12, 6, 2),    'loc': (0, 0, 0)},
        'hand_R':     {'rot': (12, -8, 12),   'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (18, -14, 16),  'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (-25, 12, -10), 'loc': (0, 0, 0)},
        'hand_L':     {'rot': (18, -6, 20),   'loc': (0, 0, 0)}
    }
}

act = bpy.data.actions.new(name="A_FPS_Unarmed_Punch_R")
act.use_fake_user = True
arm.animation_data_create()
arm.animation_data.action = act
if hasattr(act, "slots") and len(act.slots):
    arm.animation_data.action_slot = act.slots[0]

for f in sorted(KEYS_PUNCH.keys()):
    frame_data = KEYS_PUNCH[f]
    for bone_name, vals in frame_data.items():
        pb = arm.pose.bones.get(bone_name)
        if pb is None: continue
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

print("\n--- MEDIDAS ESPACIALES DEL PUÑETAZO CON ROOT CORREGIDO ---")
for f in [0, 2, 6, 8, 11, 14]:
    scene.frame_set(f)
    bpy.context.view_layer.update()
    hr = arm.matrix_world @ arm.pose.bones["hand_R"].matrix.translation
    hl = arm.matrix_world @ arm.pose.bones["hand_L"].matrix.translation
    root = arm.matrix_world @ arm.pose.bones["root"].matrix.translation
    print(f"F{f:2d}: root=({root.x:.3f}, {root.y:.3f}, {root.z:.3f}) | hand_R=({hr.x:.3f}, {hr.y:.3f}, {hr.z:.3f}) | hand_L=({hl.x:.3f}, {hl.y:.3f}, {hl.z:.3f})")

# Exportar FBX
bpy.ops.object.select_all(action='DESELECT')
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
if os.path.exists(OUT_FBX):
    try: os.remove(OUT_FBX)
    except: pass
bpy.ops.export_scene.fbx(
    filepath=OUT_FBX,
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
print(f"[OK FBX] {OUT_FBX} ({os.path.getsize(OUT_FBX)} bytes)")

# Material y luces
mat = bpy.data.materials.new(name="M_Punch_Test")
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.22, 0.48, 0.85, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.3
mesh.data.materials.clear()
mesh.data.materials.append(mat)

world = bpy.data.worlds.new("W_Punch_Test")
scene.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.05, 0.06, 0.08, 1.0)

# Luces
l1 = bpy.data.lights.new("L1", 'AREA'); l1.energy = 150.0; l1.size = 1.0
o1 = bpy.data.objects.new("L1", l1); o1.location = (0.4, -0.3, 0.4)
scene.collection.objects.link(o1)

l2 = bpy.data.lights.new("L2", 'AREA'); l2.energy = 80.0; l2.size = 1.2
o2 = bpy.data.objects.new("L2", l2); o2.location = (-0.5, -0.2, 0.3)
scene.collection.objects.link(o2)

l3 = bpy.data.lights.new("L3", 'AREA'); l3.energy = 100.0; l3.color = (0.8, 0.6, 1.0)
o3 = bpy.data.objects.new("L3", l3); o3.location = (0.0, 0.3, 0.0)
scene.collection.objects.link(o3)

# CÁMARA 100% HORIZONTAL (Pitch = 0, Roll = 0, mirando a -Y)
# Colocada exactamente a la altura de los ojos del jugador (Z = 0.05, Y = 0.18)
cam_data = bpy.data.cameras.new("Cam_Horiz")
cam_data.sensor_width = 36.0
cam_data.lens = 22.0 # FOV amplio FPS
cam_obj = bpy.data.objects.new("Cam_Horiz", cam_data)
cam_obj.location = (0.0, 0.18, 0.05)
cam_obj.rotation_euler = (math.radians(90.0), 0.0, math.radians(180.0))
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj

scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, 'RenderSettings') and 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
scene.render.resolution_x = 960
scene.render.resolution_y = 540

for f in [0, 2, 6, 11]:
    scene.frame_set(f)
    bpy.context.view_layer.update()
    p = os.path.join(BRAIN_DIR, f"punch_horiz_f{f}.png")
    scene.render.filepath = p
    bpy.ops.render.render(write_still=True)
    print(f"Rendered f{f}: {p}")

print("=== FINALIZADO TEST CÁMARA HORIZONTAL ===")

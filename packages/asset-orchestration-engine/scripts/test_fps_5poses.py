"""test_fps_5poses.py
Genera y renderiza las 5 poses FPS para verificar visualmente que la alineación,
el encuadre de cámara y las dos manos se vean impecables antes del horneado final.
"""
import bpy
import math
import os
import shutil
from mathutils import Vector, Euler

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# 1. Cargar brazos FPS
bpy.ops.import_scene.fbx(filepath=r"E:\Darx_Proyect\Art\FBX\SK_FPS_Arms.fbx")
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
fps_mesh = [o for o in bpy.data.objects if o.type == 'MESH'][0]

# Ocultar pistola vieja
for v in fps_mesh.data.vertices:
    for g in v.groups:
        if fps_mesh.vertex_groups[g.group].name in ('weapon', 'cell'):
            v.co = Vector((0, 0, -100))
            break

# 2. Cargar SMG
with bpy.data.libraries.load(r"E:\Darx_Proyect\Art\Blender\SM_Wep_PhaseSMG_Workspace.blend", link=False) as (data_from, data_to):
    data_to.objects = [n for n in data_from.objects if n not in ("StudioTable", "Cam", "KeyLight", "FillLight", "RimLight", "Light_ReactorSMG")]

smg_objs = [o for o in data_to.objects if o is not None]
for o in smg_objs:
    scene.collection.objects.link(o)

bpy.ops.object.select_all(action='DESELECT')
for o in smg_objs:
    o.select_set(True)
bpy.context.view_layer.objects.active = smg_objs[0]
bpy.ops.object.join()
smg = bpy.context.active_object
smg.name = "SMG"

# Parenting a hueso weapon
smg.parent = arm
smg.parent_type = 'BONE'
smg.parent_bone = 'weapon'
# Ubicación ergonómica calibrada en el hueso weapon:
smg.location = (0.01, 0.08, 0.0)
smg.rotation_euler = (0, 0, 0)

for pb in arm.pose.bones:
    pb.rotation_mode = 'XYZ'

# Luces de estudio
l1 = bpy.data.objects.new("L1", bpy.data.lights.new("L1", 'SUN'))
l1.data.energy = 3.5
l1.rotation_euler = (0.7, 0.3, -2.4)
scene.collection.objects.link(l1)

l2 = bpy.data.objects.new("L2", bpy.data.lights.new("L2", 'AREA'))
l2.data.energy = 450.0
l2.data.size = 2.0
l2.location = (-0.6, -0.2, 0.4)
scene.collection.objects.link(l2)

l3 = bpy.data.objects.new("L3", bpy.data.lights.new("L3", 'AREA'))
l3.data.energy = 350.0
l3.data.size = 2.0
l3.data.color = (0.75, 0.2, 1.0)
l3.location = (0.6, -0.3, 0.2)
scene.collection.objects.link(l3)

# Cámara FPS bien calibrada (FOV 26mm, posicionada a la altura de los ojos):
cam_data = bpy.data.cameras.new("CamFPS")
cam_data.lens = 26
cam = bpy.data.objects.new("CamFPS", cam_data)
cam.location = (0.02, 0.22, 0.04)
cam.rotation_euler = (math.radians(84), 0, math.radians(180))
scene.collection.objects.link(cam)
scene.camera = cam

scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 960
scene.render.resolution_y = 540

# Poses clave para las 5 acciones FPS:
poses = {
    "fps_test_walk.png": {
        'upperarm_R': {'rot': (-8, 4, -2), 'loc': (0, 0, 0)},
        'forearm_R':  {'rot': (-14, 2, 0),  'loc': (0, 0, 0)},
        'hand_R':     {'rot': (2, -4, 2),   'loc': (0, 0, 0)},
        'weapon':     {'rot': (-6, 6, -2),  'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (18, -12, 28), 'loc': (0, 0, 0)},
        'forearm_L':  {'rot': (-52, 16, -18), 'loc': (0, 0, 0)},
        'hand_L':     {'rot': (18, -10, 32), 'loc': (0.04, -0.06, 0.03)}
    },
    "fps_test_run.png": {
        'upperarm_R': {'rot': (-20, 6, -4), 'loc': (0.02, 0.04, -0.04)},
        'forearm_R':  {'rot': (-26, 4, 2),  'loc': (0, 0, 0)},
        'hand_R':     {'rot': (4, -6, 4),   'loc': (0, 0, 0)},
        'weapon':     {'rot': (-22, 10, -6), 'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (8, -16, 34), 'loc': (0.02, 0.04, -0.02)},
        'forearm_L':  {'rot': (-58, 18, -20), 'loc': (0, 0, 0)},
        'hand_L':     {'rot': (22, -12, 36), 'loc': (0.05, -0.05, 0.02)}
    },
    "fps_test_bash.png": {
        'upperarm_R': {'rot': (-32, 2, -10), 'loc': (-0.02, -0.16, 0.04)},
        'forearm_R':  {'rot': (-6, 2, 2),    'loc': (0, 0, 0)},
        'hand_R':     {'rot': (-4, 2, -2),   'loc': (0, 0, 0)},
        'weapon':     {'rot': (-8, 4, -4),   'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (-14, -8, 20), 'loc': (-0.02, -0.14, 0.05)},
        'forearm_L':  {'rot': (-28, 8, -10),  'loc': (0, 0, 0)},
        'hand_L':     {'rot': (12, -4, 18),  'loc': (0.04, -0.12, 0.04)}
    },
    "fps_test_aim.png": {
        'upperarm_R': {'rot': (-4, 1, -1), 'loc': (-0.06, 0.02, 0.04)},
        'forearm_R':  {'rot': (-8, 1, 0),  'loc': (0, 0, 0)},
        'hand_R':     {'rot': (0, -1, 0),  'loc': (0, 0, 0)},
        'weapon':     {'rot': (0, 0, 0),   'loc': (0, 0, 0)},
        'upperarm_L': {'rot': (22, -10, 26), 'loc': (-0.02, 0, 0.02)},
        'forearm_L':  {'rot': (-48, 14, -14), 'loc': (0, 0, 0)},
        'hand_L':     {'rot': (14, -8, 28), 'loc': (0.03, -0.07, 0.03)}
    },
    "fps_test_fire.png": {
        'upperarm_R': {'rot': (0, 2, -0.5), 'loc': (-0.06, 0.05, 0.05)},
        'forearm_R':  {'rot': (-5, 2, 0.5), 'loc': (0, 0, 0)},
        'hand_R':     {'rot': (1, -1, 0.5), 'loc': (0, 0, 0)},
        'weapon':     {'rot': (4.0, 0.5, -0.5), 'loc': (0, 0.03, 0.01)},
        'upperarm_L': {'rot': (25, -8, 25), 'loc': (-0.02, 0.03, 0.03)},
        'forearm_L':  {'rot': (-44, 16, -12), 'loc': (0, 0, 0)},
        'hand_L':     {'rot': (16, -6, 29), 'loc': (0.03, -0.05, 0.04)}
    }
}

for fname, pdata in poses.items():
    for bname, vals in pdata.items():
        pb = arm.pose.bones.get(bname)
        if pb:
            if 'rot' in vals:
                pb.rotation_euler = [math.radians(a) for a in vals['rot']]
            if 'loc' in vals:
                pb.location = vals['loc']
    bpy.context.view_layer.update()
    out_p = os.path.join(r"E:\Darx_Proyect\Art\Blender", fname)
    scene.render.filepath = out_p
    bpy.ops.render.render(write_still=True)
    shutil.copyfile(out_p, os.path.join(r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2", fname))
    print("Rendered:", fname)

"""evaluate_fps_hand_positions.py
Calcula la posición de hand_L y del vertical foregrip en FPS.
"""
import os
import math
import bpy
from mathutils import Vector, Matrix

PROJECT_ROOT = r"E:\Darx_Proyect"
ART_DIR = os.path.join(PROJECT_ROOT, "Art")
BLENDER_DIR = os.path.join(ART_DIR, "Blender")
SMG_BLEND = os.path.join(BLENDER_DIR, "SM_Wep_PhaseSMG_Workspace.blend")
FPS_FBX = os.path.join(ART_DIR, "FBX", "SK_FPS_Arms.fbx")

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=FPS_FBX)
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
fps_mesh = [o for o in bpy.data.objects if o.type == 'MESH'][0]

# Cargar SMG y emparentar
with bpy.data.libraries.load(SMG_BLEND, link=False) as (data_from, data_to):
    data_to.objects = [n for n in data_from.objects if n not in ("StudioTable", "Cam", "KeyLight", "FillLight", "RimLight", "Light_ReactorSMG")]
smg_objs = [o for o in data_to.objects if o is not None]
for o in smg_objs:
    bpy.context.scene.collection.objects.link(o)

bpy.ops.object.select_all(action='DESELECT')
for o in smg_objs:
    o.select_set(True)
bpy.context.view_layer.objects.active = smg_objs[0]
bpy.ops.object.join()
smg_mesh = bpy.context.active_object

smg_mesh.parent = arm
smg_mesh.parent_type = 'BONE'
smg_mesh.parent_bone = 'weapon'
smg_mesh.location = (0.01, 0.08, 0.0)
smg_mesh.rotation_euler = (0, 0, 0)

bpy.context.view_layer.update()

# Imprimir coordenadas de hand_L mesh y del foregrip con la pose BASE actual
BASE_FPS_WALK = {
    'upperarm_R': {'rot': (-8, 4, -2), 'loc': (0, 0, 0)},
    'forearm_R':  {'rot': (-14, 2, 0),  'loc': (0, 0, 0)},
    'hand_R':     {'rot': (2, -4, 2),   'loc': (0, 0, 0)},
    'weapon':     {'rot': (-6, 6, -2),  'loc': (0, 0, 0)},
    'upperarm_L': {'rot': (18, -12, 28), 'loc': (0, 0, 0)},
    'forearm_L':  {'rot': (-52, 16, -18), 'loc': (0, 0, 0)},
    'hand_L':     {'rot': (18, -10, 32), 'loc': (0.04, -0.06, 0.03)}
}

for bname, vals in BASE_FPS_WALK.items():
    pb = arm.pose.bones.get(bname)
    if 'rot' in vals:
        pb.rotation_euler = [math.radians(a) for a in vals['rot']]
    if 'loc' in vals:
        pb.location = vals['loc']

bpy.context.view_layer.update()

dg = bpy.context.evaluated_depsgraph_get()
em = fps_mesh.evaluated_get(dg)
vg_hl = fps_mesh.vertex_groups['hand_L'].index
v_hl = [em.matrix_world @ v.co for v in em.data.vertices if any(g.group == vg_hl for g in v.groups)]
c_hl = sum(v_hl, Vector((0,0,0))) / len(v_hl)

# Posición del foregrip en el espacio del mundo:
# En el blend, el foregrip está en local (0.0, 0.232, -0.022)
smg_eval = smg_mesh.evaluated_get(dg)
foregrip_world = smg_eval.matrix_world @ Vector((0.0, 0.232, -0.022))
reargrip_world = smg_eval.matrix_world @ Vector((0.0, -0.046, -0.022))

print(f"SMG RearGrip World:     ({reargrip_world.x:.3f}, {reargrip_world.y:.3f}, {reargrip_world.z:.3f})")
print(f"SMG Foregrip World:     ({foregrip_world.x:.3f}, {foregrip_world.y:.3f}, {foregrip_world.z:.3f})")
print(f"Hand_L Current Center:  ({c_hl.x:.3f}, {c_hl.y:.3f}, {c_hl.z:.3f})")
print(f"Delta (Hand_L -> Foregrip): ({foregrip_world.x - c_hl.x:.3f}, {foregrip_world.y - c_hl.y:.3f}, {foregrip_world.z - c_hl.z:.3f})")


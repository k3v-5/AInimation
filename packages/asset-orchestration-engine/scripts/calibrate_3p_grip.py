"""calibrate_3p_grip.py
Calibra el agarre a dos manos perfecto para SK_Player con el SMG emparentado al hueso hand_R.
"""
import os
import math
import shutil
import bpy
from mathutils import Vector, Euler, Matrix

PROJECT_ROOT = r"E:\Darx_Proyect"
ART_DIR = os.path.join(PROJECT_ROOT, "Art")
BLENDER_DIR = os.path.join(ART_DIR, "Blender")
BRAIN_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"
SMG_BLEND = os.path.join(BLENDER_DIR, "SM_Wep_PhaseSMG_Workspace.blend")
PLAYER_FBX = os.path.join(ART_DIR, "FBX", "SK_Player.fbx")

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# 1. Cargar jugador
bpy.ops.import_scene.fbx(filepath=PLAYER_FBX)
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
arm.name = "ARM_Player"
player_mesh = [o for o in bpy.data.objects if o.type == 'MESH'][0]

# 2. Cargar SMG
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
smg_mesh.name = "SM_Wep_PhaseSMG_3P"

# Emparentar SMG al hueso hand_R
smg_mesh.parent = arm
smg_mesh.parent_type = 'BONE'
smg_mesh.parent_bone = 'hand_R'
smg_mesh.location = (0, 0, 0)
smg_mesh.rotation_euler = (0, 0, 0)

# Aplicar BASE_3P_COMBAT
BASE_3P_COMBAT = {
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

for bname, vals in BASE_3P_COMBAT.items():
    pb = arm.pose.bones.get(bname)
    if pb and 'rot' in vals:
        pb.rotation_euler = [math.radians(a) for a in vals['rot']]
    if pb and 'loc' in vals:
        pb.location = vals['loc']

bpy.context.view_layer.update()

dg = bpy.context.evaluated_depsgraph_get()
em = player_mesh.evaluated_get(dg)
vg_hr = player_mesh.vertex_groups['hand_R'].index
vg_hl = player_mesh.vertex_groups['hand_L'].index
v_hr = [em.matrix_world @ v.co for v in em.data.vertices if any(g.group == vg_hr and g.weight > 0.8 for g in v.groups)]
v_hl = [em.matrix_world @ v.co for v in em.data.vertices if any(g.group == vg_hl and g.weight > 0.8 for g in v.groups)]
c_hr = sum(v_hr, Vector((0,0,0))) / len(v_hr)
c_hl = sum(v_hl, Vector((0,0,0))) / len(v_hl)

smg_eval = smg_mesh.evaluated_get(dg)
reargrip_world = smg_eval.matrix_world @ Vector((0.0, -0.046, -0.022))
foregrip_world = smg_eval.matrix_world @ Vector((0.0, 0.232, -0.022))

print(f"Hand_R World:       {c_hr}")
print(f"SMG RearGrip World: {reargrip_world}")
print(f"Delta Hand_R - RearGrip: {c_hr - reargrip_world}")
print(f"Hand_L World:       {c_hl}")
print(f"SMG Foregrip World: {foregrip_world}")
print(f"Delta Hand_L - Foregrip: {c_hl - foregrip_world}")

# Iluminación
l1 = bpy.data.objects.new("Key", bpy.data.lights.new("Key", 'SUN'))
l1.data.energy = 4.0
l1.rotation_euler = (math.radians(60), math.radians(15), math.radians(-25))
scene.collection.objects.link(l1)

l2 = bpy.data.objects.new("Fill", bpy.data.lights.new("Fill", 'AREA'))
l2.data.energy = 450.0
l2.data.size = 2.5
l2.location = (0.5, 2.0, 1.6)
scene.collection.objects.link(l2)

# Cámara frontal 3/4
cam_data = bpy.data.cameras.new("Cam")
cam_data.lens = 42
cam_obj = bpy.data.objects.new("Cam", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_obj.location = (1.35, 2.2, 1.45)
target = bpy.data.objects.new("Target", None)
target.location = (0.05, 0.25, 1.35)
scene.collection.objects.link(target)
tt = cam_obj.constraints.new('TRACK_TO')
tt.target = target
tt.track_axis = 'TRACK_NEGATIVE_Z'
tt.up_axis = 'UP_Y'

scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 960
scene.render.resolution_y = 540

out_img = os.path.join(BRAIN_DIR, "scratch", "test_3p_parented_grip.png")
os.makedirs(os.path.dirname(out_img), exist_ok=True)
scene.render.filepath = out_img
bpy.ops.render.render(write_still=True)
print(f"Renderizado: {out_img}")

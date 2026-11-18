"""test_combat_grip_forward.py
Prueba la rotación forward (Z=180°) del SMG y el acople Two-Bone IK de ambas manos.
"""
import os
import math
import bpy
from mathutils import Vector, Euler, Matrix

PROJECT_ROOT = r"E:\Darx_Proyect"
ART_DIR = os.path.join(PROJECT_ROOT, "Art")
BLENDER_DIR = os.path.join(ART_DIR, "Blender")
BRAIN_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"
BLEND_PATH = os.path.join(PROJECT_ROOT, "Saved", "Player_Skin_Workspace", "DarX_Player_Rigged_Canonical.blend")
SMG_BLEND = os.path.join(BLENDER_DIR, "SM_Wep_PhaseSMG_Workspace.blend")

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.open_mainfile(filepath=BLEND_PATH)
scene = bpy.context.scene

arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
mesh = [o for o in bpy.data.objects if o.type == 'MESH'][0]

# 1. Alinear huesos de brazos a la anatomía A-pose
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='EDIT')
eb = arm.data.edit_bones

eb['upperarm_R'].head = Vector((0.228, -0.010, 1.520))
eb['upperarm_R'].tail = Vector((0.550, 0.020, 1.250))

eb['forearm_R'].head = Vector((0.550, 0.020, 1.250))
eb['forearm_R'].tail = Vector((0.860, 0.045, 0.950))

eb['hand_R'].head = Vector((0.860, 0.045, 0.950))
eb['hand_R'].tail = Vector((0.950, 0.045, 0.850))

eb['upperarm_L'].head = Vector((-0.228, -0.010, 1.520))
eb['upperarm_L'].tail = Vector((-0.550, 0.020, 1.250))

eb['forearm_L'].head = Vector((-0.550, 0.020, 1.250))
eb['forearm_L'].tail = Vector((-0.860, 0.045, 0.950))

eb['hand_L'].head = Vector((-0.860, 0.045, 0.950))
eb['hand_L'].tail = Vector((-0.950, 0.045, 0.850))

bpy.ops.object.mode_set(mode='OBJECT')

# Reasignar pesos automáticos para los brazos
arm_groups = ['upperarm_R', 'forearm_R', 'hand_R', 'upperarm_L', 'forearm_L', 'hand_L']
for gname in arm_groups:
    vg = mesh.vertex_groups.get(gname)
    if vg:
        mesh.vertex_groups.remove(vg)

bpy.ops.object.select_all(action='DESELECT')
mesh.select_set(True)
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.parent_set(type='ARMATURE_AUTO')

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
smg_mesh.name = "SMG_Combat_Ref"

# Posición del arma en el espacio de combate:
# Orientada hacia adelante (-Y), cañón apuntando al frente
smg_mesh.location = Vector((0.12, -0.32, 1.26))
smg_mesh.rotation_euler = (math.radians(-6), math.radians(4), math.radians(180))
bpy.context.view_layer.update()

# Calcular coordenadas de empuñadura trasera y delantera en mundo
dg = bpy.context.evaluated_depsgraph_get()
smg_eval = smg_mesh.evaluated_get(dg)
reargrip_world = smg_eval.matrix_world @ Vector((0.0, -0.046, -0.022))
foregrip_world = smg_eval.matrix_world @ Vector((0.0, 0.232, -0.022))

print(f"RearGrip World: {reargrip_world}")
print(f"Foregrip World: {foregrip_world}")

# 3. Configurar Two-Bone IK con Pole Targets anatómicos
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='POSE')
pb_hr = arm.pose.bones['hand_R']
pb_hl = arm.pose.bones['hand_L']

# Dianas en empuñaduras
target_R = bpy.data.objects.new("Target_RearGrip", None)
target_R.location = reargrip_world
scene.collection.objects.link(target_R)

target_L = bpy.data.objects.new("Target_Foregrip", None)
target_L.location = foregrip_world
scene.collection.objects.link(target_L)

# Pole targets para codos (hacia afuera y atrás)
pole_R = bpy.data.objects.new("Pole_R", None)
pole_R.location = Vector((0.65, 0.20, 1.20))
scene.collection.objects.link(pole_R)

pole_L = bpy.data.objects.new("Pole_L", None)
pole_L.location = Vector((-0.65, 0.20, 1.20))
scene.collection.objects.link(pole_L)

ik_r = pb_hr.constraints.new('IK')
ik_r.target = target_R
ik_r.pole_target = pole_R
ik_r.pole_angle = math.radians(90)
ik_r.chain_count = 2

ik_l = pb_hl.constraints.new('IK')
ik_l.target = target_L
ik_l.pole_target = pole_L
ik_l.pole_angle = math.radians(-90)
ik_l.chain_count = 2

bpy.context.view_layer.update()

# Luces
l1 = bpy.data.objects.new("Key", bpy.data.lights.new("Key", 'SUN'))
l1.data.energy = 4.5
l1.rotation_euler = (math.radians(55), math.radians(15), math.radians(-30))
scene.collection.objects.link(l1)

l2 = bpy.data.objects.new("Fill", bpy.data.lights.new("Fill", 'AREA'))
l2.data.energy = 600.0
l2.data.size = 2.5
l2.location = (0.5, 2.2, 1.8)
scene.collection.objects.link(l2)

# Cámara 3/4 frontal
cam_data = bpy.data.cameras.new("Cam")
cam_data.lens = 38
cam_obj = bpy.data.objects.new("Cam", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_obj.location = (1.45, 2.35, 1.35)
target_cam = bpy.data.objects.new("TargetCam", None)
target_cam.location = (0.05, 0.20, 1.22)
scene.collection.objects.link(target_cam)
tt = cam_obj.constraints.new('TRACK_TO')
tt.target = target_cam
tt.track_axis = 'TRACK_NEGATIVE_Z'
tt.up_axis = 'UP_Y'

scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 960
scene.render.resolution_y = 540
out_img = os.path.join(BRAIN_DIR, "scratch", "test_combat_grip_forward.png")
scene.render.filepath = out_img
bpy.ops.render.render(write_still=True)
print(f"Render guardado: {out_img}")

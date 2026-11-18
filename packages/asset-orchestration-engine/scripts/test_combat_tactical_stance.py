"""test_combat_tactical_stance.py
Prueba la postura táctica de combate completa:
- Torso orientado tácticamente (spine -10°, chest -8°)
- Arma con buffer de seguridad >= 35cm del pecho
- Two-Bone IK analítico con Pole Targets para codos naturales
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

# Posición del arma táctica:
# A 38cm delante del pecho, ligeramente a la derecha, cañón al frente
smg_mesh.location = Vector((0.08, -0.40, 1.28))
smg_mesh.rotation_euler = (math.radians(-4), math.radians(2), math.radians(180))
bpy.context.view_layer.update()

# Calcular coordenadas de empuñaduras en mundo
dg = bpy.context.evaluated_depsgraph_get()
smg_eval = smg_mesh.evaluated_get(dg)
reargrip_world = smg_eval.matrix_world @ Vector((0.0, -0.046, -0.022))
foregrip_world = smg_eval.matrix_world @ Vector((0.0, 0.232, -0.022))

# 3. Postura del torso (Orientación táctica sin romper anatomía)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='POSE')

# Rotar suavemente spine y chest
arm.pose.bones['spine'].rotation_mode = 'XYZ'
arm.pose.bones['spine'].rotation_euler = (math.radians(-4), 0, math.radians(-12))
arm.pose.bones['chest'].rotation_mode = 'XYZ'
arm.pose.bones['chest'].rotation_euler = (math.radians(-2), 0, math.radians(-8))
arm.pose.bones['head'].rotation_mode = 'XYZ'
arm.pose.bones['head'].rotation_euler = (math.radians(2), 0, math.radians(20)) # Cabeza mira al objetivo

# Piernas en posición de combate atlética
arm.pose.bones['thigh_R'].rotation_mode = 'XYZ'
arm.pose.bones['thigh_R'].rotation_euler = (math.radians(-12), 0, math.radians(-4))
arm.pose.bones['calf_R'].rotation_mode = 'XYZ'
arm.pose.bones['calf_R'].rotation_euler = (math.radians(10), 0, 0)
arm.pose.bones['thigh_L'].rotation_mode = 'XYZ'
arm.pose.bones['thigh_L'].rotation_euler = (math.radians(10), 0, math.radians(4))
arm.pose.bones['calf_L'].rotation_mode = 'XYZ'
arm.pose.bones['calf_L'].rotation_euler = (math.radians(-6), 0, 0)

bpy.context.view_layer.update()

# 4. Configurar Two-Bone IK con Pole Targets anatómicos
pb_hr = arm.pose.bones['hand_R']
pb_hl = arm.pose.bones['hand_L']

target_R = bpy.data.objects.new("Target_RearGrip", None)
target_R.location = reargrip_world
scene.collection.objects.link(target_R)

target_L = bpy.data.objects.new("Target_Foregrip", None)
target_L.location = foregrip_world
scene.collection.objects.link(target_L)

# Pole targets para orientar codos hacia afuera
pole_R = bpy.data.objects.new("Pole_R", None)
pole_R.location = Vector((0.75, 0.30, 1.25))
scene.collection.objects.link(pole_R)

pole_L = bpy.data.objects.new("Pole_L", None)
pole_L.location = Vector((-0.75, 0.30, 1.25))
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
cam_obj.location = (1.50, 2.45, 1.35)
target_cam = bpy.data.objects.new("TargetCam", None)
target_cam.location = (0.05, 0.20, 1.20)
scene.collection.objects.link(target_cam)
tt = cam_obj.constraints.new('TRACK_TO')
tt.target = target_cam
tt.track_axis = 'TRACK_NEGATIVE_Z'
tt.up_axis = 'UP_Y'

scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 960
scene.render.resolution_y = 540
out_img = os.path.join(BRAIN_DIR, "scratch", "test_combat_tactical_stance.png")
scene.render.filepath = out_img
bpy.ops.render.render(write_still=True)
print(f"Render guardado: {out_img}")

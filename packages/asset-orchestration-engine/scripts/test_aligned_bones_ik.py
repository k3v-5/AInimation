"""test_aligned_bones_ik.py
Alinea los huesos de los brazos exactamente a la geometría A-pose del modelo,
aplica pesos automáticos y prueba la flexión con IK para verificar cero distorsión.
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

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.open_mainfile(filepath=BLEND_PATH)
scene = bpy.context.scene

arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
mesh = [o for o in bpy.data.objects if o.type == 'MESH'][0]

# Entrar en modo edición para corregir la posición de los huesos de los brazos
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='EDIT')
eb = arm.data.edit_bones

# Hombro, Codo y Muñeca medidos directamente de la malla:
# Shoulder: (0.228, -0.010, 1.520)
# Elbow:    (0.550, 0.020, 1.250)
# Wrist:    (0.860, 0.045, 0.950)
# Hand tip: (0.950, 0.045, 0.850)

# Brazo Derecho
eb['upperarm_R'].head = Vector((0.228, -0.010, 1.520))
eb['upperarm_R'].tail = Vector((0.550, 0.020, 1.250))

eb['forearm_R'].head = Vector((0.550, 0.020, 1.250))
eb['forearm_R'].tail = Vector((0.860, 0.045, 0.950))

eb['hand_R'].head = Vector((0.860, 0.045, 0.950))
eb['hand_R'].tail = Vector((0.950, 0.045, 0.850))

# Brazo Izquierdo (Simétrico)
eb['upperarm_L'].head = Vector((-0.228, -0.010, 1.520))
eb['upperarm_L'].tail = Vector((-0.550, 0.020, 1.250))

eb['forearm_L'].head = Vector((-0.550, 0.020, 1.250))
eb['forearm_L'].tail = Vector((-0.860, 0.045, 0.950))

eb['hand_L'].head = Vector((-0.860, 0.045, 0.950))
eb['hand_L'].tail = Vector((-0.950, 0.045, 0.850))

bpy.ops.object.mode_set(mode='OBJECT')
print("Huesos de brazos alineados a la anatomía A-pose.")

# Reasignar pesos automáticos para los brazos
# Quitar vertex groups viejos de brazos
arm_groups = ['upperarm_R', 'forearm_R', 'hand_R', 'upperarm_L', 'forearm_L', 'hand_L']
for gname in arm_groups:
    vg = mesh.vertex_groups.get(gname)
    if vg:
        mesh.vertex_groups.remove(vg)

# Asignar pesos automáticos limpios
bpy.ops.object.select_all(action='DESELECT')
mesh.select_set(True)
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.parent_set(type='ARMATURE_AUTO')
print("Pesos automáticos recalculados con huesos congruentes.")

# Ahora aplicar restricción IK a ambas manos hacia el centro para simular agarre de arma
bpy.ops.object.mode_set(mode='POSE')
pb_hr = arm.pose.bones['hand_R']
pb_hl = arm.pose.bones['hand_L']

# Crear dianas IK en posición de combate frontal (Z=1.25, Y=-0.35, X=±0.10)
target_R = bpy.data.objects.new("Target_R", None)
target_R.location = Vector((0.10, -0.35, 1.25))
scene.collection.objects.link(target_R)

target_L = bpy.data.objects.new("Target_L", None)
target_L.location = Vector((-0.08, -0.42, 1.30))
scene.collection.objects.link(target_L)

ik_r = pb_hr.constraints.new('IK')
ik_r.target = target_R
ik_r.chain_count = 2

ik_l = pb_hl.constraints.new('IK')
ik_l.target = target_L
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

# Cámara frontal 3/4
cam_data = bpy.data.cameras.new("Cam")
cam_data.lens = 38
cam_obj = bpy.data.objects.new("Cam", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_obj.location = (1.45, 2.4, 1.35)
target_cam = bpy.data.objects.new("TargetCam", None)
target_cam.location = (0.05, 0.15, 1.20)
scene.collection.objects.link(target_cam)
tt = cam_obj.constraints.new('TRACK_TO')
tt.target = target_cam
tt.track_axis = 'TRACK_NEGATIVE_Z'
tt.up_axis = 'UP_Y'

scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 960
scene.render.resolution_y = 540
out_img = os.path.join(BRAIN_DIR, "scratch", "test_aligned_ik_render.png")
scene.render.filepath = out_img
bpy.ops.render.render(write_still=True)
print(f"Render guardado: {out_img}")

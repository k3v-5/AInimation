"""test_fps_ik_grip.py
Prueba el acople IK de la mano izquierda en SK_FPS_Arms hacia el foregrip vertical del SMG.
"""
import os
import math
import bpy
from mathutils import Vector, Euler, Matrix

PROJECT_ROOT = r"E:\Darx_Proyect"
ART_DIR = os.path.join(PROJECT_ROOT, "Art")
BLENDER_DIR = os.path.join(ART_DIR, "Blender")
BRAIN_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"
FPS_FBX = os.path.join(ART_DIR, "FBX", "SK_FPS_Arms.fbx")
SMG_BLEND = os.path.join(BLENDER_DIR, "SM_Wep_PhaseSMG_Workspace.blend")

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

bpy.ops.import_scene.fbx(filepath=FPS_FBX)
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
fps_mesh = [o for o in bpy.data.objects if o.type == 'MESH'][0]

# Ocultar pistola vieja
for v in fps_mesh.data.vertices:
    for g in v.groups:
        if fps_mesh.vertex_groups[g.group].name in ('weapon', 'cell'):
            v.co = Vector((0, 0, -100))
            break

# Cargar SMG
with bpy.data.libraries.load(SMG_BLEND, link=False) as (data_from, data_to):
    data_to.objects = [n for n in data_from.objects if n not in ("StudioTable", "Cam", "KeyLight", "FillLight", "RimLight", "Light_ReactorSMG")]
smg_objs = [o for o in data_to.objects if o is not None]
for o in smg_objs:
    scene.collection.objects.link(o)

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

# Calcular coordenadas de empuñadura delantera en mundo
dg = bpy.context.evaluated_depsgraph_get()
smg_eval = smg_mesh.evaluated_get(dg)
foregrip_world = smg_eval.matrix_world @ Vector((0.0, 0.232, -0.022))

print(f"SMG Foregrip World: {foregrip_world}")

# Configurar IK en hand_L
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='POSE')
pb_hl = arm.pose.bones['hand_L']

target_L = bpy.data.objects.new("Target_Foregrip_FPS", None)
target_L.location = foregrip_world
scene.collection.objects.link(target_L)

# Pole target exterior
pole_L = bpy.data.objects.new("Pole_L_FPS", None)
pole_L.location = Vector((-0.40, -0.20, -0.40))
scene.collection.objects.link(pole_L)

ik = pb_hl.constraints.new('IK')
ik.target = target_L
ik.pole_target = pole_L
ik.pole_angle = math.radians(0)
ik.chain_count = 2

# Ajustar rotación base del hombro izquierdo para permitir alcance óptimo
arm.pose.bones['upperarm_L'].rotation_mode = 'XYZ'
arm.pose.bones['upperarm_L'].rotation_euler = (math.radians(30), math.radians(-10), math.radians(35))
arm.pose.bones['upperarm_L'].location = (0.08, -0.08, 0.05)

bpy.context.view_layer.update()

# Cámara ocular FPS
cam_data = bpy.data.cameras.new("Cam")
cam_data.lens = 18
cam_obj = bpy.data.objects.new("Cam", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_obj.location = (0.01, 0.24, 0.06)
cam_obj.rotation_euler = (math.radians(88), 0, math.radians(180))

l1 = bpy.data.objects.new("Key", bpy.data.lights.new("Key", 'SUN'))
l1.data.energy = 4.0
l1.rotation_euler = (0.7, 0.3, -2.4)
scene.collection.objects.link(l1)

l2 = bpy.data.objects.new("Fill", bpy.data.lights.new("Fill", 'AREA'))
l2.data.energy = 450.0
l2.data.size = 2.0
l2.location = (-0.6, -0.2, 0.4)
scene.collection.objects.link(l2)

scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 960
scene.render.resolution_y = 540
out_img = os.path.join(BRAIN_DIR, "scratch", "test_fps_ik_grip.png")
scene.render.filepath = out_img
bpy.ops.render.render(write_still=True)
print(f"Render guardado: {out_img}")

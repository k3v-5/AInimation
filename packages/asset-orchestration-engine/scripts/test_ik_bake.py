"""test_ik_bake.py
Prueba bake de IK visual para que la mano izquierda agarre la empuñadura con precision milimetrica.
"""
import bpy
import math
import shutil
from mathutils import Vector

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

bpy.ops.import_scene.fbx(filepath=r"E:\Darx_Proyect\Art\FBX\SK_FPS_Arms.fbx")
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
fps_mesh = [o for o in bpy.data.objects if o.type == 'MESH'][0]

# Ocultar pistola vieja
for v in fps_mesh.data.vertices:
    for g in v.groups:
        if fps_mesh.vertex_groups[g.group].name in ('weapon', 'cell'):
            v.co = Vector((0, 0, -100))
            break

# Cargar SMG
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

smg.parent = arm
smg.parent_type = 'BONE'
smg.parent_bone = 'weapon'
smg.location = (0, 0, 0)
smg.rotation_euler = (0, 0, 0)

# Empty objetivo para la mano izquierda en la empuñadura delantera
fg_target = bpy.data.objects.new("ForegripTarget", None)
fg_target.parent = smg
# La empuñadura delantera Tommy está en (0, 0.23, -0.06).
# La palma de hand_L debe colocarse en (0.01, 0.23, -0.06):
fg_target.location = (0.01, 0.23, -0.06)
scene.collection.objects.link(fg_target)

# Pole target para el codo izquierdo para que apunte naturalmente hacia abajo-afuera:
pole_target = bpy.data.objects.new("ElbowPole", None)
pole_target.parent = arm
pole_target.location = (-0.4, -0.2, -0.5)
scene.collection.objects.link(pole_target)

bpy.context.view_layer.update()

# Configurar IK en hand_L
pb_hand_l = arm.pose.bones['hand_L']
c_ik = pb_hand_l.constraints.new('IK')
c_ik.target = fg_target
c_ik.pole_target = pole_target
c_ik.pole_angle = math.radians(-90)
c_ik.chain_count = 2

# Rotación de hand_L para agarrar el mango vertical
pb_hand_l.rotation_mode = 'XYZ'
pb_hand_l.rotation_euler = (math.radians(-10), math.radians(35), math.radians(-65))

# Animar 1 frame
arm.animation_data_create()
act = bpy.data.actions.new(name="A_Test_Bake")
arm.animation_data.action = act
scene.frame_set(1)

# Seleccionar huesos y hacer Visual Bake
bpy.ops.object.select_all(action='DESELECT')
arm.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode='POSE')
bpy.ops.pose.select_all(action='SELECT')

bpy.ops.nla.bake(
    frame_start=1,
    frame_end=1,
    only_selected=False,
    visual_keying=True,
    clear_constraints=False, # conservar mientras renderizamos
    bake_types={'POSE'}
)
bpy.ops.object.mode_set(mode='OBJECT')

# Luces
l1 = bpy.data.objects.new("L1", bpy.data.lights.new("L1", 'SUN'))
l1.data.energy = 3.5
l1.rotation_euler = (0.7, 0.3, -2.4)
scene.collection.objects.link(l1)

l2 = bpy.data.objects.new("L2", bpy.data.lights.new("L2", 'AREA'))
l2.data.energy = 400.0
l2.data.size = 2.0
l2.location = (-0.5, -0.2, 0.4)
scene.collection.objects.link(l2)

# Camara FPS
cam_data = bpy.data.cameras.new("CamFPS")
cam_data.lens = 28
cam = bpy.data.objects.new("CamFPS", cam_data)
# Queremos ver el arma, la mano derecha y la mano izquierda sosteniendo la empuñadura
cam.location = (0.02, 0.18, 0.08)
cam.rotation_euler = (math.radians(78), 0, math.radians(180))
scene.collection.objects.link(cam)
scene.camera = cam

scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 960
scene.render.resolution_y = 540
out_img = r"E:\Darx_Proyect\Art\Blender\test_fps_bake.png"
scene.render.filepath = out_img
bpy.ops.render.render(write_still=True)
shutil.copyfile(out_img, r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2\test_fps_bake.png")
print("Rendered test_fps_bake.png")

"""test_ik_solver.py
Prueba el solucionador IK para el agarre a dos manos del SMG en SK_FPS_Arms y SK_Player.
"""
import bpy
import math
import shutil
from mathutils import Vector, Euler, Matrix

# ==========================================================
# 1. TEST IK EN SK_FPS_ARMS
# ==========================================================
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

# Parenting a hueso weapon
smg.parent = arm
smg.parent_type = 'BONE'
smg.parent_bone = 'weapon'
smg.location = (0, 0, 0)
smg.rotation_euler = (0, 0, 0)

# Empty en el foregrip del SMG (en coordenadas locales del SMG)
# En SMG local: empuñadura delantera está en (0, 0.23, -0.06)
fg_target = bpy.data.objects.new("ForegripTarget", None)
fg_target.parent = smg
fg_target.location = (0.01, 0.23, -0.07)
scene.collection.objects.link(fg_target)

bpy.context.view_layer.update()

# Configurar IK en hand_L
pb_hand_l = arm.pose.bones['hand_L']
c_ik = pb_hand_l.constraints.new('IK')
c_ik.target = fg_target
c_ik.chain_count = 2

bpy.context.view_layer.update()

# Ver las rotaciones resueltas de upperarm_L y forearm_L
pb_up_l = arm.pose.bones['upperarm_L']
pb_fore_l = arm.pose.bones['forearm_L']
print("FPS IK Solved:")
print(f"  upperarm_L rot euler: {[math.degrees(a) for a in pb_up_l.rotation_euler]}")
print(f"  forearm_L rot euler: {[math.degrees(a) for a in pb_fore_l.rotation_euler]}")

# Ajustar rotación de hand_L para que la palma abrace la empuñadura
pb_hand_l.rotation_mode = 'XYZ'
pb_hand_l.rotation_euler = (math.radians(-15), math.radians(20), math.radians(-70))

# Luces frontales y laterales bien iluminadas
l1 = bpy.data.objects.new("L1", bpy.data.lights.new("L1", 'SUN'))
l1.data.energy = 4.0
l1.rotation_euler = (0.6, 0.3, -2.5) # Luz apuntando hacia -Y (hacia el arma)
scene.collection.objects.link(l1)

l2 = bpy.data.objects.new("L2", bpy.data.lights.new("L2", 'AREA'))
l2.data.energy = 300.0
l2.location = (0.5, 0.2, 0.3)
scene.collection.objects.link(l2)

# Camara FPS apuntando hacia -Y, a la altura del hombro / mira
cam_data = bpy.data.cameras.new("CamFPS")
cam_data.lens = 28
cam = bpy.data.objects.new("CamFPS", cam_data)
# En SK_FPS_Arms, el arma está a X=0.098, Z=-0.088.
# Para ver el arma y ambas manos con claridad:
cam.location = (0.04, 0.12, 0.04)
cam.rotation_euler = (math.radians(82), 0, math.radians(180))
scene.collection.objects.link(cam)
scene.camera = cam

scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 960
scene.render.resolution_y = 540
out_img = r"E:\Darx_Proyect\Art\Blender\test_fps_ik.png"
scene.render.filepath = out_img
bpy.ops.render.render(write_still=True)
shutil.copyfile(out_img, r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2\test_fps_ik.png")
print("Rendered test_fps_ik.png")

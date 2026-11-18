"""test_ik_alignment.py
Prueba empírica de IK para alinear automáticamente hand_L al foregrip vertical
tanto en SK_FPS_Arms como en SK_Player.
"""
import os
import math
import bpy
from mathutils import Vector, Euler, Matrix

PROJECT_ROOT = r"E:\Darx_Proyect"
ART_DIR = os.path.join(PROJECT_ROOT, "Art")
BLENDER_DIR = os.path.join(ART_DIR, "Blender")
SMG_BLEND = os.path.join(BLENDER_DIR, "SM_Wep_PhaseSMG_Workspace.blend")
FPS_FBX = os.path.join(ART_DIR, "FBX", "SK_FPS_Arms.fbx")
PLAYER_FBX = os.path.join(ART_DIR, "FBX", "SK_Player.fbx")

print("="*60)
print("TEST 1: SK_FPS_Arms con IK hacia el Foregrip")
print("="*60)
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

# Crear Empty en el foregrip
dg = bpy.context.evaluated_depsgraph_get()
smg_eval = smg_mesh.evaluated_get(dg)
foregrip_world = smg_eval.matrix_world @ Vector((0.0, 0.232, -0.022))

empty_target = bpy.data.objects.new("ForegripTarget", None)
empty_target.location = foregrip_world
scene.collection.objects.link(empty_target)
empty_target.parent = smg_mesh
empty_target.matrix_parent_inverse = smg_mesh.matrix_world.inverted()

# Agregar IK constraint a hand_L
pb_hl = arm.pose.bones['hand_L']
ik = pb_hl.constraints.new('IK')
ik.target = empty_target
ik.chain_count = 2

bpy.context.view_layer.update()

# Evaluar posición de hand_L con IK
dg = bpy.context.evaluated_depsgraph_get()
em = fps_mesh.evaluated_get(dg)
vg_hl = fps_mesh.vertex_groups['hand_L'].index
v_hl = [em.matrix_world @ v.co for v in em.data.vertices if any(g.group == vg_hl for g in v.groups)]
c_hl = sum(v_hl, Vector((0,0,0))) / len(v_hl)

print(f"Target Foregrip: {foregrip_world}")
print(f"Hand_L con IK:   {c_hl}")
print(f"Distancia: {(c_hl - foregrip_world).length:.4f} m")

# Renderizar prueba visual FPS
cam_loc = (0.01, 0.24, 0.06)
cam_rot = (math.radians(88), 0, math.radians(180))

cam_data = bpy.data.cameras.new("Cam")
cam_data.lens = 18
cam_obj = bpy.data.objects.new("Cam", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_obj.location = cam_loc
cam_obj.rotation_euler = cam_rot

# Luces
l1 = bpy.data.objects.new("Key", bpy.data.lights.new("Key", 'SUN'))
l1.data.energy = 4.0
l1.rotation_euler = (0.7, 0.3, -2.4)
scene.collection.objects.link(l1)

scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 960
scene.render.resolution_y = 540
out_test = os.path.join(ART_DIR, "Blender", "test_fps_ik.png")
scene.render.filepath = out_test
bpy.ops.render.render(write_still=True)
print(f"Renderizado test FPS IK: {out_test}")


"""test_crafting_geometry_debug.py
Prueba rápida de geometría, orientación y poses corregidas (<>).
"""
import os
import math
import bpy
import bmesh
from mathutils import Vector, Euler, Matrix

R = math.radians

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, 'RenderSettings') and 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
scene.render.resolution_x = 960
scene.render.resolution_y = 960
scene.render.image_settings.file_format = 'PNG'

BENCH_BLEND = r"E:\Darx_Proyect\Saved\Player_Skin_Workspace\DarX_CraftingBench_Master.blend"
PLAYER_BLEND = r"E:\Darx_Proyect\Saved\Player_Skin_Workspace\DarX_Player_Rigged_Canonical.blend"
WEAPON_FBX = r"E:\Darx_Proyect\Art\FBX\Weapons\SM_Wep_BreacherS4.fbx"

# 1. Cargar Mesa de Crafteo
with bpy.data.libraries.load(BENCH_BLEND) as (df, dt):
    dt.objects = [o for o in df.objects if o.startswith('SM_CraftingBench')]

bench_objs = []
for o in dt.objects:
    scene.collection.objects.link(o)
    bench_objs.append(o)

# Posición y rotación de la mesa: rotada 180° para mirar al jugador (<>)
BENCH_Y = -0.75
for o in bench_objs:
    o.rotation_euler = (0, 0, math.pi)
    o.location = (0, BENCH_Y, 0)

# 2. Cargar Jugador 3P
with bpy.data.libraries.load(PLAYER_BLEND) as (df, dt):
    dt.objects = ['SK_Player', 'ARM_Player']

for o in dt.objects:
    scene.collection.objects.link(o)

player_mesh = bpy.data.objects['SK_Player']
arm_player = bpy.data.objects['ARM_Player']
arm_player.data.pose_position = 'POSE'
bpy.context.view_layer.objects.active = arm_player
bpy.ops.object.mode_set(mode='POSE')

# Inclinar torso ligeramente hacia adelante (postura ergonómica de trabajo)
for bname in ['spine', 'chest']:
    pb = arm_player.pose.bones.get(bname)
    if pb:
        pb.rotation_mode = 'XYZ'
        pb.rotation_euler = (R(10), 0, 0)

# Cabeza mirando hacia abajo hacia el arma/mesa
pb_neck = arm_player.pose.bones.get('neck')
if pb_neck:
    pb_neck.rotation_mode = 'XYZ'
    pb_neck.rotation_euler = (R(12), 0, 0)
pb_head = arm_player.pose.bones.get('head')
if pb_head:
    pb_head.rotation_mode = 'XYZ'
    pb_head.rotation_euler = (R(10), 0, 0)

# Targets IK
target_l = bpy.data.objects.new("IK_Target_L", None)
target_l.empty_display_type = 'SPHERE'
target_l.empty_display_size = 0.05
# Manos extendidas a los lados del arma (X = -0.32, Y = -0.55, Z = 0.98)
target_l.location = (-0.32, -0.55, 0.98)
scene.collection.objects.link(target_l)

target_r = bpy.data.objects.new("IK_Target_R", None)
target_r.empty_display_type = 'SPHERE'
target_r.empty_display_size = 0.05
target_r.location = (0.32, -0.55, 0.98)
scene.collection.objects.link(target_r)

pole_l = bpy.data.objects.new("IK_Pole_L", None)
pole_l.location = (-0.55, 0.10, 1.10)
scene.collection.objects.link(pole_l)

pole_r = bpy.data.objects.new("IK_Pole_R", None)
pole_r.location = (0.55, 0.10, 1.10)
scene.collection.objects.link(pole_r)

pb_fl = arm_player.pose.bones.get('forearm_L')
ik_l = pb_fl.constraints.new('IK')
ik_l.target = target_l
ik_l.pole_target = pole_l
ik_l.pole_angle = R(180)
ik_l.chain_count = 2

pb_fr = arm_player.pose.bones.get('forearm_R')
ik_r = pb_fr.constraints.new('IK')
ik_r.target = target_r
ik_r.pole_target = pole_r
ik_r.pole_angle = R(0)
ik_r.chain_count = 2

# Rotación de manos: palmas hacia adentro/abajo
pb_hl = arm_player.pose.bones.get('hand_L')
pb_hl.rotation_mode = 'XYZ'
pb_hl.rotation_euler = (R(-15), R(-40), R(20))

pb_hr = arm_player.pose.bones.get('hand_R')
pb_hr.rotation_mode = 'XYZ'
pb_hr.rotation_euler = (R(-15), R(40), R(-20))

bpy.ops.object.mode_set(mode='OBJECT')

# 3. Cargar Arma (Escopeta)
bpy.ops.import_scene.fbx(filepath=WEAPON_FBX)
wep_mesh = [o for o in bpy.data.objects if o.name.startswith('SM_Wep_BreacherS4') and o.type == 'MESH'][0]
# El arma levita exactamente en el centro entre las manos
wep_mesh.location = (0.0, -0.55, 1.02)
wep_mesh.rotation_euler = (R(12), R(-8), R(25))

# 4. Luces
l_plasma = bpy.data.objects.new("LGT_Plasma", bpy.data.lights.new("LGT_Plasma", 'POINT'))
l_plasma.data.energy = 120.0
l_plasma.data.color = (0.75, 0.20, 1.0)
l_plasma.location = (0.0, -0.55, 0.90)
scene.collection.objects.link(l_plasma)

l_key = bpy.data.objects.new("LGT_Key", bpy.data.lights.new("LGT_Key", 'AREA'))
l_key.data.energy = 260.0
l_key.data.size = 2.5
l_key.location = (1.8, -1.8, 2.2)
l_key.rotation_euler = (R(50), R(15), R(40))
scene.collection.objects.link(l_key)

l_fill = bpy.data.objects.new("LGT_Fill", bpy.data.lights.new("LGT_Fill", 'AREA'))
l_fill.data.energy = 140.0
l_fill.data.size = 2.5
l_fill.location = (-1.8, -0.8, 1.8)
l_fill.rotation_euler = (R(45), R(-15), R(-45))
scene.collection.objects.link(l_fill)

l_rim = bpy.data.objects.new("LGT_Rim", bpy.data.lights.new("LGT_Rim", 'AREA'))
l_rim.data.energy = 160.0
l_rim.data.size = 2.0
l_rim.location = (0.0, 1.5, 2.0)
l_rim.rotation_euler = (R(-40), 0, R(180))
scene.collection.objects.link(l_rim)

# 5. Cámaras de prueba (3P Front-Side y 1P)
cam_data = bpy.data.cameras.new("Cam_Test")
cam_obj = bpy.data.objects.new("Cam_Test", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj

# Test A: Vista 3P 3/4 Frontal
cam_obj.location = Vector((1.35, -1.35, 1.35))
direction = Vector((0.0, -0.45, 1.05)) - cam_obj.location
cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
cam_data.lens = 42

out_3p = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2\test_3p_fixed.png"
scene.render.filepath = out_3p
bpy.ops.render.render(write_still=True)
print(f"[OK] Render 3P guardado: {out_3p}")

# Test B: Vista 3P Over-The-Shoulder
cam_obj.location = Vector((0.75, 0.45, 1.65))
direction = Vector((0.0, -0.65, 0.98)) - cam_obj.location
cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
cam_data.lens = 35

out_ots = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2\test_ots_fixed.png"
scene.render.filepath = out_ots
bpy.ops.render.render(write_still=True)
print(f"[OK] Render OTS guardado: {out_ots}")

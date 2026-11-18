"""test_render_existing_player_walk.py
Renderiza un frame de A_Player_Walk.fbx para ver cómo se deforma la malla con animaciones existentes.
"""
import os
import math
import bpy
from mathutils import Vector

PROJECT_ROOT = r"E:\Darx_Proyect"
ART_DIR = os.path.join(PROJECT_ROOT, "Art")
BLENDER_DIR = os.path.join(ART_DIR, "Blender")
BRAIN_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"
PLAYER_FBX = os.path.join(ART_DIR, "FBX", "SK_Player.fbx")
WALK_FBX = os.path.join(ART_DIR, "FBX", "Anim_Player", "A_Player_Walk.fbx")

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# Cargar Player y Walk
bpy.ops.import_scene.fbx(filepath=PLAYER_FBX)
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]

bpy.ops.import_scene.fbx(filepath=WALK_FBX)
imported_arm = [o for o in bpy.data.objects if o.type == 'ARMATURE' and o != arm][0]
walk_act = imported_arm.animation_data.action

arm.animation_data_create()
arm.animation_data.action = walk_act
bpy.data.objects.remove(imported_arm, do_unlink=True)

scene.frame_set(10)
bpy.context.view_layer.update()

# Luces
l1 = bpy.data.objects.new("Key", bpy.data.lights.new("Key", 'SUN'))
l1.data.energy = 4.0
l1.rotation_euler = (math.radians(60), math.radians(15), math.radians(-25))
scene.collection.objects.link(l1)

l2 = bpy.data.objects.new("Fill", bpy.data.lights.new("Fill", 'AREA'))
l2.data.energy = 500.0
l2.location = (0.5, 2.0, 1.6)
scene.collection.objects.link(l2)

# Cámara frontal
cam_data = bpy.data.cameras.new("Cam")
cam_data.lens = 35
cam_obj = bpy.data.objects.new("Cam", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_obj.location = (0.0, 2.8, 1.2)
cam_obj.rotation_euler = (math.radians(90), 0, math.radians(180))

scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 960
scene.render.resolution_y = 540
out_img = os.path.join(BRAIN_DIR, "scratch", "test_original_player_walk.png")
scene.render.filepath = out_img
bpy.ops.render.render(write_still=True)
print(f"Renderizado walk original: {out_img}")

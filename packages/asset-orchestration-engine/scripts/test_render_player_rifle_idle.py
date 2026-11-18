"""test_render_player_rifle_idle.py
Renderiza A_Player_Rifle_Idle.fbx para ver cómo deforma la malla del jugador.
"""
import os
import math
import bpy

PROJECT_ROOT = r"E:\Darx_Proyect"
ART_DIR = os.path.join(PROJECT_ROOT, "Art")
BLENDER_DIR = os.path.join(ART_DIR, "Blender")
BRAIN_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"
PLAYER_FBX = os.path.join(ART_DIR, "FBX", "SK_Player.fbx")
RIFLE_IDLE = os.path.join(ART_DIR, "FBX", "Anim_Player", "A_Player_Rifle_Idle.fbx")

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

bpy.ops.import_scene.fbx(filepath=PLAYER_FBX)
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]

bpy.ops.import_scene.fbx(filepath=RIFLE_IDLE)
imported_arm = [o for o in bpy.data.objects if o.type == 'ARMATURE' and o != arm][0]
act = imported_arm.animation_data.action

arm.animation_data_create()
arm.animation_data.action = act
bpy.data.objects.remove(imported_arm, do_unlink=True)

scene.frame_set(1)
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

# Cámara 3/4 frontal
cam_data = bpy.data.cameras.new("Cam")
cam_data.lens = 38
cam_obj = bpy.data.objects.new("Cam", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_obj.location = (1.2, 2.2, 1.4)
target = bpy.data.objects.new("Target", None)
target.location = (0.0, 0.0, 1.2)
scene.collection.objects.link(target)
tt = cam_obj.constraints.new('TRACK_TO')
tt.target = target
tt.track_axis = 'TRACK_NEGATIVE_Z'
tt.up_axis = 'UP_Y'

scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 960
scene.render.resolution_y = 540
out_img = os.path.join(BRAIN_DIR, "scratch", "test_rifle_idle_deformation.png")
scene.render.filepath = out_img
bpy.ops.render.render(write_still=True)
print(f"Renderizado: {out_img}")

# -*- coding: utf-8 -*-
import bpy
import os
import math
from mathutils import Vector

FBX_PUNCH = r"E:\Darx_Proyect\Art\FBX\Anim_FPS\A_FPS_Unarmed_Punch_R.fbx"
FBX_ARMS = r"E:\Darx_Proyect\Art\FBX\SK_FPS_Arms.fbx"
BRAIN_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# 1. Cargar animacion punch
bpy.ops.import_scene.fbx(filepath=FBX_PUNCH)
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]

# 2. Cargar malla de brazos
bpy.ops.import_scene.fbx(filepath=FBX_ARMS)
mesh_arms = [o for o in bpy.data.objects if o.type == 'MESH'][0]

# Ocultar pistola vieja
for v in mesh_arms.data.vertices:
    for g in v.groups:
        if mesh_arms.vertex_groups[g.group].name in ('weapon', 'cell'):
            v.co = Vector((0, 0, -100))
            break
mesh_arms.parent = arm
mesh_arms.modifiers.new('Armature', 'ARMATURE').object = arm

# Luces
sun = bpy.data.lights.new("Sun", 'SUN')
sun.energy = 3.0
sun_obj = bpy.data.objects.new("Sun", sun)
sun_obj.rotation_euler = (math.radians(50), math.radians(15), math.radians(-30))
scene.collection.objects.link(sun_obj)

cam_data = bpy.data.cameras.new("Cam")
cam_data.lens = 18
cam_obj = bpy.data.objects.new("Cam", cam_data)
cam_obj.location = (0.01, 0.26, 0.08)
cam_obj.rotation_euler = (math.radians(85), 0, math.radians(180))
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj

scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, 'RenderSettings') and 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
scene.render.resolution_x = 960
scene.render.resolution_y = 540

for f in [0, 6]:
    scene.frame_set(f)
    out_path = os.path.join(BRAIN_DIR, f"preview_punch_f{f}.png")
    scene.render.filepath = out_path
    bpy.ops.render.render(write_still=True)
    print("Rendered:", out_path)

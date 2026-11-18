# -*- coding: utf-8 -*-
import bpy
import os

BRAIN_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"
scene = bpy.context.scene
arm = bpy.data.objects['ARM_FPS']
act = bpy.data.actions['A_FPS_Unarmed_Punch_R']
arm.animation_data.action = act

cam = bpy.data.objects['DARX_Cam_Show']
scene.camera = cam

# Ocultar mallas que no sean SK_FPS_Arms
for o in bpy.data.objects:
    if o.type == 'MESH' and o.name != 'SK_FPS_Arms':
        o.hide_render = True
    elif o.type == 'ARMATURE' and o.name != 'ARM_FPS':
        o.hide_render = True

# Habilitar luces DARX
for lname in ['DARX_Key', 'DARX_Fill', 'DARX_Rim']:
    l = bpy.data.objects.get(lname)
    if l:
        l.hide_render = False

arm.hide_render = False
mesh = bpy.data.objects['SK_FPS_Arms']
mesh.hide_render = False

scene.render.resolution_x = 960
scene.render.resolution_y = 540

for f in [0, 6]:
    scene.frame_set(f)
    bpy.context.view_layer.update()
    out_path = os.path.join(BRAIN_DIR, f"blend_punch_f{f}.png")
    scene.render.filepath = out_path
    bpy.ops.render.render(write_still=True)
    print("Rendered:", out_path)

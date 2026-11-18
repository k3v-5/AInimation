# -*- coding: utf-8 -*-
import bpy
import math
import os

BRAIN_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=r"E:\Darx_Proyect\Art\FBX\SK_FPS_Arms.fbx")

scene = bpy.context.scene
mesh = next(o for o in bpy.data.objects if o.type == 'MESH')
arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')

# Material
mat = bpy.data.materials.new(name="M_Test")
mat.use_nodes = True
mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (0.2, 0.5, 0.9, 1.0)
mesh.data.materials.clear()
mesh.data.materials.append(mat)

# Luz
l = bpy.data.lights.new("Sun", 'SUN')
l.energy = 5.0
lo = bpy.data.objects.new("Sun", l)
lo.rotation_euler = (math.radians(45), 0, math.radians(45))
scene.collection.objects.link(lo)

# Camara viendo la malla completa
cam = bpy.data.cameras.new("Cam")
co = bpy.data.objects.new("Cam", cam)
co.location = (0, -1.2, -0.2)
co.rotation_euler = (math.radians(85), 0, 0)
scene.collection.objects.link(co)
scene.camera = co

scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, 'RenderSettings') and 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
scene.render.resolution_x = 960
scene.render.resolution_y = 540
scene.render.filepath = os.path.join(BRAIN_DIR, "inspect_raw_fps_mesh.png")
bpy.ops.render.render(write_still=True)
print("Saved:", scene.render.filepath)

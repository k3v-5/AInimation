# -*- coding: utf-8 -*-
import bpy
import os
import math
from mathutils import Vector

FBX_ARMS = r"E:\Darx_Proyect\Art\FBX\SK_FPS_Arms.fbx"
FBX_PUNCH = r"E:\Darx_Proyect\Art\FBX\Anim_FPS\A_FPS_Unarmed_Punch_R.fbx"
BRAIN_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# 1. Cargar brazos canónicos
bpy.ops.import_scene.fbx(filepath=FBX_ARMS)
arm = bpy.data.objects['ARM_FPS_Arms']
mesh_arms = bpy.data.objects['SK_FPS_Arms']

# Ocultar pistola base de la plantilla para el golpe
for v in mesh_arms.data.vertices:
    for g in v.groups:
        if mesh_arms.vertex_groups[g.group].name in ('weapon', 'cell'):
            v.co = Vector((0, 0, -100))
            break

# 2. Importar animacion del golpe y asignarla a arm
bpy.ops.import_scene.fbx(filepath=FBX_PUNCH)
arm_anim = [o for o in bpy.data.objects if o.type == 'ARMATURE' and o != arm][0]
act = arm_anim.animation_data.action
arm.animation_data_create()
arm.animation_data.action = act
if hasattr(act, "slots") and len(act.slots):
    arm.animation_data.action_slot = act.slots[0]
bpy.data.objects.remove(arm_anim, do_unlink=True)

# Material visible
mat = bpy.data.materials.new(name="M_Arms_Vis")
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.2, 0.45, 0.75, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.3
mesh_arms.data.materials.clear()
mesh_arms.data.materials.append(mat)

# 3. Luces
world = bpy.data.worlds.new("W_Vis")
scene.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.07, 0.08, 0.10, 1.0)
world.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.0

key_light = bpy.data.lights.new("KeyLight", 'AREA')
key_light.energy = 80.0
key_light.size = 0.6
key_obj = bpy.data.objects.new("KeyLight", key_light)
key_obj.location = (0.2, -0.4, 0.3)
scene.collection.objects.link(key_obj)

fill_light = bpy.data.lights.new("FillLight", 'AREA')
fill_light.energy = 40.0
fill_light.size = 0.8
fill_obj = bpy.data.objects.new("FillLight", fill_light)
fill_obj.location = (-0.3, -0.2, 0.1)
scene.collection.objects.link(fill_obj)

cam_data = bpy.data.cameras.new("Cam_FPS")
cam_data.lens = 22
cam_obj = bpy.data.objects.new("Cam_FPS", cam_data)
cam_obj.location = (0.0, 0.10, 0.0)
cam_obj.rotation_euler = (math.radians(78), 0, math.radians(180))
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj

scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, 'RenderSettings') and 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
scene.render.resolution_x = 960
scene.render.resolution_y = 540

for f in [0, 6]:
    scene.frame_set(f)
    bpy.context.view_layer.update()
    out_path = os.path.join(BRAIN_DIR, f"preview_punch_f{f}.png")
    scene.render.filepath = out_path
    bpy.ops.render.render(write_still=True)
    print(f"Rendered punch F{f}:", out_path)

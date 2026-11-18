# -*- coding: utf-8 -*-
import bpy
import os
import math
from mathutils import Vector

FBX_ARMS = r"E:\Darx_Proyect\Art\FBX\SK_FPS_Arms.fbx"
WEP_FBX = r"E:\Darx_Proyect\Art\FBX\Weapons\SM_Wep_BreacherS4.fbx"
ANIM_FBX = r"E:\Darx_Proyect\Art\FBX\Anim_FPS\A_FPS_Shotgun_Reload.fbx"
BRAIN_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

bpy.ops.import_scene.fbx(filepath=FBX_ARMS)
arm = bpy.data.objects['ARM_FPS_Arms']
mesh_arms = bpy.data.objects['SK_FPS_Arms']

for v in mesh_arms.data.vertices:
    for g in v.groups:
        if mesh_arms.vertex_groups[g.group].name in ('weapon', 'cell'):
            v.co = Vector((0, 0, -100))
            break

bpy.ops.import_scene.fbx(filepath=WEP_FBX)
wep_mesh = [o for o in bpy.data.objects if o not in (arm, mesh_arms) and o.type == 'MESH'][0]
wep_mesh.parent = arm
wep_mesh.parent_type = 'BONE'
wep_mesh.parent_bone = 'weapon'
wep_mesh.location = (0.0, 0.0, 0.0)
wep_mesh.rotation_euler = (0, 0, 0)

bpy.ops.import_scene.fbx(filepath=ANIM_FBX)
arm_anim = [o for o in bpy.data.objects if o.type == 'ARMATURE' and o != arm][0]
act = arm_anim.animation_data.action
arm.animation_data_create()
arm.animation_data.action = act
if hasattr(act, "slots") and len(act.slots):
    arm.animation_data.action_slot = act.slots[0]
bpy.data.objects.remove(arm_anim, do_unlink=True)

scene.frame_set(42)
bpy.context.view_layer.update()

# Materiales
mat_arm = bpy.data.materials.new(name="M_Arm")
mat_arm.use_nodes = True
bsdf_arm = mat_arm.node_tree.nodes.get("Principled BSDF")
if bsdf_arm:
    bsdf_arm.inputs['Base Color'].default_value = (0.15, 0.40, 0.72, 1.0)
    bsdf_arm.inputs['Roughness'].default_value = 0.35
mesh_arms.data.materials.clear()
mesh_arms.data.materials.append(mat_arm)

mat_wep = bpy.data.materials.new(name="M_Wep")
mat_wep.use_nodes = True
bsdf_w = mat_wep.node_tree.nodes.get("Principled BSDF")
if bsdf_w:
    bsdf_w.inputs['Base Color'].default_value = (0.85, 0.88, 0.92, 1.0)
    bsdf_w.inputs['Metallic'].default_value = 0.85
    bsdf_w.inputs['Roughness'].default_value = 0.2
wep_mesh.data.materials.clear()
wep_mesh.data.materials.append(mat_wep)

# Luces
world = bpy.data.worlds.new("W_Test")
scene.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.06, 0.07, 0.09, 1.0)
world.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.0

key_light = bpy.data.lights.new("Key", 'AREA')
key_light.energy = 100.0
key_light.size = 0.8
key_obj = bpy.data.objects.new("Key", key_light)
key_obj.location = (0.3, -0.5, 0.4)
scene.collection.objects.link(key_obj)

fill_light = bpy.data.lights.new("Fill", 'AREA')
fill_light.energy = 50.0
fill_light.size = 1.0
fill_obj = bpy.data.objects.new("Fill", fill_light)
fill_obj.location = (-0.4, -0.3, 0.2)
scene.collection.objects.link(fill_obj)

# CAMARA EN LA POSICION REAL DE LOS OJOS (Y=0.24, Z=0.06)
cam_data = bpy.data.cameras.new("Cam_FPS")
cam_data.sensor_width = 36.0
cam_data.lens = 24.0 # FOV amplio
cam_obj = bpy.data.objects.new("Cam_FPS", cam_data)
cam_obj.location = (0.0, 0.24, 0.06)

# Mirar hacia el arma
target = wep_mesh.matrix_world.translation
direction = target - cam_obj.location
cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

scene.collection.objects.link(cam_obj)
scene.camera = cam_obj

scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, 'RenderSettings') and 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
scene.render.resolution_x = 960
scene.render.resolution_y = 540

out_path = os.path.join(BRAIN_DIR, "preview_real_eye_test.png")
scene.render.filepath = out_path
bpy.ops.render.render(write_still=True)
print("Rendered eye test:", out_path)

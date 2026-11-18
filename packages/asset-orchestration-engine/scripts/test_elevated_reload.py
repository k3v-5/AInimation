# -*- coding: utf-8 -*-
import bpy
import os
import math
from mathutils import Vector

FBX_ARMS = r"E:\Darx_Proyect\Art\FBX\SK_FPS_Arms.fbx"
WEP_FBX = r"E:\Darx_Proyect\Art\FBX\Weapons\SM_Wep_Apex6.fbx"
BRAIN_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# 1. Cargar brazos canónicos
bpy.ops.import_scene.fbx(filepath=FBX_ARMS)
arm = bpy.data.objects['ARM_FPS_Arms']
mesh_arms = bpy.data.objects['SK_FPS_Arms']

# Ocultar pistola vieja de la plantilla
for v in mesh_arms.data.vertices:
    for g in v.groups:
        if mesh_arms.vertex_groups[g.group].name in ('weapon', 'cell'):
            v.co = Vector((0, 0, -100))
            break

# 2. Cargar arma Apex 6
bpy.ops.import_scene.fbx(filepath=WEP_FBX)
wep_mesh = [o for o in bpy.data.objects if o not in (arm, mesh_arms) and o.type == 'MESH'][0]
wep_mesh.parent = arm
wep_mesh.parent_type = 'BONE'
wep_mesh.parent_bone = 'weapon'
wep_mesh.location = (0, 0.08, 0)
wep_mesh.rotation_euler = (0, 0, 0)

# 3. Material visible para brazos
mat_arm = bpy.data.materials.new(name="M_Arms_Vis")
mat_arm.use_nodes = True
bsdf = mat_arm.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.2, 0.45, 0.75, 1.0) # Azul táctico
    bsdf.inputs['Roughness'].default_value = 0.3
mesh_arms.data.materials.clear()
mesh_arms.data.materials.append(mat_arm)

# 4. Material brillante para el arma
mat_wep = bpy.data.materials.new(name="M_Wep_Vis")
mat_wep.use_nodes = True
bsdf_w = mat_wep.node_tree.nodes.get("Principled BSDF")
if bsdf_w:
    bsdf_w.inputs['Base Color'].default_value = (0.85, 0.88, 0.92, 1.0)
    bsdf_w.inputs['Metallic'].default_value = 0.8
    bsdf_w.inputs['Roughness'].default_value = 0.2
wep_mesh.data.materials.clear()
wep_mesh.data.materials.append(mat_wep)

# 5. Configurar pose de recarga elevada y visible (Root levantado 8 cm y adelantado 4 cm)
for pb in arm.pose.bones:
    pb.rotation_mode = 'XYZ'

arm.pose.bones['root'].location = (0.0, -0.04, 0.09)

# Brazo derecho sostiene el arma en el tercio medio-inferior de la pantalla
arm.pose.bones['upperarm_R'].rotation_euler = [math.radians(a) for a in (-12, 14, -2)]
arm.pose.bones['forearm_R'].rotation_euler = [math.radians(a) for a in (18, 4, 0)]
arm.pose.bones['hand_R'].rotation_euler = [math.radians(a) for a in (5, -10, 8)]

# Brazo izquierdo asciende claramente y encastra la celda de energía en la empuñadura
arm.pose.bones['upperarm_L'].rotation_euler = [math.radians(a) for a in (-28, -35, 24)]
arm.pose.bones['forearm_L'].rotation_euler = [math.radians(a) for a in (32, 12, -10)]
arm.pose.bones['hand_L'].rotation_euler = [math.radians(a) for a in (15, 10, 20)]

bpy.context.view_layer.update()

# 6. Luces y entorno claro
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

# Camara FPS alineada con Unreal Engine (FOV 70 horizontal, 16:9)
cam_data = bpy.data.cameras.new("Cam_FPS")
cam_data.sensor_width = 36.0
cam_data.lens = 25.7 # Exacto 70 deg horiz FOV en 36mm
cam_obj = bpy.data.objects.new("Cam_FPS", cam_data)
cam_obj.location = (0.0, 0.0, 0.0) # En el origen de la camara
cam_obj.rotation_euler = (math.radians(82), 0, math.radians(180)) # Leve pitch hacia abajo de 8 deg
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj

scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, 'RenderSettings') and 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
scene.render.resolution_x = 960
scene.render.resolution_y = 540

out_path = os.path.join(BRAIN_DIR, "preview_elevated_reload_test.png")
scene.render.filepath = out_path
bpy.ops.render.render(write_still=True)

hl = arm.matrix_world @ arm.pose.bones["hand_L"].matrix.translation
hr = arm.matrix_world @ arm.pose.bones["hand_R"].matrix.translation
wep = arm.matrix_world @ arm.pose.bones["weapon"].matrix.translation
print(f"hand_L pos: ({hl.x:.3f}, {hl.y:.3f}, {hl.z:.3f})")
print(f"hand_R pos: ({hr.x:.3f}, {hr.y:.3f}, {hr.z:.3f})")
print(f"wep pos:    ({wep.x:.3f}, {wep.y:.3f}, {wep.z:.3f})")
print("Rendered:", out_path)

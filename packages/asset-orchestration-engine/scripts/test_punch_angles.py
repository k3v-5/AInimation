# -*- coding: utf-8 -*-
"""test_punch_angles.py
Renderiza 4 variantes de rotación del puño en el impacto máximo (Frame 6):
1. Straight Cross (Pronación completa, nudillos horizontales)
2. Vertical Fist (Nudillos verticales, clásico combate cuerpo a cuerpo)
3. Heavy Hook / Overhand (Golpe curvo potente con antebrazo en ángulo)
4. Fast Jab (Golpe directo rápido y estilizado)
Compone las 4 vistas espejadas (orientación real UE5) en una imagen para comparar.
"""

import sys, os, math
import bpy
from mathutils import Vector, Euler

FBX_ARMS = r"E:\Darx_Proyect\Art\FBX\SK_FPS_Arms.fbx"
BRAIN_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"

VARIANTS = [
    {
        "name": "1. Straight Cross (Pronado)",
        "upperarm_R": (-30, -22, 18),
        "forearm_R": (42, -14, 12),
        "hand_R": (18, -14, 80),
        "root_z": 0.14,
        "root_y": -0.14
    },
    {
        "name": "2. Vertical Fist (Nudillos Verticales)",
        "upperarm_R": (-28, -18, 14),
        "forearm_R": (40, -10, 8),
        "hand_R": (10, -5, 10),
        "root_z": 0.14,
        "root_y": -0.14
    },
    {
        "name": "3. Heavy Overhand / Hook",
        "upperarm_R": (-24, -32, 28),
        "forearm_R": (48, -18, 16),
        "hand_R": (25, -20, 110),
        "root_z": 0.14,
        "root_y": -0.14
    },
    {
        "name": "4. Fast Tactical Jab",
        "upperarm_R": (-26, -14, 10),
        "forearm_R": (36, -8, 6),
        "hand_R": (15, -10, 45),
        "root_z": 0.14,
        "root_y": -0.14
    }
]

rendered_files = []

for idx, var in enumerate(VARIANTS):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=FBX_ARMS)
    arm = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
    mesh = next(o for o in bpy.data.objects if o.type == 'MESH')
    arm.name = "ARM_FPS"

    # Ocultar pistola vieja
    for v in mesh.data.vertices:
        for g in v.groups:
            if mesh.vertex_groups[g.group].name in ('weapon', 'cell'):
                v.co = Vector((0, 0, -100))
                break

    for pb in arm.pose.bones:
        pb.rotation_mode = 'XYZ'
        pb.rotation_euler = (0, 0, 0)
        pb.location = (0, 0, 0)

    # Root
    arm.pose.bones['root'].location = (0.0, var['root_z'], -var['root_y'])

    # Right arm (punch)
    arm.pose.bones['upperarm_R'].rotation_euler = [math.radians(a) for a in var['upperarm_R']]
    arm.pose.bones['forearm_R'].rotation_euler = [math.radians(a) for a in var['forearm_R']]
    arm.pose.bones['hand_R'].rotation_euler = [math.radians(a) for a in var['hand_R']]

    # Left arm (guard)
    arm.pose.bones['upperarm_L'].rotation_euler = [math.radians(a) for a in (24, -18, 20)]
    arm.pose.bones['forearm_L'].rotation_euler = [math.radians(a) for a in (-34, 16, -14)]
    arm.pose.bones['hand_L'].rotation_euler = [math.radians(a) for a in (22, -6, 24)]

    bpy.context.view_layer.update()

    # Material
    mat = bpy.data.materials.new(name=f"M_{idx}")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.18, 0.42, 0.78, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.35
    mesh.data.materials.clear()
    mesh.data.materials.append(mat)

    scene = bpy.context.scene
    world = bpy.data.worlds.new(f"W_{idx}")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.06, 0.07, 0.09, 1.0)

    # 3 Luces
    l1 = bpy.data.lights.new("L1", 'AREA'); l1.energy = 140.0; l1.size = 1.0
    o1 = bpy.data.objects.new("L1", l1); o1.location = (0.4, -0.3, 0.4)
    scene.collection.objects.link(o1)

    l2 = bpy.data.lights.new("L2", 'AREA'); l2.energy = 70.0; l2.size = 1.2
    o2 = bpy.data.objects.new("L2", l2); o2.location = (-0.5, -0.2, 0.3)
    scene.collection.objects.link(o2)

    l3 = bpy.data.lights.new("L3", 'AREA'); l3.energy = 90.0; l3.color = (0.8, 0.6, 1.0)
    o3 = bpy.data.objects.new("L3", l3); o3.location = (0.0, 0.3, 0.0)
    scene.collection.objects.link(o3)

    # Cámara horizontal FPS
    cam_data = bpy.data.cameras.new("Cam")
    cam_data.sensor_width = 36.0
    cam_data.lens = 22.0
    cam_obj = bpy.data.objects.new("Cam", cam_data)
    cam_obj.location = (0.0, 0.18, 0.05)
    cam_obj.rotation_euler = (math.radians(90.0), 0.0, math.radians(180.0))
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, 'RenderSettings') and 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
    scene.render.resolution_x = 960
    scene.render.resolution_y = 540

    out_p = os.path.join(BRAIN_DIR, f"temp_punch_var_{idx}.png")
    scene.render.filepath = out_p
    bpy.ops.render.render(write_still=True)
    rendered_files.append((out_p, var['name']))
    print(f"Rendered {var['name']}: {out_p}")

print("=== ALL 4 PUNCH VARIANTS RENDERED ===")

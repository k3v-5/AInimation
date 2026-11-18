# -*- coding: utf-8 -*-
"""render_reload_mosaics.py
Renderiza un mosaico de 4 cuadrantes con las poses clave de recarga de las 4 armas en FPS
para la validacion visual previa del usuario (Regla 4 y 5 de AGENTS.md).
"""

import bpy
import bmesh
import os
import math
from mathutils import Vector, Euler

ART_DIR = r"E:\Darx_Proyect\Art"
FBX_FPS_DIR = os.path.join(ART_DIR, "FBX", "Anim_FPS")
FBX_ARMS = os.path.join(ART_DIR, "FBX", "SK_FPS_Arms.fbx")
BRAIN_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"
OUT_IMAGE = os.path.join(BRAIN_DIR, "preview_reload_suite.png")

# Armas correspondientes
WEAPONS = [
    ("A_FPS_Pistol_Reload.fbx", r"E:\Darx_Proyect\Art\FBX\Weapons\SM_Wep_Apex6.fbx", 22, (0, 0.08, 0)),
    ("A_FPS_SMG_Reload.fbx", r"E:\Darx_Proyect\Art\FBX\Weapons\SM_Wep_PhaseSMG.fbx", 36, (0.01, 0.08, 0)),
    ("A_FPS_Shotgun_Reload.fbx", r"E:\Darx_Proyect\Art\FBX\Weapons\SM_Wep_BreacherS4.fbx", 42, (0, 0.08, 0)),
    ("A_FPS_Rifle_Reload.fbx", r"E:\Darx_Proyect\Art\FBX\Weapons\SM_Wep_VanguardAR.fbx", 34, (0, 0.08, 0))
]

rendered_frames = []

for idx, (anim_fbx, wep_fbx, target_frame, wep_loc) in enumerate(WEAPONS):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    
    # 1. Cargar brazos con su animacion
    anim_path = os.path.join(FBX_FPS_DIR, anim_fbx)
    bpy.ops.import_scene.fbx(filepath=anim_path)
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

    # 3. Cargar arma
    if os.path.exists(wep_fbx):
        bpy.ops.import_scene.fbx(filepath=wep_fbx)
        wep_objs = [o for o in bpy.data.objects if o != mesh_arms and o != arm and o.type == 'MESH']
        if wep_objs:
            wep_mesh = wep_objs[0]
            wep_mesh.parent = arm
            wep_mesh.parent_type = 'BONE'
            wep_mesh.parent_bone = 'weapon'
            wep_mesh.location = wep_loc

    # Set frame
    scene.frame_set(target_frame)

    # World & Lights
    world = bpy.data.worlds.new("W_Render")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.03, 0.035, 0.045, 1.0)
    world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.8

    sun = bpy.data.lights.new("Sun", 'SUN')
    sun.energy = 4.0
    sun_obj = bpy.data.objects.new("Sun", sun)
    sun_obj.rotation_euler = (math.radians(50), math.radians(15), math.radians(-30))
    scene.collection.objects.link(sun_obj)

    light_fill = bpy.data.lights.new("Fill", 'AREA')
    light_fill.energy = 120.0
    light_fill.color = (0.8, 0.4, 1.0)
    l_obj = bpy.data.objects.new("Fill", light_fill)
    l_obj.location = (0, -0.4, 0.2)
    scene.collection.objects.link(l_obj)

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
    scene.render.resolution_percentage = 100

    frame_path = os.path.join(BRAIN_DIR, f"temp_reload_quad_{idx}.png")
    scene.render.filepath = frame_path
    bpy.ops.render.render(write_still=True)
    rendered_frames.append(frame_path)
    print(f"Renderizado cuadrante {idx}: {frame_path}")

# Combinar los 4 cuadrantes en una imagen 1920x1080
try:
    from PIL import Image
    im0 = Image.open(rendered_frames[0])
    im1 = Image.open(rendered_frames[1])
    im2 = Image.open(rendered_frames[2])
    im3 = Image.open(rendered_frames[3])
    
    mosaic = Image.new('RGB', (1920, 1080), (10, 10, 15))
    mosaic.paste(im0, (0, 0))
    mosaic.paste(im1, (960, 0))
    mosaic.paste(im2, (0, 540))
    mosaic.paste(im3, (960, 540))
    mosaic.save(OUT_IMAGE)
    print(f"[OK] Mosaico de 4 cuadrantes guardado en: {OUT_IMAGE}")
except Exception as e:
    print(f"PIL no disponible o error ({e}); copiando primer render como preview.")
    if rendered_frames:
        shutil.copyfile(rendered_frames[0], OUT_IMAGE)

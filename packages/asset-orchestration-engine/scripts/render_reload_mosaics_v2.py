# -*- coding: utf-8 -*-
"""render_reload_mosaics_v2.py
Renderiza los 4 cuadrantes con las poses clave de recarga de las 4 armas en FPS
mostrando nítidamente ambas manos (derecha empuñando, izquierda manipulando la munición).
"""

import os
import math
import bpy
from mathutils import Vector, Euler

ART_DIR = r"E:\Darx_Proyect\Art"
FBX_FPS_DIR = os.path.join(ART_DIR, "FBX", "Anim_FPS")
FBX_ARMS = os.path.join(ART_DIR, "FBX", "SK_FPS_Arms.fbx")
BRAIN_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"

WEAPONS_DATA = [
    {
        "title": "1. PISTOLA APEX 6 — ENCASTRE MAGNÉTICO DE MICRO-CELDA",
        "anim": "A_FPS_Pistol_Reload.fbx",
        "wep": r"E:\Darx_Proyect\Art\FBX\Weapons\SM_Wep_Apex6.fbx",
        "frame": 22,
        "wep_offset": (0.0, 0.08, 0.0)
    },
    {
        "title": "2. SUBFUSIL PHASE SMG — MONTAJE DE TAMBOR TOROIDAL",
        "anim": "A_FPS_SMG_Reload.fbx",
        "wep": r"E:\Darx_Proyect\Art\FBX\Weapons\SM_Wep_PhaseSMG.fbx",
        "frame": 28,
        "wep_offset": (0.01, 0.08, 0.0)
    },
    {
        "title": "3. ESCOPETA BREACHER S4 — BOMBEO MECÁNICO DE PLASMA",
        "anim": "A_FPS_Shotgun_Reload.fbx",
        "wep": r"E:\Darx_Proyect\Art\FBX\Weapons\SM_Wep_BreacherS4.fbx",
        "frame": 42,
        "wep_offset": (0.0, 0.08, 0.0)
    },
    {
        "title": "4. RIFLE VANGUARD AR — PALMADA AL CERROJO (BOLT SLAP)",
        "anim": "A_FPS_Rifle_Reload.fbx",
        "wep": r"E:\Darx_Proyect\Art\FBX\Weapons\SM_Wep_VanguardAR.fbx",
        "frame": 34,
        "wep_offset": (0.0, 0.08, 0.0)
    }
]

for idx, wdata in enumerate(WEAPONS_DATA):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene

    # 1. Cargar brazos base
    bpy.ops.import_scene.fbx(filepath=FBX_ARMS)
    arm = bpy.data.objects['ARM_FPS_Arms']
    mesh_arms = bpy.data.objects['SK_FPS_Arms']

    # Ocultar pistola vieja de la plantilla
    for v in mesh_arms.data.vertices:
        for g in v.groups:
            if mesh_arms.vertex_groups[g.group].name in ('weapon', 'cell'):
                v.co = Vector((0, 0, -100))
                break

    # 2. Cargar arma
    bpy.ops.import_scene.fbx(filepath=wdata["wep"])
    wep_mesh = [o for o in bpy.data.objects if o not in (arm, mesh_arms) and o.type == 'MESH'][0]
    wep_mesh.parent = arm
    wep_mesh.parent_type = 'BONE'
    wep_mesh.parent_bone = 'weapon'
    wep_mesh.location = wdata["wep_offset"]
    wep_mesh.rotation_euler = (0, 0, 0)

    # 3. Importar y asignar animación
    anim_fbx_path = os.path.join(FBX_FPS_DIR, wdata["anim"])
    bpy.ops.import_scene.fbx(filepath=anim_fbx_path)
    arm_anim = [o for o in bpy.data.objects if o.type == 'ARMATURE' and o != arm][0]
    act = arm_anim.animation_data.action
    arm.animation_data_create()
    arm.animation_data.action = act
    if hasattr(act, "slots") and len(act.slots):
        arm.animation_data.action_slot = act.slots[0]
    bpy.data.objects.remove(arm_anim, do_unlink=True)

    scene.frame_set(wdata["frame"])
    bpy.context.view_layer.update()

    # 4. Materiales con buen contraste
    mat_arm = bpy.data.materials.new(name=f"M_Arm_{idx}")
    mat_arm.use_nodes = True
    bsdf_arm = mat_arm.node_tree.nodes.get("Principled BSDF")
    if bsdf_arm:
        bsdf_arm.inputs['Base Color'].default_value = (0.18, 0.42, 0.70, 1.0) # Traje táctico azul
        bsdf_arm.inputs['Roughness'].default_value = 0.35
    mesh_arms.data.materials.clear()
    mesh_arms.data.materials.append(mat_arm)

    mat_wep = bpy.data.materials.new(name=f"M_Wep_{idx}")
    mat_wep.use_nodes = True
    bsdf_w = mat_wep.node_tree.nodes.get("Principled BSDF")
    if bsdf_w:
        bsdf_w.inputs['Base Color'].default_value = (0.85, 0.88, 0.92, 1.0) # Metal titanio
        bsdf_w.inputs['Metallic'].default_value = 0.85
        bsdf_w.inputs['Roughness'].default_value = 0.2
    wep_mesh.data.materials.clear()
    wep_mesh.data.materials.append(mat_wep)

    # 5. Luces de estudio
    world = bpy.data.worlds.new(f"W_{idx}")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.06, 0.07, 0.09, 1.0)
    world.node_tree.nodes['Background'].inputs['Strength'].default_value = 1.0

    key_light = bpy.data.lights.new("Key", 'AREA')
    key_light.energy = 90.0
    key_light.size = 0.7
    key_obj = bpy.data.objects.new("Key", key_light)
    key_obj.location = (0.25, -0.45, 0.35)
    scene.collection.objects.link(key_obj)

    fill_light = bpy.data.lights.new("Fill", 'AREA')
    fill_light.energy = 45.0
    fill_light.size = 0.9
    fill_obj = bpy.data.objects.new("Fill", fill_light)
    fill_obj.location = (-0.35, -0.25, 0.15)
    scene.collection.objects.link(fill_obj)

    rim_light = bpy.data.lights.new("Rim", 'AREA')
    rim_light.energy = 50.0
    rim_light.color = (0.7, 0.5, 1.0) # Resplandor púrpura de plasma
    rim_obj = bpy.data.objects.new("Rim", rim_light)
    rim_obj.location = (0.0, 0.2, -0.1)
    scene.collection.objects.link(rim_obj)

    # 6. Cámara FPS calibrada al FOV de Unreal Engine 5
    cam_data = bpy.data.cameras.new("Cam_FPS")
    cam_data.sensor_width = 36.0
    cam_data.lens = 25.7 # 70 deg horiz FOV
    cam_obj = bpy.data.objects.new("Cam_FPS", cam_data)
    cam_obj.location = (0.0, 0.0, 0.0)
    cam_obj.rotation_euler = (math.radians(82), 0, math.radians(180))
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, 'RenderSettings') and 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
    scene.render.resolution_x = 960
    scene.render.resolution_y = 540

    quad_file = os.path.join(BRAIN_DIR, f"temp_quad_v2_{idx}.png")
    scene.render.filepath = quad_file
    bpy.ops.render.render(write_still=True)
    print(f"[RENDER OK] Cuadrante {idx+1}: {quad_file}")

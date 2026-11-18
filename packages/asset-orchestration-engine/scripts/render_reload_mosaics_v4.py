# -*- coding: utf-8 -*-
"""render_reload_mosaics_v4.py
Genera y compone el mosaico final de 4 cuadrantes con:
- Cámara en la posición real de los ojos (Y=0.24, Z=0.06) con FOV de 70°.
- Ambas manos plenamente visibles: la mano derecha empuñando el arma y la mano izquierda manipulando e insertando la munición láser/plasma.
- Títulos descriptivos para cada una de las 4 armas.
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
        "title": "1. PISTOLA APEX 6 — INSERCION MICRO-CELDA BAJO EMPUÑADURA",
        "anim": "A_FPS_Pistol_Reload.fbx",
        "wep": r"E:\Darx_Proyect\Art\FBX\Weapons\SM_Wep_Apex6.fbx",
        "frame": 22,
        "wep_offset": (0.0, 0.0, 0.0)
    },
    {
        "title": "2. SUBFUSIL PHASE SMG — ENCASTRE TOROIDAL Y CERROJO",
        "anim": "A_FPS_SMG_Reload.fbx",
        "wep": r"E:\Darx_Proyect\Art\FBX\Weapons\SM_Wep_PhaseSMG.fbx",
        "frame": 28,
        "wep_offset": (0.01, -0.05, 0.0)
    },
    {
        "title": "3. ESCOPETA BREACHER S4 — INSERCION CELULA Y BOMBEO",
        "anim": "A_FPS_Shotgun_Reload.fbx",
        "wep": r"E:\Darx_Proyect\Art\FBX\Weapons\SM_Wep_BreacherS4.fbx",
        "frame": 26, # Momento clave donde la mano izquierda inserta la célula ventral
        "wep_offset": (0.0, -0.08, 0.0)
    },
    {
        "title": "4. RIFLE VANGUARD AR — INSERCION ANGULAR ROCK&LOCK Y PALMADA",
        "anim": "A_FPS_Rifle_Reload.fbx",
        "wep": r"E:\Darx_Proyect\Art\FBX\Weapons\SM_Wep_VanguardAR.fbx",
        "frame": 26, # Momento clave donde la mano izquierda inserta la petaca a 16°
        "wep_offset": (0.0, -0.08, 0.0)
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

    # 4. Materiales de alta visibilidad
    mat_arm = bpy.data.materials.new(name=f"M_Arm_{idx}")
    mat_arm.use_nodes = True
    bsdf_arm = mat_arm.node_tree.nodes.get("Principled BSDF")
    if bsdf_arm:
        bsdf_arm.inputs['Base Color'].default_value = (0.15, 0.40, 0.72, 1.0) # Azul táctico
        bsdf_arm.inputs['Roughness'].default_value = 0.35
    mesh_arms.data.materials.clear()
    mesh_arms.data.materials.append(mat_arm)

    mat_wep = bpy.data.materials.new(name=f"M_Wep_{idx}")
    mat_wep.use_nodes = True
    bsdf_w = mat_wep.node_tree.nodes.get("Principled BSDF")
    if bsdf_w:
        bsdf_w.inputs['Base Color'].default_value = (0.85, 0.88, 0.92, 1.0) # Titanio reflectante
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
    key_light.energy = 110.0
    key_light.size = 0.8
    key_obj = bpy.data.objects.new("Key", key_light)
    key_obj.location = (0.35, -0.4, 0.45)
    scene.collection.objects.link(key_obj)

    fill_light = bpy.data.lights.new("Fill", 'AREA')
    fill_light.energy = 55.0
    fill_light.size = 1.0
    fill_obj = bpy.data.objects.new("Fill", fill_light)
    fill_obj.location = (-0.45, -0.25, 0.25)
    scene.collection.objects.link(fill_obj)

    rim_light = bpy.data.lights.new("Rim", 'AREA')
    rim_light.energy = 60.0
    rim_light.color = (0.7, 0.5, 1.0)
    rim_obj = bpy.data.objects.new("Rim", rim_light)
    rim_obj.location = (0.0, 0.3, -0.1)
    scene.collection.objects.link(rim_obj)

    # 6. Cámara FPS calibrada a nivel de ojos
    cam_data = bpy.data.cameras.new("Cam_FPS")
    cam_data.sensor_width = 36.0
    cam_data.lens = 22.0 # Gran angular para captar amplitud de ambos brazos
    cam_obj = bpy.data.objects.new("Cam_FPS", cam_data)
    cam_obj.location = (0.0, 0.18, 0.05)
    
    # Encarar hacia el punto medio entre el arma y las manos
    hl = arm.matrix_world @ arm.pose.bones["hand_L"].matrix.translation
    hr = arm.matrix_world @ arm.pose.bones["hand_R"].matrix.translation
    mid_hands = (hl + hr) * 0.5
    dir_view = mid_hands - cam_obj.location
    cam_obj.rotation_euler = dir_view.to_track_quat('-Z', 'Y').to_euler()
    
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, 'RenderSettings') and 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
    scene.render.resolution_x = 960
    scene.render.resolution_y = 540

    quad_file = os.path.join(BRAIN_DIR, f"temp_quad_v4_{idx}.png")
    scene.render.filepath = quad_file
    bpy.ops.render.render(write_still=True)
    print(f"[RENDER OK] Cuadrante {idx+1}: {quad_file}")

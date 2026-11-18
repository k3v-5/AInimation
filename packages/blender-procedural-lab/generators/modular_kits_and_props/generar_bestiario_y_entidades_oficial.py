# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Generador Oficial del Bestiario, Jefes y Mascotas Alienígenas para Blender 5.2 LTS
# Modela 10 entidades completas con materiales PBR estilizados retro y renderiza showcase de alta resolución.

import bpy
import bmesh
import math
import os
from mathutils import Vector, Matrix, Euler

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if not bpy.data.scenes:
        bpy.data.scenes.new("Scene")
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types.RenderSettings, 'engine') and 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
    scene.render.resolution_x = 2560
    scene.render.resolution_y = 1440
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    return scene

def create_pbr_material(name, base_color, metallic=0.1, roughness=0.5, emission_color=(0,0,0,1), emission_strength=0.0, alpha=1.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new('ShaderNodeOutputMaterial')
    principled = nodes.new('ShaderNodeBsdfPrincipled')
    principled.inputs['Base Color'].default_value = base_color
    principled.inputs['Metallic'].default_value = metallic
    principled.inputs['Roughness'].default_value = roughness
    
    # Manejo de emisión compatible con Blender 5.x
    if 'Emission Color' in principled.inputs:
        principled.inputs['Emission Color'].default_value = emission_color
        principled.inputs['Emission Strength'].default_value = emission_strength
    elif 'Emission' in principled.inputs:
        principled.inputs['Emission'].default_value = emission_color
        if 'Emission Strength' in principled.inputs:
            principled.inputs['Emission Strength'].default_value = emission_strength

    if alpha < 1.0:
        if 'Alpha' in principled.inputs:
            principled.inputs['Alpha'].default_value = alpha
        mat.blend_method = 'BLEND' if hasattr(mat, 'blend_method') else 'HASHED'

    links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    return mat

# ==============================================================================
# MODELADO DE ENTIDADES
# ==============================================================================

def create_cinder_stalker(location=Vector((-6.0, 0, 0)), scale=1.0, is_alpha=False):
    """Cinder Stalker (Abrasador) / Alfa: Bestia ígnea de roca volcánica y magma"""
    prefix = "CinderStalker_Alpha" if is_alpha else "CinderStalker"
    root = bpy.data.objects.new(prefix, None)
    bpy.context.collection.objects.link(root)
    root.location = location

    # Materiales: Roca volcánica áspera + Magma incandescente
    mat_rock = create_pbr_material(f"{prefix}_Rock", (0.05, 0.04, 0.04, 1.0), metallic=0.2, roughness=0.9)
    magma_color = (1.0, 0.25, 0.02, 1.0) if not is_alpha else (1.0, 0.08, 0.01, 1.0)
    mat_magma = create_pbr_material(f"{prefix}_Magma", magma_color, metallic=0.1, roughness=0.3, emission_color=magma_color, emission_strength=12.0)

    # Torso de basalto
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=0.6 * scale, location=(0, 0, 1.2 * scale))
    torso = bpy.context.active_object
    torso.name = f"{prefix}_Torso"
    torso.scale = (0.9, 0.7, 1.3)
    torso.parent = root
    torso.data.materials.append(mat_rock)

    # Núcleo de magma incandescente interior
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.4 * scale, location=(0, 0.1 * scale, 1.2 * scale))
    core = bpy.context.active_object
    core.name = f"{prefix}_Core"
    core.parent = root
    core.data.materials.append(mat_magma)

    # Cabeza con cuernos/crestas de obsidiana
    bpy.ops.mesh.primitive_cone_add(radius1=0.35 * scale, depth=0.6 * scale, location=(0, 0.2 * scale, 2.0 * scale), rotation=(math.radians(15), 0, 0))
    head = bpy.context.active_object
    head.name = f"{prefix}_Head"
    head.parent = root
    head.data.materials.append(mat_rock)

    # Ojos / Fisuras ardientes en la cabeza
    for side in (-1, 1):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.06 * scale, depth=0.15 * scale, location=(side * 0.18 * scale, 0.35 * scale, 2.05 * scale), rotation=(math.radians(80), 0, side * math.radians(20)))
        eye = bpy.context.active_object
        eye.name = f"{prefix}_Eye_{side}"
        eye.parent = root
        eye.data.materials.append(mat_magma)

    # Brazos de roca volcánica
    for side in (-1, 1):
        # Brazo superior
        bpy.ops.mesh.primitive_cylinder_add(radius=0.18 * scale, depth=0.8 * scale, location=(side * 0.8 * scale, 0, 1.4 * scale), rotation=(0, side * math.radians(25), 0))
        arm = bpy.context.active_object
        arm.name = f"{prefix}_ArmUpper_{side}"
        arm.parent = root
        arm.data.materials.append(mat_rock)
        
        # Garras de magma
        bpy.ops.mesh.primitive_cone_add(radius1=0.22 * scale, depth=0.7 * scale, location=(side * 1.1 * scale, 0.2 * scale, 0.8 * scale), rotation=(math.radians(45), 0, side * math.radians(30)))
        claw = bpy.context.active_object
        claw.name = f"{prefix}_Claw_{side}"
        claw.parent = root
        claw.data.materials.append(mat_magma)

    # Si es Alfa, añadir crestas colosales en hombros y espalda
    if is_alpha:
        for i, z in enumerate((1.4, 1.8, 2.2)):
            for side in (-1, 1):
                bpy.ops.mesh.primitive_cone_add(radius1=0.15 * scale, depth=0.8 * scale, location=(side * (0.5 + i*0.1) * scale, -0.4 * scale, z * scale), rotation=(math.radians(-40), side * math.radians(25), 0))
                spike = bpy.context.active_object
                spike.name = f"{prefix}_Spike_{i}_{side}"
                spike.parent = root
                spike.data.materials.append(mat_magma if i==1 else mat_rock)

    return root

def create_corporate_auditor_droid(location=Vector((-3.0, 0, 0)), scale=1.0, is_enforcer=False):
    """Droide Auditor Astra Corp / Enforcer Mk-IV: Androide militarizado con blindaje y porra"""
    prefix = "Enforcer_MkIV" if is_enforcer else "AuditorDroid"
    root = bpy.data.objects.new(prefix, None)
    bpy.context.collection.objects.link(root)
    root.location = location

    # Materiales: Titanio desgastado, Chasis negro, Visor Ámbar LED
    mat_armor = create_pbr_material(f"{prefix}_Armor", (0.75, 0.65, 0.35, 1.0) if not is_enforcer else (0.25, 0.28, 0.32, 1.0), metallic=0.85, roughness=0.35)
    mat_frame = create_pbr_material(f"{prefix}_Frame", (0.1, 0.1, 0.12, 1.0), metallic=0.9, roughness=0.4)
    led_color = (1.0, 0.6, 0.05, 1.0) if not is_enforcer else (0.9, 0.05, 0.05, 1.0)
    mat_visor = create_pbr_material(f"{prefix}_Visor", led_color, metallic=0.1, roughness=0.1, emission_color=led_color, emission_strength=10.0)

    # Torso / Chasis blindado
    bpy.ops.mesh.primitive_cube_add(size=0.8 * scale, location=(0, 0, 1.25 * scale))
    torso = bpy.context.active_object
    torso.scale = (0.9, 0.6, 1.1)
    torso.name = f"{prefix}_Torso"
    torso.parent = root
    torso.data.materials.append(mat_armor)

    # Placa pectoral con serigrafía corporativa
    bpy.ops.mesh.primitive_cube_add(size=0.5 * scale, location=(0, 0.28 * scale, 1.35 * scale))
    chest_plate = bpy.context.active_object
    chest_plate.scale = (0.7, 0.15, 0.6)
    chest_plate.name = f"{prefix}_ChestPlate"
    chest_plate.parent = root
    chest_plate.data.materials.append(mat_frame)

    # Cabeza cilíndrica con visor CRT
    bpy.ops.mesh.primitive_cylinder_add(radius=0.22 * scale, depth=0.35 * scale, location=(0, 0, 1.85 * scale))
    head = bpy.context.active_object
    head.name = f"{prefix}_Head"
    head.parent = root
    head.data.materials.append(mat_armor)

    # Visor horizontal LED
    bpy.ops.mesh.primitive_cube_add(size=0.25 * scale, location=(0, 0.15 * scale, 1.87 * scale))
    visor = bpy.context.active_object
    visor.scale = (0.9, 0.3, 0.25)
    visor.name = f"{prefix}_Visor"
    visor.parent = root
    visor.data.materials.append(mat_visor)

    # Piernas hidráulicas
    for side in (-1, 1):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.1 * scale, depth=0.8 * scale, location=(side * 0.25 * scale, 0, 0.45 * scale))
        leg = bpy.context.active_object
        leg.name = f"{prefix}_Leg_{side}"
        leg.parent = root
        leg.data.materials.append(mat_frame)

    # Brazos y Porra de Choque / Escudo
    # Brazo derecho con Porra de Electrochoque
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08 * scale, depth=0.7 * scale, location=(0.5 * scale, 0, 1.2 * scale))
    arm_r = bpy.context.active_object
    arm_r.name = f"{prefix}_Arm_R"
    arm_r.parent = root
    arm_r.data.materials.append(mat_frame)

    # Porra eléctrica
    bpy.ops.mesh.primitive_cylinder_add(radius=0.04 * scale, depth=1.0 * scale, location=(0.5 * scale, 0.3 * scale, 0.8 * scale), rotation=(math.radians(35), 0, 0))
    baton = bpy.context.active_object
    baton.name = f"{prefix}_ShockBaton"
    baton.parent = root
    baton.data.materials.append(mat_frame)
    # Punta de la porra electrificada
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08 * scale, location=(0.5 * scale, 0.65 * scale, 1.25 * scale))
    baton_tip = bpy.context.active_object
    baton_tip.name = f"{prefix}_BatonTip"
    baton_tip.parent = root
    baton_tip.data.materials.append(mat_visor)

    # Si es Enforcer Mk-IV: Escudo balístico masivo en brazo izquierdo
    if is_enforcer:
        bpy.ops.mesh.primitive_cube_add(size=1.0 * scale, location=(-0.65 * scale, 0.3 * scale, 1.1 * scale))
        shield = bpy.context.active_object
        shield.scale = (0.1, 0.6, 1.2)
        shield.name = f"{prefix}_RiotShield"
        shield.parent = root
        shield.data.materials.append(mat_armor)

    return root

def create_vent_stalker(location=Vector((0.0, 0, 0)), scale=1.0):
    """Acechador de Conductos: Criatura biomecánica insectoide con garras trepadoras"""
    root = bpy.data.objects.new("VentStalker", None)
    bpy.context.collection.objects.link(root)
    root.location = location

    mat_chitin = create_pbr_material("VentStalker_Chitin", (0.12, 0.15, 0.14, 1.0), metallic=0.4, roughness=0.3)
    mat_flesh = create_pbr_material("VentStalker_Bio", (0.35, 0.08, 0.15, 1.0), metallic=0.1, roughness=0.6)
    mat_eye = create_pbr_material("VentStalker_Eye", (0.2, 1.0, 0.4, 1.0), emission_color=(0.2, 1.0, 0.4, 1.0), emission_strength=8.0)

    # Torso segmentado alargado
    for i in range(4):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=(0.4 - i*0.06) * scale, location=(0, -i*0.35 * scale, (1.3 - i*0.15) * scale))
        segment = bpy.context.active_object
        segment.scale = (0.8, 1.2, 0.7)
        segment.name = f"VentStalker_Segment_{i}"
        segment.parent = root
        segment.data.materials.append(mat_chitin)

    # Cabeza aplanada depredadora
    bpy.ops.mesh.primitive_cone_add(radius1=0.3 * scale, depth=0.6 * scale, location=(0, 0.35 * scale, 1.45 * scale), rotation=(math.radians(80), 0, 0))
    head = bpy.context.active_object
    head.scale = (1.1, 0.6, 1.0)
    head.name = "VentStalker_Head"
    head.parent = root
    head.data.materials.append(mat_chitin)

    # Ojos múltiples bioluminiscentes verdes
    for side in (-1, 1):
        for o in (0, 0.1, 0.2):
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.04 * scale, location=(side * (0.15 + o*0.4) * scale, (0.45 + o) * scale, 1.48 * scale))
            eye = bpy.context.active_object
            eye.name = f"VentStalker_Eye_{side}_{o}"
            eye.parent = root
            eye.data.materials.append(mat_eye)

    # 4 Patas trepadoras articuladas
    for pair in (0, 1):
        y_off = -pair * 0.45 * scale
        for side in (-1, 1):
            bpy.ops.mesh.primitive_cylinder_add(radius=0.06 * scale, depth=0.9 * scale, location=(side * 0.65 * scale, y_off, 1.3 * scale), rotation=(0, side * math.radians(45), side * math.radians(30)))
            leg_upper = bpy.context.active_object
            leg_upper.name = f"VentStalker_LegUpper_{pair}_{side}"
            leg_upper.parent = root
            leg_upper.data.materials.append(mat_chitin)

            bpy.ops.mesh.primitive_cylinder_add(radius=0.04 * scale, depth=1.1 * scale, location=(side * 1.1 * scale, y_off, 0.6 * scale), rotation=(0, -side * math.radians(25), 0))
            leg_lower = bpy.context.active_object
            leg_lower.name = f"VentStalker_LegLower_{pair}_{side}"
            leg_lower.parent = root
            leg_lower.data.materials.append(mat_flesh)

    return root

def create_hoarder_gremlin(location=Vector((3.0, 0, 0)), scale=1.0):
    """Duende Chatarrero: Criatura pequeña y escurridiza con bolsa de chatarra robada"""
    root = bpy.data.objects.new("HoarderGremlin", None)
    bpy.context.collection.objects.link(root)
    root.location = location

    mat_skin = create_pbr_material("Gremlin_Skin", (0.45, 0.38, 0.28, 1.0), metallic=0.1, roughness=0.8)
    mat_sack = create_pbr_material("Gremlin_Sack", (0.22, 0.18, 0.12, 1.0), metallic=0.2, roughness=0.9)
    mat_scrap = create_pbr_material("Gremlin_ScrapMetal", (0.8, 0.75, 0.7, 1.0), metallic=0.9, roughness=0.3)
    mat_eye = create_pbr_material("Gremlin_Eye", (1.0, 0.8, 0.1, 1.0), emission_color=(1.0, 0.8, 0.1, 1.0), emission_strength=7.0)

    # Cuerpo jorobado pequeño
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.35 * scale, location=(0, 0, 0.55 * scale))
    body = bpy.context.active_object
    body.scale = (0.8, 0.9, 1.1)
    body.name = "Gremlin_Body"
    body.parent = root
    body.data.materials.append(mat_skin)

    # Cabeza grande con orejas puntiagudas
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.28 * scale, location=(0, 0.2 * scale, 0.85 * scale))
    head = bpy.context.active_object
    head.name = "Gremlin_Head"
    head.parent = root
    head.data.materials.append(mat_skin)

    # Ojos saltones
    for side in (-1, 1):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.09 * scale, location=(side * 0.14 * scale, 0.38 * scale, 0.9 * scale))
        eye = bpy.context.active_object
        eye.name = f"Gremlin_Eye_{side}"
        eye.parent = root
        eye.data.materials.append(mat_eye)

        # Orejas de murciélago
        bpy.ops.mesh.primitive_cone_add(radius1=0.08 * scale, depth=0.35 * scale, location=(side * 0.32 * scale, 0.1 * scale, 1.05 * scale), rotation=(0, side * math.radians(55), 0))
        ear = bpy.context.active_object
        ear.name = f"Gremlin_Ear_{side}"
        ear.parent = root
        ear.data.materials.append(mat_skin)

    # Mochila / Saco de chatarra en la joroba
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.45 * scale, location=(0, -0.35 * scale, 0.7 * scale))
    sack = bpy.context.active_object
    sack.scale = (1.0, 0.8, 1.2)
    sack.name = "Gremlin_Sack"
    sack.parent = root
    sack.data.materials.append(mat_sack)

    # Piezas de herramientas y tuberías asomando del saco
    bpy.ops.mesh.primitive_cylinder_add(radius=0.05 * scale, depth=0.6 * scale, location=(0.1 * scale, -0.4 * scale, 1.15 * scale), rotation=(math.radians(25), math.radians(-20), 0))
    pipe_scrap = bpy.context.active_object
    pipe_scrap.name = "Gremlin_Scrap_Pipe"
    pipe_scrap.parent = root
    pipe_scrap.data.materials.append(mat_scrap)

    # Brazos largos ladrones
    for side in (-1, 1):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.06 * scale, depth=0.65 * scale, location=(side * 0.38 * scale, 0.1 * scale, 0.5 * scale), rotation=(math.radians(-30), side * math.radians(15), 0))
        arm = bpy.context.active_object
        arm.name = f"Gremlin_Arm_{side}"
        arm.parent = root
        arm.data.materials.append(mat_skin)

    return root

def create_thermal_echo_silhouette(location=Vector((6.0, 0, 0)), scale=1.0):
    """Silueta de Eco Térmico: Entidad espectral translúcida azulada a -40°C"""
    root = bpy.data.objects.new("ThermalEcho", None)
    bpy.context.collection.objects.link(root)
    root.location = location

    # Material espectral azul cian con brillo frío y transparencia
    mat_ghost = create_pbr_material("ThermalEcho_Spectral", (0.2, 0.7, 1.0, 0.45), metallic=0.0, roughness=0.1, emission_color=(0.1, 0.8, 1.0, 1.0), emission_strength=6.0, alpha=0.55)

    # Silueta humanoide etérea
    bpy.ops.mesh.primitive_cylinder_add(radius=0.28 * scale, depth=1.1 * scale, location=(0, 0, 0.9 * scale))
    torso = bpy.context.active_object
    torso.scale = (0.8, 0.6, 1.0)
    torso.name = "ThermalEcho_Torso"
    torso.parent = root
    torso.data.materials.append(mat_ghost)

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22 * scale, location=(0, 0, 1.65 * scale))
    head = bpy.context.active_object
    head.scale = (0.8, 0.9, 1.1)
    head.name = "ThermalEcho_Head"
    head.parent = root
    head.data.materials.append(mat_ghost)

    # Ojos vacíos espectrales
    for side in (-1, 1):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05 * scale, location=(side * 0.08 * scale, 0.18 * scale, 1.68 * scale))
        eye = bpy.context.active_object
        eye.name = f"ThermalEcho_Eye_{side}"
        eye.parent = root
        eye.data.materials.append(mat_ghost)

    # Brazos espectrales vaporosos
    for side in (-1, 1):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.09 * scale, depth=0.85 * scale, location=(side * 0.45 * scale, 0, 1.0 * scale), rotation=(math.radians(15), side * math.radians(25), 0))
        arm = bpy.context.active_object
        arm.name = f"ThermalEcho_Arm_{side}"
        arm.parent = root
        arm.data.materials.append(mat_ghost)

    # Cristales de escarcha flotantes alrededor
    for i in range(6):
        ang = i * (math.pi / 3)
        bpy.ops.mesh.primitive_cone_add(radius1=0.04 * scale, depth=0.25 * scale, location=(math.cos(ang)*0.6 * scale, math.sin(ang)*0.6 * scale, (1.0 + math.sin(i)*0.4) * scale))
        frost = bpy.context.active_object
        frost.name = f"ThermalEcho_Frost_{i}"
        frost.parent = root
        frost.data.materials.append(mat_ghost)

    return root

# ==============================================================================
# MODELADO DE MASCOTAS POR TIERS
# ==============================================================================

def create_alien_pets(base_location=Vector((-1.5, -3.5, 0))):
    """Modela las 3 mascotas alienígenas por Tier"""
    root = bpy.data.objects.new("AlienPets_Collection", None)
    bpy.context.collection.objects.link(root)
    root.location = base_location

    # Tier 1: Glip-Glop Dócil (Esférico gelatinoso lila)
    mat_glip = create_pbr_material("GlipGlop_Gelatin", (0.7, 0.3, 0.85, 0.8), roughness=0.1, emission_color=(0.5, 0.1, 0.7, 1.0), emission_strength=2.0, alpha=0.85)
    mat_eye = create_pbr_material("Pet_BigEye", (0.05, 0.05, 0.05, 1.0), roughness=0.1)

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=(-1.8, 0, 0.3))
    glip = bpy.context.active_object
    glip.name = "Pet_GlipGlop_Body"
    glip.scale = (1.0, 1.0, 0.85)
    glip.parent = root
    glip.data.materials.append(mat_glip)

    for side in (-1, 1):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.08, location=(-1.8 + side*0.12, 0.22, 0.38))
        geye = bpy.context.active_object
        geye.name = f"Pet_Glip_Eye_{side}"
        geye.parent = root
        geye.data.materials.append(mat_eye)

    # Tier 2: Hurón Estelar Evasivo (Nebula Weasel - Cian fosfórico)
    mat_weasel = create_pbr_material("NebulaWeasel_Fur", (0.1, 0.7, 0.85, 1.0), roughness=0.4, emission_color=(0.1, 0.6, 0.8, 1.0), emission_strength=4.0)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.7, location=(0, 0, 0.25), rotation=(0, math.radians(90), 0))
    weasel_body = bpy.context.active_object
    weasel_body.name = "Pet_NebulaWeasel_Body"
    weasel_body.parent = root
    weasel_body.data.materials.append(mat_weasel)

    bpy.ops.mesh.primitive_cone_add(radius1=0.12, depth=0.3, location=(0.4, 0, 0.28), rotation=(0, math.radians(-90), 0))
    weasel_head = bpy.context.active_object
    weasel_head.name = "Pet_NebulaWeasel_Head"
    weasel_head.parent = root
    weasel_head.data.materials.append(mat_weasel)

    # Tier 3: Cinderling Termófilo (Pequeño reptil de plasma incandescente naranja)
    mat_cinder = create_pbr_material("Cinderling_Scales", (1.0, 0.35, 0.05, 1.0), roughness=0.3, emission_color=(1.0, 0.3, 0.02, 1.0), emission_strength=10.0)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=(1.8, 0, 0.25))
    cinder_body = bpy.context.active_object
    cinder_body.scale = (1.4, 0.8, 0.7)
    cinder_body.name = "Pet_Cinderling_Body"
    cinder_body.parent = root
    cinder_body.data.materials.append(mat_cinder)

    # Cola de fuego
    bpy.ops.mesh.primitive_cone_add(radius1=0.08, depth=0.45, location=(1.45, 0, 0.28), rotation=(0, math.radians(75), 0))
    cinder_tail = bpy.context.active_object
    cinder_tail.name = "Pet_Cinderling_Tail"
    cinder_tail.parent = root
    cinder_tail.data.materials.append(mat_cinder)

    return root

# ==============================================================================
# CONFIGURACIÓN DE ILUMINACIÓN Y CÁMARA SHOWCASE
# ==============================================================================

def setup_lighting_and_render(output_path):
    scene = bpy.context.scene

    # Suelo industrial metálico oscuro con cuadrícula de contención
    mat_floor = create_pbr_material("Showcase_Floor", (0.04, 0.04, 0.05, 1.0), metallic=0.7, roughness=0.4)
    bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = "Showcase_Floor"
    floor.data.materials.append(mat_floor)

    # Luces clave cinematográficas
    light_data_main = bpy.data.lights.new(name="Light_MainKey", type='AREA')
    light_data_main.energy = 4500.0
    light_data_main.size = 12.0
    light_data_main.color = (0.9, 0.95, 1.0)
    light_obj_main = bpy.data.objects.new("Light_MainKey", light_data_main)
    bpy.context.collection.objects.link(light_obj_main)
    light_obj_main.location = (0, -8.0, 7.0)
    light_obj_main.rotation_euler = (math.radians(48), 0, 0)

    # Luz de relleno cian espacial
    light_data_rim = bpy.data.lights.new(name="Light_RimCyan", type='AREA')
    light_data_rim.energy = 3000.0
    light_data_rim.size = 14.0
    light_data_rim.color = (0.1, 0.6, 1.0)
    light_obj_rim = bpy.data.objects.new("Light_RimCyan", light_data_rim)
    bpy.context.collection.objects.link(light_obj_rim)
    light_obj_rim.location = (0, 8.0, 5.0)
    light_obj_rim.rotation_euler = (math.radians(-45), 0, math.radians(180))

    # Luz ámbar cálida lateral
    light_data_warm = bpy.data.lights.new(name="Light_SideAmber", type='POINT')
    light_data_warm.energy = 2000.0
    light_data_warm.color = (1.0, 0.45, 0.1)
    light_obj_warm = bpy.data.objects.new("Light_SideAmber", light_data_warm)
    bpy.context.collection.objects.link(light_obj_warm)
    light_obj_warm.location = (-9.0, -3.0, 3.5)

    # Cámara principal panorámica de showcase
    cam_data = bpy.data.cameras.new(name="Camera_Showcase")
    cam_data.lens = 32
    cam_obj = bpy.data.objects.new("Camera_Showcase", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    cam_obj.location = (0, -11.0, 3.8)
    cam_obj.rotation_euler = (math.radians(76), 0, 0)
    scene.camera = cam_obj

    # Renderizar imagen
    scene.render.filepath = output_path
    bpy.ops.render.render(write_still=True)
    print(f">>> Renderizado exitoso en: {output_path}")

def main():
    print("==========================================================")
    print(">>> INICIANDO GENERACIÓN DE BESTIARIO Y ENTIDADES OFICIAL")
    print("==========================================================")
    reset_scene()

    # 1. Monstruos y Entidades regulares
    create_cinder_stalker(location=Vector((-6.0, 0, 0)), scale=1.0, is_alpha=False)
    create_corporate_auditor_droid(location=Vector((-3.0, 0, 0)), scale=1.0, is_enforcer=False)
    create_vent_stalker(location=Vector((0.0, 0, 0)), scale=1.0)
    create_hoarder_gremlin(location=Vector((3.0, 0, 0)), scale=1.0)
    create_thermal_echo_silhouette(location=Vector((6.0, 0, 0)), scale=1.0)

    # 2. Jefes de Tier (Cinder Stalker Alfa y Enforcer Mk-IV) en plano posterior
    create_cinder_stalker(location=Vector((-4.5, 3.5, 0)), scale=1.6, is_alpha=True)
    create_corporate_auditor_droid(location=Vector((3.5, 3.5, 0)), scale=1.4, is_enforcer=True)

    # 3. Mascotas Alienígenas por Tier en primer plano
    create_alien_pets(base_location=Vector((0.0, -2.5, 0)))

    # Guardar archivo .blend maestro
    blend_path = "F:/Dev/Game/Art/Blender/Bestiario_Entidades_Oficial.blend"
    os.makedirs(os.path.dirname(blend_path), exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f">>> Archivo .blend guardado en: {blend_path}")

    # Renderizar showcase general
    render_output = "F:/Dev/Game/Art/Renders/Showcase_Bestiario_Entidades.png"
    os.makedirs(os.path.dirname(render_output), exist_ok=True)
    setup_lighting_and_render(render_output)

    print(">>> GENERACIÓN DE BESTIARIO COMPLETADA CON ÉXITO <<<")

if __name__ == "__main__":
    main()

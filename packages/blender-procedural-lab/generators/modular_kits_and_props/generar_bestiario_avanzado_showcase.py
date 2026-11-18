# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Generador Oficial del Bestiario Avanzado, Jefes y Mascotas Alienígenas para Blender 5.2 LTS
# Modela 10 entidades completas con materiales PBR estilizados retro y renderiza showcase de alta resolución.

import bpy
import bmesh
import math
import os
from mathutils import Vector, Matrix, Euler

RENDERS_DIR = "F:/Dev/Game/Art/Renders"
ARTIFACT_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\b59ff04f-3c21-4ee5-94b0-8e8f899f8923"
os.makedirs(RENDERS_DIR, exist_ok=True)
os.makedirs(ARTIFACT_DIR, exist_ok=True)

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

def create_weathered_pbr_material(name,
                                  color_clean,
                                  color_grime,
                                  color_wear,
                                  metallic,
                                  roughness_clean,
                                  roughness_worn,
                                  grunge_scale=10.0,
                                  bump_strength=0.18,
                                  noise_detail=8.0,
                                  emissive_color=(0, 0, 0, 1),
                                  emissive_strength=0.0,
                                  alpha=1.0):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out_node = nodes.new(type='ShaderNodeOutputMaterial')
    out_node.location = (700, 0)

    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (350, 0)
    bsdf.inputs['Metallic'].default_value = metallic

    # Coordenadas y mapeo
    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    tex_coord.location = (-750, 0)

    mapping = nodes.new(type='ShaderNodeMapping')
    mapping.location = (-580, 0)
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])

    # Ruido procedural de desgaste
    noise_macro = nodes.new(type='ShaderNodeTexNoise')
    noise_macro.location = (-380, 150)
    noise_macro.inputs['Scale'].default_value = grunge_scale
    noise_macro.inputs['Detail'].default_value = noise_detail
    noise_macro.inputs['Roughness'].default_value = 0.7
    links.new(mapping.outputs['Vector'], noise_macro.inputs['Vector'])

    # Rampa de color
    ramp_color = nodes.new(type='ShaderNodeValToRGB')
    ramp_color.location = (-120, 200)
    cr = ramp_color.color_ramp
    cr.elements[0].position = 0.20
    cr.elements[0].color = color_grime
    cr.elements[1].position = 0.65
    cr.elements[1].color = color_clean
    elem_wear = cr.elements.new(0.88)
    elem_wear.color = color_wear
    links.new(noise_macro.outputs['Fac'], ramp_color.inputs['Fac'])
    links.new(ramp_color.outputs['Color'], bsdf.inputs['Base Color'])

    # Rampa de rugosidad
    ramp_rough = nodes.new(type='ShaderNodeValToRGB')
    ramp_rough.location = (-120, -60)
    cr_r = ramp_rough.color_ramp
    cr_r.elements[0].position = 0.20
    cr_r.elements[0].color = (roughness_worn, roughness_worn, roughness_worn, 1.0)
    cr_r.elements[1].position = 0.85
    cr_r.elements[1].color = (roughness_clean, roughness_clean, roughness_clean, 1.0)
    links.new(noise_macro.outputs['Fac'], ramp_rough.inputs['Fac'])
    links.new(ramp_rough.outputs['Color'], bsdf.inputs['Roughness'])

    # Micro-relieve (Bump)
    if bump_strength > 0.0:
        bump = nodes.new(type='ShaderNodeBump')
        bump.location = (120, -200)
        bump.inputs['Strength'].default_value = bump_strength
        bump.inputs['Distance'].default_value = 0.03
        links.new(noise_macro.outputs['Fac'], bump.inputs['Height'])
        links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    # Emisión
    if emissive_strength > 0.0:
        if 'Emission Color' in bsdf.inputs:
            bsdf.inputs['Emission Color'].default_value = emissive_color
            bsdf.inputs['Emission Strength'].default_value = emissive_strength
        elif 'Emission' in bsdf.inputs:
            bsdf.inputs['Emission'].default_value = emissive_color
            if 'Emission Strength' in bsdf.inputs:
                bsdf.inputs['Emission Strength'].default_value = emissive_strength

    if alpha < 1.0:
        if 'Alpha' in bsdf.inputs:
            bsdf.inputs['Alpha'].default_value = alpha
        mat.blend_method = 'BLEND' if hasattr(mat, 'blend_method') else 'HASHED'

    links.new(bsdf.outputs['BSDF'], out_node.inputs['Surface'])
    return mat

# ==============================================================================
# MODELADO DETALLADO CON ESTRUCTURA COMPLEJA
# ==============================================================================

def build_cinder_stalker(location, scale=1.0, is_alpha=False):
    """Cinder Stalker de basalto fractal con fisuras de lava y garras de magma"""
    name = "CinderStalker_Alpha" if is_alpha else "CinderStalker"
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    root.location = location

    mat_rock = create_weathered_pbr_material(
        f"{name}_Rock",
        color_clean=(0.04, 0.035, 0.035, 1.0),
        color_grime=(0.02, 0.018, 0.015, 1.0),
        color_wear=(0.18, 0.12, 0.08, 1.0),
        metallic=0.1, roughness_clean=0.85, roughness_worn=0.95,
        grunge_scale=14.0, bump_strength=0.35
    )
    magma_col = (1.0, 0.12, 0.01, 1.0) if is_alpha else (1.0, 0.28, 0.02, 1.0)
    mat_magma = create_weathered_pbr_material(
        f"{name}_Magma",
        color_clean=magma_col,
        color_grime=(0.8, 0.05, 0.0, 1.0),
        color_wear=(1.0, 0.8, 0.1, 1.0),
        metallic=0.0, roughness_clean=0.2, roughness_worn=0.4,
        emissive_color=magma_col, emissive_strength=18.0 if is_alpha else 12.0
    )

    # 1. Torso de múltiples bloques de basalto angulados
    for i in range(4):
        z_pos = (0.9 + i * 0.35) * scale
        bpy.ops.mesh.primitive_cube_add(size=(0.7 - i*0.06) * scale, location=(0, 0, z_pos))
        block = bpy.context.active_object
        block.scale = (1.1 - i*0.1, 0.85, 0.75)
        block.rotation_euler = (math.radians(-5 + i*4), math.radians((i%2)*8 - 4), 0)
        block.name = f"{name}_Torso_Block_{i}"
        block.parent = root
        block.data.materials.append(mat_rock)

    # Núcleo de magma interno expuesto en el pecho
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=0.38 * scale, location=(0, 0.25 * scale, 1.45 * scale))
    core = bpy.context.active_object
    core.name = f"{name}_HeartCore"
    core.parent = root
    core.data.materials.append(mat_magma)

    # 2. Cabeza demoníaca de carbón con fauces de obsidiana
    bpy.ops.mesh.primitive_cone_add(radius1=0.32 * scale, depth=0.75 * scale, location=(0, 0.25 * scale, 2.25 * scale), rotation=(math.radians(25), 0, 0))
    head = bpy.context.active_object
    head.scale = (0.9, 0.7, 1.0)
    head.name = f"{name}_Head"
    head.parent = root
    head.data.materials.append(mat_rock)

    # Ojos y grietas faciales ardientes
    for side in (-1, 1):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.04 * scale, depth=0.2 * scale, location=(side * 0.16 * scale, 0.48 * scale, 2.28 * scale), rotation=(math.radians(75), 0, side * math.radians(15)))
        eye = bpy.context.active_object
        eye.name = f"{name}_Eye_{side}"
        eye.parent = root
        eye.data.materials.append(mat_magma)

    # Cuernos / Picos dorsales
    num_spikes = 6 if is_alpha else 3
    for s in range(num_spikes):
        z_s = (1.5 + s * 0.2) * scale
        for side in (-1, 1):
            bpy.ops.mesh.primitive_cone_add(radius1=(0.12 + s*0.02) * scale, depth=(0.6 + s*0.15) * scale, location=(side * (0.45 + s*0.08) * scale, -0.35 * scale, z_s), rotation=(math.radians(-45), side * math.radians(35), 0))
            spike = bpy.context.active_object
            spike.name = f"{name}_Spike_{s}_{side}"
            spike.parent = root
            spike.data.materials.append(mat_magma if s % 2 == 1 else mat_rock)

    # 3. Brazos pesados con articulaciones de lava y garras de basalto
    for side in (-1, 1):
        # Hombro rocoso
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.28 * scale, location=(side * 0.75 * scale, 0, 1.8 * scale))
        shoulder = bpy.context.active_object
        shoulder.parent = root
        shoulder.data.materials.append(mat_rock)

        # Brazo superior
        bpy.ops.mesh.primitive_cylinder_add(radius=0.18 * scale, depth=0.75 * scale, location=(side * 0.95 * scale, 0.1 * scale, 1.35 * scale), rotation=(0, side * math.radians(25), 0))
        bicep = bpy.context.active_object
        bicep.parent = root
        bicep.data.materials.append(mat_rock)

        # Antebrazo de magma expuesto
        bpy.ops.mesh.primitive_cylinder_add(radius=0.14 * scale, depth=0.7 * scale, location=(side * 1.15 * scale, 0.3 * scale, 0.85 * scale), rotation=(math.radians(35), 0, side * math.radians(20)))
        forearm = bpy.context.active_object
        forearm.parent = root
        forearm.data.materials.append(mat_magma)

        # 3 Garras puntiagudas de obsidiana por mano
        for c in range(3):
            bpy.ops.mesh.primitive_cone_add(radius1=0.06 * scale, depth=0.45 * scale, location=(side * (1.1 + c*0.12) * scale, 0.65 * scale, (0.55 - c*0.08) * scale), rotation=(math.radians(65), 0, side * math.radians(15)))
            claw = bpy.context.active_object
            claw.parent = root
            claw.data.materials.append(mat_rock)

    # 4. Piernas de pilar volcánico
    for side in (-1, 1):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.22 * scale, depth=0.9 * scale, location=(side * 0.35 * scale, 0, 0.45 * scale))
        leg = bpy.context.active_object
        leg.scale = (1.0, 1.1, 1.0)
        leg.parent = root
        leg.data.materials.append(mat_rock)

    return root

def build_auditor_droid(location, scale=1.0, is_enforcer=False):
    """Droide Auditor Astra Corp / Enforcer Mk-IV militarizado"""
    name = "Enforcer_MkIV" if is_enforcer else "AuditorDroid"
    root = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(root)
    root.location = location

    # Shaders de titanio corporativo industrial gastado y chasis de hierro fundido
    armor_color = (0.28, 0.32, 0.35, 1.0) if is_enforcer else (0.82, 0.72, 0.32, 1.0) # Gris táctico vs Amarillo advertencia Astra
    mat_armor = create_weathered_pbr_material(
        f"{name}_Armor",
        color_clean=armor_color,
        color_grime=(0.12, 0.12, 0.12, 1.0),
        color_wear=(0.95, 0.95, 0.95, 1.0),
        metallic=0.88, roughness_clean=0.35, roughness_worn=0.55,
        grunge_scale=12.0, bump_strength=0.25
    )
    mat_chassis = create_weathered_pbr_material(
        f"{name}_Chassis",
        color_clean=(0.08, 0.08, 0.09, 1.0),
        color_grime=(0.03, 0.03, 0.03, 1.0),
        color_wear=(0.6, 0.6, 0.6, 1.0),
        metallic=0.92, roughness_clean=0.3, roughness_worn=0.45
    )
    visor_col = (0.95, 0.05, 0.05, 1.0) if is_enforcer else (1.0, 0.65, 0.05, 1.0)
    mat_visor = create_weathered_pbr_material(
        f"{name}_Visor",
        color_clean=visor_col, color_grime=visor_col, color_wear=visor_col,
        metallic=0.1, roughness_clean=0.1, roughness_worn=0.2,
        emissive_color=visor_col, emissive_strength=14.0
    )

    # 1. Torso acorazado con placas anguladas y ventiladores
    bpy.ops.mesh.primitive_cube_add(size=0.85 * scale, location=(0, 0, 1.35 * scale))
    chest = bpy.context.active_object
    chest.scale = (1.0, 0.75, 1.1)
    chest.name = f"{name}_Chest"
    chest.parent = root
    chest.data.materials.append(mat_armor)

    # Rejillas de ventilación y chasis interno
    bpy.ops.mesh.primitive_cube_add(size=0.65 * scale, location=(0, 0.32 * scale, 1.35 * scale))
    grille = bpy.context.active_object
    grille.scale = (0.8, 0.1, 0.8)
    grille.name = f"{name}_Grille"
    grille.parent = root
    grille.data.materials.append(mat_chassis)

    # 2. Cabeza cilíndrica blindada con sensor frontal CRT
    bpy.ops.mesh.primitive_cylinder_add(radius=0.24 * scale, depth=0.42 * scale, location=(0, 0.05 * scale, 2.05 * scale))
    head = bpy.context.active_object
    head.name = f"{name}_Head"
    head.parent = root
    head.data.materials.append(mat_armor)

    # Visor óptico horizontal de alta tecnología
    bpy.ops.mesh.primitive_cube_add(size=0.3 * scale, location=(0, 0.22 * scale, 2.05 * scale))
    sensor = bpy.context.active_object
    sensor.scale = (0.9, 0.2, 0.25)
    sensor.name = f"{name}_Sensor"
    sensor.parent = root
    sensor.data.materials.append(mat_visor)

    # Antena táctica lateral
    bpy.ops.mesh.primitive_cylinder_add(radius=0.02 * scale, depth=0.6 * scale, location=(0.22 * scale, -0.1 * scale, 2.35 * scale))
    antenna = bpy.context.active_object
    antenna.parent = root
    antenna.data.materials.append(mat_chassis)

    # 3. Extremidades mecánicas (Pistones hidráulicos y placas balísticas)
    for side in (-1, 1):
        # Piernas con actuadores dobles
        bpy.ops.mesh.primitive_cylinder_add(radius=0.12 * scale, depth=0.85 * scale, location=(side * 0.28 * scale, 0, 0.45 * scale))
        thigh = bpy.context.active_object
        thigh.parent = root
        thigh.data.materials.append(mat_armor)

        # Pie magnético de bota industrial
        bpy.ops.mesh.primitive_cube_add(size=0.32 * scale, location=(side * 0.28 * scale, 0.1 * scale, 0.1 * scale))
        foot = bpy.context.active_object
        foot.scale = (0.8, 1.3, 0.4)
        foot.parent = root
        foot.data.materials.append(mat_chassis)

        # Hombros acorazados
        bpy.ops.mesh.primitive_cube_add(size=0.35 * scale, location=(side * 0.65 * scale, 0, 1.8 * scale))
        shoulder = bpy.context.active_object
        shoulder.parent = root
        shoulder.data.materials.append(mat_armor)

        # Brazo
        bpy.ops.mesh.primitive_cylinder_add(radius=0.09 * scale, depth=0.75 * scale, location=(side * 0.72 * scale, 0.05 * scale, 1.3 * scale))
        arm = bpy.context.active_object
        arm.parent = root
        arm.data.materials.append(mat_chassis)

    # 4. Armamento: Porra de Electrochoque de alta tensión en mano derecha
    bpy.ops.mesh.primitive_cylinder_add(radius=0.045 * scale, depth=1.1 * scale, location=(0.75 * scale, 0.35 * scale, 0.95 * scale), rotation=(math.radians(30), 0, 0))
    baton = bpy.context.active_object
    baton.name = f"{name}_Baton"
    baton.parent = root
    baton.data.materials.append(mat_chassis)

    # Núcleo de bobina eléctrica en la porra
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.09 * scale, location=(0.75 * scale, 0.75 * scale, 1.45 * scale))
    baton_orb = bpy.context.active_object
    baton_orb.name = f"{name}_BatonElectrode"
    baton_orb.parent = root
    baton_orb.data.materials.append(mat_visor)

    # Si es Enforcer Mk-IV: Escudo balístico masivo de asalto en mano izquierda
    if is_enforcer:
        bpy.ops.mesh.primitive_cube_add(size=1.2 * scale, location=(-0.9 * scale, 0.4 * scale, 1.15 * scale))
        shield = bpy.context.active_object
        shield.scale = (0.1, 0.65, 1.3)
        shield.name = f"{name}_HeavyRiotShield"
        shield.parent = root
        shield.data.materials.append(mat_armor)

        # Mirilla blindada en el escudo
        bpy.ops.mesh.primitive_cube_add(size=0.3 * scale, location=(-0.9 * scale, 0.4 * scale, 1.65 * scale))
        shield_slit = bpy.context.active_object
        shield_slit.scale = (0.15, 0.7, 0.15)
        shield_slit.name = f"{name}_ShieldSlit"
        shield_slit.parent = root
        shield_slit.data.materials.append(mat_visor)

    return root

def build_vent_stalker(location, scale=1.0):
    """Acechador de Conductos (Vent Stalker): Depredador insectoide biomecánico de ductos"""
    root = bpy.data.objects.new("VentStalker", None)
    bpy.context.collection.objects.link(root)
    root.location = location

    mat_chitin = create_weathered_pbr_material(
        "VentStalker_Chitin",
        color_clean=(0.14, 0.16, 0.15, 1.0),
        color_grime=(0.04, 0.05, 0.04, 1.0),
        color_wear=(0.35, 0.4, 0.38, 1.0),
        metallic=0.5, roughness_clean=0.3, roughness_worn=0.6,
        grunge_scale=16.0, bump_strength=0.25
    )
    mat_biocable = create_weathered_pbr_material(
        "VentStalker_BioCable",
        color_clean=(0.35, 0.06, 0.12, 1.0),
        color_grime=(0.15, 0.02, 0.05, 1.0),
        color_wear=(0.6, 0.1, 0.2, 1.0),
        metallic=0.2, roughness_clean=0.4, roughness_worn=0.7
    )
    mat_eye = create_weathered_pbr_material(
        "VentStalker_EyeGreen",
        color_clean=(0.1, 1.0, 0.35, 1.0), color_grime=(0.1, 1.0, 0.35, 1.0), color_wear=(0.1, 1.0, 0.35, 1.0),
        metallic=0.0, roughness_clean=0.1, roughness_worn=0.1,
        emissive_color=(0.1, 1.0, 0.35, 1.0), emissive_strength=12.0
    )

    # 1. Abdomen y tórax segmentado con costillas expuestas
    for i in range(5):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=(0.42 - i*0.05) * scale, location=(0, -i*0.38 * scale, (1.25 - i*0.1) * scale))
        seg = bpy.context.active_object
        seg.scale = (0.85, 1.25, 0.7)
        seg.name = f"VentStalker_Segment_{i}"
        seg.parent = root
        seg.data.materials.append(mat_chitin)

        # Costillas laterales
        for side in (-1, 1):
            bpy.ops.mesh.primitive_cylinder_add(radius=0.03 * scale, depth=0.45 * scale, location=(side * 0.38 * scale, -i*0.38 * scale, (1.3 - i*0.1) * scale), rotation=(0, side * math.radians(65), 0))
            rib = bpy.context.active_object
            rib.parent = root
            rib.data.materials.append(mat_biocable)

    # 2. Cabeza biomecánica alargada estilo xenomorfo con mandíbulas
    bpy.ops.mesh.primitive_cone_add(radius1=0.32 * scale, depth=0.85 * scale, location=(0, 0.45 * scale, 1.4 * scale), rotation=(math.radians(85), 0, 0))
    head = bpy.context.active_object
    head.scale = (1.1, 0.65, 1.0)
    head.name = "VentStalker_Head"
    head.parent = root
    head.data.materials.append(mat_chitin)

    # 6 Ojos verdes bioluminiscentes en racimo
    for side in (-1, 1):
        for o in range(3):
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.045 * scale, location=(side * (0.12 + o*0.08) * scale, (0.55 + o*0.12) * scale, (1.42 + o*0.05) * scale))
            eye = bpy.context.active_object
            eye.name = f"VentStalker_Eye_{side}_{o}"
            eye.parent = root
            eye.data.materials.append(mat_eye)

    # 3. 4 Patas trepadoras de triple articulación
    for pair in range(2):
        y_p = (0.1 - pair * 0.6) * scale
        for side in (-1, 1):
            # Coxa
            bpy.ops.mesh.primitive_cylinder_add(radius=0.08 * scale, depth=0.8 * scale, location=(side * 0.6 * scale, y_p, 1.25 * scale), rotation=(0, side * math.radians(50), side * math.radians(20)))
            p1 = bpy.context.active_object
            p1.parent = root
            p1.data.materials.append(mat_chitin)

            # Tibia hacia abajo
            bpy.ops.mesh.primitive_cylinder_add(radius=0.05 * scale, depth=1.1 * scale, location=(side * 1.15 * scale, y_p + 0.1 * scale, 0.6 * scale), rotation=(0, -side * math.radians(20), 0))
            p2 = bpy.context.active_object
            p2.parent = root
            p2.data.materials.append(mat_biocable)

            # Garra afilada para enrejados
            bpy.ops.mesh.primitive_cone_add(radius1=0.04 * scale, depth=0.35 * scale, location=(side * 1.35 * scale, y_p + 0.15 * scale, 0.05 * scale), rotation=(math.radians(90), 0, side * math.radians(45)))
            hook = bpy.context.active_object
            hook.parent = root
            hook.data.materials.append(mat_chitin)

    return root

def build_hoarder_gremlin(location, scale=1.0):
    """Duende Chatarrero (Hoarder Gremlin) con mochila de herramientas robadas"""
    root = bpy.data.objects.new("HoarderGremlin", None)
    bpy.context.collection.objects.link(root)
    root.location = location

    mat_skin = create_weathered_pbr_material(
        "Gremlin_Skin",
        color_clean=(0.42, 0.36, 0.26, 1.0),
        color_grime=(0.18, 0.14, 0.08, 1.0),
        color_wear=(0.6, 0.52, 0.4, 1.0),
        metallic=0.05, roughness_clean=0.75, roughness_worn=0.9,
        grunge_scale=15.0, bump_strength=0.3
    )
    mat_sack = create_weathered_pbr_material(
        "Gremlin_LeatherSack",
        color_clean=(0.28, 0.22, 0.14, 1.0),
        color_grime=(0.08, 0.06, 0.04, 1.0),
        color_wear=(0.45, 0.35, 0.25, 1.0),
        metallic=0.15, roughness_clean=0.8, roughness_worn=0.95
    )
    mat_extinguisher_stolen = create_weathered_pbr_material(
        "Gremlin_StolenExtinguisher",
        color_clean=(0.85, 0.15, 0.08, 1.0),
        color_grime=(0.2, 0.04, 0.02, 1.0),
        color_wear=(0.95, 0.9, 0.85, 1.0),
        metallic=0.85, roughness_clean=0.35, roughness_worn=0.65
    )
    mat_eye = create_weathered_pbr_material(
        "Gremlin_EyeYellow",
        color_clean=(1.0, 0.85, 0.1, 1.0), color_grime=(1.0, 0.85, 0.1, 1.0), color_wear=(1.0, 0.85, 0.1, 1.0),
        metallic=0.0, roughness_clean=0.1, roughness_worn=0.1,
        emissive_color=(1.0, 0.85, 0.1, 1.0), emissive_strength=10.0
    )

    # 1. Cuerpo encorvado con joroba
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.38 * scale, location=(0, 0, 0.6 * scale))
    body = bpy.context.active_object
    body.scale = (0.85, 0.95, 1.15)
    body.name = "Gremlin_Body"
    body.parent = root
    body.data.materials.append(mat_skin)

    # 2. Cabeza gárgola con orejas de murciélago y ojos saltones
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3 * scale, location=(0, 0.25 * scale, 0.95 * scale))
    head = bpy.context.active_object
    head.name = "Gremlin_Head"
    head.parent = root
    head.data.materials.append(mat_skin)

    for side in (-1, 1):
        # Ojos saltones reflectantes
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1 * scale, location=(side * 0.15 * scale, 0.44 * scale, 1.02 * scale))
        eye = bpy.context.active_object
        eye.name = f"Gremlin_Eye_{side}"
        eye.parent = root
        eye.data.materials.append(mat_eye)

        # Orejas puntiagudas
        bpy.ops.mesh.primitive_cone_add(radius1=0.08 * scale, depth=0.42 * scale, location=(side * 0.35 * scale, 0.12 * scale, 1.18 * scale), rotation=(0, side * math.radians(60), 0))
        ear = bpy.context.active_object
        ear.parent = root
        ear.data.materials.append(mat_skin)

    # 3. Brazos largos y delgados ladrones
    for side in (-1, 1):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.055 * scale, depth=0.75 * scale, location=(side * 0.42 * scale, 0.15 * scale, 0.5 * scale), rotation=(math.radians(-35), side * math.radians(20), 0))
        arm = bpy.context.active_object
        arm.parent = root
        arm.data.materials.append(mat_skin)

    # 4. Saco de chatarra robada repleto de herramientas reconocibles
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.48 * scale, location=(0, -0.42 * scale, 0.8 * scale))
    sack = bpy.context.active_object
    sack.scale = (1.1, 0.9, 1.3)
    sack.name = "Gremlin_LootSack"
    sack.parent = root
    sack.data.materials.append(mat_sack)

    # Extintor robado asomando del saco
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08 * scale, depth=0.55 * scale, location=(0.15 * scale, -0.45 * scale, 1.35 * scale), rotation=(math.radians(25), math.radians(-15), 0))
    ext = bpy.context.active_object
    ext.name = "Gremlin_StolenExtinguisher"
    ext.parent = root
    ext.data.materials.append(mat_extinguisher_stolen)

    return root

def build_thermal_echo(location, scale=1.0):
    """Silueta de Eco Térmico: Entidad espectral translúcida a -40°C con escarcha"""
    root = bpy.data.objects.new("ThermalEcho", None)
    bpy.context.collection.objects.link(root)
    root.location = location

    mat_ghost = create_weathered_pbr_material(
        "ThermalEcho_Spectral",
        color_clean=(0.15, 0.75, 1.0, 0.4),
        color_grime=(0.05, 0.35, 0.8, 0.4),
        color_wear=(0.8, 0.95, 1.0, 0.4),
        metallic=0.0, roughness_clean=0.05, roughness_worn=0.15,
        emissive_color=(0.1, 0.8, 1.0, 1.0), emissive_strength=8.0,
        alpha=0.48
    )

    # Torso fantasmal etéreo
    bpy.ops.mesh.primitive_cylinder_add(radius=0.28 * scale, depth=1.2 * scale, location=(0, 0, 1.0 * scale))
    torso = bpy.context.active_object
    torso.scale = (0.85, 0.6, 1.0)
    torso.name = "ThermalEcho_Torso"
    torso.parent = root
    torso.data.materials.append(mat_ghost)

    # Cabeza flotante con rostro hueco
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.24 * scale, location=(0, 0, 1.8 * scale))
    head = bpy.context.active_object
    head.scale = (0.8, 0.9, 1.1)
    head.name = "ThermalEcho_Head"
    head.parent = root
    head.data.materials.append(mat_ghost)

    # Brazos vaporosos
    for side in (-1, 1):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.08 * scale, depth=0.9 * scale, location=(side * 0.48 * scale, 0, 1.1 * scale), rotation=(math.radians(15), side * math.radians(25), 0))
        arm = bpy.context.active_object
        arm.parent = root
        arm.data.materials.append(mat_ghost)

    # Nube de fragmentos de hielo y escarcha flotante a -40°C
    for i in range(8):
        ang = i * (math.pi / 4)
        bpy.ops.mesh.primitive_cone_add(radius1=0.04 * scale, depth=0.3 * scale, location=(math.cos(ang)*0.65 * scale, math.sin(ang)*0.65 * scale, (0.8 + math.sin(i*2)*0.5) * scale))
        frost = bpy.context.active_object
        frost.name = f"ThermalEcho_FrostShard_{i}"
        frost.parent = root
        frost.data.materials.append(mat_ghost)

    return root

def build_alien_pets(base_location=Vector((0.0, -2.6, 0))):
    """Mascotas Alienígenas detalladas por Tier"""
    root = bpy.data.objects.new("AlienPets_Collection", None)
    bpy.context.collection.objects.link(root)
    root.location = base_location

    # Tier 1: Glip-Glop Dócil (Esferoide de gelatina lila con ojitos)
    mat_glip = create_weathered_pbr_material(
        "GlipGlop_GelatinPBR",
        color_clean=(0.75, 0.35, 0.9, 0.85),
        color_grime=(0.4, 0.1, 0.6, 0.85),
        color_wear=(0.9, 0.6, 1.0, 0.85),
        metallic=0.0, roughness_clean=0.1, roughness_worn=0.2,
        emissive_color=(0.5, 0.1, 0.7, 1.0), emissive_strength=3.0, alpha=0.85
    )
    mat_eye_dark = create_weathered_pbr_material(
        "Pet_PupilDark",
        color_clean=(0.02, 0.02, 0.02, 1.0), color_grime=(0.02, 0.02, 0.02, 1.0), color_wear=(0.02, 0.02, 0.02, 1.0),
        metallic=0.0, roughness_clean=0.05, roughness_worn=0.1
    )

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.32, location=(-2.2, 0, 0.32))
    glip = bpy.context.active_object
    glip.name = "Pet_GlipGlop_Body"
    glip.scale = (1.0, 1.0, 0.8)
    glip.parent = root
    glip.data.materials.append(mat_glip)

    for side in (-1, 1):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.09, location=(-2.2 + side*0.14, 0.24, 0.38))
        geye = bpy.context.active_object
        geye.name = f"Pet_Glip_Eye_{side}"
        geye.parent = root
        geye.data.materials.append(mat_eye_dark)

    # Tier 2: Hurón Estelar Evasivo (Nebula Weasel - Cian fosfórico con cola sinuosa)
    mat_weasel = create_weathered_pbr_material(
        "NebulaWeasel_PBR",
        color_clean=(0.1, 0.75, 0.92, 1.0),
        color_grime=(0.04, 0.3, 0.5, 1.0),
        color_wear=(0.4, 0.9, 1.0, 1.0),
        metallic=0.2, roughness_clean=0.4, roughness_worn=0.6,
        emissive_color=(0.1, 0.7, 0.9, 1.0), emissive_strength=5.0
    )
    bpy.ops.mesh.primitive_cylinder_add(radius=0.14, depth=0.85, location=(0, 0, 0.28), rotation=(0, math.radians(90), 0))
    weasel_body = bpy.context.active_object
    weasel_body.name = "Pet_NebulaWeasel_Body"
    weasel_body.parent = root
    weasel_body.data.materials.append(mat_weasel)

    bpy.ops.mesh.primitive_cone_add(radius1=0.14, depth=0.38, location=(0.5, 0, 0.32), rotation=(0, math.radians(-90), 0))
    weasel_head = bpy.context.active_object
    weasel_head.name = "Pet_NebulaWeasel_Head"
    weasel_head.parent = root
    weasel_head.data.materials.append(mat_weasel)

    # Cola arqueada
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.55, location=(-0.55, 0, 0.45), rotation=(0, math.radians(45), 0))
    weasel_tail = bpy.context.active_object
    weasel_tail.name = "Pet_NebulaWeasel_Tail"
    weasel_tail.parent = root
    weasel_tail.data.materials.append(mat_weasel)

    # Tier 3: Cinderling Termófilo (Lagarto de plasma acorazado con espinas de fuego)
    mat_cinder = create_weathered_pbr_material(
        "Cinderling_PBR",
        color_clean=(1.0, 0.35, 0.05, 1.0),
        color_grime=(0.4, 0.08, 0.02, 1.0),
        color_wear=(1.0, 0.8, 0.2, 1.0),
        metallic=0.1, roughness_clean=0.3, roughness_worn=0.5,
        emissive_color=(1.0, 0.35, 0.05, 1.0), emissive_strength=12.0
    )
    mat_cinder_scale = create_weathered_pbr_material(
        "Cinderling_RockScales",
        color_clean=(0.08, 0.06, 0.05, 1.0),
        color_grime=(0.04, 0.03, 0.03, 1.0),
        color_wear=(0.25, 0.15, 0.1, 1.0),
        metallic=0.1, roughness_clean=0.85, roughness_worn=0.95
    )

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22, location=(2.2, 0, 0.26))
    cinder_body = bpy.context.active_object
    cinder_body.scale = (1.5, 0.85, 0.75)
    cinder_body.name = "Pet_Cinderling_Body"
    cinder_body.parent = root
    cinder_body.data.materials.append(mat_cinder)

    # Placas dorsales de roca
    for p in range(3):
        bpy.ops.mesh.primitive_cone_add(radius1=0.08, depth=0.22, location=(2.2 + (p-1)*0.2, 0, 0.45))
        spine = bpy.context.active_object
        spine.parent = root
        spine.data.materials.append(mat_cinder_scale)

    return root

# ==============================================================================
# CONFIGURACIÓN DE ILUMINACIÓN Y RENDERS MULTI-ÁNGULO
# ==============================================================================

def setup_lighting():
    # Suelo industrial metálico oscuro con cuadrícula de contención
    mat_floor = create_weathered_pbr_material(
        "Showcase_FloorPBR",
        color_clean=(0.05, 0.05, 0.06, 1.0),
        color_grime=(0.02, 0.02, 0.025, 1.0),
        color_wear=(0.2, 0.22, 0.25, 1.0),
        metallic=0.85, roughness_clean=0.35, roughness_worn=0.5,
        grunge_scale=18.0, bump_strength=0.15
    )
    bpy.ops.mesh.primitive_plane_add(size=35, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = "Showcase_Floor"
    floor.data.materials.append(mat_floor)

    # Luces clave cinematográficas
    light_data_main = bpy.data.lights.new(name="Light_MainKey", type='AREA')
    light_data_main.energy = 5500.0
    light_data_main.size = 14.0
    light_data_main.color = (0.95, 0.95, 1.0)
    light_obj_main = bpy.data.objects.new("Light_MainKey", light_data_main)
    bpy.context.collection.objects.link(light_obj_main)
    light_obj_main.location = (0, -8.5, 7.5)
    light_obj_main.rotation_euler = (math.radians(50), 0, 0)

    # Luz de contra azul cian frío
    light_data_rim = bpy.data.lights.new(name="Light_RimCyan", type='AREA')
    light_data_rim.energy = 3800.0
    light_data_rim.size = 16.0
    light_data_rim.color = (0.15, 0.7, 1.0)
    light_obj_rim = bpy.data.objects.new("Light_RimCyan", light_data_rim)
    bpy.context.collection.objects.link(light_obj_rim)
    light_obj_rim.location = (0, 8.5, 5.5)
    light_obj_rim.rotation_euler = (math.radians(-45), 0, math.radians(180))

    # Luz de relleno ámbar lateral
    light_data_warm = bpy.data.lights.new(name="Light_SideAmber", type='POINT')
    light_data_warm.energy = 2500.0
    light_data_warm.color = (1.0, 0.45, 0.08)
    light_obj_warm = bpy.data.objects.new("Light_SideAmber", light_data_warm)
    bpy.context.collection.objects.link(light_obj_warm)
    light_obj_warm.location = (-9.5, -3.5, 4.0)

def render_camera_view(name, location, rotation, output_path):
    scene = bpy.context.scene
    cam_data = bpy.data.cameras.new(name=name)
    cam_data.lens = 35
    cam_obj = bpy.data.objects.new(name, cam_data)
    bpy.context.collection.objects.link(cam_obj)
    cam_obj.location = location
    cam_obj.rotation_euler = rotation
    scene.camera = cam_obj

    scene.render.filepath = output_path
    bpy.ops.render.render(write_still=True)
    print(f">>> Renderizado [{name}] guardado en: {output_path}")

def main():
    print("==========================================================")
    print(">>> INICIANDO GENERADOR AVANZADO DE BESTIARIO Y ENTIDADES")
    print("==========================================================")
    reset_scene()

    # 1. Monstruos y Entidades regulares (Fila media)
    build_cinder_stalker(location=Vector((-5.8, 0, 0)), scale=1.0, is_alpha=False)
    build_auditor_droid(location=Vector((-2.8, 0, 0)), scale=1.0, is_enforcer=False)
    build_vent_stalker(location=Vector((0.0, 0, 0)), scale=1.0)
    build_hoarder_gremlin(location=Vector((2.8, 0, 0)), scale=1.0)
    build_thermal_echo(location=Vector((5.8, 0, 0)), scale=1.0)

    # 2. Jefes de Tier (Fila posterior imponente)
    build_cinder_stalker(location=Vector((-4.5, 3.8, 0)), scale=1.65, is_alpha=True)
    build_auditor_droid(location=Vector((3.5, 3.8, 0)), scale=1.45, is_enforcer=True)

    # 3. Mascotas Alienígenas por Tier (Fila frontal de detalle)
    build_alien_pets(base_location=Vector((0.0, -2.4, 0)))

    # Iluminación de estudio
    setup_lighting()

    # Guardar archivo .blend maestro
    blend_path = "F:/Dev/Game/Art/Blender/Bestiario_Entidades_Oficial.blend"
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f">>> Archivo .blend actualizado: {blend_path}")

    # Renders Cinematográficos
    # 1. Panorama General de toda la Horda
    render_camera_view(
        "Cam_FullPanorama",
        location=(0, -10.5, 3.6),
        rotation=(math.radians(78), 0, 0),
        output_path=f"{RENDERS_DIR}/Showcase_Bestiario_Full_Arsenal.png"
    )

    # 2. Primer Plano: Cinder Stalkers (Regular y Alfa)
    render_camera_view(
        "Cam_CinderStalkers",
        location=(-4.8, -5.5, 2.5),
        rotation=(math.radians(75), 0, math.radians(-10)),
        output_path=f"{RENDERS_DIR}/Showcase_Cinder_Stalkers_Closeup.png"
    )

    # 3. Primer Plano: Droides de Astra Corp (Auditor y Enforcer Mk-IV)
    render_camera_view(
        "Cam_Droids",
        location=(1.0, -5.5, 2.6),
        rotation=(math.radians(76), 0, math.radians(20)),
        output_path=f"{RENDERS_DIR}/Showcase_Robotic_Enforcers_Closeup.png"
    )

    # 4. Primer Plano: Criaturas y Mascotas (Vent Stalker, Gremlin, Eco y Mascotas)
    render_camera_view(
        "Cam_AliensAndPets",
        location=(1.5, -4.5, 1.8),
        rotation=(math.radians(80), 0, 0),
        output_path=f"{RENDERS_DIR}/Showcase_Aliens_And_Pets_Closeup.png"
    )

    print(">>> TODOS LOS RENDERS DEL BESTIARIO COMPLETADOS EXITOSAMENTE <<<")

if __name__ == "__main__":
    main()

# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Generador Cinematográfico de Bestiario, Jefes y Mascotas Alienígenas
# Blender 5.2 LTS - Modelado Detallado, Shaders PBR Desgastados Multicapa y Estudio de Iluminación

import bpy
import bmesh
import math
import os
import shutil
from mathutils import Vector, Euler

PROJECT_ROOT = r"F:\Dev\Game"
RENDERS_DIR = os.path.join(PROJECT_ROOT, "Art", "Renders")
ARTIFACT_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\b59ff04f-3c21-4ee5-94b0-8e8f899f8923"
os.makedirs(RENDERS_DIR, exist_ok=True)
os.makedirs(ARTIFACT_DIR, exist_ok=True)

R = math.radians

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if not bpy.data.scenes:
        bpy.data.scenes.new("Scene")
    scene = bpy.context.scene
    engine_names = [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items]
    scene.render.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in engine_names else 'BLENDER_EEVEE'
    scene.render.resolution_x = 2560
    scene.render.resolution_y = 1440
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    return scene

def apply_smooth_and_modifiers(obj, use_subdiv=False, subdiv_levels=1, use_bevel=True, bevel_width=0.015):
    if not obj or obj.type != 'MESH':
        return
    for p in obj.data.polygons:
        p.use_smooth = True
    if use_bevel:
        bev = obj.modifiers.new(name="Bevel", type='BEVEL')
        bev.width = bevel_width
        bev.segments = 2
        bev.limit_method = 'ANGLE'
        bev.angle_limit = R(35)
    if use_subdiv:
        sub = obj.modifiers.new(name="Subdivision", type='SUBSURF')
        sub.levels = subdiv_levels
        sub.render_levels = subdiv_levels

# Shader PBR Avanzado Multicapa (Base, Óxido/Mugre, Desgaste Metálico, Rugosidad y Relieve)
def create_weathered_pbr_material(name, 
                                  color_clean, 
                                  color_grime, 
                                  color_wear, 
                                  metallic, 
                                  roughness_clean, 
                                  roughness_worn, 
                                  grunge_scale=12.0, 
                                  bump_strength=0.22, 
                                  noise_detail=8.0,
                                  emissive_color=(0,0,0,1), 
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
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Metallic'].default_value = metallic

    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    mapping = nodes.new(type='ShaderNodeMapping')
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])

    noise_macro = nodes.new(type='ShaderNodeTexNoise')
    noise_macro.inputs['Scale'].default_value = grunge_scale
    noise_macro.inputs['Detail'].default_value = noise_detail
    noise_macro.inputs['Roughness'].default_value = 0.68
    links.new(mapping.outputs['Vector'], noise_macro.inputs['Vector'])

    ramp_color = nodes.new(type='ShaderNodeValToRGB')
    cr = ramp_color.color_ramp
    cr.elements[0].position = 0.20
    cr.elements[0].color = color_grime
    cr.elements[1].position = 0.65
    cr.elements[1].color = color_clean
    elem_wear = cr.elements.new(0.86)
    elem_wear.color = color_wear
    links.new(noise_macro.outputs['Fac'], ramp_color.inputs['Fac'])
    links.new(ramp_color.outputs['Color'], bsdf.inputs['Base Color'])

    ramp_rough = nodes.new(type='ShaderNodeValToRGB')
    cr_r = ramp_rough.color_ramp
    cr_r.elements[0].position = 0.20
    cr_r.elements[0].color = (roughness_worn, roughness_worn, roughness_worn, 1.0)
    cr_r.elements[1].position = 0.85
    cr_r.elements[1].color = (roughness_clean, roughness_clean, roughness_clean, 1.0)
    links.new(noise_macro.outputs['Fac'], ramp_rough.inputs['Fac'])
    links.new(ramp_rough.outputs['Color'], bsdf.inputs['Roughness'])

    if bump_strength > 0.0:
        bump = nodes.new(type='ShaderNodeBump')
        bump.inputs['Strength'].default_value = bump_strength
        bump.inputs['Distance'].default_value = 0.025
        links.new(noise_macro.outputs['Fac'], bump.inputs['Height'])
        links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

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

MAT_VOLCANIC_ROCK = None
MAT_MAGMA_GLOW = None
MAT_ROBOT_STEEL = None
MAT_ROBOT_DARK_TITANIUM = None
MAT_HAZARD_YELLOW = None
MAT_OPTIC_RED = None
MAT_CHITIN_ARMOR = None
MAT_BIOLUM_GREEN = None
MAT_THERMAL_GHOST = None
MAT_PET_SLIME = None
MAT_PET_FERRET_FUR = None

def init_materials():
    global MAT_VOLCANIC_ROCK, MAT_MAGMA_GLOW, MAT_ROBOT_STEEL, MAT_ROBOT_DARK_TITANIUM
    global MAT_HAZARD_YELLOW, MAT_OPTIC_RED, MAT_CHITIN_ARMOR, MAT_BIOLUM_GREEN
    global MAT_THERMAL_GHOST, MAT_PET_SLIME, MAT_PET_FERRET_FUR

    MAT_VOLCANIC_ROCK = create_weathered_pbr_material(
        "M_VolcanicRock",
        color_clean=(0.10, 0.09, 0.09, 1.0),
        color_grime=(0.04, 0.03, 0.03, 1.0),
        color_wear=(0.22, 0.20, 0.19, 1.0),
        metallic=0.1, roughness_clean=0.88, roughness_worn=0.98, grunge_scale=15.0, bump_strength=0.75
    )
    MAT_MAGMA_GLOW = create_weathered_pbr_material(
        "M_MagmaGlow",
        color_clean=(1.0, 0.35, 0.05, 1.0),
        color_grime=(0.8, 0.15, 0.02, 1.0),
        color_wear=(1.0, 0.8, 0.2, 1.0),
        metallic=0.0, roughness_clean=0.1, roughness_worn=0.2, bump_strength=0.1,
        emissive_color=(1.0, 0.45, 0.05, 1.0), emissive_strength=10.0
    )
    MAT_ROBOT_STEEL = create_weathered_pbr_material(
        "M_RobotSteel",
        color_clean=(0.25, 0.27, 0.30, 1.0),
        color_grime=(0.08, 0.08, 0.09, 1.0),
        color_wear=(0.60, 0.62, 0.65, 1.0),
        metallic=0.92, roughness_clean=0.30, roughness_worn=0.65, grunge_scale=16.0, bump_strength=0.22
    )
    MAT_ROBOT_DARK_TITANIUM = create_weathered_pbr_material(
        "M_DarkTitanium",
        color_clean=(0.12, 0.13, 0.14, 1.0),
        color_grime=(0.04, 0.04, 0.05, 1.0),
        color_wear=(0.35, 0.36, 0.38, 1.0),
        metallic=0.95, roughness_clean=0.28, roughness_worn=0.55, grunge_scale=14.0, bump_strength=0.18
    )
    MAT_HAZARD_YELLOW = create_weathered_pbr_material(
        "M_HazardYellow",
        color_clean=(0.85, 0.65, 0.05, 1.0),
        color_grime=(0.15, 0.10, 0.02, 1.0),
        color_wear=(0.40, 0.40, 0.42, 1.0),
        metallic=0.3, roughness_clean=0.35, roughness_worn=0.70, grunge_scale=12.0, bump_strength=0.25
    )
    MAT_OPTIC_RED = create_weathered_pbr_material(
        "M_OpticRed",
        color_clean=(1.0, 0.05, 0.05, 1.0),
        color_grime=(0.5, 0.0, 0.0, 1.0),
        color_wear=(1.0, 0.3, 0.3, 1.0),
        metallic=0.1, roughness_clean=0.08, roughness_worn=0.15, bump_strength=0.0,
        emissive_color=(1.0, 0.08, 0.08, 1.0), emissive_strength=12.0
    )
    MAT_CHITIN_ARMOR = create_weathered_pbr_material(
        "M_ChitinArmor",
        color_clean=(0.08, 0.12, 0.10, 1.0),
        color_grime=(0.02, 0.03, 0.03, 1.0),
        color_wear=(0.20, 0.28, 0.22, 1.0),
        metallic=0.4, roughness_clean=0.25, roughness_worn=0.60, grunge_scale=18.0, bump_strength=0.5
    )
    MAT_BIOLUM_GREEN = create_weathered_pbr_material(
        "M_BiolumGreen",
        color_clean=(0.15, 1.0, 0.35, 1.0),
        color_grime=(0.05, 0.4, 0.1, 1.0),
        color_wear=(0.6, 1.0, 0.7, 1.0),
        metallic=0.0, roughness_clean=0.1, roughness_worn=0.2, bump_strength=0.0,
        emissive_color=(0.15, 1.0, 0.35, 1.0), emissive_strength=8.0
    )
    MAT_THERMAL_GHOST = create_weathered_pbr_material(
        "M_ThermalGhost",
        color_clean=(0.2, 0.6, 1.0, 1.0),
        color_grime=(0.05, 0.15, 0.35, 1.0),
        color_wear=(0.8, 0.95, 1.0, 1.0),
        metallic=0.0, roughness_clean=0.1, roughness_worn=0.2, bump_strength=0.1,
        emissive_color=(0.3, 0.7, 1.0, 1.0), emissive_strength=6.0, alpha=0.55
    )
    MAT_PET_SLIME = create_weathered_pbr_material(
        "M_PetSlimeCyan",
        color_clean=(0.1, 0.85, 0.9, 1.0),
        color_grime=(0.05, 0.4, 0.5, 1.0),
        color_wear=(0.6, 0.95, 1.0, 1.0),
        metallic=0.05, roughness_clean=0.12, roughness_worn=0.25, bump_strength=0.15,
        emissive_color=(0.15, 0.85, 0.95, 1.0), emissive_strength=3.5, alpha=0.85
    )
    MAT_PET_FERRET_FUR = create_weathered_pbr_material(
        "M_PetFerretFur",
        color_clean=(0.75, 0.70, 0.65, 1.0),
        color_grime=(0.25, 0.22, 0.20, 1.0),
        color_wear=(0.90, 0.88, 0.85, 1.0),
        metallic=0.0, roughness_clean=0.92, roughness_worn=0.98, grunge_scale=25.0, bump_strength=0.6
    )

# ==============================================================================
# 1. ENTIDAD 1: CINDER STALKER (Acechador de Ceniza)
# ==============================================================================
def build_cinder_stalker(loc=Vector((-8.0, 0.0, 0.0)), scale=1.0):
    """Monstruo ígneo: Cuadrúpedo acechante, caparazón de basalto agrietado con magma activo"""
    # Torso principal alargado y arqueado
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.65 * scale, location=(loc.x, loc.y, loc.z + 1.1 * scale))
    body = bpy.context.active_object
    body.scale = (1.0, 1.7, 0.8)
    body.data.materials.append(MAT_VOLCANIC_ROCK)
    apply_smooth_and_modifiers(body, use_subdiv=True, subdiv_levels=1, use_bevel=False)

    # Costillas / placas de basalto dorsales agrietadas
    for i in range(4):
        y_off = (i - 1.5) * 0.45 * scale
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(loc.x, loc.y + y_off, loc.z + (1.45 - i * 0.05) * scale))
        plate = bpy.context.active_object
        plate.scale = (0.9 * scale, 0.25 * scale, 0.15 * scale)
        plate.rotation_euler = (R(15 - i * 5), 0, 0)
        plate.data.materials.append(MAT_VOLCANIC_ROCK)
        apply_smooth_and_modifiers(plate, use_bevel=True, bevel_width=0.02)

        # Grieta incandescente de magma entre las placas
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(loc.x, loc.y + y_off, loc.z + (1.38 - i * 0.05) * scale))
        magma_seam = bpy.context.active_object
        magma_seam.scale = (0.7 * scale, 0.08 * scale, 0.06 * scale)
        magma_seam.data.materials.append(MAT_MAGMA_GLOW)

    # Cuello extendido hacia adelante
    bpy.ops.mesh.primitive_cylinder_add(radius=0.3 * scale, depth=0.7 * scale, location=(loc.x, loc.y - 1.1 * scale, loc.z + 1.2 * scale), rotation=(R(50), 0, 0))
    neck = bpy.context.active_object
    neck.data.materials.append(MAT_VOLCANIC_ROCK)
    apply_smooth_and_modifiers(neck, use_bevel=True, bevel_width=0.02)

    # Cabeza reptiliana/insectoide puntiaguda
    bpy.ops.mesh.primitive_cone_add(radius1=0.38 * scale, depth=0.85 * scale, location=(loc.x, loc.y - 1.6 * scale, loc.z + 1.45 * scale), rotation=(R(-100), 0, 0))
    head = bpy.context.active_object
    head.scale = (0.8, 1.2, 0.6)
    head.data.materials.append(MAT_VOLCANIC_ROCK)
    apply_smooth_and_modifiers(head, use_bevel=True, bevel_width=0.02)

    # Ojos de ascua brillante incandescente
    for side in [-0.22, 0.22]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.07 * scale, location=(loc.x + side * scale, loc.y - 1.65 * scale, loc.z + 1.55 * scale))
        eye = bpy.context.active_object
        eye.data.materials.append(MAT_MAGMA_GLOW)

    # Fauces inferiores partidas con colmillos
    bpy.ops.mesh.primitive_cone_add(radius1=0.18 * scale, depth=0.55 * scale, location=(loc.x, loc.y - 1.55 * scale, loc.z + 1.25 * scale), rotation=(R(-80), 0, 0))
    jaw = bpy.context.active_object
    jaw.data.materials.append(MAT_VOLCANIC_ROCK)

    # 4 Extremidades cuadrúpedas acechantes con zarpas
    for is_front in [True, False]:
        y_leg = (-0.7 if is_front else 0.8) * scale
        z_leg_root = (1.1 if is_front else 1.2) * scale
        for x_leg in [-0.75, 0.75]:
            # Brazo superior / muslo
            bpy.ops.mesh.primitive_cylinder_add(radius=0.14 * scale, depth=0.8 * scale, location=(loc.x + x_leg * scale, loc.y + y_leg, loc.z + (z_leg_root - 0.35) * scale), rotation=(R(20 if is_front else -25), R(20 if x_leg > 0 else -20), 0))
            upper = bpy.context.active_object
            upper.data.materials.append(MAT_VOLCANIC_ROCK)
            apply_smooth_and_modifiers(upper, use_bevel=True, bevel_width=0.015)

            # Antebrazo / espinilla en ángulo inverso (digitígrado)
            bpy.ops.mesh.primitive_cylinder_add(radius=0.10 * scale, depth=0.85 * scale, location=(loc.x + (x_leg * 1.15) * scale, loc.y + (y_leg - 0.15 if is_front else y_leg + 0.15), loc.z + 0.4 * scale), rotation=(R(-30 if is_front else 35), 0, 0))
            lower = bpy.context.active_object
            lower.data.materials.append(MAT_VOLCANIC_ROCK)
            apply_smooth_and_modifiers(lower, use_bevel=True, bevel_width=0.01)

            # Garra de obsidiana
            bpy.ops.mesh.primitive_cone_add(radius1=0.12 * scale, depth=0.35 * scale, location=(loc.x + (x_leg * 1.15) * scale, loc.y + (y_leg - 0.4 if is_front else y_leg), loc.z + 0.05 * scale), rotation=(R(75), 0, 0))
            claw = bpy.context.active_object
            claw.data.materials.append(MAT_VOLCANIC_ROCK)

    # Cola segmentada con púa volcánica
    bpy.ops.mesh.primitive_cylinder_add(radius=0.16 * scale, depth=1.2 * scale, location=(loc.x, loc.y + 1.4 * scale, loc.z + 0.9 * scale), rotation=(R(-45), 0, 0))
    tail = bpy.context.active_object
    tail.data.materials.append(MAT_VOLCANIC_ROCK)
    apply_smooth_and_modifiers(tail, use_bevel=True, bevel_width=0.015)

    # Luz de magma emitida por la criatura
    light = bpy.data.lights.new(name=f"Light_Cinder_{loc.x}", type='POINT')
    light.energy = 320.0 * scale
    light.color = (1.0, 0.4, 0.05)
    light_obj = bpy.data.objects.new(name=f"Light_Cinder_Obj_{loc.x}", object_data=light)
    light_obj.location = (loc.x, loc.y - 0.5 * scale, loc.z + 1.2 * scale)
    bpy.context.collection.objects.link(light_obj)

# ==============================================================================
# 2. JEFE TIER 1: CINDER STALKER ALFA (Colosal, Cuernos de Basalto, Grietas Masivas)
# ==============================================================================
def build_cinder_stalker_alfa(loc=Vector((-5.0, 0.0, 0.0))):
    """Versión Alfa del Cinder Stalker: Escala 1.6x, cuernos gigantescos y pecho de magma desbordante"""
    build_cinder_stalker(loc, scale=1.55)

    # Cuernos colosales curvados hacia atrás en la cabeza
    for x_horn in [-0.55, 0.55]:
        bpy.ops.mesh.primitive_cone_add(radius1=0.22, depth=1.4, location=(loc.x + x_horn, loc.y - 2.4, loc.z + 2.8), rotation=(R(-55), R(-20 if x_horn < 0 else 20), 0))
        horn = bpy.context.active_object
        horn.data.materials.append(MAT_VOLCANIC_ROCK)
        apply_smooth_and_modifiers(horn, use_bevel=True, bevel_width=0.02)

    # Espinas dorsales masivas
    for i in range(3):
        y_spine = (i - 1.0) * 0.7
        bpy.ops.mesh.primitive_cone_add(radius1=0.25, depth=0.9, location=(loc.x, loc.y + y_spine, loc.z + 2.7), rotation=(R(-25), 0, 0))
        spine = bpy.context.active_object
        spine.data.materials.append(MAT_MAGMA_GLOW)
        apply_smooth_and_modifiers(spine, use_bevel=True, bevel_width=0.02)

# ==============================================================================
# 3. ENTIDAD 2: DROIDE AUDITOR (Seguridad Corporativa, Brazo Pinza, Óptica Roja)
# ==============================================================================
def build_auditor_droid(loc=Vector((-2.0, 0.0, 0.0))):
    """Droide Auditor: Chasis angular militar, torso blindado, sensor omnisciente y pinzas hidráulicas"""
    # Pelvis y articulación de cadera
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(loc.x, loc.y, loc.z + 0.9))
    pelvis = bpy.context.active_object
    pelvis.scale = (0.55, 0.35, 0.25)
    pelvis.data.materials.append(MAT_ROBOT_DARK_TITANIUM)
    apply_smooth_and_modifiers(pelvis, use_bevel=True, bevel_width=0.02)

    # Torso blindado octogonal con rejillas
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(loc.x, loc.y, loc.z + 1.45))
    torso = bpy.context.active_object
    torso.scale = (0.75, 0.50, 0.75)
    torso.data.materials.append(MAT_ROBOT_STEEL)
    apply_smooth_and_modifiers(torso, use_bevel=True, bevel_width=0.03)

    # Franja amarilla de peligro corporativo en el pecho
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(loc.x, loc.y - 0.26, loc.z + 1.5))
    stripe = bpy.context.active_object
    stripe.scale = (0.72, 0.03, 0.16)
    stripe.data.materials.append(MAT_HAZARD_YELLOW)

    # Cabeza sensora / Unidad óptica
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(loc.x, loc.y - 0.05, loc.z + 1.95))
    head = bpy.context.active_object
    head.scale = (0.42, 0.38, 0.26)
    head.data.materials.append(MAT_ROBOT_DARK_TITANIUM)
    apply_smooth_and_modifiers(head, use_bevel=True, bevel_width=0.02)

    # Ojo óptico central cilíndrico rojo intenso
    bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.15, location=(loc.x, loc.y - 0.24, loc.z + 1.95), rotation=(R(90), 0, 0))
    optic = bpy.context.active_object
    optic.data.materials.append(MAT_OPTIC_RED)

    # Antena de enlace de datos superior
    bpy.ops.mesh.primitive_cylinder_add(radius=0.018, depth=0.6, location=(loc.x + 0.15, loc.y + 0.1, loc.z + 2.35))
    ant = bpy.context.active_object
    ant.data.materials.append(MAT_ROBOT_STEEL)

    # Piernas mecánicas con pistones
    for x_leg in [-0.28, 0.28]:
        # Muslo con camisa de pistón
        bpy.ops.mesh.primitive_cylinder_add(radius=0.09, depth=0.55, location=(loc.x + x_leg, loc.y, loc.z + 0.6))
        thigh = bpy.context.active_object
        thigh.data.materials.append(MAT_ROBOT_DARK_TITANIUM)
        apply_smooth_and_modifiers(thigh, use_bevel=True, bevel_width=0.01)

        # Espinilla
        bpy.ops.mesh.primitive_cylinder_add(radius=0.075, depth=0.55, location=(loc.x + x_leg, loc.y, loc.z + 0.25))
        shin = bpy.context.active_object
        shin.data.materials.append(MAT_ROBOT_STEEL)
        apply_smooth_and_modifiers(shin, use_bevel=True, bevel_width=0.01)

        # Pie magnético estabilizador
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(loc.x + x_leg, loc.y - 0.08, loc.z + 0.04))
        foot = bpy.context.active_object
        foot.scale = (0.22, 0.38, 0.08)
        foot.data.materials.append(MAT_ROBOT_DARK_TITANIUM)
        apply_smooth_and_modifiers(foot, use_bevel=True, bevel_width=0.015)

    # Brazos con actuadores y pinzas industriales
    for x_arm in [-0.52, 0.52]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.6, location=(loc.x + x_arm, loc.y, loc.z + 1.35))
        upper_arm = bpy.context.active_object
        upper_arm.data.materials.append(MAT_ROBOT_DARK_TITANIUM)
        apply_smooth_and_modifiers(upper_arm, use_bevel=True, bevel_width=0.01)

        # Pinza de dos garras
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(loc.x + x_arm, loc.y - 0.15, loc.z + 0.95))
        claw = bpy.context.active_object
        claw.scale = (0.16, 0.28, 0.18)
        claw.data.materials.append(MAT_ROBOT_STEEL)
        apply_smooth_and_modifiers(claw, use_bevel=True, bevel_width=0.01)

    # Luz de la óptica roja
    light = bpy.data.lights.new(name=f"Light_Droid_{loc.x}", type='POINT')
    light.energy = 180.0
    light.color = (1.0, 0.1, 0.1)
    light_obj = bpy.data.objects.new(name=f"Light_Droid_Obj_{loc.x}", object_data=light)
    light_obj.location = (loc.x, loc.y - 0.4, loc.z + 1.95)
    bpy.context.collection.objects.link(light_obj)

# ==============================================================================
# 4. JEFE TIER 2: DROIDE ENFORCER MK-IV (Androide Antidisturbios con Escudo Pesado)
# ==============================================================================
def build_enforcer_mk4(loc=Vector((1.0, 0.0, 0.0))):
    """Droide Enforcer Mk-IV: Titán blindado 2.6m, escudo balístico de torre y cañón electromagnético"""
    # Chasis principal sobredimensionado
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(loc.x, loc.y, loc.z + 1.6))
    torso = bpy.context.active_object
    torso.scale = (1.1, 0.75, 1.1)
    torso.data.materials.append(MAT_ROBOT_DARK_TITANIUM)
    apply_smooth_and_modifiers(torso, use_bevel=True, bevel_width=0.04)

    # Hombreras blindadas masivas
    for x_sp in [-0.75, 0.75]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(loc.x + x_sp, loc.y, loc.z + 2.15))
        pauldron = bpy.context.active_object
        pauldron.scale = (0.55, 0.65, 0.45)
        pauldron.data.materials.append(MAT_ROBOT_STEEL)
        apply_smooth_and_modifiers(pauldron, use_bevel=True, bevel_width=0.03)

    # Cabeza blindada angular con visor estroboscópico de rejilla
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(loc.x, loc.y - 0.1, loc.z + 2.25))
    head = bpy.context.active_object
    head.scale = (0.5, 0.45, 0.35)
    head.data.materials.append(MAT_ROBOT_DARK_TITANIUM)
    apply_smooth_and_modifiers(head, use_bevel=True, bevel_width=0.02)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(loc.x, loc.y - 0.34, loc.z + 2.25))
    visor = bpy.context.active_object
    visor.scale = (0.42, 0.04, 0.12)
    visor.data.materials.append(MAT_OPTIC_RED)

    # Piernas colosales reforzadas
    for x_leg in [-0.42, 0.42]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=0.8, location=(loc.x + x_leg, loc.y, loc.z + 0.8))
        thigh = bpy.context.active_object
        thigh.data.materials.append(MAT_ROBOT_STEEL)
        apply_smooth_and_modifiers(thigh, use_bevel=True, bevel_width=0.02)

        bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.8, location=(loc.x + x_leg, loc.y, loc.z + 0.35))
        shin = bpy.context.active_object
        shin.data.materials.append(MAT_ROBOT_DARK_TITANIUM)
        apply_smooth_and_modifiers(shin, use_bevel=True, bevel_width=0.02)

        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(loc.x + x_leg, loc.y - 0.1, loc.z + 0.06))
        foot = bpy.context.active_object
        foot.scale = (0.35, 0.55, 0.12)
        foot.data.materials.append(MAT_ROBOT_STEEL)
        apply_smooth_and_modifiers(foot, use_bevel=True, bevel_width=0.02)

    # BRAZO IZQUIERDO: GRAN ESCUDO BALÍSTICO DE TORRE
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(loc.x - 0.95, loc.y - 0.45, loc.z + 1.25), rotation=(0, R(10), 0))
    shield = bpy.context.active_object
    shield.scale = (0.22, 1.1, 2.2)
    shield.data.materials.append(MAT_ROBOT_STEEL)
    apply_smooth_and_modifiers(shield, use_bevel=True, bevel_width=0.03)

    # Franja amarilla en el escudo
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(loc.x - 1.07, loc.y - 0.45, loc.z + 1.25))
    s_stripe = bpy.context.active_object
    s_stripe.scale = (0.02, 0.95, 0.3)
    s_stripe.data.materials.append(MAT_HAZARD_YELLOW)

    # BRAZO DERECHO: CAÑÓN ELECTROMAGNÉTICO PESADO
    bpy.ops.mesh.primitive_cylinder_add(radius=0.14, depth=1.6, location=(loc.x + 0.95, loc.y - 0.5, loc.z + 1.3), rotation=(R(90), 0, 0))
    cannon = bpy.context.active_object
    cannon.data.materials.append(MAT_ROBOT_DARK_TITANIUM)
    apply_smooth_and_modifiers(cannon, use_bevel=True, bevel_width=0.02)

    # Boca del cañón con bobinas
    bpy.ops.mesh.primitive_torus_add(major_radius=0.16, minor_radius=0.03, location=(loc.x + 0.95, loc.y - 1.1, loc.z + 1.3), rotation=(R(90), 0, 0))
    coil = bpy.context.active_object
    coil.data.materials.append(MAT_OPTIC_RED)

    # Luz del Enforcer
    light = bpy.data.lights.new(name="Light_Enforcer", type='POINT')
    light.energy = 450.0
    light.color = (1.0, 0.2, 0.1)
    light_obj = bpy.data.objects.new(name="Light_Enforcer_Obj", object_data=light)
    light_obj.location = (loc.x, loc.y - 0.8, loc.z + 2.3)
    bpy.context.collection.objects.link(light_obj)

# ==============================================================================
# 5. ENTIDAD 3: ACECHADOR DE CONDUCTOS (Duct Creeper - Ciempiés Blindado)
# ==============================================================================
def build_duct_creeper(loc=Vector((3.8, 0.0, 0.0))):
    """Criatura insectoide vermiforme: 7 segmentos blindados, 12 patas articuladas y sensores bioluminiscentes"""
    # 7 segmentos corporales arqueados
    for i in range(7):
        y_seg = (i - 3.0) * 0.38
        z_seg = 0.45 + math.sin(i * 0.5) * 0.15
        rad = 0.32 - abs(i - 3) * 0.025
        bpy.ops.mesh.primitive_uv_sphere_add(segments=14, ring_count=10, radius=rad, location=(loc.x, loc.y + y_seg, loc.z + z_seg))
        seg = bpy.context.active_object
        seg.scale = (1.2, 0.85, 0.75)
        seg.data.materials.append(MAT_CHITIN_ARMOR)
        apply_smooth_and_modifiers(seg, use_subdiv=True, subdiv_levels=1)

        # Patas articuladas en pares (excepto en cola final)
        if i < 6:
            for side in [-1, 1]:
                # Fémur levantado hacia arriba
                x_knee = loc.x + side * (rad + 0.45)
                z_knee = loc.z + z_seg + 0.35
                bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=0.55, location=((loc.x + side * rad + x_knee)/2, loc.y + y_seg, (loc.z + z_seg + z_knee)/2), rotation=(0, R(side * -55), 0))
                femur = bpy.context.active_object
                femur.data.materials.append(MAT_CHITIN_ARMOR)

                # Tibia clavada en el suelo
                bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.6, location=(x_knee + side * 0.15, loc.y + y_seg, z_knee * 0.5), rotation=(0, R(side * 35), 0))
                tibia = bpy.context.active_object
                tibia.data.materials.append(MAT_CHITIN_ARMOR)

    # Cabeza aplanada frontal con quelíceros
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.35, location=(loc.x, loc.y - 1.45, loc.z + 0.42))
    head = bpy.context.active_object
    head.scale = (1.1, 1.4, 0.6)
    head.data.materials.append(MAT_CHITIN_ARMOR)
    apply_smooth_and_modifiers(head, use_subdiv=True, subdiv_levels=1)

    # 4 Sensores oculares bioluminiscentes verdes
    for eye_pos in [(-0.16, -1.6, 0.48), (0.16, -1.6, 0.48), (-0.28, -1.5, 0.42), (0.28, -1.5, 0.42)]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.045, location=(loc.x + eye_pos[0], loc.y + eye_pos[1], loc.z + eye_pos[2]))
        eye = bpy.context.active_object
        eye.data.materials.append(MAT_BIOLUM_GREEN)

    # Luz bioluminiscente del acechador
    light = bpy.data.lights.new(name="Light_Creeper", type='POINT')
    light.energy = 160.0
    light.color = (0.2, 1.0, 0.4)
    light_obj = bpy.data.objects.new(name="Light_Creeper_Obj", object_data=light)
    light_obj.location = (loc.x, loc.y - 1.5, loc.z + 0.6)
    bpy.context.collection.objects.link(light_obj)

# ==============================================================================
# 6. ENTIDAD 4: DUENDE CHATARRERO (Scrap Goblin - Carroñero Furtivo con Mochila)
# ==============================================================================
def build_scrap_goblin(loc=Vector((6.5, 0.0, 0.0))):
    """Humanoide encorvado: Mochila gigante de chatarra con botellas de O2, máscara de gas improvisada"""
    # Cuerpo / pelvis encorvada
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.45, location=(loc.x, loc.y, loc.z + 0.75))
    torso = bpy.context.active_object
    torso.scale = (0.8, 0.7, 1.1)
    torso.data.materials.append(MAT_CHITIN_ARMOR)
    apply_smooth_and_modifiers(torso, use_subdiv=True, subdiv_levels=1)

    # Cabeza con máscara de respirador oxidada
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=(loc.x, loc.y - 0.35, loc.z + 1.1))
    head = bpy.context.active_object
    head.scale = (0.9, 1.1, 0.9)
    head.data.materials.append(MAT_ROBOT_DARK_TITANIUM)

    # Filtro cilíndrico de la máscara frontal
    bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.22, location=(loc.x, loc.y - 0.62, loc.z + 1.02), rotation=(R(90), 0, 0))
    filter_can = bpy.context.active_object
    filter_can.data.materials.append(MAT_HAZARD_YELLOW)

    # Lentes asimétricos brillantes
    for x_lens, r_lens in [(-0.12, 0.06), (0.12, 0.08)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=r_lens, depth=0.08, location=(loc.x + x_lens, loc.y - 0.58, loc.z + 1.18), rotation=(R(90), 0, 0))
        lens = bpy.context.active_object
        lens.data.materials.append(MAT_MAGMA_GLOW)

    # MOCHILA DE CHATARRA DESBORDANTE DORSAL
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(loc.x, loc.y + 0.45, loc.z + 0.95))
    pack = bpy.context.active_object
    pack.scale = (0.75, 0.6, 0.85)
    pack.data.materials.append(MAT_ROBOT_STEEL)
    apply_smooth_and_modifiers(pack, use_bevel=True, bevel_width=0.03)

    # Cilindros de O2 saqueados sobresaliendo de la mochila
    for x_cyl, rot in [(-0.25, R(15)), (0.25, R(-20))]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=0.7, location=(loc.x + x_cyl, loc.y + 0.55, loc.z + 1.45), rotation=(rot, 0, 0))
        cyl = bpy.context.active_object
        cyl.data.materials.append(MAT_HAZARD_YELLOW)

    # Piernas arqueadas agachadas
    for x_leg in [-0.25, 0.25]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.09, depth=0.55, location=(loc.x + x_leg, loc.y, loc.z + 0.35), rotation=(R(20), 0, 0))
        leg = bpy.context.active_object
        leg.data.materials.append(MAT_CHITIN_ARMOR)

    # Brazo con garfio magnético en la mano derecha
    bpy.ops.mesh.primitive_cylinder_add(radius=0.07, depth=0.6, location=(loc.x + 0.45, loc.y - 0.2, loc.z + 0.65), rotation=(R(-30), 0, 0))
    arm = bpy.context.active_object
    arm.data.materials.append(MAT_CHITIN_ARMOR)

    bpy.ops.mesh.primitive_cone_add(radius1=0.1, depth=0.25, location=(loc.x + 0.45, loc.y - 0.45, loc.z + 0.45), rotation=(R(90), 0, 0))
    hook = bpy.context.active_object
    hook.data.materials.append(MAT_ROBOT_STEEL)

# ==============================================================================
# 7. ENTIDAD 5: SILUETA DE ECO TÉRMICO (Espectro Translúcido de Vacío)
# ==============================================================================
def build_thermal_echo(loc=Vector((9.0, 0.0, 0.0))):
    """Anomalía espectral humanoide translúcida que distorsiona la visión y emite frío polar"""
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.38, location=(loc.x, loc.y, loc.z + 1.45))
    torso = bpy.context.active_object
    torso.scale = (0.7, 0.4, 1.4)
    torso.data.materials.append(MAT_THERMAL_GHOST)
    apply_smooth_and_modifiers(torso, use_subdiv=True, subdiv_levels=2)

    # Cabeza etérea sin rostro
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.24, location=(loc.x, loc.y, loc.z + 2.1))
    head = bpy.context.active_object
    head.data.materials.append(MAT_THERMAL_GHOST)
    apply_smooth_and_modifiers(head, use_subdiv=True, subdiv_levels=2)

    # Núcleo de anomalía en el pecho (foco de calor/frío cuántico)
    bpy.ops.mesh.primitive_ico_sphere_add(radius=0.14, location=(loc.x, loc.y - 0.05, loc.z + 1.5))
    core = bpy.context.active_object
    core.data.materials.append(MAT_THERMAL_GHOST)

    # Zarcillos flotantes inferiores (disolución en el aire)
    for i, x_tendril in enumerate([-0.2, 0.0, 0.2]):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.06 - i * 0.01, depth=0.9, location=(loc.x + x_tendril, loc.y, loc.z + 0.65), rotation=(R(10 - i * 10), 0, 0))
        t = bpy.context.active_object
        t.data.materials.append(MAT_THERMAL_GHOST)
        apply_smooth_and_modifiers(t, use_subdiv=True, subdiv_levels=1)

    # Luz azul espectral
    light = bpy.data.lights.new(name="Light_Echo", type='POINT')
    light.energy = 280.0
    light.color = (0.3, 0.75, 1.0)
    light_obj = bpy.data.objects.new(name="Light_Echo_Obj", object_data=light)
    light_obj.location = (loc.x, loc.y, loc.z + 1.6)
    bpy.context.collection.objects.link(light_obj)

# ==============================================================================
# 8. LAS 3 MASCOTAS ALIENÍGENAS (GLIP-GLOP, HURÓN ESTELAR, CINDERLING)
# ==============================================================================
def build_glip_glop(loc=Vector((-2.0, -3.2, 0.0))):
    """Mascota Tier 1: Ameba gelatinosa translúcida dócil con antenas bulbosas y ojos curiosos"""
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.42, location=(loc.x, loc.y, loc.z + 0.35))
    slime = bpy.context.active_object
    slime.scale = (1.2, 1.1, 0.85)
    slime.data.materials.append(MAT_PET_SLIME)
    apply_smooth_and_modifiers(slime, use_subdiv=True, subdiv_levels=2)

    # Dos antenas flexibles
    for side in [-0.18, 0.18]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.35, location=(loc.x + side, loc.y, loc.z + 0.75), rotation=(0, R(side * -30), 0))
        stem = bpy.context.active_object
        stem.data.materials.append(MAT_PET_SLIME)

        # Bulbo terminal bioluminiscente
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.065, location=(loc.x + side * 1.8, loc.y, loc.z + 0.92))
        bulb = bpy.context.active_object
        bulb.data.materials.append(MAT_PET_SLIME)

    # Grandes ojos negros con brillo curioso
    for side in [-0.14, 0.14]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.07, location=(loc.x + side, loc.y - 0.38, loc.z + 0.48))
        eye = bpy.context.active_object
        eye.data.materials.append(MAT_ROBOT_DARK_TITANIUM)

def build_space_ferret(loc=Vector((0.5, -3.2, 0.0))):
    """Mascota Tier 2: Hurón cósmico ágil, pelaje suave, orejas de radar parabólicas articuladas"""
    # Cuerpo sinuoso estilizado
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.25, location=(loc.x, loc.y, loc.z + 0.28))
    body = bpy.context.active_object
    body.scale = (0.75, 2.2, 0.85)
    body.data.materials.append(MAT_PET_FERRET_FUR)
    apply_smooth_and_modifiers(body, use_subdiv=True, subdiv_levels=2)

    # Cabeza curiosa levantada
    bpy.ops.mesh.primitive_cone_add(radius1=0.18, depth=0.45, location=(loc.x, loc.y - 0.65, loc.z + 0.45), rotation=(R(-80), 0, 0))
    head = bpy.context.active_object
    head.data.materials.append(MAT_PET_FERRET_FUR)
    apply_smooth_and_modifiers(head, use_subdiv=True, subdiv_levels=1)

    # Orejas parabólicas de radar
    for side in [-0.15, 0.15]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.03, location=(loc.x + side, loc.y - 0.5, loc.z + 0.68), rotation=(R(30), R(side * 35), 0))
        ear = bpy.context.active_object
        ear.scale = (1.0, 0.2, 1.4)
        ear.data.materials.append(MAT_PET_FERRET_FUR)

    # Cola larga plumosa arqueada
    bpy.ops.mesh.primitive_cylinder_add(radius=0.09, depth=0.9, location=(loc.x, loc.y + 0.8, loc.z + 0.48), rotation=(R(55), 0, 0))
    tail = bpy.context.active_object
    tail.data.materials.append(MAT_PET_FERRET_FUR)
    apply_smooth_and_modifiers(tail, use_subdiv=True, subdiv_levels=1)

def build_cinderling(loc=Vector((3.0, -3.2, 0.0))):
    """Mascota Tier 3: Cría elemental de basalto flotante con alas de plasma cian y ojos de ascua"""
    # Esfera de piedra agrietada
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.32, location=(loc.x, loc.y, loc.z + 0.5))
    rock = bpy.context.active_object
    rock.data.materials.append(MAT_VOLCANIC_ROCK)
    apply_smooth_and_modifiers(rock, use_subdiv=True, subdiv_levels=1)

    # Ojos de magma ardiente
    for side in [-0.11, 0.11]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.05, location=(loc.x + side, loc.y - 0.28, loc.z + 0.55))
        eye = bpy.context.active_object
        eye.data.materials.append(MAT_MAGMA_GLOW)

    # Pequeñas alas de plasma flotantes
    for side in [-0.35, 0.35]:
        bpy.ops.mesh.primitive_cone_add(radius1=0.12, depth=0.45, location=(loc.x + side, loc.y + 0.05, loc.z + 0.58), rotation=(0, R(side * 65), R(30)))
        wing = bpy.context.active_object
        wing.data.materials.append(MAT_MAGMA_GLOW)

    # Anillo de levitación de plasma en la base
    bpy.ops.mesh.primitive_torus_add(major_radius=0.25, minor_radius=0.03, location=(loc.x, loc.y, loc.z + 0.18))
    ring = bpy.context.active_object
    ring.data.materials.append(MAT_MAGMA_GLOW)

# ==============================================================================
# PIPELINE DE ESCENA, CÁMARAS Y RENDER
# ==============================================================================
def setup_camera(name, location, rotation_euler, lens=35):
    cam = bpy.data.cameras.new(name=name)
    cam.lens = lens
    cam_obj = bpy.data.objects.new(name=name, object_data=cam)
    cam_obj.location = location
    cam_obj.rotation_euler = rotation_euler
    bpy.context.collection.objects.link(cam_obj)
    return cam_obj

def render_and_save(scene, cam_obj, filepath):
    scene.camera = cam_obj
    scene.render.filepath = filepath
    print(f"[RENDER] Procesando {filepath} ...")
    bpy.ops.render.render(write_still=True)
    filename = os.path.basename(filepath)
    shutil.copy2(filepath, os.path.join(ARTIFACT_DIR, filename))
    print(f"[ARTEFACTO] Copiado con éxito {filename}")

def main():
    print("=== CONSTRUYENDO BESTIARIO CINEMÁTICO COMPLETO EN BLENDER 5.2 ===")
    scene = reset_scene()
    init_materials()

    # Suelo de exposición de estudio oscuro de sci-fi
    mat_floor = create_weathered_pbr_material(
        "M_StudioFloor",
        color_clean=(0.08, 0.08, 0.09, 1.0),
        color_grime=(0.03, 0.03, 0.03, 1.0),
        color_wear=(0.18, 0.18, 0.20, 1.0),
        metallic=0.8, roughness_clean=0.4, roughness_worn=0.7, grunge_scale=20.0, bump_strength=0.15
    )
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, -1.0, -0.1))
    floor = bpy.context.active_object
    floor.scale = (24.0, 12.0, 0.2)
    floor.data.materials.append(mat_floor)
    apply_smooth_and_modifiers(floor, use_bevel=True, bevel_width=0.02)

    # Luces de estudio (Key Light, Fill Light, Rim Light para resaltar siluetas)
    key_light = bpy.data.lights.new(name="Key_Light", type='SUN')
    key_light.energy = 1.2
    key_light.color = (1.0, 0.95, 0.9)
    key_obj = bpy.data.objects.new(name="Key_Light_Obj", object_data=key_light)
    key_obj.rotation_euler = (R(55), R(25), R(-40))
    bpy.context.collection.objects.link(key_obj)

    rim_light = bpy.data.lights.new(name="Rim_Light", type='SUN')
    rim_light.energy = 0.8
    rim_light.color = (0.4, 0.7, 1.0) # Toque azul de contorno
    rim_obj = bpy.data.objects.new(name="Rim_Light_Obj", object_data=rim_light)
    rim_obj.rotation_euler = (R(-60), R(-15), R(140))
    bpy.context.collection.objects.link(rim_obj)

    # 1. Monstruos y Amenazas
    print("Modelando Cinder Stalker...")
    build_cinder_stalker(Vector((-8.0, 0.0, 0.0)))

    print("Modelando Jefe Cinder Stalker Alfa...")
    build_cinder_stalker_alfa(Vector((-5.0, 0.0, 0.0)))

    print("Modelando Droide Auditor...")
    build_auditor_droid(Vector((-2.0, 0.0, 0.0)))

    print("Modelando Jefe Droide Enforcer Mk-IV...")
    build_enforcer_mk4(Vector((1.0, 0.0, 0.0)))

    print("Modelando Acechador de Conductos (Duct Creeper)...")
    build_duct_creeper(Vector((3.8, 0.0, 0.0)))

    print("Modelando Duende Chatarrero (Scrap Goblin)...")
    build_scrap_goblin(Vector((6.5, 0.0, 0.0)))

    print("Modelando Silueta de Eco Térmico...")
    build_thermal_echo(Vector((9.0, 0.0, 0.0)))

    # 2. Mascotas Alienígenas en primera fila
    print("Modelando Mascotas (Glip-Glop, Hurón Estelar, Cinderling)...")
    build_glip_glop(Vector((-2.0, -2.8, 0.0)))
    build_space_ferret(Vector((0.8, -2.8, 0.0)))
    build_cinderling(Vector((3.5, -2.8, 0.0)))

    # Guardar archivo .blend
    blend_path = "F:/Dev/Game/Art/Blender/Bestiario_Cinematico_Oficial.blend"
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[BLEND] Guardado {blend_path}")

    # Cámaras:
    # A) Gran Panorama Cinemático de Todo el Bestiario
    cam_all = setup_camera("Cam_Bestiario_Pano", Vector((0.5, -9.5, 4.2)), (R(68), 0.0, 0.0), lens=24)

    # B) Primer Plano Tríada Ígnea (Cinder Stalker & Alfa)
    cam_fire = setup_camera("Cam_Cinder_Closeup", Vector((-6.5, -4.8, 2.5)), (R(74), 0.0, 0.0), lens=38)

    # C) Primer Plano Androides y Jefes (Droide Auditor & Enforcer Mk-IV)
    cam_droid = setup_camera("Cam_Droids_Closeup", Vector((-0.5, -4.5, 2.3)), (R(74), 0.0, 0.0), lens=38)

    # D) Primer Plano Mascotas y Criaturas Furtivas (Glip-Glop, Hurón, Cinderling, Creeper, Goblin)
    cam_pets = setup_camera("Cam_Pets_Closeup", Vector((1.0, -4.5, 1.8)), (R(70), 0.0, 0.0), lens=32)

    # Renderizados
    render_and_save(scene, cam_all, os.path.join(RENDERS_DIR, "Showcase_Bestiario_Cinematico_Panorama.png"))
    render_and_save(scene, cam_fire, os.path.join(RENDERS_DIR, "Showcase_Bestiario_Cinder_Closeup.png"))
    render_and_save(scene, cam_droid, os.path.join(RENDERS_DIR, "Showcase_Bestiario_Droids_Closeup.png"))
    render_and_save(scene, cam_pets, os.path.join(RENDERS_DIR, "Showcase_Bestiario_Pets_Closeup.png"))

    print("=== TODOS LOS RENDERS DE BESTIARIO CINEMÁTICO COMPLETADOS EXITOSAMENTE ===")

if __name__ == "__main__":
    main()

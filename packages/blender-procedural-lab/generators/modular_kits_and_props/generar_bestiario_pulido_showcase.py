# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Generador Pulido de Alta Calidad: Bestiario, Jefes y Mascotas Alienígenas
# Blender 5.2 LTS - Shade Smooth, Bevels, Subdivs, Shaders PBR y Renders de Estudio

import bpy
import bmesh
import math
import os
from mathutils import Vector, Euler

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

def apply_smooth_and_modifiers(obj, use_subdiv=False, subdiv_levels=1, use_bevel=True, bevel_width=0.015):
    """Aplica suavizado de normales y modificadores de bisel o subdivisión para evitar polígonos planos"""
    if not obj or obj.type != 'MESH':
        return
    for p in obj.data.polygons:
        p.use_smooth = True
    
    if use_bevel:
        bev = obj.modifiers.new(name="Bevel", type='BEVEL')
        bev.width = bevel_width
        bev.segments = 2
        bev.limit_method = 'ANGLE'
        bev.angle_limit = math.radians(35)
    
    if use_subdiv:
        sub = obj.modifiers.new(name="Subdivision", type='SUBSURF')
        sub.levels = subdiv_levels
        sub.render_levels = subdiv_levels

def create_pbr_mat(name, base_color, metallic=0.1, roughness=0.5, bump_strength=0.15, emission_color=(0,0,0,1), emission_strength=0.0, alpha=1.0):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = base_color
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness

    # Textura de ruido procedural para micro-desgaste
    if bump_strength > 0.0 or emission_strength > 0.0:
        tex_coord = nodes.new('ShaderNodeTexCoord')
        mapping = nodes.new('ShaderNodeMapping')
        noise = nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value = 12.0
        noise.inputs['Detail'].default_value = 6.0
        noise.inputs['Roughness'].default_value = 0.65

        links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
        links.new(mapping.outputs['Vector'], noise.inputs['Vector'])

        if bump_strength > 0.0:
            bump = nodes.new('ShaderNodeBump')
            bump.inputs['Strength'].default_value = bump_strength
            bump.inputs['Distance'].default_value = 0.02
            links.new(noise.outputs['Fac'], bump.inputs['Height'])
            links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    if emission_strength > 0.0:
        if 'Emission Color' in bsdf.inputs:
            bsdf.inputs['Emission Color'].default_value = emission_color
            bsdf.inputs['Emission Strength'].default_value = emission_strength
        elif 'Emission' in bsdf.inputs:
            bsdf.inputs['Emission'].default_value = emission_color
            if 'Emission Strength' in bsdf.inputs:
                bsdf.inputs['Emission Strength'].default_value = emission_strength

    if alpha < 1.0:
        if 'Alpha' in bsdf.inputs:
            bsdf.inputs['Alpha'].default_value = alpha
        mat.blend_method = 'BLEND' if hasattr(mat, 'blend_method') else 'HASHED'

    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

# ==============================================================================
# 1. CINDER STALKER & ALFA (Roca volcánica y magma)
# ==============================================================================
def make_cinder_stalker(loc, scale=1.0, is_alpha=False):
    prefix = "CinderAlpha" if is_alpha else "CinderStalker"
    root = bpy.data.objects.new(prefix, None)
    bpy.context.collection.objects.link(root)
    root.location = loc

    mat_rock = create_pbr_mat(f"{prefix}_Rock", (0.04, 0.035, 0.035, 1.0), metallic=0.15, roughness=0.85, bump_strength=0.35)
    magma_c = (1.0, 0.1, 0.01, 1.0) if is_alpha else (1.0, 0.32, 0.02, 1.0)
    mat_magma = create_pbr_mat(f"{prefix}_Magma", magma_c, roughness=0.2, emission_color=magma_c, emission_strength=18.0 if is_alpha else 12.0)

    # Torso cónico musculoso de roca
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.55 * scale, depth=1.1 * scale, location=(0, 0, 1.25 * scale))
    torso = bpy.context.active_object
    torso.scale = (1.0, 0.75, 1.0)
    apply_smooth_and_modifiers(torso, use_subdiv=True, subdiv_levels=1)
    torso.parent = root
    torso.data.materials.append(mat_rock)

    # Pecho hendido con núcleo de magma ardiente
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.32 * scale, location=(0, 0.22 * scale, 1.35 * scale))
    core = bpy.context.active_object
    apply_smooth_and_modifiers(core, use_subdiv=False)
    core.parent = root
    core.data.materials.append(mat_magma)

    # Cuello y Cabeza con cresta
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.3 * scale, location=(0, 0.15 * scale, 1.95 * scale))
    head = bpy.context.active_object
    head.scale = (0.85, 1.2, 0.9)
    apply_smooth_and_modifiers(head, use_subdiv=True, subdiv_levels=1)
    head.parent = root
    head.data.materials.append(mat_rock)

    # Ojos y mandíbula de lava
    for side in (-1, 1):
        bpy.ops.mesh.primitive_cube_add(size=0.08 * scale, location=(side * 0.14 * scale, 0.42 * scale, 2.02 * scale))
        eye = bpy.context.active_object
        eye.scale = (1.2, 0.5, 0.4)
        apply_smooth_and_modifiers(eye)
        eye.parent = root
        eye.data.materials.append(mat_magma)

    # Crestas y cuernos de obsidiana
    num_spikes = 6 if is_alpha else 3
    for i in range(num_spikes):
        z_s = (1.5 + i * 0.18) * scale
        for side in (-1, 1):
            bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=(0.12 + i*0.02) * scale, depth=(0.6 + i*0.12) * scale, location=(side * (0.42 + i*0.08) * scale, -0.32 * scale, z_s), rotation=(math.radians(-40), side * math.radians(35), 0))
            spk = bpy.context.active_object
            apply_smooth_and_modifiers(spk, use_bevel=True)
            spk.parent = root
            spk.data.materials.append(mat_magma if i%2 == 1 else mat_rock)

    # Brazos con hombreras colosales y garras
    for side in (-1, 1):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.26 * scale, location=(side * 0.72 * scale, 0, 1.7 * scale))
        sh = bpy.context.active_object
        apply_smooth_and_modifiers(sh, use_subdiv=True)
        sh.parent = root
        sh.data.materials.append(mat_rock)

        bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.15 * scale, depth=0.7 * scale, location=(side * 0.95 * scale, 0.1 * scale, 1.3 * scale), rotation=(0, side * math.radians(25), 0))
        arm = bpy.context.active_object
        apply_smooth_and_modifiers(arm)
        arm.parent = root
        arm.data.materials.append(mat_rock)

        bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.13 * scale, depth=0.65 * scale, location=(side * 1.15 * scale, 0.3 * scale, 0.85 * scale), rotation=(math.radians(35), 0, side * math.radians(15)))
        forearm = bpy.context.active_object
        apply_smooth_and_modifiers(forearm)
        forearm.parent = root
        forearm.data.materials.append(mat_magma)

        for c in range(3):
            bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.05 * scale, depth=0.4 * scale, location=(side * (1.1 + c*0.1) * scale, 0.65 * scale, 0.55 * scale), rotation=(math.radians(70), 0, side * math.radians(15)))
            claw = bpy.context.active_object
            apply_smooth_and_modifiers(claw)
            claw.parent = root
            claw.data.materials.append(mat_rock)

    # Piernas de pilar de basalto
    for side in (-1, 1):
        bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.2 * scale, depth=0.85 * scale, location=(side * 0.32 * scale, 0, 0.45 * scale))
        leg = bpy.context.active_object
        apply_smooth_and_modifiers(leg)
        leg.parent = root
        leg.data.materials.append(mat_rock)

    return root

# ==============================================================================
# 2. DROIDE AUDITOR & ENFORCER MK-IV
# ==============================================================================
def make_auditor_droid(loc, scale=1.0, is_enforcer=False):
    prefix = "EnforcerMkIV" if is_enforcer else "AuditorDroid"
    root = bpy.data.objects.new(prefix, None)
    bpy.context.collection.objects.link(root)
    root.location = loc

    armor_c = (0.28, 0.32, 0.36, 1.0) if is_enforcer else (0.82, 0.72, 0.28, 1.0) # Gris táctico vs Amarillo Astra
    mat_armor = create_pbr_mat(f"{prefix}_Armor", armor_c, metallic=0.85, roughness=0.35, bump_strength=0.18)
    mat_dark = create_pbr_mat(f"{prefix}_Chassis", (0.08, 0.08, 0.09, 1.0), metallic=0.92, roughness=0.3)
    visor_c = (0.95, 0.05, 0.05, 1.0) if is_enforcer else (1.0, 0.65, 0.05, 1.0)
    mat_led = create_pbr_mat(f"{prefix}_LED", visor_c, roughness=0.1, emission_color=visor_c, emission_strength=14.0)

    # Pecho acorazado biselado
    bpy.ops.mesh.primitive_cube_add(size=0.75 * scale, location=(0, 0, 1.35 * scale))
    chest = bpy.context.active_object
    chest.scale = (1.0, 0.7, 1.1)
    apply_smooth_and_modifiers(chest, use_bevel=True, bevel_width=0.03)
    chest.parent = root
    chest.data.materials.append(mat_armor)

    # Placa de blindaje frontal y núcleo de energía
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.16 * scale, depth=0.15 * scale, location=(0, 0.3 * scale, 1.45 * scale), rotation=(math.radians(90), 0, 0))
    core_ring = bpy.context.active_object
    apply_smooth_and_modifiers(core_ring)
    core_ring.parent = root
    core_ring.data.materials.append(mat_dark)

    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.11 * scale, depth=0.16 * scale, location=(0, 0.3 * scale, 1.45 * scale), rotation=(math.radians(90), 0, 0))
    core_light = bpy.context.active_object
    apply_smooth_and_modifiers(core_light)
    core_light.parent = root
    core_light.data.materials.append(mat_led)

    # Cabeza estilizada con visor CRT panorámico
    bpy.ops.mesh.primitive_cube_add(size=0.38 * scale, location=(0, 0.05 * scale, 1.95 * scale))
    head = bpy.context.active_object
    head.scale = (0.9, 0.85, 0.8)
    apply_smooth_and_modifiers(head, use_bevel=True, bevel_width=0.02)
    head.parent = root
    head.data.materials.append(mat_armor)

    # Visor LED
    bpy.ops.mesh.primitive_cube_add(size=0.28 * scale, location=(0, 0.22 * scale, 1.95 * scale))
    visor = bpy.context.active_object
    visor.scale = (0.95, 0.15, 0.3)
    apply_smooth_and_modifiers(visor)
    visor.parent = root
    visor.data.materials.append(mat_led)

    # Antena táctica
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.018 * scale, depth=0.55 * scale, location=(0.2 * scale, -0.1 * scale, 2.25 * scale))
    ant = bpy.context.active_object
    apply_smooth_and_modifiers(ant)
    ant.parent = root
    ant.data.materials.append(mat_dark)

    # Hombros mecánicos y brazos
    for side in (-1, 1):
        bpy.ops.mesh.primitive_cube_add(size=0.32 * scale, location=(side * 0.58 * scale, 0, 1.7 * scale))
        sh = bpy.context.active_object
        apply_smooth_and_modifiers(sh, use_bevel=True, bevel_width=0.02)
        sh.parent = root
        sh.data.materials.append(mat_armor)

        bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.09 * scale, depth=0.75 * scale, location=(side * 0.65 * scale, 0.05 * scale, 1.25 * scale))
        arm = bpy.context.active_object
        apply_smooth_and_modifiers(arm)
        arm.parent = root
        arm.data.materials.append(mat_dark)

        # Piernas con pistones y botas magnéticas
        bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.11 * scale, depth=0.85 * scale, location=(side * 0.25 * scale, 0, 0.45 * scale))
        leg = bpy.context.active_object
        apply_smooth_and_modifiers(leg)
        leg.parent = root
        leg.data.materials.append(mat_armor)

        bpy.ops.mesh.primitive_cube_add(size=0.28 * scale, location=(side * 0.25 * scale, 0.08 * scale, 0.1 * scale))
        boot = bpy.context.active_object
        boot.scale = (0.85, 1.3, 0.45)
        apply_smooth_and_modifiers(boot, use_bevel=True)
        boot.parent = root
        boot.data.materials.append(mat_dark)

    # Porra de Electrochoque en mano derecha
    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.04 * scale, depth=1.05 * scale, location=(0.68 * scale, 0.3 * scale, 0.95 * scale), rotation=(math.radians(30), 0, 0))
    baton = bpy.context.active_object
    apply_smooth_and_modifiers(baton)
    baton.parent = root
    baton.data.materials.append(mat_dark)

    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.08 * scale, location=(0.68 * scale, 0.7 * scale, 1.45 * scale))
    tip = bpy.context.active_object
    apply_smooth_and_modifiers(tip)
    tip.parent = root
    tip.data.materials.append(mat_led)

    # Si es Enforcer: Escudo antidisturbios masivo
    if is_enforcer:
        bpy.ops.mesh.primitive_cube_add(size=1.1 * scale, location=(-0.85 * scale, 0.35 * scale, 1.15 * scale))
        shield = bpy.context.active_object
        shield.scale = (0.08, 0.6, 1.3)
        apply_smooth_and_modifiers(shield, use_bevel=True, bevel_width=0.02)
        shield.parent = root
        shield.data.materials.append(mat_armor)

        # Mirilla blindada
        bpy.ops.mesh.primitive_cube_add(size=0.25 * scale, location=(-0.85 * scale, 0.35 * scale, 1.65 * scale))
        slit = bpy.context.active_object
        slit.scale = (0.1, 0.65, 0.12)
        apply_smooth_and_modifiers(slit)
        slit.parent = root
        slit.data.materials.append(mat_led)

    return root

# ==============================================================================
# 3. VENT STALKER (Acechador de conductos)
# ==============================================================================
def make_vent_stalker(loc, scale=1.0):
    root = bpy.data.objects.new("VentStalker", None)
    bpy.context.collection.objects.link(root)
    root.location = loc

    mat_chitin = create_pbr_mat("VentStalker_Chitin", (0.12, 0.14, 0.13, 1.0), metallic=0.5, roughness=0.35, bump_strength=0.25)
    mat_cable = create_pbr_mat("VentStalker_BioCable", (0.35, 0.05, 0.1, 1.0), metallic=0.1, roughness=0.5)
    mat_eye = create_pbr_mat("VentStalker_EyeGreen", (0.1, 1.0, 0.35, 1.0), roughness=0.1, emission_color=(0.1, 1.0, 0.35, 1.0), emission_strength=12.0)

    # Tórax y abdomen segmentado
    for i in range(5):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=14, ring_count=10, radius=(0.4 - i*0.05) * scale, location=(0, -i*0.35 * scale, (1.2 - i*0.1) * scale))
        seg = bpy.context.active_object
        seg.scale = (0.85, 1.25, 0.7)
        apply_smooth_and_modifiers(seg, use_subdiv=True, subdiv_levels=1)
        seg.parent = root
        seg.data.materials.append(mat_chitin)

        for side in (-1, 1):
            bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.03 * scale, depth=0.45 * scale, location=(side * 0.35 * scale, -i*0.35 * scale, (1.25 - i*0.1) * scale), rotation=(0, side * math.radians(65), 0))
            rib = bpy.context.active_object
            apply_smooth_and_modifiers(rib)
            rib.parent = root
            rib.data.materials.append(mat_cable)

    # Cabeza aplanada estilo depredador
    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.28 * scale, depth=0.8 * scale, location=(0, 0.42 * scale, 1.35 * scale), rotation=(math.radians(85), 0, 0))
    head = bpy.context.active_object
    head.scale = (1.1, 0.65, 1.0)
    apply_smooth_and_modifiers(head, use_subdiv=True, subdiv_levels=1)
    head.parent = root
    head.data.materials.append(mat_chitin)

    # 6 Ojos verdes bioluminiscentes
    for side in (-1, 1):
        for o in range(3):
            bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=0.04 * scale, location=(side * (0.1 + o*0.07) * scale, (0.52 + o*0.1) * scale, (1.38 + o*0.04) * scale))
            eye = bpy.context.active_object
            apply_smooth_and_modifiers(eye)
            eye.parent = root
            eye.data.materials.append(mat_eye)

    # 4 Patas trepadoras de triple articulación
    for pair in range(2):
        y_p = (0.1 - pair * 0.55) * scale
        for side in (-1, 1):
            bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.07 * scale, depth=0.75 * scale, location=(side * 0.55 * scale, y_p, 1.2 * scale), rotation=(0, side * math.radians(50), side * math.radians(20)))
            p1 = bpy.context.active_object
            apply_smooth_and_modifiers(p1)
            p1.parent = root
            p1.data.materials.append(mat_chitin)

            bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.045 * scale, depth=1.05 * scale, location=(side * 1.05 * scale, y_p + 0.1 * scale, 0.55 * scale), rotation=(0, -side * math.radians(20), 0))
            p2 = bpy.context.active_object
            apply_smooth_and_modifiers(p2)
            p2.parent = root
            p2.data.materials.append(mat_cable)

            bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.035 * scale, depth=0.3 * scale, location=(side * 1.25 * scale, y_p + 0.15 * scale, 0.05 * scale), rotation=(math.radians(90), 0, side * math.radians(45)))
            hook = bpy.context.active_object
            apply_smooth_and_modifiers(hook)
            hook.parent = root
            hook.data.materials.append(mat_chitin)

    return root

# ==============================================================================
# 4. HOARDER GREMLIN (Duende Chatarrero)
# ==============================================================================
def make_hoarder_gremlin(loc, scale=1.0):
    root = bpy.data.objects.new("HoarderGremlin", None)
    bpy.context.collection.objects.link(root)
    root.location = loc

    mat_skin = create_pbr_mat("Gremlin_Skin", (0.42, 0.36, 0.26, 1.0), metallic=0.05, roughness=0.8, bump_strength=0.25)
    mat_sack = create_pbr_mat("Gremlin_Sack", (0.26, 0.2, 0.12, 1.0), metallic=0.15, roughness=0.9)
    mat_ext = create_pbr_mat("Gremlin_Ext", (0.85, 0.12, 0.06, 1.0), metallic=0.85, roughness=0.35)
    mat_eye = create_pbr_mat("Gremlin_EyeYellow", (1.0, 0.85, 0.1, 1.0), roughness=0.1, emission_color=(1.0, 0.85, 0.1, 1.0), emission_strength=10.0)

    # Torso encorvado
    bpy.ops.mesh.primitive_uv_sphere_add(segments=14, ring_count=10, radius=0.36 * scale, location=(0, 0, 0.58 * scale))
    body = bpy.context.active_object
    body.scale = (0.85, 0.95, 1.15)
    apply_smooth_and_modifiers(body, use_subdiv=True, subdiv_levels=1)
    body.parent = root
    body.data.materials.append(mat_skin)

    # Cabeza con ojos saltones y orejas
    bpy.ops.mesh.primitive_uv_sphere_add(segments=14, ring_count=10, radius=0.28 * scale, location=(0, 0.22 * scale, 0.92 * scale))
    head = bpy.context.active_object
    apply_smooth_and_modifiers(head, use_subdiv=True, subdiv_levels=1)
    head.parent = root
    head.data.materials.append(mat_skin)

    for side in (-1, 1):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=8, radius=0.09 * scale, location=(side * 0.14 * scale, 0.42 * scale, 0.98 * scale))
        eye = bpy.context.active_object
        apply_smooth_and_modifiers(eye)
        eye.parent = root
        eye.data.materials.append(mat_eye)

        bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.07 * scale, depth=0.38 * scale, location=(side * 0.32 * scale, 0.1 * scale, 1.15 * scale), rotation=(0, side * math.radians(60), 0))
        ear = bpy.context.active_object
        apply_smooth_and_modifiers(ear)
        ear.parent = root
        ear.data.materials.append(mat_skin)

    # Brazos largos ladrones
    for side in (-1, 1):
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.05 * scale, depth=0.72 * scale, location=(side * 0.38 * scale, 0.12 * scale, 0.48 * scale), rotation=(math.radians(-35), side * math.radians(20), 0))
        arm = bpy.context.active_object
        apply_smooth_and_modifiers(arm)
        arm.parent = root
        arm.data.materials.append(mat_skin)

    # Saco de chatarra con extintor robado
    bpy.ops.mesh.primitive_uv_sphere_add(segments=14, ring_count=10, radius=0.45 * scale, location=(0, -0.38 * scale, 0.78 * scale))
    sack = bpy.context.active_object
    sack.scale = (1.1, 0.9, 1.25)
    apply_smooth_and_modifiers(sack, use_subdiv=True, subdiv_levels=1)
    sack.parent = root
    sack.data.materials.append(mat_sack)

    bpy.ops.mesh.primitive_cylinder_add(vertices=10, radius=0.075 * scale, depth=0.52 * scale, location=(0.14 * scale, -0.42 * scale, 1.3 * scale), rotation=(math.radians(25), math.radians(-15), 0))
    ext = bpy.context.active_object
    apply_smooth_and_modifiers(ext)
    ext.parent = root
    ext.data.materials.append(mat_ext)

    return root

# ==============================================================================
# 5. THERMAL ECHO SILHOUETTE (Silueta espectral a -40°C)
# ==============================================================================
def make_thermal_echo(loc, scale=1.0):
    root = bpy.data.objects.new("ThermalEcho", None)
    bpy.context.collection.objects.link(root)
    root.location = loc

    mat_ghost = create_pbr_mat(
        "ThermalEcho_Spectral",
        (0.2, 0.75, 1.0, 0.45),
        metallic=0.0, roughness=0.1,
        emission_color=(0.1, 0.8, 1.0, 1.0), emission_strength=8.0,
        alpha=0.48
    )

    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.26 * scale, depth=1.15 * scale, location=(0, 0, 0.95 * scale))
    torso = bpy.context.active_object
    torso.scale = (0.85, 0.6, 1.0)
    apply_smooth_and_modifiers(torso, use_subdiv=True, subdiv_levels=1)
    torso.parent = root
    torso.data.materials.append(mat_ghost)

    bpy.ops.mesh.primitive_uv_sphere_add(segments=14, ring_count=10, radius=0.22 * scale, location=(0, 0, 1.75 * scale))
    head = bpy.context.active_object
    head.scale = (0.8, 0.9, 1.1)
    apply_smooth_and_modifiers(head, use_subdiv=True, subdiv_levels=1)
    head.parent = root
    head.data.materials.append(mat_ghost)

    for side in (-1, 1):
        bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.075 * scale, depth=0.85 * scale, location=(side * 0.45 * scale, 0, 1.05 * scale), rotation=(math.radians(15), side * math.radians(25), 0))
        arm = bpy.context.active_object
        apply_smooth_and_modifiers(arm)
        arm.parent = root
        arm.data.materials.append(mat_ghost)

    for i in range(8):
        ang = i * (math.pi / 4)
        bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.035 * scale, depth=0.28 * scale, location=(math.cos(ang)*0.6 * scale, math.sin(ang)*0.6 * scale, (0.8 + math.sin(i*2)*0.45) * scale))
        frost = bpy.context.active_object
        apply_smooth_and_modifiers(frost)
        frost.parent = root
        frost.data.materials.append(mat_ghost)

    return root

# ==============================================================================
# 6. MASCOTAS ALIENÍGENAS POR TIER
# ==============================================================================
def make_alien_pets(base_loc):
    root = bpy.data.objects.new("AlienPets_Collection", None)
    bpy.context.collection.objects.link(root)
    root.location = base_loc

    # Tier 1: Glip-Glop Dócil
    mat_glip = create_pbr_mat("GlipGlop_PBR", (0.75, 0.35, 0.9, 0.85), roughness=0.15, emission_color=(0.5, 0.1, 0.7, 1.0), emission_strength=3.0, alpha=0.85)
    mat_pupil = create_pbr_mat("Pet_Pupil", (0.02, 0.02, 0.02, 1.0), roughness=0.05)

    bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=12, radius=0.3, location=(-2.2, 0, 0.3))
    glip = bpy.context.active_object
    glip.scale = (1.0, 1.0, 0.8)
    apply_smooth_and_modifiers(glip, use_subdiv=True, subdiv_levels=1)
    glip.parent = root
    glip.data.materials.append(mat_glip)

    for side in (-1, 1):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=10, ring_count=8, radius=0.08, location=(-2.2 + side*0.13, 0.22, 0.36))
        geye = bpy.context.active_object
        apply_smooth_and_modifiers(geye)
        geye.parent = root
        geye.data.materials.append(mat_pupil)

    # Tier 2: Hurón Estelar Evasivo (Nebula Weasel)
    mat_weasel = create_pbr_mat("NebulaWeasel_PBR", (0.1, 0.75, 0.92, 1.0), roughness=0.4, emission_color=(0.1, 0.7, 0.9, 1.0), emission_strength=5.0)
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.13, depth=0.8, location=(0, 0, 0.26), rotation=(0, math.radians(90), 0))
    w_body = bpy.context.active_object
    apply_smooth_and_modifiers(w_body, use_subdiv=True)
    w_body.parent = root
    w_body.data.materials.append(mat_weasel)

    bpy.ops.mesh.primitive_cone_add(vertices=10, radius1=0.13, depth=0.35, location=(0.48, 0, 0.3), rotation=(0, math.radians(-90), 0))
    w_head = bpy.context.active_object
    apply_smooth_and_modifiers(w_head)
    w_head.parent = root
    w_head.data.materials.append(mat_weasel)

    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.07, depth=0.5, location=(-0.5, 0, 0.42), rotation=(0, math.radians(45), 0))
    w_tail = bpy.context.active_object
    apply_smooth_and_modifiers(w_tail)
    w_tail.parent = root
    w_tail.data.materials.append(mat_weasel)

    # Tier 3: Cinderling Termófilo
    mat_cinder = create_pbr_mat("Cinderling_PBR", (1.0, 0.35, 0.05, 1.0), roughness=0.3, emission_color=(1.0, 0.35, 0.05, 1.0), emission_strength=12.0)
    mat_cinder_rock = create_pbr_mat("Cinderling_Rock", (0.08, 0.06, 0.05, 1.0), roughness=0.85)

    bpy.ops.mesh.primitive_uv_sphere_add(segments=14, ring_count=10, radius=0.2, location=(2.2, 0, 0.25))
    c_body = bpy.context.active_object
    c_body.scale = (1.5, 0.85, 0.75)
    apply_smooth_and_modifiers(c_body, use_subdiv=True)
    c_body.parent = root
    c_body.data.materials.append(mat_cinder)

    for p in range(3):
        bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.07, depth=0.2, location=(2.2 + (p-1)*0.18, 0, 0.42))
        sp = bpy.context.active_object
        apply_smooth_and_modifiers(sp)
        sp.parent = root
        sp.data.materials.append(mat_cinder_rock)

    return root

# ==============================================================================
# CONFIGURACIÓN Y RENDERS
# ==============================================================================
def setup_lighting():
    mat_floor = create_pbr_mat("Floor_StudioPBR", (0.05, 0.05, 0.06, 1.0), metallic=0.85, roughness=0.4, bump_strength=0.1)
    bpy.ops.mesh.primitive_plane_add(size=35, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = "Showcase_Floor"
    floor.data.materials.append(mat_floor)

    # Luces clave cinematográficas
    light_data_main = bpy.data.lights.new(name="Light_MainKey", type='AREA')
    light_data_main.energy = 6000.0
    light_data_main.size = 14.0
    light_data_main.color = (0.95, 0.95, 1.0)
    light_obj_main = bpy.data.objects.new("Light_MainKey", light_data_main)
    bpy.context.collection.objects.link(light_obj_main)
    light_obj_main.location = (0, -8.5, 7.5)
    light_obj_main.rotation_euler = (math.radians(50), 0, 0)

    light_data_rim = bpy.data.lights.new(name="Light_RimCyan", type='AREA')
    light_data_rim.energy = 4200.0
    light_data_rim.size = 16.0
    light_data_rim.color = (0.15, 0.7, 1.0)
    light_obj_rim = bpy.data.objects.new("Light_RimCyan", light_data_rim)
    bpy.context.collection.objects.link(light_obj_rim)
    light_obj_rim.location = (0, 8.5, 5.5)
    light_obj_rim.rotation_euler = (math.radians(-45), 0, math.radians(180))

    light_data_warm = bpy.data.lights.new(name="Light_SideAmber", type='POINT')
    light_data_warm.energy = 2800.0
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
    print(f">>> Render [{name}] -> {output_path}")

def main():
    print("==========================================================")
    print(">>> INICIANDO GENERADOR PULIDO DE BESTIARIO Y ENTIDADES")
    print("==========================================================")
    reset_scene()

    # 1. Monstruos y Entidades regulares (Fila media)
    make_cinder_stalker(loc=Vector((-5.6, 0, 0)), scale=1.0, is_alpha=False)
    make_auditor_droid(loc=Vector((-2.7, 0, 0)), scale=1.0, is_enforcer=False)
    make_vent_stalker(loc=Vector((0.0, 0, 0)), scale=1.0)
    make_hoarder_gremlin(loc=Vector((2.7, 0, 0)), scale=1.0)
    make_thermal_echo(loc=Vector((5.6, 0, 0)), scale=1.0)

    # 2. Jefes de Tier (Fila posterior imponente)
    make_cinder_stalker(loc=Vector((-4.3, 3.6, 0)), scale=1.6, is_alpha=True)
    make_auditor_droid(loc=Vector((3.4, 3.6, 0)), scale=1.4, is_enforcer=True)

    # 3. Mascotas Alienígenas por Tier (Fila frontal de detalle)
    make_alien_pets(base_loc=Vector((0.0, -2.4, 0)))

    # Iluminación de estudio
    setup_lighting()

    # Guardar archivo .blend maestro
    blend_path = "F:/Dev/Game/Art/Blender/Bestiario_Entidades_Oficial.blend"
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)

    # Renders
    render_camera_view("Cam_FullPanorama", (0, -10.5, 3.6), (math.radians(78), 0, 0), f"{RENDERS_DIR}/Showcase_Bestiario_Full_Arsenal.png")
    render_camera_view("Cam_CinderStalkers", (-4.6, -5.2, 2.5), (math.radians(76), 0, math.radians(-10)), f"{RENDERS_DIR}/Showcase_Cinder_Stalkers_Closeup.png")
    render_camera_view("Cam_Droids", (0.9, -5.2, 2.6), (math.radians(76), 0, math.radians(20)), f"{RENDERS_DIR}/Showcase_Robotic_Enforcers_Closeup.png")
    render_camera_view("Cam_AliensAndPets", (1.4, -4.2, 1.8), (math.radians(80), 0, 0), f"{RENDERS_DIR}/Showcase_Aliens_And_Pets_Closeup.png")

    print(">>> GENERADOR PULIDO COMPLETADO CON ÉXITO <<<")

if __name__ == "__main__":
    main()

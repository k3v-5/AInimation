# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Generador Oficial 3D de Arquetipos de Mapas: Carguero Químico, Crucero de Lujo, Refinería de Plasma
# Blender 5.2 LTS - Arquitecturas Únicas, Texturas PBR Diferenciadas e Iluminación Cinematográfica

import bpy
import bmesh
import math
import os
import shutil
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
        bev.angle_limit = math.radians(35)
    if use_subdiv:
        sub = obj.modifiers.new(name="Subdivision", type='SUBSURF')
        sub.levels = subdiv_levels
        sub.render_levels = subdiv_levels

def create_pbr_mat(name, base_color, metallic=0.1, roughness=0.5, bump_strength=0.15, emission_color=(0,0,0,1), emission_strength=0.0, noise_scale=12.0):
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

    if bump_strength > 0.0:
        tex_coord = nodes.new('ShaderNodeTexCoord')
        mapping = nodes.new('ShaderNodeMapping')
        noise = nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value = noise_scale
        noise.inputs['Detail'].default_value = 5.0
        noise.inputs['Roughness'].default_value = 0.6

        links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
        links.new(mapping.outputs['Vector'], noise.inputs['Vector'])

        bump = nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value = bump_strength
        bump.inputs['Distance'].default_value = 0.03
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

    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

# ==============================================================================
# 1. ARQUETIPO: CARGUERO QUÍMICO (Industrial Pesado, Corrosión, Cerchas, Tuberías)
# ==============================================================================
def build_chemical_hauler(origin=Vector((-12.0, 0.0, 0.0))):
    mat_floor_grate = create_pbr_mat("M_Chem_FloorGrate", (0.12, 0.13, 0.14, 1.0), metallic=0.85, roughness=0.45, bump_strength=0.35, noise_scale=20.0)
    mat_wall_panels = create_pbr_mat("M_Chem_WallPanels", (0.28, 0.29, 0.30, 1.0), metallic=0.75, roughness=0.55, bump_strength=0.25, noise_scale=8.0)
    mat_truss = create_pbr_mat("M_Chem_Truss_Steel", (0.15, 0.16, 0.17, 1.0), metallic=0.9, roughness=0.35, bump_strength=0.2, noise_scale=15.0)
    mat_hazard_strip = create_pbr_mat("M_Chem_HazardYellow", (0.85, 0.65, 0.05, 1.0), metallic=0.2, roughness=0.4, bump_strength=0.15)
    mat_acid_pipe = create_pbr_mat("M_Chem_AcidPipe", (0.75, 0.60, 0.02, 1.0), metallic=0.3, roughness=0.35, bump_strength=0.25)
    mat_acid_goo = create_pbr_mat("M_Chem_AcidGoo", (0.1, 0.9, 0.15, 1.0), metallic=0.1, roughness=0.1, bump_strength=0.1, emission_color=(0.15, 1.0, 0.2, 1.0), emission_strength=2.5)
    mat_rust_tank = create_pbr_mat("M_Chem_RustTank", (0.35, 0.18, 0.10, 1.0), metallic=0.4, roughness=0.75, bump_strength=0.45, noise_scale=18.0)
    mat_warning_light = create_pbr_mat("M_Chem_WarningLight", (1.0, 0.4, 0.05, 1.0), metallic=0.0, roughness=0.1, emission_color=(1.0, 0.4, 0.05, 1.0), emission_strength=8.0)

    # Suelo industrial con canaleta de drenaje
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(origin.x - 1.6, origin.y, origin.z - 0.1))
    f1 = bpy.context.active_object
    f1.scale = (3.0, 8.0, 0.2)
    f1.data.materials.append(mat_floor_grate)
    apply_smooth_and_modifiers(f1, use_bevel=True, bevel_width=0.02)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(origin.x + 1.6, origin.y, origin.z - 0.1))
    f2 = bpy.context.active_object
    f2.scale = (3.0, 8.0, 0.2)
    f2.data.materials.append(mat_floor_grate)
    apply_smooth_and_modifiers(f2, use_bevel=True, bevel_width=0.02)

    # Canaleta con charco de ácido químico verde radioactivo
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(origin.x, origin.y, origin.z - 0.18))
    trench = bpy.context.active_object
    trench.scale = (0.6, 8.0, 0.1)
    trench.data.materials.append(mat_floor_grate)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(origin.x, origin.y, origin.z - 0.12))
    acid_pool = bpy.context.active_object
    acid_pool.scale = (0.55, 6.5, 0.02)
    acid_pool.data.materials.append(mat_acid_goo)

    # Pared trasera de mamparo con franjas de peligro
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(origin.x, origin.y + 4.0, origin.z + 2.0))
    back_wall = bpy.context.active_object
    back_wall.scale = (6.0, 0.3, 4.2)
    back_wall.data.materials.append(mat_wall_panels)
    apply_smooth_and_modifiers(back_wall, use_bevel=True, bevel_width=0.03)

    # Franja amarilla de peligro en mamparo
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(origin.x, origin.y + 3.82, origin.z + 1.2))
    hazard_bar = bpy.context.active_object
    hazard_bar.scale = (5.8, 0.05, 0.25)
    hazard_bar.data.materials.append(mat_hazard_strip)

    # Compuerta circular estanca de alta presión
    bpy.ops.mesh.primitive_cylinder_add(radius=1.2, depth=0.35, location=(origin.x, origin.y + 3.9, origin.z + 2.0), rotation=(math.radians(90), 0, 0))
    door_frame = bpy.context.active_object
    door_frame.data.materials.append(mat_truss)
    apply_smooth_and_modifiers(door_frame, use_bevel=True, bevel_width=0.02)

    bpy.ops.mesh.primitive_cylinder_add(radius=1.0, depth=0.2, location=(origin.x, origin.y + 3.85, origin.z + 2.0), rotation=(math.radians(90), 0, 0))
    door_panel = bpy.context.active_object
    door_panel.data.materials.append(mat_floor_grate)
    apply_smooth_and_modifiers(door_panel, use_bevel=True, bevel_width=0.01)

    # Volante de esclusa de presión manual
    bpy.ops.mesh.primitive_torus_add(major_radius=0.3, minor_radius=0.04, location=(origin.x, origin.y + 3.7, origin.z + 2.0), rotation=(math.radians(90), 0, 0))
    wheel = bpy.context.active_object
    wheel.data.materials.append(mat_hazard_strip)
    apply_smooth_and_modifiers(wheel, use_bevel=True, bevel_width=0.01)

    # Cerchas estructurales en I (Trusses) a lo largo del pasillo
    for y_pos in [-3.0, 0.0, 3.0]:
        # Pilar izquierdo
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(origin.x - 2.8, origin.y + y_pos, origin.z + 2.0))
        col_l = bpy.context.active_object
        col_l.scale = (0.25, 0.35, 4.0)
        col_l.data.materials.append(mat_truss)
        apply_smooth_and_modifiers(col_l, use_bevel=True, bevel_width=0.02)

        # Pilar derecho
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(origin.x + 2.8, origin.y + y_pos, origin.z + 2.0))
        col_r = bpy.context.active_object
        col_r.scale = (0.25, 0.35, 4.0)
        col_r.data.materials.append(mat_truss)
        apply_smooth_and_modifiers(col_r, use_bevel=True, bevel_width=0.02)

        # Viga superior transversal
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(origin.x, origin.y + y_pos, origin.z + 3.9))
        beam = bpy.context.active_object
        beam.scale = (5.8, 0.35, 0.25)
        beam.data.materials.append(mat_truss)
        apply_smooth_and_modifiers(beam, use_bevel=True, bevel_width=0.02)

    # Tuberías químicas aéreas y laterales
    for z_pipe, r_pipe in [(3.4, 0.12), (3.15, 0.08), (2.9, 0.09)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=r_pipe, depth=7.8, location=(origin.x - 2.4, origin.y, origin.z + z_pipe), rotation=(math.radians(90), 0, 0))
        pipe = bpy.context.active_object
        pipe.data.materials.append(mat_acid_pipe)
        apply_smooth_and_modifiers(pipe, use_bevel=True, bevel_width=0.01)

    # Tanque de almacenamiento químico oxidado a la derecha
    bpy.ops.mesh.primitive_cylinder_add(radius=0.7, depth=2.8, location=(origin.x + 2.1, origin.y - 1.5, origin.z + 1.4))
    chem_tank = bpy.context.active_object
    chem_tank.data.materials.append(mat_rust_tank)
    apply_smooth_and_modifiers(chem_tank, use_subdiv=True, subdiv_levels=1, use_bevel=True, bevel_width=0.02)

    # Anillos de refuerzo del tanque
    for z_ring in [0.6, 1.4, 2.2]:
        bpy.ops.mesh.primitive_torus_add(major_radius=0.72, minor_radius=0.035, location=(origin.x + 2.1, origin.y - 1.5, origin.z + z_ring))
        ring = bpy.context.active_object
        ring.data.materials.append(mat_truss)
        apply_smooth_and_modifiers(ring, use_bevel=True, bevel_width=0.01)

    # Luz de mamparo industrial ámbar
    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.15, location=(origin.x - 2.5, origin.y + 1.0, origin.z + 2.5), rotation=(0, math.radians(90), 0))
    bulkhead_lamp = bpy.context.active_object
    bulkhead_lamp.data.materials.append(mat_warning_light)

    light_chem = bpy.data.lights.new(name="Light_Chem_Warning", type='POINT')
    light_chem.energy = 350.0
    light_chem.color = (1.0, 0.45, 0.08)
    light_chem_obj = bpy.data.objects.new(name="Light_Chem_Obj", object_data=light_chem)
    light_chem_obj.location = (origin.x - 2.2, origin.y + 1.0, origin.z + 2.5)
    bpy.context.collection.objects.link(light_chem_obj)

    # Resplandor verde ácido tenue desde el canal de drenaje
    light_acid = bpy.data.lights.new(name="Light_Acid_Glow", type='POINT')
    light_acid.energy = 80.0
    light_acid.color = (0.2, 1.0, 0.3)
    light_acid_obj = bpy.data.objects.new(name="Light_Acid_Obj", object_data=light_acid)
    light_acid_obj.location = (origin.x, origin.y, origin.z + 0.3)
    bpy.context.collection.objects.link(light_acid_obj)

# ==============================================================================
# 2. ARQUETIPO: CRUCERO DE LUJO (Art-Déco, Caoba Espacial, Molduras Doradas, Moqueta)
# ==============================================================================
def build_luxury_starliner(origin=Vector((0.0, 0.0, 0.0))):
    mat_wood = create_pbr_mat("M_Lux_MahoganyWood", (0.15, 0.06, 0.03, 1.0), metallic=0.05, roughness=0.28, bump_strength=0.18, noise_scale=25.0)
    mat_gold = create_pbr_mat("M_Lux_BrushedGold", (0.88, 0.72, 0.28, 1.0), metallic=0.92, roughness=0.25, bump_strength=0.08)
    mat_carpet = create_pbr_mat("M_Lux_VelvetCarpet", (0.32, 0.04, 0.08, 1.0), metallic=0.0, roughness=0.88, bump_strength=0.35, noise_scale=30.0)
    mat_marble = create_pbr_mat("M_Lux_WhiteMarble", (0.88, 0.88, 0.90, 1.0), metallic=0.1, roughness=0.12, bump_strength=0.08, noise_scale=6.0)
    mat_glass = create_pbr_mat("M_Lux_PanorGlass", (0.05, 0.12, 0.20, 1.0), metallic=0.15, roughness=0.05, bump_strength=0.0)
    mat_warm_glow = create_pbr_mat("M_Lux_WarmLightBar", (1.0, 0.92, 0.75, 1.0), metallic=0.0, roughness=0.1, emission_color=(1.0, 0.90, 0.70, 1.0), emission_strength=5.0)
    mat_space_bg = create_pbr_mat("M_Lux_DeepSpace", (0.01, 0.02, 0.05, 1.0), metallic=0.0, roughness=0.9, emission_color=(0.1, 0.2, 0.6, 1.0), emission_strength=0.5)

    # Suelo con Moqueta Burdeos y Bordura Dorada
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(origin.x, origin.y, origin.z - 0.1))
    floor_carpet = bpy.context.active_object
    floor_carpet.scale = (5.6, 7.6, 0.2)
    floor_carpet.data.materials.append(mat_carpet)
    apply_smooth_and_modifiers(floor_carpet, use_bevel=True, bevel_width=0.02)

    # Zócalos y Cenefas Doradas en los Bordes del Suelo
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(origin.x - 2.8, origin.y, origin.z + 0.05))
    skirt_l = bpy.context.active_object
    skirt_l.scale = (0.08, 7.8, 0.12)
    skirt_l.data.materials.append(mat_gold)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(origin.x + 2.8, origin.y, origin.z + 0.05))
    skirt_r = bpy.context.active_object
    skirt_r.scale = (0.08, 7.8, 0.12)
    skirt_r.data.materials.append(mat_gold)

    # Pared Trasera: Boiserie de Caoba Espacial con Gran Ventanal Panorámico Art-Déco
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(origin.x - 2.0, origin.y + 4.0, origin.z + 2.0))
    wall_l = bpy.context.active_object
    wall_l.scale = (1.8, 0.3, 4.2)
    wall_l.data.materials.append(mat_wood)
    apply_smooth_and_modifiers(wall_l, use_bevel=True, bevel_width=0.02)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(origin.x + 2.0, origin.y + 4.0, origin.z + 2.0))
    wall_r = bpy.context.active_object
    wall_r.scale = (1.8, 0.3, 4.2)
    wall_r.data.materials.append(mat_wood)
    apply_smooth_and_modifiers(wall_r, use_bevel=True, bevel_width=0.02)

    # Marco de Ventanal Panorámico Dorado con Arco Art-Déco
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(origin.x, origin.y + 4.0, origin.z + 2.1))
    window_frame = bpy.context.active_object
    window_frame.scale = (2.6, 0.25, 2.8)
    window_frame.data.materials.append(mat_gold)
    apply_smooth_and_modifiers(window_frame, use_bevel=True, bevel_width=0.03)

    # Cristal Panorámico
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(origin.x, origin.y + 4.05, origin.z + 2.1))
    glass_pane = bpy.context.active_object
    glass_pane.scale = (2.3, 0.05, 2.5)
    glass_pane.data.materials.append(mat_glass)

    # Telón de fondo espacial (estrellas/nebulosa tras el cristal)
    bpy.ops.mesh.primitive_plane_add(size=4.0, location=(origin.x, origin.y + 4.8, origin.z + 2.1), rotation=(math.radians(90), 0, 0))
    nebula_bg = bpy.context.active_object
    nebula_bg.scale = (1.5, 1.2, 1.0)
    nebula_bg.data.materials.append(mat_space_bg)

    # Listones y Molduras Geométricas Art-Déco en las Paredes de Madera
    for x_flute in [-2.5, -2.1, -1.7, 1.7, 2.1, 2.5]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(origin.x + x_flute, origin.y + 3.82, origin.z + 2.0))
        flute = bpy.context.active_object
        flute.scale = (0.06, 0.04, 3.8)
        flute.data.materials.append(mat_gold)

    # Techo con Cornisa Escalonada Dorada e Iluminación Indirecta Cálida
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(origin.x, origin.y, origin.z + 4.1))
    ceiling = bpy.context.active_object
    ceiling.scale = (5.8, 8.0, 0.2)
    ceiling.data.materials.append(mat_wood)

    # Tiras de Luz Indirecta Cálida en el Techo
    for y_light in [-2.0, 0.5, 3.0]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(origin.x, origin.y + y_light, origin.z + 3.96))
        light_strip = bpy.context.active_object
        light_strip.scale = (4.0, 0.15, 0.05)
        light_strip.data.materials.append(mat_warm_glow)

    # Mesa Baja de Cóctel de Mármol y Dorado en el Pasillo
    bpy.ops.mesh.primitive_cylinder_add(radius=0.75, depth=0.08, location=(origin.x - 1.5, origin.y - 1.2, origin.z + 0.65))
    table_top = bpy.context.active_object
    table_top.data.materials.append(mat_marble)
    apply_smooth_and_modifiers(table_top, use_bevel=True, bevel_width=0.015)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.6, location=(origin.x - 1.5, origin.y - 1.2, origin.z + 0.3))
    table_leg = bpy.context.active_object
    table_leg.data.materials.append(mat_gold)
    apply_smooth_and_modifiers(table_leg, use_bevel=True, bevel_width=0.01)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=0.04, location=(origin.x - 1.5, origin.y - 1.2, origin.z + 0.03))
    table_base = bpy.context.active_object
    table_base.data.materials.append(mat_gold)

    # Sofá Curvo de Terciopelo Burdeos con Detalles Dorados
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(origin.x + 1.6, origin.y - 1.0, origin.z + 0.45))
    lounge_seat = bpy.context.active_object
    lounge_seat.scale = (1.4, 1.8, 0.4)
    lounge_seat.data.materials.append(mat_carpet)
    apply_smooth_and_modifiers(lounge_seat, use_subdiv=True, subdiv_levels=1, use_bevel=True, bevel_width=0.04)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(origin.x + 2.2, origin.y - 1.0, origin.z + 0.9))
    lounge_back = bpy.context.active_object
    lounge_back.scale = (0.25, 1.8, 0.7)
    lounge_back.data.materials.append(mat_wood)
    apply_smooth_and_modifiers(lounge_back, use_bevel=True, bevel_width=0.03)

    # Lámpara Art-Déco de Pie Cálida
    bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=2.0, location=(origin.x - 2.2, origin.y + 2.0, origin.z + 1.0))
    lamp_pole = bpy.context.active_object
    lamp_pole.data.materials.append(mat_gold)

    bpy.ops.mesh.primitive_cone_add(radius1=0.35, radius2=0.15, depth=0.35, location=(origin.x - 2.2, origin.y + 2.0, origin.z + 2.05))
    lamp_shade = bpy.context.active_object
    lamp_shade.data.materials.append(mat_warm_glow)

    # Iluminación de Estudio Cálida de Lujo
    light_lux = bpy.data.lights.new(name="Light_Lux_Lounge", type='POINT')
    light_lux.energy = 450.0
    light_lux.color = (1.0, 0.88, 0.72) # Cálido champagne
    light_lux_obj = bpy.data.objects.new(name="Light_Lux_Obj", object_data=light_lux)
    light_lux_obj.location = (origin.x - 0.5, origin.y, origin.z + 2.8)
    bpy.context.collection.objects.link(light_lux_obj)

    # Luz de Acercamiento del Ventanal Estelar (Frío sutil)
    light_star = bpy.data.lights.new(name="Light_Lux_Star", type='POINT')
    light_star.energy = 180.0
    light_star.color = (0.4, 0.65, 1.0)
    light_star_obj = bpy.data.objects.new(name="Light_Lux_Star_Obj", object_data=light_star)
    light_star_obj.location = (origin.x, origin.y + 3.5, origin.z + 2.2)
    bpy.context.collection.objects.link(light_star_obj)

# ==============================================================================
# 3. ARQUETIPO: REFINERÍA DE PLASMA / ESTACIÓN MINERA (Roca Asteroide, Titanio, Plasma)
# ==============================================================================
def build_plasma_refinery(origin=Vector((12.0, 0.0, 0.0))):
    mat_asteroid_rock = create_pbr_mat("M_Mine_AsteroidBasalt", (0.08, 0.08, 0.09, 1.0), metallic=0.05, roughness=0.95, bump_strength=0.75, noise_scale=14.0)
    mat_titanium = create_pbr_mat("M_Mine_DarkTitanium", (0.16, 0.17, 0.18, 1.0), metallic=0.92, roughness=0.38, bump_strength=0.2, noise_scale=10.0)
    mat_walkway_grate = create_pbr_mat("M_Mine_WalkwayGrate", (0.11, 0.12, 0.13, 1.0), metallic=0.88, roughness=0.45, bump_strength=0.4, noise_scale=22.0)
    mat_plasma_core = create_pbr_mat("M_Mine_PlasmaCore", (0.1, 0.75, 1.0, 1.0), metallic=0.0, roughness=0.05, emission_color=(0.15, 0.85, 1.0, 1.0), emission_strength=14.0)
    mat_coil_copper = create_pbr_mat("M_Mine_CoilCopper", (0.65, 0.35, 0.15, 1.0), metallic=0.85, roughness=0.3, bump_strength=0.15)
    mat_cryo_ice = create_pbr_mat("M_Mine_CryoFrost", (0.8, 0.9, 0.98, 1.0), metallic=0.1, roughness=0.6, bump_strength=0.35, noise_scale=25.0)
    mat_hazard_red = create_pbr_mat("M_Mine_HazardRedStrobe", (1.0, 0.1, 0.1, 1.0), metallic=0.0, roughness=0.1, emission_color=(1.0, 0.15, 0.15, 1.0), emission_strength=8.0)

    # Caverna de Roca de Asteroide Perforada (Pared trasera irregular)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(origin.x, origin.y + 4.2, origin.z + 2.0))
    rock_back = bpy.context.active_object
    rock_back.scale = (6.4, 1.2, 4.4)
    rock_back.data.materials.append(mat_asteroid_rock)
    apply_smooth_and_modifiers(rock_back, use_subdiv=True, subdiv_levels=2, use_bevel=False)

    # Pared rocosa lateral izquierda
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(origin.x - 3.2, origin.y, origin.z + 2.0))
    rock_left = bpy.context.active_object
    rock_left.scale = (1.4, 8.0, 4.2)
    rock_left.data.materials.append(mat_asteroid_rock)
    apply_smooth_and_modifiers(rock_left, use_subdiv=True, subdiv_levels=2, use_bevel=False)

    # Abismo inferior (Vacío de extracción minera)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(origin.x, origin.y, origin.z - 1.5))
    abyss_base = bpy.context.active_object
    abyss_base.scale = (6.5, 8.0, 0.8)
    abyss_base.data.materials.append(mat_asteroid_rock)

    # Pasarela Colgante de Titanio y Rejilla sobre el Abismo
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(origin.x - 0.5, origin.y, origin.z + 0.1))
    walkway = bpy.context.active_object
    walkway.scale = (2.2, 8.0, 0.2)
    walkway.data.materials.append(mat_walkway_grate)
    apply_smooth_and_modifiers(walkway, use_bevel=True, bevel_width=0.02)

    # Barandilla de Seguridad de Pasarela
    for y_rail in [-3.0, -1.0, 1.0, 3.0]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=1.1, location=(origin.x + 0.55, origin.y + y_rail, origin.z + 0.65))
        post = bpy.context.active_object
        post.data.materials.append(mat_titanium)
        apply_smooth_and_modifiers(post, use_bevel=True, bevel_width=0.01)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.045, depth=7.8, location=(origin.x + 0.55, origin.y, origin.z + 1.15), rotation=(math.radians(90), 0, 0))
    rail_bar = bpy.context.active_object
    rail_bar.data.materials.append(mat_titanium)
    apply_smooth_and_modifiers(rail_bar, use_bevel=True, bevel_width=0.01)

    # Vigas de Soporte Minero Pesadas de Titanio Oscuro (Arquería de contención)
    for y_arch in [-2.5, 0.5, 3.2]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(origin.x - 2.2, origin.y + y_arch, origin.z + 2.0))
        arch_col = bpy.context.active_object
        arch_col.scale = (0.35, 0.45, 4.0)
        arch_col.data.materials.append(mat_titanium)
        apply_smooth_and_modifiers(arch_col, use_bevel=True, bevel_width=0.03)

        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(origin.x, origin.y + y_arch, origin.z + 3.8))
        arch_beam = bpy.context.active_object
        arch_beam.scale = (5.0, 0.45, 0.35)
        arch_beam.data.materials.append(mat_titanium)
        apply_smooth_and_modifiers(arch_beam, use_bevel=True, bevel_width=0.03)

    # NÚCLEO DE CONFINAMIENTO MAGNÉTICO DE PLASMA (Cámara Toroidal Gigante)
    # Cilindro central emisor de plasma azul hiperbrillante
    bpy.ops.mesh.primitive_cylinder_add(radius=0.65, depth=3.2, location=(origin.x + 2.0, origin.y - 0.5, origin.z + 1.8))
    plasma_core = bpy.context.active_object
    plasma_core.data.materials.append(mat_plasma_core)
    apply_smooth_and_modifiers(plasma_core, use_subdiv=True, subdiv_levels=1)

    # Bobinas Toroidales de Confinamiento de Cobre y Titanio
    for z_coil in [0.7, 1.4, 2.1, 2.8]:
        bpy.ops.mesh.primitive_torus_add(major_radius=0.88, minor_radius=0.12, location=(origin.x + 2.0, origin.y - 0.5, origin.z + z_coil))
        coil = bpy.context.active_object
        coil.data.materials.append(mat_coil_copper)
        apply_smooth_and_modifiers(coil, use_bevel=True, bevel_width=0.02)

    # Estructura de Jaula y Anclaje del Núcleo de Plasma
    bpy.ops.mesh.primitive_cylinder_add(radius=1.1, depth=0.35, location=(origin.x + 2.0, origin.y - 0.5, origin.z + 0.25))
    base_coil = bpy.context.active_object
    base_coil.data.materials.append(mat_titanium)
    apply_smooth_and_modifiers(base_coil, use_bevel=True, bevel_width=0.02)

    bpy.ops.mesh.primitive_cylinder_add(radius=1.1, depth=0.35, location=(origin.x + 2.0, origin.y - 0.5, origin.z + 3.35))
    top_coil = bpy.context.active_object
    top_coil.data.materials.append(mat_titanium)
    apply_smooth_and_modifiers(top_coil, use_bevel=True, bevel_width=0.02)

    # Tanque Criogénico de Enfriamiento con Escarcha
    bpy.ops.mesh.primitive_cylinder_add(radius=0.45, depth=2.4, location=(origin.x - 2.0, origin.y - 1.8, origin.z + 1.3))
    cryo_tank = bpy.context.active_object
    cryo_tank.data.materials.append(mat_cryo_ice)
    apply_smooth_and_modifiers(cryo_tank, use_bevel=True, bevel_width=0.02)

    # Baliza Estroboscópica Roja de Sobrecalentamiento
    bpy.ops.mesh.primitive_cylinder_add(radius=0.12, depth=0.15, location=(origin.x - 2.0, origin.y + 2.5, origin.z + 2.8))
    strobe = bpy.context.active_object
    strobe.data.materials.append(mat_hazard_red)

    # ILUMINACIÓN: Radiación Masiva de Plasma Cian + Luz Roja de Advertencia
    light_plasma = bpy.data.lights.new(name="Light_Plasma_Radiation", type='POINT')
    light_plasma.energy = 850.0
    light_plasma.color = (0.15, 0.85, 1.0) # Azul cian intenso
    light_plasma_obj = bpy.data.objects.new(name="Light_Plasma_Obj", object_data=light_plasma)
    light_plasma_obj.location = (origin.x + 2.0, origin.y - 0.5, origin.z + 1.8)
    bpy.context.collection.objects.link(light_plasma_obj)

    light_strobe = bpy.data.lights.new(name="Light_Mine_RedStrobe", type='POINT')
    light_strobe.energy = 200.0
    light_strobe.color = (1.0, 0.1, 0.1)
    light_strobe_obj = bpy.data.objects.new(name="Light_Strobe_Obj", object_data=light_strobe)
    light_strobe_obj.location = (origin.x - 2.0, origin.y + 2.5, origin.z + 2.8)
    bpy.context.collection.objects.link(light_strobe_obj)

# ==============================================================================
# CARTELES FLOTANTES HOLOGRÁFICOS INDICADORES DE ARQUETIPO
# ==============================================================================
def build_archetype_label(text, location, color=(0.2, 0.8, 1.0, 1.0)):
    mat_label = create_pbr_mat(f"M_HoloLabel_{text.replace(' ', '_')}", color[:3] + (1.0,), metallic=0.0, roughness=0.1, emission_color=color, emission_strength=6.0)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=location)
    banner = bpy.context.active_object
    banner.scale = (3.2, 0.1, 0.45)
    banner.data.materials.append(mat_label)
    apply_smooth_and_modifiers(banner, use_bevel=True, bevel_width=0.02)

# ==============================================================================
# SETUP DE CÁMARAS Y RENDERIZADO
# ==============================================================================
def setup_camera(name, location, rotation_euler):
    cam = bpy.data.cameras.new(name=name)
    cam.lens = 32
    cam_obj = bpy.data.objects.new(name=name, object_data=cam)
    cam_obj.location = location
    cam_obj.rotation_euler = rotation_euler
    bpy.context.collection.objects.link(cam_obj)
    return cam_obj

def render_view(scene, cam_obj, filepath):
    scene.camera = cam_obj
    scene.render.filepath = filepath
    print(f"[RENDER] Iniciando render: {filepath} ...")
    bpy.ops.render.render(write_still=True)
    print(f"[RENDER] Completado con exito: {filepath}")
    # Copiar inmediatamente al directorio de artefactos
    filename = os.path.basename(filepath)
    artifact_copy = os.path.join(ARTIFACT_DIR, filename)
    shutil.copy2(filepath, artifact_copy)
    print(f"[ARTEFACTO] Copiado a: {artifact_copy}")

def main():
    print("=== GENERANDO DIORAMAS DE LOS 3 ARQUETIPOS DE MAPAS ===")
    scene = reset_scene()

    # Luz de relleno cenital suave neutra para la escena completa
    fill_light = bpy.data.lights.new(name="Fill_Ambient_Global", type='SUN')
    fill_light.energy = 0.4
    fill_light.color = (0.7, 0.75, 0.85)
    fill_obj = bpy.data.objects.new(name="Fill_Ambient_Global_Obj", object_data=fill_light)
    fill_obj.rotation_euler = (math.radians(45), math.radians(20), math.radians(-30))
    bpy.context.collection.objects.link(fill_obj)

    # 1. Construir los 3 dioramas
    print("Construyendo Carguero Químico...")
    build_chemical_hauler(Vector((-11.0, 0.0, 0.0)))
    build_archetype_label("TIER 1 - CARGUERO QUIMICO", Vector((-11.0, 3.8, 4.4)), (1.0, 0.6, 0.1, 1.0))

    print("Construyendo Crucero de Lujo Art-Déco...")
    build_luxury_starliner(Vector((0.0, 0.0, 0.0)))
    build_archetype_label("TIER 2 - CRUCERO DE LUJO", Vector((0.0, 3.8, 4.4)), (1.0, 0.8, 0.2, 1.0))

    print("Construyendo Refinería de Plasma Minera...")
    build_plasma_refinery(Vector((11.0, 0.0, 0.0)))
    build_archetype_label("TIER 3 - REFINERIA DE PLASMA", Vector((11.0, 3.8, 4.4)), (0.2, 0.85, 1.0, 1.0))

    # Guardar archivo .blend maestro de mapas
    blend_path = "F:/Dev/Game/Art/Blender/Mapas_Arquetipos_Oficial.blend"
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[BLEND] Guardado proyecto en: {blend_path}")

    # Cámaras:
    # A) Gran Panorama Comparativo (Muestra los 3 mapas simultáneos)
    cam_pano = setup_camera("Cam_Panorama", Vector((0.0, -14.0, 5.5)), (math.radians(72), 0.0, 0.0))
    cam_pano.data.lens = 22 # Gran angular cinematográfico

    # B) Closeup Carguero Químico
    cam_chem = setup_camera("Cam_CargueroQuimico", Vector((-11.0, -5.5, 2.4)), (math.radians(82), 0.0, 0.0))
    cam_chem.data.lens = 35

    # C) Closeup Crucero de Lujo
    cam_lux = setup_camera("Cam_CruceroLujo", Vector((0.0, -5.5, 2.3)), (math.radians(82), 0.0, 0.0))
    cam_lux.data.lens = 35

    # D) Closeup Refinería de Plasma
    cam_mine = setup_camera("Cam_RefineriaPlasma", Vector((11.0, -5.5, 2.4)), (math.radians(82), 0.0, 0.0))
    cam_mine.data.lens = 35

    # Renderizados
    render_view(scene, cam_pano, os.path.join(RENDERS_DIR, "Showcase_Mapas_Arquetipos_Panorama.png"))
    render_view(scene, cam_chem, os.path.join(RENDERS_DIR, "Showcase_Mapa_Carguero_Quimico.png"))
    render_view(scene, cam_lux, os.path.join(RENDERS_DIR, "Showcase_Mapa_Crucero_Lujo.png"))
    render_view(scene, cam_mine, os.path.join(RENDERS_DIR, "Showcase_Mapa_Refineria_Plasma.png"))

    print("=== TODOS LOS RENDERS DE MAPAS COMPLETADOS EXITOSAMENTE ===")

if __name__ == "__main__":
    main()

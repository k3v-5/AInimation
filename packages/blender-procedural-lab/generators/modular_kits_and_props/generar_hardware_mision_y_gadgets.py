# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Generador Oficial 3D: Hardware de Misión y Gadgets Tácticos de la Lanzadera
# Blender 5.2 LTS - Shaders PBR Desgastados, Biseles, Suavizado y Tomas Cinematográficas

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

def create_weathered_pbr(name, base_col, metal=0.8, rough=0.35, bump_str=0.2, emissive_col=(0,0,0,1), emissive_str=0.0, noise_scale=15.0):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = base_col
    bsdf.inputs['Metallic'].default_value = metal
    bsdf.inputs['Roughness'].default_value = rough

    if bump_str > 0.0:
        tex_coord = nodes.new('ShaderNodeTexCoord')
        mapping = nodes.new('ShaderNodeMapping')
        noise = nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value = noise_scale
        noise.inputs['Detail'].default_value = 6.0
        noise.inputs['Roughness'].default_value = 0.65

        links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
        links.new(mapping.outputs['Vector'], noise.inputs['Vector'])

        bump = nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value = bump_str
        bump.inputs['Distance'].default_value = 0.02
        links.new(noise.outputs['Fac'], bump.inputs['Height'])
        links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    if emissive_str > 0.0:
        if 'Emission Color' in bsdf.inputs:
            bsdf.inputs['Emission Color'].default_value = emissive_col
            bsdf.inputs['Emission Strength'].default_value = emissive_str
        elif 'Emission' in bsdf.inputs:
            bsdf.inputs['Emission'].default_value = emissive_col
            if 'Emission Strength' in bsdf.inputs:
                bsdf.inputs['Emission Strength'].default_value = emissive_str

    links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

# ==============================================================================
# HARDWARE DE LANZADERA: MESA HOLOGRÁFICA, CÁPSULA MÉDICA, BAHÍA MAGNÉTICA
# ==============================================================================

def build_holo_table(loc=Vector((-3.5, 0.0, 0.0))):
    """Mesa Holográfica Táctica 3D con Proyector Volumétrico de Nave y Anillos de Navegación"""
    mat_metal_base = create_weathered_pbr("M_Holo_MetalBase", (0.14, 0.15, 0.17, 1.0), metal=0.9, rough=0.35, bump_str=0.2)
    mat_metal_dark = create_weathered_pbr("M_Holo_MetalDark", (0.08, 0.09, 0.10, 1.0), metal=0.95, rough=0.25, bump_str=0.1)
    mat_console_screen = create_weathered_pbr("M_Holo_Screen", (0.02, 0.08, 0.12, 1.0), metal=0.1, rough=0.1, emissive_col=(0.1, 0.6, 0.9, 1.0), emissive_str=3.5)
    mat_holo_beam = create_weathered_pbr("M_Holo_CyanBeam", (0.1, 0.8, 1.0, 1.0), metal=0.0, rough=0.1, emissive_col=(0.2, 0.85, 1.0, 1.0), emissive_str=12.0)
    mat_holo_amber = create_weathered_pbr("M_Holo_WarningRing", (1.0, 0.6, 0.1, 1.0), metal=0.0, rough=0.1, emissive_col=(1.0, 0.6, 0.1, 1.0), emissive_str=8.0)

    # Base cilíndrica octogonal
    bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=1.3, depth=0.3, location=(loc.x, loc.y, loc.z + 0.15))
    base = bpy.context.active_object
    base.data.materials.append(mat_metal_dark)
    apply_smooth_and_modifiers(base, use_bevel=True, bevel_width=0.02)

    # Columna central con ranuras de ventilación
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.7, depth=0.6, location=(loc.x, loc.y, loc.z + 0.6))
    col = bpy.context.active_object
    col.data.materials.append(mat_metal_base)
    apply_smooth_and_modifiers(col, use_bevel=True, bevel_width=0.015)

    # Tablero táctico biselado circular
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=1.45, depth=0.15, location=(loc.x, loc.y, loc.z + 0.95))
    table_top = bpy.context.active_object
    table_top.data.materials.append(mat_metal_base)
    apply_smooth_and_modifiers(table_top, use_bevel=True, bevel_width=0.025)

    # Emisor de lente de proyección en el centro
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.45, depth=0.04, location=(loc.x, loc.y, loc.z + 1.04))
    lens = bpy.context.active_object
    lens.data.materials.append(mat_holo_beam)

    # Pantallas táctiles perimetrales en los 4 cuadrantes
    for angle in [0, 90, 180, 270]:
        rad = math.radians(angle)
        sx = loc.x + math.cos(rad) * 1.0
        sy = loc.y + math.sin(rad) * 1.0
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sx, sy, loc.z + 1.03), rotation=(math.radians(15), 0, rad))
        screen = bpy.context.active_object
        screen.scale = (0.45, 0.25, 0.02)
        screen.data.materials.append(mat_console_screen)

    # PROYECCIÓN HOLOGRÁFICA VOLUMÉTRICA FLOTANTE (Nave derelict en wireframe holográfico)
    # Casco de la nave proyectada flotando
    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.35, radius2=0.05, depth=0.9, location=(loc.x, loc.y, loc.z + 1.55), rotation=(math.radians(90), 0, 0))
    holo_ship = bpy.context.active_object
    holo_ship.data.materials.append(mat_holo_beam)

    # Anillos orbitales holográficos concéntricos
    bpy.ops.mesh.primitive_torus_add(major_radius=0.75, minor_radius=0.015, location=(loc.x, loc.y, loc.z + 1.45), rotation=(math.radians(15), math.radians(25), 0))
    holo_ring1 = bpy.context.active_object
    holo_ring1.data.materials.append(mat_holo_beam)

    bpy.ops.mesh.primitive_torus_add(major_radius=1.05, minor_radius=0.012, location=(loc.x, loc.y, loc.z + 1.65), rotation=(math.radians(-20), math.radians(10), 0))
    holo_ring2 = bpy.context.active_object
    holo_ring2.data.materials.append(mat_holo_amber)

    # Luz de proyección volumétrica cian
    light = bpy.data.lights.new(name="Light_HoloTable", type='POINT')
    light.energy = 450.0
    light.color = (0.2, 0.85, 1.0)
    light_obj = bpy.data.objects.new(name="Light_HoloTable_Obj", object_data=light)
    light_obj.location = (loc.x, loc.y, loc.z + 1.5)
    bpy.context.collection.objects.link(light_obj)

def build_medical_stasis_pod(loc=Vector((0.0, 0.0, 0.0))):
    """Cápsula de Estabilización Médica / Stasis Pod de Mamparo con Soporte Vital"""
    mat_chassis = create_weathered_pbr("M_Med_Chassis", (0.78, 0.80, 0.82, 1.0), metal=0.4, rough=0.3, bump_str=0.15)
    mat_interior = create_weathered_pbr("M_Med_Interior", (0.12, 0.14, 0.16, 1.0), metal=0.7, rough=0.5, bump_str=0.25)
    mat_glass = create_weathered_pbr("M_Med_CanopyGlass", (0.1, 0.4, 0.5, 1.0), metal=0.1, rough=0.08, bump_str=0.0)
    mat_vitals_screen = create_weathered_pbr("M_Med_ECGScreen", (0.05, 0.2, 0.1, 1.0), metal=0.1, rough=0.1, emissive_col=(0.2, 1.0, 0.4, 1.0), emissive_str=5.0)
    mat_hose = create_weathered_pbr("M_Med_BioHose", (0.15, 0.45, 0.7, 1.0), metal=0.2, rough=0.4, bump_str=0.3, noise_scale=25.0)
    mat_status_blue = create_weathered_pbr("M_Med_StasisBlue", (0.2, 0.7, 1.0, 1.0), metal=0.0, rough=0.1, emissive_col=(0.2, 0.7, 1.0, 1.0), emissive_str=6.0)

    # Chasis posterior empotrado
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(loc.x, loc.y, loc.z + 1.25))
    frame = bpy.context.active_object
    frame.scale = (1.1, 0.5, 2.3)
    frame.data.materials.append(mat_chassis)
    apply_smooth_and_modifiers(frame, use_bevel=True, bevel_width=0.03)

    # Nicho interior acolchado ergonómico
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(loc.x, loc.y + 0.12, loc.z + 1.2))
    cavity = bpy.context.active_object
    cavity.scale = (0.75, 0.35, 1.95)
    cavity.data.materials.append(mat_interior)
    apply_smooth_and_modifiers(cavity, use_subdiv=True, subdiv_levels=1, use_bevel=True, bevel_width=0.02)

    # Reposacabezas y arnés torácico
    bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=0.15, location=(loc.x, loc.y + 0.15, loc.z + 1.85), rotation=(math.radians(90), 0, 0))
    headrest = bpy.context.active_object
    headrest.data.materials.append(mat_interior)

    # Cúpula frontal de vidrio blindado con escarcha cian
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=0.45, depth=1.8, location=(loc.x, loc.y - 0.12, loc.z + 1.2))
    canopy = bpy.context.active_object
    canopy.scale = (1.0, 0.6, 1.0)
    canopy.data.materials.append(mat_glass)
    apply_smooth_and_modifiers(canopy, use_subdiv=True, subdiv_levels=1, use_bevel=True, bevel_width=0.015)

    # Monitor superior de constantes vitales / ECG
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(loc.x, loc.y - 0.28, loc.z + 2.25), rotation=(math.radians(20), 0, 0))
    monitor = bpy.context.active_object
    monitor.scale = (0.6, 0.08, 0.22)
    monitor.data.materials.append(mat_vitals_screen)

    # Mangueras bio-criogénicas laterales
    for x_side in [-0.48, 0.48]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.045, depth=1.4, location=(loc.x + x_side, loc.y - 0.1, loc.z + 1.1))
        hose = bpy.context.active_object
        hose.data.materials.append(mat_hose)
        apply_smooth_and_modifiers(hose, use_bevel=True, bevel_width=0.008)

    # Luces indicadoras de estasis cian
    for z_ind in [0.4, 1.2, 2.0]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.04, location=(loc.x - 0.52, loc.y - 0.22, loc.z + z_ind), rotation=(0, math.radians(90), 0))
        led = bpy.context.active_object
        led.data.materials.append(mat_status_blue)

    # Luz de estasis interior
    light = bpy.data.lights.new(name="Light_StasisPod", type='POINT')
    light.energy = 220.0
    light.color = (0.2, 0.75, 1.0)
    light_obj = bpy.data.objects.new(name="Light_StasisPod_Obj", object_data=light)
    light_obj.location = (loc.x, loc.y - 0.05, loc.z + 1.3)
    bpy.context.collection.objects.link(light_obj)

def build_magnetic_cargo_bay(loc=Vector((3.5, 0.0, 0.0))):
    """Bahía de Carga Magnética con Cepos de Fijación, Cajas de Botín y Tanques Asegurados"""
    mat_floor_grate = create_weathered_pbr("M_Cargo_GrateFloor", (0.15, 0.16, 0.18, 1.0), metal=0.85, rough=0.4, bump_str=0.3, noise_scale=20.0)
    mat_hazard_strip = create_weathered_pbr("M_Cargo_HazardStripe", (0.85, 0.65, 0.05, 1.0), metal=0.3, rough=0.45, bump_str=0.2)
    mat_crate_heavy = create_weathered_pbr("M_Cargo_HeavyCrate", (0.25, 0.35, 0.42, 1.0), metal=0.7, rough=0.4, bump_str=0.25)
    mat_mag_clamp = create_weathered_pbr("M_Cargo_MagClamp", (0.1, 0.1, 0.12, 1.0), metal=0.95, rough=0.2, bump_str=0.15)
    mat_mag_glow = create_weathered_pbr("M_Cargo_MagGlow", (0.1, 0.5, 1.0, 1.0), metal=0.0, rough=0.1, emissive_col=(0.2, 0.6, 1.0, 1.0), emissive_str=6.0)

    # Placa base de la bahía de carga con ranuras magnéticas
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(loc.x, loc.y, loc.z + 0.1))
    plate = bpy.context.active_object
    plate.scale = (2.6, 2.6, 0.2)
    plate.data.materials.append(mat_floor_grate)
    apply_smooth_and_modifiers(plate, use_bevel=True, bevel_width=0.02)

    # Perímetro con chevrones de advertencia
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(loc.x, loc.y + 1.25, loc.z + 0.22))
    stripe_back = bpy.context.active_object
    stripe_back.scale = (2.5, 0.15, 0.04)
    stripe_back.data.materials.append(mat_hazard_strip)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(loc.x, loc.y - 1.25, loc.z + 0.22))
    stripe_front = bpy.context.active_object
    stripe_front.scale = (2.5, 0.15, 0.04)
    stripe_front.data.materials.append(mat_hazard_strip)

    # Cepos de anclaje magnético en el suelo
    for x_clamp in [-0.85, 0.85]:
        for y_clamp in [-0.85, 0.85]:
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(loc.x + x_clamp, loc.y + y_clamp, loc.z + 0.25))
            c = bpy.context.active_object
            c.scale = (0.35, 0.35, 0.1)
            c.data.materials.append(mat_mag_clamp)
            apply_smooth_and_modifiers(c, use_bevel=True, bevel_width=0.015)

            # Emisor magnético cian
            bpy.ops.mesh.primitive_cylinder_add(radius=0.1, depth=0.03, location=(loc.x + x_clamp, loc.y + y_clamp, loc.z + 0.31))
            c_glow = bpy.context.active_object
            c_glow.data.materials.append(mat_mag_glow)

    # Contenedor de Botín Pesado de Alta Densidad (Bloqueado Magnéticamente)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(loc.x - 0.25, loc.y - 0.1, loc.z + 0.65))
    crate = bpy.context.active_object
    crate.scale = (1.1, 0.9, 0.85)
    crate.data.materials.append(mat_crate_heavy)
    apply_smooth_and_modifiers(crate, use_bevel=True, bevel_width=0.03)

    # Flejes de refuerzo y asas del contenedor
    bpy.ops.mesh.primitive_torus_add(major_radius=0.48, minor_radius=0.03, location=(loc.x - 0.25, loc.y - 0.1, loc.z + 0.65), rotation=(0, math.radians(90), 0))
    strap = bpy.context.active_object
    strap.scale = (1.0, 1.2, 0.9)
    strap.data.materials.append(mat_mag_clamp)

    # Tanque Criogénico de Combustible/O2 asegurado en la bahía
    bpy.ops.mesh.primitive_cylinder_add(radius=0.3, depth=1.1, location=(loc.x + 0.65, loc.y + 0.25, loc.z + 0.75))
    canister = bpy.context.active_object
    canister.data.materials.append(mat_hazard_strip)
    apply_smooth_and_modifiers(canister, use_subdiv=True, subdiv_levels=1, use_bevel=True, bevel_width=0.02)

    # Luz de bahía magnética
    light = bpy.data.lights.new(name="Light_CargoBay", type='POINT')
    light.energy = 260.0
    light.color = (1.0, 0.85, 0.5)
    light_obj = bpy.data.objects.new(name="Light_CargoBay_Obj", object_data=light)
    light_obj.location = (loc.x, loc.y, loc.z + 1.8)
    bpy.context.collection.objects.link(light_obj)

# ==============================================================================
# 3 GADGETS TÁCTICOS: MULTI-GAS EMF SCANNER, BENGALAS TÉRMICAS, PARCHE DE BRECHAS
# ==============================================================================

def build_gas_emf_scanner(loc=Vector((-2.0, -3.2, 0.5))):
    """Escáner Portátil Multigas y EMF (Sensor Atmosférico / Anomalías Espectrales)"""
    mat_body = create_weathered_pbr("M_Scan_Body", (0.12, 0.13, 0.15, 1.0), metal=0.6, rough=0.4, bump_str=0.25)
    mat_rubber = create_weathered_pbr("M_Scan_RubberGrip", (0.05, 0.05, 0.06, 1.0), metal=0.05, rough=0.75, bump_str=0.4, noise_scale=30.0)
    mat_lcd = create_weathered_pbr("M_Scan_LCDScreen", (0.05, 0.15, 0.2, 1.0), metal=0.1, rough=0.1, emissive_col=(0.2, 0.9, 1.0, 1.0), emissive_str=4.5)
    mat_led_green = create_weathered_pbr("M_Scan_LedGreen", (0.1, 1.0, 0.2, 1.0), metal=0.0, rough=0.1, emissive_col=(0.1, 1.0, 0.2, 1.0), emissive_str=6.0)
    mat_led_red = create_weathered_pbr("M_Scan_LedRed", (1.0, 0.1, 0.1, 1.0), metal=0.0, rough=0.1, emissive_col=(1.0, 0.1, 0.1, 1.0), emissive_str=6.0)
    mat_antenna = create_weathered_pbr("M_Scan_AntennaMetal", (0.8, 0.82, 0.85, 1.0), metal=0.95, rough=0.2, bump_str=0.1)

    # Chasis principal ergonómico
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(loc.x, loc.y, loc.z))
    body = bpy.context.active_object
    body.scale = (0.42, 0.16, 0.72)
    body.data.materials.append(mat_body)
    apply_smooth_and_modifiers(body, use_bevel=True, bevel_width=0.02)

    # Empuñadura de goma antideslizante inferior
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(loc.x, loc.y, loc.z - 0.24))
    grip = bpy.context.active_object
    grip.scale = (0.44, 0.18, 0.24)
    grip.data.materials.append(mat_rubber)
    apply_smooth_and_modifiers(grip, use_bevel=True, bevel_width=0.015)

    # Pantalla LCD retroiluminada
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(loc.x, loc.y - 0.085, loc.z + 0.12))
    screen = bpy.context.active_object
    screen.scale = (0.32, 0.02, 0.26)
    screen.data.materials.append(mat_lcd)

    # Barra LED graduada de EMF (5 niveles)
    for i in range(5):
        x_led = loc.x - 0.14 + (i * 0.07)
        mat_l = mat_led_red if i >= 3 else mat_led_green
        bpy.ops.mesh.primitive_cylinder_add(radius=0.018, depth=0.02, location=(x_led, loc.y - 0.085, loc.z + 0.29), rotation=(math.radians(90), 0, 0))
        led = bpy.context.active_object
        led.data.materials.append(mat_l)

    # Sonda / Antena telescópica de detección superior
    bpy.ops.mesh.primitive_cylinder_add(radius=0.018, depth=0.55, location=(loc.x + 0.12, loc.y, loc.z + 0.58))
    antenna = bpy.context.active_object
    antenna.data.materials.append(mat_antenna)
    apply_smooth_and_modifiers(antenna, use_bevel=True, bevel_width=0.005)

    # Rejilla de sensor olfativo de gas superior
    bpy.ops.mesh.primitive_cylinder_add(radius=0.065, depth=0.08, location=(loc.x - 0.1, loc.y, loc.z + 0.38))
    gas_cap = bpy.context.active_object
    gas_cap.data.materials.append(mat_antenna)
    apply_smooth_and_modifiers(gas_cap, use_bevel=True, bevel_width=0.01)

def build_thermal_flares(loc=Vector((0.0, -3.2, 0.5))):
    """Bengalas Térmicas de Emergencia (Alta Intensidad de Magnesio y Fósforo Térmico)"""
    mat_casing = create_weathered_pbr("M_Flare_BodyRed", (0.8, 0.15, 0.1, 1.0), metal=0.35, rough=0.5, bump_str=0.25)
    mat_metal_cap = create_weathered_pbr("M_Flare_MetalCap", (0.75, 0.75, 0.78, 1.0), metal=0.9, rough=0.3, bump_str=0.15)
    mat_strike_tip = create_weathered_pbr("M_Flare_IgniterTip", (0.1, 0.1, 0.1, 1.0), metal=0.1, rough=0.8, bump_str=0.4)
    mat_burning_tip = create_weathered_pbr("M_Flare_MagnesiumFire", (1.0, 0.5, 0.1, 1.0), metal=0.0, rough=0.1, emissive_col=(1.0, 0.45, 0.08, 1.0), emissive_str=16.0)

    # Bengala apagada (lista para usar)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.065, depth=0.65, location=(loc.x - 0.25, loc.y, loc.z))
    flare1 = bpy.context.active_object
    flare1.data.materials.append(mat_casing)
    apply_smooth_and_modifiers(flare1, use_bevel=True, bevel_width=0.008)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.07, depth=0.1, location=(loc.x - 0.25, loc.y, loc.z + 0.32))
    cap1 = bpy.context.active_object
    cap1.data.materials.append(mat_metal_cap)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.08, location=(loc.x - 0.25, loc.y, loc.z - 0.32))
    tip1 = bpy.context.active_object
    tip1.data.materials.append(mat_strike_tip)

    # Bengala encendida (activa en misión, proyectando calor y luz roja-ámbar de alta potencia)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.065, depth=0.65, location=(loc.x + 0.25, loc.y, loc.z), rotation=(math.radians(20), math.radians(15), 0))
    flare2 = bpy.context.active_object
    flare2.data.materials.append(mat_casing)
    apply_smooth_and_modifiers(flare2, use_bevel=True, bevel_width=0.008)

    # Punta incandescente en ignición
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.11, location=(loc.x + 0.35, loc.y + 0.12, loc.z + 0.35))
    flame = bpy.context.active_object
    flame.data.materials.append(mat_burning_tip)
    apply_smooth_and_modifiers(flame, use_subdiv=True, subdiv_levels=1)

    # Luz de magnesio de la bengala
    light = bpy.data.lights.new(name="Light_Flare_Fire", type='POINT')
    light.energy = 550.0
    light.color = (1.0, 0.45, 0.1)
    light_obj = bpy.data.objects.new(name="Light_Flare_Fire_Obj", object_data=light)
    light_obj.location = (loc.x + 0.35, loc.y + 0.12, loc.z + 0.38)
    bpy.context.collection.objects.link(light_obj)

def build_breach_foam_patch(loc=Vector((2.0, -3.2, 0.5))):
    """Parche Expansivo de Brechas (Lanzador / Cilindro de Espuma Polimérica Selladora)"""
    mat_tank_yellow = create_weathered_pbr("M_Foam_TankYellow", (0.85, 0.72, 0.1, 1.0), metal=0.7, rough=0.35, bump_str=0.25)
    mat_gun_metal = create_weathered_pbr("M_Foam_GunMetal", (0.18, 0.2, 0.22, 1.0), metal=0.9, rough=0.3, bump_str=0.2)
    mat_foam_goo = create_weathered_pbr("M_Foam_ExpandedPolymer", (0.9, 0.88, 0.75, 1.0), metal=0.05, rough=0.85, bump_str=0.6, noise_scale=22.0)
    mat_gauge_glass = create_weathered_pbr("M_Foam_GaugeScreen", (0.1, 0.7, 0.3, 1.0), metal=0.1, rough=0.1, emissive_col=(0.1, 0.8, 0.3, 1.0), emissive_str=4.0)

    # Cilindro presurizado de polímero
    bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=0.75, location=(loc.x, loc.y, loc.z), rotation=(0, math.radians(90), 0))
    tank = bpy.context.active_object
    tank.data.materials.append(mat_tank_yellow)
    apply_smooth_and_modifiers(tank, use_subdiv=True, subdiv_levels=1, use_bevel=True, bevel_width=0.015)

    # Boquilla cónica de inyección rápida frontal
    bpy.ops.mesh.primitive_cone_add(radius1=0.14, radius2=0.05, depth=0.28, location=(loc.x + 0.48, loc.y, loc.z), rotation=(0, math.radians(90), 0))
    nozzle = bpy.context.active_object
    nozzle.data.materials.append(mat_gun_metal)
    apply_smooth_and_modifiers(nozzle, use_bevel=True, bevel_width=0.01)

    # Empuñadura ergonómica con gatillo de presión
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(loc.x - 0.2, loc.y, loc.z - 0.26))
    handle = bpy.context.active_object
    handle.scale = (0.12, 0.14, 0.32)
    handle.data.materials.append(mat_gun_metal)
    apply_smooth_and_modifiers(handle, use_bevel=True, bevel_width=0.015)

    # Manómetro miniatura de presión
    bpy.ops.mesh.primitive_cylinder_add(radius=0.065, depth=0.04, location=(loc.x + 0.1, loc.y - 0.19, loc.z + 0.12), rotation=(math.radians(90), 0, 0))
    gauge = bpy.context.active_object
    gauge.data.materials.append(mat_gauge_glass)

    # Muestra de espuma polimérica expandida endurecida en la boquilla
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.14, location=(loc.x + 0.68, loc.y, loc.z))
    foam_blob = bpy.context.active_object
    foam_blob.data.materials.append(mat_foam_goo)
    apply_smooth_and_modifiers(foam_blob, use_subdiv=True, subdiv_levels=1)

# ==============================================================================
# ESCENARIOS Y COMPOSICIÓN DE RENDER
# ==============================================================================

def setup_camera(name, location, rotation_euler):
    cam = bpy.data.cameras.new(name=name)
    cam.lens = 35
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
    print(f"[ARTEFACTO] Guardado {filename}")

def main():
    print("=== CONSTRUYENDO HARDWARE DE MISIÓN Y GADGETS DE LANZADERA ===")
    scene = reset_scene()

    # Suelo general de la lanzadera de rescate
    mat_shuttle_deck = create_weathered_pbr("M_Shuttle_Deck", (0.12, 0.13, 0.15, 1.0), metal=0.85, rough=0.4, bump_str=0.3, noise_scale=20.0)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, -1.0, -0.1))
    deck = bpy.context.active_object
    deck.scale = (14.0, 10.0, 0.2)
    deck.data.materials.append(mat_shuttle_deck)
    apply_smooth_and_modifiers(deck, use_bevel=True, bevel_width=0.03)

    # Mamparo posterior de la nave
    mat_shuttle_wall = create_weathered_pbr("M_Shuttle_Bulkhead", (0.18, 0.20, 0.22, 1.0), metal=0.8, rough=0.35, bump_str=0.2)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 2.2, 2.2))
    wall = bpy.context.active_object
    wall.scale = (14.0, 0.4, 4.6)
    wall.data.materials.append(mat_shuttle_wall)
    apply_smooth_and_modifiers(wall, use_bevel=True, bevel_width=0.03)

    # Iluminación ambiental de nave espacial
    ambient_sun = bpy.data.lights.new(name="Ambient_Shuttle", type='SUN')
    ambient_sun.energy = 0.5
    ambient_sun.color = (0.75, 0.85, 1.0)
    sun_obj = bpy.data.objects.new(name="Ambient_Shuttle_Obj", object_data=ambient_sun)
    sun_obj.rotation_euler = (math.radians(50), math.radians(20), math.radians(-30))
    bpy.context.collection.objects.link(sun_obj)

    # 1. Construir Hardware
    print("Construyendo Mesa Holográfica 3D...")
    build_holo_table(Vector((-3.5, 0.0, 0.0)))

    print("Construyendo Cápsula Médica de Estasis...")
    build_medical_stasis_pod(Vector((0.0, 1.7, 0.0)))

    print("Construyendo Bahía de Carga Magnética...")
    build_magnetic_cargo_bay(Vector((3.5, 0.0, 0.0)))

    # 2. Construir Gadgets en Mesa de Equipamiento Delantera
    print("Construyendo Gadgets Tácticos (Escáner, Bengalas, Sellador)...")
    build_gas_emf_scanner(Vector((-2.0, -2.6, 0.6)))
    build_thermal_flares(Vector((0.0, -2.6, 0.6)))
    build_breach_foam_patch(Vector((2.0, -2.6, 0.6)))

    # Mesa de armamento donde descansan los gadgets
    mat_table = create_weathered_pbr("M_Equip_Bench", (0.1, 0.11, 0.13, 1.0), metal=0.9, rough=0.3, bump_str=0.2)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, -2.6, 0.18))
    bench = bpy.context.active_object
    bench.scale = (5.5, 1.1, 0.36)
    bench.data.materials.append(mat_table)
    apply_smooth_and_modifiers(bench, use_bevel=True, bevel_width=0.02)

    # Guardar .blend
    blend_path = "F:/Dev/Game/Art/Blender/Hardware_Mision_Y_Gadgets_Oficial.blend"
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[BLEND] Guardado {blend_path}")

    # Cámaras:
    # 1. Vista Panorámica Gran Angular de la Lanzadera de Misión
    cam_all = setup_camera("Cam_ShuttleHardware_Pano", Vector((0.0, -7.8, 3.6)), (math.radians(65), 0.0, 0.0))
    cam_all.data.lens = 24

    # 2. Primer Plano de Mesa Holográfica
    cam_holo = setup_camera("Cam_HoloTable_Closeup", Vector((-3.5, -3.2, 2.2)), (math.radians(70), 0.0, 0.0))
    cam_holo.data.lens = 38

    # 3. Primer Plano de Cápsula Médica
    cam_pod = setup_camera("Cam_MedPod_Closeup", Vector((0.0, -1.2, 1.5)), (math.radians(82), 0.0, 0.0))
    cam_pod.data.lens = 38

    # 4. Primer Plano de Gadgets Tácticos
    cam_gadgets = setup_camera("Cam_Gadgets_Closeup", Vector((0.0, -4.5, 1.8)), (math.radians(68), 0.0, 0.0))
    cam_gadgets.data.lens = 32

    # Renders
    render_and_save(scene, cam_all, os.path.join(RENDERS_DIR, "Showcase_Hardware_Lanzadera_Panorama.png"))
    render_and_save(scene, cam_holo, os.path.join(RENDERS_DIR, "Showcase_Hardware_Mesa_Holografica.png"))
    render_and_save(scene, cam_pod, os.path.join(RENDERS_DIR, "Showcase_Hardware_Capsula_Medica.png"))
    render_and_save(scene, cam_gadgets, os.path.join(RENDERS_DIR, "Showcase_Gadgets_Mision_Tácticos.png"))

    print("=== TODOS LOS RENDERS DE HARDWARE Y GADGETS FINALIZADOS CON ÉXITO ===")

if __name__ == "__main__":
    main()

"""
generar_props_interactivos.py
==============================
Pipeline de Arte 3D en Blender 5.2 LTS para Astra Hazard:
Genera el conjunto de Props Industriales y Maquinaria de Soporte Vital:
1. SM_OxygenRefillStation: Estación de pared de recarga de O2 con cilindro criogénico, manómetro y pantalla cian.
   - Submalla separada: SM_OxygenDispenser_Nozzle (boquilla ergonómica de acople rápido).
2. SM_Pipe_Straight_Valve: Tubería industrial modular (diámetro 22cm) con bridas, pernos y cuerpo de válvula.
   - Submalla separada: SM_Valve_Handwheel (volante giratorio rojo de 4 radios para cierre manual).
3. SM_StationTerminal_Console: Consola de control y ventilación con pantalla CRT ámbar, teclado y palancas.
4. Colisiones UCX convexas para cada objeto.
5. Exportación FBX a Art/FBX/Environment/Props/.
6. Renderizado de estudio y composición de hoja de showcase 4 cuadrantes (Showcase_Station_Props_Interactive.png).
"""

import bpy
import bmesh
import math
import os
import shutil

R = math.radians

PROJECT_ROOT = r"F:\Dev\Game"
FBX_DIR = os.path.join(PROJECT_ROOT, "Art", "FBX", "Environment", "Props")
RENDERS_DIR = os.path.join(PROJECT_ROOT, "Art", "Renders")
ARTIFACT_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\b59ff04f-3c21-4ee5-94b0-8e8f899f8923"

os.makedirs(FBX_DIR, exist_ok=True)
os.makedirs(RENDERS_DIR, exist_ok=True)

# Limpiar escena
bpy.ops.wm.read_factory_settings(use_empty=True)

# -----------------------------------------------------------------------------
# MATERIALES PBR INDUSTRIALES DESGASTADOS (RUST BUCKET SCI-FI)
# -----------------------------------------------------------------------------
def create_weathered_material(name, 
                              color_clean, 
                              color_grime, 
                              color_wear, 
                              metallic, 
                              roughness_clean, 
                              roughness_worn, 
                              grunge_scale=9.0, 
                              bump_strength=0.18, 
                              noise_detail=10.0,
                              emissive_color=(0,0,0,1), 
                              emissive_strength=0.0):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out_node = nodes.new(type='ShaderNodeOutputMaterial')
    out_node.location = (650, 0)

    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (320, 0)
    bsdf.inputs['Metallic'].default_value = metallic

    # Coordenadas de objeto y mapeo
    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    tex_coord.location = (-750, 0)

    mapping = nodes.new(type='ShaderNodeMapping')
    mapping.location = (-580, 0)
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])

    # Ruido procedural de desgaste y mugre (grunge)
    noise_macro = nodes.new(type='ShaderNodeTexNoise')
    noise_macro.location = (-380, 150)
    noise_macro.inputs['Scale'].default_value = grunge_scale
    noise_macro.inputs['Detail'].default_value = noise_detail
    noise_macro.inputs['Roughness'].default_value = 0.72
    noise_macro.inputs['Lacunarity'].default_value = 2.2
    links.new(mapping.outputs['Vector'], noise_macro.inputs['Vector'])

    # Rampa de color base: mugre/óxido -> base industrial -> desgaste metálico
    ramp_color = nodes.new(type='ShaderNodeValToRGB')
    ramp_color.location = (-120, 200)
    cr = ramp_color.color_ramp
    cr.elements[0].position = 0.20
    cr.elements[0].color = color_grime
    cr.elements[1].position = 0.65
    cr.elements[1].color = color_clean
    elem_wear = cr.elements.new(0.85)
    elem_wear.color = color_wear
    links.new(noise_macro.outputs['Fac'], ramp_color.inputs['Fac'])
    links.new(ramp_color.outputs['Color'], bsdf.inputs['Base Color'])

    # Rampa de rugosidad: zonas sucias más mate, zonas expuestas con variación
    ramp_rough = nodes.new(type='ShaderNodeValToRGB')
    ramp_rough.location = (-120, -60)
    cr_r = ramp_rough.color_ramp
    cr_r.elements[0].position = 0.20
    cr_r.elements[0].color = (roughness_worn, roughness_worn, roughness_worn, 1.0)
    cr_r.elements[1].position = 0.80
    cr_r.elements[1].color = (roughness_clean, roughness_clean, roughness_clean, 1.0)
    links.new(noise_macro.outputs['Fac'], ramp_rough.inputs['Fac'])
    links.new(ramp_rough.outputs['Color'], bsdf.inputs['Roughness'])

    # Relieve táctil (Bump): arañazos y textura de fundición
    if bump_strength > 0.0:
        bump = nodes.new(type='ShaderNodeBump')
        bump.location = (80, -200)
        bump.inputs['Strength'].default_value = bump_strength
        bump.inputs['Distance'].default_value = 0.018
        links.new(noise_macro.outputs['Fac'], bump.inputs['Height'])
        links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    if emissive_strength > 0.0:
        bsdf.inputs['Emission Color'].default_value = emissive_color
        bsdf.inputs['Emission Strength'].default_value = emissive_strength

    links.new(bsdf.outputs['BSDF'], out_node.inputs['Surface'])
    return mat

def create_crt_screen_material(name, glow_color, base_dark, scanline_scale=380.0, emission_power=5.8):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out_node = nodes.new(type='ShaderNodeOutputMaterial')
    out_node.location = (550, 0)

    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (250, 0)
    bsdf.inputs['Base Color'].default_value = base_dark
    bsdf.inputs['Metallic'].default_value = 0.05
    bsdf.inputs['Roughness'].default_value = 0.32

    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    tex_coord.location = (-550, 0)

    wave = nodes.new(type='ShaderNodeTexWave')
    wave.location = (-350, 0)
    wave.wave_type = 'BANDS'
    wave.inputs['Scale'].default_value = scanline_scale
    wave.inputs['Distortion'].default_value = 0.0
    links.new(tex_coord.outputs['Object'], wave.inputs['Vector'])

    ramp = nodes.new(type='ShaderNodeValToRGB')
    ramp.location = (-120, 0)
    cr = ramp.color_ramp
    cr.elements[0].position = 0.30
    cr.elements[0].color = (glow_color[0]*0.25, glow_color[1]*0.25, glow_color[2]*0.25, 1.0)
    cr.elements[1].position = 0.70
    cr.elements[1].color = glow_color
    links.new(wave.outputs['Color'], ramp.inputs['Fac'])

    links.new(ramp.outputs['Color'], bsdf.inputs['Emission Color'])
    bsdf.inputs['Emission Strength'].default_value = emission_power

    links.new(bsdf.outputs['BSDF'], out_node.inputs['Surface'])
    return mat

# Titanio oscuro militar: chapa mate con mugre de hidrocarburos y bordes desgastados
MAT_DARK_TITANIUM   = create_weathered_material(
    name="M_DarkTitanium",
    color_clean=(0.045, 0.050, 0.055, 1.0),
    color_grime=(0.080, 0.055, 0.035, 1.0),
    color_wear=(0.320, 0.340, 0.360, 1.0),
    metallic=0.88,
    roughness_clean=0.48,
    roughness_worn=0.80,
    grunge_scale=9.5,
    bump_strength=0.22
)

# Rojo de emergencia industrial serio: esmalte minio desgastado, no saturado
MAT_RESCUE_RED       = create_weathered_material(
    name="M_RescueRed",
    color_clean=(0.420, 0.065, 0.045, 1.0),
    color_grime=(0.110, 0.040, 0.025, 1.0),
    color_wear=(0.280, 0.280, 0.300, 1.0),
    metallic=0.32,
    roughness_clean=0.52,
    roughness_worn=0.85,
    grunge_scale=11.0,
    bump_strength=0.24
)

# Amarillo advertencia ocre quemado con saltos de pintura
MAT_HAZARD_YELLOW    = create_weathered_material(
    name="M_HazardYellow",
    color_clean=(0.580, 0.420, 0.050, 1.0),
    color_grime=(0.100, 0.075, 0.030, 1.0),
    color_wear=(0.260, 0.280, 0.300, 1.0),
    metallic=0.28,
    roughness_clean=0.58,
    roughness_worn=0.88,
    grunge_scale=12.5,
    bump_strength=0.22
)

# Acero industrial galvanizado cepillado (no cromo espejo) con condensación y grasa
MAT_CHROME_STEEL     = create_weathered_material(
    name="M_ChromeSteel",
    color_clean=(0.440, 0.460, 0.480, 1.0),
    color_grime=(0.140, 0.110, 0.080, 1.0),
    color_wear=(0.650, 0.670, 0.700, 1.0),
    metallic=0.92,
    roughness_clean=0.40,
    roughness_worn=0.72,
    grunge_scale=8.5,
    bump_strength=0.18
)

# Goma vulcanizada pesada y áspera con micro-desgaste
MAT_RUBBER_BLACK     = create_weathered_material(
    name="M_RubberBlack",
    color_clean=(0.035, 0.035, 0.038, 1.0),
    color_grime=(0.065, 0.055, 0.045, 1.0),
    color_wear=(0.080, 0.080, 0.085, 1.0),
    metallic=0.0,
    roughness_clean=0.85,
    roughness_worn=0.95,
    grunge_scale=18.0,
    bump_strength=0.28
)

# Hierro fundido corroído / oxidado para soportes y pernos
MAT_RUST_IRON        = create_weathered_material(
    name="M_RustIron",
    color_clean=(0.180, 0.100, 0.060, 1.0),
    color_grime=(0.100, 0.050, 0.030, 1.0),
    color_wear=(0.300, 0.260, 0.220, 1.0),
    metallic=0.60,
    roughness_clean=0.75,
    roughness_worn=0.92,
    grunge_scale=14.0,
    bump_strength=0.35
)

# Tecla especial de alerta / acceso
MAT_KEY_SPECIAL      = create_weathered_material(
    name="M_KeySpecial",
    color_clean=(0.350, 0.080, 0.060, 1.0),
    color_grime=(0.080, 0.040, 0.030, 1.0),
    color_wear=(0.200, 0.180, 0.180, 1.0),
    metallic=0.15,
    roughness_clean=0.60,
    roughness_worn=0.85,
    grunge_scale=15.0,
    bump_strength=0.20
)

# Pantallas diegéticas CRT retro con scanlines auténticas
MAT_O2_CYAN_SCREEN   = create_crt_screen_material("M_O2CyanScreen", (0.0, 0.70, 0.85, 1.0), (0.01, 0.05, 0.07, 1.0), scanline_scale=420.0, emission_power=5.5)
MAT_TERMINAL_AMBER   = create_crt_screen_material("M_TerminalAmber", (0.92, 0.48, 0.04, 1.0), (0.04, 0.02, 0.005, 1.0), scanline_scale=380.0, emission_power=6.0)

# Indicador de válvula encapsulado en resina
MAT_VALVE_GREEN      = create_weathered_material(
    name="M_ValveGreen",
    color_clean=(0.05, 0.55, 0.18, 1.0),
    color_grime=(0.02, 0.15, 0.05, 1.0),
    color_wear=(0.10, 0.65, 0.25, 1.0),
    metallic=0.1,
    roughness_clean=0.30,
    roughness_worn=0.60,
    grunge_scale=8.0,
    bump_strength=0.15,
    emissive_color=(0.04, 0.75, 0.22, 1.0),
    emissive_strength=4.5
)

# -----------------------------------------------------------------------------
# 1. ESTACIÓN DE RECARGA DE OXÍGENO (SM_OxygenRefillStation)
# -----------------------------------------------------------------------------
def build_oxygen_station():
    parts = []

    # Panel trasero de montaje en mamparo (alto 135cm, ancho 65cm, prof 14cm)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.68))
    back_panel = bpy.context.active_object
    back_panel.name = "O2_BackPanel"
    back_panel.scale = (0.65, 0.14, 1.35)
    bpy.ops.object.transform_apply(scale=True)
    back_panel.data.materials.append(MAT_DARK_TITANIUM)
    parts.append(back_panel)

    # Remaches reforzados en mamparo (hierro forjado oxidado)
    for cx in [-0.28, 0.28]:
        for cz in [0.08, 1.28]:
            bpy.ops.mesh.primitive_cylinder_add(radius=0.016, depth=0.025, vertices=12, location=(cx, -0.075, cz))
            rivet = bpy.context.active_object
            rivet.name = f"O2_Rivet_{cx}_{cz}"
            rivet.rotation_euler = (R(90), 0, 0)
            bpy.ops.object.transform_apply(rotation=True)
            rivet.data.materials.append(MAT_RUST_IRON)
            parts.append(rivet)

    # Placa metálica de advertencia y mantenimiento atornillada al mamparo
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.075, 0.16))
    haz_plate = bpy.context.active_object
    haz_plate.name = "O2_HazardPlate"
    haz_plate.scale = (0.42, 0.012, 0.12)
    bpy.ops.object.transform_apply(scale=True)
    haz_plate.data.materials.append(MAT_HAZARD_YELLOW)
    parts.append(haz_plate)

    # 4 Tornillos esquineros de la placa de advertencia
    for px in [-0.18, 0.18]:
        for pz in [0.12, 0.20]:
            bpy.ops.mesh.primitive_cylinder_add(radius=0.007, depth=0.015, vertices=8, location=(px, -0.083, pz))
            p_bolt = bpy.context.active_object
            p_bolt.name = f"O2_PlateBolt_{px}_{pz}"
            p_bolt.rotation_euler = (R(90), 0, 0)
            bpy.ops.object.transform_apply(rotation=True)
            p_bolt.data.materials.append(MAT_RUST_IRON)
            parts.append(p_bolt)

    # Tubos de alimentación criogénica superiores (entran al mamparo por el techo)
    for pipe_x in [-0.12, 0.0]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.022, depth=0.32, vertices=16, location=(pipe_x, -0.14, 1.25))
        feed_pipe = bpy.context.active_object
        feed_pipe.name = f"O2_FeederPipe_{pipe_x}"
        feed_pipe.data.materials.append(MAT_CHROME_STEEL)
        parts.append(feed_pipe)

        # Brida de conexión en el techo del panel
        bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=0.03, vertices=16, location=(pipe_x, -0.14, 1.35))
        f_flange = bpy.context.active_object
        f_flange.name = f"O2_FeederFlange_{pipe_x}"
        f_flange.data.materials.append(MAT_DARK_TITANIUM)
        parts.append(f_flange)

    # Cubierta superior inclinada con visera para la pantalla
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.09, 1.20))
    hood = bpy.context.active_object
    hood.name = "O2_DisplayHood"
    hood.scale = (0.55, 0.18, 0.22)
    bpy.ops.object.transform_apply(scale=True)
    hood.data.materials.append(MAT_DARK_TITANIUM)
    parts.append(hood)

    # Pantalla CRT / Digital de telemetría de O2 (Cian con scanlines)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.185, 1.20))
    screen = bpy.context.active_object
    screen.name = "O2_Screen"
    screen.scale = (0.44, 0.015, 0.15)
    bpy.ops.object.transform_apply(scale=True)
    screen.data.materials.append(MAT_O2_CYAN_SCREEN)
    parts.append(screen)

    # Cilindro criogénico central de O2 de alta presión (acero galvanizado pesado)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.11, depth=0.68, vertices=24, location=(-0.06, -0.16, 0.58))
    tank = bpy.context.active_object
    tank.name = "O2_CryoTank"
    tank.data.materials.append(MAT_CHROME_STEEL)
    parts.append(tank)

    # Cúpulas esféricas del tanque
    for tz, td in [(0.92, 1), (0.24, -1)]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.11, segments=24, ring_count=12, location=(-0.06, -0.16, tz))
        dome = bpy.context.active_object
        dome.name = f"O2_TankDome_{tz}"
        dome.scale = (1.0, 1.0, 0.55)
        bpy.ops.object.transform_apply(scale=True)
        dome.data.materials.append(MAT_CHROME_STEEL)
        parts.append(dome)

    # Bandas de sujeción del tanque con pernos reforzados
    for bz in [0.42, 0.74]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.06, -0.16, bz))
        bracket = bpy.context.active_object
        bracket.name = f"O2_TankBracket_{bz}"
        bracket.scale = (0.26, 0.24, 0.04)
        bpy.ops.object.transform_apply(scale=True)
        bracket.data.materials.append(MAT_DARK_TITANIUM)
        parts.append(bracket)

        for bx in [-0.18, 0.06]:
            bpy.ops.mesh.primitive_cylinder_add(radius=0.012, depth=0.04, vertices=12, location=(bx, -0.27, bz))
            b_bolt = bpy.context.active_object
            b_bolt.name = f"O2_BracketBolt_{bx}_{bz}"
            b_bolt.rotation_euler = (R(90), 0, 0)
            bpy.ops.object.transform_apply(rotation=True)
            b_bolt.data.materials.append(MAT_RUST_IRON)
            parts.append(b_bolt)

    # Manómetro circular analógico con dial
    bpy.ops.mesh.primitive_cylinder_add(radius=0.042, depth=0.035, vertices=16, location=(0.18, -0.15, 0.88))
    gauge = bpy.context.active_object
    gauge.name = "O2_PressureGauge"
    gauge.rotation_euler = (R(90), 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    gauge.data.materials.append(MAT_CHROME_STEEL)
    parts.append(gauge)

    # Esfera luminiscente del manómetro
    bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=0.01, vertices=16, location=(0.18, -0.17, 0.88))
    gauge_face = bpy.context.active_object
    gauge_face.name = "O2_GaugeFace"
    gauge_face.rotation_euler = (R(90), 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    gauge_face.data.materials.append(MAT_O2_CYAN_SCREEN)
    parts.append(gauge_face)

    # Receptáculo / Holster para la boquilla de reabastecimiento
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.18, -0.14, 0.45))
    holster = bpy.context.active_object
    holster.name = "O2_NozzleHolster"
    holster.scale = (0.12, 0.16, 0.26)
    bpy.ops.object.transform_apply(scale=True)
    holster.data.materials.append(MAT_DARK_TITANIUM)
    parts.append(holster)

    # Manguera corrugada espiralada de alta presión conectando la base del holster al tanque
    for hose_idx in range(6):
        hz = 0.28 + hose_idx * 0.035
        hx = 0.06 + math.sin(hose_idx * 0.6) * 0.05
        hy = -0.18 + math.cos(hose_idx * 0.6) * 0.03
        bpy.ops.mesh.primitive_torus_add(major_radius=0.024, minor_radius=0.009, location=(hx, hy, hz))
        h_ring = bpy.context.active_object
        h_ring.name = f"O2_HoseSegment_{hose_idx}"
        h_ring.data.materials.append(MAT_RUBBER_BLACK)
        parts.append(h_ring)

    # Unir cuerpo principal de la estación
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = back_panel
    bpy.ops.object.join()
    station_obj = bpy.context.active_object
    station_obj.name = "SM_OxygenRefillStation"
    bpy.ops.object.shade_smooth()

    # Colisión UCX para la estación
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.12, 0.68))
    ucx_station = bpy.context.active_object
    ucx_station.name = "UCX_SM_OxygenRefillStation_01"
    ucx_station.scale = (0.70, 0.38, 1.40)
    bpy.ops.object.transform_apply(scale=True)

    # ---------------------------------------------------------
    # Submalla móvil: Boquilla dispensadora de O2 (SM_OxygenDispenser_Nozzle)
    # ---------------------------------------------------------
    nozzle_parts = []

    # Empuñadura estilo pistola de combustible criogénico
    bpy.ops.mesh.primitive_cylinder_add(radius=0.024, depth=0.14, vertices=16, location=(0, 0, 0.07))
    n_handle = bpy.context.active_object
    n_handle.name = "Nozzle_Handle"
    n_handle.data.materials.append(MAT_RUBBER_BLACK)
    nozzle_parts.append(n_handle)

    # Cuerpo metálico de acople rápido
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.04, 0.12))
    n_body = bpy.context.active_object
    n_body.name = "Nozzle_Body"
    n_body.scale = (0.05, 0.10, 0.06)
    bpy.ops.object.transform_apply(scale=True)
    n_body.data.materials.append(MAT_DARK_TITANIUM)
    nozzle_parts.append(n_body)

    # Boquilla cilíndrica de inserción
    bpy.ops.mesh.primitive_cylinder_add(radius=0.016, depth=0.10, vertices=16, location=(0, 0.13, 0.12))
    n_tip = bpy.context.active_object
    n_tip.name = "Nozzle_Tip"
    n_tip.rotation_euler = (R(90), 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    n_tip.data.materials.append(MAT_CHROME_STEEL)
    nozzle_parts.append(n_tip)

    # Anillo LED de estado de acople
    bpy.ops.mesh.primitive_cylinder_add(radius=0.019, depth=0.015, vertices=16, location=(0, 0.09, 0.12))
    n_led = bpy.context.active_object
    n_led.name = "Nozzle_LED"
    n_led.rotation_euler = (R(90), 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    n_led.data.materials.append(MAT_O2_CYAN_SCREEN)
    nozzle_parts.append(n_led)

    # Unir boquilla
    bpy.ops.object.select_all(action='DESELECT')
    for p in nozzle_parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = n_handle
    bpy.ops.object.join()
    nozzle_obj = bpy.context.active_object
    nozzle_obj.name = "SM_OxygenDispenser_Nozzle"
    bpy.ops.object.shade_smooth()

    # Colisión UCX boquilla
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.05, 0.10))
    ucx_nozzle = bpy.context.active_object
    ucx_nozzle.name = "UCX_SM_OxygenDispenser_Nozzle_01"
    ucx_nozzle.scale = (0.08, 0.22, 0.18)
    bpy.ops.object.transform_apply(scale=True)

    # Ubicar la boquilla encajada en el holster de la estación
    nozzle_obj.location = (0.18, -0.14, 0.38)
    nozzle_obj.rotation_euler = (R(-25), 0, 0)
    ucx_nozzle.location = nozzle_obj.location
    ucx_nozzle.rotation_euler = nozzle_obj.rotation_euler

    return station_obj, [ucx_station], nozzle_obj, [ucx_nozzle]

# -----------------------------------------------------------------------------
# 2. TUBERÍA INDUSTRIAL Y VÁLVULA INTERACTIVA (SM_Pipe_Straight_Valve + SM_Valve_Handwheel)
# -----------------------------------------------------------------------------
def build_pipe_valve_cluster():
    pipe_parts = []

    # Tramo de tubería principal (diámetro 22cm, largo 180cm sobre eje X)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.11, depth=1.80, vertices=24, location=(0, 0, 0.35))
    pipe = bpy.context.active_object
    pipe.name = "Pipe_MainSpool"
    pipe.rotation_euler = (0, R(90), 0)
    bpy.ops.object.transform_apply(rotation=True)
    pipe.data.materials.append(MAT_DARK_TITANIUM)
    pipe_parts.append(pipe)

    # Franjas de advertencia industrial amarilla en la tubería
    for fx in [-0.55, 0.55]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.112, depth=0.15, vertices=24, location=(fx, 0, 0.35))
        band = bpy.context.active_object
        band.name = f"Pipe_HazardBand_{fx}"
        band.rotation_euler = (0, R(90), 0)
        bpy.ops.object.transform_apply(rotation=True)
        band.data.materials.append(MAT_HAZARD_YELLOW)
        pipe_parts.append(band)

    # Bridas de extremo con pernos (Extremo izquierdo y derecho)
    for bx in [-0.88, 0.88]:
        # Plato de brida
        bpy.ops.mesh.primitive_cylinder_add(radius=0.16, depth=0.05, vertices=24, location=(bx, 0, 0.35))
        flange = bpy.context.active_object
        flange.name = f"Pipe_Flange_{bx}"
        flange.rotation_euler = (0, R(90), 0)
        bpy.ops.object.transform_apply(rotation=True)
        flange.data.materials.append(MAT_DARK_TITANIUM)
        pipe_parts.append(flange)

        # Pernos perimetrales (8 pernos por brida en hierro oxidado)
        for p_i in range(8):
            ang = p_i * (math.pi / 4)
            py = math.cos(ang) * 0.135
            pz = 0.35 + math.sin(ang) * 0.135
            bpy.ops.mesh.primitive_cylinder_add(radius=0.012, depth=0.07, vertices=12, location=(bx, py, pz))
            bolt = bpy.context.active_object
            bolt.name = f"Pipe_Bolt_{bx}_{p_i}"
            bolt.rotation_euler = (0, R(90), 0)
            bpy.ops.object.transform_apply(rotation=True)
            bolt.data.materials.append(MAT_RUST_IRON)
            pipe_parts.append(bolt)

    # 2 Sillas de anclaje de suelo para fijación estructural pesada (Mamparo/Cubierta)
    for sx in [-0.62, 0.62]:
        # Pie de soporte en U
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sx, 0, 0.14))
        saddle = bpy.context.active_object
        saddle.name = f"Pipe_MountSaddle_{sx}"
        saddle.scale = (0.16, 0.32, 0.28)
        bpy.ops.object.transform_apply(scale=True)
        saddle.data.materials.append(MAT_DARK_TITANIUM)
        pipe_parts.append(saddle)

        # Pernos de anclaje al suelo (hierro forjado oxidado)
        for s_py in [-0.12, 0.12]:
            bpy.ops.mesh.primitive_cylinder_add(radius=0.014, depth=0.03, vertices=10, location=(sx, s_py, 0.015))
            s_bolt = bpy.context.active_object
            s_bolt.name = f"Pipe_SaddleBolt_{sx}_{s_py}"
            s_bolt.data.materials.append(MAT_RUST_IRON)
            pipe_parts.append(s_bolt)

    # Cuerpo central de la válvula (esférico/cúbico reforzado)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.15, segments=20, ring_count=12, location=(0, 0, 0.35))
    valve_body = bpy.context.active_object
    valve_body.name = "Pipe_ValveBody"
    valve_body.scale = (1.1, 1.0, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    valve_body.data.materials.append(MAT_DARK_TITANIUM)
    pipe_parts.append(valve_body)

    # Manómetro lateral de presión diferencial
    bpy.ops.mesh.primitive_cylinder_add(radius=0.032, depth=0.04, vertices=16, location=(0, -0.16, 0.38))
    side_gauge = bpy.context.active_object
    side_gauge.name = "Pipe_SideGauge"
    side_gauge.rotation_euler = (R(90), 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    side_gauge.data.materials.append(MAT_CHROME_STEEL)
    pipe_parts.append(side_gauge)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.026, depth=0.01, vertices=16, location=(0, -0.185, 0.38))
    s_gauge_face = bpy.context.active_object
    s_gauge_face.name = "Pipe_SideGaugeFace"
    s_gauge_face.rotation_euler = (R(90), 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    s_gauge_face.data.materials.append(MAT_O2_CYAN_SCREEN)
    pipe_parts.append(s_gauge_face)

    # Cuello vertical del prensaestopas (donde se acopla el volante)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.22, vertices=16, location=(0, 0, 0.54))
    bonnet = bpy.context.active_object
    bonnet.name = "Pipe_ValveBonnet"
    bonnet.data.materials.append(MAT_CHROME_STEEL)
    pipe_parts.append(bonnet)

    # Luz LED de estado de flujo (Verde = abierto, Rojo = cerrado)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.018, depth=0.015, vertices=16, location=(0, -0.055, 0.52))
    flow_led = bpy.context.active_object
    flow_led.name = "Pipe_FlowLED"
    flow_led.rotation_euler = (R(90), 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    flow_led.data.materials.append(MAT_VALVE_GREEN)
    pipe_parts.append(flow_led)

    # Unir cuerpo fijo de la tubería
    bpy.ops.object.select_all(action='DESELECT')
    for p in pipe_parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = pipe
    bpy.ops.object.join()
    pipe_obj = bpy.context.active_object
    pipe_obj.name = "SM_Pipe_Straight_Valve"
    bpy.ops.object.shade_smooth()

    # Colisión UCX de la tubería
    bpy.ops.mesh.primitive_cylinder_add(radius=0.14, depth=1.85, vertices=12, location=(0, 0, 0.35))
    ucx_pipe = bpy.context.active_object
    ucx_pipe.name = "UCX_SM_Pipe_Straight_Valve_01"
    ucx_pipe.rotation_euler = (0, R(90), 0)
    bpy.ops.object.transform_apply(rotation=True)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.50))
    ucx_bonnet = bpy.context.active_object
    ucx_bonnet.name = "UCX_SM_Pipe_Straight_Valve_02"
    ucx_bonnet.scale = (0.32, 0.32, 0.30)
    bpy.ops.object.transform_apply(scale=True)

    # ---------------------------------------------------------
    # Submalla móvil: Volante de cierre manual (SM_Valve_Handwheel)
    # Modelado con origen local en (0,0,0) para rotación limpia en UE5
    # ---------------------------------------------------------
    wheel_parts = []

    # Vástago central roscado
    bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=0.12, vertices=16, location=(0, 0, -0.04))
    stem = bpy.context.active_object
    stem.name = "Wheel_Stem"
    stem.data.materials.append(MAT_CHROME_STEEL)
    wheel_parts.append(stem)

    # Tuerca central de bloqueo
    bpy.ops.mesh.primitive_cylinder_add(radius=0.038, depth=0.03, vertices=6, location=(0, 0, 0.01))
    hub = bpy.context.active_object
    hub.name = "Wheel_Hub"
    hub.data.materials.append(MAT_RUST_IRON)
    wheel_parts.append(hub)

    # Llanta exterior del volante (Toro de 34cm de diámetro en Rojo Rescate)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.17, minor_radius=0.022, location=(0, 0, 0.0))
    rim = bpy.context.active_object
    rim.name = "Wheel_Rim"
    rim.data.materials.append(MAT_RESCUE_RED)
    wheel_parts.append(rim)

    # Muescas ergonómicas de agarre pesado en el perímetro
    for g_idx in range(8):
        ang_g = g_idx * (math.pi / 4)
        gx = math.cos(ang_g) * 0.17
        gy = math.sin(ang_g) * 0.17
        bpy.ops.mesh.primitive_cylinder_add(radius=0.009, depth=0.035, vertices=8, location=(gx, gy, 0.0))
        grip = bpy.context.active_object
        grip.name = f"Wheel_Grip_{g_idx}"
        grip.rotation_euler = (0, 0, ang_g)
        bpy.ops.object.transform_apply(rotation=True)
        grip.data.materials.append(MAT_DARK_TITANIUM)
        wheel_parts.append(grip)

    # 4 Radios de refuerzo del volante
    for r_idx in range(4):
        ang = r_idx * (math.pi / 2)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.012, depth=0.15, vertices=12, location=(0, 0, 0))
        spoke = bpy.context.active_object
        spoke.name = f"Wheel_Spoke_{r_idx}"
        spoke.rotation_euler = (R(90), 0, ang)
        spoke.location = (math.cos(ang) * 0.08, math.sin(ang) * 0.08, 0.0)
        bpy.ops.object.transform_apply(location=True, rotation=True)
        spoke.data.materials.append(MAT_RESCUE_RED)
        wheel_parts.append(spoke)

    # Unir volante
    bpy.ops.object.select_all(action='DESELECT')
    for p in wheel_parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = rim
    bpy.ops.object.join()
    wheel_obj = bpy.context.active_object
    wheel_obj.name = "SM_Valve_Handwheel"
    bpy.ops.object.shade_smooth()

    # Colisión UCX del volante
    bpy.ops.mesh.primitive_cylinder_add(radius=0.20, depth=0.08, vertices=12, location=(0, 0, 0.0))
    ucx_wheel = bpy.context.active_object
    ucx_wheel.name = "UCX_SM_Valve_Handwheel_01"

    # Posicionar el volante en su acople sobre el prensaestopas de la válvula
    wheel_obj.location = (0, 0, 0.69)
    ucx_wheel.location = (0, 0, 0.69)

    return pipe_obj, [ucx_pipe, ucx_bonnet], wheel_obj, [ucx_wheel]

# -----------------------------------------------------------------------------
# 3. CONSOLA TERMINAL DE CONTROL Y VENTILACIÓN (SM_StationTerminal_Console)
# -----------------------------------------------------------------------------
def build_station_terminal_console():
    parts = []

    # Base de pedestal con pernos de suelo (ancho 85cm, prof 65cm, alto 55cm)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.28))
    base = bpy.context.active_object
    base.name = "Console_BasePedestal"
    base.scale = (0.85, 0.65, 0.56)
    bpy.ops.object.transform_apply(scale=True)
    base.data.materials.append(MAT_DARK_TITANIUM)
    parts.append(base)

    # Ranuras de ventilación inferiores en la base
    for sl_i in range(4):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.33, 0.18 + sl_i*0.06))
        slat = bpy.context.active_object
        slat.name = f"Console_VentSlat_{sl_i}"
        slat.scale = (0.60, 0.02, 0.025)
        bpy.ops.object.transform_apply(scale=True)
        slat.data.materials.append(MAT_RUBBER_BLACK)
        parts.append(slat)

    # Chasis superior inclinado a 35 grados (superficie de control)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.05, 0.78))
    chassis = bpy.context.active_object
    chassis.name = "Console_UpperChassis"
    chassis.scale = (0.95, 0.75, 0.44)
    bpy.ops.object.transform_apply(scale=True)
    chassis.data.materials.append(MAT_DARK_TITANIUM)
    parts.append(chassis)

    # Pantalla CRT vintage inclinada de fósforo ámbar con visera pesada
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.12, 0.04, 0.94))
    crt_bezel = bpy.context.active_object
    crt_bezel.name = "Console_CRTBezel"
    crt_bezel.scale = (0.54, 0.05, 0.38)
    crt_bezel.rotation_euler = (R(-35), 0, 0)
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    crt_bezel.data.materials.append(MAT_DARK_TITANIUM)
    parts.append(crt_bezel)

    # 4 Tornillos de fijación del bisel CRT (hierro oxidado)
    for bx in [-0.36, 0.12]:
        for bz in [0.80, 1.08]:
            bpy.ops.mesh.primitive_cylinder_add(radius=0.007, depth=0.02, vertices=8, location=(bx, -0.05, bz))
            c_bolt = bpy.context.active_object
            c_bolt.name = f"Console_CRTBolt_{bx}_{bz}"
            c_bolt.rotation_euler = (R(-35), 0, 0)
            bpy.ops.object.transform_apply(rotation=True)
            c_bolt.data.materials.append(MAT_RUST_IRON)
            parts.append(c_bolt)

    # Cristal de fósforo ámbar activo con scanlines
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.12, 0.02, 0.945))
    crt_screen = bpy.context.active_object
    crt_screen.name = "Console_AmberScreen"
    crt_screen.scale = (0.46, 0.015, 0.30)
    crt_screen.rotation_euler = (R(-35), 0, 0)
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    crt_screen.data.materials.append(MAT_TERMINAL_AMBER)
    parts.append(crt_screen)

    # Teclado mecánico integrado en la bandeja frontal
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.12, -0.22, 0.81))
    keyboard_bed = bpy.context.active_object
    keyboard_bed.name = "Console_KeyboardBed"
    keyboard_bed.scale = (0.48, 0.20, 0.03)
    keyboard_bed.rotation_euler = (R(-25), 0, 0)
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    keyboard_bed.data.materials.append(MAT_RUBBER_BLACK)
    parts.append(keyboard_bed)

    # Barra tubular de protección frontal contra golpes (Crash bar de acero pesado)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.012, depth=0.52, vertices=16, location=(-0.12, -0.34, 0.77))
    crash_bar = bpy.context.active_object
    crash_bar.name = "Console_CrashBar"
    crash_bar.rotation_euler = (0, R(90), 0)
    bpy.ops.object.transform_apply(rotation=True)
    crash_bar.data.materials.append(MAT_CHROME_STEEL)
    parts.append(crash_bar)

    for bar_end in [-0.36, 0.12]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(bar_end, -0.31, 0.76))
        c_bracket = bpy.context.active_object
        c_bracket.name = f"Console_CrashBracket_{bar_end}"
        c_bracket.scale = (0.03, 0.06, 0.04)
        bpy.ops.object.transform_apply(scale=True)
        c_bracket.data.materials.append(MAT_DARK_TITANIUM)
        parts.append(c_bracket)

    # Teclas mecánicas modeladas con variedad funcional seria
    for ky_row in range(3):
        for ky_col in range(6):
            kx = -0.28 + ky_col * 0.065
            ky = -0.28 + ky_row * 0.055
            kz = 0.80 + ky_row * 0.025
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(kx, ky, kz))
            key_cap = bpy.context.active_object
            key_cap.name = f"Console_Key_{ky_row}_{ky_col}"
            key_cap.scale = (0.045, 0.040, 0.015)
            key_cap.rotation_euler = (R(-25), 0, 0)
            bpy.ops.object.transform_apply(scale=True, rotation=True)

            # Asignar material funcional según tipo de tecla
            if ky_row == 0 and ky_col == 5:
                key_cap.data.materials.append(MAT_KEY_SPECIAL)  # Tecla ENTER / EXECUTE roja
            elif ky_row == 2 and ky_col == 0:
                key_cap.data.materials.append(MAT_HAZARD_YELLOW) # Tecla OVERRIDE ocre
            else:
                key_cap.data.materials.append(MAT_DARK_TITANIUM)

            parts.append(key_cap)

    # Banco de 3 palancas de aislamiento de sectores de emergencia (lado derecho)
    for lev_i in range(3):
        lx = 0.26 + lev_i * 0.065
        # Base de ranura de la palanca
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(lx, -0.08, 0.88))
        slot = bpy.context.active_object
        slot.name = f"Console_LeverSlot_{lev_i}"
        slot.scale = (0.04, 0.16, 0.03)
        slot.rotation_euler = (R(-35), 0, 0)
        bpy.ops.object.transform_apply(scale=True, rotation=True)
        slot.data.materials.append(MAT_CHROME_STEEL)
        parts.append(slot)

        # Palanca roja con pomo esférico
        bpy.ops.mesh.primitive_cylinder_add(radius=0.008, depth=0.10, vertices=12, location=(lx, -0.07, 0.94))
        lever_arm = bpy.context.active_object
        lever_arm.name = f"Console_LeverArm_{lev_i}"
        lever_arm.rotation_euler = (R(15), 0, 0)
        bpy.ops.object.transform_apply(rotation=True)
        lever_arm.data.materials.append(MAT_CHROME_STEEL)
        parts.append(lever_arm)

        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.018, segments=12, ring_count=8, location=(lx, -0.055, 0.99))
        knob = bpy.context.active_object
        knob.name = f"Console_LeverKnob_{lev_i}"
        knob.data.materials.append(MAT_RESCUE_RED)
        parts.append(knob)

    # Anillo bisel protector del botón maestro de purga
    bpy.ops.mesh.primitive_cylinder_add(radius=0.042, depth=0.035, vertices=16, location=(0.32, -0.24, 0.815))
    btn_guard = bpy.context.active_object
    btn_guard.name = "Console_PurgeGuardRing"
    btn_guard.rotation_euler = (R(-25), 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    btn_guard.data.materials.append(MAT_DARK_TITANIUM)
    parts.append(btn_guard)

    # Botón maestro de purga / descompresión de ventilación
    bpy.ops.mesh.primitive_cylinder_add(radius=0.030, depth=0.025, vertices=16, location=(0.32, -0.24, 0.83))
    master_btn = bpy.context.active_object
    master_btn.name = "Console_PurgeButton"
    master_btn.rotation_euler = (R(-25), 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    master_btn.data.materials.append(MAT_RESCUE_RED)
    parts.append(master_btn)

    # Unir consola terminal
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = base
    bpy.ops.object.join()
    console_obj = bpy.context.active_object
    console_obj.name = "SM_StationTerminal_Console"
    bpy.ops.object.shade_smooth()

    # Colisión UCX de consola (2 convex boxes)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.28))
    ucx_base = bpy.context.active_object
    ucx_base.name = "UCX_SM_StationTerminal_Console_01"
    ucx_base.scale = (0.90, 0.70, 0.58)
    bpy.ops.object.transform_apply(scale=True)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.06, 0.84))
    ucx_top = bpy.context.active_object
    ucx_top.name = "UCX_SM_StationTerminal_Console_02"
    ucx_top.scale = (1.00, 0.80, 0.52)
    bpy.ops.object.transform_apply(scale=True)

    return console_obj, [ucx_base, ucx_top]

# ---------------------------------------------------------
# EXPORTACIÓN FBX
# ---------------------------------------------------------
def export_fbx(name, mesh_obj, ucx_objs):
    orig_loc = mesh_obj.location.copy()
    orig_rot = mesh_obj.rotation_euler.copy()
    ucx_locs = [u.location.copy() for u in ucx_objs]
    ucx_rots = [u.rotation_euler.copy() for u in ucx_objs]

    if name in ["SM_Valve_Handwheel", "SM_OxygenDispenser_Nozzle"]:
        mesh_obj.location = (0, 0, 0)
        mesh_obj.rotation_euler = (0, 0, 0)
        for u in ucx_objs:
            u.location = (0, 0, 0)
            u.rotation_euler = (0, 0, 0)
        bpy.context.view_layer.update()

    bpy.ops.object.select_all(action='DESELECT')
    mesh_obj.select_set(True)
    for u in ucx_objs:
        u.select_set(True)
    bpy.context.view_layer.objects.active = mesh_obj

    fbx_path = os.path.join(FBX_DIR, f"{name}.fbx")
    bpy.ops.export_scene.fbx(
        filepath=fbx_path,
        use_selection=True,
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_ALL',
        axis_forward='-Z',
        axis_up='Y',
        mesh_smooth_type='FACE'
    )
    print(f"[OK] Exportado FBX: {fbx_path}")

    # Restaurar transformación para el montaje de showcase
    mesh_obj.location = orig_loc
    mesh_obj.rotation_euler = orig_rot
    for i, u in enumerate(ucx_objs):
        u.location = ucx_locs[i]
        u.rotation_euler = ucx_rots[i]
    bpy.context.view_layer.update()

# -----------------------------------------------------------------------------
# ILUMINACIÓN Y ESTUDIO DE RENDER
# -----------------------------------------------------------------------------
def setup_lighting():
    # Luz clave direccional industrial (temperatura neutra/fría, sombras dramáticas)
    key_light = bpy.data.lights.new("KeyLight", type='AREA')
    key_light.energy = 450.0
    key_light.size = 2.4
    key_light.color = (0.95, 0.96, 1.0)
    key_obj = bpy.data.objects.new("KeyLight", key_light)
    key_obj.location = (2.2, -2.6, 2.6)
    key_obj.rotation_euler = (R(55), 0, R(40))
    bpy.context.collection.objects.link(key_obj)

    # Luz de relleno suave tenue para preservar sombras profundas
    fill_light = bpy.data.lights.new("FillLight", type='AREA')
    fill_light.energy = 130.0
    fill_light.size = 3.5
    fill_light.color = (0.50, 0.70, 0.90)
    fill_obj = bpy.data.objects.new("FillLight", fill_light)
    fill_obj.location = (-2.8, 1.8, 2.0)
    fill_obj.rotation_euler = (R(60), 0, R(-130))
    bpy.context.collection.objects.link(fill_obj)

    # Rim light de recorte trasero que perfila las siluetas y los desconchones
    rim_light = bpy.data.lights.new("RimLight", type='SPOT')
    rim_light.energy = 520.0
    rim_light.spot_size = R(70)
    rim_light.color = (0.85, 0.92, 1.0)
    rim_obj = bpy.data.objects.new("RimLight", rim_light)
    rim_obj.location = (0.0, 2.6, 2.5)
    rim_obj.rotation_euler = (R(140), 0, 0)
    bpy.context.collection.objects.link(rim_obj)

    # Luz de rebote inferior muy sutil
    bounce_light = bpy.data.lights.new("BounceLight", type='AREA')
    bounce_light.energy = 40.0
    bounce_light.size = 4.0
    bounce_light.color = (0.6, 0.65, 0.7)
    bounce_obj = bpy.data.objects.new("BounceLight", bounce_light)
    bounce_obj.location = (0.0, -1.2, -0.4)
    bounce_obj.rotation_euler = (R(-60), 0, 0)
    bpy.context.collection.objects.link(bounce_obj)

    # Entorno oscuro de estación espacial decadente
    world = bpy.data.worlds.new("StudioWorld")
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (0.015, 0.018, 0.022, 1.0)
        bg.inputs['Strength'].default_value = 0.25
    bpy.context.scene.world = world

# -----------------------------------------------------------------------------
# EJECUCIÓN PRINCIPAL
# -----------------------------------------------------------------------------
print(">>> Generando Props Industriales y Maquinaria de Soporte Vital...")

o2_station, o2_ucx, o2_nozzle, nozzle_ucx = build_oxygen_station()
export_fbx("SM_OxygenRefillStation", o2_station, o2_ucx)
export_fbx("SM_OxygenDispenser_Nozzle", o2_nozzle, nozzle_ucx)

pipe_cluster, pipe_ucx, valve_wheel, wheel_ucx = build_pipe_valve_cluster()
export_fbx("SM_Pipe_Straight_Valve", pipe_cluster, pipe_ucx)
export_fbx("SM_Valve_Handwheel", valve_wheel, wheel_ucx)

console_terminal, console_ucx = build_station_terminal_console()
export_fbx("SM_StationTerminal_Console", console_terminal, console_ucx)

# Ocultar colisiones UCX en render
all_ucx = o2_ucx + nozzle_ucx + pipe_ucx + wheel_ucx + console_ucx
for u in all_ucx:
    u.hide_render = True
    u.hide_viewport = True

# Pedestal de presentación
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, -0.05))
pedestal = bpy.context.active_object
pedestal.name = "Showcase_Pedestal"
pedestal.scale = (5.2, 2.8, 0.1)
bpy.ops.object.transform_apply(scale=True)
pedestal.data.materials.append(MAT_DARK_TITANIUM)

setup_lighting()

# Cámara y Target con constraint TRACK_TO
cam_target = bpy.data.objects.new("CamTarget", None)
bpy.context.collection.objects.link(cam_target)

cam_data = bpy.data.cameras.new("ShowcaseCam")
cam_data.lens = 45.0
cam_obj = bpy.data.objects.new("ShowcaseCam", cam_data)
bpy.context.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj

track_constraint = cam_obj.constraints.new(type='TRACK_TO')
track_constraint.target = cam_target
track_constraint.track_axis = 'TRACK_NEGATIVE_Z'
track_constraint.up_axis = 'UP_Y'

scene = bpy.context.scene
scene.render.engine = 'CYCLES' if bpy.context.preferences.addons.get('cycles') else 'BLENDER_EEVEE_NEXT'
if scene.render.engine == 'CYCLES':
    scene.cycles.samples = 64
    scene.cycles.use_denoising = True

scene.render.resolution_x = 1280
scene.render.resolution_y = 720

# Configuraciones de render aisladas y calibradas
render_configs = {
    "arsenal_all": {
        "o2_pos":     (-1.50, 0.0, 0.0),      "o2_vis": True,
        "noz_pos":    (-1.32, -0.14, 0.38),   "noz_vis": True,
        "pipe_pos":   (0.0, -0.10, 0.0),      "pipe_vis": True,
        "whl_pos":    (0.0, -0.10, 0.69),     "whl_vis": True,
        "con_pos":    (1.50, 0.0, 0.0),       "con_vis": True,
        "cam_pos":    (0.0, -4.1, 1.45),
        "target_pos": (0.0, 0.0, 0.65),
        "lens":       38.0
    },
    "o2_closeup": {
        "o2_pos":     (0.0, 0.0, 0.0),        "o2_vis": True,
        "noz_pos":    (0.18, -0.14, 0.38),    "noz_vis": True,
        "pipe_pos":   (0, 0, 0),              "pipe_vis": False,
        "whl_pos":    (0, 0, 0),              "whl_vis": False,
        "con_pos":    (0, 0, 0),              "con_vis": False,
        "cam_pos":    (-0.45, -2.75, 1.05),
        "target_pos": (0.05, -0.05, 0.72),
        "lens":       44.0
    },
    "pipe_closeup": {
        "o2_pos":     (0, 0, 0),              "o2_vis": False,
        "noz_pos":    (0, 0, 0),              "noz_vis": False,
        "pipe_pos":   (0.0, 0.0, 0.0),        "pipe_vis": True,
        "whl_pos":    (0.0, 0.0, 0.69),       "whl_vis": True,
        "con_pos":    (0, 0, 0),              "con_vis": False,
        "cam_pos":    (0.0, -2.6, 0.85),
        "target_pos": (0.0, 0.0, 0.48),
        "lens":       46.0
    },
    "terminal_closeup": {
        "o2_pos":     (0, 0, 0),              "o2_vis": False,
        "noz_pos":    (0, 0, 0),              "noz_vis": False,
        "pipe_pos":   (0, 0, 0),              "pipe_vis": False,
        "whl_pos":    (0, 0, 0),              "whl_vis": False,
        "con_pos":    (0.0, 0.0, 0.0),        "con_vis": True,
        "cam_pos":    (-0.55, -1.95, 1.70),
        "target_pos": (0.0, -0.08, 0.88),
        "lens":       48.0
    }
}

rendered_files = []
for shot_name, cfg in render_configs.items():
    o2_station.location = cfg["o2_pos"]
    o2_station.hide_render = not cfg["o2_vis"]

    o2_nozzle.location = cfg["noz_pos"]
    o2_nozzle.hide_render = not cfg["noz_vis"]

    pipe_cluster.location = cfg["pipe_pos"]
    pipe_cluster.hide_render = not cfg["pipe_vis"]

    valve_wheel.location = cfg["whl_pos"]
    valve_wheel.hide_render = not cfg["whl_vis"]

    console_terminal.location = cfg["con_pos"]
    console_terminal.hide_render = not cfg["con_vis"]

    cam_obj.location = cfg["cam_pos"]
    cam_target.location = cfg["target_pos"]
    cam_data.lens = cfg["lens"]
    bpy.context.view_layer.update()

    out_file = os.path.join(RENDERS_DIR, f"Showcase_Props_{shot_name}.png")
    scene.render.filepath = out_file
    bpy.ops.render.render(write_still=True)
    rendered_files.append(out_file)
    print(f"[OK] Renderizado cuadrante: {out_file}")

# Guardar escena blend
blend_path = os.path.join(PROJECT_ROOT, "Art", "Blender", "Props_Industriales_Interactivas.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f"[OK] Guardado archivo Blender: {blend_path}")

# Composición 2x2 en 2560x1440
try:
    from PIL import Image, ImageDraw, ImageFont

    canvas = Image.new("RGB", (2560, 1440), (10, 12, 16))
    positions = [(0, 0), (1280, 0), (0, 720), (1280, 720)]
    labels = [
        "PROPS INDUSTRIALES Y SOPORTE VITAL (RUST BUCKET) - GDD SEC. 4",
        "ESTACION DE RECARGA DE OXIGENO (CILINDRO CRIOGENICO, PANTALLA Y BOQUILLA)",
        "TUBERIA INDUSTRIAL CON VALVULA INTERACTIVA (VOLANTE ROJO DESACOPLADO)",
        "CONSOLA TERMINAL DE CONTROL Y VENTILACION (PANTALLA CRT AMBAR Y PALANCAS)"
    ]

    # Cargar fuente TTF nítida si existe
    font = None
    for font_path in [r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\consola.ttf"]:
        if os.path.exists(font_path):
            try:
                font = ImageFont.truetype(font_path, 22)
                break
            except Exception:
                pass

    for i, file_path in enumerate(rendered_files):
        img = Image.open(file_path).resize((1280, 720), Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(img)
        draw.rectangle([(25, 25), (1080, 75)], fill=(12, 15, 20, 230), outline=(255, 185, 45), width=2)
        if font:
            draw.text((40, 36), labels[i], fill=(255, 185, 45), font=font)
        else:
            draw.text((40, 38), labels[i], fill=(255, 185, 45))
        canvas.paste(img, positions[i])

    showcase_path = os.path.join(RENDERS_DIR, "Showcase_Station_Props_Interactive.png")
    canvas.save(showcase_path)
    print(f"[OK] Showcase compuesto guardado: {showcase_path}")

    artifact_showcase = os.path.join(ARTIFACT_DIR, "Showcase_Station_Props_Interactive.png")
    shutil.copy2(showcase_path, artifact_showcase)
    print(f"[OK] Showcase copiado a artefactos: {artifact_showcase}")
    print(f"[OK] Showcase copiado a artefactos: {artifact_showcase}")

except Exception as e:
    print(f"[WARN] Error componiendo con PIL: {e}")
    fallback_path = rendered_files[0]
    artifact_showcase = os.path.join(ARTIFACT_DIR, "Showcase_Station_Props_Interactive.png")
    shutil.copy2(fallback_path, artifact_showcase)

print(">>> ¡Pipeline de Blender completado exitosamente!")

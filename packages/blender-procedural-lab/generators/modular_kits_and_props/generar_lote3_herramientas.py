"""
generar_lote3_herramientas.py
==============================
Pipeline de Arte 3D en Blender 5.2 LTS para Astra Hazard:
Generación de modelos de alta fidelidad, desgastados y detallados para el Lote 3 de Herramientas Especiales:
1. SM_FoamLauncher_Gun: Lanzador pesado de espuma ignífuga/retardante con cañón perforado, boquilla difusora
   con aletas internas, tanque ventral esférico-cilíndrico con manómetro de aguja y tubos trenzados.
2. SM_NetLauncher_Gun: Lanza-redes electrostático táctico con 4 cañones huecos divergentes, tambor central
   con ventana de policarbonato, bobinas de cobre cerámicas, batería militar y empuñaduras ergonómicas.
3. SM_HydraulicJack_Tool: Gato hidráulico pesado de rescate (15T) con base dentada, cilindro acanalado,
   émbolo cromado con marcas métricas, cabeza articulada en V, palanca articulada y manómetro analógico.
4. Colisionadores convexos UCX_* para cada herramienta.
5. Shaders PBR industriales hiper-detallados (desgaste, suciedad, arañazos metálicos y micro-bump).
6. Exportación FBX a Art/FBX/Equipment/ y Content/Meshes/Equipment/.
7. Renderizado en Cycles a 64 muestras con Denoising y composición 2560x1440.
"""

import bpy
import bmesh
import math
import os
import shutil

R = math.radians

PROJECT_ROOT = r"F:\Dev\Game"
FBX_CONTENT_DIR = os.path.join(PROJECT_ROOT, "Content", "Meshes", "Equipment")
FBX_ART_DIR = os.path.join(PROJECT_ROOT, "Art", "FBX", "Equipment")
RENDERS_DIR = os.path.join(PROJECT_ROOT, "Art", "Renders")
ARTIFACT_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\b59ff04f-3c21-4ee5-94b0-8e8f899f8923"

os.makedirs(FBX_CONTENT_DIR, exist_ok=True)
os.makedirs(FBX_ART_DIR, exist_ok=True)
os.makedirs(RENDERS_DIR, exist_ok=True)

# Limpiar escena
bpy.ops.wm.read_factory_settings(use_empty=True)

# -----------------------------------------------------------------------------
# SHADERS PBR INDUSTRIALES DESGASTADOS (RUST BUCKET SCI-FI)
# -----------------------------------------------------------------------------
def create_weathered_pbr_material(name,
                                  color_clean,
                                  color_grime,
                                  color_wear,
                                  metallic,
                                  roughness_clean,
                                  roughness_worn,
                                  grunge_scale=12.0,
                                  bump_strength=0.18,
                                  noise_detail=10.0,
                                  emissive_color=(0, 0, 0, 1),
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

    # Coordenadas y mapeo
    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    tex_coord.location = (-750, 0)

    mapping = nodes.new(type='ShaderNodeMapping')
    mapping.location = (-580, 0)
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])

    # Ruido procedural de desgaste (grunge)
    noise_macro = nodes.new(type='ShaderNodeTexNoise')
    noise_macro.location = (-380, 150)
    noise_macro.inputs['Scale'].default_value = grunge_scale
    noise_macro.inputs['Detail'].default_value = noise_detail
    noise_macro.inputs['Roughness'].default_value = 0.72
    noise_macro.inputs['Lacunarity'].default_value = 2.2
    links.new(mapping.outputs['Vector'], noise_macro.inputs['Vector'])

    # Rampa de color base
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

    # Bump / Micro-relieve
    if bump_strength > 0.0:
        bump = nodes.new(type='ShaderNodeBump')
        bump.location = (120, -200)
        bump.inputs['Strength'].default_value = bump_strength
        bump.inputs['Distance'].default_value = 0.03
        links.new(noise_macro.outputs['Fac'], bump.inputs['Height'])
        links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    # Emisivo
    if emissive_strength > 0.0:
        bsdf.inputs['Emission Color'].default_value = emissive_color
        bsdf.inputs['Emission Strength'].default_value = emissive_strength

    links.new(bsdf.outputs['BSDF'], out_node.inputs['Surface'])
    return mat

# Materiales desgastados
MAT_DARK_TITANIUM = create_weathered_pbr_material(
    "M_DarkTitanium",
    color_clean=(0.065, 0.075, 0.085, 1.0),
    color_grime=(0.02, 0.02, 0.025, 1.0),
    color_wear=(0.25, 0.27, 0.30, 1.0),
    metallic=0.92,
    roughness_clean=0.32,
    roughness_worn=0.68,
    grunge_scale=14.0,
    bump_strength=0.18
)

MAT_HAZARD_YELLOW = create_weathered_pbr_material(
    "M_HazardYellow",
    color_clean=(0.80, 0.58, 0.05, 1.0),
    color_grime=(0.14, 0.09, 0.02, 1.0),
    color_wear=(0.32, 0.33, 0.35, 1.0),
    metallic=0.25,
    roughness_clean=0.35,
    roughness_worn=0.75,
    grunge_scale=12.0,
    bump_strength=0.22
)

MAT_RESCUE_RED = create_weathered_pbr_material(
    "M_RescueRed",
    color_clean=(0.68, 0.09, 0.07, 1.0),
    color_grime=(0.14, 0.035, 0.025, 1.0),
    color_wear=(0.35, 0.35, 0.38, 1.0),
    metallic=0.35,
    roughness_clean=0.30,
    roughness_worn=0.70,
    grunge_scale=12.0,
    bump_strength=0.20
)

MAT_FOAM_CYAN = create_weathered_pbr_material(
    "M_FoamTank_Cyan",
    color_clean=(0.05, 0.42, 0.52, 1.0),
    color_grime=(0.02, 0.09, 0.11, 1.0),
    color_wear=(0.30, 0.32, 0.35, 1.0),
    metallic=0.45,
    roughness_clean=0.28,
    roughness_worn=0.68,
    grunge_scale=10.0,
    bump_strength=0.16
)

MAT_CHROME_STEEL = create_weathered_pbr_material(
    "M_ChromeSteel",
    color_clean=(0.84, 0.86, 0.88, 1.0),
    color_grime=(0.16, 0.16, 0.18, 1.0),
    color_wear=(0.42, 0.44, 0.46, 1.0),
    metallic=0.98,
    roughness_clean=0.12,
    roughness_worn=0.42,
    grunge_scale=15.0,
    bump_strength=0.08
)

MAT_COPPER_COIL = create_weathered_pbr_material(
    "M_CopperCoil",
    color_clean=(0.86, 0.40, 0.16, 1.0),
    color_grime=(0.16, 0.07, 0.03, 1.0),
    color_wear=(0.38, 0.32, 0.28, 1.0),
    metallic=0.96,
    roughness_clean=0.20,
    roughness_worn=0.52,
    grunge_scale=18.0,
    bump_strength=0.15
)

MAT_RUBBER_BLACK = create_weathered_pbr_material(
    "M_RubberBlack",
    color_clean=(0.025, 0.025, 0.03, 1.0),
    color_grime=(0.012, 0.012, 0.012, 1.0),
    color_wear=(0.07, 0.07, 0.08, 1.0),
    metallic=0.0,
    roughness_clean=0.72,
    roughness_worn=0.90,
    grunge_scale=8.0,
    bump_strength=0.25
)

MAT_NET_LED_BLUE = create_weathered_pbr_material(
    "M_NetLED_Blue",
    color_clean=(0.05, 0.55, 1.0, 1.0),
    color_grime=(0.0, 0.12, 0.35, 1.0),
    color_wear=(0.8, 0.9, 1.0, 1.0),
    metallic=0.1,
    roughness_clean=0.15,
    roughness_worn=0.35,
    emissive_color=(0.12, 0.68, 1.0, 1.0),
    emissive_strength=3.0
)

MAT_STATUS_AMBER = create_weathered_pbr_material(
    "M_StatusAmber",
    color_clean=(0.95, 0.55, 0.05, 1.0),
    color_grime=(0.2, 0.1, 0.0, 1.0),
    color_wear=(1.0, 0.8, 0.4, 1.0),
    metallic=0.1,
    roughness_clean=0.2,
    roughness_worn=0.4,
    emissive_color=(1.0, 0.55, 0.05, 1.0),
    emissive_strength=2.5
)

MAT_GAUGE_WHITE = create_weathered_pbr_material(
    "M_GaugeDial",
    color_clean=(0.55, 0.56, 0.52, 1.0),
    color_grime=(0.18, 0.16, 0.14, 1.0),
    color_wear=(0.40, 0.40, 0.40, 1.0),
    metallic=0.05,
    roughness_clean=0.32,
    roughness_worn=0.65,
    grunge_scale=15.0,
    bump_strength=0.06
)

def apply_smooth(obj):
    """Aplica sombreado suave a todas las caras de la malla"""
    for p in obj.data.polygons:
        p.use_smooth = True

# -----------------------------------------------------------------------------
# 1. LANZADOR DE ESPUMA RETARDANTE (SM_FoamLauncher_Gun)
# -----------------------------------------------------------------------------
def build_foam_launcher():
    parts = []

    # Receptor central hexagonal con bisel
    bpy.ops.mesh.primitive_cylinder_add(radius=0.075, depth=0.48, vertices=8, location=(0, 0, 0), rotation=(0, R(90), 0))
    recv = bpy.context.active_object
    recv.name = "Foam_Receiver"
    apply_smooth(recv)
    recv.data.materials.append(MAT_DARK_TITANIUM)
    parts.append(recv)

    # Cubierta superior acanalada con nervaduras
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.02, 0, 0.075))
    top_rail = bpy.context.active_object
    top_rail.name = "Foam_TopRail"
    top_rail.scale = (0.42, 0.08, 0.035)
    bpy.ops.object.transform_apply(scale=True)
    apply_smooth(top_rail)
    top_rail.data.materials.append(MAT_DARK_TITANIUM)
    parts.append(top_rail)

    # Asa superior de transporte
    bpy.ops.mesh.primitive_torus_add(major_radius=0.08, minor_radius=0.012, location=(-0.02, 0, 0.12), rotation=(0, R(90), 0))
    carry_handle = bpy.context.active_object
    carry_handle.name = "Foam_CarryHandle"
    carry_handle.scale = (1.4, 0.8, 0.8)
    bpy.ops.object.transform_apply(scale=True)
    apply_smooth(carry_handle)
    carry_handle.data.materials.append(MAT_RUBBER_BLACK)
    parts.append(carry_handle)

    # Bridas de advertencia amarillas
    for i in range(3):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.082, depth=0.025, vertices=16, location=(-0.14 + i * 0.14, 0, 0), rotation=(0, R(90), 0))
        band = bpy.context.active_object
        band.name = f"Foam_Band_{i}"
        apply_smooth(band)
        band.data.materials.append(MAT_HAZARD_YELLOW)
        parts.append(band)

    # Cañón principal con camisa perforada
    bpy.ops.mesh.primitive_cylinder_add(radius=0.052, depth=0.35, vertices=24, location=(0.36, 0, 0), rotation=(0, R(90), 0))
    barrel = bpy.context.active_object
    barrel.name = "Foam_Barrel"
    apply_smooth(barrel)
    barrel.data.materials.append(MAT_DARK_TITANIUM)
    parts.append(barrel)

    # Camisa de enfriamiento perforada alrededor del cañón
    bpy.ops.mesh.primitive_cylinder_add(radius=0.062, depth=0.22, vertices=24, location=(0.32, 0, 0), rotation=(0, R(90), 0))
    shroud = bpy.context.active_object
    shroud.name = "Foam_BarrelShroud"
    apply_smooth(shroud)
    shroud.data.materials.append(MAT_CHROME_STEEL)
    parts.append(shroud)

    # Boquilla difusora cónica acampanada tipo Venturi
    bpy.ops.mesh.primitive_cone_add(radius1=0.050, radius2=0.098, depth=0.14, vertices=24, location=(0.60, 0, 0), rotation=(0, R(-90), 0))
    diffuser = bpy.context.active_object
    diffuser.name = "Foam_DiffuserMuzzle"
    apply_smooth(diffuser)
    diffuser.data.materials.append(MAT_HAZARD_YELLOW)
    parts.append(diffuser)

    # Interior hueco de la boquilla (anillo interno)
    bpy.ops.mesh.primitive_cone_add(radius1=0.040, radius2=0.085, depth=0.13, vertices=24, location=(0.61, 0, 0), rotation=(0, R(-90), 0))
    inner_bore = bpy.context.active_object
    inner_bore.name = "Foam_InnerBore"
    apply_smooth(inner_bore)
    inner_bore.data.materials.append(MAT_DARK_TITANIUM)
    parts.append(inner_bore)

    # 4 aletas deflectoras radiales de dispersión en la boca
    for i in range(4):
        ang = i * 90
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.62, 0, 0))
        fin = bpy.context.active_object
        fin.name = f"Foam_Fin_{i}"
        fin.scale = (0.06, 0.008, 0.045)
        bpy.ops.object.transform_apply(scale=True)
        fin.rotation_euler = (R(ang), 0, 0)
        bpy.ops.object.transform_apply(rotation=True)
        apply_smooth(fin)
        fin.data.materials.append(MAT_CHROME_STEEL)
        parts.append(fin)

    # Tanque ventral presurizado de espumógeno químico (suavizado de alta densidad)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.082, depth=0.34, vertices=32, location=(0.05, 0, -0.16), rotation=(0, R(90), 0))
    tank = bpy.context.active_object
    tank.name = "Foam_Tank"
    apply_smooth(tank)
    tank.data.materials.append(MAT_FOAM_CYAN)
    parts.append(tank)

    # Tapas semiesféricas de domo del tanque
    for sign, x_pos in [(-1, -0.12), (1, 0.22)]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.0818, segments=32, ring_count=18, location=(x_pos, 0, -0.16))
        cap = bpy.context.active_object
        cap.name = f"Foam_TankCap_{sign}"
        apply_smooth(cap)
        cap.data.materials.append(MAT_FOAM_CYAN)
        parts.append(cap)

    # Abrazaderas de acero de retención del tanque (2 unidades)
    for x_clamp in [-0.05, 0.15]:
        bpy.ops.mesh.primitive_torus_add(major_radius=0.086, minor_radius=0.012, location=(x_clamp, 0, -0.16), rotation=(0, R(90), 0))
        clamp = bpy.context.active_object
        clamp.name = f"Foam_TankClamp_{x_clamp}"
        apply_smooth(clamp)
        clamp.data.materials.append(MAT_DARK_TITANIUM)
        parts.append(clamp)

    # Manómetro analógico lateral de presión del tanque
    bpy.ops.mesh.primitive_cylinder_add(radius=0.030, depth=0.022, vertices=24, location=(0.05, 0.085, -0.14), rotation=(R(90), 0, 0))
    gauge = bpy.context.active_object
    gauge.name = "Foam_GaugeHousing"
    apply_smooth(gauge)
    gauge.data.materials.append(MAT_CHROME_STEEL)
    parts.append(gauge)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.026, depth=0.005, vertices=24, location=(0.05, 0.097, -0.14), rotation=(R(90), 0, 0))
    gauge_face = bpy.context.active_object
    gauge_face.name = "Foam_GaugeFace"
    apply_smooth(gauge_face)
    gauge_face.data.materials.append(MAT_GAUGE_WHITE)
    parts.append(gauge_face)

    # Aguja indicadora roja
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.05, 0.100, -0.14))
    needle = bpy.context.active_object
    needle.name = "Foam_GaugeNeedle"
    needle.scale = (0.004, 0.003, 0.02)
    needle.rotation_euler = (0, 0, R(35))
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    needle.data.materials.append(MAT_RESCUE_RED)
    parts.append(needle)

    # Conducto de alta presión de acero inoxidable que conecta tanque y recámara
    bpy.ops.mesh.primitive_cylinder_add(radius=0.013, depth=0.16, vertices=16, location=(-0.10, 0.045, -0.08), rotation=(R(28), 0, 0))
    hose = bpy.context.active_object
    hose.name = "Foam_FeedLine"
    apply_smooth(hose)
    hose.data.materials.append(MAT_CHROME_STEEL)
    parts.append(hose)

    # Empuñadura trasera ergonómica conectada sólidamente al chasis
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.24, 0, -0.10))
    rear_grip = bpy.context.active_object
    rear_grip.name = "Foam_RearGrip"
    rear_grip.scale = (0.055, 0.04, 0.16)
    rear_grip.rotation_euler = (0, R(-18), 0)
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    apply_smooth(rear_grip)
    rear_grip.data.materials.append(MAT_RUBBER_BLACK)
    parts.append(rear_grip)

    # Culatín posterior reforzado
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.28, 0, 0.0))
    buttstock = bpy.context.active_object
    buttstock.name = "Foam_Buttstock"
    buttstock.scale = (0.08, 0.065, 0.12)
    bpy.ops.object.transform_apply(scale=True)
    apply_smooth(buttstock)
    buttstock.data.materials.append(MAT_DARK_TITANIUM)
    parts.append(buttstock)

    # Guardamonte y gatillo trasero
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.19, 0, -0.055))
    trigger_guard = bpy.context.active_object
    trigger_guard.name = "Foam_TriggerGuard"
    trigger_guard.scale = (0.07, 0.018, 0.045)
    bpy.ops.object.transform_apply(scale=True)
    apply_smooth(trigger_guard)
    trigger_guard.data.materials.append(MAT_DARK_TITANIUM)
    parts.append(trigger_guard)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.19, 0, -0.05))
    trigger = bpy.context.active_object
    trigger.name = "Foam_Trigger"
    trigger.scale = (0.015, 0.012, 0.025)
    bpy.ops.object.transform_apply(scale=True)
    trigger.data.materials.append(MAT_RESCUE_RED)
    parts.append(trigger)

    # Empuñadura delantera táctica vertical estriada
    bpy.ops.mesh.primitive_cylinder_add(radius=0.024, depth=0.17, vertices=20, location=(0.26, 0, -0.11))
    foregrip = bpy.context.active_object
    foregrip.name = "Foam_Foregrip"
    apply_smooth(foregrip)
    foregrip.data.materials.append(MAT_RUBBER_BLACK)
    parts.append(foregrip)

    # Selector superior de modo (Chorro / Abanico)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.022, depth=0.03, vertices=16, location=(-0.02, 0, 0.095))
    selector = bpy.context.active_object
    selector.name = "Foam_ModeSelector"
    apply_smooth(selector)
    selector.data.materials.append(MAT_CHROME_STEEL)
    parts.append(selector)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.02, 0, 0.112))
    lever = bpy.context.active_object
    lever.name = "Foam_SelectorLever"
    lever.scale = (0.045, 0.012, 0.008)
    bpy.ops.object.transform_apply(scale=True)
    lever.data.materials.append(MAT_RESCUE_RED)
    parts.append(lever)

    # LED indicador de estado
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.014, segments=16, ring_count=10, location=(0.08, 0.07, 0.04))
    led = bpy.context.active_object
    led.name = "Foam_StatusLED"
    apply_smooth(led)
    led.data.materials.append(MAT_STATUS_AMBER)
    parts.append(led)

    # Unir todas las partes
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = recv
    bpy.ops.object.join()

    foam_gun = bpy.context.active_object
    foam_gun.name = "SM_FoamLauncher_Gun"
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

    # UCX Convex Collider
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=foam_gun.location)
    ucx_foam = bpy.context.active_object
    ucx_foam.name = "UCX_SM_FoamLauncher_Gun"
    ucx_foam.scale = (0.96, 0.28, 0.40)
    bpy.ops.object.transform_apply(scale=True)
    ucx_foam.display_type = 'WIRE'

    return foam_gun, ucx_foam

# -----------------------------------------------------------------------------
# 2. LANZA-REDES ELECTROSTÁTICO (SM_NetLauncher_Gun)
# -----------------------------------------------------------------------------
def build_net_launcher():
    parts = []

    # Receptor central compacto y robusto con bisel lateral
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
    recv = bpy.context.active_object
    recv.name = "Net_Receiver"
    recv.scale = (0.36, 0.16, 0.16)
    bpy.ops.object.transform_apply(scale=True)
    apply_smooth(recv)
    recv.data.materials.append(MAT_DARK_TITANIUM)
    parts.append(recv)

    # Cubierta superior con carril Picatinny y visor óptico
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.095))
    rail = bpy.context.active_object
    rail.name = "Net_TopRail"
    rail.scale = (0.32, 0.06, 0.03)
    bpy.ops.object.transform_apply(scale=True)
    apply_smooth(rail)
    rail.data.materials.append(MAT_DARK_TITANIUM)
    parts.append(rail)

    # Visor óptico holográfico / telemetría
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.04, 0, 0.13))
    sight = bpy.context.active_object
    sight.name = "Net_Sight"
    sight.scale = (0.10, 0.045, 0.04)
    bpy.ops.object.transform_apply(scale=True)
    apply_smooth(sight)
    sight.data.materials.append(MAT_DARK_TITANIUM)
    parts.append(sight)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.04, 0, 0.13))
    sight_lens = bpy.context.active_object
    sight_lens.name = "Net_SightLens"
    sight_lens.scale = (0.104, 0.032, 0.024)
    bpy.ops.object.transform_apply(scale=True)
    sight_lens.data.materials.append(MAT_NET_LED_BLUE)
    parts.append(sight_lens)

    # Tambor central para cartucho de red plegada
    bpy.ops.mesh.primitive_cylinder_add(radius=0.068, depth=0.20, vertices=24, location=(0.04, 0, 0), rotation=(0, R(90), 0))
    drum = bpy.context.active_object
    drum.name = "Net_CanisterDrum"
    apply_smooth(drum)
    drum.data.materials.append(MAT_DARK_TITANIUM)
    parts.append(drum)

    # Ventana de inspección luminosa del cartucho de red
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.04, 0, 0.070))
    canister_view = bpy.context.active_object
    canister_view.name = "Net_CanisterWindow"
    canister_view.scale = (0.14, 0.09, 0.015)
    bpy.ops.object.transform_apply(scale=True)
    apply_smooth(canister_view)
    canister_view.data.materials.append(MAT_NET_LED_BLUE)
    parts.append(canister_view)

    # Matriz de 4 cañones divergentes huecos (con anillo de boca y ánima interior)
    barrel_offsets = [
        (0.045, 0.045, 6.0, 6.0),    # Arriba-Derecha
        (-0.045, 0.045, -6.0, 6.0),  # Arriba-Izquierda
        (0.045, -0.045, 6.0, -6.0),  # Abajo-Derecha
        (-0.045, -0.045, -6.0, -6.0) # Abajo-Izquierda
    ]

    for idx, (oy, oz, pitch_deg, yaw_deg) in enumerate(barrel_offsets):
        # Tubo eyector exterior
        bpy.ops.mesh.primitive_cylinder_add(radius=0.026, depth=0.30, vertices=20, location=(0.30, oy, oz), rotation=(0, R(90), 0))
        barrel = bpy.context.active_object
        barrel.name = f"Net_Barrel_{idx}"
        barrel.rotation_euler = (0, R(90 + pitch_deg), R(yaw_deg))
        bpy.ops.object.transform_apply(rotation=True)
        apply_smooth(barrel)
        barrel.data.materials.append(MAT_DARK_TITANIUM)
        parts.append(barrel)

        # Collarín de acero cromado en la boca
        bpy.ops.mesh.primitive_cylinder_add(radius=0.030, depth=0.04, vertices=20, location=(0.43, oy * 1.25, oz * 1.25), rotation=(0, R(90), 0))
        muzzle_ring = bpy.context.active_object
        muzzle_ring.name = f"Net_MuzzleRing_{idx}"
        muzzle_ring.rotation_euler = (0, R(90 + pitch_deg), R(yaw_deg))
        bpy.ops.object.transform_apply(rotation=True)
        apply_smooth(muzzle_ring)
        muzzle_ring.data.materials.append(MAT_CHROME_STEEL)
        parts.append(muzzle_ring)

        # Ánima interior hueca (oscura)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.020, depth=0.10, vertices=16, location=(0.435, oy * 1.25, oz * 1.25), rotation=(0, R(90), 0))
        bore = bpy.context.active_object
        bore.name = f"Net_Bore_{idx}"
        bore.rotation_euler = (0, R(90 + pitch_deg), R(yaw_deg))
        bpy.ops.object.transform_apply(rotation=True)
        apply_smooth(bore)
        bore.data.materials.append(MAT_RUBBER_BLACK)
        parts.append(bore)

    # Bobinas electrostáticas de cobre expuestas (2 bobinas toroidales de alta fidelidad)
    for idx, x_coil in enumerate([-0.06, 0.14]):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.076, minor_radius=0.014, location=(x_coil, 0, 0), rotation=(0, R(90), 0))
        coil = bpy.context.active_object
        coil.name = f"Net_CopperCoil_{idx}"
        apply_smooth(coil)
        coil.data.materials.append(MAT_COPPER_COIL)
        parts.append(coil)

    # Módulo de batería desmontable de alto voltaje en la base inferior
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.05, 0, -0.13))
    battery = bpy.context.active_object
    battery.name = "Net_HighVoltBattery"
    battery.scale = (0.18, 0.12, 0.10)
    bpy.ops.object.transform_apply(scale=True)
    apply_smooth(battery)
    battery.data.materials.append(MAT_HAZARD_YELLOW)
    parts.append(battery)

    # Barra LED de nivel de carga electrostática en la batería (ambos lados)
    for sign in [-1, 1]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.05, sign * 0.062, -0.13))
        led_bar = bpy.context.active_object
        led_bar.name = f"Net_ChargeBarLED_{sign}"
        led_bar.scale = (0.12, 0.008, 0.025)
        bpy.ops.object.transform_apply(scale=True)
        apply_smooth(led_bar)
        led_bar.data.materials.append(MAT_NET_LED_BLUE)
        parts.append(led_bar)

    # Módulo de transición ergonómica / puente inferior entre receptor y empuñadura
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.16, 0, -0.07))
    grip_tang = bpy.context.active_object
    grip_tang.name = "Net_GripTang"
    grip_tang.scale = (0.12, 0.07, 0.08)
    bpy.ops.object.transform_apply(scale=True)
    apply_smooth(grip_tang)
    grip_tang.data.materials.append(MAT_DARK_TITANIUM)
    parts.append(grip_tang)

    # Empuñadura trasera ergonómica (integrada sólidamente con la carcasa)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.18, 0, -0.13))
    rear_grip = bpy.context.active_object
    rear_grip.name = "Net_RearGrip"
    rear_grip.scale = (0.05, 0.038, 0.16)
    rear_grip.rotation_euler = (0, R(-15), 0)
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    apply_smooth(rear_grip)
    rear_grip.data.materials.append(MAT_RUBBER_BLACK)
    parts.append(rear_grip)

    # Tubo amortiguador y culatín esquelético trasero
    bpy.ops.mesh.primitive_cylinder_add(radius=0.022, depth=0.18, vertices=16, location=(-0.25, 0, 0.02), rotation=(0, R(90), 0))
    buffer_tube = bpy.context.active_object
    buffer_tube.name = "Net_BufferTube"
    apply_smooth(buffer_tube)
    buffer_tube.data.materials.append(MAT_DARK_TITANIUM)
    parts.append(buffer_tube)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.34, 0, 0.0))
    stock_pad = bpy.context.active_object
    stock_pad.name = "Net_StockPad"
    stock_pad.scale = (0.04, 0.055, 0.14)
    bpy.ops.object.transform_apply(scale=True)
    apply_smooth(stock_pad)
    stock_pad.data.materials.append(MAT_RUBBER_BLACK)
    parts.append(stock_pad)

    # Guardamonte y gatillo
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.13, 0, -0.07))
    trigger_guard = bpy.context.active_object
    trigger_guard.name = "Net_TriggerGuard"
    trigger_guard.scale = (0.065, 0.016, 0.04)
    bpy.ops.object.transform_apply(scale=True)
    apply_smooth(trigger_guard)
    trigger_guard.data.materials.append(MAT_DARK_TITANIUM)
    parts.append(trigger_guard)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.13, 0, -0.065))
    trigger = bpy.context.active_object
    trigger.name = "Net_Trigger"
    trigger.scale = (0.015, 0.012, 0.026)
    bpy.ops.object.transform_apply(scale=True)
    trigger.data.materials.append(MAT_RESCUE_RED)
    parts.append(trigger)

    # Empuñadura táctica delantera en ángulo con textura antideslizante
    bpy.ops.mesh.primitive_cylinder_add(radius=0.024, depth=0.16, vertices=20, location=(0.18, 0, -0.12), rotation=(0, R(12), 0))
    foregrip = bpy.context.active_object
    foregrip.name = "Net_Foregrip"
    apply_smooth(foregrip)
    foregrip.data.materials.append(MAT_RUBBER_BLACK)
    parts.append(foregrip)

    # Condensadores cilíndricos superiores gemelos
    for sign in [-1, 1]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.018, depth=0.20, vertices=16, location=(-0.02, sign * 0.052, 0.095), rotation=(0, R(90), 0))
        cap = bpy.context.active_object
        cap.name = f"Net_Capacitor_{sign}"
        apply_smooth(cap)
        cap.data.materials.append(MAT_CHROME_STEEL)
        parts.append(cap)

    # Unir todas las partes
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = recv
    bpy.ops.object.join()

    net_gun = bpy.context.active_object
    net_gun.name = "SM_NetLauncher_Gun"
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

    # UCX Convex Collider
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=net_gun.location)
    ucx_net = bpy.context.active_object
    ucx_net.name = "UCX_SM_NetLauncher_Gun"
    ucx_net.scale = (0.88, 0.34, 0.34)
    bpy.ops.object.transform_apply(scale=True)
    ucx_net.display_type = 'WIRE'

    return net_gun, ucx_net

# -----------------------------------------------------------------------------
# 3. GATO HIDRÁULICO DE RESCATE (SM_HydraulicJack_Tool)
# -----------------------------------------------------------------------------
def build_hydraulic_jack():
    parts = []

    # Zapata de sustentación inferior masiva (Z = eje vertical de elevación)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.025))
    base = bpy.context.active_object
    base.name = "Jack_BaseFoot"
    base.scale = (0.34, 0.24, 0.05)
    bpy.ops.object.transform_apply(scale=True)
    apply_smooth(base)
    base.data.materials.append(MAT_DARK_TITANIUM)
    parts.append(base)

    # Dientes antideslizantes inferiores en la zapata (para agarrar suelos metálicos)
    for ix in [-0.12, -0.04, 0.04, 0.12]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ix, 0, 0.003))
        lug = bpy.context.active_object
        lug.name = f"Jack_SerratedLug_{ix}"
        lug.scale = (0.022, 0.20, 0.006)
        bpy.ops.object.transform_apply(scale=True)
        apply_smooth(lug)
        lug.data.materials.append(MAT_CHROME_STEEL)
        parts.append(lug)

    # Camisa exterior del cilindro hidráulico
    bpy.ops.mesh.primitive_cylinder_add(radius=0.078, depth=0.28, vertices=32, location=(0, 0, 0.18))
    outer_cyl = bpy.context.active_object
    outer_cyl.name = "Jack_OuterCylinder"
    apply_smooth(outer_cyl)
    outer_cyl.data.materials.append(MAT_RESCUE_RED)
    parts.append(outer_cyl)

    # Franja amarilla de advertencia industrial en la camisa (4mm holgura anti Z-fighting)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.082, depth=0.06, vertices=32, location=(0, 0, 0.22))
    warn_band = bpy.context.active_object
    warn_band.name = "Jack_WarningBand"
    apply_smooth(warn_band)
    warn_band.data.materials.append(MAT_HAZARD_YELLOW)
    parts.append(warn_band)

    # 4 nervaduras de refuerzo estructural en la camisa cilíndrica
    for ang in [0, 90, 180, 270]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.18))
        rib = bpy.context.active_object
        rib.name = f"Jack_Rib_{ang}"
        rib.scale = (0.014, 0.024, 0.26)
        bpy.ops.object.transform_apply(scale=True)
        rib.rotation_euler = (0, 0, R(ang))
        rib.location = (math.cos(R(ang)) * 0.080, math.sin(R(ang)) * 0.080, 0.18)
        bpy.ops.object.transform_apply(location=True, rotation=True)
        apply_smooth(rib)
        rib.data.materials.append(MAT_DARK_TITANIUM)
        parts.append(rib)

    # Cuello superior sellado con prensaestopas
    bpy.ops.mesh.primitive_cylinder_add(radius=0.084, depth=0.035, vertices=32, location=(0, 0, 0.325))
    gland = bpy.context.active_object
    gland.name = "Jack_GlandCollar"
    apply_smooth(gland)
    gland.data.materials.append(MAT_DARK_TITANIUM)
    parts.append(gland)

    # Vástago / Pistón telescópico interior de acero cromado pulido
    bpy.ops.mesh.primitive_cylinder_add(radius=0.050, depth=0.24, vertices=28, location=(0, 0, 0.42))
    piston = bpy.context.active_object
    piston.name = "Jack_ChromePiston"
    apply_smooth(piston)
    piston.data.materials.append(MAT_CHROME_STEEL)
    parts.append(piston)

    # Marcas métricas grabadas en el pistón (anillos de medición)
    for i in range(4):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.0505, minor_radius=0.0015, location=(0, 0, 0.34 + i * 0.045))
        metric_ring = bpy.context.active_object
        metric_ring.name = f"Jack_MetricRing_{i}"
        apply_smooth(metric_ring)
        metric_ring.data.materials.append(MAT_DARK_TITANIUM)
        parts.append(metric_ring)

    # Cabezal de apoyo articulado superior (Silla en V para encajar bajo vigas)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.54))
    head_base = bpy.context.active_object
    head_base.name = "Jack_SaddleBase"
    head_base.scale = (0.14, 0.12, 0.032)
    bpy.ops.object.transform_apply(scale=True)
    apply_smooth(head_base)
    head_base.data.materials.append(MAT_DARK_TITANIUM)
    parts.append(head_base)

    # Alas estriadas en V del cabezal
    for sign in [-1, 1]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sign * 0.060, 0, 0.565))
        v_flange = bpy.context.active_object
        v_flange.name = f"Jack_VFlange_{sign}"
        v_flange.scale = (0.022, 0.11, 0.038)
        bpy.ops.object.transform_apply(scale=True)
        apply_smooth(v_flange)
        v_flange.data.materials.append(MAT_CHROME_STEEL)
        parts.append(v_flange)

    # Bloque de válvulas y bomba hidráulica lateral
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.11, 0, 0.12))
    valve_block = bpy.context.active_object
    valve_block.name = "Jack_ValveBlock"
    valve_block.scale = (0.085, 0.11, 0.13)
    bpy.ops.object.transform_apply(scale=True)
    apply_smooth(valve_block)
    valve_block.data.materials.append(MAT_DARK_TITANIUM)
    parts.append(valve_block)

    # Horquilla/Clevis de montaje del pivote en el bloque de válvulas
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.13, 0, 0.155))
    clevis = bpy.context.active_object
    clevis.name = "Jack_PivotClevis"
    clevis.scale = (0.04, 0.055, 0.04)
    bpy.ops.object.transform_apply(scale=True)
    apply_smooth(clevis)
    clevis.data.materials.append(MAT_DARK_TITANIUM)
    parts.append(clevis)

    # Articulación pivotante cilíndrica de la palanca
    bpy.ops.mesh.primitive_cylinder_add(radius=0.018, depth=0.05, vertices=20, location=(0.135, 0, 0.155), rotation=(R(90), 0, 0))
    pivot = bpy.context.active_object
    pivot.name = "Jack_LeverPivot"
    apply_smooth(pivot)
    pivot.data.materials.append(MAT_CHROME_STEEL)
    parts.append(pivot)

    # Palanca manual de bombeo (brazo tubular con empuñadura ergonómica que parte desde el pivote)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.014, depth=0.30, vertices=16, location=(0.23, 0, 0.27), rotation=(0, R(40), 0))
    lever_arm = bpy.context.active_object
    lever_arm.name = "Jack_PumpLeverArm"
    apply_smooth(lever_arm)
    lever_arm.data.materials.append(MAT_CHROME_STEEL)
    parts.append(lever_arm)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.019, depth=0.12, vertices=16, location=(0.30, 0, 0.35), rotation=(0, R(40), 0))
    lever_grip = bpy.context.active_object
    lever_grip.name = "Jack_LeverRubberGrip"
    apply_smooth(lever_grip)
    lever_grip.data.materials.append(MAT_RUBBER_BLACK)
    parts.append(lever_grip)

    # Manómetro analógico de presión y tonelaje
    bpy.ops.mesh.primitive_cylinder_add(radius=0.034, depth=0.024, vertices=24, location=(0.0, 0.115, 0.22), rotation=(R(90), 0, 0))
    gauge_body = bpy.context.active_object
    gauge_body.name = "Jack_GaugeBody"
    apply_smooth(gauge_body)
    gauge_body.data.materials.append(MAT_CHROME_STEEL)
    parts.append(gauge_body)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.029, depth=0.005, vertices=24, location=(0.0, 0.128, 0.22), rotation=(R(90), 0, 0))
    gauge_dial = bpy.context.active_object
    gauge_dial.name = "Jack_GaugeDial"
    apply_smooth(gauge_dial)
    gauge_dial.data.materials.append(MAT_GAUGE_WHITE)
    parts.append(gauge_dial)

    # Aguja indicadora
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.131, 0.22))
    jack_needle = bpy.context.active_object
    jack_needle.name = "Jack_GaugeNeedle"
    jack_needle.scale = (0.004, 0.003, 0.022)
    jack_needle.rotation_euler = (0, 0, R(-40))
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    jack_needle.data.materials.append(MAT_RESCUE_RED)
    parts.append(jack_needle)

    # Válvula de alivio/descompresión (tornillo estriado amarillo)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.022, depth=0.032, vertices=16, location=(0.11, -0.065, 0.10), rotation=(R(90), 0, 0))
    relief_valv = bpy.context.active_object
    relief_valv.name = "Jack_ReliefValve"
    apply_smooth(relief_valv)
    relief_valv.data.materials.append(MAT_HAZARD_YELLOW)
    parts.append(relief_valv)

    # Asa de transporte ergonómica superior
    bpy.ops.mesh.primitive_torus_add(major_radius=0.065, minor_radius=0.013, location=(-0.095, 0, 0.24), rotation=(0, R(90), 0))
    handle = bpy.context.active_object
    handle.name = "Jack_CarryHandle"
    apply_smooth(handle)
    handle.data.materials.append(MAT_RUBBER_BLACK)
    parts.append(handle)

    # Unir todas las partes en un objeto único
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = base
    bpy.ops.object.join()

    jack_tool = bpy.context.active_object
    jack_tool.name = "SM_HydraulicJack_Tool"
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')

    # UCX Convex Collider
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=jack_tool.location)
    ucx_jack = bpy.context.active_object
    ucx_jack.name = "UCX_SM_HydraulicJack_Tool"
    ucx_jack.scale = (0.44, 0.34, 0.62)
    bpy.ops.object.transform_apply(scale=True)
    ucx_jack.display_type = 'WIRE'

    return jack_tool, ucx_jack

# -----------------------------------------------------------------------------
# EJECUCIÓN DE CONSTRUCCIÓN
# -----------------------------------------------------------------------------
print("[1/5] Modelando Lanzador de Espuma Retardante (SM_FoamLauncher_Gun)...")
foam_gun, ucx_foam = build_foam_launcher()

print("[2/5] Modelando Lanza-Redes Electrostático (SM_NetLauncher_Gun)...")
net_gun, ucx_net = build_net_launcher()

print("[3/5] Modelando Gato Hidráulico de Rescate (SM_HydraulicJack_Tool)...")
jack_tool, ucx_jack = build_hydraulic_jack()

# -----------------------------------------------------------------------------
# EXPORTACIÓN FBX
# -----------------------------------------------------------------------------
tools_to_export = [
    ("SM_FoamLauncher_Gun", foam_gun, ucx_foam),
    ("SM_NetLauncher_Gun", net_gun, ucx_net),
    ("SM_HydraulicJack_Tool", jack_tool, ucx_jack)
]

print("[4/5] Exportando mallas FBX con colisiones UCX...")
for mesh_name, mesh_obj, ucx_obj in tools_to_export:
    bpy.ops.object.select_all(action='DESELECT')
    mesh_obj.select_set(True)
    ucx_obj.select_set(True)
    bpy.context.view_layer.objects.active = mesh_obj

    # Guardar en Art/FBX/Equipment/
    fbx_art_path = os.path.join(FBX_ART_DIR, f"{mesh_name}.fbx")
    bpy.ops.export_scene.fbx(
        filepath=fbx_art_path,
        use_selection=True,
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_ALL',
        axis_forward='-Z',
        axis_up='Y',
        mesh_smooth_type='FACE'
    )

    # Copiar a Content/Meshes/Equipment/
    fbx_content_path = os.path.join(FBX_CONTENT_DIR, f"{mesh_name}.fbx")
    shutil.copy2(fbx_art_path, fbx_content_path)
    print(f"  [OK] Exportado: {fbx_art_path}")

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE ESTUDIO Y RENDERIZADO SHOWCASE (CYCLES)
# -----------------------------------------------------------------------------
print("[5/5] Configurando iluminación de estudio y renderizando showcase en Cycles...")

scene = bpy.context.scene
scene.render.engine = 'CYCLES' if bpy.context.preferences.addons.get('cycles') else 'BLENDER_EEVEE_NEXT'
if scene.render.engine == 'CYCLES':
    scene.cycles.samples = 64
    scene.cycles.use_denoising = True

scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.film_transparent = False

# Iluminación de estudio
world = bpy.data.worlds.new("StudioWorld")
scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes.get("Background")
if bg_node:
    bg_node.inputs['Color'].default_value = (0.010, 0.012, 0.016, 1.0)
    bg_node.inputs['Strength'].default_value = 0.35

# Pedestal de presentación metálico industrial
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, -0.30))
pedestal = bpy.context.active_object
pedestal.name = "Showcase_Pedestal"
pedestal.scale = (5.5, 3.5, 0.1)
bpy.ops.object.transform_apply(scale=True)
apply_smooth(pedestal)
pedestal.data.materials.append(MAT_DARK_TITANIUM)

# Luces de estudio calibradas
def add_light(name, light_type, energy, color, location):
    light_data = bpy.data.lights.new(name=name, type=light_type)
    light_data.energy = energy
    light_data.color = color
    light_obj = bpy.data.objects.new(name=name, object_data=light_data)
    light_obj.location = location
    scene.collection.objects.link(light_obj)
    return light_obj

add_light("KeyLight", 'AREA', 1400.0, (1.0, 0.96, 0.92), (-1.5, -2.4, 2.2))
add_light("FillLight", 'AREA', 500.0, (0.55, 0.72, 0.95), (2.2, -1.8, 1.5))
add_light("RimLightCyan", 'SPOT', 1600.0, (0.1, 0.75, 1.0), (0.0, 2.6, 2.4))
add_light("BottomBounce", 'POINT', 280.0, (0.85, 0.55, 0.2), (0.0, -0.8, 0.1))

# Cámara de estudio
cam_data = bpy.data.cameras.new("ShowcaseCam")
cam_obj = bpy.data.objects.new("ShowcaseCam", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj

cam_target = bpy.data.objects.new("CamTarget", None)
scene.collection.objects.link(cam_target)

constraint = cam_obj.constraints.new(type='TRACK_TO')
constraint.target = cam_target
constraint.track_axis = 'TRACK_NEGATIVE_Z'
constraint.up_axis = 'UP_Y'

# Desactivar render de colisionadores UCX
ucx_foam.hide_render = True
ucx_net.hide_render = True
ucx_jack.hide_render = True

# Configuraciones de cámara con encuadre heroico y pedestal asentado (sin hundimiento)
render_configs = {
    "arsenal_all": {
        "foam_pos":   (-0.68, 0.10, 0.04),    "foam_rot": (0, R(-8), R(-15)),       "foam_vis": True,
        "net_pos":    (0.68, 0.08, 0.04),     "net_rot":  (0, R(8), R(15)),         "net_vis": True,
        "jack_pos":   (0.0, 0.15, 0.045),     "jack_rot": (0, 0, R(-20)),           "jack_vis": True,
        "cam_pos":    (0.0, -2.60, 0.85),
        "target_pos": (0.0, 0.10, 0.08),
        "lens":       38.0
    },
    "foam_closeup": {
        "foam_pos":   (0.0, 0.0, 0.05),       "foam_rot": (R(4), R(-6), R(-15)),    "foam_vis": True,
        "net_pos":    (0, 0, 0),              "net_rot":  (0, 0, 0),                "net_vis": False,
        "jack_pos":   (0, 0, 0),              "jack_rot": (0, 0, 0),                "jack_vis": False,
        "cam_pos":    (0.0, -2.20, 0.35),
        "target_pos": (0.05, 0.0, 0.02),
        "lens":       40.0
    },
    "net_closeup": {
        "foam_pos":   (0, 0, 0),              "foam_rot": (0, 0, 0),                "foam_vis": False,
        "net_pos":    (0.0, 0.0, 0.02),       "net_rot":  (R(4), R(6), R(18)),      "net_vis": True,
        "jack_pos":   (0, 0, 0),              "jack_rot": (0, 0, 0),                "jack_vis": False,
        "cam_pos":    (0.0, -2.15, 0.30),
        "target_pos": (0.02, 0.0, 0.0),
        "lens":       40.0
    },
    "jack_closeup": {
        "foam_pos":   (0, 0, 0),              "foam_rot": (0, 0, 0),                "foam_vis": False,
        "net_pos":    (0, 0, 0),              "net_rot":  (0, 0, 0),                "net_vis": False,
        "jack_pos":   (0.0, 0.0, 0.045),      "jack_rot": (0, 0, R(-25)),           "jack_vis": True,
        "cam_pos":    (0.0, -2.10, 0.38),
        "target_pos": (0.0, 0.0, 0.05),
        "lens":       42.0
    }
}

rendered_files = []
for shot_name, cfg in render_configs.items():
    foam_gun.location = cfg["foam_pos"]
    foam_gun.rotation_euler = cfg["foam_rot"]
    foam_gun.hide_render = not cfg["foam_vis"]

    net_gun.location = cfg["net_pos"]
    net_gun.rotation_euler = cfg["net_rot"]
    net_gun.hide_render = not cfg["net_vis"]

    jack_tool.location = cfg["jack_pos"]
    jack_tool.rotation_euler = cfg["jack_rot"]
    jack_tool.hide_render = not cfg["jack_vis"]

    cam_obj.location = cfg["cam_pos"]
    cam_target.location = cfg["target_pos"]
    cam_data.lens = cfg["lens"]
    bpy.context.view_layer.update()

    out_file = os.path.join(RENDERS_DIR, f"Showcase_Lote3_{shot_name}.png")
    scene.render.filepath = out_file
    bpy.ops.render.render(write_still=True)
    rendered_files.append(out_file)
    print(f"  [OK] Renderizado cuadrante: {out_file}")

# Guardar escena Blender .blend
blend_path = os.path.join(PROJECT_ROOT, "Art", "Blender", "Lote3_Herramientas_Especiales.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f"[OK] Archivo Blender guardado: {blend_path}")

# Composición 2x2 en 2560x1440
try:
    from PIL import Image, ImageDraw, ImageFont

    canvas = Image.new("RGB", (2560, 1440), (12, 14, 18))
    positions = [(0, 0), (1280, 0), (0, 720), (1280, 720)]
    labels = [
        "LOTE 3 DE HERRAMIENTAS ESPECIALES - ASTRA HAZARD (GDD SEC. 8)",
        "LANZADOR DE ESPUMA RETARDANTE (TANQUE CRIOGENICO, VENTURI Y DEFLECTOR)",
        "LANZA-REDES ELECTROSTATICO (CANON CUADRUPLE DIVERGENTE, BOBINAS Y BATERIA)",
        "GATO HIDRAULICO DE RESCATE 15T (BASE DENTADA, EMBOLO CROMADO Y SILLA EN V)"
    ]

    font = None
    for font_path in [r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\consola.ttf"]:
        if os.path.exists(font_path):
            try:
                font = ImageFont.truetype(font_path, 22)
                break
            except Exception:
                pass
    if not font:
        font = ImageFont.load_default()

    draw = ImageDraw.Draw(canvas)

    for i, shot_file in enumerate(rendered_files):
        if os.path.exists(shot_file):
            img = Image.open(shot_file)
            img = img.resize((1280, 720), Image.Resampling.LANCZOS)
            canvas.paste(img, positions[i])

            # Marco de acento
            px, py = positions[i]
            draw.rectangle([px + 8, py + 8, px + 1272, py + 712], outline=(38, 52, 68), width=2)
            draw.rectangle([px + 14, py + 14, px + 14 + len(labels[i]) * 13 + 24, py + 52], fill=(8, 10, 14, 210))
            draw.text((px + 24, py + 22), labels[i], fill=(240, 190, 45), font=font)

    # Líneas divisorias centrales
    draw.line([(1280, 0), (1280, 1440)], fill=(48, 64, 82), width=3)
    draw.line([(0, 720), (2560, 720)], fill=(48, 64, 82), width=3)

    master_showcase = os.path.join(RENDERS_DIR, "Showcase_Equipment_Pack_Lote3.png")
    canvas.save(master_showcase, quality=95)
    print(f"[OK] Master Showcase 2560x1440 generado: {master_showcase}")

    # Copiar también al directorio de artefactos
    artifact_showcase = os.path.join(ARTIFACT_DIR, "Showcase_Equipment_Pack_Lote3.png")
    shutil.copy2(master_showcase, artifact_showcase)
    print(f"[OK] Showcase copiado a directorio de artefactos: {artifact_showcase}")

    for rf in rendered_files:
        basename = os.path.basename(rf)
        shutil.copy2(rf, os.path.join(ARTIFACT_DIR, basename))

except Exception as e:
    print(f"[WARN] Error en composicion PIL: {e}")

print("==================================================")
print("[EXITO] Generacion de Lote 3 completada con exito.")
print("==================================================")

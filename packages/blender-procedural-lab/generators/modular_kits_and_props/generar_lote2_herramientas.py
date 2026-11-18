"""
generar_lote2_herramientas.py
==============================
Pipeline de Arte 3D en Blender 5.2 LTS para Astra Hazard:
Genera el lote 2 de herramientas de rescate y demolición con arquitectura modular estilo Phasmophobia (GDD §8):
1. SM_ThermalAxe: Hacha térmica de una mano con filo sobrecalentado, pico de brecha y celda de batería.
2. SM_CO2Extinguisher: Extintor portátil de CO2 criogénico con válvula, manómetro, difusor cónico y bota de protección.
3. SM_Defibrillator: Unidad médica de choque con pantalla ECG, barra LED de condensador y paletas gemelas desmontables con cables en espiral.
4. Colisiones físicas UCX para cada herramienta.
5. Materiales PBR industriales con acentos emisivos (filo térmico incandescente, pantalla y LEDs).
6. Exportación a FBX en Content/Meshes/Equipment/ y Art/FBX/Equipment/.
7. Renderizado en alta resolución de hoja de showcase de 4 vistas (Showcase_Equipment_Pack_Phasmo_Style.png).
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

# -----------------------------------------------------------------------------
# LIMPIEZA INICIAL
# -----------------------------------------------------------------------------
bpy.ops.wm.read_factory_settings(use_empty=True)

# -----------------------------------------------------------------------------
# GESTIÓN DE MATERIALES PBR SCI-FI
# -----------------------------------------------------------------------------
def create_pbr_material(name, base_color, metallic, roughness, emissive_color=(0,0,0,1), emissive_strength=0.0):
    mat = bpy.data.materials.get(name)
    if mat:
        return mat
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out_node = nodes.new(type='ShaderNodeOutputMaterial')
    out_node.location = (400, 0)

    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    bsdf.inputs['Base Color'].default_value = base_color
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness

    if emissive_strength > 0.0:
        bsdf.inputs['Emission Color'].default_value = emissive_color
        bsdf.inputs['Emission Strength'].default_value = emissive_strength

    links.new(bsdf.outputs['BSDF'], out_node.inputs['Surface'])
    return mat

MAT_DARK_TITANIUM = create_pbr_material("M_DarkTitanium", (0.05, 0.06, 0.07, 1.0), 0.9, 0.3)
MAT_RESCUE_RED     = create_pbr_material("M_RescueRed",     (0.78, 0.12, 0.08, 1.0), 0.2, 0.35)
MAT_RESCUE_YELLOW  = create_pbr_material("M_RescueYellow",  (0.85, 0.65, 0.05, 1.0), 0.15, 0.4)
MAT_CHROME_STEEL   = create_pbr_material("M_ChromeSteel",   (0.82, 0.85, 0.88, 1.0), 0.95, 0.18)
MAT_RUBBER_GRIP    = create_pbr_material("M_RubberGrip",    (0.02, 0.02, 0.02, 1.0), 0.0, 0.85)
MAT_THERMAL_GLOW   = create_pbr_material("M_ThermalGlow",   (1.0, 0.35, 0.05, 1.0), 0.0, 0.2, (1.0, 0.3, 0.02, 1.0), 3.2)
MAT_GAUGE_CYAN     = create_pbr_material("M_GaugeCyan",     (0.0, 0.8, 0.95, 1.0), 0.0, 0.2, (0.0, 0.8, 0.95, 1.0), 1.4)
MAT_DEFIB_SCREEN   = create_pbr_material("M_DefibScreen",   (0.02, 0.12, 0.22, 1.0), 0.0, 0.15, (0.1, 0.5, 0.9, 1.0), 2.5)
MAT_LED_GREEN      = create_pbr_material("M_LEDGreen",      (0.1, 0.9, 0.3, 1.0), 0.0, 0.2, (0.1, 0.9, 0.3, 1.0), 3.0)

# -----------------------------------------------------------------------------
# 1. HACHA TÉRMICA DE CHOQUE (SM_ThermalAxe)
# -----------------------------------------------------------------------------
def build_thermal_axe():
    parts = []

    # Mango compuesto con sección ovalada (~82 cm de longitud)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.022, depth=0.82, vertices=16, location=(0, 0, 0.41))
    shaft = bpy.context.active_object
    shaft.name = "Axe_Shaft"
    shaft.scale = (0.75, 1.0, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    shaft.data.materials.append(MAT_DARK_TITANIUM)
    parts.append(shaft)

    # Empuñadura antideslizante con textura estriada de caucho
    bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.32, vertices=16, location=(0, 0, 0.22))
    grip = bpy.context.active_object
    grip.name = "Axe_Grip"
    grip.scale = (0.8, 1.05, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    grip.data.materials.append(MAT_RUBBER_GRIP)
    parts.append(grip)

    # Anillos de agarre táctil
    for i in range(4):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.026, minor_radius=0.003, location=(0, 0, 0.12 + i * 0.06))
        ring = bpy.context.active_object
        ring.name = f"Axe_GripRing_{i}"
        ring.data.materials.append(MAT_RESCUE_RED)
        parts.append(ring)

    # Celda de batería de alta densidad en el pomo
    bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.09, vertices=16, location=(0, 0, 0.045))
    battery = bpy.context.active_object
    battery.name = "Axe_BatteryCap"
    battery.data.materials.append(MAT_RESCUE_YELLOW)
    parts.append(battery)

    # Anillo LED de batería en el pomo
    bpy.ops.mesh.primitive_cylinder_add(radius=0.028, depth=0.015, vertices=16, location=(0, 0, 0.08))
    bat_led = bpy.context.active_object
    bat_led.name = "Axe_BatLED"
    bat_led.data.materials.append(MAT_LED_GREEN)
    parts.append(bat_led)

    # Cuello de anclaje de la cabeza
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.82))
    collar = bpy.context.active_object
    collar.name = "Axe_HeadCollar"
    collar.scale = (0.045, 0.055, 0.08)
    bpy.ops.object.transform_apply(scale=True)
    collar.data.materials.append(MAT_DARK_TITANIUM)
    parts.append(collar)

    # Hoja del hacha (corte frontal)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.12, 0.83))
    blade = bpy.context.active_object
    blade.name = "Axe_BladeBase"
    blade.scale = (0.02, 0.14, 0.18)
    bpy.ops.object.transform_apply(scale=True)
    blade.data.materials.append(MAT_CHROME_STEEL)
    parts.append(blade)

    # Filo biselado térmico sobrecalentado (emissivo brillante)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.20, 0.83))
    thermal_edge = bpy.context.active_object
    thermal_edge.name = "Axe_ThermalEdge"
    thermal_edge.scale = (0.008, 0.025, 0.20)
    bpy.ops.object.transform_apply(scale=True)
    thermal_edge.data.materials.append(MAT_THERMAL_GLOW)
    parts.append(thermal_edge)

    # Ranuras de ventilación térmica en el costado del filo
    for j in range(3):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.011, 0.10 + j*0.03, 0.83))
        vent = bpy.context.active_object
        vent.name = f"Axe_VentSlot_{j}"
        vent.scale = (0.003, 0.015, 0.06)
        bpy.ops.object.transform_apply(scale=True)
        vent.data.materials.append(MAT_THERMAL_GLOW)
        parts.append(vent)

    # Pico de brecha trasero (para forzar mamparos y cerrojos)
    bpy.ops.mesh.primitive_cone_add(radius1=0.032, radius2=0.004, depth=0.16, vertices=8, location=(0, -0.13, 0.83))
    pick = bpy.context.active_object
    pick.name = "Axe_RearPick"
    pick.rotation_euler = (R(90), 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    pick.data.materials.append(MAT_DARK_TITANIUM)
    parts.append(pick)

    # Unir todas las partes en SM_ThermalAxe
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = shaft
    bpy.ops.object.join()
    axe_obj = bpy.context.active_object
    axe_obj.name = "SM_ThermalAxe"

    # Suavizado de normales
    bpy.ops.object.shade_smooth()

    # Colisión UCX_SM_ThermalAxe (2 convex primitives)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.40))
    ucx_shaft = bpy.context.active_object
    ucx_shaft.name = "UCX_SM_ThermalAxe_01"
    ucx_shaft.scale = (0.06, 0.06, 0.82)
    bpy.ops.object.transform_apply(scale=True)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.04, 0.83))
    ucx_head = bpy.context.active_object
    ucx_head.name = "UCX_SM_ThermalAxe_02"
    ucx_head.scale = (0.06, 0.36, 0.22)
    bpy.ops.object.transform_apply(scale=True)

    return axe_obj, [ucx_shaft, ucx_head]

# -----------------------------------------------------------------------------
# 2. EXTINTOR PORTÁTIL DE CO2 (SM_CO2Extinguisher)
# -----------------------------------------------------------------------------
def build_co2_extinguisher():
    parts = []

    # Cilindro principal de alta presión (~52 cm de alto, radio 10 cm)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.095, depth=0.48, vertices=24, location=(0, 0, 0.30))
    tank = bpy.context.active_object
    tank.name = "CO2_TankBody"
    tank.data.materials.append(MAT_RESCUE_RED)
    parts.append(tank)

    # Cúpula superior esférica del cilindro
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.095, segments=24, ring_count=16, location=(0, 0, 0.54))
    top_dome = bpy.context.active_object
    top_dome.name = "CO2_TopDome"
    top_dome.scale = (1.0, 1.0, 0.65)
    bpy.ops.object.transform_apply(scale=True)
    top_dome.data.materials.append(MAT_RESCUE_RED)
    parts.append(top_dome)

    # Bota base de goma absorbente de impactos
    bpy.ops.mesh.primitive_cylinder_add(radius=0.102, depth=0.10, vertices=24, location=(0, 0, 0.05))
    boot = bpy.context.active_object
    boot.name = "CO2_RubberBoot"
    boot.data.materials.append(MAT_RUBBER_GRIP)
    parts.append(boot)

    # Franja amarilla de advertencia criogénica en el cilindro (4mm holgura anti Z-fighting)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.099, depth=0.06, vertices=24, location=(0, 0, 0.38))
    stripe = bpy.context.active_object
    stripe.name = "CO2_WarningStripe"
    stripe.data.materials.append(MAT_RESCUE_YELLOW)
    parts.append(stripe)

    # Conjunto de válvula superior de latón/cromo
    bpy.ops.mesh.primitive_cylinder_add(radius=0.032, depth=0.08, vertices=16, location=(0, 0, 0.63))
    valve = bpy.context.active_object
    valve.name = "CO2_ValveStem"
    valve.data.materials.append(MAT_CHROME_STEEL)
    parts.append(valve)

    # Asa de transporte fija
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.06, 0.68))
    handle_fixed = bpy.context.active_object
    handle_fixed.name = "CO2_HandleFixed"
    handle_fixed.scale = (0.025, 0.12, 0.02)
    bpy.ops.object.transform_apply(scale=True)
    handle_fixed.data.materials.append(MAT_DARK_TITANIUM)
    parts.append(handle_fixed)

    # Palanca de accionamiento móvil (gatillo)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.06, 0.72))
    lever = bpy.context.active_object
    lever.name = "CO2_TriggerLever"
    lever.scale = (0.024, 0.13, 0.015)
    lever.rotation_euler = (R(8), 0, 0)
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    lever.data.materials.append(MAT_RESCUE_RED)
    parts.append(lever)

    # Pasador de seguridad con anilla
    bpy.ops.mesh.primitive_torus_add(major_radius=0.022, minor_radius=0.003, location=(0.04, -0.04, 0.69))
    pin_ring = bpy.context.active_object
    pin_ring.name = "CO2_SafetyPinRing"
    pin_ring.rotation_euler = (0, R(90), 0)
    bpy.ops.object.transform_apply(rotation=True)
    pin_ring.data.materials.append(MAT_CHROME_STEEL)
    parts.append(pin_ring)

    # Manómetro circular de presión interna
    bpy.ops.mesh.primitive_cylinder_add(radius=0.024, depth=0.018, vertices=16, location=(0.042, 0.0, 0.65))
    gauge = bpy.context.active_object
    gauge.name = "CO2_PressureGauge"
    gauge.rotation_euler = (0, R(90), 0)
    bpy.ops.object.transform_apply(rotation=True)
    gauge.data.materials.append(MAT_CHROME_STEEL)
    parts.append(gauge)

    # Esfera/aguja del manómetro (emisivo Cyan)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.020, depth=0.005, vertices=16, location=(0.052, 0.0, 0.65))
    gauge_dial = bpy.context.active_object
    gauge_dial.name = "CO2_GaugeDial"
    gauge_dial.rotation_euler = (0, R(90), 0)
    bpy.ops.object.transform_apply(rotation=True)
    gauge_dial.data.materials.append(MAT_GAUGE_CYAN)
    parts.append(gauge_dial)

    # Boquilla difusora criogénica cónica (estrecha en la válvula, boca ancha al frente +Y)
    bpy.ops.mesh.primitive_cone_add(radius1=0.022, radius2=0.065, depth=0.22, vertices=20, location=(0, 0.16, 0.63))
    horn = bpy.context.active_object
    horn.name = "CO2_DiffusionHorn"
    horn.rotation_euler = (R(-90), 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    horn.data.materials.append(MAT_RUBBER_GRIP)
    parts.append(horn)

    # Tubo de acople de la boquilla
    bpy.ops.mesh.primitive_cylinder_add(radius=0.016, depth=0.09, vertices=12, location=(0, 0.045, 0.63))
    neck_tube = bpy.context.active_object
    neck_tube.name = "CO2_HornNeck"
    neck_tube.rotation_euler = (R(-90), 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    neck_tube.data.materials.append(MAT_CHROME_STEEL)
    parts.append(neck_tube)

    # Unir partes
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = tank
    bpy.ops.object.join()
    ext_obj = bpy.context.active_object
    ext_obj.name = "SM_CO2Extinguisher"
    bpy.ops.object.shade_smooth()

    # Colisión UCX (3 convex primitives)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.11, depth=0.58, vertices=12, location=(0, 0, 0.29))
    ucx_tank = bpy.context.active_object
    ucx_tank.name = "UCX_SM_CO2Extinguisher_01"

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.05, 0.68))
    ucx_valve = bpy.context.active_object
    ucx_valve.name = "UCX_SM_CO2Extinguisher_02"
    ucx_valve.scale = (0.08, 0.18, 0.14)
    bpy.ops.object.transform_apply(scale=True)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.16, 0.62))
    ucx_horn = bpy.context.active_object
    ucx_horn.name = "UCX_SM_CO2Extinguisher_03"
    ucx_horn.scale = (0.14, 0.24, 0.14)
    bpy.ops.object.transform_apply(scale=True)

    return ext_obj, [ucx_tank, ucx_valve, ucx_horn]

# -----------------------------------------------------------------------------
# 3. DESFIBRILADOR DE CHOQUE RESUCITADOR (SM_Defibrillator)
# -----------------------------------------------------------------------------
def build_defibrillator():
    parts = []

    # Carcasa rugosa principal (estilo maletín médico táctico 34x24x15 cm)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.08))
    body = bpy.context.active_object
    body.name = "Defib_MainBody"
    body.scale = (0.34, 0.24, 0.15)
    bpy.ops.object.transform_apply(scale=True)
    body.data.materials.append(MAT_RESCUE_RED)
    parts.append(body)

    # Parachoques de esquinas de alta absorción (caucho negro)
    corner_offsets = [
        (-0.16, -0.11), (0.16, -0.11),
        (-0.16,  0.11), (0.16,  0.11)
    ]
    for idx, (cx, cy) in enumerate(corner_offsets):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(cx, cy, 0.08))
        bumper = bpy.context.active_object
        bumper.name = f"Defib_CornerBumper_{idx}"
        bumper.scale = (0.05, 0.05, 0.16)
        bpy.ops.object.transform_apply(scale=True)
        bumper.data.materials.append(MAT_RUBBER_GRIP)
        parts.append(bumper)

    # Asa de transporte táctica superior
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.14, 0.08))
    handle = bpy.context.active_object
    handle.name = "Defib_CarryHandle"
    handle.scale = (0.16, 0.04, 0.04)
    bpy.ops.object.transform_apply(scale=True)
    handle.data.materials.append(MAT_RUBBER_GRIP)
    parts.append(handle)

    # Panel de control frontal inclinado
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, -0.02, 0.156))
    faceplate = bpy.context.active_object
    faceplate.name = "Defib_Faceplate"
    faceplate.scale = (0.30, 0.20, 0.015)
    bpy.ops.object.transform_apply(scale=True)
    faceplate.data.materials.append(MAT_DARK_TITANIUM)
    parts.append(faceplate)

    # Pantalla LCD / Monitor ECG central
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0.02, 0.166))
    screen = bpy.context.active_object
    screen.name = "Defib_ECGScreen"
    screen.scale = (0.16, 0.10, 0.008)
    bpy.ops.object.transform_apply(scale=True)
    screen.data.materials.append(MAT_DEFIB_SCREEN)
    parts.append(screen)

    # Barra LED de carga de condensador (3 segmentos LED)
    for seg in range(3):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.05 + seg*0.05, -0.06, 0.166))
        led = bpy.context.active_object
        led.name = f"Defib_ChargeLED_{seg}"
        led.scale = (0.038, 0.018, 0.008)
        bpy.ops.object.transform_apply(scale=True)
        led.data.materials.append(MAT_LED_GREEN)
        parts.append(led)

    # Botón principal de descarga (rojo luminiscente)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.016, depth=0.015, vertices=16, location=(0, -0.09, 0.168))
    shock_btn = bpy.context.active_object
    shock_btn.name = "Defib_ShockButton"
    shock_btn.data.materials.append(MAT_RESCUE_RED)
    parts.append(shock_btn)

    # Paletas de descarga dual (acopladas en holsters laterales)
    paddle_x_positions = [-0.19, 0.19]
    for p_idx, px in enumerate(paddle_x_positions):
        # Holster / Cuna lateral
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(px, -0.02, 0.09))
        cradle = bpy.context.active_object
        cradle.name = f"Defib_Cradle_{p_idx}"
        cradle.scale = (0.05, 0.16, 0.12)
        bpy.ops.object.transform_apply(scale=True)
        cradle.data.materials.append(MAT_DARK_TITANIUM)
        parts.append(cradle)

        # Mango de la paleta
        bpy.ops.mesh.primitive_cylinder_add(radius=0.018, depth=0.12, vertices=16, location=(px, -0.02, 0.14))
        p_handle = bpy.context.active_object
        p_handle.name = f"Defib_PaddleHandle_{p_idx}"
        p_handle.data.materials.append(MAT_RUBBER_GRIP)
        parts.append(p_handle)

        # Placa metálica conductora de choque
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(px, -0.02, 0.04))
        p_plate = bpy.context.active_object
        p_plate.name = f"Defib_PaddlePlate_{p_idx}"
        p_plate.scale = (0.035, 0.11, 0.02)
        bpy.ops.object.transform_apply(scale=True)
        p_plate.data.materials.append(MAT_CHROME_STEEL)
        parts.append(p_plate)

        # Pulsador de dedo en la paleta
        bpy.ops.mesh.primitive_cylinder_add(radius=0.008, depth=0.012, vertices=12, location=(px, -0.02, 0.20))
        p_trigger = bpy.context.active_object
        p_trigger.name = f"Defib_PaddleTrigger_{p_idx}"
        p_trigger.data.materials.append(MAT_RESCUE_RED)
        parts.append(p_trigger)

        # Cable espiralado simulado
        bpy.ops.mesh.primitive_torus_add(major_radius=0.018, minor_radius=0.005, location=(px * 0.85, 0.08, 0.06))
        cable = bpy.context.active_object
        cable.name = f"Defib_CableCoil_{p_idx}"
        cable.data.materials.append(MAT_RUBBER_GRIP)
        parts.append(cable)

    # Unir componentes
    bpy.ops.object.select_all(action='DESELECT')
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = body
    bpy.ops.object.join()
    defib_obj = bpy.context.active_object
    defib_obj.name = "SM_Defibrillator"
    bpy.ops.object.shade_smooth()

    # Colisión UCX (3 convex primitives)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.08))
    ucx_main = bpy.context.active_object
    ucx_main.name = "UCX_SM_Defibrillator_01"
    ucx_main.scale = (0.36, 0.28, 0.18)
    bpy.ops.object.transform_apply(scale=True)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-0.19, -0.02, 0.10))
    ucx_pad_l = bpy.context.active_object
    ucx_pad_l.name = "UCX_SM_Defibrillator_02"
    ucx_pad_l.scale = (0.08, 0.18, 0.20)
    bpy.ops.object.transform_apply(scale=True)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.19, -0.02, 0.10))
    ucx_pad_r = bpy.context.active_object
    ucx_pad_r.name = "UCX_SM_Defibrillator_03"
    ucx_pad_r.scale = (0.08, 0.18, 0.20)
    bpy.ops.object.transform_apply(scale=True)

    return defib_obj, [ucx_main, ucx_pad_l, ucx_pad_r]

# -----------------------------------------------------------------------------
# EXPORTACIÓN FBX
# -----------------------------------------------------------------------------
def export_fbx_asset(name, mesh_obj, ucx_objs):
    bpy.ops.object.select_all(action='DESELECT')
    mesh_obj.select_set(True)
    for u in ucx_objs:
        u.select_set(True)
    bpy.context.view_layer.objects.active = mesh_obj

    for target_dir in [FBX_CONTENT_DIR, FBX_ART_DIR]:
        fbx_path = os.path.join(target_dir, f"{name}.fbx")
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

# -----------------------------------------------------------------------------
# ILUMINACIÓN Y ESTUDIO DE RENDER
# -----------------------------------------------------------------------------
def setup_lighting():
    # Luz clave principal
    key_light = bpy.data.lights.new("KeyAreaLight", type='AREA')
    key_light.energy = 550.0
    key_light.size = 2.0
    key_light.color = (1.0, 0.96, 0.92)
    key_obj = bpy.data.objects.new("KeyLight", key_light)
    key_obj.location = (1.8, -2.2, 2.0)
    key_obj.rotation_euler = (R(55), 0, R(35))
    bpy.context.collection.objects.link(key_obj)

    # Luz de relleno fría
    fill_light = bpy.data.lights.new("FillAreaLight", type='AREA')
    fill_light.energy = 260.0
    fill_light.size = 2.8
    fill_light.color = (0.65, 0.82, 1.0)
    fill_obj = bpy.data.objects.new("FillLight", fill_light)
    fill_obj.location = (-2.0, 1.6, 1.4)
    fill_obj.rotation_euler = (R(60), 0, R(-125))
    bpy.context.collection.objects.link(fill_obj)

    # Rim light de recorte sci-fi (cian)
    rim_light = bpy.data.lights.new("RimSpotLight", type='SPOT')
    rim_light.energy = 400.0
    rim_light.spot_size = R(70)
    rim_light.color = (0.2, 0.8, 1.0)
    rim_obj = bpy.data.objects.new("RimLight", rim_light)
    rim_obj.location = (0.0, 2.4, 1.8)
    rim_obj.rotation_euler = (R(140), 0, 0)
    bpy.context.collection.objects.link(rim_obj)

    # Mundo / Entorno
    world = bpy.data.worlds.new("IndustrialWorld")
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (0.03, 0.04, 0.05, 1.0)
        bg.inputs['Strength'].default_value = 0.4
    bpy.context.scene.world = world

# -----------------------------------------------------------------------------
# EJECUCIÓN PRINCIPAL
# -----------------------------------------------------------------------------
print(">>> Generando Lote 2 de Herramientas Modulares...")

# 1. Construir modelos y colisiones
axe_obj, axe_ucx = build_thermal_axe()
export_fbx_asset("SM_ThermalAxe", axe_obj, axe_ucx)

ext_obj, ext_ucx = build_co2_extinguisher()
export_fbx_asset("SM_CO2Extinguisher", ext_obj, ext_ucx)

defib_obj, defib_ucx = build_defibrillator()
export_fbx_asset("SM_Defibrillator", defib_obj, defib_ucx)

# 2. Ocultar colisiones UCX para el renderizado
for u in axe_ucx + ext_ucx + defib_ucx:
    u.hide_render = True
    u.hide_viewport = True

# 3. Disponer los 3 ítems para el showcase
# Pedestal / Stand de presentación
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, -0.05))
stand = bpy.context.active_object
stand.name = "Showcase_Pedestal"
stand.scale = (2.4, 1.2, 0.1)
bpy.ops.object.transform_apply(scale=True)
stand.data.materials.append(MAT_DARK_TITANIUM)

# Posicionamiento optimizado para exhibición:
# Hacha apoyada a la izquierda en ángulo de 30 grados
axe_obj.location = (-0.65, 0.0, 0.05)
axe_obj.rotation_euler = (R(15), R(-35), R(-40))

# Extintor al centro vertical erguido ligeramente girado para mostrar manómetro y bocina
ext_obj.location = (0.0, 0.02, 0.0)
ext_obj.rotation_euler = (0, 0, R(30))

# Desfibrilador a la derecha inclinado hacia adelante para mostrar pantalla
defib_obj.location = (0.65, -0.02, 0.0)
defib_obj.rotation_euler = (R(25), 0, R(-15))

# 4. Configurar iluminación y cámara
setup_lighting()

cam_data = bpy.data.cameras.new("ShowcaseCamera")
cam_data.lens = 45.0
cam_obj = bpy.data.objects.new("ShowcaseCamera", cam_data)
bpy.context.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj

scene = bpy.context.scene
scene.render.engine = 'CYCLES' if bpy.context.preferences.addons.get('cycles') else 'BLENDER_EEVEE_NEXT'
if scene.render.engine == 'CYCLES':
    scene.cycles.samples = 64
    scene.cycles.use_denoising = True

scene.render.resolution_x = 1280
scene.render.resolution_y = 720

# 5. Renderizar 4 vistas con aislamiento y enfoque limpio de estudio
render_config = {
    "arsenal_full": {
        "axe_pos": (-0.48, 0.02, 0.0),  "axe_rot": (0, 0, R(-35)),         "axe_vis": True,
        "ext_pos": (0.0, 0.02, 0.0),    "ext_rot": (0, 0, R(30)),          "ext_vis": True,
        "def_pos": (0.55, -0.02, 0.0),  "def_rot": (R(25), 0, R(-15)),     "def_vis": True,
        "cam_pos": (0.0, -2.1, 0.65),   "cam_rot": (R(75), 0, 0)
    },
    "axe_closeup": {
        "axe_pos": (0.0, 0.0, 0.0),    "axe_rot": (0, 0, R(35)),          "axe_vis": True,
        "ext_pos": (0, 0, 0),          "ext_rot": (0, 0, 0),              "ext_vis": False,
        "def_pos": (0, 0, 0),          "def_rot": (0, 0, 0),              "def_vis": False,
        "cam_pos": (0.0, -0.78, 0.82), "cam_rot": (R(85), 0, 0)
    },
    "ext_closeup": {
        "axe_pos": (0, 0, 0),          "axe_rot": (0, 0, 0),              "axe_vis": False,
        "ext_pos": (0.0, 0.0, 0.0),    "ext_rot": (0, 0, R(25)),          "ext_vis": True,
        "def_pos": (0, 0, 0),          "def_rot": (0, 0, 0),              "def_vis": False,
        "cam_pos": (0.0, -1.2, 0.38),  "cam_rot": (R(82), 0, 0)
    },
    "defib_closeup": {
        "axe_pos": (0, 0, 0),          "axe_rot": (0, 0, 0),              "axe_vis": False,
        "ext_pos": (0, 0, 0),          "ext_rot": (0, 0, 0),              "ext_vis": False,
        "def_pos": (0.0, 0.0, 0.0),    "def_rot": (R(22), 0, 0),          "def_vis": True,
        "cam_pos": (0.0, -0.9, 0.42),  "cam_rot": (R(65), 0, 0)
    }
}

rendered_files = []
for shot_name, cfg in render_config.items():
    axe_obj.location = cfg["axe_pos"]
    axe_obj.rotation_euler = cfg["axe_rot"]
    axe_obj.hide_render = not cfg["axe_vis"]

    ext_obj.location = cfg["ext_pos"]
    ext_obj.rotation_euler = cfg["ext_rot"]
    ext_obj.hide_render = not cfg["ext_vis"]

    defib_obj.location = cfg["def_pos"]
    defib_obj.rotation_euler = cfg["def_rot"]
    defib_obj.hide_render = not cfg["def_vis"]

    cam_obj.location = cfg["cam_pos"]
    cam_obj.rotation_euler = cfg["cam_rot"]

    out_file = os.path.join(RENDERS_DIR, f"Showcase_Equip_{shot_name}.png")
    scene.render.filepath = out_file
    bpy.ops.render.render(write_still=True)
    rendered_files.append(out_file)
    print(f"[OK] Renderizado cuadrante: {out_file}")

# Guardar escena blend
blend_path = os.path.join(PROJECT_ROOT, "Art", "Blender", "Lote2_Herramientas_PhasmoStyle.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f"[OK] Guardado archivo Blender: {blend_path}")

# 6. Componer montaje 2x2 en 2560x1440
try:
    from PIL import Image, ImageDraw, ImageFont

    canvas = Image.new("RGB", (2560, 1440), (10, 12, 16))
    positions = [(0, 0), (1280, 0), (0, 720), (1280, 720)]
    labels = [
        "ARSENAL MODULAR DE RESCATE (ESTILO PHASMOPHOBIA) - GDD 8",
        "HACHA TÉRMICA DE CHOQUE (FILO INCANDESCENTE Y PICO DE BRECHA)",
        "EXTINTOR PORTÁTIL CO2 CRIOGÉNICO (VÁLVULA, MANÓMETRO Y DIFUSOR)",
        "DESFIBRILADOR DE CHOQUE (MONITOR ECG, PALETAS DUALES Y BARRA LED)"
    ]

    for i, file_path in enumerate(rendered_files):
        img = Image.open(file_path).resize((1280, 720), Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(img)
        # Banner de texto
        draw.rectangle([(25, 25), (880, 75)], fill=(12, 15, 20, 220))
        draw.text((40, 38), labels[i], fill=(255, 185, 45))
        canvas.paste(img, positions[i])

    showcase_path = os.path.join(RENDERS_DIR, "Showcase_Equipment_Pack_Phasmo_Style.png")
    canvas.save(showcase_path)
    print(f"[OK] Showcase compuesto guardado: {showcase_path}")

    # Copiar a artifacts
    artifact_showcase = os.path.join(ARTIFACT_DIR, "Showcase_Equipment_Pack_Phasmo_Style.png")
    shutil.copy2(showcase_path, artifact_showcase)
    print(f"[OK] Showcase copiado a artefactos: {artifact_showcase}")

except Exception as e:
    print(f"[WARN] Error componiendo con PIL: {e}. Copiando vista principal como fallback.")
    fallback_path = rendered_files[0]
    artifact_showcase = os.path.join(ARTIFACT_DIR, "Showcase_Equipment_Pack_Phasmo_Style.png")
    shutil.copy2(fallback_path, artifact_showcase)

print(">>> ¡Pipeline de Blender completado exitosamente!")

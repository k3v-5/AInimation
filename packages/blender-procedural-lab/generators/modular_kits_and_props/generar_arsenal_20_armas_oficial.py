# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Arsenal Oficial de 20 Armas y Herramientas Tácticas de Bombero Espacial - Astra Hazard
# Blender 5.2 LTS - Shaders Stylized PBR, Cel-Shading, Manómetros, Franjas Hazard y Freestyle Ink Lineart

import bpy
import bmesh
import math
import os
import sys
import shutil
from PIL import Image, ImageDraw, ImageFont

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

import astra_blender_styling as abs_style

R = math.radians

WEAPONS_DATA = [
    (1, "W01_Hydra_Heavy_Hose", "Manguera de Alta Presión Hidráulica", "TIER 1 // SUPRESIÓN",
     "• Boquilla de latón macizo escalonada\n• Doble manómetro de control 250 Bar\n• Manguera corrugada de suministro"),
    (2, "W02_Thermal_Shock_Axe", "Hacha de Choque Térmico", "TIER 1 // BRECHA",
     "• Filo de plasma térmico a 1,800°C\n• Pica de ruptura de tungsteno\n• Empuñadura aislante con batería"),
    (3, "W03_Cryo_CO2_Extinguisher", "Extintor Criogénico CO2 Pesado", "TIER 1 // EXTINCIÓN",
     "• Doble cilindro presurizado con cinchas\n• Válvula de latón y manómetro analógico\n• Tobera difusora cónica escarchada"),
    (4, "W04_Bio_Defibrillator_Unit", "Desfibrilador Portátil Militar", "TIER 1 // MÉDICO",
     "• Chasis antichoque con cantoneras\n• Pantalla CRT con electrocardiograma\n• Palas bifásicas con cables espirales"),
    (5, "W05_Plasma_Halligan_Bar", "Barra Halligan de Plasma Forjado", "TIER 1 // PALANCA",
     "• Garra de cuña y pica en ángulo recto\n• Filos inductivos de corte por plasma\n• Cuerpo octogonal con agarre estriado"),
    (6, "W06_Rotary_Rescue_Saw", "Sierra Circular de Rescate Rotativa", "TIER 1 // CORTE",
     "• Disco de corte diamantado templado\n• Protector con franjas hazard reflectantes\n• Motor blindado con jaula tubular"),
    (7, "W07_Pneumatic_Bolt_Cutter", "Cizalla Neumática Asistida", "TIER 2 // RESCATE",
     "• Cuchillas templadas de aleación pesada\n• Doble pistón hidráulico cromado\n• Manómetro de presión con aguja roja"),
    (8, "W08_Chemical_Foam_Mortar", "Mortero de Espuma Química", "TIER 2 // CONTENCIÓN",
     "• Tambor rotativo de 4 cartuchos\n• Múltiple de latón con cámara de mezcla\n• Culata metálica y difusor pesado"),
    (9, "W09_Thermite_Breach_Lance", "Lanza Térmica de Perforación", "TIER 2 // PERFORACIÓN",
     "• Núcleo incandescente de termita fundente\n• Escudo deflector con franjas de peligro\n• Válvula de oxígeno con dial analógico"),
    (10,"W10_EMP_Disruptor_Pistol", "Pistola Disruptora EMP", "TIER 2 // DESACTIVACIÓN",
     "• 4 bobinas inductivas de cobre macizo\n• Condensadores de pulso azul iónico\n• Disipador térmico y gatillo ergonómico"),
    (11,"W11_Hydraulic_Spreader_Jaws", "Mandíbulas de Separación Hidráulica", "TIER 2 // EXTINCIÓN",
     "• Quijadas de expansión de 72 Toneladas\n• Pistón central cromado con manguitos\n• Asa perimetral con franja hazard"),
    (12,"W12_Cryo_Grenade_Launcher", "Lanzagranadas Criogénico de Tambor", "TIER 2 // CONTENCIÓN",
     "• Tambor de 6 proyectiles de nitrógeno\n• Cañón con respiraderos de escarcha\n• Manómetro subcero con dial blanco"),
    (13,"W13_Pneumatic_Breaching_Ram", "Ariete Neumático de Brecha Cinético", "TIER 2 // APERTURA",
     "• Pistón macizo de tungsteno kinetic\n• Doble depósito de CO2 con franjas hazard\n• Agarraderas dobles con amortiguador"),
    (14,"W14_Magnetic_Net_Launcher", "Lanzador de Red Magnética Cuádruple", "TIER 2 // CAPTURA",
     "• 4 bocas con copas magnéticas de cobre\n• Módulo de puntería láser azul frontal\n• Cartucho de microfilamento conductor"),
    (15,"W15_Chemical_Neutralizer_Pack", "Aspersor Neutralizador Portátil", "TIER 3 // DECON",
     "• Tanques presurizados dorsales con cinchas\n• Lanza de acero con difusor multichorro\n• Manguera corrugada de suministro"),
    (16,"W16_Emergency_SOS_Flare_Gun", "Pistola de Bengalas SOS Superbrillante", "TIER 3 // SEÑALIZACIÓN",
     "• Cañón basculante con bocacha de latón\n• Chasis naranja de alta visibilidad\n• Cartucho de magnesio hiperbárico"),
    (17,"W17_Sonic_Fire_Suppressor", "Supresor Sónico de Fuego Acústico", "TIER 3 // ONDA CHOQUE",
     "• Antena parabólica difusora sónica\n• Cámara de resonancia con aletas\n• Medidor analógico de frecuencia"),
    (18,"W18_Arc_Welding_Cutting_Torch", "Soplete de Arco Voltaico Industrial", "TIER 3 // SOLDADURA",
     "• Boquilla de corte con electrodo de tungsteno\n• Doble válvula reguladora de latón\n• Tubo blindado con espiral metálica"),
    (19,"W19_Tripod_Mounted_Foam_Cannon", "Cañón de Espuma Pesada Sobre Trípode", "TIER 3 // ESTACIONARIO",
     "• Monitor de gran calibre con difusor\n• Trípode industrial plegable de acero\n• Doble empuñadura con gatillos de pulgar"),
    (20,"W20_Tactical_Rescue_Machete", "Machete Táctico de Rescate y Supervivencia", "TIER 3 // SUPERVIVENCIA",
     "• Hoja pesada con lomo dentado de sierra\n• Mango con enrollado de cuerda naranja\n• Franjas hazard estarcidas en lomo")
]

def init_weapons_materials():
    mats = {}
    mats['hazard_yellow'] = abs_style.get_comic_material("W_Hazard_Yellow", base_color=(0.96, 0.76, 0.08), roughness=0.30, metallic=0.15)
    mats['hazard_stripes'] = abs_style.get_hazard_stripes_material()
    mats['safety_orange'] = abs_style.get_comic_material("W_Safety_Orange", base_color=(0.95, 0.38, 0.05), roughness=0.32, metallic=0.10)
    mats['gunmetal'] = abs_style.get_comic_material("W_Gunmetal", base_color=(0.22, 0.25, 0.30), roughness=0.32, metallic=0.88)
    mats['steel_bright'] = abs_style.get_comic_material("W_Steel_Bright", base_color=(0.88, 0.90, 0.92), roughness=0.12, metallic=0.98)
    mats['brass_gold'] = abs_style.get_comic_material("W_Brass_Gold", base_color=(0.94, 0.74, 0.18), roughness=0.20, metallic=0.95)
    mats['copper'] = abs_style.get_comic_material("W_Copper", base_color=(0.92, 0.48, 0.22), roughness=0.22, metallic=0.92)
    mats['carbon_fiber'] = abs_style.get_comic_material("W_Carbon_Fiber", base_color=(0.10, 0.11, 0.13), roughness=0.50, metallic=0.25)
    mats['rubber_grip'] = abs_style.get_comic_material("W_Rubber_Grip", base_color=(0.08, 0.08, 0.10), roughness=0.85, metallic=0.0)
    mats['fire_ext_red'] = abs_style.get_comic_material("W_Fire_Ext_Red", base_color=(0.90, 0.12, 0.08), roughness=0.25, metallic=0.20)
    mats['hose_red'] = abs_style.get_comic_material("W_Hose_Red", base_color=(0.85, 0.15, 0.10), roughness=0.60, metallic=0.05)
    mats['dial_white'] = abs_style.get_comic_material("W_Dial_White", base_color=(0.95, 0.95, 0.92), roughness=0.20, metallic=0.0)
    mats['needle_red'] = abs_style.get_comic_material("W_Needle_Red", base_color=(1.0, 0.08, 0.05), roughness=0.15, metallic=0.10,
                                                       emissive_color=(1.0, 0.1, 0.05, 1.0), emissive_strength=2.0)
    
    # Emisivos estilizados
    mats['plasma_orange'] = abs_style.get_comic_material("W_Plasma_Orange", base_color=(1.0, 0.45, 0.05), roughness=0.10,
                                                          emissive_color=(1.0, 0.48, 0.06, 1.0), emissive_strength=3.5)
    mats['cryo_cyan'] = abs_style.get_comic_material("W_Cryo_Cyan", base_color=(0.08, 0.90, 1.0), roughness=0.08,
                                                     emissive_color=(0.10, 0.92, 1.0, 1.0), emissive_strength=3.5)
    mats['emp_blue'] = abs_style.get_comic_material("W_EMP_Blue", base_color=(0.15, 0.48, 1.0), roughness=0.10,
                                                    emissive_color=(0.18, 0.52, 1.0, 1.0), emissive_strength=3.8)
    mats['crt_green'] = abs_style.get_comic_material("W_CRT_Green", base_color=(0.10, 0.98, 0.28), roughness=0.12,
                                                     emissive_color=(0.12, 1.0, 0.32, 1.0), emissive_strength=3.0)
    return mats

def build_weapon(weapon_id, name, origin, col, mats):
    root = bpy.data.objects.new(f"Root_{name}", None)
    root.location = origin
    col.objects.link(root)
    ox, oy, oz = 0.0, 0.0, 0.0

    if weapon_id == 1: # W01_Hydra_Heavy_Hose
        body = abs_style.create_cylinder(f"{name}_Body", radius=0.14, depth=1.4, rot=(R(90), 0, 0), loc=(ox, oy, oz + 0.8), mat=mats['hazard_yellow'], col=col)
        body.parent = root
        band = abs_style.create_cylinder(f"{name}_HazardBand", radius=0.145, depth=0.35, rot=(R(90), 0, 0), loc=(ox, oy + 0.1, oz + 0.8), mat=mats['hazard_stripes'], col=col)
        band.parent = root
        nozzle = abs_style.create_cone(f"{name}_Nozzle", radius1=0.22, radius2=0.11, depth=0.45, rot=(R(90), 0, 0), loc=(ox, oy - 0.90, oz + 0.8), mat=mats['brass_gold'], col=col)
        nozzle.parent = root
        flange = abs_style.create_cylinder(f"{name}_Flange", radius=0.24, depth=0.08, rot=(R(90), 0, 0), loc=(ox, oy - 0.70, oz + 0.8), mat=mats['brass_gold'], col=col)
        flange.parent = root
        handle_t = abs_style.create_torus(f"{name}_HandleT", major_r=0.20, minor_r=0.04, rot=(0, R(90), 0), loc=(ox, oy - 0.25, oz + 1.02), mat=mats['rubber_grip'], col=col)
        handle_t.parent = root
        handle_r = abs_style.create_cylinder(f"{name}_GripRear", radius=0.045, depth=0.40, loc=(ox, oy + 0.55, oz + 0.58), mat=mats['rubber_grip'], col=col)
        handle_r.parent = root
        g1 = abs_style.create_analog_gauge(f"{name}_Gauge1", loc=(ox + 0.15, oy + 0.15, oz + 0.95), rot=(0, 45, 0), radius=0.12, col=col)
        g1.parent = root
        g2 = abs_style.create_analog_gauge(f"{name}_Gauge2", loc=(ox - 0.15, oy + 0.15, oz + 0.95), rot=(0, -45, 0), radius=0.12, col=col)
        g2.parent = root
        hose = abs_style.create_cylinder(f"{name}_SupplyHose", radius=0.09, depth=1.1, rot=(R(40), 0, 0), loc=(ox, oy + 0.95, oz + 0.55), mat=mats['hose_red'], col=col)
        hose.parent = root

    elif weapon_id == 2: # W02_Thermal_Shock_Axe (Descansa horizontalmente en la cuna táctica)
        shaft = abs_style.create_cylinder(f"{name}_Shaft", radius=0.04, depth=1.35, rot=(0, R(78), 0), loc=(ox, oy, oz + 0.72), mat=mats['carbon_fiber'], col=col)
        shaft.parent = root
        grip = abs_style.create_cylinder(f"{name}_GripWrap", radius=0.046, depth=0.60, rot=(0, R(78), 0), loc=(ox + 0.28, oy, oz + 0.66), mat=mats['rubber_grip'], col=col)
        grip.parent = root
        pommel = abs_style.create_cylinder(f"{name}_Battery", radius=0.065, depth=0.20, rot=(0, R(78), 0), loc=(ox + 0.65, oy, oz + 0.58), mat=mats['hazard_yellow'], col=col)
        pommel.parent = root
        head = abs_style.create_box(f"{name}_AxeHead", size=(0.14, 0.48, 0.32), rot=(0, R(78), 0), loc=(ox - 0.55, oy, oz + 0.84), mat=mats['gunmetal'], col=col)
        head.parent = root
        edge = abs_style.create_box(f"{name}_PlasmaBlade", size=(0.05, 0.28, 0.38), rot=(0, R(78), 0), loc=(ox - 0.55, oy - 0.28, oz + 0.84), mat=mats['plasma_orange'], col=col)
        edge.parent = root
        spike = abs_style.create_cone(f"{name}_BreachSpike", radius1=0.07, radius2=0.01, depth=0.32, rot=(0, R(-12), 0), loc=(ox - 0.55, oy + 0.28, oz + 0.84), mat=mats['steel_bright'], col=col)
        spike.parent = root
        g = abs_style.create_analog_gauge(f"{name}_ChargeGauge", loc=(ox - 0.48, oy, oz + 0.86), rot=(0, 90, 0), radius=0.08, col=col)
        g.parent = root

    elif weapon_id == 3: # W03_Cryo_CO2_Extinguisher
        t1 = abs_style.create_cylinder(f"{name}_TankL", radius=0.18, depth=1.05, loc=(ox - 0.16, oy, oz + 0.65), mat=mats['fire_ext_red'], col=col)
        t1.parent = root
        t2 = abs_style.create_cylinder(f"{name}_TankR", radius=0.18, depth=1.05, loc=(ox + 0.16, oy, oz + 0.65), mat=mats['fire_ext_red'], col=col)
        t2.parent = root
        b1 = abs_style.create_cylinder(f"{name}_StripeL", radius=0.185, depth=0.25, loc=(ox - 0.16, oy, oz + 0.65), mat=mats['hazard_stripes'], col=col)
        b1.parent = root
        b2 = abs_style.create_cylinder(f"{name}_StripeR", radius=0.185, depth=0.25, loc=(ox + 0.16, oy, oz + 0.65), mat=mats['hazard_stripes'], col=col)
        b2.parent = root
        valve = abs_style.create_box(f"{name}_Manifold", size=(0.42, 0.22, 0.18), loc=(ox, oy, oz + 1.22), mat=mats['brass_gold'], col=col)
        valve.parent = root
        horn = abs_style.create_cone(f"{name}_DiffuserHorn", radius1=0.22, radius2=0.06, depth=0.65, rot=(R(30), 0, 0), loc=(ox, oy - 0.35, oz + 0.95), mat=mats['gunmetal'], col=col)
        horn.parent = root
        frost = abs_style.create_cylinder(f"{name}_FrostCore", radius=0.05, depth=0.25, rot=(R(30), 0, 0), loc=(ox, oy - 0.55, oz + 0.85), mat=mats['cryo_cyan'], col=col)
        frost.parent = root
        g = abs_style.create_analog_gauge(f"{name}_PressGauge", loc=(ox, oy - 0.12, oz + 1.22), rot=(90, 0, 0), radius=0.10, col=col)
        g.parent = root

    elif weapon_id == 4: # W04_Bio_Defibrillator_Unit
        case = abs_style.create_box(f"{name}_MainUnit", size=(0.68, 0.48, 0.32), loc=(ox, oy, oz + 0.8), mat=mats['hazard_yellow'], col=col)
        case.parent = root
        bump1 = abs_style.create_box(f"{name}_BumperF", size=(0.72, 0.06, 0.34), loc=(ox, oy - 0.22, oz + 0.8), mat=mats['rubber_grip'], col=col)
        bump1.parent = root
        screen = abs_style.create_box(f"{name}_CRTScreen", size=(0.42, 0.02, 0.20), loc=(ox, oy - 0.25, oz + 0.82), mat=mats['crt_green'], col=col)
        screen.parent = root
        pad_l = abs_style.create_box(f"{name}_PaddleL", size=(0.16, 0.16, 0.22), loc=(ox - 0.45, oy, oz + 0.8), mat=mats['gunmetal'], col=col)
        pad_l.parent = root
        pad_r = abs_style.create_box(f"{name}_PaddleR", size=(0.16, 0.16, 0.22), loc=(ox + 0.45, oy, oz + 0.8), mat=mats['gunmetal'], col=col)
        pad_r.parent = root
        elec_l = abs_style.create_cylinder(f"{name}_PlateL", radius=0.07, depth=0.02, rot=(R(90), 0, 0), loc=(ox - 0.45, oy - 0.09, oz + 0.8), mat=mats['steel_bright'], col=col)
        elec_l.parent = root
        elec_r = abs_style.create_cylinder(f"{name}_PlateR", radius=0.07, depth=0.02, rot=(R(90), 0, 0), loc=(ox + 0.45, oy - 0.09, oz + 0.8), mat=mats['steel_bright'], col=col)
        elec_r.parent = root
        g = abs_style.create_analog_gauge(f"{name}_JouleDial", loc=(ox + 0.26, oy - 0.25, oz + 0.72), rot=(90, 0, 0), radius=0.07, col=col)
        g.parent = root

    elif weapon_id == 5: # W05_Plasma_Halligan_Bar (Descansa horizontalmente en la cuna táctica)
        bar = abs_style.create_cylinder(f"{name}_Bar", radius=0.038, depth=1.45, rot=(0, R(78), 0), loc=(ox, oy, oz + 0.72), mat=mats['gunmetal'], col=col)
        bar.parent = root
        grip = abs_style.create_cylinder(f"{name}_Grip", radius=0.045, depth=0.55, rot=(0, R(78), 0), loc=(ox + 0.05, oy, oz + 0.71), mat=mats['rubber_grip'], col=col)
        grip.parent = root
        adze = abs_style.create_box(f"{name}_AdzeHead", size=(0.06, 0.28, 0.18), rot=(0, R(78), 0), loc=(ox - 0.65, oy - 0.14, oz + 0.85), mat=mats['steel_bright'], col=col)
        adze.parent = root
        pick = abs_style.create_cone(f"{name}_Pick", radius1=0.05, radius2=0.01, depth=0.28, rot=(0, R(-12), 0), loc=(ox - 0.65, oy + 0.14, oz + 0.85), mat=mats['steel_bright'], col=col)
        pick.parent = root
        fork = abs_style.create_box(f"{name}_Fork", size=(0.06, 0.18, 0.25), rot=(0, R(78), 0), loc=(ox + 0.68, oy, oz + 0.58), mat=mats['steel_bright'], col=col)
        fork.parent = root
        glow1 = abs_style.create_box(f"{name}_GlowAdze", size=(0.03, 0.14, 0.16), rot=(0, R(78), 0), loc=(ox - 0.68, oy - 0.22, oz + 0.85), mat=mats['plasma_orange'], col=col)
        glow1.parent = root
        glow2 = abs_style.create_box(f"{name}_GlowFork", size=(0.03, 0.12, 0.12), rot=(0, R(78), 0), loc=(ox + 0.72, oy, oz + 0.57), mat=mats['plasma_orange'], col=col)
        glow2.parent = root

    elif weapon_id == 6: # W06_Rotary_Rescue_Saw
        motor = abs_style.create_box(f"{name}_Motor", size=(0.38, 0.68, 0.40), loc=(ox, oy + 0.22, oz + 0.8), mat=mats['safety_orange'], col=col)
        motor.parent = root
        blade = abs_style.create_cylinder(f"{name}_DiamondBlade", radius=0.42, depth=0.025, rot=(0, R(90), 0), loc=(ox, oy - 0.70, oz + 0.8), mat=mats['steel_bright'], col=col)
        blade.parent = root
        guard = abs_style.create_cylinder(f"{name}_SparkGuard", radius=0.45, depth=0.06, rot=(0, R(90), 0), loc=(ox, oy - 0.70, oz + 0.8), mat=mats['hazard_stripes'], col=col)
        guard.parent = root
        arm = abs_style.create_box(f"{name}_SupportArm", size=(0.10, 0.55, 0.14), loc=(ox, oy - 0.35, oz + 0.8), mat=mats['gunmetal'], col=col)
        arm.parent = root
        cage = abs_style.create_torus(f"{name}_RollCage", major_r=0.28, minor_r=0.035, rot=(R(90), 0, 0), loc=(ox, oy + 0.15, oz + 1.05), mat=mats['rubber_grip'], col=col)
        cage.parent = root
        g = abs_style.create_analog_gauge(f"{name}_RPMGauge", loc=(ox + 0.20, oy + 0.10, oz + 0.95), rot=(0, 90, 0), radius=0.08, col=col)
        g.parent = root

    elif weapon_id == 7: # W07_Pneumatic_Bolt_Cutter
        jaw_l = abs_style.create_box(f"{name}_JawL", size=(0.06, 0.24, 0.32), loc=(ox - 0.08, oy - 0.55, oz + 0.8), mat=mats['steel_bright'], col=col)
        jaw_l.parent = root
        jaw_r = abs_style.create_box(f"{name}_JawR", size=(0.06, 0.24, 0.32), loc=(ox + 0.08, oy - 0.55, oz + 0.8), mat=mats['steel_bright'], col=col)
        jaw_r.parent = root
        pivot = abs_style.create_cylinder(f"{name}_PivotPin", radius=0.08, depth=0.22, rot=(0, R(90), 0), loc=(ox, oy - 0.40, oz + 0.8), mat=mats['brass_gold'], col=col)
        pivot.parent = root
        ram = abs_style.create_cylinder(f"{name}_AirRam", radius=0.12, depth=0.75, rot=(R(90), 0, 0), loc=(ox, oy + 0.10, oz + 0.8), mat=mats['hazard_yellow'], col=col)
        ram.parent = root
        band = abs_style.create_cylinder(f"{name}_RamStripes", radius=0.125, depth=0.25, rot=(R(90), 0, 0), loc=(ox, oy + 0.10, oz + 0.8), mat=mats['hazard_stripes'], col=col)
        band.parent = root
        shaft = abs_style.create_cylinder(f"{name}_ChromeRod", radius=0.06, depth=0.45, rot=(R(90), 0, 0), loc=(ox, oy - 0.22, oz + 0.8), mat=mats['steel_bright'], col=col)
        shaft.parent = root
        handle = abs_style.create_cylinder(f"{name}_TwistGrip", radius=0.045, depth=0.35, rot=(R(90), 0, 0), loc=(ox, oy + 0.60, oz + 0.8), mat=mats['rubber_grip'], col=col)
        handle.parent = root
        g = abs_style.create_analog_gauge(f"{name}_PressureDial", loc=(ox + 0.14, oy + 0.10, oz + 0.90), rot=(0, 90, 0), radius=0.09, col=col)
        g.parent = root

    elif weapon_id == 8: # W08_Chemical_Foam_Mortar
        drum = abs_style.create_cylinder(f"{name}_RevolvingDrum", radius=0.22, depth=0.45, rot=(R(90), 0, 0), loc=(ox, oy, oz + 0.8), mat=mats['gunmetal'], col=col)
        drum.parent = root
        band = abs_style.create_cylinder(f"{name}_DrumStripes", radius=0.225, depth=0.15, rot=(R(90), 0, 0), loc=(ox, oy, oz + 0.8), mat=mats['hazard_stripes'], col=col)
        band.parent = root
        for i in range(4):
            ang = i * (math.pi / 2)
            can = abs_style.create_cylinder(f"{name}_Chamber_{i}", radius=0.07, depth=0.46, rot=(R(90), 0, 0), loc=(ox + math.cos(ang)*0.12, oy, oz + 0.8 + math.sin(ang)*0.12), mat=mats['hazard_yellow'], col=col)
            can.parent = root
        barrel = abs_style.create_cylinder(f"{name}_Barrel", radius=0.10, depth=0.85, rot=(R(90), 0, 0), loc=(ox, oy - 0.60, oz + 0.8), mat=mats['gunmetal'], col=col)
        barrel.parent = root
        diff = abs_style.create_cone(f"{name}_MuzzleDiffuser", radius1=0.18, radius2=0.10, depth=0.30, rot=(R(90), 0, 0), loc=(ox, oy - 1.05, oz + 0.8), mat=mats['brass_gold'], col=col)
        diff.parent = root
        stock = abs_style.create_box(f"{name}_Stock", size=(0.08, 0.45, 0.18), loc=(ox, oy + 0.45, oz + 0.72), mat=mats['carbon_fiber'], col=col)
        stock.parent = root
        g = abs_style.create_analog_gauge(f"{name}_MixGauge", loc=(ox + 0.16, oy - 0.40, oz + 0.90), rot=(0, 90, 0), radius=0.08, col=col)
        g.parent = root

    elif weapon_id == 9: # W09_Thermite_Breach_Lance
        lance = abs_style.create_cylinder(f"{name}_LanceShaft", radius=0.05, depth=1.6, rot=(R(90), 0, 0), loc=(ox, oy - 0.35, oz + 0.8), mat=mats['steel_bright'], col=col)
        lance.parent = root
        shroud = abs_style.create_cylinder(f"{name}_HeatShroud", radius=0.08, depth=0.8, rot=(R(90), 0, 0), loc=(ox, oy - 0.20, oz + 0.8), mat=mats['gunmetal'], col=col)
        shroud.parent = root
        tip = abs_style.create_cone(f"{name}_ThermiteTip", radius1=0.07, radius2=0.01, depth=0.35, rot=(R(90), 0, 0), loc=(ox, oy - 1.25, oz + 0.8), mat=mats['plasma_orange'], col=col)
        tip.parent = root
        shield = abs_style.create_cylinder(f"{name}_HeatShield", radius=0.28, depth=0.03, rot=(R(90), 0, 0), loc=(ox, oy + 0.25, oz + 0.8), mat=mats['hazard_stripes'], col=col)
        shield.parent = root
        grip = abs_style.create_cylinder(f"{name}_Handle", radius=0.045, depth=0.45, rot=(R(90), 0, 0), loc=(ox, oy + 0.55, oz + 0.8), mat=mats['rubber_grip'], col=col)
        grip.parent = root
        g = abs_style.create_analog_gauge(f"{name}_O2Dial", loc=(ox + 0.12, oy + 0.35, oz + 0.92), rot=(0, 90, 0), radius=0.09, col=col)
        g.parent = root

    elif weapon_id == 10: # W10_EMP_Disruptor_Pistol
        receiver = abs_style.create_box(f"{name}_Chassis", size=(0.14, 0.65, 0.25), loc=(ox, oy, oz + 0.8), mat=mats['gunmetal'], col=col)
        receiver.parent = root
        grip = abs_style.create_box(f"{name}_PistolGrip", size=(0.10, 0.14, 0.32), rot=(R(18), 0, 0), loc=(ox, oy + 0.22, oz + 0.58), mat=mats['rubber_grip'], col=col)
        grip.parent = root
        barrel = abs_style.create_cylinder(f"{name}_CoreBarrel", radius=0.045, depth=0.65, rot=(R(90), 0, 0), loc=(ox, oy - 0.45, oz + 0.8), mat=mats['steel_bright'], col=col)
        barrel.parent = root
        for c in range(4):
            cy = oy - 0.25 - c * 0.10
            coil = abs_style.create_cylinder(f"{name}_Coil_{c}", radius=0.085, depth=0.06, rot=(R(90), 0, 0), loc=(ox, cy, oz + 0.8), mat=mats['copper'], col=col)
            coil.parent = root
        cap = abs_style.create_cylinder(f"{name}_EMPCapacitor", radius=0.05, depth=0.35, rot=(R(90), 0, 0), loc=(ox, oy, oz + 0.95), mat=mats['emp_blue'], col=col)
        cap.parent = root
        g = abs_style.create_analog_gauge(f"{name}_PulseRate", loc=(ox + 0.08, oy + 0.10, oz + 0.82), rot=(0, 90, 0), radius=0.06, col=col)
        g.parent = root

    elif weapon_id == 11: # W11_Hydraulic_Spreader_Jaws
        arm_l = abs_style.create_box(f"{name}_ArmL", size=(0.06, 0.35, 0.18), rot=(0, 0, R(20)), loc=(ox - 0.14, oy - 0.55, oz + 0.8), mat=mats['steel_bright'], col=col)
        arm_l.parent = root
        arm_r = abs_style.create_box(f"{name}_ArmR", size=(0.06, 0.35, 0.18), rot=(0, 0, R(-20)), loc=(ox + 0.14, oy - 0.55, oz + 0.8), mat=mats['steel_bright'], col=col)
        arm_r.parent = root
        cyl = abs_style.create_cylinder(f"{name}_RamCylinder", radius=0.15, depth=0.75, rot=(R(90), 0, 0), loc=(ox, oy, oz + 0.8), mat=mats['hazard_yellow'], col=col)
        cyl.parent = root
        band = abs_style.create_cylinder(f"{name}_RamBand", radius=0.155, depth=0.25, rot=(R(90), 0, 0), loc=(ox, oy, oz + 0.8), mat=mats['hazard_stripes'], col=col)
        band.parent = root
        cage = abs_style.create_torus(f"{name}_HandleCage", major_r=0.26, minor_r=0.035, rot=(R(90), 0, 0), loc=(ox, oy + 0.10, oz + 0.8), mat=mats['rubber_grip'], col=col)
        cage.parent = root
        g = abs_style.create_analog_gauge(f"{name}_TonGauge", loc=(ox + 0.16, oy, oz + 0.92), rot=(0, 90, 0), radius=0.09, col=col)
        g.parent = root

    elif weapon_id == 12: # W12_Cryo_Grenade_Launcher
        frame = abs_style.create_box(f"{name}_Receiver", size=(0.16, 0.70, 0.28), loc=(ox, oy, oz + 0.8), mat=mats['gunmetal'], col=col)
        frame.parent = root
        drum = abs_style.create_cylinder(f"{name}_6Drum", radius=0.20, depth=0.38, rot=(R(90), 0, 0), loc=(ox, oy - 0.05, oz + 0.8), mat=mats['carbon_fiber'], col=col)
        drum.parent = root
        barrel = abs_style.create_cylinder(f"{name}_FlutedBarrel", radius=0.09, depth=0.75, rot=(R(90), 0, 0), loc=(ox, oy - 0.65, oz + 0.8), mat=mats['gunmetal'], col=col)
        barrel.parent = root
        grip = abs_style.create_cylinder(f"{name}_Grip", radius=0.045, depth=0.32, rot=(R(15), 0, 0), loc=(ox, oy + 0.28, oz + 0.58), mat=mats['rubber_grip'], col=col)
        grip.parent = root
        core = abs_style.create_cylinder(f"{name}_FrostVents", radius=0.04, depth=0.22, rot=(R(90), 0, 0), loc=(ox, oy - 0.85, oz + 0.8), mat=mats['cryo_cyan'], col=col)
        core.parent = root
        g = abs_style.create_analog_gauge(f"{name}_CryoGauge", loc=(ox + 0.10, oy + 0.12, oz + 0.88), rot=(0, 90, 0), radius=0.07, col=col)
        g.parent = root

    elif weapon_id == 13: # W13_Pneumatic_Breaching_Ram
        body = abs_style.create_cylinder(f"{name}_RamBody", radius=0.18, depth=1.35, rot=(R(90), 0, 0), loc=(ox, oy, oz + 0.8), mat=mats['gunmetal'], col=col)
        body.parent = root
        band = abs_style.create_cylinder(f"{name}_HazardStripes", radius=0.185, depth=0.35, rot=(R(90), 0, 0), loc=(ox, oy - 0.15, oz + 0.8), mat=mats['hazard_stripes'], col=col)
        band.parent = root
        head = abs_style.create_cylinder(f"{name}_TungstenHead", radius=0.16, depth=0.35, rot=(R(90), 0, 0), loc=(ox, oy - 0.85, oz + 0.8), mat=mats['steel_bright'], col=col)
        head.parent = root
        h1 = abs_style.create_torus(f"{name}_HandleF", major_r=0.22, minor_r=0.04, rot=(0, R(90), 0), loc=(ox, oy - 0.25, oz + 1.05), mat=mats['rubber_grip'], col=col)
        h1.parent = root
        h2 = abs_style.create_torus(f"{name}_HandleR", major_r=0.22, minor_r=0.04, rot=(0, R(90), 0), loc=(ox, oy + 0.35, oz + 1.05), mat=mats['rubber_grip'], col=col)
        h2.parent = root
        g = abs_style.create_analog_gauge(f"{name}_KineticDial", loc=(ox + 0.19, oy, oz + 0.8), rot=(0, 90, 0), radius=0.10, col=col)
        g.parent = root

    elif weapon_id == 14: # W14_Magnetic_Net_Launcher
        frame = abs_style.create_box(f"{name}_Receiver", size=(0.32, 0.65, 0.28), loc=(ox, oy, oz + 0.8), mat=mats['gunmetal'], col=col)
        frame.parent = root
        for i in range(4):
            qx = ox - 0.09 + (i % 2) * 0.18
            qz = oz + 0.73 + (i // 2) * 0.14
            cup = abs_style.create_cone(f"{name}_MuzzleCup_{i}", radius1=0.08, radius2=0.045, depth=0.35, rot=(R(90), 0, 0), loc=(qx, oy - 0.48, qz), mat=mats['copper'], col=col)
            cup.parent = root
        optic = abs_style.create_cylinder(f"{name}_LaserOptic", radius=0.035, depth=0.32, rot=(R(90), 0, 0), loc=(ox, oy - 0.45, oz + 0.94), mat=mats['emp_blue'], col=col)
        optic.parent = root
        grip = abs_style.create_box(f"{name}_Grip", size=(0.10, 0.14, 0.32), rot=(R(18), 0, 0), loc=(ox, oy + 0.20, oz + 0.58), mat=mats['rubber_grip'], col=col)
        grip.parent = root
        g = abs_style.create_analog_gauge(f"{name}_FluxDial", loc=(ox + 0.17, oy - 0.15, oz + 0.82), rot=(0, 90, 0), radius=0.07, col=col)
        g.parent = root

    elif weapon_id == 15: # W15_Chemical_Neutralizer_Pack
        t1 = abs_style.create_cylinder(f"{name}_TankA", radius=0.17, depth=1.1, loc=(ox - 0.15, oy + 0.15, oz + 0.65), mat=mats['hazard_yellow'], col=col)
        t1.parent = root
        t2 = abs_style.create_cylinder(f"{name}_TankB", radius=0.17, depth=1.1, loc=(ox + 0.15, oy + 0.15, oz + 0.65), mat=mats['hazard_yellow'], col=col)
        t2.parent = root
        b1 = abs_style.create_cylinder(f"{name}_StripesA", radius=0.175, depth=0.25, loc=(ox - 0.15, oy + 0.15, oz + 0.65), mat=mats['hazard_stripes'], col=col)
        b1.parent = root
        b2 = abs_style.create_cylinder(f"{name}_StripesB", radius=0.175, depth=0.25, loc=(ox + 0.15, oy + 0.15, oz + 0.65), mat=mats['hazard_stripes'], col=col)
        b2.parent = root
        lance = abs_style.create_cylinder(f"{name}_SprayLance", radius=0.035, depth=1.2, rot=(R(90), 0, 0), loc=(ox, oy - 0.45, oz + 0.75), mat=mats['steel_bright'], col=col)
        lance.parent = root
        nozzle = abs_style.create_cone(f"{name}_Atomizer", radius1=0.10, radius2=0.035, depth=0.22, rot=(R(90), 0, 0), loc=(ox, oy - 1.10, oz + 0.75), mat=mats['brass_gold'], col=col)
        nozzle.parent = root
        hose = abs_style.create_cylinder(f"{name}_FeedHose", radius=0.045, depth=0.85, rot=(R(45), 0, 0), loc=(ox, oy - 0.10, oz + 0.55), mat=mats['hose_red'], col=col)
        hose.parent = root
        g = abs_style.create_analog_gauge(f"{name}_DeconGauge", loc=(ox, oy - 0.20, oz + 0.88), rot=(90, 0, 0), radius=0.09, col=col)
        g.parent = root

    elif weapon_id == 16: # W16_Emergency_SOS_Flare_Gun
        body = abs_style.create_box(f"{name}_Frame", size=(0.14, 0.55, 0.24), loc=(ox, oy, oz + 0.8), mat=mats['safety_orange'], col=col)
        body.parent = root
        grip = abs_style.create_box(f"{name}_Grip", size=(0.10, 0.14, 0.30), rot=(R(18), 0, 0), loc=(ox, oy + 0.18, oz + 0.58), mat=mats['rubber_grip'], col=col)
        grip.parent = root
        barrel = abs_style.create_cylinder(f"{name}_BreakBarrel", radius=0.075, depth=0.55, rot=(R(90), 0, 0), loc=(ox, oy - 0.38, oz + 0.82), mat=mats['safety_orange'], col=col)
        barrel.parent = root
        bell = abs_style.create_cone(f"{name}_MuzzleBell", radius1=0.15, radius2=0.075, depth=0.25, rot=(R(90), 0, 0), loc=(ox, oy - 0.70, oz + 0.82), mat=mats['brass_gold'], col=col)
        bell.parent = root
        hinge = abs_style.create_cylinder(f"{name}_BreakHinge", radius=0.05, depth=0.16, rot=(0, R(90), 0), loc=(ox, oy - 0.12, oz + 0.72), mat=mats['steel_bright'], col=col)
        hinge.parent = root
        flare = abs_style.create_cylinder(f"{name}_LoadedFlare", radius=0.065, depth=0.22, rot=(R(90), 0, 0), loc=(ox, oy - 0.35, oz + 0.82), mat=mats['plasma_orange'], col=col)
        flare.parent = root

    elif weapon_id == 17: # W17_Sonic_Fire_Suppressor
        dish = abs_style.create_cone(f"{name}_AcousticDish", radius1=0.48, radius2=0.08, depth=0.45, rot=(R(90), 0, 0), loc=(ox, oy - 0.65, oz + 0.8), mat=mats['gunmetal'], col=col)
        dish.parent = root
        needle = abs_style.create_cone(f"{name}_FocalEmitter", radius1=0.045, radius2=0.01, depth=0.35, rot=(R(90), 0, 0), loc=(ox, oy - 0.80, oz + 0.8), mat=mats['steel_bright'], col=col)
        needle.parent = root
        body = abs_style.create_cylinder(f"{name}_Chamber", radius=0.18, depth=0.75, rot=(R(90), 0, 0), loc=(ox, oy + 0.10, oz + 0.8), mat=mats['carbon_fiber'], col=col)
        body.parent = root
        band = abs_style.create_cylinder(f"{name}_Stripes", radius=0.185, depth=0.20, rot=(R(90), 0, 0), loc=(ox, oy + 0.10, oz + 0.8), mat=mats['hazard_stripes'], col=col)
        band.parent = root
        grip = abs_style.create_box(f"{name}_Grip", size=(0.10, 0.14, 0.32), rot=(R(18), 0, 0), loc=(ox, oy + 0.25, oz + 0.58), mat=mats['rubber_grip'], col=col)
        grip.parent = root
        g = abs_style.create_analog_gauge(f"{name}_HertzMeter", loc=(ox + 0.19, oy + 0.15, oz + 0.85), rot=(0, 90, 0), radius=0.09, col=col)
        g.parent = root

    elif weapon_id == 18: # W18_Arc_Welding_Cutting_Torch
        shaft = abs_style.create_cylinder(f"{name}_TorchBody", radius=0.05, depth=0.95, rot=(R(90), 0, 0), loc=(ox, oy, oz + 0.8), mat=mats['brass_gold'], col=col)
        shaft.parent = root
        head = abs_style.create_cylinder(f"{name}_TorchHead", radius=0.065, depth=0.35, rot=(R(45), 0, 0), loc=(ox, oy - 0.55, oz + 0.85), mat=mats['copper'], col=col)
        head.parent = root
        flame = abs_style.create_cone(f"{name}_PlasmaArc", radius1=0.06, radius2=0.01, depth=0.28, rot=(R(45), 0, 0), loc=(ox, oy - 0.72, oz + 0.98), mat=mats['plasma_orange'], col=col)
        flame.parent = root
        grip = abs_style.create_cylinder(f"{name}_Handle", radius=0.06, depth=0.45, rot=(R(90), 0, 0), loc=(ox, oy + 0.30, oz + 0.8), mat=mats['rubber_grip'], col=col)
        grip.parent = root
        hose = abs_style.create_cylinder(f"{name}_DualLine", radius=0.05, depth=0.75, rot=(R(60), 0, 0), loc=(ox, oy + 0.65, oz + 0.60), mat=mats['hose_red'], col=col)
        hose.parent = root
        g1 = abs_style.create_analog_gauge(f"{name}_FuelGauge", loc=(ox + 0.10, oy + 0.10, oz + 0.90), rot=(0, 90, 0), radius=0.07, col=col)
        g1.parent = root
        g2 = abs_style.create_analog_gauge(f"{name}_O2Gauge", loc=(ox - 0.10, oy + 0.10, oz + 0.90), rot=(0, -90, 0), radius=0.07, col=col)
        g2.parent = root

    elif weapon_id == 19: # W19_Tripod_Mounted_Foam_Cannon
        cannon = abs_style.create_cylinder(f"{name}_CannonBarrel", radius=0.18, depth=1.35, rot=(R(90), 0, 0), loc=(ox, oy, oz + 0.95), mat=mats['hazard_yellow'], col=col)
        cannon.parent = root
        band = abs_style.create_cylinder(f"{name}_CannonStripes", radius=0.185, depth=0.35, rot=(R(90), 0, 0), loc=(ox, oy - 0.15, oz + 0.95), mat=mats['hazard_stripes'], col=col)
        band.parent = root
        muzzle = abs_style.create_cone(f"{name}_MuzzleBell", radius1=0.30, radius2=0.18, depth=0.40, rot=(R(90), 0, 0), loc=(ox, oy - 0.85, oz + 0.95), mat=mats['brass_gold'], col=col)
        muzzle.parent = root
        hub = abs_style.create_cylinder(f"{name}_TripodHub", radius=0.12, depth=0.22, loc=(ox, oy, oz + 0.70), mat=mats['gunmetal'], col=col)
        hub.parent = root
        for i in range(3):
            ang = i * (2 * math.pi / 3)
            leg = abs_style.create_cylinder(f"{name}_Leg_{i}", radius=0.045, depth=0.95, rot=(R(40)*math.cos(ang), R(40)*math.sin(ang), 0), loc=(ox + math.sin(ang)*0.32, oy + math.cos(ang)*0.32, oz + 0.35), mat=mats['steel_bright'], col=col)
            leg.parent = root
        spades = abs_style.create_box(f"{name}_SpadeGrip", size=(0.35, 0.08, 0.22), loc=(ox, oy + 0.65, oz + 0.95), mat=mats['rubber_grip'], col=col)
        spades.parent = root
        g = abs_style.create_analog_gauge(f"{name}_FlowGauge", loc=(ox + 0.20, oy, oz + 1.05), rot=(0, 90, 0), radius=0.11, col=col)
        g.parent = root

    elif weapon_id == 20: # W20_Tactical_Rescue_Machete
        blade = abs_style.create_box(f"{name}_TitaniumBlade", size=(0.04, 0.85, 0.18), loc=(ox, oy - 0.25, oz + 0.8), mat=mats['gunmetal'], col=col)
        blade.parent = root
        edge = abs_style.create_box(f"{name}_CuttingEdge", size=(0.015, 0.80, 0.06), loc=(ox, oy - 0.25, oz + 0.70), mat=mats['steel_bright'], col=col)
        edge.parent = root
        stripe = abs_style.create_box(f"{name}_SpineStripes", size=(0.045, 0.60, 0.05), loc=(ox, oy - 0.20, oz + 0.88), mat=mats['hazard_stripes'], col=col)
        stripe.parent = root
        for s in range(8):
            sy = oy - 0.50 + s * 0.07
            saw = abs_style.create_cone(f"{name}_SpineTooth_{s}", radius1=0.02, radius2=0.005, depth=0.05, rot=(R(180), 0, 0), loc=(ox, sy, oz + 0.92), mat=mats['steel_bright'], col=col)
            saw.parent = root
        grip = abs_style.create_cylinder(f"{name}_CordHandle", radius=0.045, depth=0.38, rot=(R(90), 0, 0), loc=(ox, oy + 0.35, oz + 0.8), mat=mats['safety_orange'], col=col)
        grip.parent = root
        pommel = abs_style.create_box(f"{name}_SteelPommel", size=(0.06, 0.08, 0.12), loc=(ox, oy + 0.56, oz + 0.8), mat=mats['steel_bright'], col=col)
        pommel.parent = root

    return root

def generate_weapons_scene(save_blend=True):
    print("================================================================")
    print("   GENERANDO ARSENAL OFICIAL DE 20 ARMAS (CARTOON / INDUSTRIAL)")
    print("================================================================")
    abs_style.reset_comic_scene(bg_color=(0.02, 0.025, 0.035, 1.0), bg_strength=0.70, ink_thickness=2.6)
    col = abs_style.create_collection("Arsenal_Weapons_20")
    mats = init_weapons_materials()

    # Disposición en Anfiteatro Escalonado: 2 Filas de 10 Armas en pedestales tácticos
    # Fila 1: Y = 0.0, Z = 0.0 (Armas 1 a 10)
    # Fila 2: Y = 3.2, Z = 0.85 (Armas 11 a 20)
    spacing_x = 2.4
    
    # Grada estructural corrida para Fila 2
    terrace_mat = abs_style.get_comic_material("W_Terrace_Mat", base_color=(0.10, 0.12, 0.15), roughness=0.45, metallic=0.60)
    abs_style.create_box("Armory_Tier2", size=(28.0, 3.2, 0.85), loc=(0, 3.2, 0.425), mat=terrace_mat, col=col)
    abs_style.create_box("Tier2_HazardTrim", size=(28.0, 0.08, 0.08), loc=(0, 1.58, 0.83), mat=mats['hazard_stripes'], col=col)

    # Suelo general
    floor_mat = abs_style.get_comic_material("Armory_Floor", base_color=(0.035, 0.040, 0.048), roughness=0.90, metallic=0.0)
    abs_style.create_box("Armory_Floor", size=(34.0, 18.0, 0.10), loc=(0, 1.75, -0.05), mat=floor_mat, col=col)
    
    # Pared de fondo con I-beams y tuberías industriales
    wall_mat = abs_style.get_comic_material("Armory_Wall", base_color=(0.12, 0.14, 0.18), roughness=0.50, metallic=0.70)
    abs_style.create_box("Armory_Wall_Back", size=(34.0, 0.2, 7.0), loc=(0, 5.8, 3.5), mat=wall_mat, col=col)
    for bx in [-12.0, -6.0, 0.0, 6.0, 12.0]:
        abs_style.create_box(f"IBeam_{bx}", size=(0.50, 0.18, 7.0), loc=(bx, 5.65, 3.5), mat=mats['gunmetal'], col=col)
    abs_style.create_cylinder("Armory_Pipe", radius=0.18, depth=34.0, rot=(0, R(90), 0), loc=(0, 5.55, 5.2), mat=mats['gunmetal'], col=col)
    abs_style.create_box("Armory_HazardLine", size=(32.0, 0.05, 0.14), loc=(0, 5.62, 4.2), mat=mats['hazard_stripes'], col=col)

    pedestal_mat = abs_style.get_comic_material("Pedestal_Dark", base_color=(0.12, 0.14, 0.16), roughness=0.35, metallic=0.60)
    plaque_mat = mats['brass_gold']
    
    closeups = {}

    for idx, (wid, wname, title, tier, desc) in enumerate(WEAPONS_DATA):
        row = idx // 10
        col_idx = idx % 10
        x = (col_idx - 4.5) * spacing_x
        y = 0.0 if row == 0 else 3.2
        z = 0.0 if row == 0 else 0.85
        
        # Pedestal dedicado para cada arma
        abs_style.create_box(f"Plinth_{wname}", size=(1.8, 1.4, 0.25), loc=(x, y, z + 0.125), mat=pedestal_mat, col=col)
        abs_style.create_box(f"Plaque_{wname}", size=(0.95, 0.02, 0.10), loc=(x, y - 0.71, z + 0.125), mat=plaque_mat, col=col)
        # Soportes en 'V' de fijación mecánica con almohadillas de goma
        abs_style.create_cylinder(f"StandL_{wname}", radius=0.035, depth=0.38, loc=(x - 0.35, y, z + 0.44), mat=mats['gunmetal'], col=col)
        abs_style.create_cylinder(f"StandR_{wname}", radius=0.035, depth=0.38, loc=(x + 0.35, y, z + 0.44), mat=mats['gunmetal'], col=col)
        abs_style.create_box(f"StandPadL_{wname}", size=(0.09, 0.14, 0.04), loc=(x - 0.35, y, z + 0.63), mat=mats['rubber_grip'], col=col)
        abs_style.create_box(f"StandPadR_{wname}", size=(0.09, 0.14, 0.04), loc=(x + 0.35, y, z + 0.63), mat=mats['rubber_grip'], col=col)

        # Construir modelo del arma
        build_weapon(wid, wname, (x, y, z), col, mats)

    # Iluminación de Estudio Cel-Shading
    abs_style.setup_studio_lighting(sun_energy=4.6, rim_energy=4.0, fill_energy=2.0,
                                    sun_rot=(46, 16, -32), rim_rot=(-58, 0, 160))

    # Cámara Panorámica General (Abarca las 20 armas escalonadas con perfecta legibilidad)
    abs_style.setup_camera(name="Camera_Arsenal_Panorama", loc=(0.0, -15.2, 5.8), target=(0.0, 1.5, 1.25), focal_length=35)

    if save_blend:
        blend_path = os.path.join(abs_style.PROJECT_ROOT, "Art", "Blender", "Arsenal_20_Armas_Oficial.blend")
        bpy.ops.wm.save_as_mainfile(filepath=blend_path)
        print(f"[+] Arsenal Blend saved: {blend_path}")

    pano_render_path = os.path.join(abs_style.RENDERS_DIR, "Showcase_Arsenal_20_Armas_Panorama.png")
    abs_style.render_and_save("Showcase_Arsenal_20_Armas_Panorama.png", res_x=2560, res_y=850)

    # Tabla de encuadres personalizados por arma (CERO partes cortadas)
    WEAPON_CAMERAS = {
        1:  {"cam": (1.60, -2.60, 1.35), "tgt": (0.0, -0.15, 0.75), "lens": 36},
        2:  {"cam": (1.35, -2.35, 1.30), "tgt": (0.0,  0.00, 0.75), "lens": 38},
        3:  {"cam": (1.45, -2.45, 1.45), "tgt": (0.0, -0.10, 0.85), "lens": 38},
        4:  {"cam": (1.30, -2.20, 1.30), "tgt": (0.0,  0.00, 0.78), "lens": 40},
        5:  {"cam": (1.35, -2.35, 1.30), "tgt": (0.0,  0.00, 0.75), "lens": 38},
        6:  {"cam": (1.50, -2.50, 1.40), "tgt": (0.0, -0.15, 0.80), "lens": 38},
        7:  {"cam": (1.40, -2.35, 1.35), "tgt": (0.0, -0.10, 0.78), "lens": 38},
        8:  {"cam": (1.50, -2.45, 1.35), "tgt": (0.0, -0.10, 0.78), "lens": 38},
        9:  {"cam": (1.60, -2.60, 1.35), "tgt": (0.0, -0.15, 0.75), "lens": 36},
        10: {"cam": (1.20, -2.10, 1.30), "tgt": (0.0,  0.00, 0.75), "lens": 42},
        11: {"cam": (1.45, -2.40, 1.35), "tgt": (0.0, -0.10, 0.78), "lens": 38},
        12: {"cam": (1.40, -2.35, 1.35), "tgt": (0.0, -0.05, 0.78), "lens": 40},
        13: {"cam": (1.50, -2.50, 1.35), "tgt": (0.0, -0.10, 0.78), "lens": 38},
        14: {"cam": (1.30, -2.25, 1.30), "tgt": (0.0, -0.05, 0.75), "lens": 40},
        15: {"cam": (1.60, -2.60, 1.45), "tgt": (0.0, -0.10, 0.85), "lens": 36},
        16: {"cam": (1.20, -2.10, 1.30), "tgt": (0.0,  0.00, 0.75), "lens": 42},
        17: {"cam": (1.50, -2.55, 1.35), "tgt": (0.0, -0.15, 0.78), "lens": 38},
        18: {"cam": (1.40, -2.35, 1.35), "tgt": (0.0, -0.05, 0.78), "lens": 38},
        19: {"cam": (1.80, -2.90, 1.50), "tgt": (0.0, -0.10, 0.85), "lens": 32},
        20: {"cam": (1.35, -2.35, 1.30), "tgt": (0.0,  0.00, 0.75), "lens": 38},
    }

    # Close-ups 3/4 heroicos individuales para cada una de las 20 armas
    for idx, (wid, wname, _, _, _) in enumerate(WEAPONS_DATA):
        row = idx // 10
        col_idx = idx % 10
        x = (col_idx - 4.5) * spacing_x
        y = 0.0 if row == 0 else 3.2
        z = 0.0 if row == 0 else 0.85
        
        cfg = WEAPON_CAMERAS.get(wid, {"cam": (1.4, -2.4, 1.35), "tgt": (0, 0, 0.8), "lens": 38})
        cam_loc = (x + cfg["cam"][0], y + cfg["cam"][1], z + cfg["cam"][2])
        target = (x + cfg["tgt"][0], y + cfg["tgt"][1], z + cfg["tgt"][2])
        
        abs_style.setup_camera(name=f"Cam_Close_{wname}", loc=cam_loc, target=target, focal_length=cfg["lens"])
        close_file = f"CloseUp_{wname}.png"
        abs_style.render_and_save(close_file, res_x=1280, res_y=960)
        closeups[wid] = os.path.join(abs_style.RENDERS_DIR, close_file)

    generate_weapons_technical_sheet(pano_render_path, closeups)
    print("[+] Arsenal Oficial de 20 Armas Renderizado y Compuesto al 100%!")

def generate_weapons_technical_sheet(pano_path, closeups):
    import textwrap
    W, H = 2560, 1440
    canvas = Image.new("RGBA", (W, H), (14, 17, 22, 255))
    draw = ImageDraw.Draw(canvas)
    
    try:
        font_title = ImageFont.truetype("arialbd.ttf", 26)
        font_sub = ImageFont.truetype("arialbd.ttf", 15)
        font_pill = ImageFont.truetype("arialbd.ttf", 13)
        font_card_title = ImageFont.truetype("arialbd.ttf", 11)
        font_card_desc = ImageFont.truetype("arial.ttf", 9)
    except:
        font_title = font_sub = font_pill = font_card_title = font_card_desc = ImageFont.load_default()
        
    draw.text((40, 20), "ASTRA HAZARD // ARSENAL TÁCTICO & EQUIPAMIENTO PESADO", fill=(245, 166, 35), font=font_sub)
    draw.text((40, 46), "ARSENAL COMPLETO DE 20 ARMAS Y HERRAMIENTAS DE BOMBERO // CARTOON INDUSTRIAL PBR & CEL-SHADING", fill=(255, 255, 255), font=font_title)
    
    pills = [
        ("20 ARMAS TÁCTICAS", (230, 126, 34)),
        ("TEXTURAS CARTOON/PBR", (41, 128, 185)),
        ("CEL-SHADING CÓMIC", (155, 89, 182)),
        ("FREESTYLE INK 2.6PX", (39, 174, 96)),
        ("BLENDER 5.2 LTS", (108, 92, 231))
    ]
    cur_x = W - 40
    for text, bg_col in reversed(pills):
        tw = len(text) * 8 + 20
        cur_x -= tw
        draw.rounded_rectangle((cur_x, 38, cur_x + tw - 8, 68), radius=5, fill=bg_col)
        draw.text((cur_x + 8, 45), text, fill=(255, 255, 255), font=font_pill)
        cur_x -= 8
        
    draw.line((40, 95, W - 40, 95), fill=(45, 52, 65), width=2)
    
    # Panorama superior 16:5 (Redimensionado con marco)
    if os.path.exists(pano_path):
        pan_img = Image.open(pano_path).convert("RGBA")
        pan_w = W - 80
        pan_h = 580
        pan_resized = pan_img.resize((pan_w, pan_h), Image.Resampling.LANCZOS)
        canvas.paste(pan_resized, (40, 110))
        draw.rectangle((40, 110, 40 + pan_w, 110 + pan_h), outline=(45, 52, 65), width=2)
        
    # Grilla de 20 tarjetas en la parte inferior: 2 filas x 10 columnas
    cols = 10
    rows = 2
    spacing_x = 10
    spacing_y = 10
    total_w = W - 80
    card_w = int((total_w - (cols - 1) * spacing_x) / cols)
    card_h = 345
    start_y = 715
    
    tier_colors = {
        "TIER 1": (230, 126, 34),
        "TIER 2": (41, 128, 185),
        "TIER 3": (155, 89, 182)
    }

    for idx, (wid, wname, title, tier, desc) in enumerate(WEAPONS_DATA):
        r = idx // cols
        c = idx % cols
        cx = 40 + c * (card_w + spacing_x)
        cy = start_y + r * (card_h + spacing_y)
        
        tier_key = tier.split(" // ")[0]
        color_accent = tier_colors.get(tier_key, (245, 166, 35))
        
        # Fondo tarjeta
        draw.rounded_rectangle((cx, cy, cx + card_w, cy + card_h), radius=5, fill=(20, 24, 30, 255), outline=(45, 52, 65), width=1)
        draw.rounded_rectangle((cx, cy, cx + card_w, cy + 4), radius=2, fill=color_accent)
        
        # Miniatura superior de la tarjeta
        img_path = closeups.get(wid)
        if img_path and os.path.exists(img_path):
            c_img = Image.open(img_path).convert("RGBA")
            thumb_h = 155
            c_thumb = c_img.resize((card_w - 12, thumb_h), Image.Resampling.LANCZOS)
            canvas.paste(c_thumb, (cx + 6, cy + 10))
            draw.rectangle((cx + 6, cy + 10, cx + card_w - 6, cy + 10 + thumb_h), outline=(45, 52, 65), width=1)
            
        # Textos informativos con ajuste dinámico de líneas (CERO truncamiento de texto)
        draw.text((cx + 6, cy + 172), tier, fill=color_accent, font=font_card_desc)
        
        title_lines = textwrap.wrap(title, width=19)
        t_y = cy + 186
        for tl in title_lines[:2]:
            draw.text((cx + 6, t_y), tl, fill=(255, 255, 255), font=font_card_title)
            t_y += 13
            
        draw.line([(cx + 6, t_y + 3), (cx + card_w - 6, t_y + 3)], fill=(45, 52, 65), width=1)
        
        lines = desc.split("\n")
        ly = t_y + 7
        for line in lines:
            b_lines = textwrap.wrap(line, width=24)
            for bl in b_lines:
                draw.text((cx + 6, ly), bl, fill=(180, 190, 205), font=font_card_desc)
                ly += 13
            
        # Píldora de estado
        draw.rounded_rectangle((cx + 6, cy + card_h - 24, cx + card_w - 6, cy + card_h - 7), radius=3, fill=(15, 18, 22))
        draw.text((cx + 10, cy + card_h - 21), "VERIFICADO PBR 100%", fill=color_accent, font=font_card_desc)

    master_path = os.path.join(abs_style.RENDERS_DIR, "Showcase_Arsenal_20_Armas_Master.png")
    canvas.save(master_path)
    print(f"[+] Lámina Maestra Arsenal generada con éxito: {master_path}")
    shutil.copy2(master_path, os.path.join(abs_style.ARTIFACT_DIR, "Showcase_Arsenal_20_Armas_Master.png"))

if __name__ == "__main__":
    generate_weapons_scene()

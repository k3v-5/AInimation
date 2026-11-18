# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Suite Oficial de 8 Herramientas Tácticas Avanzadas - Astra Hazard
# Estilo Estricto: Cartoon / Industrial PBR, Cel-Shading, Freestyle Ink 2.6px, Soportes de Cuna Reales y Cero Elementos Flotantes

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

TOOLS_DATA = [
    (1, "T01_Foam_Launcher_Heavy", "Lanzador de Espuma Pesada Compacto", "SUPRESIÓN",
     "• Cañón de mezcla con tobera de latón macizo\n• Manómetro analógico dual 250 Bar\n• Depósito presurizado con franjas hazard"),
    (2, "T02_Net_Gun_Quad_Launcher", "Lanzador de Red Electrostática Cuádruple", "CONTENCIÓN",
     "• 4 cañones de cobre con copas magnéticas\n• Puntero láser de adquisición azul\n• Chasis ergonómico con empuñadura táctica"),
    (3, "T03_Hydraulic_Jack_15T", "Gato Hidráulico de Rescate 15T", "BRECHA",
     "• Émbolo cromado de elevación pesada (15 Ton)\n• Cilindro blindado con franjas diagonales de peligro\n• Manómetro de carga y palanca de bombeo"),
    (4, "T04_Deployable_Repeater_Beacon", "Baliza Repetidora Desplegable", "COMUNICACIÓN",
     "• Trípode industrial plegable con pies de goma\n• Mástil telescópico con baliza estroboscópica azul\n• Carcasa reforzada con dial analógico de batería"),
    (5, "T05_Acoustic_Motion_Scanner", "Escáner Acústico de Supervivientes PDA", "DETECCIÓN",
     "• Fiel a la consola táctica de referencia\n• Pantalla CRT verde fósforo con matriz de barrido\n• Carcasa con cantoneras de goma antichoque"),
    (6, "T06_Retractable_Titanium_Grapnel", "Gancho Neumático de Anclaje y Rescate", "MOVILIDAD",
     "• 4 garras basculantes de aleación de titanio\n• Bobina con tambor de latón y cable trenzado\n• Cilindro neumático de eyección rápida"),
    (7, "T07_Heavy_Hydraulic_Shears", "Cizalla Hidráulica Combinada de Rescate", "DESCARCELACIÓN",
     "• Cuchillas templadas a 700 Bar de presión\n• Doble cilindro hidráulico cromado con manguitos\n• Asa perimetral de 360° con recubrimiento estriado"),
    (8, "T08_Folding_Thermal_Shield", "Escudo Térmico Plegable Balístico", "PROTECCIÓN",
     "• Triple panel articulado con bisagras pesadas\n• Visor transparente de cuarzo multicapa\n• Ribetes perimetrales con chevrons de advertencia")
]

def init_tools_materials():
    mats = {}
    mats['hazard_yellow'] = abs_style.get_comic_material("T_Hazard_Yellow", base_color=(0.98, 0.78, 0.02), roughness=0.28, metallic=0.15)
    mats['hazard_stripes'] = abs_style.get_hazard_stripes_material()
    mats['safety_orange'] = abs_style.get_comic_material("T_Safety_Orange", base_color=(0.95, 0.38, 0.05), roughness=0.30, metallic=0.10)
    mats['emergency_red'] = abs_style.get_comic_material("T_Emergency_Red", base_color=(0.88, 0.12, 0.08), roughness=0.26, metallic=0.15)
    mats['gunmetal'] = abs_style.get_comic_material("T_Gunmetal", base_color=(0.20, 0.23, 0.28), roughness=0.32, metallic=0.88)
    mats['steel_bright'] = abs_style.get_comic_material("T_Steel_Bright", base_color=(0.90, 0.92, 0.94), roughness=0.10, metallic=0.98)
    mats['brass_gold'] = abs_style.get_comic_material("T_Brass_Gold", base_color=(0.94, 0.74, 0.18), roughness=0.20, metallic=0.95)
    mats['copper'] = abs_style.get_comic_material("T_Copper", base_color=(0.92, 0.48, 0.22), roughness=0.22, metallic=0.92)
    mats['carbon_fiber'] = abs_style.get_comic_material("T_Carbon_Fiber", base_color=(0.10, 0.11, 0.14), roughness=0.45, metallic=0.35)
    mats['rubber_grip'] = abs_style.get_comic_material("T_Rubber_Grip", base_color=(0.06, 0.06, 0.08), roughness=0.85, metallic=0.0)
    mats['dial_white'] = abs_style.get_comic_material("T_Dial_White", base_color=(0.95, 0.95, 0.92), roughness=0.20, metallic=0.0)
    
    # Emisivos Cartoon
    mats['crt_green'] = abs_style.get_comic_material("T_CRT_Green", base_color=(0.10, 0.98, 0.28), roughness=0.12,
                                                     emissive_color=(0.12, 1.0, 0.32, 1.0), emissive_strength=3.5)
    mats['beacon_blue'] = abs_style.get_comic_material("T_Beacon_Blue", base_color=(0.12, 0.85, 1.0), roughness=0.08,
                                                       emissive_color=(0.15, 0.90, 1.0, 1.0), emissive_strength=4.0)
    mats['foam_canister'] = abs_style.get_comic_material("T_Foam_Canister", base_color=(0.85, 0.12, 0.08), roughness=0.28, metallic=0.20)
    mats['shield_glass'] = abs_style.get_comic_material("T_Shield_Glass", base_color=(0.70, 0.88, 0.95), roughness=0.15, alpha=0.45, is_transparent=True)
    return mats

def add_bevel(obj, width=0.025):
    bev = obj.modifiers.new("Bevel", 'BEVEL')
    bev.width = width
    bev.segments = 2
    bev.limit_method = 'ANGLE'
    bev.angle_limit = math.radians(45.0)

# Cuna de soporte industrial para herramientas de mano sobre el pedestal
def build_cradle_mount(name, origin, col, mats, cradle_span=0.55, height=0.28):
    ox, oy, oz = origin
    # Dos bases de apoyo empernadas al pedestal (que tiene superficie en oz + 0.25)
    base_z = oz + 0.25
    b1 = abs_style.create_box(f"{name}_MntBase1", size=(0.26, 0.12, 0.05), loc=(ox, oy - cradle_span*0.5, base_z + 0.025), mat=mats['gunmetal'], col=col)
    b2 = abs_style.create_box(f"{name}_MntBase2", size=(0.26, 0.12, 0.05), loc=(ox, oy + cradle_span*0.5, base_z + 0.025), mat=mats['gunmetal'], col=col)
    
    # Postes de soporte verticales con entalladura en U
    u1 = abs_style.create_box(f"{name}_MntUpright1", size=(0.10, 0.06, height), loc=(ox, oy - cradle_span*0.5, base_z + 0.05 + height*0.5), mat=mats['gunmetal'], col=col)
    u2 = abs_style.create_box(f"{name}_MntUpright2", size=(0.10, 0.06, height), loc=(ox, oy + cradle_span*0.5, base_z + 0.05 + height*0.5), mat=mats['gunmetal'], col=col)
    
    # Almohadillas protectoras de goma donde reposa la herramienta
    p1 = abs_style.create_box(f"{name}_MntPad1", size=(0.14, 0.08, 0.03), loc=(ox, oy - cradle_span*0.5, base_z + 0.05 + height + 0.015), mat=mats['rubber_grip'], col=col)
    p2 = abs_style.create_box(f"{name}_MntPad2", size=(0.14, 0.08, 0.03), loc=(ox, oy + cradle_span*0.5, base_z + 0.05 + height + 0.015), mat=mats['rubber_grip'], col=col)
    
    add_bevel(b1)
    add_bevel(b2)
    add_bevel(u1)
    add_bevel(u2)

def build_tactical_tool(tool_id, name, origin, col, mats):
    root = bpy.data.objects.new(f"Root_{name}", None)
    root.location = origin
    col.objects.link(root)
    ox, oy, oz = 0.0, 0.0, 0.0
    plinth_surface_z = oz + 0.25 # Altura exacta de la superficie superior del pedestal

    if tool_id == 1: # T01_Foam_Launcher_Heavy (Descansa sobre cuna industrial a Z=0.55)
        build_cradle_mount(name, origin, col, mats, cradle_span=0.60, height=0.25)
        tool_z = plinth_surface_z + 0.30
        
        # Cañón de mezcla en latón y franjas hazard
        cannon = abs_style.create_cylinder(f"{name}_Barrel", radius=0.15, depth=1.30, rot=(R(90), 0, 0), loc=(ox, oy, tool_z), mat=mats['hazard_yellow'], col=col)
        cannon.parent = root
        band = abs_style.create_cylinder(f"{name}_Band", radius=0.155, depth=0.32, rot=(R(90), 0, 0), loc=(ox, oy - 0.08, tool_z), mat=mats['hazard_stripes'], col=col)
        band.parent = root
        
        # Depósitos gemelos de espuma en rojo de bombero con bridas de latón
        tank1 = abs_style.create_cylinder(f"{name}_Tank1", radius=0.12, depth=0.75, loc=(ox - 0.16, oy + 0.22, tool_z + 0.02), mat=mats['emergency_red'], col=col)
        tank1.parent = root
        tank2 = abs_style.create_cylinder(f"{name}_Tank2", radius=0.12, depth=0.75, loc=(ox + 0.16, oy + 0.22, tool_z + 0.02), mat=mats['emergency_red'], col=col)
        tank2.parent = root
        
        # Tobera difusora cónica en latón macizo con anillo de orificios
        diff = abs_style.create_cone(f"{name}_Diffuser", radius1=0.26, radius2=0.15, depth=0.32, rot=(R(90), 0, 0), loc=(ox, oy - 0.78, tool_z), mat=mats['brass_gold'], col=col)
        diff.parent = root
        
        # Empuñadura superior de transporte y empuñadura trasera
        grip_f = abs_style.create_torus(f"{name}_GripF", major_r=0.16, minor_r=0.035, rot=(0, R(90), 0), loc=(ox, oy - 0.32, tool_z + 0.20), mat=mats['rubber_grip'], col=col)
        grip_f.parent = root
        grip_r = abs_style.create_cylinder(f"{name}_GripR", radius=0.045, depth=0.36, loc=(ox, oy + 0.45, tool_z - 0.14), mat=mats['rubber_grip'], col=col)
        grip_r.parent = root
        
        # Manómetro analógico de latón con dial blanco y aguja roja
        g = abs_style.create_analog_gauge(f"{name}_PressureGauge", loc=(ox + 0.18, oy - 0.10, tool_z + 0.12), rot=(0, 90, 0), radius=0.10, col=col)
        g.parent = root
        add_bevel(cannon)
        add_bevel(tank1)
        add_bevel(tank2)

    elif tool_id == 2: # T02_Net_Gun_Quad_Launcher (Descansa sobre cuna industrial a Z=0.55)
        build_cradle_mount(name, origin, col, mats, cradle_span=0.45, height=0.22)
        tool_z = plinth_surface_z + 0.27
        
        # Receptor blindado en acero oscuro con paneles de franjas de peligro
        receiver = abs_style.create_box(f"{name}_Body", size=(0.38, 0.68, 0.28), loc=(ox, oy, tool_z), mat=mats['gunmetal'], col=col)
        receiver.parent = root
        band = abs_style.create_box(f"{name}_BodyStripes", size=(0.385, 0.24, 0.285), loc=(ox, oy + 0.06, tool_z), mat=mats['hazard_stripes'], col=col)
        band.parent = root
        
        # 4 Cañones de cobre en matriz 2x2 con copas magnéticas de latón
        for i in range(4):
            qx = ox - 0.10 + (i % 2) * 0.20
            qz = tool_z - 0.07 + (i // 2) * 0.14
            barrel = abs_style.create_cylinder(f"{name}_Tube_{i}", radius=0.065, depth=0.55, rot=(R(90), 0, 0), loc=(qx, oy - 0.46, qz), mat=mats['copper'], col=col)
            barrel.parent = root
            cup = abs_style.create_cone(f"{name}_Cup_{i}", radius1=0.085, radius2=0.065, depth=0.12, rot=(R(90), 0, 0), loc=(qx, oy - 0.76, qz), mat=mats['brass_gold'], col=col)
            cup.parent = root
            add_bevel(barrel)
            
        # Puntero láser de adquisición azul en la parte superior
        laser = abs_style.create_cylinder(f"{name}_LaserSight", radius=0.035, depth=0.30, rot=(R(90), 0, 0), loc=(ox, oy - 0.38, tool_z + 0.18), mat=mats['beacon_blue'], col=col)
        laser.parent = root
        # Empuñadura de pistola ergonómica
        grip = abs_style.create_box(f"{name}_PistolGrip", size=(0.10, 0.14, 0.28), rot=(R(18), 0, 0), loc=(ox, oy + 0.22, tool_z - 0.18), mat=mats['rubber_grip'], col=col)
        grip.parent = root
        g = abs_style.create_analog_gauge(f"{name}_CapacitorGauge", loc=(ox + 0.20, oy, tool_z + 0.04), rot=(0, 90, 0), radius=0.08, col=col)
        g.parent = root
        add_bevel(receiver)

    elif tool_id == 3: # T03_Hydraulic_Jack_15T (Apoyado DIRECTAMENTE en la superficie del pedestal)
        jack_base_z = plinth_surface_z
        base = abs_style.create_box(f"{name}_Foot", size=(0.62, 0.62, 0.12), loc=(ox, oy, jack_base_z + 0.06), mat=mats['gunmetal'], col=col)
        base.parent = root
        
        # Cilindro de elevación en amarillo de seguridad con franjas diagonales de peligro
        body = abs_style.create_cylinder(f"{name}_Cylinder", radius=0.20, depth=0.88, loc=(ox, oy, jack_base_z + 0.54), mat=mats['hazard_yellow'], col=col)
        body.parent = root
        band = abs_style.create_cylinder(f"{name}_JackStripes", radius=0.205, depth=0.34, loc=(ox, oy, jack_base_z + 0.54), mat=mats['hazard_stripes'], col=col)
        band.parent = root
        
        # Émbolo telescópico cromado y asiento dentado de elevación
        ram = abs_style.create_cylinder(f"{name}_RamShaft", radius=0.12, depth=0.60, loc=(ox, oy, jack_base_z + 1.16), mat=mats['steel_bright'], col=col)
        ram.parent = root
        saddle = abs_style.create_cylinder(f"{name}_Saddle", radius=0.15, depth=0.08, loc=(ox, oy, jack_base_z + 1.48), mat=mats['gunmetal'], col=col)
        saddle.parent = root
        
        # Palanca de bombeo manual lateral y manómetro de tonelaje
        lever = abs_style.create_cylinder(f"{name}_Handle", radius=0.035, depth=1.05, rot=(R(35), 0, 0), loc=(ox, oy + 0.42, jack_base_z + 0.75), mat=mats['rubber_grip'], col=col)
        lever.parent = root
        g = abs_style.create_analog_gauge(f"{name}_TonDial", loc=(ox + 0.22, oy, jack_base_z + 0.60), rot=(0, 90, 0), radius=0.10, col=col)
        g.parent = root
        add_bevel(base)
        add_bevel(body)

    elif tool_id == 4: # T04_Deployable_Repeater_Beacon (Trípode apoyado DIRECTAMENTE en la superficie del pedestal)
        beacon_base_z = plinth_surface_z
        # Carcasa base con batería y franjas hazard
        body = abs_style.create_cylinder(f"{name}_Body", radius=0.16, depth=0.60, loc=(ox, oy, beacon_base_z + 0.45), mat=mats['hazard_yellow'], col=col)
        body.parent = root
        band = abs_style.create_cylinder(f"{name}_BeaconStripes", radius=0.165, depth=0.22, loc=(ox, oy, beacon_base_z + 0.45), mat=mats['hazard_stripes'], col=col)
        band.parent = root
        
        # 3 Patas articuladas de trípode con pies de ventosa de goma apoyados en el pedestal
        for i in range(3):
            ang = i * (2 * math.pi / 3)
            leg_x = ox + math.sin(ang) * 0.26
            leg_y = oy + math.cos(ang) * 0.26
            leg = abs_style.create_cylinder(f"{name}_TripodLeg_{i}", radius=0.035, depth=0.68, rot=(R(40)*math.cos(ang), R(40)*math.sin(ang), 0), loc=(leg_x, leg_y, beacon_base_z + 0.24), mat=mats['gunmetal'], col=col)
            leg.parent = root
            foot = abs_style.create_cylinder(f"{name}_Foot_{i}", radius=0.07, depth=0.04, loc=(ox + math.sin(ang)*0.46, oy + math.cos(ang)*0.46, beacon_base_z + 0.02), mat=mats['rubber_grip'], col=col)
            foot.parent = root
            
        # Mástil telescópico cromado con cúpula estroboscópica azul y jaula de latón
        mast = abs_style.create_cylinder(f"{name}_TelescopicMast", radius=0.035, depth=0.95, loc=(ox, oy, beacon_base_z + 1.15), mat=mats['steel_bright'], col=col)
        mast.parent = root
        strobe = abs_style.create_cylinder(f"{name}_StrobeFresnel", radius=0.09, depth=0.18, loc=(ox, oy, beacon_base_z + 1.68), mat=mats['beacon_blue'], col=col)
        strobe.parent = root
        cage = abs_style.create_torus(f"{name}_StrobeCage", major_r=0.10, minor_r=0.015, loc=(ox, oy, beacon_base_z + 1.68), mat=mats['brass_gold'], col=col)
        cage.parent = root
        
        g = abs_style.create_analog_gauge(f"{name}_BattMeter", loc=(ox + 0.17, oy, beacon_base_z + 0.48), rot=(0, 90, 0), radius=0.08, col=col)
        g.parent = root
        add_bevel(body)

    elif tool_id == 5: # T05_Acoustic_Motion_Scanner PDA (Apoyada sobre atril táctico inclinado a 35° en el pedestal)
        pda_base_z = plinth_surface_z
        # Base de atril táctico
        dock = abs_style.create_box(f"{name}_TacticalDock", size=(0.42, 0.42, 0.12), loc=(ox, oy, pda_base_z + 0.06), mat=mats['gunmetal'], col=col)
        dock.parent = root
        
        # Carcasa robusta naranja con esquinas de goma antichoque y pantalla CRT verde fósforo
        pda_z = pda_base_z + 0.28
        case = abs_style.create_box(f"{name}_RuggedCase", size=(0.36, 0.48, 0.16), rot=(R(30), 0, 0), loc=(ox, oy, pda_z), mat=mats['safety_orange'], col=col)
        case.parent = root
        
        # 4 Cantoneras de goma negra antichoque
        for cx_s in [-0.17, 0.17]:
            for cy_s in [-0.22, 0.22]:
                bumper = abs_style.create_box(f"{name}_Bumper_{cx_s}_{cy_s}", size=(0.06, 0.08, 0.18), rot=(R(30), 0, 0), loc=(ox + cx_s, oy + cy_s * math.cos(R(30)), pda_z - cy_s * math.sin(R(30))), mat=mats['rubber_grip'], col=col)
                bumper.parent = root
                
        # Pantalla CRT verde fósforo brillante
        screen = abs_style.create_box(f"{name}_CRTScreen", size=(0.26, 0.02, 0.24), rot=(R(30), 0, 0), loc=(ox, oy - 0.15, pda_z + 0.08), mat=mats['crt_green'], col=col)
        screen.parent = root
        
        # Bocina acústica direccional de latón
        horn = abs_style.create_cone(f"{name}_AcousticHorn", radius1=0.10, radius2=0.03, depth=0.18, rot=(R(30 + 90), 0, 0), loc=(ox, oy - 0.28, pda_z - 0.10), mat=mats['brass_gold'], col=col)
        horn.parent = root
        
        # Dial giratorio de latón y antena flexible
        dial = abs_style.create_cylinder(f"{name}_TuningDial", radius=0.04, depth=0.03, rot=(R(30), 0, 0), loc=(ox + 0.12, oy - 0.22, pda_z - 0.04), mat=mats['brass_gold'], col=col)
        dial.parent = root
        ant = abs_style.create_cylinder(f"{name}_RubberAntenna", radius=0.015, depth=0.38, rot=(R(15), 0, 0), loc=(ox - 0.15, oy + 0.18, pda_z + 0.28), mat=mats['rubber_grip'], col=col)
        ant.parent = root
        add_bevel(dock)
        add_bevel(case)

    elif tool_id == 6: # T06_Retractable_Titanium_Grapnel (Descansa sobre cuna industrial a Z=0.55)
        build_cradle_mount(name, origin, col, mats, cradle_span=0.45, height=0.22)
        tool_z = plinth_surface_z + 0.27
        
        # Cañón de eyección neumática en acero oscuro
        barrel = abs_style.create_cylinder(f"{name}_LaunchBarrel", radius=0.11, depth=0.75, rot=(R(90), 0, 0), loc=(ox, oy, tool_z), mat=mats['gunmetal'], col=col)
        barrel.parent = root
        
        # Collar de fijación de garras de latón con pasadores
        collar = abs_style.create_cylinder(f"{name}_ClawCollar", radius=0.16, depth=0.10, rot=(R(90), 0, 0), loc=(ox, oy - 0.38, tool_z), mat=mats['brass_gold'], col=col)
        collar.parent = root
        
        # Carrete de cable con tambor de latón, placas laterales y bobina de acero
        spool = abs_style.create_cylinder(f"{name}_WinchSpool", radius=0.18, depth=0.20, loc=(ox, oy + 0.20, tool_z - 0.04), mat=mats['brass_gold'], col=col)
        spool.parent = root
        cable = abs_style.create_cylinder(f"{name}_CableWound", radius=0.14, depth=0.16, loc=(ox, oy + 0.20, tool_z - 0.04), mat=mats['steel_bright'], col=col)
        cable.parent = root
        crank = abs_style.create_cylinder(f"{name}_WinchCrank", radius=0.025, depth=0.18, rot=(0, R(90), 0), loc=(ox + 0.19, oy + 0.20, tool_z - 0.04), mat=mats['gunmetal'], col=col)
        crank.parent = root
        
        # 4 Garras basculantes de aleación de titanio unidas físicamente al collar con pasadores clevis
        for i in range(4):
            ang = i * (math.pi / 2)
            c_x = ox + math.cos(ang) * 0.14
            c_z = tool_z + math.sin(ang) * 0.14
            # Pasador clevis en el collar
            pin = abs_style.create_cylinder(f"{name}_Pin_{i}", radius=0.02, depth=0.06, rot=(math.sin(ang)*R(90), math.cos(ang)*R(90), 0), loc=(c_x, oy - 0.38, c_z), mat=mats['brass_gold'], col=col)
            pin.parent = root
            # Garra articulada que arranca desde el pasador
            claw_base = abs_style.create_box(f"{name}_ClawBase_{i}", size=(0.04, 0.22, 0.06), rot=(0, -ang, R(22)), loc=(c_x, oy - 0.48, c_z), mat=mats['steel_bright'], col=col)
            claw_base.parent = root
            # Punta curvada de la garra
            claw_tip = abs_style.create_box(f"{name}_ClawTip_{i}", size=(0.035, 0.14, 0.05), rot=(0, -ang, R(55)), loc=(c_x * 1.15, oy - 0.60, c_z * 1.15), mat=mats['steel_bright'], col=col)
            claw_tip.parent = root
            add_bevel(claw_base, width=0.015)
            add_bevel(claw_tip, width=0.015)
            
        # Cartucho presurizado CO2 con franjas de peligro y manómetro
        tank = abs_style.create_cylinder(f"{name}_CO2Can", radius=0.065, depth=0.35, rot=(R(90), 0, 0), loc=(ox - 0.14, oy, tool_z), mat=mats['hazard_yellow'], col=col)
        tank.parent = root
        tstripes = abs_style.create_cylinder(f"{name}_CO2Stripes", radius=0.068, depth=0.12, rot=(R(90), 0, 0), loc=(ox - 0.14, oy, tool_z), mat=mats['hazard_stripes'], col=col)
        tstripes.parent = root
        grip = abs_style.create_box(f"{name}_PistolGrip", size=(0.08, 0.12, 0.26), rot=(R(20), 0, 0), loc=(ox, oy + 0.15, tool_z - 0.22), mat=mats['rubber_grip'], col=col)
        grip.parent = root
        g = abs_style.create_analog_gauge(f"{name}_LaunchPSI", loc=(ox + 0.14, oy, tool_z + 0.08), rot=(0, 90, 0), radius=0.07, col=col)
        g.parent = root
        add_bevel(barrel)
        add_bevel(collar)

    elif tool_id == 7: # T07_Heavy_Hydraulic_Shears (Descansa sobre cuna industrial a Z=0.55)
        build_cradle_mount(name, origin, col, mats, cradle_span=0.50, height=0.24)
        tool_z = plinth_surface_z + 0.29
        
        # Mandíbulas de corte templadas de 700 Bar en acero brillante con filo biselado y muesca
        arm_l = abs_style.create_box(f"{name}_BladeL", size=(0.07, 0.38, 0.24), rot=(0, 0, R(16)), loc=(ox - 0.11, oy - 0.54, tool_z), mat=mats['steel_bright'], col=col)
        arm_l.parent = root
        arm_r = abs_style.create_box(f"{name}_BladeR", size=(0.07, 0.38, 0.24), rot=(0, 0, R(-16)), loc=(ox + 0.11, oy - 0.54, tool_z), mat=mats['steel_bright'], col=col)
        arm_r.parent = root
        pivot = abs_style.create_cylinder(f"{name}_PivotHub", radius=0.11, depth=0.24, rot=(0, R(90), 0), loc=(ox, oy - 0.36, tool_z), mat=mats['brass_gold'], col=col)
        pivot.parent = root
        nut = abs_style.create_cylinder(f"{name}_PivotNut", radius=0.06, depth=0.28, rot=(0, R(90), 0), loc=(ox, oy - 0.36, tool_z), mat=mats['steel_bright'], col=col)
        nut.parent = root
        
        # Doble cilindro hidráulico amarillo con franja diagonal de advertencia
        ram = abs_style.create_cylinder(f"{name}_RamBody", radius=0.15, depth=0.72, rot=(R(90), 0, 0), loc=(ox, oy + 0.10, tool_z), mat=mats['hazard_yellow'], col=col)
        ram.parent = root
        band = abs_style.create_cylinder(f"{name}_ShearStripes", radius=0.155, depth=0.26, rot=(R(90), 0, 0), loc=(ox, oy + 0.10, tool_z), mat=mats['hazard_stripes'], col=col)
        band.parent = root
        
        # Vástagos cromados de pistón que emergen del cuerpo hacia las mandíbulas
        rod_l = abs_style.create_cylinder(f"{name}_RodL", radius=0.045, depth=0.24, rot=(R(90), 0, 0), loc=(ox - 0.08, oy - 0.24, tool_z), mat=mats['steel_bright'], col=col)
        rod_l.parent = root
        rod_r = abs_style.create_cylinder(f"{name}_RodR", radius=0.045, depth=0.24, rot=(R(90), 0, 0), loc=(ox + 0.08, oy - 0.24, tool_z), mat=mats['steel_bright'], col=col)
        rod_r.parent = root
        
        # Asa perimetral envolvente de 360° con empuñadura de goma estriada
        cage = abs_style.create_torus(f"{name}_FullRingHandle", major_r=0.25, minor_r=0.038, rot=(R(90), 0, 0), loc=(ox, oy + 0.05, tool_z), mat=mats['rubber_grip'], col=col)
        cage.parent = root
        rear_grip = abs_style.create_cylinder(f"{name}_RearThrottle", radius=0.04, depth=0.30, loc=(ox, oy + 0.48, tool_z - 0.08), mat=mats['rubber_grip'], col=col)
        rear_grip.parent = root
        g = abs_style.create_analog_gauge(f"{name}_BarDial", loc=(ox + 0.18, oy + 0.10, tool_z + 0.10), rot=(0, 90, 0), radius=0.08, col=col)
        g.parent = root
        add_bevel(arm_l)
        add_bevel(arm_r)
        add_bevel(ram)

    elif tool_id == 8: # T08_Folding_Thermal_Shield (Apoyado DIRECTAMENTE en el pedestal con pie de apoyo trasero)
        shield_base_z = plinth_surface_z
        # Panel central reforzado en gunmetal
        main_p = abs_style.create_box(f"{name}_CenterPanel", size=(0.70, 0.06, 1.25), loc=(ox, oy, shield_base_z + 0.65), mat=mats['gunmetal'], col=col)
        main_p.parent = root
        
        # Dos paneles laterales articulados en ángulo defensivo de 25°
        left_p = abs_style.create_box(f"{name}_WingL", size=(0.36, 0.06, 1.25), rot=(0, R(25), 0), loc=(ox - 0.50, oy + 0.08, shield_base_z + 0.65), mat=mats['gunmetal'], col=col)
        left_p.parent = root
        right_p = abs_style.create_box(f"{name}_WingR", size=(0.36, 0.06, 1.25), rot=(0, R(-25), 0), loc=(ox + 0.50, oy + 0.08, shield_base_z + 0.65), mat=mats['gunmetal'], col=col)
        right_p.parent = root
        
        # Bisagras pesadas de piano cilíndricas en las uniones
        for hx in [-0.34, 0.34]:
            hinge = abs_style.create_cylinder(f"{name}_Hinge_{hx}", radius=0.03, depth=1.22, loc=(ox + hx, oy + 0.03, shield_base_z + 0.65), mat=mats['brass_gold'], col=col)
            hinge.parent = root
        
        # Franjas hazard superior e inferior de alta visibilidad
        trim_top = abs_style.create_box(f"{name}_TrimTop", size=(0.72, 0.08, 0.10), loc=(ox, oy, shield_base_z + 1.24), mat=mats['hazard_stripes'], col=col)
        trim_top.parent = root
        trim_btm = abs_style.create_box(f"{name}_TrimBtm", size=(0.72, 0.08, 0.10), loc=(ox, oy, shield_base_z + 0.08), mat=mats['hazard_stripes'], col=col)
        trim_btm.parent = root
        
        # Visor balístico transparente de cuarzo multicapa con marco de latón
        window = abs_style.create_box(f"{name}_QuartzSlit", size=(0.34, 0.08, 0.16), loc=(ox, oy, shield_base_z + 0.95), mat=mats['shield_glass'], col=col)
        window.parent = root
        w_frame = abs_style.create_box(f"{name}_QuartzFrame", size=(0.38, 0.07, 0.20), loc=(ox, oy, shield_base_z + 0.95), mat=mats['brass_gold'], col=col)
        w_frame.parent = root
        
        # Pie de apoyo trasero (kickstand) que mantiene el escudo firme sobre el pedestal
        kick = abs_style.create_cylinder(f"{name}_Kickstand", radius=0.035, depth=0.85, rot=(R(30), 0, 0), loc=(ox, oy + 0.32, shield_base_z + 0.40), mat=mats['gunmetal'], col=col)
        kick.parent = root
        handle = abs_style.create_cylinder(f"{name}_BackGrip", radius=0.045, depth=0.45, loc=(ox, oy + 0.12, shield_base_z + 0.65), mat=mats['rubber_grip'], col=col)
        handle.parent = root
        add_bevel(main_p)
        add_bevel(left_p)
        add_bevel(right_p)

    return root

def generate_tools_scene(save_blend=True):
    print("================================================================")
    print("   GENERANDO SUITE OFICIAL DE 8 HERRAMIENTAS TÁCTICAS (CARTOON)")
    print("================================================================")
    abs_style.reset_comic_scene(bg_color=(0.02, 0.025, 0.035, 1.0), bg_strength=0.70, ink_thickness=2.6)
    col = abs_style.create_collection("Tactical_Tools_8")
    mats = init_tools_materials()

    # Disposición en 2 Filas de 4 Herramientas en pedestales escalonados
    # Fila 1: Y = 0.0, Z = 0.0 (T01 a T04)
    # Fila 2: Y = 3.2, Z = 0.85 (T05 a T08)
    spacing_x = 2.8
    
    terrace_mat = abs_style.get_comic_material("T_Terrace_Mat", base_color=(0.10, 0.12, 0.15), roughness=0.45, metallic=0.60)
    abs_style.create_box("Tools_Tier2", size=(24.0, 3.2, 0.85), loc=(0, 3.2, 0.425), mat=terrace_mat, col=col)
    abs_style.create_box("Tools_Tier2_Hazard", size=(24.0, 0.08, 0.08), loc=(0, 1.58, 0.83), mat=mats['hazard_stripes'], col=col)

    floor_mat = abs_style.get_comic_material("Tools_Floor", base_color=(0.035, 0.040, 0.048), roughness=0.90, metallic=0.0)
    abs_style.create_box("Tools_Floor", size=(32.0, 18.0, 0.10), loc=(0, 1.75, -0.05), mat=floor_mat, col=col)
    
    wall_mat = abs_style.get_comic_material("Tools_Wall", base_color=(0.12, 0.14, 0.18), roughness=0.50, metallic=0.70)
    abs_style.create_box("Tools_Wall_Back", size=(32.0, 0.2, 7.0), loc=(0, 5.8, 3.5), mat=wall_mat, col=col)
    for bx in [-10.0, -5.0, 0.0, 5.0, 10.0]:
        abs_style.create_box(f"Tools_IBeam_{bx}", size=(0.50, 0.18, 7.0), loc=(bx, 5.65, 3.5), mat=mats['gunmetal'], col=col)
    abs_style.create_cylinder("Tools_Pipe", radius=0.18, depth=32.0, rot=(0, R(90), 0), loc=(0, 5.55, 5.2), mat=mats['gunmetal'], col=col)
    abs_style.create_box("Tools_HazardLine", size=(30.0, 0.05, 0.14), loc=(0, 5.62, 4.2), mat=mats['hazard_stripes'], col=col)

    pedestal_mat = abs_style.get_comic_material("Tools_Pedestal", base_color=(0.12, 0.14, 0.16), roughness=0.35, metallic=0.60)
    closeups = {}

    for idx, (tid, tname, title, category, desc) in enumerate(TOOLS_DATA):
        row = idx // 4
        col_idx = idx % 4
        x = (col_idx - 1.5) * spacing_x
        y = 0.0 if row == 0 else 3.2
        z = 0.0 if row == 0 else 0.85
        
        plinth = abs_style.create_box(f"Plinth_{tname}", size=(2.1, 1.6, 0.25), loc=(x, y, z + 0.125), mat=pedestal_mat, col=col)
        abs_style.create_box(f"Plaque_{tname}", size=(1.1, 0.02, 0.10), loc=(x, y - 0.81, z + 0.125), mat=mats['brass_gold'], col=col)
        add_bevel(plinth)
        build_tactical_tool(tid, tname, (x, y, z), col, mats)

    abs_style.setup_studio_lighting(sun_energy=5.2, rim_energy=4.4, fill_energy=2.6,
                                    sun_rot=(46, 16, -32), rim_rot=(-58, 0, 160))

    # Cámara Panorámica cercana y heroica con encuadre óptimo sin espacio vacío muerto
    abs_style.setup_camera(name="Camera_Tools_Panorama", loc=(0.0, -9.8, 3.8), target=(0.0, 1.6, 1.05), focal_length=38)

    if save_blend:
        blend_path = os.path.join(abs_style.PROJECT_ROOT, "Art", "Blender", "Herramientas_Tacticas_8_Oficial.blend")
        bpy.ops.wm.save_as_mainfile(filepath=blend_path)
        print(f"[+] Tools Blend saved: {blend_path}")

    pano_render_path = os.path.join(abs_style.RENDERS_DIR, "Showcase_Herramientas_Tacticas_8_Panorama.png")
    abs_style.render_and_save("Showcase_Herramientas_Tacticas_8_Panorama.png", res_x=2560, res_y=850)

    # Parámetros especializados de cámara para cada herramienta (CERO cortes, encuadre 100% visible)
    TOOL_CAMERAS = {
        1: {"cam": (1.75, -2.40, 0.85), "tgt": (0.0, -0.15, 0.52), "lens": 36}, # T01 Lanzador Espuma
        2: {"cam": (1.45, -2.10, 0.75), "tgt": (0.0, -0.10, 0.48), "lens": 38}, # T02 Red Cuádruple
        3: {"cam": (1.80, -2.85, 1.15), "tgt": (0.0,  0.00, 0.85), "lens": 34}, # T03 Gato 15T (Alto)
        4: {"cam": (1.90, -2.95, 1.25), "tgt": (0.0,  0.00, 0.95), "lens": 32}, # T04 Baliza (Muy Alta)
        5: {"cam": (1.10, -1.65, 0.80), "tgt": (0.0,  0.00, 0.50), "lens": 38}, # T05 PDA
        6: {"cam": (1.50, -2.25, 0.75), "tgt": (0.0, -0.10, 0.48), "lens": 38}, # T06 Gancho
        7: {"cam": (1.65, -2.35, 0.78), "tgt": (0.0, -0.12, 0.50), "lens": 38}, # T07 Cizalla
        8: {"cam": (1.85, -2.80, 1.15), "tgt": (0.0,  0.00, 0.85), "lens": 34}, # T08 Escudo (Alto)
    }

    # Renderizado de los 8 Close-Ups individuales con encuadre calibrado individualmente
    for idx, (tid, tname, _, _, _) in enumerate(TOOLS_DATA):
        row = idx // 4
        col_idx = idx % 4
        x = (col_idx - 1.5) * spacing_x
        y = 0.0 if row == 0 else 3.2
        z = 0.0 if row == 0 else 0.85
        
        cfg = TOOL_CAMERAS.get(tid, {"cam": (1.5, -2.2, 0.8), "tgt": (0, 0, 0.5), "lens": 40})
        cam_loc = (x + cfg["cam"][0], y + cfg["cam"][1], z + cfg["cam"][2])
        target = (x + cfg["tgt"][0], y + cfg["tgt"][1], z + cfg["tgt"][2])
        
        abs_style.setup_camera(name=f"Cam_Close_{tname}", loc=cam_loc, target=target, focal_length=cfg["lens"])
        close_file = f"CloseUp_{tname}.png"
        abs_style.render_and_save(close_file, res_x=1280, res_y=960)
        closeups[tid] = os.path.join(abs_style.RENDERS_DIR, close_file)

    generate_tools_technical_sheet(pano_render_path, closeups)
    print("[+] Suite de 8 Herramientas Tácticas Renderizada y Compuesta al 100%!")

def generate_tools_technical_sheet(pano_path, closeups):
    W, H = 2560, 1440
    canvas = Image.new("RGBA", (W, H), (14, 17, 22, 255))
    draw = ImageDraw.Draw(canvas)
    
    try:
        font_title = ImageFont.truetype("arialbd.ttf", 26)
        font_sub = ImageFont.truetype("arialbd.ttf", 15)
        font_pill = ImageFont.truetype("arialbd.ttf", 13)
        font_card_title = ImageFont.truetype("arialbd.ttf", 15)
        font_card_desc = ImageFont.truetype("arial.ttf", 12)
    except:
        font_title = font_sub = font_pill = font_card_title = font_card_desc = ImageFont.load_default()
        
    draw.text((40, 20), "ASTRA HAZARD // HERRAMIENTAS TÁCTICAS AVANZADAS", fill=(245, 166, 35), font=font_sub)
    draw.text((40, 46), "SUITE DE 8 HERRAMIENTAS TÁCTICAS Y GADGETS DE MISIÓN // CARTOON INDUSTRIAL PBR & FREESTYLE 2.6PX", fill=(255, 255, 255), font=font_title)
    
    pills = [
        ("8 GADGETS TÁCTICOS", (230, 126, 34)),
        ("3 EXISTENTES + 5 NUEVOS", (241, 196, 15)),
        ("CEL-SHADING CÓMIC", (155, 89, 182)),
        ("FREESTYLE 2.6PX", (39, 174, 96)),
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
    
    if os.path.exists(pano_path):
        pan_img = Image.open(pano_path).convert("RGBA")
        pan_w = W - 80
        pan_h = 580
        pan_resized = pan_img.resize((pan_w, pan_h), Image.Resampling.LANCZOS)
        canvas.paste(pan_resized, (40, 110))
        draw.rectangle((40, 110, 40 + pan_w, 110 + pan_h), outline=(45, 52, 65), width=2)
        
    cols = 4
    rows = 2
    spacing_x = 20
    spacing_y = 15
    total_w = W - 80
    card_w = int((total_w - (cols - 1) * spacing_x) / cols)
    card_h = 340
    start_y = 715
    
    colors = [
        (230, 126, 34), (41, 128, 185), (241, 196, 15), (46, 204, 113),
        (52, 152, 219), (231, 76, 60), (155, 89, 182), (26, 188, 156)
    ]

    for idx, (tid, tname, title, category, desc) in enumerate(TOOLS_DATA):
        r = idx // cols
        c = idx % cols
        cx = 40 + c * (card_w + spacing_x)
        cy = start_y + r * (card_h + spacing_y)
        color_accent = colors[idx % len(colors)]
        
        draw.rounded_rectangle((cx, cy, cx + card_w, cy + card_h), radius=6, fill=(20, 24, 30, 255), outline=(45, 52, 65), width=2)
        draw.rounded_rectangle((cx, cy, cx + card_w, cy + 5), radius=3, fill=color_accent)
        
        img_path = closeups.get(tid)
        if img_path and os.path.exists(img_path):
            c_img = Image.open(img_path).convert("RGBA")
            thumb_w = 230
            thumb_h = 290
            c_thumb = c_img.resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
            canvas.paste(c_thumb, (cx + 8, cy + 18))
            draw.rectangle((cx + 8, cy + 18, cx + 8 + thumb_w, cy + 18 + thumb_h), outline=(45, 52, 65), width=1)
            
        tx = cx + 250
        draw.text((tx, cy + 18), f"HERRAMIENTA T0{tid} // {category}", fill=color_accent, font=font_card_desc)
        draw.text((tx, cy + 38), title, fill=(255, 255, 255), font=font_card_title)
        draw.line([(tx, cy + 62), (cx + card_w - 12, cy + 62)], fill=(45, 52, 65), width=1)
        
        lines = desc.split("\n")
        ly = cy + 74
        for line in lines:
            draw.text((tx, ly), line, fill=(185, 195, 210), font=font_card_desc)
            ly += 22
            
        draw.rounded_rectangle((tx, cy + card_h - 36, cx + card_w - 12, cy + card_h - 12), radius=4, fill=(15, 18, 24))
        draw.text((tx + 10, cy + card_h - 30), "ESTADO: VERIFICADO & OPERATIVO 100%", fill=color_accent, font=font_pill)

    master_path = os.path.join(abs_style.RENDERS_DIR, "Showcase_Herramientas_Tacticas_8_Master.png")
    canvas.save(master_path)
    print(f"[+] Lámina Maestra Herramientas Tácticas generada con éxito: {master_path}")
    shutil.copy2(master_path, os.path.join(abs_style.ARTIFACT_DIR, "Showcase_Herramientas_Tacticas_8_Master.png"))

if __name__ == "__main__":
    generate_tools_scene()

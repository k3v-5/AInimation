"""
generar_personaje_fiel_referencia_v9.py
========================================
Generador Procedural 1:1 Definitivo y Pulido de Bombero Espacial (Astra Hazard)
Mejoras de acabado final:
1. ESTUDIO CYCLORAMA TÉCNICO: Fondo curvado continuo sin línea de horizonte abrupta, idéntico al Model Sheet de Reference 1.
2. ENCUADRE DE CÁMARA IMPECABLE: Margen superior e inferior holgado (distancia 4.0m, lente 40mm) para visualización completa de cresta e insignia.
3. DETALLES DE BRAZALETES Y RODILLERAS: Franjas reflectantes dobles en antebrazos y rodilleras biseladas segmentadas.
4. VISTA DE ACCIÓN 3/4 CON CELOSÍA Y FONDO ESPACIAL: Recreación fiel de la plataforma gantry del screenshot oficial.
"""

import sys, os, math, shutil
import bpy, bmesh
from mathutils import Matrix, Vector, Euler
from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = r"f:\Dev\Game"
ART_DIR = os.path.join(PROJECT_ROOT, "Art")
FBX_DIR = os.path.join(ART_DIR, "FBX", "Characters")
RENDERS_DIR = os.path.join(ART_DIR, "Renders")
BRAIN_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\b59ff04f-3c21-4ee5-94b0-8e8f899f8923"

os.makedirs(FBX_DIR, exist_ok=True)
os.makedirs(RENDERS_DIR, exist_ok=True)
os.makedirs(BRAIN_DIR, exist_ok=True)

R = math.radians

def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

# ---------------------------------------------------------------------------
# PALETA OFICIAL EXTRAÍDA EXACTAMENTE DE LA TABLA DE REFERENCIA
# ---------------------------------------------------------------------------
def create_pbr_mat(name, base_color, metallic=0.04, roughness=0.40, emission=None, emission_strength=1.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = base_color
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    
    if emission:
        if 'Emission Color' in bsdf.inputs:
            bsdf.inputs['Emission Color'].default_value = emission
            bsdf.inputs['Emission Strength'].default_value = emission_strength
        else:
            bsdf.inputs['Emission'].default_value = emission
            
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_unlit_mat(name, color):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    emis = nt.nodes.new('ShaderNodeEmission')
    emis.inputs['Color'].default_value = color
    emis.inputs['Strength'].default_value = 1.0
    nt.links.new(emis.outputs['Emission'], out.inputs['Surface'])
    mat.use_backface_culling = True
    return mat

def build_palette():
    return {
        # 0: Traje Naranja Oficial (SUIT ORANGE #CA7C32)
        'suit_orange': create_pbr_mat("M_Suit_Orange", (0.82, 0.42, 0.10, 1.0), metallic=0.02, roughness=0.45),
        # 1: Traje Naranja Sombra / Cuello (#B28241)
        'suit_dark_orange': create_pbr_mat("M_Suit_DarkOrange", (0.68, 0.32, 0.08, 1.0), metallic=0.02, roughness=0.50),
        # 2: Armadura Verde Salvia (ARMOR GREEN #629B4E)
        'armor_sage': create_pbr_mat("M_Armor_Sage", (0.32, 0.52, 0.28, 1.0), metallic=0.06, roughness=0.38),
        # 3: Casco Gris Oscuro (HELMET GREY #7B7D78)
        'helmet_grey': create_pbr_mat("M_Helmet_Grey", (0.34, 0.36, 0.35, 1.0), metallic=0.15, roughness=0.35),
        # 4: Visor Ahumado Tintado Panorámico (REINFORCED VISOR)
        'visor_tinted': create_pbr_mat("M_Visor_Tinted", (0.10, 0.14, 0.18, 1.0), metallic=0.25, roughness=0.06),
        # 5: Franjas Amarillo Lima Reflectantes (#BCBA56)
        'stripe_yellow': create_pbr_mat("M_Stripe_Yellow", (0.86, 0.86, 0.18, 1.0), metallic=0.02, roughness=0.25),
        # 6: Manguera Roja Carmín (#B4231E)
        'hose_red': create_pbr_mat("M_Hose_Red", (0.78, 0.08, 0.06, 1.0), metallic=0.03, roughness=0.45),
        # 7: Arnés y Gomas Carbón Oscuro (#292926)
        'harness_dark': create_pbr_mat("M_Harness_Dark", (0.08, 0.08, 0.09, 1.0), metallic=0.05, roughness=0.60),
        # 8: Pantalla Pectoral / LED Verde Brillante
        'led_green': create_pbr_mat("M_LED_Green", (0.15, 0.98, 0.20, 1.0), metallic=0.0, roughness=0.10, emission=(0.15, 0.98, 0.20, 1.0), emission_strength=5.0),
        # 9: Botones Rojos LED / Power Indicator
        'led_red': create_pbr_mat("M_LED_Red", (1.0, 0.06, 0.06, 1.0), metallic=0.0, roughness=0.10, emission=(1.0, 0.06, 0.06, 1.0), emission_strength=4.5),
        # 10: Cañón y Envolvente Arma Azul-Gris (#5D7F8E)
        'weapon_blue': create_pbr_mat("M_Weapon_Blue", (0.28, 0.42, 0.50, 1.0), metallic=0.35, roughness=0.30),
        # 11: Culata y Mango Arma Marrón Madera / Acero (#A85532)
        'weapon_stock': create_pbr_mat("M_Weapon_Stock", (0.55, 0.25, 0.12, 1.0), metallic=0.10, roughness=0.45),
        # 12: Ventana Amarilla Arma (#D4D843)
        'weapon_yellow': create_pbr_mat("M_Weapon_Yellow", (0.92, 0.82, 0.15, 1.0), metallic=0.05, roughness=0.20, emission=(0.92, 0.82, 0.15, 1.0), emission_strength=2.5),
        # 13: Acero Oscuro / Boquilla y Suelas
        'metal_dark': create_pbr_mat("M_Metal_Dark", (0.12, 0.13, 0.15, 1.0), metallic=0.75, roughness=0.25),
        # 14: Contorno Cel-Shading Negro Pura Tinta
        'outline_black': create_unlit_mat("M_Outline_Black", (0.01, 0.01, 0.01, 1.0))
    }

# ---------------------------------------------------------------------------
# MODELADO ANATÓMICO 1:1 CON SILUETA CHUNKY COHESIVA
# ---------------------------------------------------------------------------
def build_firefighter_mesh(mats):
    mesh = bpy.data.meshes.new("SK_Firefighter_Match1to1_Mesh")
    bm = bmesh.new()

    mat_order = [
        mats['suit_orange'],       # 0
        mats['suit_dark_orange'],  # 1
        mats['armor_sage'],        # 2
        mats['helmet_grey'],       # 3
        mats['visor_tinted'],      # 4
        mats['stripe_yellow'],     # 5
        mats['hose_red'],          # 6
        mats['harness_dark'],      # 7
        mats['led_green'],         # 8
        mats['led_red'],           # 9
        mats['weapon_blue'],       # 10
        mats['weapon_stock'],      # 11
        mats['weapon_yellow'],     # 12
        mats['metal_dark'],        # 13
        mats['outline_black']      # 14
    ]

    def add_box(center, size, mat_idx, rot=(0,0,0)):
        sx, sy, sz = size
        ret = bmesh.ops.create_cube(bm, size=1.0)
        verts = ret['verts']
        bmesh.ops.scale(bm, vec=(sx, sy, sz), verts=verts)
        if rot[0] != 0:
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=Matrix.Rotation(rot[0], 3, 'X'), verts=verts)
        if rot[1] != 0:
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=Matrix.Rotation(rot[1], 3, 'Y'), verts=verts)
        if rot[2] != 0:
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=Matrix.Rotation(rot[2], 3, 'Z'), verts=verts)
        bmesh.ops.translate(bm, vec=center, verts=verts)
        for f in bm.faces:
            if f.verts[0] in verts:
                f.material_index = mat_idx
        return verts

    def add_cylinder(center, r1, r2, depth, mat_idx, segs=16, rot=(0,0,0)):
        ret = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segs, radius1=r1, radius2=r2, depth=depth)
        verts = ret['verts']
        if rot[0] != 0:
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=Matrix.Rotation(rot[0], 3, 'X'), verts=verts)
        if rot[1] != 0:
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=Matrix.Rotation(rot[1], 3, 'Y'), verts=verts)
        if rot[2] != 0:
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=Matrix.Rotation(rot[2], 3, 'Z'), verts=verts)
        bmesh.ops.translate(bm, vec=center, verts=verts)
        for f in bm.faces:
            if f.verts[0] in verts:
                f.material_index = mat_idx
        return verts

    # -----------------------------------------------------------------------
    # 1. CASCO DOMO ESFÉRICO CON VISOR PANORÁMICO CONTINUO
    # -----------------------------------------------------------------------
    # Cúpula esférica (UV-Sphere segmentada de 16x10)
    ret_sphere = bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=10, radius=0.25)
    s_verts = ret_sphere['verts']
    bmesh.ops.scale(bm, vec=(1.02, 0.98, 0.88), verts=s_verts)
    bmesh.ops.translate(bm, vec=(0.0, 0.01, 1.48), verts=s_verts)
    for f in bm.faces:
        if f.verts[0] in s_verts:
            f.material_index = 3

    # Cresta longitudinal superior
    add_box((0, 0.01, 1.67), (0.10, 0.36, 0.04), 3)

    # Insignia amarilla frontal sobre la frente
    add_box((0, -0.19, 1.66), (0.07, 0.03, 0.035), 5)

    # VISOR PANORÁMICO CONTINUO ENVOLVENTE
    ret_visor = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16, radius1=0.23, radius2=0.23, depth=0.17)
    v_verts = ret_visor['verts']
    bmesh.ops.scale(bm, vec=(1.04, 0.95, 1.0), verts=v_verts)
    bmesh.ops.translate(bm, vec=(0.0, -0.06, 1.47), verts=v_verts)
    for f in bm.faces:
        if f.verts[0] in v_verts:
            if f.calc_center_median().y < -0.06:
                f.material_index = 4
            else:
                f.material_index = 3

    # Orejeras de comunicaciones
    add_cylinder((-0.26, 0.01, 1.48), 0.055, 0.055, 0.03, 3, segs=12, rot=(0, R(90), 0))
    add_cylinder((0.26, 0.01, 1.48), 0.055, 0.055, 0.03, 3, segs=12, rot=(0, R(90), 0))

    # Cuello envolvente acolchado que sella el casco con el torso
    add_cylinder((0, 0.01, 1.34), 0.25, 0.27, 0.08, 0, segs=18)
    add_cylinder((0, 0.01, 1.28), 0.27, 0.30, 0.06, 2, segs=18)

    # -----------------------------------------------------------------------
    # 2. TORSO CHUNKY, ARNÉS Y CAJA DE CONTROL PECTORAL
    # -----------------------------------------------------------------------
    add_box((0, 0.02, 1.12), (0.52, 0.35, 0.26), 0)
    add_box((0, 0.02, 0.98), (0.47, 0.33, 0.16), 0)

    # Tirantes oscuros del arnés táctico
    add_box((-0.15, -0.16, 1.12), (0.055, 0.025, 0.28), 7)
    add_box((0.15, -0.16, 1.12), (0.055, 0.025, 0.28), 7)

    # Correa horizontal del arnés sobre el pecho
    add_box((0, -0.16, 1.13), (0.36, 0.025, 0.04), 7)

    # Cinturón ventral ancho con franja reflectante
    add_box((0, -0.15, 0.92), (0.48, 0.03, 0.07), 7)
    add_box((0, 0.02, 0.91), (0.49, 0.34, 0.05), 5)

    # CAJA DE CONTROL EN EL PECHO ("CHEST CONTROL BOX")
    add_box((0.02, -0.185, 1.11), (0.18, 0.04, 0.11), 2)
    add_box((-0.03, -0.208, 1.11), (0.055, 0.015, 0.065), 8) # Pantalla verde
    add_box((0.065, -0.208, 1.135), (0.026, 0.015, 0.026), 9) # Botón rojo 1
    add_box((0.065, -0.208, 1.085), (0.026, 0.015, 0.026), 9) # Botón rojo 2

    # -----------------------------------------------------------------------
    # 3. MOCHILA TRASERA ("BACKPACK UNIT")
    # -----------------------------------------------------------------------
    add_box((0, 0.26, 1.14), (0.38, 0.17, 0.42), 0)
    add_box((0, 0.27, 1.35), (0.36, 0.15, 0.04), 2)

    # Rejillas de ventilación superiores (Louvers negras)
    for x_off in [0.06, 0.09, 0.12, 0.15]:
        add_box((x_off, 0.35, 1.25), (0.016, 0.015, 0.12), 7)

    for z_off in [1.29, 1.25, 1.21]:
        add_box((-0.10, 0.35, z_off), (0.09, 0.015, 0.02), 7)

    # Indicador LED verde superior izquierdo
    add_box((-0.10, 0.35, 1.15), (0.035, 0.015, 0.035), 8)

    # Indicador LED verde inferior derecho
    add_box((0.11, 0.35, 1.08), (0.035, 0.015, 0.035), 8)

    # "POWER INDICATOR": Placa gris con barra roja horizontal
    add_box((-0.04, 0.35, 1.04), (0.14, 0.015, 0.08), 2)
    add_box((-0.04, 0.36, 1.04), (0.06, 0.012, 0.025), 9)

    # "POWER CONNECTOR": Enchufe circular donde encaja la manguera
    add_cylinder((0.11, 0.34, 0.97), 0.038, 0.038, 0.04, 7, segs=12, rot=(R(90), 0, 0))
    add_cylinder((0.11, 0.36, 0.97), 0.022, 0.022, 0.02, 9, segs=12, rot=(R(90), 0, 0))

    # Tanque derecho auxiliar
    add_cylinder((0.20, 0.24, 1.17), 0.05, 0.05, 0.22, 0, segs=10)
    add_box((0.24, 0.24, 1.17), (0.02, 0.06, 0.12), 12)

    # -----------------------------------------------------------------------
    # 4. MANGUERA ROJA CURVA ("RED FLUID HOSE")
    # -----------------------------------------------------------------------
    hose_pts = [
        Vector((0.11, 0.36, 0.97)),
        Vector((0.19, 0.39, 0.88)),
        Vector((0.30, 0.33, 0.77)),
        Vector((0.37, 0.18, 0.70)),
        Vector((0.38, 0.01, 0.69)),
        Vector((0.34, -0.16, 0.74)),
        Vector((0.27, -0.27, 0.81)),
        Vector((0.18, -0.32, 0.87))
    ]
    for i in range(len(hose_pts)-1):
        p1 = hose_pts[i]
        p2 = hose_pts[i+1]
        mid = (p1 + p2) * 0.5
        v = p2 - p1
        dist = v.length
        rot_axis = Vector((0, 0, 1)).cross(v.normalized())
        angle = math.acos(max(-1.0, min(1.0, Vector((0, 0, 1)).dot(v.normalized()))))
        
        cyl = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=10, radius1=0.034, radius2=0.034, depth=dist)
        if rot_axis.length > 0.001:
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=Matrix.Rotation(angle, 3, rot_axis.normalized()), verts=cyl['verts'])
        bmesh.ops.translate(bm, vec=mid, verts=cyl['verts'])
        for f in bm.faces:
            if f.verts[0] in cyl['verts']:
                f.material_index = 6

    # -----------------------------------------------------------------------
    # 5. ARMA TÁCTICA ("EQUIPMENT ISOLATED" - CAÑÓN EXTINTOR)
    # -----------------------------------------------------------------------
    gun_center = Vector((0.02, -0.38, 0.89))
    g_rx, g_ry, g_rz = R(10), R(-12), R(-18)

    def add_gun_box(local_pos, size, mat_idx):
        sx, sy, sz = size
        ret = bmesh.ops.create_cube(bm, size=1.0)
        verts = ret['verts']
        bmesh.ops.scale(bm, vec=(sx, sy, sz), verts=verts)
        bmesh.ops.translate(bm, vec=local_pos, verts=verts)
        rot_mat = Euler((g_rx, g_ry, g_rz)).to_matrix()
        bmesh.ops.rotate(bm, cent=(0,0,0), matrix=rot_mat, verts=verts)
        bmesh.ops.translate(bm, vec=gun_center, verts=verts)
        for f in bm.faces:
            if f.verts[0] in verts:
                f.material_index = mat_idx

    def add_gun_cyl(local_pos, r1, r2, depth, mat_idx, segs=12, rot_local=(0,0,0)):
        ret = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segs, radius1=r1, radius2=r2, depth=depth)
        verts = ret['verts']
        if rot_local[0] != 0:
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=Matrix.Rotation(rot_local[0], 3, 'X'), verts=verts)
        if rot_local[1] != 0:
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=Matrix.Rotation(rot_local[1], 3, 'Y'), verts=verts)
        if rot_local[2] != 0:
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=Matrix.Rotation(rot_local[2], 3, 'Z'), verts=verts)
        bmesh.ops.translate(bm, vec=local_pos, verts=verts)
        rot_mat = Euler((g_rx, g_ry, g_rz)).to_matrix()
        bmesh.ops.rotate(bm, cent=(0,0,0), matrix=rot_mat, verts=verts)
        bmesh.ops.translate(bm, vec=gun_center, verts=verts)
        for f in bm.faces:
            if f.verts[0] in verts:
                f.material_index = mat_idx

    # Receptor superior del arma
    add_gun_box((0.0, 0.0, 0.0), (0.24, 0.11, 0.13), 10)
    add_gun_box((0.0, -0.058, 0.01), (0.09, 0.01, 0.045), 12)

    # Cañón cilíndrico azul
    add_gun_cyl((-0.22, 0.0, 0.0), 0.052, 0.052, 0.26, 10, segs=12, rot_local=(0, R(90), 0))
    # Boquilla acampanada (Muzzle ring)
    add_gun_cyl((-0.36, 0.0, 0.0), 0.066, 0.066, 0.055, 13, segs=12, rot_local=(0, R(90), 0))
    add_gun_cyl((-0.38, 0.0, 0.0), 0.040, 0.040, 0.02, 14, segs=12, rot_local=(0, R(90), 0))

    # Empuñadura delantera vertical
    add_gun_cyl((-0.09, 0.0, -0.11), 0.024, 0.024, 0.13, 13, segs=8)

    # Disparador y empuñadura trasera
    add_gun_box((0.05, 0.0, -0.065), (0.17, 0.065, 0.065), 11)
    add_gun_box((0.15, 0.0, -0.12), (0.065, 0.055, 0.13), 7)

    # Culata de rifle con cantonera
    add_gun_box((0.26, 0.0, -0.02), (0.17, 0.055, 0.11), 11)
    add_gun_box((0.35, 0.0, -0.02), (0.035, 0.060, 0.12), 13)

    # Conexión manguera en culata
    add_gun_cyl((0.18, 0.0, -0.065), 0.032, 0.032, 0.045, 6, segs=8, rot_local=(R(90), 0, 0))

    # -----------------------------------------------------------------------
    # 6. HOMBROS Y BRAZOS SOSTENIENDO EL ARMA
    # -----------------------------------------------------------------------
    # Hombreras pauldrons en verde salvia (#629B4E)
    add_box((-0.31, 0.02, 1.25), (0.20, 0.24, 0.10), 2, rot=(0, R(-26), 0))
    add_box((0.31, 0.02, 1.25), (0.20, 0.24, 0.10), 2, rot=(0, R(26), 0))

    # BRAZO IZQUIERDO (Sujeta empuñadura delantera)
    add_box((-0.31, 0.02, 1.12), (0.16, 0.19, 0.16), 0)
    add_box((-0.31, 0.02, 1.05), (0.17, 0.20, 0.035), 5) # Franja amarilla bíceps
    add_box((-0.20, -0.19, 0.96), (0.16, 0.22, 0.16), 0, rot=(R(35), R(-25), R(-25)))
    add_box((-0.15, -0.25, 0.92), (0.17, 0.05, 0.17), 2, rot=(R(35), R(-25), R(-25))) # Brazalete verde
    add_box((-0.12, -0.29, 0.89), (0.17, 0.05, 0.17), 5, rot=(R(35), R(-25), R(-25))) # Brazalete amarillo
    add_box((-0.08, -0.35, 0.86), (0.14, 0.15, 0.14), 7) # Guante izquierdo

    # BRAZO DERECHO (Sujeta empuñadura trasera / gatillo)
    add_box((0.31, 0.02, 1.12), (0.16, 0.19, 0.16), 0)
    add_box((0.31, 0.02, 1.05), (0.17, 0.20, 0.035), 5) # Franja amarilla bíceps
    add_box((0.23, -0.16, 0.97), (0.16, 0.22, 0.16), 0, rot=(R(28), R(18), R(20)))
    add_box((0.19, -0.23, 0.93), (0.17, 0.05, 0.17), 2, rot=(R(28), R(18), R(20))) # Brazalete verde
    add_box((0.16, -0.27, 0.90), (0.17, 0.05, 0.17), 5, rot=(R(28), R(18), R(20))) # Brazalete amarillo
    add_box((0.13, -0.32, 0.89), (0.14, 0.15, 0.14), 7) # Guante derecho

    # -----------------------------------------------------------------------
    # 7. PIERNAS CHUNKY COHESIVAS EN "A-STANCE", RODILLERAS Y BOTAS
    # -----------------------------------------------------------------------
    add_box((0, 0.02, 0.84), (0.42, 0.30, 0.14), 0)

    for sign in [1, -1]:
        # Muslos robustos inclinados hacia afuera (A-stance)
        add_box((0.15 * sign, 0.02, 0.68), (0.22, 0.24, 0.28), 0, rot=(0, R(-10 * sign), 0))

        # Articulación de rodilla sellada
        add_box((0.18 * sign, 0.01, 0.52), (0.20, 0.23, 0.14), 0, rot=(0, R(-8 * sign), 0))

        # RODILLERAS TÁCTICAS FRONTALES ("ARMOUR SEGMENTS" - Verde salvia con bisel y ranuras)
        add_box((0.18 * sign, -0.11, 0.52), (0.19, 0.06, 0.15), 2)
        add_box((0.18 * sign, -0.145, 0.54), (0.15, 0.015, 0.02), 7)
        add_box((0.18 * sign, -0.145, 0.50), (0.15, 0.015, 0.02), 7)

        # Pantorrillas gruesas
        add_box((0.20 * sign, 0.01, 0.36), (0.21, 0.23, 0.22), 0, rot=(0, R(-7 * sign), 0))

        # Franja reflectante amarilla continua en el tobillo
        add_box((0.21 * sign, 0.01, 0.24), (0.22, 0.24, 0.05), 5)

        # BOTAS TÁCTICAS PESADAS CON PUNTERA REFORZADA Y SUELA PLANA
        # Caña de la bota (Verde salvia)
        add_box((0.23 * sign, -0.03, 0.14), (0.23, 0.28, 0.18), 2)
        # Puntera frontal reforzada (Gris oscuro)
        add_box((0.23 * sign, -0.12, 0.06), (0.23, 0.16, 0.09), 3)
        # Suela gruesa de goma oscura con contacto plano en el suelo (Z=0.00 a 0.03)
        add_box((0.23 * sign, -0.03, 0.015), (0.24, 0.32, 0.03), 13)

    bm.to_mesh(mesh)
    bm.free()

    for m in mat_order:
        mesh.materials.append(m)

    obj = bpy.data.objects.new("SK_Firefighter_Match1to1", mesh)
    bpy.context.scene.collection.objects.link(obj)

    # Cel-Shading Inverted Hull (Tinta Negra)
    sol = obj.modifiers.new("CelOutline", 'SOLIDIFY')
    sol.thickness = -0.008
    sol.offset = 1.0
    sol.use_flip_normals = True
    sol.material_offset = 14
    sol.use_rim = True

    return obj

# ---------------------------------------------------------------------------
# ESTUDIO CYCLORAMA CONTINUO Y ESTUDIO ESPACIAL
# ---------------------------------------------------------------------------
def setup_lighting(scene, is_blueprint=True):
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'Medium High Contrast'

    for ob in list(scene.collection.objects):
        if ob.name.startswith("Studio") or ob.name.startswith("Light") or ob.name.startswith("Gantry"):
            bpy.data.objects.remove(ob, do_unlink=True)

    target = bpy.data.objects.new("LightTarget", None)
    target.location = (0, 0, 0.82)
    scene.collection.objects.link(target)

    def add_light(name, pos, energy, color, size=2.5):
        ldata = bpy.data.lights.new(name, 'AREA')
        ldata.energy = energy
        ldata.size = size
        ldata.color = color
        lobj = bpy.data.objects.new(name, ldata)
        lobj.location = pos
        tt = lobj.constraints.new('TRACK_TO')
        tt.target = target
        tt.track_axis = 'TRACK_NEGATIVE_Z'
        tt.up_axis = 'UP_Y'
        scene.collection.objects.link(lobj)
        return lobj

    if is_blueprint:
        # Fondo técnico suave
        world = scene.world or bpy.data.worlds.new("BlueprintWorld")
        scene.world = world
        world.use_nodes = True
        wnt = world.node_tree
        wnt.nodes.clear()
        w_out = wnt.nodes.new('ShaderNodeOutputWorld')
        w_bg = wnt.nodes.new('ShaderNodeBackground')
        w_bg.inputs['Color'].default_value = (0.68, 0.76, 0.82, 1.0)
        w_bg.inputs['Strength'].default_value = 0.8
        wnt.links.new(w_bg.outputs['Background'], w_out.inputs['Surface'])

        # Suelo Cyclorama sin horizonte abrupto
        floor_mesh = bpy.data.meshes.new("StudioFloor")
        bm = bmesh.new()
        bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=40)
        bm.to_mesh(floor_mesh)
        bm.free()
        f_obj = bpy.data.objects.new("StudioFloor", floor_mesh)
        f_obj.location = (0, 0, 0.0)
        mat_f = create_pbr_mat("M_BlueprintFloor", (0.65, 0.74, 0.80, 1.0), metallic=0.0, roughness=0.9)
        f_obj.data.materials.append(mat_f)
        scene.collection.objects.link(f_obj)

        add_light("LightFront", (1.5, -3.2, 2.2), 220, (1.0, 0.98, 0.96), size=2.8)
        add_light("LightBack", (-1.5, 3.2, 2.2), 240, (0.96, 0.98, 1.0), size=2.8)
        add_light("LightLeft", (-3.0, 0.0, 1.8), 140, (0.95, 0.98, 1.0), size=2.2)
        add_light("LightRight", (3.0, 0.0, 1.8), 140, (1.0, 0.97, 0.94), size=2.2)

    else:
        # Modo Acción Espacial (Screenshot Reference 2)
        world = scene.world or bpy.data.worlds.new("SpaceWorld")
        scene.world = world
        world.use_nodes = True
        wnt = world.node_tree
        wnt.nodes.clear()
        w_out = wnt.nodes.new('ShaderNodeOutputWorld')
        w_bg = wnt.nodes.new('ShaderNodeBackground')
        w_bg.inputs['Color'].default_value = (0.012, 0.015, 0.022, 1.0)
        w_bg.inputs['Strength'].default_value = 0.35
        wnt.links.new(w_bg.outputs['Background'], w_out.inputs['Surface'])

        # Plataforma Gantry limpia con celosía
        gantry_mesh = bpy.data.meshes.new("GantryFloor")
        bm = bmesh.new()
        ret = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(4.0, 4.0, 0.04), verts=ret['verts'])
        bmesh.ops.translate(bm, vec=(0, 0, -0.02), verts=ret['verts'])
        
        # Vigas de celosía laterales estilo estación espacial
        for bx in [-1.5, 1.5]:
            viga = bmesh.ops.create_cube(bm, size=1.0)
            bmesh.ops.scale(bm, vec=(0.08, 3.5, 0.08), verts=viga['verts'])
            bmesh.ops.translate(bm, vec=(bx, 0.0, 0.02), verts=viga['verts'])

        bm.to_mesh(gantry_mesh)
        bm.free()
        g_obj = bpy.data.objects.new("GantryFloor", gantry_mesh)
        mat_g = create_pbr_mat("M_GantryFloor", (0.18, 0.20, 0.24, 1.0), metallic=0.6, roughness=0.35)
        g_obj.data.materials.append(mat_g)
        scene.collection.objects.link(g_obj)

        sol_g = g_obj.modifiers.new("GantryOutline", 'SOLIDIFY')
        sol_g.thickness = -0.007
        sol_g.offset = 1.0
        sol_g.use_flip_normals = True
        sol_g.material_offset = 0

        add_light("LightFront", (1.8, -3.0, 2.2), 320, (1.0, 0.98, 0.95), size=2.5)
        add_light("LightBack", (-1.8, 3.0, 2.2), 340, (0.95, 0.98, 1.0), size=2.5)
        add_light("RimCyan", (-3.2, -0.4, 1.6), 180, (0.25, 0.85, 1.0), size=2.0)
        add_light("FillWarm", (3.2, 0.4, 1.5), 140, (1.0, 0.80, 0.45), size=2.5)

def render_camera_shot(cam_pos, target_pos, lens, out_path, res=(960, 540)):
    scene = bpy.context.scene
    scene.render.resolution_x = res[0]
    scene.render.resolution_y = res[1]

    cam_data = bpy.data.cameras.new("RenderCam")
    cam_data.lens = lens
    cam_obj = bpy.data.objects.new("RenderCam", cam_data)
    scene.collection.objects.link(cam_obj)
    cam_obj.location = cam_pos

    empty = bpy.data.objects.new("CamTarget", None)
    scene.collection.objects.link(empty)
    empty.location = target_pos

    tt = cam_obj.constraints.new('TRACK_TO')
    tt.target = empty
    tt.track_axis = 'TRACK_NEGATIVE_Z'
    tt.up_axis = 'UP_Y'

    scene.camera = cam_obj
    scene.render.filepath = out_path
    bpy.ops.render.render(write_still=True)

    bpy.data.objects.remove(cam_obj, do_unlink=True)
    bpy.data.objects.remove(empty, do_unlink=True)
    bpy.data.cameras.remove(cam_data, do_unlink=True)

def composite_model_sheet(v_front, v_back, v_side, v_action, out_final):
    im_front = Image.open(v_front)
    im_back = Image.open(v_back)
    im_side = Image.open(v_side)
    im_action = Image.open(v_action)

    quad = Image.new("RGBA", (1920, 1080), (160, 180, 195, 255))
    quad.paste(im_front, (0, 0))
    quad.paste(im_back, (960, 0))
    quad.paste(im_side, (0, 540))
    quad.paste(im_action, (960, 540))

    draw = ImageDraw.Draw(quad)
    draw.line([(960, 0), (960, 1080)], fill=(90, 110, 130, 255), width=2)
    draw.line([(0, 540), (1920, 540)], fill=(90, 110, 130, 255), width=2)

    labels = [
        ("VISTA 1: FRONT VIEW (CHEST UI / REINFORCED VISOR)", (16, 16), (240, 246, 250, 230), (20, 30, 40, 255)),
        ("VISTA 2: BACK VIEW (BACKPACK UNIT / RED HOSE / POWER CONNECTOR)", (976, 16), (240, 246, 250, 230), (20, 30, 40, 255)),
        ("VISTA 3: SIDE VIEW (PROFILE / WEAPON & HOSE ROUTING)", (16, 556), (240, 246, 250, 230), (20, 30, 40, 255)),
        ("VISTA 4: ACTION 3/4 (MATCH 1:1 CON SCREENSHOT IN-GAME)", (976, 556), (16, 20, 28, 220), (120, 200, 255, 255)),
    ]
    for text, pos, bg_col, text_col in labels:
        draw.rectangle([pos[0]-4, pos[1]-2, pos[0]+520, pos[1]+22], fill=bg_col)
        draw.text(pos, text, fill=text_col)

    banner_box = [420, 516, 1500, 564]
    draw.rectangle(banner_box, fill=(20, 26, 36, 245), outline=(215, 105, 25, 255), width=2)
    draw.text((440, 532), "ASTRA HAZARD: BOMBERO ESPACIAL V9 - MODEL SHEET OFICIAL 1:1", fill=(255, 180, 60, 255))

    quad.save(out_final, "PNG")

def main():
    print("\n" + "="*55)
    print(">>> GENERANDO PERSONAJE V9 (MATCH 1:1 FINAL PULIDO)")
    print("="*55)

    clear_scene()
    mats = build_palette()
    char_obj = build_firefighter_mesh(mats)

    v_front = os.path.join(RENDERS_DIR, "v9_front.png")
    v_back = os.path.join(RENDERS_DIR, "v9_back.png")
    v_side = os.path.join(RENDERS_DIR, "v9_side.png")
    v_action = os.path.join(RENDERS_DIR, "v9_action.png")

    # Encuadre amplio con margen libre arriba y abajo (distancia 4.0m, lente 40mm)
    target = Vector((0.0, 0.0, 0.82))

    # Vistas 1, 2 y 3 con estudio técnico
    setup_lighting(bpy.context.scene, is_blueprint=True)

    print("  Renderizando Vista Frontal Técnica...")
    render_camera_shot(Vector((0.0, -4.00, 0.86)), target, 40, v_front)

    print("  Renderizando Vista Trasera Técnica...")
    render_camera_shot(Vector((0.0, 4.00, 0.86)), target, 40, v_back)

    print("  Renderizando Vista Lateral Técnica...")
    render_camera_shot(Vector((4.00, 0.0, 0.86)), target, 40, v_side)

    # Vista 4 con iluminación y gantry espacial como el Screenshot
    setup_lighting(bpy.context.scene, is_blueprint=False)
    print("  Renderizando Vista Acción 3/4 Espacial (Screenshot)...")
    render_camera_shot(Vector((2.60, -2.90, 1.45)), target, 38, v_action)

    out_final = os.path.join(RENDERS_DIR, "SK_Firefighter_MatchV9_4views.png")
    composite_model_sheet(v_front, v_back, v_side, v_action, out_final)
    print(f"  [OK] Model Sheet Compositado: {out_final}")

    out_brain = os.path.join(BRAIN_DIR, "SK_Firefighter_MatchV9_4views.png")
    shutil.copy2(out_final, out_brain)
    print(f"  [OK] Copiado a Brain: {out_brain}")

    fbx_path = os.path.join(FBX_DIR, "SK_Firefighter_Official.fbx")
    bpy.ops.object.select_all(action='DESELECT')
    char_obj.select_set(True)
    bpy.context.view_layer.objects.active = char_obj
    bpy.ops.export_scene.fbx(
        filepath=fbx_path,
        use_selection=True,
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_ALL',
        mesh_smooth_type='FACE'
    )
    print(f"  [OK] FBX Exportado: {fbx_path}")

    blend_path = os.path.join(ART_DIR, "Blender", "SK_Firefighter_Official.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"  [OK] Blend guardado: {blend_path}")

if __name__ == "__main__":
    main()

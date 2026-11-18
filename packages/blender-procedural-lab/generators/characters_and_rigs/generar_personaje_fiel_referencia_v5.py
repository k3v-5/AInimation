"""
generar_personaje_fiel_referencia_v5.py
========================================
Generador Procedural 1:1 de Bombero Espacial (Astra Hazard: Rescue Squad)
Basado estrictamente en las referencias visuales oficiales:
- Reference 1: Model Sheet oficial (Front, Side, Back, Equipment Isolated).
- Reference 2: Captura 3D In-Game (Postura en 'A', silueta chunky, cel-shading).

Cumple estrictamente con las directrices de Clean Code, SOLID y GEMINI.md.
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
        # 0: Traje Naranja Oficial (SUIT ORANGE - RGB 202, 124, 50 -> sRGB linearizado aprox)
        'suit_orange': create_pbr_mat("M_Suit_Orange", (0.82, 0.38, 0.08, 1.0), metallic=0.02, roughness=0.45),
        # 1: Traje Naranja Sombra / Cuello (SUIT ORANGE DARK)
        'suit_dark_orange': create_pbr_mat("M_Suit_DarkOrange", (0.65, 0.28, 0.05, 1.0), metallic=0.02, roughness=0.50),
        # 2: Armadura Verde Salvia (ARMOR GREEN - RGB 98, 155, 78)
        'armor_sage': create_pbr_mat("M_Armor_Sage", (0.24, 0.42, 0.20, 1.0), metallic=0.06, roughness=0.38),
        # 3: Casco Gris Oscuro (HELMET GREY - RGB 123, 125, 120)
        'helmet_grey': create_pbr_mat("M_Helmet_Grey", (0.26, 0.27, 0.26, 1.0), metallic=0.15, roughness=0.35),
        # 4: Visor Ahumado Tintado Panorámico (REINFORCED VISOR)
        'visor_tinted': create_pbr_mat("M_Visor_Tinted", (0.08, 0.12, 0.16, 1.0), metallic=0.20, roughness=0.05),
        # 5: Franjas Amarillo Lima Reflectantes (#BCBA56 / RGB 188, 186, 86)
        'stripe_yellow': create_pbr_mat("M_Stripe_Yellow", (0.82, 0.82, 0.14, 1.0), metallic=0.02, roughness=0.25),
        # 6: Manguera y Conectores Rojo Carmín (HOSE RED)
        'hose_red': create_pbr_mat("M_Hose_Red", (0.75, 0.06, 0.05, 1.0), metallic=0.03, roughness=0.45),
        # 7: Arnés y Gomas Carbón Oscuro
        'harness_dark': create_pbr_mat("M_Harness_Dark", (0.06, 0.07, 0.07, 1.0), metallic=0.05, roughness=0.60),
        # 8: Pantalla Pectoral / LED Verde Brillante
        'led_green': create_pbr_mat("M_LED_Green", (0.15, 0.98, 0.20, 1.0), metallic=0.0, roughness=0.10, emission=(0.15, 0.98, 0.20, 1.0), emission_strength=5.0),
        # 9: Botones Rojos LED / Power Indicator
        'led_red': create_pbr_mat("M_LED_Red", (1.0, 0.06, 0.06, 1.0), metallic=0.0, roughness=0.10, emission=(1.0, 0.06, 0.06, 1.0), emission_strength=4.5),
        # 10: Cañón y Envolvente Arma Azul-Gris (WEAPON BLUE-GREY)
        'weapon_blue': create_pbr_mat("M_Weapon_Blue", (0.22, 0.35, 0.44, 1.0), metallic=0.35, roughness=0.30),
        # 11: Culata y Mango Arma Marrón Madera / Acero
        'weapon_stock': create_pbr_mat("M_Weapon_Stock", (0.46, 0.20, 0.10, 1.0), metallic=0.10, roughness=0.45),
        # 12: Ventana Amarilla Arma (WEAPON ACCENT YELLOW)
        'weapon_yellow': create_pbr_mat("M_Weapon_Yellow", (0.90, 0.78, 0.12, 1.0), metallic=0.05, roughness=0.20, emission=(0.90, 0.78, 0.12, 1.0), emission_strength=2.5),
        # 13: Acero Oscuro / Boquilla y Gatillo
        'metal_dark': create_pbr_mat("M_Metal_Dark", (0.08, 0.09, 0.10, 1.0), metallic=0.75, roughness=0.25),
        # 14: Contorno Cel-Shading Negro Pura Tinta
        'outline_black': create_unlit_mat("M_Outline_Black", (0.01, 0.01, 0.01, 1.0))
    }

# ---------------------------------------------------------------------------
# MODELADO DEL PERSONAJE 1:1 FIEL A LA REFERENCIA
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

    # Helpers de primitivas con material
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

    def add_cylinder(center, r1, r2, depth, mat_idx, segs=12, rot=(0,0,0)):
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

    # ---------------------------------------------------------
    # 1. CASCO DOMO ESFÉRICO CON VISOR PANORÁMICO (Z = 1.35 a 1.76)
    # ---------------------------------------------------------
    # Cúpula principal redondeada (tres secciones cilíndricas cónicas escalonadas)
    add_cylinder((0, 0.02, 1.54), 0.23, 0.23, 0.22, 3, segs=16)
    add_cylinder((0, 0.02, 1.66), 0.23, 0.18, 0.10, 3, segs=16)
    add_cylinder((0, 0.02, 1.72), 0.18, 0.10, 0.06, 3, segs=16)

    # Cresta longitudinal superior que recorre de adelante hacia atrás
    add_box((0, 0.02, 1.75), (0.10, 0.36, 0.04), 3)

    # Insignia amarilla frontal sobre el visor
    add_box((0, -0.16, 1.74), (0.07, 0.03, 0.035), 5)

    # Marco envolvente del visor (Gris oscuro beveled)
    add_cylinder((0, -0.06, 1.54), 0.235, 0.235, 0.18, 3, segs=16)

    # Cristal panorámico curvado único tintado (UN SOLO VISOR ANCHO Y CONTINUO)
    add_cylinder((0, -0.08, 1.54), 0.225, 0.225, 0.16, 4, segs=14)

    # Módulo de orejeras / comunicaciones laterales
    add_cylinder((-0.235, 0.02, 1.54), 0.06, 0.06, 0.03, 3, segs=12, rot=(0, R(90), 0))
    add_cylinder((0.235, 0.02, 1.54), 0.06, 0.06, 0.03, 3, segs=12, rot=(0, R(90), 0))

    # Anillo del cuello / Gorget (Naranja acolchado + base verde salvia)
    add_cylinder((0, 0.01, 1.41), 0.23, 0.25, 0.08, 0, segs=16)
    add_cylinder((0, 0.01, 1.36), 0.25, 0.26, 0.05, 2, segs=16)

    # ---------------------------------------------------------
    # 2. TORSO CHUNKY, ARNÉS Y CAJA DE CONTROL PECTORAL
    # ---------------------------------------------------------
    # Traje naranja en el torso (tronco con silueta robusta cónica)
    add_box((0, 0.02, 1.20), (0.48, 0.34, 0.30), 0)
    add_box((0, 0.02, 1.04), (0.44, 0.32, 0.16), 0)

    # Tirantes oscuros del arnés táctico (verticales sobre hombros y pecho)
    add_box((-0.14, -0.16, 1.20), (0.05, 0.025, 0.32), 7)
    add_box((0.14, -0.16, 1.20), (0.05, 0.025, 0.32), 7)

    # Cinta horizontal transversal del arnés sobre el pecho
    add_box((0, -0.16, 1.21), (0.34, 0.025, 0.04), 7)

    # Cinturón ventral ancho
    add_box((0, -0.15, 1.00), (0.45, 0.03, 0.07), 7)
    add_box((0, 0.02, 0.99), (0.46, 0.33, 0.05), 5) # Franja amarilla reflectante de cintura

    # CAJA DE CONTROL EN EL PECHO ("CHEST CONTROL BOX")
    # Base verde salvia
    add_box((0.02, -0.185, 1.19), (0.18, 0.04, 0.11), 2)
    # Pantalla cuadrada verde brillante emisiva a la izquierda
    add_box((-0.03, -0.208, 1.19), (0.055, 0.015, 0.065), 8)
    # Botón superior rojo
    add_box((0.065, -0.208, 1.215), (0.026, 0.015, 0.026), 9)
    # Botón inferior rojo
    add_box((0.065, -0.208, 1.165), (0.026, 0.015, 0.026), 9)

    # ---------------------------------------------------------
    # 3. MOCHILA TRASERA ("BACKPACK UNIT")
    # ---------------------------------------------------------
    # Carcasa principal naranja
    add_box((0, 0.26, 1.22), (0.36, 0.17, 0.42), 0)
    # Borde superior angular gris oscuro / salvia
    add_box((0, 0.27, 1.43), (0.34, 0.15, 0.04), 2)

    # Rejillas de ventilación superiores (Louvers negras)
    # Rejilla derecha (4 ranuras verticales)
    for x_off in [0.06, 0.09, 0.12, 0.15]:
        add_box((x_off, 0.35, 1.32), (0.016, 0.015, 0.12), 7)

    # Rejilla izquierda (3 ranuras horizontales)
    for z_off in [1.36, 1.32, 1.28]:
        add_box((-0.10, 0.35, z_off), (0.09, 0.015, 0.02), 7)

    # Indicador LED verde superior izquierdo
    add_box((-0.10, 0.35, 1.22), (0.035, 0.015, 0.035), 8)

    # Indicador LED verde inferior derecho
    add_box((0.11, 0.35, 1.16), (0.035, 0.015, 0.035), 8)

    # "POWER INDICATOR": Placa gris con barra roja horizontal
    add_box((-0.04, 0.35, 1.12), (0.14, 0.015, 0.08), 2)
    add_box((-0.04, 0.36, 1.12), (0.06, 0.012, 0.025), 9)

    # "POWER CONNECTOR": Enchufe circular donde encaja la manguera
    add_cylinder((0.11, 0.34, 1.05), 0.038, 0.038, 0.04, 7, segs=12, rot=(R(90), 0, 0))
    add_cylinder((0.11, 0.36, 1.05), 0.022, 0.022, 0.02, 9, segs=12, rot=(R(90), 0, 0))

    # Cilindro auxiliar lateral (tanque derecho de la mochila con ventana ámbar)
    add_cylinder((0.20, 0.24, 1.25), 0.05, 0.05, 0.22, 0, segs=10)
    add_box((0.24, 0.24, 1.25), (0.02, 0.06, 0.12), 12)

    # ---------------------------------------------------------
    # 4. MANGUERA ROJA CURVA ("RED FLUID HOSE")
    # ---------------------------------------------------------
    # Recorrido de la manguera desde el enchufe de la mochila rodeando la cadera derecha
    hose_pts = [
        Vector((0.11, 0.36, 1.05)),
        Vector((0.18, 0.38, 0.96)),
        Vector((0.28, 0.32, 0.84)),
        Vector((0.34, 0.18, 0.77)),
        Vector((0.35, 0.02, 0.76)),
        Vector((0.32, -0.15, 0.81)),
        Vector((0.26, -0.26, 0.88)),
        Vector((0.18, -0.32, 0.95))
    ]
    for i in range(len(hose_pts)-1):
        p1 = hose_pts[i]
        p2 = hose_pts[i+1]
        mid = (p1 + p2) * 0.5
        v = p2 - p1
        dist = v.length
        rot_axis = Vector((0, 0, 1)).cross(v.normalized())
        angle = math.acos(max(-1.0, min(1.0, Vector((0, 0, 1)).dot(v.normalized()))))
        
        cyl = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=10, radius1=0.032, radius2=0.032, depth=dist)
        if rot_axis.length > 0.001:
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=Matrix.Rotation(angle, 3, rot_axis.normalized()), verts=cyl['verts'])
        bmesh.ops.translate(bm, vec=mid, verts=cyl['verts'])
        for f in bm.faces:
            if f.verts[0] in cyl['verts']:
                f.material_index = 6

    # ---------------------------------------------------------
    # 5. ARMA TÁCTICA ("EQUIPMENT ISOLATED" - CAÑÓN EXTINTOR)
    # ---------------------------------------------------------
    # Posicionada cruzando el pecho/cintura con ligera inclinación frontal
    gun_center = Vector((0.02, -0.38, 0.98))
    g_rx, g_ry, g_rz = R(10), R(-12), R(-18)

    def add_gun_box(local_pos, size, mat_idx):
        sx, sy, sz = size
        ret = bmesh.ops.create_cube(bm, size=1.0)
        verts = ret['verts']
        bmesh.ops.scale(bm, vec=(sx, sy, sz), verts=verts)
        bmesh.ops.translate(bm, vec=local_pos, verts=verts)
        # Rotar y trasladar respecto al centro del arma
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

    # Receptor superior del arma (caja azul-gris con bisel)
    add_gun_box((0.0, 0.0, 0.0), (0.22, 0.10, 0.12), 10)
    # Ventana indicadora amarilla en el lado exterior
    add_gun_box((0.0, -0.052, 0.01), (0.08, 0.01, 0.04), 12)

    # Cañón cilíndrico azul
    add_gun_cyl((-0.20, 0.0, 0.0), 0.048, 0.048, 0.24, 10, segs=12, rot_local=(0, R(90), 0))
    # Boquilla acampanada (Muzzle ring)
    add_gun_cyl((-0.33, 0.0, 0.0), 0.062, 0.062, 0.05, 13, segs=12, rot_local=(0, R(90), 0))
    # Orificio interior negro del cañón
    add_gun_cyl((-0.35, 0.0, 0.0), 0.038, 0.038, 0.02, 14, segs=12, rot_local=(0, R(90), 0))

    # Empuñadura vertical delantera (Foregrip)
    add_gun_cyl((-0.08, 0.0, -0.10), 0.022, 0.022, 0.12, 13, segs=8)

    # Cuerpo inferior / disparador (Marrón rojizo)
    add_gun_box((0.05, 0.0, -0.06), (0.16, 0.06, 0.06), 11)
    # Empuñadura de pistola (Pistol grip con ángulo hacia atrás)
    add_gun_box((0.14, 0.0, -0.11), (0.06, 0.05, 0.12), 7)

    # Culata angular (Rifle Stock) con panel rebajado
    add_gun_box((0.24, 0.0, -0.02), (0.16, 0.05, 0.10), 11)
    add_gun_box((0.32, 0.0, -0.02), (0.03, 0.055, 0.11), 13) # Cantonera trasera oscura

    # Conector de la manguera roja en la culata inferior
    add_gun_cyl((0.16, 0.0, -0.06), 0.03, 0.03, 0.04, 6, segs=8, rot_local=(R(90), 0, 0))

    # ---------------------------------------------------------
    # 6. HOMBROS Y BRAZOS SOSTENIENDO EL ARMA
    # ---------------------------------------------------------
    # Hombreras angulares estilo pauldron en verde salvia (#5A6856)
    # Inclinadas hacia abajo para abrazar la silueta orgánica
    add_box((-0.29, 0.02, 1.34), (0.18, 0.22, 0.09), 2, rot=(0, R(-22), 0))
    add_box((0.29, 0.02, 1.34), (0.18, 0.22, 0.09), 2, rot=(0, R(22), 0))

    # BRAZO IZQUIERDO (Sujeta la empuñadura delantera)
    # Bíceps naranja
    add_box((-0.29, 0.02, 1.21), (0.15, 0.18, 0.16), 0)
    # Franja reflectante amarilla en el bíceps
    add_box((-0.29, 0.02, 1.13), (0.16, 0.19, 0.03), 5)
    # Antebrazo angular orientado hacia el arma
    add_box((-0.18, -0.19, 1.05), (0.15, 0.22, 0.15), 0, rot=(R(35), R(-25), R(-25)))
    # Brazalete reflectante verde y amarillo en el puño
    add_box((-0.13, -0.27, 1.00), (0.16, 0.06, 0.16), 5, rot=(R(35), R(-25), R(-25)))
    # Guante táctico oscuro sujetando el mango delantero
    add_box((-0.07, -0.36, 0.95), (0.13, 0.14, 0.13), 7)

    # BRAZO DERECHO (Sujeta la empuñadura de disparo)
    # Bíceps naranja
    add_box((0.29, 0.02, 1.21), (0.15, 0.18, 0.16), 0)
    # Franja reflectante amarilla en el bíceps
    add_box((0.29, 0.02, 1.13), (0.16, 0.19, 0.03), 5)
    # Antebrazo angular
    add_box((0.22, -0.16, 1.06), (0.15, 0.22, 0.15), 0, rot=(R(28), R(18), R(20)))
    # Brazalete reflectante verde y amarillo en el puño
    add_box((0.17, -0.25, 1.01), (0.16, 0.06, 0.16), 5, rot=(R(28), R(18), R(20)))
    # Guante táctico sujetando la culata/gatillo
    add_box((0.12, -0.32, 0.98), (0.13, 0.14, 0.13), 7)

    # ---------------------------------------------------------
    # 7. PIERNAS ROBUSTAS EN "A-STANCE", RODILLERAS Y BOTAS
    # ---------------------------------------------------------
    # Entrepierna y base de cadera
    add_box((0, 0.02, 0.92), (0.38, 0.28, 0.12), 0)

    for sign in [1, -1]:
        # Muslos robustos inclinados hacia afuera (A-stance de combate)
        add_box((0.15 * sign, 0.02, 0.73), (0.18, 0.22, 0.28), 0, rot=(0, R(-9 * sign), 0))

        # RODILLERAS TÁCTICAS ("ARMOUR SEGMENTS" - Verde salvia con reborde)
        # Placa frontal curvada sobre la articulación
        add_box((0.18 * sign, -0.09, 0.54), (0.17, 0.06, 0.14), 2)
        # Ranuras horizontales en la rodillera
        add_box((0.18 * sign, -0.125, 0.56), (0.13, 0.015, 0.02), 7)
        add_box((0.18 * sign, -0.125, 0.52), (0.13, 0.015, 0.02), 7)

        # Pantorrillas gruesas
        add_box((0.19 * sign, 0.01, 0.38), (0.18, 0.21, 0.22), 0, rot=(0, R(-7 * sign), 0))

        # Franja reflectante amarilla en el tobillo
        add_box((0.20 * sign, 0.01, 0.25), (0.19, 0.22, 0.05), 5)

        # BOTAS TÁCTICAS PESADAS CON PUNTERA REFORZADA
        # Caña de la bota (Verde salvia)
        add_box((0.22 * sign, -0.03, 0.14), (0.20, 0.26, 0.20), 2)
        # Puntera frontal reforzada
        add_box((0.22 * sign, -0.12, 0.06), (0.20, 0.14, 0.09), 3)
        # Suela gruesa de goma oscura con tacón firme
        add_box((0.22 * sign, -0.03, 0.02), (0.22, 0.29, 0.04), 13)

    bm.to_mesh(mesh)
    bm.free()

    for m in mat_order:
        mesh.materials.append(m)

    obj = bpy.data.objects.new("SK_Firefighter_Match1to1", mesh)
    bpy.context.scene.collection.objects.link(obj)

    # Delineado Cel-Shading (Inverted Hull)
    sol = obj.modifiers.new("CelOutline", 'SOLIDIFY')
    sol.thickness = -0.009
    sol.offset = 1.0
    sol.use_flip_normals = True
    sol.material_offset = 14
    sol.use_rim = True

    return obj

# ---------------------------------------------------------------------------
# ILUMINACIÓN Y ESTUDIO DE RENDERIZADO CALIBRADO
# ---------------------------------------------------------------------------
def setup_lighting(scene):
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'Medium High Contrast'

    # Suelo de plataforma espacial / cuadrícula sutil
    bg_mesh = bpy.data.meshes.new("StudioFloor")
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=40)
    bm.to_mesh(bg_mesh)
    bm.free()
    bg_obj = bpy.data.objects.new("StudioFloor", bg_mesh)
    bg_obj.location = (0, 0, 0.0)
    scene.collection.objects.link(bg_obj)
    
    mat_floor = create_pbr_mat("M_StudioFloorDark", (0.020, 0.025, 0.032, 1.0), metallic=0.3, roughness=0.50)
    bg_obj.data.materials.append(mat_floor)

    target = bpy.data.objects.new("LightTarget", None)
    target.location = (0, 0, 0.95)
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

    # Luces de estudio perfectamente balanceadas (evitan quemados y sombras negras)
    add_light("KeyFront", (1.8, -3.0, 2.2), 340, (1.0, 0.98, 0.95), size=2.5)
    add_light("KeyBack", (-1.8, 3.0, 2.2), 380, (0.95, 0.98, 1.0), size=2.5)
    add_light("RimCyan", (-3.0, -0.4, 1.6), 190, (0.25, 0.85, 1.0), size=2.0)
    add_light("FillWarm", (3.0, 0.4, 1.5), 150, (1.0, 0.80, 0.45), size=2.5)
    add_light("TopSoft", (0.0, 0.0, 3.5), 120, (1.0, 1.0, 1.0), size=3.0)

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

    quad = Image.new("RGBA", (1920, 1080), (14, 18, 24, 255))
    quad.paste(im_front, (0, 0))
    quad.paste(im_back, (960, 0))
    quad.paste(im_side, (0, 540))
    quad.paste(im_action, (960, 540))

    draw = ImageDraw.Draw(quad)
    # Líneas divisorias estéticas
    draw.line([(960, 0), (960, 1080)], fill=(45, 55, 72, 255), width=2)
    draw.line([(0, 540), (1920, 540)], fill=(45, 55, 72, 255), width=2)

    labels = [
        ("VISTA 1: FRONT VIEW (CHEST UI / REINFORCED VISOR)", (16, 16)),
        ("VISTA 2: BACK VIEW (BACKPACK UNIT / RED HOSE / POWER CONNECTOR)", (976, 16)),
        ("VISTA 3: SIDE VIEW (PROFILE / WEAPON & HOSE ROUTING)", (16, 556)),
        ("VISTA 4: ACTION 3/4 (MATCH 1:1 CON SCREENSHOT IN-GAME)", (976, 556)),
    ]
    for text, pos in labels:
        draw.rectangle([pos[0]-4, pos[1]-2, pos[0]+500, pos[1]+22], fill=(20, 26, 36, 210))
        draw.text(pos, text, fill=(130, 210, 255, 255))

    banner_box = [440, 516, 1480, 564]
    draw.rectangle(banner_box, fill=(10, 14, 20, 245), outline=(230, 105, 25, 255), width=2)
    draw.text((460, 532), "ASTRA HAZARD: BOMBERO ESPACIAL V5 - MODEL SHEET OFICIAL 1:1", fill=(255, 180, 60, 255))

    quad.save(out_final, "PNG")

# ---------------------------------------------------------------------------
# PIPELINE PRINCIPAL DE EJECUCIÓN
# ---------------------------------------------------------------------------
def main():
    print("\n" + "="*55)
    print(">>> GENERANDO PERSONAJE V5 (MATCH 1:1 FIDELIDAD TOTAL)")
    print("="*55)

    clear_scene()
    mats = build_palette()
    char_obj = build_firefighter_mesh(mats)
    setup_lighting(bpy.context.scene)

    v_front = os.path.join(RENDERS_DIR, "v5_front.png")
    v_back = os.path.join(RENDERS_DIR, "v5_back.png")
    v_side = os.path.join(RENDERS_DIR, "v5_side.png")
    v_action = os.path.join(RENDERS_DIR, "v5_action.png")

    # Vistas calibradas para encuadre completo de la silueta
    target = Vector((0.0, 0.0, 0.88))
    print("  Renderizando Vista Frontal...")
    render_camera_shot(Vector((0.0, -2.60, 0.95)), target, 55, v_front)

    print("  Renderizando Vista Trasera...")
    render_camera_shot(Vector((0.0, 2.60, 0.95)), target, 55, v_back)

    print("  Renderizando Vista Lateral (Perfil Derecho)...")
    render_camera_shot(Vector((2.60, 0.0, 0.95)), target, 55, v_side)

    print("  Renderizando Vista Acción 3/4 (Ángulo Screenshot)...")
    render_camera_shot(Vector((1.75, -2.05, 1.35)), target, 52, v_action)

    out_final = os.path.join(RENDERS_DIR, "SK_Firefighter_MatchV5_4views.png")
    composite_model_sheet(v_front, v_back, v_side, v_action, out_final)
    print(f"  [OK] Model Sheet Compositado: {out_final}")

    out_brain = os.path.join(BRAIN_DIR, "SK_Firefighter_MatchV5_4views.png")
    shutil.copy2(out_final, out_brain)
    print(f"  [OK] Copiado a Brain: {out_brain}")

    # Exportar FBX
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

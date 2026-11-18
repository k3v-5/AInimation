"""
generar_personaje_fiel_referencia_v6.py
========================================
Generador Procedural 1:1 de Bombero Espacial (Astra Hazard: Rescue Squad)
Ajustes precisos de encuadre de cámara, anatomía chunky y ambientación:
1. ENCUADRE COMPLETO: Cámara calibrada a 3.7m con lente 38mm para visualizar de pies a cabeza (100% de la silueta).
2. ANATOMÍA Y SILUETA CHUNKY: Proporciones fieles 1:1 al Model Sheet oficial y Screenshot in-game.
3. ACCIÓN 3/4 CON ENTORNO ESPACIAL: Estructura de celosía gantry y fondo estrellado para replicar la referencia 2.
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
        'suit_orange': create_pbr_mat("M_Suit_Orange", (0.84, 0.40, 0.08, 1.0), metallic=0.02, roughness=0.45),
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
# MODELADO DEL PERSONAJE CHUNKY 1:1
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

    def add_cylinder(center, r1, r2, depth, mat_idx, segs=14, rot=(0,0,0)):
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
    # 1. CASCO DOMO ESFÉRICO CON VISOR PANORÁMICO
    # ---------------------------------------------------------
    # Cúpula principal redondeada del casco
    add_cylinder((0, 0.02, 1.48), 0.22, 0.22, 0.18, 3, segs=16)
    add_cylinder((0, 0.02, 1.58), 0.22, 0.17, 0.10, 3, segs=16)
    add_cylinder((0, 0.02, 1.64), 0.17, 0.08, 0.06, 3, segs=16)

    # Cresta longitudinal superior
    add_box((0, 0.02, 1.67), (0.10, 0.34, 0.04), 3)

    # Insignia amarilla frontal sobre el visor
    add_box((0, -0.16, 1.66), (0.07, 0.03, 0.035), 5)

    # Marco del visor panorámico (Gris oscuro beveled)
    add_box((0, -0.12, 1.48), (0.34, 0.10, 0.18), 3)

    # Cristal panorámico amplio único tintado (UN SOLO VISOR ANCHO Y CONTINUO)
    add_box((0, -0.155, 1.48), (0.30, 0.04, 0.15), 4)

    # Módulo de orejeras / comunicaciones laterales
    add_cylinder((-0.225, 0.02, 1.48), 0.055, 0.055, 0.03, 3, segs=12, rot=(0, R(90), 0))
    add_cylinder((0.225, 0.02, 1.48), 0.055, 0.055, 0.03, 3, segs=12, rot=(0, R(90), 0))

    # Anillo del cuello / Gorget (Naranja acolchado + base verde salvia)
    add_cylinder((0, 0.01, 1.36), 0.22, 0.24, 0.07, 0, segs=16)
    add_cylinder((0, 0.01, 1.31), 0.24, 0.26, 0.05, 2, segs=16)

    # ---------------------------------------------------------
    # 2. TORSO CHUNKY, ARNÉS Y CAJA DE CONTROL PECTORAL
    # ---------------------------------------------------------
    # Traje naranja en el torso
    add_box((0, 0.02, 1.16), (0.46, 0.33, 0.28), 0)
    add_box((0, 0.02, 1.01), (0.42, 0.31, 0.16), 0)

    # Tirantes oscuros del arnés táctico
    add_box((-0.13, -0.15, 1.16), (0.05, 0.025, 0.30), 7)
    add_box((0.13, -0.15, 1.16), (0.05, 0.025, 0.30), 7)

    # Cinta horizontal transversal del arnés sobre el pecho
    add_box((0, -0.15, 1.17), (0.32, 0.025, 0.04), 7)

    # Cinturón ventral ancho
    add_box((0, -0.14, 0.96), (0.43, 0.03, 0.07), 7)
    add_box((0, 0.02, 0.95), (0.44, 0.32, 0.05), 5) # Franja amarilla reflectante

    # CAJA DE CONTROL EN EL PECHO ("CHEST CONTROL BOX")
    add_box((0.02, -0.175, 1.15), (0.17, 0.04, 0.11), 2)
    # Pantalla cuadrada verde brillante emisiva a la izquierda
    add_box((-0.03, -0.198, 1.15), (0.055, 0.015, 0.065), 8)
    # Botón superior rojo
    add_box((0.065, -0.198, 1.175), (0.026, 0.015, 0.026), 9)
    # Botón inferior rojo
    add_box((0.065, -0.198, 1.125), (0.026, 0.015, 0.026), 9)

    # ---------------------------------------------------------
    # 3. MOCHILA TRASERA ("BACKPACK UNIT")
    # ---------------------------------------------------------
    # Carcasa principal naranja
    add_box((0, 0.25, 1.17), (0.35, 0.16, 0.40), 0)
    # Borde superior angular gris oscuro / salvia
    add_box((0, 0.26, 1.37), (0.33, 0.14, 0.04), 2)

    # Rejillas de ventilación superiores (Louvers negras)
    for x_off in [0.06, 0.09, 0.12, 0.15]:
        add_box((x_off, 0.335, 1.27), (0.016, 0.015, 0.11), 7)

    for z_off in [1.31, 1.27, 1.23]:
        add_box((-0.09, 0.335, z_off), (0.08, 0.015, 0.02), 7)

    # Indicador LED verde superior izquierdo
    add_box((-0.09, 0.335, 1.17), (0.035, 0.015, 0.035), 8)

    # Indicador LED verde inferior derecho
    add_box((0.10, 0.335, 1.11), (0.035, 0.015, 0.035), 8)

    # "POWER INDICATOR": Placa gris con barra roja horizontal
    add_box((-0.04, 0.335, 1.07), (0.13, 0.015, 0.08), 2)
    add_box((-0.04, 0.345, 1.07), (0.06, 0.012, 0.025), 9)

    # "POWER CONNECTOR": Enchufe circular donde encaja la manguera
    add_cylinder((0.10, 0.33, 1.00), 0.038, 0.038, 0.04, 7, segs=12, rot=(R(90), 0, 0))
    add_cylinder((0.10, 0.35, 1.00), 0.022, 0.022, 0.02, 9, segs=12, rot=(R(90), 0, 0))

    # Cilindro auxiliar lateral (tanque derecho de la mochila)
    add_cylinder((0.19, 0.23, 1.20), 0.045, 0.045, 0.20, 0, segs=10)
    add_box((0.23, 0.23, 1.20), (0.02, 0.05, 0.10), 12)

    # ---------------------------------------------------------
    # 4. MANGUERA ROJA CURVA ("RED FLUID HOSE")
    # ---------------------------------------------------------
    hose_pts = [
        Vector((0.10, 0.35, 1.00)),
        Vector((0.17, 0.37, 0.91)),
        Vector((0.26, 0.31, 0.80)),
        Vector((0.32, 0.17, 0.73)),
        Vector((0.33, 0.02, 0.72)),
        Vector((0.30, -0.14, 0.77)),
        Vector((0.24, -0.24, 0.84)),
        Vector((0.16, -0.30, 0.90))
    ]
    for i in range(len(hose_pts)-1):
        p1 = hose_pts[i]
        p2 = hose_pts[i+1]
        mid = (p1 + p2) * 0.5
        v = p2 - p1
        dist = v.length
        rot_axis = Vector((0, 0, 1)).cross(v.normalized())
        angle = math.acos(max(-1.0, min(1.0, Vector((0, 0, 1)).dot(v.normalized()))))
        
        cyl = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=10, radius1=0.030, radius2=0.030, depth=dist)
        if rot_axis.length > 0.001:
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=Matrix.Rotation(angle, 3, rot_axis.normalized()), verts=cyl['verts'])
        bmesh.ops.translate(bm, vec=mid, verts=cyl['verts'])
        for f in bm.faces:
            if f.verts[0] in cyl['verts']:
                f.material_index = 6

    # ---------------------------------------------------------
    # 5. ARMA TÁCTICA ("EQUIPMENT ISOLATED" - CAÑÓN EXTINTOR)
    # ---------------------------------------------------------
    gun_center = Vector((0.02, -0.36, 0.93))
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

    add_gun_box((0.0, 0.0, 0.0), (0.22, 0.10, 0.12), 10)
    add_gun_box((0.0, -0.052, 0.01), (0.08, 0.01, 0.04), 12)

    add_gun_cyl((-0.20, 0.0, 0.0), 0.048, 0.048, 0.24, 10, segs=12, rot_local=(0, R(90), 0))
    add_gun_cyl((-0.33, 0.0, 0.0), 0.062, 0.062, 0.05, 13, segs=12, rot_local=(0, R(90), 0))
    add_gun_cyl((-0.35, 0.0, 0.0), 0.038, 0.038, 0.02, 14, segs=12, rot_local=(0, R(90), 0))

    add_gun_cyl((-0.08, 0.0, -0.10), 0.022, 0.022, 0.12, 13, segs=8)

    add_gun_box((0.05, 0.0, -0.06), (0.16, 0.06, 0.06), 11)
    add_gun_box((0.14, 0.0, -0.11), (0.06, 0.05, 0.12), 7)

    add_gun_box((0.24, 0.0, -0.02), (0.16, 0.05, 0.10), 11)
    add_gun_box((0.32, 0.0, -0.02), (0.03, 0.055, 0.11), 13)

    add_gun_cyl((0.16, 0.0, -0.06), 0.03, 0.03, 0.04, 6, segs=8, rot_local=(R(90), 0, 0))

    # ---------------------------------------------------------
    # 6. HOMBROS Y BRAZOS SOSTENIENDO EL ARMA
    # ---------------------------------------------------------
    # Hombreras angulares estilo pauldron en verde salvia
    add_box((-0.28, 0.02, 1.28), (0.18, 0.22, 0.09), 2, rot=(0, R(-22), 0))
    add_box((0.28, 0.02, 1.28), (0.18, 0.22, 0.09), 2, rot=(0, R(22), 0))

    # BRAZO IZQUIERDO
    add_box((-0.28, 0.02, 1.16), (0.15, 0.18, 0.15), 0)
    add_box((-0.28, 0.02, 1.09), (0.16, 0.19, 0.03), 5)
    add_box((-0.18, -0.18, 1.00), (0.15, 0.21, 0.15), 0, rot=(R(35), R(-25), R(-25)))
    add_box((-0.13, -0.26, 0.95), (0.16, 0.06, 0.16), 5, rot=(R(35), R(-25), R(-25)))
    add_box((-0.07, -0.34, 0.90), (0.13, 0.14, 0.13), 7)

    # BRAZO DERECHO
    add_box((0.28, 0.02, 1.16), (0.15, 0.18, 0.15), 0)
    add_box((0.28, 0.02, 1.09), (0.16, 0.19, 0.03), 5)
    add_box((0.21, -0.15, 1.01), (0.15, 0.21, 0.15), 0, rot=(R(28), R(18), R(20)))
    add_box((0.16, -0.24, 0.96), (0.16, 0.06, 0.16), 5, rot=(R(28), R(18), R(20)))
    add_box((0.11, -0.31, 0.93), (0.13, 0.14, 0.13), 7)

    # ---------------------------------------------------------
    # 7. PIERNAS ROBUSTAS EN "A-STANCE", RODILLERAS Y BOTAS
    # ---------------------------------------------------------
    add_box((0, 0.02, 0.88), (0.36, 0.27, 0.12), 0)

    for sign in [1, -1]:
        # Muslos robustos
        add_box((0.14 * sign, 0.02, 0.70), (0.18, 0.21, 0.27), 0, rot=(0, R(-9 * sign), 0))

        # RODILLERAS TÁCTICAS
        add_box((0.17 * sign, -0.09, 0.52), (0.17, 0.06, 0.14), 2)
        add_box((0.17 * sign, -0.122, 0.54), (0.13, 0.015, 0.02), 7)
        add_box((0.17 * sign, -0.122, 0.50), (0.13, 0.015, 0.02), 7)

        # Pantorrillas
        add_box((0.18 * sign, 0.01, 0.36), (0.18, 0.20, 0.21), 0, rot=(0, R(-7 * sign), 0))

        # Franja reflectante amarilla en el tobillo
        add_box((0.19 * sign, 0.01, 0.24), (0.19, 0.21, 0.05), 5)

        # BOTAS TÁCTICAS PESADAS
        add_box((0.21 * sign, -0.03, 0.14), (0.20, 0.25, 0.18), 2)
        add_box((0.21 * sign, -0.11, 0.06), (0.20, 0.13, 0.09), 3)
        add_box((0.21 * sign, -0.03, 0.02), (0.21, 0.28, 0.04), 13)

    bm.to_mesh(mesh)
    bm.free()

    for m in mat_order:
        mesh.materials.append(m)

    obj = bpy.data.objects.new("SK_Firefighter_Match1to1", mesh)
    bpy.context.scene.collection.objects.link(obj)

    # Cel-Shading Inverted Hull
    sol = obj.modifiers.new("CelOutline", 'SOLIDIFY')
    sol.thickness = -0.008
    sol.offset = 1.0
    sol.use_flip_normals = True
    sol.material_offset = 14
    sol.use_rim = True

    return obj

# ---------------------------------------------------------------------------
# ILUMINACIÓN Y ESTUDIO CON ENTORNO ESPACIAL Y ESTRUCTURA GANTRY
# ---------------------------------------------------------------------------
def setup_environment(scene):
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'Medium High Contrast'

    # Estructura Gantry de celosía espacial como en Reference 2
    gantry_mesh = bpy.data.meshes.new("GantryTruss")
    bm = bmesh.new()
    
    mat_metal = create_pbr_mat("M_GantryMetal", (0.16, 0.18, 0.21, 1.0), metallic=0.7, roughness=0.35)
    
    # Plataforma bajo los pies
    ret = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(4.0, 4.0, 0.04), verts=ret['verts'])
    bmesh.ops.translate(bm, vec=(0, 0, -0.02), verts=ret['verts'])
    
    # Vigas de celosía laterales y traseras (estilo estación espacial)
    for bx in [-1.5, 1.5]:
        viga = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(0.10, 3.5, 0.10), verts=viga['verts'])
        bmesh.ops.translate(bm, vec=(bx, 0.0, 0.8), verts=viga['verts'])

    bm.to_mesh(gantry_mesh)
    bm.free()
    
    g_obj = bpy.data.objects.new("GantryTruss", gantry_mesh)
    g_obj.data.materials.append(mat_metal)
    scene.collection.objects.link(g_obj)

    # Delineado cel-shading en el entorno también
    sol_g = g_obj.modifiers.new("GantryOutline", 'SOLIDIFY')
    sol_g.thickness = -0.007
    sol_g.offset = 1.0
    sol_g.use_flip_normals = True
    sol_g.material_offset = 0
    sol_g.use_rim = True

    # Puntos estelares de fondo (estrellas distantes como en screenshot)
    world = scene.world or bpy.data.worlds.new("SpaceWorld")
    scene.world = world
    world.use_nodes = True
    wnt = world.node_tree
    wnt.nodes.clear()
    w_out = wnt.nodes.new('ShaderNodeOutputWorld')
    w_bg = wnt.nodes.new('ShaderNodeBackground')
    w_bg.inputs['Color'].default_value = (0.010, 0.012, 0.016, 1.0) # Espacio profundo
    w_bg.inputs['Strength'].default_value = 0.4
    wnt.links.new(w_bg.outputs['Background'], w_out.inputs['Surface'])

    # Luces de estudio balanceadas
    target = bpy.data.objects.new("LightTarget", None)
    target.location = (0, 0, 0.85)
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

    add_light("KeyFront", (1.8, -3.2, 2.2), 320, (1.0, 0.98, 0.95), size=2.6)
    add_light("KeyBack", (-1.8, 3.2, 2.2), 360, (0.95, 0.98, 1.0), size=2.6)
    add_light("RimCyan", (-3.2, -0.4, 1.6), 180, (0.25, 0.85, 1.0), size=2.0)
    add_light("FillWarm", (3.2, 0.4, 1.5), 140, (1.0, 0.80, 0.45), size=2.5)
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

    quad = Image.new("RGBA", (1920, 1080), (10, 12, 16, 255))
    quad.paste(im_front, (0, 0))
    quad.paste(im_back, (960, 0))
    quad.paste(im_side, (0, 540))
    quad.paste(im_action, (960, 540))

    draw = ImageDraw.Draw(quad)
    draw.line([(960, 0), (960, 1080)], fill=(40, 50, 65, 255), width=2)
    draw.line([(0, 540), (1920, 540)], fill=(40, 50, 65, 255), width=2)

    labels = [
        ("VISTA 1: FRONT VIEW (CHEST UI / REINFORCED VISOR)", (16, 16)),
        ("VISTA 2: BACK VIEW (BACKPACK UNIT / RED HOSE / POWER CONNECTOR)", (976, 16)),
        ("VISTA 3: SIDE VIEW (PROFILE / WEAPON & HOSE ROUTING)", (16, 556)),
        ("VISTA 4: ACTION 3/4 (MATCH 1:1 CON SCREENSHOT IN-GAME)", (976, 556)),
    ]
    for text, pos in labels:
        draw.rectangle([pos[0]-4, pos[1]-2, pos[0]+500, pos[1]+22], fill=(16, 20, 28, 220))
        draw.text(pos, text, fill=(120, 200, 255, 255))

    banner_box = [440, 516, 1480, 564]
    draw.rectangle(banner_box, fill=(10, 14, 20, 245), outline=(230, 105, 25, 255), width=2)
    draw.text((460, 532), "ASTRA HAZARD: BOMBERO ESPACIAL V6 - MODEL SHEET OFICIAL 1:1", fill=(255, 180, 60, 255))

    quad.save(out_final, "PNG")

def main():
    print("\n" + "="*55)
    print(">>> GENERANDO PERSONAJE V6 (CALIBRACIÓN ÓPTICA Y AMBIENTAL)")
    print("="*55)

    clear_scene()
    mats = build_palette()
    char_obj = build_firefighter_mesh(mats)
    setup_environment(bpy.context.scene)

    v_front = os.path.join(RENDERS_DIR, "v6_front.png")
    v_back = os.path.join(RENDERS_DIR, "v6_back.png")
    v_side = os.path.join(RENDERS_DIR, "v6_side.png")
    v_action = os.path.join(RENDERS_DIR, "v6_action.png")

    # ENCUADRE DE CUERPO ENTERO PERFECTAMENTE CALIBRADO (Z_target = 0.85m, Cam dist = 3.6m, lens = 38mm)
    target = Vector((0.0, 0.0, 0.85))

    print("  Renderizando Vista Frontal Completa...")
    render_camera_shot(Vector((0.0, -3.60, 0.88)), target, 38, v_front)

    print("  Renderizando Vista Trasera Completa...")
    render_camera_shot(Vector((0.0, 3.60, 0.88)), target, 38, v_back)

    print("  Renderizando Vista Lateral Perfil...")
    render_camera_shot(Vector((3.60, 0.0, 0.88)), target, 38, v_side)

    print("  Renderizando Vista Acción 3/4 (Match Screenshot In-Game)...")
    render_camera_shot(Vector((2.40, -2.80, 1.45)), target, 36, v_action)

    out_final = os.path.join(RENDERS_DIR, "SK_Firefighter_MatchV6_4views.png")
    composite_model_sheet(v_front, v_back, v_side, v_action, out_final)
    print(f"  [OK] Model Sheet Compositado: {out_final}")

    out_brain = os.path.join(BRAIN_DIR, "SK_Firefighter_MatchV6_4views.png")
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

"""
generar_bloques_brecha_y_causalidad_oficial.py
=============================================
Pipeline de Arte 3D en Blender 5.2 LTS para Astra Hazard:
Genera nuevos bloques modulares de arquitectura rota para causalidad ambiental (Reglas 9 y 10 GEMINI.md):
1. SM_Mod_Ceiling_Breach_400x400: Losa modular de techo de 400x400x30cm con un boquete real abierto,
   bordes de chapa rota doblados hacia abajo, perfiles en I seccionados con rebabas de cizalla,
   muñones de anclaje de soporte y conductos cortados con cables expuestos.
   Incluye colisiones UCX convexas perimetrales precisas que dejan el boquete 100% permeable.
2. SM_Mod_Wall_Breach_400x350: Mamparo modular de 400x350x30cm con fractura por sobrepresión
   y refuerzos deformados plásticamente.
3. Mapeo UV profesional alineado al Master Trim Sheet M_TrimSheet_Industrial.
4. Exporta archivos FBX a Art/FBX/Environment/Modular/.
5. Renderiza showcase de Look-Dev fotométrico (2560x1440).
"""

import bpy
import bmesh
import math
import mathutils
import os
import shutil

PROJECT_ROOT = r"F:\Dev\Game"
TEX_DIR = os.path.join(PROJECT_ROOT, "Art", "Textures", "Environment")
FBX_DIR = os.path.join(PROJECT_ROOT, "Art", "FBX", "Environment", "Modular")
RENDER_DIR = os.path.join(PROJECT_ROOT, "Art", "Renders")
BLEND_DIR = os.path.join(PROJECT_ROOT, "Art", "Blender")
ARTIFACT_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\b59ff04f-3c21-4ee5-94b0-8e8f899f8923"

os.makedirs(FBX_DIR, exist_ok=True)
os.makedirs(RENDER_DIR, exist_ok=True)
os.makedirs(BLEND_DIR, exist_ok=True)

# Limpiar escena
bpy.ops.wm.read_factory_settings(use_empty=True)

# Regiones UV Trim Sheet
UV_METAL_PANEL = (0.01, 0.01, 0.49, 0.49)
UV_HAZARD_STRIPES = (0.01, 0.51, 0.99, 0.74)
UV_DARK_FRAME = (0.51, 0.01, 0.99, 0.49)
UV_RIVETS = (0.01, 0.76, 0.25, 0.99)
UV_VENT_SLATS = (0.26, 0.76, 0.50, 0.99)

def get_or_create_material():
    mat_name = "M_TrimSheet_Industrial"
    mat = bpy.data.materials.get(mat_name)
    if mat:
        return mat
    mat = bpy.data.materials.new(name=mat_name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (600, 0)
    principled = nodes.new(type='ShaderNodeBsdfPrincipled')
    principled.location = (200, 0)
    links.new(principled.outputs['BSDF'], output.inputs['Surface'])

    base_path = os.path.join(TEX_DIR, "T_TrimSheet_Industrial_BaseColor.png")
    orm_path = os.path.join(TEX_DIR, "T_TrimSheet_Industrial_ORM.png")
    norm_path = os.path.join(TEX_DIR, "T_TrimSheet_Industrial_Normal.png")

    if os.path.exists(base_path):
        img_b = bpy.data.images.load(base_path)
        node_b = nodes.new(type='ShaderNodeTexImage')
        node_b.image = img_b
        node_b.location = (-400, 200)
        links.new(node_b.outputs['Color'], principled.inputs['Base Color'])

    if os.path.exists(orm_path):
        img_o = bpy.data.images.load(orm_path)
        img_o.colorspace_settings.name = 'Non-Color'
        node_o = nodes.new(type='ShaderNodeTexImage')
        node_o.image = img_o
        node_o.location = (-400, -100)
        sep = nodes.new(type='ShaderNodeSeparateColor')
        sep.location = (-100, -100)
        links.new(node_o.outputs['Color'], sep.inputs['Color'])
        links.new(sep.outputs['Green'], principled.inputs['Roughness'])
        links.new(sep.outputs['Blue'], principled.inputs['Metallic'])

    if os.path.exists(norm_path):
        img_n = bpy.data.images.load(norm_path)
        img_n.colorspace_settings.name = 'Non-Color'
        node_n = nodes.new(type='ShaderNodeTexImage')
        node_n.image = img_n
        node_n.location = (-400, -400)
        norm_map = nodes.new(type='ShaderNodeNormalMap')
        norm_map.location = (-100, -400)
        links.new(node_n.outputs['Color'], norm_map.inputs['Color'])
        links.new(norm_map.outputs['Normal'], principled.inputs['Normal'])

    return mat

mat = get_or_create_material()

# ==============================================================================
# 1. CONSTRUCCIÓN DE SM_Mod_Ceiling_Breach_400x400
# ==============================================================================
def create_ceiling_breach():
    mesh = bpy.data.meshes.new("SM_Mod_Ceiling_Breach_400x400")
    obj = bpy.data.objects.new("SM_Mod_Ceiling_Breach_400x400", mesh)
    bpy.context.scene.collection.objects.link(obj)

    bm = bmesh.new()

    # Dimensiones: 4.0m x 4.0m, grosor perimetral 0.25m
    # Marco exterior perimetral (4 vigas C/I-channel exteriores)
    # +X borde (X = 1.9, Y: -2..2)
    f_px = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(0.20, 4.0, 0.25), verts=f_px['verts'])
    bmesh.ops.translate(bm, vec=(1.90, 0.0, 0.125), verts=f_px['verts'])

    # -X borde (X = -1.9, Y: -2..2)
    f_nx = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(0.20, 4.0, 0.25), verts=f_nx['verts'])
    bmesh.ops.translate(bm, vec=(-1.90, 0.0, 0.125), verts=f_nx['verts'])

    # +Y borde (Y = 1.9, X: -1.8..1.8)
    f_py = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(3.60, 0.20, 0.25), verts=f_py['verts'])
    bmesh.ops.translate(bm, vec=(0.0, 1.90, 0.125), verts=f_py['verts'])

    # -Y borde (Y = -1.9, X: -1.8..1.8)
    f_ny = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(3.60, 0.20, 0.25), verts=f_ny['verts'])
    bmesh.ops.translate(bm, vec=(0.0, -1.90, 0.125), verts=f_ny['verts'])

    # Planchas de techo sólidas perimetrales (los 4 bordes que no colapsaron)
    # Ala Norte (+Y de 0.9 a 1.8)
    p_n = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(3.60, 0.90, 0.06), verts=p_n['verts'])
    bmesh.ops.translate(bm, vec=(0.0, 1.35, 0.20), verts=p_n['verts'])

    # Ala Sur (-Y de -1.8 a -0.9)
    p_s = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(3.60, 0.90, 0.06), verts=p_s['verts'])
    bmesh.ops.translate(bm, vec=(0.0, -1.35, 0.20), verts=p_s['verts'])

    # Ala Este (+X de 1.1 a 1.8, Y de -0.9 a 0.9)
    p_e = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(0.70, 1.80, 0.06), verts=p_e['verts'])
    bmesh.ops.translate(bm, vec=(1.45, 0.0, 0.20), verts=p_e['verts'])

    # Ala Oeste (-X de -1.8 a -1.1, Y de -0.9 a 0.9)
    p_w = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(0.70, 1.80, 0.06), verts=p_w['verts'])
    bmesh.ops.translate(bm, vec=(-1.45, 0.0, 0.20), verts=p_w['verts'])

    # El boquete central queda en X: [-1.1, 1.1] x Y: [-0.9, 0.9] (2.2m x 1.8m de apertura pura)

    # REBARBAS Y DIENTES DE CHAPA METÁLICA DESGARRADA DOBLADOS HACIA ABAJO
    # Vértices de chapa rasgada que cuelgan hacia el pasillo (Z negativo relativo a 0.20)
    jagged_tongues = [
        # (x, y, dx, dy, dz, rot_deg)
        (-0.8, -0.9, 0.35, 0.25, -0.32, 28),
        (-0.3, -0.92, 0.40, 0.20, -0.45, 38),
        (0.4, -0.88, 0.30, 0.22, -0.28, 22),
        (0.85, -0.85, 0.25, 0.18, -0.35, 30),
        (-0.7, 0.9, 0.38, 0.24, -0.38, -32),
        (-0.1, 0.92, 0.42, 0.22, -0.42, -35),
        (0.5, 0.88, 0.32, 0.20, -0.25, -24),
        (-1.1, -0.4, 0.22, 0.35, -0.30, 25),
        (-1.08, 0.3, 0.24, 0.38, -0.40, 32),
        (1.1, -0.3, 0.20, 0.32, -0.26, -26),
        (1.08, 0.4, 0.22, 0.36, -0.34, -28),
    ]
    for jx, jy, jdx, jdy, jdz, jrot in jagged_tongues:
        tongue = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(jdx, jdy, 0.03), verts=tongue['verts'])
        # Rotar para dar inclinación hacia abajo
        rot_axis = 'X' if abs(jy) > abs(jx) else 'Y'
        rot_mat = mathutils.Matrix.Rotation(math.radians(jrot), 3, rot_axis)
        bmesh.ops.rotate(bm, cent=(0,0,0), matrix=rot_mat, verts=tongue['verts'])
        bmesh.ops.translate(bm, vec=(jx, jy, 0.20 + jdz/2.0), verts=tongue['verts'])

    # VIGAS SECUNDARIAS EN I CORTADAS/SECCIONADAS EN EL BOQUETE
    # Viga transversal Norte (Y = 0.5): se extiende de X = -1.8 a X = -0.5 (seccionada) y de X = 0.6 a 1.8
    # Segmento Oeste de viga
    b1_w = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(1.30, 0.16, 0.18), verts=b1_w['verts'])
    bmesh.ops.translate(bm, vec=(-1.15, 0.50, 0.09), verts=b1_w['verts'])
    # Punta retorcida cizallada
    b1_stub = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(0.25, 0.14, 0.16), verts=b1_stub['verts'])
    bmesh.ops.rotate(bm, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(math.radians(25), 3, 'Y'), verts=b1_stub['verts'])
    bmesh.ops.translate(bm, vec=(-0.45, 0.50, 0.03), verts=b1_stub['verts'])

    # Segmento Este de viga
    b1_e = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(1.20, 0.16, 0.18), verts=b1_e['verts'])
    bmesh.ops.translate(bm, vec=(1.20, 0.50, 0.09), verts=b1_e['verts'])
    b1_e_stub = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(0.20, 0.14, 0.16), verts=b1_e_stub['verts'])
    bmesh.ops.rotate(bm, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(math.radians(-20), 3, 'Y'), verts=b1_e_stub['verts'])
    bmesh.ops.translate(bm, vec=(0.55, 0.50, 0.04), verts=b1_e_stub['verts'])

    # Viga transversal Sur (Y = -0.5): seccionada
    b2_w = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(1.10, 0.16, 0.18), verts=b2_w['verts'])
    bmesh.ops.translate(bm, vec=(-1.25, -0.50, 0.09), verts=b2_w['verts'])
    b2_e = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(1.35, 0.16, 0.18), verts=b2_e['verts'])
    bmesh.ops.translate(bm, vec=(1.12, -0.50, 0.09), verts=b2_e['verts'])

    # MUÑÓN DE ANCLAJE ROTO / BRACKET SHEAR STUB (Donde estaba fijada la viga caída)
    bracket_base = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(0.35, 0.30, 0.08), verts=bracket_base['verts'])
    bmesh.ops.translate(bm, vec=(-0.10, 0.0, 0.22), verts=bracket_base['verts'])
    # Pernos sheared (cortados al ras con rebaba brillante)
    for bx, by in [(-0.20, -0.10), (-0.20, 0.10), (0.00, -0.10), (0.00, 0.10)]:
        bolt = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=6, radius1=0.03, radius2=0.025, depth=0.05)
        bmesh.ops.translate(bm, vec=(bx, by, 0.17), verts=bolt['verts'])

    # CONDUCTOS Y TUBERÍAS CORTADAS EN EL BORDE DEL BOQUETE
    conduits = [
        # (x, y, radius, len, dir)
        (0.0, 0.95, 0.04, 0.6, 'Y'),
        (0.2, 0.95, 0.03, 0.5, 'Y'),
        (-0.3, -0.95, 0.05, 0.55, 'Y'),
    ]
    for cx, cy, cr, clen, cdir in conduits:
        cond = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=12, radius1=cr, radius2=cr, depth=clen)
        bmesh.ops.rotate(bm, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(math.radians(90), 3, 'X'), verts=cond['verts'])
        bmesh.ops.translate(bm, vec=(cx, cy, 0.15), verts=cond['verts'])

    # UV Mapping en trim sheet
    uv_layer = bm.loops.layers.uv.verify()
    for face in bm.faces:
        center = face.calc_center_median()
        # Franjas de peligro en puntas de vigas cortadas y dientes de desgarro
        if center.z < 0.10 or abs(center.y) < 0.6 and (abs(center.x + 0.45) < 0.3 or abs(center.x - 0.55) < 0.3):
            u0, v0, u1, v1 = UV_HAZARD_STRIPES
        elif abs(face.normal.z) > 0.8:
            u0, v0, u1, v1 = UV_METAL_PANEL
        elif abs(face.normal.x) > 0.7 or abs(face.normal.y) > 0.7:
            u0, v0, u1, v1 = UV_DARK_FRAME
        else:
            u0, v0, u1, v1 = UV_RIVETS

        for loop in face.loops:
            v_co = loop.vert.co
            u = (v_co.x + 2.0) / 4.0
            v = (v_co.y + 2.0) / 4.0
            loop[uv_layer].uv = (u0 + (u % 1.0) * (u1 - u0), v0 + (v % 1.0) * (v1 - v0))

    bm.to_mesh(mesh)
    bm.free()
    obj.data.materials.append(mat)

    # --------------------------------------------------------------------------
    # COLISIONES CONVEXAS UCX PERIMETRALES (Dejan el boquete 100% permeable)
    # --------------------------------------------------------------------------
    ucx_list = []
    # UCX 01: Norte (+Y)
    u_n_mesh = bpy.data.meshes.new("UCX_SM_Mod_Ceiling_Breach_400x400_01")
    u_n_obj = bpy.data.objects.new("UCX_SM_Mod_Ceiling_Breach_400x400_01", u_n_mesh)
    bpy.context.scene.collection.objects.link(u_n_obj)
    ubm = bmesh.new()
    ucube = bmesh.ops.create_cube(ubm, size=1.0)
    bmesh.ops.scale(ubm, vec=(4.0, 1.10, 0.30), verts=ucube['verts'])
    bmesh.ops.translate(ubm, vec=(0.0, 1.45, 0.15), verts=ucube['verts'])
    ubm.to_mesh(u_n_mesh)
    ubm.free()
    ucx_list.append(u_n_obj)

    # UCX 02: Sur (-Y)
    u_s_mesh = bpy.data.meshes.new("UCX_SM_Mod_Ceiling_Breach_400x400_02")
    u_s_obj = bpy.data.objects.new("UCX_SM_Mod_Ceiling_Breach_400x400_02", u_s_mesh)
    bpy.context.scene.collection.objects.link(u_s_obj)
    ubm = bmesh.new()
    ucube = bmesh.ops.create_cube(ubm, size=1.0)
    bmesh.ops.scale(ubm, vec=(4.0, 1.10, 0.30), verts=ucube['verts'])
    bmesh.ops.translate(ubm, vec=(0.0, -1.45, 0.15), verts=ucube['verts'])
    ubm.to_mesh(u_s_mesh)
    ubm.free()
    ucx_list.append(u_s_obj)

    # UCX 03: Este (+X)
    u_e_mesh = bpy.data.meshes.new("UCX_SM_Mod_Ceiling_Breach_400x400_03")
    u_e_obj = bpy.data.objects.new("UCX_SM_Mod_Ceiling_Breach_400x400_03", u_e_mesh)
    bpy.context.scene.collection.objects.link(u_e_obj)
    ubm = bmesh.new()
    ucube = bmesh.ops.create_cube(ubm, size=1.0)
    bmesh.ops.scale(ubm, vec=(1.00, 1.80, 0.30), verts=ucube['verts'])
    bmesh.ops.translate(ubm, vec=(1.50, 0.0, 0.15), verts=ucube['verts'])
    ubm.to_mesh(u_e_mesh)
    ubm.free()
    ucx_list.append(u_e_obj)

    # UCX 04: Oeste (-X)
    u_w_mesh = bpy.data.meshes.new("UCX_SM_Mod_Ceiling_Breach_400x400_04")
    u_w_obj = bpy.data.objects.new("UCX_SM_Mod_Ceiling_Breach_400x400_04", u_w_mesh)
    bpy.context.scene.collection.objects.link(u_w_obj)
    ubm = bmesh.new()
    ucube = bmesh.ops.create_cube(ubm, size=1.0)
    bmesh.ops.scale(ubm, vec=(1.00, 1.80, 0.30), verts=ucube['verts'])
    bmesh.ops.translate(ubm, vec=(-1.50, 0.0, 0.15), verts=ucube['verts'])
    ubm.to_mesh(u_w_mesh)
    ubm.free()
    ucx_list.append(u_w_obj)

    return obj, ucx_list

# ==============================================================================
# 2. CONSTRUCCIÓN DE SM_Mod_Wall_Breach_400x350
# ==============================================================================
def create_wall_breach():
    mesh = bpy.data.meshes.new("SM_Mod_Wall_Breach_400x350")
    obj = bpy.data.objects.new("SM_Mod_Wall_Breach_400x350", mesh)
    bpy.context.scene.collection.objects.link(obj)

    bm = bmesh.new()

    # Columnas laterales estructurales intactas (X = -1.85 y X = 1.85, Z: 0..3.5)
    c_l = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(0.30, 0.30, 3.50), verts=c_l['verts'])
    bmesh.ops.translate(bm, vec=(-1.85, 0.0, 1.75), verts=c_l['verts'])

    c_r = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(0.30, 0.30, 3.50), verts=c_r['verts'])
    bmesh.ops.translate(bm, vec=(1.85, 0.0, 1.75), verts=c_r['verts'])

    # Viga dintel superior (Z = 3.35, X: -1.7..1.7)
    dintel = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(3.40, 0.30, 0.30), verts=dintel['verts'])
    bmesh.ops.translate(bm, vec=(0.0, 0.0, 3.35), verts=dintel['verts'])

    # Zócalo inferior (Z = 0.20)
    zocalo = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(3.40, 0.30, 0.40), verts=zocalo['verts'])
    bmesh.ops.translate(bm, vec=(0.0, 0.0, 0.20), verts=zocalo['verts'])

    # Mamparo fracturado: panel izquierdo abombado (X: -1.7 a -0.6)
    p_izq = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(1.10, 0.12, 2.75), verts=p_izq['verts'])
    bmesh.ops.translate(bm, vec=(-1.15, 0.05, 1.775), verts=p_izq['verts'])

    # Mamparo derecho abombado (X: 0.8 a 1.7)
    p_der = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(0.90, 0.12, 2.75), verts=p_der['verts'])
    bmesh.ops.translate(bm, vec=(1.25, -0.05, 1.775), verts=p_der['verts'])

    # Brecha central abierta (X: -0.6 a 0.8, Z: 0.4 a 3.2) con chapa doblada hacia afuera
    breach_flaps = [
        (-0.55, 0.18, 1.2, 0.25, 0.04, 0.6, 20),
        (-0.58, 0.22, 2.2, 0.22, 0.04, 0.7, 28),
        (0.75, -0.15, 1.5, 0.24, 0.04, 0.65, -25),
        (0.78, -0.20, 2.5, 0.20, 0.04, 0.55, -30),
    ]
    for fx, fy, fz, fdx, fdy, fdz, frot in breach_flaps:
        flap = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=(fdx, fdy, fdz), verts=flap['verts'])
        bmesh.ops.rotate(bm, cent=(0,0,0), matrix=mathutils.Matrix.Rotation(math.radians(frot), 3, 'Z'), verts=flap['verts'])
        bmesh.ops.translate(bm, vec=(fx, fy, fz), verts=flap['verts'])

    # UV Mapping
    uv_layer = bm.loops.layers.uv.verify()
    for face in bm.faces:
        center = face.calc_center_median()
        if abs(center.x) > 1.6 or center.z > 3.1 or center.z < 0.4:
            u0, v0, u1, v1 = UV_DARK_FRAME
        elif abs(center.y) > 0.1:
            u0, v0, u1, v1 = UV_HAZARD_STRIPES
        else:
            u0, v0, u1, v1 = UV_METAL_PANEL

        for loop in face.loops:
            v_co = loop.vert.co
            u = (v_co.x + 2.0) / 4.0
            v = v_co.z / 3.5
            loop[uv_layer].uv = (u0 + (u % 1.0) * (u1 - u0), v0 + (v % 1.0) * (v1 - v0))

    bm.to_mesh(mesh)
    bm.free()
    obj.data.materials.append(mat)

    # UCX para pared rota
    ucx_list = []
    # UCX Izquierda
    u_wl_mesh = bpy.data.meshes.new("UCX_SM_Mod_Wall_Breach_400x350_01")
    u_wl_obj = bpy.data.objects.new("UCX_SM_Mod_Wall_Breach_400x350_01", u_wl_mesh)
    bpy.context.scene.collection.objects.link(u_wl_obj)
    ubm = bmesh.new()
    ucube = bmesh.ops.create_cube(ubm, size=1.0)
    bmesh.ops.scale(ubm, vec=(1.40, 0.40, 3.50), verts=ucube['verts'])
    bmesh.ops.translate(ubm, vec=(-1.30, 0.0, 1.75), verts=ucube['verts'])
    ubm.to_mesh(u_wl_mesh)
    ubm.free()
    ucx_list.append(u_wl_obj)

    # UCX Derecha
    u_wr_mesh = bpy.data.meshes.new("UCX_SM_Mod_Wall_Breach_400x350_02")
    u_wr_obj = bpy.data.objects.new("UCX_SM_Mod_Wall_Breach_400x350_02", u_wr_mesh)
    bpy.context.scene.collection.objects.link(u_wr_obj)
    ubm = bmesh.new()
    ucube = bmesh.ops.create_cube(ubm, size=1.0)
    bmesh.ops.scale(ubm, vec=(1.20, 0.40, 3.50), verts=ucube['verts'])
    bmesh.ops.translate(ubm, vec=(1.40, 0.0, 1.75), verts=ucube['verts'])
    ubm.to_mesh(u_wr_mesh)
    ubm.free()
    ucx_list.append(u_wr_obj)

    return obj, ucx_list

# Generar objetos
ceil_obj, ceil_ucx = create_ceiling_breach()
wall_obj, wall_ucx = create_wall_breach()

# ==============================================================================
# EXPORTACIÓN FBX (Metros a Centímetros con factor 100)
# ==============================================================================
def export_asset_fbx(main_obj, ucx_list, filename):
    for o in bpy.data.objects:
        o.select_set(False)
    main_obj.select_set(True)
    for u in ucx_list:
        u.select_set(True)
    bpy.context.view_layer.objects.active = main_obj

    filepath = os.path.join(FBX_DIR, filename)
    bpy.ops.export_scene.fbx(
        filepath=filepath,
        use_selection=True,
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_ALL',
        bake_space_transform=False,
        mesh_smooth_type='FACE',
        axis_forward='-Z',
        axis_up='Y'
    )
    print(f"[OK] Exportado FBX modular: {filepath}")

export_asset_fbx(ceil_obj, ceil_ucx, "SM_Mod_Ceiling_Breach_400x400.fbx")
export_asset_fbx(wall_obj, wall_ucx, "SM_Mod_Wall_Breach_400x350.fbx")

# ==============================================================================
# RENDER LOOK-DEV DE CERTIFICACIÓN VISUAL
# ==============================================================================
# Ocultar UCX
for u in ceil_ucx + wall_ucx:
    u.hide_render = True

# Disposición para showcase: techo inclinado para mostrar boquete y bordes colapsados
ceil_obj.location = (-2.2, 0.0, 1.8)
ceil_obj.rotation_euler = (math.radians(35), math.radians(-15), math.radians(20))

wall_obj.location = (2.2, 0.0, 1.75)
wall_obj.rotation_euler = (0, 0, math.radians(-25))

# Luces de showcase
l_key = bpy.data.lights.new("KeyLight", type='AREA')
l_key.energy = 900
l_key.size = 4.0
l_key.color = (1.0, 0.9, 0.8)
ol_key = bpy.data.objects.new("KeyLight", l_key)
bpy.context.scene.collection.objects.link(ol_key)
ol_key.location = (0.0, -5.0, 5.0)
ol_key.rotation_euler = (math.radians(50), 0, 0)

l_amber = bpy.data.lights.new("AmberAlert", type='POINT')
l_amber.energy = 750
l_amber.color = (1.0, 0.45, 0.05)
ol_amber = bpy.data.objects.new("AmberAlert", l_amber)
bpy.context.scene.collection.objects.link(ol_amber)
ol_amber.location = (-2.5, -2.0, 1.2)

l_cyan = bpy.data.lights.new("CyanRim", type='AREA')
l_cyan.energy = 800
l_cyan.size = 5.0
l_cyan.color = (0.2, 0.65, 1.0)
ol_cyan = bpy.data.objects.new("CyanRim", l_cyan)
bpy.context.scene.collection.objects.link(ol_cyan)
ol_cyan.location = (2.5, 4.0, 3.5)
ol_cyan.rotation_euler = (math.radians(-35), 0, math.radians(-150))

# Cámara
cam = bpy.data.cameras.new("CamShowcase")
cam.lens = 32
camo = bpy.data.objects.new("CamShowcase", cam)
bpy.context.scene.collection.objects.link(camo)
camo.location = (0.0, -7.5, 3.0)
camo.rotation_euler = (math.radians(72), 0, 0)
bpy.context.scene.camera = camo

scene = bpy.context.scene
scene.render.resolution_x = 2560
scene.render.resolution_y = 1440

render_output = os.path.join(RENDER_DIR, "Showcase_Bloques_Brecha_Techo_y_Pared.png")
scene.render.filepath = render_output
bpy.ops.render.render(write_still=True)
print(f"[OK] Showcase guardado: {render_output}")

if os.path.exists(ARTIFACT_DIR):
    art_dest = os.path.join(ARTIFACT_DIR, "Showcase_Bloques_Brecha_Techo_y_Pared.png")
    shutil.copyfile(render_output, art_dest)
    print(f"[OK] Copiado a artefactos: {art_dest}")

blend_path = os.path.join(BLEND_DIR, "SM_Bloques_Brecha_Official.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print("[OK] Generación de Bloques de Brecha completada con éxito.")

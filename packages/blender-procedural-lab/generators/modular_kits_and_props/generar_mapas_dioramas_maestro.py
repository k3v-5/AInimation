# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Generador Maestro Oficial de Mapas y Dioramas 3D - Astra Hazard
# Fiel 1:1 a media_1791198833604.jpg:
# 1. Carguero Químico (Buque espacial oxidado, tanque abierto con ácido verde, grúa y puente de mando)
# 2. Crucero de Lujo 'Celestia' (Salón Art Déco, gran ventanal en arco con Saturno, moqueta borgoña y escalera)
# 3. Refinería de Plasma Tokamak (Reactor toroidal de plasma cian, pasarela curvada, compuerta y asteroides)
# Blender 5.2 LTS - Tríptico Maestro Oficial (2560x1440)

import bpy
import bmesh
import math
import os
import shutil
from mathutils import Vector, Euler
from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = r"F:\Dev\Game"
RENDERS_DIR = os.path.join(PROJECT_ROOT, "Art", "Renders")
TEXTURES_DIR = os.path.join(PROJECT_ROOT, "Art", "Textures", "Maps")
ARTIFACT_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\b59ff04f-3c21-4ee5-94b0-8e8f899f8923"

os.makedirs(RENDERS_DIR, exist_ok=True)
os.makedirs(TEXTURES_DIR, exist_ok=True)
os.makedirs(ARTIFACT_DIR, exist_ok=True)

R = math.radians

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if not bpy.data.scenes:
        bpy.data.scenes.new("Scene")
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 800
    scene.render.resolution_y = 1200
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'High Contrast'
    return scene

def get_system_font(size, bold=False):
    font_paths = [
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\seguiemb.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\consola.ttf"
    ]
    for p in font_paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

# ==============================================================================
# GENERACIÓN DE TEXTURAS PBR Y GRÁFICOS PROCEDURALES
# ==============================================================================
def generate_map_textures():
    # 1. Textura Casco Carguero con Óxido, Remaches y Rótulos 'QUÍMICO MORTAL' y 'ACIDGOO'
    tex_cargo_path = os.path.join(TEXTURES_DIR, "tex_cargo_hull.png")
    img_cargo = Image.new("RGBA", (1024, 1024), (105, 75, 55, 255))
    draw_c = ImageDraw.Draw(img_cargo)
    for y in range(0, 1024, 128):
        draw_c.line([(0, y), (1024, y)], fill=(55, 38, 28, 255), width=5)
        for x in range(0, 1024, 32):
            draw_c.ellipse([(x+4, y+6), (x+9, y+11)], fill=(145, 120, 95, 255))
            draw_c.ellipse([(x+5, y+7), (x+8, y+10)], fill=(45, 30, 20, 255))
    for ox in [140, 360, 600, 820]:
        draw_c.polygon([(ox, 128), (ox+30, 128), (ox+45, 520), (ox-15, 520)], fill=(135, 58, 22, 210))
    font_stencil = get_system_font(52, bold=True)
    draw_c.text((100, 260), "QUÍMICO MORTAL", fill=(225, 185, 45, 240), font=font_stencil)
    draw_c.text((620, 260), "ACIDGOO", fill=(65, 215, 55, 240), font=font_stencil)
    img_cargo.save(tex_cargo_path)

    # 2. Textura Bandas Atmosféricas Saturno
    tex_saturn_path = os.path.join(TEXTURES_DIR, "tex_saturn_bands.png")
    img_saturn = Image.new("RGB", (1024, 512), (218, 202, 168))
    draw_sat = ImageDraw.Draw(img_saturn)
    palette = [
        (205, 185, 150), (235, 218, 185), (190, 165, 130), (242, 228, 198),
        (175, 148, 118), (225, 200, 160), (155, 128, 100), (210, 190, 158)
    ]
    for y in range(512):
        col = palette[(y // 16) % len(palette)]
        var = int(14 * math.sin(y * 0.12))
        col_adj = (max(0, min(255, col[0] + var)), max(0, min(255, col[1] + var)), max(0, min(255, col[2] + var)))
        draw_sat.line([(0, y), (1024, y)], fill=col_adj)
    img_saturn.save(tex_saturn_path)

    # 3. Textura Moqueta Art Déco Vino Tinto con Patrones Geométricos Dorados
    tex_carpet_path = os.path.join(TEXTURES_DIR, "tex_artdeco_carpet.png")
    img_carpet = Image.new("RGB", (1024, 1024), (72, 14, 28))
    draw_carp = ImageDraw.Draw(img_carpet)
    gold = (225, 180, 65)
    for margin in [35, 60, 95]:
        draw_carp.rectangle([(margin, margin), (1024 - margin, 1024 - margin)], outline=gold, width=4)
    draw_carp.polygon([(512, 180), (844, 512), (512, 844), (180, 512)], outline=gold, width=5)
    draw_carp.polygon([(512, 240), (784, 512), (512, 784), (240, 512)], outline=gold, width=3)
    for corner in [(140, 140), (884, 140), (140, 884), (884, 884)]:
        cx, cy = corner
        draw_carp.rectangle([(cx-40, cy-40), (cx+40, cy+40)], outline=gold, width=3)
    img_carpet.save(tex_carpet_path)

    # 4. Textura Pared Madera Caoba Art Déco
    tex_wood_path = os.path.join(TEXTURES_DIR, "tex_artdeco_wood.png")
    img_wood = Image.new("RGB", (1024, 1024), (52, 24, 18))
    draw_w = ImageDraw.Draw(img_wood)
    for p_x in [160, 512, 864]:
        draw_w.rectangle([(p_x - 130, 80), (p_x + 130, 940)], outline=(28, 14, 10), width=8)
        draw_w.rectangle([(p_x - 120, 90), (p_x + 120, 930)], outline=gold, width=4)
        draw_w.polygon([(p_x, 300), (p_x + 80, 512), (p_x, 724), (p_x - 80, 512)], outline=gold, width=4)
    img_wood.save(tex_wood_path)

    # 5. Señalética de la Refinería de Plasma
    tex_ref_sign_path = os.path.join(TEXTURES_DIR, "tex_refineria_sign.png")
    img_sign = Image.new("RGB", (512, 256), (235, 180, 25))
    draw_s = ImageDraw.Draw(img_sign)
    draw_s.rectangle([(8, 8), (504, 248)], outline=(20, 20, 20), width=8)
    font_sign = get_system_font(38, bold=True)
    draw_s.text((35, 95), "REFINERÍA\nDE PLASMA", fill=(20, 20, 20), font=font_sign)
    img_sign.save(tex_ref_sign_path)

    # 6. Señal Peligro Alta Energía
    tex_danger_path = os.path.join(TEXTURES_DIR, "tex_danger_energy.png")
    img_dang = Image.new("RGB", (512, 256), (235, 180, 25))
    draw_d = ImageDraw.Draw(img_dang)
    draw_d.rectangle([(8, 8), (504, 248)], outline=(20, 20, 20), width=8)
    font_dang = get_system_font(32, bold=True)
    draw_d.text((45, 85), "PELIGRO:\nALTA ENERGÍA", fill=(20, 20, 20), font=font_dang)
    img_dang.save(tex_danger_path)

    return {
        "cargo": tex_cargo_path,
        "saturn": tex_saturn_path,
        "carpet": tex_carpet_path,
        "wood": tex_wood_path,
        "sign_ref": tex_ref_sign_path,
        "sign_dang": tex_danger_path
    }

# ==============================================================================
# SISTEMA DE CONTORNO CÓMIC PROFESIONAL (INVERTED HULL INK OUTLINES BLENDER 5.2)
# ==============================================================================
M_INK_OUTLINE = None

def init_outline_material():
    global M_INK_OUTLINE
    mat = bpy.data.materials.get("M_Ink_Outline_Map")
    if not mat:
        mat = bpy.data.materials.new(name="M_Ink_Outline_Map")
    mat.use_nodes = True
    mat.surface_render_method = 'BLENDED'
    nodes = mat.node_tree.nodes
    nodes.clear()

    out_node = nodes.new(type='ShaderNodeOutputMaterial')
    mix_node = nodes.new(type='ShaderNodeMixShader')
    trans_node = nodes.new(type='ShaderNodeBsdfTransparent')
    emit_node = nodes.new(type='ShaderNodeEmission')
    emit_node.inputs['Color'].default_value = (0.05, 0.04, 0.04, 1.0)
    emit_node.inputs['Strength'].default_value = 1.0
    geom_node = nodes.new(type='ShaderNodeNewGeometry')

    mat.node_tree.links.new(geom_node.outputs['Backfacing'], mix_node.inputs['Fac'])
    mat.node_tree.links.new(emit_node.outputs['Emission'], mix_node.inputs[1])
    mat.node_tree.links.new(trans_node.outputs['BSDF'], mix_node.inputs[2])
    mat.node_tree.links.new(mix_node.outputs['Shader'], out_node.inputs['Surface'])

    M_INK_OUTLINE = mat
    return mat

def apply_comic_styling(obj, smooth=True, bevel=True, bevel_width=0.02, outline=True, outline_thickness=0.012):
    if not obj or obj.type != 'MESH':
        return
    if smooth:
        for p in obj.data.polygons:
            p.use_smooth = True
    if bevel:
        bev = obj.modifiers.new(name="Bevel", type='BEVEL')
        bev.width = bevel_width
        bev.segments = 2
        bev.limit_method = 'ANGLE'
        bev.angle_limit = R(35)
        bev.harden_normals = True
    if outline and M_INK_OUTLINE:
        if M_INK_OUTLINE not in list(obj.data.materials):
            obj.data.materials.append(M_INK_OUTLINE)
        mat_idx = list(obj.data.materials).index(M_INK_OUTLINE)
        mod = obj.modifiers.new(name="Ink_Outline", type='SOLIDIFY')
        mod.thickness = outline_thickness
        mod.offset = 1.0
        mod.material_offset = mat_idx
        mod.material_offset_rim = mat_idx
        mod.use_flip_normals = True

def make_color_material(name, col_rgba, rough=0.5, met=0.0, emit_str=0.0, emit_col=None):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()

    out_node = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = col_rgba
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Metallic'].default_value = met

    if emit_str > 0.0:
        ec = emit_col if emit_col else col_rgba
        if 'Emission Color' in bsdf.inputs:
            bsdf.inputs['Emission Color'].default_value = ec
            bsdf.inputs['Emission Strength'].default_value = emit_str
        elif 'Emission' in bsdf.inputs:
            bsdf.inputs['Emission'].default_value = ec
            if 'Emission Strength' in bsdf.inputs:
                bsdf.inputs['Emission Strength'].default_value = emit_str

    mat.node_tree.links.new(bsdf.outputs['BSDF'], out_node.inputs['Surface'])
    return mat

def make_image_material(name, img_path, rough=0.5, met=0.0, emit_str=0.0):
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()

    out_node = nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Metallic'].default_value = met

    tex_node = nodes.new(type='ShaderNodeTexImage')
    if os.path.exists(img_path):
        tex_node.image = bpy.data.images.load(img_path, check_existing=True)

    mat.node_tree.links.new(tex_node.outputs['Color'], bsdf.inputs['Base Color'])
    if emit_str > 0.0:
        if 'Emission Color' in bsdf.inputs:
            mat.node_tree.links.new(tex_node.outputs['Color'], bsdf.inputs['Emission Color'])
            bsdf.inputs['Emission Strength'].default_value = emit_str

    mat.node_tree.links.new(bsdf.outputs['BSDF'], out_node.inputs['Surface'])
    return mat

# ==============================================================================
# WORLD BACKGROUND & ILUMINACIÓN CÓSMICA PROFESIONAL
# ==============================================================================
def setup_starfield_world():
    world = bpy.context.scene.world or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    nodes.clear()

    out_node = nodes.new(type='ShaderNodeOutputWorld')
    bg_node = nodes.new(type='ShaderNodeBackground')
    bg_node.inputs['Color'].default_value = (0.02, 0.03, 0.06, 1.0)

    # Estrellas procedurales
    tcoord = nodes.new(type='ShaderNodeTexCoord')
    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 160.0
    noise.inputs['Detail'].default_value = 10.0
    world.node_tree.links.new(tcoord.outputs['Generated'], noise.inputs['Vector'])

    ramp = nodes.new(type='ShaderNodeValToRGB')
    ramp.color_ramp.interpolation = 'CONSTANT'
    ramp.color_ramp.elements[0].position = 0.84
    ramp.color_ramp.elements[0].color = (0, 0, 0, 1)
    ramp.color_ramp.elements[1].position = 0.86
    ramp.color_ramp.elements[1].color = (1.8, 1.8, 2.0, 1)
    world.node_tree.links.new(noise.outputs['Fac'], ramp.inputs['Fac'])

    wmix = nodes.new(type='ShaderNodeMix')
    wmix.data_type = 'RGBA'
    wmix.blend_type = 'ADD'
    wmix.inputs['Factor'].default_value = 1.0
    wmix.inputs[6].default_value = (0.03, 0.04, 0.08, 1.0)
    world.node_tree.links.new(ramp.outputs['Color'], wmix.inputs[7])
    world.node_tree.links.new(wmix.outputs[2], bg_node.inputs['Color'])
    world.node_tree.links.new(bg_node.outputs['Background'], out_node.inputs['Surface'])

# ==============================================================================
# DIORAMA 1: CARGUERO QUÍMICO (Fiel 1:1 a media_1791198833604.jpg)
# ==============================================================================
def build_carguero(origin, tex_dict):
    m_hull = make_image_material("M_Cargo_Hull", tex_dict["cargo"], rough=0.6, met=0.45)
    m_white_sup = make_color_material("M_WhiteSup", (0.88, 0.85, 0.78, 1.0), rough=0.55)
    m_win_glow = make_color_material("M_WinGlow", (1.0, 0.88, 0.25, 1.0), emit_str=4.0)
    m_funnel_red = make_color_material("M_FunnelRed", (0.88, 0.24, 0.14, 1.0), rough=0.45)
    m_dark = make_color_material("M_DarkMetal", (0.22, 0.22, 0.25, 1.0), rough=0.6, met=0.7)
    m_yellow = make_color_material("M_GantryYellow", (0.95, 0.74, 0.05, 1.0), rough=0.4)
    m_acid = make_color_material("M_AcidGoo", (0.15, 0.95, 0.15, 1.0), rough=0.15, emit_str=2.2)
    m_acid_glass = make_color_material("M_AcidGlass", (0.6, 1.0, 0.7, 0.3), rough=0.1)
    m_green_cargo = make_color_material("M_CargoGreen", (0.22, 0.52, 0.38, 1.0), rough=0.5)
    m_rock = make_color_material("M_SpaceRock", (0.35, 0.32, 0.30, 1.0), rough=0.85)

    # Iluminación de estudio frontal para el Carguero
    sun = bpy.data.lights.new("Sun_Carguero", 'SUN')
    sun.energy = 4.5
    sun.color = (1.0, 0.98, 0.92)
    s_obj = bpy.data.objects.new("Sun_Carguero_Obj", sun)
    s_obj.rotation_euler = (R(-40), R(25), 0)
    bpy.context.collection.objects.link(s_obj)

    fill = bpy.data.lights.new("Fill_Carguero", 'AREA')
    fill.energy = 350.0
    fill.size = 25.0
    fill.color = (0.75, 0.85, 1.0)
    f_obj = bpy.data.objects.new("Fill_Carguero_Obj", fill)
    f_obj.location = (origin.x - 1.0, origin.y - 18.0, origin.z + 8.0)
    f_obj.rotation_euler = (R(60), 0, 0)
    bpy.context.collection.objects.link(f_obj)

    # Luz puntual de ácid glow
    al = bpy.data.lights.new("AcidLight", 'POINT')
    al.energy = 180.0
    al.color = (0.1, 0.95, 0.15)
    alo = bpy.data.objects.new("AcidLight_Obj", al)
    alo.location = (origin.x + 0.4, origin.y - 0.6, origin.z + 0.6)
    bpy.context.collection.objects.link(alo)

    # 1. Casco principal del buque espacial oxidado
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(origin.x + 0.2, origin.y + 0.8, origin.z + 0.2))
    hull = bpy.context.active_object
    hull.scale = (11.5, 3.8, 3.6)
    hull.rotation_euler = (R(2), R(-6), R(-25))
    hull.data.materials.append(m_hull)
    apply_comic_styling(hull, bevel=True, bevel_width=0.04, outline=True)

    # Proa redondeada
    bpy.ops.mesh.primitive_cylinder_add(radius=1.9, depth=3.6, location=(origin.x - 4.8, origin.y + 3.2, origin.z + 1.0))
    bow = bpy.context.active_object
    bow.rotation_euler = (R(2), R(-6), R(-25))
    bow.data.materials.append(m_hull)
    apply_comic_styling(bow, bevel=True, bevel_width=0.04, outline=True)

    # 2. Superestructura del puente de mando en popa/arriba izquierda
    bridge_pos = (origin.x - 4.0, origin.y + 2.6, origin.z + 3.4)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=bridge_pos)
    bridge = bpy.context.active_object
    bridge.scale = (3.0, 3.2, 2.6)
    bridge.rotation_euler = (R(2), R(-6), R(-25))
    bridge.data.materials.append(m_white_sup)
    apply_comic_styling(bridge, bevel=True, bevel_width=0.03, outline=True)

    # Ventanales de la timonera iluminados en ámbar
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(bridge_pos[0] + 0.8, bridge_pos[1] - 0.7, bridge_pos[2] + 0.5))
    b_win = bpy.context.active_object
    b_win.scale = (0.1, 2.8, 0.6)
    b_win.rotation_euler = (R(2), R(-6), R(-25))
    b_win.data.materials.append(m_win_glow)

    # Chimenea náutica inclinada con franja negra
    bpy.ops.mesh.primitive_cylinder_add(radius=0.48, depth=2.4, location=(bridge_pos[0] - 0.8, bridge_pos[1] + 0.6, bridge_pos[2] + 1.8))
    funnel = bpy.context.active_object
    funnel.rotation_euler = (R(2), R(-18), R(-25))
    funnel.data.materials.append(m_funnel_red)
    apply_comic_styling(funnel, bevel=True, bevel_width=0.02, outline=True)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.50, depth=0.4, location=(bridge_pos[0] - 1.15, bridge_pos[1] + 0.7, bridge_pos[2] + 2.8))
    f_cap = bpy.context.active_object
    f_cap.rotation_euler = (R(2), R(-18), R(-25))
    f_cap.data.materials.append(m_dark)

    # Mástil de comunicaciones con crucetas
    bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=2.6, location=(bridge_pos[0] + 0.2, bridge_pos[1] + 0.1, bridge_pos[2] + 2.5))
    mast = bpy.context.active_object
    mast.data.materials.append(m_dark)
    for mz in [bridge_pos[2] + 2.2, bridge_pos[2] + 3.1]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(bridge_pos[0] + 0.2, bridge_pos[1] + 0.1, mz))
        yard = bpy.context.active_object
        yard.scale = (1.2, 0.05, 0.05)
        yard.rotation_euler = (0, 0, R(-25))
        yard.data.materials.append(m_dark)

    # 3. TANQUE DE ÁCIDO VISCOSO EN PRIMER PLANO (Corte frontal visible)
    tank_pos = (origin.x + 0.4, origin.y - 0.6, origin.z - 0.1)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(tank_pos[0], tank_pos[1] + 0.8, tank_pos[2]))
    t_back = bpy.context.active_object
    t_back.scale = (5.6, 0.3, 2.4)
    t_back.rotation_euler = (R(2), R(-6), R(-25))
    t_back.data.materials.append(m_hull)
    apply_comic_styling(t_back, bevel=True, bevel_width=0.03, outline=True)

    for px_side in [-2.4, 2.4]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(tank_pos[0] + px_side, tank_pos[1] + (0.2 if px_side > 0 else -0.2), tank_pos[2]))
        t_side = bpy.context.active_object
        t_side.scale = (0.3, 2.2, 2.4)
        t_side.rotation_euler = (R(2), R(-6), R(-25))
        t_side.data.materials.append(m_hull)
        apply_comic_styling(t_side, bevel=True, bevel_width=0.03, outline=True)

    # Ventana frontal de cristal
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(tank_pos[0], tank_pos[1] - 0.95, tank_pos[2]))
    t_glass = bpy.context.active_object
    t_glass.scale = (5.2, 0.08, 2.1)
    t_glass.rotation_euler = (R(2), R(-6), R(-25))
    t_glass.data.materials.append(m_acid_glass)
    apply_comic_styling(t_glass, bevel=True, bevel_width=0.01, outline=True)

    # Balsa de ácido verde brillante
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(tank_pos[0], tank_pos[1], tank_pos[2] - 0.2))
    acid = bpy.context.active_object
    acid.scale = (5.0, 1.9, 1.4)
    acid.rotation_euler = (R(2), R(-6), R(-25))
    acid.data.materials.append(m_acid)

    # Vapores tóxicos ondulantes
    for vx, vy, vz in [(-1.8, 0.1, 0.8), (-0.6, -0.1, 1.1), (0.7, 0.2, 0.9), (1.9, -0.2, 1.2)]:
        bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.25, depth=1.6, location=(tank_pos[0] + vx, tank_pos[1] + vy, tank_pos[2] + vz))
        vap = bpy.context.active_object
        vap.rotation_euler = (R(12), R(-6), R(-25))
        vap.data.materials.append(m_acid)

    # 4. PÓRTICO AMARILLO DE VIGAS DOBLES EN H
    for px, py in [(-1.8, 0.6), (0.2, -0.1), (2.1, -0.8)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.14, depth=3.2, location=(tank_pos[0] + px, tank_pos[1] + py - 0.5, tank_pos[2] + 1.8))
        pillar = bpy.context.active_object
        pillar.rotation_euler = (R(2), R(-6), R(-25))
        pillar.data.materials.append(m_yellow)
        apply_comic_styling(pillar, bevel=True, bevel_width=0.02, outline=True)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(tank_pos[0] + 0.15, tank_pos[1] - 0.2, tank_pos[2] + 3.2))
    g_beam = bpy.context.active_object
    g_beam.scale = (5.2, 0.35, 0.35)
    g_beam.rotation_euler = (R(2), R(-6), R(-25))
    g_beam.data.materials.append(m_yellow)
    apply_comic_styling(g_beam, bevel=True, bevel_width=0.02, outline=True)

    # 5. GRÚA ARTICULADA CON CONTENEDOR SUSPENDIDO
    crane_base = (origin.x + 3.8, origin.y - 0.6, origin.z + 1.8)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.55, depth=0.8, location=crane_base)
    c_ped = bpy.context.active_object
    c_ped.rotation_euler = (R(2), R(-6), R(-25))
    c_ped.data.materials.append(m_dark)
    apply_comic_styling(c_ped, bevel=True, bevel_width=0.02, outline=True)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(crane_base[0] - 0.9, crane_base[1] - 0.3, crane_base[2] + 1.6))
    arm1 = bpy.context.active_object
    arm1.scale = (0.35, 0.35, 2.6)
    arm1.rotation_euler = (R(-10), R(-38), R(-12))
    arm1.data.materials.append(m_yellow)
    apply_comic_styling(arm1, bevel=True, bevel_width=0.02, outline=True)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(crane_base[0] - 1.8, crane_base[1] - 0.7, crane_base[2] + 1.0))
    box = bpy.context.active_object
    box.scale = (1.4, 0.9, 0.8)
    box.rotation_euler = (R(6), R(-10), R(15))
    box.data.materials.append(m_green_cargo)
    apply_comic_styling(box, bevel=True, bevel_width=0.02, outline=True)

    # Contenedores apilados en cubierta derecha
    for cx, cy, cz in [(4.8, 0.5, 1.6), (4.4, 1.4, 1.6)]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(origin.x + cx, origin.y + cy, origin.z + cz))
        c_box = bpy.context.active_object
        c_box.scale = (1.3, 0.85, 0.75)
        c_box.rotation_euler = (R(2), R(-6), R(-25))
        c_box.data.materials.append(m_green_cargo)
        apply_comic_styling(c_box, bevel=True, bevel_width=0.02, outline=True)

    # 6. ASTEROIDES Y CAJAS FLOTANTES EN EL ESPACIO
    for ax, ay, az, asz in [(-5.2, 4.2, 5.2, 0.65), (-6.2, 1.8, 4.0, 0.45), (-4.2, -2.5, -1.2, 0.55)]:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=asz, location=(origin.x + ax, origin.y + ay, origin.z + az))
        ast = bpy.context.active_object
        ast.data.materials.append(m_rock)
        apply_comic_styling(ast, bevel=False, outline=True)

    # Cajas flotando en gravedad cero (primer plano inferior izquierdo)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(origin.x - 3.6, origin.y - 1.8, origin.z - 1.2))
    fc1 = bpy.context.active_object
    fc1.scale = (0.7, 0.7, 0.7)
    fc1.rotation_euler = (R(22), R(35), R(-15))
    fc1.data.materials.append(make_color_material("M_BoxOrange", (0.85, 0.45, 0.15, 1.0), rough=0.6))
    apply_comic_styling(fc1, bevel=True, bevel_width=0.02, outline=True)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(origin.x - 2.8, origin.y - 2.4, origin.z - 1.5))
    fc2 = bpy.context.active_object
    fc2.scale = (0.6, 0.6, 0.6)
    fc2.rotation_euler = (R(-15), R(45), R(10))
    fc2.data.materials.append(make_color_material("M_BoxCyan", (0.2, 0.65, 0.75, 1.0), rough=0.6))
    apply_comic_styling(fc2, bevel=True, bevel_width=0.02, outline=True)

# ==============================================================================
# DIORAMA 2: CRUCERO DE LUJO 'CELESTIA' (Fiel 1:1 a media_1791198833604.jpg)
# ==============================================================================
def build_crucero(origin, tex_dict):
    m_carpet = make_image_material("M_WineCarpet", tex_dict["carpet"], rough=0.75)
    m_wood = make_image_material("M_MahoganyWall", tex_dict["wood"], rough=0.45)
    m_gold = make_color_material("M_ArtDecoGold", (0.92, 0.74, 0.25, 1.0), rough=0.25, met=0.92)
    m_velvet = make_color_material("M_VelvetChair", (0.46, 0.09, 0.18, 1.0), rough=0.75)
    m_lamp_shade = make_color_material("M_LampShade", (1.0, 0.92, 0.75, 1.0), rough=0.3, emit_str=3.5)
    m_saturn = make_image_material("M_SaturnPlanet", tex_dict["saturn"], rough=0.6)
    m_rings = make_color_material("M_SaturnRings", (0.95, 0.88, 0.72, 1.0), rough=0.4, emit_str=1.8)
    m_moon = make_color_material("M_BlueMoon", (0.35, 0.68, 0.95, 1.0), rough=0.55)

    # Iluminación cálida interior para el crucero
    l_amb = bpy.data.lights.new("WarmAmb_Crucero", 'AREA')
    l_amb.energy = 220.0
    l_amb.size = 12.0
    l_amb.color = (1.0, 0.92, 0.82)
    lo_amb = bpy.data.objects.new("WarmAmb_Crucero_Obj", l_amb)
    lo_amb.location = (origin.x, origin.y, origin.z + 5.5)
    lo_amb.rotation_euler = (R(75), 0, 0)
    bpy.context.collection.objects.link(lo_amb)

    l_cosmic = bpy.data.lights.new("CosmicFill_Crucero", 'SUN')
    l_cosmic.energy = 1.8
    l_cosmic.color = (0.6, 0.75, 1.0)
    lo_cosmic = bpy.data.objects.new("CosmicFill_Crucero_Obj", l_cosmic)
    lo_cosmic.rotation_euler = (R(25), R(55), 0)
    bpy.context.collection.objects.link(lo_cosmic)

    # 1. Suelo: Moqueta de terciopelo vino tinto Art Déco (Cubre todo el suelo del salón)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(origin.x, origin.y + 1.0, origin.z + 0.05))
    carpet = bpy.context.active_object
    carpet.scale = (16.0, 16.0, 0.1)
    carpet.data.materials.append(m_carpet)

    # 2. Pared de fondo de caoba
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(origin.x + 1.5, origin.y + 5.2, origin.z + 3.8))
    back_wall = bpy.context.active_object
    back_wall.scale = (9.5, 0.3, 7.8)
    back_wall.data.materials.append(m_wood)
    apply_comic_styling(back_wall, bevel=True, bevel_width=0.03, outline=True)

    # Puerta con arco Art Déco
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(origin.x + 3.2, origin.y + 4.6, origin.z + 2.0))
    door = bpy.context.active_object
    door.scale = (1.6, 0.1, 3.6)
    door.data.materials.append(m_wood)
    apply_comic_styling(door, bevel=True, bevel_width=0.02, outline=True)

    # 3. GRAN VENTANAL EN ARCO ART DÉCO A LA IZQUIERDA
    bpy.ops.mesh.primitive_torus_add(major_radius=4.2, minor_radius=0.18, location=(origin.x - 2.6, origin.y + 1.2, origin.z + 3.8))
    arch = bpy.context.active_object
    arch.scale = (0.35, 1.15, 1.2)
    arch.rotation_euler = (0, R(90), 0)
    arch.data.materials.append(m_gold)
    apply_comic_styling(arch, bevel=True, bevel_width=0.02, outline=True)

    bpy.ops.mesh.primitive_torus_add(major_radius=3.7, minor_radius=0.08, location=(origin.x - 2.6, origin.y + 1.2, origin.z + 3.8))
    arch_inner = bpy.context.active_object
    arch_inner.scale = (0.35, 1.15, 1.2)
    arch_inner.rotation_euler = (0, R(90), 0)
    arch_inner.data.materials.append(m_gold)
    apply_comic_styling(arch_inner, bevel=True, bevel_width=0.01, outline=True)

    for ang in [20, 40, 60]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=4.2, location=(origin.x - 2.6, origin.y + 1.2, origin.z + 3.8))
        mull = bpy.context.active_object
        mull.rotation_euler = (R(ang), 0, 0)
        mull.data.materials.append(m_gold)
        apply_comic_styling(mull, bevel=True, bevel_width=0.01, outline=True)

    # 4. SATURNO CON ANILLOS Y PLANETOIDE AZUL VISIBLES POR EL VENTANAL
    saturn_pos = (origin.x - 8.5, origin.y + 3.2, origin.z + 4.8)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=2.0, location=saturn_pos)
    sat = bpy.context.active_object
    sat.data.materials.append(m_saturn)

    for r_rad in [3.2, 4.0]:
        bpy.ops.mesh.primitive_torus_add(major_radius=r_rad, minor_radius=0.05, location=saturn_pos)
        ring = bpy.context.active_object
        ring.scale = (1.0, 1.0, 0.08)
        ring.rotation_euler = (R(28), R(-22), 0)
        ring.data.materials.append(m_rings)

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.9, location=(origin.x - 7.2, origin.y + 2.0, origin.z + 1.6))
    b_moon = bpy.context.active_object
    b_moon.data.materials.append(m_moon)

    # 5. SILLONES CLUB DE TERCIOPELO BORGOÑA Y MESITAS CON LÁMPARAS
    bpy.ops.mesh.primitive_cylinder_add(radius=0.55, depth=0.45, location=(origin.x + 0.4, origin.y - 1.8, origin.z + 0.45))
    chair_fg = bpy.context.active_object
    chair_fg.data.materials.append(m_velvet)
    apply_comic_styling(chair_fg, bevel=True, bevel_width=0.03, outline=True)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.58, depth=0.9, location=(origin.x + 0.6, origin.y - 1.7, origin.z + 0.85))
    back_fg = bpy.context.active_object
    back_fg.scale = (0.7, 1.0, 1.0)
    back_fg.data.materials.append(m_velvet)
    apply_comic_styling(back_fg, bevel=True, bevel_width=0.03, outline=True)

    # Mesita con lámpara en primer plano
    bpy.ops.mesh.primitive_cylinder_add(radius=0.35, depth=0.6, location=(origin.x + 1.2, origin.y - 1.4, origin.z + 0.35))
    t_fg = bpy.context.active_object
    t_fg.data.materials.append(m_gold)
    apply_comic_styling(t_fg, bevel=True, bevel_width=0.02, outline=True)

    bpy.ops.mesh.primitive_cone_add(radius1=0.28, depth=0.45, location=(origin.x + 1.2, origin.y - 1.4, origin.z + 0.95))
    lamp_fg = bpy.context.active_object
    lamp_fg.data.materials.append(m_lamp_shade)
    apply_comic_styling(lamp_fg, bevel=True, bevel_width=0.01, outline=True)

    l_lamp = bpy.data.lights.new("LampFG_Crucero", 'POINT')
    l_lamp.energy = 85.0
    l_lamp.color = (1.0, 0.92, 0.75)
    lo_lamp = bpy.data.objects.new("LampFG_Crucero_Obj", l_lamp)
    lo_lamp.location = (origin.x + 1.2, origin.y - 1.4, origin.z + 1.0)
    bpy.context.collection.objects.link(lo_lamp)

    # Sillones a lo largo del ventanal
    for cy in [0.0, 1.8]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.52, depth=0.42, location=(origin.x - 1.2, origin.y + cy, origin.z + 0.45))
        c_mid = bpy.context.active_object
        c_mid.data.materials.append(m_velvet)
        apply_comic_styling(c_mid, bevel=True, bevel_width=0.03, outline=True)

        bpy.ops.mesh.primitive_cylinder_add(radius=0.55, depth=0.85, location=(origin.x - 1.0, origin.y + cy, origin.z + 0.85))
        b_mid = bpy.context.active_object
        b_mid.scale = (0.7, 1.0, 1.0)
        b_mid.data.materials.append(m_velvet)
        apply_comic_styling(b_mid, bevel=True, bevel_width=0.03, outline=True)

        bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=0.5, location=(origin.x - 0.4, origin.y + cy, origin.z + 0.35))
        t_mid = bpy.context.active_object
        t_mid.data.materials.append(m_gold)
        apply_comic_styling(t_mid, bevel=True, bevel_width=0.01, outline=True)

    # 6. GRAN ESCALERA A LA DERECHA CON PASAMANOS DORADO
    stair_x = origin.x + 3.2
    for i in range(9):
        sy = origin.y + 0.5 + i * 0.42
        sz = origin.z + i * 0.25
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(stair_x, sy, sz + 0.12))
        step = bpy.context.active_object
        step.scale = (1.8, 0.42, 0.25)
        step.data.materials.append(m_wood)
        apply_comic_styling(step, bevel=True, bevel_width=0.015, outline=True)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.045, depth=4.6, location=(stair_x - 0.8, origin.y + 2.2, origin.z + 2.2), rotation=(R(-31), 0, 0))
    rail = bpy.context.active_object
    rail.data.materials.append(m_gold)
    apply_comic_styling(rail, bevel=True, bevel_width=0.01, outline=True)

    # 7. CANDELABROS ART DÉCO EN EL TECHO
    for ly in [0.0, 2.5]:
        cp = (origin.x + 0.4, origin.y + ly, origin.z + 6.2)
        for dr, dz in [(1.0, 0.0), (0.75, -0.2), (0.5, -0.38)]:
            bpy.ops.mesh.primitive_cylinder_add(radius=dr, depth=0.12, location=(cp[0], cp[1], cp[2] + dz))
            disc = bpy.context.active_object
            disc.data.materials.append(m_gold if dz == 0.0 else m_lamp_shade)
            apply_comic_styling(disc, bevel=True, bevel_width=0.015, outline=True)

# ==============================================================================
# DIORAMA 3: REFINERÍA DE PLASMA TOKAMAK (Fiel 1:1 a media_1791198833604.jpg)
# ==============================================================================
def build_refineria(origin, tex_dict):
    m_tokamak = make_color_material("M_TokamakArmor", (0.32, 0.36, 0.40, 1.0), rough=0.45, met=0.75)
    m_brass = make_color_material("M_BrassCoil", (0.88, 0.70, 0.22, 1.0), rough=0.3, met=0.9)
    m_plasma = make_color_material("M_PlasmaCyan", (0.15, 0.95, 1.0, 1.0), rough=0.1, emit_str=2.5)
    m_yellow = make_color_material("M_YellowSafety", (0.95, 0.74, 0.05, 1.0), rough=0.4)
    m_grate = make_color_material("M_SteelGrate", (0.24, 0.26, 0.28, 1.0), rough=0.55, met=0.6)
    m_rock = make_color_material("M_BasaltRock", (0.28, 0.26, 0.25, 1.0), rough=0.85)
    m_sign_ref = make_image_material("M_SignRef", tex_dict["sign_ref"], rough=0.5, emit_str=1.8)
    m_sign_dang = make_image_material("M_SignDang", tex_dict["sign_dang"], rough=0.5, emit_str=1.8)

    # Iluminación de estudio para la refinería
    sun = bpy.data.lights.new("Sun_Refineria", 'SUN')
    sun.energy = 4.2
    sun.color = (0.95, 0.96, 1.0)
    s_obj = bpy.data.objects.new("Sun_Refineria_Obj", sun)
    s_obj.rotation_euler = (R(-35), R(30), 0)
    bpy.context.collection.objects.link(s_obj)

    l_plas = bpy.data.lights.new("PlasmaLight_Ref", 'POINT')
    l_plas.energy = 450.0
    l_plas.color = (0.2, 0.95, 1.0)
    lo_plas = bpy.data.objects.new("PlasmaLight_Ref_Obj", l_plas)
    lo_plas.location = (origin.x + 2.2, origin.y + 1.2, origin.z + 3.8)
    bpy.context.collection.objects.link(lo_plas)

    fill = bpy.data.lights.new("Fill_Refineria", 'AREA')
    fill.energy = 260.0
    fill.size = 20.0
    fill.color = (0.7, 0.8, 0.95)
    fo = bpy.data.objects.new("Fill_Refineria_Obj", fill)
    fo.location = (origin.x - 1.0, origin.y - 12.0, origin.z + 6.0)
    fo.rotation_euler = (R(60), 0, 0)
    bpy.context.collection.objects.link(fo)

    # 1. PASARELA METÁLICA CURVADA EN PRIMER PLANO
    bpy.ops.mesh.primitive_torus_add(major_radius=4.8, minor_radius=0.6, location=(origin.x - 1.2, origin.y - 0.8, origin.z + 1.0))
    walk = bpy.context.active_object
    walk.scale = (0.9, 0.75, 0.12)
    walk.data.materials.append(m_grate)
    apply_comic_styling(walk, bevel=True, bevel_width=0.02, outline=True)

    # Barandilla amarilla tubular
    bpy.ops.mesh.primitive_torus_add(major_radius=5.35, minor_radius=0.045, location=(origin.x - 1.2, origin.y - 0.8, origin.z + 1.6))
    w_rail = bpy.context.active_object
    w_rail.scale = (0.9, 0.75, 1.0)
    w_rail.data.materials.append(m_yellow)
    apply_comic_styling(w_rail, bevel=True, bevel_width=0.01, outline=True)

    # Postes de soporte
    for sx, sy in [(-1.8, -2.5), (-0.2, -2.8), (1.4, -1.8)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=3.5, location=(origin.x + sx, origin.y + sy, origin.z - 0.6))
        post = bpy.context.active_object
        post.data.materials.append(m_tokamak)
        apply_comic_styling(post, bevel=True, bevel_width=0.01, outline=True)

    # 2. ESCLUSA Y COMPUERTA A LA IZQUIERDA
    gate_pos = (origin.x - 2.8, origin.y + 2.2, origin.z + 2.4)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=gate_pos)
    gate = bpy.context.active_object
    gate.scale = (2.0, 0.5, 3.2)
    gate.data.materials.append(m_tokamak)
    apply_comic_styling(gate, bevel=True, bevel_width=0.03, outline=True)

    # Rótulo iluminado REFINERÍA DE PLASMA
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(gate_pos[0], gate_pos[1] - 0.3, gate_pos[2] + 1.9))
    sign_r = bpy.context.active_object
    sign_r.scale = (1.6, 0.06, 0.45)
    sign_r.data.materials.append(m_sign_ref)
    apply_comic_styling(sign_r, bevel=True, bevel_width=0.01, outline=True)

    # 3. COLOSAL REACTOR TOKAMAK TOROIDAL A LA DERECHA
    t_loc = (origin.x + 2.2, origin.y + 1.5, origin.z + 3.8)
    bpy.ops.mesh.primitive_torus_add(major_radius=2.6, minor_radius=0.6, location=t_loc)
    t_casing = bpy.context.active_object
    t_casing.rotation_euler = (R(90), 0, 0)
    t_casing.data.materials.append(m_tokamak)
    apply_comic_styling(t_casing, bevel=True, bevel_width=0.03, outline=True)

    # ANILLO DE PLASMA CIAN
    bpy.ops.mesh.primitive_torus_add(major_radius=1.85, minor_radius=0.28, location=t_loc)
    p_ring = bpy.context.active_object
    p_ring.rotation_euler = (R(90), 0, 0)
    p_ring.data.materials.append(m_plasma)

    # Núcleo de fusión brillante
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.45, location=t_loc)
    p_core = bpy.context.active_object
    p_core.data.materials.append(m_plasma)

    # Rayos de energía radiales
    for ang in [0, 60, 120, 180, 240, 300]:
        a_rad = R(ang)
        lx = t_loc[0] + 1.1 * math.cos(a_rad)
        lz = t_loc[2] + 1.1 * math.sin(a_rad)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=1.6, location=(lx, t_loc[1], lz))
        bolt = bpy.context.active_object
        bolt.rotation_euler = (0, -a_rad + R(90), 0)
        bolt.data.materials.append(m_plasma)

    # 6 Bobinas electromagnéticas de latón
    for ang in [0, 60, 120, 180, 240, 300]:
        a_rad = R(ang)
        cx = t_loc[0] + 2.6 * math.cos(a_rad)
        cz = t_loc[2] + 2.6 * math.sin(a_rad)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.24, depth=0.85, location=(cx, t_loc[1], cz))
        clamp = bpy.context.active_object
        clamp.rotation_euler = (0, -a_rad, 0)
        clamp.data.materials.append(m_brass)
        apply_comic_styling(clamp, bevel=True, bevel_width=0.015, outline=True)

    # 4. MAQUINARIA DE LA BASE Y TUBERÍAS
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(t_loc[0], t_loc[1] - 0.4, origin.z + 0.9))
    base_mach = bpy.context.active_object
    base_mach.scale = (4.4, 2.2, 1.8)
    base_mach.data.materials.append(m_tokamak)
    apply_comic_styling(base_mach, bevel=True, bevel_width=0.03, outline=True)

    # Rótulo de advertencia: PELIGRO ALTA ENERGÍA
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(t_loc[0] + 1.8, t_loc[1] - 1.55, origin.z + 1.1))
    dang = bpy.context.active_object
    dang.scale = (0.75, 0.05, 0.45)
    dang.data.materials.append(m_sign_dang)
    apply_comic_styling(dang, bevel=True, bevel_width=0.01, outline=True)

    for px in [-1.5, 1.5]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=2.8, location=(t_loc[0] + px, t_loc[1] - 0.2, origin.z + 2.2))
        pipe = bpy.context.active_object
        pipe.data.materials.append(m_tokamak)
        apply_comic_styling(pipe, bevel=True, bevel_width=0.015, outline=True)

    # 5. DRON DE SERVICIO Y ASTEROIDES
    drone_pos = (origin.x - 0.6, origin.y - 2.4, origin.z + 1.1)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=drone_pos)
    drone = bpy.context.active_object
    drone.scale = (0.45, 0.45, 0.25)
    drone.data.materials.append(m_tokamak)
    apply_comic_styling(drone, bevel=True, bevel_width=0.015, outline=True)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.1, location=(drone_pos[0], drone_pos[1] - 0.25, drone_pos[2]))
    d_light = bpy.context.active_object
    d_light.rotation_euler = (R(90), 0, 0)
    d_light.data.materials.append(m_yellow)

    for ax, ay, az, asz in [(-3.8, 3.8, 4.8, 0.8), (4.5, 3.2, 5.5, 1.1), (-2.8, -3.8, 0.2, 0.5)]:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=asz, location=(origin.x + ax, origin.y + ay, origin.z + az))
        ast = bpy.context.active_object
        ast.data.materials.append(m_rock)
        apply_comic_styling(ast, bevel=False, outline=True)

# ==============================================================================
# PIPELINE PRINCIPAL Y GENERACIÓN DEL TRÍPTICO MAESTRO OFICIAL
# ==============================================================================
def main():
    print("=== INICIANDO GENERADOR MAESTRO DE MAPAS (FIEL 1:1 CON media_1791198833604.jpg) ===")
    scene = reset_scene()
    tex_dict = generate_map_textures()
    init_outline_material()
    setup_starfield_world()

    print("[1/3] Construyendo Diorama: Carguero Químico (X = -35.0)...")
    build_carguero(Vector((-35.0, 0.0, 0.0)), tex_dict)

    print("[2/3] Construyendo Diorama: Crucero de Lujo 'Celestia' (X = 0.0)...")
    build_crucero(Vector((0.0, 0.0, 0.0)), tex_dict)

    print("[3/3] Construyendo Diorama: Refinería de Plasma Tokamak (X = +35.0)...")
    build_refineria(Vector((35.0, 0.0, 0.0)), tex_dict)

    blend_path = os.path.join(PROJECT_ROOT, "Art", "Blender", "Mapas_Arquetipos_Oficial.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[OK] Proyecto Blend guardado: {blend_path}")

    # Configuración de Cámaras Calibradas Exactas
    cam_data = bpy.data.cameras.new("MasterCam")
    cam_obj = bpy.data.objects.new("MasterCamObj", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    shots = [
        {
            "name": "Carguero_Quimico",
            "pos": (-35.5, -13.8, 5.2),
            "rot": (R(69), 0, R(-1)),
            "lens": 32.0,
            "title": "Carguero Químico",
            "subtitle": "Transporte Industrial de Ácido Goo • Riesgo Tóxico Nivel 1"
        },
        {
            "name": "Crucero_Lujo",
            "pos": (0.8, -4.5, 2.05),
            "rot": (R(78), 0, R(16)),
            "lens": 20.0,
            "title": "Crucero de Lujo",
            "subtitle": "Transatlántico Orbital 'Celestia' • Lujo Art-Déco y Mirador"
        },
        {
            "name": "Refineria_Plasma",
            "pos": (34.2, -8.6, 2.7),
            "rot": (R(77), 0, R(-3)),
            "lens": 28.0,
            "title": "Refinería de Plasma",
            "subtitle": "Complejo Minero Tokamak • Fusión Confinada y Pasarela"
        }
    ]

    rendered_files = []
    for shot in shots:
        cam_obj.location = shot["pos"]
        cam_obj.rotation_euler = shot["rot"]
        cam_data.lens = shot["lens"]
        bpy.context.view_layer.update()

        out_path = os.path.join(RENDERS_DIR, f"Showcase_Mapa_{shot['name']}.png")
        scene.render.filepath = out_path
        print(f"[RENDER] Procesando {shot['name']}...")
        bpy.ops.render.render(write_still=True)
        rendered_files.append((out_path, shot["title"], shot["subtitle"]))
        print(f"[OK] Guardado: {out_path}")

    # Composición del Tríptico Horizontal Maestro con Pillow (Estilo Cómic 1:1)
    triptych = Image.new("RGB", (2560, 1440), (16, 14, 12))
    draw_trip = ImageDraw.Draw(triptych)

    font_large = get_system_font(38, bold=True)
    font_sub = get_system_font(22, bold=False)

    panel_w = 780
    panel_h = 1180
    paste_y = 40

    for i, (fpath, title, subtitle) in enumerate(rendered_files):
        img = Image.open(fpath)
        img_resized = img.resize((panel_w, panel_h), Image.Resampling.LANCZOS)
        paste_x = 55 + i * (panel_w + 45)
        triptych.paste(img_resized, (paste_x, paste_y))

        # Marco grueso de tinta de cómic
        draw_trip.rectangle([(paste_x - 5, paste_y - 5), (paste_x + panel_w + 5, paste_y + panel_h + 5)], outline=(8, 6, 6), width=8)
        draw_trip.rectangle([(paste_x, paste_y), (paste_x + panel_w, paste_y + panel_h)], outline=(160, 120, 75), width=2)

        # Cartela de título inferior en estilo cómic desgastado
        banner_y = paste_y + panel_h + 16
        draw_trip.rectangle([(paste_x, banner_y), (paste_x + panel_w, banner_y + 115)], fill=(28, 24, 22), outline=(215, 165, 85), width=2)
        draw_trip.text((paste_x + 35, banner_y + 20), title, fill=(250, 235, 205), font=font_large)
        draw_trip.text((paste_x + 35, banner_y + 70), subtitle, fill=(195, 165, 125), font=font_sub)

    triptych_master = os.path.join(RENDERS_DIR, "Showcase_Mapas_Arquetipos_Oficial.png")
    triptych.save(triptych_master)
    print(f"[OK] Master Triptych Mapas guardado: {triptych_master}")

    shutil.copy2(triptych_master, os.path.join(ARTIFACT_DIR, "Showcase_Mapas_Arquetipos_Oficial.png"))
    for fpath, _, _ in rendered_files:
        shutil.copy2(fpath, os.path.join(ARTIFACT_DIR, os.path.basename(fpath)))

    print("=== PIPELINE MAPAS ARQUETIPOS COMPLETADO EXITOSAMENTE ===")

if __name__ == "__main__":
    main()

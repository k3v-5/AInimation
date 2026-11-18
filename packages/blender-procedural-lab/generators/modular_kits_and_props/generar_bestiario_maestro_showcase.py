#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
===============================================================================
GENERADOR MAESTRO DEL BESTIARIO Y FACTORÍA SECTOR 7 - BLENDER 5.2 LTS (EEVEE)
FIDELIDAD 1:1 CON LA GUÍA ANOTADA OFICIAL (media_1791273929163.png)
===============================================================================
Implementación estricta y exhaustiva de los 20 pilares visuales:
01. CONTORNO NEGRO GRUESO (Inverted Hull Solidify + Backface Culling, trazo 0.024-0.034m)
02. VARIACIÓN DE TRAZO (Line weight jerárquico en siluetas y micro-detalles)
03. FUEGO ESTILIZADO 3D (Llamas cómic bicapa: contorno tinta + gradiente amarillo/naranja y blanco/cian)
04. PISTONES Y ARTICULACIONES (Cilindros hidráulicos + vástagos de latón/acero)
05. GARRAS EXAGERADAS (Garras curvas cartoon 3D afiladas y gruesas en manos y patas)
06. LENTE EMISIVA + MONITOR CRT VERDE (Dron Auditor con radar, telemetría y lente roja)
07. REMACHES, TUERCAS Y MANÓMETROS (3 manómetros superiores orientados frontalmente a cámara con dial analógico)
08. TEXTURA DE DESGASTE (Óxido en juntas, calavera de hueso marfil con fisuras y ladrillo refractario)
09. ASIMETRÍA Y CHATARRA (Trasgo con máscara calavera con dientes, monóculo gigante, cuernos curvados y sierra)
10. EXPRESIVIDAD EN LOS OJOS (Monóculo gigante dorado vs ojo hundido con pupila roja)
11. DETALLES DE ENGRANAJES (Hebilla de cinturón de bronce envejecido y sierra circular dentada de acero)
12. POSES DINÁMICAS (Lobo en acecho bajo en pasarela, trasgo en guardia, titán de magma saliendo del horno)
13. SOMBRAS Y OCLUSIÓN DE CONTACTO (Sombra dura cómic y contraste industrial oscuro)
14. CABLES Y TUBERÍAS EXPUESTOS (Conductos superiores y cables colgantes en catenaria)
15. PERSPECTIVA Y ANATOMÍA INDUSTRIAL (Spider-Bot colgado del techo con pistones)
16. ILUMINACIÓN EMISIVA (Fuego naranja/cian puro, canales de magma ardiente y baterías verdes)
17. CONO DE ESCANEO (Haz cónico rojo semitransparente que ilumina los escombros)
18. LUZ DE REBOTE (Rim lighting cálido anaranjado proyectado desde el fuego del horno)
19. CEL SHADING DE 2 TONOS (Sombra dura, alto contraste y acabado cómic puro con mapeo UV/Flat y Triplanar)
20. AMBIENTE SUCIO Y CONTRASTE INDUSTRIAL (Pasarela hazard, escombros y letrero SECTOR 7)
===============================================================================
"""

import bpy
import bmesh
import math
from mathutils import Vector, Euler, Matrix
import os
import shutil
from PIL import Image, ImageDraw, ImageFont

# ==============================================================================
# CONFIGURACIÓN DE RUTAS Y CONSTANTES
# ==============================================================================
PROJECT_ROOT = r"F:\Dev\Game"
RENDERS_DIR = os.path.join(PROJECT_ROOT, "Art", "Renders")
TEXTURES_DIR = os.path.join(PROJECT_ROOT, "Art", "Textures")
ARTIFACT_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\b59ff04f-3c21-4ee5-94b0-8e8f899f8923"

os.makedirs(RENDERS_DIR, exist_ok=True)
os.makedirs(TEXTURES_DIR, exist_ok=True)
os.makedirs(ARTIFACT_DIR, exist_ok=True)

def R(degrees):
    """Convierte grados sexagesimales a radianes."""
    return math.radians(degrees)

def get_system_font(size=18, bold=True):
    font_paths = [
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf" if bold else r"C:\Windows\Fonts\segoeui.ttf",
        r"C:\Windows\Fonts\calibrib.ttf" if bold else r"C:\Windows\Fonts\calibri.ttf",
    ]
    for p in font_paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

# ==============================================================================
# 1. GENERACIÓN DE TEXTURAS PROCEDURALES DE ALTA FIDELIDAD CÓMIC (PIL)
# ==============================================================================
def generate_annotated_bestiary_textures():
    textures = {}

    # A) Placas de Metal Desgastado Cómic con Cross-Hatching y Remaches Dobles
    tex_plates_path = os.path.join(TEXTURES_DIR, "tex_plates_crosshatch.png")
    img_p = Image.new('RGB', (1024, 1024), color=(140, 146, 160))
    draw_p = ImageDraw.Draw(img_p)
    for px in [0, 512]:
        for py in [0, 512]:
            draw_p.rectangle([px+8, py+8, px+504, py+504], fill=(168, 176, 192), outline=(42, 48, 58), width=8)
            draw_p.rectangle([px+16, py+16, px+496, py+496], outline=(195, 202, 215), width=3)
            for h in range(24, 240, 14):
                draw_p.line([(px+h, py+490), (px+h+85, py+405)], fill=(75, 82, 98), width=3)
                draw_p.line([(px+490-h, py+24), (px+405-h, py+109)], fill=(75, 82, 98), width=3)
            for rx, ry in [(px+36, py+36), (px+476, py+36), (px+36, py+476), (px+476, py+476),
                           (px+256, py+28), (px+256, py+484), (px+28, py+256), (px+484, py+256),
                           (px+120, py+36), (px+390, py+36), (px+120, py+476), (px+390, py+476)]:
                draw_p.ellipse([rx-10, ry-10, rx+10, ry+10], fill=(70, 76, 88), outline=(28, 32, 40), width=3)
                draw_p.ellipse([rx-5, ry-5, rx+5, ry+5], fill=(210, 218, 230))
                draw_p.ellipse([rx-2, ry-2, rx+2, ry+2], fill=(255, 255, 255))
            for ox, oy in [(px+160, py+430), (px+340, py+440), (px+40, py+160), (px+380, py+180)]:
                draw_p.ellipse([ox, oy, ox+60, oy+45], fill=(135, 65, 32))
                draw_p.line([(ox+5, oy+10), (ox+50, oy+25)], fill=(90, 38, 16), width=4)
    img_p.save(tex_plates_path)
    textures["plates"] = tex_plates_path

    # B) Manómetro Analógico de Presión (0-120 PSI con bisel dorado, aguja roja y dial blanco nítido)
    tex_dial_path = os.path.join(TEXTURES_DIR, "tex_dial_analogo.png")
    img_d = Image.new('RGB', (1024, 1024), color=(252, 250, 242))
    draw_d = ImageDraw.Draw(img_d)
    cx, cy = 512, 512
    draw_d.ellipse([20, 20, 1004, 1004], outline=(18, 16, 14), width=42)
    draw_d.ellipse([56, 56, 968, 968], outline=(215, 172, 38), width=32)
    draw_d.ellipse([84, 84, 940, 940], outline=(35, 32, 28), width=10)
    draw_d.pieslice([104, 104, 920, 920], start=305, end=358, fill=(232, 34, 28))
    font_num = get_system_font(46, bold=True)
    font_sub = get_system_font(34, bold=True)
    draw_d.text((cx - 75, cy + 155), "PSI x10", fill=(35, 35, 42), font=font_sub)
    draw_d.text((cx - 105, cy + 205), "HIGH PRESS", fill=(195, 22, 22), font=font_sub)
    for i in range(13):
        ang_deg = 135 + i * 22.5
        ang_rad = math.radians(ang_deg)
        x1 = cx + 375 * math.cos(ang_rad)
        y1 = cy + 375 * math.sin(ang_rad)
        is_major = (i % 2 == 0)
        len_t = 70 if is_major else 40
        x2 = cx + (375 - len_t) * math.cos(ang_rad)
        y2 = cy + (375 - len_t) * math.sin(ang_rad)
        draw_d.line([(x1, y1), (x2, y2)], fill=(16, 16, 22), width=12 if is_major else 6)
        if is_major:
            xt = cx + 250 * math.cos(ang_rad) - 28
            yt = cy + 250 * math.sin(ang_rad) - 28
            draw_d.text((xt, yt), f"{i*10}", fill=(16, 16, 22), font=font_num)
    needle_ang = math.radians(332)
    nx = cx + 330 * math.cos(needle_ang)
    ny = cy + 330 * math.sin(needle_ang)
    draw_d.line([(cx, cy), (nx, ny)], fill=(240, 20, 20), width=22)
    draw_d.ellipse([cx-44, cy-44, cx+44, cy+44], fill=(28, 28, 34), outline=(225, 185, 45), width=12)
    img_d.save(tex_dial_path)
    textures["dial"] = tex_dial_path

    # C) Monitor CRT Verde Fosfórico (Radar circular, barrido, anomalía y telemetría de Sector 7)
    tex_crt_path = os.path.join(TEXTURES_DIR, "tex_crt_green_screen.png")
    img_c = Image.new('RGB', (1024, 1024), color=(6, 24, 12))
    draw_c = ImageDraw.Draw(img_c)
    draw_c.rectangle([12, 12, 1012, 1012], outline=(45, 220, 80), width=18)
    for y in range(0, 1024, 6):
        draw_c.line([(0, y), (1024, y)], fill=(12, 42, 18), width=2)
    rcx, rcy = 512, 512
    for rad in [110, 220, 330, 420]:
        draw_c.ellipse([rcx-rad, rcy-rad, rcx+rad, rcy+rad], outline=(55, 235, 90), width=6)
    draw_c.line([(rcx-420, rcy), (rcx+420, rcy)], fill=(55, 235, 90), width=5)
    draw_c.line([(rcx, rcy-420), (rcx, rcy+420)], fill=(55, 235, 90), width=5)
    sw_ang = math.radians(38)
    draw_c.line([(rcx, rcy), (rcx + 420*math.cos(sw_ang), rcy + 420*math.sin(sw_ang))], fill=(195, 255, 210), width=9)
    for bx, by in [(610, 380), (410, 620), (690, 670), (440, 340)]:
        draw_c.ellipse([bx-18, by-18, bx+18, by+18], fill=(255, 255, 130), outline=(20, 95, 35), width=4)
    font_crt_h = get_system_font(42, bold=True)
    font_crt_s = get_system_font(28, bold=True)
    draw_c.text((55, 45), "AUDIT://SYS_ACTIVE", fill=(120, 255, 150), font=font_crt_h)
    draw_c.text((55, 102), "SECTOR 07 ANOMALY: HOSTILE DETECTED", fill=(120, 255, 150), font=font_crt_s)
    draw_c.text((55, 915), "PRESSURE: 98.4 PSI | SCAN CONE ACTIVE", fill=(120, 255, 150), font=font_crt_s)
    img_c.save(tex_crt_path)
    textures["crt"] = tex_crt_path

    # D) Rejilla Industrial de Suelo (Diamond Tread Grate)
    tex_floor_path = os.path.join(TEXTURES_DIR, "tex_floor_grate_hazard.png")
    img_f = Image.new('RGB', (1024, 1024), color=(50, 56, 68))
    draw_f = ImageDraw.Draw(img_f)
    for gx in range(0, 1024, 64):
        draw_f.line([(gx, 0), (gx, 1024)], fill=(24, 28, 36), width=7)
    for gy in range(0, 1024, 64):
        draw_f.line([(0, gy), (1024, gy)], fill=(24, 28, 36), width=7)
    for gx in range(0, 1024, 64):
        for gy in range(0, 1024, 64):
            draw_f.polygon([(gx+32, gy+12), (gx+52, gy+32), (gx+32, gy+52), (gx+12, gy+32)],
                           fill=(98, 108, 126), outline=(20, 24, 30), width=3)
    img_f.save(tex_floor_path)
    textures["floor"] = tex_floor_path

    # E) Franjas de Peligro a 45° (Hazard Stripes)
    tex_hazard_path = os.path.join(TEXTURES_DIR, "tex_hazard_stripes.png")
    img_h = Image.new('RGB', (512, 512), color=(255, 210, 15))
    draw_h = ImageDraw.Draw(img_h)
    stripe_w = 48
    for d in range(-512, 1024, stripe_w * 2):
        draw_h.polygon([(d, 0), (d + stripe_w, 0), (d + stripe_w + 512, 512), (d + 512, 512)], fill=(18, 20, 24))
    img_h.save(tex_hazard_path)
    textures["hazard_stripes"] = tex_hazard_path

    # F) Ladrillos Refractarios del Horno (Brick Forge con hollín y juntas)
    tex_brick_path = os.path.join(TEXTURES_DIR, "tex_brick_forge.png")
    img_b = Image.new('RGB', (1024, 1024), color=(145, 52, 36))
    draw_b = ImageDraw.Draw(img_b)
    brick_h = 48
    brick_w = 96
    for r, y in enumerate(range(0, 1024, brick_h)):
        draw_b.line([(0, y), (1024, y)], fill=(24, 14, 10), width=9)
        offset = (r % 2) * (brick_w // 2)
        for x in range(offset - brick_w, 1024 + brick_w, brick_w):
            draw_b.line([(x, y), (x, y + brick_h)], fill=(24, 14, 10), width=9)
            var_r = (x * 17 + y * 23) % 45
            draw_b.rectangle([x+4, y+4, x+brick_w-4, y+brick_h-4], fill=(135 + var_r, 45 + var_r//2, 28))
            if (x + y) % 55 == 0:
                draw_b.ellipse([x+10, y+8, x+55, y+36], fill=(36, 18, 12))
    img_b.save(tex_brick_path)
    textures["brick"] = tex_brick_path

    # G) Letrero Stencil SECTOR 7 (Solo visible en Panorama)
    tex_sign_path = os.path.join(TEXTURES_DIR, "tex_sector7_sign.png")
    img_sign = Image.new('RGB', (512, 256), color=(28, 32, 40))
    draw_sign = ImageDraw.Draw(img_sign)
    draw_sign.rectangle([6, 6, 506, 250], outline=(255, 205, 15), width=8)
    draw_sign.rectangle([14, 14, 498, 242], outline=(12, 14, 18), width=4)
    for bx, by in [(28, 28), (484, 28), (28, 228), (484, 228)]:
        draw_sign.ellipse([bx-8, by-8, bx+8, by+8], fill=(185, 190, 200), outline=(10, 10, 12), width=3)
    font_s7 = get_system_font(52, bold=True)
    draw_sign.text((75, 82), "SECTOR 7", fill=(255, 205, 15), font=font_s7)
    font_s7_sub = get_system_font(20, bold=True)
    draw_sign.text((120, 165), "RESTRICTED ACCESS", fill=(235, 240, 248), font=font_s7_sub)
    img_sign.save(tex_sign_path)
    textures["sign_s7"] = tex_sign_path

    return textures

# ==============================================================================
# 2. SISTEMA DE MATERIALES (CEL-SHADING 2 TONOS + INVERTED HULL + EMISIVO)
# ==============================================================================
M_COMIC_OUTLINE = None

def init_comic_outline_material():
    """Crea el material negro mate puro para la silueta Inverted Hull con Backface Culling."""
    global M_COMIC_OUTLINE
    mat = bpy.data.materials.get("M_Comic_Ink_Outline") or bpy.data.materials.new(name="M_Comic_Ink_Outline")
    mat.use_nodes = True
    mat.use_backface_culling = True
    nt = mat.node_tree
    nt.nodes.clear()

    out = nt.nodes.new(type='ShaderNodeOutputMaterial')
    emit = nt.nodes.new(type='ShaderNodeEmission')
    emit.inputs['Color'].default_value = (0.0, 0.0, 0.0, 1.0)
    emit.inputs['Strength'].default_value = 1.0
    nt.links.new(emit.outputs['Emission'], out.inputs['Surface'])

    M_COMIC_OUTLINE = mat
    return mat

def create_comic_flame_material(name, flame_type='orange'):
    """
    Shader de llamas estilizadas cómic 2D/3D (Pilar 03):
    Gradiente procedural a lo largo del eje local Z (Generated coordinates):
    - Orange: Núcleo amarillo brillante incandescente -> Cuerpo naranja puro saturado -> Puntas carmesí.
    - Cyan: Núcleo blanco-cian cegador -> Cuerpo cian eléctrico saturado -> Puntas cobalto cian.
    """
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out = nt.nodes.new(type='ShaderNodeOutputMaterial')
    emit = nt.nodes.new(type='ShaderNodeEmission')
    emit.inputs['Strength'].default_value = 1.6

    coord = nt.nodes.new(type='ShaderNodeTexCoord')
    sep = nt.nodes.new(type='ShaderNodeSeparateXYZ')
    ramp = nt.nodes.new(type='ShaderNodeValToRGB')
    ramp.color_ramp.interpolation = 'LINEAR'

    if flame_type == 'cyan':
        ramp.color_ramp.elements[0].position = 0.0
        ramp.color_ramp.elements[0].color = (0.85, 1.0, 1.0, 1.0)
        ramp.color_ramp.elements[1].position = 0.42
        ramp.color_ramp.elements[1].color = (0.0, 0.86, 1.0, 1.0)
        elem_tip = ramp.color_ramp.elements.new(0.85)
        elem_tip.color = (0.0, 0.38, 0.95, 1.0)
    else:
        ramp.color_ramp.elements[0].position = 0.0
        ramp.color_ramp.elements[0].color = (1.0, 0.95, 0.18, 1.0)
        ramp.color_ramp.elements[1].position = 0.38
        ramp.color_ramp.elements[1].color = (1.0, 0.40, 0.02, 1.0)
        elem_tip = ramp.color_ramp.elements.new(0.82)
        elem_tip.color = (0.95, 0.14, 0.01, 1.0)

    nt.links.new(coord.outputs['Generated'], sep.inputs['Vector'])
    nt.links.new(sep.outputs['Z'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], emit.inputs['Color'])
    nt.links.new(emit.outputs['Emission'], out.inputs['Surface'])
    return mat

def create_comic_cel_material(name, base_rgb, shadow_factor=0.38, tex_path=None, tex_scale=(1.4, 1.4, 1.4), is_uv_decal=False, is_emissive=False, emissive_rgb=None):
    """
    Shader Cel-Shading de 2 tonos en EEVEE (Pilar 19):
    - Detección precisa de luz Diffuse -> ShaderToRGB -> Rampa de 2 bandas constantes.
    - Sombra dura cómic y contraste punchy (Pilar 13 y 19).
    - Mapeo Triplanar Box para mallas complejas y Mapeo UV Plano para decals.
    - Preservación íntegra de texturas mediante Multiply/Overlay.
    """
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    out = nt.nodes.new(type='ShaderNodeOutputMaterial')

    # A) Material Emisivo Puro
    if is_emissive:
        emit = nt.nodes.new(type='ShaderNodeEmission')
        emit.inputs['Strength'].default_value = 1.4
        if tex_path and os.path.exists(tex_path) and is_uv_decal:
            tex_node = nt.nodes.new(type='ShaderNodeTexImage')
            tex_node.image = bpy.data.images.load(tex_path, check_existing=True)
            tex_node.projection = 'FLAT'
            coord_node = nt.nodes.new(type='ShaderNodeTexCoord')
            nt.links.new(coord_node.outputs['UV'], tex_node.inputs['Vector'])
            nt.links.new(tex_node.outputs['Color'], emit.inputs['Color'])
        else:
            emit.inputs['Color'].default_value = emissive_rgb if emissive_rgb else base_rgb
        nt.links.new(emit.outputs['Emission'], out.inputs['Surface'])
        return mat

    # B) Cel-Shading de 2 tonos
    diff = nt.nodes.new(type='ShaderNodeBsdfDiffuse')
    diff.inputs['Color'].default_value = (1.0, 1.0, 1.0, 1.0)
    diff.inputs['Roughness'].default_value = 0.0

    s2rgb = nt.nodes.new(type='ShaderNodeShaderToRGB')
    rgb2bw = nt.nodes.new(type='ShaderNodeRGBToBW')

    ramp = nt.nodes.new(type='ShaderNodeValToRGB')
    ramp.color_ramp.interpolation = 'CONSTANT'
    shadow_col = (base_rgb[0] * shadow_factor,
                  base_rgb[1] * (shadow_factor * 1.02),
                  base_rgb[2] * (shadow_factor * 1.10),
                  1.0)
    ramp.color_ramp.elements[0].position = 0.30
    ramp.color_ramp.elements[0].color = shadow_col
    ramp.color_ramp.elements[1].position = 0.34
    ramp.color_ramp.elements[1].color = base_rgb

    coord_node = nt.nodes.new(type='ShaderNodeTexCoord')

    if tex_path and os.path.exists(tex_path):
        tex_node = nt.nodes.new(type='ShaderNodeTexImage')
        tex_node.image = bpy.data.images.load(tex_path, check_existing=True)

        if is_uv_decal:
            tex_node.projection = 'FLAT'
            nt.links.new(coord_node.outputs['UV'], tex_node.inputs['Vector'])
            final_color_socket = tex_node.outputs['Color']
        else:
            tex_node.projection = 'BOX'
            tex_node.projection_blend = 0.15
            map_node = nt.nodes.new(type='ShaderNodeMapping')
            map_node.inputs['Scale'].default_value = tex_scale
            nt.links.new(coord_node.outputs['Object'], map_node.inputs['Vector'])
            nt.links.new(map_node.outputs['Vector'], tex_node.inputs['Vector'])

            mix_tex = nt.nodes.new(type='ShaderNodeMix')
            mix_tex.data_type = 'RGBA'
            mix_tex.blend_type = 'MULTIPLY'
            mix_tex.inputs['Factor'].default_value = 0.45
            nt.links.new(ramp.outputs['Color'], mix_tex.inputs[6])
            nt.links.new(tex_node.outputs['Color'], mix_tex.inputs[7])
            final_color_socket = mix_tex.outputs[2]
    else:
        final_color_socket = ramp.outputs['Color']

    emit = nt.nodes.new(type='ShaderNodeEmission')
    emit.inputs['Strength'].default_value = 1.0

    nt.links.new(diff.outputs['BSDF'], s2rgb.inputs['Shader'])
    nt.links.new(s2rgb.outputs['Color'], rgb2bw.inputs['Color'])
    nt.links.new(rgb2bw.outputs['Val'], ramp.inputs['Fac'])
    nt.links.new(final_color_socket, emit.inputs['Color'])
    nt.links.new(emit.outputs['Emission'], out.inputs['Surface'])

    return mat

def create_scan_cone_material():
    mat = bpy.data.materials.get("M_Scan_Cone_Beam") or bpy.data.materials.new(name="M_Scan_Cone_Beam")
    mat.use_nodes = True
    mat.surface_render_method = 'BLENDED'
    nt = mat.node_tree
    nt.nodes.clear()

    out = nt.nodes.new(type='ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (1.0, 0.05, 0.02, 1.0)
    bsdf.inputs['Alpha'].default_value = 0.08
    bsdf.inputs['Roughness'].default_value = 0.1
    if 'Emission Color' in bsdf.inputs:
        bsdf.inputs['Emission Color'].default_value = (1.0, 0.05, 0.02, 1.0)
        bsdf.inputs['Emission Strength'].default_value = 1.2
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def apply_comic_styling(obj, bevel_w=0.015, outline=True, outline_w=0.024, cast_shadow=True):
    """Aplica bisel cómic y contorno negro de tinta grueso con Solidify Inverted Hull (Pilar 01, 02)."""
    if not obj or obj.type != 'MESH':
        return

    obj.visible_shadow = cast_shadow

    if bevel_w > 0.001:
        bev = obj.modifiers.new(name="ComicBevel", type='BEVEL')
        bev.width = bevel_w
        bev.segments = 2
        bev.limit_method = 'ANGLE'
        bev.angle_limit = math.radians(40)

    if outline:
        global M_COMIC_OUTLINE
        if M_COMIC_OUTLINE is None:
            init_comic_outline_material()

        if M_COMIC_OUTLINE.name not in obj.data.materials:
            obj.data.materials.append(M_COMIC_OUTLINE)
        outline_mat_idx = list(obj.data.materials).index(M_COMIC_OUTLINE)

        sol = obj.modifiers.new(name="ComicOutline", type='SOLIDIFY')
        sol.thickness = outline_w
        sol.offset = 1.0
        sol.use_flip_normals = True
        sol.use_rim = False
        sol.material_offset = outline_mat_idx

# ==============================================================================
# 3. GENERADORES DE GEOMETRÍA ANATÓMICA Y PIEZAS
# ==============================================================================
def create_beveled_box(name, loc, size, rot=(0,0,0), mat=None, bevel_w=0.015, outline=True, outline_w=0.022, cast_shadow=True, registry=None):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc, rotation=rot)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if mat:
        obj.data.materials.append(mat)
    apply_comic_styling(obj, bevel_w=bevel_w, outline=outline, outline_w=outline_w, cast_shadow=cast_shadow)
    if registry is not None:
        registry.append(obj)
    return obj

def create_beveled_cylinder(name, loc, radius, depth, rot=(0,0,0), mat=None, bevel_w=0.010, outline=True, outline_w=0.020, cast_shadow=True, registry=None):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, vertices=24, location=loc, rotation=rot)
    obj = bpy.context.active_object
    obj.name = name
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if mat:
        obj.data.materials.append(mat)
    apply_comic_styling(obj, bevel_w=bevel_w, outline=outline, outline_w=outline_w, cast_shadow=cast_shadow)
    if registry is not None:
        registry.append(obj)
    return obj

def create_hydraulic_piston(name, p_start, p_end, cyl_r=0.042, rod_r=0.022, mat_cyl=None, mat_rod=None, registry=None):
    p1 = Vector(p_start)
    p2 = Vector(p_end)
    delta = p2 - p1
    length = delta.length
    if length < 0.001:
        return
    direction = delta.normalized()
    rot_quat = Vector((0, 0, 1)).rotation_difference(direction)
    rot_euler = rot_quat.to_euler()

    cyl_len = length * 0.58
    cyl_pos = p1 + direction * (cyl_len * 0.5)
    create_beveled_cylinder(f"{name}_Cyl", cyl_pos, cyl_r, cyl_len, rot_euler, mat_cyl, bevel_w=0.006, outline_w=0.016, cast_shadow=False, registry=registry)

    rod_len = length * 0.65
    rod_pos = p2 - direction * (rod_len * 0.5)
    create_beveled_cylinder(f"{name}_Rod", rod_pos, rod_r, rod_len, rot_euler, mat_rod, bevel_w=0.004, outline_w=0.012, cast_shadow=False, registry=registry)

def create_cartoon_claw(name, loc, rot, scale=1.45, mat=None, registry=None):
    """
    Genera una garra curva estilo cartoon 3D afilada, gruesa y triangular (Pilar 05).
    Se curva hacia abajo y adelante simulando un zarpazo depredador.
    """
    bm = bmesh.new()
    steps = 9
    layers = []
    for i in range(steps):
        t = i / (steps - 1)
        x = t * 0.72 * scale
        z = -0.48 * (t ** 2.2) * scale
        w = (1.0 - t * 0.80) * 0.16 * scale
        h = (1.0 - t * 0.68) * 0.18 * scale
        v0 = bm.verts.new((x, -w, z - h*0.5))
        v1 = bm.verts.new((x,  w, z - h*0.5))
        v2 = bm.verts.new((x,  w*0.5, z + h*0.5))
        v3 = bm.verts.new((x, -w*0.5, z + h*0.5))
        layers.append([v0, v1, v2, v3])

    tip = bm.verts.new((0.80 * scale, 0, -0.56 * scale))
    for i in range(steps - 1):
        l1 = layers[i]
        l2 = layers[i+1]
        for k in range(4):
            bm.faces.new([l1[k], l1[(k+1)%4], l2[(k+1)%4], l2[k]])
    last = layers[-1]
    for k in range(4):
        bm.faces.new([last[k], last[(k+1)%4], tip])
    bm.faces.new([layers[0][3], layers[0][2], layers[0][1], layers[0][0]])

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = loc
    obj.rotation_euler = rot
    if mat:
        obj.data.materials.append(mat)
    apply_comic_styling(obj, bevel_w=0.006, outline=True, outline_w=0.020, cast_shadow=True)
    if registry is not None:
        registry.append(obj)
    return obj

def create_stylized_flame_tongue(name, loc, scale=(1,1,1), rot=(0,0,0), flame_type='orange', mats=None, registry=None):
    """
    Crea llamas estilizadas cómic 3D con silueta ondulada y contorno negro de tinta grueso (Pilar 03).
    Aplica shader con gradiente continuo (núcleo incandescente -> cuerpo saturado -> puntas afiladas).
    """
    mat_flame = mats["flame_cyan_procedural"] if flame_type == 'cyan' else mats["flame_orange_procedural"]

    bm = bmesh.new()
    ring_defs = [
        (0.00, 0.28, 0.20, 0.0),
        (0.35, 0.52, 0.32, 0.07),
        (0.75, 0.62, 0.36, -0.06),
        (1.15, 0.50, 0.28, 0.12),
        (1.55, 0.34, 0.18, 0.0),
        (1.95, 0.16, 0.09, -0.08)
    ]
    rings = []
    for z, rx, ry, off_x in ring_defs:
        ring = []
        for a in range(12):
            ang = a * 2.0 * math.pi / 12
            vx = (off_x + rx * math.cos(ang)) * scale[0]
            vy = (ry * math.sin(ang)) * scale[1]
            vz = z * scale[2]
            ring.append(bm.verts.new((vx, vy, vz)))
        rings.append(ring)

    tip = bm.verts.new((-0.14 * scale[0], 0, 2.25 * scale[2]))
    for i in range(len(rings) - 1):
        r1 = rings[i]
        r2 = rings[i+1]
        for k in range(12):
            bm.faces.new([r1[k], r1[(k+1)%12], r2[(k+1)%12], r2[k]])
    for k in range(12):
        bm.faces.new([rings[-1][k], rings[-1][(k+1)%12], tip])
    bm.faces.new(rings[0][::-1])

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = loc
    obj.rotation_euler = rot
    obj.data.materials.append(mat_flame)
    apply_comic_styling(obj, bevel_w=0.008, outline=True, outline_w=0.024, cast_shadow=False)
    if registry is not None:
        registry.append(obj)
    return obj

def create_circular_saw_blade(name, loc, radius=0.46, thickness=0.07, num_teeth=16, rot=(0,0,0), mat=None, registry=None):
    """Crea una sierra circular dentada con dientes afilados estilo cómic (Pilar 11)."""
    bm = bmesh.new()
    layers = []
    for z in [-thickness*0.5, thickness*0.5]:
        ring = []
        for i in range(num_teeth):
            ang_base = i * (2 * math.pi / num_teeth)
            ang_tip = ang_base + (math.pi / num_teeth) * 0.72
            ang_gullet = ang_base + (math.pi / num_teeth) * 1.06

            r_base = radius * 0.76
            r_tip = radius
            r_gullet = radius * 0.68

            vb = bm.verts.new((r_base * math.cos(ang_base), r_base * math.sin(ang_base), z))
            vt = bm.verts.new((r_tip * math.cos(ang_tip), r_tip * math.sin(ang_tip), z))
            vg = bm.verts.new((r_gullet * math.cos(ang_gullet), r_gullet * math.sin(ang_gullet), z))
            ring.extend([vb, vt, vg])
        layers.append(ring)

    n = len(layers[0])
    for i in range(n):
        v1 = layers[0][i]
        v2 = layers[0][(i+1)%n]
        v3 = layers[1][(i+1)%n]
        v4 = layers[1][i]
        bm.faces.new([v1, v2, v3, v4])

    bm.faces.new(layers[0])
    bm.faces.new(layers[1][::-1])

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = loc
    obj.rotation_euler = rot
    if mat:
        obj.data.materials.append(mat)
    apply_comic_styling(obj, bevel_w=0.006, outline=True, outline_w=0.020, cast_shadow=True)
    if registry is not None:
        registry.append(obj)
    return obj

# ==============================================================================
# 4. ENTIDAD 1: THE MECHANICAL WEREWOLF (LOBO MECÁNICO EN PASARELA)
# ==============================================================================
def create_sculpted_wolf_skull(name, loc, rot, mats, registry=None):
    """
    Crea el cráneo de lobo mecánico esculpido con postura depredadora frontal:
    - Bóveda craneal y mandíbula superior facetada que termina en el hocico afilado.
    - Mandíbula inferior articulada abierta en ángulo de 34° dejando cavidad bucal HUECA.
    - Interior bucal incandescente con fuego visible entre los colmillos metálicos.
    """
    bm = bmesh.new()

    sections = [
        (-0.35, 0.46, 0.42, 0.0, 0.20),
        ( 0.05, 0.44, 0.44, 0.0, 0.22),
        ( 0.35, 0.32, 0.34, 0.0, 0.16),
        ( 0.60, 0.22, 0.24, 0.0, 0.12),
        ( 0.80, 0.14, 0.16, 0.0, 0.08),
        ( 0.96, 0.08, 0.10, 0.0, 0.04)
    ]

    rings = []
    for x, top_w, top_z, bot_z, bot_w in sections:
        v0 = bm.verts.new((x, -top_w*0.5, top_z))
        v1 = bm.verts.new((x,  top_w*0.5, top_z))
        v2 = bm.verts.new((x,  top_w*0.7, top_z*0.35))
        v3 = bm.verts.new((x,  bot_w*0.5, bot_z))
        v4 = bm.verts.new((x, -bot_w*0.5, bot_z))
        v5 = bm.verts.new((x, -top_w*0.7, top_z*0.35))
        rings.append([v0, v1, v2, v3, v4, v5])

    for i in range(len(rings) - 1):
        r1 = rings[i]
        r2 = rings[i+1]
        for k in range(6):
            bm.faces.new([r1[k], r1[(k+1)%6], r2[(k+1)%6], r2[k]])
    bm.faces.new(rings[0][::-1])
    bm.faces.new(rings[-1])

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(f"{name}_UpperSkullMesh")
    bm.to_mesh(mesh)
    bm.free()

    upper_obj = bpy.data.objects.new(f"{name}_UpperSkull", mesh)
    bpy.context.collection.objects.link(upper_obj)
    upper_obj.location = loc
    upper_obj.rotation_euler = rot
    upper_obj.data.materials.append(mats["werewolf_steel"])
    apply_comic_styling(upper_obj, bevel_w=0.016, outline=True, outline_w=0.024)
    if registry is not None:
        registry.append(upper_obj)

    # Mandíbula inferior articulada abierta en ángulo de 34°
    bm_jaw = bmesh.new()
    jaw_sections = [
        (0.00, 0.30, 0.13),
        (0.30, 0.22, 0.11),
        (0.60, 0.14, 0.09),
        (0.85, 0.07, 0.06)
    ]
    j_rings = []
    for jx, jw, jh in jaw_sections:
        jv0 = bm_jaw.verts.new((jx, -jw*0.5, -jh))
        jv1 = bm_jaw.verts.new((jx,  jw*0.5, -jh))
        jv2 = bm_jaw.verts.new((jx,  jw*0.35,  0.0))
        jv3 = bm_jaw.verts.new((jx, -jw*0.35,  0.0))
        j_rings.append([jv0, jv1, jv2, jv3])

    for i in range(len(j_rings) - 1):
        r1 = j_rings[i]
        r2 = j_rings[i+1]
        for k in range(4):
            bm_jaw.faces.new([r1[k], r1[(k+1)%4], r2[(k+1)%4], r2[k]])
    bm_jaw.faces.new(j_rings[0][::-1])
    bm_jaw.faces.new(j_rings[-1])

    bmesh.ops.recalc_face_normals(bm_jaw, faces=bm_jaw.faces)
    jaw_mesh = bpy.data.meshes.new(f"{name}_JawMesh")
    bm_jaw.to_mesh(jaw_mesh)
    bm_jaw.free()

    jaw_obj = bpy.data.objects.new(f"{name}_Jaw", jaw_mesh)
    bpy.context.collection.objects.link(jaw_obj)
    jaw_obj.location = loc + Vector((0.08, 0, -0.06))
    jaw_obj.rotation_euler = (rot[0], rot[1] + R(34), rot[2])
    jaw_obj.data.materials.append(mats["dark_iron"])
    apply_comic_styling(jaw_obj, bevel_w=0.014, outline=True, outline_w=0.022)
    if registry is not None:
        registry.append(jaw_obj)

    # Interior bucal incandescente con lengua de fuego estilizada visible
    create_stylized_flame_tongue(f"{name}_OralFlame", loc + Vector((0.48, 0, -0.08)), scale=(0.34, 0.18, 0.32),
                                rot=(rot[0], rot[1] + R(65), rot[2]), flame_type='orange', mats=mats, registry=registry)

    # Colmillos metálicos afilados superiores e inferiores
    for sign_y in [-1, 1]:
        fang_u_p = loc + Vector((0.68, sign_y * 0.09, -0.02))
        bpy.ops.mesh.primitive_cone_add(radius1=0.038, depth=0.22, location=fang_u_p, rotation=(rot[0] + R(175), rot[1], rot[2]))
        f_u = bpy.context.active_object
        f_u.name = f"{name}_UpperFang_{sign_y}"
        f_u.data.materials.append(mats["bone_white"])
        apply_comic_styling(f_u, bevel_w=0.004, outline_w=0.012, cast_shadow=False)
        if registry is not None:
            registry.append(f_u)

        fang_l_p = loc + Vector((0.62, sign_y * 0.07, -0.20))
        bpy.ops.mesh.primitive_cone_add(radius1=0.032, depth=0.18, location=fang_l_p, rotation=(rot[0] + R(24), rot[1], rot[2]))
        f_l = bpy.context.active_object
        f_l.name = f"{name}_LowerFang_{sign_y}"
        f_l.data.materials.append(mats["bone_white"])
        apply_comic_styling(f_l, bevel_w=0.004, outline_w=0.012, cast_shadow=False)
        if registry is not None:
            registry.append(f_l)

    # Orejas lupinas mecánicas angulares erguidas y hacia atrás
    for ey_sgn in [-1, 1]:
        ear_p = loc + Vector((-0.20, ey_sgn * 0.28, 0.44))
        create_beveled_box(f"{name}_Ear_{ey_sgn}", ear_p, (0.30, 0.08, 0.42),
                           rot=(rot[0], rot[1] + R(-38), rot[2] + R(ey_sgn*20)),
                           mat=mats["werewolf_steel"], bevel_w=0.012, outline_w=0.020, registry=registry)

    # Ojos amarillos triangulares afilados
    for sgn, y in [(-1, -0.19), (1, 0.19)]:
        bm_e = bmesh.new()
        e0 = bm_e.verts.new((0.24, y, 0.09))
        e1 = bm_e.verts.new((0.44, y*0.85, 0.16))
        e2 = bm_e.verts.new((0.39, y*0.95, 0.07))
        bm_e.faces.new([e0, e1, e2] if sgn == 1 else [e0, e2, e1])
        bmesh.ops.recalc_face_normals(bm_e, faces=bm_e.faces)
        me = bpy.data.meshes.new(f"{name}_EyeMesh_{sgn}")
        bm_e.to_mesh(me)
        bm_e.free()
        e_obj = bpy.data.objects.new(f"{name}_Eye_{sgn}", me)
        bpy.context.collection.objects.link(e_obj)
        e_obj.location = loc
        e_obj.rotation_euler = rot
        e_obj.data.materials.append(mats["eye_yellow"])
        e_obj.visible_shadow = False
        if registry is not None:
            registry.append(e_obj)

def build_faithful_werewolf_beast(loc, mats, registry=None):
    base = Vector(loc)
    # Pose baja cuadrúpeda en acecho (Pilar 12)
    torso_pos = base + Vector((0.0, 0.0, 1.15))

    # 1. Torso, Pectorales esculpidos y Abdomen en acecho frontal
    create_beveled_box("Wolf_Chest", torso_pos, (1.05, 0.78, 0.85), rot=(0, R(12), 0), mat=mats["werewolf_steel"], bevel_w=0.03, outline_w=0.026, registry=registry)
    create_beveled_box("Wolf_Pectoral_L", torso_pos + Vector((0.42, 0.22, -0.15)), (0.48, 0.30, 0.42), rot=(0, R(22), R(-8)), mat=mats["dark_iron"], bevel_w=0.02, outline_w=0.022, registry=registry)
    create_beveled_box("Wolf_Pectoral_R", torso_pos + Vector((0.42, -0.22, -0.15)), (0.48, 0.30, 0.42), rot=(0, R(22), R(8)), mat=mats["dark_iron"], bevel_w=0.02, outline_w=0.022, registry=registry)

    ab_pos = torso_pos + Vector((-0.48, 0.0, -0.15))
    create_beveled_cylinder("Wolf_Abdomen", ab_pos, 0.32, 0.55, rot=(0, R(20), 0), mat=mats["dark_iron"], bevel_w=0.02, outline_w=0.022, registry=registry)
    pelvis_pos = ab_pos + Vector((-0.45, 0.0, -0.10))
    create_beveled_box("Wolf_Pelvis", pelvis_pos, (0.76, 0.58, 0.48), rot=(0, R(10), 0), mat=mats["werewolf_steel"], bevel_w=0.025, outline_w=0.024, registry=registry)

    for si, sx in enumerate([-0.08, -0.25, -0.42, -0.59, -0.76]):
        sp_pos = torso_pos + Vector((sx, 0.0, 0.46 - si*0.06))
        create_beveled_box(f"Wolf_Spine_{si}", sp_pos, (0.14, 0.30, 0.15), rot=(0, R(15), 0), mat=mats["dark_iron"], bevel_w=0.01, outline_w=0.016, cast_shadow=False, registry=registry)

    # 2. Tres Chimeneas Dorsales orientadas hacia arriba/atrás con llamas estilizadas (Pilar 03)
    exhaust_configs = [
        ((-0.28, -0.24, 0.55), (0, R(-48), R(-10))),
        ((-0.42, 0.0, 0.58), (0, R(-52), 0)),
        ((-0.28, 0.24, 0.55), (0, R(-48), R(10))),
    ]
    for i, (p_off, p_rot) in enumerate(exhaust_configs):
        pipe_pos = torso_pos + Vector(p_off)
        create_beveled_cylinder(f"Wolf_Exhaust_{i}", pipe_pos, 0.12, 0.75, rot=p_rot, mat=mats["dark_iron"], bevel_w=0.014, outline_w=0.022, registry=registry)
        create_beveled_cylinder(f"Wolf_Exhaust_Lip_{i}", pipe_pos + Vector((-0.18, 0.0, 0.28)), 0.14, 0.10, rot=p_rot, mat=mats["brass"], outline_w=0.016, cast_shadow=False, registry=registry)
        flame_pos = pipe_pos + Vector((-0.24, 0.0, 0.34))
        create_stylized_flame_tongue(f"Wolf_Flame_{i}", flame_pos, scale=(0.75, 0.44, 0.75), rot=(0, R(-48), 0), flame_type='orange', mats=mats, registry=registry)

    # 3. Cola Mecánica Segmentada hacia atrás con llama
    tail_base = pelvis_pos + Vector((-0.38, 0.0, 0.10))
    create_beveled_cylinder("Wolf_Tail_Seg1", tail_base + Vector((-0.25, 0.0, 0.04)), 0.08, 0.60, rot=(0, R(-68), 0), mat=mats["dark_iron"], outline_w=0.018, registry=registry)
    create_beveled_cylinder("Wolf_Tail_Seg2", tail_base + Vector((-0.55, 0.0, 0.18)), 0.065, 0.55, rot=(0, R(-80), 0), mat=mats["dark_iron"], outline_w=0.018, registry=registry)
    create_stylized_flame_tongue("Wolf_Tail_Flame", tail_base + Vector((-0.70, 0.0, 0.24)), scale=(0.48, 0.32, 0.48), rot=(0, R(-80), 0), flame_type='orange', mats=mats, registry=registry)

    # 4. Cabeza Lupina Angular Esculpida encarada hacia adelante-abajo (postura de acecho)
    head_pos = torso_pos + Vector((0.82, 0.0, 0.05))
    create_beveled_cylinder("Wolf_Neck", (torso_pos + head_pos)*0.5, 0.24, 0.65, rot=(0, R(18), 0), mat=mats["dark_iron"], outline_w=0.022, registry=registry)
    create_beveled_cylinder("Wolf_Neck_Collar", head_pos + Vector((-0.20, 0, -0.06)), 0.28, 0.14, rot=(0, R(18), 0), mat=mats["brass"], outline_w=0.018, cast_shadow=False, registry=registry)

    create_sculpted_wolf_skull("Wolf_Head_Sculpted", head_pos, (0, R(-12), R(10)), mats, registry=registry)

    # 5. Extremidades Superiores con Garras Cartoon Apoyadas en la Pasarela (Pilar 05, Z=0.35)
    for arm_sgn, ay in [(1, 0.44), (-1, -0.44)]:
        shoulder_p = torso_pos + Vector((0.28, ay, 0.16))
        create_beveled_box(f"Wolf_Shoulder_Armor_{arm_sgn}", shoulder_p, (0.45, 0.40, 0.45), rot=(0, R(15), R(arm_sgn*15)), mat=mats["werewolf_steel"], bevel_w=0.02, outline_w=0.022, registry=registry)

        elbow_p = shoulder_p + Vector((0.35, ay*0.20, -0.72))
        create_beveled_cylinder(f"Wolf_Bicep_{arm_sgn}", (shoulder_p + elbow_p)*0.5, 0.14, 0.78, rot=(0, R(28), 0), mat=mats["dark_iron"], outline_w=0.020, registry=registry)
        create_hydraulic_piston(f"Wolf_Elbow_Pist_{arm_sgn}", shoulder_p + Vector((-0.08, 0, -0.10)), elbow_p,
                                cyl_r=0.042, rod_r=0.024, mat_cyl=mats["dark_iron"], mat_rod=mats["brass"], registry=registry)

        wrist_p = elbow_p + Vector((0.26, 0.0, -0.52))
        create_beveled_cylinder(f"Wolf_Forearm_{arm_sgn}", (elbow_p + wrist_p)*0.5, 0.13, 0.80, rot=(0, R(22), 0), mat=mats["werewolf_steel"], outline_w=0.020, registry=registry)
        create_beveled_box(f"Wolf_Palm_{arm_sgn}", wrist_p, (0.28, 0.28, 0.14), rot=(0, R(10), 0), mat=mats["dark_iron"], outline_w=0.020, registry=registry)

        for ci, c_off in enumerate([-0.18, -0.06, 0.06, 0.18]):
            claw_p = wrist_p + Vector((0.14, c_off*0.78, -0.06))
            create_cartoon_claw(f"Wolf_Claw_{arm_sgn}_{ci}", claw_p, (0, R(12), R(c_off*25)), scale=1.35, mat=mats["dark_iron"], registry=registry)

    # 6. Patas Traseras Digitígradas con Pistón en Rodilla y Garras en Suelo
    for leg_sgn, ly in [(1, 0.38), (-1, -0.38)]:
        hip_p = pelvis_pos + Vector((-0.12, ly, -0.08))
        create_beveled_cylinder(f"Wolf_Hip_{leg_sgn}", hip_p, 0.19, 0.24, rot=(R(90), 0, 0), mat=mats["dark_iron"], outline_w=0.020, registry=registry)

        knee_p = hip_p + Vector((-0.45, ly*0.15, -0.50))
        create_beveled_cylinder(f"Wolf_Femur_{leg_sgn}", (hip_p + knee_p)*0.5, 0.15, 0.85, rot=(0, R(-44), 0), mat=mats["werewolf_steel"], outline_w=0.020, registry=registry)
        create_hydraulic_piston(f"Wolf_Knee_Pist_{leg_sgn}", hip_p + Vector((0.16, 0, 0)), knee_p,
                                cyl_r=0.044, rod_r=0.025, mat_cyl=mats["dark_iron"], mat_rod=mats["brass"], registry=registry)

        ankle_p = knee_p + Vector((0.54, 0.0, -0.52))
        create_beveled_cylinder(f"Wolf_Shin_{leg_sgn}", (knee_p + ankle_p)*0.5, 0.13, 0.94, rot=(0, R(48), 0), mat=mats["werewolf_steel"], outline_w=0.020, registry=registry)
        create_hydraulic_piston(f"Wolf_Ankle_Pist_{leg_sgn}", knee_p + Vector((-0.10, 0, -0.15)), ankle_p,
                                cyl_r=0.040, rod_r=0.022, mat_cyl=mats["dark_iron"], mat_rod=mats["brass"], registry=registry)

        foot_p = ankle_p + Vector((0.14, 0.0, -0.12))
        create_beveled_box(f"Wolf_Foot_{leg_sgn}", foot_p, (0.46, 0.36, 0.15), rot=(0, 0, 0), mat=mats["dark_iron"], outline_w=0.020, registry=registry)
        for fi, fy in enumerate([-0.12, 0.0, 0.12]):
            f_claw_p = foot_p + Vector((0.28, fy, -0.06))
            create_cartoon_claw(f"Wolf_FootClaw_{leg_sgn}_{fi}", f_claw_p, (0, R(15), 0), scale=1.1, mat=mats["dark_iron"], registry=registry)

# ==============================================================================
# 5. ENTIDAD 2: AUDITOR DRONE (ESFERA FLOTANTE, 3 MANÓMETROS, LENTE ROJA Y CRT)
# ==============================================================================
def create_integrated_analog_gauge(name, loc, rot_euler, mats, registry=None):
    """
    Crea un manómetro analógico 3D integrado (Pilar 07):
    Cilindro con bisel dorado y cara frontal texturizada UV con el dial analógico blanco.
    """
    bm = bmesh.new()
    radius = 0.18
    depth = 0.09
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=24,
                          radius1=radius, radius2=radius, depth=depth)
    uv_layer = bm.loops.layers.uv.new("UVMap")

    bm.faces.ensure_lookup_table()
    top_face = None
    for face in bm.faces:
        if face.normal.z > 0.8:
            top_face = face
            for loop in face.loops:
                v = loop.vert.co
                loop[uv_layer].uv = ((v.x / (2.0 * radius)) + 0.5, (v.y / (2.0 * radius)) + 0.5)

    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = loc
    obj.rotation_euler = rot_euler

    obj.data.materials.append(mats["brass"])
    obj.data.materials.append(mats["dial_mat"])

    if top_face:
        for poly in obj.data.polygons:
            if poly.normal.z > 0.8:
                poly.material_index = 1

    apply_comic_styling(obj, bevel_w=0.006, outline=True, outline_w=0.018, cast_shadow=False)
    if registry is not None:
        registry.append(obj)
    return obj

def build_faithful_auditor_drone(loc, mats, registry=None):
    base = Vector(loc)

    # 1. Chasis esférico de gunmetal con anillo ecuatorial y remaches (Pilar 07)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.78, location=base)
    orb = bpy.context.active_object
    orb.name = "Auditor_Sphere"
    orb.data.materials.append(mats["drone_hull"])
    apply_comic_styling(orb, bevel_w=0.014, outline_w=0.024)
    if registry is not None:
        registry.append(orb)

    bpy.ops.mesh.primitive_torus_add(major_radius=0.79, minor_radius=0.032, location=base)
    rim = bpy.context.active_object
    rim.name = "Auditor_Rim"
    rim.data.materials.append(mats["dark_iron"])
    apply_comic_styling(rim, bevel_w=0.006, outline_w=0.016, cast_shadow=False)
    if registry is not None:
        registry.append(rim)

    for a in range(0, 360, 24):
        rad = math.radians(a)
        r_pos = base + Vector((0.79*math.cos(rad), 0.79*math.sin(rad), 0))
        create_beveled_cylinder(f"Auditor_Rivet_{a}", r_pos, 0.026, 0.06, rot=(0, R(90), rad), mat=mats["brass"], bevel_w=0.003, outline_w=0.010, cast_shadow=False, registry=registry)

    # 2. Tres Manómetros Analógicos en el Arco Superior encarados directamente a la cámara (Pilar 07)
    for i, g_rot in enumerate([-28, 0, 28]):
        grad = math.radians(g_rot)
        g_pos = base + Vector((0.36*math.sin(grad), -0.54*math.cos(grad*0.5), 0.54 + 0.03*math.cos(grad)))
        rot_bezel = (R(55), 0, R(g_rot*0.8))
        create_integrated_analog_gauge(f"Auditor_Gauge_{i}", g_pos, rot_bezel, mats, registry=registry)

    # Tuberías y antenas curvadas en la cúpula
    create_beveled_cylinder("Auditor_Antenna_1", base + Vector((-0.20, 0.06, 0.90)), 0.018, 0.72, rot=(R(-15), R(-20), 0), mat=mats["dark_iron"], outline_w=0.014, cast_shadow=False, registry=registry)
    create_beveled_cylinder("Auditor_Antenna_2", base + Vector((0.25, 0.10, 0.88)), 0.016, 0.76, rot=(R(-10), R(25), 0), mat=mats["dark_iron"], outline_w=0.014, cast_shadow=False, registry=registry)

    # 3. Pantalla CRT Verde de Telemetría (Frontal-Izquierda, orientada hacia el observador)
    crt_pos = base + Vector((-0.38, -0.66, -0.02))
    crt_rot = (R(12), 0, R(-15))
    create_beveled_box("CRT_Housing", crt_pos, (0.44, 0.18, 0.44), rot=crt_rot, mat=mats["dark_iron"], outline_w=0.020, cast_shadow=False, registry=registry)

    bm_crt = bmesh.new()
    cw, ch = 0.19, 0.19
    v0 = bm_crt.verts.new((-cw, 0, -ch))
    v1 = bm_crt.verts.new(( cw, 0, -ch))
    v2 = bm_crt.verts.new(( cw, 0,  ch))
    v3 = bm_crt.verts.new((-cw, 0,  ch))
    bm_crt.faces.new([v0, v1, v2, v3])
    uv_crt = bm_crt.loops.layers.uv.new("UVMap")
    uv_coords = [(0,0), (1,0), (1,1), (0,1)]
    for face in bm_crt.faces:
        for idx, loop in enumerate(face.loops):
            loop[uv_crt].uv = uv_coords[idx]
    m_crt = bpy.data.meshes.new("CRT_Screen_Mesh")
    bm_crt.to_mesh(m_crt)
    bm_crt.free()

    crt_screen_obj = bpy.data.objects.new("CRT_Screen_Face", m_crt)
    bpy.context.collection.objects.link(crt_screen_obj)
    crt_screen_obj.location = crt_pos + Vector((0, -0.098, 0))
    crt_screen_obj.rotation_euler = crt_rot
    crt_screen_obj.data.materials.append(mats["crt_mat"])
    crt_screen_obj.visible_shadow = False
    if registry is not None:
        registry.append(crt_screen_obj)

    # 4. Ojo Óptico Ciclópeo (Frontal-Derecho) y Cilindro Óptico Saliente (Pilar 06)
    eye_pos = base + Vector((0.38, -0.68, 0.02))
    create_beveled_cylinder("Lens_Bezel_Base", eye_pos, 0.35, 0.20, rot=(R(90), 0, 0), mat=mats["brass"], outline_w=0.020, cast_shadow=False, registry=registry)
    create_beveled_cylinder("Lens_Bezel_Ring", eye_pos + Vector((0, -0.12, 0)), 0.29, 0.12, rot=(R(90), 0, 0), mat=mats["dark_iron"], outline_w=0.016, cast_shadow=False, registry=registry)
    create_beveled_cylinder("Lens_Bezel_Inner", eye_pos + Vector((0, -0.18, 0)), 0.25, 0.08, rot=(R(90), 0, 0), mat=mats["brass"], outline_w=0.014, cast_shadow=False, registry=registry)

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.21, location=eye_pos + Vector((0, -0.21, 0)))
    lens = bpy.context.active_object
    lens.name = "Auditor_Eye_Red"
    lens.scale = (1.0, 0.65, 1.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    lens.data.materials.append(mats["eye_red"])
    apply_comic_styling(lens, bevel_w=0.006, outline_w=0.016, cast_shadow=False)
    if registry is not None:
        registry.append(lens)

    create_beveled_cylinder("Auditor_Pupil", eye_pos + Vector((0, -0.33, 0)), 0.08, 0.02, rot=(R(90), 0, 0), mat=mats["dark_iron"], outline=False, cast_shadow=False, registry=registry)
    create_beveled_box("Auditor_Status_LED", eye_pos + Vector((0, 0.08, -0.35)), (0.14, 0.06, 0.06), mat=mats["led_green"], outline=False, cast_shadow=False, registry=registry)

    # 5. Cono de Escaneo Rojo Translúcido Proyectado al Suelo hacia la derecha (Pilar 17)
    cone_pos = eye_pos + Vector((0.18, -0.45, -0.85))
    bpy.ops.mesh.primitive_cone_add(radius1=0.05, radius2=0.45, depth=1.85, location=cone_pos, rotation=(R(28), R(16), 0))
    scan_cone = bpy.context.active_object
    scan_cone.name = "Auditor_Scan_Beam"
    scan_cone.data.materials.append(mats["scan_cone"])
    scan_cone.visible_shadow = False
    if registry is not None:
        registry.append(scan_cone)

    # 6. Toberas de Empuje Laterales e Inferior y Cables Colgantes (Pilar 14)
    for tsgn, tx in [(-1, -0.76), (1, 0.76)]:
        create_beveled_cylinder(f"Auditor_Thruster_{tsgn}", base + Vector((tx, 0.0, 0.0)), 0.20, 0.24, rot=(0, R(90), 0), mat=mats["brass"], outline_w=0.020, cast_shadow=False, registry=registry)
    create_beveled_cylinder("Auditor_Thruster_Bottom", base + Vector((0, 0, -0.76)), 0.24, 0.25, rot=(0, 0, 0), mat=mats["brass"], outline_w=0.020, cast_shadow=False, registry=registry)

    for cy_off in [-0.15, 0.15]:
        create_beveled_cylinder(f"Auditor_Wire_{cy_off}", base + Vector((0.0, cy_off, -0.92)), 0.016, 0.36, rot=(R(15), 0, 0), mat=mats["dark_iron"], outline_w=0.012, cast_shadow=False, registry=registry)

# ==============================================================================
# 6. ENTIDAD 3: SCRAPPER GOBLIN (TRASGO CHATARRERO EN PRIMER PLANO)
# ==============================================================================
def create_sculpted_skull_mask(name, loc, rot, mats, registry=None):
    """
    Crea la máscara de calavera de hueso esculpida (Pilar 08, 09, 10):
    - Color marfil hueso auténtico (M_Bone_White).
    - Ojo derecho hundido con pupila roja emisiva.
    - Ojo izquierdo con monóculo telescópico dorado escalonado y lente amarilla.
    - Cuernos de tubos curvados y dientes tallados.
    """
    bm = bmesh.new()

    skull_layers = [
        ( 0.28, 0.22, 0.22),
        ( 0.14, 0.27, 0.27),
        (-0.06, 0.28, 0.24),
        (-0.20, 0.22, 0.18),
        (-0.30, 0.16, 0.14),
    ]

    rings = []
    for z, wx, wy in skull_layers:
        v0 = bm.verts.new((-wx*0.7, -wy, z))
        v1 = bm.verts.new(( wx*0.7, -wy, z))
        v2 = bm.verts.new(( wx,     -wy*0.3, z))
        v3 = bm.verts.new(( wx*0.9,  wy*0.8, z))
        v4 = bm.verts.new((-wx*0.9,  wy*0.8, z))
        v5 = bm.verts.new((-wx,     -wy*0.3, z))
        rings.append([v0, v1, v2, v3, v4, v5])

    for i in range(len(rings) - 1):
        r1 = rings[i]
        r2 = rings[i+1]
        for k in range(6):
            bm.faces.new([r1[k], r1[(k+1)%6], r2[(k+1)%6], r2[k]])
    bm.faces.new(rings[0])
    bm.faces.new(rings[-1][::-1])

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(f"{name}_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    skull_obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(skull_obj)
    skull_obj.location = loc
    skull_obj.rotation_euler = rot
    skull_obj.data.materials.append(mats["bone_white"])
    apply_comic_styling(skull_obj, bevel_w=0.022, outline=True, outline_w=0.024)
    if registry is not None:
        registry.append(skull_obj)

    # Cuernos de tubos curvados hacia atrás en la nuca (Pilar 09)
    horn_pts = [
        ((-0.15, 0.16, 0.30), (R(-35), R(-25), 0)),
        (( 0.00, 0.20, 0.34), (R(-40), 0, 0)),
        (( 0.15, 0.16, 0.30), (R(-35), R(25), 0))
    ]
    for hi, (hp, hr) in enumerate(horn_pts):
        create_beveled_cylinder(f"{name}_Horn_{hi}", loc + Vector(hp), 0.044, 0.40, rot=hr, mat=mats["dark_iron"], outline_w=0.016, cast_shadow=False, registry=registry)

    # Dientes cuadrados tallados en la mandíbula inferior
    for ti, tx in enumerate([-0.11, -0.05, 0.0, 0.05, 0.11]):
        t_pos = loc + Vector((tx, -0.24, -0.28))
        create_beveled_box(f"{name}_Tooth_{ti}", t_pos, (0.044, 0.04, 0.07), rot=rot, mat=mats["bone_white"], bevel_w=0.004, outline_w=0.010, cast_shadow=False, registry=registry)

    # Orejas de duende de chapa metálica en los costados
    for ear_sgn, ex in [(-1, -0.30), (1, 0.30)]:
        ear_p = loc + Vector((ex, 0.04, 0.06))
        create_beveled_box(f"{name}_Ear_{ear_sgn}", ear_p, (0.05, 0.25, 0.19),
                           rot=(rot[0], rot[1] + R(ear_sgn*30), rot[2]), mat=mats["scrapper_steel"], bevel_w=0.008, outline_w=0.016, cast_shadow=False, registry=registry)

    # Ojo Derecho: Hundido, oscuro con pupila roja (Pilar 10)
    eye_r_pos = loc + Vector((-0.15, -0.28, 0.04))
    create_beveled_cylinder(f"{name}_EyeSocketR", eye_r_pos, 0.10, 0.07, rot=(R(90), 0, 0), mat=mats["dark_iron"], outline=False, cast_shadow=False, registry=registry)
    create_beveled_cylinder(f"{name}_EyePupilR", eye_r_pos + Vector((0, -0.035, 0)), 0.030, 0.030, rot=(R(90), 0, 0), mat=mats["eye_red"], outline=False, cast_shadow=False, registry=registry)

    # Ojo Izquierdo: MONÓCULO TELESCÓPICO DORADO GIGANTE ESCALONADO (Pilar 10)
    eye_l_pos = loc + Vector((0.16, -0.28, 0.04))
    create_beveled_cylinder(f"{name}_LensBase", eye_l_pos, 0.25, 0.22, rot=(R(90), 0, 0), mat=mats["brass"], outline_w=0.022, cast_shadow=False, registry=registry)
    create_beveled_cylinder(f"{name}_LensRim2", eye_l_pos + Vector((0, -0.11, 0)), 0.21, 0.13, rot=(R(90), 0, 0), mat=mats["dark_iron"], outline_w=0.018, cast_shadow=False, registry=registry)
    create_beveled_cylinder(f"{name}_LensRim3", eye_l_pos + Vector((0, -0.15, 0)), 0.17, 0.09, rot=(R(90), 0, 0), mat=mats["brass"], outline_w=0.014, cast_shadow=False, registry=registry)
    create_beveled_cylinder(f"{name}_BigEyeGlow", eye_l_pos + Vector((0, -0.18, 0)), 0.15, 0.05, rot=(R(90), 0, 0), mat=mats["eye_yellow"], outline=False, cast_shadow=False, registry=registry)

    create_beveled_box(f"{name}_BrowRidge", loc + Vector((0.02, -0.30, 0.18)), (0.48, 0.08, 0.10), rot=rot, mat=mats["bone_white"], outline_w=0.016, cast_shadow=False, registry=registry)
    create_beveled_box(f"{name}_NoseCavity", loc + Vector((0.01, -0.28, -0.07)), (0.09, 0.05, 0.09), mat=mats["dark_iron"], outline=False, cast_shadow=False, registry=registry)

def build_faithful_scrapper_goblin(loc, mats, registry=None):
    base = Vector(loc)
    torso_pos = base + Vector((0.0, 0.0, 0.88))

    # 1. Torso de Chapas Remachadas con Hebilla de Engranaje de bronce envejecido (Pilar 11)
    create_beveled_box("Goblin_Torso", torso_pos, (0.60, 0.46, 0.70), rot=(0, R(-6), R(12)), mat=mats["scrapper_steel"], bevel_w=0.025, outline_w=0.022, registry=registry)

    for s_sgn, sx in [(-1, -0.36), (1, 0.36)]:
        create_beveled_box(f"Goblin_ShoulderPlate_{s_sgn}", torso_pos + Vector((sx, 0.0, 0.30)), (0.30, 0.32, 0.15),
                           rot=(0, R(s_sgn*20), R(12)), mat=mats["dark_iron"], outline_w=0.018, registry=registry)

    create_beveled_box("Goblin_Strap_1", torso_pos + Vector((0.0, -0.24, 0.08)), (0.54, 0.05, 0.11), rot=(0, 0, R(35)), mat=mats["dark_iron"], outline=False, cast_shadow=False, registry=registry)

    # Hebilla de cinturón: Engranaje de bronce oxidado (NO emisivo)
    cog_pos = torso_pos + Vector((0.02, -0.26, -0.20))
    create_beveled_cylinder("Goblin_Belt_Cog", cog_pos, 0.22, 0.10, rot=(R(90), 0, 0), mat=mats["bronze_weathered"], outline_w=0.020, cast_shadow=False, registry=registry)
    for a in range(0, 360, 45):
        rad = math.radians(a)
        tp = cog_pos + Vector((0.23*math.cos(rad), 0, 0.23*math.sin(rad)))
        create_beveled_box(f"Belt_Tooth_{a}", tp, (0.07, 0.08, 0.07), rot=(0, rad, 0), mat=mats["bronze_weathered"], bevel_w=0.005, outline_w=0.012, cast_shadow=False, registry=registry)

    # 2. Cabeza: Máscara de Calavera de Hueso Esculpida (Pilar 08, 09, 10)
    head_pos = torso_pos + Vector((0.04, -0.05, 0.64))
    create_sculpted_skull_mask("Goblin_Skull_Mask", head_pos, (0, R(-8), R(12)), mats, registry=registry)

    # 3. Brazo Derecho portando Maza con Pinchos
    r_arm_sh = torso_pos + Vector((-0.36, 0.0, 0.24))
    r_elbow = r_arm_sh + Vector((-0.22, -0.19, 0.02))
    create_beveled_cylinder("Goblin_Bicep_R", (r_arm_sh + r_elbow)*0.5, 0.085, 0.36, rot=(R(-30), R(-35), 0), mat=mats["dark_iron"], outline_w=0.016, registry=registry)

    mace_hand = r_elbow + Vector((-0.13, -0.24, 0.08))
    create_beveled_cylinder("Goblin_Forearm_R", (r_elbow + mace_hand)*0.5, 0.08, 0.34, rot=(R(-25), R(20), 0), mat=mats["dark_iron"], outline_w=0.016, registry=registry)

    mace_dir = Vector((-0.15, -0.12, 0.44)).normalized()
    mace_head = mace_hand + mace_dir * 0.42
    shaft_bot = mace_hand - mace_dir * 0.38
    create_beveled_cylinder("Goblin_Mace_Shaft", (mace_head + shaft_bot)*0.5, 0.040, 0.84, rot=(R(-30), R(40), 0), mat=mats["dark_iron"], outline_w=0.016, cast_shadow=False, registry=registry)

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.20, location=mace_head)
    mace_orb = bpy.context.active_object
    mace_orb.name = "Goblin_Mace_Orb"
    mace_orb.data.materials.append(mats["dark_iron"])
    apply_comic_styling(mace_orb, bevel_w=0.008, outline_w=0.016, cast_shadow=False)
    if registry is not None:
        registry.append(mace_orb)

    for pi, (pdx, pdy, pdz) in enumerate([
        (0.20, 0, 0), (-0.20, 0, 0), (0, 0.20, 0), (0, -0.20, 0),
        (0, 0, 0.20), (0, 0, -0.20), (0.15, 0.15, 0.15), (-0.15, 0.15, -0.15),
        (0.15, -0.15, -0.15), (-0.15, -0.15, 0.15), (0.15, 0.15, -0.15), (-0.15, -0.15, -0.15)
    ]):
        bpy.ops.mesh.primitive_cone_add(radius1=0.044, depth=0.20, location=mace_head + Vector((pdx, pdy, pdz)))
        spike = bpy.context.active_object
        spike.name = f"Mace_Spike_{pi}"
        spike.data.materials.append(mats["brass"])
        apply_comic_styling(spike, bevel_w=0.004, outline_w=0.010, cast_shadow=False)
        if registry is not None:
            registry.append(spike)

    # 4. Brazo Izquierdo con SIERRA CIRCULAR DENTADA DE ACERO (Orientada hacia cámara)
    l_arm_sh = torso_pos + Vector((0.36, -0.10, 0.16))
    l_elbow = l_arm_sh + Vector((0.19, -0.21, -0.05))
    create_beveled_cylinder("Goblin_Bicep_L", (l_arm_sh + l_elbow)*0.5, 0.085, 0.34, rot=(R(35), R(30), 0), mat=mats["dark_iron"], outline_w=0.016, registry=registry)

    l_hand = l_elbow + Vector((0.13, -0.25, -0.10))
    create_beveled_cylinder("Goblin_Forearm_L", (l_elbow + l_hand)*0.5, 0.08, 0.30, rot=(R(35), R(15), 0), mat=mats["dark_iron"], outline_w=0.016, registry=registry)

    saw_pos = l_hand + Vector((0, -0.08, 0))
    create_circular_saw_blade("Goblin_Shield_SawBlade", saw_pos, radius=0.46, thickness=0.07, num_teeth=16, rot=(R(8), R(22), R(5)), mat=mats["scrapper_steel"], registry=registry)
    create_beveled_cylinder("Goblin_Saw_Hub", saw_pos, 0.15, 0.10, rot=(R(8), R(22), R(5)), mat=mats["brass"], outline_w=0.014, cast_shadow=False, registry=registry)

    # 5. Piernas Mecánicas Articuladas
    for l_sgn, lx in [(-1, -0.23), (1, 0.23)]:
        hip_p = torso_pos + Vector((lx, 0.0, -0.36))
        knee_p = hip_p + Vector((lx*0.09, -0.12, -0.34))
        create_beveled_cylinder(f"Goblin_Thigh_{l_sgn}", (hip_p + knee_p)*0.5, 0.09, 0.42, rot=(R(20), 0, R(l_sgn*15)), mat=mats["dark_iron"], outline_w=0.016, registry=registry)

        foot_p = knee_p + Vector((0, -0.06, -0.30))
        create_beveled_cylinder(f"Goblin_Shin_{l_sgn}", (knee_p + foot_p)*0.5, 0.08, 0.38, rot=(0, 0, 0), mat=mats["scrapper_steel"], outline_w=0.016, registry=registry)
        create_beveled_box(f"Goblin_Boot_{l_sgn}", foot_p + Vector((0, -0.08, 0)), (0.22, 0.36, 0.13), rot=(0, 0, R(l_sgn*15)), mat=mats["dark_iron"], outline_w=0.016, registry=registry)

# ==============================================================================
# 7. ENTIDAD 4: CEILING SPIDER-BOT (ARAÑA DE CONDUCTOS COLGADA CON PISTONES)
# ==============================================================================
def build_faithful_ceiling_spider(loc, mats, registry=None):
    base = Vector(loc)

    # 1. Chasis mecánico anguloso verde oliva (Pilar 14, 15)
    create_beveled_box("Spider_Chassis", base, (0.84, 0.74, 0.44), rot=(R(15), 0, R(-12)), mat=mats["spider_olive"], bevel_w=0.025, outline_w=0.022, registry=registry)

    # 2. Tres celdas de energía cilíndricas verdes brillantes en el lomo (Pilar 16)
    for bi, bx_off in enumerate([-0.26, 0.0, 0.26]):
        b_pos = base + Vector((bx_off, 0.05, 0.28))
        create_beveled_cylinder(f"Spider_Battery_{bi}", b_pos, 0.10, 0.48, rot=(R(90), 0, 0), mat=mats["led_green"], outline=False, cast_shadow=False, registry=registry)
        create_beveled_cylinder(f"Spider_Bat_Cap_{bi}_1", b_pos + Vector((0, -0.25, 0)), 0.105, 0.05, rot=(R(90), 0, 0), mat=mats["brass"], outline_w=0.012, cast_shadow=False, registry=registry)
        create_beveled_cylinder(f"Spider_Bat_Cap_{bi}_2", b_pos + Vector((0, 0.25, 0)), 0.105, 0.05, rot=(R(90), 0, 0), mat=mats["brass"], outline_w=0.012, cast_shadow=False, registry=registry)

    # 3. Cabeza inclinada hacia el suelo con ojo ciclópeo verde emisivo (Pilar 06, 10)
    head_pos = base + Vector((0.0, -0.40, -0.20))
    create_beveled_box("Spider_Head", head_pos, (0.40, 0.34, 0.30), rot=(R(38), 0, R(-12)), mat=mats["dark_iron"], outline_w=0.018, cast_shadow=False, registry=registry)
    create_beveled_box("Spider_Eye_Lens", head_pos + Vector((0, -0.18, -0.04)), (0.20, 0.04, 0.20), rot=(R(38), 0, R(-12)), mat=mats["led_green"], outline=False, cast_shadow=False, registry=registry)

    # 4. Cuatro patas mecánicas articuladas con garras depredadoras (Pilar 14, 15)
    leg_anchors = [
        (-0.38, -0.26, math.radians(-35), True),
        ( 0.38, -0.26, math.radians( 35), True),
        (-0.38,  0.30, math.radians(-125), False),
        ( 0.38,  0.30, math.radians( 125), False)
    ]
    for lx, ly, ang, is_front in leg_anchors:
        root_p = base + Vector((lx, ly, 0.08))
        create_beveled_cylinder(f"Spider_Hip_{lx}_{ly}", root_p, 0.09, 0.15, mat=mats["brass"], outline_w=0.016, cast_shadow=False, registry=registry)

        if is_front:
            mid_p = root_p + Vector((0.76*math.cos(ang), 0.76*math.sin(ang), -0.60))
            create_beveled_cylinder(f"Spider_Femur_{lx}_{ly}", (root_p + mid_p)*0.5, 0.055, 1.12, rot=(R(30), R(ang), 0), mat=mats["spider_olive"], outline_w=0.016, cast_shadow=False, registry=registry)
            create_hydraulic_piston(f"Spider_Leg_Pist_{lx}_{ly}", root_p, mid_p, cyl_r=0.028, rod_r=0.015, mat_cyl=mats["dark_iron"], mat_rod=mats["brass"], registry=registry)

            end_p = mid_p + Vector((0.60*math.cos(ang), 0.60*math.sin(ang), -0.74))
            create_beveled_cylinder(f"Spider_Tibia_{lx}_{ly}", (mid_p + end_p)*0.5, 0.046, 1.14, rot=(R(45), R(ang), 0), mat=mats["spider_olive"], outline_w=0.016, cast_shadow=False, registry=registry)
            create_cartoon_claw(f"Spider_Claw_{lx}_{ly}", end_p, (0, R(85), ang), scale=0.55, mat=mats["brass"], registry=registry)
        else:
            mid_p = root_p + Vector((0.62*math.cos(ang), 0.62*math.sin(ang), 0.35))
            create_beveled_cylinder(f"Spider_Femur_{lx}_{ly}", (root_p + mid_p)*0.5, 0.052, 0.90, rot=(R(-25), R(ang), 0), mat=mats["spider_olive"], outline_w=0.016, cast_shadow=False, registry=registry)
            end_p = mid_p + Vector((0.50*math.cos(ang), 0.50*math.sin(ang), 0.42))
            create_beveled_cylinder(f"Spider_Tibia_{lx}_{ly}", (mid_p + end_p)*0.5, 0.044, 0.86, rot=(R(-40), R(ang), 0), mat=mats["spider_olive"], outline_w=0.016, cast_shadow=False, registry=registry)
            create_cartoon_claw(f"Spider_Claw_{lx}_{ly}", end_p, (0, R(-35), ang), scale=0.46, mat=mats["brass"], registry=registry)

# ==============================================================================
# 8. ENTIDAD 5: CINDER SPIRIT & HORNO ARDIENTE (TITÁN DE MAGMA + MELENA CIAN)
# ==============================================================================
def create_sculpted_titan_helmet(name, loc, rot, mats, registry=None):
    """
    Crea el casco de titán esculpido, mandíbula angular en cuña,
    ranuras de ojos de magma ardiente \ / y crestas de armadura.
    """
    bm = bmesh.new()

    h_sections = [
        ( 0.30, 0.46, 0.38),
        ( 0.14, 0.50, 0.44),
        (-0.06, 0.44, 0.40),
        (-0.25, 0.34, 0.30),
        (-0.40, 0.24, 0.20)
    ]
    h_rings = []
    for z, wx, wy in h_sections:
        v0 = bm.verts.new((-wx*0.6, -wy*0.8, z))
        v1 = bm.verts.new(( wx*0.6, -wy*0.8, z))
        v2 = bm.verts.new(( wx*0.9, -wy*0.2, z))
        v3 = bm.verts.new(( wx*0.8,  wy*0.7, z))
        v4 = bm.verts.new((-wx*0.8,  wy*0.7, z))
        v5 = bm.verts.new((-wx*0.9, -wy*0.2, z))
        h_rings.append([v0, v1, v2, v3, v4, v5])

    for i in range(len(h_rings) - 1):
        r1 = h_rings[i]
        r2 = h_rings[i+1]
        for k in range(6):
            bm.faces.new([r1[k], r1[(k+1)%6], r2[(k+1)%6], r2[k]])
    bm.faces.new(h_rings[0][::-1])
    bm.faces.new(h_rings[-1])

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    m_helm = bpy.data.meshes.new(f"{name}_Mesh")
    bm.to_mesh(m_helm)
    bm.free()

    helm_obj = bpy.data.objects.new(name, m_helm)
    bpy.context.collection.objects.link(helm_obj)
    helm_obj.location = loc
    helm_obj.rotation_euler = rot
    helm_obj.data.materials.append(mats["titan_armor"])
    apply_comic_styling(helm_obj, bevel_w=0.02, outline_w=0.024)
    if registry is not None:
        registry.append(helm_obj)

    # DOS OJOS RASGADOS DE MAGMA ARDIENTE INCANDESCENTE (\ /)
    eye_pts = [
        ((-0.14, -0.28, 0.05), (R(12), R(-18), rot[2])),
        (( 0.14, -0.28, 0.05), (R(12), R( 18), rot[2]))
    ]
    for ei, (ep, er) in enumerate(eye_pts):
        create_beveled_box(f"{name}_Eye_{ei}", loc + Vector(ep), (0.15, 0.05, 0.09), rot=er,
                           mat=mats["flame_yellow_core"], outline=False, cast_shadow=False, registry=registry)

    # Collarín de magma en el cuello
    create_beveled_box(f"{name}_NeckMagmaRing", loc + Vector((0.0, -0.16, -0.25)), (0.38, 0.32, 0.09),
                       rot=rot, mat=mats["magma_seam"], outline=False, cast_shadow=False, registry=registry)

def build_faithful_cinder_spirit_and_furnace(loc, furnace_loc, mats, registry=None):
    base = Vector(loc)
    torso_pos = base + Vector((0.0, 0.0, 1.55))

    # 1. Torso Esculpido con Pectorales y Costillas Facetadas
    bm_torso = bmesh.new()
    torso_cross_sections = [
        ( 0.58, 0.65, 0.40),
        ( 0.26, 0.70, 0.46),
        (-0.06, 0.56, 0.38),
        (-0.36, 0.46, 0.34),
        (-0.60, 0.34, 0.28),
    ]
    t_rings = []
    for z, wx, wy in torso_cross_sections:
        v0 = bm_torso.verts.new((-wx,     -wy*0.6, z))
        v1 = bm_torso.verts.new((-wx*0.6, -wy,     z))
        v2 = bm_torso.verts.new(( wx*0.6, -wy,     z))
        v3 = bm_torso.verts.new(( wx,     -wy*0.6, z))
        v4 = bm_torso.verts.new(( wx*0.8,  wy*0.8, z))
        v5 = bm_torso.verts.new((-wx*0.8,  wy*0.8, z))
        t_rings.append([v0, v1, v2, v3, v4, v5])

    for i in range(len(t_rings) - 1):
        r1 = t_rings[i]
        r2 = t_rings[i+1]
        for k in range(6):
            bm_torso.faces.new([r1[k], r1[(k+1)%6], r2[(k+1)%6], r2[k]])
    bm_torso.faces.new(t_rings[0][::-1])
    bm_torso.faces.new(t_rings[-1])

    bmesh.ops.recalc_face_normals(bm_torso, faces=bm_torso.faces)
    m_torso = bpy.data.meshes.new("Titan_Torso_Mesh")
    bm_torso.to_mesh(m_torso)
    bm_torso.free()

    torso_obj = bpy.data.objects.new("Titan_Torso", m_torso)
    bpy.context.collection.objects.link(torso_obj)
    torso_obj.location = torso_pos
    torso_obj.rotation_euler = (0, R(-4), R(10))
    torso_obj.data.materials.append(mats["titan_armor"])
    apply_comic_styling(torso_obj, bevel_w=0.025, outline_w=0.026)
    if registry is not None:
        registry.append(torso_obj)

    # CANALES DE MAGMA GRUESOS RESPLANDECIENTES EN EL PECHO (Pilar 16)
    for psgn, px in [(-1, -0.23), (1, 0.23)]:
        pec_pos = torso_pos + Vector((px, -0.35, 0.22))
        create_beveled_box(f"Titan_PectoralPlate_{psgn}", pec_pos, (0.38, 0.17, 0.34),
                           rot=(R(12), R(-4), R(10 + psgn*14)), mat=mats["titan_armor"], bevel_w=0.018, outline_w=0.022, registry=registry)
        create_beveled_box(f"Titan_Magma_PecBorder_{psgn}", pec_pos + Vector((0, -0.06, -0.17)), (0.44, 0.10, 0.10),
                           rot=(R(12), R(-4), R(10 + psgn*14)), mat=mats["magma_seam"], outline=False, cast_shadow=False, registry=registry)
        # Fisuras de magma en costillas laterales
        create_beveled_box(f"Titan_Magma_Rib_{psgn}", torso_pos + Vector((px*1.4, -0.20, -0.10)), (0.24, 0.08, 0.08),
                           rot=(R(5), R(-4), R(10 + psgn*28)), mat=mats["magma_seam"], outline=False, cast_shadow=False, registry=registry)

    # Esternón vertical de magma ardiente prominente
    create_beveled_box("Titan_Magma_Sternum", torso_pos + Vector((0.0, -0.38, 0.24)), (0.14, 0.12, 0.50),
                       rot=(R(12), R(-4), R(10)), mat=mats["magma_seam"], outline=False, cast_shadow=False, registry=registry)

    # Fisuras de magma abdominales (six-pack)
    for ai, az in enumerate([0.02, -0.16, -0.34]):
        create_beveled_box(f"Titan_Magma_AbFissure_{ai}", torso_pos + Vector((0.0, -0.33 + ai*0.03, az)),
                           (0.38 - ai*0.04, 0.10, 0.10), rot=(R(8), R(-4), R(10)), mat=mats["magma_seam"], outline=False, cast_shadow=False, registry=registry)

    # Cinturón de magma en la cintura
    create_beveled_box("Titan_Magma_WaistBand", torso_pos + Vector((0.0, -0.19, -0.54)), (0.62, 0.42, 0.12),
                       rot=(0, R(-4), R(10)), mat=mats["magma_seam"], outline=False, cast_shadow=False, registry=registry)

    # 2. Cabeza Esculpida y Casco con Rostro Incandescente
    head_pos = torso_pos + Vector((-0.02, -0.05, 0.90))
    create_sculpted_titan_helmet("Titan_Helmet_Sculpted", head_pos, (0, R(-4), R(10)), mats, registry=registry)

    # 3. MELENA DE FUEGO CIAN ESTILIZADA CÓMIC (Pilar 03, 16)
    create_stylized_flame_tongue("Titan_Mane_Crown", head_pos + Vector((0, 0.08, 0.32)),
                                scale=(0.54, 0.36, 0.65), rot=(R(-15), 0, 0), flame_type='cyan', mats=mats, registry=registry)
    create_stylized_flame_tongue("Titan_Mane_Left", head_pos + Vector((-0.26, 0.10, 0.22)),
                                scale=(0.44, 0.30, 0.54), rot=(R(-18), R(-20), 0), flame_type='cyan', mats=mats, registry=registry)
    create_stylized_flame_tongue("Titan_Mane_Right", head_pos + Vector((0.26, 0.10, 0.22)),
                                scale=(0.44, 0.30, 0.54), rot=(R(-18), R(20), 0), flame_type='cyan', mats=mats, registry=registry)

    # Chimeneas dorsales de titanio
    for c_sgn, cx in [(-1, -0.34), (1, 0.34)]:
        ch_pos = torso_pos + Vector((cx, 0.34, 0.44))
        create_beveled_cylinder(f"Titan_Exhaust_{c_sgn}", ch_pos, 0.10, 0.58, rot=(R(-35), 0, 0), mat=mats["dark_iron"], outline_w=0.018, registry=registry)
        create_stylized_flame_tongue(f"Titan_Exhaust_Flame_{c_sgn}", ch_pos + Vector((0, 0.22, 0.26)),
                                     scale=(0.32, 0.22, 0.40), rot=(R(-35), 0, 0), flame_type='cyan', mats=mats, registry=registry)

    # 4. Brazos Blindados, Hombreras y Puños con Nudillos de Magma
    for a_sgn, ax in [(-1, -0.82), (1, 0.82)]:
        pauldron_p = torso_pos + Vector((ax, 0.0, 0.30))
        create_beveled_box(f"Titan_Pauldron_{a_sgn}", pauldron_p, (0.52, 0.52, 0.42),
                           rot=(0, R(a_sgn*14), 0), mat=mats["titan_armor"], bevel_w=0.03, outline_w=0.024, registry=registry)

        elbow_p = pauldron_p + Vector((a_sgn*0.20, -0.24, -0.42))
        create_beveled_cylinder(f"Titan_Bicep_{a_sgn}", (pauldron_p + elbow_p)*0.5, 0.15, 0.58,
                                rot=(R(30), R(a_sgn*18), 0), mat=mats["titan_armor"], outline_w=0.020, registry=registry)
        create_beveled_cylinder(f"Titan_Elbow_Magma_{a_sgn}", elbow_p, 0.13, 0.17,
                                rot=(0, R(90), 0), mat=mats["magma_seam"], outline=False, cast_shadow=False, registry=registry)

        hand_p = elbow_p + Vector((a_sgn*0.12, -0.32, -0.32))
        create_beveled_cylinder(f"Titan_Forearm_{a_sgn}", (elbow_p + hand_p)*0.5, 0.14, 0.58,
                                rot=(R(40), R(a_sgn*10), 0), mat=mats["titan_armor"], outline_w=0.020, registry=registry)
        create_beveled_box(f"Titan_Hand_{a_sgn}", hand_p, (0.32, 0.36, 0.40),
                           rot=(R(40), R(a_sgn*10), 0), mat=mats["titan_armor"], bevel_w=0.02, outline_w=0.022, registry=registry)

        for fi, fx in enumerate([-0.10, 0.0, 0.10]):
            create_beveled_box(f"Titan_Knuckle_{a_sgn}_{fi}", hand_p + Vector((fx, -0.20, -0.13)),
                               (0.08, 0.16, 0.08), mat=mats["magma_seam"], outline=False, cast_shadow=False, registry=registry)

    # 5. COLA CONTINUA LOFTED DE FUEGO CIAN CONECTADA AL HORNO ARDIENTE (Pilar 03, 12)
    f_x, f_y, f_z = furnace_loc.x, furnace_loc.y, furnace_loc.z
    bm_tail = bmesh.new()
    stations = [
        Vector((f_x - 0.2, f_y - 0.5, f_z - 0.65)),
        Vector((f_x - 0.7, f_y - 0.7, f_z - 0.35)),
        Vector((torso_pos.x + 0.60, torso_pos.y + 0.12, torso_pos.z - 0.82)),
        Vector((torso_pos.x + 0.22, torso_pos.y, torso_pos.z - 0.58)),
        Vector((torso_pos.x, torso_pos.y, torso_pos.z - 0.44))
    ]
    radii = [0.50, 0.46, 0.40, 0.34, 0.26]

    rings = []
    for pt, r in zip(stations, radii):
        ring = []
        for a in range(12):
            ang = a * 2.0 * math.pi / 12
            v = bm_tail.verts.new(pt + Vector((r * math.cos(ang), 0.25 * math.sin(ang), r * math.sin(ang))))
            ring.append(v)
        rings.append(ring)

    for i in range(len(rings) - 1):
        r1 = rings[i]
        r2 = rings[i+1]
        for k in range(12):
            bm_tail.faces.new([r1[k], r1[(k+1)%12], r2[(k+1)%12], r2[k]])

    bmesh.ops.recalc_face_normals(bm_tail, faces=bm_tail.faces)
    m_tail = bpy.data.meshes.new("Titan_Tail_Loft_Mesh")
    bm_tail.to_mesh(m_tail)
    bm_tail.free()

    tail_obj = bpy.data.objects.new("Titan_Tail_Loft", m_tail)
    bpy.context.collection.objects.link(tail_obj)
    tail_obj.data.materials.append(mats["flame_cyan_procedural"])
    apply_comic_styling(tail_obj, bevel_w=0.015, outline=True, outline_w=0.024, cast_shadow=False)
    if registry is not None:
        registry.append(tail_obj)

    # 6. HORNO DE FUNDICIÓN DE LADRILLO ARDIENTE (PILAR 18, REBOTE CÁLIDO)
    create_beveled_box("Furnace_Pillar_L", (f_x - 1.25, f_y, f_z), (0.72, 2.3, 4.2), mat=mats["brick_mat"], bevel_w=0.03, outline_w=0.024, registry=registry)
    create_beveled_box("Furnace_Pillar_R", (f_x + 1.25, f_y, f_z), (0.72, 2.3, 4.2), mat=mats["brick_mat"], bevel_w=0.03, outline_w=0.024, registry=registry)
    create_beveled_box("Furnace_Back_Wall", (f_x, f_y + 0.95, f_z), (3.3, 0.65, 4.2), mat=mats["brick_mat"], bevel_w=0.03, outline_w=0.024, registry=registry)
    create_beveled_box("Furnace_Top_Hood", (f_x, f_y, f_z + 1.65), (3.3, 2.3, 1.05), mat=mats["brick_mat"], bevel_w=0.03, outline_w=0.024, registry=registry)

    arch_pos = Vector((f_x, f_y - 0.72, f_z + 0.35))
    create_beveled_box("Furnace_Arch_Lintel", arch_pos, (2.7, 0.36, 0.32), mat=mats["dark_iron"], outline_w=0.022, registry=registry)
    create_beveled_cylinder("Furnace_Keystone", arch_pos + Vector((0, -0.05, 0.12)), 0.19, 0.26, rot=(R(90), 0, 0), mat=mats["brass"], outline_w=0.016, cast_shadow=False, registry=registry)

    hearth_floor = Vector((f_x, f_y - 0.10, f_z - 1.2))
    create_beveled_box("Furnace_Ember_Bed", hearth_floor + Vector((0, 0, 0.15)), (1.85, 1.45, 0.32), mat=mats["flame_orange_core"], outline=False, cast_shadow=False, registry=registry)

    create_beveled_cylinder("Furnace_Log_1", hearth_floor + Vector((-0.35, 0.1, 0.25)), 0.13, 1.35, rot=(0, R(35), R(15)), mat=mats["dark_iron"], outline=False, cast_shadow=False, registry=registry)
    create_beveled_cylinder("Furnace_Log_2", hearth_floor + Vector((0.35, 0.1, 0.25)), 0.13, 1.35, rot=(0, R(-35), R(-15)), mat=mats["dark_iron"], outline=False, cast_shadow=False, registry=registry)

    for fi, fx_off in enumerate([-0.65, -0.38, -0.10, 0.18, 0.45, 0.70]):
        fl_pos = hearth_floor + Vector((fx_off, -0.22, 0.30 + (fi%2)*0.14))
        create_stylized_flame_tongue(f"Furnace_Fire_Tongue_{fi}", fl_pos, scale=(0.42, 0.26, 0.55), rot=(0, 0, 0), flame_type='orange', mats=mats, registry=registry)

    create_beveled_cylinder("Furnace_Flue_Stack", Vector((f_x, f_y, f_z + 2.85)), 0.68, 3.2, rot=(0, 0, 0), mat=mats["dark_iron"], outline_w=0.024, registry=registry)

    l_fire = bpy.data.lights.new(name="Light_Furnace_Interior", type='POINT')
    l_fire.energy = 4500.0
    l_fire.color = (1.0, 0.44, 0.05)
    l_fire_obj = bpy.data.objects.new("Light_Furnace_Interior_Obj", l_fire)
    l_fire_obj.location = hearth_floor + Vector((0, -0.4, 0.8))
    bpy.context.collection.objects.link(l_fire_obj)
    if registry is not None:
        registry.append(l_fire_obj)

# ==============================================================================
# 9. ENTORNO INDUSTRIAL: FACTORÍA SECTOR 7 (PASARELA, HAZARD, ESCOMBROS)
# ==============================================================================
def build_factory_sector7_environment(textures, mats, registry=None):
    # 1. Pasarela de rejilla elevada en el lado izquierdo
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-4.5, 0.4, 0.32))
    walkway = bpy.context.active_object
    walkway.name = "Walkway_Catwalk"
    walkway.scale = (4.4, 3.2, 0.64)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    walkway.data.materials.append(mats["catwalk_mat"])
    apply_comic_styling(walkway, bevel_w=0.02, outline_w=0.024)
    if registry is not None:
        registry.append(walkway)

    hazard_pos = Vector((-4.5, -1.22, 0.32))
    create_beveled_box("Catwalk_Hazard_Stripe", hazard_pos, (4.4, 0.08, 0.38), mat=mats["hazard_mat"], bevel_w=0.01, outline_w=0.020, cast_shadow=False, registry=registry)

    create_beveled_cylinder("Railing_Top", (-4.5, -1.18, 0.98), 0.035, 4.4, rot=(0, R(90), 0), mat=mats["dark_iron"], outline_w=0.014, cast_shadow=False, registry=registry)
    create_beveled_cylinder("Railing_Mid", (-4.5, -1.18, 0.65), 0.025, 4.4, rot=(0, R(90), 0), mat=mats["dark_iron"], outline_w=0.014, cast_shadow=False, registry=registry)
    for rx in [-6.4, -4.5, -2.6]:
        create_beveled_cylinder(f"Railing_Post_{rx}", (rx, -1.18, 0.65), 0.035, 0.65, rot=(0, 0, 0), mat=mats["dark_iron"], outline_w=0.014, cast_shadow=False, registry=registry)

    # 2. Suelo principal de rejilla/metal
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, -0.25))
    floor_obj = bpy.context.active_object
    floor_obj.name = "Factory_Floor"
    floor_obj.scale = (22.0, 16.0, 0.50)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    floor_obj.data.materials.append(mats["floor_mat"])
    apply_comic_styling(floor_obj, bevel_w=0.015, outline_w=0.020)
    if registry is not None:
        registry.append(floor_obj)

    # 3. Pila de chatarra y escombros industriales (Metales oxidados oscuros)
    scrap_center = Vector((-0.2, -0.6, 0.10))
    create_beveled_box("Scrap_Beam_1", scrap_center + Vector((-0.3, 0.1, 0.08)), (1.6, 0.22, 0.16), rot=(R(15), R(-20), R(40)), mat=mats["dark_iron"], outline_w=0.018, cast_shadow=True, registry=registry)
    create_beveled_box("Scrap_Plate_2", scrap_center + Vector((0.2, -0.1, 0.06)), (1.2, 0.80, 0.08), rot=(R(-10), R(15), R(-25)), mat=mats["scrapper_steel"], outline_w=0.018, cast_shadow=True, registry=registry)
    create_beveled_cylinder("Scrap_Cog_1", scrap_center + Vector((0.5, 0.2, 0.08)), 0.32, 0.10, rot=(R(35), R(-15), 0), mat=mats["dark_iron"], outline_w=0.016, cast_shadow=True, registry=registry)

    # 4. Muro de fondo industrial con columnas y viga gantry
    wall_pos = Vector((0.0, 3.8, 4.0))
    create_beveled_box("Factory_Back_Wall", wall_pos, (22.0, 0.8, 8.5), mat=mats["wall_steel"], bevel_w=0.03, outline_w=0.024, registry=registry)

    for col_x in [-5.2, -1.6, 1.8, 5.2]:
        create_beveled_box(f"Wall_Column_{col_x}", (col_x, 3.4, 4.0), (0.45, 0.35, 8.5), mat=mats["dark_iron"], bevel_w=0.02, outline_w=0.018, registry=registry)

    create_beveled_box("Wall_Gantry_Beam", (0.0, 3.4, 3.1), (22.0, 0.30, 0.35), mat=mats["dark_iron"], bevel_w=0.015, outline_w=0.016, registry=registry)

    # Letrero SECTOR 7 en la viga central alta para la panorámica (solo visible en panorama)
    sign_pos = Vector((-2.2, 3.22, 3.80))
    bm_sign = bmesh.new()
    sw, sh = 0.9, 0.45
    sv0 = bm_sign.verts.new((-sw, 0, -sh))
    sv1 = bm_sign.verts.new(( sw, 0, -sh))
    sv2 = bm_sign.verts.new(( sw, 0,  sh))
    sv3 = bm_sign.verts.new((-sw, 0,  sh))
    bm_sign.faces.new([sv0, sv1, sv2, sv3])
    uv_s = bm_sign.loops.layers.uv.new("UVMap")
    uv_s_coords = [(0,0), (1,0), (1,1), (0,1)]
    for face in bm_sign.faces:
        for idx, loop in enumerate(face.loops):
            loop[uv_s].uv = uv_s_coords[idx]
    m_sign = bpy.data.meshes.new("Sector7_Sign_Mesh")
    bm_sign.to_mesh(m_sign)
    bm_sign.free()

    sign_obj = bpy.data.objects.new("Sector7_Sign", m_sign)
    bpy.context.collection.objects.link(sign_obj)
    sign_obj.location = sign_pos
    sign_obj.data.materials.append(mats["sign_s7"])
    apply_comic_styling(sign_obj, bevel_w=0.005, outline_w=0.018, cast_shadow=False)

    # Faroles de pared (sutil luz ámbar ambiental)
    for li, lx in enumerate([-3.5, 0.0, 3.5]):
        lamp_pos = Vector((lx, 3.25, 3.4))
        create_beveled_box(f"Bulkhead_Housing_{li}", lamp_pos, (0.35, 0.16, 0.25), mat=mats["dark_iron"], outline_w=0.014, cast_shadow=False, registry=registry)
        create_beveled_cylinder(f"Bulkhead_Cage_{li}", lamp_pos + Vector((0, -0.08, 0)), 0.10, 0.12, rot=(R(90), 0, 0), mat=mats["brass"], outline=False, cast_shadow=False, registry=registry)

        l_bulk = bpy.data.lights.new(name=f"Light_Bulkhead_{li}", type='POINT')
        l_bulk.energy = 250.0
        l_bulk.color = (1.0, 0.78, 0.35)
        l_bulk_obj = bpy.data.objects.new(f"Light_Bulkhead_{li}_Obj", l_bulk)
        l_bulk_obj.location = lamp_pos + Vector((0, -0.15, 0))
        bpy.context.collection.objects.link(l_bulk_obj)
        if registry is not None:
            registry.append(l_bulk_obj)

    create_beveled_cylinder("Ceiling_Main_Pipe", (0.0, 0.8, 5.0), 0.22, 24.0, rot=(0, R(90), 0), mat=mats["dark_iron"], outline_w=0.022, cast_shadow=False, registry=registry)
    create_beveled_cylinder("Ceiling_Sub_Pipe", (0.0, 0.1, 5.3), 0.14, 24.0, rot=(0, R(90), 0), mat=mats["brass"], outline_w=0.018, cast_shadow=False, registry=registry)
    create_beveled_cylinder("Ceiling_Spider_Pipe", (1.8, 0.1, 3.45), 0.14, 8.0, rot=(0, R(90), 0), mat=mats["dark_iron"], outline_w=0.018, cast_shadow=False, registry=registry)

    for cy in [0.4, 1.2]:
        create_beveled_cylinder(f"Cable_Hanging_{cy}", (0.0, cy, 4.6), 0.024, 22.0, rot=(0, R(90), 0), mat=mats["dark_iron"], outline_w=0.010, cast_shadow=False, registry=registry)

    furnace_base = Vector((5.6, 1.4, 1.8))
    return furnace_base, sign_obj

# ==============================================================================
# 10. ILUMINACIÓN Y AJUSTES DE RENDER (EEVEE)
# ==============================================================================
def setup_studio_lighting(scene):
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'High Contrast'

    sun_data = bpy.data.lights.new(name="Sun_Key_Comic", type='SUN')
    sun_data.energy = 4.2
    sun_data.color = (1.0, 0.98, 0.95)
    sun_obj = bpy.data.objects.new("Sun_Key_Comic_Obj", sun_data)
    sun_obj.rotation_euler = (R(48), R(14), R(-25))
    bpy.context.collection.objects.link(sun_obj)

    fill_data = bpy.data.lights.new(name="Light_Fill_Front", type='AREA')
    fill_data.energy = 220.0
    fill_data.size = 12.0
    fill_data.color = (0.75, 0.82, 0.95)
    fill_obj = bpy.data.objects.new("Light_Fill_Front_Obj", fill_data)
    fill_obj.location = (0.0, -7.5, 3.5)
    fill_obj.rotation_euler = (R(32), 0, 0)
    bpy.context.collection.objects.link(fill_obj)

    rim_data = bpy.data.lights.new(name="Light_Rim_Cyan", type='AREA')
    rim_data.energy = 260.0
    rim_data.size = 8.0
    rim_data.color = (0.22, 0.88, 1.0)
    rim_obj = bpy.data.objects.new("Light_Rim_Cyan_Obj", rim_data)
    rim_obj.location = (0.0, 3.2, 5.4)
    rim_obj.rotation_euler = (R(-50), 0, 0)
    bpy.context.collection.objects.link(rim_obj)

    bounce_data = bpy.data.lights.new(name="Light_Furnace_Warm_Bounce", type='AREA')
    bounce_data.energy = 550.0
    bounce_data.size = 5.0
    bounce_data.color = (1.0, 0.50, 0.10)
    bounce_obj = bpy.data.objects.new("Light_Furnace_Warm_Bounce_Obj", bounce_data)
    bounce_obj.location = (4.8, 0.5, 1.8)
    bounce_obj.rotation_euler = (0, R(-35), R(-80))
    bpy.context.collection.objects.link(bounce_obj)

# ==============================================================================
# 11. COMPOSITOR DE CUADRANTES MAESTRO (PIL)
# ==============================================================================
def compose_master_quadrant_image(sub_renders, final_output):
    canvas_w = 2560
    canvas_h = 1440
    master = Image.new('RGB', (canvas_w, canvas_h), color=(14, 16, 20))
    draw = ImageDraw.Draw(master)

    quad_w = 1250
    quad_h = 690
    coords = [
        (20, 20),         # Panel 1: TL (Panorama)
        (1290, 20),       # Panel 2: TR (Werewolf)
        (20, 730),        # Panel 3: BL (Orb & Trasgo)
        (1290, 730)       # Panel 4: BR (Cinder Spirit & Horno)
    ]

    titles = [
        "PANORAMA 1:1: FACTORÍA SECTOR 7 (CINCO ENTIDADES, CEL-SHADING & INK OUTLINE)",
        "THE MECHANICAL WEREWOLF (FAUCES INCANDESCENTES, GARRAS CARTOON Y LLAMAS 2D)",
        "AUDITOR DRONE & TRASGO CHATARRERO (MANÓMETROS, CRT, LENTE ROJA, OJO GIGANTE Y SIERRA)",
        "CINDER SPIRIT & HORNO ARDIENTE + CEILING SPIDER-BOT (TITÁN MAGMA, COLA CIAN Y REBOTE CÁLIDO)"
    ]

    font_title = get_system_font(18, bold=True)

    for img_path, (cx, cy), title in zip(sub_renders, coords, titles):
        if os.path.exists(img_path):
            img = Image.open(img_path).convert('RGB')
            img_resized = img.resize((quad_w, quad_h), Image.Resampling.LANCZOS)
            master.paste(img_resized, (cx, cy))

            draw.rectangle([cx, cy, cx + quad_w, cy + quad_h], outline=(65, 70, 80), width=2)
            draw.rectangle([cx, cy, cx + quad_w, cy + 42], fill=(16, 20, 26))
            draw.line([(cx, cy + 42), (cx + quad_w, cy + 42)], fill=(245, 185, 35), width=2)
            draw.text((cx + 18, cy + 10), title, fill=(245, 245, 250), font=font_title)

    master.save(final_output, quality=95)
    print(f"[OK] Master Showcase Bestiario guardado con éxito: {final_output}")

# ==============================================================================
# 12. FUNCIÓN PRINCIPAL DE EJECUCIÓN
# ==============================================================================
def main():
    print("=== INICIANDO PIPELINE DE ALTA CALIDAD BESTIARIO 1:1 (BLENDER 5.2 EEVEE) ===")

    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.film_transparent = False

    world = bpy.data.worlds.new("World_Factory")
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs['Color'].default_value = (0.02, 0.025, 0.04, 1.0)
        bg_node.inputs['Strength'].default_value = 0.30
    scene.world = world

    print("[0/5] Generando texturas procedurales de alta definición...")
    textures = generate_annotated_bestiary_textures()

    init_comic_outline_material()

    mats = {
        "werewolf_steel": create_comic_cel_material("M_Werewolf_Steel", (0.38, 0.42, 0.50, 1.0), shadow_factor=0.38, tex_path=textures["plates"], tex_scale=(1.4, 1.4, 1.4)),
        "dark_iron": create_comic_cel_material("M_Dark_Iron", (0.18, 0.20, 0.24, 1.0), shadow_factor=0.40),
        "brass": create_comic_cel_material("M_Brass_Gold", (0.84, 0.65, 0.20, 1.0), shadow_factor=0.40),
        "bronze_weathered": create_comic_cel_material("M_Bronze_Weathered", (0.42, 0.36, 0.26, 1.0), shadow_factor=0.40),
        "scrapper_steel": create_comic_cel_material("M_Scrapper_Steel", (0.34, 0.36, 0.40, 1.0), shadow_factor=0.38, tex_path=textures["plates"], tex_scale=(1.4, 1.4, 1.4)),
        "drone_hull": create_comic_cel_material("M_Drone_Hull", (0.30, 0.38, 0.36, 1.0), shadow_factor=0.38, tex_path=textures["plates"], tex_scale=(1.6, 1.6, 1.6)),
        "titan_armor": create_comic_cel_material("M_Titan_Armor", (0.18, 0.24, 0.36, 1.0), shadow_factor=0.38),
        "bone_white": create_comic_cel_material("M_Bone_White", (0.92, 0.90, 0.80, 1.0), shadow_factor=0.45),
        "magma_seam": create_comic_cel_material("M_Magma_Seam", (0,0,0,1), is_emissive=True, emissive_rgb=(1.0, 0.42, 0.01, 1.0)),
        "flame_orange_core": create_comic_cel_material("M_Flame_Orange_Core", (0,0,0,1), is_emissive=True, emissive_rgb=(1.0, 0.45, 0.01, 1.0)),
        "flame_yellow_core": create_comic_cel_material("M_Flame_Yellow_Core", (0,0,0,1), is_emissive=True, emissive_rgb=(1.0, 0.92, 0.05, 1.0)),
        "flame_orange_procedural": create_comic_flame_material("M_Flame_Orange_Proc", flame_type='orange'),
        "flame_cyan_procedural": create_comic_flame_material("M_Flame_Cyan_Proc", flame_type='cyan'),
        "eye_yellow": create_comic_cel_material("M_Eye_Yellow", (0,0,0,1), is_emissive=True, emissive_rgb=(1.0, 0.88, 0.05, 1.0)),
        "eye_red": create_comic_cel_material("M_Eye_Red", (0,0,0,1), is_emissive=True, emissive_rgb=(1.0, 0.02, 0.02, 1.0)),
        "led_green": create_comic_cel_material("M_LED_Green", (0,0,0,1), is_emissive=True, emissive_rgb=(0.08, 0.96, 0.20, 1.0)),
        "dial_mat": create_comic_cel_material("M_Dial_Mat", (1,1,1,1), tex_path=textures["dial"], is_uv_decal=True, is_emissive=True),
        "crt_mat": create_comic_cel_material("M_CRT_Mat", (0,1,0,1), tex_path=textures["crt"], is_uv_decal=True, is_emissive=True),
        "floor_mat": create_comic_cel_material("M_Floor_Mat", (0.22, 0.25, 0.30, 1.0), shadow_factor=0.38, tex_path=textures["floor"], tex_scale=(4.0, 4.0, 4.0)),
        "catwalk_mat": create_comic_cel_material("M_Catwalk_Mat", (0.24, 0.28, 0.34, 1.0), shadow_factor=0.38, tex_path=textures["floor"], tex_scale=(3.0, 3.0, 3.0)),
        "wall_steel": create_comic_cel_material("M_Wall_Steel", (0.14, 0.17, 0.22, 1.0), shadow_factor=0.38, tex_path=textures["plates"], tex_scale=(2.0, 2.0, 2.0)),
        "hazard_mat": create_comic_cel_material("M_Hazard_Mat", (0.95, 0.78, 0.10, 1.0), shadow_factor=0.48, tex_path=textures["hazard_stripes"], tex_scale=(2.0, 2.0, 2.0)),
        "brick_mat": create_comic_cel_material("M_Brick_Mat", (0.64, 0.24, 0.16, 1.0), shadow_factor=0.38, tex_path=textures["brick"], tex_scale=(3.6, 3.6, 3.6)),
        "sign_s7": create_comic_cel_material("M_Sign_S7", (0.35, 0.38, 0.44, 1.0), tex_path=textures["sign_s7"], is_uv_decal=True, is_emissive=True),
        "spider_olive": create_comic_cel_material("M_Spider_Olive", (0.28, 0.35, 0.22, 1.0), shadow_factor=0.38),
        "scan_cone": create_scan_cone_material()
    }

    setup_studio_lighting(scene)

    reg_env = []
    reg_werewolf = []
    reg_drone = []
    reg_goblin = []
    reg_cinder = []
    reg_spider = []

    print("[1/5] Construyendo entorno de la Factoría Sector 7...")
    furnace_loc, sign_obj = build_factory_sector7_environment(textures, mats, registry=reg_env)

    print("[2/5] Construyendo Mechanical Werewolf (Lobo Mecánico en pasarela)...")
    build_faithful_werewolf_beast(Vector((-3.8, 0.1, 0.64)), mats, registry=reg_werewolf)

    print("[3/5] Construyendo Auditor Drone flotante...")
    build_faithful_auditor_drone(Vector((-0.9, -0.45, 1.65)), mats, registry=reg_drone)

    print("[4/5] Construyendo Scrapper Goblin (Trasgo Chatarrero)...")
    build_faithful_scrapper_goblin(Vector((1.25, -0.45, 0.0)), mats, registry=reg_goblin)

    print("[5/5] Construyendo Cinder Spirit, Horno ardiente y Ceiling Spider-Bot...")
    build_faithful_cinder_spirit_and_furnace(Vector((3.4, -0.2, 0.0)), furnace_loc, mats, registry=reg_cinder)
    build_faithful_ceiling_spider(Vector((2.2, 0.1, 3.25)), mats, registry=reg_spider)

    blend_path = os.path.join(PROJECT_ROOT, "Art", "Blender", "Bestiario_Entidades_Oficial.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[OK] Proyecto Blend guardado: {blend_path}")

    cam_target = bpy.data.objects.new("CamTarget", None)
    bpy.context.collection.objects.link(cam_target)

    cam_data = bpy.data.cameras.new("ShowcaseCam")
    cam_obj = bpy.data.objects.new("ShowcaseCam", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    track = cam_obj.constraints.new(type='TRACK_TO')
    track.target = cam_target
    track.track_axis = 'TRACK_NEGATIVE_Z'
    track.up_axis = 'UP_Y'

    # Calibración milimétrica de tiros de cámara para encuadres de impacto y cero cortes
    shots = [
        # 1. Panorama 1:1 de toda la factoría (las cinco entidades visibles + letrero)
        {
            "name": "panorama_all",
            "cam_pos": (-0.10, -8.2, 1.95),
            "target_pos": (0.15, 0.0, 1.45),
            "lens": 24.0,
            "visible_groups": [reg_env, reg_werewolf, reg_drone, reg_goblin, reg_cinder, reg_spider, [sign_obj]]
        },
        # 2. Lobo Mecánico aislado en pasarela (encuadre completo 3/4 enfocado en la bestia)
        {
            "name": "werewolf_beast",
            "cam_pos": (-1.2, -5.2, 1.65),
            "target_pos": (-3.4, 0.10, 1.05),
            "lens": 30.0,
            "visible_groups": [reg_env, reg_werewolf]
        },
        # 3. Auditor Drone y Trasgo Chatarrero (encuadre completo enfocado en el dúo)
        {
            "name": "orb_and_trasgo",
            "cam_pos": (0.25, -4.8, 1.25),
            "target_pos": (0.20, -0.45, 1.15),
            "lens": 30.0,
            "visible_groups": [reg_env, reg_drone, reg_goblin]
        },
        # 4. Cinder Spirit, Horno ardiente y Spider-Bot (encuadre completo con elevación)
        {
            "name": "cinder_spirit_furnace",
            "cam_pos": (3.4, -6.0, 2.10),
            "target_pos": (3.6, 0.20, 1.75),
            "lens": 28.0,
            "visible_groups": [reg_env, reg_cinder, reg_spider]
        }
    ]

    all_registered_objs = reg_env + reg_werewolf + reg_drone + reg_goblin + reg_cinder + reg_spider + [sign_obj]

    rendered_paths = []
    for shot in shots:
        vis_set = set()
        for grp in shot["visible_groups"]:
            vis_set.update(grp)

        for obj in all_registered_objs:
            if obj:
                obj.hide_render = (obj not in vis_set)

        cam_obj.location = shot["cam_pos"]
        cam_target.location = shot["target_pos"]
        cam_data.lens = shot["lens"]
        bpy.context.view_layer.update()

        out_path = os.path.join(RENDERS_DIR, f"Showcase_Bestiario_{shot['name']}.png")
        scene.render.filepath = out_path
        print(f"[RENDER] Procesando {shot['name']}...")
        bpy.ops.render.render(write_still=True)
        rendered_paths.append(out_path)
        print(f"[OK] Guardado: {out_path}")

    for obj in all_registered_objs:
        if obj:
            obj.hide_render = False

    showcase_master = os.path.join(RENDERS_DIR, "Showcase_Bestiario_Entidades_Oficial.png")
    compose_master_quadrant_image(rendered_paths, showcase_master)

    shutil.copy2(showcase_master, os.path.join(ARTIFACT_DIR, "Showcase_Bestiario_Entidades_Oficial.png"))
    for fpath in rendered_paths:
        shutil.copy2(fpath, os.path.join(ARTIFACT_DIR, os.path.basename(fpath)))

    print("=== PIPELINE BESTIARIO 1:1 COMPLETADO EXITOSAMENTE ===")

if __name__ == "__main__":
    main()

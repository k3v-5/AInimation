# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Generador Maestro de Hardware de Misión y Arsenal de la Lanzadera - Astra Hazard
# Fiel 1:1 a media_1791198846797.jpg (Consola Táctica, Stasis Pod Médico y Tactical Gadgets)
# Calidad Gráfica Cinematográfica Comic Cel-Shading PBR con Texturas Decal e Inverted Hull Ink Outlines
# Blender 5.2 LTS - Cockpit de Operaciones Oficial (4K Showcase)

import bpy
import bmesh
import math
import os
import shutil
from mathutils import Vector, Euler
from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = r"F:\Dev\Game"
RENDERS_DIR = os.path.join(PROJECT_ROOT, "Art", "Renders")
TEXTURES_DIR = os.path.join(PROJECT_ROOT, "Art", "Textures", "Hardware")
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
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'High Contrast'
    return scene

def get_system_font(size, bold=False):
    font_paths = [
        r"C:\Windows\Fonts\consola.ttf",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\segoeui.ttf"
    ]
    for p in font_paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

# ==============================================================================
# GENERACIÓN DE TEXTURAS PROCEDURALES PBR CON PILLOW
# ==============================================================================
def generate_hardware_textures():
    # 1. Pantalla de la Consola Táctica con Mapa Estelar y Órbitas
    tex_console_path = os.path.join(TEXTURES_DIR, "tex_holo_console.png")
    img_con = Image.new("RGB", (1024, 768), (14, 28, 48))
    draw_c = ImageDraw.Draw(img_con)
    # Rejilla cibernética azul
    for gx in range(0, 1024, 48):
        draw_c.line([(gx, 0), (gx, 768)], fill=(22, 54, 88), width=1)
    for gy in range(0, 768, 48):
        draw_c.line([(0, gy), (1024, gy)], fill=(22, 54, 88), width=1)
    # Anillos orbitales
    cx, cy = 512, 384
    draw_c.ellipse([(cx-260, cy-180), (cx+260, cy+180)], outline=(40, 180, 240), width=3)
    draw_c.ellipse([(cx-180, cy-120), (cx+180, cy+120)], outline=(40, 210, 255), width=2)
    draw_c.ellipse([(cx-100, cy-70), (cx+100, cy+70)], outline=(50, 230, 255), width=2)
    # Sol central
    draw_c.ellipse([(cx-35, cy-35), (cx+35, cy+35)], fill=(255, 220, 40), outline=(255, 255, 200), width=3)
    # Nodos orbitales
    font_hud = get_system_font(22, bold=True)
    draw_c.ellipse([(cx+170, cy-60), (cx+190, cy-40)], fill=(80, 220, 255))
    draw_c.text((cx+200, cy-65), "SECTOR 7", fill=(120, 235, 255), font=font_hud)
    draw_c.ellipse([(cx-190, cy+70), (cx-170, cy+90)], fill=(80, 220, 255))
    draw_c.text((cx-310, cy+75), "MINING RT", fill=(120, 235, 255), font=font_hud)
    draw_c.ellipse([(cx+60, cy+130), (cx+80, cy+150)], fill=(80, 220, 255))
    draw_c.text((cx+90, cy+135), "ASTEROID 14", fill=(120, 235, 255), font=font_hud)
    # Trayectoria de vuelo punteada
    draw_c.line([(cx-180, cy+80), (cx+70, cy+140), (cx+180, cy-50)], fill=(255, 180, 50), width=3)
    img_con.save(tex_console_path)

    # 2. Monitor Médico ECG (Curva de electrocardiograma verde)
    tex_ecg_path = os.path.join(TEXTURES_DIR, "tex_ecg_monitor.png")
    img_ecg = Image.new("RGB", (512, 512), (10, 24, 16))
    draw_e = ImageDraw.Draw(img_ecg)
    # Cuadrícula médica
    for ex in range(0, 512, 32):
        draw_e.line([(ex, 0), (ex, 512)], fill=(16, 48, 28), width=1)
    for ey in range(0, 512, 32):
        draw_e.line([(0, ey), (512, ey)], fill=(16, 48, 28), width=1)
    # Curva ECG (P-Q-R-S-T)
    ecg_pts = [
        (20, 200), (80, 200), (95, 185), (110, 200), (130, 200),
        (145, 220), (160, 60), (175, 240), (190, 200), (220, 200),
        (240, 175), (265, 200), (320, 200), (335, 185), (350, 200),
        (370, 200), (385, 220), (400, 60), (415, 240), (430, 200), (480, 200)
    ]
    draw_e.line(ecg_pts, fill=(50, 255, 90), width=4)
    # Texto de constantes vitales
    font_mono = get_system_font(32, bold=True)
    draw_e.text((40, 310), "HR:  64 bpm", fill=(60, 255, 110), font=font_mono)
    draw_e.text((40, 360), "STATUS: STABLE", fill=(60, 255, 110), font=font_mono)
    draw_e.text((40, 410), "CRYO: ACTIVE", fill=(100, 220, 255), font=font_mono)
    # Corazón y LEDs
    draw_e.ellipse([(420, 315), (455, 350)], fill=(255, 50, 50))
    img_ecg.save(tex_ecg_path)

    # 3. Escáner Multigas OLED
    tex_scan_path = os.path.join(TEXTURES_DIR, "tex_multigas_screen.png")
    img_scan = Image.new("RGB", (512, 512), (12, 28, 18))
    draw_s = ImageDraw.Draw(img_scan)
    font_sc = get_system_font(42, bold=True)
    draw_s.rectangle([(15, 15), (497, 497)], outline=(35, 95, 45), width=4)
    draw_s.text((40, 70), "O2:  21%", fill=(65, 255, 100), font=font_sc)
    draw_s.text((40, 160), "CO2: 0.1%", fill=(65, 255, 100), font=font_sc)
    draw_s.text((40, 250), "PSI: 14.7", fill=(80, 220, 255), font=font_sc)
    draw_s.rectangle([(40, 360), (472, 440)], fill=(25, 65, 35), outline=(50, 200, 80), width=3)
    draw_s.text((70, 375), "SCAN ACTIVE", fill=(80, 255, 120), font=font_sc)
    img_scan.save(tex_scan_path)

    # 4. Señal Breach Patch & Flare Labels
    tex_rack_path = os.path.join(TEXTURES_DIR, "tex_breach_rack.png")
    img_rack = Image.new("RGBA", (1024, 512), (75, 78, 85, 255))
    draw_r = ImageDraw.Draw(img_rack)
    # Marco de metal con remaches
    for rx in range(20, 1004, 64):
        draw_r.ellipse([(rx, 15), (rx+8, 23)], fill=(160, 165, 175))
        draw_r.ellipse([(rx, 485), (rx+8, 493)], fill=(160, 165, 175))
    font_title = get_system_font(48, bold=True)
    draw_r.rectangle([(400, 40), (980, 110)], fill=(35, 38, 42), outline=(220, 175, 35), width=3)
    draw_r.text((420, 50), "BREACH PATCH - SHIP-FIX", fill=(245, 235, 210), font=font_title)
    # Rayas diagonales en bengalas
    font_flare = get_system_font(26, bold=True)
    for fx, fn in [(60, "FLARE 1"), (170, "FLARE 2"), (280, "FLARE 3")]:
        draw_r.rectangle([(fx, 130), (fx+80, 460)], fill=(230, 95, 20), outline=(20, 20, 20), width=4)
        for y_str in range(150, 440, 30):
            draw_r.polygon([(fx, y_str), (fx+80, y_str+15), (fx+80, y_str+25), (fx, y_str+10)], fill=(20, 20, 20))
        draw_r.text((fx+8, 280), "EMERG", fill=(255, 255, 255), font=font_flare)
    img_rack.save(tex_rack_path)

    # 5. Caja Militar CARGO 04 - SUPPLIES
    tex_crate_path = os.path.join(TEXTURES_DIR, "tex_cargo_crate.png")
    img_crate = Image.new("RGB", (1024, 512), (115, 125, 110))
    draw_cr = ImageDraw.Draw(img_crate)
    for y in [40, 460]:
        draw_cr.line([(0, y), (1024, y)], fill=(45, 55, 40), width=8)
    font_cr = get_system_font(52, bold=True)
    draw_cr.rectangle([(120, 160), (900, 340)], fill=(85, 95, 80), outline=(235, 175, 30), width=4)
    draw_cr.text((150, 180), "CARGO 04 - SUPPLIES", fill=(245, 240, 220), font=font_cr)
    draw_cr.text((380, 260), "[ LOCKED ]", fill=(245, 160, 40), font=font_cr)
    img_crate.save(tex_crate_path)

    return {
        "console": tex_console_path,
        "ecg": tex_ecg_path,
        "scan": tex_scan_path,
        "rack": tex_rack_path,
        "crate": tex_crate_path
    }

# ==============================================================================
# SISTEMA DE CONTORNO CÓMIC PROFESIONAL (INVERTED HULL INK OUTLINES BLENDER 5.2)
# ==============================================================================
M_INK_OUTLINE = None

def init_outline_material():
    global M_INK_OUTLINE
    mat = bpy.data.materials.get("M_Ink_Outline_Hw")
    if not mat:
        mat = bpy.data.materials.new(name="M_Ink_Outline_Hw")
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

def apply_comic_styling(obj, smooth=True, bevel=True, bevel_width=0.015, outline=True, outline_thickness=0.012):
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

def make_color_mat(name, col_rgba, rough=0.5, met=0.0, emit_str=0.0, emit_col=None):
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

def make_image_mat(name, img_path, rough=0.5, met=0.0, emit_str=0.0):
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
# MODELADO DEL COCKPIT COMPLETO (FIEL 1:1 A media_1791198846797.jpg)
# ==============================================================================
def build_shuttle_cockpit(tex_dict):
    m_steel = make_color_mat("M_BulkheadSteel", (0.34, 0.36, 0.38, 1.0), rough=0.55, met=0.6)
    m_copper = make_color_mat("M_PodCopper", (0.65, 0.38, 0.24, 1.0), rough=0.5, met=0.7)
    m_yellow = make_color_mat("M_HazardYellow", (0.95, 0.74, 0.05, 1.0), rough=0.4)
    m_orange = make_color_mat("M_FlareOrange", (0.95, 0.40, 0.10, 1.0), rough=0.35)
    m_cyan_glow = make_color_mat("M_HoloCyan", (0.15, 0.90, 1.0, 1.0), emit_str=3.5)
    m_sun_glow = make_color_mat("M_HoloSun", (1.0, 0.90, 0.25, 1.0), emit_str=5.0)
    m_dark_rubber = make_color_mat("M_RubberGrip", (0.15, 0.15, 0.16, 1.0), rough=0.8)
    m_white_suit = make_color_mat("M_WhiteAstro", (0.85, 0.85, 0.88, 1.0), rough=0.6)
    # Material del cristal criogénico con transparencia real
    mat_cryo = bpy.data.materials.new("M_CryoGlass")
    mat_cryo.use_nodes = True
    mat_cryo.surface_render_method = 'BLENDED'
    c_nodes = mat_cryo.node_tree.nodes
    c_nodes.clear()
    c_out = c_nodes.new('ShaderNodeOutputMaterial')
    c_bsdf = c_nodes.new('ShaderNodeBsdfPrincipled')
    c_bsdf.inputs['Base Color'].default_value = (0.75, 0.95, 1.0, 1.0)
    c_bsdf.inputs['Roughness'].default_value = 0.12
    c_bsdf.inputs['Metallic'].default_value = 0.1
    c_bsdf.inputs['Transmission Weight'].default_value = 0.85
    c_bsdf.inputs['Alpha'].default_value = 0.35
    mat_cryo.node_tree.links.new(c_bsdf.outputs['BSDF'], c_out.inputs['Surface'])
    m_glass = mat_cryo

    # 1. Cabina interior: Pared trasera con ventana espacial al fondo
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 3.2, 2.2))
    back_wall = bpy.context.active_object
    back_wall.scale = (9.0, 0.3, 4.8)
    back_wall.data.materials.append(m_steel)
    apply_comic_styling(back_wall, bevel=True, bevel_width=0.03, outline=True)

    # Ventana de cabina con vista al espacio
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 3.0, 2.8))
    win = bpy.context.active_object
    win.scale = (2.8, 0.15, 1.8)
    win.data.materials.append(make_color_mat("M_CockpitWin", (0.05, 0.08, 0.15, 1.0), rough=0.2))
    apply_comic_styling(win, bevel=True, bevel_width=0.02, outline=True)

    # Asteroides visibles por la ventana
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=0.65, location=(0.7, 4.8, 3.2))
    ast1 = bpy.context.active_object
    ast1.data.materials.append(make_color_mat("M_SpaceAst", (0.35, 0.34, 0.32, 1.0), rough=0.85))
    apply_comic_styling(ast1, bevel=False, outline=True)

    # Suelo de la cabina
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.5, 0.0))
    floor = bpy.context.active_object
    floor.scale = (9.0, 6.5, 0.1)
    floor.data.materials.append(m_steel)

    # 2. BAHÍA DE CARGA A LA IZQUIERDA CON CONTENEDOR 'CARGO 04 - SUPPLIES'
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-2.8, 1.8, 1.8))
    bay = bpy.context.active_object
    bay.scale = (2.4, 2.2, 3.2)
    bay.data.materials.append(m_steel)
    apply_comic_styling(bay, bevel=True, bevel_width=0.03, outline=True)

    # Contenedor militar cerrado
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-2.6, 1.6, 1.2))
    crate = bpy.context.active_object
    crate.scale = (1.6, 1.1, 0.95)
    crate.rotation_euler = (0, 0, R(8))
    crate.data.materials.append(make_image_mat("M_CrateMat", tex_dict["crate"], rough=0.55))
    apply_comic_styling(crate, bevel=True, bevel_width=0.02, outline=True)

    # Abrazaderas naranjas del contenedor
    for cx_off in [-0.75, 0.75]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-2.6 + cx_off, 1.6, 1.2))
        clamp = bpy.context.active_object
        clamp.scale = (0.12, 1.15, 1.02)
        clamp.rotation_euler = (0, 0, R(8))
        clamp.data.materials.append(m_orange)
        apply_comic_styling(clamp, bevel=True, bevel_width=0.015, outline=True)

    # 3. CONSOLA TÁCTICA CENTRAL PUPITRE CON HOLOGRAMA 3D
    c_loc = (0.0, 0.6, 0.0)
    # Pedestal de la consola
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(c_loc[0], c_loc[1], c_loc[2] + 0.55))
    con_base = bpy.context.active_object
    con_base.scale = (2.2, 1.4, 1.1)
    con_base.data.materials.append(m_steel)
    apply_comic_styling(con_base, bevel=True, bevel_width=0.03, outline=True)

    # Superficie pupitre inclinada
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(c_loc[0], c_loc[1] - 0.15, c_loc[2] + 1.15))
    con_top = bpy.context.active_object
    con_top.scale = (2.4, 1.5, 0.25)
    con_top.rotation_euler = (R(26), 0, 0)
    con_top.data.materials.append(m_steel)
    apply_comic_styling(con_top, bevel=True, bevel_width=0.02, outline=True)

    # Pantalla holográfica de la consola con textura de órbitas
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(c_loc[0], c_loc[1] - 0.14, c_loc[2] + 1.28))
    scr = bpy.context.active_object
    scr.scale = (1.5, 1.05, 0.02)
    scr.rotation_euler = (R(26), 0, 0)
    scr.data.materials.append(make_image_mat("M_ConsoleScreen", tex_dict["console"], rough=0.3, emit_str=2.0))

    # Teclado de botones y diales
    for bx in [-0.9, 0.9]:
        for by in [-0.2, 0.1]:
            bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=0.06, location=(c_loc[0] + bx, c_loc[1] - 0.1 + by, c_loc[2] + 1.25), rotation=(R(26), 0, 0))
            dial = bpy.context.active_object
            dial.data.materials.append(m_yellow)
            apply_comic_styling(dial, bevel=True, bevel_width=0.005, outline=True)

    # Proyección Holográfica 3D del Sistema Solar flotando sobre la consola
    h_center = (c_loc[0], c_loc[1], c_loc[2] + 2.05)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.18, location=h_center)
    h_sun = bpy.context.active_object
    h_sun.data.materials.append(m_sun_glow)

    # Anillos orbitales
    for r_orb, p_rot in [(0.55, R(16)), (0.85, R(-14)), (1.15, R(22))]:
        bpy.ops.mesh.primitive_torus_add(major_radius=r_orb, minor_radius=0.015, location=h_center)
        h_ring = bpy.context.active_object
        h_ring.rotation_euler = (p_rot, 0, 0)
        h_ring.data.materials.append(m_cyan_glow)

    # Nodos planetarios
    for px, py, pz in [(0.52, 0.15, 0.14), (-0.78, -0.20, -0.16), (0.95, -0.15, 0.35)]:
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.065, location=(h_center[0] + px, h_center[1] + py, h_center[2] + pz))
        p_node = bpy.context.active_object
        p_node.data.materials.append(m_cyan_glow)

    # 4. COLOSAL STASIS POD DE COBRE A LA DERECHA (Con astronauta y monitor ECG)
    pod_pos = (2.6, 1.4, 0.0)
    # Cuerpo cilíndrico de cobre remachado
    bpy.ops.mesh.primitive_cylinder_add(radius=0.72, depth=2.6, location=(pod_pos[0], pod_pos[1], pod_pos[2] + 1.5))
    pod = bpy.context.active_object
    pod.data.materials.append(m_copper)
    apply_comic_styling(pod, bevel=True, bevel_width=0.03, outline=True)

    # Cúpula abovedada superior
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.72, location=(pod_pos[0], pod_pos[1], pod_pos[2] + 2.8))
    p_dome = bpy.context.active_object
    p_dome.scale = (1.0, 1.0, 0.55)
    p_dome.data.materials.append(m_copper)
    apply_comic_styling(p_dome, bevel=True, bevel_width=0.02, outline=True)

    # Ventana frontal abovedada transparente
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(pod_pos[0], pod_pos[1] - 0.70, pod_pos[2] + 1.65))
    p_glass = bpy.context.active_object
    p_glass.scale = (0.75, 0.06, 1.55)
    p_glass.data.materials.append(m_glass)
    apply_comic_styling(p_glass, bevel=True, bevel_width=0.015, outline=True)

    # Astronauta en escafandra blanca visible en el interior
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22, location=(pod_pos[0], pod_pos[1] - 0.25, pod_pos[2] + 2.15))
    astro_h = bpy.context.active_object
    astro_h.data.materials.append(m_white_suit)
    apply_comic_styling(astro_h, bevel=False, outline=True)

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(pod_pos[0], pod_pos[1] - 0.20, pod_pos[2] + 1.45))
    astro_b = bpy.context.active_object
    astro_b.scale = (0.55, 0.35, 0.95)
    astro_b.data.materials.append(m_white_suit)
    apply_comic_styling(astro_b, bevel=True, bevel_width=0.02, outline=True)

    # Luz interior del pod iluminando al tripulante
    l_pod = bpy.data.lights.new("Light_Pod", 'POINT')
    l_pod.energy = 85.0
    l_pod.color = (0.7, 0.95, 1.0)
    lo_pod = bpy.data.objects.new("Light_Pod_Obj", l_pod)
    lo_pod.location = (pod_pos[0], pod_pos[1] - 0.35, pod_pos[2] + 1.85)
    bpy.context.collection.objects.link(lo_pod)

    # Monitor Médico ECG articulado adherido al lateral del pod
    mon_pos = (pod_pos[0] + 0.88, pod_pos[1] - 0.35, pod_pos[2] + 1.65)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=mon_pos)
    monitor = bpy.context.active_object
    monitor.scale = (0.12, 0.58, 0.46)
    monitor.rotation_euler = (0, 0, R(-20))
    monitor.data.materials.append(m_steel)
    apply_comic_styling(monitor, bevel=True, bevel_width=0.015, outline=True)

    # Pantalla ECG activa
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(mon_pos[0] - 0.06, mon_pos[1], mon_pos[2]))
    m_screen = bpy.context.active_object
    m_screen.scale = (0.02, 0.48, 0.36)
    m_screen.rotation_euler = (0, 0, R(-20))
    m_screen.data.materials.append(make_image_mat("M_ECGScreen", tex_dict["ecg"], rough=0.3, emit_str=2.5))

    # 5. GADGETS TÁCTICOS EN PRIMER PLANO (Escáner en mano y rack de rescate)
    # A. Escáner Multigas en mano (Primer plano izquierdo)
    sc_pos = (-0.95, -1.15, 0.95)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=sc_pos)
    scanner = bpy.context.active_object
    scanner.scale = (0.28, 0.48, 0.10)
    scanner.rotation_euler = (R(22), R(-12), R(15))
    scanner.data.materials.append(make_color_mat("M_ScanGreen", (0.35, 0.48, 0.30, 1.0), rough=0.55))
    apply_comic_styling(scanner, bevel=True, bevel_width=0.015, outline=True)

    # Pantalla OLED verde del escáner
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(sc_pos[0], sc_pos[1] + 0.08, sc_pos[2] + 0.055))
    sc_lcd = bpy.context.active_object
    sc_lcd.scale = (0.20, 0.24, 0.01)
    sc_lcd.rotation_euler = (R(22), R(-12), R(15))
    sc_lcd.data.materials.append(make_image_mat("M_ScanLCD", tex_dict["scan"], rough=0.3, emit_str=2.5))

    # B. Rack de Rescate con Bengalas y Parche (Primer plano derecho)
    rk_pos = (1.15, -1.05, 0.92)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=rk_pos)
    rack = bpy.context.active_object
    rack.scale = (1.35, 0.08, 0.82)
    rack.rotation_euler = (R(-15), 0, R(-10))
    rack.data.materials.append(make_image_mat("M_RackTex", tex_dict["rack"], rough=0.5))
    apply_comic_styling(rack, bevel=True, bevel_width=0.02, outline=True)

    # 3 Bengalas de emergencia
    for fi, fx in enumerate([-0.38, -0.24, -0.10]):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.045, depth=0.48, location=(rk_pos[0] + fx, rk_pos[1] - 0.08, rk_pos[2] - 0.05))
        fl = bpy.context.active_object
        fl.rotation_euler = (R(-15), 0, R(-10))
        fl.data.materials.append(m_orange)
        apply_comic_styling(fl, bevel=True, bevel_width=0.008, outline=True)

    # Cilindro de Breach Patch
    bpy.ops.mesh.primitive_cylinder_add(radius=0.10, depth=0.52, location=(rk_pos[0] + 0.32, rk_pos[1] - 0.10, rk_pos[2] + 0.10))
    patch = bpy.context.active_object
    patch.rotation_euler = (0, R(90), R(-10))
    patch.data.materials.append(make_color_mat("M_PatchSilv", (0.75, 0.78, 0.82, 1.0), rough=0.4, met=0.8))
    apply_comic_styling(patch, bevel=True, bevel_width=0.01, outline=True)

    # Franja naranja en el parche
    bpy.ops.mesh.primitive_cylinder_add(radius=0.103, depth=0.22, location=(rk_pos[0] + 0.32, rk_pos[1] - 0.10, rk_pos[2] + 0.10))
    p_band = bpy.context.active_object
    p_band.rotation_euler = (0, R(90), R(-10))
    p_band.data.materials.append(m_orange)

    # Rollo de cinta de reparación
    bpy.ops.mesh.primitive_cylinder_add(radius=0.11, depth=0.08, location=(rk_pos[0] + 0.28, rk_pos[1] - 0.08, rk_pos[2] - 0.22))
    tape = bpy.context.active_object
    tape.rotation_euler = (R(-15), 0, R(-10))
    tape.data.materials.append(make_color_mat("M_TapeBrown", (0.72, 0.60, 0.40, 1.0), rough=0.75))
    apply_comic_styling(tape, bevel=True, bevel_width=0.008, outline=True)

# ==============================================================================
# PIPELINE Y RENDERIZADO DE 4 CUADRANTES 4K
# ==============================================================================
def setup_cockpit_lighting():
    world = bpy.context.scene.world or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    nodes.clear()
    out_node = nodes.new(type='ShaderNodeOutputWorld')
    bg_node = nodes.new(type='ShaderNodeBackground')
    bg_node.inputs['Color'].default_value = (0.04, 0.05, 0.08, 1.0)
    world.node_tree.links.new(bg_node.outputs['Background'], out_node.inputs['Surface'])

    # Luz de techo cenital cálida de la cabina
    key_light = bpy.data.lights.new("Key_Cockpit", 'AREA')
    key_light.energy = 520.0
    key_light.size = 8.0
    key_light.color = (1.0, 0.95, 0.88)
    ko = bpy.data.objects.new("Key_Cockpit_Obj", key_light)
    ko.location = (0.0, -0.5, 3.8)
    ko.rotation_euler = (R(35), 0, 0)
    bpy.context.collection.objects.link(ko)

    # Luz de relleno frontal suave
    fill_light = bpy.data.lights.new("Fill_Cockpit", 'AREA')
    fill_light.energy = 320.0
    fill_light.size = 12.0
    fill_light.color = (0.80, 0.88, 1.0)
    fo = bpy.data.objects.new("Fill_Cockpit_Obj", fill_light)
    fo.location = (0.0, -4.5, 2.5)
    fo.rotation_euler = (R(65), 0, 0)
    bpy.context.collection.objects.link(fo)

def compose_master_quadrant_image(sub_renders, final_output):
    canvas_w = 3840
    canvas_h = 2160
    master = Image.new('RGB', (canvas_w, canvas_h), color=(14, 12, 10))
    draw = ImageDraw.Draw(master)

    quad_w = 1880
    quad_h = 1040
    coords = [
        (30, 30),         # Panel 1: TL (Panorama)
        (1930, 30),       # Panel 2: TR (Consola Táctica)
        (30, 1090),       # Panel 3: BL (Stasis Pod)
        (1930, 1090)      # Panel 4: BR (Gadgets)
    ]

    titles = [
        "CABINA DE OPERACIONES: HARDWARE DE MISIÓN Y ARSENAL INTEGRADO",
        "CONSOLA TÁCTICA 3D: SISTEMA SOLAR, ÓRBITAS Y CONTRATOS",
        "STASIS POD MÉDICO: VENTANA CRIOGÉNICA Y MONITOR ECG VITAL",
        "GADGETS TÁCTICOS: ESCÁNER MULTIGAS OLED, BENGALAS TÉRMICAS Y PARCHE EXPANSIVO"
    ]

    font_t = get_system_font(32, bold=True)

    for img_path, (cx, cy), title in zip(sub_renders, coords, titles):
        if os.path.exists(img_path):
            img = Image.open(img_path).convert('RGB')
            img_resized = img.resize((quad_w, quad_h), Image.Resampling.LANCZOS)
            master.paste(img_resized, (cx, cy))

            # Borde cómic
            draw.rectangle([cx - 4, cy - 4, cx + quad_w + 4, cy + quad_h + 4], outline=(5, 5, 5), width=6)
            draw.rectangle([cx, cy, cx + quad_w, cy + quad_h], outline=(160, 120, 75), width=2)

            # Cartela de título
            draw.rectangle([cx, cy, cx + quad_w, cy + 48], fill=(22, 18, 16))
            draw.line([(cx, cy + 48), (cx + quad_w, cy + 48)], fill=(235, 175, 45), width=3)
            draw.text((cx + 25, cy + 10), title, fill=(250, 240, 215), font=font_t)

    master.save(final_output, quality=95)
    print(f"[OK] Master 4K Showcase Hardware guardado con éxito: {final_output}")

def main():
    print("=== INICIANDO CONSTRUCCIÓN MAESTRA DE HARDWARE (FIEL 1:1 A media_1791198846797.jpg) ===")
    scene = reset_scene()
    tex_dict = generate_hardware_textures()
    init_outline_material()
    setup_cockpit_lighting()

    print("[1/1] Construyendo Cockpit de Operaciones completo...")
    build_shuttle_cockpit(tex_dict)

    blend_path = os.path.join(PROJECT_ROOT, "Art", "Blender", "Hardware_Shuttle_Oficial.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"[OK] Archivo Blend guardado: {blend_path}")

    # Configuración de 4 cámaras perfectamente encuadradas y calibradas
    cam_pan = bpy.data.objects.new("Cam_Panorama", bpy.data.cameras.new("Cam_Panorama"))
    cam_pan.location = (0.0, -4.5, 2.10)
    cam_pan.rotation_euler = (R(75), 0, 0)
    cam_pan.data.lens = 22.0
    bpy.context.collection.objects.link(cam_pan)

    cam_holo = bpy.data.objects.new("Cam_Holo", bpy.data.cameras.new("Cam_Holo"))
    cam_holo.location = (0.0, -2.4, 1.85)
    cam_holo.rotation_euler = (R(82), 0, 0)
    cam_holo.data.lens = 30.0
    bpy.context.collection.objects.link(cam_holo)

    cam_pod = bpy.data.objects.new("Cam_Pod", bpy.data.cameras.new("Cam_Pod"))
    cam_pod.location = (2.6, -2.6, 1.70)
    cam_pod.rotation_euler = (R(82), 0, R(4))
    cam_pod.data.lens = 28.0
    bpy.context.collection.objects.link(cam_pod)

    cam_gear = bpy.data.objects.new("Cam_Gear", bpy.data.cameras.new("Cam_Gear"))
    cam_gear.location = (0.1, -2.6, 1.35)
    cam_gear.rotation_euler = (R(72), 0, R(-8))
    cam_gear.data.lens = 30.0
    bpy.context.collection.objects.link(cam_gear)

    r_pan = os.path.join(RENDERS_DIR, "Showcase_Hardware_shuttle_panorama.png")
    r_holo = os.path.join(RENDERS_DIR, "Showcase_Hardware_holo_table_closeup.png")
    r_pod = os.path.join(RENDERS_DIR, "Showcase_Hardware_med_pod_closeup.png")
    r_gear = os.path.join(RENDERS_DIR, "Showcase_Hardware_tactical_gadgets_closeup.png")

    for cam, fpath in [(cam_pan, r_pan), (cam_holo, r_holo), (cam_pod, r_pod), (cam_gear, r_gear)]:
        scene.camera = cam
        scene.render.resolution_x = 1920
        scene.render.resolution_y = 1080
        scene.render.filepath = fpath
        bpy.ops.render.render(write_still=True)
        print(f"[OK] Render guardado: {fpath}")

    r_master = os.path.join(RENDERS_DIR, "Showcase_Hardware_Y_Gadgets_Oficial.png")
    compose_master_quadrant_image([r_pan, r_holo, r_pod, r_gear], r_master)

    for rf in [r_pan, r_holo, r_pod, r_gear, r_master]:
        shutil.copy2(rf, os.path.join(ARTIFACT_DIR, os.path.basename(rf)))

    print("=== PIPELINE HARDWARE SHUTTLE COMPLETADO EXITOSAMENTE ===")

if __name__ == "__main__":
    main()

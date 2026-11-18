# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Generador Maestro del Catálogo de Activos 3D Modulares y Reutilizables V5 - Astra Hazard
# Descomposición Fiel 1:1 de los 3 Mapas (media_1791273626834.png) y Componentes Mecánicos (media_1791273929163.png)
# Blender 5.2 LTS - Modelado Paramétrico, Shaders Stylized PBR, Cel-Shading y Freestyle Ink Lineart

import bpy
import bmesh
import math
import os
import shutil
from mathutils import Vector, Euler
from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = r"F:\Dev\Game"
RENDERS_DIR = os.path.join(PROJECT_ROOT, "Art", "Renders")
TEXTURES_MODULAR = os.path.join(PROJECT_ROOT, "Art", "Textures", "Modular")
ARTIFACT_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\b59ff04f-3c21-4ee5-94b0-8e8f899f8923"
BLEND_FILE = os.path.join(PROJECT_ROOT, "Art", "Blender", "Catalogo_Activos_Modulares_Oficial.blend")

os.makedirs(RENDERS_DIR, exist_ok=True)
os.makedirs(ARTIFACT_DIR, exist_ok=True)

R = math.radians

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if not bpy.data.scenes:
        bpy.data.scenes.new("Scene")
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.film_transparent = False
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'High Contrast'
    
    # Entorno cósmico de estudio con iluminación ambiental sutil
    world = bpy.data.worlds.new("World_Studio")
    scene.world = world
    world.use_nodes = True
    wnodes = world.node_tree.nodes
    wlinks = world.node_tree.links
    wnodes.clear()
    
    w_out = wnodes.new(type='ShaderNodeOutputWorld')
    w_bg = wnodes.new(type='ShaderNodeBackground')
    w_bg.inputs['Color'].default_value = (0.015, 0.018, 0.024, 1.0)
    w_bg.inputs['Strength'].default_value = 0.40
    wlinks.new(w_bg.outputs['Background'], w_out.inputs['Surface'])
    
    # Freestyle Lineart (Estilo Novela Gráfica / Cómic con tinta negra)
    scene.render.use_freestyle = True
    rl = scene.view_layers["ViewLayer"]
    rl.use_freestyle = True
    rl.freestyle_settings.as_render_pass = False
    rl.freestyle_settings.crease_angle = math.radians(135.0)
    
    linesets = rl.freestyle_settings.linesets
    while linesets:
        linesets.remove(linesets[0])
    
    ls = linesets.new("ComicInkOutline")
    ls.select_silhouette = True
    ls.select_border = True
    ls.select_crease = True
    ls.select_material_boundary = True
    
    linestyles = bpy.data.linestyles
    linestyle = linestyles.new("InkStyle")
    linestyle.color = (0.03, 0.03, 0.04)
    linestyle.thickness = 1.6
    ls.linestyle = linestyle
    
    return scene

def create_collection(name, parent=None):
    col = bpy.data.collections.new(name)
    if parent:
        parent.children.link(col)
    else:
        bpy.context.scene.collection.children.link(col)
    return col

def add_bevel(obj, width=0.015, segments=3, angle_limit=35.0):
    mod = obj.modifiers.new(name="Bevel", type='BEVEL')
    mod.width = width
    mod.segments = segments
    mod.limit_method = 'ANGLE'
    mod.angle_limit = math.radians(angle_limit)
    return mod

# ==============================================================================
# PIPELINE DE SHADERS PBR ESTILIZADOS CON VIVEZA DE COLOR Y TEXTURAS
# ==============================================================================
MATS = {}

def get_stylized_material(name, base_color=(0.5, 0.5, 0.5), roughness=0.4, metallic=0.0,
                          emissive_color=(0,0,0,1), emissive_strength=0.0,
                          alpha=1.0, is_transparent=False,
                          tex_pack=None, uv_scale=(1.0, 1.0, 1.0), tex_mix=0.35, blend_type='MIX'):
    if name in MATS:
        return MATS[name]
        
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    node_out.location = (600, 0)
    
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (200, 0)
    node_bsdf.inputs['Base Color'].default_value = (*base_color, 1.0)
    node_bsdf.inputs['Roughness'].default_value = roughness
    node_bsdf.inputs['Metallic'].default_value = metallic
    
    if emissive_strength > 0.0:
        node_bsdf.inputs['Emission Color'].default_value = emissive_color
        node_bsdf.inputs['Emission Strength'].default_value = emissive_strength
        
    if is_transparent:
        node_bsdf.inputs['Alpha'].default_value = alpha
        try:
            mat.surface_render_method = 'BLENDED'
        except:
            mat.blend_method = 'BLEND'
            
    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])
    
    if tex_pack:
        basecolor_path = os.path.join(TEXTURES_MODULAR, f"{tex_pack}_BaseColor.png")
        normal_path = os.path.join(TEXTURES_MODULAR, f"{tex_pack}_Normal.png")
        
        coord = nodes.new(type='ShaderNodeTexCoord')
        coord.location = (-800, 150)
        mapping = nodes.new(type='ShaderNodeMapping')
        mapping.location = (-600, 150)
        mapping.inputs['Scale'].default_value = uv_scale
        links.new(coord.outputs['Object'], mapping.inputs['Vector'])
        
        if os.path.exists(basecolor_path):
            tex_col = nodes.new(type='ShaderNodeTexImage')
            tex_col.location = (-350, 200)
            tex_col.projection = 'BOX'
            tex_col.projection_blend = 0.2
            tex_col.image = bpy.data.images.load(basecolor_path)
            links.new(mapping.outputs['Vector'], tex_col.inputs['Vector'])
            
            mix_rgb = nodes.new(type='ShaderNodeMix')
            mix_rgb.data_type = 'RGBA'
            if blend_type == 'MULTIPLY':
                mix_rgb.blend_type = 'MULTIPLY'
            mix_rgb.location = (-50, 200)
            mix_rgb.inputs['Factor'].default_value = tex_mix
            mix_rgb.inputs[6].default_value = (*base_color, 1.0)
            links.new(tex_col.outputs['Color'], mix_rgb.inputs[7])
            links.new(mix_rgb.outputs[2], node_bsdf.inputs['Base Color'])
            
        if os.path.exists(normal_path):
            tex_norm = nodes.new(type='ShaderNodeTexImage')
            tex_norm.location = (-350, -200)
            tex_norm.projection = 'BOX'
            tex_norm.projection_blend = 0.2
            img_norm = bpy.data.images.load(normal_path)
            img_norm.colorspace_settings.name = 'Non-Color'
            tex_norm.image = img_norm
            links.new(mapping.outputs['Vector'], tex_norm.inputs['Vector'])
            
            node_norm = nodes.new(type='ShaderNodeNormalMap')
            node_norm.location = (-100, -200)
            node_norm.inputs['Strength'].default_value = 0.35
            links.new(tex_norm.outputs['Color'], node_norm.inputs['Color'])
            links.new(node_norm.outputs['Normal'], node_bsdf.inputs['Normal'])

    MATS[name] = mat
    return mat

def init_all_materials():
    # 1. Carguero Químico (Industrial Derelict)
    get_stylized_material("Mat_Hazard_Yellow", base_color=(0.95, 0.65, 0.10), roughness=0.35, metallic=0.1, tex_pack="T_Trim_Industrial")
    get_stylized_material("Mat_Rust_Hull", base_color=(0.55, 0.28, 0.16), roughness=0.55, metallic=0.35, tex_pack="T_Derelict_Rust_Plates", tex_mix=0.50)
    get_stylized_material("Mat_Teal_Container", base_color=(0.12, 0.44, 0.42), roughness=0.45, metallic=0.15, tex_pack="T_Battered_Armor_Impacts")
    get_stylized_material("Mat_Orange_Container", base_color=(0.88, 0.36, 0.10), roughness=0.45, metallic=0.15, tex_pack="T_Derelict_Rust_Plates")
    get_stylized_material("Mat_Grate_Steel", base_color=(0.24, 0.26, 0.30), roughness=0.40, metallic=0.75, tex_pack="T_Grating_Walkway")
    
    # Ácido tóxico fluorescente y líquido efervescente (Vibrante verde lima puro, nunca blanco)
    get_stylized_material("Mat_Toxic_Acid", base_color=(0.04, 0.88, 0.14), roughness=0.10, metallic=0.0,
                          emissive_color=(0.05, 0.95, 0.16, 1.0), emissive_strength=1.2)
    get_stylized_material("Mat_Pipe_Olive", base_color=(0.28, 0.38, 0.22), roughness=0.45, metallic=0.45, tex_pack="T_Corroded_Acid_Pipes")
    get_stylized_material("Mat_Valve_Red", base_color=(0.85, 0.12, 0.10), roughness=0.30, metallic=0.2)

    # 2. Crucero Art Déco (Lujo Celestia)
    # Sofá y sillones: Terciopelo burdeos capitoné profundo y regio (#4A0E1C)
    get_stylized_material("Mat_Burgundy_Velvet", base_color=(0.16, 0.008, 0.018), roughness=0.82, metallic=0.0,
                          tex_pack="T_Luxury_Quilted_Velvet_Leather", tex_mix=0.30, blend_type='MULTIPLY')
    # Suelo alfombrado burdeos de lujo
    get_stylized_material("Mat_Burgundy_Carpet", base_color=(0.11, 0.006, 0.014), roughness=0.88, metallic=0.0)
    # Madera de nogal para boiserie y patas
    get_stylized_material("Mat_Mahogany_Wood", base_color=(0.28, 0.12, 0.06), roughness=0.32, metallic=0.0, tex_pack="T_Luxury_Walnut_Wood_Panels")
    # Oro Art Déco pulido reflectante
    get_stylized_material("Mat_ArtDeco_Gold", base_color=(0.95, 0.74, 0.20), roughness=0.22, metallic=0.92, tex_pack="T_Luxury_ArtDeco_Gilded_Brass")
    # Mármol Carrara blanco con veteado noble
    get_stylized_material("Mat_Carrara_Marble", base_color=(0.85, 0.85, 0.83), roughness=0.18, metallic=0.0, tex_pack="T_Luxury_Marble_Gold_Inlay")
    get_stylized_material("Mat_Mirror_Glass", base_color=(0.90, 0.94, 0.96), roughness=0.05, metallic=0.98)
    get_stylized_material("Mat_Lamp_Glow", base_color=(1.0, 0.88, 0.62), roughness=0.2, metallic=0.0,
                          emissive_color=(1.0, 0.88, 0.62, 1.0), emissive_strength=2.2)
    # Espacio cósmico con Saturno y nebulosa
    get_stylized_material("Mat_Cosmic_Sky", base_color=(0.02, 0.03, 0.08), roughness=0.8, metallic=0.0,
                          emissive_color=(0.03, 0.05, 0.15, 1.0), emissive_strength=1.0)
    get_stylized_material("Mat_Saturn_Planet", base_color=(0.85, 0.68, 0.42), roughness=0.4, metallic=0.0,
                          emissive_color=(0.85, 0.68, 0.42, 1.0), emissive_strength=1.2)
    get_stylized_material("Mat_Saturn_Rings", base_color=(0.70, 0.80, 0.92), roughness=0.3, metallic=0.0,
                          emissive_color=(0.70, 0.80, 0.92, 1.0), emissive_strength=1.4)

    # 3. Refinería de Plasma (Alta Tensión)
    get_stylized_material("Mat_Plasma_DarkSteel", base_color=(0.16, 0.20, 0.25), roughness=0.35, metallic=0.85, tex_pack="T_Props_Machinery")
    get_stylized_material("Mat_Plasma_CyanCore", base_color=(0.0, 0.88, 1.0), roughness=0.08, metallic=0.0,
                          emissive_color=(0.0, 0.90, 1.0, 1.0), emissive_strength=2.4)
    get_stylized_material("Mat_Plasma_WhiteFlare", base_color=(0.88, 0.96, 1.0), roughness=0.05, metallic=0.0,
                          emissive_color=(0.95, 0.98, 1.0, 1.0), emissive_strength=2.8)
    get_stylized_material("Mat_Warning_Sign", base_color=(0.95, 0.80, 0.10), roughness=0.3, metallic=0.1,
                          emissive_color=(0.95, 0.80, 0.10, 1.0), emissive_strength=1.4)

    # 4. Mecánica & Chatarra (Enemigos)
    get_stylized_material("Mat_Gunmetal", base_color=(0.26, 0.28, 0.32), roughness=0.35, metallic=0.85, tex_pack="T_Steel_Plates")
    get_stylized_material("Mat_Polished_Steel", base_color=(0.78, 0.82, 0.86), roughness=0.15, metallic=0.95)
    get_stylized_material("Mat_Comic_Flame_Yellow", base_color=(1.0, 0.88, 0.12), roughness=0.2, metallic=0.0,
                          emissive_color=(1.0, 0.88, 0.12, 1.0), emissive_strength=2.2)
    get_stylized_material("Mat_Comic_Flame_Orange", base_color=(0.95, 0.30, 0.03), roughness=0.2, metallic=0.0,
                          emissive_color=(0.95, 0.30, 0.03, 1.0), emissive_strength=1.8)
    get_stylized_material("Mat_Red_Camera_Lens", base_color=(0.95, 0.04, 0.08), roughness=0.1, metallic=0.1,
                          emissive_color=(1.0, 0.06, 0.10, 1.0), emissive_strength=2.8)
    get_stylized_material("Mat_Brass_Gauge", base_color=(0.88, 0.68, 0.24), roughness=0.25, metallic=0.88, tex_pack="T_Luxury_ArtDeco_Gilded_Brass")
    get_stylized_material("Mat_Gauge_Dial_White", base_color=(0.92, 0.92, 0.88), roughness=0.35, metallic=0.0)

    # Escenografía y Showroom
    get_stylized_material("Mat_Pedestal_Base", base_color=(0.06, 0.07, 0.09), roughness=0.45, metallic=0.5)
    get_stylized_material("Mat_Studio_Floor", base_color=(0.015, 0.02, 0.028), roughness=0.25, metallic=0.8)
    get_stylized_material("Mat_Plaque_Brass", base_color=(0.92, 0.74, 0.25), roughness=0.22, metallic=0.92)

# ==============================================================================
# CONSTRUCTORES GEOMÉTRICOS BMESH Y GESTOR DE JERARQUÍA MODULAR
# ==============================================================================
def create_box(name, size=(1,1,1), mat=None, bevel=True, bevel_w=0.02):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=size, verts=bm.verts)
    bm.to_mesh(mesh)
    bm.free()
    if mat:
        mesh.materials.append(mat)
    if bevel:
        add_bevel(obj, width=bevel_w)
    return obj

def create_cylinder(name, radius=0.5, depth=1.0, segments=24, mat=None, bevel=True, bevel_w=0.015):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=segments, radius1=radius, radius2=radius, depth=depth)
    bm.to_mesh(mesh)
    bm.free()
    if mat:
        mesh.materials.append(mat)
    if bevel:
        add_bevel(obj, width=bevel_w)
    return obj

def create_torus(name, major_r=1.0, minor_r=0.2, major_seg=32, minor_seg=16, mat=None):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bm = bmesh.new()
    verts = []
    for i in range(major_seg):
        u = 2.0 * math.pi * i / major_seg
        cos_u = math.cos(u)
        sin_u = math.sin(u)
        for j in range(minor_seg):
            v = 2.0 * math.pi * j / minor_seg
            x = (major_r + minor_r * math.cos(v)) * cos_u
            y = (major_r + minor_r * math.cos(v)) * sin_u
            z = minor_r * math.sin(v)
            verts.append(bm.verts.new((x, y, z)))
    bm.verts.ensure_lookup_table()
    for i in range(major_seg):
        next_i = (i + 1) % major_seg
        for j in range(minor_seg):
            next_j = (j + 1) % minor_seg
            v0 = verts[i * minor_seg + j]
            v1 = verts[next_i * minor_seg + j]
            v2 = verts[next_i * minor_seg + next_j]
            v3 = verts[i * minor_seg + next_j]
            bm.faces.new((v0, v1, v2, v3))
    bm.to_mesh(mesh)
    bm.free()
    if mat:
        mesh.materials.append(mat)
    return obj

def create_cone(name, radius1=0.2, radius2=0.0, depth=0.8, segments=8, mat=None):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=segments, radius1=radius1, radius2=radius2, depth=depth)
    bm.to_mesh(mesh)
    bm.free()
    if mat:
        mesh.materials.append(mat)
    return obj

def assemble_asset(name, parts, col, location=(0,0,0), rotation=(0,0,0)):
    root = bpy.data.objects.new(name, None)
    root.empty_display_type = 'PLAIN_AXES'
    root.empty_display_size = 0.4
    col.objects.link(root)
    root.location = Vector(location)
    root.rotation_euler = Euler((R(rotation[0]), R(rotation[1]), R(rotation[2])), 'XYZ')
    
    for part in parts:
        col.objects.link(part)
        part.parent = root
        
    return root

# ==============================================================================
# KIT 1: CARGUERO QUÍMICO (DERELICT & TOXIC INDUSTRIAL)
# ==============================================================================
def build_container_teu(col, loc=(0,0,0), rot=(0,0,0)):
    parts = []
    body = create_box("Container_Body", size=(1.8, 3.2, 1.8), mat=MATS["Mat_Teal_Container"], bevel=False)
    parts.append(body)
    
    for side in [-0.91, 0.91]:
        for i in range(-3, 4):
            rib = create_box("Rib", size=(0.04, 0.14, 1.68), mat=MATS["Mat_Teal_Container"], bevel=True, bevel_w=0.01)
            rib.location = (side, i * 0.42, 0)
            parts.append(rib)
            
    for x in [-0.92, 0.92]:
        for y in [-1.62, 1.62]:
            pillar = create_box("ISO_CornerPillar", size=(0.14, 0.14, 1.85), mat=MATS["Mat_Orange_Container"])
            pillar.location = (x, y, 0)
            parts.append(pillar)
            for z in [-0.9, 0.9]:
                iso_block = create_box("ISO_Block", size=(0.18, 0.18, 0.18), mat=MATS["Mat_Hazard_Yellow"])
                iso_block.location = (x, y, z)
                parts.append(iso_block)
                
    door_frame = create_box("Door_Frame", size=(1.7, 0.08, 1.7), mat=MATS["Mat_Rust_Hull"])
    door_frame.location = (0, -1.62, 0)
    parts.append(door_frame)
    for bx in [-0.35, 0.35]:
        lock_bar = create_cylinder("Lock_Bar", radius=0.03, depth=1.6, mat=MATS["Mat_Hazard_Yellow"])
        lock_bar.location = (bx, -1.68, 0)
        parts.append(lock_bar)

    return assemble_asset("SM_Contenedor_Espacial_TEU", parts, col, loc, rot)

def build_acid_vat(col, loc=(0,0,0), rot=(0,0,0)):
    parts = []
    # Cuba industrial de corte seccional abierto: Se aprecia directamente el líquido verde y el interior
    back = create_box("Vat_Back", size=(2.0, 0.12, 1.2), mat=MATS["Mat_Rust_Hull"], bevel=True, bevel_w=0.01)
    back.location = (0, 0.60, 0.60)
    parts.append(back)
    
    bottom = create_box("Vat_Bottom", size=(2.0, 1.2, 0.12), mat=MATS["Mat_Rust_Hull"], bevel=True, bevel_w=0.01)
    bottom.location = (0, 0, 0.06)
    parts.append(bottom)
    
    for side_x in [-1.0, 1.0]:
        side_w = create_box("Vat_Side", size=(0.12, 1.2, 1.2), mat=MATS["Mat_Rust_Hull"], bevel=True, bevel_w=0.01)
        side_w.location = (side_x, 0, 0.60)
        parts.append(side_w)
        
    # Marco frontal y montantes de refuerzo en amarillo industrial (Sin cristal opaco que lo bloquee)
    for rib_x in [-1.04, 0.0, 1.04]:
        v_rib = create_box(f"Rib_V_{rib_x}", size=(0.08, 0.12, 1.25), mat=MATS["Mat_Hazard_Yellow"])
        v_rib.location = (rib_x, -0.62, 0.60)
        parts.append(v_rib)
        
    top_rim = create_box("Top_Rim", size=(2.16, 0.12, 0.08), mat=MATS["Mat_Hazard_Yellow"])
    top_rim.location = (0, -0.62, 1.22)
    parts.append(top_rim)

    bottom_rim = create_box("Bottom_Rim", size=(2.16, 0.12, 0.14), mat=MATS["Mat_Hazard_Yellow"])
    bottom_rim.location = (0, -0.62, 0.07)
    parts.append(bottom_rim)
    
    # Volumen interior de líquido ácido verde radiactivo vibrante (#15FF30)
    acid_vol = create_box("Acid_Volume", size=(1.88, 1.05, 0.70), mat=MATS["Mat_Toxic_Acid"], bevel=False)
    acid_vol.location = (0, -0.05, 0.40)
    parts.append(acid_vol)
    
    # Escalera interior de inspección sumergida en el ácido (Fiel al concept art)
    for lz in [0.25, 0.45, 0.65, 0.85, 1.05]:
        rung = create_cylinder(f"Ladder_Rung_{lz}", radius=0.022, depth=0.45, segments=10, mat=MATS["Mat_Hazard_Yellow"])
        rung.rotation_euler = Euler((0, R(90), 0))
        rung.location = (0.75, 0.50, lz)
        parts.append(rung)
        
    # Burbujas tóxicas efervescentes en la superficie
    bubble_coords = [(-0.5, -0.2, 0.78, 0.11), (0.4, 0.15, 0.80, 0.14), (0.05, -0.1, 0.77, 0.09), (-0.2, 0.25, 0.79, 0.12)]
    for bx, by, bz, br in bubble_coords:
        bub = create_cylinder(f"Bubble_{bx}", radius=br, depth=br*1.2, segments=12, mat=MATS["Mat_Toxic_Acid"])
        bub.location = (bx, by, bz)
        parts.append(bub)

    # Vapores / Humo verde estilizado cónico que asciende del ácido
    for vx, vy, vz, vr in [(-0.35, 0.05, 1.25, 0.18), (0.35, -0.1, 1.35, 0.22)]:
        fume = create_cone("Acid_Fume", radius1=vr, radius2=0.02, depth=0.55, segments=8, mat=MATS["Mat_Toxic_Acid"])
        fume.location = (vx, vy, vz)
        parts.append(fume)

    # Rótulo de Advertencia industrial en el travesaño frontal
    sign = create_box("Sign_Plate", size=(1.2, 0.04, 0.18), mat=MATS["Mat_Hazard_Yellow"])
    sign.location = (0, -0.66, 0.95)
    parts.append(sign)

    return assemble_asset("SM_Tanque_Acido_Radiactivo", parts, col, loc, rot)

def build_cargo_crane_arm(col, loc=(0,0,0), rot=(0,0,0)):
    parts = []
    # Brazo Grúa / Pescante de Carga Industrial
    base_swivel = create_cylinder("Crane_Base", radius=0.35, depth=0.5, segments=20, mat=MATS["Mat_Rust_Hull"])
    base_swivel.location = (0, 0, 0.25)
    parts.append(base_swivel)
    
    mast = create_box("Crane_Mast", size=(0.28, 0.28, 1.8), mat=MATS["Mat_Hazard_Yellow"])
    mast.location = (0, 0, 1.35)
    parts.append(mast)
    
    hinge = create_cylinder("Crane_Hinge", radius=0.18, depth=0.36, segments=16, mat=MATS["Mat_Gunmetal"])
    hinge.rotation_euler = Euler((0, R(90), 0))
    hinge.location = (0, 0, 2.25)
    parts.append(hinge)
    
    boom = create_box("Crane_Boom", size=(0.22, 1.9, 0.22), mat=MATS["Mat_Hazard_Yellow"])
    boom.rotation_euler = Euler((R(-28), 0, 0))
    boom.location = (0, 0.85, 2.70)
    parts.append(boom)
    
    hydraulic = create_cylinder("Crane_Hydraulic", radius=0.08, depth=1.1, segments=14, mat=MATS["Mat_Polished_Steel"])
    hydraulic.rotation_euler = Euler((R(30), 0, 0))
    hydraulic.location = (0, 0.40, 1.95)
    parts.append(hydraulic)
    
    cable = create_cylinder("Hoist_Cable", radius=0.02, depth=0.9, segments=8, mat=MATS["Mat_Gunmetal"])
    cable.location = (0, 1.65, 2.65)
    parts.append(cable)
    
    spreader = create_box("Spreader_Claw", size=(0.65, 0.45, 0.12), mat=MATS["Mat_Hazard_Yellow"])
    spreader.location = (0, 1.65, 2.15)
    parts.append(spreader)
    
    return assemble_asset("SM_Brazo_Grua_Industrial", parts, col, loc, rot)

def build_modular_gantry(col, loc=(0,0,0), rot=(0,0,0)):
    parts = []
    floor = create_box("Gantry_Floor", size=(2.4, 0.95, 0.12), mat=MATS["Mat_Grate_Steel"])
    floor.location = (0, 0, 0.06)
    parts.append(floor)
    
    for y_edge in [-0.46, 0.46]:
        curb = create_box("Curb", size=(2.44, 0.06, 0.14), mat=MATS["Mat_Hazard_Yellow"])
        curb.location = (0, y_edge, 0.07)
        parts.append(curb)
        
    for y_side in [-0.46, 0.46]:
        for x_post in [-1.1, -0.55, 0, 0.55, 1.1]:
            post = create_cylinder("Rail_Post", radius=0.028, depth=0.95, segments=12, mat=MATS["Mat_Hazard_Yellow"])
            post.location = (x_post, y_side, 0.58)
            parts.append(post)
        for z_rail in [0.60, 1.02]:
            rail = create_cylinder("Rail_Bar", radius=0.022, depth=2.4, segments=12, mat=MATS["Mat_Polished_Steel"])
            rail.rotation_euler = Euler((0, R(90), 0))
            rail.location = (0, y_side, z_rail)
            parts.append(rail)

    return assemble_asset("SM_Pasarela_Modular_Industrial", parts, col, loc, rot)

def build_heavy_i_beam(col, loc=(0,0,0), rot=(0,0,0)):
    parts = []
    web = create_box("Beam_Web", size=(0.09, 0.38, 3.2), mat=MATS["Mat_Hazard_Yellow"])
    web.location = (0, 0, 1.6)
    parts.append(web)
    for x_flange in [-0.18, 0.18]:
        flange = create_box("Beam_Flange", size=(0.38, 0.07, 3.2), mat=MATS["Mat_Hazard_Yellow"])
        flange.location = (x_flange, 0, 1.6)
        parts.append(flange)
    base_plate = create_box("Base_Plate", size=(0.75, 0.55, 0.08), mat=MATS["Mat_Gunmetal"])
    base_plate.location = (0, 0, 0.04)
    parts.append(base_plate)
    return assemble_asset("SM_Viga_I_Industrial", parts, col, loc, rot)

def build_toxic_barrel_cluster(col, loc=(0,0,0), rot=(0,0,0)):
    parts = []
    barrel_positions = [(-0.35, -0.2, 0.45), (0.35, -0.2, 0.45), (0.0, 0.3, 0.45)]
    for i, b_pos in enumerate(barrel_positions):
        b_body = create_cylinder(f"Barrel_{i}", radius=0.30, depth=0.9, segments=20, mat=MATS["Mat_Pipe_Olive"])
        b_body.location = b_pos
        parts.append(b_body)
        for z_rim in [-0.3, 0.0, 0.3]:
            rim = create_cylinder(f"Rim_{i}_{z_rim}", radius=0.32, depth=0.05, segments=20, mat=MATS["Mat_Hazard_Yellow"])
            rim.location = (b_pos[0], b_pos[1], b_pos[2] + z_rim)
            parts.append(rim)
    # Charco de ácido verde fluorescente en el suelo
    spill = create_cylinder("Acid_Spill", radius=0.85, depth=0.015, segments=16, mat=MATS["Mat_Toxic_Acid"], bevel=False)
    spill.location = (0, 0, 0.01)
    parts.append(spill)
    return assemble_asset("SM_Bateria_Barriles_Toxicos", parts, col, loc, rot)

# ==============================================================================
# KIT 2: CRUCERO DE LUJO (ART DÉCO CELESTIA)
# ==============================================================================
def build_artdeco_armchair(col, loc=(0,0,0), rot=(0,0,0)):
    parts = []
    seat = create_box("Chair_Seat", size=(0.76, 0.70, 0.22), mat=MATS["Mat_Burgundy_Velvet"], bevel=True, bevel_w=0.04)
    seat.location = (0, 0, 0.38)
    parts.append(seat)
    
    back_main = create_box("Back_Center", size=(0.78, 0.18, 0.65), mat=MATS["Mat_Burgundy_Velvet"], bevel=True, bevel_w=0.05)
    back_main.location = (0, 0.30, 0.65)
    parts.append(back_main)
    
    for side in [-0.42, 0.42]:
        arm = create_box("Armrest", size=(0.18, 0.68, 0.42), mat=MATS["Mat_Burgundy_Velvet"], bevel=True, bevel_w=0.04)
        arm.location = (side, 0.05, 0.52)
        parts.append(arm)
        
    leg_coords = [(-0.32, -0.28), (0.32, -0.28), (-0.32, 0.28), (0.32, 0.28)]
    for lx, ly in leg_coords:
        leg = create_cylinder("Wood_Leg", radius=0.035, depth=0.28, segments=12, mat=MATS["Mat_Mahogany_Wood"])
        leg.location = (lx, ly, 0.14)
        parts.append(leg)
        brass_cap = create_cylinder("Brass_Cap", radius=0.04, depth=0.08, segments=12, mat=MATS["Mat_ArtDeco_Gold"])
        brass_cap.location = (lx, ly, 0.04)
        parts.append(brass_cap)

    return assemble_asset("SM_Sillon_ArtDeco_Chesterfield", parts, col, loc, rot)

def build_artdeco_sofa(col, loc=(0,0,0), rot=(0,0,0)):
    parts = []
    seat = create_box("Sofa_Seat", size=(1.62, 0.72, 0.22), mat=MATS["Mat_Burgundy_Velvet"], bevel=True, bevel_w=0.04)
    seat.location = (0, 0, 0.38)
    parts.append(seat)
    
    back = create_box("Sofa_Back", size=(1.64, 0.18, 0.65), mat=MATS["Mat_Burgundy_Velvet"], bevel=True, bevel_w=0.05)
    back.location = (0, 0.30, 0.65)
    parts.append(back)
    
    for side in [-0.85, 0.85]:
        arm = create_box("Sofa_Arm", size=(0.18, 0.70, 0.42), mat=MATS["Mat_Burgundy_Velvet"], bevel=True, bevel_w=0.04)
        arm.location = (side, 0.05, 0.52)
        parts.append(arm)
        
    leg_coords = [(-0.72, -0.28), (0.72, -0.28), (-0.72, 0.28), (0.72, 0.28), (0, -0.28), (0, 0.28)]
    for lx, ly in leg_coords:
        leg = create_cylinder("Sofa_Leg", radius=0.035, depth=0.28, segments=12, mat=MATS["Mat_Mahogany_Wood"])
        leg.location = (lx, ly, 0.14)
        parts.append(leg)
        brass_cap = create_cylinder("Brass_Cap", radius=0.04, depth=0.08, segments=12, mat=MATS["Mat_ArtDeco_Gold"])
        brass_cap.location = (lx, ly, 0.04)
        parts.append(brass_cap)

    return assemble_asset("SM_Sofa_Doble_ArtDeco", parts, col, loc, rot)

def build_artdeco_marble_table(col, loc=(0,0,0), rot=(0,0,0)):
    parts = []
    top = create_cylinder("Marble_Top", radius=0.55, depth=0.05, segments=36, mat=MATS["Mat_Carrara_Marble"], bevel=True, bevel_w=0.01)
    top.location = (0, 0, 0.48)
    parts.append(top)
    
    gold_rim = create_cylinder("Gold_Rim", radius=0.57, depth=0.04, segments=36, mat=MATS["Mat_ArtDeco_Gold"])
    gold_rim.location = (0, 0, 0.46)
    parts.append(gold_rim)
    
    for i in range(3):
        ang = R(i * 120)
        px = 0.42 * math.cos(ang)
        py = 0.42 * math.sin(ang)
        leg = create_cylinder(f"Table_Leg_{i}", radius=0.025, depth=0.45, segments=12, mat=MATS["Mat_ArtDeco_Gold"])
        leg.location = (px, py, 0.225)
        parts.append(leg)
        
    brace = create_cylinder("Brace_Ring", radius=0.32, depth=0.02, segments=24, mat=MATS["Mat_ArtDeco_Gold"])
    brace.location = (0, 0, 0.18)
    parts.append(brace)

    return assemble_asset("SM_Mesa_Marmol_Oro_ArtDeco", parts, col, loc, rot)

def build_sunburst_mirror(col, loc=(0,0,0), rot=(0,0,0)):
    parts = []
    glass = create_cylinder("Mirror_Glass", radius=0.45, depth=0.02, segments=32, mat=MATS["Mat_Mirror_Glass"])
    glass.rotation_euler = Euler((R(90), 0, 0))
    parts.append(glass)
    
    inner_rim = create_cylinder("Inner_Rim", radius=0.48, depth=0.04, segments=32, mat=MATS["Mat_ArtDeco_Gold"])
    inner_rim.rotation_euler = Euler((R(90), 0, 0))
    parts.append(inner_rim)
    
    for i in range(16):
        ang = R(i * (360 / 16))
        ray_len = 0.45 if (i % 2 == 0) else 0.32
        ray = create_box(f"Ray_{i}", size=(0.05, 0.03, ray_len), mat=MATS["Mat_ArtDeco_Gold"])
        ray.rotation_euler = Euler((0, ang, 0))
        ray.location = ((0.48 + ray_len/2) * math.sin(ang), 0.01, (0.48 + ray_len/2) * math.cos(ang))
        parts.append(ray)

    return assemble_asset("SM_Espejo_Monumental_Solsticio", parts, col, loc, rot)

def build_artdeco_chandelier(col, loc=(0,0,0), rot=(0,0,0)):
    parts = []
    radii = [(0.58, 0.12, 0.0), (0.40, 0.12, -0.12), (0.24, 0.12, -0.24)]
    for idx, (rad, h, z_off) in enumerate(radii):
        tier_rim = create_cylinder(f"Tier_Rim_{idx}", radius=rad, depth=0.035, segments=32, mat=MATS["Mat_ArtDeco_Gold"])
        tier_rim.location = (0, 0, z_off)
        parts.append(tier_rim)
        glow = create_cylinder(f"Tier_Glow_{idx}", radius=rad*0.92, depth=h, segments=32, mat=MATS["Mat_Lamp_Glow"], bevel=False)
        glow.location = (0, 0, z_off - h/2)
        parts.append(glow)
    stem = create_cylinder("Stem", radius=0.028, depth=0.5, segments=12, mat=MATS["Mat_ArtDeco_Gold"])
    stem.location = (0, 0, 0.25)
    parts.append(stem)

    return assemble_asset("SM_Lampara_Arana_Ziggurat", parts, col, loc, rot)

def build_artdeco_floor_lamp(col, loc=(0,0,0), rot=(0,0,0)):
    parts = []
    base = create_box("Lamp_Base", size=(0.35, 0.35, 0.06), mat=MATS["Mat_ArtDeco_Gold"])
    base.location = (0, 0, 0.03)
    parts.append(base)
    pole = create_cylinder("Lamp_Pole", radius=0.025, depth=1.6, segments=16, mat=MATS["Mat_ArtDeco_Gold"])
    pole.location = (0, 0, 0.83)
    parts.append(pole)
    shade = create_cylinder("Lamp_Shade", radius=0.22, depth=0.28, segments=24, mat=MATS["Mat_Lamp_Glow"])
    shade.location = (0, 0, 1.65)
    parts.append(shade)

    return assemble_asset("SM_Lampara_Pie_Salon", parts, col, loc, rot)

def build_artdeco_wall_boiserie(col, loc=(0,0,0), rot=(0,0,0)):
    parts = []
    panel = create_box("Wood_Panel", size=(2.8, 0.12, 2.9), mat=MATS["Mat_Mahogany_Wood"])
    panel.location = (0, 0, 1.45)
    parts.append(panel)
    for mx in [-0.85, 0.85]:
        mould = create_box(f"Gold_Moulding_{mx}", size=(0.75, 0.04, 1.9), mat=MATS["Mat_ArtDeco_Gold"])
        mould.location = (mx, -0.07, 1.45)
        parts.append(mould)
        center_gem = create_box(f"Gold_Diamond_{mx}", size=(0.22, 0.05, 0.22), mat=MATS["Mat_ArtDeco_Gold"])
        center_gem.rotation_euler = Euler((0, R(45), 0))
        center_gem.location = (mx, -0.09, 1.45)
        parts.append(center_gem)

    # Base de Alfombra Burdeos Noble (#1F0208)
    carpet = create_box("Carpet_Base", size=(3.8, 2.9, 0.015), mat=MATS["Mat_Burgundy_Carpet"], bevel=False)
    carpet.location = (0, -1.85, 0.115)
    parts.append(carpet)
    
    # Cenefas geométricas doradas Art Déco sobre la alfombra
    gold_border = create_box("Carpet_Gold_Border", size=(3.6, 2.7, 0.005), mat=MATS["Mat_ArtDeco_Gold"], bevel=False)
    gold_border.location = (0, -1.85, 0.124)
    parts.append(gold_border)
    
    inner_carpet = create_box("Carpet_Inner", size=(3.3, 2.4, 0.006), mat=MATS["Mat_Burgundy_Carpet"], bevel=False)
    inner_carpet.location = (0, -1.85, 0.126)
    parts.append(inner_carpet)

    # Medallón geométrico de greca dorada Art Déco
    for r_idx in range(3):
        w = 1.6 - r_idx * 0.4
        d = 1.0 - r_idx * 0.3
        medallion = create_box(f"Medallion_{r_idx}", size=(w, d, 0.003), mat=MATS["Mat_ArtDeco_Gold"], bevel=False)
        medallion.location = (0, -1.85, 0.128 + r_idx * 0.002)
        parts.append(medallion)

    return assemble_asset("SM_Panel_Boiserie_ArtDeco", parts, col, loc, rot)

def build_arched_observatory_window(col, loc=(0,0,0), rot=(0,0,0)):
    parts = []
    # Ventanal Monumental Arqueado al Espacio
    outer_arch = create_cylinder("Window_Backdrop", radius=1.65, depth=0.08, segments=36, mat=MATS["Mat_Cosmic_Sky"])
    outer_arch.rotation_euler = Euler((R(90), 0, 0))
    outer_arch.location = (0, 0.04, 1.65)
    parts.append(outer_arch)
    
    planet_saturn = create_cylinder("Saturn_Body", radius=0.48, depth=0.02, segments=32, mat=MATS["Mat_Saturn_Planet"])
    planet_saturn.rotation_euler = Euler((R(90), 0, 0))
    planet_saturn.location = (-0.35, 0.02, 1.85)
    parts.append(planet_saturn)
    
    saturn_ring = create_cylinder("Saturn_Ring", radius=0.95, depth=0.008, segments=32, mat=MATS["Mat_Saturn_Rings"])
    saturn_ring.rotation_euler = Euler((R(70), R(25), 0))
    saturn_ring.location = (-0.35, 0.015, 1.85)
    parts.append(saturn_ring)

    # Marco monumental arqueado de latón dorado
    arch_rib1 = create_torus("Arch_Rib_Outer", major_r=1.65, minor_r=0.06, major_seg=36, minor_seg=12, mat=MATS["Mat_ArtDeco_Gold"])
    arch_rib1.rotation_euler = Euler((R(90), 0, 0))
    arch_rib1.location = (0, -0.02, 1.65)
    parts.append(arch_rib1)
    
    arch_rib2 = create_torus("Arch_Rib_Inner", major_r=1.45, minor_r=0.04, major_seg=36, minor_seg=12, mat=MATS["Mat_ArtDeco_Gold"])
    arch_rib2.rotation_euler = Euler((R(90), 0, 0))
    arch_rib2.location = (0, -0.02, 1.65)
    parts.append(arch_rib2)

    return assemble_asset("SM_Ventanal_Arqueado_Observatorio", parts, col, loc, rot)

# ==============================================================================
# KIT 3: REFINERÍA DE PLASMA (NÚCLEO ENERGÉTICO & CONDUCCIÓN)
# ==============================================================================
def build_plasma_reactor(col, loc=(0,0,0), rot=(0,0,0)):
    parts = []
    outer_torus = create_torus("Outer_Torus", major_r=1.35, minor_r=0.28, major_seg=36, minor_seg=16, mat=MATS["Mat_Plasma_DarkSteel"])
    outer_torus.rotation_euler = Euler((R(90), 0, 0))
    parts.append(outer_torus)
    
    for i in range(6):
        ang = R(i * 60)
        clamp = create_box(f"Clamp_{i}", size=(0.35, 0.65, 0.40), mat=MATS["Mat_Hazard_Yellow"])
        clamp.location = (1.35 * math.cos(ang), 0, 1.35 * math.sin(ang))
        clamp.rotation_euler = Euler((0, -ang, 0))
        parts.append(clamp)
        
    plasma_ring = create_torus("Plasma_Ring", major_r=1.0, minor_r=0.18, major_seg=32, minor_seg=12, mat=MATS["Mat_Plasma_CyanCore"])
    plasma_ring.rotation_euler = Euler((R(90), 0, 0))
    parts.append(plasma_ring)
    
    flare = create_cylinder("Central_Singularity", radius=0.42, depth=0.08, segments=24, mat=MATS["Mat_Plasma_WhiteFlare"], bevel=False)
    flare.rotation_euler = Euler((R(90), 0, 0))
    parts.append(flare)

    for i in range(4):
        ang = R(i * 90 + 25)
        arc = create_box(f"LightningArc_{i}", size=(0.04, 0.04, 0.9), mat=MATS["Mat_Plasma_WhiteFlare"])
        arc.rotation_euler = Euler((R(90), ang, R(15)))
        parts.append(arc)

    base_block = create_box("Reactor_Pedestal", size=(1.8, 0.9, 0.6), mat=MATS["Mat_Plasma_DarkSteel"])
    base_block.location = (0, 0, -1.35)
    parts.append(base_block)

    return assemble_asset("SM_Generador_Toroidal_Plasma", parts, col, loc, rot)

def build_plasma_conduit_manifold(col, loc=(0,0,0), rot=(0,0,0)):
    parts = []
    main_pipe = create_cylinder("Main_Pipe", radius=0.22, depth=2.4, segments=24, mat=MATS["Mat_Plasma_DarkSteel"])
    main_pipe.location = (0, 0, 1.2)
    parts.append(main_pipe)
    
    for z_flange in [0.3, 1.2, 2.1]:
        flange = create_cylinder(f"Flange_{z_flange}", radius=0.32, depth=0.08, segments=24, mat=MATS["Mat_Hazard_Yellow"])
        flange.location = (0, 0, z_flange)
        parts.append(flange)
        
    elbow_pipe = create_cylinder("Elbow_Pipe", radius=0.16, depth=1.3, segments=20, mat=MATS["Mat_Plasma_DarkSteel"])
    elbow_pipe.rotation_euler = Euler((0, R(90), 0))
    elbow_pipe.location = (0.65, 0, 1.8)
    parts.append(elbow_pipe)
    
    sight_glass = create_cylinder("Sight_Glass", radius=0.18, depth=0.32, segments=16, mat=MATS["Mat_Plasma_CyanCore"])
    sight_glass.rotation_euler = Euler((0, R(90), 0))
    sight_glass.location = (0.65, 0, 1.8)
    parts.append(sight_glass)

    return assemble_asset("SM_Bateria_Tuberias_Colector", parts, col, loc, rot)

def build_plasma_terminal_console(col, loc=(0,0,0), rot=(0,0,0)):
    parts = []
    base = create_box("Console_Desk", size=(1.2, 0.75, 0.82), mat=MATS["Mat_Plasma_DarkSteel"])
    base.location = (0, 0, 0.41)
    parts.append(base)
    hood = create_box("Console_Hood", size=(1.15, 0.38, 0.52), mat=MATS["Mat_Gunmetal"])
    hood.location = (0, 0.16, 1.05)
    hood.rotation_euler = Euler((R(-15), 0, 0))
    parts.append(hood)
    screen = create_box("CRT_Screen", size=(0.7, 0.05, 0.32), mat=MATS["Mat_Plasma_CyanCore"], bevel=False)
    screen.location = (0, 0.02, 1.05)
    screen.rotation_euler = Euler((R(-15), 0, 0))
    parts.append(screen)
    estop = create_cylinder("Estop_Button", radius=0.06, depth=0.06, segments=12, mat=MATS["Mat_Red_Camera_Lens"])
    estop.location = (0.42, -0.15, 0.85)
    parts.append(estop)

    return assemble_asset("SM_Consola_Control_Plasma", parts, col, loc, rot)

def build_hazard_signboard(col, loc=(0,0,0), rot=(0,0,0)):
    parts = []
    plate = create_box("Sign_Plate", size=(1.1, 0.06, 0.75), mat=MATS["Mat_Warning_Sign"])
    plate.location = (0, 0, 0.375)
    parts.append(plate)
    frame = create_box("Sign_Frame", size=(1.16, 0.04, 0.81), mat=MATS["Mat_Plasma_DarkSteel"])
    frame.location = (0, -0.01, 0.375)
    parts.append(frame)
    for sy in [-0.22, 0.0, 0.22]:
        stripe = create_box(f"Stripe_{sy}", size=(0.95, 0.07, 0.08), mat=MATS["Mat_Gunmetal"], bevel=False)
        stripe.location = (0, 0.02, 0.375 + sy)
        parts.append(stripe)

    return assemble_asset("SM_Cartelera_Peligro_Plasma", parts, col, loc, rot)

def build_curved_catwalk_module(col, loc=(0,0,0), rot=(0,0,0)):
    parts = []
    # Tramo de pasarela curva de inspección de plasma
    curved_deck = create_cylinder("Curved_Deck", radius=1.6, depth=0.10, segments=28, mat=MATS["Mat_Grate_Steel"])
    curved_deck.location = (0, 0, 0.05)
    parts.append(curved_deck)
    inner_hole = create_cylinder("Deck_Hole", radius=1.0, depth=0.14, segments=28, mat=MATS["Mat_Pedestal_Base"])
    inner_hole.location = (0, 0, 0.05)
    parts.append(inner_hole)
    
    # Barandilla exterior curva despejada
    rail = create_torus("Outer_Curved_Rail", major_r=1.55, minor_r=0.025, major_seg=28, minor_seg=8, mat=MATS["Mat_Hazard_Yellow"])
    rail.location = (0, 0, 0.90)
    parts.append(rail)
    
    for ang_deg in [10, 45, 80]:
        ang = R(ang_deg)
        post = create_cylinder(f"Post_{ang_deg}", radius=0.025, depth=0.90, segments=10, mat=MATS["Mat_Hazard_Yellow"])
        post.location = (1.55 * math.cos(ang), 1.55 * math.sin(ang), 0.48)
        parts.append(post)

    return assemble_asset("SM_Modulo_Pasarela_Curva", parts, col, loc, rot)

def build_mining_scout_drone(col, loc=(0,0,0), rot=(0,0,0)):
    parts = []
    core_sphere = create_cylinder("Scout_Hull", radius=0.25, depth=0.35, segments=18, mat=MATS["Mat_Plasma_DarkSteel"])
    core_sphere.location = (0, 0, 0.3)
    parts.append(core_sphere)
    
    eye = create_cylinder("Scout_Eye", radius=0.12, depth=0.08, segments=16, mat=MATS["Mat_Plasma_CyanCore"])
    eye.rotation_euler = Euler((R(90), 0, 0))
    eye.location = (0, -0.18, 0.3)
    parts.append(eye)
    
    for fx in [-0.28, 0.28]:
        fin = create_box(f"Fin_{fx}", size=(0.14, 0.22, 0.04), mat=MATS["Mat_Hazard_Yellow"])
        fin.location = (fx, 0, 0.3)
        parts.append(fin)

    return assemble_asset("SM_Dron_Minero_Observador", parts, col, loc, rot)

# ==============================================================================
# KIT 4: COMPONENTES MECÁNICOS & CHATARRA (ENEMIGOS Y PROPS REUTILIZABLES)
# ==============================================================================
def build_sawblade_24t(col, loc=(0,0,0), rot=(0,0,0)):
    parts = []
    core_disk = create_cylinder("Blade_Core", radius=0.55, depth=0.04, segments=36, mat=MATS["Mat_Gunmetal"])
    core_disk.rotation_euler = Euler((R(90), 0, 0))
    parts.append(core_disk)
    
    for i in range(24):
        ang = R(i * (360 / 24))
        tooth = create_box(f"Tooth_{i}", size=(0.10, 0.038, 0.16), mat=MATS["Mat_Polished_Steel"])
        tx = 0.58 * math.cos(ang)
        tz = 0.58 * math.sin(ang)
        tooth.location = (tx, 0, tz)
        tooth.rotation_euler = Euler((0, -ang + R(25), 0))
        parts.append(tooth)
        
    hub = create_cylinder("Hub_Center", radius=0.18, depth=0.08, segments=20, mat=MATS["Mat_Hazard_Yellow"])
    hub.rotation_euler = Euler((R(90), 0, 0))
    parts.append(hub)
    for b_idx in range(4):
        b_ang = R(b_idx * 90)
        bolt = create_cylinder(f"Bolt_{b_idx}", radius=0.03, depth=0.10, segments=8, mat=MATS["Mat_Polished_Steel"])
        bolt.rotation_euler = Euler((R(90), 0, 0))
        bolt.location = (0.11 * math.cos(b_ang), 0, 0.11 * math.sin(b_ang))
        parts.append(bolt)

    return assemble_asset("SM_Sierra_Circular_24Dientes", parts, col, loc, rot)

def build_hydraulic_piston(col, loc=(0,0,0), rot=(0,0,0)):
    parts = []
    cylinder = create_cylinder("Piston_Barrel", radius=0.14, depth=1.1, segments=20, mat=MATS["Mat_Gunmetal"])
    cylinder.location = (0, 0, 0.55)
    parts.append(cylinder)
    
    rod = create_cylinder("Chrome_Rod", radius=0.075, depth=0.9, segments=20, mat=MATS["Mat_Polished_Steel"])
    rod.location = (0, 0, 1.25)
    parts.append(rod)
    
    clevis_base = create_cylinder("Clevis_Base", radius=0.15, depth=0.18, segments=16, mat=MATS["Mat_Hazard_Yellow"])
    clevis_base.rotation_euler = Euler((0, R(90), 0))
    clevis_base.location = (0, 0, 0.05)
    parts.append(clevis_base)
    
    clevis_top = create_cylinder("Clevis_Top", radius=0.10, depth=0.14, segments=16, mat=MATS["Mat_Hazard_Yellow"])
    clevis_top.rotation_euler = Euler((0, R(90), 0))
    clevis_top.location = (0, 0, 1.70)
    parts.append(clevis_top)
    
    hose = create_torus("Hose_Loop", major_r=0.22, minor_r=0.035, major_seg=20, minor_seg=8, mat=MATS["Mat_Pedestal_Base"])
    hose.location = (0.16, 0, 0.75)
    parts.append(hose)

    return assemble_asset("SM_Piston_Hidraulico_Articulado", parts, col, loc, rot)

def build_spiked_mace(col, loc=(0,0,0), rot=(0,0,0)):
    parts = []
    shaft = create_cylinder("Mace_Shaft", radius=0.035, depth=1.3, segments=12, mat=MATS["Mat_Mahogany_Wood"])
    shaft.location = (0, 0, 0.65)
    parts.append(shaft)
    
    head = create_cylinder("Mace_Head", radius=0.20, depth=0.35, segments=16, mat=MATS["Mat_Gunmetal"])
    head.location = (0, 0, 1.25)
    parts.append(head)
    
    for i in range(8):
        ang = R(i * 45)
        spike = create_cylinder(f"Spike_{i}", radius=0.05, depth=0.18, segments=8, mat=MATS["Mat_Polished_Steel"])
        spike.rotation_euler = Euler((0, -ang + R(90), 0))
        spike.location = (0.26 * math.cos(ang), 0, 1.25 + 0.26 * math.sin(ang))
        parts.append(spike)
        
    top_spike = create_cylinder("Top_Spike", radius=0.06, depth=0.25, segments=8, mat=MATS["Mat_Polished_Steel"])
    top_spike.location = (0, 0, 1.52)
    parts.append(top_spike)

    return assemble_asset("SM_Maza_Puas_Chatarrera", parts, col, loc, rot)

def build_chimney_comic_flames(col, loc=(0,0,0), rot=(0,0,0)):
    parts = []
    angles = [-18, 0, 18]
    x_positions = [-0.35, 0.0, 0.35]
    for i, (ang, xp) in enumerate(zip(angles, x_positions)):
        pipe = create_cylinder(f"Exhaust_{i}", radius=0.09, depth=0.75, segments=16, mat=MATS["Mat_Gunmetal"])
        pipe.rotation_euler = Euler((0, R(ang), 0))
        pipe.location = (xp, 0, 0.4)
        parts.append(pipe)
        
        flame_outer = create_cone(f"Flame_Outer_{i}", radius1=0.17, radius2=0.015, depth=0.85, segments=7, mat=MATS["Mat_Comic_Flame_Orange"])
        flame_outer.rotation_euler = Euler((0, R(ang), 0))
        flame_outer.location = (xp + 0.42 * math.sin(R(ang)), 0, 1.05 + 0.42 * math.cos(R(ang)))
        parts.append(flame_outer)
        
        flame_inner = create_cone(f"Flame_Inner_{i}", radius1=0.11, radius2=0.01, depth=0.55, segments=7, mat=MATS["Mat_Comic_Flame_Yellow"])
        flame_inner.rotation_euler = Euler((0, R(ang), 0))
        flame_inner.location = (xp + 0.38 * math.sin(R(ang)), 0, 0.95 + 0.38 * math.cos(R(ang)))
        parts.append(flame_inner)

    return assemble_asset("SM_Chimeneas_Fuego_Comic", parts, col, loc, rot)

def build_triple_gauge_cluster(col, loc=(0,0,0), rot=(0,0,0)):
    parts = []
    bracket = create_box("Gauge_Bracket", size=(0.65, 0.06, 0.30), mat=MATS["Mat_Gunmetal"])
    bracket.location = (0, 0, 0.15)
    parts.append(bracket)
    
    gauge_x = [-0.22, 0.0, 0.22]
    for i, gx in enumerate(gauge_x):
        body = create_cylinder(f"Gauge_Body_{i}", radius=0.10, depth=0.08, segments=20, mat=MATS["Mat_Brass_Gauge"])
        body.rotation_euler = Euler((R(90), 0, 0))
        body.location = (gx, -0.05, 0.18)
        parts.append(body)
        
        dial = create_cylinder(f"Gauge_Dial_{i}", radius=0.088, depth=0.02, segments=20, mat=MATS["Mat_Gauge_Dial_White"], bevel=False)
        dial.rotation_euler = Euler((R(90), 0, 0))
        dial.location = (gx, -0.09, 0.18)
        parts.append(dial)
        
        needle = create_box(f"Needle_{i}", size=(0.012, 0.01, 0.07), mat=MATS["Mat_Red_Camera_Lens"], bevel=False)
        needle.rotation_euler = Euler((0, R(i * 40 - 20), 0))
        needle.location = (gx, -0.105, 0.20)
        parts.append(needle)

    return assemble_asset("SM_Racor_Triple_Manometros", parts, col, loc, rot)

def build_auditor_drone_sphere(col, loc=(0,0,0), rot=(0,0,0)):
    parts = []
    # Dron Auditor Esférico Blindado (Fiel a media_1791273929163.png)
    hull = create_cylinder("Drone_Hull", radius=0.42, depth=0.60, segments=24, mat=MATS["Mat_Gunmetal"])
    hull.location = (0, 0, 0.45)
    parts.append(hull)
    
    # Bisel y carcasa de latón para el ojo central óptico
    eye_rim = create_cylinder("Eye_Rim", radius=0.22, depth=0.08, segments=20, mat=MATS["Mat_Brass_Gauge"])
    eye_rim.rotation_euler = Euler((R(90), 0, 0))
    eye_rim.location = (0, -0.30, 0.45)
    parts.append(eye_rim)
    
    # Lente roja emisiva brillante profunda (#FF0A1A)
    eye_lens = create_cylinder("Eye_Lens", radius=0.16, depth=0.06, segments=20, mat=MATS["Mat_Red_Camera_Lens"])
    eye_lens.rotation_euler = Euler((R(90), 0, 0))
    eye_lens.location = (0, -0.34, 0.45)
    parts.append(eye_lens)
    
    # 3 Manómetros analógicos de latón en la cúpula superior
    for gx in [-0.18, 0.0, 0.18]:
        gauge = create_cylinder(f"Top_Gauge_{gx}", radius=0.07, depth=0.06, segments=16, mat=MATS["Mat_Brass_Gauge"])
        gauge.location = (gx, 0, 0.80)
        parts.append(gauge)
        
    for sx in [-0.46, 0.46]:
        thruster = create_cylinder(f"Thruster_{sx}", radius=0.11, depth=0.16, segments=16, mat=MATS["Mat_Polished_Steel"])
        thruster.rotation_euler = Euler((0, R(90), 0))
        thruster.location = (sx, 0, 0.45)
        parts.append(thruster)
        
    # Pantalla CRT inferior de telemetría y fósforo verde
    crt = create_box("CRT_Screen", size=(0.26, 0.04, 0.16), mat=MATS["Mat_Toxic_Acid"], bevel=False)
    crt.location = (0, -0.28, 0.18)
    parts.append(crt)

    # Antena lateral de comunicación
    antenna = create_cylinder("Drone_Antenna", radius=0.015, depth=0.45, segments=8, mat=MATS["Mat_Polished_Steel"])
    antenna.rotation_euler = Euler((0, R(-25), 0))
    antenna.location = (-0.35, 0.15, 0.82)
    parts.append(antenna)

    return assemble_asset("SM_Dron_Auditor_Esferico", parts, col, loc, rot)

# ==============================================================================
# ESCENOGRAFÍA MAESTRA: 4 ISLAS DE EXHIBICIÓN Y PEDESTALES CINEMATOGRÁFICOS
# ==============================================================================
def build_exhibition_stage(col, name, center_x, glow_color):
    stage = create_box(f"Stage_{name}", size=(4.2, 3.4, 0.22), mat=MATS["Mat_Pedestal_Base"])
    stage.location = (center_x, 0, 0.11)
    col.objects.link(stage)
    
    led_mat = get_stylized_material(f"Mat_LED_{name}", base_color=glow_color, roughness=0.2,
                                    emissive_color=(*glow_color, 1.0), emissive_strength=2.8)
    led_strip = create_box(f"LED_{name}", size=(4.26, 3.46, 0.04), mat=led_mat, bevel=False)
    led_strip.location = (center_x, 0, 0.02)
    col.objects.link(led_strip)
    
    plaque = create_box(f"Plaque_{name}", size=(2.0, 0.04, 0.14), mat=MATS["Mat_Plaque_Brass"])
    plaque.location = (center_x, -1.72, 0.11)
    col.objects.link(plaque)
    
    return stage

# ==============================================================================
# ILUMINACIÓN DE ESTUDIO CINEMATOGRÁFICA Y CÁMARAS CON TRACKING EXACTO
# ==============================================================================
def setup_studio_lighting(col):
    studio_floor = create_box("Studio_Floor", size=(40.0, 24.0, 0.05), mat=MATS["Mat_Studio_Floor"], bevel=False)
    studio_floor.location = (0, 0, -0.025)
    col.objects.link(studio_floor)

    back_wall = create_box("Studio_Backwall", size=(40.0, 0.1, 10.0), mat=MATS["Mat_Pedestal_Base"], bevel=False)
    back_wall.location = (0, 3.5, 4.8)
    col.objects.link(back_wall)

    # Iluminación equilibrada: Evita quemado de blancos y conserva la riqueza cromática
    sun_data = bpy.data.lights.new(name="Key_Sun", type='SUN')
    sun_data.energy = 2.2
    sun_data.color = (1.0, 0.98, 0.95)
    sun_data.angle = R(15)
    sun_obj = bpy.data.objects.new("Key_Sun", sun_data)
    sun_obj.rotation_euler = Euler((R(48), R(18), R(-32)))
    col.objects.link(sun_obj)
    
    rim_data = bpy.data.lights.new(name="Rim_Backlight", type='SUN')
    rim_data.energy = 1.8
    rim_data.color = (0.65, 0.88, 1.0)
    rim_obj = bpy.data.objects.new("Rim_Backlight", rim_data)
    rim_obj.rotation_euler = Euler((R(-60), R(-15), R(140)))
    col.objects.link(rim_obj)
    
    island_x = [-6.75, -2.25, 2.25, 6.75]
    spot_colors = [
        (1.0, 0.85, 0.6),  # Industrial
        (1.0, 0.92, 0.8),  # Lujo Art Déco
        (0.4, 0.9, 1.0),   # Plasma
        (1.0, 0.75, 0.5)   # Enemigos (fuego forja cálido)
    ]
    for idx, (ix, scol) in enumerate(zip(island_x, spot_colors)):
        sp_data = bpy.data.lights.new(name=f"Spot_Island_{idx}", type='SPOT')
        sp_data.energy = 420.0
        sp_data.spot_size = R(70)
        sp_data.spot_blend = 0.35
        sp_data.color = scol
        sp_obj = bpy.data.objects.new(f"Spot_Island_{idx}", sp_data)
        sp_obj.location = (ix, -3.4, 4.8)
        sp_obj.rotation_euler = Euler((R(52), 0, 0))
        col.objects.link(sp_obj)

def point_camera_at(cam_obj, target_pos):
    direction = Vector(target_pos) - cam_obj.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()

def setup_cameras(col):
    cams = {}
    
    # 1. Cámara Panorama Maestro
    cam_pan_data = bpy.data.cameras.new("Cam_Panorama")
    cam_pan_data.lens = 28.0
    cam_pan_obj = bpy.data.objects.new("Cam_Panorama", cam_pan_data)
    cam_pan_obj.location = Vector((0.0, -17.5, 7.2))
    point_camera_at(cam_pan_obj, (0.0, 0.0, 1.35))
    col.objects.link(cam_pan_obj)
    cams["Panorama"] = cam_pan_obj
    
    # 2. Cámaras Close-Up Axonométricas 3/4
    island_targets = [
        ("Industrial", -6.75, (-6.75, -5.6, 3.4), (-6.75, 0.0, 1.25)),
        ("ArtDeco", -2.25, (-2.25, -5.6, 3.4), (-2.25, 0.0, 1.35)),
        ("Plasma", 2.25, (2.25, -5.6, 3.4), (2.25, 0.0, 1.35)),
        ("Enemigos", 6.75, (6.75, -5.6, 3.4), (6.75, 0.0, 1.30))
    ]
    for name, ix, cam_loc, target_loc in island_targets:
        cdata = bpy.data.cameras.new(f"Cam_{name}")
        cdata.lens = 36.0
        cobj = bpy.data.objects.new(f"Cam_{name}", cdata)
        cobj.location = Vector(cam_loc)
        point_camera_at(cobj, target_loc)
        col.objects.link(cobj)
        cams[name] = cobj
        
    return cams

# ==============================================================================
# EJECUCIÓN PRINCIPAL Y RENDERIZADO
# ==============================================================================
def main():
    print("=" * 80)
    print("CONSTRUYENDO CATÁLOGO MAESTRO DE ACTIVOS 3D MODULARES V5 - ASTRA HAZARD")
    print("=" * 80)
    
    scene = reset_scene()
    init_all_materials()
    
    col_world = create_collection("00_Escenografia_Estudio")
    col_ind = create_collection("01_Kit_Carguero_Quimico")
    col_art = create_collection("02_Kit_Crucero_ArtDeco")
    col_pla = create_collection("03_Kit_Refineria_Plasma")
    col_ene = create_collection("04_Kit_Mecanica_Enemigos")
    
    # 1. Construir las 4 Islas de Exhibición con Iluminación Perimetral
    build_exhibition_stage(col_world, "Industrial", -6.75, (1.0, 0.65, 0.1))
    build_exhibition_stage(col_world, "ArtDeco", -2.25, (0.9, 0.72, 0.2))
    build_exhibition_stage(col_world, "Plasma", 2.25, (0.0, 0.95, 1.0))
    build_exhibition_stage(col_world, "Enemigos", 6.75, (1.0, 0.25, 0.1))
    
    # 2. Instanciar Activos en Isla 1: Carguero Químico (X = -6.75)
    IX1 = -6.75
    # Cuba de Ácido centrada en plano frontal con corte abierto (visión cristalina del líquido verde)
    build_acid_vat(col_ind, loc=(IX1 - 0.25, -0.45, 0.22), rot=(0, 0, 5))
    # Contenedor Espacial TEU en plano posterior
    build_container_teu(col_ind, loc=(IX1 + 0.85, 0.75, 1.05), rot=(0, 0, -15))
    # Brazo Grúa Pescante de Carga en lateral posterior
    build_cargo_crane_arm(col_ind, loc=(IX1 - 1.25, 0.65, 0.22), rot=(0, 0, -35))
    # Pasarela de Rejilla en lateral
    build_modular_gantry(col_ind, loc=(IX1 + 1.25, -0.35, 0.22), rot=(0, 0, 90))
    # Batería de Barriles Tóxicos y Derrame
    build_toxic_barrel_cluster(col_ind, loc=(IX1 - 1.15, -0.65, 0.22), rot=(0, 0, 20))
    # Viga I Industrial con Placa de Pernos
    build_heavy_i_beam(col_ind, loc=(IX1 + 1.35, 0.95, 0.22), rot=(0, 0, 0))
    
    # 3. Instanciar Activos en Isla 2: Crucero Art Déco (X = -2.25)
    IX2 = -2.25
    build_artdeco_wall_boiserie(col_art, loc=(IX2, 1.35, 0.22), rot=(0, 0, 0))
    build_arched_observatory_window(col_art, loc=(IX2, 1.55, 0.22), rot=(0, 0, 0))
    build_sunburst_mirror(col_art, loc=(IX2, 1.20, 1.85), rot=(0, 0, 0))
    build_artdeco_chandelier(col_art, loc=(IX2, 0.0, 3.4), rot=(0, 0, 0))
    build_artdeco_sofa(col_art, loc=(IX2 + 0.75, 0.25, 0.22), rot=(0, 0, -15))
    build_artdeco_armchair(col_art, loc=(IX2 - 0.85, -0.15, 0.22), rot=(0, 0, 25))
    build_artdeco_marble_table(col_art, loc=(IX2 - 0.05, -0.35, 0.22), rot=(0, 0, 0))
    build_artdeco_floor_lamp(col_art, loc=(IX2 - 1.55, 0.65, 0.22), rot=(0, 0, 0))
    
    # 4. Instanciar Activos en Isla 3: Refinería de Plasma (X = 2.25)
    IX3 = 2.25
    # Reactor Toroidal de Plasma (Elevado, centrado y visible)
    build_plasma_reactor(col_pla, loc=(IX3 + 0.15, 0.45, 1.85), rot=(0, 0, -15))
    # Batería Colectora y Tuberías Bridadas
    build_plasma_conduit_manifold(col_pla, loc=(IX3 - 1.25, 0.55, 0.22), rot=(0, 0, 0))
    # Consola Terminal CRT
    build_plasma_terminal_console(col_pla, loc=(IX3 - 0.65, -0.65, 0.22), rot=(0, 0, 15))
    # Cartelera de Peligro Alta Energía
    build_hazard_signboard(col_pla, loc=(IX3 + 1.25, -0.55, 0.22), rot=(0, 0, -20))
    # Tramo de Pasarela Curva de Inspección (Despejado al lateral derecho posterior)
    build_curved_catwalk_module(col_pla, loc=(IX3 + 1.15, 0.45, 0.22), rot=(0, 0, 120))
    # Subdron Minero Observador Flotante
    build_mining_scout_drone(col_pla, loc=(IX3 - 1.05, -0.25, 1.15), rot=(0, 0, 30))
    
    # 5. Instanciar Activos en Isla 4: Mecánica & Enemigos (X = 6.75)
    IX4 = 6.75
    # Dron Auditor Esférico Blindado (Flotante en centro, con su ojo rojo, CRT y manómetros despejados)
    build_auditor_drone_sphere(col_ene, loc=(IX4, 0.0, 1.15), rot=(0, 0, 0))
    # Sierra Circular 24 Dientes Afilados
    build_sawblade_24t(col_ene, loc=(IX4 - 1.15, 0.45, 0.80), rot=(0, 0, 25))
    # Pistón Hidráulico Articulado Cromado
    build_hydraulic_piston(col_ene, loc=(IX4 + 1.25, 0.45, 0.22), rot=(0, 0, 0))
    # Chimeneas de Escape con Fuego Cómic 2D
    build_chimney_comic_flames(col_ene, loc=(IX4 + 0.10, 0.75, 0.22), rot=(0, 0, 0))
    # Maza de Impacto con Púas Cónicas
    build_spiked_mace(col_ene, loc=(IX4 - 1.05, -0.65, 0.22), rot=(0, 0, -15))
    # Racor Triple de Manómetros de Latón
    build_triple_gauge_cluster(col_ene, loc=(IX4 + 1.05, -0.65, 0.22), rot=(0, 0, -25))
    
    # Iluminación y Cámaras
    setup_studio_lighting(col_world)
    cams = setup_cameras(col_world)
    
    # Guardar archivo .blend oficial
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_FILE)
    print(f"\n[OK] Blend file oficial guardado en: {BLEND_FILE}")
    
    # ==============================================================================
    # RENDERIZADO DE LAS 5 TOMAS CINEMATOGRÁFICAS
    # ==============================================================================
    render_jobs = [
        ("Panorama", "Showcase_Catalogo_Modular_Panorama.png", 2480, 780),
        ("Industrial", "Showcase_Modular_Kit_Industrial.png", 1280, 720),
        ("ArtDeco", "Showcase_Modular_Kit_ArtDeco.png", 1280, 720),
        ("Plasma", "Showcase_Modular_Kit_Plasma.png", 1280, 720),
        ("Enemigos", "Showcase_Modular_Kit_Enemigos_Mecanica.png", 1280, 720)
    ]
    
    for cam_key, filename, w, h in render_jobs:
        out_path = os.path.join(RENDERS_DIR, filename)
        scene.camera = cams[cam_key]
        scene.render.resolution_x = w
        scene.render.resolution_y = h
        scene.render.resolution_percentage = 100
        scene.render.filepath = out_path
        
        print(f"  [RENDER] Generando {filename} ({w}x{h})...")
        bpy.ops.render.render(write_still=True)
        print(f"  [OK] Guardado: {out_path}")
        
    assemble_master_infographic()

def assemble_master_infographic():
    print("\n[COMPOSITOR] Ensamblando Lámina Maestra Infográfica 2.5K (2560x1440)...")
    
    W, H = 2560, 1440
    canvas = Image.new("RGBA", (W, H), (14, 16, 20, 255))
    draw = ImageDraw.Draw(canvas)
    
    try:
        font_title = ImageFont.truetype("arialbd.ttf", 30)
        font_sub = ImageFont.truetype("arialbd.ttf", 18)
        font_pill = ImageFont.truetype("arialbd.ttf", 15)
        font_card_title = ImageFont.truetype("arialbd.ttf", 20)
        font_card_desc = ImageFont.truetype("arial.ttf", 14)
    except:
        font_title = font_sub = font_pill = font_card_title = font_card_desc = ImageFont.load_default()
        
    # Encabezado
    draw.text((40, 20), "ASTRA HAZARD // REPOSITORIO DE ARQUITECTURA Y ACTIVOS 3D MODULARES", fill=(245, 166, 35), font=font_sub)
    draw.text((40, 48), "CATÁLOGO MAESTRO DE ACTIVOS 3D MODULARES (V5): KITS TIER 1, 2, 3 Y MECÁNICA", fill=(255, 255, 255), font=font_title)
    
    # Badges / Pills
    pills = [
        ("DESCOMPOSICIÓN 1:1 MAPAS", (211, 84, 0)),
        ("26 ASSETS MODULARES REUTILIZABLES", (41, 128, 185)),
        ("15 PACKS PBR APLICADOS", (39, 174, 96)),
        ("FREESTYLE INK LINEART", (142, 68, 173)),
        ("BLENDER 5.2 LTS & UE5 READY", (108, 92, 231))
    ]
    cur_x = W - 40
    for text, bg_col in reversed(pills):
        tw = len(text) * 9 + 20
        cur_x -= tw
        draw.rounded_rectangle((cur_x, 35, cur_x + tw - 10, 68), radius=6, fill=bg_col)
        draw.text((cur_x + 10, 43), text, fill=(255, 255, 255), font=font_pill)
        cur_x -= 10
        
    draw.line((40, 95, W - 40, 95), fill=(45, 52, 65), width=2)
    
    # 1. Panorama Superior Natively Rendered (2480x760)
    pan_path = os.path.join(RENDERS_DIR, "Showcase_Catalogo_Modular_Panorama.png")
    if os.path.exists(pan_path):
        pan_img = Image.open(pan_path).convert("RGBA")
        pan_w = W - 80
        pan_h = 760
        pan_resized = pan_img.resize((pan_w, pan_h), Image.Resampling.LANCZOS)
        canvas.paste(pan_resized, (40, 110))
        draw.rectangle((40, 110, 40 + pan_w, 110 + pan_h), outline=(45, 52, 65), width=2)
        
    # 2. Fila Inferior con los 4 Close-Ups de Kits Modulares
    kits_data = [
        ("01. KIT CARGUERO QUÍMICO (TIER 1)", "Showcase_Modular_Kit_Industrial.png", (245, 166, 35),
         "• Contenedor Espacial TEU con Costillas\n• Cuba de Ácido Radiactivo Efervescente\n• Brazo Grúa Pescante Articulado con Pinza\n• Pasarela con Rejilla y Barandilla\n• Viga I Industrial con Placa de Pernos\n• Batería de Barriles Tóxicos y Derrame"),
        ("02. KIT CRUCERO ART DÉCO (TIER 2)", "Showcase_Modular_Kit_ArtDeco.png", (212, 175, 55),
         "• Ventanal Arqueado al Cosmos (Saturno)\n• Sillón Club Chesterfield Terciopelo Burdeos\n• Sofá Doble Capitoné Burdeos de Lujo\n• Mesa de Centro Mármol Carrara y Oro\n• Espejo Monumental Rayos Solsticio\n• Lámpara Ziggurat, Boiserie y Alfombra"),
        ("03. KIT REFINERÍA PLASMA (TIER 3)", "Showcase_Modular_Kit_Plasma.png", (0, 240, 255),
         "• Reactor Toroidal con Rayos de Plasma\n• Vórtice Central Singularidad Blanca\n• Batería Colectora y Tuberías Bridadas\n• Consola Terminal con Pantalla CRT\n• Cartelera de Peligro Alta Energía\n• Pasarela Curva y Subdron Minero"),
        ("04. KIT MECÁNICA CHATARRERA", "Showcase_Modular_Kit_Enemigos_Mecanica.png", (255, 75, 40),
         "• Dron Auditor Esférico Blindado (Ojo Rojo)\n• Lente Óptica Carmesí y CRT de Radar\n• Sierra Circular 24 Dientes Afilados\n• Chimeneas de Escape con Fuego Cómic\n• Pistón Hidráulico Articulado Cromado\n• Maza de Impacto con Púas Cónicas\n• Racor Triple de Manómetros de Latón")
    ]
    
    card_w = (W - 80 - 45) // 4
    card_h = 510
    card_y = 890
    
    for i, (title, img_name, border_col, desc) in enumerate(kits_data):
        cx = 40 + i * (card_w + 15)
        
        draw.rectangle((cx, card_y, cx + card_w, card_y + card_h), fill=(20, 24, 30), outline=border_col, width=2)
        
        img_path = os.path.join(RENDERS_DIR, img_name)
        if os.path.exists(img_path):
            card_img = Image.open(img_path).convert("RGBA")
            c_render_h = 300
            c_render_w = card_w - 4
            card_resized = card_img.resize((c_render_w, c_render_h), Image.Resampling.LANCZOS)
            canvas.paste(card_resized, (cx + 2, card_y + 2))
            
        draw.rectangle((cx, card_y + 302, cx + card_w, card_y + 338), fill=(28, 33, 42))
        draw.text((cx + 10, card_y + 310), title, fill=border_col, font=font_card_title)
        
        draw.text((cx + 12, card_y + 348), desc, fill=(210, 220, 235), font=font_card_desc, spacing=3)

    master_path = os.path.join(RENDERS_DIR, "Showcase_Catalogo_Activos_Modulares_Master.png")
    canvas.save(master_path, "PNG")
    
    shutil.copy2(master_path, os.path.join(ARTIFACT_DIR, "Showcase_Catalogo_Activos_Modulares_Master.png"))
    for _, fname, _, _ in kits_data:
        shutil.copy2(os.path.join(RENDERS_DIR, fname), os.path.join(ARTIFACT_DIR, fname))
    shutil.copy2(pan_path, os.path.join(ARTIFACT_DIR, "Showcase_Catalogo_Modular_Panorama.png"))
    
    print(f"\n[MASTER OK] Lámina Maestra Oficial generada con éxito: {master_path}")
    print("=" * 80)

if __name__ == "__main__":
    main()

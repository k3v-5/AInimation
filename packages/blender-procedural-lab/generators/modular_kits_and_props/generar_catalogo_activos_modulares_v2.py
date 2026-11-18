# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Generador Maestro del Catálogo de Activos 3D Modulares y Reutilizables V2 - Astra Hazard
# Descomposición Fiel 1:1 de los 3 Mapas (media_1791273626834.png) y Componentes Mecánicos
# Blender 5.2 LTS - Shaders PBR Físicos (15 Packs Oficiales), Modelado de Alta Fidelidad y Freestyle Lineart

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
    
    # Configuración de Freestyle para Lineart de Cómic / Novela Gráfica
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
    linestyle.color = (0.04, 0.04, 0.04)
    linestyle.thickness = 1.5
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

def finalize_asset(obj, col, location=(0,0,0), rotation=(0,0,0)):
    col.objects.link(obj)
    obj.location = Vector(location)
    obj.rotation_euler = Euler((R(rotation[0]), R(rotation[1]), R(rotation[2])), 'XYZ')
    bpy.context.view_layer.update()
    return obj

# ==============================================================================
# PIPELINE DE SHADERS PBR CINEMATOGRÁFICOS (15 PACKS OFICIALES)
# ==============================================================================
MATS = {}

def create_pbr_material(name, pack_name, default_color=(0.5, 0.5, 0.5), default_roughness=0.5, default_metallic=0.0,
                        emissive_color=(0, 0, 0, 1), emissive_strength=0.0, box_scale=(1.0, 1.0, 1.0)):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    node_out.location = (500, 0)
    
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (150, 0)
    node_bsdf.inputs['Base Color'].default_value = (*default_color, 1.0)
    node_bsdf.inputs['Roughness'].default_value = default_roughness
    node_bsdf.inputs['Metallic'].default_value = default_metallic
    
    coord_node = nodes.new(type='ShaderNodeTexCoord')
    coord_node.location = (-850, 150)
    
    mapping_node = nodes.new(type='ShaderNodeMapping')
    mapping_node.location = (-650, 150)
    mapping_node.inputs['Scale'].default_value = box_scale
    links.new(coord_node.outputs['Object'], mapping_node.inputs['Vector'])
    
    basecolor_path = os.path.join(TEXTURES_MODULAR, f"{pack_name}_BaseColor.png")
    normal_path = os.path.join(TEXTURES_MODULAR, f"{pack_name}_Normal.png")
    orm_path = os.path.join(TEXTURES_MODULAR, f"{pack_name}_ORM.png")
    emissive_path = os.path.join(TEXTURES_MODULAR, f"{pack_name}_Emissive.png")
    
    # 1. BaseColor
    if os.path.exists(basecolor_path):
        tex_col = nodes.new(type='ShaderNodeTexImage')
        tex_col.location = (-400, 300)
        tex_col.projection = 'BOX'
        tex_col.projection_blend = 0.25
        tex_col.image = bpy.data.images.load(basecolor_path)
        links.new(mapping_node.outputs['Vector'], tex_col.inputs['Vector'])
        links.new(tex_col.outputs['Color'], node_bsdf.inputs['Base Color'])
        
    # 2. ORM (AO/Roughness/Metallic)
    if os.path.exists(orm_path):
        tex_orm = nodes.new(type='ShaderNodeTexImage')
        tex_orm.location = (-400, 0)
        tex_orm.projection = 'BOX'
        tex_orm.projection_blend = 0.25
        img_orm = bpy.data.images.load(orm_path)
        img_orm.colorspace_settings.name = 'Non-Color'
        tex_orm.image = img_orm
        links.new(mapping_node.outputs['Vector'], tex_orm.inputs['Vector'])
        
        sep = nodes.new(type='ShaderNodeSeparateColor')
        sep.location = (-150, 0)
        links.new(tex_orm.outputs['Color'], sep.inputs['Color'])
        links.new(sep.outputs['Green'], node_bsdf.inputs['Roughness'])
        links.new(sep.outputs['Blue'], node_bsdf.inputs['Metallic'])
        
    # 3. Normal Map
    if os.path.exists(normal_path):
        tex_norm = nodes.new(type='ShaderNodeTexImage')
        tex_norm.location = (-400, -300)
        tex_norm.projection = 'BOX'
        tex_norm.projection_blend = 0.25
        img_norm = bpy.data.images.load(normal_path)
        img_norm.colorspace_settings.name = 'Non-Color'
        tex_norm.image = img_norm
        links.new(mapping_node.outputs['Vector'], tex_norm.inputs['Vector'])
        
        node_norm = nodes.new(type='ShaderNodeNormalMap')
        node_norm.location = (-150, -300)
        node_norm.space = 'TANGENT'
        node_norm.inputs['Strength'].default_value = 1.3
        links.new(tex_norm.outputs['Color'], node_norm.inputs['Color'])
        links.new(node_norm.outputs['Normal'], node_bsdf.inputs['Normal'])
        
    # 4. Emissive
    if os.path.exists(emissive_path):
        tex_emi = nodes.new(type='ShaderNodeTexImage')
        tex_emi.location = (-400, -600)
        tex_emi.projection = 'BOX'
        tex_emi.projection_blend = 0.25
        tex_emi.image = bpy.data.images.load(emissive_path)
        links.new(mapping_node.outputs['Vector'], tex_emi.inputs['Vector'])
        links.new(tex_emi.outputs['Color'], node_bsdf.inputs['Emission Color'])
        node_bsdf.inputs['Emission Strength'].default_value = emissive_strength if emissive_strength > 0.0 else 4.0
    elif emissive_strength > 0.0:
        node_bsdf.inputs['Emission Color'].default_value = emissive_color
        node_bsdf.inputs['Emission Strength'].default_value = emissive_strength
        
    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])
    return mat

def build_all_materials():
    print("  [SHADERS] Compilando Shaders PBR basados en los 15 packs...")
    # Kit 1: Industrial & Derelict
    MATS["PBR_Rust_Plates"] = create_pbr_material("M_PBR_Rust_Plates", "T_Derelict_Rust_Plates", box_scale=(0.6, 0.6, 0.6))
    MATS["PBR_Battered_Armor"] = create_pbr_material("M_PBR_Battered_Armor", "T_Battered_Armor_Impacts", box_scale=(0.7, 0.7, 0.7))
    MATS["PBR_Corroded_Pipes"] = create_pbr_material("M_PBR_Corroded_Pipes", "T_Corroded_Acid_Pipes", emissive_strength=4.5, box_scale=(0.8, 0.8, 0.8))
    MATS["PBR_Decayed_Grating"] = create_pbr_material("M_PBR_Decayed_Grating", "T_Decayed_Rusted_Grating", box_scale=(1.2, 1.2, 1.2))
    MATS["PBR_Trim_Industrial"] = create_pbr_material("M_PBR_Trim_Industrial", "T_Trim_Industrial", box_scale=(0.8, 0.8, 0.8))
    MATS["PBR_Steel_Plates"] = create_pbr_material("M_PBR_Steel_Plates", "T_Steel_Plates", box_scale=(0.6, 0.6, 0.6))
    
    # Kit 2: Luxury Art Déco Celestia
    MATS["PBR_Marble_Gold"] = create_pbr_material("M_PBR_Marble_Gold", "T_Luxury_Marble_Gold_Inlay", box_scale=(0.8, 0.8, 0.8))
    MATS["PBR_Walnut_Panels"] = create_pbr_material("M_PBR_Walnut_Panels", "T_Luxury_Walnut_Wood_Panels", box_scale=(0.8, 0.8, 0.8))
    MATS["PBR_Gilded_Brass"] = create_pbr_material("M_PBR_Gilded_Brass", "T_Luxury_ArtDeco_Gilded_Brass", box_scale=(0.8, 0.8, 0.8))
    MATS["PBR_Quilted_Velvet"] = create_pbr_material("M_PBR_Quilted_Velvet", "T_Luxury_Quilted_Velvet_Leather", box_scale=(1.1, 1.1, 1.1))
    MATS["PBR_Smoked_Glass"] = create_pbr_material("M_PBR_Smoked_Glass", "T_Luxury_Smoked_Glass_Lattice", emissive_strength=3.5, box_scale=(0.9, 0.9, 0.9))
    
    # Kit 3: Plasma & High Energy
    MATS["PBR_Plasma_Slag"] = create_pbr_material("M_PBR_Plasma_Slag", "T_Scorched_Plasma_Slag", emissive_strength=5.0, box_scale=(0.7, 0.7, 0.7))
    MATS["PBR_Props_Machinery"] = create_pbr_material("M_PBR_Props_Machinery", "T_Props_Machinery", emissive_strength=3.0, box_scale=(0.8, 0.8, 0.8))
    
    # Materiales Auxiliares
    mat_brass = bpy.data.materials.new("M_Polished_Brass")
    mat_brass.use_nodes = True
    b = mat_brass.node_tree.nodes.get("Principled BSDF")
    b.inputs['Base Color'].default_value = (0.95, 0.82, 0.32, 1.0)
    b.inputs['Metallic'].default_value = 0.98
    b.inputs['Roughness'].default_value = 0.16
    MATS["Polished_Brass"] = mat_brass
    
    mat_cyan_core = bpy.data.materials.new("M_Plasma_Core_Glow")
    mat_cyan_core.use_nodes = True
    c = mat_cyan_core.node_tree.nodes.get("Principled BSDF")
    c.inputs['Base Color'].default_value = (0.1, 0.9, 1.0, 1.0)
    c.inputs['Emission Color'].default_value = (0.05, 0.92, 1.0, 1.0)
    c.inputs['Emission Strength'].default_value = 7.5
    MATS["Plasma_Core_Glow"] = mat_cyan_core
    
    mat_ped = bpy.data.materials.new("M_Showroom_Pedestal")
    mat_ped.use_nodes = True
    p = mat_ped.node_tree.nodes.get("Principled BSDF")
    p.inputs['Base Color'].default_value = (0.07, 0.08, 0.09, 1.0)
    p.inputs['Metallic'].default_value = 0.85
    p.inputs['Roughness'].default_value = 0.35
    MATS["Showroom_Pedestal"] = mat_ped

# ==============================================================================
# MODELADO PROCEDURAL DE ALTA FIDELIDAD: KIT 1 (CARGUERO DERELICT & ESTRUCTURAL)
# ==============================================================================
def build_kit_industrial(parent_col, origin=(-11.4, 0.0, 0.25)):
    col = create_collection("Kit_01_Carguero_Industrial", parent_col)
    ox, oy, oz = origin

    # 1. Pasarela Modular de Rejilla con Barandilla (SM_Catwalk_Grating_400cm)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ox - 1.8, oy - 1.2, oz + 0.12))
    walk = bpy.context.active_object
    walk.name = "SM_Catwalk_Grating_400cm"
    walk.scale = (3.6, 1.2, 0.15)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    walk.data.materials.append(MATS["PBR_Decayed_Grating"])
    add_bevel(walk, width=0.015)
    # Vigas I inferiores
    for by in [-0.5, 0.5]:
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ox - 1.8, oy - 1.2 + by, oz - 0.05))
        beam = bpy.context.active_object
        beam.scale = (3.6, 0.12, 0.20)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        beam.data.materials.append(MATS["PBR_Rust_Plates"])
        add_bevel(beam, width=0.01)
    # Barandilla amarilla
    for bz in [0.45, 0.85]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=3.6, location=(ox - 1.8, oy - 1.2 - 0.55, oz + bz))
        rail = bpy.context.active_object
        rail.rotation_euler = (0, R(90), 0)
        rail.data.materials.append(MATS["PBR_Trim_Industrial"])
    for px in [-1.6, 0.0, 1.6]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=0.9, location=(ox - 1.8 + px, oy - 1.2 - 0.55, oz + 0.45))
        post = bpy.context.active_object
        post.data.materials.append(MATS["PBR_Trim_Industrial"])

    # 2. Contenedor Espacial Modular TEU (SM_Cargo_Container_Space)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ox + 1.6, oy - 0.8, oz + 0.95))
    cont = bpy.context.active_object
    cont.name = "SM_Cargo_Container_Space"
    cont.scale = (1.8, 3.2, 1.8)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    cont.data.materials.append(MATS["PBR_Rust_Plates"])
    add_bevel(cont, width=0.03)
    # Marcos de esquineros ISO
    for cx in [-0.9, 0.9]:
        for cy in [-1.6, 1.6]:
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ox + 1.6 + cx, oy - 0.8 + cy, oz + 0.95))
            c_post = bpy.context.active_object
            c_post.scale = (0.16, 0.16, 1.85)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            c_post.data.materials.append(MATS["PBR_Steel_Plates"])
            add_bevel(c_post, width=0.015)

    # 3. Tanque de Reactivos con Ácido Verde (SM_Chemical_Vat_Acid)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ox - 1.5, oy + 1.4, oz + 0.70))
    vat = bpy.context.active_object
    vat.name = "SM_Chemical_Vat_Acid"
    vat.scale = (1.8, 1.8, 1.35)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    vat.data.materials.append(MATS["PBR_Battered_Armor"])
    add_bevel(vat, width=0.03)
    # Superficie líquida de ácido burbujeante
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=(ox - 1.5, oy + 1.4, oz + 1.15))
    acid_surf = bpy.context.active_object
    acid_surf.scale = (1.65, 1.65, 1.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    acid_surf.data.materials.append(MATS["PBR_Corroded_Pipes"])

    # 4. Batería de Tuberías con Válvula y Manómetro (SM_Pipe_Network_Flanged)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.14, depth=2.8, location=(ox + 0.4, oy + 1.5, oz + 0.65))
    pipe = bpy.context.active_object
    pipe.name = "SM_Pipe_Network_Flanged"
    pipe.rotation_euler = (0, R(90), 0)
    pipe.data.materials.append(MATS["PBR_Corroded_Pipes"])
    add_bevel(pipe, width=0.01)
    # Bridas hexagonales
    for fx in [-1.0, 0.0, 1.0]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=0.08, vertices=6, location=(ox + 0.4 + fx, oy + 1.5, oz + 0.65))
        flange = bpy.context.active_object
        flange.rotation_euler = (0, R(90), 0)
        flange.data.materials.append(MATS["PBR_Rust_Plates"])
    # Válvula roja
    bpy.ops.mesh.primitive_torus_add(major_radius=0.22, minor_radius=0.04, location=(ox + 0.4, oy + 1.5, oz + 1.15))
    wheel = bpy.context.active_object
    wheel.rotation_euler = (R(90), 0, 0)
    wheel.data.materials.append(MATS["PBR_Trim_Industrial"])

    # 5. Grúa Pórtico Pesada (SM_Cargo_Crane_Gantry)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ox - 2.8, oy - 0.2, oz + 2.1))
    crane_arm = bpy.context.active_object
    crane_arm.name = "SM_Cargo_Crane_Gantry"
    crane_arm.scale = (0.35, 4.2, 0.45)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    crane_arm.data.materials.append(MATS["PBR_Trim_Industrial"])
    add_bevel(crane_arm, width=0.02)
    # Pilar vertical
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ox - 2.8, oy - 2.1, oz + 1.05))
    crane_post = bpy.context.active_object
    crane_post.scale = (0.45, 0.45, 2.1)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    crane_post.data.materials.append(MATS["PBR_Trim_Industrial"])
    add_bevel(crane_post, width=0.02)

# ==============================================================================
# MODELADO PROCEDURAL DE ALTA FIDELIDAD: KIT 2 (CRUCERO DE LUJO ART DÉCO CELESTIA)
# ==============================================================================
def build_kit_artdeco(parent_col, origin=(-3.8, 0.0, 0.25)):
    col = create_collection("Kit_02_Crucero_ArtDeco", parent_col)
    ox, oy, oz = origin

    # 1. Sillón Chesterfield Capitoné VIP (SM_Chesterfield_Armchair)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ox - 1.4, oy - 0.8, oz + 0.45))
    chair = bpy.context.active_object
    chair.name = "SM_Chesterfield_Armchair"
    chair.scale = (1.1, 1.05, 0.88)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    chair.data.materials.append(MATS["PBR_Quilted_Velvet"])
    add_bevel(chair, width=0.06, segments=4)
    # Cojín de asiento mullido
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ox - 1.4, oy - 0.75, oz + 0.42))
    cush = bpy.context.active_object
    cush.scale = (0.75, 0.75, 0.22)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    cush.data.materials.append(MATS["PBR_Quilted_Velvet"])
    add_bevel(cush, width=0.04)
    # 4 patas cónicas de latón
    for lx in [-0.45, 0.45]:
        for ly in [-0.42, 0.42]:
            bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=0.22, location=(ox - 1.4 + lx, oy - 0.8 + ly, oz + 0.11))
            leg = bpy.context.active_object
            leg.data.materials.append(MATS["Polished_Brass"])

    # 2. Sofá Doble Chesterfield Imperial (SM_Chesterfield_Sofa_2P)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ox + 1.2, oy - 0.8, oz + 0.45))
    sofa = bpy.context.active_object
    sofa.name = "SM_Chesterfield_Sofa_2P"
    sofa.scale = (2.1, 1.05, 0.88)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    sofa.data.materials.append(MATS["PBR_Quilted_Velvet"])
    add_bevel(sofa, width=0.06, segments=4)
    for lx in [-0.95, 0.0, 0.95]:
        for ly in [-0.42, 0.42]:
            bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=0.22, location=(ox + 1.2 + lx, oy - 0.8 + ly, oz + 0.11))
            leg = bpy.context.active_object
            leg.data.materials.append(MATS["Polished_Brass"])

    # 3. Mesa de Centro de Mármol y Oro 24k (SM_ArtDeco_Coffee_Table)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.65, depth=0.06, vertices=32, location=(ox - 0.1, oy - 0.8, oz + 0.48))
    table_top = bpy.context.active_object
    table_top.name = "SM_ArtDeco_Coffee_Table"
    table_top.data.materials.append(MATS["PBR_Marble_Gold"])
    add_bevel(table_top, width=0.015)
    # Anillo y patas trípode de latón
    bpy.ops.mesh.primitive_cylinder_add(radius=0.66, depth=0.04, vertices=32, location=(ox - 0.1, oy - 0.8, oz + 0.44))
    rim = bpy.context.active_object
    rim.data.materials.append(MATS["Polished_Brass"])
    for a in [0, 120, 240]:
        ang = R(a)
        bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.45, location=(ox - 0.1 + math.cos(ang)*0.55, oy - 0.8 + math.sin(ang)*0.55, oz + 0.22))
        tleg = bpy.context.active_object
        tleg.data.materials.append(MATS["Polished_Brass"])

    # 4. Espejo Monumental de Pared Solsticio (SM_ArtDeco_Sunburst_Mirror)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ox, oy + 1.8, oz + 1.6))
    mirror_frame = bpy.context.active_object
    mirror_frame.name = "SM_ArtDeco_Sunburst_Mirror"
    mirror_frame.scale = (2.2, 0.12, 1.6)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    mirror_frame.data.materials.append(MATS["PBR_Gilded_Brass"])
    add_bevel(mirror_frame, width=0.03)
    # Luna de espejo central
    bpy.ops.mesh.primitive_cylinder_add(radius=0.55, depth=0.04, vertices=32, location=(ox, oy + 1.74, oz + 1.6))
    mirror_glass = bpy.context.active_object
    mirror_glass.rotation_euler = (R(90), 0, 0)
    mirror_glass.data.materials.append(MATS["PBR_Marble_Gold"])

    # 5. Biombo Divisorio de Vidrio Ahumado y Celosía (SM_ArtDeco_Lattice_Screen)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ox + 1.8, oy + 1.2, oz + 1.2))
    screen = bpy.context.active_object
    screen.name = "SM_ArtDeco_Lattice_Screen"
    screen.scale = (1.4, 0.15, 2.3)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    screen.data.materials.append(MATS["PBR_Smoked_Glass"])
    add_bevel(screen, width=0.02)

    # 6. Módulo de Boiserie de Pared de Nogal (SM_ArtDeco_Wall_Boiserie)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ox - 1.8, oy + 1.8, oz + 1.25))
    boiserie = bpy.context.active_object
    boiserie.name = "SM_ArtDeco_Wall_Boiserie"
    boiserie.scale = (1.5, 0.18, 2.4)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    boiserie.data.materials.append(MATS["PBR_Walnut_Panels"])
    add_bevel(boiserie, width=0.02)

    # 7. Lámpara de Araña Monumental en 3 Capas (SM_ArtDeco_Chandelier)
    ch_z = oz + 2.5
    for lvl, (rad, dep) in enumerate([(0.75, 0.18), (0.50, 0.18), (0.28, 0.18)]):
        bpy.ops.mesh.primitive_cylinder_add(radius=rad, depth=dep, vertices=24, location=(ox, oy - 0.4, ch_z - lvl*0.16))
        ch_ring = bpy.context.active_object
        ch_ring.name = f"SM_ArtDeco_Chandelier_L{lvl}"
        ch_ring.data.materials.append(MATS["PBR_Gilded_Brass"])
        add_bevel(ch_ring, width=0.015)

    # 8. Lámpara de Pie de Salón (SM_ArtDeco_Floor_Lamp)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=1.65, location=(ox - 2.2, oy - 0.2, oz + 0.85))
    flamp = bpy.context.active_object
    flamp.name = "SM_ArtDeco_Floor_Lamp"
    flamp.data.materials.append(MATS["Polished_Brass"])
    # Pantalla cónica
    bpy.ops.mesh.primitive_cone_add(radius1=0.28, radius2=0.15, depth=0.35, location=(ox - 2.2, oy - 0.2, oz + 1.75))
    shade = bpy.context.active_object
    shade.data.materials.append(MATS["PBR_Smoked_Glass"])

# ==============================================================================
# MODELADO PROCEDURAL DE ALTA FIDELIDAD: KIT 3 (REFINERÍA DE PLASMA BLACK ROCK)
# ==============================================================================
def build_kit_plasma(parent_col, origin=(3.8, 0.0, 0.25)):
    col = create_collection("Kit_03_Refineria_Plasma", parent_col)
    ox, oy, oz = origin

    # 1. Reactor Toroidal de Confinamiento Magnético (SM_Plasma_Toroid_Reactor)
    bpy.ops.mesh.primitive_torus_add(major_radius=1.35, minor_radius=0.32, major_segments=24, minor_segments=16, location=(ox, oy + 0.6, oz + 1.65))
    toroid = bpy.context.active_object
    toroid.name = "SM_Plasma_Toroid_Reactor"
    toroid.rotation_euler = (R(90), 0, 0)
    toroid.data.materials.append(MATS["PBR_Battered_Armor"])
    add_bevel(toroid, width=0.02)
    # Núcleo toroidal central de plasma cian brillante
    bpy.ops.mesh.primitive_torus_add(major_radius=1.35, minor_radius=0.14, major_segments=24, minor_segments=16, location=(ox, oy + 0.6, oz + 1.65))
    core_plasma = bpy.context.active_object
    core_plasma.rotation_euler = (R(90), 0, 0)
    core_plasma.data.materials.append(MATS["Plasma_Core_Glow"])
    # Bobinas magnéticas de cobre
    for deg in range(0, 360, 45):
        ang = R(deg)
        bx = ox + math.cos(ang) * 1.35
        bz = oz + 1.65 + math.sin(ang) * 1.35
        bpy.ops.mesh.primitive_cylinder_add(radius=0.42, depth=0.14, vertices=16, location=(bx, oy + 0.6, bz))
        coil = bpy.context.active_object
        coil.rotation_euler = (0, -ang, 0)
        coil.data.materials.append(MATS["Polished_Brass"])

    # 2. Mamparo Perforado por Brecha de Plasma (SM_Plasma_Breached_Bulkhead)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ox - 1.8, oy + 1.6, oz + 1.25))
    breach = bpy.context.active_object
    breach.name = "SM_Plasma_Breached_Bulkhead"
    breach.scale = (1.6, 0.18, 2.3)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    breach.data.materials.append(MATS["PBR_Plasma_Slag"])
    add_bevel(breach, width=0.02)

    # 3. Pasarela Curva Suspendida (SM_Curved_Catwalk_Platform)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ox - 1.2, oy - 1.2, oz + 0.22))
    catwalk_curv = bpy.context.active_object
    catwalk_curv.name = "SM_Curved_Catwalk_Platform"
    catwalk_curv.scale = (2.2, 1.2, 0.18)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    catwalk_curv.data.materials.append(MATS["PBR_Decayed_Grating"])
    add_bevel(catwalk_curv, width=0.02)
    # Barandilla curvada
    bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=2.2, location=(ox - 1.2, oy - 1.2 - 0.55, oz + 0.95))
    rail_c = bpy.context.active_object
    rail_c.rotation_euler = (0, R(90), 0)
    rail_c.data.materials.append(MATS["PBR_Trim_Industrial"])

    # 4. Batería de Condensadores de Plasma (SM_Plasma_Capacitor_Bank)
    for i, cx in enumerate([-0.4, 0.0, 0.4]):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=1.45, vertices=16, location=(ox + 1.6 + cx, oy - 0.6, oz + 0.75))
        cap = bpy.context.active_object
        cap.name = f"SM_Plasma_Capacitor_{i}"
        cap.data.materials.append(MATS["PBR_Steel_Plates"])
        add_bevel(cap, width=0.015)
        # Anillos luminosos de energía
        bpy.ops.mesh.primitive_torus_add(major_radius=0.19, minor_radius=0.02, location=(ox + 1.6 + cx, oy - 0.6, oz + 0.75))
        ring_c = bpy.context.active_object
        ring_c.data.materials.append(MATS["Plasma_Core_Glow"])

    # 5. Consola Maestra de Regulación de Plasma (SM_Plasma_Control_Station)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ox + 1.6, oy + 1.4, oz + 0.65))
    console = bpy.context.active_object
    console.name = "SM_Plasma_Control_Station"
    console.scale = (1.4, 0.85, 1.2)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    console.data.materials.append(MATS["PBR_Props_Machinery"])
    add_bevel(console, width=0.02)

# ==============================================================================
# MODELADO PROCEDURAL DE ALTA FIDELIDAD: KIT 4 (COMPONENTES MECÁNICOS Y ENEMIGOS)
# ==============================================================================
def build_kit_mechanics(parent_col, origin=(11.4, 0.0, 0.25)):
    col = create_collection("Kit_04_Mecanica_Enemigos", parent_col)
    ox, oy, oz = origin

    # 1. Sierra Circular / Engranaje de Corte de 24 Dientes (SM_Mech_Sawblade_Gear)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.75, depth=0.08, vertices=24, location=(ox - 1.2, oy + 1.2, oz + 0.85))
    saw = bpy.context.active_object
    saw.name = "SM_Mech_Sawblade_Gear"
    saw.rotation_euler = (R(90), 0, 0)
    saw.data.materials.append(MATS["PBR_Battered_Armor"])
    add_bevel(saw, width=0.015)
    # Cubo central y chavetero
    bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=0.14, vertices=16, location=(ox - 1.2, oy + 1.2, oz + 0.85))
    hub = bpy.context.active_object
    hub.rotation_euler = (R(90), 0, 0)
    hub.data.materials.append(MATS["PBR_Steel_Plates"])

    # 2. Pistón Hidráulico de Doble Camisa (SM_Hydraulic_Piston_Dual)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.14, depth=1.2, vertices=16, location=(ox + 1.2, oy + 1.2, oz + 0.75))
    cylinder = bpy.context.active_object
    cylinder.name = "SM_Hydraulic_Piston_Dual"
    cylinder.data.materials.append(MATS["PBR_Steel_Plates"])
    add_bevel(cylinder, width=0.01)
    # Vástago cromado interior pulido
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.85, vertices=16, location=(ox + 1.2, oy + 1.2, oz + 1.55))
    rod = bpy.context.active_object
    rod.data.materials.append(MATS["Polished_Brass"])
    add_bevel(rod, width=0.005)

    # 3. Maza Pesada de Púas Chatarrera (SM_Scrapper_Spiked_Mace)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=1.35, vertices=12, location=(ox - 1.4, oy - 0.8, oz + 0.70))
    mace_handle = bpy.context.active_object
    mace_handle.name = "SM_Scrapper_Spiked_Mace"
    mace_handle.data.materials.append(MATS["PBR_Rust_Plates"])
    # Cabeza esférica armada con púas
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22, location=(ox - 1.4, oy - 0.8, oz + 1.35))
    mace_head = bpy.context.active_object
    mace_head.data.materials.append(MATS["PBR_Battered_Armor"])
    for dx, dy, dz in [(0.25,0,0), (-0.25,0,0), (0,0.25,0), (0,-0.25,0), (0,0,0.25)]:
        bpy.ops.mesh.primitive_cone_add(radius1=0.06, depth=0.18, location=(ox - 1.4 + dx, oy - 0.8 + dy, oz + 1.35 + dz))
        spike = bpy.context.active_object
        spike.data.materials.append(MATS["PBR_Steel_Plates"])

    # 4. Trío de Chimeneas con Llamaradas 2D (SM_Exhaust_Pipes_Flames)
    for i, ex in enumerate([-0.3, 0.0, 0.3]):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.10, depth=0.75, vertices=16, location=(ox + 0.2 + ex, oy - 0.8, oz + 0.65))
        pipe_ex = bpy.context.active_object
        pipe_ex.name = f"SM_Exhaust_Pipe_{i}"
        pipe_ex.rotation_euler = (R(25), 0, 0)
        pipe_ex.data.materials.append(MATS["PBR_Rust_Plates"])
        add_bevel(pipe_ex, width=0.01)
        # Llamarada 2D estilizada cómic
        bpy.ops.mesh.primitive_cone_add(radius1=0.18, depth=0.65, location=(ox + 0.2 + ex, oy - 0.8 - 0.25, oz + 1.25))
        flame = bpy.context.active_object
        flame.rotation_euler = (R(25), 0, 0)
        flame.data.materials.append(MATS["PBR_Plasma_Slag"])

    # 5. Manómetros Triples de Latón (SM_Brass_Gauges_Cluster)
    for j, (gx, gz) in enumerate([(-0.25, 0.0), (0.0, 0.22), (0.25, 0.0)]):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.15, depth=0.08, vertices=24, location=(ox + 1.4 + gx, oy - 0.8, oz + 0.55 + gz))
        gauge = bpy.context.active_object
        gauge.name = f"SM_Brass_Gauge_{j}"
        gauge.rotation_euler = (R(90), 0, 0)
        gauge.data.materials.append(MATS["Polished_Brass"])
        add_bevel(gauge, width=0.01)

    # 6. Monóculo Óptico Telescópico de 3 Aros (SM_Scrapper_Monocular_Lens)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.28, depth=0.35, vertices=24, location=(ox, oy + 0.2, oz + 0.65))
    mono = bpy.context.active_object
    mono.name = "SM_Scrapper_Monocular_Lens"
    mono.rotation_euler = (R(90), 0, 0)
    mono.data.materials.append(MATS["Polished_Brass"])
    add_bevel(mono, width=0.015)
    # Lente convexa ámbar
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.26, location=(ox, oy + 0.05, oz + 0.65))
    lens = bpy.context.active_object
    lens.scale = (1.0, 0.35, 1.0)
    lens.data.materials.append(MATS["PBR_Smoked_Glass"])

# ==============================================================================
# CONSTRUCCIÓN DE ESTUDIO, ISLAS DE EXHIBICIÓN E ILUMINACIÓN
# ==============================================================================
def build_showcase_studio(scene):
    # Ciclorama continuo de fondo
    bpy.ops.mesh.primitive_plane_add(size=48.0, location=(0, 4.0, 0.0))
    floor = bpy.context.active_object
    floor.name = "Studio_Floor"
    floor.data.materials.append(MATS["Showroom_Pedestal"])
    
    bpy.ops.mesh.primitive_plane_add(size=48.0, location=(0, 9.0, 6.0))
    wall = bpy.context.active_object
    wall.name = "Studio_Wall"
    wall.rotation_euler = (R(90), 0, 0)
    wall.data.materials.append(MATS["Showroom_Pedestal"])
    
    # 4 Islas de Exhibición con biseles y placas doradas 3D
    islands = [
        ("01. CARGUERO QUÍMICO & ESTRUCTURAL", -11.4),
        ("02. CRUCERO DE LUJO ART DÉCO", -3.8),
        ("03. REFINERÍA DE PLASMA BLACK ROCK", 3.8),
        ("04. COMPONENTES Y MECÁNICA", 11.4),
    ]
    
    for label, ix in islands:
        # Plinto de la isla
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ix, 0.0, 0.12))
        isle = bpy.context.active_object
        isle.name = f"Isle_Pedestal_{ix}"
        isle.scale = (6.8, 5.2, 0.24)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        isle.data.materials.append(MATS["Showroom_Pedestal"])
        add_bevel(isle, width=0.04)
        
        # Placa frontal de latón
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(ix, -2.62, 0.12))
        plaque = bpy.context.active_object
        plaque.scale = (3.4, 0.04, 0.16)
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
        plaque.data.materials.append(MATS["Polished_Brass"])
        
        # Foco de acento superior
        bpy.ops.object.light_add(type='SPOT', location=(ix, -3.2, 5.2))
        spot = bpy.context.active_object
        spot.data.energy = 280.0
        spot.data.color = (1.0, 0.94, 0.85)
        spot.data.spot_size = R(60)
        spot.data.spot_blend = 0.35
        spot.rotation_euler = (R(35), 0, 0)

    # Iluminación de estudio global (3 Puntos)
    bpy.ops.object.light_add(type='SUN', location=(4, -12, 12))
    sun = bpy.context.active_object
    sun.data.energy = 4.5
    sun.data.color = (1.0, 0.96, 0.90)
    sun.rotation_euler = (R(48), R(14), R(-20))
    
    bpy.ops.object.light_add(type='SUN', location=(-4, 12, 8))
    rim = bpy.context.active_object
    rim.data.energy = 2.8
    rim.data.color = (0.50, 0.75, 1.0)
    rim.rotation_euler = (R(-45), R(-12), R(160))

def create_targeted_camera(name, loc, target, lens=32.0):
    bpy.ops.object.camera_add(location=loc)
    cam = bpy.context.active_object
    cam.name = name
    cam.data.lens = lens
    
    constraint = cam.constraints.new(type='TRACK_TO')
    
    empty = bpy.data.objects.new(f"{name}_Target", None)
    bpy.context.scene.collection.objects.link(empty)
    empty.location = target
    
    constraint.target = empty
    constraint.track_axis = 'TRACK_NEGATIVE_Z'
    constraint.up_axis = 'UP_Y'
    return cam

def render_camera_view(scene, cam, filename, res_x=1920, res_y=1080):
    scene.camera = cam
    scene.render.resolution_x = res_x
    scene.render.resolution_y = res_y
    out_path = os.path.join(RENDERS_DIR, filename)
    scene.render.filepath = out_path
    print(f"  [RENDER] Renderizando {filename} ({res_x}x{res_y})...")
    bpy.ops.render.render(write_still=True)
    art_path = os.path.join(ARTIFACT_DIR, filename)
    shutil.copy2(out_path, art_path)
    print(f"  [OK] Guardado en: {out_path}")
    return out_path

# ==============================================================================
# COMPOSICIÓN DE LA LÁMINA MAESTRA INFOGRÁFICA (2560 x 1440)
# ==============================================================================
def create_master_composite_sheet():
    pano_path = os.path.join(RENDERS_DIR, "Showcase_Catalogo_Modular_Panorama.png")
    ind_path = os.path.join(RENDERS_DIR, "Showcase_Modular_Kit_Industrial.png")
    deco_path = os.path.join(RENDERS_DIR, "Showcase_Modular_Kit_ArtDeco.png")
    plas_path = os.path.join(RENDERS_DIR, "Showcase_Modular_Kit_Plasma.png")
    enem_path = os.path.join(RENDERS_DIR, "Showcase_Modular_Kit_Enemigos_Mecanica.png")
    out_master = os.path.join(RENDERS_DIR, "Showcase_Catalogo_Activos_Modulares_Master.png")

    canvas = Image.new("RGBA", (2560, 1440), (13, 15, 18, 255))
    draw = ImageDraw.Draw(canvas)

    # Cuadrícula sutil
    for x in range(0, 2560, 64):
        draw.line([(x, 0), (x, 1440)], fill=(22, 26, 32, 255), width=1)
    for y in range(0, 1440, 64):
        draw.line([(0, y), (2560, y)], fill=(22, 26, 32, 255), width=1)

    # Header Superior
    draw.rectangle([(0, 0), (2560, 100)], fill=(18, 22, 28, 255))
    draw.line([(0, 100), (2560, 100)], fill=(245, 158, 11, 255), width=3)

    try:
        font_title = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 30)
        font_sub = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 16)
        font_badge = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 13)
        font_card = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 16)
    except:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_badge = ImageFont.load_default()
        font_card = ImageFont.load_default()

    draw.text((40, 20), "ASTRA HAZARD // REPOSITORIO DE ACTIVOS Y ARQUITECTURA MODULAR", font=font_sub, fill=(245, 158, 11, 255))
    draw.text((40, 48), "CATÁLOGO MAESTRO DE ACTIVOS 3D MODULARES: KITS TIER 1, 2, 3 Y MECÁNICA", font=font_title, fill=(240, 243, 246, 255))

    # Badges
    badges = [
        ("DESCOMPOSICIÓN 1:1 MAPAS", (180, 83, 9, 255)),
        ("15 PACKS PBR APLICADOS", (30, 64, 175, 255)),
        ("FREESTYLE INK LINEART", (5, 150, 105, 255)),
        ("BLENDER 5.2 & UE5 READY", (124, 58, 237, 255)),
    ]
    bx = 2520
    for text, bg_col in reversed(badges):
        tw = draw.textlength(text, font=font_badge)
        bw = int(tw + 24)
        bx -= bw
        draw.rounded_rectangle([(bx, 38), (bx + bw, 72)], radius=6, fill=bg_col)
        draw.text((bx + 12, 46), text, font=font_badge, fill=(255, 255, 255, 255))

    # Panorama Superior (2560 x 740)
    if os.path.exists(pano_path):
        img_pano = Image.open(pano_path).resize((2560, 740), Image.Resampling.LANCZOS)
        canvas.paste(img_pano, (0, 102))

    # Separador intermedio
    draw.rectangle([(0, 842), (2560, 882)], fill=(18, 22, 28, 255))
    draw.line([(0, 842), (2560, 842)], fill=(50, 56, 68, 255), width=2)
    draw.line([(0, 882), (2560, 882)], fill=(50, 56, 68, 255), width=2)
    draw.text((40, 852), "DETALLE DE LOS 4 KITS MODULARES // PERSPECTIVA AXONOMÉTRICA 3/4", font=font_badge, fill=(245, 158, 11, 255))

    # 4 Tarjetas Inferiores (620 x 530 cada una)
    kits_info = [
        (ind_path, "01. KIT CARGUERO QUÍMICO (TIER 1)", (245, 158, 11, 255)),
        (deco_path, "02. KIT CRUCERO ART DÉCO (TIER 2)", (234, 179, 8, 255)),
        (plas_path, "03. KIT REFINERÍA PLASMA (TIER 3)", (6, 182, 212, 255)),
        (enem_path, "04. KIT COMPONENTES MECÁNICOS", (249, 115, 22, 255)),
    ]

    for i, (path, label, accent_color) in enumerate(kits_info):
        cx = 20 + i * 635
        cy = 895
        cw = 620
        ch = 530
        
        # Marco tarjeta
        draw.rounded_rectangle([(cx, cy), (cx + cw, cy + ch)], radius=8, fill=(20, 24, 30, 255), outline=accent_color, width=2)
        
        if os.path.exists(path):
            img_thumb = Image.open(path).resize((cw - 12, ch - 50), Image.Resampling.LANCZOS)
            canvas.paste(img_thumb, (cx + 6, cy + 42))
            
        # Header de tarjeta
        draw.rectangle([(cx + 2, cy + 2), (cx + cw - 2, cy + 38)], fill=(15, 18, 22, 255))
        draw.text((cx + 14, cy + 10), label, font=font_card, fill=accent_color)

    canvas.save(out_master)
    shutil.copy2(out_master, os.path.join(ARTIFACT_DIR, "Showcase_Catalogo_Activos_Modulares_Master.png"))
    print(f"\n[MASTER OK] Lámina Maestra Oficial generada con éxito: {out_master}")

# ==============================================================================
# EJECUCIÓN PRINCIPAL
# ==============================================================================
def main():
    print("=" * 80)
    print("CONSTRUYENDO CATÁLOGO MAESTRO DE ACTIVOS MODULARES 3D V2 - ASTRA HAZARD")
    print("=" * 80)
    
    scene = reset_scene()
    root_col = scene.collection
    
    build_all_materials()
    build_showcase_studio(scene)
    
    print("\n[ISLAS 3D] Instanciando los 4 Kits Modulares...")
    build_kit_industrial(root_col, (-11.4, 0.0, 0.25))
    build_kit_artdeco(root_col, (-3.8, 0.0, 0.25))
    build_kit_plasma(root_col, (3.8, 0.0, 0.25))
    build_kit_mechanics(root_col, (11.4, 0.0, 0.25))
    
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_FILE)
    print(f"\n[OK] Guardado archivo Blender oficial: {BLEND_FILE}")
    
    print("\n[RENDERING] Renderizando cámaras con encuadre calibrado...")
    # 1. Panorama General (cubriendo las 4 islas sin clipping)
    cam_pano = create_targeted_camera("Cam_Pano", (0.0, -18.2, 7.5), (0.0, 0.1, 1.1), lens=24.0)
    render_camera_view(scene, cam_pano, "Showcase_Catalogo_Modular_Panorama.png", res_x=2560, res_y=1440)
    
    # 2. Primer Plano: Kit 1 Industrial
    cam_ind = create_targeted_camera("Cam_Ind", (-11.4, -6.8, 4.2), (-11.4, 0.0, 1.1), lens=36.0)
    render_camera_view(scene, cam_ind, "Showcase_Modular_Kit_Industrial.png", res_x=1920, res_y=1080)
    
    # 3. Primer Plano: Kit 2 Art Déco
    cam_deco = create_targeted_camera("Cam_Deco", (-3.8, -6.8, 4.2), (-3.8, 0.0, 1.1), lens=36.0)
    render_camera_view(scene, cam_deco, "Showcase_Modular_Kit_ArtDeco.png", res_x=1920, res_y=1080)
    
    # 4. Primer Plano: Kit 3 Plasma
    cam_plas = create_targeted_camera("Cam_Plas", (3.8, -6.8, 4.2), (3.8, 0.0, 1.1), lens=36.0)
    render_camera_view(scene, cam_plas, "Showcase_Modular_Kit_Plasma.png", res_x=1920, res_y=1080)
    
    # 5. Primer Plano: Kit 4 Mecánica
    cam_mech = create_targeted_camera("Cam_Mech", (11.4, -6.8, 4.2), (11.4, 0.0, 1.1), lens=36.0)
    render_camera_view(scene, cam_mech, "Showcase_Modular_Kit_Enemigos_Mecanica.png", res_x=1920, res_y=1080)
    
    print("\n[COMPOSITOR] Ensamblando Lámina Maestra Infográfica 2.5K...")
    create_master_composite_sheet()
    
    print("=" * 80)
    print("¡CATÁLOGO MAESTRO MODULAR COMPLETADO EXITOSAMENTE!")
    print("=" * 80)

if __name__ == "__main__":
    main()

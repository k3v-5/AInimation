# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Generador Maestro del Catálogo de Activos 3D Modulares y Reutilizables - Astra Hazard
# Descomposición Fiel 1:1 de los 3 Mapas (media_1791273626834.png) y Componentes de Enemigos
# Blender 5.2 LTS - Shaders PBR Estilizados, Multi-Material Per-Face, Freestyle Lineart y Cámaras 3/4

import bpy
import bmesh
import math
import os
import shutil
from mathutils import Vector, Euler
from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = r"F:\Dev\Game"
RENDERS_DIR = os.path.join(PROJECT_ROOT, "Art", "Renders")
TEXTURES_DIR = os.path.join(PROJECT_ROOT, "Art", "Textures")
TEXTURES_MAPS = os.path.join(PROJECT_ROOT, "Art", "Textures", "Maps")
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
    
    # Configuración de Freestyle para Lineart estilo Cómic/Novela Gráfica
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
    linestyle.color = (0.05, 0.04, 0.04)
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

def add_bevel(obj, width=0.012, segments=2, angle_limit=35.0):
    mod = obj.modifiers.new(name="Bevel", type='BEVEL')
    mod.width = width
    mod.segments = segments
    mod.limit_method = 'ANGLE'
    mod.angle_limit = math.radians(angle_limit)
    return mod

def create_cylinder(bm, radius=0.1, depth=1.0, segments=16, cap_ends=True, cap_tris=False):
    return bmesh.ops.create_cone(bm, cap_ends=cap_ends, cap_tris=cap_tris, radius1=radius, radius2=radius, depth=depth, segments=segments)

def assign_mat(bm, op_result, idx):
    v_set = set(op_result['verts'])
    for f in bm.faces:
        if all(v in v_set for v in f.verts):
            f.material_index = idx

def create_material(name, base_color, metallic=0.0, roughness=0.5, emission_color=(0,0,0,1), emission_strength=0.0, texture_path=None, box_scale=(1,1,1)):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    node_out.location = (450, 0)
    
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (100, 0)
    node_bsdf.inputs['Metallic'].default_value = metallic
    node_bsdf.inputs['Roughness'].default_value = roughness
    
    if texture_path and os.path.exists(texture_path):
        tex_node = nodes.new(type='ShaderNodeTexImage')
        tex_node.location = (-300, 100)
        tex_node.projection = 'BOX'
        tex_node.projection_blend = 0.2
        
        coord_node = nodes.new(type='ShaderNodeTexCoord')
        coord_node.location = (-700, 100)
        
        mapping_node = nodes.new(type='ShaderNodeMapping')
        mapping_node.location = (-500, 100)
        mapping_node.inputs['Scale'].default_value = box_scale
        
        links.new(coord_node.outputs['Object'], mapping_node.inputs['Vector'])
        links.new(mapping_node.outputs['Vector'], tex_node.inputs['Vector'])
        
        try:
            img = bpy.data.images.load(texture_path)
            tex_node.image = img
            links.new(tex_node.outputs['Color'], node_bsdf.inputs['Base Color'])
        except Exception:
            node_bsdf.inputs['Base Color'].default_value = (*base_color, 1.0)
    else:
        node_bsdf.inputs['Base Color'].default_value = (*base_color, 1.0)
        
    if emission_strength > 0.0:
        node_bsdf.inputs['Emission Color'].default_value = emission_color
        node_bsdf.inputs['Emission Strength'].default_value = emission_strength
        
    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])
    return mat

# Diccionario de Materiales
MATS = {}

def build_materials():
    t_cargo = os.path.join(TEXTURES_MAPS, "tex_cargo_hull.png")
    t_wood = os.path.join(TEXTURES_MAPS, "tex_artdeco_wood.png")
    t_carpet = os.path.join(TEXTURES_MAPS, "tex_artdeco_carpet.png")
    t_ref_sign = os.path.join(TEXTURES_MAPS, "tex_refineria_sign.png")
    t_dial = os.path.join(TEXTURES_DIR, "tex_dial_analogo.png")
    t_ind_trim = os.path.join(TEXTURES_MODULAR, "T_Trim_Industrial_Modular.png")

    # 1. Industrial & Estructural
    MATS["Ind_Yellow"] = create_material("M_Ind_Yellow", (0.92, 0.72, 0.08), 0.15, 0.42)
    MATS["Ind_Steel"] = create_material("M_Ind_Steel", (0.28, 0.27, 0.26), 0.82, 0.45)
    MATS["Ind_Grate"] = create_material("M_Ind_Grate", (0.16, 0.16, 0.17), 0.85, 0.55, texture_path=t_ind_trim, box_scale=(1.5,1.5,1.5))
    MATS["Ind_Hazard_Stripe"] = create_material("M_Ind_Hazard", (0.95, 0.8, 0.05), 0.1, 0.35, texture_path=t_ind_trim, box_scale=(1.0,1.0,1.0))
    MATS["Ind_Cont_Hull"] = create_material("M_Ind_Cont_Hull", (0.45, 0.25, 0.15), 0.35, 0.5, texture_path=t_cargo, box_scale=(0.4,0.4,0.4))
    MATS["Ind_Acid_Green"] = create_material("M_Ind_Acid_Green", (0.15, 0.95, 0.1), 0.0, 0.1, emission_color=(0.18, 1.0, 0.12, 1.0), emission_strength=7.5)
    MATS["Ind_Valve_Red"] = create_material("M_Ind_Valve_Red", (0.88, 0.12, 0.08), 0.1, 0.35)

    # 2. Art Déco & Mobiliario de Lujo (Terciopelo Burdeos Profundo #4A0E18)
    MATS["Deco_Velvet_Burgundy"] = create_material("M_Deco_Velvet", (0.055, 0.006, 0.012), 0.02, 0.72)
    MATS["Deco_Brass_Gold"] = create_material("M_Deco_Brass_Gold", (0.96, 0.78, 0.26), 0.95, 0.22)
    MATS["Deco_Mahogany_Wood"] = create_material("M_Deco_Mahogany", (0.22, 0.07, 0.035), 0.02, 0.32)
    MATS["Deco_Wall_Panel"] = create_material("M_Deco_Wall_Panel", (0.28, 0.1, 0.05), 0.15, 0.35, texture_path=t_wood, box_scale=(0.5,0.5,0.5))
    MATS["Deco_Carpet"] = create_material("M_Deco_Carpet", (0.35, 0.03, 0.08), 0.05, 0.85, texture_path=t_carpet, box_scale=(0.5,0.5,0.5))
    MATS["Deco_Glass_WarmGlow"] = create_material("M_Deco_Glass_Warm", (1.0, 0.92, 0.82), 0.1, 0.15, emission_color=(1.0, 0.86, 0.62, 1.0), emission_strength=3.5)
    MATS["Deco_Mirror_Glass"] = create_material("M_Deco_Mirror", (0.92, 0.94, 0.96), 0.98, 0.04)

    # 3. Plasma Sci-Fi & Energía
    MATS["Plas_Gunmetal"] = create_material("M_Plas_Gunmetal", (0.16, 0.18, 0.22), 0.82, 0.38)
    MATS["Plas_Copper"] = create_material("M_Plas_Copper", (0.85, 0.42, 0.18), 0.9, 0.28)
    MATS["Plas_Cyan_Glow"] = create_material("M_Plas_Cyan_Glow", (0.02, 0.85, 1.0), 0.0, 0.05, emission_color=(0.04, 0.88, 1.0, 1.0), emission_strength=7.0)
    MATS["Plas_Electric_White"] = create_material("M_Plas_Electric_White", (0.7, 0.95, 1.0), 0.0, 0.02, emission_color=(0.85, 0.98, 1.0, 1.0), emission_strength=10.0)
    MATS["Plas_Sign_Hazard"] = create_material("M_Plas_Sign_Hazard", (0.96, 0.82, 0.1), 0.1, 0.35, texture_path=t_ref_sign, box_scale=(0.7,0.7,0.7))
    MATS["Plas_Headlight"] = create_material("M_Plas_Headlight", (1.0, 0.98, 0.9), 0.0, 0.1, emission_color=(1.0, 0.98, 0.9, 1.0), emission_strength=8.0)

    # 4. Componentes de Enemigos & Mecánica
    MATS["Mech_Chrome"] = create_material("M_Mech_Chrome", (0.92, 0.94, 0.96), 0.98, 0.05)
    MATS["Mech_DarkIron"] = create_material("M_Mech_DarkIron", (0.22, 0.21, 0.2), 0.82, 0.48)
    MATS["Mech_Dial_Face"] = create_material("M_Mech_Dial_Face", (0.98, 0.98, 0.95), 0.05, 0.25, texture_path=t_dial, box_scale=(1.2,1.2,1.2), emission_color=(0.95, 0.95, 0.9, 1.0), emission_strength=1.5)
    MATS["Mech_Sensor_Emerald"] = create_material("M_Mech_Sensor_Emerald", (0.08, 0.95, 0.42), 0.05, 0.1, emission_color=(0.1, 1.0, 0.48, 1.0), emission_strength=7.0)
    MATS["Mech_Flame_Outer"] = create_material("M_Mech_Flame_Outer", (0.95, 0.18, 0.02), 0.0, 0.2, emission_color=(1.0, 0.25, 0.02, 1.0), emission_strength=2.2)
    MATS["Mech_Flame_Inner"] = create_material("M_Mech_Flame_Inner", (1.0, 0.82, 0.05), 0.0, 0.1, emission_color=(1.0, 0.9, 0.1, 1.0), emission_strength=4.0)

    # 5. Estudio & Pedestales
    MATS["Studio_Floor"] = create_material("M_Studio_Floor", (0.09, 0.095, 0.105), 0.35, 0.65)
    MATS["Pedestal_Body"] = create_material("M_Pedestal_Body", (0.13, 0.14, 0.16), 0.4, 0.5)
    MATS["LED_Strip_Yellow"] = create_material("M_LED_Yellow", (0.95, 0.75, 0.1), 0.0, 0.1, emission_color=(0.95, 0.75, 0.1, 1.0), emission_strength=5.0)
    MATS["LED_Strip_Gold"] = create_material("M_LED_Gold", (0.95, 0.8, 0.3), 0.0, 0.1, emission_color=(0.95, 0.8, 0.3, 1.0), emission_strength=5.0)
    MATS["LED_Strip_Cyan"] = create_material("M_LED_Cyan", (0.1, 0.85, 1.0), 0.0, 0.1, emission_color=(0.1, 0.85, 1.0, 1.0), emission_strength=5.0)
    MATS["LED_Strip_Orange"] = create_material("M_LED_Orange", (1.0, 0.45, 0.1), 0.0, 0.1, emission_color=(1.0, 0.45, 0.1, 1.0), emission_strength=5.0)

def finalize_asset(obj, col, location=(0,0,0), rotation=(0,0,0)):
    col.objects.link(obj)
    obj.location = Vector(location)
    obj.rotation_euler = Euler((R(rotation[0]), R(rotation[1]), R(rotation[2])), 'XYZ')
    bpy.context.view_layer.update()
    return obj

# ==============================================================================
# 1. KIT INDUSTRIAL Y ESTRUCTURAL (CARGUERO QUÍMICO)
# ==============================================================================
def build_kit_industrial(parent_col, base_origin=(-12.0, 0.0, 0.25)):
    col = create_collection("Kit_01_Industrial_Cargo", parent_col)
    ox, oy, oz = base_origin

    # 1. Columna I-Beam Vertical Apernada 4m
    mesh_col = bpy.data.meshes.new("SM_Ind_Beam_Column_4m_Mesh")
    obj_col = bpy.data.objects.new("SM_Ind_Beam_Column_4m", mesh_col)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= 0.26
        v.co.y *= 0.26
        v.co.z = (v.co.z + 0.5) * 3.8
    p_base = bmesh.ops.create_cube(bm, size=1.0)
    for v in p_base['verts']:
        v.co.x *= 0.62
        v.co.y *= 0.62
        v.co.z = (v.co.z + 0.5) * 0.06
    for bx, by in [(-0.22, -0.22), (0.22, -0.22), (-0.22, 0.22), (0.22, 0.22)]:
        b = create_cylinder(bm, radius=0.03, depth=0.05, segments=6)
        for v in b['verts']:
            v.co.x += bx
            v.co.y += by
            v.co.z += 0.08
    c_top = bmesh.ops.create_cube(bm, size=1.0)
    for v in c_top['verts']:
        v.co.x *= 0.46
        v.co.y *= 0.46
        v.co.z = 3.8 + (v.co.z + 0.5) * 0.08
    bm.to_mesh(mesh_col)
    bm.free()
    obj_col.data.materials.append(MATS["Ind_Yellow"])
    add_bevel(obj_col, width=0.012)
    finalize_asset(obj_col, col, (ox - 2.2, oy + 1.2, oz))

    # 2. Viga Horizontal I-Beam 4m
    mesh_beam = bpy.data.meshes.new("SM_Ind_Beam_I_Straight_4m_Mesh")
    obj_beam = bpy.data.objects.new("SM_Ind_Beam_I_Straight_4m", mesh_beam)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= 3.8
        v.co.y *= 0.08
        v.co.z = 0.35 + v.co.z * 0.35
    for z_wing in [0.18, 0.52]:
        w = bmesh.ops.create_cube(bm, size=1.0)
        for v in w['verts']:
            v.co.x *= 3.8
            v.co.y *= 0.28
            v.co.z = z_wing + v.co.z * 0.04
    bm.to_mesh(mesh_beam)
    bm.free()
    obj_beam.data.materials.append(MATS["Ind_Yellow"])
    add_bevel(obj_beam, width=0.01)
    finalize_asset(obj_beam, col, (ox - 0.4, oy + 1.2, oz + 3.2))

    # 3. Contenedor de Carga Corrugado
    mesh_cont = bpy.data.meshes.new("SM_Ind_CargoContainer_Standard_Mesh")
    obj_cont = bpy.data.objects.new("SM_Ind_CargoContainer_Standard", mesh_cont)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= 2.5
        v.co.y *= 1.3
        v.co.z = (v.co.z + 0.5) * 1.35
    for nx in [-0.9, -0.6, -0.3, 0.0, 0.3, 0.6, 0.9]:
        rib = bmesh.ops.create_cube(bm, size=1.0)
        for v in rib['verts']:
            v.co.x = nx + v.co.x * 0.12
            v.co.y *= 1.36
            v.co.z = (v.co.z + 0.5) * 1.3 + 0.025
    bm.to_mesh(mesh_cont)
    bm.free()
    obj_cont.data.materials.append(MATS["Ind_Cont_Hull"])
    add_bevel(obj_cont, width=0.012)
    finalize_asset(obj_cont, col, (ox + 1.3, oy + 0.8, oz), rotation=(0, 0, -12))

    # 4. Foso de Ácido Químico Modular Abierto
    mesh_vat = bpy.data.meshes.new("SM_Ind_AcidVat_Modular_Mesh")
    obj_vat = bpy.data.objects.new("SM_Ind_AcidVat_Modular", mesh_vat)
    bm = bmesh.new()
    # Suelo del tanque
    floor = bmesh.ops.create_cube(bm, size=1.0)
    for v in floor['verts']:
        v.co.x *= 2.2
        v.co.y *= 1.4
        v.co.z = (v.co.z + 0.5) * 0.12
    # Pared frontal
    w_front = bmesh.ops.create_cube(bm, size=1.0)
    for v in w_front['verts']:
        v.co.x *= 2.2
        v.co.y = -0.65 + v.co.y * 0.1
        v.co.z = 0.12 + (v.co.z + 0.5) * 0.95
    # Pared trasera
    w_back = bmesh.ops.create_cube(bm, size=1.0)
    for v in w_back['verts']:
        v.co.x *= 2.2
        v.co.y = 0.65 + v.co.y * 0.1
        v.co.z = 0.12 + (v.co.z + 0.5) * 0.95
    # Pared izquierda
    w_left = bmesh.ops.create_cube(bm, size=1.0)
    for v in w_left['verts']:
        v.co.x = -1.05 + v.co.x * 0.1
        v.co.y *= 1.2
        v.co.z = 0.12 + (v.co.z + 0.5) * 0.95
    # Pared derecha
    w_right = bmesh.ops.create_cube(bm, size=1.0)
    for v in w_right['verts']:
        v.co.x = 1.05 + v.co.x * 0.1
        v.co.y *= 1.2
        v.co.z = 0.12 + (v.co.z + 0.5) * 0.95
    # Reborde superior de seguridad (Hazard Stripe) (Slot 1)
    rim = bmesh.ops.create_cube(bm, size=1.0)
    for v in rim['verts']:
        v.co.x *= 2.3
        v.co.y *= 1.5
        v.co.z = 1.05 + (v.co.z + 0.5) * 0.08
    assign_mat(bm, rim, 1)
    # Marco de ventana de observación en pared frontal (Slot 1)
    w_frame = bmesh.ops.create_cube(bm, size=1.0)
    for v in w_frame['verts']:
        v.co.x *= 1.4
        v.co.y = -0.71 + v.co.y * 0.04
        v.co.z = 0.35 + (v.co.z + 0.5) * 0.55
    assign_mat(bm, w_frame, 1)
    bm.to_mesh(mesh_vat)
    bm.free()
    obj_vat.data.materials.append(MATS["Ind_Steel"])
    obj_vat.data.materials.append(MATS["Ind_Hazard_Stripe"])
    add_bevel(obj_vat, width=0.012)
    finalize_asset(obj_vat, col, (ox - 0.6, oy + 0.2, oz))

    # Ácido Verde Fosforescente Líquido en Superficie Abierta
    mesh_liq = bpy.data.meshes.new("SM_Ind_AcidLiquid_Mesh")
    obj_liq = bpy.data.objects.new("SM_Ind_AcidLiquid", mesh_liq)
    bm_l = bmesh.new()
    liq = bmesh.ops.create_cube(bm_l, size=1.0)
    for v in liq['verts']:
        v.co.x *= 2.0
        v.co.y *= 1.2
        v.co.z = 0.12 + (v.co.z + 0.5) * 0.72
    # Burbujas y vapores químicos en superficie
    for vx, vy, vrad in [(-0.55, -0.2, 0.18), (0.1, 0.15, 0.22), (0.6, -0.1, 0.15), (-0.1, -0.3, 0.12)]:
        bub = bmesh.ops.create_uvsphere(bm_l, u_segments=12, v_segments=10, radius=vrad)
        for v in bub['verts']:
            v.co.x += vx
            v.co.y += vy
            v.co.z += 0.84
        cone = bmesh.ops.create_cone(bm_l, cap_ends=True, radius1=vrad*0.9, radius2=0.02, depth=0.55, segments=6)
        for v in cone['verts']:
            v.co.x += vx
            v.co.y += vy
            v.co.z += 0.85 + 0.27
    bm_l.to_mesh(mesh_liq)
    bm_l.free()
    obj_liq.data.materials.append(MATS["Ind_Acid_Green"])
    finalize_asset(obj_liq, col, (ox - 0.6, oy + 0.2, oz))

    # 5. Suelo de Rejilla Metálica Modular 2x2m
    mesh_grate = bpy.data.meshes.new("SM_Ind_Grate_Floor_2x2m_Mesh")
    obj_grate = bpy.data.objects.new("SM_Ind_Grate_Floor_2x2m", mesh_grate)
    bm = bmesh.new()
    frame = bmesh.ops.create_cube(bm, size=1.0)
    for v in frame['verts']:
        v.co.x *= 1.8
        v.co.y *= 1.8
        v.co.z = (v.co.z + 0.5) * 0.08
    mesh_in = bmesh.ops.create_cube(bm, size=1.0)
    for v in mesh_in['verts']:
        v.co.x *= 1.65
        v.co.y *= 1.65
        v.co.z = 0.03 + (v.co.z + 0.5) * 0.04
    bm.to_mesh(mesh_grate)
    bm.free()
    obj_grate.data.materials.append(MATS["Ind_Grate"])
    add_bevel(obj_grate, width=0.008)
    finalize_asset(obj_grate, col, (ox - 1.4, oy - 1.2, oz))

    # 6. Barandilla Tubular de Seguridad Amarilla 2m
    mesh_rail = bpy.data.meshes.new("SM_Ind_Handrail_Tubular_2m_Mesh")
    obj_rail = bpy.data.objects.new("SM_Ind_Handrail_Tubular_2m", mesh_rail)
    bm = bmesh.new()
    for px in [-0.85, 0.85]:
        p = create_cylinder(bm, radius=0.032, depth=1.0, segments=12)
        for v in p['verts']:
            v.co.x += px
            v.co.z += 0.5
        f = create_cylinder(bm, radius=0.065, depth=0.02, segments=12)
        for v in f['verts']:
            v.co.x += px
            v.co.z += 0.01
    for rz, rrad in [(1.0, 0.035), (0.52, 0.025)]:
        r = create_cylinder(bm, radius=rrad, depth=1.8, segments=14)
        for v in r['verts']:
            old_z = v.co.z
            v.co.z = v.co.x + rz
            v.co.x = old_z
    bm.to_mesh(mesh_rail)
    bm.free()
    obj_rail.data.materials.append(MATS["Ind_Yellow"])
    add_bevel(obj_rail, width=0.006)
    finalize_asset(obj_rail, col, (ox - 1.4, oy - 1.9, oz))

    # 7. Tubería Industrial con Válvula de Paso Roja
    mesh_pipe = bpy.data.meshes.new("SM_Ind_Pipe_Straight_2m_Mesh")
    obj_pipe = bpy.data.objects.new("SM_Ind_Pipe_Straight_2m", mesh_pipe)
    bm = bmesh.new()
    p = create_cylinder(bm, radius=0.14, depth=2.0, segments=20)
    for v in p['verts']:
        old_z = v.co.z
        v.co.z = v.co.x + 0.16
        v.co.x = old_z
    for fx in [-1.0, 1.0]:
        fl = create_cylinder(bm, radius=0.24, depth=0.06, segments=20)
        for v in fl['verts']:
            old_z = v.co.z
            v.co.z = v.co.x + 0.16
            v.co.x = old_z + fx
    # Volante rojo (Slot 1)
    wheel = create_cylinder(bm, radius=0.2, depth=0.04, segments=18)
    for v in wheel['verts']:
        v.co.z += 0.44
    stem = create_cylinder(bm, radius=0.035, depth=0.22, segments=10)
    for v in stem['verts']:
        v.co.z += 0.28
    assign_mat(bm, wheel, 1)
    bm.to_mesh(mesh_pipe)
    bm.free()
    obj_pipe.data.materials.append(MATS["Ind_Steel"])
    obj_pipe.data.materials.append(MATS["Ind_Valve_Red"])
    add_bevel(obj_pipe, width=0.008)
    finalize_asset(obj_pipe, col, (ox + 1.2, oy - 1.1, oz))

    return col

# ==============================================================================
# 2. KIT ART DÉCO Y MOBILIARIO DE LUJO (CRUCERO 'CELESTIA')
# ==============================================================================
def build_kit_artdeco(parent_col, base_origin=(-4.0, 0.0, 0.25)):
    col = create_collection("Kit_02_ArtDeco_Luxury", parent_col)
    ox, oy, oz = base_origin

    # 0. Alfombra de Terciopelo y Greca Dorada Art Déco
    mesh_carp = bpy.data.meshes.new("SM_Deco_Luxury_Carpet_Mesh")
    obj_carp = bpy.data.objects.new("SM_Deco_Luxury_Carpet", mesh_carp)
    bm_c = bmesh.new()
    carp = bmesh.ops.create_cube(bm_c, size=1.0)
    for v in carp['verts']:
        v.co.x *= 4.0
        v.co.y *= 2.8
        v.co.z = (v.co.z + 0.5) * 0.02
    bm_c.to_mesh(mesh_carp)
    bm_c.free()
    obj_carp.data.materials.append(MATS["Deco_Carpet"])
    finalize_asset(obj_carp, col, (ox + 0.2, oy - 0.2, oz))

    # 1. Panel de Pared Art Déco de Caoba con Molduras de Oro (Fondo)
    mesh_wp = bpy.data.meshes.new("SM_Deco_WallPanel_2x3m_Mesh")
    obj_wp = bpy.data.objects.new("SM_Deco_WallPanel_2x3m", mesh_wp)
    bm = bmesh.new()
    wall = bmesh.ops.create_cube(bm, size=1.0)
    for v in wall['verts']:
        v.co.x *= 2.4
        v.co.y *= 0.12
        v.co.z = (v.co.z + 0.5) * 3.2
    mould = bmesh.ops.create_cube(bm, size=1.0)
    for v in mould['verts']:
        v.co.x *= 2.0
        v.co.y = 0.08 + v.co.y * 0.04
        v.co.z = 0.3 + (v.co.z + 0.5) * 2.6
    bm.to_mesh(mesh_wp)
    bm.free()
    obj_wp.data.materials.append(MATS["Deco_Wall_Panel"])
    obj_wp.data.materials.append(MATS["Deco_Brass_Gold"])
    add_bevel(obj_wp, width=0.01)
    finalize_asset(obj_wp, col, (ox + 0.4, oy + 1.8, oz))

    # 2. Espejo Biselado Octogonal con Marco Dorado
    mesh_mir = bpy.data.meshes.new("SM_Deco_Mirror_Octagonal_Mesh")
    obj_mir = bpy.data.objects.new("SM_Deco_Mirror_Octagonal", mesh_mir)
    bm = bmesh.new()
    fr = create_cylinder(bm, radius=0.6, depth=0.05, segments=8)
    for v in fr['verts']:
        old_y = v.co.y
        v.co.y = v.co.z
        v.co.z = old_y + 1.5
    gl = create_cylinder(bm, radius=0.52, depth=0.03, segments=8)
    for v in gl['verts']:
        old_y = v.co.y
        v.co.y = v.co.z - 0.015
        v.co.z = old_y + 1.5
    assign_mat(bm, gl, 1)
    bm.to_mesh(mesh_mir)
    bm.free()
    obj_mir.data.materials.append(MATS["Deco_Brass_Gold"])
    obj_mir.data.materials.append(MATS["Deco_Mirror_Glass"])
    add_bevel(obj_mir, width=0.008)
    finalize_asset(obj_mir, col, (ox + 0.4, oy + 1.7, oz))

    # 3. Candelabro Concéntrico de Cristal y Latón 3 Niveles
    mesh_ch = bpy.data.meshes.new("SM_Deco_Chandelier_Tiered_Mesh")
    obj_ch = bpy.data.objects.new("SM_Deco_Chandelier_Tiered", mesh_ch)
    bm = bmesh.new()
    rod = create_cylinder(bm, radius=0.025, depth=0.6, segments=12)
    for v in rod['verts']:
        v.co.z += 1.3
    t1 = create_cylinder(bm, radius=0.55, depth=0.14, segments=24)
    for v in t1['verts']:
        v.co.z += 1.0
    t2 = create_cylinder(bm, radius=0.4, depth=0.14, segments=20)
    for v in t2['verts']:
        v.co.z += 0.82
    t3 = create_cylinder(bm, radius=0.25, depth=0.14, segments=16)
    for v in t3['verts']:
        v.co.z += 0.64
    fin = bmesh.ops.create_cone(bm, cap_ends=True, radius1=0.06, radius2=0.01, depth=0.12, segments=12)
    for v in fin['verts']:
        v.co.z += 0.5
    assign_mat(bm, t1, 1)
    assign_mat(bm, t2, 1)
    assign_mat(bm, t3, 1)
    bm.to_mesh(mesh_ch)
    bm.free()
    obj_ch.data.materials.append(MATS["Deco_Brass_Gold"])
    obj_ch.data.materials.append(MATS["Deco_Glass_WarmGlow"])
    add_bevel(obj_ch, width=0.008)
    finalize_asset(obj_ch, col, (ox, oy + 0.2, oz + 0.95))

    # 4. Lámpara de Pie de Salón (1.8m)
    mesh_lamp = bpy.data.meshes.new("SM_Deco_Lamp_Floor_Mesh")
    obj_lamp = bpy.data.objects.new("SM_Deco_Lamp_Floor", mesh_lamp)
    bm = bmesh.new()
    base = create_cylinder(bm, radius=0.22, depth=0.05, segments=24)
    for v in base['verts']:
        v.co.z += 0.025
    stem = create_cylinder(bm, radius=0.02, depth=1.5, segments=14)
    for v in stem['verts']:
        v.co.z += 0.8
    shade = bmesh.ops.create_cone(bm, cap_ends=True, radius1=0.26, radius2=0.12, depth=0.32, segments=20)
    for v in shade['verts']:
        v.co.z += 1.68
    assign_mat(bm, shade, 1)
    bm.to_mesh(mesh_lamp)
    bm.free()
    obj_lamp.data.materials.append(MATS["Deco_Brass_Gold"])
    obj_lamp.data.materials.append(MATS["Deco_Glass_WarmGlow"])
    add_bevel(obj_lamp, width=0.006)
    finalize_asset(obj_lamp, col, (ox - 2.1, oy + 0.8, oz))

    # 5. Mesita Auxiliar Redonda de Caoba y Cerco Dorado
    mesh_table = bpy.data.meshes.new("SM_Deco_SideTable_Round_Mesh")
    obj_table = bpy.data.objects.new("SM_Deco_SideTable_Round", mesh_table)
    bm = bmesh.new()
    top = create_cylinder(bm, radius=0.4, depth=0.04, segments=32)
    for v in top['verts']:
        v.co.z += 0.55
    shelf = create_cylinder(bm, radius=0.3, depth=0.03, segments=32)
    for v in shelf['verts']:
        v.co.z += 0.22
    rim = create_cylinder(bm, radius=0.41, depth=0.05, segments=32)
    for v in rim['verts']:
        v.co.z += 0.55
    assign_mat(bm, rim, 1)
    for i in range(3):
        ang = math.radians(i * 120)
        leg = create_cylinder(bm, radius=0.02, depth=0.55, segments=12)
        for v in leg['verts']:
            v.co.x += 0.32 * math.cos(ang)
            v.co.y += 0.32 * math.sin(ang)
            v.co.z += 0.275
        assign_mat(bm, leg, 1)
    # Lámpara sobre la mesita
    t_base = create_cylinder(bm, radius=0.08, depth=0.03, segments=14)
    for v in t_base['verts']:
        v.co.z += 0.58
    assign_mat(bm, t_base, 1)
    t_stem = create_cylinder(bm, radius=0.015, depth=0.18, segments=10)
    for v in t_stem['verts']:
        v.co.z += 0.67
    assign_mat(bm, t_stem, 1)
    t_shade = bmesh.ops.create_cone(bm, cap_ends=True, radius1=0.15, radius2=0.08, depth=0.16, segments=14)
    for v in t_shade['verts']:
        v.co.z += 0.83
    assign_mat(bm, t_shade, 2)
    bm.to_mesh(mesh_table)
    bm.free()
    obj_table.data.materials.append(MATS["Deco_Mahogany_Wood"])
    obj_table.data.materials.append(MATS["Deco_Brass_Gold"])
    obj_table.data.materials.append(MATS["Deco_Glass_WarmGlow"])
    add_bevel(obj_table, width=0.008)
    finalize_asset(obj_table, col, (ox - 0.2, oy - 0.2, oz))

    # 6. Butaca Individual Art Déco en Terciopelo Burdeos (Slot 0) y Patas de Latón (Slot 1)
    mesh_chair = bpy.data.meshes.new("SM_Deco_Armchair_Single_Mesh")
    obj_chair = bpy.data.objects.new("SM_Deco_Armchair_Single", mesh_chair)
    bm = bmesh.new()
    seat = bmesh.ops.create_cube(bm, size=1.0)
    for v in seat['verts']:
        v.co.x *= 0.78
        v.co.y *= 0.74
        v.co.z = 0.28 + (v.co.z + 0.5) * 0.22
    back = bmesh.ops.create_cube(bm, size=1.0)
    for v in back['verts']:
        v.co.x *= 0.78
        v.co.y = 0.32 + v.co.y * 0.18
        v.co.z = 0.45 + (v.co.z + 0.5) * 0.65
    for ax in [-0.42, 0.42]:
        arm = bmesh.ops.create_cube(bm, size=1.0)
        for v in arm['verts']:
            v.co.x = ax + v.co.x * 0.16
            v.co.y *= 0.72
            v.co.z = 0.35 + (v.co.z + 0.5) * 0.32
    # 4 Patas cónicas de latón (Slot 1)
    for lx, ly in [(-0.35, -0.32), (0.35, -0.32), (-0.35, 0.32), (0.35, 0.32)]:
        leg = bmesh.ops.create_cone(bm, cap_ends=True, radius1=0.035, radius2=0.015, depth=0.28, segments=12)
        for v in leg['verts']:
            v.co.x += lx
            v.co.y += ly
            v.co.z += 0.14
        assign_mat(bm, leg, 1)
    # Botones dorados (Slot 1)
    for bz in [0.65, 0.85]:
        for bx in [-0.2, 0.0, 0.2]:
            btn = create_cylinder(bm, radius=0.018, depth=0.02, segments=10)
            for v in btn['verts']:
                v.co.x += bx
                v.co.y += 0.23
                v.co.z += bz
            assign_mat(bm, btn, 1)
    bm.to_mesh(mesh_chair)
    bm.free()
    obj_chair.data.materials.append(MATS["Deco_Velvet_Burgundy"])
    obj_chair.data.materials.append(MATS["Deco_Brass_Gold"])
    add_bevel(obj_chair, width=0.015)
    finalize_asset(obj_chair, col, (ox - 1.5, oy - 1.0, oz), rotation=(0, 0, 22))

    # 7. Sofá Doble Art Déco en Capitoné Burdeos (Slot 0) y Patas de Latón (Slot 1)
    mesh_sofa = bpy.data.meshes.new("SM_Deco_Sofa_Double_Mesh")
    obj_sofa = bpy.data.objects.new("SM_Deco_Sofa_Double", mesh_sofa)
    bm = bmesh.new()
    seat = bmesh.ops.create_cube(bm, size=1.0)
    for v in seat['verts']:
        v.co.x *= 1.6
        v.co.y *= 0.78
        v.co.z = 0.28 + (v.co.z + 0.5) * 0.22
    back = bmesh.ops.create_cube(bm, size=1.0)
    for v in back['verts']:
        v.co.x *= 1.6
        v.co.y = 0.32 + v.co.y * 0.18
        v.co.z = 0.45 + (v.co.z + 0.5) * 0.65
    for ax in [-0.85, 0.85]:
        arm = bmesh.ops.create_cube(bm, size=1.0)
        for v in arm['verts']:
            v.co.x = ax + v.co.x * 0.18
            v.co.y *= 0.74
            v.co.z = 0.35 + (v.co.z + 0.5) * 0.32
    for lx, ly in [(-0.75, -0.32), (0.75, -0.32), (-0.75, 0.32), (0.75, 0.32)]:
        leg = bmesh.ops.create_cone(bm, cap_ends=True, radius1=0.04, radius2=0.018, depth=0.28, segments=12)
        for v in leg['verts']:
            v.co.x += lx
            v.co.y += ly
            v.co.z += 0.14
        assign_mat(bm, leg, 1)
    bm.to_mesh(mesh_sofa)
    bm.free()
    obj_sofa.data.materials.append(MATS["Deco_Velvet_Burgundy"])
    obj_sofa.data.materials.append(MATS["Deco_Brass_Gold"])
    add_bevel(obj_sofa, width=0.015)
    finalize_asset(obj_sofa, col, (ox + 1.2, oy - 0.9, oz), rotation=(0, 0, -18))

    return col

# ==============================================================================
# 3. KIT SCI-FI Y ENERGÍA (REFINERÍA DE PLASMA 'BLACK ROCK')
# ==============================================================================
def build_kit_plasma(parent_col, base_origin=(4.0, 0.0, 0.25)):
    col = create_collection("Kit_03_Plasma_Refinery", parent_col)
    ox, oy, oz = base_origin

    # 1. Reactor Tokamak Toroidal (Carcasa exterior en C con hueco central abierto)
    mesh_tok = bpy.data.meshes.new("SM_Plas_Tokamak_Segment_45_Mesh")
    obj_tok = bpy.data.objects.new("SM_Plas_Tokamak_Segment_45", mesh_tok)
    bm = bmesh.new()
    # Construcción de anillo toroidal hueco con 8 sectores poligonales
    num_sectors = 16
    r_major = 1.05
    r_tube = 0.24
    for i in range(num_sectors):
        phi1 = math.radians(i * (360 / num_sectors))
        phi2 = math.radians((i + 1) * (360 / num_sectors))
        # Segmento tubular
        c1 = Vector((r_major * math.cos(phi1), 0.0, 1.45 + r_major * math.sin(phi1)))
        c2 = Vector((r_major * math.cos(phi2), 0.0, 1.45 + r_major * math.sin(phi2)))
        seg = create_cylinder(bm, radius=r_tube, depth=(c2 - c1).length, segments=12)
        mid = (c1 + c2) * 0.5
        dir_v = (c2 - c1).normalized()
        rot_q = dir_v.to_track_quat('Z', 'Y')
        for v in seg['verts']:
            v.co = rot_q @ v.co + mid
    # 4 Abrazaderas magnéticas de cobre (Slot 1)
    for ca in [0, 90, 180, 270]:
        crad = math.radians(ca)
        clamp = create_cylinder(bm, radius=0.32, depth=0.18, segments=14)
        c_pos = Vector((r_major * math.cos(crad), 0.0, 1.45 + r_major * math.sin(crad)))
        for v in clamp['verts']:
            old_y = v.co.y
            v.co.y = v.co.z
            v.co.z = old_y
            v.co += c_pos
        assign_mat(bm, clamp, 1)
    bm.to_mesh(mesh_tok)
    bm.free()
    obj_tok.data.materials.append(MATS["Plas_Gunmetal"])
    obj_tok.data.materials.append(MATS["Plas_Copper"])
    add_bevel(obj_tok, width=0.012)
    finalize_asset(obj_tok, col, (ox, oy + 1.1, oz))

    # Núcleo de Plasma Cian Eléctrico Emisivo Flotando dentro del Anillo
    mesh_core = bpy.data.meshes.new("SM_Plas_PlasmaCore_Mesh")
    obj_core = bpy.data.objects.new("SM_Plas_PlasmaCore", mesh_core)
    bm_c = bmesh.new()
    # Anillo de plasma interior (r_major = 1.05, r_tube = 0.12)
    for i in range(16):
        phi1 = math.radians(i * 22.5)
        phi2 = math.radians((i + 1) * 22.5)
        c1 = Vector((1.05 * math.cos(phi1), 0.0, 1.45 + 1.05 * math.sin(phi1)))
        c2 = Vector((1.05 * math.cos(phi2), 0.0, 1.45 + 1.05 * math.sin(phi2)))
        p_seg = create_cylinder(bm_c, radius=0.12, depth=(c2 - c1).length, segments=8)
        mid = (c1 + c2) * 0.5
        dir_v = (c2 - c1).normalized()
        rot_q = dir_v.to_track_quat('Z', 'Y')
        for v in p_seg['verts']:
            v.co = rot_q @ v.co + mid
    # Orbe central con relámpagos
    p_orb = bmesh.ops.create_uvsphere(bm_c, u_segments=16, v_segments=12, radius=0.28)
    for v in p_orb['verts']:
        v.co.z += 1.45
    for i in range(8):
        ang = math.radians(i * 45)
        bolt = bmesh.ops.create_cone(bm_c, cap_ends=True, radius1=0.04, radius2=0.005, depth=0.75, segments=4)
        for v in bolt['verts']:
            v.co.x += math.cos(ang) * 0.38
            v.co.z += 1.45 + math.sin(ang) * 0.38
    bm_c.to_mesh(mesh_core)
    bm_c.free()
    obj_core.data.materials.append(MATS["Plas_Cyan_Glow"])
    finalize_asset(obj_core, col, (ox, oy + 1.1, oz))

    # 2. Bobina Magnética de Cobre Modular con Pistón (Fondo Derecha)
    mesh_coil = bpy.data.meshes.new("SM_Plas_Magnetic_Coil_Mesh")
    obj_coil = bpy.data.objects.new("SM_Plas_Magnetic_Coil", mesh_coil)
    bm = bmesh.new()
    c_ring = create_cylinder(bm, radius=0.58, depth=0.35, segments=24)
    for v in c_ring['verts']:
        v.co.z += 0.7
    cu_ring = create_cylinder(bm, radius=0.5, depth=0.42, segments=24)
    for v in cu_ring['verts']:
        v.co.z += 0.7
    assign_mat(bm, cu_ring, 1)
    pist = create_cylinder(bm, radius=0.08, depth=0.5, segments=12)
    for v in pist['verts']:
        v.co.x += 0.65
        v.co.z += 0.7
    assign_mat(bm, pist, 2)
    bm.to_mesh(mesh_coil)
    bm.free()
    obj_coil.data.materials.append(MATS["Plas_Gunmetal"])
    obj_coil.data.materials.append(MATS["Plas_Copper"])
    obj_coil.data.materials.append(MATS["Mech_Chrome"])
    add_bevel(obj_coil, width=0.01)
    finalize_asset(obj_coil, col, (ox + 2.0, oy + 0.9, oz), rotation=(0, 0, -25))

    # 3. Letrero de Advertencia Hazard "REFINERÍA DE PLASMA" (Fondo Izquierda)
    mesh_sign = bpy.data.meshes.new("SM_Plas_HazardSign_Wall_Mesh")
    obj_sign = bpy.data.objects.new("SM_Plas_HazardSign_Wall", mesh_sign)
    bm = bmesh.new()
    plaque = bmesh.ops.create_cube(bm, size=1.0)
    for v in plaque['verts']:
        v.co.x *= 1.3
        v.co.y *= 0.05
        v.co.z = 1.3 + v.co.z * 0.65
    for cx in [-0.45, 0.45]:
        ch = create_cylinder(bm, radius=0.02, depth=0.55, segments=8)
        for v in ch['verts']:
            v.co.x += cx
            v.co.z += 1.85
    bm.to_mesh(mesh_sign)
    bm.free()
    obj_sign.data.materials.append(MATS["Plas_Sign_Hazard"])
    add_bevel(obj_sign, width=0.008)
    finalize_asset(obj_sign, col, (ox - 2.0, oy + 0.9, oz), rotation=(0, 0, 20))

    # 4. Pasarela Curva Suspendida con Rejilla y Barandilla Tubular (Frente Izquierda)
    mesh_walk = bpy.data.meshes.new("SM_Plas_Curved_Catwalk_Mesh")
    obj_walk = bpy.data.objects.new("SM_Plas_Curved_Catwalk", mesh_walk)
    bm = bmesh.new()
    deck = bmesh.ops.create_cube(bm, size=1.0)
    for v in deck['verts']:
        v.co.x *= 2.2
        v.co.y *= 1.1
        v.co.z = 0.35 + v.co.z * 0.08
    for ry in [-0.52, 0.52]:
        for px in [-0.95, 0.0, 0.95]:
            p = create_cylinder(bm, radius=0.03, depth=0.85, segments=8)
            for v in p['verts']:
                v.co.x += px
                v.co.y += ry
                v.co.z += 0.35 + 0.425
            assign_mat(bm, p, 1)
        rail = create_cylinder(bm, radius=0.035, depth=2.1, segments=12)
        for v in rail['verts']:
            old_z = v.co.z
            v.co.z = v.co.x + 1.2
            v.co.x = old_z
            v.co.y += ry
        assign_mat(bm, rail, 1)
    bm.to_mesh(mesh_walk)
    bm.free()
    obj_walk.data.materials.append(MATS["Ind_Grate"])
    obj_walk.data.materials.append(MATS["Ind_Yellow"])
    add_bevel(obj_walk, width=0.008)
    finalize_asset(obj_walk, col, (ox - 1.4, oy - 1.2, oz), rotation=(0, 0, 32))

    # 5. Dron Minero / Servicio Flotante con 4 Propulsores y Faros Gemelos (Frente Derecha)
    mesh_drone = bpy.data.meshes.new("SM_Plas_MiningDrone_Chassis_Mesh")
    obj_drone = bpy.data.objects.new("SM_Plas_MiningDrone_Chassis", mesh_drone)
    bm = bmesh.new()
    body = bmesh.ops.create_cube(bm, size=1.0)
    for v in body['verts']:
        v.co.x *= 0.55
        v.co.y *= 0.55
        v.co.z = 0.75 + v.co.z * 0.45
    for tx, ty in [(-0.45, -0.45), (0.45, -0.45), (-0.45, 0.45), (0.45, 0.45)]:
        thr = create_cylinder(bm, radius=0.12, depth=0.25, segments=14)
        for v in thr['verts']:
            v.co.x += tx
            v.co.y += ty
            v.co.z += 0.75
        assign_mat(bm, thr, 1)
    for fx in [-0.18, 0.18]:
        head = create_cylinder(bm, radius=0.08, depth=0.1, segments=14)
        for v in head['verts']:
            old_z = v.co.z
            v.co.z = 0.68 + v.co.y
            v.co.y = -0.32 + old_z
            v.co.x += fx
        assign_mat(bm, head, 2)
    ant = create_cylinder(bm, radius=0.015, depth=0.45, segments=8)
    for v in ant['verts']:
        v.co.z += 1.2
    bm.to_mesh(mesh_drone)
    bm.free()
    obj_drone.data.materials.append(MATS["Plas_Gunmetal"])
    obj_drone.data.materials.append(MATS["Mech_DarkIron"])
    obj_drone.data.materials.append(MATS["Plas_Headlight"])
    add_bevel(obj_drone, width=0.008)
    finalize_asset(obj_drone, col, (ox + 1.2, oy - 1.0, oz + 0.4), rotation=(0, 0, -25))

    return col

# ==============================================================================
# 4. KIT COMPONENTES MODULARES DE ENEMIGOS Y MECÁNICA (REUTILIZABLES)
# ==============================================================================
def build_kit_enemy_parts(parent_col, base_origin=(12.0, 0.0, 0.25)):
    col = create_collection("Kit_04_Enemy_Components", parent_col)
    ox, oy, oz = base_origin

    # 1. Cilindro y Vástago de Pistón Hidráulico Cromado (Fondo Izquierda)
    mesh_pist = bpy.data.meshes.new("SM_Part_Hydraulic_Piston_Mesh")
    obj_pist = bpy.data.objects.new("SM_Part_Hydraulic_Piston", mesh_pist)
    bm = bmesh.new()
    barrel = create_cylinder(bm, radius=0.14, depth=0.75, segments=20)
    for v in barrel['verts']:
        v.co.z += 0.375
    # Anillos amarillos (Slot 2)
    for rz in [0.2, 0.4, 0.6]:
        ring = create_cylinder(bm, radius=0.16, depth=0.05, segments=20)
        for v in ring['verts']:
            v.co.z += rz
        assign_mat(bm, ring, 2)
    # Vástago cromado (Slot 1)
    rod = create_cylinder(bm, radius=0.075, depth=0.65, segments=20)
    for v in rod['verts']:
        v.co.z += 0.75 + 0.325
    assign_mat(bm, rod, 1)
    clev = bmesh.ops.create_cube(bm, size=1.0)
    for v in clev['verts']:
        v.co.x *= 0.18
        v.co.y *= 0.14
        v.co.z = 1.45 + (v.co.z + 0.5) * 0.16
    bm.to_mesh(mesh_pist)
    bm.free()
    obj_pist.data.materials.append(MATS["Mech_DarkIron"])
    obj_pist.data.materials.append(MATS["Mech_Chrome"])
    obj_pist.data.materials.append(MATS["Ind_Yellow"])
    add_bevel(obj_pist, width=0.008)
    finalize_asset(obj_pist, col, (ox - 2.0, oy + 1.1, oz))

    # 2. Chimenea de Escape Industrial Acodada (Fondo Centro-Izq)
    mesh_chm = bpy.data.meshes.new("SM_Part_Exhaust_Chimney_Mesh")
    obj_chm = bpy.data.objects.new("SM_Part_Exhaust_Chimney", mesh_chm)
    bm = bmesh.new()
    stack = create_cylinder(bm, radius=0.18, depth=1.3, segments=20)
    for v in stack['verts']:
        v.co.z += 0.65
    elbow = create_cylinder(bm, radius=0.18, depth=0.5, segments=20)
    for v in elbow['verts']:
        old_x = v.co.x
        old_z = v.co.z
        v.co.x = old_x * 0.707 - old_z * 0.707 + 0.28
        v.co.z = old_x * 0.707 + old_z * 0.707 + 1.45
    for cz in [0.4, 0.95]:
        clamp = create_cylinder(bm, radius=0.22, depth=0.06, segments=20)
        for v in clamp['verts']:
            v.co.z += cz
    bm.to_mesh(mesh_chm)
    bm.free()
    obj_chm.data.materials.append(MATS["Ind_Steel"])
    add_bevel(obj_chm, width=0.008)
    finalize_asset(obj_chm, col, (ox - 0.7, oy + 1.1, oz))

    # 3. Garra Curva de Titanio Reutilizable (Fondo Centro-Der)
    mesh_claw = bpy.data.meshes.new("SM_Part_BeastClaw_Reinforced_Mesh")
    obj_claw = bpy.data.objects.new("SM_Part_BeastClaw_Reinforced", mesh_claw)
    bm = bmesh.new()
    # Base apernada cilíndrica de anclaje (Slot 1: Mech_DarkIron)
    mount = create_cylinder(bm, radius=0.22, depth=0.18, segments=18)
    for v in mount['verts']:
        v.co.z += 0.09
    assign_mat(bm, mount, 1)
    # Rótula de articulación
    joint = bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=12, radius=0.2)
    for v in joint['verts']:
        v.co.z += 0.24
    assign_mat(bm, joint, 1)
    # Garra curva orgánica segmentada (Slot 0: Mech_Chrome)
    num_pts = 12
    prev_center = Vector((0.0, 0.0, 0.32))
    for i in range(num_pts):
        t = (i + 1) / float(num_pts)
        r = 0.18 * (1.0 - t * 0.9) + 0.012
        curr_y = -math.sin(t * math.pi * 0.55) * 0.55
        curr_z = 0.32 + math.sin(t * math.pi * 0.6) * 0.55 - (t ** 2) * 0.45
        curr_center = Vector((0.0, curr_y, curr_z))
        seg = create_cylinder(bm, radius=r, depth=(curr_center - prev_center).length + 0.02, segments=12)
        dir_v = (curr_center - prev_center).normalized()
        rot_q = dir_v.to_track_quat('Z', 'Y')
        mid = (prev_center + curr_center) * 0.5
        for v in seg['verts']:
            v.co = rot_q @ v.co + mid
        prev_center = curr_center
    bm.to_mesh(mesh_claw)
    bm.free()
    obj_claw.data.materials.append(MATS["Mech_Chrome"])
    obj_claw.data.materials.append(MATS["Mech_DarkIron"])
    add_bevel(obj_claw, width=0.008)
    finalize_asset(obj_claw, col, (ox + 0.6, oy + 1.1, oz), rotation=(0, 0, 25))

    # 4. Disco de Sierra Circular Industrial Dentado (Fondo Derecha)
    mesh_saw = bpy.data.meshes.new("SM_Part_Industrial_Sawblade_Mesh")
    obj_saw = bpy.data.objects.new("SM_Part_Industrial_Sawblade", mesh_saw)
    bm = bmesh.new()
    disc = create_cylinder(bm, radius=0.62, depth=0.04, segments=32)
    for v in disc['verts']:
        old_y = v.co.y
        v.co.y = v.co.z
        v.co.z = old_y + 0.75
    num_teeth = 20
    for i in range(num_teeth):
        rad = math.radians(i * (360 / num_teeth))
        tx = math.cos(rad) * 0.66
        tz = math.sin(rad) * 0.66 + 0.75
        tooth = bmesh.ops.create_cone(bm, cap_ends=True, radius1=0.09, radius2=0.005, depth=0.18, segments=4)
        for v in tooth['verts']:
            v.co.x += tx
            v.co.y = v.co.z
            v.co.z = tz
        assign_mat(bm, tooth, 1)
    hub = create_cylinder(bm, radius=0.22, depth=0.09, segments=16)
    for v in hub['verts']:
        old_y = v.co.y
        v.co.y = v.co.z
        v.co.z = old_y + 0.75
    assign_mat(bm, hub, 2)
    bm.to_mesh(mesh_saw)
    bm.free()
    obj_saw.data.materials.append(MATS["Ind_Steel"])
    obj_saw.data.materials.append(MATS["Mech_Chrome"])
    obj_saw.data.materials.append(MATS["Mech_DarkIron"])
    add_bevel(obj_saw, width=0.006)
    finalize_asset(obj_saw, col, (ox + 1.9, oy + 1.1, oz), rotation=(0, 15, -28))

    # 5. Rótula Mecánica Esférica (Frente Izquierda)
    mesh_bj = bpy.data.meshes.new("SM_Part_Mechanical_BallJoint_Mesh")
    obj_bj = bpy.data.objects.new("SM_Part_Mechanical_BallJoint", mesh_bj)
    bm = bmesh.new()
    sph = bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=16, radius=0.26)
    for v in sph['verts']:
        v.co.z += 0.35
    assign_mat(bm, sph, 1)
    case = create_cylinder(bm, radius=0.32, depth=0.3, segments=20)
    for v in case['verts']:
        v.co.z += 0.35
    pin = create_cylinder(bm, radius=0.09, depth=0.45, segments=14)
    for v in pin['verts']:
        v.co.z += 0.65
    assign_mat(bm, pin, 1)
    bm.to_mesh(mesh_bj)
    bm.free()
    obj_bj.data.materials.append(MATS["Mech_DarkIron"])
    obj_bj.data.materials.append(MATS["Mech_Chrome"])
    add_bevel(obj_bj, width=0.008)
    finalize_asset(obj_bj, col, (ox - 1.8, oy - 0.7, oz))

    # 6. Manómetro Analógico de Precisión 3D (Carcasa de Latón + Esfera Blanca + Aguja Roja)
    mesh_gauge = bpy.data.meshes.new("SM_Part_AnalogGauge_Dial_3D_Mesh")
    obj_gauge = bpy.data.objects.new("SM_Part_AnalogGauge_Dial_3D", mesh_gauge)
    bm = bmesh.new()
    case = create_cylinder(bm, radius=0.32, depth=0.14, segments=24)
    for v in case['verts']:
        old_y = v.co.y
        old_z = v.co.z
        v.co.y = -old_z
        v.co.z = old_y + 0.45
    bezel = create_cylinder(bm, radius=0.34, depth=0.05, segments=24)
    for v in bezel['verts']:
        old_y = v.co.y
        old_z = v.co.z
        v.co.y = -old_z - 0.05
        v.co.z = old_y + 0.45
    fit = create_cylinder(bm, radius=0.07, depth=0.22, segments=12)
    for v in fit['verts']:
        v.co.z += 0.11
    # Esfera blanca del dial (Slot 1)
    face = create_cylinder(bm, radius=0.3, depth=0.02, segments=24)
    for v in face['verts']:
        old_y = v.co.y
        old_z = v.co.z
        v.co.y = -old_z - 0.06
        v.co.z = old_y + 0.45
    assign_mat(bm, face, 1)
    # Aguja roja biselada (Slot 2)
    ndl = bmesh.ops.create_cone(bm, cap_ends=True, radius1=0.025, radius2=0.004, depth=0.22, segments=4)
    for v in ndl['verts']:
        v.co.y = -0.09
        v.co.x += 0.06
        v.co.z += 0.45 + 0.08
    assign_mat(bm, ndl, 2)
    bm.to_mesh(mesh_gauge)
    bm.free()
    obj_gauge.data.materials.append(MATS["Deco_Brass_Gold"])
    obj_gauge.data.materials.append(MATS["Mech_Dial_Face"])
    obj_gauge.data.materials.append(MATS["Ind_Valve_Red"])
    finalize_asset(obj_gauge, col, (ox - 0.6, oy - 0.8, oz), rotation=(30, 0, -20))

    # 7. Conjunto de Llamas Estilizadas 2D de Cómic en Capas
    mesh_flame = bpy.data.meshes.new("SM_Part_ComicFlame_2D_Cluster_Mesh")
    obj_flame = bpy.data.objects.new("SM_Part_ComicFlame_2D_Cluster", mesh_flame)
    bm = bmesh.new()
    for fx, f_h in [(-0.18, 0.75), (0.0, 1.1), (0.2, 0.85)]:
        fl = bmesh.ops.create_cone(bm, cap_ends=True, radius1=0.22, radius2=0.015, depth=f_h, segments=5)
        for v in fl['verts']:
            v.co.x += fx
            v.co.y *= 0.12
            v.co.z += f_h * 0.5
    for fx, f_h in [(-0.08, 0.5), (0.0, 0.75), (0.1, 0.55)]:
        core = bmesh.ops.create_cone(bm, cap_ends=True, radius1=0.12, radius2=0.01, depth=f_h, segments=5)
        for v in core['verts']:
            v.co.x += fx
            v.co.y *= 0.08
            v.co.z += f_h * 0.5
        assign_mat(bm, core, 1)
    for sx, sz in [(-0.25, 0.9), (0.28, 1.05), (0.05, 1.3)]:
        sp = create_cylinder(bm, radius=0.035, depth=0.09, segments=4)
        for v in sp['verts']:
            v.co.x += sx
            v.co.y *= 0.1
            v.co.z += sz
        assign_mat(bm, sp, 1)
    bm.to_mesh(mesh_flame)
    bm.free()
    obj_flame.data.materials.append(MATS["Mech_Flame_Outer"])
    obj_flame.data.materials.append(MATS["Mech_Flame_Inner"])
    finalize_asset(obj_flame, col, (ox + 0.6, oy - 0.8, oz))

    # 8. Pod de Sensores Ópticos / Lente Monocular Emisiva Esmeralda
    mesh_pod = bpy.data.meshes.new("SM_Part_Sensor_OpticLens_Pod_Mesh")
    obj_pod = bpy.data.objects.new("SM_Part_Sensor_OpticLens_Pod", mesh_pod)
    bm = bmesh.new()
    housing = bmesh.ops.create_cube(bm, size=1.0)
    for v in housing['verts']:
        v.co.x *= 0.42
        v.co.y *= 0.32
        v.co.z = 0.4 + v.co.z * 0.35
    lens = create_cylinder(bm, radius=0.16, depth=0.09, segments=20)
    for v in lens['verts']:
        old_y = v.co.y
        v.co.y = v.co.z - 0.18
        v.co.z = 0.4 + old_y
    assign_mat(bm, lens, 1)
    bezel = create_cylinder(bm, radius=0.19, depth=0.05, segments=20)
    for v in bezel['verts']:
        old_y = v.co.y
        v.co.y = v.co.z - 0.16
        v.co.z = 0.4 + old_y
    assign_mat(bm, bezel, 2)
    for cy in [-0.08, 0.08]:
        wire = create_cylinder(bm, radius=0.025, depth=0.35, segments=10)
        for v in wire['verts']:
            v.co.x += cy
            v.co.y += 0.22
            v.co.z += 0.4
    bm.to_mesh(mesh_pod)
    bm.free()
    obj_pod.data.materials.append(MATS["Mech_DarkIron"])
    obj_pod.data.materials.append(MATS["Mech_Sensor_Emerald"])
    obj_pod.data.materials.append(MATS["Deco_Brass_Gold"])
    add_bevel(obj_pod, width=0.008)
    finalize_asset(obj_pod, col, (ox + 1.8, oy - 0.8, oz), rotation=(-15, 0, -20))

    return col

# ==============================================================================
# SALA DE EXHIBICIÓN Y PLATAFORMAS (SHOWCASE STUDIO)
# ==============================================================================
def build_showcase_studio(scene):
    col = create_collection("Showcase_Studio_Platforms")

    mesh_floor = bpy.data.meshes.new("Studio_Floor_Mesh")
    obj_floor = bpy.data.objects.new("Studio_Floor", mesh_floor)
    bm_f = bmesh.new()
    bmesh.ops.create_cube(bm_f, size=1.0)
    for v in bm_f.verts:
        v.co.x *= 48.0
        v.co.y *= 36.0
        v.co.z = (v.co.z - 0.5) * 0.2
    wall = bmesh.ops.create_cube(bm_f, size=1.0)
    for v in wall['verts']:
        v.co.x *= 48.0
        v.co.y = 12.0 + v.co.y * 1.0
        v.co.z = (v.co.z + 0.5) * 14.0
    bm_f.to_mesh(mesh_floor)
    bm_f.free()
    obj_floor.data.materials.append(MATS["Studio_Floor"])
    col.objects.link(obj_floor)

    platforms_data = [
        ("Pedestal_01_Industrial", (-12.0, 0.0, 0.0), MATS["Ind_Grate"], MATS["LED_Strip_Yellow"]),
        ("Pedestal_02_ArtDeco", (-4.0, 0.0, 0.0), MATS["Deco_Carpet"], MATS["LED_Strip_Gold"]),
        ("Pedestal_03_Plasma", (4.0, 0.0, 0.0), MATS["Plas_Gunmetal"], MATS["LED_Strip_Cyan"]),
        ("Pedestal_04_Enemies", (12.0, 0.0, 0.0), MATS["Ind_Steel"], MATS["LED_Strip_Orange"]),
    ]

    for p_name, p_pos, top_mat, led_mat in platforms_data:
        mesh_p = bpy.data.meshes.new(p_name + "_Mesh")
        obj_p = bpy.data.objects.new(p_name, mesh_p)
        bm_p = bmesh.new()
        b = bmesh.ops.create_cube(bm_p, size=1.0)
        for v in b['verts']:
            v.co.x *= 5.8
            v.co.y *= 4.8
            v.co.z = (v.co.z + 0.5) * 0.25
        led = bmesh.ops.create_cube(bm_p, size=1.0)
        for v in led['verts']:
            v.co.x *= 5.9
            v.co.y *= 4.9
            v.co.z = 0.04 + (v.co.z + 0.5) * 0.04
        bm_p.to_mesh(mesh_p)
        bm_p.free()
        obj_p.data.materials.append(MATS["Pedestal_Body"])
        obj_p.data.materials.append(top_mat)
        obj_p.data.materials.append(led_mat)
        add_bevel(obj_p, width=0.02)
        obj_p.location = Vector(p_pos)
        col.objects.link(obj_p)

    sun = bpy.data.lights.new(name="Studio_Key_Sun", type='SUN')
    sun.energy = 5.2
    sun.color = (1.0, 0.98, 0.92)
    sun_obj = bpy.data.objects.new("Studio_Key_Sun_Obj", sun)
    sun_obj.rotation_euler = Euler((R(48), R(15), R(-25)), 'XYZ')
    col.objects.link(sun_obj)

    fill = bpy.data.lights.new(name="Studio_Fill_Sun", type='SUN')
    fill.energy = 2.2
    fill.color = (0.75, 0.85, 1.0)
    fill_obj = bpy.data.objects.new("Studio_Fill_Sun_Obj", fill)
    fill_obj.rotation_euler = Euler((R(-60), R(-20), R(140)), 'XYZ')
    col.objects.link(fill_obj)

    spotlights = [
        ("Spot_Ind", (-12.0, -1.0, 6.0), (1.0, 0.9, 0.6), 2600),
        ("Spot_Deco", (-4.0, -0.8, 6.0), (1.0, 0.94, 0.8), 2400),
        ("Spot_Plas", (4.0, -1.0, 6.0), (0.45, 0.92, 1.0), 3000),
        ("Spot_Enem", (12.0, -0.8, 5.8), (1.0, 0.8, 0.5), 2600),
    ]
    for s_name, spos, scolor, spower in spotlights:
        sp = bpy.data.lights.new(name=s_name, type='POINT')
        sp.energy = spower
        sp.color = scolor
        sp_obj = bpy.data.objects.new(s_name + "_Obj", sp)
        sp_obj.location = Vector(spos)
        col.objects.link(sp_obj)

# ==============================================================================
# CÁMARAS CON TRACKING MATEMÁTICO LOOK-AT
# ==============================================================================
def create_targeted_camera(name, cam_pos, target_pos, lens=45.0):
    cam = bpy.data.cameras.new(name)
    cam.lens = lens
    cam_obj = bpy.data.objects.new(name + "_Obj", cam)
    cam_obj.location = Vector(cam_pos)
    
    direction = Vector(target_pos) - Vector(cam_pos)
    cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    
    bpy.context.scene.collection.objects.link(cam_obj)
    return cam_obj

def render_camera_view(scene, cam_obj, filename, res_x=1920, res_y=1080):
    scene.camera = cam_obj
    scene.render.resolution_x = res_x
    scene.render.resolution_y = res_y
    scene.render.resolution_percentage = 100
    filepath = os.path.join(RENDERS_DIR, filename)
    scene.render.filepath = filepath
    print(f"[RENDER] Procesando {filename} ({res_x}x{res_y})...")
    bpy.ops.render.render(write_still=True)
    print(f"[OK] Guardado en: {filepath}")
    
    artifact_path = os.path.join(ARTIFACT_DIR, filename)
    try:
        shutil.copy2(filepath, artifact_path)
    except Exception as e:
        print(f"Aviso copia artefacto: {e}")
    return filepath

# ==============================================================================
# ENSAMBLAJE DE LÁMINA MAESTRA / COMPOSITE SHOWCASE SHEET
# ==============================================================================
def create_master_composite_sheet():
    print("[POST-PROCESS] Ensamblando lámina de catálogo maestro...")
    pano_path = os.path.join(RENDERS_DIR, "Showcase_Catalogo_Modular_Panorama.png")
    ind_path = os.path.join(RENDERS_DIR, "Showcase_Modular_Kit_Industrial.png")
    deco_path = os.path.join(RENDERS_DIR, "Showcase_Modular_Kit_ArtDeco.png")
    plas_path = os.path.join(RENDERS_DIR, "Showcase_Modular_Kit_Plasma.png")
    enem_path = os.path.join(RENDERS_DIR, "Showcase_Modular_Kit_Enemigos_Mecanica.png")
    out_master = os.path.join(RENDERS_DIR, "Showcase_Catalogo_Activos_Modulares_Master.png")

    if not all(os.path.exists(p) for p in [pano_path, ind_path, deco_path, plas_path, enem_path]):
        print("[AVISO] Faltan renders para ensamblar la lámina maestra.")
        return

    canvas = Image.new("RGBA", (2560, 1440), (14, 15, 18, 255))
    draw = ImageDraw.Draw(canvas)

    img_pano = Image.open(pano_path).resize((2560, 780), Image.Resampling.LANCZOS)
    canvas.paste(img_pano, (0, 0))

    kits_imgs = [
        (ind_path, "01. KIT INDUSTRIAL Y ESTRUCTURAL", (240, 195, 25)),
        (deco_path, "02. KIT ART DÉCO Y MOBILIARIO", (245, 205, 85)),
        (plas_path, "03. KIT REFINERÍA DE PLASMA", (45, 225, 255)),
        (enem_path, "04. KIT COMPONENTES Y MECÁNICA", (255, 125, 30)),
    ]

    try:
        font_head = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 36)
        font_sub = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 22)
    except Exception:
        font_head = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    draw.rectangle([(0, 776), (2560, 840)], fill=(22, 24, 28, 255))
    draw.line([(0, 776), (2560, 776)], fill=(240, 195, 25, 255), width=4)
    draw.line([(0, 840), (2560, 840)], fill=(60, 65, 75, 255), width=2)
    draw.text((40, 788), "CATÁLOGO OFICIAL DE ACTIVOS 3D MODULARES & REUTILIZABLES", fill=(255, 255, 255, 255), font=font_head)
    draw.text((1700, 796), "ASTRA HAZARD // BLENDER 5.2 LTS // FREESTYLE & PBR", fill=(180, 185, 195, 255), font=font_sub)

    for i, (path, label, color) in enumerate(kits_imgs):
        cx = 15 + i * 635
        cy = 850
        img_thumb = Image.open(path).resize((625, 530), Image.Resampling.LANCZOS)
        canvas.paste(img_thumb, (cx, cy))
        draw.rectangle([(cx, cy), (cx + 625, cy + 530)], outline=color, width=3)
        draw.rectangle([(cx, cy), (cx + 625, cy + 38)], fill=(15, 16, 20, 230))
        draw.text((cx + 15, cy + 8), label, fill=color, font=font_sub)

    canvas.save(out_master)
    print(f"[MASTER OK] Lámina maestra guardada en: {out_master}")
    shutil.copy2(out_master, os.path.join(ARTIFACT_DIR, "Showcase_Catalogo_Activos_Modulares_Master.png"))

# ==============================================================================
# EJECUCIÓN PRINCIPAL
# ==============================================================================
def main():
    print("======================================================================")
    print("Generando Catálogo Maestro de Activos Modulares 3D - Astra Hazard")
    print("======================================================================")
    
    scene = reset_scene()
    root_col = scene.collection
    
    print("[1/6] Compilando Shaders PBR, Cel-Shading y Texturas Modulares...")
    build_materials()
    
    print("[2/6] Construyendo Sala de Exhibición y Pedestales...")
    build_showcase_studio(scene)
    
    print("[3/6] Construyendo los 4 Kits Modulares...")
    build_kit_industrial(root_col, (-12.0, 0.0, 0.25))
    build_kit_artdeco(root_col, (-4.0, 0.0, 0.25))
    build_kit_plasma(root_col, (4.0, 0.0, 0.25))
    build_kit_enemy_parts(root_col, (12.0, 0.0, 0.25))
    
    print(f"[4/6] Guardando Archivo Nativo Oficial: {BLEND_FILE}...")
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_FILE)
    print("[OK] Proyecto guardado con éxito.")
    
    print("[5/6] Renderizando Cámaras Focalizadas con Perspectiva 3/4...")
    # 1. Cámara Panorámica General (Todo el Showroom, encuadre amplio de las 4 islas)
    cam_pano = create_targeted_camera("Cam_Pano", (0.0, -18.5, 7.8), (0.0, 0.1, 1.2), lens=24.0)
    render_camera_view(scene, cam_pano, "Showcase_Catalogo_Modular_Panorama.png", res_x=2560, res_y=1440)
    
    # 2. Primer Plano 3/4: Kit Industrial & Carga
    cam_ind = create_targeted_camera("Cam_Industrial", (-14.0, -6.8, 4.4), (-12.0, 0.0, 1.1), lens=35.0)
    render_camera_view(scene, cam_ind, "Showcase_Modular_Kit_Industrial.png", res_x=1920, res_y=1080)
    
    # 3. Primer Plano 3/4: Kit Art Déco & Mobiliario
    cam_deco = create_targeted_camera("Cam_ArtDeco", (-5.6, -6.4, 4.2), (-4.0, 0.0, 1.2), lens=35.0)
    render_camera_view(scene, cam_deco, "Showcase_Modular_Kit_ArtDeco.png", res_x=1920, res_y=1080)
    
    # 4. Primer Plano 3/4: Kit Refinería de Plasma & Sci-Fi
    cam_plas = create_targeted_camera("Cam_Plasma", (2.2, -6.4, 4.2), (4.0, 0.0, 1.25), lens=35.0)
    render_camera_view(scene, cam_plas, "Showcase_Modular_Kit_Plasma.png", res_x=1920, res_y=1080)
    
    # 5. Primer Plano 3/4: Kit Componentes de Enemigos & Mecánica
    cam_enem = create_targeted_camera("Cam_Enemies", (10.2, -6.2, 4.0), (12.0, 0.0, 1.05), lens=35.0)
    render_camera_view(scene, cam_enem, "Showcase_Modular_Kit_Enemigos_Mecanica.png", res_x=1920, res_y=1080)
    
    print("[6/6] Ensamblando Lámina Maestra de Catálogo...")
    create_master_composite_sheet()
    
    print("======================================================================")
    print("¡Catálogo de Activos Modulares completado con éxito total!")
    print("======================================================================")

if __name__ == "__main__":
    main()

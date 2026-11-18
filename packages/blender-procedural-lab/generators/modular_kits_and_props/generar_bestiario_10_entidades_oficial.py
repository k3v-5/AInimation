# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Generador Maestro 3D - Bestiario de Entidades Hostiles (10 Entidades Biomecánicas 100% 3D)
# Estilo Estricto: Cartoon / Industrial PBR, Cel-Shading, Freestyle Comic Ink 2.6px y Articulaciones Mecánicas Explícitas

import bpy
import bmesh
import math
import os
import sys
import shutil
from mathutils import Vector, Euler
from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = r"F:\Dev\Game"
RENDERS_DIR = os.path.join(PROJECT_ROOT, "Art", "Renders")
ARTIFACT_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\b59ff04f-3c21-4ee5-94b0-8e8f899f8923"
BLEND_FILE = os.path.join(PROJECT_ROOT, "Art", "Blender", "Bestiario_10_Entidades_Oficial.blend")

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
    
    # Entorno de estudio industrial oscuro con alto contraste cómic
    world = bpy.data.worlds.new("World_Studio")
    scene.world = world
    world.use_nodes = True
    wnodes = world.node_tree.nodes
    wlinks = world.node_tree.links
    wnodes.clear()
    
    w_out = wnodes.new(type='ShaderNodeOutputWorld')
    w_bg = wnodes.new(type='ShaderNodeBackground')
    w_bg.inputs['Color'].default_value = (0.02, 0.025, 0.035, 1.0)
    w_bg.inputs['Strength'].default_value = 0.65
    wlinks.new(w_bg.outputs['Background'], w_out.inputs['Surface'])
    
    # Freestyle Comic Ink Grueso (2.6px) para estética de cómic industrial
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
    linestyle.color = (0.015, 0.015, 0.02)
    linestyle.thickness = 2.6
    ls.linestyle = linestyle
    
    return scene

def create_collection(name, parent=None):
    col = bpy.data.collections.new(name)
    if parent:
        parent.children.link(col)
    else:
        bpy.context.scene.collection.children.link(col)
    return col

# -------------------------------------------------------------------------
# SHADERS PBR CEL-SHADING ESTILIZADOS
# -------------------------------------------------------------------------
def create_materials():
    mats = {}
    
    def make_pbr(name, base_col, roughness=0.35, metallic=0.0, emissive_col=(0,0,0,1), emissive_str=0.0):
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()
        
        node_out = nodes.new(type='ShaderNodeOutputMaterial')
        node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        node_bsdf.inputs['Base Color'].default_value = base_col
        node_bsdf.inputs['Roughness'].default_value = roughness
        node_bsdf.inputs['Metallic'].default_value = metallic
        
        if 'Emission Color' in node_bsdf.inputs:
            node_bsdf.inputs['Emission Color'].default_value = emissive_col
            node_bsdf.inputs['Emission Strength'].default_value = emissive_str
            
        links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])
        return mat

    def make_hazard_stripes(name="Mat_Hazard_Stripes_Comic"):
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()
        
        node_out = nodes.new(type='ShaderNodeOutputMaterial')
        node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        node_ramp = nodes.new(type='ShaderNodeValToRGB')
        node_ramp.color_ramp.interpolation = 'CONSTANT'
        node_ramp.color_ramp.elements[0].position = 0.0
        node_ramp.color_ramp.elements[0].color = (0.98, 0.78, 0.02, 1.0)
        node_ramp.color_ramp.elements[1].position = 0.50
        node_ramp.color_ramp.elements[1].color = (0.07, 0.08, 0.10, 1.0)
        
        node_wave = nodes.new(type='ShaderNodeTexWave')
        node_wave.wave_type = 'BANDS'
        node_wave.bands_direction = 'DIAGONAL'
        node_wave.inputs['Scale'].default_value = 12.0
        
        node_coord = nodes.new(type='ShaderNodeTexCoord')
        links.new(node_coord.outputs['Object'], node_wave.inputs['Vector'])
        links.new(node_wave.outputs['Color'], node_ramp.inputs['Fac'])
        links.new(node_ramp.outputs['Color'], node_bsdf.inputs['Base Color'])
        links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])
        node_bsdf.inputs['Roughness'].default_value = 0.30
        node_bsdf.inputs['Metallic'].default_value = 0.20
        return mat

    def make_cone_laser(name, base_col=(1.0, 0.12, 0.08, 1.0)):
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()
        
        node_out = nodes.new(type='ShaderNodeOutputMaterial')
        node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        node_bsdf.inputs['Base Color'].default_value = (1.0, 0.15, 0.10, 0.35)
        node_bsdf.inputs['Roughness'].default_value = 0.15
        node_bsdf.inputs['Metallic'].default_value = 0.0
        if 'Alpha' in node_bsdf.inputs:
            node_bsdf.inputs['Alpha'].default_value = 0.35
        if 'Emission Color' in node_bsdf.inputs:
            node_bsdf.inputs['Emission Color'].default_value = (1.0, 0.12, 0.08, 1.0)
            node_bsdf.inputs['Emission Strength'].default_value = 1.6
        links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])
        if hasattr(mat, 'surface_render_method'):
            mat.surface_render_method = 'BLENDED'
        if hasattr(mat, 'blend_method'):
            try:
                mat.blend_method = 'BLEND'
            except Exception:
                pass
        return mat

    # Armaduras y Materiales Industriales
    mats['Armor_Gunmetal'] = make_pbr("Mat_Armor_Gunmetal", (0.22, 0.25, 0.30, 1.0), roughness=0.32, metallic=0.85)
    mats['Armor_Steel_Dark'] = make_pbr("Mat_Armor_Steel_Dark", (0.13, 0.15, 0.19, 1.0), roughness=0.28, metallic=0.92)
    mats['Armor_Greenish_Hull'] = make_pbr("Mat_Armor_Greenish_Hull", (0.20, 0.30, 0.24, 1.0), roughness=0.35, metallic=0.70)
    mats['Armor_Navy_Blue'] = make_pbr("Mat_Armor_Navy_Blue", (0.10, 0.20, 0.35, 1.0), roughness=0.30, metallic=0.70)
    mats['Armor_Bone_Pale'] = make_pbr("Mat_Armor_Bone_Pale", (0.85, 0.86, 0.82, 1.0), roughness=0.45, metallic=0.10)
    mats['Armor_Safety_Orange'] = make_pbr("Mat_Armor_Safety_Orange", (0.95, 0.40, 0.05, 1.0), roughness=0.32, metallic=0.20)
    mats['Machinery_Brass'] = make_pbr("Mat_Machinery_Brass", (0.94, 0.74, 0.18, 1.0), roughness=0.20, metallic=0.95)
    mats['Polished_Chrome'] = make_pbr("Mat_Polished_Chrome", (0.92, 0.94, 0.96, 1.0), roughness=0.08, metallic=0.98)
    mats['Hazard_Yellow'] = make_pbr("Mat_Hazard_Yellow", (0.98, 0.78, 0.02, 1.0), roughness=0.28, metallic=0.15)
    mats['Emergency_Red'] = make_pbr("Mat_Emergency_Red", (0.88, 0.10, 0.08, 1.0), roughness=0.25, metallic=0.15)
    mats['Rubber_Black'] = make_pbr("Mat_Rubber_Black", (0.06, 0.06, 0.08, 1.0), roughness=0.85, metallic=0.0)
    mats['Dial_White'] = make_pbr("Mat_Dial_White", (0.95, 0.95, 0.92, 1.0), roughness=0.20, metallic=0.0)

    # Shaders Emisivos Cartoon
    mats['Comic_Flame_Yellow'] = make_pbr("Mat_Comic_Flame_Yellow", (1.0, 0.95, 0.20, 1.0), roughness=0.10, metallic=0.0,
                                          emissive_col=(1.0, 0.95, 0.20, 1.0), emissive_str=4.5)
    mats['Comic_Flame_Orange'] = make_pbr("Mat_Comic_Flame_Orange", (1.0, 0.48, 0.05, 1.0), roughness=0.10, metallic=0.0,
                                          emissive_col=(1.0, 0.48, 0.05, 1.0), emissive_str=4.0)
    mats['Glow_Eye_Red'] = make_pbr("Mat_Glow_Eye_Red", (1.0, 0.08, 0.08, 1.0), roughness=0.08, metallic=0.0,
                                    emissive_col=(1.0, 0.08, 0.08, 1.0), emissive_str=3.5)
    mats['Glow_Eye_Yellow'] = make_pbr("Mat_Glow_Eye_Yellow", (1.0, 0.88, 0.10, 1.0), roughness=0.08, metallic=0.0,
                                       emissive_col=(1.0, 0.88, 0.10, 1.0), emissive_str=3.5)
    mats['Glow_Monocle_Gold'] = make_pbr("Mat_Glow_Monocle_Gold", (1.0, 0.84, 0.15, 1.0), roughness=0.10, metallic=0.4,
                                         emissive_col=(1.0, 0.86, 0.18, 1.0), emissive_str=3.5)
    mats['Glow_CRT_Green'] = make_pbr("Mat_Glow_CRT_Green", (0.08, 0.98, 0.28, 1.0), roughness=0.12, metallic=0.0,
                                      emissive_col=(0.10, 1.0, 0.32, 1.0), emissive_str=3.5)
    mats['Glow_Plasma_Cyan'] = make_pbr("Mat_Glow_Plasma_Cyan", (0.08, 0.88, 1.0, 1.0), roughness=0.08, metallic=0.0,
                                        emissive_col=(0.12, 0.92, 1.0, 1.0), emissive_str=4.2)
    mats['Molten_Magma_Seams'] = make_pbr("Mat_Molten_Magma_Seams", (1.0, 0.38, 0.03, 1.0), roughness=0.12, metallic=0.0,
                                          emissive_col=(1.0, 0.40, 0.04, 1.0), emissive_str=4.0)
    mats['Toxin_Neon_Green'] = make_pbr("Mat_Toxin_Neon_Green", (0.25, 1.0, 0.15, 1.0), roughness=0.10, metallic=0.0,
                                        emissive_col=(0.30, 1.0, 0.18, 1.0), emissive_str=3.8)
    
    mats['Hazard_Stripes'] = make_hazard_stripes()
    mats['Laser_Scanner_Cone_Red'] = make_cone_laser("Mat_Laser_Scanner_Cone_Red")

    # Entorno y pedestales
    mats['Studio_Floor'] = make_pbr("Mat_Studio_Floor", (0.03, 0.035, 0.042, 1.0), roughness=0.90, metallic=0.0)
    mats['Plinth_Dark'] = make_pbr("Mat_Plinth_Dark", (0.08, 0.09, 0.11, 1.0), roughness=0.40, metallic=0.60)
    mats['Plinth_Plaque'] = make_pbr("Mat_Plinth_Plaque", (0.92, 0.74, 0.25, 1.0), roughness=0.20, metallic=0.95)
    mats['Catwalk_Plate'] = make_pbr("Mat_Catwalk_Plate", (0.15, 0.16, 0.19, 1.0), roughness=0.50, metallic=0.80)
    mats['Furnace_Cast_Iron'] = make_pbr("Mat_Furnace_Cast_Iron", (0.11, 0.12, 0.14, 1.0), roughness=0.65, metallic=0.75)
    
    return mats

def create_mesh_object(name, collection, mesh_func, materials):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    mesh_func(bm)
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    
    if isinstance(materials, list):
        for m in materials:
            obj.data.materials.append(m)
    elif materials:
        obj.data.materials.append(materials)
        
    return obj

# -------------------------------------------------------------------------
# GEOMETRÍA PRIMITIVA Y AUXILIARES DE ARTICULACIÓN MECÁNICA
# -------------------------------------------------------------------------
def build_box(bm, center, size, rot=(0,0,0), mat_idx=0):
    geom = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector((size[0], size[1], size[2])), verts=geom['verts'])
    if rot != (0,0,0):
        euler = Euler(rot, 'XYZ')
        bmesh.ops.rotate(bm, matrix=euler.to_matrix().to_4x4(), verts=geom['verts'])
    bmesh.ops.translate(bm, vec=Vector(center), verts=geom['verts'])
    for elem in geom['verts']:
        for f in elem.link_faces:
            f.material_index = mat_idx
    return geom

def build_cylinder(bm, center, radius, depth, segments=16, rot=(0,0,0), mat_idx=0):
    geom = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments, radius1=radius, radius2=radius, depth=depth)
    if rot != (0,0,0):
        euler = Euler(rot, 'XYZ')
        bmesh.ops.rotate(bm, matrix=euler.to_matrix().to_4x4(), verts=geom['verts'])
    bmesh.ops.translate(bm, vec=Vector(center), verts=geom['verts'])
    for elem in geom['verts']:
        for f in elem.link_faces:
            f.material_index = mat_idx
    return geom

def build_sphere(bm, center, radius, segments=16, rings=12, rot=(0,0,0), mat_idx=0):
    geom = bmesh.ops.create_uvsphere(bm, u_segments=segments, v_segments=rings, radius=radius)
    if rot != (0,0,0):
        euler = Euler(rot, 'XYZ')
        bmesh.ops.rotate(bm, matrix=euler.to_matrix().to_4x4(), verts=geom['verts'])
    bmesh.ops.translate(bm, vec=Vector(center), verts=geom['verts'])
    for elem in geom['verts']:
        for f in elem.link_faces:
            f.material_index = mat_idx
    return geom

def build_cone(bm, center, radius1, depth, segments=16, rot=(0,0,0), mat_idx=0):
    geom = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segments, radius1=radius1, radius2=0.0, depth=depth)
    if rot != (0,0,0):
        euler = Euler(rot, 'XYZ')
        bmesh.ops.rotate(bm, matrix=euler.to_matrix().to_4x4(), verts=geom['verts'])
    bmesh.ops.translate(bm, vec=Vector(center), verts=geom['verts'])
    for elem in geom['verts']:
        for f in elem.link_faces:
            f.material_index = mat_idx
    return geom

# Articulación Mecánica Explícita: Rótula cilíndrica con pasador y doble vástago de pistón
def build_mechanical_joint_bm(bm, center, rot, hub_radius=0.10, hub_width=0.22, length=0.48, piston_radius=0.045,
                             mat_hub=0, mat_cyl=1, mat_rod=2, mat_pin=3):
    cx, cy, cz = center
    # Cubo central del pivote (Pivot Boss)
    build_cylinder(bm, (cx, cy, cz), hub_radius, hub_width, segments=16, rot=rot, mat_idx=mat_hub)
    # Pasador central con cabeza de perno (Pin)
    build_cylinder(bm, (cx, cy, cz), hub_radius * 0.45, hub_width * 1.25, segments=12, rot=rot, mat_idx=mat_pin)
    # Cilindro hidráulico exterior
    cyl_pos = (cx, cy, cz - length * 0.28)
    build_cylinder(bm, cyl_pos, piston_radius, length * 0.55, segments=14, rot=rot, mat_idx=mat_cyl)
    # Vástago cromado interior deslizante
    rod_pos = (cx, cy, cz + length * 0.28)
    build_cylinder(bm, rod_pos, piston_radius * 0.58, length * 0.55, segments=12, rot=rot, mat_idx=mat_rod)

# Rueda de engranaje dentado visible
def build_gear_cog_bm(bm, center, rot, radius=0.22, teeth=8, depth=0.06, mat_gear=0):
    cx, cy, cz = center
    build_cylinder(bm, (cx, cy, cz), radius * 0.82, depth, segments=18, rot=rot, mat_idx=mat_gear)
    for t in range(teeth):
        ang = t * (2.0 * math.pi / teeth)
        tx = cx + math.cos(ang) * radius * 0.88
        tz = cz + math.sin(ang) * radius * 0.88
        build_box(bm, (tx, cy, tz), (radius * 0.30, depth * 0.95, radius * 0.30), rot=(rot[0], -ang, rot[2]), mat_idx=mat_gear)

# Manómetro analógico de latón con aguja roja
def build_gauge_bm(bm, center, rot, radius=0.14, depth=0.08, mat_brass=0, mat_face=1, mat_needle=2):
    cx, cy, cz = center
    build_cylinder(bm, (cx, cy, cz), radius, depth, segments=16, rot=rot, mat_idx=mat_brass)
    build_cylinder(bm, (cx, cy - depth * 0.45, cz), radius * 0.82, 0.02, segments=16, rot=rot, mat_idx=mat_face)
    build_cone(bm, (cx, cy - depth * 0.52, cz + radius * 0.25), radius * 0.16, radius * 0.65, segments=4, rot=(rot[0], rot[1], rot[2] + R(45)), mat_idx=mat_needle)


# # -------------------------------------------------------------------------
# CONSTRUCCIÓN DE LAS 10 ENTIDADES BIOMECÁNICAS (CARTOON / INDUSTRIAL)
# -------------------------------------------------------------------------

def add_bevel_modifier(obj, width=0.035, segments=2):
    bev = obj.modifiers.new("Bevel", 'BEVEL')
    bev.width = width
    bev.segments = segments
    bev.limit_method = 'ANGLE'
    bev.angle_limit = math.radians(45.0)

# 01. MECHANICAL WEREWOLF (Lobo Biomecánico Industrial)
# Fila 1 - X = -8.0, Y = -0.4, Z = 0.0
def build_entity1_werewolf(col, mats):
    X0 = -8.0; Y0 = -0.4; Z0 = 0.0
    def geom(bm):
        # Pasarela con barandilla industrial
        build_box(bm, (X0, Y0, Z0 + 0.30), (2.8, 1.4, 0.16), mat_idx=0)
        build_box(bm, (X0, Y0 - 0.65, Z0 + 0.30), (2.8, 0.06, 0.14), mat_idx=1) # Hazard trim
        build_cylinder(bm, (X0, Y0 - 0.65, Z0 + 0.72), 0.025, 2.7, rot=(0, R(90), 0), mat_idx=2)
        for bx in [-1.0, 0.0, 1.0]:
            build_cylinder(bm, (X0 + bx, Y0 - 0.65, Z0 + 0.52), 0.022, 0.40, mat_idx=2)
            
        # Torso lupino acorazado masivo
        build_box(bm, (X0 - 0.20, Y0, Z0 + 1.30), (0.95, 0.72, 0.68), rot=(0, R(20), 0), mat_idx=3)
        build_box(bm, (X0 + 0.32, Y0, Z0 + 1.42), (0.76, 0.64, 0.56), rot=(0, R(-15), 0), mat_idx=3)
        # Placas de hombrera con franja de peligro
        build_box(bm, (X0 - 0.32, Y0 - 0.34, Z0 + 1.25), (0.72, 0.08, 0.46), rot=(0, R(20), 0), mat_idx=1)
        build_box(bm, (X0 - 0.32, Y0 + 0.34, Z0 + 1.25), (0.72, 0.08, 0.46), rot=(0, R(20), 0), mat_idx=1)
        
        # Cabeza y fauces mecánicas
        build_box(bm, (X0 - 0.90, Y0, Z0 + 1.52), (0.48, 0.44, 0.40), rot=(0, R(12), 0), mat_idx=3)
        build_cone(bm, (X0 - 0.85, Y0 - 0.18, Z0 + 1.80), 0.06, 0.26, rot=(R(-15), R(-15), 0), mat_idx=9)
        build_cone(bm, (X0 - 0.85, Y0 + 0.18, Z0 + 1.80), 0.06, 0.26, rot=(R(15), R(-15), 0), mat_idx=9)
        build_box(bm, (X0 - 1.25, Y0, Z0 + 1.48), (0.54, 0.28, 0.22), rot=(0, R(18), 0), mat_idx=3)
        build_box(bm, (X0 - 1.20, Y0, Z0 + 1.28), (0.48, 0.24, 0.16), rot=(0, R(-18), 0), mat_idx=4)
        
        # Colmillos de tungsteno
        for tz in [-0.09, 0.09]:
            build_cone(bm, (X0 - 1.42, Y0 + tz, Z0 + 1.40), 0.03, 0.10, rot=(R(180), 0, 0), mat_idx=5)
            build_cone(bm, (X0 - 1.38, Y0 + tz, Z0 + 1.32), 0.025, 0.08, rot=(0, 0, 0), mat_idx=5)
        
        # Ojos amarillos y núcleo incandescente
        build_box(bm, (X0 - 1.05, Y0 - 0.20, Z0 + 1.62), (0.16, 0.03, 0.08), rot=(0, R(30), R(15)), mat_idx=6)
        build_box(bm, (X0 - 1.05, Y0 + 0.20, Z0 + 1.62), (0.16, 0.03, 0.08), rot=(0, R(30), R(-15)), mat_idx=6)
        build_box(bm, (X0 - 1.26, Y0, Z0 + 1.36), (0.24, 0.14, 0.12), mat_idx=7)
        
        # 3 Tubos de escape dorsales con llamas cómic 2D facetadas
        for ex, ey, ez in [(-0.15, -0.22, 1.68), (0.08, 0.00, 1.76), (-0.15, 0.22, 1.68)]:
            build_cylinder(bm, (X0 + ex, Y0 + ey, Z0 + ez), 0.09, 0.58, segments=16, rot=(0, R(-42), 0), mat_idx=3)
            build_cylinder(bm, (X0 + ex + 0.22, Y0 + ey, Z0 + ez + 0.22), 0.105, 0.07, segments=16, rot=(0, R(-42), 0), mat_idx=5)
            
            flame_tip_x = X0 + ex + 0.52
            flame_tip_z = Z0 + ez + 0.50
            f_geom = bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=0.32, radius2=0.0, depth=0.90)
            bmesh.ops.scale(bm, vec=Vector((1.0, 0.22, 1.0)), verts=f_geom['verts'])
            bmesh.ops.rotate(bm, matrix=Euler((0, R(-42), 0), 'XYZ').to_matrix().to_4x4(), verts=f_geom['verts'])
            bmesh.ops.translate(bm, vec=Vector((flame_tip_x, Y0 + ey, flame_tip_z)), verts=f_geom['verts'])
            for elem in f_geom['verts']:
                for f in elem.link_faces:
                    f.material_index = 8
                    
            fi_geom = bmesh.ops.create_cone(bm, cap_ends=True, segments=4, radius1=0.19, radius2=0.0, depth=0.58)
            bmesh.ops.scale(bm, vec=Vector((1.0, 0.20, 1.0)), verts=fi_geom['verts'])
            bmesh.ops.rotate(bm, matrix=Euler((0, R(-42), 0), 'XYZ').to_matrix().to_4x4(), verts=fi_geom['verts'])
            bmesh.ops.translate(bm, vec=Vector((flame_tip_x - 0.12, Y0 + ey, flame_tip_z - 0.12)), verts=fi_geom['verts'])
            for elem in fi_geom['verts']:
                for f in elem.link_faces:
                    f.material_index = 7

        # Extremidades con articulaciones de pistón y garras
        for py in [-0.38, 0.38]:
            build_sphere(bm, (X0 - 0.35, Y0 + py, Z0 + 1.15), 0.15, segments=14, rings=10, mat_idx=4)
            build_cylinder(bm, (X0 - 0.48, Y0 + py, Z0 + 1.02), 0.08, 0.48, rot=(0, R(28), 0), mat_idx=9)
            build_mechanical_joint_bm(bm, (X0 - 0.62, Y0 + py, Z0 + 0.85), rot=(0, R(90), 0), length=0.40, piston_radius=0.045,
                                      mat_hub=4, mat_cyl=9, mat_rod=5, mat_pin=4)
            build_cylinder(bm, (X0 - 0.72, Y0 + py, Z0 + 0.66), 0.065, 0.48, rot=(0, R(-15), 0), mat_idx=4)
            build_box(bm, (X0 - 0.82, Y0 + py, Z0 + 0.46), (0.24, 0.18, 0.08), mat_idx=4)
            for gx in [-0.06, -0.02, 0.02, 0.06]:
                build_cone(bm, (X0 - 0.96, Y0 + py + gx, Z0 + 0.46), 0.025, 0.14, rot=(0, R(95), 0), mat_idx=5)
                
        for py in [-0.40, 0.40]:
            build_sphere(bm, (X0 + 0.45, Y0 + py, Z0 + 1.25), 0.16, segments=14, rings=10, mat_idx=4)
            build_cylinder(bm, (X0 + 0.58, Y0 + py, Z0 + 1.10), 0.10, 0.52, rot=(0, R(-35), 0), mat_idx=9)
            build_mechanical_joint_bm(bm, (X0 + 0.68, Y0 + py, Z0 + 0.85), rot=(0, R(90), 0), length=0.45, piston_radius=0.05,
                                      mat_hub=4, mat_cyl=9, mat_rod=5, mat_pin=4)
            build_cylinder(bm, (X0 + 0.56, Y0 + py, Z0 + 0.62), 0.07, 0.55, rot=(0, R(42), 0), mat_idx=4)
            build_box(bm, (X0 + 0.68, Y0 + py, Z0 + 0.44), (0.28, 0.20, 0.08), mat_idx=3)
            for tx in [-0.06, 0.0, 0.06]:
                build_cone(bm, (X0 + 0.82, Y0 + py + tx, Z0 + 0.44), 0.025, 0.12, rot=(0, R(90), 0), mat_idx=5)

    mat_list = [
        mats['Catwalk_Plate'], mats['Hazard_Stripes'], mats['Armor_Steel_Dark'],
        mats['Armor_Steel_Dark'], mats['Armor_Gunmetal'], mats['Polished_Chrome'],
        mats['Glow_Eye_Yellow'], mats['Comic_Flame_Orange'], mats['Comic_Flame_Yellow'],
        mats['Hazard_Yellow']
    ]
    obj = create_mesh_object("SM_Bestiary_01_Werewolf", col, geom, mat_list)
    add_bevel_modifier(obj, width=0.03)
    return obj


# 02. AUDITOR DRONE (Dron Auditor O.S.H.A.)
# Fila 1 - X = -4.0, Y = -0.4, Z = 0.0
def build_entity2_drone(col, mats):
    X0 = -4.0; Y0 = -0.4; Z0 = 0.0
    def geom(bm):
        # Esfera acorazada verde oliva
        build_sphere(bm, (X0, Y0, Z0 + 1.35), 0.62, segments=24, rings=18, mat_idx=0)
        build_cylinder(bm, (X0, Y0, Z0 + 1.35), 0.645, 0.06, segments=24, mat_idx=1)
        for r_ang in range(12):
            ang = r_ang * (2.0 * math.pi / 12)
            build_sphere(bm, (X0 + math.cos(ang)*0.64, Y0 + math.sin(ang)*0.64, Z0 + 1.35), 0.02, segments=8, rings=6, mat_idx=2)
            
        # Trío de manómetros analógicos de latón en la coronilla
        for gx, gy, gz, gr in [(-0.20, -0.22, 1.84, R(-22)), (0.00, -0.28, 1.88, R(0)), (0.20, -0.22, 1.84, R(22))]:
            build_gauge_bm(bm, (X0 + gx, Y0 + gy, Z0 + gz), rot=(R(30), 0, gr), radius=0.10, depth=0.06,
                           mat_brass=1, mat_face=3, mat_needle=4)

        # Antenas de comunicación
        build_cylinder(bm, (X0 - 0.22, Y0 + 0.12, Z0 + 1.98), 0.018, 0.50, rot=(R(-15), R(-20), 0), mat_idx=5)
        build_cylinder(bm, (X0 + 0.22, Y0 + 0.12, Z0 + 1.98), 0.018, 0.50, rot=(R(-15), R(20), 0), mat_idx=5)
        build_cylinder(bm, (X0 - 0.22, Y0 + 0.12, Z0 + 1.85), 0.035, 0.10, rot=(R(-15), R(-20), 0), mat_idx=1)
        build_cylinder(bm, (X0 + 0.22, Y0 + 0.12, Z0 + 1.85), 0.035, 0.10, rot=(R(-15), R(20), 0), mat_idx=1)

        # Monitor CRT lateral verde fósforo
        build_box(bm, (X0 - 0.52, Y0 - 0.26, Z0 + 1.35), (0.28, 0.12, 0.28), rot=(R(10), R(-25), 0), mat_idx=5)
        build_box(bm, (X0 - 0.53, Y0 - 0.32, Z0 + 1.35), (0.24, 0.02, 0.24), rot=(R(10), R(-25), 0), mat_idx=6)
        build_cylinder(bm, (X0 - 0.38, Y0 - 0.15, Z0 + 1.35), 0.03, 0.22, rot=(0, R(90), 0), mat_idx=1)

        # Lente telescópica central y haz de escaneo cónico
        build_cylinder(bm, (X0 + 0.14, Y0 - 0.52, Z0 + 1.30), 0.26, 0.12, segments=24, rot=(R(85), 0, 0), mat_idx=1)
        build_cylinder(bm, (X0 + 0.14, Y0 - 0.58, Z0 + 1.30), 0.20, 0.05, segments=20, rot=(R(85), 0, 0), mat_idx=7)
        build_cylinder(bm, (X0 + 0.14, Y0 - 0.61, Z0 + 1.30), 0.15, 0.04, segments=20, rot=(R(85), 0, 0), mat_idx=4)
        build_sphere(bm, (X0 + 0.14, Y0 - 0.62, Z0 + 1.30), 0.06, segments=12, rings=8, mat_idx=7)
        build_cone(bm, (X0 + 0.16, Y0 - 1.05, Z0 + 0.65), 0.52, 1.35, segments=20, rot=(R(115), 0, 0), mat_idx=8)

        # Propulsores vectoriales laterales
        for tx, trot in [(-0.58, R(-90)), (0.58, R(90))]:
            build_cylinder(bm, (X0 + tx, Y0, Z0 + 1.35), 0.14, 0.22, segments=16, rot=(0, trot, 0), mat_idx=5)
            build_cylinder(bm, (X0 + tx * 1.15, Y0, Z0 + 1.35), 0.15, 0.06, segments=16, rot=(0, trot, 0), mat_idx=1)
            build_sphere(bm, (X0 + tx * 1.18, Y0, Z0 + 1.35), 0.08, segments=12, rings=8, mat_idx=9)
        build_cylinder(bm, (X0, Y0, Z0 + 0.70), 0.03, 0.28, segments=8, mat_idx=1)

    mat_list = [
        mats['Armor_Greenish_Hull'], mats['Machinery_Brass'], mats['Polished_Chrome'],
        mats['Dial_White'], mats['Glow_Eye_Red'], mats['Armor_Gunmetal'],
        mats['Glow_CRT_Green'], mats['Glow_Monocle_Gold'], mats['Laser_Scanner_Cone_Red'],
        mats['Glow_Plasma_Cyan']
    ]
    obj = create_mesh_object("SM_Bestiary_02_Drone", col, geom, mat_list)
    add_bevel_modifier(obj, width=0.025)
    return obj


# 03. SCRAPPER GOBLIN (Trasgo Chatarrero)
# Fila 1 - X = 0.0, Y = -0.4, Z = 0.0 (Centro Escenario)
def build_entity3_scrapper(col, mats):
    X0 = 0.0; Y0 = -0.4; Z0 = 0.0
    def geom(bm):
        # Torso acorazado de chapa remachada
        build_box(bm, (X0, Y0, Z0 + 1.10), (0.64, 0.44, 0.68), mat_idx=0)
        build_box(bm, (X0, Y0 - 0.22, Z0 + 1.18), (0.54, 0.06, 0.35), mat_idx=1)
        build_box(bm, (X0, Y0, Z0 + 0.82), (0.68, 0.46, 0.14), mat_idx=0)
        # Rueda dentada central como hebilla de cinturón
        build_gear_cog_bm(bm, (X0, Y0 - 0.24, Z0 + 0.82), rot=(R(90), 0, 0), radius=0.22, teeth=8, depth=0.07, mat_gear=2)

        # Cabeza con máscara ósea y cuernos metálicos
        build_box(bm, (X0, Y0, Z0 + 1.70), (0.46, 0.42, 0.45), mat_idx=3)
        build_cylinder(bm, (X0 - 0.16, Y0, Z0 + 2.02), 0.045, 0.28, segments=12, rot=(0, R(-28), 0), mat_idx=0)
        build_cylinder(bm, (X0 + 0.16, Y0, Z0 + 2.02), 0.045, 0.28, segments=12, rot=(0, R(28), 0), mat_idx=0)
        build_cylinder(bm, (X0, Y0, Z0 + 2.06), 0.038, 0.32, segments=12, mat_idx=0)

        # Monóculo telescópico gigante de latón
        build_box(bm, (X0 - 0.12, Y0 - 0.21, Z0 + 1.70), (0.10, 0.04, 0.08), mat_idx=0)
        build_sphere(bm, (X0 - 0.12, Y0 - 0.23, Z0 + 1.70), 0.035, segments=8, rings=6, mat_idx=4)
        build_cylinder(bm, (X0 + 0.15, Y0 - 0.24, Z0 + 1.71), 0.15, 0.12, segments=20, rot=(R(90), 0, 0), mat_idx=2)
        build_cylinder(bm, (X0 + 0.15, Y0 - 0.30, Z0 + 1.71), 0.12, 0.04, segments=16, rot=(R(90), 0, 0), mat_idx=5)
        for tx in [-0.09, -0.03, 0.03, 0.09]:
            build_box(bm, (X0 + tx, Y0 - 0.21, Z0 + 1.52), (0.04, 0.03, 0.08), mat_idx=3)

        # Brazo derecho con mangual de púas
        build_gear_cog_bm(bm, (X0 - 0.38, Y0, Z0 + 1.25), rot=(0, R(90), 0), radius=0.14, teeth=6, depth=0.06, mat_gear=2)
        build_cylinder(bm, (X0 - 0.46, Y0 - 0.12, Z0 + 1.10), 0.065, 0.42, rot=(R(-35), 0, 0), mat_idx=0)
        build_mechanical_joint_bm(bm, (X0 - 0.55, Y0 - 0.28, Z0 + 0.95), rot=(R(90), 0, 0), length=0.35, piston_radius=0.035,
                                  mat_hub=0, mat_cyl=0, mat_rod=6, mat_pin=7)
        build_cylinder(bm, (X0 - 0.65, Y0 - 0.42, Z0 + 1.18), 0.03, 0.90, rot=(R(-30), R(15), 0), mat_idx=0)
        build_sphere(bm, (X0 - 0.74, Y0 - 0.62, Z0 + 1.50), 0.14, segments=16, rings=12, mat_idx=0)
        for pa in [0, 60, 120, 180, 240, 300]:
            rad = R(pa)
            build_cone(bm, (X0 - 0.74 + 0.18*math.cos(rad), Y0 - 0.62, Z0 + 1.50 + 0.18*math.sin(rad)), 0.04, 0.14, rot=(0, -rad, 0), mat_idx=2)

        # Brazo izquierdo con sierra circular motorizada
        build_gear_cog_bm(bm, (X0 + 0.38, Y0, Z0 + 1.25), rot=(0, R(90), 0), radius=0.14, teeth=6, depth=0.06, mat_gear=2)
        build_cylinder(bm, (X0 + 0.50, Y0 - 0.12, Z0 + 1.05), 0.065, 0.42, rot=(R(25), 0, 0), mat_idx=0)
        build_cylinder(bm, (X0 + 0.62, Y0 - 0.28, Z0 + 0.90), 0.26, 0.025, segments=24, rot=(0, R(90), 0), mat_idx=6)
        for sa in range(12):
            srad = R(sa * 30)
            build_box(bm, (X0 + 0.62, Y0 - 0.28 + 0.27*math.cos(srad), Z0 + 0.90 + 0.27*math.sin(srad)), (0.03, 0.04, 0.04), mat_idx=6)
        build_box(bm, (X0 + 0.62, Y0 - 0.28, Z0 + 1.08), (0.08, 0.32, 0.12), mat_idx=7)

        # Piernas con pistones y articulaciones mecánicas
        for ly in [-0.20, 0.20]:
            build_cylinder(bm, (X0 + ly, Y0, Z0 + 0.58), 0.075, 0.46, mat_idx=0)
            build_mechanical_joint_bm(bm, (X0 + ly, Y0, Z0 + 0.38), rot=(0, R(90), 0), length=0.38, piston_radius=0.04,
                                      mat_hub=0, mat_cyl=0, mat_rod=6, mat_pin=7)
            build_box(bm, (X0 + ly, Y0 - 0.08, Z0 + 0.38), (0.14, 0.12, 0.14), mat_idx=2)
            build_cylinder(bm, (X0 + ly, Y0, Z0 + 0.20), 0.065, 0.38, mat_idx=0)
            build_box(bm, (X0 + ly, Y0 - 0.08, Z0 + 0.06), (0.16, 0.26, 0.12), mat_idx=0)

    mat_list = [
        mats['Armor_Gunmetal'], mats['Armor_Steel_Dark'], mats['Machinery_Brass'],
        mats['Armor_Bone_Pale'], mats['Glow_Eye_Red'], mats['Glow_Monocle_Gold'],
        mats['Polished_Chrome'], mats['Hazard_Yellow']
    ]
    obj = create_mesh_object("SM_Bestiary_03_Scrapper", col, geom, mat_list)
    add_bevel_modifier(obj, width=0.03)
    return obj


# 04. CEILING SPIDER-BOT (Araña Centinela de Techo)
# Fila 1 - X = 4.0, Y = -0.4, Z = 0.0
def build_entity4_spider(col, mats):
    X0 = 4.0; Y0 = -0.4; Z0 = 0.0
    def geom(bm):
        # Viga de techo con riel de grúa
        build_box(bm, (X0, Y0, Z0 + 2.15), (2.8, 0.35, 0.25), mat_idx=0)
        build_box(bm, (X0, Y0, Z0 + 2.28), (2.8, 0.50, 0.05), mat_idx=1)
        build_box(bm, (X0, Y0, Z0 + 2.02), (2.8, 0.50, 0.05), mat_idx=1)
        
        # Carro de grúa móvil fijado a la viga
        build_box(bm, (X0, Y0, Z0 + 1.95), (0.45, 0.45, 0.12), mat_idx=1)
        for wx in [-0.18, 0.18]:
            for wy in [-0.20, 0.20]:
                build_cylinder(bm, (X0 + wx, Y0 + wy, Z0 + 2.02), 0.06, 0.04, rot=(R(90), 0, 0), mat_idx=2)
        
        # Cable de suspensión y unión giratoria
        build_cylinder(bm, (X0, Y0, Z0 + 1.82), 0.045, 0.22, mat_idx=2)
        
        # Chasis central suspendido con armadura facetada y franja hazard
        build_box(bm, (X0, Y0, Z0 + 1.60), (0.68, 0.68, 0.32), mat_idx=0)
        build_box(bm, (X0, Y0, Z0 + 1.60), (0.72, 0.72, 0.10), mat_idx=5) # Franja hazard
        # Visor óptico esférico verde CRT centinela con marco de latón
        build_cylinder(bm, (X0, Y0 - 0.35, Z0 + 1.60), 0.16, 0.06, rot=(R(90), 0, 0), mat_idx=1)
        build_sphere(bm, (X0, Y0 - 0.38, Z0 + 1.60), 0.13, segments=16, rings=12, mat_idx=3)
        build_sphere(bm, (X0 - 0.18, Y0 - 0.35, Z0 + 1.66), 0.045, segments=8, rings=6, mat_idx=4)
        build_sphere(bm, (X0 + 0.18, Y0 - 0.35, Z0 + 1.66), 0.045, segments=8, rings=6, mat_idx=4)

        # 4 Patas robóticas articuladas 100% CONECTADAS y apoyadas en el pedestal
        leg_coords = [
            (-0.28, -0.28, -0.65, -0.65, -1.05, -1.05, 0.40),
            (-0.28,  0.28, -0.65,  0.65, -1.05,  1.05, 0.40),
            ( 0.28, -0.28,  0.65, -0.65,  1.05, -1.05, 0.40),
            ( 0.28,  0.28,  0.65,  0.65,  1.05,  1.05, 0.40)
        ]
        for hx, hy, kx, ky, fx, fy, fz in leg_coords:
            hip_pos = (X0 + hx, Y0 + hy, Z0 + 1.60)
            build_sphere(bm, hip_pos, 0.10, segments=12, rings=8, mat_idx=1) # Rótula de cadera
            
            # Muslo (Femur): desde cadera a rodilla
            knee_pos = (X0 + kx, Y0 + ky, Z0 + 1.82)
            mid_thigh = ((hip_pos[0] + knee_pos[0])*0.5, (hip_pos[1] + knee_pos[1])*0.5, (hip_pos[2] + knee_pos[2])*0.5)
            dx, dy, dz = knee_pos[0] - hip_pos[0], knee_pos[1] - hip_pos[1], knee_pos[2] - hip_pos[2]
            t_len = math.sqrt(dx*dx + dy*dy + dz*dz)
            yaw = math.atan2(dy, dx)
            pitch = math.atan2(math.sqrt(dx*dx + dy*dy), dz)
            build_cylinder(bm, mid_thigh, 0.065, t_len, rot=(0, pitch, yaw - math.pi/2), mat_idx=5)
            build_cylinder(bm, (mid_thigh[0], mid_thigh[1], mid_thigh[2] + 0.04), 0.035, t_len*0.7, rot=(0, pitch, yaw - math.pi/2), mat_idx=2)
            
            # Rodilla: bisagra con pasador cromado
            build_sphere(bm, knee_pos, 0.11, segments=14, rings=10, mat_idx=1)
            build_cylinder(bm, knee_pos, 0.06, 0.26, rot=(0, R(90), math.atan2(ky, kx)), mat_idx=2)
            
            # Pantorrilla (Tibia): desde rodilla hasta tobillo
            ankle_pos = (X0 + fx, Y0 + fy, Z0 + fz + 0.15)
            mid_shin = ((knee_pos[0] + ankle_pos[0])*0.5, (knee_pos[1] + ankle_pos[1])*0.5, (knee_pos[2] + ankle_pos[2])*0.5)
            sdx, sdy, sdz = ankle_pos[0] - knee_pos[0], ankle_pos[1] - knee_pos[1], ankle_pos[2] - knee_pos[2]
            s_len = math.sqrt(sdx*sdx + sdy*sdy + sdz*sdz)
            s_yaw = math.atan2(sdy, sdx)
            s_pitch = math.atan2(math.sqrt(sdx*sdx + sdy*sdy), sdz)
            build_cylinder(bm, mid_shin, 0.055, s_len, rot=(0, s_pitch, s_yaw - math.pi/2), mat_idx=0)
            
            # Tobillo y pie de agarre magnético
            build_sphere(bm, ankle_pos, 0.08, segments=12, rings=8, mat_idx=1)
            foot_base = (ankle_pos[0], ankle_pos[1], Z0 + fz)
            build_cylinder(bm, foot_base, 0.10, 0.05, mat_idx=1)
            for ca in [0, 120, 240]:
                crad = R(ca) + math.atan2(fy, fx)
                c_x = ankle_pos[0] + 0.09 * math.cos(crad)
                c_y = ankle_pos[1] + 0.09 * math.sin(crad)
                build_box(bm, (c_x, c_y, Z0 + fz + 0.03), (0.04, 0.11, 0.06), rot=(0, 0, crad), mat_idx=2)

    mat_list = [
        mats['Armor_Steel_Dark'], mats['Armor_Gunmetal'], mats['Polished_Chrome'],
        mats['Glow_CRT_Green'], mats['Glow_Eye_Red'], mats['Hazard_Yellow']
    ]
    obj = create_mesh_object("SM_Bestiary_04_Spider", col, geom, mat_list)
    add_bevel_modifier(obj, width=0.03)
    return obj


# 05. CINDER SPIRIT GOLEM (Gólem de la Fragua / Espíritu Ígneo 100% Esculpido)
# Fila 1 - X = 8.0, Y = -0.4, Z = 0.0
def build_entity5_golem(col, mats):
    X0 = 8.0; Y0 = -0.4; Z0 = 0.0
    def geom(bm):
        # Torso: Caldera masiva de fundición oscura con perfiles biselados
        build_box(bm, (X0, Y0, Z0 + 1.45), (1.05, 0.85, 0.95), mat_idx=0)
        
        # Compuerta de fragua arqueada frontal con barrotes y magma incandescente
        build_box(bm, (X0 - 0.52, Y0, Z0 + 1.40), (0.08, 0.52, 0.55), mat_idx=2) # Marco de acero
        build_box(bm, (X0 - 0.55, Y0, Z0 + 1.40), (0.02, 0.44, 0.48), mat_idx=1) # Fuego/Magma incandescente
        for bz in [-0.14, 0.0, 0.14]:
            build_cylinder(bm, (X0 - 0.56, Y0, Z0 + 1.40 + bz), 0.02, 0.48, rot=(0, R(90), 0), mat_idx=0)
            
        # Chimeneas dorsales dobles de fundición con llamas vivas cómic
        for cy in [-0.28, 0.28]:
            build_cylinder(bm, (X0 + 0.35, Y0 + cy, Z0 + 2.05), 0.12, 0.55, mat_idx=0)
            build_cylinder(bm, (X0 + 0.35, Y0 + cy, Z0 + 2.30), 0.14, 0.08, mat_idx=2) # Anillo de escape
            build_cone(bm, (X0 + 0.35, Y0 + cy, Z0 + 2.55), 0.15, 0.45, rot=(0,0,0), mat_idx=6) # Llama
            
        # Cabeza de yunque de fundición con visor de triple ranura ardiente
        build_box(bm, (X0 - 0.10, Y0, Z0 + 2.05), (0.58, 0.52, 0.42), mat_idx=0)
        for vx in [-0.12, 0.0, 0.12]:
            build_box(bm, (X0 - 0.38, Y0 + vx, Z0 + 2.05), (0.05, 0.04, 0.20), mat_idx=1)
            
        # Hombros acorazados con bridas pesadas y rótulas de magma
        for ay in [-0.68, 0.68]:
            build_cylinder(bm, (X0, Y0 + ay, Z0 + 1.65), 0.24, 0.16, rot=(R(90), 0, 0), mat_idx=0)
            build_sphere(bm, (X0, Y0 + ay, Z0 + 1.65), 0.18, segments=14, rings=10, mat_idx=1) # Rótula magma
            
            # Brazo masivo de fundición y piedra
            build_cylinder(bm, (X0 - 0.18, Y0 + ay, Z0 + 1.30), 0.18, 0.65, rot=(0, R(30), 0), mat_idx=4)
            # Fisuras de magma en el antebrazo
            build_box(bm, (X0 - 0.20, Y0 + ay, Z0 + 1.30), (0.38, 0.04, 0.10), rot=(0, R(30), 0), mat_idx=5)
            
            # Puño colosal de fundición apoyado con placas de impacto
            build_box(bm, (X0 - 0.45, Y0 + ay, Z0 + 0.85), (0.44, 0.38, 0.42), mat_idx=0)
            build_box(bm, (X0 - 0.66, Y0 + ay, Z0 + 0.85), (0.04, 0.32, 0.18), mat_idx=1) # Nudillos ardientes
            
        # Cola / tobera de escape inferior de plasma
        for i, tz in enumerate([0.70, 0.90, 1.15]):
            tx = X0 + 0.45 - i * 0.12
            build_sphere(bm, (tx, Y0, Z0 + tz), 0.22 - i * 0.03, segments=12, rings=8, mat_idx=3)

    mat_list = [
        mats['Furnace_Cast_Iron'], mats['Comic_Flame_Orange'], mats['Armor_Steel_Dark'],
        mats['Glow_Plasma_Cyan'], mats['Armor_Navy_Blue'], mats['Molten_Magma_Seams'],
        mats['Comic_Flame_Yellow']
    ]
    obj = create_mesh_object("SM_Bestiary_05_Golem", col, geom, mat_list)
    add_bevel_modifier(obj, width=0.04)
    return obj


# 06. CHARR-BRUTE (Gorila de Fundición Mecanizado - Rediseño Vívido Cartoon/Industrial)
# Fila 2 - X = -6.0, Y = 3.8, Z = 1.35m
def build_entity6_brute(col, mats):
    X0 = -6.0; Y0 = 3.8; Z0 = 1.35
    def geom(bm):
        # Torso masivo de fundición color naranja de seguridad / fundición viva
        build_box(bm, (X0, Y0, Z0 + 1.45), (1.15, 0.90, 0.95), mat_idx=0) # Armor_Safety_Orange
        # Rejilla pectoral de fundición con fuego interior
        build_box(bm, (X0 - 0.55, Y0, Z0 + 1.45), (0.08, 0.55, 0.55), mat_idx=1) # Armor_Gunmetal
        build_box(bm, (X0 - 0.58, Y0, Z0 + 1.45), (0.02, 0.45, 0.45), mat_idx=2) # Comic_Flame_Orange (resplandor!)
        # Franja Hazard en el pecho
        build_box(bm, (X0 - 0.57, Y0, Z0 + 1.80), (0.04, 0.70, 0.12), mat_idx=3) # Hazard_Stripes
        
        # Cabeza de gorila con mandíbula masiva y visor horizontal rojo intenso
        build_box(bm, (X0 - 0.52, Y0, Z0 + 1.82), (0.50, 0.46, 0.44), mat_idx=1)
        build_box(bm, (X0 - 0.75, Y0, Z0 + 1.80), (0.08, 0.32, 0.14), mat_idx=4) # Visor rojo brillante
        build_box(bm, (X0 - 0.68, Y0, Z0 + 1.60), (0.28, 0.38, 0.18), mat_idx=0) # Mandíbula inferior naranja
        
        # Brazos colosales con DOBLE pistón hidráulico cromado y hombreras con franja de peligro
        for hy in [-0.65, 0.65]:
            # Hombrera enorme redondeada
            build_box(bm, (X0, Y0 + hy, Z0 + 2.05), (0.55, 0.50, 0.45), mat_idx=0)
            build_box(bm, (X0, Y0 + hy, Z0 + 2.05), (0.57, 0.10, 0.16), mat_idx=3) # Hazard band
            # Articulación doble de hombro y codo con pistones
            build_mechanical_joint_bm(bm, (X0 - 0.14, Y0 + hy, Z0 + 1.75), rot=(0, R(40), 0), hub_radius=0.14, length=0.60, piston_radius=0.065,
                                      mat_hub=1, mat_cyl=5, mat_rod=6, mat_pin=5)
            build_cylinder(bm, (X0 - 0.38, Y0 + hy, Z0 + 1.25), 0.20, 0.85, rot=(0, R(35), 0), mat_idx=0)
            build_mechanical_joint_bm(bm, (X0 - 0.58, Y0 + hy, Z0 + 0.95), rot=(0, R(90), 0), hub_radius=0.12, length=0.50, piston_radius=0.055,
                                      mat_hub=1, mat_cyl=5, mat_rod=6, mat_pin=5)
            # Puño colosal de fundición con placas de impacto
            build_box(bm, (X0 - 0.78, Y0 + hy, Z0 + 0.45), (0.55, 0.48, 0.48), mat_idx=1)
            build_box(bm, (X0 - 1.02, Y0 + hy, Z0 + 0.45), (0.08, 0.44, 0.18), mat_idx=2) # Nudillos ardientes
            
        # Patas cortas de soporte pesado
        for ly in [-0.34, 0.34]:
            build_cylinder(bm, (X0 + 0.20, Y0 + ly, Z0 + 0.70), 0.22, 0.82, mat_idx=1)
            build_box(bm, (X0 + 0.20, Y0 + ly, Z0 + 0.18), (0.55, 0.44, 0.28), mat_idx=0)

    mat_list = [
        mats['Armor_Safety_Orange'], mats['Armor_Gunmetal'], mats['Comic_Flame_Orange'],
        mats['Hazard_Stripes'], mats['Glow_Eye_Red'], mats['Hazard_Yellow'],
        mats['Polished_Chrome']
    ]
    obj = create_mesh_object("SM_Bestiary_06_Brute", col, geom, mat_list)
    add_bevel_modifier(obj, width=0.04)
    return obj


# 07. PLASMA LEECH (Sanguijuela de Plasma y Tubería)
# Fila 2 - X = -2.0, Y = 3.8, Z = 1.35m
def build_entity7_leech(col, mats):
    X0 = -2.0; Y0 = 3.8; Z0 = 1.35
    def geom(bm):
        # Cuerpo serpenteante de 8 anillos de acero oscuro y latón
        for i in range(8):
            ang = R(i * 18 - 40)
            cz = Z0 + 0.65 + 0.70 * math.sin(R(i * 22))
            cx = X0 + 0.60 * math.cos(ang)
            rad = 0.32 - i * 0.016
            build_cylinder(bm, (cx, Y0, cz), rad, 0.22, segments=18, rot=(0, -ang, 0), mat_idx=0)
            build_cylinder(bm, (cx, Y0, cz), rad * 1.12, 0.06, segments=18, rot=(0, -ang, 0), mat_idx=1)
            if i % 2 == 0:
                build_cone(bm, (cx, Y0 - rad, cz - 0.10), 0.035, 0.15, rot=(R(90), 0, 0), mat_idx=2)
                build_cone(bm, (cx, Y0 + rad, cz - 0.10), 0.035, 0.15, rot=(R(-90), 0, 0), mat_idx=2)

        # Fauce circular mecánica con iris de 12 dientes de carburo
        bx = X0 + 0.60 * math.cos(R(-40))
        bz = Z0 + 0.65
        build_cylinder(bm, (bx, Y0, bz), 0.34, 0.12, segments=24, rot=(0, R(40), 0), mat_idx=1)
        for da in range(12):
            d_rad = R(da * 30)
            build_cone(bm, (bx - 0.06 + 0.20*math.cos(d_rad), Y0 + 0.20*math.sin(d_rad), bz), 0.04, 0.14, rot=(0, R(40), 0), mat_idx=2)
            build_cone(bm, (bx - 0.04 + 0.11*math.cos(d_rad), Y0 + 0.11*math.sin(d_rad), bz), 0.028, 0.09, rot=(0, R(40), 0), mat_idx=2)

        # Núcleo de plasma cian brillante
        build_sphere(bm, (bx - 0.12, Y0, bz), 0.18, segments=14, rings=10, mat_idx=3)
        build_sphere(bm, (X0, Y0, Z0 + 1.35), 0.28, segments=14, rings=10, mat_idx=3)

    mat_list = [
        mats['Armor_Steel_Dark'], mats['Machinery_Brass'], mats['Polished_Chrome'],
        mats['Glow_Plasma_Cyan']
    ]
    obj = create_mesh_object("SM_Bestiary_07_Leech", col, geom, mat_list)
    add_bevel_modifier(obj, width=0.03)
    return obj


# 08. CYBER-HOUND SCOUT (Sabueso Cibernético Ligero - Rediseño 100% Mecánico Robusto)
# Fila 2 - X = 2.0, Y = 3.8, Z = 1.35m
def build_entity8_hound(col, mats):
    X0 = 2.0; Y0 = 3.8; Z0 = 1.35
    def geom(bm):
        # Chasis aerodinámico acorazado bi-tono (Hazard Yellow + Dark Gunmetal)
        build_box(bm, (X0, Y0, Z0 + 0.90), (0.88, 0.46, 0.40), mat_idx=0) # Hazard Yellow
        build_box(bm, (X0, Y0, Z0 + 0.92), (0.75, 0.48, 0.32), mat_idx=1) # Dark Gunmetal
        build_box(bm, (X0, Y0 - 0.24, Z0 + 0.90), (0.90, 0.02, 0.14), mat_idx=2) # Hazard stripe
        build_box(bm, (X0, Y0 + 0.24, Z0 + 0.90), (0.90, 0.02, 0.14), mat_idx=2) # Hazard stripe
        
        # Cuello y cabeza estilizada con hocico sensor y visor cian
        build_box(bm, (X0 - 0.52, Y0, Z0 + 1.05), (0.45, 0.30, 0.28), mat_idx=0)
        build_box(bm, (X0 - 0.74, Y0, Z0 + 1.05), (0.06, 0.24, 0.09), mat_idx=3) # Visor óptico cian
        # Orejas de radar
        build_cone(bm, (X0 - 0.45, Y0 - 0.12, Z0 + 1.25), 0.04, 0.20, rot=(R(-15), R(-20), 0), mat_idx=1)
        build_cone(bm, (X0 - 0.45, Y0 + 0.12, Z0 + 1.25), 0.04, 0.20, rot=(R(15), R(-20), 0), mat_idx=1)
        
        # Unidad de sensor LIDAR giratoria en el lomo
        build_cylinder(bm, (X0 - 0.10, Y0, Z0 + 1.15), 0.04, 0.18, mat_idx=1)
        build_cylinder(bm, (X0 - 0.10, Y0, Z0 + 1.26), 0.20, 0.05, segments=18, rot=(R(20), 0, 0), mat_idx=5)
        
        # 4 Patas digitígradas con pistones articulados, resortes y pezuñas de goma
        for px, py, sgn in [(-0.30, -0.22, 1), (-0.30, 0.22, 1), (0.32, -0.22, -1), (0.32, 0.22, -1)]:
            # Muslo con articulación
            build_mechanical_joint_bm(bm, (X0 + px, Y0 + py, Z0 + 0.65), rot=(0, R(30 * sgn), 0), length=0.45, piston_radius=0.04,
                                      mat_hub=1, mat_cyl=0, mat_rod=6, mat_pin=5)
            # Amortiguador y pantorrilla con resorte
            build_cylinder(bm, (X0 + px + 0.08 * sgn, Y0 + py, Z0 + 0.25), 0.04, 0.48, mat_idx=6)
            build_box(bm, (X0 + px + 0.08 * sgn, Y0 + py, Z0 + 0.05), (0.18, 0.14, 0.09), mat_idx=4)

        # Cola de antena de látigo con emisor de punta
        build_cylinder(bm, (X0 + 0.55, Y0, Z0 + 1.05), 0.025, 0.65, rot=(0, R(-65), 0), mat_idx=6)
        build_sphere(bm, (X0 + 0.85, Y0, Z0 + 1.35), 0.06, segments=8, rings=6, mat_idx=3)

    mat_list = [
        mats['Hazard_Yellow'], mats['Armor_Gunmetal'], mats['Hazard_Stripes'],
        mats['Glow_Plasma_Cyan'], mats['Rubber_Black'], mats['Machinery_Brass'],
        mats['Polished_Chrome']
    ]
    obj = create_mesh_object("SM_Bestiary_08_Hound", col, geom, mat_list)
    add_bevel_modifier(obj, width=0.03)
    return obj


# 09. FURNACE KEEPER (Guardián de la Caldera - Rediseño Caldera Roja/Naranja con Gran Puerta de Fuego)
# Fila 2 - X = 6.0, Y = 3.8, Z = 1.35m
def build_entity9_keeper(col, mats):
    X0 = 6.0; Y0 = 3.8; Z0 = 1.35
    def geom(bm):
        # Caldera cilíndrica de chapa remachada en Rojo Industrial de Bombero
        build_cylinder(bm, (X0, Y0, Z0 + 1.25), 0.46, 0.88, segments=18, mat_idx=0) # Emergency_Red
        # Anillos de latón reforzados en la caldera
        build_cylinder(bm, (X0, Y0, Z0 + 1.55), 0.48, 0.05, segments=18, mat_idx=3) # Brass
        build_cylinder(bm, (X0, Y0, Z0 + 0.95), 0.48, 0.05, segments=18, mat_idx=3) # Brass
        
        # Puerta de fuego arqueada frontal con barrotes y fuego ardiendo
        build_box(bm, (X0 - 0.42, Y0, Z0 + 1.10), (0.10, 0.42, 0.40), mat_idx=1) # Gunmetal frame
        build_box(bm, (X0 - 0.46, Y0, Z0 + 1.10), (0.02, 0.34, 0.32), mat_idx=2) # Comic_Flame_Orange (Fuego vivo!)
        for bz in [-0.10, 0.0, 0.10]:
            build_cylinder(bm, (X0 - 0.47, Y0, Z0 + 1.10 + bz), 0.015, 0.38, rot=(0, R(90), 0), mat_idx=1)
        
        # Manómetro analógico gigante de presión
        build_gauge_bm(bm, (X0 - 0.42, Y0, Z0 + 1.52), rot=(0, R(-90), 0), radius=0.14, depth=0.08,
                       mat_brass=3, mat_face=4, mat_needle=5)

        # Casco de buzo / escafandra en latón con mirilla enrejada
        build_cylinder(bm, (X0, Y0, Z0 + 1.85), 0.26, 0.40, segments=16, mat_idx=3)
        build_box(bm, (X0 - 0.24, Y0, Z0 + 1.85), (0.06, 0.26, 0.12), mat_idx=6) # Mirilla dorada brillante
        build_cylinder(bm, (X0 + 0.18, Y0, Z0 + 2.10), 0.08, 0.40, mat_idx=1) # Chimenea con contrapeso

        # Brazo derecho: Tenazas forjadas gigantes con cilindro amarillo y franja hazard
        build_sphere(bm, (X0, Y0 - 0.52, Z0 + 1.45), 0.15, segments=12, rings=8, mat_idx=1)
        build_cylinder(bm, (X0 - 0.26, Y0 - 0.52, Z0 + 1.20), 0.11, 0.55, rot=(0, R(30), 0), mat_idx=0)
        build_mechanical_joint_bm(bm, (X0 - 0.48, Y0 - 0.52, Z0 + 0.90), rot=(0, R(90), 0), hub_radius=0.12, length=0.48, piston_radius=0.055,
                                  mat_hub=1, mat_cyl=8, mat_rod=7, mat_pin=3)
        # Quijadas de tenaza
        build_box(bm, (X0 - 0.70, Y0 - 0.52, Z0 + 0.70), (0.45, 0.10, 0.28), mat_idx=1)
        build_box(bm, (X0 - 0.70, Y0 - 0.52, Z0 + 0.70), (0.47, 0.11, 0.08), mat_idx=9) # Hazard band

        # Brazo izquierdo: Martillo neumático de fundición con manguera de presión
        build_sphere(bm, (X0, Y0 + 0.52, Z0 + 1.45), 0.15, segments=12, rings=8, mat_idx=1)
        build_cylinder(bm, (X0 - 0.24, Y0 + 0.52, Z0 + 1.20), 0.10, 0.55, rot=(0, R(25), 0), mat_idx=0)
        build_cylinder(bm, (X0 - 0.45, Y0 + 0.52, Z0 + 0.95), 0.06, 0.58, rot=(R(-25), 0, 0), mat_idx=1)
        build_box(bm, (X0 - 0.76, Y0 + 0.46, Z0 + 0.75), (0.38, 0.10, 0.24), mat_idx=7)
        build_box(bm, (X0 - 0.76, Y0 + 0.58, Z0 + 0.75), (0.38, 0.10, 0.24), mat_idx=7)

        # Piernas con protectores acorazados y botas de fundición
        for ly in [-0.24, 0.24]:
            build_cylinder(bm, (X0, Y0 + ly, Z0 + 0.55), 0.13, 0.62, mat_idx=1)
            build_mechanical_joint_bm(bm, (X0, Y0 + ly, Z0 + 0.45), rot=(0, R(90), 0), length=0.48, piston_radius=0.05,
                                      mat_hub=1, mat_cyl=8, mat_rod=7, mat_pin=3)
            build_box(bm, (X0 - 0.08, Y0 + ly, Z0 + 0.10), (0.40, 0.28, 0.20), mat_idx=0)

    mat_list = [
        mats['Emergency_Red'], mats['Armor_Gunmetal'], mats['Comic_Flame_Orange'],
        mats['Machinery_Brass'], mats['Dial_White'], mats['Emergency_Red'],
        mats['Comic_Flame_Yellow'], mats['Polished_Chrome'], mats['Hazard_Yellow'],
        mats['Hazard_Stripes']
    ]
    obj = create_mesh_object("SM_Bestiary_09_Keeper", col, geom, mat_list)
    add_bevel_modifier(obj, width=0.035)
    return obj


# 10. VAPOR CREEPER (Merodeador de Vapor y Toxinas)
# Fila 2 - X = 10.0, Y = 3.8, Z = 1.35m
def build_entity10_creeper(col, mats):
    X0 = 10.0; Y0 = 3.8; Z0 = 1.35
    def geom(bm):
        # Columna vertebral biomecánica de 6 segmentos
        for vi, vz in enumerate([0.70, 0.88, 1.06, 1.24, 1.42, 1.60]):
            build_cylinder(bm, (X0, Y0, Z0 + vz), 0.08, 0.15, segments=12, mat_idx=0)
            build_box(bm, (X0 - 0.08, Y0, Z0 + vz), (0.24, 0.38, 0.07), mat_idx=1)
            
        # Contenedor cilíndrico de toxina verde neón pulsante en el pecho
        build_cylinder(bm, (X0 - 0.14, Y0, Z0 + 1.20), 0.14, 0.45, segments=16, mat_idx=7)
        # Costillas de protección sobre la toxina
        for rz in [1.05, 1.20, 1.35]:
            build_box(bm, (X0 - 0.28, Y0, Z0 + rz), (0.04, 0.36, 0.04), mat_idx=0)

        # Cráneo con visor de triple lente roja y máscara de filtros amarillos
        build_box(bm, (X0 - 0.20, Y0, Z0 + 1.82), (0.38, 0.34, 0.38), mat_idx=2)
        build_sphere(bm, (X0 - 0.38, Y0, Z0 + 1.88), 0.045, segments=8, rings=6, mat_idx=3)
        build_sphere(bm, (X0 - 0.38, Y0 - 0.08, Z0 + 1.78), 0.038, segments=8, rings=6, mat_idx=3)
        build_sphere(bm, (X0 - 0.38, Y0 + 0.08, Z0 + 1.78), 0.038, segments=8, rings=6, mat_idx=3)
        # Filtros de máscara antigás laterales
        build_cylinder(bm, (X0 - 0.18, Y0 - 0.22, Z0 + 1.72), 0.07, 0.14, rot=(0, R(90), 0), mat_idx=5)
        build_cylinder(bm, (X0 - 0.18, Y0 + 0.22, Z0 + 1.72), 0.07, 0.14, rot=(0, R(90), 0), mat_idx=5)

        # 4 Toberas dorsales de vapor con conos de escape
        for ti, ty in enumerate([-0.24, -0.08, 0.08, 0.24]):
            build_cylinder(bm, (X0 + 0.18, Y0 + ty, Z0 + 1.50), 0.06, 0.42, rot=(R(-30), R(20), 0), mat_idx=1)
            build_sphere(bm, (X0 + 0.28, Y0 + ty, Z0 + 1.70), 0.045, segments=8, rings=6, mat_idx=4)
            build_cone(bm, (X0 + 0.44, Y0 + ty, Z0 + 1.88), 0.14, 0.42, rot=(R(30), R(-20), 0), mat_idx=5)

        # Brazos mantis de corte con cuchillas de cromo y tubos de veneno
        for ay in [-0.32, 0.32]:
            build_sphere(bm, (X0 - 0.08, Y0 + ay, Z0 + 1.55), 0.08, segments=10, rings=8, mat_idx=1)
            build_cylinder(bm, (X0 - 0.22, Y0 + ay, Z0 + 1.30), 0.045, 0.58, rot=(0, R(35), 0), mat_idx=0)
            build_cone(bm, (X0 - 0.45, Y0 + ay, Z0 + 1.00), 0.03, 0.36, rot=(0, R(-90), 0), mat_idx=6)
            build_cylinder(bm, (X0 - 0.32, Y0 + ay, Z0 + 1.15), 0.035, 0.20, mat_idx=7)

        # Depósito inferior y tobera ventral
        build_cylinder(bm, (X0, Y0, Z0 + 0.55), 0.16, 0.22, mat_idx=1)
        build_cone(bm, (X0, Y0, Z0 + 0.35), 0.14, 0.28, rot=(R(180), 0, 0), mat_idx=7)

    mat_list = [
        mats['Armor_Steel_Dark'], mats['Armor_Gunmetal'], mats['Armor_Bone_Pale'],
        mats['Glow_Eye_Red'], mats['Machinery_Brass'], mats['Hazard_Yellow'],
        mats['Polished_Chrome'], mats['Toxin_Neon_Green']
    ]
    obj = create_mesh_object("SM_Bestiary_10_Creeper", col, geom, mat_list)
    add_bevel_modifier(obj, width=0.03)
    return obj


# -------------------------------------------------------------------------
# PEDESTALES Y ENTORNO DE HANGAR DE ALTA CALIDAD
# -------------------------------------------------------------------------
def build_environment(col, mats):
    def geom_floor(bm):
        build_box(bm, (0, 1.75, -0.05), (32.0, 18.0, 0.10), mat_idx=0)
    create_mesh_object("Studio_Floor_Mesh", col, geom_floor, mats['Studio_Floor'])
    
    # Grada escalonada para Fila 2
    def geom_terrace(bm):
        build_box(bm, (0, 3.8, 0.675), (28.0, 3.6, 1.35), mat_idx=0)
        build_box(bm, (0, 1.95, 1.32), (28.0, 0.08, 0.10), mat_idx=1) # Hazard stripe en el borde del escalón
    create_mesh_object("Terrace_Tier2", col, geom_terrace, [mats['Plinth_Dark'], mats['Hazard_Stripes']])

    # Pedestales para las 10 entidades
    plinth_coords = [
        (-8.0, -0.4, 0.075), (-4.0, -0.4, 0.075), (0.0, -0.4, 0.075), (4.0, -0.4, 0.075), (8.0, -0.4, 0.075),
        (-6.0,  3.8, 1.425), (-2.0,  3.8, 1.425), (2.0,  3.8, 1.425), (6.0,  3.8, 1.425), (10.0, 3.8, 1.425)
    ]
    for px, py, pz in plinth_coords:
        def make_plinth(cx=px, cy=py, cz=pz):
            def geom_p(bm):
                build_box(bm, (cx, cy, cz), (2.4, 2.0, 0.15), mat_idx=0)
                build_box(bm, (cx, cy - 1.01, cz), (1.1, 0.02, 0.06), mat_idx=1)
            return geom_p
        create_mesh_object(f"Plinth_X_{px}_Y_{py}", col, make_plinth(), [mats['Plinth_Dark'], mats['Plinth_Plaque']])

    # Muro de hangar industrial al fondo
    def geom_wall(bm):
        build_box(bm, (0, 6.4, 4.0), (34.0, 0.2, 8.0), mat_idx=0)
        for bx in [-12.0, -8.0, -4.0, 0.0, 4.0, 8.0, 12.0]:
            build_box(bm, (bx, 6.25, 4.0), (0.50, 0.18, 8.0), mat_idx=1)
        build_cylinder(bm, (0, 6.15, 5.8), 0.20, 34.0, segments=16, rot=(0, R(90), 0), mat_idx=1)
        build_box(bm, (0, 6.22, 4.8), (32.0, 0.05, 0.15), mat_idx=2)
    create_mesh_object("Hangar_Wall_Background", col, geom_wall, [mats['Studio_Floor'], mats['Armor_Steel_Dark'], mats['Hazard_Stripes']])


# -------------------------------------------------------------------------
# ILUMINACIÓN FOTOMÉTRICA DE ESTUDIO (CÓMIC CEL-SHADING)
# -------------------------------------------------------------------------
def setup_lighting(col):
    # Luz Principal Cálida (Key Sun)
    key_data = bpy.data.lights.new(name="Key_Sun", type='SUN')
    key_data.energy = 5.2
    key_data.color = (1.0, 0.98, 0.94)
    key_data.angle = math.radians(8.0)
    key_obj = bpy.data.objects.new("Key_Sun", key_data)
    key_obj.rotation_euler = (R(46), R(16), R(-32))
    col.objects.link(key_obj)

    # Luz de Recorte Fría (Rim Sun - Silueta Azul)
    rim_data = bpy.data.lights.new(name="Rim_Sun", type='SUN')
    rim_data.energy = 4.5
    rim_data.color = (0.75, 0.88, 1.0)
    rim_data.angle = math.radians(15.0)
    rim_obj = bpy.data.objects.new("Rim_Sun", rim_data)
    rim_obj.rotation_euler = (R(-58), 0, R(160))
    col.objects.link(rim_obj)

    # Luz de Relleno Suave (Fill Sun)
    fill_data = bpy.data.lights.new(name="Fill_Sun", type='SUN')
    fill_data.energy = 2.8
    fill_data.color = (0.86, 0.90, 0.96)
    fill_data.angle = math.radians(35.0)
    fill_obj = bpy.data.objects.new("Fill_Sun", fill_data)
    fill_obj.rotation_euler = (R(60), R(-30), R(45))
    col.objects.link(fill_obj)

    # Luz Adicional Frontal para Grada 2 (Tier 2 Accent Sun)
    tier2_key = bpy.data.lights.new(name="Tier2_Key_Sun", type='SUN')
    tier2_key.energy = 3.6
    tier2_key.color = (1.0, 0.96, 0.92)
    tier2_key.angle = math.radians(10.0)
    tier2_obj = bpy.data.objects.new("Tier2_Key_Sun", tier2_key)
    tier2_obj.rotation_euler = (R(35), R(-12), R(-18))
    col.objects.link(tier2_obj)


# -------------------------------------------------------------------------
# CÁMARAS Y ENCUADRES PRECISOS (PANORAMA Y CLOSE-UPS HEROICOS 1080P)
# -------------------------------------------------------------------------
def create_camera_tracking(col, name, cam_pos, target_pos, lens=45.0):
    cam_data = bpy.data.cameras.new(name)
    cam_data.lens = lens
    cam_data.clip_start = 0.1
    cam_data.clip_end = 250.0
    cam_obj = bpy.data.objects.new(name, cam_data)
    cam_obj.location = cam_pos
    col.objects.link(cam_obj)
    
    dir_vec = Vector(target_pos) - Vector(cam_pos)
    rot_quat = dir_vec.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()
    return cam_obj

def setup_all_cameras(col):
    cams = {}
    # Cámara panorámica que abarca con perfecta visibilidad las 10 entidades
    cams['Panorama'] = create_camera_tracking(
        col, "Cam_Panorama",
        cam_pos=(0.0, -17.5, 6.8),
        target_pos=(0.0, 1.8, 1.6),
        lens=35.0
    )
    
    # Coordenadas exactas de encuadre heroico 3/4 para cada entidad (mirando a sus caras y frontales)
    camera_configs = {
        1: ((-8.0, -0.4, 1.20), (-10.2, -2.6, 1.55), 45.0),   # Werewolf (cara a -X/-Y)
        2: ((-4.0, -0.4, 1.35), ( -2.6, -3.0, 1.60), 46.0),   # Drone (frente a -Y)
        3: (( 0.0, -0.4, 1.15), (  1.5, -2.8, 1.45), 46.0),   # Goblin (frente a -Y)
        4: (( 4.0, -0.4, 1.55), (  5.5, -2.8, 1.80), 45.0),   # Spider (frente a -Y)
        5: (( 8.0, -0.4, 1.35), (  6.4, -2.8, 1.65), 45.0),   # Golem (frente a -Y)
        6: ((-6.0,  3.8, 2.40), ( -8.4,  1.4, 2.70), 42.0),   # Brute (cara a -X/-Y)
        7: ((-2.0,  3.8, 2.20), ( -0.6,  1.8, 2.45), 44.0),   # Leech (fauce abierta)
        8: (( 2.0,  3.8, 2.15), ( -0.2,  1.6, 2.45), 42.0),   # Hound (cara a -X/-Y)
        9: (( 6.0,  3.8, 2.40), (  3.8,  1.4, 2.70), 42.0),   # Keeper (puerta fuego a -X/-Y)
        10:((10.0,  3.8, 2.40), (  7.8,  1.4, 2.70), 42.0)    # Creeper (máscara a -X/-Y)
    }
    for cid, (t_pos, c_pos, flens) in camera_configs.items():
        cams[cid] = create_camera_tracking(col, f"Cam_Entity_{cid:02d}", c_pos, t_pos, lens=flens)
        
    return cams


# -------------------------------------------------------------------------
# GENERACIÓN DE LÁMINA MAESTRA 2.5K CON PIL
# -------------------------------------------------------------------------
def create_master_bestiary_sheet(render_files, output_path):
    W, H = 2560, 1440
    sheet = Image.new("RGBA", (W, H), (14, 16, 20, 255))
    draw = ImageDraw.Draw(sheet)

    def get_font(size):
        font_paths = [
            r"C:\Windows\Fonts\segoeuib.ttf",
            r"C:\Windows\Fonts\arialbd.ttf",
            r"C:\Windows\Fonts\segoeui.ttf",
            r"C:\Windows\Fonts\arial.ttf"
        ]
        for fp in font_paths:
            if os.path.exists(fp):
                try:
                    return ImageFont.truetype(fp, size)
                except Exception:
                    pass
        return ImageFont.load_default()

    font_title = get_font(26)
    font_sub = get_font(15)
    font_badge = get_font(13)
    font_card_tit = get_font(15)
    font_card_desc = get_font(12)

    # Cabecera
    draw.rectangle([(0, 0), (W, 70)], fill=(18, 22, 28, 255))
    draw.text((36, 14), "ASTRA HAZARD // BESTIARIO DE AMENAZAS Y ENTIDADES BIOMECÁNICAS", fill=(250, 175, 25, 255), font=font_sub)
    draw.text((36, 34), "CATÁLOGO MAESTRO 100% 3D (10 ENTIDADES OFICIALES) // BLENDER 5.2 LTS FREESTYLE CEL-SHADING", fill=(255, 255, 255, 255), font=font_title)

    badges = [
        ("10 ENTIDADES 3D", (220, 110, 20, 255)),
        ("CEL-SHADING CÓMIC", (140, 60, 180, 255)),
        ("IA CONDUCTUAL UE5", (20, 160, 90, 255)),
        ("FREESTYLE INK 2.6PX", (20, 110, 200, 255)),
        ("BLENDER 5.2 LTS", (90, 70, 210, 255))
    ]
    bx = W - 36
    for text, col in reversed(badges):
        bw = 150
        bx -= bw
        draw.rectangle([(bx, 24), (bx + bw - 10, 48)], fill=col)
        draw.text((bx + 12, 28), text, fill=(255, 255, 255, 255), font=font_badge)
        bx -= 10

    # Panorama Principal (2488 x 680)
    pan_path = render_files.get('Panorama')
    if pan_path and os.path.exists(pan_path):
        try:
            im_pan = Image.open(pan_path).convert("RGBA")
            im_pan_res = im_pan.resize((2488, 680), Image.Resampling.LANCZOS)
            sheet.paste(im_pan_res, (36, 85))
            draw.rectangle([(36, 85), (36 + 2488, 85 + 680)], outline=(60, 70, 85, 255), width=2)
        except Exception as e:
            print(f"Error cargando panorama: {e}")

    # Cuadrícula inferior de 10 Fichas Técnicas (2 filas x 5 columnas)
    info_entities = {
        1: ("01. Mechanical Werewolf", ["• 3 escapes con llamas cómic 2D", "• Pistones hidráulicos en codos/rodillas", "• Garras cartoon sobre pasarela"], (235, 115, 25, 255)),
        2: ("02. Auditor Drone", ["• Ojo rojo con cono de escaneo", "• 3 manómetros analógicos latón", "• Pantalla CRT verde de radar"], (45, 155, 230, 255)),
        3: ("03. Scrapper Goblin", ["• Monóculo dorado y máscara ósea", "• Maza con púas doradas y sierra", "• Cinturón con engranaje central"], (240, 195, 30, 255)),
        4: ("04. Ceiling Spider-Bot", ["• Suspendida de vigas con pistones", "• 4 patas articuladas hidráulicas", "• Sensor óptico verde de emboscada"], (35, 195, 125, 255)),
        5: ("05. Cinder Spirit Golem", ["• Cola de plasma saliendo del horno", "• Armadura azul con magma naranja", "• Visor triple incandescente"], (35, 175, 245, 255)),
        6: ("06. Charr-Brute", ["• Gorila de fundición acorazado", "• Pistones dobles en hombros", "• Puños gigantes incandescentes"], (235, 65, 35, 255)),
        7: ("07. Plasma Leech", ["• Sanguijuela anélida segmentada", "• Boca circular con dientes radiales", "• Núcleo con arco eléctrico de plasma"], (165, 85, 235, 255)),
        8: ("08. Cyber-Hound Scout", ["• Cuadrúpedo ligero de infiltración", "• Disco giratorio LIDAR y sensor", "• Patas de resorte de alta agilidad"], (25, 195, 175, 255)),
        9: ("09. Furnace Keeper", ["• Humanoide con mandil térmico", "• Máscara con visor y chimenea", "• Tenazas forjadas gigantes"], (230, 115, 25, 255)),
        10: ("10. Vapor Creeper", ["• Esqueleto flotante biomecánico", "• 4 toberas dorsales con vapor", "• Agujas inyectoras de toxinas"], (110, 150, 160, 255))
    }

    card_w = 480
    card_h = 280
    start_y = 785
    spacing_x = 22
    spacing_y = 20

    for i in range(10):
        cid = i + 1
        row = i // 5
        col_idx = i % 5
        cx = 36 + col_idx * (card_w + spacing_x)
        cy = start_y + row * (card_h + spacing_y)

        name, bullets, col_accent = info_entities[cid]

        draw.rectangle([(cx, cy), (cx + card_w, cy + card_h)], fill=(22, 26, 32, 255), outline=(42, 50, 62, 255), width=2)
        draw.rectangle([(cx, cy), (cx + card_w, cy + 6)], fill=col_accent)

        thumb_w = 200
        thumb_h = card_h - 10
        tx = cx + 4
        ty = cy + 6

        c_path = render_files.get(cid)
        if c_path and os.path.exists(c_path):
            try:
                im_c = Image.open(c_path).convert("RGBA")
                im_c_res = im_c.resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
                sheet.paste(im_c_res, (tx, ty))
                draw.rectangle([(tx, ty), (tx + thumb_w, ty + thumb_h)], outline=(50, 60, 75, 255), width=1)
            except Exception as e:
                print(f"Error pegando close-up {cid}: {e}")

        info_x = tx + thumb_w + 16
        draw.text((info_x, cy + 18), name, fill=(255, 255, 255, 255), font=font_card_tit)
        draw.line([(info_x, cy + 42), (cx + card_w - 14, cy + 42)], fill=(55, 65, 80, 255), width=1)

        by = cy + 54
        for b in bullets:
            draw.text((info_x, by), b, fill=(195, 205, 218, 255), font=font_card_desc)
            by += 22

        draw.text((info_x, cy + card_h - 26), "ESTADO: APROBADO 100% 3D", fill=col_accent, font=font_badge)

    sheet.save(output_path, "PNG")
    print(f"[BESTIARIO] Lamina Maestra generada exitosamente en: {output_path}")


# -------------------------------------------------------------------------
# FUNCIÓN PRINCIPAL DE EJECUCIÓN Y RENDER
# -------------------------------------------------------------------------
def main():
    print("=== INICIANDO GENERACIÓN OFICIAL BESTIARIO 10 ENTIDADES 3D ===")
    scene = reset_scene()
    col = create_collection("Bestiary_Official_10")
    mats = create_materials()

    print("Construyendo geometrías 3D fieles...")
    build_entity1_werewolf(col, mats)
    build_entity2_drone(col, mats)
    build_entity3_scrapper(col, mats)
    build_entity4_spider(col, mats)
    build_entity5_golem(col, mats)
    build_entity6_brute(col, mats)
    build_entity7_leech(col, mats)
    build_entity8_hound(col, mats)
    build_entity9_keeper(col, mats)
    build_entity10_creeper(col, mats)

    build_environment(col, mats)
    setup_lighting(col)
    cams = setup_all_cameras(col)

    bpy.ops.wm.save_as_mainfile(filepath=BLEND_FILE)
    print(f"Archivo .blend maestro guardado en: {BLEND_FILE}")

    render_files = {}

    # 1. Render Panorama General (2560 x 850)
    pan_cam = cams['Panorama']
    scene.camera = pan_cam
    scene.render.resolution_x = 2560
    scene.render.resolution_y = 850
    scene.render.resolution_percentage = 100
    
    pan_path = os.path.join(RENDERS_DIR, "Showcase_Bestiario_10_Entidades_Panorama.png")
    scene.render.filepath = pan_path
    print(f"Renderizando Panorama: {pan_path}...")
    bpy.ops.render.render(write_still=True)
    render_files['Panorama'] = pan_path
    shutil.copy2(pan_path, os.path.join(ARTIFACT_DIR, "Showcase_Bestiario_10_Entidades_Panorama.png"))

    # 2. Render de los 10 Close-Ups Individuales
    entity_names = {
        1: "Showcase_Bestiario_01_Mechanical_Werewolf.png",
        2: "Showcase_Bestiario_02_Auditor_Drone.png",
        3: "Showcase_Bestiario_03_Scrapper_Goblin.png",
        4: "Showcase_Bestiario_04_Ceiling_Spider_Bot.png",
        5: "Showcase_Bestiario_05_Cinder_Spirit_Golem.png",
        6: "Showcase_Bestiario_06_Charr_Brute.png",
        7: "Showcase_Bestiario_07_Plasma_Leech.png",
        8: "Showcase_Bestiario_08_Cyber_Hound_Scout.png",
        9: "Showcase_Bestiario_09_Furnace_Keeper.png",
        10:"Showcase_Bestiario_10_Vapor_Creeper.png"
    }

    scene.render.resolution_x = 1080
    scene.render.resolution_y = 1080

    for cid in range(1, 11):
        cam = cams[cid]
        scene.camera = cam
        out_name = entity_names[cid]
        out_path = os.path.join(RENDERS_DIR, out_name)
        scene.render.filepath = out_path
        print(f"Renderizando Close-Up Entidad {cid} ({out_name})...")
        bpy.ops.render.render(write_still=True)
        render_files[cid] = out_path
        shutil.copy2(out_path, os.path.join(ARTIFACT_DIR, out_name))

    # 3. Composición de Lámina Maestra 2.5K
    master_path = os.path.join(RENDERS_DIR, "Showcase_Bestiario_10_Entidades_Master.png")
    create_master_bestiary_sheet(render_files, master_path)
    shutil.copy2(master_path, os.path.join(ARTIFACT_DIR, "Showcase_Bestiario_10_Entidades_Master.png"))
    print("=== PROCESO DE BESTIARIO COMPLETADO CON ÉXITO ===")

if __name__ == "__main__":
    main()

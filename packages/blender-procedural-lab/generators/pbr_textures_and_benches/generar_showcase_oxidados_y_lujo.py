# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Generador Maestro de Showcases en Blender 5.2 LTS: Texturas Oxidadas y de Lujo
# Genera dos escenas completas con Shader Balls Pro V5, props contextuales estilizados,
# iluminación de estudio cinematográfica, Freestyle Lineart cómic y renders multi-ángulo.

import bpy
import bmesh
import math
import os
import sys
import shutil
from mathutils import Vector, Euler

PROJECT_ROOT = r"F:\Dev\Game"
RENDERS_DIR = os.path.join(PROJECT_ROOT, "Art", "Renders")
TEXTURES_MODULAR = os.path.join(PROJECT_ROOT, "Art", "Textures", "Modular")
ARTIFACT_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\b59ff04f-3c21-4ee5-94b0-8e8f899f8923"
BLEND_FILE_OXIDADO = os.path.join(PROJECT_ROOT, "Art", "Blender", "Showcase_Texturas_Oxidadas.blend")
BLEND_FILE_LUJO = os.path.join(PROJECT_ROOT, "Art", "Blender", "Showcase_Texturas_Lujo.blend")

os.makedirs(RENDERS_DIR, exist_ok=True)
os.makedirs(ARTIFACT_DIR, exist_ok=True)

R = math.radians

def reset_scene(style="derelict"):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if not bpy.data.scenes:
        bpy.data.scenes.new("Scene")
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.film_transparent = False
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'High Contrast'
    
    # Freestyle Lineart Cómic
    scene.render.use_freestyle = True
    rl = scene.view_layers["ViewLayer"]
    rl.use_freestyle = True
    rl.freestyle_settings.as_render_pass = False
    rl.freestyle_settings.crease_angle = math.radians(130.0)
    
    linesets = rl.freestyle_settings.linesets
    while linesets:
        linesets.remove(linesets[0])
    
    ls = linesets.new("ComicInkLine")
    ls.select_silhouette = True
    ls.select_border = True
    ls.select_crease = True
    ls.select_material_boundary = True
    
    linestyles = bpy.data.linestyles
    linestyle = linestyles.new("InkStyle")
    if style == "derelict":
        linestyle.color = (0.04, 0.03, 0.03)
        linestyle.thickness = 1.8
    else:
        linestyle.color = (0.06, 0.05, 0.04)
        linestyle.thickness = 1.4
    ls.linestyle = linestyle
    
    return scene

def create_pbr_toon_material(name, base_color_path, normal_path, orm_path, emissive_path=None, uv_scale=(1.0, 1.0)):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    node_out.location = (700, 0)
    
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (300, 0)
    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])
    
    coord_node = nodes.new(type='ShaderNodeTexCoord')
    coord_node.location = (-900, 0)
    
    mapping_node = nodes.new(type='ShaderNodeMapping')
    mapping_node.location = (-700, 0)
    mapping_node.inputs['Scale'].default_value = (uv_scale[0], uv_scale[1], 1.0)
    links.new(coord_node.outputs['UV'], mapping_node.inputs['Vector'])
    
    # BaseColor
    if os.path.exists(base_color_path):
        tex_bc = nodes.new(type='ShaderNodeTexImage')
        tex_bc.location = (-400, 300)
        tex_bc.image = bpy.data.images.load(base_color_path)
        links.new(mapping_node.outputs['Vector'], tex_bc.inputs['Vector'])
        links.new(tex_bc.outputs['Color'], node_bsdf.inputs['Base Color'])
    
    # ORM
    if os.path.exists(orm_path):
        tex_orm = nodes.new(type='ShaderNodeTexImage')
        tex_orm.location = (-400, 0)
        img_orm = bpy.data.images.load(orm_path)
        img_orm.colorspace_settings.name = 'Non-Color'
        tex_orm.image = img_orm
        links.new(mapping_node.outputs['Vector'], tex_orm.inputs['Vector'])
        
        sep_color = nodes.new(type='ShaderNodeSeparateColor')
        sep_color.location = (-120, 0)
        links.new(tex_orm.outputs['Color'], sep_color.inputs['Color'])
        links.new(sep_color.outputs['Green'], node_bsdf.inputs['Roughness'])
        links.new(sep_color.outputs['Blue'], node_bsdf.inputs['Metallic'])
    
    # Normal Map
    if os.path.exists(normal_path):
        tex_norm = nodes.new(type='ShaderNodeTexImage')
        tex_norm.location = (-400, -300)
        img_norm = bpy.data.images.load(normal_path)
        img_norm.colorspace_settings.name = 'Non-Color'
        tex_norm.image = img_norm
        links.new(mapping_node.outputs['Vector'], tex_norm.inputs['Vector'])
        
        norm_map = nodes.new(type='ShaderNodeNormalMap')
        norm_map.location = (-120, -300)
        norm_map.space = 'TANGENT'
        norm_map.inputs['Strength'].default_value = 1.3
        links.new(tex_norm.outputs['Color'], norm_map.inputs['Color'])
        links.new(norm_map.outputs['Normal'], node_bsdf.inputs['Normal'])
    
    # Emissive
    if emissive_path and os.path.exists(emissive_path):
        tex_emi = nodes.new(type='ShaderNodeTexImage')
        tex_emi.location = (-400, -600)
        tex_emi.image = bpy.data.images.load(emissive_path)
        links.new(mapping_node.outputs['Vector'], tex_emi.inputs['Vector'])
        links.new(tex_emi.outputs['Color'], node_bsdf.inputs['Emission Color'])
        node_bsdf.inputs['Emission Strength'].default_value = 4.0
        
    return mat

def create_pedestal_material(style="derelict"):
    mat = bpy.data.materials.new(name=f"M_Pedestal_{style}")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        if style == "derelict":
            bsdf.inputs['Base Color'].default_value = (0.08, 0.08, 0.09, 1.0)
            bsdf.inputs['Roughness'].default_value = 0.45
            bsdf.inputs['Metallic'].default_value = 0.85
        else:
            bsdf.inputs['Base Color'].default_value = (0.12, 0.11, 0.13, 1.0)
            bsdf.inputs['Roughness'].default_value = 0.18
            bsdf.inputs['Metallic'].default_value = 0.92
    return mat

def create_backdrop_material(style="derelict"):
    mat = bpy.data.materials.new(name=f"M_Backdrop_{style}")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        if style == "derelict":
            bsdf.inputs['Base Color'].default_value = (0.04, 0.04, 0.05, 1.0)
            bsdf.inputs['Roughness'].default_value = 0.92
            bsdf.inputs['Metallic'].default_value = 0.05
        else:
            bsdf.inputs['Base Color'].default_value = (0.05, 0.04, 0.06, 1.0)
            bsdf.inputs['Roughness'].default_value = 0.85
            bsdf.inputs['Metallic'].default_value = 0.10
    return mat

def create_core_material(style="derelict"):
    mat = bpy.data.materials.new(name=f"M_Core_{style}")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        if style == "derelict":
            bsdf.inputs['Base Color'].default_value = (0.85, 0.65, 0.22, 1.0) # Latón oscuro
            bsdf.inputs['Roughness'].default_value = 0.22
            bsdf.inputs['Metallic'].default_value = 0.95
        else:
            bsdf.inputs['Base Color'].default_value = (0.98, 0.84, 0.32, 1.0) # Oro 24k
            bsdf.inputs['Roughness'].default_value = 0.10
            bsdf.inputs['Metallic'].default_value = 1.0
    return mat

def create_plaque_material(style="derelict"):
    mat = bpy.data.materials.new(name=f"M_Plaque_{style}")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        if style == "derelict":
            bsdf.inputs['Base Color'].default_value = (0.75, 0.55, 0.18, 1.0)
            bsdf.inputs['Roughness'].default_value = 0.30
            bsdf.inputs['Metallic'].default_value = 0.90
        else:
            bsdf.inputs['Base Color'].default_value = (0.95, 0.80, 0.25, 1.0)
            bsdf.inputs['Roughness'].default_value = 0.15
            bsdf.inputs['Metallic'].default_value = 0.98
    return mat

def create_text_material():
    mat = bpy.data.materials.new(name="M_Text_Black")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.02, 0.02, 0.02, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.70
        bsdf.inputs['Metallic'].default_value = 0.05
    return mat

def build_pro_shader_ball(loc=(0, 0, 0), mat_outer=None, mat_core=None):
    x, y, z = loc
    radius = 0.58
    center_z = z + radius
    
    # 1. Esfera exterior con UVs nativas y corte frontal-derecho
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, segments=48, ring_count=24, location=(x, y, center_z))
    outer_obj = bpy.context.active_object
    outer_obj.name = f"ShaderBall_Outer_{x:.0f}"
    
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(outer_obj.data)
    verts_to_delete = [v for v in bm.verts if v.co.x > 0.04 and v.co.y < -0.04 and v.co.z > -0.22]
    bmesh.ops.delete(bm, geom=verts_to_delete, context='VERTS')
    bmesh.update_edit_mesh(outer_obj.data)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    outer_obj.rotation_euler = (0, 0, 0)
    
    mod_sol = outer_obj.modifiers.new("Solidify", 'SOLIDIFY')
    mod_sol.thickness = 0.042
    mod_sol.offset = -1.0
    
    mod_bev = outer_obj.modifiers.new("Bevel", 'BEVEL')
    mod_bev.width = 0.012
    mod_bev.segments = 2
    
    bpy.ops.object.shade_smooth()
    if mat_outer:
        outer_obj.data.materials.append(mat_outer)
        
    # 2. Núcleo interior reflectante
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=0.38, location=(x, y, center_z))
    core_obj = bpy.context.active_object
    core_obj.name = f"ShaderBall_Core_{x:.0f}"
    bpy.ops.object.shade_smooth()
    if mat_core:
        core_obj.data.materials.append(mat_core)
        
    # 3. Anillo giroscópico con inclinación de 14°
    bpy.ops.mesh.primitive_torus_add(major_radius=0.52, minor_radius=0.04, major_segments=36, minor_segments=12, location=(x, y, center_z))
    ring_obj = bpy.context.active_object
    ring_obj.name = f"ShaderBall_Ring_{x:.0f}"
    ring_obj.rotation_euler = (R(14), R(12), 0)
    bpy.ops.object.shade_smooth()
    if mat_core:
        ring_obj.data.materials.append(mat_core)
        
    # 4. Base cilíndrica de acople
    bpy.ops.mesh.primitive_cylinder_add(radius=0.40, depth=0.16, vertices=32, location=(x, y, z + 0.08))
    stand_obj = bpy.context.active_object
    stand_obj.name = f"ShaderBall_Stand_{x:.0f}"
    mod_bs = stand_obj.modifiers.new("Bevel", 'BEVEL')
    mod_bs.width = 0.02
    mod_bs.segments = 2
    bpy.ops.object.shade_smooth()
    if mat_core:
        stand_obj.data.materials.append(mat_core)
        
    return outer_obj

def build_station_pedestal(loc, style="derelict", mat_pedestal=None, mat_plaque=None, mat_text=None, title="STATION"):
    x, y, z = loc
    # Pedestal cúbico con bisel
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y, 0.25))
    ped = bpy.context.active_object
    ped.name = f"Pedestal_{x:.0f}"
    ped.scale = (1.50, 1.40, 0.50)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    mod_b = ped.modifiers.new("Bevel", 'BEVEL')
    mod_b.width = 0.03
    mod_b.segments = 2
    bpy.ops.object.shade_smooth()
    if mat_pedestal:
        ped.data.materials.append(mat_pedestal)
        
    # Placa frontal de latón/oro
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y - 0.71, 0.28))
    plaque = bpy.context.active_object
    plaque.name = f"Plaque_{x:.0f}"
    plaque.scale = (0.95, 0.02, 0.18)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    mod_bp = plaque.modifiers.new("Bevel", 'BEVEL')
    mod_bp.width = 0.008
    mod_bp.segments = 2
    bpy.ops.object.shade_smooth()
    if mat_plaque:
        plaque.data.materials.append(mat_plaque)
        
    # Texto 3D centrado
    bpy.ops.object.text_add(location=(x, y - 0.73, 0.24))
    txt = bpy.context.active_object
    txt.name = f"Text_{x:.0f}"
    txt.data.body = title
    txt.data.size = 0.065
    txt.data.align_x = 'CENTER'
    txt.data.align_y = 'CENTER'
    txt.data.extrude = 0.008
    txt.rotation_euler = (R(90), 0, 0)
    if mat_text:
        txt.data.materials.append(mat_text)
        
    return ped

# ==============================================================================
# PROPS CONTEXTUALES: SET OXIDADO / DERELICT
# ==============================================================================
def build_prop_derelict_1(loc, mat): # Mamparo desgastado
    x, y, z = loc
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y, z + 0.55))
    prop = bpy.context.active_object
    prop.name = "Prop_Rust_Bulkhead"
    prop.scale = (0.95, 0.30, 1.10)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    mod = prop.modifiers.new("Bevel", 'BEVEL')
    mod.width = 0.025
    mod.segments = 2
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.uv.cube_project()
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.shade_smooth()
    if mat:
        prop.data.materials.append(mat)
    return prop

def build_prop_derelict_2(loc, mat): # Placa blindada con impacto
    x, y, z = loc
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y, z + 0.55))
    prop = bpy.context.active_object
    prop.name = "Prop_Battered_Armor"
    prop.scale = (0.90, 0.35, 1.10)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    mod = prop.modifiers.new("Bevel", 'BEVEL')
    mod.width = 0.03
    mod.segments = 2
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.uv.cube_project()
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.shade_smooth()
    if mat:
        prop.data.materials.append(mat)
    return prop

def build_prop_derelict_3(loc, mat): # Tubería con fuga ácida
    x, y, z = loc
    bpy.ops.mesh.primitive_cylinder_add(radius=0.28, depth=1.10, vertices=32, location=(x, y, z + 0.55))
    prop = bpy.context.active_object
    prop.name = "Prop_Acid_Pipe"
    mod = prop.modifiers.new("Bevel", 'BEVEL')
    mod.width = 0.02
    mod.segments = 2
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.uv.cylinder_project()
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.shade_smooth()
    if mat:
        prop.data.materials.append(mat)
    return prop

def build_prop_derelict_4(loc, mat): # Pasarela de rejilla carcomida
    x, y, z = loc
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y, z + 0.55))
    prop = bpy.context.active_object
    prop.name = "Prop_Rusted_Grating"
    prop.scale = (0.95, 0.85, 0.22)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    mod = prop.modifiers.new("Bevel", 'BEVEL')
    mod.width = 0.02
    mod.segments = 2
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.uv.cube_project()
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.shade_smooth()
    if mat:
        prop.data.materials.append(mat)
    return prop

def build_prop_derelict_5(loc, mat): # Escudo térmico con plasma fundido
    x, y, z = loc
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y, z + 0.55))
    prop = bpy.context.active_object
    prop.name = "Prop_Plasma_Shield"
    prop.scale = (0.95, 0.35, 1.10)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    mod = prop.modifiers.new("Bevel", 'BEVEL')
    mod.width = 0.025
    mod.segments = 2
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.uv.cube_project()
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.shade_smooth()
    if mat:
        prop.data.materials.append(mat)
    return prop

# ==============================================================================
# PROPS CONTEXTUALES: SET LUJO / ART DÉCO CELESTIA
# ==============================================================================
def build_prop_luxury_1(loc, mat): # Plinto monumental de mármol Carrara
    x, y, z = loc
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y, z + 0.55))
    prop = bpy.context.active_object
    prop.name = "Prop_Marble_Plinth"
    prop.scale = (0.85, 0.85, 1.10)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    mod = prop.modifiers.new("Bevel", 'BEVEL')
    mod.width = 0.04
    mod.segments = 3
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.uv.cube_project()
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.shade_smooth()
    if mat:
        prop.data.materials.append(mat)
    return prop

def build_prop_luxury_2(loc, mat): # Boiserie de nogal vertical
    x, y, z = loc
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y, z + 0.60))
    prop = bpy.context.active_object
    prop.name = "Prop_Walnut_Boiserie"
    prop.scale = (0.95, 0.25, 1.20)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    mod = prop.modifiers.new("Bevel", 'BEVEL')
    mod.width = 0.03
    mod.segments = 3
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.uv.cube_project()
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.shade_smooth()
    if mat:
        prop.data.materials.append(mat)
    return prop

def build_prop_luxury_3(loc, mat): # Panel arquitectónico de latón solar
    x, y, z = loc
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y, z + 0.60))
    prop = bpy.context.active_object
    prop.name = "Prop_ArtDeco_Screen"
    prop.scale = (0.95, 0.25, 1.20)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    mod = prop.modifiers.new("Bevel", 'BEVEL')
    mod.width = 0.025
    mod.segments = 3
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.uv.cube_project()
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.shade_smooth()
    if mat:
        prop.data.materials.append(mat)
    return prop

def build_prop_luxury_4(loc, mat): # Respaldo curvo capitoné de butaca
    x, y, z = loc
    bpy.ops.mesh.primitive_cylinder_add(radius=0.48, depth=1.10, vertices=32, location=(x, y, z + 0.55))
    prop = bpy.context.active_object
    prop.name = "Prop_Chesterfield_Back"
    prop.scale = (0.95, 0.60, 1.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    mod = prop.modifiers.new("Bevel", 'BEVEL')
    mod.width = 0.03
    mod.segments = 3
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.uv.cylinder_project()
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.shade_smooth()
    if mat:
        prop.data.materials.append(mat)
    return prop

def build_prop_luxury_5(loc, mat): # Pantalla de celosía de vidrio ahumado
    x, y, z = loc
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y, z + 0.60))
    prop = bpy.context.active_object
    prop.name = "Prop_Smoked_Lattice_Screen"
    prop.scale = (0.95, 0.20, 1.20)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    mod = prop.modifiers.new("Bevel", 'BEVEL')
    mod.width = 0.02
    mod.segments = 3
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.uv.cube_project()
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.shade_smooth()
    if mat:
        prop.data.materials.append(mat)
    return prop

# ==============================================================================
# CONSTRUCCIÓN DE ESTUDIO Y ESCENARIO
# ==============================================================================
def build_studio_environment(style="derelict"):
    mat_back = create_backdrop_material(style)
    # Suelo infinito curvo de ciclorama
    bpy.ops.mesh.primitive_plane_add(size=36.0, location=(0, 2.0, 0.0))
    floor = bpy.context.active_object
    floor.name = "Studio_Floor"
    floor.data.materials.append(mat_back)
    
    # Pared de fondo
    bpy.ops.mesh.primitive_plane_add(size=36.0, location=(0, 6.0, 4.0))
    wall = bpy.context.active_object
    wall.name = "Studio_Wall"
    wall.rotation_euler = (R(90), 0, 0)
    wall.data.materials.append(mat_back)
    
    # Iluminación de estudio
    if style == "derelict":
        # Luz clave sombría industrial
        bpy.ops.object.light_add(type='SUN', location=(3, -7, 10))
        sun = bpy.context.active_object
        sun.data.energy = 4.2
        sun.data.color = (0.85, 0.88, 0.95)
        sun.rotation_euler = (R(48), R(12), R(-25))
        
        # Luces de relleno ámbar de advertencia en cada estación
        for lx in [-5.2, -2.6, 0.0, 2.6, 5.2]:
            bpy.ops.object.light_add(type='POINT', location=(lx, -2.2, 2.8))
            fill = bpy.context.active_object
            fill.data.energy = 140.0
            fill.data.color = (1.0, 0.65, 0.25)
            
        # Luz de contra azul fría (Rim light)
        bpy.ops.object.light_add(type='SUN', location=(-3, 7, 6))
        rim = bpy.context.active_object
        rim.data.energy = 3.0
        rim.data.color = (0.45, 0.70, 1.0)
        rim.rotation_euler = (R(-40), R(-12), R(160))
    else: # Luxury
        # Luz clave champagne 3000K
        bpy.ops.object.light_add(type='SUN', location=(3, -7, 11))
        sun = bpy.context.active_object
        sun.data.energy = 5.0
        sun.data.color = (1.0, 0.94, 0.82)
        sun.rotation_euler = (R(45), R(12), R(-20))
        
        # Focos de relleno cálidos y elegantes en cada estación
        for lx in [-5.2, -2.6, 0.0, 2.6, 5.2]:
            bpy.ops.object.light_add(type='SPOT', location=(lx, -2.8, 3.5))
            spot = bpy.context.active_object
            spot.data.energy = 200.0
            spot.data.color = (1.0, 0.90, 0.75)
            spot.data.spot_size = R(55)
            spot.data.spot_blend = 0.4
            spot.rotation_euler = (R(45), 0, 0)
            
        # Rim light dorada suave
        bpy.ops.object.light_add(type='SUN', location=(-3, 7, 7))
        rim = bpy.context.active_object
        rim.data.energy = 2.5
        rim.data.color = (1.0, 0.88, 0.65)
        rim.rotation_euler = (R(-40), R(-10), R(150))

def setup_cameras(station_x_coords, prefix="Oxidados"):
    # 1. Cámara Maestra Panorámica (encuadre completo de las 5 estaciones)
    bpy.ops.object.camera_add(location=(0, -10.2, 3.0))
    cam_master = bpy.context.active_object
    cam_master.name = f"Cam_Master_{prefix}"
    cam_master.data.lens = 28.0
    cam_master.rotation_euler = (R(78), 0, 0)
    
    close_cams = []
    # 2. Cámaras de primer plano para cada estación (Shader Ball + Prop + Placa)
    for i, x in enumerate(station_x_coords, start=1):
        bpy.ops.object.camera_add(location=(x, -3.9, 1.35))
        cam = bpy.context.active_object
        cam.name = f"Cam_Station_{i}_{prefix}"
        cam.data.lens = 46.0
        cam.rotation_euler = (R(80), 0, 0)
        close_cams.append(cam)
        
    return cam_master, close_cams

# ==============================================================================
# PIPELINE COMPLETO DE SHOWROOMS
# ==============================================================================
def render_showcase(style="derelict"):
    prefix = "Oxidados" if style == "derelict" else "Lujo"
    blend_path = BLEND_FILE_OXIDADO if style == "derelict" else BLEND_FILE_LUJO
    print(f"\n{'='*70}\nCONSTRUYENDO SHOWCASE EN BLENDER: SET {prefix.upper()}\n{'='*70}")
    
    scene = reset_scene(style=style)
    build_studio_environment(style=style)
    
    mat_ped = create_pedestal_material(style)
    mat_core = create_core_material(style)
    mat_plaque = create_plaque_material(style)
    mat_text = create_text_material()
    
    station_x = [-5.2, -2.6, 0.0, 2.6, 5.2]
    
    if style == "derelict":
        packs = [
            ("T_Derelict_Rust_Plates", "01. DERELICT RUST PLATES", build_prop_derelict_1),
            ("T_Battered_Armor_Impacts", "02. BATTERED ARMOR IMPACTS", build_prop_derelict_2),
            ("T_Corroded_Acid_Pipes", "03. CORRODED ACID PIPES", build_prop_derelict_3),
            ("T_Decayed_Rusted_Grating", "04. DECAYED RUSTED GRATING", build_prop_derelict_4),
            ("T_Scorched_Plasma_Slag", "05. SCORCHED PLASMA SLAG", build_prop_derelict_5),
        ]
    else:
        packs = [
            ("T_Luxury_Marble_Gold_Inlay", "01. CARRARA MARBLE & GOLD", build_prop_luxury_1),
            ("T_Luxury_Walnut_Wood_Panels", "02. NOBLE WALNUT BOISERIE", build_prop_luxury_2),
            ("T_Luxury_ArtDeco_Gilded_Brass", "03. ART DÉCO GILDED BRASS", build_prop_luxury_3),
            ("T_Luxury_Quilted_Velvet_Leather", "04. QUILTED VELVET LEATHER", build_prop_luxury_4),
            ("T_Luxury_Smoked_Glass_Lattice", "05. SMOKED GLASS LATTICE", build_prop_luxury_5),
        ]
        
    for i, (tex_name, title, prop_func) in enumerate(packs):
        x = station_x[i]
        bc_path = os.path.join(TEXTURES_MODULAR, f"{tex_name}_BaseColor.png")
        norm_path = os.path.join(TEXTURES_MODULAR, f"{tex_name}_Normal.png")
        orm_path = os.path.join(TEXTURES_MODULAR, f"{tex_name}_ORM.png")
        emi_path = os.path.join(TEXTURES_MODULAR, f"{tex_name}_Emissive.png")
        
        mat = create_pbr_toon_material(f"M_{tex_name}", bc_path, norm_path, orm_path, emi_path)
        
        # 1. Pedestal y placa
        build_station_pedestal((x, 0, 0), style=style, mat_pedestal=mat_ped, mat_plaque=mat_plaque, mat_text=mat_text, title=title)
        
        # 2. Shader Ball Pro V5
        build_pro_shader_ball((x - 0.40, 0.05, 0.50), mat_outer=mat, mat_core=mat_core)
        
        # 3. Prop Contextual
        prop_func((x + 0.42, 0.15, 0.50), mat)
        
    # Cámaras
    cam_master, close_cams = setup_cameras(station_x, prefix=prefix)
    
    # Guardar archivo .blend oficial
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"  [OK] Guardado archivo Blender: {blend_path}")
    
    # Render Master Panorama (2560x1440)
    print(f"  [RENDER] Renderizando Panorama Maestro ({prefix})...")
    scene.camera = cam_master
    scene.render.resolution_x = 2560
    scene.render.resolution_y = 1440
    master_render_path = os.path.join(RENDERS_DIR, f"Showcase_Texturas_{prefix}_Panorama.png")
    scene.render.filepath = master_render_path
    bpy.ops.render.render(write_still=True)
    shutil.copy(master_render_path, os.path.join(ARTIFACT_DIR, os.path.basename(master_render_path)))
    print(f"  [OK] Guardado render panorama: {master_render_path}")
    
    # Renders Close-Up (1080p)
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    for i, cam in enumerate(close_cams, start=1):
        print(f"  [RENDER] Renderizando Close-Up Estación {i} ({prefix})...")
        scene.camera = cam
        cup_path = os.path.join(RENDERS_DIR, f"CloseUp_{prefix}_Estacion_{i}.png")
        scene.render.filepath = cup_path
        bpy.ops.render.render(write_still=True)
        shutil.copy(cup_path, os.path.join(ARTIFACT_DIR, os.path.basename(cup_path)))
        print(f"  [OK] Guardado close-up: {cup_path}")

def main():
    mode = "all"
    if "--mode" in sys.argv:
        idx = sys.argv.index("--mode")
        if idx + 1 < len(sys.argv):
            mode = sys.argv[idx + 1]
            
    if mode in ["all", "derelict"]:
        render_showcase("derelict")
    if mode in ["all", "luxury"]:
        render_showcase("luxury")

if __name__ == "__main__":
    main()

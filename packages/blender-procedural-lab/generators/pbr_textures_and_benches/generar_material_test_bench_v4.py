# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Generador Maestro del Banco de Pruebas de Materiales V4 (Material Test Bench) - Astra Hazard
# Blender 5.2 LTS - Corte 3D frontal-derecho visible, smooth shading en mallas, UVs proyectadas cúbicamente y composición óptima.

import bpy
import bmesh
import math
import os
import shutil
from mathutils import Vector, Euler

PROJECT_ROOT = r"F:\Dev\Game"
RENDERS_DIR = os.path.join(PROJECT_ROOT, "Art", "Renders")
TEXTURES_MODULAR = os.path.join(PROJECT_ROOT, "Art", "Textures", "Modular")
ARTIFACT_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\b59ff04f-3c21-4ee5-94b0-8e8f899f8923"
BLEND_FILE = os.path.join(PROJECT_ROOT, "Art", "Blender", "Material_Test_Bench.blend")

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
    linestyle.color = (0.04, 0.03, 0.03)
    linestyle.thickness = 1.8
    ls.linestyle = linestyle
    
    return scene

def create_pbr_toon_material(name, base_color_path, normal_path, orm_path, emissive_path=None, uv_scale=(1.0, 1.0)):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    node_out.location = (650, 0)
    
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (250, 0)
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

def create_pedestal_material():
    mat = bpy.data.materials.new(name="M_Pedestal_Studio")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.07, 0.07, 0.08, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.35
        bsdf.inputs['Metallic'].default_value = 0.85
    return mat

def create_backdrop_material():
    mat = bpy.data.materials.new(name="M_Backdrop_Studio")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.05, 0.05, 0.06, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.90
        bsdf.inputs['Metallic'].default_value = 0.02
    return mat

def create_brass_core_material():
    mat = bpy.data.materials.new(name="M_Core_Brass")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.95, 0.76, 0.22, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.15
        bsdf.inputs['Metallic'].default_value = 0.98
    return mat

def create_plaque_material():
    mat = bpy.data.materials.new(name="M_Plaque_Brass")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.85, 0.65, 0.18, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.28
        bsdf.inputs['Metallic'].default_value = 0.92
    return mat

def create_text_material():
    mat = bpy.data.materials.new(name="M_Text_Black")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.04, 0.04, 0.04, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.60
        bsdf.inputs['Metallic'].default_value = 0.10
    return mat

# ==============================================================================
# MODELADO V4: SHADER BALL CON CORTE FRONTAL-DERECHO VISIBLE Y SUAVE
# ==============================================================================
def build_pro_shader_ball_v4(loc=(0, 0, 0), mat_outer=None, mat_core=None):
    x, y, z = loc
    radius = 0.58
    center_z = z + radius # z = 0.50 + 0.58 = 1.08m
    
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=24, radius=radius)
    
    # Cortar cuadrante FRONTAL-DERECHO visible a la cámara (x > 0.08 y y < -0.08)
    verts_to_delete = []
    for v in bm.verts:
        if v.co.x > 0.08 and v.co.y < -0.08 and v.co.z > -0.18:
            verts_to_delete.append(v)
    bmesh.ops.delete(bm, geom=verts_to_delete, context='VERTS')
    
    mesh_outer = bpy.data.meshes.new("ShaderBall_Outer_Mesh")
    bm.to_mesh(mesh_outer)
    bm.free()
    
    # Smooth shading en la malla
    for p in mesh_outer.polygons:
        p.use_smooth = True
        
    outer_obj = bpy.data.objects.new("ShaderBall_Outer", mesh_outer)
    outer_obj.location = (x, y, center_z)
    bpy.context.scene.collection.objects.link(outer_obj)
    
    mod_sol = outer_obj.modifiers.new("Solidify", 'SOLIDIFY')
    mod_sol.thickness = 0.042
    mod_sol.offset = -1.0
    
    mod_bev = outer_obj.modifiers.new("Bevel", 'BEVEL')
    mod_bev.width = 0.012
    mod_bev.segments = 2
    
    bpy.context.view_layer.objects.active = outer_obj
    bpy.ops.object.shade_smooth()
    
    # UV Unwrap cúbico para envolver textura de forma limpia
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.uv.cube_project(cube_size=1.2)
    bpy.ops.object.mode_set(mode='OBJECT')
    
    if mat_outer:
        outer_obj.data.materials.append(mat_outer)
        
    # Núcleo metálico reflectante
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=0.38, location=(x, y, center_z))
    core_obj = bpy.context.active_object
    core_obj.name = "ShaderBall_Core"
    bpy.ops.object.shade_smooth()
    if mat_core:
        core_obj.data.materials.append(mat_core)
        
    # Anillo collar de latón
    bpy.ops.mesh.primitive_torus_add(major_radius=0.52, minor_radius=0.04, major_segments=36, minor_segments=12, location=(x, y, center_z))
    ring_obj = bpy.context.active_object
    ring_obj.name = "ShaderBall_Ring"
    bpy.ops.object.shade_smooth()
    if mat_core:
        ring_obj.data.materials.append(mat_core)
        
    # Base de acople descansando firmemente a z = 0.50
    bpy.ops.mesh.primitive_cylinder_add(radius=0.40, depth=0.16, vertices=32, location=(x, y, z + 0.08))
    stand_obj = bpy.context.active_object
    stand_obj.name = "ShaderBall_Stand"
    mod_bs = stand_obj.modifiers.new("Bevel", 'BEVEL')
    mod_bs.width = 0.02
    mod_bs.segments = 2
    bpy.ops.object.shade_smooth()
    if mat_core:
        stand_obj.data.materials.append(mat_core)
        
    return outer_obj

# ==============================================================================
# PROPS CONTEXTUALES MODULARES
# ==============================================================================
def build_station1_modular_wall(loc, mat):
    x, y, z = loc
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y, z + 0.55))
    wall = bpy.context.active_object
    wall.name = "Prop_Modular_Wall"
    wall.scale = (0.95, 0.30, 1.10)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    mod_b = wall.modifiers.new("Bevel", 'BEVEL')
    mod_b.width = 0.025
    mod_b.segments = 2
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.uv.cube_project()
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.shade_smooth()
    if mat:
        wall.data.materials.append(mat)
    return wall

def build_station2_ibeam(loc, mat):
    x, y, z = loc
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y, z + 0.55))
    block = bpy.context.active_object
    block.name = "Prop_Armor_Bulkhead"
    block.scale = (0.85, 0.40, 1.10)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    mod_b = block.modifiers.new("Bevel", 'BEVEL')
    mod_b.width = 0.03
    mod_b.segments = 2
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.uv.cube_project()
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.shade_smooth()
    if mat:
        block.data.materials.append(mat)
    return block

def build_station3_grate_platform(loc, mat):
    x, y, z = loc
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y, z + 0.55))
    plat = bpy.context.active_object
    plat.name = "Prop_Grate_Platform"
    plat.scale = (0.95, 0.85, 0.25)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    mod_b = plat.modifiers.new("Bevel", 'BEVEL')
    mod_b.width = 0.02
    mod_b.segments = 2
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.uv.cube_project()
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.shade_smooth()
    if mat:
        plat.data.materials.append(mat)
        
    for px in [-0.4, 0.4]:
        for py in [-0.35, 0.35]:
            bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.45, vertices=16, location=(x + px, y + py, z + 0.23))
            leg = bpy.context.active_object
            leg.name = "Grate_Leg"
            bpy.ops.object.shade_smooth()
            if mat:
                leg.data.materials.append(mat)
    return plat

def build_station4_concrete_pillar(loc, mat):
    x, y, z = loc
    bpy.ops.mesh.primitive_cylinder_add(radius=0.52, depth=1.10, vertices=8, location=(x, y, z + 0.55))
    pillar = bpy.context.active_object
    pillar.name = "Prop_Concrete_Pillar"
    mod_b = pillar.modifiers.new("Bevel", 'BEVEL')
    mod_b.width = 0.035
    mod_b.segments = 2
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.uv.cube_project()
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.shade_smooth()
    if mat:
        pillar.data.materials.append(mat)
    return pillar

def build_station5_control_console(loc, mat):
    x, y, z = loc
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y, z + 0.48))
    console = bpy.context.active_object
    console.name = "Prop_Console_Body"
    console.scale = (0.90, 0.60, 0.95)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    mod_b = console.modifiers.new("Bevel", 'BEVEL')
    mod_b.width = 0.025
    mod_b.segments = 2
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.uv.cube_project()
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.shade_smooth()
    if mat:
        console.data.materials.append(mat)
        
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y + 0.08, z + 0.88))
    panel = bpy.context.active_object
    panel.name = "Prop_Console_ScreenPanel"
    panel.scale = (0.82, 0.45, 0.22)
    panel.rotation_euler = (R(25), 0, 0)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    mod_bp = panel.modifiers.new("Bevel", 'BEVEL')
    mod_bp.width = 0.02
    mod_bp.segments = 2
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.uv.cube_project()
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.shade_smooth()
    if mat:
        panel.data.materials.append(mat)
    return console

def build_sample_tablet(loc=(0, 0, 0), mat=None):
    x, y, z = loc
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y, z + 0.46))
    tablet = bpy.context.active_object
    tablet.name = "SampleTablet"
    tablet.scale = (0.85, 0.06, 0.85)
    tablet.rotation_euler = (R(30), 0, 0)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    mod_b = tablet.modifiers.new("Bevel", 'BEVEL')
    mod_b.width = 0.02
    mod_b.segments = 2
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.uv.cube_project()
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.shade_smooth()
    if mat:
        tablet.data.materials.append(mat)
    return tablet

def build_station_pedestal(x=0.0, name_str="01. TRIM INDUSTRIAL", mat_pedestal=None, mat_plaque=None, mat_text=None):
    # Plinto inferior (z: 0..0.22)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, 0, 0.11))
    base1 = bpy.context.active_object
    base1.name = f"Pedestal_Base_{x}"
    base1.scale = (3.6, 2.4, 0.22)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    mod_b = base1.modifiers.new("Bevel", 'BEVEL')
    mod_b.width = 0.03
    mod_b.segments = 2
    if mat_pedestal:
        base1.data.materials.append(mat_pedestal)
        
    # Columna central (z: 0.22..0.50)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.55, depth=0.28, vertices=32, location=(x, -0.15, 0.36))
    col = bpy.context.active_object
    col.name = f"Pedestal_Col_{x}"
    mod_bc = col.modifiers.new("Bevel", 'BEVEL')
    mod_bc.width = 0.02
    mod_bc.segments = 2
    if mat_pedestal:
        col.data.materials.append(mat_pedestal)
        
    # Placa de identificación frontal de latón
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, -1.21, 0.12))
    plaque = bpy.context.active_object
    plaque.name = f"Plaque_{x}"
    plaque.scale = (1.5, 0.04, 0.14)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    mod_bp = plaque.modifiers.new("Bevel", 'BEVEL')
    mod_bp.width = 0.015
    mod_bp.segments = 2
    if mat_plaque:
        plaque.data.materials.append(mat_plaque)
        
    # Texto 3D centrado verticalmente en la placa
    bpy.ops.object.text_add(location=(x, -1.24, 0.12))
    txt_obj = bpy.context.active_object
    txt_obj.name = f"Text_{x}"
    txt_obj.data.body = name_str
    txt_obj.data.size = 0.075
    txt_obj.data.extrude = 0.012
    txt_obj.data.align_x = 'CENTER'
    txt_obj.data.align_y = 'CENTER'
    txt_obj.rotation_euler = (R(90), 0, 0)
    if mat_text:
        txt_obj.data.materials.append(mat_text)
        
    return base1

def build_studio_environment(mat_back):
    bm = bmesh.new()
    v1 = bm.verts.new((-24.0, -12.0, 0.0))
    v2 = bm.verts.new((24.0, -12.0, 0.0))
    v3 = bm.verts.new((24.0, 5.0, 0.0))
    v4 = bm.verts.new((-24.0, 5.0, 0.0))
    bm.faces.new([v1, v2, v3, v4])
    
    prev_v_left, prev_v_right = v4, v3
    curve_pts = [(5.5, 0.4), (6.5, 1.2), (7.5, 2.5), (8.2, 4.5), (8.6, 7.5), (8.8, 11.0)]
    for y_pos, z_pos in curve_pts:
        vl = bm.verts.new((-24.0, y_pos, z_pos))
        vr = bm.verts.new((24.0, y_pos, z_pos))
        bm.faces.new([prev_v_left, prev_v_right, vr, vl])
        prev_v_left = vl
        prev_v_right = vr
        
    mesh = bpy.data.meshes.new("Studio_Backdrop_Mesh")
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new("Studio_Backdrop", mesh)
    bpy.context.scene.collection.objects.link(obj)
    mod_sub = obj.modifiers.new("Subsurf", 'SUBSURF')
    mod_sub.levels = 2
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.shade_smooth()
    if mat_back:
        obj.data.materials.append(mat_back)
    return obj

def setup_studio_lighting():
    bpy.ops.object.light_add(type='SUN', location=(10.0, -12.0, 14.0))
    sun = bpy.context.active_object
    sun.name = "Key_Sun"
    sun.data.energy = 6.8
    sun.data.color = (1.0, 0.96, 0.90)
    sun.rotation_euler = (R(48), R(14), R(-28))
    
    bpy.ops.object.light_add(type='AREA', location=(0.0, 5.2, 6.8))
    rim = bpy.context.active_object
    rim.name = "Rim_Cyan"
    rim.data.shape = 'RECTANGLE'
    rim.data.size = 32.0
    rim.data.size_y = 5.0
    rim.data.energy = 3200.0
    rim.data.color = (0.35, 0.85, 1.0)
    rim.rotation_euler = (R(-55), 0, 0)
    
    bpy.ops.object.light_add(type='AREA', location=(0.0, -8.5, 1.8))
    fill = bpy.context.active_object
    fill.name = "Fill_Orange"
    fill.data.shape = 'RECTANGLE'
    fill.data.size = 28.0
    fill.data.size_y = 3.0
    fill.data.energy = 650.0
    fill.data.color = (1.0, 0.70, 0.40)
    fill.rotation_euler = (R(32), 0, 0)

def create_camera(name, loc, rot, fov=45.0):
    cam_data = bpy.data.cameras.new(name=name)
    cam_data.lens_unit = 'FOV'
    cam_data.angle = math.radians(fov)
    cam_obj = bpy.data.objects.new(name=name, object_data=cam_data)
    cam_obj.location = loc
    cam_obj.rotation_euler = rot
    bpy.context.scene.collection.objects.link(cam_obj)
    return cam_obj

# ==============================================================================
# PIPELINE MAESTRO V4
# ==============================================================================
def main():
    print("=== INICIANDO CONSTRUCCIÓN MATERIAL TEST BENCH V4 ===")
    scene = reset_scene()
    
    mat_pedestal = create_pedestal_material()
    mat_backdrop = create_backdrop_material()
    mat_core = create_brass_core_material()
    mat_plaque = create_plaque_material()
    mat_text = create_text_material()
    
    build_studio_environment(mat_backdrop)
    setup_studio_lighting()
    
    stations = [
        {
            "name": "M_PBR_Trim_Industrial",
            "station_name": "01. TRIM INDUSTRIAL",
            "x": -8.0,
            "bc": os.path.join(TEXTURES_MODULAR, "T_Trim_Industrial_BaseColor.png"),
            "norm": os.path.join(TEXTURES_MODULAR, "T_Trim_Industrial_Normal.png"),
            "orm": os.path.join(TEXTURES_MODULAR, "T_Trim_Industrial_ORM.png"),
            "emi": os.path.join(TEXTURES_MODULAR, "T_Trim_Industrial_Emissive.png"),
            "cam_name": "Cam_Trim_Industrial",
            "prop_builder": build_station1_modular_wall
        },
        {
            "name": "M_PBR_Steel_Plates",
            "station_name": "02. STEEL PLATES",
            "x": -4.0,
            "bc": os.path.join(TEXTURES_MODULAR, "T_Steel_Plates_BaseColor.png"),
            "norm": os.path.join(TEXTURES_MODULAR, "T_Steel_Plates_Normal.png"),
            "orm": os.path.join(TEXTURES_MODULAR, "T_Steel_Plates_ORM.png"),
            "emi": os.path.join(TEXTURES_MODULAR, "T_Steel_Plates_Emissive.png"),
            "cam_name": "Cam_Steel_Plates",
            "prop_builder": build_station2_ibeam
        },
        {
            "name": "M_PBR_Grating_Walkway",
            "station_name": "03. GRATING WALKWAY",
            "x": 0.0,
            "bc": os.path.join(TEXTURES_MODULAR, "T_Grating_Walkway_BaseColor.png"),
            "norm": os.path.join(TEXTURES_MODULAR, "T_Grating_Walkway_Normal.png"),
            "orm": os.path.join(TEXTURES_MODULAR, "T_Grating_Walkway_ORM.png"),
            "emi": os.path.join(TEXTURES_MODULAR, "T_Grating_Walkway_Emissive.png"),
            "cam_name": "Cam_Grating_Walkway",
            "prop_builder": build_station3_grate_platform
        },
        {
            "name": "M_PBR_Concrete_Factory",
            "station_name": "04. CONCRETE FACTORY",
            "x": 4.0,
            "bc": os.path.join(TEXTURES_MODULAR, "T_Concrete_Factory_BaseColor.png"),
            "norm": os.path.join(TEXTURES_MODULAR, "T_Concrete_Factory_Normal.png"),
            "orm": os.path.join(TEXTURES_MODULAR, "T_Concrete_Factory_ORM.png"),
            "emi": os.path.join(TEXTURES_MODULAR, "T_Concrete_Factory_Emissive.png"),
            "cam_name": "Cam_Concrete_Factory",
            "prop_builder": build_station4_concrete_pillar
        },
        {
            "name": "M_PBR_Props_Machinery",
            "station_name": "05. PROPS MACHINERY",
            "x": 8.0,
            "bc": os.path.join(TEXTURES_MODULAR, "T_Props_Machinery_BaseColor.png"),
            "norm": os.path.join(TEXTURES_MODULAR, "T_Props_Machinery_Normal.png"),
            "orm": os.path.join(TEXTURES_MODULAR, "T_Props_Machinery_ORM.png"),
            "emi": os.path.join(TEXTURES_MODULAR, "T_Props_Machinery_Emissive.png"),
            "cam_name": "Cam_Props_Machinery",
            "prop_builder": build_station5_control_console
        }
    ]
    
    cameras = {}
    
    for cfg in stations:
        mat = create_pbr_toon_material(
            name=cfg["name"],
            base_color_path=cfg["bc"],
            normal_path=cfg["norm"],
            orm_path=cfg["orm"],
            emissive_path=cfg["emi"]
        )
        x = cfg["x"]
        
        build_station_pedestal(x=x, name_str=cfg["station_name"], mat_pedestal=mat_pedestal, mat_plaque=mat_plaque, mat_text=mat_text)
        build_pro_shader_ball_v4(loc=(x, -0.15, 0.50), mat_outer=mat, mat_core=mat_core)
        cfg["prop_builder"](loc=(x - 1.10, 0.25, 0.22), mat=mat)
        build_sample_tablet(loc=(x + 1.10, 0.25, 0.22), mat=mat)
        
        # Cámara focal V4
        cam = create_camera(
            name=cfg["cam_name"],
            loc=(x, -5.5, 1.55),
            rot=(R(78), 0, 0),
            fov=48.0
        )
        cameras[cfg["cam_name"]] = cam
        
    # Cámara panorámica V4: Y=-15.0m, Z=3.5m, FOV=70°
    cam_master = create_camera(
        name="Cam_Master_Panorama",
        loc=(0.0, -15.0, 3.5),
        rot=(R(78), 0, 0),
        fov=70.0
    )
    cameras["Cam_Master_Panorama"] = cam_master
    
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_FILE)
    print(f"[OK] Proyecto guardado: {BLEND_FILE}")
    
    # -------------------------------------------------------------
    # RENDERS V4
    # -------------------------------------------------------------
    # 1. Panorama Master (2560x1440)
    scene.camera = cam_master
    scene.render.resolution_x = 2560
    scene.render.resolution_y = 1440
    master_render_path = os.path.join(RENDERS_DIR, "Showcase_Material_Test_Bench_Master.png")
    scene.render.filepath = master_render_path
    print("Renderizando Panorama V4 2560x1440...")
    bpy.ops.render.render(write_still=True)
    shutil.copy(master_render_path, os.path.join(ARTIFACT_DIR, "Showcase_Material_Test_Bench_Master.png"))
    print(f"[OK] Renderizado: {master_render_path}")
    
    # 2. Planos Focales Individuales V4 (1920x1080)
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    
    render_targets = [
        ("Cam_Trim_Industrial", "Showcase_Material_Trim_Industrial.png"),
        ("Cam_Steel_Plates", "Showcase_Material_Steel_Plates.png"),
        ("Cam_Grating_Walkway", "Showcase_Material_Grating_Walkway.png"),
        ("Cam_Concrete_Factory", "Showcase_Material_Concrete_Factory.png"),
        ("Cam_Props_Machinery", "Showcase_Material_Props_Machinery.png")
    ]
    
    for cam_name, file_name in render_targets:
        scene.camera = cameras[cam_name]
        out_path = os.path.join(RENDERS_DIR, file_name)
        scene.render.filepath = out_path
        print(f"Renderizando close-up V4 {file_name}...")
        bpy.ops.render.render(write_still=True)
        shutil.copy(out_path, os.path.join(ARTIFACT_DIR, file_name))
        print(f"[OK] Renderizado: {out_path}")
        
    print("=== TODOS LOS RENDERS V4 DEL MATERIAL TEST BENCH COMPLETADOS ===")

if __name__ == "__main__":
    main()

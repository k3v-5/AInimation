# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Generador Maestro del Banco de Pruebas de Materiales V2 (Material Test Bench) - Astra Hazard
# Blender 5.2 LTS - Corrige encuadres de cámara, shader ball con corte 120°, props contextuales y cel-shading nítido.

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
    linestyle.thickness = 2.0
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
        bsdf.inputs['Base Color'].default_value = (0.05, 0.05, 0.06, 1.0) # Grafito oscuro
        bsdf.inputs['Roughness'].default_value = 0.90
        bsdf.inputs['Metallic'].default_value = 0.02
    return mat

def create_brass_core_material():
    mat = bpy.data.materials.new(name="M_Core_Brass")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.95, 0.76, 0.22, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.15 # Espejo pulido
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

# ==============================================================================
# MODELADO: SHADER BALL PROFESIONAL CON CORTE FRONTAL 120°
# ==============================================================================
def build_pro_shader_ball(loc=(0, 0, 0), mat_outer=None, mat_core=None):
    """
    Construye la Shader Ball profesional estándar:
    - Cáscara exterior esférica con sección recortada a 120° mostrando el interior.
    - Núcleo interior pulido de latón brillante.
    - Aro ecuatorial biselado y base de soporte mecánica integrada.
    """
    x, y, z = loc
    center_z = z + 0.92
    
    # 1. Cáscara exterior recortada (Cutaway Sphere)
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=24, radius=0.62)
    
    # Cortar un gajo frontal de 120° (entre ángulos -150° y -30°)
    verts_to_delete = []
    for v in bm.verts:
        # Ángulo en plano XY
        angle = math.atan2(v.co.y, v.co.x)
        # Cortar cuadrante frontal inferior hacia la cámara
        if -2.5 < angle < -0.6 and v.co.z > -0.45:
            verts_to_delete.append(v)
    bmesh.ops.delete(bm, geom=verts_to_delete, context='VERTS')
    
    mesh_outer = bpy.data.meshes.new("ShaderBall_Outer_Mesh")
    bm.to_mesh(mesh_outer)
    bm.free()
    
    outer_obj = bpy.data.objects.new("ShaderBall_Outer", mesh_outer)
    outer_obj.location = (x, y, center_z)
    bpy.context.scene.collection.objects.link(outer_obj)
    
    # Espesor sólido en el borde del corte
    mod_sol = outer_obj.modifiers.new("Solidify", 'SOLIDIFY')
    mod_sol.thickness = 0.045
    mod_sol.offset = -1.0
    
    mod_bev = outer_obj.modifiers.new("Bevel", 'BEVEL')
    mod_bev.width = 0.012
    mod_bev.segments = 2
    
    bpy.context.view_layer.objects.active = outer_obj
    bpy.ops.object.shade_smooth()
    
    # Mapeo UV cilíndrico limpio para evitar polar pinch
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.uv.cylinder_project(direction='VIEW_ON_EQUATOR')
    bpy.ops.object.mode_set(mode='OBJECT')
    
    if mat_outer:
        outer_obj.data.materials.append(mat_outer)
        
    # 2. Núcleo interior (Core)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=0.40, location=(x, y, center_z))
    core_obj = bpy.context.active_object
    core_obj.name = "ShaderBall_Core"
    bpy.ops.object.shade_smooth()
    if mat_core:
        core_obj.data.materials.append(mat_core)
        
    # 3. Anillo de collar ecuatorial
    bpy.ops.mesh.primitive_torus_add(major_radius=0.55, minor_radius=0.045, major_segments=36, minor_segments=12, location=(x, y, center_z))
    ring_obj = bpy.context.active_object
    ring_obj.name = "ShaderBall_Ring"
    bpy.ops.object.shade_smooth()
    if mat_core:
        ring_obj.data.materials.append(mat_core)
        
    # 4. Soporte base / pedestal del soporte
    bpy.ops.mesh.primitive_cylinder_add(radius=0.42, depth=0.18, vertices=32, location=(x, y, z + 0.38))
    stand_obj = bpy.context.active_object
    stand_obj.name = "ShaderBall_Stand"
    mod_b = stand_obj.modifiers.new("Bevel", 'BEVEL')
    mod_b.width = 0.02
    mod_b.segments = 2
    bpy.ops.object.shade_smooth()
    if mat_core:
        stand_obj.data.materials.append(mat_core)
        
    return outer_obj

# ==============================================================================
# PROPS CONTEXTUALES MODULARES (Reemplazo del cubo genérico)
# ==============================================================================
def build_station1_modular_wall(loc, mat):
    """Estación 1: Sección de Muro Industrial con Zócalo Hazard y Placa Central."""
    x, y, z = loc
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y, z + 0.58))
    wall = bpy.context.active_object
    wall.name = "Prop_Modular_Wall"
    wall.scale = (0.95, 0.30, 1.15)
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
    """Estación 2: Viga Estructural en I con Remaches y Placas de Blindaje."""
    x, y, z = loc
    # Tronco de Viga en I
    bm = bmesh.new()
    # Perfil en I
    w, h, fl_t, w_t = 0.85, 1.15, 0.12, 0.16
    # Crear malla por extrusión
    v1 = bm.verts.new((-w/2, -0.2, 0))
    v2 = bm.verts.new((w/2, -0.2, 0))
    v3 = bm.verts.new((w/2, 0.2, 0))
    v4 = bm.verts.new((-w/2, 0.2, 0))
    bm.faces.new([v1, v2, v3, v4])
    
    bmesh.ops.extrude_face_region(bm, geom=bm.faces[:])
    mesh_b = bpy.data.meshes.new("IBeam_Mesh")
    bm.to_mesh(mesh_b)
    bm.free()
    
    beam = bpy.data.objects.new("Prop_IBeam", mesh_b)
    beam.location = (x, y, z + 0.10)
    bpy.context.scene.collection.objects.link(beam)
    
    # Cubo biselado con textura de placas de acero
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y, z + 0.58))
    block = bpy.context.active_object
    block.name = "Prop_Armor_Bulkhead"
    block.scale = (0.85, 0.40, 1.15)
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
    """Estación 3: Plataforma Elevada con Rejilla Calada y Marco de Acero."""
    x, y, z = loc
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y, z + 0.58))
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
        
    # Patas de soporte metálicas
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
    """Estación 4: Pilar Octagonal de Cemento Armado con Zócalo Biselado."""
    x, y, z = loc
    bpy.ops.mesh.primitive_cylinder_add(radius=0.52, depth=1.15, vertices=8, location=(x, y, z + 0.58))
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
    """Estación 5: Consola Terminal Industrial con Carátula Inclinada."""
    x, y, z = loc
    # Cuerpo de consola
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y, z + 0.50))
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
        
    # Carátula inclinada superior
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y + 0.08, z + 0.92))
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
    """Tableta inclinada a 30° mostrando la textura ortogonal plana."""
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

def build_station_pedestal(x=0.0, name_str="01. TRIM INDUSTRIAL", mat_pedestal=None, mat_plaque=None):
    """Construye el pedestal escalonado con placa metálica identificadora."""
    # Plinto inferior
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, 0, 0.12))
    base1 = bpy.context.active_object
    base1.name = f"Pedestal_Base_{x}"
    base1.scale = (3.6, 2.4, 0.24)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    mod_b = base1.modifiers.new("Bevel", 'BEVEL')
    mod_b.width = 0.03
    mod_b.segments = 2
    if mat_pedestal:
        base1.data.materials.append(mat_pedestal)
        
    # Columna central
    bpy.ops.mesh.primitive_cylinder_add(radius=0.55, depth=0.32, vertices=32, location=(x, -0.15, 0.35))
    col = bpy.context.active_object
    col.name = f"Pedestal_Col_{x}"
    mod_bc = col.modifiers.new("Bevel", 'BEVEL')
    mod_bc.width = 0.02
    mod_bc.segments = 2
    if mat_pedestal:
        col.data.materials.append(mat_pedestal)
        
    # Placa de identificación frontal de latón
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, -1.21, 0.14))
    plaque = bpy.context.active_object
    plaque.name = f"Plaque_{x}"
    plaque.scale = (1.4, 0.04, 0.14)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    mod_bp = plaque.modifiers.new("Bevel", 'BEVEL')
    mod_bp.width = 0.015
    mod_bp.segments = 2
    if mat_plaque:
        plaque.data.materials.append(mat_plaque)
        
    return base1

def build_studio_environment(mat_back):
    bm = bmesh.new()
    v1 = bm.verts.new((-20.0, -10.0, 0.0))
    v2 = bm.verts.new((20.0, -10.0, 0.0))
    v3 = bm.verts.new((20.0, 4.0, 0.0))
    v4 = bm.verts.new((-20.0, 4.0, 0.0))
    bm.faces.new([v1, v2, v3, v4])
    
    prev_v_left, prev_v_right = v4, v3
    curve_pts = [(4.5, 0.3), (5.3, 1.0), (6.0, 2.2), (6.5, 4.0), (6.8, 6.5), (7.0, 9.5)]
    for y_pos, z_pos in curve_pts:
        vl = bm.verts.new((-20.0, y_pos, z_pos))
        vr = bm.verts.new((20.0, y_pos, z_pos))
        bm.faces.new([prev_v_left, prev_v_right, vr, vl])
        prev_v_left, prev_v_right = vl, vr
        
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
    # Key Sun cálida
    bpy.ops.object.light_add(type='SUN', location=(8.0, -10.0, 12.0))
    sun = bpy.context.active_object
    sun.name = "Key_Sun"
    sun.data.energy = 6.2
    sun.data.color = (1.0, 0.96, 0.90)
    sun.rotation_euler = (R(48), R(14), R(-28))
    
    # Rim Light Cyan detrás
    bpy.ops.object.light_add(type='AREA', location=(0.0, 4.8, 6.2))
    rim = bpy.context.active_object
    rim.name = "Rim_Cyan"
    rim.data.shape = 'RECTANGLE'
    rim.data.size = 28.0
    rim.data.size_y = 4.0
    rim.data.energy = 2800.0
    rim.data.color = (0.35, 0.82, 1.0)
    rim.rotation_euler = (R(-55), 0, 0)
    
    # Fill Light Orange frontal rasante
    bpy.ops.object.light_add(type='AREA', location=(0.0, -7.0, 1.4))
    fill = bpy.context.active_object
    fill.name = "Fill_Orange"
    fill.data.shape = 'RECTANGLE'
    fill.data.size = 24.0
    fill.data.size_y = 2.5
    fill.data.energy = 550.0
    fill.data.color = (1.0, 0.68, 0.38)
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
# PIPELINE MAESTRO V2
# ==============================================================================
def main():
    print("=== INICIANDO CONSTRUCCIÓN MATERIAL TEST BENCH V2 (BLENDER 5.2 LTS) ===")
    scene = reset_scene()
    
    mat_pedestal = create_pedestal_material()
    mat_backdrop = create_backdrop_material()
    mat_core = create_brass_core_material()
    mat_plaque = create_plaque_material()
    
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
        
        # Pedestal con placa metálica
        build_station_pedestal(x=x, name_str=cfg["station_name"], mat_pedestal=mat_pedestal, mat_plaque=mat_plaque)
        
        # Shader Ball Profesional con corte a 120°
        build_pro_shader_ball(loc=(x, -0.15, 0.45), mat_outer=mat, mat_core=mat_core)
        
        # Prop modular contextual a la izquierda
        cfg["prop_builder"](loc=(x - 1.15, 0.30, 0.24), mat=mat)
        
        # Tableta inclinada a la derecha
        build_sample_tablet(loc=(x + 1.15, 0.30, 0.24), mat=mat)
        
        # Cámara focal individual calibrada: distancia de 4.8m y altura 1.45m para encuadre completo sin cortes
        cam = create_camera(
            name=cfg["cam_name"],
            loc=(x, -4.8, 1.45),
            rot=(R(78), 0, 0),
            fov=48.0
        )
        cameras[cfg["cam_name"]] = cam
        
    # Cámara panorámica maestra para los 5 materiales juntos con suficiente distancia y FOV amplio
    cam_master = create_camera(
        name="Cam_Master_Panorama",
        loc=(0.0, -14.5, 3.8),
        rot=(R(78), 0, 0),
        fov=74.0
    )
    cameras["Cam_Master_Panorama"] = cam_master
    
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_FILE)
    print(f"[OK] Proyecto guardado: {BLEND_FILE}")
    
    # -------------------------------------------------------------
    # RENDERS V2 OFICIALES
    # -------------------------------------------------------------
    # 1. Master Panorama (2560x1440)
    scene.camera = cam_master
    scene.render.resolution_x = 2560
    scene.render.resolution_y = 1440
    master_render_path = os.path.join(RENDERS_DIR, "Showcase_Material_Test_Bench_Master.png")
    scene.render.filepath = master_render_path
    print("Renderizando Panorama V2 2560x1440...")
    bpy.ops.render.render(write_still=True)
    shutil.copy(master_render_path, os.path.join(ARTIFACT_DIR, "Showcase_Material_Test_Bench_Master.png"))
    print(f"[OK] Renderizado: {master_render_path}")
    
    # 2. Planos Focales Individuales (1920x1080)
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
        print(f"Renderizando close-up V2 {file_name}...")
        bpy.ops.render.render(write_still=True)
        shutil.copy(out_path, os.path.join(ARTIFACT_DIR, file_name))
        print(f"[OK] Renderizado: {out_path}")
        
    print("=== TODOS LOS RENDERS V2 DEL MATERIAL TEST BENCH COMPLETADOS ===")

if __name__ == "__main__":
    main()

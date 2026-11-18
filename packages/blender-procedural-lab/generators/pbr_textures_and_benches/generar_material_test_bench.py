# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Generador Maestro del Banco de Pruebas de Materiales (Material Test Bench) - Astra Hazard
# Crea la escena oficial en Blender 5.2 LTS y renderiza showcases en alta resolución (2560x1440 y 1080p).
# Implementa el pipeline PBR Toon completo: BaseColor, Normal (Tangent), ORM (AO/Roughness/Metallic) y Emissive.

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
    
    # Freestyle para entintado cómic
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
    linestyle.color = (0.04, 0.03, 0.03)
    linestyle.thickness = 1.8
    ls.linestyle = linestyle
    
    return scene

def create_pbr_toon_material(name, base_color_path, normal_path, orm_path, emissive_path=None, uv_scale=(1.0, 1.0)):
    """
    Construye el grafo maestro PBR Toon en Blender 5.2 LTS:
    - BaseColor conectado a Principled BSDF Base Color
    - Normal Map (Tangent Space) conectado a Normal
    - ORM descompuesto (R: AO mix, G: Roughness, B: Metallic)
    - Emissive conectado a Emission Color con Strength adecuado
    """
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    node_out = nodes.new(type='ShaderNodeOutputMaterial')
    node_out.location = (600, 0)
    
    node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    node_bsdf.location = (200, 0)
    links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])
    
    # Coordenadas UV y mapeo
    coord_node = nodes.new(type='ShaderNodeTexCoord')
    coord_node.location = (-900, 0)
    
    mapping_node = nodes.new(type='ShaderNodeMapping')
    mapping_node.location = (-700, 0)
    mapping_node.inputs['Scale'].default_value = (uv_scale[0], uv_scale[1], 1.0)
    links.new(coord_node.outputs['UV'], mapping_node.inputs['Vector'])
    
    # 1. BaseColor
    if os.path.exists(base_color_path):
        tex_bc = nodes.new(type='ShaderNodeTexImage')
        tex_bc.location = (-400, 300)
        tex_bc.image = bpy.data.images.load(base_color_path)
        links.new(mapping_node.outputs['Vector'], tex_bc.inputs['Vector'])
        links.new(tex_bc.outputs['Color'], node_bsdf.inputs['Base Color'])
    
    # 2. ORM (R: AO, G: Roughness, B: Metallic)
    if os.path.exists(orm_path):
        tex_orm = nodes.new(type='ShaderNodeTexImage')
        tex_orm.location = (-400, 0)
        img_orm = bpy.data.images.load(orm_path)
        img_orm.colorspace_settings.name = 'Non-Color'
        tex_orm.image = img_orm
        links.new(mapping_node.outputs['Vector'], tex_orm.inputs['Vector'])
        
        sep_color = nodes.new(type='ShaderNodeSeparateColor')
        sep_color.location = (-150, 0)
        links.new(tex_orm.outputs['Color'], sep_color.inputs['Color'])
        
        # G -> Roughness
        links.new(sep_color.outputs['Green'], node_bsdf.inputs['Roughness'])
        # B -> Metallic
        links.new(sep_color.outputs['Blue'], node_bsdf.inputs['Metallic'])
    
    # 3. Normal Map
    if os.path.exists(normal_path):
        tex_norm = nodes.new(type='ShaderNodeTexImage')
        tex_norm.location = (-400, -300)
        img_norm = bpy.data.images.load(normal_path)
        img_norm.colorspace_settings.name = 'Non-Color'
        tex_norm.image = img_norm
        links.new(mapping_node.outputs['Vector'], tex_norm.inputs['Vector'])
        
        norm_map = nodes.new(type='ShaderNodeNormalMap')
        norm_map.location = (-150, -300)
        norm_map.space = 'TANGENT'
        norm_map.inputs['Strength'].default_value = 1.2
        links.new(tex_norm.outputs['Color'], norm_map.inputs['Color'])
        links.new(norm_map.outputs['Normal'], node_bsdf.inputs['Normal'])
    
    # 4. Emissive
    if emissive_path and os.path.exists(emissive_path):
        tex_emi = nodes.new(type='ShaderNodeTexImage')
        tex_emi.location = (-400, -600)
        tex_emi.image = bpy.data.images.load(emissive_path)
        links.new(mapping_node.outputs['Vector'], tex_emi.inputs['Vector'])
        links.new(tex_emi.outputs['Color'], node_bsdf.inputs['Emission Color'])
        node_bsdf.inputs['Emission Strength'].default_value = 3.5
        
    return mat

def create_pedestal_material():
    mat = bpy.data.materials.new(name="M_Pedestal_Studio")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.08, 0.08, 0.09, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.4
        bsdf.inputs['Metallic'].default_value = 0.8
    return mat

def create_backdrop_material():
    mat = bpy.data.materials.new(name="M_Backdrop_Studio")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.12, 0.12, 0.14, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.85
        bsdf.inputs['Metallic'].default_value = 0.05
    return mat

def create_brass_core_material():
    mat = bpy.data.materials.new(name="M_Core_Brass")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.95, 0.75, 0.22, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.25
        bsdf.inputs['Metallic'].default_value = 0.95
    return mat

# ==============================================================================
# GEOMETRÍA: SHADER BALL, CUBO BISELADO, TABLETA DE MUESTRA Y PEDESTAL
# ==============================================================================
def build_shader_ball(loc=(0, 0, 0), mat_outer=None, mat_core=None):
    """
    Crea una Shader Ball profesional estándar de la industria:
    - Esfera exterior cortada con bisel y reborde
    - Esfera interior (núcleo de contraste metálico)
    - Soporte / anillo base
    """
    x, y, z = loc
    
    # 1. Esfera exterior
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, radius=0.65, location=(x, y, z + 0.95))
    ball_outer = bpy.context.active_object
    ball_outer.name = "ShaderBall_Outer"
    
    # Bisel y suavizado
    bpy.ops.object.shade_smooth()
    mod_b = ball_outer.modifiers.new("Bevel", 'BEVEL')
    mod_b.width = 0.015
    mod_b.segments = 2
    
    # UV Unwrap cilíndrico / esférico
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.uv.sphere_project()
    bpy.ops.object.mode_set(mode='OBJECT')
    
    if mat_outer:
        ball_outer.data.materials.append(mat_outer)
        
    # 2. Núcleo interior (Core)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=0.38, location=(x, y, z + 0.95))
    ball_core = bpy.context.active_object
    ball_core.name = "ShaderBall_Core"
    bpy.ops.object.shade_smooth()
    if mat_core:
        ball_core.data.materials.append(mat_core)
        
    # 3. Anillo de soporte
    bpy.ops.mesh.primitive_torus_add(major_radius=0.48, minor_radius=0.06, major_segments=32, minor_segments=12, location=(x, y, z + 0.38))
    ring = bpy.context.active_object
    ring.name = "ShaderBall_Ring"
    bpy.ops.object.shade_smooth()
    if mat_core:
        ring.data.materials.append(mat_core)
        
    return ball_outer

def build_sample_cube(loc=(0, 0, 0), mat=None):
    """
    Cubo biselado que demuestra cómo el material y las texturas envuelven aristas y remaches.
    """
    x, y, z = loc
    bpy.ops.mesh.primitive_cube_add(size=0.85, location=(x, y, z + 0.52))
    cube = bpy.context.active_object
    cube.name = "SampleCube"
    
    mod_b = cube.modifiers.new("Bevel", 'BEVEL')
    mod_b.width = 0.035
    mod_b.segments = 3
    
    # UV Unwrap en caja cúbica
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.uv.cube_project(cube_size=0.85)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.shade_smooth()
    
    if mat:
        cube.data.materials.append(mat)
    return cube

def build_sample_tablet(loc=(0, 0, 0), mat=None):
    """
    Tableta inclinada a 45° que muestra el plano 2D de la textura completa.
    """
    x, y, z = loc
    # Plano con bisel
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y, z + 0.45))
    tablet = bpy.context.active_object
    tablet.name = "SampleTablet"
    tablet.scale = (0.85, 0.05, 0.85)
    tablet.rotation_euler = (R(35), 0, 0)
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

def build_station_pedestal(x=0.0, mat_pedestal=None):
    """
    Construye el plinto / base escalonada para cada estación de material.
    """
    # Base inferior ancha
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, 0, 0.12))
    base1 = bpy.context.active_object
    base1.name = f"Pedestal_Base_{x}"
    base1.scale = (3.4, 2.2, 0.24)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    
    mod_b = base1.modifiers.new("Bevel", 'BEVEL')
    mod_b.width = 0.03
    mod_b.segments = 2
    if mat_pedestal:
        base1.data.materials.append(mat_pedestal)
        
    # Columna superior para la shader ball
    bpy.ops.mesh.primitive_cylinder_add(radius=0.6, depth=0.35, vertices=32, location=(x, -0.15, 0.35))
    col = bpy.context.active_object
    col.name = f"Pedestal_Col_{x}"
    mod_bc = col.modifiers.new("Bevel", 'BEVEL')
    mod_bc.width = 0.02
    mod_bc.segments = 2
    if mat_pedestal:
        col.data.materials.append(mat_pedestal)
        
    return base1

def build_studio_environment(mat_back):
    """
    Crea el suelo continuo y el ciclorama de fondo de estudio curvo.
    """
    bm = bmesh.new()
    
    # Plano de suelo ancho
    v1 = bm.verts.new((-16.0, -8.0, 0.0))
    v2 = bm.verts.new((16.0, -8.0, 0.0))
    v3 = bm.verts.new((16.0, 4.0, 0.0))
    v4 = bm.verts.new((-16.0, 4.0, 0.0))
    bm.faces.new([v1, v2, v3, v4])
    
    # Curva ascendente de ciclorama
    prev_v_left = v4
    prev_v_right = v3
    curve_pts = [
        (4.5, 0.2),
        (5.2, 0.8),
        (5.8, 1.8),
        (6.2, 3.2),
        (6.4, 5.5),
        (6.5, 8.0)
    ]
    for y_pos, z_pos in curve_pts:
        vl = bm.verts.new((-16.0, y_pos, z_pos))
        vr = bm.verts.new((16.0, y_pos, z_pos))
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
    # 1. Key Light (Luz Solar Cálida Frontal a 45°)
    bpy.ops.object.light_add(type='SUN', location=(6.0, -8.0, 10.0))
    sun = bpy.context.active_object
    sun.name = "Key_Sun"
    sun.data.energy = 5.5
    sun.data.color = (1.0, 0.94, 0.88)
    sun.rotation_euler = (R(48), R(12), R(-25))
    
    # 2. Rim Light (Luz de Silueta Azul Turquesa desde atrás)
    bpy.ops.object.light_add(type='AREA', location=(0.0, 4.5, 5.5))
    rim = bpy.context.active_object
    rim.name = "Rim_Cyan"
    rim.data.shape = 'RECTANGLE'
    rim.data.size = 24.0
    rim.data.size_y = 3.0
    rim.data.energy = 2200.0
    rim.data.color = (0.35, 0.80, 1.0)
    rim.rotation_euler = (R(-55), 0, 0)
    
    # 3. Fill Light (Rebote Cálido Anaranjado de Suelo)
    bpy.ops.object.light_add(type='AREA', location=(0.0, -5.5, 1.2))
    fill = bpy.context.active_object
    fill.name = "Fill_Orange"
    fill.data.shape = 'RECTANGLE'
    fill.data.size = 20.0
    fill.data.size_y = 2.0
    fill.data.energy = 450.0
    fill.data.color = (1.0, 0.65, 0.35)
    fill.rotation_euler = (R(35), 0, 0)

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
# PIPELINE MAESTRO Y RENDERIZADO
# ==============================================================================
def main():
    print("=== CONSTRUYENDO BANCO DE PRUEBAS DE MATERIALES (BLENDER 5.2 LTS) ===")
    scene = reset_scene()
    
    # Materiales auxiliares de estudio
    mat_pedestal = create_pedestal_material()
    mat_backdrop = create_backdrop_material()
    mat_core = create_brass_core_material()
    
    # Construir ciclorama e iluminación
    build_studio_environment(mat_backdrop)
    setup_studio_lighting()
    
    # 5 Materiales Maestros PBR Toon
    material_configs = [
        {
            "name": "M_PBR_Trim_Industrial",
            "station_name": "TRIM INDUSTRIAL",
            "x": -8.0,
            "bc": os.path.join(TEXTURES_MODULAR, "T_Trim_Industrial_BaseColor.png"),
            "norm": os.path.join(TEXTURES_MODULAR, "T_Trim_Industrial_Normal.png"),
            "orm": os.path.join(TEXTURES_MODULAR, "T_Trim_Industrial_ORM.png"),
            "emi": os.path.join(TEXTURES_MODULAR, "T_Trim_Industrial_Emissive.png"),
            "cam_name": "Cam_Trim_Industrial"
        },
        {
            "name": "M_PBR_Steel_Plates",
            "station_name": "STEEL PLATES",
            "x": -4.0,
            "bc": os.path.join(TEXTURES_MODULAR, "T_Steel_Plates_BaseColor.png"),
            "norm": os.path.join(TEXTURES_MODULAR, "T_Steel_Plates_Normal.png"),
            "orm": os.path.join(TEXTURES_MODULAR, "T_Steel_Plates_ORM.png"),
            "emi": os.path.join(TEXTURES_MODULAR, "T_Steel_Plates_Emissive.png"),
            "cam_name": "Cam_Steel_Plates"
        },
        {
            "name": "M_PBR_Grating_Walkway",
            "station_name": "GRATING WALKWAY",
            "x": 0.0,
            "bc": os.path.join(TEXTURES_MODULAR, "T_Grating_Walkway_BaseColor.png"),
            "norm": os.path.join(TEXTURES_MODULAR, "T_Grating_Walkway_Normal.png"),
            "orm": os.path.join(TEXTURES_MODULAR, "T_Grating_Walkway_ORM.png"),
            "emi": os.path.join(TEXTURES_MODULAR, "T_Grating_Walkway_Emissive.png"),
            "cam_name": "Cam_Grating_Walkway"
        },
        {
            "name": "M_PBR_Concrete_Factory",
            "station_name": "CONCRETE FACTORY",
            "x": 4.0,
            "bc": os.path.join(TEXTURES_MODULAR, "T_Concrete_Factory_BaseColor.png"),
            "norm": os.path.join(TEXTURES_MODULAR, "T_Concrete_Factory_Normal.png"),
            "orm": os.path.join(TEXTURES_MODULAR, "T_Concrete_Factory_ORM.png"),
            "emi": os.path.join(TEXTURES_MODULAR, "T_Concrete_Factory_Emissive.png"),
            "cam_name": "Cam_Concrete_Factory"
        },
        {
            "name": "M_PBR_Props_Machinery",
            "station_name": "PROPS MACHINERY",
            "x": 8.0,
            "bc": os.path.join(TEXTURES_MODULAR, "T_Props_Machinery_BaseColor.png"),
            "norm": os.path.join(TEXTURES_MODULAR, "T_Props_Machinery_Normal.png"),
            "orm": os.path.join(TEXTURES_MODULAR, "T_Props_Machinery_ORM.png"),
            "emi": os.path.join(TEXTURES_MODULAR, "T_Props_Machinery_Emissive.png"),
            "cam_name": "Cam_Props_Machinery"
        }
    ]
    
    cameras = {}
    
    # Construir estaciones
    for cfg in material_configs:
        mat = create_pbr_toon_material(
            name=cfg["name"],
            base_color_path=cfg["bc"],
            normal_path=cfg["norm"],
            orm_path=cfg["orm"],
            emissive_path=cfg["emi"]
        )
        x = cfg["x"]
        
        # Plinto
        build_station_pedestal(x=x, mat_pedestal=mat_pedestal)
        
        # 1. Shader Ball central
        build_shader_ball(loc=(x, -0.15, 0.45), mat_outer=mat, mat_core=mat_core)
        
        # 2. Sample Cube a la izquierda
        build_sample_cube(loc=(x - 1.05, 0.35, 0.24), mat=mat)
        
        # 3. Sample Tablet a la derecha
        build_sample_tablet(loc=(x + 1.05, 0.35, 0.24), mat=mat)
        
        # Cámara focal individual (1080p close-up)
        cam = create_camera(
            name=cfg["cam_name"],
            loc=(x, -3.8, 1.85),
            rot=(R(74), 0, 0),
            fov=40.0
        )
        cameras[cfg["cam_name"]] = cam
    
    # Cámara panorámica maestra para los 5 materiales juntos
    cam_master = create_camera(
        name="Cam_Master_Panorama",
        loc=(0.0, -11.5, 4.2),
        rot=(R(75), 0, 0),
        fov=68.0
    )
    cameras["Cam_Master_Panorama"] = cam_master
    
    # Guardar archivo .blend oficial
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_FILE)
    print(f"[OK] Proyecto guardado: {BLEND_FILE}")
    
    # -------------------------------------------------------------
    # RENDERS OFICIALES DE EXHIBICIÓN
    # -------------------------------------------------------------
    # 1. Master Panorama (2560x1440)
    scene.camera = cam_master
    scene.render.resolution_x = 2560
    scene.render.resolution_y = 1440
    master_render_path = os.path.join(RENDERS_DIR, "Showcase_Material_Test_Bench_Master.png")
    scene.render.filepath = master_render_path
    print("Renderizando Lámina Maestra Panorama 2560x1440...")
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
        print(f"Renderizando close-up {file_name}...")
        bpy.ops.render.render(write_still=True)
        shutil.copy(out_path, os.path.join(ARTIFACT_DIR, file_name))
        print(f"[OK] Renderizado: {out_path}")
        
    print("=== TODOS LOS RENDERS DEL MATERIAL TEST BENCH COMPLETADOS ===")

if __name__ == "__main__":
    main()

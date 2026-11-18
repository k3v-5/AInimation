# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Generador Maestro 3D - Lote 2 de Props: Energía, Generadores y Red Eléctrica Auxiliar (V3 Óptima)
# Blender 5.2 LTS - Modelado Paramétrico, Shaders Stylized PBR, Freestyle Lineart y Lámina Maestra 2.5K

import bpy
import bmesh
import math
import os
import shutil
from mathutils import Vector, Euler
from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = r"F:\Dev\Game"
RENDERS_DIR = os.path.join(PROJECT_ROOT, "Art", "Renders")
ARTIFACT_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\b59ff04f-3c21-4ee5-94b0-8e8f899f8923"
BLEND_FILE = os.path.join(PROJECT_ROOT, "Art", "Blender", "Lote2_Props_Maestros_Oficial.blend")

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
    
    # World studio setup
    world = bpy.data.worlds.new("World_Studio")
    scene.world = world
    world.use_nodes = True
    wnodes = world.node_tree.nodes
    wlinks = world.node_tree.links
    wnodes.clear()
    
    w_out = wnodes.new(type='ShaderNodeOutputWorld')
    w_bg = wnodes.new(type='ShaderNodeBackground')
    w_bg.inputs['Color'].default_value = (0.025, 0.030, 0.040, 1.0)
    w_bg.inputs['Strength'].default_value = 0.75
    wlinks.new(w_bg.outputs['Background'], w_out.inputs['Surface'])
    
    # Freestyle Lineart
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

# -------------------------------------------------------------------------
# SHADERS PBR & STYLIZED
# -------------------------------------------------------------------------
def create_materials():
    mats = {}
    
    def make_pbr(name, base_col, roughness=0.5, metallic=0.0, emissive_col=(0,0,0,1), emissive_str=0.0):
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

    mats['Cast_Iron'] = make_pbr("Mat_Cast_Iron", (0.16, 0.17, 0.19, 1.0), roughness=0.48, metallic=0.82)
    mats['Dark_Gunmetal'] = make_pbr("Mat_Dark_Gunmetal", (0.09, 0.10, 0.12, 1.0), roughness=0.32, metallic=0.92)
    mats['Industrial_Orange'] = make_pbr("Mat_Industrial_Orange", (0.95, 0.44, 0.06, 1.0), roughness=0.38, metallic=0.15)
    mats['Hazard_Yellow'] = make_pbr("Mat_Hazard_Yellow", (0.96, 0.74, 0.08, 1.0), roughness=0.40, metallic=0.10)
    mats['Hazard_Black'] = make_pbr("Mat_Hazard_Black", (0.05, 0.05, 0.06, 1.0), roughness=0.45, metallic=0.15)
    mats['Pure_Copper'] = make_pbr("Mat_Pure_Copper", (0.95, 0.54, 0.35, 1.0), roughness=0.22, metallic=0.96)
    mats['Machinery_Brass'] = make_pbr("Mat_Machinery_Brass", (0.88, 0.70, 0.28, 1.0), roughness=0.26, metallic=0.92)
    mats['Ceramic_Insulator'] = make_pbr("Mat_Ceramic_Insulator", (0.85, 0.83, 0.80, 1.0), roughness=0.16, metallic=0.0)
    mats['Cable_Rubber_Orange'] = make_pbr("Mat_Cable_Rubber_Orange", (0.92, 0.38, 0.08, 1.0), roughness=0.55, metallic=0.05)
    mats['Tire_Rubber_Black'] = make_pbr("Mat_Tire_Rubber_Black", (0.06, 0.06, 0.07, 1.0), roughness=0.75, metallic=0.0)
    mats['Polished_Chrome'] = make_pbr("Mat_Polished_Chrome", (0.92, 0.94, 0.96, 1.0), roughness=0.06, metallic=1.0)
    mats['Graphene_Cell'] = make_pbr("Mat_Graphene_Cell", (0.16, 0.18, 0.22, 1.0), roughness=0.28, metallic=0.78)
    
    mats['Plasma_Cyan'] = make_pbr("Mat_Plasma_Cyan", (0.1, 0.85, 1.0, 1.0), roughness=0.10, metallic=0.0,
                                   emissive_col=(0.0, 0.95, 1.0, 1.0), emissive_str=5.5)
    mats['LED_Green'] = make_pbr("Mat_LED_Green", (0.15, 0.95, 0.3, 1.0), roughness=0.15, metallic=0.0,
                                 emissive_col=(0.2, 1.0, 0.35, 1.0), emissive_str=4.5)
    mats['LED_Red'] = make_pbr("Mat_LED_Red", (0.95, 0.12, 0.1, 1.0), roughness=0.15, metallic=0.0,
                               emissive_col=(1.0, 0.15, 0.1, 1.0), emissive_str=4.5)
    mats['LED_Amber'] = make_pbr("Mat_LED_Amber", (1.0, 0.6, 0.05, 1.0), roughness=0.15, metallic=0.0,
                                 emissive_col=(1.0, 0.65, 0.08, 1.0), emissive_str=4.0)

    mats['Studio_Floor'] = make_pbr("Mat_Studio_Floor", (0.045, 0.052, 0.062, 1.0), roughness=0.92, metallic=0.0)
    mats['Plinth_Dark'] = make_pbr("Mat_Plinth_Dark", (0.08, 0.09, 0.11, 1.0), roughness=0.40, metallic=0.55)
    mats['Plinth_Plaque'] = make_pbr("Mat_Plinth_Plaque", (0.90, 0.74, 0.32, 1.0), roughness=0.22, metallic=0.95)
    
    return mats

def create_mesh_object(name, collection, mesh_func, materials):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    mesh_func(bm)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    
    for mat in materials:
        if mat:
            obj.data.materials.append(mat)
            
    return obj

def add_box(bm, center, size, mat_idx=0):
    ret = bmesh.ops.create_cube(bm, size=1.0)
    verts = ret['verts']
    bmesh.ops.scale(bm, vec=size, verts=verts)
    bmesh.ops.translate(bm, vec=center, verts=verts)
    faces = set()
    for v in verts:
        for f in v.link_faces:
            faces.add(f)
    for f in faces:
        f.material_index = mat_idx
    return verts, list(faces)

def add_cylinder(bm, center, radius, height, segments=16, mat_idx=0, axis='Z'):
    cx, cy, cz = center
    half_h = height * 0.5
    top_verts = []
    bot_verts = []
    
    for i in range(segments):
        ang = (2.0 * math.pi * i) / segments
        ca = math.cos(ang) * radius
        sa = math.sin(ang) * radius
        if axis == 'Z':
            b_pt = (cx + ca, cy + sa, cz - half_h)
            t_pt = (cx + ca, cy + sa, cz + half_h)
        elif axis == 'Y':
            b_pt = (cx + ca, cy - half_h, cz + sa)
            t_pt = (cx + ca, cy + half_h, cz + sa)
        else: # X
            b_pt = (cx - half_h, cy + ca, cz + sa)
            t_pt = (cx + half_h, cy + ca, cz + sa)
            
        bot_verts.append(bm.verts.new(b_pt))
        top_verts.append(bm.verts.new(t_pt))
        
    faces = []
    for i in range(segments):
        ni = (i + 1) % segments
        f = bm.faces.new((bot_verts[i], bot_verts[ni], top_verts[ni], top_verts[i]))
        f.material_index = mat_idx
        faces.append(f)
        
    fb = bm.faces.new(list(reversed(bot_verts)))
    fb.material_index = mat_idx
    ft = bm.faces.new(top_verts)
    ft.material_index = mat_idx
    faces.extend([fb, ft])
    return faces

# -------------------------------------------------------------------------
# PROP 06: SM_Backup_Diesel_Generator
# -------------------------------------------------------------------------
def build_prop06_diesel_generator(col, mats):
    def geom(bm):
        # 1. Chasis patín de vigas en U
        add_box(bm, (0, -0.45, 0.08), (1.60, 0.14, 0.16), mat_idx=0)
        add_box(bm, (0,  0.45, 0.08), (1.60, 0.14, 0.16), mat_idx=0)
        add_box(bm, (-0.72, 0, 0.08), (0.14, 0.86, 0.16), mat_idx=0)
        add_box(bm, ( 0.72, 0, 0.08), (0.14, 0.86, 0.16), mat_idx=0)
        
        # 2. Bloque motor diésel central
        add_box(bm, (-0.15, 0, 0.60), (0.85, 0.80, 0.75), mat_idx=1)
        add_box(bm, (-0.15, 0, 1.02), (0.78, 0.48, 0.12), mat_idx=2)
        
        # 3. Radiador frontal con chevrons amarillos
        add_box(bm, (0.50, 0, 0.65), (0.32, 0.82, 0.85), mat_idx=1)
        for ry in range(-4, 5):
            add_box(bm, (0.67, ry * 0.085, 0.65), (0.02, 0.065, 0.75), mat_idx=3 if ry % 2 == 0 else 4)
            
        # 4. Tanque de combustible superior cilíndrico
        add_cylinder(bm, (-0.15, 0, 1.18), radius=0.20, height=0.82, segments=20, mat_idx=2, axis='X')
        add_cylinder(bm, (-0.15, 0, 1.41), radius=0.06, height=0.06, segments=14, mat_idx=5, axis='Z')
        add_cylinder(bm, (-0.15, -0.20, 1.18), radius=0.016, height=0.26, segments=10, mat_idx=6, axis='Z')
        
        # 5. Tubo de escape vertical con silenciador
        add_cylinder(bm, (-0.52, 0.26, 1.10), radius=0.045, height=0.55, segments=14, mat_idx=0, axis='Z')
        add_cylinder(bm, (-0.52, 0.26, 1.40), radius=0.065, height=0.08, segments=14, mat_idx=1, axis='Z')
        
        # 6. Carcasa del alternador y tirador manual
        add_cylinder(bm, (-0.68, 0, 0.55), radius=0.30, height=0.22, segments=20, mat_idx=0, axis='X')
        add_cylinder(bm, (-0.82, 0, 0.55), radius=0.03, height=0.06, segments=12, mat_idx=5, axis='X')
        add_box(bm, (-0.86, 0, 0.55), (0.04, 0.15, 0.04), mat_idx=4)
        
        # 7. Panel de control frontal
        add_box(bm, (-0.15, -0.42, 0.62), (0.48, 0.05, 0.32), mat_idx=0)
        add_cylinder(bm, (-0.26, -0.46, 0.68), radius=0.045, height=0.02, segments=14, mat_idx=5, axis='Y')
        add_cylinder(bm, (-0.13, -0.46, 0.68), radius=0.035, height=0.02, segments=14, mat_idx=5, axis='Y')
        add_cylinder(bm, (0.01, -0.46, 0.68), radius=0.02, height=0.02, segments=10, mat_idx=7, axis='Y')
        add_cylinder(bm, (0.01, -0.46, 0.58), radius=0.02, height=0.02, segments=10, mat_idx=8, axis='Y')

    mat_list = [
        mats['Cast_Iron'], mats['Dark_Gunmetal'], mats['Industrial_Orange'],
        mats['Hazard_Yellow'], mats['Hazard_Black'], mats['Machinery_Brass'],
        mats['Polished_Chrome'], mats['LED_Green'], mats['LED_Red']
    ]
    return create_mesh_object("SM_Backup_Diesel_Generator", col, geom, mat_list)

# -------------------------------------------------------------------------
# PROP 07: SM_High_Voltage_Breaker_Box (Gabinete hueco con interior visible)
# -------------------------------------------------------------------------
def build_prop07_breaker_box(col, mats):
    def geom(bm):
        cz = 0.85
        # 1. Carcasa de mamparo hueca (pared trasera, laterales, techo y suelo)
        add_box(bm, (0, 0.12, cz), (0.80, 0.04, 1.25), mat_idx=0) # Back wall
        add_box(bm, (-0.38, 0, cz), (0.04, 0.24, 1.25), mat_idx=0) # Left wall
        add_box(bm, ( 0.38, 0, cz), (0.04, 0.24, 1.25), mat_idx=0) # Right wall
        add_box(bm, (0, 0, cz + 0.60), (0.80, 0.24, 0.05), mat_idx=0) # Top
        add_box(bm, (0, 0, cz - 0.60), (0.80, 0.24, 0.05), mat_idx=0) # Bottom
        
        # 2. Puerta batiente abierta hacia la izquierda (-X) a 75°
        door_w = 0.74
        door_ang = math.radians(75.0)
        cos_a = math.cos(door_ang)
        sin_a = math.sin(door_ang)
        dx_c = -0.38 - (door_w * 0.5) * sin_a
        dy_c = -0.12 - (door_w * 0.5) * cos_a
        add_box(bm, (dx_c, dy_c, cz), (0.03, door_w * cos_a, 1.20), mat_idx=1)
        
        # Rótulo de peligro en la puerta abierta
        add_box(bm, (dx_c - 0.02, dy_c, cz + 0.30), (0.01, 0.26 * cos_a, 0.18), mat_idx=2)
        
        # Bisagras
        add_cylinder(bm, (-0.39, -0.12, cz + 0.45), radius=0.025, height=0.10, segments=10, mat_idx=5, axis='Z')
        add_cylinder(bm, (-0.39, -0.12, cz - 0.45), radius=0.025, height=0.10, segments=10, mat_idx=5, axis='Z')
        
        # 3. Placa de baquelita interior en el fondo de la cavidad
        add_box(bm, (0, 0.08, cz), (0.72, 0.02, 1.15), mat_idx=1)
        
        # 3 Disyuntores de cuchilla de alta tensión dentro de la cavidad
        for idx, bx in enumerate([-0.20, 0.0, 0.20]):
            # Aisladores cerámicos acanalados
            add_cylinder(bm, (bx, 0.03, cz + 0.30), radius=0.042, height=0.12, segments=12, mat_idx=4, axis='Z')
            add_cylinder(bm, (bx, 0.03, cz - 0.22), radius=0.042, height=0.12, segments=12, mat_idx=4, axis='Z')
            # Cuchilla de contacto de cobre puro
            add_box(bm, (bx, 0.00, cz + 0.04), (0.02, 0.06, 0.42), mat_idx=3)
            # Mango aislante rojo/naranja saliendo hacia adelante
            add_cylinder(bm, (bx, -0.06, cz + 0.04), radius=0.025, height=0.16, segments=12, mat_idx=2, axis='Y')
            
        # 4. Voltímetro analógico central superior en el fondo
        add_cylinder(bm, (0, 0.05, cz + 0.45), radius=0.075, height=0.03, segments=16, mat_idx=5, axis='Y')
        add_cylinder(bm, (0, 0.034, cz + 0.45), radius=0.06, height=0.005, segments=16, mat_idx=0, axis='Y')
        
        # 5. Pasamuros de conductos de potencia superior e inferior
        add_cylinder(bm, (-0.22, 0, cz + 0.68), radius=0.04, height=0.12, segments=12, mat_idx=0, axis='Z')
        add_cylinder(bm, ( 0.22, 0, cz + 0.68), radius=0.04, height=0.12, segments=12, mat_idx=0, axis='Z')
        add_cylinder(bm, (0, 0, cz - 0.68), radius=0.05, height=0.12, segments=12, mat_idx=0, axis='Z')

    mat_list = [
        mats['Cast_Iron'], mats['Dark_Gunmetal'], mats['Industrial_Orange'],
        mats['Pure_Copper'], mats['Ceramic_Insulator'], mats['Polished_Chrome'],
        mats['Hazard_Yellow']
    ]
    return create_mesh_object("SM_High_Voltage_Breaker_Box", col, geom, mat_list)

# -------------------------------------------------------------------------
# PROP 08: SM_Portable_Battery_Rack (Celdas elevadas y visibles)
# -------------------------------------------------------------------------
def build_prop08_battery_rack(col, mats):
    def geom(bm):
        cz = 0.35
        # 1. Carcasa / Jaula estructural naranja
        add_box(bm, (0, 0, cz - 0.04), (0.90, 0.55, 0.28), mat_idx=0)
        add_box(bm, (0, 0, cz), (0.80, 0.46, 0.24), mat_idx=1)
        
        # 2. Dos asas de goma ergonómicas en los extremos X
        add_box(bm, (-0.48, 0, cz + 0.04), (0.08, 0.24, 0.06), mat_idx=4)
        add_box(bm, ( 0.48, 0, cz + 0.04), (0.08, 0.24, 0.06), mat_idx=4)
        
        # 3. Cuatro celdas de combustible cilíndricas de grafeno elevadas y visibles
        for idx, bx in enumerate([-0.28, -0.09, 0.09, 0.28]):
            # Cilindro de celda
            add_cylinder(bm, (bx, 0, cz + 0.12), radius=0.085, height=0.40, segments=16, mat_idx=3, axis='Z')
            # Borne de cobre superior
            add_cylinder(bm, (bx, 0, cz + 0.33), radius=0.045, height=0.04, segments=14, mat_idx=2, axis='Z')
            # Barra LED vertical frontal emisiva (plasma cian)
            add_box(bm, (bx, -0.088, cz + 0.12), (0.05, 0.015, 0.28), mat_idx=5)
            
        # 4. Display frontal central de telemetría digital
        add_box(bm, (0, -0.28, cz - 0.02), (0.34, 0.04, 0.12), mat_idx=1)
        add_box(bm, (0, -0.302, cz - 0.02), (0.30, 0.005, 0.08), mat_idx=5)
        
        # 5. Conector de acople rápido macho trifásico lateral
        add_cylinder(bm, (0.47, 0, cz - 0.05), radius=0.05, height=0.06, segments=14, mat_idx=2, axis='X')

    mat_list = [
        mats['Industrial_Orange'], mats['Dark_Gunmetal'], mats['Pure_Copper'],
        mats['Graphene_Cell'], mats['Tire_Rubber_Black'], mats['Plasma_Cyan']
    ]
    return create_mesh_object("SM_Portable_Battery_Rack", col, geom, mat_list)

# -------------------------------------------------------------------------
# PROP 09: SM_Industrial_Cable_Reel (Orientado a 30 grados para ver bridas y cable)
# -------------------------------------------------------------------------
def build_prop09_cable_reel(col, mats):
    def geom(bm):
        cz = 0.50
        # 1. Carro tubular de soporte con ruedas de goma
        add_box(bm, (-0.32, 0, cz), (0.05, 0.05, 0.80), mat_idx=0)
        add_box(bm, ( 0.32, 0, cz), (0.05, 0.05, 0.80), mat_idx=0)
        add_box(bm, (0, 0, cz + 0.40), (0.68, 0.05, 0.05), mat_idx=0)
        
        # Dos ruedas traseras
        add_cylinder(bm, (-0.36, 0.25, cz - 0.35), radius=0.12, height=0.06, segments=16, mat_idx=3, axis='X')
        add_cylinder(bm, ( 0.36, 0.25, cz - 0.35), radius=0.12, height=0.06, segments=16, mat_idx=3, axis='X')
        
        # 2. Tambor central de acero con bridas circulares
        add_cylinder(bm, (-0.24, 0, cz), radius=0.32, height=0.03, segments=20, mat_idx=1, axis='X')
        add_cylinder(bm, ( 0.24, 0, cz), radius=0.32, height=0.03, segments=20, mat_idx=1, axis='X')
        add_cylinder(bm, (0, 0, cz), radius=0.14, height=0.45, segments=16, mat_idx=1, axis='X')
        
        # 3. Mazo de cable trifásico enrollado de caucho naranja
        add_cylinder(bm, (0, 0, cz), radius=0.28, height=0.42, segments=20, mat_idx=2, axis='X')
        
        # 4. Manivela de rebobinado lateral con mango giratorio
        add_cylinder(bm, (0.28, 0, cz), radius=0.03, height=0.06, segments=12, mat_idx=4, axis='X')
        add_box(bm, (0.32, 0.10, cz), (0.03, 0.22, 0.04), mat_idx=4)
        add_cylinder(bm, (0.35, 0.18, cz), radius=0.025, height=0.08, segments=12, mat_idx=3, axis='X')
        
        # 5. Extremo del cable desenrollado con enchufe industrial amarillo en el suelo
        add_cylinder(bm, (0.16, -0.28, cz - 0.20), radius=0.022, height=0.36, segments=10, mat_idx=2, axis='Z')
        add_cylinder(bm, (0.16, -0.28, cz - 0.40), radius=0.055, height=0.12, segments=14, mat_idx=5, axis='Z')
        add_cylinder(bm, (0.16, -0.28, cz - 0.47), radius=0.022, height=0.03, segments=8, mat_idx=4, axis='Z')

    mat_list = [
        mats['Industrial_Orange'], mats['Dark_Gunmetal'], mats['Cable_Rubber_Orange'],
        mats['Tire_Rubber_Black'], mats['Machinery_Brass'], mats['Hazard_Yellow']
    ]
    return create_mesh_object("SM_Industrial_Cable_Reel", col, geom, mat_list)

# -------------------------------------------------------------------------
# PROP 10: SM_Emergency_Capacitor_Bank (Rack abierto transparente de alta energía)
# -------------------------------------------------------------------------
def build_prop10_capacitor_bank(col, mats):
    def geom(bm):
        cz = 1.05
        # 1. Bastidor de rack abierto de 4 columnas de acero (120 x 60 x 200 cm)
        for rx in [-0.55, 0.55]:
            for ry in [-0.26, 0.26]:
                add_box(bm, (rx, ry, cz), (0.08, 0.08, 1.95), mat_idx=1)
        # Travesaños
        for pz in [cz - 0.90, cz, cz + 0.90]:
            add_box(bm, (0, -0.26, pz), (1.18, 0.06, 0.06), mat_idx=1)
            add_box(bm, (0,  0.26, pz), (1.18, 0.06, 0.06), mat_idx=1)
            add_box(bm, (-0.55, 0, pz), (0.06, 0.58, 0.06), mat_idx=1)
            add_box(bm, ( 0.55, 0, pz), (0.06, 0.58, 0.06), mat_idx=1)
            
        # 2. Seis condensadores cilíndricos de aluminio pulido (2 pisos x 3 condensadores)
        cap_xs = [-0.36, 0.0, 0.36]
        for cx in cap_xs:
            for pz in [cz - 0.42, cz + 0.38]:
                add_cylinder(bm, (cx, 0, pz), radius=0.14, height=0.52, segments=18, mat_idx=4, axis='Z')
                add_cylinder(bm, (cx, 0, pz + 0.28), radius=0.05, height=0.08, segments=12, mat_idx=3, axis='Z')
                add_cylinder(bm, (cx, 0, pz + 0.33), radius=0.025, height=0.04, segments=10, mat_idx=2, axis='Z')
                
        # 3. Pletinas de interconexión (Busbars masivas de cobre)
        add_box(bm, (0, 0, cz - 0.08), (0.86, 0.04, 0.03), mat_idx=2)
        add_box(bm, (0, 0, cz + 0.72), (0.86, 0.04, 0.03), mat_idx=2)
        
        # 4. Brecha de descarga de chispa (Spark Gap) central con plasma cian
        add_cylinder(bm, (0, -0.15, cz), radius=0.065, height=0.08, segments=14, mat_idx=5, axis='Y')
        add_cylinder(bm, (-0.10, -0.15, cz), radius=0.025, height=0.12, segments=10, mat_idx=2, axis='X')
        add_cylinder(bm, ( 0.10, -0.15, cz), radius=0.025, height=0.12, segments=10, mat_idx=2, axis='X')
        
        # 5. Palanca masiva de descarga de emergencia (Dump switch)
        add_box(bm, (0.58, -0.10, cz), (0.08, 0.16, 0.35), mat_idx=0)
        add_cylinder(bm, (0.64, -0.10, cz - 0.05), radius=0.03, height=0.10, segments=12, mat_idx=2, axis='X')
        add_box(bm, (0.64, -0.22, cz + 0.10), (0.04, 0.22, 0.05), mat_idx=6)
        
        # 6. Barra indicadora de carga LED y baliza superior
        for b_idx in range(5):
            add_cylinder(bm, (-0.56, -0.20, cz + 0.40 + b_idx * 0.07), radius=0.025, height=0.02, segments=10, mat_idx=5, axis='Y')
        add_cylinder(bm, (0, 0, cz + 1.02), radius=0.07, height=0.12, segments=16, mat_idx=7, axis='Z')

    mat_list = [
        mats['Cast_Iron'], mats['Dark_Gunmetal'], mats['Pure_Copper'],
        mats['Ceramic_Insulator'], mats['Polished_Chrome'], mats['Plasma_Cyan'],
        mats['LED_Red'], mats['LED_Amber']
    ]
    return create_mesh_object("SM_Emergency_Capacitor_Bank", col, geom, mat_list)

# -------------------------------------------------------------------------
# ESCENOGRAFÍA: PEDESTALES DE EXPOSICIÓN Y PLACAS GRABADAS
# -------------------------------------------------------------------------
def build_pedestal(col, mats, name, pos_x, width=2.4, depth=1.8, height=0.16, label_text="PROP"):
    def geom(bm):
        add_box(bm, (pos_x, 0, height*0.5), (width, depth, height), mat_idx=0)
        add_box(bm, (pos_x, 0, height + 0.01), (width - 0.08, depth - 0.08, 0.02), mat_idx=0)
        add_box(bm, (pos_x, -depth*0.5 - 0.01, height*0.6), (0.75, 0.02, 0.09), mat_idx=1)
        
    mat_list = [mats['Plinth_Dark'], mats['Plinth_Plaque']]
    return create_mesh_object(f"Plinth_{name}", col, geom, mat_list)

# -------------------------------------------------------------------------
# ILUMINACIÓN FOTOMÉTRICA DE ESTUDIO
# -------------------------------------------------------------------------
def setup_lighting(col):
    key_data = bpy.data.lights.new(name="Light_Key_Overhead", type='AREA')
    key_data.energy = 1100.0
    key_data.size = 22.0
    key_data.size_y = 8.0
    key_data.color = (1.0, 0.96, 0.92)
    key_obj = bpy.data.objects.new("Light_Key_Overhead", key_data)
    key_obj.location = (0, -4.5, 6.2)
    key_obj.rotation_euler = (R(35), 0, 0)
    col.objects.link(key_obj)
    
    rim_data = bpy.data.lights.new(name="Light_Rim_Back", type='AREA')
    rim_data.energy = 850.0
    rim_data.size = 24.0
    rim_data.size_y = 4.0
    rim_data.color = (0.85, 0.95, 1.0)
    rim_obj = bpy.data.objects.new("Light_Rim_Back", rim_data)
    rim_obj.location = (0, 3.5, 5.0)
    rim_obj.rotation_euler = (R(-40), 0, R(180))
    col.objects.link(rim_obj)
    
    fill_l_data = bpy.data.lights.new(name="Light_Fill_Cyan", type='AREA')
    fill_l_data.energy = 520.0
    fill_l_data.size = 8.0
    fill_l_data.color = (0.78, 0.90, 1.0)
    fill_l_obj = bpy.data.objects.new("Light_Fill_Cyan", fill_l_data)
    fill_l_obj.location = (-11.0, -5.5, 4.2)
    fill_l_obj.rotation_euler = (R(30), R(-25), R(-40))
    col.objects.link(fill_l_obj)
    
    fill_r_data = bpy.data.lights.new(name="Light_Fill_Amber", type='AREA')
    fill_r_data.energy = 520.0
    fill_r_data.size = 8.0
    fill_r_data.color = (1.0, 0.85, 0.68)
    fill_r_obj = bpy.data.objects.new("Light_Fill_Amber", fill_r_data)
    fill_r_obj.location = (11.0, -5.5, 4.2)
    fill_r_obj.rotation_euler = (R(30), R(25), R(40))
    col.objects.link(fill_r_obj)

def create_camera_tracking(col, name, cam_pos, target_pos, lens=45.0):
    cam_data = bpy.data.cameras.new(name)
    cam_data.lens = lens
    cam_data.clip_start = 0.1
    cam_data.clip_end = 250.0
    cam_obj = bpy.data.objects.new(name, cam_data)
    cam_obj.location = cam_pos
    col.objects.link(cam_obj)
    
    empty_target = bpy.data.objects.new(f"Target_{name}", None)
    empty_target.location = target_pos
    col.objects.link(empty_target)
    
    tt = cam_obj.constraints.new(type='TRACK_TO')
    tt.target = empty_target
    tt.track_axis = 'TRACK_NEGATIVE_Z'
    tt.up_axis = 'UP_Y'
    
    return cam_obj

# -------------------------------------------------------------------------
# COMPOSITOR DE LA LÁMINA MAESTRA 2.5K
# -------------------------------------------------------------------------
def assemble_master_infographic():
    print("\n[COMPOSITOR] Ensamblando Lámina Maestra Infográfica 2.5K (2560x1440)...")
    W, H = 2560, 1440
    canvas = Image.new("RGBA", (W, H), (14, 16, 20, 255))
    draw = ImageDraw.Draw(canvas)
    
    try:
        font_title = ImageFont.truetype("arialbd.ttf", 26)
        font_sub = ImageFont.truetype("arialbd.ttf", 15)
        font_pill = ImageFont.truetype("arialbd.ttf", 13)
        font_card_title = ImageFont.truetype("arialbd.ttf", 17)
        font_card_desc = ImageFont.truetype("arial.ttf", 13)
    except:
        font_title = font_sub = font_pill = font_card_title = font_card_desc = ImageFont.load_default()
        
    draw.text((40, 20), "ASTRA HAZARD // REPOSITORIO DE ARQUITECTURA Y PROPS INTERACTIVOS", fill=(245, 166, 35), font=font_sub)
    draw.text((40, 46), "CATÁLOGO DE PROPS - LOTE 2 (PROPS 06-10): ENERGÍA, GENERADORES Y RED AUXILIAR", fill=(255, 255, 255), font=font_title)
    
    pills = [
        ("LOTE 2 DE 10", (211, 84, 0)),
        ("RED ELÉCTRICA DINÁMICA", (41, 128, 185)),
        ("COLISIÓN UCX READY", (39, 174, 96)),
        ("FREESTYLE INK", (142, 68, 173)),
        ("BLENDER 5.2 LTS", (108, 92, 231))
    ]
    cur_x = W - 40
    for text, bg_col in reversed(pills):
        tw = len(text) * 8 + 20
        cur_x -= tw
        draw.rounded_rectangle((cur_x, 38, cur_x + tw - 8, 68), radius=5, fill=bg_col)
        draw.text((cur_x + 8, 45), text, fill=(255, 255, 255), font=font_pill)
        cur_x -= 8
        
    draw.line((40, 95, W - 40, 95), fill=(45, 52, 65), width=2)
    
    pan_path = os.path.join(RENDERS_DIR, "Showcase_Lote2_Props_Panorama.png")
    if os.path.exists(pan_path):
        pan_img = Image.open(pan_path).convert("RGBA")
        pan_w = W - 80
        pan_h = 760
        pan_resized = pan_img.resize((pan_w, pan_h), Image.Resampling.LANCZOS)
        canvas.paste(pan_resized, (40, 110))
        draw.rectangle((40, 110, 40 + pan_w, 110 + pan_h), outline=(45, 52, 65), width=2)
        
    props_cards = [
        ("06. SM_Backup_Diesel_Generator", "Showcase_Prop06_Backup_Diesel_Generator.png", (245, 166, 35),
         "• Generador de combustión en patín de vigas\n• Radiador masivo con chevrons amarillos\n• Tirador manual de arranque y silenciador\n• Tacómetro analógico y nivel de diésel"),
         
        ("07. SM_High_Voltage_Breaker_Box", "Showcase_Prop07_High_Voltage_Breaker_Box.png", (41, 128, 185),
         "• Cuadro eléctrico con puerta abierta a 70°\n• 3 disyuntores de cuchilla de cobre puro\n• Aisladores cerámicos y voltímetro 480V\n• Placa de peligro por alto voltaje"),
         
        ("08. SM_Portable_Battery_Rack", "Showcase_Prop08_Portable_Battery_Rack.png", (231, 76, 60),
         "• Rack transportable con doble asa de goma\n• 4 celdas de grafeno con barras LED cian\n• Telemetría digital y borne de conexión\n• Compatible con ICarriableInterface"),
         
        ("09. SM_Industrial_Cable_Reel", "Showcase_Prop09_Industrial_Cable_Reel.png", (155, 89, 182),
         "• Carro de acero móvil con ruedas de goma\n• Bobina con cable trifásico caucho naranja\n• Manivela de rebobinado manual lateral\n• Clavija industrial de bloqueo por giro"),
         
        ("10. SM_Emergency_Capacitor_Bank", "Showcase_Prop10_Emergency_Capacitor_Bank.png", (26, 188, 156),
         "• Rack abierto con 6 condensadores de aluminio\n• Busbars masivas de cobre y spark-gap\n• Descarga por plasma cian para pulsos EMP\n• Palanca manual roja e indicador de carga")
    ]
    
    card_w = (W - 80 - (4 * 15)) // 5
    card_h = 510
    card_y = 890
    
    for i, (title, img_name, border_col, desc) in enumerate(props_cards):
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
        draw.text((cx + 10, card_y + 311), title, fill=border_col, font=font_card_title)
        
        draw.text((cx + 12, card_y + 348), desc, fill=(210, 220, 235), font=font_card_desc, spacing=4)

    master_path = os.path.join(RENDERS_DIR, "Showcase_Lote2_Props_Master.png")
    canvas.save(master_path, "PNG")
    
    shutil.copy2(master_path, os.path.join(ARTIFACT_DIR, "Showcase_Lote2_Props_Master.png"))
    for _, fname, _, _ in props_cards:
        fsrc = os.path.join(RENDERS_DIR, fname)
        if os.path.exists(fsrc):
            shutil.copy2(fsrc, os.path.join(ARTIFACT_DIR, fname))
    if os.path.exists(pan_path):
        shutil.copy2(pan_path, os.path.join(ARTIFACT_DIR, "Showcase_Lote2_Props_Panorama.png"))
        
    print(f"\n[MASTER OK] Lámina Maestra Oficial generada con éxito: {master_path}")

# -------------------------------------------------------------------------
# FLUJO PRINCIPAL DE PRODUCCIÓN Y RENDER
# -------------------------------------------------------------------------
def main():
    print("=" * 80)
    print("ASTRA HAZARD - GENERADOR MAESTRO 3D (LOTE 2 DE PROPS V3)")
    print("ENERGÍA, GENERADORES Y RED ELÉCTRICA AUXILIAR")
    print("=" * 80)
    
    scene = reset_scene()
    mats = create_materials()
    
    col_props = create_collection("Props_Lote2")
    col_env = create_collection("Showroom_Environment")
    col_lights = create_collection("Lighting")
    col_cams = create_collection("Cameras")
    
    # Suelo de estudio infinito (36 x 24 m)
    mesh_floor = bpy.data.meshes.new("Studio_Floor")
    bm_f = bmesh.new()
    add_box(bm_f, (0, 0, -0.05), (36.0, 24.0, 0.10), mat_idx=0)
    bm_f.to_mesh(mesh_floor)
    bm_f.free()
    floor_obj = bpy.data.objects.new("Studio_Floor", mesh_floor)
    floor_obj.data.materials.append(mats['Studio_Floor'])
    col_env.objects.link(floor_obj)
    
    # Configuración de los 5 Props con encuadres y targets optimizados
    prop_configs = [
        {"id": 6, "x": -6.4, "name": "Backup_Diesel_Generator", "label": "06 // DIESEL GENERATOR", "build": build_prop06_diesel_generator, "w": 2.2, "d": 1.6, "cam_dist": 4.2, "cam_z": 1.35, "targ_z": 0.70},
        {"id": 7, "x": -3.2, "name": "High_Voltage_Breaker_Box", "label": "07 // BREAKER BOX 480V", "build": build_prop07_breaker_box, "w": 1.8, "d": 1.6, "cam_dist": 2.8, "cam_z": 1.10, "targ_z": 0.85},
        {"id": 8, "x":  0.0, "name": "Portable_Battery_Rack", "label": "08 // PORTABLE BATTERY RACK", "build": build_prop08_battery_rack, "w": 1.8, "d": 1.6, "cam_dist": 1.9, "cam_z": 0.75, "targ_z": 0.38},
        {"id": 9, "x":  3.2, "name": "Industrial_Cable_Reel", "label": "09 // INDUSTRIAL CABLE REEL", "build": build_prop09_cable_reel, "w": 1.8, "d": 1.6, "cam_dist": 2.5, "cam_z": 0.85, "targ_z": 0.50},
        {"id": 10, "x": 6.4, "name": "Emergency_Capacitor_Bank", "label": "10 // CAPACITOR BANK EMP", "build": build_prop10_capacitor_bank, "w": 2.0, "d": 1.6, "cam_dist": 4.6, "cam_z": 1.55, "targ_z": 1.05},
    ]
    
    props_created = []
    for cfg in prop_configs:
        build_pedestal(col_env, mats, cfg['name'], pos_x=cfg['x'], width=cfg['w'], depth=cfg['d'], label_text=cfg['label'])
        obj = cfg['build'](col_props, mats)
        obj.location.x = cfg['x']
        obj.location.z = 0.16 # Montado sobre el plinto
        props_created.append(obj)
        print(f"  [OK] Creado Prop {cfg['id']:02d}: {obj.name} en X={cfg['x']}")
        
    setup_lighting(col_lights)
    
    # Panorama General
    cam_pan_data = bpy.data.cameras.new("Cam_Panorama")
    cam_pan_data.lens = 28.0
    cam_pan_data.clip_start = 0.1
    cam_pan_data.clip_end = 250.0
    cam_pan = bpy.data.objects.new("Cam_Panorama", cam_pan_data)
    cam_pan.location = (0.0, -14.2, 4.0)
    cam_pan.rotation_euler = (R(75.5), 0, 0)
    col_cams.objects.link(cam_pan)
    
    ind_cams = []
    for cfg in prop_configs:
        c_name = f"Cam_Prop{cfg['id']:02d}_{cfg['name']}"
        cam_pos = (cfg['x'] + (cfg['cam_dist'] * 0.45), -(cfg['cam_dist'] * 0.89), cfg['cam_z'])
        targ_pos = (cfg['x'], 0.0, cfg['targ_z'])
        
        cam = create_camera_tracking(col_cams, c_name, cam_pos, targ_pos, lens=42.0)
        ind_cams.append((cam, f"Showcase_Prop{cfg['id']:02d}_{cfg['name']}.png"))
        
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_FILE)
    print(f"\n[OK] Escena Blend guardada: {BLEND_FILE}")
    
    print("\n[RENDER] Generando secuencias fotográficas en EEVEE...")
    
    # Panorama General
    scene.camera = cam_pan
    scene.render.resolution_x = 2560
    scene.render.resolution_y = 900
    scene.render.filepath = os.path.join(RENDERS_DIR, "Showcase_Lote2_Props_Panorama.png")
    bpy.ops.render.render(write_still=True)
    print("  [OK] Renderizado Panorama General.")
    
    # Close-ups individuales
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    for cam, fname in ind_cams:
        scene.camera = cam
        scene.render.filepath = os.path.join(RENDERS_DIR, fname)
        bpy.ops.render.render(write_still=True)
        print(f"  [OK] Renderizado Close-Up: {fname}")
        
    assemble_master_infographic()
    print("\n" + "=" * 80)
    print("LOTE 2 DE PROPS MAESTROS COMPLETADO CON ÉXITO")
    print("=" * 80)

if __name__ == "__main__":
    main()

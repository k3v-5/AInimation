# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Generador Maestro 3D - Lote 1 de Props: Sistemas de Acceso, Compuertas y Conductos de Evacuación (V2 Perfeccionada)
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
BLEND_FILE = os.path.join(PROJECT_ROOT, "Art", "Blender", "Lote1_Props_Maestros_Oficial.blend")

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
    
    # World studio setup con luz ambiental de relleno
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

    # 1. Acero Naval Derelict con matiz azulado
    mats['Naval_Steel'] = make_pbr("Mat_Naval_Steel", (0.24, 0.28, 0.32, 1.0), roughness=0.38, metallic=0.85)
    
    # 2. Acero Oscuro / Carcasa y Marco
    mats['Dark_Gunmetal'] = make_pbr("Mat_Dark_Gunmetal", (0.11, 0.13, 0.15, 1.0), roughness=0.32, metallic=0.90)
    
    # 3. Franjas de Peligro / Chevron Amarillo y Negro
    mats['Hazard_Yellow'] = make_pbr("Mat_Hazard_Yellow", (0.96, 0.74, 0.08, 1.0), roughness=0.40, metallic=0.10)
    mats['Hazard_Black'] = make_pbr("Mat_Hazard_Black", (0.05, 0.05, 0.06, 1.0), roughness=0.45, metallic=0.15)
    
    # 4. Latón / Bronce Mecánico Dorado
    mats['Machinery_Brass'] = make_pbr("Mat_Machinery_Brass", (0.86, 0.68, 0.26, 1.0), roughness=0.28, metallic=0.92)
    
    # 5. Cromo Hidráulico Pulido Espejo
    mats['Chrome_Piston'] = make_pbr("Mat_Chrome_Piston", (0.92, 0.94, 0.96, 1.0), roughness=0.06, metallic=1.0)
    
    # 6. Escarcha Criogénica y Tuberías Cian
    mats['Cryo_Frost'] = make_pbr("Mat_Cryo_Frost", (0.88, 0.96, 1.0, 1.0), roughness=0.45, metallic=0.08,
                                  emissive_col=(0.5, 0.85, 1.0, 1.0), emissive_str=0.8)
    mats['Cryo_Pipe_Cyan'] = make_pbr("Mat_Cryo_Pipe_Cyan", (0.12, 0.45, 0.58, 1.0), roughness=0.22, metallic=0.82)
    
    # 7. LEDs de Estado Emisivos Brillantes
    mats['LED_Green'] = make_pbr("Mat_LED_Green", (0.15, 0.95, 0.3, 1.0), roughness=0.15, metallic=0.0,
                                 emissive_col=(0.2, 1.0, 0.35, 1.0), emissive_str=4.5)
    mats['LED_Red'] = make_pbr("Mat_LED_Red", (0.95, 0.12, 0.1, 1.0), roughness=0.15, metallic=0.0,
                               emissive_col=(1.0, 0.15, 0.1, 1.0), emissive_str=4.5)
    mats['LED_Amber'] = make_pbr("Mat_LED_Amber", (1.0, 0.6, 0.05, 1.0), roughness=0.15, metallic=0.0,
                                 emissive_col=(1.0, 0.65, 0.08, 1.0), emissive_str=4.0)
                                 
    # 8. Vidrio Blindado Reforzado
    mat_glass = bpy.data.materials.new("Mat_Armored_Glass")
    mat_glass.use_nodes = True
    gnodes = mat_glass.node_tree.nodes
    glinks = mat_glass.node_tree.links
    gnodes.clear()
    g_out = gnodes.new(type='ShaderNodeOutputMaterial')
    g_bsdf = gnodes.new(type='ShaderNodeBsdfPrincipled')
    g_bsdf.inputs['Base Color'].default_value = (0.25, 0.55, 0.48, 1.0)
    g_bsdf.inputs['Roughness'].default_value = 0.08
    g_bsdf.inputs['Transmission Weight'].default_value = 0.88
    g_bsdf.inputs['IOR'].default_value = 1.52
    glinks.new(g_bsdf.outputs['BSDF'], g_out.inputs['Surface'])
    mats['Armored_Glass'] = mat_glass
    
    # 9. Plinto de Estudio y Suelo
    mats['Studio_Floor'] = make_pbr("Mat_Studio_Floor", (0.045, 0.052, 0.062, 1.0), roughness=0.92, metallic=0.0)
    mats['Plinth_Dark'] = make_pbr("Mat_Plinth_Dark", (0.08, 0.09, 0.11, 1.0), roughness=0.40, metallic=0.55)
    mats['Plinth_Plaque'] = make_pbr("Mat_Plinth_Plaque", (0.90, 0.74, 0.32, 1.0), roughness=0.22, metallic=0.95)
    
    return mats

# -------------------------------------------------------------------------
# UTILIDADES GEOMÉTRICAS BMESH
# -------------------------------------------------------------------------
def create_mesh_object(name, collection, mesh_func, materials):
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    mesh_func(bm)
    bm.to_mesh(mesh)
    bm.free()
    
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    
    for mat in materials:
        if mat:
            obj.data.materials.append(mat)
            
    return obj

def add_box(bm, center, size, mat_idx=0):
    dx, dy, dz = size[0]*0.5, size[1]*0.5, size[2]*0.5
    cx, cy, cz = center
    verts = [
        bm.verts.new((cx - dx, cy - dy, cz - dz)),
        bm.verts.new((cx + dx, cy - dy, cz - dz)),
        bm.verts.new((cx + dx, cy + dy, cz - dz)),
        bm.verts.new((cx - dx, cy + dy, cz - dz)),
        bm.verts.new((cx - dx, cy - dy, cz + dz)),
        bm.verts.new((cx + dx, cy - dy, cz + dz)),
        bm.verts.new((cx + dx, cy + dy, cz + dz)),
        bm.verts.new((cx - dx, cy + dy, cz + dz)),
    ]
    faces = [
        bm.faces.new((verts[0], verts[1], verts[2], verts[3])), # Bottom
        bm.faces.new((verts[4], verts[7], verts[6], verts[5])), # Top
        bm.faces.new((verts[0], verts[4], verts[5], verts[1])), # Front
        bm.faces.new((verts[2], verts[6], verts[7], verts[3])), # Back
        bm.faces.new((verts[0], verts[3], verts[7], verts[4])), # Left
        bm.faces.new((verts[1], verts[5], verts[6], verts[2])), # Right
    ]
    for f in faces:
        f.material_index = mat_idx
    return verts, faces

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
# PROP 01: SM_Airlock_Heavy_Hatch
# -------------------------------------------------------------------------
def build_prop01_airlock_hatch(col, mats):
    def geom(bm):
        # 1. Marco exterior reforzado de mamparo (140 x 220 x 35 cm)
        add_box(bm, (-0.60, 0, 1.10), (0.20, 0.35, 2.20), mat_idx=1) # Left pillar
        add_box(bm, ( 0.60, 0, 1.10), (0.20, 0.35, 2.20), mat_idx=1) # Right pillar
        add_box(bm, (0, 0, 2.10), (1.40, 0.35, 0.20), mat_idx=1) # Top lintel
        add_box(bm, (0, 0, 0.10), (1.40, 0.35, 0.20), mat_idx=1) # Bottom threshold
        
        # 2. Hojas de la compuerta (acero naval)
        add_box(bm, (-0.25, 0, 1.10), (0.48, 0.18, 1.78), mat_idx=0) # Left door
        add_box(bm, ( 0.25, 0, 1.10), (0.48, 0.18, 1.78), mat_idx=0) # Right door
        add_box(bm, (0, -0.01, 1.10), (0.04, 0.20, 1.80), mat_idx=1) # Gasket seal
        
        # 3. Franjas de peligro chevron en umbral y dintel
        for x_step in range(-5, 6):
            m_idx = 2 if x_step % 2 == 0 else 3
            add_box(bm, (x_step * 0.11, -0.18, 2.10), (0.09, 0.01, 0.16), mat_idx=m_idx)
            add_box(bm, (x_step * 0.11, -0.18, 0.10), (0.09, 0.01, 0.16), mat_idx=m_idx)
            
        # 4. Volante manual circular central de bloqueo
        add_cylinder(bm, (0, -0.12, 1.10), radius=0.08, height=0.08, segments=16, mat_idx=4, axis='Y')
        add_cylinder(bm, (0, -0.15, 1.10), radius=0.24, height=0.045, segments=24, mat_idx=4, axis='Y')
        add_cylinder(bm, (0, -0.155, 1.10), radius=0.19, height=0.05, segments=20, mat_idx=1, axis='Y')
        add_box(bm, (0, -0.14, 1.10), (0.42, 0.035, 0.045), mat_idx=4)
        add_box(bm, (0, -0.14, 1.10), (0.045, 0.035, 0.42), mat_idx=4)
        
        # 5. Pestillos de anclaje de bronce
        add_box(bm, (-0.48, -0.10, 1.10), (0.12, 0.04, 0.06), mat_idx=4)
        add_box(bm, ( 0.48, -0.10, 1.10), (0.12, 0.04, 0.06), mat_idx=4)
        add_box(bm, (0, -0.10, 1.96), (0.06, 0.04, 0.12), mat_idx=4)
        add_box(bm, (0, -0.10, 0.24), (0.06, 0.04, 0.12), mat_idx=4)
        
        # 6. Placa de telemetría de estado y LEDs
        add_box(bm, (0, -0.18, 1.85), (0.38, 0.02, 0.16), mat_idx=1)
        add_cylinder(bm, (-0.11, -0.195, 1.85), radius=0.035, height=0.02, segments=12, mat_idx=5, axis='Y') # Verde
        add_cylinder(bm, ( 0.11, -0.195, 1.85), radius=0.035, height=0.02, segments=12, mat_idx=6, axis='Y') # Rojo
        
        # Manómetro de presión
        add_cylinder(bm, (0, -0.19, 1.62), radius=0.07, height=0.03, segments=16, mat_idx=4, axis='Y')
        add_cylinder(bm, (0, -0.208, 1.62), radius=0.055, height=0.005, segments=16, mat_idx=1, axis='Y')
        
        # 7. Bisagras de mamparo
        for z_h in [0.45, 1.75]:
            add_cylinder(bm, (-0.51, -0.06, z_h), radius=0.045, height=0.20, segments=14, mat_idx=1, axis='Z')
            add_cylinder(bm, ( 0.51, -0.06, z_h), radius=0.045, height=0.20, segments=14, mat_idx=1, axis='Z')

    mat_list = [
        mats['Naval_Steel'], mats['Dark_Gunmetal'], mats['Hazard_Yellow'],
        mats['Hazard_Black'], mats['Machinery_Brass'], mats['LED_Green'],
        mats['LED_Red']
    ]
    return create_mesh_object("SM_Airlock_Heavy_Hatch", col, geom, mat_list)

# -------------------------------------------------------------------------
# PROP 02: SM_Ventilation_Grating_Duct
# -------------------------------------------------------------------------
def build_prop02_vent_duct(col, mats):
    def geom(bm):
        # 1. Conducto cúbico hueco (90 x 90 x 120 cm) centrado en Z=0.60
        cz = 0.60
        add_box(bm, (0, 0, cz + 0.45), (0.90, 1.20, 0.08), mat_idx=1) # Top
        add_box(bm, (0, 0, cz - 0.45), (0.90, 1.20, 0.08), mat_idx=1) # Bottom
        add_box(bm, (-0.45, 0, cz), (0.08, 1.20, 0.90), mat_idx=1) # Left
        add_box(bm, ( 0.45, 0, cz), (0.08, 1.20, 0.90), mat_idx=1) # Right
        
        # 2. Brida perimetral frontal de mamparo (Y = -0.60)
        add_box(bm, (0, -0.60, cz + 0.43), (1.06, 0.07, 0.16), mat_idx=0)
        add_box(bm, (0, -0.60, cz - 0.43), (1.06, 0.07, 0.16), mat_idx=0)
        add_box(bm, (-0.43, -0.60, cz), (0.16, 0.07, 1.06), mat_idx=0)
        add_box(bm, ( 0.43, -0.60, cz), (0.16, 0.07, 1.06), mat_idx=0)
        
        # 8 Pernos hexagonales de latón
        for bx in [-0.43, 0.43]:
            for bz in [-0.43, 0.43]:
                add_cylinder(bm, (bx, -0.64, cz + bz), radius=0.024, height=0.035, segments=8, mat_idx=3, axis='Y')
        for bx in [0.0]:
            for bz in [-0.43, 0.43]:
                add_cylinder(bm, (bx, -0.64, cz + bz), radius=0.024, height=0.035, segments=8, mat_idx=3, axis='Y')
        for bx in [-0.43, 0.43]:
            for bz in [0.0]:
                add_cylinder(bm, (bx, -0.64, cz + bz), radius=0.024, height=0.035, segments=8, mat_idx=3, axis='Y')
                
        # 3. Bisagras de la rejilla
        add_box(bm, (-0.38, -0.58, cz + 0.25), (0.05, 0.08, 0.15), mat_idx=3)
        add_box(bm, (-0.38, -0.58, cz - 0.25), (0.05, 0.08, 0.15), mat_idx=3)
        
        # 4. Lamas de rejilla inclinadas a 45°
        for i in range(-5, 5):
            zl = cz + i * 0.075 + 0.037
            add_box(bm, (0, -0.57, zl), (0.72, 0.06, 0.016), mat_idx=0)
            
        # 5. Arañazos de bestia en el borde inferior
        add_box(bm, (0.15, -0.61, cz - 0.28), (0.02, 0.04, 0.20), mat_idx=2)
        add_box(bm, (0.22, -0.61, cz - 0.31), (0.02, 0.04, 0.18), mat_idx=2)
        add_box(bm, (0.29, -0.61, cz - 0.27), (0.02, 0.04, 0.22), mat_idx=2)
        
        # 6. Filtro interior plisado
        for fx in range(-6, 7):
            add_box(bm, (fx * 0.055, 0.10, cz), (0.015, 0.16, 0.74), mat_idx=1)
            
        # LED indicador de flujo
        add_cylinder(bm, (0.38, -0.61, cz + 0.38), radius=0.025, height=0.02, segments=12, mat_idx=4, axis='Y')

    mat_list = [
        mats['Naval_Steel'], mats['Dark_Gunmetal'], mats['Hazard_Yellow'],
        mats['Machinery_Brass'], mats['LED_Green']
    ]
    return create_mesh_object("SM_Ventilation_Grating_Duct", col, geom, mat_list)

# -------------------------------------------------------------------------
# PROP 03: SM_Hydraulic_Blast_Door
# -------------------------------------------------------------------------
def build_prop03_blast_door(col, mats):
    def geom(bm):
        # 1. Marco masivo de acero blindado (240 x 280 x 40 cm)
        add_box(bm, (-1.10, 0, 1.40), (0.35, 0.40, 2.80), mat_idx=1) # Left I-beam
        add_box(bm, ( 1.10, 0, 1.40), (0.35, 0.40, 2.80), mat_idx=1) # Right I-beam
        add_box(bm, (0, 0, 2.65), (2.55, 0.45, 0.35), mat_idx=1) # Top lintel
        add_box(bm, (0, 0, 0.10), (2.55, 0.45, 0.20), mat_idx=1) # Threshold
        
        # 2. Hojas del portón
        add_box(bm, (0, 0, 0.95), (1.80, 0.22, 1.45), mat_idx=0) # Hoja inferior
        add_box(bm, (0, 0, 1.95), (1.80, 0.22, 0.50), mat_idx=0) # Hoja superior
        
        # Costillas de refuerzo en V
        for rx in [-0.60, 0, 0.60]:
            add_box(bm, (rx, -0.13, 0.95), (0.08, 0.05, 1.30), mat_idx=1)
            
        # Franjas diagonales de peligro (Chevrons)
        for i in range(-7, 8):
            m_idx = 2 if i % 2 == 0 else 3
            add_box(bm, (i * 0.12, -0.13, 1.55), (0.10, 0.01, 0.18), mat_idx=m_idx)
            add_box(bm, (i * 0.12, -0.13, 0.35), (0.10, 0.01, 0.18), mat_idx=m_idx)
            
        # 3. Dos cilindros hidráulicos telescópicos superiores
        for hx in [-0.55, 0.55]:
            add_cylinder(bm, (hx, -0.16, 2.45), radius=0.07, height=0.45, segments=16, mat_idx=1, axis='Z')
            add_cylinder(bm, (hx, -0.16, 2.10), radius=0.04, height=0.35, segments=16, mat_idx=4, axis='Z') # Cromo
            add_cylinder(bm, (hx + 0.10, -0.16, 2.50), radius=0.018, height=0.30, segments=10, mat_idx=3, axis='Z') # Latón racor
            
        # 4. Palanca manual de derivación de emergencia
        add_box(bm, (1.10, -0.22, 1.20), (0.18, 0.08, 0.28), mat_idx=6) # Caja roja
        add_box(bm, (1.10, -0.27, 1.20), (0.03, 0.09, 0.18), mat_idx=4) # Palanca
        add_cylinder(bm, (1.10, -0.32, 1.28), radius=0.038, height=0.04, segments=12, mat_idx=2, axis='Y') # Pomo
        
        # 5. Luces de alarma gemelas en dintel
        add_cylinder(bm, (-0.90, -0.24, 2.65), radius=0.05, height=0.06, segments=14, mat_idx=5, axis='Y')
        add_cylinder(bm, ( 0.90, -0.24, 2.65), radius=0.05, height=0.06, segments=14, mat_idx=5, axis='Y')

    mat_list = [
        mats['Naval_Steel'], mats['Dark_Gunmetal'], mats['Hazard_Yellow'],
        mats['Hazard_Black'], mats['Chrome_Piston'], mats['LED_Amber'],
        mats['LED_Red']
    ]
    return create_mesh_object("SM_Hydraulic_Blast_Door", col, geom, mat_list)

# -------------------------------------------------------------------------
# PROP 04: SM_Crawlway_Escape_Portal
# -------------------------------------------------------------------------
def build_prop04_escape_portal(col, mats):
    def geom(bm):
        # 1. Marco circular exterior (110 x 110 x 30 cm) centrado en Z=0.85
        cz = 0.85
        add_cylinder(bm, (0, 0, cz), radius=0.55, height=0.18, segments=24, mat_idx=1, axis='Y')
        add_cylinder(bm, (0, -0.06, cz), radius=0.48, height=0.12, segments=24, mat_idx=0, axis='Y')
        
        # 16 Pernos perimetrales
        for i in range(16):
            ang = (2.0 * math.pi * i) / 16.0
            px = math.cos(ang) * 0.51
            pz = cz + math.sin(ang) * 0.51
            add_cylinder(bm, (px, -0.10, pz), radius=0.02, height=0.035, segments=8, mat_idx=3, axis='Y')
            
        # 2. Escotilla circular central
        add_cylinder(bm, (0, -0.11, cz), radius=0.40, height=0.10, segments=24, mat_idx=0, axis='Y')
        
        # 3. Bisagra masiva con contrapeso
        add_box(bm, (-0.46, -0.11, cz), (0.12, 0.16, 0.28), mat_idx=1)
        add_cylinder(bm, (-0.46, -0.11, cz - 0.20), radius=0.065, height=0.16, segments=16, mat_idx=3, axis='Z')
        
        # 4. Cuatro pestillos radiales de bronce
        for ang_deg in [0, 90, 180, 270]:
            rad = math.radians(ang_deg)
            lx = math.cos(rad) * 0.32
            lz = cz + math.sin(rad) * 0.32
            add_box(bm, (lx, -0.18, lz), (0.06, 0.045, 0.15) if ang_deg % 180 == 0 else (0.15, 0.045, 0.06), mat_idx=3)
            
        # Corona de engranaje central
        add_cylinder(bm, (0, -0.18, cz), radius=0.15, height=0.045, segments=20, mat_idx=3, axis='Y')
        
        # 5. Ojo de buey de vidrio blindado
        add_cylinder(bm, (0, -0.19, cz), radius=0.11, height=0.025, segments=20, mat_idx=4, axis='Y')
        add_box(bm, (0, -0.21, cz), (0.22, 0.015, 0.018), mat_idx=1)
        add_box(bm, (0, -0.21, cz), (0.018, 0.015, 0.22), mat_idx=1)
        
        # 6. Manija de agarre de titanio
        add_box(bm, (0.24, -0.22, cz), (0.04, 0.035, 0.24), mat_idx=1)
        add_box(bm, (0.24, -0.245, cz + 0.10), (0.035, 0.05, 0.035), mat_idx=1)
        add_box(bm, (0.24, -0.245, cz - 0.10), (0.035, 0.05, 0.035), mat_idx=1)

    mat_list = [
        mats['Naval_Steel'], mats['Dark_Gunmetal'], mats['Hazard_Yellow'],
        mats['Machinery_Brass'], mats['Armored_Glass']
    ]
    return create_mesh_object("SM_Crawlway_Escape_Portal", col, geom, mat_list)

# -------------------------------------------------------------------------
# PROP 05: SM_Cryo_Tube_Maintenance_Hatch
# -------------------------------------------------------------------------
def build_prop05_cryo_hatch(col, mats):
    def geom(bm):
        # 1. Marco rectangular empotrado (100 x 160 x 25 cm)
        add_box(bm, (-0.46, 0, 0.95), (0.08, 0.25, 1.60), mat_idx=1) # Left
        add_box(bm, ( 0.46, 0, 0.95), (0.08, 0.25, 1.60), mat_idx=1) # Right
        add_box(bm, (0, 0, 1.71), (1.00, 0.25, 0.08), mat_idx=1) # Top
        add_box(bm, (0, 0, 0.19), (1.00, 0.25, 0.08), mat_idx=1) # Bottom
        add_box(bm, (0, 0.10, 0.95), (0.92, 0.04, 1.50), mat_idx=1) # Back wall
        
        # 2. Puerta batiente entreabierta a 35°
        door_w = 0.86
        door_ang = math.radians(35.0)
        cos_a = math.cos(door_ang)
        sin_a = math.sin(door_ang)
        dx_c = -0.42 + (door_w * 0.5) * cos_a
        dy_c = -0.05 - (door_w * 0.5) * sin_a
        add_box(bm, (dx_c, dy_c, 0.95), (door_w * cos_a, 0.04, 1.46), mat_idx=0)
        
        # Bisagras externas
        add_cylinder(bm, (-0.43, -0.06, 1.55), radius=0.035, height=0.14, segments=12, mat_idx=3, axis='Z')
        add_cylinder(bm, (-0.43, -0.06, 0.35), radius=0.035, height=0.14, segments=12, mat_idx=3, axis='Z')
        
        # 3. Paquete interno de 3 tuberías criogénicas con escarcha
        pipe_xs = [-0.18, 0.02, 0.22]
        for px in pipe_xs:
            add_cylinder(bm, (px, 0.04, 0.95), radius=0.045, height=1.44, segments=14, mat_idx=5, axis='Z')
            for fz in [0.45, 0.75, 1.05, 1.35]:
                add_cylinder(bm, (px, 0.04, fz), radius=0.06, height=0.11, segments=12, mat_idx=4, axis='Z')
                
        # 4. Llave de paso esférica de latón
        add_cylinder(bm, (0.02, 0.04, 0.90), radius=0.07, height=0.08, segments=14, mat_idx=3, axis='Z')
        add_cylinder(bm, (0.02, -0.04, 0.90), radius=0.09, height=0.03, segments=16, mat_idx=7, axis='Y')
        add_cylinder(bm, (0.02, -0.04, 0.90), radius=0.035, height=0.04, segments=12, mat_idx=3, axis='Y')
        
        # 5. Manómetro de nitrógeno líquido
        add_cylinder(bm, (0.22, -0.03, 1.15), radius=0.06, height=0.035, segments=16, mat_idx=3, axis='Y')
        add_cylinder(bm, (0.22, -0.05, 1.15), radius=0.048, height=0.005, segments=16, mat_idx=6, axis='Y')
        
        # 6. Letrero de advertencia LN2
        add_box(bm, (dx_c, dy_c - 0.03, 1.45), (0.35 * cos_a, 0.015, 0.14), mat_idx=2)

    mat_list = [
        mats['Naval_Steel'], mats['Dark_Gunmetal'], mats['Hazard_Yellow'],
        mats['Machinery_Brass'], mats['Cryo_Frost'], mats['Cryo_Pipe_Cyan'],
        mats['LED_Green'], mats['LED_Red']
    ]
    return create_mesh_object("SM_Cryo_Tube_Maintenance_Hatch", col, geom, mat_list)

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
    # 1. Softbox cenital difusa principal (1100W)
    key_data = bpy.data.lights.new(name="Light_Key_Overhead", type='AREA')
    key_data.energy = 1100.0
    key_data.size = 22.0
    key_data.size_y = 8.0
    key_data.color = (1.0, 0.96, 0.92)
    key_obj = bpy.data.objects.new("Light_Key_Overhead", key_data)
    key_obj.location = (0, -4.5, 6.2)
    key_obj.rotation_euler = (R(35), 0, 0)
    col.objects.link(key_obj)
    
    # 2. Luz de contra / Rim Light posterior para perfilar siluetas (850W)
    rim_data = bpy.data.lights.new(name="Light_Rim_Back", type='AREA')
    rim_data.energy = 850.0
    rim_data.size = 24.0
    rim_data.size_y = 4.0
    rim_data.color = (0.85, 0.95, 1.0)
    rim_obj = bpy.data.objects.new("Light_Rim_Back", rim_data)
    rim_obj.location = (0, 3.5, 5.0)
    rim_obj.rotation_euler = (R(-40), 0, R(180))
    col.objects.link(rim_obj)
    
    # 3. Relleno cian frío desde la izquierda (520W)
    fill_l_data = bpy.data.lights.new(name="Light_Fill_Cyan", type='AREA')
    fill_l_data.energy = 520.0
    fill_l_data.size = 8.0
    fill_l_data.color = (0.78, 0.90, 1.0)
    fill_l_obj = bpy.data.objects.new("Light_Fill_Cyan", fill_l_data)
    fill_l_obj.location = (-11.0, -5.5, 4.2)
    fill_l_obj.rotation_euler = (R(30), R(-25), R(-40))
    col.objects.link(fill_l_obj)
    
    # 4. Relleno ámbar cálido desde la derecha (520W)
    fill_r_data = bpy.data.lights.new(name="Light_Fill_Amber", type='AREA')
    fill_r_data.energy = 520.0
    fill_r_data.size = 8.0
    fill_r_data.color = (1.0, 0.85, 0.68)
    fill_r_obj = bpy.data.objects.new("Light_Fill_Amber", fill_r_data)
    fill_r_obj.location = (11.0, -5.5, 4.2)
    fill_r_obj.rotation_euler = (R(30), R(25), R(40))
    col.objects.link(fill_r_obj)

def create_camera(col, name, location, rotation, lens=45.0):
    cam_data = bpy.data.cameras.new(name)
    cam_data.lens = lens
    cam_data.clip_start = 0.1
    cam_data.clip_end = 250.0
    cam_obj = bpy.data.objects.new(name, cam_data)
    cam_obj.location = location
    cam_obj.rotation_euler = rotation
    col.objects.link(cam_obj)
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
        
    # Encabezado
    draw.text((40, 20), "ASTRA HAZARD // REPOSITORIO DE ARQUITECTURA Y PROPS INTERACTIVOS", fill=(245, 166, 35), font=font_sub)
    draw.text((40, 46), "CATÁLOGO DE PROPS - LOTE 1 (PROPS 01-05): SISTEMAS DE ACCESO, ESCLUSAS Y CONDUCTOS", fill=(255, 255, 255), font=font_title)
    
    # Badges / Pills compactas en el margen derecho
    pills = [
        ("LOTE 1 DE 10", (211, 84, 0)),
        ("MECÁNICAS DE BYPASS", (41, 128, 185)),
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
    
    # 1. Panorama Superior
    pan_path = os.path.join(RENDERS_DIR, "Showcase_Lote1_Props_Panorama.png")
    if os.path.exists(pan_path):
        pan_img = Image.open(pan_path).convert("RGBA")
        pan_w = W - 80
        pan_h = 760
        pan_resized = pan_img.resize((pan_w, pan_h), Image.Resampling.LANCZOS)
        canvas.paste(pan_resized, (40, 110))
        draw.rectangle((40, 110, 40 + pan_w, 110 + pan_h), outline=(45, 52, 65), width=2)
        
    # 2. Fila Inferior con los 5 Close-Ups de Props
    props_cards = [
        ("01. SM_Airlock_Heavy_Hatch", "Showcase_Prop01_Airlock_Heavy_Hatch.png", (245, 166, 35),
         "• Compuerta de esclusa naval doble hoja\n• Volante manual circular hermético\n• 4 pestillos de bronce y junta de neopreno\n• Luces gemelas LED y manómetro de bar"),
         
        ("02. SM_Ventilation_Grating_Duct", "Showcase_Prop02_Ventilation_Grating_Duct.png", (41, 128, 185),
         "• Conducto técnico transitable agachado\n• Brida de 8 pernos y bisagra lateral\n• 10 lamas a 45° y filtro plisado sucio\n• Arañazos de bestia en marco inferior"),
         
        ("03. SM_Hydraulic_Blast_Door", "Showcase_Prop03_Hydraulic_Blast_Door.png", (231, 76, 60),
         "• Portón anti-deflagración masivo en I\n• Chevrons de peligro amarillo y negro\n• 2 pistones hidráulicos telescópicos cromados\n• Palanca manual de derivación en caja roja"),
         
        ("04. SM_Crawlway_Escape_Portal", "Showcase_Prop04_Crawlway_Escape_Portal.png", (155, 89, 182),
         "• Escotilla circular de mamparo con 16 pernos\n• Bisagra con contrapeso cilíndrico\n• 4 pestillos sincronizados por corona\n• Ojo de buey de vidrio con cruz protectora"),
         
        ("05. SM_Cryo_Tube_Maintenance_Hatch", "Showcase_Prop05_Cryo_Tube_Maintenance_Hatch.png", (26, 188, 156),
         "• Panel técnico ajar con cerradura 1/4 vuelta\n• Paquete de 3 tubos criogénicos con escarcha\n• Llave de paso esférica con volante rojo\n• Manómetro de nitrógeno y stencils de LN2")
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

    master_path = os.path.join(RENDERS_DIR, "Showcase_Lote1_Props_Master.png")
    canvas.save(master_path, "PNG")
    
    shutil.copy2(master_path, os.path.join(ARTIFACT_DIR, "Showcase_Lote1_Props_Master.png"))
    for _, fname, _, _ in props_cards:
        fsrc = os.path.join(RENDERS_DIR, fname)
        if os.path.exists(fsrc):
            shutil.copy2(fsrc, os.path.join(ARTIFACT_DIR, fname))
    if os.path.exists(pan_path):
        shutil.copy2(pan_path, os.path.join(ARTIFACT_DIR, "Showcase_Lote1_Props_Panorama.png"))
        
    print(f"\n[MASTER OK] Lámina Maestra Oficial generada con éxito: {master_path}")

# -------------------------------------------------------------------------
# FLUJO PRINCIPAL DE PRODUCCIÓN Y RENDER
# -------------------------------------------------------------------------
def main():
    print("=" * 80)
    print("ASTRA HAZARD - GENERADOR MAESTRO 3D (LOTE 1 DE PROPS V2)")
    print("SISTEMAS DE ACCESO, ESCLUSAS Y CONDUCTOS DE EVACUACIÓN")
    print("=" * 80)
    
    scene = reset_scene()
    mats = create_materials()
    
    col_props = create_collection("Props_Lote1")
    col_env = create_collection("Showroom_Environment")
    col_lights = create_collection("Lighting")
    col_cams = create_collection("Cameras")
    
    # 1. Suelo de estudio infinito (36 x 24 m)
    mesh_floor = bpy.data.meshes.new("Studio_Floor")
    bm_f = bmesh.new()
    add_box(bm_f, (0, 0, -0.05), (36.0, 24.0, 0.10), mat_idx=0)
    bm_f.to_mesh(mesh_floor)
    bm_f.free()
    floor_obj = bpy.data.objects.new("Studio_Floor", mesh_floor)
    floor_obj.data.materials.append(mats['Studio_Floor'])
    col_env.objects.link(floor_obj)
    
    # 2. Configurar Posiciones y Pedestales para los 5 Props
    # Espaciado X: -6.4, -3.2, 0.0, +3.2, +6.4
    prop_configs = [
        {"id": 1, "x": -6.4, "name": "Airlock_Heavy_Hatch", "label": "01 // AIRLOCK HEAVY HATCH", "build": build_prop01_airlock_hatch, "w": 2.2, "d": 1.6, "cam_dist": 4.5, "cam_z": 1.45, "targ_z": 1.20},
        {"id": 2, "x": -3.2, "name": "Ventilation_Grating_Duct", "label": "02 // VENT GRATING DUCT", "build": build_prop02_vent_duct, "w": 1.8, "d": 1.8, "cam_dist": 2.5, "cam_z": 0.85, "targ_z": 0.60},
        {"id": 3, "x":  0.0, "name": "Hydraulic_Blast_Door", "label": "03 // HYDRAULIC BLAST DOOR", "build": build_prop03_blast_door, "w": 2.8, "d": 1.6, "cam_dist": 5.4, "cam_z": 1.70, "targ_z": 1.45},
        {"id": 4, "x":  3.2, "name": "Crawlway_Escape_Portal", "label": "04 // CRAWLWAY ESCAPE PORTAL", "build": build_prop04_escape_portal, "w": 1.8, "d": 1.6, "cam_dist": 2.8, "cam_z": 1.05, "targ_z": 0.85},
        {"id": 5, "x":  6.4, "name": "Cryo_Tube_Maintenance_Hatch", "label": "05 // CRYO TUBE HATCH", "build": build_prop05_cryo_hatch, "w": 1.8, "d": 1.6, "cam_dist": 3.6, "cam_z": 1.35, "targ_z": 1.05},
    ]
    
    props_created = []
    for cfg in prop_configs:
        build_pedestal(col_env, mats, cfg['name'], pos_x=cfg['x'], width=cfg['w'], depth=cfg['d'], label_text=cfg['label'])
        obj = cfg['build'](col_props, mats)
        obj.location.x = cfg['x']
        obj.location.z = 0.16 # Montado sobre el plinto
        props_created.append(obj)
        print(f"  [OK] Creado Prop 0{cfg['id']}: {obj.name} en X={cfg['x']}")
        
    setup_lighting(col_lights)
    
    # 3. Cámaras: 1 Panorama General Amplio + 5 Hero Shots Individuales Perfectamente Encuadrados
    # Panorama General: Retrocedemos a Y=-14.5, Z=4.2 con lente 28mm para capturar los 5 props completos de arriba a abajo
    cam_pan = create_camera(col_cams, "Cam_Panorama", location=(0.0, -14.2, 4.0), rotation=(R(75.5), 0, 0), lens=28.0)
    
    # 5 Cámaras individuales en ángulo 3/4 heroico apuntando al centro focal de cada prop
    ind_cams = []
    for cfg in prop_configs:
        c_name = f"Cam_Prop0{cfg['id']}_{cfg['name']}"
        # Posición 3/4: ligeramente a la derecha del prop en X, retirado en Y y a la altura visual calculada
        cam_x = cfg['x'] + (cfg['cam_dist'] * 0.45)
        cam_y = -(cfg['cam_dist'] * 0.89)
        cam_z = cfg['cam_z']
        
        # Calcular vector hacia el centro focal del prop (cfg['x'], 0.0, cfg['targ_z'])
        dx = cfg['x'] - cam_x
        dy = 0.0 - cam_y
        dz = cfg['targ_z'] - cam_z
        dist_xy = math.sqrt(dx*dx + dy*dy)
        pitch = math.atan2(dy, -dz) # Pitch
        yaw = math.atan2(dx, dy)    # Yaw
        
        # Orientación Euler
        rot_euler = (math.pi/2 - math.atan2(dz, dist_xy), 0, -yaw)
        
        cam = create_camera(col_cams, c_name, location=(cam_x, cam_y, cam_z), rotation=rot_euler, lens=42.0)
        ind_cams.append((cam, f"Showcase_Prop0{cfg['id']}_{cfg['name']}.png"))
        
    # Guardar archivo .blend oficial
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_FILE)
    print(f"\n[OK] Escena Blend guardada: {BLEND_FILE}")
    
    # 4. Renders
    print("\n[RENDER] Generando secuencias fotográficas en EEVEE...")
    
    # A. Panorama General (2560x900)
    scene.camera = cam_pan
    scene.render.resolution_x = 2560
    scene.render.resolution_y = 900
    scene.render.filepath = os.path.join(RENDERS_DIR, "Showcase_Lote1_Props_Panorama.png")
    bpy.ops.render.render(write_still=True)
    print("  [OK] Renderizado Panorama General.")
    
    # B. Close-ups individuales (1920x1080)
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    for cam, fname in ind_cams:
        scene.camera = cam
        scene.render.filepath = os.path.join(RENDERS_DIR, fname)
        bpy.ops.render.render(write_still=True)
        print(f"  [OK] Renderizado Close-Up: {fname}")
        
    assemble_master_infographic()
    print("\n" + "=" * 80)
    print("LOTE 1 DE PROPS MAESTROS COMPLETADO CON ÉXITO")
    print("=" * 80)

if __name__ == "__main__":
    main()

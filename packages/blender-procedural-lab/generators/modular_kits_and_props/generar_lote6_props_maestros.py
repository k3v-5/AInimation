# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Generador Maestro 3D - Lote 6 de Props: Vida a Bordo, Camarotes & Hábitat
# Blender 5.2 LTS - Cavidades Abiertas de Alta Fidelidad, Shaders PBR Stylized, Freestyle Ink y Lámina Maestra 2.5K

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
BLEND_FILE = os.path.join(PROJECT_ROOT, "Art", "Blender", "Lote6_Props_Maestros_Oficial.blend")

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
    
    world = bpy.data.worlds.new("World_Studio")
    scene.world = world
    world.use_nodes = True
    wnodes = world.node_tree.nodes
    wlinks = world.node_tree.links
    wnodes.clear()
    
    w_out = wnodes.new(type='ShaderNodeOutputWorld')
    w_bg = wnodes.new(type='ShaderNodeBackground')
    w_bg.inputs['Color'].default_value = (0.020, 0.024, 0.032, 1.0)
    w_bg.inputs['Strength'].default_value = 0.80
    wlinks.new(w_bg.outputs['Background'], w_out.inputs['Surface'])
    
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
    linestyle.color = (0.02, 0.02, 0.03)
    linestyle.thickness = 1.4
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

    def make_transparent_glass(name, base_col=(0.85, 0.95, 1.0, 1.0), roughness=0.05, trans_fac=0.75):
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        nodes.clear()
        
        node_out = nodes.new(type='ShaderNodeOutputMaterial')
        node_mix = nodes.new(type='ShaderNodeMixShader')
        node_trans = nodes.new(type='ShaderNodeBsdfTransparent')
        node_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
        
        node_bsdf.inputs['Base Color'].default_value = base_col
        node_bsdf.inputs['Roughness'].default_value = roughness
        node_bsdf.inputs['Metallic'].default_value = 0.08
        if 'Transmission Weight' in node_bsdf.inputs:
            node_bsdf.inputs['Transmission Weight'].default_value = 0.95
        elif 'Transmission' in node_bsdf.inputs:
            node_bsdf.inputs['Transmission'].default_value = 0.95
            
        node_trans.inputs['Color'].default_value = (0.92, 0.96, 1.0, 1.0)
        node_mix.inputs['Fac'].default_value = trans_fac
        
        links.new(node_bsdf.outputs['BSDF'], node_mix.inputs[1])
        links.new(node_trans.outputs['BSDF'], node_mix.inputs[2])
        links.new(node_mix.outputs['Shader'], node_out.inputs['Surface'])
        
        if hasattr(mat, 'surface_render_method'):
            mat.surface_render_method = 'DITHERED'
        if hasattr(mat, 'blend_method'):
            mat.blend_method = 'BLEND'
            
        return mat

    mats['Dark_Gunmetal'] = make_pbr("Mat_Dark_Gunmetal", (0.09, 0.10, 0.12, 1.0), roughness=0.32, metallic=0.92)
    mats['Dark_Titanium'] = make_pbr("Mat_Dark_Titanium", (0.13, 0.14, 0.16, 1.0), roughness=0.40, metallic=0.85)
    mats['Polished_Chrome'] = make_pbr("Mat_Polished_Chrome", (0.92, 0.93, 0.95, 1.0), roughness=0.08, metallic=0.98)
    mats['Machinery_Brass'] = make_pbr("Mat_Machinery_Brass", (0.88, 0.70, 0.28, 1.0), roughness=0.25, metallic=0.92)
    mats['Emergency_Red'] = make_pbr("Mat_Emergency_Red", (0.88, 0.08, 0.06, 1.0), roughness=0.30, metallic=0.15)
    mats['HighVis_Orange'] = make_pbr("Mat_HighVis_Orange", (0.98, 0.35, 0.05, 1.0), roughness=0.32, metallic=0.10)
    mats['Hazard_Yellow'] = make_pbr("Mat_Hazard_Yellow", (0.96, 0.74, 0.08, 1.0), roughness=0.35, metallic=0.10)

    # Shaders de Hábitat
    mats['Thermal_Canvas_Olive'] = make_pbr("Mat_Thermal_Canvas_Olive", (0.24, 0.30, 0.18, 1.0), roughness=0.75, metallic=0.0)
    mats['Thermal_Canvas_Pillow'] = make_pbr("Mat_Thermal_Canvas_Pillow", (0.38, 0.44, 0.32, 1.0), roughness=0.70, metallic=0.0)
    mats['Offwhite_Appliance'] = make_pbr("Mat_Offwhite_Appliance", (0.86, 0.88, 0.90, 1.0), roughness=0.32, metallic=0.10)
    mats['Interior_White'] = make_pbr("Mat_Interior_White", (0.92, 0.93, 0.95, 1.0), roughness=0.25, metallic=0.05)
    mats['Sanitation_Navy_Blue'] = make_pbr("Mat_Sanitation_Navy_Blue", (0.08, 0.18, 0.32, 1.0), roughness=0.28, metallic=0.40)
    mats['Locker_Steel_Grey'] = make_pbr("Mat_Locker_Steel_Grey", (0.25, 0.28, 0.32, 1.0), roughness=0.45, metallic=0.82)
    
    # Vidrio transparente y fluidos
    mats['Clear_Acrylic_Hopper'] = make_transparent_glass("Mat_Clear_Acrylic_Hopper", (0.90, 0.95, 1.0, 1.0), roughness=0.08, trans_fac=0.75)
    mats['Chamber_Glass_Clear'] = make_transparent_glass("Mat_Chamber_Glass_Clear", (0.88, 0.94, 0.98, 1.0), roughness=0.05, trans_fac=0.82)
    mats['Nutrient_Paste_Orange'] = make_pbr("Mat_Nutrient_Paste_Orange", (0.98, 0.48, 0.08, 1.0), roughness=0.25, metallic=0.0,
                                             emissive_col=(0.95, 0.42, 0.05, 1.0), emissive_str=1.6)
    
    # Bioluminiscencia, LEDs y Emisivos
    mats['Hydroponic_Plant_Green'] = make_pbr("Mat_Hydroponic_Plant_Green", (0.10, 0.82, 0.22, 1.0), roughness=0.35, metallic=0.0,
                                              emissive_col=(0.10, 0.70, 0.18, 1.0), emissive_str=1.8)
    mats['Grow_LED_VioletMagenta'] = make_pbr("Mat_Grow_LED_VioletMagenta", (0.88, 0.10, 0.98, 1.0), roughness=0.10, metallic=0.0,
                                              emissive_col=(0.92, 0.15, 1.0, 1.0), emissive_str=9.5)
    mats['Reading_Light_Amber'] = make_pbr("Mat_Reading_Light_Amber", (1.0, 0.78, 0.25, 1.0), roughness=0.15, metallic=0.0,
                                           emissive_col=(1.0, 0.82, 0.30, 1.0), emissive_str=5.5)
    mats['Screen_Phosphor_Green'] = make_pbr("Mat_Screen_Phosphor_Green", (0.10, 0.92, 0.32, 1.0), roughness=0.15, metallic=0.0,
                                             emissive_col=(0.15, 1.0, 0.35, 1.0), emissive_str=6.5)
    mats['Sanitation_LED_Status'] = make_pbr("Mat_Sanitation_LED_Status", (0.10, 0.85, 0.95, 1.0), roughness=0.12, metallic=0.0,
                                             emissive_col=(0.15, 0.90, 1.0, 1.0), emissive_str=6.0)
    mats['Gold_Chip_Glow'] = make_pbr("Mat_Gold_Chip_Glow", (1.0, 0.82, 0.20, 1.0), roughness=0.18, metallic=0.95,
                                      emissive_col=(1.0, 0.85, 0.25, 1.0), emissive_str=5.0)
    mats['Rubber_Black'] = make_pbr("Mat_Rubber_Black", (0.07, 0.07, 0.08, 1.0), roughness=0.80, metallic=0.0)

    # Entorno y pedestales
    mats['Studio_Floor'] = make_pbr("Mat_Studio_Floor", (0.040, 0.046, 0.055, 1.0), roughness=0.92, metallic=0.0)
    mats['Plinth_Dark'] = make_pbr("Mat_Plinth_Dark", (0.08, 0.09, 0.11, 1.0), roughness=0.40, metallic=0.55)
    mats['Plinth_Plaque'] = make_pbr("Mat_Plinth_Plaque", (0.90, 0.74, 0.32, 1.0), roughness=0.22, metallic=0.95)
    
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

def build_box(bm, center, size, mat_idx=0):
    geom = bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector((size[0], size[1], size[2])), verts=geom['verts'])
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

# -------------------------------------------------------------------------
# CONSTRUCCIÓN DE PROPS (MODELADO CON CAVIDADES REALES Y ACCESOS ABIERTOS)
# -------------------------------------------------------------------------

# PROP 26: SM_Crew_Bunk_Double_Fold (Literas Plegables de Mamparo)
# X = -6.0
def build_prop26(col, mats):
    X0 = -6.0
    
    def geom_bunk(bm):
        # 1. 4 Postes tubulares esquineros
        posts = [(-1.05, -0.45), (-1.05, 0.45), (1.05, -0.45), (1.05, 0.45)]
        for px, py in posts:
            build_cylinder(bm, (X0 + px, py, 0.95), 0.035, 1.90, segments=16, mat_idx=0)
            build_box(bm, (X0 + px, py, 0.02), (0.14, 0.14, 0.04), mat_idx=1)
            
        # Largueros longitudinales y transversales de unión
        build_box(bm, (X0, -0.45, 1.88), (2.10, 0.06, 0.06), mat_idx=0)
        build_box(bm, (X0, 0.45, 1.88), (2.10, 0.06, 0.06), mat_idx=0)
        build_box(bm, (X0 - 1.05, 0.0, 1.88), (0.06, 0.90, 0.06), mat_idx=0)
        build_box(bm, (X0 + 1.05, 0.0, 1.88), (0.06, 0.90, 0.06), mat_idx=0)
        
        # 2. Litera Inferior (Z = 0.42)
        build_box(bm, (X0, 0.0, 0.42), (2.02, 0.88, 0.08), mat_idx=1)
        build_cylinder(bm, (X0 - 0.98, -0.40, 0.30), 0.018, 0.28, rot=(R(35), 0, 0), mat_idx=2)
        build_cylinder(bm, (X0 + 0.98, -0.40, 0.30), 0.018, 0.28, rot=(R(35), 0, 0), mat_idx=2)
        build_box(bm, (X0, 0.0, 0.54), (1.92, 0.80, 0.16), mat_idx=3) # Colchón oliva
        build_box(bm, (X0 - 0.75, 0.0, 0.65), (0.35, 0.70, 0.09), mat_idx=4) # Almohada
        build_box(bm, (X0 - 0.25, 0.0, 0.63), (0.05, 0.82, 0.02), mat_idx=5) # Cincha 1
        build_box(bm, (X0 + 0.35, 0.0, 0.63), (0.05, 0.82, 0.02), mat_idx=5) # Cincha 2
        build_box(bm, (X0 - 0.25, 0.0, 0.645), (0.07, 0.09, 0.025), mat_idx=2) # Hebilla
        build_box(bm, (X0 + 0.35, 0.0, 0.645), (0.07, 0.09, 0.025), mat_idx=2)

        # 3. Litera Superior (Z = 1.35)
        build_box(bm, (X0, 0.0, 1.35), (2.02, 0.88, 0.08), mat_idx=1)
        build_box(bm, (X0, 0.0, 1.47), (1.92, 0.80, 0.16), mat_idx=3)
        build_box(bm, (X0 - 0.75, 0.0, 1.58), (0.35, 0.70, 0.09), mat_idx=4)
        build_box(bm, (X0 - 0.25, 0.0, 1.56), (0.05, 0.82, 0.02), mat_idx=5)
        build_box(bm, (X0 + 0.35, 0.0, 1.56), (0.05, 0.82, 0.02), mat_idx=5)
        build_box(bm, (X0 - 0.25, 0.0, 1.575), (0.07, 0.09, 0.025), mat_idx=2)
        build_box(bm, (X0 + 0.35, 0.0, 1.575), (0.07, 0.09, 0.025), mat_idx=2)
        # Barandilla tubular
        build_cylinder(bm, (X0, -0.44, 1.62), 0.02, 1.80, rot=(0, R(90), 0), mat_idx=0)
        build_cylinder(bm, (X0 - 0.90, -0.44, 1.51), 0.016, 0.22, mat_idx=0)
        build_cylinder(bm, (X0 + 0.90, -0.44, 1.51), 0.016, 0.22, mat_idx=0)

        # 4. Escalera tubular vertical
        build_cylinder(bm, (X0 + 1.05, -0.22, 0.95), 0.025, 1.90, mat_idx=0)
        for r_z in [0.40, 0.75, 1.10, 1.45]:
            build_cylinder(bm, (X0 + 1.05, 0.11, r_z), 0.018, 0.66, rot=(R(90), 0, 0), mat_idx=2)

        # 5. Lámparas de lectura diegéticas
        for lamp_z in [0.75, 1.68]:
            build_box(bm, (X0 - 1.02, -0.15, lamp_z), (0.06, 0.16, 0.10), mat_idx=1)
            build_box(bm, (X0 - 0.99, -0.15, lamp_z), (0.02, 0.12, 0.06), mat_idx=6)

        # 6. Taquilla / cajón deslizante inferior
        build_box(bm, (X0 - 0.15, 0.0, 0.18), (1.60, 0.82, 0.26), mat_idx=1)
        build_cylinder(bm, (X0 - 0.15, -0.42, 0.18), 0.015, 0.25, rot=(0, R(90), 0), mat_idx=2)
        build_box(bm, (X0 + 0.15, -0.42, 0.25), (0.08, 0.04, 0.06), mat_idx=7)

    mat_list = [
        mats['Dark_Titanium'], mats['Dark_Gunmetal'], mats['Polished_Chrome'],
        mats['Thermal_Canvas_Olive'], mats['Thermal_Canvas_Pillow'],
        mats['Rubber_Black'], mats['Reading_Light_Amber'], mats['Machinery_Brass']
    ]
    return create_mesh_object("SM_Crew_Bunk_Double_Fold", col, geom_bunk, mat_list)


# PROP 27: SM_Nutrient_Paste_Dispenser (Dispensador Industrial de Pasta Nutritiva)
# X = -3.0
def build_prop27(col, mats):
    X0 = -3.0
    
    def geom_dispenser(bm):
        # 1. Base zócalo de mamparo (mat 1 = Dark_Gunmetal)
        build_box(bm, (X0, 0.0, 0.08), (0.92, 0.68, 0.16), mat_idx=1)
        
        # 2. Bloque inferior del mueble (Z = 0.16 a 0.58)
        build_box(bm, (X0, 0.0, 0.37), (0.86, 0.62, 0.42), mat_idx=0) # Offwhite
        
        # 3. Muro posterior (fondo del nicho)
        build_box(bm, (X0, 0.22, 0.85), (0.86, 0.18, 0.54), mat_idx=0)
        # Paredes laterales del nicho
        build_box(bm, (X0 - 0.34, 0.0, 0.85), (0.18, 0.62, 0.54), mat_idx=0)
        build_box(bm, (X0 + 0.34, 0.0, 0.85), (0.18, 0.62, 0.54), mat_idx=0)
        
        # 4. Nicho de dispensación HUECO Y VISIBLE (Centro frontal, Z = 0.58 a 1.12)
        # Bandeja de drenaje y rejilla perforada
        build_box(bm, (X0, -0.06, 0.60), (0.48, 0.40, 0.04), mat_idx=4) # Cromo
        # Boquilla dispensadora en el techo del nicho
        build_cylinder(bm, (X0, -0.06, 1.08), 0.06, 0.10, segments=16, mat_idx=4)
        build_cylinder(bm, (X0, -0.06, 1.00), 0.03, 0.06, segments=16, mat_idx=5) # Boquilla latón
        # Ración de gel naranja brillante fresca en la bandeja
        build_box(bm, (X0, -0.06, 0.66), (0.18, 0.15, 0.08), mat_idx=3) # Gel naranja
        
        # 5. Bloque superior de control (Z = 1.12 a 1.72)
        build_box(bm, (X0, 0.0, 1.42), (0.86, 0.62, 0.60), mat_idx=0)
        build_box(bm, (X0, 0.0, 1.73), (0.90, 0.66, 0.04), mat_idx=1) # Cornisa superior
        
        # 6. Tolva superior cilíndrica acrílica translúcida SOBRESALIENTE AL FRENTE
        # Centrada y proyectada para verse en 360°
        build_cylinder(bm, (X0, -0.04, 1.50), 0.27, 0.44, segments=24, mat_idx=2) # Acrílico claro
        build_cylinder(bm, (X0, -0.04, 1.48), 0.24, 0.38, segments=20, mat_idx=3) # Núcleo gel naranja emisivo
        # Bridas y sellos cromados
        build_cylinder(bm, (X0, -0.04, 1.27), 0.30, 0.03, segments=24, mat_idx=4)
        build_cylinder(bm, (X0, -0.04, 1.72), 0.29, 0.03, segments=24, mat_idx=4)
        build_cylinder(bm, (X0, -0.04, 1.84), 0.08, 0.20, segments=16, mat_idx=1) # Tubo al techo

        # 7. Manómetro de aguja en el frontal superior
        build_cylinder(bm, (X0 - 0.28, -0.32, 1.56), 0.08, 0.05, segments=16, rot=(R(90), 0, 0), mat_idx=5)
        build_cylinder(bm, (X0 - 0.28, -0.346, 1.56), 0.07, 0.01, segments=16, rot=(R(90), 0, 0), mat_idx=0)
        build_box(bm, (X0 - 0.28, -0.353, 1.56), (0.008, 0.01, 0.08), mat_idx=6)

        # 8. Pantalla CRT verde fósforo de telemetría de raciones
        build_box(bm, (X0 + 0.18, -0.315, 1.54), (0.30, 0.04, 0.22), mat_idx=1)
        build_box(bm, (X0 + 0.18, -0.336, 1.54), (0.26, 0.02, 0.18), mat_idx=7)
        for b_x in [-0.08, 0.0, 0.08]:
            build_box(bm, (X0 + 0.18 + b_x, -0.325, 1.38), (0.05, 0.03, 0.04), mat_idx=8)

        # 9. Palanca dosificadora ergonómica manual en el lateral derecho
        build_cylinder(bm, (X0 + 0.44, -0.08, 0.90), 0.06, 0.08, segments=16, rot=(0, R(90), 0), mat_idx=1)
        build_cylinder(bm, (X0 + 0.49, -0.20, 1.05), 0.022, 0.36, segments=12, rot=(R(40), 0, 0), mat_idx=4)
        build_cylinder(bm, (X0 + 0.49, -0.33, 1.20), 0.06, 0.09, segments=16, mat_idx=6)

        # 10. Mangueras y filtro lateral izquierdo
        build_cylinder(bm, (X0 - 0.44, 0.05, 0.85), 0.09, 0.70, segments=16, mat_idx=1)
        build_cylinder(bm, (X0 - 0.44, 0.05, 0.85), 0.095, 0.05, segments=16, mat_idx=5)
        build_cylinder(bm, (X0 - 0.44, -0.15, 0.75), 0.035, 0.85, segments=12, mat_idx=9)

    mat_list = [
        mats['Offwhite_Appliance'], mats['Dark_Gunmetal'], mats['Clear_Acrylic_Hopper'],
        mats['Nutrient_Paste_Orange'], mats['Polished_Chrome'], mats['Machinery_Brass'],
        mats['Emergency_Red'], mats['Screen_Phosphor_Green'], mats['Hazard_Yellow'],
        mats['Rubber_Black']
    ]
    return create_mesh_object("SM_Nutrient_Paste_Dispenser", col, geom_dispenser, mat_list)


# PROP 28: SM_Hydroponic_Sprout_Chamber (Cámara Hidropónica de Brotes y O2)
# X = 0.0
def build_prop28(col, mats):
    X0 = 0.0
    
    def geom_hydroponic(bm):
        # 1. Armazón perimétrico con cavidad frontal TOTALMENTE HUECA Y VISIBLE
        # Base zócalo (Z = 0.0 a 0.24)
        build_box(bm, (X0, 0.0, 0.12), (1.30, 0.72, 0.24), mat_idx=1) # Dark_Titanium
        # Pared trasera (Y = +0.28)
        build_box(bm, (X0, 0.28, 1.15), (1.30, 0.16, 1.82), mat_idx=0) # Offwhite exterior
        build_box(bm, (X0, 0.19, 1.15), (1.18, 0.02, 1.78), mat_idx=2) # Interior dark gunmetal
        # Pared lateral izquierda (X = -0.59)
        build_box(bm, (X0 - 0.59, 0.0, 1.15), (0.12, 0.72, 1.82), mat_idx=0)
        # Pared lateral derecha (X = +0.59)
        build_box(bm, (X0 + 0.59, 0.0, 1.15), (0.12, 0.72, 1.82), mat_idx=0)
        # Techo (Z = 2.06)
        build_box(bm, (X0, 0.0, 2.06), (1.30, 0.72, 0.12), mat_idx=1)

        # 2. 3 Niveles de bandejas de cultivo escalonadas (Z = 0.50, 1.00, 1.50)
        tray_zs = [0.50, 1.00, 1.50]
        for tz in tray_zs:
            # Bandeja blanca
            build_box(bm, (X0, 0.0, tz), (1.06, 0.44, 0.07), mat_idx=0)
            # Sustrato oscuro
            build_box(bm, (X0, 0.0, tz + 0.04), (1.02, 0.40, 0.02), mat_idx=2)
            
            # Brotes verdes procedimentales abundantes (mat 3 = Hydroponic_Plant_Green)
            for bx in [-0.40, -0.27, -0.13, 0.0, 0.13, 0.27, 0.40]:
                for by in [-0.14, -0.02, 0.10]:
                    build_cylinder(bm, (X0 + bx, by, tz + 0.11), 0.038, 0.14, segments=8, rot=(0, 0, R(bx*30)), mat_idx=3)
                    build_box(bm, (X0 + bx, by, tz + 0.17), (0.09, 0.07, 0.02), mat_idx=3)
            
            # Iluminación hortícola UV en el techo de cada nivel (mat 4 = Grow_LED_VioletMagenta)
            build_box(bm, (X0, 0.0, tz + 0.36), (1.04, 0.14, 0.04), mat_idx=4)
            build_box(bm, (X0, 0.0, tz + 0.38), (1.06, 0.18, 0.02), mat_idx=5) # Reflector cromo

        # 3. Puerta acristalada en bisagras izquierdas, ABIERTA HACIA AFUERA A 45 GRADOS
        # Pivote en (X0 - 0.53, Y = -0.36)
        build_cylinder(bm, (X0 - 0.53, -0.36, 0.50), 0.025, 0.12, segments=12, mat_idx=1)
        build_cylinder(bm, (X0 - 0.53, -0.36, 1.70), 0.025, 0.12, segments=12, mat_idx=1)
        
        door_ang = R(45)
        d_len = 1.06
        d_cx = (X0 - 0.53) + (d_len * 0.5 * math.cos(door_ang))
        d_cy = -0.36 - (d_len * 0.5 * math.sin(door_ang))
        
        # Marco exterior de la puerta rotada
        door_frame = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=Vector((d_len, 0.04, 1.68)), verts=door_frame['verts'])
        euler_d = Euler((0, 0, -door_ang), 'XYZ')
        bmesh.ops.rotate(bm, matrix=euler_d.to_matrix().to_4x4(), verts=door_frame['verts'])
        bmesh.ops.translate(bm, vec=Vector((d_cx, d_cy, 1.15)), verts=door_frame['verts'])
        for elem in door_frame['verts']:
            for f in elem.link_faces:
                f.material_index = 1 # Dark_Titanium
                
        # Cristal ultra-transparente en el interior de la puerta (mat 6 = Chamber_Glass_Clear)
        glass_pane = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=Vector((d_len - 0.12, 0.015, 1.54)), verts=glass_pane['verts'])
        bmesh.ops.rotate(bm, matrix=euler_d.to_matrix().to_4x4(), verts=glass_pane['verts'])
        bmesh.ops.translate(bm, vec=Vector((d_cx, d_cy, 1.15)), verts=glass_pane['verts'])
        for elem in glass_pane['verts']:
            for f in elem.link_faces:
                f.material_index = 6
                
        # Maneta hermética de compresión de latón en el borde de la puerta
        h_cx = (X0 - 0.53) + ((d_len - 0.05) * math.cos(door_ang))
        h_cy = -0.36 - ((d_len - 0.05) * math.sin(door_ang))
        build_box(bm, (h_cx, h_cy, 1.15), (0.05, 0.08, 0.18), mat_idx=7) # Latón

        # 4. Sistema de recirculación y bomba hidráulica
        build_cylinder(bm, (X0 - 0.38, -0.10, 0.22), 0.08, 0.18, segments=16, mat_idx=5)
        build_cylinder(bm, (X0 - 0.53, -0.12, 1.15), 0.025, 1.45, segments=12, mat_idx=6)
        for c_z in [0.60, 1.10, 1.60]:
            build_cylinder(bm, (X0 - 0.53, -0.12, c_z), 0.032, 0.03, segments=12, mat_idx=7)

        # 5. Panel digital de telemetría en el lateral frontal derecho
        build_box(bm, (X0 + 0.59, -0.15, 1.70), (0.04, 0.24, 0.16), mat_idx=2)
        build_box(bm, (X0 + 0.612, -0.15, 1.70), (0.015, 0.20, 0.12), mat_idx=8) # Pantalla verde
        # Difusor de O2 superior
        build_cylinder(bm, (X0, 0.0, 2.14), 0.16, 0.08, segments=20, mat_idx=5)
        build_cylinder(bm, (X0, 0.0, 2.19), 0.12, 0.03, segments=20, mat_idx=8)

    mat_list = [
        mats['Offwhite_Appliance'], mats['Dark_Titanium'], mats['Dark_Gunmetal'],
        mats['Hydroponic_Plant_Green'], mats['Grow_LED_VioletMagenta'],
        mats['Polished_Chrome'], mats['Chamber_Glass_Clear'], mats['Machinery_Brass'],
        mats['Screen_Phosphor_Green']
    ]
    return create_mesh_object("SM_Hydroponic_Sprout_Chamber", col, geom_hydroponic, mat_list)


# PROP 29: SM_Sanitation_Locker_Unit (Módulo Sanitario Estanco / Ducha Sónica)
# X = +3.0
def build_prop29(col, mats):
    X0 = 3.0
    
    def geom_sanitation(bm):
        # 1. Cabina monobloque con cavidad frontal TOTALMENTE HUECA Y VISIBLE
        # Base zócalo (Z = 0.0 a 0.18)
        build_box(bm, (X0, 0.0, 0.09), (1.12, 0.92, 0.18), mat_idx=1)
        # Pared trasera (Y = +0.38)
        build_box(bm, (X0, 0.38, 1.05), (1.10, 0.16, 1.80), mat_idx=0) # Navy Blue
        build_box(bm, (X0, 0.29, 1.05), (0.94, 0.02, 1.76), mat_idx=2) # Blanco interior
        # Pared lateral izquierda (X = -0.50)
        build_box(bm, (X0 - 0.50, 0.0, 1.05), (0.12, 0.90, 1.80), mat_idx=0)
        # Pared lateral derecha (X = +0.50)
        build_box(bm, (X0 + 0.50, 0.0, 1.05), (0.12, 0.90, 1.80), mat_idx=0)
        # Techo (Z = 1.98)
        build_box(bm, (X0, 0.0, 1.98), (1.10, 0.92, 0.10), mat_idx=1)

        # 2. Equipamiento interior visible:
        # Rejilla circular cromada de suelo con succión de vórtice
        build_cylinder(bm, (X0, -0.04, 0.19), 0.28, 0.02, segments=24, mat_idx=3)
        build_cylinder(bm, (X0, -0.04, 0.205), 0.08, 0.015, segments=16, mat_idx=1)
        
        # Techo con cabezal de ducha sónica cromada
        build_cylinder(bm, (X0, -0.04, 1.88), 0.24, 0.04, segments=24, mat_idx=3)
        for ang in [0, 45, 90, 135, 180, 225, 270, 315]:
            rad = R(ang)
            bx = 0.15 * math.cos(rad)
            by = 0.15 * math.sin(rad)
            build_cylinder(bm, (X0 + bx, -0.04 + by, 1.85), 0.02, 0.03, segments=8, mat_idx=3)
        build_cylinder(bm, (X0, -0.04, 1.87), 0.06, 0.02, segments=16, mat_idx=4) # Foco UV cian

        # Pasamanos tubular curvo en la pared izquierda
        build_cylinder(bm, (X0 - 0.41, -0.04, 1.05), 0.02, 0.80, segments=12, mat_idx=3)
        # Dispensador de jabón bacteriostático
        build_box(bm, (X0 - 0.42, 0.15, 1.15), (0.05, 0.12, 0.22), mat_idx=3)
        build_cylinder(bm, (X0 - 0.42, 0.15, 1.02), 0.015, 0.05, segments=8, mat_idx=5)

        # 3. Puerta de escotilla presurizada - Bisagra a la izquierda, ABIERTA HACIA AFUERA A 65°
        # Pivote en (X0 - 0.45, Y = -0.44)
        build_cylinder(bm, (X0 - 0.45, -0.44, 0.55), 0.03, 0.12, segments=16, mat_idx=1)
        build_cylinder(bm, (X0 - 0.45, -0.44, 1.50), 0.03, 0.12, segments=16, mat_idx=1)
        
        door_ang = R(65)
        d_len = 0.84
        d_cx = (X0 - 0.45) + (d_len * 0.5 * math.cos(door_ang))
        d_cy = -0.44 - (d_len * 0.5 * math.sin(door_ang))
        
        # Hoja de la puerta
        door_geom = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=Vector((d_len, 0.06, 1.76)), verts=door_geom['verts'])
        euler_d = Euler((0, 0, -door_ang), 'XYZ')
        bmesh.ops.rotate(bm, matrix=euler_d.to_matrix().to_4x4(), verts=door_geom['verts'])
        bmesh.ops.translate(bm, vec=Vector((d_cx, d_cy, 1.04)), verts=door_geom['verts'])
        for elem in door_geom['verts']:
            for f in elem.link_faces:
                f.material_index = 0 # Navy Blue
                
        # Ojo de buey en la puerta rotada
        p_cx = (X0 - 0.45) + (0.42 * math.cos(door_ang))
        p_cy = -0.44 - (0.42 * math.sin(door_ang))
        build_cylinder(bm, (p_cx, p_cy, 1.35), 0.14, 0.08, segments=20, rot=(R(90), 0, -door_ang), mat_idx=3)
        build_cylinder(bm, (p_cx, p_cy, 1.35), 0.11, 0.09, segments=20, rot=(R(90), 0, -door_ang), mat_idx=6)
        
        # Volante circular cromado de triple bulón
        v_cx = (X0 - 0.45) + (0.65 * math.cos(door_ang))
        v_cy = -0.44 - (0.65 * math.sin(door_ang))
        build_cylinder(bm, (v_cx, v_cy, 0.95), 0.12, 0.04, segments=20, rot=(R(90), 0, -door_ang), mat_idx=3)
        build_cylinder(bm, (v_cx, v_cy, 0.95), 0.03, 0.10, segments=12, rot=(R(90), 0, -door_ang), mat_idx=5)

        # 4. Panel lateral exterior con estatus desinfectante
        build_box(bm, (X0 + 0.56, -0.15, 1.45), (0.04, 0.22, 0.35), mat_idx=1)
        build_box(bm, (X0 + 0.582, -0.15, 1.50), (0.015, 0.18, 0.14), mat_idx=4)
        build_cylinder(bm, (X0 + 0.582, -0.20, 1.35), 0.018, 0.02, segments=12, rot=(0, R(90), 0), mat_idx=7)
        build_cylinder(bm, (X0 + 0.582, -0.15, 1.35), 0.018, 0.02, segments=12, rot=(0, R(90), 0), mat_idx=8)
        build_cylinder(bm, (X0 + 0.582, -0.10, 1.35), 0.018, 0.02, segments=12, rot=(0, R(90), 0), mat_idx=9)

    mat_list = [
        mats['Sanitation_Navy_Blue'], mats['Dark_Gunmetal'], mats['Interior_White'],
        mats['Polished_Chrome'], mats['Sanitation_LED_Status'], mats['Machinery_Brass'],
        mats['Chamber_Glass_Clear'], mats['Screen_Phosphor_Green'], mats['Hazard_Yellow'],
        mats['Emergency_Red']
    ]
    return create_mesh_object("SM_Sanitation_Locker_Unit", col, geom_sanitation, mat_list)


# PROP 30: SM_Crew_Personal_Locker (Taquilla Personal de Mamparo con Botín)
# X = +6.0
def build_prop30(col, mats):
    X0 = 6.0
    
    def geom_locker(bm):
        # 1. Armario de chapa doblada con cavidad frontal TOTALMENTE HUECA Y VISIBLE
        # Base zócalo (Z = 0.0 a 0.14)
        build_box(bm, (X0, 0.0, 0.07), (0.58, 0.54, 0.14), mat_idx=1)
        # Pared trasera (Y = +0.22)
        build_box(bm, (X0, 0.22, 1.02), (0.54, 0.08, 1.80), mat_idx=0)
        # Pared lateral izquierda (X = -0.25)
        build_box(bm, (X0 - 0.25, 0.0, 1.02), (0.06, 0.50, 1.80), mat_idx=0)
        # Pared lateral derecha (X = +0.25)
        build_box(bm, (X0 + 0.25, 0.0, 1.02), (0.06, 0.50, 1.80), mat_idx=0)
        # Techo (Z = 1.94)
        build_box(bm, (X0, 0.0, 1.94), (0.56, 0.54, 0.06), mat_idx=1)

        # 2. Baldas interiores (Z = 0.45, 1.02, 1.55)
        build_box(bm, (X0, 0.0, 0.45), (0.44, 0.42, 0.03), mat_idx=1)
        build_box(bm, (X0, 0.0, 1.02), (0.44, 0.42, 0.03), mat_idx=1)
        build_box(bm, (X0, 0.0, 1.55), (0.44, 0.42, 0.03), mat_idx=1)

        # 3. Objetos visibles en el interior:
        # Balda superior: Termo cilíndrico cromado con tapón rojo + credencial tripulante
        build_cylinder(bm, (X0 - 0.10, -0.04, 1.68), 0.042, 0.22, segments=16, mat_idx=3)
        build_cylinder(bm, (X0 - 0.10, -0.04, 1.80), 0.038, 0.04, segments=16, mat_idx=4)
        build_box(bm, (X0 + 0.10, -0.04, 1.60), (0.10, 0.15, 0.04), mat_idx=5)
        
        # Balda intermedia: Linterna táctica imantada encendida + maletín de herramientas naranja
        build_cylinder(bm, (X0 - 0.15, -0.03, 1.25), 0.022, 0.18, segments=12, mat_idx=1)
        build_cylinder(bm, (X0 - 0.15, -0.03, 1.34), 0.025, 0.02, segments=12, mat_idx=6)
        build_box(bm, (X0 + 0.06, -0.03, 1.14), (0.18, 0.22, 0.18), mat_idx=7)

        # Base / Doble fondo: Trampilla levantada revelando 2 lingotes/chips dorados emisivos
        build_box(bm, (X0, -0.02, 0.49), (0.40, 0.36, 0.02), mat_idx=1)
        build_box(bm, (X0 - 0.08, -0.06, 0.53), (0.08, 0.14, 0.04), mat_idx=8) # Oro
        build_box(bm, (X0 + 0.06, -0.06, 0.53), (0.08, 0.14, 0.04), mat_idx=8) # Oro

        # 4. Puerta frontal semiabierta a 60 grados hacia afuera a la izquierda
        # Bisagra izquierda en (X0 - 0.25, Y = -0.24)
        build_cylinder(bm, (X0 - 0.25, -0.24, 0.50), 0.02, 0.10, segments=12, mat_idx=1)
        build_cylinder(bm, (X0 - 0.25, -0.24, 1.45), 0.02, 0.10, segments=12, mat_idx=1)
        
        door_ang = R(60)
        d_len = 0.48
        d_cx = (X0 - 0.25) + (d_len * 0.5 * math.cos(door_ang))
        d_cy = -0.24 - (d_len * 0.5 * math.sin(door_ang))
        
        door_geom = bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=Vector((d_len, 0.03, 1.76)), verts=door_geom['verts'])
        euler_d = Euler((0, 0, -door_ang), 'XYZ')
        bmesh.ops.rotate(bm, matrix=euler_d.to_matrix().to_4x4(), verts=door_geom['verts'])
        bmesh.ops.translate(bm, vec=Vector((d_cx, d_cy, 1.02)), verts=door_geom['verts'])
        for elem in door_geom['verts']:
            for f in elem.link_faces:
                f.material_index = 0 # Locker_Steel_Grey

        # Cierre forzado: aldaba rota con candado cortado colgando
        l_cx = (X0 - 0.25) + (0.42 * math.cos(door_ang))
        l_cy = -0.24 - (0.42 * math.sin(door_ang))
        build_box(bm, (l_cx, l_cy, 1.02), (0.05, 0.06, 0.08), mat_idx=9)
        build_cylinder(bm, (l_cx, l_cy - 0.03, 0.96), 0.015, 0.06, segments=12, mat_idx=1)

    mat_list = [
        mats['Locker_Steel_Grey'], mats['Dark_Titanium'], mats['Dark_Gunmetal'],
        mats['Polished_Chrome'], mats['Emergency_Red'], mats['Offwhite_Appliance'],
        mats['Reading_Light_Amber'], mats['HighVis_Orange'], mats['Gold_Chip_Glow'],
        mats['Machinery_Brass']
    ]
    return create_mesh_object("SM_Crew_Personal_Locker", col, geom_locker, mat_list)


# -------------------------------------------------------------------------
# PEDESTALES, SUELO Y PLACAS IDENTIFICATIVAS
# -------------------------------------------------------------------------
def build_environment(col, mats):
    def geom_floor(bm):
        build_box(bm, (0, 0, -0.05), (28.0, 16.0, 0.10), mat_idx=0)
    create_mesh_object("Studio_Floor_Mesh", col, geom_floor, mats['Studio_Floor'])
    
    plinth_coords = [
        (-6.0, 2.50, 1.40, "PROP 26: CREW BUNK DOUBLE FOLD"),
        (-3.0, 1.50, 1.40, "PROP 27: NUTRIENT PASTE DISPENSER"),
        ( 0.0, 1.80, 1.40, "PROP 28: HYDROPONIC SPROUT CHAMBER"),
        ( 3.0, 1.60, 1.50, "PROP 29: SANITATION LOCKER UNIT"),
        ( 6.0, 1.30, 1.30, "PROP 30: CREW PERSONAL LOCKER")
    ]
    
    for px, sx, sy, label in plinth_coords:
        def make_plinth_func(cx=px, sx_val=sx, sy_val=sy):
            def geom_p(bm):
                build_box(bm, (cx, 0.0, 0.075), (sx_val, sy_val, 0.15), mat_idx=0)
                build_box(bm, (cx, -sy_val*0.5 - 0.01, 0.075), (sx_val*0.55, 0.02, 0.06), mat_idx=1)
            return geom_p
            
        create_mesh_object(f"Plinth_X_{px}", col, make_plinth_func(), [mats['Plinth_Dark'], mats['Plinth_Plaque']])

# -------------------------------------------------------------------------
# ILUMINACIÓN FOTOMÉTRICA DE ESTUDIO
# -------------------------------------------------------------------------
def setup_lighting(col):
    key_data = bpy.data.lights.new(name="Light_Key_Overhead", type='AREA')
    key_data.energy = 1200.0
    key_data.size = 24.0
    key_data.size_y = 8.0
    key_data.color = (0.95, 0.98, 1.0)
    key_obj = bpy.data.objects.new("Light_Key_Overhead", key_data)
    key_obj.location = (0, -4.8, 6.4)
    key_obj.rotation_euler = (R(35), 0, 0)
    col.objects.link(key_obj)
    
    rim_data = bpy.data.lights.new(name="Light_Rim_Back", type='AREA')
    rim_data.energy = 950.0
    rim_data.size = 26.0
    rim_data.size_y = 4.0
    rim_data.color = (0.80, 0.92, 1.0)
    rim_obj = bpy.data.objects.new("Light_Rim_Back", rim_data)
    rim_obj.location = (0, 3.8, 5.2)
    rim_obj.rotation_euler = (R(-40), 0, R(180))
    col.objects.link(rim_obj)
    
    fill_l_data = bpy.data.lights.new(name="Light_Fill_Cool", type='AREA')
    fill_l_data.energy = 550.0
    fill_l_data.size = 10.0
    fill_l_data.color = (0.85, 0.95, 1.0)
    fill_l_obj = bpy.data.objects.new("Light_Fill_Cool", fill_l_data)
    fill_l_obj.location = (-12.0, -6.0, 4.2)
    fill_l_obj.rotation_euler = (R(30), R(-25), R(-40))
    col.objects.link(fill_l_obj)
    
    fill_r_data = bpy.data.lights.new(name="Light_Fill_Warm", type='AREA')
    fill_r_data.energy = 550.0
    fill_r_data.size = 10.0
    fill_r_data.color = (1.0, 0.90, 0.80)
    fill_r_obj = bpy.data.objects.new("Light_Fill_Warm", fill_r_data)
    fill_r_obj.location = (12.0, -6.0, 4.2)
    fill_r_obj.rotation_euler = (R(30), R(25), R(40))
    col.objects.link(fill_r_obj)

    # Acentos internos diegéticos:
    # Prop 28: Luz puntual interna UV magenta vibrante para iluminar brotes
    accent_p28 = bpy.data.lights.new(name="Light_Prop28_UV_Internal", type='POINT')
    accent_p28.energy = 180.0
    accent_p28.color = (0.95, 0.15, 1.0)
    accent_p28_obj = bpy.data.objects.new("Light_Prop28_UV_Internal", accent_p28)
    accent_p28_obj.location = (0.0, 0.0, 1.25)
    col.objects.link(accent_p28_obj)

    # Prop 29: Luz puntual interna cabina sónica
    accent_p29 = bpy.data.lights.new(name="Light_Prop29_Internal", type='POINT')
    accent_p29.energy = 160.0
    accent_p29.color = (0.50, 0.88, 1.0)
    accent_p29_obj = bpy.data.objects.new("Light_Prop29_Internal", accent_p29)
    accent_p29_obj.location = (3.0, 0.0, 1.25)
    col.objects.link(accent_p29_obj)

    # Prop 30: Luz puntual interna taquilla botín dorado
    accent_p30 = bpy.data.lights.new(name="Light_Prop30_Loot", type='POINT')
    accent_p30.energy = 110.0
    accent_p30.color = (1.0, 0.85, 0.35)
    accent_p30_obj = bpy.data.objects.new("Light_Prop30_Loot", accent_p30)
    accent_p30_obj.location = (6.0, 0.0, 0.95)
    col.objects.link(accent_p30_obj)

# -------------------------------------------------------------------------
# SISTEMA DE CÁMARAS CON TRACK_TO DINÁMICO (3/4 PERSPECTIVA HEROICA)
# -------------------------------------------------------------------------
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

def setup_all_cameras(col):
    cams = {}
    
    # 1. Panorama General (26mm a 12.4m de distancia)
    cams['Panorama'] = create_camera_tracking(col, "Cam_Panorama", (0.0, -12.4, 3.6), (0.0, 0.0, 0.90), lens=26.0)
    
    # 2. Close-ups 1080p en perspectiva 3/4 aislados (lentes 44-48mm para eliminar vecinos del fondo)
    # Prop 26: Literas (vistas de 3/4 heroicas, encuadre completo de 2.1m)
    cams[26] = create_camera_tracking(col, "Cam_Prop26", (-6.0 + 1.20, -3.40, 1.65), (-6.0, 0.0, 0.95), lens=44.0)
    
    # Prop 27: Dispensador de pasta (encuadre centrado desde la tolva acrílica hasta la base)
    cams[27] = create_camera_tracking(col, "Cam_Prop27", (-3.0 + 0.95, -3.10, 1.55), (-3.0, 0.0, 0.95), lens=46.0)
    
    # Prop 28: Cámara hidropónica (puerta a 45° mostrando brotes verdes en 3 niveles y luz magenta)
    cams[28] = create_camera_tracking(col, "Cam_Prop28", ( 0.0 + 1.10, -3.35, 1.65), ( 0.0, 0.0, 1.05), lens=45.0)
    
    # Prop 29: Módulo sanitario (mirando al interior con ducha sónica cromada, pasamanos y puerta abierta a 65°)
    cams[29] = create_camera_tracking(col, "Cam_Prop29", ( 3.0 + 1.05, -3.20, 1.60), ( 3.0, 0.0, 1.02), lens=46.0)
    
    # Prop 30: Taquilla de mamparo (mirando al interior con termo, linterna y lingotes dorados)
    cams[30] = create_camera_tracking(col, "Cam_Prop30", ( 6.0 + 0.85, -2.85, 1.50), ( 6.0, 0.0, 0.98), lens=48.0)
    
    return cams

# -------------------------------------------------------------------------
# PIPELINE DE RENDERIZADO Y POST-PROCESADO INFOGRÁFICO
# -------------------------------------------------------------------------
def render_all(cams):
    scene = bpy.context.scene
    
    # Render 1: Panorama Maestro (2560 x 900)
    scene.camera = cams['Panorama']
    scene.render.resolution_x = 2560
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    pano_path = os.path.join(RENDERS_DIR, "Showcase_Lote6_Props_Panorama.png")
    scene.render.filepath = pano_path
    print(f"[*] Renderizando Panorama Maestro: {pano_path}...")
    bpy.ops.render.render(write_still=True)
    shutil.copy2(pano_path, os.path.join(ARTIFACT_DIR, "Showcase_Lote6_Props_Panorama.png"))

    # Renders 2 a 6: Close-ups individuales (1920 x 1080)
    closeups = {}
    closeup_names = {
        26: "Showcase_Prop26_Crew_Bunk_Double_Fold.png",
        27: "Showcase_Prop27_Nutrient_Paste_Dispenser.png",
        28: "Showcase_Prop28_Hydroponic_Sprout_Chamber.png",
        29: "Showcase_Prop29_Sanitation_Locker_Unit.png",
        30: "Showcase_Prop30_Crew_Personal_Locker.png"
    }
    
    for pid in [26, 27, 28, 29, 30]:
        scene.camera = cams[pid]
        scene.render.resolution_x = 1920
        scene.render.resolution_y = 1080
        out_name = closeup_names[pid]
        out_path = os.path.join(RENDERS_DIR, out_name)
        scene.render.filepath = out_path
        print(f"[*] Renderizando Close-up Prop {pid}: {out_path}...")
        bpy.ops.render.render(write_still=True)
        shutil.copy2(out_path, os.path.join(ARTIFACT_DIR, out_name))
        closeups[pid] = out_path

    # Generación de la Lámina Maestra Compuesta 2.5K
    generate_master_sheet(pano_path, closeups)

def generate_master_sheet(pano_path, closeups):
    W, H = 2560, 1440
    canvas = Image.new("RGBA", (W, H), (14, 17, 22, 255))
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
    draw.text((40, 46), "CATÁLOGO DE PROPS - LOTE 6 (PROPS 26-30): VIDA A BORDO, CAMAROTES & HÁBITAT", fill=(255, 255, 255), font=font_title)
    
    pills = [
        ("LOTE 6 DE 10", (230, 126, 34)),
        ("HÁBITAT & SOPORTE", (155, 89, 182)),
        ("COLISIÓN UCX READY", (39, 174, 96)),
        ("FREESTYLE INK", (41, 128, 185)),
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
    
    if os.path.exists(pano_path):
        pan_img = Image.open(pano_path).convert("RGBA")
        pan_w = W - 80
        pan_h = 760
        pan_resized = pan_img.resize((pan_w, pan_h), Image.Resampling.LANCZOS)
        canvas.paste(pan_resized, (40, 110))
        draw.rectangle((40, 110, 40 + pan_w, 110 + pan_h), outline=(45, 52, 65), width=2)
        
    props_cards = [
        ("26. SM_Crew_Bunk_Double_Fold", closeups.get(26), (41, 128, 185),
         "• Litera tubular doble con colchón ignífugo\n• Cinchas elásticas cruzadas de gravedad cero\n• Escalera vertical lateral y taquilla inferior\n• Refugio y escondite de supervivientes aterrados"),
         
        ("27. SM_Nutrient_Paste_Dispenser", closeups.get(27), (230, 126, 34),
         "• Dispensador inox con tolva acrílica de gel\n• Palanca manual con pomo rojo ergonómico\n• Pantalla CRT fósforo verde de raciones\n• Consumible para restaurar vigor o calmar mascota"),
         
        ("28. SM_Hydroponic_Sprout_Chamber", closeups.get(28), (46, 204, 113),
         "• Vitrina estanca con 3 bandejas de brotes\n• Luces LED UV magenta hortícolas resplandecientes\n• Puerta de policarbonato y recirculación\n• Genera burbuja de O2 puro local al reactivar energía"),
         
        ("29. SM_Sanitation_Locker_Unit", closeups.get(29), (52, 152, 219),
         "• Módulo de descontaminación en azul naval\n• Puerta abierta a 65° con volante y ojo de buey\n• Ducha sónica cromada en techo y desagüe\n• Refugio contra ácido o trampa para trasgo"),
         
        ("30. SM_Crew_Personal_Locker", closeups.get(30), (241, 196, 15),
         "• Taquilla de acero con puerta abierta a 60°\n• Aldaba rota y candado cortado colgando\n• Termo inox, linterna y lingotes en falso fondo\n• Saqueo de créditos corporativos y repuestos")
    ]
    
    card_w = 472
    card_h = 510
    start_y = 890
    spacing = 20
    
    for i, (title, img_path, color_accent, desc) in enumerate(props_cards):
        x = 40 + i * (card_w + spacing)
        
        draw.rounded_rectangle((x, start_y, x + card_w, start_y + card_h), radius=8, fill=(22, 26, 34, 255), outline=(45, 52, 65), width=2)
        draw.rounded_rectangle((x, start_y, x + card_w, start_y + 6), radius=3, fill=color_accent)
        
        if img_path and os.path.exists(img_path):
            p_img = Image.open(img_path).convert("RGBA")
            p_thumb = p_img.resize((card_w - 20, 275), Image.Resampling.LANCZOS)
            canvas.paste(p_thumb, (x + 10, start_y + 16))
            draw.rectangle((x + 10, start_y + 16, x + card_w - 10, start_y + 291), outline=(45, 52, 65), width=1)
            
        draw.text((x + 16, start_y + 305), title, fill=(255, 255, 255), font=font_card_title)
        draw.line((x + 16, start_y + 332, x + card_w - 16, start_y + 332), fill=(45, 52, 65), width=1)
        
        lines = desc.split("\n")
        line_y = start_y + 342
        for line in lines:
            draw.text((x + 16, line_y), line, fill=(185, 195, 210), font=font_card_desc)
            line_y += 22
            
        draw.rounded_rectangle((x + 16, start_y + card_h - 38, x + card_w - 16, start_y + card_h - 14), radius=4, fill=(15, 18, 24))
        draw.text((x + 24, start_y + card_h - 33), "ESTADO: APROBADO // ASSET MASTER UE5", fill=color_accent, font=font_pill)
        
    master_path = os.path.join(RENDERS_DIR, "Showcase_Lote6_Props_Master.png")
    canvas.save(master_path)
    print(f"[+] Lámina Maestra Compuesta generada con éxito: {master_path}")
    shutil.copy2(master_path, os.path.join(ARTIFACT_DIR, "Showcase_Lote6_Props_Master.png"))

# -------------------------------------------------------------------------
# FUNCIÓN PRINCIPAL
# -------------------------------------------------------------------------
def main():
    print("================================================================")
    print("   GENERANDO LOTE 6: VIDA A BORDO, CAMAROTES & HÁBITAT (PROPS 26-30)")
    print("================================================================")
    
    scene = reset_scene()
    col_props = create_collection("Lote6_Props_Habitats")
    col_studio = create_collection("Studio_Environment")
    col_cams = create_collection("Cameras")
    
    mats = create_materials()
    
    print("[1/5] Construyendo Prop 26: SM_Crew_Bunk_Double_Fold...")
    build_prop26(col_props, mats)

    print("[2/5] Construyendo Prop 27: SM_Nutrient_Paste_Dispenser...")
    build_prop27(col_props, mats)

    print("[3/5] Construyendo Prop 28: SM_Hydroponic_Sprout_Chamber...")
    build_prop28(col_props, mats)

    print("[4/5] Construyendo Prop 29: SM_Sanitation_Locker_Unit...")
    build_prop29(col_props, mats)

    print("[5/5] Construyendo Prop 30: SM_Crew_Personal_Locker...")
    build_prop30(col_props, mats)

    print("[*] Construyendo Entorno de Estudio y Pedestales...")
    build_environment(col_studio, mats)

    print("[*] Configurando Iluminación...")
    setup_lighting(col_studio)

    print("[*] Configurando Cámaras 3/4...")
    cams = setup_all_cameras(col_cams)

    print(f"[*] Guardando archivo Blender oficial: {BLEND_FILE}...")
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_FILE)

    print("[*] Iniciando Renderizado de Alta Definición...")
    render_all(cams)
    
    print("================================================================")
    print("   LOTE 6 GENERADO Y RENDERIZADO COMPLETAMENTE")
    print("================================================================")

if __name__ == "__main__":
    main()

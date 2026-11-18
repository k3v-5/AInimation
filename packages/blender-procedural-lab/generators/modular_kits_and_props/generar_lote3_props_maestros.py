# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Generador Maestro 3D - Lote 3 de Props: Contención de Peligros, Mitigación y Residuos
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
BLEND_FILE = os.path.join(PROJECT_ROOT, "Art", "Blender", "Lote3_Props_Maestros_Oficial.blend")

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
    w_bg.inputs['Color'].default_value = (0.025, 0.030, 0.040, 1.0)
    w_bg.inputs['Strength'].default_value = 0.75
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

    # 1. Acero Inoxidable & Plomo Pesado
    mats['Stainless_Steel'] = make_pbr("Mat_Stainless_Steel", (0.75, 0.78, 0.82, 1.0), roughness=0.28, metallic=0.92)
    mats['Heavy_Lead'] = make_pbr("Mat_Heavy_Lead", (0.18, 0.20, 0.23, 1.0), roughness=0.45, metallic=0.75)
    mats['Dark_Gunmetal'] = make_pbr("Mat_Dark_Gunmetal", (0.09, 0.10, 0.12, 1.0), roughness=0.32, metallic=0.92)
    
    # 2. Señalética de Peligro & Biohazard
    mats['Hazard_Yellow'] = make_pbr("Mat_Hazard_Yellow", (0.96, 0.74, 0.08, 1.0), roughness=0.40, metallic=0.10)
    mats['Hazard_Black'] = make_pbr("Mat_Hazard_Black", (0.05, 0.05, 0.06, 1.0), roughness=0.45, metallic=0.15)
    mats['Biohazard_Yellow'] = make_pbr("Mat_Biohazard_Yellow", (0.95, 0.80, 0.05, 1.0), roughness=0.35, metallic=0.12)
    
    # 3. Metales de Tubería & Cobre
    mats['Pure_Copper'] = make_pbr("Mat_Pure_Copper", (0.95, 0.54, 0.35, 1.0), roughness=0.22, metallic=0.96)
    mats['Machinery_Brass'] = make_pbr("Mat_Machinery_Brass", (0.88, 0.70, 0.28, 1.0), roughness=0.26, metallic=0.92)
    mats['Valve_Cyan'] = make_pbr("Mat_Valve_Cyan", (0.12, 0.55, 0.65, 1.0), roughness=0.30, metallic=0.20)
    
    # 4. Fuego & Incineración Térmica
    mats['Incinerator_Fire'] = make_pbr("Mat_Incinerator_Fire", (1.0, 0.35, 0.05, 1.0), roughness=0.10, metallic=0.0,
                                        emissive_col=(1.0, 0.38, 0.05, 1.0), emissive_str=6.0)
    mats['Incinerator_Iron'] = make_pbr("Mat_Incinerator_Iron", (0.14, 0.12, 0.12, 1.0), roughness=0.60, metallic=0.70)
    
    # 5. Vidrio Plomado Amarillo para Radiación
    mat_lead_glass = bpy.data.materials.new("Mat_Lead_Glass_Yellow")
    mat_lead_glass.use_nodes = True
    gnodes = mat_lead_glass.node_tree.nodes
    glinks = mat_lead_glass.node_tree.links
    gnodes.clear()
    g_out = gnodes.new(type='ShaderNodeOutputMaterial')
    g_bsdf = gnodes.new(type='ShaderNodeBsdfPrincipled')
    g_bsdf.inputs['Base Color'].default_value = (0.95, 0.85, 0.20, 1.0)
    g_bsdf.inputs['Roughness'].default_value = 0.12
    g_bsdf.inputs['Transmission Weight'].default_value = 0.82
    g_bsdf.inputs['IOR'].default_value = 1.62
    glinks.new(g_bsdf.outputs['BSDF'], g_out.inputs['Surface'])
    mats['Lead_Glass_Yellow'] = mat_lead_glass
    
    # 6. Escarcha Criogénica
    mats['Cryo_Frost'] = make_pbr("Mat_Cryo_Frost", (0.88, 0.96, 1.0, 1.0), roughness=0.45, metallic=0.08,
                                  emissive_col=(0.5, 0.85, 1.0, 1.0), emissive_str=1.2)
    mats['Bio_Green_Glow'] = make_pbr("Mat_Bio_Green_Glow", (0.1, 0.95, 0.25, 1.0), roughness=0.10, metallic=0.0,
                                      emissive_col=(0.15, 1.0, 0.30, 1.0), emissive_str=4.5)
    
    # 7. Plinto y Estudio
    mats['Studio_Floor'] = make_pbr("Mat_Studio_Floor", (0.045, 0.052, 0.062, 1.0), roughness=0.92, metallic=0.0)
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
        bm.faces.new((verts[0], verts[1], verts[2], verts[3])),
        bm.faces.new((verts[4], verts[7], verts[6], verts[5])),
        bm.faces.new((verts[0], verts[4], verts[5], verts[1])),
        bm.faces.new((verts[2], verts[6], verts[7], verts[3])),
        bm.faces.new((verts[0], verts[3], verts[7], verts[4])),
        bm.faces.new((verts[1], verts[5], verts[6], verts[2])),
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
# PROP 11: SM_Decontamination_Shower_Unit (Ducha de descontaminación química)
# -------------------------------------------------------------------------
def build_prop11_decon_shower(col, mats):
    def geom(bm):
        # Dimensiones: 120 x 120 x 240 cm
        # 1. Plataforma base de desagüe de rejilla de acero inoxidable con marco amarillo
        add_box(bm, (0, 0, 0.05), (1.20, 1.20, 0.10), mat_idx=2) # Marco amarillo
        add_box(bm, (0, 0, 0.06), (1.04, 1.04, 0.08), mat_idx=0) # Rejilla desagüe
        
        # 2. Tubería vertical maestra de suministro (lado posterior)
        add_cylinder(bm, (0, 0.48, 1.20), radius=0.045, height=2.20, segments=14, mat_idx=0, axis='Z')
        
        # 3. Brazo superior curvado hacia el centro
        add_cylinder(bm, (0, 0.24, 2.30), radius=0.045, height=0.50, segments=14, mat_idx=0, axis='Y')
        
        # 4. Rociador cónico masivo de latón (Deluge shower head) en (0, 0, 2.20)
        add_cylinder(bm, (0, 0, 2.22), radius=0.18, height=0.06, segments=20, mat_idx=4, axis='Z')
        add_cylinder(bm, (0, 0, 2.16), radius=0.24, height=0.04, segments=24, mat_idx=4, axis='Z')
        
        # 5. Cadena vertical y anilla triangular de tirador de emergencia
        add_cylinder(bm, (0.16, 0.0, 1.65), radius=0.008, height=0.90, segments=8, mat_idx=4, axis='Z')
        # Anilla triangular de accionamiento
        add_cylinder(bm, (0.16, 0.0, 1.15), radius=0.07, height=0.02, segments=16, mat_idx=4, axis='Y')
        
        # 6. Estación lavaojos lateral con palanca de empuje amarilla
        add_cylinder(bm, (0.42, 0.48, 1.05), radius=0.03, height=0.35, segments=10, mat_idx=0, axis='X')
        add_box(bm, (0.54, 0.48, 1.05), (0.22, 0.30, 0.08), mat_idx=0) # Bandeja inox
        add_cylinder(bm, (0.50, 0.44, 1.12), radius=0.025, height=0.05, segments=10, mat_idx=4, axis='Z') # Nozzle 1
        add_cylinder(bm, (0.50, 0.52, 1.12), radius=0.025, height=0.05, segments=10, mat_idx=4, axis='Z') # Nozzle 2
        add_box(bm, (0.64, 0.48, 1.05), (0.02, 0.12, 0.14), mat_idx=2) # Palanca amarilla
        
        # 7. Cartel de advertencia superior "EMERGENCY SHOWER"
        add_box(bm, (0, 0.48, 2.05), (0.55, 0.02, 0.22), mat_idx=2)

    mat_list = [
        mats['Stainless_Steel'], mats['Dark_Gunmetal'], mats['Hazard_Yellow'],
        mats['Hazard_Black'], mats['Machinery_Brass']
    ]
    return create_mesh_object("SM_Decontamination_Shower_Unit", col, geom, mat_list)

# -------------------------------------------------------------------------
# PROP 12: SM_Hazardous_Waste_Incinerator (Incinerador blindado con fuego)
# -------------------------------------------------------------------------
def build_prop12_incinerator(col, mats):
    def geom(bm):
        # Dimensiones: 160 x 140 x 210 cm
        # 1. Cuerpo principal del horno de acero térmico fundido
        add_box(bm, (0, 0, 0.85), (1.45, 1.25, 1.50), mat_idx=1)
        
        # 2. Costillas de disipación térmica laterales
        for rx in [-0.76, 0.76]:
            for rz in [0.45, 0.85, 1.25]:
                add_box(bm, (rx, 0, rz), (0.06, 1.15, 0.08), mat_idx=1)
                
        # 3. Compuerta vertical deslizante blindada frontal
        add_box(bm, (0, -0.64, 0.80), (0.90, 0.08, 0.90), mat_idx=0)
        
        # 4. Visor refractario de cuarzo con fuego interior brillante
        add_cylinder(bm, (0, -0.68, 0.80), radius=0.18, height=0.06, segments=20, mat_idx=0, axis='Y')
        add_cylinder(bm, (0, -0.66, 0.80), radius=0.14, height=0.04, segments=20, mat_idx=3, axis='Y') # Fuego naranja emisivo
        
        # Rejilla protectora de alambre sobre el visor
        add_box(bm, (0, -0.71, 0.80), (0.28, 0.015, 0.02), mat_idx=0)
        add_box(bm, (0, -0.71, 0.80), (0.02, 0.015, 0.28), mat_idx=0)
        
        # 5. Palanca masiva de elevación hidráulica y contrapeso
        add_cylinder(bm, (0.55, -0.66, 0.80), radius=0.035, height=0.12, segments=12, mat_idx=4, axis='Y')
        add_box(bm, (0.55, -0.72, 0.95), (0.04, 0.04, 0.32), mat_idx=4)
        
        # 6. Chimenea vertical superior aislada con válvula de sobrepresión
        add_cylinder(bm, (0, 0.25, 1.85), radius=0.20, height=0.60, segments=20, mat_idx=1, axis='Z')
        add_cylinder(bm, (0, 0.25, 2.15), radius=0.26, height=0.08, segments=20, mat_idx=0, axis='Z')
        
        # 7. Termómetro analógico de alta temperatura (0-1200°C)
        add_cylinder(bm, (-0.52, -0.66, 1.10), radius=0.075, height=0.03, segments=16, mat_idx=4, axis='Y')
        add_cylinder(bm, (-0.52, -0.676, 1.10), radius=0.06, height=0.005, segments=16, mat_idx=2, axis='Y')

    mat_list = [
        mats['Dark_Gunmetal'], mats['Incinerator_Iron'], mats['Hazard_Yellow'],
        mats['Incinerator_Fire'], mats['Machinery_Brass']
    ]
    return create_mesh_object("SM_Hazardous_Waste_Incinerator", col, geom, mat_list)

# -------------------------------------------------------------------------
# PROP 13: SM_Pressurized_Coolant_Manifold (Distribuidor criogénico)
# -------------------------------------------------------------------------
def build_prop13_coolant_manifold(col, mats):
    def geom(bm):
        cz = 0.65
        # Dimensiones: 140 x 80 x 60 cm
        # 1. Colector maestro horizontal de cobre oxidado
        add_cylinder(bm, (0, 0, cz), radius=0.10, height=1.30, segments=18, mat_idx=0, axis='X')
        add_cylinder(bm, (-0.66, 0, cz), radius=0.15, height=0.06, segments=18, mat_idx=1, axis='X') # Brida izq
        add_cylinder(bm, ( 0.66, 0, cz), radius=0.15, height=0.06, segments=18, mat_idx=1, axis='X') # Brida der
        
        # 2. Tres ramales verticales con manguitos criogénicos y escarcha
        for idx, bx in enumerate([-0.36, 0.0, 0.36]):
            # Tubo vertical
            add_cylinder(bm, (bx, 0, cz - 0.22), radius=0.055, height=0.35, segments=14, mat_idx=1, axis='Z')
            # Anillo de escarcha criogénica
            add_cylinder(bm, (bx, 0, cz - 0.15), radius=0.075, height=0.10, segments=14, mat_idx=5, axis='Z')
            
            # Válvula de compuerta con volante cian hacia el frente (-Y)
            add_cylinder(bm, (bx, -0.06, cz - 0.25), radius=0.065, height=0.08, segments=14, mat_idx=2, axis='Y')
            # Volante cian de 4 radios
            add_cylinder(bm, (bx, -0.16, cz - 0.25), radius=0.11, height=0.03, segments=18, mat_idx=3, axis='Y')
            add_cylinder(bm, (bx, -0.16, cz - 0.25), radius=0.03, height=0.04, segments=12, mat_idx=2, axis='Y')
            
        # 3. Manómetro analógico dual maestro central superior
        add_cylinder(bm, (0, -0.08, cz + 0.22), radius=0.085, height=0.035, segments=16, mat_idx=2, axis='Y')
        add_cylinder(bm, (0, -0.10, cz + 0.22), radius=0.07, height=0.005, segments=16, mat_idx=1, axis='Y')
        add_cylinder(bm, (0, 0, cz + 0.11), radius=0.025, height=0.14, segments=10, mat_idx=0, axis='Z') # Cuello
        
        # 4. Dos soportes de anclaje a mamparo de acero pesado
        add_box(bm, (-0.45, 0.18, cz), (0.08, 0.32, 0.28), mat_idx=1)
        add_box(bm, ( 0.45, 0.18, cz), (0.08, 0.32, 0.28), mat_idx=1)

    mat_list = [
        mats['Pure_Copper'], mats['Dark_Gunmetal'], mats['Machinery_Brass'],
        mats['Valve_Cyan'], mats['Hazard_Yellow'], mats['Cryo_Frost']
    ]
    return create_mesh_object("SM_Pressurized_Coolant_Manifold", col, geom, mat_list)

# -------------------------------------------------------------------------
# PROP 14: SM_Biohazard_Storage_Vault (Caja fuerte hermética de muestras)
# -------------------------------------------------------------------------
def build_prop14_biohazard_vault(col, mats):
    def geom(bm):
        cz = 0.50
        # Dimensiones: 90 x 150 x 70 cm
        # 1. Cuerpo del arcón blindado de plomo (ancho X = 1.35, prof Y = 0.75, alto Z = 0.65)
        add_box(bm, (0, 0, cz), (1.35, 0.75, 0.65), mat_idx=0) # Cuerpo plomo pesado
        
        # 2. Tapa abisagrada pesada con bordes achaflanados
        add_box(bm, (0, 0, cz + 0.36), (1.39, 0.79, 0.12), mat_idx=1) # Marco tapa
        
        # 3. Dos cierres de tracción magnética amarillos en el frente
        for cx in [-0.42, 0.42]:
            add_box(bm, (cx, -0.40, cz + 0.18), (0.10, 0.06, 0.24), mat_idx=2)
            add_cylinder(bm, (cx, -0.42, cz + 0.18), radius=0.03, height=0.06, segments=12, mat_idx=4, axis='Y')
            
        # 4. Panel central con símbolo Biohazard en la tapa
        add_box(bm, (0, -0.10, cz + 0.43), (0.45, 0.45, 0.015), mat_idx=2)
        # Símbolo circular biohazard
        add_cylinder(bm, (0, -0.10, cz + 0.44), radius=0.16, height=0.01, segments=20, mat_idx=3, axis='Z')
        add_cylinder(bm, (0, -0.10, cz + 0.445), radius=0.06, height=0.01, segments=16, mat_idx=2, axis='Z')
        
        # 5. Indicador digital de sellado y tubo de muestra luminiscente verde
        add_box(bm, (0, -0.39, cz + 0.12), (0.28, 0.03, 0.10), mat_idx=1)
        add_box(bm, (0, -0.408, cz + 0.12), (0.24, 0.005, 0.06), mat_idx=5) # Pantalla verde biológico
        
        # 6. Dos asas de arrastre reforzadas en los extremos X
        add_box(bm, (-0.70, 0, cz + 0.15), (0.05, 0.24, 0.08), mat_idx=4)
        add_box(bm, ( 0.70, 0, cz + 0.15), (0.05, 0.24, 0.08), mat_idx=4)

    mat_list = [
        mats['Heavy_Lead'], mats['Dark_Gunmetal'], mats['Biohazard_Yellow'],
        mats['Hazard_Black'], mats['Machinery_Brass'], mats['Bio_Green_Glow']
    ]
    return create_mesh_object("SM_Biohazard_Storage_Vault", col, geom, mat_list)

# -------------------------------------------------------------------------
# PROP 15: SM_Radiation_Lead_Shield_Screen (Mampara móvil rodante de plomo)
# -------------------------------------------------------------------------
def build_prop15_radiation_screen(col, mats):
    def geom(bm):
        cz = 1.05
        # Dimensiones: 150 x 30 x 200 cm
        # 1. Marco perimetral tubular y pletinas de esquina
        add_box(bm, (0, 0, cz), (1.46, 0.12, 1.90), mat_idx=1) # Marco
        # Placa masiva central de plomo de 20 mm
        add_box(bm, (0, 0, cz), (1.38, 0.05, 1.82), mat_idx=0) # Placa plomo
        
        # 2. Ventana de vidrio plomado amarillo (60 x 30 cm) a la altura de los ojos (Z = 1.45)
        add_box(bm, (0, 0, 1.45), (0.64, 0.14, 0.34), mat_idx=1) # Marco ventana
        add_box(bm, (0, 0, 1.45), (0.58, 0.06, 0.28), mat_idx=3) # Vidrio amarillo plomado
        
        # 3. Cuatro ruedas industriales con freno de pie
        for wx in [-0.60, 0.60]:
            for wy in [-0.22, 0.22]:
                # Soporte de rueda
                add_box(bm, (wx, wy, 0.12), (0.08, 0.08, 0.12), mat_idx=1)
                # Rueda de acero/nylon
                add_cylinder(bm, (wx, wy, 0.06), radius=0.06, height=0.04, segments=14, mat_idx=1, axis='X')
                
        # Travesaños estabilizadores inferiores que unen las ruedas
        add_box(bm, (-0.60, 0, 0.16), (0.08, 0.52, 0.05), mat_idx=1)
        add_box(bm, ( 0.60, 0, 0.16), (0.08, 0.52, 0.05), mat_idx=1)
        
        # 4. Barra horizontal de empuje en la cara trasera (+Y)
        add_cylinder(bm, (0, 0.18, 1.05), radius=0.025, height=1.20, segments=12, mat_idx=2, axis='X')
        add_cylinder(bm, (-0.55, 0.10, 1.05), radius=0.02, height=0.18, segments=10, mat_idx=2, axis='Y')
        add_cylinder(bm, ( 0.55, 0.10, 1.05), radius=0.02, height=0.18, segments=10, mat_idx=2, axis='Y')
        
        # 5. Franjas de advertencia de radiación amarilla/negra en la base de la mampara
        for i in range(-5, 6):
            add_box(bm, (i * 0.12, -0.04, 0.35), (0.10, 0.01, 0.18), mat_idx=4 if i % 2 == 0 else 5)

    mat_list = [
        mats['Heavy_Lead'], mats['Dark_Gunmetal'], mats['Machinery_Brass'],
        mats['Lead_Glass_Yellow'], mats['Hazard_Yellow'], mats['Hazard_Black']
    ]
    return create_mesh_object("SM_Radiation_Lead_Shield_Screen", col, geom, mat_list)

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
    draw.text((40, 46), "CATÁLOGO DE PROPS - LOTE 3 (PROPS 11-15): CONTENCIÓN DE PELIGROS, MITIGACIÓN Y RESIDUOS", fill=(255, 255, 255), font=font_title)
    
    pills = [
        ("LOTE 3 DE 10", (211, 84, 0)),
        ("CONTENCIÓN QUÍMICA & RAD", (41, 128, 185)),
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
    
    pan_path = os.path.join(RENDERS_DIR, "Showcase_Lote3_Props_Panorama.png")
    if os.path.exists(pan_path):
        pan_img = Image.open(pan_path).convert("RGBA")
        pan_w = W - 80
        pan_h = 760
        pan_resized = pan_img.resize((pan_w, pan_h), Image.Resampling.LANCZOS)
        canvas.paste(pan_resized, (40, 110))
        draw.rectangle((40, 110, 40 + pan_w, 110 + pan_h), outline=(45, 52, 65), width=2)
        
    props_cards = [
        ("11. SM_Decontamination_Shower_Unit", "Showcase_Prop11_Decontamination_Shower_Unit.png", (245, 166, 35),
         "• Ducha de descontaminación de acero inox\n• Rociador cónico masivo de latón y tirador\n• Estación lavaojos con palanca amarilla\n• Rejilla de desagüe y marco de seguridad"),
         
        ("12. SM_Hazardous_Waste_Incinerator", "Showcase_Prop12_Hazardous_Waste_Incinerator.png", (231, 76, 60),
         "• Horno incinerador de hierro refractario\n• Visor de cuarzo con fuego vivo a 1200°C\n• Compuerta vertical con palanca masiva\n• Chimenea superior aislada y termómetro"),
         
        ("13. SM_Pressurized_Coolant_Manifold", "Showcase_Prop13_Pressurized_Coolant_Manifold.png", (41, 128, 185),
         "• Colector maestro de cobre con bridas\n• 3 ramales con manguitos criogénicos LN2\n• Volantes cian de corte y manómetro dual\n• Soportes masivos de mamparo con pernos"),
         
        ("14. SM_Biohazard_Storage_Vault", "Showcase_Prop14_Biohazard_Storage_Vault.png", (39, 174, 96),
         "• Arcón blindado de plomo con cierre magnético\n• Tapa achaflanada con logo Biohazard\n• Display frontal con telemetría verde activo\n• Asas de arrastre para muestras orgánicas"),
         
        ("15. SM_Radiation_Lead_Shield_Screen", "Showcase_Prop15_Radiation_Lead_Shield_Screen.png", (155, 89, 182),
         "• Mampara móvil de plomo de 20mm con ruedas\n• Visor de vidrio plomado amarillo (60x30cm)\n• Barra horizontal posterior de empuje táctico\n• Chevrons amarillos y negros anti-radiación")
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

    master_path = os.path.join(RENDERS_DIR, "Showcase_Lote3_Props_Master.png")
    canvas.save(master_path, "PNG")
    
    shutil.copy2(master_path, os.path.join(ARTIFACT_DIR, "Showcase_Lote3_Props_Master.png"))
    for _, fname, _, _ in props_cards:
        fsrc = os.path.join(RENDERS_DIR, fname)
        if os.path.exists(fsrc):
            shutil.copy2(fsrc, os.path.join(ARTIFACT_DIR, fname))
    if os.path.exists(pan_path):
        shutil.copy2(pan_path, os.path.join(ARTIFACT_DIR, "Showcase_Lote3_Props_Panorama.png"))
        
    print(f"\n[MASTER OK] Lámina Maestra Oficial generada con éxito: {master_path}")

# -------------------------------------------------------------------------
# FLUJO PRINCIPAL DE PRODUCCIÓN Y RENDER
# -------------------------------------------------------------------------
def main():
    print("=" * 80)
    print("ASTRA HAZARD - GENERADOR MAESTRO 3D (LOTE 3 DE PROPS)")
    print("CONTENCIÓN DE PELIGROS, MITIGACIÓN Y RESIDUOS")
    print("=" * 80)
    
    scene = reset_scene()
    mats = create_materials()
    
    col_props = create_collection("Props_Lote3")
    col_env = create_collection("Showroom_Environment")
    col_lights = create_collection("Lighting")
    col_cams = create_collection("Cameras")
    
    mesh_floor = bpy.data.meshes.new("Studio_Floor")
    bm_f = bmesh.new()
    add_box(bm_f, (0, 0, -0.05), (36.0, 24.0, 0.10), mat_idx=0)
    bm_f.to_mesh(mesh_floor)
    bm_f.free()
    floor_obj = bpy.data.objects.new("Studio_Floor", mesh_floor)
    floor_obj.data.materials.append(mats['Studio_Floor'])
    col_env.objects.link(floor_obj)
    
    # 5 Props Lote 3
    prop_configs = [
        {"id": 11, "x": -6.4, "name": "Decontamination_Shower_Unit", "label": "11 // DECON SHOWER", "build": build_prop11_decon_shower, "w": 2.0, "d": 1.8, "cam_dist": 4.6, "cam_z": 1.60, "targ_z": 1.20},
        {"id": 12, "x": -3.2, "name": "Hazardous_Waste_Incinerator", "label": "12 // WASTE INCINERATOR", "build": build_prop12_incinerator, "w": 2.2, "d": 1.8, "cam_dist": 4.2, "cam_z": 1.45, "targ_z": 1.05},
        {"id": 13, "x":  0.0, "name": "Pressurized_Coolant_Manifold", "label": "13 // COOLANT MANIFOLD", "build": build_prop13_coolant_manifold, "w": 2.0, "d": 1.6, "cam_dist": 2.8, "cam_z": 0.95, "targ_z": 0.65},
        {"id": 14, "x":  3.2, "name": "Biohazard_Storage_Vault", "label": "14 // BIOHAZARD VAULT", "build": build_prop14_biohazard_vault, "w": 2.0, "d": 1.6, "cam_dist": 2.6, "cam_z": 0.95, "targ_z": 0.50},
        {"id": 15, "x":  6.4, "name": "Radiation_Lead_Shield_Screen", "label": "15 // RADIATION LEAD SHIELD", "build": build_prop15_radiation_screen, "w": 2.0, "d": 1.6, "cam_dist": 4.2, "cam_z": 1.45, "targ_z": 1.05},
    ]
    
    props_created = []
    for cfg in prop_configs:
        build_pedestal(col_env, mats, cfg['name'], pos_x=cfg['x'], width=cfg['w'], depth=cfg['d'], label_text=cfg['label'])
        obj = cfg['build'](col_props, mats)
        obj.location.x = cfg['x']
        obj.location.z = 0.16
        props_created.append(obj)
        print(f"  [OK] Creado Prop {cfg['id']:02d}: {obj.name} en X={cfg['x']}")
        
    setup_lighting(col_lights)
    
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
    
    scene.camera = cam_pan
    scene.render.resolution_x = 2560
    scene.render.resolution_y = 900
    scene.render.filepath = os.path.join(RENDERS_DIR, "Showcase_Lote3_Props_Panorama.png")
    bpy.ops.render.render(write_still=True)
    print("  [OK] Renderizado Panorama General.")
    
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    for cam, fname in ind_cams:
        scene.camera = cam
        scene.render.filepath = os.path.join(RENDERS_DIR, fname)
        bpy.ops.render.render(write_still=True)
        print(f"  [OK] Renderizado Close-Up: {fname}")
        
    assemble_master_infographic()
    print("\n" + "=" * 80)
    print("LOTE 3 DE PROPS MAESTROS COMPLETADO CON ÉXITO")
    print("=" * 80)

if __name__ == "__main__":
    main()

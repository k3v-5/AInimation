# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Generador Maestro 3D - Lote 4 de Props: Medicina, Triage y Soporte Vital
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
BLEND_FILE = os.path.join(PROJECT_ROOT, "Art", "Blender", "Lote4_Props_Maestros_Oficial.blend")

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
    w_bg.inputs['Color'].default_value = (0.022, 0.026, 0.034, 1.0)
    w_bg.inputs['Strength'].default_value = 0.70
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
    
    def make_pbr(name, base_col, roughness=0.5, metallic=0.0, emissive_col=(0,0,0,1), emissive_str=0.0, transmission=0.0):
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
        if 'Transmission Weight' in node_bsdf.inputs:
            node_bsdf.inputs['Transmission Weight'].default_value = transmission
        elif 'Transmission' in node_bsdf.inputs:
            node_bsdf.inputs['Transmission'].default_value = transmission
            
        if 'Emission Color' in node_bsdf.inputs:
            node_bsdf.inputs['Emission Color'].default_value = emissive_col
            node_bsdf.inputs['Emission Strength'].default_value = emissive_str
            
        links.new(node_bsdf.outputs['BSDF'], node_out.inputs['Surface'])
        return mat

    mats['Hospital_White'] = make_pbr("Mat_Hospital_White", (0.86, 0.89, 0.92, 1.0), roughness=0.32, metallic=0.05)
    mats['Clinical_Cyan'] = make_pbr("Mat_Clinical_Cyan", (0.09, 0.42, 0.55, 1.0), roughness=0.38, metallic=0.10)
    mats['Medical_Red_Cross'] = make_pbr("Mat_Medical_Red_Cross", (0.88, 0.08, 0.10, 1.0), roughness=0.25, metallic=0.05)
    mats['Emergency_Red_Glow'] = make_pbr("Mat_Emergency_Red_Glow", (1.0, 0.15, 0.12, 1.0), roughness=0.15, metallic=0.0,
                                          emissive_col=(1.0, 0.12, 0.10, 1.0), emissive_str=5.0)
    mats['ECG_Green_Glow'] = make_pbr("Mat_ECG_Green_Glow", (0.1, 0.95, 0.35, 1.0), roughness=0.12, metallic=0.0,
                                      emissive_col=(0.15, 1.0, 0.40, 1.0), emissive_str=5.5)
    mats['Cryo_Blue_Glass'] = make_pbr("Mat_Cryo_Blue_Glass", (0.45, 0.78, 0.95, 1.0), roughness=0.08, metallic=0.05,
                                       emissive_col=(0.20, 0.75, 0.95, 1.0), emissive_str=0.4, transmission=0.92)
    mats['Cryo_Frost'] = make_pbr("Mat_Cryo_Frost", (0.92, 0.96, 1.0, 1.0), roughness=0.75, metallic=0.0)
    mats['Dark_Titanium'] = make_pbr("Mat_Dark_Titanium", (0.11, 0.12, 0.14, 1.0), roughness=0.42, metallic=0.85)
    mats['Stainless_Steel'] = make_pbr("Mat_Stainless_Steel", (0.75, 0.78, 0.82, 1.0), roughness=0.20, metallic=0.92)
    mats['Machinery_Brass'] = make_pbr("Mat_Machinery_Brass", (0.88, 0.70, 0.28, 1.0), roughness=0.25, metallic=0.90)
    mats['Hazard_Yellow'] = make_pbr("Mat_Hazard_Yellow", (0.96, 0.74, 0.08, 1.0), roughness=0.38, metallic=0.10)
    mats['Hazard_Orange'] = make_pbr("Mat_Hazard_Orange", (0.92, 0.38, 0.08, 1.0), roughness=0.50, metallic=0.05)
    mats['Rubber_Black'] = make_pbr("Mat_Rubber_Black", (0.07, 0.07, 0.08, 1.0), roughness=0.80, metallic=0.0)
    mats['Saline_IV_Liquid'] = make_pbr("Mat_Saline_IV_Liquid", (0.85, 0.94, 0.98, 1.0), roughness=0.15, metallic=0.0,
                                        transmission=0.90)
    mats['Triage_Amber_Glow'] = make_pbr("Mat_Triage_Amber_Glow", (1.0, 0.65, 0.05, 1.0), roughness=0.15, metallic=0.0,
                                         emissive_col=(1.0, 0.70, 0.08, 1.0), emissive_str=4.8)
    mats['Plasma_Cyan'] = make_pbr("Mat_Plasma_Cyan", (0.1, 0.85, 1.0, 1.0), roughness=0.10, metallic=0.0,
                                   emissive_col=(0.0, 0.95, 1.0, 1.0), emissive_str=5.0)

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
    
    for mat in materials:
        if mat:
            obj.data.materials.append(mat)
            
    return obj

def add_box(bm, center, size, mat_idx=0, rot_z=0.0):
    dx, dy, dz = size[0]*0.5, size[1]*0.5, size[2]*0.5
    cx, cy, cz = center
    
    raw_verts = [
        (-dx, -dy, -dz), (dx, -dy, -dz), (dx, dy, -dz), (-dx, dy, -dz),
        (-dx, -dy, dz),  (dx, -dy, dz),  (dx, dy, dz),  (-dx, dy, dz)
    ]
    
    cos_a = math.cos(rot_z)
    sin_a = math.sin(rot_z)
    
    verts = []
    for rx, ry, rz in raw_verts:
        x_rot = rx * cos_a - ry * sin_a + cx
        y_rot = rx * sin_a + ry * cos_a + cy
        z_rot = rz + cz
        verts.append(bm.verts.new((x_rot, y_rot, z_rot)))
        
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
# PROP 16: SM_Trauma_Kit_Wall_Cabinet (Botiquín de pared rompe-fácil)
# -------------------------------------------------------------------------
def build_prop16_trauma_cabinet(col, mats):
    def geom(bm):
        px = -6.0
        # Dimensiones compactas de pared: 56 x 22 x 78 cm (sin placa gigante desplazada)
        # 0. Placa posterior de anclaje a mamparo (ajustada al contorno del gabinete)
        add_box(bm, (px, 0.10, 0.68), (0.58, 0.03, 0.78), mat_idx=2) # Dark_Titanium
        for bx_off in (-0.26, 0.26):
            for bz_off in (0.33, 1.03):
                add_cylinder(bm, (px + bx_off, 0.085, bz_off), radius=0.014, height=0.02, segments=8, mat_idx=5, axis='Y')

        # 1. Cuerpo del gabinete (caja hueca de chapa blanca hospitalaria)
        # Fondo posterior
        add_box(bm, (px, 0.085, 0.68), (0.52, 0.02, 0.72), mat_idx=0) # Fondo Hospital_White
        # Paredes laterales
        add_box(bm, (px - 0.25, 0.0, 0.68), (0.02, 0.18, 0.72), mat_idx=0)
        add_box(bm, (px + 0.25, 0.0, 0.68), (0.02, 0.18, 0.72), mat_idx=0)
        # Techo y suelo del gabinete
        add_box(bm, (px, 0.0, 1.03), (0.52, 0.18, 0.02), mat_idx=0)
        add_box(bm, (px, 0.0, 0.33), (0.52, 0.18, 0.02), mat_idx=0)

        # 2. Estantes interiores con reborde frontal de acero inoxidable
        add_box(bm, (px, 0.01, 0.70), (0.48, 0.15, 0.02), mat_idx=2) # Estante sup
        add_box(bm, (px, -0.065, 0.705), (0.48, 0.01, 0.025), mat_idx=5)
        add_box(bm, (px, 0.01, 0.48), (0.48, 0.15, 0.02), mat_idx=2) # Estante inf
        add_box(bm, (px, -0.065, 0.485), (0.48, 0.01, 0.025), mat_idx=5)

        # 3. Contenido interior visible en ambos estantes:
        # Estante Superior (z_base = 0.71): 3 Autoinyectores cilíndricos con émbolos y tapas de color
        # Inyector 1: Adrenalina (verde)
        add_cylinder(bm, (px - 0.14, 0.0, 0.78), radius=0.026, height=0.14, segments=12, mat_idx=5, axis='Z')
        add_cylinder(bm, (px - 0.14, 0.0, 0.865), radius=0.020, height=0.035, segments=12, mat_idx=6, axis='Z')
        # Inyector 2: Morfina (azul cian)
        add_cylinder(bm, (px, 0.0, 0.78), radius=0.026, height=0.14, segments=12, mat_idx=5, axis='Z')
        add_cylinder(bm, (px, 0.0, 0.865), radius=0.020, height=0.035, segments=12, mat_idx=7, axis='Z')
        # Inyector 3: O2 concentrado (naranja)
        add_cylinder(bm, (px + 0.14, 0.0, 0.78), radius=0.026, height=0.14, segments=12, mat_idx=5, axis='Z')
        add_cylinder(bm, (px + 0.14, 0.0, 0.865), radius=0.020, height=0.035, segments=12, mat_idx=8, axis='Z')

        # Estante Inferior (z_base = 0.49): Botiquín hemostático con Cruz Roja y frasco antiséptico
        add_box(bm, (px - 0.11, 0.0, 0.55), (0.16, 0.11, 0.12), mat_idx=0) # Caja gasas blancas
        add_box(bm, (px - 0.11, -0.056, 0.55), (0.07, 0.006, 0.022), mat_idx=1) # Cruz roja horiz
        add_box(bm, (px - 0.11, -0.056, 0.55), (0.022, 0.006, 0.07), mat_idx=1) # Cruz roja vert
        add_cylinder(bm, (px + 0.12, 0.0, 0.56), radius=0.044, height=0.14, segments=14, mat_idx=7, axis='Z') # Frasco cian
        add_cylinder(bm, (px + 0.12, 0.0, 0.645), radius=0.022, height=0.03, segments=12, mat_idx=9, axis='Z') # Tapón latón

        # 4. Puerta frontal articulada en la bisagra izquierda (px - 0.25, -0.09) abierta hacia afuera/izquierda (-105°)
        # Despeja 100% el interior del gabinete sin cortar los estantes
        hinge_x = px - 0.25
        hinge_y = -0.09
        for hz in (0.44, 0.92):
            add_cylinder(bm, (hinge_x, hinge_y, hz), radius=0.012, height=0.06, segments=10, mat_idx=5, axis='Z')

        door_ang = R(-125.0)
        cos_a = math.cos(door_ang)
        sin_a = math.sin(door_ang)

        def door_part_pos(l_center, y_offset):
            return (
                hinge_x + l_center * cos_a - y_offset * sin_a,
                hinge_y + l_center * sin_a + y_offset * cos_a
            )

        # Marco de puerta de 4 largueros sin superposición coplanar con el cristal central
        # Larguero izquierdo (bisagra, l = 0.00..0.07) y derecho (cierre, l = 0.43..0.50)
        dlx, dly = door_part_pos(0.035, 0.0)
        add_box(bm, (dlx, dly, 0.68), (0.07, 0.028, 0.72), mat_idx=0, rot_z=door_ang)
        drx, dry = door_part_pos(0.465, 0.0)
        add_box(bm, (drx, dry, 0.68), (0.07, 0.028, 0.72), mat_idx=0, rot_z=door_ang)
        # Travesaños superior (z = 0.97..1.04) e inferior (z = 0.32..0.39) entre largueros
        dtx, dty = door_part_pos(0.25, 0.0)
        add_box(bm, (dtx, dty, 1.005), (0.36, 0.028, 0.07), mat_idx=0, rot_z=door_ang)
        add_box(bm, (dtx, dty, 0.355), (0.36, 0.028, 0.07), mat_idx=0, rot_z=door_ang)
        # Cristal templado central encastrado sin solapar los largueros (l = 0.07..0.43, z = 0.39..0.97)
        gcx, gcy = door_part_pos(0.25, 0.0)
        add_box(bm, (gcx, gcy, 0.68), (0.356, 0.016, 0.576), mat_idx=4, rot_z=door_ang)
        # Cruz Roja médica en relieve limpio (>= 6mm sobre el cristal) en ambas caras de la puerta
        for side_y in (-0.014, 0.014):
            ccx, ccy = door_part_pos(0.25, side_y)
            add_box(bm, (ccx, ccy, 0.68), (0.18, 0.008, 0.055), mat_idx=1, rot_z=door_ang)
            add_box(bm, (ccx, ccy, 0.68), (0.055, 0.008, 0.18), mat_idx=1, rot_z=door_ang)
        # Manilla cromada en ambas caras del larguero derecho (l_center = 0.465)
        for h_side_y in (-0.022, 0.022):
            hcx, hcy = door_part_pos(0.465, h_side_y)
            add_box(bm, (hcx, hcy, 0.68), (0.022, 0.014, 0.14), mat_idx=5, rot_z=door_ang)

        # 5. Martillo percutor de emergencia adosado sin holguras al costado derecho (px + 0.26)
        add_box(bm, (px + 0.27, -0.01, 0.68), (0.03, 0.05, 0.06), mat_idx=2) # Clip de sujeción adosado
        add_cylinder(bm, (px + 0.285, -0.01, 0.64), radius=0.013, height=0.20, segments=10, mat_idx=10, axis='Z') # Mango goma
        add_box(bm, (px + 0.285, -0.01, 0.75), (0.036, 0.085, 0.036), mat_idx=1) # Cabeza percutora roja médica

        # 6. Cabezal superior integrado al ras del techo del gabinete (sin flotar)
        add_box(bm, (px, -0.02, 1.055), (0.50, 0.12, 0.045), mat_idx=2) # Cabezal titanio unido a z=1.03..1.04
        add_box(bm, (px, -0.081, 1.055), (0.44, 0.006, 0.030), mat_idx=0) # Placa frontal blanca
        add_box(bm, (px, -0.085, 1.055), (0.32, 0.005, 0.014), mat_idx=1) # Franja médica roja

    mat_list = [
        mats['Hospital_White'], mats['Medical_Red_Cross'], mats['Dark_Titanium'],
        mats['Emergency_Red_Glow'], mats['Cryo_Blue_Glass'], mats['Stainless_Steel'],
        mats['ECG_Green_Glow'], mats['Clinical_Cyan'], mats['Hazard_Orange'],
        mats['Machinery_Brass'], mats['Rubber_Black']
    ]
    return create_mesh_object("SM_Trauma_Kit_Wall_Cabinet", col, geom, mat_list)

# -------------------------------------------------------------------------
# PROP 17: SM_Stasis_Sleeper_Pod (Cápsula de hibernación/estasis médica)
# -------------------------------------------------------------------------
def build_prop17_stasis_pod(col, mats):
    def geom(bm):
        px = -3.0
        # Dimensiones: 220 x 90 x 110 cm
        # 1. Dos zócalos estructurales transversales de titanio sobre el pedestal
        add_box(bm, (px - 0.70, 0, 0.22), (0.24, 0.85, 0.12), mat_idx=0) # Dark_Titanium
        add_box(bm, (px + 0.70, 0, 0.22), (0.24, 0.85, 0.12), mat_idx=0)
        
        # 2. Casco inferior de cuna ergonómica
        add_box(bm, (px, 0, 0.44), (2.10, 0.82, 0.34), mat_idx=0)
        # Remates curvos en cabecera y pies
        add_cylinder(bm, (px - 1.05, 0, 0.44), radius=0.41, height=0.34, segments=18, mat_idx=0, axis='Z')
        add_cylinder(bm, (px + 1.05, 0, 0.44), radius=0.41, height=0.34, segments=18, mat_idx=0, axis='Z')
        
        # 3. Interior ergonómico de la cápsula (camilla acolchada clínica)
        add_box(bm, (px, 0, 0.54), (1.85, 0.65, 0.12), mat_idx=1) # Colchón Clinical_Cyan
        # Almohada reposacabezas en cabecera (izquierda)
        add_box(bm, (px - 0.72, 0, 0.63), (0.34, 0.45, 0.08), mat_idx=2) # Hospital_White
        # Mascarilla de soporte vital de goma negra con manguera
        add_cylinder(bm, (px - 0.72, 0, 0.70), radius=0.08, height=0.06, segments=14, mat_idx=3, axis='Z')
        add_cylinder(bm, (px - 0.82, 0.10, 0.66), radius=0.025, height=0.18, segments=10, mat_idx=3, axis='X') # Tubo goma
        
        # 4. Cúpula acrílica estanca abierta a 35° hacia atrás (+Y)
        # Permite ver perfectamente el interior y la tecnología criogénica
        cupula_cy = 0.15
        cupula_cz = 0.82
        add_cylinder(bm, (px, cupula_cy, cupula_cz), radius=0.38, height=1.90, segments=24, mat_idx=4, axis='X') # Cryo_Blue_Glass
        # Marcos de sellado de titanio y bisagras hidráulicas cromadas
        add_box(bm, (px, cupula_cy + 0.36, cupula_cz), (1.92, 0.05, 0.05), mat_idx=0)
        add_box(bm, (px, cupula_cy - 0.36, cupula_cz), (1.92, 0.05, 0.05), mat_idx=0)
        # Dos pistones hidráulicos telescópicos de apertura cromados
        for hx in [-0.65, 0.65]:
            add_cylinder(bm, (px + hx, 0.28, 0.66), radius=0.025, height=0.32, segments=10, mat_idx=6, axis='Z')
            
        # 5. Mangueras corrugadas de retorno criogénico en la base frontal
        for sy in [-0.36]:
            add_cylinder(bm, (px - 0.95, sy, 0.38), radius=0.045, height=0.35, segments=12, mat_idx=3, axis='X')
            add_cylinder(bm, (px - 0.78, sy, 0.38), radius=0.06, height=0.04, segments=12, mat_idx=5, axis='X') # Brida latón
            
        # 6. Brazo articulado con monitor LCD de telemetría biométrica (ECG verde)
        # Inclinado 30° hacia la cámara para máxima legibilidad diegética
        mon_x = px + 0.20
        mon_y = -0.52
        mon_z = 0.80
        add_box(bm, (mon_x, mon_y + 0.08, 0.60), (0.06, 0.10, 0.06), mat_idx=6) # Soporte
        add_box(bm, (mon_x, mon_y, mon_z), (0.38, 0.04, 0.26), mat_idx=0, rot_z=R(-20)) # Carcasa monitor
        add_box(bm, (mon_x, mon_y - 0.022, mon_z), (0.33, 0.006, 0.21), mat_idx=7, rot_z=R(-20)) # Pantalla verde ECG
        
        # 7. Baliza cilíndrica de estasis activa en la cabecera
        add_cylinder(bm, (px - 1.05, 0, 0.80), radius=0.065, height=0.15, segments=16, mat_idx=8, axis='Z')

    mat_list = [
        mats['Dark_Titanium'], mats['Clinical_Cyan'], mats['Hospital_White'],
        mats['Rubber_Black'], mats['Cryo_Blue_Glass'], mats['Machinery_Brass'],
        mats['Stainless_Steel'], mats['ECG_Green_Glow'], mats['Plasma_Cyan']
    ]
    return create_mesh_object("SM_Stasis_Sleeper_Pod", col, geom, mat_list)

# -------------------------------------------------------------------------
# PROP 18: SM_Oxygen_Scrubber_Cartridge_Rack (Depurador de aire con zeolita)
# -------------------------------------------------------------------------
def build_prop18_scrubber_rack(col, mats):
    def geom(bm):
        px = 0.0
        # Dimensiones: 110 x 40 x 170 cm
        # 1. Base reforzada de titanio sobre el pedestal
        add_box(bm, (px, 0, 0.26), (1.12, 0.44, 0.20), mat_idx=0) # Dark_Titanium
        
        # 2. Paneles laterales verticales en blanco hospitalario con ranuras de ventilación
        add_box(bm, (px - 0.52, 0, 0.95), (0.08, 0.42, 1.25), mat_idx=1) # Hospital_White izq
        add_box(bm, (px + 0.52, 0, 0.95), (0.08, 0.42, 1.25), mat_idx=1) # Hospital_White der
        add_box(bm, (px, 0.18, 0.95), (1.08, 0.05, 1.25), mat_idx=0) # Panel trasero
        add_box(bm, (px, 0, 1.60), (1.16, 0.46, 0.08), mat_idx=0) # Techo
        
        # 3. Turbina centrífuga inferior de succión
        add_cylinder(bm, (px, -0.05, 0.44), radius=0.18, height=0.30, segments=20, mat_idx=0, axis='Y')
        add_cylinder(bm, (px, -0.21, 0.44), radius=0.16, height=0.02, segments=20, mat_idx=2, axis='Y') # Rejilla amarilla
        # Aspas en cruz
        add_box(bm, (px, -0.22, 0.44), (0.30, 0.01, 0.03), mat_idx=0)
        add_box(bm, (px, -0.22, 0.44), (0.03, 0.01, 0.30), mat_idx=0)
        
        # 4. Cuatro cartuchos de zeolita en 2 filas de 2
        # Fila inferior Z=0.82, Fila superior Z=1.18
        # Cartucho 1 (abajo izq)
        add_cylinder(bm, (px - 0.26, -0.02, 0.82), radius=0.11, height=0.36, segments=18, mat_idx=3, axis='Y')
        add_cylinder(bm, (px - 0.26, -0.21, 0.82), radius=0.03, height=0.05, segments=12, mat_idx=2, axis='Y') # Mango amarillo
        
        # Cartucho 2 (abajo der)
        add_cylinder(bm, (px + 0.26, -0.02, 0.82), radius=0.11, height=0.36, segments=18, mat_idx=3, axis='Y')
        add_cylinder(bm, (px + 0.26, -0.21, 0.82), radius=0.03, height=0.05, segments=12, mat_idx=2, axis='Y')
        
        # Cartucho 3 (arriba izq)
        add_cylinder(bm, (px - 0.26, -0.02, 1.18), radius=0.11, height=0.36, segments=18, mat_idx=3, axis='Y')
        add_cylinder(bm, (px - 0.26, -0.21, 1.18), radius=0.03, height=0.05, segments=12, mat_idx=2, axis='Y')
        
        # Cartucho 4 (arriba der) - ¡EXTRAÍDO HACIA EL FRENTE PARA DEMOSTRAR INTERACCIÓN!
        add_cylinder(bm, (px + 0.26, -0.16, 1.18), radius=0.11, height=0.36, segments=18, mat_idx=3, axis='Y')
        add_cylinder(bm, (px + 0.26, -0.35, 1.18), radius=0.03, height=0.05, segments=12, mat_idx=2, axis='Y')
        add_cylinder(bm, (px + 0.26, -0.10, 1.18), radius=0.125, height=0.04, segments=18, mat_idx=4, axis='Y') # Anillo latón
        
        # 5. Panel superior de instrumentación y LEDs de saturación de CO2
        add_box(bm, (px, -0.19, 1.45), (0.92, 0.03, 0.22), mat_idx=0)
        # Manómetro de presión analógico central
        add_cylinder(bm, (px, -0.21, 1.45), radius=0.075, height=0.025, segments=16, mat_idx=4, axis='Y')
        add_cylinder(bm, (px, -0.225, 1.45), radius=0.06, height=0.005, segments=16, mat_idx=1, axis='Y')
        
        # LEDs indicadores (verde OK, amarillo saturado, rojo crítico)
        for l_idx, (lx, l_mat) in enumerate([(-0.35, 5), (-0.22, 6), (0.22, 5), (0.35, 7)]):
            add_cylinder(bm, (px + lx, -0.21, 1.45), radius=0.025, height=0.015, segments=10, mat_idx=l_mat, axis='Y')

    mat_list = [
        mats['Dark_Titanium'], mats['Hospital_White'], mats['Hazard_Yellow'],
        mats['Clinical_Cyan'], mats['Machinery_Brass'], mats['ECG_Green_Glow'],
        mats['Triage_Amber_Glow'], mats['Emergency_Red_Glow']
    ]
    return create_mesh_object("SM_Oxygen_Scrubber_Cartridge_Rack", col, geom, mat_list)

# -------------------------------------------------------------------------
# PROP 19: SM_Burn_Triage_Gurney (Camilla rodante de quemados)
# -------------------------------------------------------------------------
def build_prop19_triage_gurney(col, mats):
    def geom(bm):
        px = 3.0
        # Dimensiones: 200 x 80 x 95 cm
        # 1. Cuatro ruedas orientables con pedal de freno amarillo sobre el pedestal
        for rx, ry in [(-0.75, -0.28), (-0.75, 0.28), (0.75, -0.28), (0.75, 0.28)]:
            # Rueda de goma
            add_cylinder(bm, (px + rx, ry, 0.23), radius=0.07, height=0.04, segments=14, mat_idx=0, axis='Y')
            # Horquilla de acero
            add_box(bm, (px + rx, ry, 0.31), (0.05, 0.06, 0.12), mat_idx=1)
            # Pedal de freno en ruedas delanteras
            if rx < 0:
                add_box(bm, (px + rx - 0.05, ry, 0.27), (0.06, 0.04, 0.02), mat_idx=2)
                
        # 2. Chasis tubular soldado en X / patas de tijera
        add_cylinder(bm, (px, 0, 0.35), radius=0.025, height=1.45, segments=12, mat_idx=1, axis='X') # Eje longitudinal inferior
        # Tirantes verticales de soporte
        for sy in [-0.26, 0.26]:
            add_cylinder(bm, (px - 0.38, sy, 0.54), radius=0.02, height=0.55, segments=10, mat_idx=1, axis='Z')
            add_cylinder(bm, (px + 0.38, sy, 0.54), radius=0.02, height=0.55, segments=10, mat_idx=1, axis='Z')
            
        # 3. Plataforma superior y barandillas perimétricas tubulares de acero inoxidable
        add_box(bm, (px, 0, 0.74), (1.92, 0.74, 0.04), mat_idx=1)
        # Asas de empuje tubulares en cabecera y pies
        add_cylinder(bm, (px - 0.98, 0, 0.82), radius=0.02, height=0.60, segments=12, mat_idx=0, axis='Y')
        add_cylinder(bm, (px + 0.98, 0, 0.82), radius=0.02, height=0.60, segments=12, mat_idx=0, axis='Y')
        
        # 4. Colchoneta médica de vinilo cian segmentada
        add_box(bm, (px + 0.18, 0, 0.81), (1.35, 0.66, 0.10), mat_idx=3) # Cuerpo cian
        # Cabecero ergonómico inclinado a 22°
        cab_ang = R(-22)
        cab_cx = px - 0.64
        cab_cz = 0.87
        add_box(bm, (cab_cx, 0, cab_cz), (0.48, 0.66, 0.09), mat_idx=3, rot_z=0.0) # Cabecero cian
        add_box(bm, (px - 0.75, 0, 0.93), (0.26, 0.42, 0.05), mat_idx=4) # Almohadilla reposacabezas blanca
        
        # 5. Dos correas de sujeción rápida de nylon naranja con hebilla metálica
        for cx in [-0.15, 0.55]:
            add_box(bm, (px + cx, 0, 0.87), (0.05, 0.68, 0.02), mat_idx=5) # Correa naranja
            add_box(bm, (px + cx, 0, 0.885), (0.07, 0.08, 0.025), mat_idx=1) # Hebilla cromada
            
        # 6. Poste telescópico de suero IV y doble bolsa translúcida
        add_cylinder(bm, (px - 0.88, -0.34, 1.15), radius=0.015, height=0.85, segments=12, mat_idx=1, axis='Z')
        add_cylinder(bm, (px - 0.88, -0.34, 1.56), radius=0.01, height=0.20, segments=10, mat_idx=1, axis='Y') # Gancho doble
        # 2 Bolsas de suero translúcidas
        for by in [-0.42, -0.26]:
            add_box(bm, (px - 0.88, by, 1.42), (0.04, 0.08, 0.18), mat_idx=6) # Saline_IV_Liquid
            add_cylinder(bm, (px - 0.88, by, 1.31), radius=0.012, height=0.03, segments=10, mat_idx=3, axis='Z') # Gotero
            
        # 7. Monitor portátil de constantes vitales en barandilla de los pies
        # Orientado hacia la cabecera / cámara
        mon_x = px + 0.80
        mon_y = 0.38
        mon_z = 0.92
        add_box(bm, (mon_x, mon_y, mon_z), (0.24, 0.04, 0.18), mat_idx=7, rot_z=R(15)) # Carcasa Dark_Titanium
        add_box(bm, (mon_x, mon_y - 0.022, mon_z), (0.21, 0.005, 0.15), mat_idx=8, rot_z=R(15)) # Pantalla verde ECG

    mat_list = [
        mats['Rubber_Black'], mats['Stainless_Steel'], mats['Hazard_Yellow'],
        mats['Clinical_Cyan'], mats['Hospital_White'], mats['Hazard_Orange'],
        mats['Saline_IV_Liquid'], mats['Dark_Titanium'], mats['ECG_Green_Glow']
    ]
    return create_mesh_object("SM_Burn_Triage_Gurney", col, geom, mat_list)

# -------------------------------------------------------------------------
# PROP 20: SM_Casualty_Identification_Kiosk (Terminal de triaje y registro)
# -------------------------------------------------------------------------
def build_prop20_triage_kiosk(col, mats):
    def geom(bm):
        px = 6.0
        # Dimensiones: 70 x 50 x 165 cm
        # 1. Base estabilizadora octogonal pesada sobre el pedestal
        add_box(bm, (px, 0, 0.22), (0.65, 0.52, 0.12), mat_idx=0) # Dark_Titanium
        for bx, by in [(-0.26, -0.20), (0.26, -0.20), (-0.26, 0.20), (0.26, 0.20)]:
            add_cylinder(bm, (px + bx, by, 0.285), radius=0.02, height=0.02, segments=10, mat_idx=1, axis='Z') # Pernos latón
            
        # 2. Fuste vertical estilizado en blanco hospitalario
        add_box(bm, (px, 0, 0.65), (0.46, 0.36, 0.75), mat_idx=2) # Hospital_White
        add_box(bm, (px - 0.24, 0, 0.65), (0.03, 0.38, 0.72), mat_idx=0) # Molduras laterales Dark_Titanium
        add_box(bm, (px + 0.24, 0, 0.65), (0.03, 0.38, 0.72), mat_idx=0)
        
        # 3. Consola interactiva inclinada a 30° hacia el usuario
        add_box(bm, (px, -0.06, 1.05), (0.50, 0.40, 0.24), mat_idx=2)
        # Pantalla táctil de triaje de plasma cian emisivo
        add_box(bm, (px, -0.18, 1.10), (0.40, 0.18, 0.02), mat_idx=3) # Pantalla cian interactiva
        
        # 4. Bandeja cóncava inferior con escáner óptico de pulseras RFID / biométrico
        add_box(bm, (px, -0.20, 0.88), (0.34, 0.12, 0.04), mat_idx=0) # Bandeja escaneo
        add_cylinder(bm, (px, -0.20, 0.905), radius=0.08, height=0.015, segments=16, mat_idx=4, axis='Z') # Emisor láser verde/cian
        
        # 5. Dispensador de etiquetas de triaje con ticket saliente en el lateral
        add_box(bm, (px + 0.255, -0.06, 0.98), (0.015, 0.12, 0.01), mat_idx=0) # Ranura
        add_box(bm, (px + 0.31, -0.06, 0.97), (0.10, 0.09, 0.005), mat_idx=2) # Ticket blanco saliente
        add_box(bm, (px + 0.31, -0.06, 0.972), (0.04, 0.08, 0.006), mat_idx=5) # Franja amarilla
        
        # 6. Baliza semafórica superior de 3 luces de triaje de gravedad
        add_cylinder(bm, (px, 0, 1.28), radius=0.045, height=0.20, segments=12, mat_idx=0, axis='Z') # Mástil
        # Tres pisos de baliza cilíndrica
        add_cylinder(bm, (px, 0, 1.40), radius=0.065, height=0.06, segments=16, mat_idx=6, axis='Z') # T1 Inmediato (Rojo)
        add_cylinder(bm, (px, 0, 1.47), radius=0.065, height=0.06, segments=16, mat_idx=7, axis='Z') # T2 Urgente (Ámbar)
        add_cylinder(bm, (px, 0, 1.54), radius=0.065, height=0.06, segments=16, mat_idx=4, axis='Z') # T3 Leve (Verde activo)
        # Caperuza superior
        add_cylinder(bm, (px, 0, 1.59), radius=0.075, height=0.03, segments=16, mat_idx=0, axis='Z')

    mat_list = [
        mats['Dark_Titanium'], mats['Machinery_Brass'], mats['Hospital_White'],
        mats['Plasma_Cyan'], mats['ECG_Green_Glow'], mats['Hazard_Yellow'],
        mats['Emergency_Red_Glow'], mats['Triage_Amber_Glow']
    ]
    return create_mesh_object("SM_Casualty_Identification_Kiosk", col, geom, mat_list)

# -------------------------------------------------------------------------
# ESCENOGRAFÍA: PEDESTALES DE EXPOSICIÓN Y PLACAS GRABADAS
# -------------------------------------------------------------------------
def build_pedestal(col, mats, name, pos_x, width=2.4, depth=1.8, height=0.16):
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
    key_data.energy = 1150.0
    key_data.size = 24.0
    key_data.size_y = 8.0
    key_data.color = (0.95, 0.98, 1.0) # Blanco clínico puro
    key_obj = bpy.data.objects.new("Light_Key_Overhead", key_data)
    key_obj.location = (0, -4.8, 6.4)
    key_obj.rotation_euler = (R(35), 0, 0)
    col.objects.link(key_obj)
    
    rim_data = bpy.data.lights.new(name="Light_Rim_Back", type='AREA')
    rim_data.energy = 880.0
    rim_data.size = 26.0
    rim_data.size_y = 4.0
    rim_data.color = (0.80, 0.92, 1.0) # Rim cian sutil
    rim_obj = bpy.data.objects.new("Light_Rim_Back", rim_data)
    rim_obj.location = (0, 3.8, 5.2)
    rim_obj.rotation_euler = (R(-40), 0, R(180))
    col.objects.link(rim_obj)
    
    fill_l_data = bpy.data.lights.new(name="Light_Fill_Cool", type='AREA')
    fill_l_data.energy = 540.0
    fill_l_data.size = 10.0
    fill_l_data.color = (0.85, 0.95, 1.0)
    fill_l_obj = bpy.data.objects.new("Light_Fill_Cool", fill_l_data)
    fill_l_obj.location = (-12.0, -6.0, 4.2)
    fill_l_obj.rotation_euler = (R(30), R(-25), R(-40))
    col.objects.link(fill_l_obj)
    
    fill_r_data = bpy.data.lights.new(name="Light_Fill_Warm", type='AREA')
    fill_r_data.energy = 540.0
    fill_r_data.size = 10.0
    fill_r_data.color = (1.0, 0.90, 0.80)
    fill_r_obj = bpy.data.objects.new("Light_Fill_Warm", fill_r_data)
    fill_r_obj.location = (12.0, -6.0, 4.2)
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
    draw.text((40, 46), "CATÁLOGO DE PROPS - LOTE 4 (PROPS 16-20): MEDICINA, TRIAGE Y SOPORTE VITAL", fill=(255, 255, 255), font=font_title)
    
    pills = [
        ("LOTE 4 DE 10", (230, 126, 34)),
        ("TRIAGE & RESCATE", (26, 188, 156)),
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
    
    pan_path = os.path.join(RENDERS_DIR, "Showcase_Lote4_Props_Panorama.png")
    if os.path.exists(pan_path):
        pan_img = Image.open(pan_path).convert("RGBA")
        pan_w = W - 80
        pan_h = 760
        pan_resized = pan_img.resize((pan_w, pan_h), Image.Resampling.LANCZOS)
        canvas.paste(pan_resized, (40, 110))
        draw.rectangle((40, 110, 40 + pan_w, 110 + pan_h), outline=(45, 52, 65), width=2)
        
    props_cards = [
        ("16. SM_Trauma_Kit_Wall_Cabinet", "Showcase_Prop16_Trauma_Kit_Wall_Cabinet.png", (231, 76, 60),
         "• Botiquín de pared rompible con Cruz Roja\n• 3 autoinyectores (Adrenalina, Morfina, O2)\n• Paquetes hemostáticos y antiséptico\n• Martillo percutor rojo colgado con cadena"),
         
        ("17. SM_Stasis_Sleeper_Pod", "Showcase_Prop17_Stasis_Sleeper_Pod.png", (41, 128, 185),
         "• Pod médico de estasis de titanio curvado\n• Cúpula acrílica con pistones hidráulicos\n• Monitor lateral inclinado y ECG verde\n• Detiene hemorragia y sangrado de bajas"),
         
        ("18. SM_Oxygen_Scrubber_Cartridge_Rack", "Showcase_Prop18_Oxygen_Scrubber_Cartridge_Rack.png", (39, 174, 96),
         "• Depurador atmosférico con 4 cartuchos\n• Cartucho de zeolita superior interactivo\n• Turbina centrífuga con rejilla amarilla\n• LEDs de saturación de CO2 y manómetro"),
         
        ("19. SM_Burn_Triage_Gurney", "Showcase_Prop19_Burn_Triage_Gurney.png", (241, 196, 15),
         "• Camilla de quemados de acero inoxidable\n• 4 ruedas con freno y correas naranjas\n• Doble gotero IV con suero translúcido\n• Monitor compacto y transporte rápido"),
         
        ("20. SM_Casualty_Identification_Kiosk", "Showcase_Prop20_Casualty_Identification_Kiosk.png", (155, 89, 182),
         "• Terminal de registro de bajas corporativas\n• Pantalla táctil y escáner óptico RFID\n• Dispensador de ticket térmico de triaje\n• Baliza semafórica superior tricolor")
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
        
        lines = desc.split("\n")
        ly = card_y + 352
        for line in lines:
            draw.text((cx + 12, ly), line, fill=(200, 208, 220), font=font_card_desc)
            ly += 26
            
    master_path = os.path.join(RENDERS_DIR, "Showcase_Lote4_Props_Master.png")
    canvas.save(master_path, "PNG", quality=95)
    print(f"[COMPOSITOR] Lámina Maestra guardada exitosamente en:\n  -> {master_path}")
    
    art_master = os.path.join(ARTIFACT_DIR, "Showcase_Lote4_Props_Master.png")
    shutil.copy2(master_path, art_master)
    print(f"  -> Copiada a artefactos: {art_master}")

# -------------------------------------------------------------------------
# FUNCIÓN PRINCIPAL DE CONSTRUCCIÓN Y RENDER
# -------------------------------------------------------------------------
def main():
    print("==========================================================================")
    print("  ASTRA HAZARD - CONSTRUCTOR DE LOTE 4 DE PROPS (PROPS 16-20: MEDICINA)   ")
    print("==========================================================================")
    
    scene = reset_scene()
    col_props = create_collection("Lote4_Props_Medicina")
    col_studio = create_collection("Studio_Setup")
    
    mats = create_materials()
    
    # 1. Suelo continuo de estudio
    def floor_geom(bm):
        add_box(bm, (0, 0, -0.05), (38.0, 22.0, 0.1), mat_idx=0)
    create_mesh_object("Studio_Floor", col_studio, floor_geom, [mats['Studio_Floor']])
    
    # 2. Construcción de los 5 pedestales
    build_pedestal(col_studio, mats, "Prop16", pos_x=-6.0, width=2.0, depth=1.6)
    build_pedestal(col_studio, mats, "Prop17", pos_x=-3.0, width=2.6, depth=1.8)
    build_pedestal(col_studio, mats, "Prop18", pos_x= 0.0, width=2.0, depth=1.6)
    build_pedestal(col_studio, mats, "Prop19", pos_x= 3.0, width=2.5, depth=1.6)
    build_pedestal(col_studio, mats, "Prop20", pos_x= 6.0, width=2.0, depth=1.6)
    
    # 3. Construcción de los 5 Props de Medicina y Triage
    print("-> Construyendo Prop 16: SM_Trauma_Kit_Wall_Cabinet...")
    build_prop16_trauma_cabinet(col_props, mats)
    
    print("-> Construyendo Prop 17: SM_Stasis_Sleeper_Pod...")
    build_prop17_stasis_pod(col_props, mats)
    
    print("-> Construyendo Prop 18: SM_Oxygen_Scrubber_Cartridge_Rack...")
    build_prop18_scrubber_rack(col_props, mats)
    
    print("-> Construyendo Prop 19: SM_Burn_Triage_Gurney...")
    build_prop19_triage_gurney(col_props, mats)
    
    print("-> Construyendo Prop 20: SM_Casualty_Identification_Kiosk...")
    build_prop20_triage_kiosk(col_props, mats)
    
    # 4. Iluminación de estudio
    setup_lighting(col_studio)
    
    # 5. Cámaras con encuadres 3/4 heroicos y sin cortes de FOV
    col_cams = create_collection("Cameras")
    
    # Panorámica general (cubre holgadamente de X=-7.5 a X=+7.5 con 26mm a 12.2m de distancia)
    cam_pan = create_camera_tracking(col_cams, "Cam_Panorama", (0, -12.2, 3.4), (0, 0, 0.78), lens=26.0)
    
    # Close-ups 1080p en perspectiva 3/4
    # Prop 16: Vista 3/4 que captura la puerta abierta, la cruz roja, los 3 autoinyectores y el martillo
    cam_p16 = create_camera_tracking(col_cams, "Cam_Prop16", (-6.0 + 1.25, -2.5, 0.95), (-6.0, 0.02, 0.68), lens=46.0)
    
    # Prop 17: Vista 3/4 elevada mostrando la cúpula inclinada, colchón cian, almohada, mascarilla y ECG
    cam_p17 = create_camera_tracking(col_cams, "Cam_Prop17", (-3.0 + 1.5, -3.1, 1.55), (-3.0, 0, 0.62), lens=42.0)
    
    # Prop 18: Vista 3/4 que captura el rack vertical, turbina inferior, cartucho extraído y manómetro
    cam_p18 = create_camera_tracking(col_cams, "Cam_Prop18", ( 0.0 + 0.45, -2.85, 1.20), ( 0.0, -0.05, 0.95), lens=42.0)
    
    # Prop 19: Vista 3/4 que captura la camilla entera, ruedas con freno, colchoneta inclinada, gotero IV y monitor
    cam_p19 = create_camera_tracking(col_cams, "Cam_Prop19", ( 3.0 + 1.15, -3.25, 1.35), ( 3.0, 0, 0.88), lens=38.0)
    
    # Prop 20: Vista 3/4 que captura el kiosco completo, base octogonal, pantalla inclinada, escáner, ticket y baliza
    cam_p20 = create_camera_tracking(col_cams, "Cam_Prop20", ( 6.0 + 0.55, -2.75, 1.15), ( 6.0, -0.05, 0.95), lens=40.0)
    
    # 6. Guardar archivo .blend
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_FILE)
    print(f"\n[OK] Escena guardada en: {BLEND_FILE}")
    
    # 7. Renderizado fotográfico de alta resolución
    renders_to_do = [
        ("Showcase_Lote4_Props_Panorama.png", cam_pan, 2560, 900),
        ("Showcase_Prop16_Trauma_Kit_Wall_Cabinet.png", cam_p16, 1920, 1080),
        ("Showcase_Prop17_Stasis_Sleeper_Pod.png", cam_p17, 1920, 1080),
        ("Showcase_Prop18_Oxygen_Scrubber_Cartridge_Rack.png", cam_p18, 1920, 1080),
        ("Showcase_Prop19_Burn_Triage_Gurney.png", cam_p19, 1920, 1080),
        ("Showcase_Prop20_Casualty_Identification_Kiosk.png", cam_p20, 1920, 1080),
    ]
    
    for filename, cam_obj, rx, ry in renders_to_do:
        out_path = os.path.join(RENDERS_DIR, filename)
        print(f"\n[RENDER] Generando {filename} ({rx}x{ry}) con {cam_obj.name}...")
        scene.camera = cam_obj
        scene.render.resolution_x = rx
        scene.render.resolution_y = ry
        scene.render.filepath = out_path
        bpy.ops.render.render(write_still=True)
        
        # Copiar al directorio de artefactos
        art_path = os.path.join(ARTIFACT_DIR, filename)
        shutil.copy2(out_path, art_path)
        print(f"  -> Guardado: {out_path}")
        print(f"  -> Copiado a artefacto: {art_path}")
        
    # 8. Ensamblar lámina infográfica
    assemble_master_infographic()
    
    print("\n==========================================================================")
    print("  [EXITO] LOTE 4 DE PROPS (MEDICINA & TRIAGE) COMPLETADO AL 100%          ")
    print("==========================================================================")

if __name__ == "__main__":
    main()

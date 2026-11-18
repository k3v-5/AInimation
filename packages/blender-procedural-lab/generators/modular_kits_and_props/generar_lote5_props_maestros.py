# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Generador Maestro 3D - Lote 5 de Props: Cajas Negras, Servidores y Datos Corporativos
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
BLEND_FILE = os.path.join(PROJECT_ROOT, "Art", "Blender", "Lote5_Props_Maestros_Oficial.blend")

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

    mats['HighVis_Orange'] = make_pbr("Mat_HighVis_Orange", (0.98, 0.32, 0.04, 1.0), roughness=0.35, metallic=0.10)
    mats['Reflective_White'] = make_pbr("Mat_Reflective_White", (0.92, 0.94, 0.96, 1.0), roughness=0.15, metallic=0.20)
    mats['Dark_Gunmetal'] = make_pbr("Mat_Dark_Gunmetal", (0.09, 0.10, 0.12, 1.0), roughness=0.32, metallic=0.92)
    mats['Cast_Iron'] = make_pbr("Mat_Cast_Iron", (0.16, 0.17, 0.19, 1.0), roughness=0.50, metallic=0.80)
    mats['Dark_Titanium'] = make_pbr("Mat_Dark_Titanium", (0.12, 0.13, 0.15, 1.0), roughness=0.40, metallic=0.85)
    mats['Polished_Chrome'] = make_pbr("Mat_Polished_Chrome", (0.90, 0.92, 0.94, 1.0), roughness=0.08, metallic=0.98)
    mats['Machinery_Brass'] = make_pbr("Mat_Machinery_Brass", (0.88, 0.70, 0.28, 1.0), roughness=0.25, metallic=0.92)
    mats['Hardwood_Polished'] = make_pbr("Mat_Hardwood_Polished", (0.24, 0.12, 0.06, 1.0), roughness=0.28, metallic=0.0)
    mats['Hazard_Yellow'] = make_pbr("Mat_Hazard_Yellow", (0.96, 0.74, 0.08, 1.0), roughness=0.38, metallic=0.10)
    mats['Server_LED_Green'] = make_pbr("Mat_Server_LED_Green", (0.1, 0.95, 0.35, 1.0), roughness=0.12, metallic=0.0,
                                        emissive_col=(0.15, 1.0, 0.40, 1.0), emissive_str=6.0)
    mats['Server_LED_Amber'] = make_pbr("Mat_Server_LED_Amber", (1.0, 0.65, 0.05, 1.0), roughness=0.15, metallic=0.0,
                                        emissive_col=(1.0, 0.70, 0.08, 1.0), emissive_str=5.2)
    mats['Hologram_Cyan'] = make_pbr("Mat_Hologram_Cyan", (0.1, 0.85, 1.0, 1.0), roughness=0.08, metallic=0.0,
                                     emissive_col=(0.05, 0.90, 1.0, 1.0), emissive_str=6.0, transmission=0.80)
    mats['Hologram_Gold'] = make_pbr("Mat_Hologram_Gold", (1.0, 0.80, 0.15, 1.0), roughness=0.10, metallic=0.0,
                                     emissive_col=(1.0, 0.85, 0.20, 1.0), emissive_str=5.0, transmission=0.75)
    mats['Xenon_Flash_Glow'] = make_pbr("Mat_Xenon_Flash_Glow", (0.95, 0.98, 1.0, 1.0), roughness=0.10, metallic=0.0,
                                        emissive_col=(1.0, 1.0, 1.0, 1.0), emissive_str=8.0)
    mats['Optical_Fiber_Blue'] = make_pbr("Mat_Optical_Fiber_Blue", (0.15, 0.45, 0.95, 1.0), roughness=0.30, metallic=0.10)
    mats['Rubber_Black'] = make_pbr("Mat_Rubber_Black", (0.07, 0.07, 0.08, 1.0), roughness=0.80, metallic=0.0)

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
# PROP 21: SM_Flight_Data_Recorder_BlackBox (Caja negra de vuelo)
# -------------------------------------------------------------------------
def build_prop21_black_box(col, mats):
    def geom(bm):
        px = -6.0
        # Dimensiones: 45 x 35 x 35 cm montada en banco técnico sobre el pedestal
        # 1. Base o banco de soporte de ensayo sobre el pedestal
        add_box(bm, (px, 0, 0.25), (0.75, 0.55, 0.18), mat_idx=2) # Dark_Titanium
        for bx, by in [(-0.32, -0.22), (0.32, -0.22), (-0.32, 0.22), (0.32, 0.22)]:
            add_cylinder(bm, (px + bx, by, 0.35), radius=0.02, height=0.03, segments=10, mat_idx=3, axis='Z') # Pernos latón
            
        # 2. Caja negra blindada naranja internacional (longitud X=0.48, ancho Y=0.34, alto Z=0.32)
        cz = 0.52
        add_box(bm, (px, 0, cz), (0.48, 0.34, 0.32), mat_idx=0) # HighVis_Orange
        
        # Franjas reflectantes blancas diagonales/perimétricas
        add_box(bm, (px - 0.18, 0, cz), (0.04, 0.344, 0.324), mat_idx=1) # Franja blanca izq
        add_box(bm, (px + 0.18, 0, cz), (0.04, 0.344, 0.324), mat_idx=1) # Franja blanca der
        
        # 3. Baliza acústica subacuática cilíndrica acoplada en el frente (-Y)
        add_cylinder(bm, (px, -0.21, cz - 0.04), radius=0.042, height=0.32, segments=16, mat_idx=4, axis='X') # Tubo cromo
        add_cylinder(bm, (px + 0.17, -0.21, cz - 0.04), radius=0.045, height=0.03, segments=16, mat_idx=3, axis='X') # Cabezal latón
        # LED estroboscópico de xenón activo en la punta de la baliza
        add_cylinder(bm, (px + 0.19, -0.21, cz - 0.04), radius=0.025, height=0.015, segments=12, mat_idx=5, axis='X')
        
        # 4. Asa superior ergonómica de transporte abatible
        add_cylinder(bm, (px, 0, cz + 0.18), radius=0.014, height=0.28, segments=12, mat_idx=4, axis='X')
        add_box(bm, (px - 0.13, 0, cz + 0.17), (0.02, 0.04, 0.04), mat_idx=2)
        add_box(bm, (px + 0.13, 0, cz + 0.17), (0.02, 0.04, 0.04), mat_idx=2)
        
        # 5. Conector blindado multipin de interfaz con tapa de rosca
        add_cylinder(bm, (px - 0.12, -0.175, cz + 0.06), radius=0.03, height=0.025, segments=14, mat_idx=3, axis='Y')
        
        # 6. Rótulo diegético impreso "FLIGHT RECORDER // DO NOT OPEN"
        add_box(bm, (px, -0.172, cz + 0.08), (0.18, 0.005, 0.05), mat_idx=1)

    mat_list = [
        mats['HighVis_Orange'], mats['Reflective_White'], mats['Dark_Titanium'],
        mats['Machinery_Brass'], mats['Polished_Chrome'], mats['Xenon_Flash_Glow']
    ]
    return create_mesh_object("SM_Flight_Data_Recorder_BlackBox", col, geom, mat_list)

# -------------------------------------------------------------------------
# PROP 22: SM_Server_Rack_Reinforced (Rack de servidores corporativo)
# -------------------------------------------------------------------------
def build_prop22_server_rack(col, mats):
    def geom(bm):
        px = -3.0
        # Dimensiones: 80 x 100 x 220 cm
        # 1. Chasis exterior vertical blindado en Gunmetal oscuro
        cz = 1.25
        # Pared trasera y laterales
        add_box(bm, (px, 0.40, cz), (0.84, 0.16, 2.18), mat_idx=0) # Trasera Dark_Gunmetal
        add_box(bm, (px - 0.38, 0, cz), (0.08, 0.96, 2.18), mat_idx=0) # Lateral izq
        add_box(bm, (px + 0.38, 0, cz), (0.08, 0.96, 2.18), mat_idx=0) # Lateral der
        add_box(bm, (px, 0, 2.26), (0.84, 0.96, 0.16), mat_idx=0) # Techo
        add_box(bm, (px, 0, 0.24), (0.84, 0.96, 0.16), mat_idx=0) # Base
        
        # 2. Cavidad interior hueca para bandejas (bahías de servidores)
        add_box(bm, (px, 0.0, cz), (0.68, 0.70, 1.86), mat_idx=1) # Dark_Titanium
        
        # 3. Zócalo inferior con turbina de refrigeración
        add_cylinder(bm, (px, -0.40, 0.40), radius=0.16, height=0.06, segments=18, mat_idx=2, axis='Y') # Rejilla amarilla
        add_box(bm, (px, -0.41, 0.40), (0.28, 0.01, 0.03), mat_idx=0)
        
        # 4. Seis bandejas modulares de discos duros en vertical
        # Bandeja 4 (Z=1.40) ¡PARCIALMENTE EXTRAÍDA hacia el frente (-Y)!
        for idx, bz in enumerate([0.65, 0.90, 1.15, 1.40, 1.65, 1.90]):
            is_extracted = (idx == 3)
            by_off = -0.22 if is_extracted else 0.0
            
            # Bloque de la bandeja
            add_box(bm, (px, 0.05 + by_off, bz), (0.64, 0.65, 0.18), mat_idx=1)
            # Frontal con tirador de extracción
            add_box(bm, (px, -0.28 + by_off, bz), (0.64, 0.02, 0.18), mat_idx=0)
            add_box(bm, (px, -0.30 + by_off, bz), (0.24, 0.02, 0.05), mat_idx=3) # Asa latón
            
            # Contactos dorados visibles en los laterales si está extraída
            if is_extracted:
                add_box(bm, (px - 0.31, -0.10, bz), (0.015, 0.22, 0.04), mat_idx=3)
                add_box(bm, (px + 0.31, -0.10, bz), (0.015, 0.22, 0.04), mat_idx=3)
                
            # LEDs de actividad de datos (verde y ámbar)
            for lx, led_mat in [(-0.24, 4), (-0.18, 5), (-0.12, 4), (0.18, 4), (0.24, 5)]:
                add_cylinder(bm, (px + lx, -0.30 + by_off, bz + 0.04), radius=0.014, height=0.015, segments=8, mat_idx=led_mat, axis='Y')
                
        # 5. Puerta frontal abierta a 65° hacia la izquierda (pivote en esquina px - 0.38, -0.48)
        door_ang = R(65)
        dcx = px - 0.38 + math.cos(door_ang) * 0.38
        dcy = -0.48 - math.sin(door_ang) * 0.38
        # Marco exterior de la puerta
        add_box(bm, (dcx, dcy, cz), (0.76, 0.03, 1.96), mat_idx=0, rot_z=door_ang)
        # Rejilla interior perforada
        add_box(bm, (dcx, dcy - 0.01, cz), (0.64, 0.01, 1.84), mat_idx=1, rot_z=door_ang)
        # Cerradura electrónica en el marco
        add_box(bm, (dcx - math.cos(door_ang)*0.32, dcy + math.sin(door_ang)*0.32, cz), (0.08, 0.04, 0.14), mat_idx=3, rot_z=door_ang)
        
        # 6. Mazo vertical de fibra óptica en la derecha
        for fy in [-0.20, 0.0, 0.20]:
            add_cylinder(bm, (px + 0.43, fy, cz), radius=0.022, height=1.90, segments=10, mat_idx=6, axis='Z')

    mat_list = [
        mats['Dark_Gunmetal'], mats['Dark_Titanium'], mats['Hazard_Yellow'],
        mats['Machinery_Brass'], mats['Server_LED_Green'], mats['Server_LED_Amber'],
        mats['Optical_Fiber_Blue']
    ]
    return create_mesh_object("SM_Server_Rack_Reinforced", col, geom, mat_list)

# -------------------------------------------------------------------------
# PROP 23: SM_Captains_Secure_Vault (Caja fuerte acorazada de capitanía)
# -------------------------------------------------------------------------
def build_prop23_captains_vault(col, mats):
    def geom(bm):
        px = 0.0
        # Dimensiones: 100 x 80 x 140 cm
        # 1. Cuerpo principal acorazado de acero naval sobre el pedestal
        cz = 0.85
        # Carcasa exterior (pared trasera, laterales, techo y fondo)
        add_box(bm, (px, 0.36, cz), (1.05, 0.16, 1.38), mat_idx=0) # Trasera Cast_Iron
        add_box(bm, (px - 0.46, 0, cz), (0.13, 0.82, 1.38), mat_idx=0) # Lateral izq
        add_box(bm, (px + 0.46, 0, cz), (0.13, 0.82, 1.38), mat_idx=0) # Lateral der
        add_box(bm, (px, 0, cz + 0.62), (1.05, 0.82, 0.14), mat_idx=0) # Techo
        add_box(bm, (px, 0, cz - 0.62), (1.05, 0.82, 0.14), mat_idx=0) # Base
        
        # Cavidad interior hueca
        add_box(bm, (px, 0.0, cz), (0.80, 0.64, 1.12), mat_idx=1) # Dark_Gunmetal
        
        # 2. Dos estantes interiores blindados con lingotes de oro/platino
        add_box(bm, (px, 0.0, cz - 0.20), (0.78, 0.60, 0.04), mat_idx=0)
        add_box(bm, (px, 0.0, cz + 0.15), (0.78, 0.60, 0.04), mat_idx=0)
        
        # Pilas de lingotes de metales preciosos en ambos estantes (bien visibles hacia el frente)
        for ix, iy in [(-0.20, -0.05), (-0.08, -0.05), (0.04, -0.05), (0.16, -0.05), (-0.14, 0.08), (-0.02, 0.08)]:
            add_box(bm, (px + ix, iy, cz - 0.15), (0.10, 0.06, 0.04), mat_idx=2) # Lingotes estante inf
            add_box(bm, (px + ix, iy, cz - 0.11), (0.09, 0.05, 0.035), mat_idx=2) # 2da capa
            
        for ix in [-0.15, 0.0, 0.15]:
            add_box(bm, (px + ix, -0.05, cz + 0.20), (0.11, 0.06, 0.04), mat_idx=2) # Lingotes estante sup
            
        # 3. Puerta acorazada gruesa abierta a 55° hacia la izquierda (pivote en px - 0.46, -0.41)
        door_ang = R(55)
        dcx = px - 0.46 + math.cos(door_ang) * 0.42
        dcy = -0.41 - math.sin(door_ang) * 0.42
        # Hoja blindada de 10 cm de espesor
        add_box(bm, (dcx, dcy, cz), (0.84, 0.10, 1.22), mat_idx=0, rot_z=door_ang)
        
        # 4. En el canto derecho libre de la puerta: 3 bulones cilíndricos cromados salientes
        for bz in [cz - 0.35, cz, cz + 0.35]:
            bx_edge = dcx + math.cos(door_ang) * 0.43
            by_edge = dcy - math.sin(door_ang) * 0.43
            add_cylinder(bm, (bx_edge, by_edge, bz), radius=0.035, height=0.09, segments=14, mat_idx=3, axis='X') # Bulones cromados
            
        # 5. Volante de combinación analógico circular en latón pulido (en la cara frontal exterior de la puerta)
        vx = dcx - math.sin(door_ang) * 0.09
        vy = dcy - math.cos(door_ang) * 0.09
        add_cylinder(bm, (vx, vy, cz), radius=0.14, height=0.035, segments=18, mat_idx=2, axis='Y') # Dial
        add_cylinder(bm, (vx, vy - 0.02, cz), radius=0.04, height=0.05, segments=14, mat_idx=2, axis='Y') # Eje
        # Tres radios del volante
        for r_ang in [0, 120, 240]:
            r_rad = R(r_ang)
            add_box(bm, (vx + math.cos(r_rad)*0.08, vy - 0.03, cz + math.sin(r_rad)*0.08), (0.02, 0.02, 0.16), mat_idx=2)
            
        # 6. Palanca de cerrojo horizontal en latón
        add_cylinder(bm, (vx + 0.20, vy - 0.02, cz), radius=0.02, height=0.22, segments=10, mat_idx=2, axis='Z')
        
        # 7. Teclado numérico electrónico de respaldo con display ámbar en la puerta
        add_box(bm, (vx - 0.18, vy - 0.02, cz + 0.28), (0.14, 0.025, 0.18), mat_idx=1, rot_z=door_ang)
        add_box(bm, (vx - 0.18, vy - 0.035, cz + 0.32), (0.10, 0.005, 0.05), mat_idx=4, rot_z=door_ang) # Display ámbar
        
        # 8. Marcas de quemadura por soplete térmico en la esquina superior derecha del marco
        add_box(bm, (px + 0.46, -0.41, cz + 0.58), (0.12, 0.02, 0.14), mat_idx=5) # Naranja quemado

    mat_list = [
        mats['Cast_Iron'], mats['Dark_Gunmetal'], mats['Machinery_Brass'],
        mats['Polished_Chrome'], mats['Server_LED_Amber'], mats['HighVis_Orange']
    ]
    return create_mesh_object("SM_Captains_Secure_Vault", col, geom, mat_list)

# -------------------------------------------------------------------------
# PROP 24: SM_Cartographic_Navigation_Table (Mesa cartográfica holográfica)
# -------------------------------------------------------------------------
def build_prop24_navigation_table(col, mats):
    def geom(bm):
        px = 3.0
        # Dimensiones: 160 x 120 x 95 cm
        # 1. Base cónica pesada de bronce náutico y aleación sobre el pedestal
        cz = 0.55
        add_box(bm, (px, 0, 0.26), (1.30, 0.95, 0.20), mat_idx=0) # Dark_Titanium
        add_box(bm, (px, 0, 0.42), (1.10, 0.75, 0.18), mat_idx=1) # Machinery_Brass
        
        # 2. Marco superior de la mesa con molduras de madera noble barnizada
        add_box(bm, (px, 0, 0.68), (1.65, 1.25, 0.16), mat_idx=2) # Hardwood_Polished
        
        # 3. Superficie superior cóncava de vidrio blindado negro antracita
        add_box(bm, (px, 0, 0.77), (1.45, 1.05, 0.02), mat_idx=3) # Dark_Gunmetal
        
        # 4. Proyector holográfico central cóncavo
        add_cylinder(bm, (px, 0, 0.78), radius=0.22, height=0.03, segments=20, mat_idx=1, axis='Z') # Anillo latón
        add_cylinder(bm, (px, 0, 0.795), radius=0.18, height=0.01, segments=20, mat_idx=4, axis='Z') # Lente cian
        
        # 5. Proyección holográfica volumétrica 3D flotante (Nave y rutas en plasma cian y dorado)
        # Anillos orbitales y silueta de crucero espacial en plasma
        add_cylinder(bm, (px, 0, 1.02), radius=0.38, height=0.02, segments=24, mat_idx=4, axis='Z') # Hologram_Cyan
        add_cylinder(bm, (px, 0, 1.14), radius=0.26, height=0.02, segments=20, mat_idx=5, axis='Z') # Hologram_Gold
        # Malla vectorial del casco de la nave
        add_box(bm, (px, 0, 1.08), (0.70, 0.02, 0.02), mat_idx=4)
        add_box(bm, (px, 0, 1.08), (0.02, 0.50, 0.02), mat_idx=4)
        # Baliza cilíndrica de zona de evacuación recomendada
        add_cylinder(bm, (px + 0.18, 0.10, 1.18), radius=0.035, height=0.10, segments=12, mat_idx=5, axis='Z') # Marcador oro
        
        # 6. Cuatro consolas perimétricas táctiles inclinadas
        for cx, cy in [(-0.55, 0), (0.55, 0), (0, -0.42), (0, 0.42)]:
            add_box(bm, (px + cx, cy, 0.79), (0.24, 0.14, 0.015), mat_idx=4) # Pantallas cian
            
        # 7. Apoyamanos perimétrico de latón náutico
        for ey in [-0.58, 0.58]:
            add_cylinder(bm, (px, ey, 0.78), radius=0.015, height=1.60, segments=10, mat_idx=1, axis='X')

    mat_list = [
        mats['Dark_Titanium'], mats['Machinery_Brass'], mats['Hardwood_Polished'],
        mats['Dark_Gunmetal'], mats['Hologram_Cyan'], mats['Hologram_Gold']
    ]
    return create_mesh_object("SM_Cartographic_Navigation_Table", col, geom, mat_list)

# -------------------------------------------------------------------------
# PROP 25: SM_SOS_Transponder_Mast (Mástil baliza SOS de emergencia)
# -------------------------------------------------------------------------
def build_prop25_transponder_mast(col, mats):
    def geom(bm):
        px = 6.0
        # Dimensiones: 60 x 60 x 260 cm
        # 1. Trípode inferior articulado con 3 zapatas magnéticas circulares en el pedestal
        for ang in [0, 120, 240]:
            rad = R(ang)
            foot_x = px + math.cos(rad) * 0.46
            foot_y = math.sin(rad) * 0.46
            # Zapata circular magnética
            add_cylinder(bm, (foot_x, foot_y, 0.20), radius=0.08, height=0.08, segments=14, mat_idx=0, axis='Z') # Dark_Titanium
            # Pata inclinada hacia el centro
            add_cylinder(bm, ((px + foot_x)*0.5, foot_y*0.5, 0.36), radius=0.025, height=0.45, segments=10, mat_idx=1, axis='Z')
            
        # 2. Generador RTG central en la base con aletas de refrigeración
        add_cylinder(bm, (px, 0, 0.48), radius=0.18, height=0.28, segments=18, mat_idx=0, axis='Z') # Cuerpo RTG
        for f_ang in [0, 45, 90, 135, 180, 225, 270, 315]:
            f_rad = R(f_ang)
            add_box(bm, (px + math.cos(f_rad)*0.20, math.sin(f_rad)*0.20, 0.48), (0.06, 0.015, 0.24), mat_idx=2) # Aletas amarillas
            
        # 3. Mástil vertical telescópico de 3 tramos escalonados
        add_cylinder(bm, (px, 0, 0.95), radius=0.065, height=0.70, segments=14, mat_idx=0, axis='Z') # Tramo inferior
        add_cylinder(bm, (px, 0, 1.55), radius=0.048, height=0.60, segments=14, mat_idx=1, axis='Z') # Tramo medio
        add_cylinder(bm, (px, 0, 2.05), radius=0.035, height=0.55, segments=12, mat_idx=0, axis='Z') # Tramo superior
        
        # 4. Plato de antena parabólica superior orientada a 45°
        ant_z = 2.05
        add_cylinder(bm, (px, 0.08, ant_z), radius=0.22, height=0.04, segments=20, mat_idx=1, axis='Y') # Parabólica cromo
        add_cylinder(bm, (px, 0.16, ant_z), radius=0.03, height=0.14, segments=12, mat_idx=3, axis='Y') # Bocina emisora cian
        
        # 5. Baliza estroboscópica de xenón superior con cúpula ámbar
        add_cylinder(bm, (px, 0, 2.38), radius=0.055, height=0.12, segments=16, mat_idx=0, axis='Z') # Base baliza
        add_cylinder(bm, (px, 0, 2.48), radius=0.075, height=0.14, segments=18, mat_idx=4, axis='Z') # Xenon_Flash_Glow
        add_cylinder(bm, (px, 0, 2.56), radius=0.08, height=0.03, segments=18, mat_idx=0, axis='Z') # Caperuza
        
        # 6. Caja de control y palanca manual de activación de socorro
        add_box(bm, (px, -0.12, 1.05), (0.16, 0.10, 0.22), mat_idx=0)
        add_cylinder(bm, (px, -0.18, 1.05), radius=0.015, height=0.12, segments=8, mat_idx=5, axis='Y') # Tirador rojo

    mat_list = [
        mats['Dark_Titanium'], mats['Polished_Chrome'], mats['Hazard_Yellow'],
        mats['Hologram_Cyan'], mats['Xenon_Flash_Glow'], mats['HighVis_Orange']
    ]
    return create_mesh_object("SM_SOS_Transponder_Mast", col, geom, mat_list)

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
    key_data.color = (0.95, 0.98, 1.0)
    key_obj = bpy.data.objects.new("Light_Key_Overhead", key_data)
    key_obj.location = (0, -4.8, 6.4)
    key_obj.rotation_euler = (R(35), 0, 0)
    col.objects.link(key_obj)
    
    rim_data = bpy.data.lights.new(name="Light_Rim_Back", type='AREA')
    rim_data.energy = 880.0
    rim_data.size = 26.0
    rim_data.size_y = 4.0
    rim_data.color = (0.80, 0.92, 1.0)
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
    
    # Luz interna puntual suave para iluminar el interior de la caja fuerte (lingotes)
    vault_l_data = bpy.data.lights.new(name="Light_Vault_Interior", type='POINT')
    vault_l_data.energy = 90.0
    vault_l_data.color = (1.0, 0.88, 0.65)
    vault_l_obj = bpy.data.objects.new("Light_Vault_Interior", vault_l_data)
    vault_l_obj.location = (0.08, -0.05, 0.95)
    col.objects.link(vault_l_obj)

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
    draw.text((40, 46), "CATÁLOGO DE PROPS - LOTE 5 (PROPS 21-25): CAJAS NEGRAS, SERVIDORES Y DATOS", fill=(255, 255, 255), font=font_title)
    
    pills = [
        ("LOTE 5 DE 10", (230, 126, 34)),
        ("DATOS & ALTO VALOR", (155, 89, 182)),
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
    
    pan_path = os.path.join(RENDERS_DIR, "Showcase_Lote5_Props_Panorama.png")
    if os.path.exists(pan_path):
        pan_img = Image.open(pan_path).convert("RGBA")
        pan_w = W - 80
        pan_h = 760
        pan_resized = pan_img.resize((pan_w, pan_h), Image.Resampling.LANCZOS)
        canvas.paste(pan_resized, (40, 110))
        draw.rectangle((40, 110, 40 + pan_w, 110 + pan_h), outline=(45, 52, 65), width=2)
        
    props_cards = [
        ("21. SM_Flight_Data_Recorder_BlackBox", "Showcase_Prop21_Flight_Data_Recorder_BlackBox.png", (230, 126, 34),
         "• Registrador de titanio naranja fluorescente\n• Baliza acústica con destello de xenón\n• Asa abatible y conector multipin\n• Recompensa económica de rescate $50,000"),
         
        ("22. SM_Server_Rack_Reinforced", "Showcase_Prop22_Server_Rack_Reinforced.png", (41, 128, 185),
         "• Rack blindado con puerta abierta a 65°\n• 6 bandejas modulares de discos duros\n• Bandeja interactiva extraída con contactos\n• Matriz de LEDs verdes/ámbar y fibra óptica"),
         
        ("23. SM_Captains_Secure_Vault", "Showcase_Prop23_Captains_Secure_Vault.png", (241, 196, 15),
         "• Caja fuerte naval con puerta abierta a 55°\n• 3 bulones de bloqueo de acero cromado\n• Volante analógico de latón y lingotes\n• Teclado numérico y marcas de soplete"),
         
        ("24. SM_Cartographic_Navigation_Table", "Showcase_Prop24_Cartographic_Navigation_Table.png", (26, 188, 156),
         "• Mesa de mando con bronce y madera noble\n• Proyector holográfico 3D en plasma cian\n• Silueta volumétrica de la nave y rutas\n• 4 cuadrantes táctiles y apoyamanos náutico"),
         
        ("25. SM_SOS_Transponder_Mast", "Showcase_Prop25_SOS_Transponder_Mast.png", (231, 76, 60),
         "• Mástil con trípode y zapatas magnéticas\n• Generador RTG con aletas de refrigeración\n• Plato parabólico a 45° y bocina cian\n• Baliza estroboscópica de xenón superior")
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
            
    master_path = os.path.join(RENDERS_DIR, "Showcase_Lote5_Props_Master.png")
    canvas.save(master_path, "PNG", quality=95)
    print(f"[COMPOSITOR] Lámina Maestra guardada exitosamente en:\n  -> {master_path}")
    
    art_master = os.path.join(ARTIFACT_DIR, "Showcase_Lote5_Props_Master.png")
    shutil.copy2(master_path, art_master)
    print(f"  -> Copiada a artefactos: {art_master}")

# -------------------------------------------------------------------------
# FUNCIÓN PRINCIPAL DE CONSTRUCCIÓN Y RENDER
# -------------------------------------------------------------------------
def main():
    print("==========================================================================")
    print("  ASTRA HAZARD - CONSTRUCTOR DE LOTE 5 DE PROPS (PROPS 21-25: DATOS)      ")
    print("==========================================================================")
    
    scene = reset_scene()
    col_props = create_collection("Lote5_Props_Datos")
    col_studio = create_collection("Studio_Setup")
    
    mats = create_materials()
    
    # 1. Suelo continuo de estudio
    def floor_geom(bm):
        add_box(bm, (0, 0, -0.05), (38.0, 22.0, 0.1), mat_idx=0)
    create_mesh_object("Studio_Floor", col_studio, floor_geom, [mats['Studio_Floor']])
    
    # 2. Construcción de los 5 pedestales
    build_pedestal(col_studio, mats, "Prop21", pos_x=-6.0, width=2.0, depth=1.6)
    build_pedestal(col_studio, mats, "Prop22", pos_x=-3.0, width=2.2, depth=1.8)
    build_pedestal(col_studio, mats, "Prop23", pos_x= 0.0, width=2.2, depth=1.8)
    build_pedestal(col_studio, mats, "Prop24", pos_x= 3.0, width=2.6, depth=1.8)
    build_pedestal(col_studio, mats, "Prop25", pos_x= 6.0, width=2.2, depth=1.8)
    
    # 3. Construcción de los 5 Props de Cajas Negras y Datos
    print("-> Construyendo Prop 21: SM_Flight_Data_Recorder_BlackBox...")
    build_prop21_black_box(col_props, mats)
    
    print("-> Construyendo Prop 22: SM_Server_Rack_Reinforced...")
    build_prop22_server_rack(col_props, mats)
    
    print("-> Construyendo Prop 23: SM_Captains_Secure_Vault...")
    build_prop23_captains_vault(col_props, mats)
    
    print("-> Construyendo Prop 24: SM_Cartographic_Navigation_Table...")
    build_prop24_navigation_table(col_props, mats)
    
    print("-> Construyendo Prop 25: SM_SOS_Transponder_Mast...")
    build_prop25_transponder_mast(col_props, mats)
    
    # 4. Iluminación de estudio
    setup_lighting(col_studio)
    
    # 5. Cámaras con encuadres 3/4 heroicos y sin cortes de FOV
    col_cams = create_collection("Cameras")
    
    # Panorámica general (cubre holgadamente de X=-7.5 a X=+7.5 con 26mm a 12.4m de distancia)
    cam_pan = create_camera_tracking(col_cams, "Cam_Panorama", (0, -12.4, 3.5), (0, 0, 0.85), lens=26.0)
    
    # Close-ups 1080p en perspectiva 3/4
    # Prop 21: Caja negra con baliza de xenón, asa, rótulo y conectores
    cam_p21 = create_camera_tracking(col_cams, "Cam_Prop21", (-6.0 + 0.95, -2.15, 0.88), (-6.0, 0, 0.48), lens=46.0)
    
    # Prop 22: Servidor vertical visto desde la derecha-frente (muestra interior iluminado, bahías y puerta a 65°)
    cam_p22 = create_camera_tracking(col_cams, "Cam_Prop22", (-3.0 + 1.05, -2.65, 1.30), (-3.0, -0.05, 1.25), lens=42.0)
    
    # Prop 23: Caja fuerte vista desde la derecha-frente (muestra volante de latón, 3 bulones y lingotes dorados)
    cam_p23 = create_camera_tracking(col_cams, "Cam_Prop23", ( 0.0 + 1.45, -2.60, 1.05), ( 0.0, -0.05, 0.85), lens=42.0)
    
    # Prop 24: Mesa cartográfica con holograma 3D cian/oro, proyector y molduras
    cam_p24 = create_camera_tracking(col_cams, "Cam_Prop24", ( 3.0 + 1.25, -2.85, 1.45), ( 3.0, 0, 0.90), lens=42.0)
    
    # Prop 25: Mástil SOS completo desde la base hasta la baliza de xenón superior
    cam_p25 = create_camera_tracking(col_cams, "Cam_Prop25", ( 6.0 + 1.85, -4.30, 1.65), ( 6.0, 0, 1.40), lens=32.0)
    
    # 6. Guardar archivo .blend
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_FILE)
    print(f"\n[OK] Escena guardada en: {BLEND_FILE}")
    
    # 7. Renderizado fotográfico de alta resolución
    renders_to_do = [
        ("Showcase_Lote5_Props_Panorama.png", cam_pan, 2560, 900),
        ("Showcase_Prop21_Flight_Data_Recorder_BlackBox.png", cam_p21, 1920, 1080),
        ("Showcase_Prop22_Server_Rack_Reinforced.png", cam_p22, 1920, 1080),
        ("Showcase_Prop23_Captains_Secure_Vault.png", cam_p23, 1920, 1080),
        ("Showcase_Prop24_Cartographic_Navigation_Table.png", cam_p24, 1920, 1080),
        ("Showcase_Prop25_SOS_Transponder_Mast.png", cam_p25, 1920, 1080),
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
    print("  [EXITO] LOTE 5 DE PROPS (DATOS & ALTO VALOR) COMPLETADO AL 100%          ")
    print("==========================================================================")

if __name__ == "__main__":
    main()

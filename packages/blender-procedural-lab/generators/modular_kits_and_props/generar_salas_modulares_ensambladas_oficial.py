# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Generador Maestro de Salas Modulares Ensambladas (Level Assembly Dioramas) - Astra Hazard
# Ensamblado de Entornos Completos Jugables Tier 1, 2 y 3 usando los 26 Activos Modulares Oficiales
# Blender 5.2 LTS - Shaders Stylized PBR, Cel-Shading, Iluminación de Estudio y Freestyle Ink Lineart

import bpy
import bmesh
import math
import os
import sys
import shutil
from mathutils import Vector, Euler
from PIL import Image, ImageDraw, ImageFont

# Agregar directorio actual al path para importar el catálogo modular oficial
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.append(SCRIPT_DIR)

import generar_catalogo_activos_modulares_v6 as cat

PROJECT_ROOT = r"F:\Dev\Game"
RENDERS_DIR = os.path.join(PROJECT_ROOT, "Art", "Renders")
ARTIFACT_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\b59ff04f-3c21-4ee5-94b0-8e8f899f8923"
BLEND_FILE = os.path.join(PROJECT_ROOT, "Art", "Blender", "Salas_Modulares_Ensambladas_Oficial.blend")

os.makedirs(RENDERS_DIR, exist_ok=True)
os.makedirs(ARTIFACT_DIR, exist_ok=True)

R = math.radians

def reset_assembly_scene():
    """Reinicia la escena y configura motor EEVEE con parámetros cinematográficos y Freestyle."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if not bpy.data.scenes:
        bpy.data.scenes.new("Scene")
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.film_transparent = False
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'High Contrast'
    
    # Entorno cósmico de estudio con iluminación ambiental tenue
    world = bpy.data.worlds.new("World_Assembly")
    scene.world = world
    world.use_nodes = True
    wnodes = world.node_tree.nodes
    wlinks = world.node_tree.links
    wnodes.clear()
    
    w_out = wnodes.new(type='ShaderNodeOutputWorld')
    w_bg = wnodes.new(type='ShaderNodeBackground')
    w_bg.inputs['Color'].default_value = (0.010, 0.012, 0.018, 1.0)
    w_bg.inputs['Strength'].default_value = 0.35
    wlinks.new(w_bg.outputs['Background'], w_out.inputs['Surface'])
    
    # Freestyle Lineart (Línea de tinta de cómic estilizada)
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
    linestyle.thickness = 1.6
    ls.linestyle = linestyle
    
    return scene

def point_camera_at(cam_obj, target_pos):
    """Orienta suavemente la cámara o luz hacia un vector de objetivo 3D."""
    direction = Vector(target_pos) - cam_obj.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()

def create_studio_area_light(col, name, location, target, size_x=8.0, size_y=6.0, energy=500.0, color=(1.0, 1.0, 1.0)):
    """Crea una luz de área de estudio difusa (softbox) eliminando conos duros de corte y sombras quemadas."""
    ldata = bpy.data.lights.new(name=name, type='AREA')
    ldata.shape = 'RECTANGLE'
    ldata.size = size_x
    ldata.size_y = size_y
    ldata.energy = energy
    ldata.color = color
    lobj = bpy.data.objects.new(name, ldata)
    lobj.location = Vector(location)
    point_camera_at(lobj, target)
    col.objects.link(lobj)
    return lobj

def update_material_properties(mat, base_color=None, roughness=None, metallic=None, emissive_strength=None, emissive_color=None):
    """Ajusta propiedades PBR de un material existente directamente en su nodo Principled BSDF."""
    if not mat or not mat.use_nodes:
        return
    bsdf = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if not bsdf:
        return
    if base_color:
        bsdf.inputs['Base Color'].default_value = (*base_color, 1.0)
    if roughness is not None:
        bsdf.inputs['Roughness'].default_value = roughness
    if metallic is not None:
        bsdf.inputs['Metallic'].default_value = metallic
    if emissive_strength is not None:
        bsdf.inputs['Emission Strength'].default_value = emissive_strength
    if emissive_color is not None:
        bsdf.inputs['Emission Color'].default_value = emissive_color

# ==============================================================================
# CONSTRUCTORES DE ELEMENTOS ESTRUCTURALES Y ARQUITECTÓNICOS DE SALA
# ==============================================================================
def init_assembly_materials():
    """Inicializa materiales específicos de la arquitectura de salas con balances visuales PBR."""
    cat.init_all_materials()
    
    # Suelo exterior mate (erradica reflejos especulares circulares en el panorama)
    update_material_properties(cat.MATS.get("Mat_Studio_Floor"), base_color=(0.012, 0.014, 0.018), roughness=0.98, metallic=0.0)
    
    # Muros exclusivos de la refinería de plasma (acero militar oscuro sin manómetros repetidos)
    cat.get_stylized_material("Mat_Plasma_Chamber_Wall", base_color=(0.14, 0.16, 0.20), roughness=0.45, metallic=0.88,
                              tex_pack="T_Steel_Plates", tex_mix=0.35)
    cat.get_stylized_material("Mat_Chamber_Floor_Dark", base_color=(0.08, 0.09, 0.12), roughness=0.35, metallic=0.75,
                              tex_pack="T_Grating_Walkway", tex_mix=0.40)
    
    # Charco químico de lodo tóxico brillante (mojado de alto brillo especular, sin autoiluminación plana)
    cat.get_stylized_material("Mat_Acid_Spill_Puddle", base_color=(0.02, 0.32, 0.08), roughness=0.03, metallic=0.0,
                              emissive_strength=0.0)
    
    # Ajuste de ácido fluorescente en cuba
    update_material_properties(cat.MATS.get("Mat_Toxic_Acid"), base_color=(0.04, 0.82, 0.14), roughness=0.10,
                               emissive_strength=0.85, emissive_color=(0.05, 0.90, 0.16, 1.0))
    
    # Pantalla CRT Terminal de Plasma (Fósforo verde de osciloscopio y radar de alta visibilidad)
    cat.get_stylized_material("Mat_CRT_Radar_Screen", base_color=(0.02, 0.24, 0.10), roughness=0.12, metallic=0.0,
                              emissive_color=(0.06, 0.96, 0.22, 1.0), emissive_strength=2.2)
    
    # Vista Astronómica de Saturno (Estética Art Déco monumental, tonos áureos y ocres cálidos)
    cat.get_stylized_material("Mat_Space_Stars", base_color=(0.006, 0.009, 0.022), roughness=0.95, metallic=0.0)
    cat.get_stylized_material("Mat_Saturn_Atmosphere", base_color=(0.86, 0.66, 0.36), roughness=0.60, metallic=0.0,
                              emissive_color=(0.86, 0.66, 0.36, 1.0), emissive_strength=0.08)
    cat.get_stylized_material("Mat_Saturn_Bands", base_color=(0.70, 0.48, 0.24), roughness=0.65, metallic=0.0,
                              emissive_color=(0.70, 0.48, 0.24, 1.0), emissive_strength=0.05)
    cat.get_stylized_material("Mat_Saturn_Rings_Clean", base_color=(0.84, 0.70, 0.44), roughness=0.55, metallic=0.05,
                              emissive_color=(0.84, 0.70, 0.44, 1.0), emissive_strength=0.10)
    cat.get_stylized_material("Mat_Saturn_Rings_Inner", base_color=(0.68, 0.52, 0.30), roughness=0.60, metallic=0.05,
                              emissive_color=(0.68, 0.52, 0.30, 1.0), emissive_strength=0.06)

def build_saturn_ring_arc(name, r_in, r_out, aspect, tilt, y_pos, theta_start, theta_end, segments=48, mat=None):
    """
    Crea un arco de anillo elíptico 2.5D plano en el plano del ventanal.
    Permite ordenamiento de profundidad perfecto (el arco posterior queda tras Saturno y el frontal por delante).
    """
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bm = bmesh.new()
    cos_t = math.cos(tilt)
    sin_t = math.sin(tilt)
    
    v_in = []
    v_out = []
    for i in range(segments + 1):
        t = theta_start + (theta_end - theta_start) * i / segments
        u_in = r_in * math.cos(t)
        v_in_val = r_in * aspect * math.sin(t)
        u_out = r_out * math.cos(t)
        v_out_val = r_out * aspect * math.sin(t)
        
        # Rotación en el plano X-Z de la ventana
        x_in = u_in * cos_t - v_in_val * sin_t
        z_in = u_in * sin_t + v_in_val * cos_t
        x_out = u_out * cos_t - v_out_val * sin_t
        z_out = u_out * sin_t + v_out_val * cos_t
        
        v_in.append(bm.verts.new((x_in, y_pos, z_in)))
        v_out.append(bm.verts.new((x_out, y_pos, z_out)))
        
    bm.verts.ensure_lookup_table()
    for i in range(segments):
        bm.faces.new((v_in[i], v_out[i], v_out[i+1], v_in[i+1]))
        
    bm.to_mesh(mesh)
    bm.free()
    if mat:
        mesh.materials.append(mat)
    return obj

def build_room_shell(col, name, center_x, floor_mat, wall_mat, size=(8.6, 8.6, 4.6), title="SALA"):
    """Construye el caparazón arquitectónico diorama con peana de exhibición y placa de latón."""
    sx, sy, sz = size
    
    # 0. Peana de exhibición del diorama (Plinto biselado)
    plinth = cat.create_box(f"{name}_Plinth", size=(sx + 0.6, sy + 0.6, 0.35), mat=cat.MATS["Mat_Pedestal_Base"], bevel=True, bevel_w=0.04)
    plinth.location = (center_x, 0, -0.175)
    col.objects.link(plinth)
    
    # Placa frontal de latón grabada en la peana
    plaque = cat.create_box(f"{name}_Plaque", size=(3.2, 0.06, 0.18), mat=cat.MATS["Mat_Plaque_Brass"], bevel=True, bevel_w=0.01)
    plaque.location = (center_x, -sy/2 - 0.28, -0.16)
    col.objects.link(plaque)
    
    # Suelo base estructural
    floor = cat.create_box(f"{name}_Floor", size=(sx, sy, 0.24), mat=floor_mat, bevel=True, bevel_w=0.03)
    floor.location = (center_x, 0, 0.12)
    col.objects.link(floor)
    
    # Zócalo perimetral elevado de acero oscuro
    zocalo_rear = cat.create_box(f"{name}_Zocalo_Rear", size=(sx + 0.1, 0.22, 0.20), mat=cat.MATS["Mat_Gunmetal"], bevel=True)
    zocalo_rear.location = (center_x, sy/2 - 0.11, 0.34)
    col.objects.link(zocalo_rear)
    
    # Pared posterior (Mamparo)
    wall_rear = cat.create_box(f"{name}_Wall_Rear", size=(sx, 0.22, sz), mat=wall_mat, bevel=True, bevel_w=0.02)
    wall_rear.location = (center_x, sy/2 - 0.11, sz/2 + 0.24)
    col.objects.link(wall_rear)
    
    # Cornisa superior posterior
    cornice_rear = cat.create_box(f"{name}_Cornice_Rear", size=(sx + 0.2, 0.35, 0.25), mat=cat.MATS["Mat_Gunmetal"], bevel=True)
    cornice_rear.location = (center_x, sy/2 - 0.15, sz + 0.24)
    col.objects.link(cornice_rear)
    
    # Pared lateral izquierda (Mamparo)
    wall_left = cat.create_box(f"{name}_Wall_Left", size=(0.22, sy, sz), mat=wall_mat, bevel=True, bevel_w=0.02)
    wall_left.location = (center_x - sx/2 + 0.11, 0, sz/2 + 0.24)
    col.objects.link(wall_left)
    
    # Cornisa superior lateral izquierda
    cornice_left = cat.create_box(f"{name}_Cornice_Left", size=(0.35, sy + 0.2, 0.25), mat=cat.MATS["Mat_Gunmetal"], bevel=True)
    cornice_left.location = (center_x - sx/2 + 0.15, 0, sz + 0.24)
    col.objects.link(cornice_left)
    
    # Columna esquinera gantry
    corner_col = cat.create_box(f"{name}_Corner_Pillar", size=(0.45, 0.45, sz + 0.2), mat=cat.MATS["Mat_Gunmetal"], bevel=True)
    corner_col.location = (center_x - sx/2 + 0.22, sy/2 - 0.22, (sz + 0.2)/2 + 0.24)
    col.objects.link(corner_col)
    
    return floor

def build_hazard_border(col, name, center_x, size=(8.6, 8.6)):
    """Añade franjas de borde de seguridad hazard en el frontal y laterales abiertos."""
    sx, sy = size
    # Franja frontal hazard
    strip_front = cat.create_box(f"{name}_Hazard_Front", size=(sx, 0.25, 0.03), mat=cat.MATS["Mat_Hazard_Yellow"], bevel=False)
    strip_front.location = (center_x, -sy/2 + 0.125, 0.255)
    col.objects.link(strip_front)
    
    # Franja lateral derecha hazard
    strip_right = cat.create_box(f"{name}_Hazard_Right", size=(0.25, sy, 0.03), mat=cat.MATS["Mat_Hazard_Yellow"], bevel=False)
    strip_right.location = (center_x + sx/2 - 0.125, 0, 0.255)
    col.objects.link(strip_right)

# ==============================================================================
# SALA 1: BAHÍA DE CARGA Y PELIGRO QUÍMICO (TIER 1 - CARGUERO INDUSTRIAL)
# ==============================================================================
def assemble_room_chemical_freighter(col, center_x=-14.0):
    print(f"[ENSAMBLADO] Construyendo Sala 1: Bahía de Carga Química (X={center_x})...")
    
    # 1. Caparazón de la sala con peana
    build_room_shell(col, "Room_Chem", center_x, 
                     floor_mat=cat.MATS["Mat_Grate_Steel"], 
                     wall_mat=cat.MATS["Mat_Rust_Hull"], 
                     size=(8.6, 8.6, 4.6),
                     title="TIER 1 // BAHIA QUIMICA")
    build_hazard_border(col, "Room_Chem", center_x, size=(8.6, 8.6))
    
    # 2. Cuba de Ácido Radiactivo (Ubicada en el cuadrante medio-izquierdo para encuadre 3/4)
    cat.build_acid_vat(col, loc=(center_x - 1.2, -0.6, 0.24), rot=(0, 0, 15))
    
    # 3. Contenedores Espaciales TEU apilados de forma realista en el cuadrante posterior derecho
    cat.build_container_teu(col, loc=(center_x + 2.0, 1.8, 1.15), rot=(0, 0, -10))
    cat.build_container_teu(col, loc=(center_x + 2.1, 1.7, 3.0), rot=(0, 0, 8))
    
    # 4. Brazo Grúa Pescante Articulado con Celosía y Pinza
    cat.build_cargo_crane_arm(col, loc=(center_x - 2.6, 2.2, 0.24), rot=(0, 0, -38))
    
    # 5. Pasarela Modular Elevada de Rejilla con barandilla tubular
    cat.build_modular_gantry(col, loc=(center_x - 3.2, -0.4, 2.2), rot=(0, 0, 90))
    cat.build_modular_gantry(col, loc=(center_x + 1.8, -2.0, 0.24), rot=(0, 0, 0))
    
    # 6. Columnas Estructurales Pesadas en Perfil I con Placas de Pernos
    cat.build_heavy_i_beam(col, loc=(center_x - 3.8, 3.8, 0.24), rot=(0, 0, 0))
    cat.build_heavy_i_beam(col, loc=(center_x + 3.8, 3.8, 0.24), rot=(0, 0, 0))
    cat.build_heavy_i_beam(col, loc=(center_x - 3.8, -1.8, 0.24), rot=(0, 0, 90))
    cat.build_heavy_i_beam(col, loc=(center_x + 3.8, -1.8, 0.24), rot=(0, 0, 90))
    
    # Viga I horizontal transversal gantry en el techo
    beam_h = cat.create_box("Gantry_Cross_Beam", size=(7.6, 0.35, 0.35), mat=cat.MATS["Mat_Gunmetal"], bevel=True)
    beam_h.location = (center_x, 3.8, 3.9)
    col.objects.link(beam_h)
    
    # 7. Batería de Barriles Químicos Tóxicos con derrame líquido realista
    barrel_parts = []
    barrel_positions = [(-0.35, -0.2, 0.45), (0.35, -0.2, 0.45), (0.0, 0.3, 0.45)]
    for i, b_pos in enumerate(barrel_positions):
        b_body = cat.create_cylinder(f"Chem_Barrel_{i}", radius=0.30, depth=0.9, segments=20, mat=cat.MATS["Mat_Pipe_Olive"])
        b_body.location = b_pos
        barrel_parts.append(b_body)
        for z_rim in [-0.3, 0.0, 0.3]:
            rim = cat.create_cylinder(f"Chem_Rim_{i}_{z_rim}", radius=0.32, depth=0.05, segments=20, mat=cat.MATS["Mat_Hazard_Yellow"])
            rim.location = (b_pos[0], b_pos[1], b_pos[2] + z_rim)
            barrel_parts.append(rim)
    spill = cat.create_cylinder("Chem_Acid_Spill", radius=0.90, depth=0.012, segments=24, mat=cat.MATS["Mat_Acid_Spill_Puddle"], bevel=False)
    spill.location = (0, 0, 0.01)
    barrel_parts.append(spill)
    cat.assemble_asset("SM_Bateria_Barriles_Toxicos_Room", barrel_parts, col, location=(center_x - 2.4, -2.6, 0.24), rotation=(0, 0, 20))
    
    # 8. Racor Triple de Manómetros Analógicos de Latón en Mamparo
    cat.build_triple_gauge_cluster(col, loc=(center_x - 0.4, 4.05, 2.4), rot=(0, 0, 0))
    
    # 9. Tuberías industriales de ácido y vapor en la pared posterior
    pipe_main = cat.create_cylinder("Chem_Wall_Pipe", radius=0.12, depth=7.4, segments=20, mat=cat.MATS["Mat_Pipe_Olive"])
    pipe_main.rotation_euler = Euler((0, R(90), 0))
    pipe_main.location = (center_x, 4.0, 2.9)
    col.objects.link(pipe_main)
    
    valve = cat.create_cylinder("Chem_Pipe_Valve", radius=0.22, depth=0.06, segments=16, mat=cat.MATS["Mat_Valve_Red"])
    valve.rotation_euler = Euler((R(90), 0, 0))
    valve.location = (center_x + 1.2, 3.88, 2.9)
    col.objects.link(valve)
    
    sign_mesh = cat.create_box("Chem_Warning_Sign", size=(1.8, 0.04, 0.6), mat=cat.MATS["Mat_Hazard_Yellow"])
    sign_mesh.location = (center_x + 1.8, 4.15, 3.7)
    col.objects.link(sign_mesh)
    
    # 10. Iluminación diegética de la sala mediante luces de área de estudio suaves
    # Luz Clave difusa frontal-derecha (softbox 8.5x6m para bañar armónicamente el espacio)
    create_studio_area_light(col, "Chem_Key_Area", location=(center_x + 3.6, -6.5, 6.0), 
                             target=(center_x, 0.4, 2.0), size_x=8.5, size_y=6.0, energy=560.0, color=(1.0, 0.90, 0.70))
    
    # Luz de Relleno difusa lateral-izquierda (softbox 7.0x5.0m eliminando sombras negras de la pared)
    create_studio_area_light(col, "Chem_Fill_Area", location=(center_x - 4.5, -4.5, 5.0), 
                             target=(center_x, 0.4, 2.0), size_x=7.0, size_y=5.0, energy=300.0, color=(0.70, 0.82, 0.95))
    
    # Foco verde radiactivo ascendente desde la cuba de ácido (sin sombras oclusivas sobre paredes)
    l_acid = bpy.data.lights.new(name="Chem_Acid_Glow", type='POINT')
    l_acid.energy = 220.0
    l_acid.color = (0.08, 1.0, 0.18)
    l_acid.use_shadow = False
    l_acid_obj = bpy.data.objects.new("Chem_Acid_Glow", l_acid)
    l_acid_obj.location = (center_x - 1.2, -0.6, 1.3)
    col.objects.link(l_acid_obj)

# ==============================================================================
# SALA 2: GRAN SALÓN VIP Y OBSERVATORIO "CELESTIA" (TIER 2 - CRUCERO ART DÉCO)
# ==============================================================================
def build_clean_artdeco_wall_boiserie(col, loc=(0,0,0), rot=(0,0,0)):
    """Construye panel boiserie de pared exclusivamente arquitectónico (sin alfombras de showroom adyacentes)."""
    parts = []
    panel = cat.create_box("Wood_Panel", size=(2.6, 0.12, 2.9), mat=cat.MATS["Mat_Mahogany_Wood"])
    panel.location = (0, 0, 1.45)
    parts.append(panel)
    for mx in [-0.75, 0.75]:
        mould = cat.create_box(f"Gold_Moulding_{mx}", size=(0.70, 0.04, 1.9), mat=cat.MATS["Mat_ArtDeco_Gold"])
        mould.location = (mx, -0.07, 1.45)
        parts.append(mould)
        center_gem = cat.create_box(f"Gold_Diamond_{mx}", size=(0.22, 0.05, 0.22), mat=cat.MATS["Mat_ArtDeco_Gold"])
        center_gem.rotation_euler = Euler((0, R(45), 0))
        center_gem.location = (mx, -0.09, 1.45)
        parts.append(center_gem)
    return cat.assemble_asset("SM_Panel_Boiserie_ArtDeco", parts, col, loc, rot)

def assemble_room_luxury_celestia(col, center_x=0.0):
    print(f"[ENSAMBLADO] Construyendo Sala 2: Salón VIP Celestia (X={center_x})...")
    
    # 1. Caparazón de la sala (Mármol Carrara y madera noble) con peana
    build_room_shell(col, "Room_Lux", center_x, 
                     floor_mat=cat.MATS["Mat_Carrara_Marble"], 
                     wall_mat=cat.MATS["Mat_Mahogany_Wood"], 
                     size=(8.6, 8.6, 4.8),
                     title="TIER 2 // CRUCERO CELESTIA")
    
    # Moldura perimetral dorada en el borde del suelo
    lux_border = cat.create_box("Lux_Gold_Border", size=(8.6, 0.18, 0.04), mat=cat.MATS["Mat_ArtDeco_Gold"])
    lux_border.location = (center_x, -4.21, 0.25)
    col.objects.link(lux_border)
    
    # 2. Gran Alfombra Palaciega Art Déco Unificada (Sin tapetes superpuestos en laterales)
    carpet_grand = cat.create_box("Carpet_Grand_Lounge", size=(6.8, 5.8, 0.03), mat=cat.MATS["Mat_Burgundy_Carpet"])
    carpet_grand.location = (center_x, 0.4, 0.255)
    col.objects.link(carpet_grand)
    
    carpet_outer_gold = cat.create_box("Carpet_Outer_Gold", size=(6.86, 5.86, 0.01), mat=cat.MATS["Mat_ArtDeco_Gold"])
    carpet_outer_gold.location = (center_x, 0.4, 0.252)
    col.objects.link(carpet_outer_gold)
    
    for dx in [-2.4, 2.4]:
        strip_y = cat.create_box(f"Carpet_Inlay_Y_{dx}", size=(0.10, 4.4, 0.01), mat=cat.MATS["Mat_ArtDeco_Gold"])
        strip_y.location = (center_x + dx, 0.4, 0.272)
        col.objects.link(strip_y)
    for dy in [-2.0, 2.0]:
        strip_x = cat.create_box(f"Carpet_Inlay_X_{dy}", size=(4.9, 0.10, 0.01), mat=cat.MATS["Mat_ArtDeco_Gold"])
        strip_x.location = (center_x, 0.4 + dy, 0.272)
        col.objects.link(strip_x)
        
    # 3. Ventanal Arqueado Monumental al Cosmos con Saturno 2.5D Perfeccionado
    win_group = []
    
    # Fondo del espacio exterior profundo
    outer_arch = cat.create_cylinder("Lux_Window_Backdrop", radius=2.3, depth=0.04, segments=48, mat=cat.MATS["Mat_Space_Stars"])
    outer_arch.rotation_euler = Euler((R(90), 0, 0))
    outer_arch.location = (0, 0.0, 2.3)
    win_group.append(outer_arch)
    
    # Planeta Saturno: Esfera/disco gas giant en el plano cósmico (Local Y = -0.018)
    sat_cx, sat_cz = -0.42, 2.45
    sat_rad = 0.68
    saturn_body = cat.create_cylinder("Lux_Saturn_Body", radius=sat_rad, depth=0.02, segments=48, mat=cat.MATS["Mat_Saturn_Atmosphere"])
    saturn_body.rotation_euler = Euler((R(90), 0, 0))
    saturn_body.location = (sat_cx, -0.018, sat_cz)
    win_group.append(saturn_body)
    
    for b_offset in [-0.15, 0.12]:
        band = cat.create_cylinder(f"Lux_Saturn_Band_{b_offset}", radius=sat_rad * 1.002, depth=0.022, segments=48, mat=cat.MATS["Mat_Saturn_Bands"])
        band.rotation_euler = Euler((R(90), 0, 0))
        band.location = (sat_cx, -0.019, sat_cz + b_offset)
        win_group.append(band)
    
    # Anillos elípticos auténticos planos 2.5D con ordenamiento de profundidad y división Cassini
    ring_tilt = R(24)
    ring_aspect = 0.34
    
    saturn_ring_back_b = build_saturn_ring_arc("Ring_Back_B", r_in=0.88, r_out=1.24, aspect=ring_aspect, 
                                              tilt=ring_tilt, y_pos=-0.012, theta_start=0, theta_end=math.pi, 
                                              segments=48, mat=cat.MATS["Mat_Saturn_Rings_Clean"])
    saturn_ring_back_b.location = (sat_cx, 0, sat_cz)
    win_group.append(saturn_ring_back_b)
    
    saturn_ring_back_a = build_saturn_ring_arc("Ring_Back_A", r_in=1.30, r_out=1.56, aspect=ring_aspect, 
                                              tilt=ring_tilt, y_pos=-0.012, theta_start=0, theta_end=math.pi, 
                                              segments=48, mat=cat.MATS["Mat_Saturn_Rings_Inner"])
    saturn_ring_back_a.location = (sat_cx, 0, sat_cz)
    win_group.append(saturn_ring_back_a)
    
    saturn_ring_front_b = build_saturn_ring_arc("Ring_Front_B", r_in=0.88, r_out=1.24, aspect=ring_aspect, 
                                               tilt=ring_tilt, y_pos=-0.024, theta_start=math.pi, theta_end=2*math.pi, 
                                               segments=48, mat=cat.MATS["Mat_Saturn_Rings_Clean"])
    saturn_ring_front_b.location = (sat_cx, 0, sat_cz)
    win_group.append(saturn_ring_front_b)
    
    saturn_ring_front_a = build_saturn_ring_arc("Ring_Front_A", r_in=1.30, r_out=1.56, aspect=ring_aspect, 
                                               tilt=ring_tilt, y_pos=-0.024, theta_start=math.pi, theta_end=2*math.pi, 
                                               segments=48, mat=cat.MATS["Mat_Saturn_Rings_Inner"])
    saturn_ring_front_a.location = (sat_cx, 0, sat_cz)
    win_group.append(saturn_ring_front_a)
    
    # Nervadura monumental de oro Art Déco del ventanal
    arch_outer_ring = cat.create_torus("Lux_Arch_Rib_Outer", major_r=2.3, minor_r=0.08, major_seg=48, minor_seg=14, mat=cat.MATS["Mat_ArtDeco_Gold"])
    arch_outer_ring.rotation_euler = Euler((R(90), 0, 0))
    arch_outer_ring.location = (0, -0.045, 2.3)
    win_group.append(arch_outer_ring)
    
    arch_inner_ring = cat.create_torus("Lux_Arch_Rib_Inner", major_r=2.05, minor_r=0.05, major_seg=48, minor_seg=12, mat=cat.MATS["Mat_ArtDeco_Gold"])
    arch_inner_ring.rotation_euler = Euler((R(90), 0, 0))
    arch_inner_ring.location = (0, -0.045, 2.3)
    win_group.append(arch_inner_ring)
    
    for m_ang in [0, 45, 90, 135]:
        mullion = cat.create_box(f"Lux_Mullion_{m_ang}", size=(0.04, 0.04, 4.4), mat=cat.MATS["Mat_ArtDeco_Gold"])
        mullion.rotation_euler = Euler((0, R(m_ang), 0))
        mullion.location = (0, -0.040, 2.3)
        win_group.append(mullion)
    
    cat.assemble_asset("SM_Ventanal_Monumental_Celestia", win_group, col, location=(center_x, 4.08, 0.24))
    
    # 4. Paneles Boiserie limpios en mamparo posterior y lateral izquierdo
    build_clean_artdeco_wall_boiserie(col, loc=(center_x - 3.2, 4.05, 0.24), rot=(0, 0, 0))
    build_clean_artdeco_wall_boiserie(col, loc=(center_x + 3.2, 4.05, 0.24), rot=(0, 0, 0))
    build_clean_artdeco_wall_boiserie(col, loc=(center_x - 4.15, 0.2, 0.24), rot=(0, 0, 90))
    cat.build_sunburst_mirror(col, loc=(center_x - 4.0, 0.2, 2.3), rot=(0, 0, 90))
    
    # 5. Mobiliario Central de Lujo (Lounge VIP de Terciopelo Burdeos Capitoné)
    cat.build_artdeco_sofa(col, loc=(center_x, 1.4, 0.26), rot=(0, 0, 0))
    cat.build_artdeco_marble_table(col, loc=(center_x, -0.2, 0.26), rot=(0, 0, 0))
    cat.build_artdeco_armchair(col, loc=(center_x - 1.8, -0.4, 0.26), rot=(0, 0, 32))
    cat.build_artdeco_armchair(col, loc=(center_x + 1.8, -0.4, 0.26), rot=(0, 0, -32))
    
    # 6. Iluminación Diegética Art Déco
    cat.build_artdeco_chandelier(col, loc=(center_x, 0.4, 4.0), rot=(0, 0, 0))
    cat.build_artdeco_floor_lamp(col, loc=(center_x - 2.8, 1.6, 0.26), rot=(0, 0, 0))
    cat.build_artdeco_floor_lamp(col, loc=(center_x + 2.8, 1.6, 0.26), rot=(0, 0, 0))
    
    # 7. Luces cinematográficas de sala mediante softboxes difusos
    l_chan = bpy.data.lights.new(name="Lux_Chandelier_Light", type='POINT')
    l_chan.energy = 440.0
    l_chan.color = (1.0, 0.88, 0.65)
    l_chan_obj = bpy.data.objects.new("Lux_Chandelier_Light", l_chan)
    l_chan_obj.location = (center_x, 0.4, 3.4)
    col.objects.link(l_chan_obj)
    
    create_studio_area_light(col, "Lux_Key_Area", location=(center_x + 3.6, -6.0, 5.8), 
                             target=(center_x, 0.4, 1.8), size_x=8.5, size_y=6.0, energy=460.0, color=(1.0, 0.94, 0.82))
    
    create_studio_area_light(col, "Lux_Fill_Area", location=(center_x - 4.2, -4.8, 5.0), 
                             target=(center_x, 0.4, 1.8), size_x=7.0, size_y=5.0, energy=240.0, color=(0.95, 0.90, 0.82))

# ==============================================================================
# SALA 3: CÁMARA DEL REACTOR TOKAMAK Y REFINERÍA DE PLASMA (TIER 3 - ALTA TENSIÓN)
# ==============================================================================
def assemble_room_plasma_refinery(col, center_x=14.0):
    print(f"[ENSAMBLADO] Construyendo Sala 3: Cámara del Reactor de Plasma (X={center_x})...")
    
    # 1. Caparazón de la sala (Acero de blindaje de alta tensión oscuro sin manómetros repetidos) con peana
    build_room_shell(col, "Room_Plasma", center_x, 
                     floor_mat=cat.MATS["Mat_Chamber_Floor_Dark"], 
                     wall_mat=cat.MATS["Mat_Plasma_Chamber_Wall"], 
                     size=(8.6, 8.6, 4.8),
                     title="TIER 3 // REFINERIA PLASMA")
    build_hazard_border(col, "Room_Plasma", center_x, size=(8.6, 8.6))
    
    # 2. Pozo Central de Confinamiento Magnético
    pit_rim = cat.create_cylinder("Pit_Rim", radius=2.6, depth=0.28, segments=36, mat=cat.MATS["Mat_Gunmetal"])
    pit_rim.location = (center_x, 0.2, 0.26)
    col.objects.link(pit_rim)
    
    pit_inner = cat.create_cylinder("Pit_Inner", radius=2.3, depth=0.35, segments=36, mat=cat.MATS["Mat_Hazard_Yellow"], bevel=False)
    pit_inner.location = (center_x, 0.2, 0.22)
    col.objects.link(pit_inner)
    
    # 3. Reactor Toroidal Tokamak de Plasma en el Corazón del Pozo (con Toro Gunmetal y Núcleo Cian)
    reactor_parts = []
    outer_torus = cat.create_torus("Outer_Torus_Room", major_r=1.35, minor_r=0.28, major_seg=36, minor_seg=16, mat=cat.MATS["Mat_Gunmetal"])
    outer_torus.rotation_euler = Euler((R(90), 0, 0))
    reactor_parts.append(outer_torus)
    for i in range(6):
        ang = R(i * 60)
        clamp = cat.create_box(f"Clamp_Room_{i}", size=(0.35, 0.65, 0.40), mat=cat.MATS["Mat_Hazard_Yellow"])
        clamp.location = (1.35 * math.cos(ang), 0, 1.35 * math.sin(ang))
        clamp.rotation_euler = Euler((0, -ang, 0))
        reactor_parts.append(clamp)
    plasma_ring = cat.create_torus("Plasma_Ring_Room", major_r=1.0, minor_r=0.18, major_seg=32, minor_seg=12, mat=cat.MATS["Mat_Plasma_CyanCore"])
    plasma_ring.rotation_euler = Euler((R(90), 0, 0))
    reactor_parts.append(plasma_ring)
    flare = cat.create_cylinder("Central_Singularity_Room", radius=0.42, depth=0.08, segments=24, mat=cat.MATS["Mat_Plasma_CyanCore"], bevel=False)
    flare.rotation_euler = Euler((R(90), 0, 0))
    reactor_parts.append(flare)
    for i in range(4):
        ang = R(i * 90 + 25)
        arc = cat.create_box(f"LightningArc_Room_{i}", size=(0.04, 0.04, 0.9), mat=cat.MATS["Mat_Plasma_WhiteFlare"])
        arc.rotation_euler = Euler((R(90), ang, R(15)))
        reactor_parts.append(arc)
    cat.assemble_asset("SM_Generador_Toroidal_Plasma_Room", reactor_parts, col, location=(center_x, 0.2, 1.9), rotation=(0, 0, 15))
    
    # 4. Pasarela Modular Curva de Inspección volando sobre el foso con barandilla tubular
    cat.build_curved_catwalk_module(col, loc=(center_x - 1.4, -1.2, 0.26), rot=(0, 0, 25))
    
    # 5. Puesto de Control y Consola Terminal CRT de Plasma (Encarada a la cámara con CRT activo)
    con_parts = []
    con_desk = cat.create_box("Console_Desk_Room", size=(1.2, 0.75, 0.82), mat=cat.MATS["Mat_Plasma_Chamber_Wall"])
    con_desk.location = (0, 0, 0.41)
    con_parts.append(con_desk)
    
    con_hood = cat.create_box("Console_Hood_Room", size=(1.15, 0.38, 0.52), mat=cat.MATS["Mat_Gunmetal"])
    con_hood.location = (0, 0.16, 1.05)
    con_hood.rotation_euler = Euler((R(-15), 0, 0))
    con_parts.append(con_hood)
    
    con_screen = cat.create_box("CRT_Screen_Room", size=(0.74, 0.04, 0.34), mat=cat.MATS["Mat_CRT_Radar_Screen"], bevel=False)
    con_screen.location = (0, -0.045, 1.05)
    con_screen.rotation_euler = Euler((R(-15), 0, 0))
    con_parts.append(con_screen)
    
    con_pulse = cat.create_box("CRT_Oscilloscope_Line", size=(0.55, 0.02, 0.03), mat=cat.MATS["Mat_Plasma_WhiteFlare"], bevel=False)
    con_pulse.location = (0, -0.068, 1.05)
    con_pulse.rotation_euler = Euler((R(-15), 0, 0))
    con_parts.append(con_pulse)
    
    con_estop = cat.create_cylinder("Estop_Button_Room", radius=0.06, depth=0.06, segments=12, mat=cat.MATS["Mat_Valve_Red"])
    con_estop.location = (0.42, -0.15, 0.85)
    con_parts.append(con_estop)
    
    cat.assemble_asset("SM_Consola_Terminal_Ensamblada", con_parts, col, location=(center_x + 1.8, -1.5, 0.26), rotation=(0, 0, 40))
    
    # 6. Batería Colectora y Tuberías Bridadas de Plasma en Mamparo Posterior
    cat.build_plasma_conduit_manifold(col, loc=(center_x - 2.2, 4.05, 0.26), rot=(0, 0, 0))
    
    # 7. Cartelera Mural de Advertencia de Peligro Alta Energía
    cat.build_hazard_signboard(col, loc=(center_x + 2.2, 4.05, 2.2), rot=(0, 0, 0))
    
    # 8. Dron Minero Observador Flotando en Suspensión Gravitatoria (Ojo cian y propulsores encarados a la cámara)
    cat.build_mining_scout_drone(col, loc=(center_x - 1.6, -1.3, 1.95), rot=(12, 0, 42))
    
    l_drone = bpy.data.lights.new(name="Scout_Drone_Light", type='POINT')
    l_drone.energy = 140.0
    l_drone.color = (0.0, 0.95, 1.0)
    l_drone_obj = bpy.data.objects.new("Scout_Drone_Light", l_drone)
    l_drone_obj.location = (center_x - 1.6, -1.45, 1.95)
    col.objects.link(l_drone_obj)
    
    # 9. Componentes Mecánicos Auxiliares
    cat.build_hydraulic_piston(col, loc=(center_x + 3.9, 1.2, 0.26), rot=(0, 0, -90))
    
    box_trans = cat.create_box("Transformer_Box", size=(1.2, 1.2, 0.8), mat=cat.MATS["Mat_Gunmetal"], bevel=True)
    box_trans.location = (center_x + 0.6, 3.4, 0.64)
    col.objects.link(box_trans)
    cat.build_chimney_comic_flames(col, loc=(center_x + 0.6, 3.4, 1.05), rot=(0, 0, 0))
    
    cat.build_sawblade_24t(col, loc=(center_x - 3.9, 2.0, 1.8), rot=(0, 90, 0))
    
    # 10. Iluminación diegética de plasma de alto contraste con luces de área suaves
    # Luz del plasma sin sombras oclusivas del toro sobre las paredes
    l_plasma = bpy.data.lights.new(name="Plasma_Core_Light", type='POINT')
    l_plasma.energy = 620.0
    l_plasma.color = (0.0, 0.92, 1.0)
    l_plasma.use_shadow = False
    l_plasma_obj = bpy.data.objects.new("Plasma_Core_Light", l_plasma)
    l_plasma_obj.location = (center_x, 0.2, 1.9)
    col.objects.link(l_plasma_obj)
    
    # Luz Clave difusa frontal-derecha (softbox 8.5x6m baña la sala y ambos mamparos sin recortes oscuros)
    create_studio_area_light(col, "Plasma_Key_Area", location=(center_x + 3.8, -6.5, 6.0), 
                             target=(center_x, 0.4, 2.0), size_x=8.5, size_y=6.0, energy=560.0, color=(0.75, 0.90, 1.0))
    
    # Luz de Relleno difusa lateral-izquierda (softbox 7.0x5.0m elimina el corte oscuro en la pared izquierda)
    create_studio_area_light(col, "Plasma_Fill_Area", location=(center_x - 4.5, -4.5, 5.0), 
                             target=(center_x, 0.4, 2.0), size_x=7.0, size_y=5.0, energy=300.0, color=(0.65, 0.85, 1.0))

# ==============================================================================
# ILUMINACIÓN GLOBAL DE ESTUDIO Y CÁMARAS CINEMATOGRÁFICAS
# ==============================================================================
def setup_global_lighting(col):
    """Configura iluminación cenital neutra y suelo exterior infinito mate."""
    outer_floor = cat.create_box("Outer_Void_Floor", size=(60.0, 30.0, 0.05), mat=cat.MATS["Mat_Studio_Floor"], bevel=False)
    outer_floor.location = (0, 0, -0.025)
    col.objects.link(outer_floor)
    
    outer_wall = cat.create_box("Outer_Void_Backwall", size=(60.0, 0.1, 14.0), mat=cat.MATS["Mat_Pedestal_Base"], bevel=False)
    outer_wall.location = (0, 5.0, 6.8)
    col.objects.link(outer_wall)
    
    sun_data = bpy.data.lights.new(name="Global_Key_Sun", type='SUN')
    sun_data.energy = 1.6
    sun_data.color = (1.0, 0.98, 0.95)
    sun_data.angle = R(15)
    sun_obj = bpy.data.objects.new("Global_Key_Sun", sun_data)
    sun_obj.rotation_euler = Euler((R(52), R(15), R(-25)))
    col.objects.link(sun_obj)
    
    rim_data = bpy.data.lights.new(name="Global_Rim_Sun", type='SUN')
    rim_data.energy = 1.0
    rim_data.color = (0.6, 0.8, 1.0)
    rim_obj = bpy.data.objects.new("Global_Rim_Sun", rim_data)
    rim_obj.rotation_euler = Euler((R(-60), R(-15), R(140)))
    col.objects.link(rim_obj)

def setup_assembly_cameras(col):
    """Configura cámaras para el panorama general y planos individuales en encuadre 3/4 diorama."""
    cams = {}
    
    # 1. Cámara Panorama Maestro Tríptico (24mm, encuadre expansivo de las 3 salas)
    cam_pan_data = bpy.data.cameras.new("Cam_Panorama_Triptico")
    cam_pan_data.lens = 24.0
    cam_pan_obj = bpy.data.objects.new("Cam_Panorama_Triptico", cam_pan_data)
    cam_pan_obj.location = Vector((0.0, -23.5, 10.5))
    point_camera_at(cam_pan_obj, (0.0, 0.2, 2.2))
    col.objects.link(cam_pan_obj)
    cams["Panorama"] = cam_pan_obj
    
    # 2. Cámaras de Sala Individuales: Perspectiva 3/4 Diorama Isométrico Auténtico
    room_configs = [
        ("Carguero_Quimico", -14.0, (-14.0 + 6.8, -7.6, 6.2), (-14.0, 0.4, 1.8)),
        ("Crucero_Celestia", 0.0, (0.0 + 6.8, -7.6, 6.0), (0.0, 0.4, 1.9)),
        ("Refineria_Plasma", 14.0, (14.0 + 6.8, -7.6, 6.2), (14.0, 0.4, 1.8))
    ]
    
    for name, rx, cam_pos, target_pos in room_configs:
        cdata = bpy.data.cameras.new(f"Cam_{name}")
        cdata.lens = 34.0
        cobj = bpy.data.objects.new(f"Cam_{name}", cdata)
        cobj.location = Vector(cam_pos)
        point_camera_at(cobj, target_pos)
        col.objects.link(cobj)
        cams[name] = cobj
        
    return cams

# ==============================================================================
# EJECUCIÓN PRINCIPAL Y RENDERIZADO
# ==============================================================================
def main():
    print("=" * 80)
    print("CONSTRUYENDO SALAS MODULARES ENSAMBLADAS OFICIALES - ASTRA HAZARD")
    print("=" * 80)
    
    scene = reset_assembly_scene()
    init_assembly_materials()
    
    col_world = cat.create_collection("00_Escenografia_Global")
    col_room1 = cat.create_collection("01_Sala_Carguero_Quimico")
    col_room2 = cat.create_collection("02_Sala_Crucero_Celestia")
    col_room3 = cat.create_collection("03_Sala_Refineria_Plasma")
    
    # 1. Ensamblar las 3 salas modulares completas
    assemble_room_chemical_freighter(col_room1, center_x=-14.0)
    assemble_room_luxury_celestia(col_room2, center_x=0.0)
    assemble_room_plasma_refinery(col_room3, center_x=14.0)
    
    # 2. Configurar iluminación y cámaras
    setup_global_lighting(col_world)
    cams = setup_assembly_cameras(col_world)
    
    # 3. Guardar archivo Blend oficial
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_FILE)
    print(f"\n[OK] Blend oficial guardado en: {BLEND_FILE}")
    
    # ==============================================================================
    # RENDERIZADO CINEMATOGRÁFICO DE ALTA RESOLUCIÓN
    # ==============================================================================
    render_jobs = [
        ("Panorama", "Showcase_Salas_Panorama_Triptico.png", 2560, 920),
        ("Carguero_Quimico", "Showcase_Sala_Carguero_Quimico.png", 1920, 1080),
        ("Crucero_Celestia", "Showcase_Sala_Crucero_Celestia.png", 1920, 1080),
        ("Refineria_Plasma", "Showcase_Sala_Refineria_Plasma.png", 1920, 1080)
    ]
    
    for cam_key, filename, w, h in render_jobs:
        out_path = os.path.join(RENDERS_DIR, filename)
        scene.camera = cams[cam_key]
        scene.render.resolution_x = w
        scene.render.resolution_y = h
        scene.render.resolution_percentage = 100
        scene.render.filepath = out_path
        
        print(f"  [RENDER] Generando {filename} ({w}x{h})...")
        bpy.ops.render.render(write_still=True)
        print(f"  [OK] Guardado en: {out_path}")
        
    assemble_master_assembly_infographic()

# ==============================================================================
# COMPOSICIÓN DE LA LÁMINA INFOGRÁFICA MAESTRA (2560x1440)
# ==============================================================================
def assemble_master_assembly_infographic():
    print("\n[COMPOSITOR] Ensamblando Lámina Maestra de Salas Ensambladas (2560x1440)...")
    
    W, H = 2560, 1440
    canvas = Image.new("RGBA", (W, H), (14, 16, 20, 255))
    draw = ImageDraw.Draw(canvas)
    
    try:
        font_title = ImageFont.truetype("arialbd.ttf", 26)
        font_sub = ImageFont.truetype("arialbd.ttf", 16)
        font_pill = ImageFont.truetype("arialbd.ttf", 14)
        font_card_title = ImageFont.truetype("arialbd.ttf", 19)
        font_card_desc = ImageFont.truetype("arial.ttf", 14)
    except:
        font_title = font_sub = font_pill = font_card_title = font_card_desc = ImageFont.load_default()
        
    # Encabezado Oficial con margen protegido
    draw.text((40, 18), "ASTRA HAZARD // REPOSITORIO DE ARQUITECTURA, LEVEL DESIGN Y ENTORNOS MODULARES", fill=(245, 166, 35), font=font_sub)
    draw.text((40, 46), "SALAS JUGABLES ENSAMBLADAS: DIORAMAS DE NIVELES TIER 1, 2 Y 3 (26 ASSETS)", fill=(255, 255, 255), font=font_title)
    
    # Badges Técnicos alineados a la derecha sin colisión
    pills = [
        ("100% ACTIVOS REUTILIZABLES", (211, 84, 0)),
        ("3 SALAS JUGABLES", (41, 128, 185)),
        ("DIORAMAS DIÉGETICOS", (39, 174, 96)),
        ("FREESTYLE INK", (142, 68, 173)),
        ("UE5 READY", (108, 92, 231))
    ]
    cur_x = W - 40
    for text, bg_col in reversed(pills):
        tw = len(text) * 9 + 18
        cur_x -= tw
        draw.rounded_rectangle((cur_x, 34, cur_x + tw - 8, 66), radius=6, fill=bg_col)
        draw.text((cur_x + 9, 42), text, fill=(255, 255, 255), font=font_pill)
        cur_x -= 8
        
    draw.line((40, 92, W - 40, 92), fill=(45, 52, 65), width=2)
    
    # 1. Tríptico Panorámico Superior (2480x730)
    pan_path = os.path.join(RENDERS_DIR, "Showcase_Salas_Panorama_Triptico.png")
    if os.path.exists(pan_path):
        pan_img = Image.open(pan_path).convert("RGBA")
        pan_w = W - 80
        pan_h = 730
        pan_resized = pan_img.resize((pan_w, pan_h), Image.Resampling.LANCZOS)
        canvas.paste(pan_resized, (40, 108))
        draw.rectangle((40, 108, 40 + pan_w, 108 + pan_h), outline=(45, 52, 65), width=2)
        
    # 2. Tres Paneles Inferiores (Uno por cada sala)
    rooms_data = [
        ("SALA 1: BAHÍA DE CARGA QUÍMICA (TIER 1)", "Showcase_Sala_Carguero_Quimico.png", (245, 166, 35),
         "• Activos: Contenedores TEU apilados, Cuba ácida, Grúa, Vigas I, Pasarelas y Barriles.\n• Jugabilidad: Foco de peligro químico activo, vapores ácidos, contención y rescate.\n• Iluminación: Softbox difuso de estudio (560W) + relleno azul (300W) + glow ácido verde (220W).\n• Estilo: Derelict industrial sci-fi con corrosión profunda y chapa naval oxidada."),
        ("SALA 2: GRAN SALÓN OBSERVATORIO CELESTIA (TIER 2)", "Showcase_Sala_Crucero_Celestia.png", (212, 175, 55),
         "• Activos: Ventanal a Saturno 2.5D, Gran alfombra palaciega, Sofá/sillones, Mesa Carrara y Boiserie.\n• Jugabilidad: Salón VIP de pasajeros, extracción de civiles VIP y artefactos valiosos.\n• Iluminación: Softbox cálido (460W) + araña Ziggurat de latón (440W) + luz estelar del cosmos.\n• Estilo: Art Déco monumental, terciopelo burdeos (#3A0A16), nogal barnizado y oro pulido."),
        ("SALA 3: CÁMARA REACTOR TOKAMAK (TIER 3)", "Showcase_Sala_Refineria_Plasma.png", (0, 240, 255),
         "• Activos: Reactor toroidal Tokamak, Pasarela curva, Consola CRT activa, Colector y Dron minero.\n• Jugabilidad: Falla crítica de plasma de alta energía, estabilización y purga térmica.\n• Iluminación: Softbox frío de estudio (560W) + resplandor plasma cian (620W) + CRT verde activo.\n• Estilo: Hipertecnología industrial, gunmetal oscuro y singularidad energética activa.")
    ]
    
    card_w = (W - 80 - 30) // 3
    card_h = 540
    card_y = 860
    
    for i, (title, img_name, border_col, desc) in enumerate(rooms_data):
        cx = 40 + i * (card_w + 15)
        
        draw.rectangle((cx, card_y, cx + card_w, card_y + card_h), fill=(20, 24, 30), outline=border_col, width=2)
        
        img_path = os.path.join(RENDERS_DIR, img_name)
        if os.path.exists(img_path):
            card_img = Image.open(img_path).convert("RGBA")
            c_render_h = 340
            c_render_w = card_w - 4
            card_resized = card_img.resize((c_render_w, c_render_h), Image.Resampling.LANCZOS)
            canvas.paste(card_resized, (cx + 2, card_y + 2))
            
        draw.rectangle((cx, card_y + 342, cx + card_w, card_y + 380), fill=(28, 33, 42))
        draw.text((cx + 12, card_y + 350), title, fill=border_col, font=font_card_title)
        
        draw.text((cx + 14, card_y + 392), desc, fill=(215, 225, 240), font=font_card_desc, spacing=4)

    master_path = os.path.join(RENDERS_DIR, "Showcase_Salas_Ensambladas_Master.png")
    canvas.save(master_path, "PNG")
    
    shutil.copy2(master_path, os.path.join(ARTIFACT_DIR, "Showcase_Salas_Ensambladas_Master.png"))
    for _, fname, _, _ in rooms_data:
        shutil.copy2(os.path.join(RENDERS_DIR, fname), os.path.join(ARTIFACT_DIR, fname))
    shutil.copy2(pan_path, os.path.join(ARTIFACT_DIR, "Showcase_Salas_Panorama_Triptico.png"))
    
    print(f"\n[MASTER OK] Lámina Maestra Oficial generada con éxito: {master_path}")
    print("=" * 80)

if __name__ == "__main__":
    main()

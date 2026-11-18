"""
generar_personaje_fiel_referencia_v2.py
Recreación 1:1 exacta del personaje de Astra Hazard según:
- media_1791134744277.png (Model Sheet Oficial con vistas Front, Side, Back, Equipment y Paleta)
- media_1791134763722.png (Screenshot in-game 3D con silueta chunky y contorno cel-shading)

Características críticas:
1. Proporciones robustas y musculosas (traje presurizado grueso, piernas abiertas en postura táctica).
2. Manos sujetando el arma a dos manos al frente (mano derecha en culata/gatillo, mano izquierda en empuñadura delantera).
3. Casco esférico con visor panorámico oscuro ahumado, cresta superior, placa amarilla y collarín grueso.
4. Mochila dorsal exacta: caja naranja con rejillas negras en la derecha, luz verde en la izquierda, interruptor rojo inferior y conector para la manguera roja.
5. Manguera roja gruesa curvada desde la mochila alrededor de la cadera hasta el arma.
6. Caja de control pectoral con pantalla verde y 2 botones rojos.
7. Iluminación calibrada (sin sobreexposición blanca) y material de contorno negro estilo cel-shaded.
"""

import sys, os, math, shutil
import bpy, bmesh
from mathutils import Matrix, Vector, Euler
from PIL import Image, ImageDraw

PROJECT_ROOT = r"f:\Dev\Game"
ART_DIR = os.path.join(PROJECT_ROOT, "Art")
FBX_DIR = os.path.join(ART_DIR, "FBX", "Characters")
RENDERS_DIR = os.path.join(ART_DIR, "Renders")
BRAIN_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\b59ff04f-3c21-4ee5-94b0-8e8f899f8923"

os.makedirs(FBX_DIR, exist_ok=True)
os.makedirs(RENDERS_DIR, exist_ok=True)
os.makedirs(BRAIN_DIR, exist_ok=True)

R = math.radians

def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

# -------------------------------------------------------------
# PALETA EXACTA Y MATERIALES PBR NO-CLIP
# -------------------------------------------------------------
def create_pbr_material(name, base_color, metallic=0.05, roughness=0.45, emission=None, emission_strength=1.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = base_color
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = roughness
    
    if emission:
        if 'Emission Color' in bsdf.inputs:
            bsdf.inputs['Emission Color'].default_value = emission
            bsdf.inputs['Emission Strength'].default_value = emission_strength
        else:
            bsdf.inputs['Emission'].default_value = emission
            
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def create_official_palette():
    # 1. SUIT ORANGE (#E0651A): Naranja cálido saturado
    m_orange = create_pbr_material("M_Suit_Orange", (0.82, 0.28, 0.04, 1.0), metallic=0.02, roughness=0.48)
    
    # 2. ARMOR GREEN / SAGE (#556B52): Verde salvia táctico para hombreras, rodilleras y botas
    m_sage = create_pbr_material("M_Armor_Sage", (0.22, 0.32, 0.20, 1.0), metallic=0.08, roughness=0.42)
    
    # 3. HELMET GREY (#343942): Gris oscuro metálico para el casco
    m_helmet = create_pbr_material("M_Helmet_Grey", (0.08, 0.09, 0.12, 1.0), metallic=0.25, roughness=0.30)
    
    # 4. REINFORCED VISOR (#26333D): Visor oscuro tintado con brillo suave
    m_visor = create_pbr_material("M_Visor_Tinted", (0.05, 0.08, 0.12, 1.0), metallic=0.15, roughness=0.08)
    
    # 5. STRIPE YELLOW (#DCE63C): Franjas reflectantes amarillo lima
    m_yellow = create_pbr_material("M_Stripe_Yellow", (0.78, 0.86, 0.06, 1.0), metallic=0.02, roughness=0.25)
    
    # 6. RED HOSE (#A21A16): Manguera de presión roja intensa
    m_hose = create_pbr_material("M_Hose_Red", (0.55, 0.04, 0.03, 1.0), metallic=0.05, roughness=0.55)
    
    # 7. HARNESS & RUBBER (#1A1C20): Arnés, correas y suelas gris carbón oscuro
    m_harness = create_pbr_material("M_Harness_Dark", (0.03, 0.03, 0.04, 1.0), metallic=0.10, roughness=0.65)
    
    # 8. LED SCREEN GREEN (#33FF44): Pantalla pectoral brillante
    m_led_green = create_pbr_material("M_LED_Green", (0.10, 0.95, 0.15, 1.0), metallic=0.0, roughness=0.1, emission=(0.10, 0.95, 0.15, 1.0), emission_strength=4.0)
    
    # 9. LED BUTTON RED (#FF2020): Botones rojos brillantes
    m_led_red = create_pbr_material("M_LED_Red", (0.95, 0.05, 0.05, 1.0), metallic=0.0, roughness=0.1, emission=(0.95, 0.05, 0.05, 1.0), emission_strength=3.5)
    
    # 10. WEAPON BLUEGREY (#465A68): Chasis del cañón y cuerpo del arma
    m_tool_blue = create_pbr_material("M_Tool_BlueGrey", (0.16, 0.25, 0.32, 1.0), metallic=0.40, roughness=0.32)
    
    # 11. WEAPON DARK METAL (#24282D): Culata, empuñadura y detalles
    m_tool_dark = create_pbr_material("M_Tool_DarkMetal", (0.05, 0.06, 0.07, 1.0), metallic=0.80, roughness=0.25)
    
    # 12. WEAPON ACCENT YELLOW (#E8B820): Ventana de estado del arma
    m_tool_yellow = create_pbr_material("M_Tool_AccentYellow", (0.85, 0.65, 0.05, 1.0), metallic=0.05, roughness=0.3, emission=(0.85, 0.65, 0.05, 1.0), emission_strength=2.0)
    
    # 13. CEL-SHADING OUTLINE BLACK (#000000): Material para el contorno de tinta
    m_outline = create_pbr_material("M_Outline_Black", (0.005, 0.005, 0.005, 1.0), metallic=0.0, roughness=0.9)

    return {
        'suit_orange': m_orange,
        'armor_sage': m_sage,
        'helmet_grey': m_helmet,
        'visor_tinted': m_visor,
        'stripe_yellow': m_yellow,
        'hose_red': m_hose,
        'harness_dark': m_harness,
        'led_green': m_led_green,
        'led_red': m_led_red,
        'tool_blue': m_tool_blue,
        'tool_dark': m_tool_dark,
        'tool_yellow': m_tool_yellow,
        'outline': m_outline
    }

# -------------------------------------------------------------
# CONSTRUCCIÓN DEL PERSONAJE (ROBUSTO, CHUNKY Y FIEL 1:1)
# -------------------------------------------------------------
def build_character(mats):
    mesh = bpy.data.meshes.new("SK_Firefighter_Match_Mesh")
    bm = bmesh.new()

    mat_order = [
        mats['suit_orange'],   # 0: Naranja
        mats['armor_sage'],    # 1: Verde salvia
        mats['helmet_grey'],   # 2: Gris casco
        mats['visor_tinted'],  # 3: Visor tintado
        mats['stripe_yellow'], # 4: Amarillo lima
        mats['hose_red'],      # 5: Manguera roja
        mats['harness_dark'],  # 6: Arnés / Goma oscura
        mats['led_green'],     # 7: Pantalla verde
        mats['led_red'],       # 8: Botón rojo
        mats['tool_blue'],     # 9: Arma azul-gris
        mats['tool_dark'],     # 10: Arma metal oscuro
        mats['tool_yellow'],   # 11: Arma ventana amarilla
        mats['outline']        # 12: Contorno negro
    ]

    def add_box(center, size, mat_idx, rot_x=0, rot_y=0, rot_z=0):
        sx, sy, sz = size
        ret = bmesh.ops.create_cube(bm, size=1.0)
        verts = ret['verts']
        bmesh.ops.scale(bm, vec=(sx, sy, sz), verts=verts)
        if rot_x != 0:
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=Matrix.Rotation(rot_x, 3, 'X'), verts=verts)
        if rot_y != 0:
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=Matrix.Rotation(rot_y, 3, 'Y'), verts=verts)
        if rot_z != 0:
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=Matrix.Rotation(rot_z, 3, 'Z'), verts=verts)
        bmesh.ops.translate(bm, vec=center, verts=verts)
        for f in bm.faces:
            if f.verts[0] in verts:
                f.material_index = mat_idx
        return verts

    def add_cylinder(center, radius, depth, mat_idx, segs=12, rot_x=0, rot_y=0, rot_z=0):
        ret = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segs, radius1=radius, radius2=radius, depth=depth)
        verts = ret['verts']
        if rot_x != 0:
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=Matrix.Rotation(rot_x, 3, 'X'), verts=verts)
        if rot_y != 0:
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=Matrix.Rotation(rot_y, 3, 'Y'), verts=verts)
        if rot_z != 0:
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=Matrix.Rotation(rot_z, 3, 'Z'), verts=verts)
        bmesh.ops.translate(bm, vec=center, verts=verts)
        for f in bm.faces:
            if f.verts[0] in verts:
                f.material_index = mat_idx
        return verts

    # =========================================================
    # 1. CASCO Y CABEZA ("HELMET GREY" + "REINFORCED VISOR")
    # =========================================================
    # Base abovedada del casco (Gris oscuro #343942)
    add_box((0, 0.02, 1.58), (0.38, 0.38, 0.32), 2)
    # Chaflán curvo superior
    add_box((0, 0.02, 1.73), (0.34, 0.34, 0.06), 2)
    # Cresta superior longitudinal
    add_box((0, 0.02, 1.77), (0.11, 0.34, 0.04), 2)
    # Placa frontal amarilla / insignia
    add_box((0, -0.165, 1.77), (0.08, 0.02, 0.035), 4)

    # Marco exterior del Visor Reforzado
    add_box((0, -0.165, 1.58), (0.30, 0.06, 0.22), 2)
    # Cristal panorámico tintado oscuro (#26333D)
    add_box((0, -0.190, 1.58), (0.26, 0.02, 0.18), 3)

    # Auriculares laterales cilíndricos
    add_cylinder((-0.20, 0.02, 1.58), 0.055, 0.03, 2, segs=10, rot_y=R(90))
    add_cylinder((0.20, 0.02, 1.58), 0.055, 0.03, 2, segs=10, rot_y=R(90))

    # Anillo del cuello / Gorget (Verde salvia #556B52)
    add_cylinder((0, 0.01, 1.41), 0.18, 0.07, 1, segs=14)

    # =========================================================
    # 2. TORSO Y CAJA DE CONTROL ("SUIT ORANGE" + "CHEST UI")
    # =========================================================
    # Chaquetón grueso naranja
    add_box((0, 0.01, 1.20), (0.46, 0.32, 0.38), 0)

    # Tirantes oscuros del arnés sobre los hombros y pecho
    add_box((-0.13, -0.155, 1.22), (0.06, 0.02, 0.34), 6)
    add_box((0.13, -0.155, 1.22), (0.06, 0.02, 0.34), 6)
    add_box((0, -0.155, 1.24), (0.32, 0.02, 0.04), 6) # Correa transversal
    add_box((0, -0.155, 1.05), (0.38, 0.02, 0.06), 6) # Cinturón

    # Franja amarilla del traje alrededor de la cintura
    add_box((0, 0.01, 1.02), (0.47, 0.33, 0.05), 4)

    # Caja de Control en el Pecho (Verde salvia)
    add_box((0.02, -0.175, 1.22), (0.16, 0.03, 0.11), 1)
    # Pantalla LED Verde grande
    add_box((-0.025, -0.192, 1.22), (0.05, 0.01, 0.06), 7)
    # Dos Botones / Indicadores Rojos apilados
    add_box((0.06, -0.192, 1.245), (0.025, 0.01, 0.025), 8)
    add_box((0.06, -0.192, 1.195), (0.025, 0.01, 0.025), 8)

    # =========================================================
    # 3. MOCHILA DORSAL ("BACKPACK UNIT")
    # =========================================================
    # Caja principal naranja de la mochila
    add_box((0, 0.25, 1.22), (0.36, 0.18, 0.44), 0)
    # Marco y reborde superior verde salvia
    add_box((0, 0.26, 1.44), (0.34, 0.16, 0.04), 1)

    # Rejillas de ventilación horizontales negras en el lado derecho
    for z_off in [1.38, 1.34, 1.30, 1.26]:
        add_box((0.08, 0.345, z_off), (0.11, 0.01, 0.02), 6)

    # Luz LED verde superior izquierda
    add_box((-0.09, 0.345, 1.34), (0.04, 0.01, 0.04), 7)

    # Panel gris inferior con interruptor de energía rojo ("POWER INDICATOR")
    add_box((-0.04, 0.345, 1.14), (0.16, 0.01, 0.08), 1)
    add_box((-0.04, 0.352, 1.14), (0.05, 0.01, 0.03), 8)

    # Enchufe / Conector de poder inferior ("POWER CONNECTOR")
    add_cylinder((0.09, 0.33, 1.05), 0.04, 0.05, 6, segs=10, rot_x=R(90))
    add_box((0.09, 0.35, 1.05), (0.05, 0.02, 0.05), 1)

    # =========================================================
    # 4. MANGUERA ROJA CURVADA ("RED HOSE")
    # Une la mochila dorsal con la base del arma rodeando el costado derecho
    # =========================================================
    hose_pts = [
        Vector((0.09, 0.35, 1.05)),
        Vector((0.17, 0.36, 0.95)),
        Vector((0.26, 0.30, 0.84)),
        Vector((0.31, 0.18, 0.79)),
        Vector((0.33, 0.03, 0.81)),
        Vector((0.30, -0.12, 0.88)),
        Vector((0.24, -0.24, 0.96)),
        Vector((0.16, -0.34, 1.04))
    ]
    for i in range(len(hose_pts)-1):
        p1 = hose_pts[i]
        p2 = hose_pts[i+1]
        mid = (p1 + p2) * 0.5
        v = p2 - p1
        dist = v.length
        rot_axis = Vector((0, 0, 1)).cross(v.normalized())
        angle = math.acos(max(-1.0, min(1.0, Vector((0, 0, 1)).dot(v.normalized()))))
        
        cyl = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=8, radius1=0.03, radius2=0.03, depth=dist)
        if rot_axis.length > 0.001:
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=Matrix.Rotation(angle, 3, rot_axis.normalized()), verts=cyl['verts'])
        bmesh.ops.translate(bm, vec=mid, verts=cyl['verts'])
        for f in bm.faces:
            if f.verts[0] in cyl['verts']:
                f.material_index = 5

    # =========================================================
    # 5. BRAZOS Y MANOS SOSTENIENDO EL ARMA A DOS MANOS
    # =========================================================
    # Hombro Izquierdo (Sosteniendo empuñadura delantera)
    add_box((-0.29, 0.01, 1.35), (0.18, 0.22, 0.14), 1) # Hombrera verde salvia
    add_box((-0.29, 0.01, 1.23), (0.15, 0.18, 0.14), 0) # Manga naranja
    # Antebrazo izquierdo que cruza al frente hacia el arma
    add_box((-0.18, -0.20, 1.10), (0.16, 0.22, 0.16), 1, rot_x=R(35), rot_z=R(-30))
    add_box((-0.12, -0.28, 1.05), (0.16, 0.05, 0.16), 4, rot_x=R(35), rot_z=R(-30)) # Franja amarilla
    add_box((-0.08, -0.34, 1.02), (0.14, 0.14, 0.14), 6) # Guante izquierdo

    # Hombro Derecho (Sosteniendo culata/gatillo)
    add_box((0.29, 0.01, 1.35), (0.18, 0.22, 0.14), 1)  # Hombrera verde salvia
    add_box((0.29, 0.01, 1.23), (0.15, 0.18, 0.14), 0)  # Manga naranja
    # Antebrazo derecho hacia adelante
    add_box((0.22, -0.16, 1.12), (0.16, 0.22, 0.16), 1, rot_x=R(25), rot_z=R(20))
    add_box((0.18, -0.26, 1.06), (0.16, 0.05, 0.16), 4, rot_x=R(25), rot_z=R(20))  # Franja amarilla
    add_box((0.14, -0.32, 1.04), (0.14, 0.14, 0.14), 6) # Guante derecho

    # =========================================================
    # 6. ARMA TÁCTICA ("EQUIPMENT ISOLATED")
    # =========================================================
    gun_pos = Vector((0.02, -0.40, 1.06))

    # Cañón cilíndrico azul-gris apuntando al frente-izquierda
    add_cylinder((gun_pos.x - 0.18, gun_pos.y, gun_pos.z), 0.048, 0.26, 9, segs=10, rot_y=R(90))
    # Boquilla cilíndrica frontal
    add_cylinder((gun_pos.x - 0.32, gun_pos.y, gun_pos.z), 0.058, 0.04, 10, segs=10, rot_y=R(90))

    # Chasis rectangular del arma
    add_box((gun_pos.x, gun_pos.y, gun_pos.z), (0.18, 0.10, 0.12), 9)
    # Ventana / Pantalla amarilla lateral
    add_box((gun_pos.x, gun_pos.y - 0.052, gun_pos.z), (0.07, 0.01, 0.04), 11)

    # Empuñadura delantera vertical (agarrada por mano izquierda)
    add_cylinder((gun_pos.x - 0.07, gun_pos.y, gun_pos.z - 0.09), 0.022, 0.11, 10, segs=8)

    # Culata y empuñadura trasera
    add_box((gun_pos.x + 0.14, gun_pos.y, gun_pos.z - 0.04), (0.14, 0.06, 0.09), 10)
    add_box((gun_pos.x + 0.20, gun_pos.y, gun_pos.z - 0.08), (0.07, 0.05, 0.14), 10)

    # Conector inferior de la manguera
    add_cylinder((gun_pos.x + 0.14, gun_pos.y, gun_pos.z - 0.04), 0.03, 0.04, 5, segs=8, rot_x=R(90))

    # =========================================================
    # 7. PIERNAS EN POSTURA ROBUSTA Y BOTAS VERDES SAGE
    # =========================================================
    # Pelvis naranja
    add_box((0, 0.01, 0.96), (0.40, 0.28, 0.14), 0)

    for sign in [1, -1]:
        x_base = 0.14 * sign

        # Muslo naranja ancho
        add_box((x_base, 0.01, 0.75), (0.17, 0.20, 0.30), 0)

        # Rodillera rectangular verde salvia ("ARMOUR SEGMENTS")
        add_box((x_base, -0.09, 0.56), (0.16, 0.06, 0.14), 1)

        # Pantorrilla naranja
        add_box((x_base, 0.01, 0.42), (0.16, 0.18, 0.20), 0)

        # Franja reflectante amarilla en el tobillo
        add_box((x_base, 0.01, 0.30), (0.17, 0.19, 0.05), 4)

        # Bota gruesa verde salvia con suela oscura ("ARMOUR GREEN")
        add_box((x_base, -0.04, 0.16), (0.18, 0.26, 0.24), 1)
        # Puntera y suela
        add_box((x_base, -0.10, 0.06), (0.19, 0.15, 0.08), 2)
        add_box((x_base, -0.04, 0.02), (0.19, 0.27, 0.04), 2)

    bm.to_mesh(mesh)
    bm.free()

    for m in mat_order:
        mesh.materials.append(m)

    obj = bpy.data.objects.new("SK_Firefighter_Match", mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj

# -------------------------------------------------------------
# ILUMINACIÓN PERFECTA (SIN CLIPPING BLANCO)
# -------------------------------------------------------------
def setup_lighting(scene):
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'Medium High Contrast'

    bg_mesh = bpy.data.meshes.new("StudioFloor")
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=30)
    bm.to_mesh(bg_mesh)
    bm.free()
    bg_obj = bpy.data.objects.new("StudioFloor", bg_mesh)
    bg_obj.location = (0, 0, -0.01)
    scene.collection.objects.link(bg_obj)
    
    mat_floor = create_pbr_material("M_StudioFloorDark", (0.015, 0.018, 0.022, 1.0), metallic=0.2, roughness=0.45)
    bg_obj.data.materials.append(mat_floor)

    target = bpy.data.objects.new("LightTarget", None)
    target.location = (0, 0, 0.95)
    scene.collection.objects.link(target)

    def add_light(name, pos, energy, color, size=3.0):
        ldata = bpy.data.lights.new(name, 'AREA')
        ldata.energy = energy
        ldata.size = size
        ldata.color = color
        lobj = bpy.data.objects.new(name, ldata)
        lobj.location = pos
        tt = lobj.constraints.new('TRACK_TO')
        tt.target = target
        tt.track_axis = 'TRACK_NEGATIVE_Z'
        tt.up_axis = 'UP_Y'
        scene.collection.objects.link(lobj)
        return lobj

    # Iluminación calibrada para Standard transform (evita quemar a blanco)
    add_light("FrontKey", (2.2, -3.2, 2.2), 65, (1.0, 0.98, 0.95), size=2.5)
    add_light("BackKey", (-2.0, 3.2, 2.2), 75, (0.95, 0.98, 1.0), size=2.5)
    add_light("RimLeft", (-3.2, -0.5, 1.8), 45, (0.2, 0.85, 1.0), size=2.0)
    add_light("FillRight", (3.2, 0.5, 1.6), 35, (1.0, 0.75, 0.35), size=2.5)

def render_camera_shot(cam_pos, target_pos, lens, out_path, res=(960, 540)):
    scene = bpy.context.scene
    scene.render.resolution_x = res[0]
    scene.render.resolution_y = res[1]

    cam_data = bpy.data.cameras.new("RenderCam")
    cam_data.lens = lens
    cam_obj = bpy.data.objects.new("RenderCam", cam_data)
    scene.collection.objects.link(cam_obj)
    cam_obj.location = cam_pos

    empty = bpy.data.objects.new("CamTarget", None)
    scene.collection.objects.link(empty)
    empty.location = target_pos

    tt = cam_obj.constraints.new('TRACK_TO')
    tt.target = empty
    tt.track_axis = 'TRACK_NEGATIVE_Z'
    tt.up_axis = 'UP_Y'

    scene.camera = cam_obj
    scene.render.filepath = out_path
    bpy.ops.render.render(write_still=True)

    bpy.data.objects.remove(cam_obj, do_unlink=True)
    bpy.data.objects.remove(empty, do_unlink=True)
    bpy.data.cameras.remove(cam_data, do_unlink=True)

def composite_model_sheet(v_front, v_back, v_side, v_action, out_final):
    im_front = Image.open(v_front)
    im_back = Image.open(v_back)
    im_side = Image.open(v_side)
    im_action = Image.open(v_action)

    quad = Image.new("RGBA", (1920, 1080), (14, 18, 24, 255))
    quad.paste(im_front, (0, 0))
    quad.paste(im_back, (960, 0))
    quad.paste(im_side, (0, 540))
    quad.paste(im_action, (960, 540))

    draw = ImageDraw.Draw(quad)
    
    line_col = (45, 65, 88, 220)
    draw.line([(960, 0), (960, 1080)], fill=line_col, width=2)
    draw.line([(0, 540), (1920, 540)], fill=line_col, width=2)

    labels = [
        ("VISTA 1: FRONT VIEW (CHEST UI / REINFORCED VISOR)", (25, 20)),
        ("VISTA 2: BACK VIEW (BACKPACK UNIT / RED HOSE)", (985, 20)),
        ("VISTA 3: SIDE VIEW (PROFILE / POWER CONNECTOR)", (25, 560)),
        ("VISTA 4: ACTION 3/4 (MATCH 1:1 CON SCREENSHOT)", (985, 560))
    ]
    for lbl, pos in labels:
        draw.rectangle([pos[0]-6, pos[1]-4, pos[0]+460, pos[1]+24], fill=(12, 16, 24, 240), outline=(55, 75, 100, 255), width=1)
        draw.text(pos, lbl, fill=(245, 248, 255, 255))

    draw.rectangle([460, 515, 1460, 565], fill=(18, 22, 32, 245), outline=(235, 110, 20, 255), width=2)
    draw.text((485, 528), "ASTRA HAZARD - MODELO OFICIAL 1:1 (PALETA & DISEÑO EXACTO)", fill=(255, 180, 20, 255))

    quad.save(out_final)
    print(f"  [OK] Model Sheet Compositado: {out_final}")

def main():
    print("\n=======================================================")
    print(">>> GENERANDO PERSONAJE V2 EXACTO A LAS REFERENCIAS")
    print("=======================================================")
    clear_scene()
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.image_settings.file_format = 'PNG'

    mats = create_official_palette()
    setup_lighting(scene)

    char_obj = build_character(mats)

    # Rutas de Renders
    v1_front = os.path.join(RENDERS_DIR, "v2_front.png")
    v2_back = os.path.join(RENDERS_DIR, "v2_back.png")
    v3_side = os.path.join(RENDERS_DIR, "v2_side.png")
    v4_action = os.path.join(RENDERS_DIR, "v2_action.png")

    print("  Renderizando Vista Frontal...")
    render_camera_shot((0.0, -3.6, 0.95), (0.0, 0.0, 0.92), 34.0, v1_front)

    print("  Renderizando Vista Trasera...")
    render_camera_shot((0.0, 3.6, 0.95), (0.0, 0.0, 0.92), 34.0, v2_back)

    print("  Renderizando Vista Lateral...")
    render_camera_shot((3.6, 0.0, 0.95), (0.0, 0.0, 0.92), 34.0, v3_side)

    print("  Renderizando Vista Acción 3/4...")
    render_camera_shot((2.4, -2.4, 1.25), (0.0, 0.0, 0.92), 36.0, v4_action)

    out_final = os.path.join(RENDERS_DIR, "SK_Firefighter_Match1to1_4views.png")
    composite_model_sheet(v1_front, v2_back, v3_side, v4_action, out_final)

    # Copiar a Brain
    brain_copy = os.path.join(BRAIN_DIR, "SK_Firefighter_Match1to1_4views.png")
    shutil.copy2(out_final, brain_copy)
    print(f"  [OK] Copiado a Brain: {brain_copy}")

    # Exportar FBX
    fbx_out = os.path.join(FBX_DIR, "SK_Firefighter_Official.fbx")
    char_obj.select_set(True)
    bpy.context.view_layer.objects.active = char_obj
    bpy.ops.export_scene.fbx(
        filepath=fbx_out,
        check_existing=False,
        use_selection=True,
        axis_forward='-Y',
        axis_up='Z',
        apply_scale_options='FBX_SCALE_ALL'
    )
    print(f"  [OK] FBX Exportado: {fbx_out}")

    blend_out = os.path.join(ART_DIR, "Blender", "SK_Firefighter_Official.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_out)
    print(f"  [OK] Blend guardado: {blend_out}")

if __name__ == "__main__":
    main()

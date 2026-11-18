"""
generar_personaje_fiel_referencia.py
Generador 3D exacto basado en las hojas de modelo y referencias del usuario:
- media_1791134744277.png (Model Sheet Oficial: Front, Side, Back, Equipment, Palette)
- media_1791134763722.png (Render 3D en juego con estilo PSX / Pixel Outline)

Colores oficiales de la paleta:
- SUIT ORANGE: #D9681E / #E0651A (Traje presurizado naranja)
- ARMOR GREEN / SAGE: #5A6E58 (Placas de blindaje hombreras, rodilleras, botas)
- HELMET GREY: #363B44 (Casco gris oscuro con cresta superior)
- VISOR: #2B3842 (Visor panorámico tintado ahumado)
- YELLOW STRIPES: #D8E048 (Franjas reflectantes amarillo lima)
- RED HOSE: #A62018 (Manguera de poder/extinción roja curvada desde la mochila al arma)
- CHEST DISPLAY: Caja de control en el pecho con pantalla verde LED y botones rojos
"""

import sys, os, math, shutil
import bpy, bmesh
from mathutils import Matrix, Vector, Euler
from PIL import Image, ImageDraw, ImageFont

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
# PALETA EXACTA DE MATERIALES PBR SEGÚN LA HOJA DE MODELO
# -------------------------------------------------------------
def create_pbr_material(name, base_color, metallic=0.1, roughness=0.45, emission=None, emission_strength=1.0):
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

def create_reference_materials():
    return {
        # 1. Traje Naranja Principal (#D9681E)
        'suit_orange': create_pbr_material("M_Suit_Orange", (0.85, 0.40, 0.12, 1.0), metallic=0.04, roughness=0.42),
        # 2. Armadura Verde Salvia (#5A6E58)
        'armor_sage': create_pbr_material("M_Armor_Sage", (0.35, 0.43, 0.34, 1.0), metallic=0.12, roughness=0.38),
        # 3. Casco Gris Oscuro (#363B44)
        'helmet_grey': create_pbr_material("M_Helmet_Grey", (0.21, 0.23, 0.27, 1.0), metallic=0.25, roughness=0.30),
        # 4. Visor Tintado Ahumado Azulino (#2B3842)
        'visor_tinted': create_pbr_material("M_Visor_Tinted", (0.17, 0.22, 0.26, 1.0), metallic=0.10, roughness=0.08),
        # 5. Franjas Reflectantes Amarillo Lima (#D8E048)
        'stripe_yellow': create_pbr_material("M_Stripe_Yellow", (0.85, 0.88, 0.28, 1.0), metallic=0.02, roughness=0.25),
        # 6. Manguera Roja Flexible (#A62018)
        'hose_red': create_pbr_material("M_Hose_Red", (0.65, 0.12, 0.10, 1.0), metallic=0.08, roughness=0.50),
        # 7. Arnés y Juntas Gris Oscuro / Goma
        'harness_dark': create_pbr_material("M_Harness_Dark", (0.12, 0.13, 0.15, 1.0), metallic=0.15, roughness=0.60),
        # 8. LED Verde de la Pantalla del Pecho
        'led_green': create_pbr_material("M_LED_Green", (0.20, 1.0, 0.25, 1.0), metallic=0.0, roughness=0.1, emission=(0.20, 1.0, 0.25, 1.0), emission_strength=7.0),
        # 9. LED Rojo / Botones
        'led_red': create_pbr_material("M_LED_Red", (1.0, 0.15, 0.15, 1.0), metallic=0.0, roughness=0.1, emission=(1.0, 0.15, 0.15, 1.0), emission_strength=5.0),
        # 10. Chasis del Arma / Herramienta (Azul Grisáceo & Acero)
        'tool_bluegrey': create_pbr_material("M_Tool_BlueGrey", (0.32, 0.42, 0.48, 1.0), metallic=0.45, roughness=0.28),
        'tool_darkmetal': create_pbr_material("M_Tool_DarkMetal", (0.14, 0.15, 0.17, 1.0), metallic=0.85, roughness=0.22),
        'tool_accent_yellow': create_pbr_material("M_Tool_AccentYellow", (0.95, 0.80, 0.15, 1.0), metallic=0.1, roughness=0.3, emission=(0.95, 0.80, 0.15, 1.0), emission_strength=2.0)
    }

# -------------------------------------------------------------
# CONSTRUCCIÓN GEOMÉTRICA CONTIGUA Y FIEL AL MODEL SHEET
# -------------------------------------------------------------
def build_character_from_reference(mats):
    mesh = bpy.data.meshes.new("SK_Firefighter_Official_Mesh")
    bm = bmesh.new()

    # Mapeo ordenado de materiales a slots
    mat_order = [
        mats['suit_orange'],       # 0: Naranja base
        mats['armor_sage'],        # 1: Verde salvia
        mats['helmet_grey'],       # 2: Gris casco
        mats['visor_tinted'],      # 3: Visor tintado
        mats['stripe_yellow'],     # 4: Amarillo lima
        mats['hose_red'],          # 5: Manguera roja
        mats['harness_dark'],      # 6: Arnés oscuro
        mats['led_green'],         # 7: Pantalla verde
        mats['led_red'],           # 8: Botón rojo
        mats['tool_bluegrey'],     # 9: Metal azulino arma
        mats['tool_darkmetal'],    # 10: Acero oscuro arma
        mats['tool_accent_yellow'] # 11: Acento amarillo arma
    ]

    def add_box(center, size, mat_idx):
        sx, sy, sz = size
        ret = bmesh.ops.create_cube(bm, size=1.0)
        verts = ret['verts']
        bmesh.ops.scale(bm, vec=(sx, sy, sz), verts=verts)
        bmesh.ops.translate(bm, vec=center, verts=verts)
        for f in bm.faces:
            if f.verts[0] in verts:
                f.material_index = mat_idx
        return verts

    def add_cylinder(center, radius, depth, mat_idx, segs=12, rot_x=0, rot_y=0):
        ret = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segs, radius1=radius, radius2=radius, depth=depth)
        verts = ret['verts']
        if rot_x != 0:
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=Matrix.Rotation(rot_x, 3, 'X'), verts=verts)
        if rot_y != 0:
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=Matrix.Rotation(rot_y, 3, 'Y'), verts=verts)
        bmesh.ops.translate(bm, vec=center, verts=verts)
        for f in bm.faces:
            if f.verts[0] in verts:
                f.material_index = mat_idx
        return verts

    # ---------------------------------------------------------
    # 1. CASCO ("HELMET GREY" con cresta y visor reforzado)
    # ---------------------------------------------------------
    # Cúpula principal del casco (Gris oscuro)
    add_box((0, 0.02, 1.62), (0.34, 0.35, 0.30), 2)
    # Cresta central elevada superior
    add_box((0, 0.02, 1.78), (0.09, 0.32, 0.04), 2)
    # Insignia / luz frontal amarilla sobre el visor
    add_box((0, -0.155, 1.78), (0.07, 0.02, 0.03), 4)
    # Anillo del cuello / Gorget (Verde salvia)
    add_box((0, 0.01, 1.45), (0.32, 0.32, 0.06), 1)

    # Visor panorámico frontal reforzado ("REINFORCED VISOR")
    # Marco exterior del visor
    add_box((0, -0.16, 1.62), (0.27, 0.04, 0.19), 2)
    # Cristal tintado ahumado
    add_box((0, -0.175, 1.62), (0.24, 0.02, 0.16), 3)

    # Módulos auditivos / auriculares cilíndricos a los lados del casco
    add_cylinder((-0.18, 0.02, 1.62), 0.05, 0.03, 2, segs=10, rot_y=R(90))
    add_cylinder((0.18, 0.02, 1.62), 0.05, 0.03, 2, segs=10, rot_y=R(90))

    # ---------------------------------------------------------
    # 2. TORSO ("SUIT ORANGE" + Arnés + Unidad de Control)
    # ---------------------------------------------------------
    # Torso principal naranja
    add_box((0, 0.01, 1.22), (0.42, 0.28, 0.40), 0)

    # Arnés de correas oscuras en el pecho y hombros
    add_box((-0.11, -0.135, 1.25), (0.05, 0.015, 0.36), 6) # Tirante izq
    add_box((0.11, -0.135, 1.25), (0.05, 0.015, 0.36), 6)  # Tirante der
    add_box((0, -0.135, 1.28), (0.28, 0.015, 0.04), 6)     # Correa pectoral
    add_box((0, -0.135, 1.08), (0.34, 0.015, 0.05), 6)     # Cinturón frontal

    # Franja amarilla del traje en la cintura
    add_box((0, 0.01, 1.05), (0.43, 0.29, 0.04), 4)

    # Unidad de Control en el Pecho (Caja gris con pantalla verde y 2 botones rojos)
    add_box((0.02, -0.155, 1.26), (0.14, 0.03, 0.10), 1)
    # Pantalla LED Verde grande
    add_box((-0.02, -0.172, 1.26), (0.045, 0.01, 0.055), 7)
    # Dos Botones / LEDs Rojos apilados
    add_box((0.055, -0.172, 1.28), (0.025, 0.01, 0.025), 8)
    add_box((0.055, -0.172, 1.24), (0.025, 0.01, 0.025), 8)

    # ---------------------------------------------------------
    # 3. MOCHILA TRASERA ("BACKPACK UNIT")
    # ---------------------------------------------------------
    # Unidad de mochila rectangular naranja
    add_box((0, 0.23, 1.24), (0.34, 0.16, 0.42), 0)
    # Marco superior de la mochila
    add_box((0, 0.24, 1.45), (0.32, 0.14, 0.04), 1)

    # Rejillas de ventilación superiores negras/oscuras en el lado derecho
    for z_off in [1.38, 1.34, 1.30]:
        add_box((0.07, 0.315, z_off), (0.09, 0.01, 0.02), 6)

    # Luz indicadora LED verde superior izquierda
    add_box((-0.08, 0.315, 1.35), (0.035, 0.01, 0.035), 7)

    # Panel inferior gris con interruptor de energía rojo ("POWER INDICATOR")
    add_box((-0.03, 0.315, 1.16), (0.16, 0.01, 0.08), 1)
    add_box((-0.03, 0.322, 1.16), (0.05, 0.01, 0.03), 8) # Botón rojo deslizante

    # Conector de energía / fluido inferior ("POWER CONNECTOR")
    add_cylinder((0.08, 0.31, 1.08), 0.035, 0.04, 6, segs=10, rot_x=R(90))
    add_box((0.08, 0.33, 1.08), (0.04, 0.02, 0.04), 1)

    # ---------------------------------------------------------
    # 4. MANGUERA ROJA CURVADA ("RED HOSE")
    # Conecta la mochila trasera (lado derecho) y rodea la cadera hasta el arma
    # ---------------------------------------------------------
    hose_points = [
        (0.08, 0.33, 1.08),
        (0.16, 0.34, 0.98),
        (0.24, 0.28, 0.88),
        (0.29, 0.16, 0.84),
        (0.30, 0.02, 0.85),
        (0.28, -0.12, 0.90),
        (0.22, -0.25, 0.96),
        (0.16, -0.36, 1.04)
    ]
    for i in range(len(hose_points)-1):
        p1 = Vector(hose_points[i])
        p2 = Vector(hose_points[i+1])
        mid = (p1 + p2) * 0.5
        vec = p2 - p1
        length = vec.length
        # Segmento cilíndrico
        add_cylinder((mid.x, mid.y, mid.z), 0.028, length, 5, segs=8)

    # ---------------------------------------------------------
    # 5. BRAZOS ("ARMOUR GREEN" en hombros y antebrazos)
    # ---------------------------------------------------------
    for sign in [1, -1]:
        # Hombrera gruesa verde salvia ("ARMOR GREEN")
        add_box((0.26 * sign, 0, 1.38), (0.16, 0.20, 0.12), 1)
        # Biceps naranja con franja del traje
        add_box((0.26 * sign, 0, 1.25), (0.14, 0.17, 0.15), 0)

        # Antebrazo con armadura verde salvia ("ARMOUR SEGMENTS")
        add_box((0.27 * sign, -0.06 if sign == 1 else 0, 1.10), (0.15, 0.18, 0.18), 1)
        # Franja reflectante amarilla en el puño
        add_box((0.27 * sign, -0.06 if sign == 1 else 0, 1.00), (0.16, 0.19, 0.05), 4)
        # Guante protector oscuro
        add_box((0.26 * sign, -0.08 if sign == 1 else 0, 0.92), (0.13, 0.15, 0.13), 6)

    # ---------------------------------------------------------
    # 6. ARMA / HERRAMIENTA AISLADA ("EQUIPMENT ISOLATED")
    # Sostenida al frente en posición táctica como en la imagen 2
    # ---------------------------------------------------------
    gun_center = (0.05, -0.38, 1.08)

    # Cañón principal azul grisáceo cilíndrico ("WEAPON FRONT VIEW")
    add_cylinder((gun_center[0] - 0.14, gun_center[1], gun_center[2]), 0.045, 0.22, 9, segs=10, rot_y=R(90))
    # Boquilla / aro frontal
    add_cylinder((gun_center[0] - 0.26, gun_center[1], gun_center[2]), 0.055, 0.04, 10, segs=10, rot_y=R(90))

    # Receptor / Caja del arma (Metal azulino con ventana amarilla)
    add_box((gun_center[0], gun_center[1], gun_center[2]), (0.14, 0.09, 0.11), 9)
    # Ventana / Pantalla de estado amarilla lateral
    add_box((gun_center[0], gun_center[1] - 0.048, gun_center[2]), (0.06, 0.01, 0.04), 11)

    # Empuñadura frontal vertical
    add_cylinder((gun_center[0] - 0.06, gun_center[1], gun_center[2] - 0.09), 0.02, 0.10, 10, segs=8)

    # Empuñadura trasera / Culata marrón oxidada / acero
    add_box((gun_center[0] + 0.12, gun_center[1], gun_center[2] - 0.04), (0.12, 0.05, 0.08), 10)
    add_box((gun_center[0] + 0.18, gun_center[1], gun_center[2] - 0.08), (0.06, 0.04, 0.12), 10)

    # Conector de la manguera roja en la base del arma
    add_cylinder((gun_center[0] + 0.11, gun_center[1], gun_center[2] - 0.05), 0.026, 0.04, 5, segs=8, rot_x=R(90))

    # ---------------------------------------------------------
    # 7. PIERNAS Y BOTAS ("ARMOUR GREEN" en rodillas y botas)
    # ---------------------------------------------------------
    # Cintura / Pelvis naranja
    add_box((0, 0.01, 0.98), (0.36, 0.25, 0.12), 0)

    for sign in [1, -1]:
        # Muslo naranja
        add_box((0.13 * sign, 0.01, 0.77), (0.16, 0.19, 0.30), 0)

        # Rodillera gruesa verde salvia ("ARMOUR SEGMENTS")
        add_box((0.13 * sign, -0.09, 0.58), (0.15, 0.06, 0.13), 1)

        # Espinilla naranja
        add_box((0.13 * sign, 0.01, 0.44), (0.15, 0.17, 0.20), 0)

        # Franja amarilla reflectante en la pantorrilla
        add_box((0.13 * sign, 0.01, 0.32), (0.16, 0.18, 0.05), 4)

        # Bota robusta verde salvia / gris ("ARMOUR GREEN")
        add_box((0.13 * sign, -0.04, 0.16), (0.17, 0.24, 0.22), 1)
        # Suela y puntera reforzada
        add_box((0.13 * sign, -0.09, 0.06), (0.18, 0.14, 0.08), 2)
        add_box((0.13 * sign, -0.04, 0.02), (0.18, 0.26, 0.04), 2)

    bm.to_mesh(mesh)
    bm.free()

    for m in mat_order:
        mesh.materials.append(m)

    obj = bpy.data.objects.new("SK_Firefighter_Official", mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj

# -------------------------------------------------------------
# ARMATURE BIPEDAL PARA POSADO Y EXPORTACIÓN
# -------------------------------------------------------------
def create_rig(name="Armature_Official"):
    arm_data = bpy.data.armatures.new(name)
    arm_obj = bpy.data.objects.new(name, arm_data)
    bpy.context.scene.collection.objects.link(arm_obj)
    bpy.context.view_layer.objects.active = arm_obj
    
    bpy.ops.object.mode_set(mode='EDIT')
    eb = arm_data.edit_bones

    root = eb.new('root')
    root.head = (0, 0, 0)
    root.tail = (0, 0, 0.1)

    pelvis = eb.new('pelvis')
    pelvis.head = (0, 0, 0.95)
    pelvis.tail = (0, 0, 1.05)
    pelvis.parent = root

    spine1 = eb.new('spine_01')
    spine1.head = (0, 0, 1.05)
    spine1.tail = (0, 0, 1.25)
    spine1.parent = pelvis

    spine2 = eb.new('spine_02')
    spine2.head = (0, 0, 1.25)
    spine2.tail = (0, 0, 1.45)
    spine2.parent = spine1

    neck = eb.new('neck_01')
    neck.head = (0, 0, 1.45)
    neck.tail = (0, 0, 1.55)
    neck.parent = spine2

    head = eb.new('head')
    head.head = (0, 0, 1.55)
    head.tail = (0, 0, 1.82)
    head.parent = neck

    for side, sign in [('_l', 1), ('_r', -1)]:
        clav = eb.new(f'clavicle{side}')
        clav.head = (0, 0, 1.42)
        clav.tail = (0.16 * sign, 0, 1.44)
        clav.parent = spine2

        uarm = eb.new(f'upperarm{side}')
        uarm.head = (0.20 * sign, 0, 1.42)
        uarm.tail = (0.42 * sign, -0.05, 1.18)
        uarm.parent = clav

        larm = eb.new(f'lowerarm{side}')
        larm.head = (0.42 * sign, -0.05, 1.18)
        larm.tail = (0.35 * sign, -0.25, 1.02)
        larm.parent = uarm

        hand = eb.new(f'hand{side}')
        hand.head = (0.35 * sign, -0.25, 1.02)
        hand.tail = (0.25 * sign, -0.32, 0.96)
        hand.parent = larm

    for side, sign in [('_l', 1), ('_r', -1)]:
        thigh = eb.new(f'thigh{side}')
        thigh.head = (0.13 * sign, 0, 0.92)
        thigh.tail = (0.14 * sign, 0.02, 0.50)
        thigh.parent = pelvis

        calf = eb.new(f'calf{side}')
        calf.head = (0.14 * sign, 0.02, 0.50)
        calf.tail = (0.14 * sign, -0.01, 0.14)
        calf.parent = thigh

        foot = eb.new(f'foot{side}')
        foot.head = (0.14 * sign, -0.01, 0.14)
        foot.tail = (0.14 * sign, -0.16, 0.0)
        foot.parent = calf

    bpy.ops.object.mode_set(mode='OBJECT')
    return arm_obj

def skin_mesh(mesh_obj, arm_obj):
    mesh_obj.select_set(True)
    arm_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    mod = mesh_obj.modifiers.get("Armature") or mesh_obj.modifiers.new("Armature", 'ARMATURE')
    mod.object = arm_obj

# -------------------------------------------------------------
# ESTUDIO DE ILUMINACIÓN Y CÁMARA (ESTILO PSX / BLUEPRINT)
# -------------------------------------------------------------
def setup_lighting(scene):
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'High Contrast'

    # Fondo neutro oscuro estilo espacio / hangar
    bg_mesh = bpy.data.meshes.new("StudioGrid")
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=25)
    bm.to_mesh(bg_mesh)
    bm.free()
    bg_obj = bpy.data.objects.new("StudioGrid", bg_mesh)
    bg_obj.location = (0, 0, -0.01)
    scene.collection.objects.link(bg_obj)
    
    mat_floor = create_pbr_material("M_StudioFloorDark", (0.02, 0.025, 0.03, 1.0), metallic=0.3, roughness=0.35)
    bg_obj.data.materials.append(mat_floor)

    target = bpy.data.objects.new("LightTarget", None)
    target.location = (0, 0, 1.0)
    scene.collection.objects.link(target)

    def add_light(name, pos, energy, color, size=2.5):
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

    # Luces para visibilidad 360° nítida
    add_light("FrontKey", (2.4, -3.2, 2.5), 1100, (1.0, 0.98, 0.94), size=2.8)
    add_light("BackKey", (-2.2, 3.2, 2.5), 1200, (0.95, 0.98, 1.0), size=2.8)
    add_light("RimLeft", (-3.2, -0.5, 2.0), 750, (0.2, 0.85, 1.0), size=2.0)
    add_light("FillRight", (3.2, 0.5, 1.8), 550, (1.0, 0.75, 0.35), size=2.5)

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

    quad = Image.new("RGBA", (1920, 1080), (16, 20, 26, 255))
    quad.paste(im_front, (0, 0))
    quad.paste(im_back, (960, 0))
    quad.paste(im_side, (0, 540))
    quad.paste(im_action, (960, 540))

    draw = ImageDraw.Draw(quad)
    
    # Cuadrícula técnica estilo blueprint
    line_col = (45, 65, 88, 220)
    draw.line([(960, 0), (960, 1080)], fill=line_col, width=2)
    draw.line([(0, 540), (1920, 540)], fill=line_col, width=2)

    # Etiquetas según la hoja de modelo oficial
    labels = [
        ("VISTA 1: FRONT VIEW (REINFORCED VISOR / CHEST UI)", (25, 20)),
        ("VISTA 2: BACK VIEW (BACKPACK UNIT / RED HOSE)", (985, 20)),
        ("VISTA 3: SIDE VIEW (PROFILE / POWER CONNECTOR)", (25, 560)),
        ("VISTA 4: ACTION 3/4 (IN-GAME SCREENSHOT MATCH)", (985, 560))
    ]
    for lbl, pos in labels:
        draw.rectangle([pos[0]-6, pos[1]-4, pos[0]+460, pos[1]+24], fill=(12, 16, 24, 240), outline=(55, 75, 100, 255), width=1)
        draw.text(pos, lbl, fill=(245, 248, 255, 255))

    # Banner superior
    draw.rectangle([480, 515, 1440, 565], fill=(18, 22, 32, 245), outline=(235, 120, 25, 255), width=2)
    draw.text((505, 528), "ASTRA HAZARD - BOMBERO ESPACIAL (MATCH 1:1 CON MODEL SHEET)", fill=(255, 180, 20, 255))

    quad.save(out_final)
    print(f"  [OK] Model Sheet Compositado: {out_final}")

# -------------------------------------------------------------
# EJECUCIÓN PRINCIPAL
# -------------------------------------------------------------
def main():
    print("\n=======================================================")
    print(">>> GENERANDO PERSONAJE 1:1 FIEL A LAS IMÁGENES SUBIDAS")
    print("=======================================================")
    clear_scene()
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.image_settings.file_format = 'PNG'

    mats = create_reference_materials()
    setup_lighting(scene)

    # 1. Crear personaje y rig
    arm = create_rig("Armature_Official_Firefighter")
    char_obj = build_character_from_reference(mats)
    skin_mesh(char_obj, arm)

    # 2. Rutas de Renders
    v1_front = os.path.join(RENDERS_DIR, "ref_match_v1_front.png")
    v2_back = os.path.join(RENDERS_DIR, "ref_match_v2_back.png")
    v3_side = os.path.join(RENDERS_DIR, "ref_match_v3_side.png")
    v4_action = os.path.join(RENDERS_DIR, "ref_match_v4_action.png")

    print("  Renderizando Vista Frontal (Front View)...")
    render_camera_shot((0.0, -3.8, 1.00), (0.0, 0.0, 0.95), 32.0, v1_front)

    print("  Renderizando Vista Trasera (Back View con Mochila y Manguera)...")
    render_camera_shot((0.0, 3.8, 1.00), (0.0, 0.0, 0.95), 32.0, v2_back)

    print("  Renderizando Vista Lateral (Side View)...")
    render_camera_shot((3.8, 0.0, 1.00), (0.0, 0.0, 0.95), 32.0, v3_side)

    print("  Renderizando Vista Acción 3/4 (Match con Screenshot In-Game)...")
    render_camera_shot((2.4, -2.4, 1.25), (0.0, 0.0, 0.95), 34.0, v4_action)

    # 3. Composición en Hoja de Modelo 4 Vistas
    out_final = os.path.join(RENDERS_DIR, "SK_Firefighter_Official_4views.png")
    composite_model_sheet(v1_front, v2_back, v3_side, v4_action, out_final)

    # Copiar a Brain Directory para previsualización inmediata
    brain_copy = os.path.join(BRAIN_DIR, "SK_Firefighter_Official_4views.png")
    shutil.copy2(out_final, brain_copy)
    print(f"  [OK] Copiado a Brain Artifact: {brain_copy}")

    # 4. Exportar FBX Limpio para Unreal Engine 5
    fbx_out = os.path.join(FBX_DIR, "SK_Firefighter_Official.fbx")
    bpy.ops.object.select_all(action='DESELECT')
    arm.select_set(True)
    char_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm

    bpy.ops.export_scene.fbx(
        filepath=fbx_out,
        check_existing=False,
        use_selection=True,
        add_leaf_bones=False,
        axis_forward='-Y',
        axis_up='Z',
        apply_scale_options='FBX_SCALE_ALL'
    )
    print(f"  [OK] Exportado FBX Oficial para UE5: {fbx_out}")

    blend_out = os.path.join(ART_DIR, "Blender", "SK_Firefighter_Official.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_out)
    print(f"  [OK] Archivo Blend oficial guardado: {blend_out}")
    print("\n>>> ¡GENERACIÓN Y RENDERIZADO COMPLETADO!")

if __name__ == "__main__":
    main()

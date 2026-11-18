"""
generar_lote3_personajes.py
Generador automatizado para Astra Hazard: Rescue Squad
Lote 3: Personajes (SK_Firefighter_SpaceSuit & SK_TestDummy_Ragdoll)
Estilo: Low-Poly PSX Industrial con Texturas Cartoon y Acabados PBR.
Versión Pro: Standard View Transform (colores vivos), iluminación Track-To 360° y encuadre 32mm perfecto.
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
# MATERIALES PBR ESTILO PSX CARTOON (VIBRANTES & SATURADOS)
# -------------------------------------------------------------
def get_or_create_material(name, base_color, metallic=0.05, roughness=0.35, emission=None, emission_strength=1.0):
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

def create_firefighter_materials():
    return {
        # Rojo bombero de alta saturación
        'red': get_or_create_material("M_Suit_RescueRed", (0.82, 0.05, 0.02, 1.0), metallic=0.04, roughness=0.35),
        # Amarillo reflectante de alta visibilidad
        'yellow': get_or_create_material("M_Suit_YellowHighVis", (1.0, 0.85, 0.0, 1.0), metallic=0.02, roughness=0.20),
        # Goma aislante oscura de botas y guantes
        'dark_rubber': get_or_create_material("M_Suit_DarkRubber", (0.04, 0.04, 0.05, 1.0), metallic=0.1, roughness=0.60),
        # Marcos metálicos y hebillas
        'steel': get_or_create_material("M_Suit_SteelTrim", (0.70, 0.73, 0.78, 1.0), metallic=0.95, roughness=0.18),
        # Botellas de oxígeno amarillas
        'tank_yellow': get_or_create_material("M_Suit_TankYellow", (1.0, 0.70, 0.02, 1.0), metallic=0.25, roughness=0.25),
        # Visor CRT cian brillante retro
        'visor_crt': get_or_create_material("M_Suit_VisorCRT", (0.02, 0.90, 1.0, 1.0), metallic=0.05, roughness=0.05, emission=(0.05, 0.95, 1.0, 1.0), emission_strength=4.0),
        # Linterna frontal
        'headlamp': get_or_create_material("M_Suit_Headlamp", (1.0, 0.98, 0.85, 1.0), metallic=0.0, roughness=0.1, emission=(1.0, 0.98, 0.85, 1.0), emission_strength=8.0),
        # Manómetro
        'gauge_face': get_or_create_material("M_Suit_Gauge", (0.95, 0.95, 0.92, 1.0), metallic=0.0, roughness=0.25),
        'needle_red': get_or_create_material("M_Suit_Needle", (1.0, 0.02, 0.02, 1.0), metallic=0.0, roughness=0.2, emission=(1.0, 0.0, 0.0, 1.0), emission_strength=3.0)
    }

def create_dummy_materials():
    return {
        # Naranja de prueba automotriz
        'orange_body': get_or_create_material("M_Dummy_SafetyOrange", (0.98, 0.40, 0.02, 1.0), metallic=0.05, roughness=0.35),
        # Franjas blancas de cuadrícula
        'white_trim': get_or_create_material("M_Dummy_WhiteCheck", (0.95, 0.95, 0.95, 1.0), metallic=0.05, roughness=0.30),
        # Juntas negras de flexión
        'black_joints': get_or_create_material("M_Dummy_BlackJoints", (0.03, 0.03, 0.04, 1.0), metallic=0.10, roughness=0.60),
        # Dianas de choque
        'target_yellow': get_or_create_material("M_Dummy_TargetYellow", (1.0, 0.88, 0.0, 1.0), metallic=0.05, roughness=0.25, emission=(1.0, 0.88, 0.0, 1.0), emission_strength=1.5),
        'target_black': get_or_create_material("M_Dummy_TargetBlack", (0.02, 0.02, 0.02, 1.0), metallic=0.1, roughness=0.5),
        # Visor oscuro
        'visor_dark': get_or_create_material("M_Dummy_VisorDark", (0.08, 0.10, 0.12, 1.0), metallic=0.8, roughness=0.12)
    }

# -------------------------------------------------------------
# ARMATURE ESTÁNDAR BIPEDAL
# -------------------------------------------------------------
def create_biped_armature(name="Armature_Biped"):
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
    pelvis.head = (0, 0, 0.92)
    pelvis.tail = (0, 0, 1.02)
    pelvis.parent = root

    spine1 = eb.new('spine_01')
    spine1.head = (0, 0, 1.02)
    spine1.tail = (0, 0, 1.22)
    spine1.parent = pelvis

    spine2 = eb.new('spine_02')
    spine2.head = (0, 0, 1.22)
    spine2.tail = (0, 0, 1.42)
    spine2.parent = spine1

    neck = eb.new('neck_01')
    neck.head = (0, 0, 1.42)
    neck.tail = (0, 0, 1.52)
    neck.parent = spine2

    head = eb.new('head')
    head.head = (0, 0, 1.52)
    head.tail = (0, 0, 1.80)
    head.parent = neck

    for side, sign in [('_l', 1), ('_r', -1)]:
        clav = eb.new(f'clavicle{side}')
        clav.head = (0, 0, 1.40)
        clav.tail = (0.16 * sign, 0, 1.42)
        clav.parent = spine2

        uarm = eb.new(f'upperarm{side}')
        uarm.head = (0.20 * sign, 0, 1.40)
        uarm.tail = (0.44 * sign, 0, 1.16)
        uarm.parent = clav

        larm = eb.new(f'lowerarm{side}')
        larm.head = (0.44 * sign, 0, 1.16)
        larm.tail = (0.66 * sign, 0, 0.94)
        larm.parent = uarm

        hand = eb.new(f'hand{side}')
        hand.head = (0.66 * sign, 0, 0.94)
        hand.tail = (0.78 * sign, 0, 0.86)
        hand.parent = larm

    for side, sign in [('_l', 1), ('_r', -1)]:
        thigh = eb.new(f'thigh{side}')
        thigh.head = (0.13 * sign, 0, 0.90)
        thigh.tail = (0.14 * sign, 0.02, 0.48)
        thigh.parent = pelvis

        calf = eb.new(f'calf{side}')
        calf.head = (0.14 * sign, 0.02, 0.48)
        calf.tail = (0.14 * sign, -0.01, 0.12)
        calf.parent = thigh

        foot = eb.new(f'foot{side}')
        foot.head = (0.14 * sign, -0.01, 0.12)
        foot.tail = (0.14 * sign, -0.16, 0.0)
        foot.parent = calf

    bpy.ops.object.mode_set(mode='OBJECT')
    return arm_obj

# -------------------------------------------------------------
# CONSTRUCCIÓN DE MALLA: BOMBERO ESPACIAL (SK_Firefighter_SpaceSuit)
# -------------------------------------------------------------
def build_firefighter_mesh(materials):
    mesh = bpy.data.meshes.new("SK_Firefighter_SpaceSuit_Mesh")
    bm = bmesh.new()

    mat_list = [
        materials['red'],          # 0: Rojo Bombero
        materials['yellow'],       # 1: Amarillo Reflectante
        materials['dark_rubber'],  # 2: Goma Oscura
        materials['steel'],        # 3: Titanio / Marcos
        materials['tank_yellow'],  # 4: Tanque Amarillo
        materials['visor_crt'],    # 5: Visor CRT Cian
        materials['headlamp'],     # 6: Linterna Frontal
        materials['gauge_face'],   # 7: Manómetro
        materials['needle_red']    # 8: Aguja Manómetro
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

    def add_cylinder(center, radius, depth, mat_idx, segs=12):
        ret = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segs, radius1=radius, radius2=radius, depth=depth)
        verts = ret['verts']
        bmesh.ops.translate(bm, vec=center, verts=verts)
        for f in bm.faces:
            if f.verts[0] in verts:
                f.material_index = mat_idx
        return verts

    # 1. Torso y Chaquetón de Bombero Espacial
    add_box((0, 0, 1.24), (0.44, 0.30, 0.44), 0)
    add_box((0, 0, 1.32), (0.45, 0.31, 0.08), 1)
    add_box((0, 0, 1.14), (0.45, 0.31, 0.07), 1)
    add_cylinder((0, 0, 1.48), 0.17, 0.08, 2, segs=12)
    add_box((0, -0.155, 1.24), (0.06, 0.02, 0.42), 3)
    add_box((0, 0, 1.03), (0.43, 0.29, 0.08), 2)
    add_box((0, -0.15, 1.03), (0.09, 0.02, 0.09), 3)
    add_box((-0.20, -0.02, 1.03), (0.06, 0.12, 0.09), 2)
    add_box((0.20, -0.02, 1.03), (0.06, 0.12, 0.09), 2)

    # 2. Casco de Bombero Espacial con Cresta y Visor Curvo CRT
    add_box((0, 0.01, 1.66), (0.35, 0.36, 0.32), 0)
    add_box((0, 0.02, 1.83), (0.08, 0.34, 0.05), 3)
    add_box((0, -0.165, 1.65), (0.26, 0.04, 0.18), 5)
    add_box((0, -0.15, 1.65), (0.29, 0.03, 0.21), 3)
    add_box((0, -0.17, 1.80), (0.10, 0.06, 0.05), 2)
    add_box((0, -0.20, 1.80), (0.08, 0.015, 0.04), 6)

    # 3. Tanque de Oxígeno Doble a la Espalda (Dorsal Pack)
    add_box((0, 0.19, 1.25), (0.34, 0.06, 0.38), 2)
    add_box((-0.12, 0.02, 1.40), (0.07, 0.32, 0.04), 2)
    add_box((0.12, 0.02, 1.40), (0.07, 0.32, 0.04), 2)
    add_cylinder((-0.09, 0.28, 1.25), 0.08, 0.44, 4, segs=12)
    add_cylinder((0.09, 0.28, 1.25), 0.08, 0.44, 4, segs=12)
    add_cylinder((-0.09, 0.28, 1.34), 0.083, 0.07, 1, segs=12)
    add_cylinder((0.09, 0.28, 1.34), 0.083, 0.07, 1, segs=12)
    add_cylinder((-0.09, 0.28, 1.50), 0.035, 0.08, 3, segs=8)
    add_cylinder((0.09, 0.28, 1.50), 0.035, 0.08, 3, segs=8)
    add_box((0, 0.28, 1.50), (0.18, 0.04, 0.03), 3)
    add_cylinder((0.16, 0.22, 1.54), 0.025, 0.16, 2, segs=8)
    add_cylinder((0.18, 0.26, 1.44), 0.045, 0.03, 7, segs=12)
    add_box((0.18, 0.28, 1.44), (0.005, 0.015, 0.03), 8)

    # 4. Brazos y Guantes Térmicos de Rescate
    for sign in [1, -1]:
        add_box((0.27 * sign, 0, 1.41), (0.17, 0.21, 0.13), 0)
        add_box((0.27 * sign, 0, 1.43), (0.18, 0.22, 0.04), 1)
        add_box((0.34 * sign, 0, 1.28), (0.14, 0.16, 0.22), 0)
        add_box((0.44 * sign, 0, 1.15), (0.15, 0.16, 0.06), 1)
        add_box((0.44 * sign, 0, 1.07), (0.13, 0.14, 0.16), 0)
        add_box((0.55 * sign, 0, 0.93), (0.13, 0.15, 0.17), 2)
        add_box((0.56 * sign, 0, 0.95), (0.14, 0.16, 0.04), 3)

    # 5. Caderas, Piernas y Botas Magnéticas
    add_box((0, 0, 0.95), (0.40, 0.26, 0.18), 0)

    for sign in [1, -1]:
        add_box((0.14 * sign, 0, 0.73), (0.16, 0.19, 0.32), 0)
        add_box((0.14 * sign, 0, 0.67), (0.17, 0.20, 0.06), 1)
        add_box((0.14 * sign, -0.10, 0.51), (0.14, 0.06, 0.12), 2)
        add_box((0.14 * sign, 0, 0.37), (0.15, 0.17, 0.24), 0)
        add_box((0.14 * sign, -0.04, 0.15), (0.17, 0.25, 0.22), 2)
        add_box((0.14 * sign, -0.11, 0.05), (0.17, 0.13, 0.06), 3)
        add_box((0.14 * sign, -0.04, 0.02), (0.18, 0.26, 0.04), 3)

    bm.to_mesh(mesh)
    bm.free()

    for m in mat_list:
        mesh.materials.append(m)

    obj = bpy.data.objects.new("SK_Firefighter_SpaceSuit", mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj

# -------------------------------------------------------------
# CONSTRUCCIÓN DE MALLA: MUÑECO DE PRUEBAS (SK_TestDummy_Ragdoll)
# -------------------------------------------------------------
def build_dummy_mesh(materials):
    mesh = bpy.data.meshes.new("SK_TestDummy_Ragdoll_Mesh")
    bm = bmesh.new()

    mat_list = [
        materials['orange_body'],  # 0: Naranja de Seguridad
        materials['white_trim'],   # 1: Blanco Cuadrículas
        materials['black_joints'], # 2: Juntas / Articulaciones Negras
        materials['target_yellow'],# 3: Diana Amarillo
        materials['target_black'], # 4: Diana Negro
        materials['visor_dark']    # 5: Visor Calibración
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

    def add_cylinder(center, radius, depth, mat_idx, segs=12):
        ret = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segs, radius1=radius, radius2=radius, depth=depth)
        verts = ret['verts']
        bmesh.ops.translate(bm, vec=center, verts=verts)
        for f in bm.faces:
            if f.verts[0] in verts:
                f.material_index = mat_idx
        return verts

    # 1. Torso Naranja con Diana de Impacto Central
    add_box((0, 0, 1.24), (0.42, 0.26, 0.44), 0)
    add_box((0, 0, 1.34), (0.43, 0.27, 0.08), 1)
    add_box((0, 0, 1.14), (0.43, 0.27, 0.07), 1)
    add_cylinder((0, -0.135, 1.34), 0.075, 0.015, 3, segs=12)
    add_cylinder((0, -0.142, 1.34), 0.038, 0.02, 4, segs=12)
    add_cylinder((0, 0.135, 1.34), 0.075, 0.015, 3, segs=12)
    add_cylinder((0, 0.142, 1.34), 0.038, 0.02, 4, segs=12)

    # 2. Cabeza Esférica / Low-Poly con Visor de Sensores
    add_cylinder((0, 0, 1.48), 0.10, 0.09, 2, segs=8)
    add_box((0, 0.01, 1.66), (0.32, 0.32, 0.30), 0)
    add_box((0, 0.01, 1.66), (0.33, 0.33, 0.07), 1)
    add_box((0, -0.155, 1.66), (0.24, 0.04, 0.15), 5)
    add_cylinder((-0.165, 0.01, 1.66), 0.055, 0.015, 3, segs=10)
    add_cylinder((0.165, 0.01, 1.66), 0.055, 0.015, 3, segs=10)

    # 3. Articulaciones y Brazos
    for sign in [1, -1]:
        add_cylinder((0.25 * sign, 0, 1.41), 0.085, 0.13, 2, segs=10)
        add_box((0.33 * sign, 0, 1.28), (0.13, 0.15, 0.20), 0)
        add_cylinder((0.39 * sign, 0, 1.15), 0.07, 0.11, 2, segs=10)
        add_box((0.44 * sign, 0, 1.05), (0.12, 0.13, 0.17), 1)
        add_box((0.55 * sign, 0, 0.93), (0.11, 0.13, 0.15), 2)

    # 4. Pelvis, Piernas y Pies
    add_box((0, 0, 0.95), (0.38, 0.24, 0.18), 2)

    for sign in [1, -1]:
        add_cylinder((0.14 * sign, 0, 0.86), 0.085, 0.09, 2, segs=10)
        add_box((0.14 * sign, 0, 0.72), (0.14, 0.17, 0.28), 0)
        add_cylinder((0.14 * sign, -0.07, 0.52), 0.065, 0.09, 3, segs=10)
        add_cylinder((0.14 * sign, -0.09, 0.52), 0.032, 0.06, 4, segs=10)
        add_box((0.14 * sign, 0, 0.36), (0.13, 0.15, 0.24), 1)
        add_cylinder((0.14 * sign, 0, 0.19), 0.065, 0.09, 2, segs=10)
        add_box((0.14 * sign, -0.04, 0.08), (0.15, 0.24, 0.15), 2)

    bm.to_mesh(mesh)
    bm.free()

    for m in mat_list:
        mesh.materials.append(m)

    obj = bpy.data.objects.new("SK_TestDummy_Ragdoll", mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj

# -------------------------------------------------------------
# ASIGNACIÓN DE PESOS AL ESQUELETO
# -------------------------------------------------------------
def skin_mesh_to_armature(mesh_obj, arm_obj):
    mesh_obj.select_set(True)
    arm_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    
    mod = mesh_obj.modifiers.get("Armature")
    if not mod:
        mod = mesh_obj.modifiers.new("Armature", 'ARMATURE')
        mod.object = arm_obj

# -------------------------------------------------------------
# ESTUDIO DE ILUMINACIÓN 360° CON COLORES VIVOS
# -------------------------------------------------------------
def setup_lighting(scene):
    # Forzar vista estándar para evitar desaturación de colores cartoon
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'High Contrast'

    bg_mesh = bpy.data.meshes.new("StudioBackdrop")
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=30)
    bm.to_mesh(bg_mesh)
    bm.free()
    bg_obj = bpy.data.objects.new("StudioBackdrop", bg_mesh)
    bg_obj.location = (0, 0, -0.01)
    scene.collection.objects.link(bg_obj)
    
    mat_floor = get_or_create_material("M_StudioFloor", (0.018, 0.020, 0.025, 1.0), metallic=0.2, roughness=0.35)
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

    # 1. Front Key Light (Cálida potente)
    add_light("FrontKey", (2.2, -3.2, 2.4), 850, (1.0, 0.98, 0.94), size=2.8)
    # 2. Back Key Light (Ilumina los tanques O2 desde atrás)
    add_light("BackKey", (-2.0, 3.2, 2.4), 950, (0.96, 0.98, 1.0), size=2.8)
    # 3. Rim Lateral Cian
    add_light("RimCyan", (-3.2, -0.5, 2.0), 600, (0.1, 0.85, 1.0), size=2.0)
    # 4. Fill Lateral Ámbar
    add_light("FillAmber", (3.2, 0.5, 1.8), 450, (1.0, 0.75, 0.35), size=2.5)

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

def composite_quadrant(v1_path, v2_path, v3_path, v4_path, out_final, title_text):
    im1 = Image.open(v1_path)
    im2 = Image.open(v2_path)
    im3 = Image.open(v3_path)
    im4 = Image.open(v4_path)

    quad = Image.new("RGBA", (1920, 1080), (12, 14, 20, 255))
    quad.paste(im1, (0, 0))
    quad.paste(im2, (960, 0))
    quad.paste(im3, (0, 540))
    quad.paste(im4, (960, 540))

    draw = ImageDraw.Draw(quad)
    
    line_col = (45, 60, 85, 220)
    draw.line([(960, 0), (960, 1080)], fill=line_col, width=2)
    draw.line([(0, 540), (1920, 540)], fill=line_col, width=2)

    labels = [
        ("VISTA 1: FRONTAL COMPLETA", (25, 20)),
        ("VISTA 2: TRASERA (TANQUE O2 / ARNÉS)", (985, 20)),
        ("VISTA 3: PERSPECTIVA ACCIÓN 3/4", (25, 560)),
        ("VISTA 4: PRIMER PLANO / DETALLE VISOR", (985, 560))
    ]
    for lbl, pos in labels:
        draw.rectangle([pos[0]-5, pos[1]-3, pos[0]+390, pos[1]+24], fill=(12, 16, 24, 230), outline=(50, 70, 95, 255), width=1)
        draw.text(pos, lbl, fill=(240, 245, 255, 255))

    draw.rectangle([500, 515, 1420, 565], fill=(18, 22, 32, 245), outline=(255, 185, 0, 255), width=2)
    draw.text((520, 528), title_text, fill=(255, 215, 0, 255))

    quad.save(out_final)
    print(f"  [OK] Cuadrante compositado: {out_final}")

# -------------------------------------------------------------
# EXPORTACIÓN
# -------------------------------------------------------------
def export_character(char_name, build_func, mats_func, title_text):
    print(f"\n=======================================================")
    print(f">>> Generando y Renderizando: {char_name}...")
    print(f"=======================================================")
    clear_scene()
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.image_settings.file_format = 'PNG'

    mats = mats_func()
    setup_lighting(scene)

    # 1. Armature & Mesh
    arm = create_biped_armature(f"Armature_{char_name}")
    mesh_obj = build_func(mats)
    skin_mesh_to_armature(mesh_obj, arm)

    # 2. Renders de 4 Vistas con Lente 32mm para Encuadre de Cuerpo Completo
    v1 = os.path.join(RENDERS_DIR, f"{char_name}_v1_front.png")
    v2 = os.path.join(RENDERS_DIR, f"{char_name}_v2_back.png")
    v3 = os.path.join(RENDERS_DIR, f"{char_name}_v3_action.png")
    v4 = os.path.join(RENDERS_DIR, f"{char_name}_v4_detail.png")

    print(f"  Renderizando 4 vistas...")
    # Frontal con lente 32mm centrada
    render_camera_shot((0.0, -3.8, 0.95), (0.0, 0.0, 0.92), 32.0, v1)
    # Trasera iluminada con lente 32mm
    render_camera_shot((0.0, 3.8, 0.95), (0.0, 0.0, 0.92), 32.0, v2)
    # Acción 3/4
    render_camera_shot((2.6, -2.6, 1.25), (0.0, 0.0, 0.90), 34.0, v3)
    # Detalle / Primer plano de Casco y Visor
    render_camera_shot((0.0, -1.25, 1.64), (0.0, 0.0, 1.62), 52.0, v4)

    # 3. Composición 4-Quadrant
    out_quad = os.path.join(RENDERS_DIR, f"{char_name}_4views.png")
    composite_quadrant(v1, v2, v3, v4, out_quad, title_text)

    # Copiar al brain directory para previsualización inmediata en el chat
    brain_copy = os.path.join(BRAIN_DIR, f"{char_name}_4views.png")
    shutil.copy2(out_quad, brain_copy)
    print(f"  [OK] Copiado a Brain Artifact: {brain_copy}")

    # 4. Exportar FBX Limpio para Unreal Engine 5
    fbx_out = os.path.join(FBX_DIR, f"{char_name}.fbx")
    bpy.ops.object.select_all(action='DESELECT')
    arm.select_set(True)
    mesh_obj.select_set(True)
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
    print(f"  [OK] Exportado FBX para UE5: {fbx_out}")

    blend_out = os.path.join(ART_DIR, "Blender", f"{char_name}.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_out)
    print(f"  [OK] Archivo Blend maestro guardado: {blend_out}")

if __name__ == "__main__":
    export_character(
        "SK_Firefighter_SpaceSuit",
        build_firefighter_mesh,
        create_firefighter_materials,
        "ASTRA HAZARD - SK_FIREFIGHTER_SPACESUIT (PBR LOW-POLY)"
    )

    export_character(
        "SK_TestDummy_Ragdoll",
        build_dummy_mesh,
        create_dummy_materials,
        "ASTRA HAZARD - SK_TESTDUMMY_RAGDOLL (PHYSICAL RIG)"
    )

    print("\n>>> [ASTRA HAZARD] ¡Lote 3 completado y refinado con éxito!")

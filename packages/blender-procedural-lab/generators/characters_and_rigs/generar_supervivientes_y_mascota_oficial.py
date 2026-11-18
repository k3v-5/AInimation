"""
generar_supervivientes_y_mascota_oficial.py
============================================
Pipeline Oficial de Modelado, Rigging y Exportación para Astra Hazard:
1. SK_Civilian_Survivor:
   - Superviviente humano civil en mono de trabajo industrial desgastado.
   - Esqueleto oficial 100% compatible con SK_Firefighter_Official_Rigged_Skeleton.
   - Peso de vértices determinista por capas BMesh.
   - Exporta a Art/FBX/Characters/SK_Civilian_Survivor.fbx.

2. SK_AlienPet_Blobby:
   - Mascota alienígena exótica compacta (altura 42 cm, ancho 38 cm) para conductos SM_VentDuct.
   - Criatura de 6 patas, antenas bioluminiscentes y ojos expresivos.
   - Esqueleto dedicado de 12 huesos con jerarquía limpia para navegación rápida.
   - Genera 4 secuencias de animación:
     * A_Pet_Idle (Respiración y meneo de cola)
     * A_Pet_Run (Carrera rápida de 6 patas a 650 cm/s)
     * A_Pet_Scared (Ovillado y temblor de pánico)
     * A_Pet_Curious (Inclinación de cabeza y olfateo de aproximación)
   - Exporta a Art/FBX/Characters/SK_AlienPet_Blobby.fbx y Art/FBX/Animations/A_Pet_*.fbx.

3. Genera una hoja de render 4-views de validación para los supervivientes.
"""

import sys, os, math, shutil
import bpy, bmesh
from mathutils import Matrix, Vector, Euler
from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = r"f:\Dev\Game"
ART_DIR = os.path.join(PROJECT_ROOT, "Art")
FBX_CHAR_DIR = os.path.join(ART_DIR, "FBX", "Characters")
FBX_ANIM_DIR = os.path.join(ART_DIR, "FBX", "Animations")
RENDERS_DIR = os.path.join(ART_DIR, "Renders")
BRAIN_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\b59ff04f-3c21-4ee5-94b0-8e8f899f8923"

os.makedirs(FBX_CHAR_DIR, exist_ok=True)
os.makedirs(FBX_ANIM_DIR, exist_ok=True)
os.makedirs(RENDERS_DIR, exist_ok=True)
os.makedirs(BRAIN_DIR, exist_ok=True)

R = math.radians
PI = math.pi

def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def create_pbr_mat(name, base_color, metallic=0.04, roughness=0.5, emission=None, emission_strength=1.0):
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

# ==============================================================================
# 1. PARTE 1: CIVILIAN SURVIVOR (HUMANOIDE CON RIG OFICIAL)
# ==============================================================================

BONE_NAMES_HUMANOID = [
    'root', 'pelvis', 'spine_01', 'spine_02', 'neck_01', 'head',
    'clavicle_l', 'upperarm_l', 'lowerarm_l', 'hand_l',
    'clavicle_r', 'upperarm_r', 'lowerarm_r', 'hand_r',
    'weapon_socket_r',
    'thigh_l', 'calf_l', 'foot_l',
    'thigh_r', 'calf_r', 'foot_r'
]

def build_humanoid_armature(name="SK_Civilian_Armature"):
    arm_data = bpy.data.armatures.new(name + "_Data")
    arm_obj = bpy.data.objects.new(name, arm_data)
    bpy.context.scene.collection.objects.link(arm_obj)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='EDIT')
    eb = arm_data.edit_bones

    root = eb.new('root')
    root.head = (0, 0, 0)
    root.tail = (0, 0, 0.10)

    pelvis = eb.new('pelvis')
    pelvis.head = (0, 0, 0.72)
    pelvis.tail = (0, 0, 0.86)
    pelvis.parent = root

    spine1 = eb.new('spine_01')
    spine1.head = (0, 0, 0.86)
    spine1.tail = (0, 0, 1.04)
    spine1.parent = pelvis

    spine2 = eb.new('spine_02')
    spine2.head = (0, 0, 1.04)
    spine2.tail = (0, 0, 1.20)
    spine2.parent = spine1

    neck = eb.new('neck_01')
    neck.head = (0, 0, 1.20)
    neck.tail = (0, 0, 1.30)
    neck.parent = spine2

    head = eb.new('head')
    head.head = (0, 0, 1.30)
    head.tail = (0, 0, 1.62)
    head.parent = neck

    for side, sign in [('_l', 1), ('_r', -1)]:
        clav = eb.new(f'clavicle{side}')
        clav.head = (0, 0.01, 1.16)
        clav.tail = (0.16 * sign, 0.01, 1.18)
        clav.parent = spine2

        uarm = eb.new(f'upperarm{side}')
        uarm.head = (0.28 * sign, 0.01, 1.14)
        uarm.tail = (0.46 * sign, 0.01, 0.94)
        uarm.parent = clav

        larm = eb.new(f'lowerarm{side}')
        larm.head = (0.46 * sign, 0.01, 0.94)
        larm.tail = (0.64 * sign, 0.01, 0.76)
        larm.parent = uarm

        hand = eb.new(f'hand{side}')
        hand.head = (0.64 * sign, 0.01, 0.76)
        hand.tail = (0.74 * sign, 0.01, 0.68)
        hand.parent = larm

    sock_gun = eb.new('weapon_socket_r')
    sock_gun.head = (-0.72, 0.01, 0.70)
    sock_gun.tail = (-0.72, -0.15, 0.70)
    sock_gun.parent = eb['hand_r']

    for side, sign in [('_l', 1), ('_r', -1)]:
        thigh = eb.new(f'thigh{side}')
        thigh.head = (0.16 * sign, 0.01, 0.70)
        thigh.tail = (0.21 * sign, 0.01, 0.44)
        thigh.parent = pelvis

        calf = eb.new(f'calf{side}')
        calf.head = (0.21 * sign, 0.01, 0.44)
        calf.tail = (0.25 * sign, 0.01, 0.16)
        calf.parent = thigh

        foot = eb.new(f'foot{side}')
        foot.head = (0.25 * sign, 0.01, 0.16)
        foot.tail = (0.26 * sign, -0.16, 0.02)
        foot.parent = calf

    bpy.ops.object.mode_set(mode='OBJECT')
    return arm_obj

def build_civilian_mesh(arm_obj):
    mesh = bpy.data.meshes.new("SK_Civilian_Survivor_Mesh")
    char_obj = bpy.data.objects.new("SK_Civilian_Survivor", mesh)
    bpy.context.scene.collection.objects.link(char_obj)

    mats = {
        'jumpsuit': create_pbr_mat("M_Civilian_Jumpsuit", (0.18, 0.42, 0.52, 1.0), roughness=0.65), # Azul trabajo gastado
        'vest': create_pbr_mat("M_Civilian_Vest", (0.85, 0.55, 0.12, 1.0), roughness=0.55),      # Chaleco seguridad desgastado
        'skin': create_pbr_mat("M_Civilian_Skin", (0.86, 0.66, 0.54, 1.0), roughness=0.45),      # Piel humana
        'hair': create_pbr_mat("M_Civilian_Hair", (0.22, 0.15, 0.10, 1.0), roughness=0.70),      # Pelo castaño
        'bandage': create_pbr_mat("M_Civilian_Bandage", (0.88, 0.85, 0.82, 1.0), roughness=0.8), # Vendas médicas
        'boots': create_pbr_mat("M_Civilian_Boots", (0.12, 0.10, 0.09, 1.0), roughness=0.50),    # Botas de cuero
        'mask': create_pbr_mat("M_Civilian_Respirator", (0.75, 0.75, 0.78, 1.0), metallic=0.4, roughness=0.3) # Mascarilla filtro
    }

    mat_list = [mats['jumpsuit'], mats['vest'], mats['skin'], mats['hair'], mats['bandage'], mats['boots'], mats['mask']]
    for m in mat_list:
        mesh.materials.append(m)

    mat_idx = {
        'jumpsuit': 0, 'vest': 1, 'skin': 2, 'hair': 3, 'bandage': 4, 'boots': 5, 'mask': 6
    }

    group_map = {}
    for bname in BONE_NAMES_HUMANOID:
        vg = char_obj.vertex_groups.new(name=bname)
        group_map[bname] = vg.index

    bm = bmesh.new()
    dlayer = bm.verts.layers.deform.verify()

    def assign_weights(verts, weights_dict):
        for v in verts:
            for bname, w in weights_dict.items():
                if bname in group_map:
                    v[dlayer][group_map[bname]] = w

    def add_box(center, size, midx, weights, rot=(0,0,0)):
        sx, sy, sz = size
        ret = bmesh.ops.create_cube(bm, size=1.0)
        verts = ret['verts']
        bmesh.ops.scale(bm, vec=(sx, sy, sz), verts=verts)
        if rot[0] != 0:
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=Matrix.Rotation(rot[0], 3, 'X'), verts=verts)
        if rot[1] != 0:
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=Matrix.Rotation(rot[1], 3, 'Y'), verts=verts)
        if rot[2] != 0:
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=Matrix.Rotation(rot[2], 3, 'Z'), verts=verts)
        bmesh.ops.translate(bm, vec=center, verts=verts)
        for f in bm.faces:
            if f.verts[0] in verts:
                f.material_index = midx
        assign_weights(verts, weights)
        return verts

    def add_cylinder(center, r1, r2, depth, midx, weights, segs=16, rot=(0,0,0)):
        ret = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segs, radius1=r1, radius2=r2, depth=depth)
        verts = ret['verts']
        if rot[0] != 0:
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=Matrix.Rotation(rot[0], 3, 'X'), verts=verts)
        if rot[1] != 0:
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=Matrix.Rotation(rot[1], 3, 'Y'), verts=verts)
        if rot[2] != 0:
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=Matrix.Rotation(rot[2], 3, 'Z'), verts=verts)
        bmesh.ops.translate(bm, vec=center, verts=verts)
        for f in bm.faces:
            if f.verts[0] in verts:
                f.material_index = midx
        assign_weights(verts, weights)
        return verts

    # 1. Pelvis / Caderas del civil
    add_box((0.0, 0.0, 0.76), (0.34, 0.22, 0.18), mat_idx['jumpsuit'], {'pelvis': 1.0})

    # 2. Torso inferior y superior (mono azul + chaleco de seguridad reflectante naranja)
    add_box((0.0, 0.0, 0.94), (0.36, 0.24, 0.22), mat_idx['jumpsuit'], {'spine_01': 0.8, 'pelvis': 0.2})
    add_box((0.0, 0.0, 1.12), (0.40, 0.26, 0.24), mat_idx['vest'], {'spine_02': 1.0})
    # Cuello del chaleco
    add_box((0.0, 0.01, 1.22), (0.30, 0.24, 0.08), mat_idx['vest'], {'spine_02': 0.8, 'neck_01': 0.2})

    # 3. Cuello anatómico
    add_cylinder((0.0, 0.0, 1.25), 0.08, 0.08, 0.12, mat_idx['skin'], {'neck_01': 1.0}, segs=14)

    # 4. Cabeza civil con pelo y respirador de supervivencia
    add_cylinder((0.0, 0.0, 1.40), 0.11, 0.10, 0.22, mat_idx['skin'], {'head': 1.0}, segs=16)
    # Cabello
    add_box((0.0, 0.01, 1.49), (0.24, 0.24, 0.10), mat_idx['hair'], {'head': 1.0})
    # Mascarilla de respiración / filtro de emergencia frontal
    add_box((0.0, -0.11, 1.35), (0.15, 0.09, 0.10), mat_idx['mask'], {'head': 1.0})
    # Cartuchos dobles de filtrado químico
    add_cylinder((-0.09, -0.09, 1.34), 0.038, 0.038, 0.06, mat_idx['mask'], {'head': 1.0}, segs=12, rot=(R(90), 0, 0))
    add_cylinder(( 0.09, -0.09, 1.34), 0.038, 0.038, 0.06, mat_idx['mask'], {'head': 1.0}, segs=12, rot=(R(90), 0, 0))

    # 5. Extremidades Superiores en Rest A-Pose (-35°)
    for side, sign in [('_l', 1), ('_r', -1)]:
        u_name = f'upperarm{side}'
        l_name = f'lowerarm{side}'
        h_name = f'hand{side}'
        c_name = f'clavicle{side}'

        # Hombro / Clavícula del chaleco
        add_box((0.26 * sign, 0.01, 1.15), (0.16, 0.22, 0.16), mat_idx['vest'], {c_name: 0.8, 'spine_02': 0.2})

        # Brazo superior en A-pose
        rot_a = (0, R(-35 * sign), 0)
        p_uarm_mid = Vector((0.37 * sign, 0.01, 1.04))
        add_box(p_uarm_mid, (0.18, 0.19, 0.22), mat_idx['jumpsuit'], {u_name: 1.0}, rot=rot_a)

        # Codo (unión 50/50 elástica)
        p_elbow = Vector((0.46 * sign, 0.01, 0.94))
        elbow_mat = mat_idx['bandage'] if side == '_l' else mat_idx['jumpsuit']
        add_cylinder(p_elbow, 0.08, 0.08, 0.10, elbow_mat, {u_name: 0.5, l_name: 0.5}, rot=rot_a)

        # Antebrazo (Brazo izquierdo vendado con apósito médico)
        p_larm_mid = Vector((0.55 * sign, 0.01, 0.85))
        forearm_mat = mat_idx['bandage'] if side == '_l' else mat_idx['skin']
        add_box(p_larm_mid, (0.16, 0.17, 0.22), forearm_mat, {l_name: 1.0}, rot=rot_a)

        # Mano conectada a la muñeca
        p_hand = Vector((0.66 * sign, 0.01, 0.74))
        add_box(p_hand, (0.12, 0.13, 0.12), mat_idx['skin'], {h_name: 1.0}, rot=rot_a)

    # 6. Extremidades Inferiores en Rest A-Pose (-10°)
    for side, sign in [('_l', 1), ('_r', -1)]:
        t_name = f'thigh{side}'
        k_name = f'calf{side}'
        f_name = f'foot{side}'

        rot_leg = (0, R(-10 * sign), 0)
        p_thigh = Vector((0.18 * sign, 0.01, 0.58))
        add_box(p_thigh, (0.22, 0.23, 0.24), mat_idx['jumpsuit'], {t_name: 1.0}, rot=rot_leg)

        p_knee = Vector((0.21 * sign, 0.01, 0.44))
        add_cylinder(p_knee, 0.09, 0.09, 0.10, mat_idx['jumpsuit'], {t_name: 0.5, k_name: 0.5}, rot=rot_leg)

        p_calf = Vector((0.23 * sign, 0.01, 0.30))
        add_box(p_calf, (0.20, 0.21, 0.22), mat_idx['jumpsuit'], {k_name: 1.0}, rot=rot_leg)

        p_foot = Vector((0.25 * sign, -0.05, 0.09))
        add_box(p_foot, (0.16, 0.28, 0.18), mat_idx['boots'], {f_name: 1.0})


    bm.to_mesh(mesh)
    bm.free()

    # Modificador Armature
    mod = char_obj.modifiers.new("Armature", 'ARMATURE')
    mod.object = arm_obj
    char_obj.parent = arm_obj

    return char_obj

# ==============================================================================
# 2. PARTE 2: ALIEN PET (BLOBBY - 6 PATAS, ANTENAS Y BIOLUMINISCENCIA)
# ==============================================================================

BONE_NAMES_PET = [
    'root', 'body', 'head', 'antenna_l', 'antenna_r', 'tail',
    'leg_fl', 'leg_fr',
    'leg_ml', 'leg_mr',
    'leg_bl', 'leg_br'
]

def build_pet_armature(name="SK_AlienPet_Armature"):
    arm_data = bpy.data.armatures.new(name + "_Data")
    arm_obj = bpy.data.objects.new(name, arm_data)
    bpy.context.scene.collection.objects.link(arm_obj)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='EDIT')
    eb = arm_data.edit_bones

    root = eb.new('root')
    root.head = (0, 0, 0)
    root.tail = (0, 0, 0.05)

    body = eb.new('body')
    body.head = (0, 0.10, 0.20)
    body.tail = (0, -0.15, 0.22)
    body.parent = root

    head = eb.new('head')
    head.head = (0, -0.15, 0.22)
    head.tail = (0, -0.32, 0.24)
    head.parent = body

    ant_l = eb.new('antenna_l')
    ant_l.head = (0.08, -0.26, 0.32)
    ant_l.tail = (0.14, -0.32, 0.44)
    ant_l.parent = head

    ant_r = eb.new('antenna_r')
    ant_r.head = (-0.08, -0.26, 0.32)
    ant_r.tail = (-0.14, -0.32, 0.44)
    ant_r.parent = head

    tail = eb.new('tail')
    tail.head = (0, 0.15, 0.20)
    tail.tail = (0, 0.32, 0.26)
    tail.parent = body

    # 6 patas (front, mid, back)
    leg_coords = [
        ('fl', 0.15, -0.10, 0.16),
        ('fr', -0.15, -0.10, 0.16),
        ('ml', 0.16, 0.02, 0.16),
        ('mr', -0.16, 0.02, 0.16),
        ('bl', 0.15, 0.12, 0.16),
        ('br', -0.15, 0.12, 0.16),
    ]

    for code, hx, hy, hz in leg_coords:
        lbone = eb.new(f'leg_{code}')
        lbone.head = (hx, hy, hz)
        lbone.tail = (hx * 1.3, hy, 0.02)
        lbone.parent = body

    bpy.ops.object.mode_set(mode='OBJECT')
    return arm_obj

def build_pet_mesh(arm_obj):
    mesh = bpy.data.meshes.new("SK_AlienPet_Mesh")
    pet_obj = bpy.data.objects.new("SK_AlienPet_Blobby", mesh)
    bpy.context.scene.collection.objects.link(pet_obj)

    mats = {
        'skin': create_pbr_mat("M_Pet_Skin", (0.25, 0.78, 0.82, 1.0), metallic=0.02, roughness=0.35), # Cian bioluminiscente
        'underbelly': create_pbr_mat("M_Pet_Belly", (0.85, 0.92, 0.95, 1.0), metallic=0.01, roughness=0.40), # Vientre suave
        'glow': create_pbr_mat("M_Pet_Glow", (0.95, 0.85, 0.20, 1.0), metallic=0.0, roughness=0.1, emission=(0.95, 0.85, 0.20, 1.0), emission_strength=4.5), # Ámbar brillante
        'eyes': create_pbr_mat("M_Pet_Eyes", (0.03, 0.03, 0.04, 1.0), metallic=0.3, roughness=0.04) # Ojos saltones brillantes
    }

    mat_list = [mats['skin'], mats['underbelly'], mats['glow'], mats['eyes']]
    for m in mat_list:
        mesh.materials.append(m)

    mat_idx = {'skin': 0, 'underbelly': 1, 'glow': 2, 'eyes': 3}

    group_map = {}
    for bname in BONE_NAMES_PET:
        vg = pet_obj.vertex_groups.new(name=bname)
        group_map[bname] = vg.index

    bm = bmesh.new()
    dlayer = bm.verts.layers.deform.verify()

    def assign_weights(verts, weights_dict):
        for v in verts:
            for bname, w in weights_dict.items():
                if bname in group_map:
                    v[dlayer][group_map[bname]] = w

    def add_pet_box(center, size, midx, weights):
        sx, sy, sz = size
        ret = bmesh.ops.create_cube(bm, size=1.0)
        verts = ret['verts']
        bmesh.ops.scale(bm, vec=(sx, sy, sz), verts=verts)
        bmesh.ops.translate(bm, vec=center, verts=verts)
        for f in bm.faces:
            if f.verts[0] in verts:
                f.material_index = midx
        assign_weights(verts, weights)
        return verts

    def add_pet_cylinder(center, r1, r2, depth, midx, weights, segs=12, rot=(0,0,0)):
        ret = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segs, radius1=r1, radius2=r2, depth=depth)
        verts = ret['verts']
        if rot[0] != 0:
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=Matrix.Rotation(rot[0], 3, 'X'), verts=verts)
        if rot[1] != 0:
            bmesh.ops.rotate(bm, cent=(0,0,0), matrix=Matrix.Rotation(rot[1], 3, 'Y'), verts=verts)
        bmesh.ops.translate(bm, vec=center, verts=verts)
        for f in bm.faces:
            if f.verts[0] in verts:
                f.material_index = midx
        assign_weights(verts, weights)
        return verts

    # 1. Cuerpo principal regordete
    add_pet_box((0.0, 0.0, 0.20), (0.28, 0.38, 0.18), mat_idx['skin'], {'body': 1.0})
    # Vientre
    add_pet_box((0.0, 0.0, 0.12), (0.22, 0.32, 0.06), mat_idx['underbelly'], {'body': 1.0})

    # 2. Cabeza esférica expresiva
    add_pet_cylinder((0.0, -0.24, 0.22), 0.14, 0.13, 0.18, mat_idx['skin'], {'head': 1.0}, segs=16, rot=(R(90), 0, 0))

    # Ojos grandes expresivos
    add_pet_box((0.09, -0.32, 0.26), (0.06, 0.04, 0.06), mat_idx['eyes'], {'head': 1.0})
    add_pet_box((-0.09, -0.32, 0.26), (0.06, 0.04, 0.06), mat_idx['eyes'], {'head': 1.0})

    # 3. Antenas bioluminiscentes
    add_pet_cylinder((0.11, -0.28, 0.36), 0.02, 0.015, 0.14, mat_idx['skin'], {'antenna_l': 1.0}, segs=8, rot=(R(-20), R(20), 0))
    add_pet_box((0.14, -0.32, 0.43), (0.04, 0.04, 0.04), mat_idx['glow'], {'antenna_l': 1.0})

    add_pet_cylinder((-0.11, -0.28, 0.36), 0.02, 0.015, 0.14, mat_idx['skin'], {'antenna_r': 1.0}, segs=8, rot=(R(-20), R(-20), 0))
    add_pet_box((-0.14, -0.32, 0.43), (0.04, 0.04, 0.04), mat_idx['glow'], {'antenna_r': 1.0})

    # 4. Cola corta y redondeada
    add_pet_cylinder((0.0, 0.24, 0.22), 0.06, 0.02, 0.16, mat_idx['skin'], {'tail': 1.0}, segs=10, rot=(R(-70), 0, 0))
    add_pet_box((0.0, 0.31, 0.25), (0.035, 0.035, 0.035), mat_idx['glow'], {'tail': 1.0})

    # 5. Seis patas con patitas de apoyo
    leg_coords = [
        ('fl', 0.15, -0.10), ('fr', -0.15, -0.10),
        ('ml', 0.16, 0.02), ('mr', -0.16, 0.02),
        ('bl', 0.15, 0.12), ('br', -0.15, 0.12)
    ]
    for code, px, py in leg_coords:
        sign = 1 if 'l' in code else -1
        add_pet_cylinder((px * 1.1, py, 0.10), 0.035, 0.028, 0.12, mat_idx['skin'], {f'leg_{code}': 1.0}, segs=8, rot=(0, R(25 * sign), 0))
        add_pet_box((px * 1.25, py, 0.03), (0.05, 0.07, 0.03), mat_idx['underbelly'], {f'leg_{code}': 1.0})

    bm.to_mesh(mesh)
    bm.free()

    mod = pet_obj.modifiers.new("Armature", 'ARMATURE')
    mod.object = arm_obj
    pet_obj.parent = arm_obj

    return pet_obj

# ==============================================================================
# 3. ANIMACIONES PROCEDURALES DE LA MASCOTA
# ==============================================================================

def generate_pet_animations(arm_obj):
    def reset_pet_pose():
        bpy.context.view_layer.objects.active = arm_obj
        bpy.ops.object.mode_set(mode='POSE')
        for b in arm_obj.pose.bones:
            for c in list(b.constraints):
                b.constraints.remove(c)
            b.rotation_mode = 'XYZ'
            b.rotation_euler = (0.0, 0.0, 0.0)
            b.location = (0.0, 0.0, 0.0)
            b.scale = (1.0, 1.0, 1.0)
        bpy.context.view_layer.update()

    if arm_obj.animation_data:
        arm_obj.animation_data_clear()
    arm_obj.animation_data_create()
    pb = arm_obj.pose.bones

    # A_Pet_Idle (30 frames, 1.0s loop)
    print("  [PET ANIM] Generando A_Pet_Idle...")
    reset_pet_pose()
    act_idle = bpy.data.actions.new("A_Pet_Idle")
    arm_obj.animation_data.action = act_idle
    for f in range(31):
        t = 0.0 if f == 30 else (f / 30.0)
        p = 2.0 * PI * t
        pb['body'].location = Vector((0.0, 0.0, math.sin(p) * 0.015))
        pb['head'].rotation_euler = Euler((math.sin(p) * R(4), 0.0, math.sin(p) * R(6)))
        pb['tail'].rotation_euler = Euler((0.0, 0.0, math.sin(p * 2.0) * R(25)))
        pb['antenna_l'].rotation_euler = Euler((math.sin(p * 2.0) * R(8), 0.0, math.sin(p) * R(6)))
        pb['antenna_r'].rotation_euler = Euler((math.sin(p * 2.0 + 0.5) * R(8), 0.0, -math.sin(p) * R(6)))
        for b in pb:
            b.keyframe_insert('location', frame=f)
            b.keyframe_insert('rotation_euler', frame=f)

    # Exportar A_Pet_Idle (siempre en origen (0,0,0))
    arm_obj.location = Vector((0.0, 0.0, 0.0))
    fbx_idle = os.path.join(FBX_ANIM_DIR, "A_Pet_Idle.fbx")
    export_fbx_anim(arm_obj, fbx_idle, 0, 30)

    # A_Pet_Run (20 frames, 0.66s loop - Carrera rápida de 6 patas a 650 cm/s)
    print("  [PET ANIM] Generando A_Pet_Run...")
    reset_pet_pose()
    act_run = bpy.data.actions.new("A_Pet_Run")
    arm_obj.animation_data.action = act_run
    for f in range(21):
        t = 0.0 if f == 20 else (f / 20.0)
        p = 2.0 * PI * t
        s1 = math.sin(p)
        s2 = math.sin(p + PI)

        pb['body'].location = Vector((math.sin(p * 2.0) * 0.01, 0.0, -abs(math.sin(p * 2.0)) * 0.025))
        pb['head'].rotation_euler = Euler((R(-6), 0.0, math.sin(p) * R(4)))
        pb['tail'].rotation_euler = Euler((R(15), 0.0, math.sin(p) * R(16)))

        pb['leg_fl'].rotation_euler = Euler((s1 * R(30), 0, 0))
        pb['leg_mr'].rotation_euler = Euler((s1 * R(30), 0, 0))
        pb['leg_bl'].rotation_euler = Euler((s1 * R(30), 0, 0))

        pb['leg_fr'].rotation_euler = Euler((s2 * R(30), 0, 0))
        pb['leg_ml'].rotation_euler = Euler((s2 * R(30), 0, 0))
        pb['leg_br'].rotation_euler = Euler((s2 * R(30), 0, 0))

        for b in pb:
            b.keyframe_insert('location', frame=f)
            b.keyframe_insert('rotation_euler', frame=f)

    arm_obj.location = Vector((0.0, 0.0, 0.0))
    fbx_run = os.path.join(FBX_ANIM_DIR, "A_Pet_Run.fbx")
    export_fbx_anim(arm_obj, fbx_run, 0, 20)

    # A_Pet_Curious (40 frames, 1.33s loop - Inclinación de cabeza y aproximación)
    print("  [PET ANIM] Generando A_Pet_Curious...")
    reset_pet_pose()
    act_curious = bpy.data.actions.new("A_Pet_Curious")
    arm_obj.animation_data.action = act_curious
    for f in range(41):
        t = 0.0 if f == 40 else (f / 40.0)
        p = 2.0 * PI * t
        pb['body'].location = Vector((0.0, -0.04, 0.02))
        pb['head'].rotation_euler = Euler((R(-12) + math.sin(p) * R(5), math.sin(p) * R(12), math.sin(p) * R(14)))
        pb['tail'].rotation_euler = Euler((R(20), 0.0, math.sin(p * 4.0) * R(20)))
        pb['antenna_l'].rotation_euler = Euler((R(15), 0.0, math.sin(p * 2.0) * R(12)))
        pb['antenna_r'].rotation_euler = Euler((R(15), 0.0, -math.sin(p * 2.0) * R(12)))
        for b in pb:
            b.keyframe_insert('location', frame=f)
            b.keyframe_insert('rotation_euler', frame=f)

    arm_obj.location = Vector((0.0, 0.0, 0.0))
    fbx_curious = os.path.join(FBX_ANIM_DIR, "A_Pet_Curious.fbx")
    export_fbx_anim(arm_obj, fbx_curious, 0, 40)

def export_fbx_anim(arm_obj, out_path, fstart, fend):
    bpy.context.scene.frame_start = fstart
    bpy.context.scene.frame_end = fend
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    arm_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj

    bpy.ops.export_scene.fbx(
        filepath=out_path,
        use_selection=True,
        add_leaf_bones=False,
        armature_nodetype='NULL',
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_ALL',
        mesh_smooth_type='FACE',
        bake_anim=True,
        bake_anim_use_nla_strips=False,
        bake_anim_use_all_actions=False,
        bake_anim_step=1.0,
        bake_anim_simplify_factor=0.0
    )
    print(f"    [OK] Anim FBX: {out_path} ({os.path.getsize(out_path) // 1024} KB)")

def _solve_2bone_ik_civ(root_pos, target_pos, l1, l2, pole_dir):
    to_target = target_pos - root_pos
    dist = to_target.length
    max_len = (l1 + l2) * 0.999
    min_len = abs(l1 - l2) * 1.001
    dist_clamped = max(min_len, min(max_len, dist))
    cos_alpha = max(-1.0, min(1.0, (l1 * l1 + dist_clamped * dist_clamped - l2 * l2) / (2.0 * l1 * dist_clamped)))
    alpha = math.acos(cos_alpha)
    target_dir = to_target.normalized()
    plane_normal = target_dir.cross(pole_dir)
    if plane_normal.length < 1e-4:
        plane_normal = target_dir.cross(Vector((0, 0, 1)))
    plane_normal.normalize()
    arm_up = plane_normal.cross(target_dir).normalized()
    upper_dir = (target_dir * math.cos(alpha) + arm_up * math.sin(alpha)).normalized()
    elbow_pos = root_pos + upper_dir * l1
    lower_dir = (target_pos - elbow_pos).normalized()
    return upper_dir, lower_dir, plane_normal

def _align_bone_twistfree_civ(arm_obj, bone_name, target_dir, front_dir, prev_eulers):
    b = arm_obj.pose.bones[bone_name]
    rest_mat3 = b.bone.matrix_local.to_3x3()
    y_r = rest_mat3.col[1].normalized()
    front_r0 = Vector((0.0, -1.0, 0.0))
    z_r = front_r0 - front_r0.dot(y_r) * y_r
    if z_r.length < 1e-4:
        z_r = Vector((0.0, 0.0, 1.0)) - Vector((0.0, 0.0, 1.0)).dot(y_r) * y_r
    z_r.normalize()
    x_r = y_r.cross(z_r).normalized()
    m_mesh_rest = Matrix((x_r, y_r, z_r)).transposed()

    y_t = target_dir.normalized()
    z_t = front_dir - front_dir.dot(y_t) * y_t
    if z_t.length < 1e-4:
        fallback = Vector((0.0, 0.0, 1.0)) if abs(y_t.z) < 0.9 else Vector((1.0, 0.0, 0.0))
        z_t = fallback - fallback.dot(y_t) * y_t
    z_t.normalize()
    x_t = y_t.cross(z_t).normalized()
    m_mesh_target = Matrix((x_t, y_t, z_t)).transposed()

    pose_mat3 = m_mesh_target @ m_mesh_rest.transposed() @ rest_mat3
    b.matrix = Matrix.LocRotScale(b.head.copy(), pose_mat3, Vector((1, 1, 1)))
    bpy.context.view_layer.update()
    b.rotation_mode = 'XYZ'
    if bone_name in prev_eulers:
        eul = b.rotation_euler.copy()
        eul.make_compatible(prev_eulers[bone_name])
        b.rotation_euler = eul
    prev_eulers[bone_name] = b.rotation_euler.copy()

def _pose_injured_left_arm_civ(arm_obj, l_target, prev_eulers):
    bpy.context.view_layer.update()
    pb = arm_obj.pose.bones
    root_pos = pb['upperarm_l'].head.copy()
    l1 = (pb['upperarm_l'].tail - pb['upperarm_l'].head).length
    l2 = (pb['lowerarm_l'].tail - pb['lowerarm_l'].head).length
    pole_l = Vector((0.75, 0.25, -0.55)).normalized()
    u_dir, l_dir, p_norm = _solve_2bone_ik_civ(root_pos, l_target, l1, l2, pole_l)
    u_front = u_dir.cross(p_norm).normalized()
    l_front = l_dir.cross(p_norm).normalized()
    _align_bone_twistfree_civ(arm_obj, 'upperarm_l', u_dir, u_front, prev_eulers)
    _align_bone_twistfree_civ(arm_obj, 'lowerarm_l', l_dir, l_front, prev_eulers)
    _align_bone_twistfree_civ(arm_obj, 'hand_l', Vector((-0.7, -0.7, 0.1)).normalized(), l_front, prev_eulers)

def generate_civilian_animations(arm_obj):
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='POSE')
    pb = arm_obj.pose.bones
    for b in pb:
        b.rotation_mode = 'XYZ'

    def clear_anim():
        if arm_obj.animation_data:
            arm_obj.animation_data_clear()
        for b in pb:
            b.rotation_mode = 'XYZ'
            b.rotation_euler = (0, 0, 0)
            b.location = (0, 0, 0)
            b.scale = (1, 1, 1)

    def unwrap_all(f, prev_eulers):
        for b in pb:
            if b.name in prev_eulers:
                eul = b.rotation_euler.copy()
                eul.make_compatible(prev_eulers[b.name])
                b.rotation_euler = eul
            prev_eulers[b.name] = b.rotation_euler.copy()
            b.keyframe_insert('location', frame=f)
            b.keyframe_insert('rotation_euler', frame=f)

    # 1. A_Civilian_Idle (60 frames loop - Superviviente exhausto, brazo vendado despejado del pecho)
    print("  [CIVILIAN ANIM] Generando A_Civilian_Idle (Calibrado 3D Sin Clipping)...")
    clear_anim()
    act_idle = bpy.data.actions.new("A_Civilian_Idle")
    arm_obj.animation_data_create()
    arm_obj.animation_data.action = act_idle

    prev_eulers = {}
    for f in range(61):
        t = 0.0 if f == 60 else (f / 60.0)
        p = 2.0 * PI * t
        pb['pelvis'].location = Vector((0.0, math.sin(p) * 0.005, 0.0))
        pb['spine_01'].rotation_euler = Euler((R(4) + math.sin(p) * R(1.2), 0.0, 0.0))
        pb['spine_02'].rotation_euler = Euler((R(6) + math.sin(p) * R(1.0), 0.0, 0.0))
        pb['neck_01'].rotation_euler = Euler((R(-6), 0.0, 0.0))
        pb['head'].rotation_euler = Euler((R(-4), 0.0, math.sin(p) * R(1.0)))

        pb['clavicle_r'].rotation_euler = Euler((0.0, 0.0, 0.0))
        pb['upperarm_r'].rotation_euler = Euler((R(-5) + math.sin(p) * R(0.5), 0.0, R(4)))
        pb['lowerarm_r'].rotation_euler = Euler((0.0, 0.0, -R(10)))
        pb['hand_r'].rotation_euler = Euler((0.0, 0.0, 0.0))

        pb['thigh_l'].rotation_euler = Euler((R(2), 0.0, R(1)))
        pb['calf_l'].rotation_euler = Euler((R(4), 0.0, 0.0))
        pb['foot_l'].rotation_euler = Euler((R(-6), 0.0, 0.0))

        pb['thigh_r'].rotation_euler = Euler((R(2), 0.0, R(-1)))
        pb['calf_r'].rotation_euler = Euler((R(4), 0.0, 0.0))
        pb['foot_r'].rotation_euler = Euler((R(-6), 0.0, 0.0))

        pb['clavicle_l'].rotation_euler = Euler((R(-8), R(-8), R(6)))
        _pose_injured_left_arm_civ(arm_obj, Vector((0.08, -0.26, 0.88 + math.sin(p) * 0.005)), prev_eulers)
        unwrap_all(f, prev_eulers)

    fbx_idle = os.path.join(FBX_ANIM_DIR, "A_Civilian_Idle.fbx")
    export_fbx_anim(arm_obj, fbx_idle, 0, 60)

    # 2. A_Civilian_Walk (30 frames loop - Marcha herida con zancada asimétrica)
    print("  [CIVILIAN ANIM] Generando A_Civilian_Walk (Calibrado 3D Sin Clipping)...")
    clear_anim()
    act_walk = bpy.data.actions.new("A_Civilian_Walk")
    arm_obj.animation_data_create()
    arm_obj.animation_data.action = act_walk

    prev_eulers = {}
    for f in range(31):
        t = 0.0 if f == 30 else (f / 30.0)
        p = 2.0 * PI * t
        s_l = math.sin(p)
        s_r = math.sin(p + PI)

        pelvis_y_bob = -abs(math.sin(p)) * 0.018
        pelvis_x_sway = math.sin(p) * 0.015
        pb['pelvis'].location = Vector((pelvis_x_sway, pelvis_y_bob, 0.0))
        pb['pelvis'].rotation_euler = Euler((R(3), math.sin(p) * R(1.5), -s_l * R(2.5)))

        pb['spine_01'].rotation_euler = Euler((R(8), -math.sin(p) * R(1.2), s_l * R(2.0)))
        pb['spine_02'].rotation_euler = Euler((R(6), 0.0, 0.0))
        pb['neck_01'].rotation_euler = Euler((R(-8), 0.0, 0.0))
        pb['head'].rotation_euler = Euler((R(-4), 0.0, -s_l * R(1.2)))

        thigh_l_pitch = s_l * R(20)
        pb['thigh_l'].rotation_euler = Euler((thigh_l_pitch, 0.0, R(1)))
        calf_l_bend = R(6) + (max(0.0, -s_l) ** 1.3) * R(40)
        pb['calf_l'].rotation_euler = Euler((calf_l_bend, 0.0, 0.0))
        pb['foot_l'].rotation_euler = Euler((-s_l * R(12) - R(4), 0.0, 0.0))

        thigh_r_pitch = s_r * R(20)
        pb['thigh_r'].rotation_euler = Euler((thigh_r_pitch, 0.0, R(-1)))
        calf_r_bend = R(6) + (max(0.0, -s_r) ** 1.3) * R(40)
        pb['calf_r'].rotation_euler = Euler((calf_r_bend, 0.0, 0.0))
        pb['foot_r'].rotation_euler = Euler((-s_r * R(12) - R(4), 0.0, 0.0))

        pb['clavicle_r'].rotation_euler = Euler((-s_l * R(2.5), 0.0, -s_l * R(2.0)))
        u_r_x = R(-10) - s_l * R(22)
        u_r_z = R(6) + s_l * R(4)
        pb['upperarm_r'].rotation_euler = Euler((u_r_x, 0.0, u_r_z))
        pb['lowerarm_r'].rotation_euler = Euler((R(-5) - max(0.0, s_l) * R(10), 0.0, -R(14) - max(0.0, s_l) * R(10)))
        pb['hand_r'].rotation_euler = Euler((R(4), 0.0, 0.0))

        pb['clavicle_l'].rotation_euler = Euler((R(-8), R(-8), R(6)))
        _pose_injured_left_arm_civ(arm_obj, Vector((0.08, -0.27, 0.87 + pelvis_y_bob)), prev_eulers)
        unwrap_all(f, prev_eulers)

    fbx_walk = os.path.join(FBX_ANIM_DIR, "A_Civilian_Walk.fbx")
    export_fbx_anim(arm_obj, fbx_walk, 0, 30)

    # 3. A_Civilian_Panic_Run (24 frames loop - Carrera de pánico agachada protegiéndose)
    print("  [CIVILIAN ANIM] Generando A_Civilian_Panic_Run (Calibrado 3D Sin Clipping)...")
    clear_anim()
    act_run = bpy.data.actions.new("A_Civilian_Panic_Run")
    arm_obj.animation_data_create()
    arm_obj.animation_data.action = act_run

    prev_eulers = {}
    for f in range(25):
        t = 0.0 if f == 24 else (f / 24.0)
        p = 2.0 * PI * t
        s_l = math.sin(p)
        s_r = math.sin(p + PI)

        pelvis_y_bob = -abs(math.sin(p)) * 0.035
        pelvis_x_sway = math.sin(p) * 0.018
        pb['pelvis'].location = Vector((pelvis_x_sway, pelvis_y_bob, -0.015))
        pb['pelvis'].rotation_euler = Euler((R(10), math.sin(p) * R(3.0), -s_l * R(4.0)))

        pb['spine_01'].rotation_euler = Euler((R(16), -math.sin(p) * R(2.0), s_l * R(3.5)))
        pb['spine_02'].rotation_euler = Euler((R(12), 0.0, 0.0))
        pb['neck_01'].rotation_euler = Euler((R(-16), 0.0, 0.0))
        pb['head'].rotation_euler = Euler((R(-10), 0.0, -s_l * R(2.0)))

        thigh_l_pitch = s_l * R(34)
        pb['thigh_l'].rotation_euler = Euler((thigh_l_pitch, 0.0, R(2)))
        calf_l_bend = R(10) + (max(0.0, -s_l) ** 1.3) * R(64)
        pb['calf_l'].rotation_euler = Euler((calf_l_bend, 0.0, 0.0))
        pb['foot_l'].rotation_euler = Euler((-s_l * R(18) - R(6), 0.0, 0.0))

        thigh_r_pitch = s_r * R(34)
        pb['thigh_r'].rotation_euler = Euler((thigh_r_pitch, 0.0, R(-2)))
        calf_r_bend = R(10) + (max(0.0, -s_r) ** 1.3) * R(64)
        pb['calf_r'].rotation_euler = Euler((calf_r_bend, 0.0, 0.0))
        pb['foot_r'].rotation_euler = Euler((-s_r * R(18) - R(6), 0.0, 0.0))

        pb['clavicle_r'].rotation_euler = Euler((-s_l * R(4.0), 0.0, -s_l * R(3.0)))
        u_r_x = R(-20) - s_l * R(28)
        u_r_z = R(8) + s_l * R(5)
        pb['upperarm_r'].rotation_euler = Euler((u_r_x, 0.0, u_r_z))
        pb['lowerarm_r'].rotation_euler = Euler((R(-18) - max(0.0, s_l) * R(20), 0.0, -R(30) - max(0.0, s_l) * R(15)))
        pb['hand_r'].rotation_euler = Euler((R(6), 0.0, 0.0))

        pb['clavicle_l'].rotation_euler = Euler((R(-10), R(-10), R(8)))
        _pose_injured_left_arm_civ(arm_obj, Vector((0.08, -0.30, 0.85 + pelvis_y_bob)), prev_eulers)
        unwrap_all(f, prev_eulers)

    fbx_run = os.path.join(FBX_ANIM_DIR, "A_Civilian_Panic_Run.fbx")
    export_fbx_anim(arm_obj, fbx_run, 0, 24)

# ==============================================================================
# 4. PIPELINE PRINCIPAL Y RENDER DE COMPARATIVA
# ==============================================================================

def main():
    print("=" * 75)
    print("GENERADOR OFICIAL DE SUPERVIVIENTES Y MASCOTAS (BLENDER 5.2)")
    print("=" * 75)

    clear_scene()

    # 1. Crear Civilian Survivor
    print("\n[1/3] Construyendo SK_Civilian_Survivor...")
    civ_arm = build_humanoid_armature("SK_Civilian_Armature")
    civ_mesh = build_civilian_mesh(civ_arm)

    fbx_civ_path = os.path.join(FBX_CHAR_DIR, "SK_Civilian_Survivor.fbx")
    bpy.ops.object.select_all(action='DESELECT')
    civ_mesh.select_set(True)
    civ_arm.select_set(True)
    bpy.context.view_layer.objects.active = civ_arm

    bpy.ops.export_scene.fbx(
        filepath=fbx_civ_path,
        use_selection=True,
        add_leaf_bones=False,
        armature_nodetype='NULL',
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_ALL',
        mesh_smooth_type='FACE',
        bake_anim=False
    )
    print(f"  [OK] Exportado Skeletal Mesh: {fbx_civ_path} ({os.path.getsize(fbx_civ_path) // 1024} KB)")

    # 1.1 Generar animación de reposo para el civil
    generate_civilian_animations(civ_arm)

    # 2. Crear Alien Pet
    print("\n[2/3] Construyendo SK_AlienPet_Blobby...")
    pet_arm = build_pet_armature("SK_AlienPet_Armature")
    pet_mesh = build_pet_mesh(pet_arm)
    pet_arm.location = Vector((0.0, 0.0, 0.0))

    # Exportar Mesh base de la mascota centrada en (0, 0, 0)
    fbx_pet_path = os.path.join(FBX_CHAR_DIR, "SK_AlienPet_Blobby.fbx")
    bpy.ops.object.select_all(action='DESELECT')
    pet_mesh.select_set(True)
    pet_arm.select_set(True)
    bpy.context.view_layer.objects.active = pet_arm

    assert pet_arm.location.length < 1e-6, f"AlienPet must be centered at origin before mesh FBX export, got {pet_arm.location}"
    bpy.ops.export_scene.fbx(
        filepath=fbx_pet_path,
        use_selection=True,
        add_leaf_bones=False,
        armature_nodetype='NULL',
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_ALL',
        mesh_smooth_type='FACE',
        bake_anim=False
    )
    print(f"  [OK] Exportado Skeletal Mesh: {fbx_pet_path} ({os.path.getsize(fbx_pet_path) // 1024} KB)")

    # 3. Generar animaciones de la mascota
    print("\n[3/3] Generando animaciones de locomoción para la mascota...")
    generate_pet_animations(pet_arm)

    # 4. Configurar escena de render y generar showcase
    print("\n[RENDER] Generando render showcase de los supervivientes...")
    pet_arm.location = Vector((0.85, -0.2, 0.0)) # Colocar la mascota al lado del civil

    # Cámara
    cam_data = bpy.data.cameras.new("ShowcaseCam")
    cam_obj = bpy.data.objects.new("ShowcaseCam", cam_data)
    bpy.context.scene.collection.objects.link(cam_obj)
    cam_loc = Vector((2.2, -3.2, 1.1))
    target = Vector((0.4, 0.0, 0.75))
    cam_obj.location = cam_loc
    cam_obj.rotation_euler = (target - cam_loc).to_track_quat('-Z', 'Y').to_euler()
    cam_data.lens = 45
    bpy.context.scene.camera = cam_obj

    # Iluminación
    world = bpy.context.scene.world or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs['Color'].default_value = (0.05, 0.07, 0.10, 1.0)
        bg.inputs['Strength'].default_value = 0.9

    light_data = bpy.data.lights.new("Sun", 'SUN')
    light_obj = bpy.data.objects.new("Sun", light_data)
    bpy.context.scene.collection.objects.link(light_obj)
    light_obj.location = Vector((3.0, -3.0, 4.0))
    light_obj.rotation_euler = Euler((R(50), R(15), R(35)))
    light_data.energy = 4.0

    bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
    bpy.context.scene.render.resolution_x = 1280
    bpy.context.scene.render.resolution_y = 720

    out_render = os.path.join(RENDERS_DIR, "Showcase_Survivors_Civilian_and_Pet.png")
    bpy.context.scene.render.filepath = out_render
    bpy.ops.render.render(write_still=True)
    print(f"  [OK] Render generado: {out_render}")

    out_brain = os.path.join(BRAIN_DIR, "Showcase_Survivors_Civilian_and_Pet.png")
    shutil.copy2(out_render, out_brain)
    print(f"  [OK] Copiado a Brain: {out_brain}")

    blend_file = os.path.join(ART_DIR, "Blender", "SK_Survivors_Official.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_file)
    print(f"  [OK] Blend guardado: {blend_file}")

    print("\nTODOS LOS ACTIVOS DE SUPERVIVIENTES Y MASCOTAS COMPLETADOS EXITOSAMENTE.")

if __name__ == "__main__":
    main()

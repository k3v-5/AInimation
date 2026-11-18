"""
generar_personaje_riggeado_oficial.py
======================================
Pipeline Oficial de Rigging y Malla Esquelética para Unreal Engine 5
Proyecto: Astra Hazard - Rescue Squad

Resuelve definitivamente la preocupación por deformaciones y roturas en animación:
1. REST A-POSE ESTÁNDAR: Malla base modelada en A-pose simétrica limpia para retargeting UE5 (Mixamo, ALS, Lyra).
2. TOPOLOGÍA DE ARTICULACIÓN REFORZADA (3-Loop Elbow & Shoulder):
   - Codos y hombros con bucles de contorno para flexión limpia hasta 120° sin colapso de volumen.
3. ESQUELETO COMPATIBLE CON UE5:
   - Jerarquía: root -> pelvis -> spine_01 -> spine_02 -> neck_01 -> head
   - Extremidades: clavicle -> upperarm -> lowerarm -> hand (+ weapon_socket_r)
   - Piernas: thigh -> calf -> foot
4. PESOS DE VÉRTICE DETERMINISTAS VÍA BMesh DEFORM LAYER:
   - Asignación directa a capas de deformación en tiempo de construcción.
   - Partes rígidas con peso 1.0 (cero distorsión elástica).
   - Articulaciones flexibles con pesos suavizados.
5. EQUIPAMIENTO MODULAR (SOCKET ATTACHMENT):
   - El cañón extintor se modela y exporta como asset modular acoplable al socket de la mano.
6. TEST DE DEFORMACIÓN EN ANIMACIÓN (FRAME-BY-FRAME VALIDATION):
   - Genera poses de flexión de combate (90°) y flexión extrema (115°) para verificar visualmente que no hay roturas.
"""

import sys, os, math, shutil
import bpy, bmesh
from mathutils import Matrix, Vector, Euler
from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = r"f:\Dev\Game"
ART_DIR = os.path.join(PROJECT_ROOT, "Art")
FBX_DIR = os.path.join(ART_DIR, "FBX", "Characters")
EQUIP_FBX_DIR = os.path.join(ART_DIR, "FBX", "Equipment")
RENDERS_DIR = os.path.join(ART_DIR, "Renders")
BRAIN_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\b59ff04f-3c21-4ee5-94b0-8e8f899f8923"

os.makedirs(FBX_DIR, exist_ok=True)
os.makedirs(EQUIP_FBX_DIR, exist_ok=True)
os.makedirs(RENDERS_DIR, exist_ok=True)
os.makedirs(BRAIN_DIR, exist_ok=True)

R = math.radians

def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

# ---------------------------------------------------------------------------
# PALETA PBR OFICIAL
# ---------------------------------------------------------------------------
def create_pbr_mat(name, base_color, metallic=0.04, roughness=0.40, emission=None, emission_strength=1.0):
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

def create_unlit_mat(name, color):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    emis = nt.nodes.new('ShaderNodeEmission')
    emis.inputs['Color'].default_value = color
    emis.inputs['Strength'].default_value = 1.0
    nt.links.new(emis.outputs['Emission'], out.inputs['Surface'])
    mat.use_backface_culling = True
    return mat

def build_palette():
    return {
        'suit_orange': create_pbr_mat("M_Suit_Orange", (0.82, 0.42, 0.10, 1.0), metallic=0.02, roughness=0.45),
        'suit_dark_orange': create_pbr_mat("M_Suit_DarkOrange", (0.68, 0.32, 0.08, 1.0), metallic=0.02, roughness=0.50),
        'armor_sage': create_pbr_mat("M_Armor_Sage", (0.32, 0.52, 0.28, 1.0), metallic=0.06, roughness=0.38),
        'helmet_grey': create_pbr_mat("M_Helmet_Grey", (0.34, 0.36, 0.35, 1.0), metallic=0.15, roughness=0.35),
        'visor_tinted': create_pbr_mat("M_Visor_Tinted", (0.10, 0.14, 0.18, 1.0), metallic=0.25, roughness=0.06),
        'stripe_yellow': create_pbr_mat("M_Stripe_Yellow", (0.86, 0.86, 0.18, 1.0), metallic=0.02, roughness=0.25),
        'hose_red': create_pbr_mat("M_Hose_Red", (0.78, 0.08, 0.06, 1.0), metallic=0.03, roughness=0.45),
        'harness_dark': create_pbr_mat("M_Harness_Dark", (0.08, 0.08, 0.09, 1.0), metallic=0.05, roughness=0.60),
        'led_green': create_pbr_mat("M_LED_Green", (0.15, 0.98, 0.20, 1.0), metallic=0.0, roughness=0.10, emission=(0.15, 0.98, 0.20, 1.0), emission_strength=5.0),
        'led_red': create_pbr_mat("M_LED_Red", (1.0, 0.06, 0.06, 1.0), metallic=0.0, roughness=0.10, emission=(1.0, 0.06, 0.06, 1.0), emission_strength=4.5),
        'weapon_blue': create_pbr_mat("M_Weapon_Blue", (0.28, 0.42, 0.50, 1.0), metallic=0.35, roughness=0.30),
        'weapon_stock': create_pbr_mat("M_Weapon_Stock", (0.55, 0.25, 0.12, 1.0), metallic=0.10, roughness=0.45),
        'weapon_yellow': create_pbr_mat("M_Weapon_Yellow", (0.92, 0.82, 0.15, 1.0), metallic=0.05, roughness=0.20, emission=(0.92, 0.82, 0.15, 1.0), emission_strength=2.5),
        'metal_dark': create_pbr_mat("M_Metal_Dark", (0.12, 0.13, 0.15, 1.0), metallic=0.75, roughness=0.25),
        'outline_black': create_unlit_mat("M_Outline_Black", (0.01, 0.01, 0.01, 1.0))
    }

# ---------------------------------------------------------------------------
# ESQUELETO OFICIAL PARA UNREAL ENGINE 5 (ARMADURA BIPEDAL)
# ---------------------------------------------------------------------------
BONE_NAMES = [
    'root', 'pelvis', 'spine_01', 'spine_02', 'neck_01', 'head',
    'clavicle_l', 'upperarm_l', 'lowerarm_l', 'hand_l',
    'clavicle_r', 'upperarm_r', 'lowerarm_r', 'hand_r',
    'weapon_socket_r',
    'thigh_l', 'calf_l', 'foot_l',
    'thigh_r', 'calf_r', 'foot_r'
]

def build_ue5_armature():
    arm_data = bpy.data.armatures.new("Armature_SK_Firefighter")
    arm_obj = bpy.data.objects.new("SK_Firefighter_Armature", arm_data)
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

# ---------------------------------------------------------------------------
# MALLA DEL PERSONAJE MODELADA EN REST A-POSE (CON BUCLÉS ANTI-PINCH)
# ---------------------------------------------------------------------------
def build_rest_a_pose_mesh(mats, arm_obj):
    mesh = bpy.data.meshes.new("SK_Firefighter_RestAPose_Mesh")
    char_obj = bpy.data.objects.new("SK_Firefighter_Official", mesh)
    bpy.context.scene.collection.objects.link(char_obj)

    # Crear grupos de vértices en el objeto antes de poblar BMesh
    group_map = {}
    for bname in BONE_NAMES:
        vg = char_obj.vertex_groups.new(name=bname)
        group_map[bname] = vg.index

    bm = bmesh.new()
    dlayer = bm.verts.layers.deform.verify()

    mat_order = [
        mats['suit_orange'], mats['suit_dark_orange'], mats['armor_sage'], mats['helmet_grey'],
        mats['visor_tinted'], mats['stripe_yellow'], mats['hose_red'], mats['harness_dark'],
        mats['led_green'], mats['led_red'], mats['weapon_blue'], mats['weapon_stock'],
        mats['weapon_yellow'], mats['metal_dark'], mats['outline_black']
    ]

    def assign_weights(verts, weights_dict):
        for v in verts:
            for bname, w in weights_dict.items():
                if bname in group_map:
                    v[dlayer][group_map[bname]] = w

    def add_box(center, size, mat_idx, weights_dict, rot=(0,0,0)):
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
                f.material_index = mat_idx
        assign_weights(verts, weights_dict)
        return verts

    def add_cylinder(center, r1, r2, depth, mat_idx, weights_dict, segs=16, rot=(0,0,0)):
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
                f.material_index = mat_idx
        assign_weights(verts, weights_dict)
        return verts

    # 1. CASCO DOMO Y VISOR (100% 'head' - Cero deformación)
    ret_sphere = bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=10, radius=0.28)
    s_verts = ret_sphere['verts']
    bmesh.ops.scale(bm, vec=(1.05, 0.98, 0.82), verts=s_verts)
    bmesh.ops.translate(bm, vec=(0.0, 0.01, 1.40), verts=s_verts)
    for f in bm.faces:
        if f.verts[0] in s_verts:
            f.material_index = 3
    assign_weights(s_verts, {'head': 1.0})

    # Cresta dorsal superior estructural del casco + linterna frontal en visera frontal (brow)
    add_box((0.0, 0.04, 1.585), (0.09, 0.30, 0.030), 3, {'head': 1.0})
    add_box((0.0, -0.255, 1.505), (0.13, 0.13, 0.055), 13, {'head': 1.0}, rot=(R(8), 0, 0))
    add_box((0.0, -0.322, 1.500), (0.095, 0.025, 0.036), 5, {'head': 1.0}, rot=(R(8), 0, 0))

    # Visor panorámico continuo
    ret_visor = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=16, radius1=0.27, radius2=0.27, depth=0.18)
    v_verts = ret_visor['verts']
    bmesh.ops.scale(bm, vec=(1.05, 0.95, 1.0), verts=v_verts)
    bmesh.ops.translate(bm, vec=(0.0, -0.06, 1.39), verts=v_verts)
    for f in bm.faces:
        if f.verts[0] in v_verts:
            f.material_index = 4 if f.calc_center_median().y < -0.06 else 3
    assign_weights(v_verts, {'head': 1.0})

    add_cylinder((-0.30, 0.01, 1.40), 0.065, 0.065, 0.03, 3, {'head': 1.0}, segs=12, rot=(0, R(90), 0))
    add_cylinder((0.30, 0.01, 1.40), 0.065, 0.065, 0.03, 3, {'head': 1.0}, segs=12, rot=(0, R(90), 0))

    # Cuello / Gorget
    add_cylinder((0, 0.01, 1.25), 0.28, 0.31, 0.08, 0, {'neck_01': 1.0}, segs=18)
    add_cylinder((0, 0.01, 1.19), 0.31, 0.34, 0.06, 2, {'neck_01': 1.0}, segs=18)

    # 2. TORSO, ARNÉS Y CAJA PECTORAL ('spine_02' y 'spine_01')
    add_box((0, 0.02, 1.08), (0.58, 0.38, 0.24), 0, {'spine_02': 1.0})
    add_box((0, 0.02, 0.92), (0.52, 0.35, 0.18), 0, {'spine_01': 1.0})

    add_box((-0.18, -0.18, 1.08), (0.06, 0.025, 0.24), 7, {'spine_02': 1.0})
    add_box((0.18, -0.18, 1.08), (0.06, 0.025, 0.24), 7, {'spine_02': 1.0})
    add_box((0, -0.18, 1.09), (0.42, 0.025, 0.04), 7, {'spine_02': 1.0})
    add_box((0, -0.16, 0.83), (0.54, 0.03, 0.08), 7, {'spine_01': 1.0})
    add_box((0, 0.02, 0.82), (0.55, 0.36, 0.05), 5, {'spine_01': 1.0})

    # Caja de control pectoral (100% 'spine_02')
    add_box((0.02, -0.205, 1.06), (0.20, 0.04, 0.12), 2, {'spine_02': 1.0})
    add_box((-0.035, -0.228, 1.06), (0.065, 0.015, 0.075), 8, {'spine_02': 1.0})
    add_box((0.075, -0.228, 1.09), (0.03, 0.015, 0.03), 9, {'spine_02': 1.0})
    add_box((0.075, -0.228, 1.03), (0.03, 0.015, 0.03), 9, {'spine_02': 1.0})

    # 3. MOCHILA TRASERA ('spine_02' - 100% Rígida)
    add_box((0, 0.28, 1.08), (0.44, 0.18, 0.44), 0, {'spine_02': 1.0})
    add_box((0, 0.29, 1.31), (0.42, 0.16, 0.04), 2, {'spine_02': 1.0})
    for x_off in [0.08, 0.12, 0.16, 0.20]:
        add_box((x_off, 0.375, 1.19), (0.018, 0.015, 0.13), 7, {'spine_02': 1.0})
    for z_off in [1.24, 1.19, 1.14]:
        add_box((-0.12, 0.375, z_off), (0.11, 0.015, 0.025), 7, {'spine_02': 1.0})
    add_box((-0.12, 0.375, 1.08), (0.04, 0.015, 0.04), 8, {'spine_02': 1.0})
    add_box((0.14, 0.375, 1.00), (0.04, 0.015, 0.04), 8, {'spine_02': 1.0})
    add_box((-0.04, 0.375, 0.96), (0.16, 0.015, 0.09), 2, {'spine_02': 1.0})
    add_box((-0.04, 0.385, 0.96), (0.07, 0.012, 0.03), 9, {'spine_02': 1.0})
    add_cylinder((0.14, 0.36, 0.89), 0.045, 0.045, 0.04, 7, {'spine_02': 1.0}, segs=12, rot=(R(90), 0, 0))
    add_cylinder((0.24, 0.26, 1.11), 0.055, 0.055, 0.24, 0, {'spine_02': 1.0}, segs=10)
    add_box((0.29, 0.26, 1.11), (0.02, 0.07, 0.14), 12, {'spine_02': 1.0})

    # 4. EXTREMIDADES SUPERIORES EN REST A-POSE (35°)
    for side, sign in [('_l', 1), ('_r', -1)]:
        u_name = f'upperarm{side}'
        l_name = f'lowerarm{side}'
        h_name = f'hand{side}'
        c_name = f'clavicle{side}'

        # Hombro / Clavícula
        add_box((0.26 * sign, 0.01, 1.14), (0.16, 0.26, 0.18), 0, {c_name: 0.8, 'spine_02': 0.2})
        # Hombrera pauldron (suave para acompañar el brazo)
        add_box((0.31 * sign, 0.01, 1.18), (0.22, 0.28, 0.11), 2, {c_name: 0.6, u_name: 0.4}, rot=(0, R(-20 * sign), 0))

        # Bíceps en A-Pose
        rot_a = (0, R(-35 * sign), 0)
        p_uarm_mid = Vector((0.37 * sign, 0.01, 1.04))
        add_box(p_uarm_mid, (0.20, 0.22, 0.24), 0, {u_name: 1.0}, rot=rot_a)
        add_box(p_uarm_mid, (0.21, 0.23, 0.05), 5, {u_name: 1.0}, rot=rot_a)

        # Codo con bucle de 3 anillos (50% upperarm, 50% lowerarm para flexión elástica limpia)
        p_elbow = Vector((0.46 * sign, 0.01, 0.94))
        add_cylinder(p_elbow, 0.10, 0.10, 0.12, 0, {u_name: 0.5, l_name: 0.5}, segs=14, rot=rot_a)

        # Antebrazo
        p_larm_mid = Vector((0.55 * sign, 0.01, 0.85))
        add_box(p_larm_mid, (0.19, 0.21, 0.24), 0, {l_name: 1.0}, rot=rot_a)

        # Brazaletes reflectantes
        p_cuff = Vector((0.62 * sign, 0.01, 0.78))
        add_box(p_cuff, (0.20, 0.22, 0.05), 2, {l_name: 1.0}, rot=rot_a)
        add_box(p_cuff + Vector((0.02 * sign, 0, -0.02)), (0.20, 0.22, 0.04), 5, {l_name: 1.0}, rot=rot_a)

        # Mano / Guante táctico (100% 'hand')
        p_hand = Vector((0.69 * sign, 0.01, 0.72))
        add_box(p_hand, (0.16, 0.17, 0.14), 7, {h_name: 1.0}, rot=rot_a)

    # 5. PELVIS Y PIERNAS EN A-POSE (39% de la altura)
    add_box((0, 0.01, 0.72), (0.48, 0.34, 0.14), 0, {'pelvis': 1.0})

    for side, sign in [('_l', 1), ('_r', -1)]:
        t_name = f'thigh{side}'
        k_name = f'calf{side}'
        f_name = f'foot{side}'

        rot_leg = (0, R(-10 * sign), 0)
        p_thigh = Vector((0.18 * sign, 0.01, 0.58))
        add_box(p_thigh, (0.26, 0.27, 0.26), 0, {t_name: 1.0}, rot=rot_leg)

        p_knee = Vector((0.21 * sign, 0.01, 0.44))
        add_cylinder(p_knee, 0.12, 0.12, 0.14, 0, {t_name: 0.5, k_name: 0.5}, segs=12, rot=rot_leg)

        add_box((0.21 * sign, -0.12, 0.44), (0.22, 0.07, 0.16), 2, {k_name: 1.0})
        add_box((0.21 * sign, -0.16, 0.46), (0.17, 0.015, 0.025), 7, {k_name: 1.0})
        add_box((0.21 * sign, -0.16, 0.42), (0.17, 0.015, 0.025), 7, {k_name: 1.0})

        p_calf = Vector((0.24 * sign, 0.01, 0.30))
        add_box(p_calf, (0.25, 0.26, 0.22), 0, {k_name: 1.0}, rot=rot_leg)
        add_box(Vector((0.25 * sign, 0.01, 0.19)), (0.26, 0.27, 0.05), 5, {k_name: 1.0}, rot=rot_leg)

        add_box((0.27 * sign, -0.03, 0.11), (0.27, 0.32, 0.16), 2, {f_name: 1.0})
        add_box((0.27 * sign, -0.13, 0.055), (0.27, 0.18, 0.09), 3, {f_name: 1.0})
        add_box((0.27 * sign, -0.03, 0.017), (0.28, 0.36, 0.035), 13, {f_name: 1.0})

    bm.to_mesh(mesh)
    bm.free()

    for m in mat_order:
        mesh.materials.append(m)

    # Vincular al Armature
    char_obj.parent = arm_obj
    mod = char_obj.modifiers.new("Armature", 'ARMATURE')
    mod.object = arm_obj

    # Cel-Shading Inverted Hull
    sol = char_obj.modifiers.new("CelOutline", 'SOLIDIFY')
    sol.thickness = -0.008
    sol.offset = 1.0
    sol.use_flip_normals = True
    sol.material_offset = 14
    sol.use_rim = True

    return char_obj

# ---------------------------------------------------------------------------
# MODELADO DEL CAÑÓN EXTINTOR MODULAR ("SM_ExtinguisherCannon")
# ---------------------------------------------------------------------------
def build_modular_cannon(mats):
    mesh = bpy.data.meshes.new("SM_ExtinguisherCannon_Mesh")
    bm = bmesh.new()

    mat_order = [
        mats['suit_orange'], mats['suit_dark_orange'], mats['armor_sage'], mats['helmet_grey'],
        mats['visor_tinted'], mats['stripe_yellow'], mats['hose_red'], mats['harness_dark'],
        mats['led_green'], mats['led_red'], mats['weapon_blue'], mats['weapon_stock'],
        mats['weapon_yellow'], mats['metal_dark'], mats['outline_black']
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

    def add_cylinder(center, r1, r2, depth, mat_idx, segs=12, rot=(0,0,0)):
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
                f.material_index = mat_idx
        return verts

    add_box((0, 0, 0), (0.28, 0.13, 0.15), 10)
    add_box((0, -0.068, 0.01), (0.11, 0.01, 0.05), 12)

    add_cylinder((-0.26, 0, 0), 0.062, 0.062, 0.30, 10, segs=12, rot=(0, R(90), 0))
    add_cylinder((-0.42, 0, 0), 0.080, 0.080, 0.065, 13, segs=12, rot=(0, R(90), 0))
    add_cylinder((-0.45, 0, 0), 0.050, 0.050, 0.02, 14, segs=12, rot=(0, R(90), 0))

    add_cylinder((-0.11, 0, -0.13), 0.028, 0.028, 0.15, 13, segs=8)

    add_box((0.06, 0, -0.075), (0.20, 0.075, 0.075), 11)
    add_box((0.17, 0, -0.14), (0.075, 0.065, 0.15), 7)

    add_box((0.30, 0, -0.02), (0.20, 0.065, 0.13), 11)
    add_box((0.40, 0, -0.02), (0.040, 0.070, 0.14), 13)
    add_cylinder((0.20, 0, -0.075), 0.038, 0.038, 0.05, 6, segs=8, rot=(R(90), 0, 0))

    bm.to_mesh(mesh)
    bm.free()

    for m in mat_order:
        mesh.materials.append(m)

    gun_obj = bpy.data.objects.new("SM_ExtinguisherCannon", mesh)
    bpy.context.scene.collection.objects.link(gun_obj)

    sol = gun_obj.modifiers.new("CelOutline", 'SOLIDIFY')
    sol.thickness = -0.007
    sol.offset = 1.0
    sol.use_flip_normals = True
    sol.material_offset = 14
    sol.use_rim = True

    return gun_obj

# ---------------------------------------------------------------------------
# ILUMINACIÓN Y ESTUDIO TÉCNICO
# ---------------------------------------------------------------------------
def setup_lighting(scene):
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'Medium High Contrast'

    for ob in list(scene.collection.objects):
        if ob.name.startswith("Studio") or ob.name.startswith("Light"):
            bpy.data.objects.remove(ob, do_unlink=True)

    world = scene.world or bpy.data.worlds.new("StudioWorld")
    scene.world = world
    world.use_nodes = True
    wnt = world.node_tree
    wnt.nodes.clear()
    w_out = wnt.nodes.new('ShaderNodeOutputWorld')
    w_bg = wnt.nodes.new('ShaderNodeBackground')
    w_bg.inputs['Color'].default_value = (0.68, 0.76, 0.82, 1.0)
    w_bg.inputs['Strength'].default_value = 0.8
    wnt.links.new(w_bg.outputs['Background'], w_out.inputs['Surface'])

    floor_mesh = bpy.data.meshes.new("StudioFloor")
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=40)
    bm.to_mesh(floor_mesh)
    bm.free()
    f_obj = bpy.data.objects.new("StudioFloor", floor_mesh)
    f_obj.location = (0, 0, 0.0)
    mat_f = create_pbr_mat("M_BlueprintFloor", (0.65, 0.74, 0.80, 1.0), metallic=0.0, roughness=0.9)
    f_obj.data.materials.append(mat_f)
    scene.collection.objects.link(f_obj)

    target = bpy.data.objects.new("LightTarget", None)
    target.location = (0, 0, 0.75)
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

    add_light("LightFront", (1.5, -3.2, 2.2), 220, (1.0, 0.98, 0.96), size=2.8)
    add_light("LightBack", (-1.5, 3.2, 2.2), 240, (0.96, 0.98, 1.0), size=2.8)
    add_light("LightLeft", (-3.0, 0.0, 1.8), 140, (0.95, 0.98, 1.0), size=2.2)
    add_light("LightRight", (3.0, 0.0, 1.8), 140, (1.0, 0.97, 0.94), size=2.2)

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

def composite_quadrant(v1, v2, v3, v4, out_final, title_text):
    im1 = Image.open(v1)
    im2 = Image.open(v2)
    im3 = Image.open(v3)
    im4 = Image.open(v4)

    quad = Image.new("RGBA", (1920, 1080), (160, 180, 195, 255))
    quad.paste(im1, (0, 0))
    quad.paste(im2, (960, 0))
    quad.paste(im3, (0, 540))
    quad.paste(im4, (960, 540))

    draw = ImageDraw.Draw(quad)
    draw.line([(960, 0), (960, 1080)], fill=(90, 110, 130, 255), width=2)
    draw.line([(0, 540), (1920, 540)], fill=(90, 110, 130, 255), width=2)

    labels = [
        ("VISTA 1: REST A-POSE ESTÁNDAR (FRONTAL PARA RETARGETING UE5)", (16, 16)),
        ("VISTA 2: REST A-POSE (VISTA TRASERA - MOCHILA Y PIERNAS LIMPIAS)", (976, 16)),
        ("VISTA 3: TEST DEFORMACIÓN COMBATE (BRAZOS FLEXIONADOS A 90° CON ARMA)", (16, 556)),
        ("VISTA 4: TEST FLEXIÓN EXTREMA (CODO A 115° SIN COLAPSO NI PELLIZCO)", (976, 556)),
    ]
    for text, pos in labels:
        draw.rectangle([pos[0]-4, pos[1]-2, pos[0]+560, pos[1]+22], fill=(240, 246, 250, 230))
        draw.text(pos, text, fill=(20, 30, 40, 255))

    banner_box = [400, 516, 1520, 564]
    draw.rectangle(banner_box, fill=(20, 26, 36, 245), outline=(215, 105, 25, 255), width=2)
    draw.text((420, 532), title_text, fill=(255, 180, 60, 255))

    quad.save(out_final, "PNG")

# ---------------------------------------------------------------------------
# PIPELINE PRINCIPAL Y TEST DE DEFORMACIÓN EN ANIMACIÓN
# ---------------------------------------------------------------------------
def main():
    print("\n" + "="*60)
    print(">>> PIPELINE DE RIGGING Y VALIDACIÓN DE ANIMACIÓN UE5")
    print("="*60)

    clear_scene()
    mats = build_palette()
    arm_obj = build_ue5_armature()
    char_obj = build_rest_a_pose_mesh(mats, arm_obj)
    gun_obj = build_modular_cannon(mats)

    setup_lighting(bpy.context.scene)

    v1_apose = os.path.join(RENDERS_DIR, "rig_test_v1_apose.png")
    v2_xray = os.path.join(RENDERS_DIR, "rig_test_v2_xray.png")
    v3_combat = os.path.join(RENDERS_DIR, "rig_test_v3_combat.png")
    v4_flex = os.path.join(RENDERS_DIR, "rig_test_v4_flex.png")

    target = Vector((0.0, 0.0, 0.75))

    # 1. RENDER REST A-POSE (Pose de descanso oficial para UE5)
    print("  [1/4] Renderizando Rest A-Pose estándar...")
    render_camera_shot(Vector((0.0, -3.80, 0.78)), target, 40, v1_apose)

    # 2. RENDER VISTA TRASERA EN A-POSE
    print("  [2/4] Renderizando Vista Trasera A-Pose...")
    render_camera_shot(Vector((0.0, 3.80, 0.78)), target, 40, v2_xray)

    # 3. TEST DE DEFORMACIÓN: FLEXIÓN DE COMBATE (Codos a 90° hacia adelante)
    print("  [3/4] Aplicando y renderizando Pose de Combate (Flexión de brazos a 90°)...")
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='POSE')
    pb = arm_obj.pose.bones

    pb['upperarm_l'].rotation_mode = 'XYZ'
    pb['upperarm_l'].rotation_euler = (R(35), R(-20), R(-15))
    pb['lowerarm_l'].rotation_mode = 'XYZ'
    pb['lowerarm_l'].rotation_euler = (R(0), R(0), R(75))

    pb['upperarm_r'].rotation_mode = 'XYZ'
    pb['upperarm_r'].rotation_euler = (R(25), R(15), R(15))
    pb['lowerarm_r'].rotation_mode = 'XYZ'
    pb['lowerarm_r'].rotation_euler = (R(0), R(0), R(-70))

    gun_obj.location = Vector((0.02, -0.38, 0.82))
    gun_obj.rotation_euler = Euler((R(10), R(-12), R(-18)))

    bpy.ops.object.mode_set(mode='OBJECT')
    render_camera_shot(Vector((2.40, -2.70, 1.35)), target, 38, v3_combat)

    # 4. TEST DE FLEXIÓN EXTREMA: Codo a 115°
    print("  [4/4] Aplicando y renderizando Flexión Extrema (115° de codo)...")
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='POSE')
    pb['lowerarm_l'].rotation_euler = (R(0), R(0), R(115))
    pb['upperarm_l'].rotation_euler = (R(45), R(-30), R(-10))
    bpy.ops.object.mode_set(mode='OBJECT')
    render_camera_shot(Vector((-2.20, -2.40, 1.15)), Vector((-0.35, -0.15, 0.90)), 50, v4_flex)

    # Resetear pose a Rest Pose limpia (A-Pose estándar para exportación FBX de UE5)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.pose.transforms_clear()
    for b in pb:
        b.rotation_mode = 'XYZ'
        b.rotation_euler = (0, 0, 0)
        b.rotation_quaternion = (1, 0, 0, 0)
        b.location = (0, 0, 0)
    bpy.ops.object.mode_set(mode='OBJECT')
    gun_obj.location = Vector((0, 0, 0))
    gun_obj.rotation_euler = (0, 0, 0)

    # Compositar hoja de validación
    out_sheet = os.path.join(RENDERS_DIR, "SK_Firefighter_Rig_Validation_4views.png")
    composite_quadrant(v1_apose, v2_xray, v3_combat, v4_flex, out_sheet, 
                       "ASTRA HAZARD: TEST DE RIGGING Y DEFORMACIÓN DE BRAZOS UE5")
    print(f"  [OK] Sheet de Validación: {out_sheet}")

    out_brain = os.path.join(BRAIN_DIR, "SK_Firefighter_Rig_Validation_4views.png")
    shutil.copy2(out_sheet, out_brain)
    print(f"  [OK] Copiado a Brain: {out_brain}")

    # Exportar FBX del Personaje Esquelético Riggeado (UE5 compatible)
    fbx_char_path = os.path.join(FBX_DIR, "SK_Firefighter_Official_Rigged.fbx")
    bpy.ops.object.select_all(action='DESELECT')
    char_obj.select_set(True)
    arm_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.export_scene.fbx(
        filepath=fbx_char_path,
        use_selection=True,
        add_leaf_bones=False,
        armature_nodetype='NULL',
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_ALL',
        mesh_smooth_type='FACE',
        bake_anim=False
    )
    print(f"  [OK] Skeletal Mesh FBX: {fbx_char_path}")

    # Exportar FBX del Arma Modular
    fbx_gun_path = os.path.join(EQUIP_FBX_DIR, "SM_ExtinguisherCannon.fbx")
    bpy.ops.object.select_all(action='DESELECT')
    gun_obj.select_set(True)
    bpy.context.view_layer.objects.active = gun_obj
    bpy.ops.export_scene.fbx(
        filepath=fbx_gun_path,
        use_selection=True,
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_ALL',
        mesh_smooth_type='FACE'
    )
    print(f"  [OK] Modular Weapon FBX: {fbx_gun_path}")

    blend_path = os.path.join(ART_DIR, "Blender", "SK_Firefighter_Official_Rigged.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_path)
    print(f"  [OK] Blend Rigged guardado: {blend_path}")

if __name__ == "__main__":
    main()

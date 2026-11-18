"""
generar_testdummy_fiel_referencia.py
Generador oficial 1:1 de máxima fidelidad: Muñeco de Pruebas (SK_TestDummy_Ragdoll).
Basado estrictamente en el Model Sheet de referencia conceptual (media_1791137482814.png).
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

BONE_NAMES = [
    'root', 'pelvis', 'spine_01', 'spine_02', 'neck_01', 'head',
    'clavicle_l', 'upperarm_l', 'lowerarm_l', 'hand_l',
    'clavicle_r', 'upperarm_r', 'lowerarm_r', 'hand_r',
    'thigh_l', 'calf_l', 'foot_l',
    'thigh_r', 'calf_r', 'foot_r'
]

# -------------------------------------------------------------------------
# MATERIALES PBR FIDELIDAD 1:1 (CALIBRADOS CON LA REFERENCIA)
# -------------------------------------------------------------------------
def create_testdummy_materials():
    mats = {}

    def new_pbr(name, base_color, roughness=0.55, metallic=0.0, emission=None, emission_strength=1.0, is_burlap=False):
        mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
        mat.use_nodes = True
        nt = mat.node_tree
        nt.nodes.clear()

        out = nt.nodes.new('ShaderNodeOutputMaterial')
        bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
        bsdf.inputs['Base Color'].default_value = base_color
        bsdf.inputs['Roughness'].default_value = roughness
        bsdf.inputs['Metallic'].default_value = metallic

        if emission:
            if 'Emission Color' in bsdf.inputs:
                bsdf.inputs['Emission Color'].default_value = emission
                bsdf.inputs['Emission Strength'].default_value = emission_strength
            else:
                bsdf.inputs['Emission'].default_value = emission

        if is_burlap:
            tex_coord = nt.nodes.new('ShaderNodeTexCoord')
            noise = nt.nodes.new('ShaderNodeTexNoise')
            noise.inputs['Scale'].default_value = 110.0
            noise.inputs['Detail'].default_value = 6.0
            noise.inputs['Roughness'].default_value = 0.90

            bump = nt.nodes.new('ShaderNodeBump')
            bump.inputs['Strength'].default_value = 0.35
            bump.inputs['Distance'].default_value = 0.03

            nt.links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])
            nt.links.new(noise.outputs['Fac'], bump.inputs['Height'])
            nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

        nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
        return mat

    # 1. Tela de arpillera beige/arena cálida para cabeza y manos
    mats['burlap'] = new_pbr("M_Dummy_Burlap", (0.55, 0.47, 0.36, 1.0), roughness=0.88, is_burlap=True)
    
    # 2. Hilo oscuro carbón de costuras y ojos en X
    mats['stitches'] = new_pbr("M_Dummy_Stitches", (0.04, 0.035, 0.03, 1.0), roughness=0.95)

    # 3. Sudadera y pantalón verde salvia / olive drab cálido
    mats['sage_suit'] = new_pbr("M_Dummy_SageSuit", (0.14, 0.24, 0.17, 1.0), roughness=0.62)

    # 4. Verde salvia oscuro para mochilas, parches y bolsillos
    mats['sage_dark'] = new_pbr("M_Dummy_SageDark", (0.09, 0.17, 0.11, 1.0), roughness=0.58)

    # 5. Cordones blancos de la sudadera y parches de tela blanca
    mats['white_drawstrings'] = new_pbr("M_Dummy_WhiteStrings", (0.86, 0.88, 0.86, 1.0), roughness=0.40)

    # 6. Cremallera y hebillas metálicas plateadas
    mats['metal_trim'] = new_pbr("M_Dummy_MetalZip", (0.65, 0.68, 0.72, 1.0), roughness=0.20, metallic=0.95)

    # 7. Cuero marrón medio para cinturón táctico y cartucheras
    mats['leather_belt'] = new_pbr("M_Dummy_LeatherBelt", (0.24, 0.15, 0.08, 1.0), roughness=0.50)

    # 8. Cuero marrón cálido oscuro para botas pesadas
    mats['boots_brown'] = new_pbr("M_Dummy_BootsBrown", (0.11, 0.06, 0.03, 1.0), roughness=0.48)

    # 9. Goma negra de suelas y bisagras mecánicas de articulación
    mats['black_hinge'] = new_pbr("M_Dummy_BlackHinge", (0.03, 0.03, 0.035, 1.0), roughness=0.65, metallic=0.1)

    # 10. Diana de choque amarillo vivo de seguridad
    mats['target_yellow'] = new_pbr("M_Dummy_TargetYellow", (1.0, 0.78, 0.0, 1.0), roughness=0.25)

    # 11. Diana de choque negro profundo
    mats['target_black'] = new_pbr("M_Dummy_TargetBlack", (0.015, 0.015, 0.015, 1.0), roughness=0.40)

    # 12. Pantalla LED verde fluorescente en la muñeca
    mats['screen_neon'] = new_pbr("M_Dummy_ScreenNeon", (0.20, 1.0, 0.15, 1.0), roughness=0.1, emission=(0.20, 1.0, 0.15, 1.0), emission_strength=5.0)

    # 13. Máscara de respiración colgante (oliva táctico)
    mats['respirator'] = new_pbr("M_Dummy_Respirator", (0.08, 0.14, 0.10, 1.0), roughness=0.50)

    # 14. Cuerda colgante enrollada (cáñamo/tan)
    mats['rope_tan'] = new_pbr("M_Dummy_RopeTan", (0.58, 0.49, 0.35, 1.0), roughness=0.80)

    # 15. Estera de acampada enrollada (verde sage enrollado)
    mats['bedroll'] = new_pbr("M_Dummy_Bedroll", (0.16, 0.27, 0.19, 1.0), roughness=0.65)

    return mats

# -------------------------------------------------------------------------
# ESQUELETO BIPEDAL ESTÁNDAR PARA UNREAL ENGINE 5
# -------------------------------------------------------------------------
def create_testdummy_armature():
    arm_data = bpy.data.armatures.new("Armature_SK_TestDummy")
    arm_obj = bpy.data.objects.new("SK_TestDummy_Armature", arm_data)
    bpy.context.scene.collection.objects.link(arm_obj)
    bpy.context.view_layer.objects.active = arm_obj

    bpy.ops.object.mode_set(mode='EDIT')
    eb = arm_data.edit_bones

    root = eb.new('root')
    root.head = (0, 0, 0)
    root.tail = (0, 0, 0.1)

    pelvis = eb.new('pelvis')
    pelvis.head = (0, 0, 0.68)
    pelvis.tail = (0, 0, 0.78)
    pelvis.parent = root

    spine1 = eb.new('spine_01')
    spine1.head = (0, 0, 0.78)
    spine1.tail = (0, 0, 0.92)
    spine1.parent = pelvis

    spine2 = eb.new('spine_02')
    spine2.head = (0, 0, 0.92)
    spine2.tail = (0, 0, 1.10)
    spine2.parent = spine1

    neck = eb.new('neck_01')
    neck.head = (0, 0, 1.10)
    neck.tail = (0, 0, 1.18)
    neck.parent = spine2

    head = eb.new('head')
    head.head = (0, 0, 1.18)
    head.tail = (0, 0, 1.54)
    head.parent = neck

    for side, sign in [('_l', 1), ('_r', -1)]:
        clav = eb.new(f'clavicle{side}')
        clav.head = (0, 0, 1.08)
        clav.tail = (0.16 * sign, 0, 1.05)
        clav.parent = spine2

        uarm = eb.new(f'upperarm{side}')
        uarm.head = (0.16 * sign, 0, 1.05)
        uarm.tail = (0.22 * sign, 0, 0.84)
        uarm.parent = clav

        larm = eb.new(f'lowerarm{side}')
        larm.head = (0.22 * sign, 0, 0.84)
        larm.tail = (0.23 * sign, 0, 0.66)
        larm.parent = uarm

        hand = eb.new(f'hand{side}')
        hand.head = (0.23 * sign, 0, 0.66)
        hand.tail = (0.23 * sign, 0, 0.52)
        hand.parent = larm

    for side, sign in [('_l', 1), ('_r', -1)]:
        thigh = eb.new(f'thigh{side}')
        thigh.head = (0.11 * sign, 0, 0.68)
        thigh.tail = (0.11 * sign, 0, 0.40)
        thigh.parent = pelvis

        calf = eb.new(f'calf{side}')
        calf.head = (0.11 * sign, 0, 0.40)
        calf.tail = (0.11 * sign, 0, 0.16)
        calf.parent = thigh

        foot = eb.new(f'foot{side}')
        foot.head = (0.11 * sign, 0, 0.16)
        foot.tail = (0.11 * sign, -0.16, 0.0)
        foot.parent = calf

    bpy.ops.object.mode_set(mode='OBJECT')
    return arm_obj

# -------------------------------------------------------------------------
# CONSTRUCCIÓN DE LA MALLA COMPLETA 1:1 CON ALTA FIDELIDAD VISUAL
# -------------------------------------------------------------------------
def build_testdummy_mesh(materials, arm_obj):
    mesh = bpy.data.meshes.new("SK_TestDummy_Ragdoll_Mesh")
    char_obj = bpy.data.objects.new("SK_TestDummy_Ragdoll", mesh)
    bpy.context.scene.collection.objects.link(char_obj)

    group_map = {}
    for bname in BONE_NAMES:
        vg = char_obj.vertex_groups.new(name=bname)
        group_map[bname] = vg.index

    bm = bmesh.new()
    dlayer = bm.verts.layers.deform.verify()

    mat_keys = [
        'burlap',           # 0
        'stitches',         # 1
        'sage_suit',        # 2
        'sage_dark',        # 3
        'white_drawstrings',# 4
        'metal_trim',       # 5
        'leather_belt',     # 6
        'boots_brown',      # 7
        'black_hinge',      # 8
        'target_yellow',    # 9
        'target_black',     # 10
        'screen_neon',      # 11
        'respirator',       # 12
        'rope_tan',         # 13
        'bedroll'           # 14
    ]

    mat_idx_map = {k: i for i, k in enumerate(mat_keys)}

    def assign_weights(verts, weights_dict):
        for v in verts:
            for bname, w in weights_dict.items():
                if bname in group_map:
                    v[dlayer][group_map[bname]] = w

    def tag_smooth_faces(verts, mat_key, smooth=True):
        idx = mat_idx_map[mat_key]
        for f in bm.faces:
            if f.verts[0] in verts:
                f.material_index = idx
                f.smooth = smooth

    def add_box(center, size, mat_key, bone_dict, rot=(0,0,0), smooth=True):
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
        tag_smooth_faces(verts, mat_key, smooth=smooth)
        assign_weights(verts, bone_dict)
        return verts

    def add_cylinder(center, r1, r2, depth, mat_key, bone_dict, segs=20, rot=None, smooth=True):
        ret = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=segs, radius1=r1, radius2=r2, depth=depth)
        verts = ret['verts']
        if rot:
            mat_rot = Euler(rot).to_matrix().to_4x4()
            bmesh.ops.transform(bm, matrix=mat_rot, verts=verts)
        bmesh.ops.translate(bm, vec=center, verts=verts)
        tag_smooth_faces(verts, mat_key, smooth=smooth)
        assign_weights(verts, bone_dict)
        return verts

    def add_uv_sphere(center, radius, mat_key, bone_dict, u_segs=32, v_segs=24, scale=(1,1,1), smooth=True):
        ret = bmesh.ops.create_uvsphere(bm, u_segments=u_segs, v_segments=v_segs, radius=radius)
        verts = ret['verts']
        if scale != (1, 1, 1):
            bmesh.ops.scale(bm, vec=scale, verts=verts)
        bmesh.ops.translate(bm, vec=center, verts=verts)
        tag_smooth_faces(verts, mat_key, smooth=smooth)
        assign_weights(verts, bone_dict)
        return verts

    def add_crash_target(center, radius, bone_dict, normal_axis='Z'):
        """Crea una diana de choque circular de 4 cuadrantes alternados con cap_tris=True."""
        depth = 0.008
        segs = 24
        # IMPORTANTE: cap_tris=True genera caras triangulares radiales para permitir cuadrantes
        ret = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=True, segments=segs, radius1=radius, radius2=radius, depth=depth)
        verts = ret['verts']
        
        if normal_axis == 'X+':
            rot_m = Euler((0, R(90), 0)).to_matrix().to_4x4()
            bmesh.ops.transform(bm, matrix=rot_m, verts=verts)
        elif normal_axis == 'X-':
            rot_m = Euler((0, R(-90), 0)).to_matrix().to_4x4()
            bmesh.ops.transform(bm, matrix=rot_m, verts=verts)
        elif normal_axis == 'Y-':
            rot_m = Euler((R(-90), 0, 0)).to_matrix().to_4x4()
            bmesh.ops.transform(bm, matrix=rot_m, verts=verts)
        elif normal_axis == 'Y+':
            rot_m = Euler((R(90), 0, 0)).to_matrix().to_4x4()
            bmesh.ops.transform(bm, matrix=rot_m, verts=verts)

        bmesh.ops.translate(bm, vec=center, verts=verts)

        idx_y = mat_idx_map['target_yellow']
        idx_b = mat_idx_map['target_black']
        c_vec = Vector(center)

        for f in bm.faces:
            if f.verts[0] in verts:
                f.smooth = True
                f_cen = f.calc_center_median() - c_vec
                if normal_axis in ['X+', 'X-']:
                    u, v = f_cen.y, f_cen.z
                elif normal_axis in ['Y+', 'Y-']:
                    u, v = f_cen.x, f_cen.z
                else:
                    u, v = f_cen.x, f_cen.y
                
                ang = math.atan2(v, u)
                if ang < 0:
                    ang += 2 * math.pi
                quadrant = int((ang / (math.pi / 2))) % 4
                if quadrant in [0, 2]:
                    f.material_index = idx_y
                else:
                    f.material_index = idx_b

        assign_weights(verts, bone_dict)
        return verts

    # ---------------------------------------------------------------------
    # 1. CABEZA DE ARPILLERA (SACKCLOTH), OJOS EN 'X' GRANDES Y COSTURAS
    # ---------------------------------------------------------------------
    head_center = (0, 0.01, 1.34)
    head_radius = 0.205
    # Esfera ligeramente ovoide
    add_uv_sphere(head_center, head_radius, 'burlap', {'head': 1.0}, u_segs=36, v_segs=28, scale=(1.02, 1.04, 1.12), smooth=True)

    # Costura sagital central en relieve (cordón continuo + 24 puntadas transversales)
    for i in range(24):
        t = -math.pi/2 + (i / 23.0) * math.pi
        sy = head_center[1] + (head_radius * 1.04 + 0.003) * math.sin(t)
        sz = head_center[2] + (head_radius * 1.12 + 0.003) * math.cos(t)
        add_box((0, sy, sz), (0.028, 0.006, 0.006), 'stitches', {'head': 1.0}, rot=(t, 0, 0), smooth=False)

    # Ojos en X (dos cruces GRANDES y gruesas de hilo oscuro como en la referencia)
    eye_z = 1.35
    eye_y = head_center[1] - (head_radius * 1.04) + 0.002
    for eye_x in [-0.078, 0.078]:
        add_cylinder((eye_x, eye_y, eye_z), 0.010, 0.010, 0.065, 'stitches', {'head': 1.0}, segs=12, rot=(0, R(45), 0), smooth=True)
        add_cylinder((eye_x, eye_y, eye_z), 0.010, 0.010, 0.065, 'stitches', {'head': 1.0}, segs=12, rot=(0, R(-45), 0), smooth=True)

    # Sonrisa de puntadas discontinuas en arco (9 puntadas gruesas bien visibles)
    mouth_center_z = 1.23
    mouth_radius_arc = 0.095
    for i in range(9):
        ang_m = -R(65) + i * R(16.25)
        mx = mouth_radius_arc * math.sin(ang_m)
        mz = mouth_center_z - mouth_radius_arc * (1.0 - math.cos(ang_m)) * 0.40
        my = head_center[1] - (head_radius * 1.04) + 0.012
        add_box((mx, my, mz), (0.018, 0.007, 0.007), 'stitches', {'head': 1.0}, smooth=False)

    # Cuello cilíndrico
    add_cylinder((0, 0, 1.15), 0.11, 0.11, 0.08, 'burlap', {'neck_01': 1.0}, segs=20, smooth=True)

    # ---------------------------------------------------------------------
    # 2. CAPUCHA GRANDE DE LA SUDADERA Y CORDONES BLANCOS
    # ---------------------------------------------------------------------
    # Capucha envolvente alrededor del cuello
    add_cylinder((0, 0.02, 1.12), 0.20, 0.18, 0.12, 'sage_suit', {'spine_02': 1.0}, segs=24, smooth=True)
    add_uv_sphere((0, 0.11, 1.11), 0.17, 'sage_suit', {'spine_02': 1.0}, scale=(1.25, 0.85, 0.85), smooth=True)

    # ---------------------------------------------------------------------
    # 3. TORSO: SUDADERA CON CREMALLERA METÁLICA, CORDONES Y BOLSILLO CANGURO
    # ---------------------------------------------------------------------
    # Pecho contorneado suave
    add_cylinder((0, 0, 1.01), 0.20, 0.21, 0.24, 'sage_suit', {'spine_02': 1.0}, segs=24, smooth=True)
    # Abdomen suave
    add_cylinder((0, 0, 0.85), 0.21, 0.20, 0.18, 'sage_suit', {'spine_01': 1.0}, segs=24, smooth=True)

    # CREMALLERA METÁLICA VERTICAL (Colocada en el frente visible Y = -0.212)
    add_box((0, -0.212, 0.96), (0.018, 0.010, 0.30), 'metal_trim', {'spine_02': 1.0}, smooth=False)
    # Cursor/tirador de cremallera
    add_box((0, -0.220, 1.06), (0.024, 0.016, 0.035), 'metal_trim', {'spine_02': 1.0}, smooth=False)

    # CORDONES BLANCOS DE LA SUDADERA (Colocados en el frente visible Y = -0.218)
    add_cylinder((-0.075, -0.218, 1.00), 0.007, 0.007, 0.18, 'white_drawstrings', {'spine_02': 1.0}, segs=10, smooth=True)
    add_cylinder((0.075, -0.218, 1.00), 0.007, 0.007, 0.18, 'white_drawstrings', {'spine_02': 1.0}, segs=10, smooth=True)
    # Punteras metálicas de los cordones
    add_cylinder((-0.075, -0.218, 0.90), 0.009, 0.009, 0.025, 'metal_trim', {'spine_02': 1.0}, segs=10, smooth=True)
    add_cylinder((0.075, -0.218, 0.90), 0.009, 0.009, 0.025, 'metal_trim', {'spine_02': 1.0}, segs=10, smooth=True)

    # BOLSILLO CANGURO FRONTAL PLANO (Colocado en Y = -0.214)
    add_box((-0.09, -0.214, 0.82), (0.13, 0.016, 0.11), 'sage_dark', {'spine_01': 1.0}, smooth=True)
    add_box((0.09, -0.214, 0.82), (0.13, 0.016, 0.11), 'sage_dark', {'spine_01': 1.0}, smooth=True)

    # Dobladillo elástico inferior de la sudadera
    add_cylinder((0, 0, 0.74), 0.208, 0.208, 0.05, 'sage_dark', {'pelvis': 1.0}, segs=24, smooth=True)

    # ---------------------------------------------------------------------
    # 4. CINTURÓN TÁCTICO DE CUERO Y ACCESORIOS COLGANTES
    # ---------------------------------------------------------------------
    belt_z = 0.69
    add_cylinder((0, 0, belt_z), 0.212, 0.212, 0.055, 'leather_belt', {'pelvis': 1.0}, segs=24, smooth=True)
    # Hebilla metálica plateada frontal (visible en Y = -0.224)
    add_box((0, -0.224, belt_z), (0.085, 0.016, 0.065), 'metal_trim', {'pelvis': 1.0}, smooth=False)
    # Cartucheras de cuero
    add_box((-0.13, -0.220, belt_z), (0.065, 0.025, 0.060), 'leather_belt', {'pelvis': 1.0}, smooth=True)
    add_box((0.13, -0.220, belt_z), (0.065, 0.025, 0.060), 'leather_belt', {'pelvis': 1.0}, smooth=True)

    # Mini Respirador / Máscara de Gas colgando a la izquierda (X > 0)
    resp_center = (0.16, -0.20, 0.60)
    add_uv_sphere(resp_center, 0.045, 'respirator', {'pelvis': 1.0}, scale=(1.0, 1.0, 1.15), smooth=True)
    add_cylinder((0.16, -0.24, 0.59), 0.026, 0.026, 0.038, 'black_hinge', {'pelvis': 1.0}, segs=14, rot=(R(90), 0, 0), smooth=True)
    add_cylinder((0.20, -0.20, 0.59), 0.024, 0.024, 0.032, 'black_hinge', {'pelvis': 1.0}, segs=14, rot=(0, R(90), 0), smooth=True)

    # Cuerda enrollada colgando a la derecha (X < 0)
    rope_center = (-0.19, -0.05, 0.62)
    add_cylinder(rope_center, 0.042, 0.042, 0.09, 'rope_tan', {'pelvis': 1.0}, segs=18, smooth=True)
    add_box((-0.19, -0.05, 0.68), (0.02, 0.02, 0.04), 'metal_trim', {'pelvis': 1.0}, smooth=False)

    # ---------------------------------------------------------------------
    # 5. BRAZOS ORGÁNICOS NATURALES, DIANAS DE CHOQUE Y MANOS DE ARPILLERA
    # ---------------------------------------------------------------------
    for side, sign in [('_l', 1), ('_r', -1)]:
        uarm_bone = f'upperarm{side}'
        larm_bone = f'lowerarm{side}'
        hand_bone = f'hand{side}'

        # Hombro orgánico integrado a la sudadera
        sh_pos = (0.20 * sign, 0, 1.03)
        add_uv_sphere(sh_pos, 0.095, 'sage_suit', {f'clavicle{side}': 1.0}, scale=(1.05, 1.10, 1.05), smooth=True)

        # Manga superior
        uarm_pos = (0.22 * sign, 0, 0.93)
        add_cylinder(uarm_pos, 0.085, 0.078, 0.18, 'sage_suit', {uarm_bone: 1.0}, segs=20, smooth=True)
        # Diana de choque deltoide exterior
        add_crash_target((0.302 * sign, 0, 0.94), 0.044, {uarm_bone: 1.0}, normal_axis=('X+' if sign > 0 else 'X-'))

        # Codo con articulación mecánica y diana posterior
        elbow_pos = (0.23 * sign, 0, 0.82)
        add_cylinder(elbow_pos, 0.078, 0.074, 0.10, 'sage_suit', {uarm_bone: 0.5, larm_bone: 0.5}, segs=20, smooth=True)
        add_cylinder((0.23 * sign, 0.065, 0.82), 0.034, 0.034, 0.06, 'black_hinge', {larm_bone: 1.0}, segs=14, rot=(0, R(90), 0), smooth=True)
        add_crash_target((0.298 * sign, 0.02, 0.82), 0.034, {larm_bone: 1.0}, normal_axis=('X+' if sign > 0 else 'X-'))

        # Antebrazo
        larm_pos = (0.23 * sign, 0, 0.72)
        add_cylinder(larm_pos, 0.074, 0.068, 0.16, 'sage_suit', {larm_bone: 1.0}, segs=20, smooth=True)
        add_cylinder((0.23 * sign, 0, 0.635), 0.072, 0.072, 0.04, 'sage_dark', {larm_bone: 1.0}, segs=20, smooth=True)

        # Muñeca izquierda: Gauntlet táctico con pantalla LED verde
        if sign > 0:
            add_box((0.24, -0.055, 0.645), (0.055, 0.03, 0.055), 'black_hinge', {larm_bone: 1.0}, smooth=False)
            add_box((0.24, -0.075, 0.645), (0.042, 0.01, 0.042), 'screen_neon', {larm_bone: 1.0}, smooth=False)

        # Mano de arpillera
        hand_pos = (0.23 * sign, 0, 0.55)
        add_uv_sphere(hand_pos, 0.065, 'burlap', {hand_bone: 1.0}, scale=(0.95, 1.15, 1.25), smooth=True)
        thumb_pos = (0.205 * sign, -0.04, 0.56)
        add_cylinder(thumb_pos, 0.022, 0.018, 0.05, 'burlap', {hand_bone: 1.0}, segs=10, rot=(R(25), 0, R(20 * sign)), smooth=True)

        # Diana de choque en la mano/muñeca exterior
        add_crash_target((0.285 * sign, 0, 0.55), 0.030, {hand_bone: 1.0}, normal_axis=('X+' if sign > 0 else 'X-'))

    # ---------------------------------------------------------------------
    # 6. PELVIS, PANTALONES CARGO, DIANAS DE CHOQUE Y ARTICULACIÓN DE RODILLA
    # ---------------------------------------------------------------------
    add_cylinder((0, 0, 0.62), 0.19, 0.17, 0.14, 'sage_suit', {'pelvis': 1.0}, segs=24, smooth=True)

    for side, sign in [('_l', 1), ('_r', -1)]:
        thigh_bone = f'thigh{side}'
        calf_bone = f'calf{side}'
        foot_bone = f'foot{side}'

        # Muslo
        thigh_pos = (0.11 * sign, 0, 0.50)
        add_cylinder(thigh_pos, 0.092, 0.086, 0.22, 'sage_suit', {thigh_bone: 1.0}, segs=20, smooth=True)
        # Bolsillo cargo exterior
        add_box((0.195 * sign, 0, 0.48), (0.035, 0.13, 0.15), 'sage_dark', {thigh_bone: 1.0}, smooth=True)

        # Rodilla
        knee_pos = (0.11 * sign, 0, 0.38)
        add_cylinder(knee_pos, 0.086, 0.082, 0.10, 'sage_suit', {thigh_bone: 0.5, calf_bone: 0.5}, segs=20, smooth=True)
        # DIANA FRONTAL DE RODILLA (Visible en Y = -0.090)
        add_crash_target((0.11 * sign, -0.090, 0.38), 0.044, {calf_bone: 1.0}, normal_axis='Y-')
        # Diana lateral de rodilla
        add_crash_target((0.195 * sign, 0, 0.38), 0.040, {calf_bone: 1.0}, normal_axis=('X+' if sign > 0 else 'X-'))
        # Bisagra mecánica trasera de rodilla
        add_cylinder((0.11 * sign, 0.068, 0.38), 0.040, 0.040, 0.08, 'black_hinge', {calf_bone: 1.0}, segs=14, rot=(0, R(90), 0), smooth=True)

        # Pantorrilla
        calf_pos = (0.11 * sign, 0, 0.26)
        add_cylinder(calf_pos, 0.084, 0.090, 0.20, 'sage_suit', {calf_bone: 1.0}, segs=20, smooth=True)
        # Dobladillo arrugado sobre la bota
        add_cylinder((0.11 * sign, 0.15, 0.15), 0.095, 0.095, 0.05, 'sage_dark', {calf_bone: 1.0}, segs=20, smooth=True)

        # -----------------------------------------------------------------
        # 7. BOTAS MARRONES TÁCTICAS
        # -----------------------------------------------------------------
        boot_pos = (0.11 * sign, -0.02, 0.08)
        add_cylinder(boot_pos, 0.090, 0.096, 0.14, 'boots_brown', {foot_bone: 1.0}, segs=20, smooth=True)
        # Puntera redondeada
        add_uv_sphere((0.11 * sign, -0.12, 0.06), 0.068, 'boots_brown', {foot_bone: 1.0}, scale=(1.20, 1.30, 0.85), smooth=True)
        # Suela gruesa de goma marrón oscura con estrías
        sole_pos = (0.11 * sign, -0.02, 0.02)
        add_box(sole_pos, (0.16, 0.28, 0.04), 'boots_brown', {foot_bone: 1.0}, smooth=True)

    # ---------------------------------------------------------------------
    # 8. MOCHILA TÁCTICA EXPEDICIONARIA CON ESTERA ENROLLADA (BEDROLL)
    # ---------------------------------------------------------------------
    pack_center_y = 0.22
    pack_base_z = 0.94

    # Cuerpo principal de la mochila con bordes suaves
    add_box((0, pack_center_y, pack_base_z), (0.34, 0.16, 0.36), 'sage_dark', {'spine_02': 1.0}, smooth=True)
    add_box((0, pack_center_y + 0.02, pack_base_z + 0.12), (0.35, 0.18, 0.14), 'sage_suit', {'spine_02': 1.0}, smooth=True)

    # Bolsillo posterior
    add_box((0, pack_center_y + 0.10, pack_base_z - 0.05), (0.24, 0.08, 0.18), 'sage_suit', {'spine_02': 1.0}, smooth=True)
    add_box((0, pack_center_y + 0.12, pack_base_z - 0.02), (0.25, 0.06, 0.08), 'sage_dark', {'spine_02': 1.0}, smooth=True)

    # Bolsillos laterales de la mochila
    add_box((-0.19, pack_center_y, pack_base_z - 0.04), (0.08, 0.12, 0.18), 'sage_dark', {'spine_02': 1.0}, smooth=True)
    add_box((0.19, pack_center_y, pack_base_z - 0.04), (0.08, 0.12, 0.18), 'sage_dark', {'spine_02': 1.0}, smooth=True)

    # Parches blancos rectangulares 'MAS' en los bolsillos laterales
    add_box((-0.235, pack_center_y, pack_base_z - 0.04), (0.01, 0.07, 0.05), 'white_drawstrings', {'spine_02': 1.0}, smooth=False)
    add_box((0.235, pack_center_y, pack_base_z - 0.04), (0.01, 0.07, 0.05), 'white_drawstrings', {'spine_02': 1.0}, smooth=False)
    add_box((-0.242, pack_center_y, pack_base_z - 0.04), (0.005, 0.05, 0.025), 'target_black', {'spine_02': 1.0}, smooth=False)
    add_box((0.242, pack_center_y, pack_base_z - 0.04), (0.005, 0.05, 0.025), 'target_black', {'spine_02': 1.0}, smooth=False)

    # Parche dorsal superior 'MAS CORP.' debajo de la estera
    add_box((0, pack_center_y + 0.09, pack_base_z + 0.11), (0.14, 0.01, 0.06), 'white_drawstrings', {'spine_02': 1.0}, smooth=False)
    add_box((0, pack_center_y + 0.096, pack_base_z + 0.11), (0.11, 0.005, 0.03), 'target_black', {'spine_02': 1.0}, smooth=False)

    # Correas de fijación cruzando los hombros
    add_box((-0.12, -0.06, 1.05), (0.04, 0.28, 0.02), 'sage_dark', {'spine_02': 1.0}, smooth=True)
    add_box((0.12, -0.06, 1.05), (0.04, 0.28, 0.02), 'sage_dark', {'spine_02': 1.0}, smooth=True)

    # ESTERA ENROLLADA SUPERIOR (BEDROLL)
    bedroll_z = pack_base_z + 0.24
    bedroll_y = pack_center_y
    add_cylinder((0, bedroll_y, bedroll_z), 0.080, 0.080, 0.44, 'bedroll', {'spine_02': 1.0}, segs=24, rot=(0, R(90), 0), smooth=True)
    add_cylinder((-0.22, bedroll_y, bedroll_z), 0.070, 0.070, 0.02, 'sage_dark', {'spine_02': 1.0}, segs=20, rot=(0, R(90), 0), smooth=True)
    add_cylinder((0.22, bedroll_y, bedroll_z), 0.070, 0.070, 0.02, 'sage_dark', {'spine_02': 1.0}, segs=20, rot=(0, R(90), 0), smooth=True)
    # Correas y hebillas
    add_cylinder((-0.10, bedroll_y, bedroll_z), 0.088, 0.088, 0.03, 'leather_belt', {'spine_02': 1.0}, segs=20, rot=(0, R(90), 0), smooth=True)
    add_cylinder((0.10, bedroll_y, bedroll_z), 0.088, 0.088, 0.03, 'leather_belt', {'spine_02': 1.0}, segs=20, rot=(0, R(90), 0), smooth=True)
    add_box((-0.10, bedroll_y + 0.09, bedroll_z), (0.04, 0.015, 0.03), 'metal_trim', {'spine_02': 1.0}, smooth=False)
    add_box((0.10, bedroll_y + 0.09, bedroll_z), (0.04, 0.015, 0.03), 'metal_trim', {'spine_02': 1.0}, smooth=False)

    bm.to_mesh(mesh)
    bm.free()

    for k in mat_keys:
        mesh.materials.append(materials[k])

    char_obj.parent = arm_obj
    mod = char_obj.modifiers.new("Armature", 'ARMATURE')
    mod.object = arm_obj

    return char_obj

# -------------------------------------------------------------------------
# ILUMINACIÓN CINEMATOGRÁFICA DE HANGAR INDUSTRIAL (CALIBRADA)
# -------------------------------------------------------------------------
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
    w_bg.inputs['Color'].default_value = (0.06, 0.08, 0.10, 1.0)
    w_bg.inputs['Strength'].default_value = 0.35
    wnt.links.new(w_bg.outputs['Background'], w_out.inputs['Surface'])

    floor_mesh = bpy.data.meshes.new("StudioFloor")
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=40)
    bm.to_mesh(floor_mesh)
    bm.free()
    f_obj = bpy.data.objects.new("StudioFloor", floor_mesh)
    f_obj.location = (0, 0, 0.0)
    mat_floor = bpy.data.materials.new("M_HangarFloor")
    mat_floor.use_nodes = True
    bsdf = mat_floor.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = (0.05, 0.06, 0.07, 1.0)
        bsdf.inputs['Roughness'].default_value = 0.40
        bsdf.inputs['Metallic'].default_value = 0.30
    f_obj.data.materials.append(mat_floor)
    scene.collection.objects.link(f_obj)

    target = bpy.data.objects.new("LightTarget", None)
    target.location = (0, 0, 0.80)
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

    add_light("LightFront", (1.0, -2.8, 1.8), 130, (1.0, 0.96, 0.90), size=2.6)
    add_light("LightBack", (-1.0, 2.8, 1.8), 140, (0.95, 0.98, 1.0), size=2.6)
    add_light("LightWarmLeft", (-2.4, -0.6, 2.0), 95, (1.0, 0.82, 0.35), size=2.2)
    add_light("LightFillRight", (2.4, 0.4, 1.6), 85, (0.85, 0.92, 1.0), size=2.2)

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

# -------------------------------------------------------------------------
# COMPOSICIÓN DEL MODEL SHEET Y COMPARATIVA VISUAL
# -------------------------------------------------------------------------
def composite_sheet(v1_path, v2_path, v3_path, v4_path, out_final, title_text):
    im1 = Image.open(v1_path)
    im2 = Image.open(v2_path)
    im3 = Image.open(v3_path)
    im4 = Image.open(v4_path)

    quad = Image.new("RGBA", (1920, 1080), (14, 17, 22, 255))
    quad.paste(im1, (0, 0))
    quad.paste(im2, (960, 0))
    quad.paste(im3, (0, 540))
    quad.paste(im4, (960, 540))

    draw = ImageDraw.Draw(quad)
    line_col = (45, 60, 85, 220)
    draw.line([(960, 0), (960, 1080)], fill=line_col, width=2)
    draw.line([(0, 540), (1920, 540)], fill=line_col, width=2)

    labels = [
        ("VISTA 1: FRONTAL (CABEZA ARPILLERA, OJOS EN X, SUDADERA VERDE Y DIANAS)", (25, 20)),
        ("VISTA 2: TRASERA (MOCHILA 'MAS CORP.', ESTERA ENROLLADA Y BISAGRAS)", (985, 20)),
        ("VISTA 3: PERSPECTIVA ACCION 3/4 (MINI RESPIRADOR, CUERDA Y GAUNTLET)", (25, 560)),
        ("VISTA 4: PERFIL LATERAL DERECHO (ESTERA SUPERIOR Y DIANAS DE CODO/RODILLA)", (985, 560))
    ]
    for lbl, pos in labels:
        draw.rectangle([pos[0]-5, pos[1]-3, pos[0]+650, pos[1]+24], fill=(12, 16, 24, 230), outline=(50, 70, 95, 255), width=1)
        draw.text(pos, lbl, fill=(240, 245, 255, 255))

    draw.rectangle([440, 515, 1480, 565], fill=(18, 22, 32, 245), outline=(255, 185, 0, 255), width=2)
    draw.text((460, 528), title_text, fill=(255, 215, 0, 255))

    quad.save(out_final)
    print(f"  [OK] Model Sheet Compositado: {out_final}")

def composite_comparison(ref_path, render_front_path, render_side_path, out_comp):
    if not os.path.exists(ref_path):
        print("  [WARN] No se encontro la imagen de referencia para comparativa.")
        return

    ref_img = Image.open(ref_path)
    front_img = Image.open(render_front_path)
    side_img = Image.open(render_side_path)

    comp_img = Image.new("RGBA", (1920, 1080), (14, 17, 22, 255))

    ref_aspect = ref_img.width / ref_img.height
    ref_target_h = 460
    ref_target_w = int(ref_target_h * ref_aspect)
    ref_resized = ref_img.resize((min(ref_target_w, 1880), ref_target_h), Image.Resampling.LANCZOS)
    ref_x = (1920 - ref_resized.width) // 2
    comp_img.paste(ref_resized, (ref_x, 60))

    front_crop = front_img.resize((920, 480), Image.Resampling.LANCZOS)
    side_crop = side_img.resize((920, 480), Image.Resampling.LANCZOS)
    comp_img.paste(front_crop, (30, 560))
    comp_img.paste(side_crop, (970, 560))

    draw = ImageDraw.Draw(comp_img)
    draw.rectangle([20, 12, 1900, 52], fill=(24, 30, 42, 240), outline=(255, 185, 0, 255), width=2)
    draw.text((40, 22), "REFERENCIA ORIGINAL DEL USUARIO: MODEL SHEET CONCEPTUAL (media_1791137482814.png)", fill=(255, 215, 0, 255))

    draw.rectangle([30, 530, 950, 556], fill=(18, 22, 32, 240), outline=(0, 230, 150, 255), width=1)
    draw.text((45, 536), "RENDER 3D BLENDER: VISTA FRONTAL FIDELIDAD 1:1", fill=(0, 240, 160, 255))

    draw.rectangle([970, 530, 1890, 556], fill=(18, 22, 32, 240), outline=(0, 230, 150, 255), width=1)
    draw.text((985, 536), "RENDER 3D BLENDER: VISTA PERFIL (MOCHILA, ESTERA Y DIANAS)", fill=(0, 240, 160, 255))

    comp_img.save(out_comp)
    print(f"  [OK] Comparativa Visual Guardada: {out_comp}")

# -------------------------------------------------------------------------
# EJECUCIÓN PRINCIPAL
# -------------------------------------------------------------------------
def main():
    print("============================================================")
    print(">>> GENERADOR OFICIAL 1:1: MUÑECO DE PRUEBAS (SK_TestDummy_Ragdoll)")
    print("============================================================")
    clear_scene()
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.image_settings.file_format = 'PNG'

    mats = create_testdummy_materials()
    setup_lighting(scene)

    # 1. Armature & Malla con pesos deterministas
    arm_obj = create_testdummy_armature()
    char_obj = build_testdummy_mesh(mats, arm_obj)

    # 2. Render de las 4 vistas
    v1 = os.path.join(RENDERS_DIR, "SK_TestDummy_Fiel_v1_front.png")
    v2 = os.path.join(RENDERS_DIR, "SK_TestDummy_Fiel_v2_back.png")
    v3 = os.path.join(RENDERS_DIR, "SK_TestDummy_Fiel_v3_action.png")
    v4 = os.path.join(RENDERS_DIR, "SK_TestDummy_Fiel_v4_side.png")

    cam_dist = 3.1
    cam_lens = 34.0
    target_center = (0.0, 0.0, 0.78)

    print("  [1/4] Renderizando Vista Frontal...")
    render_camera_shot((0.0, -cam_dist, 0.80), target_center, cam_lens, v1)

    print("  [2/4] Renderizando Vista Trasera...")
    render_camera_shot((0.0, cam_dist, 0.80), target_center, cam_lens, v2)

    print("  [3/4] Renderizando Vista de Acción 3/4...")
    render_camera_shot((2.2, -2.2, 0.95), target_center, cam_lens, v3)

    print("  [4/4] Renderizando Vista de Perfil Lateral...")
    render_camera_shot((cam_dist, 0.0, 0.80), target_center, cam_lens, v4)

    # 3. Composición 4-Quadrant
    out_quad = os.path.join(RENDERS_DIR, "SK_TestDummy_Fiel_4views.png")
    composite_sheet(v1, v2, v3, v4, out_quad, "ASTRA HAZARD: MUÑECO DE PRUEBAS 1:1 (SK_TESTDUMMY_RAGDOLL)")

    # Copiar a Brain Artifacts
    brain_quad = os.path.join(BRAIN_DIR, "SK_TestDummy_Fiel_4views.png")
    shutil.copy2(out_quad, brain_quad)
    print(f"  [OK] Copiado a Brain: {brain_quad}")

    # 4. Comparativa Visual con la imagen subida por el usuario
    ref_user_img = os.path.join(BRAIN_DIR, ".user_uploaded", "media_1791137482814.png")
    out_comp = os.path.join(RENDERS_DIR, "comparativa_testdummy_fiel.png")
    composite_comparison(ref_user_img, v1, v4, out_comp)
    brain_comp = os.path.join(BRAIN_DIR, "comparativa_testdummy_fiel.png")
    if os.path.exists(out_comp):
        shutil.copy2(out_comp, brain_comp)
        print(f"  [OK] Comparativa copiada a Brain: {brain_comp}")

    # 5. Exportar FBX Limpio para Unreal Engine 5
    fbx_out = os.path.join(FBX_DIR, "SK_TestDummy_Ragdoll.fbx")
    bpy.ops.object.select_all(action='DESELECT')
    arm_obj.select_set(True)
    char_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj

    bpy.ops.export_scene.fbx(
        filepath=fbx_out,
        check_existing=False,
        use_selection=True,
        add_leaf_bones=False,
        axis_forward='-Y',
        axis_up='Z',
        apply_scale_options='FBX_SCALE_ALL'
    )
    print(f"  [OK] FBX para UE5: {fbx_out}")

    blend_out = os.path.join(ART_DIR, "Blender", "SK_TestDummy_Ragdoll.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_out)
    print(f"  [OK] Blend Maestro: {blend_out}")

if __name__ == "__main__":
    main()

import os
import sys
import math
import shutil

print("=" * 80)
print("  AOE — GENERACIÓN DE PERSONAJE ESTILO ANIME EN BLENDER (V2)")
print("=" * 80)

try:
    import bpy
    import bmesh
    from mathutils import Vector, Euler, Matrix
except ImportError:
    print("ERROR: Este script debe ser ejecutado dentro de Blender (bpy).")
    sys.exit(1)

# 1. PREPARACIÓN DE ESCENA AISLADA (REGLA 52)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0

# Configuración de World / Iluminación ambiental
world = bpy.data.worlds.new("Anime_World")
world.use_nodes = True
bg_node = world.node_tree.nodes.get('Background')
if bg_node:
    bg_node.inputs['Color'].default_value = (0.10, 0.12, 0.16, 1.0)
    bg_node.inputs['Strength'].default_value = 0.5
scene.world = world

col = bpy.data.collections.new("AOE_Anime_Character")
scene.collection.children.link(col)

def bmesh_create_cylinder(bm, radius=0.05, depth=0.1, segments=16, cap_ends=True):
    return bmesh.ops.create_cone(
        bm,
        cap_ends=cap_ends,
        segments=segments,
        radius1=radius,
        radius2=radius,
        depth=depth
    )

# 2. CREACIÓN DE SHADERS ANIME / CEL-SHADED CON TONOS VIBRANTES
def create_anime_toon_mat(name, base_color, rough=0.35, metal=0.0, emit_color=(0,0,0,1), emit_strength=0.0):
    mat = bpy.data.materials.new(name=name)
    nodes = mat.node_tree.nodes
    nodes.clear()
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (400, 0)

    principled = nodes.new(type='ShaderNodeBsdfPrincipled')
    principled.location = (0, 0)
    principled.inputs['Base Color'].default_value = base_color
    principled.inputs['Roughness'].default_value = rough
    principled.inputs['Metallic'].default_value = metal
    if emit_strength > 0.0:
        principled.inputs['Emission Color'].default_value = emit_color
        principled.inputs['Emission Strength'].default_value = emit_strength

    mat.node_tree.links.new(principled.outputs['BSDF'], output.inputs['Surface'])
    return mat

# Paleta anime rica y luminosa
m_skin = create_anime_toon_mat("M_Anime_Skin", (0.98, 0.88, 0.82, 1.0), rough=0.45)
m_hair = create_anime_toon_mat("M_Anime_Hair", (0.28, 0.18, 0.48, 1.0), rough=0.30)
m_hair_hl = create_anime_toon_mat("M_Anime_Hair_HL", (0.75, 0.42, 0.95, 1.0), rough=0.20)
m_eyes = create_anime_toon_mat("M_Anime_Eye_Iris", (0.05, 0.80, 1.0, 1.0), rough=0.10)
m_eye_glint = create_anime_toon_mat("M_Anime_Eye_Glint", (1.0, 1.0, 1.0, 1.0), rough=0.05, emit_color=(1,1,1,1), emit_strength=3.0)
m_eyeliner = create_anime_toon_mat("M_Anime_Eyeliner", (0.06, 0.04, 0.08, 1.0), rough=0.40)
m_suit = create_anime_toon_mat("M_Anime_Suit", (0.11, 0.13, 0.18, 1.0), rough=0.40)
m_suit_accent = create_anime_toon_mat("M_Anime_Suit_Accent", (0.20, 0.22, 0.30, 1.0), rough=0.35)
m_armor = create_anime_toon_mat("M_Anime_Armor", (0.95, 0.96, 0.98, 1.0), rough=0.20, metal=0.08)
m_gold = create_anime_toon_mat("M_Anime_Gold_Accent", (0.95, 0.80, 0.25, 1.0), rough=0.25, metal=0.85)
m_glow = create_anime_toon_mat("M_Anime_Cyber_Glow", (0.0, 0.92, 1.0, 1.0), rough=0.1, emit_color=(0.0, 0.92, 1.0, 1.0), emit_strength=5.0)

# Helper para añadir malla con material y sombreado suave (smooth shading)
def add_mesh_obj(name, bm, material, loc=(0,0,0), rot=(0,0,0), scale=(1,1,1), smooth=True):
    mesh = bpy.data.meshes.new(name + "_Mesh")
    bm.to_mesh(mesh)
    bm.free()
    if smooth:
        mesh.shade_smooth()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = loc
    obj.rotation_euler = [math.radians(a) for a in rot]
    obj.scale = scale
    if material:
        obj.data.materials.append(material)
    col.objects.link(obj)
    return obj

# 3. CABEZA ANIME ESTILIZADA SUAVE
bm_head = bmesh.new()
bmesh.ops.create_icosphere(bm_head, subdivisions=4, radius=0.10)
for v in bm_head.verts:
    # Mandíbula en V suave
    if v.co.z < 0:
        factor = 1.0 + (v.co.z / 0.10) * 0.58
        v.co.x *= max(factor, 0.32)
        if v.co.y < 0:
            v.co.y *= max(factor, 0.48)
            v.co.y -= 0.018 * (1.0 - factor)
    # Frente amplia y curva
    if v.co.z > 0.02 and v.co.y < 0:
        v.co.y *= 0.92
    v.co.z *= 1.15
bmesh.ops.recalc_face_normals(bm_head, faces=bm_head.faces)
obj_head = add_mesh_obj("CH_Kira_Head", bm_head, m_skin, loc=(0, 0, 1.54), smooth=True)

# Nariz Anime delicada
bm_nose = bmesh.new()
bmesh.ops.create_cone(bm_nose, cap_ends=True, segments=4, radius1=0.005, radius2=0.001, depth=0.016)
for v in bm_nose.verts:
    v.co.y -= 0.008
obj_nose = add_mesh_obj("CH_Kira_Nose", bm_nose, m_skin, loc=(0, -0.096, 1.515), rot=(90, 0, 0), smooth=True)

# Labios sutiles
bm_mouth = bmesh.new()
bmesh.ops.create_cube(bm_mouth, size=1.0)
for v in bm_mouth.verts:
    v.co.x *= 0.018
    v.co.y *= 0.003
    v.co.z *= 0.002
obj_mouth = add_mesh_obj("CH_Kira_Mouth", bm_mouth, m_eyeliner, loc=(0, -0.088, 1.485), smooth=True)

# Orejas Anime
for side, sign in [("L", 1), ("R", -1)]:
    bm_ear = bmesh.new()
    bmesh.ops.create_cone(bm_ear, cap_ends=True, segments=8, radius1=0.022, radius2=0.005, depth=0.045)
    obj_ear = add_mesh_obj(f"CH_Kira_Ear_{side}", bm_ear, m_skin, loc=(sign * 0.092, -0.01, 1.54), rot=(15, sign * 25, sign * -10), smooth=True)

# 4. OJOS ANIME INTEGRADOS (FLAT ORBITAL CORNEAS & IRIS)
for side, sign in [("L", 1), ("R", -1)]:
    # Esclera Blanca plana empotrada
    bm_white = bmesh.new()
    bmesh.ops.create_circle(bm_white, cap_ends=True, segments=20, radius=0.025)
    for v in bm_white.verts:
        v.co.y *= 1.25
    obj_white = add_mesh_obj(f"CH_Kira_EyeWhite_{side}", bm_white, m_armor, loc=(sign * 0.038, -0.082, 1.542), rot=(90, sign * 6, 0), smooth=True)

    # Iris Anime vibrante con base oscura
    bm_iris = bmesh.new()
    bmesh.ops.create_circle(bm_iris, cap_ends=True, segments=20, radius=0.016)
    for v in bm_iris.verts:
        v.co.y *= 1.30
    obj_iris = add_mesh_obj(f"CH_Kira_Iris_{side}", bm_iris, m_eyes, loc=(sign * 0.038, -0.084, 1.540), rot=(90, sign * 6, 0), smooth=True)

    # Pupila Negra Central Anime
    bm_pupil = bmesh.new()
    bmesh.ops.create_circle(bm_pupil, cap_ends=True, segments=16, radius=0.008)
    for v in bm_pupil.verts:
        v.co.y *= 1.30
    obj_pupil = add_mesh_obj(f"CH_Kira_Pupil_{side}", bm_pupil, m_eyeliner, loc=(sign * 0.038, -0.0845, 1.540), rot=(90, sign * 6, 0), smooth=True)

    # Glints Especulares Blancos
    bm_glint1 = bmesh.new()
    bmesh.ops.create_circle(bm_glint1, cap_ends=True, segments=12, radius=0.004)
    obj_glint1 = add_mesh_obj(f"CH_Kira_Glint1_{side}", bm_glint1, m_eye_glint, loc=(sign * 0.034 + 0.005, -0.085, 1.548), rot=(90, sign * 6, 0), smooth=True)

    bm_glint2 = bmesh.new()
    bmesh.ops.create_circle(bm_glint2, cap_ends=True, segments=8, radius=0.002)
    obj_glint2 = add_mesh_obj(f"CH_Kira_Glint2_{side}", bm_glint2, m_eye_glint, loc=(sign * 0.034 - 0.003, -0.085, 1.533), rot=(90, sign * 6, 0), smooth=True)

    # Pestaña Superior Arqueada
    bm_lash = bmesh.new()
    bmesh_create_cylinder(bm_lash, radius=0.003, depth=0.042, segments=10)
    for v in bm_lash.verts:
        v.co.z = -0.5 * (v.co.y**2) * 12.0
    obj_lash = add_mesh_obj(f"CH_Kira_Eyelash_{side}", bm_lash, m_eyeliner, loc=(sign * 0.038, -0.086, 1.560), rot=(0, 90, sign * 12), smooth=True)

    # Ceja estilizada anime
    bm_brow = bmesh.new()
    bmesh_create_cylinder(bm_brow, radius=0.002, depth=0.036, segments=8)
    obj_brow = add_mesh_obj(f"CH_Kira_Eyebrow_{side}", bm_brow, m_hair, loc=(sign * 0.040, -0.088, 1.578), rot=(0, 90, sign * 15), smooth=True)

# 5. CABELLO ANIME EN MECHONES SUAVES POLIGONALES
bm_hair_base = bmesh.new()
bmesh.ops.create_icosphere(bm_hair_base, subdivisions=3, radius=0.108)
for v in bm_hair_base.verts:
    v.co.z *= 1.20
    if v.co.y > -0.02:
        v.co.y *= 1.15
        v.co.z += 0.015
    if v.co.y < -0.03 and v.co.z < 0.04:
        v.co.y += 0.05
bmesh.ops.recalc_face_normals(bm_hair_base, faces=bm_hair_base.faces)
obj_hair_base = add_mesh_obj("CH_Kira_Hair_Base", bm_hair_base, m_hair, loc=(0, 0.012, 1.555), smooth=True)

def create_hair_strand(name, length=0.12, width=0.025, thickness=0.015, curve=0.03, loc=(0,0,0), rot=(0,0,0), mat=m_hair):
    bm_strand = bmesh.new()
    bmesh.ops.create_cone(bm_strand, cap_ends=True, segments=6, radius1=width, radius2=0.002, depth=length)
    for v in bm_strand.verts:
        t = max(0.001, min(1.0, (v.co.z + length/2.0) / length))
        v.co.y += (1.0 - t)**2 * curve
        v.co.x *= (t**0.7) * 1.2
    bmesh.ops.recalc_face_normals(bm_strand, faces=bm_strand.faces)
    return add_mesh_obj(name, bm_strand, mat, loc=loc, rot=rot, smooth=True)

# Flequillo Frontal y Mechones Laterales
bang_params = [
    ("Bang_Center", 0.09, 0.024, 0.02, (0.00, -0.095, 1.58), (-35, 0, 0)),
    ("Bang_Front_L", 0.11, 0.026, 0.025, (0.028, -0.092, 1.57), (-30, 8, 12)),
    ("Bang_Front_R", 0.10, 0.026, 0.025, (-0.026, -0.092, 1.57), (-32, -6, -10)),
    ("SideLock_L1", 0.18, 0.028, 0.035, (0.078, -0.055, 1.52), (-15, 12, 10)),
    ("SideLock_R1", 0.18, 0.028, 0.035, (-0.078, -0.055, 1.52), (-15, -12, -10)),
    ("SideLock_L2", 0.15, 0.022, 0.030, (0.092, -0.035, 1.50), (-10, 18, 15)),
    ("SideLock_R2", 0.15, 0.022, 0.030, (-0.092, -0.035, 1.50), (-10, -18, -15)),
    ("Bang_HL_01", 0.08, 0.016, 0.02, (0.015, -0.098, 1.59), (-40, 4, 5)),
]
for name, length, width, curve, loc, rot in bang_params:
    mat = m_hair_hl if "HL" in name else m_hair
    create_hair_strand(f"CH_Kira_{name}", length=length, width=width, curve=curve, loc=loc, rot=rot, mat=mat)

# Coleta Alta Anime
bm_tie = bmesh.new()
bmesh_create_cylinder(bm_tie, radius=0.032, depth=0.025, segments=16)
obj_tie = add_mesh_obj("CH_Kira_HairTie", bm_tie, m_glow, loc=(0, 0.105, 1.62), rot=(60, 0, 0), smooth=True)

ponytail_strands = [
    ("Tail_Core", 0.32, 0.055, 0.08, (0.0, 0.17, 1.54), (55, 0, 0)),
    ("Tail_Top", 0.28, 0.045, 0.07, (0.0, 0.16, 1.61), (40, 0, 0)),
    ("Tail_L", 0.30, 0.040, 0.09, (0.04, 0.16, 1.53), (50, 12, 10)),
    ("Tail_R", 0.30, 0.040, 0.09, (-0.04, 0.16, 1.53), (50, -12, -10)),
    ("Tail_Tip_HL", 0.24, 0.032, 0.06, (0.0, 0.21, 1.48), (62, 0, 0)),
]
for name, length, width, curve, loc, rot in ponytail_strands:
    mat = m_hair_hl if "HL" in name else m_hair
    create_hair_strand(f"CH_Kira_{name}", length=length, width=width, curve=curve, loc=loc, rot=rot, mat=mat)

# Horquilla Cibernética
bm_pin = bmesh.new()
bmesh.ops.create_cube(bm_pin, size=1.0)
for v in bm_pin.verts:
    v.co.x *= 0.045
    v.co.y *= 0.008
    v.co.z *= 0.012
obj_pin = add_mesh_obj("CH_Kira_CyberPin", bm_pin, m_glow, loc=(0.085, -0.04, 1.61), rot=(15, 20, -35), smooth=True)

# 6. CUELLO Y TORSO TÁCTICO
bm_neck = bmesh.new()
bmesh_create_cylinder(bm_neck, radius=0.036, depth=0.10, segments=16)
for v in bm_neck.verts:
    if v.co.z < -0.02:
        v.co.x *= 1.15
        v.co.y *= 1.15
obj_neck = add_mesh_obj("CH_Kira_Neck", bm_neck, m_skin, loc=(0, -0.01, 1.44), smooth=True)

bm_choker = bmesh.new()
bmesh_create_cylinder(bm_choker, radius=0.042, depth=0.022, segments=20)
obj_choker = add_mesh_obj("CH_Kira_Choker", bm_choker, m_suit, loc=(0, -0.01, 1.415), smooth=True)

# Torso y Armadura
bm_chest = bmesh.new()
bmesh.ops.create_cube(bm_chest, size=1.0)
for v in bm_chest.verts:
    v.co.x *= 0.120
    v.co.y *= 0.075
    v.co.z *= 0.100
    if v.co.z < 0:
        v.co.x *= 0.78
        v.co.y *= 0.85
bmesh.ops.recalc_face_normals(bm_chest, faces=bm_chest.faces)
obj_chest = add_mesh_obj("CH_Kira_Chest", bm_chest, m_suit, loc=(0, -0.015, 1.31), smooth=True)

for side, sign in [("L", 1), ("R", -1)]:
    bm_plate = bmesh.new()
    bmesh.ops.create_cone(bm_plate, cap_ends=True, segments=6, radius1=0.055, radius2=0.025, depth=0.08)
    for v in bm_plate.verts:
        v.co.y *= 0.40
    obj_plate = add_mesh_obj(f"CH_Kira_ChestPlate_{side}", bm_plate, m_armor, loc=(sign * 0.052, -0.075, 1.32), rot=(15, sign * -12, 0), smooth=True)

bm_core = bmesh.new()
bmesh_create_cylinder(bm_core, radius=0.016, depth=0.015, segments=12)
obj_core = add_mesh_obj("CH_Kira_ChestCore", bm_core, m_glow, loc=(0, -0.082, 1.34), rot=(90, 0, 0), smooth=True)

bm_waist = bmesh.new()
bmesh_create_cylinder(bm_waist, radius=0.072, depth=0.14, segments=16)
for v in bm_waist.verts:
    v.co.y *= 0.72
    t = abs(v.co.z / 0.07)
    v.co.x *= (0.80 + 0.20 * t)
obj_waist = add_mesh_obj("CH_Kira_Waist", bm_waist, m_suit, loc=(0, -0.012, 1.18), smooth=True)

bm_belt = bmesh.new()
bmesh_create_cylinder(bm_belt, radius=0.082, depth=0.030, segments=20)
for v in bm_belt.verts:
    v.co.y *= 0.75
obj_belt = add_mesh_obj("CH_Kira_Belt", bm_belt, m_suit_accent, loc=(0, -0.012, 1.11), smooth=True)

bm_buckle = bmesh.new()
bmesh.ops.create_cube(bm_buckle, size=1.0)
for v in bm_buckle.verts:
    v.co.x *= 0.025
    v.co.y *= 0.008
    v.co.z *= 0.018
obj_buckle = add_mesh_obj("CH_Kira_Buckle", bm_buckle, m_gold, loc=(0, -0.075, 1.11), smooth=True)

bm_hips = bmesh.new()
bmesh.ops.create_cube(bm_hips, size=1.0)
for v in bm_hips.verts:
    v.co.x *= 0.115
    v.co.y *= 0.085
    v.co.z *= 0.080
    if v.co.z < 0:
        v.co.x *= 0.75
bmesh.ops.recalc_face_normals(bm_hips, faces=bm_hips.faces)
obj_hips = add_mesh_obj("CH_Kira_Hips", bm_hips, m_suit, loc=(0, -0.012, 1.02), smooth=True)

# 7. HOMBROS, BRAZOS Y GUANTELETES
for side, sign in [("L", 1), ("R", -1)]:
    bm_pauldron = bmesh.new()
    bmesh.ops.create_icosphere(bm_pauldron, subdivisions=2, radius=0.045)
    for v in bm_pauldron.verts:
        v.co.x *= 1.30
        v.co.z *= 0.85
    obj_pauldron = add_mesh_obj(f"CH_Kira_Pauldron_{side}", bm_pauldron, m_armor, loc=(sign * 0.165, -0.015, 1.34), rot=(0, sign * 15, 0), smooth=True)

    bm_arm = bmesh.new()
    bmesh_create_cylinder(bm_arm, radius=0.026, depth=0.20, segments=12)
    obj_arm = add_mesh_obj(f"CH_Kira_UpperArm_{side}", bm_arm, m_suit, loc=(sign * 0.165, -0.015, 1.22), rot=(0, sign * 8, 0), smooth=True)

    bm_elbow = bmesh.new()
    bmesh.ops.create_uvsphere(bm_elbow, u_segments=12, v_segments=12, radius=0.024)
    obj_elbow = add_mesh_obj(f"CH_Kira_Elbow_{side}", bm_elbow, m_gold, loc=(sign * 0.185, -0.015, 1.11), smooth=True)

    bm_forearm = bmesh.new()
    bmesh_create_cylinder(bm_forearm, radius=0.030, depth=0.18, segments=12)
    for v in bm_forearm.verts:
        if v.co.z > 0:
            v.co.x *= 1.25
    obj_forearm = add_mesh_obj(f"CH_Kira_Forearm_{side}", bm_forearm, m_armor, loc=(sign * 0.205, -0.015, 1.00), rot=(0, sign * 10, 0), smooth=True)

    bm_gline = bmesh.new()
    bmesh.ops.create_cube(bm_gline, size=1.0)
    for v in bm_gline.verts:
        v.co.x *= 0.005
        v.co.y *= 0.025
        v.co.z *= 0.080
    obj_gline = add_mesh_obj(f"CH_Kira_GauntletGlow_{side}", bm_gline, m_glow, loc=(sign * 0.240, -0.015, 1.00), rot=(0, sign * 10, 0), smooth=True)

    bm_hand = bmesh.new()
    bmesh.ops.create_cube(bm_hand, size=1.0)
    for v in bm_hand.verts:
        v.co.x *= 0.018
        v.co.y *= 0.032
        v.co.z *= 0.040
    obj_hand = add_mesh_obj(f"CH_Kira_Hand_{side}", bm_hand, m_skin, loc=(sign * 0.225, -0.015, 0.88), rot=(0, sign * 10, 0), smooth=True)

# 8. PIERNAS LARGAS ANIME Y BOTAS
for side, sign in [("L", 1), ("R", -1)]:
    bm_thigh = bmesh.new()
    bmesh_create_cylinder(bm_thigh, radius=0.052, depth=0.38, segments=16)
    for v in bm_thigh.verts:
        t = (v.co.z + 0.19) / 0.38
        v.co.x *= (0.75 + 0.25 * t)
        v.co.y *= (0.80 + 0.20 * t)
    obj_thigh = add_mesh_obj(f"CH_Kira_Thigh_{side}", bm_thigh, m_suit, loc=(sign * 0.065, -0.010, 0.78), rot=(0, sign * -2, 0), smooth=True)

    bm_knee = bmesh.new()
    bmesh.ops.create_cube(bm_knee, size=1.0)
    for v in bm_knee.verts:
        v.co.x *= 0.035
        v.co.y *= 0.020
        v.co.z *= 0.035
        if v.co.y < 0:
            v.co.z *= 1.2
    obj_knee = add_mesh_obj(f"CH_Kira_Knee_{side}", bm_knee, m_armor, loc=(sign * 0.065, -0.050, 0.58), smooth=True)

    bm_calf = bmesh.new()
    bmesh_create_cylinder(bm_calf, radius=0.042, depth=0.34, segments=16)
    for v in bm_calf.verts:
        if v.co.z > 0.05:
            v.co.y *= 1.15
        else:
            v.co.x *= 0.85
    obj_calf = add_mesh_obj(f"CH_Kira_Calf_{side}", bm_calf, m_suit_accent, loc=(sign * 0.065, -0.012, 0.40), smooth=True)

    bm_boot = bmesh.new()
    bmesh.ops.create_cube(bm_boot, size=1.0)
    for v in bm_boot.verts:
        v.co.x *= 0.045
        v.co.y *= 0.100
        v.co.z *= 0.110
        if v.co.z < 0:
            v.co.y -= 0.015
    obj_boot = add_mesh_obj(f"CH_Kira_Boot_{side}", bm_boot, m_armor, loc=(sign * 0.065, -0.025, 0.11), smooth=True)

    bm_bootglow = bmesh.new()
    bmesh_create_cylinder(bm_bootglow, radius=0.048, depth=0.015, segments=16)
    for v in bm_bootglow.verts:
        v.co.y *= 1.35
    obj_bglow = add_mesh_obj(f"CH_Kira_BootGlow_{side}", bm_bootglow, m_glow, loc=(sign * 0.065, -0.025, 0.20), smooth=True)

# 9. SUELO Y CICLORAMA ESTUDIO
bm_floor = bmesh.new()
bmesh_create_cylinder(bm_floor, radius=1.1, depth=0.03, segments=32)
obj_floor = add_mesh_obj("Studio_Pedestal", bm_floor, m_suit, loc=(0, 0, -0.015), smooth=True)

bm_ped_ring = bmesh.new()
bmesh_create_cylinder(bm_ped_ring, radius=1.12, depth=0.015, segments=32)
obj_ped_ring = add_mesh_obj("Studio_Pedestal_Ring", bm_ped_ring, m_glow, loc=(0, 0, -0.005), smooth=True)

# Ciclorama amplio
m_backdrop = create_anime_toon_mat("M_Studio_Backdrop", (0.08, 0.09, 0.13, 1.0), rough=0.90)
bm_bg = bmesh.new()
bmesh.ops.create_grid(bm_bg, x_segments=20, y_segments=20, size=8.0)
for v in bm_bg.verts:
    if v.co.y > 0:
        v.co.z += (v.co.y / 3.0)**2 * 4.0
    v.co.y += 2.0
bmesh.ops.recalc_face_normals(bm_bg, faces=bm_bg.faces)
obj_bg = add_mesh_obj("Studio_Backdrop", bm_bg, m_backdrop, loc=(0, 2.0, 0.0), smooth=True)

# 10. ILUMINACIÓN ESTUDIO DE ALTA CALIDAD PARA ANIME
# Front Beauty Softbox (Ilumina cara y torso suavemente sin quemar los ojos)
light_beauty_data = bpy.data.lights.new(name="Beauty_Light", type='AREA')
light_beauty_data.energy = 24.0
light_beauty_data.size = 1.8
light_beauty_data.color = (1.0, 0.97, 0.94)
light_beauty = bpy.data.objects.new(name="Beauty_Light", object_data=light_beauty_data)
light_beauty.location = (0.15, -2.0, 1.55)
light_beauty.rotation_euler = (math.radians(75), 0, math.radians(4))
col.objects.link(light_beauty)

# Key Light 3/4
light_key_data = bpy.data.lights.new(name="Key_Light", type='AREA')
light_key_data.energy = 36.0
light_key_data.size = 2.0
light_key_data.color = (0.95, 0.95, 1.0)
light_key = bpy.data.objects.new(name="Key_Light", object_data=light_key_data)
light_key.location = (1.8, -2.6, 2.2)
light_key.rotation_euler = (math.radians(55), math.radians(10), math.radians(35))
col.objects.link(light_key)

# Fill Light (Suave lateral)
light_fill_data = bpy.data.lights.new(name="Fill_Light", type='AREA')
light_fill_data.energy = 20.0
light_fill_data.size = 2.5
light_fill_data.color = (0.75, 0.85, 1.0)
light_fill = bpy.data.objects.new(name="Fill_Light", object_data=light_fill_data)
light_fill.location = (-2.0, -2.0, 1.6)
light_fill.rotation_euler = (math.radians(45), math.radians(-15), math.radians(-45))
col.objects.link(light_fill)

# Rim Light (Contorno Anime Acentuado)
light_rim_data = bpy.data.lights.new(name="Rim_Light", type='SPOT')
light_rim_data.energy = 75.0
light_rim_data.spot_size = math.radians(70)
light_rim_data.color = (0.9, 0.85, 1.0)
light_rim = bpy.data.objects.new(name="Rim_Light", object_data=light_rim_data)
light_rim.location = (-0.8, 2.0, 2.6)
light_rim.rotation_euler = (math.radians(-130), math.radians(-15), math.radians(-150))
col.objects.link(light_rim)

# 11. CÁMARAS Y CONFIGURACIÓN DE RENDER
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.resolution_percentage = 100
scene.render.film_transparent = False
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'Medium High Contrast'

output_dir = r"E:\Darx_Proyect\Saved\Anime_Character_Workspace"
os.makedirs(output_dir, exist_ok=True)

# Cámara 1: Full Body Heroica 3/4
cam_body_data = bpy.data.cameras.new(name="Camera_FullBody")
cam_body_data.lens = 42.0
cam_body = bpy.data.objects.new(name="Camera_FullBody", object_data=cam_body_data)
cam_body.location = (0.15, -4.6, 0.95)
cam_body.rotation_euler = (math.radians(89), 0, math.radians(3))
col.objects.link(cam_body)

scene.camera = cam_body
output_body = os.path.join(output_dir, "preview_anime_character_kira_body.png")
scene.render.filepath = output_body
print(f"\n[1/2] RENDERIZANDO CUERPO ENTERO EN: {output_body}...")
bpy.ops.render.render(write_still=True)
print(f"RENDER BODY COMPLETADO: {os.path.exists(output_body)}")

# Cámara 2: Primer Plano Retrato Facial Anime
cam_face_data = bpy.data.cameras.new(name="Camera_Face")
cam_face_data.lens = 72.0
cam_face = bpy.data.objects.new(name="Camera_Face", object_data=cam_face_data)
cam_face.location = (0.12, -1.35, 1.54)
cam_face.rotation_euler = (math.radians(88), 0, math.radians(6))
col.objects.link(cam_face)

scene.camera = cam_face
output_face = os.path.join(output_dir, "preview_anime_character_kira_face.png")
scene.render.filepath = output_face
print(f"\n[2/2] RENDERIZANDO RETRATO FACIAL EN: {output_face}...")
bpy.ops.render.render(write_still=True)
print(f"RENDER FACE COMPLETADO: {os.path.exists(output_face)}")

# Guardar archivo .blend
blend_out = os.path.join(output_dir, "CH_Anime_Kira.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_out)
print(f"\nARCHIVO BLEND GUARDADO: {blend_out}")
print("=" * 80)

import os
import sys
import math
import shutil

print("=" * 80)
print("  AOE — FASE 3 & 4: DETALLES, MATERIALES Y PREVISUALIZACIÓN DE 4 VISTAS")
print("  ENTIDAD: CH_Anime_Kira (Kira - Cybernetic Anime Operative)")
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

# Iluminación Ambiental del Mundo
world = bpy.data.worlds.new("Anime_World_V3")
world.use_nodes = True
bg_node = world.node_tree.nodes.get('Background')
if bg_node:
    bg_node.inputs['Color'].default_value = (0.08, 0.10, 0.14, 1.0)
    bg_node.inputs['Strength'].default_value = 0.6
scene.world = world

col = bpy.data.collections.new("AOE_Anime_Character")
scene.collection.children.link(col)

# Helper cilindro BMesh
def bmesh_create_cylinder(bm, radius=0.05, depth=0.1, segments=16, cap_ends=True):
    return bmesh.ops.create_cone(
        bm,
        cap_ends=cap_ends,
        segments=segments,
        radius1=radius,
        radius2=radius,
        depth=depth
    )

# 2. SHADERS ESTILO ANIME / CEL-SHADED TOON (FASE 4)
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

# Paleta completa
m_skin = create_anime_toon_mat("M_Anime_Skin", (0.98, 0.89, 0.83, 1.0), rough=0.45)
m_blush = create_anime_toon_mat("M_Anime_Blush", (0.95, 0.65, 0.68, 1.0), rough=0.50)
m_hair = create_anime_toon_mat("M_Anime_Hair", (0.26, 0.16, 0.46, 1.0), rough=0.30)
m_hair_hl = create_anime_toon_mat("M_Anime_Hair_HL", (0.76, 0.42, 0.96, 1.0), rough=0.20)
m_angel_ring = create_anime_toon_mat("M_Anime_AngelRing", (0.92, 0.75, 1.0, 1.0), rough=0.10, emit_color=(0.85, 0.65, 1.0, 1.0), emit_strength=2.2)
m_eyes = create_anime_toon_mat("M_Anime_Eye_Iris", (0.05, 0.80, 1.0, 1.0), rough=0.10)
m_eye_glint = create_anime_toon_mat("M_Anime_Eye_Glint", (1.0, 1.0, 1.0, 1.0), rough=0.05, emit_color=(1,1,1,1), emit_strength=3.5)
m_eyeliner = create_anime_toon_mat("M_Anime_Eyeliner", (0.06, 0.04, 0.08, 1.0), rough=0.40)
m_suit = create_anime_toon_mat("M_Anime_Suit", (0.11, 0.13, 0.18, 1.0), rough=0.40)
m_suit_accent = create_anime_toon_mat("M_Anime_Suit_Accent", (0.20, 0.22, 0.30, 1.0), rough=0.35)
m_suit_joint = create_anime_toon_mat("M_Anime_Suit_Joint", (0.15, 0.17, 0.22, 1.0), rough=0.30)
m_armor = create_anime_toon_mat("M_Anime_Armor", (0.95, 0.96, 0.98, 1.0), rough=0.20, metal=0.08)
m_gold = create_anime_toon_mat("M_Anime_Gold_Accent", (0.95, 0.80, 0.25, 1.0), rough=0.25, metal=0.85)
m_glow = create_anime_toon_mat("M_Anime_Cyber_Glow", (0.0, 0.92, 1.0, 1.0), rough=0.1, emit_color=(0.0, 0.92, 1.0, 1.0), emit_strength=5.5)
m_scarf = create_anime_toon_mat("M_Anime_CyberScarf", (0.85, 0.15, 0.32, 1.0), rough=0.40)
m_blade_edge = create_anime_toon_mat("M_Anime_BladeEdge", (0.0, 0.95, 1.0, 1.0), rough=0.1, emit_color=(0.0, 0.95, 1.0, 1.0), emit_strength=6.0)
m_blade_steel = create_anime_toon_mat("M_Anime_BladeSteel", (0.25, 0.28, 0.32, 1.0), rough=0.15, metal=0.92)

# Helper para añadir malla con material y sombreado suave
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

# 3. CABEZA Y ROSTRO ANIME ESTILIZADO
bm_head = bmesh.new()
bmesh.ops.create_icosphere(bm_head, subdivisions=4, radius=0.10)
for v in bm_head.verts:
    if v.co.z < 0:
        factor = 1.0 + (v.co.z / 0.10) * 0.58
        v.co.x *= max(factor, 0.32)
        if v.co.y < 0:
            v.co.y *= max(factor, 0.48)
            v.co.y -= 0.018 * (1.0 - factor)
    if v.co.z > 0.02 and v.co.y < 0:
        v.co.y *= 0.92
    v.co.z *= 1.15
bmesh.ops.recalc_face_normals(bm_head, faces=bm_head.faces)
obj_head = add_mesh_obj("CH_Kira_Head", bm_head, m_skin, loc=(0, 0, 1.54), smooth=True)

# Nariz anime delicada
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

# Orejas anime
for side, sign in [("L", 1), ("R", -1)]:
    bm_ear = bmesh.new()
    bmesh.ops.create_cone(bm_ear, cap_ends=True, segments=8, radius1=0.022, radius2=0.005, depth=0.045)
    obj_ear = add_mesh_obj(f"CH_Kira_Ear_{side}", bm_ear, m_skin, loc=(sign * 0.092, -0.01, 1.54), rot=(15, sign * 25, sign * -10), smooth=True)

    # Rubor anime en pómulos (Anime Cheek Blush)
    bm_blush = bmesh.new()
    bmesh.ops.create_circle(bm_blush, cap_ends=True, segments=12, radius=0.012)
    for v in bm_blush.verts:
        v.co.y *= 0.50
    obj_blush = add_mesh_obj(f"CH_Kira_Blush_{side}", bm_blush, m_blush, loc=(sign * 0.052, -0.082, 1.505), rot=(90, sign * 15, 0), smooth=True)

# 4. OJOS ANIME DE 3 TONOS, PUPILA Y PESTAÑAS ARQUEADAS
for side, sign in [("L", 1), ("R", -1)]:
    # Esclera Blanca
    bm_white = bmesh.new()
    bmesh.ops.create_circle(bm_white, cap_ends=True, segments=20, radius=0.025)
    for v in bm_white.verts:
        v.co.y *= 1.25
    obj_white = add_mesh_obj(f"CH_Kira_EyeWhite_{side}", bm_white, m_armor, loc=(sign * 0.038, -0.082, 1.542), rot=(90, sign * 6, 0), smooth=True)

    # Iris Cian Anime
    bm_iris = bmesh.new()
    bmesh.ops.create_circle(bm_iris, cap_ends=True, segments=20, radius=0.016)
    for v in bm_iris.verts:
        v.co.y *= 1.30
    obj_iris = add_mesh_obj(f"CH_Kira_Iris_{side}", bm_iris, m_eyes, loc=(sign * 0.038, -0.084, 1.540), rot=(90, sign * 6, 0), smooth=True)

    # Pupila Central Oscura
    bm_pupil = bmesh.new()
    bmesh.ops.create_circle(bm_pupil, cap_ends=True, segments=16, radius=0.008)
    for v in bm_pupil.verts:
        v.co.y *= 1.30
    obj_pupil = add_mesh_obj(f"CH_Kira_Pupil_{side}", bm_pupil, m_eyeliner, loc=(sign * 0.038, -0.0845, 1.540), rot=(90, sign * 6, 0), smooth=True)

    # Doble Glint Especular
    bm_glint1 = bmesh.new()
    bmesh.ops.create_circle(bm_glint1, cap_ends=True, segments=12, radius=0.004)
    obj_glint1 = add_mesh_obj(f"CH_Kira_Glint1_{side}", bm_glint1, m_eye_glint, loc=(sign * 0.034 + 0.005, -0.085, 1.548), rot=(90, sign * 6, 0), smooth=True)

    bm_glint2 = bmesh.new()
    bmesh.ops.create_circle(bm_glint2, cap_ends=True, segments=8, radius=0.002)
    obj_glint2 = add_mesh_obj(f"CH_Kira_Glint2_{side}", bm_glint2, m_eye_glint, loc=(sign * 0.034 - 0.003, -0.085, 1.533), rot=(90, sign * 6, 0), smooth=True)

    # Pestaña Superior Alargada (Winged Lash)
    bm_lash = bmesh.new()
    bmesh_create_cylinder(bm_lash, radius=0.003, depth=0.045, segments=10)
    for v in bm_lash.verts:
        v.co.z = -0.5 * (v.co.y**2) * 12.0
    obj_lash = add_mesh_obj(f"CH_Kira_Eyelash_{side}", bm_lash, m_eyeliner, loc=(sign * 0.038, -0.086, 1.560), rot=(0, 90, sign * 12), smooth=True)

    # Ceja estilizada
    bm_brow = bmesh.new()
    bmesh_create_cylinder(bm_brow, radius=0.002, depth=0.036, segments=8)
    obj_brow = add_mesh_obj(f"CH_Kira_Eyebrow_{side}", bm_brow, m_hair, loc=(sign * 0.040, -0.088, 1.578), rot=(0, 90, sign * 15), smooth=True)

# 5. PEINADO ANIME CON CAPAS, FLEQUILLO Y ANGEL RING
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

# Resalte Circular de Cabello Anime (Angel Ring / Halo Táctico)
bm_ring = bmesh.new()
bmesh_create_cylinder(bm_ring, radius=0.108, depth=0.012, segments=24)
for v in bm_ring.verts:
    v.co.z *= 0.4
obj_ring = add_mesh_obj("CH_Kira_AngelRing", bm_ring, m_angel_ring, loc=(0, 0.008, 1.60), rot=(18, 0, 0), smooth=True)

def create_hair_strand(name, length=0.12, width=0.025, thickness=0.015, curve=0.03, loc=(0,0,0), rot=(0,0,0), mat=m_hair):
    bm_strand = bmesh.new()
    bmesh.ops.create_cone(bm_strand, cap_ends=True, segments=6, radius1=width, radius2=0.002, depth=length)
    for v in bm_strand.verts:
        t = max(0.001, min(1.0, (v.co.z + length/2.0) / length))
        v.co.y += (1.0 - t)**2 * curve
        v.co.x *= (t**0.7) * 1.2
    bmesh.ops.recalc_face_normals(bm_strand, faces=bm_strand.faces)
    return add_mesh_obj(name, bm_strand, mat, loc=loc, rot=rot, smooth=True)

# Mechones Frontales y Laterales en Capas
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

# Coleta Alta Anime Dinámica
bm_tie = bmesh.new()
bmesh_create_cylinder(bm_tie, radius=0.032, depth=0.025, segments=16)
obj_tie = add_mesh_obj("CH_Kira_HairTie", bm_tie, m_glow, loc=(0, 0.105, 1.62), rot=(60, 0, 0), smooth=True)

ponytail_strands = [
    ("Tail_Core", 0.35, 0.055, 0.09, (0.0, 0.18, 1.53), (58, 0, 0)),
    ("Tail_Top", 0.30, 0.045, 0.08, (0.0, 0.17, 1.61), (42, 0, 0)),
    ("Tail_L", 0.32, 0.040, 0.10, (0.045, 0.17, 1.52), (52, 12, 10)),
    ("Tail_R", 0.32, 0.040, 0.10, (-0.045, 0.17, 1.52), (52, -12, -10)),
    ("Tail_Tip_HL", 0.26, 0.032, 0.07, (0.0, 0.22, 1.47), (65, 0, 0)),
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

# 6. CUELLO, BUFANDA CIBERNÉTICA Y TORSO ORGÁNICO CONTINUO
bm_neck = bmesh.new()
bmesh_create_cylinder(bm_neck, radius=0.036, depth=0.10, segments=16)
for v in bm_neck.verts:
    if v.co.z < -0.02:
        v.co.x *= 1.15
        v.co.y *= 1.15
obj_neck = add_mesh_obj("CH_Kira_Neck", bm_neck, m_skin, loc=(0, -0.01, 1.44), smooth=True)

# Gargantilla Táctica
bm_choker = bmesh.new()
bmesh_create_cylinder(bm_choker, radius=0.042, depth=0.022, segments=20)
obj_choker = add_mesh_obj("CH_Kira_Choker", bm_choker, m_suit, loc=(0, -0.01, 1.415), smooth=True)

# Bufanda Cibernética Táctica (Cyber Scarf) ondeando hacia atrás
bm_scarf_neck = bmesh.new()
bmesh_create_cylinder(bm_scarf_neck, radius=0.065, depth=0.045, segments=16)
for v in bm_scarf_neck.verts:
    v.co.y *= 0.90
obj_scarf_neck = add_mesh_obj("CH_Kira_ScarfCollar", bm_scarf_neck, m_scarf, loc=(0, -0.01, 1.385), smooth=True)

# Colas de la bufanda que ondean al viento
for i, (name, length, offset_x, rot_z) in enumerate([("ScarfTail_1", 0.42, 0.06, 18), ("ScarfTail_2", 0.35, 0.03, 30)]):
    bm_tail = bmesh.new()
    bmesh.ops.create_cone(bm_tail, cap_ends=True, segments=4, radius1=0.035, radius2=0.015, depth=length)
    for v in bm_tail.verts:
        t = (v.co.z + length/2.0) / length
        v.co.y += (1.0 - t)**2 * 0.15  # ondea hacia +Y (hacia atrás)
        v.co.x *= 0.35  # cinta plana
    obj_tail = add_mesh_obj(f"CH_Kira_{name}", bm_tail, m_scarf, loc=(offset_x, 0.08, 1.35 - i*0.04), rot=(45, 0, rot_z), smooth=True)

# Torso y Coraza Táctica
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

# Placas Pectorales Cerámicas
for side, sign in [("L", 1), ("R", -1)]:
    bm_plate = bmesh.new()
    bmesh.ops.create_cone(bm_plate, cap_ends=True, segments=6, radius1=0.055, radius2=0.025, depth=0.08)
    for v in bm_plate.verts:
        v.co.y *= 0.40
    obj_plate = add_mesh_obj(f"CH_Kira_ChestPlate_{side}", bm_plate, m_armor, loc=(sign * 0.052, -0.075, 1.32), rot=(15, sign * -12, 0), smooth=True)

# Núcleo Cibernético Central
bm_core = bmesh.new()
bmesh_create_cylinder(bm_core, radius=0.016, depth=0.015, segments=12)
obj_core = add_mesh_obj("CH_Kira_ChestCore", bm_core, m_glow, loc=(0, -0.082, 1.34), rot=(90, 0, 0), smooth=True)

# Abdomen y Cintura Estilizada
bm_waist = bmesh.new()
bmesh_create_cylinder(bm_waist, radius=0.072, depth=0.14, segments=16)
for v in bm_waist.verts:
    v.co.y *= 0.72
    t = abs(v.co.z / 0.07)
    v.co.x *= (0.80 + 0.20 * t)
obj_waist = add_mesh_obj("CH_Kira_Waist", bm_waist, m_suit, loc=(0, -0.012, 1.18), smooth=True)

# Juntas de Cintura / Conector Orgánico (Elimina huecos flotantes)
bm_joint_w = bmesh.new()
bmesh_create_cylinder(bm_joint_w, radius=0.068, depth=0.035, segments=16)
for v in bm_joint_w.verts:
    v.co.y *= 0.70
obj_joint_w = add_mesh_obj("CH_Kira_WaistJoint", bm_joint_w, m_suit_joint, loc=(0, -0.012, 1.25), smooth=True)

# Cinturón Táctico y Hebilla Dorada
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

# Cartucheras tácticas laterales
for side, sign in [("L", 1), ("R", -1)]:
    bm_pouch = bmesh.new()
    bmesh.ops.create_cube(bm_pouch, size=1.0)
    for v in bm_pouch.verts:
        v.co.x *= 0.018
        v.co.y *= 0.032
        v.co.z *= 0.025
    obj_pouch = add_mesh_obj(f"CH_Kira_Pouch_{side}", bm_pouch, m_armor, loc=(sign * 0.088, -0.015, 1.10), rot=(0, sign * 5, 0), smooth=True)

# Caderas / Pelvis Táctica (Sin huecos flotantes)
bm_hips = bmesh.new()
bmesh.ops.create_cube(bm_hips, size=1.0)
for v in bm_hips.verts:
    v.co.x *= 0.115
    v.co.y *= 0.085
    v.co.z *= 0.130
    if v.co.z < 0:
        v.co.x *= 0.85
bmesh.ops.recalc_face_normals(bm_hips, faces=bm_hips.faces)
obj_hips = add_mesh_obj("CH_Kira_Hips", bm_hips, m_suit, loc=(0, -0.012, 1.05), smooth=True)

# 7. HOMBROS, BRAZOS, GUANTELETES Y MANOS ANATÓMICAS CON 5 DEDOS
for side, sign in [("L", 1), ("R", -1)]:
    # Conector Hombro (elimina hueco flotante)
    bm_sh_joint = bmesh.new()
    bmesh.ops.create_uvsphere(bm_sh_joint, u_segments=12, v_segments=12, radius=0.035)
    obj_sh_joint = add_mesh_obj(f"CH_Kira_ShoulderJoint_{side}", bm_sh_joint, m_suit_joint, loc=(sign * 0.145, -0.015, 1.34), smooth=True)

    # Hombrera Cerámica Anime
    bm_pauldron = bmesh.new()
    bmesh.ops.create_icosphere(bm_pauldron, subdivisions=2, radius=0.045)
    for v in bm_pauldron.verts:
        v.co.x *= 1.30
        v.co.z *= 0.85
    obj_pauldron = add_mesh_obj(f"CH_Kira_Pauldron_{side}", bm_pauldron, m_armor, loc=(sign * 0.165, -0.015, 1.34), rot=(0, sign * 15, 0), smooth=True)

    # Brazo Superior
    bm_arm = bmesh.new()
    bmesh_create_cylinder(bm_arm, radius=0.026, depth=0.20, segments=12)
    obj_arm = add_mesh_obj(f"CH_Kira_UpperArm_{side}", bm_arm, m_suit, loc=(sign * 0.165, -0.015, 1.22), rot=(0, sign * 8, 0), smooth=True)

    # Codo Articulado
    bm_elbow = bmesh.new()
    bmesh.ops.create_uvsphere(bm_elbow, u_segments=12, v_segments=12, radius=0.026)
    obj_elbow = add_mesh_obj(f"CH_Kira_Elbow_{side}", bm_elbow, m_gold, loc=(sign * 0.182, -0.015, 1.11), smooth=True)

    # Antebrazo con Escudo Exterior
    bm_forearm = bmesh.new()
    bmesh_create_cylinder(bm_forearm, radius=0.030, depth=0.18, segments=12)
    for v in bm_forearm.verts:
        if v.co.z > 0:
            v.co.x *= 1.25
    obj_forearm = add_mesh_obj(f"CH_Kira_Forearm_{side}", bm_forearm, m_armor, loc=(sign * 0.200, -0.015, 1.00), rot=(0, sign * 10, 0), smooth=True)

    # Línea emisiva en guantelete
    bm_gline = bmesh.new()
    bmesh.ops.create_cube(bm_gline, size=1.0)
    for v in bm_gline.verts:
        v.co.x *= 0.005
        v.co.y *= 0.025
        v.co.z *= 0.080
    obj_gline = add_mesh_obj(f"CH_Kira_GauntletGlow_{side}", bm_gline, m_glow, loc=(sign * 0.235, -0.015, 1.00), rot=(0, sign * 10, 0), smooth=True)

    # Muñeca Conectora
    bm_wrist = bmesh.new()
    bmesh_create_cylinder(bm_wrist, radius=0.022, depth=0.03, segments=12)
    obj_wrist = add_mesh_obj(f"CH_Kira_Wrist_{side}", bm_wrist, m_suit_joint, loc=(sign * 0.215, -0.015, 0.905), rot=(0, sign * 10, 0), smooth=True)

    # Palma de la Mano
    bm_hand = bmesh.new()
    bmesh.ops.create_cube(bm_hand, size=1.0)
    for v in bm_hand.verts:
        v.co.x *= 0.016
        v.co.y *= 0.026
        v.co.z *= 0.032
    obj_hand = add_mesh_obj(f"CH_Kira_Hand_{side}", bm_hand, m_skin, loc=(sign * 0.222, -0.015, 0.875), rot=(0, sign * 10, 0), smooth=True)

    # 5 Dedos Anatómicos Estilizados
    # Pulgar
    bm_thumb = bmesh.new()
    bmesh_create_cylinder(bm_thumb, radius=0.004, depth=0.024, segments=6)
    obj_thumb = add_mesh_obj(f"CH_Kira_Thumb_{side}", bm_thumb, m_skin, loc=(sign * 0.210, -0.028, 0.875), rot=(25, sign * 20, 0), smooth=True)

    # 4 Dedos extendidos
    for f_idx in range(4):
        offset_y = (f_idx - 1.5) * 0.010
        bm_finger = bmesh.new()
        bmesh_create_cylinder(bm_finger, radius=0.0035, depth=0.030, segments=6)
        obj_finger = add_mesh_obj(f"CH_Kira_Finger_{f_idx}_{side}", bm_finger, m_skin, loc=(sign * 0.226, offset_y, 0.845), rot=(5, sign * 10, 0), smooth=True)

# 8. PIERNAS LARGAS, ARTICULACIONES Y BOTAS DE COMBATE
for side, sign in [("L", 1), ("R", -1)]:
    # Conector Cadera / Muslo
    bm_hip_j = bmesh.new()
    bmesh.ops.create_uvsphere(bm_hip_j, u_segments=12, v_segments=12, radius=0.045)
    obj_hip_j = add_mesh_obj(f"CH_Kira_HipJoint_{side}", bm_hip_j, m_suit_joint, loc=(sign * 0.065, -0.010, 0.98), smooth=True)

    # Muslo Anime Estilizado
    bm_thigh = bmesh.new()
    bmesh_create_cylinder(bm_thigh, radius=0.052, depth=0.38, segments=16)
    for v in bm_thigh.verts:
        t = (v.co.z + 0.19) / 0.38
        v.co.x *= (0.75 + 0.25 * t)
        v.co.y *= (0.80 + 0.20 * t)
    obj_thigh = add_mesh_obj(f"CH_Kira_Thigh_{side}", bm_thigh, m_suit, loc=(sign * 0.065, -0.010, 0.78), rot=(0, sign * -2, 0), smooth=True)

    # Conector Rodilla
    bm_knee_j = bmesh.new()
    bmesh.ops.create_uvsphere(bm_knee_j, u_segments=12, v_segments=12, radius=0.038)
    obj_knee_j = add_mesh_obj(f"CH_Kira_KneeJoint_{side}", bm_knee_j, m_suit_joint, loc=(sign * 0.065, -0.012, 0.58), smooth=True)

    # Rodillera Cerámica
    bm_knee = bmesh.new()
    bmesh.ops.create_cube(bm_knee, size=1.0)
    for v in bm_knee.verts:
        v.co.x *= 0.035
        v.co.y *= 0.020
        v.co.z *= 0.035
        if v.co.y < 0:
            v.co.z *= 1.2
    obj_knee = add_mesh_obj(f"CH_Kira_Knee_{side}", bm_knee, m_armor, loc=(sign * 0.065, -0.048, 0.58), smooth=True)

    # Pantorrilla Estilizada
    bm_calf = bmesh.new()
    bmesh_create_cylinder(bm_calf, radius=0.042, depth=0.34, segments=16)
    for v in bm_calf.verts:
        if v.co.z > 0.05:
            v.co.y *= 1.15
        else:
            v.co.x *= 0.85
    obj_calf = add_mesh_obj(f"CH_Kira_Calf_{side}", bm_calf, m_suit_accent, loc=(sign * 0.065, -0.012, 0.40), smooth=True)

    # Conector Tobillo
    bm_ank_j = bmesh.new()
    bmesh_create_cylinder(bm_ank_j, radius=0.034, depth=0.04, segments=12)
    obj_ank_j = add_mesh_obj(f"CH_Kira_AnkleJoint_{side}", bm_ank_j, m_suit_joint, loc=(sign * 0.065, -0.015, 0.22), smooth=True)

    # Bota Táctica de Combate
    bm_boot = bmesh.new()
    bmesh.ops.create_cube(bm_boot, size=1.0)
    for v in bm_boot.verts:
        v.co.x *= 0.045
        v.co.y *= 0.105
        v.co.z *= 0.110
        if v.co.z < 0:
            v.co.y -= 0.018
    obj_boot = add_mesh_obj(f"CH_Kira_Boot_{side}", bm_boot, m_armor, loc=(sign * 0.065, -0.025, 0.11), smooth=True)

    # Banda Luminosa Cian en Bota
    bm_bootglow = bmesh.new()
    bmesh_create_cylinder(bm_bootglow, radius=0.048, depth=0.015, segments=16)
    for v in bm_bootglow.verts:
        v.co.y *= 1.35
    obj_bglow = add_mesh_obj(f"CH_Kira_BootGlow_{side}", bm_bootglow, m_glow, loc=(sign * 0.065, -0.025, 0.19), smooth=True)

# 9. KATANA CIBERNÉTICA EN LA CADERA IZQUIERDA (CYBER KATANA SHEATHED)
# Vaina de la Katana (Saya)
bm_saya = bmesh.new()
bmesh_create_cylinder(bm_saya, radius=0.016, depth=0.75, segments=8)
for v in bm_saya.verts:
    v.co.x *= 0.45  # perfil delgado
    # ligera curvatura de katana
    t = (v.co.z + 0.375) / 0.75
    v.co.y += (t**1.8) * 0.045
obj_saya = add_mesh_obj("WP_Anime_Katana_Saya", bm_saya, m_suit_accent, loc=(-0.14, 0.05, 0.85), rot=(25, -15, 15), smooth=True)

# Acople Dorado a la Cadera
bm_saya_mount = bmesh.new()
bmesh.ops.create_cube(bm_saya_mount, size=1.0)
for v in bm_saya_mount.verts:
    v.co.x *= 0.018
    v.co.y *= 0.025
    v.co.z *= 0.035
obj_smount = add_mesh_obj("WP_Anime_Katana_Mount", bm_saya_mount, m_gold, loc=(-0.12, 0.02, 1.05), rot=(25, -15, 15), smooth=True)

# Empuñadura (Tsuka) y Guardamano (Tsuba)
bm_tsuba = bmesh.new()
bmesh.ops.create_circle(bm_tsuba, cap_ends=True, segments=12, radius=0.035)
obj_tsuba = add_mesh_obj("WP_Anime_Katana_Tsuba", bm_tsuba, m_gold, loc=(-0.155, -0.015, 1.18), rot=(65, 15, -75), smooth=True)

bm_tsuka = bmesh.new()
bmesh_create_cylinder(bm_tsuka, radius=0.014, depth=0.22, segments=8)
for v in bm_tsuka.verts:
    v.co.x *= 0.50
obj_tsuka = add_mesh_obj("WP_Anime_Katana_Tsuka", bm_tsuka, m_armor, loc=(-0.175, -0.065, 1.28), rot=(25, -15, 15), smooth=True)

# Pomo Dorado (Kashira) y filo de energía
bm_kashira = bmesh.new()
bmesh.ops.create_cube(bm_kashira, size=1.0)
for v in bm_kashira.verts:
    v.co.x *= 0.012
    v.co.y *= 0.016
    v.co.z *= 0.012
obj_kashira = add_mesh_obj("WP_Anime_Katana_Kashira", bm_kashira, m_gold, loc=(-0.195, -0.115, 1.38), rot=(25, -15, 15), smooth=True)

# 10. SUELO, PEDESTAL Y CICLORAMA ESTUDIO
bm_floor = bmesh.new()
bmesh_create_cylinder(bm_floor, radius=1.2, depth=0.03, segments=32)
obj_floor = add_mesh_obj("Studio_Pedestal", bm_floor, m_suit, loc=(0, 0, -0.015), smooth=True)

bm_ped_ring = bmesh.new()
bmesh_create_cylinder(bm_ped_ring, radius=1.22, depth=0.015, segments=32)
obj_ped_ring = add_mesh_obj("Studio_Pedestal_Ring", bm_ped_ring, m_glow, loc=(0, 0, -0.005), smooth=True)

m_backdrop = create_anime_toon_mat("M_Studio_Backdrop", (0.18, 0.20, 0.25, 1.0), rough=0.92)
bm_bg = bmesh.new()
bmesh.ops.create_grid(bm_bg, x_segments=24, y_segments=24, size=10.0)
for v in bm_bg.verts:
    if v.co.y > 0:
        v.co.z += (v.co.y / 3.5)**2 * 4.5
    v.co.y += 2.5
bmesh.ops.recalc_face_normals(bm_bg, faces=bm_bg.faces)
obj_bg = add_mesh_obj("Studio_Backdrop", bm_bg, m_backdrop, loc=(0, 2.5, 0.0), smooth=True)

# 11. ILUMINACIÓN ESTUDIO MULTI-ÁNGULO EQUILIBRADA
# Front Beauty Light (Ilumina suavemente el rostro)
l_beauty = bpy.data.objects.new("Beauty_Light", bpy.data.lights.new("Beauty_Light", 'AREA'))
l_beauty.data.energy = 22.0
l_beauty.data.size = 2.0
l_beauty.data.color = (1.0, 0.97, 0.94)
l_beauty.location = (0.1, -2.2, 1.55)
l_beauty.rotation_euler = (math.radians(75), 0, math.radians(3))
col.objects.link(l_beauty)

# Key Light Frontal 3/4
l_key = bpy.data.objects.new("Key_Light", bpy.data.lights.new("Key_Light", 'AREA'))
l_key.data.energy = 38.0
l_key.data.size = 2.2
l_key.data.color = (0.95, 0.95, 1.0)
l_key.location = (1.8, -2.8, 2.2)
l_key.rotation_euler = (math.radians(55), math.radians(10), math.radians(35))
col.objects.link(l_key)

# Fill Light Izquierda
l_fill = bpy.data.objects.new("Fill_Light", bpy.data.lights.new("Fill_Light", 'AREA'))
l_fill.data.energy = 22.0
l_fill.data.size = 2.5
l_fill.data.color = (0.75, 0.85, 1.0)
l_fill.location = (-2.0, -2.2, 1.8)
l_fill.rotation_euler = (math.radians(45), math.radians(-15), math.radians(-45))
col.objects.link(l_fill)

# Rim Light Trasera Izquierda (Contorno de silueta y coleta)
l_rim = bpy.data.objects.new("Rim_Light_L", bpy.data.lights.new("Rim_Light_L", 'SPOT'))
l_rim.data.energy = 85.0
l_rim.data.spot_size = math.radians(75)
l_rim.data.color = (0.9, 0.85, 1.0)
l_rim.location = (-1.2, 2.2, 2.4)
l_rim.rotation_euler = (math.radians(-130), math.radians(-15), math.radians(-150))
col.objects.link(l_rim)

# Rim Light Trasera Derecha (Contorno opuesto para separación de silueta)
l_rim_r = bpy.data.objects.new("Rim_Light_R", bpy.data.lights.new("Rim_Light_R", 'SPOT'))
l_rim_r.data.energy = 75.0
l_rim_r.data.spot_size = math.radians(75)
l_rim_r.data.color = (0.85, 0.90, 1.0)
l_rim_r.location = (1.2, 2.2, 2.4)
l_rim_r.rotation_euler = (math.radians(-130), math.radians(15), math.radians(150))
col.objects.link(l_rim_r)

# Luz de Relleno Trasera (para la vista posterior)
l_back_fill = bpy.data.objects.new("Back_Fill_Light", bpy.data.lights.new("Back_Fill_Light", 'AREA'))
l_back_fill.data.energy = 35.0
l_back_fill.data.size = 2.5
l_back_fill.data.color = (0.85, 0.90, 1.0)
l_back_fill.location = (0.0, 3.0, 1.6)
l_back_fill.rotation_euler = (math.radians(-65), 0, 0)
col.objects.link(l_back_fill)

# 12. CONFIGURACIÓN DE LAS 4 CÁMARAS PARA LA PREVISUALIZACIÓN DE 4 VISTAS (REGLA 5)
output_dir = r"E:\Darx_Proyect\Saved\Anime_Character_Workspace"
os.makedirs(output_dir, exist_ok=True)

scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.film_transparent = False
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'Medium High Contrast'

cameras_config = [
    ("Cam_01_Frontal", 45.0, (0.0, -3.2, 0.90), (0.0, 0.0, 0.88), "view_01_frontal.png"),
    ("Cam_02_Trasera", 45.0, (0.0, 3.2, 0.90), (0.0, 0.0, 0.88), "view_02_trasera.png"),
    ("Cam_03_Retrato", 75.0, (0.05, -1.15, 1.50), (0.0, 0.0, 1.50), "view_03_retrato.png"),
    ("Cam_04_Accion34", 42.0, (2.2, -2.8, 1.25), (0.0, 0.0, 0.88), "view_04_accion34.png")
]

rendered_paths = []
for name, lens, loc, target, filename in cameras_config:
    cam_d = bpy.data.cameras.new(name)
    cam_d.lens = lens
    cam_o = bpy.data.objects.new(name, cam_d)
    cam_o.location = loc
    direction = Vector(target) - Vector(loc)
    cam_o.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    col.objects.link(cam_o)
    scene.camera = cam_o

    out_p = os.path.join(output_dir, filename)
    scene.render.filepath = out_p
    print(f"Renderizando {name} en {out_p}...")
    bpy.ops.render.render(write_still=True)
    rendered_paths.append(out_p)

# 13. FASE 5: EXPORTACIÓN FBX OPTIMIZADA PARA UNREAL ENGINE 5
fbx_out = os.path.join(output_dir, "SK_Anime_Kira.fbx")
bpy.ops.object.select_all(action='DESELECT')
char_objects = [o for o in col.objects if (o.name.startswith("CH_") or o.name.startswith("WP_")) and o.type == 'MESH']
for o in char_objects:
    o.select_set(True)
if char_objects:
    bpy.context.view_layer.objects.active = char_objects[0]
    bpy.ops.export_scene.fbx(
        filepath=fbx_out,
        use_selection=True,
        apply_scale_options='FBX_SCALE_UNITS',
        object_types={'MESH'}
    )
    print(f"Exportacion FBX Fase 5 completada: {fbx_out} ({len(char_objects)} mallas exportadas)")

# Guardar archivo .blend maestro actualizado
blend_out = os.path.join(output_dir, "CH_Anime_Kira.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_out)
print(f"Archivo .blend guardado en: {blend_out}")
print("=" * 80)


"""Boss 6: Sujeto Cero (El Experimento Telequinético)
Ajustes solicitados:
1. Posición de rodillas corregida:
   - Eliminación total de hiperextensión (la rodilla antes estaba en Y=+0.04 hacia atrás).
   - Flexión anatómica natural de gravedad cero hacia adelante (Y=-0.08), pantorrilla relajada hacia atrás (Y=+0.02).
2. Pies mejorados y estructurados:
   - Talón definido (calcáneo), arco plantar estilizado, almohadilla metatarsal y dedos/puntera articulada en flexión plantar ingrávida.
   - Suelas de contención magnética con detalles de alta tecnología.
3. Cabeza con forma humana real:
   - Estructura craneofacial humana: bóveda craneal redondeada, sienes estrechadas, pómulos (arcos cigomáticos) marcados, mandíbula angular definida y mentón esculpido.
   - Integración del visor espectral tenebroso, respirador tipo mordaza y clavijas neurales sobre esta base craneofacial humana.
4. Aros orbitantes sin colisión mantenidos (radios amplios, cero clipping).
"""

import bpy, bmesh, math, os, sys
from mathutils import Vector, Matrix, Euler

art_blender_dir = r"E:\Darx_Proyect\Art\Blender"
if art_blender_dir not in sys.path:
    sys.path.append(art_blender_dir)

import darx_lib as dl

output_dir = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"
os.makedirs(output_dir, exist_ok=True)

ARM_NAME = "ARM_Boss_Telekinetic"
SK_NAME = "SK_Boss_Telekinetic"
COL_NAME = "DARX_TelekineticBoss"
R = math.radians

# Clean Scene
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.resolution_x = 960
scene.render.resolution_y = 960
scene.render.film_transparent = False

col = dl.coll(COL_NAME)

# --------------------------------------------------------------------------
# 1. MATERIALES PBR
# --------------------------------------------------------------------------
m_suit_dark = dl.mat("M_Telek_SuitDark", (0.040, 0.040, 0.048), rough=0.45, metal=0.08)
m_suit_joint = dl.mat("M_Telek_SuitJoint", (0.020, 0.020, 0.024), rough=0.65, metal=0.0)

m_armor_black = dl.mat("M_Telek_ArmorBlack", (0.10, 0.10, 0.12), rough=0.25, metal=0.90)
m_armor_iron = dl.mat("M_Telek_ArmorIron", (0.24, 0.25, 0.28), rough=0.22, metal=0.94)
m_lab_chrome = dl.mat("M_Lab_Chrome", (0.86, 0.88, 0.92), rough=0.10, metal=0.98)
m_claws_black = dl.mat("M_Telek_ClawsBlack", (0.015, 0.015, 0.02), rough=0.15, metal=0.60)

# Energía Psiónica Espectral
m_core_spectral = dl.mat("M_Telek_CoreSpectral", (0.0, 0.95, 1.0), emis=(0.0, 0.95, 1.0), emis_str=38.0)
m_void_purple = dl.mat("M_Telek_VoidPurple", (0.65, 0.02, 0.95), emis=(0.65, 0.02, 0.95), emis_str=28.0)
m_eye_slit = dl.mat("M_Telek_EyeSlit", (0.0, 1.0, 0.92), emis=(0.0, 1.0, 0.92), emis_str=45.0)

# --------------------------------------------------------------------------
# 2. ARMATURE (POSTURA DE LEVITACIÓN CON FLEXIÓN DE RODILLA NATURAL)
# --------------------------------------------------------------------------
bones = [
    ("root",            (0, 0, 0),          (0, 0, 0.40),       None,          False),
    ("pelvis",          (0, -0.01, 1.20),   (0, -0.01, 1.40),   "root",        False),
    ("spine",           (0, -0.01, 1.40),   (0, -0.02, 1.75),   "pelvis",      False),
    ("chest",           (0, -0.02, 1.75),   (0, -0.04, 2.10),   "spine",       False),
    ("head",            (0, -0.04, 2.10),   (0, -0.05, 2.46),   "chest",       False),

    ("clavicle_r",      (0.12, 0, 2.02),     (0.36, -0.02, 2.02), "chest",      False),
    ("arm_upper_r",     (0.36, -0.02, 2.02), (0.64, -0.08, 1.76), "clavicle_r", False),
    ("arm_lower_r",     (0.64, -0.08, 1.76), (0.88, -0.18, 1.48), "arm_upper_r", False),
    ("hand_r",          (0.88, -0.18, 1.48), (1.06, -0.26, 1.30), "arm_lower_r", False),

    ("clavicle_l",      (-0.12, 0, 2.02),    (-0.36, -0.02, 2.02), "chest",     False),
    ("arm_upper_l",     (-0.36, -0.02, 2.02), (-0.64, -0.08, 1.76), "clavicle_l", False),
    ("arm_lower_l",     (-0.64, -0.08, 1.76), (-0.88, -0.18, 1.48), "arm_upper_l", False),
    ("hand_l",          (-0.88, -0.18, 1.48), (-1.06, -0.26, 1.30), "arm_lower_l", False),

    ("ring_upper",      (0, 0.02, 1.80),    (0, 0.02, 2.00),    "chest",       False),
    ("ring_lower",      (0, 0.02, 1.48),    (0, 0.02, 1.68),    "spine",       False),
    ("focus_r",         (1.06, -0.26, 1.30), (1.20, -0.32, 1.30), "hand_r",     False),
    ("focus_l",         (-1.06, -0.26, 1.30), (-1.20, -0.32, 1.30), "hand_l",   False),

    # PIERNAS CON FLEXIÓN NATURAL DE GRAVEDAD CERO (Knee forward Y=-0.08, Calf back Y=+0.02)
    ("thigh_r",         (0.18, -0.01, 1.20), (0.20, -0.08, 0.74), "pelvis",     False),
    ("calf_r",          (0.20, -0.08, 0.74), (0.17, 0.02, 0.32),  "thigh_r",   False),
    ("foot_r",          (0.17, 0.02, 0.32),  (0.16, -0.16, 0.06), "calf_r",    False),

    ("thigh_l",         (-0.18, -0.01, 1.20), (-0.20, -0.08, 0.74), "pelvis",    False),
    ("calf_l",          (-0.20, -0.08, 0.74), (-0.17, 0.02, 0.32),  "thigh_l",  False),
    ("foot_l",          (-0.17, 0.02, 0.32),  (-0.16, -0.16, 0.06), "calf_l",   False),
]
arm_obj = dl.armature(ARM_NAME, bones, COL_NAME)

# --------------------------------------------------------------------------
# 3. CONSTRUCCIÓN DE LA MALLA
# --------------------------------------------------------------------------
b = dl.MB(SK_NAME)
bm = b.bm

def _crear_anillo(bm, center, rx, ry, n_pts=24, rot_euler=None, mod_front=0.0, mod_side=0.0):
    M = Matrix.Translation(Vector(center))
    if rot_euler:
        M = M @ Euler(rot_euler, 'XYZ').to_matrix().to_4x4()
    verts = []
    for i in range(n_pts):
        theta = 2.0 * math.pi * i / n_pts
        r_scale = 1.0
        if math.sin(theta) < 0:
            r_scale += mod_front * abs(math.sin(theta))
        r_scale += mod_side * abs(math.cos(theta))
        x = rx * math.cos(theta) * r_scale
        y = ry * math.sin(theta) * r_scale
        v = bm.verts.new(M @ Vector((x, y, 0.0)))
        verts.append(v)
    return verts

def _conectar_anillos(bm, r1, r2, m_idx=0, smooth=True):
    faces = []
    n = len(r1)
    for i in range(n):
        i_next = (i + 1) % n
        f = bm.faces.new([r1[i], r1[i_next], r2[i_next], r2[i]])
        f.material_index = m_idx
        f.smooth = smooth
        faces.append(f)
    return faces

def _tapar_anillo(bm, ring, top=True, center_offset=0.04, m_idx=0, smooth=True):
    n = len(ring)
    c_pos = sum((v.co for v in ring), Vector()) / n
    c_pos.z += (center_offset if top else -center_offset)
    v_center = bm.verts.new(c_pos)
    faces = []
    for i in range(n):
        i_next = (i + 1) % n
        if top:
            f = bm.faces.new([v_center, ring[i], ring[i_next]])
        else:
            f = bm.faces.new([v_center, ring[i_next], ring[i]])
        f.material_index = m_idx
        f.smooth = smooth
        faces.append(f)
    return [v_center] + ring

# =========================================================================
# TORSO Y TRAJE DE CONTENCIÓN
# =========================================================================
idx_suit = b.midx(m_suit_dark)
anillos_torso_def = [
    (1.10, 0.19, 0.13, 0.0, 0.00, None, 0.02, 0.02, "pelvis"),
    (1.24, 0.25, 0.17, 0.0, 0.00, None, 0.03, 0.04, "pelvis"),
    (1.40, 0.22, 0.15, 0.0, -0.01, None, 0.03, 0.02, "spine"),
    (1.58, 0.26, 0.17, 0.0, -0.02, (R(2), 0, 0), 0.05, 0.04, "spine"),
    (1.76, 0.31, 0.19, 0.0, -0.02, (R(3), 0, 0), 0.06, 0.05, "chest"),
    (1.94, 0.33, 0.20, 0.0, -0.02, (R(3), 0, 0), 0.07, 0.06, "chest"),
    (2.06, 0.25, 0.16, 0.0, -0.01, None, 0.03, 0.02, "chest"),
    (2.14, 0.13, 0.11, 0.0, -0.01, None, 0.0, 0.0, "head"),
]

rings_torso = []
for z, rx, ry, cx, cy, rot_e, mod_f, mod_s, bname in anillos_torso_def:
    b.bone(bname)
    r = _crear_anillo(bm, (cx, cy, z), rx, ry, n_pts=24, rot_euler=rot_e, mod_front=mod_f, mod_side=mod_s)
    rings_torso.append(r)

for i in range(len(rings_torso) - 1):
    b.bone(anillos_torso_def[i][8])
    _conectar_anillos(bm, rings_torso[i], rings_torso[i+1], m_idx=idx_suit, smooth=True)

b.bone("pelvis")
_tapar_anillo(bm, rings_torso[0], top=False, center_offset=0.06, m_idx=idx_suit, smooth=True)
b.bone("head")
_tapar_anillo(bm, rings_torso[-1], top=True, center_offset=0.03, m_idx=idx_suit, smooth=True)

# COSTILLAS DE CONTENCIÓN EXTERNAS
b.bone("spine")
for sign in (1, -1):
    for idx_c, z_cost in enumerate([1.42, 1.54, 1.66]):
        b.seg((sign * 0.24, -0.02, z_cost), (sign * 0.21, -0.16, z_cost - 0.02), 0.018, 0.014, m=m_armor_black, seg=8, smooth=True)
        b.seg((sign * 0.21, -0.16, z_cost - 0.02), (sign * 0.06, -0.19, z_cost - 0.01), 0.014, 0.010, m=m_armor_iron, seg=8, smooth=True)
        b.sph(0.010, (sign * 0.14, -0.18, z_cost - 0.015), m=m_void_purple, smooth=True)

# REACTOR DE VACÍO PECTORAL
b.bone("chest")
b.box((0.28, 0.05, 0.24), loc=(0, -0.21, 1.88), rot=(3, 0, 0), m=m_armor_black)
for sgn_bar in (1, -1):
    b.seg((sgn_bar * 0.12, -0.21, 1.96), (sgn_bar * 0.16, -0.27, 1.94), 0.016, 0.012, m=m_armor_iron, seg=8, smooth=True)
    b.seg((sgn_bar * 0.12, -0.21, 1.80), (sgn_bar * 0.16, -0.27, 1.82), 0.016, 0.012, m=m_armor_iron, seg=8, smooth=True)

b.cyl(0.11, 0.04, loc=(0, -0.24, 1.88), rot=(93, 0, 0), m=m_armor_iron)
b.cyl(0.08, 0.045, loc=(0, -0.25, 1.88), rot=(93, 0, 0), m=m_void_purple)
b.box((0.085, 0.085, 0.085), loc=(0, -0.275, 1.88), rot=(0, R(45), R(45)), m=m_core_spectral)

# CABLES DORSALES ROTOS FLOTANDO EN GRAVEDAD CERO
b.bone("chest")
cables_dorsales = [
    [(0.10, 0.15, 1.92), (0.24, 0.36, 2.05), (0.42, 0.55, 2.32)],
    [(-0.10, 0.15, 1.92), (-0.24, 0.36, 2.02), (-0.40, 0.52, 2.26)],
    [(0.05, 0.16, 1.80), (0.14, 0.40, 1.78), (0.26, 0.62, 1.90)],
    [(-0.05, 0.16, 1.80), (-0.16, 0.38, 1.79), (-0.28, 0.58, 1.92)],
    [(0.0, 0.16, 1.98), (0.02, 0.42, 2.18), (0.06, 0.66, 2.46)],
]
for pts in cables_dorsales:
    b.seg(pts[0], pts[1], 0.020, 0.014, m=m_suit_joint, seg=8, smooth=True)
    b.seg(pts[1], pts[2], 0.014, 0.007, m=m_suit_joint, seg=8, smooth=True)
    b.cyl(0.015, 0.04, loc=pts[2], rot=(25, 30, 0), m=m_core_spectral)

# =========================================================================
# CABEZA CON FORMA HUMANA REAL (ANATOMÍA CRANEOFACIAL + HORROR BIOCONTENCIÓN)
# =========================================================================
b.bone("head")
# Cuello humanoide con esternocleidomastoideo visible
b.seg((0, -0.01, 2.12), (0, -0.03, 2.22), 0.088, 0.080, m=m_suit_joint, seg=14, smooth=True)

# Perfiles anatómicos de la cabeza humana:
# (Z, radioX, radioY, centroX, centroY, mod_front, mod_side)
# Mod_front positivo expande pómulos/nariz/mentón hacia adelante (-Y)
perfiles_cabeza_humana = [
    # 1. Base mandíbula y cuello alto
    (2.18, 0.085, 0.085, 0.0, -0.02, 0.02, 0.01),
    # 2. Mentón y ángulo mandibular (mentón chiseled hacia adelante, ramas mandibulares laterales)
    (2.24, 0.095, 0.105, 0.0, -0.05, 0.12, 0.06),
    # 3. Boca y labio superior
    (2.29, 0.100, 0.115, 0.0, -0.055, 0.10, 0.05),
    # 4. Pómulos (arcos cigomáticos) y puente nasal / cuencas
    (2.35, 0.118, 0.125, 0.0, -0.045, 0.14, 0.08),
    # 5. Arco superciliar (ceño / frente) y sienes
    (2.41, 0.114, 0.120, 0.0, -0.035, 0.08, 0.04),
    # 6. Bóveda craneal media (parietales más anchos atrás)
    (2.47, 0.105, 0.115, 0.0, -0.015, -0.02, 0.05),
    # 7. Cúspide craneal
    (2.53, 0.065, 0.075, 0.0, 0.00, -0.05, 0.02),
]

rings_head = []
for z, rx, ry, cx, cy, mod_f, mod_s in perfiles_cabeza_humana:
    r = _crear_anillo(bm, (cx, cy, z), rx, ry, n_pts=22, mod_front=mod_f, mod_side=mod_s)
    rings_head.append(r)

for i in range(len(rings_head) - 1):
    _conectar_anillos(bm, rings_head[i], rings_head[i+1], m_idx=idx_suit, smooth=True)
_tapar_anillo(bm, rings_head[0], top=False, center_offset=0.03, m_idx=idx_suit, smooth=True)
_tapar_anillo(bm, rings_head[-1], top=True, center_offset=0.03, m_idx=idx_suit, smooth=True)

# Mentón humanoide reforzado (chin plate)
b.prism(0.08, 0.06, 0.04, loc=(0, -0.165, 2.23), rot=(14, 0, 0), taper=0.6, m=m_armor_black)

# Respirador / Mordaza en la boca
b.box((0.11, 0.05, 0.045), loc=(0, -0.170, 2.28), rot=(10, 0, 0), m=m_armor_black)
for x_g in (-0.03, 0.0, 0.03):
    b.box((0.008, 0.02, 0.03), loc=(x_g, -0.198, 2.28), rot=(10, 0, 0), m=m_void_purple)

# Pómulos y nariz angular
b.prism(0.04, 0.05, 0.06, loc=(0, -0.180, 2.34), rot=(5, 0, 0), taper=0.4, m=m_armor_black)

# Hendidura Ocular Espectral en cuencas humanas
b.box((0.17, 0.035, 0.018), loc=(0, -0.175, 2.38), rot=(5, 0, 0), m=m_eye_slit)
for sign in (1, -1):
    b.box((0.025, 0.02, 0.008), loc=(sign * 0.065, -0.170, 2.42), rot=(12, sign * 12, 0), m=m_core_spectral)

# Corona occipital de espinas biomecánicas en la nuca
for sign in (1, -1):
    b.seg((sign * 0.08, 0.09, 2.44), (sign * 0.16, 0.16, 2.56), 0.018, 0.003, m=m_armor_black, seg=8, smooth=True)
    b.seg((sign * 0.11, 0.05, 2.40), (sign * 0.20, 0.11, 2.48), 0.016, 0.003, m=m_armor_iron, seg=8, smooth=True)
    b.sph(0.014, (sign * 0.16, 0.16, 2.56), m=m_core_spectral, smooth=True)

# =========================================================================
# BRAZOS, GRILLETES Y MANOS EN TRANCE SINIESTRO
# =========================================================================
for side, sign in [("r", 1), ("l", -1)]:
    b.bone(f"clavicle_{side}")
    p_clav_start = (sign * 0.12, 0.0, 2.02)
    p_shoulder = (sign * 0.36, -0.02, 2.02)
    b.seg(p_clav_start, p_shoulder, 0.075, 0.065, m=m_suit_dark, seg=12, smooth=True)
    b.box((0.15, 0.15, 0.07), loc=(sign * 0.36, -0.02, 2.06), rot=(10, sign * 25, 0), m=m_armor_black)
    b.cyl(0.040, 0.035, loc=(sign * 0.36, -0.02, 2.02), rot=(0, 90, 0), m=m_armor_iron)

    # Brazo Superior
    b.bone(f"arm_upper_{side}")
    p_elbow = (sign * 0.64, -0.08, 1.76)
    b.seg(p_shoulder, p_elbow, 0.062, 0.048, m=m_suit_dark, seg=14, smooth=True)
    b.sph(0.052, p_elbow, m=m_suit_joint, smooth=True)

    # Antebrazo con Grillete
    b.bone(f"arm_lower_{side}")
    p_wrist = (sign * 0.88, -0.18, 1.48)
    b.seg(p_elbow, p_wrist, 0.052, 0.040, m=m_suit_dark, seg=14, smooth=True)
    b.cyl(0.072, 0.070, loc=(sign * 0.80, -0.15, 1.54), rot=(20, sign * 35, 0), m=m_armor_black)
    b.cyl(0.064, 0.075, loc=(sign * 0.80, -0.15, 1.54), rot=(20, sign * 35, 0), m=m_core_spectral)
    b.seg((sign * 0.84, -0.18, 1.50), (sign * 0.93, -0.14, 1.62), 0.016, 0.012, m=m_armor_iron, seg=8, smooth=True)

    # Mano y Garras Psiónicas
    b.bone(f"hand_{side}")
    p_palm = (sign * 0.96, -0.22, 1.40)
    b.seg(p_wrist, p_palm, 0.040, 0.032, m=m_suit_joint, seg=10, smooth=True)
    b.box((0.055, 0.070, 0.026), loc=p_palm, rot=(25, sign * -25, 0), m=m_armor_black)

    for idx_finger, (dx, dy, dz) in enumerate([(-0.025, -0.06, -0.04), (0.0, -0.09, -0.05), (0.025, -0.08, -0.04), (0.045, -0.05, -0.03)]):
        f_base = (p_palm[0] + dx * sign, p_palm[1] + dy, p_palm[2] + dz)
        f_tip = (f_base[0] + dx * 1.6 * sign, f_base[1] - 0.08, f_base[2] - 0.07)
        b.seg(f_base, f_tip, 0.010, 0.002, m=m_claws_black, seg=8, smooth=True)

# =========================================================================
# AROS VECTORIALES ORBITANTES: CERO CLIPPING (HOLGURA AMPLIA > 30 CM)
# =========================================================================
def _crear_aro_amplio_sin_colision(mb, r_major, r_minor, center, rot_euler, m_body, m_glow, bone_name, n_segs=32):
    mb.bone(bone_name)
    pts = []
    for i in range(n_segs):
        theta = 2.0 * math.pi * i / n_segs
        pts.append(Vector((r_major * math.cos(theta), r_major * math.sin(theta), 0.0)))
    M = Matrix.Translation(Vector(center)) @ Euler(rot_euler, 'XYZ').to_matrix().to_4x4()
    pts_world = [M @ p for p in pts]

    for i in range(n_segs):
        i_next = (i + 1) % n_segs
        m_curr = m_glow if (i % 4 == 0) else m_body
        mb.seg(pts_world[i], pts_world[i_next], r_minor, r_minor, m=m_curr, seg=8, smooth=True)

# Aro Superior
_crear_aro_amplio_sin_colision(b, 0.96, 0.015, (0, 0.02, 1.80), (R(12), R(-18), 0), m_armor_black, m_core_spectral, "ring_upper", n_segs=32)
b.bone("ring_upper")
for angle in (0.4, 2.5, 4.6):
    M_ang = Matrix.Translation(Vector((0, 0.02, 1.80))) @ Euler((R(12), R(-18), 0), 'XYZ').to_matrix().to_4x4()
    p_mono = M_ang @ Vector((0.96 * math.cos(angle), 0.96 * math.sin(angle), 0.0))
    b.box((0.05, 0.05, 0.24), loc=p_mono, rot=(R(45), R(45), angle), m=m_armor_black)
    b.box((0.02, 0.02, 0.28), loc=p_mono, rot=(R(45), R(45), angle), m=m_core_spectral)

# Aro Inferior
_crear_aro_amplio_sin_colision(b, 1.10, 0.016, (0, 0.02, 1.48), (R(-14), R(20), 0), m_armor_black, m_void_purple, "ring_lower", n_segs=32)
b.bone("ring_lower")
for angle in (1.2, 3.3, 5.4):
    M_ang = Matrix.Translation(Vector((0, 0.02, 1.48))) @ Euler((R(-14), R(20), 0), 'XYZ').to_matrix().to_4x4()
    p_mono = M_ang @ Vector((1.10 * math.cos(angle), 1.10 * math.sin(angle), 0.0))
    b.box((0.06, 0.06, 0.26), loc=p_mono, rot=(R(45), 0, angle), m=m_armor_iron)
    b.box((0.025, 0.025, 0.30), loc=p_mono, rot=(R(45), 0, angle), m=m_void_purple)

# Focos psiónicos flotando sobre las palmas
b.bone("focus_r")
b.box((0.08, 0.08, 0.08), loc=(1.10, -0.30, 1.30), rot=(R(45), R(45), 0), m=m_armor_black)
b.sph(0.045, (1.10, -0.30, 1.30), m=m_core_spectral, smooth=True)

b.bone("focus_l")
b.box((0.08, 0.08, 0.08), loc=(-1.10, -0.30, 1.30), rot=(R(45), R(-45), 0), m=m_armor_black)
b.sph(0.045, (-1.10, -0.30, 1.30), m=m_void_purple, smooth=True)

# =========================================================================
# PIERNAS CON FLEXIÓN NATURAL DE GRAVEDAD CERO (CERO HIPEREXTENSIÓN)
# Y PIES ESTRUCTURADOS CON TALÓN, ARCO Y DEDOS
# =========================================================================
for side, sign in [("r", 1), ("l", -1)]:
    b.bone(f"thigh_{side}")
    p_hip = (sign * 0.18, -0.01, 1.20)
    # Rodilla doblada hacia adelante en flexión natural (-Y, Z=0.74)
    p_knee_top = (sign * 0.20, -0.04, 0.82)
    p_knee_center = (sign * 0.20, -0.08, 0.74)
    p_knee_bot = (sign * 0.19, -0.05, 0.66)

    # Muslo anterior descendiendo hacia la rodilla adelantada
    b.seg(p_hip, p_knee_top, 0.110, 0.085, m=m_suit_dark, seg=16, smooth=True)
    # Cuádriceps y placa femoral
    b.seg((sign * 0.18, -0.07, 1.15), (sign * 0.20, -0.10, 0.86), 0.050, 0.030, m=m_armor_black, seg=12, smooth=True)

    # --- ARTICULACIÓN DE RODILLA FLEXIONADA HACIA ADELANTE ---
    b.seg(p_knee_top, p_knee_bot, 0.088, 0.082, m=m_suit_joint, seg=14, smooth=True)

    # Rótula en cuña angular (apuntando hacia el frente en -Y)
    b.box((0.090, 0.060, 0.100), loc=(sign * 0.20, -0.115, 0.74), rot=(20, sign * 5, 0), m=m_armor_black)
    # Ranura emisora psiónica central
    b.box((0.025, 0.018, 0.080), loc=(sign * 0.20, -0.148, 0.74), rot=(20, sign * 5, 0), m=m_core_spectral)

    # Placa suprapatelar
    b.box((0.100, 0.050, 0.045), loc=(sign * 0.20, -0.095, 0.82), rot=(25, sign * 5, 0), m=m_armor_iron)

    # Pistones hidráulicos laterales (siguiendo la inclinación de la flexión)
    for sgn_lat in (1, -1):
        x_piston = sign * 0.20 + sgn_lat * 0.068
        b.cyl(0.016, 0.080, loc=(x_piston, -0.03, 0.74), rot=(-15, 0, 0), m=m_lab_chrome)
        b.cyl(0.024, 0.045, loc=(x_piston, -0.03, 0.77), rot=(-15, 0, 0), m=m_armor_black)
        b.sph(0.018, (x_piston, -0.02, 0.80), m=m_armor_iron, smooth=True)
        b.sph(0.018, (x_piston, -0.04, 0.68), m=m_armor_iron, smooth=True)

    # --- PANTORRILLA (Flotando relajada hacia atrás en +Y) ---
    b.bone(f"calf_{side}")
    p_ankle = (sign * 0.17, 0.02, 0.32)
    b.seg(p_knee_bot, p_ankle, 0.082, 0.058, m=m_suit_dark, seg=14, smooth=True)

    # Espinillera biomecánica
    b.seg((sign * 0.19, -0.08, 0.68), (sign * 0.18, -0.02, 0.44), 0.035, 0.020, m=m_armor_black, seg=10, smooth=True)

    # Grillete magnético en el tobillo
    b.cyl(0.078, 0.060, loc=(sign * 0.17, 0.01, 0.38), rot=(-12, sign * 5, 0), m=m_armor_black)
    b.cyl(0.070, 0.065, loc=(sign * 0.17, 0.01, 0.38), rot=(-12, sign * 5, 0), m=m_core_spectral)

    # =========================================================================
    # PIES ESTRUCTURADOS CON ANATOMÍA REAL (TALÓN, ARCO, METATARSO Y DEDOS)
    # =========================================================================
    b.bone(f"foot_{side}")
    # 1. Talón (Calcáneo)
    p_heel = (sign * 0.17, 0.07, 0.28)
    b.seg(p_ankle, p_heel, 0.058, 0.050, m=m_armor_black, seg=10, smooth=True)
    b.sph(0.042, p_heel, m=m_armor_black, smooth=True)

    # 2. Empeine y Arco Plantar
    p_midfoot = (sign * 0.168, -0.03, 0.21)
    b.seg(p_ankle, p_midfoot, 0.054, 0.046, m=m_suit_dark, seg=10, smooth=True)
    b.seg(p_heel, p_midfoot, 0.046, 0.042, m=m_armor_iron, seg=10, smooth=True)

    # 3. Almohadilla Metatarsal (Base de la planta)
    p_ball = (sign * 0.165, -0.11, 0.13)
    b.seg(p_midfoot, p_ball, 0.046, 0.044, m=m_armor_black, seg=10, smooth=True)
    # Placa de suela magnética
    b.box((0.070, 0.090, 0.016), loc=(sign * 0.165, -0.06, 0.18), rot=(42, sign * 5, 0), m=m_armor_iron)

    # 4. Dedos / Puntera Articulada en Flexión Plantar Ingrávida
    p_toes = (sign * 0.160, -0.18, 0.05)
    b.seg(p_ball, p_toes, 0.040, 0.018, m=m_armor_black, seg=10, smooth=True)
    # Puntas de garra/refuerzo en los dedos
    for idx_t, dx_t in enumerate([-0.022, 0.0, 0.022]):
        p_toe_base = (sign * 0.165 + dx_t, -0.12, 0.12)
        p_toe_tip = (sign * 0.160 + dx_t * 1.2, -0.20, 0.03)
        b.seg(p_toe_base, p_toe_tip, 0.010, 0.002, m=m_claws_black, seg=6, smooth=True)

# --------------------------------------------------------------------------
# 4. BUILD Y ARMATURE
# --------------------------------------------------------------------------
mesh_obj = b.build(COL_NAME)
if mesh_obj and arm_obj:
    mesh_obj.parent = arm_obj
    mod = mesh_obj.modifiers.new("Armature", 'ARMATURE')
    mod.object = arm_obj
    mod.use_vertex_groups = True

# --------------------------------------------------------------------------
# 5. LIGHTING & CAMERA
# --------------------------------------------------------------------------
if scene.world is None:
    scene.world = bpy.data.worlds.new("World_Studio")
scene.world.use_nodes = True
bg = scene.world.node_tree.nodes.get("Background")
if bg:
    bg.inputs["Color"].default_value = (0.025, 0.03, 0.04, 1.0)
    bg.inputs["Strength"].default_value = 0.4

cam_data = bpy.data.cameras.new("Cam_Boss6_Adjust")
cam_obj = bpy.data.objects.new("Cam_Boss6_Adjust", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_data.lens = 45.0

empty_target = bpy.data.objects.new("Cam_Boss6_Target", None)
scene.collection.objects.link(empty_target)
empty_target.location = (0.0, -0.10, 1.55)

tt = cam_obj.constraints.new(type='TRACK_TO')
tt.target = empty_target
tt.track_axis = 'TRACK_NEGATIVE_Z'
tt.up_axis = 'UP_Y'

dist = 4.8
cam_obj.location = (dist * 0.65, -dist * 0.85, 1.55 + dist * 0.30)

# Studio Lights
key_data = bpy.data.lights.new("Light_Key_B6", type='AREA')
key_obj = bpy.data.objects.new("Light_Key_B6", key_data)
scene.collection.objects.link(key_obj)
key_data.energy = 250.0
key_data.size = 3.0
key_data.color = (0.92, 0.95, 1.0)
key_obj.location = (dist * 0.8, -dist * 0.7, 1.55 + dist * 0.9)

fill_data = bpy.data.lights.new("Light_Fill_B6", type='AREA')
fill_obj = bpy.data.objects.new("Light_Fill_B6", fill_data)
scene.collection.objects.link(fill_obj)
fill_data.energy = 85.0
fill_data.size = 4.0
fill_data.color = (0.35, 0.15, 0.60)
fill_obj.location = (-dist * 0.8, -dist * 0.7, 1.55 + dist * 0.5)

rim_data = bpy.data.lights.new("Light_Rim_B6", type='AREA')
rim_obj = bpy.data.objects.new("Light_Rim_B6", rim_data)
scene.collection.objects.link(rim_obj)
rim_data.energy = 280.0
rim_data.size = 3.0
rim_data.color = (0.0, 0.92, 1.0)
rim_obj.location = (-dist * 0.3, dist * 0.9, 1.55 + dist * 0.7)

out_despues = os.path.join(output_dir, "boss6_despues.png")
scene.render.filepath = out_despues
bpy.ops.render.render(write_still=True)
print(f"RENDERED CORRECTED ANATOMY BOSS 6 DESPUES -> {out_despues}")

blend_path = r"E:\Darx_Proyect\Saved\Player_Skin_Workspace\DarX_Boss6_Redesign.blend"
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f"FILE_SAVED: {blend_path}")

"""Boss 5: El Amalgama Celular (Proyecto Quimera Alfa)
Estilo Auténtico de Titán Colosal (Attack on Titan):
- Haces y cables musculares anatómicamente definidos (escala amplia de paquete muscular, no textura pequeña)
- Alternancia de:
  * Surcos y hendiduras profundas en el OXBLOOD ORIGINAL DE MUESTRA (#2E1312)
  * Cuerdas y paquetes de carne en ROJO VIVO ARTERIAL (#C5160C)
  * Bandas de TENDÓN Y FASCIA BLANCA MARFIL (#EFE7DE)
- Cables musculares de cuello (esternocleidomastoideo) y serratos intercostales en el torso
- Cuernos de titanio aeroespacial y ojos rojos agónicos de suplicio
"""

import bpy, bmesh, math, os, sys
from mathutils import Vector, Matrix, Euler

art_blender_dir = r"E:\Darx_Proyect\Art\Blender"
if art_blender_dir not in sys.path:
    sys.path.append(art_blender_dir)

import darx_lib as dl

output_dir = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"
os.makedirs(output_dir, exist_ok=True)

ARM_NAME = "ARM_Boss_Amalgam"
SK_NAME = "SK_Boss_Amalgam"
COL_NAME = "DARX_AmalgamBoss"
R = math.radians

# Clean Scene
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.resolution_x = 960
scene.render.resolution_y = 960
scene.render.film_transparent = False

col = dl.coll(COL_NAME)

# --------------------------------------------------------------------------
# SHADER PROCEDURAL TITÁN COLOSAL (HACES MUSCULARES ANATÓMICOS GRUESOS)
# --------------------------------------------------------------------------
def create_colossal_titan_shader(name, z_scale=5.0, wave_scale=4.5, bump_str=0.80):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    # 1. Coordenadas de Objeto
    tex_coord = nt.nodes.new("ShaderNodeTexCoord")
    mapping = nt.nodes.new("ShaderNodeMapping")
    # Escala macro: cada paquete muscular mide entre 4 y 7 cm de grosor real
    mapping.inputs["Scale"].default_value = (2.2, 2.2, z_scale)
    nt.links.new(tex_coord.outputs["Object"], mapping.inputs["Vector"])

    # 2. Bandas gruesas de cables musculares (Wave Texture macro)
    wave_tex = nt.nodes.new("ShaderNodeTexWave")
    wave_tex.inputs["Scale"].default_value = wave_scale
    wave_tex.inputs["Distortion"].default_value = 2.4
    wave_tex.inputs["Detail"].default_value = 2.0
    wave_tex.inputs["Detail Roughness"].default_value = 0.50
    nt.links.new(mapping.outputs["Vector"], wave_tex.inputs["Vector"])

    # 3. Ruido sutil para estriaciones internas
    noise_fiber = nt.nodes.new("ShaderNodeTexNoise")
    noise_fiber.inputs["Scale"].default_value = 5.0
    noise_fiber.inputs["Detail"].default_value = 4.0
    noise_fiber.inputs["Roughness"].default_value = 0.60
    nt.links.new(mapping.outputs["Vector"], noise_fiber.inputs["Vector"])

    # 4. Mezcla ponderada
    mix_fibers = nt.nodes.new("ShaderNodeMix")
    mix_fibers.data_type = 'FLOAT'
    mix_fibers.inputs["Factor"].default_value = 0.30
    nt.links.new(noise_fiber.outputs["Fac"], mix_fibers.inputs[2])
    nt.links.new(wave_tex.outputs["Fac"], mix_fibers.inputs[3])

    # 5. Rampa de Color Titán Colosal:
    # 0.00: Base en hendidura profunda: #2E1312 exacto
    # 0.22: Músculo profundo oxblood
    # 0.44: ROJO VIVO arterial de Titán Colosal (#C5160C)
    # 0.76: Resalte muscular luminoso
    # 0.88 a 1.00: Bandas de TENDÓN BLANCO MARFIL (#EFE7DE)
    cramp = nt.nodes.new("ShaderNodeValToRGB")

    c_oxblood = (0.027, 0.007, 0.006, 1.0)        # #2E1312 original
    c_deep = (0.095, 0.015, 0.011, 1.0)          # Transición oscura
    c_rojo_vivo = (0.76, 0.045, 0.022, 1.0)       # Rojo vivo Colosal
    c_rojo_bright = (0.96, 0.080, 0.035, 1.0)     # Resalte vivo
    c_tendon = (0.92, 0.88, 0.82, 1.0)            # Fascia y tendón blanco marfil

    cramp.color_ramp.elements[0].position = 0.0
    cramp.color_ramp.elements[0].color = c_oxblood

    cramp.color_ramp.elements[1].position = 1.0
    cramp.color_ramp.elements[1].color = c_tendon

    e1 = cramp.color_ramp.elements.new(0.20)
    e1.color = c_deep

    e2 = cramp.color_ramp.elements.new(0.44)
    e2.color = c_rojo_vivo

    e3 = cramp.color_ramp.elements.new(0.74)
    e3.color = c_rojo_bright

    nt.links.new(mix_fibers.outputs["Result"], cramp.inputs["Fac"])

    # 6. Relieve 3D físico pronunciado (Bump de haces musculares de Titán)
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = bump_str
    bump.inputs["Distance"].default_value = 0.040
    nt.links.new(mix_fibers.outputs["Result"], bump.inputs["Height"])

    # 7. Principled BSDF
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    nt.links.new(cramp.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.35
    bsdf.inputs["Specular IOR Level"].default_value = 0.48

    # Subsurface Scattering orgánico
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.42
        bsdf.inputs["Subsurface Radius"].default_value = (0.9, 0.14, 0.07)
        bsdf.inputs["Subsurface Scale"].default_value = 0.07

    if "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = 0.16
        bsdf.inputs["Coat Roughness"].default_value = 0.20

    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    mat.diffuse_color = (0.65, 0.05, 0.03, 1.0)
    return mat

# Material Titán Colosal
m_titan_colossal = create_colossal_titan_shader("M_Titan_Colossal", z_scale=5.0, wave_scale=4.5, bump_str=0.85)
m_titan_accent = create_colossal_titan_shader("M_Titan_ColossalAccent", z_scale=6.0, wave_scale=5.5, bump_str=0.90)

# Músculo liso oscuro puro (#2E1312) para detalles de fondo
m_flesh_oxblood_pure = dl.mat("M_Flesh_OxbloodPure", (0.18, 0.075, 0.071), rough=0.36, metal=0.0)

# Materiales de Hueso, Titanio y Ojos
m_bone_dark = dl.mat("M_Amalgam_BoneDark", (0.24, 0.22, 0.20), rough=0.35, metal=0.12)
m_bone_ivory = dl.mat("M_Amalgam_BoneIvory", (0.88, 0.85, 0.74), rough=0.18, metal=0.05)
m_claws_black = dl.mat("M_Amalgam_ClawsBlack", (0.015, 0.015, 0.02), rough=0.15, metal=0.50)

m_lab_titanium = dl.mat("M_Lab_Titanium", (0.64, 0.66, 0.70), rough=0.18, metal=0.96)
m_lab_steel = dl.mat("M_Lab_Steel", (0.24, 0.26, 0.30), rough=0.22, metal=0.92)
m_lab_chrome = dl.mat("M_Lab_Chrome", (0.85, 0.88, 0.92), rough=0.12, metal=0.98)

# Ojos rojos agónicos
m_eye_sorrow_red = dl.mat("M_Eye_SorrowRed", (1.0, 0.01, 0.01), emis=(1.0, 0.01, 0.01), emis_str=34.0)
m_eye_tear_glow = dl.mat("M_Eye_TearGlow", (0.85, 0.02, 0.04), emis=(0.85, 0.02, 0.04), emis_str=18.0)
m_purple_glow = dl.mat("M_Amalgam_PurpleGlow", (0.85, 0.0, 1.0), emis=(0.85, 0.0, 1.0), emis_str=28.0)
m_cyan_glow = dl.mat("M_Lab_CyanGlow", (0.0, 0.90, 1.0), emis=(0.0, 0.90, 1.0), emis_str=24.0)

# --------------------------------------------------------------------------
# 2. ARMATURE
# --------------------------------------------------------------------------
bones = [
    ("root",            (0, 0, 0),          (0, 0, 0.20),       None,          False),
    ("pelvis",          (0, 0, 1.05),       (0, 0, 1.30),       "root",        False),
    ("spine",           (0, 0, 1.30),       (0, 0, 1.68),       "pelvis",      False),
    ("chest",           (0, 0, 1.68),       (0, 0, 2.05),       "spine",       False),
    ("head",            (0, 0, 2.05),       (0, -0.04, 2.56),   "chest",       False),

    ("clavicle_r",      (0.18, 0, 2.02),     (0.44, -0.02, 2.02), "chest",      False),
    ("arm_upper_r",     (0.44, -0.02, 2.02), (0.78, -0.06, 1.70), "clavicle_r", False),
    ("arm_lower_r",     (0.78, -0.06, 1.70), (1.08, -0.12, 1.32), "arm_upper_r", False),
    ("hand_r",          (1.08, -0.12, 1.32), (1.28, -0.18, 0.95), "arm_lower_r", False),

    ("clavicle_l",      (-0.18, 0, 2.02),    (-0.44, -0.02, 2.02), "chest",     False),
    ("arm_upper_l",     (-0.44, -0.02, 2.02), (-0.78, -0.06, 1.70), "clavicle_l", False),
    ("arm_lower_l",     (-0.78, -0.06, 1.70), (-1.08, -0.12, 1.32), "arm_upper_l", False),
    ("hand_l",          (-1.08, -0.12, 1.32), (-1.28, -0.18, 0.95), "arm_lower_l", False),

    ("tail_base",       (0.12, 0.18, 1.90),  (0.18, 0.38, 2.28), "chest",      False),
    ("tail_mid",        (0.18, 0.38, 2.28),  (0.12, 0.48, 2.75), "tail_base",   False),
    ("tail_scythe",     (0.12, 0.48, 2.75),  (0.0, 0.22, 3.18),  "tail_mid",    False),

    ("thigh_r",         (0.24, 0, 1.05),     (0.26, 0.04, 0.55), "pelvis",     False),
    ("calf_r",          (0.26, 0.04, 0.55),  (0.28, -0.04, 0.14), "thigh_r",   False),
    ("foot_r",          (0.28, -0.04, 0.14), (0.28, -0.28, 0.0),  "calf_r",    False),

    ("thigh_l",         (-0.24, 0, 1.05),    (-0.26, 0.04, 0.55), "pelvis",    False),
    ("calf_l",          (-0.26, 0.04, 0.55), (-0.28, -0.04, 0.14), "thigh_l",  False),
    ("foot_l",          (-0.28, -0.04, 0.14), (-0.28, -0.28, 0.0), "calf_l",   False),
]
arm_obj = dl.armature(ARM_NAME, bones, COL_NAME)

# --------------------------------------------------------------------------
# 3. CONSTRUCCIÓN DE LA MALLA
# --------------------------------------------------------------------------
b = dl.MB(SK_NAME)
bm = b.bm
idx_colossal = b.midx(m_titan_colossal)

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
# TORSO Y CADERA ESTILO TITÁN COLOSAL
# =========================================================================
anillos_torso_def = [
    (0.88, 0.24, 0.17, 0.0, 0.01, None, 0.02, 0.02, "pelvis"),
    (1.00, 0.31, 0.20, 0.0, 0.00, None, 0.04, 0.06, "pelvis"),
    (1.12, 0.33, 0.21, 0.0, -0.01, None, 0.04, 0.08, "pelvis"),
    (1.26, 0.27, 0.18, 0.0, -0.01, None, 0.04, 0.03, "spine"),
    (1.40, 0.29, 0.19, 0.0, -0.02, None, 0.06, 0.03, "spine"),
    (1.56, 0.35, 0.22, 0.0, -0.02, (R(2), 0, 0), 0.07, 0.06, "spine"),
    (1.74, 0.41, 0.25, 0.0, -0.02, (R(3), 0, 0), 0.10, 0.08, "chest"),
    (1.92, 0.45, 0.26, 0.0, -0.02, (R(3), 0, 0), 0.12, 0.09, "chest"),
    (2.06, 0.36, 0.20, 0.0, -0.01, None, 0.05, 0.03, "chest"),
    (2.16, 0.19, 0.15, 0.0, -0.01, None, 0.0, 0.0, "head"),
]

rings_torso = []
for z, rx, ry, cx, cy, rot_e, mod_f, mod_s, bname in anillos_torso_def:
    b.bone(bname)
    r = _crear_anillo(bm, (cx, cy, z), rx, ry, n_pts=24, rot_euler=rot_e, mod_front=mod_f, mod_side=mod_s)
    rings_torso.append(r)

for i in range(len(rings_torso) - 1):
    b.bone(anillos_torso_def[i][8])
    _conectar_anillos(bm, rings_torso[i], rings_torso[i+1], m_idx=idx_colossal, smooth=True)

b.bone("pelvis")
_tapar_anillo(bm, rings_torso[0], top=False, center_offset=0.08, m_idx=idx_colossal, smooth=True)
b.bone("head")
_tapar_anillo(bm, rings_torso[-1], top=True, center_offset=0.04, m_idx=idx_colossal, smooth=True)

# SERRATOS Y COSTILLAS MUSCULARES (DETALLES ANATÓMICOS DE TITÁN)
b.bone("spine")
for sign in [1, -1]:
    for z_rib in [1.44, 1.54, 1.64]:
        b.seg((sign * 0.28, -0.05, z_rib), (sign * 0.33, 0.06, z_rib + 0.04), 0.032, 0.018, m=m_titan_accent, seg=10, smooth=True)

# =========================================================================
# CADERA Y PIERNAS (MÚSCULOS DE TITÁN COLOSAL)
# =========================================================================
for side, sign in [("r", 1), ("l", -1)]:
    b.bone("pelvis")
    # Glúteos y cadera
    b.seg((sign * 0.22, -0.01, 1.12), (sign * 0.26, 0.01, 0.96), 0.145, 0.155, m=m_titan_colossal, seg=16, smooth=True)
    b.seg((sign * 0.16, 0.05, 1.08), (sign * 0.24, 0.08, 0.94), 0.13, 0.14, m=m_flesh_oxblood_pure, seg=14, smooth=True)

    # --- MUSLO ---
    b.bone(f"thigh_{side}")
    p_hip_center = (sign * 0.25, 0.01, 0.96)
    p_knee = (sign * 0.26, 0.04, 0.55)

    b.seg(p_hip_center, p_knee, 0.160, 0.130, m=m_titan_colossal, seg=18, smooth=True)

    # Cuádriceps frontal con estriaciones prominentes
    b.seg((sign * 0.24, -0.07, 1.00), (sign * 0.26, -0.05, 0.65), 0.105, 0.070, m=m_titan_accent, seg=14, smooth=True)

    # Tensor lateral en oxblood profundo
    b.seg((sign * 0.31, 0.00, 0.96), (sign * 0.33, 0.03, 0.68), 0.075, 0.050, m=m_flesh_oxblood_pure, seg=12, smooth=True)

    # Vasto interno / aductor
    b.seg((sign * 0.15, -0.01, 0.92), (sign * 0.19, 0.02, 0.68), 0.085, 0.055, m=m_titan_colossal, seg=12, smooth=True)

    # Placa de titanio aeroespacial
    b.seg((sign * 0.33, 0.02, 0.88), (sign * 0.35, 0.04, 0.64), 0.038, 0.026, m=m_lab_titanium, seg=10, smooth=True)

    # --- RODILLA ---
    b.seg((sign * 0.26, 0.04, 0.60), p_knee, 0.138, 0.130, m=m_bone_dark, seg=16, smooth=True)

    # --- PANTORRILLA (Gemelos estriados Titán Colosal) ---
    b.bone(f"calf_{side}")
    p_ankle = (sign * 0.28, -0.04, 0.14)
    b.seg(p_knee, (sign * 0.26, 0.02, 0.50), 0.130, 0.130, m=m_bone_dark, seg=16, smooth=True)
    b.seg((sign * 0.26, -0.06, 0.60), (sign * 0.28, -0.11, 0.50), 0.072, 0.052, m=m_bone_ivory, seg=12, smooth=True)
    b.cyl(0.050, 0.03, loc=(sign * 0.28, -0.12, 0.55), rot=(16, sign * 6, 0), m=m_lab_titanium)

    b.seg((sign * 0.26, 0.02, 0.50), p_ankle, 0.135, 0.095, m=m_titan_colossal, seg=16, smooth=True)
    b.seg((sign * 0.26, 0.08, 0.44), (sign * 0.27, 0.04, 0.24), 0.070, 0.035, m=m_titan_accent, seg=12, smooth=True)
    b.seg((sign * 0.28, -0.07, 0.44), (sign * 0.30, -0.10, 0.20), 0.032, 0.020, m=m_lab_titanium, seg=10, smooth=True)
    b.seg((sign * 0.28, -0.04, 0.18), p_ankle, 0.10, 0.09, m=m_bone_dark, seg=14, smooth=True)

    # --- PIE ---
    b.bone(f"foot_{side}")
    b.seg(p_ankle, (sign * 0.28, -0.12, 0.08), 0.09, 0.09, m=m_bone_dark, seg=14, smooth=True)
    b.seg((sign * 0.28, -0.10, 0.08), (sign * 0.28, -0.24, 0.04), 0.10, 0.08, m=m_bone_dark, seg=14, smooth=True)
    for gx, gy, gz in [(sign * 0.22, -0.24, 0.03), (sign * 0.28, -0.28, 0.03), (sign * 0.34, -0.24, 0.03)]:
        b.seg((gx, gy, gz), (gx + sign * 0.02, gy - 0.10, gz - 0.02), 0.018, 0.003, m=m_claws_black, seg=10, smooth=True)

# =========================================================================
# BRAZOS
# =========================================================================
for side, sign in [("r", 1), ("l", -1)]:
    p_clav_start = (sign * 0.18, 0.0, 2.02)
    p_shoulder = (sign * 0.44, -0.02, 2.02)
    p_elbow = (sign * 0.78, -0.06, 1.70)
    p_wrist = (sign * 1.08, -0.12, 1.32)
    p_hand_end = (sign * 1.28, -0.18, 0.95)

    b.bone(f"clavicle_{side}")
    b.seg(p_clav_start, p_shoulder, 0.14, 0.13, m=m_titan_colossal if side == "r" else m_bone_dark, seg=16, smooth=True)

    b.bone(f"arm_upper_{side}")
    b.seg((sign * 0.42, -0.02, 2.02), (sign * 0.48, -0.03, 1.98), 0.15, 0.15, m=m_bone_dark, seg=16, smooth=True)

    if side == "r":
        b.box((0.26, 0.22, 0.11), loc=(0.48, -0.04, 2.02), rot=(15, 30, -10), m=m_bone_dark)
        b.box((0.20, 0.16, 0.05), loc=(0.52, -0.02, 1.92), rot=(15, 30, -10), m=m_titan_accent)
    else:
        b.box((0.28, 0.24, 0.12), loc=(-0.48, -0.04, 2.02), rot=(15, -30, 10), m=m_lab_titanium)
        b.box((0.22, 0.18, 0.05), loc=(-0.52, -0.02, 1.92), rot=(15, -30, 10), m=m_lab_steel)

    # Brazo biológico estriado
    b.seg(p_shoulder, p_elbow, 0.15, 0.13, m=m_titan_colossal if side == "r" else m_bone_dark, seg=18, smooth=True)
    b.cyl(0.16, 0.045, loc=(sign * 0.64, -0.05, 1.82), rot=(20, sign * 35, 0), m=m_lab_titanium)
    b.seg((sign * 0.72, -0.05, 1.74), p_elbow, 0.13, 0.12, m=m_bone_dark, seg=16, smooth=True)

    b.bone(f"arm_lower_{side}")
    b.seg(p_elbow, (sign * 0.84, -0.07, 1.62), 0.12, 0.12, m=m_bone_dark, seg=16, smooth=True)
    b.seg((sign * 0.84, -0.07, 1.62), p_wrist, 0.13, 0.10, m=m_titan_colossal if side == "r" else m_bone_dark, seg=16, smooth=True)
    b.seg((sign * 0.84, -0.14, 1.60), (sign * 1.04, -0.18, 1.36), 0.038, 0.024, m=m_lab_titanium, seg=10, smooth=True)
    b.seg((sign * 1.02, -0.11, 1.36), p_wrist, 0.10, 0.09, m=m_bone_dark, seg=14, smooth=True)

    if side == "l":
        cuchillas = [
            ((-0.94, -0.09, 1.56), (-1.26, -0.15, 1.62), 0.028, 0.003),
            ((-1.02, -0.11, 1.42), (-1.34, -0.18, 1.46), 0.032, 0.003),
            ((-1.08, -0.13, 1.28), (-1.30, -0.16, 1.28), 0.026, 0.003),
        ]
        for p_a, p_b, r_a, r_b in cuchillas:
            b.seg(p_a, p_b, r_a, r_b, m=m_bone_ivory, seg=12, smooth=True)
            b.cyl(r_a * 1.10, 0.022, loc=p_a, rot=(0, 90, 0), m=m_lab_titanium)

    b.bone(f"hand_{side}")
    b.cyl(0.11, 0.04, loc=p_wrist, rot=(20, sign * 35, 0), m=m_lab_titanium)
    b.seg(p_wrist, p_hand_end, 0.11, 0.08, m=m_bone_dark, seg=12, smooth=True)
    if side == "r":
        for k, (gx, gy, gz) in enumerate([(1.20, -0.22, 1.05), (1.24, -0.24, 1.03), (1.28, -0.23, 1.05), (1.32, -0.19, 1.08)]):
            b.seg((gx, gy, gz), (gx + 0.09, gy - 0.16, gz - 0.16), 0.020, 0.003, m=m_claws_black, seg=12, smooth=True)
    else:
        for k, (gx, gy, gz) in enumerate([(-1.20, -0.26, 0.98), (-1.25, -0.28, 0.96), (-1.30, -0.26, 0.98)]):
            b.box((0.030, 0.042, 0.035), loc=(gx, gy, gz), rot=(25, -25, 0), m=m_claws_black)
        for gy_off, gx_off in [(-0.02, 0.0), (0.0, -0.02), (0.02, -0.04)]:
            b.seg((-1.24 + gx_off, -0.20 + gy_off, 0.92), (-1.34 + gx_off, -0.28 + gy_off, 0.82), 0.014, 0.002, m=m_claws_black, seg=8, smooth=True)

# =========================================================================
# CABEZA, TENDONES DE CUELLO, PECTORALES EN ROJO VIVO Y CUERNOS METÁLICOS
# =========================================================================
b.bone("head")
b.seg((0, 0.0, 2.08), (0, -0.04, 2.32), 0.14, 0.12, m=m_titan_colossal, seg=16, smooth=True)
b.seg((0, -0.04, 2.30), (0, -0.06, 2.56), 0.14, 0.12, m=m_titan_colossal, seg=16, smooth=True)

# Tendones de cuello icónicos del Titán Colosal (esternocleidomastoideo)
b.seg((0.09, -0.05, 2.12), (0.05, -0.14, 2.04), 0.024, 0.015, m=m_titan_accent, seg=10, smooth=True)
b.seg((-0.09, -0.05, 2.12), (-0.05, -0.14, 2.04), 0.024, 0.015, m=m_titan_accent, seg=10, smooth=True)

b.prism(0.20, 0.14, 0.07, loc=(0, -0.15, 2.48), rot=(14, 0, 0), taper=0.7, m=m_bone_dark)

# CUERNOS METÁLICOS
c_pts_r = [(0.09, -0.04, 2.56), (0.16, 0.06, 2.76), (0.24, 0.18, 2.96), (0.30, 0.30, 3.16)]
for k in range(len(c_pts_r) - 1):
    m_seg = m_lab_titanium if k % 2 == 0 else m_lab_steel
    b.seg(c_pts_r[k], c_pts_r[k+1], 0.052 - k * 0.012, 0.052 - (k + 1) * 0.012, m=m_seg, seg=14, smooth=True)
b.cyl(0.048, 0.030, loc=(0.16, 0.06, 2.76), rot=(-20, -30, 0), m=m_lab_chrome)
b.cyl(0.032, 0.025, loc=(0.24, 0.18, 2.96), rot=(-20, -30, 0), m=m_lab_chrome)
b.seg((0.30, 0.30, 3.16), (0.33, 0.36, 3.26), 0.014, 0.002, m=m_lab_chrome, seg=10, smooth=True)

c_pts_l = [(-0.09, -0.04, 2.56), (-0.16, 0.06, 2.76), (-0.24, 0.18, 2.96), (-0.30, 0.30, 3.16)]
for k in range(len(c_pts_l) - 1):
    m_seg = m_lab_titanium if k % 2 == 0 else m_lab_steel
    b.seg(c_pts_l[k], c_pts_l[k+1], 0.052 - k * 0.012, 0.052 - (k + 1) * 0.012, m=m_seg, seg=14, smooth=True)
b.cyl(0.048, 0.030, loc=(-0.16, 0.06, 2.76), rot=(-20, 30, 0), m=m_lab_chrome)
b.cyl(0.032, 0.025, loc=(-0.24, 0.18, 2.96), rot=(-20, 30, 0), m=m_lab_chrome)
b.seg((-0.30, 0.30, 3.16), (-0.33, 0.36, 3.26), 0.014, 0.002, m=m_lab_chrome, seg=10, smooth=True)

# OJOS ROJOS AGÓNICOS (MIEDO Y PENA)
for side_eye, sign_eye in [("r", 1), ("l", -1)]:
    b.seg((sign_eye * 0.048, -0.16, 2.45), (sign_eye * 0.052, -0.20, 2.44), 0.028, 0.024, m=m_bone_dark, seg=10, smooth=True)
    b.seg((sign_eye * 0.048, -0.19, 2.45), (sign_eye * 0.050, -0.22, 2.44), 0.016, 0.013, m=m_eye_sorrow_red, seg=12, smooth=True)
    b.seg((sign_eye * 0.048, -0.21, 2.43), (sign_eye * 0.045, -0.22, 2.36), 0.007, 0.002, m=m_eye_tear_glow, seg=8, smooth=True)

# Mandíbula y dientes
b.prism(0.16, 0.14, 0.08, loc=(0, -0.15, 2.26), rot=(12, 0, 0), taper=0.6, m=m_bone_dark)
for x in [-0.045, -0.022, 0.0, 0.022, 0.045]:
    b.seg((x, -0.21, 2.32), (x, -0.21, 2.24), 0.008, 0.002, m=m_bone_ivory, seg=8, smooth=True)

# PECTORALES EN ROJO VIVO CON ESTRIACIONES DE TITÁN
b.bone("chest")
b.seg((0.07, -0.22, 1.88), (0.28, -0.21, 1.90), 0.095, 0.055, m=m_titan_accent, seg=16, smooth=True)
b.seg((-0.07, -0.22, 1.88), (-0.28, -0.21, 1.90), 0.095, 0.055, m=m_titan_accent, seg=16, smooth=True)

# Tira esternal y mutágeno púrpura
b.seg((0, -0.25, 1.68), (0, -0.27, 2.06), 0.018, 0.026, m=m_bone_ivory, seg=12, smooth=True)
b.cyl(0.040, 0.020, loc=(0, -0.28, 1.86), rot=(90, 0, 0), m=m_lab_titanium)
b.cyl(0.026, 0.028, loc=(0, -0.29, 1.86), rot=(90, 0, 0), m=m_purple_glow)

# ABDOMEN: PASTILLAS MUSCULARES EN ROJO VIVO
b.bone("spine")
for z_ab, rx_ab in [(1.26, 0.038), (1.40, 0.044), (1.54, 0.050)]:
    b.seg((0.04, -0.19, z_ab), (0.13, -0.17, z_ab), rx_ab, rx_ab * 0.70, m=m_titan_accent, seg=12, smooth=True)
    b.seg((-0.04, -0.19, z_ab), (-0.13, -0.17, z_ab), rx_ab, rx_ab * 0.70, m=m_titan_accent, seg=12, smooth=True)

# Espinas vertebrales
for z in [1.15, 1.30, 1.45, 1.60, 1.75, 1.90, 2.02]:
    b.box((0.10, 0.06, 0.04), loc=(0, 0.16, z), rot=(-2, 0, 0), m=m_lab_steel)

# Aguijón Dorsal
b.bone("tail_base")
b.seg((0.12, 0.18, 1.90), (0.18, 0.38, 2.28), 0.075, 0.055, m=m_bone_ivory, seg=14, smooth=True)

b.bone("tail_mid")
b.seg((0.18, 0.38, 2.28), (0.12, 0.48, 2.75), 0.055, 0.040, m=m_bone_dark, seg=14, smooth=True)
b.cyl(0.048, 0.16, loc=(0.15, 0.43, 2.52), rot=(-38, -8, 0), m=m_purple_glow)

b.bone("tail_scythe")
b.seg((0.12, 0.48, 2.75), (0.0, 0.22, 3.18), 0.048, 0.005, m=m_lab_titanium, seg=16, smooth=True)
b.seg((0.08, 0.36, 2.96), (0.02, 0.18, 3.18), 0.016, 0.002, m=m_cyan_glow, seg=10, smooth=True)

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
    bg.inputs["Color"].default_value = (0.04, 0.05, 0.07, 1.0)
    bg.inputs["Strength"].default_value = 0.5

cam_data = bpy.data.cameras.new("Cam_Boss5_Adjust")
cam_obj = bpy.data.objects.new("Cam_Boss5_Adjust", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_data.lens = 45.0

empty_target = bpy.data.objects.new("Cam_Boss5_Target", None)
scene.collection.objects.link(empty_target)
empty_target.location = (0.0, -0.10, 1.65)

tt = cam_obj.constraints.new(type='TRACK_TO')
tt.target = empty_target
tt.track_axis = 'TRACK_NEGATIVE_Z'
tt.up_axis = 'UP_Y'

dist = 4.4
cam_obj.location = (dist * 0.65, -dist * 0.85, 1.65 + dist * 0.30)

# Studio Lights
key_data = bpy.data.lights.new("Light_Key_B5", type='AREA')
key_obj = bpy.data.objects.new("Light_Key_B5", key_data)
scene.collection.objects.link(key_obj)
key_data.energy = 280.0
key_data.size = 3.0
key_data.color = (1.0, 0.98, 0.95)
key_obj.location = (dist * 0.8, -dist * 0.7, 1.65 + dist * 0.9)

fill_data = bpy.data.lights.new("Light_Fill_B5", type='AREA')
fill_obj = bpy.data.objects.new("Light_Fill_B5", fill_data)
scene.collection.objects.link(fill_obj)
fill_data.energy = 95.0
fill_data.size = 4.0
fill_data.color = (0.65, 0.75, 0.90)
fill_obj.location = (-dist * 0.8, -dist * 0.7, 1.65 + dist * 0.5)

rim_data = bpy.data.lights.new("Light_Rim_B5", type='AREA')
rim_obj = bpy.data.objects.new("Light_Rim_B5", rim_data)
scene.collection.objects.link(rim_obj)
rim_data.energy = 220.0
rim_data.size = 3.0
rim_data.color = (0.80, 0.75, 1.0)
rim_obj.location = (-dist * 0.3, dist * 0.9, 1.65 + dist * 0.7)

out_despues = os.path.join(output_dir, "boss5_despues.png")
scene.render.filepath = out_despues
bpy.ops.render.render(write_still=True)
print(f"RENDERED ANATOMICAL COLOSSAL TITAN BOSS 5 DESPUES -> {out_despues}")

blend_path = r"E:\Darx_Proyect\Saved\Player_Skin_Workspace\DarX_Boss5_Redesign.blend"
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f"FILE_SAVED: {blend_path}")

import bpy
import bmesh
import math
from mathutils import Matrix, Vector, Euler
import os

output_dir = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"
os.makedirs(output_dir, exist_ok=True)

# Clean scene
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.resolution_x = 960
scene.render.resolution_y = 960
scene.render.film_transparent = False

col = bpy.data.collections.new("DARX_FloraBoss_V2")
scene.collection.children.link(col)
R = math.radians

# --------------------------------------------------------------------------
# MATERIALS (BIO-HORROR SCI-FI: VEGETAL GREEN, BLACK CHITIN, ARTERIAL RED, ACID)
# --------------------------------------------------------------------------

def create_pbr_mat(name, rgb, rough=0.45, metal=0.0, emis_rgb=None, emis_str=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
        bsdf.inputs["Roughness"].default_value = rough
        bsdf.inputs["Metallic"].default_value = metal
        if emis_rgb:
            for em_col_name in ["Emission Color", "Emission"]:
                if em_col_name in bsdf.inputs:
                    bsdf.inputs[em_col_name].default_value = (*emis_rgb, 1.0)
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = emis_str
    return mat

m_bark = create_pbr_mat("M_Flora_Bark", (0.05, 0.13, 0.06), rough=0.80) # Mottled dark bark
m_green_jaw = create_pbr_mat("M_Flora_GreenJaw", (0.07, 0.20, 0.08), rough=0.40) # Living predatory plant flesh
m_black_chitin = create_pbr_mat("M_Flora_BlackChitin", (0.012, 0.014, 0.016), rough=0.25, metal=0.40) # Black razor chitin
m_blood_red = create_pbr_mat("M_Flora_BloodRed", (0.60, 0.003, 0.010), rough=0.25, metal=0.0) # Deep wet arterial blood red
m_tendon_flesh = create_pbr_mat("M_Flora_TendonFlesh", (0.45, 0.08, 0.08), rough=0.20, metal=0.0) # Stretchy jaw tendon cords

m_glow_acid = create_pbr_mat("M_Flora_AcidGlow", (0.12, 1.0, 0.18), rough=0.08, emis_rgb=(0.12, 1.0, 0.18), emis_str=26.0) # Toxic acid
m_glow_purp = create_pbr_mat("M_Flora_Biolum", (0.65, 0.0, 1.0), rough=0.10, emis_rgb=(0.65, 0.0, 1.0), emis_str=20.0)

m_teeth_black = create_pbr_mat("M_Flora_TeethBlack", (0.02, 0.02, 0.025), rough=0.15, metal=0.30)
m_teeth_ivory = create_pbr_mat("M_Flora_TeethIvory", (0.94, 0.92, 0.82), rough=0.12)

# Sci-Fi Lab Materials
m_host_suit = create_pbr_mat("M_Flora_HostSuit", (0.75, 0.78, 0.82), rough=0.45)
m_host_skin = create_pbr_mat("M_Flora_HostSkin", (0.80, 0.65, 0.60), rough=0.55)
m_lab_steel = create_pbr_mat("M_Lab_SteelPlates", (0.24, 0.26, 0.28), rough=0.35, metal=0.90)
m_lab_titanium = create_pbr_mat("M_Lab_TitaniumClamps", (0.55, 0.58, 0.62), rough=0.20, metal=0.95)
m_lab_glass = create_pbr_mat("M_Lab_VatGlass", (0.20, 0.40, 0.50), rough=0.08, metal=0.10)
m_warning_amber = create_pbr_mat("M_Lab_WarningAmber", (1.0, 0.55, 0.0), rough=0.10, emis_rgb=(1.0, 0.55, 0.0), emis_str=22.0)
m_cyan_glow = create_pbr_mat("M_Lab_CyanGlow", (0.0, 0.85, 1.0), rough=0.10, emis_rgb=(0.0, 0.85, 1.0), emis_str=18.0)

# --------------------------------------------------------------------------
# MESH & BUILDER HELPERS
# --------------------------------------------------------------------------

mesh = bpy.data.meshes.new("SK_Boss_Flora_V2_Mesh")
obj = bpy.data.objects.new("SK_Boss_Flora_V2", mesh)
col.objects.link(obj)

mat_list = [
    m_bark,          # 0
    m_green_jaw,     # 1
    m_black_chitin,  # 2
    m_blood_red,     # 3
    m_tendon_flesh,  # 4
    m_glow_acid,     # 5
    m_glow_purp,     # 6
    m_teeth_black,   # 7
    m_teeth_ivory,   # 8
    m_host_suit,     # 9
    m_host_skin,     # 10
    m_lab_steel,     # 11
    m_lab_titanium,  # 12
    m_lab_glass,     # 13
    m_warning_amber, # 14
    m_cyan_glow,     # 15
]
for m in mat_list:
    obj.data.materials.append(m)

bm = bmesh.new()

def tag(old_count, mat_idx, smooth=True):
    for f in bm.faces[old_count:]:
        f.material_index = mat_idx
        f.smooth = smooth

def add_box(size, loc, rot=(0,0,0), mat_idx=0):
    fc = len(bm.faces)
    mat = Matrix.Translation(loc) @ Euler(rot).to_matrix().to_4x4() @ Matrix.Diagonal((*size, 1.0))
    bmesh.ops.create_cube(bm, size=1.0, matrix=mat)
    tag(fc, mat_idx, smooth=False)

def add_cyl(r, depth, loc, rot=(0,0,0), seg=16, mat_idx=0, smooth=True):
    fc = len(bm.faces)
    mat = Matrix.Translation(loc) @ Euler(rot).to_matrix().to_4x4()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=depth, matrix=mat)
    tag(fc, mat_idx, smooth=smooth)

def add_frustum(r1, r2, depth, loc, rot=(0,0,0), seg=16, mat_idx=0, smooth=True):
    fc = len(bm.faces)
    mat = Matrix.Translation(loc) @ Euler(rot).to_matrix().to_4x4()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r1, radius2=r2, depth=depth, matrix=mat)
    tag(fc, mat_idx, smooth=smooth)

def add_seg(p0, p1, r0, r1, seg=12, mat_idx=0):
    fc = len(bm.faces)
    v0, v1 = Vector(p0), Vector(p1)
    diff = v1 - v0
    length = diff.length
    if length < 1e-6:
        return
    center = (v0 + v1) * 0.5
    rot = diff.to_track_quat('Z', 'Y').to_euler()
    mat = Matrix.Translation(center) @ rot.to_matrix().to_4x4()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r0, radius2=r1, depth=length, matrix=mat)
    tag(fc, mat_idx, smooth=True)

def _crear_anillo(center, rx, ry, n_pts=20, rot_euler=None):
    M = Matrix.Translation(Vector(center))
    if rot_euler:
        M = M @ Euler(rot_euler, 'XYZ').to_matrix().to_4x4()
    verts = []
    for i in range(n_pts):
        theta = 2.0 * math.pi * i / n_pts
        x = rx * math.cos(theta)
        y = ry * math.sin(theta)
        verts.append(bm.verts.new(M @ Vector((x, y, 0.0))))
    return verts

def _conectar_anillos(r1, r2, mat_idx=0):
    n = len(r1)
    for i in range(n):
        i_next = (i + 1) % n
        f = bm.faces.new([r1[i], r1[i_next], r2[i_next], r2[i]])
        f.material_index = mat_idx
        f.smooth = True

# ==========================================================================
# 1. CUBA HIDROPÓNICA Y BASE ORIGINAL DE BIOCONTENCIÓN
# ==========================================================================
add_cyl(0.52, 0.09, (0, 0, 0.12), seg=24, mat_idx=11) # m_lab_steel
add_frustum(0.50, 0.46, 0.14, (0, 0, 0.08), seg=24, mat_idx=11)

for a in range(8):
    ang = (a / 8.0) * 2 * math.pi
    add_cyl(0.016, 0.04, (math.cos(ang) * 0.52, math.sin(ang) * 0.52, 0.15), mat_idx=12)

for c_ang in [0.7, 2.3, 3.8, 5.4]:
    cx, cy = math.cos(c_ang) * 0.46, math.sin(c_ang) * 0.46
    add_cyl(0.04, 0.22, (cx, cy, 0.20), rot=(0, 0, c_ang), seg=12, mat_idx=13)
    add_cyl(0.032, 0.18, (cx, cy, 0.18), mat_idx=5)
    add_cyl(0.044, 0.03, (cx, cy, 0.30), mat_idx=12)

# Tronco Continuo de Raíces Trenzadas
anillos_tronco = [
    (0.20, 0.44, 0.40, 0.0, 0.0),
    (0.36, 0.38, 0.35, 0.0, 0.0),
    (0.52, 0.32, 0.30, 0.0, 0.02),
    (0.68, 0.28, 0.26, 0.0, 0.04),
    (0.85, 0.24, 0.22, 0.0, 0.05),
]
rings_tr = []
for z, rx, ry, cx, cy in anillos_tronco:
    rings_tr.append(_crear_anillo((cx, cy, z), rx, ry, n_pts=20))
for i in range(len(rings_tr) - 1):
    _conectar_anillos(rings_tr[i], rings_tr[i+1], mat_idx=0)

# Lianas y tendones negros con savia ácida
for k, l_ang in enumerate([0.3, 1.8, 3.4, 4.9]):
    p0 = (math.cos(l_ang) * 0.40, math.sin(l_ang) * 0.38, 0.22)
    p1 = (math.cos(l_ang + 0.4) * 0.30, math.sin(l_ang + 0.4) * 0.28, 0.54)
    p2 = (math.cos(l_ang + 0.8) * 0.22, math.sin(l_ang + 0.8) * 0.20, 0.85)
    add_seg(p0, p1, 0.032, 0.024, seg=10, mat_idx=2)
    add_seg(p1, p2, 0.024, 0.016, seg=8, mat_idx=5)
    add_seg(p1, (p1[0] * 1.15, p1[1] * 1.15, p1[2] + 0.04), 0.012, 0.002, seg=6, mat_idx=2)

# ==========================================================================
# 2. 4 PATAS DE RAÍZ ARTICULADAS (ORIGINAL)
# ==========================================================================
patas = [
    ((-0.35, -0.35, 0.35), (-0.75, -0.75, 0.0)),
    (( 0.35, -0.35, 0.35), ( 0.75, -0.75, 0.0)),
    ((-0.35,  0.35, 0.35), (-0.75,  0.75, 0.0)),
    (( 0.35,  0.35, 0.35), ( 0.75,  0.75, 0.0)),
]
for p_base, p_tip in patas:
    p_mid = ((p_base[0] + p_tip[0]) * 0.55, (p_base[1] + p_tip[1]) * 0.55, 0.28)
    add_seg(p_base, p_mid, 0.12, 0.09, seg=12, mat_idx=0)
    add_seg(p_mid, p_tip, 0.09, 0.04, seg=12, mat_idx=0)

    add_cyl(0.13, 0.04, loc=p_mid, rot=(R(20), R(20), 0), seg=16, mat_idx=12)
    add_box((0.025, 0.025, 0.025), loc=(p_mid[0] + 0.08, p_mid[1] + 0.08, p_mid[2] + 0.02), mat_idx=14)
    add_seg(p_tip, (p_tip[0] * 1.15, p_tip[1] * 1.15, 0.0), 0.035, 0.005, seg=8, mat_idx=2)

# ==========================================================================
# 3. 3 VAINAS DE ESPORAS BULBOSAS (ORIGINAL)
# ==========================================================================
bulbos = [
    ((-0.32, -0.22, 0.35), (-0.48, -0.32, 0.42)),
    (( 0.32, -0.22, 0.35), ( 0.48, -0.32, 0.42)),
    (( 0.0,   0.35, 0.38), ( 0.0,   0.52, 0.48)),
]
for p_in, p_out in bulbos:
    add_seg(p_in, p_out, 0.07, 0.12, seg=12, mat_idx=0)
    add_seg(p_out, (p_out[0] * 1.15, p_out[1] * 1.15, p_out[2] + 0.06), 0.12, 0.02, seg=12, mat_idx=6)
    add_cyl(0.09, 0.02, loc=p_in, rot=(R(20), R(20), 0), seg=12, mat_idx=12)

# ==========================================================================
# 4. HUÉSPED HUMANOIDE FUSIONADO (CON DETALLES DE BIO-ABSORCIÓN)
# ==========================================================================
add_seg((0, -0.16, 0.82), (0, -0.24, 1.18), 0.13, 0.11, seg=14, mat_idx=9)
add_seg((0, -0.24, 1.18), (0, -0.26, 1.34), 0.085, 0.075, seg=12, mat_idx=10)
add_box((0.11, 0.08, 0.07), loc=(0, -0.30, 1.32), rot=(-R(15), 0, 0), mat_idx=15)
add_box((0.13, 0.10, 0.08), loc=(0, -0.28, 1.32), rot=(-R(15), 0, 0), mat_idx=9)

add_seg((-0.14, -0.12, 0.85), (0.12, -0.24, 1.10), 0.028, 0.016, seg=8, mat_idx=2)
add_seg((0.14, -0.12, 0.85), (-0.12, -0.24, 1.10), 0.028, 0.016, seg=8, mat_idx=2)
add_seg((0.12, -0.22, 1.12), (0.18, -0.26, 1.16), 0.014, 0.002, seg=6, mat_idx=2)

# ==========================================================================
# 5. CUELLO CENTRAL Y COLLAR DE MONITOREO
# ==========================================================================
anillos_cuello_main = [
    (0.85, 0.22, 0.20, 0.0, 0.05, None),
    (1.05, 0.19, 0.18, 0.0, 0.02, (-R(5), 0, 0)),
    (1.25, 0.17, 0.16, 0.0, -0.02, (-R(10), 0, 0)),
    (1.48, 0.16, 0.15, 0.0, -0.04, (-R(12), 0, 0)),
    (1.70, 0.15, 0.14, 0.0, -0.05, (-R(15), 0, 0)),
]
rings_nm = []
for z, rx, ry, cx, cy, rot_e in anillos_cuello_main:
    rings_nm.append(_crear_anillo((cx, cy, z), rx, ry, n_pts=18, rot_euler=rot_e))
for i in range(len(rings_nm) - 1):
    _conectar_anillos(rings_nm[i], rings_nm[i+1], mat_idx=0)

add_cyl(0.18, 0.05, loc=(0, -0.04, 1.45), rot=(-R(12), 0, 0), seg=20, mat_idx=12)
add_box((0.03, 0.02, 0.02), loc=(0.14, -0.04, 1.45), mat_idx=14)
add_box((0.03, 0.02, 0.02), loc=(-0.14, -0.04, 1.45), mat_idx=14)

# ==========================================================================
# 6. REDISEÑO TRIPLE-A DE CABEZAS: BIO-HORROR PREDADOR CON TENDONES Y CIENCIA FICCIÓN
# ==========================================================================

# A. ARNÉS DE TITANIO DE BIOCONTENCIÓN EN LA NUCA (SCI-FI INTEGRATION)
# -------------------------------------------------------------------
# Abrazadera de titanio craneal rota con pernos y pistones de sujeción
add_cyl(0.20, 0.06, loc=(0, -0.22, 1.96), rot=(R(35), 0, 0), seg=20, mat_idx=12) # Titanio
add_box((0.04, 0.03, 0.03), loc=(0.17, -0.22, 1.96), mat_idx=14) # LED ámbar sobrecarga
add_box((0.04, 0.03, 0.03), loc=(-0.17, -0.22, 1.96), mat_idx=14)

# Pistón hidráulico de biocontención partido en la nuca
add_cyl(0.028, 0.14, loc=(0.12, -0.15, 1.88), rot=(-R(15), 0, 0), seg=12, mat_idx=12)
add_cyl(0.016, 0.10, loc=(0.12, -0.15, 1.82), rot=(-R(15), 0, 0), seg=10, mat_idx=11)

# B. CAPERUZA DE SÉPALOS ACORAZADOS (COBRA HOOD)
# -----------------------------------------------
frill_angles = [-0.65, -0.32, 0.0, 0.32, 0.65]
for idx, f_ang in enumerate(frill_angles):
    fx = math.sin(f_ang) * 0.30
    fy = -0.18 + math.cos(f_ang) * 0.12
    fz = 1.98 + abs(f_ang) * 0.10
    fc = len(bm.faces)
    rot_sepal = Euler((-R(22), R(f_ang * 45), R(f_ang * 30)), 'XYZ')
    mat_sepal = Matrix.Translation((fx, fy, fz)) @ rot_sepal.to_matrix().to_4x4() @ Matrix.Diagonal((0.09, 0.20, 0.025, 1.0))
    bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=1.0, matrix=mat_sepal)
    tag(fc, 1, smooth=True)
    # Espolón negro que remata cada sépalo
    add_seg((fx, fy, fz), (fx * 1.35, fy + 0.08, fz + 0.16), 0.016, 0.002, seg=6, mat_idx=2)

# C. CABEZA PRINCIPAL: MANDÍBULA SUPERIOR PREDADORA ACORAZADA
# -----------------------------------------------------------
# Caparazón superior con volumen aovado estilizado (VERDE)
fc = len(bm.faces)
mat_jaw_up_green = Matrix.Translation((0.0, -0.60, 2.10)) @ Matrix.Rotation(-R(22), 4, 'X') @ Matrix.Diagonal((0.26, 0.48, 0.15, 1.0))
bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=16, radius=1.0, matrix=mat_jaw_up_green)
tag(fc, 1, smooth=True)

# Cresta sagital blindada negra
fc = len(bm.faces)
mat_jaw_up_black = Matrix.Translation((0.0, -0.58, 2.17)) @ Matrix.Rotation(-R(22), 4, 'X') @ Matrix.Diagonal((0.27, 0.49, 0.06, 1.0))
bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=16, radius=1.0, matrix=mat_jaw_up_black)
tag(fc, 2, smooth=True)

# Corona de 7 espolones dorsales curvados hacia atrás con puntas carmesí
for sp_i, (sp_y, sp_z, sp_len) in enumerate([
    (-0.25, 2.02, 0.09), (-0.38, 2.14, 0.13), (-0.52, 2.24, 0.16),
    (-0.66, 2.32, 0.18), (-0.80, 2.36, 0.16), (-0.92, 2.32, 0.12), (-1.02, 2.24, 0.08)
]):
    add_seg((0, sp_y, sp_z), (0, sp_y + 0.04, sp_z + sp_len), 0.020, 0.003, seg=8, mat_idx=2)
    if sp_i in [2, 3, 4]:
        add_seg((0, sp_y + 0.03, sp_z + sp_len * 0.65), (0, sp_y + 0.04, sp_z + sp_len), 0.010, 0.001, seg=6, mat_idx=3)

# Pico ganchudo superior en garra rapaz negra
fc = len(bm.faces)
mat_beak_up = Matrix.Translation((0.0, -0.96, 2.12)) @ Matrix.Rotation(R(135), 4, 'X')
bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=0.045, radius2=0.004, depth=0.18, matrix=mat_beak_up)
tag(fc, 2, smooth=True)

# FOSAS SENSORIALES BIOLUMINISCENTES (Ojos de víbora vegetal a los costados)
for side_eye in [-1.0, 1.0]:
    fc = len(bm.faces)
    rot_eye = Euler((-R(22), R(side_eye * 35), R(side_eye * 20)), 'XYZ')
    mat_eye = Matrix.Translation((side_eye * 0.19, -0.66, 2.18)) @ rot_eye.to_matrix().to_4x4() @ Matrix.Diagonal((0.028, 0.09, 0.020, 1.0))
    bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=1.0, matrix=mat_eye)
    tag(fc, 5, smooth=True) # Ácido fosforescente

# Paladar interior: ROJO SANGRE PROFUNDO
fc = len(bm.faces)
mat_palate_red = Matrix.Translation((0.0, -0.58, 2.03)) @ Matrix.Rotation(-R(22), 4, 'X') @ Matrix.Diagonal((0.21, 0.42, 0.06, 1.0))
bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=12, radius=1.0, matrix=mat_palate_red)
tag(fc, 3, smooth=True)

# D. CABEZA PRINCIPAL: MANDÍBULA INFERIOR CON PICO RAPAZ Y LENGUA DE ARPÓN
# ------------------------------------------------------------------------
# Mandíbula inferior (VERDE)
fc = len(bm.faces)
mat_jaw_low_green = Matrix.Translation((0.0, -0.56, 1.60)) @ Matrix.Rotation(R(30), 4, 'X') @ Matrix.Diagonal((0.23, 0.46, 0.14, 1.0))
bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=16, radius=1.0, matrix=mat_jaw_low_green)
tag(fc, 1, smooth=True)

# Cresta ventral negra
fc = len(bm.faces)
mat_jaw_low_black = Matrix.Translation((0.0, -0.52, 1.53)) @ Matrix.Rotation(R(30), 4, 'X') @ Matrix.Diagonal((0.24, 0.47, 0.06, 1.0))
bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=16, radius=1.0, matrix=mat_jaw_low_black)
tag(fc, 2, smooth=True)

# Pico ganchudo inferior negro
fc = len(bm.faces)
mat_beak_low = Matrix.Translation((0.0, -0.92, 1.44)) @ Matrix.Rotation(-R(35), 4, 'X')
bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=0.040, radius2=0.004, depth=0.16, matrix=mat_beak_low)
tag(fc, 2, smooth=True)

# Cavidad oral inferior y lengua de arpón: ROJO SANGRE
fc = len(bm.faces)
mat_tongue_red = Matrix.Translation((0.0, -0.54, 1.66)) @ Matrix.Rotation(R(30), 4, 'X') @ Matrix.Diagonal((0.19, 0.40, 0.06, 1.0))
bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=12, radius=1.0, matrix=mat_tongue_red)
tag(fc, 3, smooth=True)

# Lengua predadora extendida con 4 bulbos arponados
for tg_i, (tg_y, tg_z) in enumerate([(-0.35, 1.73), (-0.48, 1.76), (-0.62, 1.78), (-0.76, 1.76)]):
    fc = len(bm.faces)
    bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=0.040 - tg_i * 0.004, matrix=Matrix.Translation((0, tg_y, tg_z)))
    tag(fc, 3, smooth=True)
    add_seg((0, tg_y, tg_z + 0.02), (0, tg_y - 0.06, tg_z + 0.07), 0.011, 0.001, seg=6, mat_idx=2)

# Inyector de titanio y glándula gástrica ácida profunda
add_cyl(0.045, 0.16, loc=(0, -0.16, 1.82), rot=(R(78), 0, 0), seg=16, mat_idx=12)
add_cyl(0.032, 0.14, loc=(0, -0.22, 1.82), rot=(R(78), 0, 0), seg=12, mat_idx=5)

# E. TENDONES CARNOSOS Y CORDONES DE MUCOSA (LATERAL JAW WEBS)
# ------------------------------------------------------------
# Conectan el fondo de la mandíbula superior e inferior a los costados
for side_w, sign_w in [("l", -1.0), ("r", 1.0)]:
    # 3 cordones de tendón tenso estirándose entre las comisuras de la boca
    add_seg((sign_w * 0.19, -0.32, 1.98), (sign_w * 0.17, -0.34, 1.66), 0.016, 0.014, seg=8, mat_idx=4) # m_tendon_flesh
    add_seg((sign_w * 0.21, -0.42, 1.94), (sign_w * 0.19, -0.44, 1.68), 0.014, 0.012, seg=8, mat_idx=4)
    add_seg((sign_w * 0.22, -0.52, 1.90), (sign_w * 0.20, -0.54, 1.72), 0.012, 0.010, seg=8, mat_idx=4)
    # Filamento de savia ácida goteando entre las mandíbulas
    add_seg((sign_w * 0.20, -0.44, 1.84), (sign_w * 0.20, -0.44, 1.70), 0.006, 0.002, seg=6, mat_idx=5)

# F. DIENTES TRIPLE-A: CILIOS EXTERIORES + SABLES INTERIORES
# -----------------------------------------------------------
# Mandíbula Superior: 16 colmillos en doble hilera
for step in range(16):
    t = step / 15.0
    t_ang = -math.pi * 0.44 + t * math.pi * 0.88
    tx = 0.22 * math.sin(t_ang)
    ty = -0.42 - 0.46 * math.cos(t_ang)
    tz = 2.00 - 0.15 * math.cos(t_ang)
    
    # Cilio exterior negro
    cilia_rot = Euler((R(150), R(-t_ang * 25), R(tx * 25)), 'XYZ')
    mat_cilia = Matrix.Translation((tx * 1.12, ty, tz + 0.02)) @ cilia_rot.to_matrix().to_4x4()
    fc = len(bm.faces)
    bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=0.013, radius2=0.001, depth=0.11, matrix=mat_cilia)
    tag(fc, 2, smooth=True)
    
    # Sable interior (curvado hacia adentro)
    fang_len = 0.18 if (3 <= step <= 12) else 0.09
    rot_fang = Euler((R(165), R(-t_ang * 30), R(tx * 35)), 'XYZ')
    mat_fang = Matrix.Translation((tx, ty, tz)) @ rot_fang.to_matrix().to_4x4()
    fc = len(bm.faces)
    bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=0.017, radius2=0.002, depth=fang_len, matrix=mat_fang)
    tag(fc, 8 if step % 2 == 0 else 7, smooth=True)

# Mandíbula Inferior: 14 colmillos intercalados hacia arriba
for step in range(14):
    t = step / 13.0
    t_ang = -math.pi * 0.42 + t * math.pi * 0.84
    tx = 0.20 * math.sin(t_ang)
    ty = -0.42 - 0.44 * math.cos(t_ang)
    tz = 1.68 + 0.12 * math.cos(t_ang)
    
    # Cilio exterior
    cilia_rot = Euler((R(30), R(-t_ang * 25), R(-tx * 25)), 'XYZ')
    mat_cilia = Matrix.Translation((tx * 1.12, ty, tz - 0.02)) @ cilia_rot.to_matrix().to_4x4()
    fc = len(bm.faces)
    bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=0.012, radius2=0.001, depth=0.10, matrix=mat_cilia)
    tag(fc, 2, smooth=True)
    
    # Colmillo interior
    fang_len = 0.15 if (2 <= step <= 11) else 0.08
    rot_fang = Euler((R(20), R(-t_ang * 30), R(-tx * 35)), 'XYZ')
    mat_fang = Matrix.Translation((tx, ty, tz)) @ rot_fang.to_matrix().to_4x4()
    fc = len(bm.faces)
    bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=0.016, radius2=0.002, depth=fang_len, matrix=mat_fang)
    tag(fc, 8 if step % 2 == 0 else 7, smooth=True)

# G. 2 CABEZAS LATERALES SERPENTINAS HIDRA DE ALTO DETALLE
# ---------------------------------------------------------
for side, sign in [("left", -1), ("right", 1)]:
    # Cuello en S-curve orgánica con anillos de espinas
    p0 = (sign * 0.28, 0.0, 0.80)
    p1 = (sign * 0.54, -0.12, 1.15)
    p2 = (sign * 0.74, -0.28, 1.48)
    p3 = (sign * 0.92, -0.46, 1.72)
    add_seg(p0, p1, 0.09, 0.075, seg=12, mat_idx=0)
    add_seg(p1, p2, 0.075, 0.060, seg=12, mat_idx=0)
    add_seg(p2, p3, 0.060, 0.045, seg=12, mat_idx=0)

    for ring_z in [1.15, 1.42]:
        add_cyl(0.08, 0.02, (sign * 0.54 * (ring_z/1.15), -0.20, ring_z), rot=(R(20), 0, R(sign * 30)), seg=12, mat_idx=2)

    hx = sign * 0.98
    hy = -0.54
    hz = 1.78
    
    # Caperuza acorazada de víbora con espinas
    fc = len(bm.faces)
    mat_v_hood = Matrix.Translation((hx - sign * 0.06, hy + 0.08, hz)) @ Euler((0, 0, R(sign * 35))).to_matrix().to_4x4() @ Matrix.Diagonal((0.15, 0.06, 0.13, 1.0))
    bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=1.0, matrix=mat_v_hood)
    tag(fc, 1, smooth=True)
    # Espinas de la caperuza lateral
    add_seg((hx - sign * 0.06, hy + 0.08, hz + 0.08), (hx - sign * 0.10, hy + 0.14, hz + 0.18), 0.014, 0.002, seg=6, mat_idx=2)
    
    # Cráneo viperino afilado (VERDE)
    fc = len(bm.faces)
    mat_s_up = Matrix.Translation((hx, hy, hz + 0.04)) @ Matrix.Rotation(-R(22), 4, 'X') @ Matrix.Rotation(R(32 * sign), 4, 'Z') @ Matrix.Diagonal((0.11, 0.25, 0.07, 1.0))
    bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=12, radius=1.0, matrix=mat_s_up)
    tag(fc, 1, smooth=True)

    # Pico negro viperino
    add_seg((hx, hy - 0.14, hz + 0.02), (hx + sign * 0.02, hy - 0.22, hz + 0.01), 0.026, 0.002, seg=6, mat_idx=2)

    # Ojos sensoriales ácidos en la víbora lateral
    for v_eye_side in [-0.06, 0.06]:
        fc = len(bm.faces)
        bmesh.ops.create_uvsphere(bm, u_segments=8, v_segments=6, radius=0.018,
                                  matrix=Matrix.Translation((hx + v_eye_side, hy - 0.04, hz + 0.07)))
        tag(fc, 5, smooth=True)

    # Mandíbula inferior serpentina
    fc = len(bm.faces)
    mat_s_low = Matrix.Translation((hx, hy, hz - 0.06)) @ Matrix.Rotation(R(32), 4, 'X') @ Matrix.Rotation(R(32 * sign), 4, 'Z') @ Matrix.Diagonal((0.09, 0.23, 0.06, 1.0))
    bmesh.ops.create_uvsphere(bm, u_segments=16, v_segments=12, radius=1.0, matrix=mat_s_low)
    tag(fc, 1, smooth=True)

    # Interior boca víbora: ROJO SANGRE PROFUNDO
    fc = len(bm.faces)
    mat_s_red = Matrix.Translation((hx, hy - 0.02, hz)) @ Matrix.Diagonal((0.07, 0.16, 0.04, 1.0))
    bmesh.ops.create_uvsphere(bm, u_segments=12, v_segments=8, radius=1.0, matrix=mat_s_red)
    tag(fc, 3, smooth=True)

    # Glándula de veneno ácido
    fc = len(bm.faces)
    bmesh.ops.create_uvsphere(bm, u_segments=10, v_segments=8, radius=0.040,
                              matrix=Matrix.Translation((hx, hy + 0.04, hz)))
    tag(fc, 5, smooth=True)

    # Tendones de la comisura en la cabeza lateral
    add_seg((hx + sign * 0.06, hy - 0.02, hz + 0.03), (hx + sign * 0.05, hy - 0.03, hz - 0.05), 0.009, 0.007, seg=6, mat_idx=4)

    # 4 Colmillos de víbora curvados
    for f_x, f_y, f_len in [(-0.04, -0.06, 0.10), (0.04, -0.06, 0.10), (-0.02, -0.15, 0.12), (0.02, -0.15, 0.12)]:
        fc = len(bm.faces)
        mat_f_viper = Matrix.Translation((hx + f_x * sign, hy + f_y, hz + 0.02)) @ Matrix.Rotation(R(155), 4, 'X')
        bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=0.012, radius2=0.001, depth=f_len, matrix=mat_f_viper)
        tag(fc, 7 if abs(f_y) > 0.10 else 8, smooth=True)

bm.to_mesh(mesh)
bm.free()
mesh.update()

# --------------------------------------------------------------------------
# LIGHTING & CAMERA
# --------------------------------------------------------------------------

if scene.world is None:
    scene.world = bpy.data.worlds.new("World_Studio")
scene.world.use_nodes = True
bg = scene.world.node_tree.nodes.get("Background")
if bg:
    bg.inputs["Color"].default_value = (0.08, 0.09, 0.12, 1.0)
    bg.inputs["Strength"].default_value = 0.8

cam_data = bpy.data.cameras.new("Cam_Boss4_V2")
cam_obj = bpy.data.objects.new("Cam_Boss4_V2", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_data.lens = 45.0

empty_target = bpy.data.objects.new("Cam_Boss4_Target", None)
scene.collection.objects.link(empty_target)
empty_target.location = (0.0, -0.15, 1.15)

tt = cam_obj.constraints.new(type='TRACK_TO')
tt.target = empty_target
tt.track_axis = 'TRACK_NEGATIVE_Z'
tt.up_axis = 'UP_Y'

dist = 3.6
cam_obj.location = (dist * 0.65, -0.15 - dist * 0.85, 1.15 + dist * 0.30)

key_data = bpy.data.lights.new("Light_Key_B4", type='AREA')
key_obj = bpy.data.objects.new("Light_Key_B4", key_data)
scene.collection.objects.link(key_obj)
key_data.energy = 250.0
key_data.size = 3.5
key_data.color = (1.0, 0.98, 0.94)
key_obj.location = (2.6, -2.6, 3.6)

fill_data = bpy.data.lights.new("Light_Fill_B4", type='AREA')
fill_obj = bpy.data.objects.new("Light_Fill_B4", fill_data)
scene.collection.objects.link(fill_obj)
fill_data.energy = 90.0
fill_data.size = 4.0
fill_data.color = (0.1, 0.9, 0.25)
fill_obj.location = (-2.6, -2.6, 2.2)

rim_data = bpy.data.lights.new("Light_Rim_B4", type='AREA')
rim_obj = bpy.data.objects.new("Light_Rim_B4", rim_data)
scene.collection.objects.link(rim_obj)
rim_data.energy = 210.0
rim_data.size = 3.0
rim_data.color = (1.0, 0.02, 0.02)
rim_obj.location = (-0.5, 3.2, 2.8)

out_despues = os.path.join(output_dir, "boss4_despues.png")
scene.render.filepath = out_despues
bpy.ops.render.render(write_still=True)
print(f"RENDERED REFINED BOSS 4 DESPUES -> {out_despues}")

blend_path = r"E:\Darx_Proyect\Saved\Player_Skin_Workspace\DarX_Boss4_Redesign.blend"
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f"FILE_SAVED: {blend_path}")

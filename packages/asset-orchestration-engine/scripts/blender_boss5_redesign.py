import bpy, bmesh, math, os, sys
from mathutils import Vector, Matrix, Euler

art_blender_dir = r"E:\Darx_Proyect\Art\Blender"
if art_blender_dir not in sys.path:
    sys.path.append(art_blender_dir)

import darx_lib as dl

output_dir = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"
os.makedirs(output_dir, exist_ok=True)

COL_NAME = "DARX_AmalgamBoss_Polished"
SK_NAME = "SK_Boss_Amalgam_Polished"
R = math.radians

# Clean
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.resolution_x = 960
scene.render.resolution_y = 960
scene.render.film_transparent = False

col = dl.coll(COL_NAME)

# --------------------------------------------------------------------------
# 1. MATERIALES EXACTOS DEL ORIGINAL
# --------------------------------------------------------------------------
m_flesh_dark = dl.mat("M_Titan_FleshDark", (0.34, 0.08, 0.06), rough=0.45)
m_flesh_fibers = dl.mat("M_Titan_MuscleFibers", (0.46, 0.12, 0.09), rough=0.40)
m_flesh_highlight = dl.mat("M_Titan_FleshHighlight", (0.58, 0.18, 0.13), rough=0.35)

m_bone_dark = dl.mat("M_Amalgam_BoneDark", (0.28, 0.26, 0.24), rough=0.35, metal=0.10)
m_bone_ivory = dl.mat("M_Amalgam_BoneIvory", (0.88, 0.85, 0.74), rough=0.20, metal=0.05)
m_claws_black = dl.mat("M_Amalgam_ClawsBlack", (0.015, 0.015, 0.02), rough=0.15, metal=0.50)

m_lab_titanium = dl.mat("M_Lab_Titanium", (0.58, 0.60, 0.64), rough=0.22, metal=0.92)
m_lab_steel = dl.mat("M_Lab_Steel", (0.20, 0.22, 0.26), rough=0.30, metal=0.88)

m_cyan_glow = dl.mat("M_Lab_CyanGlow", (0.0, 0.90, 1.0), emis=(0.0, 0.90, 1.0), emis_str=28.0)
m_warning_red = dl.mat("M_Lab_WarningRed", (1.0, 0.02, 0.02), emis=(1.0, 0.02, 0.02), emis_str=26.0)
m_purple_glow = dl.mat("M_Amalgam_PurpleGlow", (0.85, 0.0, 1.0), emis=(0.85, 0.0, 1.0), emis_str=28.0)

b = dl.MB(SK_NAME)
bm = b.bm
idx_flesh = b.midx(m_flesh_fibers)
idx_flesh_hi = b.midx(m_flesh_highlight)

# --------------------------------------------------------------------------
# 2. TORSO CONTINUO Y COHESIVO CON PECTORALES Y ABDOMEN CHISELADO
# --------------------------------------------------------------------------
def crear_anillo_torso(center, rx, ry, n_pts=32, pec=0.0, abs_m=0.0, lat=0.0):
    verts = []
    for i in range(n_pts):
        theta = 2.0 * math.pi * i / n_pts
        xn = math.cos(theta)
        yn = math.sin(theta)
        cur_rx = rx
        cur_ry = ry
        if pec > 0.0 and yn < 0:
            p_val = math.exp(-((xn - 0.40)**2) / 0.06) + math.exp(-((xn + 0.40)**2) / 0.06)
            cur_ry += pec * p_val
        if abs_m > 0.0 and yn < 0:
            a_val = math.exp(-((xn - 0.28)**2) / 0.04) + math.exp(-((xn + 0.28)**2) / 0.04)
            if abs(xn) < 0.09:
                a_val -= 0.65
            cur_ry += abs_m * a_val
        if lat > 0.0 and yn > 0:
            cur_rx += lat * abs(xn)
        vx = center[0] + cur_rx * xn
        vy = center[1] + cur_ry * yn
        vz = center[2]
        verts.append(bm.verts.new((vx, vy, vz)))
    return verts

torso_levels = [
    (0.96, 0.28, 0.19, 0.0,  0.00, 0.00, 0.00, 0.00), # Pelvis baja
    (1.10, 0.31, 0.21, 0.0, -0.01, 0.00, 0.00, 0.00), # Caderas
    (1.26, 0.26, 0.18, 0.0, -0.02, 0.00, 0.11, 0.00), # Cintura
    (1.42, 0.30, 0.21, 0.0, -0.03, 0.00, 0.14, 0.04), # Abdomen medio
    (1.58, 0.36, 0.24, 0.0, -0.04, 0.03, 0.14, 0.08), # Abdomen alto
    (1.74, 0.44, 0.27, 0.0, -0.04, 0.18, 0.05, 0.10), # Pectorales base
    (1.92, 0.48, 0.29, 0.0, -0.03, 0.22, 0.00, 0.10), # Pectorales pico / Lats
    (2.08, 0.41, 0.24, 0.0, -0.02, 0.10, 0.00, 0.04), # Clavículas
    (2.20, 0.22, 0.17, 0.0, -0.01, 0.00, 0.00, 0.00), # Cuello
]

rings = [crear_anillo_torso((lvl[3], lvl[4], lvl[0]), lvl[1], lvl[2], pec=lvl[5], abs_m=lvl[6], lat=lvl[7]) for lvl in torso_levels]
for i in range(len(rings) - 1):
    r1, r2 = rings[i], rings[i+1]
    n = len(r1)
    for j in range(n):
        j_next = (j + 1) % n
        v_mid = (r1[j].co + r2[j].co) * 0.5
        is_highlight = (v_mid.y < -0.14 and (i in [4, 5, 6]))
        m_idx = idx_flesh_hi if is_highlight else idx_flesh
        f = bm.faces.new([r1[j], r1[j_next], r2[j_next], r2[j]])
        f.material_index = m_idx
        f.smooth = True

# Tira Esternal de Titanio y Mutágeno Púrpura (Diseño Original)
b.seg((0, -0.29, 1.70), (0, -0.35, 2.06), 0.022, 0.028, m=m_lab_titanium, seg=12, smooth=True)
b.cyl(0.045, 0.025, loc=(0, -0.35, 1.88), rot=(90, 0, 0), seg=16, m=m_lab_titanium)
b.cyl(0.032, 0.030, loc=(0, -0.36, 1.88), rot=(90, 0, 0), seg=14, m=m_purple_glow)

# 6 Abdominales orgánicos sutilmente realzados (sin ser pastillas toscas)
for z_ab in [1.32, 1.46, 1.60]:
    b.seg((0.04, -0.24, z_ab), (0.13, -0.22, z_ab), 0.042, 0.035, m=m_flesh_highlight, seg=10, smooth=True)
    b.seg((-0.04, -0.24, z_ab), (-0.13, -0.22, z_ab), 0.042, 0.035, m=m_flesh_highlight, seg=10, smooth=True)

# Crestas vertebrales dorsales
for idx, sz in enumerate([1.16, 1.30, 1.45, 1.60, 1.75, 1.90, 2.05]):
    b.seg((0, 0.19 + idx * 0.01, sz), (0, 0.31 + idx * 0.015, sz + 0.02), 0.026, 0.005, m=m_bone_dark, seg=8, smooth=True)

# --------------------------------------------------------------------------
# 3. PIERNAS DE PILAR
# --------------------------------------------------------------------------
for side, sign in [("r", 1), ("l", -1)]:
    p_hip = (sign * 0.24, 0.0, 1.05)
    p_knee = (sign * 0.27, 0.04, 0.55)
    p_ankle = (sign * 0.28, -0.04, 0.14)

    # Muslo
    b.seg(p_hip, p_knee, 0.17, 0.14, m=m_flesh_fibers, seg=16, smooth=True)

    # Rodillera concéntrica envolvente (Titanio y hueso)
    b.cyl(0.08, 0.06, loc=(sign * 0.27, -0.07, 0.55), rot=(18, sign * 6, 0), seg=16, m=m_lab_titanium)
    b.seg((sign * 0.27, -0.07, 0.55), (sign * 0.29, -0.16, 0.52), 0.035, 0.006, m=m_bone_dark, seg=8, smooth=True)

    # Pantorrilla
    b.seg(p_knee, p_ankle, 0.14, 0.11, m=m_flesh_fibers, seg=16, smooth=True)

    # Grillete de titanio en tobillo
    b.cyl(0.12, 0.04, loc=(sign * 0.28, -0.04, 0.18), seg=16, m=m_lab_titanium)

    # Pie ensanchado de apoyo sísmico
    b.seg(p_ankle, (sign * 0.28, -0.20, 0.04), 0.12, 0.09, m=m_bone_dark, seg=14, smooth=True)
    for gx in [-0.06, 0.0, 0.06]:
        g_base = (sign * 0.28 + gx, -0.24, 0.04)
        g_tip = (sign * 0.28 + gx * 1.15, -0.38, 0.0)
        b.seg(g_base, g_tip, 0.020, 0.003, m=m_claws_black, seg=8, smooth=True)

# --------------------------------------------------------------------------
# 4. BRAZO DERECHO (IZQUIERDA DE LA IMAGEN): BONE-GREY CHITIN CON 3 ESPINAS
# --------------------------------------------------------------------------
p_sh_spiked = (-0.46, -0.02, 2.04)
p_elb_spiked = (-0.76, -0.08, 1.66)
p_wri_spiked = (-1.04, -0.16, 1.26)
p_hand_spiked = (-1.22, -0.22, 0.98)

# Clavícula y hombro en hueso/quitina gris
b.seg((-0.20, 0.0, 2.06), p_sh_spiked, 0.16, 0.15, m=m_bone_dark, seg=16, smooth=True)
b.seg(p_sh_spiked, p_elb_spiked, 0.17, 0.14, m=m_bone_dark, seg=18, smooth=True)
b.cyl(0.18, 0.045, loc=(-0.61, -0.05, 1.85), rot=(20, -40, 0), seg=16, m=m_lab_titanium)

# 2 Espinas deltoides del diseño original
b.seg((-0.52, -0.04, 2.14), (-0.72, -0.08, 2.26), 0.026, 0.003, m=m_bone_ivory, seg=8, smooth=True)
b.seg((-0.46, 0.06, 2.10), (-0.62, 0.14, 2.22), 0.024, 0.003, m=m_bone_ivory, seg=8, smooth=True)

# Antebrazo con 3 ESPINAS LATERALES PROMINENTES (Del diseño original)
b.seg(p_elb_spiked, p_wri_spiked, 0.15, 0.12, m=m_bone_dark, seg=18, smooth=True)

for sp_i, (sx, sy, sz, s_len) in enumerate([
    (-0.80, -0.10, 1.60, 0.30),
    (-0.90, -0.13, 1.46, 0.34),
    (-0.98, -0.15, 1.32, 0.28),
]):
    p_base = (sx, sy, sz)
    p_tip = (sx - s_len * 0.85, sy - 0.08, sz + 0.06)
    b.seg(p_base, p_tip, 0.030, 0.003, m=m_bone_ivory, seg=8, smooth=True)
    b.cyl(0.036, 0.02, loc=p_base, seg=8, m=m_lab_titanium)

# Mano y garras
b.seg(p_wri_spiked, p_hand_spiked, 0.11, 0.07, m=m_bone_dark, seg=14, smooth=True)
for g_i, gy_off in enumerate([-0.04, -0.015, 0.015, 0.04]):
    g_start = (-1.22 + gy_off, -0.22, 0.98)
    g_end = (-1.22 + gy_off * 1.2 - 0.08, -0.34, 0.78)
    b.seg(g_start, g_end, 0.018, 0.002, m=m_claws_black, seg=8, smooth=True)

# --------------------------------------------------------------------------
# 5. BRAZO IZQUIERDO (DERECHA DE LA IMAGEN): HOMBRERA TITANIO + BÍCEPS ROJO + GARRAS AGUJA
# --------------------------------------------------------------------------
p_sh_needle = (0.46, -0.02, 2.04)
p_elb_needle = (0.74, -0.08, 1.66)
p_wri_needle = (1.02, -0.16, 1.26)
p_hand_needle = (1.20, -0.22, 0.96)

# Clavícula roja
b.seg((0.20, 0.0, 2.06), p_sh_needle, 0.16, 0.14, m=m_flesh_fibers, seg=16, smooth=True)

# Hombrera Angular de Titanio
b.box((0.26, 0.22, 0.14), loc=(0.50, -0.03, 2.10), rot=(15, 35, -12), m=m_lab_titanium)

# Bíceps rojo
b.seg(p_sh_needle, p_elb_needle, 0.15, 0.13, m=m_flesh_fibers, seg=18, smooth=True)

# Antebrazo gris oscuro (Bone Chitin)
b.seg(p_elb_needle, p_wri_needle, 0.14, 0.11, m=m_bone_dark, seg=16, smooth=True)
# Bracer de titanio
b.seg((0.84, -0.14, 1.54), (0.98, -0.18, 1.34), 0.035, 0.022, m=m_lab_titanium, seg=8, smooth=True)

# Palma y LARGAS GARRAS DE AGUJA (Needle Claws)
b.seg(p_wri_needle, p_hand_needle, 0.10, 0.07, m=m_bone_dark, seg=14, smooth=True)
for n_i, ny_off in enumerate([-0.05, -0.015, 0.015, 0.05]):
    n_start = (1.20 + ny_off, -0.22, 0.96)
    n_end = (1.20 + ny_off * 1.3 + 0.06, -0.36, 0.68)
    b.seg(n_start, n_end, 0.016, 0.002, m=m_claws_black, seg=8, smooth=True)

# --------------------------------------------------------------------------
# 6. AGUIJÓN DORSAL CON NODO PÚRPURA Y HOJA CIAN
# --------------------------------------------------------------------------
tail_pts = [
    ((-0.10, 0.20, 1.94), (-0.16, 0.38, 2.28), 0.09, 0.075),
    ((-0.16, 0.38, 2.28), (-0.12, 0.50, 2.70), 0.075, 0.055),
    ((-0.12, 0.50, 2.70), (-0.02, 0.36, 3.02), 0.055, 0.040),
    ((-0.02, 0.36, 3.02), ( 0.05, 0.18, 3.22), 0.040, 0.022),
]
for p1, p2, r1, r2 in tail_pts:
    b.seg(p1, p2, r1, r2, m=m_bone_dark, seg=12, smooth=True)
    b.cyl(r1 * 1.15, 0.025, loc=p1, seg=12, m=m_lab_titanium)

# Nodo de energía púrpura
b.cyl(0.055, 0.18, loc=(-0.14, 0.44, 2.48), rot=(-35, 8, 0), seg=14, m=m_purple_glow)

# Hoja de guadaña con filo cian
b.seg((0.05, 0.18, 3.22), (0.10, -0.10, 3.38), 0.050, 0.006, m=m_lab_titanium, seg=12, smooth=True)
b.seg((0.07, 0.08, 3.26), (0.12, -0.16, 3.42), 0.016, 0.002, m=m_cyan_glow, seg=8, smooth=True)

# --------------------------------------------------------------------------
# 7. CABEZA DEMONÍACA: OJOS CIAN Y ROJO CLARAMENTE VISIBLES
# --------------------------------------------------------------------------
# Cuello
b.seg((0, -0.02, 2.18), (0, -0.05, 2.38), 0.15, 0.12, m=m_flesh_fibers, seg=16, smooth=True)

# Bóveda craneal
b.sph(0.16, loc=(0.0, -0.06, 2.52), scale=(1.0, 1.15, 0.95), m=m_flesh_fibers)

# Cuernos altos del original
for sign in [-1, 1]:
    h_segs = [
        ((sign * 0.09, -0.04, 2.62), (sign * 0.18, 0.06, 2.86), 0.050, 0.035),
        ((sign * 0.18, 0.06, 2.86),  (sign * 0.25, 0.20, 3.12), 0.035, 0.018),
        ((sign * 0.25, 0.20, 3.12),  (sign * 0.30, 0.34, 3.32), 0.018, 0.004),
    ]
    for p1, p2, r1, r2 in h_segs:
        b.seg(p1, p2, r1, r2, m=m_bone_dark, seg=12, smooth=True)
        b.cyl(r1 * 1.15, 0.022, loc=p1, seg=12, m=m_lab_titanium)

    p_tip_glow = (sign * 0.30, 0.34, 3.32)
    p_tip_end = (sign * 0.32, 0.38, 3.38)
    b.seg(p_tip_glow, p_tip_end, 0.008, 0.001, m=m_cyan_glow if sign == 1 else m_warning_red, seg=6, smooth=True)

# OJOS RECTANGULARES BIEN VISIBLES SOBRE EL ROSTRO (Sin quedar hundidos)
# Ojo derecho (visto a la izquierda): CIAN BRILLANTE
b.box((0.034, 0.022, 0.022), loc=(-0.050, -0.23, 2.54), rot=(10, 0, 0), m=m_cyan_glow)

# Ojo izquierdo (visto a la derecha): ROJO BRILLANTE
b.box((0.034, 0.022, 0.022), loc=(0.050, -0.23, 2.54), rot=(10, 0, 0), m=m_warning_red)

# Mandíbula inferior integrada con dientes
b.sph(0.13, loc=(0.0, -0.15, 2.40), scale=(1.0, 1.25, 0.55), m=m_bone_dark)

# Dientes de marfil
for step in range(7):
    t = step / 6.0
    t_ang = -math.pi * 0.35 + t * math.pi * 0.70
    fx = 0.08 * math.sin(t_ang)
    fy = -0.20 - 0.08 * math.cos(t_ang)
    b.seg((fx, fy, 2.48), (fx, fy, 2.42), 0.008, 0.0015, m=m_bone_ivory, seg=6, smooth=True)
    if step % 2 == 0:
        b.seg((fx * 0.9, fy, 2.37), (fx * 0.9, fy, 2.43), 0.007, 0.0015, m=m_bone_ivory, seg=6, smooth=True)

# Build mesh
b.build(COL_NAME)

# --------------------------------------------------------------------------
# LIGHTING & CAMERA
# --------------------------------------------------------------------------
if scene.world is None:
    scene.world = bpy.data.worlds.new("World_Studio")
scene.world.use_nodes = True
bg = scene.world.node_tree.nodes.get("Background")
if bg:
    bg.inputs["Color"].default_value = (0.04, 0.05, 0.07, 1.0)
    bg.inputs["Strength"].default_value = 0.5

cam_data = bpy.data.cameras.new("Cam_Boss5_V2")
cam_obj = bpy.data.objects.new("Cam_Boss5_V2", cam_data)
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

key_data = bpy.data.lights.new("Light_Key_B5", type='AREA')
key_obj = bpy.data.objects.new("Light_Key_B5", key_data)
scene.collection.objects.link(key_obj)
key_data.energy = 250.0
key_data.size = 3.5
key_data.color = (1.0, 0.98, 0.95)
key_obj.location = (3.2, -3.2, 4.2)

fill_data = bpy.data.lights.new("Light_Fill_B5", type='AREA')
fill_obj = bpy.data.objects.new("Light_Fill_B5", fill_data)
scene.collection.objects.link(fill_obj)
fill_data.energy = 90.0
fill_data.size = 4.5
fill_data.color = (0.75, 0.85, 1.0)
fill_obj.location = (-3.2, -3.2, 2.5)

rim_data = bpy.data.lights.new("Light_Rim_B5", type='AREA')
rim_obj = bpy.data.objects.new("Light_Rim_B5", rim_data)
scene.collection.objects.link(rim_obj)
rim_data.energy = 200.0
rim_data.size = 3.5
rim_data.color = (0.85, 0.70, 1.0)
rim_obj.location = (-0.6, 3.6, 3.4)

out_despues = os.path.join(output_dir, "boss5_despues.png")
scene.render.filepath = out_despues
bpy.ops.render.render(write_still=True)
print(f"RENDERED POLISHED BOSS 5 DESPUES -> {out_despues}")

blend_path = r"E:\Darx_Proyect\Saved\Player_Skin_Workspace\DarX_Boss5_Redesign.blend"
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f"FILE_SAVED: {blend_path}")

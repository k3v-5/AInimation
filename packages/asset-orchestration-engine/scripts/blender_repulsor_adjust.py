"""darx_repulsor_adjust.py — Rediseño Completo de El Repulsor (SK_Repulsor)
Entidad Robótica Flotante de Manipulación Cinética y Gravedad Inversa:
- Doble anillo magnético circular toroidal orbitando el torso con holgura segura (cero clipping >= 30cm)
- Guanteletes gravitatorios pesados de onda de choque con placas de compresión y emisores cóncavos en las palmas
- Columna vertebral biomecánica y nodo de levitación cónico inferior (sin piernas) con haz gravitatorio
- Reactor toroidal pectoral de compresión de plasma cinético
- Casco aerodinámico facetado con visor envolvente cian y estabilizadores
"""

import bpy, bmesh, math, os, sys
from mathutils import Vector, Matrix, Euler

art_blender_dir = r"E:\Darx_Proyect\Art\Blender"
if art_blender_dir not in sys.path:
    sys.path.append(art_blender_dir)

import darx_lib as dl

output_dir = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"
os.makedirs(output_dir, exist_ok=True)

ARM_NAME = "ARM_Repulsor"
SK_NAME = "SK_Repulsor"
COL_NAME = "DARX_Repulsor"
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
m_dark = dl.mat("M_Repulsor_Dark", (0.05, 0.06, 0.08), rough=0.24, metal=0.90)
m_steel = dl.mat("M_Repulsor_Steel", (0.24, 0.25, 0.28), rough=0.18, metal=0.95)
m_chrome = dl.mat("M_Repulsor_Chrome", (0.86, 0.88, 0.92), rough=0.08, metal=0.98)

# Emisión de Plasma Cinético y Fuerza Gravitatoria
m_cyan = dl.mat("M_Repulsor_Cyan", (0.0, 0.95, 1.0), emis=(0.0, 0.95, 1.0), emis_str=42.0)
m_magenta = dl.mat("M_Repulsor_Magenta", (0.92, 0.08, 0.95), emis=(0.92, 0.08, 0.95), emis_str=36.0)

# --------------------------------------------------------------------------
# 2. ARMATURE
# --------------------------------------------------------------------------
def build_rig():
    arm_data = bpy.data.armatures.new(f"{ARM_NAME}_Data")
    arm_obj = bpy.data.objects.new(ARM_NAME, arm_data)
    col.objects.link(arm_obj)
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='EDIT')

    eb = arm_data.edit_bones
    root = eb.new("root")
    root.head = (0, 0, 0)
    root.tail = (0, -0.15, 0)

    # Nodo de Levitación Inferior
    node = eb.new("levitation_node")
    node.parent = root
    node.head = (0, 0, 0.55)
    node.tail = (0, 0, 0.95)

    spine = eb.new("spine")
    spine.parent = node
    spine.head = (0, 0, 0.95)
    spine.tail = (0, 0, 1.35)

    chest = eb.new("chest")
    chest.parent = spine
    chest.head = (0, 0, 1.35)
    chest.tail = (0, 0, 1.68)

    head = eb.new("head")
    head.parent = chest
    head.head = (0, -0.02, 1.68)
    head.tail = (0, -0.02, 1.98)

    # Anillos Magnéticos Orbitantes (Emparentados rígidamente a spine)
    ring_out = eb.new("ring_outer")
    ring_out.parent = spine
    ring_out.head = (0, 0, 1.25)
    ring_out.tail = (0, -0.75, 1.25)

    ring_in = eb.new("ring_inner")
    ring_in.parent = spine
    ring_in.head = (0, 0, 1.25)
    ring_in.tail = (0, -0.58, 1.25)

    # Brazos con Guanteletes Gravitatorios
    sh_l = eb.new("shoulder_L")
    sh_l.parent = chest
    sh_l.head = (0.24, 0, 1.60)
    sh_l.tail = (0.42, 0, 1.56)

    arm_l = eb.new("upperarm_L")
    arm_l.parent = sh_l
    arm_l.head = (0.42, 0, 1.56)
    arm_l.tail = (0.48, -0.22, 1.24)

    hand_l = eb.new("hand_L")
    hand_l.parent = arm_l
    hand_l.head = (0.48, -0.22, 1.24)
    hand_l.tail = (0.42, -0.52, 1.10)

    sh_r = eb.new("shoulder_R")
    sh_r.parent = chest
    sh_r.head = (-0.24, 0, 1.60)
    sh_r.tail = (-0.42, 0, 1.56)

    arm_r = eb.new("upperarm_R")
    arm_r.parent = sh_r
    arm_r.head = (-0.42, 0, 1.56)
    arm_r.tail = (-0.48, -0.22, 1.24)

    hand_r = eb.new("hand_R")
    hand_r.parent = arm_r
    hand_r.head = (-0.48, -0.22, 1.24)
    hand_r.tail = (-0.42, -0.52, 1.10)

    bpy.ops.object.mode_set(mode='OBJECT')
    return arm_obj

arm_obj = build_rig()

# --------------------------------------------------------------------------
# 3. CONSTRUCCIÓN DE LA MALLA
# --------------------------------------------------------------------------
b = dl.MB(SK_NAME)

# =========================================================================
# CABEZA: CASCO AERODINÁMICO CON VISOR ENVOLVENTE
# =========================================================================
b.bone("head")
# Cuello articulado con amortiguador central
b.cyl(0.065, 0.10, loc=(0, -0.02, 1.68), rot=(0, 0, 0), m=m_steel)

# Casco angular facetado
b.box((0.24, 0.26, 0.24), loc=(0, -0.02, 1.84), m=m_dark)
# Visera frontal estilizada en cromo
b.box((0.26, 0.08, 0.04), loc=(0, -0.14, 1.94), rot=(14, 0, 0), m=m_chrome)

# Visor envolvente cinético cian
b.box((0.22, 0.04, 0.06), loc=(0, -0.145, 1.85), m=m_cyan)
# Diodos de telemetría magenta en las sienes
b.sph(0.014, loc=(-0.13, -0.06, 1.88), m=m_magenta, smooth=True)
b.sph(0.014, loc=(0.13, -0.06, 1.88), m=m_magenta, smooth=True)

# Aletas de estabilización de fase traseras
for sign in (1, -1):
    b.prism(0.03, 0.08, 0.14, loc=(sign * 0.10, 0.12, 1.90), rot=(R(20), sign * R(15), 0), taper=0.2, m=m_steel)

# =========================================================================
# PECHO: CORAZA EN "V" Y REACTOR CINÉTICO TOROIDAL
# =========================================================================
b.bone("chest")
# Chasis pectoral de aleación oscura
b.box((0.48, 0.32, 0.42), loc=(0, 0, 1.52), m=m_dark)

# REACTOR CINÉTICO TOROIDAL CENTRAL EN EL PECHO
b.cyl(0.12, 0.06, loc=(0, -0.14, 1.52), rot=(R(90), 0, 0), m=m_steel)
b.cyl(0.09, 0.08, loc=(0, -0.14, 1.52), rot=(R(90), 0, 0), m=m_cyan)
b.sph(0.06, loc=(0, -0.16, 1.52), m=m_cyan, smooth=True)
b.cyl(0.03, 0.09, loc=(0, -0.15, 1.52), rot=(R(90), 0, 0), m=m_chrome)

# Costillas de contención de plasma frontal
for sign in (1, -1):
    b.box((0.08, 0.04, 0.28), loc=(sign * 0.16, -0.13, 1.52), rot=(0, sign * 14, 0), m=m_steel)
    b.box((0.015, 0.015, 0.20), loc=(sign * 0.16, -0.15, 1.52), rot=(0, sign * 14, 0), m=m_cyan)

# =========================================================================
# COLUMNA ESPINAL Y NODO DE LEVITACIÓN INFERIOR (SIN PIERNAS)
# =========================================================================
b.bone("spine")
# Columna biomecánica segmentada
b.box((0.26, 0.22, 0.36), loc=(0, 0, 1.15), m=m_dark)
for z_v in (1.05, 1.15, 1.25):
    b.cyl(0.09, 0.04, loc=(0, 0.08, z_v), rot=(0, 90, 0), m=m_steel)
    b.sph(0.02, loc=(0, -0.10, z_v), m=m_magenta, smooth=True)

b.bone("levitation_node")
# Cono de eyección de gravedad inversa
b.frustum(0.22, 0.09, 0.36, loc=(0, 0, 0.76), rot=(R(180), 0, 0), m=m_dark, seg=16)
# Anillos magnéticos concéntricos en la base
b.cyl(0.18, 0.03, loc=(0, 0, 0.85), rot=(0, 0, 0), m=m_steel)
b.cyl(0.13, 0.03, loc=(0, 0, 0.72), rot=(0, 0, 0), m=m_chrome)
b.cyl(0.08, 0.05, loc=(0, 0, 0.58), rot=(0, 0, 0), m=m_cyan, seg=16)
b.sph(0.05, loc=(0, 0, 0.54), m=m_cyan, smooth=True)

# 4 Aletas de estabilización gravitatoria inferior
for ang_stab in (45, 135, 225, 315):
    rad_s = math.radians(ang_stab)
    sx = 0.16 * math.cos(rad_s)
    sy = 0.16 * math.sin(rad_s)
    b.prism(0.03, 0.08, 0.20, loc=(sx, sy, 0.72), rot=(0, 0, ang_stab), taper=0.2, m=m_steel)

# =========================================================================
# ANILLOS MAGNÉTICOS ORBITANTES (CERO-CLIPPING: BUFFER >= 30CM)
# =========================================================================
# 1. Anillo Interior (ring_inner): Radio 0.58m, Inclinado en X a 15°
b.bone("ring_inner")
r_in = 0.58
rot_in_x = R(15)
for a in range(0, 360, 15):
    rad = math.radians(a)
    lx = r_in * math.cos(rad)
    ly = r_in * math.sin(rad)
    # Aplicar rotación inclinada en X
    wy = ly * math.cos(rot_in_x)
    wz = 1.25 + ly * math.sin(rot_in_x)
    # Eslabón del anillo
    b.box((0.035, 0.05, 0.025), loc=(lx, wy, wz), rot=(rot_in_x, 0, -rad), m=m_chrome)

# 6 Inductores de compresión magnética en el anillo interior
for a_ind in (0, 60, 120, 180, 240, 300):
    rad_i = math.radians(a_ind)
    ix = r_in * math.cos(rad_i)
    iy = r_in * math.sin(rad_i)
    wiy = iy * math.cos(rot_in_x)
    wiz = 1.25 + iy * math.sin(rot_in_x)
    b.box((0.05, 0.08, 0.04), loc=(ix, wiy, wiz), rot=(rot_in_x, 0, -rad_i), m=m_steel)
    b.sph(0.016, loc=(ix, wiy, wiz), m=m_cyan, smooth=True)

# 2. Anillo Exterior (ring_outer): Radio 0.75m, Inclinado en Y a -18°
b.bone("ring_outer")
r_out = 0.75
rot_out_y = R(-18)
for a in range(0, 360, 12):
    rad = math.radians(a)
    lx = r_out * math.cos(rad)
    ly = r_out * math.sin(rad)
    # Aplicar rotación inclinada en Y
    wx = lx * math.cos(rot_out_y)
    wz = 1.25 - lx * math.sin(rot_out_y)
    b.box((0.045, 0.065, 0.030), loc=(wx, ly, wz), rot=(0, rot_out_y, -rad), m=m_dark)

# 4 Proyectores vectoriales en el anillo exterior
for a_proj in (45, 135, 225, 315):
    rad_p = math.radians(a_proj)
    px = r_out * math.cos(rad_p)
    py = r_out * math.sin(rad_p)
    wpx = px * math.cos(rot_out_y)
    wpz = 1.25 - px * math.sin(rot_out_y)
    b.prism(0.06, 0.09, 0.08, loc=(wpx, py, wpz), rot=(0, rot_out_y, -rad_p), taper=0.2, m=m_steel)
    b.sph(0.022, loc=(wpx, py, wpz), m=m_cyan, smooth=True)

# =========================================================================
# BRAZOS Y GUANTELETES GRAVITATORIOS DE ONDA DE CHOQUE
# =========================================================================
for side, sign in [("L", 1), ("R", -1)]:
    b.bone(f"shoulder_{side}")
    # Hombrera angular en aleación y cromo
    b.box((0.20, 0.24, 0.16), loc=(sign * 0.34, 0, 1.62), rot=(0, sign * 15, 0), m=m_dark)
    b.box((0.14, 0.18, 0.05), loc=(sign * 0.36, 0, 1.71), rot=(0, sign * 15, 0), m=m_chrome)

    # Brazo Superior con Pistón Hidráulico
    b.bone(f"upperarm_{side}")
    p_sh = (sign * 0.42, 0, 1.56)
    p_el = (sign * 0.48, -0.22, 1.24)
    b.seg(p_sh, p_el, 0.065, 0.055, m=m_dark, seg=8, smooth=False)
    b.cyl(0.055, 0.08, loc=p_el, rot=(90, 0, 0), m=m_steel)
    # Vástago de cromo
    b.seg((sign * 0.40, -0.05, 1.52), (sign * 0.46, -0.20, 1.28), 0.016, 0.012, m=m_chrome, seg=6, smooth=True)

    # GUANTELETE GRAVITATORIO DE ONDA DE CHOQUE
    b.bone(f"hand_{side}")
    p_wrist = (sign * 0.42, -0.52, 1.10)
    p_mid_g = ((p_el[0]+p_wrist[0])/2, (p_el[1]+p_wrist[1])/2, (p_el[2]+p_wrist[2])/2)

    # Bloque principal del antebrazo reforzado
    b.box((0.18, 0.26, 0.16), loc=p_mid_g, rot=(22, sign * 10, 0), m=m_steel)

    # 3 Placas de compresión de choque retráctiles exteriores
    for dy_p in (-0.08, 0.0, 0.08):
        b.box((0.04, 0.06, 0.18), loc=(p_mid_g[0] + sign * 0.10, p_mid_g[1] + dy_p, p_mid_g[2]), rot=(22, sign * 10, 0), m=m_dark)

    # EMISOR CÓNCAVO DE PLASMA CINÉTICO EN LA PALMA / FRENTE
    p_emitter = (p_wrist[0], p_wrist[1] - 0.06, p_wrist[2] - 0.02)
    b.cyl(0.085, 0.04, loc=p_emitter, rot=(R(-70), sign * R(10), 0), m=m_chrome, seg=16)
    # Núcleo de disparo de onda de choque cian
    b.sph(0.065, loc=p_emitter, m=m_cyan, u=16, v=8, smooth=True)
    b.cyl(0.04, 0.03, loc=(p_emitter[0], p_emitter[1] - 0.02, p_emitter[2]), rot=(R(-70), sign * R(10), 0), m=m_magenta, seg=12)

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
    bg.inputs["Color"].default_value = (0.02, 0.02, 0.025, 1.0)
    bg.inputs["Strength"].default_value = 0.35

cam_data = bpy.data.cameras.new("Cam_Repulsor_Adjust")
cam_obj = bpy.data.objects.new("Cam_Repulsor_Adjust", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_data.lens = 45.0

empty_target = bpy.data.objects.new("Cam_Repulsor_Target", None)
scene.collection.objects.link(empty_target)
empty_target.location = (0.0, -0.10, 1.30)

tt = cam_obj.constraints.new(type='TRACK_TO')
tt.target = empty_target
tt.track_axis = 'TRACK_NEGATIVE_Z'
tt.up_axis = 'UP_Y'

dist = 3.2
cam_obj.location = (dist * 0.65, -dist * 0.85, 1.30 + dist * 0.30)

# Studio Lights
key_data = bpy.data.lights.new("Light_Key_Rep", type='AREA')
key_obj = bpy.data.objects.new("Light_Key_Rep", key_data)
scene.collection.objects.link(key_obj)
key_data.energy = 260.0
key_data.size = 2.5
key_data.color = (0.95, 0.98, 1.0)
key_obj.location = (dist * 0.7, -dist * 0.6, 1.30 + dist * 0.8)

fill_data = bpy.data.lights.new("Light_Fill_Rep", type='AREA')
fill_obj = bpy.data.objects.new("Light_Fill_Rep", fill_data)
scene.collection.objects.link(fill_obj)
fill_data.energy = 90.0
fill_data.size = 3.5
fill_data.color = (0.0, 0.85, 1.0) # Relleno cian cinético
fill_obj.location = (-dist * 0.7, -dist * 0.6, 1.30 + dist * 0.4)

rim_data = bpy.data.lights.new("Light_Rim_Rep", type='AREA')
rim_obj = bpy.data.objects.new("Light_Rim_Rep", rim_data)
scene.collection.objects.link(rim_obj)
rim_data.energy = 240.0
rim_data.size = 2.0
rim_data.color = (0.85, 0.10, 0.95) # Contraluz magenta
rim_obj.location = (-dist * 0.2, dist * 0.8, 1.30 + dist * 0.6)

out_despues = os.path.join(output_dir, "repulsor_despues.png")
scene.render.filepath = out_despues
bpy.ops.render.render(write_still=True)
print(f"RENDERED REFINED REPULSOR DESPUES -> {out_despues}")

blend_path = r"E:\Darx_Proyect\Saved\Player_Skin_Workspace\DarX_Repulsor_Redesign.blend"
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f"FILE_SAVED: {blend_path}")

"""darx_robot_adjust.py — Rediseño Completo de El Robot de Agarre (SK_Robot_Grab)
Robot Patrullero Oruga de Asfixia e Inmovilización:
- Tren de rodaje pesado con orugas de acero, ruedas motrices perforadas y tubos de escape dobles
- Garras mecánicas gigantes de prensa hidráulica con almohadillas dentadas de sujeción y pistones de cromo
- Coraza de fundición industrial en rojo maquinaria pesada (M_Robot_IndustrialRed) y placas de acero
- Cabeza acorazada hundida entre hombreras con visor óptico de detección rojo penetrante
- Cintura estrecha con columna hidráulica central (cero clipping con las garras)
"""

import bpy, bmesh, math, os, sys
from mathutils import Vector, Matrix, Euler

art_blender_dir = r"E:\Darx_Proyect\Art\Blender"
if art_blender_dir not in sys.path:
    sys.path.append(art_blender_dir)

import darx_lib as dl

output_dir = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"
os.makedirs(output_dir, exist_ok=True)

ARM_NAME = "ARM_Robot_Grab"
SK_NAME = "SK_Robot_Grab"
COL_NAME = "DARX_Robot"
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
m_red = dl.mat("M_Robot_IndustrialRed", (0.72, 0.06, 0.04), rough=0.32, metal=0.25)
m_dark = dl.mat("M_Robot_Dark", (0.06, 0.065, 0.075), rough=0.35, metal=0.85)
m_steel = dl.mat("M_Robot_Steel", (0.42, 0.44, 0.48), rough=0.20, metal=0.95)
m_chrome = dl.mat("M_Robot_Chrome", (0.88, 0.90, 0.94), rough=0.08, metal=0.98)
m_hazard = dl.mat("M_Robot_Hazard", (0.92, 0.72, 0.08), rough=0.35, metal=0.20)
m_eye = dl.mat("M_Robot_Eye", (1.0, 0.04, 0.02), emis=(1.0, 0.04, 0.02), emis_str=42.0)

# --------------------------------------------------------------------------
# 2. PUNTOS CLAVE Y TREN DE RODAJE
# --------------------------------------------------------------------------
TRACK_X = 0.212
TRACK_R = 0.152
TRACK_Y = 0.150
DECK_Z = (0.352, 0.560)
RING_Z = (0.560, 0.630)
WAIST_R = 0.104

ARM_X = 0.228
SH = (ARM_X, -0.030, 1.440)
EL = (ARM_X + 0.008, -0.062, 1.140)
WR = (ARM_X, -0.150, 1.010)
HAND_Y, PALM_Z, KNUCKLE_Z = -0.178, 0.940, 0.850
WRIST_Z = WR[2]
FINGER_X = (-0.044, 0.018, 0.080)
LEAN = R(-6)

LUG_T = 0.028
N_LUGS = 24

def _mir(pt, s):
    return (pt[0] * s, pt[1], pt[2])

def belt_bone(t, i):
    return "belt_%s_%02d" % (t, i)

def _belt_path(n, inset=LUG_T / 2 + 0.0012):
    rad = TRACK_R - inset
    straight, arc = TRACK_Y * 2, math.pi * rad
    total = 2 * straight + 2 * arc
    top, bot = TRACK_R * 2 - inset, inset
    out = []
    for i in range(n):
        d = total * i / n
        if d < straight:
            out.append(((-TRACK_Y + d, bot), 0.0))
        elif d < straight + arc:
            a = (d - straight) / rad
            out.append(((TRACK_Y + math.sin(a) * rad, TRACK_R - math.cos(a) * rad), a))
        elif d < 2 * straight + arc:
            k = d - straight - arc
            out.append(((TRACK_Y - k, top), math.pi))
        else:
            a = (d - 2 * straight - arc) / rad
            out.append(((-TRACK_Y - math.sin(a) * rad, TRACK_R + math.cos(a) * rad), math.pi + a))
    return out

def _belt_bones():
    out = []
    for s, t in ((-1, "L"), (1, "R")):
        x = TRACK_X * s
        for i, ((py, pz), ang) in enumerate(_belt_path(N_LUGS)):
            ty, tz = py + math.cos(ang) * 0.05, pz + math.sin(ang) * 0.05
            out.append((belt_bone(t, i), (x, py, pz), (x, ty, tz), "track_%s" % t, False))
    return out

def bone_list():
    Y = HAND_Y
    B = [
        ("root", (0, 0, 0), (0, -0.25, 0), None, False),
        ("track_L", (-TRACK_X, 0, TRACK_R), (-TRACK_X, -0.26, TRACK_R), "root", False),
        ("track_R", (TRACK_X, 0, TRACK_R), (TRACK_X, -0.26, TRACK_R), "root", False),
    ] + _belt_bones() + [
        ("chassis", (0, 0, DECK_Z[0]), (0, 0, RING_Z[1]), "root", False),
        ("spine", (0, 0, RING_Z[1]), (0, -0.02, 1.000), "chassis", True),
        ("chest", (0, -0.02, 1.000), (0, -0.05, 1.490), "spine", True),
        ("neck", (0, -0.05, 1.490), (0, -0.062, 1.600), "chest", True),
        ("head", (0, -0.062, 1.600), (0, -0.082, 1.920), "neck", True),
    ]
    for s, t in ((-1, "L"), (1, "R")):
        B += [
            ("clavicle_%s" % t, (0.088 * s, -0.045, 1.470), _mir(SH, s), "chest", False),
            ("upperarm_%s" % t, _mir(SH, s), _mir(EL, s), "clavicle_%s" % t, True),
            ("forearm_%s" % t, _mir(EL, s), _mir(WR, s), "upperarm_%s" % t, True),
            ("hand_%s" % t, _mir(WR, s), (ARM_X * s, Y - 0.005, KNUCKLE_Z), "forearm_%s" % t, True),
            ("thumb_%s" % t, (ARM_X * s - 0.030 * s, Y + 0.000, 0.955), (ARM_X * s - 0.070 * s, Y - 0.120, 0.795), "hand_%s" % t, False),
        ]
        for i, fx in enumerate(FINGER_X):
            B.append(("finger%d_%s" % (i + 1, t), (ARM_X * s + fx, Y - 0.005, 0.838), (ARM_X * s + fx, Y - 0.150, 0.612), "hand_%s" % t, False))
    return B

# --------------------------------------------------------------------------
# 3. CONSTRUCCIÓN DE LA MALLA
# --------------------------------------------------------------------------
b = dl.MB(SK_NAME)

# =========================================================================
# ORUGAS Y TREN DE RODAJE
# =========================================================================
for s, t in ((-1, "L"), (1, "R")):
    x = TRACK_X * s
    b.bone("track_%s" % t)
    W = 0.184
    # Ruedas motrices con orificios de aligeramiento
    for sy in (-1, 1):
        b.cyl(TRACK_R - 0.024, W - 0.052, (x, TRACK_Y * sy, TRACK_R), rot=(0, R(90), 0), seg=18, m=m_steel)
        b.cyl(0.055, W - 0.030, (x, TRACK_Y * sy, TRACK_R), rot=(0, R(90), 0), seg=12, m=m_dark)
        b.cyl(0.025, W - 0.020, (x, TRACK_Y * sy, TRACK_R), rot=(0, R(90), 0), seg=8, m=m_chrome)
    # Rodillos tensores
    for i in (-1, 0, 1):
        b.cyl(0.058, W - 0.054, (x, i * 0.098, 0.070), rot=(0, R(90), 0), seg=12, m=m_steel)

    # Faldón blindado de oruga
    b.box((W - 0.055, TRACK_Y * 2 + 0.12, 0.140), (x, 0, TRACK_R), m=m_red)
    b.box((W - 0.025, 0.065, 0.180), (x, 0, TRACK_R), m=m_steel)

    # Tacos de la cadena (un hueso por taco)
    for i, ((py, pz), ang) in enumerate(_belt_path(N_LUGS)):
        b.bone(belt_bone(t, i))
        # Zapata de tracción pesada
        b.box((W, 0.066, LUG_T), (x, py, pz), rot=(-ang, 0, 0), m=m_dark)
        # Nervio de agarre central de acero
        b.box((W + 0.012, 0.024, 0.016), (x, py, pz), rot=(-ang, 0, 0), m=m_steel)

# =========================================================================
# CHASIS DE CUBIERTA Y MOTOR POSTERIOR
# =========================================================================
b.bone("chassis")
z0, z1 = DECK_Z
# Casco de cubierta blindado
b.prism(0.530, 0.440, z1 - z0, (0, 0.010, (z0 + z1) / 2), taper=0.46, m=m_red)
# Paragolpes frontal de choque
b.box((0.560, 0.160, 0.120), (0, -0.190, z0 + 0.070), m=m_dark)
b.box((0.320, 0.075, 0.065), (0, -0.245, z0 + 0.090), m=m_steel)

# DOBLE ESCAPE TÉRMICO POSTERIOR Y REJILLAS DE VENTILACIÓN
b.box((0.440, 0.140, 0.140), (0, 0.210, z0 + 0.120), m=m_dark)
# Rejillas de refrigeración
for z_v in (z0 + 0.08, z0 + 0.12, z0 + 0.16):
    b.box((0.36, 0.02, 0.015), (0, 0.285, z_v), m=m_steel)

# Tubos de escape cilíndricos gemelos
for sign in (1, -1):
    b.cyl(0.038, 0.22, (sign * 0.16, 0.22, z1 + 0.08), rot=(R(15), 0, 0), seg=12, m=m_steel)
    b.cyl(0.046, 0.04, (sign * 0.16, 0.22, z1 + 0.18), rot=(R(15), 0, 0), seg=12, m=m_dark)

# Corona de rodamiento para el giro del torso
b.cyl(0.120, RING_Z[1] - RING_Z[0] + 0.02, (0, 0, (RING_Z[0] + RING_Z[1]) / 2), seg=24, m=m_steel)
b.cyl(0.105, 0.030, (0, 0, RING_Z[1]), seg=20, m=m_dark)

# =========================================================================
# TORSO, COLUMNA Y BLINDAJE PECTORAL
# =========================================================================
b.bone("spine")
# Cintura estrecha con columna hidráulica central (libre de colisión con garras)
b.cyl(WAIST_R, 0.360, (0, -0.010, 0.800), seg=16, m=m_dark)
b.cyl(WAIST_R + 0.022, 0.055, (0, -0.010, 0.650), seg=16, m=m_steel)
b.cyl(WAIST_R + 0.015, 0.045, (0, -0.012, 0.960), seg=16, m=m_steel)
# Columnas de refuerzo hidráulico laterales
for sign in (1, -1):
    b.cyl(0.024, 0.32, (sign * 0.08, -0.01, 0.80), rot=(0, 0, 0), m=m_chrome)

b.bone("chest")
# Coraza pectoral en "V" de maquinaria pesada
b.prism(0.420, 0.390, 0.520, (0, -0.030, 1.245), rot=(LEAN, 0, 0), taper=1.14, m=m_red)
# Peto frontal biselado de fundición oscura
b.box((0.340, 0.085, 0.310), (0, -0.220, 1.265), rot=(LEAN, 0, 0), m=m_dark)
b.box((0.260, 0.065, 0.090), (0, -0.245, 1.360), rot=(LEAN, 0, 0), m=m_steel)

# Franja de advertencia industrial (Hazard)
b.box((0.280, 0.030, 0.045), (0, -0.250, 1.220), rot=(LEAN, 0, 0), m=m_hazard)

# Mochila trasera y radiador
b.box((0.340, 0.150, 0.330), (0, 0.165, 1.265), rot=(LEAN, 0, 0), m=m_dark)
b.box((0.220, 0.065, 0.190), (0, 0.230, 1.295), rot=(LEAN, 0, 0), m=m_steel)
b.box((0.410, 0.340, 0.080), (0, -0.048, 1.490), rot=(LEAN, 0, 0), m=m_dark)

b.bone("neck")
b.cyl(0.085, 0.110, (0, -0.050, 1.545), seg=14, m=m_steel)

# =========================================================================
# CABEZA ACORAZADA Y FOCO ÓPTICO ROJO PENETRANTE
# =========================================================================
b.bone("head")
# Casco bunker hundido
b.prism(0.252, 0.248, 0.175, (0, -0.092, 1.700), rot=(LEAN, 0, 0), taper=0.82, m=m_red)
b.box((0.195, 0.160, 0.055), (0, -0.082, 1.8859), rot=(LEAN, 0, 0), m=m_dark)
b.box((0.220, 0.058, 0.075), (0, -0.200, 1.694), rot=(LEAN, 0, 0), m=m_dark)

# VISOR ÓPTICO DE DETECCIÓN ROJO PENETRANTE
b.box((0.190, 0.032, 0.050), (0, -0.220, 1.692), rot=(LEAN, 0, 0), m=m_eye)
b.cyl(0.024, 0.180, (0, -0.222, 1.692), rot=(0, R(90), 0), seg=12, m=m_eye)

# Transductores de audio / sensores laterales
for s in (-1, 1):
    b.cyl(0.040, 0.036, (0.128 * s, -0.084, 1.706), rot=(0, R(90), 0), seg=12, m=m_steel)
    b.sph(0.016, (0.145 * s, -0.084, 1.706), m=m_dark, smooth=True)

# =========================================================================
# BRAZOS Y CLAVÍCULAS
# =========================================================================
for s, t in ((-1, "L"), (1, "R")):
    x = ARM_X * s
    sh = _mir(SH, s)
    el = _mir(EL, s)
    wr = _mir(WR, s)

    # Clavícula y hombrera
    b.bone("clavicle_%s" % t)
    b.box((0.205, 0.330, 0.300), (x, -0.036, 1.530), rot=(LEAN, 0, 0), m=m_red)
    b.box((0.215, 0.270, 0.060), (x, -0.038, 1.660), rot=(LEAN, 0, 0), m=m_dark)
    b.box((0.072, 0.280, 0.230), (x + 0.066 * s, -0.036, 1.522), rot=(LEAN, 0, 0), m=m_steel)

    # Brazo Superior con Pistón Hidráulico
    b.bone("upperarm_%s" % t)
    b.sph(0.110, sh, u=16, v=10, m=m_dark, smooth=True)
    b.seg(sh, el, 0.102, 0.095, m=m_red, seg=10, smooth=True)
    # Cilindro hidráulico de bíceps
    b.cyl(0.035, 0.26, ((sh[0]+el[0])/2 + 0.03*s, (sh[1]+el[1])/2 + 0.04, (sh[2]+el[2])/2), rot=(R(35), 0, 0), m=m_steel)
    b.cyl(0.018, 0.28, ((sh[0]+el[0])/2 + 0.03*s, (sh[1]+el[1])/2 + 0.04, (sh[2]+el[2])/2), rot=(R(35), 0, 0), m=m_chrome)

    # Antebrazo Reforzado
    b.bone("forearm_%s" % t)
    b.sph(0.098, el, u=14, v=8, m=m_dark, smooth=True)
    b.seg(el, wr, 0.094, 0.104, m=m_red, seg=10, smooth=True)
    # Vástago de antebrazo
    b.seg((el[0] + 0.070 * s, el[1] + 0.010, el[2] - 0.010),
          (wr[0] + 0.070 * s, wr[1] + 0.010, wr[2] - 0.010), 0.034, 0.030, m=m_steel, seg=8, smooth=True)

    # =====================================================================
    # GARRAS DE PRENSA HIDRÁULICA INDUSTRIAL (MANOS DE ASFIXIA)
    # =====================================================================
    y = HAND_Y
    b.bone("hand_%s" % t)
    # Muñeca articulada de alto torque
    b.cyl(0.102, 0.082, (x, y + 0.005, WRIST_Z), rot=(R(90), 0, 0), seg=16, m=m_dark)
    # Bloque de la palma
    b.box((0.220, 0.235, 0.230), (x, y, PALM_Z), m=m_red)
    b.box((0.215, 0.198, 0.060), (x, y + 0.008, 1.044), m=m_dark)
    # Placa frontal de agarre en acero de fundición
    b.box((0.202, 0.075, 0.155), (x, y - 0.125, 0.948), m=m_steel)
    b.box((0.208, 0.218, 0.052), (x, y - 0.005, KNUCKLE_Z), m=m_dark)

    # 3 DEDOS ARTICULADOS CON ALMOHADILLAS DENTADAS
    for i, fx in enumerate(FINGER_X):
        px = x + fx
        b.bone("finger%d_%s" % (i + 1, t))
        # Falange proximal
        b.box((0.058, 0.098, 0.136), (px, y - 0.048, 0.772), rot=(R(-14), 0, 0), m=m_red)
        # Falange medial
        b.box((0.052, 0.084, 0.114), (px, y - 0.104, 0.686), rot=(R(-40), 0, 0), m=m_dark)
        # Falange distal con garras dentadas de prensado
        b.box((0.045, 0.068, 0.082), (px, y - 0.134, 0.632), rot=(R(-66), 0, 0), m=m_steel)
        # Diente de agarre
        b.prism(0.038, 0.050, 0.035, (px, y - 0.150, 0.615), rot=(R(-66), 0, 0), taper=0.2, m=m_chrome)

    # PULGAR DE BLOQUEO DE ESTRANGULAMIENTO
    tx = x - 0.048 * s
    b.bone("thumb_%s" % t)
    b.box((0.074, 0.098, 0.130), (tx, y - 0.014, 0.908), rot=(R(24), 0, R(14) * s), m=m_red)
    b.box((0.062, 0.082, 0.105), (tx - 0.010 * s, y - 0.082, 0.830), rot=(R(58), 0, R(14) * s), m=m_dark)
    b.box((0.052, 0.064, 0.075), (tx - 0.018 * s, y - 0.132, 0.796), rot=(R(84), 0, R(14) * s), m=m_steel)
    b.prism(0.042, 0.048, 0.032, (tx - 0.022 * s, y - 0.152, 0.785), rot=(R(84), 0, R(14) * s), taper=0.2, m=m_chrome)

# --------------------------------------------------------------------------
# 4. BUILD Y ARMATURE
# --------------------------------------------------------------------------
mesh_obj = b.build(COL_NAME)
arm_obj = dl.armature(ARM_NAME, bone_list(), COL_NAME)
if mesh_obj and arm_obj:
    _, sin_malla = dl.bind(mesh_obj, arm_obj)
    if sin_malla:
        print("Huesos sin geometria propia:", sin_malla)

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

cam_data = bpy.data.cameras.new("Cam_Robot_Adjust")
cam_obj = bpy.data.objects.new("Cam_Robot_Adjust", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_data.lens = 45.0

empty_target = bpy.data.objects.new("Cam_Robot_Target", None)
scene.collection.objects.link(empty_target)
empty_target.location = (0.0, -0.10, 1.15)

tt = cam_obj.constraints.new(type='TRACK_TO')
tt.target = empty_target
tt.track_axis = 'TRACK_NEGATIVE_Z'
tt.up_axis = 'UP_Y'

dist = 3.2
cam_obj.location = (dist * 0.65, -dist * 0.85, 1.15 + dist * 0.30)

# Studio Lights
key_data = bpy.data.lights.new("Light_Key_Rob", type='AREA')
key_obj = bpy.data.objects.new("Light_Key_Rob", key_data)
scene.collection.objects.link(key_obj)
key_data.energy = 280.0
key_data.size = 2.5
key_data.color = (0.95, 0.98, 1.0)
key_obj.location = (dist * 0.7, -dist * 0.6, 1.15 + dist * 0.8)

fill_data = bpy.data.lights.new("Light_Fill_Rob", type='AREA')
fill_obj = bpy.data.objects.new("Light_Fill_Rob", fill_data)
scene.collection.objects.link(fill_obj)
fill_data.energy = 90.0
fill_data.size = 3.5
fill_data.color = (0.95, 0.20, 0.15) # Relleno rojo industrial
fill_obj.location = (-dist * 0.7, -dist * 0.6, 1.15 + dist * 0.4)

rim_data = bpy.data.lights.new("Light_Rim_Rob", type='AREA')
rim_obj = bpy.data.objects.new("Light_Rim_Rob", rim_data)
scene.collection.objects.link(rim_obj)
rim_data.energy = 220.0
rim_data.size = 2.0
rim_data.color = (0.95, 0.85, 0.45) # Contraluz ámbar industrial
rim_obj.location = (-dist * 0.2, dist * 0.8, 1.15 + dist * 0.6)

out_despues = os.path.join(output_dir, "robot_despues.png")
scene.render.filepath = out_despues
bpy.ops.render.render(write_still=True)
print(f"RENDERED REFINED ROBOT DESPUES -> {out_despues}")

blend_path = r"E:\Darx_Proyect\Saved\Player_Skin_Workspace\DarX_Robot_Redesign.blend"
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f"FILE_SAVED: {blend_path}")

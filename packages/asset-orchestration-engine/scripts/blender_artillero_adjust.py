"""darx_artillero_adjust.py — Rediseño de El Artillero (SK_Gunner_Turret)
Droide Centinela de Artillería Pesada:
- Base trípode articulada con pistones hidráulicos de nivelación y zapatas de anclaje sísmico
- Torreta blindada angular de perfil bajo con blindaje militar biselado y disipadores traseros
- Sensor óptico frontal de telemetría y puntería láser roja/ámbar
- Doble cañón gemelo reforzado con camisas de ventilación, pistones de retroceso y frenos de boca
- Materiales PBR: acero militar pavonado, acero cepillado, vástagos de cromo y láser de alta emisión
"""

import bpy, bmesh, math, os, sys
from mathutils import Vector, Matrix, Euler

art_blender_dir = r"E:\Darx_Proyect\Art\Blender"
if art_blender_dir not in sys.path:
    sys.path.append(art_blender_dir)

import darx_lib as dl

output_dir = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"
os.makedirs(output_dir, exist_ok=True)

ARM_NAME = "ARM_Gunner_Turret"
SK_NAME = "SK_Gunner_Turret"
COL_NAME = "DARX_Artillero"
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
m_gunner_dark = dl.mat("M_Gunner_ChassisDark", (0.07, 0.07, 0.09), rough=0.28, metal=0.90)
m_gunner_steel = dl.mat("M_Gunner_Steel", (0.24, 0.25, 0.28), rough=0.20, metal=0.95)
m_gunner_chrome = dl.mat("M_Gunner_Chrome", (0.86, 0.88, 0.92), rough=0.10, metal=0.98)

# Emisión de Telemetría y Láser
m_gunner_laser = dl.mat("M_Gunner_Laser", (1.0, 0.04, 0.02), emis=(1.0, 0.04, 0.02), emis_str=38.0)
m_gunner_amber = dl.mat("M_Gunner_Amber", (0.95, 0.60, 0.05), emis=(0.95, 0.60, 0.05), emis_str=24.0)

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

    # Base Trípode en el suelo
    hub = eb.new("base_tripod")
    hub.parent = root
    hub.head = (0, 0, 0.30)
    hub.tail = (0, 0, 0.50)

    # 3 Patas Hidráulicas a 120°
    angles = [R(-90), R(30), R(150)]
    for i, ang in enumerate(angles, start=1):
        leg = eb.new(f"leg_{i}")
        leg.parent = hub
        lx_start = 0.22 * math.cos(ang)
        ly_start = 0.22 * math.sin(ang)
        lx_end = 0.68 * math.cos(ang)
        ly_end = 0.68 * math.sin(ang)
        leg.head = (lx_start, ly_start, 0.30)
        leg.tail = (lx_end, ly_end, 0.0)

    # Torreta Giratoria Superior (Yaw 360)
    turret = eb.new("turret_yaw")
    turret.parent = hub
    turret.head = (0, 0, 0.52)
    turret.tail = (0, -0.25, 0.52)

    # Cañones Gemelos (Pitch)
    barrels = eb.new("barrels_pitch")
    barrels.parent = turret
    barrels.head = (0, -0.12, 0.54)
    barrels.tail = (0, -0.95, 0.54)

    bpy.ops.object.mode_set(mode='OBJECT')
    return arm_obj

arm_obj = build_rig()

# --------------------------------------------------------------------------
# 3. CONSTRUCCIÓN DE LA MALLA
# --------------------------------------------------------------------------
b = dl.MB(SK_NAME)

# =========================================================================
# BASE TRÍPODE Y ANILLO DE ROTACIÓN
# =========================================================================
b.bone("base_tripod")
# Anillo de rodamiento y corona dentada inferior
b.cyl(0.24, 0.08, loc=(0, 0, 0.28), rot=(0, 0, 0), m=m_gunner_steel)
b.cyl(0.20, 0.12, loc=(0, 0, 0.36), rot=(0, 0, 0), m=m_gunner_dark)
b.cyl(0.16, 0.06, loc=(0, 0, 0.44), rot=(0, 0, 0), m=m_gunner_chrome)

# =========================================================================
# 3 PATAS ARTICULADAS DE ANCLAJE SÍSMICO (120°)
# =========================================================================
angles_legs = [
    (1, R(-90)),  # Pata Frontal (-Y)
    (2, R(30)),   # Pata Trasera Derecha (+X, +Y)
    (3, R(150)),  # Pata Trasera Izquierda (-X, +Y)
]

for idx_leg, ang in angles_legs:
    b.bone(f"leg_{idx_leg}")
    cos_a = math.cos(ang)
    sin_a = math.sin(ang)

    p_hip = (0.20 * cos_a, 0.20 * sin_a, 0.32)
    p_knee = (0.42 * cos_a, 0.42 * sin_a, 0.26)
    p_foot = (0.68 * cos_a, 0.68 * sin_a, 0.04)

    # 1. Bisagra de hombro en el chasis
    b.cyl(0.045, 0.08, loc=p_hip, rot=(0, 90, math.degrees(ang)), m=m_gunner_steel)

    # 2. Brazo superior de la pata (viga reforzada)
    b.seg(p_hip, p_knee, 0.042, 0.036, m=m_gunner_dark, seg=8, smooth=False)
    # Refuerzo superior
    p_mid_femur = ((p_hip[0] + p_knee[0])/2, (p_hip[1] + p_knee[1])/2, (p_hip[2] + p_knee[2])/2 + 0.02)
    b.box((0.06, 0.16, 0.04), loc=p_mid_femur, rot=(0, 0, math.degrees(ang) + 90), m=m_gunner_steel)

    # 3. Articulación de rodilla y pistón neumático
    b.cyl(0.040, 0.07, loc=p_knee, rot=(0, 90, math.degrees(ang)), m=m_gunner_steel)
    p_piston_base = (0.16 * cos_a, 0.16 * sin_a, 0.24)
    b.seg(p_piston_base, p_knee, 0.016, 0.012, m=m_gunner_chrome, seg=6, smooth=True)

    # 4. Brazo inferior descendiendo al suelo
    b.seg(p_knee, p_foot, 0.038, 0.030, m=m_gunner_dark, seg=8, smooth=False)

    # 5. Zapata de anclaje sísmico (pie de agarre con garra al suelo Z=0)
    b.box((0.14, 0.22, 0.05), loc=p_foot, rot=(0, 0, math.degrees(ang) + 90), m=m_gunner_steel)
    # Garra / púa de penetración en el suelo
    p_spike = (0.76 * cos_a, 0.76 * sin_a, 0.01)
    b.seg(p_foot, p_spike, 0.024, 0.005, m=m_gunner_dark, seg=6, smooth=False)
    # Indicador de luz de anclaje
    b.sph(0.012, (0.64 * cos_a, 0.64 * sin_a, 0.07), m=m_gunner_amber, smooth=True)

# =========================================================================
# TORRETA BLINDADA (YAW 360)
# =========================================================================
b.bone("turret_yaw")
# Cuerpo principal de la cápsula blindada (perfil angular biselado)
b.box((0.48, 0.44, 0.24), loc=(0, 0.02, 0.58), m=m_gunner_dark)
# Blindaje biselado lateral
for sign in (1, -1):
    b.box((0.08, 0.38, 0.20), loc=(sign * 0.25, 0.02, 0.58), rot=(0, sign * 18, 0), m=m_gunner_steel)

# Módulo trasero de munición y disipadores térmicos
b.box((0.36, 0.18, 0.22), loc=(0, 0.24, 0.59), m=m_gunner_dark)
for z_v in (0.54, 0.60, 0.66):
    b.box((0.28, 0.03, 0.02), loc=(0, 0.33, z_v), m=m_gunner_steel)

# Batería de plasma / celda de energía trasera
b.cyl(0.045, 0.24, loc=(0, 0.18, 0.72), rot=(0, 90, 0), m=m_gunner_steel)
b.cyl(0.035, 0.20, loc=(0, 0.18, 0.72), rot=(0, 90, 0), m=m_gunner_amber)

# Cúpula superior y módulo de antena / sensor
b.box((0.24, 0.26, 0.08), loc=(0, 0.02, 0.72), m=m_gunner_dark)
b.cyl(0.05, 0.06, loc=(0.10, 0.08, 0.78), rot=(0, 0, 0), m=m_gunner_steel)

# UNIDAD DE TELEMETRÍA Y SENSOR FRONTAL (LÁSER ROJO / ÁMBAR)
b.box((0.20, 0.06, 0.10), loc=(0, -0.22, 0.66), m=m_gunner_steel)
# Visor óptico de puntería en rojo de alerta
b.box((0.14, 0.03, 0.04), loc=(0, -0.25, 0.66), m=m_gunner_laser)
# Telémetro láser auxiliar ámbar
b.sph(0.016, (0.06, -0.24, 0.62), m=m_gunner_amber, smooth=True)
b.sph(0.016, (-0.06, -0.24, 0.62), m=m_gunner_amber, smooth=True)

# =========================================================================
# DOBLE CAÑÓN GEMELO DE ARTILLERÍA PESADA (PITCH)
# =========================================================================
b.bone("barrels_pitch")
# Eje central de giro de elevación / inclinación
b.cyl(0.055, 0.38, loc=(0, -0.12, 0.54), rot=(0, 90, 0), m=m_gunner_steel)

for sign in (1, -1):
    x_barrel = sign * 0.14

    # 1. Bloque de culata reforzado
    b.box((0.09, 0.18, 0.12), loc=(x_barrel, -0.16, 0.54), m=m_gunner_dark)

    # 2. Pistón hidráulico de retroceso
    b.cyl(0.018, 0.22, loc=(x_barrel, -0.26, 0.61), rot=(90, 0, 0), m=m_gunner_chrome)
    b.cyl(0.025, 0.14, loc=(x_barrel, -0.18, 0.61), rot=(90, 0, 0), m=m_gunner_steel)

    # 3. Tubo de cañón cilíndrico estriado
    b.cyl(0.042, 0.62, loc=(x_barrel, -0.52, 0.54), rot=(90, 0, 0), m=m_gunner_steel)

    # 4. Camisa de refrigeración ranurada sobre el cañón
    b.cyl(0.052, 0.32, loc=(x_barrel, -0.42, 0.54), rot=(90, 0, 0), m=m_gunner_dark)
    for z_slot in (-0.34, -0.42, -0.50):
        b.box((0.11, 0.02, 0.02), loc=(x_barrel, z_slot, 0.54), m=m_gunner_steel)

    # 5. Freno de boca angular de gran calibre
    b.box((0.095, 0.10, 0.095), loc=(x_barrel, -0.86, 0.54), m=m_gunner_dark)
    # Ranuras de dispersión de gases laterales
    b.box((0.11, 0.03, 0.04), loc=(x_barrel, -0.86, 0.54), m=m_gunner_laser)
    # Salida del cañón (ánima)
    b.cyl(0.030, 0.04, loc=(x_barrel, -0.91, 0.54), rot=(90, 0, 0), m=m_gunner_dark)

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
    bg.inputs["Color"].default_value = (0.025, 0.025, 0.03, 1.0)
    bg.inputs["Strength"].default_value = 0.4

cam_data = bpy.data.cameras.new("Cam_Artillero_Adjust")
cam_obj = bpy.data.objects.new("Cam_Artillero_Adjust", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_data.lens = 45.0

empty_target = bpy.data.objects.new("Cam_Artillero_Target", None)
scene.collection.objects.link(empty_target)
empty_target.location = (0.0, -0.15, 0.45)

tt = cam_obj.constraints.new(type='TRACK_TO')
tt.target = empty_target
tt.track_axis = 'TRACK_NEGATIVE_Z'
tt.up_axis = 'UP_Y'

dist = 2.4
cam_obj.location = (dist * 0.70, -dist * 0.80, 0.45 + dist * 0.45)

# Studio Lights
key_data = bpy.data.lights.new("Light_Key_Art", type='AREA')
key_obj = bpy.data.objects.new("Light_Key_Art", key_data)
scene.collection.objects.link(key_obj)
key_data.energy = 220.0
key_data.size = 2.0
key_data.color = (0.95, 0.98, 1.0)
key_obj.location = (dist * 0.7, -dist * 0.6, 0.45 + dist * 0.9)

fill_data = bpy.data.lights.new("Light_Fill_Art", type='AREA')
fill_obj = bpy.data.objects.new("Light_Fill_Art", fill_data)
scene.collection.objects.link(fill_obj)
fill_data.energy = 70.0
fill_data.size = 3.0
fill_data.color = (0.65, 0.75, 0.90)
fill_obj.location = (-dist * 0.7, -dist * 0.6, 0.45 + dist * 0.4)

rim_data = bpy.data.lights.new("Light_Rim_Art", type='AREA')
rim_obj = bpy.data.objects.new("Light_Rim_Art", rim_data)
scene.collection.objects.link(rim_obj)
rim_data.energy = 200.0
rim_data.size = 2.0
rim_data.color = (1.0, 0.45, 0.15) # Contraluz ámbar/fuego
rim_obj.location = (-dist * 0.2, dist * 0.8, 0.45 + dist * 0.6)

out_despues = os.path.join(output_dir, "artillero_despues.png")
scene.render.filepath = out_despues
bpy.ops.render.render(write_still=True)
print(f"RENDERED REFINED ARTILLERO DESPUES -> {out_despues}")

blend_path = r"E:\Darx_Proyect\Saved\Player_Skin_Workspace\DarX_Artillero_Redesign.blend"
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f"FILE_SAVED: {blend_path}")

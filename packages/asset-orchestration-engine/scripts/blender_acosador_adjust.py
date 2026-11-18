"""darx_acosador_adjust.py — Rediseño Robótico Fiel al Original (Ente Tipo Robot)
Respeta la estética geométrica robótica del primer diseño:
- Ente robótico de combate y glitch digital con chasis angular de placas biseladas
- Cabeza robótica geométrica con visor horizontal de hendidura de código
- Chasis pectoral blindado con el icónico núcleo vertical magenta emisor
- 4 Bloques / Monolitos de glitch flotantes desarticulados orbitando hombros y flancos (2 magenta, 2 cian)
- Cuchillas robóticas geométricas de plasma montadas en antebrazos
- Piernas robóticas articuladas con juntas mecánicas de precisión y botas angulares
- Acabados PBR: aleación oscura de sigilo, acero cepillado y emisión de energía cuántica
"""

import bpy, bmesh, math, os, sys
from mathutils import Vector, Matrix, Euler

art_blender_dir = r"E:\Darx_Proyect\Art\Blender"
if art_blender_dir not in sys.path:
    sys.path.append(art_blender_dir)

import darx_lib as dl

output_dir = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"
os.makedirs(output_dir, exist_ok=True)

ARM_NAME = "ARM_Acosador"
SK_NAME = "SK_Acosador"
COL_NAME = "DARX_Acosador"
R = math.radians

# Clean Scene
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.resolution_x = 960
scene.render.resolution_y = 960
scene.render.film_transparent = False

col = dl.coll(COL_NAME)

# --------------------------------------------------------------------------
# 1. MATERIALES PBR: ENTE ROBÓTICO DIGITAL
# --------------------------------------------------------------------------
# Chasis de aleación oscura de sigilo (mate y biselado)
m_robot_chassis = dl.mat("M_Acosador_RobotChassis", (0.05, 0.05, 0.06), rough=0.25, metal=0.88)
# Mecanismos de acero cepillado y juntas
m_robot_steel = dl.mat("M_Acosador_Steel", (0.24, 0.25, 0.28), rough=0.20, metal=0.95)
# Cromo pulido para biseles y vástagos
m_robot_chrome = dl.mat("M_Acosador_Chrome", (0.86, 0.88, 0.92), rough=0.10, metal=0.98)

# Energía de Glitch y Código Digital
m_glitch_magenta = dl.mat("M_Glitch_Magenta", (0.92, 0.05, 0.95), emis=(0.92, 0.05, 0.95), emis_str=36.0)
m_glitch_cyan = dl.mat("M_Glitch_Cyan", (0.0, 0.95, 1.0), emis=(0.0, 0.95, 1.0), emis_str=38.0)

# --------------------------------------------------------------------------
# 2. ARMATURE (ENTE ROBÓTICO EN POSTURA DE COMBATE)
# --------------------------------------------------------------------------
bones = [
    ("root",            (0, 0, 0),          (0, 0, 0.35),       None,          False),
    ("pelvis",          (0, 0, 0.95),       (0, 0, 1.10),       "root",        False),
    ("spine",           (0, 0, 1.10),       (0, 0, 1.40),       "pelvis",      False),
    ("chest",           (0, 0, 1.40),       (0, 0, 1.70),       "spine",       False),
    ("head",            (0, 0, 1.70),       (0, 0, 2.02),       "chest",       False),

    # Brazo Izquierdo
    ("shoulder_l",      (-0.16, 0, 1.64),   (-0.36, 0, 1.62),   "chest",       False),
    ("arm_upper_l",     (-0.36, 0, 1.62),   (-0.46, -0.16, 1.28), "shoulder_l", False),
    ("arm_lower_l",     (-0.46, -0.16, 1.28), (-0.42, -0.38, 1.16), "arm_upper_l", False),
    ("blade_l",         (-0.42, -0.38, 1.16), (-0.38, -0.80, 1.10), "arm_lower_l", False),

    # Brazo Derecho
    ("shoulder_r",      (0.16, 0, 1.64),    (0.36, 0, 1.62),    "chest",       False),
    ("arm_upper_r",     (0.36, 0, 1.62),    (0.46, -0.16, 1.28), "shoulder_r", False),
    ("arm_lower_r",     (0.46, -0.16, 1.28), (0.42, -0.38, 1.16), "arm_upper_r", False),
    ("blade_r",         (0.42, -0.38, 1.16), (0.38, -0.80, 1.10), "arm_lower_r", False),

    # 4 Bloques de Glitch Flotantes Desarticulados (Iconos del Acosador)
    ("shard_1",         (-0.34, -0.18, 1.72), (-0.42, -0.24, 1.84), "chest",      False),
    ("shard_2",         (0.34, -0.18, 1.72),  (0.42, -0.24, 1.84),  "chest",      False),
    ("shard_3",         (-0.36, 0.16, 1.28),  (-0.44, 0.22, 1.38),  "spine",      False),
    ("shard_4",         (0.36, 0.16, 1.28),   (0.44, 0.22, 1.38),   "spine",      False),

    # Piernas Robóticas
    ("thigh_l",         (-0.16, 0, 0.95),   (-0.17, -0.06, 0.52), "pelvis",    False),
    ("calf_l",          (-0.17, -0.06, 0.52), (-0.16, 0.04, 0.16),  "thigh_l",  False),
    ("foot_l",          (-0.16, 0.04, 0.16),  (-0.16, -0.18, 0.02), "calf_l",   False),

    ("thigh_r",         (0.16, 0, 0.95),    (0.17, -0.06, 0.52),  "pelvis",    False),
    ("calf_r",          (0.17, -0.06, 0.52),  (0.16, 0.04, 0.16),   "thigh_r",   False),
    ("foot_r",          (0.16, 0.04, 0.16),   (0.16, -0.18, 0.02),  "calf_r",    False),
]
arm_obj = dl.armature(ARM_NAME, bones, COL_NAME)

# --------------------------------------------------------------------------
# 3. CONSTRUCCIÓN DE LA MALLA
# --------------------------------------------------------------------------
b = dl.MB(SK_NAME)

# =========================================================================
# PELVIS Y COLUMNA ROBÓTICA
# =========================================================================
b.bone("pelvis")
# Chasis de cadera angular facetado
b.box((0.26, 0.18, 0.14), loc=(0, 0, 0.98), m=m_robot_chassis)
b.box((0.20, 0.14, 0.08), loc=(0, 0, 0.92), m=m_robot_steel)
b.cyl(0.06, 0.08, loc=(0, 0, 1.05), rot=(0, 0, 0), m=m_robot_steel)

# Columna mecánica segmentada
b.bone("spine")
b.box((0.18, 0.15, 0.18), loc=(0, 0, 1.20), m=m_robot_chassis)
b.box((0.08, 0.02, 0.14), loc=(0, -0.08, 1.20), m=m_glitch_cyan)
b.cyl(0.07, 0.10, loc=(0, 0, 1.34), rot=(0, 0, 0), m=m_robot_steel)

# =========================================================================
# PECHO: CHASIS ROBÓTICO Y NÚCLEO VERTICAL DE GLITCH MAGENTA
# =========================================================================
b.bone("chest")
# Armadura pectoral angular con biseles limpios
b.box((0.32, 0.22, 0.28), loc=(0, 0, 1.54), m=m_robot_chassis)
b.box((0.34, 0.14, 0.16), loc=(0, -0.05, 1.54), m=m_robot_steel)

# NÚCLEO VERTICAL DE GLITCH MAGENTA (EL RASGO CENTRAL DEL ORIGINAL)
b.box((0.07, 0.04, 0.20), loc=(0, -0.12, 1.54), m=m_glitch_magenta)
b.box((0.09, 0.02, 0.22), loc=(0, -0.115, 1.54), m=m_robot_steel)

# Rejillas de ventilación y disipadores
for sign in (1, -1):
    b.box((0.04, 0.02, 0.18), loc=(sign * 0.11, -0.11, 1.54), m=m_robot_chassis)
    b.box((0.015, 0.015, 0.12), loc=(sign * 0.11, -0.125, 1.54), m=m_glitch_cyan)

# =========================================================================
# CABEZA: AUTÓMATA GEOMÉTRICO CON VISOR DE CÓDIGO
# =========================================================================
b.bone("head")
# Cuello mecánico
b.cyl(0.055, 0.08, loc=(0, 0, 1.72), rot=(0, 0, 0), m=m_robot_steel)

# Casco angular facetado (respetando la silueta geométrica del original)
b.box((0.18, 0.18, 0.20), loc=(0, -0.01, 1.86), m=m_robot_chassis)
# Mandíbula / barbilla biselada
b.box((0.14, 0.14, 0.08), loc=(0, -0.03, 1.78), m=m_robot_steel)

# Visor horizontal de código glitch (el visor icónico del diseño 1)
b.box((0.16, 0.03, 0.035), loc=(0, -0.105, 1.88), m=m_glitch_magenta)
b.box((0.12, 0.02, 0.015), loc=(0, -0.112, 1.88), m=m_glitch_cyan)

# Módulos sensoriales laterales (orejeras de procesamiento de código)
for sign in (1, -1):
    b.box((0.03, 0.10, 0.12), loc=(sign * 0.10, -0.01, 1.86), m=m_robot_steel)
    b.cyl(0.012, 0.04, loc=(sign * 0.11, -0.01, 1.90), rot=(0, 90, 0), m=m_glitch_cyan)

# =========================================================================
# 4 MONOLITOS / CUBOS DE GLITCH FLOTANTES ORBITANTES
# =========================================================================
# Superiores (Flotando cerca de hombros en magenta)
b.bone("shard_1")
b.box((0.09, 0.09, 0.14), loc=(-0.36, -0.16, 1.74), rot=(R(15), R(25), 0), m=m_robot_chassis)
b.box((0.05, 0.05, 0.16), loc=(-0.36, -0.16, 1.74), rot=(R(15), R(25), 0), m=m_glitch_magenta)

b.bone("shard_2")
b.box((0.09, 0.09, 0.14), loc=(0.36, -0.16, 1.74), rot=(R(15), R(-25), 0), m=m_robot_chassis)
b.box((0.05, 0.05, 0.16), loc=(0.36, -0.16, 1.74), rot=(R(15), R(-25), 0), m=m_glitch_magenta)

# Inferiores (Flotando cerca de flancos en cian)
b.bone("shard_3")
b.box((0.08, 0.08, 0.13), loc=(-0.36, 0.16, 1.30), rot=(R(-15), R(-20), 0), m=m_robot_chassis)
b.box((0.045, 0.045, 0.15), loc=(-0.36, 0.16, 1.30), rot=(R(-15), R(-20), 0), m=m_glitch_cyan)

b.bone("shard_4")
b.box((0.08, 0.08, 0.13), loc=(0.36, 0.16, 1.30), rot=(R(-15), R(20), 0), m=m_robot_chassis)
b.box((0.045, 0.045, 0.15), loc=(0.36, 0.16, 1.30), rot=(R(-15), R(20), 0), m=m_glitch_cyan)

# =========================================================================
# BRAZOS ROBÓTICOS Y CUCHILLAS GEOMÉTRICAS DE CÓDIGO
# =========================================================================
for side, sign in [("l", -1), ("r", 1)]:
    b.bone(f"shoulder_{side}")
    # Hombrera cúbica/angular (estética robot original)
    p_sh = (sign * 0.28, 0, 1.63)
    b.box((0.14, 0.14, 0.12), loc=p_sh, rot=(0, sign * 15, 0), m=m_robot_chassis)
    b.cyl(0.045, 0.05, loc=(sign * 0.20, 0, 1.63), rot=(0, 90, 0), m=m_robot_steel)

    # Brazo Superior
    b.bone(f"arm_upper_{side}")
    p_elbow = (sign * 0.46, -0.16, 1.28)
    b.seg((sign * 0.28, 0, 1.63), p_elbow, 0.055, 0.045, m=m_robot_chassis, seg=8, smooth=False)
    b.box((0.09, 0.09, 0.16), loc=(sign * 0.38, -0.08, 1.45), rot=(15, sign * 20, 0), m=m_robot_chassis)
    b.cyl(0.045, 0.08, loc=p_elbow, rot=(90, 0, 0), m=m_robot_steel)

    # Antebrazo
    b.bone(f"arm_lower_{side}")
    p_wrist = (sign * 0.42, -0.38, 1.16)
    b.seg(p_elbow, p_wrist, 0.048, 0.040, m=m_robot_chassis, seg=8, smooth=False)
    b.box((0.08, 0.16, 0.08), loc=((p_elbow[0] + p_wrist[0])/2, (p_elbow[1] + p_wrist[1])/2, (p_elbow[2] + p_wrist[2])/2),
          rot=(20, sign * 10, 0), m=m_robot_chassis)

    # CUCHILLA ROBÓTICA GEOMÉTRICA DE PLASMA (COMO LA ORIGINAL PERO CON FILO Y BISEL)
    b.bone(f"blade_{side}")
    p_blade_tip = (sign * 0.38, -0.80, 1.10)
    # Espina de la cuchilla rectangular estilizada
    b.seg(p_wrist, p_blade_tip, 0.035, 0.015, m=m_robot_chassis, seg=8, smooth=False)
    # Filo luminoso de plasma cian cuántico
    b.box((0.015, 0.38, 0.04), loc=(sign * 0.40, -0.58, 1.13), rot=(8, sign * 5, 0), m=m_glitch_cyan)
    b.box((0.008, 0.32, 0.02), loc=(sign * 0.40, -0.58, 1.13), rot=(8, sign * 5, 0), m=m_glitch_magenta)

# =========================================================================
# PIERNAS Y BOTAS ROBÓTICAS ANGULARES
# =========================================================================
for side, sign in [("l", -1), ("r", 1)]:
    b.bone(f"thigh_{side}")
    p_hip = (sign * 0.16, 0, 0.95)
    p_knee = (sign * 0.17, -0.06, 0.52)
    b.seg(p_hip, p_knee, 0.085, 0.070, m=m_robot_chassis, seg=8, smooth=False)
    b.box((0.12, 0.14, 0.22), loc=(sign * 0.165, -0.03, 0.74), rot=(10, sign * 5, 0), m=m_robot_chassis)
    # Articulación de rodilla mecánica
    b.cyl(0.060, 0.09, loc=p_knee, rot=(0, 90, 0), m=m_robot_steel)

    b.bone(f"calf_{side}")
    p_ankle = (sign * 0.16, 0.04, 0.16)
    b.seg(p_knee, p_ankle, 0.070, 0.055, m=m_robot_chassis, seg=8, smooth=False)
    b.box((0.11, 0.13, 0.22), loc=(sign * 0.165, 0.00, 0.34), rot=(-8, sign * 5, 0), m=m_robot_chassis)
    b.box((0.02, 0.02, 0.14), loc=(sign * 0.165, -0.07, 0.34), rot=(-8, sign * 5, 0), m=m_glitch_cyan)

    # BOTA ROBÓTICA ANGULAR (ESTÉTICA MECÁNICA SÓLIDA)
    b.bone(f"foot_{side}")
    p_toe = (sign * 0.16, -0.18, 0.02)
    b.box((0.11, 0.18, 0.07), loc=(sign * 0.16, -0.08, 0.06), rot=(12, 0, 0), m=m_robot_chassis)
    b.box((0.09, 0.10, 0.04), loc=p_toe, rot=(12, 0, 0), m=m_robot_steel)

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
    bg.inputs["Color"].default_value = (0.02, 0.02, 0.03, 1.0)
    bg.inputs["Strength"].default_value = 0.4

cam_data = bpy.data.cameras.new("Cam_Acosador_Robot")
cam_obj = bpy.data.objects.new("Cam_Acosador_Robot", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_data.lens = 45.0

empty_target = bpy.data.objects.new("Cam_Acosador_Target", None)
scene.collection.objects.link(empty_target)
empty_target.location = (0.0, -0.15, 1.10)

tt = cam_obj.constraints.new(type='TRACK_TO')
tt.target = empty_target
tt.track_axis = 'TRACK_NEGATIVE_Z'
tt.up_axis = 'UP_Y'

dist = 3.6
cam_obj.location = (dist * 0.65, -dist * 0.85, 1.10 + dist * 0.25)

# Studio Lights
key_data = bpy.data.lights.new("Light_Key_Aco", type='AREA')
key_obj = bpy.data.objects.new("Light_Key_Aco", key_data)
scene.collection.objects.link(key_obj)
key_data.energy = 240.0
key_data.size = 2.5
key_data.color = (0.95, 0.98, 1.0)
key_obj.location = (dist * 0.7, -dist * 0.6, 1.10 + dist * 0.8)

fill_data = bpy.data.lights.new("Light_Fill_Aco", type='AREA')
fill_obj = bpy.data.objects.new("Light_Fill_Aco", fill_data)
scene.collection.objects.link(fill_obj)
fill_data.energy = 70.0
fill_data.size = 3.5
fill_data.color = (0.85, 0.10, 0.95)
fill_obj.location = (-dist * 0.7, -dist * 0.6, 1.10 + dist * 0.4)

rim_data = bpy.data.lights.new("Light_Rim_Aco", type='AREA')
rim_obj = bpy.data.objects.new("Light_Rim_Aco", rim_data)
scene.collection.objects.link(rim_obj)
rim_data.energy = 260.0
rim_data.size = 2.5
rim_data.color = (0.0, 0.95, 1.0)
rim_obj.location = (-dist * 0.2, dist * 0.8, 1.10 + dist * 0.6)

out_despues = os.path.join(output_dir, "acosador_despues.png")
scene.render.filepath = out_despues
bpy.ops.render.render(write_still=True)
print(f"RENDERED ROBOT ACOSADOR DESPUES -> {out_despues}")

blend_path = r"E:\Darx_Proyect\Saved\Player_Skin_Workspace\DarX_Acosador_Redesign.blend"
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f"FILE_SAVED: {blend_path}")

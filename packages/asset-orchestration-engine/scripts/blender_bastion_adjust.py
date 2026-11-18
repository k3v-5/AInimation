"""darx_bastion_adjust.py — Rediseño Completo de El Bastión (SK_Bastion_SWAT)
Coloso SWAT Blindado de Intervención Pesada:
- Escudo balístico de 3 paneles angulares con visera de policarbonato reforzada con rejilla
- Focos tácticos estroboscópicos de aturdimiento y ariete de choque inferior
- Casco táctico pesado con visor ámbar estrecho y respirador lateral
- Hombreras balísticas sobredimensionadas y coraza de Kevlar/titanio
- Guanteletes mecánicos de alta presión anclados a los asideros traseros del escudo
- Piernas pesadas con rodilleras de cuña y botas sísmicas de alta tracción
- Offset de seguridad >= 60cm en el escudo (cero clipping estricto garantizado)
"""

import bpy, bmesh, math, os, sys
from mathutils import Vector, Matrix, Euler

art_blender_dir = r"E:\Darx_Proyect\Art\Blender"
if art_blender_dir not in sys.path:
    sys.path.append(art_blender_dir)

import darx_lib as dl

output_dir = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"
os.makedirs(output_dir, exist_ok=True)

ARM_NAME = "ARM_Bastion"
SK_NAME = "SK_Bastion_SWAT"
COL_NAME = "DARX_Bastion"
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
# Blindaje compuesto en titanio táctico oscuro
m_armor_dark = dl.mat("M_Bastion_ArmorDark", (0.06, 0.06, 0.08), rough=0.28, metal=0.88)
# Acero templado para biseles, remaches y asideros
m_armor_steel = dl.mat("M_Bastion_Steel", (0.24, 0.25, 0.28), rough=0.20, metal=0.95)
m_armor_chrome = dl.mat("M_Bastion_Chrome", (0.86, 0.88, 0.92), rough=0.10, metal=0.98)

# Visor SWAT y Focos Estroboscópicos
m_visor_amber = dl.mat("M_Visor_SWAT", (1.0, 0.50, 0.05), emis=(1.0, 0.50, 0.05), emis_str=34.0)
m_shield_glass = dl.mat("M_Shield_Glass", (0.10, 0.50, 0.60), rough=0.08, metal=0.15, emis=(0.10, 0.50, 0.60), emis_str=8.0)
m_strobe_white = dl.mat("M_Strobe_Light", (1.0, 0.95, 0.88), emis=(1.0, 0.95, 0.88), emis_str=42.0)
m_strobe_red = dl.mat("M_Strobe_Red", (1.0, 0.05, 0.02), emis=(1.0, 0.05, 0.02), emis_str=38.0)

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

    pelvis = eb.new("pelvis")
    pelvis.parent = root
    pelvis.head = (0, 0.06, 1.05)
    pelvis.tail = (0, 0.06, 1.22)

    spine = eb.new("spine")
    spine.parent = pelvis
    spine.head = (0, 0.06, 1.22)
    spine.tail = (0, 0.06, 1.55)

    chest = eb.new("chest")
    chest.parent = spine
    chest.head = (0, 0.06, 1.55)
    chest.tail = (0, 0.04, 1.86)

    head = eb.new("head")
    head.parent = chest
    head.head = (0, 0.02, 1.86)
    head.tail = (0, 0.00, 2.18)

    # ESCUDO BALÍSTICO (Anclado rígidamente al pecho con offset seguro Y = -0.68)
    shield = eb.new("shield_bone")
    shield.parent = chest
    shield.head = (0, -0.68, 1.05)
    shield.tail = (0, -0.68, 1.88)

    # Brazo Izquierdo (Sujeción principal del escudo)
    sh_l = eb.new("shoulder_L")
    sh_l.parent = chest
    sh_l.head = (-0.28, 0.06, 1.80)
    sh_l.tail = (-0.46, 0.04, 1.74)

    arm_l = eb.new("upperarm_L")
    arm_l.parent = sh_l
    arm_l.head = (-0.46, 0.04, 1.74)
    arm_l.tail = (-0.38, -0.26, 1.40)

    hand_l = eb.new("hand_L")
    hand_l.parent = arm_l
    hand_l.head = (-0.38, -0.26, 1.40)
    hand_l.tail = (-0.26, -0.56, 1.32)

    # Brazo Derecho (Soporte y pistón de choque)
    sh_r = eb.new("shoulder_R")
    sh_r.parent = chest
    sh_r.head = (0.28, 0.06, 1.80)
    sh_r.tail = (0.46, 0.04, 1.74)

    arm_r = eb.new("upperarm_R")
    arm_r.parent = sh_r
    arm_r.head = (0.46, 0.04, 1.74)
    arm_r.tail = (0.38, -0.26, 1.40)

    hand_r = eb.new("hand_R")
    hand_r.parent = arm_r
    hand_r.head = (0.38, -0.26, 1.40)
    hand_r.tail = (0.26, -0.56, 1.32)

    # Piernas
    th_l = eb.new("thigh_L")
    th_l.parent = pelvis
    th_l.head = (-0.22, 0.06, 1.05)
    th_l.tail = (-0.24, 0.02, 0.54)

    calf_l = eb.new("calf_L")
    calf_l.parent = th_l
    calf_l.head = (-0.24, 0.02, 0.54)
    calf_l.tail = (-0.22, 0.04, 0.16)

    foot_l = eb.new("foot_L")
    foot_l.parent = calf_l
    foot_l.head = (-0.22, 0.04, 0.16)
    foot_l.tail = (-0.22, -0.18, 0.0)

    th_r = eb.new("thigh_R")
    th_r.parent = pelvis
    th_r.head = (0.22, 0.06, 1.05)
    th_r.tail = (0.24, 0.02, 0.54)

    calf_r = eb.new("calf_R")
    calf_r.parent = th_r
    calf_r.head = (0.24, 0.02, 0.54)
    calf_r.tail = (0.22, 0.04, 0.16)

    foot_r = eb.new("foot_R")
    foot_r.parent = calf_r
    foot_r.head = (0.22, 0.04, 0.16)
    foot_r.tail = (0.22, -0.18, 0.0)

    bpy.ops.object.mode_set(mode='OBJECT')
    return arm_obj

arm_obj = build_rig()

# --------------------------------------------------------------------------
# 3. CONSTRUCCIÓN DE LA MALLA
# --------------------------------------------------------------------------
b = dl.MB(SK_NAME)

# =========================================================================
# ESCUDO BALÍSTICO SWAT PESADO (Y = -0.68, BUFFER DE SEGURIDAD GARANTIZADO)
# =========================================================================
b.bone("shield_bone")

# 1. Panel Central del Escudo (Ancho 0.82m, Alto 1.48m, Grueso 0.08m)
b.box((0.82, 0.08, 1.48), loc=(0, -0.68, 1.14), m=m_armor_dark)

# 2. Chaflanes Laterales Doblados hacia Atrás a 25°
for sign in (1, -1):
    x_chaflan = sign * 0.53
    y_chaflan = -0.68 + 0.05
    b.box((0.26, 0.07, 1.48), loc=(x_chaflan, y_chaflan, 1.14), rot=(0, 0, sign * R(-24)), m=m_armor_dark)
    # Refuerzo perimetral en acero
    b.box((0.04, 0.09, 1.50), loc=(sign * 0.64, y_chaflan + 0.04, 1.14), rot=(0, 0, sign * R(-24)), m=m_armor_steel)

# 3. Marcos de Refuerzo Superior e Inferior
b.box((0.88, 0.11, 0.09), loc=(0, -0.68, 1.86), m=m_armor_steel)
b.box((0.88, 0.11, 0.09), loc=(0, -0.68, 0.42), m=m_armor_steel)

# 4. Ventana de Policarbonato Balístico Tintado y Rejilla
b.box((0.54, 0.10, 0.22), loc=(0, -0.68, 1.64), m=m_shield_glass)
b.box((0.58, 0.12, 0.03), loc=(0, -0.68, 1.75), m=m_armor_steel)
b.box((0.58, 0.12, 0.03), loc=(0, -0.68, 1.53), m=m_armor_steel)
for x_bar in (-0.20, -0.10, 0.0, 0.10, 0.20):
    b.box((0.02, 0.12, 0.22), loc=(x_bar, -0.68, 1.64), m=m_armor_steel)

# 5. Focos Tácticos Estroboscópicos de Aturdimiento
b.box((0.14, 0.06, 0.08), loc=(-0.24, -0.72, 1.86), m=m_strobe_white)
b.box((0.14, 0.06, 0.08), loc=(0.24, -0.72, 1.86), m=m_strobe_red)

# 6. Ariete de Choque Inferior (Dientes de acero para impacto)
b.box((0.84, 0.14, 0.08), loc=(0, -0.68, 0.36), m=m_armor_steel)
for x_spike in (-0.30, -0.15, 0.0, 0.15, 0.30):
    b.prism(0.06, 0.08, 0.07, loc=(x_spike, -0.74, 0.36), rot=(90, 0, 0), taper=0.2, m=m_armor_steel)

# 7. Asideros Hidráulicos Posteriores
for sign in (1, -1):
    b.cyl(0.028, 0.24, loc=(sign * 0.24, -0.56, 1.34), rot=(0, 90, 0), m=m_armor_chrome)
    b.box((0.06, 0.12, 0.06), loc=(sign * 0.12, -0.60, 1.34), m=m_armor_steel)
    b.box((0.06, 0.12, 0.06), loc=(sign * 0.36, -0.60, 1.34), m=m_armor_steel)

# =========================================================================
# COLOSO SWAT: CABEZA Y CASCO TÁCTICO REFORZADO
# =========================================================================
b.bone("head")
# Cuello protegido
b.cyl(0.08, 0.10, loc=(0, 0.02, 1.88), rot=(0, 0, 0), m=m_armor_dark)

# Casco balístico modular
b.box((0.30, 0.28, 0.26), loc=(0, 0.02, 2.02), m=m_armor_dark)
# Cúpula de refuerzo superior
b.box((0.26, 0.26, 0.06), loc=(0, 0.02, 2.16), m=m_armor_steel)

# Visera frontal táctica en ángulo
b.box((0.28, 0.08, 0.04), loc=(0, -0.13, 2.08), rot=(15, 0, 0), m=m_armor_steel)

# Visor horizontal ámbar SWAT
b.box((0.22, 0.04, 0.045), loc=(0, -0.13, 2.02), m=m_visor_amber)

# Respirador táctico / filtro cilíndrico lateral
b.cyl(0.040, 0.08, loc=(0.14, -0.08, 1.94), rot=(0, 90, 20), m=m_armor_steel)
b.box((0.14, 0.08, 0.06), loc=(0, -0.12, 1.94), m=m_armor_dark)

# =========================================================================
# PECHO Y CORAZA DEL COLOSO
# =========================================================================
b.bone("chest")
# Pectoral masivo de aleación
b.box((0.56, 0.36, 0.44), loc=(0, 0.06, 1.62), m=m_armor_dark)
# Placa frontal de refuerzo Kevlar/titanio
b.box((0.44, 0.08, 0.32), loc=(0, -0.11, 1.62), m=m_armor_steel)

# Insignia de advertencia / núcleo táctico ámbar
b.box((0.12, 0.02, 0.18), loc=(0, -0.155, 1.62), m=m_visor_amber)

# =========================================================================
# HOMBROS Y BRAZOS PESADOS (SUJECIÓN RÍGIDA DEL ESCUDO)
# =========================================================================
for side, sign in [("L", -1), ("R", 1)]:
    b.bone(f"shoulder_{side}")
    # Hombrera balística sobredimensionada de triple placa
    b.box((0.22, 0.28, 0.16), loc=(sign * 0.38, 0.05, 1.78), rot=(0, sign * 14, 0), m=m_armor_steel)
    b.box((0.18, 0.24, 0.06), loc=(sign * 0.40, 0.05, 1.87), rot=(0, sign * 14, 0), m=m_armor_dark)

    # Brazo Superior
    b.bone(f"upperarm_{side}")
    p_shoulder = (sign * 0.46, 0.04, 1.74)
    p_elbow = (sign * 0.38, -0.26, 1.40)
    b.seg(p_shoulder, p_elbow, 0.080, 0.070, m=m_armor_dark, seg=10, smooth=False)
    b.cyl(0.065, 0.08, loc=p_elbow, rot=(90, 0, 0), m=m_armor_steel)

    # Antebrazo y Guantelete Blindado
    b.bone(f"hand_{side}")
    p_wrist = (sign * 0.26, -0.56, 1.32)
    b.seg(p_elbow, p_wrist, 0.070, 0.060, m=m_armor_dark, seg=10, smooth=False)
    # Guantelete mecánico reforzado que agarra el asidero
    b.box((0.12, 0.16, 0.12), loc=(sign * 0.26, -0.54, 1.33), m=m_armor_steel)
    b.cyl(0.035, 0.14, loc=(sign * 0.26, -0.56, 1.34), rot=(0, 90, 0), m=m_armor_chrome)

# =========================================================================
# PELVIS, PIERNAS Y BOTAS SÍSMICAS
# =========================================================================
b.bone("pelvis")
b.box((0.48, 0.32, 0.18), loc=(0, 0.06, 1.12), m=m_armor_dark)
b.box((0.50, 0.34, 0.06), loc=(0, 0.06, 1.19), m=m_armor_steel)

for side, sign in [("L", -1), ("R", 1)]:
    b.bone(f"thigh_{side}")
    p_hip = (sign * 0.22, 0.06, 1.05)
    p_knee = (sign * 0.24, 0.02, 0.54)
    b.seg(p_hip, p_knee, 0.110, 0.090, m=m_armor_dark, seg=12, smooth=False)
    # Placa femoral
    b.box((0.16, 0.18, 0.26), loc=(sign * 0.23, 0.02, 0.78), rot=(5, sign * 4, 0), m=m_armor_steel)

    # Rótula en cuña de protección pesada
    b.box((0.13, 0.10, 0.12), loc=(sign * 0.24, -0.06, 0.54), rot=(15, sign * 4, 0), m=m_armor_steel)
    b.cyl(0.065, 0.12, loc=p_knee, rot=(0, 90, 0), m=m_armor_steel)

    b.bone(f"calf_{side}")
    p_ankle = (sign * 0.22, 0.04, 0.16)
    b.seg(p_knee, p_ankle, 0.090, 0.075, m=m_armor_dark, seg=10, smooth=False)
    # Espinillera balística
    b.box((0.14, 0.16, 0.24), loc=(sign * 0.22, -0.02, 0.34), m=m_armor_steel)

    # BOTA SÍSMICA PESADA
    b.bone(f"foot_{side}")
    p_toe = (sign * 0.22, -0.18, 0.04)
    b.box((0.16, 0.26, 0.10), loc=(sign * 0.22, -0.06, 0.08), m=m_armor_steel)
    b.box((0.14, 0.12, 0.08), loc=p_toe, m=m_armor_dark)
    # Suela de alta tracción
    b.box((0.18, 0.30, 0.03), loc=(sign * 0.22, -0.08, 0.02), m=m_armor_dark)

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

cam_data = bpy.data.cameras.new("Cam_Bastion_Adjust")
cam_obj = bpy.data.objects.new("Cam_Bastion_Adjust", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_data.lens = 45.0

empty_target = bpy.data.objects.new("Cam_Bastion_Target", None)
scene.collection.objects.link(empty_target)
empty_target.location = (0.0, -0.25, 1.25)

tt = cam_obj.constraints.new(type='TRACK_TO')
tt.target = empty_target
tt.track_axis = 'TRACK_NEGATIVE_Z'
tt.up_axis = 'UP_Y'

dist = 3.6
cam_obj.location = (dist * 0.70, -dist * 0.85, 1.25 + dist * 0.25)

# Studio Lights
key_data = bpy.data.lights.new("Light_Key_Bas", type='AREA')
key_obj = bpy.data.objects.new("Light_Key_Bas", key_data)
scene.collection.objects.link(key_obj)
key_data.energy = 280.0
key_data.size = 2.5
key_data.color = (0.95, 0.98, 1.0)
key_obj.location = (dist * 0.7, -dist * 0.6, 1.25 + dist * 0.8)

fill_data = bpy.data.lights.new("Light_Fill_Bas", type='AREA')
fill_obj = bpy.data.objects.new("Light_Fill_Bas", fill_data)
scene.collection.objects.link(fill_obj)
fill_data.energy = 90.0
fill_data.size = 3.5
fill_data.color = (0.65, 0.75, 0.90)
fill_obj.location = (-dist * 0.7, -dist * 0.6, 1.25 + dist * 0.4)

rim_data = bpy.data.lights.new("Light_Rim_Bas", type='AREA')
rim_obj = bpy.data.objects.new("Light_Rim_Bas", rim_data)
scene.collection.objects.link(rim_obj)
rim_data.energy = 240.0
rim_data.size = 2.5
rim_data.color = (1.0, 0.50, 0.10) # Contraluz ámbar táctico
rim_obj.location = (-dist * 0.2, dist * 0.8, 1.25 + dist * 0.6)

out_despues = os.path.join(output_dir, "bastion_despues.png")
scene.render.filepath = out_despues
bpy.ops.render.render(write_still=True)
print(f"RENDERED REFINED BASTION DESPUES -> {out_despues}")

blend_path = r"E:\Darx_Proyect\Saved\Player_Skin_Workspace\DarX_Bastion_Redesign.blend"
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f"FILE_SAVED: {blend_path}")

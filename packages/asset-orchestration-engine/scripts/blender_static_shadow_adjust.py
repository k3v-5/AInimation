"""darx_static_shadow_adjust.py — Rediseño TERRORÍFICO de La Sombra Estática (SK_StaticShadow)
Ajuste solicitado por el usuario: "Mejoralo aun mas, que de miedo"
- Silueta espectral cadavérica con brazos alargados y garras de aguja hiperafiladas
- Jaula torácica con costillas angulares expuestas como fauces biomecánicas envolviendo el núcleo
- Cráneo cadavérico de grafeno con fracturas de ruido estático analógico y mandíbula desencajada de fósforo blanco
- Espina dorsal con vértebras punzantes sobresaliendo como púas biomecánicas
- Fragmentos flotantes de código corrupto y espolones afilados en extremidades inferiores
"""

import bpy, bmesh, math, os, sys
from mathutils import Vector, Matrix, Euler

art_blender_dir = r"E:\Darx_Proyect\Art\Blender"
if art_blender_dir not in sys.path:
    sys.path.append(art_blender_dir)

import darx_lib as dl

output_dir = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"
os.makedirs(output_dir, exist_ok=True)

ARM_NAME = "ARM_StaticShadow"
SK_NAME = "SK_StaticShadow"
COL_NAME = "DARX_StaticShadow"
R = math.radians

# Clean Scene
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.resolution_x = 960
scene.render.resolution_y = 960
scene.render.film_transparent = False

col = dl.coll(COL_NAME)

# --------------------------------------------------------------------------
# 1. MATERIALES PBR TERRORÍFICOS: GRAFENO OBSIDIANA, RUIDO BLANCO Y NEÓN CORRUPTO
# --------------------------------------------------------------------------
m_graph = dl.mat("M_Shadow_Graphene", (0.012, 0.014, 0.018), rough=0.16, metal=0.96)
m_bone = dl.mat("M_Shadow_BonePlate", (0.18, 0.20, 0.22), rough=0.28, metal=0.82)
m_prism = dl.mat("M_Shadow_Prism", (0.05, 0.08, 0.12), rough=0.08, metal=0.92)

# Emisiones de Terror Analógico y Glitch
m_cyan = dl.mat("M_Shadow_GlitchCyan", (0.0, 0.95, 1.0), emis=(0.0, 0.95, 1.0), emis_str=46.0)
m_mag = dl.mat("M_Shadow_GlitchMagenta", (0.95, 0.05, 0.85), emis=(0.95, 0.05, 0.85), emis_str=46.0)
m_noise = dl.mat("M_Shadow_WhiteNoise", (1.0, 1.0, 1.0), emis=(1.0, 1.0, 1.0), emis_str=52.0)
m_blood = dl.mat("M_Shadow_BloodNeon", (1.0, 0.02, 0.04), emis=(1.0, 0.02, 0.04), emis_str=40.0)

# --------------------------------------------------------------------------
# 2. ARMATURE (PROPORCIONES ALARGADAS Y AMENAZANTES)
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
    pelvis.head = (0, 0, 0.90)
    pelvis.tail = (0, 0, 1.15)

    spine = eb.new("spine")
    spine.parent = pelvis
    spine.head = (0, 0, 1.15)
    spine.tail = (0, 0, 1.52)

    head = eb.new("head")
    head.parent = spine
    head.head = (0, 0, 1.55)
    head.tail = (0, 0, 1.92)

    core = eb.new("core")
    core.parent = spine
    core.head = (0, 0, 1.32)
    core.tail = (0, -0.22, 1.32)

    # Brazos alargados y cadavéricos
    sh_l = eb.new("upperarm_L")
    sh_l.parent = spine
    sh_l.head = (0.24, 0, 1.48)
    sh_l.tail = (0.46, 0, 1.10)

    hand_l = eb.new("hand_L")
    hand_l.parent = sh_l
    hand_l.head = (0.46, 0, 1.10)
    hand_l.tail = (0.54, -0.22, 0.70)

    sh_r = eb.new("upperarm_R")
    sh_r.parent = spine
    sh_r.head = (-0.24, 0, 1.48)
    sh_r.tail = (-0.46, 0, 1.10)

    hand_r = eb.new("hand_R")
    hand_r.parent = sh_r
    hand_r.head = (-0.46, 0, 1.10)
    hand_r.tail = (-0.54, -0.22, 0.70)

    thigh_l = eb.new("thigh_L")
    thigh_l.parent = pelvis
    thigh_l.head = (0.16, 0, 0.90)
    thigh_l.tail = (0.18, 0, 0.45)

    foot_l = eb.new("foot_L")
    foot_l.parent = thigh_l
    foot_l.head = (0.18, 0, 0.45)
    foot_l.tail = (0.20, -0.14, 0.02)

    thigh_r = eb.new("thigh_R")
    thigh_r.parent = pelvis
    thigh_r.head = (-0.16, 0, 0.90)
    thigh_r.tail = (-0.18, 0, 0.45)

    foot_r = eb.new("foot_R")
    foot_r.parent = thigh_r
    foot_r.head = (-0.18, 0, 0.45)
    foot_r.tail = (-0.20, -0.14, 0.02)

    bpy.ops.object.mode_set(mode='OBJECT')
    return arm_obj

arm_obj = build_rig()

# --------------------------------------------------------------------------
# 3. CONSTRUCCIÓN DE LA MALLA
# --------------------------------------------------------------------------
b = dl.MB(SK_NAME)

# =========================================================================
# CABEZA: CRÁNEO CADAVÉRICO DE HORROR ANALÓGICO
# =========================================================================
b.bone("head")
# Cuello alargado y tenso con tendones mecánicos
b.cyl(0.055, 0.16, loc=(0, 0, 1.54), rot=(0, 0, 0), m=m_graph)
for sign in (1, -1):
    b.cyl(0.015, 0.15, loc=(sign * 0.04, -0.02, 1.54), rot=(0, 0, 0), m=m_cyan)

# Cráneo biselado afilado cadavérico (prisma elongado con cuernos fracturados)
b.prism(0.20, 0.22, 0.32, loc=(0, -0.02, 1.74), taper=0.65, m=m_graph)
b.prism(0.22, 0.12, 0.14, loc=(0, -0.08, 1.88), taper=0.20, m=m_bone)

# CUERNOS ASIMÉTRICOS DE GLITCH SALIENDO DEL CRÁNEO
b.prism(0.04, 0.06, 0.22, loc=(0.11, 0.06, 1.94), rot=(R(25), R(20), 0), taper=0.1, m=m_prism)
b.prism(0.035, 0.05, 0.18, loc=(-0.10, 0.05, 1.90), rot=(R(30), R(-15), 0), taper=0.1, m=m_prism)

# MANDÍBULA DESENCAJADA CON RUIDO DE ESTÁTICA BLANCA (SONRISA / FAUCE ANALÓGICA)
b.box((0.18, 0.05, 0.04), loc=(0, -0.13, 1.62), m=m_noise)
# Dientes / filamentos de ruido analógico
for dx in (-0.06, -0.02, 0.02, 0.06):
    b.box((0.012, 0.02, 0.035), loc=(dx, -0.14, 1.64), m=m_bone)

# HENDIDURAS OCULARES VACÍAS CON RESPLANDOR CARMESÍ SANGRIENTO
for sign in (1, -1):
    b.box((0.05, 0.03, 0.018), loc=(sign * 0.06, -0.13, 1.76), rot=(0, 0, sign * 15), m=m_blood)
    b.sph(0.018, loc=(sign * 0.06, -0.13, 1.76), m=m_noise, smooth=True)

# Cresta sagital de fósforo cian
b.box((0.015, 0.16, 0.04), loc=(0, 0.02, 1.84), m=m_cyan)

# =========================================================================
# TORSO: COSTILLAS EN FAUCES ABIERTAS Y ESPINA DORSAL PUNZANTE
# =========================================================================
b.bone("spine")
# Columna vertebral torácica angosta
b.prism(0.36, 0.24, 0.26, loc=(0, 0, 1.48), taper=1.14, m=m_graph)
b.prism(0.28, 0.20, 0.20, loc=(0, 0, 1.30), taper=0.88, m=m_prism)

# COSTILLAS CADAVÉRICAS EN FAUCES ENVOLVENTES (ABIERTA AL FRENTE)
for sign in (1, -1):
    for z_c, l_w, curv in [(1.46, 0.25, 20), (1.38, 0.23, 24), (1.30, 0.20, 28)]:
        # Costilla de grafeno curvada hacia adelante como garras envolventes
        b.box((0.035, 0.14, 0.030), loc=(sign * l_w, -0.04, z_c), rot=(0, sign * curv, 0), m=m_bone)
        b.prism(0.025, 0.040, 0.08, loc=(sign * (l_w - 0.06), -0.12, z_c), rot=(R(90), 0, sign * R(-40)), taper=0.1, m=m_cyan)

# ESPINA DORSAL CON VÉRTEBRAS PUNZANTES SOBRESALIENTES (ESTILO DEMONIACO)
for z_v, l_spike in [(1.26, 0.14), (1.36, 0.18), (1.46, 0.20), (1.54, 0.16)]:
    b.prism(0.035, 0.035, l_spike, loc=(0, 0.14, z_v), rot=(R(-55), 0, 0), taper=0.1, m=m_prism)
    b.sph(0.018, loc=(0, 0.18, z_v), m=m_mag, smooth=True)

# FRAGMENTOS DE GLITCH FLOTANTES Y ASIMÉTRICOS
b.box((0.06, 0.06, 0.06), loc=(0.34, -0.18, 1.42), rot=(20, 35, 45), m=m_noise)
b.box((0.04, 0.05, 0.10), loc=(-0.32, 0.16, 1.36), rot=(40, -30, 15), m=m_blood)
b.box((0.04, 0.08, 0.04), loc=(0.30, 0.20, 1.22), rot=(-20, 50, -40), m=m_mag)
b.box((0.03, 0.03, 0.05), loc=(-0.26, -0.16, 1.26), rot=(15, -45, 30), m=m_cyan)

# =========================================================================
# NÚCLEO DE SINGULARIDAD DE FASE (CORAZÓN CORRUPTO)
# =========================================================================
b.bone("core")
# Cavidad profunda torácica
b.prism(0.18, 0.18, 0.24, loc=(0, -0.06, 1.32), rot=(R(180), 0, 0), taper=0.2, m=m_graph)

# VÓRTICE DE SINGULARIDAD CUÁNTICA: NÚCLEO BICOLOR SANGRE Y CIAN
b.sph(0.080, loc=(0, -0.08, 1.32), m=m_blood, u=20, v=12, smooth=True)
b.sph(0.050, loc=(0, -0.09, 1.32), m=m_noise, u=16, v=8, smooth=True)
b.cyl(0.105, 0.015, loc=(0, -0.08, 1.32), rot=(R(90), 0, 0), m=m_cyan, seg=16)

# =========================================================================
# PELVIS CADAVÉRICA
# =========================================================================
b.bone("pelvis")
b.prism(0.34, 0.20, 0.20, loc=(0, 0, 1.02), taper=0.55, m=m_graph)
b.box((0.16, 0.06, 0.12), loc=(0, -0.10, 1.02), m=m_bone)
b.box((0.10, 0.03, 0.06), loc=(0, -0.13, 1.02), m=m_noise)
b.box((0.26, 0.04, 0.02), loc=(0, -0.11, 0.95), m=m_mag)

# =========================================================================
# BRAZOS ALARGADOS Y GARRAS DE AGUJA DESPROPORCIONADAS
# =========================================================================
for side, sign in [("L", 1), ("R", -1)]:
    b.bone(f"upperarm_{side}")
    # Hombro puntiagudo fracturado
    b.prism(0.16, 0.18, 0.18, loc=(sign * 0.30, 0, 1.50), rot=(0, sign * R(22), 0), taper=0.2, m=m_prism)
    b.box((0.025, 0.12, 0.025), loc=(sign * 0.35, 0, 1.56), m=m_blood)

    # Brazo superior delgado cadavérico
    p_sh = (sign * 0.35, 0, 1.34)
    p_el = (sign * 0.44, -0.04, 1.12)
    b.seg(p_sh, p_el, 0.055, 0.042, m=m_graph, seg=8, smooth=False)
    b.cyl(0.045, 0.06, loc=p_el, rot=(90, 0, 0), m=m_bone)
    # Filamento de plasma tenso en el codo
    b.box((0.015, 0.03, 0.22), loc=(sign * 0.40, -0.02, 1.23), rot=(0, sign * 12, 0), m=m_cyan)

    # ANTEBRAZO Y GARRAS DE AGUJA LARGAS
    b.bone(f"hand_{side}")
    p_wr = (sign * 0.48, -0.12, 0.92)
    b.seg(p_el, p_wr, 0.046, 0.038, m=m_graph, seg=8, smooth=False)
    b.box((0.08, 0.08, 0.12), loc=p_wr, m=m_bone)

    # 4 GARRAS DE AGUJA ENORMES Y DESIGUALES (ESTILO NIGHTMARE / SLENDER)
    claw_params = [
        (-0.04, 0.26, m_cyan),
        (-0.01, 0.32, m_noise),
        (0.02,  0.28, m_mag),
        (0.05,  0.20, m_blood)
    ]
    for dy_c, len_c, mat_c in claw_params:
        p_c_base = (p_wr[0] + sign * dy_c, p_wr[1] - 0.06, p_wr[2] - 0.04)
        p_c_tip = (p_wr[0] + sign * (dy_c * 1.6), p_wr[1] - 0.16, p_wr[2] - len_c)
        b.seg(p_c_base, p_c_tip, 0.022, 0.005, m=mat_c, seg=6, smooth=True)

# =========================================================================
# PIERNAS Y ESPOLONES DE AGUJA DIGITÍGRADOS
# =========================================================================
for side, sign in [("L", 1), ("R", -1)]:
    b.bone(f"thigh_{side}")
    # Muslo alargado y fibroso
    b.prism(0.13, 0.14, 0.44, loc=(sign * 0.17, 0, 0.68), taper=0.62, m=m_graph)
    b.box((0.02, 0.04, 0.32), loc=(sign * 0.19, -0.06, 0.68), m=m_cyan)
    b.sph(0.042, loc=(sign * 0.18, 0, 0.46), m=m_bone, smooth=True)

    b.bone(f"foot_{side}")
    # Espinilla angosta con inclinación digitígrada
    b.prism(0.09, 0.12, 0.38, loc=(sign * 0.19, -0.05, 0.26), taper=0.50, m=m_prism)
    b.box((0.015, 0.03, 0.28), loc=(sign * 0.20, -0.10, 0.26), m=m_blood)

    # ESPOLÓN TRASERO DE AGUJA
    b.prism(0.03, 0.06, 0.16, loc=(sign * 0.20, 0.08, 0.10), rot=(R(40), 0, 0), taper=0.1, m=m_prism)
    # Garra frontal del pie clavándose en el suelo
    b.prism(0.06, 0.16, 0.08, loc=(sign * 0.20, -0.12, 0.05), rot=(R(-25), 0, 0), taper=0.1, m=m_graph)
    b.prism(0.025, 0.08, 0.04, loc=(sign * 0.20, -0.18, 0.02), rot=(R(-25), 0, 0), taper=0.1, m=m_noise)

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
# 5. LIGHTING & CAMERA (ATMÓSFERA OSCURA Y ATERRADORA)
# --------------------------------------------------------------------------
if scene.world is None:
    scene.world = bpy.data.worlds.new("World_Studio")
scene.world.use_nodes = True
bg = scene.world.node_tree.nodes.get("Background")
if bg:
    bg.inputs["Color"].default_value = (0.01, 0.01, 0.015, 1.0)
    bg.inputs["Strength"].default_value = 0.20

cam_data = bpy.data.cameras.new("Cam_Shadow_Adjust")
cam_obj = bpy.data.objects.new("Cam_Shadow_Adjust", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_data.lens = 45.0

empty_target = bpy.data.objects.new("Cam_Shadow_Target", None)
scene.collection.objects.link(empty_target)
empty_target.location = (0.0, -0.05, 1.18)

tt = cam_obj.constraints.new(type='TRACK_TO')
tt.target = empty_target
tt.track_axis = 'TRACK_NEGATIVE_Z'
tt.up_axis = 'UP_Y'

dist = 3.0
cam_obj.location = (dist * 0.65, -dist * 0.85, 1.18 + dist * 0.25)

# Iluminación de Terror: Key Fría, Fill Sombra y Rim Incandescente
key_data = bpy.data.lights.new("Light_Key_Sha", type='AREA')
key_obj = bpy.data.objects.new("Light_Key_Sha", key_data)
scene.collection.objects.link(key_obj)
key_data.energy = 220.0
key_data.size = 2.5
key_data.color = (0.90, 0.95, 1.0)
key_obj.location = (dist * 0.7, -dist * 0.6, 1.18 + dist * 0.8)

fill_data = bpy.data.lights.new("Light_Fill_Sha", type='AREA')
fill_obj = bpy.data.objects.new("Light_Fill_Sha", fill_data)
scene.collection.objects.link(fill_obj)
fill_data.energy = 80.0
fill_data.size = 3.5
fill_data.color = (0.80, 0.05, 0.15) # Relleno rojo sangre sutil
fill_obj.location = (-dist * 0.7, -dist * 0.6, 1.18 + dist * 0.4)

rim_data = bpy.data.lights.new("Light_Rim_Sha", type='AREA')
rim_obj = bpy.data.objects.new("Light_Rim_Sha", rim_data)
scene.collection.objects.link(rim_obj)
rim_data.energy = 260.0
rim_data.size = 2.0
rim_data.color = (0.0, 0.95, 1.0) # Contraluz cian frío
rim_obj.location = (-dist * 0.2, dist * 0.8, 1.18 + dist * 0.6)

out_despues = os.path.join(output_dir, "static_shadow_despues.png")
scene.render.filepath = out_despues
bpy.ops.render.render(write_still=True)
print(f"RENDERED TERRIFYING STATIC SHADOW DESPUES -> {out_despues}")

blend_path = r"E:\Darx_Proyect\Saved\Player_Skin_Workspace\DarX_StaticShadow_Redesign.blend"
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f"FILE_SAVED: {blend_path}")

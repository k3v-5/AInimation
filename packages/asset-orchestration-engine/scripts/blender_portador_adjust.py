"""darx_portador_adjust.py — Rediseño Completo de El Portador (SK_Portador_Herald)
Heraldo e Invocador Dimensional de DarX:
- Corona de 5 prismas dimensionales romboidales afilados levitando en arco sobre la cabeza
- Báculo ceremonial de convocatoria con jaula toroidal dorada y orbe cuántico radiante
- Casco ceremonial facetado con visor vertical de grieta dimensional púrpura y diadema de oro
- Coraza de mando con hombreras imperiales oro/plata y runa de energía pectoral
- Capa dorsal segmentada con conductos luminosos y túnica balística ceremonial
"""

import bpy, bmesh, math, os, sys
from mathutils import Vector, Matrix, Euler

art_blender_dir = r"E:\Darx_Proyect\Art\Blender"
if art_blender_dir not in sys.path:
    sys.path.append(art_blender_dir)

import darx_lib as dl

output_dir = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"
os.makedirs(output_dir, exist_ok=True)

ARM_NAME = "ARM_Portador"
SK_NAME = "SK_Portador_Herald"
COL_NAME = "DARX_Portador"
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
m_dark = dl.mat("M_Herald_Armor", (0.04, 0.04, 0.05), rough=0.22, metal=0.90)
m_silver = dl.mat("M_Herald_Silver", (0.40, 0.42, 0.46), rough=0.16, metal=0.95)
m_gold = dl.mat("M_Herald_Gold", (0.92, 0.72, 0.15), rough=0.18, metal=0.92)

# Emisiones Cuánticas y Dimensionales
m_purple = dl.mat("M_Prism_Purple", (0.88, 0.08, 0.98), emis=(0.88, 0.08, 0.98), emis_str=42.0)
m_cyan = dl.mat("M_Prism_Cyan", (0.0, 0.95, 1.0), emis=(0.0, 0.95, 1.0), emis_str=40.0)
m_mint = dl.mat("M_Prism_Mint", (0.12, 1.0, 0.55), emis=(0.12, 1.0, 0.55), emis_str=38.0)

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
    pelvis.head = (0, 0, 1.00)
    pelvis.tail = (0, 0, 1.15)

    spine = eb.new("spine")
    spine.parent = pelvis
    spine.head = (0, 0, 1.15)
    spine.tail = (0, 0, 1.50)

    chest = eb.new("chest")
    chest.parent = spine
    chest.head = (0, 0, 1.50)
    chest.tail = (0, 0, 1.80)

    head = eb.new("head")
    head.parent = chest
    head.head = (0, -0.02, 1.80)
    head.tail = (0, -0.02, 2.15)

    # 5 Huesos de los Prismas Dimensionales en Arco
    prisms = [
        ("prism_1", (-0.46, 0, 2.32), (-0.52, 0, 2.72)),
        ("prism_2", (-0.24, 0, 2.50), (-0.28, 0, 2.94)),
        ("prism_3", (0, 0, 2.61),     (0, 0, 3.10)),
        ("prism_4", (0.24, 0, 2.50),  (0.28, 0, 2.94)),
        ("prism_5", (0.46, 0, 2.32),  (0.52, 0, 2.72)),
    ]
    for pname, h_p, t_p in prisms:
        p_bone = eb.new(pname)
        p_bone.parent = head
        p_bone.head = h_p
        p_bone.tail = t_p

    # Brazos
    sh_l = eb.new("shoulder_L")
    sh_l.parent = chest
    sh_l.head = (0.25, 0, 1.72)
    sh_l.tail = (0.44, 0, 1.72)

    arm_l = eb.new("upperarm_L")
    arm_l.parent = sh_l
    arm_l.head = (0.44, -0.06, 1.70)
    arm_l.tail = (0.45, -0.20, 1.35)

    hand_l = eb.new("hand_L")
    hand_l.parent = arm_l
    hand_l.head = (0.45, -0.20, 1.35)
    hand_l.tail = (0.45, -0.35, 1.10)

    sh_r = eb.new("shoulder_R")
    sh_r.parent = chest
    sh_r.head = (-0.25, 0, 1.72)
    sh_r.tail = (-0.44, 0, 1.72)

    arm_r = eb.new("upperarm_R")
    arm_r.parent = sh_r
    arm_r.head = (-0.44, 0.02, 1.70)
    arm_r.tail = (-0.45, 0, 1.35)

    hand_r = eb.new("hand_R")
    hand_r.parent = arm_r
    hand_r.head = (-0.45, 0, 1.35)
    hand_r.tail = (-0.45, -0.10, 1.10)

    # Báculo de Convocatoria (emparentado a hand_L)
    staff = eb.new("staff_bone")
    staff.parent = hand_l
    staff.head = (0.45, -0.35, 0.05)
    staff.tail = (0.45, -0.35, 2.25)

    # Piernas
    th_l = eb.new("thigh_L")
    th_l.parent = pelvis
    th_l.head = (0.19, 0, 1.00)
    th_l.tail = (0.19, 0, 0.50)

    foot_l = eb.new("foot_L")
    foot_l.parent = th_l
    foot_l.head = (0.19, 0, 0.50)
    foot_l.tail = (0.20, -0.18, 0)

    th_r = eb.new("thigh_R")
    th_r.parent = pelvis
    th_r.head = (-0.19, 0, 1.00)
    th_r.tail = (-0.19, 0, 0.50)

    foot_r = eb.new("foot_R")
    foot_r.parent = th_r
    foot_r.head = (-0.19, 0, 0.50)
    foot_r.tail = (-0.20, -0.18, 0)

    bpy.ops.object.mode_set(mode='OBJECT')
    return arm_obj

arm_obj = build_rig()

# --------------------------------------------------------------------------
# 3. CONSTRUCCIÓN DE LA MALLA
# --------------------------------------------------------------------------
b = dl.MB(SK_NAME)

# =========================================================================
# CABEZA: CASCO CEREMONIAL Y VISOR VERTICAL DE GRIETA
# =========================================================================
b.bone("head")
# Cuello estilizado con placas segmentadas
b.cyl(0.075, 0.12, loc=(0, -0.02, 1.78), rot=(0, 0, 0), m=m_silver)

# Casco facetado imperial
b.box((0.26, 0.28, 0.28), loc=(0, -0.02, 1.95), m=m_dark)

# Visera frontal estilizada en oro
b.box((0.28, 0.08, 0.05), loc=(0, -0.16, 2.06), rot=(14, 0, 0), m=m_gold)

# VISOR VERTICAL DE GRIETA DIMENSIONAL PÚRPURA
b.box((0.045, 0.05, 0.20), loc=(0, -0.16, 1.96), m=m_purple)
b.box((0.025, 0.06, 0.16), loc=(0, -0.165, 1.96), m=m_cyan)

# Corona / Diadema de soporte superior con remates de cresta
b.box((0.28, 0.30, 0.06), loc=(0, -0.02, 2.11), m=m_gold)
b.prism(0.12, 0.14, 0.08, loc=(0, -0.14, 2.14), rot=(0, 0, 0), taper=0.2, m=m_silver)

# Conducto de resonancia psiónica dorsal
b.cyl(0.045, 0.18, loc=(0, 0.13, 1.95), rot=(0, 0, 0), m=m_cyan)

# =========================================================================
# 5 PRISMAS DIMENSIONALES LEVITANDO EN ARCO (FACETADOS Y AFILADOS)
# =========================================================================
prisms_mesh = [
    ("prism_1", (-0.46, 0, 2.45), R(-25), m_purple),
    ("prism_2", (-0.24, 0, 2.62), R(-12), m_mint),
    ("prism_3", (0, 0, 2.76),     0,      m_cyan),
    ("prism_4", (0.24, 0, 2.62),  R(12),  m_gold),
    ("prism_5", (0.46, 0, 2.45),  R(25),  m_purple),
]

for bname, loc_p, rot_y, mat_p in prisms_mesh:
    b.bone(bname)
    # Prisma romboidal alargado doble con puntas afiladas
    b.prism(0.09, 0.09, 0.44, loc=loc_p, rot=(0, rot_y, 0), taper=0.2, m=mat_p)
    # Núcleo de runa interna radiante
    b.box((0.035, 0.035, 0.36), loc=loc_p, rot=(0, rot_y, 0), m=mat_p)
    # Anillo de fijación en plata
    b.box((0.11, 0.11, 0.03), loc=loc_p, rot=(0, rot_y, 0), m=m_silver)

# =========================================================================
# TORSO: CORAZA IMPERIAL Y CAPA SEGMENTADA
# =========================================================================
b.bone("chest")
# Chasis pectoral de aleación oscura
b.box((0.52, 0.34, 0.48), loc=(0, 0, 1.62), m=m_dark)

# Placa pechera frontal plateada biselada
b.box((0.26, 0.06, 0.34), loc=(0, -0.15, 1.64), m=m_silver)
# Runa central de mando en púrpura y cian
b.box((0.07, 0.03, 0.24), loc=(0, -0.18, 1.64), m=m_purple)
b.box((0.03, 0.04, 0.18), loc=(0, -0.185, 1.64), m=m_cyan)

# Ribetes dorados en los pectorales
for sign in (1, -1):
    b.box((0.08, 0.04, 0.28), loc=(sign * 0.18, -0.14, 1.64), rot=(0, sign * 12, 0), m=m_gold)

# CAPA DORSAL SEGMENTADA CON CONDUCTOS DE ENERGÍA
b.box((0.50, 0.06, 0.98), loc=(0, 0.16, 1.42), rot=(R(6), 0, 0), m=m_dark)
# Columna de conductos de resonancia
b.cyl(0.045, 0.72, loc=(0, 0.20, 1.42), rot=(R(6), 0, 0), m=m_purple)
for z_c in (1.25, 1.42, 1.60):
    b.box((0.36, 0.03, 0.05), loc=(0, 0.20, z_c), rot=(R(6), 0, 0), m=m_cyan)

# =========================================================================
# HOMBRERAS CEREMONIALES Y BRAZOS
# =========================================================================
for side, sign in [("L", 1), ("R", -1)]:
    b.bone(f"shoulder_{side}")
    # Hombrera de doble placa imperial en oro y plata
    b.box((0.24, 0.28, 0.16), loc=(sign * 0.38, 0, 1.74), rot=(0, sign * 16, 0), m=m_gold)
    b.box((0.20, 0.24, 0.08), loc=(sign * 0.40, 0, 1.83), rot=(0, sign * 16, 0), m=m_silver)
    # Gema de hombro púrpura
    b.box((0.12, 0.04, 0.10), loc=(sign * 0.38, -0.14, 1.74), m=m_purple)

    # Brazo Superior
    b.bone(f"upperarm_{side}")
    y_off = -0.06 if side == "L" else 0.02
    b.box((0.15, 0.16, 0.36), loc=(sign * 0.44, y_off, 1.50), m=m_dark)
    b.cyl(0.055, 0.08, loc=(sign * 0.45, -0.18 if side == "L" else 0, 1.35), rot=(90, 0, 0), m=m_silver)

    # Antebrazo y Guantelete
    b.bone(f"hand_{side}")
    y_h = -0.25 if side == "L" else -0.10
    b.box((0.14, 0.15, 0.26), loc=(sign * 0.45, y_h, 1.22), m=m_silver)
    b.box((0.16, 0.17, 0.08), loc=(sign * 0.45, y_h, 1.18), m=m_purple)
    b.cyl(0.035, 0.12, loc=(sign * 0.45, y_h - 0.04, 1.12), rot=(0, 90, 0), m=m_gold)

# =========================================================================
# BÁCULO / BALIZA DE ANCLAJE DIMENSIONAL (STAFF)
# =========================================================================
b.bone("staff_bone")
p_staff_x = 0.45
p_staff_y = -0.35

# 1. Asta principal de aleación oscura con anillos dorados
b.cyl(0.032, 2.20, loc=(p_staff_x, p_staff_y, 1.10), rot=(0, 0, 0), m=m_dark)
for z_ring in (0.45, 0.85, 1.35, 1.75):
    b.cyl(0.042, 0.04, loc=(p_staff_x, p_staff_y, z_ring), rot=(0, 0, 0), m=m_gold)

# Empuñadura plateada central
b.cyl(0.038, 0.30, loc=(p_staff_x, p_staff_y, 1.15), rot=(0, 0, 0), m=m_silver)

# 2. Cabeza Ceremonial: Jaula Toroidal de Oro
b.box((0.22, 0.14, 0.32), loc=(p_staff_x, p_staff_y, 2.05), m=m_gold)
b.box((0.18, 0.16, 0.04), loc=(p_staff_x, p_staff_y, 2.22), m=m_silver)

# 3. ORBE CUÁNTICO RADIANTE EN CIAN (EL NÚCLEO DE CONVOCATORIA)
b.sph(0.085, loc=(p_staff_x, p_staff_y, 2.05), m=m_cyan, u=18, v=10, smooth=True)
b.cyl(0.10, 0.015, loc=(p_staff_x, p_staff_y, 2.05), rot=(0, 0, 0), m=m_purple)

# 4. Punta de Resonancia Inferior
b.prism(0.06, 0.06, 0.20, loc=(p_staff_x, p_staff_y, 0.08), rot=(180, 0, 0), taper=0.1, m=m_gold)
b.sph(0.035, loc=(p_staff_x, p_staff_y, 0.18), m=m_purple, smooth=True)

# =========================================================================
# TÚNICA INFERIOR Y PIERNAS
# =========================================================================
b.bone("pelvis")
b.box((0.46, 0.30, 0.22), loc=(0, 0, 1.08), m=m_dark)

# Faldón ceremonial frontal
b.box((0.38, 0.05, 0.58), loc=(0, -0.15, 0.80), rot=(R(-8), 0, 0), m=m_silver)
b.box((0.10, 0.03, 0.44), loc=(0, -0.18, 0.80), rot=(R(-8), 0, 0), m=m_cyan)
for sign in (1, -1):
    b.box((0.05, 0.03, 0.50), loc=(sign * 0.16, -0.16, 0.80), rot=(R(-8), 0, 0), m=m_gold)

# Faldón posterior
b.box((0.46, 0.05, 0.68), loc=(0, 0.15, 0.80), rot=(R(8), 0, 0), m=m_dark)

for side, sign in [("L", 1), ("R", -1)]:
    b.bone(f"thigh_{side}")
    b.box((0.17, 0.19, 0.44), loc=(sign * 0.19, 0, 0.75), m=m_dark)

    b.bone(f"foot_{side}")
    # Bota ceremonial de placas
    b.box((0.18, 0.26, 0.48), loc=(sign * 0.20, -0.05, 0.25), m=m_silver)
    b.box((0.12, 0.04, 0.22), loc=(sign * 0.20, -0.18, 0.20), m=m_gold)

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

cam_data = bpy.data.cameras.new("Cam_Portador_Adjust")
cam_obj = bpy.data.objects.new("Cam_Portador_Adjust", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_data.lens = 45.0

empty_target = bpy.data.objects.new("Cam_Portador_Target", None)
scene.collection.objects.link(empty_target)
empty_target.location = (0.0, -0.10, 1.55)

tt = cam_obj.constraints.new(type='TRACK_TO')
tt.target = empty_target
tt.track_axis = 'TRACK_NEGATIVE_Z'
tt.up_axis = 'UP_Y'

dist = 3.6
cam_obj.location = (dist * 0.65, -dist * 0.85, 1.55 + dist * 0.25)

# Studio Lights
key_data = bpy.data.lights.new("Light_Key_Por", type='AREA')
key_obj = bpy.data.objects.new("Light_Key_Por", key_data)
scene.collection.objects.link(key_obj)
key_data.energy = 280.0
key_data.size = 2.5
key_data.color = (0.95, 0.98, 1.0)
key_obj.location = (dist * 0.7, -dist * 0.6, 1.55 + dist * 0.8)

fill_data = bpy.data.lights.new("Light_Fill_Por", type='AREA')
fill_obj = bpy.data.objects.new("Light_Fill_Por", fill_data)
scene.collection.objects.link(fill_obj)
fill_data.energy = 90.0
fill_data.size = 3.5
fill_data.color = (0.80, 0.20, 0.95) # Relleno púrpura dimensional
fill_obj.location = (-dist * 0.7, -dist * 0.6, 1.55 + dist * 0.4)

rim_data = bpy.data.lights.new("Light_Rim_Por", type='AREA')
rim_obj = bpy.data.objects.new("Light_Rim_Por", rim_data)
scene.collection.objects.link(rim_obj)
rim_data.energy = 240.0
rim_data.size = 2.5
rim_data.color = (0.0, 0.95, 1.0) # Contraluz cian cuántico
rim_obj.location = (-dist * 0.2, dist * 0.8, 1.55 + dist * 0.6)

out_despues = os.path.join(output_dir, "portador_despues.png")
scene.render.filepath = out_despues
bpy.ops.render.render(write_still=True)
print(f"RENDERED REFINED PORTADOR DESPUES -> {out_despues}")

blend_path = r"E:\Darx_Proyect\Saved\Player_Skin_Workspace\DarX_Portador_Redesign.blend"
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f"FILE_SAVED: {blend_path}")

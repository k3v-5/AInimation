"""darx_interferente_adjust.py — Rediseño Completo de El Interferente (SK_Interferente)
Dron Flotante de Guerra Electrónica / Inhibidor EMP:
- Chasis hexagonal de grafeno militar con blindaje biselado y disipadores térmicos
- Tobera antigravitatoria inferior con anillos de compresión iónica y haz de levitación magenta
- Dos bobinas de resonancia Tesla laterales con devanado de cobre helicoidal, aislamiento cerámico y emisores de arco
- Cúpula cuántica superior giratoria con esfera de emisión electromagnética
- 4 antenas phased-array en guía de onda angular con emisores direccionales de pulso EMP
"""

import bpy, bmesh, math, os, sys
from mathutils import Vector, Matrix, Euler

art_blender_dir = r"E:\Darx_Proyect\Art\Blender"
if art_blender_dir not in sys.path:
    sys.path.append(art_blender_dir)

import darx_lib as dl

output_dir = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"
os.makedirs(output_dir, exist_ok=True)

ARM_NAME = "ARM_Interferente"
SK_NAME = "SK_Interferente"
COL_NAME = "DARX_Interferente"
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
m_graph = dl.mat("M_Interferente_Graphene", (0.04, 0.04, 0.05), rough=0.22, metal=0.92)
m_copper = dl.mat("M_Interferente_Copper", (0.88, 0.48, 0.22), rough=0.16, metal=0.96)
m_steel = dl.mat("M_Interferente_Steel", (0.24, 0.25, 0.28), rough=0.20, metal=0.95)
m_chrome = dl.mat("M_Interferente_Chrome", (0.86, 0.88, 0.92), rough=0.10, metal=0.98)

# Emisión de Glitch y Pulso Electromagnético (EMP)
m_neon = dl.mat("M_Interferente_Neon", (0.95, 0.08, 0.98), emis=(0.95, 0.08, 0.98), emis_str=42.0)
m_cyan = dl.mat("M_Interferente_Cyan", (0.0, 0.95, 1.0), emis=(0.0, 0.95, 1.0), emis_str=36.0)

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

    # Base de propulsión antigravitatoria
    base = eb.new("base")
    base.parent = root
    base.head = (0, 0, 0.38)
    base.tail = (0, 0, 0.65)

    # Cuerpo central blindado
    body = eb.new("body")
    body.parent = base
    body.head = (0, 0, 0.65)
    body.tail = (0, -0.28, 0.65)

    # Bobinas laterales Tesla
    coil_l = eb.new("coil_L")
    coil_l.parent = body
    coil_l.head = (0.34, 0, 0.65)
    coil_l.tail = (0.56, 0, 0.65)

    coil_r = eb.new("coil_R")
    coil_r.parent = body
    coil_r.head = (-0.34, 0, 0.65)
    coil_r.tail = (-0.56, 0, 0.65)

    # Cúpula de guerra electrónica superior
    turret = eb.new("turret")
    turret.parent = body
    turret.head = (0, 0, 0.88)
    turret.tail = (0, 0, 1.15)

    # 4 Antenas Phased-Array
    antennas = [
        ("FL", (0.16, -0.16, 1.06), (0.30, -0.30, 1.48)),
        ("FR", (-0.16, -0.16, 1.06), (-0.30, -0.30, 1.48)),
        ("BL", (0.16, 0.16, 1.06), (0.30, 0.30, 1.48)),
        ("BR", (-0.16, 0.16, 1.06), (-0.30, 0.30, 1.48))
    ]

    for pfx, h_pos, t_pos in antennas:
        ant = eb.new(f"antenna_{pfx}")
        ant.parent = turret
        ant.head = h_pos
        ant.tail = t_pos

    bpy.ops.object.mode_set(mode='OBJECT')
    return arm_obj

arm_obj = build_rig()

# --------------------------------------------------------------------------
# 3. CONSTRUCCIÓN DE LA MALLA
# --------------------------------------------------------------------------
b = dl.MB(SK_NAME)

# =========================================================================
# BASE INFERIOR: PROPULSIÓN ANTIGRAVITATORIA Y HAZ IÓNICO
# =========================================================================
b.bone("base")
# Cono de dispersión iónica invertido
b.frustum(0.24, 0.12, 0.18, loc=(0, 0, 0.48), rot=(R(180), 0, 0), m=m_steel, seg=16)
# Anillo magnético de levitación
b.cyl(0.26, 0.04, loc=(0, 0, 0.52), rot=(0, 0, 0), m=m_graph)
# Tobera de haz iónico emisor (magenta EMP)
b.cyl(0.10, 0.06, loc=(0, 0, 0.38), rot=(0, 0, 0), m=m_neon, seg=16)
b.cyl(0.06, 0.03, loc=(0, 0, 0.34), rot=(0, 0, 0), m=m_chrome)

# 4 Aletas estabilizadoras de flujo en la base
for ang_stab in (0, 90, 180, 270):
    rad_s = math.radians(ang_stab)
    sx = 0.18 * math.cos(rad_s)
    sy = 0.18 * math.sin(rad_s)
    b.box((0.02, 0.08, 0.14), loc=(sx, sy, 0.46), rot=(0, 0, ang_stab), m=m_steel)

# =========================================================================
# CUERPO CENTRAL: CHASIS HEXAGONAL DE GRAFENO MILITAR
# =========================================================================
b.bone("body")
# Casco principal facetado (prisma biselado hexagonal)
b.prism(0.64, 0.56, 0.26, loc=(0, 0, 0.65), taper=0.88, m=m_graph)

# Placas de blindaje superior e inferior en cruz
b.box((0.68, 0.16, 0.20), loc=(0, 0, 0.65), m=m_steel)
b.box((0.22, 0.60, 0.20), loc=(0, 0, 0.65), m=m_steel)

# Núcleos de visualización de interferencia y disipadores (Frontal y Trasero)
for sign in (1, -1):
    # Pantalla / emisor de distorsión de interfaz
    b.box((0.18, 0.04, 0.10), loc=(0, sign * 0.30, 0.65), m=m_neon)
    b.box((0.22, 0.02, 0.12), loc=(0, sign * 0.31, 0.65), m=m_steel)
    # Ranuras de ventilación térmica
    for z_sl in (0.61, 0.69):
        b.box((0.30, 0.02, 0.015), loc=(0, sign * 0.28, z_sl), m=m_cyan)

# =========================================================================
# BOBINAS LATERALES DE RESONANCIA TESLA (L & R)
# =========================================================================
for side, sign in [("L", 1), ("R", -1)]:
    b.bone(f"coil_{side}")
    # Estator / viga de acople al chasis
    b.cyl(0.09, 0.26, loc=(sign * 0.44, 0, 0.65), rot=(0, R(90), 0), m=m_steel, seg=16)

    # Núcleo magnético de cromo central
    b.cyl(0.045, 0.28, loc=(sign * 0.45, 0, 0.65), rot=(0, R(90), 0), m=m_chrome, seg=12)

    # Devanado de bobina helicoidal en cobre macizo
    for cx in [0.35, 0.39, 0.43, 0.47, 0.51]:
        b.cyl(0.105, 0.024, loc=(sign * cx, 0, 0.65), rot=(0, R(90), 0), m=m_copper, seg=16)
        # Anillos aislantes cerámicos
        b.cyl(0.112, 0.008, loc=(sign * cx, 0, 0.65), rot=(0, R(90), 0), m=m_steel, seg=16)

    # Jaula protectora de soporte exterior (Faraday Struts)
    for ang_f in (0, 90, 180, 270):
        rad_f = math.radians(ang_f)
        fy = 0.115 * math.sin(rad_f)
        fz = 0.115 * math.cos(rad_f)
        b.seg((sign * 0.33, fy, 0.65 + fz), (sign * 0.55, fy, 0.65 + fz), 0.012, 0.008, m=m_steel, seg=6, smooth=True)

    # Terminal esférico de descarga de arco (magenta incandescente)
    b.sph(0.065, loc=(sign * 0.57, 0, 0.65), m=m_neon, u=14, v=8, smooth=True)
    # Corona de descarga en cromo
    b.cyl(0.05, 0.02, loc=(sign * 0.59, 0, 0.65), rot=(0, R(90), 0), m=m_chrome, seg=12)

# =========================================================================
# TORRETA SUPERIOR RADOMO Y ANTENAS PHASED-ARRAY
# =========================================================================
b.bone("turret")
# Base giratoria de la cúpula
b.frustum(0.24, 0.16, 0.16, loc=(0, 0, 0.94), m=m_graph, seg=16)
b.cyl(0.20, 0.04, loc=(0, 0, 0.88), rot=(0, 0, 0), m=m_steel)

# Esfera central cuántica de emisión EMP
b.sph(0.12, loc=(0, 0, 1.04), m=m_neon, u=18, v=10, smooth=True)
# Anillo ecuatorial de enfoque magnético
b.cyl(0.14, 0.02, loc=(0, 0, 1.04), rot=(0, 0, 0), m=m_copper)

# 4 ANTENAS PHASED-ARRAY EN GUÍA DE ONDA
ant_mesh = [
    ("FL", (0.16, -0.16, 1.06), (0.30, -0.30, 1.48)),
    ("FR", (-0.16, -0.16, 1.06), (-0.30, -0.30, 1.48)),
    ("BL", (0.16, 0.16, 1.06), (0.30, 0.30, 1.48)),
    ("BR", (-0.16, 0.16, 1.06), (-0.30, 0.30, 1.48))
]

for pfx, h_pos, t_pos in ant_mesh:
    b.bone(f"antenna_{pfx}")
    # Rótula de soporte en la cúpula
    b.sph(0.038, loc=h_pos, m=m_steel, smooth=True)

    # Guía de onda tubular principal en cobre
    b.seg(h_pos, t_pos, 0.032, 0.016, m=m_copper, seg=10, smooth=True)

    # Viga de refuerzo estructural en grafeno
    p_mid_ant = ((h_pos[0]+t_pos[0])/2, (h_pos[1]+t_pos[1])/2, (h_pos[2]+t_pos[2])/2)
    b.box((0.04, 0.04, 0.18), loc=p_mid_ant, rot=(15, 15, 0), m=m_graph)

    # Emisor direccional de bocina en la punta
    b.box((0.09, 0.06, 0.14), loc=t_pos, rot=(15, 15, 0), m=m_steel)
    # Núcleo de descarga luminosa EMP
    b.box((0.06, 0.03, 0.10), loc=t_pos, rot=(15, 15, 0), m=m_neon)
    # Sensor auxiliar cian
    b.sph(0.014, loc=(t_pos[0], t_pos[1], t_pos[2] + 0.07), m=m_cyan, smooth=True)

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

cam_data = bpy.data.cameras.new("Cam_Interferente_Adjust")
cam_obj = bpy.data.objects.new("Cam_Interferente_Adjust", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_data.lens = 45.0

empty_target = bpy.data.objects.new("Cam_Interferente_Target", None)
scene.collection.objects.link(empty_target)
empty_target.location = (0.0, 0.0, 0.85)

tt = cam_obj.constraints.new(type='TRACK_TO')
tt.target = empty_target
tt.track_axis = 'TRACK_NEGATIVE_Z'
tt.up_axis = 'UP_Y'

dist = 2.8
cam_obj.location = (dist * 0.65, -dist * 0.85, 0.85 + dist * 0.35)

# Studio Lights
key_data = bpy.data.lights.new("Light_Key_Int", type='AREA')
key_obj = bpy.data.objects.new("Light_Key_Int", key_data)
scene.collection.objects.link(key_obj)
key_data.energy = 240.0
key_data.size = 2.5
key_data.color = (0.95, 0.98, 1.0)
key_obj.location = (dist * 0.7, -dist * 0.6, 0.85 + dist * 0.8)

fill_data = bpy.data.lights.new("Light_Fill_Int", type='AREA')
fill_obj = bpy.data.objects.new("Light_Fill_Int", fill_data)
scene.collection.objects.link(fill_obj)
fill_data.energy = 90.0
fill_data.size = 3.5
fill_data.color = (0.85, 0.10, 0.95) # Relleno magenta EMP
fill_obj.location = (-dist * 0.7, -dist * 0.6, 0.85 + dist * 0.4)

rim_data = bpy.data.lights.new("Light_Rim_Int", type='AREA')
rim_obj = bpy.data.objects.new("Light_Rim_Int", rim_data)
scene.collection.objects.link(rim_obj)
rim_data.energy = 220.0
rim_data.size = 2.0
rim_data.color = (0.0, 0.95, 1.0) # Contraluz cian cuántico
rim_obj.location = (-dist * 0.2, dist * 0.8, 0.85 + dist * 0.6)

out_despues = os.path.join(output_dir, "interferente_despues.png")
scene.render.filepath = out_despues
bpy.ops.render.render(write_still=True)
print(f"RENDERED REFINED INTERFERENTE DESPUES -> {out_despues}")

blend_path = r"E:\Darx_Proyect\Saved\Player_Skin_Workspace\DarX_Interferente_Redesign.blend"
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f"FILE_SAVED: {blend_path}")

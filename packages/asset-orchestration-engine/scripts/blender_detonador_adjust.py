"""darx_detonador_adjust.py — Rediseño Terrorífico de El Detonador (SK_Detonador)
Ajuste solicitado por el usuario:
- Aro de advertencia en ROJO carmesí peligro extremo con canales emisivos
- Aspecto mucho más siniestro y aterrador:
  * Cluster de 6 ojos arácnidos carmesí depredadores
  * Quelíceros / colmillos mecánicos afilados frontales para clavarse en la presa
  * Espinas dorsales y fisuras incandescentes en la cápsula
  * Patas con espolones estilo agujas / guadañas biomecánicas de tracción
"""

import bpy, bmesh, math, os, sys
from mathutils import Vector, Matrix, Euler

art_blender_dir = r"E:\Darx_Proyect\Art\Blender"
if art_blender_dir not in sys.path:
    sys.path.append(art_blender_dir)

import darx_lib as dl

output_dir = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"
os.makedirs(output_dir, exist_ok=True)

ARM_NAME = "ARM_Detonador"
SK_NAME = "SK_Detonador"
COL_NAME = "DARX_Detonador"
R = math.radians

# Clean Scene
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.resolution_x = 960
scene.render.resolution_y = 960
scene.render.film_transparent = False

col = dl.coll(COL_NAME)

# --------------------------------------------------------------------------
# 1. MATERIALES PBR: TERROR INDUSTRIAL
# --------------------------------------------------------------------------
m_armor = dl.mat("M_Detonador_Armor", (0.03, 0.03, 0.04), rough=0.25, metal=0.90)
m_steel = dl.mat("M_Detonador_Steel", (0.20, 0.21, 0.24), rough=0.18, metal=0.96)
m_chrome = dl.mat("M_Detonador_Chrome", (0.86, 0.88, 0.92), rough=0.10, metal=0.98)

# ARO ROJO DE PELIGRO EXTREMO
m_ring_red = dl.mat("M_Detonador_RingRed", (0.75, 0.04, 0.03), rough=0.25, metal=0.50)
m_red_glow = dl.mat("M_Detonador_RedGlow", (1.0, 0.02, 0.01), emis=(1.0, 0.02, 0.01), emis_str=38.0)

# Núcleo y Ojos Arácnidos
m_core = dl.mat("M_Detonador_Core", (1.0, 0.15, 0.02), emis=(1.0, 0.18, 0.02), emis_str=45.0)
m_eye_blood = dl.mat("M_Detonador_EyeBlood", (1.0, 0.0, 0.0), emis=(1.0, 0.0, 0.0), emis_str=48.0)

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

    body = eb.new("body")
    body.parent = root
    body.head = (0, 0, 0.42)
    body.tail = (0, -0.22, 0.42)

    core = eb.new("core")
    core.parent = body
    core.head = (0, 0, 0.42)
    core.tail = (0, 0, 0.58)

    # Quelíceros / Mandíbulas mecánicas
    fang_l = eb.new("fang_L")
    fang_l.parent = body
    fang_l.head = (-0.08, -0.32, 0.38)
    fang_l.tail = (-0.04, -0.46, 0.28)

    fang_r = eb.new("fang_R")
    fang_r.parent = body
    fang_r.head = (0.08, -0.32, 0.38)
    fang_r.tail = (0.04, -0.46, 0.28)

    # Escapes
    vent_l = eb.new("vent_L")
    vent_l.parent = body
    vent_l.head = (0.14, 0.16, 0.54)
    vent_l.tail = (0.20, 0.32, 0.70)

    vent_r = eb.new("vent_R")
    vent_r.parent = body
    vent_r.head = (-0.14, 0.16, 0.54)
    vent_r.tail = (-0.20, 0.32, 0.70)

    patas = [
        ("FL", (0.20, -0.16, 0.38), (0.46, -0.38, 0.52), (0.58, -0.52, 0.18), (0.64, -0.58, 0.0)),
        ("FR", (-0.20, -0.16, 0.38), (-0.46, -0.38, 0.52), (-0.58, -0.52, 0.18), (-0.64, -0.58, 0.0)),
        ("BL", (0.20, 0.18, 0.38), (0.48, 0.40, 0.52), (0.60, 0.54, 0.18), (0.66, 0.60, 0.0)),
        ("BR", (-0.20, 0.18, 0.38), (-0.48, 0.40, 0.52), (-0.60, 0.54, 0.18), (-0.66, 0.60, 0.0))
    ]

    for pfx, h_hip, t_thigh, t_shin, t_foot in patas:
        hip = eb.new(f"leg_{pfx}_hip")
        hip.parent = body
        hip.head = h_hip
        hip.tail = t_thigh

        shin = eb.new(f"leg_{pfx}_shin")
        shin.parent = hip
        shin.head = t_thigh
        shin.tail = t_shin

        foot = eb.new(f"leg_{pfx}_foot")
        foot.parent = shin
        foot.head = t_shin
        foot.tail = t_foot

    bpy.ops.object.mode_set(mode='OBJECT')
    return arm_obj

arm_obj = build_rig()

# --------------------------------------------------------------------------
# 3. CONSTRUCCIÓN DE LA MALLA
# --------------------------------------------------------------------------
b = dl.MB(SK_NAME)

# =========================================================================
# CUERPO CENTRAL: MINA DE TERROR ARÁCNIDO
# =========================================================================
b.bone("body")

# 1. Chasis central facetado (cúpula hemisférica inferior y superior)
b.sph(0.27, loc=(0, 0, 0.40), m=m_armor, u=20, v=12, smooth=True)

# 2. Cúpula de Cristal Blindado Superior con el Núcleo Hirviente
b.sph(0.19, loc=(0, 0, 0.51), m=dl.mat("M_Detonador_Glass", (0.9, 0.1, 0.05), rough=0.08, metal=0.1, emis=(1.0, 0.15, 0.02), emis_str=16.0), u=18, v=10, smooth=True)

# 3. EL ARO ROJO (SOLICITADO POR EL USUARIO): CINTURÓN ROJO CARMESÍ CON CANALES INCANDESCENTES
b.cyl(0.315, 0.085, loc=(0, 0, 0.42), rot=(0, 0, 0), m=m_ring_red)
# Anillo central de emisión roja pura
b.cyl(0.325, 0.025, loc=(0, 0, 0.42), rot=(0, 0, 0), m=m_red_glow)

# Dientes / puas de advertencia a lo largo del aro rojo
for ang_d in range(0, 360, 30):
    rad_d = math.radians(ang_d)
    tx = 0.32 * math.cos(rad_d)
    ty = 0.32 * math.sin(rad_d)
    b.prism(0.025, 0.045, 0.035, loc=(tx, ty, 0.42), rot=(0, 90, ang_d), taper=0.2, m=m_steel)

# Costillas de compresión de acero oscuro
for ang_deg in (45, 135, 225, 315):
    rad = math.radians(ang_deg)
    rx = 0.20 * math.cos(rad)
    ry = 0.20 * math.sin(rad)
    b.box((0.04, 0.04, 0.26), loc=(rx, ry, 0.46), rot=(0, 0, ang_deg), m=m_steel)
    # Púa de amenaza dorsal sobre cada costilla
    b.prism(0.03, 0.03, 0.06, loc=(rx * 1.05, ry * 1.05, 0.60), rot=(0, 0, ang_deg), taper=0.1, m=m_steel)

# 4. CLUSTER DE OJOS ARÁCNIDOS SINIESTROS (6 OJOS EN TOTAL)
b.box((0.20, 0.12, 0.12), loc=(0, -0.24, 0.44), rot=(14, 0, 0), m=m_armor)

# Dos ojos centrales principales (mirada sanguinaria)
b.sph(0.028, loc=(-0.045, -0.31, 0.46), m=m_eye_blood, smooth=True)
b.sph(0.028, loc=(0.045, -0.31, 0.46), m=m_eye_blood, smooth=True)

# Dos ojos secundarios superiores
b.sph(0.018, loc=(-0.08, -0.28, 0.50), m=m_eye_blood, smooth=True)
b.sph(0.018, loc=(0.08, -0.28, 0.50), m=m_eye_blood, smooth=True)

# Dos ojos inferiores laterales
b.sph(0.016, loc=(-0.07, -0.29, 0.41), m=m_eye_blood, smooth=True)
b.sph(0.016, loc=(0.07, -0.29, 0.41), m=m_eye_blood, smooth=True)

# =========================================================================
# QUELÍCEROS / COLMILLOS MECÁNICOS FRONTALES (ASPECTO TERRORÍFICO)
# =========================================================================
b.bone("fang_L")
b.seg((-0.08, -0.30, 0.38), (-0.05, -0.42, 0.32), 0.024, 0.012, m=m_steel, seg=6, smooth=False)
b.seg((-0.05, -0.42, 0.32), (-0.02, -0.47, 0.26), 0.012, 0.002, m=m_chrome, seg=6, smooth=True)

b.bone("fang_R")
b.seg((0.08, -0.30, 0.38), (0.05, -0.42, 0.32), 0.024, 0.012, m=m_steel, seg=6, smooth=False)
b.seg((0.05, -0.42, 0.32), (0.02, -0.47, 0.26), 0.012, 0.002, m=m_chrome, seg=6, smooth=True)

# =========================================================================
# NÚCLEO DE PLASMA EN SOBRECARGA CRÍTICA
# =========================================================================
b.bone("core")
b.sph(0.16, loc=(0, 0, 0.42), m=m_core, u=18, v=10, smooth=True)
b.cyl(0.07, 0.24, loc=(0, 0, 0.42), rot=(0, 0, 0), m=m_chrome)
for z_ring in (0.35, 0.42, 0.49):
    b.cyl(0.19, 0.015, loc=(0, 0, z_ring), rot=(0, 0, 0), m=m_steel)

# =========================================================================
# TOBERAS Y CHIMENEAS DE DESPRESURIZACIÓN TRASERAS
# =========================================================================
for side, sign in [("L", 1), ("R", -1)]:
    b.bone(f"vent_{side}")
    p_base = (sign * 0.13, 0.16, 0.53)
    p_tip = (sign * 0.19, 0.30, 0.69)
    b.seg(p_base, p_tip, 0.055, 0.040, m=m_steel, seg=10, smooth=True)
    p_mid = ((p_base[0]+p_tip[0])/2, (p_base[1]+p_tip[1])/2, (p_base[2]+p_tip[2])/2)
    b.box((0.08, 0.08, 0.10), loc=p_mid, rot=(R(-38), sign * R(18), 0), m=m_armor)
    b.sph(0.028, loc=p_tip, m=m_core, smooth=True)

# =========================================================================
# 4 PATAS ARÁCNIDAS CON ESPOLONES DE AGUJA
# =========================================================================
patas_coords = [
    ("FL", (0.20, -0.16, 0.38), (0.46, -0.38, 0.52), (0.58, -0.52, 0.18), (0.64, -0.58, 0.0)),
    ("FR", (-0.20, -0.16, 0.38), (-0.46, -0.38, 0.52), (-0.58, -0.52, 0.18), (-0.64, -0.58, 0.0)),
    ("BL", (0.20, 0.18, 0.38), (0.48, 0.40, 0.52), (0.60, 0.54, 0.18), (0.66, 0.60, 0.0)),
    ("BR", (-0.20, 0.18, 0.38), (-0.48, 0.40, 0.52), (-0.60, 0.54, 0.18), (-0.66, 0.60, 0.0))
]

for pfx, h_hip, t_thigh, t_shin, t_foot in patas_coords:
    b.bone(f"leg_{pfx}_hip")
    b.sph(0.055, loc=h_hip, m=m_steel, smooth=True)
    b.seg(h_hip, t_thigh, 0.048, 0.038, m=m_armor, seg=8, smooth=False)
    p_mid_femur = ((h_hip[0]+t_thigh[0])/2, (h_hip[1]+t_thigh[1])/2, (h_hip[2]+t_thigh[2])/2 + 0.015)
    b.box((0.07, 0.12, 0.04), loc=p_mid_femur, rot=(15, 0, 0), m=m_ring_red)
    # Espina lateral en el muslo
    b.prism(0.02, 0.03, 0.05, loc=(p_mid_femur[0], p_mid_femur[1], p_mid_femur[2] + 0.03), rot=(0, 0, 0), taper=0.1, m=m_steel)

    b.bone(f"leg_{pfx}_shin")
    b.sph(0.048, loc=t_thigh, m=m_steel, smooth=True)
    b.cyl(0.025, 0.08, loc=t_thigh, rot=(0, 90, 0), m=m_chrome)
    b.seg(t_thigh, t_shin, 0.038, 0.024, m=m_armor, seg=8, smooth=False)
    p_mid_shin = ((t_thigh[0]+t_shin[0])/2, (t_thigh[1]+t_shin[1])/2, (t_thigh[2]+t_shin[2])/2)
    b.seg(t_thigh, p_mid_shin, 0.014, 0.010, m=m_chrome, seg=6, smooth=True)

    b.bone(f"leg_{pfx}_foot")
    b.sph(0.035, loc=t_shin, m=m_steel, smooth=True)
    b.seg(t_shin, t_foot, 0.026, 0.008, m=m_steel, seg=8, smooth=False)
    # Espolón afilado en aguja de penetración Z=0
    p_ground_needle = (t_foot[0] * 1.05, t_foot[1] * 1.05, -0.01)
    b.seg(t_foot, p_ground_needle, 0.016, 0.002, m=m_chrome, seg=6, smooth=True)

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

cam_data = bpy.data.cameras.new("Cam_Detonador_Adjust")
cam_obj = bpy.data.objects.new("Cam_Detonador_Adjust", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_data.lens = 45.0

empty_target = bpy.data.objects.new("Cam_Detonador_Target", None)
scene.collection.objects.link(empty_target)
empty_target.location = (0.0, 0.0, 0.38)

tt = cam_obj.constraints.new(type='TRACK_TO')
tt.target = empty_target
tt.track_axis = 'TRACK_NEGATIVE_Z'
tt.up_axis = 'UP_Y'

dist = 2.4
cam_obj.location = (dist * 0.65, -dist * 0.85, 0.38 + dist * 0.45)

# Studio Lights
key_data = bpy.data.lights.new("Light_Key_Det", type='AREA')
key_obj = bpy.data.objects.new("Light_Key_Det", key_data)
scene.collection.objects.link(key_obj)
key_data.energy = 240.0
key_data.size = 2.0
key_data.color = (0.95, 0.98, 1.0)
key_obj.location = (dist * 0.7, -dist * 0.6, 0.38 + dist * 0.8)

fill_data = bpy.data.lights.new("Light_Fill_Det", type='AREA')
fill_obj = bpy.data.objects.new("Light_Fill_Det", fill_data)
scene.collection.objects.link(fill_obj)
fill_data.energy = 80.0
fill_data.size = 3.0
fill_data.color = (1.0, 0.15, 0.10) # Relleno rojo sangre
fill_obj.location = (-dist * 0.7, -dist * 0.6, 0.38 + dist * 0.4)

rim_data = bpy.data.lights.new("Light_Rim_Det", type='AREA')
rim_obj = bpy.data.objects.new("Light_Rim_Det", rim_data)
scene.collection.objects.link(rim_obj)
rim_data.energy = 220.0
rim_data.size = 2.0
rim_data.color = (1.0, 0.05, 0.02) # Contraluz carmesí de peligro
rim_obj.location = (-dist * 0.2, dist * 0.8, 0.38 + dist * 0.6)

out_despues = os.path.join(output_dir, "detonador_despues.png")
scene.render.filepath = out_despues
bpy.ops.render.render(write_still=True)
print(f"RENDERED SCARY RED DETONADOR DESPUES -> {out_despues}")

blend_path = r"E:\Darx_Proyect\Saved\Player_Skin_Workspace\DarX_Detonador_Redesign.blend"
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f"FILE_SAVED: {blend_path}")

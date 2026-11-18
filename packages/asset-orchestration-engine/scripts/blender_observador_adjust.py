"""darx_observador_adjust.py — Rediseño Completo de El Observador (SK_Observador)
Ajuste solicitado por el usuario:
- UN SOLO OJO central (eliminadas las ópticas satélite secundarias)
- Ojo en ROJO carmesí penetrante (estilo HAL 9000 / GLaDOS / centinela clínico de escaneo)
- Chasis en blanco cerámico aeroespacial de alta tecnología con cromo pulido
- Doble gimbal giroscópico con diodos de telemetría en rojo de alerta
- Tobera inferior de levitación vectorial
"""

import bpy, bmesh, math, os, sys
from mathutils import Vector, Matrix, Euler

art_blender_dir = r"E:\Darx_Proyect\Art\Blender"
if art_blender_dir not in sys.path:
    sys.path.append(art_blender_dir)

import darx_lib as dl

output_dir = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"
os.makedirs(output_dir, exist_ok=True)

ARM_NAME = "ARM_Observador"
SK_NAME = "SK_Observador"
COL_NAME = "DARX_Observador"
R = math.radians

# Clean Scene
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.resolution_x = 960
scene.render.resolution_y = 960
scene.render.film_transparent = False

col = dl.coll(COL_NAME)

# --------------------------------------------------------------------------
# 1. MATERIALES PBR: BLANCO CERÁMICO Y OJO ROJO
# --------------------------------------------------------------------------
# Blindaje en blanco cerámico de alta tecnología
m_white = dl.mat("M_Observador_WhiteCeramic", (0.92, 0.94, 0.96), rough=0.12, metal=0.15)
# Chasis interno en aleación oscura de sigilo
m_dark = dl.mat("M_Observador_DarkChassis", (0.06, 0.07, 0.08), rough=0.26, metal=0.88)
# Cromo pulido para gimbal, pernos y aros de rodamiento
m_chrome = dl.mat("M_Observador_Chrome", (0.88, 0.90, 0.94), rough=0.08, metal=0.98)

# ÓPTICA ROJA PENETRANTE (SOLICITADA POR EL USUARIO)
m_red_laser = dl.mat("M_Observador_RedLaser", (1.0, 0.02, 0.01), emis=(1.0, 0.02, 0.01), emis_str=46.0)
m_red_glass = dl.mat("M_Observador_RedGlass", (0.95, 0.10, 0.08), rough=0.03, metal=0.10, emis=(0.85, 0.02, 0.01), emis_str=10.0)

# --------------------------------------------------------------------------
# 2. ARMATURE (UN SOLO OJO CENTRAL)
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
    body.head = (0, 0, 1.25)
    body.tail = (0, -0.28, 1.25)

    thruster = eb.new("thruster")
    thruster.parent = body
    thruster.head = (0, 0, 1.05)
    thruster.tail = (0, 0, 0.82)

    ring_out = eb.new("ring_outer")
    ring_out.parent = body
    ring_out.head = (0, 0, 1.25)
    ring_out.tail = (0, -0.46, 1.25)

    ring_in = eb.new("ring_inner")
    ring_in.parent = body
    ring_in.head = (0, 0, 1.25)
    ring_in.tail = (0, -0.36, 1.25)

    # UN SOLO OJO CENTRAL
    eye_main = eb.new("eye_main")
    eye_main.parent = body
    eye_main.head = (0, -0.18, 1.25)
    eye_main.tail = (0, -0.44, 1.25)

    bpy.ops.object.mode_set(mode='OBJECT')
    return arm_obj

arm_obj = build_rig()

# --------------------------------------------------------------------------
# 3. CONSTRUCCIÓN DE LA MALLA
# --------------------------------------------------------------------------
b = dl.MB(SK_NAME)

# =========================================================================
# CUERPO ESFÉRICO BLANCO CERÁMICO
# =========================================================================
b.bone("body")

# 1. Esfera central blanca aerodinámica
b.sph(0.26, loc=(0, 0, 1.25), m=m_white, u=24, v=14, smooth=True)

# 2. Casquetes polares y bandas de unión en titanio oscuro
b.cyl(0.275, 0.05, loc=(0, 0, 1.25), rot=(0, 0, 0), m=m_dark)
b.cyl(0.280, 0.015, loc=(0, 0, 1.25), rot=(0, 0, 0), m=m_chrome)

# Cúpula superior aerodinámica en blanco cerámico
b.frustum(0.25, 0.12, 0.12, loc=(0, 0, 1.38), rot=(0, 0, 0), m=m_white, seg=20)
b.cyl(0.08, 0.04, loc=(0, 0, 1.48), rot=(0, 0, 0), m=m_chrome)
b.sph(0.04, loc=(0, 0, 1.50), m=m_red_laser, smooth=True)

# Disipadores térmicos ranurados posteriores
b.box((0.22, 0.08, 0.18), loc=(0, 0.20, 1.25), m=m_dark)
for z_v in (1.18, 1.25, 1.32):
    b.box((0.18, 0.02, 0.015), loc=(0, 0.25, z_v), m=m_red_laser)

# =========================================================================
# GIMBAL GIROSCÓPICO DE DOBLE ANILLO (ANILLO EXTERIOR E INTERIOR)
# =========================================================================
# 1. Anillo Exterior (ring_outer): Blanco Cerámico con Rebordes de Cromo
b.bone("ring_outer")
r_out = 0.44
for a in range(0, 360, 20):
    rad = math.radians(a)
    x = r_out * math.cos(rad)
    y = r_out * math.sin(rad)
    b.box((0.05, 0.07, 0.05), loc=(x, y, 1.25), rot=(0, 0, rad), m=m_white)

b.cyl(r_out, 0.02, loc=(0, 0, 1.25), rot=(R(90), 0, 0), m=m_chrome, seg=32)

# 4 Cojinetes de articulación de gimbal a 90° con diodos rojos de alerta
for a_pin in (0, 90, 180, 270):
    rad_p = math.radians(a_pin)
    px = r_out * math.cos(rad_p)
    py = r_out * math.sin(rad_p)
    b.cyl(0.035, 0.06, loc=(px, py, 1.25), rot=(0, 0, a_pin), m=m_chrome)
    b.sph(0.015, loc=(px, py, 1.25), m=m_red_laser, smooth=True)

# 2. Anillo Interior (ring_inner): Cardán Gimbal Inclinado en Cromo y Diodos Rojos
b.bone("ring_inner")
r_in = 0.34
for a in range(0, 360, 30):
    rad = math.radians(a)
    x = r_in * math.cos(rad)
    z = 1.25 + r_in * math.sin(rad)
    b.box((0.035, 0.06, 0.035), loc=(x, 0, z), rot=(0, rad, 0), m=m_chrome)
    b.sph(0.012, loc=(x, -0.035, z), m=m_red_laser, smooth=True)

b.cyl(r_in, 0.018, loc=(0, 0, 1.25), rot=(0, 0, 0), m=m_white, seg=24)

# =========================================================================
# UN SOLO OJO ÓPTICO CENTRAL (ROJO PENETRANTE DE ALTA RESOLUCIÓN)
# =========================================================================
b.bone("eye_main")
# Carcasa telescópica de la lente en blanco cerámico (más prominente y centrada)
b.frustum(0.15, 0.105, 0.18, loc=(0, -0.22, 1.25), rot=(R(-90), 0, 0), m=m_white, seg=24)

# Anillo exterior biselado de titanio oscuro
b.cyl(0.155, 0.035, loc=(0, -0.20, 1.25), rot=(R(90), 0, 0), m=m_dark, seg=24)

# Anillo de enfoque estriado en cromo pulido
b.cyl(0.145, 0.04, loc=(0, -0.25, 1.25), rot=(R(90), 0, 0), m=m_chrome, seg=24)

# Diafragma / Iris mecánico de obturación en titanio oscuro
b.cyl(0.10, 0.015, loc=(0, -0.30, 1.25), rot=(R(90), 0, 0), m=m_dark, seg=16)

# Pupila / Núcleo de escaneo láser en ROJO CARMESÍ INCANDESCENTE
b.sph(0.080, loc=(0, -0.32, 1.25), m=m_red_laser, u=20, v=12, smooth=True)

# Lente convexa exterior de cristal rojo antirreflejo
b.sph(0.092, loc=(0, -0.33, 1.25), m=m_red_glass, u=20, v=12, smooth=True)

# Aro luminoso perimetral de advertencia roja
b.cyl(0.115, 0.010, loc=(0, -0.31, 1.25), rot=(R(90), 0, 0), m=m_red_laser, seg=24)

# =========================================================================
# PROPULSOR VECTORIAL INFERIOR (TOBERA IÓNICA ROJA)
# =========================================================================
b.bone("thruster")
# Tobera cónica en blanco cerámico y cromo
b.frustum(0.16, 0.08, 0.18, loc=(0, 0, 1.02), rot=(R(180), 0, 0), m=m_white, seg=18)
b.cyl(0.12, 0.04, loc=(0, 0, 0.96), rot=(0, 0, 0), m=m_chrome)

# Haz de levitación iónica roja orientado al suelo
b.cyl(0.06, 0.06, loc=(0, 0, 0.88), rot=(0, 0, 0), m=m_red_laser, seg=16)
b.sph(0.045, loc=(0, 0, 0.86), m=m_red_laser, smooth=True)

# 4 Micro-aletas vectoriales en cromo
for ang_fin in (45, 135, 225, 315):
    rad_f = math.radians(ang_fin)
    fx = 0.12 * math.cos(rad_f)
    fy = 0.12 * math.sin(rad_f)
    b.box((0.015, 0.06, 0.10), loc=(fx, fy, 0.98), rot=(0, 0, ang_fin), m=m_chrome)

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

cam_data = bpy.data.cameras.new("Cam_Observador_Adjust")
cam_obj = bpy.data.objects.new("Cam_Observador_Adjust", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_data.lens = 45.0

empty_target = bpy.data.objects.new("Cam_Observador_Target", None)
scene.collection.objects.link(empty_target)
empty_target.location = (0.0, -0.05, 1.25)

tt = cam_obj.constraints.new(type='TRACK_TO')
tt.target = empty_target
tt.track_axis = 'TRACK_NEGATIVE_Z'
tt.up_axis = 'UP_Y'

dist = 2.4
cam_obj.location = (dist * 0.65, -dist * 0.85, 1.25 + dist * 0.35)

# Studio Lights
key_data = bpy.data.lights.new("Light_Key_Obs", type='AREA')
key_obj = bpy.data.objects.new("Light_Key_Obs", key_data)
scene.collection.objects.link(key_obj)
key_data.energy = 240.0
key_data.size = 2.0
key_data.color = (0.95, 0.98, 1.0)
key_obj.location = (dist * 0.7, -dist * 0.6, 1.25 + dist * 0.8)

fill_data = bpy.data.lights.new("Light_Fill_Obs", type='AREA')
fill_obj = bpy.data.objects.new("Light_Fill_Obs", fill_data)
scene.collection.objects.link(fill_obj)
fill_data.energy = 80.0
fill_data.size = 3.0
fill_data.color = (1.0, 0.2, 0.15) # Relleno rojo sutil
fill_obj.location = (-dist * 0.7, -dist * 0.6, 1.25 + dist * 0.4)

rim_data = bpy.data.lights.new("Light_Rim_Obs", type='AREA')
rim_obj = bpy.data.objects.new("Light_Rim_Obs", rim_data)
scene.collection.objects.link(rim_obj)
rim_data.energy = 220.0
rim_data.size = 2.0
rim_data.color = (1.0, 0.05, 0.02) # Contraluz rojo de escaneo
rim_obj.location = (-dist * 0.2, dist * 0.8, 1.25 + dist * 0.6)

out_despues = os.path.join(output_dir, "observador_despues.png")
scene.render.filepath = out_despues
bpy.ops.render.render(write_still=True)
print(f"RENDERED RED SINGLE EYE OBSERVADOR DESPUES -> {out_despues}")

blend_path = r"E:\Darx_Proyect\Saved\Player_Skin_Workspace\DarX_Observador_Redesign.blend"
bpy.ops.wm.save_as_mainfile(filepath=blend_path)
print(f"FILE_SAVED: {blend_path}")

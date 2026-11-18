import bpy
import bmesh
import math
import os
import shutil
from mathutils import Vector, Euler, Matrix

# Reset
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

wep_col = bpy.data.collections.new("Wep_PhaseLance")
scene.collection.children.link(wep_col)

# -------------------------------------------------------------
# UTILITY BUILDERS
# -------------------------------------------------------------
def make_box(name, center, size, chamfer=0.0025, col=wep_col):
    mesh = bpy.data.meshes.new(name + "_Mesh")
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=size, verts=bm.verts)
    bmesh.ops.translate(bm, vec=center, verts=bm.verts)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    if chamfer > 0.0005:
        bev = obj.modifiers.new("Bevel", 'BEVEL')
        bev.width = chamfer
        bev.segments = 2
        bev.limit_method = 'ANGLE'
        bev.angle_limit = math.radians(35)
    return obj

def make_cylinder(name, center, radius, depth, rot_euler=(0, 0, 0), vertices=32, col=wep_col):
    mesh = bpy.data.meshes.new(name + "_Mesh")
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=vertices, radius1=radius, radius2=radius, depth=depth)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = center
    obj.rotation_euler = rot_euler
    col.objects.link(obj)
    return obj

def make_cone(name, center, r1, r2, depth, rot_euler=(0, 0, 0), vertices=24, col=wep_col):
    mesh = bpy.data.meshes.new(name + "_Mesh")
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=vertices, radius1=r1, radius2=r2, depth=depth)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = center
    obj.rotation_euler = rot_euler
    col.objects.link(obj)
    return obj

# -------------------------------------------------------------
# SHADERS: DISCREET ELEGANT PURPLE LIGHTING (NO WASH-OUT)
# -------------------------------------------------------------
mat_ceramic = bpy.data.materials.new(name="M_PhaseLance_Ceramic")
bsdf = mat_ceramic.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.76, 0.78, 0.82, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.32
    bsdf.inputs['Metallic'].default_value = 0.08

mat_metal = bpy.data.materials.new(name="M_PhaseLance_Gunmetal")
bsdf = mat_metal.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.045, 0.048, 0.055, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.22
    bsdf.inputs['Metallic'].default_value = 0.92

mat_rubber = bpy.data.materials.new(name="M_PhaseLance_Rubber")
bsdf = mat_rubber.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.015, 0.015, 0.018, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.65
    bsdf.inputs['Metallic'].default_value = 0.0

# Discreet Rich Violet Emission: calibrated to preserve vivid purple color without burning out to white
mat_glow = bpy.data.materials.new(name="M_PhaseLance_VioletGlow")
bsdf = mat_glow.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.68, 0.10, 1.0, 1.0)
    bsdf.inputs['Emission Color'].default_value = (0.72, 0.14, 1.0, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 8.5 # Discreet, refined luminance

mat_glass = bpy.data.materials.new(name="M_PhaseLance_Glass")
bsdf = mat_glass.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.95, 0.92, 1.0, 1.0)
    bsdf.inputs['Transmission Weight'].default_value = 0.92
    bsdf.inputs['Roughness'].default_value = 0.02
    bsdf.inputs['IOR'].default_value = 1.48

def apply_mat(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)

# -------------------------------------------------------------
# 1. BUTTSTOCK (CULATA)
# -------------------------------------------------------------
stock_socket = make_box("Stock_Socket", (0, -0.155, 0.075), (0.046, 0.035, 0.070), chamfer=0.003)
apply_mat(stock_socket, mat_metal)

stock_main = make_box("Stock_MainBody", (0, -0.235, 0.078), (0.044, 0.13, 0.082), chamfer=0.004)
apply_mat(stock_main, mat_ceramic)

stock_cheek = make_box("Stock_CheekRiser", (0, -0.235, 0.125), (0.040, 0.11, 0.020), chamfer=0.003)
apply_mat(stock_cheek, mat_ceramic)

# 1.1 LUZ DISCRETA: Ranura horizontal empotrada en el reposamejillas
stock_glow = make_box("Stock_GlowSlot", (0, -0.255, 0.128), (0.008, 0.045, 0.004), chamfer=0.0005)
apply_mat(stock_glow, mat_glow)

# 1.2 LUZ DISCRETA: Indicador de bloqueo de culata
stock_led_hinge = make_box("Stock_LED_Hinge", (0.024, -0.155, 0.082), (0.003, 0.012, 0.004), chamfer=0.0005)
apply_mat(stock_led_hinge, mat_glow)

buttpad = make_box("Stock_Buttpad", (0, -0.305, 0.055), (0.046, 0.020, 0.135), chamfer=0.004)
apply_mat(buttpad, mat_rubber)

stock_brace = make_box("Stock_LowerBrace", (0, -0.26, 0.008), (0.034, 0.085, 0.020), chamfer=0.003)
stock_brace.rotation_euler = (math.radians(-24), 0, 0)
apply_mat(stock_brace, mat_ceramic)

# -------------------------------------------------------------
# 2. RECEIVER & CONTROLS
# -------------------------------------------------------------
rec_rear = make_box("Receiver_UpperRear", (0, -0.045, 0.095), (0.052, 0.18, 0.065), chamfer=0.004)
apply_mat(rec_rear, mat_ceramic)

top_rail = make_box("Top_PicatinnyRail", (0, 0.035, 0.134), (0.036, 0.35, 0.015), chamfer=0.002)
apply_mat(top_rail, mat_metal)

# 2.1 LUZ DISCRETA: Hendidura fina de estado a lo largo del lomo superior
top_led = make_box("Receiver_TopSpineLED", (0, 0.02, 0.142), (0.008, 0.26, 0.003), chamfer=0.0005)
apply_mat(top_led, mat_glow)

# 2.2 LUZ DISCRETA: Línea de costura lateral fina bajo el riel (ambos lados)
side_led_r = make_box("Receiver_SideLED_R", (0.027, -0.040, 0.115), (0.002, 0.14, 0.003), chamfer=0.0005)
apply_mat(side_led_r, mat_glow)
side_led_l = make_box("Receiver_SideLED_L", (-0.027, -0.040, 0.115), (0.002, 0.14, 0.003), chamfer=0.0005)
apply_mat(side_led_l, mat_glow)

chassis_floor = make_box("Chassis_FloorBeam", (0, 0.04, 0.045), (0.046, 0.26, 0.025), chamfer=0.003)
apply_mat(chassis_floor, mat_metal)

rec_lower = make_box("Receiver_Lower", (0, -0.02, 0.025), (0.048, 0.15, 0.040), chamfer=0.003)
apply_mat(rec_lower, mat_ceramic)

# 2.3 LUZ DISCRETA: Indicador LED puntual junto al selector de tiro
fire_led = make_cylinder("FireSelector_LED", (0.027, -0.018, 0.052), radius=0.002, depth=0.002, rot_euler=(0, math.radians(90), 0))
apply_mat(fire_led, mat_glow)

# Pistol Grip
bm_grip = bmesh.new()
bmesh.ops.create_cube(bm_grip, size=1.0)
bmesh.ops.scale(bm_grip, vec=(0.034, 0.044, 0.11), verts=bm_grip.verts)
for v in bm_grip.verts:
    if v.co.z < 0:
        v.co.y += (v.co.z * -0.24)
        v.co.x *= 0.94
mesh_grip = bpy.data.meshes.new("PistolGrip_Mesh")
bm_grip.to_mesh(mesh_grip)
bm_grip.free()
obj_grip = bpy.data.objects.new("PistolGrip", mesh_grip)
obj_grip.location = (0, -0.02, -0.045)
obj_grip.rotation_euler = (math.radians(16), 0, 0)
wep_col.objects.link(obj_grip)
bev = obj_grip.modifiers.new("Bevel", 'BEVEL')
bev.width = 0.004
apply_mat(obj_grip, mat_rubber)

# D-Guard
pts_dg = [
    Vector((0, 0.042, 0.008)),
    Vector((0, 0.045, -0.052)),
    Vector((0, -0.018, -0.095))
]
curve_dg = bpy.data.curves.new("DGuard_Curve", type='CURVE')
curve_dg.dimensions = '3D'
poly_dg = curve_dg.splines.new('POLY')
poly_dg.points.add(len(pts_dg) - 1)
for i, pt in enumerate(pts_dg):
    poly_dg.points[i].co = (pt.x, pt.y, pt.z, 1.0)
curve_dg.bevel_depth = 0.008
curve_dg.bevel_resolution = 3
obj_dg = bpy.data.objects.new("DGuard_Loop", curve_dg)
wep_col.objects.link(obj_dg)
apply_mat(obj_dg, mat_metal)

# 2.4 LUZ DISCRETA: Filete de neón morado empotrado en la guarda interior
curve_dgn = bpy.data.curves.new("DGuard_NeonCurve", type='CURVE')
curve_dgn.dimensions = '3D'
poly_dgn = curve_dgn.splines.new('POLY')
poly_dgn.points.add(len(pts_dg) - 1)
for i, pt in enumerate(pts_dg):
    poly_dgn.points[i].co = (pt.x, pt.y, pt.z, 1.0)
curve_dgn.bevel_depth = 0.0025 # Más fina y discreta
curve_dgn.bevel_resolution = 2
obj_dgn = bpy.data.objects.new("DGuard_NeonStrip", curve_dgn)
wep_col.objects.link(obj_dgn)
apply_mat(obj_dgn, mat_glow)

# Trigger
trigger = make_box("Trigger", (0, 0.014, -0.010), (0.008, 0.014, 0.028), chamfer=0.002)
trigger.rotation_euler = (math.radians(-14), 0, 0)
apply_mat(trigger, mat_metal)

# Fire selector switch
selector = make_cylinder("FireSelector", (0.026, -0.025, 0.045), radius=0.009, depth=0.006, rot_euler=(0, math.radians(90), 0))
apply_mat(selector, mat_metal)

# -------------------------------------------------------------
# 3. EXPOSED PLASMA REACTOR CHAMBER
# -------------------------------------------------------------
rec_front = make_box("Receiver_UpperFront", (0, 0.185, 0.095), (0.052, 0.035, 0.065), chamfer=0.003)
apply_mat(rec_front, mat_ceramic)

reactor_glass = make_cylinder("Reactor_GlassBulb", (0, 0.110, 0.095), radius=0.022, depth=0.095, rot_euler=(math.radians(90), 0, 0), vertices=32)
apply_mat(reactor_glass, mat_glass)

# 3.1 LUZ DISCRETA: Núcleo de plasma contenido dentro del bulbo
reactor_core = make_cylinder("Reactor_PlasmaCore", (0, 0.110, 0.095), radius=0.012, depth=0.080, rot_euler=(math.radians(90), 0, 0), vertices=24)
apply_mat(reactor_core, mat_glow)

cap_r = make_cylinder("Reactor_CoilRear", (0, 0.065, 0.095), radius=0.024, depth=0.014, rot_euler=(math.radians(90), 0, 0), vertices=24)
apply_mat(cap_r, mat_metal)
cap_f = make_cylinder("Reactor_CoilFront", (0, 0.155, 0.095), radius=0.024, depth=0.014, rot_euler=(math.radians(90), 0, 0), vertices=24)
apply_mat(cap_f, mat_metal)

cage_top = make_box("Reactor_CageTopBar", (0.024, 0.110, 0.122), (0.008, 0.090, 0.008), chamfer=0.001)
apply_mat(cage_top, mat_ceramic)
cage_bot = make_box("Reactor_CageBotBar", (0.024, 0.110, 0.068), (0.008, 0.090, 0.008), chamfer=0.001)
apply_mat(cage_bot, mat_ceramic)

mag_cowl = make_box("Reactor_UnderCowl", (0, 0.100, 0.020), (0.044, 0.085, 0.035), chamfer=0.003)
apply_mat(mag_cowl, mat_ceramic)

battery = make_box("Battery_Module", (0, 0.110, -0.018), (0.038, 0.060, 0.045), chamfer=0.003)
battery.rotation_euler = (math.radians(16), 0, 0)
apply_mat(battery, mat_metal)

# 3.2 LUZ DISCRETA: 3 Micro-LEDs de estado de carga en la batería
for i_led, y_led in enumerate([-0.012, 0.0, 0.012]):
    b_led = make_box(f"Battery_LED_{i_led}", (0.020, 0.110 + y_led, -0.032), (0.002, 0.008, 0.004), chamfer=0.0005)
    b_led.rotation_euler = (math.radians(16), 0, 0)
    apply_mat(b_led, mat_glow)

# -------------------------------------------------------------
# 4. FRONT PHASE LANCE SYSTEM
# -------------------------------------------------------------
# Top Lance Rail
bm_tl = bmesh.new()
bmesh.ops.create_cube(bm_tl, size=1.0)
bmesh.ops.scale(bm_tl, vec=(0.044, 0.38, 0.028), verts=bm_tl.verts)
bmesh.ops.translate(bm_tl, vec=(0, 0.38, 0.125), verts=bm_tl.verts)
for v in bm_tl.verts:
    if v.co.y > 0.38:
        factor = (v.co.y - 0.38) / 0.19
        v.co.x *= (1.0 - factor * 0.45)
        v.co.z -= factor * 0.014
mesh_tl = bpy.data.meshes.new("TopLanceRail_Mesh")
bm_tl.to_mesh(mesh_tl)
bm_tl.free()
top_lance = bpy.data.objects.new("TopLanceRail", mesh_tl)
wep_col.objects.link(top_lance)
bev = top_lance.modifiers.new("Bevel", 'BEVEL')
bev.width = 0.003
apply_mat(top_lance, mat_ceramic)

# 4.1 LUZ DISCRETA: Guía de haz de fibra óptica violeta incrustada en el lateral del riel superior
lance_fiber_r = make_box("TopLance_Fiber_R", (0.023, 0.38, 0.126), (0.002, 0.34, 0.003), chamfer=0.0005)
apply_mat(lance_fiber_r, mat_glow)

# Bottom Blade Rail
bm_bb = bmesh.new()
bmesh.ops.create_cube(bm_bb, size=1.0)
bmesh.ops.scale(bm_bb, vec=(0.040, 0.48, 0.030), verts=bm_bb.verts)
bmesh.ops.translate(bm_bb, vec=(0, 0.42, 0.022), verts=bm_bb.verts)
for v in bm_bb.verts:
    if v.co.y > 0.42:
        factor = (v.co.y - 0.42) / 0.24
        v.co.x *= (1.0 - factor * 0.50)
        if v.co.z < 0.022:
            v.co.z += factor * 0.018
mesh_bb = bpy.data.meshes.new("BottomBladeRail_Mesh")
bm_bb.to_mesh(mesh_bb)
bm_bb.free()
bot_blade = bpy.data.objects.new("BottomBladeRail", mesh_bb)
wep_col.objects.link(bot_blade)
bev = bot_blade.modifiers.new("Bevel", 'BEVEL')
bev.width = 0.003
apply_mat(bot_blade, mat_ceramic)

# 4.2 LUZ DISCRETA: Fino filo emisor morado en el bisel inferior de la hoja
blade_neon = make_box("BottomBlade_NeonEdge", (0, 0.42, 0.007), (0.006, 0.46, 0.003), chamfer=0.0005)
apply_mat(blade_neon, mat_glow)

# -------------------------------------------------------------
# 5. COLLIMATOR ARRAY & BEAM TUBE
# -------------------------------------------------------------
beam_glass = make_cylinder("BeamVacuumTube", (0, 0.38, 0.075), radius=0.013, depth=0.35, rot_euler=(math.radians(90), 0, 0), vertices=32)
apply_mat(beam_glass, mat_glass)

# 5.1 LUZ DISCRETA: Haz central focalizado contenido en el tubo
laser_core = make_cylinder("LaserBeamCore", (0, 0.38, 0.075), radius=0.004, depth=0.36, rot_euler=(math.radians(90), 0, 0), vertices=16)
apply_mat(laser_core, mat_glow)

# 4 Colimadores magnéticos con anillos de energía morada discretos
collimator_positions = [0.25, 0.33, 0.41, 0.49]
for idx, y_c in enumerate(collimator_positions):
    c_rear = make_cone(f"Collimator_Rear_{idx}", (0, y_c - 0.009, 0.075), r1=0.019, r2=0.013, depth=0.018, rot_euler=(math.radians(90), 0, 0))
    apply_mat(c_rear, mat_metal)
    c_front = make_cone(f"Collimator_Front_{idx}", (0, y_c + 0.009, 0.075), r1=0.013, r2=0.019, depth=0.018, rot_euler=(math.radians(90), 0, 0))
    apply_mat(c_front, mat_metal)
    c_ring = make_cylinder(f"Collimator_Ring_{idx}", (0, y_c, 0.075), radius=0.020, depth=0.005, rot_euler=(math.radians(90), 0, 0))
    apply_mat(c_ring, mat_metal)
    # 5.2 LUZ DISCRETA: Anillo interno iluminado en la garganta del colimador
    glow_ring = make_cylinder(f"Collimator_Glow_{idx}", (0, y_c, 0.075), radius=0.014, depth=0.003, rot_euler=(math.radians(90), 0, 0))
    apply_mat(glow_ring, mat_glow)
    riser = make_box(f"Collimator_Bracket_{idx}", (0, y_c, 0.046), (0.022, 0.010, 0.024), chamfer=0.002)
    apply_mat(riser, mat_metal)

nozzle = make_cylinder("EmitterNozzle", (0, 0.55, 0.075), radius=0.021, depth=0.020, rot_euler=(math.radians(90), 0, 0), vertices=32)
apply_mat(nozzle, mat_metal)

# Haz de disparo frontal de salida
forward_laser = make_cylinder("ForwardLaserPulse", (0, 0.73, 0.075), radius=0.004, depth=0.34, rot_euler=(math.radians(90), 0, 0), vertices=16)
apply_mat(forward_laser, mat_glow)

# -------------------------------------------------------------
# 6. RENDER SETUP
# -------------------------------------------------------------
studio_col = bpy.data.collections.new("StudioCol")
scene.collection.children.link(studio_col)

if not scene.world:
    scene.world = bpy.data.worlds.new("World")
scene.world.use_nodes = True
bg = scene.world.node_tree.nodes.get("Background")
if bg:
    bg.inputs['Color'].default_value = (0.010, 0.012, 0.018, 1.0)
    bg.inputs['Strength'].default_value = 0.20

mesh_f = bpy.data.meshes.new("FloorMesh")
bm = bmesh.new()
bmesh.ops.create_grid(bm, size=15)
bm.to_mesh(mesh_f)
bm.free()
fl = bpy.data.objects.new("StudioFloor", mesh_f)
fl.location = (0, 0, -0.15)
studio_col.objects.link(fl)

mat_fl = bpy.data.materials.new(name="M_StudioFloor")
bsdf = mat_fl.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.018, 0.020, 0.025, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.20
    bsdf.inputs['Metallic'].default_value = 0.4
fl.data.materials.append(mat_fl)

# Studio Lights
lk = bpy.data.lights.new("KeyLight", 'AREA')
lk.energy = 60.0
lk.size = 1.8
lk.color = (0.92, 0.95, 1.0)
olk = bpy.data.objects.new("KeyLight", lk)
olk.location = (1.8, 0.20, 1.2)
olk.rotation_euler = (0.7, 0.2, 1.1)
studio_col.objects.link(olk)

lr = bpy.data.lights.new("RimLight", 'AREA')
lr.energy = 85.0
lr.size = 2.5
lr.color = (0.68, 0.15, 1.0)
olr = bpy.data.objects.new("RimLight", lr)
olr.location = (-1.8, 0.35, 1.0)
olr.rotation_euler = (-0.7, -0.3, -1.8)
studio_col.objects.link(olr)

lf = bpy.data.lights.new("FillLight", 'AREA')
lf.energy = 18.0
lf.size = 2.0
lf.color = (0.6, 0.8, 1.0)
olf = bpy.data.objects.new("FillLight", lf)
olf.location = (0.2, -1.5, 0.7)
olf.rotation_euler = (1.1, 0, 0)
studio_col.objects.link(olf)

scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100

cam_data = bpy.data.cameras.new("Cam")
cam_obj = bpy.data.objects.new("Cam", cam_data)
studio_col.objects.link(cam_obj)
scene.camera = cam_obj

brain_dir = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"
out_dir = r"E:\Darx_Proyect\Art\Blender"

views = [
    ("quad1_hero_side.png", (1.80, 0.18, 0.18), Vector((0, 0.18, 0.065)), 48),
    ("quad2_iso_front.png", (1.25, 0.85, 0.28), Vector((0, 0.32, 0.065)), 44),
    ("quad3_fps_view.png", (0.0, -0.42, 0.160), Vector((0.0, 0.55, 0.130)), 46),
    ("quad4_rear_detail.png", (1.15, -0.32, 0.18), Vector((0, -0.08, 0.04)), 46)
]

for fname, cam_loc, target, lens in views:
    cam_data.lens = lens
    cam_obj.location = cam_loc
    direction = target - Vector(cam_loc)
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam_obj.rotation_euler = rot_quat.to_euler()
    
    out_file = os.path.join(out_dir, fname)
    scene.render.filepath = out_file
    bpy.ops.render.render(write_still=True)
    
    dest = os.path.join(brain_dir, fname)
    shutil.copyfile(out_file, dest)
    print(f"Rendered and copied {fname}")

master_save = r"E:\Darx_Proyect\Art\Blender\SM_Wep_PhaseLance_Workspace.blend"
bpy.ops.wm.save_as_mainfile(filepath=master_save)
print("Workspace saved to:", master_save)
print("=== RENDER COMPLETE ===")

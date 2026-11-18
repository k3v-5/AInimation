import bpy
import bmesh
import math
import os
import shutil
from mathutils import Vector, Euler, Matrix

# Reset scene
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

pistol_col = bpy.data.collections.new("Wep_PhasePistol")
scene.collection.children.link(pistol_col)

# -------------------------------------------------------------
# SHADERS (METALLIC INDIGO TITANIUM + DISCREET VIOLET EMISSION)
# -------------------------------------------------------------
# 1. Anodized Midnight Indigo Titanium Metallic Chassis
mat_indigo = bpy.data.materials.new(name="M_Pistol_IndigoTitanium")
mat_indigo.use_nodes = True
bsdf = mat_indigo.node_tree.nodes.get("Principled BSDF")
if bsdf:
    # Deep royal indigo-purple titanium
    bsdf.inputs['Base Color'].default_value = (0.08, 0.045, 0.16, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.28
    bsdf.inputs['Metallic'].default_value = 0.90

# 2. Gunmetal / Mechanical Carbon Chassis Alloy
mat_gunmetal = bpy.data.materials.new(name="M_Pistol_Gunmetal")
mat_gunmetal.use_nodes = True
bsdf = mat_gunmetal.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.035, 0.038, 0.045, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.24
    bsdf.inputs['Metallic'].default_value = 0.85

# 3. Tactical Matte Rubber Grip Panels
mat_rubber = bpy.data.materials.new(name="M_Pistol_Rubber")
mat_rubber.use_nodes = True
bsdf = mat_rubber.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.015, 0.015, 0.018, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.70
    bsdf.inputs['Metallic'].default_value = 0.0

# 4. Polished Chrome Accents (Collimator Rings & Caps)
mat_chrome = bpy.data.materials.new(name="M_Pistol_Chrome")
mat_chrome.use_nodes = True
bsdf = mat_chrome.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.75, 0.76, 0.80, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.14
    bsdf.inputs['Metallic'].default_value = 0.98

# 5. Discreet Rich Violet LED Glow (Calibrated: Doesn't wash out to white!)
mat_glow = bpy.data.materials.new(name="M_Pistol_VioletGlow")
mat_glow.use_nodes = True
bsdf = mat_glow.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.65, 0.08, 1.0, 1.0)
    bsdf.inputs['Emission Color'].default_value = (0.68, 0.10, 1.0, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 7.5

# 6. Reactor High-Energy Plasma Filament
mat_plasma = bpy.data.materials.new(name="M_Pistol_PlasmaCore")
mat_plasma.use_nodes = True
bsdf = mat_plasma.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.78, 0.18, 1.0, 1.0)
    bsdf.inputs['Emission Color'].default_value = (0.80, 0.20, 1.0, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 9.5

# 7. Quartz Vacuum Glass Tube
mat_glass = bpy.data.materials.new(name="M_Pistol_QuartzGlass")
mat_glass.use_nodes = True
bsdf = mat_glass.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.92, 0.90, 1.0, 1.0)
    bsdf.inputs['Transmission Weight'].default_value = 0.94
    bsdf.inputs['Roughness'].default_value = 0.05
    bsdf.inputs['IOR'].default_value = 1.48

def apply_mat(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)

def make_box(name, center, size, chamfer=0.002, col=pistol_col):
    mesh = bpy.data.meshes.new(name + "_Mesh")
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=size, verts=bm.verts)
    bmesh.ops.translate(bm, vec=center, verts=bm.verts)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    if chamfer > 0.0003:
        bev = obj.modifiers.new("Bevel", 'BEVEL')
        bev.width = chamfer
        bev.segments = 2
        bev.limit_method = 'ANGLE'
        bev.angle_limit = math.radians(35)
    return obj

def make_cylinder(name, center, radius, depth, rot_euler=(0, 0, 0), vertices=32, col=pistol_col):
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

def make_cone(name, center, r1, r2, depth, rot_euler=(0, 0, 0), vertices=24, col=pistol_col):
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
# 1. REAR END & UPPER RECEIVER (TACTICAL COMPACT HANDGUN PROFILE)
# -------------------------------------------------------------
# Rear buffer cap with QD sling mount port
rear_cap = make_box("Pistol_RearCap", (0, -0.078, 0.074), (0.044, 0.020, 0.058), chamfer=0.0025)
apply_mat(rear_cap, mat_gunmetal)

qd_port = make_cylinder("Pistol_QDPort", (0.023, -0.078, 0.065), radius=0.006, depth=0.004, rot_euler=(0, math.radians(90), 0))
apply_mat(qd_port, mat_chrome)

# Rear Combat Iron Sight (Dual purple dots with notch)
sight_rear_base = make_box("Pistol_RearSightBase", (0, -0.066, 0.116), (0.024, 0.020, 0.014), chamfer=0.001)
apply_mat(sight_rear_base, mat_gunmetal)
for s_x in [-0.007, 0.007]:
    dot = make_box(f"Pistol_SightDot_{s_x}", (s_x, -0.074, 0.121), (0.002, 0.003, 0.002), chamfer=0.0003)
    apply_mat(dot, mat_glow)

# Upper Receiver Main Body (Midnight Indigo Titanium)
rec_upper = make_box("Pistol_UpperReceiver", (0, -0.010, 0.082), (0.048, 0.116, 0.054), chamfer=0.003)
apply_mat(rec_upper, mat_indigo)

# Beveled side detail plates
for s_x in [-0.025, 0.025]:
    rec_plate = make_box(f"Pistol_RecPlate_{s_x}", (s_x, -0.010, 0.082), (0.003, 0.100, 0.038), chamfer=0.0015)
    apply_mat(rec_plate, mat_gunmetal)

# "Z" Phase EM badge on right flank
z_badge = make_box("Pistol_ZBadge", (0.027, -0.015, 0.085), (0.002, 0.028, 0.024), chamfer=0.001)
apply_mat(z_badge, mat_chrome)

# Top Picatinny Rail
top_rail = make_box("Pistol_TopRail", (0, 0.040, 0.114), (0.032, 0.220, 0.012), chamfer=0.0012)
apply_mat(top_rail, mat_gunmetal)

# LUZ DISCRETA 1: Micro-guía LED superior en el lomo
top_led_strip = make_box("Pistol_TopLEDStrip", (0, 0.040, 0.121), (0.006, 0.190, 0.002), chamfer=0.0004)
apply_mat(top_led_strip, mat_glow)

# -------------------------------------------------------------
# 2. LOWER RECEIVER, PISTOL GRIP & ANGLED D-GUARD
# -------------------------------------------------------------
rec_lower = make_box("Pistol_LowerChassis", (0, -0.010, 0.032), (0.044, 0.105, 0.044), chamfer=0.0025)
apply_mat(rec_lower, mat_indigo)

# Ergonomic Pistol Grip (16 deg backward tilt, 10cm grip height)
bm_grip = bmesh.new()
bmesh.ops.create_cube(bm_grip, size=1.0)
bmesh.ops.scale(bm_grip, vec=(0.030, 0.040, 0.098), verts=bm_grip.verts)
for v in bm_grip.verts:
    if v.co.z < 0:
        v.co.y += (v.co.z * -0.22)
        v.co.x *= 0.94
mesh_grip = bpy.data.meshes.new("PistolGrip_Mesh")
bm_grip.to_mesh(mesh_grip)
bm_grip.free()
obj_grip = bpy.data.objects.new("PistolGrip", mesh_grip)
obj_grip.location = (0, -0.018, -0.036)
obj_grip.rotation_euler = (math.radians(16), 0, 0)
pistol_col.objects.link(obj_grip)
bev_grip = obj_grip.modifiers.new("Bevel", 'BEVEL')
bev_grip.width = 0.003
apply_mat(obj_grip, mat_rubber)

# Carbon Grip Side Inlays
for s_x in [-0.016, 0.016]:
    g_panel = make_box(f"Pistol_GripPanel_{s_x}", (s_x, -0.018, -0.036), (0.0025, 0.030, 0.065), chamfer=0.001)
    g_panel.rotation_euler = (math.radians(16), 0, 0)
    apply_mat(g_panel, mat_gunmetal)

# CONTINUOUS GEOMETRIC D-GUARD (Faithful angled loop to base of grip)
pts_dg = [
    Vector((0, 0.034, 0.010)),
    Vector((0, 0.038, -0.048)),
    Vector((0, -0.014, -0.082))
]
curve_dg = bpy.data.curves.new("DGuard_Curve", type='CURVE')
curve_dg.dimensions = '3D'
poly_dg = curve_dg.splines.new('POLY')
poly_dg.points.add(len(pts_dg) - 1)
for i, pt in enumerate(pts_dg):
    poly_dg.points[i].co = (pt.x, pt.y, pt.z, 1.0)
curve_dg.bevel_depth = 0.006
curve_dg.bevel_resolution = 3
obj_dg = bpy.data.objects.new("Pistol_DGuard", curve_dg)
pistol_col.objects.link(obj_dg)
apply_mat(obj_dg, mat_gunmetal)

# LUZ DISCRETA 2: Filete neón morado empotrado en la D-Guard (exacto a la referencia)
curve_dgn = bpy.data.curves.new("DGuard_Neon", type='CURVE')
curve_dgn.dimensions = '3D'
poly_dgn = curve_dgn.splines.new('POLY')
poly_dgn.points.add(len(pts_dg) - 1)
for i, pt in enumerate(pts_dg):
    poly_dgn.points[i].co = (pt.x, pt.y, pt.z, 1.0)
curve_dgn.bevel_depth = 0.0020
curve_dgn.bevel_resolution = 2
obj_dgn = bpy.data.objects.new("Pistol_DGuard_Neon", curve_dgn)
pistol_col.objects.link(obj_dgn)
apply_mat(obj_dgn, mat_glow)

trigger = make_box("Pistol_Trigger", (0, 0.010, -0.005), (0.007, 0.012, 0.024), chamfer=0.001)
trigger.rotation_euler = (math.radians(-15), 0, 0)
apply_mat(trigger, mat_gunmetal)

selector = make_cylinder("Pistol_Selector", (0.024, -0.020, 0.045), radius=0.007, depth=0.005, rot_euler=(0, math.radians(90), 0))
apply_mat(selector, mat_gunmetal)

# -------------------------------------------------------------
# 3. OPEN PLASMA REACTOR WINDOW (100% VISIBLE & GLOWING)
# -------------------------------------------------------------
# Frame borders surrounding the open window (NOT solid blocks!):
# Top frame bridge:
win_top = make_box("Pistol_ReactorWinTop", (0, 0.102, 0.106), (0.046, 0.088, 0.012), chamfer=0.0015)
apply_mat(win_top, mat_gunmetal)
# Bottom frame bridge:
win_bot = make_box("Pistol_ReactorWinBot", (0, 0.102, 0.058), (0.046, 0.088, 0.012), chamfer=0.0015)
apply_mat(win_bot, mat_gunmetal)
# Rear frame pillar:
win_rear = make_box("Pistol_ReactorWinRear", (0, 0.056, 0.082), (0.046, 0.016, 0.040), chamfer=0.0015)
apply_mat(win_rear, mat_gunmetal)
# Front frame pillar:
win_front = make_box("Pistol_ReactorWinFront", (0, 0.146, 0.082), (0.046, 0.016, 0.040), chamfer=0.0015)
apply_mat(win_front, mat_gunmetal)

# Outer Glass Ampoule inside the open window
reactor_glass = make_cylinder("Pistol_ReactorGlass", (0, 0.102, 0.082), radius=0.015, depth=0.072, rot_euler=(math.radians(90), 0, 0), vertices=32)
apply_mat(reactor_glass, mat_glass)

# Internal Intense Plasma Filament / Core
reactor_core = make_cylinder("Pistol_ReactorCore", (0, 0.102, 0.082), radius=0.0065, depth=0.064, rot_euler=(math.radians(90), 0, 0), vertices=16)
apply_mat(reactor_core, mat_plasma)

# Magnetic Confinement Cap Ends
cap_rear = make_cone("Pistol_ReactorCap_R", (0, 0.064, 0.082), r1=0.017, r2=0.011, depth=0.012, rot_euler=(math.radians(-90), 0, 0))
apply_mat(cap_rear, mat_chrome)
cap_front = make_cone("Pistol_ReactorCap_F", (0, 0.140, 0.082), r1=0.011, r2=0.017, depth=0.012, rot_euler=(math.radians(-90), 0, 0))
apply_mat(cap_front, mat_chrome)

# 3 Inner chrome confinement rings along the ampoule
for r_y in [0.086, 0.102, 0.118]:
    c_amp_ring = make_cylinder(f"Pistol_AmpRing_{r_y}", (0, r_y, 0.082), radius=0.0162, depth=0.003, rot_euler=(math.radians(90), 0, 0))
    apply_mat(c_amp_ring, mat_chrome)

# Local violet point light inside the reactor (Casts genuine purple glow onto the gun body!)
light_reactor = bpy.data.lights.new("Light_ReactorInternal", 'POINT')
light_reactor.energy = 3.5
light_reactor.color = (0.72, 0.12, 1.0)
obj_lr = bpy.data.objects.new("Light_ReactorInternal", light_reactor)
obj_lr.location = (0, 0.102, 0.082)
pistol_col.objects.link(obj_lr)

# LUZ DISCRETA 3: Barra LED horizontal morada superior del reactor (solicitada explícitamente)
reactor_led_top = make_box("Pistol_ReactorLED_Top", (0.024, 0.102, 0.108), (0.002, 0.052, 0.0035), chamfer=0.0004)
apply_mat(reactor_led_top, mat_glow)

# LUZ DISCRETA 4: Acento LED diagonal inferior bajo el reactor (exacto a la imagen)
reactor_led_bot = make_box("Pistol_ReactorLED_Bot", (0.024, 0.084, 0.054), (0.002, 0.034, 0.0035), chamfer=0.0004)
reactor_led_bot.rotation_euler = (0, math.radians(-25), 0)
apply_mat(reactor_led_bot, mat_glow)

# Battery Module flush beneath reactor
battery_cowl = make_box("Pistol_BatteryCowl", (0, 0.096, 0.016), (0.040, 0.076, 0.026), chamfer=0.002)
apply_mat(battery_cowl, mat_indigo)

# -------------------------------------------------------------
# 4. FRONT PHASE SYSTEM (COMPACT PISTOL COWL & BLADE)
# -------------------------------------------------------------
# Upper Shroud (Compact: extends to Y=0.290 with forward angled chisel tip)
bm_us = bmesh.new()
bmesh.ops.create_cube(bm_us, size=1.0)
bmesh.ops.scale(bm_us, vec=(0.042, 0.150, 0.026), verts=bm_us.verts)
bmesh.ops.translate(bm_us, vec=(0, 0.215, 0.106), verts=bm_us.verts)
for v in bm_us.verts:
    if v.co.y > 0.230:
        f = (v.co.y - 0.230) / 0.060
        v.co.x *= (1.0 - f * 0.35)
        if v.co.z > 0.106:
            v.co.z -= f * 0.014
mesh_us = bpy.data.meshes.new("Pistol_UpperShroud_Mesh")
bm_us.to_mesh(mesh_us)
bm_us.free()
obj_us = bpy.data.objects.new("Pistol_UpperShroud", mesh_us)
pistol_col.objects.link(obj_us)
bev_us = obj_us.modifiers.new("Bevel", 'BEVEL')
bev_us.width = 0.002
apply_mat(obj_us, mat_indigo)

# Front Iron Sight Post with purple fiber bead
front_sight = make_box("Pistol_FrontSight", (0, 0.280, 0.114), (0.012, 0.010, 0.014), chamfer=0.001)
apply_mat(front_sight, mat_gunmetal)
front_dot = make_box("Pistol_FrontDot", (0, 0.282, 0.118), (0.002, 0.003, 0.002), chamfer=0.0003)
apply_mat(front_dot, mat_glow)

# LUZ DISCRETA 5: Guía de fibra óptica superior en el lateral
fiber_top = make_box("Pistol_FiberTop_R", (0.022, 0.215, 0.106), (0.002, 0.130, 0.003), chamfer=0.0004)
apply_mat(fiber_top, mat_glow)

# Lower Shroud / Compact Underside Blade (Extends forward to Y=0.320 with forward-down chisel point)
bm_ls = bmesh.new()
bmesh.ops.create_cube(bm_ls, size=1.0)
bmesh.ops.scale(bm_ls, vec=(0.040, 0.240, 0.028), verts=bm_ls.verts)
bmesh.ops.translate(bm_ls, vec=(0, 0.200, 0.016), verts=bm_ls.verts)
for v in bm_ls.verts:
    if v.co.y > 0.230:
        f = (v.co.y - 0.230) / 0.090
        v.co.x *= (1.0 - f * 0.45)
        if v.co.z < 0.016:
            v.co.z += f * 0.018
mesh_ls = bpy.data.meshes.new("Pistol_LowerBlade_Mesh")
bm_ls.to_mesh(mesh_ls)
bm_ls.free()
obj_ls = bpy.data.objects.new("Pistol_LowerBlade", mesh_ls)
pistol_col.objects.link(obj_ls)
bev_ls = obj_ls.modifiers.new("Bevel", 'BEVEL')
bev_ls.width = 0.0025
apply_mat(obj_ls, mat_indigo)

# LUZ DISCRETA 6: Filo de neón morado en el bisel inferior de la hoja (exacto a la referencia)
blade_neon = make_box("Pistol_BladeNeonEdge", (0, 0.200, 0.003), (0.003, 0.230, 0.0025), chamfer=0.0004)
apply_mat(blade_neon, mat_glow)

# -------------------------------------------------------------
# 5. COMPACT COLLIMATOR CHAMBER & BEAM TUBE
# -------------------------------------------------------------
# Central Quartz Beam Vacuum Tube
beam_tube = make_cylinder("Pistol_BeamTube", (0, 0.210, 0.062), radius=0.012, depth=0.150, rot_euler=(math.radians(90), 0, 0), vertices=32)
apply_mat(beam_tube, mat_glass)

# Internal glowing violet beam core
beam_core = make_cylinder("Pistol_BeamCore", (0, 0.210, 0.062), radius=0.0035, depth=0.155, rot_euler=(math.radians(90), 0, 0), vertices=16)
apply_mat(beam_core, mat_plasma)

# 4 Collimator Coils in Compact Cluster (3.5cm spacing)
collimator_y = [0.155, 0.190, 0.225, 0.260]
for idx, cy in enumerate(collimator_y):
    cr = make_cone(f"Pistol_CollCone_R_{idx}", (0, cy - 0.005, 0.062), r1=0.016, r2=0.012, depth=0.010, rot_euler=(math.radians(90), 0, 0))
    apply_mat(cr, mat_gunmetal)
    cf = make_cone(f"Pistol_CollCone_F_{idx}", (0, cy + 0.005, 0.062), r1=0.012, r2=0.016, depth=0.010, rot_euler=(math.radians(90), 0, 0))
    apply_mat(cf, mat_gunmetal)
    c_ring = make_cylinder(f"Pistol_CollRing_{idx}", (0, cy, 0.062), radius=0.0175, depth=0.0035, rot_euler=(math.radians(90), 0, 0))
    apply_mat(c_ring, mat_chrome)
    # LUZ DISCRETA 7: Anillo interno morado en cada colimador
    g_ring = make_cylinder(f"Pistol_CollGlow_{idx}", (0, cy, 0.062), radius=0.0132, depth=0.002, rot_euler=(math.radians(90), 0, 0))
    apply_mat(g_ring, mat_glow)
    bracket = make_box(f"Pistol_CollBracket_{idx}", (0, cy, 0.038), (0.018, 0.006, 0.020), chamfer=0.001)
    apply_mat(bracket, mat_gunmetal)

# Front Muzzle Emitter Nozzle at Y=0.280
muzzle = make_cylinder("Pistol_MuzzleNozzle", (0, 0.280, 0.062), radius=0.018, depth=0.014, rot_euler=(math.radians(90), 0, 0), vertices=32)
apply_mat(muzzle, mat_chrome)

# Focused laser pulse beam emerging from the nozzle
laser_burst = make_cone("Pistol_LaserBurst", (0, 0.325, 0.062), r1=0.0035, r2=0.007, depth=0.075, rot_euler=(math.radians(-90), 0, 0), vertices=16)
apply_mat(laser_burst, mat_plasma)

# -------------------------------------------------------------
# 6. HIGH-CONTRAST SCI-FI STUDIO RENDER (EEVEE)
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

mesh_tab = bpy.data.meshes.new("TableMesh")
bm_t = bmesh.new()
bmesh.ops.create_grid(bm_t, size=8)
bm_t.to_mesh(mesh_tab)
bm_t.free()
tab = bpy.data.objects.new("StudioTable", mesh_tab)
tab.location = (0, 0.15, -0.12)
studio_col.objects.link(tab)
mat_tab = bpy.data.materials.new(name="M_StudioTable")
mat_tab.use_nodes = True
bsdf = mat_tab.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.018, 0.020, 0.025, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.20
    bsdf.inputs['Metallic'].default_value = 0.4
tab.data.materials.append(mat_tab)

# Studio Lights
lk = bpy.data.lights.new("KeyLight", 'AREA')
lk.energy = 50.0
lk.size = 1.2
lk.color = (0.92, 0.95, 1.0)
olk = bpy.data.objects.new("KeyLight", lk)
olk.location = (1.0, 0.15, 0.8)
olk.rotation_euler = (0.7, 0.2, 1.1)
studio_col.objects.link(olk)

lr = bpy.data.lights.new("RimLight", 'AREA')
lr.energy = 70.0
lr.size = 1.8
lr.color = (0.68, 0.15, 1.0)
olr = bpy.data.objects.new("RimLight", lr)
olr.location = (-1.0, 0.25, 0.65)
olr.rotation_euler = (-0.7, -0.3, -1.8)
studio_col.objects.link(olr)

lf = bpy.data.lights.new("FillLight", 'AREA')
lf.energy = 14.0
lf.size = 1.5
lf.color = (0.6, 0.8, 1.0)
olf = bpy.data.objects.new("FillLight", lf)
olf.location = (0.2, -0.9, 0.45)
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
    # 1. Hero Side Profile (Closer framing of compact handgun proportions)
    ("pistol_quad1_hero_side.png", (0.85, 0.12, 0.08), Vector((0, 0.12, 0.035)), 52),
    # 2. Front 3/4 Perspective (Showing collimator cluster, muzzle and depth)
    ("pistol_quad2_iso_front.png", (0.68, 0.38, 0.15), Vector((0, 0.16, 0.035)), 48),
    # 3. FPS / ADS View (Perfect eye alignment over rear sight notch looking at front bead)
    ("pistol_quad3_fps_view.png", (0.0, -0.22, 0.136), Vector((0.0, 0.30, 0.114)), 46),
    # 4. Rear 3/4 Detail (Dynamic perspective of grip, D-guard and reactor window)
    ("pistol_quad4_rear_detail.png", (0.60, -0.15, 0.12), Vector((0, 0.04, 0.025)), 50)
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
    print(f'Rendered and copied {fname}')

master_save = r"E:\Darx_Proyect\Art\Blender\SM_Wep_PhasePistol_Workspace.blend"
bpy.ops.wm.save_as_mainfile(filepath=master_save)
print('Workspace saved to:', master_save)
print('=== PISTOL V3 RENDER COMPLETE ===')

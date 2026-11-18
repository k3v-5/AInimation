import bpy
import bmesh
import math
import os
import shutil
from mathutils import Vector, Euler, Matrix

# Reset scene
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

shotgun_col = bpy.data.collections.new("Wep_PhaseShotgun")
scene.collection.children.link(shotgun_col)

# -------------------------------------------------------------
# SHADERS (METALLIC INDIGO TITANIUM + HEAVY GUNMETAL + VIOLET GLOW)
# -------------------------------------------------------------
# 1. Anodized Midnight Indigo Titanium Chassis
mat_indigo = bpy.data.materials.new(name="M_Shotgun_IndigoTitanium")
mat_indigo.use_nodes = True
bsdf = mat_indigo.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.09, 0.05, 0.18, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.28
    bsdf.inputs['Metallic'].default_value = 0.90

# 2. Heavy Gunmetal / Weathered Steel for 4 Barrels & Mechanism
mat_gunmetal = bpy.data.materials.new(name="M_Shotgun_Gunmetal")
mat_gunmetal.use_nodes = True
bsdf = mat_gunmetal.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.040, 0.042, 0.048, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.24
    bsdf.inputs['Metallic'].default_value = 0.88

# 3. Tactical Matte Rubber / Carbon Fiber Composite (Pump & Grips)
mat_carbon = bpy.data.materials.new(name="M_Shotgun_Carbon")
mat_carbon.use_nodes = True
bsdf = mat_carbon.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.015, 0.015, 0.018, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.65
    bsdf.inputs['Metallic'].default_value = 0.0

# 4. Machined Alloy / Chrome (Buffer Tube, Rings & Accents)
mat_chrome = bpy.data.materials.new(name="M_Shotgun_Chrome")
mat_chrome.use_nodes = True
bsdf = mat_chrome.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.65, 0.66, 0.70, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.18
    bsdf.inputs['Metallic'].default_value = 0.95

# 5. Discreet Rich Violet LED Glow
mat_glow = bpy.data.materials.new(name="M_Shotgun_VioletGlow")
mat_glow.use_nodes = True
bsdf = mat_glow.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.65, 0.08, 1.0, 1.0)
    bsdf.inputs['Emission Color'].default_value = (0.70, 0.12, 1.0, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 8.0

# 6. Reactor Intense Plasma Filament Core
mat_plasma = bpy.data.materials.new(name="M_Shotgun_PlasmaCore")
mat_plasma.use_nodes = True
bsdf = mat_plasma.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.80, 0.22, 1.0, 1.0)
    bsdf.inputs['Emission Color'].default_value = (0.85, 0.25, 1.0, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 11.0

# 7. Quartz Glass Tube & Ampoule
mat_glass = bpy.data.materials.new(name="M_Shotgun_QuartzGlass")
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

def make_box(name, center, size, chamfer=0.002, col=shotgun_col):
    mesh = bpy.data.meshes.new(name + "_Mesh")
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=size, verts=bm.verts)
    bmesh.ops.translate(bm, vec=center, verts=bm.verts)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    if chamfer > 0.0004:
        bev = obj.modifiers.new("Bevel", 'BEVEL')
        bev.width = chamfer
        bev.segments = 2
        bev.limit_method = 'ANGLE'
        bev.angle_limit = math.radians(35)
    return obj

def make_cylinder(name, center, radius, depth, rot_euler=(0, 0, 0), vertices=32, col=shotgun_col):
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

def make_cone(name, center, r1, r2, depth, rot_euler=(0, 0, 0), vertices=24, col=shotgun_col):
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
# 1. TACTICAL MODULAR BUTTSTOCK (SKELETONIZED WITH RECOIL PAD)
# -------------------------------------------------------------
# Cylindrical Buffer Tube (machined silver steel)
buffer_tube = make_cylinder("Stock_BufferTube", (0, -0.160, 0.088), radius=0.015, depth=0.14, rot_euler=(math.radians(90), 0, 0))
apply_mat(buffer_tube, mat_chrome)

# Buffer Tube Castle Nut / Collar
collar = make_cylinder("Stock_CollarNut", (0, -0.095, 0.088), radius=0.019, depth=0.012, rot_euler=(math.radians(90), 0, 0), vertices=24)
apply_mat(collar, mat_gunmetal)

# Stock Main Housing (Upper slider over buffer tube)
stock_body = make_box("Stock_MainBody", (0, -0.200, 0.088), (0.042, 0.160, 0.034), chamfer=0.003)
apply_mat(stock_body, mat_indigo)

# Rubber Cheek Rest / Comb on top of stock
cheek_rest = make_box("Stock_CheekRest", (0, -0.210, 0.112), (0.038, 0.120, 0.018), chamfer=0.002)
apply_mat(cheek_rest, mat_carbon)

# Lower Skeleton Horizontal Strut
strut_bot = make_box("Stock_LowerStrut", (0, -0.235, 0.012), (0.036, 0.100, 0.020), chamfer=0.002)
apply_mat(strut_bot, mat_indigo)

# Vertical Skeleton Connector (leaves hollow window in stock)
strut_vert = make_box("Stock_VertStrut", (0, -0.170, 0.048), (0.036, 0.024, 0.054), chamfer=0.002)
apply_mat(strut_vert, mat_indigo)

# Ergonomic Rubber Buttpad with Recoil Grooves
buttpad = make_box("Stock_Buttpad", (0, -0.295, 0.065), (0.044, 0.022, 0.135), chamfer=0.003)
apply_mat(buttpad, mat_carbon)

# QD Sling Swivel Port on stock flank
qd_stock = make_cylinder("Stock_QDPort", (0.022, -0.235, 0.075), radius=0.006, depth=0.004, rot_euler=(0, math.radians(90), 0))
apply_mat(qd_stock, mat_chrome)

# -------------------------------------------------------------
# 2. MAIN RECEIVER, CONTROLS & ERGONOMIC PISTOL GRIP
# -------------------------------------------------------------
# Rear Upper Receiver Housing (Indigo Titanium)
rec_rear = make_box("Receiver_Rear", (0, -0.040, 0.088), (0.052, 0.110, 0.065), chamfer=0.003)
apply_mat(rec_rear, mat_indigo)

# Beveled Side Armor Plates
for s_x in [-0.027, 0.027]:
    plate = make_box(f"Receiver_SidePlate_{s_x}", (s_x, -0.040, 0.088), (0.003, 0.095, 0.048), chamfer=0.0015)
    apply_mat(plate, mat_gunmetal)

# Manufacturer Badge Plate on right flank
mfg_badge = make_box("Receiver_Badge", (0.029, -0.015, 0.072), (0.002, 0.024, 0.024), chamfer=0.0008)
apply_mat(mfg_badge, mat_chrome)

# Top Picatinny Rail across Receiver
top_rail = make_box("Receiver_TopRail", (0, 0.010, 0.125), (0.034, 0.220, 0.012), chamfer=0.0012)
apply_mat(top_rail, mat_gunmetal)

# Combat Ghost-Ring Rear Sight on top rail
sight_base = make_box("Receiver_RearSight", (0, -0.045, 0.136), (0.022, 0.022, 0.014), chamfer=0.001)
apply_mat(sight_base, mat_gunmetal)
sight_ring = make_cylinder("Receiver_SightRing", (0, -0.045, 0.144), radius=0.006, depth=0.004, rot_euler=(math.radians(90), 0, 0))
apply_mat(sight_ring, mat_gunmetal)
for s_x in [-0.007, 0.007]:
    dot = make_box(f"SightDot_{s_x}", (s_x, -0.052, 0.144), (0.002, 0.002, 0.002), chamfer=0.0003)
    apply_mat(dot, mat_glow)

# Lower Receiver (Trigger Housing)
rec_lower = make_box("Receiver_Lower", (0, -0.030, 0.040), (0.046, 0.095, 0.035), chamfer=0.0025)
apply_mat(rec_lower, mat_indigo)

# Ergonomic Pistol Grip (Angled 18 deg backward, textured carbon finger inlays)
bm_grip = bmesh.new()
bmesh.ops.create_cube(bm_grip, size=1.0)
bmesh.ops.scale(bm_grip, vec=(0.032, 0.044, 0.105), verts=bm_grip.verts)
for v in bm_grip.verts:
    if v.co.z < 0:
        v.co.y += (v.co.z * -0.24)
        v.co.x *= 0.94
mesh_grip = bpy.data.meshes.new("ShotgunGrip_Mesh")
bm_grip.to_mesh(mesh_grip)
bm_grip.free()
obj_grip = bpy.data.objects.new("ShotgunGrip", mesh_grip)
obj_grip.location = (0, -0.035, -0.035)
obj_grip.rotation_euler = (math.radians(18), 0, 0)
shotgun_col.objects.link(obj_grip)
bev_grip = obj_grip.modifiers.new("Bevel", 'BEVEL')
bev_grip.width = 0.003
apply_mat(obj_grip, mat_indigo)

# Carbon Grip Panel Inserts (Both Flanks)
for s_x in [-0.017, 0.017]:
    g_panel = make_box(f"Grip_Panel_{s_x}", (s_x, -0.035, -0.035), (0.0025, 0.032, 0.070), chamfer=0.001)
    g_panel.rotation_euler = (math.radians(18), 0, 0)
    apply_mat(g_panel, mat_carbon)

# Trigger & Tactical Trigger Guard
t_guard = make_box("TriggerGuard", (0, 0.002, 0.008), (0.024, 0.048, 0.026), chamfer=0.0015)
apply_mat(t_guard, mat_gunmetal)
trigger = make_box("Shotgun_Trigger", (0, 0.002, 0.012), (0.007, 0.014, 0.024), chamfer=0.001)
trigger.rotation_euler = (math.radians(-16), 0, 0)
apply_mat(trigger, mat_gunmetal)

# Fire Selector Lever
selector = make_cylinder("Shotgun_Selector", (0.027, -0.042, 0.065), radius=0.008, depth=0.005, rot_euler=(0, math.radians(90), 0))
apply_mat(selector, mat_gunmetal)

# -------------------------------------------------------------
# 3. EXPOSED PLASMA REACTOR CHAMBER (RECESSED OCTAGONAL WINDOW)
# -------------------------------------------------------------
# Window Frame Borders (Leaving cavity 100% open to interior ampoule!)
win_top = make_box("Reactor_WinTop", (0, 0.090, 0.110), (0.050, 0.095, 0.014), chamfer=0.0015)
apply_mat(win_top, mat_gunmetal)
win_bot = make_box("Reactor_WinBot", (0, 0.090, 0.062), (0.050, 0.095, 0.014), chamfer=0.0015)
apply_mat(win_bot, mat_gunmetal)
win_rear = make_box("Reactor_WinRear", (0, 0.040, 0.086), (0.050, 0.018, 0.042), chamfer=0.0015)
apply_mat(win_rear, mat_gunmetal)
win_front = make_box("Reactor_WinFront", (0, 0.140, 0.086), (0.050, 0.018, 0.042), chamfer=0.0015)
apply_mat(win_front, mat_gunmetal)

# Horizontal Quartz Ampoule Inside Window
reactor_glass = make_cylinder("Reactor_GlassAmpoule", (0, 0.090, 0.086), radius=0.017, depth=0.080, rot_euler=(math.radians(90), 0, 0), vertices=32)
apply_mat(reactor_glass, mat_glass)

# Internal Intense Swirling Plasma Helix Filament
reactor_plasma = make_cylinder("Reactor_PlasmaCore", (0, 0.090, 0.086), radius=0.0075, depth=0.070, rot_euler=(math.radians(90), 0, 0), vertices=16)
apply_mat(reactor_plasma, mat_plasma)

# Magnetic Confinement Cap Ends (Chrome Cones)
cap_rear = make_cone("Reactor_Cap_R", (0, 0.048, 0.086), r1=0.019, r2=0.013, depth=0.014, rot_euler=(math.radians(-90), 0, 0))
apply_mat(cap_rear, mat_chrome)
cap_front = make_cone("Reactor_Cap_F", (0, 0.132, 0.086), r1=0.013, r2=0.019, depth=0.014, rot_euler=(math.radians(-90), 0, 0))
apply_mat(cap_front, mat_chrome)

# Inner Chrome Confinement Rings around Ampoule
for r_y in [0.072, 0.090, 0.108]:
    c_ring = make_cylinder(f"Reactor_AmpRing_{r_y}", (0, r_y, 0.086), radius=0.0182, depth=0.003, rot_euler=(math.radians(90), 0, 0))
    apply_mat(c_ring, mat_chrome)

# Local Point Light (genuine purple glow on gun frame and workbench)
light_reactor = bpy.data.lights.new("Light_ReactorShotgun", 'POINT')
light_reactor.energy = 4.0
light_reactor.color = (0.72, 0.12, 1.0)
obj_lr = bpy.data.objects.new("Light_ReactorShotgun", light_reactor)
obj_lr.location = (0, 0.090, 0.086)
shotgun_col.objects.link(obj_lr)

# LUZ DISCRETA 1: Barra LED horizontal superior sobre el reactor (fiel a la foto)
led_top_reactor = make_box("LED_TopReactor", (0.026, 0.090, 0.118), (0.002, 0.055, 0.0035), chamfer=0.0004)
apply_mat(led_top_reactor, mat_glow)

# LUZ DISCRETA 2: Barra LED horizontal inferior bajo el reactor
led_bot_reactor = make_box("LED_BotReactor", (0.026, 0.085, 0.046), (0.002, 0.042, 0.0035), chamfer=0.0004)
apply_mat(led_bot_reactor, mat_glow)

# -------------------------------------------------------------
# 4. CENTRAL OPEN CRADLE (PERFORATED TOP SHROUD & FOCUS COILS)
# -------------------------------------------------------------
# Upper Ventilated Shroud (Indigo Titanium with rectangular cooling cutouts!)
bm_us = bmesh.new()
bmesh.ops.create_cube(bm_us, size=1.0)
bmesh.ops.scale(bm_us, vec=(0.048, 0.220, 0.024), verts=bm_us.verts)
bmesh.ops.translate(bm_us, vec=(0, 0.260, 0.116), verts=bm_us.verts)
mesh_us = bpy.data.meshes.new("Shotgun_UpperShroud_Mesh")
bm_us.to_mesh(mesh_us)
bm_us.free()
obj_us = bpy.data.objects.new("Shotgun_UpperShroud", mesh_us)
shotgun_col.objects.link(obj_us)
bev_us = obj_us.modifiers.new("Bevel", 'BEVEL')
bev_us.width = 0.002
apply_mat(obj_us, mat_indigo)

# 5 Rectangular Cooling Ventilation Slots along top shroud
for i_slot, s_y in enumerate([0.180, 0.215, 0.250, 0.285, 0.320]):
    slot_l = make_box(f"VentSlot_L_{i_slot}", (-0.025, s_y, 0.116), (0.002, 0.020, 0.008), chamfer=0.0005)
    apply_mat(slot_l, mat_gunmetal)
    slot_r = make_box(f"VentSlot_R_{i_slot}", (0.025, s_y, 0.116), (0.002, 0.020, 0.008), chamfer=0.0005)
    apply_mat(slot_r, mat_gunmetal)

# Lower Chassis Beam under Cradle
beam_lower = make_box("Shotgun_LowerBeam", (0, 0.230, 0.042), (0.044, 0.180, 0.016), chamfer=0.0015)
apply_mat(beam_lower, mat_gunmetal)

# LUZ DISCRETA 3: Tira LED horizontal morada a lo largo del riel inferior
led_cradle_lower = make_box("Shotgun_CradleLED_Lower", (0.023, 0.230, 0.042), (0.002, 0.160, 0.0035), chamfer=0.0004)
apply_mat(led_cradle_lower, mat_glow)

# Central Quartz Beam Vacuum Tube
central_tube = make_cylinder("Shotgun_CentralBeamTube", (0, 0.260, 0.080), radius=0.013, depth=0.22, rot_euler=(math.radians(90), 0, 0), vertices=32)
apply_mat(central_tube, mat_glass)

# Internal concentrated pulse core
pulse_core = make_cylinder("Shotgun_PulseCore", (0, 0.260, 0.080), radius=0.004, depth=0.23, rot_euler=(math.radians(90), 0, 0), vertices=16)
apply_mat(pulse_core, mat_plasma)

# 2 Hourglass Collimator Rings mounted on brackets along the tube
collimator_y = [0.220, 0.280]
for idx, cy in enumerate(collimator_y):
    cr = make_cone(f"Shotgun_CollCone_R_{idx}", (0, cy - 0.006, 0.080), r1=0.018, r2=0.013, depth=0.012, rot_euler=(math.radians(90), 0, 0))
    apply_mat(cr, mat_gunmetal)
    cf = make_cone(f"Shotgun_CollCone_F_{idx}", (0, cy + 0.006, 0.080), r1=0.013, r2=0.018, depth=0.012, rot_euler=(math.radians(90), 0, 0))
    apply_mat(cf, mat_gunmetal)
    c_ring = make_cylinder(f"Shotgun_CollRing_{idx}", (0, cy, 0.080), radius=0.0195, depth=0.004, rot_euler=(math.radians(90), 0, 0))
    apply_mat(c_ring, mat_chrome)
    # LUZ DISCRETA 4: Anillo interno iluminado en cada colimador
    g_ring = make_cylinder(f"Shotgun_CollGlow_{idx}", (0, cy, 0.080), radius=0.0142, depth=0.002, rot_euler=(math.radians(90), 0, 0))
    apply_mat(g_ring, mat_glow)
    bracket = make_box(f"Shotgun_CollBracket_{idx}", (0, cy, 0.056), (0.020, 0.008, 0.022), chamfer=0.001)
    apply_mat(bracket, mat_gunmetal)

# -------------------------------------------------------------
# 5. FOREGRIP / PUMP ACTION HANDLE & GILLS
# -------------------------------------------------------------
# Chunky Ergonomic Pump Handle (Carbon Fiber with front & rear flared handstops)
bm_pump = bmesh.new()
bmesh.ops.create_cube(bm_pump, size=1.0)
bmesh.ops.scale(bm_pump, vec=(0.048, 0.160, 0.040), verts=bm_pump.verts)
bmesh.ops.translate(bm_pump, vec=(0, 0.320, 0.012), verts=bm_pump.verts)
# Flare handstops at front and rear
for v in bm_pump.verts:
    if v.co.y > 0.380:
        v.co.z -= (v.co.y - 0.380) * 0.45
    elif v.co.y < 0.260:
        v.co.z -= (0.260 - v.co.y) * 0.45
mesh_pump = bpy.data.meshes.new("Shotgun_PumpHandle_Mesh")
bm_pump.to_mesh(mesh_pump)
bm_pump.free()
obj_pump = bpy.data.objects.new("Shotgun_PumpHandle", mesh_pump)
shotgun_col.objects.link(obj_pump)
bev_pump = obj_pump.modifiers.new("Bevel", 'BEVEL')
bev_pump.width = 0.003
apply_mat(obj_pump, mat_carbon)

# Pump Shroud Flanks with 3 Slanted Cooling Gills (Carbon composite)
for s_x in [-0.026, 0.026]:
    shroud_flank = make_box(f"Pump_Flank_{s_x}", (s_x, 0.395, 0.075), (0.003, 0.090, 0.055), chamfer=0.002)
    apply_mat(shroud_flank, mat_carbon)
    # 3 Slanted Gills
    for i_gill, gy in enumerate([0.375, 0.395, 0.415]):
        gill = make_box(f"Gill_{s_x}_{i_gill}", (s_x * 1.02, gy, 0.075), (0.002, 0.006, 0.028), chamfer=0.0005)
        gill.rotation_euler = (0, math.radians(24 if s_x > 0 else -24), 0)
        apply_mat(gill, mat_gunmetal)

# -------------------------------------------------------------
# 6. ICONIC QUAD-BARREL MUZZLE CLUSTER (2x2 MATRIX)
# -------------------------------------------------------------
# 4 Heavy Steel Barrels arranged in 2x2 Square:
# Top pair: Z = 0.095, Bottom pair: Z = 0.065
# Left pair: X = -0.015, Right pair: X = +0.015
barrel_coords = [
    ("TL", -0.015, 0.095),
    ("TR",  0.015, 0.095),
    ("BL", -0.015, 0.065),
    ("BR",  0.015, 0.065)
]

for b_id, bx, bz in barrel_coords:
    # Outer heavy barrel tube (Fluted gunmetal steel)
    b_obj = make_cylinder(f"Shotgun_Barrel_{b_id}", (bx, 0.505, bz), radius=0.0125, depth=0.23, rot_euler=(math.radians(90), 0, 0), vertices=32)
    apply_mat(b_obj, mat_gunmetal)
    # Inner dark bore hole at muzzle tip
    bore = make_cylinder(f"Shotgun_Bore_{b_id}", (bx, 0.620, bz), radius=0.0075, depth=0.006, rot_euler=(math.radians(90), 0, 0), vertices=24)
    apply_mat(bore, mat_carbon)

# Quad-Barrel Rear Receiver Coupling Sleeve
coupling = make_box("Shotgun_BarrelCoupling", (0, 0.410, 0.080), (0.054, 0.050, 0.062), chamfer=0.002)
apply_mat(coupling, mat_indigo)

# Front Barrel Clamp Block (locks all 4 barrels at muzzle)
clamp_block = make_box("Shotgun_BarrelClamp", (0, 0.570, 0.080), (0.054, 0.024, 0.062), chamfer=0.002)
apply_mat(clamp_block, mat_gunmetal)

# Front High-Profile Iron Sight Post
front_sight = make_box("Shotgun_FrontSight", (0, 0.575, 0.124), (0.012, 0.016, 0.022), chamfer=0.001)
apply_mat(front_sight, mat_gunmetal)
front_dot = make_box("Shotgun_FrontDot", (0, 0.582, 0.131), (0.002, 0.003, 0.002), chamfer=0.0003)
apply_mat(front_dot, mat_glow)

# Lower Accessory Rail under the 4 Barrels
lower_rail = make_box("Shotgun_UnderRail", (0, 0.490, 0.038), (0.034, 0.160, 0.014), chamfer=0.0015)
apply_mat(lower_rail, mat_gunmetal)

# LUZ DISCRETA 5: Tiras LED moradas dobles en los laterales bajo los cañones (exactas a la imagen)
for s_x in [-0.024, 0.024]:
    b_led_strip = make_box(f"Shotgun_BarrelLED_{s_x}", (s_x, 0.490, 0.038), (0.002, 0.140, 0.0035), chamfer=0.0004)
    apply_mat(b_led_strip, mat_glow)

# -------------------------------------------------------------
# 7. HIGH-CONTRAST SCI-FI STUDIO RENDER (EEVEE)
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
bmesh.ops.create_grid(bm_t, size=15)
bm_t.to_mesh(mesh_tab)
bm_t.free()
tab = bpy.data.objects.new("StudioTable", mesh_tab)
tab.location = (0, 0.15, -0.15)
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
lk.energy = 60.0
lk.size = 1.6
lk.color = (0.92, 0.95, 1.0)
olk = bpy.data.objects.new("KeyLight", lk)
olk.location = (1.6, 0.18, 1.1)
olk.rotation_euler = (0.7, 0.2, 1.1)
studio_col.objects.link(olk)

lr = bpy.data.lights.new("RimLight", 'AREA')
lr.energy = 85.0
lr.size = 2.4
lr.color = (0.68, 0.15, 1.0)
olr = bpy.data.objects.new("RimLight", lr)
olr.location = (-1.6, 0.28, 0.9)
olr.rotation_euler = (-0.7, -0.3, -1.8)
studio_col.objects.link(olr)

lf = bpy.data.lights.new("FillLight", 'AREA')
lf.energy = 16.0
lf.size = 1.8
lf.color = (0.6, 0.8, 1.0)
olf = bpy.data.objects.new("FillLight", lf)
olf.location = (0.2, -1.3, 0.6)
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

# Shotgun span: Y from -0.30 to +0.62, center at Y=0.16, Z=0.065
views = [
    # 1. Hero Side Profile (Full length matching reference photo angle!)
    ("shotgun_quad1_hero_side.png", (1.60, 0.16, 0.12), Vector((0, 0.16, 0.065)), 50),
    # 2. Front 3/4 Perspective (Showing the imposing 2x2 quad-barrel muzzle, pump, and cradle)
    ("shotgun_quad2_iso_front.png", (1.05, 0.70, 0.22), Vector((0, 0.28, 0.065)), 46),
    # 3. FPS / ADS View (Shooter's eye aiming through the ghost-ring sight onto front bead)
    ("shotgun_quad3_fps_view.png", (0.0, -0.16, 0.158), Vector((0.0, 0.58, 0.131)), 48),
    # 4. Rear 3/4 Detail (Modular skeleton stock, pistol grip, trigger and reactor window)
    ("shotgun_quad4_rear_detail.png", (0.95, -0.16, 0.14), Vector((0, -0.02, 0.045)), 48)
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

master_save = r"E:\Darx_Proyect\Art\Blender\SM_Wep_PhaseShotgun_Workspace.blend"
bpy.ops.wm.save_as_mainfile(filepath=master_save)
print('Workspace saved to:', master_save)
print('=== SHOTGUN RENDER COMPLETE ===')

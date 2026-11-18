import bpy
import bmesh
import math
import os
import shutil
from mathutils import Vector, Euler, Matrix

# Reset scene
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

smg_col = bpy.data.collections.new("Wep_PhaseSMG")
scene.collection.children.link(smg_col)

# -------------------------------------------------------------
# SHADERS (PRISTINE WHITE CERAMIC + GUNMETAL + VIOLET GLOW)
# -------------------------------------------------------------
# 1. Pristine Matte White Ceramic Chassis (Fiel a la foto de referencia)
mat_ceramic = bpy.data.materials.new(name="M_PhaseSMG_Ceramic")
mat_ceramic.use_nodes = True
bsdf = mat_ceramic.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.87, 0.88, 0.91, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.26
    bsdf.inputs['Metallic'].default_value = 0.02

# 2. Gunmetal / Weathered Steel for Mechanics, Barrels & Muzzle
mat_gunmetal = bpy.data.materials.new(name="M_PhaseSMG_Gunmetal")
mat_gunmetal.use_nodes = True
bsdf = mat_gunmetal.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.042, 0.045, 0.052, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.20
    bsdf.inputs['Metallic'].default_value = 0.94

# 3. Tactical Rubber (Buttpad & Grip Inlays)
mat_rubber = bpy.data.materials.new(name="M_PhaseSMG_Rubber")
mat_rubber.use_nodes = True
bsdf = mat_rubber.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.012, 0.012, 0.015, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.75
    bsdf.inputs['Metallic'].default_value = 0.0

# 4. Machined Silver Chrome (Caps & Winding Key)
mat_chrome = bpy.data.materials.new(name="M_PhaseSMG_Chrome")
mat_chrome.use_nodes = True
bsdf = mat_chrome.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.80, 0.82, 0.85, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.12
    bsdf.inputs['Metallic'].default_value = 0.98

# 5. Discreet Rich Violet LED Glow (Calibrated)
mat_glow = bpy.data.materials.new(name="M_PhaseSMG_VioletGlow")
mat_glow.use_nodes = True
bsdf = mat_glow.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.72, 0.10, 1.0, 1.0)
    bsdf.inputs['Emission Color'].default_value = (0.76, 0.12, 1.0, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 16.0

# 6. High-Energy Plasma Filament Core
mat_plasma = bpy.data.materials.new(name="M_PhaseSMG_PlasmaCore")
mat_plasma.use_nodes = True
bsdf = mat_plasma.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.88, 0.25, 1.0, 1.0)
    bsdf.inputs['Emission Color'].default_value = (0.92, 0.30, 1.0, 1.0)
    bsdf.inputs['Emission Strength'].default_value = 24.0

# 7. Quartz Vacuum Glass Tube (Crystal clear)
mat_glass = bpy.data.materials.new(name="M_PhaseSMG_QuartzGlass")
mat_glass.use_nodes = True
bsdf = mat_glass.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.95, 0.94, 1.0, 1.0)
    bsdf.inputs['Transmission Weight'].default_value = 0.96
    bsdf.inputs['Roughness'].default_value = 0.02
    bsdf.inputs['IOR'].default_value = 1.45
    bsdf.inputs['Alpha'].default_value = 0.22

def apply_mat(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)

def make_box(name, center, size, rot_euler=(0, 0, 0), chamfer=0.002, col=smg_col):
    mesh = bpy.data.meshes.new(name + "_Mesh")
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=size, verts=bm.verts)
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    obj.location = center
    obj.rotation_euler = rot_euler
    col.objects.link(obj)
    if chamfer > 0.0004:
        bev = obj.modifiers.new("Bevel", 'BEVEL')
        bev.width = chamfer
        bev.segments = 2
        bev.limit_method = 'ANGLE'
        bev.angle_limit = math.radians(35)
    return obj

def make_cylinder(name, center, radius, depth, rot_euler=(0, 0, 0), vertices=32, col=smg_col):
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

def make_cone(name, center, r1, r2, depth, rot_euler=(0, 0, 0), vertices=24, col=smg_col):
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

def make_arc_led_xz(name, center_xz, y_pos, r_mid, width, angle_start_deg, angle_end_deg, thickness=0.002, segments=16, col=smg_col):
    """Creates a curved ribbon LED strip flush in the X-Z plane (facing front/rear)."""
    mesh = bpy.data.meshes.new(name + "_Mesh")
    bm = bmesh.new()
    
    r_in = r_mid - width * 0.5
    r_out = r_mid + width * 0.5
    
    a_start = math.radians(angle_start_deg)
    a_end = math.radians(angle_end_deg)
    step = (a_end - a_start) / segments
    
    verts_inner = []
    verts_outer = []
    
    for i in range(segments + 1):
        ang = a_start + i * step
        x_in = center_xz[0] + math.sin(ang) * r_in
        z_in = center_xz[1] + math.cos(ang) * r_in
        x_out = center_xz[0] + math.sin(ang) * r_out
        z_out = center_xz[1] + math.cos(ang) * r_out
        
        v_in_f = bm.verts.new((x_in, y_pos + thickness * 0.5, z_in))
        v_in_b = bm.verts.new((x_in, y_pos - thickness * 0.5, z_in))
        v_out_f = bm.verts.new((x_out, y_pos + thickness * 0.5, z_out))
        v_out_b = bm.verts.new((x_out, y_pos - thickness * 0.5, z_out))
        
        verts_inner.append((v_in_f, v_in_b))
        verts_outer.append((v_out_f, v_out_b))
    
    bm.verts.ensure_lookup_table()
    
    for i in range(segments):
        bm.faces.new([verts_inner[i][0], verts_outer[i][0], verts_outer[i+1][0], verts_inner[i+1][0]])
        bm.faces.new([verts_inner[i][1], verts_inner[i+1][1], verts_outer[i+1][1], verts_outer[i][1]])
        bm.faces.new([verts_outer[i][0], verts_outer[i][1], verts_outer[i+1][1], verts_outer[i+1][0]])
        bm.faces.new([verts_inner[i][0], verts_inner[i+1][0], verts_inner[i+1][1], verts_inner[i][1]])
        
    bm.faces.new([verts_inner[0][0], verts_inner[0][1], verts_outer[0][1], verts_outer[0][0]])
    bm.faces.new([verts_inner[-1][0], verts_outer[-1][0], verts_outer[-1][1], verts_inner[-1][1]])
    
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    col.objects.link(obj)
    apply_mat(obj, mat_glow)
    return obj

# -------------------------------------------------------------
# 1. FIXED ERGONOMIC BUTTSTOCK (CLASSIC TOMMY-STYLE PROFILE)
# -------------------------------------------------------------
bm_stock = bmesh.new()
bmesh.ops.create_cube(bm_stock, size=1.0)
bmesh.ops.scale(bm_stock, vec=(0.044, 0.200, 0.110), verts=bm_stock.verts)
bmesh.ops.translate(bm_stock, vec=(0, -0.180, 0.065), verts=bm_stock.verts)
for v in bm_stock.verts:
    if v.co.y > -0.140:
        f = (v.co.y - (-0.140)) / 0.060
        v.co.x *= (1.0 - f * 0.15)
        if v.co.z < 0.065:
            v.co.z += f * 0.035
mesh_stock = bpy.data.meshes.new("Stock_Mesh")
bm_stock.to_mesh(mesh_stock)
bm_stock.free()
obj_stock = bpy.data.objects.new("SMG_Stock", mesh_stock)
smg_col.objects.link(obj_stock)
bev_stock = obj_stock.modifiers.new("Bevel", 'BEVEL')
bev_stock.width = 0.0035
apply_mat(obj_stock, mat_ceramic)

# Recessed Cheek Comb Inlay Panel
cheek_panel = make_box("Stock_CheekPanel", (0, -0.185, 0.095), (0.046, 0.110, 0.024), chamfer=0.0015)
apply_mat(cheek_panel, mat_ceramic)

# Rubber Buttpad with Recoil Grooves
buttpad = make_box("Stock_Buttpad", (0, -0.282, 0.065), (0.046, 0.020, 0.125), chamfer=0.003)
apply_mat(buttpad, mat_rubber)

# Hinge collar / Stock Connector Nut
collar = make_cylinder("Stock_Collar", (0, -0.076, 0.070), radius=0.018, depth=0.014, rot_euler=(math.radians(90), 0, 0), vertices=24)
apply_mat(collar, mat_gunmetal)

# Stock pivot bolt detail
pivot_bolt = make_cylinder("Stock_PivotBolt", (0.024, -0.076, 0.070), radius=0.006, depth=0.006, rot_euler=(0, math.radians(90), 0), vertices=16)
apply_mat(pivot_bolt, mat_gunmetal)

# LUZ DISCRETA 1: Anillo de luz morada vertical separando culata y cajón
stock_led_ring = make_cylinder("Stock_LEDRing", (0, -0.076, 0.070), radius=0.0205, depth=0.003, rot_euler=(math.radians(90), 0, 0), vertices=32)
apply_mat(stock_led_ring, mat_glow)

# -------------------------------------------------------------
# 2. MAIN RECEIVER, CONTROLS & ERGONOMIC REAR PISTOL GRIP
# -------------------------------------------------------------
rec_rear = make_box("Receiver_Rear", (0, -0.015, 0.095), (0.052, 0.110, 0.065), chamfer=0.003)
apply_mat(rec_rear, mat_ceramic)

rec_front = make_box("Receiver_Front", (0, 0.142, 0.095), (0.052, 0.016, 0.065), chamfer=0.002)
apply_mat(rec_front, mat_ceramic)

rec_top_bridge = make_box("Receiver_TopBridge", (0, 0.088, 0.122), (0.052, 0.096, 0.012), chamfer=0.0015)
apply_mat(rec_top_bridge, mat_ceramic)

rec_bot_bridge = make_box("Receiver_BotBridge", (0, 0.088, 0.068), (0.052, 0.096, 0.012), chamfer=0.0015)
apply_mat(rec_bot_bridge, mat_ceramic)

# Top Tactical Iron Sight (Rear notch sight)
sight_rear = make_box("Receiver_RearSight", (0, 0.005, 0.135), (0.022, 0.035, 0.016), chamfer=0.001)
apply_mat(sight_rear, mat_gunmetal)
sight_notch = make_box("Receiver_SightNotch", (0, 0.005, 0.141), (0.007, 0.038, 0.006))
apply_mat(sight_notch, mat_rubber)

rec_lower = make_box("Receiver_Lower", (0, -0.020, 0.040), (0.046, 0.110, 0.035), chamfer=0.0025)
apply_mat(rec_lower, mat_ceramic)

# Sculpted Ergonomic Rear Pistol Grip with Authentic Finger Swells
def make_rear_pistol_grip():
    mesh = bpy.data.meshes.new("SMG_RearGrip_Mesh")
    bm = bmesh.new()
    slices = [
        ( 0.035, -0.020, 0.036, 0.048),
        ( 0.015, -0.025, 0.034, 0.046),
        (-0.005, -0.032, 0.032, 0.042),
        (-0.020, -0.039, 0.033, 0.046),
        (-0.035, -0.047, 0.032, 0.042),
        (-0.050, -0.055, 0.033, 0.046),
        (-0.065, -0.063, 0.032, 0.043),
        (-0.080, -0.072, 0.035, 0.050)
    ]
    ring_verts = []
    for z, yc, wx, dy in slices:
        hx = wx * 0.5
        hy = dy * 0.5
        pts = [
            (-hx * 0.7, yc - hy, z),
            ( hx * 0.7, yc - hy, z),
            ( hx, yc - hy * 0.7, z),
            ( hx, yc + hy * 0.7, z),
            ( hx * 0.7, yc + hy, z),
            (-hx * 0.7, yc + hy, z),
            (-hx, yc + hy * 0.7, z),
            (-hx, yc - hy * 0.7, z)
        ]
        verts = [bm.verts.new(p) for p in pts]
        ring_verts.append(verts)
    
    for i in range(len(ring_verts) - 1):
        r1 = ring_verts[i]
        r2 = ring_verts[i+1]
        for j in range(8):
            j_next = (j + 1) % 8
            bm.faces.new([r1[j], r1[j_next], r2[j_next], r2[j]])
    
    bm.faces.new(ring_verts[-1])
    bm.faces.new(list(reversed(ring_verts[0])))
    
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("SMG_RearGrip", mesh)
    smg_col.objects.link(obj)
    bev = obj.modifiers.new("Bevel", 'BEVEL')
    bev.width = 0.002
    bev.segments = 2
    apply_mat(obj, mat_ceramic)
    return obj

make_rear_pistol_grip()

# Trigger & Trigger Guard
t_guard = make_box("TriggerGuard", (0, 0.008, 0.010), (0.022, 0.044, 0.024), chamfer=0.0015)
apply_mat(t_guard, mat_gunmetal)
trigger = make_box("Trigger", (0, 0.008, 0.012), (0.006, 0.012, 0.022), rot_euler=(math.radians(-15), 0, 0), chamfer=0.001)
apply_mat(trigger, mat_gunmetal)

# Fire selector switch
selector = make_cylinder("FireSelector", (0.027, -0.035, 0.065), radius=0.007, depth=0.004, rot_euler=(0, math.radians(90), 0))
apply_mat(selector, mat_gunmetal)

# Oval Cocking / Charging Handle on Upper Right Flank
ch_handle = make_box("ChargingHandle", (0.028, 0.010, 0.115), (0.005, 0.038, 0.014), chamfer=0.002)
apply_mat(ch_handle, mat_gunmetal)

# LUZ DISCRETA 2: Tira LED horizontal morada a lo largo del lateral del cajón (Both flanks!)
for s_x in [-0.027, 0.027]:
    rec_led_strip = make_box(f"Receiver_SideLED_{s_x}", (s_x, 0.010, 0.092), (0.002, 0.130, 0.0035), chamfer=0.0004)
    apply_mat(rec_led_strip, mat_glow)

# LUZ DISCRETA 3: Micro-LED rojo de estado en la parte trasera del cajón
status_dot = make_box("StatusDot_Red", (0.027, -0.068, 0.100), (0.002, 0.003, 0.003), chamfer=0.0003)
mat_red = bpy.data.materials.new(name="M_DotRed")
mat_red.use_nodes = True
bsdf_r = mat_red.node_tree.nodes.get("Principled BSDF")
if bsdf_r:
    bsdf_r.inputs['Base Color'].default_value = (1.0, 0.08, 0.08, 1.0)
    bsdf_r.inputs['Emission Color'].default_value = (1.0, 0.08, 0.08, 1.0)
    bsdf_r.inputs['Emission Strength'].default_value = 8.0
apply_mat(status_dot, mat_red)

# -------------------------------------------------------------
# 3. EXPOSED PLASMA REACTOR CHAMBER (ABOVE DRUM MAG)
# -------------------------------------------------------------
# Dark Gunmetal Hexagonal Window Frame
win_frame_t = make_box("Reactor_FrameT", (0, 0.088, 0.116), (0.054, 0.088, 0.006), chamfer=0.001)
apply_mat(win_frame_t, mat_gunmetal)
win_frame_b = make_box("Reactor_FrameB", (0, 0.088, 0.074), (0.054, 0.088, 0.006), chamfer=0.001)
apply_mat(win_frame_b, mat_gunmetal)
win_frame_r = make_box("Reactor_FrameR", (0, 0.046, 0.095), (0.054, 0.008, 0.038), chamfer=0.001)
apply_mat(win_frame_r, mat_gunmetal)
win_frame_f = make_box("Reactor_FrameF", (0, 0.130, 0.095), (0.054, 0.008, 0.038), chamfer=0.001)
apply_mat(win_frame_f, mat_gunmetal)

# Magnetic Confinement Cap Funnels pointing inward
cap_rear = make_cone("Reactor_Cap_R", (0, 0.056, 0.095), r1=0.017, r2=0.010, depth=0.015, rot_euler=(math.radians(-90), 0, 0))
apply_mat(cap_rear, mat_gunmetal)
cap_rear_ring = make_cylinder("Reactor_CapRing_R", (0, 0.056, 0.095), radius=0.0185, depth=0.004, rot_euler=(math.radians(90), 0, 0))
apply_mat(cap_rear_ring, mat_chrome)

cap_front = make_cone("Reactor_Cap_F", (0, 0.120, 0.095), r1=0.010, r2=0.017, depth=0.015, rot_euler=(math.radians(-90), 0, 0))
apply_mat(cap_front, mat_gunmetal)
cap_front_ring = make_cylinder("Reactor_CapRing_F", (0, 0.120, 0.095), radius=0.0185, depth=0.004, rot_euler=(math.radians(90), 0, 0))
apply_mat(cap_front_ring, mat_chrome)

# Crystal-Clear Quartz Glass Ampoule Inside Window (visible_shadow=False for pure transparency)
reactor_glass = make_cylinder("Reactor_Glass", (0, 0.088, 0.095), radius=0.016, depth=0.068, rot_euler=(math.radians(90), 0, 0), vertices=32)
apply_mat(reactor_glass, mat_glass)
reactor_glass.visible_shadow = False

# Glowing Spherical Plasma Core
mesh_sphere = bpy.data.meshes.new("Reactor_CoreSphere_Mesh")
bm_sp = bmesh.new()
bmesh.ops.create_uvsphere(bm_sp, u_segments=24, v_segments=16, radius=0.012)
bm_sp.to_mesh(mesh_sphere)
bm_sp.free()
reactor_plasma = bpy.data.objects.new("Reactor_CoreSphere", mesh_sphere)
reactor_plasma.location = (0, 0.088, 0.095)
smg_col.objects.link(reactor_plasma)
apply_mat(reactor_plasma, mat_plasma)

# Magnetic containment ring around core sphere
core_ring = make_cylinder("Reactor_CoreRing", (0, 0.088, 0.095), radius=0.0145, depth=0.003, rot_euler=(math.radians(90), 0, 0), vertices=24)
apply_mat(core_ring, mat_chrome)

# Local violet point light inside reactor
light_reactor = bpy.data.lights.new("Light_ReactorSMG", 'POINT')
light_reactor.energy = 16.0
light_reactor.color = (0.78, 0.18, 1.0)
obj_lr = bpy.data.objects.new("Light_ReactorSMG", light_reactor)
obj_lr.location = (0, 0.088, 0.095)
smg_col.objects.link(obj_lr)

# Vertical Purple LED Band at front of receiver
rec_front_band = make_cylinder("Rec_FrontBand", (0, 0.149, 0.095), radius=0.0262, depth=0.003, rot_euler=(math.radians(90), 0, 0), vertices=32)
apply_mat(rec_front_band, mat_glow)

# -------------------------------------------------------------
# 4. HIGH-CAPACITY CIRCULAR DRUM MAGAZINE (UNIDO AL ARMA Y ROTADO 90° FRONTAL)
# -------------------------------------------------------------
# Sits right in front of trigger guard at Y=0.068, Z=-0.026.
# Oriented with axis along Y: Flat circular faces face FRONT and REAR!
drum_center = (0, 0.068, -0.026)
drum_rad = 0.080
drum_thick = 0.048

# Magwell Feed Tower / Attachment Collar: UNIDO FIRMEMENTE AL ARMA SIN HUECOS!
drum_tower = make_box("Drum_FeedTower", (0, 0.068, 0.044), (0.044, 0.052, 0.026), chamfer=0.0015)
apply_mat(drum_tower, mat_ceramic)

drum_tower_rail = make_box("Drum_TowerRail", (0, 0.068, 0.046), (0.048, 0.038, 0.014), chamfer=0.001)
apply_mat(drum_tower_rail, mat_gunmetal)

drum_latch_pin = make_cylinder("Drum_LatchPin", (0.025, 0.068, 0.044), radius=0.005, depth=0.006, rot_euler=(0, math.radians(90), 0), vertices=16)
apply_mat(drum_latch_pin, mat_gunmetal)

# Main Drum Body (White Ceramic cylinder facing front/back)
drum_body = make_cylinder("Drum_MainBody", drum_center, radius=drum_rad, depth=drum_thick, rot_euler=(math.radians(90), 0, 0), vertices=48)
apply_mat(drum_body, mat_ceramic)

# Drum Outer Rim Flange (Gunmetal tactical grip rim)
drum_rim = make_cylinder("Drum_RimFlange", drum_center, radius=drum_rad + 0.002, depth=drum_thick - 0.008, rot_euler=(math.radians(90), 0, 0), vertices=48)
apply_mat(drum_rim, mat_gunmetal)

# FRONT FACE DETAILS (Y = 0.068 + 0.024 = 0.092)
y_front = drum_center[1] + drum_thick * 0.5

# Raised Ceramic Concentric Ring on Front Face
drum_face_ring_f = make_cylinder("Drum_FaceRing_F", (0, y_front + 0.0015, drum_center[2]), radius=0.060, depth=0.003, rot_euler=(math.radians(90), 0, 0), vertices=40)
apply_mat(drum_face_ring_f, mat_ceramic)

# Central Drum Hub & Winding Latch Key (Chrome)
drum_key_center_f = make_cylinder("Drum_KeyCenter_F", (0, y_front + 0.0035, drum_center[2]), radius=0.019, depth=0.005, rot_euler=(math.radians(90), 0, 0), vertices=32)
apply_mat(drum_key_center_f, mat_chrome)

drum_key_bar_f = make_box("Drum_KeyBar_F", (0, y_front + 0.006, drum_center[2]), (0.056, 0.005, 0.013), chamfer=0.001)
apply_mat(drum_key_bar_f, mat_chrome)

# Curved neon LED arcs on the FRONT face (X-Z plane!)
make_arc_led_xz("Drum_LED_Inner_R1", (0, drum_center[2]), y_front + 0.002, r_mid=0.046, width=0.0038, angle_start_deg=35, angle_end_deg=80)
make_arc_led_xz("Drum_LED_Inner_R2", (0, drum_center[2]), y_front + 0.002, r_mid=0.046, width=0.0038, angle_start_deg=100, angle_end_deg=145)
make_arc_led_xz("Drum_LED_Outer_R1", (0, drum_center[2]), y_front + 0.002, r_mid=0.068, width=0.0042, angle_start_deg=35, angle_end_deg=80)
make_arc_led_xz("Drum_LED_Outer_R2", (0, drum_center[2]), y_front + 0.002, r_mid=0.068, width=0.0042, angle_start_deg=100, angle_end_deg=145)

make_arc_led_xz("Drum_LED_Outer_L1", (0, drum_center[2]), y_front + 0.002, r_mid=0.068, width=0.0042, angle_start_deg=-35, angle_end_deg=-80)
make_arc_led_xz("Drum_LED_Outer_L2", (0, drum_center[2]), y_front + 0.002, r_mid=0.068, width=0.0042, angle_start_deg=-100, angle_end_deg=-145)

# Digital Ammo Counter Display Badge on lower front face
ammo_screen = make_box("Drum_AmmoScreen", (0, y_front + 0.002, drum_center[2] - 0.055), (0.026, 0.003, 0.018), chamfer=0.0005)
mat_screen = bpy.data.materials.new(name="M_AmmoScreen")
mat_screen.use_nodes = True
bsdf_s = mat_screen.node_tree.nodes.get("Principled BSDF")
if bsdf_s:
    bsdf_s.inputs['Base Color'].default_value = (0.05, 0.20, 0.45, 1.0)
    bsdf_s.inputs['Emission Color'].default_value = (0.12, 0.55, 1.0, 1.0)
    bsdf_s.inputs['Emission Strength'].default_value = 8.0
apply_mat(ammo_screen, mat_screen)

# REAR FACE DETAILS (Y = 0.068 - 0.024 = 0.044)
y_rear = drum_center[1] - drum_thick * 0.5
drum_face_ring_b = make_cylinder("Drum_FaceRing_B", (0, y_rear - 0.0015, drum_center[2]), radius=0.060, depth=0.003, rot_euler=(math.radians(90), 0, 0), vertices=40)
apply_mat(drum_face_ring_b, mat_ceramic)
drum_key_center_b = make_cylinder("Drum_KeyCenter_B", (0, y_rear - 0.003, drum_center[2]), radius=0.019, depth=0.004, rot_euler=(math.radians(90), 0, 0), vertices=32)
apply_mat(drum_key_center_b, mat_chrome)

# -------------------------------------------------------------
# 5. OPEN CRADLE, COLLIMATORS & SCULPTED TOMMY VERTICAL FOREGRIP
# -------------------------------------------------------------
spine_top = make_cylinder("Cradle_SpineTop", (0, 0.240, 0.122), radius=0.007, depth=0.18, rot_euler=(math.radians(90), 0, 0))
apply_mat(spine_top, mat_gunmetal)

cradle_tube = make_cylinder("Cradle_Tube", (0, 0.240, 0.085), radius=0.013, depth=0.18, rot_euler=(math.radians(90), 0, 0), vertices=32)
apply_mat(cradle_tube, mat_glass)
cradle_tube.visible_shadow = False

cradle_core = make_cylinder("Cradle_Core", (0, 0.240, 0.085), radius=0.0035, depth=0.19, rot_euler=(math.radians(90), 0, 0), vertices=16)
apply_mat(cradle_core, mat_plasma)

collimator_y = [0.195, 0.235, 0.275]
for idx, cy in enumerate(collimator_y):
    cr = make_cone(f"SMG_CollCone_R_{idx}", (0, cy - 0.004, 0.085), r1=0.016, r2=0.013, depth=0.008, rot_euler=(math.radians(90), 0, 0))
    apply_mat(cr, mat_gunmetal)
    cf = make_cone(f"SMG_CollCone_F_{idx}", (0, cy + 0.004, 0.085), r1=0.013, r2=0.016, depth=0.008, rot_euler=(math.radians(90), 0, 0))
    apply_mat(cf, mat_gunmetal)
    c_ring = make_cylinder(f"SMG_CollRing_{idx}", (0, cy, 0.085), radius=0.0175, depth=0.0035, rot_euler=(math.radians(90), 0, 0))
    apply_mat(c_ring, mat_chrome)
    g_ring = make_cylinder(f"SMG_CollGlow_{idx}", (0, cy, 0.085), radius=0.0132, depth=0.002, rot_euler=(math.radians(90), 0, 0))
    apply_mat(g_ring, mat_glow)
    bracket = make_box(f"SMG_CollBracket_{idx}", (0, cy, 0.060), (0.016, 0.006, 0.024), chamfer=0.001)
    apply_mat(bracket, mat_gunmetal)

cradle_base = make_box("Cradle_Base", (0, 0.240, 0.046), (0.044, 0.180, 0.016), chamfer=0.0015)
apply_mat(cradle_base, mat_ceramic)

# Sculpted Authentic Tommy Gun Vertical Foregrip
def make_tommy_foregrip():
    mesh = bpy.data.meshes.new("SMG_VerticalForegrip_Mesh")
    bm = bmesh.new()
    slices = [
        ( 0.038, 0.215, 0.036, 0.065),
        ( 0.022, 0.218, 0.034, 0.054),
        ( 0.006, 0.222, 0.032, 0.047),
        (-0.010, 0.226, 0.030, 0.042),
        (-0.022, 0.231, 0.031, 0.046),
        (-0.035, 0.235, 0.030, 0.042),
        (-0.048, 0.239, 0.031, 0.046),
        (-0.060, 0.243, 0.030, 0.042),
        (-0.072, 0.248, 0.033, 0.048),
        (-0.082, 0.254, 0.035, 0.054)
    ]
    ring_verts = []
    for z, yc, wx, dy in slices:
        hx = wx * 0.5
        hy = dy * 0.5
        pts = [
            (-hx * 0.7, yc - hy, z),
            ( hx * 0.7, yc - hy, z),
            ( hx, yc - hy * 0.7, z),
            ( hx, yc + hy * 0.7, z),
            ( hx * 0.7, yc + hy, z),
            (-hx * 0.7, yc + hy, z),
            (-hx, yc + hy * 0.7, z),
            (-hx, yc - hy * 0.7, z)
        ]
        verts = [bm.verts.new(p) for p in pts]
        ring_verts.append(verts)
    
    for i in range(len(ring_verts) - 1):
        r1 = ring_verts[i]
        r2 = ring_verts[i+1]
        for j in range(8):
            j_next = (j + 1) % 8
            bm.faces.new([r1[j], r1[j_next], r2[j_next], r2[j]])
    
    bm.faces.new(ring_verts[-1])
    bm.faces.new(list(reversed(ring_verts[0])))
    
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new("SMG_VerticalForegrip", mesh)
    smg_col.objects.link(obj)
    bev = obj.modifiers.new("Bevel", 'BEVEL')
    bev.width = 0.002
    bev.segments = 2
    apply_mat(obj, mat_ceramic)
    return obj

make_tommy_foregrip()

# -------------------------------------------------------------
# 6. FRONT BARREL SHROUD & SECONDARY PLASMA ACCELERATOR
# -------------------------------------------------------------
bm_fs = bmesh.new()
bmesh.ops.create_cone(bm_fs, cap_ends=True, segments=8, radius1=0.034, radius2=0.034, depth=0.23)
for v in bm_fs.verts:
    old_y = v.co.y
    old_z = v.co.z
    v.co.y = old_z
    v.co.z = old_y
bmesh.ops.translate(bm_fs, vec=(0, 0.445, 0.085), verts=bm_fs.verts)
mesh_fs = bpy.data.meshes.new("SMG_FrontShroud_Mesh")
bm_fs.to_mesh(mesh_fs)
bm_fs.free()
obj_fs = bpy.data.objects.new("SMG_FrontShroud", mesh_fs)
smg_col.objects.link(obj_fs)
bev_fs = obj_fs.modifiers.new("Bevel", 'BEVEL')
bev_fs.width = 0.002
apply_mat(obj_fs, mat_ceramic)

sight_front = make_box("Shroud_FrontSight", (0, 0.540, 0.125), (0.006, 0.016, 0.012), chamfer=0.0008)
apply_mat(sight_front, mat_gunmetal)

for s_x in [-0.030, 0.030]:
    shroud_cut = make_box(f"Shroud_Window_{s_x}", (s_x, 0.445, 0.085), (0.008, 0.115, 0.026), chamfer=0.001)
    apply_mat(shroud_cut, mat_gunmetal)

front_tube = make_cylinder("SMG_FrontPlasmaTube", (0, 0.445, 0.085), radius=0.014, depth=0.110, rot_euler=(math.radians(90), 0, 0), vertices=32)
apply_mat(front_tube, mat_glass)
front_tube.visible_shadow = False

front_plasma = make_cylinder("SMG_FrontPlasmaBeam", (0, 0.445, 0.085), radius=0.005, depth=0.105, rot_euler=(math.radians(90), 0, 0), vertices=16)
apply_mat(front_plasma, mat_plasma)

cap_front_rear = make_cylinder("FrontChamber_CapR", (0, 0.388, 0.085), radius=0.016, depth=0.012, rot_euler=(math.radians(90), 0, 0), vertices=24)
apply_mat(cap_front_rear, mat_gunmetal)
cap_front_front = make_cylinder("FrontChamber_CapF", (0, 0.502, 0.085), radius=0.016, depth=0.012, rot_euler=(math.radians(90), 0, 0), vertices=24)
apply_mat(cap_front_front, mat_gunmetal)

bm_mcap = bmesh.new()
bmesh.ops.create_cone(bm_mcap, cap_ends=True, segments=8, radius1=0.035, radius2=0.035, depth=0.020)
for v in bm_mcap.verts:
    old_y = v.co.y
    old_z = v.co.z
    v.co.y = old_z
    v.co.z = old_y
bmesh.ops.translate(bm_mcap, vec=(0, 0.565, 0.085), verts=bm_mcap.verts)
mesh_mcap = bpy.data.meshes.new("SMG_MuzzleCap_Mesh")
bm_mcap.to_mesh(mesh_mcap)
bm_mcap.free()
obj_mcap = bpy.data.objects.new("SMG_MuzzleCap", mesh_mcap)
smg_col.objects.link(obj_mcap)
bev_mcap = obj_mcap.modifiers.new("Bevel", 'BEVEL')
bev_mcap.width = 0.0015
apply_mat(obj_mcap, mat_gunmetal)

main_bore = make_cylinder("SMG_MainBore", (0, 0.575, 0.085), radius=0.009, depth=0.008, rot_euler=(math.radians(90), 0, 0), vertices=24)
apply_mat(main_bore, mat_rubber)
main_bore_glow = make_cylinder("SMG_MainBoreGlow", (0, 0.574, 0.085), radius=0.0098, depth=0.002, rot_euler=(math.radians(90), 0, 0), vertices=24)
apply_mat(main_bore_glow, mat_glow)

top_port = make_cylinder("SMG_TopPort", (0, 0.575, 0.104), radius=0.0055, depth=0.008, rot_euler=(math.radians(90), 0, 0), vertices=20)
apply_mat(top_port, mat_rubber)
top_port_glow = make_cylinder("SMG_TopPortGlow", (0, 0.574, 0.104), radius=0.0062, depth=0.002, rot_euler=(math.radians(90), 0, 0), vertices=20)
apply_mat(top_port_glow, mat_glow)

bot_port = make_cylinder("SMG_BotPort", (0, 0.575, 0.066), radius=0.0055, depth=0.008, rot_euler=(math.radians(90), 0, 0), vertices=20)
apply_mat(bot_port, mat_rubber)
bot_port_glow = make_cylinder("SMG_BotPortGlow", (0, 0.574, 0.066), radius=0.0062, depth=0.002, rot_euler=(math.radians(90), 0, 0), vertices=20)
apply_mat(bot_port_glow, mat_glow)

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
    bg.inputs['Strength'].default_value = 0.22

mesh_tab = bpy.data.meshes.new("TableMesh")
bm_t = bmesh.new()
bmesh.ops.create_grid(bm_t, size=15)
bm_t.to_mesh(mesh_tab)
bm_t.free()
tab = bpy.data.objects.new("StudioTable", mesh_tab)
tab.location = (0, 0.12, -0.18)
studio_col.objects.link(tab)
mat_tab = bpy.data.materials.new(name="M_StudioTable")
mat_tab.use_nodes = True
bsdf = mat_tab.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs['Base Color'].default_value = (0.018, 0.020, 0.025, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.20
    bsdf.inputs['Metallic'].default_value = 0.4
tab.data.materials.append(mat_tab)

lk = bpy.data.lights.new("KeyLight", 'AREA')
lk.energy = 65.0
lk.size = 1.6
lk.color = (0.94, 0.96, 1.0)
olk = bpy.data.objects.new("KeyLight", lk)
olk.location = (1.5, 0.15, 1.1)
olk.rotation_euler = (0.7, 0.2, 1.1)
studio_col.objects.link(olk)

lr = bpy.data.lights.new("RimLight", 'AREA')
lr.energy = 90.0
lr.size = 2.2
lr.color = (0.72, 0.18, 1.0)
olr = bpy.data.objects.new("RimLight", lr)
olr.location = (-1.5, 0.25, 0.85)
olr.rotation_euler = (-0.7, -0.3, -1.8)
studio_col.objects.link(olr)

lf = bpy.data.lights.new("FillLight", 'AREA')
lf.energy = 20.0
lf.size = 1.6
lf.color = (0.6, 0.8, 1.0)
olf = bpy.data.objects.new("FillLight", lf)
olf.location = (0.2, -1.2, 0.55)
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
    # 1. Hero Side Profile (Full length showing cylindrical drum profile seated tightly under receiver)
    ("smg_quad1_hero_side.png", (1.45, 0.14, 0.11), Vector((0, 0.14, 0.035)), 50),
    # 2. Front 3/4 Perspective (Showing front circular face of drum, winding key, neon arcs, and muzzle)
    ("smg_quad2_iso_front.png", (1.05, 0.65, 0.24), Vector((0, 0.20, 0.030)), 45),
    # 3. FPS / ADS View (Shooter's eye aiming over rear sight notch; drum wings visible symmetrically below)
    ("smg_quad3_fps_view.png", (0.0, -0.06, 0.166), Vector((0.0, 0.55, 0.108)), 38),
    # 4. Rear 3/4 Detail (Fixed ergonomic stock, drum seated in front of trigger guard, and reactor window)
    ("smg_quad4_rear_detail.png", (0.95, -0.12, 0.14), Vector((0, 0.02, 0.035)), 48)
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

master_save = r"E:\Darx_Proyect\Art\Blender\SM_Wep_PhaseSMG_Workspace.blend"
bpy.ops.wm.save_as_mainfile(filepath=master_save)
print('Workspace saved to:', master_save)
print('=== SMG RENDER COMPLETE ===')

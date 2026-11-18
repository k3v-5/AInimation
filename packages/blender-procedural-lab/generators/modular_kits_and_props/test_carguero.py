import bpy
import bmesh
import math
import os
from mathutils import Vector, Euler

R = math.radians
OUT_IMG = r"F:\Dev\Game\Art\Renders\test_carguero.png"

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
scene.render.resolution_x = 800
scene.render.resolution_y = 1200
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'High Contrast'

# Outline material (Fools-proof inverted hull in Blender 5.2 EEVEE)
mat_outline = bpy.data.materials.new(name="M_Outline")
mat_outline.use_nodes = True
mat_outline.surface_render_method = 'BLENDED'
nodes = mat_outline.node_tree.nodes
nodes.clear()
out_n = nodes.new('ShaderNodeOutputMaterial')
mix_n = nodes.new('ShaderNodeMixShader')
trans_n = nodes.new('ShaderNodeBsdfTransparent')
emit_n = nodes.new('ShaderNodeEmission')
emit_n.inputs['Color'].default_value = (0.05, 0.04, 0.04, 1.0)
geom_n = nodes.new('ShaderNodeNewGeometry')

mat_outline.node_tree.links.new(geom_n.outputs['Backfacing'], mix_n.inputs['Fac'])
mat_outline.node_tree.links.new(emit_n.outputs['Emission'], mix_n.inputs[1])
mat_outline.node_tree.links.new(trans_n.outputs['BSDF'], mix_n.inputs[2])
mat_outline.node_tree.links.new(mix_n.outputs['Shader'], out_n.inputs['Surface'])

def apply_style(obj, bevel_w=0.03, outline_t=0.012):
    if not obj or obj.type != 'MESH': return
    for p in obj.data.polygons: p.use_smooth = True
    if bevel_w > 0:
        b = obj.modifiers.new('B', 'BEVEL')
        b.width = bevel_w
        b.segments = 2
        b.limit_method = 'ANGLE'
        b.angle_limit = R(35)
        b.harden_normals = True
    if outline_t > 0:
        if mat_outline not in list(obj.data.materials):
            obj.data.materials.append(mat_outline)
        idx = list(obj.data.materials).index(mat_outline)
        s = obj.modifiers.new('S', 'SOLIDIFY')
        s.thickness = outline_t
        s.offset = 1.0
        s.material_offset = idx
        s.material_offset_rim = idx
        s.use_flip_normals = True

def make_mat(name, col, rough=0.5, met=0.0, emit_str=0.0, emit_col=None):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nodes = m.node_tree.nodes
    nodes.clear()
    out = nodes.new('ShaderNodeOutputMaterial')
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = col
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Metallic'].default_value = met
    if emit_str > 0:
        ec = emit_col if emit_col else col
        if 'Emission Color' in bsdf.inputs:
            bsdf.inputs['Emission Color'].default_value = ec
            bsdf.inputs['Emission Strength'].default_value = emit_str
        elif 'Emission' in bsdf.inputs:
            bsdf.inputs['Emission'].default_value = ec
            if 'Emission Strength' in bsdf.inputs:
                bsdf.inputs['Emission Strength'].default_value = emit_str
    m.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return m

# Materials
m_rust_hull = make_mat("M_RustHull", (0.55, 0.35, 0.22, 1.0), rough=0.6, met=0.4)
m_white_sup = make_mat("M_WhiteSup", (0.88, 0.85, 0.78, 1.0), rough=0.5)
m_win_glow = make_mat("M_WinGlow", (1.0, 0.88, 0.25, 1.0), emit_str=5.0)
m_funnel_red = make_mat("M_FunnelRed", (0.88, 0.24, 0.14, 1.0), rough=0.45)
m_dark = make_mat("M_Dark", (0.22, 0.22, 0.25, 1.0), rough=0.6, met=0.7)
m_yellow = make_mat("M_Yellow", (0.95, 0.74, 0.05, 1.0), rough=0.4)
m_acid = make_mat("M_Acid", (0.15, 0.95, 0.15, 1.0), rough=0.15, emit_str=2.2)
m_acid_glass = make_mat("M_AcidGlass", (0.6, 1.0, 0.7, 0.3), rough=0.1)
m_green_cargo = make_mat("M_CargoBox", (0.22, 0.52, 0.38, 1.0), rough=0.5)
m_rock = make_mat("M_Rock", (0.35, 0.32, 0.30, 1.0), rough=0.85)

# World background
world = scene.world or bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
wnodes = world.node_tree.nodes
wnodes.clear()
wout = wnodes.new('ShaderNodeOutputWorld')
wbg = wnodes.new('ShaderNodeBackground')
wbg.inputs['Color'].default_value = (0.04, 0.05, 0.09, 1.0)
wbg.inputs['Strength'].default_value = 1.0
world.node_tree.links.new(wbg.outputs['Background'], wout.inputs['Surface'])

# Star field
tcoord = wnodes.new('ShaderNodeTexCoord')
noise = wnodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value = 180.0
noise.inputs['Detail'].default_value = 8.0
world.node_tree.links.new(tcoord.outputs['Generated'], noise.inputs['Vector'])

ramp = wnodes.new('ShaderNodeValToRGB')
ramp.color_ramp.interpolation = 'CONSTANT'
ramp.color_ramp.elements[0].position = 0.84
ramp.color_ramp.elements[0].color = (0, 0, 0, 1)
ramp.color_ramp.elements[1].position = 0.86
ramp.color_ramp.elements[1].color = (1.8, 1.8, 2.0, 1)
world.node_tree.links.new(noise.outputs['Fac'], ramp.inputs['Fac'])

wmix = wnodes.new('ShaderNodeMix')
wmix.data_type = 'RGBA'
wmix.blend_type = 'ADD'
wmix.inputs['Factor'].default_value = 1.0
wmix.inputs[6].default_value = (0.04, 0.05, 0.10, 1.0)
world.node_tree.links.new(ramp.outputs['Color'], wmix.inputs[7])
world.node_tree.links.new(wmix.outputs[2], wbg.inputs['Color'])

# FRONT-FACING KEY SUN (Directly illuminates the front face of the ship towards +Y)
key_sun = bpy.data.lights.new("KeySun", 'SUN')
key_sun.energy = 4.5
key_sun.color = (1.0, 0.98, 0.92)
key_obj = bpy.data.objects.new("KeySunObj", key_sun)
key_obj.rotation_euler = (R(-40), R(25), 0)
bpy.context.collection.objects.link(key_obj)

# Front fill light
fill_light = bpy.data.lights.new("FillLight", 'AREA')
fill_light.energy = 350.0
fill_light.size = 25.0
fill_light.color = (0.75, 0.85, 1.0)
fill_obj = bpy.data.objects.new("FillObj", fill_light)
fill_obj.location = (-1.0, -18.0, 8.0)
fill_obj.rotation_euler = (R(60), 0, 0)
bpy.context.collection.objects.link(fill_obj)

# Acid glow point light inside vat
acid_light = bpy.data.lights.new("AcidLight", 'POINT')
acid_light.energy = 180.0
acid_light.color = (0.1, 0.95, 0.15)
al_obj = bpy.data.objects.new("AcidLightObj", acid_light)
al_obj.location = (0.4, -0.6, 0.6)
bpy.context.collection.objects.link(al_obj)

# ==============================================================================
# CARGUERO QUÍMICO MODEL (Faithful layout matching concept art)
# ==============================================================================
# 1. Main ship hull: Runs across diagonally
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.2, 0.8, 0.2))
hull = bpy.context.active_object
hull.scale = (11.5, 3.8, 3.6)
hull.rotation_euler = (R(2), R(-6), R(-25))
hull.data.materials.append(m_rust_hull)
apply_style(hull, bevel_w=0.04, outline_t=0.015)

# Rounded Bow on the left
bpy.ops.mesh.primitive_cylinder_add(radius=1.9, depth=3.6, location=(-4.8, 3.2, 1.0))
bow = bpy.context.active_object
bow.rotation_euler = (R(2), R(-6), R(-25))
bow.data.materials.append(m_rust_hull)
apply_style(bow, bevel_w=0.04, outline_t=0.015)

# 2. Superstructure Bridge (White tower on upper left)
bridge_pos = (-4.0, 2.6, 3.4)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=bridge_pos)
bridge = bpy.context.active_object
bridge.scale = (3.0, 3.2, 2.6)
bridge.rotation_euler = (R(2), R(-6), R(-25))
bridge.data.materials.append(m_white_sup)
apply_style(bridge, bevel_w=0.03, outline_t=0.014)

# Bridge Windows with glowing amber light
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(bridge_pos[0] + 0.8, bridge_pos[1] - 0.7, bridge_pos[2] + 0.5))
b_win = bpy.context.active_object
b_win.scale = (0.1, 2.8, 0.6)
b_win.rotation_euler = (R(2), R(-6), R(-25))
b_win.data.materials.append(m_win_glow)

# Lower bridge windows
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(bridge_pos[0] + 0.8, bridge_pos[1] - 0.7, bridge_pos[2] - 0.3))
b_win2 = bpy.context.active_object
b_win2.scale = (0.1, 2.8, 0.4)
b_win2.rotation_euler = (R(2), R(-6), R(-25))
b_win2.data.materials.append(m_win_glow)

# Nautical Red/Orange Funnel with black stripe
bpy.ops.mesh.primitive_cylinder_add(radius=0.48, depth=2.4, location=(bridge_pos[0] - 0.8, bridge_pos[1] + 0.6, bridge_pos[2] + 1.8))
funnel = bpy.context.active_object
funnel.rotation_euler = (R(2), R(-18), R(-25))
funnel.data.materials.append(m_funnel_red)
apply_style(funnel, bevel_w=0.02, outline_t=0.012)

bpy.ops.mesh.primitive_cylinder_add(radius=0.50, depth=0.4, location=(bridge_pos[0] - 1.15, bridge_pos[1] + 0.7, bridge_pos[2] + 2.8))
f_cap = bpy.context.active_object
f_cap.rotation_euler = (R(2), R(-18), R(-25))
f_cap.data.materials.append(m_dark)

# Radar mast
bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=2.6, location=(bridge_pos[0] + 0.2, bridge_pos[1] + 0.1, bridge_pos[2] + 2.5))
mast = bpy.context.active_object
mast.data.materials.append(m_dark)
for mz in [bridge_pos[2] + 2.2, bridge_pos[2] + 3.1]:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(bridge_pos[0] + 0.2, bridge_pos[1] + 0.1, mz))
    yard = bpy.context.active_object
    yard.scale = (1.2, 0.05, 0.05)
    yard.rotation_euler = (0, 0, R(-25))
    yard.data.materials.append(m_dark)

# 3. OPEN CUTAWAY ACID HOLD IN THE HULL (Center Foreground)
tank_pos = (0.4, -0.6, -0.1)
# Tank Back & Sides
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(tank_pos[0], tank_pos[1] + 0.8, tank_pos[2]))
t_back = bpy.context.active_object
t_back.scale = (5.6, 0.3, 2.4)
t_back.rotation_euler = (R(2), R(-6), R(-25))
t_back.data.materials.append(m_rust_hull)
apply_style(t_back, bevel_w=0.03, outline_t=0.012)

# Left wall of tank
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(tank_pos[0] - 2.4, tank_pos[1] - 0.2, tank_pos[2]))
t_left = bpy.context.active_object
t_left.scale = (0.3, 2.2, 2.4)
t_left.rotation_euler = (R(2), R(-6), R(-25))
t_left.data.materials.append(m_rust_hull)
apply_style(t_left, bevel_w=0.03, outline_t=0.012)

# Right wall of tank
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(tank_pos[0] + 2.4, tank_pos[1] + 0.2, tank_pos[2]))
t_right = bpy.context.active_object
t_right.scale = (0.3, 2.2, 2.4)
t_right.rotation_euler = (R(2), R(-6), R(-25))
t_right.data.materials.append(m_rust_hull)
apply_style(t_right, bevel_w=0.03, outline_t=0.012)

# Bottom of tank
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(tank_pos[0], tank_pos[1], tank_pos[2] - 1.1))
t_bot = bpy.context.active_object
t_bot.scale = (5.6, 2.2, 0.3)
t_bot.rotation_euler = (R(2), R(-6), R(-25))
t_bot.data.materials.append(m_rust_hull)
apply_style(t_bot, bevel_w=0.03, outline_t=0.012)

# Front Glass Wall (Cutaway viewing pane)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(tank_pos[0], tank_pos[1] - 0.95, tank_pos[2]))
t_glass = bpy.context.active_object
t_glass.scale = (5.2, 0.08, 2.1)
t_glass.rotation_euler = (R(2), R(-6), R(-25))
t_glass.data.materials.append(m_acid_glass)
apply_style(t_glass, bevel_w=0.01, outline_t=0.01)

# POOL OF VISCOUS NEON-GREEN GLOWING ACID
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(tank_pos[0], tank_pos[1], tank_pos[2] - 0.2))
acid = bpy.context.active_object
acid.scale = (5.0, 1.9, 1.4)
acid.rotation_euler = (R(2), R(-6), R(-25))
acid.data.materials.append(m_acid)

# Acid Vapor tentacle flames
for vx, vy, vz in [(-1.8, 0.1, 0.8), (-0.6, -0.1, 1.1), (0.7, 0.2, 0.9), (1.9, -0.2, 1.2)]:
    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.25, depth=1.6, location=(tank_pos[0] + vx, tank_pos[1] + vy, tank_pos[2] + vz))
    vap = bpy.context.active_object
    vap.rotation_euler = (R(12), R(-6), R(-25))
    vap.data.materials.append(m_acid)

# 4. THREE YELLOW VERTICAL GANTRY COLUMNS & OVERHEAD BEAM
for px, py in [(-1.8, 0.6), (0.2, -0.1), (2.1, -0.8)]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.14, depth=3.2, location=(tank_pos[0] + px, tank_pos[1] + py - 0.5, tank_pos[2] + 1.8))
    pillar = bpy.context.active_object
    pillar.rotation_euler = (R(2), R(-6), R(-25))
    pillar.data.materials.append(m_yellow)
    apply_style(pillar, bevel_w=0.02, outline_t=0.012)

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(tank_pos[0] + 0.15, tank_pos[1] - 0.2, tank_pos[2] + 3.2))
g_beam = bpy.context.active_object
g_beam.scale = (5.2, 0.35, 0.35)
g_beam.rotation_euler = (R(2), R(-6), R(-25))
g_beam.data.materials.append(m_yellow)
apply_style(g_beam, bevel_w=0.02, outline_t=0.012)

# 5. HYDRAULIC DECK CRANE ON THE RIGHT
crane_base = (3.8, -0.6, 1.8)
bpy.ops.mesh.primitive_cylinder_add(radius=0.55, depth=0.8, location=crane_base)
c_ped = bpy.context.active_object
c_ped.rotation_euler = (R(2), R(-6), R(-25))
c_ped.data.materials.append(m_dark)
apply_style(c_ped, bevel_w=0.02, outline_t=0.012)

# Crane arm reaching upward & left
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(crane_base[0] - 0.9, crane_base[1] - 0.3, crane_base[2] + 1.6))
arm1 = bpy.context.active_object
arm1.scale = (0.35, 0.35, 2.6)
arm1.rotation_euler = (R(-10), R(-38), R(-12))
arm1.data.materials.append(m_yellow)
apply_style(arm1, bevel_w=0.02, outline_t=0.012)

# Suspended green shipping container
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(crane_base[0] - 1.8, crane_base[1] - 0.7, crane_base[2] + 1.0))
box = bpy.context.active_object
box.scale = (1.4, 0.9, 0.8)
box.rotation_euler = (R(6), R(-10), R(15))
box.data.materials.append(m_green_cargo)
apply_style(box, bevel_w=0.02, outline_t=0.012)

# Stacked containers on the right deck
for cx, cy, cz in [(4.8, 0.5, 1.6), (4.4, 1.4, 1.6), (4.6, 0.9, 2.4)]:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(cx, cy, cz))
    c_box = bpy.context.active_object
    c_box.scale = (1.3, 0.85, 0.75)
    c_box.rotation_euler = (R(2), R(-6), R(-25))
    c_box.data.materials.append(m_green_cargo)
    apply_style(c_box, bevel_w=0.02, outline_t=0.012)

# 6. FLOATING ASTEROIDS & CRATES IN SPACE
for ax, ay, az, asz in [(-5.2, 4.2, 5.2, 0.65), (-6.2, 1.8, 4.0, 0.45), (-4.2, -2.5, -1.2, 0.55), (-3.2, -3.5, -1.8, 0.4)]:
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=asz, location=(ax, ay, az))
    ast = bpy.context.active_object
    ast.data.materials.append(m_rock)
    apply_style(ast, bevel_w=0.0, outline_t=0.012)

# Floating crates lower left
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-3.6, -1.8, -1.2))
fc1 = bpy.context.active_object
fc1.scale = (0.7, 0.7, 0.7)
fc1.rotation_euler = (R(22), R(35), R(-15))
fc1.data.materials.append(make_mat("M_BoxOrange", (0.85, 0.45, 0.15, 1.0), rough=0.6))
apply_style(fc1, bevel_w=0.02, outline_t=0.012)

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(-2.8, -2.4, -1.5))
fc2 = bpy.context.active_object
fc2.scale = (0.6, 0.6, 0.6)
fc2.rotation_euler = (R(-15), R(45), R(10))
fc2.data.materials.append(make_mat("M_BoxCyan", (0.2, 0.65, 0.75, 1.0), rough=0.6))
apply_style(fc2, bevel_w=0.02, outline_t=0.012)

# 7. CAMERA POSITION: Elevated 3/4 perspective matching concept art
cam_data = bpy.data.cameras.new("Cam")
cam_obj = bpy.data.objects.new("CamObj", cam_data)
bpy.context.collection.objects.link(cam_obj)
scene.camera = cam_obj

cam_obj.location = (-0.5, -17.5, 6.2)
cam_obj.rotation_euler = (R(70), 0, R(-1))
cam_data.lens = 28.0

scene.render.filepath = OUT_IMG
bpy.ops.render.render(write_still=True)
print(f"[OK] Rendered test to {OUT_IMG}")

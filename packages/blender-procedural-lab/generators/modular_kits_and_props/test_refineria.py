import bpy
import bmesh
import math
import os
from mathutils import Vector, Euler

R = math.radians
OUT_IMG = r"F:\Dev\Game\Art\Renders\test_refineria.png"

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
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

def apply_style(obj, bevel_w=0.02, outline_t=0.012):
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
m_tokamak = make_mat("M_TokamakArmor", (0.32, 0.36, 0.40, 1.0), rough=0.45, met=0.75)
m_brass = make_mat("M_BrassCoil", (0.88, 0.70, 0.22, 1.0), rough=0.3, met=0.9)
m_plasma = make_mat("M_PlasmaCyan", (0.15, 0.95, 1.0, 1.0), rough=0.1, emit_str=4.5)
m_yellow = make_mat("M_YellowSafety", (0.95, 0.74, 0.05, 1.0), rough=0.4)
m_grate = make_mat("M_SteelGrate", (0.24, 0.26, 0.28, 1.0), rough=0.55, met=0.6)
m_rock = make_mat("M_BasaltRock", (0.28, 0.26, 0.25, 1.0), rough=0.85)

# World & Stars
world = scene.world or bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
wnodes = world.node_tree.nodes
wnodes.clear()
wout = wnodes.new('ShaderNodeOutputWorld')
wbg = wnodes.new('ShaderNodeBackground')
wbg.inputs['Color'].default_value = (0.02, 0.03, 0.06, 1.0)
world.node_tree.links.new(wbg.outputs['Background'], wout.inputs['Surface'])

tcoord = wnodes.new('ShaderNodeTexCoord')
noise = wnodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value = 160.0
noise.inputs['Detail'].default_value = 10.0
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
wmix.inputs[6].default_value = (0.03, 0.04, 0.08, 1.0)
world.node_tree.links.new(ramp.outputs['Color'], wmix.inputs[7])
world.node_tree.links.new(wmix.outputs[2], wbg.inputs['Color'])

# Cosmic Key Sun from front-right
sun = bpy.data.lights.new("Sun", 'SUN')
sun.energy = 4.0
sun.color = (0.95, 0.96, 1.0)
s_obj = bpy.data.objects.new("SunObj", sun)
s_obj.rotation_euler = (R(-35), R(30), 0)
bpy.context.collection.objects.link(s_obj)

# Blue Plasma Point Light from Tokamak Center
l_plas = bpy.data.lights.new("PlasmaLight", 'POINT')
l_plas.energy = 650.0
l_plas.color = (0.2, 0.95, 1.0)
lo_plas = bpy.data.objects.new("PlasmaLightObj", l_plas)
lo_plas.location = (2.2, 1.2, 3.8)
bpy.context.collection.objects.link(lo_plas)

# Soft front fill
fill = bpy.data.lights.new("Fill", 'AREA')
fill.energy = 260.0
fill.size = 20.0
fill.color = (0.7, 0.8, 0.95)
fo = bpy.data.objects.new("FillObj", fill)
fo.location = (-1.0, -12.0, 6.0)
fo.rotation_euler = (R(60), 0, 0)
bpy.context.collection.objects.link(fo)

# ==============================================================================
# REFINERÍA DE PLASMA MODEL (media_1791198833604.jpg right panel)
# ==============================================================================
# 1. CURVED METALLIC CATWALK IN FOREGROUND
# Curved walkway from (-1.5, -3.5, 0.2) curving around to (-2.8, 1.8, 1.8)
bpy.ops.mesh.primitive_torus_add(major_radius=4.8, minor_radius=0.6, location=(-1.2, -0.8, 1.0))
walk = bpy.context.active_object
walk.scale = (0.9, 0.75, 0.12)
walk.data.materials.append(m_grate)
apply_style(walk, bevel_w=0.02, outline_t=0.012)

# Safety railing
bpy.ops.mesh.primitive_torus_add(major_radius=5.35, minor_radius=0.045, location=(-1.2, -0.8, 1.6))
w_rail = bpy.context.active_object
w_rail.scale = (0.9, 0.75, 1.0)
w_rail.data.materials.append(m_yellow)
apply_style(w_rail, bevel_w=0.01, outline_t=0.01)

# Walkway support struts
for sx, sy in [(-1.8, -2.5), (-0.2, -2.8), (1.4, -1.8)]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=3.5, location=(sx, sy, -0.6))
    post = bpy.context.active_object
    post.data.materials.append(m_tokamak)
    apply_style(post, bevel_w=0.01, outline_t=0.01)

# 2. AIRLOCK DOORWAY ON THE LEFT (End of catwalk)
gate_pos = (-2.8, 2.2, 2.4)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=gate_pos)
gate = bpy.context.active_object
gate.scale = (2.0, 0.5, 3.2)
gate.data.materials.append(m_tokamak)
apply_style(gate, bevel_w=0.03, outline_t=0.012)

# Illuminated Yellow Sign over Door: REFINERÍA DE PLASMA
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(gate_pos[0], gate_pos[1] - 0.3, gate_pos[2] + 1.9))
sign_r = bpy.context.active_object
sign_r.scale = (1.6, 0.06, 0.45)
sign_r.data.materials.append(m_yellow)
apply_style(sign_r, bevel_w=0.01, outline_t=0.01)

# 3. COLOSSAL VERTICAL TOKAMAK REACTOR ON THE RIGHT
t_loc = (2.2, 1.5, 3.8)

# Torus outer magnetic casing
bpy.ops.mesh.primitive_torus_add(major_radius=2.6, minor_radius=0.6, location=t_loc)
t_casing = bpy.context.active_object
t_casing.rotation_euler = (R(90), 0, 0)
t_casing.data.materials.append(m_tokamak)
apply_style(t_casing, bevel_w=0.03, outline_t=0.014)

# LUMINOUS CYAN PLASMA VORTEX RING IN CENTER
bpy.ops.mesh.primitive_torus_add(major_radius=1.85, minor_radius=0.28, location=t_loc)
p_ring = bpy.context.active_object
p_ring.rotation_euler = (R(90), 0, 0)
p_ring.data.materials.append(m_plasma)

# Central bright fusion spark core
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.45, location=t_loc)
p_core = bpy.context.active_object
p_core.data.materials.append(m_plasma)

# Electric plasma arcs converging to center
for ang in [0, 60, 120, 180, 240, 300]:
    a_rad = R(ang)
    lx = t_loc[0] + 1.1 * math.cos(a_rad)
    lz = t_loc[2] + 1.1 * math.sin(a_rad)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.035, depth=1.6, location=(lx, t_loc[1], lz))
    bolt = bpy.context.active_object
    bolt.rotation_euler = (0, -a_rad + R(90), 0)
    bolt.data.materials.append(m_plasma)

# 6 Brass magnetic clamp coils around the torus
for ang in [0, 60, 120, 180, 240, 300]:
    a_rad = R(ang)
    cx = t_loc[0] + 2.6 * math.cos(a_rad)
    cz = t_loc[2] + 2.6 * math.sin(a_rad)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.24, depth=0.85, location=(cx, t_loc[1], cz))
    clamp = bpy.context.active_object
    clamp.rotation_euler = (0, -a_rad, 0)
    clamp.data.materials.append(m_brass)
    apply_style(clamp, bevel_w=0.015, outline_t=0.01)

# 4. BASE MACHINERY & HEAVY COOLING PIPES
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(t_loc[0], t_loc[1] - 0.4, 0.9))
base_mach = bpy.context.active_object
base_mach.scale = (4.4, 2.2, 1.8)
base_mach.data.materials.append(m_tokamak)
apply_style(base_mach, bevel_w=0.03, outline_t=0.012)

# Hazard Sign: PELIGRO ALTA ENERGÍA
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(t_loc[0] + 1.8, t_loc[1] - 1.55, 1.1))
dang = bpy.context.active_object
dang.scale = (0.75, 0.05, 0.45)
dang.data.materials.append(m_yellow)
apply_style(dang, bevel_w=0.01, outline_t=0.01)

# Heavy coolant conduits connecting reactor
for px in [-1.5, 1.5]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.18, depth=2.8, location=(t_loc[0] + px, t_loc[1] - 0.2, 2.2))
    pipe = bpy.context.active_object
    pipe.data.materials.append(m_tokamak)
    apply_style(pipe, bevel_w=0.015, outline_t=0.01)

# 5. MAINTENANCE SERVICE DRONE HOVERING UNDER CATWALK
drone_pos = (-0.6, -2.4, 1.1)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=drone_pos)
drone = bpy.context.active_object
drone.scale = (0.45, 0.45, 0.25)
drone.data.materials.append(m_tokamak)
apply_style(drone, bevel_w=0.015, outline_t=0.01)

# Drone searchlight
bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=0.1, location=(drone_pos[0], drone_pos[1] - 0.25, drone_pos[2]))
d_light = bpy.context.active_object
d_light.rotation_euler = (R(90), 0, 0)
d_light.data.materials.append(m_yellow)

# 6. FLOATING BASALT ASTEROIDS IN BACKGROUND
for ax, ay, az, asz in [(-3.8, 3.8, 4.8, 0.8), (4.5, 3.2, 5.5, 1.1), (-2.8, -3.8, 0.2, 0.5), (3.6, -3.2, 0.6, 0.6)]:
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=asz, location=(ax, ay, az))
    ast = bpy.context.active_object
    ast.data.materials.append(m_rock)
    apply_style(ast, bevel_w=0.0, outline_t=0.01)

# 7. CAMERA SETUP: Exact perspective like media_1791198833604.jpg right panel
cam_data = bpy.data.cameras.new("Cam")
cam_obj = bpy.data.objects.new("CamObj", cam_data)
bpy.context.collection.objects.link(cam_obj)
scene.camera = cam_obj

cam_obj.location = (-0.5, -9.8, 2.8)
cam_obj.rotation_euler = (R(78), 0, R(-3))
cam_data.lens = 28.0

scene.render.filepath = OUT_IMG
bpy.ops.render.render(write_still=True)
print(f"[OK] Rendered test to {OUT_IMG}")

import bpy
import bmesh
import math
import os
from mathutils import Vector, Euler

R = math.radians
OUT_IMG = r"F:\Dev\Game\Art\Renders\test_crucero.png"

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 800
scene.render.resolution_y = 1200
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'High Contrast'

# Outline material
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
m_carpet = make_mat("M_WineCarpet", (0.38, 0.08, 0.14, 1.0), rough=0.8)
m_gold = make_mat("M_ArtDecoGold", (0.92, 0.74, 0.25, 1.0), rough=0.25, met=0.92)
m_wood = make_mat("M_Mahogany", (0.28, 0.14, 0.10, 1.0), rough=0.45, met=0.05)
m_velvet = make_mat("M_VelvetChair", (0.46, 0.09, 0.18, 1.0), rough=0.75)
m_lamp_shade = make_mat("M_LampShade", (1.0, 0.92, 0.75, 1.0), rough=0.3, emit_str=3.8)
m_saturn = make_mat("M_SaturnPlanet", (0.88, 0.80, 0.65, 1.0), rough=0.6)
m_rings = make_mat("M_SaturnRings", (0.95, 0.88, 0.72, 1.0), rough=0.4, emit_str=2.0)
m_moon = make_mat("M_BlueMoon", (0.35, 0.68, 0.95, 1.0), rough=0.55)

# World
world = scene.world or bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
wnodes = world.node_tree.nodes
wnodes.clear()
wout = wnodes.new('ShaderNodeOutputWorld')
wbg = wnodes.new('ShaderNodeBackground')
wbg.inputs['Color'].default_value = (0.02, 0.03, 0.06, 1.0)
world.node_tree.links.new(wbg.outputs['Background'], wout.inputs['Surface'])

# Stars
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

# Interior Warm Ambient & Chandelier Light
l_amb = bpy.data.lights.new("WarmAmb", 'AREA')
l_amb.energy = 220.0
l_amb.size = 12.0
l_amb.color = (1.0, 0.92, 0.82)
lo_amb = bpy.data.objects.new("WarmAmbObj", l_amb)
lo_amb.location = (0.0, 0.0, 5.5)
lo_amb.rotation_euler = (R(75), 0, 0)
bpy.context.collection.objects.link(lo_amb)

# Soft cosmic fill light from outside window (left)
l_cosmic = bpy.data.lights.new("CosmicFill", 'SUN')
l_cosmic.energy = 1.8
l_cosmic.color = (0.6, 0.75, 1.0)
lo_cosmic = bpy.data.objects.new("CosmicFillObj", l_cosmic)
lo_cosmic.rotation_euler = (R(25), R(55), 0)
bpy.context.collection.objects.link(lo_cosmic)

# ==============================================================================
# CRUCERO CELESTIA MODEL (Exact layout like media_1791198833604.jpg middle panel)
# ==============================================================================
# 1. Burgundy Carpet Floor with Golden geometric borders
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 1.0, 0.0))
carpet = bpy.context.active_object
carpet.scale = (9.0, 10.0, 0.1)
carpet.data.materials.append(m_carpet)

# Gold borders on carpet
for gy in [-1.5, 1.2]:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, gy, 0.06))
    gb = bpy.context.active_object
    gb.scale = (3.6, 2.8, 0.015)
    gb.data.materials.append(m_gold)

# 2. Back Mahogany Walls with Art Déco Panel Inlays
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(1.5, 4.8, 3.6))
back_wall = bpy.context.active_object
back_wall.scale = (7.0, 0.3, 7.2)
back_wall.data.materials.append(m_wood)
apply_style(back_wall, bevel_w=0.03, outline_t=0.012)

# Art Déco Gold Inlay Panels on the back wall
for px in [-0.6, 1.8]:
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(px, 4.62, 3.8))
    panel = bpy.context.active_object
    panel.scale = (1.4, 0.04, 2.4)
    panel.data.materials.append(m_wood)
    apply_style(panel, bevel_w=0.02, outline_t=0.01)

    # Diamond center
    bpy.ops.mesh.primitive_cylinder_add(vertices=4, radius=0.42, depth=0.05, location=(px, 4.58, 3.8), rotation=(R(90), R(45), 0))
    diam = bpy.context.active_object
    diam.data.materials.append(m_gold)

# Doorway with Art Déco pediment
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(3.2, 4.6, 2.0))
door = bpy.context.active_object
door.scale = (1.6, 0.1, 3.6)
door.data.materials.append(m_wood)
apply_style(door, bevel_w=0.02, outline_t=0.012)

# 3. GRAND PANORAMIC ART DÉCO ARCH WINDOW ON THE LEFT
# The arch frames the entire left side:
bpy.ops.mesh.primitive_torus_add(major_radius=4.2, minor_radius=0.18, location=(-2.6, 1.2, 3.8))
arch = bpy.context.active_object
arch.scale = (0.35, 1.15, 1.2)
arch.rotation_euler = (0, R(90), 0)
arch.data.materials.append(m_gold)
apply_style(arch, bevel_w=0.02, outline_t=0.012)

# Concentric inner arch strut
bpy.ops.mesh.primitive_torus_add(major_radius=3.7, minor_radius=0.08, location=(-2.6, 1.2, 3.8))
arch_inner = bpy.context.active_object
arch_inner.scale = (0.35, 1.15, 1.2)
arch_inner.rotation_euler = (0, R(90), 0)
arch_inner.data.materials.append(m_gold)
apply_style(arch_inner, bevel_w=0.01, outline_t=0.01)

# Radial window mullions
for ang in [20, 40, 60]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=4.2, location=(-2.6, 1.2, 3.8))
    mull = bpy.context.active_object
    mull.rotation_euler = (R(ang), 0, 0)
    mull.data.materials.append(m_gold)
    apply_style(mull, bevel_w=0.01, outline_t=0.01)

# 4. SATURN WITH RINGS & BLUE PLANETOID (Perfect line of sight through window)
saturn_pos = (-8.5, 3.2, 4.8)
bpy.ops.mesh.primitive_uv_sphere_add(radius=2.0, location=saturn_pos)
sat = bpy.context.active_object
sat.data.materials.append(m_saturn)

# Rings of Saturn
for r_rad, r_thick in [(3.2, 0.25), (4.0, 0.35)]:
    bpy.ops.mesh.primitive_torus_add(major_radius=r_rad, minor_radius=0.05, location=saturn_pos)
    ring = bpy.context.active_object
    ring.scale = (1.0, 1.0, 0.08)
    ring.rotation_euler = (R(28), R(-22), 0)
    ring.data.materials.append(m_rings)

# Blue moon below
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.9, location=(-7.2, 2.0, 1.6))
b_moon = bpy.context.active_object
b_moon.data.materials.append(m_moon)

# 5. VELVET ARMCHAIRS & COCKTAIL TABLES WITH LAMPS
# In foreground right: cozy armchair and table with glowing lamp shade
bpy.ops.mesh.primitive_cylinder_add(radius=0.55, depth=0.45, location=(0.4, -1.8, 0.45))
chair_fg = bpy.context.active_object
chair_fg.data.materials.append(m_velvet)
apply_style(chair_fg, bevel_w=0.03, outline_t=0.012)

bpy.ops.mesh.primitive_cylinder_add(radius=0.58, depth=0.9, location=(0.6, -1.7, 0.85))
back_fg = bpy.context.active_object
back_fg.scale = (0.7, 1.0, 1.0)
back_fg.data.materials.append(m_velvet)
apply_style(back_fg, bevel_w=0.03, outline_t=0.012)

# Table with lamp in immediate foreground right
bpy.ops.mesh.primitive_cylinder_add(radius=0.35, depth=0.6, location=(1.2, -1.4, 0.35))
t_fg = bpy.context.active_object
t_fg.data.materials.append(m_gold)
apply_style(t_fg, bevel_w=0.02, outline_t=0.01)

bpy.ops.mesh.primitive_cone_add(radius1=0.28, depth=0.45, location=(1.2, -1.4, 0.95))
lamp_fg = bpy.context.active_object
lamp_fg.data.materials.append(m_lamp_shade)
apply_style(lamp_fg, bevel_w=0.01, outline_t=0.01)

# Point light from lamp
l_lamp = bpy.data.lights.new("LampFG", 'POINT')
l_lamp.energy = 85.0
l_lamp.color = (1.0, 0.92, 0.75)
lo_lamp = bpy.data.objects.new("LampFGObj", l_lamp)
lo_lamp.location = (1.2, -1.4, 1.0)
bpy.context.collection.objects.link(lo_lamp)

# Mid-ground armchairs along the window
for cy in [0.0, 1.8]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.52, depth=0.42, location=(-1.2, cy, 0.45))
    c_mid = bpy.context.active_object
    c_mid.data.materials.append(m_velvet)
    apply_style(c_mid, bevel_w=0.03, outline_t=0.012)

    bpy.ops.mesh.primitive_cylinder_add(radius=0.55, depth=0.85, location=(-1.0, cy, 0.85))
    b_mid = bpy.context.active_object
    b_mid.scale = (0.7, 1.0, 1.0)
    b_mid.data.materials.append(m_velvet)
    apply_style(b_mid, bevel_w=0.03, outline_t=0.012)

    # Small cocktail table between them
    bpy.ops.mesh.primitive_cylinder_add(radius=0.25, depth=0.5, location=(-0.4, cy, 0.35))
    t_mid = bpy.context.active_object
    t_mid.data.materials.append(m_gold)
    apply_style(t_mid, bevel_w=0.01, outline_t=0.01)

# 6. GRAND STAIRCASE ON THE RIGHT
stair_x = 3.2
for i in range(9):
    sy = 0.5 + i * 0.42
    sz = i * 0.25
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(stair_x, sy, sz + 0.12))
    step = bpy.context.active_object
    step.scale = (1.8, 0.42, 0.25)
    step.data.materials.append(m_wood)
    apply_style(step, bevel_w=0.015, outline_t=0.01)

# Golden brass handrail
bpy.ops.mesh.primitive_cylinder_add(radius=0.045, depth=4.6, location=(stair_x - 0.8, 2.2, 2.2), rotation=(R(-31), 0, 0))
rail = bpy.context.active_object
rail.data.materials.append(m_gold)
apply_style(rail, bevel_w=0.01, outline_t=0.01)

# 7. TIERED ART DÉCO CHANDELIERS IN CEILING
for ly in [0.0, 2.5]:
    cp = (0.4, ly, 6.2)
    for dr, dz in [(1.0, 0.0), (0.75, -0.2), (0.5, -0.38)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=dr, depth=0.12, location=(cp[0], cp[1], cp[2] + dz))
        disc = bpy.context.active_object
        disc.data.materials.append(m_gold if dz == 0.0 else m_lamp_shade)
        apply_style(disc, bevel_w=0.015, outline_t=0.01)

# 8. CAMERA SETUP: Looking toward the panoramic window and lounge
cam_data = bpy.data.cameras.new("Cam")
cam_obj = bpy.data.objects.new("CamObj", cam_data)
bpy.context.collection.objects.link(cam_obj)
scene.camera = cam_obj

cam_obj.location = (1.2, -6.8, 2.5)
cam_obj.rotation_euler = (R(76), 0, R(12))
cam_data.lens = 19.0

scene.render.filepath = OUT_IMG
bpy.ops.render.render(write_still=True)
print(f"[OK] Rendered test to {OUT_IMG}")

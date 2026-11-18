import bpy
from mathutils import Vector, Euler
from math import radians as R

blend_path = r"E:\Darx_Proyect\Saved\Player_Skin_Workspace\DarX_Player_LatexHuman_V2.blend"
bpy.ops.wm.open_mainfile(filepath=blend_path)
scene = bpy.context.scene

char = bpy.data.objects.get("SK_DarX_LatexHuman_Eyeless")

# Crear o actualizar shader de Fluido Oscuro con Destellos Morados
mat = bpy.data.materials.new(name="M_DarX_DarkFluid_PurpleSparks")
mat.use_nodes = True
nt = mat.node_tree
nt.nodes.clear()

out_node = nt.nodes.new("ShaderNodeOutputMaterial")
out_node.location = (1200, 0)

bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
bsdf.location = (800, 0)
nt.links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])

# Coordenadas y mapeo
tex_coord = nt.nodes.new("ShaderNodeTexCoord")
tex_coord.location = (-800, 0)

mapping = nt.nodes.new("ShaderNodeMapping")
mapping.location = (-600, 0)
mapping.inputs["Scale"].default_value = (3.5, 3.5, 3.5)
nt.links.new(tex_coord.outputs["Object"], mapping.inputs["Vector"])

# Textura Voronoi para destellos/chispas concentradas
voronoi = nt.nodes.new("ShaderNodeTexVoronoi")
voronoi.location = (-350, 150)
voronoi.feature = 'SMOOTH_F1'
voronoi.inputs["Scale"].default_value = 8.0
voronoi.inputs["Smoothness"].default_value = 0.5
nt.links.new(mapping.outputs["Vector"], voronoi.inputs["Vector"])

# Textura de Ruido para ondas de fluido oscuras
noise = nt.nodes.new("ShaderNodeTexNoise")
noise.location = (-350, -150)
noise.inputs["Scale"].default_value = 6.5
noise.inputs["Detail"].default_value = 4.0
noise.inputs["Roughness"].default_value = 0.55
nt.links.new(mapping.outputs["Vector"], noise.inputs["Vector"])

# Mezcla de texturas
mix = nt.nodes.new("ShaderNodeMix")
mix.data_type = 'FLOAT'
mix.location = (-100, 0)
mix.inputs["Factor"].default_value = 0.65
nt.links.new(voronoi.outputs["Distance"], mix.inputs[2]) # A
nt.links.new(noise.outputs["Fac"], mix.inputs[3])       # B

# Rampa de Color para Base Color (Fluido negro a destellos morados)
cr_base = nt.nodes.new("ShaderNodeValToRGB")
cr_base.location = (200, 150)
cr_base.color_ramp.interpolation = 'EASE'
cr_base.color_ramp.elements[0].position = 0.48
cr_base.color_ramp.elements[0].color = (0.002, 0.002, 0.004, 1.0) # Fluido negro profundo
cr_base.color_ramp.elements[1].position = 0.68
cr_base.color_ramp.elements[1].color = (0.28, 0.01, 0.60, 1.0)    # Violeta oscuro
e3 = cr_base.color_ramp.elements.new(0.82)
e3.color = (0.75, 0.02, 1.0, 1.0)                                  # Destello Morado Neon
e4 = cr_base.color_ramp.elements.new(0.95)
e4.color = (0.98, 0.70, 1.0, 1.0)                                  # Chispas nucleares lavanda
nt.links.new(mix.outputs["Result"], cr_base.inputs["Fac"])
nt.links.new(cr_base.outputs["Color"], bsdf.inputs["Base Color"])

# Rampa para Emision de Destellos
cr_emit = nt.nodes.new("ShaderNodeValToRGB")
cr_emit.location = (200, -150)
cr_emit.color_ramp.interpolation = 'B_SPLINE'
cr_emit.color_ramp.elements[0].position = 0.72
cr_emit.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)       # Cero emision en el cuerpo
cr_emit.color_ramp.elements[1].position = 0.94
cr_emit.color_ramp.elements[1].color = (0.85, 0.15, 1.0, 1.0)     # Destello morado puro
nt.links.new(mix.outputs["Result"], cr_emit.inputs["Fac"])
nt.links.new(cr_emit.outputs["Color"], bsdf.inputs["Emission Color"])

# Fuerza de emision
math_emit = nt.nodes.new("ShaderNodeMath")
math_emit.location = (500, -150)
math_emit.operation = 'MULTIPLY'
math_emit.inputs[1].default_value = 6.0
nt.links.new(cr_emit.outputs["Color"], math_emit.inputs[0])
nt.links.new(math_emit.outputs["Value"], bsdf.inputs["Emission Strength"])

# Relieve fluido (Bump)
bump = nt.nodes.new("ShaderNodeBump")
bump.location = (500, 50)
bump.inputs["Strength"].default_value = 0.025
bump.inputs["Distance"].default_value = 0.012
nt.links.new(mix.outputs["Result"], bump.inputs["Height"])
nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

# Parametros fisicos del Principled BSDF
bsdf.inputs["Metallic"].default_value = 0.0
bsdf.inputs["Roughness"].default_value = 0.055
bsdf.inputs["IOR"].default_value = 1.58
if "Coat Weight" in bsdf.inputs:
    bsdf.inputs["Coat Weight"].default_value = 1.0
    bsdf.inputs["Coat Roughness"].default_value = 0.025
    if "Coat IOR" in bsdf.inputs:
        bsdf.inputs["Coat IOR"].default_value = 1.60

char.data.materials.clear()
char.data.materials.append(mat)

# Test Render Hero View
cam_obj = bpy.data.objects.get("Cam_RenderMaster")
cam_obj.location = Vector((1.6, -3.0, 1.25))
dir_vec = Vector((0, 0, 0.90)) - cam_obj.location
cam_obj.rotation_euler = dir_vec.to_track_quat('-Z', 'Y').to_euler()
cam_obj.data.angle = R(38)

scene.render.resolution_x = 720
scene.render.resolution_y = 720
out_p = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2\scratch\test_darkfluid_hero.png"
scene.render.filepath = out_p
bpy.ops.render.render(write_still=True)
print("TEST_DARKFLUID_SAVED:", out_p)

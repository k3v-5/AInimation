import bpy
from mathutils import Vector, Euler
from math import radians as R

blend_path = r"E:\Darx_Proyect\Saved\Player_Skin_Workspace\DarX_Player_LatexHuman_V2.blend"
bpy.ops.wm.open_mainfile(filepath=blend_path)
scene = bpy.context.scene

char = bpy.data.objects.get("SK_DarX_LatexHuman_Eyeless")

# Aplicar la receta maestra de Fluido Oscuro con Destellos Morados (DarkFluid V9)
mat = bpy.data.materials.new(name="M_DarX_DarkFluid_PurpleSparks")
mat.use_nodes = True
nt = mat.node_tree
nt.nodes.clear()

out_node = nt.nodes.new("ShaderNodeOutputMaterial")
out_node.location = (1200, 0)

bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
bsdf.location = (850, 0)
nt.links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])

# Coordenadas y Mapping
tex_coord = nt.nodes.new("ShaderNodeTexCoord")
tex_coord.location = (-900, 0)

mapping = nt.nodes.new("ShaderNodeMapping")
mapping.location = (-700, 0)
mapping.inputs["Scale"].default_value = (3.5, 3.5, 1.8) # Proporcional a la altura del personaje
nt.links.new(tex_coord.outputs["Object"], mapping.inputs["Vector"])

# Voronoi Texture (Células y Destellos)
voronoi = nt.nodes.new("ShaderNodeTexVoronoi")
voronoi.location = (-450, 150)
voronoi.feature = 'SMOOTH_F1'
voronoi.inputs["Scale"].default_value = 6.2
voronoi.inputs["Smoothness"].default_value = 0.8
nt.links.new(mapping.outputs["Vector"], voronoi.inputs["Vector"])

# Noise Texture (Corrientes de fluido oscuro)
noise = nt.nodes.new("ShaderNodeTexNoise")
noise.location = (-450, -150)
noise.inputs["Scale"].default_value = 7.5
noise.inputs["Detail"].default_value = 4.0
noise.inputs["Roughness"].default_value = 0.48
nt.links.new(mapping.outputs["Vector"], noise.inputs["Vector"])

# Mix de texturas (80% Voronoi + 20% Ruido)
mix = nt.nodes.new("ShaderNodeMix")
mix.data_type = 'FLOAT'
mix.location = (-200, 0)
mix.inputs["Factor"].default_value = 0.80
nt.links.new(voronoi.outputs["Distance"], mix.inputs[2]) # A
nt.links.new(noise.outputs["Fac"], mix.inputs[3])       # B

# Rampa de Color para Base Color (Fluido negro oscuro a destellos morados)
cr_base = nt.nodes.new("ShaderNodeValToRGB")
cr_base.location = (150, 150)
cr_base.color_ramp.interpolation = 'LINEAR'
cr_base.color_ramp.elements[0].position = 0.52
cr_base.color_ramp.elements[0].color = (0.001, 0.001, 0.002, 1.0) # Fluido negro obsidiana
cr_base.color_ramp.elements[1].position = 0.64
cr_base.color_ramp.elements[1].color = (0.22, 0.0, 0.60, 1.0)     # Violeta fluido
e3 = cr_base.color_ramp.elements.new(0.76)
e3.color = (0.68, 0.02, 1.0, 1.0)                                  # Destello Morado Neón
e4 = cr_base.color_ramp.elements.new(0.88)
e4.color = (0.92, 0.05, 0.90, 1.0)                                  # Chispas magenta
e5 = cr_base.color_ramp.elements.new(0.96)
e5.color = (0.98, 0.75, 1.0, 1.0)                                  # Destello lavanda incandescente
nt.links.new(mix.outputs["Result"], cr_base.inputs["Fac"])
nt.links.new(cr_base.outputs["Color"], bsdf.inputs["Base Color"])

# Rampa para Emisión de Destellos
cr_emit = nt.nodes.new("ShaderNodeValToRGB")
cr_emit.location = (150, -150)
cr_emit.color_ramp.interpolation = 'B_SPLINE'
cr_emit.color_ramp.elements[0].position = 0.65
cr_emit.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)       # Cero emisión en el fluido oscuro
cr_emit.color_ramp.elements[1].position = 0.94
cr_emit.color_ramp.elements[1].color = (1.0, 1.0, 1.0, 1.0)       # Máxima intensidad
nt.links.new(mix.outputs["Result"], cr_emit.inputs["Fac"])

# Multiplicador de Emisión (Fuerza de brillo de los destellos)
math_emit = nt.nodes.new("ShaderNodeMath")
math_emit.location = (450, -150)
math_emit.operation = 'MULTIPLY'
math_emit.inputs[1].default_value = 8.0
nt.links.new(cr_emit.outputs["Color"], math_emit.inputs[0])
nt.links.new(math_emit.outputs["Value"], bsdf.inputs["Emission Strength"])
nt.links.new(cr_base.outputs["Color"], bsdf.inputs["Emission Color"])

# Bump sutil de ondas de fluido
bump = nt.nodes.new("ShaderNodeBump")
bump.location = (450, 50)
bump.inputs["Strength"].default_value = 0.022
bump.inputs["Distance"].default_value = 0.012
nt.links.new(mix.outputs["Result"], bump.inputs["Height"])
nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

# Parámetros físicos de Fluido Pulido
bsdf.inputs["Metallic"].default_value = 0.0
bsdf.inputs["Roughness"].default_value = 0.048
bsdf.inputs["IOR"].default_value = 1.62
if "Coat Weight" in bsdf.inputs:
    bsdf.inputs["Coat Weight"].default_value = 1.0
    bsdf.inputs["Coat Roughness"].default_value = 0.015
    if "Coat IOR" in bsdf.inputs:
        bsdf.inputs["Coat IOR"].default_value = 1.55

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
out_p = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2\scratch\test_darkfluid_v9_hero.png"
scene.render.filepath = out_p
bpy.ops.render.render(write_still=True)
print("TEST_DARKFLUID_V9_SAVED:", out_p)

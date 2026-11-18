import bpy
from mathutils import Vector, Euler
from math import radians as R

blend_path = r"E:\Darx_Proyect\Saved\Player_Skin_Workspace\DarX_Player_LatexHuman_V2.blend"
bpy.ops.wm.open_mainfile(filepath=blend_path)
scene = bpy.context.scene

char = bpy.data.objects.get("SK_DarX_LatexHuman_Eyeless")

# Crear Shader Maestro de Fluido Oscuro con Destellos Morados (Dark Fluid with Purple Sparkles)
mat = bpy.data.materials.new(name="M_DarX_DarkFluid_PurpleSparks")
mat.use_nodes = True
nt = mat.node_tree
nt.nodes.clear()

out_node = nt.nodes.new("ShaderNodeOutputMaterial")
out_node.location = (1400, 0)

bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
bsdf.location = (1000, 0)
nt.links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])

# Coordenadas
tex_coord = nt.nodes.new("ShaderNodeTexCoord")
tex_coord.location = (-1000, 0)

mapping = nt.nodes.new("ShaderNodeMapping")
mapping.location = (-800, 0)
mapping.inputs["Scale"].default_value = (4.0, 4.0, 4.0)
nt.links.new(tex_coord.outputs["Object"], mapping.inputs["Vector"])

# 1. Voronoi F1 para destellos concentrados (chispas / puntos de energia)
voronoi = nt.nodes.new("ShaderNodeTexVoronoi")
voronoi.location = (-550, 200)
voronoi.feature = 'F1'
voronoi.distance = 'EUCLIDEAN'
voronoi.inputs["Scale"].default_value = 18.0
nt.links.new(mapping.outputs["Vector"], voronoi.inputs["Vector"])

# Invertir distancia de Voronoi para que los centros de las celulas sean picos (1.0 = destello brillante)
math_inv_voro = nt.nodes.new("ShaderNodeMath")
math_inv_voro.location = (-350, 200)
math_inv_voro.operation = 'SUBTRACT'
math_inv_voro.inputs[0].default_value = 1.0
nt.links.new(voronoi.outputs["Distance"], math_inv_voro.inputs[1])

# Elevar a potencia para hacer los destellos afilados y puntuales
math_pow = nt.nodes.new("ShaderNodeMath")
math_pow.location = (-150, 200)
math_pow.operation = 'POWER'
math_pow.inputs[1].default_value = 3.5
nt.links.new(math_inv_voro.outputs["Value"], math_pow.inputs[0])

# 2. Ruido organico para turbulencia y corrientes de fluido oscuro
noise_fluid = nt.nodes.new("ShaderNodeTexNoise")
noise_fluid.location = (-550, -200)
noise_fluid.inputs["Scale"].default_value = 5.2
noise_fluid.inputs["Detail"].default_value = 5.0
noise_fluid.inputs["Roughness"].default_value = 0.50
noise_fluid.inputs["Distortion"].default_value = 1.2 # Ondas vorticiales de fluido
nt.links.new(mapping.outputs["Vector"], noise_fluid.inputs["Vector"])

# 3. Micro-ruido para micro-destellos de purpurina / escamas cosmicas
noise_spark = nt.nodes.new("ShaderNodeTexNoise")
noise_spark.location = (-550, 0)
noise_spark.inputs["Scale"].default_value = 35.0
noise_spark.inputs["Detail"].default_value = 3.0
nt.links.new(mapping.outputs["Vector"], noise_spark.inputs["Vector"])

# Combinar destellos voronoi con micro-destellos
mix_sparks = nt.nodes.new("ShaderNodeMix")
mix_sparks.data_type = 'FLOAT'
mix_sparks.location = (50, 150)
mix_sparks.inputs["Factor"].default_value = 0.75
nt.links.new(math_pow.outputs["Value"], mix_sparks.inputs[2]) # A
nt.links.new(noise_spark.outputs["Fac"], mix_sparks.inputs[3]) # B

# Modular los destellos con las corrientes del fluido (solo aparecen en ciertas corrientes)
math_mod = nt.nodes.new("ShaderNodeMath")
math_mod.location = (250, 150)
math_mod.operation = 'MULTIPLY'
nt.links.new(mix_sparks.outputs["Result"], math_mod.inputs[0])
nt.links.new(noise_fluid.outputs["Fac"], math_mod.inputs[1])

# Color Ramp Base: Fluido 85% Negro Obsidiana con Destellos Purpura / Violeta Neon
cr_base = nt.nodes.new("ShaderNodeValToRGB")
cr_base.location = (450, 150)
cr_base.color_ramp.interpolation = 'EASE'
cr_base.color_ramp.elements[0].position = 0.55
cr_base.color_ramp.elements[0].color = (0.003, 0.003, 0.005, 1.0) # Fluido negro puro
cr_base.color_ramp.elements[1].position = 0.70
cr_base.color_ramp.elements[1].color = (0.16, 0.005, 0.38, 1.0)   # Fluido violeta profundo
e2 = cr_base.color_ramp.elements.new(0.82)
e2.color = (0.68, 0.02, 1.0, 1.0)                                  # Destello Morado Electrico
e3 = cr_base.color_ramp.elements.new(0.94)
e3.color = (0.95, 0.72, 1.0, 1.0)                                  # Centro blanco-lavanda incandescente
nt.links.new(math_mod.outputs["Value"], cr_base.inputs["Fac"])
nt.links.new(cr_base.outputs["Color"], bsdf.inputs["Base Color"])

# Color Ramp Emision: Solo los picos de los destellos emiten luz
cr_emit = nt.nodes.new("ShaderNodeValToRGB")
cr_emit.location = (450, -150)
cr_emit.color_ramp.interpolation = 'B_SPLINE'
cr_emit.color_ramp.elements[0].position = 0.74
cr_emit.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)       # Cero emision en el fluido base
cr_emit.color_ramp.elements[1].position = 0.92
cr_emit.color_ramp.elements[1].color = (0.78, 0.08, 1.0, 1.0)     # Destello morado brillante
nt.links.new(math_mod.outputs["Value"], cr_emit.inputs["Fac"])
nt.links.new(cr_emit.outputs["Color"], bsdf.inputs["Emission Color"])

# Fuerza de emision (destellos intensos)
math_emit_str = nt.nodes.new("ShaderNodeMath")
math_emit_str.location = (720, -150)
math_emit_str.operation = 'MULTIPLY'
math_emit_str.inputs[1].default_value = 8.5
nt.links.new(cr_emit.outputs["Color"], math_emit_str.inputs[0])
nt.links.new(math_emit_str.outputs["Value"], bsdf.inputs["Emission Strength"])

# Bump sutil de ondas de fluido
bump = nt.nodes.new("ShaderNodeBump")
bump.location = (720, 50)
bump.inputs["Strength"].default_value = 0.020
bump.inputs["Distance"].default_value = 0.015
nt.links.new(noise_fluid.outputs["Fac"], bump.inputs["Height"])
nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

# Parametros de fluido pulido con menisco
bsdf.inputs["Metallic"].default_value = 0.0
bsdf.inputs["Roughness"].default_value = 0.075
bsdf.inputs["IOR"].default_value = 1.54
if "Coat Weight" in bsdf.inputs:
    bsdf.inputs["Coat Weight"].default_value = 1.0
    bsdf.inputs["Coat Roughness"].default_value = 0.025
    if "Coat IOR" in bsdf.inputs:
        bsdf.inputs["Coat IOR"].default_value = 1.58

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
out_p = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2\scratch\test_darkfluid_refined_hero.png"
scene.render.filepath = out_p
bpy.ops.render.render(write_still=True)
print("TEST_DARKFLUID_REFINED_SAVED:", out_p)

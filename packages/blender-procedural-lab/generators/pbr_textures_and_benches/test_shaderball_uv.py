import bpy
import bmesh
import math
import os

PROJECT_ROOT = r"F:\Dev\Game"
TEXTURES_MODULAR = os.path.join(PROJECT_ROOT, "Art", "Textures", "Modular")
R = math.radians

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'

# Crear esfera nativa con UVs
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.58, segments=48, ring_count=24, location=(0, 0, 1.08))
obj = bpy.context.active_object
obj.name = "ShaderBall_Outer"

# Entrar en Edit Mode y borrar cuadrante frontal-derecho
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(obj.data)
verts_to_delete = [v for v in bm.verts if v.co.x > 0.08 and v.co.y < -0.08 and v.co.z > -0.18]
bmesh.ops.delete(bm, geom=verts_to_delete, context='VERTS')
bmesh.update_edit_mesh(obj.data)
bpy.ops.object.mode_set(mode='OBJECT')

# Solidify & Bevel
mod_sol = obj.modifiers.new("Solidify", 'SOLIDIFY')
mod_sol.thickness = 0.04
mod_sol.offset = -1.0
bpy.ops.object.shade_smooth()

# Núcleo interior
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.38, location=(0, 0, 1.08))
core = bpy.context.active_object
bpy.ops.object.shade_smooth()

# Material Outer
mat = bpy.data.materials.new(name="M_Test_Trim")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links
nodes.clear()
out = nodes.new('ShaderNodeOutputMaterial')
bsdf = nodes.new('ShaderNodeBsdfPrincipled')
links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])

tex = nodes.new('ShaderNodeTexImage')
tex.image = bpy.data.images.load(os.path.join(TEXTURES_MODULAR, "T_Trim_Industrial_BaseColor.png"))
links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
obj.data.materials.append(mat)

# Material Core Brass
mat_core = bpy.data.materials.new(name="M_Core")
mat_core.use_nodes = True
bsdf_c = mat_core.node_tree.nodes.get("Principled BSDF")
bsdf_c.inputs['Base Color'].default_value = (0.95, 0.75, 0.22, 1.0)
bsdf_c.inputs['Metallic'].default_value = 0.98
bsdf_c.inputs['Roughness'].default_value = 0.15
core.data.materials.append(mat_core)

# Luz y Cámara
bpy.ops.object.light_add(type='SUN', location=(5, -5, 8))
bpy.context.active_object.data.energy = 5.0
bpy.ops.object.camera_add(location=(0, -4.5, 1.25), rotation=(R(80), 0, 0))
scene.camera = bpy.context.active_object

out_path = r"F:\Dev\Game\Art\Renders\test_shaderball_uv_render.png"
scene.render.filepath = out_path
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
bpy.ops.render.render(write_still=True)
print("Rendered test to:", out_path)

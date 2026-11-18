import os
import sys
import math

try:
    import bpy
    from mathutils import Vector
except ImportError:
    print("Run inside Blender.")
    sys.exit(1)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0

# 1. World & Lighting
world = bpy.data.worlds.new("VRM_World")
world.use_nodes = True
bg_node = world.node_tree.nodes.get('Background')
if bg_node:
    bg_node.inputs['Color'].default_value = (0.12, 0.14, 0.18, 1.0)
    bg_node.inputs['Strength'].default_value = 0.8
scene.world = world

# 2. Import Seed-san VRM
vrm_path = r"E:\Darx_Proyect\Saved\Anime_Benchmark_Workspace\Seed-san.vrm"
bpy.ops.import_scene.gltf(filepath=vrm_path)

# Let's inspect imported meshes
meshes = [o for o in scene.objects if o.type == 'MESH']
print(f"Imported {len(meshes)} meshes: {[m.name for m in meshes]}")

# 3. Studio Lights
# Key light
l_key = bpy.data.objects.new("Key_Light", bpy.data.lights.new("Key_Light", 'AREA'))
l_key.data.energy = 45.0
l_key.data.size = 3.0
l_key.data.color = (1.0, 0.98, 0.96)
l_key.location = (1.5, -2.5, 2.0)
l_key.rotation_euler = (math.radians(55), 0, math.radians(30))
scene.collection.objects.link(l_key)

# Fill light
l_fill = bpy.data.objects.new("Fill_Light", bpy.data.lights.new("Fill_Light", 'AREA'))
l_fill.data.energy = 25.0
l_fill.data.size = 3.5
l_fill.data.color = (0.80, 0.90, 1.0)
l_fill.location = (-2.0, -2.0, 1.6)
l_fill.rotation_euler = (math.radians(45), 0, math.radians(-45))
scene.collection.objects.link(l_fill)

# Rim light
l_rim = bpy.data.objects.new("Rim_Light", bpy.data.lights.new("Rim_Light", 'SPOT'))
l_rim.data.energy = 90.0
l_rim.data.spot_size = math.radians(75)
l_rim.data.color = (0.85, 0.90, 1.0)
l_rim.location = (0.0, 2.5, 2.4)
l_rim.rotation_euler = (math.radians(-130), 0, math.radians(180))
scene.collection.objects.link(l_rim)

# 4. Render Settings
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.view_settings.view_transform = 'Standard'
scene.view_settings.look = 'Medium High Contrast'

output_dir = r"E:\Darx_Proyect\Saved\Anime_Benchmark_Workspace"

# Camera 1: Portrait / Face close-up
cam_portrait = bpy.data.objects.new("Cam_Portrait", bpy.data.cameras.new("Cam_Portrait"))
cam_portrait.data.lens = 70.0
cam_portrait.location = (0.0, -1.25, 1.40)
target_portrait = (0.0, 0.0, 1.35)
cam_portrait.rotation_euler = (Vector(target_portrait) - cam_portrait.location).to_track_quat('-Z', 'Y').to_euler()
scene.collection.objects.link(cam_portrait)

scene.camera = cam_portrait
scene.render.filepath = os.path.join(output_dir, "vrm_01_portrait.png")
bpy.ops.render.render(write_still=True)
print("Renderizado Portrait OK")

# Camera 2: Full Body 3/4 Action
cam_full = bpy.data.objects.new("Cam_Full", bpy.data.cameras.new("Cam_Full"))
cam_full.data.lens = 45.0
cam_full.location = (1.5, -2.8, 1.10)
target_full = (0.0, 0.0, 0.80)
cam_full.rotation_euler = (Vector(target_full) - cam_full.location).to_track_quat('-Z', 'Y').to_euler()
scene.collection.objects.link(cam_full)

scene.camera = cam_full
scene.render.filepath = os.path.join(output_dir, "vrm_02_fullbody.png")
bpy.ops.render.render(write_still=True)
print("Renderizado Full Body OK")

# 5. Inverted Hull Outline Material & Modifier
m_outline = bpy.data.materials.new(name="M_VRM_NPR_Outline")
m_outline.use_backface_culling = True
nodes_o = m_outline.node_tree.nodes
nodes_o.clear()
out_o = nodes_o.new('ShaderNodeOutputMaterial')
emit_o = nodes_o.new('ShaderNodeEmission')
emit_o.inputs['Color'].default_value = (0.05, 0.03, 0.08, 1.0)
emit_o.inputs['Strength'].default_value = 1.0
m_outline.node_tree.links.new(emit_o.outputs['Emission'], out_o.inputs['Surface'])

for m in meshes:
    if m.name in ['head', 'hair', 'hair_tail', 'wear', 'robo_arm']:
        m.data.materials.append(m_outline)
        mat_idx = len(m.data.materials) - 1
        mod = m.modifiers.new("InvertedHull", 'SOLIDIFY')
        mod.thickness = 0.0025
        mod.offset = 1.0
        mod.use_flip_normals = True
        mod.use_rim = True
        mod.material_offset = mat_idx
        mod.material_offset_rim = mat_idx
        mod.use_quality_normals = True

# Camera 3: Portrait with Inverted Hull Outline
scene.camera = cam_portrait
scene.render.filepath = os.path.join(output_dir, "vrm_03_outline_portrait.png")
bpy.ops.render.render(write_still=True)
print("Renderizado Outline Portrait OK")

# Camera 4: Full Body 3/4 with Inverted Hull Outline
scene.camera = cam_full
scene.render.filepath = os.path.join(output_dir, "vrm_04_outline_fullbody.png")
bpy.ops.render.render(write_still=True)
print("Renderizado Outline Full Body OK")

# Save blend file
blend_out = os.path.join(output_dir, "CH_Anime_VRM_Showcase.blend")
bpy.ops.wm.save_as_mainfile(filepath=blend_out)
print(f"Blend guardado en: {blend_out}")


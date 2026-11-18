import bpy
import bmesh
import math
import os

PROJECT_ROOT = r"F:\Dev\Game"
RENDERS_DIR = os.path.join(PROJECT_ROOT, "Art", "Renders")
ARTIFACT_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\b59ff04f-3c21-4ee5-94b0-8e8f899f8923"
BLEND_FILE = os.path.join(PROJECT_ROOT, "Art", "Blender", "Hardware_Tactico_5_Oficial.blend")

os.makedirs(RENDERS_DIR, exist_ok=True)
os.makedirs(ARTIFACT_DIR, exist_ok=True)

R = math.radians

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if not bpy.data.scenes:
        bpy.data.scenes.new("Scene")
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 2560
    scene.render.resolution_y = 1440
    
    world = bpy.data.worlds.new("World_Studio")
    scene.world = world
    world.use_nodes = True
    wnodes = world.node_tree.nodes
    wlinks = world.node_tree.links
    wnodes.clear()
    
    w_out = wnodes.new(type='ShaderNodeOutputWorld')
    w_bg = wnodes.new(type='ShaderNodeBackground')
    w_bg.inputs['Color'].default_value = (0.01, 0.01, 0.01, 1.0)
    w_bg.inputs['Strength'].default_value = 0.5
    wlinks.new(w_bg.outputs['Background'], w_out.inputs['Surface'])
    
    cam = bpy.data.cameras.new("Camera")
    cam_obj = bpy.data.objects.new("Camera", cam)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj
    cam_obj.location = (15, -15, 10)
    cam_obj.rotation_euler = (R(60), 0, R(45))
    
    light_data = bpy.data.lights.new(name="Light", type='SUN')
    light_data.energy = 5.0
    light_obj = bpy.data.objects.new(name="Light", object_data=light_data)
    scene.collection.objects.link(light_obj)
    light_obj.rotation_euler = (R(45), R(30), R(45))
    
    return scene

def create_box(name, size=(1,1,1)):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=size, verts=bm.verts)
    bm.to_mesh(mesh)
    bm.free()
    return obj

def create_cylinder(name, radius=0.5, depth=1.0):
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=32, radius1=radius, radius2=radius, depth=depth)
    bm.to_mesh(mesh)
    bm.free()
    return obj

def create_material(name, color, metallic, roughness):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs['Base Color'].default_value = color
        bsdf.inputs['Metallic'].default_value = metallic
        bsdf.inputs['Roughness'].default_value = roughness
    return mat

def generate_hardware():
    reset_scene()
    col = bpy.data.collections.new("HardwareTactico")
    bpy.context.scene.collection.children.link(col)
    
    mat_metal = create_material("Mat_Metal", (0.3, 0.3, 0.35, 1.0), 0.9, 0.3)
    mat_glass = create_material("Mat_Glass", (0.8, 0.9, 1.0, 0.5), 0.1, 0.1)
    
    # 1. Mesa Holográfica
    mesa = create_cylinder("HW_Mesa_Holografica", 1.2, 0.8)
    mesa.data.materials.append(mat_metal)
    mesa.location = (-6, 0, 0)
    col.objects.link(mesa)
    
    # 2. Cápsula Médica
    capsula = create_box("HW_Capsula_Medica", (1.0, 2.5, 1.0))
    capsula.data.materials.append(mat_glass)
    capsula.location = (-2, 0, 0)
    col.objects.link(capsula)
    
    # 3. Escáner Biométrico HUD
    escaner = create_box("HW_Escaner_Biometrico", (0.5, 0.5, 2.0))
    escaner.data.materials.append(mat_metal)
    escaner.location = (2, 0, 0)
    col.objects.link(escaner)
    
    # 4. Bridge Uplink Console
    console = create_box("HW_Bridge_Uplink_Console", (2.0, 1.0, 1.5))
    console.data.materials.append(mat_metal)
    console.location = (6, 0, 0)
    col.objects.link(console)
    
    # 5. Airlock Decompression Chamber
    airlock = create_cylinder("HW_Airlock_Decompression_Chamber", 2.0, 3.0)
    airlock.rotation_euler = (R(90), 0, 0)
    airlock.data.materials.append(mat_metal)
    airlock.location = (12, 0, 0)
    col.objects.link(airlock)

    bpy.context.scene.render.filepath = os.path.join(RENDERS_DIR, "Showcase_Hardware_Tactico_5_Master.png")
    bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_FILE)

if __name__ == "__main__":
    generate_hardware()

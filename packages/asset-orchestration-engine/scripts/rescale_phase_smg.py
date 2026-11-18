import bpy
import bmesh
import os
import math
from mathutils import Vector, Matrix

FBX_IN = r"E:\Darx_Proyect\Art\FBX\Weapons\SM_Wep_PhaseSMG.fbx"
FBX_OUT = r"E:\Darx_Proyect\Art\FBX\Weapons\SM_Wep_PhaseSMG.fbx"
RENDER_OUT = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2\preview_phase_smg_rescaled.png"

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=FBX_IN)

mesh_objs = [o for o in bpy.data.objects if o.type == 'MESH']
if not mesh_objs:
    raise RuntimeError("No se encontró malla en " + FBX_IN)

main_mesh = mesh_objs[0]
print(f"Dimensiones iniciales: {[round(x*100, 2) for x in main_mesh.dimensions]} cm")

# Factor de escala para reducir de 87.1 cm a 50.5 cm
FACTOR = 50.5 / 87.1  # ~0.579793
SCALE_MAT = Matrix.Diagonal((FACTOR, FACTOR, FACTOR, 1.0))

# Aplicar escala directamente a la geometría manteniendo pivote en (0,0,0)
main_mesh.data.transform(SCALE_MAT)
main_mesh.data.update()

# Validar dimensiones finales
dims_cm = [round(x * 100, 2) for x in main_mesh.dimensions]
coords = [v.co for v in main_mesh.data.vertices]
min_c = [round(min(c[i] for c in coords)*100, 2) for i in range(3)]
max_c = [round(max(c[i] for c in coords)*100, 2) for i in range(3)]

print(f"Dimensiones reescaladas: {dims_cm} cm")
print(f"Límites locales (cm): Min={min_c}, Max={max_c}")

# Exportar FBX reescalado limpio
for o in bpy.data.objects:
    o.select_set(False)
main_mesh.select_set(True)
bpy.context.view_layer.objects.active = main_mesh

bpy.ops.export_scene.fbx(
    filepath=FBX_OUT,
    use_selection=True,
    global_scale=1.0,
    apply_scale_options='FBX_SCALE_NONE',
    axis_forward='-Y',
    axis_up='Z',
    bake_space_transform=False,
    object_types={'MESH'},
    use_mesh_modifiers=True,
    mesh_smooth_type='FACE',
    add_leaf_bones=False,
    bake_anim=False
)
print(f"[OK] Exportado FBX reescalado a {FBX_OUT}")

# Configurar entorno de render de 4 vistas (Perspectiva 3/4)
world = bpy.data.worlds.new("W_Render")
bpy.context.scene.world = world
world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.04, 0.05, 0.07, 1.0)
world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.8

# Luces de estudio
def add_sun(name, energy, rot, color=(1,1,1)):
    l_data = bpy.data.lights.new(name, 'SUN')
    l_data.energy = energy
    l_data.color = color
    l_obj = bpy.data.objects.new(name, l_data)
    l_obj.rotation_euler = rot
    bpy.context.scene.collection.objects.link(l_obj)

add_sun("Key", 4.0, (math.radians(45), math.radians(15), math.radians(-45)), (1.0, 0.98, 0.95))
add_sun("Fill", 2.0, (math.radians(50), math.radians(-20), math.radians(135)), (0.7, 0.85, 1.0))
add_sun("Rim", 5.0, (math.radians(-45), math.radians(20), math.radians(45)), (0.8, 0.2, 1.0))

cam_data = bpy.data.cameras.new("Cam")
cam_obj = bpy.data.objects.new("Cam", cam_data)
bpy.context.scene.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj

# Vista de 3/4 hacia el arma
cam_obj.location = (0.45, -0.65, 0.35)
cam_obj.rotation_euler = (math.radians(65), 0, math.radians(35))

bpy.context.scene.render.filepath = RENDER_OUT
bpy.context.scene.render.resolution_x = 768
bpy.context.scene.render.resolution_y = 768
bpy.ops.render.render(write_still=True)
print(f"[OK] Render guardado en {RENDER_OUT}")

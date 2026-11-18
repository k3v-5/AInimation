"""calibrate_fps_attachment.py
Verifica la posicion visual del arma y los brazos con parent directo al hueso.
"""
import bpy
import os
import shutil
from mathutils import Vector, Euler, Matrix

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

bpy.ops.import_scene.fbx(filepath=r"E:\Darx_Proyect\Art\FBX\SK_FPS_Arms.fbx")
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
fps_mesh = [o for o in bpy.data.objects if o.type == 'MESH'][0]

# Ocultar pistola vieja
for v in fps_mesh.data.vertices:
    for g in v.groups:
        if fps_mesh.vertex_groups[g.group].name in ('weapon', 'cell'):
            v.co = Vector((0, 0, -100))
            break

# Cargar SMG
with bpy.data.libraries.load(r"E:\Darx_Proyect\Art\Blender\SM_Wep_PhaseSMG_Workspace.blend", link=False) as (data_from, data_to):
    data_to.objects = [n for n in data_from.objects if n not in ("StudioTable", "Cam", "KeyLight", "FillLight", "RimLight", "Light_ReactorSMG")]

smg_objs = [o for o in data_to.objects if o is not None]
for o in smg_objs:
    scene.collection.objects.link(o)

bpy.ops.object.select_all(action='DESELECT')
for o in smg_objs:
    o.select_set(True)
bpy.context.view_layer.objects.active = smg_objs[0]
bpy.ops.object.join()
smg = bpy.context.active_object
smg.name = "SMG"

# Parenting a hueso weapon
smg.parent = arm
smg.parent_type = 'BONE'
smg.parent_bone = 'weapon'

# Ajuste local en el hueso weapon
# En el hueso weapon de SK_FPS_Arms:
# Queremos que la empuñadura trasera esté en la mano derecha.
# Probemos loc=(0,0,0)
smg.location = (0, 0, 0)
smg.rotation_euler = (0, 0, 0)

# Luz
l_data = bpy.data.lights.new("Key", 'SUN')
l_data.energy = 5.0
l = bpy.data.objects.new("Key", l_data)
l.rotation_euler = (0.7, 0.2, 0.5)
scene.collection.objects.link(l)

# Camara subjetiva FPS (a la altura de los ojos, detrás del arma)
cam_data = bpy.data.cameras.new("CamFPS")
cam_data.lens = 32
cam = bpy.data.objects.new("CamFPS", cam_data)
# Los brazos FPS tienen root=(0,0,0), clavicles at Y=+0.15, Z=-0.51.
# Ojos estarían en (0, 0.15, 0.0)
cam.location = (0.0, 0.05, 0.02)
cam.rotation_euler = (1.5708, 0, 3.14159) # Mirando hacia -Y
scene.collection.objects.link(cam)
scene.camera = cam

scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 960
scene.render.resolution_y = 540
out_img = r"E:\Darx_Proyect\Art\Blender\test_fps_parent.png"
scene.render.filepath = out_img
bpy.ops.render.render(write_still=True)
shutil.copyfile(out_img, r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2\test_fps_parent.png")
print("Rendered test_fps_parent.png")

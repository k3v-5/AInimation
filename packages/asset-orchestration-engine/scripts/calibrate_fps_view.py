"""calibrate_fps_view.py
Calibra la vista FPS perfecta:
1. SMG parented a hueso weapon con rot=(0,0,0) y loc calibrado.
2. Brazo derecho sosteniendo la empuñadura trasera y gatillo.
3. Brazo izquierdo sosteniendo firmemente la empuñadura delantera vertical.
4. Cámara en perspectiva de ojos (FOV amplio para ver arma y brazos).
"""
import bpy
import math
import shutil
from mathutils import Vector, Euler

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# 1. Importar SK_FPS_Arms
bpy.ops.import_scene.fbx(filepath=r"E:\Darx_Proyect\Art\FBX\SK_FPS_Arms.fbx")
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
fps_mesh = [o for o in bpy.data.objects if o.type == 'MESH'][0]

# Ocultar pistola vieja
for v in fps_mesh.data.vertices:
    for g in v.groups:
        if fps_mesh.vertex_groups[g.group].name in ('weapon', 'cell'):
            v.co = Vector((0, 0, -100))
            break

# 2. Cargar SMG
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

# Parenting directo al hueso weapon
smg.parent = arm
smg.parent_type = 'BONE'
smg.parent_bone = 'weapon'
# Empuñadura trasera en el hueso weapon:
smg.location = (0.0, 0.03, 0.02)
smg.rotation_euler = (0, 0, 0)

for pb in arm.pose.bones:
    pb.rotation_mode = 'XYZ'

# En SK_FPS_Arms:
# bone weapon en rest pose ya está en la mano derecha (hand_R).
# Si el arma está ligeramente a la derecha en posición de tiro táctica (Hipfire/Walk):
pb_uR = arm.pose.bones['upperarm_R']
pb_fR = arm.pose.bones['forearm_R']
pb_hR = arm.pose.bones['hand_R']
pb_wep = arm.pose.bones['weapon']

# Rotación natural del brazo derecho sosteniendo el arma a la altura del pecho/cadera táctica
pb_uR.rotation_euler = (math.radians(-6), math.radians(4), math.radians(-2))
pb_fR.rotation_euler = (math.radians(-10), math.radians(2), math.radians(0))
pb_wep.rotation_euler = (math.radians(-4), math.radians(4), math.radians(-2))

# Brazo izquierdo alcanzando la empuñadura delantera vertical
# En SK_FPS_Arms, el foregrip queda aproximadamente en:
# X ~ 0.09, Y ~ -0.42, Z ~ -0.12 en mundo
pb_uL = arm.pose.bones['upperarm_L']
pb_fL = arm.pose.bones['forearm_L']
pb_hL = arm.pose.bones['hand_L']

pb_uL.rotation_euler = (math.radians(26), math.radians(-12), math.radians(22))
pb_fL.rotation_euler = (math.radians(-58), math.radians(18), math.radians(-12))
pb_hL.rotation_euler = (math.radians(15), math.radians(-10), math.radians(30))
pb_hL.location = Vector((0.02, -0.06, 0.03))

bpy.context.view_layer.update()

# Iluminación de estudio
l1 = bpy.data.objects.new("Key", bpy.data.lights.new("Key", 'SUN'))
l1.data.energy = 4.0
l1.rotation_euler = (0.7, 0.3, -2.4)
scene.collection.objects.link(l1)

l2 = bpy.data.objects.new("Fill", bpy.data.lights.new("Fill", 'AREA'))
l2.data.energy = 450.0
l2.data.size = 2.0
l2.location = (-0.6, -0.2, 0.4)
scene.collection.objects.link(l2)

l3 = bpy.data.objects.new("Rim", bpy.data.lights.new("Rim", 'AREA'))
l3.data.energy = 350.0
l3.data.size = 2.0
l3.data.color = (0.75, 0.2, 1.0)
l3.location = (0.6, -0.3, 0.2)
scene.collection.objects.link(l3)

# Cámara FPS
# Para ver las manos sosteniendo el arma desde la perspectiva en primera persona:
cam_data = bpy.data.cameras.new("CamFPS")
cam_data.lens = 24 # 24mm amplio típico de juegos FPS (permite ver manos y arma sin distorsión extrema)
cam = bpy.data.objects.new("CamFPS", cam_data)
# Posición de ojos del jugador
cam.location = (0.0, 0.15, 0.02)
# Mirando hacia el frente (-Y) y ligeramente abajo hacia el arma
cam.rotation_euler = (math.radians(82), 0, math.radians(180))
scene.collection.objects.link(cam)
scene.camera = cam

scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 960
scene.render.resolution_y = 540
out_img = r"E:\Darx_Proyect\Art\Blender\test_fps_calibrated.png"
scene.render.filepath = out_img
bpy.ops.render.render(write_still=True)
shutil.copyfile(out_img, r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2\test_fps_calibrated.png")
print("Rendered test_fps_calibrated.png")

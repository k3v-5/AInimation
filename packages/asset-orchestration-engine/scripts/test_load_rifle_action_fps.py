"""test_load_rifle_action_fps.py
Aplica la acción canónica de rifle a SK_FPS_Arms y verifica la posición de las dos manos.
"""
import os
import math
import bpy
from mathutils import Vector, Matrix

PROJECT_ROOT = r"E:\Darx_Proyect"
ART_DIR = os.path.join(PROJECT_ROOT, "Art")
BLENDER_DIR = os.path.join(ART_DIR, "Blender")
SMG_BLEND = os.path.join(BLENDER_DIR, "SM_Wep_PhaseSMG_Workspace.blend")
FPS_FBX = os.path.join(ART_DIR, "FBX", "SK_FPS_Arms.fbx")
RIFLE_WALK = os.path.join(ART_DIR, "FBX", "Anim_FPS", "A_FPS_Rifle_Walk.fbx")

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# 1. Cargar brazos FPS
bpy.ops.import_scene.fbx(filepath=FPS_FBX)
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
fps_mesh = [o for o in bpy.data.objects if o.type == 'MESH'][0]

# Ocultar pistola vieja
for v in fps_mesh.data.vertices:
    for g in v.groups:
        if fps_mesh.vertex_groups[g.group].name in ('weapon', 'cell'):
            v.co = Vector((0, 0, -100))
            break

# 2. Cargar acción de Rifle_Walk
bpy.ops.import_scene.fbx(filepath=RIFLE_WALK)
# El importador de FBX crea un nuevo armature o añade la acción
imported_arms = [o for o in bpy.data.objects if o.type == 'ARMATURE' and o != arm]
if imported_arms:
    rifle_arm = imported_arms[0]
    rifle_act = rifle_arm.animation_data.action
    print(f"Rifle Action cargada: {rifle_act.name}")
    if arm.animation_data is None:
        arm.animation_data_create()
    arm.animation_data.action = rifle_act
    bpy.data.objects.remove(rifle_arm, do_unlink=True)

# 3. Cargar SMG
with bpy.data.libraries.load(SMG_BLEND, link=False) as (data_from, data_to):
    data_to.objects = [n for n in data_from.objects if n not in ("StudioTable", "Cam", "KeyLight", "FillLight", "RimLight", "Light_ReactorSMG")]
smg_objs = [o for o in data_to.objects if o is not None]
for o in smg_objs:
    scene.collection.objects.link(o)

bpy.ops.object.select_all(action='DESELECT')
for o in smg_objs:
    o.select_set(True)
bpy.context.view_layer.objects.active = smg_objs[0]
bpy.ops.object.join()
smg_mesh = bpy.context.active_object

smg_mesh.parent = arm
smg_mesh.parent_type = 'BONE'
smg_mesh.parent_bone = 'weapon'
# Ubicación relativa en el hueso weapon
smg_mesh.location = (0, 0, 0)
smg_mesh.rotation_euler = (0, 0, 0)

scene.frame_set(1)
bpy.context.view_layer.update()

# Imprimir coordenadas de hand_R, hand_L y weapon
for bname in ['hand_R', 'hand_L', 'weapon']:
    pb = arm.pose.bones[bname]
    loc = (arm.matrix_world @ pb.matrix).to_translation()
    print(f"Bone {bname:10s} WorldLoc: ({loc.x:.3f}, {loc.y:.3f}, {loc.z:.3f})")

# Renderizar prueba con cámara mirando hacia donde apuntan los brazos
cam_data = bpy.data.cameras.new("Cam")
cam_data.lens = 24
cam_obj = bpy.data.objects.new("Cam", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj

# En A_FPS_Rifle_Walk, los brazos están en Y ~ 0.1 a 0.2, Z ~ -0.3.
# La cámara en FPS típica está en el origen o cerca:
cam_obj.location = (0.0, -0.3, -0.2)
cam_obj.rotation_euler = (math.radians(90), 0, 0)

l1 = bpy.data.objects.new("Key", bpy.data.lights.new("Key", 'SUN'))
l1.data.energy = 4.0
l1.rotation_euler = (math.radians(45), math.radians(15), math.radians(-30))
scene.collection.objects.link(l1)

scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 960
scene.render.resolution_y = 540
out_test = os.path.join(ART_DIR, "Blender", "test_rifle_fps.png")
scene.render.filepath = out_test
bpy.ops.render.render(write_still=True)
print(f"Render guardado: {out_test}")

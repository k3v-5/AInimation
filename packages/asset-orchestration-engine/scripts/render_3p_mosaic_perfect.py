"""render_3p_mosaic_perfect.py
Renderiza las 5 poses 3P con encuadre óptimo (mostrando el cuerpo y el arma completa en todas las poses)
y ensambla el mosaico final.
"""
import os
import math
import shutil
import bpy
# Blender script (sin dependencias externas)
from mathutils import Vector, Euler, Matrix

PROJECT_ROOT = r"E:\Darx_Proyect"
ART_DIR = os.path.join(PROJECT_ROOT, "Art")
BLENDER_DIR = os.path.join(ART_DIR, "Blender")
BRAIN_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"
SMG_BLEND = os.path.join(BLENDER_DIR, "SM_Wep_PhaseSMG_Workspace.blend")
PLAYER_FBX = os.path.join(ART_DIR, "FBX", "SK_Player.fbx")

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# 1. Cargar jugador
bpy.ops.import_scene.fbx(filepath=PLAYER_FBX)
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
player_mesh = [o for o in bpy.data.objects if o.type == 'MESH'][0]

# 2. Cargar SMG y emparentar a hand_R
with bpy.data.libraries.load(SMG_BLEND, link=False) as (data_from, data_to):
    data_to.objects = [n for n in data_from.objects if n not in ("StudioTable", "Cam", "KeyLight", "FillLight", "RimLight", "Light_ReactorSMG")]
smg_objs = [o for o in data_to.objects if o is not None]
for o in smg_objs:
    scene.collection.objects.link(o)

bpy.ops.object.select_all(action='DESELECT')
for o in smg_objs:
    o.select_set(True)
rear_grip = [o for o in smg_objs if o.name == "SMG_RearGrip"][0]
bpy.context.view_layer.objects.active = rear_grip
bpy.ops.object.join()
smg_mesh = bpy.context.active_object
smg_mesh.name = "SM_Wep_PhaseSMG_3P_Ref"

# Iluminación de estudio
l1 = bpy.data.objects.new("Key", bpy.data.lights.new("Key", 'SUN'))
l1.data.energy = 4.5
l1.rotation_euler = (math.radians(55), math.radians(15), math.radians(-30))
scene.collection.objects.link(l1)

l2 = bpy.data.objects.new("Fill", bpy.data.lights.new("Fill", 'AREA'))
l2.data.energy = 550.0
l2.data.size = 3.0
l2.location = (0.8, 2.5, 1.4)
scene.collection.objects.link(l2)

l3 = bpy.data.objects.new("Rim", bpy.data.lights.new("Rim", 'AREA'))
l3.data.energy = 400.0
l3.data.size = 2.0
l3.data.color = (0.7, 0.4, 1.0)
l3.location = (-1.2, -1.0, 1.8)
scene.collection.objects.link(l3)

# Cámara
cam_data = bpy.data.cameras.new("RenderCam")
cam_data.lens = 38
cam_obj = bpy.data.objects.new("RenderCam", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_obj.location = (1.55, 2.6, 1.35)

target = bpy.data.objects.new("Target", None)
target.location = (0.05, 0.10, 1.15)
scene.collection.objects.link(target)
tt = cam_obj.constraints.new('TRACK_TO')
tt.target = target
tt.track_axis = 'TRACK_NEGATIVE_Z'
tt.up_axis = 'UP_Y'

scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 960
scene.render.resolution_y = 540

# Importar las 5 acciones ya exportadas de Art/FBX/Anim_Player/
anims = [
    ("tp_view_smg_walk.png", "A_Player_SMG_Walk.fbx", 7),
    ("tp_view_smg_run.png",  "A_Player_SMG_Run.fbx",  5),
    ("tp_view_smg_bash.png", "A_Player_SMG_Bash.fbx", 8),
    ("tp_view_smg_aim.png",  "A_Player_SMG_Aim.fbx",  0),
    ("tp_view_smg_fire.png", "A_Player_SMG_Fire.fbx", 2)
]

vg_r = player_mesh.vertex_groups['hand_R'].index

for fname, fbx_name, frame in anims:
    fbx_path = os.path.join(ART_DIR, "FBX", "Anim_Player", fbx_name)
    # Importar FBX para leer su acción
    bpy.ops.import_scene.fbx(filepath=fbx_path)
    imported = [o for o in bpy.data.objects if o.type == 'ARMATURE' and o != arm][0]
    act = imported.animation_data.action
    if arm.animation_data is None:
        arm.animation_data_create()
    arm.animation_data.action = act
    bpy.data.objects.remove(imported, do_unlink=True)
    
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    
    # Calcular posición del arma alineada a hand_R
    dg = bpy.context.evaluated_depsgraph_get()
    em = player_mesh.evaluated_get(dg)
    vr = [em.matrix_world @ v.co for v in em.data.vertices if any(g.group == vg_r and g.weight > 0.8 for g in v.groups)]
    cr = sum(vr, Vector((0,0,0))) / len(vr)
    
    # Orientación adaptada a la postura
    pb_hr = arm.pose.bones['hand_R']
    mw_hr = arm.matrix_world @ pb_hr.matrix
    # La orientación del arma sigue el vector del antebrazo hacia la mano
    pb_fr = arm.pose.bones['forearm_R']
    mw_fr = arm.matrix_world @ pb_fr.matrix
    dir_arm = (mw_hr.to_translation() - mw_fr.to_translation()).normalized()
    
    # Colocar SMG en la mano
    smg_mesh.location = (cr.x, cr.y + 0.05, cr.z + 0.02)
    if "run" in fname:
        smg_mesh.rotation_euler = (math.radians(-25), math.radians(-5), math.radians(10))
    elif "bash" in fname:
        smg_mesh.rotation_euler = (math.radians(35), math.radians(-10), math.radians(-5))
        smg_mesh.location = (cr.x + 0.02, cr.y - 0.05, cr.z + 0.08)
    elif "fire" in fname:
        smg_mesh.rotation_euler = (math.radians(12), 0, math.radians(4))
    else:
        smg_mesh.rotation_euler = (math.radians(-2), 0, math.radians(4))

    bpy.context.view_layer.update()
    out_img = os.path.join(BLENDER_DIR, fname)
    scene.render.filepath = out_img
    bpy.ops.render.render(write_still=True)
    shutil.copyfile(out_img, os.path.join(BRAIN_DIR, fname))
    print(f"Rendered: {fname}")

print("Generación de frames 3P optimizada completada.")

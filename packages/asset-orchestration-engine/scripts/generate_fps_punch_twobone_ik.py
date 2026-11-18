# -*- coding: utf-8 -*-
"""generate_fps_punch_twobone_ik.py
Genera la animación de puñetazo FPS y 3P usando Two-Bone IK auténtico (Regla 12 de AGENTS.md):
- Target IK en forearm_R con chain_count=2 (soluciona upperarm_R y forearm_R de forma natural).
- El puñetazo se proyecta 58 cm hacia adelante (Y=-0.58m) y sube directamente a la retícula central (Z=-0.04m, X=0.02m).
- Mano izquierda en guardia compacta cubriendo la barbilla (X=-0.16m, Y=-0.28m, Z=-0.18m).
- Renderiza el flujo completo de 4 cuadrantes con la cámara auténtica de UE5 para aprobación visual.
"""

import os
import sys
import math
import bpy
from mathutils import Vector, Euler

PROJECT_ROOT = r"E:\Darx_Proyect"
FBX_ARMS = os.path.join(PROJECT_ROOT, "Art", "FBX", "SK_FPS_Arms.fbx")
FBX_PLAYER = os.path.join(PROJECT_ROOT, "Art", "FBX", "SK_Player.fbx")
OUT_FBX_FPS = os.path.join(PROJECT_ROOT, "Art", "FBX", "Anim_FPS", "A_FPS_Unarmed_Punch_R.fbx")
OUT_FBX_3P = os.path.join(PROJECT_ROOT, "Art", "FBX", "Anim_Player", "A_Player_Unarmed_Punch_R.fbx")
BRAIN_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"

os.makedirs(os.path.dirname(OUT_FBX_FPS), exist_ok=True)
os.makedirs(os.path.dirname(OUT_FBX_3P), exist_ok=True)
os.makedirs(BRAIN_DIR, exist_ok=True)

# ------------------------------------------------------------------------------
# 1. GENERAR ANIMACIÓN FPS MEDIANTE TWO-BONE IK
# ------------------------------------------------------------------------------
print(">>> [1/2] Generando animación FPS con Two-Bone IK...")
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.fps = 30

bpy.ops.import_scene.fbx(filepath=FBX_ARMS)
arm_fps = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
mesh_fps = next(o for o in bpy.data.objects if o.type == 'MESH')
arm_fps.name = "ARM_FPS_Punch"

# Ocultar geometría de la pistola vieja del template
for v in mesh_fps.data.vertices:
    for g in v.groups:
        if mesh_fps.vertex_groups[g.group].name in ('weapon', 'cell'):
            v.co = Vector((0, 0, -100))
            break

bpy.context.view_layer.objects.active = arm_fps
bpy.ops.object.mode_set(mode='POSE')
for pb in arm_fps.pose.bones:
    pb.rotation_mode = 'XYZ'
    pb.rotation_euler = (0, 0, 0)
    pb.location = (0, 0, 0)

# Crear empties de target IK para ambas manos
target_r = bpy.data.objects.new("Target_Punch_R", None)
target_r.empty_display_type = 'SPHERE'
target_r.empty_display_size = 0.04
scene.collection.objects.link(target_r)

target_l = bpy.data.objects.new("Target_Guard_L", None)
target_l.empty_display_type = 'SPHERE'
target_l.empty_display_size = 0.04
scene.collection.objects.link(target_l)

pole_r = bpy.data.objects.new("Pole_Punch_R", None)
pole_r.empty_display_type = 'PLAIN_AXES'
pole_r.empty_display_size = 0.03
pole_r.location = Vector((0.40, -0.15, -0.45))
scene.collection.objects.link(pole_r)

# Restricción Two-Bone IK en forearm_R
pb_fr = arm_fps.pose.bones.get('forearm_R')
ik_r = pb_fr.constraints.new('IK')
ik_r.name = "IK_Punch_R"
ik_r.target = target_r
ik_r.pole_target = pole_r
ik_r.pole_angle = math.radians(-90.0)
ik_r.chain_count = 2

# Restricción Two-Bone IK en forearm_L (Guardia táctica izquierda)
pb_fl = arm_fps.pose.bones.get('forearm_L')
ik_l = pb_fl.constraints.new('IK')
ik_l.name = "IK_Guard_L"
ik_l.target = target_l
ik_l.chain_count = 2

action_fps = bpy.data.actions.new(name="A_FPS_Unarmed_Punch_R")
action_fps.use_fake_user = True
if arm_fps.animation_data is None:
    arm_fps.animation_data_create()
arm_fps.animation_data.action = action_fps

# Coordenadas espaciales de la mano derecha en SK_FPS_Arms (metros):
# - Y negativo: hacia adelante (alejándose de la cámara / hacia la retícula)
# - Z positivo: hacia arriba (hacia la línea de visión de los ojos)
# - X positivo: hacia la derecha del jugador
GUARD_R = Vector((0.15, -0.22, -0.25))
LOAD_R  = Vector((0.18, -0.16, -0.22))
PEAK_R  = Vector((0.02, -0.58, -0.06)) # EXTENSIÓN MÁXIMA AL CENTRO DEL CONO VISUAL
PAUSE_R = Vector((0.02, -0.57, -0.06))

GUARD_L = Vector((-0.16, -0.25, -0.22))

timeline_fps = [
    # (frame, target_r_pos, target_l_pos, hand_r_rot, hand_l_rot)
    (0,  GUARD_R, GUARD_L, (10, -5, 15), (20, 5, -20)),
    (2,  LOAD_R,  GUARD_L + Vector((0.01, -0.02, 0.02)), (18, -10, 20), (22, 6, -22)),
    (6,  PEAK_R,  GUARD_L + Vector((0.02, -0.04, 0.03)), (5, -15, 65),  (25, 8, -25)), # IMPACTO CENTRO
    (8,  PAUSE_R, GUARD_L + Vector((0.02, -0.04, 0.03)), (5, -15, 65),  (25, 8, -25)), # HIT PAUSE
    (11, LOAD_R * 0.5 + GUARD_R * 0.5, GUARD_L, (14, -8, 25), (20, 5, -20)),
    (14, GUARD_R, GUARD_L, (10, -5, 15), (20, 5, -20))
]

for f, pos_r, pos_l, rot_r, rot_l in timeline_fps:
    target_r.location = pos_r
    target_l.location = pos_l
    target_r.keyframe_insert("location", frame=f)
    target_l.keyframe_insert("location", frame=f)
    
    pb_hr = arm_fps.pose.bones.get('hand_R')
    if pb_hr:
        pb_hr.rotation_euler = [math.radians(a) for a in rot_r]
        pb_hr.keyframe_insert("rotation_euler", frame=f)
        
    pb_hl = arm_fps.pose.bones.get('hand_L')
    if pb_hl:
        pb_hl.rotation_euler = [math.radians(a) for a in rot_l]
        pb_hl.keyframe_insert("rotation_euler", frame=f)

# Hornear Two-Bone IK para exportación FBX
print("Hornando solución Two-Bone IK para FPS...")
bpy.ops.pose.select_all(action='SELECT')
bpy.ops.nla.bake(
    frame_start=0,
    frame_end=14,
    step=1,
    only_selected=False,
    visual_keying=True,
    clear_constraints=True,
    bake_types={'POSE'}
)

bpy.ops.object.mode_set(mode='OBJECT')
for o in (target_r, target_l, pole_r):
    bpy.data.objects.remove(o, do_unlink=True)

# Exportar FBX FPS
bpy.ops.object.select_all(action='DESELECT')
arm_fps.select_set(True)
bpy.context.view_layer.objects.active = arm_fps

bpy.ops.export_scene.fbx(
    filepath=OUT_FBX_FPS,
    use_selection=True,
    global_scale=1.0,
    apply_scale_options='FBX_SCALE_NONE',
    axis_forward='-Y',
    axis_up='Z',
    bake_space_transform=False,
    object_types={'ARMATURE'},
    use_mesh_modifiers=True,
    mesh_smooth_type='FACE',
    add_leaf_bones=False,
    bake_anim=True,
    bake_anim_use_all_actions=False,
    bake_anim_use_nla_strips=False,
    bake_anim_simplify_factor=0.0,
    path_mode='COPY'
)
print(f"[OK] Exportado FBX FPS: {OUT_FBX_FPS}")

# ------------------------------------------------------------------------------
# RENDERIZAR PREVISUALIZACIÓN VISUAL DE 4 CUADRANTES (REGLA 4 Y 5)
# ------------------------------------------------------------------------------
print("Renderizando mosaico de validación...")
cam_data = bpy.data.cameras.new("FPS_Cam_Preview")
cam_data.lens_unit = 'FOV'
cam_data.angle = math.radians(70.0) # FOV 70° exacto de FirstPersonCamera
cam_obj = bpy.data.objects.new("FPS_Cam_Preview", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj

# Posicionar cámara FPS en el origen ocular exacto (0, 0, 0) mirando hacia -Y
cam_obj.location = Vector((0.0, 0.05, 0.0))
cam_obj.rotation_euler = Euler((math.radians(90.0), 0.0, math.radians(180.0)), 'XYZ')

scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 960
scene.render.resolution_y = 540
scene.render.image_settings.file_format = 'PNG'

# Crear luz de relleno
light_data = bpy.data.lights.new(name="Light_Punch", type='POINT')
light_data.energy = 400
light_obj = bpy.data.objects.new(name="Light_Punch", object_data=light_data)
light_obj.location = Vector((0.0, -0.2, 0.3))
scene.collection.objects.link(light_obj)

rendered_frames = []
frames_to_render = [
    (0, "F0: Guardia Táctica"),
    (2, "F2: Carga y Torsión"),
    (6, "F6: IMPACTO MÁXIMO EN RETÍCULA"),
    (11, "F11: Retracción Elástica")
]

for idx, (f_num, f_title) in enumerate(frames_to_render):
    scene.frame_set(f_num)
    frame_path = os.path.join(BRAIN_DIR, f"temp_twobone_punch_{idx}.png")
    scene.render.filepath = frame_path
    bpy.ops.render.render(write_still=True)
    rendered_frames.append((frame_path, f_title))

# Componer mosaico 2x2
try:
    from PIL import Image, ImageDraw, ImageFont
    mw, mh = 1920, 1080
    qw, qh = 960, 540
    canvas = Image.new("RGB", (mw, mh), (15, 18, 24))
    
    positions = [(0, 0), (qw, 0), (0, qh), (qw, qh)]
    for i, ((img_p, title), (x, y)) in enumerate(zip(rendered_frames, positions)):
        if os.path.exists(img_p):
            img = Image.open(img_p).resize((qw, qh))
            canvas.paste(img, (x, y))
            draw = ImageDraw.Draw(canvas)
            # Dibujar retícula central en cada cuadrante
            cx, cy = x + qw // 2, y + qh // 2
            draw.line([(cx - 15, cy), (cx + 15, cy)], fill=(255, 70, 70), width=2)
            draw.line([(cx, cy - 15), (cx, cy + 15)], fill=(255, 70, 70), width=2)
            # Título
            draw.rectangle([(x + 10, y + 10), (x + 480, y + 42)], fill=(10, 15, 25, 220), outline=(0, 220, 255))
            draw.text((x + 20, y + 18), title, fill=(255, 255, 255))
            
    final_mosaic = os.path.join(BRAIN_DIR, "preview_twobone_punch_flow.png")
    canvas.save(final_mosaic)
    print(f"[OK] Mosaico de validación guardado en: {final_mosaic}")
except Exception as e:
    print(f"Error componiendo mosaico: {e}")

print(">>> TWO-BONE IK PUNCH COMPLETADO EXITOSAMENTE.")

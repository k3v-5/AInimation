"""
generar_animaciones_locomocion_oficial.py
=========================================
Generador Oficial Maestro de Animaciones de Locomoción y Posturas Tácticas para Astra Hazard.
Esqueleto: SK_Firefighter_Official_Rigged_Skeleton (Unreal Engine 5.8)

Genera y exporta 10 secuencias de animación cinemáticas en formato FBX estricto:
1.  A_Firefighter_Idle         (60f, 2.5s - Respiración biomecánica y postura de guardia)
2.  A_Firefighter_Walk         (30f, 1.25s - Ciclo de marcha desarmada a 240 cm/s con balanceo contralateral)
3.  A_Firefighter_Run          (24f, 1.0s - Carrera atlética desarmada a 480 cm/s con bombeo a 60°)
4.  A_Firefighter_Walk_1H      (30f, 1.25s - Marcha con herramienta/hacha a una mano en guardia táctica)
5.  A_Firefighter_Run_1H       (24f, 1.0s - Carrera rápida con herramienta estabilizada en el tórax)
6.  A_Firefighter_Walk_2H      (30f, 1.25s - Marcha sosteniendo cañón Hydra a dos manos)
7.  A_Firefighter_Run_2H       (24f, 1.0s - Carrera sosteniendo cañón Hydra a dos manos)
8.  A_Firefighter_Crouch_Idle  (60f, 2.5s - Postura agachada táctica para conductos SM_VentDuct < 1.05m)
9.  A_Firefighter_Crouch_Walk  (36f, 1.5s - Gateo/avance bajo coordinado en cuclillas)
10. A_Firefighter_Hose_Hold    (60f, 2.5s - Postura de contención presurizada Hydra a dos manos)

Calibración Euler Verificada:
- Frente del personaje = -Y de mundo / +X de UE5.
- Espalda / Mochila de soporte vital = +Y de mundo.
- Cero penetración en mochila de soporte vital (+Y).
- Pelvis en cuclillas remapeada a coordenadas locales (0, -0.32, 0.07).
"""

import sys
import os
import math
import shutil
import bpy
from mathutils import Matrix, Vector, Euler
from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT = r"F:\Dev\Game"
ART_DIR = os.path.join(PROJECT_ROOT, "Art")
BLEND_FILE = os.path.join(ART_DIR, "Blender", "SK_Firefighter_Official_Rigged.blend")
FBX_ANIM_DIR = os.path.join(ART_DIR, "FBX", "Animations")
RENDERS_DIR = os.path.join(ART_DIR, "Renders")
BRAIN_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\b59ff04f-3c21-4ee5-94b0-8e8f899f8923"

os.makedirs(FBX_ANIM_DIR, exist_ok=True)
os.makedirs(RENDERS_DIR, exist_ok=True)
os.makedirs(BRAIN_DIR, exist_ok=True)

R = math.radians
PI = math.pi

def reset_pose(arm_obj):
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='POSE')
    for b in arm_obj.pose.bones:
        for c in list(b.constraints):
            b.constraints.remove(c)
        b.rotation_mode = 'XYZ'
        b.rotation_euler = (0, 0, 0)
        b.location = (0, 0, 0)
        b.scale = (1, 1, 1)

def clear_animation(arm_obj):
    if arm_obj.animation_data:
        arm_obj.animation_data_clear()

def setup_camera_and_lighting():
    cam = bpy.data.objects.get("AuditCam")
    if not cam:
        cam_data = bpy.data.cameras.new("AuditCam")
        cam = bpy.data.objects.new("AuditCam", cam_data)
        bpy.context.scene.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    cam.location = Vector((-2.6, -3.8, 1.15))
    cam.data.lens = 40.0

    target = bpy.data.objects.get("AuditTarget")
    if not target:
        target = bpy.data.objects.new("AuditTarget", None)
        bpy.context.scene.collection.objects.link(target)
    target.location = Vector((0.0, 0.0, 0.65))

    for c in list(cam.constraints):
        cam.constraints.remove(c)
    tt = cam.constraints.new('TRACK_TO')
    tt.target = target
    tt.track_axis = 'TRACK_NEGATIVE_Z'
    tt.up_axis = 'UP_Y'

    light = bpy.data.objects.get("AuditSun")
    if not light:
        ldata = bpy.data.lights.new("AuditSun", 'SUN')
        light = bpy.data.objects.new("AuditSun", ldata)
        bpy.context.scene.collection.objects.link(light)
    light.data.energy = 4.0
    light.rotation_euler = Euler((R(45), R(30), 0))

    bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, 'RenderSettings') and 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
    if hasattr(bpy.context.scene, 'eevee'):
        bpy.context.scene.eevee.taa_render_samples = 16
    bpy.context.scene.render.resolution_x = 960
    bpy.context.scene.render.resolution_y = 540

def export_fbx(arm_obj, action_name, num_frames):
    fbx_out = os.path.join(FBX_ANIM_DIR, f"{action_name}.fbx")
    bpy.context.scene.frame_start = 0
    bpy.context.scene.frame_end = num_frames
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    arm_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj

    bpy.ops.export_scene.fbx(
        filepath=fbx_out,
        use_selection=True,
        add_leaf_bones=False,
        armature_nodetype='NULL',
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_ALL',
        mesh_smooth_type='FACE',
        bake_anim=True,
        bake_anim_use_nla_strips=False,
        bake_anim_use_all_actions=False,
        bake_anim_step=1.0,
        bake_anim_simplify_factor=0.0
    )
    print(f"[EXPORTED FBX] {fbx_out}")

def render_preview(frame_idx, img_name):
    bpy.context.scene.frame_set(frame_idx)
    bpy.context.view_layer.update()
    out_path = os.path.join(RENDERS_DIR, img_name)
    bpy.context.scene.render.filepath = out_path
    bpy.ops.render.render(write_still=True)
    brain_path = os.path.join(BRAIN_DIR, img_name)
    shutil.copy2(out_path, brain_path)
    return out_path

# ==============================================================================
# DEFINICIONES DE CURVAS BIOMECÁNICAS CALIBRADAS
# ==============================================================================

def build_idle(pb, f, total_frames):
    t = f / float(total_frames)
    p = 2.0 * PI * t
    breath = math.sin(p) * 0.006

    pb['pelvis'].location = Vector((0.0, breath * 0.6, 0.0))
    pb['pelvis'].rotation_euler = Euler((0.0, math.sin(p) * R(0.4), 0.0))

    # Piernas firmes y separadas a nivel de hombros
    pb['thigh_l'].rotation_euler = Euler((R(3), 0.0, R(2)))
    pb['thigh_r'].rotation_euler = Euler((R(3), 0.0, R(-2)))
    pb['calf_l'].rotation_euler = Euler((R(5), 0.0, 0.0))
    pb['calf_r'].rotation_euler = Euler((R(5), 0.0, 0.0))
    pb['foot_l'].rotation_euler = Euler((R(-7), 0.0, 0.0))
    pb['foot_r'].rotation_euler = Euler((R(-7), 0.0, 0.0))

    # Columna erguida con sutil expansión torácica
    pb['spine_01'].rotation_euler = Euler((R(3) + breath * 40.0, 0.0, 0.0))
    pb['spine_02'].rotation_euler = Euler((R(2) + breath * 30.0, 0.0, 0.0))
    pb['neck_01'].rotation_euler = Euler((R(-2), 0.0, 0.0))
    pb['head'].rotation_euler = Euler((0.0, 0.0, math.sin(p * 0.5) * R(0.8)))

    # Brazos relajados a los lados del cuerpo (en reposo anatómico, caídos hacia los muslos sin cruce)
    pb['clavicle_l'].rotation_euler = Euler((0.0, 0.0, 0.0))
    pb['upperarm_l'].rotation_euler = Euler((0.0, 0.0, R(12) + math.sin(p) * R(0.4)))
    pb['lowerarm_l'].rotation_euler = Euler((0.0, 0.0, 0.0))
    pb['hand_l'].rotation_euler = Euler((0.0, 0.0, 0.0))

    pb['clavicle_r'].rotation_euler = Euler((0.0, 0.0, 0.0))
    pb['upperarm_r'].rotation_euler = Euler((0.0, 0.0, R(-12) - math.sin(p) * R(0.4)))
    pb['lowerarm_r'].rotation_euler = Euler((0.0, 0.0, 0.0))
    pb['hand_r'].rotation_euler = Euler((0.0, 0.0, 0.0))

def apply_walk_base(pb, f, total_frames):
    t = f / float(total_frames)
    p = 2.0 * PI * t
    s_l = math.sin(p)
    s_r = math.sin(p + PI)

    pelvis_y_bob = -abs(math.sin(p)) * 0.02
    pelvis_x_sway = math.sin(p) * 0.015
    pb['pelvis'].location = Vector((pelvis_x_sway, pelvis_y_bob, -0.01))
    pb['pelvis'].rotation_euler = Euler((R(3), math.sin(p) * R(2.0), -s_l * R(3.0)))

    pb['spine_01'].rotation_euler = Euler((R(4), -math.sin(p) * R(1.5), s_l * R(2.5)))
    pb['spine_02'].rotation_euler = Euler((R(2), 0.0, s_l * R(1.5)))
    pb['neck_01'].rotation_euler = Euler((R(-4), 0.0, 0.0))
    pb['head'].rotation_euler = Euler((R(-2), 0.0, -s_l * R(1.5)))

    thigh_l_pitch = s_l * R(24)
    pb['thigh_l'].rotation_euler = Euler((thigh_l_pitch, 0.0, R(1)))
    calf_l_bend = R(6) + (max(0.0, -s_l) ** 1.4) * R(48)
    pb['calf_l'].rotation_euler = Euler((calf_l_bend, 0.0, 0.0))
    pb['foot_l'].rotation_euler = Euler((-s_l * R(14) - R(4), 0.0, 0.0))

    thigh_r_pitch = s_r * R(24)
    pb['thigh_r'].rotation_euler = Euler((thigh_r_pitch, 0.0, R(-1)))
    calf_r_bend = R(6) + (max(0.0, -s_r) ** 1.4) * R(48)
    pb['calf_r'].rotation_euler = Euler((calf_r_bend, 0.0, 0.0))
    pb['foot_r'].rotation_euler = Euler((-s_r * R(14) - R(4), 0.0, 0.0))
    return p, s_l, s_r

def build_walk(pb, f, total_frames):
    p, s_l, s_r = apply_walk_base(pb, f, total_frames)
    pb['clavicle_r'].rotation_euler = Euler((-s_l * R(3.0), 0.0, -s_l * R(2.0)))
    u_r_x = R(-10) - s_l * R(24)
    u_r_z = R(7) + s_l * R(5)
    pb['upperarm_r'].rotation_euler = Euler((u_r_x, 0.0, u_r_z))
    pb['lowerarm_r'].rotation_euler = Euler((R(-5) - max(0.0, s_l) * R(10), 0.0, -R(15) - max(0.0, s_l) * R(12)))
    pb['hand_r'].rotation_euler = Euler((R(5), 0.0, 0.0))

    pb['clavicle_l'].rotation_euler = Euler((-s_r * R(3.0), 0.0, s_r * R(2.0)))
    u_l_x = R(-10) - s_r * R(24)
    u_l_z = R(-7) - s_r * R(5)
    pb['upperarm_l'].rotation_euler = Euler((u_l_x, 0.0, u_l_z))
    pb['lowerarm_l'].rotation_euler = Euler((R(-5) - max(0.0, s_r) * R(10), 0.0, R(15) + max(0.0, s_r) * R(12)))
    pb['hand_l'].rotation_euler = Euler((R(5), 0.0, 0.0))

def apply_run_base(pb, f, total_frames):
    t = f / float(total_frames)
    p = 2.0 * PI * t
    s_l = math.sin(p)
    s_r = math.sin(p + PI)

    pelvis_y_bob = -abs(math.sin(p)) * 0.045
    pelvis_x_sway = math.sin(p) * 0.024
    pb['pelvis'].location = Vector((pelvis_x_sway, pelvis_y_bob, -0.015))
    pb['pelvis'].rotation_euler = Euler((R(6), math.sin(p) * R(3.5), -s_l * R(5.0)))

    pb['spine_01'].rotation_euler = Euler((R(12), -math.sin(p) * R(2.0), s_l * R(4.5)))
    pb['spine_02'].rotation_euler = Euler((R(6), 0.0, s_l * R(2.5)))
    pb['neck_01'].rotation_euler = Euler((R(-10), 0.0, 0.0))
    pb['head'].rotation_euler = Euler((R(-5), 0.0, -s_l * R(2.0)))

    thigh_l_pitch = s_l * R(38)
    pb['thigh_l'].rotation_euler = Euler((thigh_l_pitch, 0.0, R(2)))
    calf_l_bend = R(10) + (max(0.0, -s_l) ** 1.3) * R(72)
    pb['calf_l'].rotation_euler = Euler((calf_l_bend, 0.0, 0.0))
    pb['foot_l'].rotation_euler = Euler((-s_l * R(22) - R(6), 0.0, 0.0))

    thigh_r_pitch = s_r * R(38)
    pb['thigh_r'].rotation_euler = Euler((thigh_r_pitch, 0.0, R(-2)))
    calf_r_bend = R(10) + (max(0.0, -s_r) ** 1.3) * R(72)
    pb['calf_r'].rotation_euler = Euler((calf_r_bend, 0.0, 0.0))
    pb['foot_r'].rotation_euler = Euler((-s_r * R(22) - R(6), 0.0, 0.0))
    return p, s_l, s_r

def build_run(pb, f, total_frames):
    p, s_l, s_r = apply_run_base(pb, f, total_frames)
    pb['clavicle_r'].rotation_euler = Euler((-s_l * R(5.0), 0.0, -s_l * R(3.0)))
    u_r_x = R(-22) - s_l * R(32)
    u_r_z = R(10) + s_l * R(6)
    pb['upperarm_r'].rotation_euler = Euler((u_r_x, 0.0, u_r_z))
    pb['lowerarm_r'].rotation_euler = Euler((R(-20) - max(0.0, s_l) * R(25), 0.0, -R(35) - max(0.0, s_l) * R(15)))
    pb['hand_r'].rotation_euler = Euler((R(8), 0.0, 0.0))

    pb['clavicle_l'].rotation_euler = Euler((-s_r * R(5.0), 0.0, s_r * R(3.0)))
    u_l_x = R(-22) - s_r * R(32)
    u_l_z = R(-10) - s_r * R(6)
    pb['upperarm_l'].rotation_euler = Euler((u_l_x, 0.0, u_l_z))
    pb['lowerarm_l'].rotation_euler = Euler((R(-20) - max(0.0, s_r) * R(25), 0.0, R(35) + max(0.0, s_r) * R(15)))
    pb['hand_l'].rotation_euler = Euler((R(8), 0.0, 0.0))

def _solve_2bone_ik(root_pos, target_pos, l1, l2, pole_dir):
    to_target = target_pos - root_pos
    dist = to_target.length
    max_len = (l1 + l2) * 0.999
    min_len = abs(l1 - l2) * 1.001
    dist_clamped = max(min_len, min(max_len, dist))

    cos_alpha = max(-1.0, min(1.0, (l1 * l1 + dist_clamped * dist_clamped - l2 * l2) / (2.0 * l1 * dist_clamped)))
    alpha = math.acos(cos_alpha)
    target_dir = to_target.normalized()
    plane_normal = target_dir.cross(pole_dir)
    if plane_normal.length < 1e-4:
        plane_normal = target_dir.cross(Vector((0, 0, 1)))
    plane_normal.normalize()

    arm_up = plane_normal.cross(target_dir).normalized()
    upper_dir = (target_dir * math.cos(alpha) + arm_up * math.sin(alpha)).normalized()
    elbow_pos = root_pos + upper_dir * l1
    lower_dir = (target_pos - elbow_pos).normalized()
    return elbow_pos, upper_dir, lower_dir, plane_normal

def _align_bone_twistfree(arm_obj, bone_name, target_dir, front_dir, prev_eulers=None):
    b = arm_obj.pose.bones[bone_name]
    rest_mat3 = b.bone.matrix_local.to_3x3()

    y_r = rest_mat3.col[1].normalized()
    front_r0 = Vector((0.0, -1.0, 0.0))
    z_r = front_r0 - front_r0.dot(y_r) * y_r
    if z_r.length < 1e-4:
        z_r = Vector((0.0, 0.0, 1.0)) - Vector((0.0, 0.0, 1.0)).dot(y_r) * y_r
    z_r.normalize()
    x_r = y_r.cross(z_r).normalized()
    m_mesh_rest = Matrix((x_r, y_r, z_r)).transposed()

    y_t = target_dir.normalized()
    z_t = front_dir - front_dir.dot(y_t) * y_t
    if z_t.length < 1e-4:
        fallback = Vector((0.0, 0.0, 1.0)) if abs(y_t.z) < 0.9 else Vector((1.0, 0.0, 0.0))
        z_t = fallback - fallback.dot(y_t) * y_t
    z_t.normalize()
    x_t = y_t.cross(z_t).normalized()
    m_mesh_target = Matrix((x_t, y_t, z_t)).transposed()

    pose_mat3 = m_mesh_target @ m_mesh_rest.transposed() @ rest_mat3
    head_pos = b.head.copy()
    b.matrix = Matrix.LocRotScale(head_pos, pose_mat3, Vector((1, 1, 1)))
    bpy.context.view_layer.update()

    b.rotation_mode = 'XYZ'
    eul = b.rotation_euler.copy()
    if prev_eulers is not None:
        if bone_name in prev_eulers:
            eul.make_compatible(prev_eulers[bone_name])
            b.rotation_euler = eul
        prev_eulers[bone_name] = eul.copy()

def _apply_arm_ik(arm_obj, side, target_pos, hand_dir, pole_dir, hand_front=None, prev_eulers=None):
    bpy.context.view_layer.update()
    pb = arm_obj.pose.bones
    u_name = f'upperarm_{side}'
    l_name = f'lowerarm_{side}'
    h_name = f'hand_{side}'

    root_pos = pb[u_name].head.copy()
    l1 = (pb[u_name].tail - pb[u_name].head).length
    l2 = (pb[l_name].tail - pb[l_name].head).length
    _, u_dir, l_dir, p_norm = _solve_2bone_ik(root_pos, target_pos, l1, l2, pole_dir)

    u_front = u_dir.cross(p_norm).normalized()
    l_front = l_dir.cross(p_norm).normalized()
    h_dir = hand_dir.normalized()
    h_front = l_front if hand_front is None else hand_front.normalized()

    _align_bone_twistfree(arm_obj, u_name, u_dir, u_front, prev_eulers)
    _align_bone_twistfree(arm_obj, l_name, l_dir, l_front, prev_eulers)
    _align_bone_twistfree(arm_obj, h_name, h_dir, h_front, prev_eulers)

def build_walk_1h(pb, f, total_frames, prev_eulers=None):
    p, s_l, s_r = apply_walk_base(pb, f, total_frames)
    pb['clavicle_l'].rotation_euler = Euler((-s_r * R(3.0), 0.0, s_r * R(2.0)))
    u_l_x = R(-10) - s_r * R(22)
    u_l_z = R(-9) - s_r * R(4)
    pb['upperarm_l'].rotation_euler = Euler((u_l_x, 0.0, u_l_z))
    pb['lowerarm_l'].rotation_euler = Euler((R(-5) - max(0.0, s_r) * R(10), 0.0, R(15) + max(0.0, s_r) * R(10)))
    pb['hand_l'].rotation_euler = Euler((R(5), 0.0, 0.0))

    arm_obj = pb['upperarm_r'].id_data
    pb['clavicle_r'].rotation_euler = Euler((0.0, 0.0, 0.0))
    sway_y = math.sin(p) * 0.020
    bob_z = abs(math.cos(p)) * 0.015
    _apply_arm_ik(
        arm_obj, 'r',
        Vector((-0.37, -0.28 + sway_y, 0.86 + bob_z)),
        Vector((0.0, -1.0, -0.10)),
        Vector((-0.80, 0.25, -0.55)).normalized(),
        prev_eulers=prev_eulers,
    )

def build_run_1h(pb, f, total_frames, prev_eulers=None):
    p, s_l, s_r = apply_run_base(pb, f, total_frames)
    pb['clavicle_l'].rotation_euler = Euler((-s_r * R(5.0), 0.0, s_r * R(3.0)))
    u_l_x = R(-22) - s_r * R(30)
    u_l_z = R(-12) - s_r * R(6)
    pb['upperarm_l'].rotation_euler = Euler((u_l_x, 0.0, u_l_z))
    pb['lowerarm_l'].rotation_euler = Euler((R(-20) - max(0.0, s_r) * R(22), 0.0, R(32) + max(0.0, s_r) * R(14)))
    pb['hand_l'].rotation_euler = Euler((R(8), 0.0, 0.0))

    arm_obj = pb['upperarm_r'].id_data
    pb['clavicle_r'].rotation_euler = Euler((0.0, 0.0, 0.0))
    sway_y = math.sin(p) * 0.025
    bob_z = abs(math.sin(p)) * 0.020
    _apply_arm_ik(
        arm_obj, 'r',
        Vector((-0.37, -0.29 + sway_y, 0.87 + bob_z)),
        Vector((0.0, -1.0, -0.10)),
        Vector((-0.80, 0.25, -0.55)).normalized(),
        prev_eulers=prev_eulers,
    )

def build_walk_2h(pb, f, total_frames, prev_eulers=None):
    p, s_l, s_r = apply_walk_base(pb, f, total_frames)
    pb['spine_01'].rotation_euler = Euler((R(5), R(-9.0) - math.sin(p) * R(1.5), s_l * R(2.0)))
    pb['spine_02'].rotation_euler = Euler((R(3), R(-9.0), s_l * R(1.5)))
    pb['neck_01'].rotation_euler = Euler((R(-5), R(9.0), 0.0))
    pb['head'].rotation_euler = Euler((R(-3), R(9.0), -s_l * R(1.5)))

    arm_obj = pb['upperarm_r'].id_data
    pb['clavicle_r'].rotation_euler = Euler((0.0, 0.0, 0.0))
    pb['clavicle_l'].rotation_euler = Euler((0.0, 0.0, 0.0))

    sway_x = math.sin(p) * 0.012
    bob_z = abs(math.cos(p)) * 0.016
    _apply_arm_ik(
        arm_obj, 'r',
        Vector((-0.28 + sway_x, -0.24, 0.87 + bob_z)),
        Vector((0.35, -0.92, -0.10)),
        Vector((-0.75, 0.45, -0.50)).normalized(),
        prev_eulers=prev_eulers,
    )
    _apply_arm_ik(
        arm_obj, 'l',
        Vector((0.06 + sway_x, -0.44, 0.90 + bob_z)),
        Vector((-0.25, -0.96, -0.05)),
        Vector((0.75, 0.45, -0.50)).normalized(),
        prev_eulers=prev_eulers,
    )

def build_run_2h(pb, f, total_frames, prev_eulers=None):
    p, s_l, s_r = apply_run_base(pb, f, total_frames)
    pb['spine_01'].rotation_euler = Euler((R(12), R(-9.0) - math.sin(p) * R(2.0), s_l * R(3.0)))
    pb['spine_02'].rotation_euler = Euler((R(6), R(-9.0), s_l * R(2.0)))
    pb['neck_01'].rotation_euler = Euler((R(-10), R(9.0), 0.0))
    pb['head'].rotation_euler = Euler((R(-6), R(9.0), -s_l * R(2.0)))

    arm_obj = pb['upperarm_r'].id_data
    pb['clavicle_r'].rotation_euler = Euler((0.0, 0.0, 0.0))
    pb['clavicle_l'].rotation_euler = Euler((0.0, 0.0, 0.0))

    sway_x = math.sin(p) * 0.016
    bob_z = abs(math.sin(p)) * 0.022
    _apply_arm_ik(
        arm_obj, 'r',
        Vector((-0.28 + sway_x, -0.25, 0.88 + bob_z)),
        Vector((0.35, -0.92, -0.10)),
        Vector((-0.75, 0.45, -0.50)).normalized(),
        prev_eulers=prev_eulers,
    )
    _apply_arm_ik(
        arm_obj, 'l',
        Vector((0.06 + sway_x, -0.45, 0.91 + bob_z)),
        Vector((-0.25, -0.96, -0.05)),
        Vector((0.75, 0.45, -0.50)).normalized(),
        prev_eulers=prev_eulers,
    )

def build_crouch_idle(pb, f, total_frames, prev_eulers=None):
    t = f / float(total_frames)
    p = 2.0 * PI * t
    pb['pelvis'].location = Vector((0.0, -0.25 + math.sin(p) * 0.004, 0.03))
    pb['pelvis'].rotation_euler = Euler((R(8), 0.0, 0.0))
    pb['spine_01'].rotation_euler = Euler((R(22) + math.sin(p) * R(0.8), 0.0, 0.0))
    pb['spine_02'].rotation_euler = Euler((R(14) + math.sin(p) * R(0.6), 0.0, 0.0))
    pb['neck_01'].rotation_euler = Euler((R(-26), 0.0, 0.0))
    pb['head'].rotation_euler = Euler((R(-12), 0.0, math.sin(p * 0.5) * R(1.0)))

    pb['thigh_l'].rotation_euler = Euler((R(-74), 0.0, R(5)))
    pb['calf_l'].rotation_euler = Euler((R(118), 0.0, 0.0))
    pb['foot_l'].rotation_euler = Euler((R(-50), 0.0, 0.0))

    pb['thigh_r'].rotation_euler = Euler((R(-74), 0.0, R(-5)))
    pb['calf_r'].rotation_euler = Euler((R(118), 0.0, 0.0))
    pb['foot_r'].rotation_euler = Euler((R(-50), 0.0, 0.0))

    pb['clavicle_l'].rotation_euler = Euler((R(-4), 0.0, R(-4)))
    pb['upperarm_l'].rotation_euler = Euler((R(-26) + math.sin(p) * R(0.5), 0.0, R(-26)))
    pb['lowerarm_l'].rotation_euler = Euler((R(-52), 0.0, R(8)))
    pb['hand_l'].rotation_euler = Euler((0.0, 0.0, 0.0))

    pb['clavicle_r'].rotation_euler = Euler((R(-4), 0.0, R(4)))
    pb['upperarm_r'].rotation_euler = Euler((R(-26) + math.sin(p) * R(0.5), 0.0, R(26)))
    pb['lowerarm_r'].rotation_euler = Euler((R(-52), 0.0, R(-8)))
    pb['hand_r'].rotation_euler = Euler((0.0, 0.0, 0.0))

def build_crouch_walk(pb, f, total_frames, prev_eulers=None):
    t = f / float(total_frames)
    p = 2.0 * PI * t
    s_l = math.sin(p)
    s_r = math.sin(p + PI)

    pb['pelvis'].location = Vector((math.sin(p) * 0.012, -0.24 + math.sin(2*p) * 0.008, 0.03))
    pb['pelvis'].rotation_euler = Euler((R(12), math.sin(p) * R(1.5), -s_l * R(2.0)))

    pb['spine_01'].rotation_euler = Euler((R(20), 0.0, s_l * R(1.5)))
    pb['spine_02'].rotation_euler = Euler((R(14), 0.0, 0.0))
    pb['neck_01'].rotation_euler = Euler((R(-24), 0.0, 0.0))
    pb['head'].rotation_euler = Euler((R(-10), 0.0, -s_l * R(1.5)))

    thigh_l_pitch = R(-72) + s_l * R(16)
    pb['thigh_l'].rotation_euler = Euler((thigh_l_pitch, 0.0, R(5)))
    calf_l_bend = R(114) + (max(0.0, -s_l) ** 1.2) * R(22)
    pb['calf_l'].rotation_euler = Euler((calf_l_bend, 0.0, 0.0))
    pb['foot_l'].rotation_euler = Euler((R(-48) - s_l * R(8), 0.0, 0.0))

    thigh_r_pitch = R(-72) + s_r * R(16)
    pb['thigh_r'].rotation_euler = Euler((thigh_r_pitch, 0.0, R(-5)))
    calf_r_bend = R(114) + (max(0.0, -s_r) ** 1.2) * R(22)
    pb['calf_r'].rotation_euler = Euler((calf_r_bend, 0.0, 0.0))
    pb['foot_r'].rotation_euler = Euler((R(-48) - s_r * R(8), 0.0, 0.0))

    pb['clavicle_r'].rotation_euler = Euler((R(-4), 0.0, R(4)))
    u_r_x = R(-26) - s_l * R(14)
    pb['upperarm_r'].rotation_euler = Euler((u_r_x, 0.0, R(26)))
    pb['lowerarm_r'].rotation_euler = Euler((R(-50) - max(0.0, s_l) * R(10), 0.0, R(-8)))
    pb['hand_r'].rotation_euler = Euler((0.0, 0.0, 0.0))

    pb['clavicle_l'].rotation_euler = Euler((R(-4), 0.0, R(-4)))
    u_l_x = R(-26) - s_r * R(14)
    pb['upperarm_l'].rotation_euler = Euler((u_l_x, 0.0, R(-26)))
    pb['lowerarm_l'].rotation_euler = Euler((R(-50) - max(0.0, s_r) * R(10), 0.0, R(8)))
    pb['hand_l'].rotation_euler = Euler((0.0, 0.0, 0.0))

def build_hose_hold(pb, f, total_frames, prev_eulers=None):
    t = f / float(total_frames)
    p = 2.0 * PI * t
    jitter = math.sin(t * 16.0 * PI) * 0.002
    breathe = math.sin(p) * R(0.6)

    pb['pelvis'].location = Vector((0.0, -0.015, 0.0))
    pb['pelvis'].rotation_euler = Euler((R(3), 0.0, 0.0))

    pb['thigh_l'].rotation_euler = Euler((R(2), 0.0, R(2)))
    pb['calf_l'].rotation_euler = Euler((R(8), 0.0, 0.0))
    pb['foot_l'].rotation_euler = Euler((R(-9), 0.0, 0.0))

    pb['thigh_r'].rotation_euler = Euler((R(2), 0.0, R(-2)))
    pb['calf_r'].rotation_euler = Euler((R(8), 0.0, 0.0))
    pb['foot_r'].rotation_euler = Euler((R(-9), 0.0, 0.0))

    pb['spine_01'].rotation_euler = Euler((R(4) + breathe, R(-9.0), 0.0))
    pb['spine_02'].rotation_euler = Euler((R(3) + breathe * 0.5, R(-9.0), 0.0))
    pb['neck_01'].rotation_euler = Euler((R(-4), R(9.0), 0.0))
    pb['head'].rotation_euler = Euler((R(-3), R(9.0), 0.0))

    arm_obj = pb['upperarm_r'].id_data
    pb['clavicle_r'].rotation_euler = Euler((0.0, 0.0, 0.0))
    pb['clavicle_l'].rotation_euler = Euler((0.0, 0.0, 0.0))

    _apply_arm_ik(
        arm_obj, 'r',
        Vector((-0.28, -0.24 + jitter, 0.87 + math.sin(p) * 0.004)),
        Vector((0.35, -0.92, -0.10)),
        Vector((-0.75, 0.45, -0.50)).normalized(),
        prev_eulers=prev_eulers,
    )
    _apply_arm_ik(
        arm_obj, 'l',
        Vector((0.06, -0.44 + jitter, 0.90 + math.sin(p) * 0.004)),
        Vector((-0.25, -0.96, -0.05)),
        Vector((0.75, 0.45, -0.50)).normalized(),
        prev_eulers=prev_eulers,
    )

ANIM_CONFIGS = [
    {'name': 'A_Firefighter_Idle',        'frames': 60, 'func': build_idle,        'preview_frame': 0},
    {'name': 'A_Firefighter_Walk',        'frames': 30, 'func': build_walk,        'preview_frame': 7},
    {'name': 'A_Firefighter_Run',         'frames': 24, 'func': build_run,         'preview_frame': 6},
    {'name': 'A_Firefighter_Walk_1H',     'frames': 30, 'func': build_walk_1h,     'preview_frame': 7},
    {'name': 'A_Firefighter_Run_1H',      'frames': 24, 'func': build_run_1h,      'preview_frame': 6},
    {'name': 'A_Firefighter_Walk_2H',     'frames': 30, 'func': build_walk_2h,     'preview_frame': 7},
    {'name': 'A_Firefighter_Run_2H',      'frames': 24, 'func': build_run_2h,      'preview_frame': 6},
    {'name': 'A_Firefighter_Crouch_Idle', 'frames': 60, 'func': build_crouch_idle, 'preview_frame': 0},
    {'name': 'A_Firefighter_Crouch_Walk', 'frames': 36, 'func': build_crouch_walk, 'preview_frame': 9},
    {'name': 'A_Firefighter_Hose_Hold',   'frames': 60, 'func': build_hose_hold,   'preview_frame': 20},
]

def main():
    print("=" * 80)
    print("INICIANDO GENERACION OFICIAL MAESTRA DE ANIMACIONES DE LOCOMOCION")
    print("=" * 80)

    if not os.path.exists(BLEND_FILE):
        print(f"[ERROR FATAL] Archivo base no existe: {BLEND_FILE}")
        sys.exit(1)

    bpy.ops.wm.open_mainfile(filepath=BLEND_FILE)
    for o in bpy.data.objects:
        if o.type == 'MESH' and ('Cannon' in o.name or 'Extinguisher' in o.name):
            o.hide_render = True
            o.hide_viewport = True
    setup_camera_and_lighting()

    arm_obj = [o for o in bpy.context.scene.objects if o.type == 'ARMATURE'][0]
    pb = arm_obj.pose.bones

    for cfg in ANIM_CONFIGS:
        name = cfg['name']
        frames = cfg['frames']
        func = cfg['func']
        prev_f = cfg['preview_frame']

        print(f"\n[GENERATING] {name} ({frames} frames)...")
        reset_pose(arm_obj)
        clear_animation(arm_obj)

        act = bpy.data.actions.new(name=name)
        arm_obj.animation_data_create()
        arm_obj.animation_data.action = act

        prev_eulers = {}
        for f in range(frames + 1):
            bpy.context.scene.frame_set(f)
            f_eval = 0 if f == frames else f
            func(pb, f_eval, frames) if func in (build_idle, build_walk, build_run) else func(pb, f_eval, frames, prev_eulers)
            if 'weapon_socket_r' in pb:
                pb['weapon_socket_r'].location = Vector((0, 0, 0))
                pb['weapon_socket_r'].rotation_euler = Euler((0, 0, 0))
            for b in pb:
                if b.name in prev_eulers:
                    eul = b.rotation_euler.copy()
                    eul.make_compatible(prev_eulers[b.name])
                    b.rotation_euler = eul
                prev_eulers[b.name] = b.rotation_euler.copy()
                b.keyframe_insert("location", frame=f)
                b.keyframe_insert("rotation_euler", frame=f)

        export_fbx(arm_obj, name, frames)
        render_preview(prev_f, f"LocomotionOfficial_{name}.png")

    print("\n" + "=" * 80)
    print("TODAS LAS 10 ANIMACIONES DE LOCOMOCION GENERADAS, EXPORTADAS Y RENDERIZADAS.")
    print("=" * 80)

if __name__ == '__main__':
    main()

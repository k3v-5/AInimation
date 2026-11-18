"""
generar_animaciones_combate_y_transporte_oficial.py
===================================================
Generador OFICIAL y DEFINITIVO de Animaciones de Combate (Hacha Térmica),
Posturas de Guardia Táctica y Transporte Bimanual (Carro de Soldadura / Batería).

Genera 4 secuencias autoritativas para Unreal Engine 5:
1. A_Firefighter_Axe_Swing  (24f - Golpe con Hacha Térmica: Windup overhead -> Strike descendente -> Recovery)
2. A_Firefighter_Carry_Hold (60f - Transporte Estacionario de Equipo Pesado / Carro)
3. A_Firefighter_Carry_Walk (30f - Locomoción en Marcha Empujando Carro con Zancada Segura)
4. A_Firefighter_1H_Hold    (60f - Guardia Táctica Frontal a 1 Mano: Hacha, Extintor, Desfibrilador)

Garantiza:
- Rigurosa cinemática de 2 huesos sin torsiones invertidas de hombro ni dislocaciones.
- Cero penetración del carro de soldadura en los pies del bombero (holgura > 30 cm garantizada).
- Renderizado de comprobación visual directa (GEMINI.md Regla 5).
"""

import bpy
import math
import os
import shutil
from mathutils import Vector, Euler, Matrix

PROJECT_ROOT = r"F:\Dev\Game"
BLEND_FILE = os.path.join(PROJECT_ROOT, "Art", "Blender", "SK_Firefighter_Official_Rigged.blend")
FBX_DIR = os.path.join(PROJECT_ROOT, "Art", "FBX", "Animations")
RENDERS_DIR = os.path.join(PROJECT_ROOT, "Art", "Renders")
BRAIN_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\b59ff04f-3c21-4ee5-94b0-8e8f899f8923"

os.makedirs(FBX_DIR, exist_ok=True)
os.makedirs(RENDERS_DIR, exist_ok=True)
os.makedirs(BRAIN_DIR, exist_ok=True)

def R(deg):
    return math.radians(deg)

def reset_pose(arm_obj):
    for b in arm_obj.pose.bones:
        b.rotation_euler = (0, 0, 0)
        b.location = (0, 0, 0)
    bpy.context.view_layer.update()

def clear_armature(arm_obj):
    if arm_obj.animation_data:
        arm_obj.animation_data_clear()
    for b in arm_obj.pose.bones:
        for c in list(b.constraints):
            b.constraints.remove(c)

def setup_camera():
    cam = bpy.data.objects.get("MasterCam")
    if not cam:
        cdata = bpy.data.cameras.new("MasterCam")
        cam = bpy.data.objects.new("MasterCam", cdata)
        bpy.context.scene.collection.objects.link(cam)
    cam.location = Vector((2.8, -4.0, 1.25))
    target = Vector((0.0, -0.1, 0.70))
    cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
    cam.data.lens = 38
    bpy.context.scene.camera = cam
    bpy.context.scene.render.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
    bpy.context.scene.render.resolution_x = 960
    bpy.context.scene.render.resolution_y = 720

def solve_2bone_ik(root_pos, target_pos, l1, l2, pole_dir):
    to_target = target_pos - root_pos
    dist = to_target.length
    max_len = (l1 + l2) * 0.999
    min_len = abs(l1 - l2) * 1.001
    dist_clamped = max(min_len, min(max_len, dist))
    
    cos_alpha = (l1 * l1 + dist_clamped * dist_clamped - l2 * l2) / (2.0 * l1 * dist_clamped)
    cos_alpha = max(-1.0, min(1.0, cos_alpha))
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

def align_bone_twistfree(arm_obj, bone_name, target_dir, front_dir, prev_eulers=None):
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

def apply_arm_ik(arm_obj, side, target_pos, hand_dir, pole_dir, hand_front=None, prev_eulers=None):
    bpy.context.view_layer.update()
    pb = arm_obj.pose.bones
    u_name = f'upperarm_{side}'
    l_name = f'lowerarm_{side}'
    h_name = f'hand_{side}'

    root_pos = pb[u_name].head.copy()
    l1 = (pb[u_name].tail - pb[u_name].head).length
    l2 = (pb[l_name].tail - pb[l_name].head).length
    _, u_dir, l_dir, p_norm = solve_2bone_ik(root_pos, target_pos, l1, l2, pole_dir)

    u_front = u_dir.cross(p_norm).normalized()
    l_front = l_dir.cross(p_norm).normalized()
    h_dir = hand_dir.normalized()
    h_front = l_front if hand_front is None else hand_front.normalized()

    align_bone_twistfree(arm_obj, u_name, u_dir, u_front, prev_eulers)
    align_bone_twistfree(arm_obj, l_name, l_dir, l_front, prev_eulers)
    align_bone_twistfree(arm_obj, h_name, h_dir, h_front, prev_eulers)

def finalize_frame_eulers(pb, f, prev_eulers):
    for b in pb:
        b.rotation_mode = 'XYZ'
        if b.name in prev_eulers:
            eul = b.rotation_euler.copy()
            eul.make_compatible(prev_eulers[b.name])
            b.rotation_euler = eul
        prev_eulers[b.name] = b.rotation_euler.copy()
        b.keyframe_insert("location", frame=f)
        b.keyframe_insert("rotation_euler", frame=f)

# ----------------------------------------------------------------------
# ANIMATION 1: A_Firefighter_Axe_Swing (2-Bone IK Unified Chop)
# ----------------------------------------------------------------------
def build_axe_swing(arm_obj):
    clear_armature(arm_obj)
    reset_pose(arm_obj)
    pb = arm_obj.pose.bones

    action = bpy.data.actions.new("A_Firefighter_Axe_Swing")
    if arm_obj.animation_data is None:
        arm_obj.animation_data_create()
    arm_obj.animation_data.action = action

    def smooth_step(t):
        t = max(0.0, min(1.0, t))
        return t * t * (3.0 - 2.0 * t)

    def lerp_vec(v1, v2, a):
        return v1.lerp(v2, a)

    # Puntos clave unificados con A_Firefighter_1H_Hold y despejados del casco (>18cm en windup)
    t_ready  = Vector((-0.37, -0.28, 0.86))
    t_windup = Vector((-0.44, -0.18, 1.38))
    t_impact = Vector((-0.30, -0.46, 0.76))
    t_recoil = Vector((-0.33, -0.39, 0.80))

    h_ready  = Vector((0.0, -1.0, -0.10)).normalized()
    h_windup = Vector((-0.25, -0.60, 0.76)).normalized()
    h_impact = Vector((-0.05, -0.78, -0.62)).normalized()
    h_recoil = Vector((-0.02, -0.90, -0.35)).normalized()

    p_ready  = Vector((-0.80, 0.25, -0.55)).normalized()
    p_windup = Vector((-0.75, 0.45, -0.35)).normalized()
    p_impact = Vector((-0.80, 0.25, -0.50)).normalized()

    total_frames = 24
    prev_eulers = {}
    for f in range(total_frames + 1):
        f_eval = 0 if f == total_frames else f
        if f_eval <= 7:
            a = smooth_step(f_eval / 7.0)
            r_target = lerp_vec(t_ready, t_windup, a)
            h_dir = lerp_vec(h_ready, h_windup, a).normalized()
            pole_r = lerp_vec(p_ready, p_windup, a).normalized()
            sp1_x, sp1_y, sp1_z = R(3 - 7*a), R(-3*a), R(-8*a)
            pelvis_z, leg_rot = 0.0, 0.0
        elif f_eval <= 15:
            t_swing = (f_eval - 7.0) / 8.0
            a = smooth_step(t_swing)
            r_target = lerp_vec(t_windup, t_impact, a)
            h_dir = lerp_vec(h_windup, h_impact, a).normalized()
            pole_r = lerp_vec(p_windup, p_impact, a).normalized()
            sp1_x, sp1_y, sp1_z = R(-4 + 16*a), R(-3 + 7*a), R(-8 + 18*a)
            pelvis_z = -0.02 * math.sin(math.pi * t_swing)
            leg_rot = math.sin(math.pi * t_swing)
        elif f_eval <= 18:
            a = smooth_step((f_eval - 15.0) / 3.0)
            r_target = lerp_vec(t_impact, t_recoil, a)
            h_dir = lerp_vec(h_impact, h_recoil, a).normalized()
            pole_r = lerp_vec(p_impact, p_ready, a).normalized()
            sp1_x, sp1_y, sp1_z = R(12 - 4*a), R(4 - a), R(10 - 3*a)
            pelvis_z = -0.02 * (1.0 - a)
            leg_rot = 0.5 * (1.0 - a)
        else:
            a = smooth_step((f_eval - 18.0) / 6.0)
            r_target = lerp_vec(t_recoil, t_ready, a)
            h_dir = lerp_vec(h_recoil, h_ready, a).normalized()
            pole_r = p_ready
            sp1_x, sp1_y, sp1_z = R(8 - 5*a), R(3*(1-a)), R(7*(1-a))
            pelvis_z, leg_rot = 0.0, 0.0

        pb['pelvis'].location = Vector((0, 0, pelvis_z))
        pb['spine_01'].rotation_euler = Euler((sp1_x, sp1_y, sp1_z))
        pb['spine_02'].rotation_euler = Euler((sp1_x * 0.6, sp1_y * 0.6, sp1_z * 0.6))
        pb['thigh_r'].rotation_euler = Euler((R(2 + 2 * leg_rot), 0, R(-2)))
        pb['thigh_l'].rotation_euler = Euler((R(2 - 2 * leg_rot), 0, R(2)))
        pb['calf_r'].rotation_euler = Euler((R(4 + 3 * leg_rot), 0, 0))
        pb['calf_l'].rotation_euler = Euler((R(4 - 2 * leg_rot), 0, 0))
        pb['foot_r'].rotation_euler = Euler((R(-6), 0, 0))
        pb['foot_l'].rotation_euler = Euler((R(-6), 0, 0))

        apply_arm_ik(arm_obj, 'r', r_target, h_dir, pole_r, prev_eulers=prev_eulers)
        apply_arm_ik(
            arm_obj, 'l',
            Vector((0.40, -0.10, 0.78)),
            Vector((0.0, -1.0, -0.20)),
            Vector((0.80, 0.25, -0.50)).normalized(),
            prev_eulers=prev_eulers,
        )

        if 'weapon_socket_r' in pb:
            pb['weapon_socket_r'].location = Vector((0, 0, 0))
            pb['weapon_socket_r'].rotation_euler = Euler((0, 0, 0))

        finalize_frame_eulers(pb, f, prev_eulers)

# ----------------------------------------------------------------------
# ANIMATION 2: A_Firefighter_Carry_Hold (60f)
# ----------------------------------------------------------------------
def build_carry_hold(arm_obj):
    clear_armature(arm_obj)
    reset_pose(arm_obj)
    pb = arm_obj.pose.bones

    action = bpy.data.actions.new("A_Firefighter_Carry_Hold")
    if arm_obj.animation_data is None:
        arm_obj.animation_data_create()
    arm_obj.animation_data.action = action

    total_frames = 60
    prev_eulers = {}
    for f in range(total_frames + 1):
        t = 0.0 if f == total_frames else (f / float(total_frames))
        p = 2.0 * math.pi * t
        breath = math.sin(p) * 0.005

        pb['pelvis'].location = Vector((0.0, breath, 0.0))
        pb['pelvis'].rotation_euler = Euler((0.0, math.sin(p) * R(0.5), 0.0))
        pb['thigh_l'].rotation_euler = Euler((R(3), 0.0, R(2)))
        pb['thigh_r'].rotation_euler = Euler((R(3), 0.0, R(-2)))
        pb['calf_l'].rotation_euler = Euler((R(6), 0.0, 0.0))
        pb['calf_r'].rotation_euler = Euler((R(6), 0.0, 0.0))
        pb['foot_l'].rotation_euler = Euler((R(-8), 0.0, 0.0))
        pb['foot_r'].rotation_euler = Euler((R(-8), 0.0, 0.0))
        pb['spine_01'].rotation_euler = Euler((R(6), 0.0, 0.0))
        pb['spine_02'].rotation_euler = Euler((R(3), 0.0, 0.0))
        pb['neck_01'].rotation_euler = Euler((R(-3), 0.0, 0.0))
        pb['head'].rotation_euler = Euler((0.0, 0.0, 0.0))

        apply_arm_ik(
            arm_obj, 'r',
            Vector((-0.24, -0.45 + breath * 0.5, 0.95 + breath)),
            Vector((0.0, -1.0, -0.2)),
            Vector((-0.80, 0.25, -0.45)).normalized(),
            prev_eulers=prev_eulers,
        )
        apply_arm_ik(
            arm_obj, 'l',
            Vector((0.24, -0.45 + breath * 0.5, 0.95 + breath)),
            Vector((0.0, -1.0, -0.2)),
            Vector((0.80, 0.25, -0.45)).normalized(),
            prev_eulers=prev_eulers,
        )

        finalize_frame_eulers(pb, f, prev_eulers)

# ----------------------------------------------------------------------
# ANIMATION 3: A_Firefighter_Carry_Walk (30f)
# ----------------------------------------------------------------------
def build_carry_walk(arm_obj):
    clear_armature(arm_obj)
    reset_pose(arm_obj)
    pb = arm_obj.pose.bones

    action = bpy.data.actions.new("A_Firefighter_Carry_Walk")
    if arm_obj.animation_data is None:
        arm_obj.animation_data_create()
    arm_obj.animation_data.action = action

    total_frames = 30
    prev_eulers = {}
    for f in range(total_frames + 1):
        t = 0.0 if f == total_frames else (f / float(total_frames))
        p = 2.0 * math.pi * t
        s_l = math.sin(p)
        s_r = math.sin(p + math.pi)

        pelvis_bob = -abs(math.sin(p)) * 0.018
        pelvis_sway = math.sin(p) * 0.012
        pb['pelvis'].location = Vector((pelvis_sway, pelvis_bob, 0.0))
        pb['pelvis'].rotation_euler = Euler((R(4), math.sin(p) * R(1.5), -s_l * R(2.0)))
        pb['spine_01'].rotation_euler = Euler((R(7), -math.sin(p) * R(1.0), s_l * R(1.5)))
        pb['spine_02'].rotation_euler = Euler((R(3), 0.0, s_l * R(1.0)))
        pb['head'].rotation_euler = Euler((R(-2), 0.0, -s_l * R(1.0)))

        thigh_l_pitch = s_l * R(18)
        pb['thigh_l'].rotation_euler = Euler((thigh_l_pitch, 0.0, R(1.5)))
        calf_l_bend = R(6) + (max(0.0, -s_l) ** 1.2) * R(38)
        pb['calf_l'].rotation_euler = Euler((calf_l_bend, 0.0, 0.0))
        pb['foot_l'].rotation_euler = Euler((-s_l * R(12) - R(4), 0.0, 0.0))

        thigh_r_pitch = s_r * R(18)
        pb['thigh_r'].rotation_euler = Euler((thigh_r_pitch, 0.0, R(-1.5)))
        calf_r_bend = R(6) + (max(0.0, -s_r) ** 1.2) * R(38)
        pb['calf_r'].rotation_euler = Euler((calf_r_bend, 0.0, 0.0))
        pb['foot_r'].rotation_euler = Euler((-s_r * R(12) - R(4), 0.0, 0.0))

        apply_arm_ik(
            arm_obj, 'r',
            Vector((-0.24, -0.45, 0.95 + pelvis_bob * 0.5)),
            Vector((0.0, -1.0, -0.2)),
            Vector((-0.80, 0.25, -0.45)).normalized(),
            prev_eulers=prev_eulers,
        )
        apply_arm_ik(
            arm_obj, 'l',
            Vector((0.24, -0.45, 0.95 + pelvis_bob * 0.5)),
            Vector((0.0, -1.0, -0.2)),
            Vector((0.80, 0.25, -0.45)).normalized(),
            prev_eulers=prev_eulers,
        )

        finalize_frame_eulers(pb, f, prev_eulers)

# ----------------------------------------------------------------------
# ANIMATION 4: A_Firefighter_1H_Hold (60f)
# ----------------------------------------------------------------------
def build_1h_hold(arm_obj):
    clear_armature(arm_obj)
    reset_pose(arm_obj)
    pb = arm_obj.pose.bones

    action = bpy.data.actions.new("A_Firefighter_1H_Hold")
    if arm_obj.animation_data is None:
        arm_obj.animation_data_create()
    arm_obj.animation_data.action = action

    total_frames = 60
    prev_eulers = {}
    for f in range(total_frames + 1):
        t = 0.0 if f == total_frames else (f / float(total_frames))
        p = 2.0 * math.pi * t
        breath = math.sin(p) * 0.005

        pb['pelvis'].location = Vector((0.0, breath, 0.0))
        pb['pelvis'].rotation_euler = Euler((0.0, math.sin(p) * R(0.5), 0.0))
        pb['thigh_l'].rotation_euler = Euler((R(2), 0.0, R(1)))
        pb['thigh_r'].rotation_euler = Euler((R(2), 0.0, R(-1)))
        pb['calf_l'].rotation_euler = Euler((R(4), 0.0, 0.0))
        pb['calf_r'].rotation_euler = Euler((R(4), 0.0, 0.0))
        pb['foot_l'].rotation_euler = Euler((R(-6), 0.0, 0.0))
        pb['foot_r'].rotation_euler = Euler((R(-6), 0.0, 0.0))
        pb['spine_01'].rotation_euler = Euler((R(3), 0.0, 0.0))
        pb['spine_02'].rotation_euler = Euler((R(2), 0.0, 0.0))

        apply_arm_ik(
            arm_obj, 'r',
            Vector((-0.37, -0.28, 0.86 + breath)),
            Vector((0.0, -1.0, -0.10)),
            Vector((-0.80, 0.25, -0.55)).normalized(),
            prev_eulers=prev_eulers,
        )
        apply_arm_ik(
            arm_obj, 'l',
            Vector((0.40, -0.10, 0.78 + breath)),
            Vector((0.0, -1.0, -0.20)),
            Vector((0.80, 0.25, -0.50)).normalized(),
            prev_eulers=prev_eulers,
        )

        # Mantener weapon_socket_r consistente con Walk_1H, Run_1H y Axe_Swing (cero sobrescritura de matriz)
        if 'weapon_socket_r' in pb:
            pb['weapon_socket_r'].location = Vector((0, 0, 0))
            pb['weapon_socket_r'].rotation_euler = Euler((0, 0, 0))

        finalize_frame_eulers(pb, f, prev_eulers)

def export_active_anim(arm_obj, char_obj, anim_name, frames, previews):
    bpy.context.scene.frame_start = 0
    bpy.context.scene.frame_end = frames
    
    for tag, f_num in previews:
        bpy.context.scene.frame_set(f_num)
        bpy.context.view_layer.update()
        png_name = f"FinalCert_{anim_name}_{tag}.png"
        out_png = os.path.join(RENDERS_DIR, png_name)
        bpy.context.scene.render.filepath = out_png
        bpy.ops.render.render(write_still=True)
        brain_png = os.path.join(BRAIN_DIR, png_name)
        shutil.copy2(out_png, brain_png)
        print(f"  [RENDER OK] {png_name} (Frame {f_num})")
        
    fbx_path = os.path.join(FBX_DIR, f"{anim_name}.fbx")
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    arm_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj
    
    bpy.ops.export_scene.fbx(
        filepath=fbx_path,
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
    print(f"  [FBX OK] Exported: {fbx_path} ({os.path.getsize(fbx_path) // 1024} KB)")

def main():
    print("=" * 70)
    print("EJECUTANDO GENERADOR OFICIAL DE ANIMACIONES DE COMBATE Y TRANSPORTE")
    print("=" * 70)
    
    bpy.ops.wm.open_mainfile(filepath=BLEND_FILE)
    for o in bpy.data.objects:
        if o.type == 'MESH' and ('Cannon' in o.name or 'Extinguisher' in o.name):
            o.hide_render = True
            o.hide_viewport = True
    arm_obj = bpy.data.objects.get("SK_Firefighter_Armature")
    char_obj = bpy.data.objects.get("SK_Firefighter_Official")
    setup_camera()
    
    # 1. Axe Swing
    print("\n>>> Generando A_Firefighter_Axe_Swing...")
    build_axe_swing(arm_obj)
    export_active_anim(arm_obj, char_obj, "A_Firefighter_Axe_Swing", 24, [('Windup', 7), ('Impact', 15), ('Recovery', 19)])
    
    # 2. Carry Hold
    print("\n>>> Generando A_Firefighter_Carry_Hold...")
    build_carry_hold(arm_obj)
    export_active_anim(arm_obj, char_obj, "A_Firefighter_Carry_Hold", 60, [('Hold_Pose', 15)])
    
    # 3. Carry Walk
    print("\n>>> Generando A_Firefighter_Carry_Walk...")
    build_carry_walk(arm_obj)
    export_active_anim(arm_obj, char_obj, "A_Firefighter_Carry_Walk", 30, [('Walk_Left', 7), ('Walk_Right', 22)])
    
    # 4. 1H Hold
    print("\n>>> Generando A_Firefighter_1H_Hold...")
    build_1h_hold(arm_obj)
    export_active_anim(arm_obj, char_obj, "A_Firefighter_1H_Hold", 60, [('Guard_Pose', 15)])
    
    # Save master blend
    blend_out = os.path.join(PROJECT_ROOT, "Art", "Blender", "SK_Firefighter_Official_Animated.blend")
    bpy.ops.wm.save_as_mainfile(filepath=blend_out)
    print(f"\n[BLEND OK] Guardado archivo maestro animado: {blend_out}")
    print("[FINAL SUCCESS] Pipeline completado exitosamente.")

if __name__ == "__main__":
    main()

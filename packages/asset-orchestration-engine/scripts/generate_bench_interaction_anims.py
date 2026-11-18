"""generate_bench_interaction_anims.py
================================================================================
ANIMACIONES PROCEDURALES DE INTERACCIÓN CON LA MESA DE CRAFTEO (1P Y 3P)
================================================================================
Genera las animaciones canónicas para la Mesa de Crafteo Sci-Fi (SM_CraftingBench):
- A_Player_CraftingBench_Interact (3P - SK_Player / ARM_Player, 22 huesos canónicos)
- A_FPS_CraftingBench_Interact (1P - SK_FPS_Arms)

Coreografía de Interacción (3.2s / 96 frames a 30 FPS):
1. Frame 0:   Postura neutral frente a la mesa.
2. Frame 25:  Manos juntas al centro de la fosa depositando el scrap.
3. Frame 50:  Manos extendidas bimanualmente hacia los marcos laterales (palmas hacia abajo,
              Two-Bone IK biológico, buffer >= 35 cm).
4. Frame 70:  Micro-vibración bimanual y contención mientras estallan destellos morados
              y se materializa el arma en la fosa central.
5. Frame 96:  Retracción fluida y retorno a la postura neutral.

Renderiza el mosaico de 4 vistas (Directiva 4):
- Vista 1: Frontal 3P (Personaje + Mesa completa con manos extendidas)
- Vista 2: Perspectiva 3/4 3P (Encuadre heroico de cuerpo entero)
- Vista 3: Detalle de Manos (Primer plano sobre las placas laterales y plasma)
- Vista 4: Cámara FPS (Punto de vista en primera persona encuadrando los brazos sobre la mesa)
"""

import os
import sys
import math
import bpy
import bmesh
from mathutils import Vector, Euler, Matrix

R = math.radians

# Rutas
PROJECT_ROOT = r"E:\Darx_Proyect"
ART_DIR = os.path.join(PROJECT_ROOT, "Art")
FBX_FPS_DIR = os.path.join(ART_DIR, "FBX", "Anim_FPS")
FBX_3P_DIR = os.path.join(ART_DIR, "FBX", "Anim_Player")
BRAIN_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"

# Importar guardián de validación de exportación
val_dir = os.path.join(PROJECT_ROOT, "Tools", "AssetEngine", "src", "validation")
if val_dir not in sys.path:
    sys.path.insert(0, val_dir)
try:
    import blender_export_guard
    validar_ruta_destino_fbx = blender_export_guard.validar_ruta_destino_fbx
    crear_respaldo_blend = blender_export_guard.crear_respaldo_blend
    verificar_esqueleto_canonico = blender_export_guard.verificar_esqueleto_canonico
except ImportError:
    validar_ruta_destino_fbx = None
    crear_respaldo_blend = None
    verificar_esqueleto_canonico = None

BENCH_BLEND = os.path.join(PROJECT_ROOT, r"Saved\Player_Skin_Workspace\DarX_CraftingBench_Master.blend")
PLAYER_BLEND = os.path.join(PROJECT_ROOT, r"Saved\Player_Skin_Workspace\DarX_Player_Rigged_Canonical.blend")
FPS_FBX = os.path.join(ART_DIR, "FBX", "SK_FPS_Arms.fbx")

os.makedirs(FBX_FPS_DIR, exist_ok=True)
os.makedirs(FBX_3P_DIR, exist_ok=True)
os.makedirs(BRAIN_DIR, exist_ok=True)


def export_armature_fbx(arm_obj, filepath):
    """Exporta armadura pura con animación a 30 FPS compatible con UE5."""
    if validar_ruta_destino_fbx:
        valido, razon = validar_ruta_destino_fbx(filepath)
        if not valido:
            raise RuntimeError(razon)

    if bpy.context.active_object and bpy.context.active_object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')
    arm_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj

    scene = bpy.context.scene
    scene.frame_start = 0
    scene.frame_end = 96

    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except Exception:
            pass

    bpy.ops.export_scene.fbx(
        filepath=filepath,
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
    print(f"[Export] FBX exportado: {filepath} ({os.path.getsize(filepath)} bytes)")


# ==============================================================================
# 1. GENERACIÓN ANIMACIÓN 3P (A_Player_CraftingBench_Interact)
# ==============================================================================
def produce_3p_animation():
    print("\n=======================================================")
    print(">>> [1/3] GENERANDO ANIMACIÓN 3P CON TWO-BONE IK")
    print("=======================================================")
    bpy.ops.wm.open_mainfile(filepath=PLAYER_BLEND)
    scene = bpy.context.scene
    scene.render.fps = 30

    arm = bpy.data.objects.get("ARM_Player")
    arm.data.pose_position = 'POSE'
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='POSE')

    for pb in arm.pose.bones:
        pb.rotation_mode = 'XYZ'
        pb.rotation_euler = (0, 0, 0)
        pb.location = (0, 0, 0)

    # 1. Crear Targets IK para manos
    target_l = bpy.data.objects.new("IK_Target_L", None)
    target_l.empty_display_type = 'SPHERE'
    target_l.empty_display_size = 0.06
    scene.collection.objects.link(target_l)

    target_r = bpy.data.objects.new("IK_Target_R", None)
    target_r.empty_display_type = 'SPHERE'
    target_r.empty_display_size = 0.06
    scene.collection.objects.link(target_r)

    pole_l = bpy.data.objects.new("IK_Pole_L", None)
    pole_l.empty_display_type = 'CUBE'
    pole_l.empty_display_size = 0.04
    pole_l.location = (-0.60, -0.30, 1.10)
    scene.collection.objects.link(pole_l)

    pole_r = bpy.data.objects.new("IK_Pole_R", None)
    pole_r.empty_display_type = 'CUBE'
    pole_r.empty_display_size = 0.04
    pole_r.location = (0.60, -0.30, 1.10)
    scene.collection.objects.link(pole_r)

    # Configurar Two-Bone IK en forearm_L y forearm_R (simetría biológica)
    pb_fl = arm.pose.bones.get('forearm_L')
    ik_l = pb_fl.constraints.new('IK')
    ik_l.name = "IK_Craft_L"
    ik_l.target = target_l
    ik_l.pole_target = pole_l
    ik_l.pole_angle = R(180)
    ik_l.chain_count = 2

    pb_fr = arm.pose.bones.get('forearm_R')
    ik_r = pb_fr.constraints.new('IK')
    ik_r.name = "IK_Craft_R"
    ik_r.target = target_r
    ik_r.pole_target = pole_r
    ik_r.pole_angle = R(0)
    ik_r.chain_count = 2

    # Puntos espaciales clave (Mesa al frente a Y = +0.75m, fosa/reactor a Y=+0.50m, Z=0.98m)
    REST_L = Vector((-0.28, 0.05, 0.95))
    REST_R = Vector((0.28, 0.05, 0.95))
    
    # Depósito de Scrap: manos juntas directamente sobre la fosa central
    SCRAP_L = Vector((-0.09, 0.45, 0.90))
    SCRAP_R = Vector((0.09, 0.45, 0.90))
    
    # Apertura y contención: manos flanqueando estrechamente el arma (±0.30m en X, Y=+0.50m)
    EXTEND_L = Vector((-0.30, 0.50, 0.98))
    EXTEND_R = Vector((0.30, 0.50, 0.98))

    action_name = "A_Player_CraftingBench_Interact"
    act = bpy.data.actions.new(name=action_name)
    act.use_fake_user = True
    if arm.animation_data is None:
        arm.animation_data_create()
    arm.animation_data.action = act

    # Definir keyframes temporales: (frame, pos_l, pos_r, spine_pitch, chest_pitch, neck_pitch, head_pitch, rot_l, rot_r)
    # En ARM_Player la rotación en X negativa inclina el tronco hacia el frente (+Y)
    timeline = [
        (0,  REST_L,   REST_R,   0.0,   0.0,   0.0,   0.0,  (0, 0, 0),         (0, 0, 0)),
        (12, REST_L*0.5 + SCRAP_L*0.5, REST_R*0.5 + SCRAP_R*0.5, -4.0, -5.0, -5.0, -4.0, (-10, -10, 10), (-10, 10, -10)),
        (25, SCRAP_L,  SCRAP_R,  -8.0, -10.0, -10.0, -8.0, (-15, -20, 20),   (-15, 20, -20)),
        (35, SCRAP_L,  SCRAP_R,  -8.0, -10.0, -10.0, -8.0, (-15, -20, 20),   (-15, 20, -20)),
        (48, EXTEND_L, EXTEND_R, -8.0, -10.0, -10.0, -8.0, (-15, -40, 20),   (-15, 40, -20)),
        (60, EXTEND_L + Vector((0, 0, 0.006)), EXTEND_R + Vector((0, 0, 0.006)), -8.0, -10.0, -10.0, -8.0, (-15, -40, 20), (-15, 40, -20)),
        (72, EXTEND_L - Vector((0, 0, 0.004)), EXTEND_R - Vector((0, 0, 0.004)), -8.0, -10.0, -10.0, -8.0, (-15, -38, 18), (-15, 38, -18)),
        (82, REST_L*0.4 + EXTEND_L*0.6, REST_R*0.4 + EXTEND_R*0.6, -4.0, -5.0, -5.0, -4.0, (-8, -15, 10), (-8, 15, -10)),
        (96, REST_L,   REST_R,   0.0,   0.0,   0.0,   0.0,  (0, 0, 0),         (0, 0, 0))
    ]

    for f, pos_l, pos_r, spine_p, chest_p, neck_p, head_p, h_rot_l, h_rot_r in timeline:
        target_l.location = pos_l
        target_r.location = pos_r
        target_l.keyframe_insert("location", frame=f)
        target_r.keyframe_insert("location", frame=f)

        # Pose de torso y cabeza: inclinación ergonómica hacia adelante mirando hacia el arma (+Y)
        arm.pose.bones['spine'].rotation_euler = (R(spine_p), 0, 0)
        arm.pose.bones['chest'].rotation_euler = (R(chest_p), 0, 0)
        arm.pose.bones['neck'].rotation_euler = (R(neck_p), 0, 0)
        arm.pose.bones['head'].rotation_euler = (R(head_p), 0, 0)

        # Clavículas y muñecas
        arm.pose.bones['clavicle_L'].rotation_euler = (R(abs(chest_p)*0.2), R(chest_p*0.1), R(chest_p*0.2))
        arm.pose.bones['clavicle_R'].rotation_euler = (R(abs(chest_p)*0.2), R(-chest_p*0.1), R(-chest_p*0.2))

        arm.pose.bones['hand_L'].rotation_euler = [R(a) for a in h_rot_l]
        arm.pose.bones['hand_R'].rotation_euler = [R(a) for a in h_rot_r]

        # Inserción de keyframes en huesos de tronco y manos
        for b_name in ['spine', 'chest', 'neck', 'head', 'clavicle_L', 'clavicle_R', 'hand_L', 'hand_R']:
            pb = arm.pose.bones[b_name]
            pb.keyframe_insert("rotation_euler", frame=f)

    # Hornear solución IK con arm ACTIVO
    print("[3P] Activando armature y horneando solución Two-Bone IK...")
    bpy.context.view_layer.objects.active = arm
    if bpy.context.active_object.mode != 'POSE':
        bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.nla.bake(
        frame_start=0,
        frame_end=96,
        step=1,
        only_selected=False,
        visual_keying=True,
        clear_constraints=True,
        bake_types={'POSE'}
    )

    if bpy.context.active_object and bpy.context.active_object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # Eliminar objetos auxiliares IK
    for o in (target_l, target_r, pole_l, pole_r):
        bpy.data.objects.remove(o, do_unlink=True)

    out_fbx_3p = os.path.join(FBX_3P_DIR, "A_Player_CraftingBench_Interact.fbx")
    export_armature_fbx(arm, out_fbx_3p)
    return arm


# ==============================================================================
# 2. GENERACIÓN ANIMACIÓN 1P (A_FPS_CraftingBench_Interact)
# ==============================================================================
def produce_1p_animation():
    print("\n=======================================================")
    print(">>> [2/3] GENERANDO ANIMACIÓN 1P (SK_FPS_Arms)")
    print("=======================================================")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.fps = 30

    bpy.ops.import_scene.fbx(filepath=FPS_FBX)
    arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
    arm.name = "ARM_FPS_Arms"
    fps_mesh = [o for o in bpy.data.objects if o.type == 'MESH'][0]

    # Ocultar geometría de pistola/weapon de los brazos
    for v in fps_mesh.data.vertices:
        for g in v.groups:
            if fps_mesh.vertex_groups[g.group].name in ('weapon', 'cell'):
                v.co = Vector((0, 0, -100))
                break

    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='POSE')
    for pb in arm.pose.bones:
        pb.rotation_mode = 'XYZ'
        pb.rotation_euler = (0, 0, 0)
        pb.location = (0, 0, 0)

    # Targets IK FPS
    target_l = bpy.data.objects.new("FPS_Target_L", None)
    target_l.empty_display_type = 'SPHERE'
    target_l.empty_display_size = 0.05
    scene.collection.objects.link(target_l)

    target_r = bpy.data.objects.new("FPS_Target_R", None)
    target_r.empty_display_type = 'SPHERE'
    target_r.empty_display_size = 0.05
    scene.collection.objects.link(target_r)

    pb_fl = arm.pose.bones.get('forearm_L')
    ik_l = pb_fl.constraints.new('IK')
    ik_l.name = "IK_FPS_L"
    ik_l.target = target_l
    ik_l.chain_count = 2

    pb_fr = arm.pose.bones.get('forearm_R')
    ik_r = pb_fr.constraints.new('IK')
    ik_r.name = "IK_FPS_R"
    ik_r.target = target_r
    ik_r.chain_count = 2

    action_name = "A_FPS_CraftingBench_Interact"
    act = bpy.data.actions.new(name=action_name)
    act.use_fake_user = True
    if arm.animation_data is None:
        arm.animation_data_create()
    arm.animation_data.action = act

    # Posiciones espaciales FPS relativas a la cámara (calibradas para cono de visión FirstPersonCamera FOV=70)
    # Rango visible en viewport: Z entre -0.26 y -0.18, Y entre -0.34 y -0.22
    FPS_REST_L = Vector((-0.18, -0.22, -0.26))
    FPS_REST_R = Vector((0.18, -0.22, -0.26))

    FPS_SCRAP_L = Vector((-0.08, -0.34, -0.20))
    FPS_SCRAP_R = Vector((0.08, -0.34, -0.20))

    FPS_EXTEND_L = Vector((-0.22, -0.30, -0.18))
    FPS_EXTEND_R = Vector((0.22, -0.30, -0.18))

    timeline_fps = [
        (0,  FPS_REST_L,   FPS_REST_R,   (0, 0, 0),        (0, 0, 0)),
        (14, FPS_REST_L*0.4 + FPS_SCRAP_L*0.6, FPS_REST_R*0.4 + FPS_SCRAP_R*0.6, (15, 10, -10), (15, -10, 10)),
        (25, FPS_SCRAP_L,  FPS_SCRAP_R,  (25, 10, -10),    (-15, 15, -20)),
        (35, FPS_SCRAP_L,  FPS_SCRAP_R,  (25, 10, -10),    (-15, 15, -20)),
        (48, FPS_EXTEND_L, FPS_EXTEND_R, (25, 10, -15),    (-15, 20, -25)),
        (60, FPS_EXTEND_L + Vector((0, 0, 0.007)), FPS_EXTEND_R + Vector((0, 0, 0.007)), (25, 10, -15), (-15, 20, -25)),
        (72, FPS_EXTEND_L - Vector((0, 0, 0.004)), FPS_EXTEND_R - Vector((0, 0, 0.004)), (25, 10, -15), (-15, 20, -25)),
        (82, FPS_REST_L*0.4 + FPS_EXTEND_L*0.6, FPS_REST_R*0.4 + FPS_EXTEND_R*0.6, (10, 5, -8), (-8, 10, -12)),
        (96, FPS_REST_L,   FPS_REST_R,   (0, 0, 0),        (0, 0, 0))
    ]

    for f, pos_l, pos_r, h_rot_l, h_rot_r in timeline_fps:
        target_l.location = pos_l
        target_r.location = pos_r
        target_l.keyframe_insert("location", frame=f)
        target_r.keyframe_insert("location", frame=f)

        arm.pose.bones['hand_L'].rotation_euler = [R(a) for a in h_rot_l]
        arm.pose.bones['hand_R'].rotation_euler = [R(a) for a in h_rot_r]
        arm.pose.bones['hand_L'].keyframe_insert("rotation_euler", frame=f)
        arm.pose.bones['hand_R'].keyframe_insert("rotation_euler", frame=f)

    print("[1P] Activando armature y horneando solución IK FPS a curvas...")
    bpy.context.view_layer.objects.active = arm
    if bpy.context.active_object.mode != 'POSE':
        bpy.ops.object.mode_set(mode='POSE')
    bpy.ops.pose.select_all(action='SELECT')
    bpy.ops.nla.bake(
        frame_start=0,
        frame_end=96,
        step=1,
        only_selected=False,
        visual_keying=True,
        clear_constraints=True,
        bake_types={'POSE'}
    )

    if bpy.context.active_object and bpy.context.active_object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    for o in (target_l, target_r):
        bpy.data.objects.remove(o, do_unlink=True)

    out_fbx_fps = os.path.join(FBX_FPS_DIR, "A_FPS_CraftingBench_Interact.fbx")
    export_armature_fbx(arm, out_fbx_fps)
    return arm, fps_mesh


# ==============================================================================
# 3. ENSAMBLAJE DE ESCENA Y RENDERIZADO DEL MOSAICO DE 4 VISTAS (DIRECTIVA 4)
# ==============================================================================
def render_4view_mosaic():
    print("\n=======================================================")
    print(">>> [3/3] CONFIGURANDO ESTUDIO Y RENDERIZANDO MOSAICO DE 4 VISTAS")
    print("=======================================================")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene

    scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, 'RenderSettings') and 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
    scene.render.resolution_x = 1080
    scene.render.resolution_y = 1080
    scene.render.image_settings.file_format = 'PNG'

    scene.view_settings.view_transform = 'AgX' if 'AgX' in [c.name for c in bpy.types.ColorManagedViewSettings.bl_rna.properties['view_transform'].enum_items] else 'Filmic'
    scene.view_settings.look = 'Medium High Contrast'

    # 1. Cargar Mesa de Crafteo
    with bpy.data.libraries.load(BENCH_BLEND) as (df, dt):
        dt.objects = [o for o in df.objects if o.startswith('SM_CraftingBench')]

    bench_objs = []
    for o in dt.objects:
        scene.collection.objects.link(o)
        bench_objs.append(o)

    for o in bench_objs:
        o.rotation_euler = (0, 0, math.pi)
        o.location = (0.0, -0.75, 0.0)

    # 2. Cargar Jugador Canónico en 3P
    with bpy.data.libraries.load(PLAYER_BLEND) as (df, dt):
        dt.objects = ['SK_Player']

    for o in dt.objects:
        scene.collection.objects.link(o)

    player_mesh = bpy.data.objects['SK_Player']

    # Si vino un ARM_Player no animado por dependencia de biblioteca, lo eliminamos
    old_arm = bpy.data.objects.get('ARM_Player')
    if old_arm:
        bpy.data.objects.remove(old_arm, do_unlink=True)

    # Cargar animación 3P horneada FBX
    fbx_3p_path = os.path.join(FBX_3P_DIR, "A_Player_CraftingBench_Interact.fbx")
    bpy.ops.import_scene.fbx(filepath=fbx_3p_path)
    arm_player = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
    arm_player.name = "ARM_Player"
    arm_player.data.pose_position = 'POSE'

    # Vincular visualmente SK_Player a la armadura animada
    player_mesh.parent = arm_player
    for mod in player_mesh.modifiers:
        if mod.type == 'ARMATURE':
            mod.object = arm_player

    # 3. Cargar Brazos FPS para el cuadrante 4
    bpy.ops.import_scene.fbx(filepath=FPS_FBX)
    arm_fps = [o for o in bpy.data.objects if o.type == 'ARMATURE' and o != arm_player][0]
    arm_fps.name = "ARM_FPS_Preview"
    fps_mesh = [o for o in bpy.data.objects if o.type == 'MESH' and o != player_mesh and o not in bench_objs][0]
    fps_mesh.name = "SK_FPS_Preview"

    # Ocultar arma vieja de brazos FPS
    for v in fps_mesh.data.vertices:
        for g in v.groups:
            if fps_mesh.vertex_groups[g.group].name in ('weapon', 'cell'):
                v.co = Vector((0, 0, -100))
                break

    # Cargar animación 1P horneada
    fbx_1p_path = os.path.join(FBX_FPS_DIR, "A_FPS_CraftingBench_Interact.fbx")
    bpy.ops.import_scene.fbx(filepath=fbx_1p_path)
    imported_arm_1p = [o for o in bpy.data.objects if o.type == 'ARMATURE' and o not in (arm_player, arm_fps)][0]
    if arm_fps.animation_data is None:
        arm_fps.animation_data_create()
    if imported_arm_1p.animation_data and imported_arm_1p.animation_data.action:
        arm_fps.animation_data.action = imported_arm_1p.animation_data.action
        if len(imported_arm_1p.animation_data.action.slots) > 0:
            arm_fps.animation_data.action_slot = imported_arm_1p.animation_data.action.slots[0]
    bpy.data.objects.remove(imported_arm_1p, do_unlink=True)

    # Posicionar ARM_FPS_Preview en la altura ocular del jugador (Z=1.60, Y=-0.05) mediante Empty
    fps_root = bpy.data.objects.new("FPS_Rig_Root", None)
    fps_root.location = Vector((0.0, -0.05, 1.60))
    scene.collection.objects.link(fps_root)
    arm_fps.parent = fps_root

    # Situar animación en frame 55 (clímax de manos extendidas y materialización)
    scene.frame_set(55)
    bpy.context.view_layer.update()

    # 4. Añadir Arma Flotante Materializándose en la fosa central (Y = -1.00m, Z = 0.94m)
    vanguard_fbx = os.path.join(ART_DIR, "FBX", "Weapons", "SM_Wep_VanguardAR.fbx")
    if os.path.exists(vanguard_fbx):
        bpy.ops.import_scene.fbx(filepath=vanguard_fbx)
        wep_obj = [o for o in bpy.data.objects if o.name.startswith("SM_Wep_VanguardAR")][0]
    else:
        me_weapon = bpy.data.meshes.new("FloatingWeapon")
        bm_w = bmesh.new()
        bmesh.ops.create_cube(bm_w, size=1.0, matrix=Matrix.Diagonal((0.10, 0.46, 0.16, 1.0)))
        bm_w.to_mesh(me_weapon)
        bm_w.free()
        wep_obj = bpy.data.objects.new("Preview_Materialized_Weapon", me_weapon)
        scene.collection.objects.link(wep_obj)

    wep_obj.location = (0.0, -0.55, 1.02)
    wep_obj.rotation_euler = (R(12), R(-8), R(25))

    # Material Plasma de Arma con brillo cuántico morado
    m_wep = bpy.data.materials.new("M_Preview_WeaponPlasma")
    nt = m_wep.node_tree
    nt.nodes.clear()
    out_w = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf_w = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf_w.inputs['Base Color'].default_value = (0.05, 0.01, 0.12, 1.0)
    bsdf_w.inputs['Metallic'].default_value = 0.90
    bsdf_w.inputs['Roughness'].default_value = 0.12
    bsdf_w.inputs['Emission Color'].default_value = (0.75, 0.18, 1.0, 1.0)
    bsdf_w.inputs['Emission Strength'].default_value = 5.0
    nt.links.new(bsdf_w.outputs['BSDF'], out_w.inputs['Surface'])
    wep_obj.data.materials.clear()
    wep_obj.data.materials.append(m_wep)

    # 5. Destellos morados / chispas en la fosa
    for i in range(12):
        angle = i * (math.pi * 2 / 12)
        rad = 0.14 + (i % 3) * 0.04
        me_spark = bpy.data.meshes.new(f"Spark_{i}")
        bm_s = bmesh.new()
        bmesh.ops.create_icosphere(bm_s, subdivisions=1, radius=0.015 + (i % 2)*0.01)
        bm_s.to_mesh(me_spark)
        bm_s.free()
        sp_obj = bpy.data.objects.new(f"Spark_{i}", me_spark)
        sp_obj.location = (math.cos(angle)*rad, -1.00 + math.sin(angle)*rad, 0.86 + (i % 4)*0.05)
        scene.collection.objects.link(sp_obj)

        m_sp = bpy.data.materials.new(f"M_Spark_{i}")
        emis = m_sp.node_tree.nodes.new('ShaderNodeEmission')
        emis.inputs['Color'].default_value = (0.85, 0.35, 1.0, 1.0)
        emis.inputs['Strength'].default_value = 12.0
        out_s = m_sp.node_tree.nodes.get('Material Output')
        if not out_s:
            out_s = m_sp.node_tree.nodes.new('ShaderNodeOutputMaterial')
        m_sp.node_tree.links.new(emis.outputs['Emission'], out_s.inputs['Surface'])
        sp_obj.data.materials.append(m_sp)

    # 6. Suelo oscuro de estudio
    me_fl = bpy.data.meshes.new("Floor")
    bm_fl = bmesh.new()
    bmesh.ops.create_grid(bm_fl, x_segments=4, y_segments=4, size=24.0)
    bm_fl.to_mesh(me_fl)
    bm_fl.free()
    fl_obj = bpy.data.objects.new("Studio_Floor", me_fl)
    scene.collection.objects.link(fl_obj)

    m_fl = bpy.data.materials.new("M_Floor")
    bsdf_fl = m_fl.node_tree.nodes.get("Principled BSDF")
    if bsdf_fl:
        bsdf_fl.inputs['Base Color'].default_value = (0.015, 0.015, 0.02, 1.0)
        bsdf_fl.inputs['Roughness'].default_value = 0.50
    fl_obj.data.materials.append(m_fl)

    # 7. Iluminación de estudio
    l1 = bpy.data.objects.new("LGT_Key", bpy.data.lights.new("LGT_Key", 'AREA'))
    l1.data.energy = 240.0
    l1.data.size = 2.5
    l1.data.color = (0.96, 0.98, 1.0)
    l1.location = (1.6, -3.2, 2.4)
    l1.rotation_euler = (R(52), R(12), R(35))
    scene.collection.objects.link(l1)

    l2 = bpy.data.objects.new("LGT_Fill", bpy.data.lights.new("LGT_Fill", 'AREA'))
    l2.data.energy = 110.0
    l2.data.size = 2.8
    l2.data.color = (0.85, 0.92, 1.0)
    l2.location = (-2.2, -2.5, 1.8)
    l2.rotation_euler = (R(55), R(-15), R(-40))
    scene.collection.objects.link(l2)

    l_plasma = bpy.data.objects.new("LGT_PlasmaPit", bpy.data.lights.new("LGT_PlasmaPit", 'POINT'))
    l_plasma.data.energy = 75.0
    l_plasma.data.color = (0.78, 0.18, 1.0)
    l_plasma.location = (0.0, -0.55, 0.90)
    scene.collection.objects.link(l_plasma)

    l3 = bpy.data.objects.new("LGT_Rim", bpy.data.lights.new("LGT_Rim", 'AREA'))
    l3.data.energy = 180.0
    l3.data.size = 2.0
    l3.data.color = (0.90, 0.95, 1.0)
    l3.location = (0.0, 1.8, 2.2)
    l3.rotation_euler = (R(-45), 0, R(180))
    scene.collection.objects.link(l3)

    # 8. Cámaras y Renderizado de los 4 Cuadrantes
    cam_data = bpy.data.cameras.new("Cam_Quadrant")
    cam_obj = bpy.data.objects.new("Cam_Quadrant", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    quadrant_specs = [
        {
            'id': 'bench_front_3p',
            'is_fps': False,
            'loc': Vector((0.0, -2.10, 1.35)),
            'target': Vector((0.0, -0.45, 1.05)),
            'lens': 42
        },
        {
            'id': 'bench_perspective_34',
            'is_fps': False,
            'loc': Vector((1.35, -1.35, 1.35)),
            'target': Vector((0.0, -0.45, 1.05)),
            'lens': 40
        },
        {
            'id': 'bench_hands_closeup',
            'is_fps': False,
            'loc': Vector((0.75, 0.45, 1.65)),
            'target': Vector((0.0, -0.65, 0.98)),
            'lens': 35
        },
        {
            'id': 'bench_fps_view',
            'is_fps': True,
            'loc': Vector((0.0, -0.05, 1.62)),
            'target': Vector((0.0, -0.55, 1.00)),
            'lens': 24
        }
    ]

    rendered_images = {}
    for spec in quadrant_specs:
        if spec['is_fps']:
            # Ocultar cuerpo 3P y mostrar brazos FPS
            player_mesh.hide_render = True
            arm_player.hide_render = True
            arm_fps.hide_render = False
            fps_mesh.hide_render = False
        else:
            player_mesh.hide_render = False
            arm_player.hide_render = False
            arm_fps.hide_render = True
            fps_mesh.hide_render = True

        cam_obj.location = spec['loc']
        direction = spec['target'] - cam_obj.location
        cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
        cam_data.lens = spec['lens']

        out_path = os.path.join(BRAIN_DIR, f"{spec['id']}.png")
        scene.render.filepath = out_path
        bpy.ops.render.render(write_still=True)
        rendered_images[spec['id']] = out_path
        print(f"[Render] Cuadrante generado: {out_path}")

    preview_blend = os.path.join(PROJECT_ROOT, r"Saved\Player_Skin_Workspace\DarX_Bench_Interaction_Preview.blend")
    bpy.ops.wm.save_as_mainfile(filepath=preview_blend)
    print(f"[OK] Blend de validación guardado: {preview_blend}")
    return rendered_images


def main():
    print("=================================================================")
    print("   DARX | PIPELINE DE ANIMACIONES DE MESA DE CRAFTEO (1P & 3P)   ")
    print("=================================================================")
    produce_3p_animation()
    produce_1p_animation()
    render_4view_mosaic()
    print("=================================================================")
    print("   PIPELINE DE BLENDER COMPLETADO CON ÉXITO                     ")
    print("=================================================================")


if __name__ == "__main__":
    main()

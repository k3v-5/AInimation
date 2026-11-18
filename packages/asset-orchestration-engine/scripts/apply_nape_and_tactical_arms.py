# -*- coding: utf-8 -*-
"""apply_nape_and_tactical_arms.py
Corrige la nuca de SK_Player eliminando la solapa/chimenea abierta y sellando
la transición occipucio-cervical. Configura la postura táctica de brazos estilo FPS
(elevados al pecho/plexo solar, codos recogidos, ambas manos al frente) para:
- A_Player_Idle
- A_Player_Pistol_Idle
- A_Player_Unarmed_Idle
- A_Player_Walk / A_Player_Run
- A_Player_Unarmed_Walk / A_Player_Unarmed_Run
Exporta SK_Player.fbx y las secuencias de animación a Art/FBX/, y renderiza vistas de validación.
"""

import os
import sys
import math
import bpy
import bmesh
from mathutils import Vector, Matrix, Euler

PROJECT_ROOT = r"E:\Darx_Proyect"
CANONICAL_BLEND = os.path.join(PROJECT_ROOT, "Saved", "Player_Skin_Workspace", "DarX_Player_Rigged_Canonical.blend")
ASSETS_BLEND = os.path.join(PROJECT_ROOT, "Art", "Blender", "DarX_Assets.blend")
FBX_PLAYER = os.path.join(PROJECT_ROOT, "Art", "FBX", "SK_Player.fbx")
FBX_ANIM_DIR = os.path.join(PROJECT_ROOT, "Art", "FBX", "Anim_Player")
OUT_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"

sys.path.append(os.path.join(PROJECT_ROOT, "Art", "Blender"))
import darx_lib as dl

def fix_nape_geometry(mesh):
    """Suaviza y repliega la solapa posterior del cuello para cerrar la cavidad cervical."""
    bm = bmesh.new()
    bm.from_mesh(mesh)
    adjusted_flap = 0
    adjusted_cavity = 0
    
    for v in bm.verts:
        z, y, x = v.co.z, v.co.y, v.co.x
        # 1. Solapa posterior (Z 1.48-1.63, Y > 0.05, |X| < 0.09)
        if 1.48 <= z <= 1.63 and y > 0.05 and abs(x) < 0.09:
            decay = math.exp(-((x / 0.07) ** 2))
            t = (z - 1.48) / (1.63 - 1.48)
            target_y = 0.055 + 0.020 * t
            if y > target_y:
                v.co.y -= (y - target_y) * 0.85 * decay
                adjusted_flap += 1
                
        # 2. Cavidad interior del cuello: expandir hacia atras para sellar con la piel
        if 1.50 <= z <= 1.64 and -0.02 <= y <= 0.05 and abs(x) < 0.06:
            t = (z - 1.50) / (1.64 - 1.50)
            target_fill_y = 0.050 + 0.022 * t
            if y < target_fill_y:
                decay = math.exp(-((x / 0.05) ** 2))
                v.co.y += (target_fill_y - y) * 0.85 * decay
                adjusted_cavity += 1
                
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    print(f"  [OK] Nuca ajustada: {adjusted_flap} verts de solapa replegados, {adjusted_cavity} verts de cavidad sellados.")

def _mix(rots=None, locs=None):
    out = {}
    for k, v in (rots or {}).items():
        out.setdefault(k, {})["rot"] = v
    for k, v in (locs or {}).items():
        out.setdefault(k, {})["loc"] = v
    return out

def export_single_action(arm_obj, action_name, fbx_filename):
    """Exporta una única acción a FBX con convenio canónico."""
    act = bpy.data.actions.get(action_name)
    if not act:
        print(f"  [ERROR] Acción no encontrada: {action_name}")
        return False
        
    arm_obj.data.pose_position = 'POSE'
    arm_obj.animation_data.action = act
    if hasattr(arm_obj.animation_data, "action_slot") and act.slots:
        arm_obj.animation_data.action_slot = act.slots[0]
    f_start = int(act.frame_range[0])
    f_end = int(act.frame_range[1])
    bpy.context.scene.frame_start = f_start
    bpy.context.scene.frame_end = f_end
    bpy.context.scene.frame_set(f_start)
    bpy.context.view_layer.update()
    
    out_path = os.path.join(FBX_ANIM_DIR, fbx_filename)
    if os.path.exists(out_path):
        os.remove(out_path)
        
    bpy.ops.object.select_all(action='DESELECT')
    arm_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj
    
    bpy.ops.export_scene.fbx(
        filepath=out_path,
        use_selection=True,
        global_scale=1.0,
        apply_scale_options='FBX_SCALE_NONE',
        axis_forward='-Y',
        axis_up='Z',
        bake_space_transform=False,
        object_types={'ARMATURE'},
        add_leaf_bones=False,
        primary_bone_axis='Y',
        secondary_bone_axis='X',
        bake_anim=True,
        bake_anim_use_all_actions=False,
        bake_anim_use_nla_strips=False,
        bake_anim_simplify_factor=0.0
    )
    print(f"  [OK] Exportada animación: {fbx_filename} ({os.path.getsize(out_path)} bytes, {f_end - f_start + 1} frames)")
    return True

def main():
    print("==================================================================")
    print("=== [1/5] APLICANDO CORRECCIÓN DE NUCA EN MODELO CANÓNICO ===")
    print("==================================================================")
    bpy.ops.wm.open_mainfile(filepath=CANONICAL_BLEND)
    
    mesh_obj = bpy.data.objects.get('SK_Player')
    arm_obj = bpy.data.objects.get('ARM_Player')
    if not mesh_obj or not arm_obj:
        raise RuntimeError("SK_Player o ARM_Player no encontrados en blend canónico.")
        
    fix_nape_geometry(mesh_obj.data)
    
    # Guardar canonical blend
    bpy.ops.wm.save_as_mainfile(filepath=CANONICAL_BLEND)
    print(f"[OK] Guardado {CANONICAL_BLEND}")
    
    # También aplicar a DarX_Assets.blend si existe SK_Player allí
    try:
        bpy.ops.wm.open_mainfile(filepath=ASSETS_BLEND)
        assets_player = bpy.data.objects.get('SK_Player')
        if assets_player:
            fix_nape_geometry(assets_player.data)
            bpy.ops.wm.save_as_mainfile(filepath=ASSETS_BLEND)
            print(f"[OK] Guardado {ASSETS_BLEND}")
    except Exception as e:
        print(f"[WARN] No se pudo actualizar DarX_Assets.blend: {e}")
        
    # Reabrir canonical blend para trabajar las animaciones y exportar FBX
    bpy.ops.wm.open_mainfile(filepath=CANONICAL_BLEND)
    mesh_obj = bpy.data.objects['SK_Player']
    arm_obj = bpy.data.objects['ARM_Player']

    print("==================================================================")
    print("=== [2/5] EXPORTANDO SK_Player.fbx CANÓNICO ===")
    print("==================================================================")
    arm_obj.data.pose_position = 'REST'
    bpy.context.scene.frame_set(0)
    bpy.context.view_layer.update()
    
    bpy.ops.object.select_all(action='DESELECT')
    arm_obj.select_set(True)
    mesh_obj.select_set(True)
    bpy.context.view_layer.objects.active = arm_obj
    
    if os.path.exists(FBX_PLAYER):
        os.remove(FBX_PLAYER)
        
    bpy.ops.export_scene.fbx(
        filepath=FBX_PLAYER,
        use_selection=True,
        global_scale=1.0,
        apply_scale_options='FBX_SCALE_NONE',
        axis_forward='-Y',
        axis_up='Z',
        bake_space_transform=False,
        object_types={'ARMATURE', 'MESH'},
        use_mesh_modifiers=True,
        mesh_smooth_type='FACE',
        add_leaf_bones=False,
        primary_bone_axis='Y',
        secondary_bone_axis='X',
        bake_anim=False
    )
    print(f"[OK] SK_Player.fbx exportado: {FBX_PLAYER} ({os.path.getsize(FBX_PLAYER)} bytes)")

    print("==================================================================")
    print("=== [3/5] GENERANDO POSTURAS TÁCTICAS FPS EN ANIM_PLAYER ===")
    print("==================================================================")
    if not arm_obj.animation_data:
        arm_obj.animation_data_create()
        
    # Constantes tácticas FPS calibradas empíricamente
    # Brazo derecho: sostiene arma elevada frente al plexo/esternón
    CARGA_HOMBRO = -35.0
    CARGA_CODO = -65.0
    CARGA_ADENTRO = 24.0
    CARGA_FOREARM_Z = 28.0
    
    # Brazo izquierdo armado: guardia táctica / mano de soporte elevada al frente
    IZQ_HOMBRO = -35.0
    IZQ_CODO = -65.0
    IZQ_ADENTRO = -24.0
    IZQ_FOREARM_Z = -28.0
    
    # 1. A_Player_Idle y A_Player_Pistol_Idle (90 frames = 3s bucle suave de respiración)
    idle_keys = {}
    idle_keys[0] = _mix(
        rots={
            "spine": (2, 0, 0), "chest": (1, 0, 0), "head": (0, 0, 0),
            "upperarm_R": (CARGA_HOMBRO, 6, CARGA_ADENTRO),
            "forearm_R": (CARGA_CODO, -6, CARGA_FOREARM_Z),
            "hand_R": (14, 0, 10),
            "upperarm_L": (IZQ_HOMBRO, -6, IZQ_ADENTRO),
            "forearm_L": (IZQ_CODO, 6, IZQ_FOREARM_Z),
            "hand_L": (14, 0, -10),
        },
        locs={"pelvis": (0, 0, 0)}
    )
    idle_keys[45] = _mix(
        rots={
            "spine": (0, 0, 0), "chest": (-1, 0, 0), "head": (-1, 0, 0),
            "upperarm_R": (CARGA_HOMBRO + 2, 6, CARGA_ADENTRO),
            "forearm_R": (CARGA_CODO - 2, -6, CARGA_FOREARM_Z),
            "hand_R": (14, 0, 10),
            "upperarm_L": (IZQ_HOMBRO + 2, -6, IZQ_ADENTRO),
            "forearm_L": (IZQ_CODO - 2, 6, IZQ_FOREARM_Z),
            "hand_L": (14, 0, -10),
        },
        locs={"pelvis": (0, 0, 0.014)}
    )
    idle_keys[90] = idle_keys[0]
    
    dl.action(arm_obj, "A_Player_Idle", 90, idle_keys, interp='BEZIER')
    dl.action(arm_obj, "A_Player_Pistol_Idle", 90, idle_keys, interp='BEZIER')
    print("  [OK] Creadas acciones A_Player_Idle y A_Player_Pistol_Idle")

    # 2. A_Player_Unarmed_Idle (90 frames: guardia marcial táctica con puños al pecho/mentón)
    unarmed_idle_keys = {}
    unarmed_idle_keys[0] = _mix(
        rots={
            "spine": (2, 0, 0), "chest": (1, 0, 0), "head": (0, 0, 0),
            "upperarm_R": (CARGA_HOMBRO, 6, CARGA_ADENTRO),
            "forearm_R": (CARGA_CODO, -6, CARGA_FOREARM_Z),
            "hand_R": (14, 0, 10),
            "upperarm_L": (IZQ_HOMBRO, -6, IZQ_ADENTRO),
            "forearm_L": (IZQ_CODO, 6, IZQ_FOREARM_Z),
            "hand_L": (14, 0, -10),
        },
        locs={"pelvis": (0, 0, 0)}
    )
    unarmed_idle_keys[45] = _mix(
        rots={
            "spine": (0, 0, 0), "chest": (-1, 0, 0), "head": (-1, 0, 0),
            "upperarm_R": (CARGA_HOMBRO + 2, 6, CARGA_ADENTRO),
            "forearm_R": (CARGA_CODO - 2, -6, CARGA_FOREARM_Z),
            "hand_R": (14, 0, 10),
            "upperarm_L": (IZQ_HOMBRO + 2, -6, IZQ_ADENTRO),
            "forearm_L": (IZQ_CODO - 2, 6, IZQ_FOREARM_Z),
            "hand_L": (14, 0, -10),
        },
        locs={"pelvis": (0, 0, 0.014)}
    )
    unarmed_idle_keys[90] = unarmed_idle_keys[0]
    dl.action(arm_obj, "A_Player_Unarmed_Idle", 90, unarmed_idle_keys, interp='BEZIER')
    print("  [OK] Creada acción A_Player_Unarmed_Idle")

    # 3. A_Player_Walk y A_Player_Run (con guardia alta en brazos)
    def _brazos_tacticos(brazo_R, brazo_L):
        return {
            "upperarm_R": (CARGA_HOMBRO + brazo_R * 0.20, 6, CARGA_ADENTRO),
            "forearm_R": (CARGA_CODO, -6, CARGA_FOREARM_Z),
            "hand_R": (14, 0, 10),
            "upperarm_L": (IZQ_HOMBRO + brazo_L * 0.20, -6, IZQ_ADENTRO),
            "forearm_L": (IZQ_CODO, 6, IZQ_FOREARM_Z),
            "hand_L": (14, 0, -10),
        }

    def _paso_tactico(m_r, r_r, m_l, r_l, b_r, b_l, cad_z=0.0, inc=0.0):
        rots = {
            "thigh_R": (m_r, 0, 0), "calf_R": (r_r, 0, 0),
            "thigh_L": (m_l, 0, 0), "calf_L": (r_l, 0, 0),
            "spine": (inc, 0, 0),
        }
        rots.update(_brazos_tacticos(b_r, b_l))
        return _mix(rots=rots, locs={"pelvis": (0, 0, cad_z)})

    walk_keys = {
        0:  _paso_tactico(-24, 4, 22, 26, 10, -10, 0.000, 3),
        7:  _paso_tactico(-6, 22, 4, 8, 4, -4, -0.020, 3),
        15: _paso_tactico(22, 26, -24, 4, -10, 10, 0.000, 3),
        22: _paso_tactico(4, 8, -6, 22, -4, 4, -0.020, 3),
        30: _paso_tactico(-24, 4, 22, 26, 10, -10, 0.000, 3),
    }
    dl.action(arm_obj, "A_Player_Walk", 30, walk_keys, interp='BEZIER')

    run_keys = {
        0:  _paso_tactico(-42, 8, 34, 62, 16, -16, 0.000, 12),
        5:  _paso_tactico(-10, 46, 6, 16, 6, -6, -0.042, 12),
        11: _paso_tactico(34, 62, -42, 8, -16, 16, 0.000, 12),
        16: _paso_tactico(6, 16, -10, 46, -6, 6, -0.042, 12),
        22: _paso_tactico(-42, 8, 34, 62, 16, -16, 0.000, 12),
    }
    dl.action(arm_obj, "A_Player_Run", 22, run_keys, interp='BEZIER')
    print("  [OK] Creadas acciones A_Player_Walk y A_Player_Run con brazos tácticos.")

    # 4. A_Player_Unarmed_Walk y A_Player_Unarmed_Run (puños en guardia durante el desplazamiento)
    def _brazos_unarmed_loco(b_r, b_l):
        return {
            "upperarm_R": (CARGA_HOMBRO + b_r * 0.20, 6, CARGA_ADENTRO),
            "forearm_R": (CARGA_CODO, -6, CARGA_FOREARM_Z),
            "hand_R": (14, 0, 10),
            "upperarm_L": (IZQ_HOMBRO + b_l * 0.20, -6, IZQ_ADENTRO),
            "forearm_L": (IZQ_CODO, 6, IZQ_FOREARM_Z),
            "hand_L": (14, 0, -10),
        }

    def _paso_unarmed(m_r, r_r, m_l, r_l, b_r, b_l, cad_z=0.0, inc=0.0):
        rots = {
            "thigh_R": (m_r, 0, 0), "calf_R": (r_r, 0, 0),
            "thigh_L": (m_l, 0, 0), "calf_L": (r_l, 0, 0),
            "spine": (inc, 0, 0),
        }
        rots.update(_brazos_unarmed_loco(b_r, b_l))
        return _mix(rots=rots, locs={"pelvis": (0, 0, cad_z)})

    unarmed_walk_keys = {
        0:  _paso_unarmed(-24, 4, 22, 26, 12, -12, 0.000, 3),
        7:  _paso_unarmed(-6, 22, 4, 8, 4, -4, -0.020, 3),
        15: _paso_unarmed(22, 26, -24, 4, -12, 12, 0.000, 3),
        22: _paso_unarmed(4, 8, -6, 22, -4, 4, -0.020, 3),
        30: _paso_unarmed(-24, 4, 22, 26, 12, -12, 0.000, 3),
    }
    dl.action(arm_obj, "A_Player_Unarmed_Walk", 30, unarmed_walk_keys, interp='BEZIER')

    unarmed_run_keys = {
        0:  _paso_unarmed(-42, 8, 34, 62, 24, -24, 0.000, 12),
        5:  _paso_unarmed(-10, 46, 6, 16, 8, -8, -0.042, 12),
        11: _paso_unarmed(34, 62, -42, 8, -24, 24, 0.000, 12),
        16: _paso_unarmed(6, 16, -10, 46, -8, 8, -0.042, 12),
        22: _paso_unarmed(-42, 8, 34, 62, 24, -24, 0.000, 12),
    }
    dl.action(arm_obj, "A_Player_Unarmed_Run", 22, unarmed_run_keys, interp='BEZIER')
    print("  [OK] Creadas acciones A_Player_Unarmed_Walk y A_Player_Unarmed_Run con puños en guardia.")

    print("==================================================================")
    print("=== [4/5] EXPORTANDO FBX DE ANIMACIONES A Art/FBX/Anim_Player ===")
    print("==================================================================")
    os.makedirs(FBX_ANIM_DIR, exist_ok=True)
    anims_to_export = [
        ("A_Player_Idle", "A_Player_Idle.fbx"),
        ("A_Player_Pistol_Idle", "A_Player_Pistol_Idle.fbx"),
        ("A_Player_Unarmed_Idle", "A_Player_Unarmed_Idle.fbx"),
        ("A_Player_Walk", "A_Player_Walk.fbx"),
        ("A_Player_Run", "A_Player_Run.fbx"),
        ("A_Player_Unarmed_Walk", "A_Player_Unarmed_Walk.fbx"),
        ("A_Player_Unarmed_Run", "A_Player_Unarmed_Run.fbx"),
    ]
    for act_name, fbx_name in anims_to_export:
        export_single_action(arm_obj, act_name, fbx_name)

    # Guardar blend canónico con las nuevas animaciones
    bpy.ops.wm.save_as_mainfile(filepath=CANONICAL_BLEND)
    print(f"[OK] Master blend guardado con nuevas animaciones: {CANONICAL_BLEND}")

    print("==================================================================")
    print("=== [5/5] RENDERIZANDO PREVISUALIZACIONES DE VALIDACIÓN ===")
    print("==================================================================")
    # Posear en A_Player_Pistol_Idle y renderizar
    arm_obj.data.pose_position = 'POSE'
    act_pistol = bpy.data.actions.get("A_Player_Pistol_Idle")
    arm_obj.animation_data.action = act_pistol
    if hasattr(arm_obj.animation_data, "action_slot") and act_pistol.slots:
        arm_obj.animation_data.action_slot = act_pistol.slots[0]
    bpy.context.scene.frame_set(0)
    bpy.context.view_layer.update()
    
    scene = bpy.context.scene
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 768
    scene.render.resolution_y = 1024

    for o in list(scene.collection.objects):
        if o.type in ('LIGHT', 'CAMERA'):
            bpy.data.objects.remove(o, do_unlink=True)

    world = scene.world or bpy.data.worlds.new('StudioWorld')
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get('Background')
    if bg:
        bg.inputs['Color'].default_value = (0.08, 0.09, 0.12, 1.0)
        bg.inputs['Strength'].default_value = 1.0

    l_key = bpy.data.lights.new('Key', 'SUN')
    l_key.energy = 4.0
    o_key = bpy.data.objects.new('Key', l_key)
    o_key.rotation_euler = (math.radians(-50), math.radians(25), math.radians(160))
    scene.collection.objects.link(o_key)

    l_fill = bpy.data.lights.new('Fill', 'SUN')
    l_fill.energy = 2.5
    l_fill.color = (0.80, 0.88, 1.0)
    o_fill = bpy.data.objects.new('Fill', l_fill)
    o_fill.rotation_euler = (math.radians(35), math.radians(-30), math.radians(-45))
    scene.collection.objects.link(o_fill)

    cam_data = bpy.data.cameras.new('Cam')
    cam_obj = bpy.data.objects.new('Cam', cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    for o in bpy.data.objects:
        if o.type == 'MESH':
            o.hide_render = (o.name != 'SK_Player')

    def render_view(name, loc, target, fov=30):
        cam_data.lens_unit = 'FOV'
        cam_data.angle = math.radians(fov)
        cam_obj.location = Vector(loc)
        d = Vector(target) - Vector(loc)
        cam_obj.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
        p = os.path.join(OUT_DIR, f"{name}.png")
        scene.render.filepath = p
        bpy.ops.render.render(write_still=True)
        print(f"  [OK] Render guardado: {p}")
        return p

    # 1. Vista exacta al screenshot del usuario (trasera 3/4 mostrando nuca lisa y brazo izquierdo en guardia táctica)
    render_view("validation_nape_tactical_user_angle", (0.55, 1.35, 1.55), (0.0, -0.05, 1.35), fov=28)
    
    # 2. Vista trasera completa (nuca limpia y simétrica, hombros y espalda)
    render_view("validation_nape_tactical_back", (0.0, 1.7, 1.55), (0.0, 0.0, 1.45), fov=28)
    
    # 3. Vista frontal mostrando ambos brazos en guardia táctica FPS
    render_view("validation_arms_tactical_front", (0.0, -2.0, 1.35), (0.0, 0.0, 1.25), fov=30)
    
    # 4. Vista de perfil
    render_view("validation_profile_tactical", (1.7, 0.0, 1.45), (0.0, 0.0, 1.35), fov=28)

    print("=== PIPELINE BLENDER COMPLETADO AL 100% ===")

if __name__ == "__main__":
    main()

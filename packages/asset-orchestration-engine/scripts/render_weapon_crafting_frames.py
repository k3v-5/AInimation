"""render_weapon_crafting_frames.py
================================================================================
RENDERIZADO EN LOTE DE STORYBOARDS DE ANIMACIÓN Y MATERIALIZACIÓN DE ARMAS
================================================================================
Genera la secuencia multi-frame de la interacción con la Mesa de Crafteo para
cada una de las cuatro armas principales de DarX:
1. Escopeta Pesada (SM_Wep_BreacherS4)
2. Subfusil Cuántico (SM_Wep_PhaseSMG)
3. Pistola Láser (SM_Wep_Apex6)
4. Rifle de Asalto (SM_Wep_VanguardAR)

Por cada arma se generan 4 momentos clave:
- Frame 20: Depósito bimanual de Scrap en la fosa central (mesa iniciando encendido).
- Frame 45: Apertura bimanual hacia los marcos laterales y vórtice de plasma violeta.
- Frame 60: Materialización completa 3P del arma levitando sobre la fosa.
- Frame 65: Perspectiva ocular en Primera Persona (FPS) con brazos sobre la mesa.

Los 4 frames se ensamblan mediante Pillow en un storyboard 2x2 de 2160x2280 con rotulación HUD.
"""

import os
import sys
import math
import bpy
import bmesh
from mathutils import Vector, Euler, Matrix

R = math.radians

# Rutas del proyecto
PROJECT_ROOT = r"E:\Darx_Proyect"
ART_DIR = os.path.join(PROJECT_ROOT, "Art")
FBX_WEAPONS_DIR = os.path.join(ART_DIR, "FBX", "Weapons")
FBX_FPS_DIR = os.path.join(ART_DIR, "FBX", "Anim_FPS")
FBX_3P_DIR = os.path.join(ART_DIR, "FBX", "Anim_Player")
BRAIN_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"

BENCH_BLEND = os.path.join(PROJECT_ROOT, r"Saved\Player_Skin_Workspace\DarX_CraftingBench_Master.blend")
PLAYER_BLEND = os.path.join(PROJECT_ROOT, r"Saved\Player_Skin_Workspace\DarX_Player_Rigged_Canonical.blend")
FPS_FBX = os.path.join(ART_DIR, "FBX", "SK_FPS_Arms.fbx")

TEMP_RENDER_DIR = os.path.join(BRAIN_DIR, "temp_crafting_renders")
os.makedirs(TEMP_RENDER_DIR, exist_ok=True)
os.makedirs(BRAIN_DIR, exist_ok=True)

WEAPON_CATALOG = [
    {
        'id': 'escopeta',
        'name': 'ESCOPETA BREACHER-S4',
        'sub': 'Calibre Cuántico Pesado // Dispersión de Pulso',
        'fbx': os.path.join(FBX_WEAPONS_DIR, 'SM_Wep_BreacherS4.fbx'),
        'mesh_name': 'SM_Wep_BreacherS4',
        'scale': 1.0,
        'offset_z': 0.0,
        'storyboard': os.path.join(BRAIN_DIR, 'storyboard_escopeta.png')
    },
    {
        'id': 'subfusil',
        'name': 'SUBFUSIL PHASE-SMG',
        'sub': 'Cadencia Cuántica // Tambor de Plasma y Fuga de Fase',
        'fbx': os.path.join(FBX_WEAPONS_DIR, 'SM_Wep_PhaseSMG.fbx'),
        'mesh_name': 'SM_Wep_PhaseSMG',
        'scale': 0.95,
        'offset_z': -0.01,
        'storyboard': os.path.join(BRAIN_DIR, 'storyboard_subfusil.png')
    },
    {
        'id': 'pistola',
        'name': 'PISTOLA APEX-6',
        'sub': 'Disipador Láser Compacto // Recámara de Alta Tensión',
        'fbx': os.path.join(FBX_WEAPONS_DIR, 'SM_Wep_Apex6.fbx'),
        'mesh_name': 'SM_Wep_Apex6',
        'scale': 1.15,
        'offset_z': -0.03,
        'storyboard': os.path.join(BRAIN_DIR, 'storyboard_pistola.png')
    },
    {
        'id': 'rifle',
        'name': 'RIFLE VANGUARD-AR',
        'sub': 'Asalto Cinético // Cañón Magnetizado y Núcleo de Plasma',
        'fbx': os.path.join(FBX_WEAPONS_DIR, 'SM_Wep_VanguardAR.fbx'),
        'mesh_name': 'SM_Wep_VanguardAR',
        'scale': 1.0,
        'offset_z': 0.0,
        'storyboard': os.path.join(BRAIN_DIR, 'storyboard_rifle.png')
    }
]


def setup_base_scene():
    """Configura la escena base: mesa de crafteo, jugador 3P con Two-Bone IK, brazos 1P, suelo e iluminación."""
    # 1. Abrir directamente el archivo maestro del jugador canónico para preservar todos sus pesos y modificadores
    bpy.ops.wm.open_mainfile(filepath=PLAYER_BLEND)
    scene = bpy.context.scene

    scene.render.engine = 'BLENDER_EEVEE_NEXT' if hasattr(bpy.types, 'RenderSettings') and 'BLENDER_EEVEE_NEXT' in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items] else 'BLENDER_EEVEE'
    scene.render.resolution_x = 1080
    scene.render.resolution_y = 1080
    scene.render.image_settings.file_format = 'PNG'

    scene.view_settings.view_transform = 'AgX' if 'AgX' in [c.name for c in bpy.types.ColorManagedViewSettings.bl_rna.properties['view_transform'].enum_items] else 'Filmic'
    scene.view_settings.look = 'Medium High Contrast'

    player_mesh = bpy.data.objects['SK_Player']
    arm_player = bpy.data.objects['ARM_Player']
    arm_player.data.pose_position = 'POSE'

    # Configurar Two-Bone IK en el personaje canónico
    bpy.context.view_layer.objects.active = arm_player
    bpy.ops.object.mode_set(mode='POSE')

    target_l = bpy.data.objects.new("IK_Target_L", None)
    target_l.empty_display_type = 'SPHERE'
    target_l.empty_display_size = 0.05
    scene.collection.objects.link(target_l)

    target_r = bpy.data.objects.new("IK_Target_R", None)
    target_r.empty_display_type = 'SPHERE'
    target_r.empty_display_size = 0.05
    scene.collection.objects.link(target_r)

    pole_l = bpy.data.objects.new("IK_Pole_L", None)
    pole_l.empty_display_type = 'CUBE'
    pole_l.empty_display_size = 0.03
    pole_l.location = (-0.60, -0.15, 1.10)
    scene.collection.objects.link(pole_l)

    pole_r = bpy.data.objects.new("IK_Pole_R", None)
    pole_r.empty_display_type = 'CUBE'
    pole_r.empty_display_size = 0.03
    pole_r.location = (0.60, -0.15, 1.10)
    scene.collection.objects.link(pole_r)

    ik_l = arm_player.pose.bones['forearm_L'].constraints.new('IK')
    ik_l.target = target_l
    ik_l.pole_target = pole_l
    ik_l.pole_angle = R(180)
    ik_l.chain_count = 2

    ik_r = arm_player.pose.bones['forearm_R'].constraints.new('IK')
    ik_r.target = target_r
    ik_r.pole_target = pole_r
    ik_r.pole_angle = R(0)
    ik_r.chain_count = 2

    for b in ['spine', 'chest', 'neck', 'head', 'hand_L', 'hand_R']:
        arm_player.pose.bones[b].rotation_mode = 'XYZ'

    # Inclinación ergonómica natural del torso hacia adelante (+Y) hacia la mesa de trabajo
    arm_player.pose.bones['spine'].rotation_euler = (R(-8.0), 0, 0)
    arm_player.pose.bones['chest'].rotation_euler = (R(-10.0), 0, 0)
    arm_player.pose.bones['neck'].rotation_euler = (R(-8.0), 0, 0)
    arm_player.pose.bones['head'].rotation_euler = (R(-6.0), 0, 0)

    bpy.ops.object.mode_set(mode='OBJECT')

    # 2. Cargar Mesa de Crafteo
    with bpy.data.libraries.load(BENCH_BLEND) as (df, dt):
        dt.objects = [o for o in df.objects if o.startswith('SM_CraftingBench')]

    bench_objs = []
    for o in dt.objects:
        scene.collection.objects.link(o)
        bench_objs.append(o)

    # Mesa en Y = +0.75m con orientación frontal hacia el jugador (HoloHUD al fondo mirando hacia el jugador)
    for o in bench_objs:
        o.rotation_euler = (0, 0, 0)
        o.location = (0.0, 0.75, 0.0)

    # 3. Configuración para vistas FPS (1P): Máscara de brazos limpios y luz POV dedicada
    vg_fps = player_mesh.vertex_groups.new(name="FPS_Arms_Clean")
    for v in player_mesh.data.vertices:
        weight = 0.0
        for g in v.groups:
            vg_name = player_mesh.vertex_groups[g.group].name
            if vg_name in ['forearm_R', 'hand_R', 'forearm_L', 'hand_L']:
                weight = max(weight, g.weight)
        if weight > 0.05:
            vg_fps.add([v.index], weight, 'REPLACE')

    mask_mod = player_mesh.modifiers.new(name="FPS_Mask", type='MASK')
    mask_mod.vertex_group = "FPS_Arms_Clean"
    mask_mod.show_render = False

    l_pov = bpy.data.objects.new("LGT_POV_Hands", bpy.data.lights.new("LGT_POV_Hands", 'POINT'))
    l_pov.data.energy = 0.0
    l_pov.data.color = (0.92, 0.96, 1.0)
    l_pov.data.shadow_soft_size = 0.2
    l_pov.location = (0.0, 0.15, 1.65)
    scene.collection.objects.link(l_pov)

    # 4. Prop de Chatarra / Cubos de Scrap para Frame 20
    me_scrap = bpy.data.meshes.new("Scrap_Canister")
    bm_sc = bmesh.new()
    bmesh.ops.create_cube(bm_sc, size=1.0, matrix=Matrix.Diagonal((0.14, 0.14, 0.10, 1.0)))
    bm_sc.to_mesh(me_scrap)
    bm_sc.free()
    scrap_obj = bpy.data.objects.new("Prop_Scrap_Canister", me_scrap)
    scrap_obj.location = (0.0, 0.45, 0.90)
    scene.collection.objects.link(scrap_obj)

    m_scrap = bpy.data.materials.new("M_Scrap_Canister")
    bsdf_sc = m_scrap.node_tree.nodes.get("Principled BSDF")
    if bsdf_sc:
        bsdf_sc.inputs['Base Color'].default_value = (0.12, 0.14, 0.16, 1.0)
        bsdf_sc.inputs['Metallic'].default_value = 0.85
        bsdf_sc.inputs['Roughness'].default_value = 0.25
        bsdf_sc.inputs['Emission Color'].default_value = (0.2, 0.7, 1.0, 1.0)
        bsdf_sc.inputs['Emission Strength'].default_value = 4.0
    scrap_obj.data.materials.append(m_scrap)

    # 5. Destellos morados / chispas cuánticas
    sparks = []
    for i in range(12):
        angle = i * (math.pi * 2 / 12)
        rad = 0.15 + (i % 3) * 0.04
        me_spark = bpy.data.meshes.new(f"Spark_{i}")
        bm_s = bmesh.new()
        bmesh.ops.create_icosphere(bm_s, subdivisions=1, radius=0.015 + (i % 2) * 0.01)
        bm_s.to_mesh(me_spark)
        bm_s.free()
        sp_obj = bpy.data.objects.new(f"Spark_{i}", me_spark)
        sp_obj.location = (math.cos(angle) * rad, 0.50 + math.sin(angle) * rad, 0.95 + (i % 4) * 0.03)
        scene.collection.objects.link(sp_obj)

        m_sp = bpy.data.materials.new(f"M_Spark_{i}")
        emis = m_sp.node_tree.nodes.new('ShaderNodeEmission')
        emis.inputs['Color'].default_value = (0.85, 0.35, 1.0, 1.0)
        emis.inputs['Strength'].default_value = 14.0
        out_s = m_sp.node_tree.nodes.get('Material Output')
        if not out_s:
            out_s = m_sp.node_tree.nodes.new('ShaderNodeOutputMaterial')
        m_sp.node_tree.links.new(emis.outputs['Emission'], out_s.inputs['Surface'])
        sp_obj.data.materials.append(m_sp)
        sparks.append(sp_obj)

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
        bsdf_fl.inputs['Base Color'].default_value = (0.02, 0.02, 0.03, 1.0)
        bsdf_fl.inputs['Roughness'].default_value = 0.50
    fl_obj.data.materials.append(m_fl)

    # 7. Luces de estudio optimizadas para vista Over-The-Shoulder y Hero
    l_key = bpy.data.objects.new("LGT_Key", bpy.data.lights.new("LGT_Key", 'AREA'))
    l_key.data.energy = 380.0
    l_key.data.size = 2.4
    l_key.data.color = (0.96, 0.98, 1.0)
    l_key.location = (1.4, -0.6, 2.3)
    l_key.rotation_euler = (R(45), R(15), R(35))
    scene.collection.objects.link(l_key)

    l_fill = bpy.data.objects.new("LGT_Fill", bpy.data.lights.new("LGT_Fill", 'AREA'))
    l_fill.data.energy = 160.0
    l_fill.data.size = 2.8
    l_fill.data.color = (0.85, 0.92, 1.0)
    l_fill.location = (-1.8, -0.6, 2.0)
    l_fill.rotation_euler = (R(45), R(-15), R(-35))
    scene.collection.objects.link(l_fill)

    l_plasma = bpy.data.objects.new("LGT_PlasmaPit", bpy.data.lights.new("LGT_PlasmaPit", 'POINT'))
    l_plasma.data.energy = 110.0
    l_plasma.data.color = (0.80, 0.20, 1.0)
    l_plasma.location = (0.0, 0.50, 0.92)
    scene.collection.objects.link(l_plasma)

    l_sun = bpy.data.objects.new("LGT_Sun", bpy.data.lights.new("LGT_Sun", 'SUN'))
    l_sun.data.energy = 3.5
    l_sun.location = (2, -2, 5)
    l_sun.rotation_euler = (R(45), R(15), R(30))
    scene.collection.objects.link(l_sun)

    # 8. Cámara principal
    cam_data = bpy.data.cameras.new("Cam_Storyboard")
    cam_obj = bpy.data.objects.new("Cam_Storyboard", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    return {
        'player_mesh': player_mesh,
        'arm_player': arm_player,
        'target_l': target_l,
        'target_r': target_r,
        'mask_mod': mask_mod,
        'l_pov': l_pov,
        'scrap_obj': scrap_obj,
        'sparks': sparks,
        'l_plasma': l_plasma,
        'cam_obj': cam_obj,
        'cam_data': cam_data
    }


def render_weapon_storyboard(scene_elements, wep_info):
    """Renderiza los 4 frames clave para un arma específica y genera su storyboard 2x2."""
    scene = bpy.context.scene
    player_mesh = scene_elements['player_mesh']
    arm_player = scene_elements['arm_player']
    target_l = scene_elements['target_l']
    target_r = scene_elements['target_r']
    mask_mod = scene_elements['mask_mod']
    l_pov = scene_elements['l_pov']
    scrap_obj = scene_elements['scrap_obj']
    sparks = scene_elements['sparks']
    l_plasma = scene_elements['l_plasma']
    cam_obj = scene_elements['cam_obj']
    cam_data = scene_elements['cam_data']

    print(f"\n=================================================================")
    print(f">>> PROCESANDO ARMA: {wep_info['name']}")
    print(f"=================================================================")

    # Cargar FBX del arma
    bpy.ops.import_scene.fbx(filepath=wep_info['fbx'])
    wep_mesh = [o for o in bpy.data.objects if o.name.startswith(wep_info['mesh_name']) and o.type == 'MESH'][0]
    
    # Orientación horizontal sobre la mesa: el arma levita paralelamente a la superficie con el lateral visible a la cámara
    wep_mesh.location = Vector((0.0, 0.50, 1.05 + wep_info['offset_z']))
    wep_mesh.rotation_euler = (0, 0, R(75))
    wep_mesh.scale = Vector((wep_info['scale'], wep_info['scale'], wep_info['scale']))

    # Crear material cuántico de génesis / plasma translúcido para Frame 45
    m_genesis = bpy.data.materials.new("M_Genesis_Plasma")
    m_genesis.blend_method = 'BLEND'
    nt_g = m_genesis.node_tree
    nt_g.nodes.clear()
    out_g = nt_g.nodes.new('ShaderNodeOutputMaterial')
    bsdf_g = nt_g.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf_g.inputs['Base Color'].default_value = (0.6, 0.1, 0.9, 0.65)
    bsdf_g.inputs['Metallic'].default_value = 0.5
    bsdf_g.inputs['Roughness'].default_value = 0.1
    bsdf_g.inputs['Emission Color'].default_value = (0.85, 0.25, 1.0, 1.0)
    bsdf_g.inputs['Emission Strength'].default_value = 12.0
    bsdf_g.inputs['Alpha'].default_value = 0.70
    nt_g.links.new(bsdf_g.outputs['BSDF'], out_g.inputs['Surface'])

    # Guardar materiales originales
    orig_materials = [m for m in wep_mesh.data.materials]

    # Cámara Over-The-Shoulder (3P): detrás-derecha del jugador mirando hacia la mesa
    ots_cam_loc = Vector((0.82, -0.85, 1.60))
    ots_cam_tgt = Vector((0.0, 0.45, 1.00))

    # Especificación de los 4 momentos clave del storyboard
    moments = [
        {
            'panel_idx': 1,
            'frame': 20,
            'is_fps': False,
            'title': 'FRAME 20 | 1. DEPOSITO DE SCRAP',
            'desc': 'Convergencia bimanual en la fosa central y deposito de modulos de datos.',
            'target_l': Vector((-0.09, 0.45, 0.90)),
            'target_r': Vector((0.09, 0.45, 0.90)),
            'rot_l': (R(-15), R(-20), R(20)),
            'rot_r': (R(-15), R(20), R(-20)),
            'cam_loc': ots_cam_loc,
            'cam_tgt': ots_cam_tgt,
            'cam_lens': 35,
            'show_scrap': True,
            'show_weapon': False,
            'plasma_energy': 35.0,
            'sparks_visible': False,
            'use_genesis_mat': False
        },
        {
            'panel_idx': 2,
            'frame': 45,
            'is_fps': False,
            'title': 'FRAME 45 | 2. ENERGIZACION Y APERTURA',
            'desc': 'Manos extendidas a los marcos exteriores, estallido de plasma y genesis del arma.',
            'target_l': Vector((-0.35, 0.48, 0.98)),
            'target_r': Vector((0.35, 0.48, 0.98)),
            'rot_l': (R(-15), R(-35), R(20)),
            'rot_r': (R(-15), R(35), R(-20)),
            'cam_loc': ots_cam_loc,
            'cam_tgt': ots_cam_tgt,
            'cam_lens': 35,
            'show_scrap': False,
            'show_weapon': True,
            'plasma_energy': 220.0,
            'sparks_visible': True,
            'use_genesis_mat': True
        },
        {
            'panel_idx': 3,
            'frame': 60,
            'is_fps': False,
            'title': f"FRAME 60 | 3. MATERIALIZACION 3P ({wep_info['id'].upper()})",
            'desc': 'Contencion bimanual sobre los marcos laterales con el arma final levitando.',
            'target_l': Vector((-0.30, 0.50, 1.02)),
            'target_r': Vector((0.30, 0.50, 1.02)),
            'rot_l': (R(-10), R(-25), R(15)),
            'rot_r': (R(-10), R(25), R(-15)),
            'cam_loc': ots_cam_loc,
            'cam_tgt': ots_cam_tgt,
            'cam_lens': 35,
            'show_scrap': False,
            'show_weapon': True,
            'plasma_energy': 110.0,
            'sparks_visible': True,
            'use_genesis_mat': False
        },
        {
            'panel_idx': 4,
            'frame': 65,
            'is_fps': True,
            'title': 'FRAME 65 | 4. VISTA OCULAR FPS (1P)',
            'desc': 'Perspectiva ocular del jugador: brazos extendidos sobre la mesa y arma terminada.',
            'target_l': Vector((-0.30, 0.50, 1.02)),
            'target_r': Vector((0.30, 0.50, 1.02)),
            'rot_l': (R(-10), R(-25), R(15)),
            'rot_r': (R(-10), R(25), R(-15)),
            'cam_loc': Vector((0.0, 0.08, 1.50)),
            'cam_tgt': Vector((0.0, 0.50, 1.02)),
            'cam_lens': 26,
            'show_scrap': False,
            'show_weapon': True,
            'plasma_energy': 95.0,
            'sparks_visible': True,
            'use_genesis_mat': False
        }
    ]

    rendered_panel_files = []

    for m in moments:
        scene.frame_set(m['frame'])

        # Configuración de visibilidad y máscara según modo 1P / 3P
        if m['is_fps']:
            mask_mod.show_render = True
            l_pov.data.energy = 90.0
        else:
            mask_mod.show_render = False
            l_pov.data.energy = 0.0

        player_mesh.hide_render = False
        arm_player.hide_render = False

        # Actualizar posición y rotación de manos IK
        target_l.location = m['target_l']
        target_r.location = m['target_r']
        arm_player.pose.bones['hand_L'].rotation_euler = m['rot_l']
        arm_player.pose.bones['hand_R'].rotation_euler = m['rot_r']

        # Visibilidad del scrap
        scrap_obj.hide_render = not m['show_scrap']

        # Visibilidad y material del arma
        wep_mesh.hide_render = not m['show_weapon']
        if m['use_genesis_mat']:
            wep_mesh.data.materials.clear()
            wep_mesh.data.materials.append(m_genesis)
        else:
            wep_mesh.data.materials.clear()
            for mat in orig_materials:
                wep_mesh.data.materials.append(mat)

        # Destellos y energía de plasma
        l_plasma.data.energy = m['plasma_energy']
        for sp in sparks:
            sp.hide_render = not m['sparks_visible']

        # Configurar Cámara
        cam_obj.location = m['cam_loc']
        direction = m['cam_tgt'] - cam_obj.location
        cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
        cam_data.lens = m['cam_lens']

        # Renderizar panel individual
        out_name = f"{wep_info['id']}_panel_{m['panel_idx']}.png"
        out_path = os.path.join(TEMP_RENDER_DIR, out_name)
        scene.render.filepath = out_path

        print(f"  -> Renderizando {wep_info['id']} | Panel {m['panel_idx']} (Frame {m['frame']})...")
        bpy.ops.render.render(write_still=True)
        rendered_panel_files.append(out_path)

    # Limpiar objeto arma tras completar sus renders
    bpy.data.objects.remove(wep_mesh, do_unlink=True)
    return rendered_panel_files


def main():
    print("=================================================================")
    print("   DARX | RENDERIZADOR DE STORYBOARDS DE CRAFTEO DE ARMAS        ")
    print("=================================================================")

    # 1. Configurar Escena
    print("[1/2] Configurando escena base (mesa, rig 3P/1P, iluminación)...")
    scene_elements = setup_base_scene()

    # 2. Renderizar frames por cada arma
    print("[2/2] Renderizando frames clave para las 4 armas...")
    for wep_info in WEAPON_CATALOG:
        render_weapon_storyboard(scene_elements, wep_info)

    print("\n=================================================================")
    print("   TODOS LOS PANELES FUERON RENDERIZADOS CON ÉXITO               ")
    print("=================================================================")


if __name__ == "__main__":
    main()

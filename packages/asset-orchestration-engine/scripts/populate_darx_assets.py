"""populate_darx_assets.py
Integra todos los modelos canónicos del proyecto dentro del archivo maestro Art/Blender/DarX_Assets.blend:
1. Colección DARX_Player: Personaje Jugador Adulto Riggeado (SK_Player / ARM_Player) con shader Dark Fluid.
2. Colección DARX_CraftingBench: Mesa de Crafteo Sci-Fi completa (SM_Mesa_Crafteo / SM_CraftingBench).
3. Colección DARX_Bastion: Enemigo táctico Bastion SWAT (SK_Bastion_SWAT / ARM_Bastion).
4. Exporta el FBX estático a Art/FBX/World_Props/SM_Mesa_Crafteo.fbx y Art/FBX/SM_CraftingBench.fbx.
5. Renderiza las vistas de vitrina (Showcase) mostrando los modelos integrados y la escala comparativa.
"""

import os
import sys
import math
import bpy
import bmesh
from mathutils import Vector, Matrix, Euler

R = math.radians

DARX_ASSETS_BLEND = r"E:\Darx_Proyect\Art\Blender\DarX_Assets.blend"
PLAYER_BLEND = r"E:\Darx_Proyect\Saved\Player_Skin_Workspace\DarX_Player_Rigged_Canonical.blend"
BENCH_BLEND = r"E:\Darx_Proyect\Saved\Player_Skin_Workspace\DarX_CraftingBench_Master.blend"
OUT_DIR = r"C:\Users\sasuk\.gemini\antigravity\brain\695523dc-0f49-434f-b134-d3298443b0f2"
FBX_WORLD_PROPS = r"E:\Darx_Proyect\Art\FBX\World_Props\SM_Mesa_Crafteo.fbx"
FBX_BENCH_ROOT = r"E:\Darx_Proyect\Art\FBX\SM_CraftingBench.fbx"

def append_from_blend(filepath, obj_names):
    """Anexa objetos y sus dependencias de datos desde otro archivo .blend"""
    with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
        data_to.objects = [name for name in data_from.objects if name in obj_names]
    return [o for o in data_to.objects if o is not None]

def main():
    print(f"=== [1/5] ABRIENDO ARCHIVO MAESTRO: {DARX_ASSETS_BLEND} ===")
    bpy.ops.wm.open_mainfile(filepath=DARX_ASSETS_BLEND)
    scene = bpy.context.scene

    # 1. Asegurar o crear colecciones principales
    def get_or_create_col(name, parent_col=scene.collection):
        col = bpy.data.collections.get(name)
        if not col:
            col = bpy.data.collections.new(name)
            parent_col.children.link(col)
        return col

    col_player = get_or_create_col("DARX_Player")
    col_bench = get_or_create_col("DARX_CraftingBench")
    col_bastion = get_or_create_col("DARX_Bastion")

    # 2. Anexar Jugador Canónico si no está en la escena
    player_objs_needed = ["ARM_Player", "SK_Player"]
    existing_player = [o for o in bpy.data.objects if o.name in player_objs_needed]
    if len(existing_player) < 2:
        print(f"Anexando Jugador Canónico desde {PLAYER_BLEND}...")
        appended_p = append_from_blend(PLAYER_BLEND, player_objs_needed)
        for obj in appended_p:
            if obj.name not in col_player.objects:
                col_player.objects.link(obj)
            print(f"  + Objeto de Jugador anexado: {obj.name}")

    # 3. Anexar Mesa de Crafteo Canónica si no está en la escena
    bench_objs_needed = [
        "SM_CraftingBench", "SM_CraftingBench_Glass", "SM_CraftingBench_Vortex",
        "SM_CraftingBench_Ring", "SM_CraftingBench_HoloHUD", "SM_CraftingBench_ProjBar"
    ]
    existing_bench = [o for o in bpy.data.objects if o.name in bench_objs_needed]
    if len(existing_bench) < len(bench_objs_needed):
        print(f"Anexando Mesa de Crafteo desde {BENCH_BLEND}...")
        appended_b = append_from_blend(BENCH_BLEND, bench_objs_needed)
        for obj in appended_b:
            if obj.name not in col_bench.objects:
                col_bench.objects.link(obj)
            print(f"  + Objeto de Mesa anexado: {obj.name}")

    # 4. Crear Malla Estática Unificada SM_Mesa_Crafteo para Exportación FBX
    print("=== [2/5] CREANDO MALLA ESTÁTICA UNIFICADA SM_Mesa_Crafteo ===")
    bench_parts = [bpy.data.objects.get(n) for n in bench_objs_needed if bpy.data.objects.get(n)]
    
    # Duplicar y unir partes para crear el asset estático único de Unreal Engine
    bpy.ops.object.select_all(action='DESELECT')
    dup_objs = []
    for part in bench_parts:
        dup = part.copy()
        dup.data = part.data.copy()
        col_bench.objects.link(dup)
        dup.select_set(True)
        dup_objs.append(dup)

    bpy.context.view_layer.objects.active = dup_objs[0]
    bpy.ops.object.join()
    unified_bench = bpy.context.active_object
    unified_bench.name = "SM_Mesa_Crafteo"
    unified_bench.data.name = "SM_Mesa_Crafteo_Mesh"
    print(f"Malla unificada creada: {unified_bench.name} ({len(unified_bench.data.vertices)} vértices, {len(unified_bench.data.materials)} materiales)")

    # 5. Exportar FBX para Unreal Engine 5
    print("=== [3/5] EXPORTANDO ASSETS FBX PARA UNREAL ENGINE ===")
    os.makedirs(os.path.dirname(FBX_WORLD_PROPS), exist_ok=True)
    
    bpy.ops.object.select_all(action='DESELECT')
    unified_bench.select_set(True)
    bpy.context.view_layer.objects.active = unified_bench

    # Exportar a World_Props y raíz de FBX
    for fbx_target in [FBX_WORLD_PROPS, FBX_BENCH_ROOT]:
        bpy.ops.export_scene.fbx(
            filepath=fbx_target,
            use_selection=True,
            global_scale=1.0,
            apply_scale_options='FBX_SCALE_NONE',
            axis_forward='-Y',
            axis_up='Z',
            bake_space_transform=False,
            object_types={'MESH'},
            use_mesh_modifiers=True,
            mesh_smooth_type='FACE',
            bake_anim=False,
            path_mode='COPY'
        )
        print(f"  -> FBX Exportado: {fbx_target} ({os.path.getsize(fbx_target)} bytes)")

    # 6. Organizar Showroom en la Escena de DarX_Assets
    print("=== [4/5] ORGANIZANDO VITRINA EN LA ESCENA ===")
    # Ocultar o eliminar el clon temporal del render de vitrina para evitar duplicación
    col_bench.objects.unlink(unified_bench)
    # Crear colección de exportación dedicada
    col_export = get_or_create_col("EXPORT_UE5")
    col_export.objects.link(unified_bench)
    unified_bench.hide_render = True
    unified_bench.hide_viewport = True

    # Posicionar activos para la vitrina comparativa de escalas:
    # 1. Jugador Canónico en X = 0.0, Y = 0.0 (Mirando hacia -Y)
    arm_p = bpy.data.objects.get("ARM_Player")
    sk_p = bpy.data.objects.get("SK_Player")
    if arm_p:
        arm_p.location = Vector((0.0, 0.0, 0.0))
        arm_p.rotation_euler = Euler((0, 0, R(180)), 'XYZ') # Mirando al frente

    # 2. Mesa de Crafteo en X = 1.60 m, Y = 0.35 m (Ergonómicamente al lado derecho del jugador)
    for b_name in bench_objs_needed:
        b_obj = bpy.data.objects.get(b_name)
        if b_obj:
            b_obj.location = Vector((1.55, 0.30, 0.0))
            b_obj.rotation_euler = Euler((0, 0, R(25)), 'XYZ') # Ligero giro dinámico

    # 3. Bastion SWAT en X = -2.30 m, Y = 0.60 m (A la izquierda en pose de guardia)
    arm_b = bpy.data.objects.get("ARM_Bastion")
    if arm_b:
        arm_b.location = Vector((-2.20, 0.50, 0.0))
        arm_b.rotation_euler = Euler((0, 0, R(160)), 'XYZ')

    # Configuración de Estudio y Render
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.image_settings.file_format = 'PNG'

    # Crear Suelo de Vitrina
    me_f = bpy.data.meshes.new("Showroom_Floor")
    bm_f = bmesh.new()
    bmesh.ops.create_grid(bm_f, x_segments=4, y_segments=4, size=24.0)
    bm_f.to_mesh(me_f)
    bm_f.free()
    obj_f = bpy.data.objects.new("Showroom_Floor_Obj", me_f)
    scene.collection.objects.link(obj_f)
    m_f = bpy.data.materials.new("M_Floor_Showroom")
    bsdf_f = m_f.node_tree.nodes.get("Principled BSDF")
    if bsdf_f:
        bsdf_f.inputs['Base Color'].default_value = (0.015, 0.015, 0.022, 1.0)
        bsdf_f.inputs['Roughness'].default_value = 0.45
        bsdf_f.inputs['Metallic'].default_value = 0.50
    me_f.materials.append(m_f)

    # Luces de Estudio para Vitrina
    def add_area_light(name, energy, size, color, loc, rot):
        ld = bpy.data.lights.new(name, 'AREA')
        ld.energy = energy
        ld.size = size
        ld.color = color
        lo = bpy.data.objects.new(name, ld)
        lo.location = Vector(loc)
        lo.rotation_euler = Euler((R(rot[0]), R(rot[1]), R(rot[2])), 'XYZ')
        scene.collection.objects.link(lo)
        return lo

    add_area_light("LGT_MainKey", 220.0, 4.0, (1.0, 0.98, 0.95), (1.0, -4.5, 3.2), (55, 0, 10))
    add_area_light("LGT_FillLeft", 120.0, 4.0, (0.75, 0.88, 1.0), (-3.5, -3.2, 2.5), (50, -20, -35))
    add_area_light("LGT_FillRight", 130.0, 3.5, (0.85, 0.90, 1.0), (3.5, -2.5, 2.8), (50, 20, 35))
    add_area_light("LGT_RimBack", 200.0, 3.0, (0.9, 0.95, 1.0), (0.0, 3.5, 2.8), (-45, 0, 180))
    add_area_light("LGT_RimPurple", 160.0, 2.5, (0.75, 0.15, 1.0), (2.0, 3.0, 2.0), (-40, 20, 150))

    # Cámaras de Vitrina
    cam_d = bpy.data.cameras.new("Cam_DarX_Assets")
    cam_o = bpy.data.objects.new("Cam_DarX_Assets", cam_d)
    scene.collection.objects.link(cam_o)
    scene.camera = cam_o

    # 7. Renderizar las 2 Tomas Oficiales de DarX_Assets
    print("=== [5/5] RENDERIZANDO VISTAS DE VITRINA ===")
    
    # Toma 1: Showroom Completo (Bastion, Player, Mesa de Crafteo)
    cam_o.location = Vector((0.0, -4.8, 1.65))
    dir_vec = Vector((0.0, 0.3, 0.95)) - cam_o.location
    cam_o.rotation_euler = dir_vec.to_track_quat('-Z', 'Y').to_euler()
    cam_d.angle = R(50)
    out_all = os.path.join(OUT_DIR, "showcase_darx_assets_all.png")
    scene.render.filepath = out_all
    bpy.ops.render.render(write_still=True)
    print(f"  -> RENDER COMPLETO GUARDADO: {out_all}")

    # Toma 2: Primer Plano Comparativo (Player + Mesa de Crafteo)
    cam_o.location = Vector((0.75, -2.9, 1.35))
    dir_vec2 = Vector((0.75, 0.20, 0.92)) - cam_o.location
    cam_o.rotation_euler = dir_vec2.to_track_quat('-Z', 'Y').to_euler()
    cam_d.angle = R(42)
    out_pair = os.path.join(OUT_DIR, "showcase_player_and_bench.png")
    scene.render.filepath = out_pair
    bpy.ops.render.render(write_still=True)
    print(f"  -> RENDER PLAYER+MESA GUARDADO: {out_pair}")

    # Guardar archivo maestro DarX_Assets.blend actualizado
    bpy.ops.wm.save_as_mainfile(filepath=DARX_ASSETS_BLEND)
    print(f"=== ARCHIVO MAESTRO DARX_ASSETS GUARDADO EXITOSAMENTE: {DARX_ASSETS_BLEND} ===")

if __name__ == "__main__":
    main()

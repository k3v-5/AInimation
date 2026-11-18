"""restore_full_darx_assets.py
Restaura la biblioteca maestra completa en Art/Blender/DarX_Assets.blend:
- Recupera las 17 colecciones originales con todos los jefes, armas, props y terminales.
- Actualiza DARX_Player con el Jugador Adulto Canónico (ARM_Player / SK_Player, shader Dark Fluid).
- Añade DARX_Bastion con Bastion SWAT (ARM_Bastion / SK_Bastion_SWAT).
- Actualiza DARX_World_Props y crea DARX_CraftingBench con la nueva Mesa de Crafteo Modular Sci-Fi (SM_Mesa_Crafteo).
"""

import os
import sys
import bpy

BASE_HISTORICA = r"E:\Darx_Proyect\Saved\temp_bf830355.blend"
PLAYER_CANONICAL = r"E:\Darx_Proyect\Saved\Player_Skin_Workspace\DarX_Player_Rigged_Canonical.blend"
BASTION_REDESIGN = r"E:\Darx_Proyect\Saved\Player_Skin_Workspace\DarX_Bastion_Redesign.blend"
BENCH_MASTER = r"E:\Darx_Proyect\Saved\Player_Skin_Workspace\DarX_CraftingBench_Master.blend"
DESTINO_MASTER = r"E:\Darx_Proyect\Art\Blender\DarX_Assets.blend"

def append_objects(filepath, obj_names):
    """Anexa objetos específicos desde otro archivo blend."""
    with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
        data_to.objects = [name for name in data_from.objects if name in obj_names]
    return [o for o in data_to.objects if o is not None]

def main():
    print(f"=== [1/5] CARGANDO ARCHIVO BASE HISTÓRICO: {BASE_HISTORICA} ===")
    bpy.ops.wm.open_mainfile(filepath=BASE_HISTORICA)
    scene = bpy.context.scene

    # 1. Limpieza de elementos obsoletos que serán actualizados
    print("=== [2/5] RETIRANDO PLACEHOLDERS ANTIGUOS ===")
    # Retirar jugador antiguo
    col_player = bpy.data.collections.get("DARX_Player")
    if col_player:
        for o in list(col_player.objects):
            print(f"  - Retirando objeto antiguo: {o.name}")
            bpy.data.objects.remove(o, do_unlink=True)
    else:
        col_player = bpy.data.collections.new("DARX_Player")
        scene.collection.children.link(col_player)

    # Retirar mesa antigua en World_Props
    col_wprops = bpy.data.collections.get("DARX_World_Props")
    old_bench = bpy.data.objects.get("SM_Mesa_Crafteo")
    if old_bench:
        print(f"  - Retirando placeholder antiguo de mesa: {old_bench.name}")
        bpy.data.objects.remove(old_bench, do_unlink=True)

    # 2. Anexar Jugador Canónico Adulto
    print(f"=== [3/5] ANEXANDO JUGADOR CANÓNICO ADULTO DESDE: {PLAYER_CANONICAL} ===")
    player_objs = append_objects(PLAYER_CANONICAL, ["ARM_Player", "SK_Player"])
    for o in player_objs:
        if o.name not in col_player.objects:
            col_player.objects.link(o)
        print(f"  + Objeto de Jugador integrado: {o.name}")

    # 3. Anexar Bastion SWAT
    print(f"=== [4/5] ANEXANDO BASTION SWAT DESDE: {BASTION_REDESIGN} ===")
    col_bastion = bpy.data.collections.get("DARX_Bastion")
    if not col_bastion:
        col_bastion = bpy.data.collections.new("DARX_Bastion")
        scene.collection.children.link(col_bastion)
    
    bastion_objs = append_objects(BASTION_REDESIGN, ["ARM_Bastion", "SK_Bastion_SWAT"])
    for o in bastion_objs:
        if o.name not in col_bastion.objects:
            col_bastion.objects.link(o)
        print(f"  + Objeto de Bastion integrado: {o.name}")

    # 4. Anexar Mesa de Crafteo Modular Sci-Fi
    print(f"=== [5/5] ANEXANDO MESA DE CRAFTEO SCI-FI DESDE: {BENCH_MASTER} ===")
    col_bench = bpy.data.collections.get("DARX_CraftingBench")
    if not col_bench:
        col_bench = bpy.data.collections.new("DARX_CraftingBench")
        scene.collection.children.link(col_bench)

    bench_parts_names = [
        "SM_CraftingBench", "SM_CraftingBench_Glass", "SM_CraftingBench_Vortex",
        "SM_CraftingBench_Ring", "SM_CraftingBench_HoloHUD", "SM_CraftingBench_ProjBar"
    ]
    bench_objs = append_objects(BENCH_MASTER, bench_parts_names)
    for o in bench_objs:
        if o.name not in col_bench.objects:
            col_bench.objects.link(o)
        print(f"  + Componente de Mesa integrado: {o.name}")

    # Crear Malla Estática Unificada SM_Mesa_Crafteo para DARX_World_Props
    bpy.ops.object.select_all(action='DESELECT')
    dup_objs = []
    for part in bench_objs:
        dup = part.copy()
        dup.data = part.data.copy()
        col_wprops.objects.link(dup)
        dup.select_set(True)
        dup_objs.append(dup)

    bpy.context.view_layer.objects.active = dup_objs[0]
    bpy.ops.object.join()
    unified_bench = bpy.context.active_object
    unified_bench.name = "SM_Mesa_Crafteo"
    unified_bench.data.name = "SM_Mesa_Crafteo_Mesh"
    print(f"  + Malla unificada generada en DARX_World_Props: {unified_bench.name} ({len(unified_bench.data.vertices)} vértices)")

    # 5. Guardar Archivo Maestro Consolidado
    bpy.ops.wm.save_as_mainfile(filepath=DESTINO_MASTER)
    print(f"=== GUARDADO EXITOSO: {DESTINO_MASTER} ({os.path.getsize(DESTINO_MASTER)} bytes) ===")

if __name__ == "__main__":
    main()

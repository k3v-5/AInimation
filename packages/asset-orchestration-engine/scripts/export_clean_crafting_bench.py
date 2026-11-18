import os
import sys
import bpy

BENCH_BLEND = r"E:\Darx_Proyect\Saved\Player_Skin_Workspace\DarX_CraftingBench_Master.blend"
OUT_FBX = r"E:\Darx_Proyect\Art\FBX\SM_CraftingBench.fbx"

bpy.ops.wm.open_mainfile(filepath=BENCH_BLEND)

bench_names = [
    'SM_CraftingBench',
    'SM_CraftingBench_Glass',
    'SM_CraftingBench_HoloHUD',
    'SM_CraftingBench_ProjBar',
    'SM_CraftingBench_Ring',
    'SM_CraftingBench_Vortex'
]

bpy.ops.object.select_all(action='DESELECT')
bench_objs = []
for name in bench_names:
    o = bpy.data.objects.get(name)
    if o and o.type == 'MESH':
        bench_objs.append(o)
        o.select_set(True)

if not bench_objs:
    print("[ERROR] No se encontraron mallas de la mesa!")
    sys.exit(1)

dup_objs = []
for o in bench_objs:
    dup = o.copy()
    dup.data = o.data.copy()
    bpy.context.scene.collection.objects.link(dup)
    dup_objs.append(dup)

bpy.ops.object.select_all(action='DESELECT')
for d in dup_objs:
    d.select_set(True)

bpy.context.view_layer.objects.active = dup_objs[0]
bpy.ops.object.join()
clean_bench = bpy.context.active_object
clean_bench.name = "SM_CraftingBench"
clean_bench.data.name = "SM_CraftingBench_Mesh"

bpy.ops.object.select_all(action='DESELECT')
clean_bench.select_set(True)
bpy.context.view_layer.objects.active = clean_bench

os.makedirs(os.path.dirname(OUT_FBX), exist_ok=True)
bpy.ops.export_scene.fbx(
    filepath=OUT_FBX,
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

print(f"[SUCCESS] Exportado clean FBX: {OUT_FBX} ({os.path.getsize(OUT_FBX)} bytes)")
for idx, m in enumerate(clean_bench.data.materials):
    print(f"  Slot {idx}: {m.name if m else 'None'}")

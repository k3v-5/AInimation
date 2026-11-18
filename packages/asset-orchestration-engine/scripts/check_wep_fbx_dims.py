import bpy
import os

weapon_fbx_dir = r"E:\Darx_Proyect\Art\FBX\Weapons"
fbx_files = ['SM_Wep_BreacherS4.fbx', 'SM_Wep_PhaseSMG.fbx', 'SM_Wep_Apex6.fbx', 'SM_Wep_VanguardAR.fbx']

for f in fbx_files:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    fbx_path = os.path.join(weapon_fbx_dir, f)
    bpy.ops.import_scene.fbx(filepath=fbx_path)
    print(f"\n=================== {f} ===================")
    meshes = [o for o in bpy.data.objects if o.type == 'MESH']
    for m in meshes:
        dims = [round(x, 4) for x in m.dimensions]
        print(f"  Mesh: {m.name}")
        print(f"  Dimensions (X, Y, Z meters): {dims}")
        print(f"  Dimensions (cm): {[round(x * 100, 2) for x in m.dimensions]}")
        print(f"  Scale: {[round(x, 4) for x in m.scale]}")
        print(f"  Location: {[round(x, 4) for x in m.location]}")
        coords = [v.co for v in m.data.vertices]
        min_c = [round(min(c[i] for c in coords), 4) for i in range(3)]
        max_c = [round(max(c[i] for c in coords), 4) for i in range(3)]
        print(f"  Local Bounds Min: {min_c}")
        print(f"  Local Bounds Max: {max_c}")

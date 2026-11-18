import sys, os
import bpy

sys.path.append(r"E:\Darx_Proyect\Art\Blender")

files = [
    ("darx_acosador", "SK_Acosador"),
    ("darx_artillero", "SK_Gunner_Turret"),
    ("darx_bastion", "SK_Bastion_SWAT"),
    ("darx_detonador", "SK_Detonador"),
    ("darx_interferente", "SK_Interferente"),
    ("darx_observador", "SK_Observador"),
    ("darx_portador", "SK_Portador_Herald"),
    ("darx_repulsor", "SK_Repulsor"),
    ("darx_robot", "SK_Robot_Grab"),
    ("darx_static_shadow", "SK_StaticShadow")
]

print("=== TESTING build_all() FOR ALL 10 MOBS ===")
for mod_name, expected_sk in files:
    try:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        mod = __import__(mod_name)
        mesh_obj, arm_obj = mod.build_all()
        assert mesh_obj is not None, f"mesh_obj is None in {mod_name}"
        assert arm_obj is not None, f"arm_obj is None in {mod_name}"
        bone_count = len(arm_obj.data.bones)
        vert_count = len(mesh_obj.data.vertices)
        print(f"[OK] {mod_name:20}: mesh '{mesh_obj.name}' ({vert_count:4} verts), arm '{arm_obj.name}' ({bone_count:2} bones)")
    except Exception as e:
        print(f"[FAILED] {mod_name}: {e}")

print("=== DONE ===")

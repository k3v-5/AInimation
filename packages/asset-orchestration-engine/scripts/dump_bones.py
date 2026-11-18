import sys, os
import bpy

sys.path.append(r"E:\Darx_Proyect\Art\Blender")

files = [
    "darx_acosador",
    "darx_artillero",
    "darx_bastion",
    "darx_detonador",
    "darx_interferente",
    "darx_observador",
    "darx_portador",
    "darx_repulsor",
    "darx_robot",
    "darx_static_shadow"
]

for mod_name in files:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    m = __import__(mod_name)
    mesh_obj, arm_obj = m.build_all()
    bones = [b.name for b in arm_obj.data.bones]
    print(f"=== {mod_name} ({arm_obj.name}) ===")
    print("   Bones:", ", ".join(bones))

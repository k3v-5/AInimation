import sys, os
import bpy

sys.path.append(r"E:\Darx_Proyect\Art\Blender")

pairs = [
    ("darx_acosador", "darx_acosador_anim", "Acosador"),
    ("darx_bastion", "darx_bastion_anim", "Bastion"),
    ("darx_detonador", "darx_detonador_anim", "Detonador"),
    ("darx_interferente", "darx_interferente_anim", "Interferente"),
    ("darx_observador", "darx_observador_anim", "Observador"),
    ("darx_portador", "darx_portador_anim", "Portador"),
    ("darx_repulsor", "darx_repulsor_anim", "Repulsor"),
    ("darx_robot", "darx_robot_anim", "Robot"),
    ("darx_static_shadow", "darx_static_shadow_anim", "StaticShadow"),
]

print("=== INSPECCIONANDO MODELOS Y ANIMACIONES ===")
for m_mod, a_mod, name in pairs:
    try:
        m = __import__(m_mod)
        a = __import__(a_mod)
        print(f"\n--- {name} ---")
        bpy.ops.wm.read_factory_settings(use_empty=True)
        res = m.build_all()
        arm = res[1] if isinstance(res, tuple) else res
        bone_names = set(b.name for b in arm.data.bones)
        print(f"Huesos en rig ({len(bone_names)}): {sorted(list(bone_names))[:10]}...")

        actions = a.build_all() if hasattr(a, "build_all") else []
        print(f"Acciones ({len(actions)}): {[act.name for act in actions]}")

        for act in actions:
            act_bones = set()
            for fc in act.fcurves:
                dp = fc.data_path
                if 'pose.bones["' in dp:
                    bname = dp.split('pose.bones["')[1].split('"]')[0]
                    act_bones.add(bname)
            missing = act_bones - bone_names
            if missing:
                print(f"  [ALERTA] {act.name}: huesos en animacion que NO existen en rig: {missing}")
            else:
                print(f"  [OK] {act.name}: coinciden {len(act_bones)} huesos")
    except Exception as e:
        print(f"ERROR en {name}: {e}")

# Check Artillero and darx_anim2
print("\n--- Artillero ---")
try:
    import darx_artillero, darx_anim2
    bpy.ops.wm.read_factory_settings(use_empty=True)
    res = darx_artillero.build_all()
    arm = res[1] if isinstance(res, tuple) else res
    bone_names = set(b.name for b in arm.data.bones)
    print(f"Huesos en rig Artillero ({len(bone_names)}): {sorted(list(bone_names))}")
except Exception as e:
    print(f"ERROR en Artillero: {e}")

import sys, os
import bpy

sys.path.append(r"E:\Darx_Proyect\Art\Blender")

mobs = [
    ("darx_acosador", "darx_acosador_anim", "ARM_Acosador"),
    ("darx_artillero", "darx_artillero_anim", "ARM_Gunner_Turret"),
    ("darx_bastion", "darx_bastion_anim", "ARM_Bastion"),
    ("darx_detonador", "darx_detonador_anim", "ARM_Detonador"),
    ("darx_interferente", "darx_interferente_anim", "ARM_Interferente"),
    ("darx_observador", "darx_observador_anim", "ARM_Observador"),
    ("darx_portador", "darx_portador_anim", "ARM_Portador"),
    ("darx_repulsor", "darx_repulsor_anim", "ARM_Repulsor"),
    ("darx_robot", "darx_robot_anim", "ARM_Robot_Grab"),
    ("darx_static_shadow", "darx_static_shadow_anim", "ARM_StaticShadow"),
]

print("=== VERIFICANDO TODAS LAS ANIMACIONES DEDICADAS (10 MOBS) ===")
total_actions = 0
errors = 0

for mesh_mod_name, anim_mod_name, arm_name in mobs:
    try:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        m_mod = __import__(mesh_mod_name)
        a_mod = __import__(anim_mod_name)

        mesh_obj, arm_obj = m_mod.build_all()
        assert mesh_obj is not None
        assert arm_obj is not None

        actions = a_mod.build_all()
        assert len(actions) > 0, "No actions generated"
        act_names = [act.name for act in actions]
        total_actions += len(actions)

        # Assign each action to verify it binds without error
        for act in actions:
            arm_obj.animation_data.action = act
            # Check frame range
            fr = act.frame_range
            assert fr[1] > fr[0], f"Invalid frame range for {act.name}: {fr}"

        print(f"[OK] {mesh_mod_name:20}: {len(actions)} acciones válidas -> {act_names}")
    except Exception as e:
        print(f"[ERROR EXCEPCION] {mesh_mod_name}: {e}")
        errors += 1

print(f"\n=== RESUMEN: {total_actions} ACCIONES VERIFICADAS, {errors} ERRORES ===")
if errors > 0:
    sys.exit(1)

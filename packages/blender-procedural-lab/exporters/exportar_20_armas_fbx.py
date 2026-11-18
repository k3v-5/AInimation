# Copyright (c) 2026 Astra Hazard Studios. All Rights Reserved.
# Pipeline de Exportación Automatizada de las 20 Armas y Herramientas Tácticas Oficiales
# Exporta Static Meshes limpias con Nanite readiness, origen normalizado (Z base = 0) y volúmenes de colisión UCX.

import bpy
import bmesh
import os
import sys
from mathutils import Vector

PROJECT_ROOT = r"F:\Dev\Game"
BLEND_FILE = os.path.join(PROJECT_ROOT, "Art", "Blender", "Arsenal_20_Armas_Oficial.blend")
FBX_WEAPONS_DIR = os.path.join(PROJECT_ROOT, "Art", "FBX", "Equipment", "Weapons")
os.makedirs(FBX_WEAPONS_DIR, exist_ok=True)

WEAPONS_CONFIG = [
    (1, "W01_Hydra_Heavy_Hose", "Manguera de Alta Presión Hidráulica"),
    (2, "W02_Thermal_Shock_Axe", "Hacha de Choque Térmico"),
    (3, "W03_Cryo_CO2_Extinguisher", "Extintor Criogénico CO2 Pesado"),
    (4, "W04_Bio_Defibrillator_Unit", "Desfibrilador Portátil Militar"),
    (5, "W05_Plasma_Halligan_Bar", "Barra Halligan de Plasma Forjado"),
    (6, "W06_Rotary_Rescue_Saw", "Sierra Circular de Rescate Rotativa"),
    (7, "W07_Pneumatic_Bolt_Cutter", "Cizalla Neumática Asistida"),
    (8, "W08_Chemical_Foam_Mortar", "Mortero de Espuma Química"),
    (9, "W09_Thermite_Breach_Lance", "Lanza Térmica de Perforación"),
    (10, "W10_EMP_Disruptor_Pistol", "Pistola Disruptora EMP"),
    (11, "W11_Hydraulic_Spreader_Jaws", "Mandíbulas de Separación Hidráulica"),
    (12, "W12_Cryo_Grenade_Launcher", "Lanzagranadas Criogénico de Tambor"),
    (13, "W13_Pneumatic_Breaching_Ram", "Ariete Neumático de Brecha Cinético"),
    (14, "W14_Magnetic_Net_Launcher", "Lanzador de Red Magnética Cuádruple"),
    (15, "W15_Chemical_Neutralizer_Pack", "Aspersor Neutralizador Portátil"),
    (16, "W16_Emergency_SOS_Flare_Gun", "Pistola de Bengalas SOS Superbrillante"),
    (17, "W17_Sonic_Fire_Suppressor", "Supresor Sónico de Fuego Acústico"),
    (18, "W18_Arc_Welding_Cutting_Torch", "Soplete de Arco Voltaico Industrial"),
    (19, "W19_Tripod_Mounted_Foam_Cannon", "Cañón de Espuma Pesada Sobre Trípode"),
    (20, "W20_Tactical_Rescue_Machete", "Machete Táctico de Rescate y Supervivencia")
]

def get_all_descendant_meshes(parent_obj):
    """Obtiene recursivamente todas las mallas hijas directas e indirectas."""
    meshes = []
    for child in parent_obj.children:
        if child.type == 'MESH':
            meshes.append(child)
        meshes.extend(get_all_descendant_meshes(child))
    return meshes

def export_weapon_to_fbx(weapon_id, weapon_name, label):
    root_name = f"Root_{weapon_name}"
    root = bpy.data.objects.get(root_name)
    if not root:
        print(f"[ERROR] W{weapon_id:02d}: Root '{root_name}' no encontrado en escena.")
        return False

    meshes = get_all_descendant_meshes(root)
    if not meshes:
        print(f"[ERROR] W{weapon_id:02d}: No se encontraron mallas hijas para '{root_name}'.")
        return False

    # Calcular bounding box total en espacio de mundo
    all_corners = []
    for m in meshes:
        corners = [m.matrix_world @ Vector(c) for c in m.bound_box]
        all_corners.extend(corners)

    min_x = min(c.x for c in all_corners)
    max_x = max(c.x for c in all_corners)
    min_y = min(c.y for c in all_corners)
    max_y = max(c.y for c in all_corners)
    min_z = min(c.z for c in all_corners)
    max_z = max(c.z for c in all_corners)

    center_x = (min_x + max_x) / 2.0
    center_y = (min_y + max_y) / 2.0
    base_z = min_z

    width = max(max_x - min_x, 0.05)
    depth = max(max_y - min_y, 0.05)
    height = max(max_z - min_z, 0.05)

    # Duplicar todas las mallas para unión limpia sin tocar originales
    bpy.ops.object.select_all(action='DESELECT')
    for m in meshes:
        m.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.object.duplicate()

    dup_meshes = [o for o in bpy.context.selected_objects if o.type == 'MESH']
    for dm in dup_meshes:
        dm.parent = None

    bpy.context.view_layer.objects.active = dup_meshes[0]
    bpy.ops.object.join()

    joined_obj = bpy.context.active_object
    sm_name = f"SM_{weapon_name}"
    joined_obj.name = sm_name

    # Hornear transformaciones a nivel de mundo
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # Desplazar vértices al origen de contacto inferior (0, 0, 0)
    for v in joined_obj.data.vertices:
        v.co.x -= center_x
        v.co.y -= center_y
        v.co.z -= base_z
    joined_obj.data.update()

    # Generar volumen de colisión convexa UCX_
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, height / 2.0))
    ucx_obj = bpy.context.active_object
    ucx_obj.name = f"UCX_{sm_name}_01"
    ucx_obj.scale = (width * 0.96, depth * 0.96, height)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    # Seleccionar malla principal y volumen UCX para exportación
    bpy.ops.object.select_all(action='DESELECT')
    joined_obj.select_set(True)
    ucx_obj.select_set(True)
    bpy.context.view_layer.objects.active = joined_obj

    fbx_path = os.path.join(FBX_WEAPONS_DIR, f"{sm_name}.fbx")
    bpy.ops.export_scene.fbx(
        filepath=fbx_path,
        use_selection=True,
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_ALL',
        axis_forward='-Z',
        axis_up='Y',
        mesh_smooth_type='FACE'
    )

    # Limpieza de duplicados y auxiliares
    bpy.data.objects.remove(ucx_obj, do_unlink=True)
    bpy.data.objects.remove(joined_obj, do_unlink=True)

    print(f" [OK] W{weapon_id:02d} ({sm_name} | {label}) -> {fbx_path} [Dims: {width:.2f}x{depth:.2f}x{height:.2f} m]")
    return True

def main():
    print("=" * 80)
    print("PIPELINE DE EXPORTACIÓN FBX: ARSENAL OFICIAL 20 ARMAS Y HERRAMIENTAS")
    print("=" * 80)

    if not os.path.exists(BLEND_FILE):
        print(f"[FATAL] No existe archivo .blend: {BLEND_FILE}")
        sys.exit(1)

    print(f"Abriendo archivo maestro: {BLEND_FILE}")
    bpy.ops.wm.open_mainfile(filepath=BLEND_FILE)

    total_exported = 0
    total_expected = len(WEAPONS_CONFIG)

    for w_id, w_name, label in WEAPONS_CONFIG:
        if export_weapon_to_fbx(w_id, w_name, label):
            total_exported += 1

    print("\n" + "=" * 80)
    print(f"EXPORTACIÓN FBX COMPLETADA: {total_exported}/{total_expected} ARMAS GENERADAS EN {FBX_WEAPONS_DIR}")
    print("=" * 80)

if __name__ == "__main__":
    main()

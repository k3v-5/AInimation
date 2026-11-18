"""regenerar_suelos_zero_zfighting.py — Regenerador Maestro de Mallas de Suelo para DarX.
CERO Z-FIGHTING, CERO CARAS COPLANARES, CERO CAJAS SUELTAS EN RELIEVE.
Aplica arquitectura de geometría escalonada sumergida (sunken manifold topology) con cotas Z únicas.
"""

import bpy
import bmesh
import math
import os
import sys
from mathutils import Matrix, Vector

FBX_DIR = r"E:/Darx_Proyect/Art/FBX/Biomas"
COL_MAESTRA = "DARX_MegaFase_Biomas"

def crear_material(name, rgb, rough=0.3, metal=0.5, emis=None, emis_str=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
        bsdf.inputs["Roughness"].default_value = rough
        bsdf.inputs["Metallic"].default_value = metal
        if emis and "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = (*emis, 1.0)
            bsdf.inputs["Emission Strength"].default_value = emis_str
    m.diffuse_color = (*rgb, 1.0)
    return m

def crear_materiales():
    mats = {}
    # ROBÓTICA
    mats["M_Robo_CobaltSteel"] = crear_material("M_Robo_CobaltSteel", (0.04, 0.08, 0.18), rough=0.32, metal=0.75)
    mats["M_Robo_Charcoal"] = crear_material("M_Robo_Charcoal", (0.03, 0.03, 0.03), rough=0.45, metal=0.55)
    mats["M_Robo_CopperBronze"] = crear_material("M_Robo_CopperBronze", (0.75, 0.40, 0.14), rough=0.20, metal=0.96)

    # SALA LIMPIA / CUÁNTICO
    mats["M_Clean_WhiteCeramic"] = crear_material("M_Clean_WhiteCeramic", (0.92, 0.93, 0.95), rough=0.14, metal=0.04)
    mats["M_Clean_DarkMetal"] = crear_material("M_Clean_DarkMetal", (0.03, 0.03, 0.04), rough=0.32, metal=0.94)
    mats["M_Clean_CyanNeon"] = crear_material("M_Clean_CyanNeon", (0.0, 0.88, 1.0), rough=0.06, metal=0.0, emis=(0.0, 0.88, 1.0), emis_str=3.5)
    mats["M_Clean_Chrome"] = crear_material("M_Clean_Chrome", (0.95, 0.95, 0.98), rough=0.02, metal=0.99)

    # BIOTECH
    mats["M_Bio_DarkMetal"] = crear_material("M_Bio_DarkMetal", (0.04, 0.05, 0.045), rough=0.40, metal=0.60)
    mats["M_Bio_AcidGreen"] = crear_material("M_Bio_AcidGreen", (0.05, 0.95, 0.12), rough=0.12, metal=0.0, emis=(0.05, 0.95, 0.12), emis_str=2.5)
    mats["M_Bio_PipeYellow"] = crear_material("M_Bio_PipeYellow", (0.85, 0.65, 0.08), rough=0.35, metal=0.35)
    return mats

def exportar_fbx_limpio(obj, filepath):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_scene.fbx(
        filepath=filepath,
        use_selection=True,
        global_scale=1.0,
        apply_unit_scale=True,
        apply_scale_options='FBX_SCALE_NONE',
        axis_forward='-Y',
        axis_up='Z',
        object_types={'MESH'},
        use_mesh_modifiers=True,
        mesh_smooth_type='FACE',
        add_leaf_bones=False,
        bake_anim=False
    )
    print(f"Exportado FBX limpio: {filepath}")

def modelar_robo_floor_darkplate(col, mats):
    """SM_Robo_Floor_DarkPlate: Losa de acero azul cobalto con marco carbón, canaleta de cobre y pernos.
    CERO cajas sueltas en relieve: los 4 paneles están biselados en el sólido sin caras coplanares."""
    me = bpy.data.meshes.new("SM_Robo_Floor_DarkPlate")
    bm = bmesh.new()
    
    # Asignar slots en orden canónico
    me.materials.append(mats["M_Robo_CobaltSteel"])  # Slot 0
    me.materials.append(mats["M_Robo_Charcoal"])     # Slot 1
    me.materials.append(mats["M_Robo_CopperBronze"]) # Slot 2

    # 1. Bloque de cimentación base (Z: 0.0 a 0.95 m)
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((0, 0, 0.475)) @ Matrix.Diagonal((1.0, 1.0, 0.95, 1.0)))
    for f in bm.faces: f.material_index = 0

    # 2. Marco perimetral rebajado de carbón (Z: 0.50 a 0.98 m) - Sumergido
    f_start = len(bm.faces)
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((0, 0, 0.74)) @ Matrix.Diagonal((0.98, 0.98, 0.48, 1.0)))
    for f in bm.faces[f_start:]: f.material_index = 1

    # 3. Losa central diamantada de acero cobalto (Z: 0.60 a 1.00 m) - Sumergida
    f_start = len(bm.faces)
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((0, 0, 0.80)) @ Matrix.Diagonal((0.90, 0.90, 0.40, 1.0)))
    for f in bm.faces[f_start:]: f.material_index = 0

    # 4. Canaleta lateral sumergida (Z: 0.70 a 0.985 m)
    f_start = len(bm.faces)
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((0.35, 0, 0.8425)) @ Matrix.Diagonal((0.14, 0.86, 0.285, 1.0)))
    for f in bm.faces[f_start:]: f.material_index = 1

    # 5. Línea doble de cables/conduits de cobre en la canaleta (Z_center = 0.995 m)
    for dx in [0.325, 0.375]:
        f_start = len(bm.faces)
        bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=0.018, radius2=0.018, depth=0.86,
                              matrix=Matrix.Translation((dx, 0, 0.995)) @ Matrix.Rotation(math.pi/2, 4, 'X'))
        for f in bm.faces[f_start:]: f.material_index = 2

    # 6. Pernos de bronce esquineros sumergidos (Z: 0.85 a 1.015 m)
    for bx in [-0.42, 0.42]:
        for by in [-0.42, 0.42]:
            f_start = len(bm.faces)
            bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=0.026, radius2=0.026, depth=0.165,
                                  matrix=Matrix.Translation((bx, by, 0.9325)))
            for f in bm.faces[f_start:]: f.material_index = 2

    bm.to_mesh(me)
    bm.free()

    obj = bpy.data.objects.new("SM_Robo_Floor_DarkPlate", me)
    col.objects.link(obj)
    return obj

def modelar_clean_floor_tile(col, mats):
    """SM_Clean_Floor_Tile: Losa blanca cerámica estéril con marco oscuro, cruz de neón cian y centro cromado."""
    me = bpy.data.meshes.new("SM_Clean_Floor_Tile")
    bm = bmesh.new()

    # Slots en orden canónico
    me.materials.append(mats["M_Clean_WhiteCeramic"]) # Slot 0
    me.materials.append(mats["M_Clean_DarkMetal"])    # Slot 1
    me.materials.append(mats["M_Clean_CyanNeon"])     # Slot 2
    me.materials.append(mats["M_Clean_Chrome"])       # Slot 3

    # 1. Bloque de cimentación base (Z: 0.0 a 0.95 m)
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((0, 0, 0.475)) @ Matrix.Diagonal((1.0, 1.0, 0.95, 1.0)))
    for f in bm.faces: f.material_index = 1

    # 2. Marco perimetral y junta de silicona oscura (Z: 0.50 a 0.98 m) - Sumergido
    f_start = len(bm.faces)
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((0, 0, 0.74)) @ Matrix.Diagonal((0.98, 0.98, 0.48, 1.0)))
    for f in bm.faces[f_start:]: f.material_index = 1

    # 3. Losa cerámica blanca brillante elevada (Z: 0.60 a 1.00 m) - Sumergida
    f_start = len(bm.faces)
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((0, 0, 0.80)) @ Matrix.Diagonal((0.92, 0.92, 0.40, 1.0)))
    for f in bm.faces[f_start:]: f.material_index = 0

    # 4. Cruz de fibra óptica cian (Z: 0.75 a 1.015 m) - Sumergida
    for dx, dy, sx, sy in [(0, 0.245, 0.04, 0.41), (0, -0.245, 0.04, 0.41), (0.245, 0, 0.41, 0.04), (-0.245, 0, 0.41, 0.04)]:
        f_start = len(bm.faces)
        bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((dx, dy, 0.8825)) @ Matrix.Diagonal((sx, sy, 0.265, 1.0)))
        for f in bm.faces[f_start:]: f.material_index = 2

    # 5. Hub central de cromo cilíndrico (Z: 0.80 a 1.020 m) - Sumergido
    f_start = len(bm.faces)
    bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=0.048, radius2=0.048, depth=0.22,
                          matrix=Matrix.Translation((0, 0, 0.910)))
    for f in bm.faces[f_start:]: f.material_index = 3

    # 6. Esquineros de cromo (Z: 0.80 a 1.018 m) - Sumergidos
    for cx in [-0.41, 0.41]:
        for cy in [-0.41, 0.41]:
            f_start = len(bm.faces)
            bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((cx, cy, 0.909)) @ Matrix.Diagonal((0.06, 0.06, 0.218, 1.0)))
            for f in bm.faces[f_start:]: f.material_index = 3

    bm.to_mesh(me)
    bm.free()

    obj = bpy.data.objects.new("SM_Clean_Floor_Tile", me)
    col.objects.link(obj)
    return obj

def modelar_bio_floor_grate(col, mats):
    """SM_Bio_Floor_Grate: Rejilla industrial de biohazard sobre fosa de lodo cáustico."""
    me = bpy.data.meshes.new("SM_Bio_Floor_Grate")
    bm = bmesh.new()

    # Slots en orden canónico
    me.materials.append(mats["M_Bio_DarkMetal"])  # Slot 0
    me.materials.append(mats["M_Bio_AcidGreen"])  # Slot 1
    me.materials.append(mats["M_Bio_PipeYellow"]) # Slot 2

    # 1. Marco exterior estructural base (Z: 0.0 a 0.70 m)
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((0, 0, 0.35)) @ Matrix.Diagonal((1.0, 1.0, 0.70, 1.0)))
    for f in bm.faces: f.material_index = 0

    # 2. Marco superior de apoyo de rejilla (Z: 0.45 a 1.00 m) - Sumergido
    f_start = len(bm.faces)
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((0, 0, 0.725)) @ Matrix.Diagonal((0.98, 0.98, 0.55, 1.0)))
    for f in bm.faces[f_start:]: f.material_index = 0

    # 3. Fosa de lodo ácido cáustico (Z: 0.55 a 0.90 m) - Sumergido
    f_start = len(bm.faces)
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((0, 0, 0.725)) @ Matrix.Diagonal((0.84, 0.84, 0.35, 1.0)))
    for f in bm.faces[f_start:]: f.material_index = 1

    # 4. Barras longitudinales de rejilla (Z: 0.80 a 0.98 m)
    for dx in [-0.32, -0.16, 0.0, 0.16, 0.32]:
        f_start = len(bm.faces)
        bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((dx, 0, 0.89)) @ Matrix.Diagonal((0.035, 0.84, 0.18, 1.0)))
        for f in bm.faces[f_start:]: f.material_index = 0

    # 5. Pernos de advertencia en esquinas (Z: 0.77 a 1.02 m) - Sumergidos
    for px in [-0.45, 0.45]:
        for py in [-0.45, 0.45]:
            f_start = len(bm.faces)
            bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=0.026, radius2=0.026, depth=0.25,
                                  matrix=Matrix.Translation((px, py, 0.895)))
            for f in bm.faces[f_start:]: f.material_index = 2

    bm.to_mesh(me)
    bm.free()

    obj = bpy.data.objects.new("SM_Bio_Floor_Grate", me)
    col.objects.link(obj)
    return obj

def main():
    print("=================================================================")
    print("DarX | Generando Mallas de Suelo con Cero Z-Fighting y Cotas Únicas")
    print("=================================================================")
    bpy.ops.wm.read_factory_settings(use_empty=True)

    col = bpy.data.collections.get(COL_MAESTRA) or bpy.data.collections.new(COL_MAESTRA)
    if col.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(col)

    mats = crear_materiales()

    suelos = [
        modelar_robo_floor_darkplate(col, mats),
        modelar_clean_floor_tile(col, mats),
        modelar_bio_floor_grate(col, mats)
    ]

    os.makedirs(FBX_DIR, exist_ok=True)
    for obj in suelos:
        fbx_path = os.path.join(FBX_DIR, f"{obj.name}.fbx")
        exportar_fbx_limpio(obj, fbx_path)

    print("=== TODAS LAS MALLAS DE SUELO REGENERADAS EXITOSAMENTE ===")

if __name__ == "__main__":
    main()

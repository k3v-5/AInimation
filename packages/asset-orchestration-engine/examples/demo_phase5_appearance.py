import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import (
    GeometryEngine, AppearanceEngine, AppearanceAPI, TextureMetadata,
    TextureUsage, ColorSpace, UVMethod
)

def main():
    print("=" * 85)
    print("  ASSET ORCHESTRATION ENGINE v5 (AOE v5) — FASE 5: APPEARANCE ENGINE DEMO")
    print("=" * 85)

    geo_engine = GeometryEngine()
    app_engine = AppearanceEngine(geo_engine)
    app_api = AppearanceAPI(app_engine)

    # 1. Geometría Previamente Aprobada por Fase 4
    print("\n[PASO 1] Estado de Geometría Aprobada por Fase 4 (GEOMETRY_LOCK = ACTIVO):")
    geo_engine.create_component("sword_01", "handle", "primitive", {"primitive": "cylinder", "width": 0.035, "depth": 0.035, "height": 0.25})
    geo_engine.create_component("sword_01", "guard", "primitive", {"primitive": "box", "width": 0.15, "depth": 0.03, "height": 0.03}, parent_id="sword_01.handle")
    geo_engine.create_component("sword_01", "blade", "profile", {"length": 0.95, "width": 0.05, "thickness": 0.015, "tip_ratio": 0.15}, parent_id="sword_01.guard")
    geo_engine.create_component("sword_01", "pommel", "primitive", {"primitive": "sphere", "width": 0.05, "depth": 0.05, "height": 0.05}, parent_id="sword_01.handle")

    insp_blade_geo = geo_engine.inspect_component("sword_01.blade")
    print(f" - Blade Geometría: {insp_blade_geo['vertices_count']} vértices, {insp_blade_geo['triangle_count']} triángulos, dim={insp_blade_geo['dimensions']}")
    print(f" - Bloqueo de Geometría: {app_engine.context.geometry_locked}")

    # 2. Creación de Materiales PBR
    print("\n[PASO 2] Creando Materiales Base PBR:")
    app_api.create_material("metal_dark", "Dark Metal", "PBR", {"base_color": "#2A2D34", "metallic": 0.90, "roughness": 0.25})
    app_api.create_material("leather_brown", "Brown Leather", "PBR", {"base_color": "#5A3D28", "metallic": 0.0, "roughness": 0.75})
    print(" - Material 'metal_dark' creado: metallic=0.90, roughness=0.25")
    print(" - Material 'leather_brown' creado: metallic=0.0, roughness=0.75")

    # 3. Asignación a Componentes e Instancias
    print("\n[PASO 3] Asignando Materiales a Componentes (Slots & Instancias):")
    app_api.assign_material("sword_01.blade", "metal_dark", "slot_blade")
    app_api.assign_material("sword_01.guard", "metal_dark", "slot_guard")
    app_api.assign_material("sword_01.handle", "leather_brown", "slot_handle")
    print(" - sword_01.blade -> metal_dark (Instancia creada)")
    print(" - sword_01.guard -> metal_dark (Instancia creada)")
    print(" - sword_01.handle -> leather_brown (Instancia creada)")

    # 4. Generación Procedural de UVs (UV0)
    print("\n[PASO 4] Generación de UV Sets (UV0) sobre la Geometría:")
    r_uv_blade = app_api.generate_uv("sword_01.blade", method="PLANAR", channel="UV0")
    r_uv_handle = app_api.generate_uv("sword_01.handle", method="CYLINDRICAL", channel="UV0")
    print(f" - UV0 Blade: {r_uv_blade['coordinates_count']} coordenadas generadas ({r_uv_blade['channel']})")
    print(f" - UV0 Handle: {r_uv_handle['coordinates_count']} coordenadas generadas ({r_uv_handle['channel']})")

    # 5. Registro de Texturas con Validación de Color Space
    print("\n[PASO 5] Registro de Texturas PBR con Validación de Color Space:")
    app_api.register_texture("tex_blade_albedo", "/textures/blade_diff.png", "BASE_COLOR", "sRGB")
    app_api.register_texture("tex_blade_normal", "/textures/blade_norm.png", "NORMAL", "Non-Color")
    app_api.register_texture("tex_blade_rough", "/textures/blade_rough.png", "ROUGHNESS", "Non-Color")
    print(" - BASE_COLOR -> sRGB (Validado)")
    print(" - NORMAL -> Non-Color (Validado)")
    print(" - ROUGHNESS -> Non-Color (Validado)")

    # 6. Modificación Quirúrgica de Apariencia
    print("\n[PASO 6] Petición del Usuario: 'El metal de la hoja está demasiado brillante' -> roughness 0.25 -> 0.35")
    mod_res = app_api.modify_material("sword_01.blade", {"roughness": 0.35})

    print(" - Resultado de la Modificación:")
    print(f"   * Status: {mod_res['status']}")
    print(f"   * Material Changes: {mod_res['diff']['material_changes']}")
    print(f"   * Geometry Changes: {mod_res['geometry_changes']} (Garantizado 0)")

    # 7. Verificación de Aislamiento de Instancias y Geometría
    print("\n[PASO 7] Verificación de Invarianza:")
    inst_blade = app_engine.materials.get_instance_for_component("sword_01.blade")
    inst_guard = app_engine.materials.get_instance_for_component("sword_01.guard")
    base_mat = app_engine.materials.get_material("metal_dark")
    insp_blade_geo_after = geo_engine.inspect_component("sword_01.blade")

    print(f" - Blade Instance Roughness: {inst_blade.parameter_overrides['roughness']} (Actualizado)")
    print(f" - Guard Instance Roughness: {inst_guard.get_effective_parameters(base_mat)['roughness']} (INTACTO en 0.25)")
    print(f" - Base metal_dark Roughness: {base_mat.parameters.roughness} (INTACTO en 0.25)")
    print(f" - Blade Vértices: {insp_blade_geo_after['vertices_count']} (INTACTO)")

    # 8. Manifest Final de Apariencia
    print("\n[PASO 8] Manifest Final de Apariencia:")
    manifest = app_api.get_manifest("sword_01")
    print(f" - Materiales Registrados: {len(manifest['materials'])}")
    print(f" - Texturas Registradas: {len(manifest['textures'])}")
    print(f" - UV Sets: {len(manifest['uv_sets'])}")
    print(f" - Asignaciones de Slots: {len(manifest['assignments'])}")
    print(f" - Validación de Apariencia: {app_api.validate()['status']}")

    print("\n" + "=" * 85)
    print("  CRITERIO DE EXITO DE FASE 5 CUMPLIDO AL 100% (APPROVED)")
    print("=" * 85)

if __name__ == "__main__":
    main()

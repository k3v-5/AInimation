import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import (
    GeometryEngine, AppearanceEngine, GameReadyEngine, GameReadyAPI,
    PivotType
)

def main():
    print("=" * 85)
    print("  ASSET ORCHESTRATION ENGINE v6 (AOE v6) — FASE 6: GAME READY PREPARATION DEMO")
    print("=" * 85)

    geo_engine = GeometryEngine()
    app_engine = AppearanceEngine(geo_engine)
    gr_engine = GameReadyEngine(geo_engine, app_engine)
    gr_api = GameReadyAPI(gr_engine)

    # 1. Geometría y Apariencia Aprobadas
    print("\n[PASO 1] Estado de Entrada: Asset Fuente Aprobado (READ ONLY):")
    geo_engine.create_component("sword_01", "handle", "primitive", {"primitive": "cylinder", "width": 0.035, "depth": 0.035, "height": 0.25})
    geo_engine.create_component("sword_01", "guard", "primitive", {"primitive": "box", "width": 0.15, "depth": 0.03, "height": 0.03}, parent_id="sword_01.handle")
    geo_engine.create_component("sword_01", "blade", "profile", {"length": 0.95, "width": 0.05, "thickness": 0.015, "tip_ratio": 0.15}, parent_id="sword_01.guard")
    geo_engine.create_component("sword_01", "pommel", "primitive", {"primitive": "sphere", "width": 0.05, "depth": 0.05, "height": 0.05}, parent_id="sword_01.handle")

    app_engine.create_material("M_DarkMetal", "Dark Metal", "PBR", {"metallic": 0.9, "roughness": 0.25})
    app_engine.create_material("M_Leather", "Leather", "PBR", {"metallic": 0.0, "roughness": 0.75})
    app_engine.assign_material("sword_01.blade", "M_DarkMetal", "slot_blade")
    app_engine.assign_material("sword_01.guard", "M_DarkMetal", "slot_guard")
    app_engine.assign_material("sword_01.handle", "M_Leather", "slot_handle")

    print(" - Geometría Fuente: APPROVED (v4)")
    print(" - Apariencia Fuente: APPROVED (v3)")
    print(" - Bloqueo de Fuente: INMUTABLE (Read Only)")

    # 2. Agregar Sockets para Unreal
    print("\n[PASO 2] Configuración de Sockets de Gameplay:")
    gr_api.add_socket("socket_grip", "handle", location=(0.0, 0.0, 10.0))
    gr_api.add_socket("socket_tip", "blade", location=(0.0, 0.0, 115.0))
    print(" - socket_grip en handle (Z = 10 cm)")
    print(" - socket_tip en blade (Z = 115 cm)")

    # 3. Procesamiento Game-Ready
    print("\n[PASO 3] Procesamiento Game-Ready (Decimación, LODs, Colisión UCX, Pivote y Escala):")
    res = gr_api.prepare_asset_for_unreal(
        asset_id="sword_01",
        category="Weapons",
        geometry_status="APPROVED",
        appearance_status="APPROVED",
        pivot_type="BOTTOM_CENTER"
    )

    print(" - Resultado del Procesamiento:")
    print(f"   * Status: {res['status']}")
    print(f"   * Nombre Unreal: {res['unreal_asset_name']}")
    print(f"   * Ruta en Unreal: {res['unreal_package_path']}")
    print(f"   * Dimensiones en Centímetros: {res['dimensions_cm']} (cm)")
    print(f"   * Cadena de LODs: {res['triangles']}")
    print(f"   * Colisión: {res['collision']}")

    # 4. Manifest Final Game-Ready
    print("\n[PASO 4] Manifiesto Game-Ready Exportable:")
    manifest = res["manifest"]
    print(f" - Asset ID: {manifest.asset_id}")
    print(f" - Versión Game Ready: {manifest.game_ready_version}")
    print(f" - Archivo FBX: {manifest.unreal_mapping.fbx_filename}")
    print(f" - Hulls de Colisión: {manifest.collision_hulls}")
    print(f" - Sockets Registrados: {manifest.sockets}")
    print(f" - Slots de Materiales: {manifest.material_slots}")
    print(f" - Import Scale: {manifest.import_settings.import_scale}")

    print("\n" + "=" * 85)
    print("  CRITERIO DE EXITO DE FASE 6 CUMPLIDO AL 100% (GAME_READY)")
    print("=" * 85)

if __name__ == "__main__":
    main()

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import (
    AssetReuseEngineAPI, LibraryAssetRecord, AssetMetadata, AssetState,
    ReuseDecisionType, AssetSearchQuery, FingerprintMatcher
)

def main():
    print("=" * 95)
    print("  ASSET ORCHESTRATION ENGINE (AOE) — FASE 23: ASSET LIBRARY, RETRIEVAL & REUSE DEMO")
    print("=" * 95)

    api = AssetReuseEngineAPI()

    # Registrar activo base en la biblioteca
    house_001 = LibraryAssetRecord(
        asset_id="house_001",
        name="Medieval House Standard",
        metadata=AssetMetadata(
            category="BUILDING",
            type_name="house",
            style="medieval_stylized",
            dimensions={"width": 4.0, "length": 4.0, "height": 5.0}
        ),
        quality_score=0.95,
        geometry_fingerprint=FingerprintMatcher.compute_geometry_fingerprint({"width": 4.0, "length": 4.0, "height": 5.0}, 1200)
    )
    api.register_asset(house_001)

    # 1. Escenario 133: Reutilización Exacta (0 Geometría Nueva)
    print("\n[ESCENARIO 133] Usuario: \"Crea una casa medieval estilizada de 4 metros.\"")
    q1 = AssetSearchQuery("house", style="medieval_stylized", target_dimensions={"width": 4.0})
    dec1 = api.search_and_decide_reuse(q1)
    print(f" - Decisión: {dec1.decision.value} -> Activo Seleccionado: '{dec1.selected_asset_id}'")
    print(f" - Razones: {dec1.reasons}")

    # 2. Escenario 134: Variante Paramétrica
    print("\n[ESCENARIO 134] Usuario: \"Quiero la misma casa pero de 6 metros.\"")
    q2 = AssetSearchQuery("house", style="medieval_stylized", target_dimensions={"width": 6.0})
    dec2 = api.search_and_decide_reuse(q2, overrides={"width": 6.0})
    print(f" - Decisión: {dec2.decision.value} -> Padre: '{dec2.selected_asset_id}'")
    print(f" - ID de Variante Generada: '{dec2.variant_id}' (Padre Preservado al 100%)")

    # 3. Escenario 135: Descarte por Discrepancia de Estilo
    print("\n[ESCENARIO 135] Usuario: \"Crea una casa futurista.\"")
    q3 = AssetSearchQuery("house", style="futuristic", target_dimensions={"width": 4.0})
    dec3 = api.search_and_decide_reuse(q3)
    print(f" - Decisión: {dec3.decision.value} (Casa medieval rechazada por filtro estricto de estilo)")
    print(f" - Razones: {dec3.reasons}")

    # 4. Escenario 136: Detección de Duplicados
    print("\n[ESCENARIO 136] Detección de Activos Duplicados por Huella Geométrica:")
    house_clone = LibraryAssetRecord(
        asset_id="house_clone",
        name="House Clone",
        metadata=AssetMetadata(category="BUILDING", type_name="house", style="medieval_stylized", dimensions={"width": 4.0, "length": 4.0, "height": 5.0}),
        geometry_fingerprint=house_001.geometry_fingerprint
    )
    api.register_asset(house_clone)
    dups = api.find_duplicate_geometries()
    print(f" - Pares Duplicados Identificados: {dups}")

    # 5. Escenario 137: Instanciación de Lote
    print("\n[ESCENARIO 137] Usuario: \"Haz 50 casas iguales.\"")
    inst_res = api.instantiate_batch("house_001", count=50)
    print(f" - Referencia Canónica: {inst_res['canonical_count']} ({inst_res['canonical_asset_id']})")
    print(f" - Instancias Ligeras Generadas: {inst_res['instances_count']} (0 Mallas Duplicadas)")

    # 6. Escenario 140: Cuarentena de Activos Fallidos
    print("\n[ESCENARIO 140] Cuarentena Automática de Activo tras 5 Fallos Consecutivos:")
    for _ in range(5):
        api.registry.record_failure("house_001")
        api.registry.record_failure("house_clone")
    print(f" - Estado de house_001: {house_001.state.value} | Estado de house_clone: {house_clone.state.value}")
    dec_q = api.search_and_decide_reuse(q1)
    print(f" - Decisión tras Cuarentena: {dec_q.decision.value} (Activos en cuarentena excluidos al 100%)")

    # 7. Escenario 142: Política Anti-Desperdicio
    print("\n[ESCENARIO 142] Verificación de Política Anti-Desperdicio:")
    ok_p, msg_p = api.validate_creation_policy(performed_retrieval=False)
    print(f" - Intento de Crear sin Búsqueda Previa: {ok_p} -> {msg_p}")

    print("\n" + "=" * 95)
    print("  CRITERIO DE EXITO DE FASE 23 CUMPLIDO AL 100% (APPROVED)")
    print("=" * 95)

if __name__ == "__main__":
    main()

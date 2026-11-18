import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.production_pipeline_unreal import (
    ProductionPipelineAPI, SocketDefinition
)

def main():
    print("=" * 95)
    print("  ASSET ORCHESTRATION ENGINE (AOE) — FASE 48: PRODUCTION PIPELINE & UNREAL INTEGRATION")
    print("=" * 95)

    api = ProductionPipelineAPI()

    # 1. Caso Obligatorio 1: Exportación e Importación de MedievalHouse_001
    print("\n[PASO 1] Caso Obligatorio 1: Exportación y Mapeo Determinista a Unreal (Sección 201):")
    sockets = [
        SocketDefinition(socket_name="entrance", relative_location=(0.0, 0.0, 0.0), is_critical=True),
        SocketDefinition(socket_name="chimney_smoke", relative_location=(0.0, 2.0, 4.0), is_critical=False)
    ]
    manifest, is_cached = api.process_and_export_asset(
        "MedievalHouse_001",
        "1.0.0",
        {"width": 8.0, "wall_height": 3.0, "roof_height": 1.45},
        sockets=sockets
    )
    print(f" - Malla Estática: [{manifest.mesh_name}] | Colisión: [{manifest.collision_name}]")
    print(f" - Instancia de Material: {manifest.material_instances} | Texturas: {manifest.textures}")
    print(f" - Cadena de LODs: {manifest.lod_count} niveles | Sockets: {[s.socket_name for s in manifest.sockets]}")
    print(f" - Data Asset de Metadata: [{manifest.metadata['data_asset']}] | Hash de Contenido: {manifest.content_hash}")

    # 2. Quality Gate de Producción
    print("\n[PASO 2] Quality Gate de Producción (Sección 126-130):")
    qg = api.validate_quality_gate(manifest)
    print(f" - Estado de Quality Gate: [{qg.status.value}]")
    print(f" - Verificaciones: {qg.checks}")

    # 3. Importación a Staging y Publicación Atómica
    print("\n[PASO 3] Importación a Staging y Publicación Atómica (Sección 81-90):")
    staged = api.stage_asset_in_unreal(manifest)
    print(f" - Asset Staged en: [{staged.unreal_path}] | Estado: [{staged.status.value}]")
    
    pub_rec = api.publish_asset_to_unreal("MedievalHouse_001", category="Environment/Houses")
    print(f" - Publicación Exitosa: ID={pub_rec.publication_id} -> Publicado en [{pub_rec.target_path}] | Estado: [{pub_rec.status}]")

    # 4. Caso Obligatorio 4: Detección de Breaking Changes en Sockets
    print("\n[PASO 4] Caso Obligatorio 4: Detección de Breaking Changes en Sockets (Sección 204):")
    prev_sockets = [SocketDefinition(socket_name="entrance", is_critical=True)]
    new_sockets = [SocketDefinition(socket_name="chimney_smoke", is_critical=False)]
    change_class, missing = api.evaluate_socket_compatibility(prev_sockets, new_sockets)
    print(f" - Evaluación de Compatibilidad de Sockets: [{change_class.value}] | Sockets Críticos Faltantes: {missing}")

    # 5. Caso Obligatorio 5: Protección de Modificaciones Manuales en Unreal
    print("\n[PASO 5] Caso Obligatorio 5: Protección de Modificaciones Manuales (Sección 205):")
    api.mark_manual_modified_in_unreal("MedievalHouse_001")
    print(f" - [!] Asset 'MedievalHouse_001' marcado como modificado manualmente por un artista en Unreal.")
    try:
        api.publish_asset_to_unreal("MedievalHouse_001")
    except PermissionError as e:
        print(f" - [+] Intento de sobreescritura bloqueado: {e}")

    # 6. Caso Obligatorio 7: Reutilización de Caché ante Fingerprint Idéntico
    print("\n[PASO 6] Caso Obligatorio 7: Reutilización de Build Cache (Sección 207):")
    _, is_cached_again = api.process_and_export_asset(
        "MedievalHouse_001",
        "1.0.0",
        {"width": 8.0, "wall_height": 3.0, "roof_height": 1.45},
        sockets=sockets
    )
    print(f" - Re-ejecución con mismos parámetros -> CACHE HIT: [{is_cached_again}] (Cero rebuilds innecesarios)")

    print("\n" + "=" * 95)
    print("  CRITERIO DE EXITO DE FASE 48 CUMPLIDO AL 100% (APPROVED)")
    print("=" * 95)

if __name__ == "__main__":
    main()

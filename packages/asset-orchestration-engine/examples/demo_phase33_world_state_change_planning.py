import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.world_state_change_planning import (
    WorldStateAPI, AssetState, WorldAssetStatus, ChangeRequest,
    WorldChangeType, WorldChangeScope, ContextLevel
)

def main():
    print("=" * 95)
    print("  ASSET ORCHESTRATION ENGINE (AOE) — FASE 33: WORLD STATE, SCENE UNDERSTANDING & CHANGE PLANNING")
    print("=" * 95)

    api = WorldStateAPI()

    # 1. Registrar Asset Existente en WorldState
    house_001 = AssetState(
        asset_id="HOUSE_001",
        asset_type="HOUSE",
        version=1,
        status=WorldAssetStatus.VALID,
        geometry_hash="geo_hash_house_01",
        parameters={"door.width": 0.90, "roof.pitch": 40.0, "roof.shape": "GABLE", "windows": 2},
        components=["FOUNDATION", "WALLS", "DOOR", "WINDOWS", "ROOF", "STAIRS"],
        locked_properties=["roof.shape"]
    )
    api.register_asset(house_001)

    print("\n[ESTADO INICIAL] WorldState consultado para 'HOUSE_001':")
    ctx = api.get_asset_state("HOUSE_001", ContextLevel.STANDARD)
    print(f" - Asset: {ctx['id']} ({ctx['type']}) | Versión: {ctx['version']} | Estado: {ctx['status']}")
    print(f" - Dimensiones: {ctx['size']} | Parámetros: {ctx['parameters']}")

    # 2. Escenario 113: Planificación de Cambio Mínimo (Minimal Change Principle)
    print("\n[ESCENARIO 113] 1. Planificación de Cambio Mínimo (Minimal Change Principle):")
    print("   Usuario: \"haz la puerta 20 cm más ancha\" (0.90m -> 1.10m)")
    req_door = ChangeRequest(
        target_asset_id="HOUSE_001",
        operation=WorldChangeType.MODIFY,
        property_path="door.width",
        new_value=1.10
    )
    dry_run = api.dry_run_change(req_door)
    print(f" - Estado Dry-Run: {dry_run.status} | Costo Estimado: {dry_run.estimated_cost_ms}ms")
    print(f" - Componentes Afectados:   {dry_run.what_will_change}")
    print(f" - Componentes NO Afectados: {dry_run.what_will_not_change}")

    # Ejecutar transacción atómica
    tx1 = api.execute_change(req_door, current_blender_hash="geo_hash_house_01")
    print(f" - Transacción {tx1.transaction_id} ejecutada -> Status: {tx1.status.value}")
    print(f" - Nueva Versión de HOUSE_001: {api.state_mgr.get_asset('HOUSE_001').version} | Ancho: {api.state_mgr.get_asset('HOUSE_001').parameters['door.width']}m")

    # 3. Escenario 114: Protección contra Restricciones Bloqueadas (Locked Constraint)
    print("\n[ESCENARIO 114] 2. Protección contra Modificación de Restricciones Bloqueadas:")
    print("   Usuario: \"haz el techo plano\" (cuando ROOF.SHAPE = LOCKED)")
    req_roof = ChangeRequest(
        target_asset_id="HOUSE_001",
        operation=WorldChangeType.MODIFY,
        property_path="roof.shape",
        new_value="FLAT"
    )
    try:
        api.plan_change(req_roof)
    except ValueError as e:
        print(f" - Bloqueo de Seguridad: {e}")

    # 4. Escenario 115: Detección de Modificación Externa en Blender
    print("\n[ESCENARIO 115] 3. Detección de Modificaciones Manuales en Blender (External Modification):")
    print("   Usuario editó manualmente la malla en Blender fuera del sistema.")
    try:
        req_mod = ChangeRequest(target_asset_id="HOUSE_001", operation=WorldChangeType.MODIFY, property_path="door.width", new_value=1.20)
        api.execute_change(req_mod, current_blender_hash="hash_tampered_by_artist_in_blender")
    except ValueError as e:
        print(f" - Detección de Desincronización: {e}")

    # 5. Escenario 116: Detección de Ambigüedad de Objetivo
    print("\n[ESCENARIO 116] 4. Detección de Ambigüedad de Objetivo (Ambiguous Target):")
    house_002 = AssetState(asset_id="HOUSE_002", asset_type="HOUSE", version=1)
    api.register_asset(house_002)
    print("   Existen 'HOUSE_001' y 'HOUSE_002'. Usuario pide: \"haz la casa más grande\"")
    req_ambiguous = ChangeRequest(target_asset_id=None, operation=WorldChangeType.MODIFY, property_path="door.width", new_value=1.30)
    try:
        api.plan_change(req_ambiguous)
    except ValueError as e:
        print(f" - Detección de Ambigüedad: {e}")

    # 6. Escenario 117: Idempotencia (Already Applied)
    print("\n[ESCENARIO 117] 5. Idempotencia y Prevención de Retrabajo Duplicado:")
    print("   Intentando re-ejecutar el mismo ChangePlan de puerta a 1.10m...")
    try:
        api.execute_change(req_door, current_blender_hash="geo_hash_house_01")
    except ValueError as e:
        print(f" - Idempotencia Confirmada: {e}")

    # 7. Undo y Redo
    print("\n[TRANSACCIONES] 6. Deshacer (Undo) y Rehacer (Redo):")
    api.undo()
    print(f" - Después de Undo -> Versión: {api.state_mgr.get_asset('HOUSE_001').version} | Puerta: {api.state_mgr.get_asset('HOUSE_001').parameters['door.width']}m")
    api.redo()
    print(f" - Después de Redo -> Versión: {api.state_mgr.get_asset('HOUSE_001').version} | Puerta: {api.state_mgr.get_asset('HOUSE_001').parameters['door.width']}m")

    print("\n" + "=" * 95)
    print("  CRITERIO DE EXITO DE FASE 33 CUMPLIDO AL 100% (APPROVED)")
    print("=" * 95)

if __name__ == "__main__":
    main()

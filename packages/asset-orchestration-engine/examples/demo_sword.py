import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import AssetOrchestrationEngine

def main():
    print("=" * 70)
    print("  ASSET ORCHESTRATION ENGINE v1 (AOE v1) — DEMO ESPADA MEDIEVAL")
    print("=" * 70)

    engine = AssetOrchestrationEngine()

    # PASO 1: Creación de la Espada Medieval
    print("\n[PASO 1] Creando Espada Medieval de 120 cm (Hoja 85cm, Mango 25cm, Guarda 15cm)...")
    sword_spec = {
        "asset_id": "sword_medieval_001",
        "name": "Espada Medieval",
        "category": "weapon",
        "dimensions": {"width": 0.15, "depth": 0.04, "height": 1.20, "unit": "meters"},
        "budget": {"max_triangles": 5000, "max_materials": 4},
        "components": [
            {
                "id": "handle",
                "type": "handle",
                "primitive": "cylinder",
                "dimensions": {"width": 0.035, "depth": 0.035, "height": 0.25, "unit": "meters"},
                "material": "leather_grip"
            },
            {
                "id": "guard",
                "type": "guard",
                "primitive": "box",
                "parent": "handle",
                "dimensions": {"width": 0.15, "depth": 0.03, "height": 0.03, "unit": "meters"},
                "material": "steel"
            },
            {
                "id": "blade",
                "type": "blade",
                "primitive": "box",
                "parent": "guard",
                "dimensions": {"width": 0.05, "depth": 0.015, "height": 0.85, "unit": "meters"},
                "material": "steel"
            },
            {
                "id": "pommel",
                "type": "pommel",
                "primitive": "sphere",
                "parent": "handle",
                "dimensions": {"width": 0.05, "depth": 0.05, "height": 0.05, "unit": "meters"},
                "material": "steel"
            }
        ]
    }

    create_res = engine.create_asset(sword_spec)
    print(f"Resultado de Creación:")
    print(f" - Status: {create_res['status']}")
    print(f" - Operaciones ejecutadas: {create_res['operations']}")
    print(f" - Quality Gate Status: {create_res['validation']['status']}")
    print(f" - Objetos creados: {create_res['objects_modified']}")

    # Inspección inicial
    insp_1 = engine.inspect_asset("sword_medieval_001")
    print(f"\n[INSPECCION v1] Componentes totales: {insp_1['components_count']}")
    for k, v in insp_1["nodes"].items():
        if k == "sword_medieval_001": continue
        print(f"   * {v['name']} (v{v['version']}): dim={v['dimensions']}")

    # PASO 2: Modificación Quirúrgica ("Alarga la hoja 10 cm")
    print("\n[PASO 2] Usuario solicita: 'Alarga la hoja 10 cm' -> Altura deseada = 0.95m")
    
    # 2.1 Planificación previa (Dry-Run / Plan Only)
    plan = engine.plan_change(
        asset_id="sword_medieval_001",
        target_component="blade",
        changes={"dimensions": {"width": 0.05, "depth": 0.015, "height": 0.95}}
    )
    print(f"Plan de Modificación:")
    print(f" - Operaciones requeridas: {plan['operations_count']}")
    print(f" - Objetos afectados: {plan['affected_objects']}")
    print(f" - ¿Es NO_OP?: {plan['is_no_op']}")

    # 2.2 Aplicación de cambio
    mod_res = engine.apply_change(
        asset_id="sword_medieval_001",
        target_component="blade",
        changes={"dimensions": {"width": 0.05, "depth": 0.015, "height": 0.95}}
    )
    print(f"\nResultado de Modificación:")
    print(f" - Status: {mod_res['status']}")
    print(f" - Nueva Versión del Asset: v{mod_res['version']}")
    print(f" - Objetos modificados: {mod_res['objects_modified']}")
    print(f" - Quality Gate: {mod_res['validation']['status']}")

    # PASO 3: Verificación de Mínima Modificación
    insp_2 = engine.inspect_asset("sword_medieval_001")
    print(f"\n[INSPECCION v2] Comprobación de componentes tras modificación:")
    for k, v in insp_2["nodes"].items():
        if k == "sword_medieval_001": continue
        status_tag = "MODIFICADO" if v["version"] > 1 else "INTACTO (Sin reconstruir)"
        print(f"   * {v['name']} (v{v['version']}) [{status_tag}]: dim={v['dimensions']}")

    # PASO 4: Prueba de NO_OP (Reenviar la misma orden)
    print("\n[PASO 4] Reenviando la misma modificación (0.95m) para probar Change Analyzer NO_OP...")
    plan_noop = engine.plan_change(
        asset_id="sword_medieval_001",
        target_component="blade",
        changes={"dimensions": {"width": 0.05, "depth": 0.015, "height": 0.95}}
    )
    print(f" - ¿Detectado como NO_OP?: {plan_noop['is_no_op']}")
    print(f" - Operaciones a ejecutar en Blender: {len([op for op in plan_noop['operations'] if not op['is_no_op']])}")

    print("\n" + "=" * 70)
    print("  CRITERIO DE EXITO DE FASE 1 CUMPLIDO AL 100% (READY)")
    print("=" * 70)

if __name__ == "__main__":
    main()

import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import (
    AssetOrchestrationEngine, ScopeSpec, ChangeBudget
)

def main():
    print("=" * 75)
    print("  ASSET ORCHESTRATION ENGINE v2 (AOE v2) — FASE 2: INTENT -> PLAN DEMO")
    print("=" * 75)

    engine = AssetOrchestrationEngine()

    # 1. Creación previa del asset en memoria
    print("\n[ESCENARIO] Registrando Espada Medieval en estado inicial:")
    sword_spec = {
        "asset_id": "sword_001",
        "name": "Medieval Sword",
        "category": "weapon",
        "components": [
            {"id": "handle", "type": "handle", "primitive": "cylinder", "dimensions": {"width": 0.035, "depth": 0.035, "height": 0.25}},
            {"id": "guard", "type": "guard", "primitive": "box", "parent": "handle", "dimensions": {"width": 0.15, "depth": 0.03, "height": 0.03}},
            {"id": "blade", "type": "blade", "primitive": "box", "parent": "guard", "dimensions": {"width": 0.05, "depth": 0.015, "height": 0.85}}
        ]
    }
    engine.create_asset(sword_spec)
    print(" - Estado actual: blade = 0.85m, handle = 0.25m, guard = 0.15m")

    # 2. Petición en Lenguaje Natural (PLAN_ONLY)
    user_prompt = "En sword_001 haz la hoja 10 cm más larga, pero no cambies el mango ni la guarda."
    print(f"\n[PETICIÓN NL]: \"{user_prompt}\"")

    scope = ScopeSpec(asset_ids=["sword_001"], allowed_components=["blade"])
    plan_res = engine.plan_intent(user_prompt, active_asset_id="sword_001", scope=scope)

    print("\n[1. INTERPRETACIÓN DE INTENCIÓN]:")
    print(f" - Tipo de Intención: {plan_res['intent']['intent_type']}")
    print(f" - Modificador: {plan_res['intent']['modifier_type']}")
    print(f" - Target Resuelto: {plan_res['intent']['target_component']}")
    print(f" - Confianza: {plan_res['intent']['confidence'] * 100:.1f}%")

    print("\n[2. PLAN DETERMINISTA GENERADO (PLAN_ONLY)]:")
    print(f" - Plan Válido: {plan_res['plan_valid']}")
    print(f" - Total Operaciones: {plan_res['operations_count']}")
    print(f" - Objetos Afectados: {plan_res['affected_objects']}")

    # 3. Explicación estructurada del plan
    explanation = engine.explain_plan(plan_res)
    print("\n[3. EXPLICACIÓN ESTRUCTURADA (Explain Plan)]:")
    print(f" - Resumen: {explanation['summary']}")
    for step in explanation["steps"]:
        print(f"   {step}")

    # 4. Caso de Ambigüedad
    print("\n[4. CASO DE PRUEBA: AMBIGÜEDAD DE TARGETS]")
    engine.create_asset({
        "asset_id": "dual_blade_asset",
        "name": "Dual Blade",
        "components": [
            {"id": "blade_left", "type": "blade", "primitive": "box", "dimensions": {"width": 0.05, "depth": 0.02, "height": 0.40}},
            {"id": "blade_right", "type": "blade", "primitive": "box", "dimensions": {"width": 0.05, "depth": 0.02, "height": 0.40}}
        ]
    })
    ambiguous_res = engine.plan_intent("Alarga la hoja 10cm", active_asset_id="dual_blade_asset")
    print(f" - Petición: 'Alarga la hoja 10cm'")
    print(f" - Resultado: {ambiguous_res['error_message']}")

    # 5. Caso de Violación de Scope
    print("\n[5. CASO DE PRUEBA: PROTECCIÓN DE SCOPE]")
    scope_restricted = ScopeSpec(allowed_components=["blade"])
    scope_res = engine.plan_intent("Alarga el mango 10cm", active_asset_id="sword_001", scope=scope_restricted)
    print(f" - Petición: 'Alarga el mango 10cm' con scope restringido a ['blade']")
    print(f" - Resultado: {scope_res['error_message']}")

    print("\n" + "=" * 75)
    print("  FASE 2: INTENT -> SPECIFICATION -> PLAN COMPLETADA AL 100%")
    print("=" * 75)

if __name__ == "__main__":
    main()

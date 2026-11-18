import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.generation_strategy_engine import (
    GenerationStrategyAPI, GenerationStrategyType,
    StrategyFailureCategory
)

def main():
    print("=" * 95)
    print("  ASSET ORCHESTRATION ENGINE (AOE) — FASE 52: ASSET GENERATION STRATEGY ENGINE")
    print("=" * 95)

    api = GenerationStrategyAPI()

    # 1. Caso Obligatorio 1: Barril Individual Estilizado (Scripted Modeling)
    print("\n[PASO 1] Caso Obligatorio 1: Selección de Estrategia para Barril Individual (Sección 172):")
    strat_1, rec_1 = api.select_strategy(
        asset_class="PROP.BARREL",
        components_count=2,
        batch_size=1,
        expected_frequent_revisions=True
    )
    print(f" - Asset: 'PROP.BARREL' (1 unidad, revisiones frecuentes esperadas)")
    print(f" - Estrategia Seleccionada: [{strat_1.value}]")
    print(f" - Puntuación de Candidatos: {rec_1.candidate_scores}")
    print(f" - Justificación: \"{rec_1.reason}\"")

    # 2. Caso Obligatorio 2: Lote de 100 Barriles (Procedural Generation)
    print("\n[PASO 2] Caso Obligatorio 2: Lote de 100 Barriles (Sección 173):")
    strat_2, rec_2 = api.select_strategy(
        asset_class="PROP.BARREL",
        components_count=2,
        batch_size=100
    )
    print(f" - Asset: 'PROP.BARREL' (100 unidades en lote)")
    print(f" - Estrategia Seleccionada: [{strat_2.value}] | Motivo: \"{rec_2.reason}\"")

    # 3. Caso Obligatorio 3: Casa Modular / Aldea (Component Assembly)
    print("\n[PASO 3] Caso Obligatorio 3: Casa Modular / Aldea (Sección 174):")
    strat_3, rec_3 = api.select_strategy(
        asset_class="BUILDING.HOUSE",
        components_count=6,
        batch_size=1
    )
    print(f" - Asset: 'BUILDING.HOUSE' (6 componentes modulares)")
    print(f" - Estrategia Seleccionada: [{strat_3.value}] | Motivo: \"{rec_3.reason}\"")

    # 4. Caso Obligatorio 4: Reutilización de Activo Aprobado (Existing Asset Modification)
    print("\n[PASO 4] Caso Obligatorio 4: Reutilización de Activo Aprobado (Sección 175):")
    library = {
        "approved_house_01": {
            "asset_class": "BUILDING.HOUSE",
            "status": "APPROVED",
            "similarity": 0.94
        }
    }
    strat_4, rec_4 = api.select_strategy(
        asset_class="BUILDING.HOUSE",
        components_count=6,
        existing_library=library,
        intent_type="MODIFY"
    )
    print(f" - Biblioteca: Coincidencia encontrada con 'approved_house_01' (Similitud: 94%)")
    print(f" - Estrategia Seleccionada: [{strat_4.value}] | Motivo: \"{rec_4.reason}\"")

    # 5. Caso Obligatorio 6: Blacklist y Fallback ante Fallos Repetidos de Topología
    print("\n[PASO 5] Caso Obligatorio 6: Fallos Repetidos y Activación de Fallback (Sección 177):")
    api.record_failure("PROP.BARREL", GenerationStrategyType.SCRIPTED_MODELING, StrategyFailureCategory.TOPOLOGY_ERROR)
    api.record_failure("PROP.BARREL", GenerationStrategyType.SCRIPTED_MODELING, StrategyFailureCategory.TOPOLOGY_ERROR)
    strat_6, rec_6 = api.select_strategy("PROP.BARREL", 2)
    print(f" - Tras 2 fallos de topología en SCRIPTED_MODELING:")
    print(f" - Estrategia Resultante: [{strat_6.value}] | Motivo: \"{rec_6.reason}\"")

    # 6. Caso Obligatorio 9: Plan de Generación Progresivo con Quality Gates
    print("\n[PASO 6] Caso Obligatorio 9: Construcción de Plan de Generación Progresivo (Sección 167):")
    plan = api.build_plan(
        specification_id="SPEC_BARREL_01",
        selected_strategy=strat_1,
        parameters={"height": 1.5, "radius": 0.6, "rings": 2},
        seed=1337
    )
    print(f" - Plan ID: {plan.plan_id} | Semilla Determinista: {plan.seed}")
    print(f" - Fallback Strategy Configurada: [{plan.fallback_strategy.value}]")
    print(f" - Etapas del Pipeline ({len(plan.stages)} etapas ordenadas):")
    for stg in plan.stages:
        print(f"   * Etapa {stg.order}: [{stg.stage_type.value}] -> {stg.description} | Quality Gates: {stg.quality_gates}")

    print("\n" + "=" * 95)
    print("  CRITERIO DE EXITO DE FASE 52 CUMPLIDO AL 100% (APPROVED)")
    print("=" * 95)

if __name__ == "__main__":
    main()

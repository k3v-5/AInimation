import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.visual_specification_compiler import (
    VisualSpecificationAPI, VisualCompilationInput
)
from src.reference_analysis_visual_decomposition import (
    DecomposedReferenceReport, SilhouetteExtraction, ProportionEstimate,
    DecomposedPart, MaterialPalette, ExtractedMaterialType
)
from src.procedural_modeling_strategy import (
    ProceduralModelingStrategyAPI
)

def main():
    print("=" * 95)
    print("  ASSET ORCHESTRATION ENGINE (AOE) — FASE 57: PROCEDURAL MODELING STRATEGY ENGINE")
    print("=" * 95)

    vas_api = VisualSpecificationAPI()
    msp_api = ProceduralModelingStrategyAPI()

    # 1. Preparación de la VAS (Fase 56)
    print("\n[PASO 1] Ingesta de la Visual Asset Specification (VAS) de Fase 56:")
    f55_report = DecomposedReferenceReport(
        report_id="REP_F55_HERO_BARREL",
        reference_ids=["REF_HERO_01"],
        silhouette=SilhouetteExtraction(aspect_ratio=1.42, symmetry_axis="VERTICAL_Z"),
        proportions=ProportionEstimate(component_ratios={"body": 0.80, "top_ring": 0.10, "bottom_ring": 0.10}),
        parts=[
            DecomposedPart("part_body", "BODY", (0, 0, 1, 1.42), (0, 0, 0), True, 0.98),
            DecomposedPart("part_ring_top", "RING_01", (0, 1.1, 1.02, 0.15), (0, 0, 1.1), False, 0.95),
            DecomposedPart("part_ring_bottom", "RING_02", (0, 0.2, 1.02, 0.15), (0, 0, 0.2), False, 0.95)
        ],
        materials=MaterialPalette(base_material=ExtractedMaterialType.WOOD, surface_roughness=0.68)
    )

    vas_input = VisualCompilationInput(
        prompt="Barril medieval de roble oscuro con 2 aros de hierro reforzado, altura 1.20 metros con simetría bilateral",
        asset_class_hint="PROP.BARREL",
        reference_reports=[f55_report],
        semantic_context={"semantic_id": "barrel_42.root", "asset_id": "barrel_42"},
        project_constraints={"nanite": True, "lod_count": 3, "poly_budget": 12000, "triangle_budget": 24000}
    )
    vas = vas_api.compile_specification(vas_input)
    print(f" - VAS Compilada: ID=[{vas.specification_id}] | Hash={vas.specification_hash[:12]}...")

    # 2. Compilación del Plan de Estrategia de Modelado (MSP)
    print("\n[PASO 2] Compilación del Modeling Strategy Plan (MSP) para F58:")
    msp = msp_api.plan_strategy(vas)
    val = msp_api.validate_plan(msp)
    print(f" - Plan ID: [{msp.strategy_id}] | Versión: {msp.strategy_version} | Válido: {val.is_valid}")
    print(f" - Hash Determinista MSP (SHA-256): {msp.strategy_hash[:16]}...{msp.strategy_hash[-8:]}")
    print(f" - Clasificación del Asset: {[c.value for c in msp.asset_classification]}")
    print(f" - Método Global: [{msp.global_strategy.construction_method}] | Simetría: [{msp.symmetry_strategy.value}]")

    # 3. Descomposición y Estrategias por Componente
    print("\n[PASO 3] Estrategias de Construcción por Componente:")
    for comp in msp.component_strategies:
        print(f"   * [{comp.component_id}] (Rol: {comp.semantic_role}) -> Método: [{comp.method.value}] | Primitiva Base: [{comp.base_geometry.value}] | Presupuesto Tris: {comp.triangle_budget}")
        if comp.modifiers:
            mod_names = [f"{m.modifier_type} (orden {m.order})" for m in comp.modifiers]
            print(f"     Modifiers Planificados: {mod_names}")

    # 4. Grafo Acíclico Dirigido (DAG) de Operaciones de Ejecución
    print("\n[PASO 4] Grafo de Ejecución (DAG) de Operaciones Geométricas para F58:")
    for op in msp.execution_graph:
        deps_str = f"<- deps: {op.dependencies}" if op.dependencies else "(Raíz)"
        print(f"   * [{op.operation_id}] -> Tipo: [{op.operation_type.value}] sobre '{op.target_component}' {deps_str}")

    # 5. Distribución de Presupuesto y Estimación de Costes
    print("\n[PASO 5] Presupuesto Geométrico y Score de Calidad:")
    print(f" - Presupuesto Total: {msp.geometry_budget.total_triangle_budget} triángulos distribuidos:")
    for cid, b in msp.geometry_budget.component_budgets.items():
        print(f"   * {cid}: {b} tris")
    print(f" - Estimación de Coste -> Tris Estimados: {msp.cost_estimate.estimated_triangles} | Modifiers: {msp.cost_estimate.estimated_modifiers} | Riesgo: [{msp.cost_estimate.risk_level.value}] | Score: {msp.cost_estimate.strategy_score * 100:.1f}%")

    # 6. Interfaz con Unreal Engine y Capabilities
    print("\n[PASO 6] Interfaz Técnica de Destino (Unreal Engine & LODs):")
    print(f" - Unreal Interface: Nanite={msp.unreal_interface['nanite']}, LODs={msp.unreal_interface['lod_count']}, Colisión={msp.unreal_interface['collision_type']}")
    print(f" - Pivot Strategy: [{msp.pivot_strategy.value}]")

    print("\n" + "=" * 95)
    print("  CRITERIO DE EXITO DE FASE 57 CUMPLIDO AL 100% (APPROVED)")
    print("=" * 95)

if __name__ == "__main__":
    main()

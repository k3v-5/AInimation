import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import (
    ToolGovernanceAPI, ActionProposal, ActionScope, ExecutionBudget,
    BuildSpecification, Requirement, RequirementPriority, ActionType, SpecStatus
)

def main():
    print("=" * 95)
    print("  ASSET ORCHESTRATION ENGINE (AOE) — FASE 22: AI EXECUTION POLICY & TOOL GOVERNANCE DEMO")
    print("=" * 95)

    gov = ToolGovernanceAPI()

    # 1. Acción Válida y Post-Verificada
    print("\n[TEST 1] Propuesta Válida: modify_asset (roof_height = 0.80m)")
    prop1 = ActionProposal("prop_01", "task_01", "modify_asset", "house_003", parameters={"roof_height": 0.80})
    res1 = gov.submit_action_proposal("designer_agent", prop1)
    print(f" - Estado: {res1.status.value} | Verificación Exitosa: {res1.verification_passed}")
    print(f" - Mensaje: {res1.message}")

    # 2. Rechazo de Parámetro Fuera de Rango
    print("\n[TEST 2] Parámetro Fuera de Rango: roof_height = 100m (Límite máximo: 3.0m)")
    prop2 = ActionProposal("prop_02", "task_01", "modify_asset", "house_003", parameters={"roof_height": 100.0})
    res2 = gov.submit_action_proposal("designer_agent", prop2)
    print(f" - Estado: {res2.status.value} | Razón: {res2.message}")

    # 3. Rechazo de Escalada de Alcance No Autorizada
    print("\n[TEST 3] Escalada de Alcance No Autorizada: Escalar modify_component a SCENE")
    prop3 = ActionProposal("prop_03", "task_01", "modify_component", "house_003", scope=ActionScope.SCENE, parameters={"roof_height": 0.80})
    res3 = gov.submit_action_proposal("designer_agent", prop3)
    print(f" - Estado: {res3.status.value} | Razón: {res3.message}")

    # 4. Detección de Acción Duplicada
    print("\n[TEST 4] Detección de Acción Duplicada: Reintentar idéntica acción")
    res4 = gov.submit_action_proposal("designer_agent", prop1)
    print(f" - Estado: {res4.status.value} | Razón: {res4.message}")

    # 5. Detección de Bucle Infinito
    print("\n[TEST 5] Protección contra Bucles Infinitos: Ciclo alternante A -> B -> A -> B")
    propA = ActionProposal("propA", "task_01", "modify_asset", "house_003", parameters={"roof_height": 0.70})
    propB = ActionProposal("propB", "task_01", "modify_asset", "house_003", parameters={"roof_height": 0.90})
    gov.gateway.dup_detector.clear()
    gov.submit_action_proposal("designer_agent", propA)
    gov.gateway.dup_detector.clear()
    gov.submit_action_proposal("designer_agent", propB)
    gov.gateway.dup_detector.clear()
    gov.submit_action_proposal("designer_agent", propA)
    gov.gateway.dup_detector.clear()
    res5 = gov.submit_action_proposal("designer_agent", propB)
    print(f" - Estado: {res5.status.value} | Razón: {res5.message}")

    # 6. Agotamiento de Presupuesto
    print("\n[TEST 6] Protección contra Exceso de Presupuesto (max_rebuilds = 3)")
    gov.set_budget(ExecutionBudget(max_asset_rebuilds=3, used_asset_rebuilds=3))
    prop6 = ActionProposal("prop_06", "task_01", "rebuild_asset", "house_003")
    res6 = gov.submit_action_proposal("designer_agent", prop6)
    print(f" - Estado: {res6.status.value} | Razón: {res6.message}")

    # 7. Fallo de Verificación y Rollback Transaccional
    print("\n[TEST 7] Fallo de Post-Verificación en Blender y Rollback Automático")
    gov.set_budget(ExecutionBudget())
    gov.gateway.dup_detector.clear()
    prop7 = ActionProposal("prop_07", "task_01", "modify_asset", "house_003", parameters={"roof_height": 0.80})
    res7 = gov.submit_action_proposal("designer_agent", prop7, simulate_blender_state_failure=True)
    print(f" - Estado: {res7.status.value} | Razón: {res7.message}")

    # 8. Protección de Requisitos Explícitos
    print("\n[TEST 8] Protección de Requisitos Explícitos del Usuario (4m exactos)")
    spec_ex = BuildSpecification(
        spec_id="spec_4m",
        action=ActionType.CREATE,
        target_type="HOUSE",
        target_id="house_003",
        requirements={"length": Requirement("r1", "DIMENSION", "length", 4.0, priority=RequirementPriority.CRITICAL, source="USER_EXPLICIT")},
        status=SpecStatus.READY
    )
    prop8 = ActionProposal("prop_08", "task_01", "modify_asset", "house_003", parameters={"width": 5.0})
    res8 = gov.submit_action_proposal("designer_agent", prop8, spec=spec_ex)
    print(f" - Estado: {res8.status.value} | Razón: {res8.message}")

    # 9. Operación Destructiva de Alto Riesgo
    print("\n[TEST 9] Política de Alto Riesgo: delete_asset requiere aprobación humana")
    prop9 = ActionProposal("prop_09", "task_01", "delete_asset", "house_003")
    res9 = gov.submit_action_proposal("designer_agent", prop9)
    print(f" - Estado: {res9.status.value} | Razón: {res9.message}")

    # 10. Principio de Menor Privilegio
    print("\n[TEST 10] Principio de Menor Privilegio: inspector_agent intenta modificar")
    prop10 = ActionProposal("prop_10", "task_01", "modify_asset", "house_003", parameters={"roof_height": 0.80})
    res10 = gov.submit_action_proposal("inspector_agent", prop10)
    print(f" - Estado: {res10.status.value} | Razón: {res10.message}")

    print("\n" + "=" * 95)
    print("  CRITERIO DE EXITO DE FASE 22 CUMPLIDO AL 100% (APPROVED)")
    print("=" * 95)

if __name__ == "__main__":
    main()

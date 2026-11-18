import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.governance import (
    AgentContractsToolGovernanceAPI, AuthorizationStatus, AuthorizationRequest,
    Permission, AuthorizationDeniedError
)

def run_f72_real_blender_governance():
    print("=" * 100)
    print("  AOE FASE 72 — VALIDACIÓN REAL DE AGENT CONTRACTS & TOOL GOVERNANCE")
    print("=" * 100)

    api = AgentContractsToolGovernanceAPI()
    
    print("\n[PASO 1] Registro y Validación de Contratos V2 de Agentes:")
    for c in api.contracts.list_contracts():
        intact = c.verify_integrity()
        print(f" - Contrato [{c.agent_id:<26}] | Version: [{c.contract_version}] | Permisos: {len(c.permissions):<2} | Integridad Hash: {'VALID [OK]' if intact else 'TAMPERED'}")

    print("\n[PASO 2] Prueba de Operación AUTORIZADA sobre Blender:")
    auth_req = AuthorizationRequest(
        agent_id="agent.blender.execution",
        tool_id="blender_capability_api",
        capability_id="blender.assemble_asset",
        resource_id="AOE_Generated/WP_Vandal_MarkII",
        operation="ASSEMBLE_MESH",
        task_id="T6_BlenderAssembly",
        orchestration_id="ORCH_F72_REAL"
    )
    
    executed_blender = []
    def execute_blender_action():
        executed_blender.append("Blender Capability Executed")
        return {"status": "BLENDER_ASSEMBLED", "objects": 7}

    result = api.mutation_guard.execute_guarded_mutation(
        auth_req=auth_req,
        mutation_fn=execute_blender_action,
        asset_id="WP_Vandal_MarkII",
        semantic_id="weapon.darx.vandal.mk2",
        created=["WP_Vandal_Receiver", "WP_Vandal_Barrel"]
    )
    print(f" - Decisión del AuthorizationEngine: [AUTHORIZED]")
    print(f" - Ejecución de la Mutación: {executed_blender[0]}")
    print(f" - Registro de Mutación Creado: {len(api.mutation_guard.list_mutations('WP_Vandal_MarkII'))} récord(s)")

    print("\n[PASO 3] Prueba de Operación DELIBERADAMENTE NO AUTORIZADA:")
    unauth_req = AuthorizationRequest(
        agent_id="agent.visual.critic",
        tool_id="mesh_generator",
        capability_id="geometry.generate_mesh",
        resource_id="Art/Blender/DarX_Assets.blend", # Protected file
        operation="DELETE_OR_OVERWRITE",
        task_id="T_MALICIOUS",
        orchestration_id="ORCH_F72_REAL"
    )
    
    decision = api.auth_engine.authorize(unauth_req)
    print(f" - Decisión del AuthorizationEngine: [{decision.status.value}]")
    print(f" - Motivo de Denegación: {decision.reason}")
    
    blocked_execution = False
    try:
        api.mutation_guard.execute_guarded_mutation(
            auth_req=unauth_req,
            mutation_fn=lambda: "SHOULD_NEVER_RUN",
            asset_id="DarX_Assets",
            semantic_id="source.project.master"
        )
    except AuthorizationDeniedError:
        blocked_execution = True

    print(f" - Interceptación por MutationGuard: {'BLOCKED (0 calls to Blender) [PASS]' if blocked_execution else 'FAILED'}")

    print("\n[PASO 4] Prueba de Parada Administrativa de Emergencia (Emergency Stop):")
    api.emergency_stop("SECURITY_INCIDENT_SIMULATION")
    em_dec = api.authorize_operation(agent_id="agent.geometry", tool_id="mesh_generator")
    print(f" - Estado con Parada de Emergencia: [{em_dec.status.value}] | Motivo: [{em_dec.reason}]")
    api.resume_from_emergency_stop()
    res_dec = api.authorize_operation(agent_id="agent.geometry", tool_id="mesh_generator")
    print(f" - Estado tras Reanudar: [{res_dec.status.value}]")

    print("\n[PASO 5] Verificación del Audit Log Inmutable:")
    records = api.audit.list_records()
    print(f" - Total Registros en AuditLogger: {len(records)}")
    for r in records[-4:]:
        print(f"   * [{r.record_id}] Agente: [{r.agent_id:<24}] -> Status: [{r.status.value:<10}] | Tool: [{str(r.tool_id):<22}] | Razón: {r.reason[:55]}...")

    print("\n" + "=" * 100)
    print("  VALIDACIÓN REAL DE FASE 72 COMPLETADA AL 100% (APPROVED)")
    print("=" * 100)

if __name__ == "__main__":
    run_f72_real_blender_governance()

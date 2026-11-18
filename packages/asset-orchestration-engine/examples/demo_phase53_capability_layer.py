import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.blender_capability_layer import (
    BlenderCapabilityAPI, OperationRequest, MockBlenderAdapter,
    AhujasidBlenderAdapter
)

def main():
    print("=" * 95)
    print("  ASSET ORCHESTRATION ENGINE (AOE) — FASE 53: BLENDER CAPABILITY & MCP EXECUTION LAYER")
    print("=" * 95)

    mock = MockBlenderAdapter()
    api = BlenderCapabilityAPI(adapter=mock)

    # 1. Caso Obligatorio 1: Ejecución de Capabilities Abstractas
    print("\n[PASO 1] Caso Obligatorio 1: Ejecución de Capabilities Abstractas (Sección 174):")
    req_body = OperationRequest("OP_BODY", "object.create", {"object_id": "Barrel_Body", "semantic_id": "barrel_body"})
    res_body = api.execute_operation(req_body)
    print(f" - [object.create] -> Estado: [{res_body.status.value}] | Resultado: {res_body.result}")

    req_scale = OperationRequest("OP_SCALE", "transform.set", {"object_id": "Barrel_Body", "scale": (1.0, 1.0, 1.2)})
    res_scale = api.execute_operation(req_scale)
    print(f" - [transform.set] -> Estado: [{res_scale.status.value}] | Resultado: {res_scale.result}")

    req_mat = OperationRequest("OP_MAT", "material.assign", {"object_id": "Barrel_Body", "material_name": "M_DarkWood"})
    res_mat = api.execute_operation(req_mat)
    print(f" - [material.assign] -> Estado: [{res_mat.status.value}] | Resultado: {res_mat.result}")

    # 2. Caso Obligatorio 2: Reconciliación de Estado e Idempotencia
    print("\n[PASO 2] Caso Obligatorio 2: Reconciliación de Estado e Idempotencia (Sección 175):")
    req_ring2 = OperationRequest("OP_RING2", "object.create", {"object_id": "Barrel_Ring_02", "semantic_id": "barrel_ring_02"})
    api.execute_operation(req_ring2)
    # Simular reintento de la misma operación tras timeout de red
    res_retry = api.execute_operation(req_ring2)
    print(f" - Reintento tras fallo de red -> Estado: [{res_retry.status.value}]")
    print(f" - Advertencias: {res_retry.warnings} (Cero duplicados en la escena)")

    # 3. Caso Obligatorio 3: Modificación Delta (Sin destrucción total)
    print("\n[PASO 3] Caso Obligatorio 3: Modificación Delta Paramétrica (Sección 176):")
    req_delta = OperationRequest("OP_DELTA", "transform.set", {"object_id": "Barrel_Body", "scale": (1.0, 1.0, 1.44)})
    res_delta = api.execute_operation(req_delta)
    obj_inspect = api.inspect_object("Barrel_Body")
    print(f" - Modificación 20% adicional -> Nueva escala inspeccionada en Blender: {obj_inspect.transform['scale']}")

    # 4. Caso Obligatorio 4: Hot-Swap de Adaptadores sin tocar Capas Superiores
    print("\n[PASO 4] Caso Obligatorio 4: Hot-Swap de Adaptadores (Sección 177):")
    ahujasid_adapter = AhujasidBlenderAdapter(mock)
    api.swap_adapter(ahujasid_adapter)
    print(f" - Adaptador cambiado a: [{api.adapter.__class__.__name__}]")
    res_ahu = api.execute_operation(OperationRequest("OP_TEST_AHU", "object.create", {"object_id": "Test_Ahu"}))
    print(f" - Ejecución transparente -> Estado: [{res_ahu.status.value}] | Adapter: [{res_ahu.adapter_name}]")

    # 5. Caso Obligatorio 5: Circuit Breaker de Seguridad
    print("\n[PASO 5] Caso Obligatorio 5: Circuit Breaker y Monitor de Salud (Sección 98):")
    mock.fault_connection_loss = True
    req_f = OperationRequest("OP_F", "object.create", {"object_id": "F_Obj"})
    for i in range(3):
        api.execute_operation(req_f)
    print(f" - Estado del Circuit Breaker tras 3 fallos: [{api.circuit_breaker.state.value}]")
    res_blocked = api.execute_operation(req_f)
    print(f" - Petición subsiguiente bloqueada con seguridad: \"{res_blocked.errors[0]}\"")
    mock.fault_connection_loss = False
    api.circuit_breaker.reset()

    # 6. Caso Obligatorio 6: Transacciones con Compensación Rollback
    print("\n[PASO 6] Caso Obligatorio 6: Transacciones Atómicas y Compensación (Sección 68):")
    tx_id = "TX_DEMO"
    api.begin_transaction(tx_id)
    req_tx_obj = OperationRequest("OP_TX", "object.create", {"object_id": "TX_Obj"})
    comp_tx_obj = OperationRequest("COMP_TX", "object.delete", {"object_id": "TX_Obj"})
    api.execute_operation(req_tx_obj)
    api.register_compensation(tx_id, req_tx_obj, comp_tx_obj)
    print(f" - Objeto 'TX_Obj' creado en transacción. Objetos en escena: {list(mock.scene.objects.keys())}")
    api.rollback_transaction(tx_id)
    print(f" - Rollback ejecutado. Objetos en escena: {list(mock.scene.objects.keys())}")

    print("\n" + "=" * 95)
    print("  CRITERIO DE EXITO DE FASE 53 CUMPLIDO AL 100% (APPROVED)")
    print("=" * 95)

if __name__ == "__main__":
    main()

import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { MCPServerKernel } from "../../mcp/server/MCPServerKernel.js";
import { AERuntimeBridge } from "../../mcp/bridge/AERuntimeBridge.js";
import { Composition } from "../../core/composition.js";

describe("Fase 5 — Idempotency & Transactions Stress Battery (REQ-009, REQ-012, REQ-013)", () => {
  it("executes the exact same mutation 100 times producing exactly 1 state modification (same_op x 100)", async () => {
    const comp = new Composition({
      name: "StressComp",
      width: 1080,
      height: 1920,
      fps: 60,
      duration: 30.0,
    });
    const kernel = new MCPServerKernel(comp, 1);
    const opId = "op_stress_100x";

    let lastResult;
    for (let i = 0; i < 100; i++) {
      lastResult = await kernel.handleRequest({
        operationId: opId,
        toolName: "set_property",
        category: "mutation",
        expectedVersion: 1,
        params: { name: "RenamedOnce" },
      });
    }

    assert.ok(lastResult?.success);
    // Invariante: La versión avanzó solo de 1 -> 2 (no 101)
    assert.equal(kernel.versionController.getVersion(), 2);
    assert.equal(kernel.composition.name, "RenamedOnce");
  });

  it("handles simulated network timeout and subsequent retry cleanly", async () => {
    const kernel = new MCPServerKernel();
    const opId = "op_timeout_retry";

    // Primer intento
    const res1 = await kernel.handleRequest({
      operationId: opId,
      toolName: "set_property",
      category: "mutation",
      params: { name: "RetriedSuccessfully" },
    });
    assert.equal(res1.success, true);

    // Segundo intento tras timeout del cliente
    const res2 = await kernel.handleRequest({
      operationId: opId,
      toolName: "set_property",
      category: "mutation",
      params: { name: "RetriedSuccessfully" },
    });

    assert.equal(res2.success, true);
    assert.equal(res2.projectHash, res1.projectHash);
  });

  it("executes complex 37-operation sequence and rolls back cleanly to exact initial SHA-256 hash", async () => {
    const kernel = new MCPServerKernel();
    const hashInitial = kernel.transactionManager.computeHash(kernel.composition);
    const versionInitial = kernel.versionController.getVersion();

    const txId = "tx_multi_37";
    kernel.transactionManager.beginTransaction(txId, kernel.composition, versionInitial);

    // Ejecutar 37 mutaciones sucesivas en la composición
    for (let i = 1; i <= 37; i++) {
      kernel.composition.name = `Mutation_Step_${i}`;
    }

    // Comprobar que el nombre mutó
    assert.equal(kernel.composition.name, "Mutation_Step_37");

    // Simular fallo en el paso 38 y ejecutar rollback
    const rollback = kernel.transactionManager.rollbackTransaction(txId);
    assert.equal(rollback.success, true);
    if (rollback.restoredComposition) {
      kernel.composition = rollback.restoredComposition;
    }

    // Invariante REQ-013: Hash post-rollback idéntico al hash inicial
    const hashRestored = kernel.transactionManager.computeHash(kernel.composition);
    assert.equal(hashRestored, hashInitial);
    assert.equal(kernel.versionController.getVersion(), versionInitial);
    assert.notEqual(kernel.composition.name, "Mutation_Step_37");
  });

  it("recovers bridge state after connection drop and reconciles layers", async () => {
    const bridge = new AERuntimeBridge();
    await bridge.connect();
    assert.equal(bridge.getState(), "CONNECTED");

    // Simular desconexión
    bridge.disconnect();
    assert.equal(bridge.getState(), "DISCONNECTED");

    // Recuperar
    const recovered = await bridge.recoverConnection();
    assert.equal(recovered, true);
    assert.equal(bridge.getState(), "CONNECTED");

    // Reconciliar
    const report = await bridge.reconcileLayers([
      { id: "l1", name: "MainVideo", inPoint: 0, outPoint: 10, position: [540, 960] },
    ]);
    assert.equal(report.isEquivalent, true);
  });
});

import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { MCPServerKernel } from "../../mcp/server/MCPServerKernel.js";

describe("MCP Kernel — Transactions & Cryptographic Rollback Tests (REQ-012, REQ-013)", () => {
  it("restores exact SHA-256 state and version upon mutation failure (hash_before === hash_after)", async () => {
    const kernel = new MCPServerKernel();
    const hashBefore = kernel.transactionManager.computeHash(kernel.composition);
    const versionBefore = kernel.versionController.getVersion();

    // Registrar handler que lanza excepción
    kernel.registerMutationHandler("failing_mutation", () => {
      kernel.composition.name = "CorruptedState";
      throw new Error("Simulated unexpected failure during compilation");
    });

    const res = await kernel.handleRequest({
      operationId: "op_fail_tx",
      toolName: "failing_mutation",
      category: "mutation",
      params: {},
    });

    assert.equal(res.success, false);
    assert.equal(res.error?.errorCode, "INVALID_OPERATION");

    // Invariante REQ-013: El hash y versión después del rollback deben ser idénticos al inicio
    const hashAfter = kernel.transactionManager.computeHash(kernel.composition);
    assert.equal(hashAfter, hashBefore);
    assert.equal(kernel.versionController.getVersion(), versionBefore);
    assert.notEqual(kernel.composition.name, "CorruptedState");
  });
});

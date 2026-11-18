import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { MCPServerKernel } from "../../mcp/server/MCPServerKernel.js";

describe("MCP Kernel — Idempotency & Deduplication Tests (REQ-009, REQ-011)", () => {
  it("returns cached result without re-executing when sending duplicate operation_id", async () => {
    const kernel = new MCPServerKernel();

    // Primera ejecución
    const res1 = await kernel.handleRequest({
      operationId: "op_idempotent_100",
      toolName: "set_property",
      category: "mutation",
      params: { name: "FirstPass" },
    });

    assert.equal(res1.success, true);
    assert.equal(res1.projectVersion, 2);

    // Segunda ejecución con mismo operation_id
    const res2 = await kernel.handleRequest({
      operationId: "op_idempotent_100",
      toolName: "set_property",
      category: "mutation",
      params: { name: "SecondPassIgnored" },
    });

    assert.equal(res2.success, true);
    assert.equal(res2.projectVersion, 2, "Expected version NOT to advance on duplicate operation_id");
    assert.equal(kernel.composition.name, "FirstPass", "Expected state not to be overwritten");
  });
});

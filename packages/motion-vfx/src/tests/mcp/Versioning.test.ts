import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { MCPServerKernel } from "../../mcp/server/MCPServerKernel.js";

describe("MCP Kernel — Optimistic Concurrency & Versioning Tests (REQ-010)", () => {
  it("rejects stale operations with structured VERSION_CONFLICT error", async () => {
    const kernel = new MCPServerKernel(undefined, 5);

    const res = await kernel.handleRequest({
      operationId: "op_stale",
      toolName: "set_property",
      category: "mutation",
      expectedVersion: 4, // Stale version
      params: { name: "ConflictName" },
    });

    assert.equal(res.success, false);
    assert.equal(res.error?.errorCode, "VERSION_CONFLICT");
    assert.equal(res.error?.recoverable, true);
    assert.ok(res.error?.suggestedActions.includes("inspect_project"));
  });
});

import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { MCPServerKernel } from "../../mcp/server/MCPServerKernel.js";
import { Composition } from "../../core/composition.js";

describe("MCP Kernel — Server Pipeline & Safety Tests", () => {
  it("processes valid mutation and advances version monotonically", async () => {
    const comp = new Composition({
      name: "InitialComp",
      width: 1080,
      height: 1920,
      fps: 60,
      duration: 10.0,
    });
    const kernel = new MCPServerKernel(comp, 1);

    const res = await kernel.handleRequest({
      operationId: "op_001",
      toolName: "set_property",
      category: "mutation",
      expectedVersion: 1,
      params: { name: "RenamedComp" },
    });

    assert.equal(res.success, true);
    assert.equal(res.projectVersion, 2);
    assert.equal(kernel.composition.name, "RenamedComp");
  });

  it("blocks dangerous payloads with forbidden tokens (eval/exec)", async () => {
    const kernel = new MCPServerKernel();

    const res = await kernel.handleRequest({
      operationId: "op_bad",
      toolName: "set_property",
      category: "mutation",
      params: { code: "eval('process.exit()')" },
    });

    assert.equal(res.success, false);
    assert.equal(res.error?.errorCode, "UNAUTHORIZED_CAPABILITY");
  });

  it("handles dry-run requests without mutating state or advancing version", async () => {
    const kernel = new MCPServerKernel();
    const initialVersion = kernel.versionController.getVersion();
    const initialHash = kernel.transactionManager.computeHash(kernel.composition);

    const res = await kernel.handleRequest({
      operationId: "op_dry",
      toolName: "set_property",
      category: "mutation",
      dryRun: true,
      params: { name: "ShouldNotApply" },
    });

    assert.equal(res.success, true);
    assert.equal(res.projectVersion, initialVersion);
    assert.equal(res.projectHash, initialHash);
    assert.ok(res.dryRunReport);
  });
});

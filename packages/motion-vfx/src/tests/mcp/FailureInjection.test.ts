import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { MCPServerKernel } from "../../mcp/server/MCPServerKernel.js";
import { AERuntimeBridge } from "../../mcp/bridge/AERuntimeBridge.js";
import { AutonomousAgentLoop } from "../../mcp/agent/AutonomousAgentLoop.js";

describe("Fase 9 — Failure Injection & Chaos Engineering Suite (Failure Handling & Recovery)", () => {
  it("recovers gracefully from unauthorized token injection and prevents execution", async () => {
    const kernel = new MCPServerKernel();
    const initialHash = kernel.transactionManager.computeHash(kernel.composition);

    const res = await kernel.handleRequest({
      operationId: "chaos_eval",
      toolName: "set_property",
      category: "mutation",
      params: { maliciousPayload: "child_process.execSync('rm -rf /')" },
    });

    assert.equal(res.success, false);
    assert.equal(res.error?.errorCode, "UNAUTHORIZED_CAPABILITY");
    // Invariante: El hash no cambió
    assert.equal(kernel.transactionManager.computeHash(kernel.composition), initialHash);
  });

  it("handles stale version conflict and instructs agent on recovery actions", async () => {
    const kernel = new MCPServerKernel(undefined, 10);

    const res = await kernel.handleRequest({
      operationId: "chaos_stale_v",
      toolName: "set_property",
      category: "mutation",
      expectedVersion: 9, // Obsoleto
      params: { name: "ShouldFail" },
    });

    assert.equal(res.success, false);
    assert.equal(res.error?.errorCode, "VERSION_CONFLICT");
    assert.equal(res.error?.recoverable, true);
    assert.ok(res.error?.suggestedActions.includes("inspect_project"));
  });

  it("handles bridge disconnection without crashing server", async () => {
    const bridge = new AERuntimeBridge();
    // Estado inicial desconectado
    assert.equal(bridge.getState(), "DISCONNECTED");

    const res = await bridge.sendCommand({
      jsonrpc: "2.0",
      id: "cmd_fail",
      method: "query_comp",
    });

    assert.ok(res.error);
    assert.equal(res.error?.errorCode, "AE_DISCONNECTED");
  });

  it("executes the AutonomousAgentLoop successfully under valid creative brief", async () => {
    const loop = new AutonomousAgentLoop();
    const result = await loop.executeAutonomousProduction({
      title: "GUADALAJARA MASTER REEL",
      targetAspectRatios: ["9:16", "16:9"],
      stylePreset: "teal_orange",
      includeCaptions: true,
      includeSFX: true,
      includeDepthSandwich: true,
    });

    assert.equal(result.success, true);
    assert.ok(result.executedSteps.length >= 8);
    assert.ok(result.executedSteps.includes("ae_sync_to_beats"));
    assert.ok(result.executedSteps.includes("ae_auto_reframe"));
    assert.ok(result.executedSteps.includes("ae_create_depth_sandwich"));
    assert.ok(result.executedSteps.includes("ae_generate_captions"));
    assert.ok(result.executedSteps.includes("ae_apply_color_grade"));
    assert.ok(result.executedSteps.includes("ae_add_sfx_sound_design"));
    assert.ok(result.executedSteps.includes("ae_export_omni"));
    assert.ok(result.qaScore >= 85.0);
    assert.equal(result.omniExportReady, true);
  });
});

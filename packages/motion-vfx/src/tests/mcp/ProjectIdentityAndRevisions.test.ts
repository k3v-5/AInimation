import { describe, it, beforeEach } from "node:test";
import assert from "node:assert/strict";
import { MCPProjectSnapshot, MCPProjectStore, ProjectIdentityInput } from "../../mcp/types.js";

describe("Fase 17 — Project Identity & Immutable Revisions Tests", () => {
  beforeEach(() => {
    MCPProjectStore.clear();
  });

  it("computes deterministic projectId from canonical identity inputs", () => {
    const inputA: ProjectIdentityInput = {
      script: "Guion de prueba viral",
      styleId: "fast-tiktok",
      durationTarget: 30,
      aspectRatio: "9:16",
      fps: 30,
      seed: 42,
    };

    const inputB: ProjectIdentityInput = {
      fps: 30,
      aspectRatio: "9:16",
      seed: 42,
      durationTarget: 30,
      styleId: "fast-tiktok",
      script: "Guion de prueba viral",
    };

    const idA = MCPProjectStore.computeProjectId(inputA);
    const idB = MCPProjectStore.computeProjectId(inputB);

    assert.ok(idA.startsWith("proj_"));
    assert.equal(idA, idB, "Permutation of JSON object keys must produce the exact same projectId");
  });

  it("manages immutable revision progression without in-place mutation", () => {
    const projectId = "proj_test_123";

    const snapshot1: MCPProjectSnapshot = {
      projectId,
      revisionId: "rev_001",
      parentRevisionId: undefined,
      operation: "create",
      createdAt: new Date().toISOString(),
      ir: { id: "comp_1", duration: 10, layers: [] },
      summary: { duration: 10, width: 1080, height: 1920, fps: 30, layerCount: 0 },
    };

    MCPProjectStore.saveRevision(snapshot1);

    const snapshot2: MCPProjectSnapshot = {
      projectId,
      revisionId: "rev_002",
      parentRevisionId: "rev_001",
      operation: "apply_preset",
      createdAt: new Date().toISOString(),
      ir: { id: "comp_1", duration: 10, layers: [{ id: "l1" }] },
      summary: { duration: 10, width: 1080, height: 1920, fps: 30, layerCount: 1 },
    };

    MCPProjectStore.saveRevision(snapshot2);

    const rev1 = MCPProjectStore.getRevision(projectId, "rev_001");
    const rev2 = MCPProjectStore.getRevision(projectId, "rev_002");
    const latest = MCPProjectStore.getRevision(projectId);

    assert.equal(rev1?.revisionId, "rev_001");
    assert.equal(rev1?.summary.layerCount, 0);

    assert.equal(rev2?.revisionId, "rev_002");
    assert.equal(rev2?.parentRevisionId, "rev_001");
    assert.equal(rev2?.summary.layerCount, 1);

    assert.equal(latest?.revisionId, "rev_002");

    const allRevs = MCPProjectStore.listRevisions(projectId);
    assert.equal(allRevs.length, 2);
  });
});

import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { StateReconciler } from "../../mcp/reconciliation/StateReconciler.js";

describe("MCP Kernel — State Reconciliation Tests (REQ-018, REQ-021)", () => {
  it("reconciles matching states within float tolerance as PASS", () => {
    const expected = [
      { id: "layer_1", name: "TextHero", inPoint: 0.0, outPoint: 5.0, position: [540, 960] as [number, number] },
    ];

    const actual = [
      { index: 1, name: "TextHero", inPoint: 0.0, outPoint: 5.0, position: [540.02, 960.01] as [number, number] }, // delta = 0.022px <= 0.05px
    ];

    const report = StateReconciler.reconcile(expected, actual);
    assert.equal(report.isEquivalent, true);
    assert.equal(report.status, "pass");
    assert.equal(report.discrepancies.length, 0);
  });

  it("detects spatial mismatch when discrepancy exceeds tolerance threshold", () => {
    const expected = [
      { id: "layer_1", name: "TextHero", inPoint: 0.0, outPoint: 5.0, position: [540, 960] as [number, number] },
    ];

    const actual = [
      { index: 1, name: "TextHero", inPoint: 0.0, outPoint: 5.0, position: [600, 960] as [number, number] }, // delta = 60px > 0.05px
    ];

    const report = StateReconciler.reconcile(expected, actual);
    assert.equal(report.isEquivalent, false);
    assert.equal(report.status, "mismatch");
    assert.ok(report.discrepancies.length > 0);
  });
});

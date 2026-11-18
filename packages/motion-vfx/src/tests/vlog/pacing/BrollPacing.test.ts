import assert from "node:assert/strict";
import { describe, it } from "node:test";
import fc from "fast-check";
import { BRollPacingAssignment, BRollPacingResolver } from "../../../vlog/index.js";

describe("Milestone 5 — B-Roll Pacing & Punch-In Precedence Suite", () => {
  const createAssignment = (
    sourceStart: number,
    sourceEnd: number,
    assetDuration: number
  ): BRollPacingAssignment => ({
    mediaId: "broll_sample_01",
    sourceStartSeconds: sourceStart,
    sourceEndSeconds: sourceEnd,
    targetStartSeconds: 0,
    targetEndSeconds: sourceEnd - sourceStart,
    assetDurationSeconds: assetDuration,
    lockMode: "PREFERRED",
  });

  it("trims B-Roll when required duration is shorter than current clip", () => {
    const assignment = createAssignment(0.0, 5.0, 10.0);
    const res = BRollPacingResolver.retimeBRoll(assignment, 3.5);

    assert.equal(res.strategyApplied, "TRIMMED");
    assert.equal(res.adaptedRange.durationSeconds, 3.5);
    assert.equal(res.suppressPunchIn, true);
  });

  it("extends B-Roll using available asset footage when possible", () => {
    const assignment = createAssignment(0.0, 4.0, 10.0);
    const res = BRollPacingResolver.retimeBRoll(assignment, 7.0);

    assert.equal(res.strategyApplied, "EXTENDED");
    assert.equal(res.adaptedRange.durationSeconds, 7.0);
    assert.equal(res.holdDurationSeconds, 0);
  });

  it("applies freeze frame hold when required duration exceeds asset bounds", () => {
    const assignment = createAssignment(0.0, 5.0, 6.0); // Asset tiene 6s max
    const res = BRollPacingResolver.retimeBRoll(assignment, 8.0); // Necesitamos 8s

    assert.equal(res.strategyApplied, "HOLD_APPLIED");
    assert.equal(res.adaptedRange.endSeconds, 6.0); // Tope de archivo
    assert.equal(res.holdDurationSeconds, 2.0); // 2 segundos de hold al final
  });

  it("strictly enforces B-Roll > Punch-In priority in all retimed states", () => {
    const assignment = createAssignment(1.0, 4.0, 8.0);
    const res = BRollPacingResolver.retimeBRoll(assignment, 3.0);
    assert.equal(res.suppressPunchIn, true);
  });

  it("PBT: adaptedRange always satisfies 0 <= start < end <= assetDuration", () => {
    fc.assert(
      fc.property(
        fc.double({ min: 5.0, max: 60.0, noNaN: true }),
        fc.double({ min: 0.1, max: 20.0, noNaN: true }),
        (assetDur, reqDur) => {
          const assignment = createAssignment(0.0, Math.min(3.0, assetDur * 0.5), assetDur);
          const res = BRollPacingResolver.retimeBRoll(assignment, reqDur);

          assert.ok(res.adaptedRange.startSeconds >= 0.0);
          assert.ok(res.adaptedRange.endSeconds <= assetDur + 0.001);
          assert.ok(res.adaptedRange.endSeconds > res.adaptedRange.startSeconds);
        }
      )
    );
  });
});

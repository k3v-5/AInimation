import assert from "node:assert/strict";
import { describe, it } from "node:test";
import fc from "fast-check";
import { VisualRetimingResolver } from "../../../vlog/index.js";

describe("Milestone 5 — Visual Retiming Suite", () => {
  it("trims clip when target duration is shorter than source", () => {
    const res = VisualRetimingResolver.resolve("clip_01", 5.0, 3.0);
    assert.equal(res.action, "TRIM");
    assert.equal(res.isPossible, true);
    assert.equal(res.targetDurationSeconds, 3.0);
  });

  it("extends clip using available source media without freeze frame", () => {
    // Necesitamos 6.0s de un clip de 4.0s, pero el asset tiene 10.0s en total
    const res = VisualRetimingResolver.resolve("clip_02", 4.0, 6.0, 10.0);
    assert.equal(res.action, "EXTEND");
    assert.equal(res.isPossible, true);
    assert.equal(res.holdDurationSeconds, 0);
  });

  it("applies freeze frame hold when extension is within maxHoldDurationSeconds", () => {
    // Requiere 1.2s de extensión (<= maxHold de 2.0s)
    const res = VisualRetimingResolver.resolve("clip_03", 3.0, 4.2, 3.0, {
      maxHoldDurationSeconds: 2.0,
    });
    assert.equal(res.action, "HOLD");
    assert.equal(res.isPossible, true);
    assert.equal(res.holdDurationSeconds, 1.2);
  });

  it("fails with NO_VALID_SOLUTION when required hold exceeds maxHoldDurationSeconds", () => {
    // Requiere 3.5s de extensión (> maxHold de 2.0s y excede minSpeed de 0.75x)
    const res = VisualRetimingResolver.resolve("clip_04", 3.0, 6.5, 3.0, {
      maxHoldDurationSeconds: 2.0,
      minSpeedFactor: 0.75,
    });
    assert.equal(res.action, "NO_VALID_SOLUTION");
    assert.equal(res.isPossible, false);
    assert.ok(res.reason.includes("exceeds max hold"));
  });

  it("slows down clip when within permissible speed limits", () => {
    // Source 4.0s a target 4.8s (speed = 4.0 / 4.8 = 0.833x >= 0.75x minSpeed, con allowHold=false)
    const res = VisualRetimingResolver.resolve("clip_05", 4.0, 4.8, 4.0, {
      allowHold: false,
      minSpeedFactor: 0.75,
    });
    assert.equal(res.action, "SLOW_DOWN");
    assert.equal(res.isPossible, true);
    assert.ok(res.speedFactor >= 0.75);
  });

  it("PBT: retiming decision never produces zero or negative target duration when inputs are positive", () => {
    fc.assert(
      fc.property(
        fc.double({ min: 0.5, max: 20.0, noNaN: true }),
        fc.double({ min: 0.5, max: 20.0, noNaN: true }),
        (src, tgt) => {
          const res = VisualRetimingResolver.resolve("pbt_clip", src, tgt);
          assert.ok(res.targetDurationSeconds > 0);
          assert.ok(!isNaN(res.targetDurationSeconds));
          assert.ok(isFinite(res.targetDurationSeconds));
        }
      )
    );
  });
});

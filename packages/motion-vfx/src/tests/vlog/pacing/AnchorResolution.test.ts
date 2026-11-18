import assert from "node:assert/strict";
import { describe, it } from "node:test";
import fc from "fast-check";
import { AnchorResolver, NarrativeAnchor } from "../../../vlog/index.js";

describe("Milestone 5 — Narrative Anchor Resolution Suite", () => {
  const createAnchor = (id: string, targetTime: number, locked = false): NarrativeAnchor => ({
    id,
    type: "HOOK",
    sourceTimeSeconds: targetTime,
    targetTimeSeconds: targetTime,
    priority: 5,
    locked,
  });

  it("classifies drift <= 40ms as OK", () => {
    const anchor = createAnchor("a1", 5.0, true);
    const res = AnchorResolver.evaluateAnchor(anchor, 5.025); // +25ms

    assert.equal(res.status, "OK");
    assert.equal(res.isCompliant, true);
    assert.equal(res.driftSeconds, 0.025);
  });

  it("classifies 40ms < drift <= 100ms as WARNING (compliant if flexible, non-compliant if locked)", () => {
    // Flexible
    const anchorFlex = createAnchor("a_flex", 5.0, false);
    const resFlex = AnchorResolver.evaluateAnchor(anchorFlex, 5.080); // +80ms
    assert.equal(resFlex.status, "WARNING");
    assert.equal(resFlex.isCompliant, true);

    // Locked
    const anchorLocked = createAnchor("a_locked", 5.0, true);
    const resLocked = AnchorResolver.evaluateAnchor(anchorLocked, 5.080); // +80ms
    assert.equal(resLocked.status, "WARNING");
    assert.equal(resLocked.isCompliant, false); // Locked no tolera warning sin conflicto
  });

  it("classifies 100ms < drift <= 250ms as ERROR and > 250ms as FATAL", () => {
    const anchor = createAnchor("a2", 10.0, false);

    // 150ms drift -> ERROR
    const resError = AnchorResolver.evaluateAnchor(anchor, 10.150);
    assert.equal(resError.status, "ERROR");
    assert.equal(resError.isCompliant, false);

    // 350ms drift -> FATAL
    const resFatal = AnchorResolver.evaluateAnchor(anchor, 10.350);
    assert.equal(resFatal.status, "FATAL");
    assert.equal(resFatal.isCompliant, false);
  });

  it("PBT: compliance strictly requires |drift| <= 0.040s when locked=true", () => {
    fc.assert(
      fc.property(
        fc.double({ min: 1.0, max: 100.0, noNaN: true }),
        fc.double({ min: -0.5, max: 0.5, noNaN: true }),
        (targetTime, drift) => {
          const anchor = createAnchor("pbt_anchor", targetTime, true);
          const actualTime = targetTime + drift;
          const res = AnchorResolver.evaluateAnchor(anchor, actualTime);

          if (Math.abs(drift) <= 0.040) {
            assert.equal(res.isCompliant, true);
          } else {
            assert.equal(res.isCompliant, false);
          }
        }
      )
    );
  });
});

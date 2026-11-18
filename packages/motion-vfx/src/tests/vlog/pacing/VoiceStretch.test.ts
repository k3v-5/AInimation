import assert from "node:assert/strict";
import { describe, it } from "node:test";
import fc from "fast-check";
import { VoiceStretchResolver } from "../../../vlog/index.js";

describe("Milestone 5 — Voice Stretch Suite", () => {
  it("accepts exact bounds 0.95x and 1.05x in automatic mode", () => {
    // Exactamente 0.95x: voz 9.5s, visual 10.0s
    const resMin = VoiceStretchResolver.evaluateStretch(9.5, 10.0, false);
    assert.equal(resMin.applied, true);
    assert.equal(resMin.mode, "AUTOMATIC");
    assert.equal(resMin.ratio, 0.95);

    // Exactamente 1.05x: voz 10.5s, visual 10.0s
    const resMax = VoiceStretchResolver.evaluateStretch(10.5, 10.0, false);
    assert.equal(resMax.applied, true);
    assert.equal(resMax.mode, "AUTOMATIC");
    assert.equal(resMax.ratio, 1.05);
  });

  it("applies automatic stretch for slight disparities (1.02x and 0.98x)", () => {
    const res1 = VoiceStretchResolver.evaluateStretch(10.2, 10.0, false);
    assert.equal(res1.applied, true);
    assert.equal(res1.ratio, 1.02);

    const res2 = VoiceStretchResolver.evaluateStretch(9.8, 10.0, false);
    assert.equal(res2.applied, true);
    assert.equal(res2.ratio, 0.98);
  });

  it("rejects ratios outside [0.95, 1.05] when allowManualOverride is false", () => {
    // 1.10x
    const resHigh = VoiceStretchResolver.evaluateStretch(11.0, 10.0, false);
    assert.equal(resHigh.applied, false);
    assert.equal(resHigh.mode, "AUTOMATIC");
    assert.ok(resHigh.reason.includes("exceeds permissible voice elasticity"));

    // 0.90x
    const resLow = VoiceStretchResolver.evaluateStretch(9.0, 10.0, false);
    assert.equal(resLow.applied, false);
  });

  it("permits hard limits [0.85, 1.15] only when allowManualOverride is true", () => {
    // 1.10x con override
    const resOverride = VoiceStretchResolver.evaluateStretch(11.0, 10.0, true);
    assert.equal(resOverride.applied, true);
    assert.equal(resOverride.mode, "MANUAL_OVERRIDE");

    // 1.25x incluso con override debe ser rechazado
    const resExtreme = VoiceStretchResolver.evaluateStretch(12.5, 10.0, true);
    assert.equal(resExtreme.applied, false);
  });

  it("PBT: for any duration ratio strictly within [0.95, 1.05], applied is guaranteed", () => {
    fc.assert(
      fc.property(
        fc.double({ min: 1.0, max: 60.0, noNaN: true }),
        fc.double({ min: 0.951, max: 1.049, noNaN: true }),
        (visualDur, factor) => {
          const voiceDur = visualDur * factor;
          const res = VoiceStretchResolver.evaluateStretch(voiceDur, visualDur, false);
          assert.equal(res.applied, true);
          assert.equal(res.mode, "AUTOMATIC");
        }
      )
    );
  });
});

import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { DynamicSpeedRampEngine } from "../../timeline/speed/DynamicSpeedRampEngine.js";

describe("Timeline — DynamicSpeedRampEngine Tests", () => {
  it("calculates continuous speed ramp points with whip-slowmo-whip profile", () => {
    const points = DynamicSpeedRampEngine.calculateRampCurve(0.0, 4.0, 10.0, {
      name: "whip_slowmo_whip",
      description: "Fast in -> SlowMo -> Fast Out",
      whipInSpeed: 3.0,
      slowMoSpeed: 0.3,
      whipOutSpeed: 2.5,
    });

    assert.equal(points.length, 4);
    assert.equal(points[0].compTime, 0.0);
    assert.equal(points[0].sourceTime, 0.0);

    // Source time must be monotonically increasing
    for (let i = 1; i < points.length; i++) {
      assert.ok(
        points[i].sourceTime >= points[i - 1].sourceTime,
        `Expected monotonic source time progression at step ${i}`
      );
      assert.ok(
        points[i].compTime > points[i - 1].compTime,
        `Expected increasing comp time progression at step ${i}`
      );
    }
  });

  it("generates well-formed ExtendScript snippet for timeRemap", () => {
    const snippet = DynamicSpeedRampEngine.generateExtendScriptSpeedRamp("clipLayer", 0.0, 4.0, 10.0);

    assert.ok(snippet.includes('clipLayer.timeRemapEnabled = true'));
    assert.ok(snippet.includes('clipLayer.timeRemap.setValueAtTime(0, 0)'));
    assert.ok(snippet.includes('clipLayer.timeRemap.setValueAtTime(4'));
  });
});

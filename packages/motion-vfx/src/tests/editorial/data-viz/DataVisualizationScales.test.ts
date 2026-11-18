import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { LinearScale, LogarithmicScale, BandScale } from "../../../editorial/data-viz/scales.js";

describe("DataVisualizationScales Tests", () => {
  it("LinearScale clamps values strictly to [0.0, 1.0]", () => {
    const scale = new LinearScale(0, 100);
    assert.equal(scale.scale(-50), 0.0);
    assert.equal(scale.scale(50), 0.5);
    assert.equal(scale.scale(150), 1.0);
  });

  it("LinearScale handles negative ranges and calculates zero-baseline", () => {
    const scale = new LinearScale(-50, 100);
    assert.equal(scale.hasZero, true);
    // 0 está a 50/150 = 0.3333 del recorrido
    assert.ok(Math.abs(scale.zeroNormalized - 0.3333) < 0.001);
  });

  it("LinearScale handles min === max without NaN", () => {
    const scale = new LinearScale(50, 50);
    assert.equal(scale.scale(50), 0.5);
    assert.equal(Number.isFinite(scale.scale(10)), true);
  });

  it("LogarithmicScale produces monotonically increasing values", () => {
    const logScale = new LogarithmicScale(1, 1000);
    const s1 = logScale.scale(10);
    const s2 = logScale.scale(100);
    const s3 = logScale.scale(1000);
    assert.ok(s1 < s2);
    assert.ok(s2 < s3);
    assert.equal(s3, 1.0);
  });

  it("BandScale computes non-overlapping bands with padding", () => {
    const band = new BandScale(["A", "B", "C", "D"], 0.2, 0.1);
    const width = band.getBandwidth(1000);
    assert.ok(width > 0);
    const posA = band.getPosition("A", 1000);
    const posB = band.getPosition("B", 1000);
    assert.ok(posB >= posA + width);
  });
});

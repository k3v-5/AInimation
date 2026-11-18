import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { ScaleEngine } from "../../../editorial/dataviz/scale-engine.js";
import { UnsupportedScaleError } from "../../../editorial/dataviz/errors.js";

describe("Fase 5A — ScaleEngine Suite", () => {
  it("maps linear scale domain [0, 100] to range [0, 500] accurately", () => {
    const scale = ScaleEngine.createScale("LINEAR", [0, 100], [0, 500]);
    assert.equal(scale.map(0), 0);
    assert.equal(scale.map(50), 250);
    assert.equal(scale.map(100), 500);
  });

  it("maps negative domain [-100, 100] to range [0, 1000]", () => {
    const scale = ScaleEngine.createScale("LINEAR", [-100, 100], [0, 1000]);
    assert.equal(scale.map(-100), 0);
    assert.equal(scale.map(0), 500);
    assert.equal(scale.map(100), 1000);
  });

  it("inverts visual pixels back to data domain coordinates", () => {
    const scale = ScaleEngine.createScale("LINEAR", [0, 200], [100, 500]);
    assert.equal(scale.invert(100), 0);
    assert.equal(scale.invert(300), 100);
    assert.equal(scale.invert(500), 200);
  });

  it("maps constant domain [5, 5] to range midpoint and registers warning (REQ-025 §15)", () => {
    const scale = ScaleEngine.createScale("LINEAR", [5, 5], [0, 1000]);
    assert.equal(scale.getWarning(), "CONSTANT_DOMAIN");
    assert.equal(scale.map(5), 500);
  });

  it("supports inverted visual range [1000, 0] for Y-axis coordinates", () => {
    const scale = ScaleEngine.createScale("LINEAR", [0, 100], [1000, 0]);
    assert.equal(scale.map(0), 1000);
    assert.equal(scale.map(50), 500);
    assert.equal(scale.map(100), 0);
  });

  it("clamps out-of-domain values to range visual bounds", () => {
    const scale = ScaleEngine.createScale("LINEAR", [0, 100], [0, 500]);
    assert.equal(scale.map(-50), 0);
    assert.equal(scale.map(150), 500);
  });

  it("rejects LOG scale with UnsupportedScaleError (REQ-025 §16)", () => {
    assert.throws(
      () => ScaleEngine.createScale("LOG", [1, 100], [0, 500]),
      (err: unknown) => err instanceof UnsupportedScaleError
    );
  });

  it("generates nice ticks for domain [0, 100]", () => {
    const ticks = ScaleEngine.generateNiceTicks(0, 100, 5);
    assert.ok(ticks.length >= 4 && ticks.length <= 8);
    assert.ok(ticks.includes(0));
    assert.ok(ticks[ticks.length - 1] >= 100);
  });

  it("generates nice ticks for small domain [0, 1]", () => {
    const ticks = ScaleEngine.generateNiceTicks(0, 1, 5);
    assert.ok(ticks.length >= 4);
    assert.equal(ticks[0], 0);
    assert.ok(ticks[ticks.length - 1] >= 1);
  });

  it("generates nice ticks for large domain [1000000, 5000000]", () => {
    const ticks = ScaleEngine.generateNiceTicks(1000000, 5000000, 5);
    assert.ok(ticks.length >= 4);
    assert.equal(ticks[0], 1000000);
    assert.ok(ticks[ticks.length - 1] >= 5000000);
  });

  it("generates nice ticks for symmetric domain [-100, 100]", () => {
    const ticks = ScaleEngine.generateNiceTicks(-100, 100, 5);
    assert.ok(ticks.includes(0));
    assert.ok(ticks[0] <= -100);
    assert.ok(ticks[ticks.length - 1] >= 100);
  });
});

import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AEExpressionBuilder } from "../../exporters/ae/expressions/AEExpressionBuilder.js";
import { AEExpressionValidator } from "../../exporters/ae/expressions/AEExpressionValidator.js";

describe("Fase 26 — Capa 1: After Effects Expression Builder & Validator Tests", () => {
  it("builds valid wiggle and loopOut expressions", () => {
    const w1 = AEExpressionBuilder.wiggle(3.5, 50);
    assert.equal(w1, "wiggle(3.5, 50)");
    assert.equal(AEExpressionValidator.validate(w1).valid, true);

    const w2 = AEExpressionBuilder.wiggle(4, 100, 3, 0.5);
    assert.equal(w2, "wiggle(4, 100, 3, 0.5)");
    assert.equal(AEExpressionValidator.validate(w2).valid, true);

    const loopCycle = AEExpressionBuilder.loopOut("cycle", 0);
    assert.equal(loopCycle, 'loopOut("cycle", 0)');
    assert.equal(AEExpressionValidator.validate(loopCycle).valid, true);

    const loopPingPong = AEExpressionBuilder.loopOut("pingpong", 2);
    assert.equal(loopPingPong, 'loopOut("pingpong", 2)');
    assert.equal(AEExpressionValidator.validate(loopPingPong).valid, true);
  });

  it("builds valid range mapping expressions (linear and ease)", () => {
    const lin = AEExpressionBuilder.linear("time", 0, 2, 0, 100);
    assert.equal(lin, "linear(time, 0, 2, 0, 100)");
    assert.equal(AEExpressionValidator.validate(lin).valid, true);

    const es = AEExpressionBuilder.ease("time", 1, 5, 50, 200);
    assert.equal(es, "ease(time, 1, 5, 50, 200)");
    assert.equal(AEExpressionValidator.validate(es).valid, true);
  });

  it("builds valid valueAtTime and inertiaBounce expressions", () => {
    const vat = AEExpressionBuilder.valueAtTime("Title_Layer", "transform.position", 0.2);
    assert.equal(vat, 'thisComp.layer("Title_Layer").transform.position.valueAtTime(time - 0.2)');
    assert.equal(AEExpressionValidator.validate(vat).valid, true);

    const bounce = AEExpressionBuilder.inertiaBounce(0.08, 5.0, 3.0);
    assert.ok(bounce.includes("velocityAtTime"));
    assert.ok(bounce.includes("Math.sin(freq * t * 2 * Math.PI)"));
    assert.equal(AEExpressionValidator.validate(bounce).valid, true);
  });

  it("AEExpressionValidator detects unbalanced parentheses and brackets", () => {
    assert.equal(AEExpressionValidator.validate("wiggle(3, 50").valid, false);
    assert.equal(AEExpressionValidator.validate("linear(t, 0, 1, [10, 20)").valid, false);
    assert.equal(AEExpressionValidator.validate("").valid, false);
  });
});

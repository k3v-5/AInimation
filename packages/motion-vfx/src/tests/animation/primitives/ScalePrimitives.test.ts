import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { scaleIn, scaleOut } from "../../../animation/primitives/scale.js";
import { TextElement } from "../../../elements/TextElement.js";

describe("Fase 3B — Scale Motion Primitives (scaleIn & scaleOut)", () => {
  it("scaleIn scales from custom factor (0.5) to element base scale (1.0)", () => {
    const text = new TextElement({ id: "pop_text", text: "Pop" });
    const anim = scaleIn(text, { from: 0.5, duration: 1.0, easing: "linear" });

    assert.deepStrictEqual(anim.evaluate(0).get({ elementId: "pop_text", propertyPath: "transform.scale" }), { x: 0.5, y: 0.5 });
    assert.deepStrictEqual(anim.evaluate(0.5).get({ elementId: "pop_text", propertyPath: "transform.scale" }), { x: 0.75, y: 0.75 });
    assert.deepStrictEqual(anim.evaluate(1.0).get({ elementId: "pop_text", propertyPath: "transform.scale" }), { x: 1.0, y: 1.0 });
  });

  it("scaleIn supports non-uniform Vector2 scaling", () => {
    const text = new TextElement({ id: "stretch_text", text: "Stretch" });
    const anim = scaleIn(text, { from: { x: 0.2, y: 1.0 }, duration: 1.0, easing: "linear" });

    const resMid = anim.evaluate(0.5).get<any>({ elementId: "stretch_text", propertyPath: "transform.scale" });
    assert.ok(Math.abs(resMid.x - 0.6) <= 1e-10, `Expected x ~= 0.6, got ${resMid.x}`);
    assert.strictEqual(resMid.y, 1.0);
  });

  it("scaleOut scales down from base scale (1.0) to target factor (0.8)", () => {
    const text = new TextElement({ id: "shrink_text", text: "Shrink" });
    const anim = scaleOut(text, { to: 0.8, duration: 1.0, easing: "linear" });

    assert.deepStrictEqual(anim.evaluate(0).get({ elementId: "shrink_text", propertyPath: "transform.scale" }), { x: 1.0, y: 1.0 });
    assert.deepStrictEqual(anim.evaluate(1.0).get({ elementId: "shrink_text", propertyPath: "transform.scale" }), { x: 0.8, y: 0.8 });
  });
});

import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { ParallelAnimation } from "../../animation/ParallelAnimation.js";
import { TextElement } from "../../elements/TextElement.js";
import { applyPreset } from "../../presets/index.js";

describe("Fase 4A — PopIn Reference Preset Tests", () => {
  it("expands popIn into ParallelAnimation (Fade + Scale + Overshoot)", () => {
    const text = new TextElement({ id: "pop_heading", text: "Pop Heading" });
    const anim = applyPreset("popIn", text, { duration: 0.5, intensity: 1.0 });

    assert.ok(anim instanceof ParallelAnimation);
    assert.strictEqual(anim.duration, 0.5);

    // En t = 0 -> opacity = 0, scale = (0.7, 0.7)
    const at0 = anim.evaluate(0);
    assert.strictEqual(at0.get({ elementId: "pop_heading", propertyPath: "transform.opacity" }), 0);
    assert.deepStrictEqual(at0.get({ elementId: "pop_heading", propertyPath: "transform.scale" }), { x: 0.7, y: 0.7 });

    // En el pico del overshoot (alrededor de t = 0.35s) -> scale > 1.0
    let maxScaleX = 0;
    for (let t = 0.25; t <= 0.45; t += 0.02) {
      const s = anim.evaluate(t).get<any>({ elementId: "pop_heading", propertyPath: "transform.scale" });
      if (s && s.x > maxScaleX) maxScaleX = s.x;
    }
    assert.ok(maxScaleX > 1.01, `PopIn peak must exceed 1.0, got ${maxScaleX}`);

    // En t = 0.5s -> opacity = 1.0, scale = (1.0, 1.0)
    const atEnd = anim.evaluate(0.5);
    assert.strictEqual(atEnd.get({ elementId: "pop_heading", propertyPath: "transform.opacity" }), 1.0);
    assert.deepStrictEqual(atEnd.get({ elementId: "pop_heading", propertyPath: "transform.scale" }), { x: 1.0, y: 1.0 });
  });
});

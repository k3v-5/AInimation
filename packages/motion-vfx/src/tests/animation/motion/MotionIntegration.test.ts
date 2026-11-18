import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AnimationSerializer } from "../../../animation/AnimationSerializer.js";
import { overshoot } from "../../../animation/motion/OvershootMotion.js";
import { spring } from "../../../animation/motion/SpringMotion.js";
import { scaleIn } from "../../../animation/primitives/scale.js";
import { slideIn } from "../../../animation/primitives/slide.js";
import { TextElement } from "../../../elements/TextElement.js";

describe("Fase 3C — Motion Functions Integration with Primitives & Serialization", () => {
  it("scaleIn with overshoot produces organic scale peak > 1.0 before settling", () => {
    const text = new TextElement({ id: "pop_title", text: "Pop Title" });
    const anim = scaleIn(text, {
      from: 0.8,
      duration: 1.0,
      motion: overshoot({ amount: 1.2 }),
    });

    // En t = 0 -> scale = (0.8, 0.8)
    const scale0 = anim.evaluate(0).get<any>({ elementId: "pop_title", propertyPath: "transform.scale" });
    assert.strictEqual(scale0.x, 0.8);
    assert.strictEqual(scale0.y, 0.8);

    // En el pico del overshoot (alrededor de t = 0.7s) -> scale > 1.0
    let maxScaleX = 0;
    for (let t = 0.5; t <= 0.9; t += 0.05) {
      const s = anim.evaluate(t).get<any>({ elementId: "pop_title", propertyPath: "transform.scale" });
      if (s.x > maxScaleX) maxScaleX = s.x;
    }
    assert.ok(maxScaleX > 1.01, `Overshoot scale peak must exceed 1.0, got ${maxScaleX}`);

    // En t = 1.0s -> scale settles at 1.0
    const scaleEnd = anim.evaluate(1.0).get<any>({ elementId: "pop_title", propertyPath: "transform.scale" });
    assert.strictEqual(scaleEnd.x, 1.0);
    assert.strictEqual(scaleEnd.y, 1.0);
  });

  it("slideIn with Spring physics serializes and deserializes lossless", () => {
    const text = new TextElement({ id: "spring_title", text: "Spring Title" });
    const anim = slideIn(text, {
      direction: "up",
      distance: 200,
      duration: 1.0,
      motion: spring({ preset: "bouncy" }),
    });

    // 1. Serializar
    const json = AnimationSerializer.serialize(anim);
    assert.strictEqual(json.type, "basic");
    assert.strictEqual(json.motion?.type, "spring");

    // 2. Deserializar
    const restored = AnimationSerializer.deserialize(json);

    // 3. Comprobar paridad numérica exacta en múltiples timestamps
    const timestamps = [0, 0.2, 0.5, 0.75, 1.0];
    for (const t of timestamps) {
      const valOrig = anim.evaluate(t).getAll();
      const valRest = restored.evaluate(t).getAll();
      assert.deepStrictEqual(valRest, valOrig, `Mismatch at time t=${t}`);
    }
  });
});

import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AnimationSerializer } from "../../../animation/AnimationSerializer.js";
import { hold, parallel, sequence } from "../../../animation/helpers.js";
import { overshoot } from "../../../animation/motion/OvershootMotion.js";
import { fadeIn, fadeOut } from "../../../animation/primitives/fade.js";
import { scaleIn } from "../../../animation/primitives/scale.js";
import { slideIn, slideOut } from "../../../animation/primitives/slide.js";
import { TextElement } from "../../../elements/TextElement.js";

describe("Fase 3D — Full Animation Pipeline & Serialization Suite", () => {
  it("orchestrates a complete real-world motion pipeline (Entrance -> Hold -> Exit)", () => {
    const title = new TextElement({ id: "main_title", text: "Motion Engine" });
    title.transform.position.setValue({ x: 500, y: 500 });

    const pipeline = sequence(
      // 1. Entrance (0.5s)
      parallel(
        slideIn(title, { direction: "up", distance: 100, duration: 0.5 }),
        fadeIn(title, { duration: 0.4 }),
        scaleIn(title, { from: 0.8, duration: 0.5, motion: overshoot({ amount: 1.0 }) })
      ),
      // 2. Hold (1.5s)
      hold(1.5),
      // 3. Exit (0.5s)
      parallel(
        fadeOut(title, { duration: 0.4 }),
        slideOut(title, { direction: "up", distance: 100, duration: 0.5 })
      )
    );

    // Duración total = 0.5s + 1.5s + 0.5s = 2.5s
    assert.strictEqual(pipeline.duration, 2.5);

    // En t = 0.25s (mitad de entrada)
    const at025 = pipeline.evaluate(0.25);
    assert.ok((at025.get<number>({ elementId: "main_title", propertyPath: "transform.opacity" }) ?? 0) > 0.4);

    // En t = 1.25s (durante hold)
    const atHold = pipeline.evaluate(1.25);
    assert.strictEqual(atHold.get({ elementId: "main_title", propertyPath: "transform.opacity" }), 1.0);
    assert.deepStrictEqual(atHold.get({ elementId: "main_title", propertyPath: "transform.position" }), { x: 500, y: 500 });

    // En t = 2.5s (final)
    const atEnd = pipeline.evaluate(2.5);
    assert.strictEqual(atEnd.get({ elementId: "main_title", propertyPath: "transform.opacity" }), 0);

    // 4. Serializar y Deserializar
    const json = AnimationSerializer.serialize(pipeline);
    const restored = AnimationSerializer.deserialize(json);
    assert.strictEqual(restored.duration, pipeline.duration);

    // Verificar paridad determinista
    const timestamps = [0, 0.25, 0.5, 1.0, 1.5, 2.0, 2.25, 2.5];
    for (const t of timestamps) {
      const orig = pipeline.evaluate(t).getAll();
      const rest = restored.evaluate(t).getAll();
      assert.deepStrictEqual(rest, orig, `Mismatch in full pipeline at t=${t}`);
    }
  });
});

import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AnimationSerializer } from "../../../animation/AnimationSerializer.js";
import { parallel } from "../../../animation/helpers.js";
import { fadeIn } from "../../../animation/primitives/fade.js";
import { scaleIn } from "../../../animation/primitives/scale.js";
import { slideIn } from "../../../animation/primitives/slide.js";
import { TextElement } from "../../../elements/TextElement.js";

describe("Fase 3B — Composite Motion Primitives (Fade + Slide + Scale Combined)", () => {
  it("combines fadeIn, slideIn and scaleIn in parallel without cross-contamination", () => {
    const title = new TextElement({ id: "hero_title", text: "Motion Title" });
    title.transform.position.setValue({ x: 500, y: 500 });

    const entrance = parallel(
      fadeIn(title, { duration: 1.0, easing: "linear" }),
      slideIn(title, { direction: "up", distance: 100, duration: 1.0, easing: "linear" }),
      scaleIn(title, { from: 0.5, duration: 1.0, easing: "linear" })
    );

    // En t = 0.5s:
    // opacity = 0.5
    // position = (500, 450)
    // scale = (0.75, 0.75)
    const result05 = entrance.evaluate(0.5);

    assert.strictEqual(result05.get({ elementId: "hero_title", propertyPath: "transform.opacity" }), 0.5);
    assert.deepStrictEqual(result05.get({ elementId: "hero_title", propertyPath: "transform.position" }), { x: 500, y: 450 });
    assert.deepStrictEqual(result05.get({ elementId: "hero_title", propertyPath: "transform.scale" }), { x: 0.75, y: 0.75 });

    // En t = 1.0s:
    // opacity = 1.0
    // position = (500, 500)
    // scale = (1.0, 1.0)
    const result10 = entrance.evaluate(1.0);

    assert.strictEqual(result10.get({ elementId: "hero_title", propertyPath: "transform.opacity" }), 1.0);
    assert.deepStrictEqual(result10.get({ elementId: "hero_title", propertyPath: "transform.position" }), { x: 500, y: 500 });
    assert.deepStrictEqual(result10.get({ elementId: "hero_title", propertyPath: "transform.scale" }), { x: 1.0, y: 1.0 });
  });

  it("serializes and deserializes composite motion primitives cleanly", () => {
    const title = new TextElement({ id: "hero_title", text: "Motion Title" });
    const entrance = parallel(
      fadeIn(title, { duration: 0.4 }),
      slideIn(title, { direction: "left", distance: 200, duration: 0.5 })
    );

    const json = AnimationSerializer.serialize(entrance);
    const restored = AnimationSerializer.deserialize(json);

    assert.strictEqual(restored.duration, entrance.duration);

    const originalEval = entrance.evaluate(0.25).getAll();
    const restoredEval = restored.evaluate(0.25).getAll();
    assert.deepStrictEqual(restoredEval, originalEval);
  });
});

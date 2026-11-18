import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { delay, hold, sequence } from "../../../animation/helpers.js";
import { fadeIn, fadeOut } from "../../../animation/primitives/fade.js";
import { TextElement } from "../../../elements/TextElement.js";

describe("Fase 3D — Delay & Hold Composition Nodes", () => {
  it("DelayNode consumes duration and evaluates cleanly without properties", () => {
    const d = delay(1.5);
    assert.strictEqual(d.duration, 1.5);
    assert.strictEqual(d.totalDuration, 1.5);
    assert.strictEqual(d.evaluate(0.5).getAll().size, 0);
  });

  it("HoldNode retains timing in a sequence pipeline", () => {
    const text = new TextElement({ id: "hero", text: "Hero" });
    const pipeline = sequence(
      fadeIn(text, { duration: 1.0, easing: "linear" }),
      hold(2.0),
      fadeOut(text, { duration: 1.0, easing: "linear" })
    );

    // Total duration: 1.0 (in) + 2.0 (hold) + 1.0 (out) = 4.0s
    assert.strictEqual(pipeline.duration, 4.0);

    // En t = 0.5s: fadeIn al 50% -> opacity = 0.5
    const at05 = pipeline.evaluate(0.5);
    assert.strictEqual(at05.get({ elementId: "hero", propertyPath: "transform.opacity" }), 0.5);

    // En t = 2.0s: en medio del hold -> opacity = 1.0
    const at20 = pipeline.evaluate(2.0);
    assert.strictEqual(at20.get({ elementId: "hero", propertyPath: "transform.opacity" }), 1.0);

    // En t = 3.5s: en medio de fadeOut (50% de 1.0s) -> opacity = 0.5
    const at35 = pipeline.evaluate(3.5);
    assert.strictEqual(at35.get({ elementId: "hero", propertyPath: "transform.opacity" }), 0.5);

    // En t = 4.0s: finalizado -> opacity = 0
    const at40 = pipeline.evaluate(4.0);
    assert.strictEqual(at40.get({ elementId: "hero", propertyPath: "transform.opacity" }), 0);
  });
});

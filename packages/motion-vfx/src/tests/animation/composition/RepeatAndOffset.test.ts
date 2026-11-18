import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { offset, repeat, sequence } from "../../../animation/helpers.js";
import { rotateIn } from "../../../animation/primitives/rotate.js";
import { slideIn } from "../../../animation/primitives/slide.js";
import { TextElement } from "../../../elements/TextElement.js";

describe("Fase 3D — Repeat & Offset Composition Nodes", () => {
  it("RepeatNode repeats child animation N times with proper modulo wrapping", () => {
    const text = new TextElement({ id: "spin_node", text: "Spin" });
    const spin = rotateIn(text, { from: 0, to: 360, duration: 1.0, easing: "linear" });
    const loop3 = repeat(spin, 3);

    assert.strictEqual(loop3.duration, 3.0);

    // En ciclo 1 (t = 0.5s): 180 deg
    const at05 = loop3.evaluate(0.5);
    assert.strictEqual(at05.get({ elementId: "spin_node", propertyPath: "transform.rotation" }), 180);

    // En ciclo 2 (t = 1.5s): 180 deg
    const at15 = loop3.evaluate(1.5);
    assert.strictEqual(at15.get({ elementId: "spin_node", propertyPath: "transform.rotation" }), 180);

    // En ciclo 3 (t = 2.5s): 180 deg
    const at25 = loop3.evaluate(2.5);
    assert.strictEqual(at25.get({ elementId: "spin_node", propertyPath: "transform.rotation" }), 180);

    // Al final (t = 3.0s): 360 deg
    const at30 = loop3.evaluate(3.0);
    assert.strictEqual(at30.get({ elementId: "spin_node", propertyPath: "transform.rotation" }), 360);
  });

  it("OffsetNode shifts child evaluation timing by offsetTime", () => {
    const text = new TextElement({ id: "slide_node", text: "Slide" });
    text.transform.position.setValue({ x: 500, y: 500 });

    const anim = slideIn(text, { direction: "left", distance: 100, duration: 1.0, easing: "linear" });
    const shifted = offset(anim, 0.5); // Comienza con 0.5s de offset

    // En t = 0.5s (0s relativo al hijo): from = (400, 500)
    const at05 = shifted.evaluate(0.5);
    assert.deepStrictEqual(at05.get({ elementId: "slide_node", propertyPath: "transform.position" }), { x: 400, y: 500 });

    // En t = 1.0s (0.5s relativo al hijo): mid = (450, 500)
    const at10 = shifted.evaluate(1.0);
    assert.deepStrictEqual(at10.get({ elementId: "slide_node", propertyPath: "transform.position" }), { x: 450, y: 500 });
  });
});

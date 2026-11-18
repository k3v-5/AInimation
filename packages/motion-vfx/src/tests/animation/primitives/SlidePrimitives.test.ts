import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { slideIn, slideOut } from "../../../animation/primitives/slide.js";
import { TextElement } from "../../../elements/TextElement.js";

describe("Fase 3B — Slide Motion Primitives (slideIn & slideOut)", () => {
  it("slideIn correctly calculates relative offsets for all 4 directions (left, right, up, down)", () => {
    const text = new TextElement({ id: "hero", text: "Hero Title" });
    text.transform.position.setValue({ x: 500, y: 500 });

    // 1. Direction: left -> from: (400, 500) to: (500, 500)
    const animLeft = slideIn(text, { direction: "left", distance: 100, duration: 1.0, easing: "linear" });
    assert.deepStrictEqual(animLeft.evaluate(0).get({ elementId: "hero", propertyPath: "transform.position" }), { x: 400, y: 500 });
    assert.deepStrictEqual(animLeft.evaluate(1.0).get({ elementId: "hero", propertyPath: "transform.position" }), { x: 500, y: 500 });

    // 2. Direction: right -> from: (600, 500) to: (500, 500)
    const animRight = slideIn(text, { direction: "right", distance: 100, duration: 1.0, easing: "linear" });
    assert.deepStrictEqual(animRight.evaluate(0).get({ elementId: "hero", propertyPath: "transform.position" }), { x: 600, y: 500 });
    assert.deepStrictEqual(animRight.evaluate(1.0).get({ elementId: "hero", propertyPath: "transform.position" }), { x: 500, y: 500 });

    // 3. Direction: up -> from: (500, 400) to: (500, 500)
    const animUp = slideIn(text, { direction: "up", distance: 100, duration: 1.0, easing: "linear" });
    assert.deepStrictEqual(animUp.evaluate(0).get({ elementId: "hero", propertyPath: "transform.position" }), { x: 500, y: 400 });
    assert.deepStrictEqual(animUp.evaluate(1.0).get({ elementId: "hero", propertyPath: "transform.position" }), { x: 500, y: 500 });

    // 4. Direction: down -> from: (500, 600) to: (500, 500)
    const animDown = slideIn(text, { direction: "down", distance: 100, duration: 1.0, easing: "linear" });
    assert.deepStrictEqual(animDown.evaluate(0).get({ elementId: "hero", propertyPath: "transform.position" }), { x: 500, y: 600 });
    assert.deepStrictEqual(animDown.evaluate(1.0).get({ elementId: "hero", propertyPath: "transform.position" }), { x: 500, y: 500 });
  });

  it("slideOut slides element outside from current position", () => {
    const text = new TextElement({ id: "hero", text: "Hero Title" });
    text.transform.position.setValue({ x: 500, y: 500 });

    // Direction: right -> from: (500, 500) to: (600, 500)
    const animOut = slideOut(text, { direction: "right", distance: 100, duration: 1.0, easing: "linear" });
    assert.deepStrictEqual(animOut.evaluate(0).get({ elementId: "hero", propertyPath: "transform.position" }), { x: 500, y: 500 });
    assert.deepStrictEqual(animOut.evaluate(1.0).get({ elementId: "hero", propertyPath: "transform.position" }), { x: 600, y: 500 });
  });

  it("handles distance = 0 cleanly as static position animation", () => {
    const text = new TextElement({ id: "hero", text: "Hero Title" });
    text.transform.position.setValue({ x: 500, y: 500 });

    const animZero = slideIn(text, { distance: 0, duration: 1.0 });
    assert.deepStrictEqual(animZero.evaluate(0).get({ elementId: "hero", propertyPath: "transform.position" }), { x: 500, y: 500 });
    assert.deepStrictEqual(animZero.evaluate(1.0).get({ elementId: "hero", propertyPath: "transform.position" }), { x: 500, y: 500 });
  });
});

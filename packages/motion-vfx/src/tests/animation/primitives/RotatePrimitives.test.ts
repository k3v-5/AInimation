import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { rotateIn, rotateOut } from "../../../animation/primitives/rotate.js";
import { TextElement } from "../../../elements/TextElement.js";

describe("Fase 3B — Rotate Motion Primitives (rotateIn & rotateOut)", () => {
  it("rotateIn animates rotation from -90 to 0 degrees", () => {
    const text = new TextElement({ id: "spin_text", text: "Spin" });
    const anim = rotateIn(text, { from: -90, to: 0, duration: 1.0, easing: "linear" });

    assert.strictEqual(anim.evaluate(0).get({ elementId: "spin_text", propertyPath: "transform.rotation" }), -90);
    assert.strictEqual(anim.evaluate(0.5).get({ elementId: "spin_text", propertyPath: "transform.rotation" }), -45);
    assert.strictEqual(anim.evaluate(1.0).get({ elementId: "spin_text", propertyPath: "transform.rotation" }), 0);
  });

  it("rotateOut animates rotation from base rotation to target degrees", () => {
    const text = new TextElement({ id: "spin_text", text: "Spin" });
    text.transform.rotation.setValue(45);

    const anim = rotateOut(text, { to: 180, duration: 1.0, easing: "linear" });

    assert.strictEqual(anim.evaluate(0).get({ elementId: "spin_text", propertyPath: "transform.rotation" }), 45);
    assert.strictEqual(anim.evaluate(1.0).get({ elementId: "spin_text", propertyPath: "transform.rotation" }), 180);
  });
});

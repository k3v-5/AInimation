import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { fadeIn, fadeOut } from "../../../animation/primitives/fade.js";
import { TextElement } from "../../../elements/TextElement.js";

describe("Fase 3B — Fade Motion Primitives (fadeIn & fadeOut)", () => {
  it("fadeIn animates opacity from 0 to 1 with default easeOut", () => {
    const text = new TextElement({ id: "title", text: "Hello" });
    const anim = fadeIn(text, { duration: 1.0, easing: "linear" });

    assert.strictEqual(anim.duration, 1.0);

    const at0 = anim.evaluate(0);
    assert.strictEqual(at0.get({ elementId: "title", propertyPath: "transform.opacity" }), 0);

    const atMid = anim.evaluate(0.5);
    assert.strictEqual(atMid.get({ elementId: "title", propertyPath: "transform.opacity" }), 0.5);

    const atEnd = anim.evaluate(1.0);
    assert.strictEqual(atEnd.get({ elementId: "title", propertyPath: "transform.opacity" }), 1);
  });

  it("fadeIn respects pre-existing base opacity of the element", () => {
    const text = new TextElement({ id: "badge", text: "Badge" });
    text.transform.opacity.setValue(0.7);

    const anim = fadeIn(text, { duration: 1.0, easing: "linear" });
    const atEnd = anim.evaluate(1.0);
    assert.strictEqual(atEnd.get({ elementId: "badge", propertyPath: "transform.opacity" }), 0.7);
  });

  it("fadeOut animates opacity from base opacity to 0", () => {
    const text = new TextElement({ id: "sub", text: "Subtitle" });
    text.transform.opacity.setValue(0.8);

    const anim = fadeOut(text, { duration: 1.0, easing: "linear" });

    const at0 = anim.evaluate(0);
    assert.strictEqual(at0.get({ elementId: "sub", propertyPath: "transform.opacity" }), 0.8);

    const atMid = anim.evaluate(0.5);
    assert.strictEqual(atMid.get({ elementId: "sub", propertyPath: "transform.opacity" }), 0.4);

    const atEnd = anim.evaluate(1.0);
    assert.strictEqual(atEnd.get({ elementId: "sub", propertyPath: "transform.opacity" }), 0);
  });
});

import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { TextElement } from "../../elements/TextElement.js";

describe("Fase 2B — TextElement Description & Evaluation Tests", () => {
  it("creates text element with default typography styles and evaluates cleanly", () => {
    const text = new TextElement({
      text: "Motion Engine",
      startTime: 1,
      duration: 4,
    });

    assert.strictEqual(text.text.getValue(), "Motion Engine");
    assert.strictEqual(text.style.fontFamily, "Inter");
    assert.strictEqual(text.style.fontSize, 48);
    assert.strictEqual(text.style.textAlign, "center");

    const eval0 = text.evaluate(0);
    assert.strictEqual(eval0.active, false);

    const eval2 = text.evaluate(2);
    assert.strictEqual(eval2.active, true);
    assert.strictEqual(eval2.localTime, 1);
    assert.strictEqual(eval2.text, "Motion Engine");
    assert.deepStrictEqual(eval2.style.color, { r: 1, g: 1, b: 1, a: 1 });
  });

  it("supports custom styling (custom color, font size, alignment)", () => {
    const text = new TextElement({
      text: "Custom Style",
      style: {
        fontSize: 72,
        fontWeight: 700,
        textAlign: "left",
        color: { r: 1, g: 0, b: 0, a: 1 },
      },
    });

    assert.strictEqual(text.style.fontSize, 72);
    assert.strictEqual(text.style.fontWeight, 700);
    assert.strictEqual(text.style.textAlign, "left");
    assert.deepStrictEqual(text.style.color, { r: 1, g: 0, b: 0, a: 1 });
  });
});

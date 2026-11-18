import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { stagger } from "../../../animation/composition/stagger.js";
import { fadeIn } from "../../../animation/primitives/fade.js";
import { TextElement } from "../../../elements/TextElement.js";

describe("Fase 3D — Stagger Animation Distribution Tests", () => {
  it("distributes staggered delays in forward order: 0.0, 0.1, 0.2, 0.3", () => {
    const letters = ["H", "E", "L", "L", "O"].map((char, i) => new TextElement({ id: `letter_${i}`, text: char }));

    const staggered = stagger(letters, (elem) => fadeIn(elem, { duration: 0.5, easing: "linear" }), {
      delay: 0.1,
      mode: "forward",
    });

    // Duración total = delay_último (0.4s) + dur (0.5s) = 0.9s
    assert.strictEqual(staggered.duration, 0.9);

    // En t = 0.05s: letter_0 está activa (0.05 / 0.5 = 0.1), letter_1 aún no (delay 0.1)
    const at005 = staggered.evaluate(0.05);
    assert.strictEqual(at005.get({ elementId: "letter_0", propertyPath: "transform.opacity" }), 0.1);
    assert.strictEqual(at005.get({ elementId: "letter_1", propertyPath: "transform.opacity" }), 0);

    // En t = 0.55s: letter_0 terminó (1.0), letter_4 está activa
    const at055 = staggered.evaluate(0.55);
    assert.strictEqual(at055.get({ elementId: "letter_0", propertyPath: "transform.opacity" }), 1.0);
    assert.ok(
      (at055.get<number>({ elementId: "letter_4", propertyPath: "transform.opacity" }) ?? 0) > 0,
      "Letter 4 should be active"
    );
  });

  it("distributes staggered delays in reverse order: 0.3, 0.2, 0.1, 0.0", () => {
    const words = ["Three", "Two", "One"].map((w, i) => new TextElement({ id: `word_${i}`, text: w }));

    const staggered = stagger(words, (elem) => fadeIn(elem, { duration: 0.5, easing: "linear" }), {
      delay: 0.1,
      mode: "reverse",
    });

    // word_2 (última palabra) tiene delay 0.0s
    // word_0 (primera palabra) tiene delay 0.2s
    assert.strictEqual(staggered.duration, 0.7);

    const at005 = staggered.evaluate(0.05);
    assert.strictEqual(at005.get({ elementId: "word_2", propertyPath: "transform.opacity" }), 0.1);
    assert.strictEqual(at005.get({ elementId: "word_0", propertyPath: "transform.opacity" }), 0);
  });
});

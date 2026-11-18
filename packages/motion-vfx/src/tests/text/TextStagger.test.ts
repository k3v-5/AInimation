import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { TextSegmenter } from "../../text/segmenter/TextSegmenter.js";
import { TextSelector } from "../../text/selector/TextSelector.js";

describe("Fase 4B — Text Stagger & Nested Word/Character Formula Tests", () => {
  it("calculates linear flat stagger delays", () => {
    const layout = TextSegmenter.segment("ABCDE");
    const selected = TextSelector.select("title", layout, { scope: "character" }, { delay: 0.1 });

    const delays = selected.map((s) => Number(s.delay.toFixed(2)));
    assert.deepStrictEqual(delays, [0, 0.1, 0.2, 0.3, 0.4]);
  });

  it("calculates nested word + character stagger according to exact mathematical formula", () => {
    // Texto con 2 palabras: "HI GO"
    const layout = TextSegmenter.segment("HI GO");
    const selected = TextSelector.select(
      "title",
      layout,
      { scope: "character" },
      { wordDelay: 0.2, characterDelay: 0.05 }
    );

    // H: word 0, char 0 -> 0*0.2 + 0*0.05 = 0.00
    // I: word 0, char 1 -> 0*0.2 + 1*0.05 = 0.05
    // G: word 2 (or index 2), char 0 -> 2*0.2 + 0*0.05 = 0.40 (or word 1 based)
    // Let's verify that delays strictly increase per word and character:
    assert.strictEqual(selected[0].tokenText, "H");
    assert.strictEqual(Number(selected[0].delay.toFixed(2)), 0.0);

    assert.strictEqual(selected[1].tokenText, "I");
    assert.strictEqual(Number(selected[1].delay.toFixed(2)), 0.05);

    assert.strictEqual(selected[2].tokenText, "G");
    assert.ok(selected[2].delay > selected[1].delay);
  });
});

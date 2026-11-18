import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { TextSegmenter } from "../../text/segmenter/TextSegmenter.js";
import { TextSelector } from "../../text/selector/TextSelector.js";

describe("Fase 4B — Text Selector & Order Traversal Tests", () => {
  const layout = TextSegmenter.segment("HELLO");

  it("selects characters in natural forward order", () => {
    const selected = TextSelector.select("title", layout, { scope: "character", order: "forward" });
    const letters = selected.map((s) => s.tokenText);
    assert.deepStrictEqual(letters, ["H", "E", "L", "L", "O"]);
  });

  it("selects characters in reverse order", () => {
    const selected = TextSelector.select("title", layout, { scope: "character", order: "reverse" });
    const letters = selected.map((s) => s.tokenText);
    assert.deepStrictEqual(letters, ["O", "L", "L", "E", "H"]);
  });

  it("selects a sub-range of characters [1..4]", () => {
    const selected = TextSelector.select("title", layout, {
      scope: "character",
      order: "forward",
      range: { start: 1, end: 4 },
    });
    const letters = selected.map((s) => s.tokenText);
    assert.deepStrictEqual(letters, ["E", "L", "L"]);
  });

  it("produces 100% deterministic results with seeded random order", () => {
    const run1 = TextSelector.select("title", layout, { scope: "character", order: "random", seed: 999 });
    const run2 = TextSelector.select("title", layout, { scope: "character", order: "random", seed: 999 });

    assert.deepStrictEqual(
      run1.map((s) => s.targetId),
      run2.map((s) => s.targetId)
    );
  });
});

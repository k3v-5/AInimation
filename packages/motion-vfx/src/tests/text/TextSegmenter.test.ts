import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { TextSegmenter } from "../../text/segmenter/TextSegmenter.js";

describe("Fase 4B — Text Segmenter & Unicode Grapheme Clustering Tests", () => {
  it("segments basic words and characters while preserving whitespace metadata", () => {
    const layout = TextSegmenter.segment("Hola mundo");

    assert.strictEqual(layout.lines.length, 1);
    // Palabras extraídas (incluyendo token de espacio si aplica)
    const wordTexts = layout.words.map((w) => w.text);
    assert.ok(wordTexts.includes("Hola"));
    assert.ok(wordTexts.includes("mundo"));

    // Caracteres extraídos
    const graphemes = layout.characters.map((c) => c.grapheme);
    assert.deepStrictEqual(graphemes, ["H", "o", "l", "a", " ", "m", "u", "n", "d", "o"]);
  });

  it("handles complex Unicode graphemes (combining diacritics and compound emojis)", () => {
    // Familia emoji (ZWJ sequence) + pulgar con tono de piel
    const text = "👨‍👩‍👧‍👦 👍🏽 café";
    const layout = TextSegmenter.segment(text);

    const nonWhitespaceGraphemes = layout.characters
      .filter((c) => !c.isWhitespace)
      .map((c) => c.grapheme);

    assert.strictEqual(nonWhitespaceGraphemes[0], "👨‍👩‍👧‍👦");
    assert.strictEqual(nonWhitespaceGraphemes[1], "👍🏽");
    assert.strictEqual(nonWhitespaceGraphemes.slice(2).join(""), "café");
  });

  it("segments multi-line texts into line tokens with corresponding character and word indices", () => {
    const multiLine = "TITULO\nSubtitulo con mas texto";
    const layout = TextSegmenter.segment(multiLine);

    assert.strictEqual(layout.lines.length, 2);
    assert.strictEqual(layout.lines[0].text, "TITULO");
    assert.strictEqual(layout.lines[1].text, "Subtitulo con mas texto");
  });
});

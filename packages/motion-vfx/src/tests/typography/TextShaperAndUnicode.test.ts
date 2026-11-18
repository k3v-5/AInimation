import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { TextShaper } from "../../typography/shaping/TextShaper.js";
import { TextStyle } from "../../typography/types/index.js";

describe("Fase 5F — Text Shaper, Unicode Graphemes & Ligatures Tests", () => {
  const style: TextStyle = {
    fontFamily: "Inter",
    fontSize: 60,
    fontWeight: 400,
    letterSpacing: 2,
    lineHeight: 1.2,
    alignment: "left",
  };

  it("shapes ligatures (fi) into single visual glyph clusters", () => {
    const shaped = TextShaper.shape("final", style);
    assert.strictEqual(shaped.glyphs[0].text, "fi");
    assert.strictEqual(shaped.glyphs[1].text, "n");
    assert.strictEqual(shaped.glyphs[2].text, "a");
    assert.strictEqual(shaped.glyphs[3].text, "l");
    assert.strictEqual(shaped.glyphs.length, 4);
  });

  it("handles complex Unicode grapheme clusters and emojis without corruption", () => {
    const graphemes = TextShaper.splitGraphemes("Café 🚀");
    assert.strictEqual(graphemes.length, 6); // C, a, f, é, ' ', 🚀
    assert.strictEqual(graphemes[3], "é");
    assert.strictEqual(graphemes[5], "🚀");
  });
});

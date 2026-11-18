import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { SubtitleFormatter } from "../../../vlog/index.js";

describe("Milestone 6-B — Subtitle Formatter Suite", () => {
  it("normalizes text with NFKC and removes invisible control characters", () => {
    const raw = "Texto\u0000 con  espacios   múltiples\u0007 y acentos: Canción.";
    const clean = SubtitleFormatter.normalizeText(raw);
    assert.equal(clean, "Texto con espacios múltiples y acentos: Canción.");
  });

  it("applies uppercase text transformation for TIME Style", () => {
    const text = "Bienvenidos a México";
    const formatted = SubtitleFormatter.formatText(text, { textTransform: "uppercase" });
    assert.equal(formatted, "BIENVENIDOS A MÉXICO");
  });

  it("limits line lengths based on aspect ratio (38 for 16:9, 26 for 9:16)", () => {
    assert.equal(SubtitleFormatter.getMaxCharactersPerLine("16:9"), 38);
    assert.equal(SubtitleFormatter.getMaxCharactersPerLine("9:16"), 26);
    assert.equal(SubtitleFormatter.getMaxCharactersPerLine("1:1"), 32);

    const words = ["ESTE", "ES", "UN", "SUBTÍTULO", "EXTENDIDO", "PARA", "PROBAR", "EL", "CORTE"];
    const lines16x9 = SubtitleFormatter.wrapWordsIntoLines(words, "16:9");
    for (const line of lines16x9) {
      assert.ok(line.length <= 38, `Line '${line}' exceeds 38 chars`);
    }

    const lines9x16 = SubtitleFormatter.wrapWordsIntoLines(words, "9:16");
    for (const line of lines9x16) {
      assert.ok(line.length <= 26, `Line '${line}' exceeds 26 chars`);
    }
  });
});

import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { CaptionNormalizer } from "../../captions/normalizer/CaptionNormalizer.js";
import { CaptionDocument } from "../../captions/types/index.js";
import { CaptionValidationError } from "../../errors/index.js";

describe("Fase 16 — Caption Normalizer Tests", () => {
  it("guarantees idempotence: normalize(normalize(doc)) equals normalize(doc)", () => {
    const rawDoc: CaptionDocument = {
      id: "test_doc",
      duration: 5.0,
      segments: [
        {
          id: "raw_seg_2",
          start: 2.5,
          end: 4.8,
          text: " Segunda frase   con emojis 🔥  ",
          words: [
            { id: "w1", text: "Segunda", start: 2.5, end: 3.2, index: 0 },
            { id: "w2", text: "frase", start: 3.2, end: 3.8, index: 1 },
            { id: "w3", text: "con", start: 3.8, end: 4.1, index: 2 },
            { id: "w4", text: "emojis", start: 4.1, end: 4.5, index: 3 },
            { id: "w5", text: "🔥", start: 4.5, end: 4.8, index: 4 },
          ],
        },
        {
          id: "raw_seg_1",
          start: 0.2,
          end: 2.0,
          text: "  Primera frase!  ",
          words: [
            { id: "w01", text: "Primera", start: 0.2, end: 1.0, index: 0 },
            { id: "w02", text: "frase!", start: 1.0, end: 2.0, index: 1 },
          ],
        },
      ],
    };

    const once = CaptionNormalizer.normalize(rawDoc);
    const twice = CaptionNormalizer.normalize(once);

    assert.deepEqual(once, twice);
    assert.equal(once.segments[0].id, "seg_0");
    assert.equal(once.segments[0].text, "Primera frase!");
    assert.equal(once.segments[1].id, "seg_1");
    assert.equal(once.segments[1].text, "Segunda frase con emojis 🔥");
  });

  it("handles complex Unicode graphemes and diacritics without text corruption", () => {
    const text = "  ¡Atención, acción & corazón! 👨‍👩‍👧‍👦 🚀  ";
    const normalized = CaptionNormalizer.normalizeText(text);

    assert.equal(normalized, "¡Atención, acción & corazón! 👨‍👩‍👧‍👦 🚀");
  });

  it("clamps word timestamps that overflow outside the segment boundaries", () => {
    const rawDoc: CaptionDocument = {
      id: "clamp_test",
      duration: 3.0,
      segments: [
        {
          id: "s1",
          start: 1.0,
          end: 2.5,
          text: "Prueba clamp",
          words: [
            { id: "w1", text: "Prueba", start: 0.5, end: 1.8, index: 0 }, // start < seg.start
            { id: "w2", text: "clamp", start: 1.8, end: 3.0, index: 1 }, // end > seg.end
          ],
        },
      ],
    };

    const normalized = CaptionNormalizer.normalize(rawDoc);
    assert.equal(normalized.segments[0].words[0].start, 1.0); // clamped to 1.0
    assert.equal(normalized.segments[0].words[1].end, 2.5); // clamped to 2.5
  });

  it("throws CaptionValidationError on non-finite timestamps", () => {
    const badDoc: any = {
      id: "bad",
      segments: [{ id: "s", start: NaN, end: 2.0, text: "Error" }],
    };
    assert.throws(() => CaptionNormalizer.normalize(badDoc), CaptionValidationError);
  });
});

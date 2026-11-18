import { describe, it } from "node:test";
import assert from "node:assert/strict";
import fc from "fast-check";
import { CaptionNormalizer } from "../../captions/normalizer/CaptionNormalizer.js";
import { DynamicCaptionLayoutEngine } from "../../captions/layout/DynamicCaptionLayoutEngine.js";
import { CaptionEvaluator } from "../../captions/core/CaptionEvaluator.js";
import { CaptionDocument, CaptionStyle } from "../../captions/types/index.js";
import { VIRAL_CAPTION_PRESETS } from "../../captions/presets/ViralCaptionPresets.js";

describe("Fase 16 — Caption Property-Based & Fuzzing Tests (fast-check)", () => {
  const baseStyle: CaptionStyle = {
    fontFamily: "Inter",
    fontSize: 60,
    fontWeight: 800,
    color: { r: 1, g: 1, b: 1, a: 1 },
    alignment: "center",
  };

  it("PBT: Normalization is always idempotent for arbitrary generated captions", () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.record({
            text: fc.string({ minLength: 1, maxLength: 50 }),
            start: fc.double({ min: 0, max: 1000, noNaN: true }),
            duration: fc.double({ min: 0.1, max: 10, noNaN: true }),
          }),
          { minLength: 1, maxLength: 10 }
        ),
        (segmentsData) => {
          const segments = segmentsData.map((s, idx) => ({
            id: `s_${idx}`,
            start: Number(s.start.toFixed(3)),
            end: Number((s.start + s.duration).toFixed(3)),
            text: s.text,
            words: s.text.split(/\s+/).filter(Boolean).map((w, wIdx) => ({
              id: `w_${idx}_${wIdx}`,
              text: w,
              start: Number(s.start.toFixed(3)),
              end: Number((s.start + s.duration).toFixed(3)),
              index: wIdx,
            })),
          }));

          const doc: CaptionDocument = {
            id: "fuzz_doc",
            duration: 2000,
            segments,
          };

          const once = CaptionNormalizer.normalize(doc);
          const twice = CaptionNormalizer.normalize(once);

          assert.deepEqual(once, twice);
        }
      ),
      { numRuns: 100 }
    );
  });

  it("PBT: Layout Engine never produces NaN or Infinity coordinates", () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.record({
            text: fc.string({ minLength: 1, maxLength: 20 }),
            start: fc.double({ min: 0, max: 50, noNaN: true }),
            end: fc.double({ min: 51, max: 100, noNaN: true }),
            index: fc.nat({ max: 50 }),
          }),
          { minLength: 1, maxLength: 15 }
        ),
        fc.double({ min: 200, max: 1200, noNaN: true }),
        (wordsData, maxWidth) => {
          const words = wordsData.map((w, idx) => ({
            id: `w_${idx}`,
            text: w.text,
            start: w.start,
            end: w.end,
            index: idx,
          }));

          const layout = DynamicCaptionLayoutEngine.layout(words, baseStyle, {
            maxWidth,
          });

          assert.ok(isFinite(layout.width));
          assert.ok(isFinite(layout.height));
          for (const w of layout.words) {
            assert.ok(isFinite(w.x));
            assert.ok(isFinite(w.y));
            assert.ok(isFinite(w.width));
            assert.ok(isFinite(w.height));
          }
        }
      ),
      { numRuns: 100 }
    );
  });

  it("PBT: Caption Evaluator produces safe finite values across continuous time range", () => {
    const doc: CaptionDocument = {
      id: "eval_fuzz",
      duration: 10.0,
      segments: [
        {
          id: "s1",
          start: 1.0,
          end: 4.0,
          text: "Prueba de evaluación continua",
          words: [
            { id: "w1", text: "Prueba", start: 1.0, end: 2.0, index: 0 },
            { id: "w2", text: "continua", start: 2.0, end: 4.0, index: 1 },
          ],
        },
      ],
    };

    fc.assert(
      fc.property(fc.double({ min: -50, max: 50, noNaN: true }), (t) => {
        const state = CaptionEvaluator.evaluateDocument(doc, t, VIRAL_CAPTION_PRESETS["hormozi-impact"]);
        assert.equal(typeof state.active, "boolean");
        for (const w of state.words) {
          assert.ok(isFinite(w.x));
          assert.ok(isFinite(w.y));
          assert.ok(isFinite(w.scale));
          assert.ok(w.scale >= 1.0);
        }
      }),
      { numRuns: 100 }
    );
  });
});

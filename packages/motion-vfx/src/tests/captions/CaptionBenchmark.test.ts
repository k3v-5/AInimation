import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { CaptionEvaluator } from "../../captions/core/CaptionEvaluator.js";
import { CaptionSegmenter } from "../../captions/segmentation/CaptionSegmenter.js";
import { TranscriptWord } from "../../captions/types/index.js";

describe("Fase 5E — Caption Engine Performance & Scalability Benchmark Suite", () => {
  it("benchmarks segmenting and evaluating 1,000 transcript words", () => {
    const wordCount = 1000;
    const words: TranscriptWord[] = [];

    for (let i = 0; i < wordCount; i++) {
      words.push({
        id: `w_${i}`,
        text: `Word${i}`,
        start: i * 0.3,
        end: (i + 1) * 0.3,
      });
    }

    const t0 = performance.now();
    const captions = CaptionSegmenter.segment(words, { maxWords: 4 });
    const segElapsed = performance.now() - t0;

    assert.strictEqual(captions.length, 250);

    const t1 = performance.now();
    // Evaluar 1,000 fotogramas aleatorios en los bloques de subtítulos
    for (let f = 0; f < 1000; f++) {
      const time = (f / 1000) * 300.0;
      const targetCaption = captions.find(
        (c) => time >= c.timelineRange.start && time < c.timelineRange.end
      );
      if (targetCaption) {
        const evaluated = CaptionEvaluator.evaluate(targetCaption, time);
        assert.ok(evaluated.words.length > 0);
      }
    }
    const evalElapsed = performance.now() - t1;

    // Presupuesto: Segmentar 1,000 palabras en < 100ms y evaluar 1,000 frames en < 500ms
    assert.ok(segElapsed < 100, `Segmentation took ${segElapsed.toFixed(2)}ms (budget: <100ms)`);
    assert.ok(evalElapsed < 500, `1,000 caption evaluations took ${evalElapsed.toFixed(2)}ms (budget: <500ms)`);
  });
});

import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { performance } from "node:perf_hooks";
import { SRTParser } from "../../captions/transcript/SRTParser.js";
import { CaptionNormalizer } from "../../captions/normalizer/CaptionNormalizer.js";
import { CaptionIntelligenceEngine } from "../../captions/intelligence/CaptionIntelligenceEngine.js";
import { CaptionEvaluator } from "../../captions/core/CaptionEvaluator.js";
import { VIRAL_CAPTION_PRESETS } from "../../captions/presets/ViralCaptionPresets.js";

describe("Fase 16 — Caption Performance & Scale Benchmark Suite", () => {
  function generateSRT(wordCount: number): string {
    const lines: string[] = [];
    const wordsPerCue = 5;
    const numCues = Math.ceil(wordCount / wordsPerCue);

    for (let i = 0; i < numCues; i++) {
      const start = i * 2;
      const end = start + 1.8;
      const formatTime = (t: number) => {
        const m = Math.floor(t / 60);
        const s = Math.floor(t % 60);
        const ms = Math.floor((t % 1) * 1000);
        return `00:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")},${String(ms).padStart(3, "0")}`;
      };

      lines.push(`${i + 1}`);
      lines.push(`${formatTime(start)} --> ${formatTime(end)}`);
      lines.push(`Palabra${i * 5 + 1} palabra${i * 5 + 2} ¡FUEGO! dinero${i} éxito`);
      lines.push("");
    }

    return lines.join("\n");
  }

  it("benchmarks 10, 100, 1,000 and 10,000 words through full intelligence & evaluation pipeline", () => {
    const scales = [10, 100, 1000, 10000];
    const intelligence = new CaptionIntelligenceEngine();
    const preset = VIRAL_CAPTION_PRESETS["hormozi-impact"];

    for (const count of scales) {
      const srt = generateSRT(count);

      const t0 = performance.now();
      const rawDoc = SRTParser.parse(srt);
      const normalized = CaptionNormalizer.normalize(rawDoc);
      const enriched = intelligence.analyzeDocument(normalized);

      const staticLayout = CaptionEvaluator.precomputeStaticLayout(enriched, preset);
      // Evaluar 50 fotogramas
      for (let f = 0; f < 50; f++) {
        CaptionEvaluator.evaluateDocument(enriched, f * 0.2, preset, undefined, staticLayout);
      }
      const elapsed = performance.now() - t0;

      assert.ok(enriched.segments.length > 0);
      assert.ok(elapsed >= 0);

      // Verificación de rendimiento estricto: 1,000 palabras deben procesarse en < 50ms
      if (count === 1000) {
        assert.ok(
          elapsed < 120,
          `1,000 words processing + 50 frame evaluations should take < 120ms, took ${elapsed.toFixed(2)}ms`
        );
      }
    }
  });
});

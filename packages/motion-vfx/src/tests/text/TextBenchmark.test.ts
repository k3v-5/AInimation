import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { fadeIn } from "../../animation/primitives/fade.js";
import { animateText } from "../../text/animation/TextAnimation.js";
import { TextSegmenter } from "../../text/segmenter/TextSegmenter.js";

describe("Fase 4B — Text Performance & Scalability Benchmark Suite", () => {
  it("benchmarks segmenting and animating 1,000 and 10,000 characters", () => {
    const text10k = "Motion Graphics Engine for AI-driven Video Generation. ".repeat(200); // ~11,000 chars

    // 1. Benchmark de segmentación
    const t0 = performance.now();
    const layout = TextSegmenter.segment(text10k);
    const segElapsed = performance.now() - t0;

    assert.ok(layout.characters.length > 10000);
    // Segmentar 10,000+ caracteres en < 150ms
    assert.ok(
      segElapsed < 150,
      `Segmentation exceeded budget: took ${segElapsed.toFixed(2)}ms for ${layout.characters.length} characters`
    );

    // 2. Benchmark de creación de animación para 1,000 caracteres
    const text1k = "Motion Graphics. ".repeat(70); // ~1,190 chars (~1,050 non-whitespace)
    const t1 = performance.now();
    const anim = animateText({ id: "large_text", text: text1k }, {
      scope: "character",
      animation: fadeIn({ id: "fade" } as any, { duration: 0.3 }),
      stagger: 0.01,
    });
    const animElapsed = performance.now() - t1;

    assert.ok(anim.children.length >= 900);
    // Instanciar 1,000 subtargets en < 100ms
    assert.ok(
      animElapsed < 100,
      `Animation instantiation exceeded budget: took ${animElapsed.toFixed(2)}ms for ${anim.children.length} instances`
    );
  });
});

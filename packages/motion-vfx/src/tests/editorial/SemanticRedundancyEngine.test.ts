import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { SemanticRedundancyEngine } from "../../editorial/performance/semantic-redundancy-engine.js";
import { PerformanceSegment } from "../../editorial/performance/performance-types.js";

describe("RF-056 — SemanticRedundancyEngine Suite (REQ-056.010 - REQ-056.020)", () => {
  it("detects high redundancy on identical and semantically equivalent phrases with scores in [0, 1]", () => {
    const segments: PerformanceSegment[] = [
      {
        id: "seg_a",
        sourceClipId: "clip_1",
        startSeconds: 0,
        endSeconds: 4,
        transcript: "El proyecto costó cincuenta millones de dólares.",
        confidence: 0.95,
        markers: [],
      },
      {
        id: "seg_b",
        sourceClipId: "clip_2",
        startSeconds: 5,
        endSeconds: 9,
        transcript: "El proyecto costó cincuenta millones de dólares.",
        confidence: 0.95,
        markers: [],
      },
    ];

    const results = SemanticRedundancyEngine.analyze(segments);
    assert.equal(results.length, 1);
    const candidate = results[0];
    assert.ok(candidate.redundancyScore >= 0.75);
    assert.ok(candidate.redundancyScore <= 1.0);
    assert.equal(candidate.semanticSimilarity, 1.0);
    assert.equal(candidate.informationOverlap, 1.0);
  });

  it("REQ-056.020: preserves segment B when it brings new facts, citations or figures", () => {
    const segments: PerformanceSegment[] = [
      {
        id: "seg_simple",
        sourceClipId: "clip_1",
        startSeconds: 0,
        endSeconds: 4,
        transcript: "El proyecto costó mucho dinero.",
        confidence: 0.9,
        markers: [],
        evidenceProtection: false,
      },
      {
        id: "seg_evidenced",
        sourceClipId: "clip_2",
        startSeconds: 10,
        endSeconds: 15,
        transcript: "Según el informe financiero de 2024, el proyecto costó cincuenta millones.",
        confidence: 0.95,
        markers: [],
        evidenceProtection: true,
      },
    ];

    const results = SemanticRedundancyEngine.analyze(segments);
    assert.equal(results.length, 1);
    const candidate = results[0];
    assert.equal(candidate.recommendation, "KEEP_B");
    assert.ok(candidate.reason.includes("datos fácticos") || candidate.reason.includes("evidencia"));
  });

  it("yields KEEP_BOTH for completely different phrases", () => {
    const segments: PerformanceSegment[] = [
      {
        id: "seg_1",
        sourceClipId: "clip_1",
        startSeconds: 0,
        endSeconds: 4,
        transcript: "El clima en la montaña es sumamente frío.",
        confidence: 0.95,
        markers: [],
      },
      {
        id: "seg_2",
        sourceClipId: "clip_2",
        startSeconds: 5,
        endSeconds: 9,
        transcript: "La economía digital transformó el comercio internacional.",
        confidence: 0.95,
        markers: [],
      },
    ];

    const results = SemanticRedundancyEngine.analyze(segments);
    assert.equal(results.length, 0); // No redundancy detected, skipped
  });

  it("REQ-056.003: produces byte-identical deterministic results on re-execution", () => {
    const segments: PerformanceSegment[] = [
      {
        id: "s1",
        sourceClipId: "c1",
        startSeconds: 0,
        endSeconds: 3,
        transcript: "La junta directiva votó en contra de la propuesta.",
        confidence: 0.92,
        markers: [],
      },
      {
        id: "s2",
        sourceClipId: "c2",
        startSeconds: 4,
        endSeconds: 7,
        transcript: "Los directores rechazaron unánimemente la iniciativa.",
        confidence: 0.91,
        markers: [],
      },
    ];

    const run1 = SemanticRedundancyEngine.analyze(segments);
    const run2 = SemanticRedundancyEngine.analyze(segments);

    assert.deepEqual(run1, run2);
    assert.equal(JSON.stringify(run1), JSON.stringify(run2));
  });
});

import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { BrollRanker } from "../../media-intelligence/core/BrollRanker.js";
import { Asset } from "../../media-intelligence/types/index.js";

describe("Fase 6 — B-roll Ranking & Candidate Selection Tests", () => {
  it("ranks B-roll shots by object detection relevance and quality scores", () => {
    const assetA: Asset = {
      id: "vid_city",
      type: "video",
      source: { uri: "/media/city.mp4" },
      metadata: { filename: "city.mp4", mimeType: "video/mp4", duration: 10.0 },
      status: "available",
      shots: [
        {
          id: "shot_car",
          start: 0.0,
          end: 5.0,
          keyframes: [0, 1.25, 2.5, 3.75, 5.0],
          analysis: {
            objects: [{ label: "car", bbox: { x: 0, y: 0, width: 100, height: 100 }, confidence: 0.9 }],
            quality: { sharpness: 0.9, exposure: 0.9, stability: 0.9, resolutionScore: 1.0, overall: 0.9 },
          },
        },
        {
          id: "shot_person",
          start: 5.0,
          end: 10.0,
          keyframes: [5.0, 6.25, 7.5, 8.75, 10.0],
          analysis: {
            objects: [{ label: "person", bbox: { x: 0, y: 0, width: 100, height: 100 }, confidence: 0.95 }],
            quality: { sharpness: 0.95, exposure: 0.95, stability: 0.95, resolutionScore: 1.0, overall: 0.95 },
          },
        },
      ],
    };

    // Búsqueda de planos que contengan "person"
    const ranked = BrollRanker.rankCandidates([assetA], undefined, ["person"]);
    assert.strictEqual(ranked.length, 2);
    // El shot_person debe encabezar el ranking con mayor puntuación
    assert.strictEqual(ranked[0].shotId, "shot_person");
    assert.ok(ranked[0].finalScore > ranked[1].finalScore);
  });
});

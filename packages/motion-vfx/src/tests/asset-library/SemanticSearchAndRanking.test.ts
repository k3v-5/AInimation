import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { SemanticMediaIndex } from "../../asset-library/core/SemanticMediaIndex.js";
import { IntelligentAsset } from "../../asset-library/types/index.js";

describe("Fase 10 — Semantic Search & Ranking Tests", () => {
  it("searches shots by semantic similarity and ranks top candidates", () => {
    const index = new SemanticMediaIndex();

    const asset1: IntelligentAsset = {
      id: "asset_01",
      type: "video",
      filename: "ai_robot.mp4",
      duration: 10.0,
      provenance: {
        source: "library",
        license: "royalty-free",
        importDate: new Date().toISOString(),
        originalPath: "/assets/ai_robot.mp4",
      },
      tags: ["ai", "robotics", "future"],
      userCorrections: {},
      metadata: {},
      shots: [
        {
          id: "shot_robot_01",
          assetId: "asset_01",
          start: 0,
          end: 5.0,
          duration: 5.0,
          description: "Humanoid AI robot walking in a high-tech lab",
          analysis: {
            objects: ["robot", "lab"],
            environment: ["laboratory"],
            action: ["walking"],
            camera: { shot: "medium", movement: "tracking" },
            qualityScore: 0.98,
          },
        },
      ],
    };

    index.indexAsset(asset1);

    const results = index.searchShots("robotics artificial intelligence");
    assert.strictEqual(results.length, 1);
    assert.strictEqual(results[0].shot.id, "shot_robot_01");
    assert.strictEqual(results[0].score > 0.5, true);
  });
});

import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AssetRankingEngine } from "../../broll-retrieval/core/AssetRankingEngine.js";
import { IndexedAsset } from "../../broll-retrieval/types/index.js";

describe("Fase 15 — Asset Ranking & Scoring Tests", () => {
  it("calculates explainable multicriteria score including text-safe compatibility and reuse penalty", () => {
    const asset: IndexedAsset = {
      id: "asset_01",
      uri: "file://clips/coding.mp4",
      fingerprint: "hash_01",
      duration: 5.0,
      orientation: "portrait",
      tags: ["coding", "laptop", "developer"],
      shots: [
        {
          id: "shot_01",
          start: 0,
          end: 5.0,
          objects: ["laptop"],
          hasFace: true,
          textSafeSide: "left",
          quality: 0.9,
          energy: 0.8,
        },
      ],
      license: { source: "user", attributionRequired: false, commercialUse: true },
      usageCount: 1,
    };

    // 1. Consulta solicitando espacio a la izquierda
    const scoreSafe = AssetRankingEngine.scoreAsset(asset, {
      intent: "developer coding laptop",
      targetDuration: 3.0,
      textSafeSide: "left",
    });

    assert.strictEqual(scoreSafe.semanticRelevance >= 0.9, true);
    assert.strictEqual(scoreSafe.quality, 0.9);
    assert.strictEqual(scoreSafe.textSafeMatch, 1.0);
    assert.strictEqual(scoreSafe.reusePenalty, 0.15); // usageCount 1 * 0.15
    assert.strictEqual(scoreSafe.total > 0.6, true);

    // 2. Consulta solicitando espacio a la derecha (penaliza textSafeMatch)
    const scoreUnsafe = AssetRankingEngine.scoreAsset(asset, {
      intent: "developer coding laptop",
      targetDuration: 3.0,
      textSafeSide: "right",
    });
    assert.strictEqual(scoreUnsafe.textSafeMatch, 0.4);
    assert.strictEqual(scoreUnsafe.total < scoreSafe.total, true);
  });
});

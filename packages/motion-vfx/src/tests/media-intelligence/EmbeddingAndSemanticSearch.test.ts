import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { EmbeddingService } from "../../media-intelligence/core/EmbeddingService.js";

describe("Fase 6 — Embedding & Semantic Vector Search Tests", () => {
  it("calculates cosine similarity between vectors accurately", () => {
    const vecA = [1, 0, 0];
    const vecB = [1, 0, 0];
    const vecC = [0, 1, 0];

    // Vectores idénticos -> similitud = 1.0
    assert.strictEqual(EmbeddingService.cosineSimilarity(vecA, vecB), 1.0);
    // Vectores ortogonales -> similitud = 0.0
    assert.strictEqual(EmbeddingService.cosineSimilarity(vecA, vecC), 0.0);
  });

  it("generates deterministic mock vectors with unit norm", () => {
    const v1 = EmbeddingService.generateDeterministicMockVector("apple");
    const v2 = EmbeddingService.generateDeterministicMockVector("apple");
    assert.deepStrictEqual(v1, v2);

    const norm = Math.sqrt(v1.reduce((acc, v) => acc + v * v, 0));
    assert.ok(Math.abs(norm - 1.0) < 1e-6);
  });
});

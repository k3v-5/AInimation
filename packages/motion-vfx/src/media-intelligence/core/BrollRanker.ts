import { Asset, BrollCandidate, MediaShot } from "../types/index.js";
import { EmbeddingService } from "./EmbeddingService.js";

export interface BrollRankWeights {
  semantic: number;
  visual: number;
  quality: number;
  relevance: number;
}

/**
 * Evaluador y clasificador multicriterio de candidatos B-roll para el planificador de IA (Fase 6).
 */
export class BrollRanker {
  public static readonly DEFAULT_WEIGHTS: BrollRankWeights = {
    semantic: 0.4,
    visual: 0.2,
    quality: 0.2,
    relevance: 0.2,
  };

  /**
   * Calcula la puntuación final de un candidato B-roll combinando semántica, calidad y objetos.
   */
  public static scoreShot(
    shot: MediaShot,
    assetId: string,
    queryVector?: number[],
    requiredObjects?: string[],
    weights: BrollRankWeights = this.DEFAULT_WEIGHTS
  ): BrollCandidate {
    let semanticScore = 0.5;
    let visualScore = 0.5;

    // 1. Puntuación semántica / visual si hay embeddings
    if (queryVector && shot.analysis?.embedding?.vector) {
      visualScore = Math.max(
        0,
        EmbeddingService.cosineSimilarity(queryVector, shot.analysis.embedding.vector)
      );
      semanticScore = visualScore;
    }

    // 2. Calidad técnica
    const qualityScore = shot.analysis?.quality?.overall ?? 0.8;

    // 3. Relevancia de objetos requeridos
    let relevanceScore = 1.0;
    if (requiredObjects && requiredObjects.length > 0) {
      const shotObjects = (shot.analysis?.objects ?? []).map((o) => o.label.toLowerCase());
      const matched = requiredObjects.filter((req) =>
        shotObjects.includes(req.toLowerCase())
      ).length;
      relevanceScore = matched / requiredObjects.length;
    }

    const finalScore =
      semanticScore * weights.semantic +
      visualScore * weights.visual +
      qualityScore * weights.quality +
      relevanceScore * weights.relevance;

    return {
      assetId,
      shotId: shot.id,
      range: { assetId, start: shot.start, end: shot.end },
      relevance: relevanceScore,
      visualScore,
      semanticScore,
      qualityScore,
      finalScore: Math.round(finalScore * 1000) / 1000,
    };
  }

  /**
   * Clasifica y ordena todos los shots de una lista de assets candidatos.
   */
  public static rankCandidates(
    assets: Asset[],
    queryVector?: number[],
    requiredObjects?: string[]
  ): BrollCandidate[] {
    const candidates: BrollCandidate[] = [];

    for (const asset of assets) {
      if (!asset.shots || asset.shots.length === 0) continue;

      for (const shot of asset.shots) {
        const scored = this.scoreShot(shot, asset.id, queryVector, requiredObjects);
        candidates.push(scored);
      }
    }

    return candidates.sort((a, b) => b.finalScore - a.finalScore);
  }
}

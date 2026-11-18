import { BRollQuery, IndexedAsset, ScoreBreakdown } from "../types/index.js";

/**
 * Motor de puntuación y ranking multicriterio para selección de B-Roll (Fase 15).
 */
export class AssetRankingEngine {
  /**
   * Calcula el desglose de puntuación de un asset para una consulta específica.
   */
  public static scoreAsset(asset: IndexedAsset, query: BRollQuery): ScoreBreakdown {
    const intentWords = query.intent.toLowerCase().split(/\s+/);
    let matchedTags = 0;
    for (const tag of asset.tags) {
      if (intentWords.some((w) => tag.toLowerCase().includes(w) || w.includes(tag.toLowerCase()))) {
        matchedTags++;
      }
    }
    const semanticRelevance = Math.min(1.0, matchedTags / Math.max(1, intentWords.length));

    // Calidad promedio de las tomas
    const quality =
      asset.shots.length > 0
        ? asset.shots.reduce((acc, s) => acc + s.quality, 0) / asset.shots.length
        : 0.7;

    // Ajuste de duración: penalizar si sobra demasiado metraje innecesario
    const durationDiff = Math.abs(asset.duration - query.targetDuration);
    const durationFit = Math.max(0, 1.0 - durationDiff / Math.max(asset.duration, 10.0));

    // Espacio seguro para texto (si se solicita)
    let textSafeMatch = 1.0;
    if (query.textSafeSide) {
      const hasMatchingShot = asset.shots.some((s) => s.textSafeSide === query.textSafeSide);
      textSafeMatch = hasMatchingShot ? 1.0 : 0.4;
    }

    // Penalización por reutilización frecuente
    const reusePenalty = Math.min(0.6, asset.usageCount * 0.15);

    // Ponderación total
    const rawTotal =
      semanticRelevance * 0.4 +
      quality * 0.25 +
      durationFit * 0.15 +
      textSafeMatch * 0.2 -
      reusePenalty;

    const total = Math.round(Math.max(0, Math.min(1.0, rawTotal)) * 1000) / 1000;

    return {
      semanticRelevance: Math.round(semanticRelevance * 100) / 100,
      quality: Math.round(quality * 100) / 100,
      durationFit: Math.round(durationFit * 100) / 100,
      textSafeMatch: Math.round(textSafeMatch * 100) / 100,
      reusePenalty: Math.round(reusePenalty * 100) / 100,
      total,
    };
  }
}

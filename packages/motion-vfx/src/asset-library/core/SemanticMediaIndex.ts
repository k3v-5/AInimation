import { EmbeddingService } from "../../media-intelligence/core/EmbeddingService.js";
import {
  BestVisualQuery,
  BestVisualResult,
  IntelligentAsset,
  SemanticSearchOptions,
  Shot,
} from "../types/index.js";
import { LicenseManager } from "./LicenseManager.js";

interface IndexedShotEntry {
  shot: Shot;
  asset: IntelligentAsset;
  vector: number[];
  text: string;
}

/**
 * Índice de medios inteligente con búsqueda semántica vectorial y ranking multicriterio (Fase 10).
 */
export class SemanticMediaIndex {
  private assets = new Map<string, IntelligentAsset>();
  private flatShots: IndexedShotEntry[] = [];

  public indexAsset(asset: IntelligentAsset): void {
    this.assets.set(asset.id, asset);
    for (const shot of asset.shots) {
      const text =
        `${shot.description} ${asset.tags.join(" ")} ${shot.analysis.objects.join(" ")}`.toLowerCase();
      const vector =
        shot.embedding ??
        EmbeddingService.generateDeterministicMockVector(text);

      this.flatShots.push({
        shot,
        asset,
        vector,
        text,
      });
    }
  }

  public getAsset(id: string): IntelligentAsset | undefined {
    return this.assets.get(id);
  }

  public get totalAssets(): number {
    return this.assets.size;
  }

  public getAllShots(): Shot[] {
    return this.flatShots.map((entry) => entry.shot);
  }

  /**
   * Búsqueda semántica de tomas aplicando filtros de metadatos y similitud vectorial.
   */
  public searchShots(
    query: string,
    options: SemanticSearchOptions = {}
  ): { shot: Shot; asset: IntelligentAsset; score: number }[] {
    const queryVector = EmbeddingService.generateDeterministicMockVector(query);
    const queryTokens = query.toLowerCase().split(/\s+/);
    const results: { shot: Shot; asset: IntelligentAsset; score: number }[] = [];

    for (let i = 0; i < this.flatShots.length; i++) {
      const entry = this.flatShots[i];
      const asset = entry.asset;
      const shot = entry.shot;

      if (options.license && !LicenseManager.canUseInRender(asset.provenance.license)) {
        continue;
      }

      if (options.minDuration && shot.duration < options.minDuration) continue;
      if (options.maxDuration && shot.duration > options.maxDuration) continue;

      const sim = EmbeddingService.cosineSimilarity(queryVector, entry.vector);

      // Token match boost
      let tokenMatches = 0;
      for (let t = 0; t < queryTokens.length; t++) {
        if (entry.text.includes(queryTokens[t])) tokenMatches++;
      }
      const lexicalScore = queryTokens.length > 0 ? tokenMatches / queryTokens.length : 0;

      // Puntuación combinada (Semántica/Léxica 60% + Calidad visual 40%)
      const semanticRelevance = Math.max(Math.max(0, sim), lexicalScore);
      const score = 0.6 * semanticRelevance + 0.4 * shot.analysis.qualityScore;

      results.push({ shot, asset, score });
    }

    results.sort((a, b) => b.score - a.score);

    const limit = options.limit ?? 10;
    return results.slice(0, limit);
  }

  /**
   * Recupera la toma más óptima para un concepto visual y duración objetivo (Fase 10 API).
   */
  public findBestVisual(query: BestVisualQuery): BestVisualResult | undefined {
    const results = this.searchShots(query.concept, {
      minDuration: Math.min(query.duration * 0.5, 1.0),
      limit: 5,
    });

    if (results.length === 0) return undefined;

    const best = results[0];
    return {
      shot: best.shot,
      asset: best.asset,
      confidence: Math.round(best.score * 100) / 100,
      reasoning: `Selected shot '${best.shot.id}' with ${best.shot.description} matching concept '${query.concept}' (confidence: ${best.score.toFixed(2)}).`,
    };
  }
}

import { BRollQuery, BRollResolution, RankedCandidate } from "../types/index.js";
import { AssetCatalogIndex } from "./AssetCatalogIndex.js";
import { AssetRankingEngine } from "./AssetRankingEngine.js";
import { SubclipOptimizer } from "./SubclipOptimizer.js";

/**
 * Resolvedor integral de B-Roll para integración con el AI Director (Fase 15).
 */
export class BRollResolver {
  constructor(private catalog: AssetCatalogIndex) {}

  /**
   * Resuelve una consulta de B-Roll devolviendo el candidato principal y alternativas clasificadas.
   */
  public resolveBRoll(query: BRollQuery): BRollResolution {
    const candidates = this.catalog.filterCandidates(query);

    if (candidates.length === 0) {
      throw new Error(`NO_BROLL_CANDIDATES: No suitable assets found for intent '${query.intent}'.`);
    }

    const scored: RankedCandidate[] = candidates.map((asset) => {
      const score = AssetRankingEngine.scoreAsset(asset, query);
      const subclip = SubclipOptimizer.findBestSubclip(asset, query.targetDuration);
      const rationale = `Asset '${asset.id}' scored ${score.total} (relevance: ${score.semanticRelevance}, quality: ${score.quality}, textSafe: ${score.textSafeMatch})`;

      return {
        assetId: asset.id,
        subclipStart: subclip.start,
        subclipEnd: subclip.end,
        score,
        rationale,
      };
    });

    scored.sort((a, b) => b.score.total - a.score.total);

    const primary = scored[0];
    const alternatives = scored.slice(1);

    return {
      primary,
      alternatives,
    };
  }
}

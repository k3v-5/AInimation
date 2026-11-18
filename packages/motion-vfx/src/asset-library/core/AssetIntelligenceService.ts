import {
  BestVisualQuery,
  BestVisualResult,
  IntelligentAsset,
  SemanticSearchOptions,
  Shot,
} from "../types/index.js";
import { SemanticMediaIndex } from "./SemanticMediaIndex.js";

/**
 * Servicio central de Inteligencia de Medios y Biblioteca Semántica (Fase 10).
 */
export class AssetIntelligenceService {
  private index = new SemanticMediaIndex();

  public registerAsset(asset: IntelligentAsset): void {
    this.index.indexAsset(asset);
  }

  public getAsset(id: string): IntelligentAsset | undefined {
    return this.index.getAsset(id);
  }

  public findBestVisual(query: BestVisualQuery): BestVisualResult | undefined {
    return this.index.findBestVisual(query);
  }

  public search(
    query: string,
    options?: SemanticSearchOptions
  ): { shot: Shot; asset: IntelligentAsset; score: number }[] {
    return this.index.searchShots(query, options);
  }

  /**
   * Registra una corrección manual del usuario sobre una etiqueta generada automáticamente.
   */
  public recordUserCorrection(
    assetId: string,
    originalTag: string,
    correctedTag: string
  ): void {
    const asset = this.index.getAsset(assetId);
    if (asset) {
      asset.userCorrections[originalTag] = correctedTag;
      // Reemplazar etiqueta en la lista
      const idx = asset.tags.indexOf(originalTag);
      if (idx !== -1) {
        asset.tags[idx] = correctedTag;
      } else {
        asset.tags.push(correctedTag);
      }
    }
  }

  /**
   * Detecta duplicados o casi-duplicados basados en coincidencia de SHA-256 o similitud de nombre.
   */
  public detectDuplicates(
    assetId: string
  ): { duplicateAssetId: string; reason: string }[] {
    const target = this.index.getAsset(assetId);
    if (!target) return [];

    const duplicates: { duplicateAssetId: string; reason: string }[] = [];

    for (const [id, asset] of (this.index as any).assets.entries()) {
      if (id === assetId) continue;

      if (
        target.metadata.sha256 &&
        asset.metadata.sha256 &&
        target.metadata.sha256 === asset.metadata.sha256
      ) {
        duplicates.push({
          duplicateAssetId: id,
          reason: "Identical SHA-256 binary hash.",
        });
      } else if (
        target.filename.toLowerCase().replace(/_copy|\_final|\d+/g, "") ===
        asset.filename.toLowerCase().replace(/_copy|\_final|\d+/g, "")
      ) {
        duplicates.push({
          duplicateAssetId: id,
          reason: "Near-duplicate filename pattern.",
        });
      }
    }

    return duplicates;
  }
}

import { BRollQuery, IndexedAsset } from "../types/index.js";

/**
 * Catálogo indexado de medios con soporte de huellas digitales y búsqueda de candidatos (Fase 15).
 */
export class AssetCatalogIndex {
  private assets = new Map<string, IndexedAsset>();

  public registerAsset(asset: IndexedAsset): void {
    this.assets.set(asset.id, asset);
  }

  public getAsset(id: string): IndexedAsset | undefined {
    return this.assets.get(id);
  }

  public getAllAssets(): IndexedAsset[] {
    return Array.from(this.assets.values());
  }

  /**
   * Detecta si un nuevo asset es duplicado o cuasi-duplicado de uno existente.
   */
  public findDuplicate(fingerprint: string): IndexedAsset | undefined {
    for (const asset of this.assets.values()) {
      if (asset.fingerprint === fingerprint) {
        return asset;
      }
    }
    return undefined;
  }

  /**
   * Filtra candidatos que cumplan los criterios básicos de la query.
   */
  public filterCandidates(query: BRollQuery): IndexedAsset[] {
    const avoid = new Set(query.avoidAssetIds ?? []);
    const intentWords = query.intent.toLowerCase().split(/\s+/);

    return this.getAllAssets().filter((asset) => {
      if (avoid.has(asset.id)) return false;
      if (asset.duration < query.targetDuration) return false;

      if (query.preferredOrientation && asset.orientation !== query.preferredOrientation) {
        // Permitir crop pero no descartar totalmente a menos que sea estricto
      }

      // Debe coincidir con al menos un tag o palabra del intent
      const matchesIntent = asset.tags.some((tag) =>
        intentWords.some((w) => tag.toLowerCase().includes(w) || w.includes(tag.toLowerCase()))
      );

      return matchesIntent || asset.tags.length === 0;
    });
  }
}

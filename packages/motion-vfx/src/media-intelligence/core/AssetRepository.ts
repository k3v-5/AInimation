import { ValidationError } from "../../errors/index.js";
import { Asset, AssetContext, AssetQuery, SmartCollection } from "../types/index.js";
import { BrollRanker } from "./BrollRanker.js";
import { ChecksumService } from "./ChecksumService.js";
import { EmbeddingService } from "./EmbeddingService.js";

/**
 * Repositorio de assets multimedia con búsqueda semántica y colecciones inteligentes (Fase 6).
 */
export class AssetRepository {
  private assets = new Map<string, Asset>();
  private collections = new Map<string, SmartCollection>();

  public create(asset: Asset): this {
    if (!asset || !asset.id) {
      throw new ValidationError("Asset requires a valid 'id'.");
    }
    if (this.assets.has(asset.id)) {
      throw new ValidationError(`DUPLICATE_ASSET_ID: Asset '${asset.id}' already exists.`);
    }

    if (asset.source.checksum) {
      ChecksumService.registerAsset(asset.source.checksum, asset.id);
    }

    this.assets.set(asset.id, { ...asset });
    return this;
  }

  public get(id: string): Asset | undefined {
    return this.assets.get(id);
  }

  public has(id: string): boolean {
    return this.assets.has(id);
  }

  public update(asset: Asset): boolean {
    if (!this.assets.has(asset.id)) {
      return false;
    }
    this.assets.set(asset.id, { ...asset });
    return true;
  }

  public delete(id: string): boolean {
    return this.assets.delete(id);
  }

  public get size(): number {
    return this.assets.size;
  }

  public list(): Asset[] {
    return Array.from(this.assets.values());
  }

  public search(query: AssetQuery): Asset[] {
    return Array.from(this.assets.values()).filter((asset) => {
      // 1. Filtrar por tipo
      if (query.type && asset.type !== query.type) {
        return false;
      }

      // 2. Filtrar por tags
      if (query.tags && query.tags.length > 0) {
        const assetTags = asset.tags ?? [];
        const hasAllTags = query.tags.every((t) =>
          assetTags.map((at) => at.toLowerCase()).includes(t.toLowerCase())
        );
        if (!hasAllTags) return false;
      }

      // 3. Filtrar por texto en nombre de archivo o transcripción
      if (query.text) {
        const queryText = query.text.toLowerCase();
        const filenameMatch = asset.metadata.filename.toLowerCase().includes(queryText);
        const transcriptMatch = (asset.transcript?.segments ?? []).some((seg) =>
          seg.text.toLowerCase().includes(queryText)
        );
        if (!filenameMatch && !transcriptMatch) return false;
      }

      // 4. Filtrar por dimensiones
      if (query.minWidth && (asset.metadata.width ?? 0) < query.minWidth) return false;
      if (query.minHeight && (asset.metadata.height ?? 0) < query.minHeight) return false;

      // 5. Filtrar por duración
      if (query.minDuration && (asset.metadata.duration ?? 0) < query.minDuration) return false;
      if (query.maxDuration && (asset.metadata.duration ?? 0) > query.maxDuration) return false;

      return true;
    });
  }

  public relink(assetId: string, newUri: string, newChecksum?: string): boolean {
    const asset = this.assets.get(assetId);
    if (!asset) return false;

    asset.source.uri = newUri;
    if (newChecksum) {
      asset.source.checksum = newChecksum;
    }
    asset.status = "available";
    return true;
  }

  public addSmartCollection(collection: SmartCollection): this {
    this.collections.set(collection.id, collection);
    return this;
  }

  public getSmartCollectionResults(collectionId: string): Asset[] {
    const col = this.collections.get(collectionId);
    if (!col) return [];
    return this.search(col.query);
  }

  public buildAIContext(assetId: string, query?: string): AssetContext {
    const asset = this.assets.get(assetId);
    if (!asset) {
      throw new ValidationError(`ASSET_NOT_FOUND: Asset '${assetId}' does not exist.`);
    }

    let queryVec: number[] | undefined;
    if (query) {
      queryVec = EmbeddingService.generateDeterministicMockVector(query);
    }

    const relevantShots = BrollRanker.rankCandidates([asset], queryVec);

    return {
      asset,
      relevantShots,
      transcript: asset.transcript,
      summary: `Asset ${asset.id} (${asset.type}) - Duration: ${asset.metadata.duration ?? 0}s, ${asset.shots?.length ?? 0} shots indexed.`,
    };
  }
}

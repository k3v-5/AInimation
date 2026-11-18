import crypto from "crypto";
import {
  ShotIndexRecord,
  PersistentIndexManifest,
  VisualFeature,
} from "./perception.types.js";
import { IEmbeddingProvider, DeterministicLocalEmbeddingAdapter } from "./embedding-provider.js";

/**
 * REQ-013 §7, §8 & §9: Persistent Local Multimodal Indexer
 * Gestiona el almacenamiento local, indexación incremental,
 * persistencia y reconstrucción determinista del catálogo de planos audiovisuales.
 */
export class MultimodalIndexer {
  public static readonly SCHEMA_VERSION = "4.0.0";
  private readonly records: Map<string, ShotIndexRecord> = new Map();
  private readonly assetHashes: Map<string, string> = new Map();
  private readonly embeddingProvider: IEmbeddingProvider;

  constructor(provider?: IEmbeddingProvider) {
    this.embeddingProvider = provider || new DeterministicLocalEmbeddingAdapter();
  }

  public size(): number {
    return this.records.size;
  }

  public clear(): void {
    this.records.clear();
    this.assetHashes.clear();
  }

  /**
   * Indexa un plano con extracción de embedding multimodal y registro en memoria
   */
  public indexShot(params: {
    shotId: string;
    sourceAssetId: string;
    sourceAssetHash: string;
    startTimeSeconds: number;
    durationSeconds: number;
    visualFeatures: VisualFeature;
    detectedSubjects: string[];
    transcriptText?: string;
  }): ShotIndexRecord {
    const {
      shotId,
      sourceAssetId,
      sourceAssetHash,
      startTimeSeconds,
      durationSeconds,
      visualFeatures,
      detectedSubjects,
      transcriptText,
    } = params;

    // Generar embedding multimodal a partir de visuales y conceptos
    const embedding = this.embeddingProvider.generateVisualEmbedding(visualFeatures, [
      ...detectedSubjects,
      transcriptText || "",
    ]);

    const modelInfo = this.embeddingProvider.getModelInfo();

    const record: ShotIndexRecord = {
      shotId,
      sourceAssetId,
      sourceAssetHash,
      startTimeSeconds,
      durationSeconds,
      visualFeatures,
      detectedSubjects,
      transcriptText,
      embedding,
      modelProvenance: {
        providerType: modelInfo.providerType,
        modelId: modelInfo.id,
        modelVersion: modelInfo.version,
        modelHash: modelInfo.hash,
        runtime: modelInfo.runtime,
      },
    };

    this.records.set(shotId, record);
    this.assetHashes.set(sourceAssetId, sourceAssetHash);

    return record;
  }

  /**
   * Indexación incremental: actualiza únicamente los planos del activo modificado
   */
  public updateAsset(
    sourceAssetId: string,
    newAssetHash: string,
    newShots: Array<Omit<ShotIndexRecord, "sourceAssetId" | "sourceAssetHash" | "embedding" | "modelProvenance">>
  ): void {
    // 1. Eliminar planos anteriores del mismo activo
    this.removeAsset(sourceAssetId);

    // 2. Indexar nuevos planos con el nuevo hash
    for (const shot of newShots) {
      this.indexShot({
        ...shot,
        sourceAssetId,
        sourceAssetHash: newAssetHash,
      });
    }
  }

  /**
   * Elimina todos los planos vinculados a un activo dado
   */
  public removeAsset(sourceAssetId: string): number {
    let removedCount = 0;
    for (const [id, rec] of this.records) {
      if (rec.sourceAssetId === sourceAssetId) {
        this.records.delete(id);
        removedCount++;
      }
    }
    this.assetHashes.delete(sourceAssetId);
    return removedCount;
  }

  public getRecord(shotId: string): ShotIndexRecord | undefined {
    return this.records.get(shotId);
  }

  public getAllRecords(): ShotIndexRecord[] {
    return Array.from(this.records.values()).sort((a, b) => a.shotId.localeCompare(b.shotId));
  }

  /**
   * Genera el hash canónico SHA-256 del índice completo
   */
  public calculateCanonicalIndexHash(): string {
    const sorted = this.getAllRecords();
    const payload = JSON.stringify(sorted.map((r) => ({
      shotId: r.shotId,
      sourceAssetHash: r.sourceAssetHash,
      start: r.startTimeSeconds,
      dur: r.durationSeconds,
      embedding: r.embedding,
    })));

    return crypto.createHash("sha256").update(payload, "utf8").digest("hex");
  }

  /**
   * Serializa el índice completo y su manifiesto a un JSON canónico
   */
  public saveToJson(): string {
    const modelInfo = this.embeddingProvider.getModelInfo();
    const records = this.getAllRecords();
    const canonicalIndexHash = this.calculateCanonicalIndexHash();

    const manifest: PersistentIndexManifest = {
      schemaVersion: MultimodalIndexer.SCHEMA_VERSION,
      providerType: modelInfo.providerType,
      modelId: modelInfo.id,
      modelVersion: modelInfo.version,
      modelHash: modelInfo.hash,
      runtime: modelInfo.runtime,
      indexVersion: "1.0.0",
      assetCount: this.assetHashes.size,
      shotCount: records.length,
      sourceAssetHashes: Object.fromEntries(this.assetHashes.entries()),
      configurationHash: crypto.createHash("sha256").update(modelInfo.id + modelInfo.version).digest("hex"),
      canonicalIndexHash,
    };

    return JSON.stringify({ manifest, records }, null, 2);
  }

  /**
   * Restaura un índice desde un JSON validando su integridad
   */
  public loadFromJson(jsonString: string): void {
    let parsed: any;
    try {
      parsed = JSON.parse(jsonString);
    } catch (err) {
      throw new Error(`[INDEX_CORRUPT_ERROR] JSON de índice malformado: ${(err as Error).message}`);
    }

    const manifest: PersistentIndexManifest = parsed.manifest;
    if (!manifest || manifest.schemaVersion !== MultimodalIndexer.SCHEMA_VERSION) {
      throw new Error(`[INDEX_SCHEMA_MISMATCH] Se esperaba esquema '${MultimodalIndexer.SCHEMA_VERSION}'`);
    }

    const currentModel = this.embeddingProvider.getModelInfo();
    if (manifest.modelHash !== currentModel.hash || manifest.providerType !== currentModel.providerType) {
      throw new Error(
        `[INDEX_MODEL_MISMATCH] El índice fue construido con el modelo '${manifest.modelId}' (${manifest.providerType}, hash ${manifest.modelHash}), incompatible con '${currentModel.id}' (${currentModel.providerType}, hash ${currentModel.hash})`
      );
    }

    this.clear();
    for (const rec of parsed.records || []) {
      this.records.set(rec.shotId, rec);
    }
    for (const [k, v] of Object.entries(manifest.sourceAssetHashes || {})) {
      this.assetHashes.set(k, v as string);
    }

    const currentHash = this.calculateCanonicalIndexHash();
    if (currentHash !== manifest.canonicalIndexHash) {
      throw new Error("[INDEX_HASH_CORRUPTION] El hash canónico de los datos restaurados no coincide con el manifiesto.");
    }
  }
}

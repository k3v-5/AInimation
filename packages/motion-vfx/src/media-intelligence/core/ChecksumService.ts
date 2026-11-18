import { createHash } from "node:crypto";

/**
 * Servicio de hashing de contenido y deduplicación de assets (Fase 6).
 */
export class ChecksumService {
  private static deduplicationMap = new Map<string, string>(); // checksum -> assetId

  public static computeSHA256(content: string | Buffer): string {
    return createHash("sha256").update(content).digest("hex");
  }

  public static registerAsset(checksum: string, assetId: string): void {
    if (!this.deduplicationMap.has(checksum)) {
      this.deduplicationMap.set(checksum, assetId);
    }
  }

  public static findCanonicalAssetId(checksum: string): string | undefined {
    return this.deduplicationMap.get(checksum);
  }

  public static clear(): void {
    this.deduplicationMap.clear();
  }

  public static get size(): number {
    return this.deduplicationMap.size;
  }
}

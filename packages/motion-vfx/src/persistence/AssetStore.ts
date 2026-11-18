import * as fs from "node:fs/promises";
import * as path from "node:path";
import { ProjectSerializer } from "./ProjectSerializer.js";

export interface StoredAsset {
  assetId: string;
  name: string;
  type: string;
  path: string;
  sha256: string;
  sizeBytes: number;
}

/**
 * Almacén y validador de integridad para assets persistidos (Fase 18).
 */
export class AssetStore {
  private assets = new Map<string, StoredAsset>();

  public register(asset: StoredAsset): void {
    this.assets.set(asset.assetId, asset);
  }

  public get(assetId: string): StoredAsset | undefined {
    return this.assets.get(assetId);
  }

  public list(): StoredAsset[] {
    return Array.from(this.assets.values()).sort((a, b) => a.assetId.localeCompare(b.assetId));
  }

  public static async calculateFileHash(filePath: string): Promise<string> {
    const buffer = await fs.readFile(filePath);
    return ProjectSerializer.hashCanonical(buffer.toString("binary"));
  }
}

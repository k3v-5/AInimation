import { Time } from "../../core/types.js";
import { Frame } from "../types/index.js";
import { LRUCache } from "./LRUCache.js";

/**
 * Caché especializada para almacenar fotogramas decodificados indexados por asset y timestamp.
 */
export class FrameCache {
  private cache: LRUCache<string, Frame>;

  constructor(maxFrames = 120) {
    this.cache = new LRUCache<string, Frame>(maxFrames);
  }

  private makeKey(assetId: string, time: Time): string {
    return `${assetId}@${time.toFixed(4)}`;
  }

  public get(assetId: string, time: Time): Frame | undefined {
    return this.cache.get(this.makeKey(assetId, time));
  }

  public set(assetId: string, time: Time, frame: Frame): void {
    this.cache.set(this.makeKey(assetId, time), frame);
  }

  public has(assetId: string, time: Time): boolean {
    return this.cache.has(this.makeKey(assetId, time));
  }

  public clear(): void {
    this.cache.clear();
  }

  public get size(): number {
    return this.cache.size;
  }
}

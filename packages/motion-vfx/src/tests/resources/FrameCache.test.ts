import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { FrameCache } from "../../resources/cache/FrameCache.js";
import { LRUCache } from "../../resources/cache/LRUCache.js";

describe("Fase 5A — LRU Cache & Frame Cache Tests", () => {
  it("evicts oldest entries when LRUCache exceeds maxSize", () => {
    const cache = new LRUCache<string, number>(3);
    cache.set("a", 1);
    cache.set("b", 2);
    cache.set("c", 3);

    // Acceder a 'a' para marcarlo como recientemente usado
    assert.strictEqual(cache.get("a"), 1);

    // Insertar 'd' -> debe expulsar 'b' (el más viejo no accedido)
    cache.set("d", 4);

    assert.strictEqual(cache.has("b"), false);
    assert.strictEqual(cache.has("a"), true);
    assert.strictEqual(cache.has("c"), true);
    assert.strictEqual(cache.has("d"), true);
  });

  it("stores and retrieves frames indexed by asset and timestamp in FrameCache", () => {
    const frameCache = new FrameCache(10);
    const mockFrame = {
      width: 1920,
      height: 1080,
      format: "rgba8" as const,
      timestamp: 1.5,
    };

    frameCache.set("video_1", 1.5, mockFrame);
    assert.strictEqual(frameCache.has("video_1", 1.5), true);
    assert.strictEqual(frameCache.get("video_1", 1.5), mockFrame);
    assert.strictEqual(frameCache.get("video_1", 2.0), undefined);
  });
});

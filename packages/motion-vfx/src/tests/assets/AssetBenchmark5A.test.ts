import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AssetRegistry } from "../../assets/AssetRegistry.js";

describe("Fase 5A — Asset Registry Performance & Scalability Benchmark Suite", () => {
  it("benchmarks registering and looking up 10,000 assets in O(1)", () => {
    const registry = new AssetRegistry();
    const count = 10000;

    const t0 = performance.now();
    for (let i = 0; i < count; i++) {
      registry.register({
        id: `asset_${i}`,
        type: i % 2 === 0 ? "video" : "image",
        source: { path: `/media/file_${i}.mp4` },
      });
    }
    const regTime = performance.now() - t0;

    assert.strictEqual(registry.size, count);
    assert.ok(regTime < 200, `Registering 10k assets took ${regTime.toFixed(2)}ms (budget: <200ms)`);

    // Lookup benchmark
    const t1 = performance.now();
    for (let i = 0; i < count; i++) {
      const asset = registry.get(`asset_${i}`);
      assert.ok(asset !== undefined);
    }
    const lookupTime = performance.now() - t1;

    assert.ok(lookupTime < 50, `10k lookups took ${lookupTime.toFixed(2)}ms (budget: <50ms)`);
  });
});

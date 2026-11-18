import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AssetRegistry } from "../../assets/AssetRegistry.js";
import { ResourceManager } from "../../resources/manager/ResourceManager.js";

describe("Fase 5A — Resource Manager & Frame Provider Tests", () => {
  it("requests frames on-demand and caches them automatically", () => {
    const registry = new AssetRegistry();
    registry.register({
      id: "clip_sample",
      type: "video",
      source: { path: "sample.mp4" },
      metadata: { width: 1280, height: 720 },
    });

    let decodeCalls = 0;
    const resourceManager = new ResourceManager(registry, 50);

    resourceManager.registerProvider("clip_sample", {
      getFrame: (assetId, time) => {
        decodeCalls++;
        return {
          width: 1280,
          height: 720,
          format: "rgba8",
          timestamp: time,
          data: `frame_data_${time}`,
        };
      },
    });

    // 1ra llamada -> decodifica
    const frame1 = resourceManager.getFrame("clip_sample", 0.5);
    assert.strictEqual(decodeCalls, 1);
    assert.strictEqual(frame1.width, 1280);

    // 2da llamada con mismo tiempo -> usa caché (0 decodificaciones extras)
    const frame2 = resourceManager.getFrame("clip_sample", 0.5);
    assert.strictEqual(decodeCalls, 1);
    assert.strictEqual(frame2, frame1);

    // 3ra llamada con tiempo diferente -> decodifica
    resourceManager.getFrame("clip_sample", 1.0);
    assert.strictEqual(decodeCalls, 2);
  });
});

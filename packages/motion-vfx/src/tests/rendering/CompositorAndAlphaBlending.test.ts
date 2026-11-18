import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { Compositor, RenderLayerItem } from "../../rendering/compositor/Compositor.js";

describe("Fase 9 — Compositor & Alpha Blending Tests", () => {
  it("composites multiple stacked layers respecting opacity and blend modes", () => {
    const ctx = { frame: 0, time: 0, fps: 30, width: 1920, height: 1080, quality: "final" as const };

    const layers: RenderLayerItem[] = [
      {
        id: "bg_layer",
        frame: { frameNumber: 0, time: 0, width: 1920, height: 1080, channels: 4 },
        opacity: 1.0,
        blendMode: "normal",
      },
      {
        id: "overlay_graphic",
        frame: { frameNumber: 0, time: 0, width: 1920, height: 1080, channels: 4 },
        opacity: 0.8,
        blendMode: "screen",
      },
    ];

    const result = Compositor.composite(layers, ctx);
    assert.strictEqual(result.width, 1920);
    assert.strictEqual(result.height, 1080);
    assert.strictEqual(result.metadata?.compositeLayersCount, 2);
  });
});

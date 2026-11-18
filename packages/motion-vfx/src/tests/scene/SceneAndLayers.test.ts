import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { Layer } from "../../scene/core/Layer.js";
import { Scene } from "../../scene/core/Scene.js";

describe("Fase 5H — Scene, Layers & Hierarchy Tests", () => {
  it("creates scene and filters active layers and semantic markers accurately", () => {
    const scene = new Scene({
      id: "scene_main",
      duration: 10.0,
      width: 1080,
      height: 1920,
    });

    const bgLayer = new Layer({ id: "l_bg", type: "video", start: 0, duration: 10 });
    const textLayer = new Layer({ id: "l_text", type: "text", start: 2, duration: 4 });
    const ctaLayer = new Layer({ id: "l_cta", type: "shape", start: 6, duration: 4 });

    scene.addLayer(bgLayer).addLayer(textLayer).addLayer(ctaLayer);
    scene.addMarker({ id: "m1", name: "Hook Point", time: 1.5, type: "HOOK" });

    assert.strictEqual(scene.layerCount, 3);
    assert.strictEqual(scene.markers.length, 1);

    // En t = 3.0s -> activos bg y text
    const activeAt3 = scene.getActiveLayers(3.0);
    assert.strictEqual(activeAt3.length, 2);
    assert.strictEqual(activeAt3.some((l) => l.id === "l_bg"), true);
    assert.strictEqual(activeAt3.some((l) => l.id === "l_text"), true);

    // En t = 7.0s -> activos bg y cta
    const activeAt7 = scene.getActiveLayers(7.0);
    assert.strictEqual(activeAt7.length, 2);
    assert.strictEqual(activeAt7.some((l) => l.id === "l_cta"), true);
  });
});

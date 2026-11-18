import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { Layer } from "../../scene/core/Layer.js";
import { Scene } from "../../scene/core/Scene.js";

describe("Fase 5H — Scene & Layer Serialization Tests", () => {
  it("serializes and deserializes Scene with Camera, Layers and Markers cleanly", () => {
    const scene = new Scene({
      id: "scene_save",
      duration: 15.0,
      width: 1080,
      height: 1920,
      camera: {
        position: { x: 0, y: 100, z: 0 },
        rotation: { x: 0, y: 0, z: 5 },
        zoom: 1.1,
      },
      markers: [{ id: "m1", name: "Punchline", time: 4.5, type: "PUNCHLINE" }],
      layers: [
        new Layer({
          id: "layer_text",
          type: "text",
          start: 1.0,
          duration: 5.0,
          blendMode: "screen",
          opacity: 0.9,
        }),
      ],
    });

    const json = scene.toJSON();
    const reconstructed = Scene.fromJSON(json);

    assert.strictEqual(reconstructed.id, "scene_save");
    assert.strictEqual(reconstructed.camera?.zoom, 1.1);
    assert.strictEqual(reconstructed.markers[0].type, "PUNCHLINE");
    assert.strictEqual(reconstructed.layerCount, 1);
    assert.strictEqual(reconstructed.layers[0].blendMode, "screen");
  });
});

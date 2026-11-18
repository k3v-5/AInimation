import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { Scene } from "../../scenes/core/Scene.js";

describe("Fase 5C — Scene Serialization & Round-Trip Tests", () => {
  it("serializes and deserializes Scene with metadata and markers cleanly", () => {
    const original = new Scene({
      id: "scene_cta",
      duration: 8.0,
      metadata: {
        name: "Call to Action",
        semanticRole: "cta",
        tags: ["subscribe", "like"],
      },
    });
    original.addMarker({ id: "m_subscribe", time: 3.0, label: "Button Appear" });

    const json = original.toJSON();
    const reconstructed = Scene.fromJSON(json);

    assert.strictEqual(reconstructed.id, "scene_cta");
    assert.strictEqual(reconstructed.duration, 8.0);
    assert.strictEqual(reconstructed.metadata.semanticRole, "cta");
    assert.strictEqual(reconstructed.markers.length, 1);
    assert.strictEqual(reconstructed.markers[0].label, "Button Appear");

    const evalOrig = original.evaluate(3.0);
    const evalRecon = reconstructed.evaluate(3.0);
    assert.deepStrictEqual(evalRecon, evalOrig);
  });
});

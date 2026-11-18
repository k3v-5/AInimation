import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { Scene } from "../../scenes/core/Scene.js";

describe("Fase 5C — Scene Model & Semantic Roles Tests", () => {
  it("initializes scene with duration, semantic role and active interval [0, duration)", () => {
    const scene = new Scene({
      id: "scene_hook",
      duration: 5.0,
      metadata: {
        name: "Viral Hook",
        semanticRole: "hook",
        tags: ["high-energy", "intro"],
      },
    });

    assert.strictEqual(scene.id, "scene_hook");
    assert.strictEqual(scene.duration, 5.0);
    assert.strictEqual(scene.metadata.semanticRole, "hook");

    assert.strictEqual(scene.isActive(0.0), true);
    assert.strictEqual(scene.isActive(4.999), true);
    assert.strictEqual(scene.isActive(5.0), false);
    assert.strictEqual(scene.isActive(-0.1), false);
  });

  it("evaluates scene elements and metadata deterministically at local time", () => {
    const scene = new Scene({
      id: "scene_01",
      duration: 10.0,
      metadata: { semanticRole: "explanation" },
    });

    scene.addMarker({ id: "m1", time: 2.5, label: "Keyword Pop" });
    assert.strictEqual(scene.markers.length, 1);

    const evaluated = scene.evaluate(2.5);
    assert.strictEqual(evaluated.id, "scene_01");
    assert.strictEqual(evaluated.localTime, 2.5);
    assert.strictEqual(evaluated.active, true);
    assert.strictEqual(evaluated.metadata?.semanticRole, "explanation");
  });
});

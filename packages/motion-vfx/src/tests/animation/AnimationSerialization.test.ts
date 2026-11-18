import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AnimationSerializer } from "../../animation/AnimationSerializer.js";
import { basic, parallel, sequence } from "../../animation/helpers.js";

describe("Fase 3A — Animation Serialization & Round-Trip Tests", () => {
  it("serializes and deserializes a complex nested animation tree with exact evaluation parity", () => {
    const tree = parallel(
      basic({
        id: "fade_node",
        target: { elementId: "headline", propertyPath: "transform.opacity" },
        from: 0,
        to: 1,
        duration: 1.0,
        easing: "easeOut",
      }),
      sequence(
        basic({
          id: "pos_step_1",
          target: { elementId: "headline", propertyPath: "transform.position" },
          from: { x: -500, y: 0 },
          to: { x: 0, y: 0 },
          duration: 1.0,
          easing: "easeOut",
        }),
        basic({
          id: "pos_step_2",
          target: { elementId: "headline", propertyPath: "transform.scale" },
          from: { x: 0.8, y: 0.8 },
          to: { x: 1.0, y: 1.0 },
          duration: 0.5,
          easing: "easeInOut",
        })
      )
    );

    // 1. Serializar
    const json = AnimationSerializer.serialize(tree);
    assert.strictEqual(json.type, "parallel");

    // 2. Deserializar
    const restoredTree = AnimationSerializer.deserialize(json);
    assert.strictEqual(restoredTree.duration, tree.duration);

    // 3. Comprobar igualdad determinista en múltiples puntos temporales
    const timestamps = [0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0];
    for (const t of timestamps) {
      const origResult = tree.evaluate(t).getAll();
      const restResult = restoredTree.evaluate(t).getAll();
      assert.deepStrictEqual(restResult, origResult, `Mismatch at time t=${t}`);
    }
  });
});

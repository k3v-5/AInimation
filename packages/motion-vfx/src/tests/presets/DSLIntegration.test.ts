import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { compileDSL } from "../../animation/dsl/index.js";
import { ParallelAnimation } from "../../animation/ParallelAnimation.js";
import "../../presets/index.js";

describe("Fase 4A — DSL Integration with Preset System Tests", () => {
  it("compiles DSL preset node into expanded AnimationNode tree", () => {
    const dsl = {
      version: 1 as const,
      animations: [
        {
          type: "preset" as const,
          name: "popIn",
          target: "banner_title",
          overrides: {
            duration: 0.75,
            intensity: 0.9,
          },
        },
      ],
    };

    const ir = compileDSL(dsl);

    assert.strictEqual(ir.rootNodes.length, 1);
    const node = ir.rootNodes[0];
    assert.ok(node instanceof ParallelAnimation);
    assert.strictEqual(node.duration, 0.75);

    // En t = 0.75s -> opacity = 1.0, scale = (1.0, 1.0)
    const atEnd = node.evaluate(0.75);
    assert.strictEqual(atEnd.get({ elementId: "banner_title", propertyPath: "transform.opacity" }), 1.0);
    assert.deepStrictEqual(atEnd.get({ elementId: "banner_title", propertyPath: "transform.scale" }), { x: 1.0, y: 1.0 });
  });
});

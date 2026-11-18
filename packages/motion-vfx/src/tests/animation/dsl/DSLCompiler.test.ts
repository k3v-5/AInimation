import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { DSLCompiler } from "../../../animation/dsl/compiler/DSLCompiler.js";
import { SequenceAnimation } from "../../../animation/SequenceAnimation.js";

describe("Fase 3E — DSL Compiler & IR Generation Tests", () => {
  it("compiles declarative JSON into validated AnimationIR and AnimationNode tree", () => {
    const dsl = {
      version: 1 as const,
      variables: {
        inDur: 0.5,
        holdDur: 1.0,
      },
      animations: [
        {
          type: "sequence" as const,
          children: [
            {
              type: "parallel" as const,
              children: [
                {
                  type: "slideIn" as const,
                  target: "hero_title",
                  direction: "up" as const,
                  distance: 80,
                  duration: "$inDur",
                  motion: "spring",
                },
                {
                  type: "fadeIn" as const,
                  target: "hero_title",
                  duration: "$inDur",
                },
              ],
            },
            {
              type: "hold" as const,
              duration: "$holdDur",
            },
            {
              type: "fadeOut" as const,
              target: "hero_title",
              duration: 0.4,
            },
          ],
        },
      ],
    };

    const ir = DSLCompiler.compile(dsl);

    assert.strictEqual(ir.version, 1);
    assert.strictEqual(ir.rootNodes.length, 1);
    assert.ok(ir.rootNodes[0] instanceof SequenceAnimation);

    // Metadata
    assert.deepStrictEqual(ir.metadata.targets, ["hero_title"]);
    // Total duration = 0.5 (in) + 1.0 (hold) + 0.4 (out) = 1.9s
    assert.strictEqual(ir.metadata.totalDuration, 1.9);
  });
});

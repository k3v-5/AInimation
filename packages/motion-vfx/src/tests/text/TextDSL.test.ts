import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { compileDSL } from "../../animation/dsl/index.js";
import { ParallelAnimation } from "../../animation/ParallelAnimation.js";

describe("Fase 4B — Text Animation DSL Integration Tests", () => {
  it("compiles textAnimation node in DSL to validated AnimationIR", () => {
    const dsl = {
      version: 1 as const,
      variables: {
        slideDist: 60,
      },
      animations: [
        {
          type: "textAnimation" as const,
          target: "intro_title",
          text: "HELLO",
          scope: "character" as const,
          order: "forward" as const,
          stagger: 0.05,
          animation: {
            type: "slideIn" as const,
            target: "intro_title",
            direction: "up" as const,
            distance: "$slideDist",
            duration: 0.4,
          },
        },
      ],
    };

    const ir = compileDSL(dsl);
    assert.strictEqual(ir.rootNodes.length, 1);
    const root = ir.rootNodes[0];
    assert.ok(root instanceof ParallelAnimation);
    // 5 caracteres ("H", "E", "L", "L", "O")
    assert.strictEqual(root.children.length, 5);
  });
});

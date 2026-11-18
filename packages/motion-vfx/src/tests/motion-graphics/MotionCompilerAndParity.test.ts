import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { MotionCompiler } from "../../motion-graphics/core/MotionCompiler.js";

describe("Fase 11 — Motion Compiler & Audio Reactive Tests", () => {
  it("compiles a high-level motion macro into coordinated elements with text staggers", () => {
    const compiled = MotionCompiler.compileMacro("high-impact-hook", {
      text: "NUNCA HAGAS ESTO",
      accentWord: "ESTO",
    });

    assert.strictEqual(compiled.compiledElements.length, 3);
    const textElem = compiled.compiledElements.find((e) => e.type === "kinetic_text");
    assert.strictEqual(textElem !== undefined, true);
    assert.strictEqual(textElem.segments.length, 3);
    assert.strictEqual(textElem.segments[2].text, "ESTO");
    assert.strictEqual(textElem.segments[2].isEmphasized, true);
  });

  it("calculates audio-reactive scale boosts based on audio amplitude", () => {
    const baseScale = 1.0;
    const scaled = MotionCompiler.evaluateAudioReactiveScale(baseScale, 0.8, 0.5);
    // 1.0 + 0.8 * 0.5 = 1.4
    assert.strictEqual(Math.abs(scaled - 1.4) < 1e-6, true);
  });
});

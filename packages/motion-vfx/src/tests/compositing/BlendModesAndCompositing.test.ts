import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { BlendMath, PixelRGBA } from "../../compositing/index.js";

describe("Fase 5H — Blend Modes & Compositing Math Tests", () => {
  it("blends pixels with standard Porter-Duff and blend mode operations", () => {
    const bottom: PixelRGBA = { r: 0.5, g: 0.5, b: 0.5, a: 1.0 };
    const top: PixelRGBA = { r: 1.0, g: 1.0, b: 1.0, a: 0.5 };

    // Normal blend
    const normal = BlendMath.blendPixels(bottom, top, "normal");
    assert.strictEqual(normal.a, 1.0);
    assert.strictEqual(normal.r, 0.75); // 1.0 * 0.5 + 0.5 * 0.5 = 0.75

    // Multiply: channel = 0.5 * 1.0 = 0.5 -> composited = 0.5 * 0.5 + 0.5 * 0.5 = 0.5
    const multiply = BlendMath.blendPixels(bottom, top, "multiply");
    assert.strictEqual(multiply.r, 0.5);

    // Screen: channel = 0.5 + 1.0 - 0.5 = 1.0 -> composited = 1.0 * 0.5 + 0.5 * 0.5 = 0.75
    const screen = BlendMath.blendPixels(bottom, top, "screen");
    assert.strictEqual(screen.r, 0.75);

    // Add: channel = min(1.0, 0.5 + 1.0) = 1.0
    const add = BlendMath.blendPixels(bottom, top, "add");
    assert.strictEqual(add.r, 0.75);
  });
});

import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { DropShadow } from "../../effects/glow/DropShadow.js";
import { Glow } from "../../effects/glow/Glow.js";
import { Outline } from "../../effects/stylize/Outline.js";

describe("Fase 4C — Builtin Effects Pipeline Tests", () => {
  it("evaluates Glow with radius, intensity, threshold and color", () => {
    const glow = new Glow({ radius: 30, intensity: 1.5, threshold: 0.4 });
    const ev = glow.evaluate(0);

    assert.strictEqual(ev.type, "glow");
    assert.strictEqual(ev.params.radius, 30);
    assert.strictEqual(ev.params.intensity, 1.5);
    assert.strictEqual(ev.params.threshold, 0.4);
  });

  it("evaluates DropShadow with offsets, blur, opacity and color", () => {
    const shadow = new DropShadow({ offsetX: 8, offsetY: 12, blur: 15, opacity: 0.75 });
    const ev = shadow.evaluate(0);

    assert.strictEqual(ev.type, "dropShadow");
    assert.strictEqual(ev.params.offsetX, 8);
    assert.strictEqual(ev.params.offsetY, 12);
    assert.strictEqual(ev.params.blur, 15);
    assert.strictEqual(ev.params.opacity, 0.75);
  });

  it("evaluates Outline with stroke width, opacity and color", () => {
    const outline = new Outline({ width: 4, opacity: 0.9 });
    const ev = outline.evaluate(0);

    assert.strictEqual(ev.type, "outline");
    assert.strictEqual(ev.params.width, 4);
    assert.strictEqual(ev.params.opacity, 0.9);
  });
});

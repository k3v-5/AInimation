import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { GaussianBlur } from "../../effects/blur/GaussianBlur.js";
import { Brightness } from "../../effects/color/Brightness.js";
import { Contrast } from "../../effects/color/Contrast.js";
import { EffectStack } from "../../effects/core/EffectStack.js";
import { DropShadow } from "../../effects/glow/DropShadow.js";
import { Glow } from "../../effects/glow/Glow.js";
import { Outline } from "../../effects/stylize/Outline.js";

describe("Fase 4C — Effect Stack Benchmark Suite", () => {
  it("benchmarks evaluating 10, 50 effects in stack across resolutions (720p, 1080p, 4K)", () => {
    const stack50 = new EffectStack();
    for (let i = 0; i < 10; i++) {
      stack50
        .add(new GaussianBlur({ amount: i * 2 }))
        .add(new Brightness({ amount: 1.1 }))
        .add(new Contrast({ amount: 1.2 }))
        .add(new Glow({ radius: 15 }))
        .add(new DropShadow({ blur: 10 }));
    }

    assert.strictEqual(stack50.length, 50);

    const resolutions = [
      { width: 1280, height: 720 },
      { width: 1920, height: 1080 },
      { width: 3840, height: 2160 },
    ];

    const iterations = 1000;
    const start = performance.now();

    for (const res of resolutions) {
      for (let i = 0; i < iterations; i++) {
        const ev = stack50.evaluate(i * 0.016, { time: i * 0.016, resolution: res });
        assert.strictEqual(ev.effects.length, 50);
      }
    }

    const elapsed = performance.now() - start;

    // Presupuesto: 3,000 evaluaciones completas de pilas de 50 efectos en < 1500ms
    assert.ok(
      elapsed < 1500,
      `Effect stack evaluation budget exceeded: took ${elapsed.toFixed(2)}ms for 3,000 evaluations of 50 effects`
    );
  });
});

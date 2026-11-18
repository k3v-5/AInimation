import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { GaussianBlur } from "../../effects/blur/GaussianBlur.js";
import { Brightness } from "../../effects/color/Brightness.js";
import { Contrast } from "../../effects/color/Contrast.js";
import { EffectStack } from "../../effects/core/EffectStack.js";

describe("Fase 4C — Effect Stack Execution Order & Isolation Tests", () => {
  it("preserves explicit array pipeline order across stack evaluation", () => {
    const stack = new EffectStack();
    const blur = new GaussianBlur({ amount: 15 });
    const bright = new Brightness({ amount: 1.2 });
    const contrast = new Contrast({ amount: 1.5 });

    stack.add(blur).add(bright).add(contrast);

    const evaluated = stack.evaluate(0);
    assert.strictEqual(evaluated.effects.length, 3);
    assert.strictEqual(evaluated.effects[0].type, "blur");
    assert.strictEqual(evaluated.effects[1].type, "brightness");
    assert.strictEqual(evaluated.effects[2].type, "contrast");
  });

  it("respects enabled: false and isolates disabled effects", () => {
    const stack = new EffectStack();
    const blur = new GaussianBlur({ amount: 20, enabled: false });
    const bright = new Brightness({ amount: 1.2, enabled: true });

    stack.add(blur).add(bright);

    const evaluated = stack.evaluate(0);
    assert.strictEqual(evaluated.effects[0].enabled, false);
    assert.strictEqual(evaluated.effects[1].enabled, true);
  });
});

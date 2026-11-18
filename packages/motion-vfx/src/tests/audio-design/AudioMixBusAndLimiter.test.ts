import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AudioMixBus } from "../../audio-design/core/AudioMixBus.js";

describe("Fase 13 — Audio Mix Bus & Limiter Tests", () => {
  it("sums multi-track buses with gain weighting and limits peaks against clipping", () => {
    const mixer = new AudioMixBus();
    mixer.setBusGain("voice", 1.0);
    mixer.setBusGain("music", 0.5);
    mixer.setBusGain("sfx", 0.5);

    // 1. Mezcla normal: 0.5 * 1.0 + 0.4 * 0.5 + 0.4 * 0.5 = 0.5 + 0.2 + 0.2 = 0.9
    const normalMix = mixer.mixAndLimit([
      { bus: "voice", rawLevel: 0.5 },
      { bus: "music", rawLevel: 0.4 },
      { bus: "sfx", rawLevel: 0.4 },
    ]);
    assert.strictEqual(Math.abs(normalMix.masterLevel - 0.9) < 1e-6, true);
    assert.strictEqual(normalMix.hasClipped, false);

    // 2. Mezcla saturada: 1.0 * 1.0 + 0.8 * 0.5 + 0.8 * 0.5 = 1.0 + 0.4 + 0.4 = 1.8 -> Limitado a 1.0
    const hotMix = mixer.mixAndLimit([
      { bus: "voice", rawLevel: 1.0 },
      { bus: "music", rawLevel: 0.8 },
      { bus: "sfx", rawLevel: 0.8 },
    ]);
    assert.strictEqual(hotMix.masterLevel, 1.0);
    assert.strictEqual(hotMix.hasClipped, true);
  });
});

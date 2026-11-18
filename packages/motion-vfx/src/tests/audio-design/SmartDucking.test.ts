import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { SmartDuckingEngine } from "../../audio-design/core/SmartDuckingEngine.js";
import { DuckingRule, SpeechRegion } from "../../audio-design/types/index.js";

describe("Fase 13 — Smart Ducking Tests", () => {
  const rule: DuckingRule = {
    voiceTrackId: "voice_01",
    musicTrackId: "music_01",
    duckedVolume: 0.2,
    normalVolume: 1.0,
    attackDuration: 0.2,
    releaseDuration: 0.4,
  };

  const speechRegions: SpeechRegion[] = [{ start: 2.0, end: 4.0, confidence: 0.95 }];

  it("calculates ducked volume during speech and normal volume outside", () => {
    // 1. Antes del ataque (t = 1.0s): volumen normal 1.0
    const gainBefore = SmartDuckingEngine.evaluateDuckingGain(speechRegions, rule, 1.0);
    assert.strictEqual(gainBefore, 1.0);

    // 2. Durante la voz activa (t = 3.0s): volumen atenuado 0.2
    const gainDuring = SmartDuckingEngine.evaluateDuckingGain(speechRegions, rule, 3.0);
    assert.strictEqual(gainDuring, 0.2);

    // 3. Mitad del ataque (t = 1.9s, 0.1s dentro del ataque de 0.2s): 1.0 - 0.8 * 0.5 = 0.6
    const gainAttack = SmartDuckingEngine.evaluateDuckingGain(speechRegions, rule, 1.9);
    assert.strictEqual(Math.abs(gainAttack - 0.6) < 1e-6, true);

    // 4. Mitad del release (t = 4.2s, 0.2s dentro del release de 0.4s): 0.2 + 0.8 * 0.5 = 0.6
    const gainRelease = SmartDuckingEngine.evaluateDuckingGain(speechRegions, rule, 4.2);
    assert.strictEqual(Math.abs(gainRelease - 0.6) < 1e-6, true);
  });
});

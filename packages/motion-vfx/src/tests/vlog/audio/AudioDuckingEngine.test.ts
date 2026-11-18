import assert from "node:assert/strict";
import { describe, it } from "node:test";
import fc from "fast-check";
import { AudioDuckingEngine } from "../../../vlog/audio/audio-ducking-engine.js";

describe("Milestone 7 — Audio Ducking Engine Suite", () => {
  it("generates attack, hold and release keyframes for isolated dialogue", () => {
    const dialogue = [{ startSeconds: 2.0, endSeconds: 5.0 }];
    const envelope = AudioDuckingEngine.generateDuckingEnvelope("music_01", "voice_01", dialogue, {
      duckAmountDb: -10.0,
      attackSeconds: 0.12,
      releaseSeconds: 0.40,
    });

    assert.equal(envelope.targetTrackId, "music_01");
    assert.equal(envelope.duckAmountDb, -10.0);
    assert.ok(envelope.keyframes.length >= 4);

    // Keyframes:
    // 0: t=0.0 -> 0dB
    // 1: t=1.88 (2.0 - 0.12) -> 0dB
    // 2: t=2.0 -> -10dB
    // 3: t=5.0 -> -10dB
    // 4: t=5.4 (5.0 + 0.40) -> 0dB
    const kf1 = envelope.keyframes.find((k) => Math.abs(k.timeSeconds - 1.88) < 0.01);
    const kf2 = envelope.keyframes.find((k) => Math.abs(k.timeSeconds - 2.0) < 0.01);
    const kf3 = envelope.keyframes.find((k) => Math.abs(k.timeSeconds - 5.0) < 0.01);
    const kf4 = envelope.keyframes.find((k) => Math.abs(k.timeSeconds - 5.4) < 0.01);

    assert.ok(kf1 !== undefined && kf1.gainDb === 0.0);
    assert.ok(kf2 !== undefined && kf2.gainDb === -10.0);
    assert.ok(kf3 !== undefined && kf3.gainDb === -10.0);
    assert.ok(kf4 !== undefined && kf4.gainDb === 0.0);
  });

  it("merges closely-spaced dialogue segments to prevent audio pumping", () => {
    // Dos frases separadas por solo 0.20s (menor al umbral minPause = 0.52s)
    const dialogue = [
      { startSeconds: 1.0, endSeconds: 3.0 },
      { startSeconds: 3.2, endSeconds: 5.0 }, // Pausa de 0.20s
    ];

    const envelope = AudioDuckingEngine.generateDuckingEnvelope("music_01", "voice_01", dialogue);

    // No debe haber keyframe intermedio que suba a 0dB entre 3.0s y 3.2s
    const pumpingKeyframe = envelope.keyframes.find(
      (k) => k.timeSeconds > 3.0 && k.timeSeconds < 3.2 && k.gainDb > -10.0
    );
    assert.equal(pumpingKeyframe, undefined);

    // La recuperación a 0dB ocurre recién después del segundo segmento (5.0 + 0.40 = 5.4s)
    const finalRecovery = envelope.keyframes.find((k) => Math.abs(k.timeSeconds - 5.4) < 0.02);
    assert.ok(finalRecovery !== undefined && finalRecovery.gainDb === 0.0);
  });

  it("handles empty dialogue cleanly returning constant 0dB envelope", () => {
    const envelope = AudioDuckingEngine.generateDuckingEnvelope("m", "v", []);
    assert.equal(envelope.keyframes.length, 1);
    assert.equal(envelope.keyframes[0].gainDb, 0.0);
  });

  it("PBT: keyframe timestamps are monotonically non-decreasing and gain within [-10, 0]", () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.record({
            start: fc.double({ min: 1.0, max: 20.0, noNaN: true }),
            dur: fc.double({ min: 0.5, max: 5.0, noNaN: true }),
          }),
          { minLength: 1, maxLength: 6 }
        ),
        (segments) => {
          const intervals = segments.map((s) => ({
            startSeconds: s.start,
            endSeconds: s.start + s.dur,
          }));

          const env = AudioDuckingEngine.generateDuckingEnvelope("m", "v", intervals, {
            duckAmountDb: -10.0,
          });

          for (let i = 0; i < env.keyframes.length; i++) {
            const kf = env.keyframes[i];
            assert.ok(kf.gainDb >= -10.0 && kf.gainDb <= 0.0);
            if (i > 0) {
              assert.ok(kf.timeSeconds >= env.keyframes[i - 1].timeSeconds);
            }
          }
        }
      )
    );
  });
});

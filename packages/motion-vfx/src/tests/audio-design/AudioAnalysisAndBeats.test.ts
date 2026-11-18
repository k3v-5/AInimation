import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AudioAnalysisEngine } from "../../audio-design/core/AudioAnalysisEngine.js";
import { SpeechRegion } from "../../audio-design/types/index.js";

describe("Fase 13 — Audio Analysis & Beat Grid Tests", () => {
  it("generates deterministic beat grid with downbeats at bar starts", () => {
    // 120 BPM = 0.5s por beat
    const beats = AudioAnalysisEngine.generateBeatGrid(120, 2.0);
    assert.strictEqual(beats.length, 4);

    assert.strictEqual(beats[0].time, 0.0);
    assert.strictEqual(beats[0].isDownbeat, true);
    assert.strictEqual(beats[0].strength, 1.0);

    assert.strictEqual(beats[1].time, 0.5);
    assert.strictEqual(beats[1].isDownbeat, false);
    assert.strictEqual(beats[1].strength, 0.7);
  });

  it("detects silence intervals between active speech regions", () => {
    const speechRegions: SpeechRegion[] = [
      { start: 1.0, end: 3.0, confidence: 0.95 },
      { start: 5.0, end: 8.0, confidence: 0.95 },
    ];

    const silences = AudioAnalysisEngine.detectSilenceRegions(speechRegions, 10.0, 0.5);
    assert.strictEqual(silences.length, 3);
    assert.deepStrictEqual(silences[0], { start: 0, end: 1.0 });
    assert.deepStrictEqual(silences[1], { start: 3.0, end: 5.0 });
    assert.deepStrictEqual(silences[2], { start: 8.0, end: 10.0 });
  });
});

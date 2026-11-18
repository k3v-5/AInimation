import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AudioAnalyzer } from "../../audio/analysis/AudioAnalyzer.js";
import { AudioBuffer } from "../../audio/core/AudioBuffer.js";
import { SyntheticAudioSource } from "../../audio/core/AudioSource.js";
import { TimeRange } from "../../timeline/core/TimeRange.js";

describe("Fase 5D — Audio Analysis (RMS, Peaks, Silence & Beat Detection) Tests", () => {
  it("calculates RMS energy and peak amplitude on pure sine wave precisely", () => {
    const src = new SyntheticAudioSource({ type: "sine", duration: 1.0, frequency: 100, amplitude: 0.8 });
    const buffer = src.read(new TimeRange(0, 1.0));

    const peak = AudioAnalyzer.calculatePeak(buffer);
    const rms = AudioAnalyzer.calculateRMS(buffer);

    // Peak debe ser ~0.8
    assert.ok(Math.abs(peak - 0.8) < 1e-3);
    // RMS de seno con amplitud A es A / sqrt(2) = 0.8 / 1.4142 ~= 0.5656
    assert.ok(Math.abs(rms - 0.5656) < 1e-2);
  });

  it("generates waveform points downsampled for timeline display", () => {
    const src = new SyntheticAudioSource({ type: "sine", duration: 2.0, frequency: 440 });
    const buffer = src.read(new TimeRange(0, 2.0));

    const waveform = AudioAnalyzer.generateWaveform(buffer, 50);
    assert.strictEqual(waveform.length, 50);
    assert.ok(waveform[0].max > 0);
    assert.ok(waveform[0].min < 0);
  });

  it("detects silence intervals accurately", () => {
    // 3 segundos: 1s sonido + 1s silencio + 1s sonido
    const buffer = AudioBuffer.create(1, 48000 * 3, 48000);
    // Llenar seg 0-1 con sonido
    for (let i = 0; i < 48000; i++) buffer.data[0][i] = 0.5 * Math.sin((i / 48000) * 100);
    // seg 1-2 silencio (0)
    // Llenar seg 2-3 con sonido
    for (let i = 48000 * 2; i < 48000 * 3; i++) buffer.data[0][i] = 0.5 * Math.sin((i / 48000) * 100);

    const silence = AudioAnalyzer.detectSilence(buffer, -40, 0.5);
    assert.strictEqual(silence.length, 1);
    assert.ok(silence[0].start >= 0.95 && silence[0].start <= 1.05);
    assert.ok(silence[0].end >= 1.95 && silence[0].end <= 2.05);
  });

  it("detects beats and estimates BPM from rhythmic click pulses", () => {
    // Clicks cada 0.5 segundos -> 120 BPM
    const src = new SyntheticAudioSource({ type: "clicks", duration: 4.0, clickInterval: 0.5, amplitude: 0.9 });
    const buffer = src.read(new TimeRange(0, 4.0));

    const beatMap = AudioAnalyzer.detectBeats(buffer, { windowSizeMs: 10, sensitivity: 1.5 });
    assert.ok(beatMap.beats.length >= 6);
    assert.ok(beatMap.bpm !== undefined);
    assert.ok(Math.abs(beatMap.bpm! - 120) <= 5); // BPM estimado ~120
  });
});

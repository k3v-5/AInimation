import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AudioAnalyzer } from "../../audio/analysis/AudioAnalyzer.js";
import { AudioClip } from "../../audio/core/AudioClip.js";
import { SyntheticAudioSource } from "../../audio/core/AudioSource.js";
import { AudioTrack } from "../../audio/core/AudioTrack.js";
import { AudioMixer } from "../../audio/mixer/AudioMixer.js";
import { TimeRange } from "../../timeline/core/TimeRange.js";

describe("Fase 5D — Audio Mixing & Analysis Performance Benchmark Suite", () => {
  it("benchmarks mixing 50 audio clips and analyzing waveform", () => {
    const mixer = new AudioMixer({ sampleRate: 48000, channels: 2 });
    const track = new AudioTrack({ id: "bench_track" });

    const sources = new Map<string, SyntheticAudioSource>();
    const count = 50;

    for (let i = 0; i < count; i++) {
      const id = `snd_${i}`;
      sources.set(id, new SyntheticAudioSource({ type: "sine", duration: 5.0, frequency: 200 + i * 10, amplitude: 0.1 }));
      track.addClip(new AudioClip({ id: `clip_${i}`, assetId: id, timelineRange: new TimeRange(i * 0.5, i * 0.5 + 4.0) }));
    }

    const t0 = performance.now();
    const mixed = mixer.mix([track], new TimeRange(0, 10.0), (id) => sources.get(id));
    const mixElapsed = performance.now() - t0;

    assert.strictEqual(mixed.duration, 10.0);
    assert.strictEqual(mixed.frames, 480000);

    // Medir análisis de waveform y beats
    const t1 = performance.now();
    const waveform = AudioAnalyzer.generateWaveform(mixed, 200);
    const beatMap = AudioAnalyzer.detectBeats(mixed);
    const analysisElapsed = performance.now() - t1;

    assert.strictEqual(waveform.length, 200);
    assert.ok(beatMap.beats.length >= 0);

    // Presupuesto: Mezcla de 10s con 50 clips en < 500ms y análisis en < 500ms
    assert.ok(mixElapsed < 500, `Audio mix took ${mixElapsed.toFixed(2)}ms (budget: <500ms)`);
    assert.ok(analysisElapsed < 500, `Audio analysis took ${analysisElapsed.toFixed(2)}ms (budget: <500ms)`);
  });
});

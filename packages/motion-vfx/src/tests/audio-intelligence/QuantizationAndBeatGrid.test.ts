import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { Quantizer } from "../../audio-intelligence/core/Quantizer.js";
import { Beat, BeatGrid } from "../../audio-intelligence/types/index.js";

describe("Fase 5I — Beat Grid Quantization & Musical Bar Snapping Tests", () => {
  it("snaps continuous timestamps to nearest beat, bar and subdivisions at 120 BPM", () => {
    // 120 BPM -> 0.5s por beat, 2.0s por compás (4/4)
    const grid: BeatGrid = {
      bpm: 120,
      offset: 0.0,
      subdivision: 2, // Corcheas (1/8 -> 0.25s)
    };

    // t = 0.48s ajustado a 'beat' -> 0.50s
    assert.strictEqual(Quantizer.snap(0.48, grid, "beat"), 0.5);

    // t = 0.23s ajustado a 'subdivision' -> 0.25s
    assert.strictEqual(Quantizer.snap(0.23, grid, "subdivision"), 0.25);

    // t = 1.85s ajustado a 'bar' -> 2.0s
    assert.strictEqual(Quantizer.snap(1.85, grid, "bar"), 2.0);
  });

  it("groups sequence of beats into musical bars of 4 beats", () => {
    const beats: Beat[] = [
      { time: 0.0, strength: 1.0 },
      { time: 0.5, strength: 0.5 },
      { time: 1.0, strength: 0.7 },
      { time: 1.5, strength: 0.5 },
      { time: 2.0, strength: 1.0 },
      { time: 2.5, strength: 0.5 },
      { time: 3.0, strength: 0.7 },
      { time: 3.5, strength: 0.5 },
    ];

    const bars = Quantizer.createMusicalBars(beats, 4);
    assert.strictEqual(bars.length, 2);
    assert.strictEqual(bars[0].start, 0.0);
    assert.strictEqual(bars[0].end, 2.0);
    assert.strictEqual(bars[0].beats.length, 4);
    assert.strictEqual(bars[1].start, 2.0);
  });
});

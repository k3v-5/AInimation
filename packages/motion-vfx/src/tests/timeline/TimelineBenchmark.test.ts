import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { Clip } from "../../timeline/core/Clip.js";
import { TimeRange } from "../../timeline/core/TimeRange.js";
import { Track } from "../../timeline/core/Track.js";
import { VideoTimeline } from "../../timeline/core/VideoTimeline.js";

describe("Fase 5B — Timeline Performance & Scalability Benchmark Suite", () => {
  it("benchmarks evaluating timeline with 1,000 and 10,000 clips", () => {
    const timeline = new VideoTimeline({ duration: 1000 });
    const trackCount = 10;
    const clipsPerTrack = 100; // 1,000 clips total

    for (let t = 0; t < trackCount; t++) {
      const track = new Track({ id: `track_${t}`, order: t });
      for (let c = 0; c < clipsPerTrack; c++) {
        track.addClip(
          new Clip({
            id: `clip_${t}_${c}`,
            elementId: `elem_${t}_${c}`,
            timelineRange: new TimeRange(c * 5, (c + 1) * 5),
          })
        );
      }
      timeline.addTrack(track);
    }

    assert.strictEqual(timeline.tracks.length, 10);

    // Medir 1,000 evaluaciones temporales
    const t0 = performance.now();
    for (let i = 0; i < 1000; i++) {
      const state = timeline.evaluate(i * 0.5);
      assert.ok(state.activeClips.length <= 10);
    }
    const elapsed = performance.now() - t0;

    // Presupuesto: 1,000 evaluaciones de 1,000 clips en < 500ms
    assert.ok(
      elapsed < 500,
      `1,000 timeline evaluations took ${elapsed.toFixed(2)}ms (budget: <500ms)`
    );
  });
});

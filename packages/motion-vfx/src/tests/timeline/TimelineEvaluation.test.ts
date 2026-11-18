import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { Clip } from "../../timeline/core/Clip.js";
import { TimeRange } from "../../timeline/core/TimeRange.js";
import { Track } from "../../timeline/core/Track.js";
import { VideoTimeline } from "../../timeline/core/VideoTimeline.js";

describe("Fase 5B — Multi-Track Timeline Evaluation Tests", () => {
  it("evaluates active clips cleanly across multiple tracks and timepoints", () => {
    const timeline = new VideoTimeline({ duration: 30, timeBase: { fps: 30 } });

    const track1 = new Track({ id: "t1", name: "Background", order: 0 });
    const track2 = new Track({ id: "t2", name: "Titles", order: 10 });

    track1.addClip(new Clip({ id: "bg_clip", elementId: "bg_elem", timelineRange: new TimeRange(0, 20) }));
    track2.addClip(new Clip({ id: "title_clip", elementId: "text_elem", timelineRange: new TimeRange(5, 10) }));

    timeline.addTrack(track1).addTrack(track2);

    // En t = 2.0s -> solo bg_clip está activo
    const stateAt2 = timeline.evaluate(2.0);
    assert.strictEqual(stateAt2.activeClips.length, 1);
    assert.strictEqual(stateAt2.activeClips[0].clipId, "bg_clip");
    assert.strictEqual(stateAt2.activeClips[0].localTime, 2.0);

    // En t = 7.5s -> tanto bg_clip como title_clip están activos
    const stateAt75 = timeline.evaluate(7.5);
    assert.strictEqual(stateAt75.activeClips.length, 2);
    assert.strictEqual(stateAt75.activeClips[0].clipId, "bg_clip");
    assert.strictEqual(stateAt75.activeClips[1].clipId, "title_clip");
    assert.strictEqual(stateAt75.activeClips[1].localTime, 2.5); // 7.5 - 5.0

    // En t = 25.0s -> ninguno activo
    const stateAt25 = timeline.evaluate(25.0);
    assert.strictEqual(stateAt25.activeClips.length, 0);
  });

  it("respects solo and mute track settings during evaluation", () => {
    const timeline = new VideoTimeline();
    const trackA = new Track({ id: "ta", type: "audio", solo: true });
    const trackB = new Track({ id: "tb", type: "audio", solo: false });

    trackA.addClip(new Clip({ id: "ca", elementId: "ea", timelineRange: new TimeRange(0, 10) }));
    trackB.addClip(new Clip({ id: "cb", elementId: "eb", timelineRange: new TimeRange(0, 10) }));

    timeline.addTrack(trackA).addTrack(trackB);

    const state = timeline.evaluate(5.0);
    assert.strictEqual(state.activeClips.length, 1);
    assert.strictEqual(state.activeClips[0].clipId, "ca");
  });
});

import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { Clip } from "../../timeline/core/Clip.js";
import { TimeRange } from "../../timeline/core/TimeRange.js";
import { Track } from "../../timeline/core/Track.js";
import { VideoTimeline } from "../../timeline/core/VideoTimeline.js";

describe("Fase 5B — Timeline Serialization & Deserialization Tests", () => {
  it("serializes and deserializes multi-track VideoTimeline cleanly", () => {
    const original = new VideoTimeline({ duration: 60, timeBase: { fps: 60 } });
    const track = new Track({ id: "t_video", name: "Main Video", type: "video", order: 1 });
    track.addClip(
      new Clip({
        id: "c_hero",
        name: "Hero Clip",
        elementId: "hero_vid",
        timelineRange: new TimeRange(0, 15),
        sourceRange: new TimeRange(10, 25),
        speed: 1.0,
      })
    );

    original.addTrack(track);
    original.addMarker({ id: "m_beat1", time: 5.0, label: "Beat Drop", color: "#ff0000" });

    const json = original.toJSON();
    const reconstructed = VideoTimeline.fromJSON(json);

    assert.strictEqual(reconstructed.duration, 60);
    assert.strictEqual(reconstructed.timeBase.fps, 60);
    assert.strictEqual(reconstructed.tracks.length, 1);
    assert.strictEqual(reconstructed.tracks[0].clips.length, 1);
    assert.strictEqual(reconstructed.tracks[0].clips[0].id, "c_hero");
    assert.strictEqual(reconstructed.markers.length, 1);
    assert.strictEqual(reconstructed.markers[0].label, "Beat Drop");

    // Verificar igualdad de evaluación determinista
    const evalOrig = original.evaluate(7.5);
    const evalRecon = reconstructed.evaluate(7.5);
    assert.deepStrictEqual(evalRecon, evalOrig);
  });
});

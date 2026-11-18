import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AudioClip } from "../../audio/core/AudioClip.js";
import { AudioTrack } from "../../audio/core/AudioTrack.js";
import { TimeRange } from "../../timeline/core/TimeRange.js";

describe("Fase 5D — Audio Serialization & Round-Trip Tests", () => {
  it("serializes and deserializes AudioClip and AudioTrack with ducking settings cleanly", () => {
    const originalTrack = new AudioTrack({
      id: "track_music",
      name: "Music Track",
      gainDb: -2.5,
      pan: 0.2,
      ducking: {
        sourceTrackId: "track_voice",
        attenuationDb: -8.0,
        thresholdRms: 0.15,
      },
    });

    const clip = new AudioClip({
      id: "clip_m1",
      assetId: "music_wav",
      timelineRange: new TimeRange(0, 30),
      sourceRange: new TimeRange(10, 40),
      speed: 1.0,
      gainDb: -3.0,
      fadeIn: { duration: 1.5, easing: "easeInOut" },
    });

    originalTrack.addClip(clip);

    const json = originalTrack.toJSON();
    const reconstructed = AudioTrack.fromJSON(json);

    assert.strictEqual(reconstructed.id, "track_music");
    assert.strictEqual(reconstructed.gainDb, -2.5);
    assert.strictEqual(reconstructed.pan, 0.2);
    assert.strictEqual(reconstructed.ducking?.attenuationDb, -8.0);
    assert.strictEqual(reconstructed.clips.length, 1);
    assert.strictEqual(reconstructed.clips[0].id, "clip_m1");
    assert.strictEqual(reconstructed.clips[0].fadeIn?.duration, 1.5);
  });
});

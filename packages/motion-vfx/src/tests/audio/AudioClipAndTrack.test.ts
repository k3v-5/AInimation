import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AudioClip } from "../../audio/core/AudioClip.js";
import { AudioTrack } from "../../audio/core/AudioTrack.js";
import { TimeRange } from "../../timeline/core/TimeRange.js";

describe("Fase 5D — AudioClip, Fades & AudioTrack Tests", () => {
  it("calculates clip gain across fadeIn and fadeOut easing curves", () => {
    const clip = new AudioClip({
      id: "aclip_01",
      assetId: "bg_music",
      timelineRange: new TimeRange(0, 10),
      volume: 1.0,
      fadeIn: { duration: 2.0, easing: "linear" },
      fadeOut: { duration: 2.0, easing: "linear" },
    });

    // En localTime = 0.0s -> inicio de fade-in -> ganancia = 0.0
    assert.strictEqual(clip.getGainAtTime(0.0), 0.0);

    // En localTime = 1.0s -> mitad de fade-in -> ganancia = 0.5
    assert.strictEqual(clip.getGainAtTime(1.0), 0.5);

    // En localTime = 5.0s -> zona plana -> ganancia = 1.0
    assert.strictEqual(clip.getGainAtTime(5.0), 1.0);

    // En localTime = 9.0s -> mitad de fade-out (queda 1s de 2s) -> ganancia = 0.5
    assert.strictEqual(clip.getGainAtTime(9.0), 0.5);

    // En localTime = 10.0s -> fin -> 0.0
    assert.strictEqual(clip.getGainAtTime(10.0), 0.0);
  });

  it("manages audio track active clips and solo/mute states", () => {
    const track = new AudioTrack({ id: "track_music", gainDb: -3.0 });
    const clip1 = new AudioClip({ id: "c1", assetId: "m1", timelineRange: new TimeRange(0, 5) });
    const clip2 = new AudioClip({ id: "c2", assetId: "m2", timelineRange: new TimeRange(5, 10) });

    track.addClip(clip1).addClip(clip2);
    assert.strictEqual(track.size, 2);

    // Activo en t = 2s -> c1
    const activeAt2 = track.getActiveClips(2.0);
    assert.strictEqual(activeAt2.length, 1);
    assert.strictEqual(activeAt2[0].id, "c1");

    // Muted -> no retorna clips activos
    track.muted = true;
    assert.strictEqual(track.getActiveClips(2.0).length, 0);
  });
});

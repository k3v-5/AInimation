import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { ValidationError } from "../../errors/index.js";
import { Clip } from "../../timeline/core/Clip.js";
import { TimeRange } from "../../timeline/core/TimeRange.js";
import { Track } from "../../timeline/core/Track.js";

describe("Fase 5B — Track Operations & NLE Edits Tests", () => {
  it("adds, retrieves, moves, trims, and splits clips in track", () => {
    const track = new Track({ id: "track_v1", type: "video" });
    const clip1 = new Clip({ id: "c1", elementId: "e1", timelineRange: new TimeRange(0, 5) });
    const clip2 = new Clip({ id: "c2", elementId: "e2", timelineRange: new TimeRange(5, 10) });

    track.addClip(clip1).addClip(clip2);
    assert.strictEqual(track.size, 2);

    // Mover c1 a [10, 15)
    track.moveClip("c1", 10);
    assert.strictEqual(track.getClip("c1")?.timelineRange.start, 10);
    assert.strictEqual(track.getClip("c1")?.timelineRange.end, 15);

    // Recortar c2 a [6, 9)
    track.trimClip("c2", 6, 9);
    assert.strictEqual(track.getClip("c2")?.timelineRange.start, 6);
    assert.strictEqual(track.getClip("c2")?.timelineRange.end, 9);

    // Dividir c1 (10-15) en 12 -> [10, 12) y [12, 15)
    const [p1, p2] = track.splitClip("c1", 12);
    assert.strictEqual(p1.timelineRange.duration, 2);
    assert.strictEqual(p2.timelineRange.duration, 3);
    assert.strictEqual(track.size, 3);
  });

  it("prevents modifying clips when track is locked", () => {
    const track = new Track({ id: "track_locked", locked: true });
    const clip = new Clip({ id: "c_lock", elementId: "e1", timelineRange: new TimeRange(0, 5) });

    assert.throws(() => track.addClip(clip), ValidationError);
  });
});

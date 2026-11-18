import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { Clip } from "../../timeline/core/Clip.js";
import { TimeRange } from "../../timeline/core/TimeRange.js";

describe("Fase 5B — Clip Operations & Source Mapping Tests", () => {
  it("calculates local and source times across playback speeds", () => {
    const clip = new Clip({
      id: "clip_01",
      elementId: "video_elem_1",
      timelineRange: new TimeRange(5.0, 15.0), // 10s duration
      sourceRange: new TimeRange(30.0, 50.0), // 20s source span
      speed: 2.0, // 2x playback speed
    });

    // En globalTime = 5.0 -> localTime = 0.0 -> sourceTime = 30.0
    assert.strictEqual(clip.getLocalTime(5.0), 0.0);
    assert.strictEqual(clip.getSourceTime(5.0), 30.0);

    // En globalTime = 7.5 -> localTime = 2.5 -> sourceTime = 30.0 + (2.5 * 2.0) = 35.0
    assert.strictEqual(clip.getLocalTime(7.5), 2.5);
    assert.strictEqual(clip.getSourceTime(7.5), 35.0);

    // En globalTime = 14.999 -> activo
    assert.strictEqual(clip.isActive(14.999), true);
    // En globalTime = 15.0 -> inactivo (end exclusive)
    assert.strictEqual(clip.isActive(15.0), false);
  });

  it("splits a clip accurately into two proportional sub-clips", () => {
    const clip = new Clip({
      id: "clip_main",
      elementId: "video_elem_1",
      timelineRange: new TimeRange(0.0, 10.0),
      sourceRange: new TimeRange(20.0, 30.0),
      speed: 1.0,
    });

    const [part1, part2] = clip.split(4.0);

    // Parte 1: timeline [0, 4), source [20, 24)
    assert.strictEqual(part1.timelineRange.start, 0.0);
    assert.strictEqual(part1.timelineRange.end, 4.0);
    assert.strictEqual(part1.sourceRange?.start, 20.0);
    assert.strictEqual(part1.sourceRange?.end, 24.0);

    // Parte 2: timeline [4, 10), source [24, 30)
    assert.strictEqual(part2.timelineRange.start, 4.0);
    assert.strictEqual(part2.timelineRange.end, 10.0);
    assert.strictEqual(part2.sourceRange?.start, 24.0);
    assert.strictEqual(part2.sourceRange?.end, 30.0);
  });
});

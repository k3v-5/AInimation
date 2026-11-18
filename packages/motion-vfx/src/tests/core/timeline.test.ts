import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { Timeline } from "../../core/timeline.js";
import { ValidationError } from "../../errors/index.js";

describe("Timeline", () => {
  it("converts frames to time and vice versa", () => {
    const timeline = new Timeline(30, 10);
    assert.strictEqual(timeline.timeToFrame(1), 30);
    assert.strictEqual(timeline.timeToFrame(1.5), 45);
    assert.strictEqual(timeline.frameToTime(45), 1.5);
    assert.strictEqual(timeline.frameToTime(30), 1);
    assert.strictEqual(timeline.totalFrames(), 300);
  });

  it("handles rounding for fractional frames", () => {
    const timeline = new Timeline(30, 5);
    // 1.333333 * 30 = 39.99999 -> 40
    assert.strictEqual(timeline.timeToFrame(1.3333333), 40);
  });

  it("validates constructor parameters", () => {
    assert.throws(() => new Timeline(0, 10), ValidationError);
    assert.throws(() => new Timeline(-30, 10), ValidationError);
    assert.throws(() => new Timeline(30, -5), ValidationError);
  });
});

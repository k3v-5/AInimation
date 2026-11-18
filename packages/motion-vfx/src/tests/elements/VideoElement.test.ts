import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { VideoElement } from "../../elements/VideoElement.js";

describe("Fase 2B — VideoElement Timing & Trim Tests", () => {
  it("calculates exact sourceTime offset for trimmed video clips", () => {
    // start = 5, duration = 10, sourceStart = 20
    const vid = new VideoElement({
      assetId: "main_video",
      startTime: 5,
      duration: 10,
      sourceStartTime: 20,
    });

    // En globalTime = 8:
    // localTime = 8 - 5 = 3
    // sourceTime = 20 + 3 = 23
    assert.strictEqual(vid.getLocalTime(8), 3);
    assert.strictEqual(vid.getSourceTime(8), 23);

    const evaluated = vid.evaluate(8);
    assert.strictEqual(evaluated.active, true);
    assert.strictEqual(evaluated.sourceTime, 23);
    assert.strictEqual(evaluated.localTime, 3);
  });
});

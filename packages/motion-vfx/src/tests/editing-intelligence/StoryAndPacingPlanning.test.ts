import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { StoryAndPacingPlanner } from "../../editing-intelligence/core/StoryAndPacingPlanner.js";

describe("Fase 14 — Story & Pacing Planning Tests", () => {
  it("plans shot durations according to pacing profile constraints", () => {
    const totalDuration = 10.0;

    // 1. Fast Social: 2.0s promedio -> 5 tomas de 2.0s
    const fastShots = StoryAndPacingPlanner.planShotDurations(totalDuration, "fast_social");
    assert.strictEqual(fastShots.length, 5);
    assert.strictEqual(fastShots[0], 2.0);

    // 2. Educational: 5.0s promedio -> 2 tomas de 5.0s
    const eduShots = StoryAndPacingPlanner.planShotDurations(totalDuration, "educational");
    assert.strictEqual(eduShots.length, 2);
    assert.strictEqual(eduShots[0], 5.0);
  });
});

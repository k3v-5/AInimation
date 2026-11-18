import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { FrameScheduler } from "../../rendering/scheduler/FrameScheduler.js";
import { RenderProgress } from "../../rendering/types/index.js";

describe("Fase 9 — Frame Scheduler & Subframe Sampling Tests", () => {
  it("calculates 5 subframe samples for motion blur accumulation", () => {
    const samples = FrameScheduler.calculateSubframeSamples(1.0, 30, 5, 180);
    assert.strictEqual(samples.length, 5);
    // El sample central debe ser exactamente frameTime (1.0)
    assert.strictEqual(samples[2], 1.0);
    // El primer sample es < 1.0 y el último > 1.0
    assert.ok(samples[0] < 1.0);
    assert.ok(samples[4] > 1.0);
  });

  it("iterates frames sequentially reporting progress callbacks", async () => {
    const progresses: RenderProgress[] = [];
    let frameCount = 0;

    for await (const _ of FrameScheduler.generateFrames(5, 30, 1920, 1080, (p) => progresses.push(p))) {
      frameCount++;
    }

    assert.strictEqual(frameCount, 5);
    assert.strictEqual(progresses.length, 5);
    assert.strictEqual(progresses[progresses.length - 1].percentage, 100);
  });
});

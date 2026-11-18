import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { TrackBindingEngine } from "../../tracking-rotoscopy/core/TrackBindingEngine.js";
import { Track } from "../../tracking-rotoscopy/types/index.js";

describe("Fase 12 — Track Binding & Smart Arrow Tests", () => {
  const sampleTrack: Track = {
    id: "track_phone",
    targetType: "object",
    start: 0,
    end: 2.0,
    confidence: 0.9,
    state: "active",
    samples: [{ time: 0, position: { x: 500, y: 500 }, confidence: 0.9 }],
  };

  it("calculates bound layer position applying relative offset", () => {
    const boundPos = TrackBindingEngine.calculateBoundPosition(sampleTrack, 0, {
      offset: { x: 50, y: -100 },
    });

    assert.strictEqual(boundPos !== undefined, true);
    assert.strictEqual(boundPos?.x, 550);
    assert.strictEqual(boundPos?.y, 400);
  });

  it("calculates smart arrow length and angle targeting the tracked object", () => {
    const arrow = TrackBindingEngine.calculateSmartArrow({ x: 100, y: 500 }, sampleTrack, 0);

    assert.strictEqual(arrow !== undefined, true);
    assert.strictEqual(arrow?.targetPos.x, 500);
    assert.strictEqual(arrow?.targetPos.y, 500);
    assert.strictEqual(arrow?.length, 400); // 500 - 100
    assert.strictEqual(arrow?.angleRadians, 0); // Horizontal hacia la derecha (0 rad)
  });
});

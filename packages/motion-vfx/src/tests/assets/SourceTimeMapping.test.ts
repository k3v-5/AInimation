import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { toCompositionTime, toSourceTime } from "../../assets/utils/timeMapping.js";
import { VideoElement } from "../../elements/VideoElement.js";

describe("Fase 5A — Source-Time Mapping & Playback Speed Tests", () => {
  it("calculates source time accurately with normal speed (1.0x)", () => {
    // 10s source start, compTime = 2.5s -> sourceTime = 12.5s
    assert.strictEqual(toSourceTime(2.5, 10, 1.0), 12.5);
    assert.strictEqual(toCompositionTime(12.5, 10, 1.0), 2.5);
  });

  it("calculates source time accurately with fast forward (2.0x) and slow motion (0.5x)", () => {
    // 2.0x speed: 3s comp -> 6s source advance
    assert.strictEqual(toSourceTime(3.0, 5.0, 2.0), 11.0);
    assert.strictEqual(toCompositionTime(11.0, 5.0, 2.0), 3.0);

    // 0.5x speed: 4s comp -> 2s source advance
    assert.strictEqual(toSourceTime(4.0, 10.0, 0.5), 12.0);
    assert.strictEqual(toCompositionTime(12.0, 10.0, 0.5), 4.0);
  });

  it("evaluates VideoElement sourceTime according to startTime, sourceStartTime, and speed", () => {
    const video = new VideoElement({
      assetId: "clip_01",
      startTime: 2.0, // starts at 2s in composition
      duration: 5.0,
      sourceStartTime: 10.0, // trimmed from 10s of source
      speed: 2.0, // 2x playback speed
    });

    // En t = 2.0 (localTime = 0s) -> sourceTime = 10.0s
    const stateAt2 = video.evaluate(2.0);
    assert.strictEqual(stateAt2.sourceTime, 10.0);

    // En t = 3.5 (localTime = 1.5s, 1.5 * 2 = 3s) -> sourceTime = 13.0s
    const stateAt35 = video.evaluate(3.5);
    assert.strictEqual(stateAt35.sourceTime, 13.0);
  });
});

import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AutoReframeEngine } from "../../camera/core/AutoReframeEngine.js";

describe("Camera & Compositing — AutoReframeEngine Tests", () => {
  it("computes horizontal 16:9 to vertical 9:16 cover scale and centering accurately", () => {
    const sourceDim = { width: 1920, height: 1080 };
    const targetDim = { width: 1080, height: 1920 };

    // Center focal point
    const centerReframe = AutoReframeEngine.computeFocalOffset(sourceDim, targetDim, [0.5, 0.5]);

    // Cover scale factor: max(1080/1920, 1920/1080) * 100 = (1920/1080)*100 = 177.78%
    assert.ok(Math.abs(centerReframe.scale[0] - 177.78) < 0.1);
    assert.equal(centerReframe.position[0], 540);
    assert.equal(centerReframe.position[1], 960);
  });

  it("shifts position X when subject is off-center while strictly clamping to prevent black edges", () => {
    const sourceDim = { width: 1920, height: 1080 };
    const targetDim = { width: 1080, height: 1920 };

    // Subject on far right: fx = 0.95
    const rightReframe = AutoReframeEngine.computeFocalOffset(sourceDim, targetDim, [0.95, 0.5]);

    // Scaled width = 1920 * (1920/1080) = 3413.33px
    // minX = 1080 - 3413.33/2 = -626.67px
    // maxX = 3413.33/2 = 1706.67px
    assert.ok(rightReframe.position[0] < 540, "Expected position X to pan left when subject is on right");
    assert.ok(rightReframe.position[0] >= -626.7, "Expected position X strictly clamped above minX");

    // Subject on far left: fx = 0.05
    const leftReframe = AutoReframeEngine.computeFocalOffset(sourceDim, targetDim, [0.05, 0.5]);
    assert.ok(leftReframe.position[0] > 540, "Expected position X to pan right when subject is on left");
    assert.ok(leftReframe.position[0] <= 1706.7, "Expected position X strictly clamped below maxX");
  });

  it("generates smoothed moving average keyframes across continuous saliency track", () => {
    const sourceDim = { width: 1920, height: 1080 };
    const targetDim = { width: 1080, height: 1920 };

    const track = [
      { time: 0.0, focalPoint: [0.5, 0.5] as [number, number], confidence: 0.9 },
      { time: 0.5, focalPoint: [0.7, 0.5] as [number, number], confidence: 0.9 },
      { time: 1.0, focalPoint: [0.3, 0.5] as [number, number], confidence: 0.9 },
      { time: 1.5, focalPoint: [0.5, 0.5] as [number, number], confidence: 0.9 },
    ];

    const keyframes = AutoReframeEngine.generateReframeKeyframes(track, sourceDim, targetDim, 3);
    assert.equal(keyframes.length, 4);
    assert.equal(keyframes[0].time, 0.0);
    assert.equal(keyframes[3].time, 1.5);
    assert.ok(keyframes[1].position[0] !== undefined);
  });
});

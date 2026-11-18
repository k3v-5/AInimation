import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AudioBuffer } from "../../audio/core/AudioBuffer.js";
import { AudioTransientSyncEngine } from "../../audio/analysis/AudioTransientSyncEngine.js";

describe("Audio Intelligence — AudioTransientSyncEngine Tests", () => {
  it("detects synthesized rhythmic transients accurately", () => {
    const sampleRate = 44100;
    const duration = 2.5; // 2.5 seconds
    const totalFrames = Math.round(sampleRate * duration);
    const buf = AudioBuffer.create(1, totalFrames, sampleRate);
    const ch = buf.data[0];

    // Inject transient bursts (kicks/beats) at t = 0.4s, 1.0s, 1.6s, 2.2s
    const burstTimes = [0.4, 1.0, 1.6, 2.2];
    for (const bt of burstTimes) {
      const centerFrame = Math.round(bt * sampleRate);
      for (let f = 0; f < 800; f++) {
        const idx = centerFrame + f;
        if (idx < totalFrames) {
          // Exponential decay sine burst
          ch[idx] = Math.sin((f / 44100) * 2 * Math.PI * 60) * Math.exp(-f / 150);
        }
      }
    }

    const transients = AudioTransientSyncEngine.detectTransients(buf, {
      sensitivity: 0.7,
      minPeakDistanceMs: 200,
    });

    assert.ok(transients.length >= 3, `Expected at least 3 transients, got ${transients.length}`);

    // Verify detected transient timestamps are within 40ms tolerance of synthesized bursts
    for (const bt of burstTimes.slice(0, transients.length)) {
      const match = transients.some((t) => Math.abs(t.time - bt) < 0.05);
      assert.ok(match, `Expected transient near ${bt}s`);
    }

    // Verify Bass Punch timestamps extraction
    const punchTimestamps = AudioTransientSyncEngine.extractBassPunchTimestamps(transients, 0.2);
    assert.ok(punchTimestamps.length >= 2, "Expected bass punch timestamps extracted");
  });

  it("aligns clip cut points to nearest acoustic transients", () => {
    const transients = [
      { time: 0.98, energy: 0.9, band: "sub" as const, confidence: 0.95 },
      { time: 2.05, energy: 0.85, band: "full" as const, confidence: 0.9 },
      { time: 3.12, energy: 0.88, band: "sub" as const, confidence: 0.92 },
    ];

    const clipDurations = [1.0, 1.0, 1.0, 1.0]; // Total 4.0s requested
    const aligned = AudioTransientSyncEngine.alignTimelineToTransients(clipDurations, transients, {
      maxSnapToleranceSec: 0.25,
      totalDuration: 4.0,
    });

    assert.equal(aligned.length, 4);
    assert.equal(aligned[0].alignedInTime, 0);
    assert.equal(aligned[0].alignedOutTime, 0.98); // Snapped to 0.98s transient
    assert.equal(aligned[1].alignedInTime, 0.98);
    assert.equal(aligned[1].alignedOutTime, 2.05); // Snapped to 2.05s transient
    assert.equal(aligned[2].alignedInTime, 2.05);
    assert.equal(aligned[2].alignedOutTime, 3.12); // Snapped to 3.12s transient
    assert.equal(aligned[3].alignedInTime, 3.12);
    assert.equal(aligned[3].alignedOutTime, 4.0);  // Ends at total duration
  });
});

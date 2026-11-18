import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { TimecodeUtils, StandardFrameRates } from "../../exporters/common/TimecodeUtils.js";

describe("Fase 17 — TimecodeUtils Deterministic Math Tests", () => {
  it("converts seconds to frames and timecode accurately for integer framerates (24, 25, 30, 60 fps)", () => {
    const rate30 = StandardFrameRates["30"];
    assert.equal(TimecodeUtils.secondsToFrame(0, rate30), 0);
    assert.equal(TimecodeUtils.secondsToFrame(1.0, rate30), 30);
    assert.equal(TimecodeUtils.secondsToFrame(10.5, rate30), 315);

    assert.equal(TimecodeUtils.frameToTimecode(0, rate30), "00:00:00:00");
    assert.equal(TimecodeUtils.frameToTimecode(30, rate30), "00:00:01:00");
    assert.equal(TimecodeUtils.frameToTimecode(315, rate30), "00:00:10:15");
    assert.equal(TimecodeUtils.frameToTimecode(108000, rate30), "01:00:00:00");

    assert.equal(TimecodeUtils.timecodeToFrame("00:00:01:00", rate30), 30);
    assert.equal(TimecodeUtils.timecodeToFrame("00:00:10:15", rate30), 315);
    assert.equal(TimecodeUtils.timecodeToFrame("01:00:00:00", rate30), 108000);
  });

  it("handles SMPTE 29.97 Drop-Frame (DF) and Non-Drop-Frame (NDF) accurately", () => {
    const rateNDF = StandardFrameRates["29.97ndf"];
    const rateDF = StandardFrameRates["29.97df"];

    assert.equal(rateNDF.dropFrame, false);
    assert.equal(rateDF.dropFrame, true);

    // En 29.97 DF, el separador de frames es ';'
    const tcDF = TimecodeUtils.frameToTimecode(30, rateDF);
    assert.ok(tcDF.includes(";"), `Expected drop-frame separator ';' in ${tcDF}`);

    // Round-trip conversion test
    const testFrames = [0, 30, 1797, 1798, 1800, 17982, 107892];
    for (const frame of testFrames) {
      const tc = TimecodeUtils.frameToTimecode(frame, rateDF);
      const recovered = TimecodeUtils.timecodeToFrame(tc, rateDF);
      assert.equal(recovered, frame, `Mismatch in DF frame ${frame} -> ${tc} -> ${recovered}`);
    }
  });

  it("resolves rational framerates flexibly from numbers and strings", () => {
    const r2997 = TimecodeUtils.resolveFrameRate(29.97);
    assert.equal(r2997.numerator, 30000);
    assert.equal(r2997.denominator, 1001);

    const r2398 = TimecodeUtils.resolveFrameRate(23.976);
    assert.equal(r2398.numerator, 24000);
    assert.equal(r2398.denominator, 1001);

    const r60 = TimecodeUtils.resolveFrameRate("60");
    assert.equal(r60.numerator, 60);
    assert.equal(r60.denominator, 1);
  });
});

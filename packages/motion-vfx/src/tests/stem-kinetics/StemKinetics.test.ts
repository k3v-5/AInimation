import { describe, it } from "node:test";
import assert from "node:assert";
import fc from "fast-check";
import {
  SubBassReactionEngine,
  AspectRatioBreathingEngine,
  DatamoshEngine,
  StemKineticsOrchestrator,
  AspectRatioFormat,
} from "../../stem-kinetics/index.js";

describe("Fase 29: Audio Stem Engine, Aspect Ratio & Datamosh Suite", () => {
  it("SubBassReactionEngine: evaluates bounce scale accurately at t = hitTime and after decay", () => {
    const hitTimes = [1.0];
    const bouncePercent = 10.0; // +10%
    const decay = 0.25;
    const resonanceHz = 12.0;

    // At exactly t = 1.0, scale must be 100 * (1 + 0.1) = 110.0%
    const scalePeak = SubBassReactionEngine.evaluateBounceScale(1.0, hitTimes, bouncePercent, decay, resonanceHz, 100.0);
    assert.strictEqual(Math.round(scalePeak * 10) / 10, 110.0);

    // Prior to hit, scale is baseline 100.0%
    const scaleBefore = SubBassReactionEngine.evaluateBounceScale(0.8, hitTimes, bouncePercent, decay, resonanceHz, 100.0);
    assert.strictEqual(scaleBefore, 100.0);

    // After 4*tau = 1.0s (t = 2.0s), scale is essentially back to 100.0%
    const scaleAfter = SubBassReactionEngine.evaluateBounceScale(2.5, hitTimes, bouncePercent, decay, resonanceHz, 100.0);
    assert.strictEqual(Math.round(scaleAfter), 100);
  });

  it("SubBassReactionEngine: generates keyframes array covering 808 hit times", () => {
    const kfs = SubBassReactionEngine.generateKeyframes([1.5], 8.0, 0.2, 12.0, 30.0);
    assert.ok(kfs.length > 5);
    // Should have peak near 108.0%
    const maxScale = Math.max(...kfs.map(k => k.scale));
    assert.strictEqual(Math.round(maxScale * 10) / 10, 108.0);
  });

  it("AspectRatioBreathingEngine: computes format ratios for 9:16, 1:1, 4:3, 16:9, and 2.39:1", () => {
    assert.strictEqual(AspectRatioBreathingEngine.getFormatRatio("9:16"), 9 / 16);
    assert.strictEqual(AspectRatioBreathingEngine.getFormatRatio("1:1"), 1.0);
    assert.strictEqual(Math.round(AspectRatioBreathingEngine.getFormatRatio("4:3") * 100) / 100, 1.33);
    assert.strictEqual(Math.round(AspectRatioBreathingEngine.getFormatRatio("16:9") * 100) / 100, 1.78);
    assert.strictEqual(AspectRatioBreathingEngine.getFormatRatio("2.39:1"), 2.39);
  });

  it("AspectRatioBreathingEngine: calculates accurate letterbox bar heights and pillarbox widths without negative values", () => {
    // 1920x1080 comp (16:9) to 2.39:1 (Scope) -> letterbox (top and bottom bars)
    const scopeDims = AspectRatioBreathingEngine.computeMatteDimensions(1920, 1080, 2.39);
    assert.strictEqual(scopeDims.visibleWidth, 1920);
    assert.ok(scopeDims.visibleHeight < 1080);
    assert.ok(scopeDims.topBottomBarHeight > 0);
    assert.strictEqual(scopeDims.leftRightBarWidth, 0);

    // 1920x1080 comp (16:9) to 4:3 (IMAX Academy) -> pillarbox (left and right bars)
    const imaxDims = AspectRatioBreathingEngine.computeMatteDimensions(1920, 1080, 4 / 3);
    assert.strictEqual(imaxDims.visibleHeight, 1080);
    assert.ok(imaxDims.visibleWidth < 1920);
    assert.strictEqual(imaxDims.topBottomBarHeight, 0);
    assert.ok(imaxDims.leftRightBarWidth > 0);
  });

  it("AspectRatioBreathingEngine: exports ExtendScript with subtractive matte mask and animated shape vertices", () => {
    const script = AspectRatioBreathingEngine.exportToExtendScript({
      id: "breathing_test",
      transitions: [
        { targetFormat: "2.39:1", startTimeSeconds: 1.0, durationSeconds: 0.8 },
      ],
      barColor: [0, 0, 0],
    }, { compVarName: "mainComp" });

    const joined = script.join("\n");
    assert.ok(joined.includes("mainComp.layers.addSolid"));
    assert.ok(joined.includes("matteSolid.motionBlur = true;"));
    assert.ok(joined.includes("maskMode = MaskMode.SUBTRACT;"));
    assert.ok(joined.includes("shapeAtT.vertices"));
    assert.ok(joined.includes("maskProp.setValueAtTime(1.8000, shapeAtT);"));
  });

  it("DatamoshEngine: computes macroblock counts for 8px and 16px sizes", () => {
    const mb16 = DatamoshEngine.computeMacroblockCounts(1920, 1080, 16);
    assert.strictEqual(mb16.horizontalBlocks, 120);
    assert.strictEqual(mb16.verticalBlocks, 67);

    const mb8 = DatamoshEngine.computeMacroblockCounts(1920, 1080, 8);
    assert.strictEqual(mb8.horizontalBlocks, 240);
    assert.strictEqual(mb8.verticalBlocks, 135);
  });

  it("DatamoshEngine: exports ExtendScript with ADBE Mosaic and ADBE Displacement Map", () => {
    const script = DatamoshEngine.exportToExtendScript({
      id: "datamosh_test",
      cutTimeSeconds: 3.5,
      durationSeconds: 0.5,
      macroblockSize: 16,
      displacementIntensity: 75.0,
    }, { compVarName: "comp", sourceLayerVarName: "lyrA", destLayerVarName: "lyrB" });

    const joined = script.join("\n");
    assert.ok(joined.includes("comp.layers.addSolid"));
    assert.ok(joined.includes("moshAdj.adjustmentLayer = true;"));
    assert.ok(joined.includes('addProperty("ADBE Mosaic")'));
    assert.ok(joined.includes('addProperty("ADBE Displacement Map")'));
    assert.ok(joined.includes("maxDispProp.setValueAtTime(3.5000, 75.0);"));
    assert.ok(joined.includes("maxDispProp.setValueAtTime(4.0000, 0.0);"));
  });

  it("StemKineticsOrchestrator: produces deterministic plan with SHA-256 and comp.motionBlur", () => {
    const plan1 = StemKineticsOrchestrator.compilePlan({
      id: "kinetics_orch_test",
      subBass: {
        id: "sub_orch",
        hitTimesSeconds: [1.0, 2.0],
        bounceScalePercent: 8.0,
        decaySeconds: 0.25,
        resonanceHz: 12.0,
      },
      aspectRatioBreathing: {
        id: "aspect_orch",
        transitions: [{ targetFormat: "2.39:1", startTimeSeconds: 1.0, durationSeconds: 0.5 }],
      },
      datamosh: {
        id: "mosh_orch",
        cutTimeSeconds: 2.0,
        durationSeconds: 0.4,
        macroblockSize: 16,
        displacementIntensity: 50.0,
      },
    });

    const plan2 = StemKineticsOrchestrator.compilePlan({
      id: "kinetics_orch_test",
      subBass: {
        id: "sub_orch",
        hitTimesSeconds: [1.0, 2.0],
        bounceScalePercent: 8.0,
        decaySeconds: 0.25,
        resonanceHz: 12.0,
      },
      aspectRatioBreathing: {
        id: "aspect_orch",
        transitions: [{ targetFormat: "2.39:1", startTimeSeconds: 1.0, durationSeconds: 0.5 }],
      },
      datamosh: {
        id: "mosh_orch",
        cutTimeSeconds: 2.0,
        durationSeconds: 0.4,
        macroblockSize: 16,
        displacementIntensity: 50.0,
      },
    });

    assert.strictEqual(plan1.checksumSha256, plan2.checksumSha256);
    assert.strictEqual(plan1.checksumSha256.length, 64);
    assert.ok(plan1.extendScriptLines.some(line => line.includes("comp.motionBlur = true;")));
  });

  // --- PROPERTY-BASED TESTS ---
  it("PBT: evaluateBounceScale never returns zero or negative scale for positive baseScale", () => {
    fc.assert(
      fc.property(
        fc.double({ min: 0.0, max: 10.0, noNaN: true }),
        fc.double({ min: 1.0, max: 20.0, noNaN: true }),
        fc.double({ min: 0.05, max: 0.5, noNaN: true }),
        fc.double({ min: 5.0, max: 25.0, noNaN: true }),
        (t, bounce, decay, res) => {
          const s = SubBassReactionEngine.evaluateBounceScale(t, [1.0, 3.0], bounce, decay, res, 100.0);
          assert.ok(s > 0, `Scale ${s} must be strictly positive`);
        }
      ),
      { numRuns: 100 }
    );
  });

  it("PBT: computeMatteDimensions always yields topBottomBarHeight >= 0 and leftRightBarWidth >= 0", () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 320, max: 4096 }),
        fc.integer({ min: 240, max: 4096 }),
        fc.constantFrom("9:16", "1:1", "4:3", "16:9", "2.39:1" as AspectRatioFormat),
        (w, h, format) => {
          const r = AspectRatioBreathingEngine.getFormatRatio(format);
          const dims = AspectRatioBreathingEngine.computeMatteDimensions(w, h, r);
          assert.ok(dims.topBottomBarHeight >= 0, `Top/bottom bar ${dims.topBottomBarHeight} must be >= 0`);
          assert.ok(dims.leftRightBarWidth >= 0, `Left/right bar ${dims.leftRightBarWidth} must be >= 0`);
          assert.ok(dims.visibleWidth <= w + 1e-3, `Visible width ${dims.visibleWidth} must not exceed comp width ${w}`);
          assert.ok(dims.visibleHeight <= h + 1e-3, `Visible height ${dims.visibleHeight} must not exceed comp height ${h}`);
        }
      ),
      { numRuns: 150 }
    );
  });
});

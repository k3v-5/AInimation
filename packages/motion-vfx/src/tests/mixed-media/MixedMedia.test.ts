import { describe, it } from "node:test";
import assert from "node:assert";
import fc from "fast-check";
import {
  ImpactFramesEngine,
  SpeedLinesEngine,
  SprocketHolesEngine,
  PaperTearEngine,
  DoodleBoilEngine,
  MixedMediaOrchestrator,
} from "../../mixed-media/index.js";

describe("Fase 28: Mixed-Media & Anime Kinetics Suite", () => {
  it("ImpactFramesEngine: quantizes time to exact frame grid and calculates window duration", () => {
    const fps = 30.0;
    // 1.01s at 30fps -> frame 30 -> 1.0000s
    const q1 = ImpactFramesEngine.quantizeToFrameGrid(1.01, fps);
    assert.strictEqual(q1, 1.0);

    // 1.04s at 30fps -> frame 31 -> 31/30 = 1.0333333s
    const q2 = ImpactFramesEngine.quantizeToFrameGrid(1.04, fps);
    assert.strictEqual(Math.round(q2 * 1000) / 1000, 1.033);

    // 1 frame window
    const win1 = ImpactFramesEngine.calculateFrameWindow(2.0, 1, 30.0);
    assert.strictEqual(win1.startSeconds, 2.0);
    assert.strictEqual(Math.round(win1.endSeconds * 1000) / 1000, 2.033);
    assert.strictEqual(win1.frameCount, 1);

    // 2 frame window
    const win2 = ImpactFramesEngine.calculateFrameWindow(2.0, 2, 30.0);
    assert.strictEqual(win2.startSeconds, 2.0);
    assert.strictEqual(Math.round(win2.endSeconds * 1000) / 1000, 2.067);
    assert.strictEqual(win2.frameCount, 2);
  });

  it("ImpactFramesEngine: exports valid ExtendScript with Difference mode for INVERT_NEGATIVE", () => {
    const script = ImpactFramesEngine.exportToExtendScript({
      id: "manga_hit",
      impactTimeSeconds: 1.5,
      frameDuration: 1,
      mode: "INVERT_NEGATIVE",
    }, 30.0, { compVarName: "mainComp" });

    const joined = script.join("\n");
    assert.ok(joined.includes("mainComp.layers.addSolid"));
    assert.ok(joined.includes("impactSolid.blendingMode = BlendingMode.DIFFERENCE;"));
    assert.ok(joined.includes("impactSolid.motionBlur = true;"));
    assert.ok(joined.includes("impactSolid.inPoint = 1.5000;"));
  });

  it("SpeedLinesEngine: geometrically checks inside/outside of subject exclusion zone", () => {
    const center: [number, number] = [540, 960];
    const innerRadius = 250;

    // Center is inside
    assert.strictEqual(SpeedLinesEngine.isInsideExclusionZone(540, 960, center, innerRadius), true);
    // Point at distance 100px is inside
    assert.strictEqual(SpeedLinesEngine.isInsideExclusionZone(540, 1060, center, innerRadius), true);
    // Point at distance 300px is outside
    assert.strictEqual(SpeedLinesEngine.isInsideExclusionZone(540, 1260, center, innerRadius), false);
    // Corner is outside
    assert.strictEqual(SpeedLinesEngine.isInsideExclusionZone(0, 0, center, innerRadius), false);
  });

  it("SpeedLinesEngine: exports ExtendScript with subtractive elliptical mask and posterizeTime boil", () => {
    const script = SpeedLinesEngine.exportToExtendScript({
      id: "shonen_speed",
      startTimeSeconds: 1.0,
      durationSeconds: 2.0,
      centerPoint: [540, 850],
      innerRadiusPx: 260,
      lineCount: 75,
      color: [1, 1, 1],
      boilFps: 12,
      density: 0.7,
    }, { compVarName: "myComp" });

    const joined = script.join("\n");
    assert.ok(joined.includes("myComp.layers.addSolid"));
    assert.ok(joined.includes("maskMode = MaskMode.SUBTRACT"));
    assert.ok(joined.includes('addProperty("ADBE Radial Blur")'));
    assert.ok(joined.includes("posterizeTime(12);"));
    assert.ok(joined.includes("speedSolid.motionBlur = true;"));
  });

  it("SprocketHolesEngine: computes 4 perforations for 35mm and 1 for 16mm", () => {
    const p35 = SprocketHolesEngine.computePerforationPositions(1920, "35MM");
    assert.strictEqual(p35.length, 4);
    assert.strictEqual(p35[0], 240);
    assert.strictEqual(p35[1], 720);
    assert.strictEqual(p35[2], 1200);
    assert.strictEqual(p35[3], 1680);

    const p16 = SprocketHolesEngine.computePerforationPositions(1920, "16MM");
    assert.strictEqual(p16.length, 1);
    assert.strictEqual(p16[0], 960);
  });

  it("PaperTearEngine: generates deterministic fractal tear offsets with roughness", () => {
    const offsets = PaperTearEngine.generateFractalTearOffsets(40, 8);
    assert.strictEqual(offsets.length, 8);
    // First offset at s=0 is 0
    assert.strictEqual(offsets[0], 12); // cos(0)*0.3*40 = 12
    // All offsets should be bounded by roughness
    for (const off of offsets) {
      assert.ok(Math.abs(off) <= 45);
    }
  });

  it("DoodleBoilEngine: calculates frame step and exports turbulent displace with posterized evolution", () => {
    assert.strictEqual(DoodleBoilEngine.calculateFrameStep(12), 1.0 / 12);
    assert.strictEqual(DoodleBoilEngine.calculateFrameStep(8), 1.0 / 8);

    const script = DoodleBoilEngine.exportToExtendScript({
      id: "doodle_test",
      startTimeSeconds: 0.0,
      durationSeconds: 2.0,
      boilFps: 12,
      jitterAmplitudePx: 4,
      strokeColor: [1, 1, 0],
      strokeWidthPx: 3,
    }, { layerVarName: "heroLyr" });

    const joined = script.join("\n");
    assert.ok(joined.includes("heroLyr.motionBlur = true;"));
    assert.ok(joined.includes('addProperty("ADBE Turbulent Displace")'));
    assert.ok(joined.includes("posterizeTime(12);"));
    assert.ok(joined.includes('addProperty("ADBE Roughen Edges")'));
  });

  it("MixedMediaOrchestrator: produces deterministic plan with SHA-256 and comp.motionBlur", () => {
    const plan1 = MixedMediaOrchestrator.compilePlan({
      id: "media_orch_test",
      impactFrame: {
        id: "impact_sub",
        impactTimeSeconds: 2.5,
        frameDuration: 1,
        mode: "INVERT_NEGATIVE",
      },
      speedLines: {
        id: "speed_sub",
        startTimeSeconds: 1.0,
        durationSeconds: 1.5,
        innerRadiusPx: 250,
      },
      sprocketHoles: {
        id: "sprocket_sub",
        gauge: "35MM",
        side: "BOTH",
        gateWeaveJitterPx: 2.0,
      },
    });

    const plan2 = MixedMediaOrchestrator.compilePlan({
      id: "media_orch_test",
      impactFrame: {
        id: "impact_sub",
        impactTimeSeconds: 2.5,
        frameDuration: 1,
        mode: "INVERT_NEGATIVE",
      },
      speedLines: {
        id: "speed_sub",
        startTimeSeconds: 1.0,
        durationSeconds: 1.5,
        innerRadiusPx: 250,
      },
      sprocketHoles: {
        id: "sprocket_sub",
        gauge: "35MM",
        side: "BOTH",
        gateWeaveJitterPx: 2.0,
      },
    });

    assert.strictEqual(plan1.checksumSha256, plan2.checksumSha256);
    assert.strictEqual(plan1.checksumSha256.length, 64);
    assert.ok(plan1.extendScriptLines.some(line => line.includes("comp.motionBlur = true;")));
  });

  // --- PROPERTY-BASED TESTS ---
  it("PBT: quantizeToFrameGrid is always an exact multiple of (1 / fps) within epsilon", () => {
    fc.assert(
      fc.property(
        fc.double({ min: 0.0, max: 100.0, noNaN: true }),
        fc.constantFrom(24.0, 25.0, 29.97, 30.0, 60.0),
        (t, fps) => {
          const q = ImpactFramesEngine.quantizeToFrameGrid(t, fps);
          const frame = Math.round(q * fps);
          const reconstructed = frame / fps;
          assert.ok(Math.abs(q - reconstructed) < 1e-9, `Quantized ${q} must equal ${reconstructed}`);
        }
      ),
      { numRuns: 100 }
    );
  });

  it("PBT: isInsideExclusionZone strictly obeys Euclidean distance < innerRadius", () => {
    fc.assert(
      fc.property(
        fc.double({ min: 0, max: 1920, noNaN: true }),
        fc.double({ min: 0, max: 1920, noNaN: true }),
        fc.double({ min: 50, max: 800, noNaN: true }),
        (x, y, radius) => {
          const center: [number, number] = [960, 540];
          const inside = SpeedLinesEngine.isInsideExclusionZone(x, y, center, radius);
          const dist = Math.hypot(x - center[0], y - center[1]);
          assert.strictEqual(inside, dist < radius);
        }
      ),
      { numRuns: 150 }
    );
  });
});

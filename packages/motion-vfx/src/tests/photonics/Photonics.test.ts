import { describe, it } from "node:test";
import assert from "node:assert";
import fc from "fast-check";
import {
  ShutterDragEngine,
  AnamorphicStreakEngine,
  PrismStarEngine,
  FlirThermalEngine,
  PhotonicsOrchestrator,
  FlirPalette,
} from "../../photonics/index.js";

describe("Fase 27: Nocturnal Photonics & Optical Artefacts Suite", () => {
  it("ShutterDragEngine: maps operators and computes exponential decay amplitudes", () => {
    assert.strictEqual(ShutterDragEngine.mapOperatorToIndex("MAXIMUM"), 8);
    assert.strictEqual(ShutterDragEngine.mapOperatorToIndex("ADD"), 1);
    assert.strictEqual(ShutterDragEngine.mapOperatorToIndex("SCREEN"), 2);
    assert.strictEqual(ShutterDragEngine.mapOperatorToIndex("COMPOSITE_IN_BACK"), 5);

    const amps = ShutterDragEngine.calculateEchoAmplitudes(5, 0.5);
    assert.strictEqual(amps.length, 5);
    assert.strictEqual(amps[0], 1.0);
    assert.strictEqual(amps[1], 0.5);
    assert.strictEqual(amps[2], 0.25);
    assert.strictEqual(amps[3], 0.125);
    assert.strictEqual(amps[4], 0.0625);
  });

  it("ShutterDragEngine: exports valid ExtendScript with keyframed Number of Echoes and motion blur", () => {
    const script = ShutterDragEngine.exportToExtendScript({
      id: "shutter_test",
      startTimeSeconds: 1.0,
      durationSeconds: 2.0,
      echoCount: 6,
      echoTimeStepSeconds: -0.033,
      decay: 0.8,
      blendOperator: "MAXIMUM",
      chromaticDispersion: true,
    }, { layerVarName: "myLyr" });

    const joined = script.join("\n");
    assert.ok(joined.includes("myLyr.motionBlur = true;"));
    assert.ok(joined.includes('addProperty("ADBE Echo")'));
    assert.ok(joined.includes('echoFx.property("Echo Operator").setValue(8)'));
    assert.ok(joined.includes('numEchoesProp.setValueAtTime("1.0000", 0)') || joined.includes("setValueAtTime(1.0000, 0)"));
    assert.ok(joined.includes('addProperty("ADBE Shift Channels")'));
  });

  it("AnamorphicStreakEngine: calculates perceptual luminance and highlight thresholding", () => {
    // Luminance Rec. 601 / 709
    const lumBlack = AnamorphicStreakEngine.computePerceptualLuminance(0, 0, 0);
    assert.strictEqual(lumBlack, 0.0);

    const lumWhite = AnamorphicStreakEngine.computePerceptualLuminance(1, 1, 1);
    assert.strictEqual(Math.round(lumWhite * 1000) / 1000, 1.0);

    // Pure green is highest contributor: 0.587
    const lumGreen = AnamorphicStreakEngine.computePerceptualLuminance(0, 1, 0);
    assert.strictEqual(Math.round(lumGreen * 1000) / 1000, 0.587);

    // Highlight test: 80% threshold
    assert.strictEqual(AnamorphicStreakEngine.isHighlight(1.0, 1.0, 1.0, 80), true);
    assert.strictEqual(AnamorphicStreakEngine.isHighlight(0.2, 0.2, 0.2, 80), false);
  });

  it("AnamorphicStreakEngine: exports ExtendScript with ADBE Levels2, Directional Blur, and ADBE Tint", () => {
    const script = AnamorphicStreakEngine.exportToExtendScript({
      id: "streak_test",
      startTimeSeconds: 2.0,
      durationSeconds: 1.5,
      thresholdPercent: 85,
      streakLength: 350,
      directionDegrees: 90.0,
      tintColor: [0.0, 0.85, 1.0],
      intensity: 1.2,
    }, { compVarName: "mainComp", layerVarName: "heroLayer" });

    const joined = script.join("\n");
    assert.ok(joined.includes("mainComp.layers.addSolid"));
    assert.ok(joined.includes("streakAdj.blendingMode = BlendingMode.ADD"));
    assert.ok(joined.includes('addProperty("ADBE Levels2")'));
    assert.ok(joined.includes('addProperty("ADBE Directional Blur")'));
    assert.ok(joined.includes("dirBlurFx.property(\"Direction\").setValue(90.0)"));
    assert.ok(joined.includes("dirBlurFx.property(\"Blur Length\").setValue(350.0)"));
    assert.ok(joined.includes('addProperty("ADBE Tint")'));
    assert.ok(joined.includes("streakAdj.inPoint = 2.0000;"));
  });

  it("PrismStarEngine: computes symmetric diffraction angles for 4-point and 6-point stars", () => {
    const angles4 = PrismStarEngine.computeDiffractionAngles(4, 45);
    assert.strictEqual(angles4.length, 2);
    assert.strictEqual(angles4[0], 45);
    assert.strictEqual(angles4[1], 135);

    const angles6 = PrismStarEngine.computeDiffractionAngles(6, 30);
    assert.strictEqual(angles6.length, 3);
    assert.strictEqual(angles6[0], 30);
    assert.strictEqual(angles6[1], 90);
    assert.strictEqual(angles6[2], 150);
  });

  it("FlirThermalEngine: evaluates thermal Ironbow transfer function correctly across Y ranges", () => {
    // Cold background (Y = 0) -> Blue/Dark Purple
    const cold = FlirThermalEngine.evaluateThermalColor(0.0, "IRONBOW");
    assert.ok(cold[2] > cold[0]);
    assert.strictEqual(cold[1], 0.0);

    // Mid-high heat (Y = 0.6) -> Red/Orange
    const midHot = FlirThermalEngine.evaluateThermalColor(0.6, "IRONBOW");
    assert.strictEqual(midHot[0], 1.0); // Full red
    assert.ok(midHot[1] > 0.0); // Some green for orange
    assert.strictEqual(midHot[2], 0.0); // Zero blue

    // Blinding heat (Y = 1.0) -> White
    const maxHeat = FlirThermalEngine.evaluateThermalColor(1.0, "IRONBOW");
    assert.strictEqual(maxHeat[0], 1.0);
    assert.strictEqual(maxHeat[1], 1.0);
    assert.strictEqual(maxHeat[2], 1.0);
  });

  it("PhotonicsOrchestrator: produces deterministic plan with SHA-256 and comp.motionBlur", () => {
    const plan1 = PhotonicsOrchestrator.compilePlan({
      id: "orch_test",
      shutterDrag: {
        id: "shutter_sub",
        startTimeSeconds: 0.0,
        durationSeconds: 1.0,
        echoCount: 4,
        echoTimeStepSeconds: -0.04,
        decay: 0.7,
        blendOperator: "MAXIMUM",
      },
      anamorphicStreak: {
        id: "streak_sub",
        thresholdPercent: 80,
        streakLength: 200,
        directionDegrees: 90,
        tintColor: [0.0, 0.9, 1.0],
        intensity: 1.0,
      },
      flirThermal: {
        id: "thermal_sub",
        palette: "IRONBOW",
        thermalNoiseIntensity: 15,
        edgeEnhancement: true,
      },
    });

    const plan2 = PhotonicsOrchestrator.compilePlan({
      id: "orch_test",
      shutterDrag: {
        id: "shutter_sub",
        startTimeSeconds: 0.0,
        durationSeconds: 1.0,
        echoCount: 4,
        echoTimeStepSeconds: -0.04,
        decay: 0.7,
        blendOperator: "MAXIMUM",
      },
      anamorphicStreak: {
        id: "streak_sub",
        thresholdPercent: 80,
        streakLength: 200,
        directionDegrees: 90,
        tintColor: [0.0, 0.9, 1.0],
        intensity: 1.0,
      },
      flirThermal: {
        id: "thermal_sub",
        palette: "IRONBOW",
        thermalNoiseIntensity: 15,
        edgeEnhancement: true,
      },
    });

    assert.strictEqual(plan1.checksumSha256, plan2.checksumSha256);
    assert.strictEqual(plan1.checksumSha256.length, 64);
    assert.ok(plan1.extendScriptLines.some(line => line.includes("comp.motionBlur = true;")));
  });

  // --- PROPERTY-BASED TESTS ---
  it("PBT: Shutter drag echo amplitudes are strictly monotonically decreasing for decay in (0, 1)", () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 2, max: 15 }),
        fc.double({ min: 0.05, max: 0.95, noNaN: true }),
        (count, decay) => {
          const amps = ShutterDragEngine.calculateEchoAmplitudes(count, decay);
          for (let i = 0; i < amps.length - 1; i++) {
            assert.ok(amps[i] > amps[i + 1], `Amplitudes must strictly decrease: amps[${i}]=${amps[i]} > amps[${i+1}]=${amps[i+1]}`);
          }
        }
      ),
      { numRuns: 100 }
    );
  });

  it("PBT: Perceptual luminance is always bounded in [0, 1] for any valid RGB input", () => {
    fc.assert(
      fc.property(
        fc.double({ min: 0.0, max: 1.0, noNaN: true }),
        fc.double({ min: 0.0, max: 1.0, noNaN: true }),
        fc.double({ min: 0.0, max: 1.0, noNaN: true }),
        (r, g, b) => {
          const lum = AnamorphicStreakEngine.computePerceptualLuminance(r, g, b);
          assert.ok(lum >= -1e-10 && lum <= 1.0 + 1e-10, `Luminance ${lum} must be in [0, 1]`);
        }
      ),
      { numRuns: 100 }
    );
  });

  it("PBT: FLIR thermal RGB components are always strictly bounded in [0, 1] across all palettes", () => {
    const palettes: FlirPalette[] = ["IRONBOW", "RAINBOW", "WHITE_HOT", "ARCTIC"];
    fc.assert(
      fc.property(
        fc.double({ min: 0.0, max: 1.0, noNaN: true }),
        fc.constantFrom(...palettes),
        (y, palette) => {
          const [r, g, b] = FlirThermalEngine.evaluateThermalColor(y, palette);
          assert.ok(r >= -1e-6 && r <= 1.0001, `R ${r} must be in [0, 1] for palette ${palette}`);
          assert.ok(g >= -1e-6 && g <= 1.0001, `G ${g} must be in [0, 1] for palette ${palette}`);
          assert.ok(b >= -1e-6 && b <= 1.0001, `B ${b} must be in [0, 1] for palette ${palette}`);
        }
      ),
      { numRuns: 150 }
    );
  });
});

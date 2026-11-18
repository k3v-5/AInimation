import test from "node:test";
import assert from "node:assert/strict";
import fc from "fast-check";
import {
  FilmGrainEngine,
  FilmHalationEngine,
  FilmShutterFlickerEngine,
  AuteurColorGradingEngine,
  FilmOrchestrator,
  FilmGrainSpecSchema,
  FilmHalationSpecSchema,
  ShutterFlickerSpecSchema,
  AuteurColorGradingSpecSchema,
} from "../../film/index.js";

test("Fase 22: Analog Film Texture & Auteur Color Grading Suite", async (t) => {
  // 1. UNIT TESTS: Luminance-Coupled Film Grain
  await t.test("FilmGrainEngine: G(Y) is 0 at bounds and maximizes at midtones (Y = 0.5)", () => {
    const base = 0.8;
    // Límites puros
    assert.equal(FilmGrainEngine.calculateLuminanceCoupledDensity(base, 0.0), 0.0);
    assert.equal(FilmGrainEngine.calculateLuminanceCoupledDensity(base, 1.0), 0.0);

    // Midtone perfecto Y = 0.5 -> 4 * 0.5 * 0.5 = 1.0 -> densidad = base
    assert.equal(FilmGrainEngine.calculateLuminanceCoupledDensity(base, 0.5), base);

    // Cuarto de tono Y = 0.25 -> 4 * 0.25 * 0.75 = 0.75 -> 0.8 * 0.75 = 0.6
    assert.equal(FilmGrainEngine.calculateLuminanceCoupledDensity(base, 0.25), 0.6);
  });

  // 2. UNIT TESTS: Halation Intensity Evaluation
  await t.test("FilmHalationEngine: evaluates zero below threshold and scales to maxIntensity at 1.0", () => {
    const threshold = 0.85;
    const maxI = 0.9;

    // Luminancia por debajo del umbral -> 0.0
    assert.equal(FilmHalationEngine.calculateHalationIntensity(0.5, threshold, maxI), 0.0);
    assert.equal(FilmHalationEngine.calculateHalationIntensity(0.85, threshold, maxI), 0.0);

    // Luminancia pico Y = 1.0 -> maxIntensity
    assert.equal(FilmHalationEngine.calculateHalationIntensity(1.0, threshold, maxI), maxI);

    // Luminancia intermedia Y = 0.925
    const midHalation = FilmHalationEngine.calculateHalationIntensity(0.925, threshold, maxI);
    assert.ok(midHalation > 0.0 && midHalation < maxI);
  });

  // 3. UNIT TESTS: Auteur Profiles Resolution
  await t.test("AuteurColorGradingEngine resolves iconic profile presets accurately", () => {
    const tyler = AuteurColorGradingEngine.resolveProfileSettings({ profile: "TYLER_PASTEL_70S" });
    assert.equal(tyler.saturationMultiplier, 1.18);
    assert.equal(tyler.contrastMultiplier, 1.06);
    assert.equal(tyler.liftPedestal, 0.05);
    assert.deepEqual(tyler.shadowTint, [-5, 8, 12]);

    const kendrick = AuteurColorGradingEngine.resolveProfileSettings({ profile: "KENDRICK_BLEACH_BYPASS_BW" });
    assert.equal(kendrick.saturationMultiplier, 0.0);
    assert.equal(kendrick.contrastMultiplier, 1.75);
    assert.equal(kendrick.liftPedestal, -0.04);

    const ralphie = AuteurColorGradingEngine.resolveProfileSettings({ profile: "RALPHIE_MINIDV_ACID" });
    assert.equal(ralphie.saturationMultiplier, 1.50);
    assert.equal(ralphie.contrastMultiplier, 1.30);
  });

  // 4. INTEGRATION TESTS: ExtendScript Emission
  await t.test("Engines generate valid ExtendScript for Grain, Halation, Flicker, and Grading", () => {
    // Grano
    const grainScript = FilmGrainEngine.exportToExtendScript({
      gauge: "16MM",
      intensity: 0.5,
      colorNoise: false,
    }).join("\n");
    assert.match(grainScript, /ADBE Noise/);
    assert.match(grainScript, /Amount of Noise/);

    // Halation
    const haloScript = FilmHalationEngine.exportToExtendScript({
      threshold: 0.85,
      intensity: 0.75,
      radiusPx: 45.0,
      tintRgb: [1.0, 0.1, 0.1],
    }).join("\n");
    assert.match(haloScript, /duplicate\(\)/);
    assert.match(haloScript, /BlendingMode\.SCREEN/);
    assert.match(haloScript, /ADBE Extract/);
    assert.match(haloScript, /ADBE Gaussian Blur/);
    assert.match(haloScript, /ADBE Tint/);

    // Flicker
    const flickScript = FilmShutterFlickerEngine.exportToExtendScript({
      frequencyHz: 18.0,
      amplitudeEv: 0.15,
      gateWeavePx: 1.2,
    }).join("\n");
    assert.match(flickScript, /wiggle\(18\.0, 1\.2\)/);
    assert.match(flickScript, /wiggle\(18\.0, 6\.0\)/);

    // Grading
    const gradeScript = AuteurColorGradingEngine.exportToExtendScript({
      profile: "TYLER_PASTEL_70S",
    }).join("\n");
    assert.match(gradeScript, /ADBE Color Balance \(HLS\)/);
    assert.match(gradeScript, /ADBE Brightness & Contrast 2/);
  });

  // 5. ORCHESTRATION & INVARIANT TESTS: Determinism and Motion Blur
  await t.test("FilmOrchestrator produces deterministic plan with SHA-256 and motionBlur invariant", () => {
    const plan1 = FilmOrchestrator.compilePlan({
      id: "film_mv_take1",
      grain: { gauge: "16MM", intensity: 0.6, colorNoise: false },
      halation: { threshold: 0.88, intensity: 0.8, radiusPx: 40.0, tintRgb: [1.0, 0.1, 0.1] },
      flicker: { frequencyHz: 24.0, amplitudeEv: 0.1, gateWeavePx: 1.5 },
      colorGrading: { profile: "TYLER_PASTEL_70S" },
    });

    const plan2 = FilmOrchestrator.compilePlan({
      id: "film_mv_take1",
      grain: { gauge: "16MM", intensity: 0.6, colorNoise: false },
      halation: { threshold: 0.88, intensity: 0.8, radiusPx: 40.0, tintRgb: [1.0, 0.1, 0.1] },
      flicker: { frequencyHz: 24.0, amplitudeEv: 0.1, gateWeavePx: 1.5 },
      colorGrading: { profile: "TYLER_PASTEL_70S" },
    });

    assert.equal(plan1.id, "film_mv_take1");
    assert.equal(plan1.checksumSha256, plan2.checksumSha256);
    assert.equal(plan1.checksumSha256.length, 64);

    const jsx = plan1.extendScriptLines.join("\n");
    assert.match(jsx, /mainComp\.motionBlur = true/);
    assert.match(jsx, /targetLayer\.motionBlur = true/);
    assert.match(jsx, /app\.endUndoGroup\(\)/);
  });

  // 6. PROPERTY-BASED TESTING: Film Grain Density Bounds & Symmetry
  await t.test("PBT: Grain density is strictly bounded within [0, baseIntensity] and symmetric around 0.5", () => {
    fc.assert(
      fc.property(
        fc.double({ min: 0.0, max: 2.0, noNaN: true }),
        fc.double({ min: 0.0, max: 1.0, noNaN: true }),
        (base, y) => {
          const density = FilmGrainEngine.calculateLuminanceCoupledDensity(base, y);
          const symmetricDensity = FilmGrainEngine.calculateLuminanceCoupledDensity(base, 1.0 - y);

          // Debe estar acotado entre 0 y base (con margen mínimo de redondeo)
          const bounded = density >= 0.0 && density <= base + 1e-5;
          // Simetría parabólica G(y) == G(1 - y)
          const symmetric = Math.abs(density - symmetricDensity) < 1e-4;

          return bounded && symmetric;
        }
      ),
      { numRuns: 150 }
    );
  });

  // 7. PROPERTY-BASED TESTING: Halation Monotonicity
  await t.test("PBT: Halation intensity is monotonically non-decreasing with respect to luminance Y", () => {
    fc.assert(
      fc.property(
        fc.double({ min: 0.5, max: 0.9, noNaN: true }), // threshold
        fc.double({ min: 0.1, max: 1.0, noNaN: true }), // maxIntensity
        fc.double({ min: 0.0, max: 1.0, noNaN: true }), // y1
        fc.double({ min: 0.0, max: 1.0, noNaN: true }), // y2
        (threshold, maxI, yA, yB) => {
          const yMin = Math.min(yA, yB);
          const yMax = Math.max(yA, yB);
          const hMin = FilmHalationEngine.calculateHalationIntensity(yMin, threshold, maxI);
          const hMax = FilmHalationEngine.calculateHalationIntensity(yMax, threshold, maxI);

          return hMax >= hMin;
        }
      ),
      { numRuns: 150 }
    );
  });
});

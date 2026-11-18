import test from "node:test";
import assert from "node:assert/strict";
import fc from "fast-check";
import {
  SnapZoomEngine,
  FisheyeOpticsEngine,
  DollyZoomEngine,
  CameraMotionOrchestrator,
  SnapZoomSpec,
  DollyZoomSpec,
} from "../../optics/index.js";

test("Fase 20: Extreme Optics, Fisheye & Camera Movement Suite", async (t) => {
  // 1. UNIT TESTS: Snap Zoom Inertial Calculation
  await t.test("SnapZoomEngine evaluates scale curve with rise, peak, and settlement", () => {
    const spec: SnapZoomSpec = {
      id: "sz_1",
      triggerTimeSeconds: 1.0,
      durationSeconds: 0.2,
      startScalePercent: 100.0,
      peakScalePercent: 180.0,
      settleScalePercent: 105.0,
      dampingRatio: 0.5,
      frequencyHz: 6.0,
      overshootPercent: 15.0,
    };

    // Antes del impacto
    assert.equal(SnapZoomEngine.evaluateScaleAtTime(spec, 0.5), 100.0);
    // En el pico (aproximadamente en t = 1.0 + 0.2*0.25 = 1.05)
    const peakScale = SnapZoomEngine.evaluateScaleAtTime(spec, 1.05);
    assert.equal(peakScale, 180.0);
    // Después de concluir la duración
    assert.equal(SnapZoomEngine.evaluateScaleAtTime(spec, 1.25), 105.0);
  });

  await t.test("SnapZoomEngine generates discrete keyframes including pre-trigger boundary", () => {
    const spec: SnapZoomSpec = {
      id: "sz_kf",
      triggerTimeSeconds: 2.0,
      durationSeconds: 0.15,
      startScalePercent: 100.0,
      peakScalePercent: 190.0,
      settleScalePercent: 100.0,
      dampingRatio: 0.5,
      frequencyHz: 6.0,
      overshootPercent: 10.0,
    };

    const kfs = SnapZoomEngine.generateKeyframes(spec, 30.0);
    assert.ok(kfs.length >= 5);
    assert.equal(kfs[0].scalePercent, 100.0);
    assert.equal(kfs[kfs.length - 1].scalePercent, 100.0);
  });

  // 2. UNIT TESTS: Fisheye Barrel Distortion
  await t.test("FisheyeOpticsEngine computes Brown-Conrady barrel distortion accurately", () => {
    // En el centro óptico (r = 0), la distorsión es cero
    assert.equal(FisheyeOpticsEngine.calculateBarrelDistortion(0.0, 50.0), 0.0);

    // Sin distorsión (k = 0), r_d = r_u
    assert.equal(FisheyeOpticsEngine.calculateBarrelDistortion(0.8, 0.0), 0.8);

    // Con distorsión positiva (Fisheye), r_d > r_u
    const dist = FisheyeOpticsEngine.calculateBarrelDistortion(0.8, 65.0);
    assert.ok(dist > 0.8, `r_d (${dist}) debe ser mayor que r_u (0.8) en lente gran angular`);
  });

  // 3. UNIT TESTS: Dolly Zoom Scale Invariance
  await t.test("DollyZoomEngine computes exact scale compensation preserving subject height", () => {
    // Si FOV inicial y final son idénticos, factor es 1.0
    assert.equal(DollyZoomEngine.calculateScaleCompensation(35.0, 35.0), 1.0);

    // Cuando FOV se abre de 35° (tele) a 85° (wide), la cámara se acerca y el factor disminuye
    const factor = DollyZoomEngine.calculateScaleCompensation(35.0, 85.0);
    assert.ok(factor < 1.0 && factor > 0.0);

    // Invariante de conservación óptica: S * tan(theta_final / 2) == tan(theta_init / 2)
    const radInit = (35.0 * Math.PI) / 360.0;
    const radFinal = (85.0 * Math.PI) / 360.0;
    const product = factor * Math.tan(radFinal);
    assert.ok(Math.abs(product - Math.tan(radInit)) < 1e-5);
  });

  // 4. INTEGRATION TESTS: Camera Motion Orchestrator Plan Compilation
  await t.test("CameraMotionOrchestrator compiles full optics plan with motion blur and ExtendScript", () => {
    const plan = CameraMotionOrchestrator.compilePlan({
      id: "videoclip_optics_master",
      targetCompWidth: 1080,
      targetCompHeight: 1920,
      fps: 30.0,
      snapZooms: [
        {
          id: "sz_snare_1",
          triggerTimeSeconds: 1.0,
          durationSeconds: 0.2,
          startScalePercent: 100,
          peakScalePercent: 185,
          settleScalePercent: 105,
          dampingRatio: 0.5,
          frequencyHz: 6.0,
          overshootPercent: 15,
        },
      ],
      fisheye: {
        id: "fish_vintage",
        distortionFactor: 70.0,
        chromaticAberrationPx: 10.0,
        vignetteAmount: 0.4,
        centerOffsetX: 0,
        centerOffsetY: 0,
      },
      whipPans: [
        {
          id: "whip_beat_drop",
          triggerTimeSeconds: 4.0,
          durationSeconds: 0.15,
          direction: "RIGHT",
          travelAngleDegrees: 270,
          blurIntensityPx: 50.0,
        },
      ],
    });

    assert.equal(plan.id, "videoclip_optics_master");
    assert.equal(plan.checksumSha256.length, 64);
    const jsx = plan.extendScriptLines.join("\n");
    assert.match(jsx, /mainComp\.motionBlur = true/);
    assert.match(jsx, /ADBE Optics Compensation/);
    assert.match(jsx, /ADBE Directional Blur/);
    assert.match(jsx, /Fisheye_Vignette/);
  });

  // 5. PROPERTY-BASED TESTING (fast-check)
  await t.test("PBT: Fisheye distortion is strictly monotonic non-decreasing for any normalized radius", () => {
    fc.assert(
      fc.property(
        fc.float({ min: 0.0, max: 0.5, noNaN: true }),
        fc.float({ min: 0.5, max: 1.0, noNaN: true }),
        fc.float({ min: 10.0, max: 100.0, noNaN: true }),
        (r1, r2, distFactor) => {
          const d1 = FisheyeOpticsEngine.calculateBarrelDistortion(r1, distFactor);
          const d2 = FisheyeOpticsEngine.calculateBarrelDistortion(r2, distFactor);
          return d2 >= d1;
        }
      ),
      { numRuns: 100 }
    );
  });

  await t.test("PBT: Dolly Zoom scale compensation satisfies optical conservation invariant for any FOVs", () => {
    fc.assert(
      fc.property(
        fc.float({ min: 20.0, max: 60.0, noNaN: true }), // Tele FOV
        fc.float({ min: 65.0, max: 120.0, noNaN: true }), // Wide FOV
        (fovInit, fovTarget) => {
          const factor = DollyZoomEngine.calculateScaleCompensation(fovInit, fovTarget);
          const radInit = (fovInit * Math.PI) / 360.0;
          const radTarget = (fovTarget * Math.PI) / 360.0;
          const recoveredTan = factor * Math.tan(radTarget);

          return Math.abs(recoveredTan - Math.tan(radInit)) < 1e-5;
        }
      ),
      { numRuns: 100 }
    );
  });
});

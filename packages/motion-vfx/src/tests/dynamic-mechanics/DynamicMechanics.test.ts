import test from "node:test";
import assert from "node:assert/strict";
import fc from "fast-check";
import {
  GyroRollEngine,
  WhipPanEngine,
  LensBreathingEngine,
  DynamicMechanicsOrchestrator,
  CentrifugalGyroRollSpecSchema,
  WhipPanMatchCutSpecSchema,
  LensBreathingSpecSchema,
} from "../../dynamic-mechanics/index.js";

test("Fase 26: Dynamic Optics & Mechanics (Gyro Rolls, Whip-Pans & Lens Breathing) Suite", async (t) => {
  // 1. UNIT TESTS: Centrifugal Gyro Angle Evaluation
  await t.test("GyroRollEngine: evaluates smooth barrel roll angle across tau [0, 1]", () => {
    // Rotación horaria 360 grados
    assert.equal(GyroRollEngine.evaluateRollAngle(0.0, 360, "CLOCKWISE", "SMOOTH"), 0.0);
    assert.equal(GyroRollEngine.evaluateRollAngle(0.5, 360, "CLOCKWISE", "SMOOTH"), 180.0);
    assert.equal(GyroRollEngine.evaluateRollAngle(1.0, 360, "CLOCKWISE", "SMOOTH"), 360.0);

    // Rotación antihoraria 720 grados (doble barrel roll estilo Big Dawgs)
    assert.equal(GyroRollEngine.evaluateRollAngle(0.0, 720, "COUNTER_CLOCKWISE", "SMOOTH"), 0.0);
    assert.equal(GyroRollEngine.evaluateRollAngle(0.5, 720, "COUNTER_CLOCKWISE", "SMOOTH"), -360.0);
    assert.equal(GyroRollEngine.evaluateRollAngle(1.0, 720, "COUNTER_CLOCKWISE", "SMOOTH"), -720.0);
  });

  // 2. UNIT TESTS: Gyro Roll Keyframes & ExtendScript
  await t.test("GyroRollEngine: generates circumscribed scale and Motion Tile mirror script", () => {
    const kfs = GyroRollEngine.generateRotationKeyframes(
      {
        startTimeSeconds: 1.0,
        durationSeconds: 1.0,
        totalRollDegrees: 360,
      },
      30.0
    );

    assert.equal(kfs.length, 31);
    assert.equal(kfs[0].timeSeconds, 1.0);
    assert.equal(kfs[0].angleDegrees, 0.0);
    assert.equal(kfs[kfs.length - 1].angleDegrees, 360.0);

    const script = GyroRollEngine.exportToExtendScript(
      {
        totalRollDegrees: 360,
        scaleBufferPercent: 142.0,
        mirrorEdges: true,
      },
      30.0
    ).join("\n");

    assert.match(script, /ADBE Motion2/);
    assert.match(script, /Mirror Edges"\)\.setValue\(true\)/);
    assert.match(script, /Scale"\)\.setValue\(\[142\.0, 142\.0\]\)/);
    assert.match(script, /motionBlur = true/);
  });

  // 3. UNIT TESTS: Directional Whip-Pan Angle and Symmetry
  await t.test("WhipPanEngine: resolves angles and symmetric directional blur in cut point", () => {
    assert.equal(WhipPanEngine.getDirectionAngleDegrees("PAN_RIGHT"), 90.0);
    assert.equal(WhipPanEngine.getDirectionAngleDegrees("PAN_LEFT"), 90.0);
    assert.equal(WhipPanEngine.getDirectionAngleDegrees("TILT_UP"), 0.0);
    assert.equal(WhipPanEngine.getDirectionAngleDegrees("TILT_DOWN"), 0.0);

    const script = WhipPanEngine.exportToExtendScript({
      cutTimeSeconds: 3.0,
      transitionDurationSeconds: 0.3,
      direction: "PAN_RIGHT",
      maxBlurLengthPx: 180,
    }).join("\n");

    assert.match(script, /ADBE Directional Blur/);
    assert.match(script, /Direction"\)\.setValue\(90\.0\)/);
    assert.match(script, /setValueAtTime\(3\.0000, 180\.0\)/); // Pico de desenfoque en el corte
    assert.match(script, /motionBlur = true/);
  });

  // 4. UNIT TESTS: Lens Breathing Scale and Focus Pull
  await t.test("LensBreathingEngine: simulates optical focal expansion during focus rack", () => {
    const script = LensBreathingEngine.exportToExtendScript({
      startTimeSeconds: 1.5,
      durationSeconds: 0.8,
      breatheScalePercent: 2.0,
      focusPullDirection: "NEAR_TO_FAR",
    }).join("\n");

    assert.match(script, /setValueAtTime\(1\.5000, \[100\.00, 100\.00\]\)/);
    assert.match(script, /setValueAtTime\(2\.3000, \[102\.00, 102\.00\]\)/);
    assert.match(script, /ADBE Gaussian Blur/);
    assert.match(script, /Repeat Edge Pixels/);
  });

  // 5. ORCHESTRATION & INVARIANT TESTS
  await t.test("DynamicMechanicsOrchestrator: produces deterministic plan with SHA-256 and motion blur", () => {
    const plan1 = DynamicMechanicsOrchestrator.compilePlan({
      id: "mechanics_mv_take",
      fps: 30,
      gyroRoll: {
        totalRollDegrees: 360,
        durationSeconds: 1.5,
      },
      whipPan: {
        cutTimeSeconds: 3.0,
        direction: "PAN_LEFT",
      },
      lensBreathing: {
        startTimeSeconds: 0.5,
        breatheScalePercent: 1.8,
      },
    });

    const plan2 = DynamicMechanicsOrchestrator.compilePlan({
      id: "mechanics_mv_take",
      fps: 30,
      gyroRoll: {
        totalRollDegrees: 360,
        durationSeconds: 1.5,
      },
      whipPan: {
        cutTimeSeconds: 3.0,
        direction: "PAN_LEFT",
      },
      lensBreathing: {
        startTimeSeconds: 0.5,
        breatheScalePercent: 1.8,
      },
    });

    assert.equal(plan1.id, "mechanics_mv_take");
    assert.equal(plan1.checksumSha256, plan2.checksumSha256);
    assert.equal(plan1.checksumSha256.length, 64);

    const jsx = plan1.extendScriptLines.join("\n");
    assert.match(jsx, /comp\.motionBlur = true/);
    assert.match(jsx, /ADBE Motion2/);
    assert.match(jsx, /ADBE Directional Blur/);
    assert.match(jsx, /app\.endUndoGroup\(\)/);
  });

  // 6. PROPERTY-BASED TESTING: Roll Angle Monotonicity
  await t.test("PBT: Gyro roll magnitude increases monotonically with tau for smooth easing", () => {
    fc.assert(
      fc.property(
        fc.double({ min: 90.0, max: 1080.0, noNaN: true }), // degrees
        fc.double({ min: 0.0, max: 1.0, noNaN: true }),     // tauA
        fc.double({ min: 0.0, max: 1.0, noNaN: true }),     // tauB
        (degrees, tA, tB) => {
          const tauMin = Math.min(tA, tB);
          const tauMax = Math.max(tA, tB);
          const aMin = Math.abs(GyroRollEngine.evaluateRollAngle(tauMin, degrees, "CLOCKWISE", "SMOOTH"));
          const aMax = Math.abs(GyroRollEngine.evaluateRollAngle(tauMax, degrees, "CLOCKWISE", "SMOOTH"));

          return aMax >= aMin;
        }
      ),
      { numRuns: 150 }
    );
  });

  // 7. PROPERTY-BASED TESTING: Circumscribed Scale Minimum Bound
  await t.test("PBT: Scale buffer percent is strictly >= 141.42% for circumscribed full-frame coverage", () => {
    fc.assert(
      fc.property(
        fc.double({ min: 141.42, max: 250.0, noNaN: true }),
        (scale) => {
          const parsed = CentrifugalGyroRollSpecSchema.parse({
            scaleBufferPercent: scale,
          });
          return parsed.scaleBufferPercent >= 141.42;
        }
      ),
      { numRuns: 100 }
    );
  });
});

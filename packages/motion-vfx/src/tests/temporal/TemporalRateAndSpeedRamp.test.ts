import test from "node:test";
import assert from "node:assert/strict";
import fc from "fast-check";
import {
  PosterizeTimeEngine,
  SpeedRampEngine,
  StutterFreezeEngine,
  TemporalOrchestrator,
  QuantizedSpeedRampSpec,
  TimeRemapKeyframe,
} from "../../temporal/index.js";

test("Fase 21: Temporal Rate Modulation & Quantized Speed Ramping Suite", async (t) => {
  // 1. UNIT TESTS: Posterize Time Quantization
  await t.test("PosterizeTimeEngine quantizes timestamps correctly for 12fps and 8fps", () => {
    // A 12fps, cada frame dura 1/12 = 0.083333s
    // t = 0.05s cae en frame 0 -> 0.0s
    assert.equal(PosterizeTimeEngine.quantizeTimestamp(0.05, 12), 0.0);
    // t = 0.10s cae en frame 1 -> 1/12 ~ 0.083333s
    assert.equal(PosterizeTimeEngine.quantizeTimestamp(0.10, 12), Number((1 / 12).toFixed(6)));
    // t = 0.50s cae en frame 6 -> 6/12 = 0.5s
    assert.equal(PosterizeTimeEngine.quantizeTimestamp(0.50, 12), 0.5);

    // A 8fps, cada frame dura 1/8 = 0.125s
    assert.equal(PosterizeTimeEngine.quantizeTimestamp(0.20, 8), 0.125);
    assert.equal(PosterizeTimeEngine.quantizeTimestamp(0.26, 8), 0.25);
  });

  // 2. UNIT TESTS: Speed Ramp Velocity Evaluation
  await t.test("SpeedRampEngine smoothly decelerates from fast to slow landing on beat drop", () => {
    const spec: QuantizedSpeedRampSpec = {
      id: "sr_drop_1",
      sourceClipDurationSeconds: 15.0,
      targetBeatDropTimeSeconds: 2.0,
      fastMultiplier: 3.0,
      slowMultiplier: 0.4,
      transitionDurationSeconds: 0.3,
      totalTimelineDurationSeconds: 5.0,
    };

    // Antes de la transición (t < 1.7) -> 3.0x
    assert.equal(SpeedRampEngine.evaluateVelocityAtTime(spec, 1.0), 3.0);
    // Exactamente en el beat drop (t = 2.0) -> 0.4x
    assert.equal(SpeedRampEngine.evaluateVelocityAtTime(spec, 2.0), 0.4);
    // Después del beat drop (t > 2.0) -> 0.4x (cámara lenta)
    assert.equal(SpeedRampEngine.evaluateVelocityAtTime(spec, 3.0), 0.4);

    // A mitad de la transición (t = 1.85) -> velocidad intermedia entre 3.0 y 0.4
    const vMid = SpeedRampEngine.evaluateVelocityAtTime(spec, 1.85);
    assert.ok(vMid < 3.0 && vMid > 0.4, `vMid (${vMid}) debe estar entre 0.4 y 3.0`);
  });

  // 3. UNIT TESTS: Stutter Freeze
  await t.test("StutterFreezeEngine locks source time during freeze interval", () => {
    const rawKfs: TimeRemapKeyframe[] = [
      { timelineSeconds: 0.0, sourceSeconds: 0.0 },
      { timelineSeconds: 1.0, sourceSeconds: 1.0 },
      { timelineSeconds: 1.05, sourceSeconds: 1.1 },
      { timelineSeconds: 1.10, sourceSeconds: 1.2 },
      { timelineSeconds: 1.20, sourceSeconds: 1.4 },
    ];

    const frozen = StutterFreezeEngine.injectFreezeIntoKeyframes(rawKfs, {
      id: "stutter_1",
      triggerTimeSeconds: 1.0,
      freezeDurationSeconds: 0.10, // Hasta 1.10s
      postResumeSpeedMultiplier: 1.0,
    });

    // En t = 1.0, 1.05, 1.10 el tiempo fuente debe estar congelado en 1.0
    assert.equal(frozen[1].sourceSeconds, 1.0);
    assert.equal(frozen[2].sourceSeconds, 1.0);
    assert.equal(frozen[3].sourceSeconds, 1.0);
  });

  // 4. INVARIANT TESTS: Keyframe Generation & Orchestration
  await t.test("SpeedRampEngine generates strictly monotonic non-decreasing time remap keyframes", () => {
    const spec: QuantizedSpeedRampSpec = {
      id: "sr_mono",
      sourceClipDurationSeconds: 10.0,
      targetBeatDropTimeSeconds: 1.5,
      fastMultiplier: 4.0,
      slowMultiplier: 0.35,
      transitionDurationSeconds: 0.2,
      totalTimelineDurationSeconds: 4.0,
    };

    const kfs = SpeedRampEngine.generateTimeRemapKeyframes(spec, 30.0);
    assert.ok(kfs.length > 0);

    for (let i = 0; i < kfs.length - 1; i++) {
      assert.ok(
        kfs[i + 1].sourceSeconds >= kfs[i].sourceSeconds,
        `Invariante de monotonía violada en t = ${kfs[i].timelineSeconds}`
      );
      assert.ok(kfs[i].sourceSeconds <= 10.0, "Tiempo fuente excede metraje disponible");
    }
  });

  await t.test("TemporalOrchestrator compiles unified plan with Posterize Time and Speed Ramp", () => {
    const plan = TemporalOrchestrator.compilePlan({
      id: "test_temp_plan",
      fps: 30.0,
      posterizeTime: { id: "p1", targetFps: 12 },
      speedRamps: [
        {
          id: "sr1",
          sourceClipDurationSeconds: 12.0,
          targetBeatDropTimeSeconds: 2.0,
          fastMultiplier: 3.0,
          slowMultiplier: 0.4,
          transitionDurationSeconds: 0.25,
          totalTimelineDurationSeconds: 6.0,
        },
      ],
      stutters: [
        {
          id: "st1",
          triggerTimeSeconds: 3.5,
          freezeDurationSeconds: 0.12,
          postResumeSpeedMultiplier: 1.0,
        },
      ],
    });

    assert.equal(plan.id, "test_temp_plan");
    assert.equal(plan.checksumSha256.length, 64);
    const jsx = plan.extendScriptLines.join("\n");
    assert.match(jsx, /mainComp\.motionBlur = true/);
    assert.match(jsx, /targetLayer\.enableTimeRemapping\(\)/);
    assert.match(jsx, /ADBE Posterize Time/);
    assert.match(jsx, /postFx\.property\("Frame Rate"\)\.setValue\(12\)/);
  });

  // 5. PROPERTY-BASED TESTING (fast-check)
  await t.test("PBT: quantizeTimestamp is strictly monotonic non-decreasing for any targetFps", () => {
    fc.assert(
      fc.property(
        fc.double({ min: 0.0, max: 10.0, noNaN: true }),
        fc.double({ min: 10.0, max: 20.0, noNaN: true }),
        fc.integer({ min: 4, max: 60 }),
        (t1, t2, fps) => {
          const q1 = PosterizeTimeEngine.quantizeTimestamp(t1, fps);
          const q2 = PosterizeTimeEngine.quantizeTimestamp(t2, fps);
          return q2 >= q1;
        }
      ),
      { numRuns: 100 }
    );
  });

  await t.test("PBT: Time remap keyframes always monotonic for arbitrary drop and speed multipliers", () => {
    fc.assert(
      fc.property(
        fc.double({ min: 1.0, max: 4.0, noNaN: true }), // targetBeatDrop
        fc.double({ min: 1.5, max: 5.0, noNaN: true }), // fastMultiplier
        fc.double({ min: 0.2, max: 0.8, noNaN: true }), // slowMultiplier
        (dropTime, fastMult, slowMult) => {
          const spec: QuantizedSpeedRampSpec = {
            id: "pbt_sr",
            sourceClipDurationSeconds: 30.0,
            targetBeatDropTimeSeconds: dropTime,
            fastMultiplier: fastMult,
            slowMultiplier: slowMult,
            transitionDurationSeconds: 0.2,
            totalTimelineDurationSeconds: dropTime + 2.0,
          };

          const kfs = SpeedRampEngine.generateTimeRemapKeyframes(spec, 30.0);
          for (let i = 0; i < kfs.length - 1; i++) {
            if (kfs[i + 1].sourceSeconds < kfs[i].sourceSeconds) return false;
          }
          return true;
        }
      ),
      { numRuns: 100 }
    );
  });
});

import test from "node:test";
import assert from "node:assert/strict";
import fc from "fast-check";
import {
  VisualContinuityEngine,
  ShotContinuityMetadata,
} from "../../editorial/index.js";

test("Fase 4B — Visual Continuity Engine Suite", async (t) => {
  await t.test("detects 180-degree line of action crossing between opposing camera azimuths", () => {
    const shots: ShotContinuityMetadata[] = [
      {
        shotId: "shot_01",
        assetId: "cam_a.mp4",
        timestampSeconds: 0,
        durationSeconds: 4.0,
        scale: "MEDIUM",
        cameraAzimuthDeg: 30.0,
      },
      {
        shotId: "shot_02",
        assetId: "cam_b.mp4",
        timestampSeconds: 4.0,
        durationSeconds: 4.0,
        scale: "MEDIUM_CLOSE",
        cameraAzimuthDeg: 200.0, // Delta = 170 degrees -> Crosses axis
      },
    ];

    const report = VisualContinuityEngine.auditSequence("seq_axis", shots);
    assert.equal(report.issues.length, 1);
    assert.equal(report.issues[0].type, "AXIS_CROSSING_180");
    assert.equal(report.issues[0].severity, "WARNING");
    assert.equal(report.issues[0].suggestedAction, "USE_BRIDGE_SHOT");
    assert.ok(report.continuityScore < 100);
  });

  await t.test("detects screen direction break when motion vector flips without neutral bridge", () => {
    const shots: ShotContinuityMetadata[] = [
      {
        shotId: "runner_01",
        assetId: "park_run.mp4",
        timestampSeconds: 0,
        durationSeconds: 3.0,
        scale: "WIDE",
        screenMotionDirection: "LEFT_TO_RIGHT",
      },
      {
        shotId: "runner_02",
        assetId: "street_run.mp4",
        timestampSeconds: 3.0,
        durationSeconds: 3.0,
        scale: "MEDIUM",
        screenMotionDirection: "RIGHT_TO_LEFT", // Inverted direction
      },
    ];

    const report = VisualContinuityEngine.auditSequence("seq_direction", shots);
    const directionIssue = report.issues.find((i) => i.type === "SCREEN_DIRECTION_BREAK");
    assert.ok(directionIssue);
    assert.equal(directionIssue.severity, "WARNING");
    assert.equal(directionIssue.suggestedAction, "INSERT_CUTAWAY");
  });

  await t.test("detects eyeline mismatch in conversational shot-reverse-shot dialogue", () => {
    const shots: ShotContinuityMetadata[] = [
      {
        shotId: "interviewer",
        assetId: "interviewer.mp4",
        timestampSeconds: 0,
        durationSeconds: 3.0,
        scale: "MEDIUM_CLOSE",
        subjectGazeAngleDeg: 25.0, // Looking right
      },
      {
        shotId: "guest",
        assetId: "guest.mp4",
        timestampSeconds: 3.0,
        durationSeconds: 4.0,
        scale: "MEDIUM_CLOSE",
        subjectGazeAngleDeg: 30.0, // Also looking right -> Collision
      },
    ];

    const report = VisualContinuityEngine.auditSequence("seq_eyeline", shots);
    const eyeIssue = report.issues.find((i) => i.type === "EYELINE_MISMATCH");
    assert.ok(eyeIssue);
    assert.equal(eyeIssue.suggestedAction, "REVERSE_CUT");
  });

  await t.test("detects color temperature drift exceeding 800K threshold", () => {
    const shots: ShotContinuityMetadata[] = [
      {
        shotId: "indoor_warm",
        assetId: "indoor.mp4",
        timestampSeconds: 0,
        durationSeconds: 5.0,
        scale: "MEDIUM",
        colorTemperatureK: 3200, // Tungsten warm
      },
      {
        shotId: "outdoor_daylight",
        assetId: "outdoor.mp4",
        timestampSeconds: 5.0,
        durationSeconds: 5.0,
        scale: "WIDE",
        colorTemperatureK: 5600, // Daylight (delta 2400K)
      },
    ];

    const report = VisualContinuityEngine.auditSequence("seq_color", shots, { colorTempThresholdK: 800 });
    const colorIssue = report.issues.find((i) => i.type === "COLOR_TEMPERATURE_DRIFT");
    assert.ok(colorIssue);
    assert.equal(colorIssue.deltaValue, 2400);
    assert.equal(colorIssue.suggestedAction, "GRADE_MATCH");
  });

  await t.test("PBT: continuityScore is always strictly bounded in [0, 100]", () => {
    fc.assert(
      fc.property(
        fc.array(
          fc.record({
            shotId: fc.string({ minLength: 1, maxLength: 8 }),
            assetId: fc.string({ minLength: 1, maxLength: 8 }),
            timestampSeconds: fc.float({ min: 0, max: 1000, noNaN: true }),
            durationSeconds: fc.float({ min: 1, max: 30, noNaN: true }),
            scale: fc.constantFrom("WIDE", "MEDIUM", "CLOSE_UP", "DETAIL" as any),
            cameraAzimuthDeg: fc.float({ min: 0, max: 360, noNaN: true }),
            colorTemperatureK: fc.float({ min: 2000, max: 10000, noNaN: true }),
          }),
          { minLength: 2, maxLength: 10 }
        ),
        (shots) => {
          const report = VisualContinuityEngine.auditSequence("pbt_seq", shots as any);
          return report.continuityScore >= 0 && report.continuityScore <= 100;
        }
      ),
      { numRuns: 50 }
    );
  });
});

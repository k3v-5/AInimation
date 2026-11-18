import crypto from "crypto";
import {
  ContinuityAuditIssue,
  ContinuityAuditIssueSchema,
  ContinuityAuditReport,
  ContinuityAuditReportSchema,
  ShotContinuityMetadata,
} from "./visual-continuity.types.js";

/**
 * REQ-005, REQ-017, REQ-018, REQ-056:
 * Master Visual Continuity Engine.
 * Audits sequences of shots against classical cinema grammar rules,
 * detecting 180-degree line crosses, screen direction flips, eyeline collisions,
 * and chromatic color temperature jumps.
 */
export class VisualContinuityEngine {
  /**
   * Audits a sequence of shots and produces a formal ContinuityAuditReport.
   */
  public static auditSequence(
    sequenceId: string,
    shots: ShotContinuityMetadata[],
    options: {
      colorTempThresholdK?: number;
      strictAxisAdherence?: boolean;
    } = {}
  ): ContinuityAuditReport {
    const colorTempThresholdK = options.colorTempThresholdK ?? 800;
    const strictAxis = options.strictAxisAdherence ?? true;
    const issues: ContinuityAuditIssue[] = [];

    if (shots.length < 2) {
      return ContinuityAuditReportSchema.parse({
        sequenceId,
        continuityScore: 100.0,
        issues: [],
        passed: true,
        analyzedShotCount: shots.length,
      });
    }

    for (let i = 0; i < shots.length - 1; i++) {
      const shotA = shots[i];
      const shotB = shots[i + 1];

      // 1. Audit 180-Degree Line of Action Crossing (REQ-005)
      if (shotA.cameraAzimuthDeg !== undefined && shotB.cameraAzimuthDeg !== undefined) {
        const deltaAngle = Math.abs(shotA.cameraAzimuthDeg - shotB.cameraAzimuthDeg) % 360;
        const normalizedDelta = deltaAngle > 180 ? 360 - deltaAngle : deltaAngle;

        if (normalizedDelta >= 140 && normalizedDelta <= 220) {
          const issueId = `issue_${i}_axis_${crypto.createHash("sha256").update(`${i}_axis_${shotA.shotId}_${shotB.shotId}`).digest("hex").slice(0, 8)}`;
          issues.push(
            ContinuityAuditIssueSchema.parse({
              id: issueId,
              type: "AXIS_CROSSING_180",
              severity: strictAxis ? "WARNING" : "INFO",
              shotAId: shotA.shotId,
              shotBId: shotB.shotId,
              timestampSeconds: shotB.timestampSeconds,
              description: `Camera azimuth flipped across action line (delta ${normalizedDelta.toFixed(1)}° between ${shotA.shotId} and ${shotB.shotId}).`,
              deltaValue: normalizedDelta,
              suggestedAction: "USE_BRIDGE_SHOT",
            })
          );
        }
      }

      // 2. Audit Screen Direction Breaks (REQ-017)
      if (
        shotA.screenMotionDirection &&
        shotB.screenMotionDirection &&
        shotA.screenMotionDirection !== "STATIC" &&
        shotB.screenMotionDirection !== "STATIC"
      ) {
        const isAtoRight = shotA.screenMotionDirection === "LEFT_TO_RIGHT";
        const isBtoLeft = shotB.screenMotionDirection === "RIGHT_TO_LEFT";
        const isAtoLeft = shotA.screenMotionDirection === "RIGHT_TO_LEFT";
        const isBtoRight = shotB.screenMotionDirection === "LEFT_TO_RIGHT";

        if ((isAtoRight && isBtoLeft) || (isAtoLeft && isBtoRight)) {
          const issueId = `issue_${i}_dir_${crypto.createHash("sha256").update(`${i}_dir_${shotA.shotId}_${shotB.shotId}`).digest("hex").slice(0, 8)}`;
          issues.push(
            ContinuityAuditIssueSchema.parse({
              id: issueId,
              type: "SCREEN_DIRECTION_BREAK",
              severity: "WARNING",
              shotAId: shotA.shotId,
              shotBId: shotB.shotId,
              timestampSeconds: shotB.timestampSeconds,
              description: `Opposing screen motion vectors (${shotA.screenMotionDirection} -> ${shotB.screenMotionDirection}) without neutral bridge.`,
              suggestedAction: "INSERT_CUTAWAY",
            })
          );
        }
      }

      // 3. Audit Eyeline Collisions (REQ-056)
      if (shotA.subjectGazeAngleDeg !== undefined && shotB.subjectGazeAngleDeg !== undefined) {
        const aLooksRight = shotA.subjectGazeAngleDeg > 15;
        const bLooksRight = shotB.subjectGazeAngleDeg > 15;
        const aLooksLeft = shotA.subjectGazeAngleDeg < -15;
        const bLooksLeft = shotB.subjectGazeAngleDeg < -15;

        // In shot-reverse-shot dialogue, subjects must look in opposite screen directions to converse
        if ((aLooksRight && bLooksRight) || (aLooksLeft && bLooksLeft)) {
          const issueId = `issue_${i}_eye_${crypto.createHash("sha256").update(`${i}_eye_${shotA.shotId}_${shotB.shotId}`).digest("hex").slice(0, 8)}`;
          issues.push(
            ContinuityAuditIssueSchema.parse({
              id: issueId,
              type: "EYELINE_MISMATCH",
              severity: "WARNING",
              shotAId: shotA.shotId,
              shotBId: shotB.shotId,
              timestampSeconds: shotB.timestampSeconds,
              description: `Eyeline collision: both subjects looking in same horizontal direction (${aLooksRight ? "RIGHT" : "LEFT"}).`,
              deltaValue: Math.abs(shotA.subjectGazeAngleDeg - shotB.subjectGazeAngleDeg),
              suggestedAction: "REVERSE_CUT",
            })
          );
        }
      }

      // 4. Audit Scale Jump Disparity (REQ-005)
      if (shotA.scale === shotB.scale && (shotA.scale === "CLOSE_UP" || shotA.scale === "EXTREME_CLOSE")) {
        const issueId = `issue_${i}_scale_${crypto.createHash("sha256").update(`${i}_scale_${shotA.shotId}_${shotB.shotId}`).digest("hex").slice(0, 8)}`;
        issues.push(
          ContinuityAuditIssueSchema.parse({
            id: issueId,
            type: "SCALE_JUMP_DISPARITY",
            severity: "INFO",
            shotAId: shotA.shotId,
            shotBId: shotB.shotId,
            timestampSeconds: shotB.timestampSeconds,
            description: `Consecutive identical tight framing (${shotA.scale} -> ${shotB.scale}) may produce jarring jump cut.`,
            suggestedAction: "INSERT_CUTAWAY",
          })
        );
      }

      // 5. Audit Color Temperature Drift (REQ-018)
      if (shotA.colorTemperatureK !== undefined && shotB.colorTemperatureK !== undefined) {
        const tempDelta = Math.abs(shotA.colorTemperatureK - shotB.colorTemperatureK);
        if (tempDelta >= colorTempThresholdK) {
          const issueId = `issue_${i}_color_${crypto.createHash("sha256").update(`${i}_color_${shotA.shotId}_${shotB.shotId}`).digest("hex").slice(0, 8)}`;
          issues.push(
            ContinuityAuditIssueSchema.parse({
              id: issueId,
              type: "COLOR_TEMPERATURE_DRIFT",
              severity: tempDelta > 1500 ? "WARNING" : "INFO",
              shotAId: shotA.shotId,
              shotBId: shotB.shotId,
              timestampSeconds: shotB.timestampSeconds,
              description: `Color temperature delta of ${tempDelta.toFixed(0)}K (${shotA.colorTemperatureK}K -> ${shotB.colorTemperatureK}K) exceeds ${colorTempThresholdK}K threshold.`,
              deltaValue: tempDelta,
              suggestedAction: "GRADE_MATCH",
            })
          );
        }
      }
    }

    // Compute Continuity Score
    let deduction = 0;
    let hasBlocking = false;

    for (const issue of issues) {
      if (issue.severity === "BLOCKING") {
        deduction += 25;
        hasBlocking = true;
      } else if (issue.severity === "WARNING") {
        deduction += 10;
      } else if (issue.severity === "INFO") {
        deduction += 3;
      }
    }

    const rawScore = 100.0 - deduction;
    const continuityScore = Math.max(0.0, Math.min(100.0, rawScore));
    const passed = continuityScore >= 70.0 && !hasBlocking;

    return ContinuityAuditReportSchema.parse({
      sequenceId,
      continuityScore: Number(continuityScore.toFixed(2)),
      issues,
      passed,
      analyzedShotCount: shots.length,
    });
  }
}

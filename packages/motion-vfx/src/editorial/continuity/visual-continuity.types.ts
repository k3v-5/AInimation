import { z } from "zod";
import { ShotClassificationScaleSchema } from "../contracts/knowledge-graph.types.js";

/**
 * REQ-005, REQ-017, REQ-056: Types of continuity issues detectable in montage.
 */
export const ContinuityIssueTypeSchema = z.enum([
  "AXIS_CROSSING_180",        // Camera crossed the 180-degree line of action
  "EYELINE_MISMATCH",         // Subject eyelines collide or look in identical incorrect directions
  "SCREEN_DIRECTION_BREAK",   // Movement vector flipped without a neutral bridge shot
  "SCALE_JUMP_DISPARITY",     // Disorienting or monotonous scale transitions (e.g. CU -> identical CU)
  "COLOR_TEMPERATURE_DRIFT",  // Color temperature delta > threshold (e.g. 800K)
  "CAMERA_MOTION_COLLISION",  // Unmotivated fast motion vector collision
]);

export type ContinuityIssueType = z.infer<typeof ContinuityIssueTypeSchema>;

export const ContinuitySeveritySchema = z.enum([
  "INFO",
  "WARNING",
  "BLOCKING",
]);

export type ContinuitySeverity = z.infer<typeof ContinuitySeveritySchema>;

export const ContinuitySuggestedActionSchema = z.enum([
  "INSERT_CUTAWAY",
  "USE_BRIDGE_SHOT",
  "GRADE_MATCH",
  "REVERSE_CUT",
  "ALLOW_WITH_EXPLANATION",
]);

export type ContinuitySuggestedAction = z.infer<typeof ContinuitySuggestedActionSchema>;

/**
 * Single continuity issue audit entry.
 */
export const ContinuityAuditIssueSchema = z.object({
  id: z.string().min(1),
  type: ContinuityIssueTypeSchema,
  severity: ContinuitySeveritySchema,
  shotAId: z.string().min(1),
  shotBId: z.string().min(1),
  timestampSeconds: z.number().min(0),
  description: z.string().min(1),
  deltaValue: z.number().optional(), // e.g. color temp delta in Kelvins or degree angle
  suggestedAction: ContinuitySuggestedActionSchema,
});

export type ContinuityAuditIssue = z.infer<typeof ContinuityAuditIssueSchema>;

/**
 * Complete Continuity Audit Report for a sequence.
 */
export const ContinuityAuditReportSchema = z.object({
  sequenceId: z.string().min(1),
  continuityScore: z.number().min(0.0).max(100.0), // 100 = perfect continuity
  issues: z.array(ContinuityAuditIssueSchema),
  passed: z.boolean(),
  analyzedShotCount: z.number().int().min(0),
});

export type ContinuityAuditReport = z.infer<typeof ContinuityAuditReportSchema>;

/**
 * Metadata profile of an individual shot needed for continuity analysis.
 */
export interface ShotContinuityMetadata {
  shotId: string;
  assetId: string;
  timestampSeconds: number;
  durationSeconds: number;
  scale: z.infer<typeof ShotClassificationScaleSchema>;
  subjectPositionX?: number; // Normalized [0, 1] left to right
  subjectGazeAngleDeg?: number; // 0 = straight, -45 = looking left, +45 = looking right
  screenMotionDirection?: "LEFT_TO_RIGHT" | "RIGHT_TO_LEFT" | "TOWARDS_CAMERA" | "AWAY_FROM_CAMERA" | "STATIC";
  colorTemperatureK?: number; // Estimated color temperature in Kelvin (e.g. 5600K)
  cameraAzimuthDeg?: number; // Camera angle around subject (0-360)
  cameraMotionType?: "STATIC" | "PAN" | "TILT" | "DOLLY" | "WHIP" | "HANDHELD";
}

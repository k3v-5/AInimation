import { z } from "zod";
import { SilenceRegion, SilenceRegionSchema } from "./speech.types.js";

/** Segmento de A-Roll retenido tras eliminación de silencios */
export interface RetainedSegment {
  id: string;
  sourceStartSeconds: number;
  sourceEndSeconds: number;
  timelineStartSeconds: number;
  timelineEndSeconds: number;
  durationSeconds: number;
  hasSpeech: boolean;
}

export const RetainedSegmentSchema = z.object({
  id: z.string().min(1),
  sourceStartSeconds: z.number().min(0),
  sourceEndSeconds: z.number().min(0),
  timelineStartSeconds: z.number().min(0),
  timelineEndSeconds: z.number().min(0),
  durationSeconds: z.number().min(0),
  hasSpeech: z.boolean(),
});

/** Decisión individual de corte o preservación */
export interface JumpCutDecision {
  id: string;
  sourceCutTimeSeconds: number;
  timelineCutTimeSeconds: number;
  action: "CUT_SILENCE" | "PRESERVE_NARRATIVE_PAUSE" | "ATTENUATE_BREATH" | "KEEP_TRANSITION";
  silenceDurationRemovedSeconds: number;
  microCrossfadeSeconds: number; // 0.010 s (10 ms)
  reason: string;
}

export const JumpCutDecisionSchema = z.object({
  id: z.string().min(1),
  sourceCutTimeSeconds: z.number().min(0),
  timelineCutTimeSeconds: z.number().min(0),
  action: z.enum(["CUT_SILENCE", "PRESERVE_NARRATIVE_PAUSE", "ATTENUATE_BREATH", "KEEP_TRANSITION"]),
  silenceDurationRemovedSeconds: z.number().min(0),
  microCrossfadeSeconds: z.number().min(0).default(0.010),
  reason: z.string(),
});

/** Decisión de Punch-In dinámico sobre un punto de atención */
export interface PunchInDecision {
  id: string;
  timelineStartSeconds: number;
  timelineEndSeconds: number;
  holdDurationSeconds: number;
  targetScale: number; // Ej. 1.15 (115%)
  originScale: number; // 1.00 (100%)
  focalPointNormalized: {
    x: number; // [0, 1]
    y: number; // [0, 1]
  };
  trigger: "EMPHASIS_KEYWORD" | "TOPIC_SHIFT" | "NARRATIVE_CLIMAX" | "MANUAL_OVERRIDE";
  isSuppressedByBRoll: boolean; // Si B-Roll cubre el segmento, se omite (Doc 16 Sec 78)
}

export const PunchInDecisionSchema = z.object({
  id: z.string().min(1),
  timelineStartSeconds: z.number().min(0),
  timelineEndSeconds: z.number().min(0),
  holdDurationSeconds: z.number().min(0),
  targetScale: z.number().min(1.0).max(1.30).default(1.15),
  originScale: z.number().min(0.5).max(1.5).default(1.00),
  focalPointNormalized: z.object({
    x: z.number().min(0).max(1),
    y: z.number().min(0).max(1),
  }),
  trigger: z.enum(["EMPHASIS_KEYWORD", "TOPIC_SHIFT", "NARRATIVE_CLIMAX", "MANUAL_OVERRIDE"]),
  isSuppressedByBRoll: z.boolean().default(false),
});

/** Estadísticas cuantitativas del proceso de jump cut */
export interface JumpCutStatistics {
  originalDurationSeconds: number;
  editedDurationSeconds: number;
  totalTimeSavedSeconds: number;
  percentSaved: number;
  cutsCount: number;
  pausesPreservedCount: number;
  breathsAttenuatedCount: number;
  punchInsAppliedCount: number;
}

export const JumpCutStatisticsSchema = z.object({
  originalDurationSeconds: z.number().min(0),
  editedDurationSeconds: z.number().min(0),
  totalTimeSavedSeconds: z.number().min(0),
  percentSaved: z.number().min(0).max(100),
  cutsCount: z.number().int().min(0),
  pausesPreservedCount: z.number().int().min(0),
  breathsAttenuatedCount: z.number().int().min(0),
  punchInsAppliedCount: z.number().int().min(0),
});

/** Plan maestro de edición por saltos de corte y encuadre */
export interface JumpCutPlan {
  projectId: string;
  sourceMediaId: string;
  retainedSegments: RetainedSegment[];
  decisions: JumpCutDecision[];
  punchIns: PunchInDecision[];
  statistics: JumpCutStatistics;
  silencesAnalyzed: SilenceRegion[];
}

export const JumpCutPlanSchema = z.object({
  projectId: z.string().min(1),
  sourceMediaId: z.string().min(1),
  retainedSegments: z.array(RetainedSegmentSchema),
  decisions: z.array(JumpCutDecisionSchema),
  punchIns: z.array(PunchInDecisionSchema),
  statistics: JumpCutStatisticsSchema,
  silencesAnalyzed: z.array(SilenceRegionSchema),
});

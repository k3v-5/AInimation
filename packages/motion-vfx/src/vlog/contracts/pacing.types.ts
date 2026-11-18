import { z } from "zod";
import { SupportedLocaleSchema } from "./language.types.js";
import { SupportedLocale } from "./vlog.constants.js";

/** Nivel de importancia narrativa de un segmento para tolerancia a desincronización */
export type SegmentImportance = "CRITICAL" | "HIGH" | "NORMAL" | "LOW";

export const SegmentImportanceSchema = z.enum(["CRITICAL", "HIGH", "NORMAL", "LOW"]);

/** Ancla temporal fija que no debe desplazarse durante la adaptación */
export interface TimingAnchor {
  id: string;
  sourceTimeSeconds: number;
  adaptedTimeSeconds: number;
  type: "CHAPTER_BOUNDARY" | "HOOK_DROP" | "VISUAL_PUNCH" | "MUSIC_DOWNBEAT";
  isImmutable: boolean;
}

export const TimingAnchorSchema = z.object({
  id: z.string().min(1),
  sourceTimeSeconds: z.number().min(0),
  adaptedTimeSeconds: z.number().min(0),
  type: z.enum(["CHAPTER_BOUNDARY", "HOOK_DROP", "VISUAL_PUNCH", "MUSIC_DOWNBEAT"]),
  isImmutable: z.boolean(),
});

/** Alineación calculada entre un segmento de voz y su representación visual */
export interface SegmentAlignment {
  narrativeSegmentId: string;
  voiceStartSeconds: number;
  voiceEndSeconds: number;
  visualStartSeconds: number;
  visualEndSeconds: number;
  driftSeconds: number; // visualStart - voiceStart
  isWithinDriftTolerance: boolean; // |drift| <= 40ms
}

export const SegmentAlignmentSchema = z.object({
  narrativeSegmentId: z.string().min(1),
  voiceStartSeconds: z.number().min(0),
  voiceEndSeconds: z.number().min(0),
  visualStartSeconds: z.number().min(0),
  visualEndSeconds: z.number().min(0),
  driftSeconds: z.number(),
  isWithinDriftTolerance: z.boolean(),
});

/** Ajuste editorial individual aplicado para sincronizar el ritmo */
export interface PacingAdjustment {
  segmentId: string;
  strategy:
    | "BROLL_EXTENDED"
    | "BROLL_TRIMMED"
    | "PAUSE_EXTENDED"
    | "PAUSE_COMPRESSED"
    | "TRANSITION_TIMED"
    | "VOICE_MICRO_STRETCH";
  appliedRatio: number; // Factor de estiramiento/compresión
  deltaSeconds: number;
  rationale: string;
}

export const PacingAdjustmentSchema = z.object({
  segmentId: z.string().min(1),
  strategy: z.enum([
    "BROLL_EXTENDED",
    "BROLL_TRIMMED",
    "PAUSE_EXTENDED",
    "PAUSE_COMPRESSED",
    "TRANSITION_TIMED",
    "VOICE_MICRO_STRETCH",
  ]),
  appliedRatio: z.number().positive(),
  deltaSeconds: z.number(),
  rationale: z.string(),
});

/** Conflicto temporal de pacing cuando la elasticidad no es suficiente */
export interface PacingConflict {
  segmentId: string;
  locale: SupportedLocale;
  unresolvedDeltaSeconds: number;
  requiredVoiceStretch: number; // Si > 1.05 o < 0.95
  severity: "WARNING" | "BLOCKING";
  suggestedAction: "EXTEND_BROLL_FURTHER" | "ADD_PAUSE" | "MANUAL_SCRIPT_EDIT";
}

export const PacingConflictSchema = z.object({
  segmentId: z.string().min(1),
  locale: SupportedLocaleSchema,
  unresolvedDeltaSeconds: z.number(),
  requiredVoiceStretch: z.number().positive(),
  severity: z.enum(["WARNING", "BLOCKING"]),
  suggestedAction: z.enum(["EXTEND_BROLL_FURTHER", "ADD_PAUSE", "MANUAL_SCRIPT_EDIT"]),
});

/** Solicitud de adaptación de ritmo para un idioma */
export interface PacingRequest {
  projectId: string;
  locale: SupportedLocale;
  sourceTimelineDurationSeconds: number;
  voiceDurationSeconds: number;
  allowStretchRange?: [number, number]; // Default [0.95, 1.05]
}

export const PacingRequestSchema = z.object({
  projectId: z.string().min(1),
  locale: SupportedLocaleSchema,
  sourceTimelineDurationSeconds: z.number().positive(),
  voiceDurationSeconds: z.number().positive(),
  allowStretchRange: z.tuple([z.number().min(0.80), z.number().max(1.20)]).optional(),
});

/** Resultado del cálculo de adaptación elástica */
export interface PacingResult {
  locale: SupportedLocale;
  adaptedDurationSeconds: number;
  deltaFromSourceSeconds: number;
  adjustments: PacingAdjustment[];
  alignments: SegmentAlignment[];
  conflicts: PacingConflict[];
  voiceStretchFactor: number; // Dentro de [0.95, 1.05]
  success: boolean;
}

export const PacingResultSchema = z.object({
  locale: SupportedLocaleSchema,
  adaptedDurationSeconds: z.number().positive(),
  deltaFromSourceSeconds: z.number(),
  adjustments: z.array(PacingAdjustmentSchema),
  alignments: z.array(SegmentAlignmentSchema),
  conflicts: z.array(PacingConflictSchema),
  voiceStretchFactor: z.number().min(0.85).max(1.15),
  success: z.boolean(),
});

import { z } from "zod";
import { FOOTAGE_TYPES, FootageType } from "./vlog.constants.js";

export { FootageType };

export const FootageTypeSchema = z.enum(FOOTAGE_TYPES);

/** Puntuaciones probabilísticas por categoría */
export interface ClassificationScores {
  aRoll: number; // [0.0, 1.0]
  bRoll: number;
  action: number;
  timelapse: number;
  screen: number;
  photo: number;
  other: number;
}

export const ClassificationScoresSchema = z.object({
  aRoll: z.number().min(0).max(1),
  bRoll: z.number().min(0).max(1),
  action: z.number().min(0).max(1),
  timelapse: z.number().min(0).max(1),
  screen: z.number().min(0).max(1),
  photo: z.number().min(0).max(1),
  other: z.number().min(0).max(1),
});

/** Evidencia que respalda la decisión de clasificación */
export interface ClassificationEvidence {
  hasVoiceActivity: boolean;
  voiceActivityRatio: number; // [0, 1]
  hasDominantFace: boolean;
  faceCoverageRatio: number;
  averageOpticalFlow: number;
  isStaticImage: boolean;
  aspectRatio: string;
  detectedTags: string[];
}

export const ClassificationEvidenceSchema = z.object({
  hasVoiceActivity: z.boolean(),
  voiceActivityRatio: z.number().min(0).max(1),
  hasDominantFace: z.boolean(),
  faceCoverageRatio: z.number().min(0).max(1),
  averageOpticalFlow: z.number().min(0),
  isStaticImage: z.boolean(),
  aspectRatio: z.string(),
  detectedTags: z.array(z.string()),
});

/** Resultado de clasificación editorial para un medio individual */
export interface FootageClassification {
  mediaId: string;
  primaryType: FootageType;
  confidence: number; // [0.0, 1.0]
  scores: ClassificationScores;
  evidence: ClassificationEvidence;
  recommendedRole: "A_ROLL_PRIMARY" | "B_ROLL_CUTAWAY" | "TRANSITION_STINGER" | "UNKNOWN";
  tags: string[];
}

export const FootageClassificationSchema = z.object({
  mediaId: z.string().min(1),
  primaryType: FootageTypeSchema,
  confidence: z.number().min(0).max(1),
  scores: ClassificationScoresSchema,
  evidence: ClassificationEvidenceSchema,
  recommendedRole: z.enum(["A_ROLL_PRIMARY", "B_ROLL_CUTAWAY", "TRANSITION_STINGER", "UNKNOWN"]),
  tags: z.array(z.string()),
});

/** Rango temporal sub-clip utilizable */
export interface ClipRange {
  assetId: string;
  startSeconds: number;
  endSeconds: number;
  durationSeconds: number;
}

export const ClipRangeSchema = z.object({
  assetId: z.string().min(1),
  startSeconds: z.number().min(0),
  endSeconds: z.number().min(0),
  durationSeconds: z.number().min(0),
}).refine((r) => r.endSeconds >= r.startSeconds, {
  message: "endSeconds must be >= startSeconds",
});

/** Desglose de puntuación de emparejamiento B-Roll (0 a 100) */
export interface BRollMatchScore {
  total: number; // [0, 100]
  semanticRelevance: number; // [0, 100]
  entityMatch: number;
  visualQuality: number;
  locationRelevance: number;
  activityRelevance: number;
  durationFit: number;
  noveltyPenalty: number; // [0, 100], mayor número = mayor penalización por repetición
}

export const BRollMatchScoreSchema = z.object({
  total: z.number().min(0).max(100),
  semanticRelevance: z.number().min(0).max(100),
  entityMatch: z.number().min(0).max(100),
  visualQuality: z.number().min(0).max(100),
  locationRelevance: z.number().min(0).max(100),
  activityRelevance: z.number().min(0).max(100),
  durationFit: z.number().min(0).max(100),
  noveltyPenalty: z.number().min(0).max(100),
});

/** Candidato individual a plano de apoyo B-Roll */
export interface BRollCandidate {
  candidateId: string;
  mediaId: string;
  subclipRange: ClipRange;
  score: BRollMatchScore;
  matchedTags: string[];
  rationale: string;
}

export const BRollCandidateSchema = z.object({
  candidateId: z.string().min(1),
  mediaId: z.string().min(1),
  subclipRange: ClipRangeSchema,
  score: BRollMatchScoreSchema,
  matchedTags: z.array(z.string()),
  rationale: z.string(),
});

/** Decisión de emparejamiento B-Roll para un segmento narrativo */
export interface BRollMatch {
  narrativeSegmentId: string;
  selectedCandidate: BRollCandidate;
  alternatives: BRollCandidate[];
  timelineStartSeconds: number;
  timelineEndSeconds: number;
  isExclusiveCover: boolean; // Si cubre 100% del A-Roll, suprime Punch-In
}

export const BRollMatchSchema = z.object({
  narrativeSegmentId: z.string().min(1),
  selectedCandidate: BRollCandidateSchema,
  alternatives: z.array(BRollCandidateSchema),
  timelineStartSeconds: z.number().min(0),
  timelineEndSeconds: z.number().min(0),
  isExclusiveCover: z.boolean(),
});

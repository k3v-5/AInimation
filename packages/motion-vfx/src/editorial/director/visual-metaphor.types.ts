import { z } from "zod";

export const AbstractNarrativeConceptSchema = z.enum([
  "ISOLATION",
  "CONFLICT",
  "LOSS",
  "HOPE",
  "BUREAUCRACY",
  "POWER",
  "UNCERTAINTY",
  "FREEDOM",
  "CONFINEMENT",
  "TRANSFORMATION",
]);

export type AbstractNarrativeConcept = z.infer<typeof AbstractNarrativeConceptSchema>;

export interface VisualMetaphorPattern {
  concept: AbstractNarrativeConcept;
  requiredFraming?: ("WIDE" | "MEDIUM" | "CLOSE_UP" | "EXTREME_CLOSE")[];
  lightingMood?: ("DAYLIGHT" | "NIGHT" | "GOLDEN_HOUR" | "DRAMATIC_LOW_KEY" | "HIGH_KEY")[];
  cameraMotion?: ("STATIC" | "PAN" | "TILT" | "DOLLY" | "TRACKING" | "HANDHELD")[];
  requiredKeywords: string[];
  compositionHint: string;
}

export interface MetaphorCandidate {
  metaphorId: string;
  abstractConcept: AbstractNarrativeConcept;
  visualPattern: string;
  candidateShotId: string;
  sourceAssetId: string;
  semanticScore: number;
  narrativeFit: number;
  visualFit: number;
  continuityFit: number;
  compositeScore: number;
  explanation: string;
  confidence: number;
  requiresHumanReview: boolean;
}

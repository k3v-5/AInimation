import { z } from "zod";

/**
 * REQ-030 / REQ-081 §33: Perfil de Configuración para Editorial QA Linter & Auditoría
 */

export const EditorialQAProfileSchema = z.object({
  humanReviewConfidenceThreshold: z.number().min(0).max(1).default(0.70),
  failOnWarnings: z.boolean().default(false),
  failOnSuggestions: z.boolean().default(false),
  cognitiveLoadThreshold: z.number().min(0).max(1).default(0.85),
  cognitiveLoadMinDurationSeconds: z.number().min(0).default(3.0),
  pacingWarningThreshold: z.number().min(0).default(0.30),
  attentionWarningThreshold: z.number().min(0).default(0.40),
  mandatoryNarrativeBeats: z.array(z.string()).default(["HOOK", "CLIMAX"]),
  requiredEvidenceForClaims: z.boolean().default(true),
});

export type EditorialQAProfile = z.infer<typeof EditorialQAProfileSchema>;

export const DEFAULT_EDITORIAL_QA_PROFILE: EditorialQAProfile = {
  humanReviewConfidenceThreshold: 0.70,
  failOnWarnings: false,
  failOnSuggestions: false,
  cognitiveLoadThreshold: 0.85,
  cognitiveLoadMinDurationSeconds: 3.0,
  pacingWarningThreshold: 0.30,
  attentionWarningThreshold: 0.40,
  mandatoryNarrativeBeats: ["HOOK", "CLIMAX"],
  requiredEvidenceForClaims: true,
};

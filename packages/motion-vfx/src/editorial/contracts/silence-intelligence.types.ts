import { z } from "zod";

/**
 * REQ-006 & REQ-068: Semantic Silence Typology.
 */
export const SilenceTypeSchema = z.enum([
  "FILLER_SILENCE",   // Dead space, hesitation, mumbling -> candidate for trim
  "BREATH",           // Natural respiratory intake
  "THINKING_PAUSE",   // Cognitive processing, reflection
  "DRAMATIC_PAUSE",   // High-tension, narrative emphasis, sacred silence
  "ROOM_TONE",        // Ambient room noise bed
  "EDITING_GAP",      // Artificial gap produced by edits
  "NATURAL_PAUSE",    // Punctuation pause (commas, periods)
]);

export type SilenceType = z.infer<typeof SilenceTypeSchema>;

/**
 * Action decided for a given silence.
 */
export const SilenceDecisionActionSchema = z.enum([
  "TRIM",                      // Remove or shorten
  "KEEP",                      // Keep untouched
  "ATTENUATE",                 // Lower gain
  "REPLACE_WITH_ROOM_TONE",    // Fill with natural ambient bed
]);

export type SilenceDecisionAction = z.infer<typeof SilenceDecisionActionSchema>;

/**
 * REQ-006: Classified Silence Segment.
 */
export const ClassifiedSilenceSchema = z.object({
  id: z.string().min(1),
  startSeconds: z.number().min(0),
  endSeconds: z.number().min(0),
  durationSeconds: z.number().min(0),
  type: SilenceTypeSchema,
  confidence: z.number().min(0.0).max(1.0),
  decision: SilenceDecisionActionSchema,
  targetDurationSeconds: z.number().min(0),
  reasoning: z.string().min(1),
  sourceAudioTrackId: z.string().optional(),
});

export type ClassifiedSilence = z.infer<typeof ClassifiedSilenceSchema>;

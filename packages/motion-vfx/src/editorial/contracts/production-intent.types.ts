import { z } from "zod";
import { EditorialGenreSchema } from "./content-profile.types.js";

/**
 * REQ-002: Canonical Production Intent Schema.
 * Defines project purpose, audience, platform target, and creative objectives.
 */
export const ProductionObjectiveSchema = z.enum([
  "INFORM",
  "EMOTE",
  "PERSUADE",
  "ENTERTAIN",
  "DOCUMENT",
  "EDUCATE",
]);

export type ProductionObjective = z.infer<typeof ProductionObjectiveSchema>;

export const AudienceLevelSchema = z.enum([
  "GENERAL",
  "EXPERT",
  "YOUTH",
  "BUSINESS",
  "ACADEMIC",
]);

export type AudienceLevel = z.infer<typeof AudienceLevelSchema>;

export const PlatformTargetSchema = z.enum([
  "YOUTUBE_16x9",
  "VERTICAL_SOCIAL", // TikTok, Reels, Shorts
  "BROADCAST",
  "CINEMA",
  "CORPORATE_WEB",
]);

export type PlatformTarget = z.infer<typeof PlatformTargetSchema>;

export const PacingPreferenceSchema = z.enum([
  "CONTEMPLATIVE",
  "MODERATE",
  "AGGRESSIVE",
  "DYNAMIC_WAVE",
]);

export type PacingPreference = z.infer<typeof PacingPreferenceSchema>;

export const ProductionIntentSchema = z.object({
  projectId: z.string().min(1),
  format: z.union([EditorialGenreSchema, z.literal("AUTO")]),
  primaryObjective: ProductionObjectiveSchema,
  secondaryObjective: ProductionObjectiveSchema.optional(),
  audience: AudienceLevelSchema.default("GENERAL"),
  platform: PlatformTargetSchema.default("YOUTUBE_16x9"),
  targetDurationSeconds: z.number().positive().optional(),
  language: z.string().default("es-MX"),
  tone: z.string().default("NEUTRAL"),
  pacingPreference: PacingPreferenceSchema.default("MODERATE"),
  visualDensity: z.number().min(0.0).max(1.0).default(0.5),
  narrationDensity: z.number().min(0.0).max(1.0).default(0.7),
  brollDensity: z.number().min(0.0).max(1.0).default(0.6),
});

export type ProductionIntent = z.infer<typeof ProductionIntentSchema>;

import { z } from "zod";

/**
 * REQ-088: Speaker Lower Third Overlay.
 */
export const SpeakerLowerThirdSchema = z.object({
  id: z.string().min(1),
  speakerId: z.string().min(1),
  fullName: z.string().min(1),
  roleOrTitle: z.string().min(1),
  affiliation: z.string().optional(),
  timelineStartSeconds: z.number().nonnegative(),
  timelineEndSeconds: z.number().nonnegative(),
  style: z.enum(["MINIMAL_EDITORIAL", "TIME_INSIGNIA", "BROADCAST_SLATE"]).default("TIME_INSIGNIA"),
});

export type SpeakerLowerThird = z.infer<typeof SpeakerLowerThirdSchema>;

/**
 * REQ-089: Credits Roll and Cards Entry.
 */
export const CreditEntrySchema = z.object({
  role: z.string().min(1),
  names: z.array(z.string().min(1)),
  notes: z.string().optional(),
});

export type CreditEntry = z.infer<typeof CreditEntrySchema>;

export const CreditSectionSchema = z.object({
  sectionTitle: z.string().min(1),
  entries: z.array(CreditEntrySchema),
});

export type CreditSection = z.infer<typeof CreditSectionSchema>;

/**
 * Master Credits & Attribution Plan.
 */
export const CreditsPlanSchema = z.object({
  projectId: z.string().min(1),
  speakerLowerThirds: z.array(SpeakerLowerThirdSchema),
  archivalAttributions: z.array(
    z.object({
      text: z.string().min(1),
      timelineStartSeconds: z.number().nonnegative(),
      timelineEndSeconds: z.number().nonnegative(),
    })
  ),
  endCredits: z.array(CreditSectionSchema),
  endCreditsMode: z.enum(["CARDS", "CRAWL", "STATIC_SLATE"]).default("CARDS"),
  estimatedEndCreditsDurationSeconds: z.number().positive(),
  checksumSha256: z.string().length(64),
});

export type CreditsPlan = z.infer<typeof CreditsPlanSchema>;

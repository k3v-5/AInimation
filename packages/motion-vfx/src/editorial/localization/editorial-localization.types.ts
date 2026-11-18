import { z } from "zod";

/**
 * REQ-071: Official supported locales in the editorial suite.
 */
export const OfficialEditorialLocaleSchema = z.enum([
  "es-MX",
  "es-ES",
  "en-US",
  "en-GB",
  "pt-BR",
  "fr-FR",
  "de-DE",
]);

export type OfficialEditorialLocale = z.infer<typeof OfficialEditorialLocaleSchema>;

/**
 * Localized subtitle cue.
 */
export const LocalizedSubtitleCueSchema = z.object({
  startSeconds: z.number().min(0),
  endSeconds: z.number().min(0),
  text: z.string().min(1),
});

export type LocalizedSubtitleCue = z.infer<typeof LocalizedSubtitleCueSchema>;

/**
 * REQ-072: Audio and Subtitle pair for a specific language locale.
 */
export const LocalizedTrackPairSchema = z.object({
  locale: OfficialEditorialLocaleSchema,
  audioDialogueAssetId: z.string().min(1),
  subtitleCues: z.array(LocalizedSubtitleCueSchema).default([]),
  timingOffsetSeconds: z.number().default(0.0),
});

export type LocalizedTrackPair = z.infer<typeof LocalizedTrackPairSchema>;

/**
 * REQ-073: Master multi-language localization package.
 */
export const EditorialLocalizationPackageSchema = z.object({
  masterProjectId: z.string().min(1),
  supportedLocales: z.array(OfficialEditorialLocaleSchema),
  variants: z.array(LocalizedTrackPairSchema),
  checksum: z.string().length(64),
});

export type EditorialLocalizationPackage = z.infer<typeof EditorialLocalizationPackageSchema>;

import { z } from "zod";

/**
 * REQ-026: Supported cutdown duration targets.
 */
export const CutdownTargetSchema = z.enum([
  "FULL_LENGTH",     // Complete master timeline
  "CUTDOWN_60S",     // 60-second summary
  "CUTDOWN_30S",     // 30-second commercial / social hook
  "CUTDOWN_15S",     // 15-second teaser / story / ad
  "HOOK_TEASER_6S",  // 6-second bumper / pre-roll
]);

export type CutdownTarget = z.infer<typeof CutdownTargetSchema>;

/**
 * Target aspect ratios for packaging.
 */
export const AspectRatioTargetSchema = z.enum([
  "16:9",
  "9:16",
  "1:1",
  "4:5",
  "21:9",
]);

export type AspectRatioTarget = z.infer<typeof AspectRatioTargetSchema>;

/**
 * Canonical dimensions for each aspect ratio target.
 */
export const EDITORIAL_ASPECT_RATIO_DIMENSIONS: Record<AspectRatioTarget, { width: number; height: number }> = {
  "16:9": { width: 1920, height: 1080 },
  "9:16": { width: 1080, height: 1920 },
  "1:1": { width: 1080, height: 1080 },
  "4:5": { width: 1080, height: 1350 },
  "21:9": { width: 2560, height: 1080 },
};

/**
 * REQ-027: Editorial Variant Plan specifying the parameters of a compiled variant.
 */
export const EditorialVariantPlanSchema = z.object({
  variantId: z.string().min(1),
  masterProjectId: z.string().min(1),
  cutdownTarget: CutdownTargetSchema,
  aspectRatio: AspectRatioTargetSchema,
  targetDurationSeconds: z.number().positive(),
  actualDurationSeconds: z.number().positive(),
  retainedClipIds: z.array(z.string()),
  checksum: z.string().length(64), // SHA-256 seal of the variant
});

export type EditorialVariantPlan = z.infer<typeof EditorialVariantPlanSchema>;

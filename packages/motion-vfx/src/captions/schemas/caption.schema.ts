import { z } from "zod";

export const ColorRGBASchema = z.object({
  r: z.number().finite().min(0).max(1),
  g: z.number().finite().min(0).max(1),
  b: z.number().finite().min(0).max(1),
  a: z.number().finite().min(0).max(1).optional(),
});

export const StrokeStyleSchema = z.object({
  width: z.number().finite().nonnegative(),
  color: ColorRGBASchema,
  opacity: z.number().finite().min(0).max(1).optional(),
});

export const ShadowStyleSchema = z.object({
  offsetX: z.number().finite(),
  offsetY: z.number().finite(),
  blur: z.number().finite().nonnegative(),
  color: ColorRGBASchema,
  opacity: z.number().finite().min(0).max(1).optional(),
});

export const BackgroundStyleSchema = z.object({
  color: ColorRGBASchema,
  opacity: z.number().finite().min(0).max(1).optional(),
  padding: z
    .object({
      top: z.number().finite().nonnegative(),
      right: z.number().finite().nonnegative(),
      bottom: z.number().finite().nonnegative(),
      left: z.number().finite().nonnegative(),
    })
    .optional(),
  cornerRadius: z.number().finite().nonnegative().optional(),
});

export const CaptionStyleSchema = z.object({
  fontFamily: z.string().min(1),
  fontSize: z.number().finite().positive(),
  fontWeight: z.number().finite().int().min(100).max(900),
  color: ColorRGBASchema,
  stroke: StrokeStyleSchema.optional(),
  shadow: ShadowStyleSchema.optional(),
  background: BackgroundStyleSchema.optional(),
  alignment: z.enum(["left", "center", "right"]),
  letterSpacing: z.number().finite().optional(),
  lineHeight: z.number().finite().positive().optional(),
  textTransform: z.enum(["none", "uppercase", "lowercase", "capitalize"]).optional(),
});

export const ProsodySignalsSchema = z.object({
  energy: z.number().finite().min(0).max(1).optional(),
  pitch: z.number().finite().optional(),
  speakingRate: z.number().finite().nonnegative().optional(),
  pauseBefore: z.number().finite().nonnegative().optional(),
  pauseAfter: z.number().finite().nonnegative().optional(),
});

export const WordAnimationConfigSchema = z.object({
  type: z.enum(["popScale", "glowPulse", "colorHighlight", "shake", "none"]),
  duration: z.number().finite().nonnegative().optional(),
  intensity: z.number().finite().min(0).max(1).optional(),
  color: ColorRGBASchema.optional(),
  easing: z.string().optional(),
  seed: z.number().finite().int().optional(),
});

export const EmphasisDecisionSchema = z.object({
  isEmphasized: z.boolean(),
  score: z.number().finite().min(0).max(1),
  reasons: z.array(z.string()),
  priority: z.number().finite().int().min(1).max(10),
  recommendedStyle: z.string().optional(),
  recommendedAnimation: z.enum(["popScale", "glowPulse", "colorHighlight", "shake", "none"]).optional(),
  recommendedEmojiTag: z.string().optional(),
});

export const CaptionWordSchema = z
  .object({
    id: z.string().min(1),
    text: z.string(),
    start: z.number().finite().nonnegative(),
    end: z.number().finite().nonnegative(),
    index: z.number().finite().int().nonnegative().optional(),
    confidence: z.number().finite().min(0).max(1).optional(),
    prosody: ProsodySignalsSchema.optional(),
    emphasis: EmphasisDecisionSchema.optional(),
    animation: WordAnimationConfigSchema.optional(),
  })
  .refine((w) => w.end >= w.start, {
    message: "Word end time must be greater than or equal to start time",
  });

export const CaptionSegmentSchema = z
  .object({
    id: z.string().min(1),
    start: z.number().finite().nonnegative(),
    end: z.number().finite().nonnegative(),
    text: z.string(),
    words: z.array(CaptionWordSchema),
    timingPrecision: z.enum(["segment", "word"]).optional(),
  })
  .refine((s) => s.end > s.start, {
    message: "Segment end time must be strictly greater than start time",
  });

export const CaptionDocumentSchema = z
  .object({
    id: z.string().min(1),
    duration: z.number().finite().nonnegative(),
    segments: z.array(CaptionSegmentSchema),
    timingPrecision: z.enum(["segment", "word"]).optional(),
    defaultStyle: CaptionStyleSchema.optional(),
    safeZoneProfile: z.string().optional(),
    metadata: z.record(z.any()).optional(),
    schemaVersion: z.string().default("1.6.0"),
  })
  .refine(
    (doc) => {
      for (let i = 0; i < doc.segments.length - 1; i++) {
        if (doc.segments[i + 1].start < doc.segments[i].start) {
          return false;
        }
      }
      return true;
    },
    {
      message: "Segments must be in ascending chronological order",
    }
  );

export const SafeZoneProfileSchema = z.object({
  id: z.string().min(1),
  name: z.string().min(1),
  version: z.string().default("2026.1"),
  canvasWidth: z.number().finite().positive(),
  canvasHeight: z.number().finite().positive(),
  topInset: z.number().finite().nonnegative(),
  bottomInset: z.number().finite().nonnegative(),
  leftInset: z.number().finite().nonnegative(),
  rightInset: z.number().finite().nonnegative(),
  forbiddenRegions: z
    .array(
      z.object({
        x: z.number().finite(),
        y: z.number().finite(),
        width: z.number().finite().positive(),
        height: z.number().finite().positive(),
      })
    )
    .optional(),
  source: z.string().optional(),
  confidence: z.number().finite().min(0).max(1).optional(),
});

import { z } from "zod";

export const CreateVideoFromScriptSchema = z.object({
  script: z
    .string()
    .min(1, "Script cannot be empty")
    .max(250000, "Script exceeds maximum allowed length (250,000 characters)"),
  styleId: z.string().default("fast-tiktok"),
  aspectRatio: z.enum(["9:16", "16:9", "1:1"]).default("9:16"),
  durationTarget: z.number().finite().positive().max(7200).default(30),
  resolution: z
    .object({
      width: z.number().finite().positive().max(7680),
      height: z.number().finite().positive().max(7680),
    })
    .optional(),
  fps: z.number().finite().positive().max(120).default(30),
  language: z.string().default("es"),
  captionPreset: z
    .enum(["hormozi-impact", "beast-clean", "vox-minimal", "karaoke-gradient", "neon-glow"])
    .optional(),
  seed: z.number().int().default(42),
  dryRun: z.boolean().default(false),
});

export const ExportAfterEffectsJSXSchema = z.object({
  projectId: z.string().min(1, "projectId is required"),
  revisionId: z.string().optional(),
  outputPath: z.string().optional(),
  strict: z.boolean().default(false),
  dryRun: z.boolean().default(false),
});

export const GetTimelinePreviewFrameSchema = z.object({
  projectId: z.string().min(1, "projectId is required"),
  revisionId: z.string().optional(),
  time: z.number().finite().nonnegative(),
  width: z.number().finite().positive().optional(),
  height: z.number().finite().positive().optional(),
});

export const ApplyViralCaptionStyleSchema = z.object({
  projectId: z.string().min(1, "projectId is required"),
  revisionId: z.string().optional(),
  preset: z.enum(["hormozi-impact", "beast-clean", "vox-minimal", "karaoke-gradient", "neon-glow"]),
  overrides: z
    .object({
      fontSize: z.number().finite().positive().optional(),
      color: z
        .object({
          r: z.number().min(0).max(1),
          g: z.number().min(0).max(1),
          b: z.number().min(0).max(1),
          a: z.number().min(0).max(1).optional(),
        })
        .optional(),
      highlightColor: z
        .object({
          r: z.number().min(0).max(1),
          g: z.number().min(0).max(1),
          b: z.number().min(0).max(1),
          a: z.number().min(0).max(1).optional(),
        })
        .optional(),
    })
    .optional(),
  safeZoneProfile: z.string().optional(),
});

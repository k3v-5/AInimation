import { z } from "zod";

export const ManifestSchema = z.object({
  schemaVersion: z.literal("1.8.0"),
  projectId: z.string().min(1),
  revisionId: z.string().min(1),
  projectHash: z.string().length(64),
  engineVersion: z.string().min(1),
  duration: z.number().nonnegative(),
  resolution: z.object({
    width: z.number().int().positive(),
    height: z.number().int().positive(),
  }),
  fps: z.number().positive(),
  compositionCount: z.number().int().nonnegative(),
  layerCount: z.number().int().nonnegative(),
  assetCount: z.number().int().nonnegative(),
  exports: z.array(
    z.object({
      format: z.string(),
      path: z.string(),
      hash: z.string(),
      sizeBytes: z.number().nonnegative(),
      target: z.string(),
    })
  ),
  manifestHash: z.string().length(64),
  createdAt: z.string().optional(),
});

export type Manifest = z.infer<typeof ManifestSchema>;

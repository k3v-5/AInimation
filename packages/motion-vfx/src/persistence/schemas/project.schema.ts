import { z } from "zod";

export const ProjectMetadataSchema = z.object({
  name: z.string().min(1).max(256),
  description: z.string().max(2000).optional(),
  author: z.string().max(256).optional(),
  tags: z.array(z.string().max(64)).max(50).optional(),
  custom: z.record(z.unknown()).optional(),
});

export type ProjectMetadata = z.infer<typeof ProjectMetadataSchema>;

export const ProjectSummarySchema = z.object({
  projectId: z.string().min(1),
  name: z.string(),
  headRevisionId: z.string(),
  revisionCount: z.number().int().nonnegative(),
  duration: z.number().nonnegative(),
  width: z.number().int().positive(),
  height: z.number().int().positive(),
  fps: z.number().positive(),
  updatedAt: z.string().optional(),
});

export type ProjectSummary = z.infer<typeof ProjectSummarySchema>;

export const ProjectFileSchema = z.object({
  schemaVersion: z.literal("1.8.0"),
  engineVersion: z.string().min(1),
  projectId: z.string().min(1),
  headRevisionId: z.string().min(1),
  metadata: ProjectMetadataSchema,
  project: z.record(z.unknown()), // Canonical Project IR
  contentHash: z.string().length(64),
  createdAt: z.string().optional(),
  updatedAt: z.string().optional(),
});

export type ProjectFile = z.infer<typeof ProjectFileSchema>;

import { z } from "zod";

/**
 * Límites de recursos centralizados para evitar proyectos patológicos (Fase 18).
 */
export const RuntimeLimits = {
  MAX_PROJECT_JSON_SIZE: 50 * 1024 * 1024, // 50MB
  MAX_LAYERS: 5000,
  MAX_ELEMENTS: 5000,
  MAX_KEYFRAMES_PER_PROPERTY: 10000,
  MAX_TOTAL_KEYFRAMES: 100000,
  MAX_ASSETS: 1000,
  MAX_CAPTIONS: 10000,
  MAX_WORDS_PER_CAPTION: 50000,
  MAX_SCRIPT_LENGTH: 100000,
  MAX_STRING_LENGTH: 10000,
  MAX_JSON_DEPTH: 32,
  MAX_OPERATION_DURATION_MS: 300000, // 5 minutos
  LOCK_TIMEOUT_MS: 10000,
  LOCK_STALE_AGE_MS: 60000,
};

export const RuntimeConfigSchema = z.object({
  storageRoot: z.string().min(1),
  assetRoot: z.string().optional(),
  enableRecovery: z.boolean().default(true),
  enableJournal: z.boolean().default(true),
  strictValidation: z.boolean().default(true),
  maxLayers: z.number().int().positive().default(RuntimeLimits.MAX_LAYERS),
  maxKeyframes: z.number().int().positive().default(RuntimeLimits.MAX_TOTAL_KEYFRAMES),
  maxAssets: z.number().int().positive().default(RuntimeLimits.MAX_ASSETS),
  maxOperationDurationMs: z.number().int().positive().default(RuntimeLimits.MAX_OPERATION_DURATION_MS),
  lockTimeoutMs: z.number().int().positive().default(RuntimeLimits.LOCK_TIMEOUT_MS),
});

export type RuntimeConfig = z.infer<typeof RuntimeConfigSchema>;

export const ProjectMetadataSchema = z.object({
  name: z.string().min(1).max(RuntimeLimits.MAX_STRING_LENGTH),
  description: z.string().max(RuntimeLimits.MAX_STRING_LENGTH).optional(),
  author: z.string().max(RuntimeLimits.MAX_STRING_LENGTH).optional(),
  tags: z.array(z.string().max(100)).max(100).optional(),
  custom: z.record(z.unknown()).optional(),
});

export type ProjectMetadata = z.infer<typeof ProjectMetadataSchema>;

export const ProjectEnvelopeSchema = z.object({
  schemaVersion: z.string().min(1),
  engineVersion: z.string().min(1),
  projectId: z.string().min(1),
  revisionId: z.string().min(1),
  createdAt: z.string().min(1),
  updatedAt: z.string().min(1),
  contentHash: z.string().min(64).max(64),
  project: z.record(z.unknown()),
  metadata: ProjectMetadataSchema,
  migrations: z
    .object({
      originalSchemaVersion: z.string(),
      migratedAt: z.string(),
      steps: z.array(z.string()),
    })
    .optional(),
});

export type ProjectEnvelopeType = z.infer<typeof ProjectEnvelopeSchema>;

export const CreateProjectInputSchema = z.object({
  name: z.string().min(1).max(256),
  description: z.string().max(1000).optional(),
  projectIR: z.record(z.unknown()).optional(),
  aspectRatio: z.enum(["16:9", "9:16", "1:1", "4:5"]).default("9:16"),
  width: z.number().int().min(16).max(7680).default(1080),
  height: z.number().int().min(16).max(7680).default(1920),
  fps: z.number().min(1).max(240).default(30),
  duration: z.number().min(0.1).max(7200).default(30),
});

export const OpenProjectInputSchema = z.object({
  projectId: z.string().min(1),
  expectedRevisionId: z.string().optional(),
  readOnly: z.boolean().default(false),
});

export const SaveProjectInputSchema = z.object({
  projectId: z.string().min(1),
  expectedRevisionId: z.string().optional(),
  description: z.string().max(500).optional(),
});

export const CloseProjectInputSchema = z.object({
  projectId: z.string().min(1),
  force: z.boolean().default(false),
});

export const DiffProjectRevisionsInputSchema = z.object({
  projectId: z.string().min(1),
  fromRevisionId: z.string().min(1),
  toRevisionId: z.string().min(1),
});

export const RestoreProjectRevisionInputSchema = z.object({
  projectId: z.string().min(1),
  targetRevisionId: z.string().min(1),
  description: z.string().max(500).optional(),
});

export const ValidateProjectInputSchema = z.object({
  projectId: z.string().min(1),
  strict: z.boolean().default(true),
});

export const CancelOperationInputSchema = z.object({
  operationId: z.string().min(1),
  reason: z.string().max(500).optional(),
});

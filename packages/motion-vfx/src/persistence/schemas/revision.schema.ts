import { z } from "zod";

export const RevisionAuthorSchema = z.discriminatedUnion("type", [
  z.object({
    type: z.literal("agent"),
    agentId: z.string().min(1),
  }),
  z.object({
    type: z.literal("user"),
    userId: z.string().min(1),
  }),
  z.object({
    type: z.literal("system"),
    systemId: z.string().min(1),
  }),
]);

export type RevisionAuthor = z.infer<typeof RevisionAuthorSchema>;

export const RevisionChangeSchema = z.object({
  path: z.string().min(1),
  operation: z.enum(["add", "remove", "replace", "move"]),
  before: z.unknown().optional(),
  after: z.unknown().optional(),
  description: z.string().optional(),
});

export type RevisionChange = z.infer<typeof RevisionChangeSchema>;

export const RevisionSchema = z.object({
  revisionId: z.string().min(1),
  projectId: z.string().min(1),
  parentRevisionId: z.string().nullable(),
  createdBy: RevisionAuthorSchema,
  message: z.string().max(1000),
  changes: z.array(RevisionChangeSchema),
  projectHash: z.string().length(64),
  schemaVersion: z.string().default("1.8.0"),
  project: z.record(z.unknown()), // Snapshot of the canonical project IR
  createdAt: z.string().optional(),
});

export type Revision = z.infer<typeof RevisionSchema>;

export const RevisionSummarySchema = z.object({
  revisionId: z.string(),
  projectId: z.string(),
  parentRevisionId: z.string().nullable(),
  createdBy: RevisionAuthorSchema,
  message: z.string(),
  projectHash: z.string(),
  changeCount: z.number().int().nonnegative(),
  createdAt: z.string().optional(),
});

export type RevisionSummary = z.infer<typeof RevisionSummarySchema>;

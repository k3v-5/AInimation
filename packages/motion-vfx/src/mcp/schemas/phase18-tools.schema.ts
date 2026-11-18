import { z } from "zod";

export const CreateProjectSchema = z.object({
  projectId: z.string().min(1).max(128),
  name: z.string().min(1).max(256),
  description: z.string().max(2000).optional(),
  author: z.string().max(256).default("agent"),
  width: z.number().int().positive().default(1920),
  height: z.number().int().positive().default(1080),
  fps: z.number().positive().default(30),
  duration: z.number().positive().default(10),
  initialElements: z.array(z.record(z.unknown())).optional(),
});

export const OpenProjectSchema = z.object({
  projectId: z.string().min(1),
  revisionId: z.string().optional(),
});

export const SaveProjectSchema = z.object({
  projectId: z.string().min(1),
  message: z.string().max(1000).default("Save project state"),
  author: z.string().max(256).default("agent"),
});

export const GetProjectSchema = z.object({
  projectId: z.string().min(1),
  revisionId: z.string().optional(),
});

export const ListProjectsSchema = z.object({
  limit: z.number().int().positive().max(100).default(50),
});

export const CreateRevisionSchema = z.object({
  projectId: z.string().min(1),
  parentRevisionId: z.string().nullable().optional(),
  message: z.string().min(1).max(1000),
  author: z.string().max(256).default("agent"),
  projectData: z.record(z.unknown()).optional(),
});

export const GetRevisionSchema = z.object({
  projectId: z.string().min(1),
  revisionId: z.string().min(1),
});

export const ListRevisionsSchema = z.object({
  projectId: z.string().min(1),
});

export const DiffRevisionsSchema = z.object({
  projectId: z.string().min(1),
  fromRevisionId: z.string().min(1),
  toRevisionId: z.string().min(1),
});

export const RestoreRevisionSchema = z.object({
  projectId: z.string().min(1),
  targetRevisionId: z.string().min(1),
  message: z.string().max(1000).optional(),
  author: z.string().max(256).default("agent"),
});

export const UndoRevisionSchema = z.object({
  projectId: z.string().min(1),
  targetRevisionId: z.string().min(1),
  message: z.string().max(1000).optional(),
  author: z.string().max(256).default("agent"),
});

export const RunWorkflowSchema = z.object({
  workflowId: z.string().min(1),
  projectId: z.string().min(1),
  revisionId: z.string().optional(),
  parameters: z.record(z.unknown()).optional(),
  dryRun: z.boolean().default(false),
});

export const GetWorkflowStatusSchema = z.object({
  workflowId: z.string().min(1),
});

export const CancelWorkflowSchema = z.object({
  workflowId: z.string().min(1),
  reason: z.string().max(500).optional(),
});

export const ResumeWorkflowSchema = z.object({
  workflowId: z.string().min(1),
  projectId: z.string().min(1),
});

export const ValidateProjectSchema = z.object({
  projectId: z.string().min(1),
  revisionId: z.string().optional(),
});

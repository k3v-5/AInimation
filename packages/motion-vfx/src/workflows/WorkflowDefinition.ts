import { z } from "zod";

export const RetryPolicySchema = z.object({
  maxAttempts: z.number().int().min(1).default(3),
  strategy: z.enum(["none", "fixed", "exponential"]).default("fixed"),
  intervalMs: z.number().int().min(0).default(100),
});

export type RetryPolicy = z.infer<typeof RetryPolicySchema>;

export const WorkflowStepDefinitionSchema = z.object({
  id: z.string().min(1),
  type: z.string().min(1),
  dependsOn: z.array(z.string()).default([]),
  retryPolicy: RetryPolicySchema.default({ maxAttempts: 1, strategy: "none", intervalMs: 0 }),
  idempotent: z.boolean().default(true),
  parameters: z.record(z.unknown()).optional(),
});

export type WorkflowStepDefinition = z.infer<typeof WorkflowStepDefinitionSchema>;

export const WorkflowDefinitionSchema = z.object({
  id: z.string().min(1),
  version: z.string().min(1),
  description: z.string().optional(),
  steps: z.array(WorkflowStepDefinitionSchema),
});

export type WorkflowDefinition = z.infer<typeof WorkflowDefinitionSchema>;

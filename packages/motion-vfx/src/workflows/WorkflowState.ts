import { z } from "zod";

export const WorkflowStateSchema = z.enum([
  "pending",
  "running",
  "paused",
  "completed",
  "failed",
  "cancelled",
]);

export type WorkflowState = z.infer<typeof WorkflowStateSchema>;

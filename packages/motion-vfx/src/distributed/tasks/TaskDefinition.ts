import { z } from "zod";
import { ProjectSerializer } from "../../persistence/ProjectSerializer.js";

export const TaskTypeSchema = z.enum([
  "plan_story",
  "edit_timeline",
  "design_motion",
  "mix_audio",
  "render_chunk",
  "perceptual_qa",
  "mux_export",
]);

export type TaskType = z.infer<typeof TaskTypeSchema>;

export const TaskStatusSchema = z.enum([
  "pending",
  "ready",
  "leased",
  "running",
  "completed",
  "failed",
  "cancelled",
]);

export type TaskStatus = z.infer<typeof TaskStatusSchema>;

export interface TaskRetryPolicy {
  maxAttempts: number;
  timeoutMs: number;
  backoffStrategy: "fixed" | "exponential";
}

export interface TaskDefinition {
  taskId: string;
  jobId: string;
  type: TaskType;
  requiredRole?: string;
  dependencies: string[]; // array de taskIds
  payload: Record<string, unknown>;
  status: TaskStatus;
  retryPolicy: TaskRetryPolicy;
  idempotencyKey: string;
  attemptCount: number;
  outputPayloadHash?: string;
  deterministicHash: string;
}

export function computeTaskHash(task: Omit<TaskDefinition, "deterministicHash" | "status" | "attemptCount">): string {
  return ProjectSerializer.hashCanonical({
    taskId: task.taskId,
    jobId: task.jobId,
    type: task.type,
    requiredRole: task.requiredRole ?? null,
    dependencies: [...task.dependencies].sort(),
    payload: task.payload,
    idempotencyKey: task.idempotencyKey,
  });
}

export function createTaskDefinition(params: {
  taskId: string;
  jobId: string;
  type: TaskType;
  requiredRole?: string;
  dependencies?: string[];
  payload?: Record<string, unknown>;
  retryPolicy?: Partial<TaskRetryPolicy>;
}): TaskDefinition {
  const deps = params.dependencies ? [...params.dependencies].sort() : [];
  const payload = params.payload ?? {};
  const retryPolicy: TaskRetryPolicy = {
    maxAttempts: params.retryPolicy?.maxAttempts ?? 3,
    timeoutMs: params.retryPolicy?.timeoutMs ?? 30000,
    backoffStrategy: params.retryPolicy?.backoffStrategy ?? "fixed",
  };

  const idempotencyKey = ProjectSerializer.hashCanonical({
    jobId: params.jobId,
    type: params.type,
    dependencies: deps,
    payload,
  });

  const base = {
    taskId: params.taskId,
    jobId: params.jobId,
    type: params.type,
    requiredRole: params.requiredRole,
    dependencies: deps,
    payload,
    retryPolicy,
    idempotencyKey,
  };

  return {
    ...base,
    status: "pending",
    attemptCount: 0,
    deterministicHash: computeTaskHash(base),
  };
}

import { ProjectSerializer } from "../../persistence/ProjectSerializer.js";

export interface TaskResult {
  taskId: string;
  workerId: string;
  success: boolean;
  outputPayload?: Record<string, unknown>;
  outputArtifacts?: Record<string, string>; // artifactName -> hash
  error?: {
    code: string;
    message: string;
  };
  durationTicks: number;
  deterministicHash: string;
}

export function createTaskResult(params: {
  taskId: string;
  workerId: string;
  success: boolean;
  outputPayload?: Record<string, unknown>;
  outputArtifacts?: Record<string, string>;
  error?: { code: string; message: string };
  durationTicks?: number;
}): TaskResult {
  const outputPayload = params.outputPayload ?? {};
  const outputArtifacts = params.outputArtifacts ?? {};

  const deterministicHash = ProjectSerializer.hashCanonical({
    taskId: params.taskId,
    workerId: params.workerId,
    success: params.success,
    outputPayload,
    outputArtifacts,
    error: params.error ?? null,
  });

  return {
    taskId: params.taskId,
    workerId: params.workerId,
    success: params.success,
    outputPayload,
    outputArtifacts,
    error: params.error,
    durationTicks: params.durationTicks ?? 1,
    deterministicHash,
  };
}

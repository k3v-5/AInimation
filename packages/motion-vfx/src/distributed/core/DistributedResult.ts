import { ProjectSerializer } from "../../persistence/ProjectSerializer.js";
import { DistributedJob } from "./DistributedJob.js";

export interface DistributedResult {
  jobId: string;
  projectId: string;
  success: boolean;
  finalRevisionId?: string;
  totalDurationMs: number;
  tasksCompleted: number;
  tasksFailed: number;
  outputArtifacts: Record<string, string>; // artifactName -> hash
  manifestHash: string;
}

export function createDistributedResult(params: {
  job: DistributedJob;
  success: boolean;
  finalRevisionId?: string;
  totalDurationMs: number;
  outputArtifacts?: Record<string, string>;
}): DistributedResult {
  const artifacts = params.outputArtifacts ?? {};
  const manifestHash = ProjectSerializer.hashCanonical({
    jobId: params.job.jobId,
    projectId: params.job.projectId,
    success: params.success,
    finalRevisionId: params.finalRevisionId ?? null,
    tasksCompleted: params.job.completedTasks,
    tasksFailed: params.job.failedTasks,
    artifacts,
  });

  return {
    jobId: params.job.jobId,
    projectId: params.job.projectId,
    success: params.success,
    finalRevisionId: params.finalRevisionId,
    totalDurationMs: params.totalDurationMs,
    tasksCompleted: params.job.completedTasks,
    tasksFailed: params.job.failedTasks,
    outputArtifacts: artifacts,
    manifestHash,
  };
}

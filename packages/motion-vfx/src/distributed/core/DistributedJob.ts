import { z } from "zod";
import { ProjectSerializer } from "../../persistence/ProjectSerializer.js";

export const DistributedJobStatusSchema = z.enum([
  "created",
  "planning",
  "dispatching",
  "executing",
  "merging",
  "completed",
  "failed",
  "cancelled",
]);

export type DistributedJobStatus = z.infer<typeof DistributedJobStatusSchema>;

export interface DistributedJob {
  jobId: string;
  projectId: string;
  briefHash: string;
  baselineRevisionId: string;
  status: DistributedJobStatus;
  allocatedWorkers: number;
  createdAtLogical: number;
  taskCount: number;
  completedTasks: number;
  failedTasks: number;
  resultingRevisionId?: string;
  deterministicHash: string;
}

export function computeDistributedJobHash(job: Omit<DistributedJob, "deterministicHash">): string {
  return ProjectSerializer.hashCanonical({
    jobId: job.jobId,
    projectId: job.projectId,
    briefHash: job.briefHash,
    baselineRevisionId: job.baselineRevisionId,
    status: job.status,
    taskCount: job.taskCount,
    completedTasks: job.completedTasks,
    failedTasks: job.failedTasks,
    resultingRevisionId: job.resultingRevisionId ?? null,
  });
}

export function createDistributedJob(params: {
  jobId: string;
  projectId: string;
  briefHash: string;
  baselineRevisionId: string;
  allocatedWorkers?: number;
  createdAtLogical?: number;
}): DistributedJob {
  const base = {
    jobId: params.jobId,
    projectId: params.projectId,
    briefHash: params.briefHash,
    baselineRevisionId: params.baselineRevisionId,
    status: "created" as DistributedJobStatus,
    allocatedWorkers: params.allocatedWorkers ?? 1,
    createdAtLogical: params.createdAtLogical ?? 1,
    taskCount: 0,
    completedTasks: 0,
    failedTasks: 0,
    resultingRevisionId: undefined,
  };

  return {
    ...base,
    deterministicHash: computeDistributedJobHash(base),
  };
}

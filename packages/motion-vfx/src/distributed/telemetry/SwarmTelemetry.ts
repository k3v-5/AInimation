export interface SwarmTelemetry {
  jobId: string;
  totalTasks: number;
  completedTasks: number;
  failedTasks: number;
  proposalsGenerated: number;
  proposalsMerged: number;
  throughputTasksPerSec: number;
  elapsedMs: number;
}

export function computeSwarmTelemetry(params: {
  jobId: string;
  totalTasks: number;
  completedTasks: number;
  failedTasks: number;
  proposalsGenerated: number;
  proposalsMerged: number;
  elapsedMs: number;
}): SwarmTelemetry {
  const sec = Math.max(0.001, params.elapsedMs / 1000);
  const throughput = params.completedTasks / sec;

  return {
    jobId: params.jobId,
    totalTasks: params.totalTasks,
    completedTasks: params.completedTasks,
    failedTasks: params.failedTasks,
    proposalsGenerated: params.proposalsGenerated,
    proposalsMerged: params.proposalsMerged,
    throughputTasksPerSec: Math.round(throughput * 100) / 100,
    elapsedMs: params.elapsedMs,
  };
}

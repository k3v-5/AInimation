import { DistributedConfig } from "./DistributedConfig.js";
import { DistributedJob } from "./DistributedJob.js";

export interface DistributedContext {
  job: DistributedJob;
  config: DistributedConfig;
  logicalTimestamp: number;
  metadata?: Record<string, unknown>;
}

export function createDistributedContext(job: DistributedJob, config: DistributedConfig): DistributedContext {
  return {
    job,
    config,
    logicalTimestamp: job.createdAtLogical,
  };
}

import { z } from "zod";

export const DistributedConfigSchema = z.object({
  clusterId: z.string().default("cluster_default"),
  maxWorkers: z.number().int().min(1).max(64).default(8),
  defaultTaskTimeoutMs: z.number().min(50).max(600000).default(30000),
  heartbeatIntervalMs: z.number().min(50).max(60000).default(2000),
  leaseDurationMs: z.number().min(100).max(120000).default(6000),
  maxRetryAttempts: z.number().int().min(0).max(10).default(3),
  loadBalancingStrategy: z.enum(["least_loaded", "round_robin", "affinity"]).default("least_loaded"),
  enableWorkStealing: z.boolean().default(true),
  idempotencyTtlMs: z.number().min(1000).default(3600000),
});

export type DistributedConfig = z.infer<typeof DistributedConfigSchema>;

export function createDefaultDistributedConfig(overrides?: Partial<DistributedConfig>): DistributedConfig {
  return DistributedConfigSchema.parse(overrides ?? {});
}

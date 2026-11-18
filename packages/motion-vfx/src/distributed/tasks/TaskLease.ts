import { ProjectSerializer } from "../../persistence/ProjectSerializer.js";

export interface TaskLease {
  leaseId: string;
  taskId: string;
  workerId: string;
  attemptNumber: number;
  acquiredAtLogical: number;
  expiresAtLogical: number;
  heartbeatCounter: number;
  active: boolean;
  deterministicHash: string;
}

export function createTaskLease(params: {
  taskId: string;
  workerId: string;
  attemptNumber: number;
  acquiredAtLogical: number;
  leaseDurationTicks: number;
}): TaskLease {
  const leaseId = ProjectSerializer.hashCanonical({
    taskId: params.taskId,
    workerId: params.workerId,
    attemptNumber: params.attemptNumber,
  }).slice(0, 16);

  const base = {
    leaseId: `lease_${leaseId}`,
    taskId: params.taskId,
    workerId: params.workerId,
    attemptNumber: params.attemptNumber,
    acquiredAtLogical: params.acquiredAtLogical,
    expiresAtLogical: params.acquiredAtLogical + params.leaseDurationTicks,
    heartbeatCounter: 0,
    active: true,
  };

  const deterministicHash = ProjectSerializer.hashCanonical({
    leaseId: base.leaseId,
    taskId: base.taskId,
    workerId: base.workerId,
    attemptNumber: base.attemptNumber,
  });

  return {
    ...base,
    deterministicHash,
  };
}

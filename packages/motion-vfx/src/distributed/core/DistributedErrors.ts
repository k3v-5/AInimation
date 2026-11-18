export class DistributedError extends Error {
  public readonly code: string;
  public readonly context?: Record<string, unknown>;

  constructor(message: string, code = "DISTRIBUTED_ERROR", context?: Record<string, unknown>) {
    super(message);
    this.name = this.constructor.name;
    this.code = code;
    this.context = context;
    Object.setPrototypeOf(this, new.target.prototype);
  }
}

export class TaskDAGCycleError extends DistributedError {
  constructor(cycle: string[], context?: Record<string, unknown>) {
    super(`Cycle detected in TaskDAG: ${cycle.join(" -> ")}`, "TASK_DAG_CYCLE", { cycle, ...context });
  }
}

export class TaskExecutionTimeoutError extends DistributedError {
  constructor(taskId: string, timeoutMs: number, context?: Record<string, unknown>) {
    super(`Task ${taskId} timed out after ${timeoutMs}ms`, "TASK_TIMEOUT", { taskId, timeoutMs, ...context });
  }
}

export class TaskLeaseExpiredError extends DistributedError {
  constructor(taskId: string, leaseId: string, context?: Record<string, unknown>) {
    super(`Lease ${leaseId} for task ${taskId} has expired or was revoked`, "TASK_LEASE_EXPIRED", { taskId, leaseId, ...context });
  }
}

export class WorkerCapacityExceededError extends DistributedError {
  constructor(workerId: string, current: number, max: number, context?: Record<string, unknown>) {
    super(`Worker ${workerId} capacity exceeded (${current}/${max})`, "WORKER_CAPACITY_EXCEEDED", { workerId, current, max, ...context });
  }
}

export class WorkerUnavailableError extends DistributedError {
  constructor(workerId: string, context?: Record<string, unknown>) {
    super(`Worker ${workerId} is unavailable or unresponsive`, "WORKER_UNAVAILABLE", { workerId, ...context });
  }
}

export class ProposalConflictError extends DistributedError {
  constructor(proposalA: string, proposalB: string, conflictPath: string, context?: Record<string, unknown>) {
    super(`Conflict between proposals ${proposalA} and ${proposalB} on path: ${conflictPath}`, "PROPOSAL_CONFLICT", { proposalA, proposalB, conflictPath, ...context });
  }
}

export class SwarmCoordinationError extends DistributedError {
  constructor(message: string, context?: Record<string, unknown>) {
    super(message, "SWARM_COORDINATION_ERROR", context);
  }
}

export class DistributedSerializationError extends DistributedError {
  constructor(message: string, context?: Record<string, unknown>) {
    super(message, "DISTRIBUTED_SERIALIZATION_ERROR", context);
  }
}

export class DistributedIntegrityError extends DistributedError {
  constructor(message: string, context?: Record<string, unknown>) {
    super(message, "DISTRIBUTED_INTEGRITY_ERROR", context);
  }
}

export class TaskNotFoundError extends DistributedError {
  constructor(taskId: string, context?: Record<string, unknown>) {
    super(`Task ${taskId} not found in distributed job`, "TASK_NOT_FOUND", { taskId, ...context });
  }
}

export class JobNotFoundError extends DistributedError {
  constructor(jobId: string, context?: Record<string, unknown>) {
    super(`Distributed job ${jobId} not found`, "JOB_NOT_FOUND", { jobId, ...context });
  }
}

export class DistributedEquivalenceError extends DistributedError {
  constructor(localHash: string, distributedHash: string, context?: Record<string, unknown>) {
    super(`Distributed output hash (${distributedHash}) does not match local hash (${localHash})`, "DISTRIBUTED_EQUIVALENCE_ERROR", { localHash, distributedHash, ...context });
  }
}

export class WorkStealingError extends DistributedError {
  constructor(message: string, context?: Record<string, unknown>) {
    super(message, "WORK_STEALING_ERROR", context);
  }
}

export class TransportError extends DistributedError {
  constructor(message: string, context?: Record<string, unknown>) {
    super(message, "TRANSPORT_ERROR", context);
  }
}

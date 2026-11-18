/**
 * Jerarquía de errores tipados para el motor de Workflows (Fase 18).
 */
export class WorkflowError extends Error {
  public readonly code: string;
  public readonly context?: Record<string, unknown>;

  constructor(message: string, code = "WORKFLOW_ERROR", context?: Record<string, unknown>) {
    super(`[${code}] ${message}`);
    this.name = this.constructor.name;
    this.code = code;
    this.context = context;
    Object.setPrototypeOf(this, new.target.prototype);
  }

  public toJSON(): Record<string, unknown> {
    return {
      name: this.name,
      code: this.code,
      message: this.message,
      context: this.context,
    };
  }
}

export class WorkflowNotFoundError extends WorkflowError {
  constructor(public readonly workflowId: string, context?: Record<string, unknown>) {
    super(`Workflow '${workflowId}' was not found.`, "WORKFLOW_NOT_FOUND", { workflowId, ...context });
  }
}

export class WorkflowExecutionError extends WorkflowError {
  constructor(public readonly workflowId: string, public readonly stepId: string, reason: string, context?: Record<string, unknown>) {
    super(`Workflow '${workflowId}' step '${stepId}' failed: ${reason}`, "WORKFLOW_EXECUTION_ERROR", { workflowId, stepId, reason, ...context });
  }
}

export class WorkflowCancelledError extends WorkflowError {
  constructor(public readonly workflowId: string, reason?: string) {
    super(`Workflow '${workflowId}' was cancelled: ${reason ?? "User cancellation"}`, "WORKFLOW_CANCELLED", { workflowId, reason });
  }
}

export class WorkflowDependencyError extends WorkflowError {
  constructor(public readonly stepId: string, public readonly missingDep: string) {
    super(`Step '${stepId}' depends on unmet dependency '${missingDep}'.`, "WORKFLOW_DEPENDENCY_ERROR", { stepId, missingDep });
  }
}

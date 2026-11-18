/**
 * Jerarquía de errores tipados para la orquestación y control de producción (Fase 18).
 */
export class ProductionError extends Error {
  public readonly code: string;
  public readonly context?: Record<string, unknown>;

  constructor(message: string, code = "PRODUCTION_ERROR", context?: Record<string, unknown>) {
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

export class ProductionProjectError extends ProductionError {
  constructor(message: string, context?: Record<string, unknown>) {
    super(message, "PRODUCTION_PROJECT_ERROR", context);
  }
}

export class ProductionRevisionError extends ProductionError {
  constructor(message: string, context?: Record<string, unknown>) {
    super(message, "PRODUCTION_REVISION_ERROR", context);
  }
}

export class RevisionConflictError extends ProductionError {
  constructor(public readonly expectedParent: string, public readonly actualParent: string, context?: Record<string, unknown>) {
    super(
      `Revision conflict: expected parent '${expectedParent}', but current head is '${actualParent}'.`,
      "REVISION_CONFLICT",
      { expectedParent, actualParent, ...context }
    );
  }
}

export class RevisionOperationError extends ProductionError {
  constructor(public readonly operationType: string, public readonly targetId: string, reason: string, context?: Record<string, unknown>) {
    super(`Operation '${operationType}' on target '${targetId}' failed: ${reason}`, "REVISION_OPERATION_ERROR", { operationType, targetId, reason, ...context });
  }
}

export class RevisionNotFoundError extends ProductionError {
  constructor(public readonly revisionId: string, context?: Record<string, unknown>) {
    super(`Revision '${revisionId}' was not found.`, "REVISION_NOT_FOUND", { revisionId, ...context });
  }
}

export class CheckpointError extends ProductionError {
  constructor(message: string, context?: Record<string, unknown>) {
    super(message, "CHECKPOINT_ERROR", context);
  }
}

export class ProductionValidationError extends ProductionError {
  constructor(message: string, public readonly issues: unknown[], context?: Record<string, unknown>) {
    super(`Production validation failed: ${message}`, "PRODUCTION_VALIDATION_ERROR", { issues, ...context });
  }
}

export class RenderQAError extends ProductionError {
  constructor(message: string, context?: Record<string, unknown>) {
    super(message, "RENDER_QA_ERROR", context);
  }
}

export class ProductionPipelineError extends ProductionError {
  constructor(public readonly stageId: string, reason: string, context?: Record<string, unknown>) {
    super(`Pipeline stage '${stageId}' failed: ${reason}`, "PRODUCTION_PIPELINE_ERROR", { stageId, reason, ...context });
  }
}

export class ManifestVerificationError extends ProductionError {
  constructor(message: string, context?: Record<string, unknown>) {
    super(message, "MANIFEST_VERIFICATION_ERROR", context);
  }
}

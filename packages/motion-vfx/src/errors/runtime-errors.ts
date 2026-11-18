/**
 * Clase base para todos los errores originados en el Runtime de Producción (Fase 18).
 */
export class RuntimeError extends Error {
  public readonly code: string;
  public readonly context?: Record<string, unknown>;

  constructor(message: string, code = "RUNTIME_ERROR", context?: Record<string, unknown>) {
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

export class ProjectNotFoundError extends RuntimeError {
  constructor(public readonly projectId: string, context?: Record<string, unknown>) {
    super(`Project with ID '${projectId}' was not found.`, "PROJECT_NOT_FOUND", { projectId, ...context });
    this.name = "ProjectNotFoundError";
  }
}

export class ProjectAlreadyExistsError extends RuntimeError {
  constructor(public readonly projectId: string, context?: Record<string, unknown>) {
    super(`Project with ID '${projectId}' already exists.`, "PROJECT_ALREADY_EXISTS", { projectId, ...context });
    this.name = "ProjectAlreadyExistsError";
  }
}

export class ProjectCorruptError extends RuntimeError {
  constructor(public readonly projectId: string, reason: string, context?: Record<string, unknown>) {
    super(`Project '${projectId}' is corrupted: ${reason}`, "PROJECT_CORRUPT", { projectId, reason, ...context });
    this.name = "ProjectCorruptError";
  }
}

export class ProjectValidationError extends RuntimeError {
  constructor(public readonly projectId: string, public readonly issues: unknown[], context?: Record<string, unknown>) {
    super(`Project '${projectId}' failed runtime validation with ${issues.length} issues.`, "PROJECT_VALIDATION_ERROR", { projectId, issues, ...context });
    this.name = "ProjectValidationError";
  }
}

export class RevisionNotFoundError extends RuntimeError {
  constructor(public readonly projectId: string, public readonly revisionId: string, context?: Record<string, unknown>) {
    super(`Revision '${revisionId}' not found for project '${projectId}'.`, "REVISION_NOT_FOUND", { projectId, revisionId, ...context });
    this.name = "RevisionNotFoundError";
  }
}

export class RevisionConflictError extends RuntimeError {
  constructor(public readonly projectId: string, public readonly expectedRevisionId: string, public readonly actualRevisionId: string, context?: Record<string, unknown>) {
    super(
      `Revision conflict on project '${projectId}': expected base revision '${expectedRevisionId}', but current head is '${actualRevisionId}'.`,
      "REVISION_CONFLICT",
      { projectId, expectedRevisionId, actualRevisionId, ...context }
    );
    this.name = "RevisionConflictError";
  }
}

export class RevisionRestoreError extends RuntimeError {
  constructor(public readonly projectId: string, public readonly targetRevisionId: string, reason: string, context?: Record<string, unknown>) {
    super(`Failed to restore revision '${targetRevisionId}' for project '${projectId}': ${reason}`, "REVISION_RESTORE_ERROR", { projectId, targetRevisionId, reason, ...context });
    this.name = "RevisionRestoreError";
  }
}

export class PersistenceError extends RuntimeError {
  constructor(message: string, context?: Record<string, unknown>) {
    super(`Persistence Error: ${message}`, "PERSISTENCE_ERROR", context);
    this.name = "PersistenceError";
  }
}

export class AtomicWriteError extends RuntimeError {
  constructor(public readonly targetPath: string, reason: string, context?: Record<string, unknown>) {
    super(`Atomic write failed for path '${targetPath}': ${reason}`, "ATOMIC_WRITE_ERROR", { targetPath, reason, ...context });
    this.name = "AtomicWriteError";
  }
}

export class RecoveryError extends RuntimeError {
  constructor(public readonly projectId: string, reason: string, context?: Record<string, unknown>) {
    super(`Recovery failed for project '${projectId}': ${reason}`, "RECOVERY_ERROR", { projectId, reason, ...context });
    this.name = "RecoveryError";
  }
}

export class MigrationError extends RuntimeError {
  constructor(public readonly fromVersion: string, public readonly toVersion: string, reason: string, context?: Record<string, unknown>) {
    super(`Migration failed from ${fromVersion} to ${toVersion}: ${reason}`, "MIGRATION_ERROR", { fromVersion, toVersion, reason, ...context });
    this.name = "MigrationError";
  }
}

export class AssetIntegrityError extends RuntimeError {
  constructor(public readonly assetId: string, reason: string, context?: Record<string, unknown>) {
    super(`Asset integrity violation for '${assetId}': ${reason}`, "ASSET_INTEGRITY_ERROR", { assetId, reason, ...context });
    this.name = "AssetIntegrityError";
  }
}

export class ResourceLimitError extends RuntimeError {
  constructor(message: string, context?: Record<string, unknown>) {
    super(`Resource limit exceeded: ${message}`, "RESOURCE_LIMIT_ERROR", context);
    this.name = "ResourceLimitError";
  }
}

export class ProjectResourceLimitError extends ResourceLimitError {
  constructor(public readonly limitName: string, public readonly actual: number, public readonly max: number, context?: Record<string, unknown>) {
    super(`Project resource limit '${limitName}' exceeded: got ${actual}, maximum allowed is ${max}`, { limitName, actual, max, ...context });
    this.name = "ProjectResourceLimitError";
  }
}

export class OperationError extends RuntimeError {
  constructor(public readonly operationId: string, message: string, context?: Record<string, unknown>) {
    super(`Operation '${operationId}' failed: ${message}`, "OPERATION_ERROR", { operationId, ...context });
    this.name = "OperationError";
  }
}

export class OperationCancelledError extends RuntimeError {
  constructor(public readonly operationId?: string, context?: Record<string, unknown>) {
    super(`Operation ${operationId ? `'${operationId}' ` : ""}was cancelled.`, "OPERATION_CANCELLED", { operationId, ...context });
    this.name = "OperationCancelledError";
  }
}

export class LockAcquisitionError extends RuntimeError {
  constructor(public readonly projectId: string, reason: string, context?: Record<string, unknown>) {
    super(`Could not acquire lock for project '${projectId}': ${reason}`, "LOCK_ACQUISITION_ERROR", { projectId, reason, ...context });
    this.name = "LockAcquisitionError";
  }
}

export class LockTimeoutError extends RuntimeError {
  constructor(public readonly projectId: string, timeoutMs: number, context?: Record<string, unknown>) {
    super(`Lock acquisition timed out after ${timeoutMs}ms for project '${projectId}'.`, "LOCK_TIMEOUT_ERROR", { projectId, timeoutMs, ...context });
    this.name = "LockTimeoutError";
  }
}

export class DeterminismError extends RuntimeError {
  constructor(message: string, context?: Record<string, unknown>) {
    super(`Determinism verification failed: ${message}`, "DETERMINISM_ERROR", context);
    this.name = "DeterminismError";
  }
}

export class RuntimeConfigurationError extends RuntimeError {
  constructor(message: string, context?: Record<string, unknown>) {
    super(`Runtime configuration invalid: ${message}`, "RUNTIME_CONFIG_ERROR", context);
    this.name = "RuntimeConfigurationError";
  }
}

export class UnsupportedProjectVersionError extends RuntimeError {
  constructor(public readonly schemaVersion: string, context?: Record<string, unknown>) {
    super(`Project schemaVersion '${schemaVersion}' is not supported by this engine.`, "UNSUPPORTED_PROJECT_VERSION", { schemaVersion, ...context });
    this.name = "UnsupportedProjectVersionError";
  }
}

export class RuntimeStateError extends RuntimeError {
  constructor(public readonly currentState: string, public readonly requiredState: string, context?: Record<string, unknown>) {
    super(`Cannot perform operation in runtime state '${currentState}'. Required state: '${requiredState}'.`, "RUNTIME_STATE_ERROR", { currentState, requiredState, ...context });
    this.name = "RuntimeStateError";
  }
}

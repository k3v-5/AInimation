import { OperationError } from "../errors/runtime-errors.js";
import { CancellationToken } from "./CancellationToken.js";
import { RuntimeOperation } from "./types.js";

/**
 * Gestor y monitor de operaciones asíncronas del Runtime (Fase 18).
 */
export class OperationManager {
  private operations = new Map<string, { op: RuntimeOperation; token: CancellationToken }>();

  public createOperation(projectId: string, type: string, operationId = `op_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`): {
    operation: RuntimeOperation;
    token: CancellationToken;
  } {
    const token = new CancellationToken();
    const operation: RuntimeOperation = {
      operationId,
      projectId,
      type,
      status: "queued",
      progress: 0,
      startedAt: new Date().toISOString(),
    };

    this.operations.set(operationId, { op: operation, token });
    return { operation, token };
  }

  public getOperation(operationId: string): RuntimeOperation | undefined {
    return this.operations.get(operationId)?.op;
  }

  public cancelOperation(operationId: string, reason?: string): boolean {
    const entry = this.operations.get(operationId);
    if (!entry) return false;
    entry.token.cancel(reason);
    entry.op.status = "cancelled";
    entry.op.completedAt = new Date().toISOString();
    return true;
  }

  public updateProgress(operationId: string, progress: number): void {
    const entry = this.operations.get(operationId);
    if (entry) {
      entry.op.status = "running";
      entry.op.progress = Math.min(1.0, Math.max(0, progress));
    }
  }

  public completeOperation(operationId: string): void {
    const entry = this.operations.get(operationId);
    if (entry) {
      entry.op.status = "completed";
      entry.op.progress = 1.0;
      entry.op.completedAt = new Date().toISOString();
    }
  }

  public failOperation(operationId: string, err: Error): void {
    const entry = this.operations.get(operationId);
    if (entry) {
      entry.op.status = "failed";
      entry.op.error = err;
      entry.op.completedAt = new Date().toISOString();
    }
  }

  public listActiveOperations(projectId?: string): RuntimeOperation[] {
    const ops = Array.from(this.operations.values())
      .map((e) => e.op)
      .filter((op) => op.status === "running" || op.status === "queued");

    if (projectId) {
      return ops.filter((op) => op.projectId === projectId);
    }
    return ops;
  }
}

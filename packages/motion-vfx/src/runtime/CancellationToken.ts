import { OperationCancelledError } from "../errors/runtime-errors.js";

/**
 * Token cooperativo para cancelar operaciones largas de manera segura (Fase 18).
 */
export class CancellationToken {
  private _isCancelled = false;
  private _reason?: string;
  private listeners: Array<() => void> = [];

  public isCancelled(): boolean {
    return this._isCancelled;
  }

  public getReason(): string | undefined {
    return this._reason;
  }

  public cancel(reason = "Operation cancelled by user"): void {
    if (this._isCancelled) return;
    this._isCancelled = true;
    this._reason = reason;
    for (const cb of this.listeners) {
      try {
        cb();
      } catch {
        // Silenciar errores en listeners de cancelación
      }
    }
  }

  public throwIfCancelled(): void {
    if (this._isCancelled) {
      throw new OperationCancelledError(undefined, { reason: this._reason });
    }
  }

  public onCancelled(callback: () => void): void {
    if (this._isCancelled) {
      callback();
    } else {
      this.listeners.push(callback);
    }
  }
}

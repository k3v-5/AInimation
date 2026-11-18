import { LockHandle, LockManager } from "./locking/LockManager.js";
import { StorageAdapter } from "./persistence/StorageAdapter.js";

/**
 * Envoltorio ergonómico de bloqueo a nivel de sesión de proyecto (Fase 18).
 */
export class ProjectLock {
  private lockManager: LockManager;
  private currentHandle?: LockHandle;

  constructor(storage: StorageAdapter) {
    this.lockManager = new LockManager(storage);
  }

  public async acquire(projectId: string, owner?: string): Promise<void> {
    if (this.currentHandle) return;
    this.currentHandle = await this.lockManager.acquireLock(projectId, owner);
  }

  public async release(): Promise<void> {
    if (this.currentHandle) {
      await this.currentHandle.release();
      this.currentHandle = undefined;
    }
  }

  public isHeld(): boolean {
    return this.currentHandle !== undefined;
  }
}

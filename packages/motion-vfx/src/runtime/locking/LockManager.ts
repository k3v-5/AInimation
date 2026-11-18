import { LockAcquisitionError, LockTimeoutError } from "../../errors/runtime-errors.js";
import { RuntimeLimits } from "../../schemas/runtime.schema.js";
import { StorageAdapter } from "../persistence/StorageAdapter.js";
import { LockFile, LockMetadata } from "./LockFile.js";

export interface LockHandle {
  projectId: string;
  owner: string;
  release: () => Promise<void>;
}

/**
 * Gestor de exclusión mutua para impedir accesos de escritura concurrentes (Fase 18).
 */
export class LockManager {
  private storage: StorageAdapter;
  private memoryLocks = new Set<string>();

  constructor(storage: StorageAdapter) {
    this.storage = storage;
  }

  /**
   * Intenta adquirir el bloqueo exclusivo de un proyecto.
   */
  public async acquireLock(
    projectId: string,
    owner = `process_${process.pid ?? 1}`,
    timeoutMs = RuntimeLimits.LOCK_TIMEOUT_MS
  ): Promise<LockHandle> {
    const lockKey = `projects/${projectId}/project.lock`;
    const startTime = Date.now();

    while (Date.now() - startTime < timeoutMs) {
      if (this.memoryLocks.has(projectId)) {
        await new Promise((r) => setTimeout(r, 50));
        continue;
      }

      const existingData = await this.storage.read(lockKey);
      if (existingData) {
        const meta = LockFile.deserialize(existingData);
        // Verificar si el lock ha expirado (Stale lock)
        if (meta && Date.now() > meta.expiresAt) {
          await this.storage.delete(lockKey);
        } else {
          await new Promise((r) => setTimeout(r, 50));
          continue;
        }
      }

      // Intentar escribir nuevo lock
      const now = Date.now();
      const meta: LockMetadata = {
        projectId,
        owner,
        pid: process.pid ?? 1,
        createdAt: now,
        expiresAt: now + RuntimeLimits.LOCK_STALE_AGE_MS,
      };

      try {
        await this.storage.write(lockKey, LockFile.serialize(meta));
        this.memoryLocks.add(projectId);

        let released = false;
        return {
          projectId,
          owner,
          release: async () => {
            if (released) return;
            released = true;
            this.memoryLocks.delete(projectId);
            await this.storage.delete(lockKey);
          },
        };
      } catch (err: any) {
        throw new LockAcquisitionError(projectId, err.message);
      }
    }

    throw new LockTimeoutError(projectId, timeoutMs);
  }

  public async isLocked(projectId: string): Promise<boolean> {
    if (this.memoryLocks.has(projectId)) return true;
    const lockKey = `projects/${projectId}/project.lock`;
    return this.storage.exists(lockKey);
  }
}

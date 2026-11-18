import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { LockTimeoutError } from "../../errors/runtime-errors.js";
import { LockManager } from "../../runtime/locking/LockManager.js";
import { MemoryStorageAdapter } from "../../runtime/persistence/MemoryStorageAdapter.js";
import { ProjectRepository } from "../../runtime/ProjectRepository.js";

describe("Fase 18 — Locking & Concurrency Tests", () => {
  it("enforces mutual exclusion between concurrent writers", async () => {
    const storage = new MemoryStorageAdapter();
    const lockManager = new LockManager(storage);

    const lockA = await lockManager.acquireLock("proj_locked", "writer_A", 1000);
    assert.ok(lockA);

    // Writer B intenta adquirir el mismo lock con timeout corto (100ms)
    await assert.rejects(
      async () => {
        await lockManager.acquireLock("proj_locked", "writer_B", 100);
      },
      (err: any) => err instanceof LockTimeoutError
    );

    // Writer A libera el lock
    await lockA.release();

    // Writer B ahora puede adquirirlo
    const lockB = await lockManager.acquireLock("proj_locked", "writer_B", 500);
    assert.ok(lockB);
    await lockB.release();
  });

  it("handles 10 concurrent reads without contention or data corruption", async () => {
    const storage = new MemoryStorageAdapter();
    const repo = new ProjectRepository(storage);

    const created = await repo.create({
      projectId: "proj_concurrent_reads",
      project: { name: "Read Target", data: [1, 2, 3] },
      metadata: { name: "Read Target" },
    });

    const readPromises = Array.from({ length: 10 }, async () => {
      const loaded = await repo.load("proj_concurrent_reads");
      return loaded.contentHash;
    });

    const hashes = await Promise.all(readPromises);
    assert.equal(hashes.length, 10);
    for (const h of hashes) {
      assert.equal(h, created.contentHash);
    }
  });
});

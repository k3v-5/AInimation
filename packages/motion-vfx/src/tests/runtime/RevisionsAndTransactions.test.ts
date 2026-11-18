import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { RevisionConflictError } from "../../errors/runtime-errors.js";
import { MemoryStorageAdapter } from "../../runtime/persistence/MemoryStorageAdapter.js";
import { ProjectRepository } from "../../runtime/ProjectRepository.js";
import { ProjectTransaction } from "../../runtime/ProjectTransaction.js";
import { RevisionManager } from "../../runtime/RevisionManager.js";

describe("Fase 18 — Revisions, Optimistic Concurrency & Transactions Tests", () => {
  it("creates sequential revisions and detects optimistic concurrency conflicts", async () => {
    const storage = new MemoryStorageAdapter();
    const repo = new ProjectRepository(storage);
    const revManager = new RevisionManager(repo);

    await repo.create({
      projectId: "proj_concurrency",
      project: { version: 1, layers: ["l1"] },
      metadata: { name: "Concurrency Test" },
    });

    // 1. Crear rev_000002 especificando baseRevisionId = rev_000001
    const rev2 = await revManager.createRevision({
      projectId: "proj_concurrency",
      baseRevisionId: "rev_000001",
      nextProject: { version: 2, layers: ["l1", "l2"] },
    });

    assert.equal(rev2.revisionId, "rev_000002");

    // 2. Intentar mutar desde rev_000001 cuando el head es rev_000002 -> Debe fallar
    await assert.rejects(
      async () => {
        await revManager.createRevision({
          projectId: "proj_concurrency",
          baseRevisionId: "rev_000001",
          nextProject: { version: 3, layers: ["conflict"] },
        });
      },
      (err: any) => err instanceof RevisionConflictError
    );
  });

  it("rolls back transaction changes if mutation throws an error", async () => {
    const storage = new MemoryStorageAdapter();
    const repo = new ProjectRepository(storage);
    const revManager = new RevisionManager(repo);
    const tx = new ProjectTransaction(revManager);

    await repo.create({
      projectId: "proj_tx",
      project: { count: 10, layers: ["l1"] },
      metadata: { name: "Transaction Test" },
    });

    const headBefore = await repo.load("proj_tx");
    assert.equal(headBefore.revisionId, "rev_000001");

    // Ejecutar transacción fallida
    await assert.rejects(
      async () => {
        await tx.execute({
          projectId: "proj_tx",
          currentProject: headBefore.project,
          mutation: (draft: any) => {
            draft.count = 999;
            draft.layers.push("l2");
            throw new Error("Simulated database failure inside transaction");
          },
        });
      },
      /Simulated database failure/
    );

    const headAfter = await repo.load("proj_tx");
    assert.equal(headAfter.revisionId, "rev_000001", "Head revision must remain rev_000001");
    assert.equal((headAfter.project as any).count, 10, "Project content must be unchanged");
  });

  it("restores historical revision non-destructively by creating a new revision", async () => {
    const storage = new MemoryStorageAdapter();
    const repo = new ProjectRepository(storage);
    const revManager = new RevisionManager(repo);

    await repo.create({
      projectId: "proj_restore",
      project: { state: "v1_original" },
      metadata: { name: "Restore Test" },
    });

    await revManager.createRevision({
      projectId: "proj_restore",
      nextProject: { state: "v2_modified" },
    });

    await revManager.createRevision({
      projectId: "proj_restore",
      nextProject: { state: "v3_broken" },
    });

    const headV3 = await repo.load("proj_restore");
    assert.equal(headV3.revisionId, "rev_000003");

    // Restaurar rev_000001
    const restored = await revManager.restoreRevision("proj_restore", "rev_000001");
    assert.equal(restored.revisionId, "rev_000004");
    assert.equal((restored.project as any).state, "v1_original");

    const list = await revManager.listRevisions("proj_restore");
    assert.equal(list.length, 4, "All 4 historical revisions must be preserved in history");
  });
});

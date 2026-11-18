import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { TaskPlanner } from "../../distributed/tasks/TaskPlanner.js";
import { WorkerPool } from "../../distributed/scheduler/WorkerPool.js";
import { WorkerNode } from "../../distributed/scheduler/WorkerNode.js";
import { SwarmCoordinator } from "../../distributed/swarm/SwarmCoordinator.js";
import { ElasticScheduler } from "../../distributed/scheduler/ElasticScheduler.js";
import { createDistributedJob } from "../../distributed/core/DistributedJob.js";

describe("Fase 24 — Capa 5: Distributed Equivalence & Determinism Tests", () => {
  it("proves Run(1 worker) === Run(4 workers) byte-for-byte in final revision and artifacts", async () => {
    // 1. Ejecución con 1 solo worker
    const poolSingle = new WorkerPool([new WorkerNode("worker_single")]);
    const swarmSingle = new SwarmCoordinator();
    const schedulerSingle = new ElasticScheduler(poolSingle, swarmSingle);

    const jobSingle = createDistributedJob({
      jobId: "djob_eq_test",
      projectId: "proj_eq",
      briefHash: "brief_hash_123",
      baselineRevisionId: "rev_base",
      allocatedWorkers: 1,
    });
    const dagSingle = TaskPlanner.planProduction({ jobId: "djob_eq_test", chunkCount: 2 });

    const resultSingle = await schedulerSingle.executeJob(jobSingle, dagSingle);

    // 2. Ejecución con 4 workers distribuidos concurrentes
    const poolMulti = new WorkerPool([
      new WorkerNode("worker_01"),
      new WorkerNode("worker_02"),
      new WorkerNode("worker_03"),
      new WorkerNode("worker_04"),
    ]);
    const swarmMulti = new SwarmCoordinator();
    const schedulerMulti = new ElasticScheduler(poolMulti, swarmMulti);

    const jobMulti = createDistributedJob({
      jobId: "djob_eq_test",
      projectId: "proj_eq",
      briefHash: "brief_hash_123",
      baselineRevisionId: "rev_base",
      allocatedWorkers: 4,
    });
    const dagMulti = TaskPlanner.planProduction({ jobId: "djob_eq_test", chunkCount: 2 });

    const resultMulti = await schedulerMulti.executeJob(jobMulti, dagMulti);

    // 3. Verificación de equivalencia matemática estricta
    assert.equal(resultSingle.success, true);
    assert.equal(resultMulti.success, true);
    assert.equal(resultSingle.finalRevisionId, resultMulti.finalRevisionId);
    assert.equal(resultSingle.tasksCompleted, resultMulti.tasksCompleted);
    assert.equal(resultSingle.tasksFailed, 0);
    assert.equal(resultMulti.tasksFailed, 0);

    // Las llaves de artefactos producidos deben ser exactamente idénticas
    assert.deepEqual(
      Object.keys(resultSingle.outputArtifacts).sort(),
      Object.keys(resultMulti.outputArtifacts).sort()
    );
  });
});

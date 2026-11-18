import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { TaskDAG } from "../../distributed/tasks/TaskDAG.js";
import { createTaskDefinition } from "../../distributed/tasks/TaskDefinition.js";
import { WorkerPool } from "../../distributed/scheduler/WorkerPool.js";
import { WorkerNode } from "../../distributed/scheduler/WorkerNode.js";
import { ElasticScheduler } from "../../distributed/scheduler/ElasticScheduler.js";
import { createDistributedJob } from "../../distributed/core/DistributedJob.js";

describe("Fase 24 — Capa 7: Distributed Performance & Scalability Benchmarks", () => {
  it("benchmarks topological sorting and execution of 500 tasks across a scaled worker pool", async () => {
    const taskCount = 500;
    const dag = new TaskDAG();

    // Crear un grafo denso de 500 tareas (cadena de etapas paralelas)
    for (let i = 0; i < taskCount; i++) {
      const deps = i > 0 && i % 10 === 0 ? [`task_bench_${i - 10}`] : [];
      dag.addTask(
        createTaskDefinition({
          taskId: `task_bench_${i}`,
          jobId: "bench_job",
          type: "render_chunk",
          dependencies: deps,
          payload: { index: i },
        })
      );
    }

    const t0 = performance.now();
    const order = dag.getTopologicalOrder();
    const sortElapsed = performance.now() - t0;

    assert.equal(order.length, taskCount);
    assert.ok(sortElapsed < 50, `Topological sort for 500 tasks took ${sortElapsed.toFixed(2)}ms (budget < 50ms)`);

    // Pool de 8 workers
    const pool = new WorkerPool();
    pool.scale(8);
    const scheduler = new ElasticScheduler(pool);

    const job = createDistributedJob({
      jobId: "bench_job",
      projectId: "bench_proj",
      briefHash: "hash_bench",
      baselineRevisionId: "rev_0",
      allocatedWorkers: 8,
    });

    const t1 = performance.now();
    const result = await scheduler.executeJob(job, dag);
    const execElapsed = performance.now() - t1;

    assert.equal(result.success, true);
    assert.equal(result.tasksCompleted, taskCount);
    assert.ok(execElapsed < 300, `Execution of 500 tasks took ${execElapsed.toFixed(2)}ms (budget < 300ms)`);
  });
});

import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { WorkerPool } from "../../distributed/scheduler/WorkerPool.js";
import { WorkerNode } from "../../distributed/scheduler/WorkerNode.js";
import { LoadBalancer } from "../../distributed/scheduler/LoadBalancer.js";
import { HeartbeatMonitor } from "../../distributed/scheduler/HeartbeatMonitor.js";
import { WorkStealingEngine } from "../../distributed/scheduler/WorkStealingEngine.js";
import { createTaskDefinition } from "../../distributed/tasks/TaskDefinition.js";
import { createTaskLease } from "../../distributed/tasks/TaskLease.js";

describe("Fase 24 — Capa 4: WorkerPool, LoadBalancer, Heartbeats & WorkStealing Tests", () => {
  it("WorkerPool scales dynamically and filters available workers", () => {
    const pool = new WorkerPool();
    assert.equal(pool.size, 0);

    pool.scale(4);
    assert.equal(pool.size, 4);

    const available = pool.getAvailableWorkers();
    assert.equal(available.length, 4);
  });

  it("LoadBalancer balances tasks across workers in least_loaded mode", () => {
    const pool = new WorkerPool([
      new WorkerNode("w_01"),
      new WorkerNode("w_02"),
    ]);

    const lb = new LoadBalancer(pool);
    const t1 = createTaskDefinition({ taskId: "t1", jobId: "j1", type: "render_chunk" });
    const t2 = createTaskDefinition({ taskId: "t2", jobId: "j1", type: "render_chunk" });

    const selected1 = lb.selectWorker(t1, "least_loaded");
    assert.equal(selected1.workerId, "w_01");
    selected1.assignTask(t1);

    // Con w_01 ocupado con 1 tarea, t2 debe ir a w_02
    const selected2 = lb.selectWorker(t2, "least_loaded");
    assert.equal(selected2.workerId, "w_02");
  });

  it("HeartbeatMonitor detects expired leases based on logical time", () => {
    const pool = new WorkerPool([new WorkerNode("w_01")]);
    const monitor = new HeartbeatMonitor(pool);

    const lease = createTaskLease({
      taskId: "task_exp",
      workerId: "w_01",
      attemptNumber: 1,
      acquiredAtLogical: 10,
      leaseDurationTicks: 5, // expira en tick 15
    });

    monitor.registerLease(lease);

    // En tick 12 sigue activo
    let expired = monitor.checkExpiredLeases(12);
    assert.equal(expired.length, 0);

    // En tick 16 ha expirado
    expired = monitor.checkExpiredLeases(16);
    assert.equal(expired.length, 1);
    assert.equal(expired[0].taskId, "task_exp");
    assert.equal(expired[0].active, false);
  });

  it("WorkStealingEngine balances load between overloaded and idle workers", () => {
    const wBusy = new WorkerNode("w_busy");
    const wIdle = new WorkerNode("w_idle");

    const t1 = createTaskDefinition({ taskId: "t1", jobId: "j1", type: "render_chunk" });
    const t2 = createTaskDefinition({ taskId: "t2", jobId: "j1", type: "render_chunk" });

    wBusy.assignTask(t1);
    wBusy.assignTask(t2); // w_busy tiene 2 tareas

    const pool = new WorkerPool([wBusy, wIdle]);
    const engine = new WorkStealingEngine(pool);

    const plans = engine.balance();
    assert.equal(plans.length, 1);
    assert.equal(plans[0].taskId, "t2");
    assert.equal(plans[0].fromWorkerId, "w_busy");
    assert.equal(plans[0].toWorkerId, "w_idle");

    assert.equal(wBusy.activeTasks.size, 1);
    assert.equal(wIdle.activeTasks.size, 1);
  });
});

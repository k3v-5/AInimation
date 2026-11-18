import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { TaskDAG } from "../../distributed/tasks/TaskDAG.js";
import { createTaskDefinition } from "../../distributed/tasks/TaskDefinition.js";
import { TaskPlanner } from "../../distributed/tasks/TaskPlanner.js";
import { TaskDAGCycleError, TaskNotFoundError } from "../../distributed/core/DistributedErrors.js";

describe("Fase 24 — Capa 2: TaskDAG, TopoSort & Cycle Detection Tests", () => {
  it("sorts linear tasks in topological order deterministically", () => {
    const dag = new TaskDAG();
    const t1 = createTaskDefinition({ taskId: "task_a", jobId: "job_1", type: "plan_story" });
    const t2 = createTaskDefinition({ taskId: "task_b", jobId: "job_1", type: "edit_timeline", dependencies: ["task_a"] });
    const t3 = createTaskDefinition({ taskId: "task_c", jobId: "job_1", type: "mux_export", dependencies: ["task_b"] });

    dag.addTask(t3).addTask(t1).addTask(t2); // agregado desordenado

    const order = dag.getTopologicalOrder();
    assert.deepEqual(order, ["task_a", "task_b", "task_c"]);
  });

  it("resolves ready tasks as dependencies complete", () => {
    const dag = new TaskDAG();
    const t1 = createTaskDefinition({ taskId: "t1", jobId: "j1", type: "plan_story" });
    const t2 = createTaskDefinition({ taskId: "t2", jobId: "j1", type: "design_motion", dependencies: ["t1"] });
    const t3 = createTaskDefinition({ taskId: "t3", jobId: "j1", type: "mix_audio", dependencies: ["t1"] });
    const t4 = createTaskDefinition({ taskId: "t4", jobId: "j1", type: "mux_export", dependencies: ["t2", "t3"] });

    dag.addTask(t1).addTask(t2).addTask(t3).addTask(t4);

    const completed = new Set<string>();

    // Inicialmente solo t1 está lista
    let ready = dag.getReadyTasks(completed);
    assert.deepEqual(ready.map((t) => t.taskId), ["t1"]);

    // Completar t1 -> t2 y t3 quedan listas
    completed.add("t1");
    ready = dag.getReadyTasks(completed);
    assert.deepEqual(ready.map((t) => t.taskId), ["t2", "t3"]);

    // Completar t2 -> t3 sigue lista, pero t4 no hasta que t3 termine
    completed.add("t2");
    ready = dag.getReadyTasks(completed);
    assert.deepEqual(ready.map((t) => t.taskId), ["t3"]);

    // Completar t3 -> t4 queda lista
    completed.add("t3");
    ready = dag.getReadyTasks(completed);
    assert.deepEqual(ready.map((t) => t.taskId), ["t4"]);
  });

  it("detects cycle in TaskDAG and throws TaskDAGCycleError", () => {
    const dag = new TaskDAG();
    const t1 = createTaskDefinition({ taskId: "t1", jobId: "j1", type: "plan_story", dependencies: ["t3"] });
    const t2 = createTaskDefinition({ taskId: "t2", jobId: "j1", type: "design_motion", dependencies: ["t1"] });
    const t3 = createTaskDefinition({ taskId: "t3", jobId: "j1", type: "mix_audio", dependencies: ["t2"] });

    dag.addTask(t1).addTask(t2).addTask(t3);

    assert.throws(() => {
      dag.getTopologicalOrder();
    }, TaskDAGCycleError);
  });

  it("throws TaskNotFoundError when a task depends on a non-existent task", () => {
    const dag = new TaskDAG();
    const t1 = createTaskDefinition({ taskId: "t1", jobId: "j1", type: "plan_story", dependencies: ["unknown_dep"] });
    dag.addTask(t1);

    assert.throws(() => {
      dag.getTopologicalOrder();
    }, TaskNotFoundError);
  });

  it("TaskPlanner creates a valid, acyclic standard production DAG", () => {
    const dag = TaskPlanner.planProduction({ jobId: "job_full", chunkCount: 3 });
    assert.equal(dag.size, 9); // plan + edit + motion + audio + 3 chunks + qa + mux = 9 tasks

    const order = dag.getTopologicalOrder();
    assert.equal(order.length, 9);
    assert.ok(order[0].endsWith("_plan"));
    assert.ok(order[order.length - 1].endsWith("_mux_export"));
  });
});

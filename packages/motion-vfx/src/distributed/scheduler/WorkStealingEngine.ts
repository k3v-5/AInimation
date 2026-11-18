import { WorkerPool } from "./WorkerPool.js";
import { TaskDefinition } from "../tasks/TaskDefinition.js";

export interface StolenTaskPlan {
  taskId: string;
  fromWorkerId: string;
  toWorkerId: string;
}

export class WorkStealingEngine {
  constructor(private _pool: WorkerPool) {}

  public balance(): StolenTaskPlan[] {
    const plans: StolenTaskPlan[] = [];
    const workers = this._pool.workers;

    const busyWorkers = workers.filter((w) => w.activeTasks.size > 1);
    const idleWorkers = workers.filter((w) => w.state === "idle" && w.activeTasks.size === 0);

    for (const busy of busyWorkers) {
      if (idleWorkers.length === 0) break;
      const idle = idleWorkers.shift()!;

      // Robar la última tarea asignada
      const tasks = Array.from(busy.activeTasks.values());
      const taskToSteal = tasks[tasks.length - 1];

      if (idle.canAccept(taskToSteal)) {
        busy.activeTasks.delete(taskToSteal.taskId);
        idle.assignTask(taskToSteal);
        plans.push({
          taskId: taskToSteal.taskId,
          fromWorkerId: busy.workerId,
          toWorkerId: idle.workerId,
        });
      }
    }

    return plans;
  }
}

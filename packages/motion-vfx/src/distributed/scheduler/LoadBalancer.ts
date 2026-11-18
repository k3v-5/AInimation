import { WorkerPool } from "./WorkerPool.js";
import { WorkerNode } from "./WorkerNode.js";
import { TaskDefinition } from "../tasks/TaskDefinition.js";
import { WorkerUnavailableError } from "../core/DistributedErrors.js";

export class LoadBalancer {
  private _roundRobinIndex = 0;

  constructor(private _pool: WorkerPool) {}

  public selectWorker(
    task: TaskDefinition,
    strategy: "least_loaded" | "round_robin" | "affinity" = "least_loaded"
  ): WorkerNode {
    const candidates = this._pool.getAvailableWorkers().filter((w) => w.canAccept(task));

    if (candidates.length === 0) {
      throw new WorkerUnavailableError("no_worker", { taskId: task.taskId, type: task.type });
    }

    if (strategy === "least_loaded") {
      // Ordenar por menor carga, desempate por workerId lexicográfico
      candidates.sort((a, b) => a.activeTasks.size - b.activeTasks.size || a.workerId.localeCompare(b.workerId));
      return candidates[0];
    }

    if (strategy === "round_robin") {
      const idx = this._roundRobinIndex % candidates.length;
      this._roundRobinIndex++;
      return candidates[idx];
    }

    // Affinity por taskId / requiredRole
    let hashVal = 0;
    for (let i = 0; i < task.taskId.length; i++) {
      hashVal = (hashVal << 5) - hashVal + task.taskId.charCodeAt(i);
      hashVal |= 0;
    }
    const affIdx = Math.abs(hashVal) % candidates.length;
    return candidates[affIdx];
  }
}

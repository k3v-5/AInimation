import { TaskDefinition } from "./TaskDefinition.js";
import { TaskDAGCycleError, TaskNotFoundError } from "../core/DistributedErrors.js";
import { ProjectSerializer } from "../../persistence/ProjectSerializer.js";

export class TaskDAG {
  private _tasks: Map<string, TaskDefinition> = new Map();

  constructor(tasks: TaskDefinition[] = []) {
    for (const t of tasks) {
      this.addTask(t);
    }
  }

  public addTask(task: TaskDefinition): this {
    this._tasks.set(task.taskId, { ...task });
    return this;
  }

  public getTask(taskId: string): TaskDefinition | undefined {
    return this._tasks.get(taskId);
  }

  public hasTask(taskId: string): boolean {
    return this._tasks.has(taskId);
  }

  public get tasks(): TaskDefinition[] {
    return Array.from(this._tasks.values());
  }

  public get size(): number {
    return this._tasks.size;
  }

  /**
   * Ordenamiento topológico determinista (Kahn) con detección de ciclos.
   */
  public getTopologicalOrder(): string[] {
    const inDegree: Map<string, number> = new Map();
    const adj: Map<string, string[]> = new Map();

    for (const taskId of this._tasks.keys()) {
      inDegree.set(taskId, 0);
      adj.set(taskId, []);
    }

    for (const task of this._tasks.values()) {
      for (const depId of task.dependencies) {
        if (!this._tasks.has(depId)) {
          throw new TaskNotFoundError(depId, { contextTaskId: task.taskId });
        }
        adj.get(depId)!.push(task.taskId);
        inDegree.set(task.taskId, (inDegree.get(task.taskId) ?? 0) + 1);
      }
    }

    // Usar cola ordenada lexicográficamente para determinismo absoluto
    const queue: string[] = [];
    for (const [taskId, deg] of inDegree.entries()) {
      if (deg === 0) {
        queue.push(taskId);
      }
    }
    queue.sort();

    const result: string[] = [];

    while (queue.length > 0) {
      const u = queue.shift()!;
      result.push(u);

      const neighbors = adj.get(u) ?? [];
      // Ordenar vecinos antes de procesar
      neighbors.sort();
      for (const v of neighbors) {
        const nextDeg = inDegree.get(v)! - 1;
        inDegree.set(v, nextDeg);
        if (nextDeg === 0) {
          queue.push(v);
          queue.sort();
        }
      }
    }

    if (result.length !== this._tasks.size) {
      const remaining = Array.from(inDegree.entries())
        .filter(([_, deg]) => deg > 0)
        .map(([id]) => id);
      throw new TaskDAGCycleError(remaining);
    }

    return result;
  }

  /**
   * Obtiene las tareas listas para ser ejecutadas (cuyas dependencias ya se completaron).
   */
  public getReadyTasks(completedTaskIds: Set<string>): TaskDefinition[] {
    const ready: TaskDefinition[] = [];

    for (const task of this._tasks.values()) {
      if (completedTaskIds.has(task.taskId)) {
        continue;
      }
      if (task.status === "completed" || task.status === "running" || task.status === "leased") {
        continue;
      }
      const allDepsMet = task.dependencies.every((depId) => completedTaskIds.has(depId));
      if (allDepsMet) {
        ready.push(task);
      }
    }

    // Ordenar lexicográficamente por taskId
    return ready.sort((a, b) => a.taskId.localeCompare(b.taskId));
  }

  public computeDAGHash(): string {
    const topo = this.getTopologicalOrder();
    const serializedTasks = topo.map((id) => this._tasks.get(id)!.deterministicHash);
    return ProjectSerializer.hashCanonical(serializedTasks);
  }
}

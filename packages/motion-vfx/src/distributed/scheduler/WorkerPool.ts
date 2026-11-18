import { WorkerNode } from "./WorkerNode.js";
import { WorkerUnavailableError } from "../core/DistributedErrors.js";

export class WorkerPool {
  private _workers: Map<string, WorkerNode> = new Map();

  constructor(initialWorkers: WorkerNode[] = []) {
    for (const w of initialWorkers) {
      this.registerWorker(w);
    }
  }

  public registerWorker(worker: WorkerNode): this {
    this._workers.set(worker.workerId, worker);
    return this;
  }

  public unregisterWorker(workerId: string): boolean {
    return this._workers.delete(workerId);
  }

  public getWorker(workerId: string): WorkerNode | undefined {
    return this._workers.get(workerId);
  }

  public get workers(): WorkerNode[] {
    return Array.from(this._workers.values()).sort((a, b) => a.workerId.localeCompare(b.workerId));
  }

  public get size(): number {
    return this._workers.size;
  }

  public getAvailableWorkers(): WorkerNode[] {
    return this.workers.filter((w) => w.state === "idle" || w.state === "busy");
  }

  public scale(targetCount: number): void {
    const current = this._workers.size;
    if (targetCount > current) {
      for (let i = current; i < targetCount; i++) {
        const id = `worker_${String(i + 1).padStart(2, "0")}`;
        if (!this._workers.has(id)) {
          this.registerWorker(new WorkerNode(id));
        }
      }
    } else if (targetCount < current) {
      const toRemove = this.workers.slice(targetCount);
      for (const w of toRemove) {
        if (w.activeTasks.size === 0) {
          this._workers.delete(w.workerId);
        } else {
          w.state = "draining";
        }
      }
    }
  }
}

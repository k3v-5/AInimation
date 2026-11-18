import { WorkerPool } from "../scheduler/WorkerPool.js";

export interface ClusterStatus {
  totalWorkers: number;
  idleWorkers: number;
  busyWorkers: number;
  drainingWorkers: number;
  activeTasks: number;
  timestampLogical: number;
}

export function computeClusterStatus(pool: WorkerPool, logicalTime = 1): ClusterStatus {
  const workers = pool.workers;
  let idle = 0;
  let busy = 0;
  let draining = 0;
  let activeTasks = 0;

  for (const w of workers) {
    activeTasks += w.activeTasks.size;
    if (w.state === "idle") idle++;
    else if (w.state === "busy") busy++;
    else if (w.state === "draining") draining++;
  }

  return {
    totalWorkers: workers.length,
    idleWorkers: idle,
    busyWorkers: busy,
    drainingWorkers: draining,
    activeTasks,
    timestampLogical: logicalTime,
  };
}

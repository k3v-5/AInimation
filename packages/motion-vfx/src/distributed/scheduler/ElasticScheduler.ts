import { TaskDAG } from "../tasks/TaskDAG.js";
import { TaskDefinition } from "../tasks/TaskDefinition.js";
import { TaskResult } from "../tasks/TaskResult.js";
import { createTaskLease } from "../tasks/TaskLease.js";
import { WorkerPool } from "./WorkerPool.js";
import { LoadBalancer } from "./LoadBalancer.js";
import { HeartbeatMonitor } from "./HeartbeatMonitor.js";
import { SwarmCoordinator } from "../swarm/SwarmCoordinator.js";
import { AgentProposal } from "../swarm/AgentProposal.js";
import { DistributedJob } from "../core/DistributedJob.js";
import { DistributedResult, createDistributedResult } from "../core/DistributedResult.js";
import { TaskExecutionTimeoutError, WorkerUnavailableError } from "../core/DistributedErrors.js";

export class ElasticScheduler {
  private _loadBalancer: LoadBalancer;
  private _heartbeatMonitor: HeartbeatMonitor;

  constructor(
    private _pool: WorkerPool,
    private _swarm?: SwarmCoordinator
  ) {
    this._loadBalancer = new LoadBalancer(this._pool);
    this._heartbeatMonitor = new HeartbeatMonitor(this._pool);
  }

  public async executeJob(job: DistributedJob, dag: TaskDAG): Promise<DistributedResult> {
    const startTime = Date.now();
    job.status = "executing";
    job.taskCount = dag.size;

    const completedTaskIds: Set<string> = new Set();
    const taskResults: Map<string, TaskResult> = new Map();
    const proposals: AgentProposal[] = [];
    const consolidatedArtifacts: Record<string, string> = {};

    let logicalTicks = job.createdAtLogical;

    while (completedTaskIds.size < dag.size) {
      logicalTicks++;
      const readyTasks = dag.getReadyTasks(completedTaskIds);

      if (readyTasks.length === 0 && completedTaskIds.size < dag.size) {
        // Ninguna tarea lista pero faltan tareas: posible deadlock o fallo no recuperado
        break;
      }

      for (const task of readyTasks) {
        task.status = "leased";
        task.attemptCount++;

        // Si es tarea de agente y tenemos SwarmCoordinator, la procesa el enjambre
        if (this._swarm && task.requiredRole) {
          task.status = "running";
          const proposal = await this._swarm.dispatchTask(task, job.baselineRevisionId);
          proposals.push(proposal);
          task.status = "completed";
          completedTaskIds.add(task.taskId);
          job.completedTasks++;
          continue;
        }

        // Tarea de cómputo general (render, audio mix, mux)
        const worker = this._loadBalancer.selectWorker(task, "least_loaded");
        const lease = createTaskLease({
          taskId: task.taskId,
          workerId: worker.workerId,
          attemptNumber: task.attemptCount,
          acquiredAtLogical: logicalTicks,
          leaseDurationTicks: 10,
        });

        this._heartbeatMonitor.registerLease(lease);
        task.status = "running";

        try {
          const result = await worker.executeTask(task);
          taskResults.set(task.taskId, result);

          if (result.outputArtifacts) {
            Object.assign(consolidatedArtifacts, result.outputArtifacts);
          }

          task.status = "completed";
          completedTaskIds.add(task.taskId);
          job.completedTasks++;
        } catch (err: any) {
          task.status = "failed";
          job.failedTasks++;
          if (task.attemptCount >= task.retryPolicy.maxAttempts) {
            job.status = "failed";
            throw err;
          }
        }
      }
    }

    // Si hubo propuestas del enjambre, las fusiona con ThreeWayMergeArbiter
    let finalRevisionId = job.baselineRevisionId;
    if (this._swarm && proposals.length > 0) {
      job.status = "merging";
      const mergeResult = this._swarm.mergeProposals(proposals, job.baselineRevisionId);
      finalRevisionId = `rev_merged_${mergeResult.deterministicHash.slice(0, 12)}`;
    }

    const success = job.completedTasks === dag.size && job.failedTasks === 0;
    job.status = success ? "completed" : "failed";
    job.resultingRevisionId = finalRevisionId;

    return createDistributedResult({
      job,
      success,
      finalRevisionId,
      totalDurationMs: Date.now() - startTime,
      outputArtifacts: consolidatedArtifacts,
    });
  }
}

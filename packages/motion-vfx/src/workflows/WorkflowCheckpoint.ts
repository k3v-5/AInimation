import { ProjectSerializer } from "../persistence/ProjectSerializer.js";

export interface WorkflowCheckpoint {
  checkpointId: string;
  workflowId: string;
  projectId: string;
  stepId: string;
  revisionId: string;
  completedSteps: string[];
  variables: Record<string, unknown>;
  checkpointHash: string;
  createdAt: string;
}

/**
 * Gestor de persistencia de checkpoints para reanudación resiliente de workflows (Fase 18).
 */
export class CheckpointManager {
  private checkpoints = new Map<string, WorkflowCheckpoint[]>(); // workflowId -> checkpoints[]

  public saveCheckpoint(cp: Omit<WorkflowCheckpoint, "checkpointId" | "checkpointHash" | "createdAt">): WorkflowCheckpoint {
    const payload = {
      workflowId: cp.workflowId,
      projectId: cp.projectId,
      stepId: cp.stepId,
      revisionId: cp.revisionId,
      completedSteps: cp.completedSteps,
      variables: cp.variables,
    };

    const checkpointHash = ProjectSerializer.hashCanonical(payload);
    const checkpointId = `cp_${checkpointHash.slice(0, 16)}`;

    const fullCheckpoint: WorkflowCheckpoint = {
      ...cp,
      checkpointId,
      checkpointHash,
      createdAt: new Date().toISOString(),
    };

    let list = this.checkpoints.get(cp.workflowId);
    if (!list) {
      list = [];
      this.checkpoints.set(cp.workflowId, list);
    }
    list.push(fullCheckpoint);

    return fullCheckpoint;
  }

  public getLatestCheckpoint(workflowId: string): WorkflowCheckpoint | undefined {
    const list = this.checkpoints.get(workflowId);
    if (!list || list.length === 0) return undefined;
    return list[list.length - 1];
  }

  public getCheckpoints(workflowId: string): WorkflowCheckpoint[] {
    return this.checkpoints.get(workflowId) ?? [];
  }

  public clear(workflowId: string): void {
    this.checkpoints.delete(workflowId);
  }
}

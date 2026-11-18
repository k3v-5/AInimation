import { CheckpointManager, WorkflowCheckpoint } from "./WorkflowCheckpoint.js";
import { WorkflowContext } from "./WorkflowContext.js";
import { WorkflowDefinition, WorkflowStepDefinition } from "./WorkflowDefinition.js";
import { WorkflowPlanner } from "./WorkflowPlanner.js";

/**
 * Subsistema de reanudación y recuperación de workflows interrumpidos (Fase 18).
 */
export class WorkflowRecovery {
  public static prepareResume(params: {
    definition: WorkflowDefinition;
    context: WorkflowContext;
    checkpointManager: CheckpointManager;
  }): { remainingSteps: WorkflowStepDefinition[]; checkpoint?: WorkflowCheckpoint } {
    const planned = WorkflowPlanner.planExecution(params.definition);
    const latestCp = params.checkpointManager.getLatestCheckpoint(params.context.workflowId);

    if (!latestCp) {
      return { remainingSteps: planned };
    }

    // Restaurar variables del checkpoint que no hayan sido sobreescritas explícitamente en el contexto actual
    for (const [k, v] of Object.entries(latestCp.variables)) {
      if (!params.context.variables.has(k)) {
        params.context.set(k, v);
      }
    }
    params.context.revisionId = latestCp.revisionId;

    const completedSet = new Set<string>(latestCp.completedSteps);
    const remainingSteps = planned.filter((step) => !completedSet.has(step.id));

    return { remainingSteps, checkpoint: latestCp };
  }
}

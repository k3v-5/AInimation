import { CheckpointManager } from "./WorkflowCheckpoint.js";
import { WorkflowContext } from "./WorkflowContext.js";
import { WorkflowDefinition, WorkflowStepDefinition } from "./WorkflowDefinition.js";
import { WorkflowPlanner } from "./WorkflowPlanner.js";
import { WorkflowRecovery } from "./WorkflowRecovery.js";
import { StepExecutionResult, WorkflowResult } from "./WorkflowResult.js";
import { WorkflowState } from "./WorkflowState.js";
import { StepRegistry } from "./WorkflowStep.js";
import { WorkflowCancelledError, WorkflowExecutionError, WorkflowNotFoundError } from "./errors/workflow-errors.js";

/**
 * Motor de orquestación asíncrono y resiliente de workflows (Fase 18).
 */
export class WorkflowEngine {
  private definitions = new Map<string, WorkflowDefinition>();
  private activeStates = new Map<string, WorkflowState>();
  private cancellations = new Set<string>();
  private checkpointManager = new CheckpointManager();

  public registerWorkflow(definition: WorkflowDefinition): void {
    this.definitions.set(definition.id, definition);
  }

  public getWorkflowDefinition(workflowId: string): WorkflowDefinition | undefined {
    return this.definitions.get(workflowId);
  }

  public getWorkflowState(workflowId: string): WorkflowState {
    return this.activeStates.get(workflowId) ?? "pending";
  }

  public cancelWorkflow(workflowId: string, reason = "User requested cancellation"): void {
    this.cancellations.add(workflowId);
    this.activeStates.set(workflowId, "cancelled");
  }

  /**
   * Ejecuta un workflow desde el inicio.
   */
  public async executeWorkflow(params: {
    definition: WorkflowDefinition;
    context: WorkflowContext;
  }): Promise<WorkflowResult> {
    const plannedSteps = WorkflowPlanner.planExecution(params.definition);
    return this.runSteps(params.definition, plannedSteps, params.context, []);
  }

  /**
   * Reanuda un workflow desde su último checkpoint guardado.
   */
  public async resumeWorkflow(params: {
    definition: WorkflowDefinition;
    context: WorkflowContext;
  }): Promise<WorkflowResult> {
    const { remainingSteps, checkpoint } = WorkflowRecovery.prepareResume({
      definition: params.definition,
      context: params.context,
      checkpointManager: this.checkpointManager,
    });

    const alreadyCompleted = checkpoint ? checkpoint.completedSteps : [];
    return this.runSteps(params.definition, remainingSteps, params.context, alreadyCompleted);
  }

  private async runSteps(
    definition: WorkflowDefinition,
    stepsToRun: WorkflowStepDefinition[],
    context: WorkflowContext,
    initialCompletedSteps: string[]
  ): Promise<WorkflowResult> {
    const workflowId = context.workflowId;
    const startedAt = new Date().toISOString();
    const completedSteps = [...initialCompletedSteps];
    const stepResults: StepExecutionResult[] = [];
    const initialRevisionId = context.revisionId;

    if (this.cancellations.has(workflowId)) {
      this.activeStates.set(workflowId, "cancelled");
      return {
        workflowId,
        projectId: context.projectId,
        initialRevisionId,
        finalRevisionId: context.revisionId,
        status: "cancelled",
        completedSteps,
        stepResults,
        startedAt,
        completedAt: new Date().toISOString(),
        error: "Workflow was cancelled",
      };
    }

    this.activeStates.set(workflowId, "running");

    for (const step of stepsToRun) {
      if (this.cancellations.has(workflowId)) {
        this.activeStates.set(workflowId, "cancelled");
        return {
          workflowId,
          projectId: context.projectId,
          initialRevisionId,
          finalRevisionId: context.revisionId,
          status: "cancelled",
          completedSteps,
          stepResults,
          startedAt,
          completedAt: new Date().toISOString(),
          error: "Workflow was cancelled",
        };
      }

      const handler = StepRegistry.get(step.type);
      if (!handler) {
        const err = `No step handler registered for type '${step.type}'`;
        this.activeStates.set(workflowId, "failed");
        throw new WorkflowExecutionError(workflowId, step.id, err);
      }

      let attempt = 0;
      const maxAttempts = step.retryPolicy.maxAttempts;
      let stepSuccess = false;
      let lastError: Error | undefined;
      const t0 = performance.now();

      while (attempt < maxAttempts && !stepSuccess) {
        attempt++;
        try {
          const output = await handler(context, step.parameters);
          stepSuccess = true;
          const durationMs = performance.now() - t0;

          completedSteps.push(step.id);
          stepResults.push({
            stepId: step.id,
            status: "completed",
            durationMs,
            output,
          });

          // Guardar checkpoint tras paso exitoso si no es dryRun
          if (!context.dryRun) {
            const varsRecord: Record<string, unknown> = {};
            for (const [k, v] of context.variables.entries()) {
              varsRecord[k] = v;
            }

            this.checkpointManager.saveCheckpoint({
              workflowId,
              projectId: context.projectId,
              stepId: step.id,
              revisionId: context.revisionId,
              completedSteps,
              variables: varsRecord,
            });
          }
        } catch (err: any) {
          lastError = err;
          if (attempt < maxAttempts && step.retryPolicy.intervalMs > 0) {
            await new Promise((r) => setTimeout(r, step.retryPolicy.intervalMs));
          }
        }
      }

      if (!stepSuccess) {
        const durationMs = performance.now() - t0;
        stepResults.push({
          stepId: step.id,
          status: "failed",
          durationMs,
          error: lastError?.message,
        });

        this.activeStates.set(workflowId, "failed");
        return {
          workflowId,
          projectId: context.projectId,
          initialRevisionId,
          finalRevisionId: context.revisionId,
          status: "failed",
          completedSteps,
          stepResults,
          startedAt,
          completedAt: new Date().toISOString(),
          error: lastError?.message,
        };
      }
    }

    this.activeStates.set(workflowId, "completed");
    return {
      workflowId,
      projectId: context.projectId,
      initialRevisionId,
      finalRevisionId: context.revisionId,
      status: "completed",
      completedSteps,
      stepResults,
      startedAt,
      completedAt: new Date().toISOString(),
    };
  }

  public getCheckpointManager(): CheckpointManager {
    return this.checkpointManager;
  }
}

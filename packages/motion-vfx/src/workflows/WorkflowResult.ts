import { WorkflowState } from "./WorkflowState.js";

export interface StepExecutionResult {
  stepId: string;
  status: "completed" | "failed" | "skipped";
  durationMs: number;
  output?: unknown;
  error?: string;
}

export interface WorkflowResult {
  workflowId: string;
  projectId: string;
  initialRevisionId: string;
  finalRevisionId: string;
  status: WorkflowState;
  completedSteps: string[];
  stepResults: StepExecutionResult[];
  startedAt: string;
  completedAt?: string;
  error?: string;
}

/**
 * 1. User Intent
 * High-level intention representing the creative goal.
 */
export interface Intent {
  id: string;
  type: string; // e.g., "make_character_wave"
  parameters: Record<string, any>;
}

/**
 * 2. Animation Plan
 * Universal step-by-step plan independent of the provider.
 */
export interface Plan {
  id: string;
  intentId: string;
  steps: PlanStep[];
}

export interface PlanStep {
  id: string;
  capabilityId: CapabilityId;
  parameters: Record<string, any>;
}

/**
 * 3. Operation & Execution State Machine
 * Specific execution block with its own lifecycle.
 */
export type OperationStatus =
  | 'PLANNED'
  | 'VALIDATED'
  | 'QUEUED'
  | 'EXECUTING'
  | 'OBSERVING'
  | 'SUCCESS'
  | 'DIVERGED'
  | 'RECOVERY'
  | 'FAILED'
  | 'SKIPPED';

export interface Operation {
  id: string;
  planStepId: string;
  capability: CapabilityId;
  provider: string; // Resolves to a specific provider ID
  input: Record<string, any>;
  status: OperationStatus;
  startedAt?: number;
  completedAt?: number;
  attempts: number;
  result?: any;
  error?: string;
  observations?: any[];
}

/**
 * 4. Capability
 * Strict contract defining what an operation can do.
 */
export type CapabilityId = string;

export interface CapabilityDefinition {
  id: CapabilityId;
  // In a real system, these would be JSON schema objects or Zod definitions.
  inputSchema: Record<string, any>;
  outputSchema: Record<string, any>;

  prerequisites?: CapabilityId[];

  supports: "sync" | "async";

  reliability?: {
    level: "experimental" | "stable" | "production";
  };

  reversibility: "reversible" | "partially_reversible" | "irreversible";

  observability: "full" | "partial" | "none";
}

/**
 * 5. Provider
 * Implements capabilities and connects to the actual Runtime.
 */
export interface IAnimationProvider {
  id: string;
  capabilities(): CapabilityDefinition[];

  connect(): Promise<void>;
  disconnect(): Promise<void>;

  // Execution is now based on Capabilities rather than raw strings.
  executeCapability(capabilityId: CapabilityId, input: Record<string, any>, abortSignal?: AbortSignal): Promise<any>;
}

/**
 * 6. Artifact System
 * Versioned outcomes from operations that might be used by other steps.
 */
export type ArtifactType = 'scene' | 'timeline' | 'asset' | 'render' | 'puppet' | 'audio';

export interface Artifact {
  id: string;
  type: ArtifactType;
  version: number;
  sourceApp?: string;
  createdBy: string; // OperationId
  dependencies: string[]; // ArtifactIds
  metadata: Record<string, unknown>;
}

/**
 * 7 & 8. Entity State (Desired vs Observed)
 * Replaces pure Shadow State with a reconciliation model.
 */
export type EntityStateStatus = "unknown" | "synchronized" | "pending" | "diverged" | "error";

export interface EntityState<T> {
  desired: T;
  observed?: T;
  status: EntityStateStatus;
}

/**
 * 9. Workflow Graph
 * Represents the execution pipeline.
 */
export interface WorkflowNode {
  id: string;
  capability: CapabilityId;
  inputs: Artifact[];
  outputs: Artifact[];
  constraints?: any[];
}

export interface WorkflowGraph {
  nodes: WorkflowNode[];
  edges: { sourceId: string; targetId: string }[];
}

/**
 * 10. Validation & Recovery
 * Layer handling perception and self-healing.
 */
export interface ValidationResult {
  isValid: boolean;
  divergences?: string[]; // Descriptions of what diverged
}

export interface IValidationAndRecovery {
  validateState<T>(state: EntityState<T>): ValidationResult;
  attemptRecovery(operationId: string, engineExecuteCallback: (opId: string) => Promise<Operation>): Promise<boolean>;
}

export interface AgentAction {
  actionId: string;
  type: string;
  targetId?: string;
  parameters: Record<string, unknown>;
  timestamp?: string;
}

export interface AgentObservation {
  observationId: string;
  projectId: string;
  revisionId: string;
  summary: {
    layerCount: number;
    captionCount: number;
    duration: number;
    fps: number;
  };
  metrics?: Record<string, unknown>;
  timestamp?: string;
}

export interface AgentDecision {
  decisionId: string;
  agentId: string;
  action: AgentAction;
  rationale: string;
  expectedOutcome: string;
  timestamp?: string;
}

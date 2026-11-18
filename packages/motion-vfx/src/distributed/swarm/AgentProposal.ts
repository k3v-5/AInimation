import { AgentRole } from "./AgentRole.js";
import { ProjectSerializer } from "../../persistence/ProjectSerializer.js";

export interface ChangeOperation {
  type: string;
  targetId?: string;
  property?: string;
  path?: string;
  value?: unknown;
  before?: unknown;
  after?: unknown;
}

export interface ChangeSet {
  changeSetId: string;
  description: string;
  operations: ChangeOperation[];
}

export interface AgentProposal {
  proposalId: string;
  agentRole: AgentRole;
  baseRevisionId: string;
  changeSet: ChangeSet;
  confidence: number;
  rationale: string;
  deterministicHash: string;
}

export function createAgentProposal(params: {
  proposalId: string;
  agentRole: AgentRole;
  baseRevisionId: string;
  changeSet: ChangeSet;
  confidence?: number;
  rationale: string;
}): AgentProposal {
  const confidence = Math.max(0, Math.min(1, params.confidence ?? 1.0));
  const deterministicHash = ProjectSerializer.hashCanonical({
    proposalId: params.proposalId,
    agentRole: params.agentRole,
    baseRevisionId: params.baseRevisionId,
    changeSet: params.changeSet,
    confidence,
    rationale: params.rationale,
  });

  return {
    proposalId: params.proposalId,
    agentRole: params.agentRole,
    baseRevisionId: params.baseRevisionId,
    changeSet: params.changeSet,
    confidence,
    rationale: params.rationale,
    deterministicHash,
  };
}

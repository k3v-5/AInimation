import { AgentProposal, ChangeSet, ChangeOperation } from "./AgentProposal.js";
import { ProposalConflictError } from "../core/DistributedErrors.js";
import { ProjectSerializer } from "../../persistence/ProjectSerializer.js";

export interface MergeArbiterResult {
  mergedChangeSet: ChangeSet;
  appliedProposals: string[];
  conflictCount: number;
  deterministicHash: string;
}

export class ThreeWayMergeArbiter {
  /**
   * Fusiona concurrentemente un array de propuestas de agentes en un ChangeSet unificado.
   * Si dos propuestas modifican la misma propiedad de la misma entidad con valores incompatibles,
   * lanza ProposalConflictError con contexto exacto.
   */
  public static merge(proposals: AgentProposal[], baseRevisionId: string): MergeArbiterResult {
    if (proposals.length === 0) {
      const emptyChangeSet: ChangeSet = {
        changeSetId: `cs_empty_${baseRevisionId}`,
        description: "Empty merge",
        operations: [],
      };
      return {
        mergedChangeSet: emptyChangeSet,
        appliedProposals: [],
        conflictCount: 0,
        deterministicHash: ProjectSerializer.hashCanonical(emptyChangeSet),
      };
    }

    // Ordenar propuestas por agentRole y proposalId para determinismo estricto
    const sortedProposals = [...proposals].sort((a, b) =>
      a.agentRole.localeCompare(b.agentRole) || a.proposalId.localeCompare(b.proposalId)
    );

    const propertyMap: Map<string, { value: unknown; proposalId: string; op: ChangeOperation }> = new Map();
    const mergedOps: ChangeOperation[] = [];
    const appliedProposals: string[] = [];

    for (const prop of sortedProposals) {
      appliedProposals.push(prop.proposalId);
      for (const op of prop.changeSet.operations) {
        const key = `${op.targetId ?? "root"}::${op.property ?? "default"}::${op.type}`;
        if (propertyMap.has(key)) {
          const existing = propertyMap.get(key)!;
          const valA = JSON.stringify(existing.value);
          const valB = JSON.stringify(op.value);
          if (valA !== valB) {
            throw new ProposalConflictError(
              existing.proposalId,
              prop.proposalId,
              key,
              { valueA: existing.value, valueB: op.value }
            );
          }
        } else {
          propertyMap.set(key, { value: op.value, proposalId: prop.proposalId, op });
          mergedOps.push(op);
        }
      }
    }

    // Ordenar operaciones unificadas determinísticamente
    mergedOps.sort((a, b) => {
      const ka = `${a.targetId ?? ""}::${a.property ?? ""}::${a.type}`;
      const kb = `${b.targetId ?? ""}::${b.property ?? ""}::${b.type}`;
      return ka.localeCompare(kb);
    });

    const mergedChangeSet: ChangeSet = {
      changeSetId: `cs_merged_${ProjectSerializer.hashCanonical(appliedProposals).slice(0, 12)}`,
      description: `Consolidated merge from ${appliedProposals.length} swarm agent proposals`,
      operations: mergedOps,
    };

    const deterministicHash = ProjectSerializer.hashCanonical({
      mergedChangeSet,
      appliedProposals,
    });

    return {
      mergedChangeSet,
      appliedProposals,
      conflictCount: 0,
      deterministicHash,
    };
  }
}

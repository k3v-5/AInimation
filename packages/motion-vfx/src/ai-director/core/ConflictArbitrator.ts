import { AgentConflict, ConflictResolution, DirectorPolicy } from "../types/index.js";

/**
 * Árbitro determinista de discrepancias y conflictos entre agentes especialistas (Fase 8).
 */
export class ConflictArbitrator {
  public static readonly DEFAULT_POLICY: DirectorPolicy = {
    priorities: ["narrative", "audio_beat", "visual", "platform"],
    maxIterations: 3,
    qualityThreshold: 0.85,
  };

  /**
   * Resuelve un conflicto entre recomendaciones de diferentes agentes.
   */
  public static resolve(
    conflict: AgentConflict,
    policy: DirectorPolicy = this.DEFAULT_POLICY
  ): ConflictResolution {
    if (conflict.proposals.length === 0) {
      return {
        selectedProposalIndex: -1,
        reasoning: "No proposals to arbitrate.",
        resolvedParameters: {},
      };
    }

    // Ordenar propuestas por prioridad descendente
    let bestIndex = 0;
    let highestPriority = -Infinity;

    for (let i = 0; i < conflict.proposals.length; i++) {
      const p = conflict.proposals[i];
      if (p.priority > highestPriority) {
        highestPriority = p.priority;
        bestIndex = i;
      }
    }

    const winningProposal = conflict.proposals[bestIndex];

    return {
      selectedProposalIndex: bestIndex,
      reasoning: `Selected proposal '${winningProposal.type}' by agent priority ${winningProposal.priority} following Director policy: ${policy.priorities.join(" > ")}.`,
      resolvedParameters: { ...winningProposal.parameters },
    };
  }
}

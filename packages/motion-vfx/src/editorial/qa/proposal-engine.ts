import { EditorialIR } from "../ir/editorial-ir.types.js";
import { ChecksumMismatchError, EditorialProposal } from "./types.js";
import { MathUtils } from "../attention/math-utils.js";

export interface ApplyProposalResult {
  candidateIR: EditorialIR;
  candidateChecksum: string;
}

/**
 * REQ-4I-043 a REQ-4I-045 & REQ-4I-099: Proposal-First Engine.
 * Implements non-destructive patching of Editorial IR with cryptographic checksum precondition checking.
 */
export class ProposalEngine {
  public static createProposal(params: {
    id: string;
    type: string;
    reason: string;
    confidence: number;
    baseIR: EditorialIR;
    patch: (clonedIR: EditorialIR) => void;
  }): { proposal: EditorialProposal; apply: () => ApplyProposalResult } {
    const beforeChecksum = MathUtils.computeCanonicalSha256(params.baseIR);

    const proposal: EditorialProposal = {
      id: params.id,
      type: params.type,
      reason: params.reason,
      confidence: params.confidence,
      beforeChecksum,
      candidatePatch: { type: params.type },
    };

    const apply = (): ApplyProposalResult => {
      // Check concurrency / checksum precondition
      const currentChecksum = MathUtils.computeCanonicalSha256(params.baseIR);
      if (currentChecksum !== beforeChecksum) {
        throw new ChecksumMismatchError(
          `Cannot apply proposal ${params.id}: base IR checksum has changed from ${beforeChecksum} to ${currentChecksum}.`
        );
      }

      // Deep clone base IR
      const clonedIR: EditorialIR = JSON.parse(JSON.stringify(params.baseIR));

      // Apply patch to clone
      params.patch(clonedIR);

      const candidateChecksum = MathUtils.computeCanonicalSha256(clonedIR);

      return {
        candidateIR: clonedIR,
        candidateChecksum,
      };
    };

    return { proposal, apply };
  }
}

import { ProjectSerializer } from "../persistence/ProjectSerializer.js";
import { Revision } from "../persistence/schemas/revision.schema.js";

/**
 * Validador de consistencia criptográfica e integridad de revisiones (Fase 18).
 */
export class RevisionValidator {
  public static validate(revision: Revision): { valid: boolean; error?: string } {
    const computedHash = ProjectSerializer.hashCanonical(revision.project);
    if (computedHash !== revision.projectHash) {
      return {
        valid: false,
        error: `Project hash mismatch: expected '${revision.projectHash}', computed '${computedHash}'`,
      };
    }

    return { valid: true };
  }
}

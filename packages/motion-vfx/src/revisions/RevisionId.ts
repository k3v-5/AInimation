import { ProjectSerializer } from "../persistence/ProjectSerializer.js";

/**
 * Generador determinista de identificadores de revisión criptográficos (Fase 18).
 */
export class RevisionId {
  /**
   * Genera un identificador de revisión determinista y reproducible:
   * hash(projectId + parentRevisionId + canonicalProjectHash + operationHash)
   */
  public static generate(params: {
    projectId: string;
    parentRevisionId: string | null;
    projectHash: string;
    message?: string;
    operationHash?: string;
  }): string {
    const payload = {
      projectId: params.projectId,
      parent: params.parentRevisionId ?? "root",
      projectHash: params.projectHash,
      op: params.operationHash ?? params.message ?? "initial",
    };

    const fullHash = ProjectSerializer.hashCanonical(payload);
    return `rev_${fullHash.slice(0, 16)}`;
  }
}

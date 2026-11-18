import { ProjectEnvelope } from "./ProjectEnvelope.js";
import { ProjectSerializer } from "./ProjectSerializer.js";

export interface ProjectManifestInfo {
  projectId: string;
  revisionId: string;
  schemaVersion: string;
  engineVersion: string;
  contentHash: string;
  manifestHash: string;
  createdAt: string;
  updatedAt: string;
}

/**
 * Generador de manifiesto criptográfico de integridad de proyectos (Fase 18).
 */
export class ProjectManifest {
  /**
   * Genera el manifiesto estructurado a partir de un envelope.
   */
  public static fromEnvelope(envelope: ProjectEnvelope): ProjectManifestInfo {
    const payloadForManifest = {
      projectId: envelope.projectId,
      revisionId: envelope.revisionId,
      schemaVersion: envelope.schemaVersion,
      engineVersion: envelope.engineVersion,
      contentHash: envelope.contentHash,
    };

    const manifestHash = ProjectSerializer.hashProject(payloadForManifest);

    return {
      projectId: envelope.projectId,
      revisionId: envelope.revisionId,
      schemaVersion: envelope.schemaVersion,
      engineVersion: envelope.engineVersion,
      contentHash: envelope.contentHash,
      manifestHash,
      createdAt: envelope.createdAt,
      updatedAt: envelope.updatedAt,
    };
  }
}

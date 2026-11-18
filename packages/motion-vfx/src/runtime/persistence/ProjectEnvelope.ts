import { ProjectEnvelopeSchema } from "../../schemas/runtime.schema.js";
import { ProjectCorruptError, ProjectValidationError } from "../../errors/runtime-errors.js";
import { ProjectMetadata } from "../types.js";
import { ProjectSerializer } from "./ProjectSerializer.js";

export interface MigrationMetadata {
  originalSchemaVersion: string;
  migratedAt: string;
  steps: string[];
}

export interface ProjectEnvelope<T = Record<string, unknown>> {
  schemaVersion: string;
  engineVersion: string;
  projectId: string;
  revisionId: string;
  createdAt: string;
  updatedAt: string;
  contentHash: string;
  project: T;
  metadata: ProjectMetadata;
  migrations?: MigrationMetadata;
}

/**
 * Fábrica y validador de Envelopes versionados de proyecto (Fase 18).
 */
export class ProjectEnvelopeFactory {
  public static readonly CURRENT_SCHEMA_VERSION = "1.8.0";
  public static readonly CURRENT_ENGINE_VERSION = "1.8.0";

  /**
   * Crea un nuevo envelope a partir de un proyecto IR y metadatos.
   */
  public static create<T = Record<string, unknown>>(params: {
    projectId: string;
    revisionId?: string;
    project: T;
    metadata: ProjectMetadata;
    createdAt?: string;
    updatedAt?: string;
    migrations?: MigrationMetadata;
  }): ProjectEnvelope<T> {
    const revisionId = params.revisionId ?? "rev_000001";
    const contentHash = ProjectSerializer.hashProject(params.project);
    const now = new Date().toISOString();

    const envelope: ProjectEnvelope<T> = {
      schemaVersion: this.CURRENT_SCHEMA_VERSION,
      engineVersion: this.CURRENT_ENGINE_VERSION,
      projectId: params.projectId,
      revisionId,
      createdAt: params.createdAt ?? now,
      updatedAt: params.updatedAt ?? now,
      contentHash,
      project: params.project,
      metadata: params.metadata,
      migrations: params.migrations,
    };

    return envelope;
  }

  /**
   * Valida estrictamente un envelope contra su schema y su checksum SHA-256.
   */
  public static validate(rawEnvelope: unknown): ProjectEnvelope {
    const parseResult = ProjectEnvelopeSchema.safeParse(rawEnvelope);
    if (!parseResult.success) {
      throw new ProjectValidationError(
        (rawEnvelope as any)?.projectId ?? "unknown",
        parseResult.error.issues,
        { rawEnvelope }
      );
    }

    const envelope = parseResult.data as unknown as ProjectEnvelope;

    // Validar integridad criptográfica del contentHash
    const expectedHash = ProjectSerializer.hashProject(envelope.project);
    if (envelope.contentHash !== expectedHash) {
      throw new ProjectCorruptError(
        envelope.projectId,
        `Checksum mismatch: contentHash in envelope is '${envelope.contentHash}', but calculated hash of project IR is '${expectedHash}'.`
      );
    }

    return envelope;
  }
}

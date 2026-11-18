import { ProjectEnvelope } from "./persistence/ProjectEnvelope.js";
import { RevisionManager } from "./RevisionManager.js";
import { RuntimeValidator } from "./validation/RuntimeValidator.js";

export type ProjectMutation<T, R> = (draft: T) => Promise<R> | R;

/**
 * Gestor de transacciones atómicas con garantía de Rollback ante errores (Fase 18).
 */
export class ProjectTransaction {
  private revisionManager: RevisionManager;

  constructor(revisionManager: RevisionManager) {
    this.revisionManager = revisionManager;
  }

  /**
   * Ejecuta una mutación sobre una copia aislada del proyecto de forma transaccional.
   */
  public async execute<T = Record<string, unknown>, R = unknown>(params: {
    projectId: string;
    baseRevisionId?: string;
    currentProject: T;
    operation?: string;
    description?: string;
    mutation: ProjectMutation<T, R>;
  }): Promise<{ result: R; envelope: ProjectEnvelope<T> }> {
    // 1. BEGIN: Clon defensivo de la IR para aislar mutaciones
    const draft: T = JSON.parse(JSON.stringify(params.currentProject));

    // 2. Ejecutar mutación sobre el clon
    const result = await params.mutation(draft);

    // 3. Validar integridad del draft mutado antes de persistir
    await RuntimeValidator.validateEnvelope({
      schemaVersion: "1.8.0",
      engineVersion: "1.8.0",
      projectId: params.projectId,
      revisionId: "transient",
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      contentHash: "0".repeat(64), // Temporal para bypass previo
      project: draft,
      metadata: { name: "Transaction Draft" },
    }, { strict: false });

    // 4. COMMIT: Persistir como nueva revisión
    const envelope = await this.revisionManager.createRevision<T>({
      projectId: params.projectId,
      baseRevisionId: params.baseRevisionId,
      nextProject: draft,
      operation: params.operation ?? "transaction",
      description: params.description,
    });

    return { result, envelope };
  }
}

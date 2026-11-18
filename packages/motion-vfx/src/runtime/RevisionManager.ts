import { RevisionConflictError, RevisionNotFoundError } from "../errors/runtime-errors.js";
import { ProjectEnvelope, ProjectEnvelopeFactory } from "./persistence/ProjectEnvelope.js";
import { ProjectRepository } from "./ProjectRepository.js";
import { RevisionInfo } from "./types.js";

/**
 * Gestor inmutable de revisiones con control de concurrencia optimista (Fase 18).
 */
export class RevisionManager {
  private repo: ProjectRepository;

  constructor(repo: ProjectRepository) {
    this.repo = repo;
  }

  /**
   * Crea y persiste una nueva revisión atómica en la cadena histórica.
   */
  public async createRevision<T = Record<string, unknown>>(params: {
    projectId: string;
    baseRevisionId?: string;
    nextProject: T;
    operation?: string;
    description?: string;
  }): Promise<ProjectEnvelope<T>> {
    const currentEnvelope = await this.repo.load(params.projectId);

    // Verificación de Concurrencia Optimista
    if (params.baseRevisionId && currentEnvelope.revisionId !== params.baseRevisionId) {
      throw new RevisionConflictError(
        params.projectId,
        params.baseRevisionId,
        currentEnvelope.revisionId
      );
    }

    // Calcular siguiente ID de revisión secuencial: rev_000001 -> rev_000002
    const nextRevisionId = this.incrementRevisionId(currentEnvelope.revisionId);

    const newEnvelope = ProjectEnvelopeFactory.create({
      projectId: params.projectId,
      revisionId: nextRevisionId,
      project: params.nextProject,
      metadata: {
        ...currentEnvelope.metadata,
        description: params.description ?? currentEnvelope.metadata.description,
      },
      createdAt: currentEnvelope.createdAt,
    });

    (newEnvelope as any).parentRevisionId = currentEnvelope.revisionId;
    (newEnvelope as any).operation = params.operation ?? "mutate";

    await this.repo.save(newEnvelope);
    return newEnvelope;
  }

  /**
   * Obtiene una revisión histórica por su identificador.
   */
  public async getRevision(projectId: string, revisionId: string): Promise<ProjectEnvelope> {
    return this.repo.loadRevision(projectId, revisionId);
  }

  /**
   * Lista todas las revisiones del proyecto.
   */
  public async listRevisions(projectId: string): Promise<RevisionInfo[]> {
    return this.repo.listRevisions(projectId);
  }

  /**
   * Restaura una revisión histórica creando una NUEVA revisión con su contenido (no destructivo).
   */
  public async restoreRevision(projectId: string, targetRevisionId: string, description?: string): Promise<ProjectEnvelope> {
    const targetEnvelope = await this.repo.loadRevision(projectId, targetRevisionId);
    const currentHead = await this.repo.load(projectId);

    const nextRevisionId = this.incrementRevisionId(currentHead.revisionId);

    const restoredEnvelope = ProjectEnvelopeFactory.create({
      projectId,
      revisionId: nextRevisionId,
      project: targetEnvelope.project,
      metadata: {
        ...currentHead.metadata,
        description: description ?? `Restored from revision ${targetRevisionId}`,
      },
      createdAt: currentHead.createdAt,
    });

    (restoredEnvelope as any).parentRevisionId = currentHead.revisionId;
    (restoredEnvelope as any).operation = `restore:${targetRevisionId}`;

    await this.repo.save(restoredEnvelope);
    return restoredEnvelope;
  }

  private incrementRevisionId(currentRevId: string): string {
    const match = currentRevId.match(/^rev_(\d+)$/);
    if (!match) {
      return `rev_${Date.now()}`;
    }
    const nextNum = parseInt(match[1], 10) + 1;
    return `rev_${String(nextNum).padStart(6, "0")}`;
  }
}

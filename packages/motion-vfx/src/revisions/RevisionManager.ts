import { RevisionConflictError, RevisionNotFoundError } from "../persistence/errors/persistence-errors.js";
import { ProjectSerializer } from "../persistence/ProjectSerializer.js";
import { ProjectStore } from "../persistence/ProjectStore.js";
import { Revision, RevisionAuthor, RevisionChange, RevisionSummary } from "../persistence/schemas/revision.schema.js";
import { RevisionDiff, RevisionDiffResult } from "./RevisionDiff.js";
import { RevisionGraph } from "./RevisionGraph.js";
import { RevisionId } from "./RevisionId.js";
import { MergeResult, RevisionMerge } from "./RevisionMerge.js";
import { RevisionPatch } from "./RevisionPatch.js";
import { RevisionValidator } from "./RevisionValidator.js";

/**
 * Gestor integral de control de versiones, ramificación, merge y reversión (Fase 18).
 */
export class RevisionManager {
  private store: ProjectStore;

  constructor(store: ProjectStore) {
    this.store = store;
  }

  /**
   * Crea una nueva revisión inmutable en el historial del proyecto.
   */
  public async createRevision(params: {
    projectId: string;
    parentRevisionId: string | null;
    project: Record<string, unknown>;
    author: RevisionAuthor;
    message: string;
    changes?: RevisionChange[];
  }): Promise<Revision> {
    const exists = await this.store.exists(params.projectId);
    let projectFile: any;
    if (exists) {
      projectFile = await this.store.get(params.projectId);
    }

    // Si tiene parent, verificar existencia y calcular diff si no fue provisto
    let calculatedChanges = params.changes;
    if (params.parentRevisionId !== null && exists) {
      const parentRev = await this.store.getRevision(params.projectId, params.parentRevisionId);
      if (!calculatedChanges) {
        const diffRes = RevisionDiff.diff(parentRev.project, params.project);
        calculatedChanges = diffRes.changes;
      }
    } else {
      calculatedChanges = calculatedChanges ?? [];
    }

    const projectHash = ProjectSerializer.hashCanonical(params.project);
    const revisionId = RevisionId.generate({
      projectId: params.projectId,
      parentRevisionId: params.parentRevisionId,
      projectHash,
      message: params.message,
    });

    const revision: Revision = {
      revisionId,
      projectId: params.projectId,
      parentRevisionId: params.parentRevisionId,
      createdBy: params.author,
      message: params.message,
      changes: calculatedChanges,
      projectHash,
      schemaVersion: "1.8.0",
      project: JSON.parse(ProjectSerializer.canonicalize(params.project)),
      createdAt: new Date().toISOString(),
    };

    RevisionValidator.validate(revision);

    if (exists) {
      await this.store.saveRevision(params.projectId, revision);

      // Actualizar HEAD del proyecto si deriva del head actual
      projectFile.headRevisionId = revision.revisionId;
      projectFile.project = revision.project;
      projectFile.contentHash = projectHash;
      projectFile.updatedAt = revision.createdAt;
      await this.store.update(projectFile);
    }

    return revision;
  }

  /**
   * Obtiene una revisión por su ID.
   */
  public async getRevision(projectId: string, revisionId: string): Promise<Revision> {
    return this.store.getRevision(projectId, revisionId);
  }

  /**
   * Lista el resumen de todas las revisiones.
   */
  public async listRevisions(projectId: string): Promise<RevisionSummary[]> {
    return this.store.listRevisions(projectId);
  }

  /**
   * Construye el grafo DAG completo de revisiones del proyecto.
   */
  public async getRevisionGraph(projectId: string): Promise<RevisionGraph> {
    const summaries = await this.store.listRevisions(projectId);
    const fullRevisions = await Promise.all(
      summaries.map((s) => this.store.getRevision(projectId, s.revisionId))
    );
    return new RevisionGraph(fullRevisions);
  }

  /**
   * Compara dos revisiones y devuelve el diff semántico estructurado.
   */
  public async diffRevisions(projectId: string, fromRevId: string, toRevId: string): Promise<RevisionDiffResult> {
    const fromRev = await this.store.getRevision(projectId, fromRevId);
    const toRev = await this.store.getRevision(projectId, toRevId);
    return RevisionDiff.diff(fromRev, toRev);
  }

  /**
   * Restaura una revisión previa creando una NUEVA revisión HEAD con su contenido (no destructivo).
   */
  public async restoreRevision(params: {
    projectId: string;
    targetRevisionId: string;
    author: RevisionAuthor;
    message?: string;
  }): Promise<Revision> {
    const targetRev = await this.store.getRevision(params.projectId, params.targetRevisionId);
    const projectFile = await this.store.get(params.projectId);

    return this.createRevision({
      projectId: params.projectId,
      parentRevisionId: projectFile.headRevisionId,
      project: targetRev.project,
      author: params.author,
      message: params.message ?? `Restored from revision ${params.targetRevisionId}`,
    });
  }

  /**
   * Deshace una revisión aplicando un parche inverso y creando una nueva revisión.
   */
  public async undoRevision(params: {
    projectId: string;
    targetRevisionId: string;
    author: RevisionAuthor;
    message?: string;
  }): Promise<Revision> {
    const targetRev = await this.store.getRevision(params.projectId, params.targetRevisionId);
    const projectFile = await this.store.get(params.projectId);

    const reversedProject = RevisionPatch.reversePatch(projectFile.project, targetRev.changes);

    return this.createRevision({
      projectId: params.projectId,
      parentRevisionId: projectFile.headRevisionId,
      project: reversedProject,
      author: params.author,
      message: params.message ?? `Undo revision ${params.targetRevisionId}`,
    });
  }

  /**
   * Fusiona dos ramas concurrentes no conflictivas mediante un merge 3-way.
   */
  public async mergeBranches(params: {
    projectId: string;
    baseRevisionId: string;
    leftRevisionId: string;
    rightRevisionId: string;
    author: RevisionAuthor;
    message?: string;
  }): Promise<{ revision?: Revision; mergeResult: MergeResult }> {
    const baseRev = await this.store.getRevision(params.projectId, params.baseRevisionId);
    const leftRev = await this.store.getRevision(params.projectId, params.leftRevisionId);
    const rightRev = await this.store.getRevision(params.projectId, params.rightRevisionId);

    const mergeResult = RevisionMerge.merge(baseRev.project, leftRev.project, rightRev.project);

    if (!mergeResult.merged || !mergeResult.result) {
      return { mergeResult };
    }

    const revision = await this.createRevision({
      projectId: params.projectId,
      parentRevisionId: params.leftRevisionId,
      project: mergeResult.result,
      author: params.author,
      message: params.message ?? `Merged branches ${params.leftRevisionId} and ${params.rightRevisionId}`,
    });

    return { revision, mergeResult };
  }
}

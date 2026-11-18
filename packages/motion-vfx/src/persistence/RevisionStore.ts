import { ProjectStore } from "./ProjectStore.js";
import { Revision, RevisionSummary } from "./schemas/revision.schema.js";

/**
 * Repositorio especializado para el acceso y listado de revisiones (Fase 18).
 */
export class RevisionStore {
  private store: ProjectStore;

  constructor(store: ProjectStore) {
    this.store = store;
  }

  public async saveRevision(projectId: string, revision: Revision): Promise<void> {
    await this.store.saveRevision(projectId, revision);
  }

  public async getRevision(projectId: string, revisionId: string): Promise<Revision> {
    return this.store.getRevision(projectId, revisionId);
  }

  public async listRevisions(projectId: string): Promise<RevisionSummary[]> {
    return this.store.listRevisions(projectId);
  }
}

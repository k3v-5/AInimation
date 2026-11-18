import { ProjectMigration } from "../persistence/ProjectMigration.js";
import { ProjectSerializer } from "../persistence/ProjectSerializer.js";
import { ProjectStore } from "../persistence/ProjectStore.js";
import { ProjectFile, ProjectMetadata, ProjectSummary } from "../persistence/schemas/project.schema.js";
import { Revision, RevisionAuthor } from "../persistence/schemas/revision.schema.js";
import { RevisionId } from "../revisions/RevisionId.js";
import { RevisionManager } from "../revisions/RevisionManager.js";
import { ProjectSnapshot } from "./ProjectSnapshot.js";

/**
 * Fachada de servicios de alto nivel para gestión de proyectos, snapshots y revisiones (Fase 18).
 */
export class ProjectService {
  private store: ProjectStore;
  private revisionManager: RevisionManager;

  constructor(store: ProjectStore, revisionManager: RevisionManager) {
    this.store = store;
    this.revisionManager = revisionManager;
  }

  public async createProject(params: {
    projectId: string;
    project: Record<string, unknown>;
    metadata: ProjectMetadata;
    author: RevisionAuthor;
    message?: string;
  }): Promise<{ projectFile: ProjectFile; snapshot: ProjectSnapshot }> {
    const migrated = ProjectMigration.migrate(params.project);
    const contentHash = ProjectSerializer.hashCanonical(migrated.project);

    const initialRevisionId = RevisionId.generate({
      projectId: params.projectId,
      parentRevisionId: null,
      projectHash: contentHash,
      message: params.message ?? "Initial project creation",
    });

    const projectFile: ProjectFile = {
      schemaVersion: "1.8.0",
      engineVersion: "1.8.0",
      projectId: params.projectId,
      headRevisionId: initialRevisionId,
      metadata: params.metadata,
      project: migrated.project,
      contentHash,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    await this.store.create(projectFile);

    const initialRevision: Revision = {
      revisionId: initialRevisionId,
      projectId: params.projectId,
      parentRevisionId: null,
      createdBy: params.author,
      message: params.message ?? "Initial project creation",
      changes: [],
      projectHash: contentHash,
      schemaVersion: "1.8.0",
      project: migrated.project,
      createdAt: projectFile.createdAt,
    };

    await this.store.saveRevision(params.projectId, initialRevision);

    const snapshot = new ProjectSnapshot(
      projectFile.projectId,
      projectFile.headRevisionId,
      projectFile.contentHash,
      projectFile.project
    );

    return { projectFile, snapshot };
  }

  public async getSnapshot(projectId: string, revisionId?: string): Promise<ProjectSnapshot> {
    if (revisionId) {
      const rev = await this.revisionManager.getRevision(projectId, revisionId);
      return new ProjectSnapshot(projectId, rev.revisionId, rev.projectHash, rev.project);
    }

    const projectFile = await this.store.get(projectId);
    return new ProjectSnapshot(projectId, projectFile.headRevisionId, projectFile.contentHash, projectFile.project);
  }

  public async listProjects(): Promise<ProjectSummary[]> {
    return this.store.listProjects();
  }
}

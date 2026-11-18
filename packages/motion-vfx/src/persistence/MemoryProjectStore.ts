import { ProjectAlreadyExistsError, ProjectNotFoundError, RevisionNotFoundError } from "./errors/persistence-errors.js";
import { ProjectSerializer } from "./ProjectSerializer.js";
import { ProjectStore } from "./ProjectStore.js";
import { ProjectFile, ProjectSummary } from "./schemas/project.schema.js";
import { Revision, RevisionSummary } from "./schemas/revision.schema.js";

/**
 * Almacén en memoria de proyectos y revisiones de alta velocidad (Fase 18).
 */
export class MemoryProjectStore implements ProjectStore {
  private projects = new Map<string, string>(); // projectId -> canonical JSON string
  private revisions = new Map<string, Map<string, string>>(); // projectId -> (revisionId -> canonical JSON string)

  public async create(project: ProjectFile): Promise<void> {
    if (this.projects.has(project.projectId)) {
      throw new ProjectAlreadyExistsError(project.projectId);
    }
    const canonical = ProjectSerializer.canonicalize(project);
    this.projects.set(project.projectId, canonical);
    if (!this.revisions.has(project.projectId)) {
      this.revisions.set(project.projectId, new Map());
    }
  }

  public async get(projectId: string): Promise<ProjectFile> {
    const raw = this.projects.get(projectId);
    if (!raw) {
      throw new ProjectNotFoundError(projectId);
    }
    return JSON.parse(raw) as ProjectFile;
  }

  public async update(project: ProjectFile): Promise<void> {
    if (!this.projects.has(project.projectId)) {
      throw new ProjectNotFoundError(project.projectId);
    }
    const canonical = ProjectSerializer.canonicalize(project);
    this.projects.set(project.projectId, canonical);
  }

  public async exists(projectId: string): Promise<boolean> {
    return this.projects.has(projectId);
  }

  public async delete(projectId: string): Promise<void> {
    this.projects.delete(projectId);
    this.revisions.delete(projectId);
  }

  public async saveRevision(projectId: string, revision: Revision): Promise<void> {
    if (!this.projects.has(projectId)) {
      throw new ProjectNotFoundError(projectId);
    }
    let revMap = this.revisions.get(projectId);
    if (!revMap) {
      revMap = new Map();
      this.revisions.set(projectId, revMap);
    }
    const canonical = ProjectSerializer.canonicalize(revision);
    revMap.set(revision.revisionId, canonical);
  }

  public async getRevision(projectId: string, revisionId: string): Promise<Revision> {
    const revMap = this.revisions.get(projectId);
    if (!revMap) {
      throw new RevisionNotFoundError(projectId, revisionId);
    }
    const raw = revMap.get(revisionId);
    if (!raw) {
      throw new RevisionNotFoundError(projectId, revisionId);
    }
    return JSON.parse(raw) as Revision;
  }

  public async listRevisions(projectId: string): Promise<RevisionSummary[]> {
    if (!this.projects.has(projectId)) {
      throw new ProjectNotFoundError(projectId);
    }
    const revMap = this.revisions.get(projectId);
    if (!revMap) return [];

    const summaries: RevisionSummary[] = [];
    for (const [_, raw] of revMap.entries()) {
      const rev = JSON.parse(raw) as Revision;
      summaries.push({
        revisionId: rev.revisionId,
        projectId: rev.projectId,
        parentRevisionId: rev.parentRevisionId,
        createdBy: rev.createdBy,
        message: rev.message,
        projectHash: rev.projectHash,
        changeCount: rev.changes.length,
        createdAt: rev.createdAt,
      });
    }

    return summaries.sort((a, b) => a.revisionId.localeCompare(b.revisionId));
  }

  public async listProjects(): Promise<ProjectSummary[]> {
    const list: ProjectSummary[] = [];
    for (const [id, raw] of this.projects.entries()) {
      const proj = JSON.parse(raw) as ProjectFile;
      const revMap = this.revisions.get(id);
      const rawComp = (proj.project as any)?.composition ?? proj.project;

      list.push({
        projectId: proj.projectId,
        name: proj.metadata.name,
        headRevisionId: proj.headRevisionId,
        revisionCount: revMap ? revMap.size : 1,
        duration: rawComp?.duration ?? 0,
        width: rawComp?.width ?? 1920,
        height: rawComp?.height ?? 1080,
        fps: rawComp?.fps ?? 30,
        updatedAt: proj.updatedAt,
      });
    }

    return list.sort((a, b) => a.projectId.localeCompare(b.projectId));
  }

  public clear(): void {
    this.projects.clear();
    this.revisions.clear();
  }
}

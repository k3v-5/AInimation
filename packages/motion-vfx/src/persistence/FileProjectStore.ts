import * as fs from "node:fs/promises";
import * as path from "node:path";
import { PathSanitizer } from "../exporters/common/PathSanitizer.js";
import {
  AtomicWriteError,
  CorruptedProjectError,
  PersistenceError,
  ProjectAlreadyExistsError,
  ProjectNotFoundError,
  RevisionNotFoundError,
} from "./errors/persistence-errors.js";
import { ProjectSerializer } from "./ProjectSerializer.js";
import { ProjectStore } from "./ProjectStore.js";
import { ProjectFile, ProjectFileSchema, ProjectSummary } from "./schemas/project.schema.js";
import { Revision, RevisionSchema, RevisionSummary } from "./schemas/revision.schema.js";

/**
 * Almacén en sistema de archivos local con escrituras atómicas y sandboxing (Fase 18).
 */
export class FileProjectStore implements ProjectStore {
  private readonly storageRoot: string;

  constructor(storageRoot: string) {
    this.storageRoot = path.resolve(storageRoot);
  }

  public getStorageRoot(): string {
    return this.storageRoot;
  }

  public async create(project: ProjectFile): Promise<void> {
    const projectDir = this.getProjectDir(project.projectId);
    const headFile = path.join(projectDir, "project.json");

    if (await this.pathExists(headFile)) {
      throw new ProjectAlreadyExistsError(project.projectId);
    }

    await fs.mkdir(path.join(projectDir, "revisions"), { recursive: true });
    await this.writeAtomicJson(headFile, project);
  }

  public async get(projectId: string): Promise<ProjectFile> {
    const headFile = path.join(this.getProjectDir(projectId), "project.json");
    if (!(await this.pathExists(headFile))) {
      throw new ProjectNotFoundError(projectId);
    }

    const content = await fs.readFile(headFile, "utf-8");
    try {
      const raw = JSON.parse(content);
      return ProjectFileSchema.parse(raw);
    } catch (err: any) {
      throw new CorruptedProjectError(projectId, `Failed to parse project.json: ${err.message}`);
    }
  }

  public async update(project: ProjectFile): Promise<void> {
    const headFile = path.join(this.getProjectDir(project.projectId), "project.json");
    if (!(await this.pathExists(headFile))) {
      throw new ProjectNotFoundError(project.projectId);
    }

    await this.writeAtomicJson(headFile, project);
  }

  public async exists(projectId: string): Promise<boolean> {
    const headFile = path.join(this.getProjectDir(projectId), "project.json");
    return this.pathExists(headFile);
  }

  public async delete(projectId: string): Promise<void> {
    const projectDir = this.getProjectDir(projectId);
    try {
      await fs.rm(projectDir, { recursive: true, force: true });
    } catch {}
  }

  public async saveRevision(projectId: string, revision: Revision): Promise<void> {
    if (!(await this.exists(projectId))) {
      throw new ProjectNotFoundError(projectId);
    }

    const revDir = path.join(this.getProjectDir(projectId), "revisions");
    await fs.mkdir(revDir, { recursive: true });
    const revFile = path.join(revDir, `${revision.revisionId}.json`);

    await this.writeAtomicJson(revFile, revision);
  }

  public async getRevision(projectId: string, revisionId: string): Promise<Revision> {
    const revFile = path.join(this.getProjectDir(projectId), "revisions", `${revisionId}.json`);
    if (!(await this.pathExists(revFile))) {
      throw new RevisionNotFoundError(projectId, revisionId);
    }

    const content = await fs.readFile(revFile, "utf-8");
    try {
      const raw = JSON.parse(content);
      return RevisionSchema.parse(raw);
    } catch (err: any) {
      throw new PersistenceError(`Failed to parse revision '${revisionId}': ${err.message}`);
    }
  }

  public async listRevisions(projectId: string): Promise<RevisionSummary[]> {
    if (!(await this.exists(projectId))) {
      throw new ProjectNotFoundError(projectId);
    }

    const revDir = path.join(this.getProjectDir(projectId), "revisions");
    if (!(await this.pathExists(revDir))) {
      return [];
    }

    const files = await fs.readdir(revDir);
    const summaries: RevisionSummary[] = [];

    for (const f of files) {
      if (f.endsWith(".json")) {
        try {
          const content = await fs.readFile(path.join(revDir, f), "utf-8");
          const rev = JSON.parse(content) as Revision;
          summaries.push({
            revisionId: rev.revisionId,
            projectId: rev.projectId,
            parentRevisionId: rev.parentRevisionId,
            createdBy: rev.createdBy,
            message: rev.message,
            projectHash: rev.projectHash,
            changeCount: Array.isArray(rev.changes) ? rev.changes.length : 0,
            createdAt: rev.createdAt,
          });
        } catch {}
      }
    }

    return summaries.sort((a, b) => a.revisionId.localeCompare(b.revisionId));
  }

  public async listProjects(): Promise<ProjectSummary[]> {
    const projectsRoot = path.join(this.storageRoot, "projects");
    if (!(await this.pathExists(projectsRoot))) {
      return [];
    }

    const entries = await fs.readdir(projectsRoot);
    const summaries: ProjectSummary[] = [];

    for (const entry of entries) {
      const headFile = path.join(projectsRoot, entry, "project.json");
      if (await this.pathExists(headFile)) {
        try {
          const content = await fs.readFile(headFile, "utf-8");
          const proj = JSON.parse(content) as ProjectFile;
          const revDir = path.join(projectsRoot, entry, "revisions");
          let revCount = 1;
          if (await this.pathExists(revDir)) {
            const revFiles = await fs.readdir(revDir);
            revCount = revFiles.filter((f) => f.endsWith(".json")).length;
          }

          const rawComp = (proj.project as any)?.composition ?? proj.project;
          summaries.push({
            projectId: proj.projectId,
            name: proj.metadata.name,
            headRevisionId: proj.headRevisionId,
            revisionCount: revCount,
            duration: rawComp?.duration ?? 0,
            width: rawComp?.width ?? 1920,
            height: rawComp?.height ?? 1080,
            fps: rawComp?.fps ?? 30,
            updatedAt: proj.updatedAt,
          });
        } catch {}
      }
    }

    return summaries.sort((a, b) => a.projectId.localeCompare(b.projectId));
  }

  private async writeAtomicJson(targetPath: string, data: unknown): Promise<void> {
    const canonical = ProjectSerializer.canonicalize(data);
    const parentDir = path.dirname(targetPath);
    await fs.mkdir(parentDir, { recursive: true });

    const tmpPath = `${targetPath}.tmp.${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;

    try {
      const handle = await fs.open(tmpPath, "w");
      await handle.writeFile(canonical, "utf-8");
      await handle.sync();
      await handle.close();

      await fs.rename(tmpPath, targetPath);
    } catch (err: any) {
      try {
        await fs.unlink(tmpPath);
      } catch {}
      throw new AtomicWriteError(targetPath, err.message);
    }
  }

  private getProjectDir(projectId: string): string {
    const safeId = projectId.replace(/[^a-zA-Z0-9_-]/g, "_");
    const sanitized = PathSanitizer.sanitizeFileName(safeId);
    return path.join(this.storageRoot, "projects", sanitized);
  }

  private async pathExists(p: string): Promise<boolean> {
    try {
      await fs.access(p);
      return true;
    } catch {
      return false;
    }
  }
}

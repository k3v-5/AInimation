import { ProjectAlreadyExistsError, ProjectNotFoundError, RevisionNotFoundError } from "../errors/runtime-errors.js";
import { ProjectEnvelope, ProjectEnvelopeFactory } from "./persistence/ProjectEnvelope.js";
import { ProjectSerializer } from "./persistence/ProjectSerializer.js";
import { StorageAdapter } from "./persistence/StorageAdapter.js";
import { ProjectMetadata, RevisionInfo } from "./types.js";

/**
 * Repositorio desacoplado para la gestión de proyectos, envelopes y revisiones (Fase 18).
 */
export class ProjectRepository {
  private storage: StorageAdapter;

  constructor(storage: StorageAdapter) {
    this.storage = storage;
  }

  public getStorage(): StorageAdapter {
    return this.storage;
  }

  /**
   * Crea y persiste un nuevo proyecto con su primera revisión.
   */
  public async create<T = Record<string, unknown>>(params: {
    projectId: string;
    project: T;
    metadata: ProjectMetadata;
  }): Promise<ProjectEnvelope<T>> {
    const headPath = this.getHeadKey(params.projectId);
    if (await this.storage.exists(headPath)) {
      throw new ProjectAlreadyExistsError(params.projectId);
    }

    const envelope = ProjectEnvelopeFactory.create({
      projectId: params.projectId,
      revisionId: "rev_000001",
      project: params.project,
      metadata: params.metadata,
    });

    await this.persistEnvelope(envelope as unknown as ProjectEnvelope);
    return envelope;
  }

  /**
   * Guarda una nueva revisión y actualiza el puntero HEAD del proyecto.
   */
  public async save<T = Record<string, unknown>>(envelope: ProjectEnvelope<T>): Promise<ProjectEnvelope<T>> {
    // Validar envelope antes de persistir
    ProjectEnvelopeFactory.validate(envelope);

    await this.persistEnvelope(envelope as unknown as ProjectEnvelope);
    return envelope;
  }

  /**
   * Carga el estado HEAD actual de un proyecto.
   */
  public async load(projectId: string): Promise<ProjectEnvelope> {
    const headKey = this.getHeadKey(projectId);
    const data = await this.storage.read(headKey);
    if (!data) {
      throw new ProjectNotFoundError(projectId);
    }

    const rawStr = new TextDecoder("utf-8").decode(data);
    const rawJson = JSON.parse(rawStr);
    return ProjectEnvelopeFactory.validate(rawJson);
  }

  /**
   * Comprueba si un proyecto existe en el repositorio.
   */
  public async exists(projectId: string): Promise<boolean> {
    const headKey = this.getHeadKey(projectId);
    return this.storage.exists(headKey);
  }

  /**
   * Carga una revisión histórica específica.
   */
  public async loadRevision(projectId: string, revisionId: string): Promise<ProjectEnvelope> {
    const revKey = this.getRevisionKey(projectId, revisionId);
    const data = await this.storage.read(revKey);
    if (!data) {
      throw new RevisionNotFoundError(projectId, revisionId);
    }

    const rawStr = new TextDecoder("utf-8").decode(data);
    const rawJson = JSON.parse(rawStr);
    return ProjectEnvelopeFactory.validate(rawJson);
  }

  /**
   * Lista todas las revisiones persistidas de un proyecto.
   */
  public async listRevisions(projectId: string): Promise<RevisionInfo[]> {
    if (!(await this.exists(projectId))) {
      throw new ProjectNotFoundError(projectId);
    }

    const prefix = `projects/${projectId}/revisions/`;
    const files = await this.storage.list(prefix);
    const revisions: RevisionInfo[] = [];

    for (const file of files) {
      if (file.endsWith(".json")) {
        const data = await this.storage.read(file);
        if (data) {
          try {
            const rawStr = new TextDecoder("utf-8").decode(data);
            const env = JSON.parse(rawStr) as ProjectEnvelope;
            revisions.push({
              revisionId: env.revisionId,
              operation: (env as any).operation ?? "save",
              createdAt: env.createdAt,
              contentHash: env.contentHash,
              summary: {
                layerCount: (env.project as any)?.layers?.length ?? (env.project as any)?.composition?.layers?.length ?? 0,
                elementCount: (env.project as any)?.elements?.length ?? (env.project as any)?.composition?.elements?.length ?? 0,
                duration: (env.project as any)?.duration ?? (env.project as any)?.composition?.duration ?? 0,
                fps: (env.project as any)?.fps ?? (env.project as any)?.composition?.fps ?? 30,
                width: (env.project as any)?.width ?? (env.project as any)?.composition?.width ?? 1920,
                height: (env.project as any)?.height ?? (env.project as any)?.composition?.height ?? 1080,
              },
            });
          } catch {
            // Ignorar archivos corruptos individuales al listar
          }
        }
      }
    }

    return revisions.sort((a, b) => a.revisionId.localeCompare(b.revisionId));
  }

  /**
   * Elimina un proyecto y todo su historial de revisiones.
   */
  public async delete(projectId: string): Promise<void> {
    const prefix = `projects/${projectId}/`;
    const files = await this.storage.list(prefix);
    for (const file of files) {
      await this.storage.delete(file);
    }
  }

  /**
   * Lista todos los projectIds disponibles en el repositorio.
   */
  public async listProjects(): Promise<string[]> {
    const files = await this.storage.list("projects/");
    const projectIds = new Set<string>();

    for (const file of files) {
      const match = file.match(/^projects\/([^/]+)\/project\.json$/);
      if (match) {
        projectIds.add(match[1]);
      }
    }

    return Array.from(projectIds).sort();
  }

  private async persistEnvelope(envelope: ProjectEnvelope): Promise<void> {
    const canonicalJson = ProjectSerializer.canonicalize(envelope);
    const bytes = new TextEncoder().encode(canonicalJson);

    // 1. Guardar en historial de revisiones: projects/{projectId}/revisions/{revisionId}.json
    const revKey = this.getRevisionKey(envelope.projectId, envelope.revisionId);
    await this.storage.write(revKey, bytes);

    // 2. Actualizar puntero HEAD: projects/{projectId}/project.json
    const headKey = this.getHeadKey(envelope.projectId);
    await this.storage.write(headKey, bytes);
  }

  private getHeadKey(projectId: string): string {
    return `projects/${projectId}/project.json`;
  }

  private getRevisionKey(projectId: string, revisionId: string): string {
    return `projects/${projectId}/revisions/${revisionId}.json`;
  }
}

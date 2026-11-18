import { ProjectNotFoundError } from "../errors/runtime-errors.js";
import { RuntimeConfig, RuntimeConfigSchema } from "../schemas/runtime.schema.js";
import { DiagnosticCollector } from "./diagnostics/DiagnosticCollector.js";
import { RuntimeMetrics } from "./diagnostics/RuntimeMetrics.js";
import { LockManager } from "./locking/LockManager.js";
import { MigrationRegistry } from "./migration/MigrationRegistry.js";
import { OperationManager } from "./OperationManager.js";
import { FileSystemStorageAdapter } from "./persistence/FileSystemStorageAdapter.js";
import { MemoryStorageAdapter } from "./persistence/MemoryStorageAdapter.js";
import { ProjectEnvelopeFactory } from "./persistence/ProjectEnvelope.js";
import { StorageAdapter } from "./persistence/StorageAdapter.js";
import { ProjectDiffEngine } from "./ProjectDiff.js";
import { ProjectLock } from "./ProjectLock.js";
import { ProjectRecovery } from "./ProjectRecovery.js";
import { ProjectRepository } from "./ProjectRepository.js";
import { ProjectSession } from "./ProjectSession.js";
import { ProjectTransaction } from "./ProjectTransaction.js";
import { RevisionManager } from "./RevisionManager.js";
import { RuntimeStateMachine } from "./RuntimeState.js";
import { HealthReport, ProjectMetadata, RevisionInfo } from "./types.js";
import { RuntimeValidator } from "./validation/RuntimeValidator.js";

/**
 * Fachada principal del Runtime de Producción del Motion Engine (Fase 18).
 */
export class ProjectRuntime {
  private config: RuntimeConfig;
  private storage: StorageAdapter;
  private repo: ProjectRepository;
  private revisionManager: RevisionManager;
  private recovery: ProjectRecovery;
  private lockManager: LockManager;
  private operationManager = new OperationManager();
  private stateMachine = new RuntimeStateMachine();
  private activeSessions = new Map<string, ProjectSession>();

  constructor(configInput?: Partial<RuntimeConfig>, customStorage?: StorageAdapter) {
    const parsedConfig = RuntimeConfigSchema.parse({
      storageRoot: configInput?.storageRoot ?? "storage/projects",
      ...configInput,
    });

    this.config = parsedConfig;
    this.storage = customStorage ?? (parsedConfig.storageRoot === ":memory:"
      ? new MemoryStorageAdapter()
      : new FileSystemStorageAdapter(parsedConfig.storageRoot));

    this.repo = new ProjectRepository(this.storage);
    this.revisionManager = new RevisionManager(this.repo);
    this.recovery = new ProjectRecovery(this.storage);
    this.lockManager = new LockManager(this.storage);
    this.stateMachine.transitionTo("READY");
  }

  public getRepository(): ProjectRepository {
    return this.repo;
  }

  public getRevisionManager(): RevisionManager {
    return this.revisionManager;
  }

  public getOperationManager(): OperationManager {
    return this.operationManager;
  }

  public getStorage(): StorageAdapter {
    return this.storage;
  }

  /**
   * Crea un nuevo proyecto y abre su sesión de edición.
   */
  public async createProject<T = Record<string, unknown>>(params: {
    projectId: string;
    project: T;
    metadata: ProjectMetadata;
  }): Promise<ProjectSession> {
    return RuntimeMetrics.time("project.create.duration", async () => {
      this.stateMachine.assertReadyOrBusy();

      // Ejecutar migraciones si es necesario
      const migrationResult = MigrationRegistry.migrate(params.project);
      const envelope = await this.repo.create({
        projectId: params.projectId,
        project: migrationResult.project,
        metadata: params.metadata,
      });

      const lock = new ProjectLock(this.storage);
      await lock.acquire(params.projectId);

      const session = new ProjectSession({
        envelope,
        repo: this.repo,
        revisionManager: this.revisionManager,
        transaction: new ProjectTransaction(this.revisionManager),
        lock,
      });

      this.activeSessions.set(params.projectId, session);
      return session;
    });
  }

  /**
   * Abre un proyecto existente, aplicando recuperación si hubo interrupciones y adquiriendo lock.
   */
  public async openProject(projectId: string, options: { readOnly?: boolean } = {}): Promise<ProjectSession> {
    return RuntimeMetrics.time("project.load.duration", async () => {
      this.stateMachine.assertReadyOrBusy();

      // Si ya existe una sesión abierta activa, reutilizarla
      if (this.activeSessions.has(projectId)) {
        return this.activeSessions.get(projectId)!;
      }

      // 1. Ejecutar recovery si está habilitado
      if (this.config.enableRecovery) {
        await this.recovery.recoverProject(projectId);
      }

      if (!(await this.repo.exists(projectId))) {
        throw new ProjectNotFoundError(projectId);
      }

      const envelope = await this.repo.load(projectId);

      // 2. Validar integridad multi-capa
      if (this.config.strictValidation) {
        await RuntimeValidator.validateEnvelope(envelope, { strict: true, storage: this.storage });
      }

      const lock = new ProjectLock(this.storage);
      if (!options.readOnly) {
        await lock.acquire(projectId);
      }

      const session = new ProjectSession({
        envelope,
        repo: this.repo,
        revisionManager: this.revisionManager,
        transaction: new ProjectTransaction(this.revisionManager),
        lock,
      });

      this.activeSessions.set(projectId, session);
      return session;
    });
  }

  /**
   * Cierra una sesión activa de proyecto liberando bloqueos.
   */
  public async closeProject(projectId: string): Promise<void> {
    const session = this.activeSessions.get(projectId);
    if (session) {
      await session.close();
      this.activeSessions.delete(projectId);
    }
  }

  /**
   * Valida un proyecto produciendo su reporte de salud.
   */
  public async validateProject(projectId: string, strict = true): Promise<HealthReport> {
    return RuntimeMetrics.time("project.validation.duration", async () => {
      const envelope = await this.repo.load(projectId);
      const { health } = await RuntimeValidator.validateEnvelope(envelope, { strict, storage: this.storage });
      return health;
    });
  }

  /**
   * Compara dos revisiones de un proyecto.
   */
  public async diffRevisions(projectId: string, fromRevId: string, toRevId: string) {
    return RuntimeMetrics.time("project.diff.duration", async () => {
      const fromEnv = await this.repo.loadRevision(projectId, fromRevId);
      const toEnv = await this.repo.loadRevision(projectId, toRevId);
      return ProjectDiffEngine.diff(fromEnv, toEnv);
    });
  }

  /**
   * Restaura una revisión histórica.
   */
  public async restoreRevision(projectId: string, targetRevisionId: string, description?: string) {
    return RuntimeMetrics.time("project.restore.duration", async () => {
      return this.revisionManager.restoreRevision(projectId, targetRevisionId, description);
    });
  }

  /**
   * Consulta el estado y health de un proyecto.
   */
  public async getStatus(projectId: string): Promise<{
    projectId: string;
    revisionId: string;
    contentHash: string;
    activeOperations: number;
    isLocked: boolean;
  }> {
    const envelope = await this.repo.load(projectId);
    const activeOps = this.operationManager.listActiveOperations(projectId).length;
    const isLocked = await this.lockManager.isLocked(projectId);

    return {
      projectId,
      revisionId: envelope.revisionId,
      contentHash: envelope.contentHash,
      activeOperations: activeOps,
      isLocked,
    };
  }

  /**
   * Lista todos los proyectos disponibles.
   */
  public async listProjects(): Promise<string[]> {
    return this.repo.listProjects();
  }

  /**
   * Lista todas las revisiones de un proyecto.
   */
  public async listRevisions(projectId: string): Promise<RevisionInfo[]> {
    return this.repo.listRevisions(projectId);
  }

  /**
   * Cierra ordenadamente el Runtime liberando todas las sesiones.
   */
  public async shutdown(): Promise<void> {
    this.stateMachine.transitionTo("SHUTTING_DOWN");
    for (const session of this.activeSessions.values()) {
      try {
        await session.close();
      } catch {
        // Silenciar errores durante shutdown
      }
    }
    this.activeSessions.clear();
    this.stateMachine.transitionTo("CLOSED");
  }
}

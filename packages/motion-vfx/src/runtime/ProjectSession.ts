import { Composition } from "../core/composition.js";
import { Time } from "../core/types.js";
import { ProjectDeserializer } from "./persistence/ProjectDeserializer.js";
import { ProjectEnvelope } from "./persistence/ProjectEnvelope.js";
import { ProjectLock } from "./ProjectLock.js";
import { ProjectRepository } from "./ProjectRepository.js";
import { ProjectMutation, ProjectTransaction } from "./ProjectTransaction.js";
import { RevisionManager } from "./RevisionManager.js";
import { RevisionInfo } from "./types.js";

/**
 * Sesión activa de edición y consulta de un proyecto en el Runtime (Fase 18).
 */
export class ProjectSession {
  public readonly projectId: string;
  private currentEnvelope: ProjectEnvelope;
  private repo: ProjectRepository;
  private revisionManager: RevisionManager;
  private transaction: ProjectTransaction;
  private lock: ProjectLock;
  private isClosed = false;

  constructor(params: {
    envelope: ProjectEnvelope;
    repo: ProjectRepository;
    revisionManager: RevisionManager;
    transaction: ProjectTransaction;
    lock: ProjectLock;
  }) {
    this.projectId = params.envelope.projectId;
    this.currentEnvelope = params.envelope;
    this.repo = params.repo;
    this.revisionManager = params.revisionManager;
    this.transaction = params.transaction;
    this.lock = params.lock;
  }

  public get revisionId(): string {
    return this.currentEnvelope.revisionId;
  }

  public get contentHash(): string {
    return this.currentEnvelope.contentHash;
  }

  /**
   * Retorna una copia profunda e inmutable (clon defensivo) del estado actual de la IR del proyecto.
   */
  public getProject<T = Record<string, unknown>>(): T {
    return JSON.parse(JSON.stringify(this.currentEnvelope.project)) as T;
  }

  /**
   * Obtiene el envelope completo activo.
   */
  public getEnvelope(): ProjectEnvelope {
    return JSON.parse(JSON.stringify(this.currentEnvelope));
  }

  /**
   * Evalúa el fotograma de la composición en el tiempo t de forma pura.
   */
  public evaluate(time: Time) {
    const comp: Composition = ProjectDeserializer.deserializeComposition(this.currentEnvelope);
    return comp.evaluate(time);
  }

  /**
   * Ejecuta una mutación atómica y transaccional sobre el proyecto.
   */
  public async transact<R = unknown>(
    mutation: ProjectMutation<Record<string, unknown>, R>,
    options: { description?: string; operation?: string } = {}
  ): Promise<{ result: R; newRevisionId: string }> {
    if (this.isClosed) {
      throw new Error(`Cannot execute transaction on closed ProjectSession '${this.projectId}'.`);
    }

    const { result, envelope } = await this.transaction.execute({
      projectId: this.projectId,
      baseRevisionId: this.currentEnvelope.revisionId,
      currentProject: this.currentEnvelope.project,
      operation: options.operation ?? "session_transact",
      description: options.description,
      mutation,
    });

    this.currentEnvelope = envelope;
    return { result, newRevisionId: envelope.revisionId };
  }

  /**
   * Cierra la sesión activa liberando bloqueos de concurrencia.
   */
  public async close(): Promise<void> {
    if (this.isClosed) return;
    this.isClosed = true;
    await this.lock.release();
  }
}

import { ProjectStore } from "../persistence/ProjectStore.js";
import { RevisionManager } from "../revisions/RevisionManager.js";

/**
 * Contexto de ejecución de un workflow con acceso a almacenamiento y estado compartido (Fase 18).
 */
export class WorkflowContext {
  public readonly workflowId: string;
  public readonly projectId: string;
  public revisionId: string;
  public readonly variables = new Map<string, unknown>();
  public readonly store: ProjectStore;
  public readonly revisionManager: RevisionManager;
  public readonly dryRun: boolean;

  constructor(params: {
    workflowId: string;
    projectId: string;
    revisionId: string;
    store: ProjectStore;
    revisionManager: RevisionManager;
    dryRun?: boolean;
    initialVariables?: Record<string, unknown>;
  }) {
    this.workflowId = params.workflowId;
    this.projectId = params.projectId;
    this.revisionId = params.revisionId;
    this.store = params.store;
    this.revisionManager = params.revisionManager;
    this.dryRun = params.dryRun ?? false;

    if (params.initialVariables) {
      for (const [k, v] of Object.entries(params.initialVariables)) {
        this.variables.set(k, v);
      }
    }
  }

  public set(key: string, value: unknown): void {
    this.variables.set(key, value);
  }

  public get<T = unknown>(key: string): T | undefined {
    return this.variables.get(key) as T | undefined;
  }
}

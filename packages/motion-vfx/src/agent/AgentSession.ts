import { RevisionConflictError } from "../persistence/errors/persistence-errors.js";
import { ProjectStore } from "../persistence/ProjectStore.js";
import { Revision, RevisionAuthor } from "../persistence/schemas/revision.schema.js";
import { RevisionManager } from "../revisions/RevisionManager.js";
import { AgentAction, AgentDecision, AgentObservation } from "./AgentAction.js";
import { AgentMemory, AgentPolicy, DefaultAgentPolicy } from "./AgentPolicy.js";
import { AgentValidator } from "./AgentValidator.js";

/**
 * Sesión de trabajo autónoma para un agente de IA con control de concurrencia optimista (Fase 18).
 */
export class AgentSession {
  public readonly sessionId: string;
  public readonly agentId: string;
  public readonly projectId: string;
  public expectedRevisionId: string;
  public readonly policy: AgentPolicy;
  public readonly memory = new AgentMemory();

  private store: ProjectStore;
  private revisionManager: RevisionManager;

  constructor(params: {
    sessionId: string;
    agentId: string;
    projectId: string;
    initialRevisionId: string;
    store: ProjectStore;
    revisionManager: RevisionManager;
    policy?: AgentPolicy;
  }) {
    this.sessionId = params.sessionId;
    this.agentId = params.agentId;
    this.projectId = params.projectId;
    this.expectedRevisionId = params.initialRevisionId;
    this.store = params.store;
    this.revisionManager = params.revisionManager;
    this.policy = params.policy ?? DefaultAgentPolicy;
  }

  /**
   * Obtiene la observación del estado actual del proyecto.
   */
  public async observe(): Promise<AgentObservation> {
    const projectFile = await this.store.get(this.projectId);
    const rawComp = (projectFile.project as any)?.composition ?? projectFile.project;
    const elements = projectFile.project.elements ?? rawComp?.elements ?? rawComp?.layers ?? [];

    const observation: AgentObservation = {
      observationId: `obs_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
      projectId: this.projectId,
      revisionId: projectFile.headRevisionId,
      summary: {
        layerCount: Array.isArray(elements) ? elements.length : 0,
        captionCount: (projectFile.project as any)?.captions?.length ?? 0,
        duration: rawComp?.duration ?? 0,
        fps: rawComp?.fps ?? 30,
      },
      timestamp: new Date().toISOString(),
    };

    this.memory.logObservation(observation);
    return observation;
  }

  /**
   * Aplica una mutación atómica al proyecto bajo concurrencia optimista.
   */
  public async mutate(params: {
    action: AgentAction;
    rationale: string;
    expectedOutcome: string;
    mutation: (draft: Record<string, unknown>) => Record<string, unknown>;
  }): Promise<Revision> {
    // 1. Validar política
    const val = AgentValidator.validateAction(params.action, this.policy);
    if (!val.allowed) {
      throw new Error(`Agent action rejected by policy: ${val.reason}`);
    }

    // 2. Comprobar concurrencia optimista contra HEAD actual
    const currentProjectFile = await this.store.get(this.projectId);
    if (currentProjectFile.headRevisionId !== this.expectedRevisionId) {
      throw new RevisionConflictError(this.projectId, this.expectedRevisionId, currentProjectFile.headRevisionId);
    }

    // 3. Ejecutar mutación sobre clon defensivo
    const draft = JSON.parse(JSON.stringify(currentProjectFile.project));
    const nextProject = params.mutation(draft);

    const author: RevisionAuthor = {
      type: "agent",
      agentId: this.agentId,
    };

    // 4. Crear nueva revisión
    const newRevision = await this.revisionManager.createRevision({
      projectId: this.projectId,
      parentRevisionId: this.expectedRevisionId,
      project: nextProject,
      author,
      message: params.rationale,
    });

    // 5. Actualizar expectedRevisionId a la nueva revisión creada
    this.expectedRevisionId = newRevision.revisionId;

    const decision: AgentDecision = {
      decisionId: `dec_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
      agentId: this.agentId,
      action: params.action,
      rationale: params.rationale,
      expectedOutcome: params.expectedOutcome,
      timestamp: new Date().toISOString(),
    };
    this.memory.logDecision(decision);

    return newRevision;
  }
}

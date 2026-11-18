import { MemoryProjectStore } from "../../persistence/MemoryProjectStore.js";
import { ProjectStore } from "../../persistence/ProjectStore.js";
import { RevisionAuthor } from "../../persistence/schemas/revision.schema.js";
import { ProjectMutation } from "../../project/ProjectMutation.js";
import { ProjectQuery } from "../../project/ProjectQuery.js";
import { ProjectService } from "../../project/ProjectService.js";
import { ProjectSnapshot } from "../../project/ProjectSnapshot.js";
import { RevisionDiff } from "../../revisions/RevisionDiff.js";
import { RevisionManager } from "../../revisions/RevisionManager.js";
import { WorkflowContext } from "../../workflows/WorkflowContext.js";
import { WorkflowEngine } from "../../workflows/WorkflowEngine.js";
import { StepRegistry } from "../../workflows/WorkflowStep.js";
import { McpValidationError } from "../errors/mcp-errors.js";
import {
  CancelWorkflowSchema,
  CreateProjectSchema,
  CreateRevisionSchema,
  DiffRevisionsSchema,
  GetProjectSchema,
  GetRevisionSchema,
  GetWorkflowStatusSchema,
  ListProjectsSchema,
  ListRevisionsSchema,
  OpenProjectSchema,
  RestoreRevisionSchema,
  ResumeWorkflowSchema,
  RunWorkflowSchema,
  SaveProjectSchema,
  UndoRevisionSchema,
  ValidateProjectSchema,
} from "../schemas/phase18-tools.schema.js";

/**
 * Entorno y contexto de producción para herramientas MCP (Fase 18).
 */
export class ProductionMCPContext {
  private static defaultStore: ProjectStore = new MemoryProjectStore();
  private static defaultRevisionManager = new RevisionManager(this.defaultStore);
  private static defaultProjectService = new ProjectService(this.defaultStore, this.defaultRevisionManager);
  private static defaultWorkflowEngine = new WorkflowEngine();

  public static getStore(): ProjectStore {
    return this.defaultStore;
  }

  public static setStore(store: ProjectStore): void {
    this.defaultStore = store;
    this.defaultRevisionManager = new RevisionManager(store);
    this.defaultProjectService = new ProjectService(store, this.defaultRevisionManager);
  }

  public static getRevisionManager(): RevisionManager {
    return this.defaultRevisionManager;
  }

  public static getProjectService(): ProjectService {
    return this.defaultProjectService;
  }

  public static getWorkflowEngine(): WorkflowEngine {
    return this.defaultWorkflowEngine;
  }

  public static reset(): void {
    this.defaultStore = new MemoryProjectStore();
    this.defaultRevisionManager = new RevisionManager(this.defaultStore);
    this.defaultProjectService = new ProjectService(this.defaultStore, this.defaultRevisionManager);
    this.defaultWorkflowEngine = new WorkflowEngine();
  }
}

// 1. handleCreateProject
export async function handleCreateProject(rawArgs: unknown) {
  const parse = CreateProjectSchema.safeParse(rawArgs);
  if (!parse.success) throw new McpValidationError("Invalid arguments for create_project", { issues: parse.error.issues });
  const args = parse.data;

  const author: RevisionAuthor = { type: "agent", agentId: args.author };
  const initialProject = {
    schemaVersion: "1.8.0",
    composition: {
      id: `comp_${args.projectId}`,
      name: args.name,
      width: args.width,
      height: args.height,
      fps: args.fps,
      duration: args.duration,
      layers: [],
    },
    elements: args.initialElements ?? [],
    assets: [],
  };

  const service = ProductionMCPContext.getProjectService();
  const { projectFile, snapshot } = await service.createProject({
    projectId: args.projectId,
    project: initialProject,
    metadata: {
      name: args.name,
      description: args.description,
      author: args.author,
      tags: [],
    },
    author,
    message: "Project created via MCP",
  });

  return {
    projectId: projectFile.projectId,
    headRevisionId: projectFile.headRevisionId,
    contentHash: projectFile.contentHash,
    status: "created",
    metadata: projectFile.metadata,
  };
}

// 2. handleOpenProject
export async function handleOpenProject(rawArgs: unknown) {
  const parse = OpenProjectSchema.safeParse(rawArgs);
  if (!parse.success) throw new McpValidationError("Invalid arguments for open_project", { issues: parse.error.issues });
  const { projectId, revisionId } = parse.data;

  const service = ProductionMCPContext.getProjectService();
  const snapshot = await service.getSnapshot(projectId, revisionId);

  return {
    projectId: snapshot.projectId,
    revisionId: snapshot.revisionId,
    projectHash: snapshot.projectHash,
    summary: {
      elementsCount: ProjectQuery.getElements(snapshot).length,
      duration: ProjectQuery.getDuration(snapshot),
    },
  };
}

// 3. handleSaveProject
export async function handleSaveProject(rawArgs: unknown) {
  const parse = SaveProjectSchema.safeParse(rawArgs);
  if (!parse.success) throw new McpValidationError("Invalid arguments for save_project", { issues: parse.error.issues });
  const { projectId, message, author } = parse.data;

  const store = ProductionMCPContext.getStore();
  const projectFile = await store.get(projectId);

  return {
    projectId,
    headRevisionId: projectFile.headRevisionId,
    saved: true,
    message,
    updatedAt: projectFile.updatedAt,
  };
}

// 4. handleGetProject
export async function handleGetProject(rawArgs: unknown) {
  const parse = GetProjectSchema.safeParse(rawArgs);
  if (!parse.success) throw new McpValidationError("Invalid arguments for get_project", { issues: parse.error.issues });
  const { projectId, revisionId } = parse.data;

  const service = ProductionMCPContext.getProjectService();
  const snapshot = await service.getSnapshot(projectId, revisionId);

  return {
    projectId: snapshot.projectId,
    revisionId: snapshot.revisionId,
    projectHash: snapshot.projectHash,
    project: snapshot.getRawData(),
  };
}

// 5. handleListProjects
export async function handleListProjects(rawArgs: unknown) {
  const parse = ListProjectsSchema.safeParse(rawArgs);
  if (!parse.success) throw new McpValidationError("Invalid arguments for list_projects", { issues: parse.error.issues });

  const service = ProductionMCPContext.getProjectService();
  const list = await service.listProjects();

  return {
    projects: list.slice(0, parse.data.limit),
    totalCount: list.length,
  };
}

// 6. handleCreateRevision
export async function handleCreateRevision(rawArgs: unknown) {
  const parse = CreateRevisionSchema.safeParse(rawArgs);
  if (!parse.success) throw new McpValidationError("Invalid arguments for create_revision", { issues: parse.error.issues });
  const args = parse.data;

  const store = ProductionMCPContext.getStore();
  const revManager = ProductionMCPContext.getRevisionManager();
  const current = await store.get(args.projectId);

  const author: RevisionAuthor = { type: "agent", agentId: args.author };
  const nextData = args.projectData ?? current.project;

  const rev = await revManager.createRevision({
    projectId: args.projectId,
    parentRevisionId: args.parentRevisionId !== undefined ? args.parentRevisionId : current.headRevisionId,
    project: nextData,
    author,
    message: args.message,
  });

  return {
    projectId: rev.projectId,
    revisionId: rev.revisionId,
    parentRevisionId: rev.parentRevisionId,
    projectHash: rev.projectHash,
    createdAt: rev.createdAt,
  };
}

// 7. handleGetRevision
export async function handleGetRevision(rawArgs: unknown) {
  const parse = GetRevisionSchema.safeParse(rawArgs);
  if (!parse.success) throw new McpValidationError("Invalid arguments for get_revision", { issues: parse.error.issues });
  const { projectId, revisionId } = parse.data;

  const revManager = ProductionMCPContext.getRevisionManager();
  const rev = await revManager.getRevision(projectId, revisionId);

  return {
    revisionId: rev.revisionId,
    projectId: rev.projectId,
    parentRevisionId: rev.parentRevisionId,
    createdBy: rev.createdBy,
    message: rev.message,
    projectHash: rev.projectHash,
    changesCount: rev.changes.length,
    project: rev.project,
  };
}

// 8. handleListRevisions
export async function handleListRevisions(rawArgs: unknown) {
  const parse = ListRevisionsSchema.safeParse(rawArgs);
  if (!parse.success) throw new McpValidationError("Invalid arguments for list_revisions", { issues: parse.error.issues });

  const revManager = ProductionMCPContext.getRevisionManager();
  const list = await revManager.listRevisions(parse.data.projectId);

  return {
    projectId: parse.data.projectId,
    revisions: list,
    totalCount: list.length,
  };
}

// 9. handleDiffRevisions
export async function handleDiffRevisions(rawArgs: unknown) {
  const parse = DiffRevisionsSchema.safeParse(rawArgs);
  if (!parse.success) throw new McpValidationError("Invalid arguments for diff_revisions", { issues: parse.error.issues });
  const { projectId, fromRevisionId, toRevisionId } = parse.data;

  const revManager = ProductionMCPContext.getRevisionManager();
  const diffResult = await revManager.diffRevisions(projectId, fromRevisionId, toRevisionId);

  return {
    projectId,
    fromRevisionId,
    toRevisionId,
    changes: diffResult.changes,
    summary: diffResult.summary,
  };
}

// 10. handleRestoreRevision
export async function handleRestoreRevision(rawArgs: unknown) {
  const parse = RestoreRevisionSchema.safeParse(rawArgs);
  if (!parse.success) throw new McpValidationError("Invalid arguments for restore_revision", { issues: parse.error.issues });
  const args = parse.data;

  const revManager = ProductionMCPContext.getRevisionManager();
  const author: RevisionAuthor = { type: "agent", agentId: args.author };

  const restored = await revManager.restoreRevision({
    projectId: args.projectId,
    targetRevisionId: args.targetRevisionId,
    author,
    message: args.message,
  });

  return {
    projectId: restored.projectId,
    newHeadRevisionId: restored.revisionId,
    restoredFromRevisionId: args.targetRevisionId,
    status: "restored",
  };
}

// 11. handleUndoRevision
export async function handleUndoRevision(rawArgs: unknown) {
  const parse = UndoRevisionSchema.safeParse(rawArgs);
  if (!parse.success) throw new McpValidationError("Invalid arguments for undo_revision", { issues: parse.error.issues });
  const args = parse.data;

  const revManager = ProductionMCPContext.getRevisionManager();
  const author: RevisionAuthor = { type: "agent", agentId: args.author };

  const undone = await revManager.undoRevision({
    projectId: args.projectId,
    targetRevisionId: args.targetRevisionId,
    author,
    message: args.message,
  });

  return {
    projectId: undone.projectId,
    newHeadRevisionId: undone.revisionId,
    undoneRevisionId: args.targetRevisionId,
    status: "undone",
  };
}

// 12. handleRunWorkflow
export async function handleRunWorkflow(rawArgs: unknown) {
  const parse = RunWorkflowSchema.safeParse(rawArgs);
  if (!parse.success) throw new McpValidationError("Invalid arguments for run_workflow", { issues: parse.error.issues });
  const args = parse.data;

  const engine = ProductionMCPContext.getWorkflowEngine();
  const store = ProductionMCPContext.getStore();
  const revManager = ProductionMCPContext.getRevisionManager();

  const definition = engine.getWorkflowDefinition(args.workflowId);
  if (!definition) {
    throw new Error(`Workflow definition '${args.workflowId}' is not registered`);
  }

  const projectFile = await store.get(args.projectId);
  const context = new WorkflowContext({
    workflowId: args.workflowId,
    projectId: args.projectId,
    revisionId: args.revisionId ?? projectFile.headRevisionId,
    store,
    revisionManager: revManager,
    dryRun: args.dryRun,
    initialVariables: args.parameters,
  });

  const result = await engine.executeWorkflow({ definition, context });

  return {
    workflowId: result.workflowId,
    projectId: result.projectId,
    status: result.status,
    completedSteps: result.completedSteps,
    stepResults: result.stepResults,
    initialRevisionId: result.initialRevisionId,
    finalRevisionId: result.finalRevisionId,
  };
}

// 13. handleGetWorkflowStatus
export async function handleGetWorkflowStatus(rawArgs: unknown) {
  const parse = GetWorkflowStatusSchema.safeParse(rawArgs);
  if (!parse.success) throw new McpValidationError("Invalid arguments for get_workflow_status", { issues: parse.error.issues });

  const engine = ProductionMCPContext.getWorkflowEngine();
  const state = engine.getWorkflowState(parse.data.workflowId);
  const checkpoints = engine.getCheckpointManager().getCheckpoints(parse.data.workflowId);

  return {
    workflowId: parse.data.workflowId,
    state,
    checkpointCount: checkpoints.length,
    latestCheckpoint: checkpoints.length > 0 ? checkpoints[checkpoints.length - 1] : null,
  };
}

// 14. handleCancelWorkflow
export async function handleCancelWorkflow(rawArgs: unknown) {
  const parse = CancelWorkflowSchema.safeParse(rawArgs);
  if (!parse.success) throw new McpValidationError("Invalid arguments for cancel_workflow", { issues: parse.error.issues });

  const engine = ProductionMCPContext.getWorkflowEngine();
  engine.cancelWorkflow(parse.data.workflowId, parse.data.reason);

  return {
    workflowId: parse.data.workflowId,
    status: "cancellation_requested",
  };
}

// 15. handleResumeWorkflow
export async function handleResumeWorkflow(rawArgs: unknown) {
  const parse = ResumeWorkflowSchema.safeParse(rawArgs);
  if (!parse.success) throw new McpValidationError("Invalid arguments for resume_workflow", { issues: parse.error.issues });

  const engine = ProductionMCPContext.getWorkflowEngine();
  const store = ProductionMCPContext.getStore();
  const revManager = ProductionMCPContext.getRevisionManager();

  const definition = engine.getWorkflowDefinition(parse.data.workflowId);
  if (!definition) {
    throw new Error(`Workflow definition '${parse.data.workflowId}' is not registered`);
  }

  const projectFile = await store.get(parse.data.projectId);
  const context = new WorkflowContext({
    workflowId: parse.data.workflowId,
    projectId: parse.data.projectId,
    revisionId: projectFile.headRevisionId,
    store,
    revisionManager: revManager,
  });

  const result = await engine.resumeWorkflow({ definition, context });

  return {
    workflowId: result.workflowId,
    projectId: result.projectId,
    status: result.status,
    completedSteps: result.completedSteps,
    finalRevisionId: result.finalRevisionId,
  };
}

// 16. handleValidateProject
export async function handleValidateProject(rawArgs: unknown) {
  const parse = ValidateProjectSchema.safeParse(rawArgs);
  if (!parse.success) throw new McpValidationError("Invalid arguments for validate_project", { issues: parse.error.issues });

  const service = ProductionMCPContext.getProjectService();
  const snapshot = await service.getSnapshot(parse.data.projectId, parse.data.revisionId);

  const raw = snapshot.getRawData<any>();
  let valid = true;
  const errors: string[] = [];

  const comp = raw.composition ?? raw;
  if (comp) {
    if (comp.duration !== undefined && comp.duration <= 0) {
      valid = false;
      errors.push("Composition duration must be greater than 0");
    }
    if (comp.fps !== undefined && comp.fps <= 0) {
      valid = false;
      errors.push("Composition FPS must be greater than 0");
    }
    if (comp.width !== undefined && comp.width <= 0) {
      valid = false;
      errors.push("Composition width must be greater than 0");
    }
    if (comp.height !== undefined && comp.height <= 0) {
      valid = false;
      errors.push("Composition height must be greater than 0");
    }
  }

  return {
    projectId: snapshot.projectId,
    revisionId: snapshot.revisionId,
    valid,
    errors,
  };
}

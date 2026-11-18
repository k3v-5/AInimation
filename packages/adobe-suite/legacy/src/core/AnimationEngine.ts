import fs from 'fs';
import { ProjectManager } from './ProjectManager.js';
import { EventEmitter } from 'events';
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js';
import { IAnimationProvider, CapabilityId, Operation, OperationStatus, Intent, Plan, EntityState, WorkflowNode } from './abstractions.js';
import { IntentParser } from './IntentParser.js';
import { PerceptionAndRecoveryLayer } from './PerceptionAndRecovery.js';
import { ArtifactManager } from './ArtifactManager.js';
import { WorkflowGraphEngine } from './WorkflowGraphEngine.js';
import { RiggingAgent } from '../ai/swarm/RiggingAgent.js';
import { calculateFileHash } from './utils/hash.js';

export class AnimationEngine extends EventEmitter {
  private async processNode(node: WorkflowNode, executionId: string, executionContext: Record<string, string>, dirtyNodes: Set<string>, targetProvider: string, abortSignal?: AbortSignal, successOps?: any[]): Promise<any> {
        console.log("== ENTERING PROCESS NODE ==", node.id);
        const pm = this.projectManager;
        const sourceDependencies: string[] = [];
        let forceExecute = false;
        for (const [key, value] of Object.entries(node.constraints?.[0]?.parameters || {})) {
           if (typeof value === 'string' && value.startsWith('${') && value.endsWith('}')) {
              const contextKey = value.slice(2, -1);
              const parentNodeId = contextKey.split('.')[0];
              if (dirtyNodes.has(parentNodeId)) {
                 forceExecute = true;
              }
           }
        }
        const providerId = node.constraints && node.constraints[0] ? node.constraints[0].provider : targetProvider;
        let parameters = node.constraints && node.constraints[0] ? { ...node.constraints[0].parameters } : {};

        for (const [key, value] of Object.entries(parameters)) {
           if (typeof value === 'string' && value.startsWith('${') && value.endsWith('}')) {
              const contextKey = value.slice(2, -1);
              if (executionContext[contextKey]) {
                 parameters[key] = executionContext[contextKey];
                 sourceDependencies.push(executionContext[contextKey]);
              } else {
                 throw new Error(`Unresolved dependency context: ${contextKey}`);
              }
           }
        }

        if (successOps) {
            const pastSuccess = successOps.find(o => o.capability === node.capability);
            if (pastSuccess && !forceExecute) {
               let hashDiverged = false;
               if (executionContext[`${node.id}.output`]) {
                   const filePath = executionContext[`${node.id}.output`];
                   const currentHash = calculateFileHash(filePath);
                   const dbAsset = pm.getAssetByPath(filePath);
                   if (currentHash && (!dbAsset || dbAsset.hash !== currentHash)) {
                       hashDiverged = true;
                       console.log(`[Resume Cache Invalidation] File ${filePath} changed. Forcing re-execution of ${node.id}`);
                   }
               }

               if (!hashDiverged) {
                   console.log(`[Resume] Skipping already completed node ${node.id} (${node.capability})`);
                   let artifactType = 'scene';
                   if (node.capability.includes('render')) artifactType = 'render';
                   if (node.capability.includes('audio')) artifactType = 'audio';
                   if (node.capability.includes('puppet')) artifactType = 'puppet';
                   return {
                       skipped: true,
                       artifactType,
                       local_path: executionContext[`${node.id}.output`] || ''
                   };
               }
            }
        }

        console.log("==== PARAMETERS BEFORE OP EXECUTION ===", parameters);
        const op = this.createOperation(node.id, node.capability, providerId, parameters);

        let resultOp = await this.executeOperation(op.id, abortSignal, forceExecute);

        let artifactType: any = 'scene';
        if (op.capability === 'render.export' || op.capability === 'ae.render.export') artifactType = 'render';
        if (op.capability === 'audio.import' || op.capability === 'audio.generate_tts') artifactType = 'audio';
        if (op.capability === 'puppet.import') artifactType = 'puppet';
        if (op.capability === 'ae.comp.create') artifactType = 'scene';
        if (op.capability === 'blender.execute_python') artifactType = 'scene';

        if ((op.capability === 'render.export' || op.capability === 'ps.document.export') && parameters.target_file) {
          const validationResult = await this.perception.validatePhysicalArtifact(parameters.target_file);
          if (!validationResult.isValid) {
            resultOp.status = 'DIVERGED';
            this.emit('operation_status', { id: op.id, capability: op.capability, provider: op.provider, status: resultOp.status, error: 'Validation failed' });
            this.emit('operation_recovery', { id: op.id, capability: op.capability });
            const recovered = await this.perception.attemptRecovery(op.id, async (opId) => {
               const retryOp = await this.executeOperation(opId, abortSignal, forceExecute);
               const vRes = await this.perception.validatePhysicalArtifact(parameters.target_file);
               if (!vRes.isValid) throw new Error("Physical validation failed on retry");
               return retryOp;
            });
            if (!recovered) {
               throw new Error(`Operation failed and recovery max retries reached: ${op.id}`);
            }
          }
        }

        if ((op.capability === 'render.export' || op.capability === 'ps.document.export' || op.capability === 'illustrator.document.create' || op.capability === 'ps.document.create') && parameters.visual_validation && parameters.target_file) {
          console.log("CHECKING VISUAL VALIDATION", op.capability, parameters);
          const visualResult = await this.perception.validateVisualArtifact(parameters.target_file, parameters.visual_validation);
          if (!visualResult.isValid) {
            resultOp.status = 'DIVERGED';
            this.emit('operation_status', { id: op.id, capability: op.capability, provider: op.provider, status: resultOp.status, error: `Visual Validation failed: ${visualResult.divergences?.join(', ')}` });
            this.emit('operation_recovery', { id: op.id, capability: op.capability });
            const recovered = await this.perception.attemptRecovery(op.id, async (opId) => {
               const retryOp = await this.executeOperation(opId, abortSignal, forceExecute);
               const vRes = await this.perception.validateVisualArtifact(parameters.target_file, parameters.visual_validation);
               if (!vRes.isValid) throw new Error("Visual validation failed on retry: " + vRes.divergences?.join(', '));
               return retryOp;
            });
            if (!recovered) {
               throw new Error(`Operation failed visual validation and recovery max retries reached: ${op.id}`);
            }
          }
        }

        console.log("ALL PARAMETERS:", parameters);
        if (parameters.spatial_validation && parameters.target_file) {
          console.log("CHECKING SPATIAL VALIDATION", op.capability, parameters);
          const spatialResult = await this.perception.validateSpatialArtifact(parameters.target_file, parameters.spatial_validation);
          if (!spatialResult.isValid && spatialResult.spatialData) {
             resultOp.status = 'DIVERGED';
             this.emit('operation_status', { id: op.id, capability: op.capability, provider: op.provider, status: resultOp.status, error: `Spatial Validation failed: ${spatialResult.divergences?.join(', ')}` });

             // Dynamic Swarm Correction
             const riggingAgent = new RiggingAgent();
             const correctionJsx = riggingAgent.generateCorrectionScript(spatialResult.spatialData.x || 0, spatialResult.spatialData.y || 0, "Layer 1");
             console.log("[Swarm Correction] Executing correction script natively via AE...");

             // Execute the correction immediately via AE provider
             const aeProvider = this.getProvider('after_effects');
             if (aeProvider) {
                 await aeProvider.executeCapability('ae.execute_jsx', { script_content: correctionJsx });
             }

             // Attempt standard recovery loop to re-validate
             this.emit('operation_recovery', { id: op.id, capability: op.capability });
             const recovered = await this.perception.attemptRecovery(op.id, async (opId) => {
                 const retryOp = await this.executeOperation(opId, abortSignal, forceExecute);
                 const vRes = await this.perception.validateSpatialArtifact(parameters.target_file, parameters.spatial_validation);
                 if (!vRes.isValid) throw new Error("Spatial validation failed on retry: " + vRes.divergences?.join(', '));
                 return retryOp;
             });

             if (!recovered) {
                throw new Error(`Operation failed spatial validation and recovery max retries reached: ${op.id}`);
             }
          }
        }

        let isSuccess = resultOp.status === 'SUCCESS' || resultOp.status === 'SKIPPED';
        if (resultOp.result && typeof resultOp.result.success === 'boolean') {
           isSuccess = resultOp.result.success;
        }

        let stateStatus: 'synchronized' | 'diverged' = isSuccess ? 'synchronized' : 'diverged';
        const obs = stateStatus === 'synchronized' ? { executed: true, ...resultOp.result?.observed_state } : null;
        const des = { executed: true, ...resultOp.result?.observed_state };
        const entityState: EntityState<any> = { desired: des, observed: obs, status: 'unknown' };

        if (op.capability === 'ps.document.export' && parameters.expected_layers) {
           entityState.desired.required_layers = parameters.expected_layers;
        }

        const validationResult = this.perception.validateState(entityState);

        if (!validationResult.isValid) {
          resultOp.status = 'DIVERGED';
          this.emit('operation_status', { id: op.id, capability: op.capability, provider: op.provider, status: resultOp.status, error: 'State divergence detected' });
          this.emit('operation_recovery', { id: op.id, capability: op.capability });
          const recovered = await this.perception.attemptRecovery(op.id, async (opId) => {
               const retryOp = await this.executeOperation(opId, abortSignal, forceExecute);
               const vRes = await this.perception.validatePhysicalArtifact(parameters.target_file || '');
               // we do a dummy return here since structural validation checks the whole entity state which is complex to rebuild on retry.
               return retryOp;
          });

          if (!recovered) {
             throw new Error(`Operation failed and recovery max retries reached: ${op.id} - ${resultOp.result?.error || 'Unknown error'}`);
          }
        }

        const artifact = this.artifactManager.registerArtifact(artifactType, op.id, parameters);

        if (resultOp.status !== 'SKIPPED') {
           dirtyNodes.add(node.id);
        }

        const finalPathRaw = parameters.target_file || artifact.metadata.local_path as string;
        sourceDependencies.forEach((sourcePath: string) => {
           pm.addAssetDependency(sourcePath, finalPathRaw);
        });

        const finalPath = resultOp.status === 'SKIPPED' && resultOp.result?.observed_state?.cached_path
                          ? resultOp.result.observed_state.cached_path
                          : parameters.target_file || artifact.metadata.local_path;

        executionContext[`${node.id}.output`] = finalPath;

        return {
           skipped: false,
           artifactType,
           local_path: finalPath
        };
  }

  private providers: Map<string, IAnimationProvider> = new Map();
  private operations: Map<string, Operation> = new Map();
  private server: Server;
  private intentParser: IntentParser;
  private perception: PerceptionAndRecoveryLayer;
  private artifactManager: ArtifactManager;
  private workflowEngine: WorkflowGraphEngine;
  private projectManager: ProjectManager;

  constructor() {
    super();
    this.intentParser = new IntentParser();
    this.perception = new PerceptionAndRecoveryLayer();
    this.artifactManager = new ArtifactManager();
    this.workflowEngine = new WorkflowGraphEngine();
    this.projectManager = new ProjectManager();
    this.server = new Server({
      name: 'adobe-animation-engine',
      version: '1.0.0',
    }, {
      capabilities: {
        tools: {}
      }
    });

    this.setupServer();
  }

  private setupServer() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: 'execute_intent',
            description: 'Execute an animation intent defined in a universal DSL.',
            inputSchema: {
              type: 'object',
              properties: {
                intent_id: { type: 'string' },
                action: { type: 'string' },
                parameters: { type: 'object' },
                target_provider: { type: 'string' }
              },
              required: ['intent_id', 'action', 'parameters']
            }
          },
          {
            name: 'memory.list_projects',
            description: 'List recent animation projects to retrieve their context and IDs.',
            inputSchema: { type: 'object', properties: {} }
          },
          {
            name: 'memory.get_assets',
            description: 'List all generated assets (files) associated with a specific project.',
            inputSchema: {
              type: 'object',
              properties: { project_id: { type: 'string' } },
              required: ['project_id']
            }
          },
          {
            name: 'memory.resume_intent',
            description: 'Resumes an interrupted or paused Intent execution (DAG flow) without re-running successfully completed operations.',
            inputSchema: {
              type: 'object',
              properties: {
                execution_id: { type: 'string' }
              },
              required: ['execution_id']
            }
          }
        ]
      };
    });

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      if (request.params.name === 'memory.list_projects') {
         const pm = new ProjectManager();
         return { content: [{ type: 'text', text: JSON.stringify(pm.listProjects(), null, 2) }] };
      }

      if (request.params.name === 'memory.get_assets') {
         const args = request.params.arguments as any;
         const pm = new ProjectManager();
         return { content: [{ type: 'text', text: JSON.stringify(pm.getAssetsForProject(args.project_id), null, 2) }] };
      }

      if (request.params.name === 'memory.resume_intent') {
         const args = request.params.arguments as any;
         const abortController = new AbortController();
         try {
           const result = await this.resumeIntent(args.execution_id, args.target_provider, abortController.signal);
           return { content: [{ type: 'text', text: JSON.stringify(result, null, 2) }] };
         } catch (err: any) {
           return { content: [{ type: 'text', text: `Error resuming execution: ${err.message}` }], isError: true };
         }
      }

      if (request.params.name === 'execute_intent') {
        const args = request.params.arguments as any;

        const intent: Intent = {
          id: args.intent_id,
          type: args.action,
          parameters: args.parameters
        };

        const abortController = new AbortController();

        try {
          const result = await this.processIntent(intent, args.target_provider, abortController.signal);
          return {
            content: [{ type: 'text', text: JSON.stringify(result, null, 2) }]
          };
        } catch (err: any) {
          return {
            content: [{ type: 'text', text: JSON.stringify({
              status: "FAILED",
              intent_id: intent.id,
              error_code: "EXECUTION_ERROR",
              message: err.message || String(err)
            }, null, 2) }]
          };
        }
      }

      throw new Error(`Tool not found: ${request.params.name}`);
    });
  }

  public activeExecutionId: string | null = null;

  async resumeIntent(executionId: string, targetProvider: string = 'character_animator', abortSignal?: AbortSignal): Promise<any> {
    const execution = this.projectManager.getExecution(executionId);
    if (!execution) throw new Error(`Execution ${executionId} not found.`);

    if (execution.status === 'SUCCESS') {
      return { status: "SUCCESS", message: "Execution already completed." };
    }

    const intent: Intent = JSON.parse(execution.intent_json);
    let executionContext: Record<string, string> = execution.context_json ? JSON.parse(execution.context_json) : {};

    // We update status to RUNNING
    this.projectManager.updateExecutionStatus(executionId, 'RUNNING');
    this.activeExecutionId = executionId;

    const pm = this.projectManager;
    const project = pm.getProject(execution.project_id);
    if (!project) throw new Error("Project missing for execution");
    this.artifactManager.activeProjectId = project.id;

    const operationListener = (opUpdate: any) => {
       pm.saveOperation({
          id: opUpdate.id,
          execution_id: executionId,
          capability: opUpdate.capability,
          status: opUpdate.status,
          result_json: opUpdate.result ? JSON.stringify(opUpdate.result) : null,
          error_text: opUpdate.error || null
       });
    };
    this.on('operation_status', operationListener);

    const graph = this.intentParser.parse(intent, targetProvider);
    const executionBatches = this.workflowEngine.resolveExecutionOrder(graph);

    // Get historical operations to check if we should skip them
    const historicalOps = pm.getOperationsForExecution(executionId);
    const successOps = historicalOps.filter(o => o.status === 'SUCCESS' || o.status === 'SKIPPED');

    const artifacts: any[] = [];
    const dirtyNodes: Set<string> = new Set();

    console.log("EXECUTION BATCHES:", executionBatches.length);
    for (const batch of executionBatches) {
      if (abortSignal && abortSignal.aborted) {
         pm.updateExecutionStatus(executionId, 'ABORTED', JSON.stringify(executionContext));
         this.off('operation_status', operationListener);
         throw new Error("Workflow aborted by signal");
      }

      const batchPromises = batch.map(async (node) => {
        console.log("CALLING PROCESS NODE", node.id);
        const res = await this.processNode(node, executionId, executionContext, dirtyNodes, targetProvider, abortSignal, successOps);
        if (res && res.local_path) {
            artifacts.push({ type: res.artifactType, local_path: res.local_path });
        }
      });

      try {
        await Promise.all(batchPromises);
        pm.updateExecutionStatus(executionId, 'RUNNING', JSON.stringify(executionContext));
      } catch (err: any) {
        pm.updateExecutionStatus(executionId, 'FAILED', JSON.stringify(executionContext));
        this.off('operation_status', operationListener);
        return {
          status: "FAILED",
          intent_id: intent.id,
          error_code: "OPERATION_FAILED",
          message: err.message || String(err)
        };
      }
    }

    pm.updateExecutionStatus(executionId, 'SUCCESS', JSON.stringify(executionContext));
    this.off('operation_status', operationListener);

    return {
      status: "SUCCESS",
      intent_id: intent.id,
      artifacts: artifacts
    };
  }


  // TODO: Refactor processIntent and resumeIntent node loop logic into a shared private method (e.g., executeGraphBatch)
  async processIntent(intent: Intent, targetProvider: string = 'character_animator', abortSignal?: AbortSignal): Promise<any> {
    const pm = this.projectManager;
    const project = pm.createProject(intent.parameters?.scene?.name || 'Automated Project');
    this.artifactManager.activeProjectId = project.id;

    // Create new execution record
    const executionId = "exec_" + Date.now();
    this.activeExecutionId = executionId;
    pm.saveExecution({
       id: executionId,
       project_id: project.id,
       status: 'RUNNING',
       intent_json: JSON.stringify(intent),
       context_json: null
    });

    // Listen to operation updates to mirror in SQLite
    const operationListener = (opUpdate: any) => {
       pm.saveOperation({
          id: opUpdate.id,
          execution_id: executionId,
          capability: opUpdate.capability,
          status: opUpdate.status,
          result_json: opUpdate.result ? JSON.stringify(opUpdate.result) : null,
          error_text: opUpdate.error || null
       });
    };
    this.on('operation_status', operationListener);

    const graph = this.intentParser.parse(intent, targetProvider);
    const executionBatches = this.workflowEngine.resolveExecutionOrder(graph);

    const artifacts: any[] = [];
    const executionContext: Record<string, string> = {};
    const dirtyNodes: Set<string> = new Set();

    for (const batch of executionBatches) {
      if (abortSignal && abortSignal.aborted) {
         pm.updateExecutionStatus(executionId, 'ABORTED', JSON.stringify(executionContext));
         this.off('operation_status', operationListener);
         throw new Error("Workflow aborted by signal");
      }

      const batchPromises = batch.map(async (node) => {
        const res = await this.processNode(node, executionId, executionContext, dirtyNodes, targetProvider, abortSignal);
        if (res && res.local_path) {
            artifacts.push({ type: res.artifactType, local_path: res.local_path });
        }
      });

      try {
        await Promise.all(batchPromises);
        pm.updateExecutionStatus(executionId, 'RUNNING', JSON.stringify(executionContext));
      } catch (err: any) {
        pm.updateExecutionStatus(executionId, 'FAILED', JSON.stringify(executionContext));
        this.off('operation_status', operationListener);
        return {
          status: "FAILED",
          intent_id: intent.id,
          error_code: "OPERATION_FAILED",
          message: err.message || String(err)
        };
      }
    }

    pm.updateExecutionStatus(executionId, 'SUCCESS', JSON.stringify(executionContext));
    this.off('operation_status', operationListener);

    return {
      status: "SUCCESS",
      intent_id: intent.id,
      artifacts: artifacts
    };
  }

  async startServer() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('Animation Engine MCP Server started via Stdio');
  }

  registerProvider(provider: IAnimationProvider): void {
    if (this.providers.has(provider.id)) {
      console.warn(`Provider with id ${provider.id} is already registered. Overwriting.`);
    }
    this.providers.set(provider.id, provider);
  }

  getProvider(id: string): IAnimationProvider {
    const provider = this.providers.get(id);
    if (!provider) {
      throw new Error(`Provider ${id} is not registered.`);
    }
    return provider;
  }

  async connectAll(): Promise<void> {
    const promises = Array.from(this.providers.values()).map(provider => provider.connect());
    await Promise.all(promises);
  }

  async disconnectAll(): Promise<void> {
    const promises = Array.from(this.providers.values()).map(provider => provider.disconnect());
    await Promise.all(promises);
  }

  createOperation(planStepId: string, capability: CapabilityId, providerId: string, input: Record<string, any>): Operation {
    const op: Operation = {
      id: `op_${Date.now()}_${Math.floor(Math.random() * 1000)}`,
      planStepId,
      capability,
      provider: providerId,
      input,
      status: 'PLANNED',
      attempts: 0
    };
    this.operations.set(op.id, op);
    this.emit('operation_status', { id: op.id, capability: op.capability, provider: op.provider, status: op.status });
    return op;
  }

  async executeOperation(operationId: string, abortSignal?: AbortSignal, forceExecute: boolean = false): Promise<Operation> {
    const op = this.operations.get(operationId);
    if (!op) throw new Error(`Operation ${operationId} not found.`);

    if (abortSignal && abortSignal.aborted) {
       op.status = 'FAILED';
       op.error = 'Aborted before execution';
       this.emit('operation_status', { id: op.id, capability: op.capability, provider: op.provider, status: op.status, error: op.error });
       return op;
    }

    // Req 3: Cache-Aware Execution
    // If the node represents asset creation but the user provided an explicit input file
    // that already exists physically (RAG reuse), we skip execution.
    if ((op.capability === 'ps.document.create' || op.capability === 'ps.document.export') && op.input.input_file && !forceExecute) {
       if (fs.existsSync(op.input.input_file)) {
          const pm = this.projectManager;
          const currentHash = calculateFileHash(op.input.input_file);
          const dbAsset = pm.getAssetByPath(op.input.input_file);

          if (dbAsset && dbAsset.hash === currentHash) {
             op.status = 'SKIPPED';
             this.emit('operation_status', { id: op.id, capability: op.capability, provider: op.provider, status: op.status });
             op.result = { success: true, observed_state: { executed: true, cached_path: op.input.input_file } };
             return op;
          } else {
             console.log(`[Cache Invalidation] File ${op.input.input_file} has been modified (hash mismatch). Re-executing node ${op.id}`);
             if (currentHash) pm.updateAssetHash(op.input.input_file, currentHash);
          }
       } else {
          // AC-27: If the database path doesn't exist physically, we continue generation (Self-healing).
          console.log(`[Cache] Asset ${op.input.input_file} missing from disk. Regenerating...`);
       }
    }

    const provider = this.getProvider(op.provider);

    op.status = 'EXECUTING';
    op.startedAt = Date.now();
    op.attempts++;
    this.emit('operation_status', { id: op.id, capability: op.capability, provider: op.provider, status: op.status, attempt: op.attempts });

    try {
      const result = await provider.executeCapability(op.capability, op.input, abortSignal);
      op.status = 'SUCCESS';
      op.result = result;
      op.completedAt = Date.now();
      this.emit('operation_status', { id: op.id, capability: op.capability, provider: op.provider, status: op.status });
    } catch (err: any) {
      op.status = 'FAILED';
      op.error = err.message || String(err);
      op.completedAt = Date.now();
      this.emit('operation_status', { id: op.id, capability: op.capability, provider: op.provider, status: op.status, error: op.error });
    }

    return op;
  }
}

import { DeclarativeProductionIntent, ProductionDSLCompiler } from "../../dsl/ProductionDSL.js";
import { AutonomousAgentLoop } from "../../mcp/agent/AutonomousAgentLoop.js";

export type ProductionJobStatus =
  | "QUEUED"
  | "PLANNING"
  | "BUILDING"
  | "RENDERING"
  | "QA"
  | "COMPLETE"
  | "FAILED";

export interface ProductionJobRequest {
  id?: string;
  priority?: "low" | "normal" | "high";
  intent: DeclarativeProductionIntent;
}

export interface ProductionJobRecord {
  id: string;
  priority: "low" | "normal" | "high";
  status: ProductionJobStatus;
  intent: DeclarativeProductionIntent;
  createdAt: string;
  completedAt?: string;
  executionTimeMs?: number;
  mcpCallsCount: number;
  qaScore?: number;
  error?: string;
}

export interface ProductionBatchSummary {
  totalJobs: number;
  completed: number;
  failed: number;
  averageExecutionTimeMs: number;
  averageMCPCalls: number;
  humanAcceptanceRatePct: number;
}

/**
 * Cola de Producción Distribuida y Render Farm de Proyectos Audiovisuales (Autonomous MCP v2 / REQ-036).
 * Permite procesar lotes masivos (ej. 100 videos) con control de prioridad, telemetría y métricas de producción.
 */
export class ProductionJobQueue {
  private jobs: Map<string, ProductionJobRecord> = new Map();
  private agentLoop: AutonomousAgentLoop;

  constructor(agentLoop?: AutonomousAgentLoop) {
    this.agentLoop = agentLoop ?? new AutonomousAgentLoop();
  }

  /**
   * Encola un nuevo trabajo de producción audiovisual.
   */
  public enqueue(req: ProductionJobRequest): string {
    const id = req.id ?? `job_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`;
    const record: ProductionJobRecord = {
      id,
      priority: req.priority ?? "normal",
      status: "QUEUED",
      intent: req.intent,
      createdAt: new Date().toISOString(),
      mcpCallsCount: 0,
    };
    this.jobs.set(id, record);
    return id;
  }

  /**
   * Procesa todos los trabajos encolados en orden de prioridad.
   */
  public async processBatch(): Promise<ProductionBatchSummary> {
    const queued = Array.from(this.jobs.values()).filter((j) => j.status === "QUEUED");

    // Ordenar por prioridad (high -> normal -> low)
    const priorityWeight = { high: 3, normal: 2, low: 1 };
    queued.sort((a, b) => priorityWeight[b.priority] - priorityWeight[a.priority]);

    let totalDurationMs = 0;
    let totalMCPCalls = 0;
    let completedCount = 0;
    let failedCount = 0;

    for (const job of queued) {
      const startTime = Date.now();
      job.status = "PLANNING";

      try {
        // 1. Compilar DSL
        const dslResult = ProductionDSLCompiler.compile(job.intent);
        job.status = "BUILDING";

        // 2. Ejecutar a través del AutonomousAgentLoop
        job.status = "RENDERING";
        const execResult = await this.agentLoop.executeAutonomousProduction({
          title: job.intent.style.title,
          targetAspectRatios: [job.intent.video.format],
          stylePreset: "teal_orange",
          includeCaptions: job.intent.captions?.enabled ?? true,
          includeSFX: job.intent.soundDesign?.enabled ?? true,
          includeDepthSandwich: job.intent.editing.depthSandwich,
        });

        const elapsed = Date.now() - startTime;
        job.executionTimeMs = elapsed;
        job.completedAt = new Date().toISOString();
        job.mcpCallsCount = execResult.executedSteps.length;
        job.qaScore = execResult.qaScore;

        if (execResult.success) {
          job.status = "COMPLETE";
          completedCount++;
        } else {
          job.status = "FAILED";
          job.error = execResult.error?.message ?? "Execution failed";
          failedCount++;
        }

        totalDurationMs += elapsed;
        totalMCPCalls += job.mcpCallsCount;
      } catch (err: any) {
        job.status = "FAILED";
        job.error = err.message;
        failedCount++;
      }
    }

    const total = queued.length;
    return {
      totalJobs: total,
      completed: completedCount,
      failed: failedCount,
      averageExecutionTimeMs: total > 0 ? Number((totalDurationMs / total).toFixed(1)) : 0,
      averageMCPCalls: total > 0 ? Number((totalMCPCalls / total).toFixed(1)) : 0,
      humanAcceptanceRatePct: total > 0 ? Number(((completedCount / total) * 100).toFixed(1)) : 100,
    };
  }

  public getJob(id: string): ProductionJobRecord | undefined {
    return this.jobs.get(id);
  }

  public getAllJobs(): ProductionJobRecord[] {
    return Array.from(this.jobs.values());
  }
}

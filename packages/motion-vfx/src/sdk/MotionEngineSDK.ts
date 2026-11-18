import { Composition, CompositionOptions } from "../core/composition.js";
import { AfterEffectsJSXCompiler, JSXCompileOptions, JSXCompileResult } from "../exporters/ae/AfterEffectsJSXCompiler.js";
import { AEBridgeManager } from "../exporters/ae/AEBridgeManager.js";
import { SocialDeliveryPackager, PackageBuildResult } from "../delivery/packaging/SocialDeliveryPackager.js";
import { DeliveryConfig } from "../delivery/core/DeliveryConfig.js";
import { AspectRatio } from "../delivery/core/AspectRatio.js";
import { ProjectSerializer } from "../persistence/ProjectSerializer.js";
import { TaskPlanner } from "../distributed/tasks/TaskPlanner.js";
import { ElasticScheduler } from "../distributed/scheduler/ElasticScheduler.js";
import { WorkerPool } from "../distributed/scheduler/WorkerPool.js";
import { createDistributedJob } from "../distributed/core/DistributedJob.js";
import { DistributedResult } from "../distributed/core/DistributedResult.js";

export interface MotionEngineRenderResult {
  compositionId: string;
  durationSeconds: number;
  totalFrames: number;
  success: boolean;
  contentHash: string;
}

export class MotionEngine {
  public static readonly VERSION = "3.0.0-gold-master";

  /**
   * Crea una nueva composición canónica del motor.
   */
  public static createComposition(options: CompositionOptions): Composition {
    return new Composition(options);
  }

  /**
   * Compila una composición a script ExtendScript JSX para After Effects.
   */
  public static exportToAfterEffects(comp: Composition, options: JSXCompileOptions = {}): JSXCompileResult {
    return AfterEffectsJSXCompiler.compile(comp, options);
  }

  /**
   * Genera un paquete de entrega multi-aspecto (TikTok, YouTube, Instagram) con audio normalizado y miniaturas.
   */
  public static deliverSocialPackage(
    comp: Composition,
    projectId: string,
    revisionId = "rev_1",
    configOverrides?: Partial<DeliveryConfig>
  ): PackageBuildResult {
    return SocialDeliveryPackager.package(comp, projectId, revisionId, configOverrides);
  }

  /**
   * Ejecuta un pipeline de renderizado determinista local.
   */
  public static async render(comp: Composition): Promise<MotionEngineRenderResult> {
    const totalFrames = Math.floor(comp.duration * comp.fps);
    for (let f = 0; f < totalFrames; f += 10) {
      comp.evaluate(f / comp.fps);
    }

    const contentHash = ProjectSerializer.hashCanonical({
      id: comp.id,
      width: comp.width,
      height: comp.height,
      fps: comp.fps,
      duration: comp.duration,
      elementsCount: comp.getElements().length,
    });

    return {
      compositionId: comp.id,
      durationSeconds: comp.duration,
      totalFrames,
      success: true,
      contentHash,
    };
  }

  /**
   * Ejecuta una producción completa distribuida a través de un pool elástico de workers.
   */
  public static async executeDistributed(params: {
    jobId: string;
    projectId: string;
    briefHash: string;
    baselineRevisionId: string;
    workerCount?: number;
  }): Promise<DistributedResult> {
    const pool = new WorkerPool();
    pool.scale(params.workerCount ?? 4);

    const scheduler = new ElasticScheduler(pool);
    const job = createDistributedJob({
      jobId: params.jobId,
      projectId: params.projectId,
      briefHash: params.briefHash,
      baselineRevisionId: params.baselineRevisionId,
      allocatedWorkers: params.workerCount ?? 4,
    });

    const dag = TaskPlanner.planProduction({ jobId: params.jobId, chunkCount: 2 });
    return scheduler.executeJob(job, dag);
  }

  /**
   * Acceso al puente bidireccional de After Effects.
   */
  public static get ae() {
    return AEBridgeManager;
  }
}
